# Module 7 Notes — Traffic Simulation, Digital Twins, and Operations

*Session: Nov 5, 2026. This chapter has two halves. The first is the framing the
whole course uses for where AI enters a transportation task — the workflow, its
anatomy, and the rule about where a human belongs in it. The second is the
module's own subject: simulation, digital twins, and the operations work an
agency actually does.*

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 7 &middot; Section 7.1</span>
    <span class="notes-card-session">Session: Nov 5</span>
  </div>
  <p class="notes-card-lede">Where AI actually enters a transportation task. The workflow anatomy <strong>trigger &rarr; ingest &rarr; transform &rarr; act &rarr; checkpoint &rarr; record</strong>; the six leverage labels used across the course; the checkpoint rule; and a Florida-anchored Traffic Incident Management case worked all the way through. This is operations material, which is why it sits in this module rather than with the AI foundations in Module 1.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Interactive companions on this page</h4>
      <ul>
      <li><a href="../_static/companions/AI_Workflow_Companion.html" target="_blank" rel="noopener">Anatomy of an AI workflow &#8599;</a></li>
      <li><a href="../_static/companions/TIM_AI_Workflow_Case.html" target="_blank" rel="noopener">Traffic Incident Management as an AI workflow &#8599;</a></li>
      <li><a href="../_static/companions/Newell_LWR_CNN_Companion.html" target="_blank" rel="noopener">Newell&rsquo;s shift and the LWR shockwave as convolutions &#8599;</a></li>
      </ul>
    </div>
    <div>
      <h4>Labs that go with it</h4>
      <ul>
      <li><a href="index.html#labs">RL signal control in SUMO</a></li>
      <li><a href="index.html#labs">Sensor simulation in CARLA</a></li>
      </ul>
    </div>
  </div>
</div>

:::{admonition} How to read this chapter
:class: tip
Section 7.1 is vocabulary rather than method. It was introduced in the first
class of the semester and is written up here, with the operations material it
belongs to. If you are picking a project or reading a vendor claim, this is the
section to have open.

Section 7.2 covers the module's own subject and is written up after the Nov 5
session; the {doc}`index` page carries the topics, readings and labs in the
meantime.
:::

---

## 7.1 The workflow is the unit of work

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

### Six kinds of leverage

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

### The checkpoint rule

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

### Worked case: Traffic Incident Management

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

### Two things to carry out of this section

**Exercise — workflow audit.** Take a process you have actually worked on. Write
it as trigger → ingest → transform → act → checkpoint → record. Label every step
with one of the six leverage labels, mark the steps where AI must not act alone,
and place the checkpoint immediately before the first irreversible action. State
the three baseline numbers for the current process: how long, how often wrong,
how much.

**On the job.** When someone pitches you an AI system, ask for the workflow
diagram before the architecture diagram. Which step is being automated, what is
the checkpoint, and what is the current process's baseline number. A vendor who
cannot produce those three things has not deployed the system anywhere that
measured it. And before you fund a pilot: is the output cheaper to verify than
to produce? If verifying requires a human to re-do the work, the pilot will show
a time saving that evaporates at scale.

---

## 7.2 Simulation, digital twins, and operations

*This section is written up after the Nov 5 session.* Until then the
{doc}`index` page carries the module's topics, the recommended readings, the lab
list, and the Newell/LWR interactive companion — which is the piece of this
half that is already built, and which shows a classical traffic model to
*already be* a convolution before any network is trained.
