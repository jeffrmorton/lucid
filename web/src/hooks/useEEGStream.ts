/** Hook for managing WebSocket EEG data stream. */

import { useCallback, useRef, useState } from 'react';
import { DEFAULT_CHANNELS, SERVER_WS_URL } from '../lib/constants';
import type { BandPowers, ConnectionStatus } from '../lib/types';

export interface EEGStreamData {
  bandPowers: BandPowers | null;
  /** Per-channel band powers for topo map (channel 0 values for each band) */
  channelAlpha: number[];
  /** Rolling spectrogram rows (each row = band powers over time) */
  spectrogramRows: number[][];
  psdShape: number[];
  nSamples: number;
  epochCount: number;
}

const MAX_SPECTROGRAM_ROWS = 60;

export function useEEGStream() {
  const [status, setStatus] = useState<ConnectionStatus>('disconnected');
  const [latestData, setLatestData] = useState<EEGStreamData>({
    bandPowers: null,
    channelAlpha: [],
    spectrogramRows: [],
    psdShape: [],
    nSamples: 0,
    epochCount: 0,
  });
  const wsRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    setStatus('connecting');
    const ws = new WebSocket(SERVER_WS_URL);
    wsRef.current = ws;

    ws.onopen = () => setStatus('connected');
    ws.onerror = () => setStatus('error');
    ws.onclose = () => {
      setStatus('disconnected');
      wsRef.current = null;
    };
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.status === 'processed' && data.band_powers) {
          const bp = data.band_powers;

          // Extract per-channel alpha for topo map
          const channelAlpha: number[] = bp.alpha ?? [];

          // Use the real channel-averaged PSD for spectrogram (frequency-resolved)
          // Trim to 0-55 Hz and convert to dB for better visualization
          const freqs: number[] = data.freqs ?? [];
          const rawPsd: number[] = data.psd ?? [];
          let row: number[];
          if (rawPsd.length > 0 && freqs.length > 0) {
            // Find bin index for 55 Hz cutoff
            const maxBin = freqs.findIndex((f: number) => f > 55);
            const trimmed = maxBin > 0 ? rawPsd.slice(0, maxBin) : rawPsd;
            // Convert to dB scale for better dynamic range
            row = trimmed.map((v: number) => (v > 0 ? 10 * Math.log10(v) : -60));
          } else {
            row = [
              bp.delta?.[0] ?? 0,
              bp.theta?.[0] ?? 0,
              bp.alpha?.[0] ?? 0,
              bp.beta?.[0] ?? 0,
              bp.gamma?.[0] ?? 0,
            ];
          }

          setLatestData((prev) => {
            const newRows = [...prev.spectrogramRows, row];
            if (newRows.length > MAX_SPECTROGRAM_ROWS) {
              newRows.shift();
            }
            return {
              bandPowers: {
                delta: bp.delta?.[0] ?? 0,
                theta: bp.theta?.[0] ?? 0,
                alpha: bp.alpha?.[0] ?? 0,
                beta: bp.beta?.[0] ?? 0,
                gamma: bp.gamma?.[0] ?? 0,
              },
              channelAlpha,
              spectrogramRows: newRows,
              psdShape: data.psd_shape ?? [],
              nSamples: data.n_samples ?? 0,
              epochCount: prev.epochCount + 1,
            };
          });
        }
      } catch {
        // Ignore parse errors
      }
    };
  }, []);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setStatus('disconnected');
  }, []);

  const sendData = useCallback((data: ArrayBuffer) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(data);
    }
  }, []);

  return { status, connect, disconnect, sendData, latestData };
}
