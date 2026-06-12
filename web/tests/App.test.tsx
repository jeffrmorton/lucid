import { act, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { App } from '../src/App';

let sockets: MockSocket[];

class MockSocket {
  static OPEN = 1;
  readyState = 1;
  url: string;
  sent: unknown[] = [];
  onopen: (() => void) | null = null;
  onclose: (() => void) | null = null;
  onerror: (() => void) | null = null;
  onmessage: ((e: { data: string }) => void) | null = null;
  constructor(url: string) {
    this.url = url;
    sockets.push(this);
  }
  send(d: unknown) {
    this.sent.push(d);
  }
  close() {
    this.onclose?.();
  }
}

function socketFor(fragment: string): MockSocket {
  const found = sockets.find((s) => s.url.includes(fragment));
  if (!found) throw new Error(`no socket for ${fragment}`);
  return found;
}

beforeEach(() => {
  sockets = [];
  vi.stubGlobal('WebSocket', MockSocket);
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('App navigation', () => {
  it('renders the brand and disconnected control', () => {
    render(<App />);
    expect(screen.getByText('LUCID')).toBeInTheDocument();
    expect(screen.getByText('Disconnected')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Connect' })).toBeInTheDocument();
  });

  it('renders the signals visualizations', () => {
    render(<App />);
    expect(screen.getByTestId('eeg-trace')).toBeInTheDocument();
    expect(screen.getByTestId('spectrogram')).toBeInTheDocument();
    expect(screen.getByTestId('band-power')).toBeInTheDocument();
    expect(screen.getByTestId('topo-map')).toBeInTheDocument();
    expect(screen.getByText('Del')).toBeInTheDocument();
    expect(screen.getByText('Gam')).toBeInTheDocument();
  });

  it('navigates between pages via the icon rail', () => {
    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: 'Neurofeedback' }));
    expect(screen.getByTestId('neurofeedback-panel')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Sessions' }));
    expect(screen.getByTestId('session-manager')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Device' }));
    expect(screen.getByRole('heading', { name: 'Device' })).toBeInTheDocument();
    expect(screen.getByText('Channels')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Signals' }));
    expect(screen.getByTestId('eeg-trace')).toBeInTheDocument();
  });

  it('marks the active nav item with aria-current', () => {
    render(<App />);
    expect(screen.getByRole('button', { name: 'Signals' })).toHaveAttribute('aria-current', 'page');
  });

  it('exposes a Settings control', () => {
    render(<App />);
    expect(screen.getByRole('button', { name: 'Settings' })).toBeInTheDocument();
  });
});

describe('App data flow', () => {
  it('connects and reflects a processed stream message', () => {
    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: 'Connect' }));
    const ws = socketFor('/ws/viewer');
    act(() => ws.onopen?.());
    expect(screen.getByText('Connected')).toBeInTheDocument();

    act(() =>
      ws.onmessage?.({
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
      }),
    );

    expect(screen.getByText('1.5')).toBeInTheDocument();
    expect(screen.getByText('EPOCHS 1')).toBeInTheDocument();
    expect(screen.getByText('250 SPS')).toBeInTheDocument();

    // PSD shape surfaces on the device page.
    fireEvent.click(screen.getByRole('button', { name: 'Device' }));
    expect(screen.getByText('128 × 5')).toBeInTheDocument();
    expect(screen.getByText('Epochs Received')).toBeInTheDocument();
  });

  it('shows an em-dash SPS readout before any data arrives', () => {
    render(<App />);
    expect(screen.getByText('— SPS')).toBeInTheDocument();
    expect(screen.getByText('EPOCHS 0')).toBeInTheDocument();
  });

  it('changes protocol and clears SR data when leaving an EarthSync protocol', () => {
    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: 'Neurofeedback' }));
    expect(screen.getByText('Protocol: SMR Training')).toBeInTheDocument();

    // Switch to the EarthSync SR protocol.
    fireEvent.click(screen.getByTestId('select-trigger'));
    fireEvent.click(screen.getByTestId('select-option-sr_entrainment'));
    expect(screen.getByText('Protocol: SR Entrainment')).toBeInTheDocument();

    // Switch back to a non-EarthSync protocol (clears SR).
    fireEvent.click(screen.getByTestId('select-trigger'));
    fireEvent.click(screen.getByTestId('select-option-beta_training'));
    expect(screen.getByText('Protocol: Beta Training')).toBeInTheDocument();
    expect(screen.queryByTestId('sr-status-card')).not.toBeInTheDocument();
  });

  it('surfaces live SR data from the neurofeedback socket', () => {
    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: 'Neurofeedback' }));
    fireEvent.click(screen.getByTestId('select-trigger'));
    fireEvent.click(screen.getByTestId('select-option-sr_entrainment'));
    fireEvent.click(screen.getByTestId('start-training'));

    const ws = socketFor('/ws/neurofeedback');
    act(() =>
      ws.onmessage?.({
        data: JSON.stringify({
          phase: 'calibration',
          earthsync: { sr_frequency: 7.83, station_id: 'sim1' },
        }),
      }),
    );
    expect(screen.getByTestId('sr-status-card')).toBeInTheDocument();
    expect(screen.getByTestId('sr-frequency')).toHaveTextContent('7.830');
  });
});
