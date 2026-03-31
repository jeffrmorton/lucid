/** Session recording and playback manager. */

interface Session {
  id: string;
  name: string;
  date: string;
  duration: number;
}

interface SessionManagerProps {
  sessions?: Session[];
  isRecording?: boolean;
  onStartRecording?: () => void;
  onStopRecording?: () => void;
}

export function SessionManager({
  sessions = [],
  isRecording = false,
  onStartRecording,
  onStopRecording,
}: SessionManagerProps) {
  return (
    <div className="bg-bg-panel rounded-lg p-3" data-testid="session-manager">
      <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-2">
        Sessions
      </h3>
      <div className="mb-2">
        {isRecording ? (
          <button
            type="button"
            onClick={onStopRecording}
            data-testid="stop-recording"
            className="text-xs px-3 py-1.5 rounded bg-error/20 text-error hover:bg-error/30 transition-colors"
          >
            Stop Recording
          </button>
        ) : (
          <button
            type="button"
            onClick={onStartRecording}
            data-testid="start-recording"
            className="text-xs px-3 py-1.5 rounded bg-accent/20 text-accent hover:bg-accent/30 transition-colors"
          >
            Start Recording
          </button>
        )}
      </div>
      <ul className="space-y-1" data-testid="session-list">
        {sessions.map((s) => (
          <li
            key={s.id}
            className="text-xs font-mono text-text-secondary px-2 py-1 rounded bg-bg-primary"
          >
            {s.name} &mdash; {s.date} ({s.duration}s)
          </li>
        ))}
      </ul>
      {sessions.length === 0 && <p className="text-xs text-text-muted">No recorded sessions</p>}
    </div>
  );
}
