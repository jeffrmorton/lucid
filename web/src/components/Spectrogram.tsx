/** Spectrogram display — 2D heatmap rendered on Canvas 2D.
 *
 * Rows = time steps (older at top, newer at bottom), columns = frequency bins
 * (0–55 Hz, dB scale). Uses the shared viridis colormap with a stable color
 * domain anchored to the running peak (peak − dynamicRange) so historical rows
 * keep a constant color instead of flickering. Includes a frequency axis and a
 * dB colorbar legend. DPR-scaled and resize-aware via useCanvas.
 */

import { useCallback } from 'react';
import { useCanvas } from '../lib/canvas';
import { viridisColor, viridisCss } from '../lib/colormap';
import { canvasColors, themeFontMono, themeFontSans } from '../lib/theme-colors';
import { Panel } from './ui/Panel';

interface SpectrogramProps {
  /** 2D array: rows are time steps, columns are frequency bins. */
  data: number[][];
  /** Maximum time steps to display. */
  maxRows?: number;
  /** Highest frequency represented by the columns, in Hz. */
  maxFreqHz?: number;
  /** dB window below the running peak used for the color domain. */
  dynamicRange?: number;
}

const COLORBAR_W = 8;
const RIGHT_PAD = 30;
const BOTTOM_PAD = 14;

/** Draw a spectrogram heatmap, in CSS-pixel coordinates. */
export function drawSpectrogram(
  ctx: CanvasRenderingContext2D,
  data: number[][],
  width: number,
  height: number,
  maxFreqHz = 55,
  dynamicRange = 60,
): void {
  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = canvasColors.panel();
  ctx.fillRect(0, 0, width, height);

  if (data.length === 0) {
    ctx.fillStyle = canvasColors.textMuted();
    ctx.font = themeFontSans(13);
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('Waiting for data…', width / 2, height / 2);
    ctx.textAlign = 'left';
    ctx.textBaseline = 'alphabetic';
    return;
  }

  const plotW = Math.max(1, width - COLORBAR_W - RIGHT_PAD);
  const plotH = Math.max(1, height - BOTTOM_PAD);
  const numRows = data.length;
  const numCols = data[0].length;

  // Stable color domain anchored to the running peak.
  let max = Number.NEGATIVE_INFINITY;
  for (const row of data) {
    for (const v of row) {
      if (v > max) max = v;
    }
  }
  const min = max - dynamicRange;

  const cellW = plotW / numCols;
  const cellH = plotH / numRows;

  for (let r = 0; r < numRows; r++) {
    const y = r * cellH;
    for (let c = 0; c < numCols; c++) {
      const [rr, gg, bb] = viridisColor(data[r][c], min, max);
      ctx.fillStyle = `rgb(${rr},${gg},${bb})`;
      ctx.fillRect(c * cellW, y, Math.ceil(cellW), Math.ceil(cellH));
    }
  }

  // Frequency axis labels (Hz).
  ctx.fillStyle = canvasColors.textMuted();
  ctx.font = themeFontMono(9);
  ctx.textBaseline = 'top';
  for (let hz = 0; hz <= maxFreqHz; hz += 10) {
    const x = Math.min((hz / maxFreqHz) * plotW, plotW - 10);
    ctx.fillText(`${hz}`, x, plotH + 2);
  }
  ctx.fillText('Hz', plotW - 2, plotH + 2);

  // Time direction hints.
  ctx.fillStyle = canvasColors.textSecondary();
  ctx.fillText('↑ older', 4, 2);
  ctx.textBaseline = 'bottom';
  ctx.fillText('↓ newer', 4, plotH - 2);
  ctx.textBaseline = 'alphabetic';

  // dB colorbar legend.
  const barX = width - COLORBAR_W - 2;
  const segments = 32;
  for (let i = 0; i < segments; i++) {
    const t = i / (segments - 1);
    const segY = plotH - (t * plotH) / 1;
    ctx.fillStyle = viridisCss(t, 0, 1);
    ctx.fillRect(barX, segY - plotH / segments, COLORBAR_W, plotH / segments + 1);
  }
  ctx.fillStyle = canvasColors.textMuted();
  ctx.font = themeFontMono(9);
  ctx.textAlign = 'right';
  ctx.textBaseline = 'top';
  ctx.fillText(`${Math.round(max)}`, barX - 2, 2);
  ctx.textBaseline = 'bottom';
  ctx.fillText(`${Math.round(min)} dB`, barX - 2, plotH);
  ctx.textAlign = 'left';
  ctx.textBaseline = 'alphabetic';
}

export function Spectrogram({
  data,
  maxRows = 60,
  maxFreqHz = 55,
  dynamicRange = 60,
}: SpectrogramProps) {
  const displayData = data.length > maxRows ? data.slice(-maxRows) : data;
  const bins = displayData[0]?.length ?? 0;

  const draw = useCallback(
    (ctx: CanvasRenderingContext2D, width: number, height: number) => {
      drawSpectrogram(ctx, displayData, width, height, maxFreqHz, dynamicRange);
    },
    [displayData, maxFreqHz, dynamicRange],
  );
  const canvasRef = useCanvas(draw);

  return (
    <Panel
      title="Spectrogram"
      meta={`${displayData.length} × ${bins} bins`}
      noPadding
      className="h-full"
      testId="spectrogram"
    >
      <canvas
        ref={canvasRef}
        data-testid="spectrogram-canvas"
        role="img"
        aria-label={
          displayData.length === 0
            ? 'Spectrogram, waiting for data'
            : `Spectrogram, ${displayData.length} time steps by ${bins} frequency bins, 0 to ${maxFreqHz} hertz`
        }
        className="block w-full h-full"
      />
    </Panel>
  );
}
