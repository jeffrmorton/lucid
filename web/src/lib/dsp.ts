/**
 * Lucid — Browser-side DSP utilities.
 * Lightweight FFT and band power computation for real-time display.
 */

/** EEG frequency band definition. */
export interface BandDef {
  name: string;
  low: number;
  high: number;
}

/** Standard EEG bands. */
export const EEG_BAND_DEFS: BandDef[] = [
  { name: 'delta', low: 0.5, high: 4 },
  { name: 'theta', low: 4, high: 8 },
  { name: 'alpha', low: 8, high: 13 },
  { name: 'beta', low: 13, high: 30 },
  { name: 'gamma', low: 30, high: 100 },
];

/**
 * Compute band power from a PSD array.
 * @param psd - Power spectral density values
 * @param freqResolution - Frequency resolution in Hz per bin
 * @param low - Lower frequency bound
 * @param high - Upper frequency bound
 * @returns Sum of PSD values in the frequency range
 */
export function bandPower(
  psd: number[],
  freqResolution: number,
  low: number,
  high: number,
): number {
  const lowBin = Math.floor(low / freqResolution);
  const highBin = Math.ceil(high / freqResolution);
  let sum = 0;
  for (let i = Math.max(0, lowBin); i <= Math.min(psd.length - 1, highBin); i++) {
    sum += psd[i];
  }
  return sum;
}

/**
 * Compute all standard EEG band powers from a PSD.
 */
export function allBandPowers(psd: number[], freqResolution: number): Record<string, number> {
  const result: Record<string, number> = {};
  for (const band of EEG_BAND_DEFS) {
    result[band.name] = bandPower(psd, freqResolution, band.low, band.high);
  }
  return result;
}

/**
 * Convert linear PSD values to dB scale.
 * @param psd - Linear PSD values
 * @param floor - Minimum dB value (default -60)
 * @returns PSD in dB
 */
export function toDecibels(psd: number[], floor = -60): number[] {
  return psd.map((v) => (v > 0 ? Math.max(floor, 10 * Math.log10(v)) : floor));
}

/**
 * Apply a simple moving average smoothing.
 */
export function smooth(data: number[], windowSize: number): number[] {
  if (windowSize <= 1 || data.length === 0) return [...data];
  const half = Math.floor(windowSize / 2);
  return data.map((_, i) => {
    const start = Math.max(0, i - half);
    const end = Math.min(data.length, i + half + 1);
    let sum = 0;
    for (let j = start; j < end; j++) sum += data[j];
    return sum / (end - start);
  });
}
