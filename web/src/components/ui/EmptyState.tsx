/** Centered empty-state: glyph + label + hint. */

import type { ComponentType, ReactNode } from 'react';

interface EmptyStateProps {
  /** lucide-react icon component. */
  icon: ComponentType<{ className?: string; 'aria-hidden'?: boolean }>;
  label: ReactNode;
  hint?: ReactNode;
  className?: string;
}

export function EmptyState({ icon: Icon, label, hint, className }: EmptyStateProps) {
  return (
    <div
      className={`flex flex-col items-center justify-center gap-2 text-center px-4 py-8 ${className ?? ''}`}
      data-testid="empty-state"
    >
      <Icon className="w-8 h-8 text-text-muted" aria-hidden={true} />
      <p className="text-sm text-text-secondary">{label}</p>
      {hint && <p className="text-xs text-text-muted">{hint}</p>}
    </div>
  );
}
