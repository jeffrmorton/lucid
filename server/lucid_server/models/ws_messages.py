"""Pydantic models for WebSocket message envelopes.

All outbound WebSocket messages carry a uniform ``type`` discriminator so a
client can dispatch on a single field. The models are additive: they preserve
the historical keys (``status``/``phase``/``error``) alongside ``type`` for
backward compatibility with existing dashboard clients.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class ErrorMessage(BaseModel):
    """An error envelope for a WebSocket client."""

    type: Literal["error"] = "error"
    error: str


class ProcessedMessage(BaseModel):
    """Processed EEG data broadcast to device + viewers."""

    type: Literal["processed"] = "processed"
    status: Literal["processed"] = "processed"
    n_samples: int
    band_powers: dict[str, list[float]]
    psd: list[float]
    freqs: list[float]
    psd_shape: list[int]


class CalibrationMessage(BaseModel):
    """Calibration-phase announcement."""

    type: Literal["phase"] = "phase"
    phase: Literal["calibration"] = "calibration"
    duration_s: float
    earthsync: dict | None = None


class TrainingMessage(BaseModel):
    """Transition to the training phase after calibration."""

    type: Literal["phase"] = "phase"
    phase: Literal["training"] = "training"
    calibrated: bool


class FeedbackMessage(BaseModel):
    """Per-epoch neurofeedback result."""

    type: Literal["feedback"] = "feedback"
    status: Literal["feedback"] = "feedback"
    reward: bool
    inhibit: bool
    reward_value: float
    inhibit_value: float
    band_powers: dict[str, list[float]]
    sr: dict | None = None
