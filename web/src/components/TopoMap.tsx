/** Topographic scalp map — 2D interpolated view of EEG power distribution.
 *
 * Inverse-distance-weighted interpolation between 10-20 electrode positions,
 * rendered with the shared viridis colormap and a min/max value legend. The
 * canvas fills its panel (square head centered, legend strip below), DPR-scaled
 * and resize-aware via useCanvas.
 */

import { useCallback } from 'react';
import { useCanvas } from '../lib/canvas';
import { viridisCss } from '../lib/colormap';
import { canvasColors, themeFontMono } from '../lib/theme-colors';
import { Panel } from './ui/Panel';

// 10-20 electrode positions normalized to [0, 1] (top-down view of head).
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

const DEFAULT_CHANNEL_NAMES = ['Fz', 'C3', 'Cz', 'C4', 'Pz', 'PO7', 'Oz', 'PO8'];
const LEGEND_H = 26;

interface TopoMapProps {
  channelValues?: number[];
  channelNames?: string[];
}

/** Interpolate a value at (x, y) from sparse electrode data using inverse distance weighting. */
export function interpolateValue(
  x: number,
  y: number,
  positions: [number, number][],
  values: number[],
  power = 2,
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

/** Draw the topographic map filling a (width × height) canvas in CSS pixels. */
export function drawTopoMap(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  channelNames: string[],
  values: number[],
  isEmpty: boolean,
): void {
  ctx.clearRect(0, 0, width, height);

  const positions = channelNames.map((name) => ELECTRODE_POSITIONS[name] ?? [0.5, 0.5]);
  const min = Math.min(...values);
  const max = Math.max(...values);

  const area = Math.max(20, Math.min(width, height - LEGEND_H));
  const hx0 = (width - area) / 2;
  const hy0 = 2;
  const cx = hx0 + area / 2;
  const cy = hy0 + area / 2;
  const radius = area * 0.42;

  if (!isEmpty) {
    const step = 3;
    for (let py = hy0; py < hy0 + area; py += step) {
      for (let px = hx0; px < hx0 + area; px += step) {
        const dx = px - cx;
        const dy = py - cy;
        if (dx * dx + dy * dy > radius * radius) continue;
        const nx = (px - hx0) / area;
        const ny = (py - hy0) / area;
        ctx.fillStyle = viridisCss(interpolateValue(nx, ny, positions, values), min, max);
        ctx.fillRect(px, py, step, step);
      }
    }
  }

  // Head outline.
  ctx.strokeStyle = canvasColors.border();
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.arc(cx, cy, radius, 0, Math.PI * 2);
  ctx.stroke();

  // Nose indicator.
  ctx.beginPath();
  ctx.moveTo(cx - 8, cy - radius);
  ctx.lineTo(cx, cy - radius - 10);
  ctx.lineTo(cx + 8, cy - radius);
  ctx.stroke();

  if (isEmpty) {
    ctx.fillStyle = canvasColors.textMuted();
    ctx.font = themeFontMono(12);
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('No data', cx, cy);
    ctx.textAlign = 'left';
    ctx.textBaseline = 'alphabetic';
    return;
  }

  // Electrodes.
  ctx.font = themeFontMono(10);
  for (let i = 0; i < channelNames.length; i++) {
    const ex = hx0 + positions[i][0] * area;
    const ey = hy0 + positions[i][1] * area;
    ctx.fillStyle = canvasColors.textPrimary();
    ctx.beginPath();
    ctx.arc(ex, ey, 3, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = canvasColors.textSecondary();
    ctx.fillText(channelNames[i], ex + 5, ey - 5);
  }

  // Colorbar legend with min/max labels.
  const barY = height - LEGEND_H + 6;
  const barX = hx0;
  const barW = area;
  const barH = 6;
  const segs = 40;
  for (let i = 0; i < segs; i++) {
    ctx.fillStyle = viridisCss(i / (segs - 1), 0, 1);
    ctx.fillRect(barX + (i * barW) / segs, barY, barW / segs + 1, barH);
  }
  ctx.fillStyle = canvasColors.textMuted();
  ctx.font = themeFontMono(9);
  ctx.textBaseline = 'top';
  ctx.fillText(min.toFixed(1), barX, barY + barH + 2);
  ctx.textAlign = 'right';
  ctx.fillText(`${max.toFixed(1)} µV²`, barX + barW, barY + barH + 2);
  ctx.textAlign = 'left';
  ctx.textBaseline = 'alphabetic';
}

export function TopoMap({
  channelValues = [],
  channelNames = DEFAULT_CHANNEL_NAMES,
}: TopoMapProps) {
  const isEmpty = channelValues.length === 0;
  const values = isEmpty ? channelNames.map(() => 0) : channelValues;

  const draw = useCallback(
    (ctx: CanvasRenderingContext2D, width: number, height: number) => {
      drawTopoMap(ctx, width, height, channelNames, values, isEmpty);
    },
    [channelNames, values, isEmpty],
  );
  const canvasRef = useCanvas(draw);

  return (
    <Panel title="Topography" noPadding className="h-full" testId="topo-map">
      <canvas
        ref={canvasRef}
        data-testid="topo-canvas"
        role="img"
        aria-label={`Topographic scalp map of alpha power across ${channelNames.length} electrodes (${channelNames.join(', ')})`}
        className="block w-full h-full"
      />
    </Panel>
  );
}
