//! Lucid DSP — High-performance signal processing for EEG.
//!
//! Core DSP routines compiled to native (server via PyO3) and WASM (browser).
//! All functions are pure, stateless, and zero-allocation where possible.

pub mod asr;
pub mod csp;
pub mod features;
pub mod fft;
pub mod filters;

/// EEG frequency band definitions in Hz.
pub mod bands {
    pub const DELTA: (f64, f64) = (0.5, 4.0);
    pub const THETA: (f64, f64) = (4.0, 8.0);
    pub const ALPHA: (f64, f64) = (8.0, 13.0);
    pub const BETA: (f64, f64) = (13.0, 30.0);
    pub const GAMMA: (f64, f64) = (30.0, 100.0);

    /// Schumann resonance Mode 1 — overlaps alpha/theta boundary.
    pub const SR_MODE1: f64 = 7.83;
}
