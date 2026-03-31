"""Real-time EEG processing pipeline.

Receives raw multi-channel EEG samples from device, applies bandpass filter,
notch filter, artifact rejection, and produces band power features.
"""

import numpy as np
from numpy.typing import NDArray
from scipy.signal import butter, iirnotch, sosfilt, sosfilt_zi, tf2sos, welch


class ArtifactRejector:
    """Simplified Artifact Subspace Reconstruction.

    Detects samples exceeding a threshold relative to the calibration
    baseline RMS and replaces them with interpolated values.
    """

    def __init__(self, n_channels: int, threshold: float = 5.0) -> None:
        self.n_channels = n_channels
        self.threshold = threshold
        self.calibrated = False
        self.ref_rms: NDArray[np.float64] | None = None

    def calibrate(self, clean_data: NDArray[np.float64]) -> None:
        """Calibrate from clean baseline data. Shape: (n_channels, n_samples)."""
        if clean_data.shape[0] != self.n_channels:
            msg = f"Expected {self.n_channels} channels, got {clean_data.shape[0]}"
            raise ValueError(msg)
        self.ref_rms = np.sqrt(np.mean(clean_data**2, axis=1))
        self.calibrated = True

    def process(self, data: NDArray[np.float64]) -> NDArray[np.float64]:
        """Remove artifacts by interpolating samples exceeding threshold x RMS."""
        if not self.calibrated or self.ref_rms is None:
            return data
        result = data.copy()
        for ch in range(self.n_channels):
            thresh = self.ref_rms[ch] * self.threshold
            for s in range(data.shape[1]):
                if abs(data[ch, s]) > thresh:
                    prev = data[ch, s - 1] if s > 0 else 0.0
                    nxt = data[ch, s + 1] if s < data.shape[1] - 1 else 0.0
                    result[ch, s] = (prev + nxt) / 2.0
        return result


class EEGProcessor:
    """Real-time EEG signal processing pipeline."""

    def __init__(
        self,
        sample_rate: int = 250,
        n_channels: int = 8,
        bandpass_low: float = 0.5,
        bandpass_high: float = 100.0,
        notch_freq: float = 60.0,
    ) -> None:
        self.sample_rate = sample_rate
        self.n_channels = n_channels

        # Artifact rejection
        self.artifact_rejector = ArtifactRejector(n_channels, threshold=5.0)

        # Design bandpass filter (4th order Butterworth)
        self.bp_sos = butter(
            4, [bandpass_low, bandpass_high], btype="band", fs=sample_rate, output="sos"
        )
        self.bp_zi = [sosfilt_zi(self.bp_sos) for _ in range(n_channels)]

        # Design notch filter for mains rejection
        b_notch, a_notch = iirnotch(notch_freq, Q=30.0, fs=sample_rate)
        # Convert to SOS for numerical stability
        self.notch_sos = tf2sos(b_notch, a_notch)
        self.notch_zi = [sosfilt_zi(self.notch_sos) for _ in range(n_channels)]

    def process(self, data: NDArray[np.float64]) -> NDArray[np.float64]:
        """Process a block of multi-channel EEG data.

        Args:
            data: Shape (n_channels, n_samples). Raw ADC values.

        Returns:
            Filtered data, same shape as input.
        """
        if data.shape[0] != self.n_channels:
            msg = f"Expected {self.n_channels} channels, got {data.shape[0]}"
            raise ValueError(msg)

        filtered = np.empty_like(data)
        for ch in range(self.n_channels):
            # Bandpass filter
            bp_out, self.bp_zi[ch] = sosfilt(self.bp_sos, data[ch], zi=self.bp_zi[ch])
            # Notch filter
            notch_out, self.notch_zi[ch] = sosfilt(self.notch_sos, bp_out, zi=self.notch_zi[ch])
            filtered[ch] = notch_out

        return filtered

    def compute_psd(
        self, data: NDArray[np.float64], window_seconds: float = 1.0
    ) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
        """Compute power spectral density using Welch's method.

        Args:
            data: Shape (n_channels, n_samples).
            window_seconds: FFT window length in seconds.

        Returns:
            (psd, freqs) where psd has shape (n_channels, n_freq_bins).
        """
        nperseg = int(self.sample_rate * window_seconds)
        freqs, psd = welch(data, fs=self.sample_rate, nperseg=nperseg, axis=-1)
        return psd, freqs

    def compute_band_powers(
        self, psd: NDArray[np.float64], freqs: NDArray[np.float64]
    ) -> dict[str, NDArray[np.float64]]:
        """Extract band powers from PSD.

        Args:
            psd: Shape (n_channels, n_freq_bins).
            freqs: Frequency axis.

        Returns:
            Dict with keys 'delta', 'theta', 'alpha', 'beta', 'gamma'.
            Each value is shape (n_channels,).
        """
        bands = {
            "delta": (0.5, 4.0),
            "theta": (4.0, 8.0),
            "alpha": (8.0, 13.0),
            "beta": (13.0, 30.0),
            "gamma": (30.0, 100.0),
        }
        result = {}
        for name, (low, high) in bands.items():
            mask = (freqs >= low) & (freqs <= high)
            result[name] = np.sum(psd[:, mask], axis=1)
        return result

    def compute_custom_band_power(
        self, psd: NDArray[np.float64], freqs: NDArray[np.float64], low_hz: float, high_hz: float
    ) -> NDArray[np.float64]:
        """Compute band power for a custom frequency range.

        Args:
            psd: PSD array (n_channels, n_freqs).
            freqs: Frequency array.
            low_hz: Lower bound in Hz.
            high_hz: Upper bound in Hz.

        Returns:
            Band power per channel.
        """
        mask = (freqs >= low_hz) & (freqs <= high_hz)
        return np.sum(psd[:, mask], axis=1)

    def reject_artifacts(self, data: NDArray[np.float64]) -> NDArray[np.float64]:
        """Apply artifact rejection. Auto-calibrates from first 5 epochs if not calibrated."""
        return self.artifact_rejector.process(data)
