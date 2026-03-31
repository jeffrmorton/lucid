"""EEG signal processing utilities."""

import numpy as np
from numpy.typing import NDArray
from scipy.signal import butter, filtfilt, iirnotch, sosfilt, welch


def bandpass_filter(
    data: NDArray[np.float64],
    low_hz: float,
    high_hz: float,
    sample_rate: float,
    order: int = 4,
) -> NDArray[np.float64]:
    """Apply a Butterworth bandpass filter.

    Args:
        data: 1D or 2D array (channels x samples).
        low_hz: Lower cutoff frequency.
        high_hz: Upper cutoff frequency.
        sample_rate: Sampling rate in Hz.
        order: Filter order.

    Returns:
        Filtered data, same shape as input.
    """
    sos = butter(order, [low_hz, high_hz], btype="band", fs=sample_rate, output="sos")
    return sosfilt(sos, data, axis=-1)


def notch_filter(
    data: NDArray[np.float64],
    freq_hz: float,
    sample_rate: float,
    q: float = 30.0,
) -> NDArray[np.float64]:
    """Apply a notch filter to remove mains frequency.

    Args:
        data: 1D or 2D array.
        freq_hz: Frequency to reject (50 or 60 Hz).
        sample_rate: Sampling rate in Hz.
        q: Quality factor (higher = narrower notch).

    Returns:
        Filtered data.
    """
    b, a = iirnotch(freq_hz, q, fs=sample_rate)
    return filtfilt(b, a, data, axis=-1)


def compute_psd(
    data: NDArray[np.float64],
    sample_rate: float,
    window_seconds: float = 1.0,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Compute power spectral density using Welch's method.

    Args:
        data: 1D or 2D array (channels x samples).
        sample_rate: Sampling rate in Hz.
        window_seconds: FFT window length.

    Returns:
        (psd, frequencies) tuple.
    """
    nperseg = int(sample_rate * window_seconds)
    freqs, psd = welch(data, fs=sample_rate, nperseg=nperseg, axis=-1)
    return psd, freqs
