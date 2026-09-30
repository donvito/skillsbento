# stream-shorts (Stream Studio)

One skill, `stream-studio`, for the whole livestream-to-content pipeline:

```
raw stream ──► transcript + subtitles + chapters ──► one clip per feature ──► summary reel / 9:16 shorts ──► YouTube copy
```

- Standard folder layout with linked file names (clip, transcript, subtitles, chapters and thumbnail share a stem)
- `/process-stream video.mp4` (Claude Code): transcribes, finds each feature, cuts one clip per feature, writes paste-ready chapters
- `/make-shorts <topic | clip>` (Claude Code): animated 9:16 shorts with your camera, word-synced captions, a frame-0 hook, real footage, YouTube title and description
- Summary reels with their own chapter timings
- Every short and reel lives in a `--vN` folder with its inputs, so it can be regenerated

In Codex there are no plugin slash commands: ask in plain words or use `$stream-studio process my stream video.mp4`.

## Install

```
# Claude Code
/plugin marketplace add donvito/skillsbento
/plugin install stream-shorts@skillsbento

# Codex
codex plugin marketplace add donvito/skillsbento
codex plugin add stream-shorts@skillsbento
```

## Requirements

- ffmpeg (with libx264) and ffprobe
- Python 3.10+: `pip install numpy scipy pillow playwright faster-whisper && python3 -m playwright install chromium`
- An emoji font (built into macOS; on Linux `apt install fonts-noto-color-emoji`)

Check everything: `python3 <plugin>/skills/stream-studio/scripts/stream.py doctor`.

## Folder layout

```
<stream folder>/
  stream.json                        slug + source path
  source/                            raw stream (untouched)
  clips/                             <slug>--NN-<feature>.mp4
  shorts/<slug>--short-<topic>--v1/  short.json, page.html, mp4, png, YOUTUBE.md, manifest.json
  longform/<slug>--summary--v1/      reel.json, mp4, chapters, png, manifest.json
  transcripts/  subtitles/  chapters/  thumbnails/
```

Full rules: [`references/folders.md`](skills/stream-studio/references/folders.md). An existing folder can be moved into this layout with `stream.py migrate <folder>` (dry run first, `--apply` to move).

## Good to know

- The agent reads transcripts, not audio: it can't hear tone or music, and Whisper-small mishears names. Check names and titles.
- Chapter starts snap to transcript segments (a few seconds of slack).
- Nothing is posted for you: titles, descriptions and chapters are given as paste-ready text.
