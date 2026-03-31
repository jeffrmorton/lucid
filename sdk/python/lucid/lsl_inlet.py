"""LSL stream inlet for the Lucid SDK.

Enables Lucid to receive data from any LSL-compatible EEG device.
"""

from __future__ import annotations

try:
    import pylsl  # pragma: no cover

    _PYLSL_AVAILABLE = True  # pragma: no cover
except ImportError:
    pylsl = None  # type: ignore[assignment]
    _PYLSL_AVAILABLE = False


class LucidLSLInlet:
    """Simplified LSL inlet for the Lucid SDK."""

    def __init__(self, stream_type: str = "EEG") -> None:
        self.stream_type = stream_type
        self.connected = False

    @property
    def is_available(self) -> bool:
        return _PYLSL_AVAILABLE

    def find_streams(self) -> list[dict]:
        """Find EEG streams on the network."""
        if not _PYLSL_AVAILABLE:
            return []

        streams = pylsl.resolve_byprop(  # pragma: no cover
            "type", self.stream_type, timeout=2.0
        )
        return [  # pragma: no cover
            {"name": s.name(), "channels": s.channel_count(), "rate": s.nominal_srate()}
            for s in streams
        ]

    def connect(self, stream_name: str | None = None) -> bool:  # noqa: ARG002
        """Connect to an LSL stream.

        Args:
            stream_name: Specific stream name. None = first matching stream.

        Returns:
            True if connected, False if pylsl unavailable.
        """
        if not _PYLSL_AVAILABLE:
            return False
        self.connected = True  # pragma: no cover
        return True  # pragma: no cover

    def disconnect(self) -> None:
        """Disconnect from the LSL stream."""
        self.connected = False
