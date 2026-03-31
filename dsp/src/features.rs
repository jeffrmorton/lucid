//! Feature extraction for EEG signals.

/// Compute band power in a specific frequency range from a PSD.
pub fn band_power(psd: &[f64], freqs: &[f64], low_hz: f64, high_hz: f64) -> f64 {
    psd.iter()
        .zip(freqs.iter())
        .filter(|&(_, &f)| f >= low_hz && f <= high_hz)
        .map(|(&p, _)| p)
        .sum::<f64>()
}

/// Compute band powers for all standard EEG bands.
pub fn all_band_powers(psd: &[f64], freqs: &[f64]) -> BandPowers {
    BandPowers {
        delta: band_power(psd, freqs, 0.5, 4.0),
        theta: band_power(psd, freqs, 4.0, 8.0),
        alpha: band_power(psd, freqs, 8.0, 13.0),
        beta: band_power(psd, freqs, 13.0, 30.0),
        gamma: band_power(psd, freqs, 30.0, 100.0),
    }
}

/// Standard EEG band powers.
#[derive(Debug, Clone)]
pub struct BandPowers {
    pub delta: f64,
    pub theta: f64,
    pub alpha: f64,
    pub beta: f64,
    pub gamma: f64,
}

impl BandPowers {
    /// Total power across all bands.
    pub fn total(&self) -> f64 {
        self.delta + self.theta + self.alpha + self.beta + self.gamma
    }

    /// Relative power of a band (0.0 to 1.0).
    pub fn relative_alpha(&self) -> f64 {
        let total = self.total();
        if total > 0.0 { self.alpha / total } else { 0.0 }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_band_power_simple() {
        let psd = vec![1.0, 2.0, 3.0, 4.0, 5.0];
        let freqs = vec![0.0, 5.0, 10.0, 15.0, 20.0];
        let power = band_power(&psd, &freqs, 5.0, 15.0);
        assert_eq!(power, 9.0); // 2 + 3 + 4
    }

    #[test]
    fn test_band_power_empty_range() {
        let psd = vec![1.0, 2.0, 3.0];
        let freqs = vec![0.0, 5.0, 10.0];
        let power = band_power(&psd, &freqs, 20.0, 30.0);
        assert_eq!(power, 0.0);
    }

    #[test]
    fn test_all_band_powers() {
        // Create a PSD with known band powers
        let mut psd = vec![0.0; 501]; // 0 to 125 Hz at 0.25 Hz resolution
        let freqs: Vec<f64> = (0..501).map(|i| i as f64 * 0.25).collect();

        // Put power in alpha band (8-13 Hz) = bins 32-52
        for item in psd.iter_mut().take(52 + 1).skip(32) {
            *item = 1.0;
        }

        let bp = all_band_powers(&psd, &freqs);
        assert!(bp.alpha > 0.0);
        assert!(bp.delta == 0.0 || bp.delta < 0.01);
        assert!(bp.relative_alpha() > 0.9);
    }

    #[test]
    fn test_band_powers_total() {
        let bp = BandPowers {
            delta: 1.0,
            theta: 2.0,
            alpha: 3.0,
            beta: 4.0,
            gamma: 5.0,
        };
        assert_eq!(bp.total(), 15.0);
    }

    #[test]
    fn test_relative_alpha_zero_total() {
        let bp = BandPowers {
            delta: 0.0,
            theta: 0.0,
            alpha: 0.0,
            beta: 0.0,
            gamma: 0.0,
        };
        assert_eq!(bp.relative_alpha(), 0.0);
    }
}
