#!/usr/bin/env python3
"""stream.py: folder layout, transcripts, clips, chapters, versioned shorts and reels for a livestream folder.

  stream.py doctor
  stream.py init <root> --source VIDEO [--slug S]       create folders, move the video to source/, write stream.json
  stream.py transcribe <root> [--model M] [--language L]  transcripts/<slug>.transcript.{json,txt} + subtitles/<slug>.srt
  stream.py clips <root> [--only 2,3] [--force]         chapters/<slug>.chapters.json -> clips, clip transcripts/srt, chapter files
  stream.py reel <root> --name summary [--version N] [--new]   longform/<slug>--<name>--vN/ from reel.json
  stream.py short-new <root> --topic T --clip FILE [--from-prev]   next shorts/<slug>--short-<T>--vN/ folder
  stream.py short-build <dir> [--scaffold-only|--save-page]  regenerate / build a short version folder
  stream.py migrate <root> [--apply]                    move a legacy folder into the standard layout

See references/folders.md for the layout and naming rules.
"""
import argparse, datetime, hashlib, json, os, re, shutil, subprocess, sys, textwrap
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
SHORT_PY = SKILL / "scripts" / "short.py"
BUILD_PY = SKILL / "engine" / "scripts" / "build.py"
DIRS = ["source", "clips", "shorts", "longform", "transcripts", "subtitles", "chapters", "thumbnails"]


# ---------- helpers ----------
def slugify(s):
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s.strip()).strip("-").lower()
    return s or "stream"


def guess_slug(stem):
    """kebab-case slug from a filename; drops a trailing random id token (e.g. '-1AxRnZyWMORxl')."""
    parts = slugify(stem).split("-")
    if len(parts) > 2 and len(parts[-1]) >= 10 and re.search(r"\d", parts[-1]) and re.search(r"[a-z]", parts[-1]):
        parts = parts[:-1]
    return "-".join(parts)


def hms(t, pad=True):
    t = int(t)
    h, m, s = t // 3600, t % 3600 // 60, t % 60
    return f"{h:02d}:{m:02d}:{s:02d}" if pad else (f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}")


def srt_ts(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def probe_duration(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(p)],
                         capture_output=True, text=True)
    try:
        return float(out.stdout.strip())
    except ValueError:
        return 0.0


def sha(p):
    p = Path(p)
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16] if p.exists() else None


def load_stream(root):
    root = Path(root).resolve()
    f = root / "stream.json"
    if not f.exists():
        sys.exit(f"{f} not found. Run: stream.py init {root} --source <video>")
    d = json.loads(f.read_text())
    return root, d["slug"], root / d["source"]


def write_srt(segs, path, shift=0.0, lo=None, hi=None):
    out, n = [], 0
    for s in segs:
        if lo is not None and (s["end"] <= lo or s["start"] >= hi):
            continue
        a, b = max(s["start"], lo or 0) - shift, min(s["end"], hi if hi is not None else 1e12) - shift
        n += 1
        out.append(f"{n}\n{srt_ts(a)} --> {srt_ts(b)}\n" + "\n".join(textwrap.wrap(s["text"], 42)) + "\n")
    Path(path).write_text("\n".join(out))


def font_path():
    for p in ["/System/Library/Fonts/Helvetica.ttc", "/Library/Fonts/Arial.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"]:
        if os.path.exists(p):
            return p
    sys.exit("No font found for drawtext. Install DejaVu or edit font_path() in stream.py")


def drawtext(parts, key, text, opts):
    """drawtext filter that reads its text from a file with % expansion off, so no escaping is needed."""
    f = parts / f"{key}.txt"
    f.write_text(text)
    return f"drawtext=fontfile={font_path()}:textfile={f}:expansion=none:{opts}"


# ---------- commands ----------
def cmd_doctor(a):
    ok = True
    for tool in ["ffmpeg", "ffprobe"]:
        found = shutil.which(tool)
        print(("✓ " if found else "✗ ") + tool + ("" if found else "  (install ffmpeg)"))
        ok &= bool(found)
    try:
        import faster_whisper  # noqa: F401
        print("✓ python: faster-whisper")
    except ImportError:
        print("✗ python: faster-whisper  (pip install faster-whisper)")
        ok = False
    print("\nshort.py doctor (shorts rendering):")
    subprocess.run([sys.executable, str(SHORT_PY), "doctor"])
    print("ready" if ok else "fix the ✗ items above")


def cmd_init(a):
    root = Path(a.root).resolve()
    for d in DIRS:
        (root / d).mkdir(parents=True, exist_ok=True)
    (root / ".work").mkdir(exist_ok=True)
    src = Path(a.source).resolve() if a.source else None
    existing = root / "stream.json"
    if src is None:
        if existing.exists():
            print("folders ready;", existing.read_text().strip())
            return
        sys.exit("--source VIDEO is required the first time")
    if not src.exists():
        sys.exit(f"{src} not found")
    dest = root / "source" / src.name
    if src != dest:
        shutil.move(str(src), str(dest))
        print(f"moved {src.name} -> source/")
    slug = a.slug or guess_slug(src.stem)
    existing.write_text(json.dumps({"slug": slug, "source": f"source/{src.name}"}, indent=2) + "\n")
    print(f"root: {root}\nslug: {slug}\nsource: source/{src.name}  ({hms(probe_duration(dest))})")


def cmd_transcribe(a):
    root, slug, src = load_stream(a.root)
    work = root / ".work"
    work.mkdir(exist_ok=True)
    wav = work / "audio.wav"
    if not wav.exists():
        print("extracting audio…", flush=True)
        run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-vn", "-ac", "1", "-ar", "16000", str(wav)])
    from faster_whisper import WhisperModel
    model = WhisperModel(a.model, device="cpu", compute_type="int8")
    kw: dict = {"language": a.language} if a.language else ({"language": "en"} if a.model.endswith(".en") else {})
    segments, info = model.transcribe(str(wav), vad_filter=True, beam_size=1, **kw)
    out = []
    with open(work / "progress.txt", "w") as prog:
        for s in segments:
            out.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()})
            prog.write(f"{s.end:.0f}/{info.duration:.0f}\n")
            prog.flush()
    tdir = root / "transcripts"
    (tdir / f"{slug}.transcript.json").write_text(json.dumps({"model": a.model, "duration": info.duration, "segments": out}, indent=1))
    (tdir / f"{slug}.transcript.txt").write_text("\n".join(f"[{hms(s['start'])}] {s['text']}" for s in out) + "\n")
    write_srt(out, root / "subtitles" / f"{slug}.srt")
    print(f"done: {len(out)} segments -> transcripts/{slug}.transcript.{{json,txt}}, subtitles/{slug}.srt")


def load_plan(root, slug, src):
    f = root / "chapters" / f"{slug}.chapters.json"
    if not f.exists():
        sys.exit(f"{f} not found (write the chapter plan first, see references/process-stream.md)")
    ch = json.loads(f.read_text())["chapters"]
    dur = probe_duration(src)
    for i, c in enumerate(ch):
        nxt = ch[i + 1]["start"] if i + 1 < len(ch) else dur
        c["end"] = c.get("end", nxt)
        c.setdefault("clip", True)
    if ch[0]["start"] != 0:
        print("warning: first chapter does not start at 0 (YouTube needs 0:00)")
    n = 0
    for c in ch:
        if c["clip"]:
            n += 1
            c["n"] = n
            c["name"] = f"{slug}--{n:02d}-{slugify(c.get('slug') or c['title'])}"
    return ch, dur


def cmd_clips(a):
    root, slug, src = load_stream(a.root)
    ch, dur = load_plan(root, slug, src)
    tj = root / "transcripts" / f"{slug}.transcript.json"
    segs = json.loads(tj.read_text())["segments"] if tj.exists() else []
    if not segs:
        print("note: no transcript found; clips will have no transcript/subtitles")
    only = {int(x) for x in a.only.split(",")} if a.only else None

    def cut(c):
        if only and c["n"] not in only:
            return None
        mp4 = root / "clips" / f"{c['name']}.mp4"
        if mp4.exists() and not a.force:
            return f"skip  {mp4.name}"
        run(["ffmpeg", "-y", "-v", "error", "-ss", str(c["start"]), "-to", str(c["end"]), "-i", str(src),
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "160k",
             "-movflags", "+faststart", str(mp4)])
        if segs:
            body = [f"[{hms(s['start'])}] {s['text']}" for s in segs if s["end"] > c["start"] and s["start"] < c["end"]]
            (root / "transcripts" / f"{c['name']}.txt").write_text(
                f"{c['title']}\nSource: {src.name}\nSource time: {hms(c['start'])} - {hms(c['end'])}\n\n" + "\n".join(body) + "\n")
            write_srt(segs, root / "subtitles" / f"{c['name']}.srt", shift=c["start"], lo=c["start"], hi=c["end"])
        return f"clip  {mp4.name}"

    with ThreadPoolExecutor(3) as ex:
        for r in ex.map(cut, [c for c in ch if c["clip"]]):
            if r:
                print(r, flush=True)
    write_chapter_files(root, slug, src, ch, dur)


def write_chapter_files(root, slug, src, ch, dur):
    paste = [f"{hms(c['start'], pad=False)} {c['title']}" for c in ch]
    (root / "chapters" / f"{slug}.chapters.txt").write_text("\n".join(paste) + "\n")
    rows = ["| Start | Chapter | Clip |", "|---|---|---|"]
    for c in ch:
        rows.append(f"| {hms(c['start'], pad=False)} | {c['title']} | " + (f"`clips/{c['name']}.mp4`" if c["clip"] else "none") + " |")
    md = (f"# {slug}: chapters\n\n**Video:** `{src.relative_to(root)}` (duration {hms(dur, pad=False)})\n\n"
          + "\n".join(rows) + "\n\n## Paste block\n\n```\n" + "\n".join(paste) + "\n```\n")
    (root / "chapters" / f"{slug}.chapters.md").write_text(md)
    print(f"wrote chapters/{slug}.chapters.md and .txt")


def version_dir(base, name, version, new):
    existing = sorted(int(m.group(1)) for p in base.glob(f"{name}--v*") if (m := re.search(r"--v(\d+)$", p.name)))
    if new:
        v = (existing[-1] + 1) if existing else 1
    else:
        v = version or (existing[-1] if existing else 1)
    return base / f"{name}--v{v}", v, (base / f"{name}--v{existing[-1]}" if existing else None)


def cmd_reel(a):
    root, slug, src = load_stream(a.root)
    vdir, v, prev = version_dir(root / "longform", f"{slug}--{a.name}", a.version, a.new)
    vdir.mkdir(parents=True, exist_ok=True)
    rj = vdir / "reel.json"
    if not rj.exists():
        if prev and prev != vdir and (prev / "reel.json").exists():
            shutil.copy(prev / "reel.json", rj)
        else:
            sys.exit(f"write {rj} first (see references/process-stream.md)")
    cfg = json.loads(rj.read_text())
    name = vdir.name
    parts = vdir / ".parts"
    parts.mkdir(exist_ok=True)
    items = cfg["items"]
    N = len(items)
    vf_common = "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=30,format=yuv420p"
    enc = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2"]

    def seg(i):
        it = items[i]
        d = it["dur"]
        vf = (f"{vf_common},"
              + drawtext(parts, f"t{i}", it["title"], "fontsize=64:fontcolor=white:box=1:boxcolor=black@0.65:boxborderw=28:x=60:y=110") + ","
              + drawtext(parts, f"n{i}", f"{i + 1:02d} / {N}", "fontsize=32:fontcolor=white@0.8:x=64:y=50") + ","
              + f"fade=t=in:d=0.3,fade=t=out:st={d - 0.3}:d=0.3")
        af = f"afade=t=in:d=0.25,afade=t=out:st={d - 0.25}:d=0.25"
        run(["ffmpeg", "-y", "-v", "error", "-ss", str(it["start"]), "-t", str(d), "-i", str(src), "-vf", vf, "-af", af, *enc,
             str(parts / f"{i + 1:02d}.mp4")])

    def card(nm, lines, dur):
        fc, y = "color=c=0x0b0b10:s=1920x1080:r=30,format=yuv420p", 440
        for k, (txt, size, col) in enumerate(lines):
            fc += "," + drawtext(parts, f"{nm}-{k}", txt, f"fontsize={size}:fontcolor={col}:x=(w-text_w)/2:y={y}")
            y += size + 30
        fc += f",fade=t=in:d=0.4,fade=t=out:st={dur - 0.4}:d=0.4"
        run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", fc, "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
             "-t", str(dur), *enc, str(parts / f"{nm}.mp4")])

    card("00", [(cfg.get("title", slug), 96, "white"), (cfg.get("subtitle", ""), 44, "0xaaaaaa")], 4)
    outro = cfg.get("outro", [])
    card("99", [(outro[0] if outro else "Thanks for watching", 56, "white")] + [(t, 36, "0xaaaaaa") for t in outro[1:2]], 4)
    with ThreadPoolExecutor(3) as ex:
        list(ex.map(seg, range(N)))
    order = ["00"] + [f"{i + 1:02d}" for i in range(N)] + ["99"]
    (parts / "list.txt").write_text("".join(f"file '{parts / (o + '.mp4')}'\n" for o in order))
    mp4 = vdir / f"{name}.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(parts / "list.txt"), "-c", "copy",
         "-movflags", "+faststart", str(mp4)])
    # chapter timings of the reel itself
    t, lines = 4, ["0:00 Intro"]
    for it in items:
        lines.append(f"{hms(t, pad=False)} {it['title']}")
        t += it["dur"]
    lines.append(f"{hms(t, pad=False)} Outro")
    (vdir / f"{name}.chapters.md").write_text(
        f"# {name}: chapters\n\n**Video:** `{mp4.name}` (duration {hms(probe_duration(mp4), pad=False)})\n\n```\n" + "\n".join(lines) + "\n```\n")
    run(["ffmpeg", "-y", "-v", "error", "-ss", "6", "-i", str(mp4), "-frames:v", "1", str(vdir / f"{name}.png")])
    shutil.copy(vdir / f"{name}.png", root / "thumbnails" / f"{name}.png")
    shutil.rmtree(parts, ignore_errors=True)
    (vdir / "manifest.json").write_text(json.dumps({
        "built": datetime.datetime.now().isoformat(timespec="seconds"), "source": str(src.relative_to(root)),
        "reel_json": sha(rj), "duration": round(probe_duration(mp4), 1)}, indent=2) + "\n")
    print(f"built {mp4.relative_to(root)}  ({hms(probe_duration(mp4), pad=False)})")


def cmd_short_new(a):
    root, slug, _ = load_stream(a.root)
    vdir, v, prev = version_dir(root / "shorts", f"{slug}--short-{slugify(a.topic)}", None, True)
    vdir.mkdir(parents=True)
    if a.from_prev and prev:
        for f in ["short.json", "page.html", "kit.js"]:
            if (prev / f).exists():
                shutil.copy(prev / f, vdir / f)
        print(f"copied short.json / page.html from {prev.name}")
    else:
        clip = a.clip or "CLIP.mp4"
        (vdir / "short.json").write_text(json.dumps({
            "slug": "project", "clip": f"../../clips/{clip}", "segs": [[0.0, 1.0]], "kind": "educational", "language": "en",
            "face": [0, 0, 100, 100], "stills": {}, "end_card": 1.5, "bpm": 124}, indent=2) + "\n")
    print(vdir)


def cmd_short_build(a):
    d = Path(a.dir).resolve()
    sj = d / "short.json"
    if not sj.exists():
        sys.exit(f"{sj} not found")
    root = d.parent.parent
    cfg = json.loads(sj.read_text())
    project = d / cfg.get("slug", "project")
    name = d.name
    if not a.save_page:
        run([sys.executable, str(SHORT_PY), "cut", "short.json"], cwd=d)
        run([sys.executable, str(SHORT_PY), "scaffold", "short.json"], cwd=d)
        if a.scaffold_only:
            print(f"scaffolded {project}\nnext: edit {project / 'index.html'}, then: stream.py short-build {d} --save-page")
            return
        if not (d / "page.html").exists():
            print(f"no page.html yet: author {project / 'index.html'}, then run with --save-page")
            return
        shutil.copy(d / "page.html", project / "index.html")
        if (d / "kit.js").exists():
            shutil.copy(d / "kit.js", project / "kit.js")
    else:
        if not (project / "index.html").exists():
            sys.exit(f"{project / 'index.html'} not found (run with --scaffold-only first)")
        shutil.copy(project / "index.html", d / "page.html")
        if sha(project / "kit.js") != sha(SKILL / "assets" / "kit.js"):
            shutil.copy(project / "kit.js", d / "kit.js")
        elif (d / "kit.js").exists():
            (d / "kit.js").unlink()
    mp4 = d / f"{name}.mp4"
    run([sys.executable, str(BUILD_PY), str(project), "--out", str(mp4), "--grain", "0", "--crf", "18"])
    bal = subprocess.run([sys.executable, str(SHORT_PY), "balance", str(project)], capture_output=True, text=True).stdout.strip()
    print(bal)
    png = d / f"{name}.png"
    run(["ffmpeg", "-y", "-v", "error", "-i", str(mp4), "-frames:v", "1", str(png)])
    (root / "thumbnails").mkdir(exist_ok=True)
    shutil.copy(png, root / "thumbnails" / f"{name}.png")
    clip = (d / cfg["clip"]).resolve()
    plugin = SKILL.parent.parent / ".claude-plugin" / "plugin.json"
    (d / "manifest.json").write_text(json.dumps({
        "built": datetime.datetime.now().isoformat(timespec="seconds"),
        "plugin_version": json.loads(plugin.read_text()).get("version") if plugin.exists() else None,
        "clip": cfg["clip"], "clip_size": clip.stat().st_size if clip.exists() else None,
        "inputs": {"short.json": sha(sj), "page.html": sha(d / "page.html"), "kit.js": sha(d / "kit.js")},
        "duration": round(probe_duration(mp4), 2), "audio_balance": bal.splitlines()[-1].split(": ", 1)[-1] if bal else None}, indent=2) + "\n")
    print(f"built {mp4.relative_to(root)}  ({probe_duration(mp4):.1f}s)")


def cmd_migrate(a):
    root = Path(a.root).resolve()
    moves = []
    sj = root / "stream.json"
    vids = [p for p in root.glob("*") if p.suffix.lower() in (".mp4", ".mov", ".mkv", ".webm") and p.is_file()]
    src = None
    if sj.exists():
        d = json.loads(sj.read_text())
        slug, src = d["slug"], root / d["source"]
    else:
        if not vids and not (root / "source").exists():
            sys.exit("no video found in the root folder")
        big = max(vids, key=lambda p: p.stat().st_size) if vids else next((root / "source").glob("*"))
        slug = a.slug or guess_slug(big.stem)
        moves.append((big, root / "source" / big.name))
        src = root / "source" / big.name
    for p in sorted((root / "clips").glob("[0-9][0-9]-*.mp4")):
        moves.append((p, root / "clips" / f"{slug}--{p.name}"))
    for p in sorted(q for q in (root / "transcripts").glob("[0-9][0-9]-*.txt") if not q.name.startswith("00-")):
        moves.append((p, root / "transcripts" / f"{slug}--{p.name}"))
    full = root / "transcripts" / "00-full-stream-transcript.txt"
    if full.exists():
        moves.append((full, root / "transcripts" / f"{slug}.transcript.txt"))
    for nm in ["chapters.md"]:
        if (root / nm).exists():
            moves.append((root / nm, root / "chapters" / f"{slug}.chapters.md"))
    if (root / "clips" / "INDEX.md").exists():
        moves.append((root / "clips" / "INDEX.md", root / "chapters" / f"{slug}.clips-index.md"))
    print(f"slug: {slug}")
    for s, d in moves:
        print(("move " if a.apply else "would move ") + f"{s.relative_to(root)} -> {d.relative_to(root)}")
    left = [p.relative_to(root) for p in root.iterdir() if p.name not in DIRS + [".work", "stream.json", ".DS_Store"]
            and not (a.apply and p in [m[0] for m in moves])]
    skipped = [str(p) for p in left if root / p not in [m[0] for m in moves]]
    if skipped:
        print("not moved (decide manually): " + ", ".join(skipped))
    for sub in ["shorts", "longform"]:
        items = [p.name for p in (root / sub).glob("*")] if (root / sub).exists() else []
        if items:
            print(f"{sub}/ has {len(items)} item(s) in an older layout: {', '.join(items[:6])}: move into <slug>--...--vN folders when regenerating")
    if not a.apply:
        print("\ndry run. Re-run with --apply to move files.")
        return
    for d in DIRS + [".work"]:
        (root / d).mkdir(exist_ok=True)
    for s, d in moves:
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(s), str(d))
    sj.write_text(json.dumps({"slug": slug, "source": str(src.relative_to(root))}, indent=2) + "\n")
    print("done; wrote stream.json")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)
    sp.add_parser("doctor").set_defaults(f=cmd_doctor)
    x = sp.add_parser("init"); x.add_argument("root"); x.add_argument("--source"); x.add_argument("--slug"); x.set_defaults(f=cmd_init)
    x = sp.add_parser("transcribe"); x.add_argument("root"); x.add_argument("--model", default="small.en"); x.add_argument("--language"); x.set_defaults(f=cmd_transcribe)
    x = sp.add_parser("clips"); x.add_argument("root"); x.add_argument("--only"); x.add_argument("--force", action="store_true"); x.set_defaults(f=cmd_clips)
    x = sp.add_parser("reel"); x.add_argument("root"); x.add_argument("--name", default="summary"); x.add_argument("--version", type=int); x.add_argument("--new", action="store_true"); x.set_defaults(f=cmd_reel)
    x = sp.add_parser("short-new"); x.add_argument("root"); x.add_argument("--topic", required=True); x.add_argument("--clip"); x.add_argument("--from-prev", action="store_true"); x.set_defaults(f=cmd_short_new)
    x = sp.add_parser("short-build"); x.add_argument("dir"); x.add_argument("--scaffold-only", action="store_true"); x.add_argument("--save-page", action="store_true"); x.set_defaults(f=cmd_short_build)
    x = sp.add_parser("migrate"); x.add_argument("root"); x.add_argument("--slug"); x.add_argument("--apply", action="store_true"); x.set_defaults(f=cmd_migrate)
    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
