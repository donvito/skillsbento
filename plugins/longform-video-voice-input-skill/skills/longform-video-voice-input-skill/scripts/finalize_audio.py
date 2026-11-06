#!/usr/bin/env python3
"""Two-pass loudness normalisation to the YouTube level, padded to the video length.

  finalize_audio.py <in.wav> <out.wav> --duration 415 [--lufs -14] [--tp -1.5]
Voice only by default. A music bed under narration proved distracting (ducking pumps in the pauses): only add one if
asked, keep it ~-30 dB under the voice and do NOT sidechain-duck it.
"""
import argparse, json, subprocess
ap = argparse.ArgumentParser(); ap.add_argument('inp'); ap.add_argument('out'); ap.add_argument('--duration', type=float, required=True)
ap.add_argument('--lufs', type=float, default=-14); ap.add_argument('--tp', type=float, default=-1.5); a = ap.parse_args()
base = f"aresample=48000,apad=whole_dur={a.duration}"
err = subprocess.run(['ffmpeg', '-hide_banner', '-i', a.inp, '-af', f"{base},loudnorm=I={a.lufs}:TP={a.tp}:LRA=11:print_format=json", '-f', 'null', '-'], capture_output=True, text=True).stderr
d = json.loads(err[err.rindex('{'):err.rindex('}') + 1])
af = f"{base},loudnorm=I={a.lufs}:TP={a.tp}:LRA=11:measured_I={d['input_i']}:measured_TP={d['input_tp']}:measured_LRA={d['input_lra']}:measured_thresh={d['input_thresh']}:offset={d['target_offset']}:linear=true"
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', a.inp, '-af', af, '-t', str(a.duration), '-ar', '48000', '-ac', '2', a.out], check=True)
print(f"{a.out}  (input {d['input_i']} LUFS -> {a.lufs})")
