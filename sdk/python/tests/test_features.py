"""Tests for EEG feature extraction."""

import numpy as np
import pytest
from lucid.features import (
    BANDS,
    all_band_powers,
    alpha_peak_frequency,
    band_power,
    relative_band_power,
)


@pytest.fixture
def simple_psd_and_freqs() -> tuple[np.ndarray, np.ndarray]:
    """Create a simple PSD with a known peak at 10 Hz."""
    freqs = np.arange(0, 126, 1.0)  # 0 to 125 Hz, 1 Hz resolution
    psd = np.zeros_like(freqs)
    # Put power in alpha band (8-13 Hz) peaking at 10 Hz
    for f in range(8, 14):
        psd[f] = 5.0 if f == 10 else 2.0
    # Some power in other bands
    psd[2] = 1.0  # delta
    psd[6] = 1.5  # theta
    psd[20] = 1.0  # beta
    psd[40] = 0.5  # gamma
    return psd, freqs


@pytest.fixture
def multichannel_psd_and_freqs() -> tuple[np.ndarray, np.ndarray]:
    """Create a 2D PSD (4 channels)."""
    freqs = np.arange(0, 126, 1.0)
    psd = np.zeros((4, len(freqs)))
    # Each channel has slightly different power
    for ch in range(4):
        psd[ch, 10] = 5.0 + ch  # alpha peak varies by channel
        psd[ch, 20] = 2.0
    return psd, freqs


# --- band_power ---


class TestBandPower:
    def test_alpha_power_1d(self, simple_psd_and_freqs: tuple[np.ndarray, np.ndarray]) -> None:
        psd, freqs = simple_psd_and_freqs
        power = band_power(psd, freqs, 8.0, 13.0)
        assert isinstance(power, float)
        # 8,9,10,11,12,13 Hz bins: 2+2+5+2+2+2 = 15
        assert power == pytest.approx(15.0)

    def test_delta_power_1d(self, simple_psd_and_freqs: tuple[np.ndarray, np.ndarray]) -> None:
        psd, freqs = simple_psd_and_freqs
        power = band_power(psd, freqs, 0.5, 4.0)
        assert isinstance(power, float)
        # Only bin at 2 Hz has power = 1.0; bins 1, 3, 4 have 0
        assert power == pytest.approx(1.0)

    def test_empty_band(self, simple_psd_and_freqs: tuple[np.ndarray, np.ndarray]) -> None:
        psd, freqs = simple_psd_and_freqs
        # No power between 70-80 Hz
        power = band_power(psd, freqs, 70.0, 80.0)
        assert power == pytest.approx(0.0)

    def test_multichannel(self, multichannel_psd_and_freqs: tuple[np.ndarray, np.ndarray]) -> None:
        psd, freqs = multichannel_psd_and_freqs
        power = band_power(psd, freqs, 8.0, 13.0)
        assert isinstance(power, np.ndarray)
        assert power.shape == (4,)
        # Channel 0 has 5.0 at 10 Hz, channel 3 has 8.0
        assert power[0] == pytest.approx(5.0)
        assert power[3] == pytest.approx(8.0)

    def test_single_bin_band(self, simple_psd_and_freqs: tuple[np.ndarray, np.ndarray]) -> None:
        psd, freqs = simple_psd_and_freqs
        power = band_power(psd, freqs, 10.0, 10.0)
        assert power == pytest.approx(5.0)

    def test_full_spectrum(self, simple_psd_and_freqs: tuple[np.ndarray, np.ndarray]) -> None:
        psd, freqs = simple_psd_and_freqs
        total = band_power(psd, freqs, freqs[0], freqs[-1])
        assert total == pytest.approx(np.sum(psd))


# --- all_band_powers ---


class TestAllBandPowers:
    def test_returns_all_bands(self, simple_psd_and_freqs: tuple[np.ndarray, np.ndarray]) -> None:
        psd, freqs = simple_psd_and_freqs
        powers = all_band_powers(psd, freqs)
        assert set(powers.keys()) == set(BANDS.keys())

    def test_alpha_highest(self, simple_psd_and_freqs: tuple[np.ndarray, np.ndarray]) -> None:
        """Alpha should be the dominant band in our test signal."""
        psd, freqs = simple_psd_and_freqs
        powers = all_band_powers(psd, freqs)
        alpha = powers["alpha"]
        for name, power in powers.items():
            if name != "alpha":
                assert alpha > power

    def test_multichannel(self, multichannel_psd_and_freqs: tuple[np.ndarray, np.ndarray]) -> None:
        psd, freqs = multichannel_psd_and_freqs
        powers = all_band_powers(psd, freqs)
        for power in powers.values():
            if isinstance(power, np.ndarray):
                assert power.shape == (4,)


# --- relative_band_power ---


class TestRelativeBandPower:
    def test_sums_to_one(self, simple_psd_and_freqs: tuple[np.ndarray, np.ndarray]) -> None:
        """Relative powers across all frequencies should sum to ~1."""
        psd, freqs = simple_psd_and_freqs
        total_relative = relative_band_power(psd, freqs, freqs[0], freqs[-1])
        assert total_relative == pytest.approx(1.0)

    def test_between_zero_and_one(
        self, simple_psd_and_freqs: tuple[np.ndarray, np.ndarray]
    ) -> None:
        psd, freqs = simple_psd_and_freqs
        rel = relative_band_power(psd, freqs, 8.0, 13.0)
        assert 0.0 < rel < 1.0

    def test_zero_power_band(self, simple_psd_and_freqs: tuple[np.ndarray, np.ndarray]) -> None:
        psd, freqs = simple_psd_and_freqs
        rel = relative_band_power(psd, freqs, 70.0, 80.0)
        assert rel == pytest.approx(0.0)

    def test_all_zero_psd(self) -> None:
        freqs = np.arange(0, 126, 1.0)
        psd = np.zeros_like(freqs)
        rel = relative_band_power(psd, freqs, 8.0, 13.0)
        assert rel == pytest.approx(0.0)

    def test_multichannel(self, multichannel_psd_and_freqs: tuple[np.ndarray, np.ndarray]) -> None:
        psd, freqs = multichannel_psd_and_freqs
        rel = relative_band_power(psd, freqs, 8.0, 13.0)
        assert isinstance(rel, np.ndarray)
        assert rel.shape == (4,)
        assert np.all(rel >= 0.0)
        assert np.all(rel <= 1.0)

    def test_multichannel_zero_total(self) -> None:
        """Channels with zero total power should return 0 relative power."""
        freqs = np.arange(0, 126, 1.0)
        psd = np.zeros((3, len(freqs)))
        psd[0, 10] = 5.0  # Only channel 0 has power
        rel = relative_band_power(psd, freqs, 8.0, 13.0)
        assert rel[0] > 0.0
        assert rel[1] == pytest.approx(0.0)
        assert rel[2] == pytest.approx(0.0)


# --- alpha_peak_frequency ---


class TestAlphaPeakFrequency:
    def test_finds_peak(self, simple_psd_and_freqs: tuple[np.ndarray, np.ndarray]) -> None:
        psd, freqs = simple_psd_and_freqs
        iaf = alpha_peak_frequency(psd, freqs)
        assert iaf == pytest.approx(10.0)

    def test_no_alpha_power(self) -> None:
        freqs = np.arange(0, 126, 1.0)
        psd = np.zeros_like(freqs)
        iaf = alpha_peak_frequency(psd, freqs)
        assert iaf == pytest.approx(0.0)

    def test_peak_at_band_edge(self) -> None:
        freqs = np.arange(0, 126, 1.0)
        psd = np.zeros_like(freqs)
        psd[8] = 10.0  # Peak right at 8 Hz lower edge
        iaf = alpha_peak_frequency(psd, freqs)
        assert iaf == pytest.approx(8.0)

    def test_peak_at_upper_edge(self) -> None:
        freqs = np.arange(0, 126, 1.0)
        psd = np.zeros_like(freqs)
        psd[13] = 10.0  # Peak at 13 Hz upper edge
        iaf = alpha_peak_frequency(psd, freqs)
        assert iaf == pytest.approx(13.0)

    def test_multichannel_averages(self) -> None:
        """With 2D PSD, should average across channels."""
        freqs = np.arange(0, 126, 1.0)
        psd = np.zeros((4, len(freqs)))
        # All channels peak at 10 Hz
        for ch in range(4):
            psd[ch, 10] = 5.0
        iaf = alpha_peak_frequency(psd, freqs)
        assert iaf == pytest.approx(10.0)

    def test_fine_frequency_resolution(self) -> None:
        """Test with finer frequency resolution."""
        freqs = np.arange(0, 50, 0.25)
        psd = np.zeros_like(freqs)
        # Peak at 10.5 Hz
        idx = np.argmin(np.abs(freqs - 10.5))
        psd[idx] = 10.0
        iaf = alpha_peak_frequency(psd, freqs)
        assert abs(iaf - 10.5) < 0.5
