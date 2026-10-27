---
description: Make 9:16 YouTube Shorts from a topic or clip (versioned, reproducible)
argument-hint: <topic | clip file | "3 funny shorts">
---

Use the `stream-studio` skill to make shorts: $ARGUMENTS

Follow `references/folders.md` and `references/make-shorts.md` from the skill. If the stream hasn't been processed yet (no `stream.json`, clips or transcripts), run the `/process-stream` workflow first. Pick the moments from the transcript, create a version folder with `stream.py short-new`, author the short, build with `stream.py short-build`, check frames, and deliver the mp4 path, duration, a one-line summary and YouTube title/description (`YOUTUBE.md` inside the version folder). Ask one round of questions: always the **style** (`grok`, `claude` or the default neon, recommending the one that fits the topic), unless the request already names one or you're making a new version of an existing short; plus anything else that can't be worked out (brand, camera setup, tone).
