#!/usr/bin/env python3
"""Builds the three Christmas backdrop scenes (SVG) for the backdrops mod.

  christmas-fireplace   a cosy room: a fire with stockings, a decorated tree and presents
  christmas-village     a snowy village at night, string lights, a sleigh across the moon
  christmas-snowglobe   a snow globe with a little house and tree, bokeh lights, ornaments

Vector only, drawn still (the desktop app paints backdrops as still frames),
with each subject in a side gutter beside the frosted conversation column.
Shares its helpers with build_travel.py.

Usage: python3 tools/build_christmas.py hooks/scenes
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_travel import H, VEIL, W, lin, rad, rnd, stars, svg  # noqa: E402
from smil import timeshift  # noqa: E402

GLOW = ('<filter id="glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="4" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        '<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="10"/></filter>')
BULBS = ["#ff4d4d", "#ffd23d", "#43d17a", "#4da3ff", "#ff8ad8", "#ffffff"]


def tree(cx, base, h, r, star=True, lights=True, ornaments=True, scale_w=1.0):
    """A decorated fir: four tiers, ornaments, string lights and a star."""
    out = [f'<rect x="{cx - 16}" y="{base - 30}" width="32" height="44" fill="#4a2c1a"/>']
    tiers = 4
    for i in range(tiers):
        top = base - h + i * h * .2
        bottom = base - h * .62 + i * h * .2 + h * .1
        half = (h * .2 + i * h * .12) * scale_w
        out.append(f'<path d="M{cx} {top:.0f} L{cx + half:.0f} {bottom:.0f} Q{cx} {bottom + 22:.0f} {cx - half:.0f} {bottom:.0f}Z" fill="url(#fir)"/>'
                   f'<path d="M{cx} {top:.0f} L{cx - half:.0f} {bottom:.0f} Q{cx - half * .4:.0f} {bottom + 10:.0f} {cx} {bottom + 14:.0f}Z" fill="#0d3b22" opacity=".45"/>')
    if lights:
        for k in range(5):
            y0 = base - h * .8 + k * h * .17
            half = (h * .08 + k * h * .095) * scale_w
            pts = []
            for j in range(9):
                t = j / 8
                x = cx - half + 2 * half * t
                y = y0 + 26 * t + 10 * math.sin(t * math.pi)
                pts.append((x, y))
            out.append('<path d="M' + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts) + '" stroke="#2c3a2c" stroke-width="1.5" fill="none"/>')
            for j, (x, y) in enumerate(pts[1:-1]):
                out.append(f'<circle cx="{x:.0f}" cy="{y + 3:.0f}" r="4" fill="{BULBS[(j + k) % len(BULBS)]}" filter="url(#glow)" class="tw{1 + (j + k) % 4}"/>')
    if ornaments:
        for _ in range(16):
            yy = r.uniform(base - h * .75, base - h * .12)
            frac = (yy - (base - h)) / h
            half = (h * .06 + frac * h * .4) * scale_w
            xx = cx + r.uniform(-half * .8, half * .8)
            c = r.choice(["#d92e2e", "#e8b04a", "#2f6fd8", "#c0c4cc", "#8a2be2"])
            rr = r.uniform(7, 11)
            out.append(f'<circle cx="{xx:.0f}" cy="{yy:.0f}" r="{rr:.0f}" fill="{c}"/>'
                       f'<circle cx="{xx - rr * .35:.0f}" cy="{yy - rr * .35:.0f}" r="{rr * .3:.1f}" fill="#fff" opacity=".7"/>')
    if star:
        sy = base - h - 4
        pts = []
        for k in range(10):
            a = -math.pi / 2 + k * math.pi / 5
            rad_ = 26 if k % 2 == 0 else 11
            pts.append((cx + rad_ * math.cos(a), sy + rad_ * math.sin(a)))
        out.append(f'<circle cx="{cx}" cy="{sy}" r="40" fill="url(#starGlow)"/>'
                   '<path d="M' + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + 'Z" fill="#ffd23d" stroke="#fff3b0" stroke-width="1.5"/>')
    return "".join(out)


def present(x, y, w, h, box, ribbon):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{box}"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#shade)"/>'
            f'<rect x="{x + w / 2 - 5}" y="{y}" width="10" height="{h}" fill="{ribbon}"/>'
            f'<rect x="{x}" y="{y + h / 2 - 5}" width="{w}" height="10" fill="{ribbon}"/>'
            f'<path d="M{x + w / 2} {y} q-22 -22 -26 -4 q4 10 26 4 q22 6 26 -4 q-4 -18 -26 4Z" fill="{ribbon}"/>')


COMMON = (lin("fir", [(0, "#2f8a4c"), (1, "#145a2e")])
          + rad("starGlow", [(0, "#fff3b0", .9), (1, "#ffd23d", 0)])
          + lin("shade", [(0, "#fff", .18), (.5, "#fff", 0), (1, "#000", .25)])
          + GLOW)


# ------------------------------------------------------------------ fireplace
def christmas_fireplace():
    r = rnd(21)
    defs = (COMMON
            + lin("wall", [(0, "#2a0d10"), (1, "#3d1418")])
            + '<pattern id="damask" width="60" height="60" patternUnits="userSpaceOnUse">'
              '<path d="M30 10 q10 10 0 20 q-10 -10 0 -20Z M0 40 q10 10 0 20 q-10 -10 0 -20Z M60 40 q10 10 0 20 q-10 -10 0 -20Z" '
              'fill="#5a1d22" opacity=".45"/></pattern>'
            + lin("floor", [(0, "#4a2a18"), (1, "#24130a")])
            + lin("brick", [(0, "#7a3b2a"), (1, "#5a2a1d")])
            + rad("fireGlow", [(0, "#ffb347", .75), (.5, "#ff7a1a", .25), (1, "#ff7a1a", 0)])
            + lin("flame", [(0, "#fff3b0"), (.35, "#ffd23d"), (.7, "#ff8a1a"), (1, "#d9361a")])
            + rad("roomGlow", [(0, "#ff9a3c", .22), (1, "#ff9a3c", 0)]))
    floor = ('<rect y="840" width="1600" height="160" fill="url(#floor)"/>'
             + "".join(f'<path d="M0 {840 + i * 34} H1600" stroke="#1a0d06" stroke-width="2" opacity=".6"/>' for i in range(5)))
    # fireplace on the left
    fx, fy, fw, fh = 50, 470, 400, 380
    bricks = "".join(f'<rect x="{fx + 14 + (j * 48) + (i % 2) * 24}" y="{fy + 70 + i * 26}" width="44" height="22" fill="url(#brick)" opacity=".9"/>'
                     for i in range(11) for j in range(7) if fx + 14 + j * 48 + (i % 2) * 24 + 44 < fx + fw - 10)
    flames = "".join(
        f'<path d="M{cx} 820 C{cx - w} 790 {cx - w * .5} {760 - h * .4:.0f} {cx} {820 - h} C{cx + w * .5} {760 - h * .4:.0f} {cx + w} 790 {cx} 820Z" '
        f'fill="url(#flame)" opacity="{o}"/>'
        for cx, w, h, o in ((210, 50, 120, .95), (250, 40, 150, 1), (290, 48, 110, .95), (180, 30, 80, .8), (320, 30, 85, .8)))
    stockings = "".join(
        f'<g transform="translate({x} {fy + 46})"><path d="M0 0 h40 v70 q0 14 14 20 l22 8 q12 6 4 20 q-10 12 -40 -2 l-30 -16 q-10 -6 -10 -20Z" fill="{c}"/>'
        f'<rect x="-4" y="-6" width="48" height="20" rx="6" fill="#f4f1ea"/></g>'
        for x, c in ((fx + 50, "#c62828"), (fx + 170, "#1f7a3e"), (fx + 290, "#c62828")))
    garland = ('<path d="M{0} {1} q100 30 200 0 q100 30 200 0" stroke="#1f5a2e" stroke-width="14" fill="none"/>'.format(fx, fy + 36)
               + "".join(f'<circle cx="{fx + 20 + i * 38}" cy="{fy + 44 + 12 * math.sin(i / 10.5 * math.pi * 2) ** 2:.0f}" r="4" '
                         f'fill="{BULBS[i % len(BULBS)]}" filter="url(#glow)" class="tw{1 + i % 4}"/>' for i in range(11)))
    candles = "".join(f'<rect x="{x}" y="{fy - 50}" width="16" height="50" fill="#f4f1ea"/>'
                      f'<path d="M{x + 8} {fy - 70} q8 10 0 18 q-8 -8 0 -18Z" fill="#ffd23d" filter="url(#glow)"/>' for x in (fx + 40, fx + 340))
    fireplace = ('<g class="L">'
                 f'<circle cx="{fx + fw / 2}" cy="760" r="320" fill="url(#roomGlow)"/>'
                 f'<rect x="{fx}" y="{fy + 50}" width="{fw}" height="{fh - 50}" fill="#4a2018"/>{bricks}'
                 f'<rect x="{fx - 30}" y="{fy}" width="{fw + 60}" height="56" rx="6" fill="#6b4a32"/>'
                 f'<rect x="{fx - 30}" y="{fy + 44}" width="{fw + 60}" height="12" fill="#3a2414"/>'
                 f'<path d="M{fx + 70} {fy + fh} V{fy + 170} Q{fx + fw / 2} {fy + 110} {fx + fw - 70} {fy + 170} V{fy + fh}Z" fill="#120806"/>'
                 f'<ellipse cx="{fx + fw / 2}" cy="800" rx="150" ry="90" fill="url(#fireGlow)"/>'
                 f'{flames}<rect x="{fx + 110}" y="818" width="180" height="22" rx="10" fill="#5a3418"/>'
                 f'<rect x="{fx + 130}" y="806" width="150" height="18" rx="9" fill="#6e4220" transform="rotate(-6 {fx + 200} 815)"/>'
                 f'{garland}{stockings}{candles}</g>')
    presents = (present(1170, 790, 90, 60, "#c62828", "#ffd23d") + present(1270, 805, 70, 45, "#2f6fd8", "#f4f1ea")
                + present(1440, 780, 100, 70, "#1f7a3e", "#e8b04a") + present(1350, 815, 60, 35, "#e8b04a", "#c62828"))
    tree_g = f'<g class="R"><circle cx="1360" cy="520" r="360" fill="url(#roomGlow)"/>{tree(1360, 820, 600, r, scale_w=.62)}{presents}</g>'
    body = (f'<rect width="{W}" height="{H}" fill="url(#wall)"/><rect width="{W}" height="{H}" fill="url(#damask)"/>'
            f'{floor}{fireplace}{tree_g}<rect width="{W}" height="{H}" fill="url(#veil)" opacity=".7"/>')
    return svg(defs + VEIL, body, "", "A cosy room with a crackling fire, stockings, a decorated Christmas tree and presents")


# -------------------------------------------------------------------- village
def christmas_village():
    r = rnd(22)
    defs = (COMMON
            + lin("sky", [(0, "#040a20"), (.6, "#0f2550"), (1, "#24477a")])
            + rad("moon", [(0, "#fffbe8"), (.5, "#fff3c4", .45), (1, "#fff3c4", 0)])
            + lin("snow", [(0, "#f4f8ff"), (1, "#b9cbe6")])
            + lin("wallA", [(0, "#8a5a3c"), (1, "#5e3b26")])
            + lin("wallB", [(0, "#a33a2e"), (1, "#6e2219")]))

    def house(x, base, w, h, wall, door=True):
        roof_h = w * .55
        out = [f'<rect x="{x}" y="{base - h}" width="{w}" height="{h}" fill="url(#{wall})"/>',
               f'<path d="M{x - 14} {base - h + 4} L{x + w / 2} {base - h - roof_h} L{x + w + 14} {base - h + 4}Z" fill="url(#snow)"/>',
               f'<path d="M{x - 14} {base - h + 4} L{x + w / 2} {base - h - roof_h} L{x + w + 14} {base - h + 4} L{x + w + 6} {base - h + 14} '
               f'L{x + w / 2} {base - h - roof_h + 12} L{x - 6} {base - h + 14}Z" fill="#3a2a2a"/>']
        for i in range(2):
            wx = x + w * (.18 + i * .46)
            out.append(f'<rect x="{wx:.0f}" y="{base - h * .7:.0f}" width="{w * .2:.0f}" height="{w * .2:.0f}" fill="#ffc46b" filter="url(#glow)"/>'
                       f'<path d="M{wx + w * .1:.0f} {base - h * .7:.0f} v{w * .2:.0f} M{wx:.0f} {base - h * .7 + w * .1:.0f} h{w * .2:.0f}" stroke="#5e3b26" stroke-width="2"/>')
        if door:
            out.append(f'<rect x="{x + w * .42:.0f}" y="{base - h * .42:.0f}" width="{w * .16:.0f}" height="{h * .42:.0f}" fill="#3a2414"/>'
                       f'<circle cx="{x + w / 2:.0f}" cy="{base - h * .52:.0f}" r="8" fill="none" stroke="#1f7a3e" stroke-width="4"/>')
        # string lights along the eave
        for j in range(9):
            t = j / 8
            lx = x - 8 + (w + 16) * t
            ly = base - h + 10 + 6 * math.sin(t * math.pi)
            out.append(f'<circle cx="{lx:.0f}" cy="{ly:.0f}" r="3.5" fill="{BULBS[j % len(BULBS)]}" filter="url(#glow)" class="tw{1 + j % 4}"/>')
        return "".join(out)

    def fir(x, base, s):
        return (f'<path d="M{x} {base - 120 * s:.0f} L{x + 40 * s:.0f} {base - 40 * s:.0f} L{x + 18 * s:.0f} {base - 42 * s:.0f} '
                f'L{x + 52 * s:.0f} {base} L{x - 52 * s:.0f} {base} L{x - 18 * s:.0f} {base - 42 * s:.0f} L{x - 40 * s:.0f} {base - 40 * s:.0f}Z" fill="#163a2a"/>'
                f'<path d="M{x} {base - 120 * s:.0f} L{x + 16 * s:.0f} {base - 92 * s:.0f} L{x - 16 * s:.0f} {base - 92 * s:.0f}Z" fill="#f4f8ff"/>')

    left = ('<g class="L">'
            + house(40, 840, 150, 120, "wallA") + house(230, 860, 120, 100, "wallB")
            # a little church with a steeple
            + '<rect x="380" y="690" width="110" height="170" fill="url(#wallA)"/>'
            '<path d="M372 694 L435 610 L498 694Z" fill="url(#snow)"/><rect x="418" y="520" width="34" height="100" fill="url(#wallA)"/>'
            '<path d="M412 524 L435 470 L458 524Z" fill="url(#snow)"/><path d="M435 450 V475 M426 460 H444" stroke="#e8b04a" stroke-width="4"/>'
            '<path d="M420 860 V780 Q435 760 450 780 V860Z" fill="#ffc46b" filter="url(#glow)"/>'
            + fir(20, 900, 1.1) + fir(560, 900, .9) + '</g>')
    right = ('<g class="R">'
             + house(1180, 850, 130, 110, "wallB") + house(1400, 840, 160, 125, "wallA")
             + tree(1340, 880, 210, r, ornaments=False)
             + fir(1580, 910, 1.0) + fir(1120, 905, .8) + '</g>')
    # sleigh and reindeer crossing the moon
    def deer(x, y):
        return (f'<path d="M{x} {y} q14 -8 30 -2 l8 -14 l4 2 l-6 14 q6 4 2 10 l-6 18 h-4 l3 -16 h-20 l-4 16 h-4 l2 -18 q-8 -4 -5 -10Z" fill="#0b1426"/>'
                f'<path d="M{x + 38} {y - 16} l-4 -10 l-6 -2 M{x + 38} {y - 16} l4 -10 l6 -2" stroke="#0b1426" stroke-width="2.5" fill="none"/>')
    sleigh = ('<g class="R" transform="translate(-60 0)">'
              + "".join(deer(1150 + i * 58, 205 - i * 10) for i in range(4))
              + '<path d="M1150 215 L1100 228" stroke="#0b1426" stroke-width="1.5"/>'
              '<path d="M1030 222 h70 q16 0 16 -18 v-10 h-14 v8 h-60 q-20 -8 -26 -26 h-10 q2 30 24 46Z M1024 236 h86 q16 0 20 -12" '
              'fill="#0b1426" stroke="#0b1426" stroke-width="3"/><circle cx="1060" cy="190" r="12" fill="#0b1426"/>'
              '<path d="M1048 196 q12 -26 26 0Z" fill="#0b1426"/></g>')
    snow_ground = ('<path d="M0 820 C300 790 600 810 800 830 C1000 850 1300 800 1600 820 V1000 H0Z" fill="url(#snow)"/>'
                   + "".join(f'<circle cx="{r.uniform(0, 1600):.0f}" cy="{r.uniform(0, 1000):.0f}" r="{r.uniform(.8, 3):.1f}" fill="#fff" opacity="{r.uniform(.4, .9):.2f}"/>'
                             for _ in range(150)))
    body = (f'<rect width="{W}" height="{H}" fill="url(#sky)"/>{stars(r, 120, 0, 500)}'
            f'<g class="R"><circle cx="1230" cy="200" r="160" fill="url(#moon)"/><circle cx="1230" cy="200" r="62" fill="#fffbe8"/></g>'
            f'{sleigh}<path d="M0 760 C200 700 420 730 620 700 C820 680 1050 740 1250 700 C1400 680 1500 700 1600 690 V860 H0Z" fill="#1d335a"/>'
            f'{snow_ground}{left}{right}<rect width="{W}" height="{H}" fill="url(#veil)" opacity=".6"/>')
    return svg(defs + VEIL, body, "", "A snowy village at night with string lights and a sleigh crossing the moon")


# ------------------------------------------------------------------ snowglobe
def christmas_snowglobe():
    r = rnd(23)
    defs = (COMMON
            + lin("bg", [(0, "#06141a"), (1, "#0c2a2e")])
            + rad("glass", [(0, "#cfe9ff", .08), (.75, "#9fd2ff", .18), (.96, "#e8f6ff", .55), (1, "#e8f6ff", 0)])
            + lin("inside", [(0, "#123a5a"), (1, "#1f5a7a")])
            + lin("base", [(0, "#b8862c"), (.5, "#e8c060"), (1, "#8a5e18")], x2=1, y2=0)
            + lin("baseD", [(0, "#5a3a10"), (1, "#3a2408")])
            + lin("snowG", [(0, "#f4f8ff"), (1, "#b9cbe6")])
            + f'<clipPath id="globe"><circle cx="1330" cy="500" r="230"/></clipPath>')
    bokeh = "".join(f'<circle cx="{r.uniform(0, 1600):.0f}" cy="{r.uniform(0, 1000):.0f}" r="{r.uniform(14, 60):.0f}" '
                    f'fill="{r.choice(["#ff4d4d", "#ffd23d", "#43d17a", "#ff8ad8", "#4da3ff"])}" opacity="{r.uniform(.06, .2):.2f}" filter="url(#soft)"/>'
                    for _ in range(40))
    inside = ('<rect x="1100" y="270" width="460" height="460" fill="url(#inside)"/>'
              + stars(r, 30, 280, 520, 1110, 1550)
              + '<path d="M1100 600 C1200 560 1300 590 1400 570 C1480 556 1540 580 1560 590 V740 H1100Z" fill="url(#snowG)"/>'
              '<rect x="1220" y="500" width="110" height="80" fill="#a33a2e"/>'
              '<path d="M1210 504 L1275 450 L1340 504Z" fill="url(#snowG)"/>'
              '<rect x="1240" y="520" width="24" height="24" fill="#ffc46b" filter="url(#glow)"/><rect x="1290" y="520" width="24" height="24" fill="#ffc46b" filter="url(#glow)"/>'
              '<rect x="1266" y="546" width="22" height="34" fill="#3a2414"/>'
              + tree(1420, 590, 150, r, ornaments=False)
              + "".join(f'<circle cx="{r.uniform(1110, 1550):.0f}" cy="{r.uniform(280, 720):.0f}" r="{r.uniform(1.5, 4):.1f}" fill="#fff" opacity=".9"/>'
                        for _ in range(90)))
    globe = ('<g class="R">'
             '<ellipse cx="1330" cy="770" rx="250" ry="34" fill="#000" opacity=".5" filter="url(#soft)"/>'
             f'<g clip-path="url(#globe)">{inside}</g>'
             '<circle cx="1330" cy="500" r="230" fill="url(#glass)"/>'
             '<path d="M1180 400 A180 180 0 0 1 1300 300" stroke="#fff" stroke-width="10" stroke-linecap="round" opacity=".45" fill="none"/>'
             '<circle cx="1330" cy="500" r="230" fill="none" stroke="#e8f6ff" stroke-width="2" opacity=".5"/>'
             '<path d="M1150 690 Q1330 740 1510 690 L1540 790 Q1330 830 1120 790Z" fill="url(#base)"/>'
             '<path d="M1120 790 Q1330 830 1540 790 L1550 820 Q1330 865 1110 820Z" fill="url(#baseD)"/>'
             '<path d="M1150 715 Q1330 760 1510 715" stroke="#c62828" stroke-width="14" fill="none"/>'
             '</g>')

    def bauble(x, length, rr, c):
        return (f'<path d="M{x} 0 V{length}" stroke="#d9c38a" stroke-width="1.5"/>'
                f'<rect x="{x - 7}" y="{length}" width="14" height="10" rx="2" fill="#d9c38a"/>'
                f'<circle cx="{x}" cy="{length + 10 + rr}" r="{rr}" fill="{c}"/>'
                f'<circle cx="{x - rr * .35:.0f}" cy="{length + 10 + rr * .65:.0f}" r="{rr * .28:.1f}" fill="#fff" opacity=".7"/>')
    cane = ('<path d="M300 520 V380 Q300 330 340 330 Q380 330 380 370" stroke="#f4f1ea" stroke-width="22" fill="none" stroke-linecap="round"/>'
            '<path d="M300 520 V380 Q300 330 340 330 Q380 330 380 370" stroke="#c62828" stroke-width="22" fill="none" stroke-linecap="round" stroke-dasharray="14 14"/>')
    left = ('<g class="L">'
            + bauble(80, 140, 34, "#c62828") + bauble(170, 260, 26, "#e8b04a") + bauble(250, 90, 30, "#1f7a3e")
            + bauble(380, 200, 22, "#2f6fd8")
            + cane + present(60, 760, 140, 100, "#c62828", "#e8b04a") + present(220, 790, 100, 70, "#1f7a3e", "#f4f1ea")
            + '</g>')
    body = (f'<rect width="{W}" height="{H}" fill="url(#bg)"/>{bokeh}{left}{globe}'
            f'<rect width="{W}" height="{H}" fill="url(#veil)" opacity=".6"/>')
    return svg(defs + VEIL, body, "", "A snow globe with a little house and tree, soft festive lights and hanging ornaments")


SCENES = {
    "christmas-fireplace": christmas_fireplace,
    "christmas-village": christmas_village,
    "christmas-snowglobe": christmas_snowglobe,
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
            "// Generated by tools/build_christmas.py: edit that file, not this one.\n"
            f"export const {const} = `{escaped}`\n")
        print(f"{name}: {len(s)} chars")
