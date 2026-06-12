/** Device connection status. */
export type ConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'error';

/** Band power values for standard EEG frequency bands. */
export interface BandPowers {
  delta: number;
  theta: number;
  alpha: number;
  beta: number;
  gamma: number;
}
