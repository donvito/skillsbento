#!/usr/bin/env python3
"""Builds four calm, cosy backdrop scenes (SVG) for the backdrops mod.

  rainy-cafe        rain on a café window, a steaming cup, warm city bokeh outside
  cabin-library     bookshelves, an armchair with a sleeping cat, snow at the window
  underwater-reef   coral, fish, a sea turtle and light rays from above
  deep-space        a colourful nebula, a ringed planet and distant galaxies

Vector only, drawn still, each subject in a side gutter (.L / .R) beside the
frosted conversation column. Shares its helpers with build_travel.py.

Usage: python3 tools/build_cozy.py hooks/scenes
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_travel import H, VEIL, W, lin, rad, rnd, svg  # noqa: E402
from smil import timeshift  # noqa: E402

GLOW = ('<filter id="glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="3" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        '<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="14"/></filter>'
        '<filter id="soft4" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4"/></filter>')


# ----------------------------------------------------------------- rainy café
def rainy_cafe():
    r = rnd(41)
    defs = (lin("outside", [(0, "#101826"), (.6, "#1d2433"), (1, "#2a2230")])
            + lin("wood", [(0, "#6b4428"), (1, "#3a2414")])
            + lin("frame", [(0, "#2a1c14"), (1, "#16100b")], x2=1, y2=0)
            + rad("pendant", [(0, "#ffd08a", .55), (1, "#ffd08a", 0)])
            + lin("cup", [(0, "#f4efe6"), (1, "#cfc6b8")], x2=1, y2=0)
            + rad("coffee", [(0, "#c98a52"), (.7, "#8a5a32"), (1, "#5a3a20")])
            + rad("drop", [(0, "#ffffff", .5), (.6, "#cfe0ff", .15), (1, "#cfe0ff", 0)], cx=.35, cy=.35)
            + GLOW)
    bokeh = "".join(f'<circle cx="{r.uniform(0, 1600):.0f}" cy="{r.uniform(60, 760):.0f}" r="{r.uniform(12, 55):.0f}" '
                    f'fill="{r.choice(["#ffb35a", "#ffd98a", "#ff7a5a", "#9ad1ff", "#ffcf7a"])}" opacity="{r.uniform(.12, .38):.2f}" filter="url(#soft4)"/>'
                    for _ in range(70))
    drops = "".join(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rr:.1f}" fill="url(#drop)" stroke="#e6eeff" stroke-opacity=".25" stroke-width=".8"/>'
                    for x, y, rr in ((r.uniform(0, 1600), r.uniform(40, 780), r.uniform(2, 7)) for _ in range(260)))
    streaks = "".join(f'<path d="M{x:.0f} {y:.0f} q{r.uniform(-4, 4):.0f} {ln / 2:.0f} 0 {ln:.0f}" stroke="#dfe8ff" stroke-width="2" opacity=".22" fill="none"/>'
                      for x, y, ln in ((r.uniform(0, 1600), r.uniform(40, 600), r.uniform(60, 180)) for _ in range(40)))
    frame = ('<rect x="0" y="0" width="1600" height="40" fill="url(#frame)"/>'
             '<rect x="0" y="780" width="1600" height="30" fill="url(#frame)"/>'
             '<rect x="0" y="0" width="34" height="810" fill="url(#frame)"/><rect x="1566" y="0" width="34" height="810" fill="url(#frame)"/>'
             '<rect x="783" y="0" width="34" height="810" fill="url(#frame)"/>')
    table = '<rect y="810" width="1600" height="190" fill="url(#wood)"/><path d="M0 812 H1600" stroke="#8a5a34" stroke-width="3"/>'
    steam = "".join(f'<path d="M{x} 640 c-18 -30 18 -50 0 -80 c-18 -30 18 -50 0 -80" stroke="#f4efe6" stroke-width="7" fill="none" '
                    f'stroke-linecap="round" opacity="{o}" filter="url(#soft4)"/>' for x, o in ((230, .35), (262, .25), (200, .2)))
    cup = ('<g class="L">'
           '<ellipse cx="240" cy="822" rx="140" ry="22" fill="#e9e2d6"/><ellipse cx="240" cy="818" rx="110" ry="14" fill="#d8cfc0"/>'
           '<path d="M150 690 Q150 820 240 820 Q330 820 330 690Z" fill="url(#cup)"/>'
           '<path d="M330 712 q52 6 46 46 q-6 34 -54 30" stroke="#e9e2d6" stroke-width="14" fill="none"/>'
           '<ellipse cx="240" cy="690" rx="90" ry="20" fill="url(#coffee)"/>'
           '<path d="M222 684 q18 -14 36 0 q-18 12 -36 0Z" fill="#f2e3cf" opacity=".85"/>'
           + steam + '</g>')
    lamp = ('<g class="R"><path d="M1340 0 V170" stroke="#1a120c" stroke-width="3"/>'
            '<circle cx="1340" cy="260" r="220" fill="url(#pendant)"/>'
            '<path d="M1290 170 h100 l30 60 h-160Z" fill="#2c3a2e"/><ellipse cx="1340" cy="232" rx="22" ry="10" fill="#fff1c4" filter="url(#glow)"/>'
            '<rect x="1280" y="760" width="150" height="50" rx="6" fill="#7a3a2a"/><rect x="1290" y="730" width="130" height="32" rx="5" fill="#2f5a7a"/>'
            '<rect x="1300" y="706" width="110" height="26" rx="5" fill="#c9a86a"/>'
            '<ellipse cx="1500" cy="800" rx="70" ry="12" fill="#e9e2d6"/>'
            '<path d="M1450 795 q50 -60 100 0Z" fill="#d99a4a"/><path d="M1470 778 q30 -24 60 0" stroke="#a8682a" stroke-width="3" fill="none"/></g>')
    body = (f'<rect width="{W}" height="{H}" fill="url(#outside)"/>{bokeh}{streaks}{drops}{frame}{table}{cup}{lamp}'
            f'<rect width="{W}" height="{H}" fill="url(#veil)" opacity=".55"/>')
    return svg(defs + VEIL, body, "", "Rain on a café window with a steaming cup and warm city lights outside")


# -------------------------------------------------------------- cabin library
def cabin_library():
    r = rnd(42)
    defs = (lin("wall", [(0, "#3a2416"), (1, "#24160c")])
            + lin("shelf", [(0, "#5a3a22"), (1, "#3a2414")])
            + lin("floor", [(0, "#4a2e1a"), (1, "#24160c")])
            + lin("leather", [(0, "#8a3a26"), (1, "#5a2216")])
            + rad("lampG", [(0, "#ffd08a", .6), (1, "#ffd08a", 0)])
            + lin("night", [(0, "#0a1224"), (1, "#1d2a44")])
            + GLOW)
    planks = "".join(f'<path d="M{x} 0 V840" stroke="#1a0f08" stroke-width="2" opacity=".5"/>' for x in range(0, 1600, 70))
    floor = ('<rect y="840" width="1600" height="160" fill="url(#floor)"/>'
             + "".join(f'<path d="M0 {850 + i * 30} H1600" stroke="#1a0f08" stroke-width="2" opacity=".5"/>' for i in range(5))
             + '<ellipse cx="800" cy="930" rx="560" ry="60" fill="#5a1f24" opacity=".7"/>')
    books = []
    for row in range(6):
        y = 120 + row * 118
        x = 40
        while x < 400:
            w = r.uniform(14, 28)
            h = r.uniform(70, 100)
            c = r.choice(["#7a2a24", "#2a4a6a", "#2f5a3a", "#8a6a2a", "#5a2a5a", "#a8682a", "#3a3a4a", "#b0302a"])
            if r.random() < .08:
                books.append(f'<rect x="{x:.0f}" y="{y + 100 - h * .9:.0f}" width="{h * .9:.0f}" height="{w:.0f}" fill="{c}"/>')
                x += h * .9 + 2
                continue
            books.append(f'<rect x="{x:.0f}" y="{y + 100 - h:.0f}" width="{w:.0f}" height="{h:.0f}" fill="{c}"/>'
                         f'<rect x="{x + 3:.0f}" y="{y + 110 - h:.0f}" width="{w - 6:.0f}" height="3" fill="#e8c060" opacity=".6"/>')
            x += w + 1.5
        books.append(f'<rect x="28" y="{y + 100}" width="390" height="14" fill="url(#shelf)"/>')
    shelf = (f'<g class="L"><rect x="20" y="90" width="406" height="760" fill="#1a0f08"/>{"".join(books)}'
             '<rect x="14" y="80" width="418" height="20" fill="url(#shelf)"/><rect x="14" y="80" width="16" height="770" fill="url(#shelf)"/>'
             '<rect x="416" y="80" width="16" height="770" fill="url(#shelf)"/></g>')
    flakes = "".join(f'<circle cx="{r.uniform(1210, 1510):.0f}" cy="{r.uniform(150, 430):.0f}" r="{r.uniform(1, 3):.1f}" fill="#fff" opacity=".85"/>'
                     for _ in range(60))
    window = ('<rect x="1200" y="140" width="320" height="300" fill="url(#night)"/>' + flakes
              + '<path d="M1200 400 Q1300 380 1360 396 Q1440 410 1520 392 V440 H1200Z" fill="#dfe8ff"/>'
              '<rect x="1196" y="136" width="328" height="308" fill="none" stroke="#5a3a22" stroke-width="16"/>'
              '<path d="M1360 140 V440 M1200 290 H1520" stroke="#5a3a22" stroke-width="10"/>')
    chair = ('<path d="M1180 860 V640 Q1180 560 1260 560 H1440 Q1520 560 1520 640 V860Z" fill="url(#leather)"/>'
             '<rect x="1140" y="690" width="90" height="170" rx="30" fill="url(#leather)"/>'
             '<rect x="1470" y="690" width="90" height="170" rx="30" fill="url(#leather)"/>'
             '<rect x="1220" y="740" width="270" height="70" rx="16" fill="#a04a32"/>'
             + "".join(f'<circle cx="{1220 + i * 50}" cy="{600 + j * 40}" r="4" fill="#3a140c"/>' for i in range(7) for j in range(2))
             + '<rect x="1170" y="860" width="20" height="30" fill="#2a160c"/><rect x="1510" y="860" width="20" height="30" fill="#2a160c"/>')
    cat = ('<g transform="translate(1350 730)"><ellipse cx="0" cy="0" rx="78" ry="36" fill="#d98a3a"/>'
           '<path d="M-60 -10 q-30 30 20 36 q60 6 100 -8" stroke="#b86a24" stroke-width="16" fill="none" stroke-linecap="round"/>'
           '<circle cx="58" cy="-14" r="30" fill="#d98a3a"/><path d="M38 -36 l6 -24 l14 18Z M64 -40 l14 -20 l6 24Z" fill="#d98a3a"/>'
           '<path d="M46 -14 q6 4 12 0 M64 -14 q6 4 12 0" stroke="#5a2a10" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
           '<path d="M-30 -20 q10 -6 20 0 M-6 -26 q10 -6 20 0" stroke="#b86a24" stroke-width="4" fill="none"/></g>')
    lamp = ('<circle cx="1590" cy="560" r="200" fill="url(#lampG)"/>'
            '<rect x="1560" y="760" width="60" height="100" fill="#3a2414"/>'
            '<path d="M1590 760 V620" stroke="#2a1a0e" stroke-width="5"/>'
            '<path d="M1550 620 h80 l-16 -60 h-48Z" fill="#e8c88a"/><ellipse cx="1590" cy="622" rx="30" ry="6" fill="#fff1c4" filter="url(#glow)"/>')
    right = f'<g class="R">{window}{lamp}{chair}{cat}</g>'
    body = (f'<rect width="{W}" height="{H}" fill="url(#wall)"/>{planks}{floor}{shelf}{right}'
            f'<rect width="{W}" height="{H}" fill="url(#veil)" opacity=".55"/>')
    return svg(defs + VEIL, body, "", "A cosy cabin library with bookshelves, an armchair, a sleeping cat and snow at the window")


# ------------------------------------------------------------ underwater reef
def underwater_reef():
    r = rnd(43)
    defs = (lin("water", [(0, "#1fa2c8"), (.35, "#0f6a9a"), (.75, "#0a3a6a"), (1, "#061f3f")])
            + lin("ray", [(0, "#ffffff", .35), (1, "#ffffff", 0)])
            + lin("sand", [(0, "#c9b07a"), (1, "#7a6a4a")])
            + lin("shell", [(0, "#6b8a3a"), (1, "#3a5a24")])
            + GLOW)
    rays = "".join(f'<path d="M{x:.0f} -20 L{x + w:.0f} -20 L{x + w * 4 + 160:.0f} 1000 L{x + 120:.0f} 1000Z" fill="url(#ray)" opacity="{o:.2f}"/>'
                   for x, w, o in ((r.uniform(-200, 1500), r.uniform(20, 60), r.uniform(.15, .35)) for _ in range(9)))
    sand = '<path d="M0 900 C300 870 600 890 800 900 C1000 910 1300 880 1600 895 V1000 H0Z" fill="url(#sand)"/>'

    def branch_coral(x, base, h, c):
        out = []
        def grow(x0, y0, ang, ln, depth):
            if depth == 0 or ln < 8:
                out.append(f'<circle cx="{x0:.0f}" cy="{y0:.0f}" r="5" fill="{c}"/>')
                return
            x1, y1 = x0 + ln * math.cos(ang), y0 + ln * math.sin(ang)
            out.append(f'<path d="M{x0:.0f} {y0:.0f} L{x1:.0f} {y1:.0f}" stroke="{c}" stroke-width="{depth * 3}" stroke-linecap="round"/>')
            grow(x1, y1, ang - r.uniform(.25, .55), ln * .72, depth - 1)
            grow(x1, y1, ang + r.uniform(.25, .55), ln * .72, depth - 1)
        grow(x, base, -math.pi / 2, h * .38, 4)
        return "".join(out)

    def brain_coral(x, y, rr, c):
        return (f'<path d="M{x - rr} {y} A{rr} {rr * .8} 0 0 1 {x + rr} {y}Z" fill="{c}"/>'
                + "".join(f'<path d="M{x - rr * .8 + i * rr * .32:.0f} {y - 4} q8 -{rr * .3:.0f} 16 0" stroke="#000" stroke-opacity=".2" stroke-width="3" fill="none"/>'
                          for i in range(5)))

    def fan(x, base, h, c):
        return "".join(f'<path d="M{x} {base} Q{x + math.cos(a) * h * .5:.0f} {base - h * .4:.0f} {x + math.cos(a) * h * .7:.0f} {base - math.sin(a) * h:.0f}" '
                       f'stroke="{c}" stroke-width="3" fill="none" opacity=".85"/>' for a in [math.pi * (.25 + k * .05) for k in range(11)])

    def fish(x, y, s, body, fin, flip=False):
        d = -1 if flip else 1
        return (f'<g transform="translate({x} {y}) scale({s * d} {s})">'
                f'<ellipse cx="0" cy="0" rx="26" ry="14" fill="{body}"/>'
                f'<path d="M-22 0 L-40 -14 L-40 14Z" fill="{fin}"/><path d="M-4 -12 q6 -10 14 0Z" fill="{fin}"/>'
                f'<circle cx="14" cy="-3" r="3" fill="#0a1020"/><circle cx="15" cy="-4" r="1" fill="#fff"/></g>')

    def clown(x, y, s, flip=False):
        d = -1 if flip else 1
        return (f'<g transform="translate({x} {y}) scale({s * d} {s})">'
                '<ellipse cx="0" cy="0" rx="24" ry="13" fill="#ff7a1a"/>'
                '<path d="M-6 -12 V12 M10 -11 V11" stroke="#fff" stroke-width="5"/>'
                '<path d="M-20 0 L-36 -12 L-36 12Z" fill="#ff7a1a" stroke="#1a1a1a" stroke-width="1.5"/>'
                '<circle cx="15" cy="-3" r="3" fill="#0a1020"/></g>')

    turtle = ('<g transform="translate(1340 380) rotate(-8)">'
              '<ellipse cx="0" cy="0" rx="110" ry="70" fill="url(#shell)"/>'
              + "".join(f'<path d="M{x} {y} l18 -10 l18 10 l0 20 l-18 10 l-18 -10Z" fill="#4a6a2a" stroke="#2a4a14" stroke-width="2"/>'
                        for x, y in ((-60, -18), (-24, -36), (12, -36), (-24, 4), (12, 4), (48, -18)))
              + '<ellipse cx="130" cy="-6" rx="34" ry="24" fill="#8aa86a"/><circle cx="146" cy="-12" r="4" fill="#0a1020"/>'
              '<path d="M60 40 q60 40 110 20 q-40 -10 -70 -40Z" fill="#8aa86a"/><path d="M60 -50 q70 -40 110 -30 q-40 20 -80 50Z" fill="#8aa86a"/>'
              '<path d="M-90 40 q-30 30 -60 24 q20 -14 40 -40Z" fill="#8aa86a"/><path d="M-90 -40 q-30 -26 -56 -20 q20 14 40 36Z" fill="#8aa86a"/></g>')
    school = "".join(fish(1180 + r.uniform(-60, 60), 640 + r.uniform(-40, 40), .45, "#cfe0ef", "#9ab4cc") for _ in range(14))
    left = ('<g class="L">'
            + branch_coral(120, 900, 360, "#ff6b8a") + branch_coral(330, 900, 260, "#ffb347")
            + brain_coral(230, 900, 70, "#c46bff") + fan(430, 900, 220, "#ff4d6d")
            + clown(220, 640, 1.1) + clown(300, 600, .9, True)
            + fish(110, 420, 1.3, "#2f6fd8", "#ffd23d") + fish(360, 330, 1, "#ffd23d", "#2f6fd8", True)
            + '</g>')
    right = ('<g class="R">' + turtle + school
             + branch_coral(1490, 900, 330, "#ff8a5c") + brain_coral(1340, 900, 80, "#5fd0c0")
             + fan(1220, 900, 200, "#c46bff") + '</g>')
    bubbles = "".join(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rr:.1f}" fill="none" stroke="#dff6ff" stroke-width="1.5" opacity=".6"/>'
                      for x, y, rr in ((r.choice([r.uniform(60, 460), r.uniform(1140, 1560)]), r.uniform(80, 860), r.uniform(3, 9)) for _ in range(40)))
    body = (f'<rect width="{W}" height="{H}" fill="url(#water)"/>{rays}{sand}{left}{right}{bubbles}'
            f'<rect width="{W}" height="{H}" fill="url(#veil)" opacity=".55"/>')
    return svg(defs + VEIL, body, "", "A coral reef underwater with fish, a sea turtle and light rays from above")


# ------------------------------------------------------------------ deep space
def deep_space():
    r = rnd(44)
    defs = (lin("void", [(0, "#03020a"), (1, "#0a0618")])
            + lin("planet", [(0, "#f2d6a2"), (.3, "#d9a86a"), (.5, "#f0c88a"), (.7, "#b8804a"), (1, "#e8c08a")], x2=0, y2=1)
            + rad("planetShade", [(0, "#000", 0), (.6, "#000", .1), (1, "#000", .75)], cx=.35, cy=.35, r_=.75)
            + lin("ring", [(0, "#e8d0a8", .1), (.3, "#f4e2c0", .8), (.6, "#c9a878", .55), (1, "#e8d0a8", .1)], x2=1, y2=0)
            + rad("galaxyCore", [(0, "#fff6e0"), (.3, "#ffd9a8", .7), (1, "#8a6aff", 0)])
            + rad("moonG", [(0, "#c9c9d6"), (1, "#6a6a7a")], cx=.35, cy=.35)
            + '<filter id="neb" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="38"/></filter>'
            + GLOW)
    nebula = "".join(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{rx:.0f}" ry="{ry:.0f}" fill="{c}" opacity="{o:.2f}" filter="url(#neb)" '
                     f'transform="rotate({r.uniform(-40, 40):.0f} {x:.0f} {y:.0f})"/>'
                     for x, y, rx, ry, c, o in (
                         (r.uniform(-100, 1700), r.uniform(-100, 1100), r.uniform(120, 360), r.uniform(60, 180),
                          r.choice(["#ff3d9b", "#8a3dff", "#3d8bff", "#3de1c8", "#ff8a3d", "#c43dff"]), r.uniform(.12, .32))
                         for _ in range(26)))
    dust = "".join(f'<circle cx="{r.uniform(0, 1600):.0f}" cy="{r.uniform(0, 1000):.0f}" r="{r.uniform(.4, 1.1):.1f}" fill="#fff" opacity="{r.uniform(.3, .8):.2f}"/>'
                   for _ in range(420))
    bright = "".join(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="1.8" fill="#fff" filter="url(#glow)"/>'
                     f'<path d="M{x - 9:.0f} {y:.0f} H{x + 9:.0f} M{x:.0f} {y - 9:.0f} V{y + 9:.0f}" stroke="#fff" stroke-width=".8" opacity=".7"/>'
                     for x, y in ((r.uniform(0, 1600), r.uniform(0, 1000)) for _ in range(18)))
    cx, cy, R = 1340, 470, 150
    planet = ('<g class="R">'
              f'<ellipse cx="{cx}" cy="{cy}" rx="{R * 2.1:.0f}" ry="{R * .5:.0f}" fill="none" stroke="url(#ring)" stroke-width="26" transform="rotate(-18 {cx} {cy})"/>'
              f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="url(#planet)" transform="rotate(-18 {cx} {cy})"/>'
              f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="url(#planetShade)"/>'
              f'<path d="M{cx - R * 2.1 * math.cos(math.radians(18)):.0f} {cy + R * 2.1 * math.sin(math.radians(18)):.0f} '
              f'A{R * 2.1:.0f} {R * .5:.0f} -18 0 0 {cx + R * 2.1 * math.cos(math.radians(18)):.0f} {cy - R * 2.1 * math.sin(math.radians(18)):.0f}" '
              f'stroke="url(#ring)" stroke-width="26" fill="none"/>'
              f'<circle cx="{cx - 330}" cy="{cy + 250}" r="34" fill="url(#moonG)"/></g>')

    def galaxy(gx, gy, s, tilt):
        arms = "".join(f'<ellipse cx="{gx}" cy="{gy}" rx="{(60 + k * 22) * s:.0f}" ry="{(22 + k * 8) * s:.0f}" fill="none" stroke="#b8a6ff" '
                       f'stroke-width="{max(1, 6 - k):.0f}" opacity="{.5 - k * .07:.2f}" transform="rotate({tilt + k * 18} {gx} {gy})" filter="url(#soft4)"/>'
                       for k in range(6))
        return f'{arms}<ellipse cx="{gx}" cy="{gy}" rx="{70 * s:.0f}" ry="{40 * s:.0f}" fill="url(#galaxyCore)" transform="rotate({tilt} {gx} {gy})"/>'

    left = f'<g class="L">{galaxy(230, 330, 1.4, -25)}{galaxy(380, 720, .5, 30)}</g>'
    body = (f'<rect width="{W}" height="{H}" fill="url(#void)"/>{nebula}{dust}{bright}{left}{planet}'
            f'<rect width="{W}" height="{H}" fill="url(#veil)" opacity=".5"/>')
    return svg(defs + VEIL, body, "", "A colourful nebula, a ringed planet and distant spiral galaxies in deep space")


SCENES = {
    "rainy-cafe": rainy_cafe,
    "cabin-library": cabin_library,
    "underwater-reef": underwater_reef,
    "deep-space": deep_space,
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
            "// Generated by tools/build_cozy.py: edit that file, not this one.\n"
            f"export const {const} = `{escaped}`\n")
        print(f"{name}: {len(s)} chars")
