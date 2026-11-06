# motion-reel

Code-driven motion graphics as MP4: showreels, promo and launch videos, kinetic-typography intros, social teasers and 9:16 Shorts / Reels / TikTok cuts, built from your own clips, photos, logos, screenshots and brand.

- **Deterministic rendering:** a canvas engine where `renderFrame(T)` draws the exact frame at time T. It renders in headless Chromium and encodes with ffmpeg, so any footage works and every render is reproducible.
- **Beat-synced sound:** picture and sound share one cue list, so cuts, impacts and whooshes always line up. The music can be built-in synth beds (energetic, minimal, cinematic), your own track, or none.
- **Uses your real material:** it probes footage and makes thumbnail sheets to pick the best moments, ingests tight clip ranges, and takes its colours, fonts and copy from your site or repo.
- **Any format:** 16:9, 9:16 or 1:1, at 30 or 60 fps.
- **Review before build:** contact sheets and stills are checked for overlaps, clipped text and bad crops before the final encode.

## Requirements
`ffmpeg` (with libx264), Python 3 with `numpy`, `scipy`, `playwright` (+ `playwright install chromium`). Run `bash skills/motion-reel/scripts/check_env.sh` to check; it prints the fix for anything missing.

## Try it
- *"Make a 30s promo reel from these clips and my logo"*
- *"Turn this screen recording into a 9:16 Short with captions"*
- *"Make a kinetic-typography intro for my channel, match my website's look"*

## What's inside
```
skills/motion-reel/
  SKILL.md                  workflow: brief, scaffold, probe, ingest, storyboard, review, build
  references/engine-api.md  engine helpers, scenes, transitions, cues
  references/motion-design.md  craft rules
  scripts/                  check_env, new_project, ingest, render (stills/sheets/frames), score, build
  assets/                   engine.js, reel.html template
```

The default template loads Inter Tight and JetBrains Mono from Google Fonts at render time. For offline renders, put local font files in the project's `fonts/`.
