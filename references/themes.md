# Theme guide

Visual presets (palette, fonts, button vocabulary, ornament) live in `assets/themes.json`. This
file covers the storytelling side: the voice, the hero, the kinds of places and people the
journey passes through, and the allegory patterns that tend to fit technical material. Read
only the section for the theme in play, plus "Inventing a theme" if the user asked for one that
is not listed.

These voices are flavour, not a licence to write more. Structure and length are governed by
`references/story.md` and the word budget in `SKILL.md`; where a voice note here suggests longer
or more descriptive sentences, it means *within* a 60-to-120-word stage, not instead of it. A
theme is a costume for the story, never a substitute for one.

## Contents

- [knight](#knight) — medieval quest
- [space](#space) — deep-space mission
- [pirate](#pirate) — voyage for treasure
- [noir](#noir) — detective case
- [expedition](#expedition) — jungle expedition
- [deepsea](#deepsea) — deep-sea dive
- [Inventing a theme](#inventing-a-theme)
- [Allegory patterns that recur](#allegory-patterns-that-recur)

---

## knight

**Voice.** Warm, slightly formal, storybook cadence. Short declaratives mixed with one longer
descriptive sentence per paragraph. Occasional archaic word (hence, sworn, forge) but no
"thee/thou": that tips into parody.

**Hero.** A newly sworn knight of an order, arriving at the keep to learn its ways before
riding out. Squires, quartermasters, smiths, heralds, and a wise elder are the supporting cast.

**Places.** The gates, the keep, the great hall, the forge, the armoury, the proving grounds
(where things are tested), the scriptorium (where things are written down), the treasury, the
watchtower, the road, the bridge, the dark wood, the shrine.

**Stage naming.** "The Gates of the Keep", "The Forge of Many Banners", "The Proving Grounds",
"The Oath of the Scriptorium". Chapters as "Chapter I", "Chapter II".

**Natural allegories.** Network/VPN = a veil or a gate only the sworn can pass. Credentials = a
sigil or a seal. Dependencies = provisions in a satchel. Build/compile = the forge tests the
blade. Tests = the proving grounds; a failing test = the blade breaks on the anvil. Lint = the
herald's inspection. Database = a great tame beast in the stables. Packages/plugins = banners
in the hall, each cut to a shape. Modules extending plugins = vassals sworn to a lord. Rules =
the oath. Config = the ledger. Deployment = riding out from the gate.

## space

**Voice.** Clean, calm, procedural, a little wonder. Mission-log tone: "Sector 3. Hull
nominal." Sentences trend short. Avoid jargon salad; one nice technical-sounding term per
paragraph is plenty.

**Hero.** A named new crew member aboard a survey ship, shadowing the veteran first officer.
The ship's AI, the engineer, and mission control talk to them.

**Places.** Docking bay, bridge, engine room, cargo hold, the observation deck, a derelict
station, a nebula, a jump gate, the survey planet's surface, a debris field.

**Stage naming.** "Docking at Meridian Station", "Sector 2: The Engine Room", "Jump Gate
Alpha". Chapters as "Sector 1", "Sector 2".

**Natural allegories.** Network/VPN = the docking clamps or a jump gate that only registered
ships may use. Credentials = a transponder code. Dependencies = the cargo manifest. Build =
pre-flight checks. Tests = the simulator or the burn test. Database = the ship's memory core.
Plugins = crew stations, each with a role. Modules = auxiliary systems patched into a station.
Rules = flight regulations. Incidents = hull breaches; a postmortem = the flight recorder replay.
Config = the nav computer's settings.

## pirate

**Voice.** Rollicking, a touch salty, spoken by a first mate who has seen everything. Nautical
vocabulary used correctly (bow, aft, hold, rigging, heading). A pinch of "aye" and "cap'n" goes
a long way; never "arrr" in prose.

**Hero.** A new hand aboard the ship, signed on for one voyage, learning the ropes from the
first mate and the ship's cook, who knows more than he lets on.

**Places.** The dock, the deck, the hold, the crow's nest, the galley, the captain's cabin,
the reef, the fog bank, the rival ship, the island, the cave with the chest.

**Stage naming.** "Signing On at Port Royal", "Leg 2: The Hold", "Through the Reef".
Chapters as "Leg 1", "Leg 2".

**Natural allegories.** Network = the harbour chain that only flagged ships pass. Credentials
= the captain's letter of marque. Dependencies = stores in the hold. Build = rigging the sails.
Tests = firing the guns at the practice barrel. Branches (git) = headings or forks in the
channel; commits = entries in the log; merges = two crews meeting at a rendezvous; conflicts =
two hands claiming the same bunk. Database = the treasure chest with a ledger. Rules = the
ship's articles, signed by every hand.

## noir

**Voice.** Hardboiled narration about a named detective: clipped, wry, rain-soaked. The register
is Chandler in the third person — never addressed to the reader. Concrete details (a flickering sign, a cold cup of coffee). Metaphors sparse and
sharp. Sentences short. No pastiche of specific films.

**Hero.** A detective who just got handed the case. A world-weary partner, a records clerk,
an informant, and the chief supply the exposition.

**Places.** The office, the precinct records room, a diner at 2 a.m., the docks, an alley,
the archive, the courthouse steps, the suspect's apartment.

**Stage naming.** "Scene 1: The File on the Desk", "The Records Room", "A Name in the
Ledger". Chapters as "Scene 1", "Scene 2".

**Natural allegories.** Fits postmortems, audits, decision records, and anything with a
"why did this happen" shape. Timeline = the sequence of events; root cause = the culprit;
contributing factors = accomplices; action items = the charges filed. Logs = witness
statements. Metrics = the coroner's report. A config value nobody knew about = the hidden
safe. Rules = the law; a rule that was bent = the loophole.

## expedition

**Voice.** Field-journal tone, observant and precise, with the enthusiasm of someone who
loves their subject. Present tense, dated entries feel natural ("Day 3. The river again.").

**Hero.** A junior member of an expedition, guided by a local guide who knows every trail and
a professor who names everything.

**Places.** Base camp, the river crossing, the canopy walk, the ruins, the cave, the cliff
path, the clearing with the lost city.

**Stage naming.** "Day 1: Base Camp", "The River Crossing", "Under the Canopy". Chapters as
"Day 1", "Day 2".

**Natural allegories.** Good for architecture documents and anything with taxonomy.
Categories = species with field marks. Directory structure = the trail network. Layers of a
system = canopy, understory, forest floor. Dependencies = supplies carried from camp. Tests =
checking the rope before the crossing. A monorepo = the whole valley seen from the ridge.

## deepsea

**Voice.** Hushed, slow, luminous. Longer sentences than the other themes, few exclamation
marks. Pressure, dark, and light are recurring images.

**Hero.** A named pilot on their first deep dive in a two-person submersible, with a veteran
marine biologist beside them and the surface ship on the comm.

**Places.** The surface, the twilight zone, the thermocline, a wreck, a trench wall, a
hydrothermal vent, the abyssal plain, the ascent.

**Stage naming.** "Depth 1: The Surface", "The Thermocline", "The Wreck at 900 Metres".
Chapters as "Depth 1", "Depth 2".

**Natural allegories.** Works well for layered systems (each depth is a layer) and data
pipelines (things sink, settle, and are indexed). Storage = the sediment. Search/indexing =
sonar. Caching = a school of fish that stays near the light. Queues = the current that carries
things down.

---

## Inventing a theme

When the user names a theme not listed (a western, a heist, a cooking competition, a Victorian
railway, a Studio-Ghibli-ish sky kingdom), build it the same way the sections above are built:

1. Decide the voice in one sentence, the hero in one sentence, and eight to ten places.
2. Write the mapping table for the source's concepts before writing prose.
3. Copy the closest preset in `assets/themes.json` into `book.json` as
   `"theme": { "extends": "<closest>", "colors": {...}, "vocabulary": {...} }` and change the
   palette, fonts (system stacks only), and the button words (`begin`, `next`, `back`,
   `finish`, `scroll`, `codex`, `chapter`, `recap`, `stageOf`). The `sceneStyle` for the
   generated backdrop is one of `hills`, `stars`, `waves`, `skyline`.

The button vocabulary matters more than it looks: "Ride onward" versus "Next" is most of what
makes the page feel like a book rather than a slideshow.

## Allegory patterns that recur

- **Ordered setup steps** (install, login, start services) are a journey through gates or
  checkpoints. Keep the order. The pop-out on each gate carries the exact command.
- **Naming conventions or taxonomies** are a hall, a manifest, or a field guide: things
  hanging side by side, distinguished by a visible mark. Make the marks meaningful.
- **Parent/child structure** (plugin and module, service and worker) is fealty, crew and
  station, ship and tender. The child exists to serve the parent; say so.
- **Rules and prohibitions** are an oath, articles, regulations, or the law. Give them a
  moment where the hero is tested against one.
- **Commands** are incantations, orders, or checklists. Never paraphrase a command inside a
  pop-out; quote it in backticks exactly as the source has it.
- **Incidents and postmortems** are a case, a storm, or a hull breach. The timeline is the
  journey; the root cause is what the hero finds at the end; the action items are the vows made on
  the way home.
