/**
 * Perceptually-uniform viridis colormap shared by all heatmap visualizations
 * (Spectrogram + TopoMap) so the whole app uses one consistent, accessible ramp.
 *
 * 16-stop lookup table sampled from matplotlib's viridis, linearly interpolated.
 */

/** Viridis lookup table: dark purple -> blue -> teal -> green -> yellow. */
export const VIRIDIS: ReadonlyArray<readonly [number, number, number]> = [
  [68, 1, 84],
  [72, 33, 115],
  [67, 62, 133],
  [56, 88, 140],
  [45, 112, 142],
  [37, 133, 142],
  [30, 155, 138],
  [42, 176, 127],
  [82, 197, 105],
  [134, 213, 73],
  [194, 223, 35],
  [253, 231, 37],
  [253, 231, 37],
  [253, 231, 37],
  [253, 231, 37],
  [253, 231, 37],
];

/** Sample the viridis ramp at t in [0, 1], returning an [r, g, b] triple. */
export function viridis(t: number): [number, number, number] {
  const clamped = Math.max(0, Math.min(1, t));
  const scaled = clamped * (VIRIDIS.length - 1);
  const i = Math.floor(scaled);
  const frac = scaled - i;
  const c0 = VIRIDIS[i];
  const c1 = VIRIDIS[Math.min(i + 1, VIRIDIS.length - 1)];
  return [
    Math.round(c0[0] + (c1[0] - c0[0]) * frac),
    Math.round(c0[1] + (c1[1] - c0[1]) * frac),
    Math.round(c0[2] + (c1[2] - c0[2]) * frac),
  ];
}

/** Map a value within [min, max] onto the viridis ramp, returning [r, g, b]. */
export function viridisColor(value: number, min: number, max: number): [number, number, number] {
  const range = max - min || 1;
  return viridis((value - min) / range);
}

/** Map a value within [min, max] onto the viridis ramp, returning a CSS rgb() string. */
export function viridisCss(value: number, min: number, max: number): string {
  const [r, g, b] = viridisColor(value, min, max);
  return `rgb(${r},${g},${b})`;
}
