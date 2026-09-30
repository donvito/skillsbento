# kit.js API (on top of the engine globals in engine/references/engine-api.md)

Constants: `C` palette (`bg panel panel2 pink cyan yel lime red green white dim ink`, overridable with `BRAND.colors`), `SEAM = 960`, font families `FA` (display), `FS` (body), `FJ` (mono), loaded from `fonts/display.ttf`, `body.ttf` and `mono.ttf`.
`BR` is the merged brand: `handle tagline ring live cta ctaEdu watermark faceFocus colors`. `hexA('#rrggbb', a)` gives an rgba string.
Engine globals you'll use: `W H P E lerp clamp rng noise1 font txt pill glow typeText ringText clip image`.

## Layout
| call | what |
|---|---|
| `runBeats(c, T, BEATS)` | draws the active stage beat inside the top half, with the neon floor bg (`tint`) and a slam/flash/bar on every beat change after the first. `BEATS = [{a, tint, draw(c, t, T, dur)}]` |
| `faceCam(c, T, [[t, amt]...])` | facecam clip `face` in the bottom half with a slow push + punch-ins, bottom scrim, @handle, neon seam |
| `captions(c, T, CAPS, {size, y, hot})` | `CAPS = [[t0, t1, 'TEXT *HOT*']]`, pop-in per chunk, alternating tilt, yellow hot words |
| `progress(c, T, SPEECH)` | pink progress bar at the top |
| `endCard(c, t, T, {faceT, emoji, edu, line1, line3})` | full-screen outro: face in a ring (+ ring text), optional LIVE pill, CTA (`edu` → ctaEdu) + handle + tagline, all from BRAND |
| `stageBg(c, T, tint)` | neon perspective floor + glow + scanlines (runBeats calls it) |

Branding comes from `window.BRAND` (brand.json), so don't hardcode handles in the page.

## Elements
| call | what |
|---|---|
| `big(c, s, x, y, size, {color, stroke, lw, align, s, rot, alpha, glow, font, weight})` | outlined display text centred on (x,y). `s` is the scale (pop). Returns the width |
| `label(c, s, x, y, size, color, {align, weight, font, ls, alpha})` | small UI text (middle baseline) |
| `emo(c, '🔥', x, y, size, {s, rot, alpha})` | colour emoji (system emoji font) |
| `card(c, x, y, w, h, col, {fill, glow, r, lw})` | neon panel |
| `rr(c, x, y, w, h, r, fill, stroke, lw)` | rounded rect (r can be an array) |
| `stamp(c, text, x, y, size, col, T, t0, rot)` | slams in at global time t0 (boxed, rotated) |
| `bar(c, x, y, w, h, p, col)` | progress bar |
| `burst(c, x, y, r0, r1, n, col, alpha, rot)` | radial speed lines |
| `sparks(c, x, y, T, t0, n, cols, spread, seed)` | confetti burst from t0 (1.2s) |
| `stepBadge(c, n, 'HEADING', t, col)` | numbered step pill + heading for tutorials |
| `browserBar(c, x, y, w, url, t, t0, cps)` | browser chrome with a typed URL |

## Timing helpers
- `pop(t, t0, d=.22)` gives outBack progress for scale-in. Use it as `{ s: pop(T, 12.2) }`.
- `slam(t, t0)` goes from 2.4 → 1 (0 before t0).
- `P(t, a, b)` + `E.outExpo/inCubic/ioCubic/outBack` for everything else.
- Inside a beat, `t` is local time. Pin word-synced events to **global** `T` so they match `src/words.json`.

## Media ids
`face` is the facecam clip (speech timeline). Moving screen crops use the `screens` names (draw with `clip(c, id, T, x, y, w, h, {fit:'contain'})`). Stills use the `stills` names (draw with `image(c, id, ...)`).

## Cues (sound + camera)
`clip_audio` (the voice, `duck: .96`) · `whoosh {dur}` before each beat change (t − .12) · `blip {note}` pops · `impact {shake, flash}` stamps · `stab` · `bell` · `tick` · `typing {dur, cps}` · `riser {dur}` · final `impact` with `end: true` at SPEECH.
