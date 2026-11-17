(where-knowledge-lives)=
# 6.1 Where knowledge lives: giving an agent the right knowledge

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 6 &middot; Section 6.1</span>
    <span class="notes-card-session">Session: Skills, lecture 1 &mdash; how skills work</span>
  </div>
  <p class="notes-card-lede">A strong model knows what a generator and a mast arm are. It has not read FDOT District 7's hurricane signal SOP. This section names the eight places agency knowledge can reach an agent, splits them into what the model reads on every call and what it opens only when a step needs it, and follows one hurricane-morning request through them on the course's D7 signal skill. The interactive companion at the end counts what each step puts in front of the model.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Read it first</h4>
      <ul>
      <li><a href="../module5/notes3-tools.html">5.3 Tools: what an agent can reach</a></li>
      <li><a href="../module5/notes5-architectures.html">5.4 Agent architectures</a> (Q2, reach)</li>
      </ul>
    </div>
    <div>
      <h4>Used again in</h4>
      <ul>
      <li><a href="notes2-skills.html">6.2 Inside a skill</a> (two skills opened up, with and without)</li>
      <li><a href="../skills.html">Transportation Skills</a> (build a skill in eight steps and share it)</li>
      <li><a href="../module7/notes2-rag.html">7.2 Retrieval (RAG)</a> (the retrieval home, in depth)</li>
      </ul>
    </div>
  </div>
</div>

## What this section covers

- What a model already knows, and what it has to be given
- Eight places knowledge can reach an agent
- Four kinds of knowledge, and the place each one belongs
- Every call, or only when a step needs it: what each choice costs
- One hurricane-morning request, traced step by step
- The interactive companion
- What to do for your project

## What the model knows, and what it has not read

A general model has read a great deal about traffic signals. Ask it what a mast arm is and it answers from its
training, with nothing else in front of it. Ask it when the District 7 signal team should first refuel a generator
that went out at 06:10, and it cannot know. The answer is clause 3.2.1 of the D7 Traffic Signals SOP (v1.5, June
2025): "First refueling to occur six (6) hours after initial deployment." If nothing puts that clause in front of the
model, it guesses, and a guess that reads well is worse than no answer.

So the design question is not "how do I make the model smarter?" It is: **where does each piece of the agency's
knowledge go, so that the model has it at the step that needs it, and a person can check where it came from?**

## Eight places knowledge can reach an agent

<div class="practice-table-wrap">
<table class="practice-table notes-map">
<thead>
<tr><th style="width:5%">#</th><th style="width:18%">Place</th><th style="width:22%">When the model sees it</th><th style="width:55%">In the D7 signal example</th></tr>
</thead>
<tbody>
<tr><td>1</td><td><strong>Instructions</strong></td><td>Every call</td><td>Who the agent serves, the answer format, and what it must never do: rank intersections or set generator priorities, because TMC personnel do that.</td></tr>
<tr><td>2</td><td><strong>Labeled examples</strong></td><td>Every call</td><td>Two good action cards, and one card that was sent back, with the reason.</td></tr>
<tr><td>6</td><td><strong>The output form</strong></td><td>Every call</td><td>The six-field action card: Do, Who, When, SOP, Weight, Person decides.</td></tr>
<tr><td>3</td><td><strong>Skill</strong></td><td>Only its one-line description on every call; the rest when a step needs it</td><td><code>d7-signal-sop</code>: <code>SKILL.md</code> (the reading path), the SOP text split by phase, a glossary of field words, the gaps, and lessons from past storms.</td></tr>
<tr><td>4</td><td><strong>Retrieval</strong></td><td>When a step needs a passage</td><td>Search over documents too long to load, such as the MUTCD or after-action reports, quoted with section and page.</td></tr>
<tr><td>5</td><td><strong>Code and tools</strong></td><td>When a step needs a number</td><td><code>scripts/rules.py</code>: refuel times, SAT passes, emergency TWO checks, DDIR grouping.</td></tr>
<tr><td>7</td><td><strong>A person</strong></td><td>After the model, when a decision comes back</td><td>The people the SOP names: TMC personnel, the operations centers, the DDIR team.</td></tr>
<tr><td>8</td><td><strong>The weights</strong></td><td>Always: it is the model itself</td><td>What a mast arm is, what a generator does. Nothing to load, and nothing to cite.</td></tr>
</tbody>
</table>
</div>

The numbers follow the companion's figure, where places 1, 2 and 6 sit in the left column (sent with every call) and
places 3, 4 and 5 sit in the right column (opened on request).

You already work this way. On a storm morning at the TMC, the one-page card taped to the console is always in front of
you: who you serve and what never to do (the instructions). The SOP binder sits on the shelf until you need a step (the
skill). The MUTCD is down the hall, and you pull one section (retrieval). You use a calculator for clock times, not your
head (code). Some calls go to the TMC supervisor (a person). And your training tells you what a mast arm is without
opening anything (the weights).

## Four kinds of knowledge, four homes

```{figure} ../_static/figures/AGT_Knowledge_Homes.png
:alt: Four rows. A rule (a number, a time, a threshold) goes to code, scripts/rules.py; in the D7 SOP, first refuel 6 hours after deployment, encumber within 24 hours, DDIR at $5,000 and 1/4 mile. A procedure (ordered steps) goes to the skill, SKILL.md plus references; for example the Immediately Post Storm steps. Guidance (long documents) goes to retrieval, quoting and citing the page; for example an after-action report, the MUTCD, a design manual. A judgment the agency assigns goes to a person, as a checkpoint on the card; for example TMC personnel set generator priorities (Pre-Storm, Three Hours Prior, 2.2).
:width: 100%

Code computes, the skill sets the order of steps, retrieval quotes, a person decides.
```

Before you decide where a piece of the SOP goes, decide what kind of knowledge it is.

- **A rule with a number goes to code.** The model should not add six hours to 06:10 in its head. `rules.py refuel`
  returns 12:10, and the card cites clause 3.2.1.
- **A procedure goes to the skill.** `SKILL.md` is a reading path: which file to open at each step, in order.
- **Long guidance goes to retrieval**, and every passage comes back with its page.
- **A judgment the agency assigns goes to a person.** The card marks it "Person decides: yes" and names who.

Two clauses next to each other can belong in different places. "First refueling to occur six (6) hours after initial
deployment" is a rule, so it goes to code. "Develop an ongoing refueling schedule based on fueling needs" gives no
rule, so the schedule after the first refuel goes to a person, and the skill's `gaps.md` file says so. Writing down what
the SOP does *not* say matters as much as the rest: otherwise the model fills the gap itself.

## Every call, or only when a step needs it

Anything in the left column is paid for on every request, including the requests that never use it. For the D7 skill,
the left column (instructions, two example cards, the card format, the skill's description, and the request itself)
comes to about **1,000 tokens**. The whole SOP text is about **6,246 tokens**; its Immediately Post Storm section alone,
29 of the 150 clauses, is about **1,177**.

Averaged over the eight requests in the companion, a request puts about **2,771 tokens** in front of the model when the
skill's files open only when a step needs them, and about **11,716** when every file is sent on every call: roughly four
times as much. A question such as "what is a mast arm?" never opens the skill at all and stays at 1,000.

Tokens are not the only cost. Pasting the whole SOP into the instructions also throws away the reading path. With all
150 clauses in front of it, the model has to find the right phase by itself on every request; the skill's steps do that
job for it. The RAG companion in {doc}`7.2 <../module7/notes2-rag>` measures the same problem from the other side: for a
72-hour plan, meaning search put only 3 of the 15 needed SOP items in its top three, while a filter on the SOP's own
sections found all 15. A skill is where that filter gets written down.

The counts on this page use the o200k tokenizer, so read them as estimates; Claude counts somewhat differently. They
also count what is in front of the model once. A real agent calls the model several times for one request, and each
call re-reads everything so far, so the tokens billed across a run are larger. That is one more reason to keep the left
column short and stable.

## One hurricane morning, step by step

The class scenario (synthetic): it is 07:30 the morning after landfall in Pinellas County. ATMS on US-19 shows 31
signals: 18 green, 6 yellow, 7 red. Generator NH-114 went out at 06:10 and NH-121 at 06:40. The request: *"Both
generators went out early this morning. What should the signal team do over the next 12 hours, and when do we top them
off?"*

<div class="practice-table-wrap">
<table class="practice-table notes-map">
<thead>
<tr><th style="width:5%">Step</th><th style="width:25%">What happens</th><th style="width:52%">What opens</th><th style="width:18%">In front of the model (tokens)</th></tr>
</thead>
<tbody>
<tr><td>1</td><td>The left column is already there</td><td>Instructions, example cards, card format, skill descriptions, the request. None of the 150 clauses yet.</td><td>1,000</td></tr>
<tr><td>2</td><td>Is there a skill for this job?</td><td>"Generators", "after a storm" and "District 7" match the skill's description, so <code>SKILL.md</code> comes back.</td><td>2,220</td></tr>
<tr><td>3</td><td>Translate the field words</td><td><code>glossary.md</code>: "top off" means refueling, and the units are generators.</td><td>3,515</td></tr>
<tr><td>4</td><td>Find the phase, read only that</td><td>The Immediately Post Storm section of the SOP, not the whole file.</td><td>4,692</td></tr>
<tr><td>5</td><td>A number is needed</td><td><code>rules.py refuel</code> for each generator: 12:10 and 12:40, each with clause 3.2.1 attached.</td><td>4,840</td></tr>
<tr><td>6</td><td>A passage the skill does not hold</td><td>If the operator also asked about the MUTCD, a search tool would return the quoted passage. Shown as a pattern only.</td><td>4,840</td></tr>
<tr><td>7</td><td>A decision the SOP gives to someone</td><td>Which red signal gets the next free generator goes to TMC personnel (Three Hours Prior 2.2). Nothing is loaded.</td><td>4,840</td></tr>
<tr><td>8</td><td>Say what is blank</td><td><code>gaps.md</code>: for example, the zone map appendix is blank in v1.5, and the card names who to ask.</td><td>5,361</td></tr>
<tr><td>9</td><td>The answer, in the agency's form</td><td><code>lessons.md</code> and <code>practice.md</code> for suggestions; then action cards that each quote a clause, and a "Not covered" list. <code>check_cards.py</code> reads them before anyone acts.</td><td>6,707</td></tr>
</tbody>
</table>
</div>

The run ends at about 6,707 tokens. Pasting everything in at the start would have put about 11,484 in front of the model
at step 1, without the reading path.

(where-knowledge-lives-companion)=
## Interactive companion

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion &mdash; Where knowledge lives: eight places, one hurricane morning</span>
    <a href="../_static/companions/Where_Knowledge_Lives_Companion.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/Where_Knowledge_Lives_Companion.html"
          title="Where knowledge lives: eight places, one hurricane morning" loading="lazy"></iframe>
</div>

Five tabs: the eight places (click any box to see what it holds for D7, with real files from the course kit and their
token counts); one hurricane morning (the nine steps above, with the figure lighting each arrow and a running meter); try
a request (eight requests, from a refuel time to "what is a mast arm?", each with its route, its tokens and the answer
the skill produces); what it costs (move each skill file between "every call" and "only when needed" and watch a storm
day's total); and a fit card with check-yourself questions. Every excerpt is read from the kit's files, and every tool
result comes from running `rules.py`.

## For your project

- Write the left column in under a page: who the agent serves, the output form, and what it must never do.
- Put your manual in a skill, split along its own numbering, with a reading path that names the file each step opens.
- Put every number, threshold and deadline in code, with a test on a known answer.
- Use retrieval only for documents too long to load, and quote every passage with its page.
- Name the person for every decision your agency assigns, and list what your manual does not say.

To build the skill and share it, follow the eight steps on the {doc}`Transportation Skills <../skills>` page.

## Check yourself

1. Your project's agent works with (a) twelve damage categories with one-line definitions, (b) a 200-page inspection
   manual, (c) a rule that each report is filed within 24 hours of the inspection, and (d) the decision to close a road.
   Put each in one of the eight places, and say why.
2. Suppose a new version of the SOP moves the first refuel from six hours to eight. List every place in the D7 harness
   that has to change, and say how you would find out if one was missed.
3. Of the eight places, which one can no one on your team open and read before the agent runs? What does that mean
   for where you put a rule the agency must follow?

## Sources

- FDOT District 7. *Traffic Signals Standard Operating Procedures Reference Guide*, v1.5 (June 2025), pages 5&ndash;11.
- The course's [d7-signal-sop skill](https://github.com/ai4mobility/transportation-skills/tree/main/skills/d7-signal-sop)
  in the [transportation-skills](https://github.com/ai4mobility/transportation-skills) repository. The scenario,
  generators and repairs are synthetic.
- Anthropic. [Agent Skills overview](https://claude.com/docs/skills): how a skill loads in three stages.
- [Agent Skills specification](https://agentskills.io/specification), the open format the course skills follow.
- In this course: {doc}`7.2 Retrieval (RAG) <../module7/notes2-rag>` (the RAG companion) and
  {doc}`Transportation Skills <../skills>`.
- Agents unit credit: CMU 11-768 *AI Agents* (Fried and Neubig); Stanford CS 329Z *Engineering AI Agents*.

---

Next: {doc}`6.2 Inside a skill <notes2-skills>`, two transportation skills opened up file by file.
