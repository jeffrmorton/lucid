/**
 * Accessible custom listbox replacing the native <select>.
 *
 * Keyboard: ArrowDown/ArrowUp move the active option, Enter selects, Escape
 * closes. Exposes aria-haspopup/aria-expanded on the trigger and role=listbox
 * with aria-activedescendant + role=option/aria-selected on the popover.
 * Requires a non-empty `options` array.
 */

import clsx from 'clsx';
import { ChevronDown } from 'lucide-react';
import { useEffect, useId, useRef, useState } from 'react';

export interface SelectOption {
  value: string;
  label: string;
}

interface SelectProps {
  value: string;
  options: SelectOption[];
  onChange: (value: string) => void;
  disabled?: boolean;
  /** Accessible name for the control. */
  label?: string;
  id?: string;
}

export function Select({ value, options, onChange, disabled = false, label, id }: SelectProps) {
  const reactId = useId();
  const baseId = id ?? reactId;
  const [open, setOpen] = useState(false);
  const selectedIndex = Math.max(
    0,
    options.findIndex((o) => o.value === value),
  );
  const [activeIndex, setActiveIndex] = useState(selectedIndex);
  const containerRef = useRef<HTMLDivElement>(null);
  const selected = options[selectedIndex];

  useEffect(() => {
    if (!open) return;
    const onDocMouseDown = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', onDocMouseDown);
    return () => document.removeEventListener('mousedown', onDocMouseDown);
  }, [open]);

  const openList = () => {
    setActiveIndex(selectedIndex);
    setOpen(true);
  };

  const choose = (index: number) => {
    onChange(options[index].value);
    setOpen(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!open) {
      if (e.key === 'ArrowDown' || e.key === 'Enter') {
        e.preventDefault();
        openList();
      }
      return;
    }
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setActiveIndex((i) => Math.min(i + 1, options.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActiveIndex((i) => Math.max(i - 1, 0));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      choose(activeIndex);
    } else if (e.key === 'Escape') {
      e.preventDefault();
      setOpen(false);
    }
  };

  return (
    <div ref={containerRef} className="relative">
      <button
        type="button"
        id={baseId}
        data-testid="select-trigger"
        disabled={disabled}
        role="combobox"
        aria-controls={`${baseId}-listbox`}
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-activedescendant={open ? `${baseId}-opt-${activeIndex}` : undefined}
        aria-label={label}
        onClick={() => (open ? setOpen(false) : openList())}
        onKeyDown={handleKeyDown}
        className={clsx(
          'w-full flex items-center justify-between gap-2 rounded-md px-3 py-1.5 text-sm',
          'bg-bg-raised border border-border-strong text-text-primary',
          'hover:border-accent/50 transition-colors',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-bg',
          'disabled:opacity-50 disabled:pointer-events-none',
        )}
      >
        <span className="truncate">{selected.label}</span>
        <ChevronDown
          className={clsx('w-4 h-4 text-text-muted transition-transform', open && 'rotate-180')}
          aria-hidden={true}
        />
      </button>
      {open && (
        <div
          id={`${baseId}-listbox`}
          role="listbox"
          aria-label={label}
          data-testid="select-listbox"
          className="absolute z-20 mt-1 w-full max-h-60 overflow-auto rounded-md border border-border-strong bg-bg-raised py-1 shadow-lg"
        >
          {options.map((opt, i) => (
            // biome-ignore lint/a11y/useKeyWithClickEvents: option selection is keyboard-driven via the combobox trigger + aria-activedescendant
            <div
              key={opt.value}
              id={`${baseId}-opt-${i}`}
              role="option"
              tabIndex={-1}
              aria-selected={opt.value === value}
              data-testid={`select-option-${opt.value}`}
              onMouseEnter={() => setActiveIndex(i)}
              onClick={() => choose(i)}
              className={clsx(
                'cursor-pointer px-3 py-1.5 text-sm',
                i === activeIndex ? 'bg-accent/15 text-text-primary' : 'text-text-secondary',
              )}
            >
              {opt.label}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
