# Style guide: what makes these shorts work

The examples below come from real shorts made with this skill (an AI-engineering livestream). Treat them as patterns, and swap in the creator's own topic and voice.

## Hook (frame 0)
- The first frame is the thumbnail and the swipe decision. Draw beat 0 **complete at T=0**. No fade, no rise and no typewriter on the hook. Idle motion (a bob, a pulse, a wobbling emoji) is fine.
- Formula: a small pill label + a BIG claim + a twist line + 1–3 emoji. Examples that worked:
  - `MY AI WORKS / 24/7 / FOR $0*` (the asterisk pays off at the end: "*electric bill not included ⚡")
  - `2 ACCOUNTS. / 1 DAY A WEEK. / 💀`
  - `I STOPPED DOING / FREE CALLS. / 👻 here's why ↓`
  - `FREE GPU / TO TRAIN AI MODELS / $0 stamp`
  - `SKILLS vs MCP / WHO EATS YOUR CONTEXT? / two meters`
- Speech starts at t=0 too. No silent intro.

## Pacing
- Change the stage beat every **1.5–3s**, landing on the spoken word that motivates it. `runBeats` adds the slam-zoom, flash and colour bar on every change.
- Aim for one hero motion per beat, with support 0.1–0.3s later. Stamps and pops land exactly on word times: take them from `src/words.json`, or the cut's energy map when whisper drifts.
- Use face punch-ins (`faceCam` punches) on the 4–7 strongest words.
- Total length is 15–20s of speech + a 1.2–1.5s end card. Use "FOLLOW FOR MORE" for funny shorts and "SAVE THIS + FOLLOW" for educational ones.

## Wit patterns (funny shorts)
- **Asterisk payoff**: the hook promises something ("$0*") and the last beat reveals the catch.
- **Visual stutter**: the speaker repeats "they don't… they don't…" and each repeat flips a card to 👻 while a counter ticks up (NO-SHOWS: 1, 2, 3).
- **Crickets**: a "Waiting for guest…" call UI with 🦗 bouncing.
- **Achievement unlocked**: a game toast for a mundane thing (COMMITMENT 🏆).
- **Stamp on the punchline word**: COOKED 🍳, OOPS, FREE, PRETTY BAD, NOT BROKEN.
- **Chart goes vertical**: the red alarm tint, a count-up bill, a shake on the key word.
- **Deadpan math**: `2 ACCOUNTS × 1 DAY / WEEK = 😭`.
- **Emoji crowd**: "everyone feels this" becomes a grid of 12 suffering faces popping in.
- **Callback**: reuse an earlier UI with the outcome flipped (waiting → "Guest joined ✓").
- Use the real thing when it's on screen: a viewer's post, a limit meter, the website. Real footage reads as proof.

## Explainer patterns (educational shorts)
- **Numbered steps** (`stepBadge`) with one visual per step: a browser bar typing the URL, a sign-in card, the real notebook crop.
- **Recipe card**: rows of KEY → value with the real facts from screen (base model, method, data size, runtime).
- **Real output, then anatomy**: show the actual output screenshot, then rebuild it large with bracket labels (INTRO / THE MEAT / ENDING).
- **Old way vs new way**: strike through the old path, animate the new loop (build → hit issues → learn ↻).
- **Meters**: a context window or VRAM bar filling or overflowing.
- Keep the jargon on screen as chips (LoRA, QLoRA, GGUF, epoch) so viewers learn the terms.

## Layout and type
- Font slots are display / body / mono. The defaults are Anton, Space Grotesk and JetBrains Mono; brand.json can override them. Default palette: neon on near-black, pink `#ff2e88`, cyan `#2ee6ff`, yellow `#ffe14d`, lime `#b8ff3d`, red `#ff3b3b`. brand.json `colors` overrides any key of `C`.
- Non-Latin captions: Anton only covers Latin. For Japanese, Korean, Chinese, Arabic, Cyrillic and so on, set `fonts.display` / `fonts.body` in brand.json to a font that covers the script (e.g. a Noto Sans variant). Also tone down uppercase-only styling for scripts without case.
- Keep text inside ~60px side margins. Hooks usually fit at 150–200px (display font). Shrink before letting text touch the edges.
- Captions: 1–4 words, one line, display font at 94–104px, white with a thick black stroke, `*hot*` words in yellow. If a chunk wraps to two lines, split it. Avoid a lone emoji wrapping onto its own line.
- Stamps never cover the content they comment on. Place them in empty space.
- Screen crops: crop tight to the readable part and upscale 3× with lanczos. Check that stream overlays (facecam box, chat, widgets) are not inside the crop.

## Camera
- Stream facecams are small (often ~200px wide). Upscaling to 1080×960 makes them soft, so warn the user once. A separate camera recording (`"camera"` in short.json) is much sharper.
- The box aspect should be ≈ 1.125 so it fills the bottom half. Aim for the face at about 55–60% from the left, or set `face_focus`.
- With no camera, use `"bottom": "full"` or a screen box. Then put the talking points in the top stage, since there's no face to carry the emotion.
- Camera offset: transcribe both files, find the same distinctive word, and use offset = camera_time − clip_time.

## Audio
- Stream mics are quiet (−22 to −27 LUFS). `scaffold` normalizes the voice to −16 LUFS with light compression.
- The music bed competes more than the SFX do. Use `clip_audio duck: .96`, `music.sfx: .22`, and check with `short.py balance` (target ≤ −11 dB). The final MP4 lands around −13 to −14 LUFS.
