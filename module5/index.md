# Module 5 — How an Agent Works: the Loop and Its Tools

*Part II, AI Agents for Mobility · the first module of the agents unit. The class schedule is on the
{doc}`../syllabus` page.*

## Session topics

- **What an agent is:** from answering to acting; a tool call is text that the harness picks out and runs; an
  agent is a model in a loop
- **Calling and building tools:** turning functions you know, such as SUMO's TraCI, into tools; the menu the model
  sees; how the harness runs one call and sends the result back
- **Where your transportation knowledge goes:** the decisions inside every tool; advice in the description,
  rules in code
- **Who checks the tool result:** five places to add a check, checks from traffic flow theory, and a person as
  the checker
- **MCP and live data:** one tool server that many agents share; Arizona 511 and Florida work-zone feeds as tools
- **Workflow or agent:** a scale you know from signal control; an agent is a model plus a harness; what an agent
  may do alone, must ask about first, or must never do

## Part II at a glance

Part II of the course is about **AI agents**: systems in which a language model does not just answer a
question but works through a task. It calls tools, reads the results, and decides what to do next. Each
module adds one thing an agent needs to do transportation work well.

| Module | What it adds | The question it answers |
|---|---|---|
| **5 How an agent works** (this module) | the loop and its tools | What can the agent look up or compute right now? |
| {doc}`6 Skills <../module6/index>` | the agency's know-how, packed for an agent | How does this agency, or this group, do this job? |
| {doc}`7 Context, RAG, and memory <../module7/index>` | what the model reads, and what carries over | What does a long manual say? What happened before? |
| {doc}`8 Agents at work in an agency <../module8/index>` | data, agency forms, several agents | Is the data ready, and can we tell if the agent is right? |
| {doc}`9 How models and agents are trained <../module9/index>` *(optional)* | the training behind it all | How does a model learn to reason, to use tools, or a new domain? |

Four ideas carry all of Part II.

- **An agent is a model in a loop.** The model writes a short, structured request to use a tool. A program runs
  it, the result is pasted back into the model's input, and the loop repeats until the model decides the task is
  done. The model never touches the simulator or the database itself; it only writes text that something else
  runs.
- **There is a scale from a fixed workflow to a free agent.** In a workflow, a person decides every step in
  advance. In an agent, the model decides them while it runs. Signal control has the same scale: fixed-time,
  actuated, adaptive. Adaptive control pays off when demand is unpredictable, and an agent pays off only when the
  steps cannot be written down in advance. If you know the steps, write a workflow.
- **An agent is a model plus a harness.** The harness is everything around the model: its instructions, its
  tools, its skills, its memory, the loop, and its permissions. You will almost never change the model. You will
  build harnesses.
- **What transportation adds is the lever.** Tools, skills, retrieval, memory and data were all built to work in
  any field. For each one we ask what transportation researchers and engineers can add: traffic flow and safety
  theory, an agency's decades of procedures and lessons, and its data. The harness is where that knowledge goes,
  and every idea is tested against the general version without it.

Part II adapts the structure of CMU 11-768 *AI Agents* (Fall 2026, Daniel Fried and Graham Neubig) and draws on
Stanford CS 329Z *Engineering AI Agents*, rebuilt around transportation research and agency work.

## Overview

This module takes an agent apart. It starts from the workflow you met in the first week of class, puts a
language model inside a loop, and then spends most of its time on **tools**, the part of an agent you will
build first.

A tool is a function the model may ask the harness to run: get the queue at a detector, switch a signal phase,
list the work zones on a street. The model sees a menu of tools, each with a name, a description and its inputs.
It picks one by writing its name and arguments as text; the harness runs the function and pastes the result back.
You will watch one real call slowed down, step by step, on a SUMO intersection, with a small open model and with
a strong closed one.

Your transportation knowledge enters a tool in two places. **Advice goes in the description**: what the tool
returns, when to call it, what a number means. **Rules go in code**: a minimum green, a pedestrian clearance, a
check that a result is physically possible. The model may ignore advice. It cannot ignore code.

A plain loop has only one checker, the model itself, and models are poor at checking their own work. So the
module ends the tools part with **who checks the tool result**: five places a harness can add a check, checks
built from traffic flow theory (capacity, and how fast a queue can grow), and when the checker should be a person.

Two examples run through the module: an agent that retimes a signal through **SUMO** tools, and agents that read
**live agency data**, Arizona 511 and Florida's work-zone (WZDx) feed, through tools served over MCP.

**This module's transportation question.** What should your agent compute itself, and what should it hand to a
validated engineering tool such as SUMO or an HCM procedure? And which of your rules belong in a tool's
description, and which in its code?

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
  <td><a href="notes2-loop.html"><strong>5.2 A model in a loop</strong></a><br><em>What an agent is</em></td>
  <td>From answering to acting; six words for one step of the loop; a tool call is just text; recorded runs of a small model retiming a signal in SUMO; <strong>milestone paper: ReAct</strong>; workflow or agent, and Agentless; a model plus a harness.</td>
  <td>Agent lab <em>(in development)</em></td>
</tr>
<tr>
  <td><a href="notes3-tools.html"><strong>5.3 Tools: what an agent can reach</strong></a><br><em>Calling and building tools</em></td>
  <td>A menu, not a new script each time (the TMC analogy); tool descriptions as contracts; five SUMO tools built from TraCI; tool call vs. TraCI call; how the harness runs a call; <strong>slide show: one real tool call, slowed down</strong>; what a harness can check; where your traffic knowledge goes in a tool; <strong>milestone paper: Toolformer</strong>; code as the action; MCP; the published traffic agents and the gap they leave; a detector as a tool; grading tool use.</td>
  <td>Assignment 5.1</td>
</tr>
<tr>
  <td><a href="notes5-architectures.html"><strong>5.4 Agent architectures: one loop, four questions</strong></a><br><em>What an agent is</em></td>
  <td>Why the published lists of &ldquo;architectures&rdquo; disagree; four design questions (control, reach, team, oversight); three ways to pick the next step, measured on the SUMO agent; the published traffic agents redrawn on the loop; what agencies ask for.</td>
  <td>In-class sorting worksheet</td>
</tr>
<tr>
  <td><strong>Further section</strong><br><em>Who checks the tool result</em></td>
  <td>Five places to add a check; which kind of check goes where; checks from traffic flow theory; a gate is a stop, not a fix; when a person is the checker &mdash; written up after the session.</td>
  <td>&mdash;</td>
</tr>
</tbody>
</table>
</div>

## Learning objectives

By the end of this module you will be able to:

- Explain an agent as a language model running in a loop, and say what happens, step by step, when it calls a
  tool.
- Tell a task that needs an agent from one that needs a fixed workflow, and justify the choice.
- Name the parts of a harness, and say which part to change for a given failure.
- Turn a function you already use (a TraCI call, a query on an agency feed) into a tool with a clear name,
  description and inputs.
- Put transportation knowledge into a tool: advice in its description, rules in its code, each with a source and
  a test.
- Add a check on a tool's result, say where in the harness it belongs, and say when the checker should be a
  person.
- Explain what MCP is, how it differs from calling a web API directly, and why the model should never see an
  agency's credentials.

## Topics

- What agents can do today, and which tasks an agent may do alone, must ask about first, or must never do
- The agent loop: a tool call is text the model writes; ReAct
- Workflow vs. agent: the scale from fixed steps to model-chosen steps
- The model and its harness
- Tool use: the menu, schemas, how the harness runs a call and returns the result
- Building tools from TraCI functions and from live agency feeds (Arizona 511, Florida WZDx)
- Advice in the description, rules in code
- Checking tool results: in the loop, in the harness, from traffic flow theory, and by a person
- MCP (Model Context Protocol), and keeping credentials away from the model
- Agent architectures as answers to four design questions

## Video lectures

*To be populated.* See the course [YouTube channel](https://www.youtube.com/@hao6247).

## Recommended readings

- Yao, S., et al. (2023). ReAct: Synergizing reasoning and acting in language models. *ICLR*.
- Schick, T., et al. (2023). Toolformer: Language models can teach themselves to use tools. *NeurIPS*.
- Wang, X., et al. (2024). Executable code actions elicit better LLM agents. *ICML*. *(CodeAct.)*
- Huang, J., et al. (2024). Large language models cannot self-correct reasoning yet. *ICLR*.
- Gou, Z., et al. (2024). CRITIC: Large language models can self-correct with tool-interactive critiquing. *ICLR*.
- Anthropic (2024). [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents).
- Anthropic (2024). [Introducing the Model Context Protocol](https://www.anthropic.com/news/model-context-protocol).
- OpenAI (2025). [A practical guide to building agents](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf).
- Xia, C. S., et al. (2025). Demystifying LLM-based software engineering agents (preprint title: Agentless). *FSE*.
- Ye, C., et al. (2025). [SUMO-MCP: Leveraging the Model Context Protocol for autonomous traffic simulation and optimization](https://arxiv.org/abs/2506.03548). *China Automation Congress*.
- Fried, D., & Neubig, G. (2026). [CMU 11-768 AI Agents](https://www.cmu-agents.com/).

## Labs and assignments

- **Assignment 5.1 — Agent tools with transportation knowledge** *(Canvas)*. Write at least two tools an agent can
  call, with your transportation rules in code (each with a source and a test). Serve them over MCP, read the whole
  tool-calling loop of an open model that uses them, and measure what your tools, and the knowledge inside them,
  change. Choose a track and submit a pull request:
  [ai4mobility/sumo-agent-tools](https://github.com/ai4mobility/sumo-agent-tools) (a SUMO corridor) or
  [ai4mobility/WZDx-Tools](https://github.com/ai4mobility/WZDx-Tools) (Florida and Arizona work-zone feeds).

- **An agent that tunes a signal plan** *(in development)*. Run the agent of {doc}`5.2 <notes2-loop>` on its
  SUMO intersection with the timing limits (minimum green, pedestrian clearance) hidden, shown, and enforced by
  the harness; read every trace; then change one tool description or error message and measure what changes:
  tokens read per step, plans tested, plans that broke a limit, and the gap to the best valid plan of a grid
  search.

- **In class: sort the architectures.** Place the patterns from published &ldquo;agent architecture&rdquo; lists on
  the four design questions of {doc}`5.4 <notes5-architectures>`. No notebook.
