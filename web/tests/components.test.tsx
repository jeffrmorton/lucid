import { act, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { BandPower } from '../src/components/BandPower';
import { DeviceConnect } from '../src/components/DeviceConnect';
import { EEGTrace, drawTraces } from '../src/components/EEGTrace';
import {
  NeurofeedbackPanel,
  PROTOCOL_OPTIONS,
  type FeedbackState,
  type SRData,
} from '../src/components/NeurofeedbackPanel';
import {
  SessionManager,
  formatDuration,
  formatSize,
  type Session,
} from '../src/components/SessionManager';
import { Spectrogram, drawSpectrogram } from '../src/components/Spectrogram';
import { TopoMap, drawTopoMap, interpolateValue } from '../src/components/TopoMap';
import { channelColors } from '../src/lib/theme-colors';

function makeCtx(): CanvasRenderingContext2D {
  return {
    setTransform: vi.fn(),
    clearRect: vi.fn(),
    fillRect: vi.fn(),
    fillText: vi.fn(),
    beginPath: vi.fn(),
    moveTo: vi.fn(),
    lineTo: vi.fn(),
    stroke: vi.fn(),
    arc: vi.fn(),
    fill: vi.fn(),
    fillStyle: '',
    strokeStyle: '',
    lineWidth: 0,
    font: '',
    textAlign: '',
    textBaseline: '',
  } as unknown as CanvasRenderingContext2D;
}

/** Mock getContext so useCanvas invokes the component draw callbacks. */
function mockCanvas(): CanvasRenderingContext2D {
  const ctx = makeCtx();
  vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue(
    ctx as unknown as RenderingContext,
  );
  return ctx;
}

describe('BandPower', () => {
  it('renders abbreviated bands with no powers', () => {
    render(<BandPower />);
    expect(screen.getByTestId('band-power')).toBeInTheDocument();
    expect(screen.getByText('Del')).toBeInTheDocument();
    expect(screen.getByText('Gam')).toBeInTheDocument();
  });

  it('renders an em dash for null powers', () => {
    render(<BandPower powers={null} />);
    expect(screen.queryByText(/\d+\.\d{1}/)).not.toBeInTheDocument();
  });

  it('renders values when powers provided', () => {
    render(<BandPower powers={{ delta: 1.5, theta: 2.3, alpha: 3.1, beta: 0.8, gamma: 0.2 }} />);
    expect(screen.getByText('1.5')).toBeInTheDocument();
    expect(screen.getByText('0.2')).toBeInTheDocument();
  });
});

describe('DeviceConnect', () => {
  it('shows Connect + Disconnected chip when disconnected', () => {
    const onConnect = vi.fn();
    render(<DeviceConnect status="disconnected" onConnect={onConnect} onDisconnect={vi.fn()} />);
    expect(screen.getByText('Disconnected')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Connect' }));
    expect(onConnect).toHaveBeenCalled();
  });

  it('shows Disconnect + Connected chip when connected', () => {
    const onDisconnect = vi.fn();
    render(<DeviceConnect status="connected" onConnect={vi.fn()} onDisconnect={onDisconnect} />);
    expect(screen.getByText('Connected')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Disconnect' }));
    expect(onDisconnect).toHaveBeenCalled();
  });

  it('shows a Connecting chip and no button while connecting', () => {
    render(<DeviceConnect status="connecting" onConnect={vi.fn()} onDisconnect={vi.fn()} />);
    expect(screen.getByText('Connecting')).toBeInTheDocument();
    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });

  it('shows an Error chip + Connect (retry) on error', () => {
    render(<DeviceConnect status="error" onConnect={vi.fn()} onDisconnect={vi.fn()} />);
    expect(screen.getByText('Error')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Connect' })).toBeInTheDocument();
  });
});

describe('EEGTrace', () => {
  afterEach(() => vi.restoreAllMocks());

  it('renders the panel and a labelled canvas', () => {
    mockCanvas();
    render(<EEGTrace channels={8} sampleRate={250} />);
    expect(screen.getByTestId('eeg-trace')).toBeInTheDocument();
    const canvas = screen.getByTestId('eeg-canvas');
    expect(canvas).toHaveAttribute('role', 'img');
    expect(canvas.getAttribute('aria-label')).toContain('8-channel');
  });

  it('draws provided data (data-present branch)', () => {
    const ctx = mockCanvas();
    render(<EEGTrace channels={2} sampleRate={250} data={[[1, 2, 3], [3, 2, 1]]} />);
    expect(ctx.clearRect).toHaveBeenCalled();
  });

  it('shows channel/rate meta', () => {
    mockCanvas();
    render(<EEGTrace channels={4} sampleRate={500} displaySeconds={5} />);
    expect(screen.getByText('4ch · 500 SPS · 5s')).toBeInTheDocument();
  });
});

describe('drawTraces', () => {
  const colors = channelColors();

  it('draws a waiting state when all channels are empty', () => {
    const ctx = makeCtx();
    drawTraces(ctx, [[], []], 800, 480, 2, 10, colors);
    expect(ctx.fillText).toHaveBeenCalledWith('Waiting for data…', 400, 240);
  });

  it('draws a single channel with gridlines, baseline and label', () => {
    const ctx = makeCtx();
    drawTraces(ctx, [[-5, 0, 3, 10, -2, 7]], 800, 60, 1, 10, colors);
    expect(ctx.moveTo).toHaveBeenCalled();
    expect(ctx.lineTo).toHaveBeenCalled();
    expect(ctx.stroke).toHaveBeenCalled();
    expect(ctx.fillText).toHaveBeenCalledWith('Fz', 4, expect.any(Number));
  });

  it('skips empty channels and handles equal values', () => {
    const ctx = makeCtx();
    drawTraces(ctx, [[], [5, 5, 5]], 800, 120, 2, 10, colors);
    expect(ctx.stroke).toHaveBeenCalled();
  });

  it('uses a fallback label and cycles colors beyond the palette', () => {
    const ctx = makeCtx();
    const data = Array.from({ length: 9 }, () => [1, 2, 3]);
    drawTraces(ctx, data, 800, 540, 9, 10, colors);
    expect(ctx.fillText).toHaveBeenCalledWith('Ch9', 4, expect.any(Number));
  });
});

describe('Spectrogram', () => {
  afterEach(() => vi.restoreAllMocks());

  it('renders empty state meta + waiting aria', () => {
    mockCanvas();
    render(<Spectrogram data={[]} />);
    expect(screen.getByTestId('spectrogram')).toBeInTheDocument();
    expect(screen.getByText('0 × 0 bins')).toBeInTheDocument();
    expect(screen.getByTestId('spectrogram-canvas')).toHaveAttribute(
      'aria-label',
      'Spectrogram, waiting for data',
    );
  });

  it('renders meta + aria with data and respects maxRows', () => {
    mockCanvas();
    render(<Spectrogram data={Array.from({ length: 100 }, () => [1, 2, 3])} maxRows={10} />);
    expect(screen.getByText('10 × 3 bins')).toBeInTheDocument();
    expect(screen.getByTestId('spectrogram-canvas').getAttribute('aria-label')).toContain(
      '10 time steps by 3 frequency bins',
    );
  });
});

describe('drawSpectrogram', () => {
  it('draws a centered waiting message for empty data', () => {
    const ctx = makeCtx();
    drawSpectrogram(ctx, [], 400, 200);
    expect(ctx.fillText).toHaveBeenCalledWith('Waiting for data…', 200, 100);
  });

  it('draws cells, axis labels and a colorbar for data', () => {
    const ctx = makeCtx();
    drawSpectrogram(
      ctx,
      [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
      ],
      400,
      200,
    );
    expect(ctx.fillRect).toHaveBeenCalled();
    expect(ctx.fillText).toHaveBeenCalledWith('Hz', expect.any(Number), expect.any(Number));
  });

  it('handles a zero-column row (numCols fallback)', () => {
    const ctx = makeCtx();
    expect(() => drawSpectrogram(ctx, [[]], 400, 200)).not.toThrow();
  });
});

describe('TopoMap', () => {
  afterEach(() => vi.restoreAllMocks());

  it('renders a labelled canvas and draws empty state', () => {
    const ctx = mockCanvas();
    render(<TopoMap />);
    expect(screen.getByTestId('topo-map')).toBeInTheDocument();
    expect(screen.getByTestId('topo-canvas').getAttribute('aria-label')).toContain('Topographic');
    expect(ctx.clearRect).toHaveBeenCalled();
  });

  it('draws with channel values (data-present branch)', () => {
    const ctx = mockCanvas();
    render(<TopoMap channelValues={[1.2, 4.5]} channelNames={['Fz', 'Cz']} />);
    expect(ctx.fillRect).toHaveBeenCalled();
  });
});

describe('interpolateValue', () => {
  it('returns the exact value at an electrode', () => {
    expect(interpolateValue(0.5, 0.5, [[0.5, 0.5]], [7])).toBe(7);
  });

  it('returns a weighted average between electrodes', () => {
    const result = interpolateValue(
      0.5,
      0,
      [
        [0, 0],
        [1, 0],
      ],
      [0, 10],
    );
    expect(result).toBeCloseTo(5, 1);
  });

  it('returns 0 with no electrodes', () => {
    expect(interpolateValue(0.5, 0.5, [], [])).toBe(0);
  });
});

describe('drawTopoMap', () => {
  it('draws heatmap, electrodes and legend when populated', () => {
    const ctx = makeCtx();
    drawTopoMap(ctx, 200, 200, ['Fz', 'Cz', 'XX'], [1, 2, 3], false);
    expect(ctx.fillRect).toHaveBeenCalled();
    expect(ctx.arc).toHaveBeenCalled();
    expect(ctx.fillText).toHaveBeenCalled();
  });

  it('draws a No data message when empty', () => {
    const ctx = makeCtx();
    drawTopoMap(ctx, 200, 200, ['Fz'], [0], true);
    expect(ctx.fillText).toHaveBeenCalledWith('No data', expect.any(Number), expect.any(Number));
  });
});

describe('SessionManager helpers', () => {
  it('formats durations', () => {
    expect(formatDuration(75)).toBe('1:15');
    expect(formatDuration(5)).toBe('0:05');
  });

  it('formats sizes across magnitudes', () => {
    expect(formatSize()).toBe('—');
    expect(formatSize(512)).toBe('512 B');
    expect(formatSize(2048)).toBe('2.0 KB');
    expect(formatSize(5 * 1024 * 1024)).toBe('5.0 MB');
  });
});

describe('SessionManager', () => {
  it('renders the empty state and an Idle chip when not recording', () => {
    render(<SessionManager />);
    expect(screen.getByTestId('session-manager')).toBeInTheDocument();
    expect(screen.getByText('No recorded sessions')).toBeInTheDocument();
    expect(screen.getByText('Idle')).toBeInTheDocument();
    expect(screen.getByTestId('start-recording')).toBeInTheDocument();
  });

  it('starts recording', () => {
    const onStart = vi.fn();
    render(<SessionManager onStartRecording={onStart} />);
    fireEvent.click(screen.getByTestId('start-recording'));
    expect(onStart).toHaveBeenCalledOnce();
  });

  it('shows a Recording chip + stop button while recording', () => {
    const onStop = vi.fn();
    render(<SessionManager isRecording onStopRecording={onStop} />);
    expect(screen.getByTestId('status-chip')).toHaveTextContent('Recording');
    fireEvent.click(screen.getByTestId('stop-recording'));
    expect(onStop).toHaveBeenCalledOnce();
  });

  it('renders session rows with formatted duration and size', () => {
    const sessions: Session[] = [
      { id: '1', name: 'Session 1', date: '2026-03-26', duration: 305, size: 2048 },
      { id: '2', name: 'Session 2', date: '2026-03-25', duration: 60 },
    ];
    render(<SessionManager sessions={sessions} />);
    expect(screen.getByTestId('session-list')).toBeInTheDocument();
    expect(screen.getByText('Session 1')).toBeInTheDocument();
    expect(screen.getByText('5:05')).toBeInTheDocument();
    expect(screen.getByText('2.0 KB')).toBeInTheDocument();
    expect(screen.queryByText('No recorded sessions')).not.toBeInTheDocument();
  });
});

describe('NeurofeedbackPanel (presentation)', () => {
  it('renders defaults: protocol select, description, idle, no feedback', () => {
    render(<NeurofeedbackPanel />);
    expect(screen.getByTestId('neurofeedback-panel')).toBeInTheDocument();
    expect(screen.getByText('Protocol: None')).toBeInTheDocument();
    expect(screen.getByText('No feedback data yet.')).toBeInTheDocument();
    expect(screen.getByTestId('start-training')).toBeInTheDocument();
    expect(screen.getByText('Idle')).toBeInTheDocument();
    expect(screen.getByTestId('protocol-description')).toBeInTheDocument();
  });

  it('renders the protocol name and hides description for an unknown protocol', () => {
    render(<NeurofeedbackPanel protocolName="Alpha Up" selectedProtocol="mystery" />);
    expect(screen.getByText('Protocol: Alpha Up')).toBeInTheDocument();
    expect(screen.queryByTestId('protocol-description')).not.toBeInTheDocument();
  });

  it('toggles start/stop training buttons', () => {
    const { rerender } = render(<NeurofeedbackPanel isTraining={false} />);
    expect(screen.getByTestId('start-training')).toBeInTheDocument();
    rerender(<NeurofeedbackPanel isTraining={true} />);
    expect(screen.getByTestId('stop-training')).toBeInTheDocument();
  });

  it('calls external start/stop handlers', () => {
    const onStart = vi.fn();
    const onStop = vi.fn();
    const { rerender } = render(<NeurofeedbackPanel onStartTraining={onStart} />);
    fireEvent.click(screen.getByTestId('start-training'));
    expect(onStart).toHaveBeenCalledOnce();
    rerender(<NeurofeedbackPanel isTraining onStopTraining={onStop} />);
    fireEvent.click(screen.getByTestId('stop-training'));
    expect(onStop).toHaveBeenCalledOnce();
  });

  it('renders reward (success) and inhibit (warning) readouts', () => {
    const feedback: FeedbackState = {
      reward: true,
      inhibit: false,
      rewardValue: 0.85,
      inhibitValue: 0.12,
    };
    render(<NeurofeedbackPanel feedback={feedback} />);
    const reward = screen.getByTestId('reward-indicator');
    expect(reward).toHaveTextContent('0.85');
    expect(reward).toHaveAttribute('data-active', 'true');
    const inhibit = screen.getByTestId('inhibit-indicator');
    expect(inhibit).toHaveAttribute('data-active', 'false');
  });

  it('marks the inhibit readout active', () => {
    const feedback: FeedbackState = {
      reward: false,
      inhibit: true,
      rewardValue: 0.3,
      inhibitValue: 0.9,
    };
    render(<NeurofeedbackPanel feedback={feedback} />);
    expect(screen.getByTestId('inhibit-indicator')).toHaveAttribute('data-active', 'true');
  });

  it('changes protocol via the custom select', () => {
    const onChange = vi.fn();
    render(<NeurofeedbackPanel onProtocolChange={onChange} />);
    fireEvent.click(screen.getByTestId('select-trigger'));
    fireEvent.click(screen.getByTestId('select-option-sr_entrainment'));
    expect(onChange).toHaveBeenCalledWith('sr_entrainment');
  });

  it('disables the protocol select while training', () => {
    render(<NeurofeedbackPanel isTraining />);
    expect(screen.getByTestId('select-trigger')).toBeDisabled();
  });

  it('hides the SR card without SR data', () => {
    render(<NeurofeedbackPanel />);
    expect(screen.queryByTestId('sr-status-card')).not.toBeInTheDocument();
  });

  it('renders the SR card with frequency, band and marker', () => {
    const sr: SRData = { frequency: 7.796, stationId: 'simulator1' };
    render(<NeurofeedbackPanel srData={sr} />);
    expect(screen.getByTestId('sr-status-card')).toBeInTheDocument();
    expect(screen.getByTestId('sr-frequency')).toHaveTextContent('7.796');
    expect(screen.getByTestId('sr-status-dot')).toHaveTextContent('simulator1');
    expect(screen.getByTestId('sr-target-band')).toHaveTextContent('6.80');
    expect(screen.getByTestId('sr-marker').style.left).toMatch(/42\.\d+%/);
  });

  it('clamps the SR marker at the bar extremes', () => {
    const { rerender } = render(
      <NeurofeedbackPanel srData={{ frequency: 2, stationId: 's' }} />,
    );
    expect(screen.getByTestId('sr-marker').style.left).toBe('0%');
    rerender(<NeurofeedbackPanel srData={{ frequency: 15, stationId: 's' }} />);
    expect(screen.getByTestId('sr-marker').style.left).toBe('100%');
  });

  it('PROTOCOL_OPTIONS has 4 protocols incl. the EarthSync SR one', () => {
    expect(PROTOCOL_OPTIONS).toHaveLength(4);
    const sr = PROTOCOL_OPTIONS.find((p) => p.id === 'sr_entrainment');
    expect(sr?.hasEarthSync).toBe(true);
    for (const p of PROTOCOL_OPTIONS.filter((o) => o.id !== 'sr_entrainment')) {
      expect(p.hasEarthSync).toBe(false);
    }
  });
});

describe('NeurofeedbackPanel (WebSocket training)', () => {
  let instances: MockNFSocket[];

  class MockNFSocket {
    static OPEN = 1;
    readyState = 1;
    url: string;
    sent: string[] = [];
    onopen: (() => void) | null = null;
    onmessage: ((e: { data: string }) => void) | null = null;
    onclose: (() => void) | null = null;
    constructor(url: string) {
      this.url = url;
      instances.push(this);
    }
    send(d: string) {
      this.sent.push(d);
    }
    close = vi.fn(() => {
      this.onclose?.();
    });
  }

  beforeEach(() => {
    instances = [];
    vi.stubGlobal('WebSocket', MockNFSocket);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  function start() {
    render(
      <NeurofeedbackPanel
        onTrainingChange={vi.fn()}
        onFeedbackChange={vi.fn()}
        onSRDataChange={vi.fn()}
      />,
    );
    fireEvent.click(screen.getByTestId('start-training'));
    return instances[0];
  }

  it('opens the socket and sends the selected protocol on open', () => {
    const ws = start();
    expect(ws.url).toContain('/ws/neurofeedback');
    act(() => ws.onopen?.());
    expect(ws.sent[0]).toContain('smr_training');
  });

  it('handles a calibration message with EarthSync data', () => {
    const ws = start();
    act(() =>
      ws.onmessage?.({
        data: JSON.stringify({
          phase: 'calibration',
          earthsync: { sr_frequency: 7.83, station_id: 'sim1' },
        }),
      }),
    );
    expect(screen.getByTestId('training-phase')).toHaveTextContent('calibration');
    expect(screen.getByTestId('sr-frequency')).toHaveTextContent('7.830');
    expect(screen.getByText('Calibration')).toBeInTheDocument();
  });

  it('handles calibration with a frequency but no station id', () => {
    const ws = start();
    act(() =>
      ws.onmessage?.({
        data: JSON.stringify({ phase: 'calibration', earthsync: { sr_frequency: 7.9 } }),
      }),
    );
    expect(screen.getByTestId('sr-frequency')).toHaveTextContent('7.900');
    expect(screen.getByTestId('sr-status-dot')).toHaveTextContent('');
  });

  it('handles calibration with EarthSync object but no frequency', () => {
    const ws = start();
    act(() => ws.onmessage?.({ data: JSON.stringify({ phase: 'calibration', earthsync: {} }) }));
    expect(screen.getByTestId('training-phase')).toHaveTextContent('calibration');
    expect(screen.queryByTestId('sr-status-card')).not.toBeInTheDocument();
  });

  it('handles a bare calibration message (no earthsync) then training phase', () => {
    const ws = start();
    act(() => ws.onmessage?.({ data: JSON.stringify({ phase: 'calibration' }) }));
    act(() => ws.onmessage?.({ data: JSON.stringify({ phase: 'training' }) }));
    expect(screen.getByTestId('training-phase')).toHaveTextContent('training');
    expect(screen.getByTestId('status-chip')).toHaveTextContent('Training');
  });

  it('handles a feedback message with values and SR', () => {
    const ws = start();
    act(() =>
      ws.onmessage?.({
        data: JSON.stringify({
          status: 'feedback',
          reward: true,
          inhibit: false,
          reward_value: 0.7,
          inhibit_value: 0.2,
          sr: { frequency: 7.8, station_id: 'sim2' },
        }),
      }),
    );
    expect(screen.getByTestId('reward-indicator')).toHaveTextContent('0.70');
    expect(screen.getByTestId('sr-frequency')).toHaveTextContent('7.800');
  });

  it('defaults missing feedback values to zero and ignores absent SR', () => {
    const ws = start();
    act(() =>
      ws.onmessage?.({ data: JSON.stringify({ status: 'feedback', reward: false, inhibit: true }) }),
    );
    expect(screen.getByTestId('reward-indicator')).toHaveTextContent('0.00');
    expect(screen.queryByTestId('sr-status-card')).not.toBeInTheDocument();
  });

  it('ignores messages without a known phase or status', () => {
    const ws = start();
    act(() => ws.onmessage?.({ data: JSON.stringify({ hello: 'world' }) }));
    expect(screen.getByText('No feedback data yet.')).toBeInTheDocument();
  });

  it('resets on socket close', () => {
    const ws = start();
    act(() => ws.onmessage?.({ data: JSON.stringify({ phase: 'calibration' }) }));
    act(() => ws.onclose?.());
    expect(screen.getByTestId('start-training')).toBeInTheDocument();
    expect(screen.queryByTestId('training-phase')).not.toBeInTheDocument();
  });

  it('closes the socket on stop', () => {
    const ws = start();
    act(() => ws.onmessage?.({ data: JSON.stringify({ phase: 'calibration' }) }));
    fireEvent.click(screen.getByTestId('stop-training'));
    expect(ws.close).toHaveBeenCalled();
  });

  it('uses wss when the page is served over https', () => {
    const original = window.location;
    Object.defineProperty(window, 'location', {
      configurable: true,
      value: { protocol: 'https:', host: 'example.test' },
    });
    try {
      const ws = start();
      expect(ws.url.startsWith('wss://')).toBe(true);
    } finally {
      Object.defineProperty(window, 'location', { configurable: true, value: original });
    }
  });

  it('stop without an open socket is safe (external training flag)', () => {
    render(<NeurofeedbackPanel isTraining />);
    fireEvent.click(screen.getByTestId('stop-training'));
    expect(screen.getByTestId('neurofeedback-panel')).toBeInTheDocument();
  });
});
