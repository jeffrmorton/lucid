"""Tests for EEG processor."""

import numpy as np
import pytest
from lucid_server.services.eeg_processor import EEGProcessor


@pytest.fixture
def processor():
    return EEGProcessor(sample_rate=250, n_channels=8)


def test_processor_creation(processor: EEGProcessor) -> None:
    assert processor.sample_rate == 250
    assert processor.n_channels == 8


def test_process_shape(processor: EEGProcessor) -> None:
    data = np.random.randn(8, 250)
    result = processor.process(data)
    assert result.shape == (8, 250)


def test_process_wrong_channels(processor: EEGProcessor) -> None:
    data = np.random.randn(4, 250)
    with pytest.raises(ValueError, match="Expected 8 channels"):
        processor.process(data)


def test_process_removes_dc(processor: EEGProcessor) -> None:
    # DC signal should be rejected by bandpass
    data = np.ones((8, 500))
    result = processor.process(data)
    # After settling, output should be near zero
    assert np.abs(result[:, 400:]).mean() < 0.1


def test_process_passes_10hz(processor: EEGProcessor) -> None:
    # 10 Hz signal should pass through bandpass
    t = np.arange(1000) / 250
    signal = np.sin(2 * np.pi * 10 * t)
    data = np.tile(signal, (8, 1))
    result = processor.process(data)
    # After settling, output should have significant amplitude
    rms = np.sqrt(np.mean(result[:, 500:] ** 2, axis=1))
    assert np.all(rms > 0.1)


def test_compute_psd(processor: EEGProcessor) -> None:
    data = np.random.randn(8, 500)
    psd, freqs = processor.compute_psd(data)
    assert psd.shape[0] == 8
    assert len(freqs) == psd.shape[1]
    assert freqs[0] == 0.0


def test_compute_band_powers(processor: EEGProcessor) -> None:
    data = np.random.randn(8, 500)
    psd, freqs = processor.compute_psd(data)
    bp = processor.compute_band_powers(psd, freqs)
    assert "alpha" in bp
    assert "beta" in bp
    assert bp["alpha"].shape == (8,)
    assert np.all(bp["alpha"] >= 0)


def test_band_powers_sum(processor: EEGProcessor) -> None:
    data = np.random.randn(8, 500)
    psd, freqs = processor.compute_psd(data)
    bp = processor.compute_band_powers(psd, freqs)
    total = sum(bp[b].sum() for b in bp)
    assert total > 0


def test_compute_custom_band_power(processor: EEGProcessor) -> None:
    """Compute power in a custom frequency range (SR band 6.83-8.83 Hz)."""
    data = np.random.randn(8, 500)
    psd, freqs = processor.compute_psd(data)
    sr_power = processor.compute_custom_band_power(psd, freqs, 6.83, 8.83)
    assert sr_power.shape == (8,)
    assert np.all(sr_power >= 0)


def test_compute_custom_band_power_full_range(processor: EEGProcessor) -> None:
    """Custom band covering full range matches total PSD sum."""
    data = np.random.randn(8, 500)
    psd, freqs = processor.compute_psd(data)
    full_power = processor.compute_custom_band_power(psd, freqs, freqs[0], freqs[-1])
    total_psd = np.sum(psd, axis=1)
    np.testing.assert_allclose(full_power, total_psd)


def test_compute_custom_band_power_empty_range(processor: EEGProcessor) -> None:
    """Custom band outside PSD range returns zeros."""
    data = np.random.randn(8, 500)
    psd, freqs = processor.compute_psd(data)
    # Frequency range well above Nyquist
    empty_power = processor.compute_custom_band_power(psd, freqs, 900.0, 1000.0)
    assert np.all(empty_power == 0.0)
