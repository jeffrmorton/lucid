"""Lucid Server configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Server settings loaded from environment variables."""

    host: str = "0.0.0.0"  # noqa: S104
    port: int = 3001
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    database_url: str = "sqlite:///./lucid.db"
    log_level: str = "info"

    # EEG processing
    sample_rate: int = 250
    n_channels: int = 8
    notch_freq: float = 60.0  # 50.0 for EU
    bandpass_low: float = 0.5
    bandpass_high: float = 100.0

    # ASR
    asr_threshold: float = 5.0
    asr_calibration_seconds: int = 30

    # EarthSync SR integration
    earthsync_url: str = "http://localhost:3001"

    # Device — BrainFlow board ID (-1 = synthetic, 0 = OpenBCI Cyton, 22 = Muse 2, etc.)
    brainflow_board_id: int = -1
    brainflow_serial_port: str = ""

    # LSL
    lsl_stream_type: str = "EEG"
    lsl_buffer_seconds: float = 5.0

    model_config = {"env_prefix": "LUCID_"}


settings = Settings()
