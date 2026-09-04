// AudioEngine — turns any audio source into one normalized AudioFrame per tick.
//
// Renderers read the frame and nothing else, which is what makes the three
// sources interchangeable: a mode built against the tone generator works
// unchanged against Spotify.

export const SOURCE = { DISPLAY: 'display', DEVICE: 'device', TONE: 'tone' };

const FFT_SIZE = 2048;
const MIN_DB = -90;
const MAX_DB = -10;

// Log-spaced bars, precomputed once per frame so modes never touch raw bins.
const BAR_COUNT = 96;
const BAR_MIN_HZ = 30;
const BAR_MAX_HZ = 16000;

// Beat detection.
const HISTORY = 60;             // ~1s at 60fps
const BEAT_THRESHOLD = 1.35;    // times the local average
const BEAT_MIN_GAP = 0.25;      // seconds — caps at 240 BPM
const BEAT_MIN_ENERGY = 0.10;   // don't fire on near-silence

const BANDS = [
  ['bass', 20, 140],
  ['lowMid', 140, 400],
  ['mid', 400, 1600],
  ['highMid', 1600, 5000],
  ['treble', 5000, 16000],
];

export class AudioEngine {
  constructor() {
    this.ctx = null;
    this.analyser = null;
    this.sourceType = null;
    this.onEnded = null;        // called when a capture stream dies

    this._node = null;          // current MediaStreamSource
    this._stream = null;
    this._tone = null;

    this._fftDb = null;
    this._barLo = null;
    this._barHi = null;

    // Public frame, mutated in place so we don't allocate 60x/second.
    this.frame = {
      fft: null,                // per-bin magnitude, 0..1 (not dB — renderers want this)
      wave: null,               // time domain, -1..1
      bars: null,               // log-spaced magnitudes, 0..1
      bands: { bass: 0, lowMid: 0, mid: 0, highMid: 0, treble: 0 },
      level: 0,
      beat: false,
      beatEnergy: 0,
      bpm: null,
      t: 0,
      dt: 1 / 60,
    };

    this._peak = 0.15;          // rolling peak for auto-gain
    this._history = [];
    this._lastBeat = -Infinity;
    this._onsets = [];
    this._lastT = 0;
  }

  // ---------- graph ----------

  _ensureCtx() {
    if (this.ctx) return this.ctx;
    const Ctx = window.AudioContext || window.webkitAudioContext;
    this.ctx = new Ctx();

    const a = this.ctx.createAnalyser();
    a.fftSize = FFT_SIZE;
    a.smoothingTimeConstant = 0;   // we smooth ourselves, with separate attack/release
    a.minDecibels = MIN_DB;
    a.maxDecibels = MAX_DB;
    this.analyser = a;
    // Deliberately never connected to ctx.destination. The captured audio is
    // already coming out of the speakers; connecting would double it.

    const bins = a.frequencyBinCount;
    this._fftDb = new Float32Array(bins);
    this.frame.fft = new Float32Array(bins);
    this.frame.wave = new Float32Array(a.fftSize);
    this.frame.bars = new Float32Array(BAR_COUNT);

    this._buildBarMap(bins);
    return this.ctx;
  }

  // Bins are linear in Hz; hearing is logarithmic. Precompute the bin range
  // backing each bar once, or the display crushes everything into the left edge.
  _buildBarMap(bins) {
    const binHz = this.ctx.sampleRate / FFT_SIZE;
    const lo = Math.log(BAR_MIN_HZ);
    const hi = Math.log(BAR_MAX_HZ);
    this._barLo = new Int32Array(BAR_COUNT);
    this._barHi = new Int32Array(BAR_COUNT);
    for (let i = 0; i < BAR_COUNT; i++) {
      const f0 = Math.exp(lo + (hi - lo) * (i / BAR_COUNT));
      const f1 = Math.exp(lo + (hi - lo) * ((i + 1) / BAR_COUNT));
      let a = Math.floor(f0 / binHz);
      let b = Math.ceil(f1 / binHz);
      if (b <= a) b = a + 1;
      this._barLo[i] = Math.min(a, bins - 1);
      this._barHi[i] = Math.min(b, bins);
    }
  }

  _teardown() {
    if (this._tone) { this._tone.stop(); this._tone = null; }
    if (this._node) { try { this._node.disconnect(); } catch (e) { /* already gone */ } this._node = null; }
    if (this._stream) { this._stream.getTracks().forEach((t) => t.stop()); this._stream = null; }
  }

  // ---------- sources ----------

  // System or tab audio. On Windows, Chrome and Edge offer "Share system audio"
  // for Entire Screen or a browser tab — never a single app window. That taps
  // the post-mix OS output, so DRM sources like Spotify come through fine.
  async useDisplay() {
    const ctx = this._ensureCtx();

    // Chrome will not hand over system audio unless video is also requested,
    // even though we throw the video track away immediately.
    const stream = await navigator.mediaDevices.getDisplayMedia({ video: true, audio: true });
    stream.getVideoTracks().forEach((t) => t.stop());

    const audio = stream.getAudioTracks();
    if (audio.length === 0) {
      stream.getTracks().forEach((t) => t.stop());
      throw new Error(
        'That share had no audio. Re-share and tick "Share system audio" — Chrome only ' +
        'offers it for Entire Screen or a browser tab, never a single app window.'
      );
    }

    this._teardown();
    this._stream = stream;
    this._node = ctx.createMediaStreamSource(new MediaStream(audio));
    this._node.connect(this.analyser);
    this.sourceType = SOURCE.DISPLAY;

    audio[0].addEventListener('ended', () => {
      if (this.sourceType === SOURCE.DISPLAY && this.onEnded) this.onEnded();
    });

    await ctx.resume();
    return this;
  }

  // Labels are blank until audio permission has been granted at least once.
  async listDevices() {
    let named = true;
    try {
      const probe = await navigator.mediaDevices.getUserMedia({ audio: true });
      probe.getTracks().forEach((t) => t.stop());
    } catch (e) {
      named = false;
    }
    const devices = await navigator.mediaDevices.enumerateDevices();
    return devices
      .filter((d) => d.kind === 'audioinput')
      .map((d, i) => ({
        id: d.deviceId,
        label: d.label || (named ? `Input ${i + 1}` : `Input ${i + 1} — allow access to see names`),
      }));
  }

  // An input device: a loopback driver (BlackHole, VB-CABLE) on macOS, where
  // Chrome offers tab audio but not system audio.
  async useDevice(deviceId) {
    const ctx = this._ensureCtx();
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        deviceId: deviceId ? { exact: deviceId } : undefined,
        // All three default to on and are tuned for speech. Left on, they
        // visibly wreck a music spectrum — pumping levels, gutted high end.
        echoCancellation: false,
        noiseSuppression: false,
        autoGainControl: false,
      },
    });

    this._teardown();
    this._stream = stream;
    this._node = ctx.createMediaStreamSource(stream);
    this._node.connect(this.analyser);
    this.sourceType = SOURCE.DEVICE;

    stream.getAudioTracks()[0].addEventListener('ended', () => {
      if (this.sourceType === SOURCE.DEVICE && this.onEnded) this.onEnded();
    });

    await ctx.resume();
    return this;
  }

  // Synthetic source: a 124 BPM loop with kick, hats, bass and a sustained pad.
  // No permissions, no share prompt, nothing else playing — this is what theme
  // and mode work gets built against.
  useTone() {
    const ctx = this._ensureCtx();
    this._teardown();

    const out = ctx.createGain();
    out.gain.value = 0.85;
    out.connect(this.analyser);   // analyser only, never ctx.destination

    const noise = ctx.createBuffer(1, Math.floor(ctx.sampleRate * 0.4), ctx.sampleRate);
    const nd = noise.getChannelData(0);
    for (let i = 0; i < nd.length; i++) nd[i] = Math.random() * 2 - 1;

    // Sustained pad, so the mid and treble bands always have something to show
    // between transients.
    const padGain = ctx.createGain();
    padGain.gain.value = 0.10;
    const padFilter = ctx.createBiquadFilter();
    padFilter.type = 'lowpass';
    padFilter.frequency.value = 900;
    padFilter.Q.value = 6;
    padGain.connect(padFilter);
    padFilter.connect(out);

    const padOscs = [110, 164.81, 220, 329.63].map((f, i) => {
      const o = ctx.createOscillator();
      o.type = i % 2 ? 'sawtooth' : 'triangle';
      o.frequency.value = f;
      o.detune.value = (i - 1.5) * 7;
      o.connect(padGain);
      o.start();
      return o;
    });

    // Slow sweep so the spectrum moves even during sustained passages.
    const lfo = ctx.createOscillator();
    lfo.frequency.value = 0.07;
    const lfoAmt = ctx.createGain();
    lfoAmt.gain.value = 700;
    lfo.connect(lfoAmt);
    lfoAmt.connect(padFilter.frequency);
    lfo.start();

    const kick = (t) => {
      const o = ctx.createOscillator();
      const g = ctx.createGain();
      o.frequency.setValueAtTime(150, t);
      o.frequency.exponentialRampToValueAtTime(45, t + 0.11);
      g.gain.setValueAtTime(0.0001, t);
      g.gain.exponentialRampToValueAtTime(1, t + 0.005);
      g.gain.exponentialRampToValueAtTime(0.0001, t + 0.34);
      o.connect(g); g.connect(out);
      o.start(t); o.stop(t + 0.36);
    };

    const hat = (t, open) => {
      const s = ctx.createBufferSource();
      s.buffer = noise;
      const f = ctx.createBiquadFilter();
      f.type = 'highpass';
      f.frequency.value = 7000;
      const g = ctx.createGain();
      const d = open ? 0.16 : 0.045;
      g.gain.setValueAtTime(open ? 0.25 : 0.14, t);
      g.gain.exponentialRampToValueAtTime(0.0001, t + d);
      s.connect(f); f.connect(g); g.connect(out);
      s.start(t); s.stop(t + d + 0.02);
    };

    const bass = (t, freq) => {
      const o = ctx.createOscillator();
      o.type = 'square';
      o.frequency.value = freq;
      const f = ctx.createBiquadFilter();
      f.type = 'lowpass';
      f.frequency.setValueAtTime(1400, t);
      f.frequency.exponentialRampToValueAtTime(220, t + 0.2);
      const g = ctx.createGain();
      g.gain.setValueAtTime(0.0001, t);
      g.gain.exponentialRampToValueAtTime(0.35, t + 0.01);
      g.gain.exponentialRampToValueAtTime(0.0001, t + 0.25);
      o.connect(f); f.connect(g); g.connect(out);
      o.start(t); o.stop(t + 0.27);
    };

    const eighth = 60 / 124 / 2;
    const roots = [55, 55, 73.42, 65.41];
    let step = 0;
    let nextAt = ctx.currentTime + 0.15;

    const timer = setInterval(() => {
      while (nextAt < ctx.currentTime + 0.2) {
        const s = step % 8;
        if (s === 0 || s === 4 || s === 6) kick(nextAt);
        hat(nextAt, s % 4 === 2);
        if (s % 2 === 0) bass(nextAt, roots[(step >> 3) % roots.length]);
        nextAt += eighth;
        step++;
      }
    }, 25);

    this._tone = {
      stop() {
        clearInterval(timer);
        padOscs.forEach((o) => { try { o.stop(); } catch (e) { /* already stopped */ } });
        try { lfo.stop(); } catch (e) { /* already stopped */ }
        try { out.disconnect(); } catch (e) { /* already gone */ }
      },
    };
    this.sourceType = SOURCE.TONE;
    ctx.resume();
    return this;
  }

  stop() {
    this._teardown();
    this.sourceType = null;
  }

  // ---------- per-frame read ----------

  read() {
    const f = this.frame;
    if (!this.analyser) return f;

    const now = this.ctx.currentTime;
    f.dt = this._lastT ? Math.min(now - this._lastT, 0.1) : 1 / 60;
    f.t = now;
    this._lastT = now;

    this.analyser.getFloatFrequencyData(this._fftDb);
    this.analyser.getFloatTimeDomainData(f.wave);

    const span = MAX_DB - MIN_DB;
    const db = this._fftDb;
    const norm = f.fft;
    for (let i = 0; i < db.length; i++) {
      const v = (db[i] - MIN_DB) / span;
      norm[i] = v < 0 ? 0 : v > 1 ? 1 : v;
    }

    // Raw bands, pre-gain. Beat detection uses these so auto-gain can't
    // manufacture onsets during quiet passages.
    const raw = {};
    let loudest = 0;
    const binHz = this.ctx.sampleRate / FFT_SIZE;
    for (let b = 0; b < BANDS.length; b++) {
      const [name, loHz, hiHz] = BANDS[b];
      const lo = Math.max(0, Math.floor(loHz / binHz));
      const hi = Math.min(norm.length - 1, Math.ceil(hiHz / binHz));
      let sum = 0;
      for (let i = lo; i <= hi; i++) sum += norm[i];
      const v = sum / (hi - lo + 1);
      raw[name] = v;
      if (v > loudest) loudest = v;
    }

    // Auto-gain at the visual layer, since browser AGC is off in the capture
    // path. Rolling peak with slow decay and a floor, so silence stays silent
    // instead of being amplified into noise.
    this._peak = Math.max(loudest, this._peak * (1 - 1.2 * f.dt), 0.08);
    const gain = 1 / this._peak;

    // Fast attack, slow release — reads as responsive without flickering.
    const up = 1 - Math.exp(-f.dt / 0.02);
    const down = 1 - Math.exp(-f.dt / 0.12);
    for (const name of Object.keys(f.bands)) {
      const target = Math.min(1, raw[name] * gain);
      const prev = f.bands[name];
      f.bands[name] = prev + (target - prev) * (target > prev ? up : down);
    }

    for (let i = 0; i < BAR_COUNT; i++) {
      let peak = 0;
      for (let j = this._barLo[i]; j < this._barHi[i]; j++) {
        if (norm[j] > peak) peak = norm[j];
      }
      const target = Math.min(1, peak * gain);
      const prev = f.bars[i];
      f.bars[i] = prev + (target - prev) * (target > prev ? up : down);
    }

    let sq = 0;
    for (let i = 0; i < f.wave.length; i++) sq += f.wave[i] * f.wave[i];
    f.level = Math.min(1, Math.sqrt(sq / f.wave.length) * 3);

    this._detectBeat(raw.bass, now, f);
    return f;
  }

  // Energy flux on the bass band against its own local average.
  _detectBeat(bass, now, f) {
    this._history.push(bass);
    if (this._history.length > HISTORY) this._history.shift();

    f.beat = false;
    if (this._history.length >= 20) {
      let sum = 0;
      for (let i = 0; i < this._history.length; i++) sum += this._history[i];
      const avg = sum / this._history.length;
      if (bass > avg * BEAT_THRESHOLD && bass > BEAT_MIN_ENERGY && now - this._lastBeat > BEAT_MIN_GAP) {
        f.beat = true;
        this._lastBeat = now;
        this._onsets.push(now);
        if (this._onsets.length > 24) this._onsets.shift();
        this._estimateBpm(f);
      }
    }

    f.beatEnergy = Math.max(0, 1 - (now - this._lastBeat) / 0.6);
  }

  // Median inter-onset interval, folded into a musical range.
  _estimateBpm(f) {
    if (this._onsets.length < 6) { f.bpm = null; return; }
    const iv = [];
    for (let i = 1; i < this._onsets.length; i++) iv.push(this._onsets[i] - this._onsets[i - 1]);
    iv.sort((a, b) => a - b);
    const med = iv[Math.floor(iv.length / 2)];
    if (!med) return;
    let bpm = 60 / med;
    while (bpm < 70) bpm *= 2;
    while (bpm > 180) bpm /= 2;
    f.bpm = Math.round(bpm);
  }
}
