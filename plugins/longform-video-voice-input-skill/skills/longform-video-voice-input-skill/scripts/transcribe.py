#!/usr/bin/env python3
"""Word-level transcript of a voiceover (faster-whisper).

  transcribe.py <audio> <out.json> [--model medium.en] [--start S --dur D]

Writes [{start,end,text,words:[{w,s,e}]}] and prints one line per segment.
Converts to 16 kHz mono first. Use --start/--dur to re-check a short stretch (e.g. a suspected
stumble or retake) without VAD, which whisper otherwise merges.
"""
import argparse, json, os, subprocess, tempfile
from faster_whisper import WhisperModel
ap = argparse.ArgumentParser(); ap.add_argument('audio'); ap.add_argument('out'); ap.add_argument('--model', default='medium.en')
ap.add_argument('--start', type=float); ap.add_argument('--dur', type=float); a = ap.parse_args()
tmp = tempfile.mktemp(suffix='.wav')
cmd = ['ffmpeg', '-y', '-loglevel', 'error'] + (['-ss', str(a.start)] if a.start else []) + ['-i', a.audio] + (['-t', str(a.dur)] if a.dur else []) + ['-ac', '1', '-ar', '16000', tmp]
subprocess.run(cmd, check=True)
off = a.start or 0
m = WhisperModel(a.model, device='cpu', compute_type='int8')
segs, _ = m.transcribe(tmp, word_timestamps=True, vad_filter=not a.start, beam_size=5)
out = []
for s in segs:
    out.append({'start': s.start + off, 'end': s.end + off, 'text': s.text, 'words': [{'w': w.word, 's': w.start + off, 'e': w.end + off} for w in s.words]})
    print(f"[{s.start + off:7.2f}-{s.end + off:7.2f}] {s.text}", flush=True)
json.dump(out, open(a.out, 'w'), indent=1); os.remove(tmp)
