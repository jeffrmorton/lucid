"""EEG classification service using ONNX Runtime.

Loads a pre-trained model and runs inference on EEG features.
Currently a placeholder -- no pre-trained model is included.
"""

from pathlib import Path

import numpy as np
from numpy.typing import NDArray

try:
    import onnxruntime as ort

    _ORT_AVAILABLE = True
except ImportError:  # pragma: no cover
    ort = None  # type: ignore[assignment]
    _ORT_AVAILABLE = False


class EEGClassifier:
    """ONNX-based EEG classifier."""

    def __init__(self, model_path: Path | None = None) -> None:
        self.model_path = model_path
        self.session = None
        self.loaded = False
        self.classes = ["rest", "left_hand", "right_hand", "feet", "tongue"]

    def load(self) -> bool:
        """Load ONNX model. Returns False if model not found."""
        if self.model_path is None or not self.model_path.exists():
            return False
        if not _ORT_AVAILABLE:
            return False
        try:
            self.session = ort.InferenceSession(str(self.model_path))
            self.loaded = True
        except Exception:
            return False
        else:
            return True

    def predict(self, features: NDArray[np.float64]) -> dict:
        """Run inference on feature vector.

        Args:
            features: Shape (1, n_features) or (n_features,).

        Returns:
            Dict with 'class' and 'probabilities'.
        """
        if not self.loaded or self.session is None:
            return {"class": "unknown", "probabilities": {}, "error": "model not loaded"}

        if features.ndim == 1:
            features = features.reshape(1, -1)

        input_name = self.session.get_inputs()[0].name
        result = self.session.run(None, {input_name: features.astype(np.float32)})

        probs = result[0][0] if len(result) > 0 else []
        class_idx = int(np.argmax(probs)) if len(probs) > 0 else 0
        class_name = self.classes[class_idx] if class_idx < len(self.classes) else "unknown"

        return {
            "class": class_name,
            "probabilities": {
                self.classes[i]: float(p) for i, p in enumerate(probs) if i < len(self.classes)
            },
        }
