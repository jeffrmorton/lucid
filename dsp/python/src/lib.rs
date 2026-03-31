//! Lucid DSP — Python bindings via PyO3.

use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use numpy::PyArray1;
use ::lucid_dsp::filters::{BiquadCoeffs, BiquadState, biquad_filter};
use ::lucid_dsp::fft::compute_psd;
use ::lucid_dsp::features::{band_power, all_band_powers};

/// Compute PSD from raw EEG signal.
/// Returns (psd, freqs) as numpy arrays.
#[pyfunction]
fn compute_psd_py<'py>(
    py: Python<'py>,
    signal: Vec<f64>,
    sample_rate: f64,
) -> PyResult<(Bound<'py, PyArray1<f64>>, Bound<'py, PyArray1<f64>>)> {
    let (psd, freqs) = compute_psd(&signal, sample_rate)
        .map_err(|e| PyValueError::new_err(e.to_string()))?;
    Ok((PyArray1::from_vec(py, psd), PyArray1::from_vec(py, freqs)))
}

/// Apply a notch filter to a signal in-place.
#[pyfunction]
fn apply_notch_filter_py(signal: Vec<f64>, freq_hz: f64, q: f64, sample_rate: f64) -> PyResult<Vec<f64>> {
    let coeffs = BiquadCoeffs::notch(freq_hz, q, sample_rate)
        .map_err(|e| PyValueError::new_err(e.to_string()))?;
    let mut state = BiquadState::default();
    let mut data = signal;
    biquad_filter(&coeffs, &mut state, &mut data);
    Ok(data)
}

/// Apply a bandpass filter.
#[pyfunction]
fn apply_bandpass_filter_py(signal: Vec<f64>, center_hz: f64, q: f64, sample_rate: f64) -> PyResult<Vec<f64>> {
    let coeffs = BiquadCoeffs::bandpass(center_hz, q, sample_rate)
        .map_err(|e| PyValueError::new_err(e.to_string()))?;
    let mut state = BiquadState::default();
    let mut data = signal;
    biquad_filter(&coeffs, &mut state, &mut data);
    Ok(data)
}

/// Compute band power from PSD.
#[pyfunction]
fn compute_band_power_py(psd: Vec<f64>, freqs: Vec<f64>, low_hz: f64, high_hz: f64) -> f64 {
    band_power(&psd, &freqs, low_hz, high_hz)
}

/// Compute all standard EEG band powers.
#[pyfunction]
fn compute_all_band_powers_py(psd: Vec<f64>, freqs: Vec<f64>) -> PyResult<(f64, f64, f64, f64, f64)> {
    let bp = all_band_powers(&psd, &freqs);
    Ok((bp.delta, bp.theta, bp.alpha, bp.beta, bp.gamma))
}

/// Lucid DSP Python module.
#[pymodule]
fn lucid_dsp(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(compute_psd_py, m)?)?;
    m.add_function(wrap_pyfunction!(apply_notch_filter_py, m)?)?;
    m.add_function(wrap_pyfunction!(apply_bandpass_filter_py, m)?)?;
    m.add_function(wrap_pyfunction!(compute_band_power_py, m)?)?;
    m.add_function(wrap_pyfunction!(compute_all_band_powers_py, m)?)?;
    Ok(())
}
