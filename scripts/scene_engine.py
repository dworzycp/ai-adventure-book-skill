#!/usr/bin/env python3
"""scene_engine — draw pop-up book spreads with rendered, Pixar-style shading.

You describe a spread as shapes with colours. The engine lights them: every piece gets a
height map from its own silhouette, a warm key light from one direction, a cool bounce from the
other, a tight specular, a card edge and a soft cast shadow onto whatever is behind it. Eyes,
the back panel's depth-of-field and the page's contact shadows are built in. What comes out is
one inline SVG that drops straight into a stage's `scene:` and obeys the template's contracts
(viewBox 1600x900, data-depth parallax, pop/rise unfolding).

    from scene_engine import Scene, Palette, spline, ellipse, capsule, rrect

    P  = Palette.load("storybook")                  # or Palette.load({"extends": "knight", ...})
    sc = Scene("gate", P, light=(-0.6, -0.8))
    sc.back_panel().hills()
    sc.base_page(shadow=(420, 770, 250))
    hero = sc.hero()
    hero.piece(ellipse(400, 480, 160, 200), P.land2)          # lit, edged, casting
    hero.eye(470, 380, 34, iris="#2b7bd6", look=(4, 2))
    sc.flats().bush(40, 780).bush(600, 800, .7)
    sc.write("scenes/01-gate.svg")

One hero, big, on a clean page — the engine makes it look premium; the composition is still
yours. See references/scenes.md.
"""
from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence

HERE = Path(__file__).resolve().parent
THEMES = HERE.parent / "assets" / "themes.json"

W, H = 1600, 900
# where the left leaf is on a typical window; the hero must sit inside this box
HERO_BOX = (120, 130, 760, 800)

Pt = tuple[float, float]

# --------------------------------------------------------------------------- colour

WARM = (255, 246, 224)   # highlights go towards this, never towards pure white
COOL = (34, 33, 63)      # shadows go towards this, never towards black


def _rgb(c: str) -> tuple[int, int, int]:
    c = c.lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)


def _hex(rgb: Sequence[float]) -> str:
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(v))) for v in rgb)


def mix(a: str, b: str | Sequence[float], t: float) -> str:
    ra, rb = _rgb(a), (_rgb(b) if isinstance(b, str) else b)
    return _hex([ra[i] + (rb[i] - ra[i]) * t for i in range(3)])


def tint(c: str, t: float) -> str:
    """Lighter, warmer."""
    return mix(c, WARM, t)


def shade(c: str, t: float) -> str:
    """Darker, cooler."""
    return mix(c, COOL, t)


def _f(v: float) -> str:
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


# --------------------------------------------------------------------------- palette

@dataclass
class Palette:
    """The theme's colours as attributes: P.land2, P.accent, P.cut ..."""
    colors: dict[str, str]

    def __getattr__(self, k: str) -> str:
        try:
            return self.colors[k]
        except KeyError:
            raise AttributeError(k)

    @classmethod
    def load(cls, theme: str | dict, themes_path: Path = THEMES) -> "Palette":
        presets = json.loads(Path(themes_path).read_text())
        if isinstance(theme, str):
            colors = dict(presets[theme]["colors"])
        else:
            colors = dict(presets[theme.get("extends", "knight")]["colors"])
            colors.update(theme.get("colors", {}))
        return cls(colors)


# --------------------------------------------------------------------------- shapes

@dataclass
class Shape:
    d: str
    bbox: tuple[float, float, float, float]  # x0 y0 x1 y1

    @property
    def w(self) -> float:
        return self.bbox[2] - self.bbox[0]

    @property
    def h(self) -> float:
        return self.bbox[3] - self.bbox[1]

    @property
    def cx(self) -> float:
        return (self.bbox[0] + self.bbox[2]) / 2

    @property
    def cy(self) -> float:
        return (self.bbox[1] + self.bbox[3]) / 2

    def moved(self, dx: float, dy: float) -> "Shape":
        return Shape(_translate_d(self.d, dx, dy), (self.bbox[0] + dx, self.bbox[1] + dy, self.bbox[2] + dx, self.bbox[3] + dy))


def _bbox(pts: Iterable[Pt]) -> tuple[float, float, float, float]:
    xs, ys = zip(*pts)
    return min(xs), min(ys), max(xs), max(ys)


_NUM = re.compile(r"-?\d*\.?\d+(?:e-?\d+)?")


def _translate_d(d: str, dx: float, dy: float) -> str:
    """Translate an absolute-command path (the only kind the engine emits)."""
    out, i, cmd = [], 0, ""
    tokens = re.findall(r"[MLCQAZHVmlcqazhv]|-?\d*\.?\d+", d)
    nums: list[float] = []

    def flush() -> None:
        nonlocal nums
        if not nums:
            return
        if cmd == "A":
            res = []
            for j in range(0, len(nums), 7):
                a = nums[j:j + 7]
                res += [_f(a[0]), _f(a[1]), _f(a[2]), str(int(a[3])), str(int(a[4])), _f(a[5] + dx), _f(a[6] + dy)]
            out.append(" ".join(res))
        else:
            res = []
            for j, n in enumerate(nums):
                res.append(_f(n + (dx if j % 2 == 0 else dy)))
            out.append(" ".join(res))
        nums = []

    for t in tokens:
        if re.match(r"[A-Za-z]", t):
            flush()
            cmd = t.upper()
            out.append(t)
        else:
            nums.append(float(t))
    flush()
    return " ".join(out)


def spline(pts: Sequence[Pt], closed: bool = True, tension: float = 1.0) -> Shape:
    """A smooth Catmull-Rom curve through the points. This is how organic shapes are drawn:
    place eight to fourteen points around the silhouette and let the curve do the rest."""
    n = len(pts)
    k = tension / 6.0
    d = f"M{_f(pts[0][0])} {_f(pts[0][1])}"
    segs = n if closed else n - 1
    for i in range(segs):
        if closed:
            p0, p1, p2, p3 = pts[(i - 1) % n], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        else:
            p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, n - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) * k, p1[1] + (p2[1] - p0[1]) * k)
        c2 = (p2[0] - (p3[0] - p1[0]) * k, p2[1] - (p3[1] - p1[1]) * k)
        d += f" C{_f(c1[0])} {_f(c1[1])} {_f(c2[0])} {_f(c2[1])} {_f(p2[0])} {_f(p2[1])}"
    if closed:
        d += " Z"
    return Shape(d, _bbox(pts))


def ellipse(cx: float, cy: float, rx: float, ry: float | None = None) -> Shape:
    ry = rx if ry is None else ry
    d = (f"M{_f(cx - rx)} {_f(cy)} A{_f(rx)} {_f(ry)} 0 1 0 {_f(cx + rx)} {_f(cy)} "
         f"A{_f(rx)} {_f(ry)} 0 1 0 {_f(cx - rx)} {_f(cy)} Z")
    return Shape(d, (cx - rx, cy - ry, cx + rx, cy + ry))


def circle(cx: float, cy: float, r: float) -> Shape:
    return ellipse(cx, cy, r, r)


def capsule(x1: float, y1: float, x2: float, y2: float, r: float, r2: float | None = None) -> Shape:
    """A thick rounded stroke from one point to another: limbs, necks, tails, horns.
    Give r2 for a limb that tapers."""
    r2 = r if r2 is None else r2
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    d = (f"M{_f(x1 + nx * r)} {_f(y1 + ny * r)} L{_f(x2 + nx * r2)} {_f(y2 + ny * r2)} "
         f"A{_f(r2)} {_f(r2)} 0 0 1 {_f(x2 - nx * r2)} {_f(y2 - ny * r2)} "
         f"L{_f(x1 - nx * r)} {_f(y1 - ny * r)} A{_f(r)} {_f(r)} 0 0 1 {_f(x1 + nx * r)} {_f(y1 + ny * r)} Z")
    m = max(r, r2)
    return Shape(d, (min(x1, x2) - m, min(y1, y2) - m, max(x1, x2) + m, max(y1, y2) + m))


def _cr_points(pts: Sequence[Pt], samples: int = 8, tension: float = 1.0) -> list[Pt]:
    """Sample a Catmull-Rom curve through pts (open) into a dense polyline."""
    n = len(pts)
    k = tension / 6.0
    out: list[Pt] = [pts[0]]
    for i in range(n - 1):
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, n - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) * k, p1[1] + (p2[1] - p0[1]) * k)
        c2 = (p2[0] - (p3[0] - p1[0]) * k, p2[1] - (p3[1] - p1[1]) * k)
        for s in range(1, samples + 1):
            u = s / samples
            a, b, c, d = (1 - u) ** 3, 3 * u * (1 - u) ** 2, 3 * u * u * (1 - u), u ** 3
            out.append((a * p1[0] + b * c1[0] + c * c2[0] + d * p2[0], a * p1[1] + b * c1[1] + c * c2[1] + d * p2[1]))
    return out


def tube(pts: Sequence[Pt], r0: float, r1: float, tension: float = 1.0, cap: bool = True) -> Shape:
    """A single smooth tube along the curve through `pts`, radius r0 at the start tapering to r1
    at the end. One piece, so no seams: use it for tails, necks, trunks, branches, arms."""
    line = _cr_points(pts, tension=tension)
    n = len(line)
    left, right = [], []
    for i, (x, y) in enumerate(line):
        ax, ay = line[max(i - 1, 0)]
        bx, by = line[min(i + 1, n - 1)]
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        r = r0 + (r1 - r0) * (i / (n - 1))
        left.append((x + nx * r, y + ny * r))
        right.append((x - nx * r, y - ny * r))
    ring = left + right[::-1]
    if cap:
        # round the two ends by pulling the corner points in a little
        ex, ey = line[-1]
        ring.insert(len(left), (ex + (bx - ax) / L * r1 * .9, ey + (by - ay) / L * r1 * .9))
        sx, sy = line[0]
        ax, ay = line[0]; bx, by = line[1]
        dx, dy = bx - ax, by - ay
        L2 = math.hypot(dx, dy) or 1
        ring.append((sx - dx / L2 * r0 * .9, sy - dy / L2 * r0 * .9))
    return spline(ring, closed=True, tension=.8)


def fan(outline: Sequence[Pt], apex: Pt) -> list[list[Pt]]:
    """Triangles from one apex to each edge of an outline: a folded fan. Put the apex off-centre,
    towards the light, and one side of the form lights up while the other falls dark."""
    n = len(outline)
    return [[apex, outline[i], outline[(i + 1) % n]] for i in range(n)]


def strip(left: Sequence[Pt], right: Sequence[Pt]) -> list[list[Pt]]:
    """Triangles zig-zagging between two polylines of equal length: a folded strip. Necks,
    tails, limbs, wing fingers."""
    out = []
    for i in range(len(left) - 1):
        out.append([left[i], right[i], right[i + 1]])
        out.append([left[i], right[i + 1], left[i + 1]])
    return out


def ridge(pts: Sequence[Pt], r0: float, r1: float) -> tuple[list[Pt], list[Pt]]:
    """The two edges of a tapered strip along a polyline, for `strip()`."""
    n = len(pts)
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        ax, ay = pts[max(i - 1, 0)]
        bx, by = pts[min(i + 1, n - 1)]
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        r = r0 + (r1 - r0) * i / max(n - 1, 1)
        left.append((x + nx * r, y + ny * r))
        right.append((x - nx * r, y - ny * r))
    return left, right


def rrect(x: float, y: float, w: float, h: float, r: float) -> Shape:
    r = min(r, w / 2, h / 2)
    d = (f"M{_f(x + r)} {_f(y)} H{_f(x + w - r)} A{_f(r)} {_f(r)} 0 0 1 {_f(x + w)} {_f(y + r)} "
         f"V{_f(y + h - r)} A{_f(r)} {_f(r)} 0 0 1 {_f(x + w - r)} {_f(y + h)} H{_f(x + r)} "
         f"A{_f(r)} {_f(r)} 0 0 1 {_f(x)} {_f(y + h - r)} V{_f(y + r)} A{_f(r)} {_f(r)} 0 0 1 {_f(x + r)} {_f(y)} Z")
    return Shape(d, (x, y, x + w, y + h))


def polygon(pts: Sequence[Pt]) -> Shape:
    d = "M" + " L".join(f"{_f(x)} {_f(y)}" for x, y in pts) + " Z"
    return Shape(d, _bbox(pts))


def teardrop(cx: float, cy: float, r: float, length: float, angle: float) -> Shape:
    """A round base tapering to a point: horns, spikes, petals, ears, claws.
    `angle` is where the point goes, in degrees, 0 = right, -90 = up."""
    a = math.radians(angle)
    tip = (cx + math.cos(a) * length, cy + math.sin(a) * length)
    px, py = -math.sin(a), math.cos(a)          # perpendicular
    bx, by = cx - math.cos(a) * r * .6, cy - math.sin(a) * r * .6
    pts = [tip,
           (cx + px * r * .9 + math.cos(a) * r * .3, cy + py * r * .9 + math.sin(a) * r * .3),
           (cx + px * r, cy + py * r),
           (bx + px * r * .55, by + py * r * .55),
           (bx - px * r * .55, by - py * r * .55),
           (cx - px * r, cy - py * r),
           (cx - px * r * .9 + math.cos(a) * r * .3, cy - py * r * .9 + math.sin(a) * r * .3)]
    return spline(pts, closed=True, tension=.9)


def blob(cx: float, cy: float, rx: float, ry: float, wobble: float = .08, seed: int = 1, n: int = 10) -> Shape:
    """An ellipse that is slightly, organically uneven. Bodies, heads, bushes, clouds."""
    rnd = _rng(seed)
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        k = 1 + (rnd() - .5) * 2 * wobble
        pts.append((cx + math.cos(a) * rx * k, cy + math.sin(a) * ry * k))
    return spline(pts, closed=True)


def _rng(seed: int):
    t = seed * 9301 + 49297

    def r() -> float:
        nonlocal t
        t = (t * 9301 + 49297) % 233280
        return t / 233280
    return r


def transform_pts(pts: Sequence[Pt], dx: float = 0, dy: float = 0, s: float = 1, rot: float = 0,
                  about: Pt = (0, 0), flip: bool = False) -> list[Pt]:
    a = math.radians(rot)
    out = []
    for x, y in pts:
        if flip:
            x = -x
        x, y = x * s, y * s
        x, y = x - about[0], y - about[1]
        x, y = x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)
        out.append((x + about[0] + dx, y + about[1] + dy))
    return out


# --------------------------------------------------------------------------- the scene

_TIERS = {
    # name: (wide blur, edge blur, surfaceScale, specular exponent, edge stroke)
    # Blur cost scales with sigma^2 x area, so the wide blurs are capped: a 60px dome on a
    # 400px piece still reads as round, and renders in a fraction of the time of 100px.
    "xs": (6, 2.5, 4, 24, 5),
    "s": (12, 4, 6.5, 28, 7),
    "m": (24, 6, 13, 30, 9),
    "l": (44, 10, 20, 34, 11),
    "xl": (60, 13, 26, 36, 13),
    # big pieces that should read as flat card with a soft bevel rather than a pillow: walls, roofs, signs
    "flat": (8, 3, 5, 26, 10),
}


def _tier_for(shape: Shape) -> str:
    m = min(shape.w, shape.h)
    if m < 40:
        return "xs"
    if m < 90:
        return "s"
    if m < 220:
        return "m"
    if m < 420:
        return "l"
    return "xl"


@dataclass
class Light:
    """One key light for the whole spread. `dir` points from the subject towards the light."""
    dir: Pt = (-0.6, -0.8)
    key: str = "#fff1d6"      # warm
    bounce: str = "#7fa8ff"   # cool, from the opposite side
    elevation: float = 45
    bounce_elevation: float = 20
    shadow: str = "#10233a"

    @property
    def azimuth(self) -> float:
        return math.degrees(math.atan2(self.dir[1], self.dir[0])) % 360

    @property
    def bounce_azimuth(self) -> float:
        return (self.azimuth + 180 + 8) % 360

    def offset(self, k: float) -> Pt:
        """Where a shadow falls: away from the light, with a little gravity."""
        return (-self.dir[0] * k, -self.dir[1] * k + k * .55)


DUSK = Light(dir=(0.72, -0.55), key="#ffc36b", bounce="#6a4fa8", elevation=28, shadow="#2a1230")
EVENING = Light(dir=(-0.7, -0.55), key="#ffd9a4", bounce="#7a6fe0", elevation=32, shadow="#2a1a3a")
NIGHT = Light(dir=(-0.5, -0.85), key="#e9ecff", bounce="#ffb066", elevation=50, shadow="#0a0f2a")


class Scene:
    """`finish="matte"` (default) shades like printed card: a soft tonal gradient, no specular,
    no bounce glow, depth from the cut edge and cast shadows. `finish="gloss"` is the puffy,
    wet-looking pipeline: strong dome, specular highlight, cool rim."""

    def __init__(self, sid: str, palette: Palette, light: Light | None = None, edge: str | None = None,
                 finish: str = "storybook"):
        self.sid = re.sub(r"[^a-z0-9]+", "-", sid.lower()).strip("-") or "scene"
        self.P = palette
        self.light = light or Light()
        self.finish = finish
        self.edge_color = edge or palette.colors.get("cut", "#fffdf4")
        self.defs: list[str] = []
        self.body: list[str] = []
        self._ids = 0
        self._grads: dict[str, str] = {}
        self._layers: list[Layer] = []
        self.warnings: list[str] = []
        self._filters()

    # ----- ids & defs

    def uid(self, kind: str = "g") -> str:
        self._ids += 1
        return f"{self.sid}-{kind}{self._ids}"

    def radial(self, stops: Sequence[tuple[float, str, float | None]], cx: float = .5, cy: float = .5, r: float = .5,
               fx: float | None = None, fy: float | None = None) -> str:
        key = ("R", tuple(stops), cx, cy, r, fx, fy).__repr__()
        if key in self._grads:
            return self._grads[key]
        gid = self.uid("rg")
        focal = f' fx="{fx}" fy="{fy}"' if fx is not None else ""
        s = "".join(f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a}"' if a is not None else "") + "/>"
                    for o, c, a in stops)
        self.defs.append(f'<radialGradient id="{gid}" cx="{cx}" cy="{cy}" r="{r}"{focal}>{s}</radialGradient>')
        self._grads[key] = gid
        return gid

    def linear(self, stops: Sequence[tuple[float, str, float | None]], x1=0, y1=0, x2=0, y2=1) -> str:
        key = ("L", tuple(stops), x1, y1, x2, y2).__repr__()
        if key in self._grads:
            return self._grads[key]
        gid = self.uid("lg")
        s = "".join(f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a}"' if a is not None else "") + "/>"
                    for o, c, a in stops)
        self.defs.append(f'<linearGradient id="{gid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{s}</linearGradient>')
        self._grads[key] = gid
        return gid

    def _filters(self) -> None:
        L, sid = self.light, self.sid
        az, baz = _f(L.azimuth), _f(L.bounce_azimuth)
        flat = math.sin(math.radians(L.bounce_elevation))   # the bounce's constant term on flat ground
        sox, soy = L.offset(8)
        matte = self.finish != "gloss"
        for name, (wb, eb, ss0, exp, _edge) in ([] if self.finish == "storybook" else list(_TIERS.items())):
            # matte: a shallow relief and low contrast, so the light reads as printed shading
            ss = ss0 * (.28 if matte else 1)
            k1, k3 = (.22, .84) if matte else (1.05, .30)     # flat interior stays the true colour either way
            bounce = "" if matte else f'''
  <feDiffuseLighting in="h" surfaceScale="{ss}" diffuseConstant="1" lighting-color="{L.bounce}" result="rim0">
    <feDistantLight azimuth="{baz}" elevation="{_f(L.bounce_elevation)}"/></feDiffuseLighting>
  <feComponentTransfer in="rim0" result="rim1">
    <feFuncR type="linear" slope="1.1" intercept="{_f(-flat - .06)}"/><feFuncG type="linear" slope="1.1" intercept="{_f(-flat - .06)}"/><feFuncB type="linear" slope="1.1" intercept="{_f(-flat - .06)}"/></feComponentTransfer>
  <feComposite in="rim1" in2="SourceAlpha" operator="in" result="rim"/>
  <feBlend in="shaded" in2="rim" mode="screen" result="withrim"/>
  <feSpecularLighting in="h" surfaceScale="{ss}" specularConstant=".5" specularExponent="{exp}" lighting-color="#ffffff" result="spec0">
    <feDistantLight azimuth="{az}" elevation="{_f(L.elevation + 7)}"/></feSpecularLighting>
  <feComposite in="spec0" in2="SourceAlpha" operator="in" result="spec"/>
  <feComposite in="spec" in2="withrim" operator="arithmetic" k1="0" k2="1" k3="1" k4="0" result="lit"/>'''
            final_in = "shaded" if matte else "lit"
            for variant, with_shadow in (("", True), ("-ns", False)):
                shadow = (f'<feGaussianBlur in="SourceAlpha" stdDeviation="7" result="sb"/>'
                          f'<feOffset in="sb" dx="{_f(sox)}" dy="{_f(soy)}" result="so"/>'
                          f'<feFlood flood-color="{L.shadow}" flood-opacity=".38" result="sc"/>'
                          f'<feComposite in="sc" in2="so" operator="in" result="shadow"/>'
                          f'<feMerge><feMergeNode in="shadow"/><feMergeNode in="clipped"/></feMerge>') if with_shadow else ""
                self.defs.append(f'''<filter id="{sid}-lit-{name}{variant}" x="-25%" y="-25%" width="150%" height="160%" color-interpolation-filters="sRGB">
  <feGaussianBlur in="SourceAlpha" stdDeviation="{wb}" result="hb"/>
  <feGaussianBlur in="SourceAlpha" stdDeviation="{eb}" result="hs"/>
  <feComposite in="hb" in2="hs" operator="arithmetic" k1="0" k2=".62" k3=".38" k4="0" result="h"/>
  <feDiffuseLighting in="h" surfaceScale="{ss}" diffuseConstant="1" lighting-color="{L.key}" result="key">
    <feDistantLight azimuth="{az}" elevation="{_f(L.elevation)}"/></feDiffuseLighting>
  <feComposite in="key" in2="SourceGraphic" operator="arithmetic" k1="{k1}" k2="0" k3="{k3}" k4="0" result="shaded"/>{bounce}
  <feComposite in="{final_in}" in2="SourceAlpha" operator="in" result="clipped"/>
  {shadow}
</filter>''')
        # a shadow with no lighting: origami and other flat pieces
        self.defs.append(f'<filter id="{sid}-shadow" x="-25%" y="-25%" width="150%" height="160%">'
                         f'<feDropShadow dx="{_f(sox)}" dy="{_f(soy)}" stdDeviation="7" flood-color="{L.shadow}" flood-opacity=".4"/></filter>')
        # the two faces of a V-fold: one brightened towards the key, one dimmed and cooled
        kr, kg, kb = _rgb(L.key)
        self.defs.append(f'<filter id="{sid}-face-lit" color-interpolation-filters="sRGB"><feComponentTransfer>'
                         f'<feFuncR type="linear" slope="1.12" intercept="{_f(kr / 255 * .05)}"/><feFuncG type="linear" slope="1.1" intercept="{_f(kg / 255 * .05)}"/>'
                         f'<feFuncB type="linear" slope="1.06" intercept="{_f(kb / 255 * .03)}"/></feComponentTransfer></filter>')
        self.defs.append(f'<filter id="{sid}-face-dim" color-interpolation-filters="sRGB"><feComponentTransfer>'
                         f'<feFuncR type="linear" slope=".78"/><feFuncG type="linear" slope=".8"/><feFuncB type="linear" slope=".88"/></feComponentTransfer></filter>')
        self.defs.append(f'<filter id="{sid}-apex"><feFlood flood-color="{tint(L.key, .35)}" flood-opacity=".9" result="c"/>'
                         f'<feComposite in="c" in2="SourceAlpha" operator="in"/></filter>')
        board = mix(self.edge_color, "#cdbf9f", .3 if self.finish != "storybook" else .08)
        self.defs.append(f'<filter id="{sid}-rim" x="-10%" y="-10%" width="120%" height="120%">'
                         f'<feMorphology in="SourceAlpha" operator="dilate" radius="{3.5 if self.finish == "storybook" else 4.5}" result="d"/>'
                         f'<feFlood flood-color="{board}" result="c"/><feComposite in="c" in2="d" operator="in" result="rim"/>'
                         f'<feMorphology in="SourceAlpha" operator="dilate" radius="1.2" result="d1"/>'
                         f'<feFlood flood-color="{L.shadow}" flood-opacity=".22" result="k"/><feComposite in="k" in2="d1" operator="in" result="hair"/>'
                         f'<feMerge><feMergeNode in="rim"/><feMergeNode in="hair"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
        # a standing card's shadow on the page: the card flooded dark and softened (the caller
        # mirrors and skews it about the card's base line)
        self.defs.append(f'<filter id="{sid}-ground" x="-20%" y="-20%" width="140%" height="140%">'
                         f'<feFlood flood-color="{L.shadow}" flood-opacity="{.32 if self.finish == "storybook" else .55}" result="c"/>'
                         f'<feComposite in="c" in2="SourceAlpha" operator="in" result="s"/>'
                         f'<feGaussianBlur in="s" stdDeviation="{7 if self.finish == "storybook" else 5}"/></filter>')
        # paper grain, applied once per layer rather than once per piece
        self.defs.append(f'<filter id="{sid}-grain" x="-5%" y="-5%" width="110%" height="110%" color-interpolation-filters="sRGB">'
                         f'<feTurbulence type="fractalNoise" baseFrequency=".55" numOctaves="2" seed="7" result="n"/>'
                         f'<feColorMatrix in="n" type="saturate" values="0" result="ng"/>'
                         f'<feComponentTransfer in="ng" result="nl"><feFuncR type="linear" slope=".30" intercept=".78"/><feFuncG type="linear" slope=".30" intercept=".78"/><feFuncB type="linear" slope=".28" intercept=".79"/><feFuncA type="linear" slope="0" intercept="1"/></feComponentTransfer>'
                         f'<feBlend in="SourceGraphic" in2="nl" mode="multiply" result="m"/>'
                         f'<feComposite in="m" in2="SourceAlpha" operator="in"/></filter>')
        # the shadow a whole standing layer throws on the page (long, softer)
        for name, k, std, op in (("far", 10, 8, .28), ("mid", 18, 12, .36), ("near", 28, 18, .44)):
            ox, oy = L.offset(k)
            self.defs.append(f'<filter id="{sid}-cast-{name}" x="-30%" y="-30%" width="160%" height="180%">'
                             f'<feDropShadow dx="{_f(ox)}" dy="{_f(oy)}" stdDeviation="{std}" flood-color="{L.shadow}" flood-opacity="{op}"/></filter>')
        # depth of field for the back panel; a soft blur for contact shadows
        self.defs.append(f'<filter id="{sid}-dof" x="-10%" y="-10%" width="120%" height="120%">'
                         f'<feGaussianBlur stdDeviation="7"/><feColorMatrix type="saturate" values=".72"/></filter>')
        self.defs.append(f'<filter id="{sid}-soft" x="-40%" y="-80%" width="180%" height="260%"><feGaussianBlur stdDeviation="14"/></filter>')
        self.defs.append(f'<filter id="{sid}-blush" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="9"/></filter>')
        self.defs.append(f'<radialGradient id="{sid}-glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{tint(L.key, .5)}" stop-opacity=".85"/>'
                         f'<stop offset="1" stop-color="{tint(L.key, .5)}" stop-opacity="0"/></radialGradient>')

    # ----- structure

    def back_panel(self, sky: tuple[str, str] | None = None, opacity: float = 1.0) -> "BackPanel":
        top, bottom = sky or (self.P.sky1, self.P.sky2)
        gid = self.linear([(0, top, None), (1, bottom, None)])
        self.body.append(f'<rect width="{W}" height="{H}" fill="url(#{gid})"/>')
        bp = BackPanel(self, opacity)
        bp.horizon = bottom
        self._layers.append(bp)
        return bp

    def base_page(self, shadow: tuple[float, float, float] | None = (420, 770, 250), path: bool = True,
                  flowers: bool = True, color: str | None = None) -> "Layer":
        """The flat card the hero stands on. Nearly empty on purpose."""
        ground = color or self.P.ground
        d = "M-200 900 L60 648 Q700 612 1700 648 L1900 900 Z"
        seam = self.linear([(0, self.light.shadow, .42), (.2, self.light.shadow, 0)])
        L = Layer(self, depth=.12, rise=None, cast=None)
        # light falls across the page too: brighter towards the key light
        lx = .5 + self.light.dir[0] * .3
        pg = self.radial([(0, tint(ground, .22), None), (1, shade(ground, .10), None)], cx=lx, cy=.15, r=.9)
        L.raw(f'<path d="{d}" fill="url(#{pg})"/>')
        L.raw(f'<path d="{d}" fill="url(#{seam})"/>')
        if path:
            L.raw(f'<path d="M300 634 q-70 132 -252 266 L570 900 q28-152 152-266 Z" fill="{tint(ground, .45)}" opacity=".8"/>')
        if flowers:
            a, b = self.P.accent, self.P.accent2
            L.raw(f'<g opacity=".85"><circle cx="118" cy="764" r="8" fill="{a}"/><circle cx="240" cy="842" r="7" fill="{a}"/>'
                  f'<circle cx="626" cy="702" r="7" fill="{a}"/><circle cx="694" cy="812" r="8" fill="{a}"/>'
                  f'<circle cx="516" cy="874" r="7" fill="{a}"/><circle cx="178" cy="816" r="6" fill="{b}"/>'
                  f'<circle cx="668" cy="752" r="6" fill="{b}"/><circle cx="432" cy="886" r="6" fill="{b}"/></g>')
        if shadow:
            L.contact(*shadow)
        self._layers.append(L)
        return L

    def hero(self, depth: float = .15, rise: int = 2, sway: float | None = None) -> "Layer":
        L = Layer(self, depth=depth, rise=rise, cast="near", sway=sway)
        self._layers.append(L)
        return L

    def layer(self, depth: float, rise: int = 3, cast: str | None = "mid", sway: float | None = None) -> "Layer":
        L = Layer(self, depth=depth, rise=rise, cast=cast, sway=sway)
        self._layers.append(L)
        return L

    def flats(self, depth: float = .17, rise: int = 4) -> "Layer":
        L = Layer(self, depth=depth, rise=rise, cast="mid")
        self._layers.append(L)
        return L

    # ----- output

    def render(self) -> str:
        parts = [f'<svg viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">',
                 "<defs>", *self.defs, "</defs>", *self.body]
        for L in self._layers:
            parts.append(L.render())
        parts.append("</svg>\n")
        return "\n".join(parts)

    def write(self, path: str | Path) -> Path:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(self.render())
        for w in self.warnings:
            print(f"  {self.sid}: {w}")
        return p


class Layer:
    """One distance band: parallax outside, unfolding and cast shadow inside."""

    mirror = False   # flip about x=440 (the leaf's centre); place the sun on the other side to match

    def __init__(self, scene: Scene, depth: float, rise: int | None, cast: str | None, sway: float | None = None):
        self.sc = scene
        self.depth, self.rise, self.cast, self.sway = depth, rise, cast, sway
        self.items: list[str] = []
        self.n_pieces = 0

    # ----- primitives

    def raw(self, svg: str) -> "Layer":
        self.items.append(svg)
        return self

    def piece(self, shape: Shape, color: str, *, lit: bool | None = None, edge: float | None = None,
              cast: bool = True, details: Sequence[str] = (), opacity: float | None = None,
              transform: str | None = None, tier: str | None = None, cls: str | None = None) -> "Layer":
        """One piece of cut card with printed, lit artwork. `details` are extra SVG drawn on the
        piece before it is lit (stripes, spots, a belly), so they shade with it."""
        sc = self.sc
        if lit is None:
            lit = sc.finish != "storybook"    # storybook art is printed flat
        if getattr(self, "_anim_depth", 0):
            lit, cast = False, False          # moving parts must not carry filters
        t = tier or _tier_for(shape)
        ew = _TIERS[t][4] if edge is None else edge
        if getattr(self, "_in_card", 0):
            ew = 0                            # the card is cut once, around its whole silhouette
            color = mix(color, "#efe6d2", .07)  # ink on paper, not light on a screen
        if self.cast == "near":  # the hero: check it sits on the leaf
            x0, y0, x1, y1 = shape.bbox
            if x0 < HERO_BOX[0] - 30 or y0 < HERO_BOX[1] - 30 or x1 > HERO_BOX[2] + 30 or y1 > HERO_BOX[3] + 30:
                sc.warnings.append(f"hero piece bbox {tuple(round(v) for v in shape.bbox)} leaves the hero box {HERO_BOX}")
        attrs = (f' transform="{transform}"' if transform else "") + (f' opacity="{opacity}"' if opacity is not None else "") \
            + (f' class="{cls}"' if cls else "")
        g = [f'<g{attrs}>']
        if ew > 0:
            g.append(f'<path d="{shape.d}" fill="{sc.edge_color}" stroke="{sc.edge_color}" stroke-width="{_f(ew * 2)}" stroke-linejoin="round"/>')
        inner = f'<path d="{shape.d}" fill="{color}"/>' + "".join(details)
        if lit:
            g.append(f'<g filter="url(#{sc.sid}-lit-{t}{"" if cast else "-ns"})">{inner}</g>')
        else:
            g.append(inner)
        g.append("</g>")
        self.items.append("".join(g))
        self.n_pieces += 1
        return self

    def facets(self, polys: Sequence[Sequence[Pt]], color: str, *, center: Pt | None = None, contrast: float = .6,
               jitter: float = .16, crease: str | None = None, cast: bool = True, seed: int = 1,
               tones: Sequence[float] | None = None) -> "Layer":
        """Folded paper. Each polygon is one facet, filled flat: lighter the more it faces the
        light, darker the more it faces away, with a little jitter so neighbours differ like
        real folds. `tones` overrides the automatic shade per facet (-1 dark .. +1 lit).
        No lighting filter runs, so origami heroes are also the cheapest to draw."""
        sc = self.sc
        allpts = [pt for poly in polys for pt in poly]
        x0, y0, x1, y1 = _bbox(allpts)
        cx, cy = center or ((x0 + x1) / 2, (y0 + y1) / 2)
        lx, ly = sc.light.dir
        rnd = _rng(seed)
        crease_c = crease or mix(color, WARM, .45)
        if self.cast == "near" and (x0 < HERO_BOX[0] - 30 or y0 < HERO_BOX[1] - 30 or x1 > HERO_BOX[2] + 30 or y1 > HERO_BOX[3] + 30):
            sc.warnings.append(f"origami hero bbox {tuple(round(v) for v in (x0, y0, x1, y1))} leaves the hero box {HERO_BOX}")
        out = [f'<g filter="url(#{sc.sid}-shadow)">' if cast else "<g>"]
        for i, poly in enumerate(polys):
            fx = sum(p[0] for p in poly) / len(poly)
            fy = sum(p[1] for p in poly) / len(poly)
            if tones is not None and i < len(tones) and tones[i] is not None:
                tone = tones[i]
            else:
                dx, dy = fx - cx, fy - cy
                L = math.hypot(dx, dy) or 1
                tone = (dx / L) * lx + (dy / L) * ly + (rnd() - .5) * 2 * jitter
            tone = max(-1, min(1, tone))
            fill = tint(color, tone * contrast) if tone >= 0 else shade(color, -tone * contrast)
            d = "M" + " L".join(f"{_f(x)} {_f(y)}" for x, y in poly) + " Z"
            out.append(f'<path d="{d}" fill="{fill}" stroke="{crease_c}" stroke-width="1.4" stroke-linejoin="round" stroke-opacity=".55"/>')
        out.append("</g>")
        self.items.append("".join(out))
        self.n_pieces += 1
        return self

    def flat(self, shape: Shape, color: str, **kw) -> "Layer":
        """A piece that is printed flat rather than modelled: a wall, a page, a sign."""
        return self.piece(shape, color, lit=False, **kw)

    def eye(self, cx: float, cy: float, r: float, iris: str = "#2b7bd6", look: Pt = (0, 0), lid: float = .22,
            lash: bool = True, brow: str | None = None, squash: float = 1.15, lash_color: str | None = None,
            pupil: str = "round") -> "Layer":
        """A Pixar eye: wet sclera, deep iris, big pupil, two highlights, an upper lid.
        `look` shifts the iris; `squash` > 1 makes it taller than wide (appealing)."""
        sc = self.sc
        gloss = sc.finish == "gloss"
        ry = r * squash
        sclera = sc.radial([(.55, "#fffdf6" if not gloss else "#ffffff", None), (1, "#dcd8cc" if not gloss else "#d7dbe6", None)], cx=.5, cy=.42, r=.72)
        ir = sc.radial([(0, tint(iris, .55), None), (.45, iris, None), (.78, shade(iris, .35), None), (1, shade(iris, .65), None)],
                       cx=.5, cy=.58, r=.52)
        ix, iy = cx + look[0], cy + look[1]
        ri = r * .62
        parts = [f'<g class="eye">',
                 f'<ellipse cx="{_f(cx)}" cy="{_f(cy)}" rx="{_f(r)}" ry="{_f(ry)}" fill="url(#{sclera})"/>',
                 f'<circle cx="{_f(ix)}" cy="{_f(iy)}" r="{_f(ri)}" fill="url(#{ir})"/>',
                 (f'<ellipse cx="{_f(ix + r * .02)}" cy="{_f(iy)}" rx="{_f(ri * .17)}" ry="{_f(ri * .78)}" fill="#0b1020"/>' if pupil == "slit" else
                  f'<circle cx="{_f(ix + r * .04)}" cy="{_f(iy + r * .04)}" r="{_f(ri * .5)}" fill="#0b1020"/>'),
                 f'<ellipse cx="{_f(ix - ri * .42)}" cy="{_f(iy - ri * .46)}" rx="{_f(ri * (.34 if gloss else .26))}" ry="{_f(ri * (.22 if gloss else .17))}" fill="#fff" opacity="{.95 if gloss else .85}" '
                 f'transform="rotate(-24 {_f(ix - ri * .42)} {_f(iy - ri * .46)})"/>']
        if gloss:
            parts.append(f'<circle cx="{_f(ix + ri * .38)}" cy="{_f(iy + ri * .44)}" r="{_f(ri * .13)}" fill="#fff" opacity=".7"/>')
        if lid > 0:
            parts.append(f'<path d="M{_f(cx - r)} {_f(cy)} A{_f(r)} {_f(ry)} 0 0 1 {_f(cx + r)} {_f(cy)} '
                         f'A{_f(r)} {_f(ry * (1 - lid * 2.2))} 0 0 0 {_f(cx - r)} {_f(cy)} Z" fill="#0b1020" opacity=".22"/>')
        if lash:
            lc = lash_color or shade(iris, .8)
            parts.append(f'<path d="M{_f(cx - r * 1.02)} {_f(cy - ry * .1)} A{_f(r * 1.02)} {_f(ry * 1.05)} 0 0 1 {_f(cx + r * 1.02)} {_f(cy - ry * .1)}" '
                         f'fill="none" stroke="{lc}" stroke-width="{_f(max(3, r * .18))}" stroke-linecap="round"/>')
        if brow:
            parts.append(f'<path d="M{_f(cx - r * 1.1)} {_f(cy - ry * 1.5)} q{_f(r * 1.1)} {_f(-r * .6)} {_f(r * 2.2)} {_f(-r * .05)}" '
                         f'fill="none" stroke="{brow}" stroke-width="{_f(max(4, r * .28))}" stroke-linecap="round"/>')
        parts.append("</g>")
        self.items.append("".join(parts))
        return self

    def blush(self, cx: float, cy: float, rx: float, ry: float | None = None, color: str = "#ff7a6a", opacity: float = .35) -> "Layer":
        ry = rx * .7 if ry is None else ry
        self.items.append(f'<ellipse cx="{_f(cx)}" cy="{_f(cy)}" rx="{_f(rx)}" ry="{_f(ry)}" fill="{color}" opacity="{opacity}" filter="url(#{self.sc.sid}-blush)"/>')
        return self

    def line(self, d: str, color: str, width: float, opacity: float = 1) -> "Layer":
        """A drawn line: a mouth, a seam, a nostril arc."""
        self.items.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{_f(width)}" stroke-linecap="round" stroke-linejoin="round" opacity="{opacity}"/>')
        return self

    def clip_of(self, shape: Shape) -> str:
        cid = self.sc.uid("clip")
        self.sc.defs.append(f'<clipPath id="{cid}"><path d="{shape.d}"/></clipPath>')
        return cid

    def tone(self, shape: Shape, color: str, frac: float = .38, side: str = "bottom", opacity: float = 1) -> "Layer":
        """A second flat tone printed on part of a shape — the storybook way to shade.
        `side` bottom/top/left/right, `frac` how much of the shape it covers."""
        cid = self.clip_of(shape)
        x0, y0, x1, y1 = shape.bbox
        if side == "bottom":
            r = (x0 - 5, y1 - shape.h * frac, shape.w + 10, shape.h * frac + 5)
        elif side == "top":
            r = (x0 - 5, y0 - 5, shape.w + 10, shape.h * frac + 5)
        elif side == "left":
            r = (x0 - 5, y0 - 5, shape.w * frac + 5, shape.h + 10)
        else:
            r = (x1 - shape.w * frac, y0 - 5, shape.w * frac + 5, shape.h + 10)
        self.items.append(f'<g clip-path="url(#{cid})"><rect x="{_f(r[0])}" y="{_f(r[1])}" width="{_f(r[2])}" height="{_f(r[3])}" fill="{color}" opacity="{opacity}"/></g>')
        return self

    def marks(self, shape: Shape, kind: str, color: str, step: float = 26, size: float = 10, angle: float = -35,
              opacity: float = .75, seed: int = 1, inset: float = 0) -> "Layer":
        """Drawn texture inside a shape: `dash` (leaf strokes), `grass` (upright ticks), `dot`,
        `scale` (overlapping arcs), `plank` (horizontal lines), `stone` (rounded blocks)."""
        cid = self.clip_of(shape)
        x0, y0, x1, y1 = shape.bbox
        rnd = _rng(seed)
        out = [f'<g clip-path="url(#{cid})" fill="none" stroke="{color}" stroke-width="{_f(max(2, size * .32))}" stroke-linecap="round" opacity="{opacity}">']
        a = math.radians(angle)
        dx, dy = math.cos(a) * size, math.sin(a) * size
        row = 0
        y = y0 + inset
        while y < y1 - inset:
            x = x0 + inset + (step / 2 if row % 2 else 0)
            while x < x1 - inset:
                jx, jy = (rnd() - .5) * step * .5, (rnd() - .5) * step * .4
                px, py = x + jx, y + jy
                if kind == "dash":
                    out.append(f'<path d="M{_f(px)} {_f(py)} l{_f(dx)} {_f(dy)}"/>')
                elif kind == "grass":
                    out.append(f'<path d="M{_f(px)} {_f(py + size)} q{_f((rnd() - .5) * 6)} {_f(-size * .6)} {_f((rnd() - .5) * 8)} {_f(-size)}"/>')
                elif kind == "dot":
                    out.append(f'<circle cx="{_f(px)}" cy="{_f(py)}" r="{_f(size * .22)}" fill="{color}" stroke="none"/>')
                elif kind == "scale":
                    out.append(f'<path d="M{_f(px - size * .5)} {_f(py)} a{_f(size * .5)} {_f(size * .42)} 0 0 0 {_f(size)} 0"/>')
                elif kind == "plank":
                    out.append(f'<path d="M{_f(x0)} {_f(py)} H{_f(x1)}"/>')
                    break
                elif kind == "stone":
                    w, h = step * (.7 + rnd() * .5), step * .55
                    out.append(f'<rect x="{_f(px)}" y="{_f(py)}" width="{_f(w)}" height="{_f(h)}" rx="{_f(h * .4)}"/>')
                x += step
            y += step * (.9 if kind == "scale" else 1)
            row += 1
        out.append("</g>")
        self.items.append("".join(out))
        return self

    def dot_eye(self, cx: float, cy: float, r: float, look: Pt = (0, 0), lid: bool = False) -> "Layer":
        """The storybook eye: a white with a dark dot and a pin of light. Small."""
        self.items.append(f'<ellipse cx="{_f(cx)}" cy="{_f(cy)}" rx="{_f(r)}" ry="{_f(r * 1.1)}" fill="#fffaf0"/>'
                          f'<circle cx="{_f(cx + look[0])}" cy="{_f(cy + look[1])}" r="{_f(r * .55)}" fill="#2a1e1a"/>'
                          f'<circle cx="{_f(cx + look[0] + r * .2)}" cy="{_f(cy + look[1] - r * .22)}" r="{_f(r * .16)}" fill="#fff"/>')
        if lid:
            self.items.append(f'<path d="M{_f(cx - r)} {_f(cy - r * .2)} A{_f(r)} {_f(r * 1.1)} 0 0 1 {_f(cx + r)} {_f(cy - r * .2)} L{_f(cx + r)} {_f(cy - r * 1.3)} L{_f(cx - r)} {_f(cy - r * 1.3)} Z" fill="#2a1e1a" opacity=".9"/>')
        return self

    def cheek(self, cx: float, cy: float, r: float, color: str = "#f28b7d", opacity: float = .55) -> "Layer":
        self.items.append(f'<ellipse cx="{_f(cx)}" cy="{_f(cy)}" rx="{_f(r)}" ry="{_f(r * .7)}" fill="{color}" opacity="{opacity}"/>')
        return self

    def smile(self, cx: float, cy: float, w: float, depth: float, color: str, width: float = 6,
              tongue: str | None = None, teeth: int = 0) -> "Layer":
        """A mouth line curving down by `depth` (negative for a frown), optional tongue and teeth."""
        x0, x1 = cx - w / 2, cx + w / 2
        if tongue:
            self.items.append(f'<path d="M{_f(cx - w * .22)} {_f(cy + depth * .55)} q{_f(w * .22)} {_f(depth * .9)} {_f(w * .44)} 0 Z" fill="{tongue}"/>')
        for i in range(teeth):
            tx = x0 + w * (i + 1) / (teeth + 1)
            ty = cy + depth * (1 - ((tx - cx) / (w / 2)) ** 2) - 2
            self.items.append(f'<path d="M{_f(tx - 6)} {_f(ty)} L{_f(tx)} {_f(ty + 13)} L{_f(tx + 6)} {_f(ty)} Z" fill="#fff8e6"/>')
        self.items.append(f'<path d="M{_f(x0)} {_f(cy)} Q{_f(cx)} {_f(cy + depth * 2)} {_f(x1)} {_f(cy)}" fill="none" '
                          f'stroke="{color}" stroke-width="{_f(width)}" stroke-linecap="round"/>')
        return self

    def claws(self, cx: float, cy: float, n: int = 3, r: float = 9, length: float = 22, angle: float = 90,
              spread: float = 26, color: str = "#fff8e6") -> "Layer":
        """`n` little claws fanned around `angle` (degrees, 90 = down), `spread` apart along the perpendicular."""
        a = math.radians(angle)
        px, py = -math.sin(a), math.cos(a)
        for i in range(n):
            k = (i - (n - 1) / 2) * spread
            self.piece(teardrop(cx + px * k, cy + py * k, r, length, angle + (i - (n - 1) / 2) * 12), color, cast=False, tier="xs", edge=3)
        return self

    def contact(self, cx: float, cy: float, rx: float, ry: float | None = None, opacity: float = .5) -> "Layer":
        """The soft pool of shadow where something stands on the page."""
        ry = max(22, rx / 7) if ry is None else ry
        ox, oy = self.sc.light.offset(3)
        self.items.append(f'<ellipse cx="{_f(cx + ox)}" cy="{_f(cy + oy * .3)}" rx="{_f(rx)}" ry="{_f(ry)}" fill="{self.sc.light.shadow}" '
                          f'opacity="{opacity}" filter="url(#{self.sc.sid}-soft)"/>')
        return self

    def glow(self, cx: float, cy: float, r: float, opacity: float = 1) -> "Layer":
        self.items.append(f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(r)}" fill="url(#{self.sc.sid}-glow)" opacity="{opacity}"/>')
        return self

    def bush(self, x: float, y: float, s: float = 1.0, color: str | None = None, berries: str | None = None,
             edge: float | None = None) -> "Layer":
        """A small foreground flat: three overlapping mounds."""
        c = color or self.sc.P.land3
        pts = [(0, 100), (14, 44), (54, 22), (104, 30), (136, 6), (188, 16), (224, 40), (268, 34), (300, 60), (300, 100)]
        shp = spline(transform_pts(pts, dx=x, dy=y, s=s), closed=True, tension=.9)
        dots = ""
        if berries:
            dots = "".join(f'<circle cx="{_f(x + bx * s)}" cy="{_f(y + by * s)}" r="{_f(7 * s)}" fill="{berries}"/>'
                           for bx, by in ((60, 66), (150, 50), (236, 70)))
        return self.piece(shp, c, details=[dots] if dots else (), edge=edge)

    @staticmethod
    def scales(x: float, y: float, w: float, h: float, r: float, color: str, opacity: float = .45, width: float = 3) -> str:
        """Rows of overlapping scale arcs filling the box (x, y, w, h), for a piece's `details`.
        Keep the box inside the piece: details outside the shape extend its silhouette."""
        out, row = [], 0
        cy = y + r
        while cy < y + h:
            off = r if row % 2 else 0
            cx = x + off
            while cx < x + w:
                out.append(f'<path d="M{_f(cx - r)} {_f(cy)} A{_f(r)} {_f(r * .8)} 0 0 0 {_f(cx + r)} {_f(cy)}" fill="none" '
                           f'stroke="{color}" stroke-width="{_f(width)}" opacity="{opacity}"/>')
                cx += 2 * r
            cy += r * 1.1
            row += 1
        return "".join(out)

    def card(self, base_y: float, crease_x: float | None = None, fold: float | bool = 0, **kw) -> "Card":
        """A standing card on the page; see `Card`."""
        return Card(self, base_y, crease_x, fold, **kw)

    def animate(self, kind: str, origin: Pt, duration: float | None = None, delay: float = 0, amount: float | None = None) -> "Anim":
        """A subtle motion on whatever is drawn inside: `flap` / `flap-r` (a wing about its
        root), `sway` (a tail, a spear, a branch), `bob`, `flicker` (fire), `pulse` (a glow),
        `spin` (a wheel). Pieces drawn inside are forced flat and un-shadowed so the repaint
        each frame is cheap; the card's page shadow stays still.

            with c.animate("flap", origin=(400, 470)):
                c.piece(wing, WING, lit=False)
        """
        return Anim(self, kind, origin, duration, delay, amount)

    def group(self, transform: str, cls: str | None = None) -> "Group":
        return Group(self, transform, cls)

    # ----- render

    grain = True

    def render(self) -> str:
        inner = "\n".join(self.items)
        wrap_open, wrap_close = "", ""
        if self.mirror:
            inner = f'<g transform="matrix(-1 0 0 1 880 0)">\n{inner}\n</g>'
        if self.grain and self.n_pieces:
            inner = f'<g filter="url(#{self.sc.sid}-grain)">\n{inner}\n</g>'
        if self.rise is not None:
            filt = f' filter="url(#{self.sc.sid}-cast-{self.cast})"' if self.cast else ""
            wrap_open += f'<g class="pop rise-{self.rise}"{filt}>'
            wrap_close = "</g>" + wrap_close
        if self.sway:
            wrap_open += f'<g class="sway" style="animation-duration:{_f(self.sway)}s">'
            wrap_close = "</g>" + wrap_close
        return f'<g data-depth="{self.depth}">{wrap_open}\n{inner}\n{wrap_close}</g>'


class Card:
    """A flat card standing upright on the page — the unit a real pop-up is built from.

    Draw artwork on it with the usual `piece()/facets()/eye()` calls (it behaves as a Layer),
    then `done()`. The artwork is designed flat, feet on `base_y`; the card projects it as a
    plane standing on the page seen from a camera tilted `tilt` degrees above the table:
    heights compress by cos(tilt), and — for a V-fold — each half swings back from the reader
    by `open` degrees about the crease, so it foreshortens and its outer edge recedes up the
    page. Each face gets its own tone, the apex a lit folded edge, and every face throws a
    shadow projected from its own base line onto the page.

        with g.card(base_y=764, crease_x=430, fold=True) as c:
            c.piece(body, "#3b2a26")
    """

    def __init__(self, layer: "Layer", base_y: float, crease_x: float | None = None, fold: float | bool = 0,
                 squash: float = .38, skew: float | None = None, cast_shadow: bool = True, height: float = 420,
                 crease_line: bool = False, open: float = 28, tilt: float = 0, shadow_len: float = .55, tab: float = 0):
        self.tab = tab
        self.layer, self.base_y, self.crease_x = layer, base_y, crease_x
        self.fold = bool(fold) and crease_x is not None
        self.open, self.tilt, self.shadow_len = open, tilt, shadow_len
        self.cast_shadow = cast_shadow
        self._saved = layer.items
        layer.items = []
        layer._in_card = getattr(layer, "_in_card", 0) + 1

    def __enter__(self) -> "Layer":
        return self.layer

    def __exit__(self, *exc) -> None:
        self.done()

    @staticmethod
    def _m(a, b, c, d, e, f) -> str:
        return f'matrix({_f(a)} {_f(b)} {_f(c)} {_f(d)} {_f(e)} {_f(f)})'

    def done(self) -> None:
        art = "\n".join(self.layer.items)
        still = art.replace('data-anim="', 'data-anim-off="')      # the page shadow does not move
        self.layer.items = self._saved
        self.layer._in_card -= 1
        sc, by = self.layer.sc, self.base_y
        T, Ph = math.radians(self.tilt if self.tilt else (16 if self.fold else 0)), math.radians(self.open)
        sT, cT, sP, cP = math.sin(T), math.cos(T), math.sin(Ph), math.cos(Ph)
        lx = sc.light.dir[0]
        # where a unit of height lands on the page as shadow: away from the light, towards the reader
        sx, sy = -lx * .55 * self.shadow_len, .32 * self.shadow_len
        if sc.finish == "storybook":
            sx, sy = .10, .12                 # a photographed pop-up: short, soft, straight down
        out = []
        if self.fold:
            cx = self.crease_x
            lid, rid = sc.uid("clipL"), sc.uid("clipR")
            sc.defs.append(f'<clipPath id="{lid}"><rect x="-3000" y="-3000" width="{_f(3000 + cx)}" height="8000"/></clipPath>')
            sc.defs.append(f'<clipPath id="{rid}"><rect x="{_f(cx)}" y="-3000" width="6000" height="8000"/></clipPath>')
            # each face swings back from the reader about the crease: x foreshortens by cos(open),
            # and a point `u` from the crease sits u*sin(open) deeper, i.e. u*sin(open)*sin(tilt) higher on screen
            fs, rec = math.cos(Ph), math.sin(Ph) * sT
            faceL = self._m(fs, rec, 0, cT, cx * (1 - fs), by - cx * rec - by * cT)
            faceR = self._m(fs, -rec, 0, cT, cx * (1 - fs), by + cx * rec - by * cT)
            shL = self._m(fs, rec, -sx, -sy, cx * (1 - fs) + by * sx, by - cx * rec + by * sy)
            shR = self._m(fs, -rec, -sx, -sy, cx * (1 - fs) + by * sx, by + cx * rec + by * sy)
            if self.cast_shadow:
                for m, clip in ((shL, lid), (shR, rid)):
                    out.append(f'<g transform="{m}" filter="url(#{sc.sid}-ground)" opacity=".85"><g clip-path="url(#{clip})">{still}</g></g>')
            lit_left = lx < 0
            for m, clip, lit in ((faceL, lid, lit_left), (faceR, rid, not lit_left)):
                out.append(f'<g transform="{m}" filter="url(#{sc.sid}-face-{"lit" if lit else "dim"})"><g clip-path="url(#{clip})"><g filter="url(#{sc.sid}-rim)">{art}</g></g></g>')
            # the folded apex catches the light: a 3px slice of the artwork at the crease, flooded light
            aid = sc.uid("apex")
            sc.defs.append(f'<clipPath id="{aid}"><rect x="{_f(cx - 1.5)}" y="-3000" width="3" height="8000"/></clipPath>')
            out.append(f'<g transform="{faceR}" filter="url(#{sc.sid}-apex)" opacity=".8"><g clip-path="url(#{aid})">{art}</g></g>')
        else:
            face = self._m(1, 0, 0, cT, 0, by - by * cT)
            sh = self._m(1, 0, -sx, -sy, by * sx, by + by * sy)
            if self.cast_shadow:
                out.append(f'<g transform="{sh}" filter="url(#{sc.sid}-ground)" opacity=".85">{still}</g>')
            tab = (f'<rect x="{_f(self.tab_x[0])}" y="{_f(by - 2)}" width="{_f(self.tab_x[1] - self.tab_x[0])}" height="{_f(self.tab)}" fill="{sc.edge_color}"/>'
                   if self.tab and getattr(self, "tab_x", None) else "")
            out.append(f'<g transform="{face}" filter="url(#{sc.sid}-rim)">{art}{tab}</g>')
        self.layer.items.append(f'<g class="card">{"".join(out)}</g>')


class Anim:
    def __init__(self, layer: "Layer", kind: str, origin: Pt, duration, delay, amount):
        self.layer, self.kind, self.origin, self.duration, self.delay, self.amount = layer, kind, origin, duration, delay, amount
        self._saved = layer.items
        layer.items = []
        layer._anim_depth = getattr(layer, "_anim_depth", 0) + 1

    def __enter__(self) -> "Layer":
        return self.layer

    def __exit__(self, *exc) -> None:
        inner = "\n".join(self.layer.items)
        self.layer.items = self._saved
        self.layer._anim_depth -= 1
        style = f"transform-origin:{_f(self.origin[0])}px {_f(self.origin[1])}px"
        if self.duration: style += f";animation-duration:{_f(self.duration)}s"
        if self.delay: style += f";animation-delay:{_f(-abs(self.delay))}s"
        if self.amount is not None: style += f";--amt:{_f(self.amount)}"
        self.layer.items.append(f'<g data-anim="{self.kind}" style="{style}">\n{inner}\n</g>')


class Group:
    """Pieces drawn inside a transform: a character built in local coordinates, then placed.
    Everything drawn through the group is translated for hero-box checking."""

    def __init__(self, layer: Layer, transform: str, cls: str | None):
        self.layer, self.transform, self.cls = layer, transform, cls
        self._saved = layer.items
        layer.items = []

    def __enter__(self) -> Layer:
        return self.layer

    def __exit__(self, *exc) -> None:
        inner = "\n".join(self.layer.items)
        self.layer.items = self._saved
        c = f' class="{self.cls}"' if self.cls else ""
        self.layer.items.append(f'<g transform="{self.transform}"{c}>\n{inner}\n</g>')


class BackPanel(Layer):
    """The printed panel at the back of the spread: soft, out of focus, no cut edges."""

    def __init__(self, scene: Scene, opacity: float = 1.0):
        super().__init__(scene, depth=.02, rise=None, cast=None)
        self.opacity = opacity

    def hills(self, colors: Sequence[str] | None = None, seed: int = 3) -> "BackPanel":
        P = self.sc.P
        hz = getattr(self, "horizon", P.sky2)
        cs = colors or (mix(P.land1, hz, .45), mix(P.land2, hz, .5))
        rnd = _rng(seed)
        for i, c in enumerate(cs):
            base = 600 + i * 26
            pts = [(-60, 720)]
            x = -60
            while x < W + 60:
                x += 180 + rnd() * 120
                pts.append((x, base - 40 - rnd() * (120 - i * 40)))
            pts.append((W + 60, 720))
            shp = spline(pts, closed=True, tension=.8)
            op = 1 if self.sc.finish == "storybook" else .7 - i * .15
            self.items.append(f'<path d="{shp.d}" fill="{c}" opacity="{op}"/>')
        return self

    def sun(self, cx: float, cy: float, r: float, color: str | None = None) -> "BackPanel":
        c = color or self.sc.P.accent2
        self.glow(cx, cy, r * 3.2)
        self.items.append(f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(r)}" fill="{tint(c, .12)}"/>')
        return self

    def cloud(self, cx: float, cy: float, s: float = 1.0) -> "BackPanel":
        pts = [(-150, 0), (-140, -40), (-90, -70), (-30, -60), (10, -100), (80, -96), (120, -50), (170, -40), (176, 4), (140, 30), (-120, 30)]
        shp = spline(transform_pts(pts, dx=cx, dy=cy, s=s), closed=True, tension=.9)
        self.items.append(f'<path d="{shp.d}" fill="#ffffff" opacity=".9"/>')
        return self

    def tree(self, x: float, base_y: float, w: float, h: float, crown: str, trunk: str = "#7a5236",
             marks: str | None = None, seed: int = 1) -> "BackPanel":
        """A storybook tree: one lobed crown with drawn leaf marks on a simple trunk."""
        rnd = _rng(seed)
        self.items.append(f'<path d="M{_f(x - w * .06)} {_f(base_y)} L{_f(x - w * .05)} {_f(base_y - h * .55)} L{_f(x + w * .05)} {_f(base_y - h * .55)} L{_f(x + w * .07)} {_f(base_y)} Z" fill="{trunk}"/>')
        cy = base_y - h * .62
        pts = []
        for i in range(9):
            a = 2 * math.pi * i / 9
            k = .88 + rnd() * .24
            pts.append((x + math.cos(a) * w * .5 * k, cy + math.sin(a) * h * .38 * k))
        crown_s = spline(pts, tension=.9)
        self.items.append(f'<path d="{crown_s.d}" fill="{crown}"/>')
        self.tone(crown_s, shade(crown, .18), .34)
        self.marks(crown_s, "dash", marks or tint(crown, .35), step=w * .11, size=w * .06, angle=-40, seed=seed, inset=8)
        return self

    def render(self) -> str:
        inner = "\n".join(self.items)
        filt = "" if self.sc.finish == "storybook" else f' filter="url(#{self.sc.sid}-dof)"'
        return f'<g data-depth="{self.depth}"{filt} opacity="{self.opacity}">\n{inner}\n</g>'


__all__ = ["Scene", "Layer", "Card", "Anim", "Palette", "Light", "EVENING", "NIGHT", "Shape", "spline", "ellipse", "circle",
           "capsule", "tube", "rrect", "polygon", "teardrop", "blob", "fan", "strip", "ridge", "DUSK", "transform_pts", "mix", "tint", "shade", "HERO_BOX"]
