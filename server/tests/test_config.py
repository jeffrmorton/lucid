"""Tests for server configuration."""

from lucid_server.config import Settings, get_settings


def test_default_settings() -> None:
    s = Settings()
    assert s.port == 3001
    assert s.sample_rate == 250
    assert s.n_channels == 8


def test_settings_types() -> None:
    s = Settings()
    assert isinstance(s.cors_origins, list)
    assert isinstance(s.bandpass_low, float)
    assert isinstance(s.bandpass_high, float)


def test_device_settings() -> None:
    s = Settings()
    assert s.brainflow_board_id == -1  # synthetic by default
    assert s.brainflow_serial_port == ""
    assert s.lsl_stream_type == "EEG"
    assert s.lsl_buffer_seconds == 5.0


def test_earthsync_url_not_lucid_port() -> None:
    """EarthSync URL default must not point at Lucid's own port."""
    s = Settings()
    assert str(s.port) not in s.earthsync_url
    assert s.earthsync_station_id == "simulator1"


def test_get_settings_is_cached() -> None:
    """get_settings() returns a cached singleton."""
    assert get_settings() is get_settings()
