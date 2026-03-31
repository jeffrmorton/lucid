"""EarthSync API client -- fetches live SR data for neurofeedback entrainment."""

from __future__ import annotations

import logging

import httpx

logger = logging.getLogger(__name__)


class EarthSyncClient:
    """Fetches live Schumann Resonance state from an EarthSync server.

    Used by the neurofeedback engine to dynamically adjust the target
    frequency band based on the actual SR fundamental measured by a
    real or simulated station.
    """

    def __init__(self, base_url: str, station_id: str = "simulator1"):
        self._base_url = base_url.rstrip("/")
        self._station_id = station_id
        self._last_sr_freq: float = 7.83
        self._last_sr_amp: float = 0.0

    async def fetch_sr_state(self) -> dict:
        """Fetch current SR state from EarthSync public API.

        Returns dict with freq, amp, q_factor keys.
        Falls back to last known values on error.
        """
        url = f"{self._base_url}/api/public/stations/{self._station_id}/latest"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    peaks = data.get("peaks", [])
                    if peaks:
                        mode1 = min(peaks, key=lambda p: p.get("freq", 999))
                        self._last_sr_freq = float(mode1.get("freq", 7.83))
                        self._last_sr_amp = float(mode1.get("amp", 0.0))
                        return {
                            "freq": self._last_sr_freq,
                            "amp": self._last_sr_amp,
                            "q_factor": mode1.get("q_factor"),
                        }
        except Exception:
            logger.warning("earthsync_fetch_failed station=%s", self._station_id)
        return {"freq": self._last_sr_freq, "amp": self._last_sr_amp, "q_factor": None}

    @property
    def current_frequency(self) -> float:
        """Last known SR fundamental frequency in Hz."""
        return self._last_sr_freq

    @property
    def station_id(self) -> str:
        return self._station_id
