"""
Generates the LoreCraftian-themed SVG banners for the GitHub profile README.

Every banner is written twice, img/lorecraft/<name>-dark.svg and -light.svg,
and the README swaps them with <picture> to follow the visitor's GitHub theme.
The three fonts (Orbitron, Cormorant Garamond italic, Alata) are embedded as
subsets containing only the letters each image uses, so the files stay small
and look identical everywhere. Animations are plain CSS/SMIL inside the SVG,
which GitHub plays in <img>.

    pip install fonttools brotli
    python scripts/generate.py
"""

from __future__ import annotations

import base64
import io
import math
import random
from datetime import date
import json
from pathlib import Path
from xml.sax.saxutils import escape

from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "img" / "lorecraft"
FONT_DIR = Path(__file__).resolve().parent / "fonts"

FONTS = {
    # css family -> (file, variable-axis instance)
    "LcDisplay": ("Orbitron.woff2", {"wght": 800}),
    "LcSerif": ("CormorantGaramond-Italic.woff2", {"wght": 500}),
    "LcBody": ("Alata.woff2", None),
}

# Year counts are calculated, never typed. A GitHub Action regenerates the
# banners every 1 January so they roll over on their own.
SINCE = 2019
YEARS = date.today().year - SINCE
_WORDS = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty".split()
YEARS_WORD = (_WORDS[YEARS] if YEARS < len(_WORDS) else str(YEARS)).capitalize()

THEMES = {
    "dark": dict(
        bg0="#0b0816", bg1="#160f2a", bg2="#221642", ink="#e8e6e0", soft="#a9a3b4", faint="#6f6880",
        gold="#d6ac5c", goldhi="#f6d68c", golddeep="#a87a26", line="#d6ac5c", violet="#5b3fa8",
        teal="#46aab4", wax="#b02a2c", night="#1b1236", star="#e8e6e0", card="#140d26",
        neb_a="#5b3fa8", neb_b="#b02a2c", neb_c="#46aab4", neb_op=0.38, sheen="#fff3cf",
    ),
    "light": dict(
        bg0="#f6f1e5", bg1="#efe6d2", bg2="#e4dcf3", ink="#1a1230", soft="#4f4763", faint="#7d7590",
        gold="#a87a26", goldhi="#8a5f12", golddeep="#6e4a0c", line="#a87a26", violet="#4a2f8f",
        teal="#2e7f88", wax="#a3262a", night="#cfc3ea", star="#6b5aa8", card="#fffbf1",
        neb_a="#7c5ed6", neb_b="#d6785a", neb_c="#46aab4", neb_op=0.2, sheen="#c9962f",
    ),
}

_font_cache: dict[str, TTFont] = {}


def font_face(family: str, text: str) -> str:
    buf = io.BytesIO()
    src = io.BytesIO()
    _font(family).save(src)
    src.seek(0)
    sub = TTFont(src)
    opts = Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga"]
    s = Subsetter(opts)
    s.populate(text="".join(sorted(set(text + " "))))
    s.subset(sub)
    sub.flavor = "woff2"
    sub.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"@font-face{{font-family:{family};src:url(data:font/woff2;base64,{b64}) format('woff2');}}"


def _font(family: str) -> TTFont:
    file, axes = FONTS[family]
    if file not in _font_cache:
        f = TTFont(FONT_DIR / file)
        if axes and "fvar" in f:
            f = instancer.instantiateVariableFont(f, axes)
        _font_cache[file] = f
    return _font_cache[file]


def measure(text: str, family: str, size: float, ls: float = 0.0) -> float:
    """Advance width in px, from the font's own metrics (kerning ignored)."""
    f = _font(family)
    cmap, hmtx, upm = f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm
    w = sum(hmtx[cmap.get(ord(c), ".notdef")][0] for c in text)
    return w * size / upm + ls * size * len(text)


class Svg:
    """Collects text per font so each SVG embeds only the glyphs it needs."""

    def __init__(self, w: int, h: int, theme: str, title: str):
        self.w, self.h, self.t, self.title = w, h, THEMES[theme], title
        self.used: dict[str, str] = {k: "" for k in FONTS}
        self.css: list[str] = []
        self.defs: list[str] = []
        self.body: list[str] = []

    def text(self, x, y, s, family="LcBody", size=16, fill=None, anchor="start", ls=0.0, extra="", cls="", css=""):
        self.used[family] += s
        fill = fill or self.t["ink"]
        style = f"font-family:{family};font-size:{size}px;letter-spacing:{ls}em;{css}"
        c = f' class="{cls}"' if cls else ""
        self.body.append(
            f'<text x="{x}" y="{y}" fill="{fill}" text-anchor="{anchor}" style="{style}"{c} {extra}>{escape(s)}</text>'
        )

    def render(self) -> str:
        faces = "".join(font_face(f, txt) for f, txt in self.used.items() if txt)
        css = (
            faces
            + "".join(self.css)
            + "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"
        )
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
            f'viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{escape(self.title)}">'
            f"<title>{escape(self.title)}</title>"
            f"<style>{css}</style><defs>{''.join(self.defs)}</defs>{''.join(self.body)}</svg>"
        )


# --------------------------------------------------------------- pieces ---


def sky(svg: Svg, seed: int, stars: int = 120, rounded: int = 22):
    t = svg.t
    w, h = svg.w, svg.h
    svg.defs.append(
        f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{t["bg0"]}"/><stop offset="0.6" stop-color="{t["bg1"]}"/>'
        f'<stop offset="1" stop-color="{t["bg2"]}"/></linearGradient>'
        f'<radialGradient id="nebA"><stop offset="0" stop-color="{t["neb_a"]}" stop-opacity="{t["neb_op"]}"/>'
        f'<stop offset="1" stop-color="{t["neb_a"]}" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="nebB"><stop offset="0" stop-color="{t["neb_b"]}" stop-opacity="{t["neb_op"] * 0.5}"/>'
        f'<stop offset="1" stop-color="{t["neb_b"]}" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="nebC"><stop offset="0" stop-color="{t["neb_c"]}" stop-opacity="{t["neb_op"] * 0.45}"/>'
        f'<stop offset="1" stop-color="{t["neb_c"]}" stop-opacity="0"/></radialGradient>'
        f'<clipPath id="frame"><rect width="{w}" height="{h}" rx="{rounded}"/></clipPath>'
    )
    svg.css.append(
        "@keyframes tw{0%,100%{opacity:.25}50%{opacity:1}}"
        ".st{animation:tw var(--d,4s) ease-in-out infinite}"
        "@keyframes drift{from{transform:translate(-20px,-8px) scale(1)}to{transform:translate(24px,10px) scale(1.08)}}"
        ".neb{animation:drift 18s ease-in-out infinite alternate;transform-box:fill-box;transform-origin:center}"
    )
    rnd = random.Random(seed)
    g = [f'<g clip-path="url(#frame)"><rect width="{w}" height="{h}" fill="url(#bg)"/>']
    g.append(f'<ellipse class="neb" cx="{w * 0.78}" cy="{h * 0.25}" rx="{w * 0.38}" ry="{h * 0.6}" fill="url(#nebA)"/>')
    g.append(f'<ellipse class="neb" cx="{w * 0.12}" cy="{h * 0.85}" rx="{w * 0.3}" ry="{h * 0.5}" fill="url(#nebB)" style="animation-delay:-6s"/>')
    g.append(f'<ellipse class="neb" cx="{w * 0.55}" cy="{h * 0.95}" rx="{w * 0.25}" ry="{h * 0.4}" fill="url(#nebC)" style="animation-delay:-11s"/>')
    for _ in range(stars):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        big = rnd.random() < 0.06
        r = rnd.uniform(1.4, 2.2) if big else rnd.uniform(0.5, 1.2)
        col = rnd.choice([t["star"], t["star"], t["goldhi"], t["violet"]])
        g.append(
            f'<circle class="st" cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="{col}" '
            f'style="--d:{rnd.uniform(2.5, 6):.2f}s;animation-delay:-{rnd.uniform(0, 6):.2f}s"/>'
        )
    g.append("</g>")
    svg.body.extend(g)


def frame_border(svg: Svg, rounded: int = 22):
    t = svg.t
    svg.defs.append(
        f'<linearGradient id="rim" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{t["gold"]}" stop-opacity=".15"/>'
        f'<stop offset=".5" stop-color="{t["goldhi"]}" stop-opacity=".9"/>'
        f'<stop offset="1" stop-color="{t["gold"]}" stop-opacity=".15"/></linearGradient>'
    )
    svg.body.append(
        f'<rect x="1" y="1" width="{svg.w - 2}" height="{svg.h - 2}" rx="{rounded}" fill="none" stroke="url(#rim)" stroke-width="1.5"/>'
    )
    # gold corner studs, the motion-library frame language
    s, p = 16, 12
    pts = [(p, p, 1, 1), (svg.w - p, p, -1, 1), (p, svg.h - p, 1, -1), (svg.w - p, svg.h - p, -1, -1)]
    for x, y, dx, dy in pts:
        svg.body.append(
            f'<path d="M{x} {y + dy * s} L{x} {y} L{x + dx * s} {y}" fill="none" stroke="{t["gold"]}" stroke-width="1.6"/>'
        )


def medallion(svg: Svg, cx: float, cy: float, r: float, uid: str):
    """Astrolabe ornament: rings, ticks and a breathing core, turning."""
    t = svg.t
    svg.defs.append(
        f'<radialGradient id="core{uid}"><stop offset="0" stop-color="{t["goldhi"]}" stop-opacity=".95"/>'
        f'<stop offset=".45" stop-color="{t["gold"]}" stop-opacity=".35"/>'
        f'<stop offset="1" stop-color="{t["gold"]}" stop-opacity="0"/></radialGradient>'
    )
    svg.css.append(
        "@keyframes spin{to{transform:rotate(360deg)}}"
        "@keyframes breathe{0%,100%{opacity:.35;transform:scale(.85)}50%{opacity:1;transform:scale(1.12)}}"
        ".spinA{animation:spin 40s linear infinite;transform-box:view-box}"
        ".spinB{animation:spin 26s linear infinite reverse;transform-box:view-box}"
        ".core{animation:breathe 4.5s ease-in-out infinite;transform-box:fill-box;transform-origin:center}"
    )
    k = r / 92
    ticks = []
    for i in range(48):
        a = i / 48 * math.tau
        r1 = (76 if i % 4 == 0 else 80) * k
        ticks.append(
            f'<line x1="{cx + math.cos(a) * r1:.2f}" y1="{cy + math.sin(a) * r1:.2f}" '
            f'x2="{cx + math.cos(a) * 86 * k:.2f}" y2="{cy + math.sin(a) * 86 * k:.2f}"/>'
        )
    o = f"transform-origin:{cx}px {cy}px"
    svg.body.append(
        f'<g fill="none" stroke="{t["gold"]}">'
        f'<circle class="core" cx="{cx}" cy="{cy}" r="{38 * k}" fill="url(#core{uid})" stroke="none"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{92 * k}" stroke-width="1.4"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{70 * k}" stroke="{t["goldhi"]}" stroke-width=".6" opacity=".7"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{30 * k}" stroke-width="1.4"/>'
        f'<g class="spinA" style="{o}" opacity=".75">{"".join(ticks)}</g>'
        f'<g class="spinB" style="{o}"><circle cx="{cx}" cy="{cy}" r="{52 * k}" stroke-dasharray="2 6" opacity=".8"/>'
        f'<path d="M{cx} {cy - 60 * k} L{cx + 6 * k} {cy} L{cx} {cy + 60 * k} L{cx - 6 * k} {cy} Z" fill="{t["gold"]}" fill-opacity=".2" stroke-width=".8"/>'
        f'<path d="M{cx - 60 * k} {cy} L{cx} {cy - 6 * k} L{cx + 60 * k} {cy} L{cx} {cy + 6 * k} Z" fill="{t["gold"]}" fill-opacity=".2" stroke-width=".8"/></g>'
        f'<circle cx="{cx}" cy="{cy}" r="{5 * k}" fill="{t["goldhi"]}" stroke="none"/></g>'
    )


def gold_sheen(svg: Svg, gid: str, x0: float, x1: float):
    t = svg.t
    span = x1 - x0
    svg.defs.append(
        f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{x0}" y1="0" x2="{x1}" y2="0">'
        f'<stop offset="0" stop-color="{t["golddeep"]}"/><stop offset=".3" stop-color="{t["gold"]}"/>'
        f'<stop offset=".48" stop-color="{t["goldhi"]}"/><stop offset=".52" stop-color="{t["sheen"]}"/>'
        f'<stop offset=".56" stop-color="{t["goldhi"]}"/><stop offset=".8" stop-color="{t["gold"]}"/>'
        f'<stop offset="1" stop-color="{t["golddeep"]}"/>'
        f'<animateTransform attributeName="gradientTransform" type="translate" values="{-span} 0;{span} 0" dur="7s" repeatCount="indefinite"/>'
        f"</linearGradient>"
    )
    return f"url(#{gid})"


def planet(svg: Svg, cx: float, cy: float, R: float, tilt: float = -16, outer: float = 2.55):
    t = svg.t
    dark = t is THEMES["dark"]
    bands = ["#46aab4", "#5b3fa8", "#eee2c8", "#d6ac5c", "#dc8446", "#f6d68c", "#5b3fa8", "#46aab4"]
    if not dark:
        bands = ["#2e7f88", "#4a2f8f", "#c9b48a", "#a87a26", "#b8552a", "#c8962e", "#4a2f8f", "#2e7f88"]
    stops = "".join(f'<stop offset="{i / (len(bands) - 1):.3f}" stop-color="{c}"/>' for i, c in enumerate(bands))
    svg.defs.append(
        f'<linearGradient id="bands" x1="0" y1="0" x2="0.18" y2="1">{stops}</linearGradient>'
        f'<radialGradient id="shade" cx="0.28" cy="0.28" r="0.95">'
        f'<stop offset="0" stop-color="#fff6dc" stop-opacity=".35"/><stop offset=".45" stop-color="{t["night"]}" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="{t["night"]}" stop-opacity=".88"/></radialGradient>'
        f'<radialGradient id="halo"><stop offset=".55" stop-color="{t["goldhi"]}" stop-opacity="{".35" if dark else ".1"}"/>'
        f'<stop offset="1" stop-color="{t["goldhi"]}" stop-opacity="0"/></radialGradient>'
        f'<pattern id="dots" width="7" height="7" patternUnits="userSpaceOnUse">'
        f'<circle cx="3.5" cy="3.5" r="1.1" fill="#fff" fill-opacity=".22"/></pattern>'
        f'<clipPath id="pclip"><circle cx="{cx}" cy="{cy}" r="{R}"/></clipPath>'
        # front half of the rings: the part below the ring plane's centre line
        f'<clipPath id="front"><rect x="{cx - 400}" y="{cy}" width="800" height="400"/></clipPath>'
    )
    svg.css.append(
        "@keyframes flow{to{stroke-dashoffset:-400}}"
        ".ring{animation:flow var(--s,30s) linear infinite}"
        "@keyframes orbit{to{transform:rotate(360deg)}}"
        ".orb{animation:orbit var(--s,80s) linear infinite;transform-box:view-box}"
        "@keyframes band{to{transform:translateX(-120px)}}"
        ".bandmove{animation:band 40s linear infinite alternate}"
    )
    rings = []
    rnd = random.Random(5)
    ring_cols = [t["goldhi"], t["gold"], t["ink"] if dark else t["golddeep"], t["golddeep"]]
    r = R * 1.42
    while r < R * outer:
        if not (R * 1.86 < r < R * 1.95 or R * 2.32 < r < R * 2.38):
            col = ring_cols[int(r) % len(ring_cols)]
            dash = f"{rnd.uniform(0.6, 2.4):.1f} {rnd.uniform(3, 9):.1f}"
            rings.append(
                f'<ellipse class="ring" cx="{cx}" cy="{cy}" rx="{r:.1f}" ry="{r * 0.24:.1f}" fill="none" '
                f'stroke="{col}" stroke-width="{rnd.uniform(0.8, 1.9):.2f}" stroke-linecap="round" '
                f'stroke-dasharray="{dash}" opacity="{rnd.uniform(0.35, 0.95):.2f}" '
                f'style="--s:{rnd.uniform(18, 40):.1f}s"/>'
            )
        r += rnd.uniform(3.2, 5.5)
    ring_markup = "".join(rings)
    rot = f'transform="rotate({tilt} {cx} {cy})"'

    # orbit lines (the turning gold rings of the motion library)
    orbits = []
    for i, (rx, ry, ang, s) in enumerate([(R * 3.1, R * 1.05, 24, 90), (R * 3.6, R * 0.8, -12, 120), (R * 2.7, R * 2.0, 58, 70)]):
        orbits.append(
            f'<g class="orb" style="transform-origin:{cx}px {cy}px;--s:{s}s;animation-direction:{"reverse" if i % 2 else "normal"}">'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx:.0f}" ry="{ry:.0f}" transform="rotate({ang} {cx} {cy})" fill="none" '
            f'stroke="{t["gold"]}" stroke-opacity=".32" stroke-width="1"/>'
            f'<circle cx="{cx + rx * math.cos(math.radians(ang)):.1f}" cy="{cy + rx * math.sin(math.radians(ang)):.1f}" r="3" fill="{t["goldhi"]}"/></g>'
        )
    svg.body.append("".join(orbits))
    svg.body.append(f'<circle cx="{cx}" cy="{cy}" r="{R * 1.35}" fill="url(#halo)"/>')
    svg.body.append(f"<g {rot}>{ring_markup}</g>")  # back of the rings, behind the planet
    svg.body.append(particle_sphere(svg, cx, cy, R, bands, dark))
    svg.body.append(
        f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{t["goldhi"]}" stroke-opacity=".55" stroke-width="1.2" '
        f'stroke-dasharray="{R * 1.6:.0f} {R * 6:.0f}" stroke-dashoffset="{R * 3.6:.0f}"/>'
    )
    svg.body.append(f'<g {rot}><g clip-path="url(#front)">{ring_markup}</g></g>')  # front of the rings


def particle_sphere(svg: Svg, cx: float, cy: float, R: float, palette: list[str], dark: bool) -> str:
    """The portfolio's planet: a Fibonacci sphere of points, banded and lit
    from the upper left, with the night side kept violet (never black)."""
    t = svg.t
    n = int(R * 9)
    golden = math.pi * (3 - math.sqrt(5))
    light = (-0.75, 0.5, 0.6)
    ll = math.sqrt(sum(c * c for c in light))
    light = tuple(c / ll for c in light)
    tilt = math.radians(18)
    rnd = random.Random(3)

    def hexrgb(h):
        return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))

    pal = [hexrgb(c) for c in palette]
    night = hexrgb("#3d2a7a" if dark else "#b9acd9")
    out = []
    for i in range(n):
        y = 1 - i / (n - 1) * 2
        rad = math.sqrt(max(0.0, 1 - y * y))
        th = golden * i
        x, z = math.cos(th) * rad, math.sin(th) * rad
        # tilt the sphere toward the viewer slightly
        y2 = y * math.cos(tilt) - z * math.sin(tilt)
        z2 = y * math.sin(tilt) + z * math.cos(tilt)
        if z2 < -0.05:
            continue
        band = y * 5.2 + math.sin(th * 3.1) * 0.08
        k = int(band % len(pal))
        f = band - math.floor(band)
        a, b = pal[k], pal[(k + 1) % len(pal)]
        mix = max(0.0, (f - 0.55) / 0.45)
        base = tuple(a[j] + (b[j] - a[j]) * mix for j in range(3))
        lit = x * light[0] + y2 * light[1] + z2 * light[2]
        lit = min(1.0, max(0.0, (lit + 0.35) / 1.2))
        rim = (1 - max(0.0, z2)) ** 3
        col = tuple(int(min(255, night[j] * (1 - lit) + base[j] * (0.55 + 0.75 * lit) + 255 * rim * lit * 0.35)) for j in range(3))
        op = (0.35 + 0.65 * lit) * (0.55 + 0.45 * max(0.0, z2)) + rim * 0.3
        r = 0.9 + 1.3 * max(0.0, z2) * rnd.uniform(0.7, 1.2)
        tw = ' class="st" style="--d:%.1fs;animation-delay:-%.1fs"' % (rnd.uniform(2, 5), rnd.uniform(0, 5)) if rnd.random() < 0.18 else ""
        out.append(
            f'<circle cx="{cx + x * R:.1f}" cy="{cy - y2 * R:.1f}" r="{r:.2f}" '
            f'fill="rgb{col}" fill-opacity="{min(1.0, op):.2f}"{tw}/>'
        )
    return "<g>" + "".join(out) + "</g>"


def dust(svg: Svg, seed: int, n: int = 26):
    t = svg.t
    svg.css.append(
        "@keyframes rise{0%{transform:translateY(0);opacity:0}15%{opacity:1}100%{transform:translateY(-140px);opacity:0}}"
        ".du{animation:rise var(--d,9s) linear infinite}"
    )
    rnd = random.Random(seed)
    for _ in range(n):
        svg.body.append(
            f'<circle class="du" cx="{rnd.uniform(0, svg.w):.0f}" cy="{rnd.uniform(svg.h * 0.4, svg.h):.0f}" '
            f'r="{rnd.uniform(0.8, 2.2):.1f}" fill="{t["goldhi"]}" '
            f'style="--d:{rnd.uniform(7, 14):.1f}s;animation-delay:-{rnd.uniform(0, 14):.1f}s"/>'
        )


def wrap(s: str, size: float, width: float, factor: float = 0.5) -> list[str]:
    per = max(10, int(width / (size * factor)))
    words, lines, cur = s.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > per and cur:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return lines


# --------------------------------------------------------------- banners ---


def hero(theme: str) -> str:
    svg = Svg(1200, 520, theme, "Saif Rahman: I architect intelligent web ecosystems")
    t = svg.t
    sky(svg, 11, 170)
    planet(svg, 930, 245, 108, tilt=17, outer=2.35)
    dust(svg, 4)
    frame_border(svg)
    svg.css.append(
        "@keyframes up{from{opacity:0;transform:translateY(22px)}to{opacity:1;transform:none}}"
        ".u1,.u2,.u3,.u4,.u5{animation:up 1.2s cubic-bezier(.16,1,.3,1) both}"
        ".u2{animation-delay:.12s}.u3{animation-delay:.24s}.u4{animation-delay:.36s}.u5{animation-delay:.6s}"
        "@keyframes blink{50%{opacity:0}}.cur{animation:blink 1s steps(1) infinite}"
        "@keyframes roles{0%,22%{opacity:1}25%,100%{opacity:0}}"
        ".role{opacity:0;animation:roles 12s infinite}"
    )
    # HUD readouts
    svg.text(64, 52, "23.81° N · 90.41° E", "LcDisplay", 11, t["faint"], ls=0.18)
    svg.text(1136, 52, f"ORBIT · {YEARS} YRS", "LcDisplay", 11, t["faint"], "end", ls=0.18)
    svg.body.append(f'<line x1="64" y1="98" x2="94" y2="98" stroke="{t["gold"]}"/>')
    svg.text(104, 103, "SENIOR SOFTWARE ENGINEER · AI-AUGMENTED · SINCE 2019", "LcDisplay", 12.5, t["gold"], ls=0.2, cls="u1")
    svg.text(60, 186, "I ARCHITECT", "LcDisplay", 68, t["ink"], ls=-0.01, cls="u2")
    sheen = gold_sheen(svg, "sheen", 60, 520)
    svg.text(62, 278, "intelligent", "LcSerif", 96, sheen, cls="u3")
    svg.text(60, 364, "WEB", "LcDisplay", 68, t["ink"], cls="u4")
    svg.used["LcDisplay"] += "ECOSYSTEMS."
    svg.body.append(
        f'<text x="{60 + measure("WEB ", "LcDisplay", 68):.0f}" y="364" class="u4" fill="none" stroke="{t["gold"]}" stroke-width="1.3" '
        f'style="font-family:LcDisplay;font-size:68px">ECOSYSTEMS.</text>'
    )
    # cycling role line
    roles = [
        "Turning business needs into shipped products",
        "Building with AI: faster, tested, more secure",
        "Not married to any stack, obsessed with the product",
        "End to end: schema, API, interface, launch",
    ]
    for i, r in enumerate(roles):
        svg.text(64, 430, "› " + r, "LcBody", 21, t["soft"], cls="role", css=f"animation-delay:{i * 3}s")
    svg.text(64, 474, "Saif Rahman  ·  Dhaka, GMT+6  ·  engineersaif.com", "LcDisplay", 11.5, t["faint"], ls=0.16, cls="u5")
    # crosshairs
    for x, y in ((730, 120), (1110, 380)):
        svg.body.append(
            f'<path d="M{x - 7} {y} H{x + 7} M{x} {y - 7} V{y + 7}" stroke="{t["gold"]}" stroke-opacity=".6"/>'
        )
    return svg.render()


def stats(theme: str) -> str:
    svg = Svg(1200, 180, theme, f"{YEARS}+ years, 30+ projects, 100k+ users served, 30% average performance uplift")
    t = svg.t
    sky(svg, 21, 60)
    frame_border(svg)
    svg.css.append(
        "@keyframes glow{0%,100%{opacity:.55}50%{opacity:1}}.gl{animation:glow 3.6s ease-in-out infinite}"
        "@keyframes sweep{from{transform:translateX(-120px)}to{transform:translateX(320px)}}"
        ".sw{animation:sweep 4.5s cubic-bezier(.76,0,.24,1) infinite}"
    )
    svg.defs.append(
        f'<linearGradient id="swg"><stop offset="0" stop-color="{t["goldhi"]}" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="{t["goldhi"]}" stop-opacity=".12"/>'
        f'<stop offset="1" stop-color="{t["goldhi"]}" stop-opacity="0"/></linearGradient>'
    )
    items = [(f"{YEARS}+", "years writing software"), ("30+", "projects shipped"), ("100k+", "users served at peak"), ("30%", "avg. performance uplift")]
    cw = 1200 / 4
    for i, (n, l) in enumerate(items):
        x0 = i * cw
        if i:
            svg.body.append(f'<line x1="{x0}" y1="40" x2="{x0}" y2="140" stroke="{t["gold"]}" stroke-opacity=".25"/>')
        svg.body.append(
            f'<g clip-path="url(#frame)"><rect class="sw" x="{x0}" y="0" width="90" height="180" fill="url(#swg)" '
            f'style="animation-delay:{i * 0.6}s"/></g>'
        )
        svg.text(x0 + cw / 2, 98, n, "LcDisplay", 46, t["goldhi"], "middle", cls="gl",
                 css=f"animation-delay:{i * 0.9}s")
        svg.text(x0 + cw / 2, 132, l, "LcBody", 16, t["soft"], "middle")
    return svg.render()


def header(theme: str, num: str, label: str, plain: str, serif: str, tail: str = "") -> str:
    svg = Svg(1200, 150, theme, f"{label}: {plain} {serif} {tail}".strip())
    t = svg.t
    sky(svg, sum(map(ord, label)), 50)
    frame_border(svg)
    medallion(svg, 92, 75, 46, label[:3])
    svg.text(160, 58, f"{num} · {label.upper()}", "LcDisplay", 12, t["gold"], ls=0.22)
    # title: plain caps + gold serif italic, measured roughly to sit side by side
    svg.text(160, 108, plain.upper(), "LcDisplay", 34, t["ink"])
    plain_w = measure(plain.upper() + " ", "LcDisplay", 34)
    serif_w = measure(serif, "LcSerif", 46)
    sheen = gold_sheen(svg, f"sh{label[:3]}", 160 + plain_w, 160 + plain_w + serif_w)
    svg.text(160 + plain_w, 110, serif, "LcSerif", 46, sheen)
    if tail:
        svg.text(160 + plain_w + serif_w + 14, 108, tail.upper(), "LcDisplay", 34, t["ink"])
    svg.body.append(f'<line x1="160" y1="128" x2="1130" y2="128" stroke="{t["gold"]}" stroke-opacity=".22"/>')
    return svg.render()


EXPERIENCE = [
    ("2023 · NOW", "POWERLEY", "Senior Software Engineer", "Energy platform · Full-stack Next.js",
     "Architecting a 100k+ user platform end to end on Next.js and Node: API layer, data fetching and caching. Advanced caching and code-splitting drove a 30% performance boost and a 20% SEO uplift.", "30%", "faster"),
    ("2021 · 2023", "SUPERTAL", "Software Engineer", "Cross-platform web + mobile · Talent management",
     "Full-stack web and React Native features against Node/Express APIs. Optimised state with React Query, cutting redundant network calls by 35%, and streamlined CI/CD with GitHub Actions.", "35%", "fewer calls"),
    ("2020 · 2021", "FERNTECH SOLUTIONS", "Software Engineer", "SaaS · Raaga restaurant platform",
     "Built Raaga, an end-to-end SaaS for 100+ restaurants. Owned auth, realtime dashboards and a companion mobile ordering app that lifted engagement by 35%.", "100+", "restaurants"),
    ("2019", "RGB JUTE", "Web Developer", "E-commerce · Marketing automation",
     "Custom e-commerce and inventory tools. Automated marketing workflows with Python and Selenium, driving a 25% lift in online sales.", "25%", "more sales"),
]


def timeline(theme: str) -> str:
    row = 190
    top = 40
    svg = Svg(1200, top + row * len(EXPERIENCE) + 10, theme, "Experience: Powerley, Supertal, Ferntech Solutions, RGB Jute")
    t = svg.t
    sky(svg, 31, 90)
    frame_border(svg)
    spine_x = 230
    total = row * len(EXPERIENCE)
    svg.defs.append(
        f'<linearGradient id="spine" gradientUnits="userSpaceOnUse" x1="0" y1="{top}" x2="0" y2="{top + total}"><stop offset="0" stop-color="{t["goldhi"]}"/>'
        f'<stop offset=".6" stop-color="{t["gold"]}"/><stop offset="1" stop-color="{t["violet"]}"/></linearGradient>'
    )
    svg.css.append(
        f"@keyframes fill{{from{{stroke-dashoffset:{total}}}to{{stroke-dashoffset:0}}}}"
        f".spine{{stroke-dasharray:{total};animation:fill 3.2s cubic-bezier(.16,1,.3,1) both}}"
        "@keyframes ignite{0%{transform:scale(.3);opacity:.2}60%{transform:scale(1.25);opacity:1}100%{transform:scale(1);opacity:1}}"
        ".node{animation:ignite 1s cubic-bezier(.16,1,.3,1) both;transform-box:fill-box;transform-origin:center}"
        "@keyframes pulse{0%,100%{opacity:.25;transform:scale(1)}50%{opacity:.9;transform:scale(1.6)}}"
        ".halo{animation:pulse 3s ease-in-out infinite;transform-box:fill-box;transform-origin:center}"
        "@keyframes slide{from{opacity:0;transform:translateX(26px)}to{opacity:1;transform:none}}"
        ".card{animation:slide 1s cubic-bezier(.16,1,.3,1) both}"
    )
    svg.body.append(f'<line x1="{spine_x}" y1="{top}" x2="{spine_x}" y2="{top + total - 40}" stroke="{t["gold"]}" stroke-opacity=".2"/>')
    svg.body.append(f'<line class="spine" x1="{spine_x}" y1="{top}" x2="{spine_x}" y2="{top + total - 40}" stroke="url(#spine)" stroke-width="2"/>')
    for i, (yrs, co, role, ctx, summ, metric, mlabel) in enumerate(EXPERIENCE):
        y = top + i * row
        d = 0.5 + i * 0.6
        svg.text(spine_x - 34, y + 30, yrs, "LcDisplay", 12, t["gold"], "end", ls=0.14)
        svg.text(spine_x - 34, y + 92, f"0{i + 1}", "LcDisplay", 54, "none", "end",
                 extra=f'stroke="{t["gold"]}" stroke-opacity=".45" stroke-width="1"')
        svg.body.append(f'<circle class="halo" cx="{spine_x}" cy="{y + 24}" r="16" fill="{t["goldhi"]}" opacity=".3" style="animation-delay:{d}s"/>')
        svg.body.append(
            f'<g class="node" style="animation-delay:{d}s"><circle cx="{spine_x}" cy="{y + 24}" r="15" fill="{t["bg0"]}" stroke="{t["gold"]}" stroke-width="1.3"/>'
            f'<circle cx="{spine_x}" cy="{y + 24}" r="9" fill="none" stroke="{t["goldhi"]}" stroke-dasharray="2 3"/>'
            f'<circle cx="{spine_x}" cy="{y + 24}" r="4" fill="{t["goldhi"]}"/></g>'
        )
        cx0 = spine_x + 50
        svg.body.append(f'<g class="card" style="animation-delay:{d + 0.1}s">')
        svg.body.append(
            f'<rect x="{cx0}" y="{y}" width="{1200 - cx0 - 40}" height="{row - 22}" rx="18" fill="{t["card"]}" '
            f'fill-opacity=".72" stroke="{t["gold"]}" stroke-opacity=".28"/>'
        )
        svg.text(cx0 + 28, y + 42, co, "LcDisplay", 24, t["ink"])
        svg.text(cx0 + 28, y + 70, role, "LcSerif", 22, t["goldhi"])
        svg.text(1200 - 70, y + 46, metric, "LcDisplay", 32, t["goldhi"], "end")
        svg.text(1200 - 70, y + 68, mlabel, "LcBody", 13, t["faint"], "end")
        svg.text(cx0 + 28, y + 96, ctx.upper(), "LcDisplay", 10.5, t["faint"], ls=0.14)
        for j, line in enumerate(wrap(summ, 15.5, 1200 - cx0 - 110, 0.5)):
            svg.text(cx0 + 28, y + 124 + j * 22, line, "LcBody", 15.5, t["soft"])
        svg.body.append("</g>")
    return svg.render()


def footer(theme: str) -> str:
    svg = Svg(1200, 300, theme, "Architecting intelligent web ecosystems. info@engineersaif.com")
    t = svg.t
    sky(svg, 41, 110)
    planet(svg, 1010, 150, 70)
    dust(svg, 9, 18)
    frame_border(svg)
    medallion(svg, 110, 150, 60, "ft")
    svg.text(200, 92, "09 · CONTACT", "LcDisplay", 12, t["gold"], ls=0.22)
    svg.text(200, 150, "ARCHITECTING", "LcDisplay", 46, t["ink"])
    x = 200 + measure("ARCHITECTING ", "LcDisplay", 46)
    sheen = gold_sheen(svg, "fsheen", x, x + measure("intelligent", "LcSerif", 62))
    svg.text(x, 150, "intelligent", "LcSerif", 62, sheen)
    svg.text(200, 204, "WEB ECOSYSTEMS", "LcDisplay", 46, t["ink"])
    svg.text(200, 252, "info@engineersaif.com  ·  available for hire", "LcSerif", 26, t["goldhi"])
    return svg.render()


# --------------------------------------------------------------- signals ---

SIGNALS_FILE = Path(__file__).resolve().parent / "signals.json"
LANG_COLORS = {
    "dark": ["#f6d68c", "#8a6cf0", "#46aab4", "#dc8446", "#e8e6e0", "#c86a8a", "#a87a26"],
    "light": ["#a87a26", "#4a2f8f", "#2e7f88", "#b8552a", "#6b5f80", "#a3405f", "#6e4a0c"],
}


def fmt(n: int) -> str:
    return f"{n:,}"


def signals(theme: str) -> str:
    """GitHub numbers from scripts/signals.json, drawn in the LoreCraftian style."""
    d = json.loads(SIGNALS_FILE.read_text(encoding="utf-8"))
    svg = Svg(1200, 480, theme, (
        f"GitHub signals: {d['stars']} stars, {d['contributions_total']} contributions since {d['since']}, "
        f"current streak {d['current']} days, longest {d['longest']} days."))
    t = svg.t
    sky(svg, 77, 110)
    frame_border(svg)
    svg.css.append(
        "@keyframes ring{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}"
        ".ringfill{animation:ring 2.4s cubic-bezier(.16,1,.3,1) .3s both}"
        "@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}"
        ".seg{transform-box:fill-box;transform-origin:left;animation:grow 1.4s cubic-bezier(.16,1,.3,1) both}"
        "@keyframes rise2{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}"
        ".rs{animation:rise2 1s cubic-bezier(.16,1,.3,1) both}"
        "@keyframes glow{0%,100%{opacity:.6}50%{opacity:1}}.gl{animation:glow 3.6s ease-in-out infinite}"
        "@keyframes orbitc{to{transform:rotate(360deg)}}.cm{animation:orbitc 6s linear infinite;transform-box:view-box}"
    )
    svg.text(1160, 40, f"LIVE FROM GITHUB · UPDATED {d['updated']}", "LcDisplay", 9.5, t["faint"], "end", ls=0.16)

    # Row 1: four signals; the current streak is a gold ring
    cols = [
        (fmt(d["stars"]), "stars earned", f"across {d['repos']} repositories"),
        (fmt(d["contributions_total"]), "contributions", f"since {d['since']}"),
        None,
        (fmt(d["longest"]), "longest streak", "days in a row"),
    ]
    cw = 1120 / 4
    for i, c in enumerate(cols):
        cx = 40 + cw * i + cw / 2
        if i:
            svg.body.append(f'<line x1="{40 + cw * i}" y1="62" x2="{40 + cw * i}" y2="196" stroke="{t["gold"]}" stroke-opacity=".22"/>')
        delay = f"animation-delay:{0.15 * i:.2f}s"
        if c is None:
            frac = min(1.0, d["current"] / max(d["longest"], 1))
            r = 66
            svg.body.append(f'<circle cx="{cx}" cy="124" r="{r}" fill="none" stroke="{t["gold"]}" stroke-opacity=".18" stroke-width="5"/>')
            svg.body.append(
                f'<circle class="ringfill" cx="{cx}" cy="124" r="{r}" fill="none" stroke="{t["goldhi"]}" stroke-width="5" '
                f'stroke-linecap="round" pathLength="1" transform="rotate(-90 {cx} 124)" '
                f'style="stroke-dasharray:{frac:.3f} 1"/>'
            )
            svg.body.append(
                f'<g class="cm" style="transform-origin:{cx}px 124px"><circle cx="{cx}" cy="{124 - r}" r="5" fill="{t["goldhi"]}"/>'
                f'<circle cx="{cx}" cy="{124 - r}" r="11" fill="{t["goldhi"]}" opacity=".2"/></g>'
            )
            svg.text(cx, 130, fmt(d["current"]), "LcDisplay", 24, t["goldhi"], "middle", cls="gl")
            svg.text(cx, 150, "DAY STREAK", "LcDisplay", 8.5, t["soft"], "middle", ls=0.18)
            svg.text(cx, 214, f"current, since {d['current_since']}", "LcBody", 13, t["faint"], "middle")
            continue
        n, label, sub = c
        svg.text(cx, 128, n, "LcDisplay", 44, t["goldhi"], "middle", cls="rs gl", css=delay)
        svg.text(cx, 160, label, "LcBody", 17, t["ink"], "middle", cls="rs", css=delay)
        svg.text(cx, 184, sub, "LcBody", 13, t["faint"], "middle", cls="rs", css=delay)

    svg.body.append(f'<line x1="60" y1="234" x2="1140" y2="234" stroke="{t["gold"]}" stroke-opacity=".2"/>')

    # Row 2, left: the last year as a constellation of gold dots
    cal = d["calendar"]
    mx = max(cal) or 1
    x0, y0, step = 64, 296, 12.6
    svg.text(x0, 270, f"LAST 12 MONTHS · {fmt(d['contributions_year'])} CONTRIBUTIONS", "LcDisplay", 10.5, t["gold"], ls=0.18)
    rnd = random.Random(9)
    for k, v in enumerate(cal):
        col, row = divmod(k, 7)
        x, y = x0 + col * step, y0 + row * step
        if v == 0:
            svg.body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.1" fill="{t["faint"]}" opacity=".5"/>')
            continue
        lvl = math.sqrt(v / mx)
        r = 1.8 + 3.2 * lvl
        tw = (f' class="st" style="--d:{rnd.uniform(2, 5):.1f}s;animation-delay:-{rnd.uniform(0, 5):.1f}s"'
              if lvl > 0.55 else "")
        svg.body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="{t["goldhi"]}" fill-opacity="{0.35 + 0.65 * lvl:.2f}"{tw}/>')
    svg.text(x0, y0 + 7 * step + 18, "a year ago", "LcBody", 12, t["faint"])
    svg.text(x0 + 51 * step, y0 + 7 * step + 18, "today", "LcBody", 12, t["faint"], "end")

    # Row 2, right: languages
    lx, lw = 780, 360
    svg.text(lx, 270, "LANGUAGES · BY CODE VOLUME", "LcDisplay", 10.5, t["gold"], ls=0.18)
    cols_l = LANG_COLORS[theme]
    x = lx
    for i, lang in enumerate(d["languages"]):
        w = lw * lang["pct"] / 100
        svg.body.append(
            f'<rect class="seg" x="{x:.1f}" y="292" width="{max(w - 2, 1):.1f}" height="12" rx="3" fill="{cols_l[i % len(cols_l)]}" '
            f'style="animation-delay:{0.3 + i * 0.12:.2f}s"/>'
        )
        x += w
    for i, lang in enumerate(d["languages"]):
        cx_, cy_ = lx + (i % 2) * 190, 338 + (i // 2) * 30
        svg.body.append(f'<circle cx="{cx_ + 6}" cy="{cy_ - 5}" r="5" fill="{cols_l[i % len(cols_l)]}"/>')
        svg.text(cx_ + 20, cy_, lang["name"], "LcBody", 15, t["ink"])
        svg.text(cx_ + 170, cy_, f"{lang['pct']}%", "LcDisplay", 11, t["soft"], "end")
    return svg.render()


def closing(theme: str) -> str:
    """The sign-off: stars that draw themselves into a heart, a shooting star, the planet."""
    svg = Svg(1200, 400, theme, "Since you came this far, this one is for you. Thank you for reading.")
    t = svg.t
    sky(svg, 88, 150)
    planet(svg, 1050, 300, 52, tilt=-14, outer=2.3)
    dust(svg, 12, 22)
    frame_border(svg)
    svg.css.append(
        "@keyframes draw{0%{stroke-dashoffset:1;opacity:1}45%{stroke-dashoffset:0;opacity:1}85%{stroke-dashoffset:0;opacity:1}100%{stroke-dashoffset:0;opacity:0}}"
        ".heart{stroke-dasharray:1;animation:draw 9s ease-in-out infinite}"
        "@keyframes core{0%,100%{opacity:.35;transform:scale(.85)}50%{opacity:.9;transform:scale(1.15)}}"
        ".hc{animation:core 4.5s ease-in-out infinite;transform-box:fill-box;transform-origin:center}"
        "@keyframes shoot{0%{transform:translate(0,0);opacity:0}4%{opacity:1}14%{transform:translate(520px,170px);opacity:0}100%{opacity:0}}"
        ".shoot{animation:shoot 7s ease-in infinite}"
    )
    svg.defs.append(
        f'<linearGradient id="trail" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t["goldhi"]}" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="{t["goldhi"]}"/></linearGradient>'
        f'<radialGradient id="hcore"><stop offset="0" stop-color="{t["goldhi"]}" stop-opacity=".9"/>'
        f'<stop offset="1" stop-color="{t["goldhi"]}" stop-opacity="0"/></radialGradient>'
    )
    svg.body.append(
        f'<g class="shoot"><line x1="80" y1="40" x2="190" y2="76" stroke="url(#trail)" stroke-width="2" stroke-linecap="round"/>'
        f'<circle cx="190" cy="76" r="2.6" fill="{t["goldhi"]}"/></g>'
    )
    cx, cy, k = 600, 120, 5.2
    pts = []
    for i in range(16):
        a = i / 16 * math.tau
        x = 16 * math.sin(a) ** 3
        y = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((cx + x * k, cy + y * k))
    path = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"
    svg.body.append(f'<circle class="hc" cx="{cx}" cy="{cy + 8}" r="46" fill="url(#hcore)"/>')
    svg.body.append(f'<path d="{path}" fill="none" stroke="{t["gold"]}" stroke-opacity=".25" stroke-width="1"/>')
    svg.body.append(f'<path class="heart" d="{path}" pathLength="1" fill="none" stroke="{t["goldhi"]}" stroke-width="1.6" stroke-linejoin="round"/>')
    rnd = random.Random(4)
    for i, (x, y) in enumerate(pts):
        big = i in (0, 4, 8, 12)
        svg.body.append(
            f'<circle class="st" cx="{x:.1f}" cy="{y:.1f}" r="{3.2 if big else 2.1}" fill="{t["goldhi"]}" '
            f'style="--d:{rnd.uniform(2.5, 5):.1f}s;animation-delay:-{rnd.uniform(0, 5):.1f}s"/>'
        )
    sheen = gold_sheen(svg, "csheen", 360, 840)
    svg.text(600, 268, "Since you came this far,", "LcSerif", 40, sheen, "middle")
    svg.text(600, 312, "this one is for you.", "LcSerif", 40, sheen, "middle")
    svg.text(600, 360, "THANK YOU FOR READING  ✦  SAIF RAHMAN", "LcDisplay", 11, t["soft"], "middle", ls=0.22)
    return svg.render()


def divider(theme: str) -> str:
    svg = Svg(1200, 40, theme, "")
    t = svg.t
    svg.css.append("@keyframes tw2{0%,100%{opacity:.4;transform:scale(.8)}50%{opacity:1;transform:scale(1.15)}}"
                   ".dv{animation:tw2 3s ease-in-out infinite;transform-box:fill-box;transform-origin:center}")
    svg.defs.append(
        f'<linearGradient id="dl" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t["gold"]}" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="{t["gold"]}"/><stop offset="1" stop-color="{t["gold"]}" stop-opacity="0"/></linearGradient>'
    )
    svg.body.append(f'<line x1="120" y1="20" x2="1080" y2="20" stroke="url(#dl)"/>')
    svg.body.append(f'<path class="dv" d="M600 6 L603 17 L614 20 L603 23 L600 34 L597 23 L586 20 L597 17 Z" fill="{t["goldhi"]}"/>')
    return svg.render()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sections = {
        "about": ("01", "About", "Business problems into", "finished products"),
        "services": ("02", "Services", "What I build,", "end to end"),
        "work": ("03", "Selected work", "Things I'm", "proud of"),
        "process": ("04", "Process", "From problem", "to product"),
        "stack": ("05", "Stack", "Not bound to any stack,", "fluent in the right one"),
        "experience": ("06", "Experience", f"{YEARS_WORD} years,", "four kinds of teams"),
        "stats": ("07", "Signals", "The archive,", "by the numbers"),
        "hire": ("08", "Hire", "Hire an engineer", "who finishes"),
        "notice": ("00", "Notice", "A note on", "private work"),
    }
    for theme in THEMES:
        files = {
            "hero": hero(theme),
            "stats": stats(theme),
            "timeline": timeline(theme),
            "footer": footer(theme),
            "divider": divider(theme),
            "signals": signals(theme),
            "closing": closing(theme),
        }
        for key, (num, label, plain, serif) in sections.items():
            files[f"h-{key}"] = header(theme, num, label, plain, serif)
        for name, content in files.items():
            (OUT / f"{name}-{theme}.svg").write_text(content, encoding="utf-8")
    total = sum(p.stat().st_size for p in OUT.glob("*.svg"))
    print(f"wrote {len(list(OUT.glob('*.svg')))} svgs, {total / 1024:.0f} KB total")


if __name__ == "__main__":
    main()
