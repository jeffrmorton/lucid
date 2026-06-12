"""BrainFlow bridge for Lucid SDK.

Wraps BrainFlow's board API to provide a unified interface
for synthetic and real EEG data acquisition.
Handles the case where BrainFlow is not installed gracefully.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from numpy.typing import NDArray

BoardIds: Any
BoardShim: Any
BrainFlowInputParams: Any
try:
    from brainflow.board_shim import (  # type: ignore[no-redef]
        BoardIds,
        BoardShim,
        BrainFlowInputParams,
    )  # pragma: no cover

    BRAINFLOW_AVAILABLE = True  # pragma: no cover
except ImportError:
    BoardIds = None
    BoardShim = None
    BrainFlowInputParams = None
    BRAINFLOW_AVAILABLE = False


class BrainFlowBridge:
    """Bridge between BrainFlow boards and Lucid SDK.

    Uses BrainFlow's synthetic board by default for development/testing.
    Falls back gracefully if BrainFlow is not installed.

    Common board IDs:
        -1  Synthetic (default, no hardware needed)
         0  OpenBCI Cyton (8-ch, serial)
         1  OpenBCI Ganglion (4-ch, BLE)
         2  OpenBCI Cyton + Daisy (16-ch, serial)
         5  OpenBCI Cyton WiFi (8-ch, WiFi)
         7  BrainBit (4-ch, BLE)
         8  g.tec Unicorn (8-ch, BLE)
        17  FreeEEG32 (32-ch, USB)
        21  Muse S (4-ch, BLE)
        22  Muse 2 (4-ch, BLE)
        23  Neurosity Crown (8-ch, WiFi)
        40  PiEEG (8-ch, SPI)

    Full list: https://brainflow.readthedocs.io/en/stable/SupportedBoards.html
    """

    def __init__(
        self,
        board_id: int | None = None,
        sample_rate: int = 250,
        n_channels: int = 8,
    ) -> None:
        self.sample_rate = sample_rate
        self.n_channels = n_channels
        self.board_id = board_id
        self.streaming = False
        self._board: Any = None

    @property
    def available(self) -> bool:
        """Check if BrainFlow is installed and available."""
        return BRAINFLOW_AVAILABLE

    def start(self) -> bool:
        """Start data acquisition.

        Returns:
            True if started successfully, False if BrainFlow not available.
        """
        if not BRAINFLOW_AVAILABLE:
            return False

        board_id = self.board_id if self.board_id is not None else BoardIds.SYNTHETIC_BOARD.value
        params = BrainFlowInputParams()
        self._board = BoardShim(board_id, params)
        self._board.prepare_session()
        self._board.start_stream()
        self.streaming = True
        return True

    def stop(self) -> None:
        """Stop data acquisition."""
        if self._board is not None and self.streaming:
            self._board.stop_stream()
            self._board.release_session()
        self.streaming = False
        self._board = None

    def read(self, n_samples: int = 250) -> NDArray[np.float64]:
        """Read EEG samples from the board.

        Always returns shape (n_channels, n_samples). If the board exposes
        fewer EEG channels than ``n_channels`` (e.g. Muse 2 = 4 ch with the
        default n_channels=8), the missing rows are zero-padded so downstream
        code that assumes n_channels rows never misaligns. Returns zeros if not
        streaming.

        Args:
            n_samples: Number of samples to read.

        Returns:
            Array of shape (n_channels, n_samples).
        """
        if not self.streaming or self._board is None:
            return np.zeros((self.n_channels, n_samples))

        data = self._board.get_board_data(n_samples)
        # BrainFlow returns all channels; select EEG channels only
        eeg_channels = BoardShim.get_eeg_channels(
            self.board_id if self.board_id is not None else BoardIds.SYNTHETIC_BOARD.value
        )
        selected = eeg_channels[: self.n_channels]
        if len(selected) == 0 or data.shape[1] == 0:
            return np.zeros((self.n_channels, n_samples))

        out = np.zeros((self.n_channels, n_samples), dtype=np.float64)
        rows = data[selected, :n_samples].astype(np.float64)
        out[: rows.shape[0], : rows.shape[1]] = rows
        return out

    @property
    def is_streaming(self) -> bool:
        """Check if the board is currently streaming."""
        return self.streaming
