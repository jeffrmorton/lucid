"""Lab Streaming Layer (LSL) inlet for receiving EEG data.

LSL is the de facto standard protocol for real-time multi-device
physiological data streaming in research settings. Supports 60+
EEG devices via native manufacturer software or adapters.

Reference: https://labstreaminglayer.readthedocs.io/
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from numpy.typing import NDArray

pylsl: Any
try:
    import pylsl  # type: ignore[no-redef]  # pragma: no cover

    _PYLSL_AVAILABLE = True  # pragma: no cover
except ImportError:
    pylsl = None
    _PYLSL_AVAILABLE = False


class LSLInlet:
    """Receives EEG data from an LSL stream.

    Resolves LSL streams of type 'EEG' on the local network,
    connects to the first matching stream, and pulls samples.

    Falls back gracefully if pylsl is not installed.
    """

    def __init__(self, stream_type: str = "EEG", buffer_seconds: float = 5.0) -> None:
        self.stream_type = stream_type
        self.buffer_seconds = buffer_seconds
        self.inlet: Any = None
        self.stream_info: Any = None
        self.connected = False

    @property
    def is_available(self) -> bool:
        return _PYLSL_AVAILABLE

    def resolve_streams(self) -> list[dict]:
        """Find available LSL streams on the network.

        Returns:
            List of stream info dicts with name, type, channel_count, sample_rate.
        """
        if not _PYLSL_AVAILABLE:
            return []

        streams = pylsl.resolve_streams(wait_time=2.0)  # pragma: no cover
        return [  # pragma: no cover
            {
                "name": s.name(),
                "type": s.type(),
                "channel_count": s.channel_count(),
                "sample_rate": s.nominal_srate(),
                "source_id": s.source_id(),
            }
            for s in streams
            if s.type() == self.stream_type
        ]

    def connect(self, stream_name: str | None = None) -> bool:
        """Connect to an LSL stream.

        Args:
            stream_name: Specific stream name. None = first matching stream.

        Returns:
            True if connected, False if pylsl unavailable or no stream found.
        """
        if not _PYLSL_AVAILABLE:
            return False

        if stream_name:  # pragma: no cover
            streams = pylsl.resolve_byprop("name", stream_name, timeout=5.0)
        else:  # pragma: no cover
            streams = pylsl.resolve_byprop("type", self.stream_type, timeout=5.0)

        if not streams:  # pragma: no cover
            return False

        self.stream_info = streams[0]  # pragma: no cover
        max_buf = int(self.buffer_seconds * self.stream_info.nominal_srate())  # pragma: no cover
        self.inlet = pylsl.StreamInlet(  # pragma: no cover
            self.stream_info, max_buflen=max_buf
        )
        self.connected = True  # pragma: no cover
        return True  # pragma: no cover

    def disconnect(self) -> None:
        """Disconnect from the LSL stream."""
        if self.inlet:
            self.inlet.close_stream()  # pragma: no cover
        self.inlet = None
        self.stream_info = None
        self.connected = False

    def pull_chunk(self, max_samples: int = 250) -> tuple[NDArray[np.float64], list[float]] | None:
        """Pull a chunk of samples from the stream.

        Args:
            max_samples: Maximum samples to pull.

        Returns:
            (data, timestamps) tuple where data is (n_channels, n_samples),
            or None if not connected or no data.
        """
        if not self.connected or not self.inlet:
            return None

        samples, timestamps = self.inlet.pull_chunk(  # pragma: no cover
            max_samples=max_samples, timeout=0.0
        )
        if not samples:  # pragma: no cover
            return None

        data = np.array(samples, dtype=np.float64).T  # pragma: no cover
        return data, timestamps  # pragma: no cover

    def get_channel_count(self) -> int:
        if self.stream_info:
            return self.stream_info.channel_count()  # pragma: no cover
        return 0

    def get_sample_rate(self) -> float:
        if self.stream_info:
            return self.stream_info.nominal_srate()  # pragma: no cover
        return 0.0
