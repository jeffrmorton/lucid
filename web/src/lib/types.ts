/** Device connection status. */
export type ConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'error';

/** EEG sample from a single time point across all channels. */
export interface EEGSample {
  timestamp: number;
  channels: number[];
}

/** Band power values for standard EEG frequency bands. */
export interface BandPowers {
  delta: number;
  theta: number;
  alpha: number;
  beta: number;
  gamma: number;
}

/** EEG frequency band definition. */
export interface FrequencyBand {
  name: string;
  low: number;
  high: number;
  color: string;
}

/** Standard EEG frequency bands. */
export const EEG_BANDS: FrequencyBand[] = [
  { name: 'Delta', low: 0.5, high: 4, color: '#6366f1' },
  { name: 'Theta', low: 4, high: 8, color: '#8b5cf6' },
  { name: 'Alpha', low: 8, high: 13, color: '#06b6d4' },
  { name: 'Beta', low: 13, high: 30, color: '#22c55e' },
  { name: 'Gamma', low: 30, high: 100, color: '#f59e0b' },
];
