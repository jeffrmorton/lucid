"""EEG feature extraction."""

import numpy as np
from numpy.typing import NDArray

# Standard EEG band definitions (Hz)
BANDS = {
    "delta": (0.5, 4.0),
    "theta": (4.0, 8.0),
    "alpha": (8.0, 13.0),
    "beta": (13.0, 30.0),
    "gamma": (30.0, 100.0),
}


def band_power(
    psd: NDArray[np.float64],
    freqs: NDArray[np.float64],
    low_hz: float,
    high_hz: float,
) -> NDArray[np.float64] | float:
    """Compute power in a frequency band.

    Args:
        psd: PSD array (1D or 2D with channels on axis 0).
        freqs: Frequency axis.
        low_hz: Lower band edge.
        high_hz: Upper band edge.

    Returns:
        Band power (scalar for 1D, array for 2D).
    """
    mask = (freqs >= low_hz) & (freqs <= high_hz)
    if psd.ndim == 1:
        return float(np.sum(psd[mask]))
    return np.sum(psd[:, mask], axis=1)


def all_band_powers(
    psd: NDArray[np.float64],
    freqs: NDArray[np.float64],
) -> dict[str, NDArray[np.float64] | float]:
    """Compute power for all standard EEG bands.

    Returns:
        Dict mapping band name to power value(s).
    """
    return {name: band_power(psd, freqs, low, high) for name, (low, high) in BANDS.items()}


def relative_band_power(
    psd: NDArray[np.float64],
    freqs: NDArray[np.float64],
    low_hz: float,
    high_hz: float,
) -> NDArray[np.float64] | float:
    """Compute relative band power (fraction of total).

    Returns:
        Value between 0 and 1.
    """
    total = band_power(psd, freqs, freqs[0], freqs[-1])
    bp = band_power(psd, freqs, low_hz, high_hz)
    if isinstance(total, float):
        return bp / total if total > 0 else 0.0
    safe_total = np.where(total > 0, total, 1.0)
    return np.where(total > 0, bp / safe_total, 0.0)


def alpha_peak_frequency(
    psd: NDArray[np.float64],
    freqs: NDArray[np.float64],
) -> float:
    """Find the individual alpha peak frequency (IAF).

    The IAF is the frequency of maximum power in the alpha band (8-13 Hz).
    It varies between individuals (typically 9-11 Hz).

    Returns:
        Peak frequency in Hz, or 0.0 if no clear peak.
    """
    mask = (freqs >= 8.0) & (freqs <= 13.0)
    alpha_psd = psd[mask] if psd.ndim == 1 else np.mean(psd[:, mask], axis=0)
    if len(alpha_psd) == 0 or np.max(alpha_psd) == 0:
        return 0.0
    peak_idx = np.argmax(alpha_psd)
    return float(freqs[mask][peak_idx])
