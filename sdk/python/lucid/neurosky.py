"""NeuroSky ThinkGear protocol driver for MindWave devices.

Implements the ThinkGear Serial Stream Protocol to connect to NeuroSky
MindWave, MindWave Mobile 2, and compatible devices (e.g., Macrotellect
BrainLink Lite) over Bluetooth SPP or USB serial.

Protocol reference: https://developer.neurosky.com/docs/doku.php?id=thinkgear_communications_protocol

The ThinkGear protocol uses:
- Sync bytes: 0xAA 0xAA
- Payload length: 1 byte (0-169)
- Payload: variable-length code/value pairs
- Checksum: ~(sum of payload bytes) & 0xFF

Data codes:
  0x02: Signal quality (0=good, 200=no contact)
  0x04: Attention (0-100)
  0x05: Meditation (0-100)
  0x80: Raw EEG (2 bytes, big-endian signed int16, 512 SPS)
  0x83: Band powers (8 x 3-byte unsigned integers)
"""

from __future__ import annotations

import struct
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator

# ThinkGear protocol constants
SYNC_BYTE = 0xAA
CODE_SIGNAL_QUALITY = 0x02
CODE_ATTENTION = 0x04
CODE_MEDITATION = 0x05
CODE_RAW_EEG = 0x80
CODE_BAND_POWERS = 0x83

BAND_NAMES = [
    "delta",
    "theta",
    "low_alpha",
    "high_alpha",
    "low_beta",
    "high_beta",
    "low_gamma",
    "high_gamma",
]


@dataclass
class ThinkGearPacket:
    """Parsed ThinkGear data packet."""

    signal_quality: int = 200  # 0 = good, 200 = no sensor contact
    attention: int = 0  # 0-100
    meditation: int = 0  # 0-100
    raw_eeg: int = 0  # signed int16 (-32768 to 32767)
    band_powers: dict[str, int] = field(default_factory=dict)
    has_raw: bool = False
    has_attention: bool = False
    has_bands: bool = False


def parse_payload(payload: bytes) -> ThinkGearPacket:
    """Parse a ThinkGear payload into a structured packet.

    Args:
        payload: Raw payload bytes (after sync and length, before checksum).

    Returns:
        Parsed ThinkGearPacket.
    """
    packet = ThinkGearPacket()
    i = 0

    while i < len(payload):
        code = payload[i]
        i += 1

        if code < 0x80:
            # Single-byte value codes
            if i >= len(payload):
                break
            value = payload[i]
            i += 1

            if code == CODE_SIGNAL_QUALITY:
                packet.signal_quality = value
            elif code == CODE_ATTENTION:
                packet.attention = value
                packet.has_attention = True
            elif code == CODE_MEDITATION:
                packet.meditation = value
        else:
            # Multi-byte value codes: next byte is length
            if i >= len(payload):
                break
            length = payload[i]
            i += 1

            if i + length > len(payload):
                break

            data = payload[i : i + length]
            i += length

            if code == CODE_RAW_EEG and length == 2:
                packet.raw_eeg = struct.unpack(">h", data)[0]
                packet.has_raw = True
            elif code == CODE_BAND_POWERS and length == 24:
                # 8 bands x 3 bytes each (big-endian unsigned)
                for band_idx in range(8):
                    offset = band_idx * 3
                    value = (data[offset] << 16) | (data[offset + 1] << 8) | data[offset + 2]
                    packet.band_powers[BAND_NAMES[band_idx]] = value
                packet.has_bands = True

    return packet


def parse_stream(data: bytes) -> Generator[ThinkGearPacket]:
    """Parse a byte stream for ThinkGear packets.

    Yields parsed packets as they are found in the data.

    Args:
        data: Raw bytes from serial port.

    Yields:
        ThinkGearPacket for each valid packet found.
    """
    i = 0
    while i < len(data) - 3:
        # Find sync bytes
        if data[i] != SYNC_BYTE or data[i + 1] != SYNC_BYTE:
            i += 1
            continue

        # Read payload length
        plen = data[i + 2]
        if plen > 169:  # Max valid payload length
            i += 1
            continue

        # Check we have enough data
        if i + 3 + plen + 1 > len(data):
            break  # Incomplete packet, wait for more data

        payload = data[i + 3 : i + 3 + plen]
        checksum_byte = data[i + 3 + plen]

        # Verify checksum: ~(sum of payload) & 0xFF
        expected = (~sum(payload)) & 0xFF
        if checksum_byte != expected:
            i += 1
            continue

        yield parse_payload(payload)
        i += 3 + plen + 1


class NeuroSkyDevice:
    """Connect to a NeuroSky MindWave device over Bluetooth serial.

    Usage:
        device = NeuroSkyDevice("/dev/rfcomm0")  # or COM3 on Windows
        device.connect()
        while True:
            packets = device.read()
            for pkt in packets:
                if pkt.has_attention:
                    print(f"Attention: {pkt.attention}")
                if pkt.has_raw:
                    print(f"Raw EEG: {pkt.raw_eeg}")
        device.disconnect()
    """

    def __init__(self, port: str, baudrate: int = 57600, timeout: float = 1.0) -> None:
        """Initialize device connection.

        Args:
            port: Serial port (e.g., "/dev/rfcomm0", "COM3").
            baudrate: Baud rate (57600 for MindWave Mobile 2, 9600 for original).
            timeout: Read timeout in seconds.
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
        self.connected = False
        self._pyserial_available = self._check_pyserial()

    def _check_pyserial(self) -> bool:  # pragma: no cover
        """Check if pyserial is installed."""
        try:
            import serial  # noqa: F401, PLC0415

            return True  # noqa: TRY300
        except ImportError:
            return False

    @property
    def is_available(self) -> bool:
        """Whether pyserial is installed."""
        return self._pyserial_available

    def connect(self) -> bool:
        """Open serial connection to the device.

        Returns:
            True if connected successfully.
        """
        if not self._pyserial_available:
            return False

        import serial  # noqa: PLC0415

        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
            )
            self.connected = True  # pragma: no cover
            return True  # pragma: no cover  # noqa: TRY300
        except Exception:
            self.connected = False
            return False

    def disconnect(self) -> None:
        """Close the serial connection."""
        if self.serial and self.serial.is_open:
            self.serial.close()
        self.serial = None
        self.connected = False

    def read(self, max_bytes: int = 1024) -> list[ThinkGearPacket]:
        """Read and parse available data from the device.

        Args:
            max_bytes: Maximum bytes to read per call.

        Returns:
            List of parsed packets (may be empty if no complete packets available).
        """
        if not self.connected or not self.serial:
            return []

        raw = self.serial.read(max_bytes)
        if not raw:
            return []

        return list(parse_stream(raw))

    def read_until_attention(self, timeout_s: float = 10.0) -> ThinkGearPacket | None:
        """Read packets until one with attention/meditation data is received.

        Args:
            timeout_s: Maximum wait time.

        Returns:
            Packet with attention data, or None on timeout.
        """
        start = time.monotonic()
        while time.monotonic() - start < timeout_s:
            packets = self.read()
            for pkt in packets:
                if pkt.has_attention:
                    return pkt
        return None

    def to_lucid_band_powers(self, packet: ThinkGearPacket) -> dict[str, float]:
        """Convert ThinkGear band powers to Lucid standard format.

        ThinkGear reports 8 bands; Lucid uses 5. We combine:
        - delta = delta
        - theta = theta
        - alpha = low_alpha + high_alpha
        - beta = low_beta + high_beta
        - gamma = low_gamma + high_gamma

        Returns:
            Dict with keys delta, theta, alpha, beta, gamma.
        """
        bp = packet.band_powers
        return {
            "delta": float(bp.get("delta", 0)),
            "theta": float(bp.get("theta", 0)),
            "alpha": float(bp.get("low_alpha", 0) + bp.get("high_alpha", 0)),
            "beta": float(bp.get("low_beta", 0) + bp.get("high_beta", 0)),
            "gamma": float(bp.get("low_gamma", 0) + bp.get("high_gamma", 0)),
        }
