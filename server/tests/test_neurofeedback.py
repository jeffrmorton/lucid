"""Tests for neurofeedback engine."""

from pathlib import Path

import numpy as np
import pytest
from lucid_server.services.neurofeedback import (
    BandTarget,
    FeedbackState,
    NeurofeedbackEngine,
    NFProtocol,
    load_protocol,
)


def _make_protocol() -> NFProtocol:
    return NFProtocol(
        name="Test SMR",
        description="Test protocol",
        evidence_level="test",
        electrode="Cz",
        reference="linked_mastoids",
        bands=[
            BandTarget(
                name="SMR", low_hz=12, high_hz=15, target="enhance", threshold_percentile=60
            ),
            BandTarget(
                name="Theta", low_hz=4, high_hz=8, target="suppress", threshold_percentile=80
            ),
        ],
        session_duration_s=300,
        baseline_duration_s=60,
    )


def test_protocol_creation() -> None:
    p = _make_protocol()
    assert p.name == "Test SMR"
    assert len(p.bands) == 2


def test_engine_creation() -> None:
    engine = NeurofeedbackEngine(_make_protocol())
    assert not engine.calibrated


def test_engine_baseline_and_calibrate() -> None:
    engine = NeurofeedbackEngine(_make_protocol())
    for _ in range(10):
        engine.add_baseline_sample(
            {"smr": np.random.uniform(1, 5), "theta": np.random.uniform(0.5, 2)}
        )
    engine.calibrate()
    assert engine.calibrated
    assert "smr" in engine.thresholds
    assert "theta" in engine.thresholds


def test_engine_evaluate_uncalibrated() -> None:
    engine = NeurofeedbackEngine(_make_protocol())
    state = engine.evaluate({"smr": 3.0, "theta": 1.0})
    assert not state.reward
    assert not state.inhibit


def test_engine_evaluate_reward() -> None:
    engine = NeurofeedbackEngine(_make_protocol())
    engine.set_smoothing(min_streak=1)  # Disable streak for legacy behavior
    for _ in range(20):
        engine.add_baseline_sample({"smr": 2.0, "theta": 1.0})
    engine.calibrate()
    # High SMR, low theta = reward
    state = engine.evaluate({"smr": 5.0, "theta": 0.5})
    assert state.reward
    assert not state.inhibit


def test_engine_evaluate_inhibit() -> None:
    engine = NeurofeedbackEngine(_make_protocol())
    engine.set_smoothing(min_streak=1)
    for _ in range(20):
        engine.add_baseline_sample({"smr": 2.0, "theta": 1.0})
    engine.calibrate()
    # High theta = inhibit
    state = engine.evaluate({"smr": 5.0, "theta": 5.0})
    assert state.inhibit


def test_feedback_state_defaults() -> None:
    state = FeedbackState()
    assert not state.reward
    assert not state.inhibit
    assert state.reward_value == 0.0


def test_calibrate_empty_baseline() -> None:
    """Calibrating with no baseline data returns early without setting calibrated."""
    engine = NeurofeedbackEngine(_make_protocol())
    engine.calibrate()
    assert not engine.calibrated
    assert engine.thresholds == {}


def test_evaluate_enhance_below_threshold() -> None:
    """SMR below threshold means reward is False (line 142)."""
    engine = NeurofeedbackEngine(_make_protocol())
    for _ in range(20):
        engine.add_baseline_sample({"smr": 5.0, "theta": 1.0})
    engine.calibrate()
    # SMR well below threshold -> reward = False
    state = engine.evaluate({"smr": 0.1, "theta": 0.1})
    assert not state.reward


def test_load_protocol_from_yaml() -> None:
    proto_path = Path(__file__).parent.parent.parent / "protocols" / "smr_training.yaml"
    if proto_path.exists():
        protocol = load_protocol(proto_path)
        assert protocol.name == "SMR Training"
        assert len(protocol.bands) > 0


def test_update_band_range_success() -> None:
    """Update existing band returns True and changes the range."""
    engine = NeurofeedbackEngine(_make_protocol())
    result = engine.update_band_range("SMR", 10.0, 14.0)
    assert result is True
    smr_band = next(b for b in engine.protocol.bands if b.name == "SMR")
    assert smr_band.low_hz == 10.0
    assert smr_band.high_hz == 14.0


def test_update_band_range_not_found() -> None:
    """Non-existent band returns False."""
    engine = NeurofeedbackEngine(_make_protocol())
    result = engine.update_band_range("Nonexistent", 1.0, 2.0)
    assert result is False


def test_update_band_range_case_insensitive() -> None:
    """Case-insensitive match: 'sr' matches 'SR'."""
    protocol = NFProtocol(
        name="Test SR",
        description="SR test",
        evidence_level="test",
        electrode="Cz",
        reference="A1",
        bands=[
            BandTarget(name="SR", low_hz=6.83, high_hz=8.83, target="enhance"),
        ],
    )
    engine = NeurofeedbackEngine(protocol)
    result = engine.update_band_range("sr", 7.0, 9.0)
    assert result is True
    sr_band = engine.protocol.bands[0]
    assert sr_band.low_hz == 7.0
    assert sr_band.high_hz == 9.0


def test_sr_entrainment_protocol_loads() -> None:
    """Load sr_entrainment.yaml successfully."""
    proto_path = Path(__file__).parent.parent.parent / "protocols" / "sr_entrainment.yaml"
    protocol = load_protocol(proto_path)
    assert protocol.name == "SR Entrainment"
    assert len(protocol.bands) == 2
    assert protocol.electrode == "Cz"
    assert protocol.reference == "A1"
    assert protocol.session_duration_s == 1200
    assert protocol.baseline_duration_s == 120


def test_sr_entrainment_has_earthsync_config() -> None:
    """Protocol earthsync config is populated from YAML."""
    proto_path = Path(__file__).parent.parent.parent / "protocols" / "sr_entrainment.yaml"
    protocol = load_protocol(proto_path)
    assert protocol.earthsync is not None
    assert protocol.earthsync["enabled"] is True
    assert protocol.earthsync["station_id"] == "simulator1"
    assert protocol.earthsync["update_interval_s"] == 10


def test_protocol_earthsync_default_none() -> None:
    """NFProtocol earthsync defaults to None."""
    p = _make_protocol()
    assert p.earthsync is None


def test_smr_protocol_earthsync_none() -> None:
    """SMR protocol has no earthsync config."""
    proto_path = Path(__file__).parent.parent.parent / "protocols" / "smr_training.yaml"
    if proto_path.exists():
        protocol = load_protocol(proto_path)
        assert protocol.earthsync is None


# --- EMA smoothing and streak tests ---


def test_ema_smoothing_reduces_jitter() -> None:
    """Rapid value changes produce more stable smoothed output."""
    engine = NeurofeedbackEngine(_make_protocol())
    engine.set_smoothing(alpha=0.3, min_streak=1)
    for _ in range(20):
        engine.add_baseline_sample({"smr": 2.0, "theta": 1.0})
    engine.calibrate()

    # Alternate between high and low SMR values (jittery input)
    raw_values = [10.0, 1.0, 10.0, 1.0, 10.0, 1.0, 10.0, 1.0]
    reward_states = []
    for v in raw_values:
        state = engine.evaluate({"smr": v, "theta": 0.5})
        reward_states.append(state.reward)

    # Without smoothing, reward would alternate True/False every epoch.
    # With EMA, the smoothed value lags behind the raw swings, so we
    # should see fewer transitions (more stable output).
    transitions = sum(
        1 for i in range(1, len(reward_states)) if reward_states[i] != reward_states[i - 1]
    )
    # Raw without smoothing would have ~7 transitions; smoothed should have fewer
    assert transitions < len(raw_values) - 1


def test_ema_initial_value() -> None:
    """First evaluation uses raw value directly (no prior EMA)."""
    engine = NeurofeedbackEngine(_make_protocol())
    engine.set_smoothing(alpha=0.3, min_streak=1)
    for _ in range(20):
        engine.add_baseline_sample({"smr": 2.0, "theta": 1.0})
    engine.calibrate()

    # First call: EMA not yet populated, should use raw value
    engine.evaluate({"smr": 5.0, "theta": 0.5})
    # After first call, EMA should equal the raw value
    assert engine._ema_values["smr"] == 5.0
    assert engine._ema_values["theta"] == 0.5


def test_reward_streak_requirement() -> None:
    """Reward only reported after N consecutive above-threshold epochs."""
    engine = NeurofeedbackEngine(_make_protocol())
    engine.set_smoothing(alpha=1.0, min_streak=3)  # alpha=1.0 means no smoothing (raw passthrough)
    for _ in range(20):
        engine.add_baseline_sample({"smr": 2.0, "theta": 1.0})
    engine.calibrate()

    # Epoch 1: above threshold but streak = 1 < 3
    state = engine.evaluate({"smr": 5.0, "theta": 0.5})
    assert not state.reward
    assert state.reward_value == 0.0

    # Epoch 2: streak = 2 < 3
    state = engine.evaluate({"smr": 5.0, "theta": 0.5})
    assert not state.reward

    # Epoch 3: streak = 3 >= 3 -> reward!
    state = engine.evaluate({"smr": 5.0, "theta": 0.5})
    assert state.reward
    assert state.reward_value > 0.0


def test_streak_resets_on_failure() -> None:
    """One failure epoch resets the streak counter to zero."""
    engine = NeurofeedbackEngine(_make_protocol())
    engine.set_smoothing(alpha=1.0, min_streak=3)
    for _ in range(20):
        engine.add_baseline_sample({"smr": 2.0, "theta": 1.0})
    engine.calibrate()

    # Build up streak to 2
    engine.evaluate({"smr": 5.0, "theta": 0.5})
    engine.evaluate({"smr": 5.0, "theta": 0.5})
    assert engine._reward_streak == 2

    # One failure resets
    engine.evaluate({"smr": 0.1, "theta": 0.5})
    assert engine._reward_streak == 0

    # Need 3 more consecutive successes
    engine.evaluate({"smr": 5.0, "theta": 0.5})
    engine.evaluate({"smr": 5.0, "theta": 0.5})
    state = engine.evaluate({"smr": 5.0, "theta": 0.5})
    assert state.reward


def test_set_smoothing_parameters() -> None:
    """Alpha and min_streak are configurable with clamping."""
    engine = NeurofeedbackEngine(_make_protocol())

    engine.set_smoothing(alpha=0.5, min_streak=5)
    assert engine._ema_alpha == 0.5
    assert engine._min_reward_streak == 5

    # Alpha clamped to [0.01, 1.0]
    engine.set_smoothing(alpha=0.0)
    assert engine._ema_alpha == 0.01

    engine.set_smoothing(alpha=2.0)
    assert engine._ema_alpha == 1.0

    # min_streak clamped to >= 1
    engine.set_smoothing(min_streak=0)
    assert engine._min_reward_streak == 1

    engine.set_smoothing(min_streak=-5)
    assert engine._min_reward_streak == 1


def test_reset_smoothing() -> None:
    """Reset clears EMA state and streak counter."""
    engine = NeurofeedbackEngine(_make_protocol())
    engine.set_smoothing(alpha=1.0, min_streak=1)
    for _ in range(20):
        engine.add_baseline_sample({"smr": 2.0, "theta": 1.0})
    engine.calibrate()

    # Build up some state
    engine.evaluate({"smr": 5.0, "theta": 0.5})
    assert len(engine._ema_values) > 0
    assert engine._reward_streak > 0

    # Reset
    engine.reset_smoothing()
    assert engine._ema_values == {}
    assert engine._reward_streak == 0


def test_backward_compatible_smr_protocol() -> None:
    """Existing SMR protocol still works with smoothing enabled.

    With min_streak=1, behavior matches the original evaluate() logic
    (reward on first above-threshold epoch).
    """
    proto_path = Path(__file__).parent.parent.parent / "protocols" / "smr_training.yaml"
    if not proto_path.exists():
        pytest.skip("smr_training.yaml not found")

    protocol = load_protocol(proto_path)
    engine = NeurofeedbackEngine(protocol)
    engine.set_smoothing(alpha=1.0, min_streak=1)  # No smoothing, immediate reward

    # Add baseline samples for all protocol bands
    for _ in range(20):
        sample = {b.name.lower(): 2.0 for b in protocol.bands}
        engine.add_baseline_sample(sample)
    engine.calibrate()
    assert engine.calibrated

    # Provide above-threshold values for enhance bands, below for suppress
    powers = {}
    for band in protocol.bands:
        name = band.name.lower()
        if band.target == "enhance":
            powers[name] = engine.thresholds[name] * 2.0  # Well above threshold
        else:
            powers[name] = engine.thresholds[name] * 0.1  # Well below threshold

    state = engine.evaluate(powers)
    assert state.reward
    assert not state.inhibit
