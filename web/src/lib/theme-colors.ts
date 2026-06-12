/**
 * Theme color/font helpers for Canvas 2D drawing.
 *
 * Canvas rendering cannot use Tailwind classes, so these helpers read the
 * design tokens (@theme custom properties in index.css) off the document root
 * via getComputedStyle. In jsdom there is no CSS engine, so getPropertyValue
 * returns '' — the fallback hex/font string is used instead, keeping draw code
 * deterministic under test while tracking the live theme in the browser.
 */

/**
 * Read a CSS custom property from :root, falling back when unavailable.
 * In jsdom there is no CSS engine so getPropertyValue returns '' → fallback.
 */
export function themeColor(name: string, fallback: string): string {
  const value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  return value === '' ? fallback : value;
}

/** Build a canvas ctx.font string using the JetBrains Mono design token. */
export function themeFontMono(size = 11): string {
  return `${size}px ${themeColor('--font-mono', "'JetBrains Mono', ui-monospace, monospace")}`;
}

/** Build a canvas ctx.font string using the Inter design token. */
export function themeFontSans(size = 14): string {
  return `${size}px ${themeColor('--font-sans', "'Inter', system-ui, sans-serif")}`;
}

/** Eight-channel trace palette derived from the @theme tokens (band colors + accents). */
export function channelColors(): string[] {
  return [
    themeColor('--color-band-delta', '#818cf8'),
    themeColor('--color-band-theta', '#a78bfa'),
    themeColor('--color-band-alpha', '#22d3ee'),
    themeColor('--color-band-beta', '#4ade80'),
    themeColor('--color-band-gamma', '#fbbf24'),
    themeColor('--color-accent', '#6366f1'),
    themeColor('--color-danger', '#f87171'),
    themeColor('--color-accent-2', '#22d3ee'),
  ];
}

/** Common canvas chrome colors pulled from the design tokens. */
export const canvasColors = {
  background: () => themeColor('--color-bg', '#0a0a0f'),
  panel: () => themeColor('--color-bg-panel', '#15151f'),
  border: () => themeColor('--color-border-strong', 'rgba(148,163,184,0.22)'),
  textPrimary: () => themeColor('--color-text-primary', '#e7e9ee'),
  textSecondary: () => themeColor('--color-text-secondary', '#9aa1b2'),
  textMuted: () => themeColor('--color-text-muted', '#5d6371'),
};
