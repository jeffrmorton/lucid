"""Lucid Server — FastAPI application entry point."""

import struct
import time
from pathlib import Path

import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from lucid_server.config import settings
from lucid_server.routes import data, health, lsl, protocols, sessions
from lucid_server.services.eeg_processor import EEGProcessor
from lucid_server.services.neurofeedback import NeurofeedbackEngine, load_protocol

app = FastAPI(
    title="Lucid BCI Server",
    version="0.2.0",
    description="Real-time EEG processing, artifact rejection, and neurofeedback engine.",
)

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

# Connected viewer clients that receive broadcast data
_viewers: set[WebSocket] = set()


async def broadcast_to_viewers(message: dict) -> None:
    """Send processed EEG data to all connected viewer clients."""
    disconnected = set()
    for viewer in _viewers.copy():
        try:
            await viewer.send_json(message)
        except Exception:
            disconnected.add(viewer)
    for v in disconnected:
        _viewers.discard(v)


@app.websocket("/ws/viewer")
async def viewer_websocket(websocket: WebSocket) -> None:
    """WebSocket for dashboard viewers. Receives broadcast of processed EEG data."""
    await websocket.accept()
    _viewers.add(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep alive, ignore input
    except WebSocketDisconnect:
        _viewers.discard(websocket)


@app.websocket("/ws/eeg")
async def eeg_websocket(websocket: WebSocket) -> None:
    """WebSocket endpoint for EEG device data.

    Receives raw EEG samples as binary (n_channels x n_samples float64),
    processes through the pipeline, returns results to device AND broadcasts
    to all connected viewer clients.
    """
    await websocket.accept()

    processor = EEGProcessor(
        sample_rate=settings.sample_rate,
        n_channels=settings.n_channels,
        notch_freq=settings.notch_freq,
    )

    try:
        while True:
            raw = await websocket.receive_bytes()

            # Decode binary: expect n_channels x n_samples float64
            n_values = len(raw) // 8  # 8 bytes per float64
            if n_values == 0:
                await websocket.send_json({"error": "empty data"})
                continue

            values = struct.unpack(f"<{n_values}d", raw)
            n_samples = n_values // settings.n_channels
            if n_samples == 0:
                await websocket.send_json({"error": "insufficient samples"})
                continue

            # Reshape to (n_channels, n_samples)
            data_array = np.array(values[: settings.n_channels * n_samples]).reshape(
                settings.n_channels, n_samples
            )

            # Process through pipeline
            filtered = processor.process(data_array)

            # Compute PSD and band powers
            psd, freqs = processor.compute_psd(filtered)
            band_powers = processor.compute_band_powers(psd, freqs)

            # Average PSD across channels for spectrogram display
            avg_psd = np.mean(psd, axis=0).tolist()

            # Build response
            response = {
                "status": "processed",
                "n_samples": n_samples,
                "band_powers": {k: v.tolist() for k, v in band_powers.items()},
                "psd": avg_psd,
                "freqs": freqs.tolist(),
                "psd_shape": list(psd.shape),
            }

            # Send to device
            await websocket.send_json(response)

            # Broadcast to all viewer clients (dashboard)
            await broadcast_to_viewers(response)

    except WebSocketDisconnect:
        pass


@app.websocket("/ws/neurofeedback")
async def neurofeedback_websocket(websocket: WebSocket) -> None:  # noqa: PLR0915
    """WebSocket for neurofeedback training sessions."""
    await websocket.accept()

    processor = EEGProcessor(
        sample_rate=settings.sample_rate,
        n_channels=settings.n_channels,
        notch_freq=settings.notch_freq,
    )

    # Wait for protocol selection message
    try:
        init_msg = await websocket.receive_json()
        protocol_name = init_msg.get("protocol", "smr_training")

        # Load protocol — check multiple locations
        candidates = [
            Path(__file__).parent.parent / "protocols" / f"{protocol_name}.yaml",  # Docker mount
            Path(__file__).parent.parent.parent
            / "protocols"
            / f"{protocol_name}.yaml",  # repo root
        ]
        protocol_path = next((p for p in candidates if p.exists()), None)
        if protocol_path is None:
            await websocket.send_json({"error": f"Protocol {protocol_name} not found"})
            return

        protocol = load_protocol(protocol_path)
        engine = NeurofeedbackEngine(protocol)

        # Initialize EarthSync client if protocol enables it
        earthsync_client = None
        if protocol.earthsync and protocol.earthsync.get("enabled"):
            from lucid_server.services.earthsync_client import EarthSyncClient  # noqa: PLC0415

            es_config = protocol.earthsync
            earthsync_client = EarthSyncClient(
                base_url=es_config.get("url", settings.earthsync_url),
                station_id=es_config.get("station_id", "simulator1"),
            )
            # Fetch initial SR state
            sr_state = await earthsync_client.fetch_sr_state()
            sr_freq = sr_state["freq"]
            engine.update_band_range("SR", sr_freq - 1.0, sr_freq + 1.0)

            # Send SR info to client with calibration phase
            await websocket.send_json(
                {
                    "phase": "calibration",
                    "duration_s": protocol.baseline_duration_s,
                    "earthsync": {
                        "enabled": True,
                        "station_id": earthsync_client.station_id,
                        "sr_frequency": sr_freq,
                        "sr_amplitude": sr_state.get("amp", 0.0),
                    },
                }
            )
        else:
            # Calibration phase (no EarthSync)
            await websocket.send_json(
                {"phase": "calibration", "duration_s": protocol.baseline_duration_s}
            )

        calibration_samples = 0
        target_samples = settings.sample_rate * protocol.baseline_duration_s

        while calibration_samples < target_samples:
            raw = await websocket.receive_bytes()
            n_values = len(raw) // 8
            if n_values == 0:
                continue
            values = struct.unpack(f"<{n_values}d", raw)
            n_samples = n_values // settings.n_channels
            if n_samples == 0:
                continue
            data_array = np.array(values[: settings.n_channels * n_samples]).reshape(
                settings.n_channels, n_samples
            )
            filtered = processor.process(data_array)
            psd, freqs = processor.compute_psd(filtered)
            bp = processor.compute_band_powers(psd, freqs)

            # If SR entrainment, compute custom SR band power before converting
            if earthsync_client and protocol.earthsync:
                sr_band = next((b for b in protocol.bands if b.name.lower() == "sr"), None)
                if sr_band:
                    bp["sr"] = processor.compute_custom_band_power(
                        psd, freqs, sr_band.low_hz, sr_band.high_hz
                    )

            # Add to baseline (use channel 0 = active electrode)
            engine.add_baseline_sample({k: float(v[0]) for k, v in bp.items()})
            calibration_samples += n_samples

        engine.calibrate()
        await websocket.send_json({"phase": "training", "calibrated": True})

        # Training phase — periodically update SR target if EarthSync is active
        last_sr_update = time.time()
        sr_update_interval = (
            protocol.earthsync.get("update_interval_s", 10) if protocol.earthsync else 999999
        )

        while True:
            raw = await websocket.receive_bytes()
            n_values = len(raw) // 8
            if n_values == 0:
                continue
            values = struct.unpack(f"<{n_values}d", raw)
            n_samples = n_values // settings.n_channels
            if n_samples == 0:
                continue
            data_array = np.array(values[: settings.n_channels * n_samples]).reshape(
                settings.n_channels, n_samples
            )
            filtered = processor.process(data_array)
            psd, freqs = processor.compute_psd(filtered)
            bp = processor.compute_band_powers(psd, freqs)

            # Periodically refresh SR frequency from EarthSync
            if earthsync_client and time.time() - last_sr_update >= sr_update_interval:
                sr_state = await earthsync_client.fetch_sr_state()
                sr_freq = sr_state["freq"]
                engine.update_band_range("SR", sr_freq - 1.0, sr_freq + 1.0)
                last_sr_update = time.time()

            # Compute custom SR band power before evaluate/tolist conversion
            if earthsync_client and protocol.earthsync:
                sr_band = next((b for b in protocol.bands if b.name.lower() == "sr"), None)
                if sr_band:
                    bp["sr"] = processor.compute_custom_band_power(
                        psd, freqs, sr_band.low_hz, sr_band.high_hz
                    )

            state = engine.evaluate({k: float(v[0]) for k, v in bp.items()})

            feedback_msg: dict = {
                "status": "feedback",
                "reward": state.reward,
                "inhibit": state.inhibit,
                "reward_value": state.reward_value,
                "inhibit_value": state.inhibit_value,
                "band_powers": {k: v.tolist() for k, v in bp.items()},
            }
            if earthsync_client:
                feedback_msg["sr"] = {
                    "frequency": earthsync_client.current_frequency,
                    "station_id": earthsync_client.station_id,
                }
            await websocket.send_json(feedback_msg)

    except WebSocketDisconnect:
        pass
