# Neurofeedback Guide

## Available Protocols

Lucid ships with three neurofeedback protocols defined in `protocols/`:

| Protocol | File | Target Band | Electrode | Evidence Level |
|----------|------|-------------|-----------|----------------|
| SMR Training | `smr_training.yaml` | 12-15 Hz enhance, theta/high-beta suppress | Cz | Moderate |
| Alpha/Theta | `alpha_theta.yaml` | Alpha enhance, theta modulation | Pz | Moderate |
| Beta Training | `beta_training.yaml` | 15-20 Hz enhance | Cz | Preliminary |

## Evidence Levels

- **Moderate**: Multiple controlled studies with consistent positive outcomes (e.g., SMR for focus, alpha/theta for relaxation).
- **Preliminary**: Supported by pilot studies or case reports. More research needed for definitive conclusions.

Neurofeedback is an active area of research. Evidence quality varies significantly between protocols and target conditions. Always interpret results critically.

## Running a Session

1. Select a protocol in the Neurofeedback panel or via the `/ws/neurofeedback` WebSocket.
2. **Calibration phase** (typically 2 minutes): Sit quietly with eyes open. The system records baseline band power levels to set personalized thresholds.
3. **Training phase** (typically 20 minutes): The system provides real-time audio/visual feedback. A reward signal fires when the target band exceeds the calibrated threshold. An inhibit signal fires when suppression bands exceed their thresholds.
4. Review session summary statistics after completion.

For best results, train 2-3 times per week over 20+ sessions. Single sessions may show acute effects but long-term learning requires repetition.

## ADHD Caveat

SMR and beta neurofeedback have been studied for ADHD symptoms, with some meta-analyses showing moderate effect sizes. However, the largest randomized controlled trials (e.g., Cortese et al. 2016) show that effects diminish when using probably-blinded assessors. Neurofeedback should not replace evidence-based ADHD treatments (behavioral therapy, medication). If pursuing neurofeedback for ADHD, do so under clinical supervision and as an adjunct, not a replacement.
