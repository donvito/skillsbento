#!/usr/bin/env python3
"""Render a motion-reel project with headless Chromium (Playwright).

  render.py stills <project> <t> [t ...]          -> out/stills/tSSS.ss.png
  render.py sheet  <project> [--every 1.5] [--times ...] [--cols 4]
                                                   -> out/sheet.png contact sheet to review
  render.py frames <project> [--workers 6] [--start S --end E]
                                                   -> out/frames/00000.png ...
  render.py cues   <project>                       -> out/cues.json (config + cues + media, for score.py)
"""
import argparse, asyncio, base64, functools, http.server, json, os, socket, subprocess, sys, threading, time

from playwright.async_api import async_playwright


def serve(root):
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def end_headers(self):
            self.send_header("Cache-Control", "no-store")
            super().end_headers()

    s = socket.socket(); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close()
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), functools.partial(Quiet, directory=root))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return port


async def open_page(browser, port, errors):
    page = await browser.new_page(viewport={"width": 800, "height": 450}, device_scale_factor=1)
    page.on("console", lambda m: errors.append(f"console: {m.text}") if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
    await page.goto(f"http://127.0.0.1:{port}/index.html")
    try:
        await page.wait_for_function("window.READY === true", timeout=90000)
    except Exception:
        print("\n".join(errors) or "page never became READY", file=sys.stderr)
        raise
    return page


async def grab(page, t, path):
    ok = await page.evaluate(f"renderFrame({t})")
    data = await page.evaluate("document.getElementById('c').toDataURL('image/png')")
    with open(path, "wb") as f:
        f.write(base64.b64decode(data.split(",", 1)[1]))
    return ok


async def with_pages(project, n, fn):
    port = serve(project)
    errors = []
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pages = [await open_page(b, port, errors) for _ in range(n)]
        cfg = await pages[0].evaluate("window.REEL.config")
        res = await fn(pages, cfg)
        await b.close()
    for e in dict.fromkeys(errors):
        print(e, file=sys.stderr)
    return res


def stills(project, times, outdir=None):
    outdir = outdir or os.path.join(project, "out", "stills")
    os.makedirs(outdir, exist_ok=True)

    async def fn(pages, cfg):
        paths = []
        for t in times:
            pth = os.path.join(outdir, f"t{t:06.2f}.png")
            await grab(pages[0], t, pth)
            paths.append(pth)
        return paths
    return asyncio.run(with_pages(project, 1, fn))


def sheet(project, every=None, times=None, cols=4):
    if not times:
        async def get_cfg(pages, cfg):
            return cfg
        dur = asyncio.run(with_pages(project, 1, get_cfg))["duration"]
        every = every or max(0.5, dur / 20)
        times, t = [], every / 2
        while t < dur:
            times.append(round(t, 2)); t += every
    outdir = os.path.join(project, "out", "sheet_frames")
    if os.path.isdir(outdir):
        for f in os.listdir(outdir):
            os.remove(os.path.join(outdir, f))
    paths = stills(project, times, outdir)
    rows = (len(paths) + cols - 1) // cols
    out = os.path.join(project, "out", "sheet.png")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-pattern_type", "glob", "-i", os.path.join(outdir, "t*.png"),
                    "-vf", f"scale=480:-2,tile={cols}x{rows}:padding=6:margin=6:color=0x444444", "-frames:v", "1", out], check=True)
    print(out)
    print("times:", ", ".join(f"{t:g}" for t in times))


def frames(project, workers, start=None, end=None):
    outdir = os.path.join(project, "out", "frames")
    os.makedirs(outdir, exist_ok=True)

    async def fn(pages, cfg):
        total = int(round(cfg["fps"] * cfg["duration"]))
        s = start or 0; e = min(end or total, total)
        idx = list(range(s, e))
        chunk = (len(idx) + len(pages) - 1) // len(pages)      # contiguous chunks → clip prefetch hits
        t0 = time.time(); done = [0]; bad = []

        async def work(k):
            for i in idx[k * chunk:(k + 1) * chunk]:
                if not await grab(pages[k], i / cfg["fps"], os.path.join(outdir, f"{i:05d}.png")):
                    bad.append(i)
                done[0] += 1
                if done[0] % 240 == 0:
                    el = time.time() - t0
                    print(f"  {done[0]}/{len(idx)} frames  {el:.0f}s  (~{el / done[0] * (len(idx) - done[0]):.0f}s left)", flush=True)
        await asyncio.gather(*[work(k) for k in range(len(pages))])
        print(f"rendered {len(idx)} frames in {time.time() - t0:.0f}s")
        if bad:
            print(f"WARNING: {len(bad)} frames had media that failed to load (first: {bad[:5]})", file=sys.stderr)
        return cfg
    return asyncio.run(with_pages(project, workers, fn))


def cues(project):
    async def fn(pages, cfg):
        return await pages[0].evaluate("window.REEL")
    reel = asyncio.run(with_pages(project, 1, fn))
    out = os.path.join(project, "out", "cues.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(reel, open(out, "w"), indent=1)
    print(out)
    return reel


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("stills"); p.add_argument("project"); p.add_argument("times", nargs="+", type=float)
    p = sub.add_parser("sheet"); p.add_argument("project"); p.add_argument("--every", type=float); p.add_argument("--times", nargs="*", type=float); p.add_argument("--cols", type=int, default=4)
    p = sub.add_parser("frames"); p.add_argument("project"); p.add_argument("--workers", type=int, default=max(2, min(8, (os.cpu_count() or 4) - 2)))
    p.add_argument("--start", type=int); p.add_argument("--end", type=int)
    p = sub.add_parser("cues"); p.add_argument("project")
    a = ap.parse_args()
    project = os.path.abspath(a.project)
    if not os.path.exists(os.path.join(project, "index.html")):
        sys.exit(f"no index.html in {project}")
    if a.cmd == "stills":
        for pth in stills(project, a.times):
            print(pth)
    elif a.cmd == "sheet":
        sheet(project, a.every, a.times, a.cols)
    elif a.cmd == "frames":
        frames(project, a.workers, a.start, a.end)
    else:
        cues(project)


if __name__ == "__main__":
    main()
