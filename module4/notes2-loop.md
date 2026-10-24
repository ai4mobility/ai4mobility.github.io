(agent-loop)=
# 4.2 A model in a loop

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 4 &middot; Section 4.2</span>
    <span class="notes-card-session">Session: Oct 29</span>
  </div>
  <p class="notes-card-lede">What an AI agent is and how it runs: a language model whose replies can be tool calls, a program that runs them, and a loop that feeds the results back. This section opens real recorded runs of a small open model retiming a signal in SUMO, step by step and token by token, then reads the milestone paper behind the loop, ReAct, in depth. It closes with where an agent sits between a fixed workflow and full autonomy, and with the idea that organizes all of Part II: an agent is a model plus a harness.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Read it first</h4>
      <ul>
      <li><a href="notes1-workflow.html">4.1 The workflow is the unit of work</a></li>
      <li><a href="../module2/notes4-gpt.html">2.4 GPT: generating one token at a time</a></li>
      </ul>
    </div>
    <div>
      <h4>Used again in</h4>
      <ul>
      <li><a href="notes3-tools.html">4.3 Tools: what an agent can reach</a></li>
      <li><a href="notes4-context.html">4.4 Context: what the model reads</a></li>
      </ul>
    </div>
  </div>
</div>

## What this section covers

- From answering to acting: three kinds of task
- Which tasks an agent may do alone, must ask about first, or must never do
- What counts as an agent
- A tool call is just more text: the real input and output of one step
- The loop you already know, and the whole loop in a few lines of code
- Recorded runs on a SUMO intersection, and what the tool shows changing the plan
- Milestone paper: **ReAct**, reasoning and acting in one loop
- Workflow or agent: a scale you know from signal control; Agentless
- An agent is a model plus a harness

## From answering to acting

```{figure} ../_static/figures/AGL_Three_Cases.png
:alt: Three rows, one per kind of task. Traffic simulation: a request to retime a signal, tools for intersection info, running SUMO and submitting a plan, a draft timing plan, and a traffic engineer who approves. Safety analysis: a request about a corridor, tools for the crash database, safety models and manual search, a ranked site list, and a safety engineer. Visual inspection: a request about storm damage, tools for dashcam frames, a damage detector and map lookup, a damage report, and an inspector.
:width: 100%

Three kinds of task from across transportation research and agency practice. Each ends with a person who signs.
```

For two months we built models: networks that take an input and return a prediction. In Part II the model stops
being the whole system. It becomes one part of a loop that can look things up, run a simulator, and act. That is
what people mean by an **AI agent**.

Three kinds of task show the idea: **traffic simulation** with SUMO, **safety analysis** on agency data, and
**visual inspection and reporting** from dashcam, pavement and structure images. Part II draws its examples from
across transportation research and agency practice; SUMO simulation and safety analysis get extra depth later, with
a full workflow each in {doc}`Module 8 <../module8/index>`. Look at what changes from a model to an agent: a model answers one question, while an agent works
through a task, deciding what to look up, calling a tool, reading the result and deciding what to do next. And
look at what does not change. Every task ends with a person: an engineer approves the timing plan, an engineer
signs off the site list, an inspector signs the report. That is the checkpoint rule of
{doc}`4.1 <notes1-workflow>`, and it is the thread through all of Part II.

## Alone, ask first, or never?

Before building anything, decide what an agent should be allowed to do. Sort each task into one of three bins:
the agent may do it **alone**, must **ask a person first**, or should **never** do it.

| Task | Alone, ask first, or never? |
|---|---|
| Summarize last night's incident log for the morning briefing | |
| Draft the text of a DMS message for a crash on I-275 | |
| Post that message to the DMS | |
| Push a new timing plan to a signal controller | |
| Code the contributing factors of 400 crash narratives into the crash database | |
| Approve a RISC bonus payment to a towing company | |

There is not one right answer, but there are good reasons and bad ones. One defensible sorting: the summary can
be done alone because a person reads it before anyone acts. The DMS draft can be done alone; posting it should ask
first, because it reaches the public at once. The timing plan should ask first: an engineer approves it before it
reaches the controller. Coding 400 narratives should ask first, with a checked sample, because the database is the
record later safety studies rely on. The RISC payment: never, because it is a contractual and financial judgment.
The rule underneath every answer: **the person sits immediately before the first step that cannot be taken back.**

## What counts as an agent

Russell and Norvig's textbook definition is old and broad: "An agent is anything that can be viewed as perceiving
its environment through sensors and acting upon that environment through actuators." A thermostat qualifies, and
so does a TMC operator.

| | The textbook definition | A TMC operator | Our SUMO agent |
|---|---|---|---|
| **Environment** | what it acts on | the freeway network | one simulated intersection |
| **Observations** | what it senses | detector speeds, CCTV, 511 reports, calls | tool results: volumes, delays |
| **Actions** | what it can change | DMS messages, dispatching Road Rangers | look up, run a plan, submit a plan |
| **Measure of success** | what it tries to raise | shorter clearance time | lower delay, within the limits |

The new thing is not the definition. It is that a **language model** now fills the middle: it reads the
observations as text and writes the actions as text.

## A tool call is just more text

```{figure} ../_static/figures/AGL_Tokens.png
:alt: The five parts of the text at step 1 of a recorded run, with token counts: instructions 80, tool descriptions 382, the task 48, the model's reply with a thought and a tool call 44, and the tool result the harness pastes back 197.
:width: 100%

Everything the model read and wrote at step 1 of a recorded run, in the model's own format, with token counts from its tokenizer.
```

Here is exactly what the model read and wrote at the first step of one recorded run. At the top are the
instructions we wrote. Then come the tool descriptions, in a format the model's makers chose: each tool's name, what
it does, and its parameters as JSON, followed by a sentence telling the model how to write a call. Then the task.
Before step 1 that is 510 tokens, and 382 of them describe the tools, which the model reads again at every step.

The model's reply is a short thought and a tool call, 44 tokens. The call is just text between `<tool_call>` tags:
the model has not run anything, it has written a request. The harness reads that text, finds the tags, runs the
function, and pastes the result back inside `<tool_response>` tags (197 tokens here). Then it sends the whole,
longer text to the model again. That is all a tool call is. The model was trained to write this format; it has no
other way to touch the world. And it knows nothing about a tool except its name, its one-sentence description and
its parameter list ({doc}`4.3 <notes3-tools>`).

## The loop you already know

```{figure} ../_static/figures/AGL_Loop.png
:alt: Two loops side by side. Left, ramp metering with ALINEA: measure occupancy, decide with the ALINEA rule, act by setting the metering rate, observe the freeway respond. Right, an agent: read the task and history, the model writes a step, the harness runs the tool, the result joins the history.
:width: 100%

The agent loop is a control loop. What is new is the rule in the middle: a frozen language model instead of one equation.
```

ALINEA, the ramp-metering rule, measures occupancy downstream of the ramp, compares it with a target, adjusts the
metering rate by a gain times the difference, $r(k) = r(k-1) + K_R(\hat o - o_{out})$, and measures again: measure,
decide, act, observe. An agent is the same loop. It reads the context, the model decides the next step by writing
text, the harness acts by running the tool, and the result is observed by being added to the context.

The difference is the rule in the middle. ALINEA's rule is one line with one gain, and control theory tells you
when it is stable. The agent's rule is a model with more than a billion parameters, and nobody can write down when
it behaves. So the parts you can analyze and test are the parts around it: what it reads, what it may do, and when
the loop stops.

## The whole loop in a few lines

```python
messages = [instructions, task]           # what the model reads
for step in range(10):                    # the harness sets the step limit
    reply = model(messages)               # the model only writes text
    messages.append(reply)
    call = find_tool_call(reply)          # look for <tool_call>{...}</tool_call>
    if call is None:
        break                             # no call: the loop stops
    result = run_tool(call)               # the harness runs SUMO and checks limits
    messages.append(result)               # the result becomes text to read
    if call.name == "submit_plan":
        break                             # the task ends at the checkpoint
```

Count the lines that involve the model: one. Everything else is ordinary code you write and control: what the model
reads, which tools exist and what they check, the step limit, and the condition that ends the task. The last line
matters most for an agency. Submitting a plan ends the loop and hands the plan to a person; the agent cannot push a
timing plan to a controller, because no tool does that. **A permission you never give cannot be misused.**

## Recorded runs on a SUMO intersection

The agent in this section is real and recorded. A small open model, **Qwen2.5-1.5B-Instruct** (about 1.5 billion
parameters, small enough for a laptop or a free Colab GPU), retimes one **synthetic** intersection in SUMO through
three tools: `get_intersection_info`, `run_simulation` and `submit_plan`. Main St has two lanes each way and 1,100
veh/h per approach; 1st Ave has one lane each way and 300 veh/h; through movements only. The current plan gives 50 s
of green to north-south and 30 s to east-west, with 4 s of yellow and 2 s of all-red per phase, for 21.5 s/veh of
delay. Two timing limits apply: a 7 s minimum green (our design choice), and at least 21 s for the east-west phase,
because pedestrians crossing the 48-ft arterial walk with it (a 7 s walk plus 48 / 3.5 = 13.7 s of clearance,
rounded up to 14, following MUTCD practice). A grid search over 315 plans gives the reference answers: the best valid
plan on the grid is 54/22 at 18.5 s/veh; the best plan overall, 26/13 at 16.1 s/veh, breaks the pedestrian minimum.

We recorded the same task under four harness settings, three runs each:

- **A**: the lookup tool does not show the timing limits.
- **B**: it shows them.
- **C**: it shows them, and the harness rejects any plan that breaks one.
- **D**: as C, and the harness also checks the agent's claim: it accepts a submission only if the plan was simulated
  and beats the current plan, which the harness measures itself.

**One run, step by step.**

```{figure} ../_static/figures/AGL_Run_Trace.png
:alt: Run A/0 in three steps. Step 1, get_intersection_info, 510 tokens read. Step 2, run_simulation(50, 30), 21.5 s/veh, 751 tokens read. Step 3, submit_plan(40, 20), 956 tokens read. The plan was never simulated by the agent; in a fresh run it gives 18.8 s/veh and breaks the 21 s pedestrian minimum.
:width: 100%

A complete recorded run in condition A, unedited: the agent's thoughts in italics, its tool calls in green, what came back, and the tokens it read at each step.
```

The model looked up the intersection, simulated the current plan (21.5 s/veh), then submitted 40/20, which it never
simulated, with the reason "Reducing the green times to improve traffic flow and decrease average delay." A fresh run
gives 18.8 s/veh, so the claim happens to hold, but the plan leaves pedestrians 20 s to cross when they need 21, and
the agent could not have known: the limit was never in its context. This run is typical. **Eight of the nine runs in
conditions A to C took exactly three steps: one lookup, one simulation, a submission. Six of those nine submitted
plans were worse than the current plan**, with reasons such as "Reduced average delay per vehicle." A small model
stops early and states reasons it never checked.

**What the harness checks changes the plan.**

```{figure} ../_static/figures/AGL_Pair.png
:alt: Two traces with the same seed. In B, the agent proposes 30/20, gets 18.7 s/veh, and submits 30/20, which breaks the pedestrian minimum. In C, the harness rejects 30/20 with an error naming the 21 s pedestrian minimum; the next thought reads the error, the agent simulates 30/21 at 18.8 s/veh and submits it.
:width: 100%

The most controlled comparison in the recorded runs: same model, same seed, same first plan; only the harness differs.
```

With the same seed, the first two steps under B and C are identical, word for word: both agents saw
"minimum_green_ew_s: 21" in the lookup result, and both proposed 30/20. Under B the simulation simply ran (18.7
s/veh) and the agent submitted a plan that breaks the pedestrian minimum it had been shown one step earlier. Under C
the harness returned an error naming the rule; the next thought read it ("The simulation returned an error because
the pedestrian minimum for the east-west phase is set at 21 seconds"), and the agent simulated and submitted 30/21
(18.8 s/veh). **Showing a rule is advice; checking it in the harness is a rule.** The cost of the rule here was
0.1 s/veh. Condition D, and how to grade all four, are in {doc}`4.3 <notes3-tools>`.

**Our first two runs failed, and both failures were harness bugs.** In the first, the model's reply hit the 200-token
limit we had set in the middle of a tool call; the harness found no complete call and stopped at step 2. In the
second, the model wrote 14 thoughts in one reply and no call. In them it claimed the delay "decreased from 24 seconds
to 23.6 seconds" (it had measured 23.6 once; the 24 was invented), and it wrote that the traffic engineer had
already reviewed the plan, which never happened. That is ReAct's failure table (below) in our own logs. The fix was
in the harness, not the model: the harness now starts each reply, lets the model write one line of thought, then
opens the tool call. Both failed runs are kept with the reproducer, because **most agent bugs are harness bugs, and
you find them only by reading the traces.**

## Milestone paper: ReAct

**ReAct** (Yao, Zhao, Yu, Du, Shafran, Narasimhan and Cao; Princeton University and Google Research; ICLR 2023) is
the paper that made this loop standard. It starts from two failures. **Chain of thought**, prompting a model
to write out its reasoning before it answers, lets a model reason step by step but never checks anything, so
when its memory is wrong it reasons confidently from a wrong fact. Earlier agents did the opposite: they **acted
without thinking**, so they could not put together what they found, and in a game they would repeat an action that
had just failed.

ReAct's idea is small: let the model write a **thought** between actions. A thought changes nothing outside the
model; it only becomes part of the text the model reads at the next step. That is enough to make reasoning and
acting help each other.

```{figure} ../_static/figures/AGL_ReAct_Four.png
:alt: The HotpotQA question about the Apple Remote answered four ways. Standard answers iPod, wrong. Chain of thought reasons from the invented fact that the remote was designed for Apple TV, wrong. Act-only searches three times and finishes with yes, wrong. ReAct alternates thoughts, searches and observations, changes its query when Front Row is not found, and answers keyboard function keys, right.
:width: 100%

Four ways to answer one two-hop question (redrawn from Yao et al., 2023, Fig. 1). Gold italic text is invented; green text was read from Wikipedia.
```

The question is two-hop: aside from the Apple Remote, what other device can control the program the Apple Remote
was originally designed to interact with? **Standard** prompting answers "iPod": wrong. **Chain of thought**
reasons fluently from an invented fact, that the remote was designed for Apple TV: wrong, and confidently wrong.
**Act-only** searches the right pages, and even retries when Front Row is not found, but it never writes down what
it learned, and finishes with "yes". **ReAct** makes the same searches with a thought between them. Thought 2 says
what it learned and what to look up next; thought 3 notes that Front Row was not found and picks the software page;
thought 4 reads the answer off that page: keyboard function keys. For an engineer, the thoughts buy one more thing: **a record of why each
action was taken**, which is what a reviewer reads.

**The mechanism.** The actions are deliberately simple: `search[entity]` returns the first five sentences of a
Wikipedia page (or five similar titles), `lookup[string]` returns the next sentence containing a string, and
`finish[answer]` ends the task. Nothing is trained: the model is PaLM with 540 billion parameters, frozen, shown
six hand-written example trajectories for HotpotQA and three for FEVER. The one equation is about the action
space. An ordinary agent picks actions from a set $A$; ReAct adds $L$, the space of language:

$$
\hat{A} = A \cup L .
$$

**In words:** thinking is allowed to be an action, and its only effect is on what the model reads next. On the
question tasks every step has a thought; on the household and shopping tasks the model decides when to think.

:::{admonition} Going deeper &mdash; the agent as a policy
:class: dropdown
The paper writes an agent as a policy $\pi(a_t \mid c_t)$ that maps a context $c_t = (o_1, a_1, \dots, o_t)$ of
observations and actions to the next action. ReAct changes only the action set. A thought $\hat a_t \in L$ gets no
observation back; the context simply grows, $c_{t+1} = (c_t, \hat a_t)$. The policy is the frozen language model
itself, conditioned on the few-shot examples and the context.
:::

**What the results say.**

| Task (measure) | Act only | ReAct | Best prompted result |
|---|---|---|---|
| HotpotQA (exact match) | 25.7 | 27.4 | 35.1, ReAct → CoT-SC |
| FEVER (accuracy) | 58.9 | 60.9 | 64.6, CoT-SC → ReAct |
| ALFWorld (success %) | 45 | 71 (best of 6), 57 (average) | ReAct |
| WebShop (success %) | 30.1 | 40.0 | ReAct; human experts 59.6 |

On the two interactive tasks, ALFWorld (a text-based household game) and WebShop (an online shopping site),
ReAct is clearly better than acting alone. These are tasks where the agent must recover from dead ends. On the
question tasks the picture is mixed: the best results come from combining ReAct with CoT-SC, chain of thought sampled
21 times with a majority vote.

:::{admonition} Before you trust this result
:class: important
**What is the baseline?** The same frozen model with parts of the prompt deleted: no thoughts (act only), no
actions (chain of thought), or neither (standard). On the two games, also trained agents: BUTLER on ALFWorld (37%),
imitation plus reinforcement learning on WebShop (28.7%).

**How was the data split, and why is that honest?** 134 unseen ALFWorld games and 500 WebShop instructions, none
used in the prompts.

**What does it do on the ugly cases?** On HotpotQA, ReAct (27.4) scores below standard prompting (28.7) and plain
chain of thought (29.4), let alone CoT-SC (33.4), and every prompted method is far below a supervised model trained
on the dataset (67.5).
:::

**How ReAct fails.** The most useful table in the paper is about failures. The authors labelled by hand fifty
failed HotpotQA runs of each method.

| What went wrong (50 failed runs each) | ReAct | Chain of thought |
|---|---|---|
| Hallucination: an invented fact | 0% | 56% |
| Reasoning error, including repeating the same steps | 47% | 16% |
| The search returned nothing useful | 23% | – |
| The question or its label was ambiguous | 29% | 28% |

Chain of thought fails mostly by inventing facts. ReAct almost never does, because its facts come from the page it
just read, but it fails in two new ways: **loops**, repeating the same thought and action without getting out, and
**bad tool results**, where the agent is only as good as its search. Grounding a model in tools removes one failure
and adds two. Those two are what you design a harness against, and the first things to look for in a trace.

**Reading an agent paper for your own research.** Six questions work on any agent paper. Here they are for ReAct.

| Question to ask of any agent paper | ReAct's answer |
|---|---|
| What does the agent see at each step? | The question, its own past thoughts and actions, and the last observation |
| What can it do? | Three text actions, search, lookup and finish, plus thinking |
| When does the loop stop? | When it calls finish, or after a step limit |
| What is in its context, and what is left out? | Everything so far; nothing is summarized or forgotten |
| Where is the person, and what cannot be undone? | No approval step; actions touch only Wikipedia, a text game and a sandbox shop |
| How was it judged? | Exact match, accuracy or success rate, against prompt-ablated baselines and trained agents |

The fifth row is the one to underline for transportation. ReAct's actions touch only Wikipedia, a text game and a
sandbox shop; as the authors note, their models could not really buy products or edit Wikipedia (an appendix does
show a person editing the agent's thoughts mid-run). The moment your agent's action is a timing plan, a
database record or a public message, that row becomes the most important design decision you make. It is also
where the research openings are: ReAct on calibration, where the observation is a GEH statistic and the stopping
rule matters; ReAct over a crash database, where a search error is a zero-row query; a study of whether the thoughts
are a faithful record an engineer can audit.

## Workflow or agent: a scale you know

```{figure} ../_static/figures/AGL_Ladder.png
:alt: Three steps rising left to right: a fixed-time plan beside a script or fixed workflow (tagged Agentless), actuated control beside a workflow with branches, and adaptive control beside an agent (tagged ReAct and our SUMO agent). The axis reads who picks the next step: the engineer in advance, rules on what is measured, the model while it runs.
:width: 100%

The same scale as signal control. An agent earns its cost only when the next step cannot be written down in advance.
```

A fixed-time plan decides everything in advance. Actuated control follows rules an engineer wrote, triggered by
detector calls. Adaptive control chooses the timing itself from what it measures. AI systems sit on the same scale:
a script or a fixed workflow does the same steps every time, a workflow with branches follows rules you wrote, and
an agent picks its own next step. And the lesson is the same as in signal control. Adaptive control earns its cost
where demand is unpredictable; on a corridor with steady, known demand, a well-timed fixed plan is hard to beat.
**If you know the steps, write a workflow.**

**Agentless** (Xia, Deng, Dunn and Zhang, University of Illinois; FSE 2025) is the paper that argues this side,
and reviewers will ask you about it. It looked at agents that fix bugs in real software projects, which decide
every step themselves and "can take upwards of 30 or 40 turns". Agentless fixes the steps instead: find the file,
then the function, then the lines; write 40 candidate patches; let tests pick one. The model writes text inside
each step but never decides what to do next. On 300 real GitHub issues (SWE-bench Lite) it fixed 96, more than
every open-source agent of the time (which fixed 54 to 92), at $0.70 an issue; cheaper agents existed, but the best
of them fixed 16 fewer. Look at where the fixes came from: a majority vote among the 40 patches fixed 77, adding the
project's existing tests 81, and adding small tests the model writes to reproduce each bug 96.

:::{admonition} Before you trust this result
:class: important
**What is the baseline?** Published leaderboard scores of the agents, copied rather than re-run.

**How was the data split, and why is that honest?** SWE-bench Lite, 300 real issues. The authors read all 300 by
hand, removed 51 that gave away the fix or lacked the information needed, and the ranking stayed "roughly the same".

**What does it do on the ugly cases?** Closed-source agents scored higher (up to 43.0%), and did better on issues
that gave no clue where the bug was.
:::

For transportation the lesson is direct. A safety screening that follows the Highway Safety Manual's steps, or an
inspection report with a fixed template, is an Agentless problem: write the steps, put the model inside them, and
put the effort into the check at the end. Ask what plays the role of the tests in your project: a SUMO run that must
finish without teleports and match the counts; a query whose row count must match the agency dashboard; a report
whose every claim points to a frame and a detector box.

## An agent is a model plus a harness

```{figure} ../_static/figures/AGL_Harness.png
:alt: A frozen language model in the middle, surrounded by six harness parts: instructions and skills, tools, context and memory, the loop and its plan, permissions and checkpoints, the log and the tests, each labelled with the module that covers it. What leaves the harness, a plan, a list or a report, goes to an engineer who approves.
:width: 100%

The organizing idea of Part II: you will rarely change the model; you will design the harness around it.
```

The **model** is the part that writes text. The **harness** is everything else: the instructions it starts with,
the tools it can call and how their results are written back, what it remembers, the loop and when it stops, what
it is allowed to touch, and the log of everything it did. You can improve an agent in two ways: change the model,
by fine-tuning ({doc}`Module 6 <../module6/index>`), or change the harness. In the runs above, moving the pedestrian limit from the
model's reading into the harness's code changed the plan; nothing about the model changed. For the rest of Part
II, almost everything you design is harness: tools and context here, memory, skills and planning in Module 5,
measurement and fine-tuning in Module 6, permissions and people in Module 7, and full workflows for SUMO simulation and safety analysis in
Module 8.

| Fit card — the agent loop | |
| --- | --- |
| **Idea in one sentence** | A language model whose replies can be tool calls, run in a loop by a program that executes them and feeds the results back. |
| **Why it works** | A tool call is just text, so a model trained on text can write one; the results are text too, so the model can reason about them. |
| **Fits these tasks** | Multi-step work with dead ends: simulation runs, database queries, document lookups. *Leverage: retrieval, generation, extraction.* |
| **Needs this data** | Tools with clear descriptions, test tasks with known answers, and a log of every run. |
| **Breaks when** | Tools return unclear or empty results, the agent loops, or it acts on something that cannot be undone without a checkpoint. |
| **Keep the classical method when** | The steps are known in advance (write a workflow), or an optimizer already searches the space (Webster's formula, a grid search, a calibration routine). |

## Check yourself

1. Your agent retimes a signal in SUMO and proposes a plan with a 12-second side-street green. Where should the
   timing limits live: in the instructions, in the tool's output, or in the harness? Defend your choice.
2. A colleague says ReAct "solved hallucination". Using the failure table, write two sentences that correct them.
3. Your team's project processes 2,000 dashcam frames the same way every week. Agent or workflow? What one fact
   would change your answer?

## Sources

- Yao, S., et al. (2023). ReAct: Synergizing reasoning and acting in language models. *ICLR*.
  [arXiv:2210.03629](https://arxiv.org/abs/2210.03629).
- Xia, C. S., Deng, Y., Dunn, S., & Zhang, L. (2025). Demystifying LLM-based software engineering agents (preprint
  title: Agentless). *Proc. ACM Softw. Eng.* 2 (FSE). [arXiv:2407.01489](https://arxiv.org/abs/2407.01489).
- Russell, S., & Norvig, P. *Artificial Intelligence: A Modern Approach*, ch. 2.
- Papageorgiou, M., Hadj-Salem, H., & Blosseville, J.-M. (1991). ALINEA: a local feedback control law for on-ramp
  metering. *Transportation Research Record* 1320.
- Qwen Team (2024). Qwen2.5-1.5B-Instruct (Apache-2.0). Lopez, P. A., et al. (2018). Microscopic traffic simulation
  using SUMO. *IEEE ITSC*.
- Fried, D., & Neubig, G. (2026). [CMU 11-768 AI Agents](https://www.cmu-agents.com/), lecture 1.

---

Next: {doc}`notes3-tools` &mdash; what an agent can reach, and how a model learned when to call a tool.
