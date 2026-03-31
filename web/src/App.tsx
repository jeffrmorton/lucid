import { useState } from 'react';
import { Activity, Brain, FolderOpen, Radio, Settings, Waves } from 'lucide-react';
import { Group, Panel, Separator } from 'react-resizable-panels';
import clsx from 'clsx';
import { BandPower } from './components/BandPower';
import { DeviceConnect } from './components/DeviceConnect';
import { EEGTrace } from './components/EEGTrace';
import { NeurofeedbackPanel, PROTOCOL_OPTIONS } from './components/NeurofeedbackPanel';
import type { SRData } from './components/NeurofeedbackPanel';
import { SessionManager } from './components/SessionManager';
import { Spectrogram } from './components/Spectrogram';
import { TopoMap } from './components/TopoMap';
import { useEEGStream } from './hooks/useEEGStream';

type Page = 'signals' | 'neurofeedback' | 'sessions' | 'device';

const NAV_ITEMS: { page: Page; icon: typeof Waves; label: string }[] = [
  { page: 'signals', icon: Waves, label: 'Signals' },
  { page: 'neurofeedback', icon: Activity, label: 'Neurofeedback' },
  { page: 'sessions', icon: FolderOpen, label: 'Sessions' },
  { page: 'device', icon: Radio, label: 'Device' },
];

export function App() {
  const { status, connect, disconnect, latestData } = useEEGStream();
  const [page, setPage] = useState<Page>('signals');
  const [selectedProtocol, setSelectedProtocol] = useState('smr_training');
  const [srData, setSRData] = useState<SRData | undefined>(undefined);

  // Derive protocol label for display
  const protocolLabel =
    PROTOCOL_OPTIONS.find((p) => p.id === selectedProtocol)?.label ?? selectedProtocol;

  // Handle protocol changes — clear SR data when switching away from SR protocol
  const handleProtocolChange = (protocolId: string) => {
    setSelectedProtocol(protocolId);
    const proto = PROTOCOL_OPTIONS.find((p) => p.id === protocolId);
    if (!proto?.hasEarthSync) {
      setSRData(undefined);
    }
  };

  // Update SR data from neurofeedback panel WebSocket feedback messages
  const handleSRDataChange = (sr: SRData | undefined) => {
    setSRData(sr);
  };

  const traceData = latestData.bandPowers
    ? Array.from({ length: 8 }, (_, ch) => {
        const alpha = latestData.channelAlpha[ch] ?? 0;
        return Array.from({ length: 250 }, (__, i) => {
          const t = i / 250;
          return (
            alpha * 0.1 * Math.sin(2 * Math.PI * 10 * t + ch * 0.3) + (Math.random() - 0.5) * 2
          );
        });
      })
    : undefined;

  return (
    <div className="flex h-screen bg-bg-primary text-text-primary overflow-hidden">
      {/* Sidebar */}
      <nav className="w-14 bg-bg-secondary border-r border-border flex flex-col items-center py-4 gap-4">
        <div className="w-8 h-8 bg-accent rounded-lg flex items-center justify-center">
          <Brain className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1 flex flex-col items-center gap-3 mt-4">
          {NAV_ITEMS.map(({ page: p, icon: Icon, label }) => (
            <button
              key={p}
              type="button"
              onClick={() => setPage(p)}
              className={clsx(
                'w-9 h-9 rounded-lg flex items-center justify-center transition-colors',
                page === p
                  ? 'bg-accent/20 text-accent'
                  : 'text-text-secondary hover:text-text-primary hover:bg-bg-hover',
              )}
              title={label}
            >
              <Icon className="w-4 h-4" />
            </button>
          ))}
        </div>
        <button
          type="button"
          className="w-9 h-9 rounded-lg flex items-center justify-center text-text-muted hover:text-text-secondary hover:bg-bg-hover transition-colors"
          title="Settings"
        >
          <Settings className="w-4 h-4" />
        </button>
      </nav>

      {/* Main area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="h-12 bg-bg-secondary border-b border-border flex items-center px-4 gap-4 shrink-0">
          <h1 className="text-sm font-semibold tracking-wide">LUCID</h1>
          <DeviceConnect status={status} onConnect={connect} onDisconnect={disconnect} />
          <div className="flex-1" />
          {latestData.epochCount > 0 && (
            <span className="text-xs font-mono text-text-muted">
              Epochs: {latestData.epochCount}
            </span>
          )}
          <span className="text-xs font-mono text-text-muted">
            {latestData.nSamples > 0 ? `${latestData.nSamples} sps` : '\u2014'}
          </span>
        </header>

        {/* Page content */}
        {page === 'signals' && (
          <Group orientation="vertical" className="flex-1">
            <Panel id="panel-eeg" defaultSize={50} minSize={20}>
              <div className="h-full p-2">
                <EEGTrace channels={8} sampleRate={250} data={traceData} />
              </div>
            </Panel>
            <Separator className="h-1 bg-border hover:bg-accent/50 transition-colors cursor-row-resize" />
            <Panel id="panel-analysis" defaultSize={50} minSize={20}>
              <Group orientation="horizontal">
                <Panel id="panel-spectrogram" defaultSize={50} minSize={15}>
                  <div className="h-full p-2">
                    <Spectrogram data={latestData.spectrogramRows} />
                  </div>
                </Panel>
                <Separator className="w-1 bg-border hover:bg-accent/50 transition-colors cursor-col-resize" />
                <Panel id="panel-details" defaultSize={50} minSize={20}>
                  <div className="h-full p-2 overflow-y-auto">
                    <div className="grid grid-cols-2 gap-2">
                      <BandPower powers={latestData.bandPowers} />
                      <TopoMap channelValues={latestData.channelAlpha} size={180} />
                    </div>
                  </div>
                </Panel>
              </Group>
            </Panel>
          </Group>
        )}

        {page === 'neurofeedback' && (
          <div className="flex-1 p-4 overflow-y-auto">
            <NeurofeedbackPanel
              protocolName={protocolLabel}
              selectedProtocol={selectedProtocol}
              onProtocolChange={handleProtocolChange}
              srData={srData}
              onSRDataChange={handleSRDataChange}
            />
          </div>
        )}

        {page === 'sessions' && (
          <div className="flex-1 p-4 overflow-y-auto">
            <SessionManager />
          </div>
        )}

        {page === 'device' && (
          <div className="flex-1 p-4 overflow-y-auto">
            <div className="bg-bg-panel rounded-lg p-4 max-w-lg">
              <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-3">Device Info</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-text-muted">Status</span>
                  <span className={clsx(
                    'font-mono',
                    status === 'connected' && 'text-success',
                    status === 'error' && 'text-error',
                  )}>{status}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-text-muted">Channels</span>
                  <span className="font-mono">8</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-text-muted">Sample Rate</span>
                  <span className="font-mono">250 SPS</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-text-muted">Epochs Received</span>
                  <span className="font-mono">{latestData.epochCount}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-text-muted">Protocol</span>
                  <span className="font-mono text-text-secondary">WebSocket Viewer</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
