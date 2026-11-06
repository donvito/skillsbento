#!/usr/bin/env python3
"""Build the soundtrack for a motion-reel project from out/cues.json (render.py cues).

  score.py <project>            -> out/score.wav (48 kHz stereo)

Picture and sound share one timeline: every cue in index.html (impact, whoosh,
riser, blip, stab, bell, tick, typing, clip_audio) becomes a sound here, and the
music bed follows REEL_CONFIG.music:
  {mode:'synth', style:'energetic'|'minimal'|'cinematic', mood:'dark'|'bright'|'epic',
   sections:[{start,end,level:'full'|'light'|'none'}]}   (sections optional)
  {mode:'file', src:'media/music.wav', offset:0, gain:.9, sfx:.6}
  {mode:'none'}                                            (SFX only)
"""
import json, os, sys

import numpy as np
import scipy.signal as sg
from scipy.io import wavfile

SR = 48000
rs = np.random.default_rng(7)

MOODS = {
    "dark": {"chords": [(174.61, 207.65, 261.63, 349.23), (138.59, 174.61, 207.65, 277.18), (207.65, 261.63, 311.13, 415.30), (155.56, 196.00, 233.08, 311.13)],
             "roots": [87.31, 69.30, 103.83, 77.78], "pent": [349.23, 415.30, 466.16, 523.25, 622.25]},
    "bright": {"chords": [(261.63, 329.63, 392.0, 523.25), (196.0, 246.94, 293.66, 392.0), (220.0, 261.63, 329.63, 440.0), (174.61, 220.0, 261.63, 349.23)],
               "roots": [65.41, 98.0, 110.0, 87.31], "pent": [261.63, 293.66, 329.63, 392.0, 440.0]},
    "epic": {"chords": [(146.83, 174.61, 220.0, 293.66), (116.54, 146.83, 174.61, 233.08), (174.61, 220.0, 261.63, 349.23), (130.81, 164.81, 196.0, 261.63)],
             "roots": [73.42, 58.27, 87.31, 65.41], "pent": [293.66, 349.23, 392.0, 440.0, 523.25]},
}


def tt(d):
    return np.arange(max(1, int(d * SR))) / SR


def noise(d):
    return rs.standard_normal(max(1, int(d * SR)))


def lp(x, f, order=2):
    return np.asarray(sg.sosfilt(sg.butter(order, min(f, SR / 2 - 100), "low", fs=SR, output="sos"), x, axis=-1))


def hp(x, f, order=2):
    return np.asarray(sg.sosfilt(sg.butter(order, f, "high", fs=SR, output="sos"), x, axis=-1))


def bp(x, lo, hi, order=2):
    return np.asarray(sg.sosfilt(sg.butter(order, [lo, hi], "band", fs=SR, output="sos"), x, axis=-1))


def saw(ph):
    return np.asarray(sg.sawtooth(ph))


# ---------------- instruments ----------------
def kick(big=False, soft=False):
    t = tt(0.9 if big else 0.45)
    f = 44 + (120 if big else 105) * np.exp(-t * 26)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * (3.2 if big else 7.5))
    click = hp(noise(t[-1] + 1 / SR), 2000)[: len(t)] * np.exp(-t * 320) * (0.1 if soft else 0.35)
    x = np.tanh(1.6 * (body + click))
    return lp(x, 900) if soft else x


def clap():
    t = tt(0.35)
    env = sum(np.exp(-np.clip(t - o, 0, None) * 220) * (t >= o) for o in (0, 0.011, 0.023)) + 0.5 * np.exp(-t * 16) * (t >= 0.023)
    return bp(noise(0.35), 900, 5200) * env * 0.9


def rim():
    t = tt(0.08)
    return bp(noise(0.08), 1200, 2600, 3) * np.exp(-t * 90) * 0.9 + np.sin(2 * np.pi * 820 * t) * np.exp(-t * 60) * 0.3


def hat(open_=False, vol=0.5):
    d = 0.3 if open_ else 0.06
    return hp(noise(d), 7500, 4) * np.exp(-tt(d) * (14 if open_ else 75)) * vol


def tom(f0=95):
    t = tt(0.9)
    f = f0 * (0.65 + 0.35 * np.exp(-t * 8))
    return np.tanh(1.5 * (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.5) + lp(noise(0.9), 1200) * np.exp(-t * 18) * 0.3))


def stereo(x, pan=0.0):
    return np.vstack([x * np.cos((pan + 1) * np.pi / 4), x * np.sin((pan + 1) * np.pi / 4)]) * 1.414


def whoosh(d, up=True):
    x = noise(d)
    f, _, Z = sg.stft(x, SR, nperseg=1024)
    tn = np.linspace(0, 1, Z.shape[1])
    fc = 300 * (40 ** tn) if up else 12000 * (1 / 40) ** tn
    mask = np.exp(-((np.log(f[:, None] + 1) - np.log(fc[None, :])) ** 2) / 0.35)
    _, y = sg.istft(Z * mask, SR, nperseg=1024)
    y = np.asarray(y)[: len(x)]
    t = tt(d)[: len(y)]
    y = y * ((t / d) ** 2.2 if up else np.exp(-t * 4))
    y = y / (np.abs(y).max() + 1e-9)
    pan = np.linspace(-0.7, 0.7, len(y))
    return np.vstack([y * np.cos((pan + 1) * np.pi / 4), y * np.sin((pan + 1) * np.pi / 4)]) * 1.4


def riser(d):
    t = tt(d)
    f = 180 * (6 ** (t / d))
    tone = lp(saw(2 * np.pi * np.cumsum(f) / SR) + 0.5 * saw(2 * np.pi * np.cumsum(f * 1.5) / SR), 2500) * (t / d) ** 2 * 0.25
    return whoosh(d) + np.vstack([tone, tone])


def impact(big=1.0):
    d = 2.6
    t = tt(d)
    f = 30 + 55 * np.exp(-t * 9)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.0)
    crash = lp(noise(d), 6000) * np.exp(-t * 2.6) * 0.45
    hit = hp(noise(d), 1500) * np.exp(-t * 30) * 0.5
    return np.tanh(1.3 * (boom + crash + hit)) * big


def blip(freq, d=0.18):
    t = tt(d)
    return np.sin(2 * np.pi * freq * t + 1.5 * np.sin(2 * np.pi * freq * 2 * t) * np.exp(-t * 30)) * np.exp(-t * 26)


def bell(freq, d=1.2):
    t = tt(d)
    return (np.sin(2 * np.pi * freq * t) + 0.4 * np.sin(2 * np.pi * freq * 2.76 * t) * np.exp(-t * 6)) * np.exp(-t * 3.5) * 0.6


def pluck(freq, d=0.4):
    t = tt(d)
    x = saw(2 * np.pi * freq * t) * 0.5 + np.sin(2 * np.pi * freq * t)
    env = np.exp(-t * 9)
    return (lp(x, 3000) * env + lp(x, 700) * (1 - env)) * np.exp(-t * 6) * 0.5


def tick():
    return bp(noise(0.02), 2500, 9000) * np.exp(-tt(0.02) * 400) * 0.6


def saw_voice(freq, d, cutoff, a=0.01, r=0.1):
    t = tt(d)
    x = sum(saw(2 * np.pi * freq * k * t + rs.uniform(0, 6.28)) for k in (0.996, 1.0, 1.004)) / 3
    return lp(x, cutoff) * np.minimum(1, t / a) * np.minimum(1, (d - t) / r)


def chord(freqs, d, cutoff, a=0.01, r=0.1):
    L = sum(saw_voice(f * 0.999, d, cutoff, a, r) for f in freqs)
    R = sum(saw_voice(f * 1.001, d, cutoff, a, r) for f in freqs)
    return np.vstack([L, R]) / len(freqs)


def bass(freq, d, sine=False):
    t = tt(d)
    if sine:
        x = np.sin(2 * np.pi * freq * t) + 0.25 * np.sin(4 * np.pi * freq * t)
    else:
        x = saw(2 * np.pi * freq * t) * 0.6 + np.sin(2 * np.pi * freq * t)
        env = np.exp(-t * 18)
        x = lp(x, 1100) * env + lp(x, 180) * (1 - env)
    return np.tanh(1.4 * x) * np.minimum(1, t / 0.004) * np.minimum(1, (d - t) / 0.02)


def read_wav(path):
    sr, x = wavfile.read(path)
    x = x.astype(np.float32) / (32768.0 if x.dtype == np.int16 else 1.0)
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    x = x.T[:2]
    if sr != SR:
        x = sg.resample_poly(x, SR, sr, axis=1)
    return x


# ---------------- score ----------------
def build(project):
    reel = json.load(open(os.path.join(project, "out", "cues.json")))
    cfg, cues, media = reel["config"], sorted(reel["cues"], key=lambda q: q["t"]), reel.get("media", {})
    DUR, BPM = float(cfg["duration"]), float(cfg["bpm"])
    BEAT = 60 / BPM
    N = int(SR * DUR)
    music = cfg.get("music") or {"mode": "synth"}
    mood = MOODS.get(music.get("mood", "dark"), MOODS["dark"])
    style = music.get("style", "energetic")
    CH, ROOT, PENT = mood["chords"], mood["roots"], mood["pent"]
    bus = {k: np.zeros((2, N)) for k in ("drums", "bass", "pad", "fx", "send", "clip")}

    def add(name, sig, t, gain=1.0, pan=0.0, send=0.0):
        i = int(round(t * SR))
        if i >= N or gain == 0:
            return
        sig = stereo(sig, pan) if sig.ndim == 1 else sig
        if i < 0:
            sig, i = sig[:, -i:], 0
        n = min(sig.shape[1], N - i)
        bus[name][:, i:i + n] += sig[:, :n] * gain
        if send:
            bus["send"][:, i:i + n] += sig[:, :n] * gain * send

    bar_of = lambda t: int(t // (4 * BEAT)) % 4
    note = lambda k: PENT[int(k) % 5] * 2 ** (int(k) // 5 + 1)

    impacts = [q["t"] for q in cues if q["type"] == "impact"]
    end_t = next((q["t"] for q in cues if q.get("end")), impacts[-1] if impacts else DUR)
    start_t = impacts[0] if impacts else 0.0
    sections = music.get("sections") or [{"start": start_t, "end": end_t, "level": "full"}]
    kicks = []

    if music.get("mode", "synth") == "synth":
        # intro pad before the groove, outro chord after it
        if start_t > 0.2:
            add("pad", chord(CH[0], start_t + 0.2, 900, a=min(1.2, start_t * 0.6), r=0.3), 0, 0.33, send=0.4)
        for sec in sections:
            lvl = sec.get("level", "full")
            if lvl == "none":
                continue
            t = sec["start"]
            while t < sec["end"] - 1e-6:
                k = int(round((t - sec["start"]) / BEAT))
                beat_in_bar = int(round(t / BEAT)) % 4
                r = ROOT[bar_of(t)]
                if style == "energetic":
                    if lvl == "full":
                        kicks.append(t); add("drums", kick(), t, 0.95)
                        if beat_in_bar % 2 == 1:
                            add("drums", clap(), t, 0.55, send=0.25)
                        add("bass", bass(r, 0.22), t + BEAT / 2, 0.55)
                        add("drums", hat(vol=.18), t + BEAT / 4, 1, pan=-0.3); add("drums", hat(vol=.18), t + 3 * BEAT / 4, 1, pan=-0.3)
                    add("drums", hat(), t + BEAT / 2, 0.8, pan=0.25)
                    if k % 8 == 7:
                        add("drums", hat(True), t + BEAT / 2, 0.3, pan=0.4)
                elif style == "minimal":
                    if lvl == "full" and beat_in_bar in (0, 2):
                        kicks.append(t); add("drums", kick(soft=True), t, 0.8)
                    if lvl == "full" and beat_in_bar == 3:
                        add("drums", rim(), t, 0.35, send=0.3)
                    add("drums", hat(vol=.12), t + BEAT / 2, 1, pan=0.3)
                    tones = CH[bar_of(t)]
                    for h in (0, 1):
                        add("pad", pluck(tones[(k * 2 + h) % 4] * 2), t + h * BEAT / 2, 0.28, pan=0.3 * (1 - 2 * h), send=0.35)
                    if beat_in_bar == 0 and lvl == "full":
                        add("bass", bass(r, BEAT * 2.4, sine=True), t, 0.5)
                else:  # cinematic
                    if lvl == "full" and beat_in_bar in (0, 1, 3):
                        kicks.append(t); add("drums", tom(95 if beat_in_bar == 0 else 120), t, 0.7, send=0.3)
                    for s16 in range(4):
                        f = r * (2 if s16 % 2 else 4)
                        add("bass", lp(saw(2 * np.pi * f * tt(BEAT / 4 * 0.9)), 1100) * np.exp(-tt(BEAT / 4 * 0.9) * 10), t + s16 * BEAT / 4, 0.18 if lvl == "full" else 0.1)
                t += BEAT
        # pads per bar across the groove
        b = 4 * BEAT
        t = (int(start_t / b)) * b
        while t < end_t - 1e-6:
            if any(s["start"] - 1e-6 <= t < s["end"] and s.get("level", "full") != "none" for s in sections):
                cut = 900 if style == "minimal" else 1400 if style == "cinematic" else 2000
                add("pad", chord(CH[bar_of(t)], min(b + 0.05, end_t - t + 0.05), cut, a=0.05 if style == "energetic" else 0.4, r=0.2), t, 0.26, send=0.3)
            t += b
        # outro
        add("pad", chord(CH[0] + (CH[0][1] * 1.5,), max(0.5, DUR - end_t), 2200, a=0.01, r=min(1.5, max(0.3, DUR - end_t - 0.1))), end_t, 0.45, send=0.6)
        add("bass", bass(ROOT[0] / 2, max(0.5, min(2.0, DUR - end_t))), end_t, 0.6)
    elif music["mode"] == "file":
        src = os.path.join(project, music["src"])
        x = read_wav(src)
        off = int(float(music.get("offset", 0)) * SR)
        x = x[:, off:off + N]
        fade = np.minimum(1, (x.shape[1] - np.arange(x.shape[1])) / (0.6 * SR))
        add("pad", x * fade, 0, float(music.get("gain", 0.9)))

    sfx = float(music.get("sfx", 1.0 if music.get("mode", "synth") == "synth" else 0.6))
    for q in cues:
        t, ty, g = q["t"], q["type"], float(q.get("gain", 1.0))
        if ty == "impact":
            add("fx", impact(g), t, 0.75 * sfx, send=0.35)
            add("drums", kick(big=True), t, 0.7 * sfx)
        elif ty == "whoosh":
            add("fx", whoosh(q.get("dur", 0.5), up=q.get("up", True)), t, 0.5 * g * sfx)
        elif ty == "riser":
            add("fx", riser(q.get("dur", 1.5)), t, 0.5 * g * sfx)
        elif ty == "blip":
            add("fx", blip(note(q.get("note", 5))), t, 0.25 * g * sfx, pan=q.get("pan", 0), send=0.3)
        elif ty == "bell":
            add("fx", bell(note(q.get("note", 10))), t, 0.18 * g * sfx, pan=q.get("pan", 0), send=0.6)
        elif ty == "tick":
            add("fx", tick(), t, 0.3 * g * sfx, pan=q.get("pan", 0))
        elif ty == "typing":
            n = int(q.get("dur", 0.6) * q.get("cps", 64) / 2)
            for j in range(n):
                add("fx", tick(), t + j * 2 / q.get("cps", 64), (0.3 + 0.2 * rs.random()) * g * sfx, pan=rs.uniform(-0.3, 0.3))
        elif ty == "stab":
            add("pad", chord([f * 2 for f in CH[bar_of(t)]], 0.28, 4200, a=0.003, r=0.12), t, 0.35 * g * sfx, send=0.3)
            add("fx", hp(noise(0.4), 3000) * np.exp(-tt(0.4) * 9) * 0.35, t, 0.5 * g * sfx)
            kicks.append(t)
        elif ty == "clip_audio":
            m = media.get(q["id"], {})
            if not m.get("audio"):
                print(f"clip_audio: {q['id']} has no extracted audio — skipped", file=sys.stderr)
                continue
            x = read_wav(os.path.join(project, m["audio"]))
            i0 = int(float(q.get("in", 0)) * SR)
            x = x[:, i0:i0 + int(float(q.get("dur", x.shape[1] / SR)) * SR)]
            fi, fo = int(q.get("fadeIn", 0.03) * SR), int(q.get("fadeOut", 0.15) * SR)
            env = np.ones(x.shape[1])
            if fi: env[:fi] = np.linspace(0, 1, min(fi, len(env)))
            if fo: env[-fo:] = np.linspace(1, 0, min(fo, len(env)))
            add("clip", x * env, t, g)
        else:
            print(f"unknown cue type {ty!r} at {t}", file=sys.stderr)

    # sidechain pump on kicks, duck music under clip audio
    sc = np.ones(N)
    for k in kicks + impacts:
        i = int(k * SR)
        if i < N:
            sc[i:] = np.minimum(sc[i:], 1 - (0.55 if style == "energetic" else 0.3) * np.exp(-np.arange(N - i) / SR / 0.1))
    duck = np.ones(N)
    for q in cues:
        if q["type"] == "clip_audio":
            a, b = int(q["t"] * SR), int((q["t"] + float(q.get("dur", 5))) * SR)
            duck[max(0, a):min(N, b)] = 1 - float(q.get("duck", 0.7))
    duck = sg.filtfilt(*sg.butter(1, 4, fs=SR), duck) if len(duck) > 20 else duck
    music_mix = (bus["bass"] + bus["pad"]) * sc + bus["drums"]
    mix = music_mix * duck + bus["fx"] * (0.5 + 0.5 * duck) + bus["clip"]

    ir_t = np.arange(int(2.4 * SR)) / SR
    ir = lp(np.vstack([rs.standard_normal(len(ir_t)) * np.exp(-ir_t / 0.55) for _ in range(2)]), 6000)
    ir /= np.abs(ir).sum(axis=1, keepdims=True) ** 0.5 * 30
    mix = mix + 0.9 * np.vstack([sg.fftconvolve(bus["send"][c], ir[c])[:N] for c in range(2)])

    mix = hp(mix, 25)
    mix = mix / (np.abs(mix).max() + 1e-9)
    mix = np.tanh(2.0 * mix) / np.tanh(2.0)
    t = np.arange(N) / SR
    mix = mix * np.minimum(1, (DUR - t) / 0.45) * np.minimum(1, t / 0.01)
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.93
    out = os.path.join(project, "out", "score.wav")
    wavfile.write(out, SR, (mix.T * 32767).astype(np.int16))
    print(f"{out}  ({DUR:g}s, {BPM:g} BPM, music={music.get('mode', 'synth')}/{style}/{music.get('mood', 'dark')}, {len(cues)} cues)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    build(os.path.abspath(sys.argv[1]))
