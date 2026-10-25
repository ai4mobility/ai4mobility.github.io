(agent-tools)=
# 5.3 Tools: what an agent can reach

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 5 &middot; Section 5.3</span>
    <span class="notes-card-session">Session: How an agent works</span>
  </div>
  <p class="notes-card-lede">An agent is only as useful as what it can reach. This section is about the tools: how a tool is described to a model, how a model learned to decide when to call one (the milestone paper Toolformer, read in depth), code as a richer kind of action, the protocol that lets one tool serve many agents (MCP), and what the first published traffic agents show and do not show. It ends with how to grade an agent's tool use against a baseline that needs no model.</p>
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
- A tool is a contract: name, description, parameters, result
- What a harness can check about a tool call, and what it cannot
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
Protocol (MCP)**, released by Anthropic as an open standard in November 2024, is the standard plug.

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

---

Next: {doc}`notes4-context` &mdash; what the model reads on every call, and how to bring knowledge in from outside.
