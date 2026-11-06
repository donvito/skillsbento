#!/usr/bin/env python3
"""Render a motion-reel project's frames as JPEGs (a 7-min 1080p video as PNG would need ~30 GB).

  render_frames.py <project> [--workers 8] [--start F --end F] [--force]
Skips frames that already exist, so a partial re-render = delete the changed range, then run with --start/--end.
Warms each worker up first. Frames whose media failed to load are listed at the end: delete and re-render them.
"""
import argparse, asyncio, base64, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.join(HERE, '..', 'engine', 'scripts'), os.path.expanduser('~/.claude/skills/motion-reel/scripts')):
    if os.path.exists(os.path.join(_p, 'render.py')): sys.path.insert(0, _p); break
import render as R
ap = argparse.ArgumentParser(); ap.add_argument('project'); ap.add_argument('--workers', type=int, default=8)
ap.add_argument('--start', type=int, default=0); ap.add_argument('--end', type=int); ap.add_argument('--force', action='store_true'); a = ap.parse_args()
project = os.path.abspath(a.project); out = os.path.join(project, 'out', 'jframes'); os.makedirs(out, exist_ok=True)
async def grab(page, t, path):
    ok = await page.evaluate(f"renderFrame({t})")
    data = await page.evaluate("document.getElementById('c').toDataURL('image/jpeg', 0.93)")
    tmp = path + '.tmp'; open(tmp, 'wb').write(base64.b64decode(data.split(',', 1)[1])); os.replace(tmp, path); return ok
async def fn(pages, cfg):
    total = int(round(cfg['fps'] * cfg['duration'])); e = min(a.end or total, total)
    idx = [i for i in range(a.start, e) if a.force or not os.path.exists(os.path.join(out, f'{i:05d}.jpg'))]
    chunk = max(1, (len(idx) + len(pages) - 1) // len(pages)); t0 = time.time(); done = [0]; bad = []
    async def work(k):
        mine = idx[k * chunk:(k + 1) * chunk]
        if not mine: return
        for _ in range(2): await pages[k].evaluate(f"renderFrame({mine[0] / cfg['fps']})")
        for i in mine:
            if not await grab(pages[k], i / cfg['fps'], os.path.join(out, f'{i:05d}.jpg')): bad.append(i)
            done[0] += 1
            if done[0] % 600 == 0: el = time.time() - t0; print(f'  {done[0]}/{len(idx)}  {el:.0f}s', flush=True)
    await asyncio.gather(*[work(k) for k in range(len(pages))])
    print(f'rendered {len(idx)} frames in {time.time() - t0:.0f}s; total expected {total}; bad={sorted(bad)}')
    return bad
bad = asyncio.run(R.with_pages(project, a.workers, fn))
if bad:  # retry bad frames once, single worker
    for i in bad: os.remove(os.path.join(out, f'{i:05d}.jpg'))
    async def retry(pages, cfg):
        still = []
        for i in sorted(bad):
            for _ in range(2): await pages[0].evaluate(f"renderFrame({i / cfg['fps']})")
            if not await grab(pages[0], i / cfg['fps'], os.path.join(out, f'{i:05d}.jpg')): still.append(i)
        print('retried bad frames; still bad:', still)
    asyncio.run(R.with_pages(project, 1, retry))
