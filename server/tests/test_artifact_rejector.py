"""Tests for ArtifactRejector."""

import numpy as np
import pytest
from lucid_server.services.eeg_processor import ArtifactRejector, EEGProcessor


def test_artifact_rejector_creation() -> None:
    ar = ArtifactRejector(n_channels=8)
    assert not ar.calibrated


def test_calibrate() -> None:
    ar = ArtifactRejector(n_channels=2)
    data = np.random.randn(2, 200) * 0.1
    ar.calibrate(data)
    assert ar.calibrated
    assert ar.ref_rms is not None


def test_calibrate_wrong_channels() -> None:
    ar = ArtifactRejector(n_channels=8)
    data = np.random.randn(4, 200)
    with pytest.raises(ValueError, match="Expected 8"):
        ar.calibrate(data)


def test_process_uncalibrated_passthrough() -> None:
    ar = ArtifactRejector(n_channels=2)
    data = np.random.randn(2, 100)
    result = ar.process(data)
    np.testing.assert_array_equal(result, data)


def test_process_removes_artifact() -> None:
    ar = ArtifactRejector(n_channels=1, threshold=3.0)
    clean = np.random.randn(1, 200) * 0.1
    ar.calibrate(clean)
    # Create data with artifact
    data = np.random.randn(1, 50) * 0.1
    data[0, 25] = 100.0  # Large artifact
    result = ar.process(data)
    assert abs(result[0, 25]) < 50.0  # Should be reduced


def test_reject_artifacts_method() -> None:
    """Test the EEGProcessor.reject_artifacts passthrough."""
    processor = EEGProcessor(sample_rate=250, n_channels=2)
    data = np.random.randn(2, 100)
    # Uncalibrated: should pass through
    result = processor.reject_artifacts(data)
    np.testing.assert_array_equal(result, data)
