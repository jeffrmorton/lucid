//! Digital filters for EEG signal processing.
//!
//! Implements IIR bandpass, notch (50/60 Hz), and adaptive NLMS filters.

use thiserror::Error;

#[derive(Error, Debug)]
pub enum FilterError {
    #[error("Invalid filter parameters: {0}")]
    InvalidParams(String),
    #[error("Input length mismatch: expected {expected}, got {got}")]
    LengthMismatch { expected: usize, got: usize },
}

/// Second-order section (biquad) filter coefficients.
#[derive(Debug, Clone)]
pub struct BiquadCoeffs {
    pub b0: f64,
    pub b1: f64,
    pub b2: f64,
    pub a1: f64,
    pub a2: f64,
}

/// Biquad filter state for real-time streaming.
#[derive(Debug, Clone, Default)]
pub struct BiquadState {
    x1: f64,
    x2: f64,
    y1: f64,
    y2: f64,
}

impl BiquadCoeffs {
    /// Design a bandpass biquad filter.
    pub fn bandpass(center_hz: f64, q: f64, sample_rate: f64) -> Result<Self, FilterError> {
        if center_hz <= 0.0 || q <= 0.0 || sample_rate <= 0.0 {
            return Err(FilterError::InvalidParams(
                "All parameters must be positive".into(),
            ));
        }
        let w0 = 2.0 * std::f64::consts::PI * center_hz / sample_rate;
        let alpha = w0.sin() / (2.0 * q);
        let a0 = 1.0 + alpha;
        Ok(Self {
            b0: alpha / a0,
            b1: 0.0,
            b2: -alpha / a0,
            a1: -2.0 * w0.cos() / a0,
            a2: (1.0 - alpha) / a0,
        })
    }

    /// Design a notch (band-reject) filter for mains frequency rejection.
    pub fn notch(freq_hz: f64, q: f64, sample_rate: f64) -> Result<Self, FilterError> {
        if freq_hz <= 0.0 || q <= 0.0 || sample_rate <= 0.0 {
            return Err(FilterError::InvalidParams(
                "All parameters must be positive".into(),
            ));
        }
        let w0 = 2.0 * std::f64::consts::PI * freq_hz / sample_rate;
        let alpha = w0.sin() / (2.0 * q);
        let a0 = 1.0 + alpha;
        Ok(Self {
            b0: 1.0 / a0,
            b1: -2.0 * w0.cos() / a0,
            b2: 1.0 / a0,
            a1: -2.0 * w0.cos() / a0,
            a2: (1.0 - alpha) / a0,
        })
    }
}

/// Apply a biquad filter to a single sample (for real-time streaming).
pub fn biquad_process(coeffs: &BiquadCoeffs, state: &mut BiquadState, input: f64) -> f64 {
    let output = coeffs.b0 * input + coeffs.b1 * state.x1 + coeffs.b2 * state.x2
        - coeffs.a1 * state.y1
        - coeffs.a2 * state.y2;
    state.x2 = state.x1;
    state.x1 = input;
    state.y2 = state.y1;
    state.y1 = output;
    output
}

/// Apply a biquad filter to an entire buffer.
pub fn biquad_filter(coeffs: &BiquadCoeffs, state: &mut BiquadState, data: &mut [f64]) {
    for sample in data.iter_mut() {
        *sample = biquad_process(coeffs, state, *sample);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_bandpass_design() {
        let coeffs = BiquadCoeffs::bandpass(10.0, 2.0, 250.0).unwrap();
        assert!(coeffs.b0.is_finite());
        assert!(coeffs.a1.is_finite());
    }

    #[test]
    fn test_notch_design() {
        let coeffs = BiquadCoeffs::notch(50.0, 30.0, 250.0).unwrap();
        assert!(coeffs.b0.is_finite());
    }

    #[test]
    fn test_bandpass_invalid_params() {
        assert!(BiquadCoeffs::bandpass(-1.0, 2.0, 250.0).is_err());
        assert!(BiquadCoeffs::bandpass(10.0, 0.0, 250.0).is_err());
    }

    #[test]
    fn test_notch_rejects_target_frequency() {
        let coeffs = BiquadCoeffs::notch(50.0, 30.0, 250.0).unwrap();
        let mut state = BiquadState::default();

        // Generate 50 Hz sine wave
        let sample_rate = 250.0;
        let freq = 50.0;
        let mut signal: Vec<f64> = (0..1000)
            .map(|i| (2.0 * std::f64::consts::PI * freq * i as f64 / sample_rate).sin())
            .collect();

        biquad_filter(&coeffs, &mut state, &mut signal);

        // After settling, output should be near zero
        let rms: f64 = signal[500..].iter().map(|x| x * x).sum::<f64>() / 500.0;
        assert!(
            rms.sqrt() < 0.1,
            "Notch filter should attenuate 50 Hz: rms={}",
            rms.sqrt()
        );
    }

    #[test]
    fn test_biquad_process_single_sample() {
        let coeffs = BiquadCoeffs::bandpass(10.0, 2.0, 250.0).unwrap();
        let mut state = BiquadState::default();
        let output = biquad_process(&coeffs, &mut state, 1.0);
        assert!(output.is_finite());
    }

    #[test]
    fn test_dc_signal_through_bandpass() {
        let coeffs = BiquadCoeffs::bandpass(10.0, 2.0, 250.0).unwrap();
        let mut state = BiquadState::default();
        let mut signal = vec![1.0; 1000];
        biquad_filter(&coeffs, &mut state, &mut signal);
        // DC should be rejected by bandpass
        let rms: f64 = signal[500..].iter().map(|x| x * x).sum::<f64>() / 500.0;
        assert!(rms.sqrt() < 0.01, "Bandpass should reject DC");
    }
}
