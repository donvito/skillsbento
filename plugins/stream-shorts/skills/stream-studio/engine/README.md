<!-- Vendored copy of the motion-reel engine used by clips-to-shorts. Paths below refer to this engine/ folder. -->

# Motion Reel

Code-driven motion design: a canvas engine where `renderFrame(T)` draws the exact frame at time T. Clips are pre-extracted to frame sequences, so any footage works (Playwright's Chromium can't decode H.264). Picture and sound share **one cue list** defined in the page, so cuts, impacts and whooshes always line up.

```
SKILL=<clips-to-shorts>/engine      # scripts/ assets/ references/
project/ index.html  engine.js  media/manifest.json  fonts/  out/{frames,stills,sheet.png,score.wav,*.mp4}
```

## Workflow

**0. Check tools** — `bash $SKILL/scripts/check_env.sh` (ffmpeg w/ libx264, python3 + numpy, scipy, playwright + chromium). It prints the fix for anything missing.

**1. Brief (ask only what you can't infer).** Subject, audience, length (default 30s), format (16:9 1920×1080 / 9:16 1080×1920 / 1:1), fps (60; use 30 when footage is 24–30fps-heavy), BPM (120 default; 100 calmer, 128 punchier), CTA, and which media to use. If the user has a website or repo, **derive the brand from it**: read theme tokens/CSS variables, font files, logo, real copy and real numbers. Match their look (e.g. a black-and-white site → monochrome reel). Never invent stats, clients, testimonials or logos; illustrative UI/terminal text is fine but say so.

**2. Scaffold** — `python3 $SKILL/scripts/new_project.py <dir> --preset landscape|portrait|square [--size WxH] --fps 60 --duration 30 --bpm 120 --title "BRAND — REEL"`. Put projects outside git repos, or rely on the generated `.gitignore` (out/ and media frames are large).

**3. Look at the footage before choosing it.**
`python3 $SKILL/scripts/ingest.py probe <files...> --out <dir>/out/probe` prints duration / fps / size / audio / scene cuts and writes a thumbnail sheet per file. **Read the sheets** to pick the best moments (motion, faces, product close-ups), the in/out points and a focus point for cropping.

**4. Ingest** — `python3 $SKILL/scripts/ingest.py add <dir> hero=clip.mp4@12.5-18 demo=screen.mov@3+4 logo=logo.png portrait=me.jpg`
Ranges are `@IN-OUT` or `@IN+DUR` in seconds; ranges over 20s are refused unless you pass `--long`, so keep them tight. Clips become `media/<id>/00001.jpg…` at min(source fps, project fps), sized to cover the canvas, plus `media/<id>.wav` if they have sound. For a user's soundtrack, run `ingest.py music <dir> track.mp3` and set `music: {mode:'file', src:'media/music.wav', offset}`. Use `ingest.py list <dir>` to show what's available.

**5. Storyboard on the beat grid, then write the scenes.** `BEAT = 60/BPM`; cut on beats, land big moments on bar lines (every 4 beats), and put transitions across boundaries. Write a short table first: scene · start–end · visual · motion · transition · sound cue. Then edit `index.html`:
- `REEL_CONFIG`: theme colours, fonts (brand font files in `fonts/` + `@font-face`, and list them in `fontLoads`), `hud`, `music`.
- `CONTENT`: all copy and media ids.
- `S.*` scenes + `Reel.start({scenes, transitions, cues})`.

The template is a **starting point, not the design**. Rewrite, add or remove scenes so they fit the subject: a product demo needs screen-recording close-ups with callouts, a portfolio needs work to breathe, a talk promo needs the speaker's clip with captions. Read `references/engine-api.md` for helpers and `references/motion-design.md` for the craft rules.

**6. Review stills — required, and repeat until clean.** `python3 $SKILL/scripts/render.py sheet <dir> [--every 1.5 | --times 3.2 9.5 …]` then **Read `out/sheet.png`**. Check transition midpoints too. Fix overlaps, clipped or illegible text, empty frames, off-brand colours, text on busy footage without a scrim, and bad crops (set `focus:[x,y]`). For a single frame use `render.py stills <dir> 12.5`. For live preview, serve the project dir and open `index.html#play`.

**7. Build** — `python3 $SKILL/scripts/build.py <dir> [--out path.mp4] [--grain 3] [--crf 19]`. This runs cues, frames, score, then an H.264 encode at −14 LUFS. Afterwards extract 1–2 frames from the MP4 (`ffmpeg -ss T -i out.mp4 -frames:v 1 x.png`) and look at them. The build warns if any clip frames failed to load. For a picture-only rebuild after an audio tweak use `--skip-frames`; `--no-audio` makes a silent video.

**8. Deliver.** Give the path, size, format, a scene-by-scene summary, and which content is illustrative. You can't hear the audio, so say so and invite a listen. Offer a variant: a 9:16 cut (new project with `--preset portrait` and the same `media/`, symlinked or re-ingested), another music style, or a shorter 15s edit. Don't commit large MP4s to git; suggest hosting them instead.

## Sound

`music.mode`: `synth` (style `energetic` 4-on-the-floor · `minimal` soft kick + plucks · `cinematic` toms + ostinato; mood `dark` · `bright` · `epic`; optional `sections:[{start,end,level:'full'|'light'|'none'}]`), `file` (user track, with SFX layered at `sfx` gain), or `none`.
Cue types: `impact`, `whoosh{dur}`, `riser{dur}`, `blip{note}`, `stab`, `bell{note}`, `tick`, `typing{dur,cps}`, `clip_audio{id,in,dur,gain,duck}`. Music ducks automatically under `clip_audio`. Add `shake`/`flash` (0–1) to any cue to drive the camera. Mark the final hit with `end:true` so the outro chord starts there.

## Gotchas
- Media referenced but not ingested renders as a hatched placeholder. That's useful for layout, but make sure none are left before building.
- Scenes receive negative `t` while an incoming transition shows them, so gate animations with `P(t, a, b)`.
- Everything must be a pure function of time: no `Math.random()` (use `rng(seed)`) and no state carried between frames. Simulations must re-run deterministically from t=0.
- Fonts: Google Fonts need network at render time; local font files are safer. Always list the faces in `fontLoads`.
- Render time is roughly 1 minute per 30s at 1080p60 (8 workers). Clip-heavy reels are slower, and more parallel workers help.
