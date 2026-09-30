# Process a stream: `/process-stream <video.mp4>`

Goal: from one raw livestream produce **transcript, subtitles, a chapter list and one clip per feature/topic**, all named per `folders.md`.

```
SKILL=<this skill's base directory>
python3 $SKILL/scripts/stream.py doctor
```

## 1. Set up the folder
`python3 $SKILL/scripts/stream.py init <root> --source <video>` creates the folders and moves the video into `source/` (same disk = instant) and writes `stream.json`. Use `--slug` if the filename makes an ugly slug. If the folder already has files in the old layout, offer `migrate` (dry run first).

Ask only what you can't work out: which **topic** the stream is about (decides what a "feature" is: product announcements, tutorial steps, guests, segments) and whether to clip *everything* or only some features.

## 2. Transcribe (slow: run in the background)
`python3 $SKILL/scripts/stream.py transcribe <root> [--model small.en|medium.en|large-v3] [--language xx]` writes the transcript (json + timestamped txt) and the full `.srt`. About 15–20 min of compute for a 2h stream on `small.en` (CPU). Progress: `<root>/.work/progress.txt`. Run it in the background (Claude Code: Bash `run_in_background`; any agent: `nohup … > .work/job.log 2>&1 &` and poll `.work/progress.txt`) and only do work that doesn't depend on it meanwhile.
Whisper small misspells names and product terms ("Tejal" → "tato", "Sol" → "soul"). Fix names in the chapter titles, and tell the user the transcript is unedited.

## 3. Find the chapters (judgement, not a script)
Read the transcript in ~30s blocks (build a compact view: one line per 30s with the start second). Decide:
- where the **real content starts and ends** (skip pre-show chatter, countdowns, breaks) and mark those chapters `"clip": false` so they appear in the chapter list but get no clip;
- one chapter per **feature / topic / step / segment**, in order, contiguous. A chapter is a single idea a viewer could watch alone (30s–8min). Merge tiny ones; split a long demo at natural turns (separate clips for separate demo parts).
- snap starts to a **segment start** in the transcript (whisper segments are 3–10s, so boundaries are ±a few seconds; end = the next chapter's start).
- chapter titles: short, specific, Title Case, no hype. The first chapter must start at `0`.

Write `chapters/<slug>.chapters.json`:
```json
{ "chapters": [
  { "title": "Pre-show chat", "start": 0, "clip": false },
  { "title": "Dots, always-on agents", "start": 2235.5, "end": 2650.2 },
  { "title": "Our reactions", "start": 5341, "clip": false }
] }
```
(`end` optional: defaults to the next chapter's start; `clip` defaults to true; `slug` overrides the kebab name of the clip.)

## 4. Cut clips, transcripts, subtitles, chapter files
`python3 $SKILL/scripts/stream.py clips <root> [--only 3,4] [--force]` writes `clips/<slug>--NN-<feature>.mp4`, the per-clip transcript and `.srt`, and `chapters/<slug>.chapters.md` + `.chapters.txt`. Existing clips are skipped unless `--force`. Re-encodes (libx264 crf 20) so cuts are frame-accurate.

## 5. Report
Give the user: number of clips and the folder, the chapter block (paste-ready, from `chapters.txt`), and any caveats (transcript accuracy, chapter starts snapped to segments, what was left out and why). Offer next steps: `/make-shorts <topic>`, a summary reel (`longform/`), X/YouTube chapter post.

## Summary reel (longform), when asked
"Summary video of all features": one short excerpt (10–14s) per feature chapter, a title bar (top-left, not over a facecam) with `NN / total  Title`, a 4s intro card and a 4s outro card. Pick each excerpt's start from the transcript phrase that states the feature (the line an announcer would say to introduce it). Write `longform/<slug>--summary--vN/reel.json`:
```json
{ "title": "OpenAI DevDay 2026", "subtitle": "Every announcement in five minutes",
  "outro": ["Full keynote clips and transcripts", "Watch the whole stream on my channel"],
  "items": [ { "title": "Dots - always-on agents", "start": 2295.4, "dur": 14 } ] }
```
(`start` = source seconds.) Build: `python3 $SKILL/scripts/stream.py reel <root> --name summary [--version N]`, which writes the mp4, `<folder>.chapters.md` (chapter timings for the reel itself) and the manifest. Check two frames (intro card, one excerpt) before reporting.

## Chapters for X / YouTube
- Paste block = `0:00 Title` lines, `h:mm:ss` once past an hour; the first line must be `0:00`; chapters ≥ 10s for YouTube to accept them.
- X posts are short: if there are more than ~12 chapters offer a trimmed list of the biggest announcements.
- The reel's chapters and the full stream's chapters are different files with different timings: always say which video a list belongs to.
