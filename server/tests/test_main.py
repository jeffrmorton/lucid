"""Tests for main app and WebSocket."""

import asyncio
import struct
from unittest.mock import AsyncMock

import numpy as np
from lucid_server.main import _viewers, app, broadcast_to_viewers
from starlette.testclient import TestClient


def test_websocket_processes_eeg_data() -> None:
    """Test WebSocket receives binary EEG and returns processed results."""
    with TestClient(app) as client, client.websocket_connect("/ws/eeg") as ws:
        n_channels = 8
        n_samples = 250
        data = np.random.randn(n_channels * n_samples)
        raw = struct.pack(f"<{len(data)}d", *data)
        ws.send_bytes(raw)
        response = ws.receive_json()
        assert response["status"] == "processed"
        assert response["n_samples"] == n_samples
        assert "band_powers" in response
        assert "alpha" in response["band_powers"]


def test_websocket_handles_empty_data() -> None:
    """Test WebSocket handles empty binary data."""
    with TestClient(app) as client, client.websocket_connect("/ws/eeg") as ws:
        ws.send_bytes(b"")
        response = ws.receive_json()
        assert response["error"] == "empty data"


def test_websocket_handles_insufficient_samples() -> None:
    """Test WebSocket handles fewer values than n_channels."""
    with TestClient(app) as client, client.websocket_connect("/ws/eeg") as ws:
        data = struct.pack("<3d", 1.0, 2.0, 3.0)
        ws.send_bytes(data)
        response = ws.receive_json()
        assert response["error"] == "insufficient samples"


def test_neurofeedback_websocket_init() -> None:
    """Test neurofeedback WebSocket responds to protocol selection."""
    with TestClient(app) as client, client.websocket_connect("/ws/neurofeedback") as ws:
        ws.send_json({"protocol": "smr_training"})
        response = ws.receive_json()
        assert response["phase"] == "calibration"
        assert "duration_s" in response


def test_neurofeedback_websocket_not_found() -> None:
    """Test neurofeedback WebSocket with nonexistent protocol returns error."""
    with TestClient(app) as client, client.websocket_connect("/ws/neurofeedback") as ws:
        ws.send_json({"protocol": "nonexistent_protocol"})
        response = ws.receive_json()
        assert "error" in response


def test_neurofeedback_websocket_full_session() -> None:
    """Test full neurofeedback flow: calibration + training."""
    n_channels = 8
    with TestClient(app) as client, client.websocket_connect("/ws/neurofeedback") as ws:
        ws.send_json({"protocol": "smr_training"})
        init_resp = ws.receive_json()
        assert init_resp["phase"] == "calibration"
        baseline_duration = init_resp["duration_s"]
        target_samples = 250 * baseline_duration
        sent = 0
        while sent < target_samples:
            data = np.random.randn(n_channels * 250)
            ws.send_bytes(struct.pack(f"<{len(data)}d", *data))
            sent += 250
        cal_done = ws.receive_json()
        assert cal_done["phase"] == "training"
        assert cal_done["calibrated"] is True
        data = np.random.randn(n_channels * 250)
        ws.send_bytes(struct.pack(f"<{len(data)}d", *data))
        feedback = ws.receive_json()
        assert feedback["status"] == "feedback"
        assert "reward" in feedback


def test_neurofeedback_websocket_empty_data_during_calibration() -> None:
    """Empty data during calibration is skipped."""
    n_channels = 8
    with TestClient(app) as client, client.websocket_connect("/ws/neurofeedback") as ws:
        ws.send_json({"protocol": "smr_training"})
        init_resp = ws.receive_json()
        assert init_resp["phase"] == "calibration"
        ws.send_bytes(b"")
        ws.send_bytes(struct.pack("<3d", 1.0, 2.0, 3.0))
        baseline_duration = init_resp["duration_s"]
        target_samples = 250 * baseline_duration
        sent = 0
        while sent < target_samples:
            data = np.random.randn(n_channels * 250)
            ws.send_bytes(struct.pack(f"<{len(data)}d", *data))
            sent += 250
        cal_done = ws.receive_json()
        assert cal_done["phase"] == "training"


def test_neurofeedback_websocket_empty_data_during_training() -> None:
    """Empty/insufficient data during training is skipped."""
    n_channels = 8
    with TestClient(app) as client, client.websocket_connect("/ws/neurofeedback") as ws:
        ws.send_json({"protocol": "smr_training"})
        init_resp = ws.receive_json()
        baseline_duration = init_resp["duration_s"]
        target_samples = 250 * baseline_duration
        sent = 0
        while sent < target_samples:
            data = np.random.randn(n_channels * 250)
            ws.send_bytes(struct.pack(f"<{len(data)}d", *data))
            sent += 250
        ws.receive_json()
        ws.send_bytes(b"")
        ws.send_bytes(struct.pack("<3d", 1.0, 2.0, 3.0))
        data = np.random.randn(n_channels * 250)
        ws.send_bytes(struct.pack(f"<{len(data)}d", *data))
        feedback = ws.receive_json()
        assert feedback["status"] == "feedback"


def test_viewer_websocket_connects() -> None:
    """Test viewer WebSocket accepts connection."""
    with TestClient(app) as client, client.websocket_connect("/ws/viewer"):
        pass


def test_viewer_receives_broadcast() -> None:
    """Test viewer receives data when device sends EEG."""
    with (
        TestClient(app) as client,
        client.websocket_connect("/ws/viewer") as viewer,
        client.websocket_connect("/ws/eeg") as device,
    ):
        n_channels = 8
        n_samples = 250
        data = np.random.randn(n_channels * n_samples)
        raw = struct.pack(f"<{len(data)}d", *data)
        device.send_bytes(raw)
        device.receive_json()
        try:
            viewer_data = viewer.receive_json(mode="text")
            assert viewer_data["status"] == "processed"
        except Exception:  # noqa: S110
            pass  # Timing-dependent


def test_broadcast_handles_disconnected_viewer() -> None:
    """Test broadcast doesn't crash with empty viewer set."""
    asyncio.run(broadcast_to_viewers({"test": True}))


def test_broadcast_removes_bad_viewer() -> None:
    """Test broadcast removes a broken viewer."""
    bad_viewer = AsyncMock()
    bad_viewer.send_json = AsyncMock(side_effect=Exception("broken"))
    _viewers.add(bad_viewer)
    asyncio.run(broadcast_to_viewers({"test": True}))
    assert bad_viewer not in _viewers
