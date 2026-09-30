# Make shorts (9:16)

Workflow for `/make-shorts`. Folder layout and file naming come from `folders.md`; read it first. `SKILL` below is the skill's base directory.

Split-screen shorts rendered by a bundled motion-reel engine (deterministic canvas → headless Chromium → ffmpeg).

```
SKILL=<this skill's base directory>
$SKILL/scripts/short.py         doctor · brand · transcribe · frame · cut · scaffold · balance
$SKILL/engine/scripts/          render.py (stills / contact sheet) · build.py (MP4)
$SKILL/assets/                  kit.js (layout + animation helpers) · template.html · fonts/ (OFL)
$SKILL/references/              style.md (read before storyboarding) · kit-api.md · youtube.md
```

Layout (1080×1920): the **top 0–960 is the animated stage** and the **bottom 960–1920 is the camera**, filling half the screen. Captions sit on the seam between them, with a progress bar on top, the creator's handle as a watermark, and a 1.2–1.5s branded end card.

## 1. Intake: ask only what you can't work out

Before cutting anything, make sure you know the items below. Look first: check the files the user pointed at, any existing `brand.json` (next to the clips, in parent folders, or `~/.config/clips-to-shorts/brand.json`), earlier shorts, and the handle visible in the recording. **Ask about anything still missing in one round**, using the AskUserQuestion tool if it's available (otherwise a short numbered list in chat), and offer sensible defaults as options:

| needed | when to ask | default to offer |
|---|---|---|
| **Source**: which recording(s) or clip folder | always, unless given | — |
| **How many shorts + tone**: funny / educational / mix | if not stated | 3, mix |
| **Brand**: handle, tagline, LIVE badge yes/no, colours/fonts | no brand.json found | neon pink/cyan/yellow on black · Anton + Space Grotesk |
| **Camera setup**: facecam inside the recording / separate camera file / no camera | can't tell from a frame (run `frame` first and look) | the facecam box you found |
| **Camera sync offset** | separate camera file given | match a spoken word in both transcripts and say what you found |
| **Language** | the transcript isn't English | the detected language |
| **Output folder** | never | a version folder `shorts/<stream>--short-<topic>--vN/` (see `folders.md`) |

Save the brand once with `short.py brand --handle @x [--tagline ..] [--ring ..] [--live] [--accent1 #hex --accent2 #hex --highlight #hex] [--display-font f.ttf]`. By default it writes `~/.config/clips-to-shorts/brand.json`, which every future short reuses. **Whenever a script prints `NEEDS_INPUT:`, ask the user those questions, then re-run.** Don't guess a handle, an offset, or which moments the user wants when they've said they care.

## 2. Workflow

**Use the versioned helpers** (`stream.py short-new` / `short-build`, see "Versioned, reproducible output" below): they replace the manual `--out` paths in steps 3–7 and keep every version rebuildable.

**0. Check tools.** Run `python3 $SKILL/scripts/short.py doctor`. It checks ffmpeg/libx264, numpy, scipy, pillow, playwright + chromium, faster-whisper and an emoji font, and prints the fix for each ✗.

**1. Find the moments.** Run `short.py transcribe <clips...> --out <work>/words [--language xx]`. It prints the transcript, word timings and a speech-energy map. Pick the moments:
- *Funny*: complaints, contradictions, stutters, self-owns, a viewer quote, anything with a reversal or a built-in punchline.
- *Educational*: concrete steps, before/after, real numbers shown on screen, "X vs Y".

Aim for **15–20s of speech**. Plan the jump cuts: drop filler, pauses and repeats, but keep a stutter when it's the joke. A cold open with the punchline is allowed. If the user wants to choose, propose the candidates with one-line pitches and let them pick.

**2. Find the camera and screen boxes.** Run `short.py frame <video> --t 5 --out f.png`, then Read it. Zoom in with an ffmpeg crop to get exact edges. Use one of these setups in short.json:
- `"face": [x,y,w,h]`: a facecam inside the recording. Use aspect ≈ 1.125 so it fills the half without bars, and shift the box so the face sits at about 55%.
- `"camera": {"file", "offset", "box"?, "audio": "clip"|"camera"}`: a separate camera recording, which gives much sharper results.
- `"bottom": "full" | [x,y,w,h]`: no camera, so the bottom half shows the screen.

Also note real on-screen content worth reusing (posts, dashboards, docs, code). Moving crops go in `screens` and single frames in `stills`. Keep stream overlays like chat, widgets or the facecam out of those crops.

**3. Write `short.json` and cut.** See `short.py --help` for the schema. Set `kind` and `language`. Run `short.py cut short.json`; cut points snap to the nearest silence. **Read the printed "cut reads:" line.** If a word is clipped or a filler slipped through, adjust `segs` and re-run.

**4. Scaffold.** Run `short.py scaffold short.json`. This creates the project, brands it, copies fonts and `kit.js`, ingests the media, normalizes the voice, and writes `index.html` with draft captions.

**5. Storyboard, then write the page.** Read `references/style.md` and `references/kit-api.md`. Write a short table (beat · time range · words · visual · SFX), then edit `index.html`:
- **CAPS:** 1–4 words each, fix mishearings, `*star*` the punchline words, and split anything that wraps to two lines.
- **BEATS:** beat 0 is the **hook**, drawn complete at T=0. Change the beat every 1.5–3s, landing on spoken words.
- **Punch-ins:** add `faceCam` punch-ins on emphasis words, and a cue for every stamp or impact.

**6. Review stills and repeat until clean.** Run `python3 $SKILL/engine/scripts/render.py sheet <proj> --times 0 … --cols 4` with one time per beat, then Read `out/sheet.png`. Fix overlaps, text touching the edges, stamps covering content, two-line captions, and overlays leaking into crops.

**7. Build and verify.** Run `python3 $SKILL/engine/scripts/build.py <proj> --out <out>/short-NN-<slug>.mp4 --grain 0 --crf 18`, then `short.py balance <proj>`. The target is SFX+music ≤ −11 dB under the voice. If it's louder, lower `music.sfx` or raise the `duck`, then rebuild with `--skip-frames`. Check frame 0 of each MP4 as a thumbnail.

**8. Deliver.** For each file, give its duration and a one-line gag summary. Write titles and descriptions to `<out>/YOUTUBE.md` (see `references/youtube.md`) and show the titles in the reply. Say which counters and UIs are illustrative, flag third-party names or handles visible on screen, mention a soft facecam if it was upscaled, and note you can't hear the audio.

## Rules
- Frame 0 is the thumbnail: a big claim and a twist, readable in under a second.
- Everything is a pure function of time. Use `rng`/`noise1`, never `Math.random`.
- Use only the speaker's real claims and on-screen facts. Mock UIs and animated counters are fine if you say they're illustrative.
- The voice stays on top: `music.sfx ≈ .22`, `duck ≈ .96`, then verify with `balance`.
- Never invent a creator's handle, links or sponsors. Ask.

## Versioned, reproducible output

Every short lives in its own **version folder**, never loose files (details in `folders.md`):

```
shorts/<stream>--short-<topic>--v1/
  short.json        clip, segs, camera box, stills, screens
  page.html         the authored index.html (captions, beats, cues): the source of truth
  kit.js            only if this version needs a modified kit
  <folder-name>.mp4 the short      <folder-name>.png  frame-0 thumbnail
  YOUTUBE.md        titles + description        manifest.json  what built it
  project/          generated by scaffold, safe to delete and regenerate
```

Use the helpers instead of hand-running steps:

```
python3 $SKILL/scripts/stream.py short-new <root> --topic dots --clip <stream>--02-dots.mp4 [--from-prev]
python3 $SKILL/scripts/stream.py short-build <dir> --scaffold-only    # cut + scaffold, then edit <dir>/project/index.html
python3 $SKILL/scripts/stream.py short-build <dir> --save-page        # keep project/index.html as page.html, build, thumbnail
python3 $SKILL/scripts/stream.py short-build <dir>                    # regenerate everything from short.json + page.html
```

"Make a new version" = `short-new --from-prev` (copies the last short.json + page.html into `v(N+1)`), change it, `--save-page`. Older versions stay untouched and rebuildable. The source clip is referenced by relative path, so never rename files in `clips/` after a short depends on them.

## Lessons from real shorts

- **Hook from the creator's reaction**: if the user asks for "a clip where I was excited", find the reaction words in the transcript (wow, whoo, let's go, oh no…) and check the camera frame. Say honestly that you can't hear tone. Open on that moment and keep the requested visual (e.g. the product logo on the big screen) on frame 0.
- **Frame 0 must already show the requested visual**: if the source only reveals it a few frames in, add a `stills` crop of the same shot and cross-fade it into the moving footage over the first ~0.5s.
- **Camera size**: the camera is big (50%) when the creator is the one talking. When the keynote/demo speaker is talking and the creator is silent, shrink the camera to a strip: animate `SEAM` (for example `SEAM = lerp(960, 1320, E.ioCubic(P(T, 2.9, 3.4)))` at the top of `S.main`; reset `SEAM = 960` in `S.end`). Use `faceCam(..., {focus: [.5, .85]})` so the face (not the forehead) stays in the strip, and check a frame.
- **Mix in real presentation footage**: add a moving crop under `screens` (for a stream with a facecam in the corner use the region that excludes the facecam, e.g. `[350, 0, 1570, 1080]`) and draw it with `clip(c, 'pres', T, 0, 0, W, SEAM, {fit: 'cover', focus: [fx, fy]})`. Pick `fx` per beat from a contact sheet. For demo videos that fill the frame use `fit: 'cover'` inside a framed card; do not blur the backdrop (canvas blur bands badly). Use `stills` for UI callouts when the camera angle changes during the beat.
- **Clipped word endings**: after `cut`, read the "cut reads:" line. Extend a segment's end by 0.15–0.3s if a word is truncated ("agents" → "a").
- **Hidden counters**: draw count-ups only once they start (no "0" before the word).
- **Text width**: check labels against the 1080px width on the contact sheet (letter-spaced labels overflow first).
- **Platform notes**: macOS `sed -i ''`; zsh does not word-split unquoted variables, so use literal loops.
