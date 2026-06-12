/** Session recording and playback manager. */

import { Circle, FolderOpen } from 'lucide-react';
import { Button } from './ui/Button';
import { EmptyState } from './ui/EmptyState';
import { Panel } from './ui/Panel';
import { StatusChip } from './ui/StatusChip';

export interface Session {
  id: string;
  name: string;
  date: string;
  duration: number;
  /** Recording size in bytes. */
  size?: number;
}

interface SessionManagerProps {
  sessions?: Session[];
  isRecording?: boolean;
  onStartRecording?: () => void;
  onStopRecording?: () => void;
}

/** Format a duration in seconds as m:ss. */
export function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
}

/** Format a byte count as a human-readable size. */
export function formatSize(bytes?: number): string {
  if (bytes == null) return '—';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

export function SessionManager({
  sessions = [],
  isRecording = false,
  onStartRecording,
  onStopRecording,
}: SessionManagerProps) {
  return (
    <div className="mx-auto w-full flex flex-col gap-4 max-w-3xl" data-testid="session-manager">
      <Panel title="Recording" meta={`${sessions.length} saved`}>
        <div className="flex items-center justify-between gap-4">
          <StatusChip
            variant={isRecording ? 'danger' : 'neutral'}
            label={isRecording ? 'Recording' : 'Idle'}
            pulse={isRecording}
          />
          {isRecording ? (
            <Button variant="danger" onClick={onStopRecording} data-testid="stop-recording">
              <Circle className="w-3 h-3 fill-current" aria-hidden={true} />
              Stop Recording
            </Button>
          ) : (
            <Button variant="primary" onClick={onStartRecording} data-testid="start-recording">
              <Circle className="w-3 h-3 fill-current" aria-hidden={true} />
              Start Recording
            </Button>
          )}
        </div>
      </Panel>

      <Panel title="Sessions" noPadding>
        {sessions.length === 0 ? (
          <EmptyState
            icon={FolderOpen}
            label="No recorded sessions"
            hint="Start a recording to capture an EEG session."
          />
        ) : (
          <ul data-testid="session-list" className="divide-y divide-border">
            {sessions.map((s) => (
              <li
                key={s.id}
                className="grid grid-cols-[1fr_auto_auto_auto] items-center gap-4 px-4 py-2.5 text-sm hover:bg-bg-raised/50 transition-colors"
              >
                <span className="text-text-primary truncate">{s.name}</span>
                <span className="font-mono tabular-nums text-text-secondary text-xs">
                  {formatDuration(s.duration)}
                </span>
                <span className="font-mono tabular-nums text-text-muted text-xs w-16 text-right">
                  {formatSize(s.size)}
                </span>
                <span className="font-mono tabular-nums text-text-muted text-xs">{s.date}</span>
              </li>
            ))}
          </ul>
        )}
      </Panel>
    </div>
  );
}
