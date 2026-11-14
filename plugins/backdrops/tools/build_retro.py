#!/usr/bin/env python3
"""Builds the six retro backdrop scenes (SVG) for the backdrops mod.

  matrix            falling green code
  retro-80s         a synthwave sunset over a neon grid, with palms
  windows-xp        rolling hills under a blue sky, desktop icons, a blue taskbar
  windows-98        a teal desktop, a classic grey window and taskbar
  macintosh-retro   a dithered desktop, menu bar, pinstriped window, disk icons
  linux             a cartoon penguin on an ice floe, an aurora, a terminal window

Original homages to an era: no company logos, wallpapers or icon artwork.
Shares its helpers with build_travel.py (gutter shifting, gradients, the
var(--t) time offset).

Usage: python3 tools/build_retro.py hooks/scenes
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_travel import H, VEIL, W, lin, rad, rnd, stars, svg  # noqa: E402
from smil import timeshift  # noqa: E402

def pinned(scene, edge):
    """Pin a scene to its bottom (a taskbar) or top (a menu bar) edge.

    The root is a 1600 x 1000 `slice`: a box wider than 1.6 loses part of its
    height. Centred, that loss is split between top and bottom, so a bar drawn
    at an edge floats inside a wide window. Pinned, the whole loss comes off
    the other edge and the bar stays flush with the window at every width;
    .T (with a bottom pin) or .B (with a top pin) then moves the items at that
    other edge into view.
    """
    align = "xMidYMax" if edge == "bottom" else "xMidYMin"
    rules = []
    edges = [round(1.6 + 0.1 * i, 1) for i in range(19)]  # 1.6, 1.7 ... 3.4, then anything wider
    for lo, hi in list(zip(edges, edges[1:])) + [(edges[-1], 9.0)]:
        tallest = W / (hi if hi < 9 else 3.4)  # the visible height at the band's widest box
        mq = f"(min-aspect-ratio: {int(lo * 100)}/100)" + (f" and (max-aspect-ratio: {int(hi * 100) - 1}/100)" if hi < 9 else "")
        if edge == "bottom":
            # top items drop by the whole crop, so the topmost stays in view
            rule = f".T{{transform:translateY({round(H - tallest)}px)}}"
        else:
            # bottom items (lowest edge near y=880) rise only as far as they must
            rule = f".B{{transform:translateY({-max(0, round(880 + 20 - tallest))}px)}}"
        rules.append(f"@media {mq}{{{rule}}}")
    scene = scene.replace('preserveAspectRatio="xMidYMid slice"', f'preserveAspectRatio="{align} slice"', 1)
    return scene.replace("</style>", "".join(rules) + "</style>", 1)


UI_FONT = "'Tahoma', 'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
MAC_FONT = "'Chicago', 'Charcoal', 'Geneva', 'Helvetica Neue', Arial, sans-serif"


# --------------------------------------------------------------------- matrix
def matrix():
    r = rnd(11)
    glyphs = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ０１２３４５６７８９"
    defs = (rad("mglow", [(0, "#0b3d1a"), (1, "#000")], cy=.5, r_=.75)
            + lin("fade", [(0, "#00ff66", 0), (.7, "#00ff66", .55), (1, "#5dff9a", 1)])
            + '<filter id="mg" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.4" result="b"/>'
              '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    cols = []
    for size, step, op in ((14, 18, .35), (22, 30, .9)):
        x = r.uniform(0, step)
        while x < W:
            n = r.randint(6, 26)
            y0 = r.uniform(-300, 700)
            # columns over the conversation column are kept dimmer
            mid = 1 - 0.55 * max(0.0, 1 - abs(x - 800) / 420)
            glyph = []
            for i in range(n):
                a = op * mid * (0.15 + 0.85 * (i + 1) / n)
                glyph.append(f'<text y="{y0 + i * size * 1.05:.0f}" fill-opacity="{a:.2f}">{r.choice(glyphs)}</text>')
            head = (f'<text y="{y0 + n * size * 1.05:.0f}" fill="#e2ffec" fill-opacity="{min(1, op * mid + .1):.2f}" '
                    f'filter="url(#mg)">{r.choice(glyphs)}</text>')
            cols.append(f'<g transform="translate({x:.0f} 0)" font-size="{size}" fill="#2bff7a">{"".join(glyph)}{head}</g>')
            x += step * r.uniform(.9, 1.4)
    css = "text{font-family:'Hiragino Sans','Osaka','MS Gothic',monospace;text-anchor:middle}"
    body = (f'<rect width="{W}" height="{H}" fill="url(#mglow)"/>{"".join(cols)}'
            f'<rect width="{W}" height="{H}" fill="url(#veil)" opacity=".6"/>')
    return svg(defs + VEIL, body, css, "Green code raining down a black screen")


# ------------------------------------------------------------------ retro 80s
def retro_80s():
    r = rnd(12)
    horizon = 640
    defs = (lin("sky", [(0, "#07021a"), (.38, "#24083f"), (.62, "#6e1b6e"), (.8, "#e2427f"), (.86, "#ff8a5c")])
            + lin("sunG", [(0, "#fff36b"), (.45, "#ff9a3c"), (1, "#ff2f8e")])
            + lin("floor", [(0, "#2a0846"), (1, "#05010d")])
            + lin("mount", [(0, "#3b0f63"), (1, "#14042a")])
            + '<filter id="neon" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2.5" result="b"/>'
              '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
              '<mask id="sunCut" maskUnits="userSpaceOnUse" x="0" y="0" width="1600" height="1000">'
              '<rect width="1600" height="1000" fill="#fff"/>'
              + "".join(f'<rect x="0" y="{560 + i * 26 + i * i * 1.6:.0f}" width="1600" height="{3 + i * 1.6:.1f}" fill="#000"/>'
                        for i in range(9))
              + "</mask>")
    sun = ('<g class="R"><circle cx="1240" cy="520" r="250" fill="#ff4fa3" opacity=".22"/>'
           '<circle cx="1240" cy="520" r="205" fill="url(#sunG)" mask="url(#sunCut)"/></g>')
    mountains = ('<path d="M0 640 L120 520 L210 590 L330 470 L440 600 L560 540 L700 640Z M900 640 L1010 560 L1100 610 '
                 'L1220 500 L1330 590 L1460 520 L1600 610 V640Z" fill="url(#mount)" stroke="#3ee6ff" stroke-width="2.5" '
                 'filter="url(#neon)"/>')
    grid = [f'<rect y="{horizon}" width="{W}" height="{H - horizon}" fill="url(#floor)"/>']
    for k in range(-26, 27):
        x2 = 800 + k * 150
        grid.append(f'<path d="M800 {horizon} L{x2} {H}" stroke="#ff2fd1" stroke-width="1.6" opacity=".75"/>')
    for i in range(1, 16):
        y = horizon + (i / 15) ** 2.1 * (H - horizon)
        grid.append(f'<path d="M0 {y:.0f} H{W}" stroke="#ff2fd1" stroke-width="{1 + i * .12:.1f}" opacity=".8"/>')
    grid_g = f'<g filter="url(#neon)">{"".join(grid[1:])}</g>'

    def palm(x, base, h, lean):
        top = (x + lean, base - h)
        trunk = f'<path d="M{x} {base} Q{x + lean * .2} {base - h * .5} {top[0]} {top[1]}" stroke="#090014" stroke-width="12" fill="none"/>'
        fronds = "".join(
            f'<path d="M{top[0]} {top[1]} q{dx * .5:.0f} {-40 + abs(dx) * .1:.0f} {dx:.0f} {dy:.0f} '
            f'q{-dx * .35:.0f} {-20:.0f} {-dx:.0f} {-dy + 6:.0f}Z" fill="#090014"/>'
            for dx, dy in ((-150, 50), (-120, 90), (-70, 110), (150, 50), (120, 90), (70, 110), (-20, -10), (40, -14)))
        return trunk + fronds

    palms = (f'<g class="L">{palm(140, 700, 330, 40)}{palm(330, 690, 250, -30)}</g>'
             f'<g class="R">{palm(1520, 700, 300, -50)}</g>')
    body = (f'<rect width="{W}" height="{H}" fill="url(#sky)"/>{stars(r, 120, 0, 420)}{sun}{mountains}'
            f'<rect y="{horizon}" width="{W}" height="{H - horizon}" fill="url(#floor)"/>{grid_g}{palms}'
            f'<rect width="{W}" height="{H}" fill="url(#veil)" opacity=".6"/>')
    return svg(defs + VEIL, body, "", "A synthwave sunset over a neon grid with palm trees")


# ------------------------------------------------------------- desktop icons
def icon_label(x, y, text, color="#fff", shadow="#000", font=UI_FONT, size=15):
    return (f'<text x="{x + 1}" y="{y + 1}" text-anchor="middle" font-family="{font}" font-size="{size}" fill="{shadow}" opacity=".7">{text}</text>'
            f'<text x="{x}" y="{y}" text-anchor="middle" font-family="{font}" font-size="{size}" fill="{color}">{text}</text>')


def monitor_icon(x, y, s=1.0, screen="#3a7bd5"):
    return (f'<g transform="translate({x} {y}) scale({s})">'
            '<rect x="-26" y="-24" width="52" height="40" rx="4" fill="#e9e7df" stroke="#6b6a63" stroke-width="2"/>'
            f'<rect x="-20" y="-18" width="40" height="28" fill="{screen}"/>'
            '<path d="M-20 -18 L20 10" stroke="#fff" stroke-opacity=".25" stroke-width="6"/>'
            '<rect x="-8" y="16" width="16" height="6" fill="#bdbab0"/><rect x="-18" y="22" width="36" height="5" rx="2" fill="#d9d6cc"/></g>')


def folder_icon(x, y, s=1.0, color="#f6d36b"):
    return (f'<g transform="translate({x} {y}) scale({s})">'
            f'<path d="M-26 -16 h18 l6 6 h28 v32 h-52Z" fill="{color}" stroke="#a8862c" stroke-width="2"/>'
            '<path d="M-26 -4 h52 v26 h-52Z" fill="#ffe28f" stroke="#a8862c" stroke-width="2"/>'
            '<rect x="-14" y="-12" width="30" height="8" fill="#fff" opacity=".85"/></g>')


def bin_icon(x, y, s=1.0):
    return (f'<g transform="translate({x} {y}) scale({s})">'
            '<path d="M-18 -18 h36 l-4 42 h-28Z" fill="#dfe9f3" stroke="#5f7489" stroke-width="2"/>'
            '<rect x="-21" y="-24" width="42" height="7" rx="2" fill="#c6d6e6" stroke="#5f7489" stroke-width="2"/>'
            '<path d="M-8 -12 v32 M0 -12 v32 M8 -12 v32" stroke="#8fa4b8" stroke-width="2"/></g>')


def globe_icon(x, y, s=1.0):
    return (f'<g transform="translate({x} {y}) scale({s})"><circle r="24" fill="#3a8fe0" stroke="#1d4f8a" stroke-width="2"/>'
            '<path d="M-14 -12 q10 -6 18 2 q4 10 -6 14 q-10 2 -12 -16Z M6 6 q10 -4 14 4 q-4 10 -14 6Z" fill="#59b85a"/>'
            '<ellipse rx="24" ry="10" fill="none" stroke="#fff" stroke-opacity=".35"/></g>')


# ----------------------------------------------------------------- windows xp
def windows_xp():
    r = rnd(13)
    defs = (lin("sky", [(0, "#1b56c4"), (.45, "#4b8fe6"), (.75, "#a9d1fb"), (1, "#d9ecff")])
            + lin("hillB", [(0, "#4f9a2c"), (1, "#26611a")])
            + lin("hillF", [(0, "#7bc94a"), (.5, "#47a12b"), (1, "#2a6e1b")])
            + lin("bar", [(0, "#3a7ef0"), (.12, "#2458d6"), (.9, "#1d4bc0"), (1, "#163a96")])
            + lin("startG", [(0, "#5cbf4f"), (.5, "#3b9b37"), (1, "#2a7a2a")])
            + lin("tray", [(0, "#22a8f5"), (1, "#0d78d6")])
            + '<filter id="cl" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="14"/></filter>')
    clouds = "".join(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{r.uniform(80, 200):.0f}" ry="{r.uniform(30, 60):.0f}" fill="#fff" '
                     f'opacity="{r.uniform(.55, .9):.2f}" filter="url(#cl)"/>'
                     for x, y in ((r.uniform(0, 1600), r.uniform(80, 420)) for _ in range(22)))
    hills = ('<path d="M0 560 C260 500 520 520 760 560 C1000 600 1260 520 1600 470 V1000 H0Z" fill="url(#hillB)"/>'
             '<path d="M0 700 C300 600 620 590 880 640 C1120 690 1360 640 1600 600 V1000 H0Z" fill="url(#hillF)"/>'
             + "".join(f'<path d="M{x:.0f} {y:.0f} q6 -10 12 0" stroke="#9be067" stroke-width="2" fill="none" opacity=".35"/>'
                       for x, y in ((r.uniform(0, 1600), r.uniform(700, 940)) for _ in range(120))))
    icons = ('<g class="T"><g class="L">'
             + monitor_icon(70, 90) + icon_label(70, 140, "Computer")
             + folder_icon(70, 210) + icon_label(70, 258, "Documents")
             + globe_icon(70, 330) + icon_label(70, 378, "Internet")
             + bin_icon(70, 450) + icon_label(70, 500, "Recycle Bin")
             + '</g></g>')
    # flush with the bottom edge: the scene is pinned there (see pinned)
    taskbar = ('<rect y="958" width="1600" height="42" fill="url(#bar)"/>'
               '<g class="L"><path d="M0 958 H118 Q140 958 140 979 Q140 1000 118 1000 H0Z" fill="url(#startG)"/>'
               f'<text x="26" y="987" font-family="{UI_FONT}" font-size="22" font-style="italic" font-weight="700" fill="#fff">start</text></g>'
               '<g class="R"><rect x="1470" y="958" width="130" height="42" fill="url(#tray)"/>'
               f'<text x="1580" y="985" text-anchor="end" font-family="{UI_FONT}" font-size="15" fill="#fff">10:42 AM</text></g>')
    body = (f'<rect width="{W}" height="{H}" fill="url(#sky)"/>{clouds}{hills}{icons}{taskbar}')
    return pinned(svg(defs, body, "", "Rolling green hills under a blue sky with desktop icons and a blue taskbar"), "bottom")


# ----------------------------------------------------------------- windows 98
def bevel(x, y, w, h, raised=True):
    hi, lo = ("#ffffff", "#808080") if raised else ("#808080", "#ffffff")
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#c0c0c0"/>'
            f'<path d="M{x} {y + h} V{y} H{x + w}" stroke="{hi}" stroke-width="2" fill="none"/>'
            f'<path d="M{x} {y + h} H{x + w} V{y}" stroke="{lo}" stroke-width="2" fill="none"/>')


def windows_98():
    defs = (lin("title", [(0, "#000080"), (1, "#1084d0")], x2=1, y2=0)
            + lin("teal", [(0, "#007b7b"), (1, "#006666")]))
    icons = ('<g class="T"><g class="L">'
             + monitor_icon(64, 90, .9, "#008080") + icon_label(64, 136, "Computer", size=14)
             + folder_icon(64, 200, .9) + icon_label(64, 244, "Documents", size=14)
             + globe_icon(64, 312, .9) + icon_label(64, 356, "Internet", size=14)
             + bin_icon(64, 424, .9) + icon_label(64, 470, "Recycle Bin", size=14)
             + '</g></g>')
    wx, wy, ww, wh = 1170, 150, 400, 330
    lines = ["Claude Code", "", "Backdrop: windows-98", "", "Tip: pick another theme", "from the Backdrop menu", "above the chat box.", "", "C:\\>_"]
    text = "".join(f'<text x="{wx + 18}" y="{wy + 92 + i * 22}" font-family="\'Courier New\', monospace" font-size="15" fill="#000">{t}</text>'
                   for i, t in enumerate(lines))
    window = ('<g class="R">' + bevel(wx, wy, ww, wh)
              + f'<rect x="{wx + 4}" y="{wy + 4}" width="{ww - 8}" height="26" fill="url(#title)"/>'
              f'<text x="{wx + 12}" y="{wy + 22}" font-family="{UI_FONT}" font-size="14" font-weight="700" fill="#fff">readme.txt - Notepad</text>'
              + "".join(bevel(wx + ww - 24 - i * 22, wy + 8, 18, 16) for i in range(3))
              + f'<path d="M{wx + ww - 20} {wy + 12} l10 8 M{wx + ww - 10} {wy + 12} l-10 8" stroke="#000" stroke-width="2"/>'
              f'<rect x="{wx + ww - 64}" y="{wy + 12}" width="10" height="8" fill="none" stroke="#000" stroke-width="2"/>'
              f'<path d="M{wx + ww - 84} {wy + 20} h8" stroke="#000" stroke-width="2"/>'
              + "".join(f'<text x="{wx + 12 + i * 52}" y="{wy + 50}" font-family="{UI_FONT}" font-size="14" fill="#000">{m}</text>'
                        for i, m in enumerate(["File", "Edit", "Search", "Help"]))
              + f'<rect x="{wx + 8}" y="{wy + 62}" width="{ww - 16}" height="{wh - 70}" fill="#fff" stroke="#808080" stroke-width="2"/>'
              + text + '</g>')
    # flush with the bottom edge: the scene is pinned there (see pinned)
    taskbar = ('<rect y="960" width="1600" height="40" fill="#c0c0c0"/><path d="M0 961 H1600" stroke="#fff" stroke-width="2"/>'
               '<g class="L">' + bevel(4, 965, 92, 30)
               + monitor_icon(24, 981, .38, "#008080")
               + f'<text x="40" y="986" font-family="{UI_FONT}" font-size="15" font-weight="700" fill="#000">Start</text></g>'
               '<g class="R">' + bevel(1490, 965, 104, 30, raised=False)
               + f'<text x="1542" y="986" text-anchor="middle" font-family="{UI_FONT}" font-size="14" fill="#000">10:42 PM</text></g>')
    body = f'<rect width="{W}" height="{H}" fill="url(#teal)"/>{icons}{window}{taskbar}'
    return pinned(svg(defs, body, "", "A teal desktop with icons, a classic grey window and taskbar"), "bottom")


# ----------------------------------------------------------- macintosh retro
def macintosh_retro():
    defs = ('<pattern id="dither" width="4" height="4" patternUnits="userSpaceOnUse">'
            '<rect width="4" height="4" fill="#4a4a4a"/><rect width="2" height="2" fill="#6a6a6a"/>'
            '<rect x="2" y="2" width="2" height="2" fill="#6a6a6a"/></pattern>'
            '<pattern id="stripes" width="4" height="4" patternUnits="userSpaceOnUse">'
            '<rect width="4" height="4" fill="#fff"/><rect y="1" width="4" height="1.4" fill="#000"/></pattern>')
    # flush with the top edge: the scene is pinned there (see pinned)
    menubar = ('<g><rect width="1600" height="30" fill="#fff"/><path d="M0 30 H1600" stroke="#000" stroke-width="2"/>'
               '<g class="L"><path d="M30 8 l6 7 l-6 7 l-6 -7Z" fill="#000"/>'
               + "".join(f'<text x="{60 + i * 66}" y="21" font-family="{MAC_FONT}" font-size="16" font-weight="700" fill="#000">{m}</text>'
                         for i, m in enumerate(["File", "Edit", "View", "Special"]))
               + '</g><g class="R">'
               f'<text x="1570" y="21" text-anchor="end" font-family="{MAC_FONT}" font-size="16" font-weight="700" fill="#000">10:42 AM</text></g></g>')

    def mac_window(x, y, w, h, title, inner):
        return (f'<rect x="{x + 4}" y="{y + 4}" width="{w}" height="{h}" fill="#000"/>'
                f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#fff" stroke="#000" stroke-width="2"/>'
                f'<rect x="{x + 2}" y="{y + 4}" width="{w - 4}" height="18" fill="url(#stripes)"/>'
                f'<rect x="{x + 12}" y="{y + 5}" width="16" height="16" fill="#fff" stroke="#000" stroke-width="2"/>'
                f'<rect x="{x + w / 2 - len(title) * 5 - 10}" y="{y + 3}" width="{len(title) * 10 + 20}" height="20" fill="#fff"/>'
                f'<text x="{x + w / 2}" y="{y + 18}" text-anchor="middle" font-family="{MAC_FONT}" font-size="15" font-weight="700" fill="#000">{title}</text>'
                f'<path d="M{x} {y + 26} H{x + w}" stroke="#000" stroke-width="2"/>{inner}')

    def doc_icon(x, y, label):
        return (f'<path d="M{x - 14} {y - 20} h20 l8 8 v32 h-28Z" fill="#fff" stroke="#000" stroke-width="2"/>'
                f'<path d="M{x + 6} {y - 20} v8 h8" fill="none" stroke="#000" stroke-width="2"/>'
                + "".join(f'<path d="M{x - 9} {y - 6 + i * 6} h18" stroke="#000" stroke-width="1.5"/>' for i in range(4))
                + f'<text x="{x}" y="{y + 34}" text-anchor="middle" font-family="{MAC_FONT}" font-size="12" fill="#000">{label}</text>')

    inner = (doc_icon(110, 170, "Read Me") + doc_icon(200, 170, "Notes") + doc_icon(290, 170, "Ideas")
             + f'<text x="60" y="270" font-family="{MAC_FONT}" font-size="13" fill="#000">3 items     12K in disk</text>')
    window = '<g class="L">' + mac_window(40, 100, 330, 200, "Documents", inner) + '</g>'
    disk = ('<g><g class="R"><rect x="1480" y="80" width="64" height="40" rx="3" fill="#fff" stroke="#000" stroke-width="2"/>'
            '<rect x="1490" y="106" width="12" height="4" fill="#000"/><circle cx="1530" cy="108" r="3" fill="#000"/>'
            '<rect x="1458" y="128" width="108" height="20" fill="#000"/>'
            f'<text x="1512" y="143" text-anchor="middle" font-family="{MAC_FONT}" font-size="13" fill="#fff">Hard Disk</text></g></g>'
            '<g class="B"><g class="R">'
            '<path d="M1490 780 h44 l-4 64 h-36Z" fill="#fff" stroke="#000" stroke-width="2"/>'
            '<rect x="1484" y="770" width="56" height="10" fill="#fff" stroke="#000" stroke-width="2"/>'
            '<path d="M1502 792 v44 M1512 792 v44 M1522 792 v44" stroke="#000" stroke-width="2"/>'
            '<rect x="1482" y="852" width="60" height="20" fill="#fff"/>'
            f'<text x="1512" y="867" text-anchor="middle" font-family="{MAC_FONT}" font-size="13" fill="#000">Trash</text></g></g>')
    computer = ('<g class="B"><g class="L"><g transform="translate(110 560)">'
                '<path d="M0 0 h200 l10 240 h-220Z" fill="#d8d0b8" stroke="#000" stroke-width="2"/>'
                '<rect x="22" y="26" width="156" height="118" rx="10" fill="#2b2b2b" stroke="#000" stroke-width="2"/>'
                '<rect x="34" y="38" width="132" height="94" rx="6" fill="#eaeaea"/>'
                '<rect x="44" y="50" width="70" height="44" fill="#fff" stroke="#000"/><rect x="45" y="51" width="68" height="6" fill="url(#stripes)"/>'
                '<rect x="90" y="80" width="64" height="40" fill="#fff" stroke="#000"/><rect x="91" y="81" width="62" height="6" fill="url(#stripes)"/>'
                '<rect x="120" y="170" width="64" height="8" rx="2" fill="#2b2b2b"/>'
                '<rect x="-14" y="240" width="228" height="16" fill="#c9c0a6" stroke="#000" stroke-width="2"/></g></g></g>')
    body = f'<rect width="{W}" height="{H}" fill="url(#dither)"/>{menubar}{window}{computer}{disk}'
    return pinned(svg(defs, body, "", "A dithered grey desktop with a menu bar, a pinstriped window and disk icons"), "top")


# ---------------------------------------------------------------------- linux
def penguin(x, y, s=1.0):
    """An original cartoon penguin (not the Tux artwork), standing, centred on x, feet at y."""
    return (f'<g transform="translate({x} {y}) scale({s})">'
            '<ellipse cx="0" cy="-4" rx="70" ry="12" fill="#000" opacity=".25"/>'
            '<path d="M-58 -150 C-82 -90 -78 -30 -44 -8 L44 -8 C78 -30 82 -90 58 -150 C46 -214 -46 -214 -58 -150Z" fill="#14171c"/>'
            '<path d="M-38 -128 C-54 -82 -50 -36 -26 -14 L26 -14 C50 -36 54 -82 38 -128 C30 -160 -30 -160 -38 -128Z" fill="#f4f6f8"/>'
            '<path d="M-58 -130 C-92 -100 -96 -66 -84 -46 C-74 -70 -66 -96 -52 -112Z" fill="#14171c"/>'
            '<path d="M58 -130 C92 -100 96 -66 84 -46 C74 -70 66 -96 52 -112Z" fill="#14171c"/>'
            '<circle cx="0" cy="-196" r="52" fill="#14171c"/>'
            '<ellipse cx="-18" cy="-200" rx="15" ry="18" fill="#fff"/><ellipse cx="18" cy="-200" rx="15" ry="18" fill="#fff"/>'
            '<circle cx="-14" cy="-196" r="7" fill="#14171c"/><circle cx="14" cy="-196" r="7" fill="#14171c"/>'
            '<circle cx="-11" cy="-199" r="2.4" fill="#fff"/><circle cx="17" cy="-199" r="2.4" fill="#fff"/>'
            '<path d="M-20 -176 Q0 -186 20 -176 Q10 -160 0 -158 Q-10 -160 -20 -176Z" fill="#f5a623"/>'
            '<path d="M-20 -176 Q0 -170 20 -176" stroke="#c47a10" stroke-width="2" fill="none"/>'
            '<path d="M-46 -10 q-16 4 -18 12 h40 q-4 -10 -22 -12Z M46 -10 q16 4 18 12 h-40 q4 -10 22 -12Z" fill="#f5a623"/>'
            '</g>')


def linux():
    r = rnd(16)
    defs = (lin("sky", [(0, "#03060f"), (.55, "#0a1a33"), (1, "#123a55")])
            + lin("aur1", [(0, "#3dffb0", 0), (.5, "#3dffb0", .55), (1, "#3dffb0", 0)], x2=1, y2=0)
            + lin("aur2", [(0, "#9b5cff", 0), (.5, "#9b5cff", .4), (1, "#9b5cff", 0)], x2=1, y2=0)
            + lin("ice", [(0, "#eaf6ff"), (1, "#8fc1e3")])
            + lin("sea", [(0, "#0d2b45"), (1, "#050d18")])
            + '<filter id="ab" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="18"/></filter>')
    aurora = ('<path d="M-100 260 C200 160 420 320 760 220 C1060 130 1300 280 1700 180" stroke="url(#aur1)" stroke-width="90" fill="none" filter="url(#ab)"/>'
              '<path d="M-100 340 C260 260 520 380 820 300 C1120 220 1360 330 1700 260" stroke="url(#aur2)" stroke-width="70" fill="none" filter="url(#ab)"/>')
    sea = (f'<rect y="700" width="{W}" height="{H - 700}" fill="url(#sea)"/>'
           + "".join(f'<path d="M{x:.0f} {y:.0f} h{r.uniform(20, 80):.0f}" stroke="#5fb4e8" stroke-width="2" opacity=".35"/>'
                     for x, y in ((r.uniform(0, 1600), r.uniform(720, 980)) for _ in range(40))))
    floe = ('<g class="R"><path d="M1130 760 L1180 712 L1520 704 L1590 748 L1560 800 L1160 806Z" fill="url(#ice)"/>'
            '<path d="M1160 806 L1560 800 L1540 830 L1190 834Z" fill="#6fa3c7"/>'
            + penguin(1340, 742, 1.05)
            + penguin(1490, 744, .55) + '</g>')
    lines = [("#7ee787", "user@penguin", "#c9d1d9", ":~$ uname -s"), ("#c9d1d9", "Linux", "", ""),
             ("#7ee787", "user@penguin", "#c9d1d9", ":~$ claude"), ("#f5a623", "* Welcome to Claude Code", "", ""),
             ("#7ee787", "user@penguin", "#c9d1d9", ":~$ ")]
    tx, ty, tw, th = 40, 140, 400, 280
    text = "".join(
        f'<text x="{tx + 18}" y="{ty + 70 + i * 30}" font-family="\'DejaVu Sans Mono\', Menlo, monospace" font-size="16">'
        f'<tspan fill="{c1}">{t1}</tspan><tspan fill="{c2 or c1}">{t2}</tspan></text>'
        for i, (c1, t1, c2, t2) in enumerate(lines))
    terminal = ('<g class="L">'
                f'<rect x="{tx + 6}" y="{ty + 8}" width="{tw}" height="{th}" rx="10" fill="#000" opacity=".45"/>'
                f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="10" fill="#0d1117" stroke="#30363d" stroke-width="2"/>'
                f'<path d="M{tx} {ty + 10} q0 -10 10 -10 h{tw - 20} q10 0 10 10 v24 h-{tw}Z" fill="#21262d"/>'
                + "".join(f'<circle cx="{tx + 20 + i * 20}" cy="{ty + 17}" r="6" fill="{c}"/>' for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]))
                + f'<text x="{tx + tw / 2}" y="{ty + 22}" text-anchor="middle" font-family="{UI_FONT}" font-size="13" fill="#8b949e">user@penguin: ~</text>'
                + text
                + f'<rect x="{tx + 18 + 16 * 9.6:.0f}" y="{ty + 70 + 4 * 30 - 15}" width="10" height="18" fill="#c9d1d9"/>'
                + '</g>')
    body = (f'<rect width="{W}" height="{H}" fill="url(#sky)"/>{stars(r, 160, 0, 620)}{aurora}{sea}{floe}{terminal}'
            f'<rect width="{W}" height="{H}" fill="url(#veil)" opacity=".5"/>')
    return svg(defs + VEIL, body, "", "A cartoon penguin on an ice floe under an aurora, beside a terminal window")


SCENES = {
    "matrix": matrix,
    "retro-80s": retro_80s,
    "windows-xp": windows_xp,
    "windows-98": windows_98,
    "macintosh-retro": macintosh_retro,
    "linux": linux,
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
            "// Generated by tools/build_retro.py: edit that file, not this one.\n"
            f"export const {const} = `{escaped}`\n")
        print(f"{name}: {len(s)} chars")
