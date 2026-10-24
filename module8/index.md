# Module 8 — Building Transportation Harnesses

*Part II, AI Agents for Mobility · lecture 5 of 5 · Tuesday, Nov 24, 2026 (an added session). Final
presentations follow on Dec 3. See the {doc}`../syllabus`.*

## Class meetings

| Date | Session topic | Due before class |
|---|---|---|
| Tue, Nov 24 | Building transportation harnesses: a harness template, the SUMO simulation workflow, the safety analysis workflow, and data engineering for AI agents | &mdash; |

## Overview

This module puts Part II together. Every agent you build for transportation work is a model inside a
harness, and the same template describes the harness every time:

| Field | Question to answer |
|---|---|
| Task and trigger | What starts the agent, and what does "done" look like? |
| Tools and data access | Which APIs or MCP servers can it call? Read-only or write? |
| Knowledge | Which manuals or documents does it retrieve from? |
| Skills | Which agency procedures are written as skills? |
| Memory | What does it keep between runs, and who can edit it? |
| Workflow or agent | Which steps are fixed in code, and which does the model decide? |
| Checkpoints and permissions | Where must a person approve, especially before steps that cannot be undone? |
| Evaluation | How do we know it works, and what is the baseline? |
| Logs and disclosure | What is recorded, and how are AI-assisted outputs labeled? |

**The SUMO simulation workflow.** Build the network, load the demand, calibrate to field counts, compare
signal plans against a Webster or actuated baseline, and report. The agent runs the tools; a person
checks the geometry, chooses what to test, and — the key checkpoint — accepts the calibration, using the
usual GEH check against counts, before anyone trusts a scenario result.

**The safety analysis workflow.** Follow the Highway Safety Manual's safety management process:
network screening, diagnosis, countermeasure selection, economic appraisal, prioritization, and
effectiveness evaluation. The agent links crash, roadway and volume data, runs the safety performance
functions, reads crash narratives, and retrieves crash modification factors. The engineer approves the
site list and the countermeasures.

**Data engineering for AI agents.** Transportation data was collected for people to read. Agents are a
new kind of user, and they need three things:

- *Data they can use:* data dictionaries with units and codes, written like a skill; IDs that link crash
  records, roadway inventory, traffic counts and weather; access through tools with privacy rules built in.
- *What experts carry in their heads, written down:* known data errors, changes to report forms over the
  years, missing exposure data.
- *Data people could not use at scale:* narratives, sketches and video linked to crash records, and
  near-miss events.

One warning comes with it. An agent that tests 1,000 ideas at the 5% level will find about 50 that look
real by chance alone. Agent-ready data needs held-out data or tests stated in advance — above all for
crash data, where counts are small and regression to the mean is common.

*Optional:* a harness for reviewing transportation papers or projects. Use it only on published papers or
your own drafts. Funders and many journals do not allow confidential manuscripts or proposals to be
uploaded to AI tools.

## Learning objectives

By the end of this module you will be able to:

- Describe any transportation agent with the harness template, and spot the field a design has left empty.
- Lay out an AI workflow for traffic simulation and one for safety analysis, with the agent's steps, the
  person's steps, and the checkpoints.
- Say what would make a transportation dataset easier for an agent to use, and what would make the
  agent's "findings" trustworthy.

## Topics

- The harness template
- An AI workflow for traffic simulation in SUMO
- An AI workflow for transportation safety analysis
- Data engineering for AI agents: making existing data usable, writing down expert knowledge, new data to collect
- Many tests, false findings, and how to guard against them
- *(Optional)* a review harness for papers and projects

## Video lectures

*To be populated.* See the course [YouTube channel](https://www.youtube.com/@hao6247).

## Recommended readings

- Ye, C., et al. (2025). [SUMO-MCP: Leveraging the Model Context Protocol for traffic simulation](https://arxiv.org/abs/2506.03548). *arXiv:2506.03548*.
- Liu, Q., et al. (2026). [SimSkill: A self-evolving LLM agent for skill and knowledge accumulation in traffic simulation](https://arxiv.org/abs/2609.03753). *arXiv:2609.03753*.
- AASHTO. *Highway Safety Manual*, Part B: the roadway safety management process.
- Federal Highway Administration (2026). [AI for Safety and Efficiency Program Roadmap](https://highways.dot.gov/sites/fhwa.dot.gov/files/FHWA-HRT-26-063.pdf). FHWA-HRT-26-063.

## Labs

- **Your capstone's harness.** Each team fills in the harness template for its own project: what the
  agent does, what the people do, and where the checkpoints go. No notebook.
