/** Device connection control: status chip + connect/disconnect button. */

import type { ConnectionStatus } from '../lib/types';
import { Button } from './ui/Button';
import { StatusChip, type StatusVariant } from './ui/StatusChip';

interface DeviceConnectProps {
  status: ConnectionStatus;
  onConnect: () => void;
  onDisconnect: () => void;
}

export const STATUS_META: Record<
  ConnectionStatus,
  { variant: StatusVariant; label: string; pulse: boolean }
> = {
  connected: { variant: 'success', label: 'Connected', pulse: false },
  connecting: { variant: 'warning', label: 'Connecting', pulse: true },
  disconnected: { variant: 'neutral', label: 'Disconnected', pulse: false },
  error: { variant: 'danger', label: 'Error', pulse: false },
};

export function DeviceConnect({ status, onConnect, onDisconnect }: DeviceConnectProps) {
  const meta = STATUS_META[status];
  const isConnected = status === 'connected';
  const isConnecting = status === 'connecting';

  return (
    <div className="flex items-center gap-2.5" data-testid="device-connect">
      <StatusChip variant={meta.variant} label={meta.label} pulse={meta.pulse} />
      {isConnected ? (
        <Button variant="danger" onClick={onDisconnect}>
          Disconnect
        </Button>
      ) : isConnecting ? null : (
        <Button variant="primary" onClick={onConnect}>
          Connect
        </Button>
      )}
    </div>
  );
}
