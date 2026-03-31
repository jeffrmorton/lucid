/** Real-time multi-channel EEG trace display using Canvas 2D.
 *
 * Renders scrolling waveforms for each channel with auto-scaling.
 * Uses requestAnimationFrame for smooth 60fps rendering.
 */

import { useCallback, useEffect, useRef } from 'react';
import { CHANNEL_NAMES } from '../lib/constants';

interface EEGTraceProps {
  channels: number;
  sampleRate: number;
  /** Rolling buffer of samples: array of per-channel arrays */
  data?: number[][];
  /** Seconds of data to display */
  displaySeconds?: number;
  /** Height per channel in pixels */
  channelHeight?: number;
}

/** Draw multi-channel EEG traces on a canvas */
export function drawTraces(
  ctx: CanvasRenderingContext2D,
  data: number[][],
  width: number,
  height: number,
  channels: number,
  channelHeight: number,
): void {
  ctx.clearRect(0, 0, width, height);

  const colors = [
    '#6366f1',
    '#8b5cf6',
    '#06b6d4',
    '#22c55e',
    '#f59e0b',
    '#ef4444',
    '#ec4899',
    '#14b8a6',
  ];

  for (let ch = 0; ch < Math.min(channels, data.length); ch++) {
    const channelData = data[ch];
    if (!channelData || channelData.length === 0) continue;

    const yOffset = ch * channelHeight + channelHeight / 2;
    const color = colors[ch % colors.length];

    // Auto-scale: find min/max for this channel
    let min = Infinity;
    let max = -Infinity;
    for (const v of channelData) {
      if (v < min) min = v;
      if (v > max) max = v;
    }
    const range = max - min || 1;
    const scale = (channelHeight * 0.8) / range;

    // Draw channel label
    ctx.fillStyle = color;
    ctx.font = '11px monospace';
    const label = CHANNEL_NAMES[ch] ?? `Ch${ch + 1}`;
    ctx.fillText(label, 4, yOffset - channelHeight / 2 + 14);

    // Draw trace
    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineWidth = 1;

    const step = width / Math.max(1, channelData.length - 1);
    for (let i = 0; i < channelData.length; i++) {
      const x = i * step;
      const y = yOffset - (channelData[i] - (min + max) / 2) * scale;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();

    // Draw baseline
    ctx.strokeStyle = `${color}33`;
    ctx.lineWidth = 0.5;
    ctx.beginPath();
    ctx.moveTo(0, yOffset);
    ctx.lineTo(width, yOffset);
    ctx.stroke();
  }
}

export function EEGTrace({
  channels,
  sampleRate,
  data,
  displaySeconds = 10,
  channelHeight = 60,
}: EEGTraceProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const render = useCallback(() => {
    const canvas = canvasRef.current;
    /* v8 ignore next */
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    /* v8 ignore next */
    if (!ctx) return;

    const displayData = data ?? Array.from({ length: channels }, () => [] as number[]);
    drawTraces(ctx, displayData, canvas.width, canvas.height, channels, channelHeight);
  }, [data, channels, channelHeight]);

  useEffect(() => {
    render();
  }, [render]);

  const totalHeight = channels * channelHeight;

  return (
    <div className="bg-bg-panel rounded-lg p-3 h-full flex flex-col" data-testid="eeg-trace">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider">
          EEG Traces
        </h3>
        <span className="text-[10px] font-mono text-text-muted">
          {channels}ch &middot; {sampleRate} SPS &middot; {displaySeconds}s
        </span>
      </div>
      <canvas
        ref={canvasRef}
        width={800}
        height={totalHeight}
        data-testid="eeg-canvas"
        className="w-full flex-1 rounded"
        style={{ background: '#08080e' }}
      />
    </div>
  );
}
