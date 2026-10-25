# Module 7 — Agents and People in an Agency

*Part II, AI Agents for Mobility · lecture 4 of 5. The class schedule is on the {doc}`../syllabus` page.*

## Session topics

- **Agents and people in an agency:** orchestration and monitoring, safety and permissions,
  human-in-the-loop design under agency AI policy, and agents that interact

## Overview

An agency will only use an agent it can approve. This module is about building one it could.

**Orchestration.** Fix in code the steps you already know, and let the model handle only the judgment
calls. Take a citizen request to a city's traffic operations team. "The signal at this intersection is
stuck on red" should create a work order right away, with no model involved. "Please add a crosswalk
here" should look up the warrant criteria, draft a reply, and wait for an engineer's review before
anything is sent.

**Monitoring.** Keep a record of everything the agent did, so a failure can be traced. When the problems
you are watching for are rare, most alarms will be false — the same arithmetic you meet in automatic
incident detection.

**Safety.** Agents cause harm in four main ways: a user asks for something they should not; instructions
are hidden inside text the agent reads, such as a citizen request or a 511 free-text field; the agent
makes an honest mistake; or it takes a shortcut that passes the check without doing the work. The
defences are part of the harness: read-only access by default, credentials the model never sees, and an
audit log.

**People in the loop.** FDOT's AI Policy (May 2024) requires that AI supplement human work and that
people remain fully responsible for its outputs; it also asks staff to disclose AI use, use approved tools
only, and validate AI outputs. Each of those rules can be turned into a feature of the harness. The hard
part is placing the person so the review is real. A reviewer who approves a hundred items a day stops
reviewing, which is the same over-trust problem you know from driver-assistance systems.

The module ends with **agents that interact**: agents with different goals meeting one another, such as
language-model agents acting as simulated travelers or drivers.

Other examples: traffic management center operators approving the dynamic message sign messages an
agent drafts, and automated vehicles and human drivers as agents with different goals.

**This week's transportation question.** Where does the engineer's judgment belong in the loop, and which
agency rules become features of the harness? And when language-model agents play drivers, does traffic
flow theory say they behave like real ones — do they reproduce the fundamental diagram?

## Learning objectives

By the end of this module you will be able to:

- Design a workflow for an agency task, choosing which steps are fixed in code and which the model decides.
- Read an agent's trace, and explain why an alarm for rare problems produces mostly false alarms.
- Name the main ways an agent causes harm, and design permissions, credentials and logs against each.
- Turn an agency's AI policy into specific harness features, and place human review where it is real.
- Describe what changes when several agents with different goals interact.

## Topics

- Orchestration: workflow graphs, routing, saved progress, and tests for each step
- Monitoring: traces of what the agent did; why an overall score can hide the cause; alarm base rates
- Safety: four ways agents cause harm; sandboxes; read-only and write access; credentials; audit logs
- Human-in-the-loop design under an agency AI policy; real review vs. rubber stamp
- Agents that interact: different goals, simulated travelers and drivers

## Video lectures

*To be populated.* See the course [YouTube channel](https://www.youtube.com/@hao6247).

## Recommended readings

- Debenedetti, E., et al. (2024). AgentDojo: A dynamic environment to evaluate prompt injection attacks and defenses for LLM agents. *NeurIPS Datasets and Benchmarks*.
- Greenblatt, R., et al. (2024). AI control: Improving safety despite intentional subversion. *ICML*.
- HNTB. [FDOT's approach for artificial intelligence success](https://www.hntb.com/think/think-innovation-in-motion-fdots-approach-for-artificial-intelligence-success/) *(a summary of the FDOT AI Policy)*.
- Federal Highway Administration (2026). [AI for Safety and Efficiency Program Roadmap](https://highways.dot.gov/sites/fhwa.dot.gov/files/FHWA-HRT-26-063.pdf). FHWA-HRT-26-063.
- NCHRP Project 03-159. [Implementing human-AI collaboration for enhancing TMC freeway operations](https://rip.trb.org/View/2709250).
- Fried, D., & Neubig, G. (2026). [CMU 11-768 AI Agents](https://www.cmu-agents.com/), lectures 13 and 15.

## Labs

- **Reviewing an agent's work** *(in development)*. Work through a set of recorded agent runs on
  transportation tasks. Find the failures, decide which ones a human reviewer would have caught, and
  design where the approvals should go. The runs are recorded in advance, so nothing needs an API key.
