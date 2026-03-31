"""Tests for EEG artifact detection and rejection."""

import numpy as np
import pytest
from lucid.artifacts import detect_blinks, detect_motion, reject_epochs

# --- detect_blinks ---


class TestDetectBlinks:
    def test_detects_large_amplitude(self) -> None:
        signal = np.zeros(1000)
        # Simulate blink at samples 200-220
        signal[200:220] = 150.0
        mask = detect_blinks(signal, threshold_uv=100.0)
        assert mask.dtype == np.bool_
        assert np.all(mask[200:220])
        assert not np.any(mask[:200])
        assert not np.any(mask[220:])

    def test_detects_negative_deflection(self) -> None:
        signal = np.zeros(500)
        signal[100:110] = -120.0
        mask = detect_blinks(signal, threshold_uv=100.0)
        assert np.all(mask[100:110])

    def test_no_blinks_clean_signal(self) -> None:
        signal = np.random.randn(1000) * 10  # Small amplitude noise
        mask = detect_blinks(signal, threshold_uv=100.0)
        assert not np.any(mask)

    def test_custom_threshold(self) -> None:
        signal = np.array([0, 50, 80, 120, 200, 30])
        mask = detect_blinks(signal, threshold_uv=75.0)
        expected = np.array([False, False, True, True, True, False])
        np.testing.assert_array_equal(mask, expected)

    def test_output_shape(self) -> None:
        signal = np.zeros(500)
        mask = detect_blinks(signal)
        assert mask.shape == signal.shape

    def test_all_blinks(self) -> None:
        """Entire signal above threshold."""
        signal = np.ones(100) * 200
        mask = detect_blinks(signal, threshold_uv=100.0)
        assert np.all(mask)

    def test_exactly_at_threshold(self) -> None:
        """Values exactly at threshold should NOT be detected (strictly greater)."""
        signal = np.array([100.0, -100.0, 100.1, -100.1])
        mask = detect_blinks(signal, threshold_uv=100.0)
        expected = np.array([False, False, True, True])
        np.testing.assert_array_equal(mask, expected)


# --- detect_motion ---


class TestDetectMotion:
    def test_stationary(self) -> None:
        """Stationary IMU reads ~(0, 0, 1)g, should not trigger."""
        imu = np.zeros((3, 500))
        imu[2, :] = 1.0  # Gravity on z-axis
        mask = detect_motion(imu, threshold_g=0.5)
        assert not np.any(mask)

    def test_detects_shake(self) -> None:
        """Large acceleration should trigger motion detection."""
        imu = np.zeros((3, 500))
        imu[2, :] = 1.0  # Gravity
        # Shake at samples 100-120
        imu[0, 100:120] = 2.0  # Large x acceleration
        mask = detect_motion(imu, threshold_g=0.5)
        assert np.all(mask[100:120])

    def test_output_shape(self) -> None:
        imu = np.zeros((3, 300))
        imu[2, :] = 1.0
        mask = detect_motion(imu, threshold_g=0.5)
        assert mask.shape == (300,)

    def test_custom_threshold(self) -> None:
        imu = np.zeros((3, 100))
        imu[2, :] = 1.0
        # Moderate motion: x=1.0 with z=1.0 gives magnitude sqrt(2)~1.41, deviation~0.41
        imu[0, 50:60] = 1.0
        # With high threshold (0.5), not detected since deviation ~0.41
        mask_high = detect_motion(imu, threshold_g=0.5)
        assert not np.any(mask_high[50:60])
        # With low threshold (0.3), detected
        mask_low = detect_motion(imu, threshold_g=0.3)
        assert np.all(mask_low[50:60])

    def test_gravity_subtracted(self) -> None:
        """Pure gravity (1g magnitude) should result in 0 deviation."""
        # Gravity along different axes
        imu_z = np.zeros((3, 100))
        imu_z[2, :] = 1.0
        imu_x = np.zeros((3, 100))
        imu_x[0, :] = 1.0
        assert not np.any(detect_motion(imu_z, threshold_g=0.1))
        assert not np.any(detect_motion(imu_x, threshold_g=0.1))

    def test_all_axes_contribute(self) -> None:
        """Motion spread across axes should combine via magnitude."""
        imu = np.zeros((3, 100))
        # Small motion on each axis that sums to large magnitude
        imu[0, 50] = 1.0
        imu[1, 50] = 1.0
        imu[2, 50] = 1.0
        # magnitude = sqrt(3) ~ 1.73, deviation ~ 0.73
        mask = detect_motion(imu, threshold_g=0.5)
        assert mask[50]


# --- reject_epochs ---


class TestRejectEpochs:
    def test_clean_2d_epoch(self) -> None:
        """Small-amplitude 2D data should be marked clean."""
        data = np.random.randn(8, 250) * 10  # Small amplitude
        result = reject_epochs(data, threshold_uv=150.0)
        # Returns a scalar boolean for 2D
        assert isinstance(result, bool | np.bool_)
        assert result

    def test_dirty_2d_epoch(self) -> None:
        """One channel with large ptp should mark epoch as dirty."""
        data = np.random.randn(8, 250) * 10
        data[3, 100] = 200.0  # Spike on channel 3
        data[3, 101] = -200.0
        result = reject_epochs(data, threshold_uv=150.0)
        assert not result

    def test_clean_3d_epochs(self) -> None:
        """All clean epochs."""
        data = np.random.randn(10, 8, 250) * 10
        result = reject_epochs(data, threshold_uv=150.0)
        assert result.shape == (10,)
        assert np.all(result)

    def test_mixed_3d_epochs(self) -> None:
        """Some clean, some dirty epochs."""
        data = np.random.randn(5, 4, 250) * 10
        # Make epoch 1 and 3 dirty
        data[1, 0, 50] = 200.0
        data[1, 0, 51] = -200.0
        data[3, 2, 100] = 300.0
        result = reject_epochs(data, threshold_uv=150.0)
        assert result.shape == (5,)
        assert result[0]  # Clean
        assert not result[1]  # Dirty
        assert result[2]  # Clean
        assert not result[3]  # Dirty
        assert result[4]  # Clean

    def test_custom_threshold(self) -> None:
        data = np.zeros((4, 250))
        data[0, :] = np.linspace(-50, 50, 250)  # ptp = 100
        assert reject_epochs(data, threshold_uv=150.0)
        assert not reject_epochs(data, threshold_uv=80.0)

    def test_invalid_dimensions(self) -> None:
        with pytest.raises(ValueError, match="Expected 2D or 3D"):
            reject_epochs(np.zeros(100))

    def test_4d_raises(self) -> None:
        with pytest.raises(ValueError, match="Expected 2D or 3D"):
            reject_epochs(np.zeros((2, 4, 8, 250)))

    def test_all_dirty_3d(self) -> None:
        """All epochs are artifacts."""
        data = np.zeros((3, 2, 100))
        for i in range(3):
            data[i, 0, 0] = 200.0
            data[i, 0, 1] = -200.0
        result = reject_epochs(data, threshold_uv=150.0)
        assert not np.any(result)

    def test_boundary_ptp(self) -> None:
        """PTP exactly at threshold should pass (strict less-than)."""
        data = np.zeros((2, 100))
        data[0, 0] = 75.0
        data[0, 1] = -75.0  # ptp = 150.0 exactly
        # ptp < threshold, so 150.0 < 150.0 is False => dirty
        assert not reject_epochs(data, threshold_uv=150.0)
        # ptp < 150.1 => True => clean
        assert reject_epochs(data, threshold_uv=150.1)
