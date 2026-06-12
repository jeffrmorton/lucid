/** Real-time multi-channel EEG trace display using Canvas 2D.
 *
 * Renders every channel as a compact stacked lane that adapts to the panel
 * height, with a per-channel label in its palette color, faint per-second time
 * gridlines, and an auto-scaled waveform. The backing store is DPR-scaled and
 * re-rendered on container resize (see useCanvas).
 */

import { useCallback } from 'react';
import { useCanvas } from '../lib/canvas';
import { CHANNEL_NAMES } from '../lib/constants';
import { canvasColors, channelColors, themeFontMono, themeFontSans } from '../lib/theme-colors';
import { Panel } from './ui/Panel';

interface EEGTraceProps {
  channels: number;
  sampleRate: number;
  /** Rolling buffer of samples: array of per-channel arrays. */
  data?: number[][];
  /** Seconds of data to display. */
  displaySeconds?: number;
}

const LABEL_GUTTER = 34;

/** Draw multi-channel EEG traces, in CSS-pixel coordinates. */
export function drawTraces(
  ctx: CanvasRenderingContext2D,
  data: number[][],
  width: number,
  height: number,
  channels: number,
  displaySeconds: number,
  colors: string[],
): void {
  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = canvasColors.background();
  ctx.fillRect(0, 0, width, height);

  const hasData = data.some((ch) => ch && ch.length > 0);
  if (!hasData) {
    ctx.fillStyle = canvasColors.textMuted();
    ctx.font = themeFontSans(13);
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('Waiting for data…', width / 2, height / 2);
    ctx.textAlign = 'left';
    ctx.textBaseline = 'alphabetic';
    return;
  }

  const laneH = height / channels;
  const plotW = Math.max(1, width - LABEL_GUTTER);

  // Faint per-second time gridlines.
  ctx.strokeStyle = canvasColors.border();
  ctx.lineWidth = 1;
  for (let s = 0; s <= displaySeconds; s++) {
    const x = LABEL_GUTTER + (plotW * s) / displaySeconds;
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, height);
    ctx.stroke();
  }

  for (let ch = 0; ch < Math.min(channels, data.length); ch++) {
    const channelData = data[ch];
    if (!channelData || channelData.length === 0) continue;

    const yMid = ch * laneH + laneH / 2;
    const color = colors[ch % colors.length];

    let min = Number.POSITIVE_INFINITY;
    let max = Number.NEGATIVE_INFINITY;
    for (const v of channelData) {
      if (v < min) min = v;
      if (v > max) max = v;
    }
    const range = max - min || 1;
    const scale = (laneH * 0.7) / range;

    // Baseline.
    ctx.strokeStyle = canvasColors.border();
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(LABEL_GUTTER, yMid);
    ctx.lineTo(width, yMid);
    ctx.stroke();

    // Channel label chip in its palette color.
    ctx.fillStyle = color;
    ctx.font = themeFontMono(10);
    ctx.textBaseline = 'middle';
    ctx.fillText(CHANNEL_NAMES[ch] ?? `Ch${ch + 1}`, 4, yMid);
    ctx.textBaseline = 'alphabetic';

    // Waveform.
    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineWidth = 1;
    const step = plotW / Math.max(1, channelData.length - 1);
    for (let i = 0; i < channelData.length; i++) {
      const x = LABEL_GUTTER + i * step;
      const y = yMid - (channelData[i] - (min + max) / 2) * scale;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();
  }
}

export function EEGTrace({ channels, sampleRate, data, displaySeconds = 10 }: EEGTraceProps) {
  const draw = useCallback(
    (ctx: CanvasRenderingContext2D, width: number, height: number) => {
      const displayData = data ?? Array.from({ length: channels }, () => [] as number[]);
      drawTraces(ctx, displayData, width, height, channels, displaySeconds, channelColors());
    },
    [data, channels, displaySeconds],
  );
  const canvasRef = useCanvas(draw);

  return (
    <Panel
      title="EEG Traces"
      meta={`${channels}ch · ${sampleRate} SPS · ${displaySeconds}s`}
      noPadding
      className="h-full"
      testId="eeg-trace"
    >
      <canvas
        ref={canvasRef}
        data-testid="eeg-canvas"
        role="img"
        aria-label={`${channels}-channel EEG traces at ${sampleRate} samples per second over a ${displaySeconds} second window`}
        className="block w-full h-full"
      />
    </Panel>
  );
}
