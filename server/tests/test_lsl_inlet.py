"""Tests for LSL inlet service — work even without pylsl installed."""

from lucid_server.services.lsl_inlet import LSLInlet


def test_inlet_creation() -> None:
    inlet = LSLInlet()
    assert inlet.stream_type == "EEG"
    assert inlet.buffer_seconds == 5.0
    assert inlet.inlet is None
    assert inlet.stream_info is None
    assert not inlet.connected


def test_inlet_custom_params() -> None:
    inlet = LSLInlet(stream_type="EMG", buffer_seconds=10.0)
    assert inlet.stream_type == "EMG"
    assert inlet.buffer_seconds == 10.0


def test_is_available_returns_bool() -> None:
    inlet = LSLInlet()
    assert isinstance(inlet.is_available, bool)


def test_resolve_streams_without_pylsl() -> None:
    inlet = LSLInlet()
    # Without pylsl installed, should return empty list
    if not inlet.is_available:
        assert inlet.resolve_streams() == []


def test_connect_without_pylsl() -> None:
    inlet = LSLInlet()
    if not inlet.is_available:
        assert not inlet.connect()
        assert not inlet.connected


def test_connect_with_name_without_pylsl() -> None:
    inlet = LSLInlet()
    if not inlet.is_available:
        assert not inlet.connect(stream_name="TestStream")
        assert not inlet.connected


def test_disconnect_when_not_connected() -> None:
    inlet = LSLInlet()
    # Should not raise
    inlet.disconnect()
    assert inlet.inlet is None
    assert inlet.stream_info is None
    assert not inlet.connected


def test_disconnect_clears_state() -> None:
    inlet = LSLInlet()
    # Manually set state to verify disconnect clears it
    inlet.connected = True
    inlet.disconnect()
    assert not inlet.connected
    assert inlet.inlet is None
    assert inlet.stream_info is None


def test_pull_chunk_when_not_connected() -> None:
    inlet = LSLInlet()
    assert inlet.pull_chunk() is None


def test_pull_chunk_when_no_inlet() -> None:
    inlet = LSLInlet()
    inlet.connected = True
    inlet.inlet = None
    assert inlet.pull_chunk() is None


def test_pull_chunk_custom_max_samples() -> None:
    inlet = LSLInlet()
    assert inlet.pull_chunk(max_samples=100) is None


def test_get_channel_count_default() -> None:
    inlet = LSLInlet()
    assert inlet.get_channel_count() == 0


def test_get_sample_rate_default() -> None:
    inlet = LSLInlet()
    assert inlet.get_sample_rate() == 0.0
