import { describe, expect, it } from 'vitest';
import { CHANNEL_NAMES, DEFAULT_CHANNELS, DEFAULT_SAMPLE_RATE } from '../src/lib/constants';

describe('constants', () => {
  it('has correct defaults', () => {
    expect(DEFAULT_SAMPLE_RATE).toBe(250);
    expect(DEFAULT_CHANNELS).toBe(8);
  });

  it('has 8 channel names', () => {
    expect(CHANNEL_NAMES).toHaveLength(8);
  });
});
