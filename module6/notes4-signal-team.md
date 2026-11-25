(signal-ops-team)=
# 6.4 One agent or a team: the hurricane signal SOP with a lead and desks

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 6 &middot; Section 6.4</span>
    <span class="notes-card-session">Session: Agents working together (worked example, continued from 6.3)</span>
  </div>
  <p class="notes-card-lede">Section 6.3 built one agent that runs FDOT District 7's hurricane traffic signal SOP. A real traffic management center does not work as one person: it directs assessment teams, generator teams and fuel trucks. This section rebuilds the same agent as a team, a lead agent with several desk agents, in two different ways, and runs all three designs on the same simulated storms. You will see how a team of agents is wired, what it gained, what it cost, where it failed, and how little a single run can tell you.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Read it first</h4>
      <ul>
      <li><a href="notes3-signal-agent.html">6.3 A worked agent</a> (the storm, the SOP, the tools and skills)</li>
      <li><a href="../module5/notes5-architectures.html">5.4 Agent architectures</a> (question 3: one agent or a team)</li>
      </ul>
    </div>
    <div>
      <h4>Used again in</h4>
      <ul>
      <li><a href="../module7/notes1-context.html">7.1 Context: what the model reads</a> (each desk reads only its own part)</li>
      <li><a href="../module8/index.html">Module 8</a> (agents at work in an agency)</li>
      </ul>
    </div>
  </div>
</div>

## What this section covers

- The question: when is a team of agents worth it for an agency operation
- Two ways to cut the same work, and how to count what each cut breaks
- One planning moment of a team: brief, plan, report, merge, send
- The experiment: three designs on the same storms, with and without a model
- What the runs show, and what they cannot show
- Where a team breaks, the fit card, and what to take to your project

## The question: the TMC already works as a team

After a hurricane, the District 7 SOP has the traffic management center (TMC) direct three kinds of crews: Situational
Awareness Teams (SAT) that drive the corridors and report what each signal is doing, generator teams that connect
generators and set out flashing beacons, and fuel trucks that keep the generators running. In 6.3 one agent planned the
generator teams, and the other crews followed fixed rules.

That raises a design question you will meet in any agent project for an agency: **should one agent plan everything, or
should each crew type, or each area, get its own agent, with a lead agent that coordinates them?** Section 5.4 gave the
rule of thumb from the published guides: use one agent as far as it goes, and split a task only when its parts do not
depend on each other. This section tests that rule on a real procedure, with numbers.

Emergency management already has words for the two obvious ways to split. The Incident Command System (ICS) calls a unit
organized by function a **group** and a unit organized by area a **division**. We build both.

## Two ways to cut the same work

```{figure} ../_static/figures/SOT_Two_Cuts.png
:alt: Three panels. One agent: a TMC desk agent plans 6 generator teams, 5 SAT teams and 2 fuel trucks; 100 percent of linked jobs stay inside one agent. Team by job: a TMC lead agent over a SAT desk, a generator desk and a fuel desk, each with its own crews; 17 percent. Team by zone: a TMC lead agent over four zone desks, each with the SAT and generator teams of its own zone, and a fuel and yards desk with 2 fuel trucks; 29 percent.
:width: 100%

The same 13 crews, planned three ways. The bar under each design is the share of linked jobs that one agent can handle alone, with no message to another agent.
```

- **One agent.** The agent of 6.3, now also planning the SAT loops and the refueling, so that all three designs control
  the same things.
- **Team by job** (an ICS group). A lead agent and three desk agents: a SAT desk, a generator desk and a fuel desk.
- **Team by zone** (an ICS division). A lead agent, one desk agent per zone (zones 4 and 5 share one), and a fuel and
  yards desk. A zone desk plans the SAT teams and the generator teams of its own zone and sees only its own signals.

### Count the links before you cut

Two jobs are **linked** when the second needs what the first produced. A SAT report tells a generator team where to
go. A connected generator needs a refuel six hours later. If both jobs belong to the same agent, no message is needed.
If they belong to different agents, the information has to travel, and it can be late, garbled or lost.

You can count these links before building anything. We ran three moderate storms with the simulator's built-in rule (no
model) and counted every linked pair of jobs, then asked on which side of each cut the two jobs fall.

| Link between two jobs | Links | Inside one desk, job cut | Inside one desk, zone cut |
|---|---|---|---|
| SAT report &rarr; a generator team's stop | 288 | 0 (0%) | 271 (94%) |
| Signal system or outage map &rarr; a stop | 326 | 326 (100%) | 326 (100%) |
| A team's own earlier visit &rarr; a stop | 17 | 17 (100%) | 17 (100%) |
| Generator connected &rarr; its refuels | 1,452 | 0 (0%) | 0 (0%) |
| Yard &rarr; trailer | 22 | 22 (100%) | 0 (0%) |
| **All** | **2,105** | **365 (17%)** | **614 (29%)** |

The zone cut keeps SAT and generator work together. Neither cut keeps generators and fuel together, because two fuel
trucks serve all five zones. So before any run we expect the job cut to have trouble with fuel, and both teams to lean
on the lead to carry messages.

You have seen this idea in signal systems. Intersections that are close together, with strong platoon flow between
them, go into one coordinated section, and the section boundary goes where the coupling is weak. Cutting an operation
among agents follows the same logic: put the boundary where few jobs depend on each other.

## One planning moment of a team

```{figure} ../_static/figures/SOT_Team_Turn.png
:alt: Four lanes: person on shift, TMC lead agent, desk agents, crews in the field. Step 1, the lead reads the signal system, eSTORM and what the TMC knows. Step 2, the lead briefs each desk: objective, crews it owns, signals to hold, yard share. Step 3, each desk plans its own crews at the same time: SAT loops; generators and beacons, checked; refueling. Step 4, each desk reports what it planned, what it could not cover, and requests to other desks. Step 5, the lead merges the parts into one plan, runs the plan checker, sends the plan and writes the status memo. The person on shift says yes or no to a team move and to a Priority 1 shortage. Only the lead sends to the 13 crews. A dashed line shows that a request to another desk reaches it in the lead's next brief. Kept in code: one owner per crew, one writer to the field, a person decides, a scripted fallback for every desk.
:width: 100%

One planning moment. The lead never plans a route and a desk never sends anything to the field.
```

At each planning moment the team takes one turn:

1. **The lead reads** the situation, as the single agent did.
2. **The lead briefs each desk**: its objective, the crews it owns, signals to hold out of the plan, and its share of
   the yard stock.
3. **Each desk plans its own crews**, at the same time as the other desks, with its own short list of tools. A generator
   desk runs the optimizer and the plan checker on its part.
4. **Each desk reports** to the lead: what it planned, what it could not cover, and any request for another desk.
5. **The lead merges** the parts into one plan, runs the plan checker on the whole, asks the person on shift where the
   SOP gives the decision to a person, sends the plan, and writes the status memo.

Four rules are kept in code, as in 6.3, so that no agent can talk its way around them:

- **One owner per crew.** Every crew belongs to exactly one desk. A desk that tries to plan another desk's crew is refused.
- **One writer to the field.** Only the lead can send a plan, and only a plan the checker passed.
- **A person decides** what the SOP gives to a person: moving a team to another zone, and what to do about a Priority 1
  signal that cannot be covered today.
- **A scripted fallback for every desk.** If a desk agent fails or runs out of time, a fixed procedure finishes its part.

Two design choices deserve a second look. **Desks talk only through the lead.** A request from the generator desk to the
fuel desk travels in the generator desk's report and reaches the fuel desk in the lead's next brief. That is slower than
a direct message, but every message is on record and one agent sees them all. **When the lead cannot be reached**, each
desk keeps working under its last brief, as standing orders, and its own checked part goes to its crews. Nobody merges
plans, moves a team or writes the memo. The steps of both roles are written in one new skill, `signal-ops-team-handoff`.

## The experiment

All three designs got the same storms, the same tools and skills, the same person script and the same model, Claude
Sonnet 5.5. Three conditions:

- **Moderate storm**, outages spread over the area (two storms).
- **Severe storm** that hits zone 3 hardest (one storm).
- **Moderate storm with the lead silent** from hour 4 to hour 10 (two storms). For one agent this means nobody plans in
  those hours.

That is 15 runs with the model. Each design was also run with **fixed choices in place of the model** on three storms
per condition (27 runs), to see what the wiring does by itself.

## Interactive companion

The replay map from 6.3 now holds six runs of this study. Open it, set **Compare** to *One agent or a team*, pick
*Team by job* or *Team by zone*, press play, and scroll below the map to **How the agents worked together**.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion &mdash; After the storm: one agent, a team by job and a team by zone on the same storm</span>
    <a href="../_static/companions/Signal_Ops_After_Storm.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/Signal_Ops_After_Storm.html"
          title="After the storm: one agent or a team of agents" loading="lazy"></iframe>
</div>

What to look at:

- **The graph.** The person on shift, the lead, the desks and the crews. Green arrows are briefs, blue arrows are
  reports, dashed lines are requests. Gray bars are the links between two desks from the count above.
- **Step through one planning moment** with the *Step* buttons, then click a desk to read its brief, the tools it
  called, its report and its requests.
- **The whole run** adds the messages up. On the zone team's run, desks sent 383 requests to the lead and 81 to another
  desk.
- **The same, lead silent.** Move the clock to hour 6. The lead turns gray, each desk shows how old its brief is, and
  requests turn red because nobody received them.

## What the runs show

Means per run, Claude Sonnet 5.5: two storms for the moderate and lead-silent conditions, one storm for the severe
condition. Lower risk is better.

| Condition | Design | Risk score | Priority 1 dark hours at night | Times a generator ran dry | Questions to the person | Tokens and cost per run |
|---|---|---|---|---|---|---|
| Moderate | One agent | 8,111 | 0.0 | 4.0 | 6 | 3.8 M, $2.1 |
| | Team by job | 7,618 | 0.0 | 7.5 | 16 | 10.1 M, $8.0 |
| | Team by zone | 7,542 | 5.3 | 0.5 | 23 | 18.4 M, $13.6 |
| Severe, zone 3 | One agent | 18,212 | 0.0 | 1 | 4 | 5.9 M, $3.3 |
| | Team by job | 18,274 | 0.0 | 4 | 20 | 11.9 M, $9.5 |
| | Team by zone | 17,923 | 7.6 | 5 | 21 | 21.8 M, $15.7 |
| Moderate, lead silent | One agent | 8,338 | 0.1 | 4.0 | 7.5 | 4.5 M, $2.5 |
| | Team by job | 8,666 | 34.5 | 3.5 | 44 | 12.3 M, $9.8 |
| | Team by zone | 7,756 | 6.0 | 1.0 | 27.5 | 18.1 M, $13.3 |

**1. On the moderate storm both teams scored lower in risk, at several times the cost.** The team by job was 6% lower
and the team by zone 7% lower than one agent, for 2.7 and 4.9 times the tokens. On the severe storm the three designs
are within 2% of each other. A likely reason: with far more dark signals than generators, equipment is the limit, not
coordination.

**2. Is a gap of 6 to 7% real? Repeat the run and see.** A model does not give the same answer twice. We ran the
one-agent design four times on storm 1 with the same settings.

```{figure} ../_static/figures/SOT_Repeats.png
:alt: Dot plot of risk score on storm 1. One agent, four runs: 8,318, 8,420, 8,649 and 8,821, mean 8,552, standard deviation 226 or 2.6 percent. Team by job, one run: 7,739, 9.5 percent below the one-agent mean. Team by zone, one run: 7,835, 8.4 percent below the one-agent mean.
:width: 100%

Four runs of the same design on the same storm differ by up to 6%. Both team runs still sit below all four.
```

The four one-agent runs have a standard deviation of 2.6%, and the two team runs are more than three standard
deviations below their mean. So on this storm the gap is larger than the one-agent design's own noise. The team runs
were made once each, so their own noise is not measured.

**3. The two teams gained in different places.**

```{figure} ../_static/figures/SOT_Risk_By_Priority.png
:alt: Three panels of bars for storm 1. Priority 1 signals: one agent 2,513, team by job 1,473 (41 percent lower), team by zone 2,316 (8 percent lower). Priority 2 signals: one agent 3,938, team by job 3,867 (2 percent lower), team by zone 3,329 (15 percent lower). Priority 3 signals: one agent 2,100, team by job 2,399 (14 percent higher), team by zone 2,190 (4 percent higher).
:width: 100%

The team by job gained at Priority 1 signals and paid at Priority 3. The team by zone gained at Priority 2.
```

The team by job had every Priority 1 signal on a generator or on utility power by hour 56. Every other run needed until
hour 110. It paid for that with more dark hours at Priority 3 signals, and its generators ran dry 11 times.

**4. The desks did their side jobs; the single agent let them slide.** This is the clearest difference in behavior
(storm 1):

| What the agents did in one run | One agent (4 runs) | Team by job | Team by zone |
|---|---|---|---|
| SAT loop plans set | 1 to 4 | 35 | 37 |
| Refueling plans set | 5 to 12 | 35 | 37 |
| Questions to the person | 5 to 9 | 21 | 20 |
| Largest context of any one agent, tokens (mean of two storms) | 23,900 | 24,600 | 25,500 |

One agent that holds every tool followed the main procedure, the generator plan, and rarely touched the SAT loops or the
refueling. A desk with one job did that job at every planning moment. Note the last row: no agent in any design read
more than about 30,000 tokens at once. The usual argument for a team, that one agent's context gets too full, does not
apply at 245 signals. Here the gain came from **attention**, not from relieving the context.

**5. The cut decided what happened when the lead was lost.** Against its own moderate runs, risk rose 3% for one
agent, 3% for the team by zone, and 14% for the team by job, which also left Priority 1 signals dark for 34.5 hours at
night. On storm 1 the reason is visible in the companion. The lead's last brief before it went silent told the
generator desk to hold signal SIG-127, a dark Priority 1 signal, out of the plan. The desk kept that order as its
standing order for six hours. Every plan it made then failed the checker, because a dark Priority 1 signal got neither
a generator nor a beacon, and a plan with a FAIL cannot be sent. So no new generator or beacon stops went out at any
of the six silent planning moments. One stale order, kept faithfully, stopped the desk. The zone desks kept sending
their own parts.

**6. Without a model, the wiring adds little.** With fixed choices in place of the model (means of three storms):

| Condition | One agent | Team by job | Team by zone |
|---|---|---|---|
| Moderate | 7,641 | 7,641 | 7,602 |
| Severe, zone 3 | 20,584 | 20,636 | 19,050 |
| Moderate, lead silent | 7,865 | 7,633 | 7,554 |

The job cut equals one agent exactly on the moderate storm: with fixed choices it changes who makes each call, not what
is decided. So the job team's gain with Sonnet came from the model's choices. On the severe storm the zone cut is lower
in all three storms even without a model, likely because each zone desk gives the optimizer a smaller problem.

:::{admonition} Before you trust this result
**What is the baseline?** One agent with the same controls, tools, skills, person script and model; and each design with
fixed choices in place of the model. Compare a team with *both*, or you will credit the model for what the wiring did,
or the wiring for what the model did.

**How was the data split, and why is that honest?** There is no training here, and the skills were written before the
runs. But the evidence is thin: two storms at most per condition, one model, and one run per storm except for the four
one-agent runs on storm 1. Every number in the simulation is an assumption, not an FDOT figure.

**What does it do on the ugly cases?** Three of them. The person is a script that said yes to every open request (18 of
18 for the team by job), so a team that asks more gets more exceptions approved. The score is fragile: in the no-model
one-agent run on storm 1, changing only the optimizer's time limit from 2 to 10 seconds moved the risk score from 8,294
to 9,720, because two Priority 2 signals were left dark into day 4. And the team by zone left Priority 1 signals dark
at night in every condition, which one agent almost never did.
:::

## Where a team breaks

- **A cut through a strong link.** The job cut separates the generator desk from the fuel desk, and 1,452 links cross
  that line. It had the most dry generators on the moderate storm.
- **A network-wide rule with no owner.** "No Priority 1 signal dark at night" needs equipment to move between zones. A
  zone desk cannot do that alone, and the zone team missed it in every condition.
- **Standing orders go stale.** When the lead was out of reach, the generator desk of the job cut kept a six-hour-old
  hold on a Priority 1 signal and could send nothing. Decide before the storm how old an order may get, and which
  decisions a desk may take alone.
- **The person becomes the bottleneck.** Teams asked the person three to four times as many questions (44 per run for
  the team by job with the lead silent). A real shift lead cannot answer at that rate.
- **Cost and time.** Per run, 2.7 to 4.9 times the tokens, and about 50 seconds per planning moment against 21.
- **A request can go unanswered.** A desk's request reaches another desk only if the lead carries it. On the zone
  team's run, by a rough text match, most desk-to-desk requests did not show up in the lead's next brief to that desk.

| Fit card — a team of agents for an agency operation | |
| --- | --- |
| **Idea in one sentence** | A lead agent briefs several desk agents, each plans only the crews it owns, and the lead merges, checks and sends one plan. |
| **Why it works** | A desk with one job and a short tool list does that job at every planning moment; the rules that must hold stay in code; one agent sees every message. |
| **Fits these tasks** | Operations with several crew types or areas, a written procedure, and side jobs that one agent lets slide. *Leverage: judgment, extraction, generation.* |
| **Needs this data** | A record of which jobs depend on which, to count links across each cut; the procedure with its decision rights; a simulator or past events for repeated runs. |
| **Breaks when** | The cut crosses a strong link; a network-wide rule has no owner; the lead or the person is out of reach; one run is taken as proof. |
| **Keep the classical method when** | One agent with a checklist, or a fixed rule, already covers every job: without a model the three designs scored the same on the moderate storm. Try the checklist first. |

## Applications beyond this storm

- **Agency practice: traffic incident management.** A major crash already runs under unified command: law enforcement,
  fire, towing and the TMC each own their crews. A team of agents maps onto it directly, with the TMC as lead. Count the
  links first (a lane reopening depends on towing, towing on fire clearance). Data: CAD logs and TMC incident timelines.
  Baseline: the operator's checklist and one agent that follows it.
- **Agency practice: evacuation.** Contraflow, signal timing, fuel and shelter messaging are owned by different offices.
  The lead-silent test matters most here: communications fail in exactly these events, so standing orders must be written
  before the storm. Baseline: the written evacuation plan with its decision table.
- **Traffic flow research: control of a network by regions.** Regional controllers with a coordinator are the classical
  version of this design. The link count is the same question as choosing region boundaries. Data: detector counts and
  a simulator such as SUMO. Baseline: one centralized controller and fixed-time plans.

## For your project

- Start with one agent and a checklist that names every side job. Add desks only for the jobs it still lets slide.
- Before you cut, count the links: list which jobs need another job's output, and see how many cross each cut.
- Write down who owns each crew or resource, who may write to the outside world, and which decisions need a person.
  Put those in code.
- Test what happens when the lead, or the person, cannot be reached.
- Run every design more than once on the same case, and on more than one case, before you compare. Report the spread.
- Report the cost next to the gain: tokens, time, and the number of questions put to a person.

## Check yourself

1. Your district wants an agent team for hurricane signal operations and asks: by crew type or by zone? Using the link
   table, which would you propose for District 7, and what one change to the crews or the yards would change your answer?
2. The team by zone lowered the average risk and left Priority 1 signals dark at night. The team by job protected
   Priority 1 and let generators run dry 11 times. A TMC manager asks which is "better". What would you ask the manager before
   you answer?
3. A vendor shows you one storm where its five-agent system beats a single agent by 8%. List three things you would
   ask to see before you believe the 8% is caused by having five agents.
4. In these runs the gain came from desks doing their side jobs at every planning moment. Describe a cheaper design
   that might get the same gain with one agent, and the run you would make to test it.

## Sources

- FDOT District 7. *Traffic Signals Standard Operating Procedures Reference Guide*, v1.5 (June 2025). Clauses are
  paraphrased.
- The hurricane signal project of 6.3. The public
  [hurricane-signal-ops](https://github.com/ai4mobility/hurricane-signal-ops) repository holds the single agent; the
  team harness (`team_loop.py`), the skill `signal-ops-team-handoff`, the link count (`cut_links.py`) and the study
  runner (`study_teams.py`) are not published there yet. Runs of Nov 24, 2026: 15 runs and 3 repeats with Claude
  Sonnet 5.5, 27 runs with fixed choices, and 8 no-model runs that vary the optimizer's time limit.
- FEMA. *National Incident Management System*, 3rd edition (2017), for the Incident Command System terms group and
  division.
- Kim, Y., et al. (2025). [Towards a Science of Scaling Agent Systems](https://arxiv.org/abs/2512.08296). A controlled
  comparison of one agent with four team designs on benchmark tasks.
- Gao, M., et al. (2025). [Single-agent or Multi-agent Systems? Why Not Both?](https://arxiv.org/abs/2505.18286)
- In this course: {doc}`5.4 Agent architectures <../module5/notes5-architectures>`,
  {doc}`6.3 A worked agent <notes3-signal-agent>`.
- Agents unit credit: CMU 11-768 *AI Agents* (Fried and Neubig); Stanford CS 329Z *Engineering AI Agents*.

---

Next: {doc}`Module 7 <../module7/index>`, what an agent reads and remembers. Each desk in this section read only its own
part of the picture; Module 7 is about choosing what goes into that part.
