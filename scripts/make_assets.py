#!/usr/bin/env python3
"""Generate the seasonal SVG artwork used by the profile README.

Run from the repository root:

    python3 scripts/make_assets.py

For every season it writes ``assets/<season>/``:

    banner.svg                          animated header: scene, particles, typing line
    divider.svg                         thin animated section divider
    crypto.svg  stocks.svg  cryptography.svg  ai.svg   animated interest icons

All randomness is seeded, so the output is identical on every run unless this
file changes.  The SVGs use only inline CSS and SMIL animation: no scripts, no
external fonts or images, because GitHub displays README images through
<img>, where neither would load.  Animations stop for visitors who ask their
system for reduced motion.  Standard library only.
"""

from __future__ import annotations

import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAME = "K4rim"
PHRASES = ("cryptocurrencies", "stocks", "cryptography", "AI")
SANS = "'Segoe UI',Ubuntu,'Helvetica Neue',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
W, H = 1200, 340          # banner size

# ---------------------------------------------------------------------------
# Season palettes
# ---------------------------------------------------------------------------

SEASONS = {
    "winter": dict(
        title="Winter", sky=(("0", "#070B1F"), ("0.55", "#142553"), ("1", "#2D4C86")),
        text="#F4F8FF", name=("#8FE3FF", "#D3C4FF"), typing="#CFE6FF", cursor="#8FD3FF",
        shadow=("#000814", 0.55), pill=("rgba(255,255,255,0.12)", "rgba(190,220,255,0.45)", "#E3F1FF"),
        accent="#8FD3FF", accent2="#C7B8FF", tile=("#13224A", "#2D4C86"), ink="#EAF4FF", line="#8FD3FF"),
    "spring": dict(
        title="Spring", sky=(("0", "#FFD1E3"), ("0.6", "#FFF1E7"), ("1", "#DCF5E2")),
        text="#4A1F35", name=("#FF4F8B", "#FF9B5E"), typing="#8A2E5C", cursor="#FF5C93",
        shadow=("#FFFFFF", 0.75), pill=("rgba(255,255,255,0.68)", "rgba(176,58,106,0.35)", "#8A2E5C"),
        accent="#FF7AA8", accent2="#4FB477", tile=("#FFE1EC", "#E1F6E7"), ink="#5A2140", line="#FF7AA8"),
    "summer": dict(
        title="Summer", sky=(("0", "#0D5DC2"), ("0.55", "#2F95EA"), ("0.72", "#7CC6FA"), ("0.78", "#FFE2A8")),
        text="#FFFFFF", name=("#FFE36E", "#FF9F43"), typing="#FFF6D5", cursor="#FFD54F",
        shadow=("#062A5E", 0.5), pill=("rgba(255,255,255,0.18)", "rgba(255,255,255,0.5)", "#FFFFFF"),
        accent="#FFC93C", accent2="#29B6F6", tile=("#1E7FD8", "#7FD0FF"), ink="#FFFFFF", line="#FFB300"),
    "autumn": dict(
        title="Autumn", sky=(("0", "#24102B"), ("0.4", "#5E2337"), ("0.75", "#B4482F"), ("1", "#E8913F")),
        text="#FFF3E3", name=("#FFC46B", "#FF6B4A"), typing="#FFD9A8", cursor="#FFB347",
        shadow=("#1A0610", 0.55), pill=("rgba(255,255,255,0.13)", "rgba(255,214,170,0.45)", "#FFE6C7"),
        accent="#FFB347", accent2="#E2583E", tile=("#3A1530", "#B4482F"), ink="#FFF1DE", line="#F08A3E"),
}

LEAF_COLORS = ("#E2583E", "#F08A3E", "#F2C14E", "#C0392B", "#D9662B")
PETAL_COLORS = ("#FFB7CF", "#FFC9DA", "#FF9EC0", "#FFD6E4")


def f(value: float) -> str:
    """Compact number formatting for SVG coordinates."""
    text = f"{value:.1f}"
    if text.endswith(".0"):
        text = text[:-2]
    return "0" if text == "-0" else text


def smooth(points) -> str:
    """Catmull-Rom spline through ``points`` as an SVG path (no closing)."""
    d = [f"M{f(points[0][0])},{f(points[0][1])}"]
    for i in range(len(points) - 1):
        p0 = points[i - 1] if i else points[i]
        p1, p2 = points[i], points[i + 1]
        p3 = points[i + 2] if i + 2 < len(points) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f"C{f(c1[0])},{f(c1[1])} {f(c2[0])},{f(c2[1])} {f(p2[0])},{f(p2[1])}")
    return " ".join(d)


def ridge(rng, base, amplitude, x0=-20, x1=W + 20, step=40, lift_right=0.0):
    """Points of a gently rolling ridge; ``lift_right`` raises the right side."""
    phases = [rng.uniform(0, math.tau) for _ in range(3)]
    freqs = (1 / 260, 1 / 140, 1 / 70)
    weights = (1.0, 0.45, 0.2)
    points = []
    for x in range(x0, x1 + 1, step):
        y = base - lift_right * max(0.0, (x - 500) / 700)
        y -= amplitude * sum(w * math.sin(x * fr * math.tau + ph)
                             for w, fr, ph in zip(weights, freqs, phases))
        points.append((x, y))
    return points


def closed(points, bottom=H + 2) -> str:
    return smooth(points) + f" L{f(points[-1][0])},{bottom} L{f(points[0][0])},{bottom} Z"


# ---------------------------------------------------------------------------
# Small glyphs
# ---------------------------------------------------------------------------

def snowflake(r: float, color="#FFFFFF", width=1.3) -> str:
    arms = []
    for k in range(3):
        a = math.radians(90 + 60 * k)
        dx, dy = r * math.cos(a), r * math.sin(a)
        arms.append(f"M{f(-dx)},{f(-dy)} L{f(dx)},{f(dy)}")
        # small barbs near both tips
        for sign in (1, -1):
            tx, ty = sign * dx * 0.62, sign * dy * 0.62
            for side in (1, -1):
                b = a + side * math.radians(40) + (math.pi if sign < 0 else 0)
                arms.append(f"M{f(tx)},{f(ty)} L{f(tx + 0.32 * r * math.cos(b))},"
                            f"{f(ty + 0.32 * r * math.sin(b))}")
    return (f'<path d="{" ".join(arms)}" stroke="{color}" stroke-width="{width}" '
            f'stroke-linecap="round" fill="none"/>')


def blossom(r: float, petal="#FFC1D6", edge="#FF8FB5", center="#E85A8C") -> str:
    petals = "".join(
        f'<ellipse cx="0" cy="{f(-r * 0.62)}" rx="{f(r * 0.42)}" ry="{f(r * 0.62)}" '
        f'transform="rotate({72 * k})"/>' for k in range(5))
    return (f'<g fill="{petal}" stroke="{edge}" stroke-width="0.8">{petals}</g>'
            f'<circle r="{f(r * 0.24)}" fill="{center}"/>')


def leaf(scale: float, color: str) -> str:
    return (f'<g transform="scale({scale:.2f})"><path d="M0,-10 C7,-6 7,6 0,10 C-7,6 -7,-6 0,-10 Z" '
            f'fill="{color}"/><path d="M0,-9 L0,12" stroke="rgba(60,15,10,0.55)" '
            f'stroke-width="1.1" stroke-linecap="round"/></g>')


def sun_glyph(r: float, color="#FFC93C") -> str:
    rays = " ".join(
        f"M{f((r + 2) * math.cos(a))},{f((r + 2) * math.sin(a))} "
        f"L{f((r + 6) * math.cos(a))},{f((r + 6) * math.sin(a))}"
        for a in (math.radians(45 * k) for k in range(8)))
    return (f'<circle r="{f(r)}" fill="{color}"/><path d="{rays}" stroke="{color}" '
            f'stroke-width="2" stroke-linecap="round"/>')


def season_glyph(season: str, size: float, palette) -> str:
    if season == "winter":
        return snowflake(size, palette["accent"], 1.6)
    if season == "spring":
        return blossom(size * 1.1)
    if season == "summer":
        return sun_glyph(size * 0.55)
    return leaf(size / 10, "#F08A3E")


# ---------------------------------------------------------------------------
# Shared CSS (particles and decorations)
# ---------------------------------------------------------------------------

CSS = """
.fall{animation-name:fall;animation-timing-function:linear;animation-iteration-count:infinite}
.diag{animation-name:diag;animation-timing-function:linear;animation-iteration-count:infinite}
.rise{animation-name:rise;animation-timing-function:linear;animation-iteration-count:infinite}
.s1,.s2,.s3{animation-timing-function:ease-in-out;animation-iteration-count:infinite;animation-direction:alternate}
.s1{animation-name:s1}.s2{animation-name:s2}.s3{animation-name:s3}
.spin{animation-name:spin;animation-timing-function:linear;animation-iteration-count:infinite;transform-box:fill-box;transform-origin:center}
.tw{animation:tw ease-in-out infinite alternate}
.drift{animation:drift 16s ease-in-out infinite alternate}
.glow{animation:glow 7s ease-in-out infinite alternate}
.pulse{animation:pulse 5s ease-in-out infinite alternate;transform-box:fill-box;transform-origin:center}
.rays{animation:spin 70s linear infinite;transform-box:fill-box;transform-origin:center}
.wave{animation-name:wave;animation-timing-function:linear;animation-iteration-count:infinite}
.fly{animation:fly linear infinite}
.flap{animation:flap .55s ease-in-out infinite alternate;transform-box:fill-box;transform-origin:center}
.bob{animation:bob 3.2s ease-in-out infinite alternate}
@keyframes fall{from{transform:translateY(-40px)}to{transform:translateY(400px)}}
@keyframes diag{from{transform:translate(60px,-40px)}to{transform:translate(-190px,400px)}}
@keyframes rise{0%{transform:translateY(380px);opacity:0}15%{opacity:.85}85%{opacity:.85}100%{transform:translateY(-40px);opacity:0}}
@keyframes s1{from{transform:translateX(-6px)}to{transform:translateX(6px)}}
@keyframes s2{from{transform:translateX(-13px)}to{transform:translateX(13px)}}
@keyframes s3{from{transform:translateX(-22px)}to{transform:translateX(22px)}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes tw{from{opacity:.12}to{opacity:1}}
@keyframes drift{from{transform:translateX(-45px)}to{transform:translateX(45px)}}
@keyframes glow{from{opacity:.45}to{opacity:.95}}
@keyframes pulse{from{transform:scale(.94)}to{transform:scale(1.06)}}
@keyframes wave{from{transform:translateX(0)}to{transform:translateX(-200px)}}
@keyframes fly{from{transform:translateX(-140px)}to{transform:translateX(1340px)}}
@keyframes flap{from{transform:scaleY(1)}to{transform:scaleY(.35)}}
@keyframes bob{from{transform:translateY(-4px)}to{transform:translateY(4px)}}
.static{display:none}
@media (prefers-reduced-motion:reduce){*{animation:none!important}.typing{display:none}.static{display:inline}}
"""


def particle(rng, x, inner, motion="fall", dur=(8, 16), sway=True, spin=None) -> str:
    """A particle at horizontal position ``x`` that loops forever.

    Negative animation delays spread the particles over their whole path at
    load time, so the scene starts "full" instead of empty.
    """
    d = rng.uniform(*dur)
    body = inner
    if spin:
        body = (f'<g class="spin" style="animation-duration:{rng.uniform(*spin):.1f}s;'
                f'animation-direction:{rng.choice(("normal", "reverse"))}">{body}</g>')
    if sway:
        body = (f'<g class="s{rng.randint(1, 3)}" style="animation-duration:{rng.uniform(2.2, 4.8):.1f}s;'
                f'animation-delay:-{rng.uniform(0, 4):.1f}s">{body}</g>')
    return (f'<g transform="translate({f(x)} 0)"><g class="{motion}" style="animation-duration:{d:.1f}s;'
            f'animation-delay:-{rng.uniform(0, d):.1f}s">{body}</g></g>')


# ---------------------------------------------------------------------------
# Season scenes: (background layer, particle layer, foreground layer)
# ---------------------------------------------------------------------------

def scene_winter(rng, p):
    defs = ('<radialGradient id="moonGlow"><stop offset="0" stop-color="#DDE8FF" stop-opacity=".55"/>'
            '<stop offset="1" stop-color="#DDE8FF" stop-opacity="0"/></radialGradient>'
            '<linearGradient id="aur1" x1="0" x2="1"><stop offset="0" stop-color="#3CFFC6" stop-opacity="0"/>'
            '<stop offset=".35" stop-color="#3CFFC6" stop-opacity=".42"/><stop offset=".7" stop-color="#8F7BFF" '
            'stop-opacity=".34"/><stop offset="1" stop-color="#8F7BFF" stop-opacity="0"/></linearGradient>'
            '<linearGradient id="aur2" x1="0" x2="1"><stop offset="0" stop-color="#7CF3FF" stop-opacity="0"/>'
            '<stop offset=".5" stop-color="#7CF3FF" stop-opacity=".25"/><stop offset="1" stop-color="#C77DFF" '
            'stop-opacity="0"/></linearGradient>'
            '<linearGradient id="snow" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#EEF4FF"/>'
            '<stop offset="1" stop-color="#B9CBF0"/></linearGradient>'
            '<mask id="crescent"><circle cx="1050" cy="86" r="34" fill="#fff"/>'
            '<circle cx="1066" cy="76" r="30" fill="#000"/></mask>')
    back = []
    for _ in range(80):
        back.append(f'<circle class="tw" cx="{f(rng.uniform(0, W))}" cy="{f(rng.uniform(4, 210))}" '
                    f'r="{f(rng.uniform(0.5, 1.7))}" fill="#FFFFFF" style="animation-duration:'
                    f'{rng.uniform(1.4, 4):.1f}s;animation-delay:-{rng.uniform(0, 4):.1f}s"/>')
    for gid, base, thick, opacity_cls in (("aur1", 62, 58, "glow"), ("aur2", 104, 40, "glow")):
        top = [(x, base + 16 * math.sin(x / 120 + base) + 10 * math.sin(x / 47)) for x in range(260, 1261, 50)]
        bottom = [(x, y + thick + 12 * math.sin(x / 90 + 1.3)) for x, y in reversed(top)]
        d = smooth(top) + " L" + smooth(bottom)[1:] + " Z"
        back.append(f'<g class="drift"><path class="{opacity_cls}" d="{d}" fill="url(#{gid})"/></g>')
    back.append('<circle cx="1050" cy="86" r="95" fill="url(#moonGlow)"/>'
                '<circle cx="1050" cy="86" r="34" fill="#F3F6FF" mask="url(#crescent)"/>')
    far = [(x, 262 - 70 * max(0.0, (x - 520) / 680) - rng.uniform(0, 26) * (x > 560))
           for x in range(-20, W + 61, 60)]
    peaks = []
    for i, (x, y) in enumerate(far):
        peaks.append((x, y - (34 if i % 2 else 0) * (x > 600)))
    back.append('<path d="M' + " L".join(f"{f(x)},{f(y)}" for x, y in peaks)
                + f' L{W + 40},{H + 2} L-20,{H + 2} Z" fill="#1B2C57"/>')
    near_pts, caps = [], []
    for i, x in enumerate(range(-30, W + 91, 90)):
        y = 300 - (58 if i % 2 else 8) * min(1.0, max(0.25, (x - 300) / 600)) - rng.uniform(0, 10)
        near_pts.append((x, y))
    back.append('<path d="M' + " L".join(f"{f(x)},{f(y)}" for x, y in near_pts)
                + f' L{W + 90},{H + 2} L-30,{H + 2} Z" fill="#10203F"/>')
    for (x0, y0), (x1, y1), (x2, y2) in zip(near_pts, near_pts[1:], near_pts[2:]):
        if y1 < y0 and y1 < y2 and y1 < 268:
            caps.append(f'<path d="M{f(x1)},{f(y1)} L{f(x1 + (x2 - x1) * 0.28)},{f(y1 + (y2 - y1) * 0.28)} '
                        f'L{f(x1 + 6)},{f(y1 + 14)} L{f(x1 - 8)},{f(y1 + 11)} '
                        f'L{f(x1 + (x0 - x1) * 0.28)},{f(y1 + (y0 - y1) * 0.28)} Z" fill="#E6EEFF" opacity=".9"/>')
    back.extend(caps)
    trees = []
    for x in (820, 860, 905, 1110, 1150):
        base = 322 + rng.uniform(-4, 4)
        trees.append(''.join(
            f'<path d="M{f(x)},{f(base - 46 + 13 * k)} L{f(x + 15 - 2 * k)},{f(base - 24 + 13 * k)} '
            f'L{f(x - 15 + 2 * k)},{f(base - 24 + 13 * k)} Z" fill="#0A1530"/>' for k in range(3)))
    ground = ridge(rng, 322, 5)
    front = [f'<path d="{closed(ground)}" fill="url(#snow)"/>'] + trees
    parts = []
    for _ in range(64):
        r = rng.uniform(1.1, 4.6)
        if r > 3.2:
            inner = f'<g opacity="{rng.uniform(0.7, 1):.2f}">{snowflake(r + 1.5)}</g>'
            spin = (10, 22)
        else:
            inner = f'<circle r="{f(r)}" fill="#FFFFFF" opacity="{rng.uniform(0.55, 1):.2f}"/>'
            spin = None
        parts.append(particle(rng, rng.uniform(0, W), inner, "fall", (9, 19), True, spin))
    return defs, "".join(back), "".join(parts), "".join(front)


def scene_spring(rng, p):
    defs = ('<radialGradient id="sunGlow"><stop offset="0" stop-color="#FFE59A" stop-opacity=".9"/>'
            '<stop offset="1" stop-color="#FFE59A" stop-opacity="0"/></radialGradient>')
    back = ['<g class="pulse"><circle cx="985" cy="92" r="125" fill="url(#sunGlow)"/></g>',
            '<circle cx="985" cy="92" r="44" fill="#FFDD7F"/>']
    for cx, cy, s in ((700, 72, 1.0), (1110, 165, 0.75), (430, 40, 0.6)):
        blobs = "".join(f'<circle cx="{f(cx + dx * s)}" cy="{f(cy + dy * s)}" r="{f(r * s)}"/>'
                        for dx, dy, r in ((0, 0, 26), (28, -10, 30), (58, 2, 24), (24, 12, 22)))
        back.append(f'<g class="drift" style="animation-duration:{rng.uniform(18, 26):.0f}s">'
                    f'<g fill="#FFFFFF" opacity=".85">{blobs}</g></g>')
    back.append(f'<path d="{closed(ridge(rng, 286, 14, lift_right=36))}" fill="#B6E6C0"/>')
    near = ridge(rng, 318, 9, lift_right=14)
    front = [f'<path d="{closed(near)}" fill="#7CCB92"/>']
    for _ in range(26):                        # little flowers in the meadow
        x = rng.uniform(560, W - 10)
        y = 322 + rng.uniform(0, 16)
        color = rng.choice(("#FF8FB5", "#FFFFFF", "#FFD45E", "#C48BFF"))
        front.append(f'<g transform="translate({f(x)} {f(y)})"><g class="s1" style="animation-duration:'
                     f'{rng.uniform(2, 4):.1f}s"><path d="M0,0 L0,-9" stroke="#4E9E66" stroke-width="1.4"/>'
                     f'<circle cy="-10" r="{f(rng.uniform(2.2, 3.4))}" fill="{color}"/></g></g>')
    # cherry branch from the top-right corner
    branch = ("M1215,-6 C1150,40 1080,62 1010,76 C960,86 920,104 880,126", "M1065,66 C1060,40 1040,22 1018,10",
              "M960,88 C952,112 936,130 918,146", "M1140,34 C1120,66 1122,96 1140,120")
    front.append('<g fill="none" stroke="#6E4031" stroke-linecap="round">'
                 f'<path d="{branch[0]}" stroke-width="7"/><path d="{branch[1]}" stroke-width="4"/>'
                 f'<path d="{branch[2]}" stroke-width="3.5"/><path d="{branch[3]}" stroke-width="4"/></g>')
    for x, y, r in ((1008, 76, 13), (968, 86, 11), (925, 108, 12), (884, 126, 10), (1050, 30, 10),
                    (1022, 12, 11), (936, 132, 10), (1132, 74, 12), (1142, 112, 11), (1100, 52, 9),
                    (1182, 20, 12), (990, 60, 8)):
        front.append(f'<g transform="translate({x} {y})"><g class="pulse" style="animation-duration:'
                     f'{rng.uniform(3, 5.5):.1f}s;animation-delay:-{rng.uniform(0, 5):.1f}s">'
                     f'{blossom(r)}</g></g>')
    parts = []
    for _ in range(40):
        color = rng.choice(PETAL_COLORS)
        inner = (f'<ellipse rx="{f(rng.uniform(4.2, 6.2))}" ry="{f(rng.uniform(2.6, 3.6))}" fill="{color}" '
                 f'opacity="{rng.uniform(0.75, 1):.2f}"/>')
        parts.append(particle(rng, rng.uniform(60, W + 180), inner, "diag", (9, 16), True, (3, 7)))
    return defs, "".join(back), "".join(parts), "".join(front)


def scene_summer(rng, p):
    defs = ('<radialGradient id="sunGlow"><stop offset="0" stop-color="#FFF3B0" stop-opacity=".95"/>'
            '<stop offset="1" stop-color="#FFE082" stop-opacity="0"/></radialGradient>'
            '<radialGradient id="mote"><stop offset="0" stop-color="#FFFBE0"/>'
            '<stop offset="1" stop-color="#FFFBE0" stop-opacity="0"/></radialGradient>'
            '<linearGradient id="sea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1A8FD6"/>'
            '<stop offset="1" stop-color="#015A9C"/></linearGradient>')
    rays = " ".join(
        f"M{f(1000 + 62 * math.cos(a - 0.05))},{f(118 + 62 * math.sin(a - 0.05))} "
        f"L{f(1000 + 104 * math.cos(a))},{f(118 + 104 * math.sin(a))} "
        f"L{f(1000 + 62 * math.cos(a + 0.05))},{f(118 + 62 * math.sin(a + 0.05))} Z"
        for a in (math.radians(15 * k) for k in range(24)))
    back = ['<g class="pulse"><circle cx="1000" cy="118" r="150" fill="url(#sunGlow)"/></g>',
            f'<g class="rays"><path d="{rays}" fill="#FFE27A" opacity=".55"/></g>',
            '<circle cx="1000" cy="118" r="54" fill="#FFD54F"/>']
    for cx, cy, s in ((700, 66, 1.0), (520, 40, 0.7)):     # clear of the top-left pill
        blobs = "".join(f'<circle cx="{f(cx + dx * s)}" cy="{f(cy + dy * s)}" r="{f(r * s)}"/>'
                        for dx, dy, r in ((0, 0, 24), (26, -9, 28), (54, 2, 22), (22, 11, 20)))
        back.append(f'<g class="drift" style="animation-duration:{rng.uniform(20, 28):.0f}s">'
                    f'<g fill="#FFFFFF" opacity=".9">{blobs}</g></g>')
    for i in range(3):                          # gliding birds
        y = 70 + 26 * i
        back.append(f'<g transform="translate(0 {y})"><g class="fly" style="animation-duration:'
                    f'{rng.uniform(26, 38):.0f}s;animation-delay:-{rng.uniform(0, 30):.0f}s"><g class="flap">'
                    f'<path d="M0,0 q7,-7 13,0 q6,-7 13,0" stroke="#163A6B" stroke-width="2.2" '
                    f'fill="none" stroke-linecap="round"/></g></g></g>')
    front = [f'<rect x="0" y="262" width="{W}" height="{H - 262 + 2}" fill="url(#sea)"/>']
    for k, (y0, amp, color, dur) in enumerate(((262, 5, "rgba(130,212,255,0.55)", 7),
                                               (276, 7, "rgba(64,180,240,0.55)", 10),
                                               (296, 8, "rgba(10,120,200,0.6)", 14))):
        pts = [(x, y0 + amp * math.sin(x / 200 * math.tau + k)) for x in range(-200, W + 401, 25)]
        front.append(f'<g class="wave" style="animation-duration:{dur}s"><path d="{closed(pts)}" '
                     f'fill="{color}"/></g>')
    for i in range(9):                           # sun reflection on the water
        y = 272 + 7 * i
        wdt = 70 - 6 * i
        front.append(f'<rect class="tw" x="{f(1000 - wdt / 2 + rng.uniform(-8, 8))}" y="{y}" width="{f(wdt)}" '
                     f'height="2.4" rx="1.2" fill="#FFF3C4" style="animation-duration:'
                     f'{rng.uniform(0.8, 1.8):.1f}s;animation-delay:-{rng.uniform(0, 2):.1f}s"/>')
    for _ in range(16):                          # sparkles
        x, y, s = rng.uniform(40, W - 40), rng.uniform(280, 334), rng.uniform(2.5, 4.5)
        front.append(f'<path class="tw" d="M{f(x)},{f(y - s)} L{f(x + s / 3)},{f(y)} L{f(x)},{f(y + s)} '
                     f'L{f(x - s / 3)},{f(y)} Z M{f(x - s)},{f(y)} L{f(x)},{f(y - s / 3)} L{f(x + s)},{f(y)} '
                     f'L{f(x)},{f(y + s / 3)} Z" fill="#FFFFFF" style="animation-duration:'
                     f'{rng.uniform(1, 2.4):.1f}s;animation-delay:-{rng.uniform(0, 2.4):.1f}s"/>')
    parts = []
    for _ in range(24):                          # warm floating motes
        inner = f'<circle r="{f(rng.uniform(2, 4.5))}" fill="url(#mote)"/>'
        parts.append(particle(rng, rng.uniform(0, W), inner, "rise", (14, 24), True))
    return defs, "".join(back), "".join(parts), "".join(front)


def scene_autumn(rng, p):
    defs = ('<radialGradient id="sunGlow"><stop offset="0" stop-color="#FFD08A" stop-opacity=".9"/>'
            '<stop offset="1" stop-color="#FF9F4A" stop-opacity="0"/></radialGradient>'
            '<linearGradient id="mist" x1="0" x2="1"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0"/>'
            '<stop offset=".5" stop-color="#FFE6D0" stop-opacity=".16"/><stop offset="1" stop-color="#FFFFFF" '
            'stop-opacity="0"/></linearGradient>')
    back = ['<g class="pulse"><circle cx="1010" cy="232" r="170" fill="url(#sunGlow)"/></g>',
            '<circle cx="1010" cy="232" r="72" fill="#FFB75E"/>']
    far = ridge(rng, 282, 12, lift_right=40)
    back.append(f'<path d="{closed(far)}" fill="#4A1C2A"/>')
    back.append(f'<g class="drift"><rect x="120" y="236" width="1100" height="46" rx="23" fill="url(#mist)"/></g>')
    near = ridge(rng, 314, 8, lift_right=18)
    front = [f'<path d="{closed(near)}" fill="#2A0F1C"/>']
    for x, s in ((700, 0.8), (760, 1.05), (845, 0.9), (1120, 1.2), (1180, 0.85), (930, 0.7)):
        base = 318 - 18 * max(0.0, (x - 500) / 700)
        crowns = "".join(
            f'<circle cx="{f(x + dx * s)}" cy="{f(base - 40 * s + dy * s)}" r="{f(r * s)}" fill="{c}"/>'
            for dx, dy, r, c in ((0, 0, 22, "#5B1F1C"), (-14, 8, 15, "#7A2A1E"), (14, 6, 16, "#6B2420"),
                                 (4, -12, 14, "#8C3A22")))
        front.append(f'<rect x="{f(x - 3 * s)}" y="{f(base - 30 * s)}" width="{f(6 * s)}" height="{f(32 * s)}" '
                     f'fill="#1E0A12"/>{crowns}')
    parts = []
    for _ in range(36):
        inner = leaf(rng.uniform(0.75, 1.5), rng.choice(LEAF_COLORS))
        parts.append(particle(rng, rng.uniform(0, W), inner, "fall", (10, 18), True, (4, 9)))
    return defs, "".join(back), "".join(parts), "".join(front)


SCENES = {"winter": scene_winter, "spring": scene_spring, "summer": scene_summer, "autumn": scene_autumn}


# ---------------------------------------------------------------------------
# Typing line (SMIL, so it runs everywhere SVG images run)
# ---------------------------------------------------------------------------

def typing_line(p, x0=86.0, y=214.0, size=30.0, prefix="I love", period=4.0) -> str:
    cw = 0.6 * size                                   # monospace advance
    total = period * len(PHRASES)
    start_x = x0 + (len(prefix) + 1) * cw
    out = [f'<g class="typing" font-family="{MONO}" font-size="{f(size)}" fill="{p["typing"]}">',
           f'<text x="{f(x0)}" y="{f(y)}" textLength="{f(len(prefix) * cw)}" '
           f'lengthAdjust="spacingAndGlyphs">{prefix}</text>']
    cursor = [(0.0, 0)]
    for i, phrase in enumerate(PHRASES):
        n = len(phrase)
        t0 = i * period + 0.15
        type_time = min(1.35, 0.085 * n + 0.25)
        erase_at = i * period + 3.1
        events = [(t0 + k * type_time / n, k) for k in range(1, n + 1)]
        events += [(erase_at + (n - k) * 0.45 / n, k) for k in range(n - 1, -1, -1)]
        cursor += events
        key_times = "0;" + ";".join(f"{t / total:.4f}" for t, _ in events)
        widths = "0;" + ";".join(f(k * cw) for _, k in events)
        out.append(f'<clipPath id="ty{i}"><rect x="{f(start_x)}" y="{f(y - size)}" width="0" '
                   f'height="{f(size * 1.4)}"><animate attributeName="width" dur="{f(total)}s" '
                   f'repeatCount="indefinite" calcMode="discrete" keyTimes="{key_times}" '
                   f'values="{widths}"/></rect></clipPath>')
        out.append(f'<text x="{f(start_x)}" y="{f(y)}" textLength="{f(n * cw)}" '
                   f'lengthAdjust="spacingAndGlyphs" clip-path="url(#ty{i})">{phrase}</text>')
    cursor.sort()
    key_times = ";".join(f"{t / total:.4f}" for t, _ in cursor)
    xs = ";".join(f(start_x + k * cw) for _, k in cursor)
    out.append(f'<rect x="{f(start_x)}" y="{f(y - size * 0.82)}" width="3" height="{f(size * 1.02)}" '
               f'fill="{p["cursor"]}"><animate attributeName="x" dur="{f(total)}s" repeatCount="indefinite" '
               f'calcMode="discrete" keyTimes="{key_times}" values="{xs}"/><animate attributeName="opacity" '
               f'values="1;0" dur="1.06s" calcMode="discrete" repeatCount="indefinite"/></rect></g>')
    out.append(f'<text class="static" x="{f(x0)}" y="{f(y)}" font-family="{MONO}" font-size="24" '
               f'fill="{p["typing"]}">I love cryptocurrencies, stocks, cryptography &amp; AI</text>')
    return "".join(out)


# ---------------------------------------------------------------------------
# Banner, divider and icons
# ---------------------------------------------------------------------------

def banner(season: str) -> str:
    p = SEASONS[season]
    rng = random.Random(f"banner-{season}")
    extra_defs, back, particles, front = SCENES[season](rng, p)
    stops = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in p["sky"])
    shadow_color, shadow_opacity = p["shadow"]
    c1, c2 = p["name"]
    pill_fill, pill_stroke, pill_text = p["pill"]
    label = f'{p["title"].upper()} EDITION'
    pill_w = 66 + len(label) * 12.4     # the pill sits top-left, above the title,
    pill_x = 80                         # leaving the right side to the scenery
    title = f'Hi, I’m {NAME} — {p["title"]} edition'
    desc = ("Animated banner. I love cryptocurrencies, stocks, cryptography and AI. "
            f"Seasonal {p['title'].lower()} scene.")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'role="img" aria-labelledby="title desc">'
        f'<title id="title">{title}</title><desc id="desc">{desc}</desc>'
        f'<defs><clipPath id="card"><rect width="{W}" height="{H}" rx="26"/></clipPath>'
        f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">{stops}</linearGradient>'
        f'<linearGradient id="name" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="300" y2="0" '
        f'spreadMethod="repeat"><stop offset="0" stop-color="{c1}"/><stop offset=".5" stop-color="{c2}"/>'
        f'<stop offset="1" stop-color="{c1}"/><animateTransform attributeName="gradientTransform" '
        f'type="translate" values="0 0;300 0" dur="5s" repeatCount="indefinite"/></linearGradient>'
        f'<filter id="shadow" x="-10%" y="-30%" width="120%" height="160%"><feDropShadow dx="0" dy="3" '
        f'stdDeviation="5" flood-color="{shadow_color}" flood-opacity="{shadow_opacity}"/></filter>'
        f'{extra_defs}</defs><style>{CSS}</style>'
        f'<g clip-path="url(#card)"><rect width="{W}" height="{H}" fill="url(#sky)"/>'
        f'{back}{particles}{front}</g>'
        f'<g filter="url(#shadow)"><text x="80" y="150" font-family="{SANS}" font-size="76" '
        f'font-weight="800" fill="{p["text"]}">Hi, I’m <tspan fill="url(#name)">{NAME}</tspan></text>'
        f'{typing_line(p)}</g>'
        f'<g transform="translate({f(pill_x)} 26)"><rect width="{f(pill_w)}" height="44" rx="22" '
        f'fill="{pill_fill}" stroke="{pill_stroke}"/><g transform="translate(29 22)">'
        f'<g class="pulse">{season_glyph(season, 9, p)}</g></g><text x="54" y="28.5" font-family="{SANS}" '
        f'font-size="15" font-weight="700" letter-spacing="3" fill="{pill_text}">{label}</text></g>'
        f'</svg>\n')


def divider(season: str) -> str:
    p = SEASONS[season]
    width, height = 1200, 40
    glyphs = []
    for i, x in enumerate((240, 420, 600, 780, 960)):
        glyphs.append(f'<g transform="translate({x} 20)"><g class="bob" style="animation-delay:-{i * 0.6:.1f}s">'
                      f'{season_glyph(season, 7 if i != 2 else 9, p)}</g></g>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" '
            f'height="{height}" role="img" aria-label="{p["title"]} divider"><defs>'
            f'<linearGradient id="line" x1="0" x2="1"><stop offset="0" stop-color="{p["line"]}" stop-opacity="0"/>'
            f'<stop offset=".5" stop-color="{p["line"]}" stop-opacity=".85"/><stop offset="1" '
            f'stop-color="{p["line"]}" stop-opacity="0"/></linearGradient></defs><style>{CSS}</style>'
            f'<rect x="60" y="19" width="1080" height="2" rx="1" fill="url(#line)"/>{"".join(glyphs)}</svg>\n')


def icon_frame(season: str, label: str, body: str, extra_css: str = "") -> str:
    p = SEASONS[season]
    t1, t2 = p["tile"]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96" width="96" height="96" role="img" '
            f'aria-label="{label}"><defs><linearGradient id="tile" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="{t1}"/><stop offset="1" stop-color="{t2}"/></linearGradient></defs>'
            f'<style>{CSS}{extra_css}</style><rect x="2" y="2" width="92" height="92" rx="24" fill="url(#tile)" '
            f'stroke="{p["accent"]}" stroke-opacity=".55" stroke-width="2"/>{body}</svg>\n')


def icon_crypto(season: str) -> str:
    css = (".coin{animation:coin 4s ease-in-out infinite;transform-box:fill-box;transform-origin:center}"
           "@keyframes coin{0%,62%{transform:scaleX(1)}72%{transform:scaleX(.08)}82%{transform:scaleX(-1)}"
           "92%{transform:scaleX(.08)}100%{transform:scaleX(1)}}")
    hexagon = " ".join(f"{f(48 + 11 * math.cos(math.radians(60 * k + 30)))},"
                       f"{f(48 + 11 * math.sin(math.radians(60 * k + 30)))}" for k in range(6))
    nodes = "".join(f'<circle cx="{f(48 + 11 * math.cos(math.radians(60 * k + 30)))}" '
                    f'cy="{f(48 + 11 * math.sin(math.radians(60 * k + 30)))}" r="2.6" fill="#8A5A00"/>'
                    for k in range(0, 6, 2))
    body = (f'<g class="coin"><circle cx="48" cy="48" r="27" fill="#F5B932" stroke="#B57A10" stroke-width="3"/>'
            f'<circle cx="48" cy="48" r="20" fill="none" stroke="#FFE08A" stroke-width="2" stroke-dasharray="3 3"/>'
            f'<polygon points="{hexagon}" fill="none" stroke="#8A5A00" stroke-width="2.4" '
            f'stroke-linejoin="round"/>{nodes}<circle cx="48" cy="48" r="3" fill="#8A5A00"/></g>')
    return icon_frame(season, "Cryptocurrencies", body, css)


def icon_stocks(season: str) -> str:
    p = SEASONS[season]
    css = (".trend{stroke-dasharray:90;animation:trend 4s ease-in-out infinite}"
           "@keyframes trend{0%{stroke-dashoffset:90}45%,80%{stroke-dashoffset:0}100%{stroke-dashoffset:-90}}")
    candles = []
    for x, top, bottom, up in ((24, 50, 66, False), (38, 46, 60, True), (52, 38, 54, True), (66, 30, 46, True)):
        color = "#3FD07E" if up else "#FF5A5F"
        candles.append(f'<path d="M{x},{top - 6} L{x},{bottom + 6}" stroke="{color}" stroke-width="1.6"/>'
                       f'<rect x="{x - 4}" y="{top}" width="8" height="{bottom - top}" rx="1.5" fill="{color}"/>')
    body = (f'<path d="M18,76 L80,76" stroke="{p["ink"]}" stroke-opacity=".35" stroke-width="2"/>'
            f'{"".join(candles)}<path class="trend" d="M18,68 L34,58 L48,60 L62,44 L78,30" fill="none" '
            f'stroke="{p["accent"]}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="M70,29 L79,29 L79,38" fill="none" stroke="{p["accent"]}" stroke-width="3.2" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')
    return icon_frame(season, "Stocks", body, css)


def icon_cryptography(season: str) -> str:
    p = SEASONS[season]
    css = (".shackle{animation:shackle 3.6s ease-in-out infinite}"
           "@keyframes shackle{0%,55%,100%{transform:translateY(0)}70%,85%{transform:translateY(-6px)}}"
           ".bit{font:700 8px " + MONO + ";animation:tw 1.6s ease-in-out infinite alternate}")
    bits = "".join(f'<text class="bit" x="{x}" y="{y}" fill="{p["accent"]}" style="animation-delay:-{d}s">{b}</text>'
                   for x, y, b, d in ((14, 22, "1", 0), (74, 20, "0", 0.4), (12, 84, "0", 0.8), (78, 86, "1", 1.2)))
    body = (f'{bits}<g class="shackle"><path d="M36,46 L36,36 C36,28 41,23 48,23 C55,23 60,28 60,36 L60,46" '
            f'fill="none" stroke="{p["ink"]}" stroke-width="6" stroke-linecap="round"/></g>'
            f'<rect x="28" y="44" width="40" height="32" rx="7" fill="{p["accent"]}"/>'
            f'<circle cx="48" cy="57" r="4.5" fill="{SEASONS[season]["tile"][0]}"/>'
            f'<path d="M48,60 L48,68" stroke="{SEASONS[season]["tile"][0]}" stroke-width="3.5" '
            f'stroke-linecap="round"/>')
    return icon_frame(season, "Cryptography", body, css)


def icon_ai(season: str) -> str:
    p = SEASONS[season]
    layers = [[(22, 34), (22, 62)], [(48, 22), (48, 48), (48, 74)], [(74, 36), (74, 60)]]
    lines, paths = [], []
    for a, b in zip(layers, layers[1:]):
        for x1, y1 in a:
            for x2, y2 in b:
                lines.append(f"M{x1},{y1} L{x2},{y2}")
                paths.append((x1, y1, x2, y2))
    pulses = []
    for i, (x1, y1, x2, y2) in enumerate(paths[::2]):
        pulses.append(f'<circle r="2.6" fill="{p["accent"]}"><animateMotion dur="1.8s" begin="-{i * 0.35:.2f}s" '
                      f'repeatCount="indefinite" path="M{x1},{y1} L{x2},{y2}"/></circle>')
    nodes = "".join(f'<circle class="pulse" cx="{x}" cy="{y}" r="6.5" fill="{p["tile"][0]}" stroke="{p["ink"]}" '
                    f'stroke-width="2.6" style="animation-duration:{1.6 + 0.3 * i:.1f}s"/>'
                    for i, (x, y) in enumerate(pt for layer in layers for pt in layer))
    body = (f'<path d="{" ".join(lines)}" stroke="{p["ink"]}" stroke-opacity=".45" stroke-width="1.6"/>'
            f'{"".join(pulses)}{nodes}')
    return icon_frame(season, "Artificial intelligence", body)


ICONS = {"crypto": icon_crypto, "stocks": icon_stocks, "cryptography": icon_cryptography, "ai": icon_ai}


def main() -> None:
    written = 0
    for season in SEASONS:
        folder = ROOT / "assets" / season
        folder.mkdir(parents=True, exist_ok=True)
        outputs = {"banner.svg": banner(season), "divider.svg": divider(season)}
        outputs.update({f"{name}.svg": make(season) for name, make in ICONS.items()})
        for filename, content in outputs.items():
            path = folder / filename
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                path.write_text(content, encoding="utf-8")
                written += 1
    print(f"assets: {written} file(s) written")


if __name__ == "__main__":
    main()
