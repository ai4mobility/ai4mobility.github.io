# 1.1 What "AI" means here, and why the workflow is the unit of work

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 1 &middot; Section 1.1</span>
    <span class="notes-card-session">Session: Aug 27</span>
  </div>
  <p class="notes-card-lede">Where AI actually enters a transportation task. The five families and the job each is for; the workflow anatomy <strong>trigger &rarr; ingest &rarr; transform &rarr; act &rarr; checkpoint &rarr; record</strong>; the six leverage labels; the checkpoint rule; a worked Traffic Incident Management case; and how to read a capability claim. Read this one <em>before</em> the first meeting &mdash; it is the vocabulary that makes the project choice possible.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Interactive companions on this page</h4>
      <ul>
      <li><a href="../_static/companions/TIM_AI_Workflow_Case.html" target="_blank" rel="noopener">Traffic Incident Management as an AI workflow &#8599;</a></li>
      <li><a href="../_static/companions/AI_Workflow_Companion.html" target="_blank" rel="noopener">Anatomy of an AI workflow &#8599;</a></li>
      </ul>
    </div>
    <div>
      <h4>Notebooks that go with it</h4>
      <ul>
      <li><a href="lab1.html">Lab 1 &mdash; Python and ML warmup</a></li>
      </ul>
    </div>
  </div>
</div>


## Five families, and which job each is for

We use "AI" as a loose umbrella. It is worth being precise about what sits under
it, because the families have genuinely different failure modes.

**Classical machine learning.** Linear and tree-based models, SVMs, clustering.
Old, unglamorous, and still the right answer for a surprising number of
transportation problems — especially when the input is tabular sensor data and
somebody has to explain the model to a review board.

**Deep learning.** Neural networks trained end-to-end. The dominant approach for
vision, speech, and increasingly time series. The default when the input is an
image, a video, or a raw sensor waveform.

**Computer vision.** A specialized branch of deep learning: detecting and
tracking objects in images and video. Central to traffic monitoring and to
vehicle perception. Module 5 lives here.

**Reinforcement learning.** Agents that learn by interacting with an
environment. Used for signal control, driving policy, and dispatch. Powerful,
and notoriously hard to make reliable for anything safety-critical.

**Large foundation models.** LLMs, vision-language models, multimodal models.
Now appearing in agency workflows for incident description, document search,
report drafting, and natural-language querying of traffic data.

Throughout the course we will be honest about which tool fits which job.
Sometimes that means deep learning is overkill, and saying so is a professional
skill rather than a failure of ambition.

## The unit of work is the workflow, not the model

Here is the move that organizes the whole semester. When someone says "we're
using AI for crash reports," they have not told you anything actionable. Crash
reporting is a *process*: a report gets filed, someone reads it, fields get
coded into a database, the database feeds a safety analysis, the analysis
supports a project decision. AI does not do that process. AI does one or two
*steps* of it.

So we describe tasks as workflows with a fixed anatomy:

> **trigger → ingest → transform → act → checkpoint → record**

Something happens (trigger). Data comes in (ingest). Something is computed
(transform). A decision or output is produced (act). A human confirms before
anything irreversible happens (checkpoint). The result and its provenance are
written down (record).

You already know this shape. The four-step travel demand model is a workflow:
trip generation, distribution, mode choice, assignment — with a validation gate
against observed counts before anyone uses the output for a project decision.
That validation gate is a checkpoint. Nobody calls it that, but it is the same
object.

## Six kinds of leverage

Once a task is written as a workflow, label each step by what an AI system would
actually contribute. There are six labels, and we will use them all semester:

| Label | What it does | Mobility example |
|---|---|---|
| **extraction** | pulls structured fields out of unstructured input | crash narrative → coded contributing factor |
| **classification** | assigns a category from a fixed or open set | dashcam frame → sign type, or "sign is damaged" |
| **generation** | produces new text, code, or data | draft incident summary; synthetic scenarios |
| **retrieval** | finds the relevant item in a large corpus | which manual section governs this design exception |
| **prediction** | estimates a value not yet observed | travel time in 15 minutes; clearance duration |
| **judgment** | weighs incommensurable things and decides | which project gets funded; whether to close a lane |

Five of these are steps you can consider handing over. The sixth is not.
**Judgment is not a step you can hand over.** A model can inform it, order the
options, surface what you missed. It cannot own it, and a workflow diagram that
assigns judgment to a model is a workflow diagram that is going to hurt someone.

The phrase to keep is: **"AI must not act alone here."** Write it on the steps
where it applies, and be able to say why.

## The checkpoint rule

Where does the human review go? There is one rule and it is not negotiable:
**immediately before the first irreversible action.**

Not at the end, where the mistake has already been recorded. Not at the
beginning, where there is nothing yet to review. Immediately before the first
step whose output is expensive or impossible to take back — a record written to
the crash database, a work order issued, a signal timing plan pushed to a
controller, a message posted to a DMS.

This rule also tells you where the *value* of automation is. If the checkpoint
requires a human to re-do the work in order to check it, you have automated
nothing. A good workflow produces output a human can *verify* much faster than
they could *produce* it. That asymmetry — cheap to check, expensive to make — is
the real precondition for AI leverage, and it is worth testing explicitly before
you commit to a project.

## Worked case: Traffic Incident Management

The companion case study takes one Florida-anchored process — traffic incident
management, from detection through verification, response, clearance, and
after-action recording — and works it all the way through: every step labeled,
the checkpoint placed, the baseline named, and the places where the honest
answer is "no AI here" marked as such.

TIM is a good first case for a specific reason. It is a workflow where the
performance measures already exist and are already collected, so the baseline
question has a real answer rather than a hand-wave. It is also a workflow where
the eight structural differences between "a model that works in a paper" and "a
system that works on the road" are all visible at once.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Worked case — Traffic Incident Management as an AI workflow</span>
    <a href="../_static/companions/TIM_AI_Workflow_Case.html" target="_blank" rel="noopener">Open full screen ↗</a>
  </div>
  <iframe src="../_static/companions/TIM_AI_Workflow_Case.html"
          title="Traffic Incident Management as an AI workflow" loading="lazy"></iframe>
</div>

## What your graduate training already buys you

A recurring worry in a course like this is that the transportation background is
the thing being replaced. It is not, and the workflow framing is what makes that
concrete.

Traffic flow theory tells you what a plausible output looks like, which is how
you catch a model that has learned something absurd. Statistics tells you
whether a difference is real. The four-step model and simulation experience tell
you what a validation gate is and how it fails. Design manuals tell you what the
constraint actually is, not what the data suggests. Safety analysis tells you
what the cost of a false negative is. Field data collection tells you how dirty
real data is before anyone cleans it. TSM&O practice tells you who has to act on
the output and how fast. Programming and writing turn all of that into something
that runs and something that persuades.

The scarce skill in this field is not building the model. It is knowing which
step is safe to automate and how to prove the result. That is a transportation
engineering skill, and you are most of the way to having it.

## Reading a capability claim

Every result you meet — in a paper, a vendor deck, or a press release — gets the
same four questions:

1. **What is the baseline?** Beating "naive linear regression" is not the same
   as beating a well-tuned ARIMA, and beating a fixed-time signal plan is not
   the same as beating a properly configured actuated controller.
2. **What is the test set?** Was it separated from the training data
   *geographically and temporally*, or is it a random split of one corridor on
   one week, in which case the model may simply have memorized that week?
3. **What is the cost of failure?** 95% accuracy is fine for vehicle counting
   and catastrophic for emergency braking. The number means nothing until you
   know which side of that line you are on.
4. **Does the deployment story work?** Many published models assume compute,
   connectivity, or labeling budgets that no real agency has.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion — Your first AI workflow</span>
    <a href="../_static/companions/AI_Workflow_Companion.html" target="_blank" rel="noopener">Open full screen ↗</a>
  </div>
  <iframe src="../_static/companions/AI_Workflow_Companion.html"
          title="Your first AI workflow" loading="lazy"></iframe>
</div>

:::{admonition} Before you trust this result
:class: important
**What is the baseline?** · **How was the data split, and why is that honest?** ·
**What does it do on the ugly cases?**

For a workflow, the baseline is not a model — it is the current process, with
its current numbers. How long does it take today, how often is it wrong today,
how much does it cost today. If you cannot state those three numbers, you cannot
claim an improvement. Bring the real ones; do not estimate them and do not
invent them.
:::

---

Next: {doc}`notes2-networks` builds a neural network out of the discrete-choice model you already use.
