"""Tests for EEG classifier."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
from lucid_server.services.classifier import EEGClassifier


def test_classifier_creation() -> None:
    c = EEGClassifier()
    assert not c.loaded


def test_load_no_model() -> None:
    c = EEGClassifier(model_path=Path("/nonexistent/model.onnx"))
    assert not c.load()


def test_load_none_path() -> None:
    c = EEGClassifier()
    assert not c.load()


def test_predict_not_loaded() -> None:
    c = EEGClassifier()
    result = c.predict(np.zeros(10))
    assert result["class"] == "unknown"
    assert "error" in result


def test_classes_defined() -> None:
    c = EEGClassifier()
    assert len(c.classes) == 5
    assert "rest" in c.classes


def test_load_ort_not_available() -> None:
    """When ORT is not available, load returns False."""
    with tempfile.NamedTemporaryFile(suffix=".onnx") as f:
        c = EEGClassifier(model_path=Path(f.name))
        with patch("lucid_server.services.classifier._ORT_AVAILABLE", False):
            assert not c.load()


def test_load_ort_exception() -> None:
    """When ORT throws an exception during loading, returns False."""
    with tempfile.NamedTemporaryFile(suffix=".onnx") as f:
        c = EEGClassifier(model_path=Path(f.name))
        with (
            patch("lucid_server.services.classifier._ORT_AVAILABLE", True),
            patch("lucid_server.services.classifier.ort") as mock_ort,
        ):
            mock_ort.InferenceSession.side_effect = RuntimeError("bad model")
            assert not c.load()


def test_load_success_and_predict() -> None:
    """Test successful load and predict with mocked ORT."""
    mock_session = MagicMock()
    mock_input = MagicMock()
    mock_input.name = "input"
    mock_session.get_inputs.return_value = [mock_input]
    # Return probabilities for 5 classes
    mock_session.run.return_value = [np.array([[0.1, 0.5, 0.2, 0.1, 0.1]])]

    with tempfile.NamedTemporaryFile(suffix=".onnx") as f:
        c = EEGClassifier(model_path=Path(f.name))
        with (
            patch("lucid_server.services.classifier._ORT_AVAILABLE", True),
            patch("lucid_server.services.classifier.ort") as mock_ort,
        ):
            mock_ort.InferenceSession.return_value = mock_session
            assert c.load()
            assert c.loaded

    # Predict with 1D features
    result = c.predict(np.zeros(10))
    assert result["class"] == "left_hand"  # index 1 has highest prob
    assert "probabilities" in result
    assert len(result["probabilities"]) == 5

    # Predict with 2D features
    result2d = c.predict(np.zeros((1, 10)))
    assert result2d["class"] == "left_hand"


def test_predict_empty_result() -> None:
    """Test predict when session returns empty result."""
    mock_session = MagicMock()
    mock_input = MagicMock()
    mock_input.name = "input"
    mock_session.get_inputs.return_value = [mock_input]
    mock_session.run.return_value = []

    with tempfile.NamedTemporaryFile(suffix=".onnx") as f:
        c = EEGClassifier(model_path=Path(f.name))
        with (
            patch("lucid_server.services.classifier._ORT_AVAILABLE", True),
            patch("lucid_server.services.classifier.ort") as mock_ort,
        ):
            mock_ort.InferenceSession.return_value = mock_session
            c.load()

    result = c.predict(np.zeros(10))
    assert result["class"] == "rest"  # class_idx=0 from empty probs
