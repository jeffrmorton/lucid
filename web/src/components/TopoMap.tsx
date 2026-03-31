/** Topographic scalp map -- 2D interpolated view of EEG power distribution.
 *
 * Uses Canvas 2D with bilinear interpolation between electrode positions.
 * Electrode positions follow the 10-20 system.
 */

import { useCallback, useEffect, useRef } from 'react';

// 10-20 electrode positions normalized to [0, 1] (from top-down view of head)
const ELECTRODE_POSITIONS: Record<string, [number, number]> = {
  Fz: [0.5, 0.28],
  C3: [0.3, 0.5],
  Cz: [0.5, 0.5],
  C4: [0.7, 0.5],
  Pz: [0.5, 0.72],
  PO7: [0.25, 0.8],
  Oz: [0.5, 0.88],
  PO8: [0.75, 0.8],
};

interface TopoMapProps {
  channelValues?: number[];
  channelNames?: string[];
  size?: number;
}

/** Interpolate a value at (x, y) from sparse electrode data using inverse distance weighting. */
export function interpolateValue(
  x: number,
  y: number,
  positions: [number, number][],
  values: number[],
  power: number = 2,
): number {
  let weightSum = 0;
  let valueSum = 0;
  for (let i = 0; i < positions.length; i++) {
    const dx = x - positions[i][0];
    const dy = y - positions[i][1];
    const dist = Math.sqrt(dx * dx + dy * dy);
    if (dist < 0.001) return values[i];
    const w = 1 / dist ** power;
    weightSum += w;
    valueSum += w * values[i];
  }
  return weightSum > 0 ? valueSum / weightSum : 0;
}

/** Map a value to a color (blue -> green -> yellow -> red). */
export function valueToColor(value: number, min: number, max: number): string {
  const range = max - min || 1;
  const t = Math.max(0, Math.min(1, (value - min) / range));

  // Blue -> Cyan -> Green -> Yellow -> Red
  let r: number;
  let g: number;
  let b: number;
  if (t < 0.25) {
    r = 0;
    g = Math.round(t * 4 * 255);
    b = 255;
  } else if (t < 0.5) {
    r = 0;
    g = 255;
    b = Math.round((1 - (t - 0.25) * 4) * 255);
  } else if (t < 0.75) {
    r = Math.round((t - 0.5) * 4 * 255);
    g = 255;
    b = 0;
  } else {
    r = 255;
    g = Math.round((1 - (t - 0.75) * 4) * 255);
    b = 0;
  }
  return `rgb(${r},${g},${b})`;
}

/** Draw the topographic map on a canvas. */
export function drawTopoMap(
  ctx: CanvasRenderingContext2D,
  size: number,
  channelNames: string[],
  values: number[],
): void {
  const positions = channelNames.map((name) => ELECTRODE_POSITIONS[name] ?? [0.5, 0.5]);
  const min = Math.min(...values);
  const max = Math.max(...values);

  // Draw interpolated heatmap inside head circle
  const cx = size / 2;
  const cy = size / 2;
  const radius = size * 0.42;
  const step = 4; // pixel step for performance

  for (let py = 0; py < size; py += step) {
    for (let px = 0; px < size; px += step) {
      const dx = px - cx;
      const dy = py - cy;
      if (dx * dx + dy * dy > radius * radius) continue;

      const nx = px / size;
      const ny = py / size;
      const val = interpolateValue(nx, ny, positions, values);
      ctx.fillStyle = valueToColor(val, min, max);
      ctx.fillRect(px, py, step, step);
    }
  }

  // Draw head outline
  ctx.strokeStyle = '#888';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.arc(cx, cy, radius, 0, Math.PI * 2);
  ctx.stroke();

  // Draw nose indicator
  ctx.beginPath();
  ctx.moveTo(cx - 8, cy - radius);
  ctx.lineTo(cx, cy - radius - 12);
  ctx.lineTo(cx + 8, cy - radius);
  ctx.stroke();

  // Draw electrode positions
  for (let i = 0; i < channelNames.length; i++) {
    const [nx, ny] = positions[i];
    const ex = nx * size;
    const ey = ny * size;
    ctx.fillStyle = '#fff';
    ctx.beginPath();
    ctx.arc(ex, ey, 3, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#ccc';
    ctx.font = '10px monospace';
    ctx.fillText(channelNames[i], ex + 5, ey - 5);
  }
}

export function TopoMap({
  channelValues = [],
  channelNames = ['Fz', 'C3', 'Cz', 'C4', 'Pz', 'PO7', 'Oz', 'PO8'],
  size = 200,
}: TopoMapProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const render = useCallback(() => {
    const canvas = canvasRef.current;
    /* v8 ignore next */
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    /* v8 ignore next */
    if (!ctx) return;

    const values = channelValues.length > 0 ? channelValues : channelNames.map(() => 0);

    ctx.clearRect(0, 0, size, size);
    drawTopoMap(ctx, size, channelNames, values);
  }, [channelValues, channelNames, size]);

  useEffect(() => {
    render();
  }, [render]);

  return (
    <div className="bg-bg-panel rounded-lg p-3 flex flex-col items-center" data-testid="topo-map">
      <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-2">
        Topography
      </h3>
      <canvas
        ref={canvasRef}
        width={size}
        height={size}
        data-testid="topo-canvas"
        style={{ width: size, height: size }}
      />
    </div>
  );
}
