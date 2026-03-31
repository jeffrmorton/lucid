"""Tests for EDF+ export -- pure Python, no external dependencies."""

import datetime
from pathlib import Path

import numpy as np
import pytest
from lucid.edf_export import EDFConfig, _pad, read_edf_header, write_edf


def test_pad_basic() -> None:
    result = _pad("hello", 8)
    assert result == b"hello   "
    assert len(result) == 8


def test_pad_truncates_long_string() -> None:
    result = _pad("abcdefghij", 5)
    assert result == b"abcde"
    assert len(result) == 5


def test_pad_empty_string() -> None:
    result = _pad("", 4)
    assert result == b"    "
    assert len(result) == 4


def test_pad_exact_length() -> None:
    result = _pad("abc", 3)
    assert result == b"abc"
    assert len(result) == 3


def test_write_and_read_header(tmp_path: Path) -> None:
    n_channels, n_samples = 4, 500
    data = np.random.randn(n_channels, n_samples)
    filepath = tmp_path / "test.edf"
    start = datetime.datetime(2025, 6, 15, 10, 30, 0, tzinfo=datetime.UTC)

    config = EDFConfig(
        patient_id="TestPatient",
        recording_id="TestRecording",
        start_time=start,
    )
    result = write_edf(
        filepath,
        data,
        sample_rate=250,
        channel_names=["Fp1", "Fp2", "O1", "O2"],
        config=config,
    )

    assert result == filepath
    assert filepath.exists()

    header = read_edf_header(filepath)
    assert header["version"] == "0"
    assert header["patient_id"] == "TestPatient"
    assert header["recording_id"] == "TestRecording"
    assert header["start_date"] == "15.06.25"
    assert header["start_time"] == "10.30.00"
    assert header["n_channels"] == 4
    assert header["channel_names"] == ["Fp1", "Fp2", "O1", "O2"]
    assert header["format"] == "EDF+C"
    assert header["n_records"] == 2  # 500 samples / 250 Hz = 2 seconds
    assert header["record_duration"] == 1.0


def test_write_auto_channel_names(tmp_path: Path) -> None:
    data = np.random.randn(3, 250)
    filepath = tmp_path / "auto_ch.edf"

    write_edf(filepath, data, sample_rate=250)

    header = read_edf_header(filepath)
    assert header["channel_names"] == ["EEG1", "EEG2", "EEG3"]


def test_write_auto_start_time(tmp_path: Path) -> None:
    data = np.random.randn(2, 250)
    filepath = tmp_path / "auto_time.edf"

    write_edf(filepath, data, sample_rate=250)

    header = read_edf_header(filepath)
    # Should have a valid date string
    assert len(header["start_date"]) == 8
    assert "." in header["start_date"]


def test_write_custom_physical_range(tmp_path: Path) -> None:
    data = np.random.randn(1, 250) * 100  # Smaller amplitude
    filepath = tmp_path / "custom_range.edf"

    config = EDFConfig(
        physical_min=-500.0,
        physical_max=500.0,
        transducer_type="Dry electrode",
        physical_dimension="mV",
    )
    write_edf(filepath, data, sample_rate=250, config=config)

    header = read_edf_header(filepath)
    assert header["n_channels"] == 1
    assert header["n_records"] == 1


def test_write_empty_channels_raises() -> None:
    data = np.zeros((0, 100))
    with pytest.raises(ValueError, match="must have >0 channels"):
        write_edf("/tmp/empty.edf", data, sample_rate=250)  # noqa: S108


def test_write_empty_samples_raises() -> None:
    data = np.zeros((4, 0))
    with pytest.raises(ValueError, match="must have >0 channels"):
        write_edf("/tmp/empty.edf", data, sample_rate=250)  # noqa: S108


def test_write_mismatched_channel_names_raises() -> None:
    data = np.random.randn(4, 250)
    with pytest.raises(ValueError, match="channel_names length"):
        write_edf("/tmp/mismatch.edf", data, sample_rate=250, channel_names=["Fp1", "Fp2"])  # noqa: S108


def test_data_round_trip(tmp_path: Path) -> None:
    """Verify data survives write/read with acceptable quantization error."""
    n_channels, n_samples = 2, 250
    # Use data well within the physical range to avoid clipping
    data = np.random.randn(n_channels, n_samples) * 100  # +/- 100 uV in +/- 3200 range

    filepath = tmp_path / "roundtrip.edf"
    write_edf(filepath, data, sample_rate=250)

    # Read back the raw data records
    header = read_edf_header(filepath)
    header_size = header["header_bytes"]
    samples_per_record = 250

    with filepath.open("rb") as f:
        f.seek(header_size)
        recovered = np.zeros_like(data)

        for rec in range(header["n_records"]):
            for ch in range(n_channels):
                raw_bytes = f.read(samples_per_record * 2)  # int16 = 2 bytes
                digital = np.frombuffer(raw_bytes, dtype=np.int16)

                # Reverse the scaling
                physical_min, physical_max = -3200.0, 3200.0
                digital_min, digital_max = -32768, 32767
                scale = (physical_max - physical_min) / (digital_max - digital_min)
                offset = physical_min - digital_min * scale

                physical = digital.astype(np.float64) * scale + offset

                start = rec * samples_per_record
                end = min(start + samples_per_record, n_samples)
                recovered[ch, start:end] = physical[: end - start]

    # Quantization step: 6400 / 65535 ~ 0.098 uV -- error should be < 0.1 uV
    max_error = np.max(np.abs(data - recovered))
    assert max_error < 0.1, f"Max quantization error {max_error:.4f} uV exceeds 0.1 uV"


def test_incomplete_last_record_padding(tmp_path: Path) -> None:
    """Test that incomplete final data record is zero-padded correctly."""
    n_channels = 2
    n_samples = 300  # 300 / 250 Hz = 1.2s -> 2 records, second record has 50 real + 200 padded
    data = np.ones((n_channels, n_samples)) * 50.0  # constant 50 uV

    filepath = tmp_path / "padded.edf"
    write_edf(filepath, data, sample_rate=250)

    header = read_edf_header(filepath)
    assert header["n_records"] == 2  # ceil(1.2) = 2

    # Verify file size: header + 2 records * 2 channels * 250 samples * 2 bytes
    expected_size = header["header_bytes"] + 2 * n_channels * 250 * 2
    assert filepath.stat().st_size == expected_size


def test_header_bytes_calculation(tmp_path: Path) -> None:
    """Verify header size matches the EDF spec: 256 + n_channels * 256."""
    for n_ch in [1, 4, 8]:
        data = np.random.randn(n_ch, 250)
        filepath = tmp_path / f"header_{n_ch}ch.edf"
        write_edf(filepath, data, sample_rate=250)
        header = read_edf_header(filepath)
        assert header["header_bytes"] == 256 + n_ch * 256


def test_edf_config_defaults() -> None:
    """Verify EDFConfig has correct defaults."""
    config = EDFConfig()
    assert config.patient_id == "X"
    assert config.recording_id == "X"
    assert config.start_time is None
    assert config.physical_min == -3200.0
    assert config.physical_max == 3200.0
    assert config.digital_min == -32768
    assert config.digital_max == 32767
    assert config.transducer_type == "AgAgCl electrode"
    assert config.physical_dimension == "uV"
