"""EarthSync API client -- fetches live SR data for neurofeedback entrainment."""

from __future__ import annotations

import re
from urllib.parse import urlparse

import httpx
import structlog

logger = structlog.get_logger(__name__)

# Schumann Resonance Mode-1 fundamental and the window in which a detected
# peak is accepted as the fundamental. Peaks outside this band (sub-fundamental
# noise, higher modes) are ignored in favour of the canonical 7.83 Hz.
SR_FUNDAMENTAL_HZ = 7.83
SR_MODE1_LOW_HZ = 6.5
SR_MODE1_HIGH_HZ = 9.0

_STATION_ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")
_ALLOWED_SCHEMES = ("http", "https")


class EarthSyncClient:
    """Fetches live Schumann Resonance state from an EarthSync server.

    Used by the neurofeedback engine to dynamically adjust the target
    frequency band based on the actual SR fundamental measured by a
    real or simulated station.

    A single :class:`httpx.AsyncClient` is created lazily and reused across
    polls (keep-alive); call :meth:`aclose` when finished.
    """

    def __init__(self, base_url: str, station_id: str = "simulator1") -> None:
        self._base_url = self._validate_base_url(base_url)
        self._station_id = self._validate_station_id(station_id)
        self._last_sr_freq: float = SR_FUNDAMENTAL_HZ
        self._last_sr_amp: float = 0.0
        self._client: httpx.AsyncClient | None = None
        #: True after a fetch that fell back to the static 7.83 Hz default
        #: (non-200, empty peaks, or no in-band peak).
        self.degraded: bool = False

    @staticmethod
    def _validate_base_url(base_url: str) -> str:
        parsed = urlparse(base_url)
        if parsed.scheme not in _ALLOWED_SCHEMES or not parsed.hostname:
            msg = f"Unsupported EarthSync URL: {base_url!r} (need http(s) with a host)"
            raise ValueError(msg)
        return base_url.rstrip("/")

    @staticmethod
    def _validate_station_id(station_id: str) -> str:
        if not _STATION_ID_RE.match(station_id):
            msg = f"Invalid station_id: {station_id!r}"
            raise ValueError(msg)
        return station_id

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=5.0)
        return self._client

    async def aclose(self) -> None:
        """Close the underlying HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    @staticmethod
    def _select_fundamental(peaks: list[dict]) -> dict | None:
        """Return the peak closest to 7.83 Hz within the Mode-1 window, or None."""
        in_band = [p for p in peaks if SR_MODE1_LOW_HZ <= p.get("freq", -1.0) <= SR_MODE1_HIGH_HZ]
        if not in_band:
            return None
        return min(in_band, key=lambda p: abs(p.get("freq", 999.0) - SR_FUNDAMENTAL_HZ))

    async def fetch_sr_state(self) -> dict:
        """Fetch current SR state from EarthSync public API.

        Returns dict with freq, amp, q_factor keys. On any failure (network
        error, non-200, empty peaks, or no in-band peak) the last known values
        are returned, ``self.degraded`` is set, and a warning is logged.
        """
        url = f"{self._base_url}/api/public/stations/{self._station_id}/latest"
        self.degraded = False
        try:
            client = self._get_client()
            resp = await client.get(url)
            if resp.status_code != 200:
                logger.warning(
                    "earthsync_non_200",
                    status_code=resp.status_code,
                    station=self._station_id,
                    url=url,
                )
                self.degraded = True
                return self._fallback()

            peaks = resp.json().get("peaks", [])
            if not peaks:
                logger.warning("earthsync_empty_peaks", station=self._station_id, url=url)
                self.degraded = True
                return self._fallback()

            mode1 = self._select_fundamental(peaks)
            if mode1 is None:
                logger.warning("earthsync_no_mode1_peak", station=self._station_id, url=url)
                self.degraded = True
                return self._fallback()

            self._last_sr_freq = float(mode1.get("freq", SR_FUNDAMENTAL_HZ))
            self._last_sr_amp = float(mode1.get("amp", 0.0))
            return {
                "freq": self._last_sr_freq,
                "amp": self._last_sr_amp,
                "q_factor": mode1.get("q_factor"),
            }
        except httpx.HTTPError:
            logger.warning("earthsync_fetch_failed", station=self._station_id, url=url)
            self.degraded = True
            return self._fallback()

    def _fallback(self) -> dict:
        return {"freq": self._last_sr_freq, "amp": self._last_sr_amp, "q_factor": None}

    @property
    def current_frequency(self) -> float:
        """Last known SR fundamental frequency in Hz."""
        return self._last_sr_freq

    @property
    def station_id(self) -> str:
        return self._station_id
