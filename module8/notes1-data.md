(ai-ready-data)=
# 8.1 AI-ready data: what an agent needs, and making existing data ready

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 8 &middot; Section 8.1</span>
    <span class="notes-card-session">Session: Agents at work in an agency &mdash; AI-ready data, part 1</span>
  </div>
  <p class="notes-card-lede">An agent can do a job only as well as the data it can reach, read and check. For most transportation jobs that data already exists, but it was made for people to read. This section takes one job, signal operations on the morning after a hurricane, and asks what data the agent needs, why the data the district keeps today is not ready for it, and six moves that make that data ready. Section 8.2 covers the data that does not exist yet, the data it takes to improve or train an agent, and who governs the data.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Read it first</h4>
      <ul>
      <li><a href="../module5/notes3-tools.html">5.3 Tools: what an agent can reach</a> (read-only tools)</li>
      <li><a href="../module6/notes2-skills.html">6.2 Inside a skill</a> (the <code>d7-signal-sop</code> skill used here)</li>
      <li><a href="../module7/notes2-rag.html">7.2 Retrieval (RAG)</a> (looking things up in the SOP)</li>
      </ul>
    </div>
    <div>
      <h4>Used again in</h4>
      <ul>
      <li><a href="notes2-data-create.html">8.2 Data to create, data to improve an agent, and governance</a></li>
      <li><a href="../capstone/index.html">Capstone</a> (your project's one-page data plan)</li>
      </ul>
    </div>
  </div>
</div>

## What this section covers

- Why now: NSF's new program for making existing data ready for AI
- The job: signals on the morning after landfall, and the five questions the agent must answer
- Six kinds of data in one run of the agent, and where each stands today
- Why data kept for people is not ready for an agent
- Six moves that make existing data ready, each with a worked example
- What to do for your project

**Where the ideas come from.** The six moves follow the work list of NSF 26-512. The agents unit as a whole follows
[CMU 11-768 AI Agents](https://www.cmu-agents.com/) (Fried and Neubig), and the training part of Section 8.2 follows
Stanford CS 329Z *Engineering AI Agents* (Yang, Ryan and Yang), lecture 11, "What Data Do Agents Need?". The running
example is the FDOT District 7 *Traffic Signals Standard Operating Procedures Reference Guide* (v1.5, June 2025) and
the class skill [`d7-signal-sop`](https://github.com/ai4mobility/transportation-skills/tree/main/skills/d7-signal-sop)
built from it. Clause names such as "Immediately Post Storm 3.2.1" point to that SOP. **The storm scenario, the
signal IDs and every sample record on this page are synthetic.** They are not District 7 data.

## Why now: NSF pays to make existing data ready for AI

In July 2026 the National Science Foundation opened a program called
[AI Datasets (NSF 26-512)](https://www.nsf.gov/funding/opportunities/ai-datasets-unlocking-dataset-value-ai-enabled-scientific-discovery/nsf26-512/solicitation).
It pays teams to make existing scientific datasets usable by AI: up to $200,000 for planning grants, $2 million for
Impact awards and $5 million for Flagship awards, about $60 to $100 million in total, with a deadline on the first
Wednesday of November each year. It does not pay to collect new data. Its starting point is that datasets were
curated "for use by humans or heuristic scripting," and that AI systems are now often the first reader.

Transportation agencies are in the same position. They hold decades of data collected for engineers to read, and
agents are a new kind of reader. So this section uses the program's work list as a checklist for transportation data.

| Word | What it means here |
|---|---|
| **AI-ready data** | Data an agent can reach through a tool, read without guessing what a field means, join to other data, and trust because each value says where it came from |
| **State data** | What is true on the road right now: which signals are dark, where the generators are |
| **Task record** | One past piece of work packaged for testing: what was known at the time, what was decided, and what happened |
| **Checker** | Anything that says whether an answer is right: a rule in code, a rubric, or a person |
| **Trajectory** | A step-by-step recording of someone, or some agent, doing a task |
| **Environment** | A place to practice a task: a simulated situation plus a checker |
| **Provenance** | The record of where a value came from: who or what reported it, when, and how |

## The job: signals on the morning after landfall

After a hurricane, many signals lose power or are damaged at once. After Hurricane Sally in 2020, FDOT District 3
crews evaluated about 450 signals within 48 hours with the eSTORM app and found 69 damaged
([U.S. DOT ITS Deployment Evaluation, entry 2024-B01860](https://www.itskrs.its.dot.gov/2024-B01860)). The District 7
SOP sets out the response: check which signals still talk to the central signal system (ATMS), send Situational
Awareness Teams (SAT) to look, put generators at dark signals and refuel them, record the damage in eSTORM, and later
request federal reimbursement.

The agent's job is to help the district signal team decide what to do next, and to write each suggestion in a form a
person can check. It proposes. A person decides and acts.

**The scenario (synthetic, from the class skill's test file).** It is 07:30 on the morning after landfall in Pinellas
County.

- ATMS shows 31 signals on the US-19 corridor: 18 green, 6 yellow, 7 red.
- Generator NH-114 went out at 06:10 to one red signal, and NH-121 at 06:40 to another.
- The power company's outage map shows power coming back in patches.
- The Governor's executive order runs through November 8.

**What we ask the agent.** Draft the action cards for the next six hours. Each card names one action, the SOP clause
behind it, and who decides. The agent has read-only access. It never updates eSTORM or dispatches a crew.

**Five questions the agent has to answer.** Each one needs its own kind of data, and the rest of this section is
organized around them.

1. What is true on the road right now?
2. What is out there: which signals, generators, crews and corridors?
3. What do the SOP and experienced staff say to do?
4. Is my draft right?
5. What happened afterwards, and what should change next time?

**You have made this kind of list before.** Before a signal retiming study you list the counts, timing sheets and
geometry you need. A data plan for an agent is the same list plus two things a person never needs written down: what
each word and code means, and how to tell a right answer from a wrong one.

## Six kinds of data in one run

```{figure} ../_static/figures/ARD_Loop_Data.png
:alt: The agent's run as six steps down the middle. Steps 1 to 3 read state data, reference data, and rules and know-how, all of which exist today. Step 4 draws on checks and answer keys, step 5 is a person deciding, and step 6 looks back at outcomes; records of work and outcomes are drawn dashed because they are scattered or not kept. The situation box shows 31 US-19 signals, 18 green, 6 yellow and 7 red.
:width: 100%

One run of the agent touches six kinds of data. Steps 1 to 3 read data that exists but was made for people; steps 4
to 6 need data that nobody keeps yet. Step 5 is always a person.
```

| Kind of data | Question it answers | In the storm job | Where it stands today |
|---|---|---|---|
| **State** | What is true right now? | ATMS status colors, eSTORM entries, SAT reports, the power company's outage map, the generator log | Exists. Changes by the hour. |
| **Reference** | What is out there? | Signal inventory, response zone maps, Priority #1 intersections, generators and their NH numbers, who maintains each signal | Partly exists. In SOP v1.5 the zone-map and responsibility appendices are blank, and there is no Priority #1 list. |
| **Rules and know-how** | What should be done? | The SOP's 150 rules, the words field crews use, lessons from past storms | Exists as a PDF. The class skill turns it into files an agent can read. |
| **Checks and answer keys** | Is the draft right? | The SOP's numeric rules as code (six-hour refuel, 24-hour encumbrance, the $5,000 threshold); past storms with the decisions staff made | Not in the SOP. The class skill has the rules in `rules.py`. Past storms are not packaged as cases. |
| **Records of work** | What was proposed and decided? | Each draft card, the person's edit, and the reason | New. Today such decisions pass through a group chat (One Month Prior 14). |
| **Outcomes** | Did it help? | Hours each signal stayed dark, generator-hours used, whether the repair was reimbursed | Scattered across the tracking spreadsheet, eSTORM downloads and funding records. |

**One card, five kinds of data.** Here is one card from the class kit, written by Claude following the skill, on the
synthetic scenario. Trace each field to the data it came from.

```{figure} ../_static/figures/ARD_Card_Sources.png
:alt: Card 4, "Refuel NH-114 by 12:10 and NH-121 by 12:40", with arrows from its fields to five sources - the generator log (state data), gaps.md saying Appendix C is blank (a reference gap), rules.py refuel returning 12:10 (a rule as code), sop_text.md with the clause's exact words and weight, and clause 3.2 where a person sets later refuels.
:width: 100%

Each field of a good card can be traced to its data. The due times come from code, not from the model's arithmetic.
The "Who" field comes from a written gap, not a guess.
```

If one of these sources is missing or wrong, the card is still well formatted, and wrong. That is why data, not
the prompt, decides how good the card can be.

**The procedure tells you where the data is.** A fast way to start any data list is to read the procedure and mark
every system or record it names. In the D7 SOP, 77 of the 150 rules on pages 5 to 11 name at least one.

| System or record named in the SOP | Rules that name it |
|---|---|
| Funding records (TWO, DDIR, FPID, CFM, SharePoint) | 33 |
| eSTORM and eSTORM Lite | 15 |
| Generator tracking (NH numbers, check-in) | 7 |
| ATMS signal system | 6 |
| Photos and GPS | 5 |
| Tracking spreadsheet | 4 |
| Contact lists | 4 |
| Six others (damage apps, signal inventory, maps, group messaging, outage maps, CCTV) | 1 to 3 each |

Counted by keyword on the skill's `references/sop_text.md`. A rule can name more than one system, so the column adds
to more than 77.

The count shows what the procedure cares about. Money is tracked closely, because federal reimbursement depends on
it. Time on the street is tracked loosely. The SOP asks for the time each generator was deployed (Immediately Post
Storm 3.1) and for an hourly download of eSTORM (Ongoing Efforts 1.1), but there is no field for how long each signal
stayed dark. That has to be rebuilt from the two, and it matters, because hours dark is the outcome we most want an
agent to reduce.

## Why data kept for people is not ready for an agent

The data exists, but every system assumes a reader who already knows the corridor, the storm and the other systems.
An agent knows none of that unless the data says it.

```{figure} ../_static/figures/ARD_Two_Readers.png
:alt: One synthetic tracking-sheet row, "NH-114 | US19/GTB | 6:10". For each piece, an engineer reads generator 114, US-19 at Gulf to Bay Blvd (signal SIG-1041), 6:10 AM today Eastern time, and infers that the first refuel is due at 12:10. An agent can read only short strings, with no day, no AM or PM and no matching intersection name.
:width: 100%

The same row, read by an engineer and by an agent. Nothing in the row is wrong. It was written for a reader who knows.
```

```{figure} ../_static/figures/ARD_One_Signal_Five_Places.png
:alt: One red signal as kept in five places - the ATMS map, eSTORM Lite, the tracking spreadsheet, the power outage map and a photo folder - each with its own name for the signal. Arrows labeled describe, extract, link and harmonize, link by location, and extract lead to one joined record with a signal ID, status with source and time, power, generator with first refuel due, damage marked AI-extracted and not yet confirmed, and cabinet unknown.
:width: 100%

One signal lives in five places, each kept for a person. The agent needs the one record on the right, where every
value says where it came from and when. The arrows are the six moves below.
```

Six things make the left side hard for an agent. None of them is an error in the data.

1. **Names instead of keys.** The tracking sheet may say "US19/GTB". The SOP asks for photo folders named "Major Street
   @ Minor Street" (0-1 Week 5). Funding groups repairs by Object ID (Funding 0-1 Month 1). A person matches these by
   eye. An agent guesses, and a wrong guess makes no noise.
2. **Meaning that lives in people's heads.** In ATMS, green means the signal is communicating, and red means
   non-operational (Immediately Post Storm 1.1 and 1.2). Red does not say why: no power, a cut communication line, or
   physical damage. Staff know that a red symbol means "send someone to look". The data does not say so.
3. **No clock.** A status board shows the latest value. The SOP asks for an hourly eSTORM download to keep a history
   (Ongoing Efforts 1.1), because the app itself shows only now. Without those snapshots, nobody can later ask what
   was known at 07:30.
4. **Facts locked in text and photos.** A comment such as "2 heads hanging, cab ok" and a photo with GPS (Immediately
   Post Storm 6.4) are clear to a person. An agent needs fields: which of the 18 components on the field checklist,
   how badly, and confirmed by whom.
5. **Decisions that never become data.** Teams coordinate in a group chat (One Month Prior 14, Immediately Post Storm
   9.2). Why a generator went to one intersection and not another is in a text message, if it is anywhere.
6. **Blank means two things.** A signal with no SAT report may be fine, or nobody has driven that corridor yet. People
   know which. The data shows the same empty cell for both.

```{figure} ../_static/figures/ARD_Blank_Two_Things.png
:alt: Ten synthetic signals on US-19 at 09:30. SAT drove S1 to S6 at 09:00 and found S3 damaged and S6 dark; S7 to S10 have not been driven. The sheet as kept lists only problems, so S1, S2, S4 and S5 and S7 to S10 are all blank. The ready version gives every signal a value, with S8 "unknown, not observed yet".
:width: 100%

A blank cell means two different things. An agent that reads blank as "fine" sends no crew to S7 to S10. Make
"unknown, not yet observed" its own value.
```

This is good data for its first reader. The rest of this section is about preparing it for a second one.

(six-moves)=
## Six moves that make existing data ready

NSF 26-512 names the work: extract features, generate metadata, link datasets, harmonize them, fill gaps, and judge
readiness. Here is each move on the storm job. None of them needs new data collection.

```{figure} ../_static/figures/ARD_NSF_Map.png
:alt: Seven lines from the NSF solicitation on the left mapped to the work on storm signal data on the right - feature extraction to Move 1 Extract, metadata generation to Move 2 Describe, fusion and linkage to Move 3 Link, harmonize to Move 4 Harmonize, correcting noise and gaps to Move 5 Fill gaps, discerning readiness to Move 6 Score readiness, and governance to Section 8.2.
:width: 100%

What NSF 26-512 asks for, done on transportation data.
```

### Move 1. Extract: turn text and photos into fields

A vision model looks at each damage photo and proposes which checklist component is damaged: signal head, backplate,
mast arm, cabinet, power service and so on. A language model does the same for comment fields. The result is a
proposal with the photo attached, and an inspector confirms it. This is where a small model you trained yourself earns
its place: its output becomes a field the agent can read.

```{figure} ../_static/figures/ARD_Extract.png
:alt: A schematic span-wire signal with two heads hanging and the SAT comment "2 heads hanging, cab ok" go into a model, which proposes fields - component (1) signal head, count 2, condition hanging, evidence the photo and the comment; component (17) signal cabinet, no damage reported; made by AI with model and date; confirmed by an inspector, not yet.
:width: 100%

An extracted field is a proposal with its evidence attached, until a person confirms it. Keep the doubt in the field:
does "cab ok" mean someone opened the cabinet, or saw it from the truck?
```

*Check it:* compare the extracted fields with an inspector's labels on photos the model has never seen.

### Move 2. Describe: write down what every field means

This is the metadata. For each field, write the unit, the allowed values, and what each value means in practice. Add
the time zone and how the value was obtained: automatically from ATMS, seen from a vehicle, or reported by a local
agency. An AI model can draft this from sample records, and the people who use the system correct it. Keep it as a
skill file ({doc}`6.2 <../module6/notes2-skills>`), so the agent loads it only when a step needs it. Here is one
illustrative entry; the color meanings and clause numbers are the SOP's.

```text
## atms_status   references/data_dictionary.md
values:   green | yellow | red
green:    communicating, operational (1.1.1)
yellow:   in flash (1.2)
red:      non-operational (1.2)
NOT said: why it is red: no power, a cut
          comms line, or damage. Send a SAT.
use:      yellow and red rank SAT and
          generator teams (1.2.1)
obtained: automatic, from the signal system
time:     observed_at, Eastern; keep every snapshot
missing:  not polled -> "unknown", never blank
```

The line that matters most is "NOT said". Staff know a red symbol means "send someone to look". The data never says
so unless you write it down.

*Check it:* give the description and ten records to someone outside the signal team. Can they read the records
correctly?

### Move 3. Link: one key for every signal

Build a crosswalk table: one signal ID, every name people use for it, its coordinates, its maintaining agency, and its
ID in each system. The outage map has no signal IDs, so link it by location: which signals sit inside which outage
area. Link each repair to its work order and funding numbers; the SOP already asks for that log (Funding 0-1 Month 4).

```{figure} ../_static/figures/ARD_Link.png
:alt: A synthetic map of US-19 with four signals and two hatched outage areas; SIG-1041 and SIG-1050 sit inside outage areas. Beside it, the crosswalk row for SIG-1041 lists its name in ATMS, its eSTORM object, its tracking-sheet name "US19/GTB", its photo folder, "inside area A (by location)" for the outage map, its work order numbers and its latitude and longitude.
:width: 100%

One signal ID joins five systems. People join these by eye once; an agent joins them hundreds of times, so every
guess becomes a silent error.
```

*Check it:* draw a random sample of links and verify each by hand. A name that matches nothing is rejected, not guessed.

### Move 4. Harmonize: the same codes across agencies and storms

District 7 works with Pinellas County, Hillsborough County, the City of Tampa and other maintaining agencies. Each has
its own conventions, and forms change between storms. Map everything to one set of status codes, damage codes and time
formats, and keep the original value beside the harmonized one. Without this step nothing learned in one storm carries
to the next.

```{figure} ../_static/figures/ARD_Harmonize.png
:alt: Three illustrative code sets - Agency A with DARK, FLASH, OK; Agency B with 0, 1, 2 and blank; a district form from an earlier storm with Not operational, Flashing, Operational - mapped by lines to one code set of non-operational, in flash, operational and unknown. Agency B's blank maps to unknown. A record keeps status_original "0" beside status non-operational and the code map version.
:width: 100%

One set of codes, originals kept. These codes are illustrative, not real agency codes. Watch the blank in Agency B: it
maps to "unknown", not to "operational".
```

*Check it:* count records per code before and after. A code that suddenly gains or loses many records points to a
mapping mistake.

### Move 5. Fill gaps honestly

Build one timeline per signal from the hourly eSTORM downloads, the SAT passes at 9:00 AM and 2:00 PM, and the
generator log. The time power came back is then known only as a window, between the last snapshot that saw the signal
dark and the first that saw it lit. Record the window, not an invented minute, and give every value one of three
flags: observed, estimated or unknown. You know this move from detector data, where imputed values are flagged so that
nobody mistakes them for measurements.

```{figure} ../_static/figures/ARD_Timeline.png
:alt: One synthetic signal, SIG-1050, from 00:00 to 14:00 on day 1. Hourly downloads show it operational at 00:00 and 01:00, non-operational from 02:00 to 11:00, and operational from 12:00. SAT saw it dark at 09:00 and lit at 14:00. Power was lost between 01:00 and 02:00 and came back between 11:00 and 12:00, so it was dark between 9 and 11 hours.
:width: 100%

A window, not a number: hours dark between 9 and 11, not an invented "10.0". The SOP's hourly eSTORM download
(Ongoing Efforts 1.1) is what makes this timeline possible.
```

*Check it:* hide some observed values, fill them with your method, and compare.

### Move 6. Score readiness before you build anything

Write ten questions the job needs answered, and count how many the data answers without a phone call. That count is
your readiness score. Three examples:

- *Which signals on US-19 were dark at 2:00 PM on day 2?* Needs a clock and kept history (Move 5). The live board
  cannot answer it.
- *Which generators are due for refueling in the next hour?* Needs the generator log linked to signals (Move 3) and the
  refuel rule as code.
- *Which repairs within a quarter mile of each other total $5,000 or more?* Needs a location on every repair (Move 3)
  and the DDIR rule. Section 8.2 runs it.

Then score the data against seven readiness questions. Here they are for the five places of the figure above, before
and after the moves.

| Readiness question | As kept for people | Ready for an agent |
|---|---|---|
| Can the agent reach it? | Screens, a shared sheet, a web map | A read-only tool returns the records it asks for |
| Can it read it? | Colors and shorthand | Every field has a written meaning, unit and time zone |
| Can it join it? | Five names for one signal | Every record carries the same signal ID |
| Does it have a clock? | Latest value only | Every value has the time it was observed, and history is kept |
| Can it trust it? | No source on values | Every value names its source |
| Does it know what it does not know? | Blank | "Unknown" is a value, different from blank and from "OK" |
| Is anything in it that should not be? | Keys, locks and phone numbers in the sheet | Removed inside the tool, before the agent sees it |

:::{admonition} One caution
:class: warning
Moves 1 and 5 create values that no person entered. Keep them apart from observed values, label each with its method
and date ("AI-extracted, model, 2026-10-10"; "estimated window"), and never let a made value overwrite an observed
one. An extracted or estimated value that looks like a field report is the most dangerous data in this module. An agent
will happily treat your model's guess as a fact if the data does not say otherwise.
:::

**The same lesson outside storms.** Florida's work-zone feed, which you used in {doc}`5.3 <../module5/notes3-tools>`,
is machine-readable but not agent-ready. On Nov 5 it held 3,109 work zones, 1,056 of them marked completed but still
listed, and the whole file came to about 50 million tokens, far more than any agent can read. A read-only tool that
filters by status, road and distance answered "am I in a work zone?" in 176 tokens. The moves there: reach (a filtering
tool), describe (what "completed" means), and make "unknown" explicit. Machine-readable is not the same as ready for
an agent.

## For your project

Pick the one dataset your agent depends on most, and do three things before the next class:

1. **Score it.** Write ten questions your project's job needs answered and count how many the data answers without a
   phone call. Then go through the seven readiness questions above.
2. **Find the blanks.** In each source, what does "not yet observed" look like, and can your agent tell it from "fine"?
3. **Pick your first move.** Which of the six moves fixes the worst gap? If your team trained a small model, it is
   probably Move 1: your model's output becomes a field, labeled as made by your model.

Section 8.2 ends with a one-page data plan that builds on these answers.

## Check yourself

1. A county wants an agent to rank damaged signals for repair. It has 4,000 storm photos in folders named by
   intersection and a spreadsheet of repair costs. Which two moves come first, and why?
2. Your tracking sheet lists only signals with problems. An agent reads it and reports "28 of 31 signals on the
   corridor are fine." What is wrong with that sentence, and what change to the data would make it true or false?
3. For your own project, name one piece of data that exists but was made for people, and the move that would make it
   ready.

## Sources

- U.S. National Science Foundation (2026). [NSF 26-512: Unlocking Dataset Value for AI-Enabled Scientific Discovery (AI Datasets)](https://www.nsf.gov/funding/opportunities/ai-datasets-unlocking-dataset-value-ai-enabled-scientific-discovery/nsf26-512/solicitation),
  program solicitation, posted July 21, 2026 (award sizes, scope, and the work list behind the six moves).
- FDOT District 7 (2025). *Traffic Signals Standard Operating Procedures Reference Guide*, v1.5, pages 5–11, cited by
  clause; the class skill [`d7-signal-sop`](https://github.com/ai4mobility/transportation-skills/tree/main/skills/d7-signal-sop)
  (its `sop_text.md`, `gaps.md`, synthetic scenario and example cards).
- U.S. DOT ITS Deployment Evaluation database, [entry 2024-B01860](https://www.itskrs.its.dot.gov/2024-B01860) (eSTORM
  during Hurricane Sally).
- Stanford CS 329Z *Engineering AI Agents*, Fall 2026 (Yang, Ryan and Yang), lecture 11, "What Data Do Agents Need?".
- Fried, D., & Neubig, G. (2026). [CMU 11-768 AI Agents](https://www.cmu-agents.com/).
- Course materials: the slide deck *AI-Ready Transportation Data: What an Agent Needs to Do the Job*, its handout of the
  same name, and the handout *Transportation Data for AI Agents: What to Prepare and What to Augment* (the general map
  of agent data). The figures and every number on this page were computed from the skill's files; the scenario and the
  records are synthetic.

---

Next: {doc}`8.2 <notes2-data-create>` covers the data that does not exist yet, what it takes to improve or train an
agent, and who governs the data.
