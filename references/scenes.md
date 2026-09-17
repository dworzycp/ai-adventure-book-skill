# Drawing scenes

Every stage is **an open pop-up book spread**. The engine draws the book — two leaves, the
gutter, the stacked fore-edges, the table it lies on. You draw what stands on the left leaf.
The words are printed on the right leaf.

## The look

The reference is the **Robert Frederick "Fairy Tale Pop-Up" books** (Cinderella, Red Riding
Hood, Goldilocks): flat, matte storybook illustration printed on die-cut card. Study one before
drawing. What they do, every spread:

- **Standing flats, layered.** A fully illustrated back panel; two or three rows of die-cut
  flats standing on the page (a bush row, the characters, a bush row in front); the flat page
  with the words. Every flat has a **thin white edge around its whole silhouette** and throws a
  short, soft shadow straight down onto what is behind it.
- **Flat colour, two tones.** Each shape is one flat colour with a darker band on its lower
  third (`tone`). No gradients, no gloss, no modelling.
- **Drawn texture marks.** Tree crowns get leaf dashes; grass gets upright ticks; walls get
  stone blocks; scales are little arcs (`marks`). Marks are what make flat shapes read as
  printed illustration rather than clip art.
- **One colour family per spread plus one warm accent** — greens with a red cloak, blues with a
  gold crown. Pull every colour from that family.
- **Simple, appealing characters.** Rounded silhouettes of 6–10 shapes, a roundish head,
  **dot eyes with a white** (`dot_eye`), a **rosy cheek** (`cheek`), a small mouth. Villains are
  sly rather than scary — the wolf smirks and shows small teeth. Minimal, but unmistakably a
  horse, a dragon, a captain.
- **A real setting, made of big shapes.** Trees, a wall, hills, curtains — 3 to 6 large shapes
  with marks. Rich, but nothing small or fussy.

## The engine in one page

```python
import sys; sys.path.insert(0, "<skill-dir>/scripts")
from scene_engine import *

P  = Palette.load("storybook")
sc = Scene("gate", P)                                    # finish="storybook" is the default

bp = sc.back_panel(sky=("#bfe3ee", "#eaf3d6"))            # 1. the illustrated back panel
bp.sun(300, 170, 60, color="#fff3c4").hills(colors=["#a9d468", "#6fb857"])
bp.tree(150, 660, 300, 520, "#4d9a5a").tree(560, 640, 340, 580, "#3d8a4e")

sc.base_page(shadow=None, path=True, flowers=True, color="#b9dc6e")   # 2. the page

g = sc.hero()
with g.card(base_y=700) as c:                              # 3. a bush flat behind the hero
    bush(c, 90, 700, 300, 150, "#3f8f4a", flowers="#f0eaa0")
with g.card(base_y=762) as c:                              # 4. the hero on its own card
    body = spline([...], tension=.95)
    c.piece(body, "#d94b35"); c.tone(body, "#a83324", .3)   # flat colour + a darker lower band
    c.marks(body, "scale", "#8a2716", step=30, size=26)     # printed texture
    c.dot_eye(288, 338, 16, look=(-4, 2)); c.cheek(250, 378, 18)
with g.card(base_y=790) as c:                              # 5. a bush + a small figure in front
    bush(c, 540, 790, 220, 120, "#2c6e3c")

sc.write("scenes/01-gate.svg")
```

Run the script, then build. `Scene.write` warns if a hero piece leaves the box
`x 120..760, y 130..800` — heed it, except for the front bush row which may run to the edge.

### Cards

A `card` is one die-cut flat standing on the page. Everything drawn inside it gets **one**
white edge around the whole silhouette and one soft shadow onto the page.

| | |
|---|---|
| `g.card(base_y=…)` | where the card meets the page. Back row ≈ 690–710, hero ≈ 760–790, front row ≈ 800–815 |
| pieces inside a card | have no edge of their own — build a character from overlapping shapes freely |
| `crease_x=…, fold=True` | a gentle V-fold — **only** for symmetric buildings (a barn, a gate). Never through a character |
| `layer.mirror = True` | flip a layer so a subject faces left; put the sun on the other side |

Draw order inside a card is paint order: far limbs, tail, body, near limbs, head, features.

### Shapes

| call | draws |
|---|---|
| `spline(pts, tension)` | a smooth closed curve through 8–14 points — bodies, heads, coats, wings, bushes |
| `blob(cx, cy, rx, ry, wobble, seed)` | an organically uneven ellipse — heads, rocks |
| `tube(pts, r0, r1)` | one tapered tube along a curve — tails, necks, arms |
| `teardrop(cx, cy, r, length, angle)` | horns, spikes, ears, leaves, plumes. `-90` = up |
| `rrect`, `circle`, `ellipse`, `polygon` | walls, wheels, roofs, legs |

### Storybook helpers

| call | does |
|---|---|
| `piece(shape, color)` | a flat printed shape |
| `tone(shape, color, frac=.38, side="bottom")` | the second tone: a darker band on the lower third |
| `marks(shape, kind, color, step, size, angle)` | drawn texture: `dash` (leaves), `grass`, `dot`, `scale`, `plank`, `stone` |
| `dot_eye(cx, cy, r, look, lid)` | white, dark dot, pin of light. r 9–16 on a hero |
| `cheek(cx, cy, r)` | rosy cheek |
| `smile(cx, cy, w, depth, color, width, teeth=0)` | a mouth line; small |
| `claws(...)`, `line(...)`, `glow(...)` | as before |
| `bp.tree(x, base_y, w, h, crown)` | a lobed crown with leaf dashes on a simple trunk |
| `animate(kind, origin, amount)` | subtle motion on flat pieces: `sway`, `flap`, `flicker`, `pulse`, `spin` |

## Composition

One hero on its own card, filling half to two thirds of the leaf's height. A bush row behind,
a bush row in front, a small figure or prop for scale. Supporting context (the other barns,
distant keepers) on a far layer at ~0.25 scale. The back panel is a real place but made of a
few big shapes. Nothing else.

## What breaks the look

- **Gradients, glow, sheen on characters.** They are printed card. `finish="gloss"` and
  `finish="matte"` exist but are not this book.
- **Per-piece white outlines.** A card is cut once. If you see a white line inside a figure,
  something is outside its card.
- **Folds through characters.** They distort; only symmetric buildings fold.
- **Realistic anatomy.** A tiny eye on a long wedge of a head is a field guide, not a
  storybook. Round it, give it a dot eye and a cheek.
- **Fussy detail.** Six big shapes with marks beat sixty small ones.
- **Filters that move.** `animate()` forces its contents flat; never animate a lit piece or a
  group inside a filtered SVG — that is what made page turns sluggish.

## Checklist before building

- No hero-box warnings (front bushes excepted).
- Exactly one hero card, half to two thirds of the leaf; a row behind and a row in front.
- Every character: dot eyes, a cheek, a small mouth; 6–10 shapes; recognisable at a glance.
- Every large shape: flat colour, a `tone` band, and `marks` where the books would draw them.
- One colour family plus one accent.
- Back panel: sky, sun, hills, 2–3 trees or one building. Big shapes only.
- No gradients or lighting on characters; no white lines inside a figure.
- Unique `sid` per scene; no `<script>`, no external `href`.
