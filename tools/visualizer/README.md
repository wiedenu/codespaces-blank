# Visualizer

A WinAmp-style audio visualizer for whatever your machine is already playing. Five themes, four
render modes, zero dependencies. Ships as a single self-contained HTML file you can bookmark.

It never knows what the audio is. Spotify, Apple Music, a YouTube tab, a Teams call — all identical
to the code.

## Run

**Single file — no server, bookmarkable.** Open **`visualizer.html`** directly. `file://` *is* a
secure context, so screen capture works with nothing running in the background.

Copy `visualizer.html` anywhere you like (desktop, Documents), double-click it, then bookmark the
address bar. It has no dependencies and no network calls, so it works offline and keeps working if
this repo moves.

```
Windows   file:///C:/Users/<you>/Desktop/visualizer.html
macOS     file:///Users/<you>/Desktop/visualizer.html
```

Regenerate it after editing any source file:

```bash
python3 tools/visualizer/build.py
```

**Modular source — for development.** Chrome blocks ES module imports over `file://` under CORS
(the modules, *not* the media APIs — that distinction is the whole reason `build.py` exists), so the
unbundled version needs a server:

```bash
python3 -m http.server 8000
# then open http://localhost:8000/tools/visualizer/
```

The page opens on a built-in test tone — a 124 BPM loop with kick, hats, bass and a pad. That means
you can build and tune themes with nothing playing and no permission prompt. Switch **Source** once
it's running.

## Getting real audio in

### Windows (Chrome or Edge) — nothing to install

Set **Source** to *System / tab audio*, pick **Entire Screen**, and tick **Share system audio**.

That checkbox is the whole trick. It taps the post-mix OS output, where audio is already decoded
PCM, so DRM-protected sources like Spotify come through fine. (The DRM muting people run into is
narrower than it's usually described: it applies to capturing a *protected tab*, which is why the
Spotify **Web Player** in a tab comes through silent while the desktop app does not.)

Chrome only offers the checkbox for **Entire Screen** or **a browser tab** — never a single
application window. To visualize a desktop app, share the entire screen.

### macOS — needs a loopback device

Chrome on macOS offers tab audio but *not* system audio, so there is no equivalent of the checkbox
above. For anything outside a browser tab you need a virtual audio device:

1. Install [BlackHole](https://existential.audio/blackhole/) (free).
2. In **Audio MIDI Setup**, create a **Multi-Output Device** containing both BlackHole and your
   speakers, so you can still hear what you're visualizing.
3. Set that as the system output (or just Spotify's output).
4. In the visualizer, set **Source** to *Input device* and pick BlackHole.

For a browser tab specifically, *System / tab audio* → share the tab works on macOS too.

## Controls

| | |
|---|---|
| `1`–`5` | switch theme |
| `←` `→` | switch mode |
| `F` | fullscreen |

The status bar hides after 3 seconds of no mouse movement. Theme and mode persist across reloads;
the audio source deliberately does not, since restoring it would pop a share picker on page load.

## Themes and modes

Themes carry a palette *and* render character — glow, trail length, peak decay, whether bars draw
solid or as stacked blocks — but never geometry. Modes own geometry and read the theme for
everything else. The two are independent, so all 5 × 4 combinations work.

| Theme | | Mode | |
|---|---|---|---|
| Classic Green | the 1997 look: stacked blocks, peak caps, hard edges | Bars | log-spaced spectrum with peak-hold caps |
| Midnight | cyan through magenta, heavy glow, long trails | Scope | time-domain waveform |
| Amber CRT | monochrome amber, scanlines, phosphor decay | Radial | spectrum wrapped circular, pulses on beat |
| Milkdrop | high saturation, long feedback smear | Particles | beat-spawned, bass drives count and speed |
| Paper | light: ink on off-white, no glow | | |

Selecting a theme also switches to the mode it was designed around. Changing mode afterwards keeps
the theme.

## How it works

`audio.js` emits one normalized `AudioFrame` per tick and renderers read nothing else. That contract
is why the three sources are interchangeable: a mode built against the test tone works unchanged
against Spotify.

```js
{
  fft,        // per-bin magnitude, 0..1
  wave,       // time domain, -1..1
  bars,       // 96 log-spaced magnitudes, 0..1
  bands,      // { bass, lowMid, mid, highMid, treble }, 0..1
  level,      // overall RMS, 0..1
  beat,       // true only on the frame an onset fires
  beatEnergy, // 0..1, decays after each beat
  bpm,        // estimate, null until confident
  t, dt,
}
```

Four things in here are less obvious than they look, and all four are load-bearing:

**Chrome will not hand over system audio unless you also request a video track**, even though the
video is useless to us. We request it and stop it immediately.

**The three `getUserMedia` DSP flags must be off.** `echoCancellation`, `noiseSuppression` and
`autoGainControl` all default to *on* and are tuned for speech. Left on, they visibly wreck a music
spectrum — pumping levels and gutted high end. Gain is instead recovered at the visual layer with a
rolling peak, where it can't damage the signal.

**Bins are linear in Hz; hearing is logarithmic.** The 96 bars are backed by log-spaced bin ranges,
precomputed once. Skip this and everything crushes into the left-hand fifth of the display.

**The analyser is never connected to `ctx.destination`.** The captured audio is already coming out
of the speakers; connecting would double it.

Beat detection is energy flux on the bass band against its own rolling average, gated to 250ms
minimum spacing, with BPM from the median inter-onset interval. Nothing is precomputed, so it reacts
to what is actually hitting.

## Adding a theme

Append an object to `THEMES` in `themes.js`. No other file needs to change — it appears in the
picker and works across all four modes. Re-run `build.py` to refresh `visualizer.html`.

## Adding a mode

Add `modes/yours.js` exporting `name` and `render(ctx, frame, theme, w, h)`, plus an optional
`reset()` for internal state. Import it in `main.js`, add it to the `MODES` map, add its name to `MODES` in `build.py`, then
re-run `build.py`.

Read palette and character from the theme (`rampColor`, `bgColor`, `applyGlow`) rather than
hardcoding colour, and multiply anything time-based by `frame.dt` so motion matches on a 144Hz
display. Don't clear the canvas — `main.js` handles that, and the trail alpha is a theme decision.
