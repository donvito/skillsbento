#!/usr/bin/env python3
"""Builds the two F1 backdrop scenes (SVG) for the backdrops mod.

The desktop app frosts the conversation column, so each scene puts its
pictures in the two gutters beside it:

  right gutter  a top-down view of the car, nose up
  left gutter   a driver panel: race number, name and livery stripes, with a
                slot (<!--PHOTO-->) the mod fills with the person's own photo
                from photos/<scene>.jpg when there is one

Portrait boxes (phones, tall windows) have no gutters: the car lies across
the top instead and the panel is left out.

Usage: python3 tools/build_scenes.py hooks/scenes
Writes <out>/<scene>.ts (export const ...) and <out>/<scene>.svg for preview.
No logos, sponsor marks or trademarks are drawn: colours, stripes, numbers.
"""
import base64
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from smil import timeshift  # noqa: E402

PHOTOS = Path(os.environ.get("F1_PHOTOS") or Path(__file__).resolve().parent.parent / "photos")
# F1_STILL=1: a frame for tools/build_stills.py, kept clear of the edges a
# centred, cropped still image loses on narrower windows, and without motion.
STILL = os.environ.get("F1_STILL") == "1"


def traced(name):
    """photos/<name>.svg (a photo traced to vector shapes) as its viewBox and inner markup, or None.

    The desktop app strips raster images from a Svg backdrop, so a scene
    shows a photo only once it is traced into paths (see the README).
    """
    import re
    f = PHOTOS / name
    if not f.exists():
        return None
    svg = f.read_text()
    w = float(re.search(r'width="([\d.]+)"', svg).group(1))
    h = float(re.search(r'height="([\d.]+)"', svg).group(1))
    inner = svg[svg.index(">", svg.index("<svg")) + 1:svg.rindex("</svg>")]
    return f"0 0 {w:g} {h:g}", inner.strip()


def data_uri(name):
    """photos/<name> as a data: URI, or None when the file is not there."""
    f = PHOTOS / name
    if not f.exists():
        return None
    return "data:image/jpeg;base64," + base64.b64encode(f.read_bytes()).decode()

CX = 200  # centre line of the top view (viewBox 0 0 400 1000, nose up)


def catmull(points, closed=True):
    """Smooth path through points (Catmull-Rom as cubic Beziers)."""
    n = len(points)
    d = f"M{points[0][0]:.1f} {points[0][1]:.1f}"
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = points[(i - 1) % n] if closed or i > 0 else points[i]
        p1 = points[i]
        p2 = points[(i + 1) % n]
        p3 = points[(i + 2) % n] if closed or i + 2 < n else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
    return d + (" Z" if closed else "")


def sym(half):
    """A shape symmetric about CX from its right half, given as (dx, y) top to bottom."""
    right = [(CX + dx, y) for dx, y in half]
    left = [(CX - dx, y) for dx, y in reversed(half) if dx != 0]
    return right + left


def poly(points):
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in points) + " Z"


# ------------------------------------------------------------ top-view car
BODY = catmull(sym([
    (0, 26), (8, 34), (16, 70), (24, 150), (32, 240), (44, 310), (60, 360),
    (68, 420), (70, 500), (64, 580), (54, 660), (44, 740), (36, 820), (28, 880), (0, 892),
]))
SIDEPODS = catmull(sym([
    (0, 400), (96, 410), (128, 438), (140, 490), (138, 570), (124, 646),
    (98, 716), (66, 768), (40, 800), (0, 806),
]))
FLOOR = catmull(sym([
    (0, 300), (64, 306), (150, 418), (160, 520), (160, 640), (150, 760),
    (118, 836), (0, 846),
]))
FRONT_WING = poly(sym([
    (0, 44), (70, 46), (150, 54), (178, 60), (184, 70), (182, 104), (172, 108),
    (120, 100), (50, 92), (0, 90),
]))
FW_FLAP = catmull([(28, 76), (120, 68), (200, 66), (280, 68), (372, 76)], closed=False)
FW_FLAP2 = catmull([(36, 90), (120, 82), (200, 80), (280, 82), (364, 90)], closed=False)
DIFFUSER = poly(sym([(0, 830), (96, 830), (108, 900), (0, 904)]))
RW_MAIN = poly(sym([(0, 918), (116, 916), (118, 946), (0, 948)]))
RW_FLAP = poly(sym([(0, 950), (116, 950), (116, 972), (0, 974)]))
RW_PLATES = (
    f"M{CX - 124} 904 h10 v78 h-10 Z M{CX + 114} 904 h10 v78 h-10 Z"
)
SUSPENSION = (
    "M317 142 L240 176 M317 182 L242 220 M318 164 L240 200 "
    "M83 142 L160 176 M83 182 L158 220 M82 164 L160 200 "
    "M309 820 L232 790 M309 862 L230 858 "
    "M91 820 L168 790 M91 862 L170 858"
)
MIRRORS = (
    f'<path d="M{CX - 66} 392 L{CX - 86} 386" stroke="#111" stroke-width="3"/>'
    f'<path d="M{CX + 66} 392 L{CX + 86} 386" stroke="#111" stroke-width="3"/>'
)


def wheel(x, y, w, h, stripe):
    return f"""
    <g>
      <rect x="{x - w / 2}" y="{y - h / 2}" width="{w}" height="{h}" rx="{w * 0.24:.1f}" fill="url(#tyreTop)"/>
      <rect x="{x - w / 2 + 3}" y="{y - h / 2 + 6}" width="{w - 6}" height="{h - 12}" rx="{w * 0.2:.1f}"
            fill="none" stroke="#fff" stroke-opacity=".06" stroke-width="2"/>
      <path d="M{x + (w / 2 - 5) * (1 if x > CX else -1)} {y - h / 2 + 18} v{h - 36}" stroke="{stripe}"
            stroke-width="3" stroke-linecap="round" opacity=".9"/>
      <path d="M{x - w / 2 + 10} {y - h / 2 + 14} v{h - 28}" stroke="#fff" stroke-opacity=".12" stroke-width="6"
            stroke-linecap="round"/>
    </g>"""


def car_top(L):
    """<symbol id="cartop"> in a 400 x 1000 box, nose up."""
    return f"""
  <linearGradient id="roundness" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#000" stop-opacity=".6"/>
    <stop offset=".3" stop-color="#000" stop-opacity=".05"/>
    <stop offset=".42" stop-color="#fff" stop-opacity=".22"/>
    <stop offset=".5" stop-color="#fff" stop-opacity=".05"/>
    <stop offset=".75" stop-color="#000" stop-opacity=".1"/>
    <stop offset="1" stop-color="#000" stop-opacity=".65"/>
  </linearGradient>
  <linearGradient id="tyreTop" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#060607"/><stop offset=".35" stop-color="#26272a"/>
    <stop offset=".65" stop-color="#1c1d20"/><stop offset="1" stop-color="#060607"/>
  </linearGradient>
  <linearGradient id="paint" x1="0" y1="0" x2="1" y2="0">{L['paint']}</linearGradient>
  <linearGradient id="sweepV" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".28"/>
    <stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <radialGradient id="carglow" cx=".5" cy=".5" r=".5">
    <stop offset="0" stop-color="{L['glow']}" stop-opacity="{L['glow_op']}"/>
    <stop offset="1" stop-color="{L['glow']}" stop-opacity="0"/>
  </radialGradient>
  {L.get('defs', '')}
  <clipPath id="bodyclip"><path d="{BODY}"/></clipPath>
  <clipPath id="podclip"><path d="{SIDEPODS}"/></clipPath>
  <filter id="drop" x="-30%" y="-10%" width="160%" height="120%">
    <feGaussianBlur in="SourceAlpha" stdDeviation="9"/><feOffset dx="10" dy="14"/>
    <feComponentTransfer><feFuncA type="linear" slope=".75"/></feComponentTransfer>
    <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <symbol id="cartop" viewBox="0 0 400 1000" overflow="visible">
    <ellipse cx="200" cy="500" rx="260" ry="560" fill="url(#carglow)" class="pulse"/>
    <g filter="url(#drop)">
      <path d="{FLOOR}" fill="#0b0b0c"/>
      <path d="{FLOOR}" fill="none" stroke="{L['floor_edge']}" stroke-opacity=".55" stroke-width="1.6"/>
      <path d="{DIFFUSER}" fill="#101012"/>
      <path d="{SUSPENSION}" stroke="#0c0d0f" stroke-width="5" stroke-linecap="round"/>
      <path d="{SUSPENSION}" stroke="#fff" stroke-opacity=".14" stroke-width="1.2"/>
      {wheel(350, 160, 66, 144, L['compound'])}
      {wheel(50, 160, 66, 144, L['compound'])}
      {wheel(345, 842, 80, 150, L['compound'])}
      {wheel(55, 842, 80, 150, L['compound'])}
      <path d="{SIDEPODS}" fill="{L['pods']}"/>
      <g clip-path="url(#podclip)">{L['pod_livery']}
        <rect x="0" y="380" width="400" height="460" fill="url(#roundness)" opacity=".8"/></g>
      <path d="{BODY}" fill="url(#paint)"/>
      <g clip-path="url(#bodyclip)">
        {L['body_livery']}
        <rect x="0" y="0" width="400" height="1000" fill="url(#roundness)"/>
        <rect class="sheenV" x="0" y="-260" width="400" height="220" fill="url(#sweepV)"/>
      </g>
      <path d="{BODY}" fill="none" stroke="{L['rim']}" stroke-opacity=".7" stroke-width="1.6"/>
      <!-- cockpit -->
      <ellipse cx="200" cy="468" rx="34" ry="58" fill="#060607"/>
      <circle cx="200" cy="474" r="24" fill="{L['helmet']}"/>
      <path d="M180 466 Q200 448 220 466 L218 474 Q200 462 182 474 Z" fill="#0d0f12"/>
      <path d="M152 482 C152 430 172 404 200 404 C228 404 248 430 248 482" fill="none"
            stroke="{L['halo']}" stroke-width="10" stroke-linecap="round"/>
      <path d="M200 404 L200 424" stroke="{L['halo']}" stroke-width="8" stroke-linecap="round"/>
      <path d="M156 470 C158 432 176 410 200 410" fill="none" stroke="#fff" stroke-opacity=".3" stroke-width="2"/>
      <rect x="178" y="530" width="44" height="44" rx="14" fill="{L['airbox']}"/>
      <rect x="190" y="536" width="20" height="10" rx="4" fill="#050506"/>
      {MIRRORS}
      <ellipse cx="{CX - 94}" cy="384" rx="16" ry="8" fill="{L['mirror']}"/>
      <ellipse cx="{CX + 94}" cy="384" rx="16" ry="8" fill="{L['mirror']}"/>
      <!-- wings -->
      <path d="{FRONT_WING}" fill="{L['fw']}"/>
      <path d="{FW_FLAP}" fill="none" stroke="{L['fw_flap']}" stroke-width="7" stroke-linecap="round"/>
      <path d="{FW_FLAP2}" fill="none" stroke="{L['fw_flap2']}" stroke-width="5" stroke-linecap="round"/>
      <path d="M18 60 L18 106 M382 60 L382 106" stroke="{L['fw_plate']}" stroke-width="9" stroke-linecap="round"/>
      <path d="{RW_MAIN}" fill="{L['rw_main']}"/>
      <path d="{RW_FLAP}" fill="{L['rw_flap']}"/>
      <path d="{RW_PLATES}" fill="{L['rw_plate']}"/>
      <path d="M{CX - 4} 880 h8 v40 h-8 Z" fill="#111"/>
      <!-- race number on the nose -->
      <text x="200" y="262" text-anchor="middle" font-family="'Helvetica Neue', Arial, sans-serif"
            font-weight="800" font-style="italic" font-size="34" fill="{L['num_fill']}">{L['number']}</text>
    </g>
  </symbol>"""


def driver_panel(D):
    """<symbol id="driver"> in a 400 x 1000 box: number, name, stripes, photo."""
    vector = None if STILL else traced(D['photo'].replace('.jpg', '.svg'))
    uri = data_uri(D['photo']) if STILL else None
    has_photo = bool(uri or vector)
    number = (
        f'<text x="200" y="700" text-anchor="middle" font-family="\'Helvetica Neue\', Arial, sans-serif" '
        f'font-weight="900" font-style="italic" font-size="72" fill="{D["accent"]}">{D["number"]}</text>'
        if has_photo else
        f'<text x="200" y="560" text-anchor="middle" font-family="\'Helvetica Neue\', Arial, sans-serif" '
        f'font-weight="900" font-style="italic" font-size="330" letter-spacing="-12" fill="url(#numfill)" '
        f'stroke="{D["accent"]}" stroke-width="3" stroke-opacity=".9">{D["number"]}</text>')
    if vector:
        tag = (f'<g mask="url(#photofade)"><svg x="0" y="20" width="400" height="600" viewBox="{vector[0]}" '
               f'preserveAspectRatio="xMidYMid slice">{vector[1]}</svg></g>')
    elif uri:
        tag = (f'<image href="{uri}" x="0" y="20" width="400" height="600" preserveAspectRatio="xMidYMid slice" '
               f'mask="url(#photofade)"/>')
    else:
        tag = ""
    D = dict(D, photo_tag=tag)
    stripes = "".join(
        f'<rect x="{60 + i * 98}" y="826" width="86" height="6" rx="3" fill="{c}"/>'
        for i, c in enumerate(D['stripes']))
    return f"""
  <radialGradient id="featherG" cx=".5" cy=".45" r=".5">
    <stop offset=".15" stop-color="#fff"/><stop offset=".55" stop-color="#bbb"/>
    <stop offset=".8" stop-color="#444"/><stop offset="1" stop-color="#000"/>
  </radialGradient>
  <mask id="photofade" maskUnits="userSpaceOnUse" x="0" y="20" width="400" height="640">
    <rect x="0" y="20" width="400" height="640" fill="url(#featherG)"/>
  </mask>
  <linearGradient id="numfill" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{D['accent']}" stop-opacity=".35"/>
    <stop offset="1" stop-color="{D['accent']}" stop-opacity="0"/>
  </linearGradient>
  <symbol id="driver" viewBox="0 0 400 1000" overflow="visible">
    {number}
    {D['photo_tag']}
    <text x="200" y="740" text-anchor="middle" font-family="'Helvetica Neue', Arial, sans-serif"
          font-weight="500" font-size="24" letter-spacing="10" fill="{D['first_color']}">{D['first']}</text>
    <text x="200" y="796" text-anchor="middle" font-family="'Helvetica Neue', Arial, sans-serif"
          font-weight="800" font-size="46" letter-spacing="6" fill="#ffffff">{D['last']}</text>
    {stripes}
    <text x="200" y="876" text-anchor="middle" font-family="'Helvetica Neue', Arial, sans-serif"
          font-weight="500" font-size="18" letter-spacing="6" fill="{D['first_color']}">{D['caption']}</text>
  </symbol>"""


def car_photo(L):
    """<symbol id="carphoto">: the real car, feathered into the dark; None without a photo."""
    uri = data_uri(L['photo']) if STILL else None
    if uri is None:
        return None
    w, h = 640, L['photo_h']
    return f"""
  <linearGradient id="carfadeH" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#000"/><stop offset=".3" stop-color="#fff"/>
    <stop offset=".9" stop-color="#fff"/><stop offset="1" stop-color="#000"/>
  </linearGradient>
  <linearGradient id="carfadeV" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#000"/><stop offset=".32" stop-color="#fff"/>
    <stop offset=".72" stop-color="#fff"/><stop offset="1" stop-color="#000"/>
  </linearGradient>
  <mask id="carmaskH" maskUnits="userSpaceOnUse" x="0" y="0" width="{w}" height="{h}">
    <rect width="{w}" height="{h}" fill="url(#carfadeH)"/>
  </mask>
  <mask id="carmask" maskUnits="userSpaceOnUse" x="0" y="0" width="{w}" height="{h}">
    <rect width="{w}" height="{h}" fill="url(#carfadeV)"/>
  </mask>
  <symbol id="carphoto" viewBox="0 0 {w} {h}" overflow="visible">
    <ellipse cx="{w / 2}" cy="{h / 2}" rx="{w * 0.62}" ry="{h * 0.9}" fill="url(#carglow)" class="pulse"/>
    <g mask="url(#carmaskH)"><image href="{uri}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice" mask="url(#carmask)"/></g>
  </symbol>"""


# ------------------------------------------------------------------ liveries
MERCEDES = dict(
    number="12", glow="#00d2be", glow_op=".22", rim="#9ffcf2", floor_edge="#00d2be",
    paint='<stop offset="0" stop-color="#14181b"/><stop offset=".5" stop-color="#2a3035"/>'
          '<stop offset="1" stop-color="#14181b"/>',
    defs='<pattern id="carbon" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
         '<rect width="3" height="3" fill="#fff" opacity=".07"/><rect x="3" y="3" width="3" height="3" fill="#fff" opacity=".07"/></pattern>'
         '<linearGradient id="silver" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7d848b"/>'
         '<stop offset=".45" stop-color="#eef1f3"/><stop offset="1" stop-color="#8a9198"/></linearGradient>',
    body_livery=(
        '<rect width="400" height="1000" fill="url(#carbon)"/>'
        # silver nose and cockpit shoulders
        '<path d="M150 20 L250 20 L262 380 L138 380 Z" fill="url(#silver)"/>'
        # silver spine down the engine cover
        '<path d="M186 560 L214 560 L208 890 L192 890 Z" fill="url(#silver)"/>'
        # turquoise pinstripes beside the nose
        '<path d="M176 60 L166 380" stroke="#00d2be" stroke-width="3"/>'
        '<path d="M224 60 L234 380" stroke="#00d2be" stroke-width="3"/>'
    ),
    pods="#1b2024",
    pod_livery=('<rect width="400" height="1000" fill="url(#carbon)"/>'
                '<path d="M64 452 C70 560 96 680 140 760" fill="none" stroke="#00d2be" stroke-width="4"/>'
                '<path d="M336 452 C330 560 304 680 260 760" fill="none" stroke="#00d2be" stroke-width="4"/>'
                '<path d="M80 420 L320 420 L300 470 L100 470 Z" fill="url(#silver)" opacity=".9"/>'),
    helmet="#dfe3e6", halo="#15181b", airbox="#15181b", mirror="#1d2226",
    fw="#14171a", fw_flap="#c3c8cd", fw_flap2="#00d2be", fw_plate="#00d2be",
    rw_main="#16191c", rw_flap="#c3c8cd", rw_plate="#00d2be",
    compound="#f2d21b", num_fill="#0b0d10", photo="w17.jpg", photo_h=223,
)

FERRARI = dict(
    number="44", glow="#ff2a1f", glow_op=".22", rim="#ffd9d0", floor_edge="#ff3b2f",
    paint='<stop offset="0" stop-color="#b30000"/><stop offset=".45" stop-color="#ff2a1f"/>'
          '<stop offset="1" stop-color="#b30000"/>',
    defs='<linearGradient id="white" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#c9c6c0"/>'
         '<stop offset=".45" stop-color="#ffffff"/><stop offset="1" stop-color="#cfccc6"/></linearGradient>',
    body_livery=(
        # white cockpit surround and engine-cover spine
        '<path d="M120 380 L280 380 L276 580 L230 600 L222 880 L178 880 L170 600 L124 580 Z" fill="url(#white)"/>'
        # thin white centre line down the nose
        '<path d="M197 40 L203 40 L205 380 L195 380 Z" fill="#fff" opacity=".9"/>'
    ),
    pods="#e10600",
    pod_livery=('<path d="M40 640 L360 640 L360 820 L40 820 Z" fill="#0b0b0c" opacity=".85"/>'
                '<path d="M60 448 C68 560 96 680 140 760" fill="none" stroke="#fff" stroke-width="3" opacity=".8"/>'
                '<path d="M340 448 C332 560 304 680 260 760" fill="none" stroke="#fff" stroke-width="3" opacity=".8"/>'),
    helmet="#f4f1ea", halo="#f4f2ee", airbox="#f4f2ee", mirror="#e10600",
    fw="#0d0d0e", fw_flap="#e10600", fw_flap2="#ffffff", fw_plate="#e10600",
    rw_main="#e10600", rw_flap="#111111", rw_plate="#0d0d0e",
    compound="#e8e8e8", num_fill="#ffffff", photo="sf26.jpg", photo_h=197,
)

KIMI = dict(number="12", first="KIMI", last="ANTONELLI", caption="MERCEDES · 2026",
            accent="#00d2be", first_color="#9fb3b6", photo="antonelli.jpg", stripes=["#00d2be", "#c9ced3", "#2a3035"])
LEWIS = dict(number="44", first="LEWIS", last="HAMILTON", caption="FERRARI · 2026",
             accent="#ff2a1f", first_color="#c7aaa5", photo="hamilton.jpg", stripes=["#e10600", "#ffffff", "#2a2a2a"])

# ---------------------------------------------------------------- the scene
# Root space 1600 x 1000 with preserveAspectRatio slice: a wide box crops top
# and bottom, a narrow one crops the sides around x=800. For each band of
# aspect ratios the car and panel are placed inside the part still visible,
# at its edges, so they sit in the gutters beside the conversation column.
BANDS = [1.0, 1.2, 1.4, 1.6, 1.8, 2.1, 2.6, 4.0]
GUTTER_W = 0.17   # share of the visible width each picture takes
MARGIN = 0.07 if STILL else 0.03


def landscape_layouts():
    out = []
    for lo, hi in zip(BANDS, BANDS[1:]):
        # the narrowest visible area within the band
        if lo < 1.6:
            wv, hv = 1000 * lo, 1000
        else:
            wv, hv = 1600, 1600 / hi
        x0, y0 = 800 - wv / 2, 500 - hv / 2
        w = GUTTER_W * wv
        h = min(w * 2.5, 0.84 * hv)
        w = h / 2.5
        y = y0 + hv * 0.47 - h / 2
        mq = f"(min-aspect-ratio: {int(lo * 100)}/100)"
        if hi < 4.0:
            mq += f" and (max-aspect-ratio: {int(hi * 100) - 1}/100)"
        out.append((mq, dict(car=(x0 + wv - MARGIN * wv - w, y, w, h),
                             panel=(x0 + MARGIN * wv, y, w, h), wv=wv, right=x0 + wv)))
    return out


def scene(L, D, ground, accent, veil):
    uses, css = [], []
    photo = car_photo(L)
    for i, (mq, pos) in enumerate(landscape_layouts()):
        cx, cy, cw, ch = pos["car"]
        px, py, pw, ph = pos["panel"]
        if photo:
            # the real car, wider than the gutter, its tail at the window edge
            wv = pos["wv"]
            fw = (0.27 if STILL else 0.33) * wv
            fh = fw * L['photo_h'] / 640
            fx = pos["right"] - fw - (0.035 if STILL else 0.005) * wv
            fy = cy + ch / 2 - fh / 2
            uses.append(f'<use href="#carphoto" class="lay l{i}" x="{fx:.0f}" y="{fy:.0f}" width="{fw:.0f}" height="{fh:.0f}"/>')
        else:
            uses.append(f'<use href="#cartop" class="lay l{i}" x="{cx:.0f}" y="{cy:.0f}" width="{cw:.0f}" height="{ch:.0f}"/>')
        uses.append(f'<use href="#driver" class="lay l{i}" x="{px:.0f}" y="{py:.0f}" width="{pw:.0f}" height="{ph:.0f}"/>')
        css.append(f"@media {mq} {{ .l{i} {{ display: inline; }} }}")
    # portrait: the car lies across the top, nose left; no panel
    for name, lo, hi, a in (("pa", 0, 0.75, 0.46), ("pb", 0.75, 1.0, 0.75)):
        wv = 1000 * a
        x0 = 800 - wv / 2
        length = 0.8 * wv
        thick = length * 0.4
        cx, cy = 800, 70 + thick / 2
        if photo:
            fw = 0.95 * wv
            fh = fw * L['photo_h'] / 640
            uses.append(f'<use href="#carphoto" class="lay {name} portrait" x="{x0 + 0.025 * wv:.0f}" y="70" '
                        f'width="{fw:.0f}" height="{fh:.0f}"/>')
            css.append(f"@media (max-aspect-ratio: {int(hi * 100) - 1}/100)" + (f" and (min-aspect-ratio: {int(lo * 100)}/100)" if lo else "") + f" {{ .{name} {{ display: inline; }} }}")
            continue
        uses.append(
            f'<g class="lay {name} portrait" transform="translate({cx:.0f} {cy:.0f}) rotate(-90)">'
            f'<use href="#cartop" x="{-thick / 2:.0f}" y="{-length / 2:.0f}" width="{thick:.0f}" height="{length:.0f}"/></g>')
        mq = f"(max-aspect-ratio: {int(hi * 100) - 1}/100)" + (f" and (min-aspect-ratio: {int(lo * 100)}/100)" if lo else "")
        css.append(f"@media {mq} {{ .{name} {{ display: inline; }} }}")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1000" preserveAspectRatio="xMidYMid slice">
<style>
  .lay {{ display: none; }}
  {' '.join(css)}
  .portrait {{ opacity: .7; }}
  .streak {{ animation: drift 16s linear infinite; }}
  .streak.b {{ animation-duration: 23s; animation-delay: -9s; }}
  @keyframes drift {{ from {{ transform: translateY(-1200px); }} to {{ transform: translateY(1200px); }} }}
  .pulse {{ animation: pulse 7s ease-in-out infinite; }}
  @keyframes pulse {{ 0%, 100% {{ opacity: .7; }} 50% {{ opacity: 1; }} }}
  .sheenV {{ animation: sheenV 10s ease-in-out infinite; }}
  @keyframes sheenV {{ 0%, 55% {{ transform: translateY(0); }} 100% {{ transform: translateY(1500px); }} }}
  @media (prefers-reduced-motion: reduce) {{ .streak, .pulse, .sheenV {{ animation: none; }} }}
</style>
<defs>
  {ground}
  <linearGradient id="streakV" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{accent}" stop-opacity="0"/><stop offset=".5" stop-color="{accent}" stop-opacity=".45"/>
    <stop offset="1" stop-color="{accent}" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="veil" x1="0" y1="0" x2="1" y2="0">
    <stop offset=".3" stop-color="#000" stop-opacity="0"/><stop offset=".42" stop-color="#000" stop-opacity="{veil}"/>
    <stop offset=".58" stop-color="#000" stop-opacity="{veil}"/><stop offset=".7" stop-color="#000" stop-opacity="0"/>
  </linearGradient>
  {photo or car_top(L)}
  {car_top(L) if photo else ""}
  {driver_panel(D)}
</defs>
<rect width="1600" height="1000" fill="url(#ground)"/>
<rect width="1600" height="1000" fill="url(#veil)"/>
<g opacity=".7" display="{'none' if STILL else 'inline'}">
  <rect class="streak" x="300" y="0" width="1.2" height="700" fill="url(#streakV)"/>
  <rect class="streak b" x="1290" y="0" width="1" height="900" fill="url(#streakV)"/>
  <rect class="streak" x="1460" y="-300" width="1" height="600" fill="url(#streakV)"/>
  <rect class="streak b" x="140" y="-200" width="1" height="500" fill="url(#streakV)"/>
</g>
{''.join(uses)}
</svg>
"""


MERC_GROUND = """<linearGradient id="ground" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#0c1517"/><stop offset=".3" stop-color="#070a0b"/>
    <stop offset=".7" stop-color="#070a0b"/><stop offset="1" stop-color="#0d1a1b"/>
  </linearGradient>"""

FERRARI_GROUND = """<linearGradient id="ground" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#1c0707"/><stop offset=".3" stop-color="#0b0404"/>
    <stop offset=".7" stop-color="#0b0404"/><stop offset="1" stop-color="#220807"/>
  </linearGradient>"""

SCENES = {
    "f1-mercedes-kimi": scene(MERCEDES, KIMI, MERC_GROUND, "#00d2be", ".35"),
    "f1-ferrari-hamilton": scene(FERRARI, LEWIS, FERRARI_GROUND, "#ff2a1f", ".35"),
}

if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    out.mkdir(parents=True, exist_ok=True)
    for scene_name, svg in SCENES.items():
        svg = "\n".join(line.rstrip() for line in svg.splitlines() if line.strip()) + "\n"
        svg = timeshift(svg)
        (out / f"{scene_name}.svg").write_text(svg)
        const = scene_name.replace("f1-", "").replace("-", "_").upper()
        escaped = svg.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
        (out / f"{scene_name}.ts").write_text(
            "// Generated by tools/build_scenes.py: edit that file, not this one.\n"
            f"export const {const} = `{escaped}`\n")
        print(f"{scene_name}: {len(svg)} chars")
