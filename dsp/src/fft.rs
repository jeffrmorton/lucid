//! FFT computation for EEG spectral analysis.

use rustfft::{FftPlanner, num_complex::Complex};
use thiserror::Error;

#[derive(Error, Debug)]
pub enum FftError {
    #[error("Input length must be > 0")]
    EmptyInput,
}

/// Compute the one-sided power spectral density of a real signal.
///
/// Returns (psd, freqs) where psd has length nfft/2 + 1.
pub fn compute_psd(signal: &[f64], sample_rate: f64) -> Result<(Vec<f64>, Vec<f64>), FftError> {
    if signal.is_empty() {
        return Err(FftError::EmptyInput);
    }

    let n = signal.len();
    let nfft = n.next_power_of_two();

    // Apply Hann window
    let mut windowed: Vec<Complex<f64>> = (0..nfft)
        .map(|i| {
            if i < n {
                let w =
                    0.5 * (1.0 - (2.0 * std::f64::consts::PI * i as f64 / (n - 1) as f64).cos());
                Complex::new(signal[i] * w, 0.0)
            } else {
                Complex::new(0.0, 0.0) // zero-pad
            }
        })
        .collect();

    // Window power for normalization
    let s2: f64 = (0..n)
        .map(|i| {
            let w = 0.5 * (1.0 - (2.0 * std::f64::consts::PI * i as f64 / (n - 1) as f64).cos());
            w * w
        })
        .sum();

    // FFT
    let mut planner = FftPlanner::new();
    let fft = planner.plan_fft_forward(nfft);
    fft.process(&mut windowed);

    // One-sided PSD
    let num_bins = nfft / 2 + 1;
    let scale = 2.0 / (sample_rate * s2);
    let mut psd = Vec::with_capacity(num_bins);
    let mut freqs = Vec::with_capacity(num_bins);

    for (k, w) in windowed.iter().enumerate().take(num_bins) {
        let mag_sq = w.norm_sqr();
        let mut p = scale * mag_sq;
        if k == 0 || k == num_bins - 1 {
            p /= 2.0; // DC and Nyquist not doubled
        }
        psd.push(p);
        freqs.push(k as f64 * sample_rate / nfft as f64);
    }

    Ok((psd, freqs))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_psd_pure_sinusoid() {
        let sample_rate = 250.0;
        let freq = 10.0;
        let n = 2500; // 10 seconds
        let signal: Vec<f64> = (0..n)
            .map(|i| (2.0 * std::f64::consts::PI * freq * i as f64 / sample_rate).sin())
            .collect();

        let (psd, freqs) = compute_psd(&signal, sample_rate).unwrap();

        // Find peak
        let peak_idx = psd
            .iter()
            .enumerate()
            .max_by(|a, b| a.1.partial_cmp(b.1).unwrap())
            .unwrap()
            .0;
        let peak_freq = freqs[peak_idx];

        assert!(
            (peak_freq - freq).abs() < 1.0,
            "Peak at {peak_freq} Hz, expected {freq} Hz"
        );
    }

    #[test]
    fn test_psd_empty_input() {
        assert!(compute_psd(&[], 250.0).is_err());
    }

    #[test]
    fn test_psd_dc_signal() {
        let signal = vec![1.0; 250];
        let (psd, _) = compute_psd(&signal, 250.0).unwrap();
        // DC bin should have most power
        assert!(psd[0] > psd[10]);
    }

    #[test]
    fn test_psd_output_length() {
        let signal = vec![0.0; 256];
        let (psd, freqs) = compute_psd(&signal, 250.0).unwrap();
        assert_eq!(psd.len(), freqs.len());
        assert_eq!(psd.len(), 129); // 256/2 + 1
    }

    #[test]
    fn test_psd_all_positive() {
        let signal: Vec<f64> = (0..250).map(|i| (i as f64 * 0.1).sin()).collect();
        let (psd, _) = compute_psd(&signal, 250.0).unwrap();
        assert!(psd.iter().all(|&p| p >= 0.0));
    }
}
