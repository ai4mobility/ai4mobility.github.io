# Module 6 — Skills: Packaging Transportation Know-How

*Part II, AI Agents for Mobility · two lectures. The class schedule is on the {doc}`../syllabus` page.*

## Session topics

- **Lecture 1, how skills work:** what a skill is; how its folder is laid out; how a model decides to load one;
  how a skill makes the model open its files and run its rules; how a skill improves
- **Lecture 2, building transportation skills:** the eight steps; putting domain experience in, in practice;
  sorting an after-action report; two worked examples; where skills break; designing and sharing your own skill

## Overview

In {doc}`Module 5 <../module5/index>` you gave an agent tools. This module gives it a way of working: the manual,
the rules, the checks, and the experience of the people who do the job. That package is called a **skill**.

A skill is a folder with one required file, `SKILL.md`. Its short description is always in front of the model;
the full instructions, and the files they point to, load only when a task matches the description. Loading a
skill is an ordinary tool call, so everything you learned about tools still applies. Inside the folder, rules
that must hold become code the model runs, and long reference text stays in files the model opens one step at a
time.

| Piece | The question it answers | Written by | When it reaches the model |
|---|---|---|---|
| Instructions | Who am I working for, and what must I never do? | You | Every call |
| Tools (Module 5) | What can I look up or compute right now? | Developers | When the model calls one |
| **Skills (this module)** | How does this agency, or this group, do this job? | People who know the work | When a task matches its description |
| Retrieval and memory (Module 7) | What does the manual say? What happened before? | The documents; the work itself | When a step needs them |

Agencies already write this kind of know-how down: standard operating procedures, design manuals, checklists,
after-action reports. Turning one into a skill is often the cheapest improvement available, but it is not free.
In one benchmark (SkillsBench), curated skills raised the average pass rate from 33.9% to 50.5%, but made results
worse on 13 of 87 tasks, because a skill can push aside a better default.

**Lecture 1** covers how a skill works: its folder, its three levels of loading and what each costs, and how a
model decides to load one. The description works like a detection zone at an actuated signal: every phrase is
there because a real request would use it, so you write it, then test it with requests that should and should not
load the skill.

**Lecture 2** builds transportation skills in eight steps: name the job; keep the exact words; sort the content
into four homes (a rule becomes code, a procedure becomes skill steps, guidance stays in retrieval with quotes,
and judgment stays with a person); write the reading path; add what the SOP leaves out; write the description;
test before you trust it; keep it current. The heart of the lecture is step 5, **domain experience**. Field words
go into a glossary, lessons already written down (after-action reports, other districts) go into a lessons file,
and practice that lives only in people comes out through an interview. Experience stays apart from the SOP and
reaches the agent only as a suggestion that cites its source and names the person who decides.

**See a skill at work.** The {doc}`Text-to-Traffic-Diagram Agent <../traffic-diagram-agent>` is a skill plus tools, deployed as a public web page: type a short incident narrative of a crash or a lane closure, and it draws the kinematic-wave diagram and checks it against the theory.

Two skills run through both lectures, and both are in the class repository
[ai4mobility/transportation-skills](https://github.com/ai4mobility/transportation-skills):

- **`d7-signal-sop`**, built from FDOT District 7's hurricane signal SOP. It turns a storm situation into action
  cards that cite the SOP's clauses. Agency practice; mostly procedure.
- **`journal-club-paper-review`**, built from the instructor's journal-club guide. It turns a paper into review
  notes and a slide outline. Research practice: know-how for evaluating a paper.

Section 6.3 then follows one project from start to finish: an agent that runs District 7's hurricane signal SOP on a
simulated storm in Tampa with three skills, 25 tools and a person in the loop. Its companion shows every request the
model was sent, so you can see when and why it called each tool and loaded each skill.

Section 6.4 rebuilds that agent as a team, a lead agent with desk agents, cut two ways (by crew type and by zone), and
runs all three designs on the same storms. It shows what a team gained, what it cost, and how little one run can tell
you.

**This module's transportation question.** Which parts of an agency's decades of practice — its procedures,
after-action reviews and lessons from past storms — can become a skill, and which must stay with a person?

## The module, page by page

<div class="practice-table-wrap">
<table class="practice-table notes-map">
<thead>
<tr><th style="width:32%">Page</th><th style="width:50%">What it covers</th><th style="width:18%">Labs</th></tr>
</thead>
<tbody>
<tr>
  <td><a href="notes1-knowledge.html"><strong>6.1 Where knowledge lives: giving an agent the right knowledge</strong></a><br><em>Lecture 1: how skills work</em></td>
  <td>What a model knows and what it has not read; eight places knowledge can reach an agent; four kinds of knowledge and their homes (code, skill, retrieval, a person); every call vs. only when a step needs it, in tokens; one hurricane-morning request traced through the D7 signal skill; <strong>hands-on companion: where knowledge lives</strong>.</td>
  <td>In-class skill exercise</td>
</tr>
<tr>
  <td><a href="notes2-skills.html"><strong>6.2 Inside a skill: packaging transportation know-how</strong></a><br><em>Lecture 1: how skills work</em></td>
  <td>A skill as a folder and when the model sees each file; how SKILL.md sends the model to its files; sorting know-how into homes; the same request run with no skill, the document only, and the skill (D7 SOP and journal club); <strong>hands-on companion: inside a skill</strong>.</td>
  <td>&mdash;</td>
</tr>
<tr>
  <td><a href="notes3-signal-agent.html"><strong>6.3 A worked agent: running the hurricane signal SOP with tools and skills</strong></a><br><em>Lecture 2: building transportation skills</em></td>
  <td>One project end to end: why dark signals after a storm matter; a digital twin of 245 Tampa signals; the SOP sorted into code, three skills, 25 tools, a person and seven guesses; the SOP as a contract that is audited after every run; one planning moment in eight steps with four guard rails; what three Claude models did with the same storm; <strong>two companions: the storm on a map, and every request the model was sent</strong>.</td>
  <td>&mdash;</td>
</tr>
<tr>
  <td><a href="notes4-signal-team.html"><strong>6.4 One agent or a team: the hurricane signal SOP with a lead and desks</strong></a><br><em>Worked example, continued</em></td>
  <td>The same SOP run by one agent, by a team cut by crew type, and by a team cut by zone; counting the linked jobs each cut breaks (17% and 29% stay inside one desk); one planning moment of a team (brief, plan, report, merge, send) and the rules kept in code; 15 runs with Claude Sonnet 5.5 and 27 without a model; repeated runs to measure noise; what happens when the lead cannot be reached; <strong>companion: the replay map with a graph of who briefed, reported to and asked whom</strong>.</td>
  <td>&mdash;</td>
</tr>
<tr>
  <td><strong>Further sections</strong><br><em>Lectures 1 and 2</em></td>
  <td>How a model decides to load a skill, and how to write and test a description; how a skill uses its references and rules, and how it learns; building a transportation skill in eight steps; domain experience in practice, with a real after-action report; the two worked examples side by side; where skills break &mdash; written up after the sessions.</td>
  <td>Skills assignment</td>
</tr>
</tbody>
</table>
</div>

## Learning objectives

By the end of this module you will be able to:

- Explain what a skill is, and how it differs from a tool, a retrieved document and memory.
- Read a skill's folder and say when the model sees each file, and what each level of loading costs.
- Write a skill description that loads on the right requests, and test it with requests that should and should
  not load it.
- Turn an agency procedure into a skill with the eight steps, putting rules in code and judgment with a person.
- Add experience the procedure leaves out (a glossary, written lessons, an interview with the people who do the
  work) as cited suggestions, kept apart from the procedure.
- Compare the same requests run with and without a skill, and say when a skill hurts.

## Topics

- What a skill is: a new hire's binder, turned into a folder
- Skill, tool, retrieval or memory: which one a piece of know-how needs
- The folder: front matter, body, references, scripts; three levels of loading
- How the model decides: the skill list, the description as a detection zone, loading as a tool call
- How models are trained to use skills (2026 research), and why descriptions should be a little &ldquo;pushy&rdquo;
- Four devices that make a model use a skill's files: name the file in the step, put every rule in a script, fix
  the answer format, and end with a checker the model must run
- How a skill improves: people, patches and learned skills; who admits a lesson
- The eight steps for building a transportation skill
- Domain experience: glossaries, lessons, interviews, after-action reports; a card vs. a suggestion
- Where skills break, and testing a skill before you trust it
- Sharing a skill: the class repository and its rules

## Video lectures

*To be populated.* See the course [YouTube channel](https://www.youtube.com/@hao6247).

## Recommended readings

- Anthropic (2025). [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills).
- [Agent Skills specification](https://agentskills.io/specification), the open format the course skills follow.
- Li, X., et al. (2026). SkillsBench. *arXiv:2602.12670*.
- Wang, G., et al. (2023). Voyager: An open-ended embodied agent with large language models. *arXiv:2305.16291*.
- Wang, Z. Z., Mao, J., Fried, D., & Neubig, G. (2024). Agent workflow memory. *arXiv:2409.07429*.
- Fried, D., & Neubig, G. (2026). [CMU 11-768 AI Agents](https://www.cmu-agents.com/), lecture 4, &ldquo;Memory and Skills&rdquo;.
- Stanford CS 329Z *Engineering AI Agents* (Fall 2026), lecture 7.

## Labs and assignments

- **Skills assignment** *(Canvas, released after the first skills lecture)*. Build a skill for a job in your own
  project with the eight steps, test it, and compare runs with and without it.

- **In class.** Name your project's repeat job; write and test a description; sort items from a real after-action
  report; interview the expert and run the skill again. No notebook.

- **Build one and share it.** The {doc}`Transportation Skills <../skills>` page explains how to build a skill in
  eight steps and add it to the class repository.
