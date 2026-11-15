#!/usr/bin/env python3
"""Builds six city and landscape backdrop scenes (SVG) for the backdrops mod.

  new-york          the Manhattan skyline at night, the Empire State Building lit
  london            Big Ben and Westminster in the rain, a red double-decker bus
  santorini         white houses and blue domes above the sea at sunset
  northern-lights   a red cabin by a fjord under a big green aurora
  new-year          fireworks and confetti over a city skyline
  netherlands       tulip fields, a canal, windmills and bicycles at golden hour

Vector only, drawn still, each subject in a side gutter (.L / .R) beside the
frosted conversation column. Shares its helpers with build_travel.py.

Usage: python3 tools/build_places.py hooks/scenes
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_travel import H, VEIL, W, lin, rad, rnd, stars, svg  # noqa: E402
from smil import timeshift  # noqa: E402

GLOW = ('<filter id="glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="3" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        '<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="12"/></filter>')


def windows(r, x, top, w, bottom, step=(14, 18), size=(6, 9), p=.45, colors=("#ffd98a", "#ffe9b8", "#cfe3ff")):
    out = []
    for yy in range(int(top + 10), int(bottom - 10), step[1]):
        for xx in range(int(x + 6), int(x + w - 8), step[0]):
            if r.random() < p:
                out.append(f'<rect x="{xx}" y="{yy}" width="{size[0]}" height="{size[1]}" fill="{r.choice(colors)}" '
                           f'opacity="{r.uniform(.45, .95):.2f}"/>')
    return "".join(out)


def skyline(r, x0, x1, base, hmin, hmax, fill, lit=True):
    out = []
    x = x0
    while x < x1:
        w = r.uniform(40, 95)
        h = r.uniform(hmin, hmax)
        out.append(f'<rect x="{x:.0f}" y="{base - h:.0f}" width="{w:.0f}" height="{h:.0f}" fill="{fill}"/>')
        if r.random() < .3:
            out.append(f'<rect x="{x + w * .3:.0f}" y="{base - h - 18:.0f}" width="{w * .4:.0f}" height="18" fill="{fill}"/>')
        if lit:
            out.append(windows(r, x, base - h, w, base))
        x += w + r.uniform(0, 6)
    return "".join(out)


def water(r, y, color_top, color_bottom, glints=("#ffd98a",), n=40, id_="river"):
    grad = lin(id_, [(0, color_top), (1, color_bottom)])
    marks = "".join(f'<path d="M{r.uniform(0, 1600):.0f} {r.uniform(y + 8, 995):.0f} h{r.uniform(20, 90):.0f}" '
                    f'stroke="{r.choice(glints)}" stroke-width="2" opacity="{r.uniform(.2, .5):.2f}"/>' for _ in range(n))
    return grad, f'<rect y="{y}" width="{W}" height="{H - y}" fill="url(#{id_})"/>{marks}'


# ------------------------------------------------------------------- new york
def new_york():
    r = rnd(31)
    defs = (lin("sky", [(0, "#050817"), (.55, "#151a45"), (.85, "#3b2a5e"), (1, "#7a4a6a")])
            + rad("moon", [(0, "#fffbe8"), (.5, "#fff3c4", .4), (1, "#fff3c4", 0)])
            + lin("esb", [(0, "#2a2f45"), (1, "#141827")], x2=1, y2=0)
            + lin("crown", [(0, "#ffe9a8"), (.5, "#ffb84a"), (1, "#d9482f")])
            + rad("crownGlow", [(0, "#ffb84a", .55), (1, "#ffb84a", 0)])
            + GLOW)
    wgrad, river = water(r, 880, "#0d1430", "#04060f", ("#ffd98a", "#cfe3ff"), 50)
    far = skyline(r, -20, 1640, 880, 120, 300, "#1a1e3a", lit=False)
    near = skyline(r, -20, 1640, 880, 60, 220, "#0c0f22")
    # the Empire State Building, right gutter: setbacks, a lit crown, a mast
    cx = 1380
    esb = [f'<circle cx="{cx}" cy="250" r="190" fill="url(#crownGlow)"/>']
    tiers = [(170, 880, 560), (130, 560, 430), (96, 430, 330), (64, 330, 270), (40, 270, 230), (24, 230, 200)]
    for w, b, t in tiers:
        esb.append(f'<rect x="{cx - w / 2}" y="{t}" width="{w}" height="{b - t}" fill="url(#esb)"/>')
        esb.append(windows(r, cx - w / 2, t, w, b, step=(10, 14), size=(4, 7), p=.5))
    esb.append(f'<rect x="{cx - 20}" y="215" width="40" height="70" fill="url(#crown)" opacity=".9"/>'
               f'<path d="M{cx - 12} 200 L{cx} 120 L{cx + 12} 200Z" fill="url(#crown)"/>'
               f'<path d="M{cx} 120 V70" stroke="#d9dde8" stroke-width="3"/>'
               f'<circle cx="{cx}" cy="68" r="5" fill="#ff4d4d" filter="url(#glow)" class="tw1"/>')
    # an arched art-deco crown on the left
    lx = 240
    deco = [f'<rect x="{lx - 55}" y="420" width="110" height="460" fill="url(#esb)"/>',
            windows(r, lx - 55, 420, 110, 880, step=(10, 14), size=(4, 7), p=.5)]
    for i in range(5):
        w = 110 - i * 20
        y = 420 - i * 34
        deco.append(f'<path d="M{lx - w / 2} {y} Q{lx} {y - 60} {lx + w / 2} {y}Z" fill="#c9cfe0" opacity=".85"/>'
                    f'<path d="M{lx - w / 2 + 8} {y - 4} Q{lx} {y - 48} {lx + w / 2 - 8} {y - 4}" stroke="#ffd98a" stroke-width="2" fill="none" filter="url(#glow)"/>')
    deco.append(f'<path d="M{lx} 270 V180" stroke="#c9cfe0" stroke-width="4"/>')
    body = (f'<rect width="{W}" height="{H}" fill="url(#sky)"/>{stars(r, 90, 0, 380)}'
            f'<g class="L"><circle cx="380" cy="150" r="110" fill="url(#moon)"/><circle cx="380" cy="150" r="32" fill="#fffbe8"/></g>'
            f'{far}<g class="L">{"".join(deco)}</g><g class="R">{"".join(esb)}</g>{near}{river}'
            f'<rect width="{W}" height="{H}" fill="url(#veil)" opacity=".7"/>')
    return svg(defs + wgrad + VEIL, body, "", "The Manhattan skyline at night with the Empire State Building lit")


# --------------------------------------------------------------------- london
def london():
    r = rnd(32)
    defs = (lin("sky", [(0, "#0a0f1c"), (.6, "#1d2a44"), (1, "#3a4a66")])
            + lin("stone", [(0, "#c9a86a"), (1, "#7a6238")], x2=1, y2=0)
            + rad("clock", [(0, "#fff6d6"), (.8, "#ffe7a3"), (1, "#c9a86a")])
            + rad("lamp", [(0, "#ffd98a", .7), (1, "#ffd98a", 0)])
            + lin("bus", [(0, "#e8302a"), (1, "#a8160f")])
            + GLOW)
    wgrad, river = water(r, 840, "#141d33", "#05080f", ("#ffd98a", "#ffcf7a"), 60)
    # Westminster palace: a long gothic silhouette with pinnacles
    palace = ['<path d="M0 840 V700 ' + " ".join(f"L{x} {700 - (14 if i % 2 else 0)} L{x + 20} {700 - (14 if i % 2 else 0)}" for i, x in enumerate(range(0, 1200, 40))) + ' L1200 700 V840Z" fill="#2a2a32"/>']
    palace.append(windows(r, 0, 700, 1200, 840, step=(16, 22), size=(6, 10), p=.4, colors=("#ffd98a",)))
    for x in range(30, 1200, 120):
        palace.append(f'<path d="M{x} 700 V650 L{x + 6} 630 L{x + 12} 650 V700Z" fill="#2a2a32"/>')
    # Elizabeth Tower, right gutter
    cx = 1390
    tower = (f'<rect x="{cx - 42}" y="300" width="84" height="540" fill="url(#stone)"/>'
             + "".join(f'<path d="M{cx - 30 + i * 15} 320 V830" stroke="#6b5530" stroke-width="2" opacity=".6"/>' for i in range(5))
             + f'<rect x="{cx - 52}" y="230" width="104" height="110" fill="url(#stone)"/>'
             f'<circle cx="{cx}" cy="285" r="40" fill="url(#clock)" filter="url(#glow)"/>'
             f'<circle cx="{cx}" cy="285" r="40" fill="none" stroke="#3a2e18" stroke-width="3"/>'
             + "".join(f'<path d="M{cx + 33 * math.cos(a):.1f} {285 + 33 * math.sin(a):.1f} L{cx + 37 * math.cos(a):.1f} {285 + 37 * math.sin(a):.1f}" stroke="#3a2e18" stroke-width="2"/>'
                       for a in (k * math.pi / 6 for k in range(12)))
             + f'<path d="M{cx} 285 L{cx} 258 M{cx} 285 L{cx + 18} 292" stroke="#1a1408" stroke-width="3" stroke-linecap="round"/>'
             f'<rect x="{cx - 46}" y="190" width="92" height="44" fill="url(#stone)"/>'
             f'<path d="M{cx - 46} 190 L{cx} 70 L{cx + 46} 190Z" fill="#3a3a44"/>'
             f'<path d="M{cx} 70 V40" stroke="#c9a86a" stroke-width="3"/>'
             + "".join(f'<path d="M{x} 190 V160 L{x + 4} 148 L{x + 8} 160 V190Z" fill="#c9a86a"/>' for x in (cx - 50, cx + 42)))
    # Westminster Bridge with lamps, a red double-decker bus on the left
    bridge = ('<path d="M-20 820 Q300 790 640 820 V836 H-20Z" fill="#2c4a3a"/>'
              + "".join(f'<circle cx="{x}" cy="770" r="40" fill="url(#lamp)"/><path d="M{x} 776 V818" stroke="#1a1a1a" stroke-width="3"/>'
                        f'<circle cx="{x}" cy="772" r="5" fill="#fff1c4"/>' for x in (60, 330, 600)))
    bx, by = 120, 700
    bus = (f'<g transform="translate({bx} {by})">'
           '<rect x="0" y="0" width="250" height="118" rx="12" fill="url(#bus)"/>'
           '<rect x="0" y="56" width="250" height="6" fill="#7a0f0a"/>'
           + "".join(f'<rect x="{14 + i * 46}" y="12" width="38" height="30" rx="4" fill="#ffe6a8" opacity=".9"/>' for i in range(5))
           + "".join(f'<rect x="{14 + i * 46}" y="70" width="38" height="28" rx="4" fill="#ffe6a8" opacity=".85"/>' for i in range(4))
           + '<rect x="200" y="70" width="34" height="40" fill="#3a0806"/>'
           '<rect x="216" y="4" width="30" height="20" rx="3" fill="#1a1a1a"/>'
           '<circle cx="50" cy="120" r="17" fill="#141414"/><circle cx="50" cy="120" r="7" fill="#777"/>'
           '<circle cx="200" cy="120" r="17" fill="#141414"/><circle cx="200" cy="120" r="7" fill="#777"/>'
           '<circle cx="248" cy="100" r="5" fill="#fff6c4" filter="url(#glow)"/></g>')
    rain = "".join(f'<path d="M{r.uniform(0, 1700):.0f} {r.uniform(0, 1000):.0f} l-7 24" stroke="#cfd8ff" stroke-width="1.2" opacity=".3"/>'
                   for _ in range(170))
    body = (f'<rect width="{W}" height="{H}" fill="url(#sky)"/>{"".join(palace)}<g class="R">{tower}</g>{river}'
            f'<g class="L">{bridge}{bus}</g>{rain}<rect width="{W}" height="{H}" fill="url(#veil)" opacity=".65"/>')
    return svg(defs + wgrad + VEIL, body, "", "Big Ben and Westminster in the rain, with a red double-decker bus on the bridge")


# ------------------------------------------------------------------ santorini
def santorini():
    r = rnd(33)
    defs = (lin("sky", [(0, "#2a1f4f"), (.4, "#7a3f74"), (.7, "#e07a5f"), (.86, "#f6b86b")])
            + lin("sea", [(0, "#3a4f8f"), (.4, "#1d2c63"), (1, "#0b1233")])
            + rad("sun", [(0, "#fff1c4"), (.25, "#ffc46b", .9), (1, "#ff8a5c", 0)])
            + lin("cliff", [(0, "#7a4a3a"), (1, "#3a2420")])
            + lin("whiteW", [(0, "#ffffff"), (1, "#e9dfe8")], x2=1, y2=0)
            + lin("dome", [(0, "#4f8fe8"), (1, "#1d4fa8")]))

    def village(x0, x1, top_y, base_y, side):
        out = []
        cliff = (f'<path d="M{x0} {base_y} L{x0} {top_y + 80} Q{(x0 + x1) / 2} {top_y - 20} {x1} {top_y + 40} '
                 f'L{x1 + (60 if side == "L" else -60)} {base_y}Z" fill="url(#cliff)"/>')
        out.append(cliff)
        for row in range(6):
            y = top_y + 40 + row * 60
            x = x0 + 10 + (row % 2) * 30
            while x < x1 - 40:
                w = r.uniform(50, 90)
                h = r.uniform(40, 60)
                out.append(f'<rect x="{x:.0f}" y="{y - h:.0f}" width="{w:.0f}" height="{h:.0f}" fill="url(#whiteW)"/>'
                           f'<rect x="{x + w * .35:.0f}" y="{y - h * .55:.0f}" width="{w * .22:.0f}" height="{h * .4:.0f}" fill="#3a6fc8"/>')
                if r.random() < .25:
                    out.append(f'<path d="M{x + 6:.0f} {y - h:.0f} A{w / 2 - 6:.0f} {w / 2 - 6:.0f} 0 0 1 {x + w - 6:.0f} {y - h:.0f}Z" fill="url(#dome)"/>'
                               f'<path d="M{x + w / 2:.0f} {y - h - w / 2 + 4:.0f} v-14 M{x + w / 2 - 5:.0f} {y - h - w / 2 - 6:.0f} h10" stroke="#fff" stroke-width="2"/>')
                x += w + r.uniform(4, 14)
        return "".join(out)

    right = village(1150, 1620, 300, 760, "R")
    left = village(-20, 430, 420, 780, "L")
    windmill = ('<g transform="translate(140 400)"><path d="M-22 0 L22 0 L18 -90 L-18 -90Z" fill="url(#whiteW)"/>'
                '<path d="M-20 -90 Q0 -118 20 -90Z" fill="#7a4a3a"/>'
                + "".join(f'<path d="M0 -96 L{70 * math.cos(a):.0f} {-96 + 70 * math.sin(a):.0f}" stroke="#e9dfe8" stroke-width="5"/>'
                          f'<path d="M{20 * math.cos(a):.0f} {-96 + 20 * math.sin(a):.0f} L{70 * math.cos(a) + 12 * math.cos(a + 1.5):.0f} '
                          f'{-96 + 70 * math.sin(a) + 12 * math.sin(a + 1.5):.0f}" stroke="#d9c9b8" stroke-width="8" opacity=".8"/>'
                          for a in (k * math.pi / 3 + .3 for k in range(6)))
                + '<circle cx="0" cy="-96" r="6" fill="#7a4a3a"/></g>')
    glints = "".join(f'<path d="M{r.uniform(420, 1180):.0f} {r.uniform(700, 900):.0f} h{r.uniform(30, 120):.0f}" stroke="#ffd59a" stroke-width="2" opacity="{r.uniform(.25, .6):.2f}"/>'
                     for _ in range(40))
    body = (f'<rect width="{W}" height="{H}" fill="url(#sky)"/><circle cx="800" cy="690" r="240" fill="url(#sun)"/>'
            f'<rect y="690" width="{W}" height="{H - 690}" fill="url(#sea)"/>{glints}'
            f'<path d="M600 700 Q800 680 1000 700 Q980 720 620 720Z" fill="#3a2a40" opacity=".7"/>'
            f'<g class="L">{left}{windmill}</g><g class="R">{right}</g>'
            f'<rect width="{W}" height="{H}" fill="url(#veil)" opacity=".6"/>')
    return svg(defs + VEIL, body, "", "White houses and blue domes on Santorini cliffs above the sea at sunset")


# ------------------------------------------------------------ northern lights
def northern_lights():
    r = rnd(34)
    defs = (lin("sky", [(0, "#02040c"), (.6, "#06122a"), (1, "#0c2440")])
            + lin("curtain", [(0, "#7dffcf", 0), (.35, "#3dffb0", .55), (.75, "#2fd68f", .35), (1, "#2fd68f", 0)])
            + lin("curtainP", [(0, "#ff7ad9", 0), (.4, "#c46bff", .35), (1, "#c46bff", 0)])
            + lin("fjord", [(0, "#0b1a2e"), (1, "#03070f")])
            + lin("mtnL", [(0, "#22324d"), (1, "#0a1220")])
            + lin("mtnR", [(0, "#1c2a44"), (1, "#080e1a")])
            + lin("cabin", [(0, "#b0302a"), (1, "#7a1a16")])
            + '<filter id="ab" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="6"/></filter>'
            + GLOW)
    rays = []
    for band, (y0, amp, grad, n) in enumerate(((140, 70, "curtain", 120), (240, 50, "curtainP", 70))):
        for i in range(n):
            x = -40 + i * (1700 / n) + r.uniform(-6, 6)
            top = y0 + amp * math.sin(x / 260 + band) + r.uniform(-10, 10)
            length = r.uniform(180, 330)
            rays.append(f'<rect x="{x:.0f}" y="{top:.0f}" width="{r.uniform(6, 16):.0f}" height="{length:.0f}" fill="url(#{grad})" '
                        f'opacity="{r.uniform(.4, .9):.2f}"/>')
    aurora = f'<g filter="url(#ab)">{"".join(rays)}</g>'
    mountains = ('<path d="M-20 760 L120 430 L200 520 L300 380 L420 620 L520 700 L560 760Z" fill="url(#mtnL)"/>'
                 '<path d="M120 430 L150 480 L132 476 L112 500 L100 470Z M300 380 L330 430 L310 426 L290 450 L278 420Z" fill="#dfe8ff" opacity=".8"/>'
                 '<path d="M1040 760 L1100 640 L1220 420 L1330 560 L1420 360 L1520 520 L1640 460 V760Z" fill="url(#mtnR)"/>'
                 '<path d="M1220 420 L1250 470 L1228 466 L1206 490 L1196 460Z M1420 360 L1452 412 L1430 408 L1408 432 L1396 402Z" fill="#dfe8ff" opacity=".8"/>')
    reflection = (f'<g opacity=".35" transform="translate(0 1520) scale(1 -1)">{aurora}{mountains}</g>')
    cabin = ('<g class="L"><path d="M150 780 L260 770 L400 790 L380 820 L140 820Z" fill="#c9d3ea"/>'
             '<rect x="200" y="700" width="140" height="80" fill="url(#cabin)"/>'
             '<path d="M190 704 L270 650 L350 704Z" fill="#2a1a18"/><path d="M188 704 L270 646 L352 704" stroke="#dfe8ff" stroke-width="5" fill="none"/>'
             '<rect x="220" y="722" width="26" height="22" fill="#ffc46b" filter="url(#glow)"/><rect x="290" y="722" width="26" height="22" fill="#ffc46b" filter="url(#glow)"/>'
             '<rect x="258" y="740" width="22" height="40" fill="#3a1a14"/></g>')
    body = (f'<rect width="{W}" height="{H}" fill="url(#sky)"/>{stars(r, 220, 0, 700)}{aurora}{mountains}'
            f'<rect y="760" width="{W}" height="{H - 760}" fill="url(#fjord)"/>{reflection}{cabin}'
            f'<rect width="{W}" height="{H}" fill="url(#veil)" opacity=".45"/>')
    return svg(defs + VEIL, body, "", "A red cabin by a fjord under a big green aurora")


# ------------------------------------------------------------------- new year
def new_year():
    r = rnd(35)
    colors = ["#ffd23d", "#ff4d8b", "#3de1ff", "#7dff6b", "#ff8a3d", "#c38bff", "#ffffff"]
    defs = (lin("sky", [(0, "#03030c"), (.7, "#0f1236"), (1, "#2a1a4a")])
            + rad("burstGlow", [(0, "#fff", .25), (1, "#fff", 0)])
            + GLOW)

    def burst(cx, cy, rr, color, n=26):
        out = [f'<circle cx="{cx}" cy="{cy}" r="{rr * 1.2:.0f}" fill="{color}" opacity=".08" filter="url(#soft)"/>']
        for k in range(n):
            a = k / n * 2 * math.pi + r.uniform(-.05, .05)
            l1 = rr * r.uniform(.25, .4)
            l2 = rr * r.uniform(.85, 1.05)
            x1, y1 = cx + l1 * math.cos(a), cy + l1 * math.sin(a)
            x2, y2 = cx + l2 * math.cos(a), cy + l2 * math.sin(a) + rr * .08
            out.append(f'<path d="M{x1:.0f} {y1:.0f} L{x2:.0f} {y2:.0f}" stroke="{color}" stroke-width="2" stroke-linecap="round" opacity=".85"/>'
                       f'<circle cx="{x2:.0f}" cy="{y2:.0f}" r="2.6" fill="{color}" filter="url(#glow)"/>')
        out.append(f'<circle cx="{cx}" cy="{cy}" r="6" fill="#fff" filter="url(#glow)"/>')
        return "".join(out)

    def trail(x, y0, y1):
        return f'<path d="M{x} {y0} Q{x + 6} {(y0 + y1) / 2} {x} {y1}" stroke="#ffd98a" stroke-width="2" opacity=".35"/>'

    left = (burst(220, 260, 150, colors[0]) + burst(110, 470, 90, colors[2]) + burst(380, 420, 70, colors[1])
            + trail(220, 760, 280) + trail(380, 760, 430))
    right = (burst(1360, 230, 170, colors[1]) + burst(1520, 450, 95, colors[3]) + burst(1230, 470, 80, colors[5])
             + trail(1360, 760, 250) + trail(1230, 760, 480))
    def piece(x, y):
        return (f'<rect x="{x:.0f}" y="{y:.0f}" width="{r.uniform(6, 12):.0f}" height="{r.uniform(3, 6):.0f}" '
                f'fill="{r.choice(colors)}" transform="rotate({r.uniform(0, 180):.0f} {x:.0f} {y:.0f})"/>')
    conf_l = "".join(piece(r.uniform(0, 480), r.uniform(0, 980)) for _ in range(60))
    conf_r = "".join(piece(r.uniform(1120, 1600), r.uniform(0, 980)) for _ in range(60))
    city = skyline(r, -20, 1640, 860, 80, 220, "#0a0b1c")
    wgrad, river = water(r, 860, "#151a40", "#05060f", tuple(colors[:4]), 60, id_="bay")
    body = (f'<rect width="{W}" height="{H}" fill="url(#sky)"/>{stars(r, 60, 0, 300)}'
            f'<g class="L">{left}</g><g class="R">{right}</g>{city}{river}<g class="L">{conf_l}</g>'
            f'<g class="R">{conf_r}</g><rect width="{W}" height="{H}" fill="url(#veil)" opacity=".6"/>')
    return svg(defs + wgrad + VEIL, body, "", "Fireworks and confetti over a city skyline on New Year's Eve")


# ---------------------------------------------------------------- netherlands
def windmill(x, base, s, angle=18):
    """A traditional Dutch smock mill: tapered body, gallery, cap and four lattice sails."""
    def sail(a):
        blade = ('<g transform="rotate({a})">'
                 '<path d="M0 0 V-200" stroke="#3a2a1a" stroke-width="5"/>'
                 '<rect x="2" y="-196" width="34" height="150" fill="#f2ead8" opacity=".9" stroke="#3a2a1a" stroke-width="2"/>'
                 + "".join(f'<path d="M2 {-196 + i * 15} H36" stroke="#3a2a1a" stroke-width="1"/>' for i in range(1, 10))
                 + '<path d="M19 -196 V-46" stroke="#3a2a1a" stroke-width="1"/></g>')
        return blade.format(a=a)
    hub_y = -300
    return (f'<g transform="translate({x} {base}) scale({s})">'
            '<path d="M-70 0 L-46 -270 L46 -270 L70 0Z" fill="#3f5a3a"/>'
            + "".join(f'<path d="M{-66 + i * 4.6:.1f} {-20 - i * 25} H{66 - i * 4.6:.1f}" stroke="#2e4229" stroke-width="2" opacity=".7"/>' for i in range(10))
            + '<path d="M-46 -270 L46 -270 L70 0" fill="none" stroke="#2a3a26" stroke-width="2"/>'
            '<rect x="-96" y="-132" width="192" height="10" fill="#5a3a22"/>'
            + "".join(f'<path d="M{-92 + i * 23} -122 V-100" stroke="#5a3a22" stroke-width="3"/>' for i in range(9))
            + '<path d="M-20 0 V-50 Q0 -66 20 -50 V0Z" fill="#2a1a10"/>'
            '<rect x="-12" y="-200" width="24" height="28" fill="#f6d27a" opacity=".85"/>'
            '<path d="M-56 -270 Q0 -330 56 -270Z" fill="#2e2a26"/>'
            f'<g transform="translate(0 {hub_y}) rotate({angle})">{sail(0)}{sail(90)}{sail(180)}{sail(270)}'
            '<circle r="12" fill="#2a1a10"/></g></g>')


def bicycle(x, y, s, frame, basket=None):
    """A classic Dutch step-through bike in side view, wheels resting at y."""
    wheel = '<circle r="42" fill="none" stroke="#141414" stroke-width="5"/>' + "".join(
        f'<path d="M0 0 L{42 * math.cos(a):.1f} {42 * math.sin(a):.1f}" stroke="#9a9a9a" stroke-width="1"/>' for a in [k * math.pi / 8 for k in range(16)])
    flowers = ""
    if basket:
        flowers = (f'<rect x="112" y="-92" width="44" height="30" rx="4" fill="#a8782a" stroke="#6a4a18" stroke-width="2"/>'
                   + "".join(f'<path d="M{118 + i * 8} -92 v-22" stroke="#3a7a2a" stroke-width="2"/>'
                             f'<ellipse cx="{118 + i * 8}" cy="-116" rx="5" ry="8" fill="{c}"/>' for i, c in enumerate(basket)))
    return (f'<g transform="translate({x} {y - 42 * s}) scale({s})">'
            f'<g>{wheel}</g><g transform="translate(120 0)">{wheel}</g>'
            '<path d="M-48 -8 A50 50 0 0 1 30 -36 M72 -36 A50 50 0 0 1 168 -8" stroke="#202020" stroke-width="5" fill="none"/>'
            f'<path d="M0 0 L54 4 Q66 -40 104 -66 L120 0 M54 4 L36 -62 M0 0 L36 -62" stroke="{frame}" stroke-width="7" fill="none" stroke-linecap="round"/>'
            f'<path d="M104 -66 L96 -86 Q80 -94 64 -88" stroke="#202020" stroke-width="5" fill="none" stroke-linecap="round"/>'
            '<path d="M22 -70 h30 q6 0 4 6 h-36Z" fill="#3a2414"/>'
            f'<circle cx="54" cy="4" r="10" fill="none" stroke="#303030" stroke-width="4"/>{flowers}</g>')


def netherlands():
    r = rnd(36)
    horizon = 560
    defs = (lin("sky", [(0, "#2e4c80"), (.5, "#6f96c8"), (.85, "#e8b98c"), (1, "#f2c99a")])
            + lin("polder", [(0, "#5f8f3a"), (1, "#2f5a22")])
            + lin("canal", [(0, "#8fb0d0"), (1, "#3a5a80")])
            + rad("sunNL", [(0, "#ffe2a8", .9), (1, "#ffe2a8", 0)])
            + '<filter id="cl" x="-30%" y="-60%" width="160%" height="220%"><feGaussianBlur stdDeviation="12"/></filter>')
    clouds = "".join(f'<ellipse cx="{r.uniform(-100, 1700):.0f}" cy="{r.uniform(80, 380):.0f}" rx="{r.uniform(100, 220):.0f}" ry="{r.uniform(24, 50):.0f}" '
                     f'fill="#ffffff" opacity="{r.uniform(.35, .6):.2f}" filter="url(#cl)"/>' for _ in range(12))
    trees = "".join(f'<ellipse cx="{x:.0f}" cy="{horizon - r.uniform(6, 18):.0f}" rx="{r.uniform(14, 30):.0f}" ry="{r.uniform(10, 22):.0f}" fill="#2f4a2a"/>'
                    for x in [r.uniform(0, 1600) for _ in range(46)])
    polder = f'<rect y="{horizon}" width="{W}" height="{H - horizon}" fill="url(#polder)"/>'
    canal = (f'<path d="M0 600 C400 590 1200 590 1600 600 V636 C1200 626 400 626 0 636Z" fill="url(#canal)"/>'
             + "".join(f'<path d="M{r.uniform(0, 1600):.0f} {r.uniform(604, 630):.0f} h{r.uniform(20, 70):.0f}" stroke="#ffe7c4" stroke-width="2" opacity=".5"/>' for _ in range(24)))
    # tulip stripes running to a vanishing point on the horizon
    colors = ["#e8302a", "#ffd23d", "#ff8ad8", "#8a3dbf", "#ffffff", "#ff7a1a"]
    stripes = []
    vx, vy = 820, 600
    edges = list(range(-2600, 4200, 170))
    for i, (xa, xb) in enumerate(zip(edges, edges[1:])):
        c = colors[(i // 2) % len(colors)] if i % 2 == 0 else "#3f7a2a"
        stripes.append(f'<path d="M{vx} {vy} L{xa} {H} L{xb} {H}Z" fill="{c}"/>')
    field = (f'<g>{"".join(stripes)}</g>'
             f'<rect y="{vy}" width="{W}" height="40" fill="#5f8f3a" opacity=".6"/>')
    heads = "".join(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{2 + (y - 640) / 90:.1f}" ry="{3 + (y - 640) / 70:.1f}" fill="#fff" opacity=".18"/>'
                    for x, y in ((r.uniform(0, 1600), r.uniform(700, 990)) for _ in range(120)))
    distant = (windmill(560, 594, .22, 40) + windmill(1040, 592, .2, 10) + windmill(720, 590, .16, 70))
    right = f'<g class="R">{windmill(1360, 760, 1.15, 22)}</g>'
    railing = ('<path d="M-10 870 H520" stroke="#f2ead8" stroke-width="6"/><path d="M-10 830 H520" stroke="#f2ead8" stroke-width="4"/>'
               + "".join(f'<path d="M{x} 830 V900" stroke="#f2ead8" stroke-width="6"/>' for x in range(20, 520, 70)))
    path = '<path d="M-20 900 L540 900 L600 1000 L-20 1000Z" fill="#9a6a4a"/>' + "".join(
        f'<path d="M{x} 900 L{x + 20} 1000" stroke="#7a4a32" stroke-width="2"/>' for x in range(0, 560, 30))
    left = (f'<g class="L">{path}{railing}'
            + bicycle(60, 915, 1.0, "#1a1a1a", basket=["#e8302a", "#ffd23d", "#ff8ad8", "#e8302a"])
            + bicycle(300, 915, 1.0, "#4fb3a0") + '</g>')
    body = (f'<rect width="{W}" height="{H}" fill="url(#sky)"/><circle cx="800" cy="{horizon}" r="260" fill="url(#sunNL)"/>{clouds}'
            f'{polder}{trees}{distant}{canal}{field}{heads}{right}{left}'
            f'<rect width="{W}" height="{H}" fill="url(#veil)" opacity=".7"/>')
    return svg(defs + VEIL, body, "", "Dutch tulip fields and a canal at golden hour, with windmills and bicycles")


SCENES = {
    "new-york": new_york,
    "london": london,
    "santorini": santorini,
    "northern-lights": northern_lights,
    "new-year": new_year,
    "netherlands": netherlands,
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
            "// Generated by tools/build_places.py: edit that file, not this one.\n"
            f"export const {const} = `{escaped}`\n")
        print(f"{name}: {len(s)} chars")
