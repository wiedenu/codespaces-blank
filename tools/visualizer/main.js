import { AudioEngine, SOURCE } from './audio.js';
import { THEMES, bgColor } from './themes.js';
import * as bars from './modes/bars.js';
import * as scope from './modes/scope.js';
import * as radial from './modes/radial.js';
import * as particles from './modes/particles.js';

const MODES = { bars, scope, radial, particles };
const MODE_IDS = Object.keys(MODES);

const $ = (id) => document.getElementById(id);
const canvas = $('stage');
const ctx = canvas.getContext('2d', { alpha: false });
const bar = $('bar');
const toast = $('toast');
const gate = $('gate');

const engine = new AudioEngine();

let theme = THEMES[0];
let modeId = theme.defaultMode;
let needsClear = true;
let running = false;

// ---------- persistence ----------

function load(key, fallback) {
  try {
    return localStorage.getItem(key) ?? fallback;
  } catch (e) {
    return fallback;   // private window, blocked site data
  }
}

function save(key, value) {
  try {
    localStorage.setItem(key, value);
  } catch (e) {
    /* non-fatal: selections just won't persist */
  }
}

// ---------- canvas ----------

function resize() {
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  canvas.width = Math.round(canvas.clientWidth * dpr);
  canvas.height = Math.round(canvas.clientHeight * dpr);
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  needsClear = true;
}

new ResizeObserver(resize).observe(canvas);

// ---------- theme ----------

function applyTheme(next) {
  theme = next;
  needsClear = true;
  const root = document.documentElement.style;
  root.setProperty('--fg', theme.chrome.fg);
  root.setProperty('--dim', theme.chrome.dim);
  root.setProperty('--accent', theme.chrome.accent);
  root.setProperty('--bg', theme.bg);
  save('viz.theme', theme.id);
}

// Picking a theme — from the dropdown or a number key — also adopts the mode it
// was designed around. Arrow keys then change mode without touching the theme.
function selectTheme(next) {
  applyTheme(next);
  setMode(next.defaultMode);
  $('theme').value = next.id;
}

function setMode(id) {
  modeId = id;
  const m = MODES[id];
  if (m.reset) m.reset();
  needsClear = true;
  $('mode').value = id;
  save('viz.mode', id);
}

// Scanline overlay is theme-owned rather than mode-owned, so every mode picks
// it up under Amber CRT without knowing about it.
function drawScanlines(w, h) {
  ctx.fillStyle = 'rgba(0,0,0,0.18)';
  for (let y = 0; y < h; y += 3) ctx.fillRect(0, y, w, 1);
}

// ---------- loop ----------

function tick() {
  requestAnimationFrame(tick);
  if (!running || document.hidden) return;

  const w = canvas.clientWidth;
  const h = canvas.clientHeight;
  const frame = engine.read();

  // Trails instead of clearRect: filling the background at theme.trail alpha is
  // what produces the smear, and it costs nothing.
  if (needsClear) {
    ctx.fillStyle = bgColor(theme, 1);
    ctx.fillRect(0, 0, w, h);
    needsClear = false;
  } else {
    ctx.fillStyle = bgColor(theme, theme.trail);
    ctx.fillRect(0, 0, w, h);
  }

  MODES[modeId].render(ctx, frame, theme, w, h);
  if (theme.scanlines) drawScanlines(w, h);

  $('level').style.width = `${Math.round(frame.level * 100)}%`;
  const bpm = frame.bpm ? `${frame.bpm} BPM` : '--';
  if ($('bpm').textContent !== bpm) $('bpm').textContent = bpm;
}

// ---------- sources ----------

function say(msg, isError) {
  toast.textContent = msg;
  toast.hidden = false;
  toast.classList.toggle('err', !!isError);
  clearTimeout(say._t);
  say._t = setTimeout(() => { toast.hidden = true; }, isError ? 9000 : 3000);
}

async function useSource(kind) {
  try {
    if (kind === SOURCE.TONE) {
      engine.useTone();
      $('deviceRow').hidden = true;
      say('Test tone — 124 BPM. Build themes against this.');
    } else if (kind === SOURCE.DISPLAY) {
      await engine.useDisplay();
      $('deviceRow').hidden = true;
      say('Capturing shared audio.');
    } else {
      $('deviceRow').hidden = false;
      await populateDevices();
      await engine.useDevice($('device').value || undefined);
      say('Capturing input device.');
    }
    running = true;
    $('source').value = engine.sourceType;
    save('viz.source', engine.sourceType);
  } catch (err) {
    // A cancelled share picker is a normal outcome, not a failure worth shouting about.
    const cancelled = err && (err.name === 'NotAllowedError' || err.name === 'AbortError');
    say(cancelled ? 'Cancelled — still on the previous source.' : err.message || String(err), !cancelled);
    $('source').value = engine.sourceType || SOURCE.TONE;
    if (!engine.sourceType) { engine.useTone(); running = true; }
  }
}

async function populateDevices() {
  const sel = $('device');
  const devices = await engine.listDevices();
  const prev = sel.value;
  sel.innerHTML = '';
  for (const d of devices) {
    const o = document.createElement('option');
    o.value = d.id;
    o.textContent = d.label;
    sel.appendChild(o);
  }
  const remembered = load('viz.device', '');
  if (devices.some((d) => d.id === prev)) sel.value = prev;
  else if (devices.some((d) => d.id === remembered)) sel.value = remembered;
}

engine.onEnded = () => {
  say('Share ended — back on the test tone.');
  engine.useTone();
  $('source').value = SOURCE.TONE;
  $('deviceRow').hidden = true;
};

// ---------- chrome ----------

let idleTimer;
function wake() {
  bar.classList.remove('hidden');
  clearTimeout(idleTimer);
  idleTimer = setTimeout(() => {
    if (running && !bar.matches(':hover, :focus-within')) bar.classList.add('hidden');
  }, 3000);
}
['mousemove', 'keydown', 'touchstart'].forEach((e) => window.addEventListener(e, wake));

document.addEventListener('keydown', (e) => {
  if (e.target.matches('select, input')) return;
  const n = parseInt(e.key, 10);
  if (n >= 1 && n <= THEMES.length) {
    selectTheme(THEMES[n - 1]);
  } else if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
    const i = MODE_IDS.indexOf(modeId);
    const d = e.key === 'ArrowRight' ? 1 : MODE_IDS.length - 1;
    setMode(MODE_IDS[(i + d) % MODE_IDS.length]);
  } else if (e.key.toLowerCase() === 'f') {
    if (document.fullscreenElement) document.exitFullscreen();
    else document.documentElement.requestFullscreen().catch(() => {});
  }
});

// ---------- init ----------

for (const t of THEMES) {
  const o = document.createElement('option');
  o.value = t.id;
  o.textContent = t.name;
  $('theme').appendChild(o);
}
for (const id of MODE_IDS) {
  const o = document.createElement('option');
  o.value = id;
  o.textContent = MODES[id].name;
  $('mode').appendChild(o);
}

applyTheme(THEMES.find((t) => t.id === load('viz.theme', '')) || THEMES[0]);
$('theme').value = theme.id;
setMode(MODE_IDS.includes(load('viz.mode', '')) ? load('viz.mode', '') : theme.defaultMode);

$('theme').onchange = (e) => selectTheme(THEMES.find((t) => t.id === e.target.value));
$('mode').onchange = (e) => setMode(e.target.value);
$('source').onchange = (e) => useSource(e.target.value);
$('device').onchange = (e) => { save('viz.device', e.target.value); engine.useDevice(e.target.value); };
$('full').onclick = () => {
  if (document.fullscreenElement) document.exitFullscreen();
  else document.documentElement.requestFullscreen().catch(() => {});
};

// AudioContext starts suspended until a user gesture, so the page opens on a
// start gate rather than silently rendering nothing.
gate.onclick = async () => {
  gate.hidden = true;
  // Always open on the tone generator. A capture source can't be restored from
  // localStorage anyway — both getDisplayMedia and getUserMedia need their own
  // gesture, and a share picker appearing unbidden on page load is hostile.
  await useSource(SOURCE.TONE);
  wake();
};

resize();
requestAnimationFrame(tick);
