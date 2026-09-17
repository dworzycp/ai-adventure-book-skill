# Story structure

Read this before writing any prose. It is the difference between a book and a tour: a
costumed guide walking the reader past the document's sections, one per page, each with a
speech. A tour is what this skill produces by default, because documentation is a list and a
list wants to stay a list. Everything here is about turning that list into one short story
that a reader would follow even if they did not need the information — and that still
delivers every fact the document holds.

The craft comes from four traditions that solve our exact problem: picture books (teach in
very few words, read aloud, a picture on every page), fables (a lesson that arises from what
happens, never from a speech), the business novel (*The Goal*, *The Phoenix Project*: real
technical content taught through a protagonist's struggle and a mentor who only asks
questions), and narrative science communication (Randy Olson's *And, But, Therefore*).

## Contents

- [What a story is, and what a tour is](#what-a-story-is-and-what-a-tour-is)
- [Step one: the document's one argument](#step-one-the-documents-one-argument)
- [Step two: one protagonist who owns the problem](#step-two-one-protagonist-who-owns-the-problem)
- [Step three: the shape, chosen by document type](#step-three-the-shape-chosen-by-document-type)
- [Step four: the fact ledger](#step-four-the-fact-ledger)
- [Step five: the spine, then the beats](#step-five-the-spine-then-the-beats)
- [Mentors ask; the hero acts](#mentors-ask-the-hero-acts)
- [The turn: the moral arrives as a consequence](#the-turn-the-moral-arrives-as-a-consequence)
- [Allegory that teaches](#allegory-that-teaches)
- [Voice and point of view](#voice-and-point-of-view)
- [A spread, sentence by sentence](#a-spread-sentence-by-sentence)
- [Economy](#economy)
- [A worked example: the same document, as a tour and as a story](#a-worked-example)
- [Checklist](#checklist)

---

## What a story is, and what a tour is

A **tour**: the hero arrives somewhere. A wise person explains a section of the document. The
hero nods and moves on. Repeat five times. Recap.

A **story**: someone wants something concrete and cannot yet have it. Each scene changes what
they know or what they can do, and each change *causes* the next scene. Near the end they get
it wrong in the way the document warns about. Then they act, alone, and get the thing — and
the reader can now do it too.

The test is mechanical. Write the beats as one-line summaries and read the words between them.
If the honest connective is **and then**, it is a tour. If it is **therefore** or **but**, it
is a story (Trey Parker and Matt Stone's rule; Randy Olson calls the same thing *AAA* —
and-and-and — the shape of a boring narrative). A document with five sections usually contains
one real causal chain and four pieces of scenery. Find the chain; make the scenery scenery.

## Step one: the document's one argument

Before the protagonist, before the theme: **what is this document's one sentence?** Every
useful document argues something, even a reference page — "do X, because Y, or Z happens".
Write it as an ABT:

> ___ **and** ___, **but** ___, **therefore** ___.

- Storage doc: *The cluster has three small disks and is a third full, **but** a resize is a
  full rebuild because there are no master nodes, **therefore** resize generously once, to
  25 GiB on gp3.*
- Git guide: *Everyone shares `main` and commits daily, **but** history is easy to damage,
  **therefore** branch, commit small, rebase, and never force-push.*
- Postmortem: *A deploy passed its canary and the alert fired in two minutes, **but** a
  `NaN` timeout hung every worker and the restart loop pointed everyone at the wrong cause,
  **therefore** fail loudly at startup and suspect the deploy first.*

One *but*. If you need two, the document has two stories and you must pick one to carry the
plot; the other becomes a sub-beat or a pop-out. If you cannot find a *but* at all, the
document is pure reference — see kishōtenketsu under "the shape" below.

The **therefore** is the story's meaning. It is what the fable's last line will say in plain
words, and every scene exists to make the reader feel its weight before they read it.

## Step two: one protagonist who owns the problem

One hero. Not a hero and a guide who share the stage, not a hero who watches. **The
protagonist must own the problem the document solves**: they are the one who has to decide,
build, ship, stand the watch, or answer for the outage. Everyone else exists to make that
harder or to ask them a question.

- Give them a **concrete want** in the first lines (Vonnegut: *every character should want
  something, even if it is only a glass of water*). Not "to learn about storage" — "to tell
  the village what to do about the barns before winter".
- Give them **opinions and attempts**. A passive, malleable protagonist "is poison to the
  audience" (Pixar rule 13). Picture-book editors put it the other way round: the character
  must solve the problem; *avoid wise characters swooping in to fix things*.
- Give them **something to lose** that the document actually names: the barns overflow, the
  build breaks, the customers see an error page. Never invent peril the document does not
  have; real stakes, themed, read as a story — fake stakes read as childish.
- Let them **fail once**, in the way the document warns about, and recover by their own act.
  "You admire a character for trying more than for their successes" (Pixar rule 1).

The mentor, the peer who gets it wrong, the voice of authority: three named recurring
characters at most, each with one trait and one tic. They recur so that stage five feels like
the same book as stage two.

## Step three: the shape, chosen by document type

Documents come in a handful of kinds, and each kind already implies a story shape. Choose
deliberately; it decides what the protagonist is *doing* on every page.

| document | what it really is | story shape | the hero is… |
|---|---|---|---|
| README, onboarding, setup guide | a threshold to cross | **the apprenticeship** — arrive, be shown the rules one at a time, be trusted with a real task at the end | earning the right to work alone |
| decision record, ADR, proposal, sizing doc | an argument for one option over others | **the choice** — the hero must decide; each encounter removes an option or adds a constraint; the tempting wrong option is tried or nearly tried; the hero chooses and says why | deciding, and being answerable for it |
| runbook, procedure, checklist | steps under pressure | **the watch** — the alarm sounds; the hero follows the drill; one step skipped shows why it exists | doing the steps while something is at stake |
| postmortem, incident review | a tragedy already over | **the retelling** — kishōtenketsu (see below): the day as it was, the signs nobody read, the twist that reframes everything, the lesson looked back on | piecing together what happened, then what to change |
| spec, design doc | a brief to build to | **the commission** — the patron states the brief; the hero builds; the build is tested against the brief | making the thing right |
| tutorial, how-to | a path with a made thing at the end | **the journey** — each leg adds a tool; the hero uses all of them at the destination | getting somewhere with a full satchel |
| style guide, conventions, rules | a code of conduct | **the oath** — the hall of rules seen once as scenery, then one rule broken and its consequence lived | joining a guild and being caught out once |
| a fairy tale or story | already a story | keep its own shape; do not impose another | whoever it already is |

**Kishōtenketsu**, for documents with no conflict. Reference and explanatory documents often
have no *but*: nothing goes wrong, nothing is chosen. The Japanese four-part form makes meaning
without conflict — **ki** (introduce a situation), **shō** (develop it, no change), **ten**
(a twist of *perspective*: a new fact that reframes what we saw), **ketsu** (a conclusion that
reflects on both). For a postmortem it is exact: the ordinary morning, the deploy that passed,
the single log line `timeout: NaN` that recasts twenty minutes of chasing the cluster, and the
lessons. For a glossary or an architecture overview, the twist is the moment the hero sees how
the parts they were shown separately depend on one another. Research on the form finds readers
"better able to pick out the main points" — it is a teaching structure.

## Step four: the fact ledger

The plot must **align with the document**, and the book must **explain everything**. Neither
happens by feel. Before writing beats, make a ledger: every heading, every number, every
command, every rule, every warning in the source, one per line. Then assign each line a home:

- **narrative** — the fact is *shown*: it is an object, a place, a thing that happens. The
  relationships between facts live here (this causes that; this is why).
- **pop-out** — the fact is *stated*: an exact value, command, path, table. Pop-outs carry
  values; the narrative carries the *why*. A number belongs in a pop-out even when the
  narrative alludes to it ("thirty-seven parts full" in the tale; `11.12 GiB of 30 GiB (37%)`
  behind it).
- **note** — the fact belongs in the stage's **technical bit**: the plain-voice box under the
  tale that says, without allegory, what this stage's section of the document actually states.
  Every stage has one. Numbers, names, commands and rules land here even when a pop-out also
  carries them, because the note is what a reader skims when they come back to check something.
- **recap** — the fact is a takeaway the reader must leave with.
- **scenery** — a flat list with no causal weight (seven naming conventions, six action
  items). It gets one scene as a place — a hall of banners, a wall of case files — and its
  items become pop-outs. Flat lists are scenery, never plot.
- **omitted** — deliberately, and named in the hand-over.

Two rules the ledger enforces. **Nothing unassigned**: every line has a home before you write.
**Nothing invented**: if the source does not say *why*, the story does not say why either — a
mentor can say "we do not know", a pop-out can say "the document does not give a reason". The
build script warns about uncovered headings; the ledger is how you never see that warning.

The ledger also tells you the book's size. Five to nine beats carry a story; if the ledger has
forty narrative-home facts, most of them are really pop-outs or scenery.

## Step five: the spine, then the beats

Now — and only now — fill in Kenn Adams' story spine (Pixar rule 4):

> Once upon a time ___. Every day ___. But one day ___. Because of that ___. Because of that
> ___. Because of that ___. Until finally ___. And ever since then ___.

The *but one day* is the ABT's *but*. Each *because of that* is a beat. *Until finally* is
the hero's own act. *Ever since then* is the recap.

**Decide the ending first** (Pixar rule 7; Julia Donaldson: "you need to know the punchline
before you start"). The ending is the *therefore* made concrete — the hero doing the thing,
unaided. Then build the middle so that every beat is a step the hero could not skip on the way
there.

**Start as close to the end as possible** (Vonnegut rule 5). The first stage is not the
morning the hero woke up; it is the moment the problem lands on them. Setup sections (install,
access, prerequisites) *are* that moment — the threshold — not preamble before it.

**Five to nine beats**, each one scene: one place, one exchange, one change. Map them:

- **Beginning — one beat.** The want, the stake, the threshold, stated by someone entitled to
  state it. End on the door opening.
- **Middle — three to six beats.** Each caused by the last; each costs the hero more. Picture
  books count in threes and escalate (the Gruffalo's fox, owl, snake). The first tool is
  handed over; the second the hero must use; the third they must choose between two.
- **The turn — one beat, in the last third.** See below.
- **End — one beat and the ending screen.** The hero acts alone; the opening image returns,
  changed; the recap says the *therefore* in plain words.

Every stage's **last sentence pulls forward**: a question, a door, a name not yet explained,
an instruction not yet obeyed. In a picture book the page turn is the suspense; ours is the
"next" button, and a stage that ends on its own summary wastes it.

## Mentors ask; the hero acts

*The Goal* teaches manufacturing theory to millions of readers who never asked to learn it.
Goldratt was explicit about how: Jonah, the mentor, **never gives Alex the answer**. He asks a
question and leaves. Alex struggles, tries things, and the reader works it out a page before
Alex does. "Had Jonah given Alex all the answers at the outset… Alex would never have
implemented them." *The Phoenix Project* copies the device exactly.

Apply it:

- A mentor's line is a **question or a constraint**, rarely an explanation. "What happens to
  the grain while you knock the wall out?" — not a paragraph about blue/green deployments. The
  explanation lives in the pop-out, where the reader who wants it can pull it.
- The hero **answers, guesses, or acts** in the same scene. If a stage has the hero only
  listening, rewrite it until they do something with what they heard.
- Each encounter **changes the hero's options**: adds a constraint, removes a choice, hands
  over a tool. If the hero leaves a scene with the same options they arrived with, the scene is
  a tour stop.
- Dialogue does work. Every line either reveals what a character wants or moves the plot
  (Vonnegut rule 4). Cut the greeting, the weather, the "let me explain".

## The turn: the moral arrives as a consequence

Fables do not teach by presenting rules; they teach "by the learning of the consequences
brought about by acting in a particular way". The moral is *drawn from what happens*. So in
the last third, the hero — or the peer who exists to get things wrong — does the thing the
document warns against, and the consequence the document names arrives: the force-push
overwrites a shipmate's work; the `NaN` timeout hangs every worker; the cheap masters run out
of credits mid-election. Every document hands you this material: the "do not" list, the
common mistakes, the root cause, the false economy, the warning box.

Stage it as a real event with a real cost, then let the hero recover **by their own act**
using what the middle gave them. Coincidence may get them into trouble; never out of it
(Pixar rule 19). The reader remembers the rule because they watched it break — a book where
nothing goes wrong teaches nothing, because the reader never learns which mistakes the
document exists to prevent.

The recap is the fable's **epimythium**: the lesson stated once, plainly, after the story has
earned it. One line per thing the hero can now do, under a dozen words each.

## Allegory that teaches

An allegory teaches only when the *property that matters* transfers. Research on teaching
analogies is blunt: a poor analogy causes more misconceptions than none, and the failures come
from mapping surface features instead of structure. So:

- **Map the mechanism, not the look.** Master nodes "come in threes; one gives no HA, two
  split-brain" → keepers who "come in threes, never one, never two" transfers the rule that
  there is no cheap version. A "purple crystal" transfers nothing.
- **One mapping, stable for the whole book.** If the VPN is the Veil in stage one, it is the
  Veil in stage six. Readers learn the allegory once.
- **Declare the break.** Where the analogy stops holding, say so in the pop-out ("unlike a
  wheel, a volume type can be changed later — but it costs another blue/green"). The pop-out
  is the negotiated boundary of the metaphor.
- **Objects, not abstractions.** Give every concept a thing that can be held, opened, carried,
  or dropped: the env file is a ledger; the test suite an anvil; the staging area a bench. If
  the stage's central image cannot be drawn, the allegory is still abstract.
- **The tale is legible without clicking.** A reader who never opens a pop-out should still
  know what happened and roughly what it means. The marked phrase names the thing in theme;
  the sentence around it carries the real meaning.

## Voice and point of view

**Always third person, past tense, with a named protagonist.** This is the register of every
fairy-tale pop-up on the shelf — *"Little Red Riding Hood knew she wasn't to talk to strangers
but couldn't help telling the wolf all about her sick grandmother"* — and it is not optional
here. Give the hero a name on the first page and use it.

Never narrate in the second person. "You approach the keep" fails for three reasons that all
matter to this skill:

1. **"You" cannot be drawn.** Every scene has a hero standing on the page. A named character can
   be shown arriving, deciding and leaving changed; a second-person reader cannot appear in the
   picture, so the art and the prose stop describing the same thing.
2. **"You" cannot be wrong.** The turn depends on the hero making the mistake the document warns
   about. Telling a reader *they* got it wrong is an accusation; watching Adam get it wrong is a
   story, and it is the reader who draws the lesson.
3. **"You" flattens the cast.** Mentors ask questions and the hero answers. With a second-person
   hero there is no one to answer, and the scene collapses back into a lecture.

The one place second person belongs is **inside quotation marks**, where one character addresses
another: *"How many barns have you?" asked the captain.* That is correct and natural — dialogue
is where the reader hears the rule spoken.

The same applies to the cover blurb, the ending and the recap: write *about* the hero, never
*at* the reader. "Weigh anchor: it is three days' sail" becomes "The captain has the bearings,
and it is three days' sail." The build script warns when narration outside dialogue uses
second-person pronouns.

One scene per stage, one beat per scene, the same voice from cover to recap.

## A spread, sentence by sentence

The published fairy-tale pop-ups run **55 to 110 words a spread**, and every spread has the
same anatomy. Study one:

> *On the way through the forest, Little Red Riding Hood found some beautiful wild flowers to
> pick for her grandmother. As she carried on down the path with a basket full of flowers, a
> cunning wolf crept from the bushes, licking his lips. "Where are you going?" asked the wolf.
> Little Red Riding Hood knew she wasn't to talk to strangers but couldn't help telling the
> wolf all about her sick grandmother.*

1. **Where we are and what the hero is doing** — one sentence, already in motion.
2. **The other party arrives with a want of their own** — "licking his lips" is the whole
   villain.
3. **One line of dialogue that moves the plot** — a question.
4. **The hero acts, and the moral is embedded in the act** — she *knew* the rule and broke it.
   The consequence is the next spread.

Sixty-eight words. No description of the forest, no explanation of wolves. Write every stage
to that anatomy: place-and-motion, arrival, one exchange, one act with the rule inside it,
and a last line that makes the reader turn the page.

## Economy

- **60 to 120 words of narrative per stage**, and 60 is often better. Long source sections
  earn more pop-outs, not more prose.
- **Every sentence reveals character or advances the action** (Vonnegut rule 4). Mood gets one
  sentence per stage; the rest carry a fact, a movement, or a consequence.
- **Give the reader the information early** (Vonnegut rule 8: "to hell with suspense"). Our
  suspense is *what will the hero do*, never *what is the fact* — facts are in the pop-outs,
  available at once. Withholding a fact to create tension makes the book worse at its job.
- **Simplify, focus, combine characters, hop over detours** (Pixar rule 5). Two guides become
  one. Two stages that teach the same capability become one.
- **Repetition with variation**: one refrain at the same moment in three or four stages, or
  one carried object that gains an item per stage. It is how a short book feels cumulative.
  Used in every stage it becomes wallpaper.
- **Read it aloud.** Where you run out of breath, put a full stop. Strong verbs, concrete nouns,
  never two adjectives on a noun; cut "suddenly", "somehow", "seems to", "begins to", "you
  find yourself".
- **The essence and its most economical telling** (Pixar rule 22). Draft, then cut a third.

## A worked example

The storage document (`adam-and-the-hill-kids-work/source.md`) as it was first told, and as
the method above tells it.

**As a tour.** Adam is going home. At five stops, five villagers each explain one section of
the document to him — the surveyor the current state, the builders blue/green, the captain the
masters, the wheelwright gp2/gp3, the miller the recommendation. Adam says "Can't you just…?"
and "What should we do?". The refrain "Up, up, up goes Adam" carries him between stops. The
recap lists the decisions. Every fact is present; the allegory is good; the connective between
every stage is *and then*. Adam decides nothing — the miller hands him the answer.

**The one argument.** *The three barns are a third full and filling, but making a bin bigger
means rebuilding the whole row because the village keeps no keepers, therefore build once,
big — twenty-five bushels a bin, on the new wheels.*

**The shape.** A sizing doc is a decision record → **the choice**. Adam must decide, and be
answerable.

**The protagonist who owns it.** Adam is not walking home; he has been sent by the village to
come back with an answer before the sacks stop fitting. His want is concrete and his stake is
real: the surveyor's "the sacks keep arriving".

**The spine.** *Once upon a time the village kept three barns with a ten-bushel bin each.
Every day the sacks came in and the bins were a third full, which sounded fine. But one day the
surveyor showed Adam the line on the wall you may never fill past, and sent him up the hill to
decide what to do. Because of that he asked the builders to make a bin bigger — and learned it
meant raising a whole second row and carrying every sack across. Because of that he went to
hire keepers, who could have let the builders knock a wall out instead — and the captain showed
him what three keepers cost against what all the grain is worth, and that keepers earn their
keep in a village of ten barns, not three. Because of that he was tempted by the cheap keepers,
and the captain told him what happens when a cheap keeper falls asleep at the door. Because of
that he knew the rebuild was coming whatever he did, so it had better happen once — and the
wheelwright showed him that the wheels should change in the same night. Until finally, at the
miller's ledger, Adam did the sum himself and chose: twenty-five bushels a bin, on the new
wheels, for about the price of a loaf more each month. And ever since then the village has
had room for four harvests, and Adam knows the sign that means it is time to climb again.*

**What changed.** The same five villagers, the same facts, the same pop-outs. But every stage
now *removes an option or adds a constraint*, the cheap keepers are the turn (the false economy
the document warns about, nearly chosen), Adam does the final sum instead of being handed it,
and the ending returns to the surveyor's line on the wall — now with four times the room below
it. The recap states the *therefore*. That is the whole difference between a tour and a story,
and it cost no extra words.

## Checklist

Before building, every line is true:

- [ ] The document's one argument is written as an ABT with exactly one *but*.
- [ ] The story shape is chosen from the document's type and named.
- [ ] The fact ledger is complete: every heading, number, command and warning has a home
      (narrative / pop-out / recap / scenery / omitted-and-declared).
- [ ] One protagonist owns the problem, wants something concrete on the first page, and has
      something real to lose that the document names.
- [ ] The ending was written first; the hero acts alone in it and the opening image returns,
      changed.
- [ ] Adjacent beats are joined by *therefore* or *but*, never *and then*.
- [ ] Every mentor line is a question or a constraint; the hero does something with it in the
      same scene; every scene changes the hero's options.
- [ ] The turn is a real mistake from the source, with the source's consequence, recovered
      from by the hero's own act.
- [ ] Each allegory transfers the property that matters, stays stable all book, and declares
      where it breaks in a pop-out.
- [ ] Point of view chosen by reader and held throughout.
- [ ] Each stage: 60–120 words, place-and-motion first, one exchange, one act, last line pulls
      forward, reads aloud cleanly.
- [ ] Every stage has a `## note` — the technical bit — in plain voice, with the section's real
      numbers, names and commands.
- [ ] The recap states the *therefore* in plain words, one line per capability.
