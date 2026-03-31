import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { BandPower } from '../src/components/BandPower';
import { DeviceConnect } from '../src/components/DeviceConnect';
import { EEGTrace, drawTraces } from '../src/components/EEGTrace';
import { NeurofeedbackPanel, PROTOCOL_OPTIONS } from '../src/components/NeurofeedbackPanel';
import type { FeedbackState, SRData } from '../src/components/NeurofeedbackPanel';
import { SessionManager } from '../src/components/SessionManager';
import { Spectrogram } from '../src/components/Spectrogram';
import { TopoMap, interpolateValue, valueToColor, drawTopoMap } from '../src/components/TopoMap';

describe('DeviceConnect', () => {
  it('renders connect button when disconnected', () => {
    render(<DeviceConnect status="disconnected" onConnect={() => {}} onDisconnect={() => {}} />);
    expect(screen.getByText('Connect')).toBeInTheDocument();
  });

  it('calls onStatusChange with connecting when connect clicked', () => {
    vi.useFakeTimers();
    const onConnect = vi.fn();
    const onDisconnect = vi.fn();
    render(
      <DeviceConnect status="disconnected" onConnect={onConnect} onDisconnect={onDisconnect} />,
    );
    fireEvent.click(screen.getByText('Connect'));
    expect(onConnect).toHaveBeenCalled();

    vi.useRealTimers();
  });

  it('shows disconnect button when connected', () => {
    render(<DeviceConnect status="connected" onConnect={() => {}} onDisconnect={() => {}} />);
    expect(screen.getByText('Disconnect')).toBeInTheDocument();
  });

  it('calls onStatusChange with disconnected when disconnect clicked', () => {
    const onConnect = vi.fn();
    const onDisconnect = vi.fn();
    render(
      <DeviceConnect status="connected" onConnect={onConnect} onDisconnect={onDisconnect} />,
    );
    fireEvent.click(screen.getByText('Disconnect'));
    expect(onDisconnect).toHaveBeenCalled();
  });

  it('shows connecting state', () => {
    render(<DeviceConnect status="connecting" onConnect={() => {}} onDisconnect={() => {}} />);
    expect(screen.getByText('Connecting...')).toBeInTheDocument();
  });

  it('shows connect button on error status', () => {
    render(<DeviceConnect status="error" onConnect={() => {}} onDisconnect={() => {}} />);
    expect(screen.getByText('Connect')).toBeInTheDocument();
  });
});

describe('BandPower', () => {
  it('renders without powers', () => {
    render(<BandPower />);
    expect(screen.getByTestId('band-power')).toBeInTheDocument();
    expect(screen.getByText('Del')).toBeInTheDocument();
    expect(screen.getByText('Gam')).toBeInTheDocument();
  });

  it('renders with null powers', () => {
    render(<BandPower powers={null} />);
    expect(screen.getByTestId('band-power')).toBeInTheDocument();
    expect(screen.queryByText(/\d+\.\d{1}/)).not.toBeInTheDocument();
  });

  it('renders band power values when powers provided', () => {
    const powers = { delta: 1.5, theta: 2.3, alpha: 3.1, beta: 0.8, gamma: 0.2 };
    render(<BandPower powers={powers} />);
    expect(screen.getByText('1.5')).toBeInTheDocument();
    expect(screen.getByText('2.3')).toBeInTheDocument();
    expect(screen.getByText('3.1')).toBeInTheDocument();
    expect(screen.getByText('0.8')).toBeInTheDocument();
    expect(screen.getByText('0.2')).toBeInTheDocument();
  });

  it('renders all 5 frequency bands (abbreviated)', () => {
    render(<BandPower />);
    expect(screen.getByText('Del')).toBeInTheDocument();
    expect(screen.getByText('The')).toBeInTheDocument();
    expect(screen.getByText('Alp')).toBeInTheDocument();
    expect(screen.getByText('Bet')).toBeInTheDocument();
    expect(screen.getByText('Gam')).toBeInTheDocument();
  });
});

describe('Spectrogram', () => {
  it('renders with empty data', () => {
    render(<Spectrogram data={[]} />);
    expect(screen.getByTestId('spectrogram')).toBeInTheDocument();
    expect(screen.getByText(/0 time steps/)).toBeInTheDocument();
  });

  it('renders with data', () => {
    const data = [
      [1, 2, 3, 4],
      [5, 6, 7, 8],
      [9, 10, 11, 12],
    ];
    render(<Spectrogram data={data} />);
    expect(screen.getByText(/3 time steps/)).toBeInTheDocument();
    expect(screen.getByText(/4 bins/)).toBeInTheDocument();
  });

  it('limits to maxRows', () => {
    const data = Array.from({ length: 100 }, () => [1, 2, 3]);
    render(<Spectrogram data={data} maxRows={10} />);
    expect(screen.getByText(/10 time steps/)).toBeInTheDocument();
  });

  it('renders with custom dimensions', () => {
    render(<Spectrogram data={[]} width={400} height={100} />);
    const canvas = screen.getByTestId('spectrogram-canvas');
    expect(canvas).toBeInTheDocument();
  });

  it('renders canvas placeholder', () => {
    render(<Spectrogram data={[]} />);
    expect(screen.getByTestId('spectrogram-canvas')).toBeInTheDocument();
  });
});

describe('TopoMap', () => {
  const mockCtx = {
    clearRect: vi.fn(),
    beginPath: vi.fn(),
    moveTo: vi.fn(),
    lineTo: vi.fn(),
    stroke: vi.fn(),
    fill: vi.fn(),
    arc: vi.fn(),
    fillText: vi.fn(),
    fillRect: vi.fn(),
    fillStyle: '',
    strokeStyle: '',
    lineWidth: 0,
    font: '',
  };

  beforeEach(() => {
    vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue(
      mockCtx as unknown as CanvasRenderingContext2D,
    );
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders canvas element with correct data-testid', () => {
    render(<TopoMap />);
    expect(screen.getByTestId('topo-map')).toBeInTheDocument();
    expect(screen.getByTestId('topo-canvas')).toBeInTheDocument();
  });

  it('canvas has correct width/height from size prop', () => {
    render(<TopoMap size={300} />);
    const canvas = screen.getByTestId('topo-canvas') as HTMLCanvasElement;
    expect(canvas.width).toBe(300);
    expect(canvas.height).toBe(300);
  });

  it('renders with default props', () => {
    render(<TopoMap />);
    const canvas = screen.getByTestId('topo-canvas') as HTMLCanvasElement;
    expect(canvas.width).toBe(200);
    expect(canvas.height).toBe(200);
  });

  it('renders with custom channelValues and calls drawTopoMap', () => {
    render(<TopoMap channelValues={[1.23, 4.56]} channelNames={['Fz', 'Cz']} />);
    expect(screen.getByTestId('topo-canvas')).toBeInTheDocument();
    expect(mockCtx.clearRect).toHaveBeenCalled();
  });
});

describe('interpolateValue', () => {
  it('returns exact value at electrode position', () => {
    const positions: [number, number][] = [[0.5, 0.5]];
    const values = [7.0];
    const result = interpolateValue(0.5, 0.5, positions, values);
    expect(result).toBe(7.0);
  });

  it('returns weighted average between electrodes', () => {
    const positions: [number, number][] = [
      [0.0, 0.0],
      [1.0, 0.0],
    ];
    const values = [0.0, 10.0];
    // At midpoint (0.5, 0.0), equidistant from both, should be ~5.0
    const result = interpolateValue(0.5, 0.0, positions, values);
    expect(result).toBeCloseTo(5.0, 1);
  });
});

describe('valueToColor', () => {
  it('returns blue-ish for low values', () => {
    const color = valueToColor(0, 0, 1);
    // At t=0: r=0, g=0, b=255
    expect(color).toMatch(/rgb\(0,0,255\)/);
  });

  it('returns red-ish for high values', () => {
    const color = valueToColor(1, 0, 1);
    // At t=1: r=255, g=0, b=0
    expect(color).toMatch(/rgb\(255,0,0\)/);
  });
});

describe('drawTopoMap', () => {
  function makeMockCtx(): CanvasRenderingContext2D {
    return {
      clearRect: vi.fn(),
      beginPath: vi.fn(),
      moveTo: vi.fn(),
      lineTo: vi.fn(),
      stroke: vi.fn(),
      fill: vi.fn(),
      arc: vi.fn(),
      fillText: vi.fn(),
      fillRect: vi.fn(),
      fillStyle: '',
      strokeStyle: '',
      lineWidth: 0,
      font: '',
    } as unknown as CanvasRenderingContext2D;
  }

  it('draws interpolated heatmap and electrodes', () => {
    const ctx = makeMockCtx();
    drawTopoMap(ctx, 200, ['Fz', 'Cz', 'Oz'], [1.0, 2.0, 3.0]);
    // Should have called fillRect for heatmap pixels
    expect(ctx.fillRect).toHaveBeenCalled();
    // Should have drawn electrode markers (arc + fill + fillText per electrode)
    expect(ctx.arc).toHaveBeenCalled();
    expect(ctx.fillText).toHaveBeenCalled();
    // Should have drawn head outline and nose
    expect(ctx.stroke).toHaveBeenCalled();
  });

  it('handles unknown channel name gracefully', () => {
    const ctx = makeMockCtx();
    expect(() => drawTopoMap(ctx, 100, ['XX'], [1.0])).not.toThrow();
  });
});

describe('valueToColor extended', () => {
  it('returns cyan-ish for t=0.25', () => {
    const color = valueToColor(0.25, 0, 1);
    // t=0.25: r=0, g=255, b=255
    expect(color).toMatch(/rgb\(0,255,255\)/);
  });

  it('returns green for t=0.5', () => {
    const color = valueToColor(0.5, 0, 1);
    // t=0.5: r=0, g=255, b=0
    expect(color).toMatch(/rgb\(0,255,0\)/);
  });

  it('returns yellow for t=0.75', () => {
    const color = valueToColor(0.75, 0, 1);
    // t=0.75: r=255, g=255, b=0
    expect(color).toMatch(/rgb\(255,255,0\)/);
  });

  it('clamps values below min', () => {
    const color = valueToColor(-5, 0, 1);
    expect(color).toMatch(/rgb\(0,0,255\)/);
  });

  it('clamps values above max', () => {
    const color = valueToColor(5, 0, 1);
    expect(color).toMatch(/rgb\(255,0,0\)/);
  });

  it('handles equal min and max', () => {
    const color = valueToColor(5, 5, 5);
    // range=0, falls through to range=1, t clamped
    expect(color).toBeDefined();
  });
});

describe('interpolateValue extended', () => {
  it('returns 0 when no positions', () => {
    const result = interpolateValue(0.5, 0.5, [], []);
    expect(result).toBe(0);
  });

  it('weights closer electrode more heavily', () => {
    const positions: [number, number][] = [
      [0.0, 0.0],
      [1.0, 0.0],
    ];
    const values = [0.0, 10.0];
    // Close to second electrode
    const result = interpolateValue(0.9, 0.0, positions, values);
    expect(result).toBeGreaterThan(5.0);
  });
});

describe('EEGTrace', () => {
  const mockCtx = {
    clearRect: vi.fn(),
    beginPath: vi.fn(),
    moveTo: vi.fn(),
    lineTo: vi.fn(),
    stroke: vi.fn(),
    fillText: vi.fn(),
    fillStyle: '',
    strokeStyle: '',
    lineWidth: 0,
    font: '',
  };

  beforeEach(() => {
    vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue(
      mockCtx as unknown as CanvasRenderingContext2D,
    );
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders canvas element', () => {
    render(<EEGTrace channels={8} sampleRate={250} />);
    expect(screen.getByTestId('eeg-trace')).toBeInTheDocument();
    expect(screen.getByTestId('eeg-canvas')).toBeInTheDocument();
  });

  it('renders with provided data and calls drawTraces', () => {
    const data = [
      [1, 2, 3, 4, 5],
      [5, 4, 3, 2, 1],
    ];
    render(<EEGTrace channels={2} sampleRate={250} data={data} />);
    expect(screen.getByTestId('eeg-canvas')).toBeInTheDocument();
    expect(mockCtx.clearRect).toHaveBeenCalled();
  });

  it('renders without data (uses empty fallback)', () => {
    render(<EEGTrace channels={2} sampleRate={250} />);
    expect(screen.getByTestId('eeg-canvas')).toBeInTheDocument();
    expect(mockCtx.clearRect).toHaveBeenCalled();
  });

  it('displays channel and sample rate info', () => {
    render(<EEGTrace channels={4} sampleRate={500} displaySeconds={5} />);
    expect(screen.getByText(/4ch/)).toBeInTheDocument();
    expect(screen.getByText(/500 SPS/)).toBeInTheDocument();
    expect(screen.getByText(/5s/)).toBeInTheDocument();
  });
});

describe('drawTraces', () => {
  function makeMockCtx(): CanvasRenderingContext2D {
    return {
      clearRect: vi.fn(),
      beginPath: vi.fn(),
      moveTo: vi.fn(),
      lineTo: vi.fn(),
      stroke: vi.fn(),
      fillText: vi.fn(),
      fillStyle: '',
      strokeStyle: '',
      lineWidth: 0,
      font: '',
    } as unknown as CanvasRenderingContext2D;
  }

  it('does not crash with empty data', () => {
    const ctx = makeMockCtx();
    expect(() => drawTraces(ctx, [], 800, 480, 8, 60)).not.toThrow();
    expect(ctx.clearRect).toHaveBeenCalledWith(0, 0, 800, 480);
  });

  it('draws single channel with varying data', () => {
    const ctx = makeMockCtx();
    const data = [[-5, 0, 3, 10, -2, 7]];
    drawTraces(ctx, data, 800, 60, 1, 60);
    // Should call moveTo for first point, lineTo for rest
    expect(ctx.moveTo).toHaveBeenCalled();
    expect(ctx.lineTo).toHaveBeenCalled();
    expect(ctx.stroke).toHaveBeenCalled();
    expect(ctx.fillText).toHaveBeenCalled();
  });

  it('draws multiple channels', () => {
    const ctx = makeMockCtx();
    const data = [
      [1, 2, 3],
      [4, 5, 6],
    ];
    drawTraces(ctx, data, 800, 120, 2, 60);
    expect(ctx.beginPath).toHaveBeenCalled();
  });

  it('handles channel with single sample', () => {
    const ctx = makeMockCtx();
    const data = [[42]];
    drawTraces(ctx, data, 800, 60, 1, 60);
    expect(ctx.moveTo).toHaveBeenCalled();
  });

  it('handles channel with all equal values', () => {
    const ctx = makeMockCtx();
    const data = [[5, 5, 5, 5]];
    drawTraces(ctx, data, 800, 60, 1, 60);
    // range = 0, falls back to range = 1
    expect(ctx.stroke).toHaveBeenCalled();
  });

  it('skips empty channel data', () => {
    const ctx = makeMockCtx();
    const data: number[][] = [[], [1, 2, 3]];
    drawTraces(ctx, data, 800, 120, 2, 60);
    // First channel is empty (skipped), second drawn
    expect(ctx.stroke).toHaveBeenCalled();
  });

  it('uses fallback label for channels beyond CHANNEL_NAMES', () => {
    const ctx = makeMockCtx();
    // Create 9 channels to exceed the 8 named channels
    const data = Array.from({ length: 9 }, () => [1, 2, 3]);
    drawTraces(ctx, data, 800, 540, 9, 60);
    // The 9th channel should use "Ch9" fallback label
    expect(ctx.fillText).toHaveBeenCalled();
  });
});

describe('NeurofeedbackPanel', () => {
  it('renders with defaults', () => {
    render(<NeurofeedbackPanel />);
    expect(screen.getByTestId('neurofeedback-panel')).toBeInTheDocument();
    expect(screen.getByText('Protocol: None')).toBeInTheDocument();
    expect(screen.getByText('No feedback data')).toBeInTheDocument();
  });

  it('renders protocol name', () => {
    render(<NeurofeedbackPanel protocolName="Alpha Up" />);
    expect(screen.getByText('Protocol: Alpha Up')).toBeInTheDocument();
  });

  it('shows start training button when not training', () => {
    render(<NeurofeedbackPanel isTraining={false} />);
    expect(screen.getByTestId('start-training')).toBeInTheDocument();
  });

  it('shows stop training button when training', () => {
    render(<NeurofeedbackPanel isTraining={true} />);
    expect(screen.getByTestId('stop-training')).toBeInTheDocument();
  });

  it('calls onStartTraining', () => {
    const onStart = vi.fn();
    render(<NeurofeedbackPanel onStartTraining={onStart} />);
    fireEvent.click(screen.getByTestId('start-training'));
    expect(onStart).toHaveBeenCalledOnce();
  });

  it('calls onStopTraining', () => {
    const onStop = vi.fn();
    render(<NeurofeedbackPanel isTraining={true} onStopTraining={onStop} />);
    fireEvent.click(screen.getByTestId('stop-training'));
    expect(onStop).toHaveBeenCalledOnce();
  });

  it('displays feedback state with reward active', () => {
    const feedback: FeedbackState = {
      reward: true,
      inhibit: false,
      rewardValue: 0.85,
      inhibitValue: 0.12,
    };
    render(<NeurofeedbackPanel feedback={feedback} />);
    const rewardEl = screen.getByTestId('reward-indicator');
    expect(rewardEl).toHaveTextContent('0.85');
    expect(rewardEl).toHaveClass('active');
    const inhibitEl = screen.getByTestId('inhibit-indicator');
    expect(inhibitEl).toHaveTextContent('0.12');
    expect(inhibitEl).not.toHaveClass('active');
  });

  it('displays feedback state with inhibit active', () => {
    const feedback: FeedbackState = {
      reward: false,
      inhibit: true,
      rewardValue: 0.3,
      inhibitValue: 0.9,
    };
    render(<NeurofeedbackPanel feedback={feedback} />);
    expect(screen.getByTestId('reward-indicator')).not.toHaveClass('active');
    expect(screen.getByTestId('inhibit-indicator')).toHaveClass('active');
  });

  it('renders protocol selector with all options', () => {
    render(<NeurofeedbackPanel />);
    const select = screen.getByTestId('protocol-select');
    expect(select).toBeInTheDocument();
    expect(select).toHaveValue('smr_training');
  });

  it('calls onProtocolChange when protocol is selected', () => {
    const onChange = vi.fn();
    render(<NeurofeedbackPanel onProtocolChange={onChange} />);
    fireEvent.change(screen.getByTestId('protocol-select'), {
      target: { value: 'sr_entrainment' },
    });
    expect(onChange).toHaveBeenCalledWith('sr_entrainment');
  });

  it('disables protocol selector when training', () => {
    render(<NeurofeedbackPanel isTraining={true} />);
    expect(screen.getByTestId('protocol-select')).toBeDisabled();
  });

  it('does not render SR card when srData is undefined', () => {
    render(<NeurofeedbackPanel />);
    expect(screen.queryByTestId('sr-status-card')).not.toBeInTheDocument();
  });

  it('renders SR status card when srData is provided', () => {
    const sr: SRData = { frequency: 7.796, stationId: 'simulator1' };
    render(<NeurofeedbackPanel srData={sr} />);
    expect(screen.getByTestId('sr-status-card')).toBeInTheDocument();
    expect(screen.getByTestId('sr-status-dot')).toBeInTheDocument();
    expect(screen.getByTestId('sr-frequency')).toHaveTextContent('7.796 Hz');
    expect(screen.getByText('simulator1')).toBeInTheDocument();
  });

  it('displays correct SR target band range', () => {
    const sr: SRData = { frequency: 7.83, stationId: 'test-station' };
    render(<NeurofeedbackPanel srData={sr} />);
    expect(screen.getByTestId('sr-target-band')).toHaveTextContent('6.83');
    expect(screen.getByTestId('sr-target-band')).toHaveTextContent('8.83');
  });

  it('renders SR frequency marker within theta/alpha bar', () => {
    const sr: SRData = { frequency: 7.83, stationId: 'simulator1' };
    render(<NeurofeedbackPanel srData={sr} />);
    const marker = screen.getByTestId('sr-marker');
    expect(marker).toBeInTheDocument();
    // 7.83 Hz: (7.83 - 4) / (13 - 4) * 100 = 42.6%
    expect(marker.style.left).toMatch(/42\.\d+%/);
  });

  it('clamps SR marker at 0% for low frequencies', () => {
    const sr: SRData = { frequency: 2.0, stationId: 'sim' };
    render(<NeurofeedbackPanel srData={sr} />);
    expect(screen.getByTestId('sr-marker').style.left).toBe('0%');
  });

  it('clamps SR marker at 100% for high frequencies', () => {
    const sr: SRData = { frequency: 15.0, stationId: 'sim' };
    render(<NeurofeedbackPanel srData={sr} />);
    expect(screen.getByTestId('sr-marker').style.left).toBe('100%');
  });

  it('PROTOCOL_OPTIONS includes sr_entrainment with hasEarthSync', () => {
    const srProto = PROTOCOL_OPTIONS.find((p) => p.id === 'sr_entrainment');
    expect(srProto).toBeDefined();
    expect(srProto?.hasEarthSync).toBe(true);
    expect(srProto?.label).toBe('SR Entrainment');
  });

  it('PROTOCOL_OPTIONS has 4 protocols', () => {
    expect(PROTOCOL_OPTIONS).toHaveLength(4);
  });

  it('non-EarthSync protocols have hasEarthSync false', () => {
    const nonSR = PROTOCOL_OPTIONS.filter((p) => p.id !== 'sr_entrainment');
    for (const p of nonSR) {
      expect(p.hasEarthSync).toBe(false);
    }
  });
});

describe('SessionManager', () => {
  it('renders with defaults', () => {
    render(<SessionManager />);
    expect(screen.getByTestId('session-manager')).toBeInTheDocument();
    expect(screen.getByText('No recorded sessions')).toBeInTheDocument();
  });

  it('shows start recording button when not recording', () => {
    render(<SessionManager isRecording={false} />);
    expect(screen.getByTestId('start-recording')).toBeInTheDocument();
  });

  it('shows stop recording button when recording', () => {
    render(<SessionManager isRecording={true} />);
    expect(screen.getByTestId('stop-recording')).toBeInTheDocument();
  });

  it('calls onStartRecording', () => {
    const onStart = vi.fn();
    render(<SessionManager onStartRecording={onStart} />);
    fireEvent.click(screen.getByTestId('start-recording'));
    expect(onStart).toHaveBeenCalledOnce();
  });

  it('calls onStopRecording', () => {
    const onStop = vi.fn();
    render(<SessionManager isRecording={true} onStopRecording={onStop} />);
    fireEvent.click(screen.getByTestId('stop-recording'));
    expect(onStop).toHaveBeenCalledOnce();
  });

  it('renders session list', () => {
    const sessions = [
      { id: '1', name: 'Session 1', date: '2026-03-26', duration: 300 },
      { id: '2', name: 'Session 2', date: '2026-03-25', duration: 600 },
    ];
    render(<SessionManager sessions={sessions} />);
    expect(screen.getByTestId('session-list')).toBeInTheDocument();
    expect(screen.getByText(/Session 1/)).toBeInTheDocument();
    expect(screen.getByText(/Session 2/)).toBeInTheDocument();
    expect(screen.getByText(/300s/)).toBeInTheDocument();
  });

  it('does not show "no sessions" when sessions exist', () => {
    const sessions = [{ id: '1', name: 'Test', date: '2026-03-26', duration: 60 }];
    render(<SessionManager sessions={sessions} />);
    expect(screen.queryByText('No recorded sessions')).not.toBeInTheDocument();
  });
});
