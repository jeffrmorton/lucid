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
    """Custom band covering the full open range integrates PSD over frequency.

    Band power is now a true integral of the PSD over frequency: the sum of
    selected bins scaled by the bin width df (freqs[1] - freqs[0]), so the value
    carries the PSD's power units instead of being a bare bin sum.

    The mask is half-open ``[low, high)`` (see ``test_band_mask_is_half_open``),
    so selecting ``[freqs[0], freqs[-1])`` covers every bin EXCEPT the final
    (Nyquist) bin. The expected value is therefore the df-scaled sum over all but
    the last bin.
    """
    data = np.random.randn(8, 500)
    psd, freqs = processor.compute_psd(data)
    df = float(freqs[1] - freqs[0])
    full_power = processor.compute_custom_band_power(psd, freqs, freqs[0], freqs[-1])
    expected = np.sum(psd[:, :-1], axis=1) * df
    np.testing.assert_allclose(full_power, expected)


def test_compute_custom_band_power_inclusive_top_matches_integral(processor: EEGProcessor) -> None:
    """A high bound just above the last bin includes it; value is df-scaled sum."""
    data = np.random.randn(8, 500)
    psd, freqs = processor.compute_psd(data)
    df = float(freqs[1] - freqs[0])
    # Push the upper bound just past the Nyquist bin so the half-open mask keeps it.
    full_power = processor.compute_custom_band_power(psd, freqs, freqs[0], freqs[-1] + df)
    expected = np.sum(psd, axis=1) * df
    np.testing.assert_allclose(full_power, expected)


def test_compute_custom_band_power_df_scaling(processor: EEGProcessor) -> None:
    """Band power scales with the frequency bin width df, not a bare bin count.

    Using a shorter PSD window doubles df (halves nperseg → coarser bins). The
    integrated power must reflect df, so it equals the bin sum times df rather
    than the raw sum.
    """
    rng = np.random.default_rng(0)
    data = rng.standard_normal((8, 500))
    psd, freqs = processor.compute_psd(data, window_seconds=0.5)
    df = float(freqs[1] - freqs[0])
    assert df == pytest.approx(2.0)  # 250 SPS / 125 bins → 2 Hz bins
    band = processor.compute_custom_band_power(psd, freqs, 8.0, 13.0)
    mask = (freqs >= 8.0) & (freqs < 13.0)
    expected = np.sum(psd[:, mask], axis=1) * df
    np.testing.assert_allclose(band, expected)


def test_compute_custom_band_power_empty_range(processor: EEGProcessor) -> None:
    """Custom band outside PSD range returns zeros."""
    data = np.random.randn(8, 500)
    psd, freqs = processor.compute_psd(data)
    # Frequency range well above Nyquist
    empty_power = processor.compute_custom_band_power(psd, freqs, 900.0, 1000.0)
    assert np.all(empty_power == 0.0)


def test_band_mask_is_half_open(processor: EEGProcessor) -> None:
    """A bin on a shared band boundary belongs to exactly one band (no double-count).

    8 Hz is the shared edge between theta (4-8) and alpha (8-13). With a half-open
    ``[low, high)`` mask the 8 Hz bin counts in alpha only, never in both. We build
    a PSD with all power in the 8 Hz bin and assert theta gets none of it while
    alpha gets all of it (df-scaled).
    """
    nperseg = processor.sample_rate  # 1 s window → 1 Hz bins, integer frequencies
    freqs = np.fft.rfftfreq(nperseg, d=1.0 / processor.sample_rate)
    df = float(freqs[1] - freqs[0])
    psd = np.zeros((processor.n_channels, len(freqs)))
    idx_8hz = int(np.argmin(np.abs(freqs - 8.0)))
    assert freqs[idx_8hz] == pytest.approx(8.0)
    psd[:, idx_8hz] = 5.0

    bp = processor.compute_band_powers(psd, freqs)
    # Theta upper edge (8 Hz) is exclusive → no power leaks in.
    np.testing.assert_allclose(bp["theta"], np.zeros(processor.n_channels))
    # Alpha lower edge (8 Hz) is inclusive → all the power, df-scaled.
    np.testing.assert_allclose(bp["alpha"], np.full(processor.n_channels, 5.0 * df))


def test_band_power_single_bin_psd_is_zero(processor: EEGProcessor) -> None:
    """A PSD with fewer than two bins has no bin width, so power integrates to 0.

    With only one frequency point df is undefined; the degenerate result is 0.0
    power across all bands (no spectral resolution to integrate over).
    """
    freqs = np.array([8.0])
    psd = np.full((processor.n_channels, 1), 5.0)
    bp = processor.compute_band_powers(psd, freqs)
    for value in bp.values():
        np.testing.assert_allclose(value, np.zeros(processor.n_channels))
    custom = processor.compute_custom_band_power(psd, freqs, 0.0, 100.0)
    np.testing.assert_allclose(custom, np.zeros(processor.n_channels))


def test_band_powers_are_df_scaled_integral(processor: EEGProcessor) -> None:
    """Each standard band power equals its half-open bin sum times df."""
    rng = np.random.default_rng(1)
    data = rng.standard_normal((8, 500))
    psd, freqs = processor.compute_psd(data, window_seconds=0.5)
    df = float(freqs[1] - freqs[0])
    bands = {
        "delta": (0.5, 4.0),
        "theta": (4.0, 8.0),
        "alpha": (8.0, 13.0),
        "beta": (13.0, 30.0),
        "gamma": (30.0, 100.0),
    }
    bp = processor.compute_band_powers(psd, freqs)
    for name, (low, high) in bands.items():
        mask = (freqs >= low) & (freqs < high)
        expected = np.sum(psd[:, mask], axis=1) * df
        np.testing.assert_allclose(bp[name], expected, err_msg=name)
