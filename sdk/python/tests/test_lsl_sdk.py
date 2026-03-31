"""Tests for SDK LSL inlet — work even without pylsl installed."""

from lucid.lsl_inlet import LucidLSLInlet


def test_inlet_creation() -> None:
    inlet = LucidLSLInlet()
    assert inlet.stream_type == "EEG"
    assert not inlet.connected


def test_inlet_custom_stream_type() -> None:
    inlet = LucidLSLInlet(stream_type="EMG")
    assert inlet.stream_type == "EMG"


def test_is_available_returns_bool() -> None:
    inlet = LucidLSLInlet()
    assert isinstance(inlet.is_available, bool)


def test_find_streams_without_pylsl() -> None:
    inlet = LucidLSLInlet()
    if not inlet.is_available:
        assert inlet.find_streams() == []


def test_connect_without_pylsl() -> None:
    inlet = LucidLSLInlet()
    if not inlet.is_available:
        assert not inlet.connect()
        assert not inlet.connected


def test_connect_with_name_without_pylsl() -> None:
    inlet = LucidLSLInlet()
    if not inlet.is_available:
        assert not inlet.connect(stream_name="TestStream")
        assert not inlet.connected


def test_disconnect() -> None:
    inlet = LucidLSLInlet()
    inlet.connected = True
    inlet.disconnect()
    assert not inlet.connected


def test_disconnect_when_not_connected() -> None:
    inlet = LucidLSLInlet()
    # Should not raise
    inlet.disconnect()
    assert not inlet.connected
