---
description: Process a livestream video into clips, transcript, subtitles and chapters (standard folder layout)
argument-hint: <video-file.mp4>
---

Use the `stream-studio` skill to process this stream: $ARGUMENTS

Follow `references/folders.md` and `references/process-stream.md` from the skill: set up the folder layout (`stream.py init`, or `migrate` if the folder is already populated), transcribe in the background, find the chapters/features from the transcript, then cut one clip per feature with per-clip transcripts, subtitles and chapter files (`stream.py clips`). Finish with the paste-ready chapter block and any caveats. If no file was given, look for a video in the current folder and confirm it.
