"""Lucid Server configuration."""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Server settings loaded from LUCID_-prefixed environment variables."""

    model_config = {"env_prefix": "LUCID_"}

    # --- Server ---
    host: str = "0.0.0.0"  # noqa: S104
    port: int = 3001
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # --- EEG processing ---
    sample_rate: int = 250
    n_channels: int = 8
    notch_freq: float = 60.0  # 50.0 for EU
    bandpass_low: float = 0.5
    bandpass_high: float = 100.0

    # --- EarthSync SR integration ---
    # Default points at a bare EarthSync run (uvicorn default port 8000).
    # Must NOT equal Lucid's own `port` (3001) or the client would poll Lucid itself.
    # In Docker, set LUCID_EARTHSYNC_URL to the EarthSync service address
    # (e.g. http://earthsync-server:3000 on a shared network).
    earthsync_url: str = "http://localhost:8000"
    earthsync_station_id: str = "simulator1"

    # --- Device — BrainFlow board ID (-1 = synthetic, 0 = OpenBCI Cyton, 22 = Muse 2, etc.) ---
    brainflow_board_id: int = -1
    brainflow_serial_port: str = ""

    # --- LSL ---
    lsl_stream_type: str = "EEG"
    lsl_buffer_seconds: float = 5.0


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance.

    Using a cached accessor (instead of a module-level singleton) avoids
    import-time side effects and lets tests override env then call
    ``get_settings.cache_clear()``.
    """
    return Settings()


# Backward-compatible module alias; prefer get_settings() in new code.
settings = get_settings()
