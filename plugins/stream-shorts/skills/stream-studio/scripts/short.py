#!/usr/bin/env python3
"""clips-to-shorts helper — turn livestream / talking-head clips into split-screen 9:16 shorts.

  short.py doctor                                  check ffmpeg, python deps, whisper, chromium, emoji font
  short.py brand --handle @you [...] --out F       write a brand.json (asked once per creator)
  short.py transcribe <clip...> --out DIR          word timings + transcript + speech-energy map
  short.py frame <video> --t 5 --out f.png         full frame with a labelled 100px grid (find camera / screen boxes)
  short.py cut <short.json>                        jump-cut edit + bottom-half video + screen crops + stills, re-transcribed
  short.py scaffold <short.json>                   motion-reel project: brand, fonts, kit.js, media, voice loudnorm, draft captions
  short.py balance <project...>                    how far SFX+music sit under the voice (target ≤ -11 dB)

Exit code 3 + a line starting with NEEDS_INPUT means information is missing: ask the user, then re-run.

short.json (paths relative to the json file):
{
  "slug": "my-short",                              project folder name
  "clip": "../clips/clip.mp4",                     source recording (screen + audio)
  "segs": [[2.85, 4.2], [5.1, 6.55]],              source seconds to keep, in order
  "kind": "funny" | "educational",                 picks the end-card CTA
  "language": "en",                                speech language (ISO code); non-English uses the multilingual model
  // bottom half — exactly one of:
  "face":   [x, y, w, h],                          facecam box inside the source frame (aspect ≈ 1.125)
  "camera": {"file": "cam.mp4", "offset": 0.0,     separate camera recording; camera_time = clip_time + offset
             "box": [x, y, w, h], "audio": "clip"},   optional crop · which file's audio to use ("clip" | "camera")
  "bottom": "full" | [x, y, w, h],                 no camera: show this part of the source in the bottom half
  "face_focus": [0.55, 0.42],                      optional crop anchor for the bottom video
  "screens": {"name": [x, y, w, h]},               optional moving crops (follow the cut) → clip ids
  "stills":  {"name": [t, x, y, w, h]},            optional still crops from the source at t → image ids
  "brand": "brand.json" | {...},                   optional; otherwise brand.json is searched upward from short.json
  "end_card": 1.5, "bpm": 124
}
brand.json: {"handle": "@you", "tagline": "...", "ring": "WORD • WORD • WORD", "live": true,
             "cta": "FOLLOW FOR MORE", "ctaEdu": "SAVE THIS + FOLLOW",
             "colors": {"pink": "#ff2e88", "cyan": "#2ee6ff", "yel": "#ffe14d", ...},
             "fonts": {"display": "path.ttf", "body": "path.ttf", "mono": "path.ttf"}}
"""
import argparse, json, os, platform, re, shutil, subprocess, sys
from typing import NoReturn

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
ENGINE = os.path.join(SKILL, "engine")
ASSETS = os.path.join(SKILL, "assets")
DEFAULT_FONTS = {"display": "Anton-Regular.ttf", "body": "SpaceGrotesk.ttf", "mono": "JetBrainsMono.ttf"}
USER_BRAND = os.path.expanduser("~/.config/clips-to-shorts/brand.json")


def run(*cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def needs_input(what, questions) -> NoReturn:
    """stop and tell the agent exactly what to ask the user"""
    print(f"NEEDS_INPUT: {what}")
    for q in questions:
        print(f"  - {q}")
    sys.exit(3)


# ---------------------------------------------------------------- config
def load_cfg(path):
    if not os.path.exists(path):
        needs_input("short.json not found", [f"create {path} (see short.py --help)"])
    cfg = json.load(open(path))
    base = os.path.dirname(os.path.abspath(path))
    missing = [k for k in ("slug", "clip", "segs") if not cfg.get(k)]
    if missing:
        needs_input(f"short.json is missing {', '.join(missing)}",
                    ["which clip/recording should this short come from?" if "clip" in missing else "",
                     "which moment (transcribe first and propose segs)?" if "segs" in missing else ""])
    rel = lambda p: os.path.normpath(os.path.join(base, os.path.expanduser(p)))
    cfg["_base"] = base
    cfg["clip"] = rel(cfg["clip"])
    if not os.path.exists(cfg["clip"]):
        needs_input("source clip not found", [f"where is the recording? ({cfg['clip']} does not exist)"])
    if isinstance(cfg.get("camera"), dict) and cfg["camera"].get("file"):
        cfg["camera"]["file"] = rel(cfg["camera"]["file"])
    cfg["_project"] = rel(cfg.get("project", cfg["slug"]))
    cfg["_src"] = os.path.join(cfg["_project"], "src")
    return cfg


def find_brand(cfg):
    b = cfg.get("brand")
    if isinstance(b, dict):
        return b, cfg["_base"]
    cands = [os.path.join(cfg["_base"], b)] if isinstance(b, str) else []
    d = cfg["_base"]
    for _ in range(4):
        cands.append(os.path.join(d, "brand.json")); d = os.path.dirname(d)
    cands.append(USER_BRAND)
    for p in cands:
        if os.path.exists(p):
            return json.load(open(p)), os.path.dirname(p)
    needs_input("brand (no brand.json found)", [
        "What handle should appear on the video and end card? (e.g. @yourname)",
        "One-line tagline for the end card? (e.g. 'I build AI agents live on YouTube') — optional",
        "Short ring text around the avatar? (e.g. 'AI • AGENTS • LIVE') — optional",
        "Do you stream live (show a LIVE badge)? yes/no",
        "Brand colours or fonts? (default: neon pink/cyan/yellow on black, Anton + Space Grotesk)",
        f"then: short.py brand --handle @x [--tagline ..] [--ring ..] [--live] --out {os.path.join(cfg['_base'], 'brand.json')}",
    ])


# ---------------------------------------------------------------- audio / speech
def read_mono16k(path):
    from scipy.io import wavfile
    tmp = path + ".16k.wav"
    run("ffmpeg", "-v", "error", "-y", "-i", path, "-vn", "-ac", "1", "-ar", "16000", tmp)
    sr, a = wavfile.read(tmp); os.remove(tmp)
    return sr, a.astype(float) / 32768


def energy(a, sr, hop=0.02):
    import numpy as np
    n = int(sr * hop)
    return np.array([np.sqrt(np.mean(a[i:i + n] ** 2)) for i in range(0, max(1, len(a) - n), n)]), hop


def energy_map(path):
    """one char per 50ms, one row per 5s: '#' loud speech, '+' speech, '.' silence"""
    import numpy as np
    sr, a = read_mono16k(path)
    env, _ = energy(a, sr, 0.05)
    db = 20 * np.log10(env + 1e-6); thr = np.percentile(db, 90) - 22
    s = ''.join('#' if d > thr + 10 else '+' if d > thr else '.' for d in db)
    return "\n".join(f"{i * 0.05:6.1f} {s[i:i + 100]}" for i in range(0, len(s), 100))


_MODELS = {}
def whisper(lang):
    name = os.environ.get("SHORTS_WHISPER") or ("small.en" if lang == "en" else "small")
    if name not in _MODELS:
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            sys.exit("faster-whisper missing: pip install faster-whisper")
        _MODELS[name] = WhisperModel(name, device="cpu", compute_type="int8")
    return _MODELS[name]


def transcribe(path, lang="en", prompt=None):
    segs, _ = whisper(lang).transcribe(path, word_timestamps=True, initial_prompt=prompt, language=lang or None)
    words, lines = [], []
    for s in segs:
        lines.append(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text.strip()}")
        words += [(w.word.strip(), round(w.start, 3), round(w.end, 3)) for w in (s.words or [])]
    return words, lines


# ---------------------------------------------------------------- video helpers
def concat_cut(src, segs, out, vf=None, audio=True, crf=12):
    fc, parts = "", ""
    for i, (s, e) in enumerate(segs):
        d = e - s
        fc += f"[0:v]trim={s:.3f}:{e:.3f},setpts=PTS-STARTPTS,fps=30[v{i}];"
        if audio:
            fc += f"[0:a]atrim={s:.3f}:{e:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={max(0, d - 0.03):.3f}:d=0.03[a{i}];"
        parts += f"[v{i}]" + (f"[a{i}]" if audio else "")
    fc += parts + f"concat=n={len(segs)}:v=1:a={1 if audio else 0}" + ("[v][a]" if audio else "[v]")
    if vf:
        fc += f";[v]{vf}[vo]"
    vmap = "[vo]" if vf else "[v]"
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", fc, "-map", vmap]
    if audio:
        cmd += ["-map", "[a]", "-c:a", "aac", "-b:a", "256k"]
    run(*cmd, "-c:v", "libx264", "-crf", str(crf), "-preset", "fast", out)


def bottom_filter(box, small):
    """crop (optional) → cover 1080x960; small sources (stream facecams) get denoise + sharpening"""
    f = f"crop={box[2]}:{box[3]}:{box[0]}:{box[1]}," if box else ""
    if small:
        return f + "hqdn3d=1.5:1.5:3:3,scale=1080:960:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:960,unsharp=7:7:0.9:5:5:0,eq=contrast=1.05:saturation=1.08"
    return f + "scale=1080:960:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:960"


def video_size(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", path],
                         capture_output=True, text=True, check=True).stdout.strip()
    w, h = out.split(",")[:2]
    return int(w), int(h)


# ---------------------------------------------------------------- commands
def cmd_doctor(a):
    ok = True
    def check(name, good, fix=""):
        nonlocal ok
        print(("✓ " if good else "✗ ") + name + ("" if good else f"   → {fix}")); ok &= bool(good)
    ff = shutil.which("ffmpeg")
    check("ffmpeg", ff, "install ffmpeg (brew install ffmpeg / apt install ffmpeg)")
    if ff:
        enc = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True).stdout
        check("ffmpeg libx264", "libx264" in enc, "use an ffmpeg build with libx264")
    for mod, pip in [("numpy", "numpy"), ("scipy", "scipy"), ("PIL", "pillow"), ("playwright", "playwright"), ("faster_whisper", "faster-whisper")]:
        try:
            __import__(mod); check(f"python: {pip}", True)
        except ImportError:
            check(f"python: {pip}", False, f"pip install {pip}")
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch(); b.close()
        check("chromium (playwright)", True)
    except Exception:
        check("chromium (playwright)", False, "python3 -m playwright install chromium")
    sysname = platform.system()
    if sysname == "Darwin":
        check("emoji font", os.path.exists("/System/Library/Fonts/Apple Color Emoji.ttc"), "Apple Color Emoji missing")
    else:
        fl = subprocess.run(["fc-list"], capture_output=True, text=True).stdout if shutil.which("fc-list") else ""
        check("emoji font", "emoji" in fl.lower(), "install Noto Color Emoji (apt install fonts-noto-color-emoji) or emoji render as boxes")
    print("ready" if ok else "fix the ✗ items, then re-run doctor")


def cmd_brand(a):
    b = {"handle": a.handle if a.handle.startswith("@") or not a.handle else "@" + a.handle}
    if a.tagline: b["tagline"] = a.tagline
    if a.ring: b["ring"] = a.ring
    b["live"] = bool(a.live)
    if a.cta: b["cta"] = a.cta
    if a.cta_edu: b["ctaEdu"] = a.cta_edu
    cols = {k: v for k, v in (("pink", a.accent1), ("cyan", a.accent2), ("yel", a.highlight), ("bg", a.bg)) if v}
    if cols: b["colors"] = cols
    fonts = {k: os.path.abspath(v) for k, v in (("display", a.display_font), ("body", a.body_font), ("mono", a.mono_font)) if v}
    if fonts: b["fonts"] = fonts
    out = os.path.expanduser(a.out)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    json.dump(b, open(out, "w"), indent=2, ensure_ascii=False)
    print(f"wrote {out}\n{json.dumps(b, indent=2, ensure_ascii=False)}")


def cmd_transcribe(a):
    os.makedirs(a.out, exist_ok=True)
    for f in a.clips:
        words, lines = transcribe(f, a.language, a.prompt)
        b = os.path.splitext(os.path.basename(f))[0]
        json.dump(words, open(os.path.join(a.out, b + ".words.json"), "w"), ensure_ascii=False)
        open(os.path.join(a.out, b + ".txt"), "w").write("\n".join(lines))
        print(f"== {b}\n" + "\n".join(lines))
        print("-- words: " + " ".join(f"{w}[{s:.2f}]" for w, s, _ in words))
        print("-- energy (50ms/char, 5s/row):\n" + energy_map(f) + "\n")


def cmd_frame(a):
    from PIL import Image, ImageDraw
    tmp = a.out + ".raw.png"
    run("ffmpeg", "-v", "error", "-y", "-ss", str(a.t), "-i", a.clip, "-frames:v", "1", tmp)
    im = Image.open(tmp).convert("RGB"); d = ImageDraw.Draw(im); w, h = im.size
    step = 100 if w <= 2000 else 200
    for x in range(0, w, step):
        d.line([(x, 0), (x, h)], fill=(255, 0, 255), width=1); d.text((x + 3, 3), str(x), fill=(255, 255, 0))
    for y in range(0, h, step):
        d.line([(0, y), (w, y)], fill=(0, 255, 255), width=1); d.text((3, y + 3), str(y), fill=(255, 255, 0))
    im.save(a.out); os.remove(tmp)
    print(f"{a.out}  ({w}x{h}) — read it, then zoom: ffmpeg -ss T -i video -frames:v 1 -vf crop=W:H:X:Y,scale=iw*3:-1 zoom.png")


def cmd_cut(a):
    import numpy as np
    cfg = load_cfg(a.config); src, out = cfg["clip"], cfg["_src"]
    modes = [k for k in ("face", "camera", "bottom") if cfg.get(k)]
    if len(modes) != 1:
        needs_input("camera setup (set exactly one of face / camera / bottom in short.json)", [
            "Is your camera visible inside the recording (a facecam box)? → run `short.py frame` and set \"face\": [x,y,w,h]",
            "Or do you have a separate camera recording? → \"camera\": {\"file\": ..., \"offset\": seconds}",
            "Or no camera at all? → \"bottom\": \"full\" (or a screen box) fills the bottom half"])
    os.makedirs(out, exist_ok=True)
    sr, au = read_mono16k(src); env, hop = energy(au, sr)

    def snap(t):   # move a cut point to the quietest 20ms within ±0.12s
        i, r = int(t / hop), int(0.12 / hop)
        lo, hi = max(0, i - r), min(len(env) - 1, i + r)
        return (lo + int(np.argmin(env[lo:hi + 1]))) * hop

    segs = [(snap(s), snap(e)) for s, e in cfg["segs"]]
    cut = os.path.join(out, "cut.mp4")
    concat_cut(src, segs, cut)
    face = os.path.join(out, "face.mp4")
    if cfg.get("face"):
        box = cfg["face"]
        run("ffmpeg", "-v", "error", "-y", "-i", cut, "-vf", bottom_filter(box, box[2] < 540),
            "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-c:a", "copy", face)
    elif cfg.get("camera"):
        cam = cfg["camera"]
        if not cam.get("file") or not os.path.exists(cam["file"]):
            needs_input("camera file not found", ["where is the separate camera recording?"])
        if "offset" not in cam:
            needs_input("camera offset unknown", [
                "How many seconds is the camera recording ahead of (+) or behind (-) the screen recording? "
                "(if unsure: transcribe both and match the same spoken word; offset = camera_time - clip_time)"])
        off = float(cam["offset"]); box = cam.get("box")
        small = (box[2] if box else video_size(cam["file"])[0]) < 540
        camcut = os.path.join(out, "camcut.mp4")
        use_cam_audio = cam.get("audio", "clip") == "camera"
        concat_cut(cam["file"], [(s + off, e + off) for s, e in segs], camcut, vf=bottom_filter(box, small), audio=use_cam_audio, crf=14)
        if use_cam_audio:
            shutil.move(camcut, face)
        else:
            run("ffmpeg", "-v", "error", "-y", "-i", camcut, "-i", cut, "-map", "0:v", "-map", "1:a", "-c", "copy", "-shortest", face)
            os.remove(camcut)
    else:
        b = cfg["bottom"]; box = None if b == "full" else b
        run("ffmpeg", "-v", "error", "-y", "-i", cut, "-vf", bottom_filter(box, False),
            "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-c:a", "copy", face)
    for name, (x, y, w, h) in cfg.get("screens", {}).items():
        run("ffmpeg", "-v", "error", "-y", "-i", cut, "-an", "-vf", f"crop={w}:{h}:{x}:{y},scale=iw*3:ih*3:flags=lanczos,unsharp=5:5:0.6",
            "-c:v", "libx264", "-crf", "14", os.path.join(out, f"scr_{name}.mp4"))
    for name, (t, x, y, w, h) in cfg.get("stills", {}).items():
        run("ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", src, "-frames:v", "1", "-vf",
            f"crop={w}:{h}:{x}:{y},scale=iw*3:ih*3:flags=lanczos,unsharp=5:5:0.8", os.path.join(out, f"img_{name}.png"))
    total = sum(e - s for s, e in segs)
    words, _ = transcribe(face, cfg.get("language", "en"), cfg.get("prompt"))
    json.dump(words, open(os.path.join(out, "words.json"), "w"), ensure_ascii=False)
    json.dump({"segs": segs, "total": total}, open(os.path.join(out, "segs.json"), "w"))
    print(f"{cfg['slug']}: {total:.2f}s of speech in {len(segs)} segments ({modes[0]} layout)")
    if total > 21: print("  ⚠ longer than ~20s — trim segs for a snappier short")
    print("cut reads: " + " ".join(f"{w}[{s:.2f}]" for w, s, _ in words))
    print("energy of the cut:\n" + energy_map(face))


def draft_caps(words, total, max_words=3):
    chunks, cur = [], []
    for w, s, _ in words:
        cur.append((w, s))
        if re.search(r"[.,?!。、？！]$", w) or len(cur) >= max_words:
            chunks.append(cur); cur = []
    if cur: chunks.append(cur)
    caps = []
    for i, ch in enumerate(chunks):
        a = 0.0 if i == 0 else ch[0][1]
        b = chunks[i + 1][0][1] if i + 1 < len(chunks) else total
        caps.append([round(a, 2), round(b, 2), " ".join(re.sub(r"[.,!。、！]$", "", w).upper() for w, _ in ch)])
    return caps


def cmd_scaffold(a):
    cfg = load_cfg(a.config); proj, src = cfg["_project"], cfg["_src"]
    if not os.path.exists(os.path.join(src, "segs.json")):
        needs_input("not cut yet", [f"run: short.py cut {a.config}"])
    brand, brand_dir = find_brand(cfg)
    if not brand.get("handle"):
        needs_input("brand.handle is empty", ["What handle should appear on the video? (e.g. @yourname)"])
    meta = json.load(open(os.path.join(src, "segs.json"))); speech = round(meta["total"] - 0.02, 2)
    dur = round(speech + cfg.get("end_card", 1.5), 2)
    if not os.path.exists(os.path.join(proj, "engine.js")):
        run(sys.executable, os.path.join(ENGINE, "scripts", "new_project.py"), proj, "--preset", "portrait", "--fps", "30",
            "--duration", str(dur), "--bpm", str(cfg.get("bpm", 124)), "--title", cfg["slug"], "--force")
    fdir = os.path.join(proj, "fonts"); os.makedirs(fdir, exist_ok=True)
    for slot, default in DEFAULT_FONTS.items():
        custom = (brand.get("fonts") or {}).get(slot)
        path = os.path.normpath(os.path.join(brand_dir, os.path.expanduser(custom))) if custom else os.path.join(ASSETS, "fonts", default)
        if not os.path.exists(path):
            needs_input(f"font file for '{slot}' not found", [f"where is the {slot} font file? ({path} missing)"])
        shutil.copy(path, os.path.join(fdir, f"{slot}.ttf"))
    shutil.copy(os.path.join(ASSETS, "kit.js"), os.path.join(proj, "kit.js"))
    items = [f"face={os.path.join(src, 'face.mp4')}@0-{speech}"]
    for f in sorted(os.listdir(src)):
        if f.startswith("scr_"): items.append(f"{f[4:-4]}={os.path.join(src, f)}@0-{speech}")
        if f.startswith("img_"): items.append(f"{f[4:-4]}={os.path.join(src, f)}")
    run(sys.executable, os.path.join(ENGINE, "scripts", "ingest.py"), "add", proj, *items, "--long")
    # voice first: stream mics are quiet — normalise before scoring
    wav = os.path.join(proj, "media", "face.wav"); raw = os.path.join(proj, "media", "face.raw.wav")
    if not os.path.exists(wav):
        needs_input("no audio in the edit", ["the source has no audio track — which file has the voice?"])
    shutil.copy(wav, raw)
    run("ffmpeg", "-v", "error", "-y", "-i", raw, "-af",
        "highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,loudnorm=I=-16:TP=-1.5:LRA=7", "-ar", "48000", wav)
    page_brand = {k: v for k, v in brand.items() if k != "fonts"}
    if cfg.get("face_focus"): page_brand["faceFocus"] = cfg["face_focus"]
    page = os.path.join(proj, "index.html")
    cur = open(page).read() if os.path.exists(page) else ""
    if a.force or not cur or "SHORTS-TEMPLATE" in cur or "YOUR BRAND" in cur:
        caps = draft_caps(json.load(open(os.path.join(src, "words.json"))), speech)
        html = open(os.path.join(ASSETS, "template.html")).read()
        html = (html.replace("__TITLE__", cfg.get("title", cfg["slug"].replace("-", " ").title()))
                .replace("__BRAND__", json.dumps(page_brand, ensure_ascii=False))
                .replace("__EDU__", "true" if cfg.get("kind") == "educational" else "false")
                .replace("__SPEECH__", str(speech)).replace("__DUR__", str(dur)).replace("__BPM__", str(cfg.get("bpm", 124)))
                .replace("__CAPS__", ",\n  ".join(json.dumps(c, ensure_ascii=False) for c in caps)))
        open(page, "w").write(html)
    else:
        print("  (kept existing index.html — pass --force to regenerate from the template)")
    print(f"project ready: {proj}\n  speech {speech}s · duration {dur}s · brand {brand.get('handle')} · media: {', '.join(i.split('=')[0] for i in items)}")
    print("  next: edit index.html (hook, BEATS, CAPS *hot* words, cues) → render.py sheet → build.py")


def cmd_balance(a):
    import numpy as np
    from scipy.io import wavfile
    from scipy.signal import resample_poly
    for proj in a.projects:
        sr, s = wavfile.read(os.path.join(proj, "out", "score.wav")); s = s.astype(float); s = s.mean(1) if s.ndim > 1 else s
        vr, v = wavfile.read(os.path.join(proj, "media", "face.wav")); v = v.astype(float); v = v.mean(1) if v.ndim > 1 else v
        if vr != sr: v = resample_poly(v, sr, vr)
        n = min(len(v), len(s)); g = np.dot(s[:n], v[:n]) / np.dot(v[:n], v[:n]); r = s[:n] - g * v[:n]
        db = 20 * np.log10(np.sqrt(np.mean(r ** 2)) / np.sqrt(np.mean((g * v[:n]) ** 2)))
        print(f"{proj}: SFX+music sit {db:.1f} dB vs voice  ({'OK' if db <= -11 else 'TOO LOUD — lower music.sfx / raise duck'})")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("doctor")
    p = sub.add_parser("brand"); p.add_argument("--handle", required=True); p.add_argument("--tagline"); p.add_argument("--ring")
    p.add_argument("--live", action="store_true"); p.add_argument("--cta"); p.add_argument("--cta-edu")
    p.add_argument("--accent1", help="primary accent hex (default #ff2e88)"); p.add_argument("--accent2", help="secondary accent hex (default #2ee6ff)")
    p.add_argument("--highlight", help="caption highlight hex (default #ffe14d)"); p.add_argument("--bg")
    p.add_argument("--display-font"); p.add_argument("--body-font"); p.add_argument("--mono-font")
    p.add_argument("--out", default=USER_BRAND, help=f"default {USER_BRAND} (used for every short)")
    p = sub.add_parser("transcribe"); p.add_argument("clips", nargs="+"); p.add_argument("--out", default="words")
    p.add_argument("--prompt"); p.add_argument("--language", default="en")
    p = sub.add_parser("frame"); p.add_argument("clip"); p.add_argument("--t", type=float, default=5); p.add_argument("--out", default="frame.png")
    p = sub.add_parser("cut"); p.add_argument("config")
    p = sub.add_parser("scaffold"); p.add_argument("config"); p.add_argument("--force", action="store_true", help="rewrite index.html from the template")
    p = sub.add_parser("balance"); p.add_argument("projects", nargs="+")
    a = ap.parse_args()
    {"doctor": cmd_doctor, "brand": cmd_brand, "transcribe": cmd_transcribe, "frame": cmd_frame, "cut": cmd_cut,
     "scaffold": cmd_scaffold, "balance": cmd_balance}[a.cmd](a)


if __name__ == "__main__":
    main()
