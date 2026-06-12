/** Soft pill status indicator: colored dot + label. */

import clsx from 'clsx';

export type StatusVariant = 'success' | 'warning' | 'danger' | 'neutral';

interface StatusChipProps {
  variant: StatusVariant;
  label: string;
  /** Pulse the dot (e.g. live connection / recording). */
  pulse?: boolean;
  className?: string;
}

const VARIANTS: Record<StatusVariant, { pill: string; dot: string }> = {
  success: {
    pill: 'bg-success/10 text-success ring-success/20',
    dot: 'bg-success',
  },
  warning: {
    pill: 'bg-warning/10 text-warning ring-warning/20',
    dot: 'bg-warning',
  },
  danger: {
    pill: 'bg-danger/10 text-danger ring-danger/20',
    dot: 'bg-danger',
  },
  neutral: {
    pill: 'bg-bg-raised text-text-secondary ring-border-strong',
    dot: 'bg-text-muted',
  },
};

export function StatusChip({ variant, label, pulse = false, className }: StatusChipProps) {
  const v = VARIANTS[variant];
  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-xs ring-1 ring-inset',
        v.pill,
        className,
      )}
      data-testid="status-chip"
    >
      <span
        aria-hidden="true"
        className={clsx('w-1.5 h-1.5 rounded-full', v.dot, pulse && 'animate-pulse')}
      />
      {label}
    </span>
  );
}
