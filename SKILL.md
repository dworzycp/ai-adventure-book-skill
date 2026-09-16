---
name: adventure-book
description: Turn any Markdown document or story (README, onboarding guide, AGENTS.md, ADR, spec, runbook, tutorial, postmortem, fairy tale) into a self-contained interactive HTML adventure book in a chosen theme (medieval knight quest, space mission, pirate voyage, noir case, jungle expedition, deep-sea dive, or any theme the user invents) with illustrated SVG scenes, stage-by-stage navigation, a progress map, and pop-outs that reveal the real content behind each part of the tale. Use this whenever the user wants a document made into a story, quest, journey, adventure, game-like walkthrough, gamified docs, an illustrated or narrative version of a doc, a "fun" onboarding page, or any engaging way to teach a document's contents, even if they never say "adventure book".
---

# Adventure Book

You are turning a document into a journey. The reader travels stage by stage through an
illustrated tale in the user's chosen theme, and every marked word in the tale can be clicked
to see the real thing it stands for: the actual command, rule, decision, or fact from the
source document. The output is one `.html` file that works offline with no dependencies.

The engine (navigation, pop-out drawer, codex, progress map, parallax, keyboard, mobile layout,
reduced-motion) is already built in `assets/template.html`. `scripts/build_book.py` assembles
your content into it. Your job is the creative and faithful part: the allegory, the prose, the
pop-outs, and the scene art.

## Workflow

1. **Read the whole source.** Note its headings, the order things happen in, what a reader is
   supposed to be able to do afterwards, and any facts that are easy to get wrong (exact
   commands, names, numbers, rules). Those facts are what the pop-outs exist to protect.
2. **Fix the theme and the allegory.** Take the theme the user gave; if none, pick one that
   suits the material and say which you chose. Read the matching section of
   `references/themes.md` for its voice, motifs, hero archetype, and stage-naming pattern. Then
   write a short mapping table for yourself: each real concept in the source and its themed
   counterpart (VPN = the Veil, database = the great tame beast, CI pipeline = the proving
   grounds). Keep every mapping stable for the whole book. Readers learn the allegory once; if
   the Veil becomes the Mist in chapter four, the book stops teaching.
3. **Plan the stages.** Aim for 5 to 9. Each stage is one leg of the journey and usually one
   source section; merge sections that are too thin to carry a scene, split ones that would
   need more than about 250 words of narrative. Order the stages as the reader would need the
   knowledge, which is usually the document's order. Give each a title in the theme's voice and
   a `source:` heading so the reader can unroll the original section from inside the stage.
4. **Write the content files** in a working folder (`book.json`, `stages/NN-name.md`,
   `scenes/*.svg`). Formats are below.
5. **Build and read the warnings.** Fix every "no pop-out with id", "heading not found", and
   coverage warning. Rebuild until the report is clean or every remaining warning is deliberate.
6. **Verify and hand over.** Open the file (`open <file>.html` on macOS) or at least screenshot
   it with headless Chrome if available. Tell the user where the file is, how to move through it
   (arrow keys, click the map, click the glowing words), and which theme you used.

## Content formats

`book.json` (paths relative to the JSON file):

```json
{
  "title": "The Quest for the Portal",
  "subtitle": "A knight's journey through AGENTS.md",
  "theme": "knight",
  "source": "../AGENTS.md",
  "cover":  { "eyebrow": "An interactive adventure", "scene": "scenes/cover.svg", "blurb": "cover.md" },
  "stages": [ "stages/01-gates.md", "stages/02-forge.md" ],
  "ending": { "scene": "scenes/ending.svg", "blurb": "ending.md",
              "recap": [ "Cross the [[Veil|vpn]] before anything else", "Every package flies the `@internal/` banner" ] }
}
```

Each stage is a Markdown file:

```markdown
---
id: gates
title: The Gates of the Keep
chapter: Chapter I
source: Local Development Setup
scene: scenes/01-gates.svg
---
Mist clings to the road as you approach the keep. A guard bars the way: none may
enter who have not passed through [[the Veil|vpn]] ...

## popout: vpn
title: VPN
You have to be on the company VPN before anything else works, because the
internal package registry and services are only reachable from inside the network.
```

Rules the build script enforces or warns about:

- Every prose field is Markdown. Every scene is inline SVG, given as a path to a `.svg` file.
- `[[display text|id]]` marks a pop-out link; `[[docker]]` uses the text as the id. Each id needs
  a `## popout: id` block in the same stage (or a book-level `popouts` array in `book.json`).
- `source:` in the frontmatter names a heading in the source document. The script extracts
  that section verbatim and shows it behind the "original scroll" button. A pop-out block may
  also carry `source: <heading>` to attach the relevant section under its explanation.
- Theme is a preset name (`knight`, `space`, `pirate`, `noir`, `expedition`, `deepsea`) or an
  object `{ "extends": "knight", "colors": {...}, "fonts": {...}, "vocabulary": {...} }`. Presets
  live in `assets/themes.json`; copy one as the starting point for an invented theme.

Build:

```bash
python3 <skill-dir>/scripts/build_book.py --content work/book.json --out <name>.html
```

## Writing the tale

**Second person, present tense, one scene per stage.** "You" are the hero, arriving somewhere,
meeting someone, being handed something. A stage that reads like a summary with costume words
sprinkled on is the most common failure; the reader should be able to picture the place.

**120 to 250 words of narrative per stage.** Shorter feels like a caption; longer buries the
pop-outs. If the source section is long, let the pop-outs and the original scroll carry the
detail while the narrative carries the shape and the order of events.

**Mark 2 to 5 pop-outs per stage, on the words where the allegory hides something real.** The
ideal marked phrase is one the reader would otherwise nod past: "a great tame beast waits in
its box" tells them nothing until they click and learn it is PostgreSQL in Docker. Do not mark
decoration. Do not leave a stage with zero pop-outs; that stage teaches nothing.

**Make the allegory illuminate, not merely rename.** Pick counterparts that share a property
with the real thing. A backend module that "swears fealty to a greater plugin" teaches the
parent/child relationship; calling it "a purple crystal" teaches nothing. When a source concept
has structure (a table of naming conventions, a numbered setup sequence, a hierarchy), mirror
that structure in the scene: banners of different shapes, gates passed in order, a hall of
vassals.

**Let the ending pay off.** The recap lists what the hero now knows, one line per key fact,
in plain words with pop-out links where useful. The reader should finish able to do the thing
the document is for.

## Pop-outs: the contract with the reader

The tale may embellish; the pop-outs may not. A pop-out's `title` is the real name of the
thing. Its explanation is 2 to 5 sentences of plain language: what it is, why it matters here,
and the exact command, path, value, or rule from the source when there is one, in backticks or
a fenced block. Every fact in a pop-out must come from the source document or be uncontroversial
general knowledge; if the source does not say why, do not invent a why. Attach `source:` to the
pop-out when the original wording matters (commands, rules, tables).

## Scenes

Read `references/scenes.md` before drawing. In brief: one `<svg viewBox="0 0 1600 900"
preserveAspectRatio="xMidYMid slice">` per scene, built from a few layers wrapped in
`<g data-depth="0.05">` for parallax, colored with the theme's CSS variables (`style="fill:var(--land-2)"`)
so any palette works, with the subject in the left 55% because the text panel sits on the right
on wide screens. Motion is opt-in via classes on child groups (`drift`, `float`, `twinkle`,
`sway`, `pulse`, `flicker`, `spin`). Keep each scene under roughly 120 lines; suggestion beats
detail at this size.

Draw the cover, the ending, and every stage you can. A stage without a `scene:` gets a
generated themed backdrop (hills, stars, waves, or skyline depending on the theme), which looks
fine but says nothing about that stage. If you must ration effort, hand-draw the cover and the
stages whose scenes carry meaning (the hall of banners, the proving grounds), and let quiet
transitional stages use the backdrop.

## Handing over

Report the output path, the theme, the number of stages and pop-outs, and any source sections
you deliberately left out and why. Mention that the arrow keys move between stages, the map at
the bottom jumps to any stage, the glowing words open pop-outs, and the codex button lists
every pop-out in the book.
