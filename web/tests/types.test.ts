import { describe, it, expect } from 'vitest';
import { EEG_BANDS } from '../src/lib/types';
import { CHANNEL_NAMES, DEFAULT_SAMPLE_RATE, DEFAULT_CHANNELS } from '../src/lib/constants';

describe('types', () => {
  it('defines 5 EEG bands', () => {
    expect(EEG_BANDS).toHaveLength(5);
  });

  it('bands cover 0.5-100 Hz', () => {
    expect(EEG_BANDS[0].low).toBe(0.5);
    expect(EEG_BANDS[EEG_BANDS.length - 1].high).toBe(100);
  });

  it('bands have colors', () => {
    for (const band of EEG_BANDS) {
      expect(band.color).toMatch(/^#[0-9a-f]{6}$/);
    }
  });
});

describe('constants', () => {
  it('has correct defaults', () => {
    expect(DEFAULT_SAMPLE_RATE).toBe(250);
    expect(DEFAULT_CHANNELS).toBe(8);
  });

  it('has 8 channel names', () => {
    expect(CHANNEL_NAMES).toHaveLength(8);
  });
});
