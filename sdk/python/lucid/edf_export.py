"""EDF+ file export for EEG recordings.

Implements the European Data Format (EDF+) specification for storing
multi-channel time-series physiological data. This is the universal
standard format accepted by all EEG analysis software.

Reference: https://www.edfplus.info/specs/edf.html

Pure Python implementation -- no external dependencies.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, BinaryIO

import numpy as np

if TYPE_CHECKING:
    from numpy.typing import NDArray


def _pad(s: str, length: int) -> bytes:
    """Pad string to exact byte length with spaces."""
    return s[:length].ljust(length).encode("ascii")


@dataclass
class EDFConfig:
    """Configuration for EDF+ file writing."""

    patient_id: str = "X"
    recording_id: str = "X"
    start_time: datetime.datetime | None = None
    physical_min: float = -3200.0
    physical_max: float = 3200.0
    digital_min: int = -32768
    digital_max: int = 32767
    transducer_type: str = "AgAgCl electrode"
    physical_dimension: str = "uV"


@dataclass
class _EDFWriteParams:
    """Computed parameters for writing an EDF file."""

    n_channels: int
    n_samples: int
    n_records: int
    samples_per_record: int
    header_bytes: int
    scale: float
    offset: float
    start_time: datetime.datetime
    channel_names: list[str]


def _write_main_header(f: BinaryIO, config: EDFConfig, params: _EDFWriteParams) -> None:
    """Write the 256-byte EDF main header."""
    f.write(_pad("0", 8))  # Version
    f.write(_pad(config.patient_id, 80))
    f.write(_pad(config.recording_id, 80))
    f.write(_pad(params.start_time.strftime("%d.%m.%y"), 8))
    f.write(_pad(params.start_time.strftime("%H.%M.%S"), 8))
    f.write(_pad(str(params.header_bytes), 8))
    f.write(_pad("EDF+C", 44))  # EDF+ continuous
    f.write(_pad(str(params.n_records), 8))
    f.write(_pad("1", 8))  # 1-second records
    f.write(_pad(str(params.n_channels), 4))


def _write_channel_headers(f: BinaryIO, config: EDFConfig, params: _EDFWriteParams) -> None:
    """Write channel header fields (n_channels x 256 bytes total)."""
    nc = params.n_channels
    for name in params.channel_names:
        f.write(_pad(name, 16))
    for _ in range(nc):
        f.write(_pad(config.transducer_type, 80))
    for _ in range(nc):
        f.write(_pad(config.physical_dimension, 8))
    for _ in range(nc):
        f.write(_pad(f"{config.physical_min:.1f}", 8))
    for _ in range(nc):
        f.write(_pad(f"{config.physical_max:.1f}", 8))
    for _ in range(nc):
        f.write(_pad(str(config.digital_min), 8))
    for _ in range(nc):
        f.write(_pad(str(config.digital_max), 8))
    for _ in range(nc):
        f.write(_pad("", 80))  # Prefiltering
    for _ in range(nc):
        f.write(_pad(str(params.samples_per_record), 8))
    for _ in range(nc):
        f.write(_pad("", 32))  # Reserved


def _write_data_records(
    f: BinaryIO, data: NDArray[np.float64], config: EDFConfig, params: _EDFWriteParams
) -> None:
    """Write EDF data records."""
    for rec in range(params.n_records):
        start_sample = rec * params.samples_per_record
        end_sample = min(start_sample + params.samples_per_record, params.n_samples)

        for ch in range(params.n_channels):
            chunk = data[ch, start_sample:end_sample]

            # Pad with zeros if last record is incomplete
            if len(chunk) < params.samples_per_record:
                chunk = np.concatenate([chunk, np.zeros(params.samples_per_record - len(chunk))])

            digital = np.clip(
                chunk * params.scale + params.offset, config.digital_min, config.digital_max
            ).astype(np.int16)
            f.write(digital.tobytes())


def write_edf(
    filepath: Path | str,
    data: NDArray[np.float64],
    sample_rate: int,
    channel_names: list[str] | None = None,
    config: EDFConfig | None = None,
) -> Path:
    """Write EEG data to an EDF+ file.

    Args:
        filepath: Output file path.
        data: Shape (n_channels, n_samples). Values in physical units (uV).
        sample_rate: Samples per second.
        channel_names: Channel labels (10-20 system). Auto-generated if None.
        config: EDF configuration. Uses defaults if None.

    Returns:
        Path to the written file.

    Raises:
        ValueError: If data dimensions are invalid.
    """
    filepath = Path(filepath)
    if config is None:
        config = EDFConfig()

    n_channels, n_samples = data.shape

    if n_channels == 0 or n_samples == 0:
        msg = f"Data must have >0 channels and samples, got ({n_channels}, {n_samples})"
        raise ValueError(msg)

    if channel_names is None:
        channel_names = [f"EEG{i + 1}" for i in range(n_channels)]

    if len(channel_names) != n_channels:
        msg = f"channel_names length ({len(channel_names)}) != n_channels ({n_channels})"
        raise ValueError(msg)

    start_time = (
        config.start_time if config.start_time is not None else datetime.datetime.now(datetime.UTC)
    )

    # EDF uses 1-second data records
    samples_per_record = sample_rate
    n_records = int(np.ceil(n_samples / sample_rate))

    # Scale data to digital values
    phys_range = config.physical_max - config.physical_min
    scale = (config.digital_max - config.digital_min) / phys_range
    offset = (
        config.physical_max / phys_range * config.digital_min
        - config.physical_min / phys_range * config.digital_max
    )

    params = _EDFWriteParams(
        n_channels=n_channels,
        n_samples=n_samples,
        n_records=n_records,
        samples_per_record=samples_per_record,
        header_bytes=256 + n_channels * 256,
        scale=scale,
        offset=offset,
        start_time=start_time,
        channel_names=channel_names,
    )

    with filepath.open("wb") as f:
        _write_main_header(f, config, params)
        _write_channel_headers(f, config, params)
        _write_data_records(f, data, config, params)

    return filepath


def read_edf_header(filepath: Path | str) -> dict:
    """Read the header of an EDF file.

    Returns:
        Dict with version, patient_id, recording_id, start_time,
        n_channels, n_records, record_duration, sample_rate, channel_names.
    """
    filepath = Path(filepath)

    with filepath.open("rb") as f:
        version = f.read(8).decode("ascii").strip()
        patient_id = f.read(80).decode("ascii").strip()
        recording_id = f.read(80).decode("ascii").strip()
        start_date = f.read(8).decode("ascii").strip()
        start_time_str = f.read(8).decode("ascii").strip()
        header_bytes = int(f.read(8).decode("ascii").strip())
        reserved = f.read(44).decode("ascii").strip()
        n_records = int(f.read(8).decode("ascii").strip())
        record_duration = float(f.read(8).decode("ascii").strip())
        n_channels = int(f.read(4).decode("ascii").strip())

        channel_names = [f.read(16).decode("ascii").strip() for _ in range(n_channels)]

        # The remaining per-channel header sub-blocks precede samples_per_record.
        # Each is written for ALL channels consecutively (EDF spec):
        #   transducer 80, phys_dim 8, phys_min 8, phys_max 8,
        #   dig_min 8, dig_max 8, prefilter 80  -> 200 bytes per channel.
        f.seek(200 * n_channels, 1)
        samples_per_record = int(f.read(8).decode("ascii").strip())

    sample_rate = samples_per_record / record_duration if record_duration else 0.0

    return {
        "version": version,
        "patient_id": patient_id,
        "recording_id": recording_id,
        "start_date": start_date,
        "start_time": start_time_str,
        "header_bytes": header_bytes,
        "format": reserved,
        "n_records": n_records,
        "record_duration": record_duration,
        "n_channels": n_channels,
        "channel_names": channel_names,
        "samples_per_record": samples_per_record,
        "sample_rate": sample_rate,
    }
