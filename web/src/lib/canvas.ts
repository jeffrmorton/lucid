/**
 * Shared Canvas 2D plumbing: device-pixel-ratio backing-store scaling and
 * container-resize handling, so every visualization renders crisp on HiDPI
 * displays and re-renders when its resizable panel is dragged.
 */

import { useEffect, useRef } from 'react';

/** Measure an element's CSS box, clamped to at least 1px in each dimension. */
export function measureBox(el: HTMLElement): { width: number; height: number } {
  const rect = el.getBoundingClientRect();
  return {
    width: Math.max(1, Math.round(rect.width)),
    height: Math.max(1, Math.round(rect.height)),
  };
}

/**
 * Size a canvas's backing store to cssWidth/cssHeight times the device pixel
 * ratio and scale the context so all drawing happens in CSS pixels. Returns the
 * prepared context, or null if a 2D context is unavailable (e.g. jsdom).
 */
export function configureBackingStore(
  canvas: HTMLCanvasElement,
  cssWidth: number,
  cssHeight: number,
  dpr: number,
): CanvasRenderingContext2D | null {
  const ctx = canvas.getContext('2d');
  if (!ctx) return null;
  canvas.width = Math.max(1, Math.round(cssWidth * dpr));
  canvas.height = Math.max(1, Math.round(cssHeight * dpr));
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  return ctx;
}

/** A canvas draw callback receiving CSS-pixel dimensions. */
export type CanvasDraw = (ctx: CanvasRenderingContext2D, width: number, height: number) => void;

/**
 * Hook that wires a canvas to fill its parent element: it configures the DPR
 * backing store, invokes `draw` in CSS-pixel coordinates, and re-runs on both
 * data changes (when `draw` identity changes) and container resize.
 *
 * Pass a `useCallback`-memoized `draw` so the effect re-renders on data updates.
 */
export function useCanvas(draw: CanvasDraw) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    /* v8 ignore next */
    if (!canvas) return;
    const parent = canvas.parentElement;
    /* v8 ignore next */
    if (!parent) return;

    const render = () => {
      const { width, height } = measureBox(parent);
      const dpr = window.devicePixelRatio || 1;
      const ctx = configureBackingStore(canvas, width, height, dpr);
      if (!ctx) return;
      draw(ctx, width, height);
    };

    render();
    const observer = new ResizeObserver(render);
    observer.observe(parent);
    return () => observer.disconnect();
  }, [draw]);

  return canvasRef;
}
