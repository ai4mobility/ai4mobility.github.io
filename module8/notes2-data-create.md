(data-to-create)=
# 8.2 Data to create, data to improve an agent, and governance

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 8 &middot; Section 8.2</span>
    <span class="notes-card-session">Session: Agents at work in an agency &mdash; AI-ready data, part 2</span>
  </div>
  <p class="notes-card-lede">Section 8.1 made the data a district already keeps ready for an agent. Some of the data an agent needs does not exist at all: past decisions packaged as tests, records of the agent's own work, a place to practice, and the lists a procedure points to but does not contain. This section shows how to create them on the same storm job, what data each way of improving an agent needs, from worked examples to fine-tuning and reinforcement learning, how many past cases a fair test takes, and who may read or change the data.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Read it first</h4>
      <ul>
      <li><a href="notes1-data.html">8.1 What an agent needs, and making existing data ready</a></li>
      <li><a href="../module6/notes2-skills.html">6.2 Inside a skill</a> (<code>rules.py</code> and <code>check_cards.py</code>)</li>
      </ul>
    </div>
    <div>
      <h4>Used again in</h4>
      <ul>
      <li><a href="../module9/notes1-adaptation.html">9.1 The adaptation ladder</a> (how fine-tuning and RL work)</li>
      <li><a href="../capstone/index.html">Capstone</a> (your data plan and your comparison table)</li>
      </ul>
    </div>
  </div>
</div>

## What this section covers

- Data that does not exist yet: task records, records of the agent's work, a practice storm, a checker you can run
  today, and the lists the SOP points to
- Data for improving the agent, and for training one: five steps, cheapest first
- How many past cases you need to test an agent
- Where training data comes from, what a trajectory is, and what data teaches by accident
- Governance: who reads the data, who changes it, and when it expires
- Where it breaks, the fit card, and your project's one-page data plan

As in {doc}`8.1 <notes1-data>`, **the storm scenario, the signal IDs and every record on this page are synthetic.** The
outputs of `rules.py` are real: they come from running the class skill's code on its synthetic test files.

## Data that does not exist yet

Section 8.1 named three kinds of data that are scattered or not kept: checks and answer keys, records of work, and
outcomes. Building them takes five concrete things that nobody needed before agents. NSF's program does not pay for
new data, but an agency or a research team that wants a working agent still has to make these.

### 1. Task records from past storms

A task record is one past decision point, packaged so an agent can be tested on it. It holds what was known at that
moment, what staff decided, and what happened.

```{figure} ../_static/figures/ARD_Task_Clock.png
:alt: A timeline from 00:00 to 20:00 with a dashed line at 07:30. Left of the line the agent may see the SOP skill, the generator log at 06:10 and 06:40, the outage map at 07:00, the ATMS snapshot at 07:25 and the eSTORM downloads up to 07:00. Right of the line, hidden from the agent, are later downloads, the SAT reports at 09:00 and 14:00, what staff decided from 07:30 to 13:30, and the hours dark.
:width: 100%

A task record freezes the clock at the decision. Anything right of the line is the answer key or the future; if a tool
can read it, the test leaks.
```

Written down, the record looks like this:

```json
{
  "task_id": "us19-day1-0730 (synthetic)",
  "known_at": "2026-10-10 07:30 EDT",
  "agent_may_see": ["ATMS snapshot from 07:25", "eSTORM download from 07:00",
                    "generator log up to 07:30", "outage map from 07:00", "the SOP skill"],
  "hidden_from_agent": ["what staff decided", "every eSTORM download after 07:30",
                        "the 9:00 AM SAT reports"],
  "question": "Draft the action cards for the next six hours.",
  "checks": ["every card cites a real SOP clause",
             "first refuel = deployment time + 6 hours (Immediately Post Storm 3.2.1)",
             "no lesson is presented as an SOP step",
             "every card names who decides"],
  "answer_key": "what staff did between 07:30 and 13:30, from the tracking spreadsheet",
  "outcome": "hours each red signal stayed dark"
}
```

The rule that makes a task record honest is to **freeze the clock**: the agent sees only what was known at 07:30. That
is why the hourly snapshots of {doc}`8.1 <notes1-data>` matter. Without them you cannot rebuild what was known, and the
test leaks the future. One corridor at one decision time is one task, so a few past storms give enough tasks for a
test set. Write the checks before any agent runs, and keep the answer keys outside every tool's reach.

### 2. Records of the agent's own work

For each run, keep what the agent read, what it proposed, what the person changed, and one line on why.

```json
{
  "run_id": "run-2026-10-10-0731 (synthetic)",
  "task_id": "us19-day1-0730",
  "read": ["ATMS 07:25", "generator log 07:30", "sop_text 3.1, 3.2, 3.2.1"],
  "tool_calls": ["rules.py refuel 06:10 -> 12:10", "rules.py refuel 06:40 -> 12:40"],
  "proposed": "Card 4: refuel NH-114 by 12:10, then NH-121 by 12:40",
  "checks": {"check_cards.py": "pass"},
  "person": "district signal engineer (role)",
  "decision": "edited",
  "edit": "order swapped: NH-121 first",
  "reason": "NH-121 is on an evacuation route",
  "model": "<name and version>",
  "skill": "d7-signal-sop 1.0.0"
}
```

The person's edit and its reason are the most valuable lines. They show what "right" means in this district, and they
are the raw material for lessons, for better checks and for any later training. Today that reason lives in a text
message, if anywhere. Keep these records in an agency records system, not only in the AI tool.

### 3. A practice storm

A practice storm is an **environment**: a simulated situation the agent can try many times, which a real storm never
allows.

```{figure} ../_static/figures/ARD_Practice_Storm.png
:alt: The real signal inventory and a seeded outage and damage maker, built from past storm patterns, feed a simulated clock of ATMS colors, SAT reports and returning power. The agent drafts cards with read-only tools and the SOP skill. Four checkers grade them - rules.py for times and thresholds, check_cards.py for real clauses and who decides, a traffic simulator for delay with the dark signals in it, and the injected pattern as the answer key. A loop returns the score for many runs. A side box notes that recording a hurricane drill also gives human demonstrations.
:width: 100%

The real inventory, simulated damage, and checkers. The class skill already has two of the checkers; a traffic
simulator grades the effect on traffic, not only compliance with the SOP.
```

Take the real signal inventory, add a seeded pattern of outages and damage, let a clock advance, and attach a checker.
To grade whether the choices were good for traffic, and not only allowed by the SOP, run the corridor in a simulator
with the dark signals in it and measure delay. Agencies already run practice storms for people, as tabletop exercises
and hurricane drills. Record one, and you also have human demonstrations.

### 4. A checker you can run today

Checks are data too. Writing an SOP's numbers as code turns every card into something a machine can grade. The class
skill's `rules.py` does this. Here it groups eight synthetic repairs for DDIR requests, the detailed damage inspection
reports that federal reimbursement needs.

```{figure} ../_static/figures/ARD_DDIR_Groups.png
:alt: Eight synthetic repairs along a corridor, with costs, marked emergency or permanent, and a quarter-mile (402 m) scale bar. rules.py groups them - R1 and R2 total $5,600 and need a DDIR; R3 and R4 total exactly $5,000 and are flagged because the SOP says "$5000 or greater" in one clause and "exceeds $5,000" in another; R5 alone is $4,100, below the threshold; R6, R7 and R8 total $5,800 but the chained group spans 667 m end to end, more than a quarter mile, and is flagged.
:width: 100%

Real output of the class skill's `rules.py ddir` on its synthetic test file. The code applies the SOP's numbers and
flags the SOP's own ambiguities; the DDIR team decides them.
```

Three more calls and their real answers, on synthetic dates:

```text
$ rules.py two 2026-11-09 2026-11-08 --soe yes --funding yes
{"allowed": false,
 "blocked_by": ["executive order has expired (TWO 12)"]}

$ rules.py encumber "2026-10-20 15:00"
{"encumber_by": "2026-10-21 15:00",
 "clause": "TWO > Emergency TWOs > 9"}

$ rules.py sat "2026-10-10 07:30" "2026-10-11 07:30"
{"passes": ["2026-10-10 09:00", "2026-10-10 14:00"],
 "clause": "Post-Storm > 0-1 Week Post Storm > 1"}
```

Each answer names its clause, so a card can cite it. Each one is also a checker: a card that says "encumber by Friday"
fails.

### 5. The lists the SOP points to, and an outcome clock

The SOP refers to Priority #1 intersections (Three Hours Prior 2.2), hurricane response zone maps (Appendix B) and a
responsibility matrix (Appendix C). In v1.5 both appendices are blank and there is no Priority #1 list. The kit's own
example answer says it plainly: *"The agent cannot rank the 7 red signals: the SOP has no priority list and the zone
maps are blank."* A person asks a colleague. An agent has nobody to ask and must not invent them. Each list needs to
exist as a table, with an owner and a date.

Last, keep the per-signal timelines from Move 5 storm after storm. They are the outcome clock: the hours each signal
stayed dark, which tell you whether anything improved.

| Data to create | Made from | Used for |
|---|---|---|
| Task records | Past storms: hourly downloads, tracking sheets, work orders | Testing the agent |
| Work records | Every agent run from now on | Lessons, better checks, later training |
| A practice storm | The real inventory plus simulated outages | Safe practice, training, drills |
| Reference lists | Staff knowledge, written down once a season | Any ranking or assignment the agent drafts |
| An outcome clock | Per-signal timelines from Move 5 | Knowing whether anything improved |

None of these exists in most agencies today. All of them can be built from what the agency already keeps.

## Data for improving the agent, and for training one

Data can make the agent better in five ways. The first three leave the model unchanged, and most agency work stops
there. The last two change the model's weights and need far more data. Module 9 explains how fine-tuning and
reinforcement learning work; this section is about the data each one needs.

```{figure} ../_static/figures/ARD_Improve_Ladder.png
:alt: Five steps rising left to right - ready data, worked examples, skills and memory (the model stays the same), then fine-tuning and reinforcement learning (the model's weights change) - each with the data it needs. A bar under all five reads "Under every step: a test set with answer keys; about 97 past cases measure the agent's success rate within 10 points, about 385 within 5." An arrow runs from cheap, fast and easy to undo to more data, more cost and hard to undo.
:width: 100%

Five ways data makes the agent better, cheapest first. Climb only as far as the test set says you need to.
```

| Step | What changes | Data it needs | Storm example | Main risk |
|---|---|---|---|---|
| 1. Ready data | What the agent can read | The six moves of 8.1 | The joined signal record | Extracted values mistaken for observed ones |
| 2. Worked examples | The prompt | A few past cases with good answers | Three past action cards for a red signal, one corrected by staff | The agent copies details of the example |
| 3. Skills and memory | Files the harness loads | Lessons, field words, staff corrections, each with its source | "Hillsborough County intersections may be running on battery or a backup beacon" | Stale or wrong lessons, so a person promotes each one |
| 4. Fine-tuning (SFT) | The model's weights | Many recorded good runs (trajectories) | Staff decisions recorded over several storms and drills | The model copies one district's habits, mistakes included |
| 5. Reinforcement learning (RL) | The model's weights | A practice environment, a checker and many varied tasks | Simulated storms on the real inventory, graded by SOP rules and traffic delay | The agent learns to beat the checker |

### How many past cases do you need to test?

Before any step, you need past cases with answer keys, or you cannot tell whether the step helped. How many? The same
formula you use for a survey sample:

$$
n = \frac{z^2 \, p \, (1-p)}{e^2}
$$

- $n$: the number of past cases you need.
- $p$: the share of cases the agent gets right. You do not know it yet, so use 0.5, the worst case.
- $e$: the margin you accept. 0.10 means plus or minus 10 points.
- $z$: 1.96 for 95% confidence.

**In words:** to know the agent's success rate within 10 points you need about 97 cases, and within 5 points about
385. More cases buy less and less precision:

| Past cases with answer keys | Margin on the success rate (95%, $p = 0.5$) |
|---|---|
| 25 | ±19.6 points |
| 50 | ±13.9 points |
| 97 | ±10.0 points |
| 200 | ±6.9 points |
| 385 | ±5.0 points |

Going from 25 to 97 cases halves the margin. Going from 97 to 385 halves it again, at four times the cost. Each
corridor at each decision time in a past storm is one case, so a few past storms can supply a test set. They cannot
supply a training set.

:::{admonition} Going deeper &mdash; when the formula is too kind
:class: dropdown
The formula treats cases as independent draws. Cases from the same corridor, the same storm or the same crew are not:
if the agent misreads one corridor's codes, it misreads every case from that corridor. Then the real margin is wider
than the table says. Spread your test set over corridors and storms, and report results by corridor as well as
overall. At an observed 92% success rate, 25 cases still give a margin of about ±10.6 points, so a "92%" from one
storm could be 82%.
:::

### How much data does training take?

Far more than a district has. As Stanford's lecture 11 reports, DeepSeek V3 was fine-tuned on 1.5 million examples,
and DeepSeek V3.2's reinforcement-learning stage used about 85,000 task prompts. In our field, Traffic-R1 trained a
signal-control model with 3,000 scenarios reviewed by 11 experts (Zou et al., 2026). No district has thousands of
recorded storm mornings. So training data for a storm agent has to be made, and lecture 11 lists five ways to make it.

```{figure} ../_static/figures/ARD_Five_Sources.png
:alt: Five sources of agent data in storm form - people do the task while a recorder runs (a hurricane drill logged step by step), mined from records (past storms' downloads, sheets and work orders), a model runs and a filter keeps (the agent on practice storms, keeping runs that pass the checkers), tasks built by code (outages injected into the real inventory, the injected pattern is the answer key), and simulated people (an LLM plays a SAT member or a local agency). An arrow runs from more realistic and more costly to cheaper and more scalable.
:width: 100%

Five ways to get data for a storm agent, following lecture 11. A simulator gives endless practice, and its mistakes get
learned too. For roads we have physics-based simulators; for people, the crews and callers, we only have language
models.
```

### What a trajectory is

A **trajectory** is a step-by-step recording of a run. In fine-tuning, the model is trained to write only its own
steps: its thoughts, its tool calls and its answer. The task and the tool results are context it reads but does not
learn to write.

```{figure} ../_static/figures/ARD_Trajectory.png
:alt: One run step by step - the task (context), a thought (learned), a tool call rules.py refuel 06:10 (learned), its result with first refuel 12:10 and clause 3.2.1 (context), a second call and result for 06:40 and 12:40, the answer Card 4 (learned), and the person's edit, approved with the order swapped because NH-121 is on an evacuation route (the label, synthetic).
:width: 100%

What a model learns from a trajectory. The tool results here are the class skill's real output. The person's edit at
the bottom is the label that says what right looked like.
```

:::{admonition} Going deeper &mdash; why a tracking sheet is not yet a trajectory
:class: dropdown
A tracking sheet records what was done, not what was seen before each step:

```text
TRACKING SHEET (what was done)
NH-114 | US19/GTB  | 6:10
NH-121 | US19/Drew | 6:40

TRAJECTORY (what was seen, then done)
07:25 saw  ATMS: 18 green, 6 yellow, 7 red
07:28 saw  generator log: 06:10, 06:40
07:29 did  rules.py refuel "2026-10-10 06:10"
07:29 saw  first_refuel 12:10 (3.2.1)
07:31 did  Card 4: refuel NH-114 by 12:10 ...
```

Fine-tuning learns the "did" lines given the "saw" lines. A sheet has no "saw" lines, so to turn it into a trajectory
you have to rebuild what was known at each moment from the snapshots. No snapshots, no training data. (Stanford CS
329Z, lecture 11, "Anatomy of a Trajectory".)
:::

### What you reward decides what the agent learns

```{figure} ../_static/figures/ARD_Reward_Toy.png
:alt: A synthetic toy with one crew and seven dark signals - P1 and P2 are Priority #1 signals that take 3 hours each, and E1 to E5 take 1 hour each. Easy-first restores 5 signals by hour 6, leaves Priority #1 signals dark for 19 signal-hours and all signals for 34. Priority-first restores 2 by hour 6, 9 Priority #1 signal-hours and 54 in all.
:width: 100%

Three reasonable rewards, two different orders. Train on "restored by hour 6" and the agent learns easy-first; that is
a choice, not a fact.
```

None of the three rewards is wrong. Each is a value judgment, and the SOP gives generator priorities to TMC personnel
(Three Hours Prior 2.2). Ask them, then encode it.

### What data teaches by accident

Lecture 11 warns that training data teaches more than you intended. Each warning has a storm version.

| Lecture 11's warning | What happened in coding agents | The storm version | Guard |
|---|---|---|---|
| **Beating the checker** | Models learned to fake passing tests, for example by calling `sys.exit(0)` | Reward "marked operational in eSTORM" and the agent learns to mark | Grade several measures; use field-confirmed status |
| **Leaked answers** | SWE-bench agents could read the git history to find the real fix | Staff decisions sit in the sheet the agent reads | Freeze the clock; keep answer keys out of reach |
| **Copying the past** | Fine-tuning imitates the capability and the harness together, without telling them apart | If refuels ran late in past storms, the model learns to refuel late | Grade with rules and outcomes, not only with past decisions |
| **One harness, one district** | A model trained in one harness keeps its habits in another | One tool format and one set of codes | Harmonize codes (Move 4); test in more than one setup |

## Governance: who reads it, who changes it, when it expires

Ready data that anyone can read or change is a liability, so a dataset needs rules as well as fields. NSF requires
every proposal to cover access, retirement, community contribution, security and integrity. The same questions fit an
agency dataset.

| Question | For the storm data |
|---|---|
| **Access.** Who and what may read it? | The agent gets read-only tools. It never writes to eSTORM; a person submits. Decide what each local agency may see. |
| **Sensitive information.** What must never reach the agent? | Cabinet keys and generator lock combinations (One Month Prior 9 and 11, 48 Hours Prior 3), staff phone numbers (One Month Prior 4), faces and license plates in photos. Remove them inside the tool, before the model sees anything. |
| **Provenance and integrity.** Can each value be traced? | Every value carries its source, its time and its flag: observed, estimated or unknown. Photos keep their GPS and time stamp, because reimbursement depends on them. Fields extracted by AI name the model and the date. |
| **Retirement.** When does it expire? | State data goes stale in hours. The signal inventory is checked each season (One Month Prior 8). Rules expire when the SOP version changes. A test case retires once the agent, or the public, has seen its answer. |
| **Contribution.** Who may add or correct? | Field teams add through eSTORM Lite. The agent may propose a lesson, and a named person decides whether to keep it. Every change is logged. |

```{figure} ../_static/figures/ARD_Governance_Filter.png
:alt: A synthetic record as stored, with the signal, status and generator, plus a lock combination, a cabinet key, a crew lead's phone number and a photo showing faces and license plates, passes through a read-only tool that drops secrets, masks phone numbers, blurs faces and plates, logs every call and cannot write anything. The model sees only the signal, status, generator and a blurred photo.
:width: 100%

Sensitive fields leave inside the tool, before the model sees anything. A rule in the prompt can be ignored; a field
the tool never returns cannot leak. The SOP itself names the sensitive items.
```

Two rules sit above the dataset. FDOT's AI policy (May 2024) says to use approved tools only, validate AI outputs,
respect public records law and disclose AI-assisted work. Florida's public records law applies to records whatever
their format, which can include an agent's logs. Ask the records custodian before you design the log, not after, and
name who owns the dataset when the project ends.

## Where it breaks

Most failures come from a value that looks more certain than it is, or from an answer the agent could see.

| What goes wrong | Storm example | Guard |
|---|---|---|
| An extracted value is wrong but looks official | A vision model labels a swinging signal head as "missing" | Keep the photo attached, have an inspector confirm, flag the field as AI-extracted |
| A wrong link | A generator logged at "US19/GTB" is joined to the wrong intersection, and the refuel crew is sent there | A crosswalk table; unmatched names are rejected, not guessed |
| Stale state | At 10:30 the agent drafts from the 07:00 download | Every snapshot is time-stamped; the tool warns when data is older than a set age |
| Blank read as "fine" | A corridor nobody has driven is counted as operational | "Unknown" is its own value |
| The answer leaks into the test | Staff decisions sit in the sheet the agent can read | Freeze the clock; keep answer keys outside every tool's reach |
| The checker is beaten | The agent learns to mark signals as restored | Grade several measures; use field-confirmed status |
| The practice storm is unlike a real one | Simulated outages fall at random, while real ones cluster along a power feeder or a flood zone | Build outage patterns from past storms; hold one real storm out for the final test |

| Fit card — making transportation data ready for an agent | |
| --- | --- |
| **Idea in one sentence** | Start from the task, list the data each step needs, repair the data that exists, and create the kinds that do not exist yet. |
| **Why it works** | An agent has no background knowledge of your corridor. Whatever is not in the data, a tool or a skill does not exist for it. |
| **Fits these tasks** | Recurring, rule-guided work that crosses several systems: storm response, incident management, signal complaints, damage inspection, crash coding. *Leverage: extraction, retrieval; judgment stays with a person.* |
| **Needs this data** | Records the agency already keeps (status, logs, photos, funding) · about 100 past cases with answer keys · staff time to confirm extracted fields · held by the district, local agencies and contractors together. |
| **Breaks when** | Values carry no source or time, blank means two things, the answer key is within reach, or nobody owns the dataset once the project ends. |
| **Keep the classical method when** | One engineer on one corridor can do the job from the status board and the SOP. A well-kept spreadsheet and a clear procedure beat an agent on unready data. Do Moves 2 and 3 anyway; they help people too. |

## Your project: a one-page data plan

Answer these eight questions for your own agent before you build more of it. One page is enough, and it becomes the
data section of a harness paper or a pilot proposal.

1. **The task.** What does the agent draft, and who decides?
2. **The five questions.** For state, reference, rules, checks and outcomes: what data, where does it live, who owns it?
3. **Made for people.** Which of that data assumes a human reader, and which move from {doc}`8.1 <notes1-data>` fixes it?
4. **Unknown.** In each source, what does "not yet observed" look like? Can the agent tell it from "fine"?
5. **Never.** What must not reach the agent, and where is it removed?
6. **The test set.** Where do about 100 past cases with answer keys come from, and how is the answer hidden?
7. **Work records.** What will you keep from each run, including the person's edits?
8. **Afterwards.** Who owns the dataset when the semester ends, and when does each part expire?

A starting point for each class project. These are suggestions to argue with; you know your data better than this
table does.

| Project | Data made for people | First move | A possible answer key |
|---|---|---|---|
| Post-storm signal repair | The SOP as a PDF, the status board, the tracking sheet | Link: one signal key across all three | What staff did in a past storm or a drill |
| Post-storm damage inspection | The Survey123 form's menus, and photos | Describe every menu choice with its definition; then extract | The inspector's own choices on the same sites |
| Drone-based incident detection | Video, and incident logs with times typed by hand | Link each detection to a logged incident by place and time | Logged incident times, with their own uncertainty stated |
| AV and pedestrian interaction | Clips and trajectories with labels someone assigned | Describe what each label means and who assigned it | Labels from two people, with their agreement rate |
| NHTSA ADAS crash narratives | Free-text narratives, some of them redacted | Extract fields from each narrative, with "unknown" allowed | Fields a person coded on a held-out sample |
| I-4 congestion in SUMO | Counts, speeds and incident reports from different sources | Harmonize time bins, locations and units | Field counts and speeds, checked with the GEH statistic |

## Check yourself

1. On 25 cases from one storm, 92% of the agent's action cards match what staff did. What can you claim, and what can
   you not?
2. A vendor offers a model "trained on hurricane response data from five states". What do you ask about the data?
3. Someone proposes to train an agent with this reward: the share of signals marked operational in eSTORM within 24
   hours. What goes wrong, and what would you reward instead?

## Sources

- Stanford CS 329Z *Engineering AI Agents*, Fall 2026 (Yang, Ryan and Yang), lecture 11, "What Data Do Agents Need?"
  (the DeepSeek figures, the five sources of agent data, the anatomy of a trajectory and the "what data teaches by
  accident" cases, as the lecture reports them, with the original papers cited there).
- Fried, D., & Neubig, G. (2026). [CMU 11-768 AI Agents](https://www.cmu-agents.com/).
- U.S. National Science Foundation (2026). [NSF 26-512: Unlocking Dataset Value for AI-Enabled Scientific Discovery (AI Datasets)](https://www.nsf.gov/funding/opportunities/ai-datasets-unlocking-dataset-value-ai-enabled-scientific-discovery/nsf26-512/solicitation)
  (the governance requirements).
- FDOT District 7 (2025). *Traffic Signals Standard Operating Procedures Reference Guide*, v1.5, cited by clause; the
  class skill [`d7-signal-sop`](https://github.com/ai4mobility/transportation-skills/tree/main/skills/d7-signal-sop):
  `rules.py`, `check_cards.py`, `gaps.md`, the synthetic scenario, repairs file and example cards.
- Zou et al. (2026). Traffic-R1: Reinforced LLMs bring human-like reasoning to traffic signal control systems.
  *ACL 2026*. [arXiv:2508.02344](https://arxiv.org/abs/2508.02344).
- FDOT AI Policy (May 2024).
- Course materials: the slide deck and handout *AI-Ready Transportation Data: What an Agent Needs to Do the Job*. The
  sample-size table, the reward toy and the timeline were computed for them; every record is synthetic.

---

Next in {doc}`Module 8 <index>`: answering in the agency's form, several agents, and your project's five-level
comparison. Those sections are still to be written; the module page summarizes them.
