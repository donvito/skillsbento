"""Scene animation helpers.

`timeshift` (used by the build scripts) offsets every CSS animation delay by
var(--t), so the mod can draw a scene at any second: the desktop app paints a
backdrop as a still frame, and the mod redraws it once a second.

`smilify` adds SMIL children instead. It is kept for reference only: the
desktop app ran neither SMIL nor CSS animation in a backdrop.
"""
import re

INF = 'repeatCount="indefinite"'


def op(values, dur, begin=0, discrete=False, key_times=None):
    extra = ' calcMode="discrete"' if discrete else ""
    if key_times:
        extra += f' keyTimes="{key_times}"'
    return f'<animate attributeName="opacity" values="{values}" dur="{dur}s" begin="{begin}s"{extra} {INF}/>'


def tr(kind, values, dur, begin=0, key_times=None, additive=False):
    extra = f' keyTimes="{key_times}"' if key_times else ""
    if additive:
        extra += ' additive="sum"'
    return (f'<animateTransform attributeName="transform" type="{kind}" values="{values}" '
            f'dur="{dur}s" begin="{begin}s"{extra} {INF}/>')


def attr(name, values, dur, begin=0):
    return f'<animate attributeName="{name}" values="{values}" dur="{dur}s" begin="{begin}s" {INF}/>'


# class (or class pair) -> SMIL children, mirroring the CSS keyframes
ANIM = {
    "tw1": op("1;.25;1", 3.1), "tw2": op("1;.25;1", 4.3, -1.7),
    "tw3": op("1;.25;1", 5.7, -3.2), "tw4": op("1;.25;1", 2.4, -.9),
    "pulse": op(".65;1;.65", 6),
    "bl1": op("1;.15", 1.3, 0, True, "0;.5"), "bl2": op("1;.15", 2.1, -.6, True, "0;.5"),
    "bl3": op("1;.15", 3.4, -1.1, True, "0;.5"),
    "sp1": op("1;0", .9, 0, True, "0;.5"), "sp2": op("1;0", 1.3, -.4, True, "0;.5"),
    "sp3": op("1;0", .7, -.2, True, "0;.5"), "sp4": op("1;0", 1.1, -.8, True, "0;.5"),
    "glow1": op(".65;1;.65", 5), "glow2": op(".65;1;.65", 7, -2), "glow3": op(".65;1;.65", 6, -4),
    "scrA": op("1;0", 9, 0, True, "0;.333"), "scrB": op("1;0", 9, -3, True, "0;.333"),
    "scrC": op("1;0", 9, -6, True, "0;.333"),
    "drift": tr("translate", "0 0;-1600 0", 140), "drift2": tr("translate", "0 0;-1600 0", 95, -40),
    "float": tr("translate", "0 0;18 -26;0 0", 18) + tr("rotate", "0 185 346;14 185 346;0 185 346", 18, additive=True),
    "pt1": tr("translate", "0 -40;120 520;260 1080", 16), "pt2": tr("translate", "0 -40;120 520;260 1080", 21, -7),
    "pt3": tr("translate", "0 -40;120 520;260 1080", 13, -4), "pt4": tr("translate", "0 -40;120 520;260 1080", 25, -15),
    "beacon": tr("rotate", "0 1300 140;360 1300 140", 14),
    "fly": tr("translate", "-400 40;800 -30;2000 30", 38), "fly2": tr("translate", "-400 40;800 -30;2000 30", 52, -20),
    "fa": tr("translate", "0 0;-120 1000", 34), "fb": tr("translate", "0 0;-120 1000", 22),
    "fc": tr("translate", "0 0;-120 1000", 14),
    "wA": tr("translate", "-300 0;1900 0", 24), "wB": tr("translate", "-300 0;1900 0", 31, -12),
    "wC": tr("translate", "1900 0;-300 0", 27, -5), "wD": tr("translate", "1900 0;-300 0", 35, -20),
    "drift3": tr("translate", "0 0;-1400 0", 240), "drift4": tr("translate", "0 0;-1400 0", 150),
    "sat": tr("translate", "0 0;1900 -60", 60),
    "rain": tr("translate", "0 0;-90 1000", 1.6),
    "streak": tr("translate", "0 -1200;0 1200", 16), "streak b": tr("translate", "0 -1200;0 1200", 23, -9),
    "sheenV": tr("translate", "0 0;0 0;0 1500", 10, key_times="0;.55;1"),
}


def smoke(i, tag):
    r0 = float(re.search(r'\br="([\d.]+)"', tag).group(1))
    b = -1.2 * i
    return (attr("cy", "670;530", 6, b) + attr("cx", "341;381", 6, b)
            + attr("r", f"{r0 * .6:.1f};{r0 * 2.2:.1f}", 6, b) + attr("opacity", ".45;0", 6, b))


TAG = re.compile(r'<([a-zA-Z]+)(\s[^<>]*?)?\sclass="([^"]+)"([^<>]*?)(/?)>')


def smilify(svg):
    def sub(m):
        name, classes, closing = m.group(1), m.group(3).split(), m.group(5)
        whole = m.group(0)
        kids = ""
        joined = " ".join(c for c in classes if c in ("streak", "b"))
        if joined == "streak b":
            kids += ANIM["streak b"]
        else:
            for c in classes:
                if c in ANIM:
                    kids += ANIM[c]
        if "smoke" in classes:
            idx = next((int(c[1:]) for c in classes if re.fullmatch(r"s\d", c)), 0)
            kids += smoke(idx, whole)
        if not kids:
            return whole
        if closing:
            return whole[:-2] + f">{kids}</{name}>"
        return whole + kids

    head, sep, body = svg.partition("</style>")
    return head + sep + TAG.sub(sub, body) if sep else TAG.sub(sub, svg)


# --- Frames on a clock -------------------------------------------------------
# The desktop app paints a backdrop as a still frame and runs neither CSS nor
# SMIL animation in it. So every CSS animation's delay is pushed back by
# var(--t): the mod redraws the scene each second with :root{--t:<seconds>s},
# and each still frame shows the scene that much further along.

TIME = re.compile(r"^-?\d*\.?\d+m?s$")


def _shift_animation(decl):
    tokens = decl.split()
    times = [i for i, t in enumerate(tokens) if TIME.match(t)]
    if not times:
        return None
    delay = tokens[times[1]] if len(times) > 1 else "0s"
    if len(times) > 1:
        del tokens[times[1]]
    return f"animation:{' '.join(tokens)};animation-delay:calc({delay} - var(--t,0s))"


def timeshift(svg):
    head, sep, rest = svg.partition("<style>")
    if not sep:
        return svg
    css, sep2, tail = rest.partition("</style>")

    def anim(m):
        shifted = _shift_animation(m.group(1))
        return shifted if shifted else m.group(0)

    css = re.sub(r"animation:([^;{}!]+)(?=[;}])", anim, css)
    css = re.sub(r"animation-delay:(-?\d*\.?\d+m?s)(?=[;}])", r"animation-delay:calc(\1 - var(--t,0s))", css)
    return head + sep + css + sep2 + tail
