//! Common Spatial Patterns (CSP) for motor imagery BCI.
//!
//! CSP finds spatial filters that maximize variance for one class
//! while minimizing it for another.

/// Placeholder for CSP implementation.
/// Full implementation requires eigendecomposition of covariance matrices.
pub struct CspFilter {
    pub n_components: usize,
    pub filters: Vec<Vec<f64>>,
    pub fitted: bool,
}

impl CspFilter {
    pub fn new(n_components: usize) -> Self {
        Self {
            n_components,
            filters: Vec::new(),
            fitted: false,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_csp_new() {
        let csp = CspFilter::new(4);
        assert_eq!(csp.n_components, 4);
        assert!(!csp.fitted);
    }
}
