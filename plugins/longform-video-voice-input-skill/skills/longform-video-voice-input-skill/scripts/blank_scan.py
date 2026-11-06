#!/usr/bin/env python3
"""Find stretches where the screen is (nearly) empty, e.g. a scene waiting for its first word.

  blank_scan.py <project> [--step 0.5] [--thresh 1.2] [--min 0.5]
Reads out/jframes. Prints [(start, end)] seconds. Fix each with the spoken line on screen (bigSay) or b-roll.
"""
import argparse, glob, json, os, numpy as np
from PIL import Image
ap = argparse.ArgumentParser(); ap.add_argument('project'); ap.add_argument('--step', type=float, default=.5); ap.add_argument('--thresh', type=float, default=1.2); ap.add_argument('--min', type=float, default=.5); ap.add_argument('--fps', type=int, default=30); a = ap.parse_args()
d = os.path.join(a.project, 'out', 'jframes'); n = len(glob.glob(os.path.join(d, '*.jpg'))); res = []
for s in np.arange(0, n / a.fps, a.step):
    p = os.path.join(d, f'{int(s * a.fps):05d}.jpg')
    if not os.path.exists(p): continue
    im = np.asarray(Image.open(p).convert('L').resize((192, 108)), dtype=float)
    if np.abs(np.diff(im, axis=0)).mean() + np.abs(np.diff(im, axis=1)).mean() < a.thresh: res.append(float(s))
rs = []
for s in res:
    if rs and s - rs[-1][1] <= a.step + 1e-6: rs[-1][1] = s
    else: rs.append([s, s])
print([tuple(r) for r in rs if r[1] - r[0] >= a.min])
