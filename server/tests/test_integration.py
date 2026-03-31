"""Integration tests for end-to-end EEG data flow.

Tests the full pipeline: simulated device -> WebSocket -> EEG processor -> response.
"""

import math
import os
import struct

import httpx as httpx_sync
import numpy as np
import pytest
from httpx import ASGITransport, AsyncClient
from lucid_server.main import app
from lucid_server.services.eeg_processor import EEGProcessor
from lucid_server.services.neurofeedback import (
    BandTarget,
    NeurofeedbackEngine,
    NFProtocol,
)
from starlette.testclient import TestClient

# --- Helper: generate synthetic EEG ---


def generate_eeg_signal(
    n_channels: int = 8,
    n_samples: int = 250,
    sample_rate: float = 250.0,
    alpha_amplitude: float = 10.0,
    noise_amplitude: float = 1.0,
) -> np.ndarray:
    """Generate synthetic EEG with a prominent alpha (10 Hz) signal.

    Returns shape (n_channels, n_samples).
    """
    t = np.arange(n_samples) / sample_rate
    # Alpha oscillation at 10 Hz
    alpha = alpha_amplitude * np.sin(2 * np.pi * 10.0 * t)
    # White noise
    rng = np.random.default_rng(42)
    noise = noise_amplitude * rng.standard_normal((n_channels, n_samples))
    # Add alpha to all channels
    return noise + alpha[np.newaxis, :]


def eeg_to_bytes(data: np.ndarray) -> bytes:
    """Convert numpy EEG array to binary format for WebSocket."""
    flat = data.flatten().astype(np.float64)
    return struct.pack(f"<{len(flat)}d", *flat)


# --- Integration: Full pipeline via WebSocket ---


class TestWebSocketPipeline:
    """Test the complete WebSocket EEG processing pipeline."""

    def test_single_epoch_processing(self) -> None:
        """Send one epoch of EEG, receive processed band powers."""
        with TestClient(app) as client, client.websocket_connect("/ws/eeg") as ws:
            signal = generate_eeg_signal()
            ws.send_bytes(eeg_to_bytes(signal))
            response = ws.receive_json()

            assert response["status"] == "processed"
            assert response["n_samples"] == 250
            assert "band_powers" in response
            assert all(
                band in response["band_powers"]
                for band in ["delta", "theta", "alpha", "beta", "gamma"]
            )

    def test_alpha_dominant_signal(self) -> None:
        """A strong 10 Hz signal should produce high alpha power."""
        with TestClient(app) as client, client.websocket_connect("/ws/eeg") as ws:
            # Strong alpha, low noise
            signal = generate_eeg_signal(alpha_amplitude=50.0, noise_amplitude=0.1)
            ws.send_bytes(eeg_to_bytes(signal))
            response = ws.receive_json()

            bp = response["band_powers"]
            # Alpha should dominate (at least for channel 0)
            alpha = bp["alpha"][0]
            theta = bp["theta"][0]
            delta = bp["delta"][0]
            assert alpha > theta, f"Alpha ({alpha}) should exceed theta ({theta})"
            assert alpha > delta, f"Alpha ({alpha}) should exceed delta ({delta})"

    def test_multiple_epochs_sequential(self) -> None:
        """Send multiple epochs in sequence -- filters should maintain state."""
        with TestClient(app) as client, client.websocket_connect("/ws/eeg") as ws:
            for _i in range(5):
                signal = generate_eeg_signal(n_samples=250)
                ws.send_bytes(eeg_to_bytes(signal))
                response = ws.receive_json()
                assert response["status"] == "processed"
                assert response["n_samples"] == 250

    def test_varying_sample_counts(self) -> None:
        """Pipeline should handle different numbers of samples per epoch."""
        with TestClient(app) as client, client.websocket_connect("/ws/eeg") as ws:
            for n_samples in [100, 250, 500]:
                signal = generate_eeg_signal(n_channels=8, n_samples=n_samples)
                ws.send_bytes(eeg_to_bytes(signal))
                response = ws.receive_json()
                assert response["status"] == "processed"
                assert response["n_samples"] == n_samples

    def test_empty_data_handled(self) -> None:
        """Empty binary data returns error, doesn't crash."""
        with TestClient(app) as client, client.websocket_connect("/ws/eeg") as ws:
            ws.send_bytes(b"")
            response = ws.receive_json()
            assert "error" in response

    def test_partial_data_handled(self) -> None:
        """Fewer than n_channels float64 values returns error."""
        with TestClient(app) as client, client.websocket_connect("/ws/eeg") as ws:
            # Send 4 bytes -- less than one float64, so n_values = 0
            ws.send_bytes(b"\x00\x01\x02\x03")
            response = ws.receive_json()
            assert "error" in response

    def test_insufficient_channels_handled(self) -> None:
        """Fewer complete samples than n_channels returns insufficient samples."""
        with TestClient(app) as client, client.websocket_connect("/ws/eeg") as ws:
            # 3 float64 values: n_samples = 3 // 8 = 0
            data = struct.pack("<3d", 1.0, 2.0, 3.0)
            ws.send_bytes(data)
            response = ws.receive_json()
            assert response["error"] == "insufficient samples"

    def test_band_powers_are_lists(self) -> None:
        """Band power values are JSON arrays with one entry per channel."""
        with TestClient(app) as client, client.websocket_connect("/ws/eeg") as ws:
            signal = generate_eeg_signal()
            ws.send_bytes(eeg_to_bytes(signal))
            response = ws.receive_json()
            for band in ["delta", "theta", "alpha", "beta", "gamma"]:
                values = response["band_powers"][band]
                assert isinstance(values, list)
                assert len(values) == 8  # n_channels

    def test_psd_shape_in_response(self) -> None:
        """Response includes psd_shape metadata."""
        with TestClient(app) as client, client.websocket_connect("/ws/eeg") as ws:
            signal = generate_eeg_signal()
            ws.send_bytes(eeg_to_bytes(signal))
            response = ws.receive_json()
            assert "psd_shape" in response
            assert response["psd_shape"][0] == 8  # n_channels


# --- Integration: EEG Processor pipeline ---


class TestEEGProcessorPipeline:
    """Test the EEG processor as a processing pipeline."""

    def test_continuous_processing(self) -> None:
        """Process 10 seconds of continuous data in 1-second chunks."""
        processor = EEGProcessor(sample_rate=250, n_channels=8)
        for _ in range(10):
            chunk = generate_eeg_signal(n_samples=250)
            filtered = processor.process(chunk)
            assert filtered.shape == (8, 250)
            assert np.all(np.isfinite(filtered))

    def test_notch_filter_removes_60hz(self) -> None:
        """60 Hz mains signal should be attenuated after processing."""
        processor = EEGProcessor(sample_rate=250, n_channels=1, notch_freq=60.0)
        t = np.arange(2000) / 250.0
        mains = 10.0 * np.sin(2 * np.pi * 60.0 * t)
        data = mains.reshape(1, -1)

        filtered = processor.process(data)

        # After settling, 60 Hz should be attenuated
        rms_input = np.sqrt(np.mean(data[0, 1000:] ** 2))
        rms_output = np.sqrt(np.mean(filtered[0, 1000:] ** 2))
        attenuation_db = 20 * math.log10(rms_output / rms_input) if rms_input > 0 else 0
        assert attenuation_db < -10, f"Expected >10 dB attenuation, got {attenuation_db:.1f} dB"

    def test_bandpass_rejects_dc(self) -> None:
        """DC offset should be removed by bandpass filter."""
        processor = EEGProcessor(sample_rate=250, n_channels=1)
        # Use a longer signal so the filter has time to settle
        data = np.ones((1, 2000)) * 100.0  # Large DC offset
        filtered = processor.process(data)
        # After settling (last 500 samples), DC should be heavily attenuated
        assert np.abs(np.mean(filtered[0, 1500:])) < 1.0

    def test_band_powers_are_positive(self) -> None:
        """All band powers should be non-negative."""
        processor = EEGProcessor(sample_rate=250, n_channels=4)
        data = generate_eeg_signal(n_channels=4, n_samples=500)
        filtered = processor.process(data)
        psd, freqs = processor.compute_psd(filtered)
        bp = processor.compute_band_powers(psd, freqs)
        for band_name, values in bp.items():
            assert np.all(values >= 0), f"Band {band_name} has negative power"

    def test_psd_frequency_resolution(self) -> None:
        """PSD frequency resolution should match sample rate and window."""
        processor = EEGProcessor(sample_rate=250, n_channels=2)
        data = generate_eeg_signal(n_channels=2, n_samples=500)
        _psd, freqs = processor.compute_psd(data, window_seconds=1.0)
        # Frequency resolution = sample_rate / nperseg = 250/250 = 1 Hz
        assert freqs[1] - freqs[0] == pytest.approx(1.0, abs=0.1)
        # Max frequency = Nyquist = 125 Hz
        assert freqs[-1] == pytest.approx(125.0, abs=1.0)

    def test_filter_state_persists_across_chunks(self) -> None:
        """Processing multiple chunks should not produce discontinuities."""
        processor = EEGProcessor(sample_rate=250, n_channels=1)
        # Process two consecutive chunks of a continuous sine wave
        t = np.arange(500) / 250.0
        sine = 5.0 * np.sin(2 * np.pi * 10.0 * t)
        chunk1 = sine[:250].reshape(1, -1)
        chunk2 = sine[250:].reshape(1, -1)

        out1 = processor.process(chunk1)
        out2 = processor.process(chunk2)

        # The boundary between chunks should be smooth (no large jump)
        boundary_diff = abs(out2[0, 0] - out1[0, -1])
        max_signal = max(np.max(np.abs(out1[0, 200:])), np.max(np.abs(out2[0, :50])))
        # Boundary discontinuity should be small relative to signal amplitude
        assert boundary_diff < 0.5 * max_signal, (
            f"Boundary discontinuity {boundary_diff:.3f} too large vs signal {max_signal:.3f}"
        )


# --- Integration: Neurofeedback pipeline ---


class TestNeurofeedbackPipeline:
    """Test the neurofeedback engine with realistic EEG data."""

    def _make_engine(self) -> NeurofeedbackEngine:
        protocol = NFProtocol(
            name="Test Alpha",
            description="Alpha enhancement test",
            evidence_level="test",
            electrode="Oz",
            reference="linked_mastoids",
            bands=[
                BandTarget(
                    name="Alpha",
                    low_hz=8,
                    high_hz=13,
                    target="enhance",
                    threshold_percentile=50,
                ),
                BandTarget(
                    name="Theta",
                    low_hz=4,
                    high_hz=8,
                    target="suppress",
                    threshold_percentile=80,
                ),
            ],
        )
        return NeurofeedbackEngine(protocol)

    def test_baseline_then_training(self) -> None:
        """Complete neurofeedback flow: baseline -> calibrate -> evaluate."""
        engine = self._make_engine()
        engine.set_smoothing(alpha=1.0, min_streak=1)  # Immediate reward for pipeline test
        processor = EEGProcessor(sample_rate=250, n_channels=1)

        # Baseline: 10 epochs of moderate alpha
        for _ in range(10):
            data = generate_eeg_signal(n_channels=1, alpha_amplitude=5.0)
            filtered = processor.process(data)
            psd, freqs = processor.compute_psd(filtered)
            bp = processor.compute_band_powers(psd, freqs)
            engine.add_baseline_sample(
                {
                    "alpha": float(bp["alpha"][0]),
                    "theta": float(bp["theta"][0]),
                }
            )

        engine.calibrate()
        assert engine.calibrated

        # Training: high alpha should get reward
        high_alpha_data = generate_eeg_signal(
            n_channels=1, alpha_amplitude=20.0, noise_amplitude=0.5
        )
        filtered = processor.process(high_alpha_data)
        psd, freqs = processor.compute_psd(filtered)
        bp = processor.compute_band_powers(psd, freqs)
        state = engine.evaluate(
            {
                "alpha": float(bp["alpha"][0]),
                "theta": float(bp["theta"][0]),
            }
        )
        # High alpha should trigger reward (alpha above 50th percentile baseline)
        assert state.reward or state.reward_value > 0

    def test_inhibit_on_high_theta(self) -> None:
        """High theta activity should trigger inhibit."""
        engine = self._make_engine()
        engine.set_smoothing(alpha=1.0, min_streak=1)

        # Baseline with low theta
        for _ in range(10):
            engine.add_baseline_sample({"alpha": 5.0, "theta": 1.0})
        engine.calibrate()

        # High theta should inhibit
        state = engine.evaluate({"alpha": 10.0, "theta": 10.0})
        assert state.inhibit

    def test_no_reward_when_uncalibrated(self) -> None:
        """Engine should not reward before calibration."""
        engine = self._make_engine()
        state = engine.evaluate({"alpha": 100.0, "theta": 0.0})
        assert not state.reward
        assert state.reward_value == 0.0


# --- Integration: REST API endpoints ---


class TestRESTAPIIntegration:
    """Test REST API endpoints work together."""

    @pytest.fixture
    def client(self):
        transport = ASGITransport(app=app)
        return AsyncClient(transport=transport, base_url="http://test")

    async def test_health_check(self, client: AsyncClient) -> None:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    async def test_session_lifecycle(self, client: AsyncClient) -> None:
        """Create, get, and delete a session."""
        # Create
        resp = await client.post("/api/sessions/", json={"name": "Integration Test"})
        assert resp.status_code == 200
        session_id = resp.json()["id"]

        # Get
        resp = await client.get(f"/api/sessions/{session_id}")
        assert resp.json()["name"] == "Integration Test"

        # Delete
        resp = await client.delete(f"/api/sessions/{session_id}")
        assert resp.json()["status"] == "deleted"

        # Verify deleted
        resp = await client.get(f"/api/sessions/{session_id}")
        assert "error" in resp.json()

    async def test_data_endpoints(self, client: AsyncClient) -> None:
        """All data endpoints return valid responses."""
        for path in ["/api/data/", "/api/data/bands", "/api/data/protocols"]:
            resp = await client.get(path)
            assert resp.status_code == 200


# --- Integration: Live EarthSync tests (require EarthSync on localhost:3001) ---

EARTHSYNC_URL = os.environ.get("EARTHSYNC_TEST_URL", "http://localhost:3001")


@pytest.fixture
def earthsync_available():
    """Skip if EarthSync is not running."""
    try:
        resp = httpx_sync.get(f"{EARTHSYNC_URL}/health", timeout=3.0)
        if resp.status_code != 200:
            pytest.skip("EarthSync not available")
    except Exception:
        pytest.skip("EarthSync not available")


@pytest.mark.integration
class TestEarthSyncIntegration:
    """Live integration tests against a running EarthSync server."""

    def test_health(self, earthsync_available) -> None:
        resp = httpx_sync.get(f"{EARTHSYNC_URL}/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_stations_list(self, earthsync_available) -> None:
        resp = httpx_sync.get(f"{EARTHSYNC_URL}/api/public/stations")
        assert resp.status_code == 200
        stations = resp.json()
        assert isinstance(stations, list)

    def test_station_latest(self, earthsync_available) -> None:
        resp = httpx_sync.get(f"{EARTHSYNC_URL}/api/public/stations")
        stations = resp.json()
        if stations:
            station_id = stations[0]["id"]
            resp2 = httpx_sync.get(f"{EARTHSYNC_URL}/api/public/stations/{station_id}/latest")
            assert resp2.status_code == 200

    async def test_earthsync_client_live(self, earthsync_available) -> None:
        """Test EarthSyncClient against live EarthSync server."""
        from lucid_server.services.earthsync_client import EarthSyncClient

        client = EarthSyncClient(base_url=EARTHSYNC_URL, station_id="simulator1")
        state = await client.fetch_sr_state()
        assert "freq" in state
        assert 5.0 < state["freq"] < 12.0  # SR mode 1 should be near 7.83 Hz
        assert state["amp"] > 0
        assert client.current_frequency != 7.83  # Should have updated from default

    async def test_sr_entrainment_flow(self, earthsync_available) -> None:
        """Test the full SR entrainment flow: fetch -> update band -> verify."""
        from pathlib import Path

        from lucid_server.services.earthsync_client import EarthSyncClient
        from lucid_server.services.neurofeedback import NeurofeedbackEngine, load_protocol

        # Load SR entrainment protocol
        protocol = load_protocol(
            Path(__file__).parent.parent.parent / "protocols" / "sr_entrainment.yaml"
        )
        assert protocol.earthsync is not None
        assert protocol.earthsync["enabled"] is True

        # Fetch live SR
        client = EarthSyncClient(base_url=EARTHSYNC_URL, station_id="simulator1")
        state = await client.fetch_sr_state()
        live_freq = state["freq"]

        # Create engine and update band
        engine = NeurofeedbackEngine(protocol)
        updated = engine.update_band_range("SR", live_freq - 1.0, live_freq + 1.0)
        assert updated is True

        # Verify band was updated
        sr_band = next(b for b in protocol.bands if b.name.lower() == "sr")
        assert abs(sr_band.low_hz - (live_freq - 1.0)) < 0.001
        assert abs(sr_band.high_hz - (live_freq + 1.0)) < 0.001
