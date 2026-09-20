# Module 7 Notes — Traffic Simulation, Digital Twins, and Operations

*Session: Nov 5, 2026. This chapter has two halves. The first is the framing the
whole course uses for where AI enters a transportation task — the workflow, its
anatomy, and the rule about where a human belongs in it. The second is the
module's own subject: simulation, digital twins, and the operations work an
agency actually does.*

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 7 &middot; Sections 7.1&ndash;7.2</span>
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
      <li><a href="../_static/companions/GNN_On_A_Road_Network_Companion.html" target="_blank" rel="noopener">A GNN on a road network &#8599;</a></li>
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

Section 7.2 covers the module's own subject. Its opening half — learned models
standing in for simulators, on a corridor and on a network — is written up now;
digital twins, the SUMO and CARLA workflows and the operations material follow
the Nov 5 session. The {doc}`index` page carries the topics, readings and labs in
the meantime.
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

The question this half of the module keeps asking is a narrow one: **can a
learned model stand in for a simulator?** Not "is AI good at traffic" — whether
a network trained on data can do the job a calibrated model does today, and what
you give up when it does.

Two pieces of that question are written up now. Both answer it the same way, by
showing a classical traffic model to *already be* the neural architecture people
reach for — which is the honest way to compare them, because it puts the two on
the same footing instead of pitting a tuned network against a strawman. The
Newell/LWR companion on the {doc}`index` page does it for a **corridor**, where
the model turns out to be a convolution. The section below does it for a
**network**, where the model turns out to be a graph neural network. The rest of
7.2 — digital twins, SUMO and CARLA workflows, signal control and the operations
material — is written up after the Nov 5 session.

(graph-neural-networks)=
### When the thing you are modelling is a network

A corridor is a line, and a convolution slides along it. A city is not a line. If
you want to forecast queue spillback across a signalised grid, or work out how
far an incident's impact reaches, or estimate speeds at intersections where you
have no detector, the object you are modelling is a graph: intersections joined
by streets, each intersection with its own number of connections and its own
geometry.

The obvious first attempt — flatten the network into a long vector and fit a
network to it — fails for a reason worth stating plainly. The parameter count
becomes a function of how many intersections you have, the model is tied to one
specific ordering of them, and it cannot be run on any other city, or even on the
same city after a detector is added. That is the problem a graph neural network
solves, and it solves it with a move you already use.

**The bridge: the cell transmission model is already a graph neural network.**

```text
CTM, at one cell
────────────────
y      = min{ S(n_up), R(n_here) }   ← one rule, per connection
n(t+1) = n + Σ in − Σ out            ← conservation, however many legs

GNN, at one node
────────────────
m(v→u) = ψ(h_v, h_u, e_vu)           ← one rule, per connection
h_u'   = φ(h_u, ⊕ over v of m)       ← ⊕ eats however many messages
```

Nobody asks how many parameters the CTM has *for a given network*. It has four —
free-flow speed, backward wave speed, capacity, jam density — whether it runs on
three cells or thirty thousand. The sending and receiving functions are one pair
of functions applied at every cell; the network decides only how many times you
call them and who talks to whom. A GNN is exactly that, with the per-connection
function **fitted** instead of **derived**.

That one word is the whole trade. The CTM transfers to any city because its rule
came out of a conservation law and is therefore correct everywhere; you
re-estimate four parameters and the topology comes from the network file. A GNN's
rule came out of data, so it transfers only as far as the data it saw. Everything
that follows is about how much of what it learned was physics and how much was
bookkeeping about particular sensors.

Work through the companion before the equation. Every network on the page is
generated in your browser, every number is computed live from it, and the
regenerate button is the argument: press it and the intersections, the degrees
and the size all change while the same rule keeps running.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion — A GNN on a road network: one shared rule, any number of intersections</span>
    <a href="../_static/companions/GNN_On_A_Road_Network_Companion.html" target="_blank" rel="noopener">Open full screen ↗</a>
  </div>
  <iframe src="../_static/companions/GNN_On_A_Road_Network_Companion.html"
          title="A GNN on a road network" loading="lazy"></iframe>
</div>

#### The rule, written once

```text
for every directed street segment v → u  (however many that is):
    m(v→u) = tanh( Wm · [ h_v ‖ h_u ‖ e(v→u) ] + bm )

then at each intersection u, collapse however many arrived:
    a(u)   = mean over v in N(u) of m(v→u)

and update:
    h_u'   = tanh( Wu · [ h_u ‖ a(u) ] + bu )
```

| Symbol | In transportation terms |
| --- | --- |
| `h_u` | the state vector carried for intersection u. On the first layer it is the measured quantity — speed, occupancy, queue; after that it is whatever the model has worked out about u and its surroundings. |
| `e(v→u)` | what this connection *is*: upstream or downstream, turn type, link length, lanes, whether one phase serves the movement. Not which street it is — what kind of street it is. |
| `m(v→u)` | the message: what v's condition means *for u specifically*, given the kind of connection between them. |
| `Wm, bm` | the message weights. One set, shared by every segment in the city. This is the model. |
| `N(u)` | u's neighbours. Its size is the node's degree — 1 to 5 in a real street network. Nothing in `Wm` or `Wu` knows or cares. |

**In words:** for each street touching this intersection, work out what the far
end's condition means for this end; average those meanings, whatever their
number; use the average to update what you believe about this intersection.

Notice what never appears. There is no rule for a four-leg intersection and a
different one for a five-leg. The per-connection function always takes exactly
two nodes and one connection, and the varying part of the city is absorbed by
*how many times you call it* — the same way conservation of flow at a node is one
equation summed over however many approaches, not a different equation per
geometry. Stack the layer L times and a one-hop rule becomes an L-hop model:
that, and nothing more mysterious, is how a local rule reproduces a jam that
crosses the whole network.

:::{admonition} Going deeper — the ceiling on what message passing can tell apart
:class: dropdown
Message passing sees a node only through the shape of its surroundings. If two
intersections have the same degree, and their neighbours have the same degrees,
and so on outward, they receive identical messages at every layer and no depth
separates them. This is exactly the discriminating power of one-dimensional
Weisfeiler–Leman colour refinement, and each layer is one round of it.

The practical consequence is that the fix is features, not depth: lanes, control
type, speed limit, distance to the nearest ramp, betweenness centrality. All of
those are computable in any city, so unlike a learned per-sensor embedding they
cost you nothing in transferability. See Xu et al., *How Powerful are Graph
Neural Networks?* (ICLR 2019), which also explains why a sum aggregator reaches
that ceiling while mean and max fall short of it — a gap the companion lets you
reproduce in a street network in about ten seconds.
:::

#### Three results worth carrying out of the companion

The companion's last tab is a real experiment, not an illustration: a GNN trained
in PyTorch on a queue-spillback rule, then tested on **networks it had never
seen, at sizes it had never seen**. The reproducers sit beside the page as
`gnn_roadnet.py` and `sweep.py`.

- **Depth buys reach, and you need as much as the horizon demands.** At a
  one-step horizon a single layer is within 1.6× of the best depth — one hop is
  all the problem needs. At a three-step horizon that same single layer is 2.4×
  worse, because the disturbance now starts outside what it can see. Substitute
  your own numbers: a disturbance travels about the backward wave speed times
  your forecast horizon, so the hops you need is that distance over your mean
  link length. Pick depth from the traffic, then check whether the architecture
  can actually reach that far.
- **The aggregator is a modelling choice, not a hyperparameter.** Same
  architecture, same depth, same data — swapping mean for max was worth 4.3×,
  a bigger gain than going from one layer to four. The ground-truth rule takes a
  max over downstream neighbours, because a queue backs up from the *worst* road
  you feed into, not the average one. Sum when the quantity is conserved, mean
  when it is an intensive state, max when a bottleneck governs, attention when
  the weighting is the thing you do not know.
- **Structure enters through the wiring, and it can be switched off by
  accident.** Give every intersection the identical input feature and a mean
  aggregator with no edge feature leaves the entire city holding one single
  distinct state at *every* depth — a mean of identical messages is the same
  number whether two streets meet or five. Turn the edge feature on and the city
  separates on the first layer. The asymmetry of the network is information, and
  a model can be built that throws it away.

#### Where it breaks

The failure that matters most for an agency is not accuracy, it is
transferability, and it is visible in one glance at a parameter count.

> **The litmus test: does the number of nodes appear in the parameter count?**

The GNNs in the companion have 1,121 / 2,193 / 3,265 / 4,337 parameters at one
through four layers, and none of those numbers contain N — which is why the same
trained weights ran on unseen networks of unseen size. Compare with what is
common in the traffic-forecasting literature: a two-layer shared-weight block is
about 257 parameters *for any city*, while a learned adjacency built from node
embeddings is 4,140 parameters at the 207 sensors of one well-known benchmark and
6,500 at the 325 of another, and a per-sensor embedding table is larger still.
The identity part is over sixteen times the shared part, and every one of those
numbers is a fact about one sensor in one city. Models built that way top the
single-city leaderboards and cannot be moved at all.

The rest of the list: neighbours that are not interchangeable while nothing in
the edge features says so; a degree distribution that shifts between cities while
the aggregator is a sum; two intersections that are structurally identical and
operationally nothing alike; and coupling that does not travel along the network
at all, which is what a detour, a special event or weather does.

| Fit card — message-passing graph neural network | |
| --- | --- |
| **Idea in one sentence** | Learn one rule for what a single connection means, apply it to every connection, collapse whatever arrives at each node, repeat — so the size and shape of the network live in the wiring rather than the weights. |
| **Why it works** | Pairwise messages have fixed arity, so one function covers three-leg and five-leg alike; a permutation-invariant reduction absorbs varying degree; L layers compose a one-hop rule into an L-hop model. |
| **Fits these tasks** | Link speed and travel-time forecasting, sensor imputation, incident impact extent, network state estimation, cascading-failure and resilience analysis. *Leverage: prediction, classification.* |
| **Needs this data** | A network with attributes describing *what things are* (lanes, control, capacity, turn geometry, distance), plus a time series of node or link states. Labels come free when the target is a future measured state. Critically: **more than one network**, if transfer is ever the goal. |
| **Breaks when** | N appears in the parameter count; edge features do not encode role; degree shifts under a sum aggregator; the horizon needs more hops than the depth provides; the real coupling is off-network. |
| **Keep the classical method when** | The network is small enough to fit per-location models — a dozen intersections on one corridor means a dozen models, and skip all of this. The dynamics you need are already a conservation law: the CTM is derived, correct everywhere, and takes four parameters rather than three thousand. Or a per-sensor historical average by time-of-day already meets the accuracy the decision needs, which on quiet days it very often does. |

:::{admonition} Before you trust this result
:class: important
**What is the baseline?** · **How was the data split, and why is that honest?** ·
**What does it do on the ugly cases?**

The baseline here is persistence — predict that nothing changes — plus the
comparison across depths, so that no depth takes credit for what one hop already
achieves. The split is by **network**, not by time: training and test are
different graphs of different sizes, because a random time split within one city
would let a model memorise locations and still score well, which is the exact
failure this is meant to detect. The ugly cases are the nodes whose bottleneck
lies further away than the model's depth — they dominate the long-horizon error
and more data does not touch them — plus dead ends, where an average over a
single message carries no smoothing, and the step where a bottleneck clears,
when a learned bias toward persistence is exactly wrong.

One caveat the companion states about itself: its ground truth is a rule we wrote
down, so a model with enough reach can nearly nail it. Real cross-city
forecasting gains are far smaller. Take the shape of these results, not their
magnitude.
:::

### Two things to carry out of this section

**Exercise — read a model's parameter count.** Take any network-scale traffic
forecasting paper or product sheet. Find the parameter count, or reconstruct it
from the architecture description. Does the number of sensors appear in it? Then
answer three questions in writing: could this be run on your network without
retraining; what is the baseline the paper compares against; and was the reported
split across time or across networks. Most published results answer the third
question in a way that makes the first one moot.

**On the job.** When a vendor offers a network-wide prediction, ask what a node
is in their model, and what happens when you add a detector. The answers tell you
whether you are buying a model of traffic or a model of their training city. Then
ask for the persistence baseline on your own data — if they have not computed it,
neither has anyone else, and the improvement they are quoting has no
denominator.
