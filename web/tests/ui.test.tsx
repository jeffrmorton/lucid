import { fireEvent, render, screen } from '@testing-library/react';
import { Activity } from 'lucide-react';
import { describe, expect, it, vi } from 'vitest';
import { Button } from '../src/components/ui/Button';
import { EmptyState } from '../src/components/ui/EmptyState';
import { Panel } from '../src/components/ui/Panel';
import { Select } from '../src/components/ui/Select';
import { StatusChip } from '../src/components/ui/StatusChip';

describe('Panel', () => {
  it('renders a header with title (h2) and meta', () => {
    render(
      <Panel title="EEG Traces" meta="8ch">
        body
      </Panel>,
    );
    const heading = screen.getByRole('heading', { level: 2, name: 'EEG Traces' });
    expect(heading).toBeInTheDocument();
    expect(screen.getByText('8ch')).toBeInTheDocument();
    expect(screen.getByText('body')).toBeInTheDocument();
  });

  it('renders without a header when no title or meta', () => {
    render(<Panel>just body</Panel>);
    expect(screen.queryByRole('heading')).not.toBeInTheDocument();
    expect(screen.getByText('just body')).toBeInTheDocument();
  });

  it('renders meta-only header (no title)', () => {
    render(<Panel meta="60 × 56 bins">x</Panel>);
    expect(screen.queryByRole('heading')).not.toBeInTheDocument();
    expect(screen.getByText('60 × 56 bins')).toBeInTheDocument();
  });

  it('renders title-only header', () => {
    render(<Panel title="Device">x</Panel>);
    expect(screen.getByRole('heading', { name: 'Device' })).toBeInTheDocument();
  });

  it('supports an h3 heading level, noPadding body, and custom testId', () => {
    render(
      <Panel title="Sub" headingLevel="h3" noPadding testId="custom-panel">
        canvas
      </Panel>,
    );
    expect(screen.getByRole('heading', { level: 3, name: 'Sub' })).toBeInTheDocument();
    expect(screen.getByTestId('custom-panel')).toBeInTheDocument();
  });
});

describe('StatusChip', () => {
  it('renders each variant', () => {
    for (const variant of ['success', 'warning', 'danger', 'neutral'] as const) {
      const { unmount } = render(<StatusChip variant={variant} label={variant} />);
      expect(screen.getByText(variant)).toBeInTheDocument();
      unmount();
    }
  });

  it('pulses the dot when requested', () => {
    render(<StatusChip variant="success" label="Live" pulse />);
    expect(screen.getByTestId('status-chip').querySelector('.animate-pulse')).toBeTruthy();
  });

  it('does not pulse by default', () => {
    render(<StatusChip variant="neutral" label="Idle" className="extra" />);
    const chip = screen.getByTestId('status-chip');
    expect(chip.querySelector('.animate-pulse')).toBeNull();
    expect(chip).toHaveClass('extra');
  });
});

describe('Button', () => {
  it('renders the three variants and defaults to a button type', () => {
    const { rerender } = render(<Button variant="primary">P</Button>);
    expect(screen.getByRole('button', { name: 'P' })).toHaveAttribute('type', 'button');
    rerender(<Button variant="ghost">G</Button>);
    expect(screen.getByRole('button', { name: 'G' })).toBeInTheDocument();
    rerender(<Button variant="danger">D</Button>);
    expect(screen.getByRole('button', { name: 'D' })).toBeInTheDocument();
  });

  it('uses the default primary variant and forwards an explicit type', () => {
    render(<Button type="submit">S</Button>);
    expect(screen.getByRole('button', { name: 'S' })).toHaveAttribute('type', 'submit');
  });

  it('fires onClick', () => {
    const onClick = vi.fn();
    render(<Button onClick={onClick}>Go</Button>);
    fireEvent.click(screen.getByRole('button', { name: 'Go' }));
    expect(onClick).toHaveBeenCalledOnce();
  });
});

describe('EmptyState', () => {
  it('renders glyph, label and hint', () => {
    render(<EmptyState icon={Activity} label="Nothing here" hint="Try again" className="mt-2" />);
    expect(screen.getByText('Nothing here')).toBeInTheDocument();
    expect(screen.getByText('Try again')).toBeInTheDocument();
    expect(screen.getByTestId('empty-state')).toHaveClass('mt-2');
  });

  it('renders without a hint or className', () => {
    render(<EmptyState icon={Activity} label="Empty" />);
    expect(screen.getByText('Empty')).toBeInTheDocument();
    expect(screen.getByTestId('empty-state')).toBeInTheDocument();
  });
});

describe('Select', () => {
  const options = [
    { value: 'a', label: 'Alpha' },
    { value: 'b', label: 'Beta' },
    { value: 'c', label: 'Gamma' },
  ];

  function setup(value = 'a', onChange = vi.fn(), extra: Partial<{ disabled: boolean }> = {}) {
    render(
      <Select value={value} options={options} onChange={onChange} label="Pick" {...extra} />,
    );
    return { onChange };
  }

  it('shows the selected option label and is collapsed by default', () => {
    setup();
    expect(screen.getByTestId('select-trigger')).toHaveTextContent('Alpha');
    expect(screen.getByTestId('select-trigger')).toHaveAttribute('aria-expanded', 'false');
    expect(screen.queryByTestId('select-listbox')).not.toBeInTheDocument();
  });

  it('falls back to the first option when value is unknown', () => {
    setup('zzz');
    expect(screen.getByTestId('select-trigger')).toHaveTextContent('Alpha');
  });

  it('opens and closes on trigger click', () => {
    setup();
    const trigger = screen.getByTestId('select-trigger');
    fireEvent.click(trigger);
    expect(trigger).toHaveAttribute('aria-expanded', 'true');
    expect(trigger).toHaveAttribute('aria-activedescendant');
    fireEvent.click(trigger);
    expect(trigger).toHaveAttribute('aria-expanded', 'false');
  });

  it('selects an option on click', () => {
    const { onChange } = setup();
    fireEvent.click(screen.getByTestId('select-trigger'));
    fireEvent.click(screen.getByTestId('select-option-b'));
    expect(onChange).toHaveBeenCalledWith('b');
    expect(screen.queryByTestId('select-listbox')).not.toBeInTheDocument();
  });

  it('opens with ArrowDown and Enter, ignores other keys while closed', () => {
    setup();
    const trigger = screen.getByTestId('select-trigger');
    fireEvent.keyDown(trigger, { key: 'x' });
    expect(trigger).toHaveAttribute('aria-expanded', 'false');
    fireEvent.keyDown(trigger, { key: 'ArrowDown' });
    expect(trigger).toHaveAttribute('aria-expanded', 'true');
    fireEvent.click(trigger); // close
    fireEvent.keyDown(trigger, { key: 'Enter' });
    expect(trigger).toHaveAttribute('aria-expanded', 'true');
  });

  it('navigates with arrows (clamped) and selects with Enter', () => {
    const { onChange } = setup();
    const trigger = screen.getByTestId('select-trigger');
    fireEvent.keyDown(trigger, { key: 'ArrowDown' }); // open, active=0
    fireEvent.keyDown(trigger, { key: 'ArrowUp' }); // clamp at 0
    fireEvent.keyDown(trigger, { key: 'ArrowDown' }); // 1
    fireEvent.keyDown(trigger, { key: 'ArrowDown' }); // 2
    fireEvent.keyDown(trigger, { key: 'ArrowDown' }); // clamp at 2
    fireEvent.keyDown(trigger, { key: 'Enter' });
    expect(onChange).toHaveBeenCalledWith('c');
  });

  it('closes on Escape and ignores unrelated keys while open', () => {
    setup();
    const trigger = screen.getByTestId('select-trigger');
    fireEvent.keyDown(trigger, { key: 'ArrowDown' });
    fireEvent.keyDown(trigger, { key: 'q' });
    expect(trigger).toHaveAttribute('aria-expanded', 'true');
    fireEvent.keyDown(trigger, { key: 'Escape' });
    expect(trigger).toHaveAttribute('aria-expanded', 'false');
  });

  it('sets the active option on mouse enter', () => {
    setup();
    fireEvent.click(screen.getByTestId('select-trigger'));
    fireEvent.mouseEnter(screen.getByTestId('select-option-c'));
    expect(screen.getByTestId('select-option-c')).toHaveClass('bg-accent/15');
  });

  it('closes on outside mousedown but stays open on inside mousedown', () => {
    setup();
    const trigger = screen.getByTestId('select-trigger');
    fireEvent.click(trigger);
    fireEvent.mouseDown(screen.getByTestId('select-option-a'));
    expect(trigger).toHaveAttribute('aria-expanded', 'true');
    fireEvent.mouseDown(document.body);
    expect(trigger).toHaveAttribute('aria-expanded', 'false');
  });

  it('can be disabled and accepts a custom id', () => {
    render(
      <Select value="a" options={options} onChange={vi.fn()} disabled id="my-select" />,
    );
    const trigger = screen.getByTestId('select-trigger');
    expect(trigger).toBeDisabled();
    expect(trigger).toHaveAttribute('id', 'my-select');
  });
});
