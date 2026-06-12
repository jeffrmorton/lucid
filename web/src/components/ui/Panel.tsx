/** Shared panel surface with an optional uppercase title + mono meta header. */

import clsx from 'clsx';
import type { ReactNode } from 'react';

interface PanelProps {
  /** Uppercase section title shown in the header. */
  title?: ReactNode;
  /** Right-aligned mono meta (e.g. "8ch · 250 SPS · 10s"). */
  meta?: ReactNode;
  /** Heading level for the title (defaults to h2). */
  headingLevel?: 'h2' | 'h3';
  /** Remove body padding (canvas panels where the canvas fills the body). */
  noPadding?: boolean;
  /** Extra classes on the outer panel element. */
  className?: string;
  /** Extra classes on the body wrapper. */
  bodyClassName?: string;
  /** Override the panel's data-testid. */
  testId?: string;
  children?: ReactNode;
}

export function Panel({
  title,
  meta,
  headingLevel = 'h2',
  noPadding = false,
  className,
  bodyClassName,
  testId = 'panel',
  children,
}: PanelProps) {
  const Heading = headingLevel;
  return (
    <div
      className={clsx('flex flex-col bg-bg-panel border border-border rounded-lg', className)}
      data-testid={testId}
    >
      {(title || meta) && (
        <div className="flex items-center justify-between px-4 py-2.5 border-b border-border shrink-0">
          {title ? (
            <Heading className="text-[11px] font-semibold uppercase tracking-wider text-text-secondary">
              {title}
            </Heading>
          ) : (
            <span />
          )}
          {meta && (
            <span className="font-mono text-[11px] text-text-muted tabular-nums">{meta}</span>
          )}
        </div>
      )}
      <div className={clsx(noPadding ? 'flex-1 min-h-0' : 'flex-1 min-h-0 p-4', bodyClassName)}>
        {children}
      </div>
    </div>
  );
}
