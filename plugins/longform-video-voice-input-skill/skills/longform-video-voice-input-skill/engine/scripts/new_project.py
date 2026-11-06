#!/usr/bin/env python3
"""Scaffold a motion-reel project.

usage: new_project.py <dir> [--size 1920x1080 | --preset landscape|portrait|square]
                            [--fps 60] [--duration 30] [--bpm 120] [--title "Brand — Showreel"]
"""
import argparse, os, re, shutil, sys

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRESETS = {"landscape": (1920, 1080), "portrait": (1080, 1920), "square": (1080, 1080)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--preset", choices=PRESETS, default="landscape")
    ap.add_argument("--size", help="WxH, overrides --preset")
    ap.add_argument("--fps", type=int, default=60)
    ap.add_argument("--duration", type=float, default=30)
    ap.add_argument("--bpm", type=float, default=120)
    ap.add_argument("--title", default="YOUR BRAND — SHOWREEL")
    ap.add_argument("--force", action="store_true", help="overwrite index.html/engine.js if present")
    a = ap.parse_args()

    w, h = map(int, a.size.lower().split("x")) if a.size else PRESETS[a.preset]
    d = os.path.abspath(a.dir)
    os.makedirs(os.path.join(d, "media"), exist_ok=True)
    os.makedirs(os.path.join(d, "fonts"), exist_ok=True)
    os.makedirs(os.path.join(d, "out"), exist_ok=True)

    idx = os.path.join(d, "index.html")
    if os.path.exists(idx) and not a.force:
        sys.exit(f"{idx} exists — pass --force to overwrite")
    html = open(os.path.join(SKILL, "assets", "reel.html")).read()
    html = re.sub(r"w: \d+, h: \d+, fps: \d+, duration: [\d.]+, bpm: [\d.]+",
                  f"w: {w}, h: {h}, fps: {a.fps}, duration: {a.duration:g}, bpm: {a.bpm:g}", html, count=1)
    html = html.replace("title: 'YOUR BRAND — SHOWREEL'", f"title: {a.title!r}")
    open(idx, "w").write(html)
    shutil.copy(os.path.join(SKILL, "assets", "engine.js"), os.path.join(d, "engine.js"))
    man = os.path.join(d, "media", "manifest.json")
    if not os.path.exists(man):
        with open(man, "w") as f:
            f.write("{}\n")
    with open(os.path.join(d, ".gitignore"), "w") as f:
        f.write("out/\nmedia/*/\nmedia/*.wav\n")
    print(f"created {d}  ({w}x{h} @ {a.fps}fps, {a.duration:g}s, {a.bpm:g} BPM)")
    print("next: ingest media → edit index.html → render.py sheet → build.py")


if __name__ == "__main__":
    main()
