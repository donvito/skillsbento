#!/usr/bin/env python3
"""Renders each scene to one full-window JPEG for a still `image` backdrop.

The desktop app draws photos only from a still image backdrop, so the scene is
laid out by build_scenes.py (F1_STILL=1: wider margins, no motion), drawn by
headless Chrome at 2560 x 1600 and saved as backdrops/<scene>.jpg under 1 MiB.

Usage: python3 tools/build_stills.py [photo-dir]
photo-dir defaults to photos/; give a folder of larger crops (same file
names) for a sharper result. Needs Google Chrome and ImageMagick (`magick`).
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
W, H = 2560, 1600

env = dict(os.environ, F1_STILL="1")
if len(sys.argv) > 1:
    env["F1_PHOTOS"] = str(Path(sys.argv[1]).resolve())

with tempfile.TemporaryDirectory() as tmp:
    subprocess.run([sys.executable, str(ROOT / "tools" / "build_scenes.py"), tmp], check=True, env=env)
    out = ROOT / "backdrops"
    out.mkdir(exist_ok=True)
    for svg in sorted(Path(tmp).glob("*.svg")):
        page = Path(tmp) / f"{svg.stem}.html"
        page.write_text(f'<html><body style="margin:0;background:#000">'
                        f'<img src="{svg.as_uri()}" style="width:{W}px;height:{H}px;display:block"></body></html>')
        png = Path(tmp) / f"{svg.stem}.png"
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--virtual-time-budget=2000",
                        f"--screenshot={png}", f"--window-size={W},{H}", page.as_uri()],
                       check=True, capture_output=True)
        jpg = out / f"{svg.stem}.jpg"
        for quality in (86, 80, 74, 68):
            subprocess.run(["magick", str(png), "-crop", f"{W}x{H}+0+0", "+repage", "-strip",
                            "-interlace", "Plane", "-quality", str(quality), str(jpg)], check=True)
            if jpg.stat().st_size < 1024 * 1024:
                break
        print(f"{jpg.relative_to(ROOT)}: {jpg.stat().st_size // 1024} KB")
