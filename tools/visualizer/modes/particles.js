// Beat-spawned particles. Bass drives how many and how fast; treble tints
// them. The only mode that depends on frame.beat rather than the spectrum, so
// it doubles as a visual check that onset detection is working.

import { rampColor, applyGlow } from '../themes.js';

export const name = 'Particles';

const MAX = 420;
let parts = [];

export function reset() {
  parts = [];
}

function spawn(cx, cy, frame, reach) {
  const count = Math.min(60, 12 + Math.floor(frame.bands.bass * 48));
  for (let i = 0; i < count; i++) {
    if (parts.length >= MAX) break;
    const angle = Math.random() * Math.PI * 2;
    const speed = reach * (0.35 + Math.random() * 0.9) * (0.5 + frame.bands.bass);
    parts.push({
      x: cx,
      y: cy,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      life: 1,
      fade: 0.35 + Math.random() * 0.5,
      size: 1.5 + Math.random() * 3,
      tint: Math.min(1, 0.25 + frame.bands.treble * 0.9 + Math.random() * 0.2),
    });
  }
}

export function render(ctx, frame, theme, w, h) {
  const cx = w / 2;
  const cy = h / 2;

  if (frame.beat) spawn(cx, cy, frame, Math.min(w, h) * 0.5);

  // A slow outward drift keeps the field alive between onsets, and a gentle
  // drag stops fast particles leaving instantly.
  const drag = Math.pow(0.86, frame.dt * 60);

  for (let i = parts.length - 1; i >= 0; i--) {
    const p = parts[i];
    p.x += p.vx * frame.dt;
    p.y += p.vy * frame.dt;
    p.vx *= drag;
    p.vy *= drag;
    p.life -= p.fade * frame.dt;

    if (p.life <= 0 || p.x < -50 || p.x > w + 50 || p.y < -50 || p.y > h + 50) {
      parts.splice(i, 1);
      continue;
    }

    const c = rampColor(theme, p.tint, p.life);
    ctx.fillStyle = c;
    applyGlow(ctx, theme, c, 0.4);
    const r = p.size * (0.4 + p.life * 0.6);
    ctx.beginPath();
    ctx.arc(p.x, p.y, r, 0, Math.PI * 2);
    ctx.fill();
  }

  // Core that flashes on each detected beat — the readout for onset detection.
  ctx.shadowBlur = 0;
  const core = Math.min(w, h) * (0.02 + frame.beatEnergy * 0.05 + frame.bands.bass * 0.03);
  const cc = rampColor(theme, 0.5 + frame.beatEnergy * 0.5);
  applyGlow(ctx, theme, cc);
  ctx.fillStyle = cc;
  ctx.beginPath();
  ctx.arc(cx, cy, core, 0, Math.PI * 2);
  ctx.fill();
  ctx.shadowBlur = 0;
}
