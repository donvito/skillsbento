# Folder layout and file naming

One **root video folder** per stream (the folder the user opens Claude Code in). `stream.json` in the root records the stream's `slug` and source file; every helper reads it.

```
<root>/
  stream.json                         { "slug": "...", "source": "source/<file>" }
  source/                             the raw livestream / VOD (never edited, never re-encoded)
  clips/                              feature clips cut from the source
  shorts/                             9:16 shorts, one VERSION FOLDER per short version
  longform/                           summary reels, recaps, highlight videos, one VERSION FOLDER each
  transcripts/                        full-stream and per-clip transcripts
  subtitles/                          .srt files (full stream and per clip)
  chapters/                           chapter plan (json), chapter list (md / paste-ready txt)
  thumbnails/                         thumbnails and frame-0 stills
  .work/                              scratch (audio.wav, progress, caches). Safe to delete
```

## Naming: everything starts with the stream slug

`<slug>` = kebab-case stream name (from the source filename, or `--slug`). Files that belong together share the same stem, so one glance links a clip to its transcript, subtitles and thumbnail.

| what | path |
|---|---|
| source | `source/<original filename>` |
| full transcript | `transcripts/<slug>.transcript.txt` (timestamped) and `.transcript.json` (segments) |
| full subtitles | `subtitles/<slug>.srt` |
| chapter plan (source of truth) | `chapters/<slug>.chapters.json` |
| chapter list | `chapters/<slug>.chapters.md` (table + paste block) and `chapters/<slug>.chapters.txt` (paste-ready `0:00 Title`) |
| clip | `clips/<slug>--NN-<feature>.mp4` (NN = 01, 02…) |
| clip transcript / subtitles | `transcripts/<slug>--NN-<feature>.txt`, `subtitles/<slug>--NN-<feature>.srt` |
| short version folder | `shorts/<slug>--short-<topic>--v1/` |
| longform version folder | `longform/<slug>--<name>--v1/` (e.g. `--summary--v1`) |
| thumbnail | `thumbnails/<same stem as the video>.png` |

Rules:
- Two dashes `--` separate the parts (stream, then part), single dashes are inside a part. Lowercase, ASCII, no spaces.
- A chapter file for a *video* shares that video's stem: the summary reel `longform/<slug>--summary--v1/` has `<slug>--summary--v1.chapters.md` inside it.
- Never overwrite a finished version. New version = new `--vN` folder.

## Version folders (reproducible)

A version folder holds **the video and everything needed to regenerate it**:

```
shorts/<slug>--short-dots--v2/
  short.json  page.html  [kit.js]       inputs
  <folder-name>.mp4  <folder-name>.png  outputs (video + frame-0 thumbnail)
  YOUTUBE.md  manifest.json             copy + what built it (tool versions, input hashes, date)
  project/                              generated; delete and rebuild any time
```

```
longform/<slug>--summary--v1/
  reel.json                             items (title, source start, duration), intro/outro text
  <folder-name>.mp4  <folder-name>.chapters.md  <folder-name>.png
  manifest.json
```

Inputs reference sources by **relative path** (`../../clips/...`), so the whole root folder can be moved or synced. Rebuild with `stream.py short-build <dir>` or `stream.py reel <root> --name summary --version N`.

## Legacy folders

A folder that predates this layout: run `stream.py migrate <root>` (dry run by default, `--apply` to move). It moves the source into `source/`, renames clips/transcripts to the `<slug>--NN-` scheme and moves chapter files. Shorts and longform outputs are listed for the user to confirm, not moved automatically.
