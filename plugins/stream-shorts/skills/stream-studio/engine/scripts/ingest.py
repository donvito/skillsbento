#!/usr/bin/env python3
"""Inspect and ingest user media for a motion-reel project.

  ingest.py probe <file>... [--every 2] [--out DIR]
      Prints duration / fps / size / audio / detected scene cuts, and writes a
      thumbnail contact sheet per file (one tile every --every seconds) so you
      can LOOK at the footage and pick in/out points.

  ingest.py add <project> <id>=<path>[@IN-OUT | @IN+DUR] ... [--fps N] [--no-audio]
      Clips  -> media/<id>/00001.jpg… frame sequence (+ media/<id>.wav if it has sound)
      Images -> media/<id>.png|jpg
      Updates media/manifest.json. Headless Chromium can't decode H.264, so clips
      are always pre-extracted; the engine plays them frame-accurately.

  ingest.py music <project> <path> [--id music]
      Converts a soundtrack to media/<id>.wav (48 kHz stereo) for music.mode='file'.

  ingest.py list <project>
"""
import argparse, json, os, re, shutil, subprocess, sys

IMG_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff", ".heic", ".avif", ".svg"}


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def ffprobe(path):
    out = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", path]).stdout
    j = json.loads(out)
    v = next((s for s in j["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in j["streams"] if s["codec_type"] == "audio"), None)
    info = {"duration": float(j["format"].get("duration") or 0), "audio": a is not None}
    if v:
        num, den = (v.get("avg_frame_rate") or v.get("r_frame_rate") or "0/1").split("/")
        info["fps"] = float(num) / float(den) if float(den) else 0
        w, h = int(v["width"]), int(v["height"])
        rot = 0
        for sd in v.get("side_data_list", []) or []:
            rot = int(sd.get("rotation", 0) or 0)
        rot = int(v.get("tags", {}).get("rotate", rot) or rot)
        if abs(rot) in (90, 270):
            w, h = h, w
        info.update(w=w, h=h, codec=v.get("codec_name"))
    return info


def project_config(project):
    html = open(os.path.join(project, "index.html")).read()
    m = re.search(r"w: (\d+), h: (\d+), fps: (\d+)", html)
    if not m:
        sys.exit("could not read w/h/fps from index.html REEL_CONFIG")
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def load_manifest(project):
    p = os.path.join(project, "media", "manifest.json")
    return json.load(open(p)) if os.path.exists(p) else {}


def save_manifest(project, man):
    p = os.path.join(project, "media", "manifest.json")
    json.dump(man, open(p, "w"), indent=2)


def scene_cuts(path, thresh=0.3):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-an", "-vf", f"scale=320:-2,select='gt(scene,{thresh})',showinfo", "-f", "null", "-"],
                       capture_output=True, text=True)
    return [round(float(x), 2) for x in re.findall(r"pts_time:([\d.]+)", r.stderr)]


def cmd_probe(a):
    out = a.out or os.path.join(os.getcwd(), "probe")
    os.makedirs(out, exist_ok=True)
    for f in a.files:
        ext = os.path.splitext(f)[1].lower()
        info = ffprobe(f)
        name = re.sub(r"[^\w.-]+", "_", os.path.basename(f))
        if ext in IMG_EXT or info.get("duration", 0) < 0.2:
            print(f"IMAGE {f}: {info.get('w')}x{info.get('h')}")
            continue
        cuts = scene_cuts(f)
        print(f"CLIP  {f}\n      {info['duration']:.2f}s  {info.get('w')}x{info.get('h')}  {info.get('fps', 0):.2f}fps  "
              f"audio={'yes' if info['audio'] else 'no'}  codec={info.get('codec')}")
        print(f"      scene cuts: {cuts if cuts else 'none detected'}")
        every = a.every if a.every else max(1.0, info["duration"] / 24)
        n = max(1, int(info["duration"] // every))
        cols = 6
        rows = (n + cols - 1) // cols
        sheet = os.path.join(out, name + ".jpg")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", f, "-vf",
                        f"fps=1/{every},scale=320:-2,tile={cols}x{rows}:padding=4:margin=4", "-frames:v", "1", "-q:v", "4", sheet], check=True)
        print(f"      sheet: {sheet}  (tile k = {every:g}*k s, left→right, top→bottom, k from 0)")


def parse_spec(spec):
    if "=" not in spec:
        sys.exit(f"bad spec {spec!r}: expected id=path[@in-out]")
    mid, rest = spec.split("=", 1)
    rng = None
    m = re.match(r"^(.*)@([\d.]+)([-+])([\d.]+)$", rest)
    if m:
        rest, a, op, b = m.group(1), float(m.group(2)), m.group(3), float(m.group(4))
        rng = (a, b if op == "-" else a + b)
    if not re.match(r"^[A-Za-z0-9_-]+$", mid):
        sys.exit(f"bad id {mid!r}: use letters, digits, - or _")
    return mid, os.path.expanduser(rest), rng


def cmd_add(a):
    project = os.path.abspath(a.project)
    W, H, FPS = project_config(project)
    man = load_manifest(project)
    mdir = os.path.join(project, "media")
    for spec in a.items:
        mid, path, rng = parse_spec(spec)
        if not os.path.exists(path):
            sys.exit(f"missing file: {path}")
        ext = os.path.splitext(path)[1].lower()
        info = ffprobe(path)
        is_img = ext in IMG_EXT or info.get("duration", 0) < 0.2 and "fps" not in info
        if is_img:
            out_ext = ".png" if ext in {".png", ".svg", ".gif", ".webp", ".tif", ".tiff"} else ".jpg"
            dst = os.path.join(mdir, mid + out_ext)
            if ext in {".png", ".jpg", ".jpeg"}:
                shutil.copy(path, dst)
            else:
                run(["ffmpeg", "-loglevel", "error", "-y", "-i", path, "-frames:v", "1", dst])
            i2 = ffprobe(dst)
            man[mid] = {"type": "image", "src": f"media/{mid}{out_ext}", "w": i2["w"], "h": i2["h"], "source": path}
            print(f"image {mid}: {i2['w']}x{i2['h']}")
            continue
        t0, t1 = rng if rng else (0.0, info["duration"])
        t1 = min(t1, info["duration"])
        if t1 - t0 > 20 and not a.long:
            sys.exit(f"{mid}: {t1 - t0:.1f}s range — pick a tighter @in-out (or pass --long). Probe first to choose.")
        fps = min(a.fps or FPS, round(info.get("fps") or FPS))
        d = os.path.join(mdir, mid)
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
        # scale so the clip can COVER the canvas at 100% zoom (extra 15% headroom for push-ins)
        cw, ch = int(W * 1.15), int(H * 1.15)
        vf = (f"fps={fps},scale=w='if(gt(iw/ih,{cw}/{ch}),-2,min(iw,{cw}))':h='if(gt(iw/ih,{cw}/{ch}),min(ih,{ch}),-2)'")
        run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{t0}", "-to", f"{t1}", "-i", path, "-an", "-vf", vf, "-q:v", "3", os.path.join(d, "%05d.jpg")])
        frames = len([f for f in os.listdir(d) if f.endswith(".jpg")])
        fi = ffprobe(os.path.join(d, "00001.jpg"))
        entry = {"type": "clip", "dir": f"media/{mid}", "ext": "jpg", "fps": fps, "frames": frames, "duration": frames / fps,
                 "w": fi["w"], "h": fi["h"], "source": path, "in": t0, "out": t1, "audio": False}
        if info["audio"] and not a.no_audio:
            run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{t0}", "-to", f"{t1}", "-i", path, "-vn", "-ac", "2", "-ar", "48000", os.path.join(mdir, mid + ".wav")])
            entry["audio"] = f"media/{mid}.wav"
        man[mid] = entry
        print(f"clip  {mid}: {entry['duration']:.2f}s  {frames} frames @ {fps}fps  {fi['w']}x{fi['h']}  audio={'yes' if entry['audio'] else 'no'}")
    save_manifest(project, man)


def cmd_music(a):
    project = os.path.abspath(a.project)
    man = load_manifest(project)
    dst = os.path.join(project, "media", a.id + ".wav")
    run(["ffmpeg", "-loglevel", "error", "-y", "-i", os.path.expanduser(a.path), "-vn", "-ac", "2", "-ar", "48000", dst])
    info = ffprobe(dst)
    man[a.id] = {"type": "audio", "src": f"media/{a.id}.wav", "duration": info["duration"], "source": a.path}
    save_manifest(project, man)
    print(f"music {a.id}: {info['duration']:.2f}s -> {dst}")


def cmd_list(a):
    for k, v in load_manifest(os.path.abspath(a.project)).items():
        extra = f"{v['duration']:.2f}s {v['frames']}f @{v['fps']}" if v["type"] == "clip" else ""
        print(f"{k:14s} {v['type']:6s} {v.get('w', '')}x{v.get('h', '')} {extra}  ← {v.get('source', '')}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("probe"); p.add_argument("files", nargs="+"); p.add_argument("--every", type=float); p.add_argument("--out")
    p = sub.add_parser("add"); p.add_argument("project"); p.add_argument("items", nargs="+"); p.add_argument("--fps", type=int)
    p.add_argument("--no-audio", action="store_true"); p.add_argument("--long", action="store_true")
    p = sub.add_parser("music"); p.add_argument("project"); p.add_argument("path"); p.add_argument("--id", default="music")
    p = sub.add_parser("list"); p.add_argument("project")
    a = ap.parse_args()
    {"probe": cmd_probe, "add": cmd_add, "music": cmd_music, "list": cmd_list}[a.cmd](a)


if __name__ == "__main__":
    main()
