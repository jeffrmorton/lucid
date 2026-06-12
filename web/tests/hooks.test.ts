import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useEEGStream } from '../src/hooks/useEEGStream';

/** Minimal mock WebSocket that captures event handlers. */
class MockWebSocket {
  static readonly OPEN = 1;
  readonly OPEN = 1;

  onopen: (() => void) | null = null;
  onerror: (() => void) | null = null;
  onclose: (() => void) | null = null;
  onmessage: ((event: { data: string }) => void) | null = null;
  readyState = 0;
  close = vi.fn();
  send = vi.fn();

  constructor(_url: string) {}
}

beforeEach(() => {
  vi.stubGlobal('WebSocket', MockWebSocket);
});

describe('useEEGStream', () => {
  it('starts with disconnected status', () => {
    const { result } = renderHook(() => useEEGStream());
    expect(result.current.status).toBe('disconnected');
    expect(result.current.latestData.bandPowers).toBeNull();
    expect(result.current.latestData.psdShape).toEqual([]);
    expect(result.current.latestData.nSamples).toBe(0);
  });

  it('sets connecting then connected on successful connect', () => {
    const { result } = renderHook(() => useEEGStream());

    act(() => {
      result.current.connect();
    });
    expect(result.current.status).toBe('connecting');
  });

  it('sets connected on WebSocket open', () => {
    let wsInstance: MockWebSocket | null = null;
    vi.stubGlobal(
      'WebSocket',
      class extends MockWebSocket {
        constructor(url: string) {
          super(url);
          wsInstance = this;
        }
      },
    );

    const { result } = renderHook(() => useEEGStream());

    act(() => {
      result.current.connect();
    });

    act(() => {
      wsInstance?.onopen?.();
    });
    expect(result.current.status).toBe('connected');
  });

  it('sets error on WebSocket error', () => {
    let wsInstance: MockWebSocket | null = null;
    vi.stubGlobal(
      'WebSocket',
      class extends MockWebSocket {
        constructor(url: string) {
          super(url);
          wsInstance = this;
        }
      },
    );

    const { result } = renderHook(() => useEEGStream());

    act(() => {
      result.current.connect();
    });

    act(() => {
      wsInstance?.onerror?.();
    });
    expect(result.current.status).toBe('error');
  });

  it('sets disconnected on WebSocket close and nulls ref', () => {
    let wsInstance: MockWebSocket | null = null;
    vi.stubGlobal(
      'WebSocket',
      class extends MockWebSocket {
        constructor(url: string) {
          super(url);
          wsInstance = this;
        }
      },
    );

    const { result } = renderHook(() => useEEGStream());

    act(() => {
      result.current.connect();
    });

    act(() => {
      wsInstance?.onopen?.();
    });
    expect(result.current.status).toBe('connected');

    act(() => {
      wsInstance?.onclose?.();
    });
    expect(result.current.status).toBe('disconnected');
  });

  it('sets disconnected on disconnect call and closes WebSocket', () => {
    let wsInstance: MockWebSocket | null = null;
    vi.stubGlobal(
      'WebSocket',
      class extends MockWebSocket {
        constructor(url: string) {
          super(url);
          wsInstance = this;
        }
      },
    );

    const { result } = renderHook(() => useEEGStream());

    act(() => {
      result.current.connect();
    });

    act(() => {
      wsInstance?.onopen?.();
    });
    expect(result.current.status).toBe('connected');

    act(() => {
      result.current.disconnect();
    });
    expect(result.current.status).toBe('disconnected');
    expect(wsInstance?.close).toHaveBeenCalled();
  });

  it('disconnect is safe when no WebSocket exists', () => {
    const { result } = renderHook(() => useEEGStream());

    act(() => {
      result.current.disconnect();
    });
    expect(result.current.status).toBe('disconnected');
  });

  it('updates latestData on valid processed message', () => {
    let wsInstance: MockWebSocket | null = null;
    vi.stubGlobal(
      'WebSocket',
      class extends MockWebSocket {
        constructor(url: string) {
          super(url);
          wsInstance = this;
        }
      },
    );

    const { result } = renderHook(() => useEEGStream());

    act(() => {
      result.current.connect();
    });

    act(() => {
      wsInstance?.onopen?.();
    });

    act(() => {
      wsInstance?.onmessage?.({
        data: JSON.stringify({
          status: 'processed',
          band_powers: {
            delta: [1.5],
            theta: [2.3],
            alpha: [3.1],
            beta: [0.8],
            gamma: [0.2],
          },
          psd_shape: [128, 5],
          n_samples: 250,
        }),
      });
    });

    expect(result.current.latestData.bandPowers).toEqual({
      delta: 1.5,
      theta: 2.3,
      alpha: 3.1,
      beta: 0.8,
      gamma: 0.2,
    });
    expect(result.current.latestData.psdShape).toEqual([128, 5]);
    expect(result.current.latestData.nSamples).toBe(250);
  });

  it('handles message with missing optional fields', () => {
    let wsInstance: MockWebSocket | null = null;
    vi.stubGlobal(
      'WebSocket',
      class extends MockWebSocket {
        constructor(url: string) {
          super(url);
          wsInstance = this;
        }
      },
    );

    const { result } = renderHook(() => useEEGStream());

    act(() => {
      result.current.connect();
    });

    act(() => {
      wsInstance?.onmessage?.({
        data: JSON.stringify({
          status: 'processed',
          band_powers: {
            delta: [],
            theta: [],
            alpha: [],
            beta: [],
            gamma: [],
          },
        }),
      });
    });

    expect(result.current.latestData.bandPowers).toEqual({
      delta: 0,
      theta: 0,
      alpha: 0,
      beta: 0,
      gamma: 0,
    });
    expect(result.current.latestData.psdShape).toEqual([]);
    expect(result.current.latestData.nSamples).toBe(0);
  });

  it('ignores non-processed messages', () => {
    let wsInstance: MockWebSocket | null = null;
    vi.stubGlobal(
      'WebSocket',
      class extends MockWebSocket {
        constructor(url: string) {
          super(url);
          wsInstance = this;
        }
      },
    );

    const { result } = renderHook(() => useEEGStream());

    act(() => {
      result.current.connect();
    });

    act(() => {
      wsInstance?.onmessage?.({
        data: JSON.stringify({ status: 'connected', message: 'hello' }),
      });
    });

    expect(result.current.latestData.bandPowers).toBeNull();
  });

  it('ignores invalid JSON messages', () => {
    let wsInstance: MockWebSocket | null = null;
    vi.stubGlobal(
      'WebSocket',
      class extends MockWebSocket {
        constructor(url: string) {
          super(url);
          wsInstance = this;
        }
      },
    );

    const { result } = renderHook(() => useEEGStream());

    act(() => {
      result.current.connect();
    });

    act(() => {
      wsInstance?.onmessage?.({ data: 'not json{{{' });
    });

    expect(result.current.latestData.bandPowers).toBeNull();
  });

  it('sendData sends when WebSocket is open', () => {
    let wsInstance: MockWebSocket | null = null;
    vi.stubGlobal(
      'WebSocket',
      class extends MockWebSocket {
        constructor(url: string) {
          super(url);
          wsInstance = this;
        }
      },
    );

    const { result } = renderHook(() => useEEGStream());

    act(() => {
      result.current.connect();
    });

    // Simulate open state
    if (wsInstance) {
      (wsInstance as MockWebSocket).readyState = 1;
    }

    const buffer = new ArrayBuffer(8);
    act(() => {
      result.current.sendData(buffer);
    });

    expect(wsInstance?.send).toHaveBeenCalledWith(buffer);
  });

  it('sendData does nothing when WebSocket is not open', () => {
    let wsInstance: MockWebSocket | null = null;
    vi.stubGlobal(
      'WebSocket',
      class extends MockWebSocket {
        constructor(url: string) {
          super(url);
          wsInstance = this;
        }
      },
    );

    const { result } = renderHook(() => useEEGStream());

    act(() => {
      result.current.connect();
    });

    // readyState is 0 (CONNECTING), not OPEN
    const buffer = new ArrayBuffer(8);
    act(() => {
      result.current.sendData(buffer);
    });

    expect(wsInstance?.send).not.toHaveBeenCalled();
  });

  it('sendData does nothing when no WebSocket exists', () => {
    const { result } = renderHook(() => useEEGStream());

    const buffer = new ArrayBuffer(8);
    act(() => {
      result.current.sendData(buffer);
    });
    // Should not throw
  });

  it('defaults channel alpha to an empty array when absent', () => {
    let wsInstance: MockWebSocket | null = null;
    vi.stubGlobal(
      'WebSocket',
      class extends MockWebSocket {
        constructor(url: string) {
          super(url);
          wsInstance = this;
        }
      },
    );
    const { result } = renderHook(() => useEEGStream());
    act(() => result.current.connect());
    act(() => {
      wsInstance?.onmessage?.({
        data: JSON.stringify({
          status: 'processed',
          band_powers: { delta: [1], theta: [1], beta: [1], gamma: [1] },
        }),
      });
    });
    expect(result.current.latestData.channelAlpha).toEqual([]);
    expect(result.current.latestData.bandPowers?.alpha).toBe(0);
  });

  it('builds a dB spectrogram row from freqs/psd trimmed at 55 Hz', () => {
    let wsInstance: MockWebSocket | null = null;
    vi.stubGlobal(
      'WebSocket',
      class extends MockWebSocket {
        constructor(url: string) {
          super(url);
          wsInstance = this;
        }
      },
    );
    const { result } = renderHook(() => useEEGStream());
    act(() => result.current.connect());
    act(() => {
      wsInstance?.onmessage?.({
        data: JSON.stringify({
          status: 'processed',
          band_powers: { delta: [1], theta: [1], alpha: [1], beta: [1], gamma: [1] },
          freqs: [0, 10, 50, 56, 60],
          psd: [1, 10, 0, 5, 100],
        }),
      });
    });
    // Trimmed to f <= 55 (first 3 bins); 10*log10 with a -60 floor for non-positive.
    expect(result.current.latestData.spectrogramRows[0]).toEqual([0, 10, -60]);
  });

  it('keeps the full psd when no frequency exceeds 55 Hz', () => {
    let wsInstance: MockWebSocket | null = null;
    vi.stubGlobal(
      'WebSocket',
      class extends MockWebSocket {
        constructor(url: string) {
          super(url);
          wsInstance = this;
        }
      },
    );
    const { result } = renderHook(() => useEEGStream());
    act(() => result.current.connect());
    act(() => {
      wsInstance?.onmessage?.({
        data: JSON.stringify({
          status: 'processed',
          band_powers: { delta: [1], theta: [1], alpha: [1], beta: [1], gamma: [1] },
          freqs: [0, 10, 20],
          psd: [1, 10, 100],
        }),
      });
    });
    expect(result.current.latestData.spectrogramRows[0]).toEqual([0, 10, 20]);
  });

  it('caps the spectrogram history at 60 rows', () => {
    let wsInstance: MockWebSocket | null = null;
    vi.stubGlobal(
      'WebSocket',
      class extends MockWebSocket {
        constructor(url: string) {
          super(url);
          wsInstance = this;
        }
      },
    );
    const { result } = renderHook(() => useEEGStream());
    act(() => result.current.connect());
    act(() => {
      for (let i = 0; i < 61; i++) {
        wsInstance?.onmessage?.({
          data: JSON.stringify({
            status: 'processed',
            band_powers: { delta: [i], theta: [0], alpha: [0], beta: [0], gamma: [0] },
          }),
        });
      }
    });
    expect(result.current.latestData.spectrogramRows).toHaveLength(60);
  });
});
