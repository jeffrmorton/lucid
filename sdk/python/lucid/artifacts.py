"""EEG artifact detection and rejection."""

import numpy as np
from numpy.typing import NDArray


def detect_blinks(
    eog_channel: NDArray[np.float64],
    threshold_uv: float = 100.0,
) -> NDArray[np.bool_]:
    """Detect eye blinks from EOG channel.

    Args:
        eog_channel: 1D EOG signal.
        threshold_uv: Amplitude threshold for blink detection.

    Returns:
        Boolean mask where True indicates blink artifact.
    """
    return np.abs(eog_channel) > threshold_uv


def detect_motion(
    imu_data: NDArray[np.float64],
    threshold_g: float = 0.5,
) -> NDArray[np.bool_]:
    """Detect head motion from IMU accelerometer data.

    Args:
        imu_data: Shape (3, n_samples) for x, y, z accelerometer.
        threshold_g: Acceleration threshold in g.

    Returns:
        Boolean mask where True indicates motion artifact.
    """
    magnitude = np.sqrt(np.sum(imu_data**2, axis=0))
    # Subtract gravity (1g when stationary)
    deviation = np.abs(magnitude - 1.0)
    return deviation > threshold_g


def reject_epochs(
    data: NDArray[np.float64],
    threshold_uv: float = 150.0,
) -> NDArray[np.bool_] | np.bool_:
    """Mark epochs containing artifacts (peak-to-peak > threshold).

    Args:
        data: Shape (n_channels, n_samples) or (n_epochs, n_channels, n_samples).
        threshold_uv: Peak-to-peak amplitude threshold.

    Returns:
        For 2D input, a single bool (True = clean). For 3D input, a boolean
        mask per epoch (True = clean epoch).
    """
    if data.ndim == 2:
        ptp = np.ptp(data, axis=-1)
        return np.all(ptp < threshold_uv)
    if data.ndim == 3:
        ptp = np.ptp(data, axis=-1)  # (n_epochs, n_channels)
        return np.all(ptp < threshold_uv, axis=1)
    msg = f"Expected 2D or 3D data, got {data.ndim}D"
    raise ValueError(msg)
