# Module 8 — Agents at Work in an Agency: AI-Ready Data, Agency Forms, and Several Agents

*Part II, AI Agents for Mobility · the last module of the agents unit, followed by the final presentations. The
class schedule is on the {doc}`../syllabus` page.*

## Session topics

- **AI-ready data:** what an agent needs to do one real job; why data kept for people is not ready for an agent;
  six moves that make existing data ready; data that does not exist yet; data for improving or training an agent
- **Answering in the agency's form:** picking the agency's exact choices in field apps that have no API, such as
  Survey123
- **Several agents:** when a manager agent with helpers pays off, and when one agent with the whole picture does
  better *(if time allows)*
- **Your project, the agentic way:** comparing your own model with a powerful model used at five levels

## Overview

By now your agent can call tools, follow a skill, look things up in a manual and remember what happened. Every one
of those quietly assumed that the data was there and correct, and that the agent's answer would land somewhere an
agency can use. This module stops assuming.

**AI-ready data.** Transportation agencies hold decades of data collected for engineers to read. Agents are a new
kind of reader. The running job is the morning after a hurricane landfall, when many signals fail at once and the
agent must help decide what to inspect, power and repair first. FDOT District 7's signal SOP names a data system in
77 of its 150 rules, and one failed signal lives in five places, each kept for a person. The lecture follows the
work list of NSF's new *AI Datasets* program (NSF 26-512), which pays to make existing datasets usable by AI, in
four parts:

- **What the agent needs:** the questions it must answer, the six kinds of data in one run, and why data kept for
  people is hard for an agent to use.
- **Make existing data ready:** extract, describe (a data dictionary the agent loads as a skill), link, harmonize,
  fill gaps, and score readiness. One caution: keep values a model made apart from values a person observed, and
  label each with its method and date.
- **Create what does not exist:** task records from past storms, records of the agent's own work, a practice
  storm, the reference lists the SOP points to but does not contain, and a clock to tell whether anything improved.
- **Improve, train and govern:** what each way of improving an agent needs, from worked examples to fine-tuning and
  reinforcement learning; how many past cases you need to test; and who may read or change the data, and when it
  expires.

**Answering in the agency's form.** Field apps such as Survey123 damage forms, eSTORM Lite, crash report forms
and asset inventories have fixed menus and usually no API you may call. A free-text answer from a model ("heads
look twisted") is useless to the GIS layer; the agent must pick the agency's exact choice. One method works for any
app: capture the form once as a file (best from the form definition, then the manual behind it, then screenshots
checked by a person); let code walk the form one question at a time, so the model sees only that question's valid
choices and may answer "unsure"; check the answers in code before anything leaves; deliver them as a fill-in card,
a prefill link, or, with the GIS administrator's permission, a write to the layer. A person always reviews and
submits. Then measure how often the agent agrees with the inspector's own choices. The running example is a real
county's post-storm damage form, learned from the county's own how-to deck.

**Several agents.** A manager agent can hand pieces of a task to helper agents, each with its own short context.
Sometimes that helps. Often one agent that sees the whole task does better, because a hand-off is a summary, and
summaries drop things ({doc}`7.1 <../module7/notes1-context>`). {doc}`Section 5.4 <../module5/notes5-architectures>`
(question 3, the team) lays out three wirings and the case for one agent.

**Your project, the agentic way.** Every team that trained its own model compares it with a powerful model used at
five levels: (1) prompt only; (2) plus labeled examples from your training set; (3) plus your written knowledge as
a skill; (4) an agent with tools, including your own model; (5) your small model first, with the agent reviewing
the cases it is unsure about and a person seeing what the agent flags. Use the same test split for every version,
freeze the skill and any memory before scoring, run each version three times, and report the &ldquo;unsure&rdquo;
rate, the cost and the time. The agent losing is a valid result.

**This module's transportation question.** What data would let an agent do your project's job better, and what would
you have to fix or create first? And can you show, on your own test set, that the agent beats your model, or that it
does not?

## The module, page by page

<div class="practice-table-wrap">
<table class="practice-table notes-map">
<thead>
<tr><th style="width:32%">Page</th><th style="width:50%">What it covers</th><th style="width:18%">Labs</th></tr>
</thead>
<tbody>
<tr>
  <td><strong>Further sections</strong><br><em>AI-ready data</em></td>
  <td>The job: signals on the morning after landfall; six kinds of data in one run; why data kept for people is not ready; six moves that make existing data ready; data that does not exist yet; data for improving and training an agent; governance &mdash; written up after the session.</td>
  <td>&mdash;</td>
</tr>
<tr>
  <td><strong>Further sections</strong><br><em>Answering in the agency's form</em></td>
  <td>Capturing a form as a file; code walks the form; checks before anything leaves; the delivery ladder; measuring consistency with the inspector &mdash; written up after the session.</td>
  <td>Your project's form file</td>
</tr>
<tr>
  <td><strong>Further sections</strong><br><em>Several agents; your project</em></td>
  <td>A manager agent and its helpers, and the case for one agent; the five levels and the fair-comparison rules &mdash; written up after the session.</td>
  <td>Your comparison table</td>
</tr>
</tbody>
</table>
</div>

## Learning objectives

By the end of this module you will be able to:

- List the data an agent needs for one transportation job, and say which of it is not ready for an agent today.
- Apply the six moves (extract, describe, link, harmonize, fill gaps, score readiness) to an agency dataset, keeping
  made values apart from observed ones.
- Say what new data to create so that an agent can be tested, improved or trained.
- Build a form file for an agency app, and have an agent answer in the agency's exact choices with checks in code
  and a person who submits.
- Decide when to split a task across several agents and when to keep one.
- Compare your own model with a powerful model at five levels, fairly, and report the result even when the agent
  loses.

## Topics

- Agents as a new reader of transportation data; NSF 26-512 *AI Datasets*
- Six kinds of data in one agent run, and where each stands today
- Six moves that make existing data ready, and the caution about made values
- Data to create: task records, work records, a practice storm, reference lists, an outcome clock
- Data for improving and training an agent; how many past cases a test needs
- Governance: who reads, who changes, when it expires
- Field apps with fixed menus and no API: the form file, code-driven walking, checks, delivery, consistency
- A manager agent with helpers vs. one agent with the whole task
- Five levels of using a powerful model, and fair-comparison rules

## Video lectures

*To be populated.* See the course [YouTube channel](https://www.youtube.com/@hao6247).

## Recommended readings

- National Science Foundation (2026). *AI Datasets* program solicitation, NSF 26-512.
- Stanford CS 329Z *Engineering AI Agents* (Fall 2026), lecture 11, &ldquo;What data do agents need?&rdquo;
- Anthropic (2025). [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system).
- Fried, D., & Neubig, G. (2026). [CMU 11-768 AI Agents](https://www.cmu-agents.com/).

## Labs and assignments

- **Your project's form file.** If your project's results must land in an agency app, capture its form as a file:
  questions, exact choices, branching, required fields, and what is missing.
- **Your comparison table.** Run your own model and the five levels on the same test split, three times each, and
  report the table, with the failures you found, in your final presentation.
