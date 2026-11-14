#!/usr/bin/env python3
"""Builds the six travel backdrop scenes (animated SVG) for the backdrops mod.

  space-shuttle   Earth from the flight deck: stars, drifting clouds, blinking panels
  mt-fuji         Fuji at dusk over a lake, pagoda, falling cherry petals
  paris           the Eiffel Tower at night: sparkle, sweeping beacon, lit windows
  rome            the Colosseum at golden hour, stone pines, swifts in flight
  swiss-alps      a moonlit Matterhorn, a chalet with smoke, falling snow
  tokyo-shibuya   the scramble crossing in the rain, neon, walkers crossing

Every scene is vector only (the desktop app draws no raster images in a
backdrop) with CSS animation, under the 131,072-character Svg limit. The
conversation column is frosted, so each landmark sits in a side gutter
(.L and .R groups), shifted inward on narrower windows so it stays in view.

Usage: python3 tools/build_travel.py hooks/scenes
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from smil import timeshift  # noqa: E402

W, H = 1600, 1000

BASE_CSS = """
.tw1{animation:tw 3.1s ease-in-out infinite}.tw2{animation:tw 4.3s ease-in-out -1.7s infinite}
.tw3{animation:tw 5.7s ease-in-out -3.2s infinite}.tw4{animation:tw 2.4s ease-in-out -.9s infinite}
@keyframes tw{0%,100%{opacity:1}50%{opacity:.25}}
.pulse{animation:pulse 6s ease-in-out infinite}@keyframes pulse{0%,100%{opacity:.65}50%{opacity:1}}
.bl1{animation:bl 1.3s steps(1) infinite}.bl2{animation:bl 2.1s steps(1) -.6s infinite}
.bl3{animation:bl 3.4s steps(1) -1.1s infinite}@keyframes bl{0%,100%{opacity:1}50%{opacity:.15}}
.drift{animation:drift 140s linear infinite}.drift2{animation:drift 95s linear -40s infinite}
@keyframes drift{from{transform:translateX(0)}to{transform:translateX(-1600px)}}
"""

REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"

# Visible part of the 1600 x 1000 slice root at each aspect ratio: below 1.6
# the sides are cropped around x=800, so the gutter groups move inward.
BANDS = [(1.4, 1.6), (1.2, 1.4), (1.0, 1.2), (0.75, 1.0), (0.0, 0.75)]


def shift_css():
    rules = []
    for lo, hi in BANDS:
        a = max(lo, 0.5)
        x1 = 800 + 500 * a
        dx = round(W - x1)
        mq = f"(max-aspect-ratio: {int(hi * 100) - 1}/100)" + (f" and (min-aspect-ratio: {int(lo * 100)}/100)" if lo else "")
        rules.append(f"@media {mq}{{.L{{transform:translateX({dx}px)}}.R{{transform:translateX({-dx}px)}}}}")
    return "".join(rules)


def rnd(seed):
    return random.Random(seed)


def stars(r, n, y0=0, y1=H, x0=0, x1=W, big=1.6, color="#fff"):
    out = []
    for i in range(n):
        x, y = r.uniform(x0, x1), r.uniform(y0, y1) ** 1 if False else r.uniform(y0, y1)
        rad = r.uniform(0.5, big)
        cls = f"tw{1 + i % 4}" if i % 3 else ""
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rad:.1f}" fill="{color}" opacity="{r.uniform(.45, 1):.2f}"'
                   + (f' class="{cls}"' if cls else "") + "/>")
    return "".join(out)


def svg(defs, body, css, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">'
            f"<title>{title}</title><style>{BASE_CSS}{css}{shift_css()}{REDUCED}</style>"
            f"<defs>{defs}</defs>{body}</svg>")


def lin(id_, stops, x2=0, y2=1):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a}"' if a is not None else "") + "/>"
                for o, c, a in [(t + (None,))[:3] for t in stops])
    return f'<linearGradient id="{id_}" x1="0" y1="0" x2="{x2}" y2="{y2}">{s}</linearGradient>'


def rad(id_, stops, cx=.5, cy=.5, r_=.5):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a}"' if a is not None else "") + "/>"
                for o, c, a in [(t + (None,))[:3] for t in stops])
    return f'<radialGradient id="{id_}" cx="{cx}" cy="{cy}" r="{r_}">{s}</radialGradient>'


VEIL = lin("veil", [(0, "#000", 0), (.3, "#000", .28), (.7, "#000", .28), (1, "#000", 0)], x2=1, y2=0)


# ------------------------------------------------------------- space shuttle
def space_shuttle():
    """Looking out of a shuttle window at Earth: a big globe in the right gutter."""
    r = rnd(1)
    cx, cy, R = 1470, 610, 520
    defs = (lin("sp", [(0, "#010208"), (.6, "#040a1c"), (1, "#081430")], x2=1, y2=0)
            + rad("ocean", [(0, "#4fa3ec"), (.45, "#1f63b4"), (.8, "#0d3a78"), (1, "#071d45")], cx=.32, cy=.4, r_=.75)
            + lin("night", [(0, "#000", 0), (.55, "#000", 0), (.78, "#000", .78), (1, "#000", .92)], x2=1, y2=.2)
            + rad("halo", [(.86, "#7fd0ff", 0), (.93, "#7fd0ff", .55), (1, "#7fd0ff", 0)])
            + rad("sunG", [(0, "#ffffff"), (.12, "#fff3c8", .9), (.4, "#ffd27a", .25), (1, "#ffd27a", 0)])
            + rad("vig", [(.62, "#000", 0), (1, "#000", .85)])
            + f'<clipPath id="globe"><circle cx="{cx}" cy="{cy}" r="{R}"/></clipPath>'
            + '<filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="3"/></filter>')

    def blob(x, y, s):
        pts = []
        for k in range(9):
            a = k / 9 * 6.283
            rr = s * r.uniform(.6, 1.25)
            pts.append((x + rr * 1.6 * __import__("math").cos(a), y + rr * __import__("math").sin(a)))
        return "M" + " L".join(f"{px:.0f} {py:.0f}" for px, py in pts) + "Z"

    lands = []
    for k in range(2):
        for _ in range(14):
            x = r.uniform(cx - R - 100, cx + R + 100) + k * 1400
            y = r.uniform(cy - R + 60, cy + R - 60)
            lands.append(f'<path d="{blob(x, y, r.uniform(55, 150))}" fill="{r.choice(["#4d8a52", "#6b8f45", "#a08c55", "#5a7d48"])}" '
                         f'opacity=".92" filter="url(#soft)"/>')
    clouds = []
    for k in range(2):
        for _ in range(40):
            x = r.uniform(cx - R - 100, cx + R + 100) + k * 1400
            y = r.uniform(cy - R, cy + R)
            clouds.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{r.uniform(25, 120):.0f}" ry="{r.uniform(5, 16):.0f}" '
                          f'fill="#fff" opacity="{r.uniform(.3, .7):.2f}" filter="url(#soft)"/>')
        # a cyclone
        sx, sy = cx - 120 + k * 1400, cy - 140
        clouds.append(f'<path d="M{sx} {sy} m-60 0 a60 40 0 1 1 60 40 a40 26 0 1 1 -30 -50 a20 14 0 1 1 20 18" '
                      f'fill="none" stroke="#fff" stroke-width="10" opacity=".6" filter="url(#soft)"/>')
    lights = "".join(f'<circle cx="{r.uniform(cx + R * .35, cx + R * .95):.0f}" cy="{r.uniform(cy - R * .7, cy + R * .7):.0f}" '
                     f'r="{r.uniform(.8, 2):.1f}" fill="#ffd27a" class="tw{1 + i % 4}"/>' for i in range(70))
    globe = (f'<g class="R">'
             f'<circle cx="{cx}" cy="{cy}" r="{R * 1.08:.0f}" fill="url(#halo)"/>'
             f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="url(#ocean)"/>'
             f'<g clip-path="url(#globe)"><g class="drift3">{"".join(lands)}</g><g class="drift4">{"".join(clouds)}</g>'
             f'<rect x="{cx - R}" y="{cy - R}" width="{2 * R}" height="{2 * R}" fill="url(#night)"/>{lights}</g>'
             f'<circle cx="{cx}" cy="{cy}" r="{R + 1}" fill="none" stroke="#bfe8ff" stroke-width="3" opacity=".75"/>'
             f'</g>')
    sat = ('<g class="sat"><g transform="translate(-120 150) rotate(-8)">'
           '<rect x="-34" y="-5" width="26" height="10" fill="#3b6fb0" stroke="#9cc3ff" stroke-width=".8"/>'
           '<rect x="8" y="-5" width="26" height="10" fill="#3b6fb0" stroke="#9cc3ff" stroke-width=".8"/>'
           '<rect x="-8" y="-7" width="16" height="14" rx="2" fill="#d9dde3"/><path d="M-8 0H-34M8 0H34" stroke="#888" stroke-width="1"/>'
           '<circle cx="0" cy="0" r="2" fill="#ff4d4d" class="bl1"/></g></g>')
    frame = (f'<rect width="{W}" height="{H}" fill="url(#vig)"/>'
             '<rect x="14" y="14" width="1572" height="972" rx="90" fill="none" stroke="#1a1f28" stroke-width="28"/>'
             '<rect x="28" y="28" width="1544" height="944" rx="78" fill="none" stroke="#3a4352" stroke-width="3"/>'
             + "".join(f'<circle cx="{x}" cy="{y}" r="5" fill="#2c333f" stroke="#505a6a"/>'
                       for x, y in ((120, 21), (400, 21), (1200, 21), (1480, 21), (120, 979), (400, 979), (1200, 979), (1480, 979),
                                    (21, 300), (21, 700), (1579, 300), (1579, 700))))
    panel = ('<g class="L"><rect x="60" y="760" width="230" height="150" rx="10" fill="#141821" stroke="#2f3744"/>'
             + "".join(f'<circle cx="{86 + c * 30}" cy="{790 + rw * 34}" r="4" fill="{r.choice(["#36d67a", "#ffb02e", "#4da3ff", "#ff4d4d"])}" '
                       f'class="bl{1 + (c + rw) % 3}"/>' for rw in range(4) for c in range(7))
             + '</g>')
    checklist = ('<g class="L"><g class="float"><rect x="150" y="300" width="70" height="92" rx="5" fill="#e9e4d4" '
                 'transform="rotate(-12 185 346)"/>'
                 + "".join(f'<path d="M162 {320 + i * 12} h44" stroke="#8b8676" stroke-width="3" transform="rotate(-12 185 346)"/>'
                           for i in range(6))
                 + '</g></g>')
    css = (".float{animation:float 18s ease-in-out infinite;transform-box:fill-box;transform-origin:center}"
           "@keyframes float{0%,100%{transform:translate(0,0) rotate(0)}50%{transform:translate(18px,-26px) rotate(14deg)}}"
           ".drift3{animation:spin 240s linear infinite}.drift4{animation:spin 150s linear infinite}"
           "@keyframes spin{from{transform:translateX(0)}to{transform:translateX(-1400px)}}"
           ".sat{animation:sat 60s linear infinite}@keyframes sat{from{transform:translate(0,0)}to{transform:translate(1900px,-60px)}}")
    body = (f'<rect width="{W}" height="{H}" fill="url(#sp)"/>{stars(r, 220, 0, H)}'
            f'<g class="L"><circle cx="160" cy="140" r="220" fill="url(#sunG)" class="pulse"/></g>'
            f'{sat}{globe}{checklist}{panel}{frame}')
    return svg(defs, body, css, "Earth seen from a space shuttle window")


# ------------------------------------------------------------------- mt fuji
def mt_fuji():
    r = rnd(2)
    defs = (lin("sky", [(0, "#0e1433"), (.38, "#35285a"), (.6, "#a24f74"), (.72, "#e8836c"), (.8, "#f5b680")])
            + lin("fuji", [(0, "#6a5a8c"), (.5, "#3b3260"), (1, "#221d3c")])
            + lin("snow", [(0, "#ffffff"), (.6, "#fde3ec"), (1, "#e9b9d0")])
            + lin("lake", [(0, "#3a2c55"), (.4, "#1b1733"), (1, "#0b0a18")])
            + lin("pag", [(0, "#d24a33"), (1, "#8f2a1f")], x2=1, y2=0)
            + rad("sun", [(0, "#ffd9a0", .9), (1, "#ffd9a0", 0)]))
    fuji = ('M740 720 C930 610 1140 430 1222 372 Q1262 344 1302 372 C1384 430 1594 610 1784 720 Z')
    snow = ('M1150 432 C1185 405 1210 382 1222 372 Q1262 344 1302 372 C1316 382 1340 405 1374 432 '
            'L1352 446 L1336 428 L1318 458 L1298 432 L1280 470 L1262 438 L1246 466 L1228 432 L1206 455 L1190 432 L1170 450 Z')
    mountain = (f'<path d="{fuji}" fill="url(#fuji)"/><path d="{snow}" fill="url(#snow)"/>'
                f'<path d="{snow}" fill="#ff9fbf" opacity=".35" class="pulse"/>')
    reflection = (f'<g opacity=".28" transform="translate(0 1440) scale(1 -1)">{mountain}</g>')
    hills = ('<path d="M0 700 C180 660 360 690 520 670 C700 650 860 700 1040 690 C1240 680 1420 700 1600 690 V740 H0Z" fill="#231b3a"/>')
    shimmer = "".join(f'<path d="M{x:.0f} {y:.0f} h{r.uniform(40, 140):.0f}" stroke="#f3b4a0" stroke-width="2" '
                      f'opacity=".35" class="tw{1 + i % 4}"/>'
                      for i, (x, y) in enumerate((r.uniform(600, 1600), r.uniform(745, 900)) for _ in range(26)))
    # five-storey pagoda (left)
    tiers = []
    for i in range(5):
        y = 770 - i * 72
        w = 200 - i * 26
        cx = 250
        tiers.append(f'<rect x="{cx - w / 2 + 22}" y="{y - 52}" width="{w - 44}" height="52" fill="url(#pag)"/>'
                     f'<rect x="{cx - w / 2 + 34}" y="{y - 40}" width="{(w - 68)}" height="10" fill="#ffcf7a" opacity=".55" class="pulse"/>'
                     f'<path d="M{cx - w / 2 - 14} {y - 48} Q{cx} {y - 76} {cx + w / 2 + 14} {y - 48} L{cx + w / 2 - 6} {y - 58} '
                     f'Q{cx} {y - 82} {cx - w / 2 + 6} {y - 58} Z" fill="#2b1d2e"/>')
    pagoda = (f'<g class="L">{"".join(tiers)}<path d="M250 395 V300" stroke="#2b1d2e" stroke-width="6"/>'
              + "".join(f'<circle cx="250" cy="{312 + i * 14}" r="7" fill="none" stroke="#2b1d2e" stroke-width="3"/>' for i in range(5))
              + '<path d="M0 772 C90 752 180 752 260 758 C380 768 520 800 640 880 V1000 H0Z" fill="#160f22"/></g>')
    # cherry branch from the top-left corner, blossoms and falling petals
    branch = ('<path d="M-20 60 C120 90 230 70 330 130 C390 165 440 150 520 190 M180 85 C210 140 200 190 240 230 '
              'M330 130 C350 80 400 60 450 70" stroke="#3a2230" stroke-width="12" fill="none" stroke-linecap="round"/>')
    blossoms = "".join(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r.uniform(5, 12):.0f}" '
                       f'fill="{r.choice(["#ffc1d6", "#ffadc8", "#ffd6e5", "#f791b4"])}" opacity="{r.uniform(.75, 1):.2f}"/>'
                       for x, y in ((r.uniform(-10, 540), r.uniform(30, 250)) for _ in range(150))
                       if y < 120 + 0.35 * x or x < 300)
    petals = "".join(f'<g class="pt{1 + i % 4}" ><ellipse cx="{r.uniform(-100, 1500):.0f}" cy="-20" rx="5" ry="3" '
                     f'fill="#ffc1d6" transform="rotate({r.uniform(0, 180):.0f})" opacity=".9"/></g>'
                     for i in range(36))
    css = (".pt1{animation:fall 16s linear infinite}.pt2{animation:fall 21s linear -7s infinite}"
           ".pt3{animation:fall 13s linear -4s infinite}.pt4{animation:fall 25s linear -15s infinite}"
           "@keyframes fall{from{transform:translate(0,-40px)}50%{transform:translate(120px,520px)}to{transform:translate(260px,1080px)}}")
    clouds = "".join(f'<ellipse cx="{r.uniform(0, 3200):.0f}" cy="{r.uniform(380, 600):.0f}" rx="{r.uniform(90, 220):.0f}" '
                     f'ry="{r.uniform(8, 18):.0f}" fill="#f6b3a3" opacity="{r.uniform(.12, .3):.2f}"/>' for _ in range(12))
    body = (f'<rect width="{W}" height="{H}" fill="url(#sky)"/>{stars(r, 70, 0, 330)}'
            f'<circle cx="760" cy="700" r="260" fill="url(#sun)"/><g class="drift">{clouds}</g>'
            f'<g class="R">{mountain}</g>{hills}<rect y="720" width="{W}" height="280" fill="url(#lake)"/>'
            f'<g class="R">{reflection}</g>{shimmer}{pagoda}<g class="L">{branch}{blossoms}</g>{petals}'
            f'<rect width="{W}" height="{H}" fill="url(#veil)" opacity=".7"/>')
    return svg(defs + VEIL, body, css, "Mount Fuji at dusk over a lake, a pagoda and falling cherry petals")


# --------------------------------------------------------------------- paris
def paris():
    r = rnd(3)
    defs = (lin("sky", [(0, "#040822"), (.5, "#101d52"), (.82, "#2b3577"), (1, "#5a3d6a")])
            + lin("gold", [(0, "#ffd27a"), (.5, "#e8a33a"), (1, "#b06a1c")], x2=1, y2=0)
            + rad("tglow", [(0, "#ffb347", .45), (1, "#ffb347", 0)])
            + rad("moon", [(0, "#fffbe8"), (.6, "#fff3c4", .5), (1, "#fff3c4", 0)])
            + lin("beam", [(0, "#fff6d0", .55), (1, "#fff6d0", 0)], x2=1, y2=0)
            + lin("river", [(0, "#0d1435"), (1, "#05081a")])
            + '<pattern id="lat" width="14" height="14" patternUnits="userSpaceOnUse">'
              '<path d="M0 0L14 14M14 0L0 14" stroke="#6b3d10" stroke-width="1.6" opacity=".55"/></pattern>')
    tower = ('M1150 900 L1240 640 L1360 640 L1450 900 L1410 900 Q1300 700 1190 900 Z '
             'M1248 625 L1352 625 L1328 474 L1272 474 Z M1279 460 L1321 460 L1306 205 L1294 205 Z')
    platforms = ('<rect x="1222" y="622" width="156" height="20" fill="url(#gold)"/>'
                 '<rect x="1262" y="458" width="76" height="16" fill="url(#gold)"/>'
                 '<rect x="1289" y="178" width="22" height="28" fill="url(#gold)"/>'
                 '<path d="M1300 178 V128" stroke="#ffd27a" stroke-width="3"/>')
    sparkle = "".join(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r.uniform(1.2, 2.6):.1f}" fill="#fff" class="sp{1 + i % 4}"/>'
                      for i, (x, y) in enumerate(_tower_points(r, 90)))
    beacon = ('<g class="beacon"><path d="M1300 140 L2300 60 L2300 230 Z" fill="url(#beam)"/>'
              '<path d="M1300 140 L300 60 L300 230 Z" fill="url(#beam)" transform="rotate(180 1300 140) scale(1 1)" opacity=".0"/></g>')
    tower_g = (f'<g class="R"><ellipse cx="1300" cy="560" rx="260" ry="460" fill="url(#tglow)" class="pulse"/>{beacon}'
               f'<path d="{tower}" fill="url(#gold)" fill-rule="evenodd"/><path d="{tower}" fill="url(#lat)" fill-rule="evenodd"/>'
               f'{platforms}{sparkle}<circle cx="1300" cy="140" r="6" fill="#fff" class="pulse"/></g>')
    # Haussmann rooftops on the left with lit windows
    b = []
    x = -10
    while x < 470:
        w = r.uniform(90, 140)
        top = r.uniform(560, 620)
        b.append(f'<path d="M{x:.0f} 1000 V{top + 40:.0f} L{x + 14:.0f} {top:.0f} H{x + w - 14:.0f} L{x + w:.0f} {top + 40:.0f} V1000Z" fill="#0b0f26"/>')
        for c in range(r.randint(1, 3)):
            cx = x + r.uniform(16, w - 26)
            b.append(f'<rect x="{cx:.0f}" y="{top - 26:.0f}" width="10" height="28" fill="#0b0f26"/>')
        for row in range(5):
            for col in range(int(w // 26)):
                wx, wy = x + 10 + col * 26, top + 52 + row * 62
                if r.random() < .45:
                    cls = f' class="tw{1 + (row + col) % 4}"' if r.random() < .15 else ""
                    b.append(f'<rect x="{wx:.0f}" y="{wy:.0f}" width="12" height="22" fill="#ffcf7e" opacity="{r.uniform(.55, .95):.2f}"{cls}/>')
        x += w
    lamps = "".join(f'<circle cx="{lx}" cy="905" r="14" fill="#ffd27a" opacity=".25"/><circle cx="{lx}" cy="905" r="4" fill="#fff1c4"/>'
                    f'<path d="M{lx} 909 V960" stroke="#0b0f26" stroke-width="3"/>' for lx in (60, 210, 360))
    river = (f'<rect y="930" width="{W}" height="70" fill="url(#river)"/>'
             + "".join(f'<path d="M{x:.0f} {y:.0f} h{r.uniform(20, 70):.0f}" stroke="#ffcf7e" stroke-width="2" opacity=".45" class="tw{1 + i % 4}"/>'
                       for i, (x, y) in enumerate((r.uniform(0, 1600), r.uniform(940, 995)) for _ in range(30))))
    css = (".sp1{animation:sp .9s steps(1) infinite}.sp2{animation:sp 1.3s steps(1) -.4s infinite}"
           ".sp3{animation:sp .7s steps(1) -.2s infinite}.sp4{animation:sp 1.1s steps(1) -.8s infinite}"
           "@keyframes sp{0%,100%{opacity:1}50%{opacity:0}}"
           ".beacon{transform-box:view-box;transform-origin:1300px 140px;animation:beam 14s linear infinite}"
           "@keyframes beam{from{transform:rotate(0)}to{transform:rotate(360deg)}}")
    body = (f'<rect width="{W}" height="{H}" fill="url(#sky)"/>{stars(r, 110, 0, 600)}'
            f'<g class="L"><circle cx="300" cy="170" r="120" fill="url(#moon)"/><circle cx="300" cy="170" r="34" fill="#fffbe8"/></g>'
            f'{tower_g}<g class="L">{"".join(b)}{lamps}</g>{river}'
            f'<rect width="{W}" height="{H}" fill="url(#veil)" opacity=".8"/>')
    return svg(defs + VEIL, body, css, "The Eiffel Tower sparkling at night over Paris rooftops")


def _tower_points(r, n):
    pts = []
    while len(pts) < n:
        y = r.uniform(190, 890)
        if y > 640:
            half = 60 + (y - 640) / 260 * 90
        elif y > 474:
            half = 28 + (y - 474) / 151 * 24
        else:
            half = 6 + (y - 205) / 255 * 16
        pts.append((1300 + r.uniform(-half, half), y))
    return pts


# ---------------------------------------------------------------------- rome
def rome():
    r = rnd(4)
    defs = (lin("sky", [(0, "#1a1838"), (.42, "#5a3a6c"), (.7, "#d0704f"), (.86, "#f3ad66")])
            + lin("stone", [(0, "#e2b98a"), (1, "#a77a52")])
            + lin("stoneD", [(0, "#a07650"), (1, "#6e4c34")])
            + rad("arch", [(0, "#ffcf7a"), (1, "#a8521f")], cy=.7)
            + rad("sun", [(0, "#ffe2a8", .95), (1, "#ffe2a8", 0)]))
    cx0 = 1310

    def dy(x):
        return 0.00016 * (x - cx0) ** 2

    tiers = []
    top_full, x_l, x_r = 470, 960, 1640
    tier_h = 104
    # facade body: four tiers on the right, a ruined two-tier edge on the left
    for t in range(4):
        y0 = 860 - (t + 1) * tier_h
        xa = x_l + (t >= 2) * 170 + (t == 3) * 60
        pts_top = [(x, y0 + dy(x)) for x in range(int(xa), x_r + 1, 20)]
        pts_bot = [(x, y0 + tier_h + dy(x)) for x in range(x_r, int(xa) - 1, -20)]
        d = "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts_top + pts_bot) + "Z"
        tiers.append(f'<path d="{d}" fill="url(#stone)"/>')
        tiers.append(f'<path d="M{xa:.0f} {y0 + dy(xa):.0f} H{x_r}" stroke="#7a5638" stroke-width="5" opacity=".6"/>')
        # arches or attic windows
        step = 46
        x = xa + 18
        while x < x_r - 20:
            yb = y0 + tier_h - 10 + dy(x)
            if t < 3:
                aw, ah = 28, 66
                tiers.append(f'<path d="M{x:.0f} {yb:.0f} V{yb - ah + aw / 2:.0f} A{aw / 2} {aw / 2} 0 0 1 {x + aw:.0f} {yb - ah + aw / 2:.0f} V{yb:.0f}Z" '
                             f'fill="url(#arch)" class="glow{1 + int(x) % 3}"/>')
            else:
                tiers.append(f'<rect x="{x:.0f}" y="{yb - 50:.0f}" width="14" height="22" fill="#5b3b28"/>')
            x += step
    ruin = ('<path d="M960 ' + f'{860 - 2 * tier_h + dy(960):.0f}' + ' L1000 300 L1040 450 L1080 360 L1130 ' f'{860 - 3 * tier_h + dy(1130):.0f}'
            ' L1130 1000 L960 1000Z" fill="url(#stoneD)" opacity="0"/>')
    colosseum = (f'<g class="R">{"".join(tiers)}{ruin}'
                 f'<path d="M940 860 H1640 V1000 H940Z" fill="#2a1d24"/></g>')
    # stone pines and cypresses on the left
    def pine(x, y, s):
        canopy = "".join(f'<ellipse cx="{x + r.uniform(-90, 90) * s:.0f}" cy="{y + r.uniform(-18, 14) * s:.0f}" '
                         f'rx="{r.uniform(50, 90) * s:.0f}" ry="{r.uniform(18, 30) * s:.0f}" fill="#1b1622"/>' for _ in range(9))
        return (f'<path d="M{x - 6 * s:.0f} 1000 C{x - 10 * s:.0f} {y + 200 * s:.0f} {x + 30 * s:.0f} {y + 90 * s:.0f} {x:.0f} {y:.0f}" '
                f'stroke="#1b1622" stroke-width="{12 * s:.0f}" fill="none"/>{canopy}')
    def cypress(x, h):
        return f'<path d="M{x} 1000 C{x - 22} {1000 - h * .5} {x - 14} {1000 - h * .85} {x} {1000 - h} C{x + 14} {1000 - h * .85} {x + 22} {1000 - h * .5} {x} 1000Z" fill="#17131d"/>'
    trees = (f'<g class="L">{pine(190, 520, 1.25)}{pine(420, 640, .85)}{cypress(70, 470)}{cypress(560, 380)}'
             f'<path d="M0 900 C200 870 420 880 640 910 V1000 H0Z" fill="#17131d"/></g>')
    birds = "".join(f'<path d="M{bx:.0f} {by:.0f} q6 -6 12 0 q6 -6 12 0" stroke="#1d1520" stroke-width="2.4" fill="none" class="flap"/>'
                    for bx, by in ((r.uniform(0, 260), r.uniform(0, 140)) for _ in range(16)))
    flock = f'<g class="fly"><g transform="translate(0 220)">{birds}</g></g><g class="fly2"><g transform="translate(200 120)">{birds}</g></g>'
    clouds = "".join(f'<ellipse cx="{r.uniform(0, 3200):.0f}" cy="{r.uniform(120, 520):.0f}" rx="{r.uniform(120, 260):.0f}" '
                     f'ry="{r.uniform(8, 16):.0f}" fill="#f7a986" opacity="{r.uniform(.15, .35):.2f}"/>' for _ in range(12))
    css = (".glow1{animation:pulse 5s ease-in-out infinite}.glow2{animation:pulse 7s ease-in-out -2s infinite}"
           ".glow3{animation:pulse 6s ease-in-out -4s infinite}"
           ".fly{animation:fly 38s linear infinite}.fly2{animation:fly 52s linear -20s infinite}"
           "@keyframes fly{from{transform:translate(-400px,40px)}50%{transform:translate(800px,-30px)}to{transform:translate(2000px,30px)}}"
           ".flap{animation:flap .5s ease-in-out infinite;transform-box:fill-box;transform-origin:center}"
           "@keyframes flap{0%,100%{transform:scaleY(1)}50%{transform:scaleY(-.6)}}")
    body = (f'<rect width="{W}" height="{H}" fill="url(#sky)"/>{stars(r, 30, 0, 200)}'
            f'<circle cx="700" cy="830" r="300" fill="url(#sun)"/><g class="drift">{clouds}</g>{flock}'
            f'{colosseum}{trees}<rect width="{W}" height="{H}" fill="url(#veil)" opacity=".7"/>')
    return svg(defs + VEIL, body, css, "The Colosseum in Rome at golden hour with stone pines and swifts")


# ---------------------------------------------------------------- swiss alps
def swiss_alps():
    r = rnd(5)
    defs = (lin("sky", [(0, "#040818"), (.5, "#0e1c42"), (.78, "#24406e"), (1, "#3a5a8a")])
            + lin("rock", [(0, "#c9d8ff"), (.35, "#7f94c8"), (1, "#2b3a63")], x2=1, y2=.3)
            + lin("far", [(0, "#5a6f9e"), (1, "#26365e")])
            + lin("mid", [(0, "#33466f"), (1, "#162142")])
            + rad("moon", [(0, "#f4f7ff"), (.5, "#dfe8ff", .35), (1, "#dfe8ff", 0)])
            + lin("snowg", [(0, "#eef3ff"), (1, "#a9b9df")]))
    matter = ('M980 760 L1150 470 L1205 330 L1232 300 L1248 248 L1262 262 L1296 300 L1330 380 L1420 520 L1560 760 Z')
    matter_snow = ('M1150 470 L1205 330 L1232 300 L1248 248 L1262 262 L1296 300 L1330 380 L1300 400 L1270 360 '
                   'L1252 420 L1228 380 L1196 450 Z')
    far = ('M0 700 L120 560 L210 610 L330 500 L450 600 L560 540 L700 640 L820 580 L960 660 L1600 640 V800 H0Z')
    mid = ('M0 780 L160 640 L260 700 L380 620 L520 720 L660 680 L800 760 L1000 700 L1180 760 L1360 690 L1600 740 V860 H0Z')
    snowcaps = ('M120 560 L150 600 L132 596 L110 610 L96 590 Z M330 500 L370 545 L350 540 L326 556 L304 532 Z '
                'M560 540 L590 572 L570 570 L548 580 L534 562 Z')
    mountains = (f'<path d="{far}" fill="url(#far)"/><path d="{snowcaps}" fill="url(#snowg)" opacity=".85"/>'
                 f'<g class="R"><path d="{matter}" fill="url(#rock)"/><path d="{matter_snow}" fill="#eef3ff" opacity=".9"/>'
                 f'<path d="M1248 248 L1262 262 L1296 300 L1330 380 L1420 520 L1560 760 L1380 760 Z" fill="#1d2a4d" opacity=".55"/></g>'
                 f'<path d="{mid}" fill="url(#mid)"/>')
    def fir(x, y, s):
        return (f'<path d="M{x} {y - 90 * s:.0f} L{x + 34 * s:.0f} {y - 20 * s:.0f} L{x + 14 * s:.0f} {y - 22 * s:.0f} '
                f'L{x + 44 * s:.0f} {y + 20 * s:.0f} L{x - 44 * s:.0f} {y + 20 * s:.0f} L{x - 14 * s:.0f} {y - 22 * s:.0f} '
                f'L{x - 34 * s:.0f} {y - 20 * s:.0f}Z" fill="#0b1426"/>'
                f'<path d="M{x} {y - 90 * s:.0f} L{x + 14 * s:.0f} {y - 66 * s:.0f} L{x - 14 * s:.0f} {y - 66 * s:.0f}Z" fill="#dfe8ff" opacity=".8"/>')
    firs_l = "".join(fir(x, 900 + r.uniform(-20, 30), r.uniform(.8, 1.4)) for x in (30, 90, 430, 500, 560))
    firs_r = "".join(fir(x, 900 + r.uniform(-20, 30), r.uniform(.8, 1.5)) for x in (1120, 1190, 1480, 1550))
    chalet = ('<g class="L"><path d="M150 880 V760 H370 V880Z" fill="#3b2418"/>'
              '<path d="M120 770 L260 660 L400 770 L380 778 L260 684 L140 778Z" fill="#eef3ff"/>'
              '<path d="M140 778 L260 684 L380 778 V790 L260 700 L140 790Z" fill="#24150e"/>'
              + "".join(f'<rect x="{x}" y="{y}" width="34" height="34" fill="#ffc46b" class="pulse"/>'
                        f'<path d="M{x + 17} {y} V{y + 34} M{x} {y + 17} H{x + 34}" stroke="#3b2418" stroke-width="3"/>'
                        for x, y in ((180, 800), (300, 800), (243, 730)))
              + '<rect x="330" y="680" width="22" height="50" fill="#2a1a12"/>'
              + "".join(f'<circle cx="341" cy="670" r="{8 + i * 3}" fill="#c9d3ea" opacity=".35" class="smoke s{i}"/>' for i in range(5))
              + '<path d="M0 880 C200 860 420 870 640 890 V1000 H0Z" fill="#dfe8ff"/>'
              + f'{firs_l}</g>')
    snow = []
    for layer, (n, rmax, cls) in enumerate(((60, 1.6, "fa"), (45, 2.4, "fb"), (25, 3.4, "fc"))):
        flakes = "".join(f'<circle cx="{r.uniform(0, 1600):.0f}" cy="{r.uniform(-1000, 0):.0f}" r="{r.uniform(.8, rmax):.1f}" fill="#fff" opacity=".85"/>'
                         for _ in range(n))
        snow.append(f'<g class="{cls}">{flakes}<g transform="translate(0 1000)">{flakes}</g></g>')
    css = (".fa{animation:snow 34s linear infinite}.fb{animation:snow 22s linear infinite}.fc{animation:snow 14s linear infinite}"
           "@keyframes snow{from{transform:translate(0,0)}to{transform:translate(-120px,1000px)}}"
           ".smoke{animation:smoke 6s ease-out infinite;transform-box:fill-box;transform-origin:center}"
           ".s1{animation-delay:-1.2s}.s2{animation-delay:-2.4s}.s3{animation-delay:-3.6s}.s4{animation-delay:-4.8s}"
           "@keyframes smoke{from{transform:translate(0,0) scale(.6);opacity:.45}to{transform:translate(40px,-140px) scale(2.2);opacity:0}}")
    body = (f'<rect width="{W}" height="{H}" fill="url(#sky)"/>{stars(r, 150, 0, 560)}'
            f'<g class="R"><circle cx="1420" cy="150" r="130" fill="url(#moon)"/><circle cx="1420" cy="150" r="38" fill="#f4f7ff"/></g>'
            f'{mountains}<path d="M0 860 C300 840 700 850 1000 870 C1250 880 1450 860 1600 870 V1000 H0Z" fill="#c7d3ee"/>'
            f'<g class="R">{firs_r}</g>{chalet}{"".join(snow)}'
            f'<rect width="{W}" height="{H}" fill="url(#veil)" opacity=".7"/>')
    return svg(defs + VEIL, body, css, "A moonlit Matterhorn above a snowy chalet with falling snow")


# ------------------------------------------------------------- tokyo shibuya
def tokyo_shibuya():
    r = rnd(6)
    defs = (lin("sky", [(0, "#06050e"), (.6, "#170f2e"), (1, "#3a1f4f")])
            + lin("road", [(0, "#14121f"), (1, "#07060c")])
            + '<filter id="neon" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4" result="b"/>'
              '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    neon = ["#ff3d8b", "#3de1ff", "#ffd23d", "#9b5cff", "#43ff9a"]

    def building(x, w, top, side):
        out = [f'<rect x="{x:.0f}" y="{top:.0f}" width="{w:.0f}" height="{820 - top:.0f}" fill="#0d0b18"/>']
        for row in range(int((780 - top) // 22)):
            for col in range(int((w - 12) // 16)):
                if r.random() < .38:
                    c = r.choice(["#ffe2a8", "#bfe6ff", "#ffd0f0"])
                    out.append(f'<rect x="{x + 8 + col * 16:.0f}" y="{top + 12 + row * 22:.0f}" width="9" height="12" fill="{c}" opacity="{r.uniform(.35, .85):.2f}"/>')
        return "".join(out)

    left = [building(x, w, t, "L") for x, w, t in ((-20, 150, 200), (130, 120, 330), (250, 170, 120), (420, 110, 400))]
    right = [building(x, w, t, "R") for x, w, t in ((1160, 120, 380), (1280, 170, 90), (1450, 170, 250))]
    # big screens with colour cycling, vertical neon signs
    screens = ('<g class="L"><rect x="268" y="180" width="134" height="96" fill="#000"/>'
               '<rect x="272" y="184" width="126" height="88" fill="#ff3d8b" class="scrA"/>'
               '<rect x="272" y="184" width="126" height="88" fill="#3de1ff" class="scrB"/>'
               '<rect x="272" y="184" width="126" height="88" fill="#ffd23d" class="scrC"/>'
               '<path d="M290 250 h90 M290 236 h60" stroke="#fff" stroke-width="5" opacity=".7"/></g>'
               '<g class="R"><rect x="1298" y="150" width="134" height="160" fill="#000"/>'
               '<rect x="1302" y="154" width="126" height="152" fill="#9b5cff" class="scrB"/>'
               '<rect x="1302" y="154" width="126" height="152" fill="#43ff9a" class="scrC"/>'
               '<rect x="1302" y="154" width="126" height="152" fill="#ff3d8b" class="scrA"/>'
               '<circle cx="1365" cy="230" r="36" fill="#fff" opacity=".55"/></g>')
    signs = []
    for side, x, y, word, col in (("L", 140, 360, "ラーメン", "#ff3d8b"), ("L", 432, 430, "カラオケ", "#3de1ff"),
                                  ("R", 1172, 410, "渋谷", "#ffd23d"), ("R", 1580, 300, "ネオン", "#43ff9a")):
        h = 46 * len(word) + 20
        signs.append(f'<g class="{side}"><rect x="{x - 4}" y="{y}" width="44" height="{h}" rx="6" fill="#0a0812" stroke="{col}" '
                     f'stroke-width="3" filter="url(#neon)" class="bl{1 + len(signs) % 3}"/>'
                     + "".join(f'<text x="{x + 18}" y="{y + 44 + i * 46}" font-size="36" text-anchor="middle" fill="{col}" '
                               f'font-family="sans-serif" filter="url(#neon)">{ch}</text>' for i, ch in enumerate(word))
                     + "</g>")
    # the crossing: wet road, zebra stripes, reflections
    road = (f'<rect y="820" width="{W}" height="180" fill="url(#road)"/>'
            + "".join(f'<path d="M{x} 870 L{x + 30} 870 L{x + 40} 930 L{x + 8} 930Z" fill="#e8e6f0" opacity=".32"/>'
                      for x in range(40, 1600, 64))
            + "".join(f'<rect x="{x:.0f}" y="830" width="{r.uniform(8, 26):.0f}" height="{r.uniform(60, 160):.0f}" '
                      f'fill="{r.choice(neon)}" opacity=".12"/>' for i, x in enumerate(r.choice([r.uniform(0, 520), r.uniform(1150, 1600)]) for _ in range(16))))
    # walkers with umbrellas crossing both ways
    walkers = []
    for i in range(26):
        y = r.uniform(850, 960)
        x = r.uniform(-200, 1600)
        col = r.choice(["#ff3d8b", "#3de1ff", "#ffd23d", "#f4f1ff", "#9b5cff", "#1e1b2c"])
        cls = r.choice(["wA", "wB", "wC", "wD"])
        walkers.append(f'<g class="{cls}"><g transform="translate({x:.0f} {y:.0f})"><rect x="-4" y="0" width="8" height="22" rx="3" fill="#0b0a12"/>'
                       f'<path d="M-15 2 Q0 -16 15 2Z" fill="{col}" opacity=".9"/></g></g>')
    signals = ('<g class="L"><rect x="560" y="740" width="18" height="40" rx="3" fill="#111"/><circle cx="569" cy="770" r="6" fill="#43ff9a" class="bl1"/></g>'
               '<g class="R"><rect x="1040" y="740" width="18" height="40" rx="3" fill="#111"/><circle cx="1049" cy="770" r="6" fill="#43ff9a" class="bl1"/></g>')
    drops = "".join(f'<path d="M{r.uniform(0, 1700):.0f} {r.uniform(-1000, 0):.0f} l-6 22" stroke="#cfd8ff" stroke-width="1.2" opacity=".35"/>'
                    for _ in range(140))
    rain = f'<g class="rain">{drops}<g transform="translate(0 1000)">{drops}</g></g>'
    css = (".scrA{animation:scr 9s steps(1) infinite}.scrB{animation:scr 9s steps(1) -3s infinite}.scrC{animation:scr 9s steps(1) -6s infinite}"
           "@keyframes scr{0%{opacity:1}33%{opacity:0}100%{opacity:0}}"
           ".wA{animation:walkR 24s linear infinite}.wB{animation:walkR 31s linear -12s infinite}"
           ".wC{animation:walkL 27s linear -5s infinite}.wD{animation:walkL 35s linear -20s infinite}"
           "@keyframes walkR{from{transform:translateX(-300px)}to{transform:translateX(1900px)}}"
           "@keyframes walkL{from{transform:translateX(1900px)}to{transform:translateX(-300px)}}"
           ".rain{animation:rain 1.6s linear infinite}@keyframes rain{from{transform:translate(0,0)}to{transform:translate(-90px,1000px)}}")
    body = (f'<rect width="{W}" height="{H}" fill="url(#sky)"/>'
            f'<g class="L">{"".join(left)}</g><g class="R">{"".join(right)}</g>{screens}{"".join(signs)}{signals}'
            f'{road}{"".join(walkers)}{rain}<rect width="{W}" height="{H}" fill="url(#veil)" opacity=".7"/>')
    return svg(defs + VEIL, body, css, "Shibuya crossing in Tokyo at night in the rain with neon signs")


SCENES = {
    "space-shuttle": space_shuttle,
    "mt-fuji": mt_fuji,
    "paris": paris,
    "rome": rome,
    "swiss-alps": swiss_alps,
    "tokyo-shibuya": tokyo_shibuya,
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
            "// Generated by tools/build_travel.py: edit that file, not this one.\n"
            f"export const {const} = `{escaped}`\n")
        print(f"{name}: {len(s)} chars")
