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
your content into it. Your job is the creative and faithful part: the story, the allegory, the
prose, the pop-outs, and the scene art.

Three references carry the craft: `references/story.md` (structure — read it every time),
`references/themes.md` (voice and allegory per theme), and `references/scenes.md` (drawing).

The two failures to design against are **too many words** and **no story underneath them**: a
book that renames the document's sections in costume, stage after stage, and buries the real
facts in atmosphere. Fewer words, one clear journey.

## Workflow

0. **Ask before assuming.** Two things must come from the user, and if either is missing, stop
   and ask for it before doing anything else — do not pick a plausible file or a theme yourself:
   - **the source document** (a Markdown file path, or pasted Markdown). If the request names
     no file, ask which document to turn into a book; if several candidates exist, list them
     and let the user choose.
   - **the theme** (`knight`, `space`, `pirate`, `noir`, `expedition`, `deepsea`, `storybook`, or
     one the user invents), plus who the reader is (a child, a new team member, …), since that
     decides the register of the art and the prose.
   Ask both in one message. Only once both are known does the work below start.
1. **Read the whole source.** Note its headings, the order things happen in, what a reader is
   supposed to be able to do afterwards, and any facts that are easy to get wrong (exact
   commands, names, numbers, rules). Those facts are what the pop-outs exist to protect.
2. **Fix the theme and the allegory.** Use the theme the user gave in step 0 (never a default).
   Read the matching section of
   `references/themes.md` for its voice, motifs, hero archetype, and stage-naming pattern. Then
   write a short mapping table for yourself: each real concept in the source and its themed
   counterpart (VPN = the Veil, database = the great tame beast, CI pipeline = the proving
   grounds). Keep every mapping stable for the whole book. Readers learn the allegory once; if
   the Veil becomes the Mist in chapter four, the book stops teaching.
3. **Shape the story.** Read `references/story.md` and do its five steps, in order, on paper
   before planning anything: (1) the document's **one argument** as an And-But-Therefore with
   exactly one *but*; (2) **one protagonist who owns the problem** — wants something concrete
   on page one, has something real to lose that the document names, decides and acts; (3) the
   **story shape chosen from the document's type** (a decision doc is *the choice*, a runbook
   *the watch*, a postmortem *the retelling*, a README *the apprenticeship*…); (4) the **fact
   ledger** — every heading, number, command and warning assigned a home: narrative, pop-out,
   recap, scenery, or declared omission; (5) the **spine**, ending first, then five to nine
   beats joined by *therefore* or *but*. A document is a list of sections; a book is a chain of
   consequences, and turning one into the other is the whole job. Do not skip this because the
   source looks like a simple list — those are the ones that come out as tours.
4. **Plan the stages.** Aim for 5 to 9, one beat each, mapped onto the spine (one stage of
   arrival, three to six of escalating middle, one where it goes wrong, one of payoff). Each
   stage is usually one source section: merge sections too thin to carry a beat, and split ones
   that would need more than about 120 words of narrative. Order the stages as the reader would
   need the knowledge, which is usually the document's order. Give each a title in the theme's
   voice and a `source:` heading so the reader can unroll the original section from inside the
   stage.
5. **Write the content files** in a working folder (`book.json`, `stages/NN-name.md`) and a
   scene script (`draw.py`) that uses `scripts/scene_engine.py` to render `scenes/*.svg`. Run it
   and fix every hero-box warning it prints. Formats are below; the engine is in
   `references/scenes.md`.
6. **Cut, then run the checklist.** Reread each stage against "Writing the tale" and take out
   roughly a third of the words; first drafts are almost always twice as long as they need to
   be, and every sentence you delete makes the marked words easier to see. Then walk the
   checklist at the end of `references/story.md` and fix what fails. Both of these happen before
   you build; neither is optional polish.
7. **Build and read the warnings.** Fix every "no pop-out with id", "heading not found", and
   coverage warning. Rebuild until the report is clean or every remaining warning is deliberate.
8. **Verify and hand over.** Open the file (`open <file>.html` on macOS) or at least screenshot
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
Mist clung to the road as Edda came up to the keep. A guard barred the way: none
might enter who had not passed through [[the Veil|vpn]] ...

## note
The repository is private, so everything runs behind the company VPN. Connect
before anything else: the internal package registry is only reachable from inside.

## popout: vpn
title: VPN
You have to be on the company VPN before anything else works, because the
internal package registry and services are only reachable from inside the network.
```

Rules the build script enforces or warns about:

- Every prose field is Markdown. Every scene is inline SVG, given as a path to a `.svg` file.
- **Every stage carries a `## note` — the technical bit.** It sits under the tale in plain
  voice, with no allegory at all, and states what the stage's section of the document actually
  says: the numbers, the names, the commands, the rule. The tale is how the reader remembers it;
  the note is how they check it. A stage without one is an allegory the reader cannot cash in,
  and the build script warns about it. Two or three sentences, bold the figures that matter,
  and quote commands verbatim.
- `[[display text|id]]` marks a pop-out link; `[[docker]]` uses the text as the id. Each id needs
  a `## popout: id` block in the same stage (or a book-level `popouts` array in `book.json`).
- `source:` in the frontmatter names a heading in the source document. The script extracts
  that section verbatim and shows it behind the "original scroll" button. A pop-out block may
  also carry `source: <heading>` to attach the relevant section under its explanation — but it
  must sit in the pop-out's header lines, directly under `## popout: id` alongside `title:`, not
  after the explanation. Misplaced, it is silently read as prose and the section goes uncovered.
- Theme is a preset name (`knight`, `space`, `pirate`, `noir`, `expedition`, `deepsea`) or an
  object `{ "extends": "knight", "colors": {...}, "fonts": {...}, "vocabulary": {...} }`. Presets
  live in `assets/themes.json`; copy one as the starting point for an invented theme.

Build:

```bash
python3 <skill-dir>/scripts/build_book.py --content work/book.json --out <name>.html
```

## Writing the tale

**One named protagonist, in third person, past tense — never "you".** The hero has a name on
the first page and keeps it to the recap; the narration follows them the way every fairy-tale
pop-up follows Red Riding Hood. Second person belongs only inside quotation marks, where one
character speaks to another. Write *about* the hero, never *at* the reader — on the cover and in
the ending too. `references/story.md` explains why, and the build script warns when narration
outside dialogue says "you". A stage is not a
description of a place; it is something happening in one. The hero arrives, meets a person or a
problem, *does one thing with what they learn*, and leaves with different options than they
came with. If a stage boils down to "the hero is somewhere and someone explains a section", it
is a tour stop, not a beat: find the beat in the source — the thing that must be done, the
mistake that must not be made, the decision that was taken — and build the scene around the
hero doing it.

**Hold the shape you planned.** `references/story.md` is the authority on structure: the
document's one argument stated up front as the hero's want and stake, stages joined by
"therefore" and "but" rather than "and then", mentors who ask questions or set constraints
while the hero acts, the middle escalating, a real mistake from the source near the end, a
refrain or carried object, the ending the hero earns alone, and every stage's last sentence
pulling toward the next. Seven unrelated vignettes in matching costumes is a
slideshow, not a book, and it is the failure this skill falls into by default.

**60 to 120 words of narrative per stage, and that is a budget rather than a target.** Two
short paragraphs. The reader came for the document, not the prose; past about 120 words they
start skimming, and a skimmed stage teaches nothing. Long source sections do not earn more
words — they earn more pop-outs and the original scroll, which is exactly what those are for.

**Cut every sentence that is only mood.** Allow yourself one atmospheric image per stage; make
the rest of the sentences carry a fact, a movement, or a consequence. The usual things to
delete: a second adjective, a sentence that restates the previous one in themed words, a clause
about how the light falls, and any preamble before the hero actually does something.

**The tale must be legible without clicking.** Assume a reader who never opens a single
pop-out: they should still be able to say what happened and roughly what it means. The marked
phrase names the thing in theme; the sentence around it carries the real meaning.

> "The elder spoke the word of binding over the blade." — teaches nothing; the reader cannot
> tell whether this is a config file, a login, or scenery.
> "Nothing Edda forged would hold until the elder wrote her name in [[the ledger|env-file]]." —
> same costume, but the reader now knows there is a file that must list them before anything
> works. The pop-out then supplies the name of the file and the exact line.

**Mark 2 to 4 pop-outs per stage, on the words where the allegory hides something real.** Mark
the phrase a reader would otherwise nod past, never decoration. A stage with zero pop-outs
teaches nothing; a stage with seven is a glossary with a costume.

**Make the allegory illuminate, not merely rename.** Pick counterparts that share a property
with the real thing. A backend module that "swears fealty to a greater plugin" teaches the
parent/child relationship; calling it "a purple crystal" teaches nothing. When a source concept
has structure (a table of naming conventions, a numbered setup sequence, a hierarchy), mirror
that structure in the scene: banners of different shapes, gates passed in order, a hall of
vassals.

**Let the ending pay off the through-line.** The recap is the hero's new competence in plain
words: one line per key fact, under a dozen words each, with pop-out links where useful. The
reader should finish able to do the thing the document is for.

## Pop-outs: the contract with the reader

The tale may embellish; the pop-outs may not. A pop-out's `title` is the real name of the
thing, and its first sentence states plainly what it is — no story voice, no throat-clearing,
never a second helping of allegory. Then 1 to 3 more sentences at most: why it matters here,
and the exact command, path, value, or rule from the source when there is one, in backticks or
a fenced block. Quote commands verbatim; never paraphrase one. Every fact must come from the
source document or be uncontroversial general knowledge; if the source does not say why, do not
invent a why. Attach `source:` to the pop-out when the original wording matters (commands,
rules, tables) rather than retyping it.

## Scenes

**Every stage is an open pop-up book spread**, in the style of the Robert Frederick fairy-tale
pop-up books: flat, matte storybook illustration printed on die-cut card, standing in layered
rows on the page, each flat with a thin white edge around its whole silhouette and a soft shadow
onto what is behind it. The engine draws the book; your `draw.py` (using
`scripts/scene_engine.py`) describes the flats. Read `references/scenes.md` first — it is the
engine's manual and describes the look precisely.

The rules that decide whether a spread looks like those books:

- **One hero on its own card**, half to two thirds of the leaf, with a bush row behind and a
  bush row in front. Supporting context small on a far layer.
- **Flat colour with a darker lower band, and drawn texture marks** — leaf dashes, grass ticks,
  stone blocks, scale arcs. No gradients, glow or shading on characters.
- **Simple, appealing characters**: rounded, 6–10 shapes, dot eyes with a white, a rosy cheek,
  a small mouth. Villains are sly, not scary. Minimal, but unmistakably the thing.
- **A real setting made of a few big shapes** on the back panel — trees, hills, a wall, curtains.
- **One colour family per spread plus one warm accent.**

Never fold a character; never put an outline on a piece inside a card; never animate a lit
piece. Look at the render before handing over.

Draw the cover, the ending, and every stage you can. A stage without a `scene:` gets a generated
backdrop in the same style — it simply has no hero.

## Handing over

Report the output path, the theme, the number of stages and pop-outs, and any source sections
you deliberately left out and why. Mention that the arrow keys move between stages, the map at
the bottom jumps to any stage, the glowing words open pop-outs, and the codex button lists
every pop-out in the book.
