/** Band power visualization — horizontal bars for delta/theta/alpha/beta/gamma. */

import clsx from 'clsx';
import type { BandPowers } from '../lib/types';
import { Panel } from './ui/Panel';

const BANDS = [
  { name: 'Delta', key: 'delta' as const, color: 'bg-band-delta', range: '0.5–4 Hz' },
  { name: 'Theta', key: 'theta' as const, color: 'bg-band-theta', range: '4–8 Hz' },
  { name: 'Alpha', key: 'alpha' as const, color: 'bg-band-alpha', range: '8–13 Hz' },
  { name: 'Beta', key: 'beta' as const, color: 'bg-band-beta', range: '13–30 Hz' },
  { name: 'Gamma', key: 'gamma' as const, color: 'bg-band-gamma', range: '30–100 Hz' },
];

interface BandPowerProps {
  powers?: BandPowers | null;
}

export function BandPower({ powers }: BandPowerProps) {
  const maxPower = powers
    ? Math.max(powers.delta, powers.theta, powers.alpha, powers.beta, powers.gamma, 1)
    : 1;

  return (
    <Panel title="Band Power" className="h-full" testId="band-power">
      <div className="space-y-2.5">
        {BANDS.map((band) => {
          const value = powers ? powers[band.key] : 0;
          const pct = Math.min(100, (value / maxPower) * 100);
          return (
            <div key={band.name} className="flex items-center gap-2">
              <span className="text-[11px] font-mono text-text-secondary w-9 shrink-0">
                {band.name.slice(0, 3)}
              </span>
              <div className="flex-1 h-2.5 bg-bg-raised rounded-full overflow-hidden">
                <div
                  className={clsx('h-full rounded-full transition-all duration-300', band.color)}
                  style={{ width: `${pct}%`, opacity: powers ? 0.9 : 0.2 }}
                />
              </div>
              <span className="text-[11px] font-mono tabular-nums text-text-muted w-12 text-right">
                {powers ? value.toFixed(1) : '—'}
              </span>
            </div>
          );
        })}
      </div>
    </Panel>
  );
}
