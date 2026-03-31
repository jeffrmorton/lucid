import { describe, it, expect } from 'vitest';
import {
  bandPower,
  allBandPowers,
  toDecibels,
  smooth,
  EEG_BAND_DEFS,
} from '../src/lib/dsp';

describe('EEG_BAND_DEFS', () => {
  it('defines 5 standard bands', () => {
    expect(EEG_BAND_DEFS).toHaveLength(5);
  });

  it('covers delta through gamma', () => {
    const names = EEG_BAND_DEFS.map((b) => b.name);
    expect(names).toEqual(['delta', 'theta', 'alpha', 'beta', 'gamma']);
  });

  it('starts at 0.5 Hz and ends at 100 Hz', () => {
    expect(EEG_BAND_DEFS[0].low).toBe(0.5);
    expect(EEG_BAND_DEFS[EEG_BAND_DEFS.length - 1].high).toBe(100);
  });
});

describe('bandPower', () => {
  it('sums PSD values within frequency range', () => {
    // 1 Hz resolution, bins: 0Hz, 1Hz, 2Hz, ..., 9Hz
    const psd = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    // low=2, high=5 -> bins 2,3,4,5 -> 3+4+5+6 = 18
    expect(bandPower(psd, 1, 2, 5)).toBe(18);
  });

  it('clamps to array bounds', () => {
    const psd = [1, 2, 3];
    // Requesting bins beyond array length
    expect(bandPower(psd, 1, 0, 10)).toBe(6);
  });

  it('returns 0 for empty PSD', () => {
    expect(bandPower([], 1, 0, 10)).toBe(0);
  });

  it('handles fractional frequency bounds', () => {
    // 0.5 Hz resolution: bins at 0, 0.5, 1.0, 1.5, 2.0, ...
    const psd = [1, 2, 3, 4, 5, 6, 7, 8];
    // low=1, high=2 -> lowBin=floor(1/0.5)=2, highBin=ceil(2/0.5)=4
    // bins 2,3,4 -> 3+4+5 = 12
    expect(bandPower(psd, 0.5, 1, 2)).toBe(12);
  });

  it('handles single bin range', () => {
    const psd = [10, 20, 30, 40, 50];
    // low=2, high=2 -> lowBin=2, highBin=2 -> bin 2 only -> 30
    expect(bandPower(psd, 1, 2, 2)).toBe(30);
  });
});

describe('allBandPowers', () => {
  it('returns all 5 band names', () => {
    const psd = new Array(128).fill(1);
    const result = allBandPowers(psd, 1);
    expect(Object.keys(result)).toEqual(['delta', 'theta', 'alpha', 'beta', 'gamma']);
  });

  it('computes correct powers for uniform PSD', () => {
    // 1 Hz resolution, uniform PSD of 1.0
    const psd = new Array(128).fill(1);
    const result = allBandPowers(psd, 1);
    // delta: 0.5-4 Hz -> bins 0..4 = 5 bins
    expect(result.delta).toBe(5);
    // theta: 4-8 Hz -> bins 4..8 = 5 bins
    expect(result.theta).toBe(5);
    // alpha: 8-13 Hz -> bins 8..13 = 6 bins
    expect(result.alpha).toBe(6);
    // beta: 13-30 Hz -> bins 13..30 = 18 bins
    expect(result.beta).toBe(18);
    // gamma: 30-100 Hz -> bins 30..100 = 71 bins
    expect(result.gamma).toBe(71);
  });

  it('handles empty PSD', () => {
    const result = allBandPowers([], 1);
    for (const band of EEG_BAND_DEFS) {
      expect(result[band.name]).toBe(0);
    }
  });
});

describe('toDecibels', () => {
  it('converts positive values to dB', () => {
    const psd = [1, 10, 100];
    const db = toDecibels(psd);
    expect(db[0]).toBeCloseTo(0);
    expect(db[1]).toBeCloseTo(10);
    expect(db[2]).toBeCloseTo(20);
  });

  it('floors zero values', () => {
    const db = toDecibels([0]);
    expect(db[0]).toBe(-60);
  });

  it('floors negative values', () => {
    const db = toDecibels([-1]);
    expect(db[0]).toBe(-60);
  });

  it('uses custom floor', () => {
    const db = toDecibels([0], -100);
    expect(db[0]).toBe(-100);
  });

  it('clamps very small positive values to floor', () => {
    // 10*log10(1e-7) = -70, which is below default floor of -60
    const db = toDecibels([1e-7]);
    expect(db[0]).toBe(-60);
  });

  it('returns empty array for empty input', () => {
    expect(toDecibels([])).toEqual([]);
  });
});

describe('smooth', () => {
  it('returns copy with window size 1', () => {
    const data = [1, 2, 3];
    const result = smooth(data, 1);
    expect(result).toEqual([1, 2, 3]);
    // Should be a copy, not the same reference
    expect(result).not.toBe(data);
  });

  it('returns copy with window size 0', () => {
    const data = [1, 2, 3];
    expect(smooth(data, 0)).toEqual([1, 2, 3]);
  });

  it('smooths with window size 3', () => {
    const data = [0, 0, 10, 0, 0];
    const result = smooth(data, 3);
    // Center value: (0+10+0)/3 = 3.33
    expect(result[2]).toBeCloseTo(10 / 3);
    // Edge values use smaller windows
    expect(result[0]).toBeCloseTo(0); // (0+0)/2 = 0
    expect(result[1]).toBeCloseTo(10 / 3); // (0+0+10)/3
  });

  it('handles empty array', () => {
    expect(smooth([], 5)).toEqual([]);
  });

  it('handles single element', () => {
    expect(smooth([42], 5)).toEqual([42]);
  });

  it('smooths uniform data to same values', () => {
    const data = [5, 5, 5, 5, 5];
    const result = smooth(data, 3);
    for (const v of result) {
      expect(v).toBeCloseTo(5);
    }
  });
});
