#!/usr/bin/env python3
"""Builds four retro-tech backdrop scenes (SVG) for the backdrops mod.

  pixel-arcade   an original 8-bit space shooter on a CRT, with scanlines
  vaporwave      pastel twilight: a checkerboard, a retro window, a dolphin, a marble bust
  blueprint      technical drawings of a rocket and a robot on blue grid paper
  dos-prompt     a blue text-mode screen with ANSI-style block art and a prompt

Original art: the sprites, bust and drawings are drawn here, not taken from
any game or artwork. Vector only, drawn still, each subject in a side gutter
(.L / .R) beside the frosted conversation column.

Usage: python3 tools/build_tech.py hooks/scenes
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_travel import H, VEIL, W, lin, rad, rnd, svg  # noqa: E402
from smil import timeshift  # noqa: E402

GLOW = ('<filter id="glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="3" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
MONO = "'Courier New', 'DejaVu Sans Mono', Menlo, monospace"


def sprite(rows, x, y, px, color):
    """Pixel art from rows of '#' and '.', drawn as one path of px-sized squares."""
    d = []
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == "#":
                d.append(f"M{x + i * px} {y + j * px}h{px}v{px}h-{px}Z")
    return f'<path d="{"".join(d)}" fill="{color}"/>'


# --------------------------------------------------------------- pixel arcade
SHIP = [".....#.....", "....###....", "....###....", ".#..###..#.", ".#.#####.#.", "###########", "###.###.###", "#...#.#...#"]
SAUCER = ["....####....", "..########..", ".##.####.##.", "############", "..###..###..", ".##......##."]
DRONE = ["...######...", ".##########.", "##..####..##", "##..####..##", "############", ".#.#.##.#.#.", "#..........#"]
ROCK = ["..####..", ".######.", "###.####", "########", "####.###", ".######.", "..####.."]


def pixel_arcade():
    r = rnd(51)
    defs = (rad("crt", [(0, "#0b0b22"), (.7, "#05050f"), (1, "#000")], r_=.75)
            + rad("vig", [(.65, "#000", 0), (1, "#000", .55)])
            + '<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="2" fill="#000" opacity=".2"/></pattern>'
            + GLOW)
    starfield = "".join(f'<rect x="{r.randrange(0, 1600, 4)}" y="{r.randrange(0, 1000, 4)}" width="4" height="4" '
                        f'fill="{r.choice(["#ffffff", "#9ad1ff", "#ffd23d"])}" opacity="{r.uniform(.3, .9):.2f}"/>' for _ in range(160))
    px = 6
    formation = []
    for row in range(4):
        for col in range(5):
            x = 1150 + col * 84
            y = 140 + row * 70
            art, color = ((SAUCER, "#ff4d8b") if row % 2 == 0 else (DRONE, "#3de1ff"))
            formation.append(sprite(art, x, y, px, color))
    left_enemies = sprite(SAUCER, 120, 160, px, "#7dff6b") + sprite(DRONE, 260, 240, px, "#ffd23d")
    rocks = sprite(ROCK, 420, 520, 8, "#8a7a6a") + sprite(ROCK, 1500, 600, 6, "#8a7a6a")
    ship = sprite(SHIP, 180, 780, 10, "#e8f0ff") + '<rect x="230" y="860" width="10" height="20" fill="#ff8a3d" filter="url(#glow)"/>'
    shots = "".join(f'<rect x="234" y="{y}" width="4" height="22" fill="#fffb96" filter="url(#glow)"/>' for y in (700, 600, 500))
    enemy_shots = "".join(f'<rect x="{x}" y="{y}" width="4" height="14" fill="#ff4d4d" filter="url(#glow)"/>' for x, y in ((1230, 470), (1400, 560), (1314, 650)))
    boom = "".join(f'<rect x="{1440 + 24 * math.cos(a):.0f}" y="{430 + 24 * math.sin(a):.0f}" width="6" height="6" fill="{c}"/>'
                   for a, c in ((k * math.pi / 6, "#ffd23d" if k % 2 else "#ff8a3d") for k in range(12)))
    hud = (f'<g class="L"><text x="60" y="80" font-family="{MONO}" font-weight="700" font-size="28" fill="#ff4d4d">1UP</text>'
           f'<text x="140" y="80" font-family="{MONO}" font-weight="700" font-size="28" fill="#ffffff">004200</text>'
           f'<text x="60" y="960" font-family="{MONO}" font-weight="700" font-size="24" fill="#3de1ff">CREDIT 01</text>'
           + "".join(sprite(SHIP, 330 + k * 60, 930, 4, "#e8f0ff") for k in range(2)) + '</g>'
           f'<g class="R"><text x="1540" y="80" text-anchor="end" font-family="{MONO}" font-weight="700" font-size="28" fill="#ffd23d">HI 012000</text>'
           f'<text x="1540" y="960" text-anchor="end" font-family="{MONO}" font-weight="700" font-size="24" fill="#7dff6b">STAGE 07</text></g>')
    body = (f'<rect width="{W}" height="{H}" fill="url(#crt)"/>{starfield}'
            f'<g class="R">{"".join(formation)}{enemy_shots}{boom}{sprite(ROCK, 1500, 600, 6, "#8a7a6a")}</g>'
            f'<g class="L">{left_enemies}{ship}{shots}{sprite(ROCK, 420, 520, 8, "#8a7a6a")}</g>{hud}'
            f'<rect width="{W}" height="{H}" fill="url(#scan)"/><rect width="{W}" height="{H}" fill="url(#vig)"/>'
            f'<rect width="{W}" height="{H}" fill="url(#veil)" opacity=".25"/>')
    del rocks
    return svg(defs + VEIL, body, "", "An original 8-bit space shooter on a CRT screen with scanlines")


# ------------------------------------------------------------------- vaporwave
def vaporwave():
    """Pastel twilight vaporwave, deliberately unlike retro-80s: no sunset, no
    neon grid, no palm silhouettes. A dark checkerboard floor, dim clouds, a
    pastel planet, a retro program window, a leaping dolphin and a marble bust
    by a broken column."""
    r = rnd(52)
    horizon = 620
    defs = (lin("sky", [(0, "#140c30"), (.4, "#2e1f5c"), (.75, "#4a2f7a"), (1, "#1f4a66")])
            + lin("marble", [(0, "#efe4f7"), (.6, "#c9b8dc"), (1, "#8f7aaa")], x2=1, y2=.4)
            + lin("column", [(0, "#a898c0"), (.5, "#e2d6ee"), (1, "#7d6a98")], x2=1, y2=0)
            + lin("planet", [(0, "#ff9ad5"), (.55, "#c38bff"), (1, "#01cdfe")], x2=1, y2=1)
            + rad("rim", [(0, "#ff71ce", .3), (1, "#ff71ce", 0)])
            + lin("title", [(0, "#ff71ce"), (1, "#01cdfe")], x2=1, y2=0)
            + lin("dolphin", [(0, "#7ff0e0"), (1, "#3aa8d8")])
            + lin("haze", [(0, "#ffffff", 0), (1, "#ffffff", .55)])
            + '<filter id="cloud" x="-30%" y="-60%" width="160%" height="220%"><feGaussianBlur stdDeviation="16"/></filter>'
            + GLOW)
    clouds = "".join(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{r.uniform(90, 220):.0f}" ry="{r.uniform(28, 60):.0f}" '
                     f'fill="{r.choice(["#c8a6ff", "#ff9ad5", "#9fd8ff"])}" opacity="{r.uniform(.12, .28):.2f}" filter="url(#cloud)"/>'
                     for x, y in ((r.uniform(-100, 1700), r.uniform(60, 520)) for _ in range(16)))
    # a checkerboard floor in perspective, vanishing at the centre of the horizon
    tiles = []
    rows, cols = 12, 13
    ys = [horizon + (k / rows) ** 1.7 * (H - horizon) for k in range(rows + 1)]
    for k in range(rows):
        t0, t1 = (ys[k] - horizon) / (H - horizon), (ys[k + 1] - horizon) / (H - horizon)
        for j in range(-cols, cols):
            if (j + k) % 2:
                continue
            xa, xb = 800 + j * 150, 800 + (j + 1) * 150
            pts = [(800 + (xa - 800) * t0, ys[k]), (800 + (xb - 800) * t0, ys[k]),
                   (800 + (xb - 800) * t1, ys[k + 1]), (800 + (xa - 800) * t1, ys[k + 1])]
            tiles.append("M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts) + "Z")
    floor = (f'<rect y="{horizon}" width="{W}" height="{H - horizon}" fill="#3a2766"/>'
             f'<path d="{" ".join(tiles)}" fill="#120a26"/>'
             f'<path d="M0 {horizon} H{W}" stroke="#ff71ce" stroke-width="2" opacity=".55"/>'
             f'<rect y="{horizon}" width="{W}" height="70" fill="url(#haze)" opacity=".35" transform="rotate(180 800 {horizon + 35})"/>')
    # a retro program window, left
    wx, wy, ww, wh = 70, 170, 360, 230
    window = (f'<g class="L"><rect x="{wx + 10}" y="{wy + 10}" width="{ww}" height="{wh}" fill="#5a3a8a" opacity=".35"/>'
              f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" fill="#ddd0f2" stroke="#5a3a8a" stroke-width="2"/>'
              f'<rect x="{wx + 3}" y="{wy + 3}" width="{ww - 6}" height="30" fill="url(#title)"/>'
              f'<text x="{wx + 14}" y="{wy + 24}" font-family="{MONO}" font-size="17" font-weight="700" fill="#fff">ａｅｓｔｈｅｔｉｃ.ｅｘｅ</text>'
              + "".join(f'<rect x="{wx + ww - 30 - i * 26}" y="{wy + 9}" width="20" height="18" fill="#efe6ff" stroke="#5a3a8a"/>' for i in range(3))
              + f'<path d="M{wx + ww - 26} {wy + 13} l12 10 M{wx + ww - 14} {wy + 13} l-12 10" stroke="#5a3a8a" stroke-width="2"/>'
              f'<text x="{wx + ww / 2}" y="{wy + 86}" text-anchor="middle" font-family="{MONO}" font-size="20" fill="#5a3a8a">ｌｏａｄｉｎｇ ｖｉｂｅｓ…</text>'
              f'<rect x="{wx + 30}" y="{wy + 110}" width="{ww - 60}" height="30" fill="#fff" stroke="#5a3a8a" stroke-width="2"/>'
              + "".join(f'<rect x="{wx + 36 + i * 22}" y="{wy + 116}" width="18" height="18" fill="{c}"/>'
                        for i, c in enumerate(["#ff71ce", "#ff8ad8", "#c38bff", "#b967ff", "#8fb0ff", "#01cdfe", "#05ffa1", "#7dffcf", "#fffb96", "#ffd3a8", "#ff9ad5"]))
              + f'<text x="{wx + ww / 2}" y="{wy + 178}" text-anchor="middle" font-family="{MONO}" font-size="16" fill="#7a5ab8">７３％  ・  ｐｌｅａｓｅ ｗａｉｔ</text>'
              f'<rect x="{wx + ww / 2 - 50}" y="{wy + 192}" width="100" height="28" fill="#efe6ff" stroke="#5a3a8a" stroke-width="2"/>'
              f'<text x="{wx + ww / 2}" y="{wy + 212}" text-anchor="middle" font-family="{MONO}" font-size="16" fill="#5a3a8a">ＯＫ</text>'
              f'<path d="M{wx + 250} {wy + 200} l0 34 l9 -8 l7 15 l6 -3 l-7 -14 l12 -1Z" fill="#fff" stroke="#000" stroke-width="2"/></g>')
    # an original leaping dolphin, left, over a strip of water
    dolphin = ('<g class="L"><g transform="translate(250 560) rotate(-24)">'
               '<path d="M-110 10 C-70 -40 30 -52 100 -20 C120 -10 132 0 140 8 C120 6 104 6 92 10 C40 30 -40 32 -110 10Z" fill="url(#dolphin)"/>'
               '<path d="M10 -40 L30 -78 L44 -36Z" fill="#3aa8d8"/>'
               '<path d="M-104 8 L-150 -22 L-140 10 L-152 38Z" fill="#3aa8d8"/>'
               '<path d="M20 18 L40 46 L56 14Z" fill="#3aa8d8"/>'
               '<circle cx="104" cy="-8" r="4" fill="#123"/></g>'
               '<path d="M60 640 q40 -30 80 0 q40 -30 80 0 q40 -30 80 0 q40 -30 80 0" stroke="#fff" stroke-width="4" fill="none" opacity=".8"/></g>')
    # a broken Greek column and the marble bust, right
    head = ("M-130 0 C-130 -60 -90 -95 -45 -105 L-40 -150 L-62 -165 L-66 -182 L-72 -192 L-88 -205 L-70 -230 L-68 -250 "
            "C-60 -300 20 -312 42 -270 C72 -230 62 -180 30 -160 L25 -110 C80 -100 130 -60 130 0Z")
    curls = "".join(f'<circle cx="{-24 + i * 15 + (6 if j % 2 else 0)}" cy="{-286 + j * 18 + i * 4}" r="10" fill="url(#marble)" stroke="#cdbbd6" stroke-width="1.5"/>'
                    for i in range(5) for j in range(3) if not (j == 0 and i == 0))
    ruin = ('<rect x="1150" y="430" width="80" height="400" fill="url(#column)"/>'
            '<path d="M1150 430 L1170 412 L1190 426 L1206 404 L1230 430Z" fill="url(#column)"/>'
            + "".join(f'<path d="M{1160 + i * 15} 440 V826" stroke="#b8a6c9" stroke-width="3" opacity=".6"/>' for i in range(5))
            + '<rect x="1136" y="826" width="108" height="24" fill="url(#column)"/>')
    bust = (f'<g transform="translate(1400 470) scale(1.2)">'
            '<rect x="-95" y="0" width="190" height="34" fill="url(#column)"/>'
            '<rect x="-75" y="34" width="150" height="300" fill="url(#column)"/>'
            + "".join(f'<path d="M{-60 + i * 24} 40 V330" stroke="#b8a6c9" stroke-width="3" opacity=".6"/>' for i in range(6))
            + f'<path d="{head}" fill="url(#marble)"/>{curls}'
            '<path d="M-62 -228 q8 -5 14 0" stroke="#8a7a9a" stroke-width="3" fill="none"/>'
            '<ellipse cx="6" cy="-200" rx="12" ry="18" fill="#e9dcef" stroke="#cdbbd6" stroke-width="2"/>'
            '<path d="M-20 -120 q30 30 10 70 M60 -40 q-20 -20 -40 -10" stroke="#d9c6e2" stroke-width="2" fill="none" opacity=".8"/>'
            '<rect x="-88" y="-240" width="62" height="20" rx="4" fill="#ff71ce" opacity=".92"/>'
            '<path d="M-26 -232 L10 -228" stroke="#ff71ce" stroke-width="4"/></g>')
    shapes = ('<path d="M1220 200 L1270 120 L1320 200Z M1270 120 L1284 214" stroke="#ff71ce" stroke-width="3" fill="none"/>'
              '<rect x="1490" y="150" width="70" height="70" fill="none" stroke="#01cdfe" stroke-width="3" transform="rotate(20 1525 185)"/>'
              '<rect x="1505" y="165" width="70" height="70" fill="none" stroke="#01cdfe" stroke-width="3" opacity=".6" transform="rotate(20 1540 200)"/>')
    text = "".join(f'<text x="1575" y="{330 + i * 40}" font-size="30" text-anchor="middle" fill="#ffffff" '
                   f'font-family="sans-serif" opacity=".9">{ch}</text>' for i, ch in enumerate("ヴェイパーウェイヴ"))
    planet = ('<circle cx="1330" cy="250" r="230" fill="url(#rim)"/>'
              '<circle cx="1330" cy="250" r="150" fill="url(#planet)" opacity=".55"/>')
    right = f'<g class="R">{planet}{ruin}{shapes}{bust}{text}</g>'
    twinkles = "".join(f'<circle cx="{r.uniform(0, 1600):.0f}" cy="{r.uniform(0, 520):.0f}" r="{r.uniform(.6, 1.6):.1f}" fill="#fff" opacity="{r.uniform(.4, .9):.2f}"/>'
                       for _ in range(90))
    body = (f'<rect width="{W}" height="{H}" fill="url(#sky)"/>{twinkles}{clouds}{floor}{window}{dolphin}{right}'
            f'<rect width="{W}" height="{H}" fill="url(#veil)" opacity=".55"/>')
    return svg(defs + VEIL, body, "", "Pastel twilight vaporwave: a checkerboard floor, a retro program window, a leaping dolphin and a marble bust")


# ------------------------------------------------------------------- blueprint
def blueprint():
    defs = (lin("paper", [(0, "#0b3d91"), (1, "#082c6b")])
            + '<pattern id="minor" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0H0V20" fill="none" stroke="#fff" stroke-opacity=".08"/></pattern>'
            + '<pattern id="major" width="100" height="100" patternUnits="userSpaceOnUse"><path d="M100 0H0V100" fill="none" stroke="#fff" stroke-opacity=".18" stroke-width="1.5"/></pattern>'
            + '<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
              '<path d="M0 0 L10 5 L0 10Z" fill="#fff"/></marker>')
    ink = 'stroke="#fff" stroke-width="2.4" fill="none"'
    thin = 'stroke="#fff" stroke-width="1.2" fill="none" opacity=".85"'

    def label(x, y, t, size=16, anchor="middle"):
        return f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" fill="#fff" text-anchor="{anchor}">{t}</text>'

    def dim_h(x1, x2, y, t):
        return (f'<path d="M{x1} {y} H{x2}" {thin} marker-start="url(#arr)" marker-end="url(#arr)"/>'
                f'<path d="M{x1} {y - 10} V{y + 10} M{x2} {y - 10} V{y + 10}" {thin}/>' + label((x1 + x2) / 2, y - 8, t, 14))

    def dim_v(x, y1, y2, t):
        return (f'<path d="M{x} {y1} V{y2}" {thin} marker-start="url(#arr)" marker-end="url(#arr)"/>'
                f'<path d="M{x - 10} {y1} H{x + 10} M{x - 10} {y2} H{x + 10}" {thin}/>'
                f'<text x="{x - 10}" y="{(y1 + y2) / 2}" font-family="{MONO}" font-size="14" fill="#fff" text-anchor="middle" '
                f'transform="rotate(-90 {x - 10} {(y1 + y2) / 2})">{t}</text>')

    cx = 1360
    rocket = (f'<path d="M{cx} 110 C{cx + 40} 160 {cx + 52} 220 {cx + 52} 260 V600 H{cx - 52} V260 C{cx - 52} 220 {cx - 40} 160 {cx} 110Z" {ink}/>'
              f'<path d="M{cx - 52} 260 H{cx + 52} M{cx - 52} 470 H{cx + 52}" {thin}/>'
              f'<circle cx="{cx}" cy="330" r="26" {ink}/><circle cx="{cx}" cy="330" r="16" {thin}/>'
              f'<path d="M{cx - 52} 500 L{cx - 110} 610 V640 L{cx - 52} 600Z M{cx + 52} 500 L{cx + 110} 610 V640 L{cx + 52} 600Z" {ink}/>'
              f'<path d="M{cx - 30} 600 L{cx - 42} 650 H{cx + 42} L{cx + 30} 600" {ink}/>'
              f'<path d="M{cx} 80 V680" stroke="#fff" stroke-width="1" stroke-dasharray="14 6 3 6" opacity=".7"/>'
              + dim_v(cx - 170, 110, 650, "5400") + dim_h(cx - 52, cx + 52, 700, "Ø 1040")
              + dim_h(cx - 110, cx + 110, 740, "2200")
              + f'<path d="M{cx + 26} 330 L{cx + 120} 290 H{cx + 210}" {thin}/>' + label(cx + 130, 284, "PORT A", 13, "start")
              + label(cx, 790, "ELEVATION A", 18))
    rx = 230
    robot = (f'<rect x="{rx - 70}" y="160" width="140" height="110" rx="10" {ink}/>'
             f'<circle cx="{rx - 30}" cy="210" r="16" {ink}/><circle cx="{rx + 30}" cy="210" r="16" {ink}/>'
             f'<path d="M{rx - 30} 248 H{rx + 30}" {ink}/><path d="M{rx} 160 V120" {ink}/><circle cx="{rx}" cy="112" r="8" {ink}/>'
             f'<rect x="{rx - 22}" y="270" width="44" height="22" {ink}/>'
             f'<rect x="{rx - 100}" y="292" width="200" height="200" rx="12" {ink}/>'
             f'<rect x="{rx - 50}" y="330" width="100" height="70" rx="6" {thin}/>'
             + "".join(f'<circle cx="{rx - 30 + i * 30}" cy="440" r="9" {thin}/>' for i in range(3))
             + f'<path d="M{rx - 100} 310 L{rx - 160} 400 L{rx - 140} 480 M{rx + 100} 310 L{rx + 160} 400 L{rx + 140} 480" {ink}/>'
             f'<circle cx="{rx - 140}" cy="490" r="14" {ink}/><circle cx="{rx + 140}" cy="490" r="14" {ink}/>'
             f'<rect x="{rx - 70}" y="492" width="50" height="150" {ink}/><rect x="{rx + 20}" y="492" width="50" height="150" {ink}/>'
             f'<rect x="{rx - 84}" y="642" width="78" height="26" rx="6" {ink}/><rect x="{rx + 6}" y="642" width="78" height="26" rx="6" {ink}/>'
             + dim_v(rx - 200, 112, 668, "1780") + dim_h(rx - 100, rx + 100, 710, "640")
             + label(rx, 760, "FRONT VIEW", 18))
    block = ('<g class="R"><rect x="1200" y="820" width="360" height="110" {0}/>'
             '<path d="M1200 856 H1560 M1200 892 H1560 M1380 856 V930" {1}/>'.format(ink, thin)
             + label(1380, 846, "PROJECT  BACKDROPS", 16)
             + label(1290, 880, "SCALE 1:20", 14) + label(1470, 880, "SHEET 1 / 1", 14)
             + label(1290, 916, "DWG CC-0042", 14) + label(1470, 916, "REV B", 14) + '</g>')
    body = (f'<rect width="{W}" height="{H}" fill="url(#paper)"/><rect width="{W}" height="{H}" fill="url(#minor)"/>'
            f'<rect width="{W}" height="{H}" fill="url(#major)"/><g class="R">{rocket}</g><g class="L">{robot}</g>{block}'
            f'<rect width="{W}" height="{H}" fill="url(#veil)" opacity=".35"/>')
    return svg(defs + VEIL, body, "", "Technical drawings of a rocket and a robot on blue blueprint grid paper")


# ------------------------------------------------------------------ dos prompt
CGA = {"k": "#000000", "b": "#0000aa", "g": "#00aa00", "c": "#00aaaa", "r": "#aa0000", "m": "#aa00aa", "n": "#aa5500",
       "w": "#aaaaaa", "K": "#555555", "B": "#5555ff", "G": "#55ff55", "C": "#55ffff", "R": "#ff5555", "M": "#ff55ff",
       "y": "#ffff55", "W": "#ffffff"}


def ansi_art(cols, rows):
    """A sunset island in 16 colours: one CGA letter per cell, dithered like block shading."""
    grid = []
    for j in range(rows):
        line = []
        for i in range(cols):
            t = j / rows
            checker = (i + j) % 2
            dx, dy = i - cols * .62, (j - rows * .48) * 1.9
            if dx * dx + dy * dy < 22:
                ch = "y" if dx * dx + dy * dy < 12 else ("y" if checker else "R")
            elif t < .3:
                ch = "b" if not checker or t < .15 else "m"
            elif t < .5:
                ch = "m" if checker else ("M" if t > .42 else "r")
            elif t < .56:
                ch = "R" if checker else "y"
            else:
                ch = "c" if (checker and t < .8) else "b"
                if abs(i - cols * .62) < 3 - (t - .56) * 6 and t < .8:
                    ch = "y" if checker else "c"
            # island and palm
            if t > .7 and abs(i - cols * .28) < (8 - (t - .7) * 10):
                ch = "n" if checker else "y"
            if abs(i - (cols * .28 + (j - rows * .3) * .25)) < 1 and rows * .3 < j < rows * .72:
                ch = "n"
            if rows * .22 < j < rows * .36 and abs(i - cols * .28) < 6 - abs(j - rows * .29) * 1.1:
                ch = "g" if checker else "G"
            line.append(ch)
        grid.append(line)
    return grid


def dos_prompt():
    cell_w, cell_h = 12, 20
    defs = ""
    art = ansi_art(30, 26)
    ax, ay = 46, 150
    cells = []
    for j, line in enumerate(art):
        for i, ch in enumerate(line):
            cells.append(f'<rect x="{ax + i * cell_w}" y="{ay + j * cell_h}" width="{cell_w}" height="{cell_h}" fill="{CGA[ch]}"/>')

    def box(x, y, w, h, color, title):
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{color}" stroke-width="2"/>'
                f'<rect x="{x + 6}" y="{y + 6}" width="{w - 12}" height="{h - 12}" fill="none" stroke="{color}" stroke-width="2"/>'
                f'<rect x="{x + w / 2 - len(title) * 6.5 - 8}" y="{y - 10}" width="{len(title) * 13 + 16}" height="20" fill="#0000aa"/>'
                f'<text x="{x + w / 2}" y="{y + 6}" text-anchor="middle" font-family="{MONO}" font-weight="700" font-size="20" fill="{color}">{title}</text>')

    left = (f'<g class="L">{box(ax - 22, ay - 30, 30 * cell_w + 44, 26 * cell_h + 56, CGA["C"], "SUNSET.ANS")}'
            f'{"".join(cells)}'
            f'<text x="{ax}" y="{ay + 26 * cell_h + 60}" font-family="{MONO}" font-size="18" fill="{CGA["w"]}">80x25  16 colors  4K</text></g>')
    lines = [(CGA["w"], "C:\\>cd projects"), (CGA["w"], "C:\\PROJECTS>dir /w"), (CGA["C"], "[BACKDROPS]  [NOTES]"),
             (CGA["C"], "README.TXT   TODO.TXT"), (CGA["w"], ""), (CGA["w"], "C:\\PROJECTS>claude"),
             (CGA["y"], "Welcome to Claude Code"), (CGA["w"], ""), (CGA["w"], "C:\\PROJECTS>")]
    px, py, pw, ph = 1150, 150, 410, 330
    prompt = (f'<g class="R"><rect x="{px + 10}" y="{py + 10}" width="{pw}" height="{ph}" fill="#000"/>'
              f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="#0000aa"/>{box(px, py, pw, ph, CGA["W"], "COMMAND")}'
              + "".join(f'<text x="{px + 28}" y="{py + 52 + i * 30}" font-family="{MONO}" font-size="19" font-weight="700" fill="{c}">{t}</text>'
                        for i, (c, t) in enumerate(lines))
              + f'<rect x="{px + 28 + 12 * 11.4:.0f}" y="{py + 52 + 8 * 30 - 4}" width="12" height="4" fill="{CGA["W"]}"/>'
              f'<rect x="{px}" y="{py + ph + 50}" width="{pw}" height="120" fill="#aaaaaa"/>'
              f'<rect x="{px + 10}" y="{py + ph + 170}" width="{pw}" height="10" fill="#000"/><rect x="{px + pw}" y="{py + ph + 60}" width="10" height="120" fill="#000"/>'
              + f'<text x="{px + pw / 2}" y="{py + ph + 90}" text-anchor="middle" font-family="{MONO}" font-size="19" font-weight="700" fill="#000">Ready to code?</text>'
              f'<rect x="{px + 70}" y="{py + ph + 110}" width="110" height="34" fill="#00aa00"/>'
              f'<text x="{px + 125}" y="{py + ph + 133}" text-anchor="middle" font-family="{MONO}" font-size="18" font-weight="700" fill="#ffffff">  OK  </text>'
              f'<rect x="{px + 230}" y="{py + ph + 110}" width="110" height="34" fill="#0000aa"/>'
              f'<text x="{px + 285}" y="{py + ph + 133}" text-anchor="middle" font-family="{MONO}" font-size="18" font-weight="700" fill="#ffffff">Cancel</text>'
              '</g>')
    body = f'<rect width="{W}" height="{H}" fill="#0000aa"/>{left}{prompt}'
    return svg(defs, body, "", "A blue text-mode screen with ANSI-style block art of a sunset island and a DOS-style prompt")


SCENES = {
    "pixel-arcade": pixel_arcade,
    "vaporwave": vaporwave,
    "blueprint": blueprint,
    "dos-prompt": dos_prompt,
}

if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    out.mkdir(parents=True, exist_ok=True)
    for name, make in SCENES.items():
        s = timeshift(make())
        (out / f"{name}.svg").write_text(s)
        const = name.replace("-", "_").upper()
        escaped = s.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
        (out / f"{name}.ts").write_text(
            "// Generated by tools/build_tech.py: edit that file, not this one.\n"
            f"export const {const} = `{escaped}`\n")
        print(f"{name}: {len(s)} chars")
