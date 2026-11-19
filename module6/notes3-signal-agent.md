(signal-ops-agent)=
# 6.3 A worked agent: running the hurricane signal SOP with tools and skills

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 6 &middot; Section 6.3</span>
    <span class="notes-card-session">Session: Skills, lecture 2 &mdash; building transportation skills (worked example)</span>
  </div>
  <p class="notes-card-lede">Sections 6.1 and 6.2 showed how a skill packages know-how. This section follows one project from start to finish: an AI agent that runs FDOT District 7's hurricane traffic signal SOP on a simulated storm in Tampa. You will see why the problem matters, how the SOP became tools, skills and a contract, how the agent works one planning moment at a time, and what three Claude models did with the same storm. Two companions let you watch the storm on a map and read every request the model was sent: the prompt, the history, the summary of its thinking, and each tool and skill it called.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Read it first</h4>
      <ul>
      <li><a href="../module5/notes2-loop.html">5.2 A model in a loop</a> (the harness and the loop)</li>
      <li><a href="../module5/notes3-tools.html">5.3 Tools: what an agent can reach</a></li>
      <li><a href="notes2-skills.html">6.2 Inside a skill</a> (the four homes for know-how)</li>
      </ul>
    </div>
    <div>
      <h4>Used again in</h4>
      <ul>
      <li><a href="../module7/notes1-context.html">7.1 Context: what the model reads</a> (the history grows request by request)</li>
      <li><a href="../module8/index.html">Module 8</a> (agents at work in an agency)</li>
      </ul>
    </div>
  </div>
</div>

## What this section covers

- The problem: dark signals after a hurricane, and an SOP that people run by hand
- A digital twin to test an agent on
- From the SOP to code, skills, tools, people and guesses, and the SOP as a contract
- The agent: one planning moment, eight steps, four guard rails
- Inside one turn: what the model was sent, what it called, and why
- What three models did with the same storm
- Where it breaks, the fit card, and what to take to your project

## The problem: dark signals after a hurricane

After a hurricane, hundreds of traffic signals lose power at once. A dark signal at night is a crash risk: drivers
come up on an unlit intersection with no signal and no warning. FDOT's first goal is not to repair every signal. It
is to make every intersection controlled again, with a generator that brings the signal back or at least a
flashing beacon, before night falls.

FDOT District 7 (Tampa Bay) writes down how to do this in its *Traffic Signals Standard Operating Procedures
Reference Guide* (v1.5, June 2025). Before landfall, the TMC splits the district into zones, assigns generator teams
and Situational Awareness Teams (SAT) to corridors, and decides whether generators go to Priority 1 intersections
only or to every dark signal in a zone. After the storm, the TMC reads the signal system, collects what SAT sees,
dispatches generators and fuel, keeps the generator records straight, and sends a daily status update.

Two things make this hard. The first is resources: a few dozen generators for a few hundred dark signals, a
handful of trucks, and fuel every six hours. The second is the picture. The TMC never sees the street directly. Red
in the signal system means "not working *or* not communicating". SAT reports come from temporary staff, some of whom
are new to signals, and arrive late or wrong. The utility's outage map lags. The TMC acts on what it believes, not on
what is true.

```{figure} ../_static/figures/SOA_Operation.png
:alt: Two panels. Before landfall, one turn about three hours out: read the zone map and the forecast, assign generator teams to zones, set corridor routes for teams and SAT, compare both team rules in simulated storms, a person picks the team rule, check and issue the deployment sheet. After the all clear, every planning moment: read the signals, check the records, ask a person about teams out of work, plan the generator teams with the optimizer, check the plan, send route sheets and look-here-first requests, write the status memo; then the simulated storm runs on to the next planning moment. Below, field crews (simulated): generator teams, SAT loops at 9:00 and 14:00, fuel trucks every six hours. Left out: repairs, damage assessment, other agencies' generators, funding and paperwork.
:width: 100%

The job the agent was built for. Green boxes are the agent's; blue boxes are decisions the SOP gives to a person.
```

**The question.** When the next hurricane comes, could an AI agent help the TMC staff run this SOP: identify zones and
priorities, set the routes, assign the teams, and then, after the storm, check signal status, use SAT reports,
dispatch generators and fuel, reconcile the generator records and write the daily update? Repairs, damage assessment
and paperwork were left out on purpose.

## A digital twin to test it on

Nobody can test an agent on a real storm, so the project starts with a simulation of one. It is a small digital twin:
the roads and signal locations are real (OpenStreetMap), and everything uncertain is a setting you can change.

| Part | In the simulation | Real or assumed |
|---|---|---|
| Signals | 245 signals on state roads (US or SR route number) in Tampa | Real locations |
| Priority | 47 Priority 1, 98 Priority 2, 100 Priority 3 | Assumed rule (the District's list was not available) |
| Zones and yards | 5 zones of a few corridors each; 2 yards | Assumed, after a District 7 zone map |
| Equipment | 40 generators, 80 beacon kits, 6 generator teams, 2 fuel trucks, 5 SAT teams | Example numbers |
| What the TMC sees | Signal system colors, SAT reports (15% wrong, about 30 minutes late), an outage map that lags; 10% of installs never written in the ledger | Assumed |
| The storm | Outages spread over the area; power returns area by area over several days; 120 hours after the all clear | Simulated, one storm, seed 1 |

The simulator stops at every **planning moment** and asks whoever is in charge (a fixed rule, or the agent) what the
generator teams should do next. At the end it scores the whole storm.

The score this section uses is a risk score: hours that signals spent dark or flashing, weighted by priority and by
time of day.

$$
\text{Risk} \;=\; \sum_{\text{signals } i}\ \sum_{\text{hours } t} \; w_{p(i)} \cdot n_t \cdot s_{i,t}
$$

| Symbol | Meaning | Value used |
|---|---|---|
| $w_{p(i)}$ | weight of signal $i$'s priority level | 4, 2, 1 for Priority 1, 2, 3 |
| $n_t$ | night factor for hour $t$ | 3 at night, 1 by day |
| $s_{i,t}$ | state of signal $i$ in hour $t$ | 1 dark, 0.3 flashing, 0 working or on a generator |

**In words:** a Priority 1 signal dark for one night hour costs 12 points; the same signal flashing in daylight costs
1.2. The weights are assumptions, so the section also reports the plain counts: dark signal-hours at night, and dark
hours the TMC did not know about.

## From the SOP to code, skills, tools, people and guesses

Section 6.2 sorted know-how into four homes. This project used the same sort on the SOP, with two more rows: the work
that field crews do on the street, and the gaps where the SOP says nothing.

```{figure} ../_static/figures/SOA_SOP_Homes.png
:alt: The SOP on the left, 22 clauses in scope, with arrows to six homes. Code, rules with a number that must hold: dispatch_rules.json R1 to R7 bounds the optimizer; check_plan.py and check_deployment.py. Skills, steps in order: pre-landfall-signal-deployment, post-storm-signal-dispatch, post-storm-signal-operations. Tools: 10 before landfall, 15 after the storm. A person: the team rule, moving a team, a Priority 1 signal that cannot be covered. Field crews (simulated): first refuel at 6 hours, SAT loops, writing each install down, 7 clauses. Guesses: G1 to G7, each marked as a guess a person can overrule. Below: every clause becomes a line in sop_contract.json with an owner and a check; sop_audit.py marks each met, partly met or not met.
:width: 100%

Where each part of the SOP went. Code holds what must never be broken; skills hold the order of steps; a person keeps what the SOP gives to people.
```

**Three skills**, in the format you met in 6.2. Each one loads only when its job comes up.

| Skill | Its job | What it holds | Its checker |
|---|---|---|---|
| `pre-landfall-signal-deployment` | The deployment a few hours before landfall | Zones, teams and corridors; how to compare "Priority 1 first" with "all dark signals"; who decides | `check_deployment.py` |
| `post-storm-signal-dispatch` | A good generator plan | Rules R1 to R7 (every dark Priority 1 signal gets a generator or a beacon the same day; a team works only its zones; ...) and how to read the optimizer's result | `check_plan.py` |
| `post-storm-signal-operations` | One planning moment after the storm | The eight steps below, the guesses G1 to G7, and what a person decides | Uses the dispatch checker |

**Tools** give the agent eyes and hands: 10 before landfall (read the zone map, forecast work by zone, assign teams,
corridor routes, compare the two team rules in simulated storms, fuel trucks needed, ask a person, write and issue the
sheet) and 15 after the storm (read the signal system, the TMC's current picture, SAT reports and the outage map; the
generator ledger, reconciliation, pickups and fuel; suggest team moves; plan with the optimizer; check the plan; ask a
person; send the plan; write the status memo). The optimizer, `plan_generators`, is an OR-Tools routing model; the
agent never writes a route itself.

**Where the SOP is silent, make the reasonable guess, and say it is a guess.** The SOP does not say what a "route" is,
whether a team may leave its zone, or which source wins when SAT and the outage map disagree. The operations skill
writes seven guesses down, each with an id the agent must cite when the guess shapes a plan:

| # | The SOP does not say | The guess |
|---|---|---|
| G1 | what a route looks like | The optimizer's stop list for each team inside its zones |
| G2 | how long "Priority 1 only" lasts | Until every Priority 1 signal that can take a generator has one |
| G3 | whether a team may leave its zone | Only when it has no work left there, and only after a person approves |
| G4 | which source wins when they disagree | Signal system, then the newest field report, then the outage map; when SAT and the map disagree about a stop, hold it and ask SAT to look first |
| G5 | when to collect a generator on the outage map's word | Collect it, unless earlier trips found the power still out |
| G6 | when a generator leaves the refuel list | At pickup, not when power seems back |
| G7 | who refuels when fuel trucks are short | Report it at the top of the note |

None of these is confirmed by District 7. That is the honest state of most agency procedures: an agent that runs one
will meet every gap the people who wrote it filled with experience.

### The SOP as a contract

The last step turns the SOP into something you can check. `sop_contract.json` lists the 22 clauses in scope, what
each asks, who owes it (14 the agent, 1 a person, 7 the field crews), which tool does it, and which check decides it.
Four rules from the skills and the harness are added (26 lines in all). After a run, `sop_audit.py` marks each line
**met**, **partly met** or **not met**, with evidence taken from the simulator's records and the list of tool calls,
never from what the agent says it did. Clauses the project left out (training, contracts, repairs, funding) are listed
too, with the reason.

## The agent: one planning moment at a time

The agent works in two phases. **Before landfall** it takes one turn and issues the deployment sheet. **After the all
clear** the simulator stops at every planning moment: the all clear, each morning, every two hours of the working day,
and whenever a team runs out of work (a moment is skipped if no idle team could be given anything). At each moment the
agent takes one turn.

```{figure} ../_static/figures/SOA_Turn.png
:alt: Eight steps in a row with the tools each uses. Before step 1, load_skill for post-storm-signal-operations and post-storm-signal-dispatch. 1 Read: read_atms, known_status, read_estorm, check_outage_map. 2 Records: generator_ledger, reconcile_generators, pickup_candidates, check_fuel. 3 Idle teams: suggest_team_moves, ask_person. 4 Plan: plan_generators with hold_signals and confirmed_pickups_only. 5 Check: check_plan. 6 Ask: ask_person. 7 Send: send_plan with sat_look_first. 8 Report: status_report. Below, four guard rails enforced in code: a team changes zone only after a person says yes and only with no work left in its zone; the model never writes a route; send_plan is refused unless check_plan passed that plan with 0 FAIL; if the model fails, a scripted procedure finishes the turn. Between planning moments the conversation is dropped; only the agent's note carries over.
:width: 100%

One turn after the storm. The skill sets the order; the numbered guard rails are code the model cannot talk its way around.
```

Three design choices carry most of the weight:

- **The rules that must hold are code, not prompt text.** The harness refuses `send_plan` for a plan that
  `check_plan` did not pass, refuses a team move without a person's yes, and gives the agent no tool that writes a
  route. A model that ignores an instruction still cannot break these.
- **People decide what the SOP gives to people.** The team rule is chosen by the TMC shift lead before landfall, and
  the agent cannot change it. In these runs the "person" is a short script with one policy, set by the instructor:
  approve a team move only when the team has no work left in its zone. For class, `--person live` puts a real person
  at the keyboard.
- **Memory is one note.** Each planning moment starts a new conversation. The agent carries over only the short note it
  wrote with `status_report` last time, and reads everything else again with tools, because the signals have changed.

## Inside one turn: what the model was sent, what it called, and why

This is the part an agent framework usually hides. The harness here records everything: the system prompt, the tool
list, every message in order, what came back, and the tokens, seconds and dollars of each request. Claude 5.5 models
think before they answer, but the API returns that thinking empty unless you ask for a summary
(`thinking: {type: "adaptive", display: "summarized"}`); this run asked, so you can read why the model picked each tool.
The summary is written by the API, not the raw reasoning, and it costs nothing extra.

Take turn 2 of the Claude Sonnet 5.5 run: hour 2 after the all clear, 9:00 AM on day 1.

1. **Request 1.** The model receives the system prompt (2,473 characters, including the two skills' one-paragraph
   descriptions), the list of 15 tools with their input schemas, and the task: the hour, why now, the team rule, and
   its own note from hour 0. It answers with two calls: `load_skill` for the operations skill and for the dispatch skill.
2. **Request 2.** Both `SKILL.md` files (6,293 and 10,986 characters) are now in the conversation as tool results. The
   model makes eight calls in one step: it reads the signal system, the TMC's picture and the SAT reports, and checks the
   ledger, reconciliation, pickups, fuel and idle teams.
3. **Request 3.** The model thinks before it plans. The summary of that thinking reads, in part: SAT reports five
   signals as working while the signal system shows them red; "The G4 rule says to hold a stop and send someone to look
   first whenever SAT and the outage map disagree". It calls `plan_generators` with those five signals held.
4. **Requests 4 to 7.** `check_plan` returns 0 FAIL and 2 WARN; `send_plan` goes out with the five signals on SAT's
   "look here first" list; `status_report` writes the memo and the note for the next turn; a short reply ends the turn.

```{figure} ../_static/figures/SOA_Turn_Tokens.png
:alt: Bar chart of model input tokens for the seven requests of turn 2. Request 1, 3,582 tokens, then load_skill twice. Request 2, 10,142, then eight reads and record checks at once. Request 3, 15,592, then thinking and plan_generators with five signals held. Request 4, 17,267, then check_plan. Request 5, 17,431, then thinking and send_plan. Request 6, 17,914, then status_report. Request 7, 19,059, then a one-line reply. Most of each bar is read from the cache; uncached input was 2 to 4 tokens per request.
:width: 100%

Turn 2, request by request (Claude Sonnet 5.5). The history is sent again with every request, so input grows from 3,582 to 19,059 tokens. Prompt caching means most of it is read back cheaply.
```

That turn took 7 requests, 14 tool calls, 21 seconds and 6 cents. Over the whole storm the Sonnet agent made 262
requests and 532 tool calls (73% of them several at once), wrote 124 thinking summaries, read 87% of its input from the
cache, and cost $2.23.

**What does the model actually read?** Not "messages" and "tools": one long text, cut into tokens. Claude's own format
is not published, so the companion writes the last request of turn 2 out in the open chat template of Qwen3, an
open-weight model family you can run on your own computer. The tool list sits inside the system message between
`<tools>` tags; a tool call is text between `<tool_call>` tags; each result comes back between `<tool_response>` tags.
That one request is 44,055 characters (12,664 tokens for Qwen3's tokenizer). A tool call is just text the model writes,
and the harness is what turns it into an action.

(signal-ops-agent-companions)=
## Interactive companions

**Inside the agent's turns.** Every request of the Sonnet run, as recorded.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion &mdash; Inside the signal agent's turns: what the model was sent, what it called, and why</span>
    <a href="../_static/companions/Agent_Turn_Transcript.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/Agent_Turn_Transcript.html"
          title="Inside the signal agent's turns" loading="lazy"></iframe>
</div>

Four tabs:

1. How a turn works: the harness, the model, the tools, the skills and the person, with this run's numbers; the three
   levels at which a skill reaches the model; what carries over between planning moments.
2. One planning moment, step by step: pick any of the 31 turns and step through its requests. Each step shows the
   history sent, the thinking summary, the calls and the results, and a side panel with what the request carried and
   what it cost.
3. The whole storm: which tools were called in which turn, and every place a person said no.
4. What the model reads, as text: one request written out in Qwen3's chat template.

**The storm on the map.** The same storm under the built-in rule, three agent runs (Claude Haiku 5.5, Sonnet 5.5 and
Opus 5.5) and two benchmarks.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion &mdash; After the storm: the signal SOP on a Tampa map</span>
    <a href="../_static/companions/Signal_Ops_After_Storm.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/Signal_Ops_After_Storm.html"
          title="After the storm: the signal SOP on a Tampa map" loading="lazy"></iframe>
</div>

Press play and switch the map between **On the street** (the truth), **What the TMC believes** and **Signal system**.
Pick an AI agent run and open the **Agent's turn** tab to see the skills and tools of the turn at the current hour; on
the Sonnet run, a link opens that turn in the first companion. The **SOP contract** tab shows the audit, clause by
clause.

## What three models did with the same storm

Same storm, same seed, same tools, skills and person script; only the model changed. The fast built-in rule is the
baseline (it keeps to the same dispatch rules, with no model); the perfect picture is a benchmark no TMC can reach,
because its dispatcher sees every signal's true state.

| | Built-in rule | Agent, Haiku 5.5 | Agent, Sonnet 5.5 | Agent, Opus 5.5 | Perfect picture |
|---|---|---|---|---|---|
| Risk score (lower is better) | 7,765 | 8,272 | 8,640 | 8,363 | 7,632 |
| Dark signal-hours at night | 304 | 301 | 336 | 284 | 247 |
| Priority 1 dark hours at night | 0 | 0 | 0 | 0 | 0 |
| Dark signal-hours the TMC did not know about | 112 | 61 | 70 | 100 | 0 |
| Truck trips that found nothing to do | 45 | 54 | 41 | 39 | 1 |
| Times a generator ran dry | 0 | 0 | 0 | 0 | 0 |
| Agent turns after the storm / tool calls | | 32 / 484 | 30 / 522 | 30 / 490 | |
| Turns finished by the scripted fallback | | 0 | 0 | 0 | |
| SOP contract: met / partly met / not met | | 23 / 2 / 1 | 23 / 2 / 1 | 23 / 2 / 1 | |
| Seconds per turn | | 18 | 26 | 29 | |
| API cost of the whole storm | | $0.14 | $2.23 | $4.58 | |

What the runs show:

- **All three ran the whole SOP.** Every turn finished without the fallback, every plan sent had passed the checker, no
  Priority 1 signal was dark at night, and no generator ran dry.
- **None beat the built-in rule on risk.** The agent's plans come from the optimizer, and the optimizer, not the model,
  is the weak piece: in 25 of the Sonnet agent's 30 turns, the checker warned that the plan sent generators to
  flashing signals while some dark signals had no beacon.
- **The agents kept a better picture.** All three had fewer unnoticed dark hours than the built-in rule (61 to 100 vs.
  112). They also held disputed signals out of plans and asked SAT to look first (37, 87 and 134 requests).
- **A bigger model did not do better here, and cost up to 32 times more.** The three items not fully met are the same in
  every run, and all three are owed by field crews: the first refuel within six hours (only 23 to 25 first refuels per
  run came within 7.5 hours), every install written down at the time, and SAT rounds on time. The contract shows where two fuel trucks and five SAT
  teams cannot keep the SOP, whatever the agent does.

:::{admonition} Before you trust this result
:class: important
**What is the baseline?** The simulator's fast built-in rule on the same storm, with the same zones, teams, team rule and
field conditions; and the perfect-picture benchmark as the best a dispatcher could do. One difference: the built-in rule
moves an idle team to the zone with the most work by itself, while the agent must ask a person.

**How was the data split, and why is that honest?** There is no training here: the models were not tuned on this storm,
and the skills and guesses were written before the runs. But it is **one simulated storm and one seed**, so a difference
of a few percent between columns is noise, and every number in the simulation is an assumption.

**What does it do on the ugly cases?** The person is a script. The reading of "no work left in its zone" is ours (nothing
the team can do with the equipment it can reach): at hour 6.9 of the Sonnet run it let teams G4 and G5 leave zone 3,
which still had dark signals but no equipment left for them. The guesses G1 to G7 are not confirmed by District 7, and the signal system, eSTORM and the outage map are
stand-ins for the real ones.
:::

## Where it breaks

- **The plan is only as good as the optimizer.** The model chooses inputs (hold these signals, collect only confirmed
  pickups); the optimizer chooses routes. A smarter model cannot fix a weak routing model.
- **The model's explanation can be wrong.** In turn 2, the Sonnet agent's note says two generators went to flashing
  signals "as the dark ones are already covered", while the same note says 37 dark signals stay dark tonight. The tool
  output was right; the story was not. Read the checker's findings, not the agent's summary of them.
- **A one-note memory means repeated work.** Every planning moment loads both skills again and reads everything again:
  about 17 tool calls per turn. That keeps each turn honest about the present, at the price of tokens and time.
- **Silent gaps stay silent.** Where the SOP and the guesses say nothing (a closed bridge, a generator stolen from a
  site), the agent has no tool to notice it.
- **Cost and time at storm scale.** About 30 turns took 10 to 15 minutes per storm, model and tools together. That is fine
  for a TMC, but a district-wide event with many more signals means a much longer history in every request.

| Fit card — an agent that runs an agency SOP | |
| --- | --- |
| **Idea in one sentence** | A model in a loop follows a written procedure through tools, with the steps in skills, the rules in code, and the decisions with people. |
| **Why it works** | The SOP already says who does what, in which order; tools give the model eyes and hands; code keeps the rules whatever the model writes; a person signs where the SOP says a person decides. |
| **Fits these tasks** | Recurring, rule-heavy operations with several data sources and a written procedure: storm response, incident management, work zones, evacuation. *Leverage: judgment, retrieval, extraction, generation.* |
| **Needs this data** | The procedure and a list of its gaps; tools on the agency's live systems; a simulator or past events to test on before the real one; people who answer the questions. |
| **Breaks when** | The data feeds are wrong or late; the procedure is silent and nobody wrote the guess down; the planning tool is weak; people read the agent's story instead of its checks. |
| **Keep the classical method when** | A fixed rule already does the job: here the built-in rule scored better on risk at no cost. Use the agent where text, sources that disagree, and people's decisions are the hard part. |

## Applications beyond this storm

- **Agency practice: traffic incident management.** A TIM program has written steps, several data feeds (CAD, cameras,
  511) and decisions that belong to people (lane closures, towing). The same split works: steps in a skill, response
  times in code, the closure decision with the incident commander. Baseline: the TMC operator's checklist.
- **Agency practice: work zones.** A work-zone traffic control plan has rules with numbers (taper lengths, lane-closure
  hours) and approvals. An agent can check daily closure requests against the plan with a checker script, the way
  `check_plan.py` checks a dispatch plan. Baseline: a reviewer with the MUTCD Part 6 tables.
- **Research.** A digital twin plus a recorded transcript is a testbed: change one thing (the model, the skill, the
  person's policy) and compare on the same storms. The comparison this project runs next is the built-in rule, the
  optimizer and skills without a model, the agent with the skills, and the agent without them (`--no-skill`).

## For your project

- Write down the procedure your project follows, and sort it into the six homes above before you write any prompt.
- List the gaps, and write each guess with an id and a person who can overrule it.
- Put every rule that must hold in code, and make the harness refuse an action that breaks it.
- Record the full transcript of every run (prompt, history, calls, results, tokens). Without it you cannot say why the
  agent did what it did.
- Compare against the simplest baseline that does the job, and report where the agent loses.

## Check yourself

1. The Opus run cost 32 times as much as the Haiku run and did not reach a lower risk score. Your district asks which
   model to buy for the next storm season. What would you test before you answer, and what would change your mind?
2. A colleague wants to drop `check_plan.py` because "the skill already tells the model the rules". Using the turn 2
   transcript, explain what the checker catches that the skill cannot guarantee.
3. The SOP says SAT repeats its assessment at 9:00 AM and 2:00 PM, and the audit marks that clause partly met in every
   run. Is that the agent's failure, the SOP's, or the resources'? What would you change in the simulation to find out?

## Sources

- FDOT District 7. *Traffic Signals Standard Operating Procedures Reference Guide*, v1.5 (June 2025). The SOP itself is
  not published with the project; clauses are paraphrased.
- The [hurricane-signal-ops](https://github.com/ai4mobility/hurricane-signal-ops) repository: the simulator, tools,
  skills, `sop_contract.json`, `sop_audit.py`, the agent harness (`agent_loop.py`, `agent_tools.py`, `run_agent.py`), and
  the transcript exporter. Runs of Nov 18, 2026 (`out/agent_runs/haiku_moderate`, `sonnet_moderate`, `opus_moderate`).
- Map data &copy; OpenStreetMap contributors (ODbL). Routing: Google OR-Tools.
- Anthropic. [Tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview),
  [prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) and
  [thinking](https://platform.claude.com/docs/en/build-with-claude/thinking) (the `display` option) documentation.
- Qwen team. [Qwen3](https://huggingface.co/Qwen/Qwen3-8B) chat template, used in the companion to write one request out
  as text.
- In this course: {doc}`5.2 A model in a loop <../module5/notes2-loop>`, {doc}`5.3 Tools <../module5/notes3-tools>`,
  {doc}`6.1 Where knowledge lives <notes1-knowledge>`, {doc}`6.2 Inside a skill <notes2-skills>`.
- Agents unit credit: CMU 11-768 *AI Agents* (Fried and Neubig); Stanford CS 329Z *Engineering AI Agents*.

---

Next: {doc}`Module 7 <../module7/index>`, what an agent reads and remembers. The transcript in this section's companion
is a good place to start: every request in it is a context window.
