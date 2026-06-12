import clsx from 'clsx';
import { Activity, Brain, FolderOpen, Radio, Settings, Waves } from 'lucide-react';
import { useMemo, useState } from 'react';
import { Group, Panel as ResizablePanel, Separator } from 'react-resizable-panels';
import { BandPower } from './components/BandPower';
import { DeviceConnect, STATUS_META } from './components/DeviceConnect';
import { EEGTrace } from './components/EEGTrace';
import type { SRData } from './components/NeurofeedbackPanel';
import { NeurofeedbackPanel, PROTOCOL_OPTIONS } from './components/NeurofeedbackPanel';
import { SessionManager } from './components/SessionManager';
import { Spectrogram } from './components/Spectrogram';
import { TopoMap } from './components/TopoMap';
import { Panel } from './components/ui/Panel';
import { StatusChip } from './components/ui/StatusChip';
import { useEEGStream } from './hooks/useEEGStream';
import { DEFAULT_CHANNELS, DEFAULT_SAMPLE_RATE } from './lib/constants';
import { buildTraceData } from './lib/trace-sim';

type Page = 'signals' | 'neurofeedback' | 'sessions' | 'device';

const NAV_ITEMS: { page: Page; icon: typeof Waves; label: string }[] = [
  { page: 'signals', icon: Waves, label: 'Signals' },
  { page: 'neurofeedback', icon: Activity, label: 'Neurofeedback' },
  { page: 'sessions', icon: FolderOpen, label: 'Sessions' },
  { page: 'device', icon: Radio, label: 'Device' },
];

const PAGE_LABELS: Record<Page, string> = {
  signals: 'Signals',
  neurofeedback: 'Neurofeedback',
  sessions: 'Sessions',
  device: 'Device',
};

const PROTOCOL_LABELS: Record<string, string> = Object.fromEntries(
  PROTOCOL_OPTIONS.map((p) => [p.id, p.label]),
);
const PROTOCOL_HAS_EARTHSYNC: Record<string, boolean> = Object.fromEntries(
  PROTOCOL_OPTIONS.map((p) => [p.id, p.hasEarthSync]),
);

export function App() {
  const { status, connect, disconnect, latestData } = useEEGStream();
  const [page, setPage] = useState<Page>('signals');
  const [selectedProtocol, setSelectedProtocol] = useState('smr_training');
  const [srData, setSRData] = useState<SRData | undefined>(undefined);

  const protocolLabel = PROTOCOL_LABELS[selectedProtocol];

  // Clear SR data when switching away from an EarthSync protocol.
  const handleProtocolChange = (protocolId: string) => {
    setSelectedProtocol(protocolId);
    if (!PROTOCOL_HAS_EARTHSYNC[protocolId]) {
      setSRData(undefined);
    }
  };

  const handleSRDataChange = (sr: SRData | undefined) => {
    setSRData(sr);
  };

  // Simulated trace preview — regenerated only when a new epoch arrives.
  const traceData = useMemo(
    () =>
      latestData.bandPowers ? buildTraceData(latestData.channelAlpha, DEFAULT_CHANNELS) : undefined,
    [latestData.bandPowers, latestData.channelAlpha],
  );

  return (
    <div className="flex h-screen bg-bg text-text-primary overflow-hidden">
      {/* Icon rail */}
      <nav
        aria-label="Primary"
        className="w-14 bg-bg-secondary border-r border-border flex flex-col items-center py-4 gap-4 shrink-0"
      >
        <div className="w-8 h-8 bg-accent rounded-lg flex items-center justify-center">
          <Brain className="w-5 h-5 text-white" aria-hidden={true} />
        </div>
        <ul className="flex-1 flex flex-col items-center gap-2 mt-4">
          {NAV_ITEMS.map(({ page: p, icon: Icon, label }) => (
            <li key={p}>
              <button
                type="button"
                onClick={() => setPage(p)}
                aria-label={label}
                aria-current={page === p ? 'page' : undefined}
                title={label}
                className={clsx(
                  'group relative w-9 h-9 rounded-lg flex items-center justify-center transition-colors',
                  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-bg',
                  page === p
                    ? 'bg-accent/15 text-accent-bright'
                    : 'text-text-secondary hover:text-text-primary hover:bg-bg-raised',
                )}
              >
                <Icon className="w-4 h-4" aria-hidden={true} />
                <span className="pointer-events-none absolute left-full ml-2 px-2 py-1 rounded-md bg-bg-raised border border-border-strong text-xs text-text-primary whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity z-30">
                  {label}
                </span>
              </button>
            </li>
          ))}
        </ul>
        <button
          type="button"
          aria-label="Settings"
          title="Settings"
          className="w-9 h-9 rounded-lg flex items-center justify-center text-text-muted hover:text-text-secondary hover:bg-bg-raised transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-bg"
        >
          <Settings className="w-4 h-4" aria-hidden={true} />
        </button>
      </nav>

      {/* Main area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="h-12 bg-bg-secondary border-b border-border flex items-center px-4 gap-4 shrink-0">
          <h1 className="text-sm font-semibold tracking-wide">LUCID</h1>
          <DeviceConnect status={status} onConnect={connect} onDisconnect={disconnect} />
          <div className="flex-1" />
          <span className="font-mono text-[11px] tabular-nums text-text-muted px-2 py-1 rounded-md bg-bg-panel border border-border">
            EPOCHS {latestData.epochCount}
          </span>
          <span className="font-mono text-[11px] tabular-nums text-text-muted px-2 py-1 rounded-md bg-bg-panel border border-border">
            {latestData.nSamples > 0 ? `${latestData.nSamples} SPS` : '— SPS'}
          </span>
        </header>

        <main className="flex-1 min-h-0 flex flex-col" aria-label={`${PAGE_LABELS[page]} view`}>
          {page === 'signals' && (
            <Group orientation="vertical" className="flex-1 min-h-0">
              <ResizablePanel id="panel-eeg" defaultSize={46} minSize={25}>
                <div className="h-full p-2">
                  <EEGTrace
                    channels={DEFAULT_CHANNELS}
                    sampleRate={DEFAULT_SAMPLE_RATE}
                    data={traceData}
                  />
                </div>
              </ResizablePanel>
              <Separator className="h-1 bg-border hover:bg-accent/50 transition-colors cursor-row-resize" />
              <ResizablePanel id="panel-analysis" defaultSize={54} minSize={25}>
                <Group orientation="horizontal" className="h-full">
                  <ResizablePanel id="panel-spectrogram" defaultSize={50} minSize={25}>
                    <div className="h-full p-2">
                      <Spectrogram data={latestData.spectrogramRows} />
                    </div>
                  </ResizablePanel>
                  <Separator className="w-1 bg-border hover:bg-accent/50 transition-colors cursor-col-resize" />
                  <ResizablePanel id="panel-bands" defaultSize={26} minSize={18}>
                    <div className="h-full p-2">
                      <BandPower powers={latestData.bandPowers} />
                    </div>
                  </ResizablePanel>
                  <Separator className="w-1 bg-border hover:bg-accent/50 transition-colors cursor-col-resize" />
                  <ResizablePanel id="panel-topo" defaultSize={24} minSize={18}>
                    <div className="h-full p-2">
                      <TopoMap channelValues={latestData.channelAlpha} />
                    </div>
                  </ResizablePanel>
                </Group>
              </ResizablePanel>
            </Group>
          )}

          {page === 'neurofeedback' && (
            <div className="flex-1 min-h-0 p-4 overflow-y-auto">
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
            <div className="flex-1 min-h-0 p-4 overflow-y-auto">
              <SessionManager />
            </div>
          )}

          {page === 'device' && (
            <div className="flex-1 min-h-0 p-4 overflow-y-auto">
              <Panel title="Device" meta="WebSocket viewer" className="mx-auto w-full max-w-2xl">
                <dl className="grid grid-cols-2 sm:grid-cols-3 gap-x-4 gap-y-5">
                  <div>
                    <dt className="text-[11px] font-semibold uppercase tracking-wider text-text-muted mb-1.5">
                      Status
                    </dt>
                    <dd>
                      <StatusChip
                        variant={STATUS_META[status].variant}
                        label={STATUS_META[status].label}
                        pulse={STATUS_META[status].pulse}
                      />
                    </dd>
                  </div>
                  <Stat label="Channels" value={DEFAULT_CHANNELS} />
                  <Stat label="Sample Rate" value={`${DEFAULT_SAMPLE_RATE} SPS`} />
                  <Stat label="Epochs Received" value={latestData.epochCount} />
                  <Stat
                    label="PSD Shape"
                    value={latestData.psdShape.length > 0 ? latestData.psdShape.join(' × ') : '—'}
                  />
                  <Stat label="Protocol" value="WebSocket Viewer" />
                </dl>
              </Panel>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div>
      <dt className="text-[11px] font-semibold uppercase tracking-wider text-text-muted mb-1.5">
        {label}
      </dt>
      <dd className="font-mono tabular-nums text-sm text-text-primary">{value}</dd>
    </div>
  );
}
