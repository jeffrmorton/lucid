import { act, render } from '@testing-library/react';
import { createElement, useCallback } from 'react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { configureBackingStore, measureBox, useCanvas } from '../src/lib/canvas';
import { VIRIDIS, viridis, viridisColor, viridisCss } from '../src/lib/colormap';
import {
  canvasColors,
  channelColors,
  themeColor,
  themeFontMono,
  themeFontSans,
} from '../src/lib/theme-colors';
import { buildTraceData } from '../src/lib/trace-sim';

function makeCtx(): CanvasRenderingContext2D {
  return {
    setTransform: vi.fn(),
    clearRect: vi.fn(),
    fillRect: vi.fn(),
    fillText: vi.fn(),
    beginPath: vi.fn(),
    moveTo: vi.fn(),
    lineTo: vi.fn(),
    stroke: vi.fn(),
    arc: vi.fn(),
    fill: vi.fn(),
    fillStyle: '',
    strokeStyle: '',
    lineWidth: 0,
    font: '',
    textAlign: '',
    textBaseline: '',
  } as unknown as CanvasRenderingContext2D;
}

describe('theme-colors', () => {
  afterEach(() => {
    document.documentElement.style.removeProperty('--test-token');
    vi.restoreAllMocks();
  });

  it('returns the fallback when the property is unset (jsdom)', () => {
    expect(themeColor('--definitely-missing', '#abcdef')).toBe('#abcdef');
  });

  it('returns the resolved CSS variable value when present', () => {
    document.documentElement.style.setProperty('--test-token', '#123456');
    expect(themeColor('--test-token', '#000000')).toBe('#123456');
  });

  it('builds mono/sans font strings with default and custom sizes', () => {
    expect(themeFontMono()).toContain('11px');
    expect(themeFontMono(20)).toContain('20px');
    expect(themeFontSans()).toContain('14px');
    expect(themeFontSans(9)).toContain('9px');
  });

  it('exposes an 8-color channel palette and canvas chrome colors', () => {
    expect(channelColors()).toHaveLength(8);
    expect(canvasColors.background()).toMatch(/^#/);
    expect(canvasColors.panel()).toMatch(/^#/);
    expect(canvasColors.border()).toBeTruthy();
    expect(canvasColors.textPrimary()).toMatch(/^#/);
    expect(canvasColors.textSecondary()).toMatch(/^#/);
    expect(canvasColors.textMuted()).toMatch(/^#/);
  });
});

describe('colormap', () => {
  it('has a 16-stop lookup table', () => {
    expect(VIRIDIS).toHaveLength(16);
  });

  it('samples endpoints and midpoint', () => {
    expect(viridis(0)).toEqual([68, 1, 84]);
    expect(viridis(1)).toEqual([253, 231, 37]);
    const mid = viridis(0.5);
    expect(mid).toHaveLength(3);
  });

  it('clamps out-of-range t', () => {
    expect(viridis(-5)).toEqual([68, 1, 84]);
    expect(viridis(5)).toEqual([253, 231, 37]);
  });

  it('maps value ranges including a zero range', () => {
    expect(viridisColor(0, 0, 10)).toEqual([68, 1, 84]);
    expect(viridisColor(5, 5, 5)).toHaveLength(3);
    expect(viridisCss(10, 0, 10)).toBe('rgb(253,231,37)');
  });
});

describe('canvas helpers', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('measureBox clamps to at least 1px', () => {
    const el = document.createElement('div');
    expect(measureBox(el)).toEqual({ width: 1, height: 1 });
  });

  it('configureBackingStore returns null when no 2D context', () => {
    const canvas = document.createElement('canvas');
    vi.spyOn(canvas, 'getContext').mockReturnValue(null);
    expect(configureBackingStore(canvas, 100, 50, 2)).toBeNull();
  });

  it('configureBackingStore scales the backing store by dpr', () => {
    const canvas = document.createElement('canvas');
    const ctx = makeCtx();
    vi.spyOn(canvas, 'getContext').mockReturnValue(ctx as unknown as RenderingContext);
    const result = configureBackingStore(canvas, 100, 50, 2);
    expect(result).toBe(ctx);
    expect(canvas.width).toBe(200);
    expect(canvas.height).toBe(100);
    expect(ctx.setTransform).toHaveBeenCalledWith(2, 0, 0, 2, 0, 0);
  });
});

function Harness({ draw }: { draw: (c: CanvasRenderingContext2D, w: number, h: number) => void }) {
  const stable = useCallback(draw, [draw]);
  const ref = useCanvas(stable);
  return createElement('div', null, createElement('canvas', { ref, 'data-testid': 'c' }));
}

describe('useCanvas', () => {
  afterEach(() => {
    vi.restoreAllMocks();
    Object.defineProperty(window, 'devicePixelRatio', { value: 1, configurable: true });
  });

  it('renders into the canvas when a 2D context is available (dpr fallback)', () => {
    const ctx = makeCtx();
    Object.defineProperty(window, 'devicePixelRatio', { value: undefined, configurable: true });
    vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue(
      ctx as unknown as RenderingContext,
    );
    const draw = vi.fn();
    render(createElement(Harness, { draw }));
    expect(draw).toHaveBeenCalledTimes(1);
    expect(draw.mock.calls[0][0]).toBe(ctx);
    expect(ctx.setTransform).toHaveBeenCalledWith(1, 0, 0, 1, 0, 0);
  });

  it('honors devicePixelRatio when set', () => {
    const ctx = makeCtx();
    Object.defineProperty(window, 'devicePixelRatio', { value: 3, configurable: true });
    vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue(
      ctx as unknown as RenderingContext,
    );
    render(createElement(Harness, { draw: vi.fn() }));
    expect(ctx.setTransform).toHaveBeenCalledWith(3, 0, 0, 3, 0, 0);
  });

  it('skips drawing when no 2D context is available', () => {
    vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue(null);
    const draw = vi.fn();
    render(createElement(Harness, { draw }));
    expect(draw).not.toHaveBeenCalled();
  });

  it('re-renders on resize and disconnects on unmount', () => {
    const ctx = makeCtx();
    vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue(
      ctx as unknown as RenderingContext,
    );
    const observers: { cb: ResizeObserverCallback; observe: ReturnType<typeof vi.fn>; disconnect: ReturnType<typeof vi.fn> }[] = [];
    const realRO = globalThis.ResizeObserver;
    class RO {
      cb: ResizeObserverCallback;
      observe = vi.fn();
      unobserve = vi.fn();
      disconnect = vi.fn();
      constructor(cb: ResizeObserverCallback) {
        this.cb = cb;
        observers.push(this);
      }
    }
    globalThis.ResizeObserver = RO as unknown as typeof ResizeObserver;
    try {
      const draw = vi.fn();
      const { unmount } = render(createElement(Harness, { draw }));
      expect(draw).toHaveBeenCalledTimes(1);
      expect(observers[0].observe).toHaveBeenCalled();
      act(() => {
        observers[0].cb([], observers[0] as unknown as ResizeObserver);
      });
      expect(draw).toHaveBeenCalledTimes(2);
      unmount();
      expect(observers[0].disconnect).toHaveBeenCalled();
    } finally {
      globalThis.ResizeObserver = realRO;
    }
  });
});

describe('buildTraceData', () => {
  it('produces deterministic samples with an injected rng', () => {
    const data = buildTraceData([1, 2], 2, 4, () => 0.5);
    expect(data).toHaveLength(2);
    expect(data[0]).toHaveLength(4);
  });

  it('defaults missing channel alpha to 0 (flat trace with neutral rng)', () => {
    const data = buildTraceData([], 2, 3, () => 0.5);
    for (const channel of data) {
      for (const sample of channel) {
        expect(sample).toBeCloseTo(0);
      }
    }
  });

  it('uses Math.random and a default sample count by default', () => {
    const data = buildTraceData([1], 1);
    expect(data[0]).toHaveLength(250);
  });
});
