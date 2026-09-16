# Adventure Book — a Claude Code skill

Turn any Markdown document into a self-contained interactive HTML **adventure book**.

![The cover of an adventure book: a knight on an outcrop raising sword and shield against a dragon breathing fire across a sunset valley](docs/cover.png)

<sup>The cover of a book built from this very README, in the `knight` theme.</sup>

A README, onboarding guide, AGENTS.md, ADR, spec, runbook, tutorial, postmortem — or a plain
old story — becomes a themed journey the reader travels stage by stage: illustrated SVG scenes,
a progress map, keyboard navigation, and glowing words that pop out to reveal the *real* thing
behind the allegory (the actual command, rule, decision or number from the source document).

Output is **one `.html` file** that works offline: no build step for the reader, no network
requests, no dependencies.

Built-in themes: `knight`, `space`, `pirate`, `noir`, `expedition`, `deepsea`, `storybook` — or
describe your own and Claude will extend a preset.

## Install

The skill is the repository, so installing it is a clone into your skills directory.

**Personal skill (available in every project):**

```bash
git clone https://github.com/dworzycp/ai-adventure-book-skill.git ~/.claude/skills/adventure-book
```

**Project skill (checked in, available to everyone on the repo):**

```bash
git clone https://github.com/dworzycp/ai-adventure-book-skill.git .claude/skills/adventure-book
```

The directory name matters: it must be `adventure-book`, matching the `name` in `SKILL.md`.

Restart Claude Code (or start a new session) and confirm it loaded:

```
/adventure-book
```

To update later: `git -C ~/.claude/skills/adventure-book pull`.

### Requirements

- [Claude Code](https://claude.com/claude-code)
- Python 3.9+ for the build script — standard library only, nothing to `pip install`

## Use it

Just ask, in your own words:

> Turn `docs/onboarding.md` into an interactive adventure book. Theme: a pirate voyage.
> Save it as `onboarding-voyage.html`.

Claude reads the source document, maps each real concept to a themed counterpart, writes the
stages, draws the scenes, and builds the file. Then open it in any browser.

You don't have to say "adventure book" — the skill also triggers on asks like "make this doc
fun", "gamify our runbook", or "turn this postmortem into something the team will click through".

Inside a finished book: **arrow keys** move between stages, the **map** at the bottom jumps
anywhere, **glowing words** open pop-outs, the **codex** button lists every pop-out, and the
**original scroll** button unrolls the verbatim section of the source document behind the stage.

## What's in here

| Path | What it is |
| --- | --- |
| `SKILL.md` | The skill itself: workflow, content formats, and the writing rules Claude follows |
| `assets/template.html` | The engine — navigation, pop-out drawer, codex, map, parallax, mobile and reduced-motion support |
| `assets/themes.json` | Theme presets (colors, fonts, vocabulary) |
| `scripts/build_book.py` | Assembles `book.json` + stage Markdown + SVG scenes into the final HTML |
| `references/themes.md` | Voice, motifs and stage-naming patterns per theme |
| `references/scenes.md` | How to draw the SVG scenes so they work with the parallax and palette |
| `evals/` | Eval suite for [skill-creator](https://github.com/anthropics/skills), plus sample source docs |

## Building a book by hand

You don't need Claude to run the builder. Create a working folder:

```
work/
  book.json
  stages/01-gates.md
  scenes/01-gates.svg
```

`book.json` (paths relative to the JSON file):

```json
{
  "title": "The Quest for the Portal",
  "subtitle": "A knight's journey through AGENTS.md",
  "theme": "knight",
  "source": "../AGENTS.md",
  "cover":  { "eyebrow": "An interactive adventure", "scene": "scenes/cover.svg", "blurb": "cover.md" },
  "stages": [ "stages/01-gates.md" ],
  "ending": { "scene": "scenes/ending.svg", "blurb": "ending.md",
              "recap": [ "Cross the [[Veil|vpn]] before anything else" ] }
}
```

A stage is a Markdown file with frontmatter and its pop-outs inline:

```markdown
---
id: gates
title: The Gates of the Keep
chapter: Chapter I
source: Local Development Setup
scene: scenes/01-gates.svg
---
Mist clings to the road as you approach the keep. A guard bars the way: none may
enter who have not passed through [[the Veil|vpn]]...

## popout: vpn
title: VPN
You have to be on the company VPN before anything else works — the internal package
registry is only reachable from inside the network.
```

Then build:

```bash
python3 scripts/build_book.py --content work/book.json --out quest.html
```

The builder warns about pop-out ids with no matching block, `source:` headings it can't find in
the document, stages that are too thin, and source sections nothing in the book refers to.

## License

MIT — see [LICENSE](LICENSE).
