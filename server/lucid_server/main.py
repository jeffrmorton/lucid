"""Lucid Server — FastAPI application entry point."""

import asyncio
import re
import struct
import time
from pathlib import Path

import numpy as np
import structlog
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from lucid_server import __version__
from lucid_server.config import get_settings
from lucid_server.models.ws_messages import (
    CalibrationMessage,
    ErrorMessage,
    FeedbackMessage,
    ProcessedMessage,
    TrainingMessage,
)
from lucid_server.routes import data, health, lsl, protocols, sessions
from lucid_server.services.earthsync_client import EarthSyncClient
from lucid_server.services.eeg_processor import EEGProcessor
from lucid_server.services.neurofeedback import NeurofeedbackEngine, load_protocol

logger = structlog.get_logger(__name__)

# Reject frames larger than this to bound per-frame allocation (8 MB).
MAX_FRAME_BYTES = 8 * 1024 * 1024
# Cap concurrent viewer sockets to bound memory under abusive clients.
MAX_VIEWERS = 64
# Per-viewer send timeout so one slow viewer never stalls device ingestion.
VIEWER_SEND_TIMEOUT_S = 1.0
# Valid protocol filename stem (defends against path traversal / arbitrary read).
_PROTOCOL_NAME_RE = re.compile(r"^[a-z0-9_-]+$")

PROTOCOLS_CANDIDATE_DIRS = (
    Path(__file__).parent.parent / "protocols",  # Docker mount
    Path(__file__).parent.parent.parent / "protocols",  # repo root
)


def _origin_allowed(websocket: WebSocket, allowed: list[str]) -> bool:
    """Allow same-origin/native clients; block cross-site browser hijacking.

    A missing Origin header means a non-browser client (device, simulator,
    CLI), which is permitted. A present Origin must be in the allowlist.
    """
    origin = websocket.headers.get("origin")
    return origin is None or origin in allowed


def _decode_eeg_frame(raw: bytes, n_channels: int) -> np.ndarray | None:
    """Decode a binary EEG frame into (n_channels, n_samples), or None if unusable.

    Slices to an 8-byte boundary so a misaligned frame cannot raise struct.error.
    """
    n_values = len(raw) // 8  # 8 bytes per float64
    n_samples = n_values // n_channels
    if n_samples == 0:
        return None
    usable = n_channels * n_samples
    values = struct.unpack(f"<{usable}d", raw[: usable * 8])
    return np.array(values).reshape(n_channels, n_samples)


def create_app() -> FastAPI:  # noqa: PLR0915
    """Build the Lucid FastAPI application.

    Viewer sockets live on ``app.state.viewers`` so each app instance is
    isolated (important for test isolation).
    """
    settings = get_settings()
    app = FastAPI(
        title="Lucid BCI Server",
        version=__version__,
        description="Real-time EEG processing, artifact rejection, and neurofeedback engine.",
    )
    app.state.viewers = set()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, tags=["health"])
    app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])
    app.include_router(data.router, prefix="/api/data", tags=["data"])
    app.include_router(protocols.router, prefix="/api/protocols", tags=["protocols"])
    app.include_router(lsl.router, prefix="/api/lsl", tags=["lsl"])

    def _new_processor() -> EEGProcessor:
        return EEGProcessor(
            sample_rate=settings.sample_rate,
            n_channels=settings.n_channels,
            bandpass_low=settings.bandpass_low,
            bandpass_high=settings.bandpass_high,
            notch_freq=settings.notch_freq,
        )

    async def broadcast_to_viewers(message: dict) -> None:
        """Send processed EEG data to all connected viewer clients.

        Each send is bounded by a timeout so a single slow/backpressured viewer
        cannot stall device ingestion; failing viewers are dropped.
        """
        disconnected = set()
        for viewer in app.state.viewers.copy():
            try:
                await asyncio.wait_for(viewer.send_json(message), timeout=VIEWER_SEND_TIMEOUT_S)
            except (Exception, TimeoutError):
                disconnected.add(viewer)
        for v in disconnected:
            app.state.viewers.discard(v)
        if disconnected:
            logger.warning("viewer_dropped", count=len(disconnected))

    app.state.broadcast_to_viewers = broadcast_to_viewers

    @app.websocket("/ws/viewer")
    async def viewer_websocket(websocket: WebSocket) -> None:
        """WebSocket for dashboard viewers. Receives broadcast of processed EEG data."""
        if not _origin_allowed(websocket, settings.cors_origins):
            await websocket.close(code=1008)
            return
        if len(app.state.viewers) >= MAX_VIEWERS:
            await websocket.close(code=1008)
            return
        await websocket.accept()
        app.state.viewers.add(websocket)
        try:
            while True:
                await websocket.receive_text()  # Keep alive, ignore input
        except WebSocketDisconnect:
            app.state.viewers.discard(websocket)

    @app.websocket("/ws/eeg")
    async def eeg_websocket(websocket: WebSocket) -> None:
        """WebSocket endpoint for EEG device data.

        Receives raw EEG samples as binary (n_channels x n_samples float64),
        processes through the pipeline, returns results to device AND broadcasts
        to all connected viewer clients.
        """
        if not _origin_allowed(websocket, settings.cors_origins):
            await websocket.close(code=1008)
            return
        await websocket.accept()

        processor = _new_processor()

        try:
            while True:
                raw = await websocket.receive_bytes()

                if len(raw) > MAX_FRAME_BYTES:
                    await websocket.send_json(ErrorMessage(error="frame too large").model_dump())
                    continue
                n_values = len(raw) // 8  # 8 bytes per float64
                if n_values == 0:
                    await websocket.send_json(ErrorMessage(error="empty data").model_dump())
                    continue
                data_array = _decode_eeg_frame(raw, settings.n_channels)
                if data_array is None:
                    await websocket.send_json(
                        ErrorMessage(error="insufficient samples").model_dump()
                    )
                    continue

                # Process through pipeline
                filtered = processor.process(data_array)
                psd, freqs = processor.compute_psd(filtered)
                band_powers = processor.compute_band_powers(psd, freqs)
                avg_psd = np.mean(psd, axis=0).tolist()

                response = ProcessedMessage(
                    n_samples=data_array.shape[1],
                    band_powers={k: v.tolist() for k, v in band_powers.items()},
                    psd=avg_psd,
                    freqs=freqs.tolist(),
                    psd_shape=list(psd.shape),
                ).model_dump()

                await websocket.send_json(response)
                await broadcast_to_viewers(response)

        except WebSocketDisconnect:
            pass

    @app.websocket("/ws/neurofeedback")
    async def neurofeedback_websocket(websocket: WebSocket) -> None:  # noqa: PLR0915, PLR0912
        """WebSocket for neurofeedback training sessions."""
        if not _origin_allowed(websocket, settings.cors_origins):
            await websocket.close(code=1008)
            return
        await websocket.accept()

        processor = _new_processor()
        earthsync_client: EarthSyncClient | None = None

        try:
            init_msg = await websocket.receive_json()
            protocol_name = init_msg.get("protocol", "smr_training")

            if not _PROTOCOL_NAME_RE.match(protocol_name):
                await websocket.send_json(
                    ErrorMessage(error=f"Invalid protocol name: {protocol_name}").model_dump()
                )
                return

            candidates = [d / f"{protocol_name}.yaml" for d in PROTOCOLS_CANDIDATE_DIRS]
            protocol_path = next((p for p in candidates if p.exists()), None)
            if protocol_path is None:
                await websocket.send_json(
                    ErrorMessage(error=f"Protocol {protocol_name} not found").model_dump()
                )
                return

            protocol = load_protocol(protocol_path)
            engine = NeurofeedbackEngine(protocol)

            # Initialize EarthSync client if the protocol enables it.
            # settings.earthsync_url WINS over any YAML-provided url.
            if protocol.earthsync and protocol.earthsync.get("enabled"):
                es_config = protocol.earthsync
                # settings.earthsync_url (LUCID_EARTHSYNC_URL) takes precedence;
                # the YAML url is only a fallback if settings is somehow empty.
                base_url = settings.earthsync_url or str(es_config.get("url", ""))
                earthsync_client = EarthSyncClient(
                    base_url=base_url,
                    station_id=es_config.get("station_id", settings.earthsync_station_id),
                )
                sr_state = await earthsync_client.fetch_sr_state()
                _entrain_sr(engine, sr_state)

                await websocket.send_json(
                    CalibrationMessage(
                        duration_s=protocol.baseline_duration_s,
                        earthsync={
                            "enabled": True,
                            "station_id": earthsync_client.station_id,
                            "sr_frequency": sr_state["freq"],
                            "sr_amplitude": sr_state.get("amp", 0.0),
                            "degraded": earthsync_client.degraded,
                        },
                    ).model_dump()
                )
            else:
                await websocket.send_json(
                    CalibrationMessage(duration_s=protocol.baseline_duration_s).model_dump()
                )

            calibration_samples = 0
            target_samples = settings.sample_rate * protocol.baseline_duration_s

            while calibration_samples < target_samples:
                raw = await websocket.receive_bytes()
                data_array = _decode_eeg_frame(raw, settings.n_channels)
                if data_array is None:
                    continue
                bp = _all_band_powers(processor, data_array, protocol)
                engine.add_baseline_sample({k: float(v[0]) for k, v in bp.items()})
                calibration_samples += data_array.shape[1]

            engine.calibrate()
            await websocket.send_json(TrainingMessage(calibrated=engine.calibrated).model_dump())

            # Training phase — periodically update SR target if EarthSync is active.
            last_sr_update = time.time()
            sr_update_interval = (
                protocol.earthsync.get("update_interval_s", 10)
                if protocol.earthsync
                else float("inf")
            )

            while True:
                raw = await websocket.receive_bytes()
                data_array = _decode_eeg_frame(raw, settings.n_channels)
                if data_array is None:
                    continue

                if earthsync_client and time.time() - last_sr_update >= sr_update_interval:
                    sr_state = await earthsync_client.fetch_sr_state()
                    _entrain_sr(engine, sr_state)
                    last_sr_update = time.time()

                bp = _all_band_powers(processor, data_array, protocol)
                state = engine.evaluate({k: float(v[0]) for k, v in bp.items()})

                sr_info = None
                if earthsync_client:
                    sr_info = {
                        "frequency": earthsync_client.current_frequency,
                        "station_id": earthsync_client.station_id,
                        "degraded": earthsync_client.degraded,
                    }
                feedback_msg = FeedbackMessage(
                    reward=state.reward,
                    inhibit=state.inhibit,
                    reward_value=state.reward_value,
                    inhibit_value=state.inhibit_value,
                    band_powers={k: v.tolist() for k, v in bp.items()},
                    sr=sr_info,
                ).model_dump()
                await websocket.send_json(feedback_msg)

        except WebSocketDisconnect:
            pass
        finally:
            if earthsync_client is not None:
                await earthsync_client.aclose()

    return app


def _entrain_sr(engine: NeurofeedbackEngine, sr_state: dict) -> None:
    """Shift the SR reward band to track the live fundamental.

    Uses the measured Q-factor to derive the band half-width when available
    (half-width = freq / (2*Q)), clamped to a sane range; otherwise +/-1 Hz.
    """
    freq = sr_state["freq"]
    q = sr_state.get("q_factor")
    half_width = max(0.5, min(2.0, freq / (2.0 * q))) if q else 1.0
    engine.update_band_range("SR", freq - half_width, freq + half_width)


def _all_band_powers(processor: EEGProcessor, data_array: np.ndarray, protocol: object) -> dict:
    """Compute band powers for every protocol band by its own frequency range.

    The fixed-name compute_band_powers() only emits the 5 standard bands, so
    custom-named protocol bands (SMR, Low Beta, High Beta, SR) would otherwise
    never receive power. We compute each protocol band generically, keyed by
    band.name.lower(), and keep the standard bands for viewer display.
    """
    filtered = processor.process(data_array)
    psd, freqs = processor.compute_psd(filtered)
    bp = processor.compute_band_powers(psd, freqs)
    for band in protocol.bands:  # type: ignore[attr-defined]
        bp[band.name.lower()] = processor.compute_custom_band_power(
            psd, freqs, band.low_hz, band.high_hz
        )
    return bp


app = create_app()
# Module-level alias so existing imports (tests, broadcast helper) keep working.
_viewers = app.state.viewers
broadcast_to_viewers = app.state.broadcast_to_viewers
