(transportation-skills)=
# Transportation Skills: Share What You Know with AI Agents

<section class="resource-hero">
  <div class="resource-eyebrow">USF &middot; AI for Mobility &middot; Open repository</div>
  <h2>Transportation Skills <span>for research and agency practice</span></h2>
  <p>An open collection of skills that teach AI agents to do transportation work the way experienced engineers do it: which manual to open, which numbers to compute instead of guessing, what to check before answering, and what to leave to a person. Students, researchers, agency staff and consultants are all invited to build one and share it.</p>
  <div class="resource-meta">
    <span>github.com/ai4mobility/transportation-skills</span>
    <span>Free to use and to contribute (MIT license)</span>
    <span>Works in Claude, Claude Code and other agents</span>
  </div>
</section>

<div class="cta-row resource-cta-row">
  <a class="cta-button" href="https://github.com/ai4mobility/transportation-skills" target="_blank" rel="noopener">Open the repository</a>
  <a class="cta-button cta-secondary" href="https://github.com/ai4mobility/transportation-skills/issues/new/choose" target="_blank" rel="noopener">Propose a skill</a>
  <a class="cta-button" href="https://github.com/ai4mobility/transportation-skills/blob/main/SKILLS_WANTED.md" target="_blank" rel="noopener">See the skills we want</a>
</div>

## What a skill is

```{figure} _static/figures/AGT_Skill_Loading.png
:alt: Three panels from left to right. Always visible: the name and description of every skill that is turned on, for example d7-signal-sop, "Turn the FDOT District 7 Traffic Signals SOP into action cards for hurricane response". Loaded when it fits: SKILL.md, the instructions, with steps such as find the phase, read that phase's clauses, run rules.py for times and dollars, one card per action, mark who decides. Opened when a step needs it: the files references/sop_text.md, references/gaps.md, scripts/rules.py and assets/action_card.md.
:width: 100%

How the d7-signal-sop skill loads (the figure shows five of its ten steps). The agent always sees the short
description, loads the steps only when a request fits, and opens a file only when a step needs it.
```

A skill is a folder. Its `SKILL.md` file holds a short description and the steps an experienced person
follows. Next to it sit the source's exact words, a glossary of the words people use in the field, small
scripts that compute the rules, and tests. Nothing is trained: a skill is written knowledge plus a little
code.

Because the agent reads only the description until a request fits, one agent can carry many skills
without filling its context (see {doc}`5.4 Context: what the model reads <module5/notes4-context>`). The
skills here follow the open [Agent Skills format](https://agentskills.io/specification), so the same
folder works in Claude, Claude Code and other agents that support the format.

## Why transportation needs its own skills

Anyone can ask a chatbot to write a skill "about the MUTCD". What it cannot write is the knowledge that
makes a skill worth trusting:

- the right edition, section and page;
- the threshold that must be computed in code, not guessed;
- the step the SOP leaves out that every crew knows;
- the decision the agency gives to a person, not to a computer.

That knowledge is with you: in your project, your lab's data, your agency's procedures, and the engineers
you work with. Shared in one open place, a skill can be checked, improved and used by every agency and lab,
instead of each one rebuilding it alone. The repository has one rule:

> **Every rule a skill states has a source, and every skill has tests.**

## Who can contribute, and what you can bring

| You are... | A skill you could build | Other ways to help |
|---|---|---|
| A student in AI for Mobility | The skill behind your project: damage codes from photos, coding crash narratives, checking a SUMO corridor study | Test another team's skill and report what failed |
| A researcher | A reader for a dataset and its pitfalls (NHTSA complaints, crash reports), a checklist for a method | Review skills in your area |
| Agency staff | Your SOP or procedure as a skill | Give a 20-minute interview so a skill holds your practice; review a skill |
| A consultant | A daily task: a warrant check, a work zone layout, QA/QC of a traffic study | Share the mistakes you see most often |

You do not need to write code to help. An interview, a list of lessons from a past storm, or a careful
review is a real contribution.

## Ideas to start from

| Suggested skill | The job | Main source |
|---|---|---|
| `mutcd-provision-lookup` | Find the MUTCD provisions for a device or situation and quote them by section, keeping Standard, Guidance, Option and Support apart | MUTCD 11th Edition (FHWA) |
| `signal-warrant-check` | Check intersection counts against the signal warrants, every threshold in code; the decision stays with an engineer | MUTCD 11th Edition, Chapter 4C |
| `nhtsa-complaint-reader` | Read NHTSA vehicle complaints: field meanings, component codes, finding ADAS complaints, counting without double counting | NHTSA complaints data |
| `sumo-run-and-check` | Check a SUMO run before reporting it: warm-up, teleports, vehicles waiting to enter, GEH against counts | SUMO documentation; [sumo-agent-tools](https://github.com/ai4mobility/sumo-agent-tools) |
| `wzdx-feed-check` | Check a work zone data feed: required fields, records past their end date, missing lane data | WZDx specification; [WZDx-Tools](https://github.com/ai4mobility/WZDx-Tools) |
| `survey123-form-fill` | Answer an agency's field form with its exact menu choices, one question at a time, with "unsure" | The agency's form definition |

The full list, with what each source allows you to copy, is in
[SKILLS_WANTED.md](https://github.com/ai4mobility/transportation-skills/blob/main/SKILLS_WANTED.md).
Before you start, open a *Skill proposal* issue so two people do not build the same skill.

(skills-build)=
## Build a skill in eight steps

```{figure} _static/figures/AGT_Knowledge_Homes.png
:alt: Four rows. Rule (a number, a time, a threshold) goes to code, scripts/rules.py; in the D7 signal SOP, first refuel 6 hours after deployment, encumber within 24 hours, DDIR at $5,000, 1/4 mile. Procedure (ordered steps) goes to the skill, SKILL.md plus references; for example the Immediately Post Storm steps. Guidance (long documents) goes to retrieval: quote the page and cite it; for example an after-action report, the MUTCD, a design manual. Judgment (the agency names who decides) goes to a person, as a checkpoint on the card; for example TMC personnel set generator priorities (Pre-Storm, Three Hours Prior, 2.2).
:width: 100%

Sort every piece of a manual into one of four homes. Code computes, the skill sequences, retrieval quotes,
and a person decides.
```

A skill is written for a **job**, not for a document. The same SOP can become three skills: one that looks
things up, one that writes action cards, and one that checks a plan. Start from the job. The worked example
for every step is the
[d7-signal-sop skill](https://github.com/ai4mobility/transportation-skills/tree/main/skills/d7-signal-sop),
built from the FDOT District 7 Traffic Signals SOP v1.5. A second example,
[journal-club-paper-review](https://github.com/ai4mobility/transportation-skills/tree/main/skills/journal-club-paper-review),
shows a research skill built from a guide for presenting journal papers instead of an agency SOP.

| # | Step | In the D7 example |
|---|---|---|
| 1 | **Name the job.** Who asks, what they need back, and three requests in the words they really use. | The signal team the morning after landfall needs action cards that cite the SOP. |
| 2 | **Keep the source's exact words**, with version, date, pages and an id for every piece. | 150 clauses from PDF pages 5–11, each with an id. |
| 3 | **Sort every piece into a home** (the figure above). | Refuel times go to code; generator priorities stay with TMC personnel. |
| 4 | **Write the reading path:** the steps an experienced person follows, and when to stop and ask. | Find the phase, read its clauses, run the rules, write cards, mark who decides. |
| 5 | **Add what the document leaves out:** field words, lessons from past events, practice from people who do the work, each kept apart from the source. | 48 field phrases, 6 lessons from FDOT and county documents, practice from an interview. |
| 6 | **Write the description** in the words of the requests from step 1, and say when to use it. | "...even in field words ('the lights are dark', 'top off the backup power')." |
| 7 | **Test it before you trust it:** requests that should and should not load it, tasks with checked answers, a checker in code. | The card checker passes all 9 example cards and catches all 4 planted mistakes. |
| 8 | **Keep it current:** record when you checked the sources, and re-check when they change. | SOP v1.5, June 2025; lessons dated. |

**Experience never becomes a rule by itself.** A lesson from a past storm or a tip from an operator goes in
as a *suggestion* that names where it came from and leaves the decision to a person. When experience and
the manual disagree, keep both and flag it. The repository's
[interview guide](https://github.com/ai4mobility/transportation-skills/blob/main/docs/INTERVIEW_THE_EXPERT.md)
has ten questions for a 20-minute conversation with someone who has done the job, and the
[writing guide](https://github.com/ai4mobility/transportation-skills/blob/main/docs/WRITING_SKILLS.md)
explains each step in more detail.

(skills-share)=
## Share it

```{figure} _static/figures/SKL_Share_Flow.png
:alt: Five columns from left to right. You bring: a job (who asks and what they need), a source (manual or SOP, edition and pages), and experience (field words, lessons, an expert's practice). You build: a skill folder copied from the template, with SKILL.md (the steps), references (sources, words), scripts (rules and tests) and evals (tests to pass). The repo checks: a pull request that changes one folder, checked for sources and reuse notes, limits, evals, and passing tests. Trust grows: draft (checks pass), then tested (with versus without the skill, 3 runs), then reviewed (a practicing engineer agreed). Everyone uses: any agent; claude.ai by uploading the zip, Claude Code by installing the plugin, other agents by copying the folder. A dashed arrow returns from the users to the contributors: issues, fixes, new lessons.
:width: 100%

How a skill gets into the repository and out to the people who use it. The knowledge is yours; the
repository checks it, says how far to trust it, and gets it to any agent.
```

1. **Claim a job.** Open a [Skill proposal](https://github.com/ai4mobility/transportation-skills/issues/new/choose)
   issue, or pick one from the list above.
2. **Fork the repository and copy the template** into `skills/` under your skill's name.
3. **Build it** with the eight steps.
4. **Write the evals and tests:** at least 3 requests that should load the skill, 3 near misses that should
   not, 2 tasks with checkable expectations, and a test for every script.
5. **Run the checks** on your computer.
6. **Open one pull request** that changes only your skill's folder. The same checks run again on GitHub.

```
cp -r template/new-skill skills/your-skill-name
pip install -r requirements-dev.txt
python tools/check_skill.py skills/your-skill-name
python -m pytest -q skills/your-skill-name/evals
```

The checker prints a plain line for every problem: a TODO left in the template, a source without a reuse
note, a file that `SKILL.md` mentions but that does not exist, a script without a test.

<div class="resource-callout">
  <p><strong>New to GitHub or Python?</strong> Let an AI assistant do the code, the git commands and the error messages. You can also work in a GitHub Codespace in your browser, with nothing to install. The repository's <code>AGENTS.md</code> file tells coding assistants to leave the transportation knowledge to you: the job, the sources, the steps, and the expected answers. That part is what makes the skill worth sharing.</p>
</div>

(skills-trust)=
## How far to trust a skill

Every skill carries a status, so a reader knows what has been checked.

| Status | What it means | Use it for |
|---|---|---|
| `draft` | Passes the checks. Sources, limits, evals and tests are written. | Trying it out and improving it |
| `tested` | Run with and without the skill, 3 times each, graded by hand. The results are in the skill's `evals/RESULTS.md`. | Research and class work |
| `reviewed` | A practicing professional read the skill and the results and agreed. Their role, agency and date are recorded. | Agency pilots, with a person still deciding |

To move a skill to `tested`, run its evals: `python tools/run_evals.py skills/your-skill-name --client claude`
runs every task with and without the skill through Claude Code, or `--client manual` writes a sheet for
doing the same runs by hand in claude.ai. You then grade each answer as right, partly right or wrong.

:::{admonition} Before you trust this result
:class: important
**What is the baseline?** The same agent and model, on the same requests, with the skill removed and no
other copy of it installed.

**How was the data split, and why is that honest?** The requests and their expected answers are written
before the first run, from the source or from a calculation you checked, never from a model's answer. Once
scoring starts the skill is frozen; if you change it, run everything again.

**What does it do on the ugly cases?** Near-miss requests that should not load it, requests in field words
that never name the manual, and cases where the source is silent and a person must decide. A skill that
loses to the baseline is still a result worth reporting: say so, and say why.
:::

## Use a skill

- **Claude (claude.ai or the desktop app):** download the skill's zip from the repository's
  [Releases](https://github.com/ai4mobility/transportation-skills/releases) page, then go to
  Customize > Skills > Upload a skill. Skills with scripts need code execution turned on.
- **Claude Code:** `/plugin marketplace add ai4mobility/transportation-skills`, then
  `/plugin install transportation-skills@ai4mobility`.
- **Other agents:** copy the folder `skills/<name>/` into the folder your agent reads skills from, and
  leave out `evals/`, which holds the expected answers.

Check the skill's status first, and check every output before you act on it. These skills are not
official products of FDOT, FHWA, NHTSA or any other agency, and they do not replace engineering judgment.

## Rules for sources and data

- **List every source** with edition, date and pages, and say what it allows you to copy.
- **U.S. federal documents** such as the MUTCD and NHTSA data can be quoted. **Copyrighted manuals and
  papers** (Highway Capacity Manual, AASHTO, ITE, journal articles) are cited only: write the steps in your
  own words and give the section and page. **Agency documents:** check the agency's terms, or ask for
  permission.
- **Never add the source document itself** (a PDF, Word or PowerPoint file), even a public one. Put only
  the pieces the job needs into the skill as text, and say where the full document can be found.
- **No personal information, no keys,** and no data you received under a use agreement, including course
  datasets shared on Canvas.
- **People you interview** are recorded by role and date, never by name, and only with their agreement.

## License: free to use, free to contribute

The repository uses the [MIT license](https://github.com/ai4mobility/transportation-skills/blob/main/LICENSE).
Anyone may use, copy, change and share the skills, including in paid work, as long as they keep the
copyright notice. When you contribute, your work comes in under the same license. You keep the copyright to
what you wrote; the license is the permission you give everyone else. Text a skill quotes from a source,
such as SOP clauses, keeps its source's own terms.

## Fit card

| Fit card — a skill | |
| --- | --- |
| **Idea in one sentence** | A folder of written steps, sources and small scripts that an agent opens only when a request matches its description. |
| **Why it works** | The agent follows an expert's reading path, reads only the part of the source it needs, and runs code for the numbers instead of guessing them. |
| **Fits these tasks** | Work that manuals, SOPs, codebooks and data dictionaries already describe: lookups, action cards, compliance checks, form filling, reading a dataset with known pitfalls. *Leverage: retrieval, extraction, classification, generation.* |
| **Needs this data** | A written source with edition and pages, the experience of people who do the job, and a few requests and tasks with checked answers. No training data. |
| **Breaks when** | The description does not match how people ask, the source changes and nobody re-checks, or the skill crowds out a better default. In one benchmark, curated skills raised the average pass rate from 33.9% to 50.5% but made results worse on 13 of 87 tasks (SkillsBench). |
| **Keep the classical method when** | The procedure is fixed and fully specified (write a script, no model needed); the job is fetching data or driving software (write a tool); or you have plenty of labeled examples for one narrow classification (your own trained model is often cheaper and more consistent). |

## Check yourself

1. A county crash-coding manual says to "use engineering judgment" when deciding whether a knocked-down
   sign counts as property damage only. Which of the four homes does that sentence go to, and what does the
   agent's answer say at that point?
2. Your MUTCD skill loads when someone asks "what does the MUTCD say about taper lengths?" but not when they
   ask "how far ahead of the lane closure does the first sign go?" What do you change first, and how do you
   check the fix?
3. You want to share a skill built on the Highway Capacity Manual. What may you put in `references/`, and
   what must stay out?
4. Your skill scores 3 of 3 with the skill and 3 of 3 without it on every task. Is it worth sharing? What
   would you test next?

## For students in AI for Mobility

- **Start from your project.** The skill you build with the eight steps for your own project (damage codes,
  crash narratives, a SUMO corridor check, a field form) can be your pull request to the repository.
- **The Canvas assignment page** says what is graded and when it is due.
- **Leave `AGENTS.md` in place.** It tells your coding assistant which parts are yours to write.
- **Your GitHub username is public** on a pull request. If you would rather not post course work publicly,
  ask the instructor for another way to submit.

## Sources and further reading

- The repository: [ai4mobility/transportation-skills](https://github.com/ai4mobility/transportation-skills),
  with its [contributing guide](https://github.com/ai4mobility/transportation-skills/blob/main/CONTRIBUTING.md),
  [writing guide](https://github.com/ai4mobility/transportation-skills/blob/main/docs/WRITING_SKILLS.md) and
  [interview guide](https://github.com/ai4mobility/transportation-skills/blob/main/docs/INTERVIEW_THE_EXPERT.md).
- [Agent Skills specification](https://agentskills.io/specification), the open format the skills follow.
- FDOT District 7 Traffic Signals SOP, v1.5 (June 2025), pages 5–11: the source of the worked example.
- Li, X., et al. (2026). SkillsBench. *arXiv:2602.12670*.
- In this course: {doc}`5.4 Context: what the model reads <module5/notes4-context>` and
  {doc}`Module 5 <module5/index>`.
