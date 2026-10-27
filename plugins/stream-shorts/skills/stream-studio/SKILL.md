---
name: stream-studio
description: End-to-end workflow for a livestream/VOD folder. Organizes the stream into a standard folder layout (source, clips, shorts, longform, transcripts, subtitles, chapters, thumbnails) with linked file names, transcribes it, finds each feature/topic and cuts one clip per feature, writes chapter timings (X/YouTube paste-ready), builds summary/highlight reels, and makes animated 9:16 YouTube Shorts (split-screen or full-frame overlay with the creator's camera, word-synced captions, frame-0 hook, real footage mixed in; built-in `grok` style for Grok/xAI topics and `claude` style for Claude/Claude Code/Anthropic topics) with YouTube titles and descriptions, every version reproducible. Use for /process-stream and /make-shorts, or whenever the user wants clips, a transcript, chapters, subtitles, a summary video, shorts/reels or YouTube copy from a stream, keynote, webinar, podcast or recording.
---

# Stream Studio

One skill for the whole pipeline: **raw stream → transcript + chapters + clips → summary reel / shorts → YouTube copy.** All files follow one folder layout and naming scheme so a clip, its transcript, subtitles, chapters and thumbnail always link together, and every video is rebuildable from its version folder.

```
SKILL=<this skill's base directory>
$SKILL/scripts/stream.py     doctor · init · transcribe · clips · reel · short-new · short-build · migrate
$SKILL/scripts/short.py      shorts engine front end: doctor · brand · transcribe · frame · cut · scaffold · balance
$SKILL/engine/  assets/      motion-reel renderer, kit.js, fonts
$SKILL/references/           folders.md · process-stream.md · make-shorts.md · style.md · styles.md · kit-api.md · youtube.md
$SKILL/assets/styles/        grok.json · claude.json · editorial.js · overlay.js · split.js · template-overlay.html · template-split.html
```

## Which workflow?

| the user says | do | read |
|---|---|---|
| `/process-stream video.mp4`, "clip my stream", "transcript", "chapters", "subtitles" | process the stream | `references/folders.md`, then `references/process-stream.md` |
| "summary video of all features", recap, highlight reel | summary reel (longform) | `references/process-stream.md` → Summary reel |
| `/make-shorts <topic or file>`, "make a short", "vertical", "reel" | make shorts | `references/folders.md`, then `references/make-shorts.md` (+ `style.md`, `kit-api.md`, `youtube.md`; `styles.md` when a style applies) |
| a short about Grok / Grok Bot / xAI, or Claude / Claude Code / Anthropic; "Grok style", "Claude style", "overlay, no box" | make shorts with a style | `references/styles.md`: `"style": "grok"` or `"claude"` in short.json |
| "chapter timings I can paste in X/YouTube" | chapters | `references/process-stream.md` → Chapters |
| "title and description" | YouTube copy | `references/youtube.md` |

A request often chains them ("process this stream and make a short on dots"): do `/process-stream` first, then shorts from the clips.

## Works in Claude Code and Codex

- The skill is the same in both. `/process-stream` and `/make-shorts` are Claude Code commands only; in Codex ask in plain words or mention the skill (`$stream-studio process my stream video.mp4`, `$stream-studio make a 30s short about <topic>`).
- Tool names in these docs are generic: "run in the background" = Claude Code's Bash `run_in_background`, or in any agent `nohup <cmd> > .work/job.log 2>&1 &` and poll the log; "ask the user" = a question tool if you have one, otherwise a short numbered list in chat; "look at a frame" = open the PNG with your image-viewing tool.
- Python scripts locate themselves (`$SKILL` = the folder holding this file), so the skill works from any install location.

## Always

1. **Folder layout first.** The user's working directory is usually the stream's root folder. Check for `stream.json`. If it's missing, run `stream.py init` (new stream) or `stream.py migrate` (old layout, dry run first). Never write outputs loose in the root.
2. **Name by convention.** `<slug>--NN-<feature>.mp4`, `<slug>--short-<topic>--vN/`. Details in `references/folders.md`.
3. **Version, don't overwrite.** A changed short or reel is a new `--vN` folder holding its inputs (`short.json`, `page.html`, `reel.json`) so it can be regenerated. Keep old versions.
4. **Run `stream.py doctor`** before the first heavy step; it prints the fix for anything missing.
5. **Long jobs in the background** (transcription, clip cutting, rendering). Don't sleep-poll; do independent work or wait for the completion notice.
6. **Ask which style for every new short**, in the same intake round: `grok` (Grok Bot black/white/grey with serif type), `claude` (Claude ivory + terracotta) or the default neon look. Recommend the one that fits the topic (Grok/Grok Bot/xAI → `grok`, Claude/Claude Code/Anthropic → `claude`, anything else → neon). Don't ask if the request already names a style or you're making a new version of an existing short (keep its style). See `references/styles.md`.
7. **Otherwise ask only what you can't work out**, all in the same round: brand/handle (shorts), which topics/features, camera setup. Look in the folder first (existing `brand.json`, previous versions, frames).
8. **Be honest about limits.** You read transcripts, not audio: you can't hear tone, music or audio levels, only check levels with `short.py balance`. Whisper-small mishears names. Chapter starts snap to transcript segments (±seconds). Webcams that are small get soft when upscaled. Mock UI and animated counters are illustrative: say so. Don't invent claims, stats, handles or links; quote on-screen facts only.
9. **Verify before reporting**: look at frames (contact sheet) of anything you render, frame 0 of every short, and the duration. Report paths, durations and caveats; don't paste whole documents into chat.
10. **Publishing steps are the user's**: don't post to X/YouTube. Give paste-ready text.
