"""Security + EarthSync-path tests for the WebSocket endpoints."""

import struct
from unittest.mock import AsyncMock, patch

import numpy as np
import pytest
from lucid_server import main as main_module
from lucid_server.main import MAX_FRAME_BYTES, MAX_VIEWERS, app
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

BAD_ORIGIN = {"origin": "http://evil.example.com"}


def _eeg_bytes(n_channels: int = 8, n_samples: int = 250) -> bytes:
    data = np.random.randn(n_channels * n_samples)
    return struct.pack(f"<{len(data)}d", *data)


# --- Origin (CSWSH) checks ---


@pytest.mark.parametrize("path", ["/ws/viewer", "/ws/eeg", "/ws/neurofeedback"])
def test_ws_rejects_cross_site_origin(path: str) -> None:
    """A cross-site browser Origin is rejected with close 1008."""
    with TestClient(app) as client:
        with pytest.raises(WebSocketDisconnect) as exc:
            with client.websocket_connect(path, headers=BAD_ORIGIN) as ws:
                ws.receive_text()
        assert exc.value.code == 1008


def test_ws_allows_listed_origin() -> None:
    """An allowlisted Origin is accepted."""
    with (
        TestClient(app) as client,
        client.websocket_connect("/ws/eeg", headers={"origin": "http://localhost:3000"}) as ws,
    ):
        ws.send_bytes(_eeg_bytes())
        assert ws.receive_json()["type"] == "processed"


# --- Resource bounds ---


def test_eeg_rejects_oversized_frame() -> None:
    """A frame larger than MAX_FRAME_BYTES is rejected without allocation."""
    with TestClient(app) as client, client.websocket_connect("/ws/eeg") as ws:
        ws.send_bytes(b"\x00" * (MAX_FRAME_BYTES + 8))
        resp = ws.receive_json()
        assert resp["type"] == "error"
        assert resp["error"] == "frame too large"


def test_eeg_misaligned_frame_does_not_crash() -> None:
    """A frame whose length is not a multiple of 8 is decoded safely (sliced)."""
    with TestClient(app) as client, client.websocket_connect("/ws/eeg") as ws:
        # 8 channels * 250 samples + 3 trailing bytes (misaligned)
        ws.send_bytes(_eeg_bytes() + b"\x01\x02\x03")
        resp = ws.receive_json()
        assert resp["type"] == "processed"
        assert resp["n_samples"] == 250


def test_viewer_cap_enforced() -> None:
    """A new viewer is rejected with 1008 once MAX_VIEWERS are already connected.

    The set is pre-filled with sentinels to avoid opening 64 real sockets
    against the single-threaded test server (which would deadlock).
    """
    app.state.viewers.update(object() for _ in range(MAX_VIEWERS))
    try:
        with TestClient(app) as client:
            with pytest.raises(WebSocketDisconnect) as exc:
                with client.websocket_connect("/ws/viewer") as ws:
                    ws.receive_text()
            assert exc.value.code == 1008
    finally:
        app.state.viewers.clear()


# --- Path traversal ---


def test_neurofeedback_rejects_path_traversal() -> None:
    """A protocol name with traversal characters is rejected before any FS access."""
    with TestClient(app) as client, client.websocket_connect("/ws/neurofeedback") as ws:
        ws.send_json({"protocol": "../../../../etc/passwd"})
        resp = ws.receive_json()
        assert resp["type"] == "error"
        assert "Invalid protocol name" in resp["error"]


# --- EarthSync neurofeedback path (mocked) ---


def _make_fake_earthsync(freq: float = 7.84, q_factor: float | None = 5.0) -> AsyncMock:
    """Build a fake EarthSyncClient instance driving the SR WS branches."""
    fake = AsyncMock()
    fake.fetch_sr_state = AsyncMock(return_value={"freq": freq, "amp": 1.5, "q_factor": q_factor})
    fake.aclose = AsyncMock()
    fake.station_id = "simulator1"
    fake.current_frequency = freq
    fake.degraded = False
    return fake


def _run_sr_session(fake_client: AsyncMock) -> dict:
    """Drive a full sr_entrainment session and return the feedback message."""
    with patch.object(main_module, "EarthSyncClient", return_value=fake_client):
        with (
            TestClient(app) as client,
            client.websocket_connect("/ws/neurofeedback") as ws,
        ):
            ws.send_json({"protocol": "sr_entrainment"})
            cal = ws.receive_json()
            assert cal["type"] == "phase"
            assert cal["earthsync"]["enabled"] is True
            target = 250 * cal["duration_s"]
            sent = 0
            while sent < target:
                ws.send_bytes(_eeg_bytes())
                sent += 250
            train = ws.receive_json()
            assert train["phase"] == "training"
            ws.send_bytes(_eeg_bytes())
            return ws.receive_json()


def test_sr_entrainment_session_with_q_factor() -> None:
    """Full SR session: q_factor drives band half-width; feedback carries sr info."""
    fake = _make_fake_earthsync(freq=7.84, q_factor=5.0)
    feedback = _run_sr_session(fake)
    assert feedback["type"] == "feedback"
    assert feedback["sr"]["station_id"] == "simulator1"
    assert feedback["sr"]["degraded"] is False
    fake.aclose.assert_awaited()


def test_sr_entrainment_session_without_q_factor() -> None:
    """SR session with no q_factor falls back to a fixed +/-1 Hz window."""
    fake = _make_fake_earthsync(freq=7.90, q_factor=None)
    feedback = _run_sr_session(fake)
    assert feedback["type"] == "feedback"


def test_sr_entrainment_training_refreshes_sr() -> None:
    """During training the SR target is refreshed once the interval elapses."""
    fake = _make_fake_earthsync(freq=7.84, q_factor=5.0)
    with patch.object(main_module, "EarthSyncClient", return_value=fake):
        with (
            TestClient(app) as client,
            client.websocket_connect("/ws/neurofeedback") as ws,
        ):
            ws.send_json({"protocol": "sr_entrainment"})
            cal = ws.receive_json()
            target = 250 * cal["duration_s"]
            sent = 0
            while sent < target:
                ws.send_bytes(_eeg_bytes())
                sent += 250
            ws.receive_json()  # training
            # Force the update interval to elapse on the next epoch by jumping
            # the clock far past last_sr_update.
            fake.fetch_sr_state.reset_mock()
            with patch("lucid_server.main.time.time", return_value=2e9):
                ws.send_bytes(_eeg_bytes())
                fb = ws.receive_json()
            assert fb["type"] == "feedback"
            assert fake.fetch_sr_state.await_count >= 1
