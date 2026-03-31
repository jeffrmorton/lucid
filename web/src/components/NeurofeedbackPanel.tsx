/** Neurofeedback training panel with optional Schumann Resonance entrainment display. */

import { useState, useRef, useCallback } from 'react';

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
}

export const PROTOCOL_OPTIONS: ProtocolOption[] = [
  { id: 'smr_training', label: 'SMR Training', hasEarthSync: false },
  { id: 'alpha_theta', label: 'Alpha/Theta', hasEarthSync: false },
  { id: 'beta_training', label: 'Beta Training', hasEarthSync: false },
  { id: 'sr_entrainment', label: 'SR Entrainment', hasEarthSync: true },
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
  return (
    <div className="space-y-3" data-testid="neurofeedback-panel">
      <div className="bg-bg-panel rounded-lg p-3">
        <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-2">
          Neurofeedback
        </h3>

        {/* Protocol selector */}
        <div className="mb-3">
          <label htmlFor="protocol-select" className="text-xs text-text-muted block mb-1">
            Protocol
          </label>
          <select
            id="protocol-select"
            data-testid="protocol-select"
            value={selectedProtocol}
            onChange={(e) => onProtocolChange?.(e.target.value)}
            disabled={isTraining}
            className="w-full text-xs bg-bg-primary text-text-primary border border-border rounded px-2 py-1.5 focus:outline-none focus:border-accent disabled:opacity-50"
          >
            {PROTOCOL_OPTIONS.map((p) => (
              <option key={p.id} value={p.id}>
                {p.label}
                {p.hasEarthSync ? ' (EarthSync)' : ''}
              </option>
            ))}
          </select>
        </div>

        <p className="text-xs text-text-muted mb-2">Protocol: {protocolName}</p>
        <div className="space-y-1 mb-3">
          {feedback ? (
            <>
              <div
                className={`text-xs font-mono px-2 py-1 rounded ${feedback.reward ? 'active bg-success/20 text-success' : 'bg-bg-primary text-text-muted'}`}
                data-testid="reward-indicator"
              >
                Reward: {feedback.reward ? '\u2713' : '\u2014'} ({feedback.rewardValue.toFixed(2)})
              </div>
              <div
                className={`text-xs font-mono px-2 py-1 rounded ${feedback.inhibit ? 'active bg-warning/20 text-warning' : 'bg-bg-primary text-text-muted'}`}
                data-testid="inhibit-indicator"
              >
                Inhibit: {feedback.inhibit ? '\u26A0' : '\u2014'} (
                {feedback.inhibitValue.toFixed(2)})
              </div>
            </>
          ) : (
            <p className="text-xs text-text-muted">No feedback data</p>
          )}
        </div>
        {phase && (
          <p className="text-xs text-text-muted mb-2" data-testid="training-phase">
            Phase: {phase}
          </p>
        )}
        <div>
          {isTraining ? (
            <button
              type="button"
              onClick={handleStopTraining}
              data-testid="stop-training"
              className="text-xs px-3 py-1.5 rounded bg-error/20 text-error hover:bg-error/30 transition-colors"
            >
              Stop Training
            </button>
          ) : (
            <button
              type="button"
              onClick={handleStartTraining}
              data-testid="start-training"
              className="text-xs px-3 py-1.5 rounded bg-accent/20 text-accent hover:bg-accent/30 transition-colors"
            >
              Start Training
            </button>
          )}
        </div>
      </div>

      {/* Schumann Resonance status card */}
      {srData && (
        <div
          className="bg-bg-panel rounded-lg p-3 border border-border"
          data-testid="sr-status-card"
        >
          <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-2">
            Schumann Resonance
          </h3>
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <div
                className="w-2 h-2 rounded-full bg-success"
                data-testid="sr-status-dot"
              />
              <span className="text-sm text-text-secondary">EarthSync</span>
              <span className="text-xs text-text-muted">{srData.stationId}</span>
            </div>
            <div className="text-2xl font-mono text-accent" data-testid="sr-frequency">
              {srData.frequency.toFixed(3)} Hz
            </div>
            <div className="text-xs text-text-muted" data-testid="sr-target-band">
              Target: {(srData.frequency - 1).toFixed(2)} &ndash;{' '}
              {(srData.frequency + 1).toFixed(2)} Hz
            </div>
            {/* Visual frequency indicator — positions SR within theta/alpha range */}
            <div className="mt-2">
              <div className="flex justify-between text-[10px] text-text-muted mb-0.5">
                <span>4 Hz</span>
                <span>Theta | Alpha</span>
                <span>13 Hz</span>
              </div>
              <div className="relative h-2 bg-bg-primary rounded-full overflow-hidden">
                {/* Theta region (4-8 Hz) */}
                <div
                  className="absolute inset-y-0 left-0 bg-band-theta/30"
                  style={{ width: `${((8 - 4) / (13 - 4)) * 100}%` }}
                />
                {/* Alpha region (8-13 Hz) */}
                <div
                  className="absolute inset-y-0 bg-band-alpha/30"
                  style={{
                    left: `${((8 - 4) / (13 - 4)) * 100}%`,
                    width: `${((13 - 8) / (13 - 4)) * 100}%`,
                  }}
                />
                {/* SR fundamental marker */}
                <div
                  className="absolute top-0 h-full w-1 bg-accent rounded-full"
                  data-testid="sr-marker"
                  style={{
                    left: `${Math.min(Math.max(((srData.frequency - 4) / (13 - 4)) * 100, 0), 100)}%`,
                    transform: 'translateX(-50%)',
                  }}
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
