(agent-architectures)=
# 5.5 Agent architectures: one loop, four questions

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 5 &middot; Section 5.5</span>
    <span class="notes-card-session">Session: Skills, memory, and planning</span>
  </div>
  <p class="notes-card-lede">Blog posts and vendor guides list eight, eleven or more &ldquo;agent architectures,&rdquo; and no two lists agree. This section replaces the lists with one loop and four design questions, places every named pattern on them, and measures one of the choices on the small SUMO agent of Section 5.2. The interactive companion at the end holds the full catalogue: fit cards for every pattern, twelve transportation tasks, and the published traffic agents.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Read it first</h4>
      <ul>
      <li><a href="notes2-loop.html">5.2 A model in a loop</a></li>
      <li><a href="notes3-tools.html">5.3 Tools: what an agent can reach</a></li>
      </ul>
    </div>
    <div>
      <h4>Used again in</h4>
      <ul>
      <li><a href="../module7/index.html">Module 7 &mdash; Agents and people in an agency</a></li>
      <li><a href="../module8/index.html">Module 8 &mdash; Building transportation harnesses</a></li>
      </ul>
    </div>
  </div>
</div>

## What this section covers

- One loop that every agent runs
- Four design questions, and where each one sits on the loop
- Why the published lists disagree
- Q1 Control: step by step, plan first, check then retry &mdash; measured on the SUMO agent
- Q2 Reach: tools, documents, memory and skills
- Q3 Team: three ways to wire several agents, and the case for one
- Q4 Oversight: the gate before the step that cannot be undone
- The published traffic agents, placed on the four questions
- The interactive companion

## One loop

```{figure} ../_static/figures/AGA_One_Loop.png
:alt: A request enters the context window; the model reads it and writes a tool call; the harness runs the tool against outside data and adds the result to the context; the loop repeats until the model writes a final answer.
:width: 100%

The model only writes text; the harness runs each tool call and feeds the result back.
```

Every agent in this module runs the loop of {doc}`5.2 <notes2-loop>`. The model reads its context and writes the next
step as text. The harness runs any tool call and adds the result to the context. The loop stops when the model writes a
final answer, or when the harness hits a step or budget limit.

Every &ldquo;architecture&rdquo; you will meet is a choice about some part of this loop. That is why a list of them reads
as a jumble: the items are not alternatives to one another. They answer different questions.

## Four design questions

```{figure} ../_static/figures/AGA_Four_Questions.png
:alt: The loop with four gold badges. Q1 Control sits at the model, Q2 Reach at the read tools, Q3 Team at other agents, Q4 Oversight at an approval gate before the write tools.
:width: 100%

An agent design is four answers, not one pick from a list.
```

- **Q1 Control.** How does the agent pick its next step: one step at a time, from a plan written first, or by
  checking a result and retrying?
- **Q2 Reach.** What can it reach outside the model: tools, documents, notes from past tasks, written procedures?
- **Q3 Team.** How many loops run, and who reports to whom: one agent, a router, a supervisor with workers, or peers
  sharing a board?
- **Q4 Oversight.** Where does a person approve: never, before the steps that cannot be undone, or at every step?

One question comes before the four: does the model choose the path at all?

```{figure} ../_static/figures/AGA_Workflow_vs_Agent.png
:alt: Two rows. A workflow: question, retrieve top five passages, model writes the answer, answer, always in that order. An agent: question, model, tools in a loop, answer when the model judges it complete.
:width: 100%

Workflow or agent depends on who picks the next step, not on which parts the system has.
```

In a **workflow** your code fixes the steps; in an **agent** the model picks them while it runs. Anthropic's guide
draws this line first and advises the simplest system that works, often no agent at all. If you can write the steps
down, write a workflow.

## Why the lists disagree

Two widely shared posts list 11 and 8 &ldquo;architectures.&rdquo; Together they give 19 labels, but only about ten
distinct ideas plus one bundle: ReAct appears in both, as do plan-and-execute, reflection, tools, memory, retrieval and
multi-agent; the first post adds a router, a supervisor, a skill library and human-in-the-loop; the second adds an
&ldquo;autonomous loop,&rdquo; which is several answers at once with no person watching.

The industry guides disagree too, each in its own direction. Microsoft's Agent Framework names five orchestrations, all
about wiring several agents (Q3). Anthropic's guide names five workflow shapes that mix control and wiring (Q1 and Q3).
OpenAI's guide
separates a single agent from two multi-agent patterns and advises getting the most out of one agent first. A
transportation survey (Nie, Sun and Ma, 2025) sorts by a different question altogether: what job the language model does
in the transportation system. Tab 2 of the companion places all eight lists on the four questions.

:::{admonition} Answer key to the in-class sorting
:class: dropdown
```{figure} ../_static/figures/AGA_Sorting_Key.png
:alt: Five columns. Control holds ReAct, plan-and-execute and reflection from both posts. Reach holds tools, RAG, memory and the skill library. Team holds router, supervisor and multi-agent. Oversight holds human-in-the-loop. The autonomous loop sits apart as a bundle.
:width: 100%

Labels in one column answer the same question; a real agent gives an answer in every column.
```
:::

## Q1 Control: three ways to pick the next step

```{figure} ../_static/figures/AGA_Control_Three_Ways.png
:alt: Three columns. Step by step: think, act, observe, back to think. Plan first: a planner writes a five-item list, an executor runs it, re-plan on failure. Check then retry: the model drafts, a checker outside the model simulates and compares, pass or revise.
:width: 100%

The loop is the same in all three; what changes is who decides the next step.
```

**Step by step** (ReAct) lets each step use what the last one showed; it fits diagnosis, where you cannot know the next
question until you see the last answer. **Plan first** writes the list once and runs it; it fits tasks with a known
procedure, such as a traffic impact study or HSM network screening. **Check, then retry** sends the result to a check
outside the model and revises until it passes; it is only as good as that check. A model rereading its own work without
outside feedback gains little and sometimes gets worse (Huang et al., 2024).

### Measured on the SUMO agent

We gave the agent of {doc}`5.2 <notes2-loop>` the same task three ways: same model (Qwen2.5-1.5B-Instruct), same
synthetic intersection, same timing limits enforced by the harness, same limit of 10 model calls, and the same 10 model
seeds for each style. Step by step and check-then-retry run the agent of 5.2 unchanged (its conditions C and D). Plan first
needed more than a new instruction: a fourth tool, `write_plan`, its own system prompt, and a harness that opens the first
`write_plan` call. The model looks up the intersection, lists up to five signal timings in one call, and the harness
simulates every timing within the limits and returns all the delays; then the model submits or tests more. In every style,
a timing that breaks a limit is rejected by the harness, not simulated. Check-then-retry adds one rule at submission: the
harness accepts a timing only if it was simulated and beats the current one.

| | Step by step | Plan first | Check, then retry |
| --- | ---: | ---: | ---: |
| Submitted a timing | 10 of 10 | 8 of 10 | 4 of 10 |
| Submitted a timing better than the current one (21.5 s/veh) | 4 of 10 | 6 of 10 | 4 of 10 |
| Mean delay of submitted timings (s/veh) | 21.2 | 20.8 | 19.3 |
| Timings simulated per run | 1.1 | 5.1 | 2.7 |
| Timings tried that broke a limit (total) | 2 | 107 | 7 |
| Runs that simulated the current timing | 1 of 10 | 3 of 10 | 2 of 10 |
| Model calls per run | 3.4 | 5.6 | 7.7 |
| Tokens read per run | 2,774 | 9,845 | 10,055 |

Timings better than the current one came back in 4 of 10 runs step by step, 6 of 10 plan first, and 4 of 10 with check-then-retry. Plan first simulated 5.1 timings per run on average, against 1.1 step by step and 2.7 with the check; it also wrote 107 timings that broke a limit, which the harness rejected. The most expensive style was check, then retry, at 10,055 tokens read per run, 3.6 times the 2,774 of step by step. In 6 of 10 check-then-retry runs the model hit the 10-call limit before the harness accepted a timing; the check had rejected 27 submissions in those runs. Every timing the check let through beat the current one, which is what the check requires.

On this one task, plan first returned a better timing most often, but the gap is small: 6 of 10 against the next best 4 of 10. If the styles were equally good, a split at least this uneven would still turn up with probability 0.66 (Fisher's exact test), so ten runs per style cannot settle which is better.

The plan-first style also needed harness work before it ran at all. On the first try the model wrote an empty list, then
lists cut off half-way, and never simulated a single timing. The harness now writes the opening of the first list, as it
already writes &ldquo;Thought:&rdquo;, and reads every complete timing in it. A pattern is only as good as the
harness that runs it. The companion's tab 6 lists every run.

:::{admonition} Before you trust this result
:class: important
**What is the baseline?** The current timing 50/30 at 21.5 s/veh, and a plain grid search with no model: of 315 timings,
the best one within the limits is 54/22 at 18.5 s/veh. The grid is coarse (steps of 4 s north-south and 3 s east-west): 2 runs submitted 35/21 at 18.4 s/veh, a timing between its points, 0.1 s below the grid&rsquo;s best. On one SUMO seed, a gap that small may not be real. Missing: Webster's method, the
classical formula an engineer would try first (TrafficGPT gives its agent a Webster tool).

**How was the data split, and why is that honest?** There is no split. One synthetic intersection was used both to build
the plan-first harness (after its first attempt failed) and to score all three styles, with one SUMO seed and 10 model
seeds per style, in one software environment. This compares control styles on one task; it says nothing about other
intersections, models or cities. The runs in 5.2 were recorded in another environment, so single runs differ from those.

**What does it do on the ugly cases?** Count the runs that submitted nothing and the timings no better than the one already
in the field: 0, 2 and 6 runs submitted nothing; 6, 2 and 0 submitted a timing no better than the current one.
:::

| Fit card &mdash; plan first | |
| --- | --- |
| **Idea in one sentence** | Write the list of steps once, run them, and re-plan only when a step fails. |
| **Why it works** | A written plan can be checked before anything runs, and the steps can run without a model call each. |
| **Fits these tasks** | Tasks with a known procedure: a traffic impact study, HSM screening, post-storm signal restoration. *Leverage: generation, judgment.* |
| **Needs this data** | A procedure or template to plan from, and a way to tell that a step failed. |
| **Breaks when** | The plan is written before the data is seen, the plan is wrong, or the model writes lists badly. |
| **Keep the classical method when** | No step needs judgment: then drop the model and run a workflow, or let a plain search do it. |

## Q2 Reach: one mechanism, four contents

```{figure} ../_static/figures/AGA_Reach_One_Mechanism.png
:alt: A tall context window beside the model, and three stores outside it: documents, past episodes and procedures. Fetch arrows copy stored text into the context; save arrows write episodes and procedures back.
:width: 100%

RAG, memory and skills all copy stored text into the context; they differ in what is stored and who writes it.
```

Tools ({doc}`5.3 <notes3-tools>`) let the agent act and fetch exact numbers. The other three are the same move:
fetch stored text into the context window. **Documents** (RAG, {doc}`5.4 <notes4-context>`) are written by people
and indexed ahead of time. **Past episodes** (memory) are notes the agent saves during or after a task. **Procedures**
(skills) are step lists, written by people or saved by the agent once something works. The &ldquo;four memory
levels&rdquo; of one blog post follow a common analogy to human memory (see Weng, 2023); in an agent there are only two
places, the context window and the storage outside it.

## Q3 Team: three wirings, and the case for one agent

```{figure} ../_static/figures/AGA_Team_Three_Wirings.png
:alt: Three columns. A router hands a citizen request to one specialist agent. A supervisor assigns three corridor workers and merges their results into one report. A designer agent and a reviewer agent share a board until no issues remain.
:width: 100%

More agents buy parallel work and separate contexts, and every extra loop costs tokens.
```

A **router** hands each request to one specialist. A **supervisor** splits a task, lets workers run in parallel, and
merges what comes back. **Peers** take turns on a shared board. Each agent is the same loop, so each extra agent is
another loop's worth of tokens: in Anthropic's report, its multi-agent research system used about 15&times; the tokens
of a chat. Split a task only when its parts truly do not depend on each other. Corridors with spillback between them do;
OpenAI's guide puts it as &ldquo;maximize a single agent's capabilities first.&rdquo;

## Q4 Oversight: the gate before the step that cannot be undone

```{figure} ../_static/figures/AGA_Oversight_Checkpoint.png
:alt: The loop for a TMC assistant. Read tools for detector speeds, CCTV and the SunGuide event log run freely; a gold diamond, operator approves, stands between the model and the write tools that post a DMS message or change a timing plan; approved actions are logged and labeled AI-drafted.
:width: 100%

Human-in-the-loop is not a separate architecture; it is a gate on the write tools of any loop.
```

Read tools run freely; write tools pass the gate; the gate sits right before the first step that cannot be undone, the
checkpoint rule of {doc}`5.1 <notes1-workflow>`. Agencies already require this. FDOT's AI policy, as its Chief Engineer
of Operations describes it, holds that &ldquo;humans are fully responsible for the work and product outputs involving
AI&rdquo; and that AI involvement must be disclosed. A District Five meeting summary lists the same policy as requiring
that &ldquo;AI usage must engage humans throughout the process, with human involvement in reviews and decisions&rdquo;
(the summary notes it does not reflect FDOT's concurrence). TxDOT's January 2026 update requires &ldquo;a mandatory
validation of outputs&rdquo; and a &ldquo;Human-in-the-Loop&rdquo; requirement. Module 7 turns these rules into harness features.

## The published traffic agents on the four questions

```{figure} ../_static/figures/AGA_Read_TrafficGPT.png
:alt: TrafficGPT drawn on the loop: prompt management as the context window, gpt-3.5-turbo as the model, traffic foundation models as the tools, a trip database and SUMO outside, and four answers along the bottom.
:width: 100%

TrafficGPT (Zhang et al., 2024) redrawn on the loop.
```

```{figure} ../_static/figures/AGA_Read_OpenTI.png
:alt: Open-TI drawn on the loop: a traffic-designed prompt, GPT-3.5, a pool of twelve tools, and a handoff to a second model, ChatZero, that acts as the signal controller.
:width: 100%

Open-TI (Da et al., 2024) redrawn on the loop; its one extra wire is a handoff to a second model.
```

Read a new agent paper by finding the loop first. TrafficGPT's &ldquo;prompt management&rdquo; is the context
window and its traffic foundation models are the tools; Open-TI adds one wire, a handoff to a second model that acts as
the signal controller. Tab 5 of the companion places six published systems (TrafficGPT, Open-TI, LLMLight, LA-Light,
SUMO-MCP and SimSkill) on the four questions. All six act only in simulation or on stored data, and **none of the six
puts a person's approval in front of an action**, while the agency documents above require a person in the process. A traffic agent with a real answer to Q4, tested with real operators, is an
open research gap.

## Interactive companion

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion &mdash; Agent architectures: one loop, four questions</span>
    <a href="../_static/companions/Agent_Architectures_Companion.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/Agent_Architectures_Companion.html"
          title="Agent architectures: one loop, four questions" loading="lazy"></iframe>
</div>

Seven tabs: a recorded run step by step, eight lists placed on the four questions, a fit card for every pattern,
twelve transportation tasks with their four answers and a helper for your own, the published traffic agents and what
agencies ask for, the measured comparison above, and judgment questions.

## Check yourself

1. A district wants engineers to ask questions about its Standard Specifications and get the page cited. Workflow or
   agent? Which answer to Q2, and where is the check?
2. A lab mate proposes a reflection loop in which the model rereads its own crash-narrative summary and fixes the errors.
   What do you ask first?
3. Write your final project's agent as four answers, one line each, and name the case that would change each one.

## Sources

- Anthropic (2024). [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents).
- Anthropic (2025). [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system).
- OpenAI (2025). [A practical guide to building agents](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf).
- Microsoft (2026). [Workflow orchestrations](https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations), Agent Framework.
- Yao, S., et al. (2023). ReAct. *ICLR*. [arXiv:2210.03629](https://arxiv.org/abs/2210.03629).
- Wang, L., et al. (2023). Plan-and-Solve prompting. *ACL*. [arXiv:2305.04091](https://arxiv.org/abs/2305.04091).
- Shinn, N., et al. (2023). Reflexion. *NeurIPS*. [arXiv:2303.11366](https://arxiv.org/abs/2303.11366).
- Huang, J., et al. (2024). Large language models cannot self-correct reasoning yet. *ICLR*. [arXiv:2310.01798](https://arxiv.org/abs/2310.01798).
- Weng, L. (2023). [LLM powered autonomous agents](https://lilianweng.github.io/posts/2023-06-23-agent/).
- Nie, T., Sun, J., & Ma, W. (2025). Exploring the roles of large language models in reshaping transportation systems. [arXiv:2503.21411](https://arxiv.org/abs/2503.21411).
- Zhang, S., et al. (2024). TrafficGPT. *Transport Policy* 150, 95&ndash;105. [arXiv:2309.06719](https://arxiv.org/abs/2309.06719).
- Da, L., et al. (2024). Open-TI. *International Journal of Machine Learning and Cybernetics* 15, 4761&ndash;4786. [arXiv:2401.00211](https://arxiv.org/abs/2401.00211).
- Central Florida TSM&O Consortium (2024). [Meeting summary, October 24, 2024](https://cflsmartroads.com/consortium/October2024TSMOConsortiumMeetingSummary.pdf). FDOT District Five.
- Powell, R. (2025). [FDOT's approach for artificial intelligence success](https://www.hntb.com/think/think-innovation-in-motion-fdots-approach-for-artificial-intelligence-success/). HNTB THINK.
- Texas Department of Transportation (2026). [Artificial Intelligence Strategic Plan, January 2026 update](https://www.txdot.gov/content/dam/docs/division/str/txdot-ai-strategic-plan-update-jan-2026.pdf).
- Qwen Team (2024). Qwen2.5-1.5B-Instruct, the model in the measured runs.
- Fried, D., & Neubig, G. (2026). [CMU 11-768 AI Agents](https://www.cmu-agents.com/), lectures on planning and multi-agent systems.

---

Next: {doc}`Module 6 <../module6/index>`, evaluating agents and making them better.
