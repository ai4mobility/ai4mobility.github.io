# Module 5 — Understanding AI Agents: Reasoning, Tool Calling, Skills, Memory, Planning, and Coordination

*Part II, AI Agents for Mobility · lectures 1&ndash;2 of 5. The class schedule is on the {doc}`../syllabus` page.*

## Session topics

- **How an agent works:** a model in a loop, workflow vs. agent, the model and its harness, tool use and MCP,
  context engineering and RAG
- **Skills, memory, and planning:** agency procedures as skills, what an agent should remember, planning and
  re-planning, steps that cannot be undone, and coordinating several agents

## Overview

Part II of the course is about **AI agents**: systems in which a language model does not just answer a
question but works through a task — calling tools, reading the results, and deciding what to do next.
This module covers how that works, over two sessions. The first takes an agent apart: the loop, the
tools it calls, and what it reads. The second covers what an agent carries from one task to the next,
how it plans, and how several agents share a task.

Four ideas carry the whole of Part II.

- **An agent is a model in a loop.** The model writes a short, structured request to use a tool. A
  program runs it, the result is pasted back into the model's input, and the loop repeats until the model
  decides the task is done. The model never touches the simulator or the database itself; it only writes
  text that something else executes.
- **There is a scale from a fixed workflow to a free agent.** In a workflow, a person decides every step
  in advance. In an agent, the model decides them while it runs. Signal control has the same scale:
  fixed-time, actuated, adaptive. Adaptive control pays off when demand is unpredictable, and an agent
  pays off only when the steps cannot be written down in advance. If you know the steps, write a workflow.
- **An agent is a model plus a harness.** The harness is everything around the model: its instructions,
  its tools, its memory, the loop, and its permissions. You will almost never change the model. You will
  build harnesses, and {doc}`Module 8 <../module8/index>` builds them for transportation.
- **What transportation adds is the lever.** Every technique in Part II — retrieval, tools, skills,
  memory, planning, fine-tuning, evaluation, human review — was built to work in any field. For each one
  we ask what transportation researchers and engineers can add to make it work better: traffic flow and
  safety theory, an agency's decades of procedures and lessons, and its data. The harness is where that
  knowledge goes. Each lecture ends with ten minutes on this question for your own project, and every idea
  is tested against the general version without it.

**Reasoning comes before acting.** Each time round the loop, the model decides what to do next, and it
often decides better when it first writes out its steps. In this course a model *reasons* when it writes
intermediate steps before its final answer, checks and revises them, and those steps measurably raise its
accuracy. Chain-of-thought prompting asks a model for those steps; reasoning models such as OpenAI's o1
and DeepSeek-R1 are trained to write them on their own. ReAct ({doc}`5.2 <notes2-loop>`) interleaves the
steps with tool calls. A clear chain of steps is still not proof that the answer is right. How
reinforcement learning trains a reasoning model comes in {doc}`Module 6 <../module6/index>`.

The examples in Part II come from across transportation research and agency practice, so you should
find your own kind of work among them. Two topics get extra depth: **traffic simulation with SUMO** (this
module's lab and a full workflow in Module 8) and **transportation safety analysis** (the Module 6 lab and
a full workflow in Module 8). In the first session the examples are an agent that runs a SUMO simulation
through tools and reads the result, an agent that retrieves the right passage of an agency manual before
it answers, and an agent that calls live traffic data such as Florida 511 incident reports.

**The first session's transportation question.** What should your agent compute itself, and what should it hand
to a validated engineering tool such as SUMO or an HCM procedure? And how should traffic be described in
its context: as raw detector data, or as the bottleneck and queue that traffic flow theory points to?

### Skills, memory, planning, and coordination

An agent that starts every task from nothing is slow, and it makes the same mistakes twice. The second
session covers three ways an agent carries what it knows from one task to the next, and one way to split a task
too big for a single agent.

**Skills.** A skill is a written procedure the agent opens only when a task calls for it: a short
description is always visible, and the full instructions load on demand. Agencies already write these —
standard operating procedures, design manuals, checklists — so turning one into a skill is often the
cheapest improvement available. It is not free: in one benchmark, curated skills raised the average pass
rate from 33.9% to 50.5%, but made results worse on 13 of 87 tasks, because a skill can push aside a
better default.

**Memory.** What should an agent keep from past runs — a fact, a lesson, a whole episode — and when
should it update or delete what it kept?

**Planning.** A plan is a written statement of what the agent intends to do, so it can be checked before
anything happens. Some plans should be fixed up front; others need re-planning as new information
arrives. Every plan should mark the steps that cannot be undone, and the constraints that apply to the
whole task rather than to one step.

**Several agents.** A manager agent can hand pieces of a task to helper agents. Sometimes that helps.
Often one agent that sees the whole task does better, because a hand-off is a summary and summaries drop
things.

The main planning example is restoring traffic signals after a hurricane: read the damage reports,
check the generator stock, decide the order of work, and only then file the work order — the step that
cannot be undone. Other examples come from agency practice and research: an FDOT procedure written as a
skill, and a manager agent with helper agents working through a literature review (how driver-assistance
systems change freeway capacity, say) while keeping notes in memory between sessions.

**The second session's transportation question.** Which parts of an agency's decades of practice — its
procedures, after-action reviews and lessons from past storms — can become skills, memory and plan
templates, and which cannot be written down?

Part II adapts the structure of CMU 11-768 *AI Agents* (Fall 2026, Daniel Fried and Graham Neubig) and
rebuilds it around transportation research and agency work.

## The module, page by page

<div class="practice-table-wrap">
<table class="practice-table notes-map">
<thead>
<tr><th style="width:32%">Page</th><th style="width:50%">What it covers</th><th style="width:18%">Labs</th></tr>
</thead>
<tbody>
<tr>
  <td><a href="notes1-workflow.html"><strong>5.1 The workflow is the unit of work</strong></a><br><em>Course introduction, revisited</em></td>
  <td>The workflow anatomy; the six leverage labels; the checkpoint rule; the Traffic Incident Management case; from a workflow to an agent.</td>
  <td>&mdash;</td>
</tr>
<tr>
  <td><a href="notes2-loop.html"><strong>5.2 A model in a loop</strong></a><br><em>How an agent works</em></td>
  <td>From answering to acting; a tool call is just text; recorded runs of a small model retiming a signal in SUMO; <strong>milestone paper: ReAct</strong>; workflow or agent, and Agentless; a model plus a harness.</td>
  <td>Agent lab <em>(in development)</em></td>
</tr>
<tr>
  <td><a href="notes3-tools.html"><strong>5.3 Tools: what an agent can reach</strong></a><br><em>How an agent works</em></td>
  <td>Tool descriptions as contracts; what a harness can check; <strong>milestone paper: Toolformer</strong>; code as the action; MCP; the published traffic agents and the gap they leave; a detector as a tool; grading tool use.</td>
  <td>&mdash;</td>
</tr>
<tr>
  <td><a href="notes4-context.html"><strong>5.4 Context: what the model reads</strong></a><br><em>How an agent works</em></td>
  <td>The context measured and its growth; lost in the middle; four ways to keep context useful; summaries that drop a rule; <strong>milestone paper: retrieval-augmented generation</strong>; RAG for a safety analyst.</td>
  <td>&mdash;</td>
</tr>
<tr>
  <td><strong>Further sections</strong><br><em>Skills, memory, and planning</em></td>
  <td>Skills, memory, planning and re-planning, and coordinating several agents &mdash; written up after the session.</td>
  <td>In-class skill exercise</td>
</tr>
</tbody>
</table>
</div>

## Learning objectives

By the end of this module you will be able to:

- Explain an agent as a language model running in a loop, and say what happens, step by step, when it
  calls a tool.
- Explain what it means for a model to reason, tell chain-of-thought prompting from a reasoning model,
  and say why a written chain of steps is not proof that the answer is right.
- Tell a task that needs an agent from one that needs a fixed workflow, and justify the choice.
- Name the parts of a harness — instructions, tools, memory, the loop, permissions — and say which part
  to change for a given failure.
- Describe a tool to a model with a schema, and say what a schema can and cannot guarantee.
- Explain what MCP is, how it differs from calling a web API directly, and why the model should never
  see an agency's credentials.
- Decide what belongs in an agent's context window, build retrieval (RAG) over transportation
  documents, and explain why an agent's cost grows with every step it takes.
- Turn an agency procedure into a skill an agent can load, and say when a skill helps and when it gets
  in the way.
- Decide what an agent should remember between tasks, and who is allowed to change it.
- Write a plan for a multi-step transportation task, mark the steps that cannot be undone, and place the
  checkpoint.
- Explain when splitting a task across several agents helps, and when one agent with the whole picture
  does better.

## Topics

- What agents can do today, and which tasks an agent may do alone, must ask about first, or must never do
- The words of Part II: what counts as an agent, the six capabilities an agent needs, training the model vs.
  engineering the harness, and the system around the model (sandbox, inference, monitoring)
- The agent loop: a tool call is text the model writes; ReAct
- Reasoning before acting: chain-of-thought prompting and reasoning models (OpenAI o1, DeepSeek-R1); why a
  written chain of steps is not proof
- Workflow vs. agent: the scale from fixed steps to model-chosen steps
- The model and its harness
- Tool use: function calling, schemas, web APIs, one-at-a-time and parallel calls
- MCP (Model Context Protocol), and keeping credentials away from the model
- Context engineering: what fills the context window, and what it costs
- Retrieval-augmented generation: chunking, embedding, retrieving, grounding — and checking the
  retriever on its own before judging any answer
- Summaries that drift: how an agent loses an exact constraint when its history is compressed
- Skills written by people vs. skills an agent learns from experience
- Loading only what a task needs (progressive disclosure)
- Agency SOPs, manuals and checklists as skills
- Memory: facts, lessons and episodes; adding, updating and deleting
- Plans as written artifacts: breaking a task down, plan-then-act, re-planning
- Steps that cannot be undone, and constraints that span the whole task
- A manager agent with helper agents, and the case for staying with one

## Video lectures

*To be populated.* See the course [YouTube channel](https://www.youtube.com/@hao6247).

## Recommended readings

- Yao, S., et al. (2023). ReAct: Synergizing reasoning and acting in language models. *ICLR*.
- Wei, J., et al. (2022). Chain-of-thought prompting elicits reasoning in large language models. *NeurIPS*.
- DeepSeek-AI (2025). [DeepSeek-R1: Incentivizing reasoning capability in LLMs via reinforcement learning](https://arxiv.org/abs/2501.12948). *arXiv:2501.12948*.
- Schick, T., et al. (2023). Toolformer: Language models can teach themselves to use tools. *NeurIPS*.
- Lewis, P., et al. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. *NeurIPS*.
- Anthropic (2024). [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents).
- Anthropic (2024). [Introducing the Model Context Protocol](https://www.anthropic.com/news/model-context-protocol).
- Liu, N. F., et al. (2024). Lost in the middle: How language models use long contexts. *Transactions of the ACL*.
- Xia, C. S., et al. (2025). Demystifying LLM-based software engineering agents (preprint title: Agentless). *FSE*.
- Ye, C., et al. (2025). [SUMO-MCP: Leveraging the Model Context Protocol for autonomous traffic simulation and optimization](https://arxiv.org/abs/2506.03548). *China Automation Congress*.
- Packer, C., et al. (2023). MemGPT: Towards LLMs as operating systems. *arXiv:2310.08560*.
- Wang, Z. Z., Mao, J., Fried, D., & Neubig, G. (2024). Agent workflow memory. *arXiv:2409.07429*.
- Li, X., et al. (2026). SkillsBench. *arXiv:2602.12670*.
- Zhou, D., et al. (2023). Least-to-most prompting enables complex reasoning in large language models. *ICLR*.
- Ahn, M., et al. (2022). Do as I can, not as I say: Grounding language in robotic affordances. *CoRL*. *(SayCan.)*
- Fried, D., & Neubig, G. (2026). [CMU 11-768 AI Agents](https://www.cmu-agents.com/), lectures 1–5.

## Labs

- **An agent that tunes a signal plan** *(in development)*. Run the agent of {doc}`5.2 <notes2-loop>` on its
  SUMO intersection with the timing limits (minimum green, pedestrian clearance) hidden, shown, and enforced by
  the harness; read every trace; then change one tool description or error message and measure what changes:
  tokens read per step, plans tested, plans that broke a limit, and the gap to the best valid plan of a grid
  search.

- **In class: a procedure becomes a skill.** Take one FDOT procedure and write it as a skill an agent can
  load. Then plan post-storm signal restoration with the irreversible step marked and the checkpoint
  placed. No notebook.
