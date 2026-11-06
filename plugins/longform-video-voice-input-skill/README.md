# longform-video-voice-input-skill

Turn a recorded voiceover into a polished, faceless long-form YouTube explainer (16:9, 3–20 min).

- **Voice edit that keeps sync:** word-level transcript, then a simple edit list. It handles pickup lines (a re-recorded intro at the end of the file), retakes, stumbles and long pauses. Every word's new timing drives the animations.
- **Word-synced motion graphics:** headlines rise on the spoken word, chat and phone mockups, photo cards, concept animations, and big centered "spoken openers" so the screen is never empty.
- **Real proof:** your own app screenshots and screen recordings in phone mockups with magnified call-outs, real web pages captured at phone or desktop size, free Pexels/Unsplash photos and b-roll (downloaded by id, no API key).
- **Versioned renders:** every update becomes a new version (`video_vN/`, `output/<slug>-vN.mp4`, `CHANGELOG.md`). Only the changed time ranges are re-rendered, and older versions are never overwritten.
- **Default look:** monochrome black/white/gray, plain backgrounds, no small headings, voice-only audio at −14 LUFS. See `skills/longform-video-voice-input-skill/references/style.md`.

## Requirements
`ffmpeg` (with libx264), Python 3 with `numpy`, `scipy`, `pillow`, `playwright` (+ `playwright install chromium`) and `faster-whisper`; optional `noisereduce`. Run `bash skills/longform-video-voice-input-skill/engine/scripts/check_env.sh` to check.

## Try it
- *"Make a YouTube explainer from my voice recording `talk.wav` and the screenshots in `shots/`"*
- *"There's a stumble around 6:30, cut it and make a new version"*
- *"Fix the overlapping boxes at 2:13 and add some b-roll there"*

## What's inside
```
skills/longform-video-voice-input-skill/
  SKILL.md                 workflow + the versioning rule
  references/style.md      default house style and scene recipes that worked
  scripts/                 transcribe, edit_voice, enhance_voice, finalize_audio, render_frames,
                           blank_scan, stock, web_capture, make_srt, version
  assets/                  lib.js, parts.js, media.js (visual library), index.template.html, fonts/ (SIL OFL)
  engine/                  vendored motion-reel canvas engine + renderer
```

Stock media stays under its own licence (Pexels / Unsplash licences). Screenshots of third-party sites belong to their owners: label them on screen and in your description.
