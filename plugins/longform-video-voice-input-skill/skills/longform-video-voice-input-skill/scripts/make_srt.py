#!/usr/bin/env python3
"""Captions from the edited word timings (names already fixed by edit_voice.py's "fix").
  make_srt.py <words.json> <out.srt>
"""
import json, sys
W = json.load(open(sys.argv[1]))
ts = lambda t: f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(round((t % 1) * 1000)) % 1000:03d}"
cues, cur = [], []
for w in W:
    cur.append(w); s = ' '.join(x['w'] for x in cur)
    if w['w'][-1] in '.?!' or len(s) > 42 or (w['w'][-1] == ',' and len(s) > 28): cues.append(cur); cur = []
if cur: cues.append(cur)
m = []
for c in cues:
    if m and len(c) == 1: m[-1] += c
    else: m.append(c)
out = []
for i, c in enumerate(m):
    e = min(c[-1]['e'] + .25, m[i + 1][0]['s'] if i + 1 < len(m) else c[-1]['e'] + .5)
    out.append(f"{i + 1}\n{ts(c[0]['s'])} --> {ts(e)}\n{' '.join(x['w'] for x in c).replace(' -', '-')}\n")
open(sys.argv[2], 'w').write('\n'.join(out)); print(len(out), 'cues ->', sys.argv[2])
