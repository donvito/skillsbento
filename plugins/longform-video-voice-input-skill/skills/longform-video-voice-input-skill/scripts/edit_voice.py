#!/usr/bin/env python3
"""Edit the voiceover from an edit list and remap every word time to the new timeline.

  edit_voice.py <edit.json>

edit.json (all times on the ORIGINAL recording's timeline):
{
  "audio": "work/voice_enhanced.wav",     # enhanced audio, same timeline as the original recording
  "transcript": "work/transcript.json",   # from transcribe.py
  "keep": [[440.70, 448.35], [7.30, 229.62], [241.80, 438.75]],  # ranges to keep, in PLAY order
                                           #   (lets a pickup line recorded at the end replace a clipped intro)
  "cut": [[393.35, 396.25]],               # extra removals inside kept ranges (stumbles, false starts)
  "add_words": [{"w": "Let", "s": 396.3, "e": 396.6}],  # optional words re-transcribed with --start/--dur
  "pause_max": 1.4, "pause_target": 0.85,  # pauses longer than pause_max shrink to pause_target
  "lead": 0.35, "tail": 0.5,               # silence before the first word / after the last
  "fix": {"Rockbot": "Grok Bot", "Chachipiti,": "ChatGPT,"},  # whisper spelling fixes for captions/sync
  "out_audio": "work/vo.wav", "out_words": "work/words.json", "out_js": "video_v1/vo.js"
}
Prints the new duration. vo.js defines window.VO = [[word, start, end], ...] for the page (lib.js wt/phraseTimes).
"""
import json, sys, numpy as np
from scipy.io import wavfile
cfg = json.load(open(sys.argv[1]))
sr, x = wavfile.read(cfg['audio']); x = x.astype(np.float32) / (32768.0 if x.dtype == np.int16 else 2147483648.0 if x.dtype == np.int32 else 1.0)
if x.ndim == 1: x = x[:, None]
W = [dict(w=w['w'].strip(), s=w['s'], e=w['e']) for s in json.load(open(cfg['transcript'])) for w in s['words']] + cfg.get('add_words', [])
W.sort(key=lambda w: w['s'])
cuts = [tuple(c) for c in cfg.get('cut', [])]
pm, pt = cfg.get('pause_max', 1.4), cfg.get('pause_target', 0.85)
for i in range(1, len(W)):
    a, b = W[i - 1]['e'], W[i]['s']
    if b - a > pm and not any(ca <= a <= cb for ca, cb in cuts):
        mid = (a + b) / 2; cuts.append((mid - (b - a - pt) / 2, mid + (b - a - pt) / 2))
ranges = []
for a, b in cfg['keep']:
    cur = a
    for ca, cb in sorted(cuts):
        if a < ca and cb < b and ca > cur: ranges.append((cur, ca)); cur = cb
    ranges.append((cur, b))
XF = int(.025 * sr); out = []; tmap = []; pos = 0.0; ramp = np.linspace(0, 1, XF)[:, None]
for a, b in ranges:
    seg = x[int(a * sr):int(b * sr)].copy(); seg[:XF] *= ramp; seg[-XF:] *= ramp[::-1]
    tmap.append((a, b, pos)); out.append(seg); pos += b - a
lead, tail = cfg.get('lead', .35), cfg.get('tail', .5)
y = np.concatenate([np.zeros((int(lead * sr), x.shape[1]), np.float32)] + out + [np.zeros((int(tail * sr), x.shape[1]), np.float32)])
wavfile.write(cfg['out_audio'], sr, (np.clip(y, -1, 1) * 32767).astype(np.int16))
def remap(t):
    for a, b, p in tmap:
        if a - 1e-3 <= t <= b + 1e-3: return lead + p + (t - a)
fix = cfg.get('fix', {}); NW = []
for w in W:
    s, e = remap(w['s']), remap(w['e'])
    if s is not None and e is not None: NW.append(dict(w=fix.get(w['w'], w['w']), s=round(s, 3), e=round(e, 3)))
NW.sort(key=lambda w: w['s']); json.dump(NW, open(cfg['out_words'], 'w'))
if cfg.get('out_js'): open(cfg['out_js'], 'w').write('window.VO=' + json.dumps([[w['w'], w['s'], w['e']] for w in NW]) + ';\n')
print(f"ranges={len(ranges)} duration={len(y) / sr:.2f}s words={len(NW)}")
