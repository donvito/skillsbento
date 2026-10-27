# Styles: `grok` and `claude`

Two refined, editorial looks on top of the kit, picked per short with `"style"` in short.json. `"style": "neon"` (or no `"style"`) uses the stock neon kit exactly as before.

| style | for | look | layouts |
|---|---|---|---|
| `grok` | Grok, Grok Bot, xAI content | Monochrome Grok colours: black, white and greys. Black Grok-UI cards for Grok things, white paper cards for everyday things | `overlay` |
| `claude` | Claude, Claude Code, Anthropic content (Opus, Sonnet, Haiku, MCP, skills) | Warm ivory paper, ink text, Claude terracotta accents, soft shadows | `overlay` (default), `split` |

Both styles use the same type: **Source Serif 4** for headlines, with *italic* for emphasis words; **Inter** for UI and body text; **JetBrains Mono** for small kicker pills. All three are OFL and bundled in `assets/fonts`.

## Choosing a style

**Ask the user which style** in the intake round (AskUserQuestion if available), every time a new short starts. Offer all three and put the topic match first, marked "(Recommended)":

| option | recommend when the subject is |
|---|---|
| `grok`: Grok Bot black/white/grey, Source Serif + Inter | Grok, Grok Bot or xAI |
| `claude`: Claude ivory paper, ink, terracotta, Source Serif + Inter | Claude, Claude Code or Anthropic (Opus, Sonnet, Haiku, MCP, skills) |
| `neon`: the stock kit with the brand's colours | anything else |

- **Don't ask** when the request already names a style ("Grok style", "Claude look", "neon"), or when you're making a new version of an existing short (`short-new --from-prev`, or the user is iterating): keep its `"style"`.
- **Base the recommendation on the user's words and the folder or topic name, not only the transcript.** Whisper mishears product names ("RockBot" for Grok Bot). Each style also sets a whisper `prompt` with its product names, which fixes most of these. For a mixed topic (Claude vs Grok), recommend the hero's style.
- **Write the answer into short.json** as `"style": "grok" | "claude" | "neon"`, so the choice is recorded with the version.

## Layouts

- **`overlay`**: the camera fills the whole 9:16 frame. Motion graphics float over the wall above the head (y 0 to about 560) and the side strips (x < 190, x > 890). Captions sit on the chest (y ≈ 1478).
  - Use it for vertical selfie or phone recordings, and whenever the user doesn't want "the face in a box". This is the default for both styles.
  - `cut` builds `scr_cam.mp4` (clip id `cam`) covering 1080×1920. Add `"plate": [x,y,w,h]` to crop a landscape source to the person.
- **`split`** (claude only): the paper stage sits on top (0..SEAM) and the facecam below, like the kit, but with paper chips, a dot grid, a paper wipe and a terracotta seam.
  - Use it for stream facecams, where the face is too small to fill the frame.

## Precedence

- **The style owns the palette and fonts.** brand.json `colors` and `fonts` are ignored when a style is set.
- **brand.json still supplies** `handle`, `tagline`, `ring`, `live` and `cta`.

## short.json

```json
{
  "style": "grok",                      // or "claude"
  "layout": "overlay",                  // optional: the style's default
  "plate": [0, 0, 576, 1024],           // optional: overlay camera crop (default: whole frame)
  "images": {                           // optional: logos/avatars → image ids (not bundled: trademarks)
    "grok": "../../source/assets/botavatar.jpg",
    "gpt": "../../source/assets/chatgpt-logo.png"
  }
}
```

- With overlay and no `face`, `camera` or `bottom`, cut uses `"bottom": "full"`. That clip supplies the voice and the end-card ring.
- Real footage (a phone demo or a screen recording) still goes in `screens`. Use a `prep.sh` for anything cut from another file, then run `scaffold`.
- Logos: `logo()`, `phone()` and the template's hook skip any id that isn't present. A missing logo never draws a placeholder box.

## How scaffold builds it

- `project/kit.js` = the stock kit.js + `const STYLE = <style json>` + `const ST = STYLE.tokens` + `assets/styles/editorial.js` + `assets/styles/<layout>.js`.
- Because the version folder keeps that kit.js (`short-build --save-page` saves any non-stock kit), every version stays rebuildable even if the skill changes.
- The template is `assets/styles/template-<layout>.html`: the example beats show every recipe below.
- Captions are drafted in sentence case, and `WORDS` (word timings of the edit) are inlined into the page.
- `fonts/display-italic.ttf` is copied for the `"DisplayIt"` family.

## Tokens (`ST`)

| token | grok | claude | used for |
|---|---|---|---|
| `ink`, `paper`, `paper2` | #0B0B0C, #FFFFFF, #F4F4F2 | #141413, #FAF9F5, #E8E6DC | text, cards, card fills |
| `grey`, `grey2`, `line`, `hair` | greys | warm greys | labels, hairlines on paper / dark cards |
| `card`, `cardInk`, `cardDim` | Grok black | ink | dark UI cards and their text |
| `accent`, `hot` | ink, ink (*italic* carries emphasis) | terracotta #D97757, #C15F3C | scribbles, rings, hot caption words |
| `wash` | "247,247,245" | "240,238,230" | the paper wash over the wall (overlay) |
| `chip`, `chipInk`, `chipDim` | white chip, ink / dimmed ink | ivory chip | captions |
| `endBg`, `endFg`, `endDim`, `endRing` | black end card, white type | ivory end card, ink type, terracotta ring | end card |
| `stage` | — | ivory | split stage background |

In split pages `CL` is also defined (paper, ivory, oat, ink, slate, cloud, orange, crail, olive, sky, fig, red), matching the original Claude-style pages.

## Editorial primitives (`editorial.js`, both layouts)

| call | what |
|---|---|
| `serif(c, s, x, y, px, {it, align, color, s, alpha, dy, halo:false})` | serif headline (italic with `it`); a soft halo separates it from the wall; returns the width |
| `body(c, s, x, y, px, col, {w, align})` · `mono(c, s, x, y, px, col, {align, ls})` | Inter text · mono label |
| `kicker(c, T, t0, 'TEXT', x, y, {light, dot})` | mono pill (dark, or `light`), optional pulsing red dot |
| `rise(T, t0)` → `{a, dy, s}` · `inn(c, T, t0, x, y, fn)` | the house entrance: rise + settle with outBack. Use it instead of slam/pop |
| `paper(c, x, y, w, h, {r, fill})` · `dark(c, x, y, w, h, {r})` | paper card with a soft shadow · dark UI card with a hairline |
| `logo(c, id, x, y, size, {round, rot, s, bg, ringCol})` | app icon or avatar, masked; skipped if the id is missing |
| `scribble(c, x0, x1, y, p, col, lw)` · `ring(c, cx, cy, rx, ry, p)` · `stroke2(c, x0, y0, x1, y1, p, col, lw, bow)` | hand-drawn underline · circle a word · strike / arrow / X |
| `tick(c, x, y, r, p, fill, mark)` | checkbox that fills in |
| `bubble(c, T, t0, x, y, text, right, {dark})` | chat bubble anchored at its tail |
| `flip(c, T, t0, tFlip, x, y, w, h, emoji, label)` | blank card that flips to its label on the spoken word |
| `phone(c, T, t0, clipId, lt, x, y, w, h, {focus, zoom})` | real footage in a floating phone frame |
| `quote(c, T, t0, x, y, '“…”', '— source')` | pull-quote card (quote real on-screen text only) |
| `marquee(c, T, t0, 'A · B · C · ', y)` | scrolling mono band |
| `illus(c, x, y, align)` | "ILLUSTRATIVE" tag for mock UIs |

## Overlay layer (`overlay.js`)

| call | what |
|---|---|
| `overlayCam(c, T, {punches, hook:{until, zoom, focusY}, bw:[[a,b]], dim:[[a,b,amt]], wash})` | camera plate. `hook` starts close and lower for frame 0, then eases out. `bw` gives a black & white flashback with grain and a camera flash. `dim` darkens under a full-screen demo. `wash` can be a function of T, e.g. off under a dark cover hook |
| `runOverlay(c, T, BEATS, SPEECH)` | beats `[{a, draw(c, t, T, dur)}]`; each fades and drifts up over its last .16s. No stage, no box |
| `overlayCaptions(c, T, CAPS, WORDS, {hideUntil, y, px})` | paper chip with serif text; words go from dim to ink as they're spoken, and `*hot*` words show in italic in `ST.hot`. Caption text can be edited freely: lighting is proportional to the source words spoken |
| `overlayHandle(c)` · `overlayProgress(c, T, SPEECH)` | @handle at y 1600 · thin progress bar |
| `overlayEnd(c, t, T, {faceT, start, logos:[a,b]})` | style end card: face ring, ring text, LIVE, serif CTA + italic handle, optional logos |

## Split layer (`split.js`, claude)

`split.js` overrides the kit's `big card stamp bar stageBg runBeats faceCam captions progress endCard` with the editorial versions, so kit-api.md still applies.

## Recipes that worked (in the template as example beats)

1. **Magazine-cover hook (frame 0).** A dark panel, `ST.card` fading out by y≈740, covers the top.
   - Big app icons on the left: the subject's icon (210px) slapped over the comparison icon (150px), tilted.
   - A headline column at x≈436: subject (serif 108), a small grey line, then two big italic lines (132).
   - A light kicker pill with a red dot ("HOT TAKE").
   - `overlayCam` `hook` (start close), `wash` off until the hook ends, and `overlayCaptions` with `hideUntil` (the hook already says those words).
2. **Flashback.** `bw: [[a, b]]`, a kicker "FLASHBACK · <real date>", and a paper card of the old product UI.
3. **Chat bubbles** alternating paper / dark (`illus` them), then **notification banners** dropping from the top.
4. **"Not X"**: mono chips crossed out with a red `stroke2`, or ink on the claude style.
5. **List of people or roles**: `flip` cards that flip on each spoken word.
6. **Emphasis word**: italic serif with a `ring`, e.g. *again.* or *wife.*, plus a small paper status pill with a `tick`.
7. **Real demo**: `dim` the camera, `phone()` the clip, a red-dot kicker "REAL DEMO", and a `quote()` of the real on-screen text.
8. **Planner / task list**: a paper card with mono times, Inter tasks and `tick`s on the words. **Agent working**: a dark card with thin progress bars and ticks, then a paper pill "Meanwhile, you ☕".
9. **ID badge**: a dark card on a lanyard (decaying sway), with a paper "Hired ✓" pill.
10. **No code**: a dark code window typed with `typeText`, two red `stroke2` strikes, and a paper pill *No code needed.*
11. **Big claim**: a thin hand-drawn line chart drawing up behind, then an italic word at 260px with a mild scale settle (1.25→1, not a slam).
12. **Then → now**: a paper card (old product) and a dark card (new product) side by side; the old one dims when the new one lands.
13. **Payoff**: an italic line with a `scribble` underline, plus a `marquee` of who it's for.

## Rules of the look

- **Keep it refined, not comical.** No neon glows, sticker stamps, emoji crowds, VHS or glitch effects, or heavy shakes (impact shake ≤ .2).
- **Emoji are rare accents**, not the visual.
- **Motion is a rise and settle**, with ink or terracotta drawn strokes for emphasis.
- **Use real footage and real quotes as proof.** Tag mock UIs as illustrative.
- **Keep text off the face.** Overlays stay above y≈560 or in the side strips. Full-frame moments (a demo phone) dim the camera first.
- **Mind the Shorts safe zones.** Keep captions above y≈1560 and out of the right ~140px rail.
