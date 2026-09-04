// The spectrum wrapped into a circle: bass at the top, sweeping up through
// treble around both sides so the figure stays symmetrical. Radius pulses on
// the beat.

import { rampColor, applyGlow } from '../themes.js';

export const name = 'Radial';

let spin = 0;

export function reset() {
  spin = 0;
}

export function render(ctx, frame, theme, w, h) {
  const bars = frame.bars;
  const n = bars.length;
  const cx = w / 2;
  const cy = h / 2;

  // Rotation speed rides the mids, so the figure drifts rather than sitting
  // still during sparse passages.
  spin += frame.dt * (0.08 + frame.bands.mid * 0.35);

  const base = Math.min(w, h) * (0.17 + frame.bands.bass * 0.05 + frame.beatEnergy * 0.04);
  const reach = Math.min(w, h) * 0.28;

  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate(spin);

  ctx.lineCap = 'round';
  ctx.lineWidth = Math.max(1.5, (Math.PI * base) / n) * 1.4;

  // Mirrored: each bin is drawn on both sides of the vertical axis.
  for (let i = 0; i < n; i++) {
    const v = bars[i];
    const len = v * reach;
    if (len < 1) continue;

    const c = rampColor(theme, v);
    ctx.strokeStyle = c;
    applyGlow(ctx, theme, c, 0.7);

    const a = (i / n) * Math.PI;
    for (const angle of [-Math.PI / 2 + a, -Math.PI / 2 - a]) {
      const cos = Math.cos(angle);
      const sin = Math.sin(angle);
      ctx.beginPath();
      ctx.moveTo(cos * base, sin * base);
      ctx.lineTo(cos * (base + len), sin * (base + len));
      ctx.stroke();
    }
  }

  ctx.restore();

  // Inner ring, sized by overall level — a still centre for the spokes to
  // radiate from.
  ctx.shadowBlur = 0;
  const ring = base * (0.82 + frame.beatEnergy * 0.1);
  ctx.strokeStyle = rampColor(theme, 0.15 + frame.level * 0.5);
  ctx.lineWidth = theme.lineWidth;
  ctx.beginPath();
  ctx.arc(cx, cy, ring, 0, Math.PI * 2);
  ctx.stroke();
}
