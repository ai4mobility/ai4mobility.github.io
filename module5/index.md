# Module 5 — Skills, Memory, and Planning

*Part II, AI Agents for Mobility · lecture 2 of 5 · Thursday, Nov 5, 2026. See the {doc}`../syllabus`.*

## Class meetings

| Date | Session topic | Due before class |
|---|---|---|
| Nov 5 | Skills, memory, and planning: agency procedures as skills, what an agent should remember, planning and re-planning, steps that cannot be undone, and coordinating several agents | Project progress update |

## Overview

An agent that starts every task from nothing is slow, and it makes the same mistakes twice. This module
covers three ways an agent carries what it knows from one task to the next, and one way to split a task
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

**This week's transportation question.** Which parts of an agency's decades of practice — its
procedures, after-action reviews and lessons from past storms — can become skills, memory and plan
templates, and which cannot be written down?

## Learning objectives

By the end of this module you will be able to:

- Turn an agency procedure into a skill an agent can load, and say when a skill helps and when it gets
  in the way.
- Decide what an agent should remember between tasks, and who is allowed to change it.
- Write a plan for a multi-step transportation task, mark the steps that cannot be undone, and place the
  checkpoint.
- Explain when splitting a task across several agents helps, and when one agent with the whole picture
  does better.

## Topics

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

- Packer, C., et al. (2023). MemGPT: Towards LLMs as operating systems. *arXiv:2310.08560*.
- Wang, Z. Z., Mao, J., Fried, D., & Neubig, G. (2024). Agent workflow memory. *arXiv:2409.07429*.
- Li, X., et al. (2026). SkillsBench. *arXiv:2602.12670*.
- Zhou, D., et al. (2023). Least-to-most prompting enables complex reasoning in large language models. *ICLR*.
- Ahn, M., et al. (2022). Do as I can, not as I say: Grounding language in robotic affordances. *CoRL*. *(SayCan.)*
- Fried, D., & Neubig, G. (2026). [CMU 11-768 AI Agents](https://www.cmu-agents.com/), lectures 4–5.

## Labs

- **In class: a procedure becomes a skill.** Take one FDOT procedure and write it as a skill an agent can
  load. Then plan post-storm signal restoration with the irreversible step marked and the checkpoint
  placed. No notebook.
