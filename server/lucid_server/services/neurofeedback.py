"""Neurofeedback protocol engine.

Loads YAML protocol definitions and evaluates EEG features against
training thresholds to generate feedback signals.
"""

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import yaml


@dataclass
class BandTarget:
    """A frequency band with a training target."""

    name: str
    low_hz: float
    high_hz: float
    target: str  # 'enhance' or 'suppress'
    threshold_percentile: float = 60.0


@dataclass
class NFProtocol:
    """A neurofeedback training protocol."""

    name: str
    description: str
    evidence_level: str
    electrode: str
    reference: str
    bands: list[BandTarget] = field(default_factory=list)
    session_duration_s: int = 1200
    baseline_duration_s: int = 120
    earthsync: dict | None = None  # Optional EarthSync integration config


@dataclass
class FeedbackState:
    """Current neurofeedback feedback state."""

    reward: bool = False
    inhibit: bool = False
    reward_value: float = 0.0
    inhibit_value: float = 0.0


def load_protocol(path: Path) -> NFProtocol:
    """Load a neurofeedback protocol from YAML file.

    Args:
        path: Path to YAML protocol file.

    Returns:
        Parsed NFProtocol.
    """
    with Path.open(path) as f:
        data = yaml.safe_load(f)

    bands = [
        BandTarget(
            name=band_data["name"],
            low_hz=band_data["range"][0],
            high_hz=band_data["range"][1],
            target=band_data["target"],
            threshold_percentile=band_data.get("threshold_percentile", 60.0),
        )
        for band_data in data.get("bands", {}).values()
    ]

    earthsync_config = data.get("earthsync")

    # Support both electrode_montage (SMR-style) and top-level electrode/reference (SR-style)
    electrode = data.get("electrode") or data.get("electrode_montage", {}).get("active", "Cz")
    reference = data.get("reference") or data.get("electrode_montage", {}).get(
        "reference", "linked_mastoids"
    )

    # Support both session section (SMR-style) and top-level durations (SR-style)
    session_duration_s = data.get("session_duration_s") or data.get("session", {}).get(
        "training_duration_s", 1200
    )
    baseline_duration_s = data.get("baseline_duration_s") or data.get("session", {}).get(
        "baseline_duration_s", 120
    )

    return NFProtocol(
        name=data["name"],
        description=data.get("description", ""),
        evidence_level=data.get("evidence_level", "unknown"),
        electrode=electrode,
        reference=reference,
        bands=bands,
        session_duration_s=session_duration_s,
        baseline_duration_s=baseline_duration_s,
        earthsync=earthsync_config,
    )


class NeurofeedbackEngine:
    """Evaluates band powers against protocol thresholds."""

    def __init__(self, protocol: NFProtocol) -> None:
        self.protocol = protocol
        self.baseline_data: list[dict[str, float]] = []
        self.thresholds: dict[str, float] = {}
        self.calibrated = False
        self._ema_alpha: float = 0.3  # Smoothing factor (0.1=slow, 0.5=fast)
        self._ema_values: dict[str, float] = {}  # band_name -> smoothed value
        self._reward_streak: int = 0  # Consecutive reward epochs
        self._min_reward_streak: int = 3  # Require N consecutive epochs for reward

    def add_baseline_sample(self, band_powers: dict[str, float]) -> None:
        """Record a baseline band power sample.

        Args:
            band_powers: Dict mapping band name to power value.
        """
        self.baseline_data.append(band_powers)

    def calibrate(self) -> None:
        """Compute thresholds from accumulated baseline data."""
        if not self.baseline_data:
            return

        for band_target in self.protocol.bands:
            name = band_target.name.lower()
            values = [s.get(name, 0.0) for s in self.baseline_data]
            if values:
                percentile = band_target.threshold_percentile
                self.thresholds[name] = float(np.percentile(values, percentile))

        self.calibrated = True

    def update_band_range(self, band_name: str, low_hz: float, high_hz: float) -> bool:
        """Update the frequency range of a named band target.

        Used for dynamic SR entrainment where the target frequency
        drifts with the live Schumann Resonance fundamental.

        Args:
            band_name: Name of the band to update (case-insensitive).
            low_hz: New lower frequency bound.
            high_hz: New upper frequency bound.

        Returns:
            True if the band was found and updated, False otherwise.
        """
        for band in self.protocol.bands:
            if band.name.lower() == band_name.lower():
                band.low_hz = low_hz
                band.high_hz = high_hz
                return True
        return False

    def set_smoothing(self, alpha: float = 0.3, min_streak: int = 3) -> None:
        """Configure temporal smoothing parameters.

        Args:
            alpha: EMA smoothing factor (0.0-1.0). Lower = smoother.
            min_streak: Minimum consecutive reward epochs before reporting reward.
        """
        self._ema_alpha = max(0.01, min(1.0, alpha))
        self._min_reward_streak = max(1, min_streak)

    def reset_smoothing(self) -> None:
        """Reset EMA state and streak counter."""
        self._ema_values.clear()
        self._reward_streak = 0

    def evaluate(self, band_powers: dict[str, float]) -> FeedbackState:
        """Evaluate current band powers against protocol thresholds.

        Uses EMA smoothing to reduce jitter and streak tracking to require
        sustained performance before reporting reward.

        Args:
            band_powers: Current band power values.

        Returns:
            FeedbackState indicating reward/inhibit status.
        """
        if not self.calibrated:
            return FeedbackState()

        reward = True
        inhibit = False
        reward_value = 0.0
        inhibit_value = 0.0

        for band_target in self.protocol.bands:
            name = band_target.name.lower()
            raw_value = band_powers.get(name, 0.0)

            # Apply EMA smoothing
            if name in self._ema_values:
                smoothed = (
                    self._ema_alpha * raw_value + (1 - self._ema_alpha) * self._ema_values[name]
                )
            else:
                smoothed = raw_value
            self._ema_values[name] = smoothed

            threshold = self.thresholds.get(name, 0.0)

            if band_target.target == "enhance":
                if threshold > 0 and smoothed >= threshold:
                    reward_value = max(reward_value, smoothed / threshold)
                else:
                    reward = False
            elif band_target.target == "suppress" and threshold > 0 and smoothed >= threshold:
                inhibit = True
                inhibit_value = max(inhibit_value, smoothed / threshold)

        # Streak tracking
        if reward:
            self._reward_streak += 1
        else:
            self._reward_streak = 0

        # Only report reward after sustained performance
        sustained_reward = reward and self._reward_streak >= self._min_reward_streak

        return FeedbackState(
            reward=sustained_reward,
            inhibit=inhibit,
            reward_value=reward_value if sustained_reward else 0.0,
            inhibit_value=inhibit_value,
        )
