"""Tests for EEG signal processing utilities."""

import numpy as np
import pytest
from lucid.processing import bandpass_filter, compute_psd, notch_filter


@pytest.fixture
def sample_rate() -> float:
    return 250.0


@pytest.fixture
def duration_seconds() -> float:
    return 4.0


@pytest.fixture
def time_axis(sample_rate: float, duration_seconds: float) -> np.ndarray:
    return np.arange(0, duration_seconds, 1.0 / sample_rate)


# --- bandpass_filter ---


class TestBandpassFilter:
    def test_passes_signal_in_band(self, time_axis: np.ndarray, sample_rate: float) -> None:
        """A 10 Hz sine should survive a 1-50 Hz bandpass."""
        signal = np.sin(2 * np.pi * 10 * time_axis)
        filtered = bandpass_filter(signal, 1.0, 50.0, sample_rate)
        # After transient settles, amplitude should be close to 1
        steady = filtered[len(filtered) // 2 :]
        assert np.max(np.abs(steady)) > 0.8

    def test_rejects_signal_outside_band(self, time_axis: np.ndarray, sample_rate: float) -> None:
        """A 100 Hz sine should be strongly attenuated by a 1-30 Hz bandpass."""
        signal = np.sin(2 * np.pi * 100 * time_axis)
        filtered = bandpass_filter(signal, 1.0, 30.0, sample_rate)
        steady = filtered[len(filtered) // 2 :]
        assert np.max(np.abs(steady)) < 0.05

    def test_preserves_shape_1d(self, time_axis: np.ndarray, sample_rate: float) -> None:
        signal = np.sin(2 * np.pi * 10 * time_axis)
        filtered = bandpass_filter(signal, 1.0, 50.0, sample_rate)
        assert filtered.shape == signal.shape

    def test_preserves_shape_2d(self, time_axis: np.ndarray, sample_rate: float) -> None:
        """Multi-channel filtering preserves (channels, samples) shape."""
        n_channels = 4
        signal = np.tile(np.sin(2 * np.pi * 10 * time_axis), (n_channels, 1))
        filtered = bandpass_filter(signal, 1.0, 50.0, sample_rate)
        assert filtered.shape == (n_channels, len(time_axis))

    def test_dc_removal(self, time_axis: np.ndarray, sample_rate: float) -> None:
        """DC offset (0 Hz) should be removed by bandpass."""
        signal = np.ones_like(time_axis) * 5.0
        filtered = bandpass_filter(signal, 1.0, 50.0, sample_rate)
        steady = filtered[len(filtered) // 2 :]
        assert np.abs(np.mean(steady)) < 0.01

    def test_custom_order(self, time_axis: np.ndarray, sample_rate: float) -> None:
        signal = np.sin(2 * np.pi * 10 * time_axis)
        filtered = bandpass_filter(signal, 1.0, 50.0, sample_rate, order=2)
        steady = filtered[len(filtered) // 2 :]
        assert np.max(np.abs(steady)) > 0.7


# --- notch_filter ---


class TestNotchFilter:
    """Notch filter tests use 500 Hz sample rate for adequate headroom above 60 Hz."""

    NOTCH_FS = 500.0

    def _make_time(self, duration: float = 4.0) -> np.ndarray:
        return np.arange(0, duration, 1.0 / self.NOTCH_FS)

    def test_removes_60hz(self) -> None:
        """60 Hz mains interference should be strongly attenuated in steady state."""
        t = self._make_time()
        signal = np.sin(2 * np.pi * 60 * t)
        filtered = notch_filter(signal, 60.0, self.NOTCH_FS)
        # Check steady-state region (middle 50%) to avoid edge transients
        n = len(filtered)
        steady = filtered[n // 4 : 3 * n // 4]
        assert np.max(np.abs(steady)) < 0.05

    def test_removes_50hz(self) -> None:
        """50 Hz mains interference should be strongly attenuated in steady state."""
        t = self._make_time()
        signal = np.sin(2 * np.pi * 50 * t)
        filtered = notch_filter(signal, 50.0, self.NOTCH_FS)
        n = len(filtered)
        steady = filtered[n // 4 : 3 * n // 4]
        assert np.max(np.abs(steady)) < 0.05

    def test_preserves_nearby_frequencies(self) -> None:
        """A 45 Hz signal should survive a 60 Hz notch filter."""
        t = self._make_time()
        signal = np.sin(2 * np.pi * 45 * t)
        filtered = notch_filter(signal, 60.0, self.NOTCH_FS)
        steady = filtered[len(filtered) // 4 : -len(filtered) // 4]
        assert np.max(np.abs(steady)) > 0.8

    def test_preserves_shape_1d(self) -> None:
        t = self._make_time()
        signal = np.sin(2 * np.pi * 60 * t)
        filtered = notch_filter(signal, 60.0, self.NOTCH_FS)
        assert filtered.shape == signal.shape

    def test_preserves_shape_2d(self) -> None:
        t = self._make_time()
        n_channels = 3
        signal = np.tile(np.sin(2 * np.pi * 60 * t), (n_channels, 1))
        filtered = notch_filter(signal, 60.0, self.NOTCH_FS)
        assert filtered.shape == (n_channels, len(t))

    def test_custom_q_factor(self) -> None:
        """Lower Q = wider notch, should still remove target frequency."""
        t = self._make_time()
        signal = np.sin(2 * np.pi * 60 * t)
        filtered = notch_filter(signal, 60.0, self.NOTCH_FS, q=10.0)
        n = len(filtered)
        steady = filtered[n // 4 : 3 * n // 4]
        assert np.max(np.abs(steady)) < 0.05

    def test_mixed_signal_keeps_non_notch(self) -> None:
        """Mixed 10 Hz + 60 Hz: 10 Hz survives, 60 Hz removed."""
        t = self._make_time()
        clean = np.sin(2 * np.pi * 10 * t)
        noise = np.sin(2 * np.pi * 60 * t)
        filtered = notch_filter(clean + noise, 60.0, self.NOTCH_FS)
        # Correlation with original 10 Hz should be high
        mid = len(t) // 4
        corr = np.corrcoef(filtered[mid:-mid], clean[mid:-mid])[0, 1]
        assert corr > 0.95


# --- compute_psd ---


class TestComputePsd:
    def test_peak_at_signal_frequency(self, sample_rate: float) -> None:
        """PSD of a pure 10 Hz sine should peak near 10 Hz."""
        t = np.arange(0, 4.0, 1.0 / sample_rate)
        signal = np.sin(2 * np.pi * 10 * t)
        psd, freqs = compute_psd(signal, sample_rate)
        peak_freq = freqs[np.argmax(psd)]
        assert abs(peak_freq - 10.0) < 2.0

    def test_returns_tuple(self, sample_rate: float) -> None:
        t = np.arange(0, 2.0, 1.0 / sample_rate)
        signal = np.random.randn(len(t))
        result = compute_psd(signal, sample_rate)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_psd_non_negative(self, sample_rate: float) -> None:
        t = np.arange(0, 2.0, 1.0 / sample_rate)
        signal = np.random.randn(len(t))
        psd, _ = compute_psd(signal, sample_rate)
        assert np.all(psd >= 0)

    def test_frequency_range(self, sample_rate: float) -> None:
        """Frequencies should range from 0 to Nyquist."""
        t = np.arange(0, 2.0, 1.0 / sample_rate)
        signal = np.random.randn(len(t))
        _, freqs = compute_psd(signal, sample_rate)
        assert freqs[0] == 0.0
        assert freqs[-1] == sample_rate / 2.0

    def test_multichannel(self, sample_rate: float) -> None:
        """2D input (channels x samples) should produce 2D PSD."""
        t = np.arange(0, 2.0, 1.0 / sample_rate)
        signal = np.random.randn(4, len(t))
        psd, freqs = compute_psd(signal, sample_rate)
        assert psd.ndim == 2
        assert psd.shape[0] == 4
        assert psd.shape[1] == len(freqs)

    def test_custom_window_seconds(self, sample_rate: float) -> None:
        t = np.arange(0, 4.0, 1.0 / sample_rate)
        signal = np.sin(2 * np.pi * 10 * t)
        _psd_short, freqs_short = compute_psd(signal, sample_rate, window_seconds=0.5)
        _psd_long, freqs_long = compute_psd(signal, sample_rate, window_seconds=2.0)
        # Longer window gives finer frequency resolution (more bins)
        assert len(freqs_long) > len(freqs_short)

    def test_white_noise_flat_psd(self, sample_rate: float) -> None:
        """White noise should have roughly flat PSD."""
        rng = np.random.default_rng(42)
        signal = rng.standard_normal(10000)
        psd, _freqs = compute_psd(signal, sample_rate, window_seconds=0.5)
        # Exclude DC, check that max/min ratio isn't extreme
        psd_no_dc = psd[1:]
        ratio = np.max(psd_no_dc) / np.min(psd_no_dc)
        assert ratio < 20.0
