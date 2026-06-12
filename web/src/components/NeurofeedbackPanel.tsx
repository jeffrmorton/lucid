/** Neurofeedback training panel with optional Schumann Resonance entrainment display. */

import clsx from 'clsx';
import { Radio } from 'lucide-react';
import { useCallback, useRef, useState } from 'react';
import { Button } from './ui/Button';
import { Panel } from './ui/Panel';
import { Select } from './ui/Select';
import { StatusChip } from './ui/StatusChip';

export interface FeedbackState {
  reward: boolean;
  inhibit: boolean;
  rewardValue: number;
  inhibitValue: number;
}

export interface SRData {
  frequency: number;
  stationId: string;
}

/** Available neurofeedback protocol definitions. */
export interface ProtocolOption {
  id: string;
  label: string;
  hasEarthSync: boolean;
  description: string;
}

export const PROTOCOL_OPTIONS: ProtocolOption[] = [
  {
    id: 'smr_training',
    label: 'SMR Training',
    hasEarthSync: false,
    description: 'Reinforce the 12–15 Hz sensorimotor rhythm while inhibiting theta and high beta.',
  },
  {
    id: 'alpha_theta',
    label: 'Alpha/Theta',
    hasEarthSync: false,
    description: 'Deep relaxation protocol rewarding the alpha/theta crossover.',
  },
  {
    id: 'beta_training',
    label: 'Beta Training',
    hasEarthSync: false,
    description: 'Boost focused 15–20 Hz beta activity for sustained attention.',
  },
  {
    id: 'sr_entrainment',
    label: 'SR Entrainment',
    hasEarthSync: true,
    description: 'Entrain to the live Schumann Resonance fundamental streamed from EarthSync.',
  },
];

interface NeurofeedbackPanelProps {
  feedback?: FeedbackState;
  protocolName?: string;
  isTraining?: boolean;
  onStartTraining?: () => void;
  onStopTraining?: () => void;
  srData?: SRData;
  onSRDataChange?: (srData: SRData | undefined) => void;
  onFeedbackChange?: (feedback: FeedbackState | undefined) => void;
  onTrainingChange?: (isTraining: boolean) => void;
  selectedProtocol?: string;
  onProtocolChange?: (protocolId: string) => void;
}

export function NeurofeedbackPanel({
  feedback: externalFeedback,
  protocolName = 'None',
  isTraining: externalIsTraining,
  onStartTraining,
  onStopTraining,
  srData: externalSRData,
  onSRDataChange,
  onFeedbackChange,
  onTrainingChange,
  selectedProtocol = 'smr_training',
  onProtocolChange,
}: NeurofeedbackPanelProps) {
  const [localFeedback, setLocalFeedback] = useState<FeedbackState | undefined>(undefined);
  const [localIsTraining, setLocalIsTraining] = useState(false);
  const [localSRData, setLocalSRData] = useState<SRData | undefined>(undefined);
  const [phase, setPhase] = useState<string | undefined>(undefined);
  const wsRef = useRef<WebSocket | null>(null);

  // Use external props if provided, otherwise use local state
  const feedback = externalFeedback ?? localFeedback;
  const isTraining = externalIsTraining ?? localIsTraining;
  const srData = externalSRData ?? localSRData;

  const updateTraining = useCallback(
    (val: boolean) => {
      setLocalIsTraining(val);
      onTrainingChange?.(val);
    },
    [onTrainingChange],
  );

  const updateFeedback = useCallback(
    (val: FeedbackState | undefined) => {
      setLocalFeedback(val);
      onFeedbackChange?.(val);
    },
    [onFeedbackChange],
  );

  const updateSR = useCallback(
    (val: SRData | undefined) => {
      setLocalSRData(val);
      onSRDataChange?.(val);
    },
    [onSRDataChange],
  );

  const handleStartTraining = useCallback(() => {
    if (onStartTraining) {
      onStartTraining();
      return;
    }

    // Open neurofeedback WebSocket
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/neurofeedback`);
    wsRef.current = ws;

    ws.onopen = () => {
      ws.send(JSON.stringify({ protocol: selectedProtocol }));
    };

    ws.onmessage = (event: MessageEvent) => {
      const msg = JSON.parse(event.data as string) as Record<string, unknown>;
      if (msg.phase === 'calibration') {
        setPhase('calibration');
        updateTraining(true);
        // If EarthSync info is in calibration message, display it
        if (msg.earthsync && typeof msg.earthsync === 'object') {
          const es = msg.earthsync as { sr_frequency?: number; station_id?: string };
          if (es.sr_frequency != null) {
            updateSR({ frequency: es.sr_frequency, stationId: es.station_id ?? '' });
          }
        }
      } else if (msg.phase === 'training') {
        setPhase('training');
      } else if (msg.status === 'feedback') {
        setPhase('training');
        updateFeedback({
          reward: msg.reward as boolean,
          inhibit: msg.inhibit as boolean,
          rewardValue: (msg.reward_value as number) ?? 0,
          inhibitValue: (msg.inhibit_value as number) ?? 0,
        });
        if (msg.sr && typeof msg.sr === 'object') {
          const sr = msg.sr as { frequency: number; station_id: string };
          updateSR({ frequency: sr.frequency, stationId: sr.station_id });
        }
      }
    };

    ws.onclose = () => {
      updateTraining(false);
      setPhase(undefined);
      wsRef.current = null;
    };
  }, [onStartTraining, selectedProtocol, updateTraining, updateFeedback, updateSR]);

  const handleStopTraining = useCallback(() => {
    if (onStopTraining) {
      onStopTraining();
      return;
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    updateTraining(false);
    updateFeedback(undefined);
    setPhase(undefined);
  }, [onStopTraining, updateTraining, updateFeedback]);

  const activeProtocol = PROTOCOL_OPTIONS.find((p) => p.id === selectedProtocol);

  return (
    <div className="mx-auto w-full flex flex-col gap-4 max-w-2xl" data-testid="neurofeedback-panel">
      {/* Protocol selector */}
      <Panel title="Protocol">
        <Select
          value={selectedProtocol}
          options={PROTOCOL_OPTIONS.map((p) => ({
            value: p.id,
            label: p.hasEarthSync ? `${p.label} (EarthSync)` : p.label,
          }))}
          onChange={(v) => onProtocolChange?.(v)}
          disabled={isTraining}
          label="Neurofeedback protocol"
          id="protocol-select"
        />
        {activeProtocol && (
          <p className="mt-2 text-xs text-text-secondary" data-testid="protocol-description">
            {activeProtocol.description}
          </p>
        )}
      </Panel>

      {/* Training */}
      <Panel title="Training" meta={`Protocol: ${protocolName}`}>
        <div className="mb-3 flex items-center gap-2">
          {phase ? (
            <StatusChip
              variant={phase === 'training' ? 'success' : 'warning'}
              label={phase === 'training' ? 'Training' : 'Calibration'}
              pulse
              className="capitalize"
            />
          ) : (
            <StatusChip variant="neutral" label="Idle" />
          )}
          {phase && (
            <span className="sr-only" data-testid="training-phase">
              Phase: {phase}
            </span>
          )}
        </div>

        {feedback ? (
          <div className="grid grid-cols-2 gap-3">
            <FeedbackReadout
              testId="reward-indicator"
              label="Reward"
              value={feedback.rewardValue}
              active={feedback.reward}
              tone="success"
            />
            <FeedbackReadout
              testId="inhibit-indicator"
              label="Inhibit"
              value={feedback.inhibitValue}
              active={feedback.inhibit}
              tone="warning"
            />
          </div>
        ) : (
          <p className="text-sm text-text-muted">No feedback data yet.</p>
        )}

        <div className="mt-4">
          {isTraining ? (
            <Button variant="danger" onClick={handleStopTraining} data-testid="stop-training">
              Stop Training
            </Button>
          ) : (
            <Button variant="primary" onClick={handleStartTraining} data-testid="start-training">
              Start Training
            </Button>
          )}
        </div>
      </Panel>

      {/* Schumann Resonance entrainment centerpiece */}
      {srData && (
        <Panel title="SR Entrainment" className="border-border-strong" testId="sr-status-card">
          <div className="flex items-center justify-between">
            <StatusChip variant="success" label="EarthSync Live" pulse />
            <span
              className="font-mono text-[11px] text-text-muted tabular-nums"
              data-testid="sr-status-dot"
            >
              {srData.stationId}
            </span>
          </div>
          <div
            className="mt-3 font-mono tabular-nums text-4xl text-accent-bright"
            data-testid="sr-frequency"
          >
            {srData.frequency.toFixed(3)}
            <span className="ml-1 text-base text-text-muted">Hz</span>
          </div>
          <div className="mt-1 text-xs text-text-secondary" data-testid="sr-target-band">
            Reward band: {(srData.frequency - 1).toFixed(2)} – {(srData.frequency + 1).toFixed(2)}{' '}
            Hz
          </div>

          <div className="mt-4">
            <div className="flex justify-between text-[10px] text-text-muted mb-1">
              <span>4 Hz</span>
              <span>Theta · Alpha</span>
              <span>13 Hz</span>
            </div>
            <div className="relative h-2.5 bg-bg-raised rounded-full overflow-hidden">
              <div
                className="absolute inset-y-0 left-0 bg-band-theta/30"
                style={{ width: `${((8 - 4) / (13 - 4)) * 100}%` }}
              />
              <div
                className="absolute inset-y-0 bg-band-alpha/30"
                style={{
                  left: `${((8 - 4) / (13 - 4)) * 100}%`,
                  width: `${((13 - 8) / (13 - 4)) * 100}%`,
                }}
              />
              <div
                className="absolute top-0 h-full w-1 bg-accent-bright rounded-full"
                data-testid="sr-marker"
                style={{
                  left: `${Math.min(Math.max(((srData.frequency - 4) / (13 - 4)) * 100, 0), 100)}%`,
                  transform: 'translateX(-50%)',
                }}
              />
            </div>
          </div>
        </Panel>
      )}
    </div>
  );
}

interface FeedbackReadoutProps {
  testId: string;
  label: string;
  value: number;
  active: boolean;
  tone: 'success' | 'warning';
}

const TONE = {
  success: { text: 'text-success', bar: 'bg-success', activeRing: 'bg-success/10 ring-success/40' },
  warning: { text: 'text-warning', bar: 'bg-warning', activeRing: 'bg-warning/10 ring-warning/40' },
} as const;

function FeedbackReadout({ testId, label, value, active, tone }: FeedbackReadoutProps) {
  const pct = Math.min(100, Math.max(0, value * 100));
  const t = TONE[tone];
  return (
    <div
      data-testid={testId}
      data-active={active}
      className={clsx(
        'rounded-md p-3 ring-1 ring-inset transition-colors',
        active ? t.activeRing : 'bg-bg-raised ring-border',
      )}
    >
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-semibold uppercase tracking-wider text-text-secondary">
          {label}
        </span>
        <Radio
          className={clsx('w-3.5 h-3.5', active ? t.text : 'text-text-muted')}
          aria-hidden={true}
        />
      </div>
      <div
        className={clsx(
          'mt-1 font-mono tabular-nums text-2xl',
          active ? t.text : 'text-text-primary',
        )}
      >
        {value.toFixed(2)}
      </div>
      <div className="mt-2 h-1.5 bg-bg-panel rounded-full overflow-hidden">
        <div
          className={clsx('h-full rounded-full transition-all', t.bar)}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
