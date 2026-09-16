# Story structure

Read this before writing any prose. It is the difference between a book and a slideshow of
costumed summaries. Everything here comes from how picture books and early chapter books are
built, because they solve exactly our problem: teach something real, to someone who did not ask
to be taught, in very few words, with a picture on every page.

## Contents

- [The objective](#the-objective)
- [The spine](#the-spine)
- [Therefore and but, never and then](#therefore-and-but-never-and-then)
- [Mapping the spine onto stages](#mapping-the-spine-onto-stages)
- [The middle: escalation and the rule of three](#the-middle-escalation-and-the-rule-of-three)
- [The low point](#the-low-point)
- [Repetition with variation](#repetition-with-variation)
- [The page turn](#the-page-turn)
- [Objects, not abstractions](#objects-not-abstractions)
- [A small, named cast](#a-small-named-cast)
- [The ending answers the beginning](#the-ending-answers-the-beginning)
- [Sentence craft](#sentence-craft)
- [Checklist](#checklist)

---

## The objective

Every good children's book states a want in its first few lines, and the want is concrete.
Max wants to be where the wild things are. The pigeon wants to drive the bus. The caterpillar
is hungry. Not one of them wants "to learn about" anything.

So before writing a word, finish this sentence: **by the end, you must be able to ___, or ___
happens.** The blank is whatever the source document is actually for — ship a change, stand a
watch alone, keep the checkout flow up, find your way around the valley. The second blank is
what the document is warning you about, and the source almost always says it: the build breaks,
the ship runs aground, the outage repeats.

Put that objective in three places: the cover blurb, the first stage (the hero is told what
they must be able to do), and the ending (they can do it). If you cannot fill in the blanks
from the source, you have not understood the source yet — go back and reread it.

Never invent peril the document does not have. A style guide's stake is "the next person
cannot read your code", not a dragon. Real stakes, themed. Fake stakes read as childish; real
stakes read as a story.

## The spine

Kenn Adams' story spine, the one Pixar's story team is known for using, is the most useful tool
here because it is a fill-in-the-blanks form:

> Once upon a time ___. Every day ___. But one day ___. Because of that ___. Because of that
> ___. Because of that ___. Until finally ___. And ever since then ___.

Fill it in for the book before planning stages. A git guide becomes: *Once upon a time you
signed on to a ship whose log every hand must keep. Every day the crew writes each change into
the log. But one day you are given your own heading to sail. Because of that you must learn to
write a legible entry. Because of that you must bring your heading back into the main channel.
Because of that you must learn to undo a bad entry without sinking the ship. Until finally your
heading is merged and the log still reads true. And ever since then you sail your own watches.*

That paragraph is the whole book, and it took thirty seconds. Now each "because of that" is a
stage, and you already know they connect.

## Therefore and but, never and then

Trey Parker and Matt Stone's rule: if you can put "and then" between your beats, you have a
list. Beats should be joined by "therefore" or "but".

- **And then** (a list): *You visit the forge. And then you visit the stables. And then you
  visit the scriptorium.*
- **Therefore / but** (a story): *The blade is unproven, therefore you carry it to the proving
  grounds. It breaks on the first strike, but the smith shows you the flaw was in the forging,
  therefore you go back to the forge knowing what to look for.*

Documentation is written as a list of sections, so the default output of this skill is a list.
Resisting that is most of the work. Write the connective word between each pair of stages
explicitly while planning; if the only honest word is "and then", either merge the two stages
or find the causal link the document implies but never states.

## Mapping the spine onto stages

For a 5-to-9-stage book:

**Beginning — one stage.** The ordinary world, the hero's arrival, and the objective stated out
loud by someone who has authority to state it (the first mate, the veteran, the chief). End it
by crossing a threshold: a gate, a hatch, a signed article. Setup sections (install, access,
prerequisites) are naturally this stage — the threshold *is* the setup.

**Middle — three to six stages.** One capability per stage, each caused by the last, each
harder than the last. This is where the body of the document lives. The hero is acquiring
things: a tool, a rule, a name, a habit.

**The turn — one stage near the end.** Something goes wrong. See below.

**End — one stage plus the ending screen.** The hero uses what they gathered, unaided, and the
objective from stage one is met. The recap is not a summary of the book; it is the list of
things the hero can now do.

## The middle: escalation and the rule of three

Children's books count in threes and escalate: three encounters, each worse or stranger than
the last. The Gruffalo's mouse meets fox, owl and snake, and each time the threat is the same
shape but bigger, until the invented monster turns out to be real.

Apply it literally. Order the middle stages so each one costs the hero more than the one
before: the first command is typed for you, the second you type yourself, the third you must
choose between two and pick right. If your source has a genuinely flat list of peers (seven
naming conventions, six action items), do not spread them across seven stages — put them in
one stage as one scene, a hall of banners or a wall of case files, and let the pop-outs carry
the detail. Flat lists are scenery; they are not plot.

## The low point

Somewhere in the last third, the hero gets it wrong. This is the single most reliable way to
make a technical book memorable, and every document hands you the material: the "common
mistakes" section, the "do not do this" rule, the incident's root cause, the deprecated
approach, the footgun with the scary warning box.

Stage it as a real failure with a real consequence — the force-push that overwrites a
shipmate's work, the env var read as `NaN`, the migration run against the wrong beast — then
let the mentor show the fix. The reader remembers the rule because they watched it break.
A book where nothing goes wrong teaches nothing, because the reader never learns which mistakes
the document was written to prevent.

## Repetition with variation

Picture books repeat a structure and change one thing inside it. *We're Going on a Bear Hunt*
runs the same refrain through every obstacle; *Green Eggs and Ham* asks the same question in
new places. Repetition is how a short book feels cumulative instead of scattered.

Two ways to use it:

- **A refrain.** One short line that recurs, lightly varied, at the same moment in each stage —
  usually the moment the hero is about to act. "You check the log before you cut the rope."
- **A carried object.** The hero's satchel, belt, manifest, or case file gains one item per
  stage, and the narrative names what went in. By the last stage the reader has watched the
  document's toolkit assemble itself, which is the thing the document wanted them to have.
  The ending scene should show it full.

Do not over-run it. A refrain used in every single stage becomes wallpaper; three or four
placements is plenty.

## The page turn

In a picture book, the page turn is the suspense mechanism: the last line of a spread makes you
turn it. Our page turn is the "next" button, and it is wasted almost every time.

End each stage on a pull forward: a question the hero is left with, a door opening, a name
dropped that is not explained until the next stage, an instruction they have not yet obeyed.
Never end a stage on a summary of the stage. The last sentence is the most valuable sentence
you have — spend it on the next stage, not on the one the reader just read.

## Objects, not abstractions

Children's writers turn ideas into things that can be held, because a thing can be picked up,
handed over, lost, and carried. Abstractions cannot be drawn, and if it cannot be drawn, the
scene has nothing to show.

Give every important concept a physical object or a place with a door: the environment file is
a ledger the elder writes your name in; the test suite is an anvil the blade is struck against;
the staging area is the bench where you lay out what goes in the crate before you nail it shut.
Then the verbs come free — you carry it, open it, hand it over, drop it — and each one of those
verbs is a beat.

The test: if a stage's central image cannot be drawn as an SVG scene, the allegory is still
abstract. Fix it before you draw.

## A small, named cast

Three recurring characters at most, each with one trait, each named, each present in more than
one stage. A mentor who knows the rules, a peer who gets things wrong so the hero does not have
to, and one voice of authority. Reusing them is what makes stage six feel like the same book as
stage two; a fresh nameless guide in every stage is the "vignettes in costumes" failure wearing
a different hat.

Give the mentor a verbal tic or a single repeated gesture rather than a description. It costs
four words and does more than a paragraph of appearance.

## The ending answers the beginning

The strongest picture-book endings return to the opening image, changed. Max sails home and his
supper is still hot. Return to the place, object, or phrase from stage one and show what is
different now: the gate the hero could not pass is the gate they now stand watch at; the empty
satchel is full; the question the chief asked in scene one gets its answer.

Then the recap, which is the only part of the book written in plain voice: one line per thing
the hero can now do, under a dozen words each, pop-out links where a name or command matters.

## Sentence craft

Children's prose is short because it is read aloud. Read every stage aloud in your head; where
you run out of breath, put a full stop.

- Strong verbs, concrete nouns, few adjectives. Never two adjectives on one noun.
- Vary sentence length deliberately. Three short sentences, then a longer one, lands; four
  long ones in a row is soup.
- One image per sentence. Two metaphors in one sentence cancel out.
- Cut "suddenly", "somehow", "seems to", "begins to", "you find yourself". They are padding.
- Prefer the specific: not "a great beast", but "a beast the size of the stable door".
- No throat-clearing. Start the stage in the middle of the action, not with the weather.

## Checklist

Before building, check each is true:

- [ ] The objective is stated on the cover, in stage one, and met at the end.
- [ ] Every pair of adjacent stages is joined by "therefore" or "but", not "and then".
- [ ] The middle escalates: the last middle stage asks more of the hero than the first.
- [ ] Something goes wrong before the end, and it is a real mistake from the source.
- [ ] A refrain or a carried object recurs in at least three stages.
- [ ] Every stage's last sentence pulls toward the next one.
- [ ] The same named cast appears throughout.
- [ ] The ending returns to the opening image, changed.
- [ ] Every stage is 60 to 120 words, and reads cleanly aloud.
