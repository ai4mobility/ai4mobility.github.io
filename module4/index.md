# Module 4 — How an Agent Works

*Part II, AI Agents for Mobility · lecture 1 of 5 · Thursday, Oct 29, 2026. See the {doc}`../syllabus`.*

## Class meetings

| Date | Session topic | Due before class |
|---|---|---|
| Oct 29 | How an agent works: a model in a loop, workflow vs. agent, the model and its harness, tool use and MCP, context engineering and RAG | **First project progress report** |

## Overview

Part II of the course is about **AI agents**: systems in which a language model does not just answer a
question but works through a task — calling tools, reading the results, and deciding what to do next.
This module covers how that works.

Three ideas carry the whole of Part II.

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

The examples in Part II come from across transportation research and agency practice, so you should
find your own kind of work among them. Two topics get extra depth: **traffic simulation with SUMO** (this
module's lab and a full workflow in Module 8) and **transportation safety analysis** (the Module 6 lab and
a full workflow in Module 8). In this module the examples are an agent that runs a SUMO simulation
through tools and reads the result, an agent that retrieves the right passage of an agency manual before
it answers, and an agent that calls live traffic data such as Florida 511 incident reports.

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
  <td><a href="notes1-workflow.html"><strong>4.1 The workflow is the unit of work</strong></a><br><em>Aug 27, revisited Oct 29</em></td>
  <td>The workflow anatomy; the six leverage labels; the checkpoint rule; the Traffic Incident Management case; from a workflow to an agent.</td>
  <td>&mdash;</td>
</tr>
<tr>
  <td><strong>Further sections</strong><br><em>Oct 29</em></td>
  <td>The agent loop, tool use and MCP, context engineering and RAG &mdash; written up after the session.</td>
  <td>Agent lab <em>(in development)</em></td>
</tr>
</tbody>
</table>
</div>

## Learning objectives

By the end of this module you will be able to:

- Explain an agent as a language model running in a loop, and say what happens, step by step, when it
  calls a tool.
- Tell a task that needs an agent from one that needs a fixed workflow, and justify the choice.
- Name the parts of a harness — instructions, tools, memory, the loop, permissions — and say which part
  to change for a given failure.
- Describe a tool to a model with a schema, and say what a schema can and cannot guarantee.
- Explain what MCP is, how it differs from calling a web API directly, and why the model should never
  see an agency's credentials.
- Decide what belongs in an agent's context window, build retrieval (RAG) over transportation
  documents, and explain why an agent's cost grows with every step it takes.

## Topics

- What agents can do today, and which tasks an agent may do alone, must ask about first, or must never do
- The agent loop: a tool call is text the model writes; ReAct
- Workflow vs. agent: the scale from fixed steps to model-chosen steps
- The model and its harness
- Tool use: function calling, schemas, web APIs, one-at-a-time and parallel calls
- MCP (Model Context Protocol), and keeping credentials away from the model
- Context engineering: what fills the context window, and what it costs
- Retrieval-augmented generation: chunking, embedding, retrieving, grounding — and checking the
  retriever on its own before judging any answer
- Summaries that drift: how an agent loses an exact constraint when its history is compressed

## Video lectures

*To be populated.* See the course [YouTube channel](https://www.youtube.com/@hao6247).

## Recommended readings

- Yao, S., et al. (2023). ReAct: Synergizing reasoning and acting in language models. *ICLR*.
- Schick, T., et al. (2023). Toolformer: Language models can teach themselves to use tools. *NeurIPS*.
- Lewis, P., et al. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. *NeurIPS*.
- Anthropic (2024). [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents).
- Anthropic (2024). [Introducing the Model Context Protocol](https://www.anthropic.com/news/model-context-protocol).
- Ye, C., et al. (2025). [SUMO-MCP: Leveraging the Model Context Protocol for traffic simulation](https://arxiv.org/abs/2506.03548). *arXiv:2506.03548*.
- Fried, D., & Neubig, G. (2026). [CMU 11-768 AI Agents](https://www.cmu-agents.com/), lectures 1–3.

## Labs

- **An agent that tunes a signal plan** *(in development)*. Build a small agent loop that adjusts the
  timing of one intersection through SUMO tools. Run it twice — once without and once with the timing
  limits (minimum green, pedestrian clearance) shown in the tool's output — and count how many of its
  proposed plans break them. Then add a checkpoint before any plan is applied.
