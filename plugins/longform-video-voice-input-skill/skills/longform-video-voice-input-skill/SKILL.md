---
name: longform-video-voice-input-skill
description: Turn a recorded voiceover (WAV/MP3) into a polished, faceless long-form YouTube explainer (16:9, 3–20 min) with word-synced motion graphics, the user's own app screenshots/screen recordings, real web screenshots, free stock photos and b-roll. Edits the voice (pickup lines, retakes, stumbles, long pauses), keeps every animation synced to the spoken words, and versions every render (v1, v2, v3…). Use when the user gives a voice recording and asks for a YouTube video, explainer, faceless video, or long-form edit, or asks to update/tweak a video made this way.
---

# Long-form video from a voice recording

Bundles the motion-reel engine (canvas engine + Chromium renderer + `ingest.py`) in `engine/`. Read `engine/references/engine-api.md` once.
`SK=<this skill's base directory>`, `MR=$SK/engine`.

## Rule: every update is a new version
Every change to what is rendered (picture or audio) ships as a **new version**. Never overwrite a delivered MP4.
- `python3 $SK/scripts/version.py new <workdir> "<what changed>"` → creates `video_vN+1/` (code copied, media and rendered frames hard-linked, so it's instant and costs no disk).
- Edit files **only inside the new `video_vN+1/`**.
- `python3 $SK/scripts/version.py build <workdir> --from S --to S [--from S --to S …]` re-renders just the changed time ranges (pad ±0.5 s for transitions) and writes `output/<slug>-vN+1.mp4`. Use `--full` after global changes (palette, fonts, shared helpers), `--audio FILE --audio-only` for sound-only updates.
- `build` refuses to overwrite an existing version's MP4. If it says so, run `new` first.
- Every version gets a `CHANGELOG.md` entry. Tell the user the new filename and what changed versus the previous version.
- Re-review stills of the changed section from the **encoded MP4** before delivering.

## Workflow (first version)
1. **Check tools.** Run `bash $MR/scripts/check_env.sh`. You also need `faster-whisper`, `noisereduce` (optional), and Playwright Chromium.
2. **Transcribe.** `python3 $SK/scripts/transcribe.py "<voice>.wav" work/transcript.json` (medium.en, word timestamps). Read it and look for:
   - **Clipped first words:** the recording starts mid-sentence.
   - **Pickup lines:** a corrected line re-recorded at the end, often the intro.
   - **Retakes:** the same sentence said twice; keep the second take.
   - **Stumbles:** to confirm one, re-transcribe just that stretch with `--start S --dur D` (no VAD), plus a 100 ms loudness print.
   - **Long pauses.**
   - **Misheard names:** whisper writes "Rockbot" for "Grok Bot", "Chachipiti" for ChatGPT, "HART" for Hark. Use the user's spelling.
3. **Enhance, then edit.**
   - `bash $SK/scripts/enhance_voice.sh in.wav work/voice_enhanced.wav` uses the light chain and keeps the timeline.
   - Write `work/edit.json` (schema in `edit_voice.py`), then run `python3 $SK/scripts/edit_voice.py work/edit.json`. It writes `work/vo.wav`, `work/words.json` and `video_v1/vo.js`.
   - Tell the user exactly what you cut, and keep the uncut file.
   - If they enhance externally (e.g. Adobe Podcast), check alignment by cross-correlating loudness envelopes. Use their file only if it is offset-free; otherwise re-apply the edit list to it.
   - Run `python3 $SK/scripts/finalize_audio.py <voice> work/voice_final.wav --duration <video s>` for −14 LUFS, two-pass, linear.
4. **Ask only what you can't infer.** The defaults below already match this user. Confirm the app names shown in the screenshots. If a screen has no visible app name, say which one you assumed.
5. **Look at the media.** Make contact sheets of all screenshots and thumbnail strips of recordings. Downscale screenshots to 900 px wide. Ingest with `python3 $MR/scripts/ingest.py add video_v1 id=path …`, using `--long --no-audio` for screen recordings.
6. **Storyboard from the transcript, not a beat grid.** Write a table of scene · start–end · spoken words · visual. Start each scene just before its first word. Alternate light and dark scenes. Make one chapter card per section, but with no "CHAPTER 0X" label.
7. **Scaffold.**
   - `python3 $MR/scripts/new_project.py video_v1 --preset landscape --fps 30 --duration <s>`.
   - Copy `$SK/assets/{lib.js,parts.js,media.js}` in. Replace `index.html` with `$SK/assets/index.template.html`.
   - Copy fonts into `fonts/`: `cp $SK/assets/fonts/*.woff2 video_v1/fonts/` (Bricolage Grotesque 600/800, Inter 400–700, JetBrains Mono; all SIL OFL). `new_project.py` already copies the patched `engine.js`.
   - Write the project's scenes in `scenes.js`.
   - Init versioning: `python3 $SK/scripts/version.py init <workdir> --slug <name> --project video_v1 --audio work/voice_final.wav`.
8. **Write scenes** in absolute VO time (`T`), using `lib.js`, `parts.js` and `media.js`. See `references/style.md` for the house style and the scene recipes that worked.
9. **Review, required.**
   - Make contact sheets at the 80 % point of every scene, at transition midpoints, and at moments right after each spoken phrase starts: `python3 $MR/scripts/render.py sheet video_vN --times …`. Fix overlaps, clipped text, cut-off cards, alpha leaks, and text over busy photos without a scrim.
   - After rendering, run `python3 $SK/scripts/blank_scan.py video_vN` and fix every empty stretch of 0.5 s or more. Use `bigSay` (the spoken line, big and centered) or b-roll.
10. **Build.** `python3 $SK/scripts/version.py build <workdir> --full`. Then extract stills from the MP4 at frame 0, at the clip/screenshot scenes, and around any fix.
11. **Deliver.** Give the path, duration and size, and a scene summary. List:
   - what you cut from the voice;
   - which on-screen content is illustrative;
   - which images are real third-party screenshots;
   - any assumed app names.

   Also write `output/<slug>.srt` (`make_srt.py work/words.json`), a description file with chapter timestamps, and `output/stock-credits.txt`. Say you can't hear audio and ask them to listen.

## Media sourcing
- **Stock:** `python3 $SK/scripts/stock.py pexels-photo|pexels-video|unsplash <id> <out>`. Find ids with WebSearch (`allowed_domains: ["pexels.com"]`). Always view what you downloaded, because titles lie. Prefer real places matching the story (a hotel *in Japan* for a Japan trip). Resize to ≤1700 px before ingesting. Clips: ingest 8–14 s ranges.
- **Real web pages:** `python3 $SK/scripts/web_capture.py <url> out.png [--mobile]`. `--mobile` matches the phone mockup ratio. Use them for shopping and booking examples, label them on screen ("Real Amazon pages", "The villa's booking page"), and call them out in the delivery note. When the story names a specific place, show its real listing.
- **User recordings:** show them in `phone()` mockups with a `zoomPanel()` magnifier on the line that matters. Label each with the app name chip.

## Gotchas
- **zsh:** `$var` is not word-split (`${=var}` is), and `$5:l` is a modifier, so write `${5}`.
- **Bad frames:** a few frames per render can come back with media not loaded. `render_frames.py` retries them, but check the "still bad" list.
- **Global state:** never set `c.globalAlpha = x` without `save/restore`; it leaks into later scenes through the transition buffers.
- **Overrides:** override scenes in a later script (`S.x = after(S.x, fn)`, `withBg(S.x, fn)`); `bgLight`/`bgDark` call `BG_EXTRA` for footage under content. Reassigning a function declared in another script works (`fuji = function…`).
- **Disk:** keep frames as JPEG (`render_frames.py`). Hard-linked versions share frames, so delete old `out/jframes` folders only when the user agrees.
