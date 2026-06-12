/**
 * Synthetic EEG trace preview generator.
 *
 * The /ws/viewer stream delivers band powers and PSD, not per-sample waveforms,
 * so the Signals "EEG Traces" panel shows a *simulated* preview reconstructed
 * from per-channel alpha power plus noise. Kept as a pure, injectable-rng helper
 * (out of the render path) so it is deterministic under test and memoizable.
 */

/** Build a simulated per-channel sample buffer from per-channel alpha power. */
export function buildTraceData(
  channelAlpha: number[],
  channels: number,
  samples = 250,
  rng: () => number = Math.random,
): number[][] {
  return Array.from({ length: channels }, (_, ch) => {
    const alpha = channelAlpha[ch] ?? 0;
    return Array.from({ length: samples }, (_, i) => {
      const t = i / samples;
      return alpha * 0.1 * Math.sin(2 * Math.PI * 10 * t + ch * 0.3) + (rng() - 0.5) * 2;
    });
  });
}
