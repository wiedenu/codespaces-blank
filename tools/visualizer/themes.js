// Themes are data, not code. A theme carries a palette *and* render character
// (glow, trail length, peak decay, whether bars draw as solid or as stacked
// blocks), but never geometry — that belongs to the modes. Keeping the two
// independent means N themes x M modes for the cost of N + M.

function hexToRgb(h) {
  const n = parseInt(h.slice(1), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

export const THEMES = [
  {
    id: 'classic',
    name: 'Classic Green',
    bg: '#000000',
    ramp: ['#00300f', '#00d13c', '#8ce800', '#ffd400', '#ff3b1f'],
    glow: 0.15,
    trail: 1,        // full clear each frame: hard edges, no smear
    decay: 0.90,
    lineWidth: 2,
    blocks: true,    // stacked segments, the 1997 look
    scanlines: false,
    defaultMode: 'bars',
    chrome: { fg: '#00d13c', dim: '#1f6b34', accent: '#ffd400' },
  },
  {
    id: 'midnight',
    name: 'Midnight',
    bg: '#070a18',
    ramp: ['#123a6b', '#1fa8d8', '#5ee0ff', '#c86bff', '#ff5ec8'],
    glow: 0.9,
    trail: 0.18,
    decay: 0.94,
    lineWidth: 3,
    blocks: false,
    scanlines: false,
    defaultMode: 'radial',
    chrome: { fg: '#9fd8f5', dim: '#3d5a7a', accent: '#ff5ec8' },
  },
  {
    id: 'amber',
    name: 'Amber CRT',
    bg: '#0a0704',
    ramp: ['#3a1f00', '#a35c00', '#ffa726', '#ffd9a0'],
    glow: 0.55,
    trail: 0.12,      // phosphor persistence
    decay: 0.96,
    lineWidth: 2.5,
    blocks: false,
    scanlines: true,
    defaultMode: 'scope',
    chrome: { fg: '#ffa726', dim: '#7a4a10', accent: '#ffd9a0' },
  },
  {
    id: 'milkdrop',
    name: 'Milkdrop',
    bg: '#05000d',
    ramp: ['#2d0b52', '#7b1fa2', '#e91e63', '#ff9800', '#ffff00'],
    glow: 1,
    trail: 0.07,      // long feedback smear
    decay: 0.97,
    lineWidth: 3.5,
    blocks: false,
    scanlines: false,
    defaultMode: 'particles',
    chrome: { fg: '#ff9800', dim: '#6a3a7a', accent: '#ffff00' },
  },
  {
    id: 'paper',
    name: 'Paper',
    bg: '#f4f1ea',
    ramp: ['#c9c3b6', '#8a8578', '#4a463c', '#161412'],
    glow: 0,
    trail: 1,
    decay: 0.88,
    lineWidth: 1.5,
    blocks: false,
    scanlines: false,
    defaultMode: 'scope',
    chrome: { fg: '#161412', dim: '#8a8578', accent: '#8c3a2e' },
  },
];

for (const t of THEMES) {
  t._ramp = t.ramp.map(hexToRgb);
  t._bg = hexToRgb(t.bg);
}

// Sample the ramp at 0..1.
export function rampColor(theme, v, alpha = 1) {
  const r = theme._ramp;
  const x = (v < 0 ? 0 : v > 1 ? 1 : v) * (r.length - 1);
  const i = Math.floor(x);
  const f = x - i;
  const a = r[i];
  const b = r[Math.min(i + 1, r.length - 1)];
  const R = Math.round(a[0] + (b[0] - a[0]) * f);
  const G = Math.round(a[1] + (b[1] - a[1]) * f);
  const B = Math.round(a[2] + (b[2] - a[2]) * f);
  return alpha >= 1 ? `rgb(${R},${G},${B})` : `rgba(${R},${G},${B},${alpha})`;
}

export function bgColor(theme, alpha = 1) {
  const [r, g, b] = theme._bg;
  return alpha >= 1 ? `rgb(${r},${g},${b})` : `rgba(${r},${g},${b},${alpha})`;
}

// Modes call this before drawing rather than setting shadowBlur themselves, so
// a theme with glow: 0 costs nothing.
export function applyGlow(ctx, theme, color, scale = 1) {
  if (theme.glow <= 0) {
    ctx.shadowBlur = 0;
    return;
  }
  ctx.shadowBlur = theme.glow * 24 * scale;
  ctx.shadowColor = color;
}
