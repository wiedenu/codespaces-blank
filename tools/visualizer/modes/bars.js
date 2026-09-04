// Log-spaced spectrum bars with peak-hold caps — the WinAmp signature.
// frame.bars is already log-grouped by the engine, so this just draws it.

import { rampColor, bgColor, applyGlow } from '../themes.js';

export const name = 'Bars';

// Segment geometry for themes with blocks: true.
const SEG = 5;
const GAP = 2;
const STEP = SEG + GAP;

let peaks = new Float32Array(0);
let grad = null;
let gradKey = '';

export function reset() {
  peaks = new Float32Array(0);
  grad = null;
  gradKey = '';
}

// Colour by absolute height, so the top of a tall bar runs hot regardless of
// what the bar beside it is doing. Cached — rebuilding it per bar per frame is
// what makes gradients look expensive.
function heightGradient(ctx, theme, h, usable) {
  const key = `${theme.id}:${Math.round(h)}`;
  if (grad && gradKey === key) return grad;
  const g = ctx.createLinearGradient(0, h, 0, h - usable);
  for (let i = 0; i < theme.ramp.length; i++) {
    g.addColorStop(i / (theme.ramp.length - 1), theme.ramp[i]);
  }
  grad = g;
  gradKey = key;
  return g;
}

export function render(ctx, frame, theme, w, h) {
  const bars = frame.bars;
  const n = bars.length;
  if (peaks.length !== n) peaks = new Float32Array(n);

  const slot = w / n;
  const gutter = Math.max(1, slot * 0.16);
  const bw = Math.max(1, slot - gutter);
  const usable = h * 0.94;

  // Framerate-corrected, so caps fall at the same rate on a 60Hz and a 144Hz
  // display.
  const fall = Math.pow(theme.decay, frame.dt * 60);

  if (theme.blocks) {
    // One gradient rect per bar, then the segment gaps painted as full-width
    // background lines in a single pass. Drawing every segment individually is
    // ~9,000 fills a frame at 1080p; this is ~200 for the same picture.
    let tallest = 0;
    applyGlow(ctx, theme, theme.ramp[theme.ramp.length - 2], 0.5);
    ctx.fillStyle = heightGradient(ctx, theme, h, usable);
    for (let i = 0; i < n; i++) {
      const v = bars[i];
      peaks[i] = v > peaks[i] ? v : peaks[i] * fall;
      const barH = v * usable;
      if (barH > tallest) tallest = barH;
      if (barH < 0.5) continue;
      ctx.fillRect(i * slot, h - barH, bw, barH);
    }
    ctx.shadowBlur = 0;
    ctx.fillStyle = bgColor(theme, 1);
    for (let y = STEP; y < tallest + STEP; y += STEP) {
      ctx.fillRect(0, h - y, w, GAP);
    }
  } else {
    for (let i = 0; i < n; i++) {
      const v = bars[i];
      peaks[i] = v > peaks[i] ? v : peaks[i] * fall;
      const barH = v * usable;
      if (barH < 0.5) continue;
      const c = rampColor(theme, v);
      applyGlow(ctx, theme, c);
      ctx.fillStyle = c;
      ctx.fillRect(i * slot, h - barH, bw, barH);
    }
  }

  // Caps last, so they sit above every bar and above the segment gaps.
  ctx.shadowBlur = 0;
  for (let i = 0; i < n; i++) {
    if (peaks[i] < 0.02) continue;
    ctx.fillStyle = rampColor(theme, Math.min(1, peaks[i] + 0.25));
    ctx.fillRect(i * slot, h - peaks[i] * usable - 2, bw, 2);
  }
}
