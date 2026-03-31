"""Tests for BrainFlow bridge — work even without BrainFlow installed."""

from unittest.mock import MagicMock, patch

import numpy as np
from lucid.brainflow_bridge import BrainFlowBridge


def test_bridge_creation() -> None:
    bridge = BrainFlowBridge()
    assert bridge.sample_rate == 250
    assert bridge.n_channels == 8
    assert not bridge.streaming


def test_bridge_custom_params() -> None:
    bridge = BrainFlowBridge(board_id=42, sample_rate=500, n_channels=16)
    assert bridge.board_id == 42
    assert bridge.sample_rate == 500
    assert bridge.n_channels == 16


def test_available_property() -> None:
    bridge = BrainFlowBridge()
    # Returns bool regardless of whether brainflow is installed
    assert isinstance(bridge.available, bool)


def test_read_when_not_streaming() -> None:
    bridge = BrainFlowBridge()
    data = bridge.read(100)
    assert data.shape == (8, 100)
    np.testing.assert_array_equal(data, np.zeros((8, 100)))


def test_is_streaming_false_by_default() -> None:
    bridge = BrainFlowBridge()
    assert not bridge.is_streaming


def test_stop_when_not_started() -> None:
    bridge = BrainFlowBridge()
    # Should not raise
    bridge.stop()
    assert not bridge.streaming


@patch("lucid.brainflow_bridge.BRAINFLOW_AVAILABLE", False)
def test_start_without_brainflow() -> None:
    bridge = BrainFlowBridge()
    result = bridge.start()
    assert not result
    assert not bridge.streaming


def test_is_streaming_after_manual_set() -> None:
    bridge = BrainFlowBridge()
    bridge.streaming = True
    assert bridge.is_streaming
    bridge.streaming = False
    assert not bridge.is_streaming


@patch("lucid.brainflow_bridge.BRAINFLOW_AVAILABLE", True)
def test_start_with_mocked_brainflow() -> None:
    mock_board = MagicMock()
    mock_board_class = MagicMock(return_value=mock_board)
    mock_params_class = MagicMock()

    with (
        patch("lucid.brainflow_bridge.BoardShim", mock_board_class),
        patch("lucid.brainflow_bridge.BrainFlowInputParams", mock_params_class),
        patch("lucid.brainflow_bridge.BoardIds") as mock_ids,
    ):
        mock_ids.SYNTHETIC_BOARD.value = -1
        bridge = BrainFlowBridge()
        result = bridge.start()
        assert result
        assert bridge.streaming
        mock_board.prepare_session.assert_called_once()
        mock_board.start_stream.assert_called_once()


@patch("lucid.brainflow_bridge.BRAINFLOW_AVAILABLE", True)
def test_stop_releases_session() -> None:
    mock_board = MagicMock()
    mock_board_class = MagicMock(return_value=mock_board)
    mock_params_class = MagicMock()

    with (
        patch("lucid.brainflow_bridge.BoardShim", mock_board_class),
        patch("lucid.brainflow_bridge.BrainFlowInputParams", mock_params_class),
        patch("lucid.brainflow_bridge.BoardIds") as mock_ids,
    ):
        mock_ids.SYNTHETIC_BOARD.value = -1
        bridge = BrainFlowBridge()
        bridge.start()
        bridge.stop()
        assert not bridge.streaming
        mock_board.stop_stream.assert_called_once()
        mock_board.release_session.assert_called_once()


@patch("lucid.brainflow_bridge.BRAINFLOW_AVAILABLE", True)
def test_read_with_empty_eeg_channels() -> None:
    mock_board = MagicMock()
    mock_board.get_board_data.return_value = np.random.randn(16, 100)
    mock_board_class = MagicMock(return_value=mock_board)
    mock_params_class = MagicMock()

    with (
        patch("lucid.brainflow_bridge.BoardShim", mock_board_class) as mock_shim_cls,
        patch("lucid.brainflow_bridge.BrainFlowInputParams", mock_params_class),
        patch("lucid.brainflow_bridge.BoardIds") as mock_ids,
    ):
        mock_ids.SYNTHETIC_BOARD.value = -1
        # Return empty eeg channels list
        mock_shim_cls.get_eeg_channels.return_value = []

        bridge = BrainFlowBridge()
        bridge.start()
        data = bridge.read(100)
        assert data.shape == (8, 100)
        np.testing.assert_array_equal(data, np.zeros((8, 100)))


@patch("lucid.brainflow_bridge.BRAINFLOW_AVAILABLE", True)
def test_read_with_mocked_board() -> None:
    mock_board = MagicMock()
    # Simulate board returning 16 channels x 100 samples
    mock_board.get_board_data.return_value = np.random.randn(16, 100)
    mock_board_class = MagicMock(return_value=mock_board)
    mock_params_class = MagicMock()

    with (
        patch("lucid.brainflow_bridge.BoardShim", mock_board_class) as mock_shim_cls,
        patch("lucid.brainflow_bridge.BrainFlowInputParams", mock_params_class),
        patch("lucid.brainflow_bridge.BoardIds") as mock_ids,
    ):
        mock_ids.SYNTHETIC_BOARD.value = -1
        # Mock get_eeg_channels to return first 8 channels
        mock_shim_cls.get_eeg_channels.return_value = list(range(8))

        bridge = BrainFlowBridge()
        bridge.start()
        data = bridge.read(100)
        assert data.shape == (8, 100)
        assert data.dtype == np.float64
