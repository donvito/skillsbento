# engine.js API

Globals available to scene code in `index.html`.

## Frame & timing
| name | meaning |
|---|---|
| `W, H, FPS, DUR, BPM, BEAT` | canvas size, fps, duration (s), tempo, seconds per beat |
| `U` | unit scale: 1 when the short side is 1080px. Multiply every design size by `U` |
| `M` | safe side margin (6.8% of W landscape, 8.5% portrait) |
| `PORTRAIT` | `H > W`: branch layouts on it |
| `TH` | theme tokens from `REEL_CONFIG.theme`: `bg fg muted dim paper ink inkDim elev accent accentInk flash` |
| `FD, FB, FM` | quoted display / body / mono font families for `font()` |
| `DT` | display tracking (em), auto-applied to `FD` in `riseText/sliceText/fit` |
| `beats(n)`, `bars(n)` | n beats / bars in seconds |
| `beatPulse(T,k=6)` | 1 on every beat, exponential decay: pulses, scale bumps |

## Easing & progress
`P(t,a,b)` clamps the progress of t through [a,b] to 0..1. Combine with `E.outExpo, inExpo, ioExpo, outCubic, inCubic, ioCubic, outQuint, outBack, outElastic, linear`. Also `lerp, clamp`, `rng(seed)` (deterministic random), `noise1(x)` (smooth −1..1).
Pattern: `const p = E.outExpo(P(t, .2, .7)); x = lerp(start, end, p)`.

## Text
- `font(weight, px, family)` returns a CSS font string.
- `txt(c, s, x, y, {font, color, align, base, ls|track, alpha, stroke, lw})`
- `mw(c, s, font, ls)` measures width; `fit(c, s, weight, fam, maxW, maxPx)` returns the largest size ≤ maxPx that fits maxW.
- `riseText(c, s, x, y, px, weight, fam, color, t, t0, stagger=.03, dur=.5, {align, stroke, wordGap})`: letters rise from a mask. Returns the width.
- `wordsRise(c, s, x, y, px, weight, fam, color, t, t0, maxW, {stag, lh})`: word-by-word rise with wrapping. Returns the height.
- `sliceText(c, s, x, y, px, weight, fam, color, t, t0, n=6, dist)`: horizontal slices slide in from alternating sides.
- `typeText(c, s, x, y, font, color, t, t0, cps, cursor=true)`: typewriter with a block cursor.
- `ringText(c, s, cx, cy, r, rotation, font, color, alpha)`: text on a circle (rotate with `t`).
- `countUp(value, p, {prefix, suffix, decimals})`: formatted count-up string (suffix appears at p=1).

## Shapes & texture
`bgFill(c,col)` (with bleed for camera shake) · `pill(c, x, yCenter, label, {font, fg, bg, stroke, h, padX, ls, p})` returns the width · `dotGrid(c, spacing, col, alpha, ox, oy, r)` · `glow(c, x, y, r, 'rgba(r,g,b,A)', alpha)` · `star(c, x, y, rOuter, rInner, points, rot, col)` · `icon(c, 'bolt'|'spark'|'eye'|'arrow'|'play'|'check'|'plus', x, y, size, col)` · `qb()` / `ctrlPt()` for quadratic curves (node graphs, packets along edges).

## Media
Ids come from `media/manifest.json` (`ingest.py`).
- `clip(c, id, localT, x, y, w, h, opts)`: draws the clip frame for `localT` seconds into the clip.
- `image(c, id, x, y, w, h, opts)`
- `media(c, id, localT, ...)`: draws either type.
- `hasMedia(id)`

`opts`: `in` (s offset within the ingested range), `speed` (0.5 = slow-mo, 2 = fast), `loop`, `fit:'cover'|'contain'`, `focus:[fx,fy]` (0..1 crop anchor, e.g. `[.5,.3]` keeps faces), `zoom` (push-in: `lerp(1.15,1,p)`), `radius`, `filter` (canvas filter string, e.g. `'grayscale(1) contrast(1.1)'`), `alpha`.
Clip frames are prefetched and `renderFrame` waits for them, so output is always complete.
To mask media into a shape, wrap it: `c.save(); c.beginPath(); c.arc(...); c.clip(); image(...); c.restore()`.
Put text over footage only on a scrim (a linear gradient to `rgba(0,0,0,.6)`) or a solid panel.

## Timeline
```js
Reel.start({
  scenes: [{ name, start, draw(c, t, T) }, ...],          // end = next start
  transitions: [{ type, from, to, start, end, ...opts }],   // spans the boundary
  cues: [{ t, type, gain, shake, flash, ... }],             // picture + sound
});
```
Transition types:
- `whip {axis:'x'|'y', dir:1|-1}`: motion-blurred push.
- `iris {x, y, stroke}`: circle reveal from a point (0..1 coords).
- `fade`
- `wipe {angle, color}`: hard diagonal edge with a leading bar.
- `zoom {x, y}`: punch through A with a flash, then B settles in.

In-scene overlays for the last beats of a scene: `stripesWipe(c, t, t0, dur, color, n)` and `barsWipe(c, t, t0, dur, color, n)`.
Camera shake and flash come from cues (`shake`, `flash` 0..1). Set strength with `REEL_CONFIG.shake` (px) and `theme.flash` (colour).

## Config (`window.REEL_CONFIG`)
`w h fps duration bpm theme fonts fontLoads displayTracking shake vignette fadeIn fadeOut hud{title, left, sections:[[t,'LABEL']]} | null music{...}`

## Custom scene recipe
```js
S.callout = (c, t, T) => {
  bgFill(c, TH.bg);
  clip(c, 'demo', t, M, M, W * .6, H - 2 * M, { radius: 18 * U, zoom: lerp(1.1, 1, E.outCubic(P(t, 0, 3))) });
  const p = E.outBack(P(t, 1, 1.35));                       // lands on beat 2 at 120 BPM
  pill(c, W * .66, H * .4, 'AUTO-SAVES', { fg: TH.accentInk, bg: TH.accent, p });
  riseText(c, 'Never lose work.', W * .66, H * .55, fit(c, 'Never lose work.', 600, FD, W * .3, 90 * U), 600, FD, TH.fg, t, .4);
};
```
