#!/usr/bin/env python3
"""Full build: cues -> frames -> score -> encoded MP4.

usage: build.py <project> [--out FILE.mp4] [--workers N] [--grain 3] [--crf 19]
                          [--skip-frames] [--skip-score] [--no-audio]
Loudness is normalised to -14 LUFS / -1 dBTP (streaming/social standard).
"""
import argparse, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))


def sh(*cmd):
    print("$", " ".join(cmd[:4]), "…" if len(cmd) > 4 else "", flush=True)
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--out")
    ap.add_argument("--workers", type=int)
    ap.add_argument("--grain", type=float, default=3, help="film grain strength (0 = off); grain costs file size")
    ap.add_argument("--crf", type=int, default=19)
    ap.add_argument("--skip-frames", action="store_true")
    ap.add_argument("--skip-score", action="store_true")
    ap.add_argument("--no-audio", action="store_true")
    a = ap.parse_args()
    p = os.path.abspath(a.project)
    out = os.path.abspath(a.out) if a.out else os.path.join(p, "out", os.path.basename(p.rstrip("/")) + ".mp4")
    t0 = time.time()
    py = sys.executable

    sh(py, os.path.join(HERE, "render.py"), "cues", p)
    if not a.skip_frames:
        frames = os.path.join(p, "out", "frames")
        if os.path.isdir(frames):
            for f in os.listdir(frames):
                os.remove(os.path.join(frames, f))
        sh(py, os.path.join(HERE, "render.py"), "frames", p, *(["--workers", str(a.workers)] if a.workers else []))
    if not a.skip_score and not a.no_audio:
        sh(py, os.path.join(HERE, "score.py"), p)

    import json
    fps = json.load(open(os.path.join(p, "out", "cues.json")))["config"]["fps"]
    vf = (f"noise=alls={a.grain:g}:allf=t," if a.grain > 0 else "") + "format=yuv420p"
    cmd = ["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(fps), "-i", os.path.join(p, "out", "frames", "%05d.png")]
    if not a.no_audio:
        cmd += ["-i", os.path.join(p, "out", "score.wav"), "-filter_complex", f"[0:v]{vf}[v];[1:a]loudnorm=I=-14:TP=-1:LRA=9[a]",
                "-map", "[v]", "-map", "[a]", "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-shortest"]
    else:
        cmd += ["-vf", vf]
    cmd += ["-c:v", "libx264", "-preset", "slow", "-crf", str(a.crf), "-profile:v", "high", "-movflags", "+faststart"]
    if a.grain > 0:
        cmd += ["-tune", "grain"]
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sh(*cmd, out)
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size", "-of", "default=nw=1", out], capture_output=True, text=True).stdout
    print(f"\n✓ {out}\n{probe.strip()}\nbuilt in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
