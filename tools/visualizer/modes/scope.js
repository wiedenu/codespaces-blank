// Time-domain oscilloscope. Reads frame.wave directly, so it shows the actual
// waveform rather than an FFT reduction — the mode that most rewards a theme
// with long trails (Amber CRT, Milkdrop).

import { rampColor, applyGlow } from '../themes.js';

export const name = 'Scope';

export function render(ctx, frame, theme, w, h) {
  const wave = frame.wave;
  const n = wave.length;
  const mid = h / 2;

  // Amplitude tracks overall level so quiet passages still show a line rather
  // than collapsing flat.
  const amp = mid * 0.8 * (0.25 + 0.75 * Math.min(1, frame.level * 1.6));
  const c = rampColor(theme, 0.55 + 0.45 * frame.beatEnergy);

  ctx.lineWidth = theme.lineWidth + frame.beatEnergy * 1.5;
  ctx.lineJoin = 'round';
  ctx.lineCap = 'round';
  ctx.strokeStyle = c;
  applyGlow(ctx, theme, c);

  // One point per horizontal pixel; the buffer is longer than the canvas is
  // wide, so step through it rather than drawing every sample.
  const step = n / w;
  ctx.beginPath();
  for (let x = 0; x < w; x++) {
    const y = mid - wave[Math.floor(x * step)] * amp;
    if (x === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.stroke();

  // A dimmer echo, offset by a quarter of the buffer, gives the trace depth
  // without needing a second pass over the audio.
  ctx.globalAlpha = 0.35;
  ctx.lineWidth = theme.lineWidth * 0.6;
  ctx.strokeStyle = rampColor(theme, 0.25);
  ctx.beginPath();
  const off = Math.floor(n / 4);
  for (let x = 0; x < w; x++) {
    const y = mid - wave[(Math.floor(x * step) + off) % n] * amp * 0.6;
    if (x === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.stroke();
  ctx.globalAlpha = 1;
  ctx.shadowBlur = 0;
}
