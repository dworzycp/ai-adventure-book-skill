# Drawing scenes

Every scene is one inline SVG that fills the viewport behind the text panel. The engine adds
parallax to any group with `data-depth`, animates a handful of opt-in classes, and darkens the
edges with a vignette, so a scene made of six or seven flat layers already looks rich. Aim for
"illustrated storybook", not "technical diagram": flat shapes, a limited palette, a clear focal
subject, atmosphere from gradients and layering.

## The frame

```svg
<svg viewBox="0 0 1600 900" preserveAspectRatio="xMidYMid slice"
     xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <defs>
    <linearGradient id="sky-gates" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" style="stop-color:var(--sky-1)"/>
      <stop offset="1" style="stop-color:var(--sky-2)"/>
    </linearGradient>
  </defs>
  <rect width="1600" height="900" fill="url(#sky-gates)"/>
  <!-- layers, far to near -->
</svg>
```

- **`viewBox="0 0 1600 900"` with `slice`** means the image always covers the screen; edges
  may be cropped on tall or wide windows. Keep anything important inside roughly
  `x 100..1500, y 80..820`.
- **The text panel sits in the right ~40% on wide screens.** Put the focal subject in the
  left 55% (`x < 880`). Foreground silhouettes may run the full width.
- **Give gradient and pattern ids a per-scene suffix** (`sky-gates`, `sky-forge`). All scenes
  live in one HTML document, so duplicate ids bleed between scenes.
- **Colour with the theme variables** so the palette stays coherent and a re-themed book
  still works: `style="fill:var(--land-2)"`. Available: `--sky-1 --sky-2` (top/bottom of sky),
  `--land-1 --land-2 --land-3` (far, mid, near ground; near is darkest), `--water`, `--accent`
  (the theme's warm highlight: fire, flags, a red door), `--accent-2` (gold/glow: sun, lanterns,
  stars, treasure), `--paper` (moon, light, sails, snow), `--ink` and `--bg` (deep darks).
  Literal colours are fine for small accents (`#fff` stars, a skin tone), not for large areas.

## Layers and depth

Wrap each distance band in a group with a depth from 0.02 (far) to 0.16 (near). The engine
translates each group with the mouse by an amount proportional to its depth, which reads as
parallax.

```svg
<g data-depth="0.02"> <!-- sky objects: sun, moon, stars, distant clouds --> </g>
<g data-depth="0.05"> <!-- far ridge, distant castle, horizon --> </g>
<g data-depth="0.09"> <!-- mid ground: the subject usually lives here --> </g>
<g data-depth="0.14"> <!-- foreground: dark silhouettes framing the edges --> </g>
```

Put motion classes on a **child** group, not on the `data-depth` group itself, because the
parallax sets `transform` inline and a CSS animation on the same element would override it:

```svg
<g data-depth="0.03">
  <g class="drift slow"><ellipse cx="400" cy="200" rx="160" ry="34" fill="#fff" opacity=".4"/></g>
</g>
```

Motion classes: `drift` (slow horizontal, clouds and waves), `float` (gentle bob, boats and
airships), `twinkle` (opacity pulse, stars and embers), `sway` (rotate about the base, trees
and flags), `pulse` (scale and glow, suns and lanterns), `flicker` (torches, neon), `spin`
(gears, planets' rings). Modifiers: `slow`, `fast`, `delay-1/2/3` to de-synchronise siblings.
Two or three moving things per scene is plenty; everything moving is worse than nothing moving.

## Recipes

**Ridge / hills.** A closed path along the bottom with 8 to 14 points. Three ridges at
increasing depth and darkening colour make a landscape.

```svg
<g data-depth="0.05"><path d="M0 620 L180 540 L360 600 L520 500 L760 590 L980 520 L1200 600 L1400 540 L1600 590 V900 H0 Z" style="fill:var(--land-1)"/></g>
```

**Castle / keep.** Rectangles for walls, narrower taller rectangles for towers, a row of small
squares for crenellations, triangles for roofs, a tiny `--accent` rectangle for a banner and a
`--accent-2` arch for a lit gate.

**Ship.** A wide shallow hull path (`M x y q ...` curve along the bottom), one or two masts
(thin rects), sails as slightly bulged paths in `--paper`, a flag in `--accent`. Wrap in
`class="float"`. Waves as repeated `q 50 -18 100 0` paths at different depths with `drift`.

**Rocket / ship (space).** A capsule path, fins as triangles, a `--accent-2` engine glow
circle with `pulse`. Starfield: 80 to 150 small white circles with `twinkle` and varied
`animation-duration` via inline style. A planet: big circle in `--land-1` with a thinner
ellipse ring in `--paper` at low opacity, optionally `spin slow`.

**City (noir).** Rows of rectangles with `--land-1/2/3`, a few 2×3 `--accent-2` windows at
low opacity, a `--paper` moon with `flicker`, rain as a `<pattern>` of thin diagonal lines at
opacity .15 over the whole frame.

**Trees.** Trunk rect plus two or three overlapping ellipses or triangles; wrap the crown in
`class="sway"` with `transform-box: fill-box` handled by the engine.

**Torch / lantern / fire.** A `--accent-2` circle with `pulse fast` over a slightly larger
`--accent` circle at opacity .3.

**People.** Silhouettes only: a circle head over a rounded-rect body, arms as thick lines.
Two or three at most, small, mid ground, as scale reference for the architecture.

**Light and atmosphere.** A large radial gradient ellipse in `--accent-2` at opacity .15 to
.3 behind the subject sells "glow" cheaply. Fog is a wide `--paper` ellipse at opacity .12.

## Budget

A good scene is 40 to 120 lines. Past that, detail turns to noise at this scale and the HTML
file grows fast. Cover and ending scenes may be richer than stage scenes. If short on effort,
draw the cover and the two or three stages whose scene carries meaning, and omit `scene:` on
transitional stages so the engine draws a themed backdrop.

## Checklist before building

- `viewBox="0 0 1600 900"` and `preserveAspectRatio="xMidYMid slice"` present.
- Gradient/pattern ids unique per scene.
- Focal subject left of centre; nothing essential in the outer 6% on any side.
- Colours via `var(--...)` except small accents.
- At most three animated elements; motion classes on children of `data-depth` groups.
- No `<script>`, no external `href`, no `<image>` pointing at a URL (the book must work offline).
