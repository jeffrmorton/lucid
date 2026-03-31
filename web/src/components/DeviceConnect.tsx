/** Device connection UI. */

import clsx from 'clsx';
import type { ConnectionStatus } from '../lib/types';

interface DeviceConnectProps {
  status: ConnectionStatus;
  onConnect: () => void;
  onDisconnect: () => void;
}

export function DeviceConnect({ status, onConnect, onDisconnect }: DeviceConnectProps) {
  const isConnected = status === 'connected';
  const isConnecting = status === 'connecting';

  return (
    <div className="flex items-center gap-2" data-testid="device-connect">
      <div
        className={clsx(
          'w-2 h-2 rounded-full',
          isConnected && 'bg-success animate-pulse',
          isConnecting && 'bg-warning animate-pulse',
          !isConnected && !isConnecting && 'bg-text-muted',
        )}
      />
      {isConnected ? (
        <button
          type="button"
          onClick={onDisconnect}
          className="text-xs px-2 py-1 rounded bg-bg-hover text-text-secondary hover:text-error hover:bg-error/10 transition-colors"
        >
          Disconnect
        </button>
      ) : isConnecting ? (
        <span className="text-xs text-warning">Connecting...</span>
      ) : (
        <button
          type="button"
          onClick={onConnect}
          className="text-xs px-2 py-1 rounded bg-accent/20 text-accent hover:bg-accent/30 transition-colors"
        >
          Connect
        </button>
      )}
      <span className="text-xs text-text-muted" data-testid="status-dot">
        {status}
      </span>
    </div>
  );
}
