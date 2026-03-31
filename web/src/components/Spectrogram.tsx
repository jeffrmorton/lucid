/** Spectrogram display -- 2D heatmap rendered on Canvas.
 *
 * Rows = time steps (newest at bottom), columns = frequency/band bins.
 * Color maps value using a viridis-inspired palette.
 */

import { useCallback, useEffect, useRef } from 'react';

interface SpectrogramProps {
  /** 2D array: rows are time steps, columns are frequency/band bins. */
  data: number[][];
  /** Maximum time steps to display. */
  maxRows?: number;
  /** Width in pixels. */
  width?: number;
  /** Height in pixels. */
  height?: number;
}

/** Map a value to a color (viridis-inspired: dark purple -> blue -> teal -> green -> yellow). */
export function valueToColor(value: number, min: number, max: number): [number, number, number] {
  const range = max - min || 1;
  const t = Math.max(0, Math.min(1, (value - min) / range));
  // Viridis-inspired: dark purple -> blue -> teal -> green -> yellow
  const r = Math.round(Math.min(255, t < 0.5 ? t * 2 * 80 : 80 + (t - 0.5) * 2 * 175));
  const g = Math.round(Math.min(255, t < 0.3 ? t * 3.3 * 30 : 30 + (t - 0.3) * 1.43 * 225));
  const b = Math.round(Math.min(255, t < 0.5 ? 100 + t * 2 * 100 : 200 - (t - 0.5) * 2 * 200));
  return [r, g, b];
}

/** Draw a spectrogram heatmap on a canvas. */
export function drawSpectrogram(
  ctx: CanvasRenderingContext2D,
  data: number[][],
  width: number,
  height: number,
): void {
  if (data.length === 0) {
    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, width, height);
    ctx.fillStyle = '#666';
    ctx.font = '14px sans-serif';
    ctx.fillText('Waiting for data...', width / 2 - 60, height / 2);
    return;
  }

  const numRows = data.length;
  const numCols = data[0].length;

  // Find global min/max for color scaling
  let min = Number.POSITIVE_INFINITY;
  let max = Number.NEGATIVE_INFINITY;
  for (const row of data) {
    for (const v of row) {
      if (v < min) min = v;
      if (v > max) max = v;
    }
  }

  const cellW = width / numCols;
  const cellH = height / numRows;

  const imageData = ctx.createImageData(width, height);
  const pixels = imageData.data;

  for (let row = 0; row < numRows; row++) {
    const y0 = Math.floor(row * cellH);
    const y1 = Math.floor((row + 1) * cellH);
    for (let col = 0; col < numCols; col++) {
      const x0 = Math.floor(col * cellW);
      const x1 = Math.floor((col + 1) * cellW);
      const [r, g, b] = valueToColor(data[row][col], min, max);

      for (let y = y0; y < y1 && y < height; y++) {
        for (let x = x0; x < x1 && x < width; x++) {
          const idx = (y * width + x) * 4;
          pixels[idx] = r;
          pixels[idx + 1] = g;
          pixels[idx + 2] = b;
          pixels[idx + 3] = 255;
        }
      }
    }
  }

  ctx.putImageData(imageData, 0, 0);

  // Draw time axis labels (data scrolls top=older, bottom=newer)
  ctx.fillStyle = 'rgba(255,255,255,0.5)';
  ctx.font = '10px monospace';
  ctx.fillText('\u2191 older', 4, 12);
  ctx.fillText('newer', 4, height - 4);
}

export function Spectrogram({ data, maxRows = 60, width = 800, height = 200 }: SpectrogramProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const displayData = data.length > maxRows ? data.slice(-maxRows) : data;

  const render = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    drawSpectrogram(ctx, displayData, canvas.width, canvas.height);
  }, [displayData]);

  useEffect(() => {
    render();
  }, [render]);

  return (
    <div className="bg-bg-panel rounded-lg p-3 h-full flex flex-col" data-testid="spectrogram">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider">
          Spectrogram
        </h3>
        <span className="text-[10px] font-mono text-text-muted">
          {displayData.length} time steps &times; {displayData[0]?.length ?? 0} bins
        </span>
      </div>
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        data-testid="spectrogram-canvas"
        className="w-full flex-1 rounded"
      />
    </div>
  );
}
