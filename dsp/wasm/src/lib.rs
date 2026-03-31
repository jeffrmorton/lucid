//! Lucid DSP — WebAssembly bindings for browser-side EEG processing.

use wasm_bindgen::prelude::*;
use lucid_dsp::filters::{BiquadCoeffs, BiquadState, biquad_filter};
use lucid_dsp::fft::compute_psd;
use lucid_dsp::features::{band_power, all_band_powers, BandPowers};

/// Compute power spectral density from raw EEG samples.
/// Returns a JS object with `psd` and `freqs` arrays.
#[wasm_bindgen]
pub fn compute_psd_wasm(signal: &[f64], sample_rate: f64) -> Result<JsValue, JsError> {
    let (psd, freqs) = compute_psd(signal, sample_rate)
        .map_err(|e| JsError::new(&e.to_string()))?;

    let result = serde_wasm_bindgen::to_value(&(psd, freqs))
        .map_err(|e| JsError::new(&e.to_string()))?;
    Ok(result)
}

/// Design a notch filter and apply it to a signal.
/// Returns the filtered signal.
#[wasm_bindgen]
pub fn apply_notch_filter(signal: &mut [f64], freq_hz: f64, q: f64, sample_rate: f64) -> Result<(), JsError> {
    let coeffs = BiquadCoeffs::notch(freq_hz, q, sample_rate)
        .map_err(|e| JsError::new(&e.to_string()))?;
    let mut state = BiquadState::default();
    biquad_filter(&coeffs, &mut state, signal);
    Ok(())
}

/// Design a bandpass filter and apply it to a signal.
#[wasm_bindgen]
pub fn apply_bandpass_filter(signal: &mut [f64], center_hz: f64, q: f64, sample_rate: f64) -> Result<(), JsError> {
    let coeffs = BiquadCoeffs::bandpass(center_hz, q, sample_rate)
        .map_err(|e| JsError::new(&e.to_string()))?;
    let mut state = BiquadState::default();
    biquad_filter(&coeffs, &mut state, signal);
    Ok(())
}

/// Compute band power from a PSD array.
#[wasm_bindgen]
pub fn compute_band_power(psd: &[f64], freqs: &[f64], low_hz: f64, high_hz: f64) -> f64 {
    band_power(psd, freqs, low_hz, high_hz)
}

/// Compute all standard EEG band powers.
/// Returns a JS object with delta, theta, alpha, beta, gamma fields.
#[wasm_bindgen]
pub fn compute_all_band_powers(psd: &[f64], freqs: &[f64]) -> Result<JsValue, JsError> {
    let powers = all_band_powers(psd, freqs);
    let result = serde_wasm_bindgen::to_value(&serde_powers(&powers))
        .map_err(|e| JsError::new(&e.to_string()))?;
    Ok(result)
}

#[derive(serde::Serialize)]
struct BandPowersJs {
    delta: f64,
    theta: f64,
    alpha: f64,
    beta: f64,
    gamma: f64,
}

fn serde_powers(bp: &BandPowers) -> BandPowersJs {
    BandPowersJs {
        delta: bp.delta,
        theta: bp.theta,
        alpha: bp.alpha,
        beta: bp.beta,
        gamma: bp.gamma,
    }
}
