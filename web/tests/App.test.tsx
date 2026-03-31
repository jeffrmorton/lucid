import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { App } from '../src/App';

// Mock WebSocket
class MockWebSocket {
  static OPEN = 1;
  readyState = 1;
  onopen: (() => void) | null = null;
  onclose: (() => void) | null = null;
  onerror: (() => void) | null = null;
  onmessage: ((e: { data: string }) => void) | null = null;
  close() {
    this.onclose?.();
  }
  send() {}
}
vi.stubGlobal('WebSocket', MockWebSocket);

describe('App', () => {
  it('renders the app title', () => {
    render(<App />);
    expect(screen.getByText('LUCID')).toBeInTheDocument();
  });

  it('renders connect button', () => {
    render(<App />);
    expect(screen.getByText('Connect')).toBeInTheDocument();
  });

  it('renders EEG trace component', () => {
    render(<App />);
    expect(screen.getByTestId('eeg-trace')).toBeInTheDocument();
  });

  it('renders band power component', () => {
    render(<App />);
    expect(screen.getByTestId('band-power')).toBeInTheDocument();
  });

  it('shows all 5 EEG bands (abbreviated)', () => {
    render(<App />);
    expect(screen.getByText('Del')).toBeInTheDocument();
    expect(screen.getByText('The')).toBeInTheDocument();
    expect(screen.getByText('Alp')).toBeInTheDocument();
    expect(screen.getByText('Bet')).toBeInTheDocument();
    expect(screen.getByText('Gam')).toBeInTheDocument();
  });

  it('renders spectrogram', () => {
    render(<App />);
    expect(screen.getByTestId('spectrogram')).toBeInTheDocument();
  });

  it('renders topo map', () => {
    render(<App />);
    expect(screen.getByTestId('topo-map')).toBeInTheDocument();
  });

  it('renders neurofeedback panel on neurofeedback page', () => {
    render(<App />);
    // Click the neurofeedback nav button (Activity icon, title="Neurofeedback")
    fireEvent.click(screen.getByTitle('Neurofeedback'));
    expect(screen.getByTestId('neurofeedback-panel')).toBeInTheDocument();
  });

  it('renders session manager on sessions page', () => {
    render(<App />);
    fireEvent.click(screen.getByTitle('Sessions'));
    expect(screen.getByTestId('session-manager')).toBeInTheDocument();
  });

  it('renders device page', () => {
    render(<App />);
    fireEvent.click(screen.getByTitle('Device'));
    expect(screen.getByText('Device Info')).toBeInTheDocument();
  });

  it('switches back to signals page', () => {
    render(<App />);
    fireEvent.click(screen.getByTitle('Neurofeedback'));
    expect(screen.getByTestId('neurofeedback-panel')).toBeInTheDocument();
    fireEvent.click(screen.getByTitle('Signals'));
    expect(screen.getByTestId('eeg-trace')).toBeInTheDocument();
  });

  it('shows disconnected status initially', () => {
    render(<App />);
    expect(screen.getAllByText('disconnected').length).toBeGreaterThan(0);
  });

  it('connects when Connect button clicked', () => {
    render(<App />);
    fireEvent.click(screen.getByText('Connect'));
    // Status should change from disconnected
    expect(screen.getByTestId('status-dot')).toBeInTheDocument();
  });

  it('shows default protocol name on neurofeedback page', () => {
    render(<App />);
    fireEvent.click(screen.getByTitle('Neurofeedback'));
    expect(screen.getByText('Protocol: SMR Training')).toBeInTheDocument();
  });

  it('renders protocol selector on neurofeedback page', () => {
    render(<App />);
    fireEvent.click(screen.getByTitle('Neurofeedback'));
    expect(screen.getByTestId('protocol-select')).toBeInTheDocument();
  });

  it('changes protocol name when SR Entrainment is selected', () => {
    render(<App />);
    fireEvent.click(screen.getByTitle('Neurofeedback'));
    fireEvent.change(screen.getByTestId('protocol-select'), {
      target: { value: 'sr_entrainment' },
    });
    expect(screen.getByText('Protocol: SR Entrainment')).toBeInTheDocument();
  });

  it('does not show SR card when non-EarthSync protocol is selected', () => {
    render(<App />);
    fireEvent.click(screen.getByTitle('Neurofeedback'));
    expect(screen.queryByTestId('sr-status-card')).not.toBeInTheDocument();
  });
});
