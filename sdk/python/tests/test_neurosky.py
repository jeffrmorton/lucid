"""Tests for NeuroSky ThinkGear protocol driver."""

import struct

from lucid.neurosky import (
    BAND_NAMES,
    CODE_ATTENTION,
    CODE_BAND_POWERS,
    CODE_MEDITATION,
    CODE_RAW_EEG,
    CODE_SIGNAL_QUALITY,
    SYNC_BYTE,
    NeuroSkyDevice,
    ThinkGearPacket,
    parse_payload,
    parse_stream,
)


def _make_packet(payload: bytes) -> bytes:
    """Build a complete ThinkGear packet with sync, length, and checksum."""
    checksum = (~sum(payload)) & 0xFF
    return bytes([SYNC_BYTE, SYNC_BYTE, len(payload)]) + payload + bytes([checksum])


# --- ThinkGearPacket defaults ---


def test_packet_defaults() -> None:
    pkt = ThinkGearPacket()
    assert pkt.signal_quality == 200
    assert pkt.attention == 0
    assert pkt.meditation == 0
    assert pkt.raw_eeg == 0
    assert pkt.band_powers == {}
    assert not pkt.has_raw
    assert not pkt.has_attention
    assert not pkt.has_bands


# --- parse_payload ---


def test_parse_signal_quality() -> None:
    payload = bytes([CODE_SIGNAL_QUALITY, 0])  # Good quality
    pkt = parse_payload(payload)
    assert pkt.signal_quality == 0


def test_parse_signal_quality_bad() -> None:
    payload = bytes([CODE_SIGNAL_QUALITY, 200])  # No contact
    pkt = parse_payload(payload)
    assert pkt.signal_quality == 200


def test_parse_attention() -> None:
    payload = bytes([CODE_ATTENTION, 75])
    pkt = parse_payload(payload)
    assert pkt.attention == 75
    assert pkt.has_attention


def test_parse_meditation() -> None:
    payload = bytes([CODE_MEDITATION, 60])
    pkt = parse_payload(payload)
    assert pkt.meditation == 60


def test_parse_raw_eeg() -> None:
    raw_value = 1234
    raw_bytes = struct.pack(">h", raw_value)
    payload = bytes([CODE_RAW_EEG, 2]) + raw_bytes
    pkt = parse_payload(payload)
    assert pkt.raw_eeg == 1234
    assert pkt.has_raw


def test_parse_raw_eeg_negative() -> None:
    raw_value = -500
    raw_bytes = struct.pack(">h", raw_value)
    payload = bytes([CODE_RAW_EEG, 2]) + raw_bytes
    pkt = parse_payload(payload)
    assert pkt.raw_eeg == -500


def test_parse_band_powers() -> None:
    # 8 bands x 3 bytes each = 24 bytes
    band_data = bytearray()
    for i in range(8):
        value = (i + 1) * 1000
        band_data.append((value >> 16) & 0xFF)
        band_data.append((value >> 8) & 0xFF)
        band_data.append(value & 0xFF)
    payload = bytes([CODE_BAND_POWERS, 24]) + bytes(band_data)
    pkt = parse_payload(payload)
    assert pkt.has_bands
    assert len(pkt.band_powers) == 8
    assert pkt.band_powers["delta"] == 1000
    assert pkt.band_powers["theta"] == 2000
    assert pkt.band_powers["high_gamma"] == 8000


def test_parse_combined_payload() -> None:
    payload = bytes(
        [
            CODE_SIGNAL_QUALITY,
            0,
            CODE_ATTENTION,
            85,
            CODE_MEDITATION,
            70,
        ]
    )
    pkt = parse_payload(payload)
    assert pkt.signal_quality == 0
    assert pkt.attention == 85
    assert pkt.meditation == 70
    assert pkt.has_attention


def test_parse_empty_payload() -> None:
    pkt = parse_payload(b"")
    assert pkt.signal_quality == 200
    assert not pkt.has_raw


def test_parse_truncated_single_byte_code() -> None:
    # Single-byte code with no value following
    payload = bytes([CODE_ATTENTION])
    pkt = parse_payload(payload)
    assert pkt.attention == 0  # Default, not parsed


def test_parse_truncated_multi_byte_code() -> None:
    # Multi-byte code with no length following
    payload = bytes([CODE_RAW_EEG])
    pkt = parse_payload(payload)
    assert not pkt.has_raw


def test_parse_multi_byte_insufficient_data() -> None:
    # Multi-byte code with length but not enough data
    payload = bytes([CODE_RAW_EEG, 2, 0x01])  # Says 2 bytes but only 1
    pkt = parse_payload(payload)
    assert not pkt.has_raw


def test_parse_raw_eeg_wrong_length() -> None:
    # Raw EEG with length != 2 — should be ignored
    payload = bytes([CODE_RAW_EEG, 3, 0x00, 0x00, 0x00])
    pkt = parse_payload(payload)
    assert not pkt.has_raw


def test_parse_band_powers_wrong_length() -> None:
    # Band powers with length != 24 — should be ignored
    payload = bytes([CODE_BAND_POWERS, 12]) + bytes(12)
    pkt = parse_payload(payload)
    assert not pkt.has_bands


# --- parse_stream ---


def test_parse_stream_single_packet() -> None:
    payload = bytes([CODE_ATTENTION, 90])
    data = _make_packet(payload)
    packets = list(parse_stream(data))
    assert len(packets) == 1
    assert packets[0].attention == 90


def test_parse_stream_multiple_packets() -> None:
    p1 = _make_packet(bytes([CODE_ATTENTION, 80]))
    p2 = _make_packet(bytes([CODE_ATTENTION, 95]))
    packets = list(parse_stream(p1 + p2))
    assert len(packets) == 2
    assert packets[0].attention == 80
    assert packets[1].attention == 95


def test_parse_stream_with_garbage() -> None:
    garbage = bytes([0x00, 0xFF, 0x12, 0x34])
    p1 = _make_packet(bytes([CODE_ATTENTION, 50]))
    packets = list(parse_stream(garbage + p1))
    assert len(packets) == 1
    assert packets[0].attention == 50


def test_parse_stream_bad_checksum() -> None:
    payload = bytes([CODE_ATTENTION, 50])
    pkt = bytes([SYNC_BYTE, SYNC_BYTE, len(payload)]) + payload + bytes([0xFF])  # Wrong checksum
    packets = list(parse_stream(pkt))
    assert len(packets) == 0


def test_parse_stream_incomplete_packet() -> None:
    # Packet that's cut off before checksum
    data = bytes([SYNC_BYTE, SYNC_BYTE, 2, CODE_ATTENTION])  # Missing value + checksum
    packets = list(parse_stream(data))
    assert len(packets) == 0


def test_parse_stream_invalid_length() -> None:
    # Length > 169 is invalid
    data = bytes([SYNC_BYTE, SYNC_BYTE, 200, 0x00])
    packets = list(parse_stream(data))
    assert len(packets) == 0


def test_parse_stream_empty() -> None:
    packets = list(parse_stream(b""))
    assert len(packets) == 0


def test_parse_stream_too_short() -> None:
    packets = list(parse_stream(bytes([SYNC_BYTE])))
    assert len(packets) == 0


# --- NeuroSkyDevice ---


def test_device_creation() -> None:
    device = NeuroSkyDevice("/dev/rfcomm0")
    assert device.port == "/dev/rfcomm0"
    assert device.baudrate == 57600
    assert not device.connected


def test_device_custom_baudrate() -> None:
    device = NeuroSkyDevice("COM3", baudrate=9600)
    assert device.baudrate == 9600


def test_device_read_not_connected() -> None:
    device = NeuroSkyDevice("/dev/rfcomm0")
    device._pyserial_available = True
    packets = device.read()
    assert packets == []


def test_device_connect_no_pyserial() -> None:
    device = NeuroSkyDevice("/dev/rfcomm0")
    device._pyserial_available = False
    assert not device.connect()
    assert not device.is_available


def test_device_disconnect_not_connected() -> None:
    device = NeuroSkyDevice("/dev/rfcomm0")
    device.disconnect()  # Should not raise
    assert not device.connected


def test_to_lucid_band_powers() -> None:
    device = NeuroSkyDevice("/dev/rfcomm0")
    pkt = ThinkGearPacket(
        band_powers={
            "delta": 1000,
            "theta": 2000,
            "low_alpha": 3000,
            "high_alpha": 4000,
            "low_beta": 1500,
            "high_beta": 2500,
            "low_gamma": 500,
            "high_gamma": 800,
        }
    )
    bp = device.to_lucid_band_powers(pkt)
    assert bp["delta"] == 1000.0
    assert bp["theta"] == 2000.0
    assert bp["alpha"] == 7000.0  # low_alpha + high_alpha
    assert bp["beta"] == 4000.0  # low_beta + high_beta
    assert bp["gamma"] == 1300.0  # low_gamma + high_gamma


def test_to_lucid_band_powers_empty() -> None:
    device = NeuroSkyDevice("/dev/rfcomm0")
    pkt = ThinkGearPacket()
    bp = device.to_lucid_band_powers(pkt)
    assert bp["delta"] == 0.0
    assert bp["alpha"] == 0.0


def test_band_names_count() -> None:
    assert len(BAND_NAMES) == 8


def test_read_until_attention_not_connected() -> None:
    device = NeuroSkyDevice("/dev/rfcomm0")
    device._pyserial_available = True
    result = device.read_until_attention(timeout_s=0.1)
    assert result is None


def test_device_connect_success() -> None:
    """Test connect with mocked pyserial."""
    from unittest.mock import patch

    device = NeuroSkyDevice("/dev/rfcomm0")
    device._pyserial_available = True

    with patch("lucid.neurosky.NeuroSkyDevice.connect") as mock_connect:
        mock_connect.return_value = True
        assert device.connect()


def test_device_connect_failure() -> None:
    """Test connect when serial port doesn't exist."""
    from unittest.mock import MagicMock, patch

    device = NeuroSkyDevice("/dev/nonexistent")
    device._pyserial_available = True

    # Mock serial to raise
    mock_serial_class = MagicMock(side_effect=Exception("No such port"))
    with patch.dict("sys.modules", {"serial": MagicMock(Serial=mock_serial_class)}):
        result = device.connect()
        assert not result


def test_device_read_with_mock_serial() -> None:
    """Test read with mocked serial returning valid packet."""
    from unittest.mock import MagicMock

    device = NeuroSkyDevice("/dev/rfcomm0")
    device._pyserial_available = True
    device.connected = True

    payload = bytes([CODE_ATTENTION, 88])
    packet_bytes = _make_packet(payload)

    mock_serial = MagicMock()
    mock_serial.read.return_value = packet_bytes
    mock_serial.is_open = True
    device.serial = mock_serial

    packets = device.read()
    assert len(packets) == 1
    assert packets[0].attention == 88


def test_device_read_empty_serial() -> None:
    """Test read when serial returns no data."""
    from unittest.mock import MagicMock

    device = NeuroSkyDevice("/dev/rfcomm0")
    device._pyserial_available = True
    device.connected = True

    mock_serial = MagicMock()
    mock_serial.read.return_value = b""
    device.serial = mock_serial

    packets = device.read()
    assert packets == []


def test_device_disconnect_with_serial() -> None:
    """Test disconnect closes serial port."""
    from unittest.mock import MagicMock

    device = NeuroSkyDevice("/dev/rfcomm0")
    device.connected = True
    mock_serial = MagicMock()
    mock_serial.is_open = True
    device.serial = mock_serial

    device.disconnect()
    mock_serial.close.assert_called_once()
    assert not device.connected
    assert device.serial is None


def test_read_until_attention_with_data() -> None:
    """Test read_until_attention returns packet with attention data."""
    from unittest.mock import MagicMock

    device = NeuroSkyDevice("/dev/rfcomm0")
    device._pyserial_available = True
    device.connected = True

    payload = bytes([CODE_ATTENTION, 77])
    packet_bytes = _make_packet(payload)

    mock_serial = MagicMock()
    mock_serial.read.return_value = packet_bytes
    mock_serial.is_open = True
    device.serial = mock_serial

    pkt = device.read_until_attention(timeout_s=1.0)
    assert pkt is not None
    assert pkt.attention == 77
