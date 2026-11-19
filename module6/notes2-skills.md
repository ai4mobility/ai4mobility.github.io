(inside-a-skill)=
# 6.2 Inside a skill: packaging transportation know-how

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 6 &middot; Section 6.2</span>
    <span class="notes-card-session">Session: Skills, lecture 1 &mdash; how skills work</span>
  </div>
  <p class="notes-card-lede">Section 6.1 placed a skill among the eight places knowledge can reach an agent. This section opens two skills from the course's transportation-skills repository, file by file: <code>d7-signal-sop</code>, built from FDOT District 7's hurricane signal SOP, and <code>journal-club-paper-review</code>, built from the instructor's journal-club guide. You will see how a skill is laid out as a folder, how its SKILL.md sends the model to the right file at each step, and how to turn your own know-how into a skill. You will also see what changed when the same request was run with and without the skill.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Read it first</h4>
      <ul>
      <li><a href="../module5/notes3-tools.html">5.3 Tools: what an agent can reach</a> (what is inside a tool)</li>
      <li><a href="notes1-knowledge.html">6.1 Where knowledge lives</a> (where a skill sits among the eight places)</li>
      </ul>
    </div>
    <div>
      <h4>Used again in</h4>
      <ul>
      <li><a href="../skills.html">Transportation Skills</a> (build a skill in eight steps and share it)</li>
      <li><a href="../module8/notes1-data.html">8.1 AI-ready data</a> (a data dictionary loaded as a skill)</li>
      </ul>
    </div>
  </div>
</div>

## What this section covers

- A skill is a folder: what goes in it, and when the model sees each part
- How `SKILL.md` sends the model to its files
- Turning transportation know-how into a skill
- The same request with and without the skill
- The interactive companion
- What to do for your project

## A skill is a folder

A tool gives the model an action: a name, a description, an input schema, and code that runs
({doc}`5.3 <../module5/notes3-tools>`). A skill gives the model know-how for one job, packed as a folder. Here is the D7
skill, with what each file holds:

```text
d7-signal-sop/
├── SKILL.md              name + description, then the steps (the reading path)
├── references/
│   ├── sop_text.md       150 SOP clauses, word for word, split by phase
│   ├── clauses.json      the same clauses as data, read by the checker
│   ├── glossary.md       48 field phrases mapped to the SOP's words
│   ├── gaps.md           10 things the SOP does not say
│   ├── lessons.md        6 lessons from past storms (suggestions only)
│   └── practice.md       what staff say (from an interview)
├── assets/
│   └── action_card.md    the card format the answer copies
├── scripts/
│   ├── rules.py          the SOP's times and dollar limits as code
│   └── check_cards.py    checks the cards before anyone acts on them
└── evals/                tests, never shown to the model
```

The model does not read all of this at once. Its name and description (144 tokens) are in front of the
model in every chat. The `SKILL.md` body (1,653 tokens) is read once a request matches the description. Other
files are opened only when a step asks for them: the whole SOP text is 6,246 tokens, but one phase is about
1,177. Scripts are run, not read, and only what they print comes back: 74 tokens for a refuel time. The
journal-club skill has the same shape. Its folder holds the guide (`references/guide.md`), a reviewer's
transportation checks, the format of the notes (`assets/`), and a slide budget and a notes checker
(`scripts/`).

## How `SKILL.md` sends the model to its files

A file path in `SKILL.md` does nothing by itself. Each step of a good skill does five things:

- **Names the file and the moment:** "`references/gaps.md`: what the SOP does not say. Read it before you answer."
- **Says how much to read:** "Read the section for the phase you are in, not the whole file."
- **Gives the exact command:** `python3 scripts/rules.py refuel "2026-10-10 06:10"`, then "Never compute these yourself."
- **Keeps sources apart:** "Never put a lesson in a card's SOP field."
- **Ends with a check:** run the checker, "Fix every FAIL line, then run it again."

## Turning know-how into a skill

Write a skill for a job, not for a document. Then sort what you know before you write `SKILL.md`, because each
kind of know-how fails in its own way:

<div class="practice-table-wrap">
<table class="practice-table notes-map">
<thead>
<tr><th style="width:18%">Kind</th><th style="width:30%">Home in the skill</th><th style="width:52%">D7 example</th></tr>
</thead>
<tbody>
<tr><td><strong>Rule</strong> (a number, a time)</td><td><code>scripts/</code>, with a test</td><td>First refuel six hours after deployment</td></tr>
<tr><td><strong>Procedure</strong></td><td>The steps in SKILL.md</td><td>Check ATMS, send the SAT pass, then deploy generators</td></tr>
<tr><td><strong>Guidance</strong> (long text)</td><td><code>references/</code>, one section at a time</td><td>The SOP clauses, quoted word for word</td></tr>
<tr><td><strong>Judgment</strong></td><td>"Person decides: yes", and who</td><td>TMC personnel set generator priorities</td></tr>
<tr><td><strong>Experience</strong></td><td><code>lessons.md</code> and <code>practice.md</code>, used only as suggestions</td><td>Stop control when no generator is left (lesson L1)</td></tr>
<tr><td><strong>Field words</strong></td><td><code>glossary.md</code></td><td>"Backup power" means generator</td></tr>
<tr><td><strong>Gaps</strong></td><td><code>gaps.md</code></td><td>The zone-map appendix is blank in v1.5</td></tr>
</tbody>
</table>
</div>

The last three rows are the part no model has read: the words crews use, what the manual leaves blank, and
what went wrong last time. Only someone who knows the work can write them. The eight steps, from naming the
job to keeping the skill current, are on the {doc}`Transportation Skills <../skills>` page.

## The same request, with and without the skill

Each skill's first test task (from its `evals.json`) was run three ways by the same model. Each run was a
fresh session with no web search: once with no skill, once with the source document attached, and once with
the skill installed. Each answer was graded against expectations written before any run.

<div class="practice-table-wrap">
<table class="practice-table notes-map">
<thead>
<tr><th style="width:46%">Task</th><th style="width:18%">No skill</th><th style="width:18%">Document only</th><th style="width:18%">Skill installed</th></tr>
</thead>
<tbody>
<tr><td>D7: action cards for the 12 hours after landfall (5 expectations)</td><td>2</td><td>3.5</td><td>5</td></tr>
<tr><td>Journal club: review notes and a 20-minute slide outline (10 expectations)</td><td>7.5</td><td>7</td><td>10</td></tr>
</tbody>
</table>
</div>

- **D7.** With the SOP attached, the model got the refuel times right (12:10 and 12:40). It even found that the
  $5,000 rule is written two ways. But it told the TMC to rank signals using "the Priority #1 list from the
  zone maps". The SOP has no such list, and its zone-map appendix is blank. Only the skill's list of gaps
  prevented that answer.
- **Journal club.** All three runs found every planted problem in the synthetic paper. The skill did not make
  the model a sharper critic. It added the group's rules: the six-part format that a script can check,
  10 slides for 20 minutes, the opinion questions handed back to the presenter, and no references cited
  from memory.

**Before you trust these scores:** there was one run per condition, the grader knew which answer was which,
and the inputs are synthetic. Read the scores as a demonstration, not a measurement. The companion shows all six
answers unedited, with each run's trace, so you can check every grade.

(inside-a-skill-companion)=
## Interactive companion

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion &mdash; Inside a skill: two transportation skills, opened up</span>
    <a href="../_static/companions/Inside_A_Skill_Companion.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/Inside_A_Skill_Companion.html"
          title="Inside a skill: two transportation skills, opened up" loading="lazy"></iframe>
</div>

Eight tabs:

1. What a skill is.
2. Open the folder: click any file of either skill to read it as committed, colored by who uses it.
3. Read the `SKILL.md`: a map of which step opens which file, and both `SKILL.md` files annotated block by block.
4. Watch it run: the real steps of the two skill runs, with the scripts' real output.
5. Write your own, with a sorting exercise and interview questions.
6. What matters most.
7. With and without: the full grades and the six answers.
8. A fit card and check-yourself questions.

## For your project

- Pick one job your project repeats, and write down three requests in the words people really use.
- Sort your source into the homes above before you write `SKILL.md`.
- Write `gaps.md`, and name a person for every decision your source gives to someone.
- Put every number and threshold in `scripts/` with a test, and end the steps with a checker.
- Run one task three ways (no skill, document only, skill) and report the difference, including where the
  skill does not help.

## Check yourself

1. A classmate wants to paste all of MUTCD Part 6 into `SKILL.md` "so the agent knows everything." What do you
   tell them, and where should the material go instead?
2. The document-only D7 run had the full SOP and still lost points. Which file in the skill made the
   difference, and why can't pasting the document more carefully fix it?
3. Your project team trained its own damage classifier. Would a skill replace it, help it, or not apply?
   What would the skill contain?

## Sources

- The [d7-signal-sop](https://github.com/ai4mobility/transportation-skills/tree/main/skills/d7-signal-sop) and
  [journal-club-paper-review](https://github.com/ai4mobility/transportation-skills/tree/main/skills/journal-club-paper-review)
  skills in the [transportation-skills](https://github.com/ai4mobility/transportation-skills) repository
  (commit 4b7bc8d). The scenario and the paper used in the runs are synthetic.
- FDOT District 7. *Traffic Signals Standard Operating Procedures Reference Guide*, v1.5 (June 2025), pages 5&ndash;11.
- [Agent Skills specification](https://agentskills.io/specification), the open format the course skills follow.
- Anthropic (2025). [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills).
- Li, X., et al. (2026). SkillsBench. *arXiv:2602.12670*.
- In this course: {doc}`5.3 Tools <../module5/notes3-tools>`, {doc}`6.1 Where knowledge lives <notes1-knowledge>` and
  {doc}`Transportation Skills <../skills>`.
- Agents unit credit: CMU 11-768 *AI Agents* (Fried and Neubig); Stanford CS 329Z *Engineering AI Agents*.

---

Next: {doc}`6.3 A worked agent <notes3-signal-agent>`, the hurricane signal SOP run by an agent with tools and skills.
Then {doc}`Module 7 <../module7/index>`, what an agent reads and remembers. The rest of the skills material (how a
model decides to load a skill, building a skill in eight steps, and putting domain experience into it) will be added
to {doc}`this module <index>` after the two skills lectures.
