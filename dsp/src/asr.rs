//! Artifact Subspace Reconstruction (ASR) for real-time EEG artifact rejection.
//!
//! ASR identifies and reconstructs artifact-contaminated data segments by
//! comparing the current signal subspace against a clean reference subspace.
//! Reference: Mullen et al., 2015.

use ndarray::{Array1, Array2};
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AsrError {
    #[error("Insufficient calibration data: need {needed} samples, got {got}")]
    InsufficientData { needed: usize, got: usize },
    #[error("Channel count mismatch: expected {expected}, got {got}")]
    ChannelMismatch { expected: usize, got: usize },
}

/// ASR state — stores the clean reference subspace from calibration.
#[derive(Debug, Clone)]
pub struct AsrState {
    /// Number of channels.
    pub n_channels: usize,
    /// Mixing matrix from calibration PCA.
    pub mixing: Array2<f64>,
    /// Threshold for artifact detection (in standard deviations).
    pub threshold: f64,
    /// Reference RMS per component.
    pub ref_rms: Array1<f64>,
    /// Whether calibration has been performed.
    pub calibrated: bool,
}

impl AsrState {
    /// Create a new uncalibrated ASR state.
    pub fn new(n_channels: usize, threshold: f64) -> Self {
        Self {
            n_channels,
            mixing: Array2::zeros((n_channels, n_channels)),
            threshold,
            ref_rms: Array1::zeros(n_channels),
            calibrated: false,
        }
    }

    /// Calibrate ASR from clean reference data.
    ///
    /// `data` shape: (n_channels, n_samples). Should be artifact-free baseline.
    pub fn calibrate(&mut self, data: &Array2<f64>) -> Result<(), AsrError> {
        let (n_ch, n_samples) = data.dim();
        if n_ch != self.n_channels {
            return Err(AsrError::ChannelMismatch {
                expected: self.n_channels,
                got: n_ch,
            });
        }
        let min_samples = self.n_channels * 10;
        if n_samples < min_samples {
            return Err(AsrError::InsufficientData {
                needed: min_samples,
                got: n_samples,
            });
        }

        // Compute covariance matrix
        let mean = data.mean_axis(ndarray::Axis(1)).unwrap();
        let centered = data - &mean.insert_axis(ndarray::Axis(1));
        let _cov = centered.dot(&centered.t()) / (n_samples - 1) as f64;

        // Store identity as mixing matrix (simplified — full PCA would use eigendecomposition)
        self.mixing = Array2::eye(n_ch);

        // Reference RMS per channel
        for ch in 0..n_ch {
            let channel_data = data.row(ch);
            let rms = (channel_data.mapv(|x| x * x).sum() / n_samples as f64).sqrt();
            self.ref_rms[ch] = rms;
        }

        self.calibrated = true;
        Ok(())
    }

    /// Process a block of data through ASR.
    ///
    /// `data` shape: (n_channels, n_samples). Modified in place.
    pub fn process(&self, data: &mut Array2<f64>) -> Result<(), AsrError> {
        if !self.calibrated {
            return Ok(()); // Pass through if not calibrated
        }
        let (n_ch, n_samples) = data.dim();
        if n_ch != self.n_channels {
            return Err(AsrError::ChannelMismatch {
                expected: self.n_channels,
                got: n_ch,
            });
        }

        // Simplified ASR: detect and interpolate artifact-contaminated samples
        for ch in 0..n_ch {
            let threshold = self.ref_rms[ch] * self.threshold;
            for s in 0..n_samples {
                if data[[ch, s]].abs() > threshold {
                    // Replace with interpolated value (simplified)
                    let prev = if s > 0 { data[[ch, s - 1]] } else { 0.0 };
                    let next = if s < n_samples - 1 {
                        data[[ch, s + 1]]
                    } else {
                        0.0
                    };
                    data[[ch, s]] = (prev + next) / 2.0;
                }
            }
        }

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_asr_new() {
        let asr = AsrState::new(8, 5.0);
        assert_eq!(asr.n_channels, 8);
        assert!(!asr.calibrated);
    }

    #[test]
    fn test_asr_calibrate() {
        let mut asr = AsrState::new(2, 5.0);
        let data = Array2::from_shape_fn((2, 100), |(_, j)| (j as f64 * 0.1).sin());
        asr.calibrate(&data).unwrap();
        assert!(asr.calibrated);
        assert!(asr.ref_rms[0] > 0.0);
    }

    #[test]
    fn test_asr_calibrate_insufficient_data() {
        let mut asr = AsrState::new(8, 5.0);
        let data = Array2::zeros((8, 10)); // Need 80 samples minimum
        assert!(asr.calibrate(&data).is_err());
    }

    #[test]
    fn test_asr_calibrate_channel_mismatch() {
        let mut asr = AsrState::new(8, 5.0);
        let data = Array2::zeros((4, 100));
        assert!(asr.calibrate(&data).is_err());
    }

    #[test]
    fn test_asr_process_uncalibrated_passthrough() {
        let asr = AsrState::new(2, 5.0);
        let mut data = Array2::from_shape_fn((2, 50), |(_, j)| j as f64);
        let original = data.clone();
        asr.process(&mut data).unwrap();
        assert_eq!(data, original); // Should pass through unchanged
    }

    #[test]
    fn test_asr_process_removes_artifact() {
        let mut asr = AsrState::new(1, 3.0);
        // Calibrate with clean small-amplitude signal
        let clean = Array2::from_shape_fn((1, 200), |(_, j)| (j as f64 * 0.1).sin() * 0.1);
        asr.calibrate(&clean).unwrap();

        // Create data with a large artifact at sample 25
        let mut data = Array2::from_shape_fn((1, 50), |(_, j)| (j as f64 * 0.1).sin() * 0.1);
        data[[0, 25]] = 100.0; // Artifact

        asr.process(&mut data).unwrap();
        assert!(
            data[[0, 25]].abs() < 50.0,
            "Artifact should be reduced: {}",
            data[[0, 25]]
        );
    }
}
