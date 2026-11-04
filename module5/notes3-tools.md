(agent-tools)=
# 5.3 Tools: what an agent can reach

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 5 &middot; Section 5.3</span>
    <span class="notes-card-session">Session: How an agent works</span>
  </div>
  <p class="notes-card-lede">An agent is only as useful as what it can reach. This section is about the tools: why an agent picks from a menu instead of writing a new script each time, how a tool is described to a model, how a TraCI function you already know becomes a tool, how the harness turns a model's call into a run, and where your traffic knowledge goes in a tool's design. Then how a model learned to decide when to call one (the milestone paper Toolformer, read in depth), code as a richer kind of action, the protocol that lets one tool serve many agents (MCP), and what the first published traffic agents show and do not show. It ends with how to grade an agent's tool use against a baseline that needs no model.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Read it first</h4>
      <ul>
      <li><a href="notes2-loop.html">5.2 A model in a loop</a></li>
      <li><a href="notes1-workflow.html">5.1 The workflow is the unit of work</a></li>
      </ul>
    </div>
    <div>
      <h4>Used again in</h4>
      <ul>
      <li><a href="notes4-context.html">5.4 Context: what the model reads</a></li>
      <li><a href="../module8/index.html">Module 8 &mdash; Building transportation harnesses</a></li>
      </ul>
    </div>
  </div>
</div>

## What this section covers

- Why a language model needs tools at all, in four transportation needs
- A menu, not a new script each time: the TMC analogy
- A tool is a contract: name, description, parameters, result
- Five SUMO tools built from TraCI: a utility function with a new caller
- Tool call vs. TraCI call, and who names the tools
- How the model picks a tool, and how the harness runs it
- What a harness can check about a tool call, and what it cannot
- Where your transportation knowledge goes in a tool
- A full SUMO toolkit for agents on a real network, and how to write your own tool (interactive companion)
- Milestone paper: **Toolformer**, a model that learns when a call is worth making
- Code as the action (CodeAct)
- MCP: one standard plug between agents and tools, and why credentials stay in the server
- The published traffic agents, read with one checklist, and the research gap they leave
- A detector as a tool: the inspection case
- Grading tool use

## Why a model needs tools

A language model by itself can only read text and write text. Four things it cannot do come up in every
transportation task, and each one is a reason to give it a tool.

**Facts after its training date.** Its knowledge stops on the day its training data was collected. It cannot
know tonight's incidents, this week's lane closures, or the timing plan in a controller right now; a tool that calls
Florida 511's incident feed, or the signal system, can.

**Exact numbers.** It writes digits one token at a time, the same way it writes words. It will usually get a
small sum right and a sum over 400 crash records wrong. A Webster cycle length, a predicted crash frequency from
a safety performance function, or a count from the crash database should come from a tool that computes it.

**Acting on a system.** Only a program can start SUMO, run a query, or save a draft work order.

**Seeing what text cannot.** The detectors and segmentation models of Modules 1 to 3 see images. Wrapped as a
tool, a vision model lets a language model use what it sees.

Every tool you add should answer one of these needs. A tool that answers none is one more description the model
must read at every step, and one more way for the agent to go wrong.

## A menu, not a new script each time

You already know how to make SUMO do something: you write a Python script that calls SUMO's predefined API
functions through TraCI. An agent ends up calling the same API functions. What changes is how the call is made. The
model does not write a new script each time. Instead, you write each tool once, as an ordinary, tested function, much
like the TraCI functions you wrote in your traffic flow course. The harness shows the model a short menu of the tools:
each tool's name, one sentence on what it does, and its inputs. The model only fills in an order: which tool, with
which inputs, such as `run_simulation` with green_ns = 30 and green_ew = 21. The harness runs the real function, which
calls SUMO, and pastes the result back as text.

**An analogy you know: the TMC's traffic management software.** A TMC operator who wants to post a message on a DMS
does not write code. The operator picks a command from a menu and fills in a form: which sign, what message. The
software checks the form, sends the command to the sign, and logs it. A **tool call is that form**, filled in by the
model instead of the operator. The menu is the list of tools in the model's context, the form's fields are the tool's
inputs, and the software that checks and runs the command is the harness.

```{figure} ../_static/figures/AGT_TMC_Form.png
:alt: Two rows of four panels. Top, what a TMC operator does: pick Post DMS message from a menu in the TMC software; fill in a form with sign I-275 NB sign 12 and the lines CRASH AHEAD, RIGHT LANE BLOCKED, EXPECT DELAYS; check that the message fits the sign (3 lines of 18 characters), that the sign is online, that the operator confirms and that the action is logged; the sign changes. Bottom, the same four steps for an agent: pick post_dms_message from the tools listed in its context; write the call; the harness runs the same checks in code, asks a person before posting and logs every call; the harness posts the message, a real action rather than words.
:width: 100%

A tool call is a form the model fills in. Menu = tool list, form = tool call, software = harness, sign = the real world. Illustrative.
```

**Why not let the model write a script each time?** A script can do things no menu offers. But writing a new script
each time is slow, it makes mistakes, and its result can change from run to run. That is like calling a software
engineer to write new code every time you need to change a DMS message. The menu-and-form design wins on five counts:

- **Fewer mistakes.** A form with two numbers is much easier to fill in correctly than a script is to write
  correctly. The tool itself is written and tested once, by a person, so the same order runs the same way every time.
- **Checks before anything runs.** The harness can check every input against a rule, such as the 21 s pedestrian
  minimum, before SUMO starts. A free-form script is much harder to check.
- **Safety by design.** The model can do only what is on the menu. If no tool writes to a live signal controller,
  the agent cannot change one.
- **Cheaper and faster.** In the recorded runs of {doc}`5.2 <notes2-loop>`, the model's whole reply at step 1, a
  thought plus the call, was 44 tokens. A script would run to hundreds, and every token the model writes costs time
  and money.
- **Reuse.** One tool serves many tasks, and with MCP (below) one tool can serve many agents.

The price is flexibility: an agent can do only what its tools allow. When a task really needs a loop over many
intersections, some agents let the model write short code instead (CodeAct, below), always inside a sandbox.

## A tool is a contract

```{figure} ../_static/figures/AGT_Schema.png
:alt: Three panels. Left, the run_simulation tool description with its name, description and two integer parameters in seconds. Middle, the tool call the model wrote in a recorded run. Right, the result the harness pasted back, with the cycle, vehicles and average delay.
:width: 100%

The real tool from the recorded runs of 5.2: what the model is told, what it wrote, and what came back. The call is only text until the harness parses and runs it.
```

A tool is described to the model by a **schema**: a name, a description in plain English, and a list of
parameters with their types. The model never sees your code; this description is all it knows about what the
tool does and when to use it. Treat it as a contract you write for a careful stranger.

Three parts of the contract matter most.

- **Name and description.** The model reads them like documentation. "Simulate one hour of traffic in SUMO with
  a two-phase fixed-time plan and return the average delay per vehicle (seconds)" tells it what the tool is for,
  what it returns, and in what unit.
- **Parameters, with units.** "green_ew, seconds" leaves less to guess than "time". If the description says
  seconds and the model passes minutes, that is a bug in the description.
- **The result.** It is text the model reads next, so design it for that reader. A list of every vehicle buries
  the number that matters. An error that says "invalid input" teaches nothing; one that says "east-west green
  must be at least 21 s for pedestrians" tells the model what to try next.

## Five SUMO tools built from TraCI

Before agents, you wrote utility functions: helpers you write once so your own scripts stay short. A tool is the
same kind of helper, but now the model calls it, not you. Here are five SUMO tools, each a plain Python function
that calls [TraCI](https://sumo.dlr.de/docs/TraCI/index.html). Two read the simulation, two change it, and one moves
time forward. The one-line docstring under each name is the sentence the model will read.

```python
import traci

MPH = 0.44704  # 1 mph in m/s; TraCI speeds are in m/s

# Tool 1 (reads): the queue at a lane-area (E2) detector
def get_queue(detector_id):
    """Queue length at a lane-area (E2) detector."""
    meters = traci.lanearea.getJamLengthMeters(detector_id)
    vehicles = traci.lanearea.getJamLengthVehicle(detector_id)
    return f"Queue at {detector_id}: {meters:.0f} m, {vehicles} vehicles"

# Tool 2 (reads): speed and stopped vehicles on one lane
def get_lane_state(lane_id):
    """Mean speed and number of stopped vehicles on a lane, last step."""
    mph = traci.lane.getLastStepMeanSpeed(lane_id) / MPH
    stopped = traci.lane.getLastStepHaltingNumber(lane_id)
    return f"{lane_id}: mean speed {mph:.0f} mph, {stopped} vehicles stopped"

# Tool 3 (acts): switch a signal to a phase and hold it
MIN_HOLD, MAX_HOLD = 7, 60  # example limits in seconds; use your own timing plan's

def set_signal_phase(tls_id, phase, seconds):
    """Switch a signal to a phase number and hold it for some seconds."""
    if not MIN_HOLD <= seconds <= MAX_HOLD:
        return f"Rejected: hold time must be {MIN_HOLD}-{MAX_HOLD} s."
    traci.trafficlight.setPhase(tls_id, phase)
    traci.trafficlight.setPhaseDuration(tls_id, seconds)
    return f"Signal {tls_id} is in phase {phase} for {seconds} s"

# Tool 4 (acts): a variable speed limit, for example ahead of a work zone
def set_speed_limit(lane_id, mph):
    """Set the speed limit on one lane, in mph."""
    if not 25 <= mph <= 70:
        return "Rejected: speed limit must be 25-70 mph."
    traci.lane.setMaxSpeed(lane_id, mph * MPH)
    return f"{lane_id} speed limit is now {mph} mph"

# Tool 5: let time pass so a change can show up
def advance(seconds):
    """Run the simulation forward by some seconds."""
    for _ in range(seconds):  # one step = 1 s, SUMO's default step length
        traci.simulationStep()
    return f"Simulation time is now {traci.simulation.getTime():.0f} s"
```

Because the model is now the caller, a tool needs three things you could skip when you were the only caller:

- **A description the model can read:** a clear name, a short docstring, inputs with units, and what the tool cannot
  do or where its results can mislead.
- **A check on every input,** because the model may ask for something you never would, such as a 90 s hold.
- **A short text result, errors included,** because text is all the model can read.

The model never sees the code. The harness turns each function into one line of the menu, built from its name, its
docstring and its inputs:

| Tool | What the model reads | Inputs | Changes SUMO? |
|---|---|---|---|
| `get_queue` | Queue length at a lane-area (E2) detector. | detector_id (text) | No, it reads |
| `get_lane_state` | Mean speed and number of stopped vehicles on a lane, last step. | lane_id (text) | No, it reads |
| `set_signal_phase` | Switch a signal to a phase number and hold it for some seconds. | tls_id (text), phase (whole number), seconds (whole number, 7–60) | Yes |
| `set_speed_limit` | Set the speed limit on one lane, in mph. | lane_id (text), mph (number, 25–70) | Yes |
| `advance` | Run the simulation forward by some seconds. | seconds (whole number) | Moves time only |

**One order, start to finish.** Say the model writes
`{"name": "set_signal_phase", "arguments": {"tls_id": "J1", "phase": 2, "seconds": 90}}`. The harness calls
`set_signal_phase("J1", 2, 90)`. The check fails, SUMO is never touched, and the model reads back
`Rejected: hold time must be 7-60 s.` It can then try again with a valid hold time. If TraCI itself refuses, the
harness pastes TraCI's own message back the same way: for a signal with four phases, asking for phase 5 returns
`The phase index 5 is not in the allowed range [0,3].`

In SUMO, all five tools are safe to try. On a real signal system or a real speed-limit sign, the two tools that
change things would also wait for an engineer to approve, and every call would be logged.

**Try it.** Take a TraCI function you have already written and turn it into a tool: a clear name, a one-sentence
docstring, inputs with units, a check on those inputs, and a short text result.

## Tool call vs. TraCI call

At the bottom they are the same: some Python function runs. In everything around the call, they differ.

| | Your Python script calling TraCI | An agent's tool call |
|---|---|---|
| **Who picks the call and its inputs** | you, while writing the code | the model, while the task runs, after reading the context |
| **What the call is** | code that runs at once | text (a tool name and inputs) that does nothing until the harness runs it |
| **What it knows about the function** | the API documentation, and your own testing | only the tool's name, its description and its list of inputs |
| **Checks before it runs** | Python checks names and syntax; the rest is up to you | the harness checks the call and can refuse it, ask a person, or run it in a sandbox |
| **What comes back** | a Python value your code uses | text pasted into the context, which the model must read |
| **When something fails** | an exception your code catches | an error message the model reads; a clear one lets it try again |
| **Run it twice** | the same calls every time | possibly different calls each time, so test over repeated runs |
| **How many functions** | TraCI has hundreds of small ones, called every simulation step | a few larger ones, because every description is re-read at every step and every call is a trip through the model |

**Who names the tools?** You do. There is no standard list of tool names. A tool that counts turning movements could
be called `count_turns` in your SUMO harness and something else in a VISSIM or Aimsun harness. The model does not need
to know the name in advance: it reads the menu at every step and copies a name from it. That is why a clear name and a
clear one-sentence description matter so much. They are all the model has.

## How the model picks a tool, and how the harness runs it

The model picks a tool by reading the menu. But there is no separate "pick" step inside the model. It does what it
always does: it writes the next words. When the task needs data or an action, the most likely next words are a tool
call: a name copied from the menu, plus the inputs, in a fixed format the model was trained to write. In the recorded
runs of {doc}`5.2 <notes2-loop>` (Qwen), a call looks like this:

```text
<tool_call>{"name": "get_queue", "arguments": {"detector_id": "e2_A1B1"}}</tool_call>
```

So picking a tool means writing its name. Until the harness acts on it, nothing has happened: the call is still just
text.

```{figure} ../_static/figures/AGT_Harness_Flow.png
:alt: A flow of five boxes. The model's reply, plain text; find a call between the tags; check the call, is it a known tool; run the tool, your TraCI code (highlighted); text result into the context, which the model reads at its next step. If no call is found, the loop ends. If the check or the run fails, an error message goes into the context as text: unknown name, bad JSON, wrong inputs, TraCI refused.
:width: 100%

The harness, not the model, starts the tool. Every outcome, even an error, goes back to the model as text.
```

The tool starts running in the harness, in ordinary Python you can read. After each reply, the harness searches for
the call format. If it finds a call, it looks up the name in a dictionary of real functions and calls that function
with the inputs. This is the `run_tool` step of the loop in {doc}`5.2 <notes2-loop>`, written out for the five tools
above:

```python
import json, re

TOOLS = {                       # the menu: the name the model writes -> the real function
    "get_queue": get_queue,
    "get_lane_state": get_lane_state,
    "set_signal_phase": set_signal_phase,
    "set_speed_limit": set_speed_limit,
    "advance": advance,
}

def run_tool_call(reply):
    """Find a tool call in the model's reply, run it, and return the result as text."""
    found = re.search(r"<tool_call>(.*?)</tool_call>", reply, re.S)
    if found is None:
        return None                                  # no call: the model just answered
    try:
        call = json.loads(found.group(1))            # text -> {"name": ..., "arguments": {...}}
    except json.JSONDecodeError:
        return "Error: the tool call is not valid JSON."
    name = call.get("name")
    if name not in TOOLS:
        return f"Error: there is no tool named {name}."
    try:
        return TOOLS[name](**call.get("arguments", {}))  # this line runs your TraCI code
    except Exception as e:                           # wrong inputs, or TraCI refused
        return f"Error: {e}"
```

We ran this harness on a small synthetic 3×3 SUMO grid with five replies a model could write:

| What the model wrote | What it read back |
|---|---|
| No call, just "I think the queue is fine." | Nothing. The loop ends. |
| `get_queue` with detector_id `e2_A1B1` | `Queue at e2_A1B1: 8 m, 2 vehicles` |
| `get_queue_length`, a name not on the menu | `Error: there is no tool named get_queue_length.` |
| `set_signal_phase` without `seconds` | `Error: set_signal_phase() missing 1 required positional argument: 'seconds'` |
| `set_signal_phase` with phase 5 | `Error: The phase index 5 is not in the allowed range [0,3].` |

The model reads the error at its next step and can fix the call, for example by adding the missing seconds.

**Where the format comes from.** Each model family is trained on its own call format; the `<tool_call>` tags above are
Qwen's. With hosted models such as Claude or GPT, you send the menu in the API request, and the call comes back in its
own field, with the name and the inputs already separated. The harness then skips the search, but the dictionary
lookup and the function call stay the same.

## What the harness can check, and what it cannot

| Question about a tool call | Who can check it | In our SUMO agent |
|---|---|---|
| Is it a well-formed call with the right fields? | the harness, always | the parser; a broken call gets "could not parse the tool call" |
| Are the values allowed? | the harness, if you write the rule | in condition C, the harness rejects an east-west green under 21 s |
| Is it the right thing to do? | a person | the engineer reviews the submitted plan |

The harness can always check the **form** of a call. It can check that the values are **allowed**, but only if
you write the rule. No program can check whether the call was the **right** thing to do; that is the engineer's
job, and it is why the checkpoint rule of {doc}`5.1 <notes1-workflow>` still applies.

Typed tool descriptions pay off even without a person. The SUMO-MCP paper (below) wrapped SUMO's command-line
tools in typed descriptions and compared an agent using them with an agent calling the raw command lines. On the
same task in five regions, the agent with typed tools needed 5.0 tool calls on average instead of 12.6, and 74 s
instead of 106 s. The authors say why: with raw command lines, "parameter mismatches frequently lead to task
retries", and some runs stalled until a person stepped in (Ye et al., 2025, Table IV).

## Where your transportation knowledge goes

Your knowledge comes in at every step of designing a tool, not only in the description. Writing a SUMO tool means
making six decisions. At each one, a traffic engineer and a programmer would write different code:

| Design step | The question | Where your traffic and SUMO knowledge goes |
|---|---|---|
| **1. Which tools exist** | Which actions and measures belong on the menu? | Offer the actions an engineer takes, at the level an engineer thinks: `set_timing_plan(cycle, splits)`, not raw signal-state strings like `"GGrrGGrr"`. Leave off anything no engineer would let the agent do alone. |
| **2. Inputs** | What does the model fill in, and in what units? | Engineering terms and units: "NB left", green in seconds, speed in mph. The tool translates them into SUMO's lane IDs and m/s inside, where the model cannot get them wrong. |
| **3. Checks** | Which inputs must be refused? | The rules of practice: pedestrian clearance from the crossing distance at 3.5 ft/s (MUTCD), yellow and all-red from the ITE formula, a maximum cycle length, and speed limits only in steps an agency would post. |
| **4. Results** | What should the tool measure and report? | Measures that answer the engineering question: delay per vehicle, queue against storage length, spillback. Drop a warm-up period, run several random seeds, and report the spread, not one number. |
| **5. Warnings** | When can the numbers mislead? | The simulator's traps, reported in the result: teleports, vehicles still waiting to enter, and trips that never finished. |
| **6. Tests** | How do you know the tool is right? | Cases you can solve by hand: one intersection at low demand against Webster's delay, a queue against the input–output diagram, and more green giving less delay to that movement. |

**Put your experience into the description.** The docstring is the only manual the model gets. The model reads it to
decide whether to use the tool and how much to trust its results, so it should carry the traps that take years with
SUMO to learn. One example: under heavy congestion, vehicles can block a junction and lock it up. SUMO then teleports
any vehicle stuck for 300 s (its default) out of the jam, so a gridlocked run can report a delay that looks fine. A
better `advance` says so in its description, and its code reports the count:

```python
def advance(seconds):
    """Run the simulation forward by some seconds.
    Under heavy congestion, vehicles can block a junction and lock it up.
    SUMO then teleports any vehicle stuck for 300 s (its default), which
    makes delay look better than it is. Check the teleport count in the
    result before trusting a delay number."""
    teleports = 0
    for _ in range(seconds):  # one step = 1 s, SUMO's default step length
        traci.simulationStep()
        teleports += traci.simulation.getStartingTeleportNumber()
    t = traci.simulation.getTime()
    return f"Simulation time is now {t:.0f} s; {teleports} vehicles teleported"
```

**Row 5 is the one most often skipped.** We overloaded the small synthetic 3×3 grid on purpose, with 12,000 trips in
30 minutes. The new `advance` reported 57 teleports; the first version gave no sign of them. Only 664 vehicles entered
the network, 48 finished their trips, and 11,330 were still waiting to get in. SUMO's trip records list only finished
trips, so an average delay computed from them describes the 48 lucky vehicles. A tool written by someone who knows
this reports all of these counts next to the delay. A tool written without that knowledge returns a clean, wrong
number, and the model has no way to tell.

**A description is advice; a check is a rule.** The model can ignore a description. In the recorded runs of
{doc}`5.2 <notes2-loop>`, the lookup tool showed the 21 s pedestrian minimum and the model still submitted a plan that
broke it; when the harness rejected such plans, the model kept the rule. So when you can, put each trap in two places:
in the description, so the model chooses well, and in the code, as a check or an extra number in the result.

**For your own tools.** Before you write a tool, write down how a senior traffic engineer would check its answer. Each
check that is easy to compute goes into the code, as a refusal or an extra number in the result. Each one that is not
goes into the description. Then test whether your knowledge helped: run the same agent once with a plain tool and once
with yours.

(sumo-tools-companion)=
## A full SUMO toolkit, and how to write your own tool

The five tools above run on a small synthetic grid. The companion below takes the same ideas to a real study: twelve
SUMO tools on the Fowler Avenue corridor next to campus (a real OpenStreetMap network with synthetic demand), each
written the way a traffic engineer would write it, with a test for every claim its description makes. Each tab takes
one piece of traffic knowledge and measures what went wrong when a tool left it out: speed on an empty road, the
definition of a queue, the vehicles that never got in, timing rules, one run as evidence, calibration, and how much a
tool should say. Tab 10, **Write your own**, shows how to turn what you know into a tool's description and its result,
starting from one raw TraCI call.

The toolkit is public, so you can take it, run it, and add to it:
<a href="https://github.com/ai4mobility/sumo-agent-tools" target="_blank" rel="noopener">ai4mobility/sumo-agent-tools</a>.
Its `WRITING_TOOLS.md` is the step-by-step guide to writing a tool, and its `walkthrough/` folder records small models
calling the tools, round by round, with what went wrong and how each fix was made.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion &mdash; Building SUMO tools for AI agents</span>
    <a href="../_static/companions/SUMO_Tools_for_Agents_Companion.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/SUMO_Tools_for_Agents_Companion.html"
          title="Building SUMO tools for AI agents" loading="lazy"></iframe>
</div>

## Milestone paper: Toolformer

ReAct ({doc}`5.2 <notes2-loop>`) prompted a frozen model to use tools. **Toolformer** (Schick, Dwivedi-Yu,
Dessì, Raileanu, Lomeli, Zettlemoyer, Cancedda and Scialom; Meta AI Research and Universitat Pompeu Fabra; NeurIPS
2023) asked a different
question: can a model learn, by itself, *when* a tool call is worth making?

The obstacle is labels. To teach a model where a calculator helps, someone would have to mark every place in a
large body of text where a calculation appears. Toolformer avoids that. The model proposes calls, the calls are
run, a simple test keeps only the calls that helped, and the model is fine-tuned on its own filtered text.

```{figure} ../_static/figures/AGT_Toolformer.png
:alt: A pipeline from plain text through sample, run and filter steps to text with useful calls, then fine-tuning. Below, the Pittsburgh example: one question-answering call returns Steel City and is kept; another returns United States and is dropped.
:width: 100%

Toolformer's training recipe with the paper's own example (redrawn from Schick et al., 2023, Fig. 2). A call survives only if its answer helps the model predict the words that follow.
```

**The four steps.**

1. **Sample.** A short prompt with a few examples shows what a call looks like for each tool. At every position in
   a training text, the model's probability of starting a call is computed, and at the most likely positions
   (above a threshold, at most five) it proposes up to five calls.
2. **Run.** Each proposed call is executed. In the paper's example the text is "Pittsburgh is also known as the
   Steel City". At the position after "known as", the model proposes "What other name is Pittsburgh known by?",
   which returns "Steel City", and "Which country is Pittsburgh in?", which returns "United States".
3. **Filter.** Knowing "Steel City" makes the next words, "the Steel City", much easier to predict, so that call
   is kept. Knowing "United States" does not help, so that call is dropped.
4. **Fine-tune.** The kept calls are written into the text, "Pittsburgh is also known as [QA("What other name is
   Pittsburgh known by?") → Steel City] the Steel City", and the same model is fine-tuned on many such texts with
   the ordinary language-modeling loss.

At inference, when the fine-tuned model writes a call, generation pauses at the arrow, the tool runs, its answer is
pasted in, and generation continues: the loop of 5.2, inside a single reply.

**The filter, the one equation.** Let L⁺ be the model's loss on the words after position *i* when the call *and
its result* are written in. Let L⁻ be the lower of two losses: with no call at all, or with the call written in
but no result. The call is kept if

$$
L^- - L^+ \;\ge\; \tau_f ,
$$

with τ_f = 1.0 for most tools and 0.5 for the calculator and the translator.

**In words:** a call is worth keeping only if seeing its answer helps more than not asking, and more than just
asking. The second comparison is the clever part. Sometimes the text of a question alone hints at what comes
next; comparing against "the call without its answer" keeps only calls whose answers matter.

:::{admonition} Going deeper &mdash; the weighted loss
:class: dropdown
The loss after position *i*, given a prefix *z* (nothing, the call alone, or the call with its result), is a
weighted cross-entropy over the following words:

$$
L_i(z) = -\sum_{j \ge i} w_{j-i}\,\log p\!\left(x_j \mid z,\, x_{1:j-1}\right),
\qquad \tilde w_t = \max(0,\, 1 - 0.2\,t),\quad w_t = \tilde w_t \big/ \textstyle\sum_s \tilde w_s .
$$

The raw weights are 1, 0.8, 0.6, 0.4 and 0.2 for the five words right after the call, and zero after that. So
the filter asks a local question: does this answer help with the words immediately after it? Then
L⁺ = L_i(call with result) and L⁻ = min(L_i(nothing), L_i(call without result)).
:::

**What the results say.** Toolformer is GPT-J (6.7 billion parameters) fine-tuned this way with five tools: a
question-answering model, a calculator, Wikipedia search, a translator and a calendar. All tests are zero-shot.

| Benchmark (zero-shot) | GPT-J, 6.7B | Toolformer, 6.7B | GPT-3, 175B |
|---|---|---|---|
| Math word problems (ASDiv) | 7.5 | 40.4 | 14.0 |
| Facts (LAMA, T-REx) | 31.9 | 53.5 | 39.8 |
| Dates (DateSet) | 3.9 | 27.3 | 0.8 |
| Open questions (TriviaQA) | 43.9 | 48.8 | 65.9 |

On math, facts and dates, a model with tools beats one twenty-six times its size without them.

:::{admonition} Before you trust this result
:class: important
**What is the baseline?** The same fine-tuned model with tool calls switched off. It scores 14.8 on ASDiv, so
most of the jump to 40.4 comes from using the calculator, not from the extra fine-tuning. That ablation is what
makes the result convincing.

**How was the data split, and why is that honest?** Public benchmarks, with no task-specific examples in the
prompt.

**What does it do on the ugly cases?** GPT-3 still wins on open questions, because the search tool is simple and
the model cannot reword a query. On a second date benchmark, TempLAMA, the best move would be two calls (the
calendar, then a question about that date); Toolformer can make only one, so it used the calendar on only 0.2% of
those questions and relied on search instead. What a model can learn depends on what the loop around it allows.
:::

**What Toolformer cannot do**, in the authors' own list, is exactly what a loop provides. It cannot **chain**
tools, because each tool's calls were made separately in training. It cannot **try again**: a bad search result is
final. It makes **one call per input**. And in their tests (GPT-2 models, three tools), models below about 775 million
parameters did not learn to use the tools at all, search excepted; read that as a caution about small models, not a
rule. So the two milestone papers fit together. Toolformer:
a model can be trained to decide when to call. ReAct: a loop lets it chain calls and recover. The models you use
today are trained to write tool calls in a fixed format and run in a loop; the Qwen model of 5.2 is one of them.

## Code as the action

In 5.2 every action was one tool call written as JSON. **CodeAct** (Wang, Chen, Yuan, Zhang, Li, Peng and Ji,
ICML 2024) lets the action be a short Python program instead. The program can call several tools, loop, keep
variables and use any Python package; whatever it prints, or the error it raises, is the observation.

| gpt-4-1106-preview on 82 multi-tool tasks | Code | JSON | Text |
|---|---|---|---|
| Tasks solved (%) | 74.4 | 52.4 | 53.7 |
| Average turns | 5.5 | 7.6 | 7.7 |

Across the 17 models tested, code gave the best success rate for 12. Think of retiming twelve intersections:
with JSON, at least twelve calls and twelve trips through the model; with code, one loop. Two cautions. The
benchmark was built by the same authors, so read the gain as an upper bound. And code a model writes can do
anything code can do, so it must run in a **sandbox**, a closed environment with no access to the agency's real
systems.

## MCP: one plug for many tools

```{figure} ../_static/figures/AGT_MCP.png
:alt: A host containing a language model and three clients, each connected by JSON-RPC messages to a server. The SUMO server wraps SUMO, the crash-data server wraps the crash database inside a dashed agency-network boundary, and the detector server wraps a trained damage detector.
:width: 100%

The Model Context Protocol: a host holds one client per server, and each server wraps one system. The crash-data server runs inside the agency network, so the model sees tools and results, never the password.
```

Every agent so far had its tools wired in by hand. If three research groups each build a SUMO tool for their own
agent, that is three wrappers for one simulator; multiply by every app and every tool. The **Model Context
Protocol (MCP)**, released by Anthropic as an open standard in November 2024, is the standard plug. It is
plumbing, not new AI: it changes nothing about the model or about how you design a tool. The model reads the same menu
and writes the same tool call whether the tool sits in your own harness, as above, or behind MCP. What it changes is
where the tool runs, and that is the point that matters for an agency (below).

- **Host:** the app a person uses: a chat app, a coding tool, or your own harness. It holds the conversation and
  asks the person before sensitive actions.
- **Client:** one connector inside the host for each server.
- **Server:** wraps one system (SUMO, the crash database, a detector) and tells any client what it offers. Write a
  SUMO server once and any MCP host can use it.

A server can offer three kinds of things, and the difference is who decides to use them.

| What a server offers | Who decides when it is used | Transportation example |
|---|---|---|
| Tools | the model | run_simulation, query_crashes, detect_damage |
| Resources | the application | the network file, the crash data dictionary, a manual chapter |
| Prompts | the person | a template for a safety memo, started by a command |

Messages are JSON in a standard format called JSON-RPC, sent over standard input and output for a server on the
same machine, or over HTTP for a remote one. The protocol is still changing: the current revision, dated
2026-07-28, makes every request stand on its own, so diagrams that show an opening handshake describe older
versions. Check the version when you read a tutorial.

**The design point for agencies.** The server is the only piece that touches the real system. Keep the database
credentials in the server, run the server inside the agency's network, and the model never sees them; it sees only
the tools and their results. This is also where to enforce what a tool may do, since the server cannot be talked
out of its own code.

## The published traffic agents, read with one checklist

SUMO studies already have published agents. **SUMO-MCP** (Ye, Xiong, Shang, Dai, Gong and Lv, China
Automation Congress 2025) wraps SUMO's own tools as an MCP server; its agent finds the tools it needs, imports them
and chains them, guided by a workflow prompt the authors wrote (a prompt, they stress, not a fixed script). From one plain request it downloaded an OpenStreetMap network, built demand, ran fixed, actuated,
Webster and green-wave timing, and reported that Webster's timing gave the lowest delay (179.38 s per vehicle).

Two earlier systems are often cited with it. **TrafficGPT** (Zhang et al., *Transport Policy*, 2024; the
arXiv preprint is described here) lets gpt-3.5-turbo call traffic models over a trip database and SUMO in a
ReAct-style loop. **Open-TI** (Da et al.,
*International Journal of Machine Learning and Cybernetics*, 2024) gives GPT-3.5 twelve tools, from OpenStreetMap
download to SUMO and CityFlow runs, and also tests language models as signal controllers.

| | TrafficGPT (preprint) | Open-TI (2024) | SUMO-MCP (2025) |
|---|---|---|---|
| **Model** | gpt-3.5-turbo | GPT-3.5 | not stated |
| **Who picks the steps** | the model, in a ReAct loop | the model matches a request to tools, sometimes two in a row | the model chains tools, guided by a workflow prompt |
| **How it was judged** | example dialogues; no numbers | API error rate over 6 tasks × 20 trials | time and calls against raw command lines |
| **Not compared with** | anything | a timing method without a language model | an engineer or a script |

:::{admonition} Before you trust these results
:class: important
**What is the baseline?** None of the three compares the agent's result with what an engineer, or a simple script,
would produce on the same task. Open-TI compares its tool-call error rate (8.3%) with TrafficGPT's (19.2%);
SUMO-MCP compares its agent with the same agent using worse tools.

**How was the data split, and why is that honest?** Case studies on a few cities; SUMO-MCP reports one result per
region, with no repeats or spread.

**What does it do on the ugly cases?** Not reported. Read the tables yourself, too: by our arithmetic, Open-TI's
own Table 5 averages to 7.5% rather than the 8.3% it reports.
:::

These are not reasons to dismiss the papers; they were early and they opened the area. They are the questions a
reviewer will ask of yours. **An agent paper in transportation that compares against a strong non-agent baseline,
over repeated runs, with the failures counted, would stand out.**

## A detector is a tool too

```{figure} ../_static/figures/AGT_Detector.png
:alt: A dashcam frame goes to a detector tool, which returns text with the frame id, time, GPS and a list of detections with labels and confidences. An agent reads it and drafts a report; the inspector signs. A box under the detector says the threshold and categories are set by the engineer.
:width: 100%

The inspection case: the trained detector becomes a tool that returns text, and the language model never needs the pixels. The result format is our illustration, not the output of a particular model.
```

Inspection connects Part I of the course to Part II. The damage detector, or the pavement-distress
model, becomes a tool whose input is a frame and whose output is text: what it found, where in the frame, and how
confident it is. The language model reads that text, adds the location, drafts the description and builds the
report, with every claim linked to its frame so the inspector can check it.

What stays with the engineer: the confidence threshold below which a detection is ignored, the list of damage
categories, and the signature. Those decisions set what the report means, so they belong in the tool's
configuration or the harness, not in the model's judgment. A good design passes low-confidence detections through
marked "below threshold: for review", so the inspector sees them listed rather than silently dropped.

## Grading tool use

Grade an agent's tool use the way you would grade any method: against a baseline, over repeated runs, with the
failures counted. Here are our own twelve recorded runs from {doc}`5.2 <notes2-loop>`, three per harness setting.
Condition D was added after we saw A to C: the harness also checks the agent's claim, accepting a submission only if
the plan was simulated and beats the current plan, whose delay the harness measures itself.

| Our recorded runs (3 per condition) | A | B | C | D |
|---|---|---|---|---|
| Runs that submitted a plan | 3 | 3 | 3 | 2 |
| Plans simulated, in all | 3 | 3 | 4 | 11 |
| Calls the harness rejected | 0 | 0 | 1 | 8 |
| Submitted plans that break a limit | 1 | 1 | 0 | 0 |
| Submitted plans better than the current one | 1 | 1 | 1 | 2 |
| Tokens read, in all | 6,588 | 6,902 | 7,928 | 27,388 |

Only in D was every submitted plan both legal and better than the current plan. It cost about four times the tokens
of A, and one D run used all ten steps without finding a plan it was allowed to submit; another crept from 60/30 to
56/30 in 1 s steps and stopped at 21.1 s/veh. Rules make the agent honest; they do not make it a good optimizer.

Now the baseline that needs no model. A grid search over 315 plans, 298 s of SUMO, found 54/22 at 18.5 s/veh. No
agent run beat it; the best valid agent plan, 30/21 at 18.8 s/veh, came only after the harness rejected a plan that
broke the pedestrian minimum. For this task the honest conclusion is the Agentless one: a fixed procedure wins. An
agent earns its place where the steps cannot be enumerated, such as building the network from a plain request,
choosing which intersections to study, or explaining the result to an engineer.

:::{admonition} Before you trust this result
:class: important
**What is the baseline?** The grid search over 315 plans, and the current plan.

**How was the data split, and why is that honest?** There is no training here; the honest choices are repeated runs
(three seeds per condition) and harness conditions fixed before their runs were recorded.

**What does it do on the ugly cases?** One synthetic intersection, one SUMO seed, and a 1.5-billion-parameter model
on a laptop-class CPU. A larger model would likely search better; we did not measure it. The lab asks you to.
:::

The questions to ask of any agent paper, including your own: what is the baseline that needs no model; what share of
runs finished and stayed within the rules; what is the spread over repeated runs; and what did each task cost in
tokens or time?

| Fit card — tools | |
| --- | --- |
| **Idea in one sentence** | A tool is a described function the model can ask the harness to run; MCP is a standard way to offer one tool to many agents. |
| **Why it works** | The model only has to write a call; the tool does the computing, the looking up or the seeing. |
| **Fits these tasks** | Fresh data, exact numbers, simulators, databases, vision models. *Leverage: retrieval, computation, perception.* |
| **Needs this data** | Clear descriptions and schemas, informative results and errors, and test calls with known answers. |
| **Breaks when** | Descriptions are vague, results are long or empty, errors say nothing, or a call can change something that cannot be undone. |
| **Keep the classical method when** | A fixed script already calls the tools in the right order every time; then the model adds risk without adding choice. |

## Check yourself

1. Write the tool description for a crash-query tool: its name, a one-sentence description, three parameters with
   units, and what it returns when no crash matches.
2. Toolformer's model with calls switched off scored 14.8 on math word problems; with calls, 40.4. What would you
   conclude if the switched-off score had been 38?
3. Your detector server runs on the district's network. List two things the server should do itself rather than
   leave to the language model.
4. A classmate's `run_simulation` tool returns only an average delay. Under what traffic conditions would you distrust
   that number, and what would you add to the result?
5. Your agent writes a call to `get_queue_length`, a tool that does not exist. Who catches the mistake, what does the
   model read next, and what might you change in the menu?

## Sources

- Schick, T., et al. (2023). Toolformer: Language models can teach themselves to use tools. *NeurIPS*.
  [arXiv:2302.04761](https://arxiv.org/abs/2302.04761).
- Wang, X., et al. (2024). Executable code actions elicit better LLM agents. *ICML*.
  [arXiv:2402.01030](https://arxiv.org/abs/2402.01030).
- Anthropic (2024). [Introducing the Model Context Protocol](https://www.anthropic.com/news/model-context-protocol).
  Specification revision 2026-07-28, [modelcontextprotocol.io](https://modelcontextprotocol.io).
- Ye, C., et al. (2025). SUMO-MCP: Leveraging the Model Context Protocol for autonomous traffic simulation and
  optimization. *China Automation Congress*. [arXiv:2506.03548](https://arxiv.org/abs/2506.03548).
- Zhang, S., et al. (2024). TrafficGPT: Viewing, processing and interacting with traffic foundation models.
  *Transport Policy* 150, 95–105. [arXiv:2309.06719](https://arxiv.org/abs/2309.06719).
- Da, L., et al. (2024). Open-TI: Open traffic intelligence with augmented language model. *International Journal
  of Machine Learning and Cybernetics* 15, 4761–4786. [arXiv:2401.00211](https://arxiv.org/abs/2401.00211).
- Fried, D., & Neubig, G. (2026). [CMU 11-768 AI Agents](https://www.cmu-agents.com/), lectures on tool use and MCP.
- Eclipse SUMO documentation: [TraCI](https://sumo.dlr.de/docs/TraCI/index.html) (lane area detector, lane and
  traffic light value retrieval and state changes) and [TripInfo output](https://sumo.dlr.de/docs/Simulation/Output/TripInfo.html).
  The five tools, the harness and every SUMO output quoted in this section come from our own runs on a small synthetic
  3×3 grid (SUMO with the `traci` Python package, November 2026).
- The course toolkit: <a href="https://github.com/ai4mobility/sumo-agent-tools" target="_blank" rel="noopener">ai4mobility/sumo-agent-tools</a>
  (SUMO 1.28.0; Fowler Avenue network © OpenStreetMap contributors, ODbL; synthetic demand). Every number in the
  companion comes from its scripts and tests.

---

Next: {doc}`notes4-context` &mdash; what the model reads on every call, and how to bring knowledge in from outside.
