# Module 1 Notes — Foundations and Representation Learning

*Sessions: Aug 27, Sept 3, Sept 10, 2026. This chapter builds the three things
the rest of the course stands on: a way of describing where AI actually enters a
transportation task, a neural network built from a model you already use, and
the representation idea that unifies almost everything after it.*

:::{admonition} How to read this chapter
:class: tip
Read section 1.1 **before** the first meeting — you will be choosing a project
on Aug 27 and this is the vocabulary that makes that choice possible. Sections
1.2 and 1.3 pair with the Sept 3 and Sept 10 meetings; skim before, read
properly after, run the labs in between.

The interactive companions embedded here are the same pages posted on Canvas.
They are not decoration: several of the results argued in this chapter are only
convincing if you move the sliders yourself.
:::

---

## 1.0 The problem this module solves

Transportation is being reshaped by AI on three fronts: how we **sense** the
system (cameras, lidar, radar, V2X, probe data), how we **operate** vehicles
(ADAS, lane keeping, driving automation), and how we **plan and manage**
networks (simulation, digital twins, signal control, demand prediction).

That is the optimistic framing, and it is broadly true. It is also exactly why a
critical engineering perspective matters. The AI-for-mobility literature
publishes impressive demonstrations alongside a large number of results that do
not replicate, do not deploy, or do not actually beat a well-tuned classical
baseline. A significant part of what you should get out of this course is the
ability to tell those apart — quickly, and in front of a vendor.

So this module has an unusual shape for an AI course. It starts not with a model
but with a *process*, because the first decision you will make in practice is
never "which architecture" — it is "which step of this workflow is safe to hand
over, and how would I prove the result was any good." Only then do we build a
neural network, and only then do we get to the representation idea.

---

## 1.1 What "AI" means here, and why the workflow is the unit of work

*Session: Aug 27.*

### Five families, and which job each is for

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

### The unit of work is the workflow, not the model

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

### What your graduate training already buys you

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

### Reading a capability claim

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

## 1.2 Neural networks, starting from the logit you already use

*Session: Sept 3.*

### The binary logit is a sigmoid

Most introductions to neural networks begin with a biological metaphor and a
picture of a neuron. We are going to skip that, because you already use the
object in question.

The binary logit model gives the probability of choosing alternative 1 as

$$P_1 = \frac{1}{1 + e^{-\mu(V_1 - V_2)}} = \sigma\big(\mu \Delta V\big)$$

That $\sigma$ is the logistic sigmoid, and it is exactly the activation function
at the heart of a neural unit. The dictionary between the two vocabularies is
short and exact:

| Discrete choice | Neural network |
|---|---|
| scale parameter $\mu$ | weight $w$ (and $\mu = 1/\tau$, an inverse temperature) |
| alternative-specific constant | bias $b$ |
| systematic utility difference $\Delta V$ | pre-activation $z = wx + b$ |
| log-odds | $z$ |
| logit probability | $\sigma(z)$ |

A single neural unit *is* a binary logit model whose utility function you did
not specify by hand. That is the entire difference, and it is the whole idea of
the course in one sentence: **a neural network is what you get when you stop
specifying the utility function and let the data learn it.** Everything after
this — depth, attention, embeddings — is elaboration on where the learned
function comes from.

### tanh, and why it is not simply better

The other classical activation is $\tanh$, which is the same function rescaled:
$\tanh(z) = 2\sigma(2z) - 1$ exactly. It shows up in transportation on its own
merits — the car-following response $a = a_{\max}\tanh(\Delta v / k)$ is a
bounded, sign-preserving, saturating response to a speed difference, which is
precisely what $\tanh$ is for.

The textbook claim is that $\tanh$ trains better because its derivative is
larger: $\tanh'$ peaks at 1.0 while $\sigma'$ peaks at only 0.25. That is true
*at the origin* and it is where the story usually stops. It is worth pushing
further, because the honest picture is the opposite away from zero. At
$|z| = 3$, $\sigma' = 0.0452$ but $\tanh' = 0.0099$ — **$\tanh$ saturates
harder.** Its advantage is local to the region near zero, which is where a
well-initialized network starts and not where a poorly-conditioned one ends up.

This is the real reason ReLU won, and it is a better lesson than the one about
derivative magnitudes: the property that matters is not how steep an activation
is at its best point, but how gracefully it behaves at its worst.

### Softmax is the multinomial logit

Extend to more than two alternatives and the sigmoid becomes the softmax — which
is, again, a model you already use. The multinomial logit *is* a softmax, and
for two alternatives they coincide exactly: $\text{softmax}([z_1, z_2])_1 =
\sigma(z_1 - z_2)$.

Three consequences follow, and all three bite in practice.

**Only differences are identified.** Softmax is shift-invariant: adding a
constant to every utility changes nothing. This is the same fact that forces you
to normalize alternative-specific constants in a choice model. It is also why
every numerical implementation subtracts the maximum before exponentiating —
$e^{800}$ overflows to infinity, and $\infty/\infty$ is `NaN`.

**Softmax saturates too.** Its Jacobian is $p_i(\delta_{ij} - p_j)$, which goes
to zero when any $p_i \to 1$. A confident softmax has no gradient. This is
exactly why attention divides by $\sqrt{d}$ in Module 2 — that scaling factor is
a temperature, and it exists to keep the softmax off its saturated shoulder.

**It always returns a distribution.** The outputs sum to one whether or not any
of the alternatives is correct. A vehicle classifier with no "none of the above"
class will confidently label a shopping cart as a bus, because it has been
constructed so that it must label it as *something*. When you evaluate a
perception vendor, this is the first thing to ask about.

### An aside worth the detour: exploration in signal control

The softmax has a second life as a *policy*, and the companion runs a small
reinforcement-learning simulation that makes a point worth carrying well beyond
this module.

Four signal phases have true clearance rates $[0.55,\, 0.95,\, 0.42,\, 0.60]$.
The controller starts with deliberately wrong estimates $[0.90,\, 0.30,\, 0.62,\,
0.80]$ — it believes the *best* phase is the worst. It then makes 800 decisions,
updating its estimates as it goes, choosing phases by softmax with temperature
$\tau$.

- **$\tau = 0.02$ (near-greedy).** Serves the best phase on **0 of 800**
  decisions. Settles on the second-best phase, clears 474 vehicles = **62% of
  the oracle**, and finishes still believing that phase 4 clears at 0.30 when it
  truly clears at 0.95. The wrong estimate is never once corrected.
- **$\tau = 0.15$ (balanced).** 83% of late decisions go to the best phase;
  clears 661 = **87%**.
- **$\tau = 1.5$ (near-random).** Clears 520 = **68%** — it *beats greedy*. Its
  value estimates all end up accurate; it simply acts on them too weakly.

The lesson: **acting decisively on a stale belief costs more than acting
indecisively on a good one.** And note what makes the greedy failure dangerous
in practice — it is invisible in the controller's own diagnostics. Its estimates
look converged, its chosen phase looks stable, and the phase it never tries
never generates evidence against it. Any adaptive system deployed in the field
with no exploration has this failure mode, whether or not anybody called it
reinforcement learning.

### IIA does not disappear because you called it a network

Softmax inherits independence of irrelevant alternatives, and the classic
red-bus/blue-bus problem survives the rebranding intact. With route travel times
of 18, 21, and 26 minutes and $\mu = 0.35$: adding a *duplicate* of route B
leaves the A:C odds ratio at 16.4446, **unchanged** — while B's combined share
jumps from 24.8% to 39.8% and A drops from 70.9% to 56.8%.

If you have ever explained to a client why the nested logit exists, you have
already explained a limitation of the softmax output layer. Knowing the failure
in one vocabulary means you know it in the other.

### Saturation, and the detector pegged at jam occupancy

A saturated unit is a loop detector reading 100% occupancy. The detector is
still working. It is still reporting. But it has stopped carrying information,
because every condition worse than jam produces the same reading, and you cannot
recover the difference between bad and much worse from a pegged sensor.

That is what saturation costs a network: not a wrong answer, but an *insensitive*
one. And because gradients propagate by multiplication through layers, a network
that is saturated in the middle stops learning in everything upstream of it.
Stack enough saturating layers and the gradient that reaches the first layer is
numerically zero — the vanishing gradient problem, which is the single most
important reason deep networks were impractical for as long as they were.

### The loss function is not a detail

Here is the result from the companion most likely to save you a week.

Start a one-neuron logistic regression from a confidently *wrong* initialization
($w = -7$, $b = 2.5$) on synthetic Greenshields congestion data, and train it
two ways. With cross-entropy loss it recovers to the 83.9% accuracy ceiling in
about **25 steps**. With squared error it sits at or below the 51.1% majority
baseline until roughly **10,000 steps** — a penalty of about **400×**.

Same model, same data, same optimizer, same initialization. Only the loss
differs. The mechanism is that squared error multiplies the gradient by
$\sigma'$, which is nearly zero exactly when the model is confidently wrong,
whereas cross-entropy cancels that factor and produces a gradient proportional
to the error itself.

The general lesson is bigger than this one pairing: when a model "won't train,"
the problem is frequently not the architecture and not the learning rate. It is
that some part of the setup has arranged for the gradient to be zero in the
region where you most need it not to be.

### Stacking layers: a basis that moves

Why stack layers at all? The usual answer — universal approximation — is not a
good one, because a fixed grid of Gaussian basis functions is universal too and
nobody calls that deep learning. The real answer is **parameter efficiency in
high dimensions**, and it can be counted.

You already choose basis functions. A mode-choice utility specification, a
triangular fundamental diagram, the IDM functional form, a regression spline,
HOG or SIFT features — these are all decisions about $\phi(x)$, made by hand,
before any fitting happens. The neural network's claim is that $\phi$ should
itself be learned.

Count the parameters. A fixed grid with $K$ knots per axis in $D$ dimensions
costs $K^D$ basis functions, each contributing one weight. A learned basis of
$M$ units costs $M(D + 2) + 1$, because a learnable unit needs $D$ input weights
plus a bias plus an output weight. Fixed is exponential in $D$; learned is
linear in $D$. With $K = 5$ and $M = 8$ they cross at **$D = 3$**. With
$K = 10$, at $D = 2$.

That inequality is the entire argument, and it tells you when the argument does
*not* apply.

### Two results that argue against reaching for a network

Both of these are in the companion, both are verified, and neither should be
explained away.

**In one dimension, learnable basis functions lose.** Same hinge family, matched
at 25 parameters: a fixed grid with $M = 24$ knots reaches RMSE **0.90**; free
knots with $M = 8$ (best of three restarts) reaches only **1.45**. On a single
axis you can simply tile the domain, so paying three parameters per knot to
learn where the knots go is a bad trade. For a speed-density curve, a corridor
travel-time function, or any other one-dimensional relationship, a spline is
better *and* you can plot it.

For contrast, the same corridor fit with a range of methods: a cubic polynomial
gets 8.46, an 8th-order polynomial 4.49, hand-picked engineering features 7.15,
a Gaussian grid with $M = 8$ gets 3.42, with $M = 24$ gets 0.87, with $M = 60$
gets 0.76. The fixed bases with enough knots win comfortably.

**Below a sample-size threshold the learned basis is worse than predicting the
mean.** At $D = 12$ there is a cliff between $N = 100$ and $N = 200$. Below it,
every run is at or worse than the mean baseline and the seeds scatter across
0.32–0.56. At $N = 200$, all three seeds hit ~0.006. There is no graceful
degradation and no partial credit — the method either has enough data or it
produces confident noise.

Now the other side, so the argument is fair. On a task where the target depends
on an unknown *direction* in the input space, an 8-unit learned network holds
test error at 0.0019 → 0.0059 as dimension goes from 2 to 32, and recovers the
true direction to $|\cos| = 1.0000$ at every $D$. The best fixed random-feature
basis degrades from 0.085 to 0.348 against a baseline of about 0.36 — at
$D = 32$ that is a **59×** error ratio. When the structure is a direction you do
not know in advance, and the dimension is high, nothing fixed competes.

**And a warning about the obvious shortcut.** Reduce first with PCA, then fit a
small network on the components — everybody's instinct. On a 10-detector problem
where the predictive direction happens to be the *smallest* singular value,
PCA-then-fit gives 0.370 / 0.384 / 0.408 / 0.418 for $k = 1, 3, 5, 9$ against a
0.361 baseline. Keeping 99.8% of the variance buys **nothing**. Only $k = 10$ —
i.e. throwing nothing away — recovers, at 0.006. Fitting jointly on the raw
inputs gets 0.012 directly. PCA is not bad at compression; it is bad at knowing
what is worth keeping, because it was never told what you are predicting.

### What it costs

Three costs, all of which you will meet in the labs.

**Identifiability is gone.** Permuting the hidden units changes the weight vector
by 1.565 and the output by $2.2 \times 10^{-16}$. Two networks with completely
different parameters are the same function. You cannot interpret a weight the
way you interpret a coefficient in a choice model, and any claim built on
"the network learned that feature $x_3$ matters because its weight is large" is
unsupported.

**There is a seed lottery.** Six seeds on the same corridor problem: mean
disagreement between fits of 0.13 mph, worst case 2.33 mph, RMSE ranging
1.47–1.55, and up to **3 of 8 hidden units dead** — knots pushed outside the
domain, contributing nothing. Report the spread across seeds, not your best run.

**Depth without nonlinearity is nothing.** Eight layers with identity
activations differ from a single equivalent linear layer by
$1.6 \times 10^{-14}$. The nonlinearity is not a detail bolted onto depth; it is
the only reason depth exists.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion — Sigmoid, tanh, and softmax from the logit</span>
    <a href="../_static/companions/Sigmoid_Tanh_Companion.html" target="_blank" rel="noopener">Open full screen ↗</a>
  </div>
  <iframe src="../_static/companions/Sigmoid_Tanh_Companion.html"
          title="Sigmoid, tanh, and softmax from the logit" loading="lazy"></iframe>
</div>

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion — Multilayer networks and learnable basis functions</span>
    <a href="../_static/companions/Multilayer_Networks_Companion.html" target="_blank" rel="noopener">Open full screen ↗</a>
  </div>
  <iframe src="../_static/companions/Multilayer_Networks_Companion.html"
          title="Multilayer networks and learnable basis functions" loading="lazy"></iframe>
</div>

(how-a-network-learns)=
### The parts, one at a time

The argument so far has been about what a network is *for*. This is what its
pieces do, because each has a distinct job and two of them are routinely
misread.

Take one detector station reporting density $k$ and a demand-to-capacity ratio
$v/c$, and ask for the probability that the segment is congested — say, mean
speed below 45 mph. That is one neuron: $z = w_1 x_1 + w_2 x_2 + b$, then
$\hat{y} = \sigma(z)$.

**The weights** set the tilt of the decision boundary and how fast the answer
changes as you move across it. The vector $(w_1, w_2)$ points straight uphill,
perpendicular to the boundary.

**The bias** slides that boundary without rotating it. It is the threshold —
*how loaded does this segment have to be before I call it congested* — and it is
the parameter people most often forget a model needs. Fitted on 400 intervals,
the neuron reaches 94.0% accuracy at a log-loss of 0.116. Freeze the bias at
zero, so the boundary is nailed to the origin, and the same two weights on the
same data give **71.8%** and **0.528**.

**The activation** does two jobs, and the second is the structural one. It turns
a score into a probability you can threshold, price, or hand downstream. It also
gives you a *gradient*: a hard step function is flat everywhere, every derivative
is zero, and no gradient method can tell you which way to move. That is why the
1958 perceptron needed a bespoke update rule and why it could not be stacked.

**A connection** is simply the fact that $x_i$ has a $w_i$ at all. A weight of
exactly zero is a missing wire, and in larger models the wiring pattern *is* the
architecture.

One caution follows directly from the identifiability problem above. This fit
lands at $(w_1, w_2) = (26.95,\ 8.47)$ with $b = -16.91$, which in engineering
units is $0.299\,k + 11.29\,(v/c) = 20.30$ — a recovered demand-to-density
trade-off of 37.7 against a true 33.3. That comparison is only meaningful
because both inputs were rescaled to $[0, 1]$ first. Feed a network raw density
in the hundreds alongside $v/c$ near 1.0 and the weight magnitudes tell you
about your units, not about your physics.

And one thing worth watching during the fit itself: accuracy reaches 94.0% by
about step 50 and then never moves, while the weights keep growing, from a
magnitude of about 7.4 to about 28. Gradient descent stopped changing the
*decision* long ago and is now only sharpening the *confidence*, because
log-loss always pays a little more for being more certain about points it
already gets right. "Accuracy has plateaued" and "the loss is still falling" are
different statements, which is why you watch both.

### When one boundary is not enough

Keep the detector and change the question. Instead of *is this segment congested
now*, ask *will flow break down in the next fifteen minutes*. Breakdown is not
monotone in density: below the critical range there is nothing to break down,
and above it the facility is already in queue discharge, so the event has come
and gone. The risk lives in a **band** of density, and only when demand is high
enough to push through it.

That single change — from a threshold to a band — is the entire argument for a
hidden layer, and it is worth seeing what it does to a single neuron. Fitted for
6,000 steps on 400 intervals, the neuron reaches **78.75%** accuracy. Always
answering "no breakdown" reaches **79.25%**. The neuron raises the alarm on
**4 intervals out of 400**. It is less accurate than a constant, it is
operationally useless, and if the only number on your slide is accuracy you will
know neither of those things. Only 20.75% of intervals contain a breakdown, and
on a rare-event problem accuracy measures the base rate rather than the model.
Balanced accuracy of **0.50** is the honest reading.

Three hidden units fix it, and you can set them by hand: one gate that fires
above the lower density edge, one that fires below the upper edge, one that
fires when demand is high, and an output layer that demands all three at once.
Hand-set, that network scores **0.780** balanced accuracy on held-out data.
Trained from a random start, the same architecture reaches **0.797**. The
weights are not magic; they are the answer written down. Training is what you do
when nobody told you the answer.

Two things about that comparison matter more than the accuracy figures. First,
the hand-built version's log-loss is **0.547** against the trained version's
**0.334** — the same decisions, much worse probabilities, because hand-set gates
are nearly hard and announce 0.99 where the honest answer is 0.7. If anything
downstream consumes the probability, those are not the same model. Second, the
trained three-unit network did **not** recover the three gates the data actually
came from. It finds one rising density edge near $k \approx 34$, one falling edge
near $k \approx 57$, and a third unit sitting saturated across the whole domain
as an offset, with demand entering as a mild tilt shared by all three. It reaches
the same answer by a different decomposition — the identifiability problem from
the previous section showing up as a concrete disappointment. Hidden units are
not guaranteed to be the factors you had in mind, and reading meaning into an
individual unit is a claim that needs evidence.

### How the parameters actually move

Backpropagation is not a learning algorithm. It is a **derivative calculator**.
Gradient descent does the learning; backprop only tells it which way is
downhill, for every parameter at once.

Here is the problem it solves. Take a small network — two inputs, two hidden
units, one output, nine tunable numbers. A detector interval arrives, the network
produces a probability, the probability is wrong by some amount, and now somebody
has to answer nine separate questions: should *this particular number* go up or
down, and by how much?

You could answer all nine with no theory at all. Nudge a weight up by $\epsilon$
and run the network; nudge it down by $\epsilon$ and run it again; divide. Two
forward passes per parameter. For nine parameters that is eighteen passes, which
is merely annoying. For a model with seven billion parameters it is fourteen
billion passes *per training example*, which is why nobody did deep learning that
way. Backprop gets all of them for roughly the cost of one extra pass, because
the same intermediate quantities keep reappearing. Three consequences are worth
carrying away.

**The output error term is embarrassingly simple.** Work through
$\partial L / \partial z^{(2)}$ for cross-entropy loss composed with a sigmoid
output and you get exactly $\hat{y} - t$. The $\sigma'$ factor from the
activation and the $1/\hat{y}$ factor from the logarithm cancel perfectly. That
cancellation is not luck — it is *why* cross-entropy is the loss you pair with a
sigmoid, and it is the same conclusion the loss-function section above reached
from the other direction. Swap in squared error and the $\sigma'$ survives, so a
confidently wrong prediction, the case that most needs a large correction,
generates almost no gradient at all.

**The backward pass reuses the forward pass's own wires.** To send blame from the
output back to hidden unit $j$, backprop multiplies by $v_j$ — the very same
weight the forward pass used to send *information* the other way — and then
throttles it by that unit's own slope $\sigma'(z_j)$. Every gradient turns out to
be a product of local quantities: the blame arriving at a destination, times the
signal that flowed along the wire. Nothing in that expression knows about the
rest of the network. That locality is what makes automatic differentiation
possible, and it is why the backward pass costs about what the forward pass costs
however many parameters there are.

**Saturation is where this breaks, and you can watch it break.** Push the hidden
units into a regime where $\sigma'(z) = 6.4 \times 10^{-5}$ and nothing appears
wrong: the forward pass runs, the prediction is sensible, the loss is small. But
the largest gradient reaching the first layer is **0.14%** of the largest
gradient at the output layer. The output layer keeps learning and the first layer
is frozen. That is the vanishing gradient, in a network with *one* hidden layer —
stack forty and the multiplication happens forty times.

Finally: the arithmetic is checkable, and you should check it once. On the
companion's worked example the nine analytic gradients agree with central finite
differences to $1.05 \times 10^{-11}$. Do that by hand in the lab and then never
again — `loss.backward()` is doing exactly what you stepped through, in the same
order, for a few million more wires.

### Where training goes wrong, measured

The same breakdown problem, 400 training intervals and 400 held-out ones, full
batch gradient descent. Three failures are visible from the loss curves alone.

**Training for too long.** With sensible settings the held-out log-loss bottoms
out at **0.318 around step 350** and then climbs steadily to **0.348** by step
6,000, while the training loss falls politely the whole way, 0.272 → 0.255.
Nothing announces this. The training curve on its own says the run is going well
right to the end. Roughly 94% of that run was spent making the model worse at
the only job it has. That is what early stopping means, and it is why a held-out
set is not a formality you add before publication.

**Initializing at zero.** Every hidden unit receives an identical gradient, so
every hidden unit takes an identical step, so they stay identical forever. After
6,000 steps the maximum difference between any two hidden units is exactly $0$,
not approximately zero. The only thing left to learn is the output bias, which
converges to $\sigma(b) = 0.2075$ — the base rate, to four decimals. A
twenty-five-parameter neural network reduced to an expensive way of computing
the fraction of intervals containing a breakdown. Random initialization is not a
heuristic; it is what breaks the symmetry.

**The learning rate.** At $\eta = 0.02$ the training loss reaches only 0.338 in
6,000 steps, still crawling toward a solution it would eventually find. At
$\eta = 2$ it reaches 0.255. At $\eta = 8$ it reaches 0.659 with balanced
accuracy back at 0.50, having overshot the valley and settled for predicting the
base rate. The edge between those is not a gentle slope: $\eta = 5$ gives 0.261,
$\eta = 6$ gives 0.284, $\eta = 7$ gives 0.332, and $\eta = 8$ collapses — two
learning rates 15% apart, two completely different runs.

Push the rate further and something worth knowing happens: the *number* stops
being reproducible. Above roughly $\eta = 15$, the same code on two machines
lands in different places, because once the steps are large enough to bounce out
of the valley, a difference in the last bit of a floating-point $\tanh$ grows
over 6,000 steps into an entirely different trajectory. If you have ever had a
training run that would not reproduce across two machines and blamed the
framework, this is usually the reason — and it is a signal that the learning rate
is outside the regime in which any of your results mean anything.

### The same machinery, a different question

Everything above predicted a probability. Most transportation problems do not:
you want an acceleration, a travel time, a queue length. Take a car-following
problem — a follower at 20 m/s, given the gap and the closing speed, predict the
acceleration, with data from an IDM-style rule plus 0.25 m/s² of sensor and
driver noise.

**Exactly two things change.** The output activation becomes the identity instead
of a sigmoid, and the loss becomes squared error instead of cross-entropy. The
output error term is still $\hat{y} - t$ — the same cancellation for a second
reason, since squared error paired with a linear output has $\sigma' = 1$. The
backward pass, the update rule, and every hidden layer are untouched. Loss and
output activation are chosen *as a pair*, and when you choose them well the rest
of the machinery does not notice which problem it is solving.

The baselines are the point. Predicting the average acceleration for every
situation gives a held-out RMSE of **2.33 m/s²**. Fitting a plane — linear
regression on gap and closing speed — gives **1.30**. A six-unit network with 25
parameters gives **0.29**, against a measurement-noise floor of **0.250**.
Report the third number alone and it means nothing. Report all four and a reader
can see two things at once: the nonlinearity was necessary, and there is almost
nothing left to win. The reason the plane fails is physical rather than
statistical — acceleration is flat and mildly positive across most of the gap
range and then falls off a cliff as the gap closes with positive $\Delta v$,
because the IDM desired-gap term enters as $(s^{*}/s)^2$. A plane has to average
that cliff against the flat region and gets both wrong. The freedom to be flat
in one region and steep in another is exactly what a hidden layer buys.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion — What a neural network is, and how it learns</span>
    <a href="../_static/companions/Neural_Networks_and_Backprop_Companion.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/Neural_Networks_and_Backprop_Companion.html"
          title="What a neural network is, and how it learns" loading="lazy"></iframe>
</div>

:::{admonition} Before you trust this result
:class: important
**What is the baseline?** For anything in this section, the baseline is a fixed
basis expansion — a spline, a polynomial, a tuned classical model — fit properly
on the same data. If nobody ran it, the comparison has not been made. On a
rare-event problem, add the constant: always answering "no" scores 79.25% on the
breakdown task, and accuracy alone cannot tell a model apart from that.

**How was the data split, and why is that honest?** With low-dimensional traffic
data, a random split usually leaks: adjacent five-minute intervals from the same
corridor on the same day are not independent observations.

**What does it do on the ugly cases?** Report the spread across random seeds and
the number of dead units, not the best of three restarts.
:::

(convolution-kernels)=
### Convolution: the same neuron, wired to reuse its weights

Everything above took a short vector as input — a density, a $v/c$ ratio, a gap,
a speed. A single 1920 × 1080 camera frame is **6,220,800** numbers. Wiring one
neuron to all of them, the way every layer so far has been wired, would cost
6.2 million weights for one unit, and the unit would have to learn "bumper at
this pixel" separately from "bumper at the pixel next to it."

You already avoid that problem once a week without calling it anything. A
five-minute moving average of detector speeds is the weight vector
$[0.2, 0.2, 0.2, 0.2, 0.2]$ slid along a time series: five numbers, reused at
every time step. That is a convolution. In two dimensions the same move is a
small template slid over every position of a grid:

$$
y[i,j] \;=\; \sum_{a=-1}^{1}\ \sum_{b=-1}^{1}\ k[a,b]\ \cdot\ x[i+a,\,j+b]
$$

where $x$ is the image as brightness, $k$ is the **kernel** — nine numbers, also
called the filter or the template — and $y[i,j]$ is one output pixel: what the
template found at that position. The output is a **feature map**, and it is the
same size as the input less a border, because the window needs a neighbour on
every side. (Strictly this is cross-correlation rather than the flipped
convolution of a signals course. Deep learning calls it convolution, and the
sign convention makes no difference to a template that gets learned.)

What the nine numbers say is what the template wants: positive weights mean "I
want brightness here," negative weights mean "and darkness there." A negative
left column against a positive right column computes *light on the right minus
light on the left*, which is zero on a flat wall and large on a sign pole, a
mast arm or the side of a truck. Rotate it and you get the horizontal-edge
detector that finds bumpers, the stop bar and the shadow line under a vehicle.
Put a single 1 off centre and the template does not detect anything at all — it
**moves** the image by one pixel, exactly, with maximum difference $0.0$ against
a plain array shift. Hold onto that one: a translation in a time–space diagram
is what Newell's car-following model does, and Module 7 takes it up again.

**Why this wiring instead of a dense layer.** On a 384 × 241 frame — the size
used in the companion below — a 3 × 3 kernel is **9** weights covering
**91,298** output positions. A dense layer producing the same output would need
**8,449,082,112** weights, a factor of roughly **939 million**. The second half
of the argument matters more in the field: shift the frame by one pixel, the way
a camera on a mast arm does in wind, and **61.8%** of the flattened pixel vector
changes. The dense layer sees a different input. The feature map just slides —
correlation **1.000000** after realigning by that same pixel. The kernel does not
care where the bumper is, which is why it needs one copy of the bumper template
instead of one per location.

**A layer is a bank of these, and then depth.** Apply four kernels to the same
frame in parallel and the image is replaced by a stack of four answers, for
$4 \times 9 = 36$ weights. ReLU then keeps one polarity of each answer — on a
daylight frame it zeroes about **45%** of the vertical-edge map and about **52%**
of the horizontal-edge map, but **0.0%** of a blurring kernel's output, which has
no negative side to throw away and is a hint that blurring is not detection.
Pooling halves the grid. A second-layer filter then sees the *stack*, not the
pixels, and its weights say which combination to look for: one that averages the
vertical and horizontal channels together fires where both edge types coincide,
which is what a bumper, a licence plate, a sign face and a wheel arch all have.
One value after that second layer depends on an **8 × 8** patch of the original
frame. Stack it a dozen more times and the receptive field covers a whole
vehicle, and the thing being detected is a vehicle. That is the entire
architecture; everything else is bookkeeping.

**What a trained network actually put in those nine numbers.** The first layer of
a trained ResNet-18 holds 64 filters of 7 × 7 × 3, **9,408** weights. Split each
one into the part all three colour channels agree on — a pure shape detector,
which is what a hand-typed kernel is — and the part they disagree on, **41 of the
56 live filters** are shape-dominant. Gradient descent, given nothing but
photographs and a loss, arrived at oriented edge detectors. The other **15** are
colour-opponent detectors that fire on a colour boundary where brightness is
flat: useful for photographs of objects, and not obviously what a night-time
roadside camera needs.

The remaining **8 of the 64 are dead**. Their largest weight is $5.7 \times
10^{-6}$ or less, against a median largest weight of **0.432** across the live
ones — five orders of magnitude down. They are not weak detectors; they output
zero on every input. **12.5%** of the first layer of one of the most-downloaded
checkpoints in computer vision does nothing at all, and no accuracy number
reports it. This is the dead-unit failure mode from the training section above,
shipped.

**Where the wiring stops being the right answer.** The whole construction assumes
the pattern is *local* and means the same thing everywhere. A shockwave can start
anywhere on a corridor, so a kernel fits. A bottleneck at a fixed milepost is a
property of that location, and a translation-invariant filter is built to ignore
precisely that — ask "would this pattern mean the same thing fifty pixels to the
left?" before reaching for a convolution. And a kernel measures contrast, not
importance: on equal-sized crops the vertical-edge kernel's mean response is
**45.85** on a night frame against **18.56** on a daylight one, 2.5 times larger,
because headlights and their wet reflections are enormous edges. The pedestrian
is the low-contrast shape between them.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion — Convolution kernels: how a network learns to see shape</span>
    <a href="../_static/companions/Convolution_Kernels_Companion.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/Convolution_Kernels_Companion.html"
          title="Convolution kernels: how a network learns to see shape" loading="lazy"></iframe>
</div>

Type the nine numbers yourself on the first tab, click any output pixel to see
the nine multiplications behind it, then stack the kernels into a layer and
finally page through the 64 real filters — the dead ones included — on the third.

(scooter-kid-case)=
### A worked case: a child on a scooter, seen by a stock detector

Everything above is machinery. Here is thirteen seconds of it doing a real job,
on footage from this course rather than from a benchmark.

The clip is the forward camera of a Tesla driving under FSD on a residential
street in Florida — 1928 × 1208 pixels, 20 frames per second, **263 frames**,
recorded by the instructor. A child on a kick scooter comes toward the car. The
detector is `fasterrcnn_resnet50_fpn` with COCO weights, exactly as it downloads:
a ResNet-50 backbone of the kind you just took apart, a feature pyramid, a
region-proposal stage, and a head that picks one of **80** object classes. No
fine-tuning, no transportation data, no dashcam data, nothing about children. It
is the honest version of what an agency or a consultant reaches for first,
because it is free and it is five lines of code.

**What it got right, which is most of it.** It found the child at a box height of
36 pixels — roughly 74 m out — and held her for **111 consecutive frames with
zero gaps**, until she left the frame at a box height of 277 pixels. Its
confidence went from 0.65 at first sight past 0.90 within **3** frames. It found
both pedestrians standing on the shoulder. All **84** of its `fire hydrant`
detections are real hydrants. Judged as an object detector on video it had never
seen, this is a good result, and you should expect a good result: this is the
task the model was built for.

**What it did not give you is the whole lesson.** Three failures, none of them
bugs, all of them consequences of a vocabulary chosen years ago by people
solving a different problem.

The first is that **the word "child" does not exist in this model.** The output
is `person`, at a confidence of **1.00**. A five-year-old and a construction
flagger are the same output. Every property that would change a driving decision
— small, unpredictable, cannot be expected to yield, may accelerate into the lane
without looking — is invisible, and has to be supplied by whoever uses the model.
Notice that the score is no help here. A confident, correct, decision-irrelevant
label is more dangerous than an uncertain one, because it passes every threshold
check you would think to write.

The second is that **the scooter came out a skateboard**, in 17 detections up to
**0.93**, with the box correctly placed on the scooter. COCO's nearest words are
`skateboard`, `bicycle` and `motorcycle`; there is no `scooter`. The model is not
confused — it is answering the only question it was ever asked, which is which of
its 80 words fits best. And this near-miss turns out to be the *only* signal in
the model's output that separates the rider from an ordinary pedestrian, which is
a thin thread: the two shoulder pedestrians grow *larger* in the frame than the
child does, because the car drives past them, so "take the biggest track" picks
the wrong person.

The third matters most for agency work. A red-circle regulatory sign at the end
of the clip is reported as `stop sign` **35** times, peaking at **0.97**. There
is no stop sign anywhere in this clip. `stop sign` is COCO's only sign class —
no speed limit, no yield, no warning — so anything red and sign-shaped receives
the one available word, confidently. Run this pipeline over a fleet's video to
build a sign inventory and you have recorded a stop sign at a location that has
none, at 0.97, with no flag of any kind. The failure is silent, it is systematic
rather than random, and no accuracy number computed on COCO would surface it.

**And it gives you no distance.** A detector outputs a box and a word. Range,
closing speed and lane position — the three quantities a braking decision
actually needs — are not in the output. They can be *inferred* from the box, and
the companion does so, but only through

$$
Z \;=\; f \cdot H / h_{\text{px}}
$$

where $h_{\text{px}}$ is the measured box height, $f$ is the focal length in
pixels and $H$ is the object's true height. Neither $f$ nor $H$ is measured here,
so both are stated assumptions — a 50° field of view and a 1.30 m child — and
every distance scales linearly with the assumed height. Worse, the error is
worst where you need it most: at the far end **one pixel of box height is 2.05 m
of range**, and at the near end 0.035 m. That single fact is the whole argument
for radar, lidar or a stereo pair, and the reason a camera-only stack has to
learn a size prior for every class it cares about.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion — A child on a scooter, seen by a stock CNN detector</span>
    <a href="../_static/companions/Scooter_Kid_CNN_Case.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/Scooter_Kid_CNN_Case.html"
          title="A child on a scooter, seen by a stock CNN detector" loading="lazy"></iframe>
</div>

Step through the clip on the first tab and move the score threshold while you
watch — every detection above 0.05 was stored, so the slider filters results
rather than re-running anything. The second tab opens the backbone on one frame
of this footage: the same five stages, with the receptive field growing from 7
pixels to **267** and the share of values ReLU sets to zero rising from
**12.8%** to **78.4%**. In the first two rows you can still see the child; by
layer 2 the picture is gone and what remains is a handful of lit cells in
roughly the right place. Nothing in the network ever sees a child. Losing the
picture is the point — a representation that kept every pixel would have learned
nothing.

One last thing, because it is a habit worth forming. The camera is bolted to the
car, so the whole background slides sideways when the car turns, and phase
correlation between consecutive frames recovers that motion. After subtracting a
0.75 s moving average to remove the road's own curvature, the clip contains
exactly one real steering excursion — **3.82 °/s at frame 146**, while the child
was about 32 m ahead. The instructor's own account of driving it is that the car
"shook its direction laterally a little bit" as it passed her, and the
measurement is consistent with that account. It does not *prove* it. Image motion
cannot separate a steering command from a road crown, a pothole, a gust, or a
hand on the wheel, and the log that could settle it belongs to the manufacturer.
Keeping those two things apart — what you measured, and what you were told — is
most of what makes an analysis worth reading.

The detection machinery itself — proposals, non-maximum suppression, the
precision/recall trade-off, multi-camera tracking — is the Sept 10 session. This
case is here because it is the first place the convolution you just built stops
being an idea.

:::{admonition} Before you trust this result
:class: important
**What is the baseline?** For "did anything move" on a fixed camera, the baseline
is frame differencing against a median background: no training, no GPU, no
labels. For counting and speed at a point, it is the loop or radar detector you
already have, which needs a calibration rather than a training set. A CNN earns
its keep when the question needs the *appearance* of the object, not its
presence.

**How was the data split, and why is that honest?** Frames from one clip are not
independent observations — consecutive frames five per second apart are nearly
the same picture. Split by clip, by site and by lighting condition, and say which
sites the model never saw. Two of the four frames in the companion are not US
roads, and the page says so rather than letting them stand as evidence.

**What does it do on the ugly cases?** Report the response on night, rain and
glare separately, not pooled. Count the dead filters. And check that a large
response means the right thing — the night frame above scores higher on edge
energy than the daylight one, and it is the harder scene.
:::

---

## 1.3 Representation learning and embeddings

*Session: Sept 10.*

### One-hot, and its three failures

A neural network is a function from vectors of numbers to vectors of numbers. It
cannot ingest the string `"stop sign"` or a JPEG. Everything becomes numbers
first, and the question is *which* numbers.

The obvious answer is the one-hot vector: with a 50,000-word vocabulary, every
word is a vector of length 50,000 with a single 1. It works, and it fails three
ways.

1. **High-dimensional and sparse.** Wasteful to store and to compute with.
2. **No notion of similarity.** `"car"` and `"vehicle"` are exactly as different
   as `"car"` and `"banana"` — every pair is orthogonal. The geometry carries no
   information at all.
3. **No generalization.** A model trained on `"truck"` learns nothing
   transferable about `"semi-truck"`.

The same three failures apply to any categorical encoding you have used, and to
raw pixels for images, where a small change in lighting moves the vector
enormously without changing what the image means.

You have already worked around this. Road functional class is a categorical
variable that you would never leave one-hot in a model you cared about — you
would engineer features that capture what makes an arterial arterial. An
embedding is that instinct, automated and learned.

### An embedding is a geometry

An **embedding** is a fixed-length dense vector — typically a few hundred to a
few thousand dimensions — representing a word, a sentence, an image, a road
segment, a trajectory. The point of it is that the *geometry* of the space
encodes meaning:

- Things that mean similar things sit close together.
- Things that mean different things sit far apart.
- Directions in the space often correspond to interpretable axes of variation.

Nobody hand-engineers these vectors. They are learned by training a model on a
pretext task — predict the next word, predict a missing patch, match a caption
to an image — and then keeping the internal representation and throwing the
pretext task away.

This is the same conceptual move you make when you reduce a full traffic state
to a small vector of macroscopic descriptors. You accept a lossy summary because
the summary is the part that generalizes. The difference is that you chose the
descriptors and the network learns them.

### Word2Vec, and the same algorithm on a road network

The classic example is **Word2Vec** (Mikolov et al., 2013), and the idea is a
single sentence from linguistics:

> *"You shall know a word by the company it keeps."* — J. R. Firth, 1957

Word2Vec trains a shallow network to predict a word from its surrounding context
over billions of sentences. It never sees a dictionary or a part-of-speech tag.
Yet the resulting vectors satisfy relations like
$\text{vec}(\text{king}) - \text{vec}(\text{man}) + \text{vec}(\text{woman})
\approx \text{vec}(\text{queen})$, synonyms cluster, and antonyms sit on opposite
sides of meaningful axes. Rich structure, extracted from raw co-occurrence
statistics, with no labels.

Now the part that matters here: **the algorithm does not know its inputs were
words.** Replace "sentences of words" with "random walks across a road network"
and the same machinery produces **road-segment embeddings** that recover
functional classification — arterial, local, highway — without ever being told
the labels. Context in a corridor plays the role that context in a sentence
played. That is Lab 2, and it is the cheapest possible demonstration that the
representation idea transfers out of natural language.

### Image embeddings and transfer learning

The image story ran in parallel. A deep CNN trained on a large labeled dataset
learns a hierarchy: early layers respond to edges, color blobs, and oriented
textures; middle layers compose those into parts — wheels, faces, vehicle
silhouettes; late layers respond to whole-object concepts.

Take a pretrained network like **ResNet-50**, cut off the classification head,
and what remains is an *image encoder*: a function from a raw image to a
2048-dimensional vector. Those vectors have the same property as word
embeddings — semantically similar images land close together, even when the
network was trained on a completely different label set.

This is **transfer learning** in its simplest useful form, and it is the single
most practically important idea in this module for agency work: you are reusing
a representation you did not pay to train. The relevant follow-on questions are
whether to freeze the encoder and train only a head, or to fine-tune the whole
thing — and how far your imagery has drifted from what the encoder was trained
on. Florida roadside imagery at dusk in the rain is not ImageNet, and domain
shift is the reason a model that demoed well fails in deployment.

### Contrastive learning: supervision without labels

Contrastive learning trains on *similarity* rather than on labels: pull
representations of things that belong together closer, push everything else
apart. You need pairs that should match, not a labeled category for every
example.

In transportation this matters more than it does almost anywhere else, because
labels are the scarce resource. Nobody has a labeled dataset of every hazard
type on Florida's arterials. But you often have pairs that should match for
free — the same location photographed twice, two cameras seeing one incident, a
crash record and its narrative, a trajectory and the segment it traversed.
Contrastive learning is how those free pairs become a representation.

### CLIP: images and language in one space

The striking recent development is that images and text can be embedded into the
*same* space. **CLIP** is trained on image–caption pairs contrastively, so the
vector for a photo of a stop sign lands near the vector for the phrase
"a red octagonal traffic sign."

The consequence is **zero-shot, open-vocabulary recognition**. You do not train a
classifier for "flooded roadway"; you write the phrase and rank images by
similarity to it. For long-tail mobility safety scenarios — the situations that
matter most and appear in no label set — this is a genuine change in what is
possible, and it is the technical substrate under a great many of the "AI dash
camera" products on the market.

It is also where prompt sensitivity, and a fresh set of failure modes, enter the
picture. Lab 4 makes you find them yourself, which is the only way that lesson
lands.

### What is worth embedding in mobility

Almost every modern deep learning system in transportation decomposes the same
way:

1. **Encoder** — raw input (image, video frame, trajectory, segment, text) → embedding.
2. **Backbone** — work in embedding space (attention, graph network, MLP).
3. **Head** — embedding → output (a class, a number, a sentence).

Most of the engineering decisions you will make are about choosing, freezing, or
fine-tuning encoders. Which means the first design question in a mobility AI
project is usually: *what is the unit being embedded?* A road segment. A
trajectory. An OD pair. A whole scene. A five-minute traffic state. An incident
record. Choosing that unit wrong is more damaging than choosing the architecture
wrong, and it is a transportation decision, not a machine learning one.

### How to know a representation is any good

An embedding space is easy to produce and easy to over-trust. Before you build
anything on top of one, check it:

- **Does the neighborhood structure make sense?** Pick a handful of items you
  know well and look at their nearest neighbors. If two stop signs from
  different angles are not neighbors, stop.
- **Does a simple probe recover something you did not train on?** If a linear
  classifier on frozen embeddings can recover functional class, the information
  is genuinely in there.
- **Does the low-dimensional plot mislead you?** t-SNE and UMAP will produce
  attractive clusters from noise. Treat those pictures as hypotheses.
- **Does it transfer?** The real test is whether the representation helps on a
  task it was not trained for.

We come back to this with real measurements later in the course, on a
representation trained on traffic states rather than images.

:::{admonition} Before you trust this result
:class: important
**What is the baseline?** For an embedding, the baseline is the hand-engineered
feature set you would have built anyway. Learned representations frequently win;
they should still have to.

**How was the data split, and why is that honest?** If the encoder was pretrained
on data that overlaps your test set, your evaluation is contaminated and the
number is meaningless.

**What does it do on the ugly cases?** Night, rain, glare, occlusion,
construction, and the classes that appear twice in the whole dataset. Aggregate
accuracy hides exactly the cases that matter in safety work.
:::

---

## Labs

Four notebooks accompany this module. All run in Google Colab and use open data.
What matters is not that they run — it is what each one proves.

- **{doc}`lab1` — Python and ML warmup.** Loads a synthetic traffic-flow
  dataset, plots the Greenshields fundamental diagram, and fits a simple model.
  *Proves:* your environment works, and the supervised-learning pipeline
  (data → model → loss → optimization → evaluation) is a thing you can execute
  end to end.
- **{doc}`lab2_word_embeddings` — From Word2Vec to Road2Vec.** Write skip-gram
  with negative sampling from scratch, train it on a small corpus and see the
  analogy structure appear, then hand the *same trainer* random walks on the real
  road network around USF Tampa. *Proves:* representation learning is not about
  language — functional class does fall out of context statistics without ever
  being labeled. *And then:* the same lab shows that plain latitude and longitude
  recover it just as well, because a uniform random walk mostly encodes where a
  place is, not what it does. Evaluating a representation against a free baseline
  is the habit the lab is really teaching.
- **{doc}`lab3_image_embeddings` — Image embeddings with a deep CNN.** Load a
  pretrained ResNet-50, visualize what each layer responds to, extract
  2048-dimensional embeddings, and check that semantically similar images
  cluster. *Proves:* transfer learning in its simplest useful form, and gives
  you a feel for what "the representation is already in there" means.
- **{doc}`lab4_clip_vs_traditional_cv` — CLIP versus traditional computer
  vision.** Compare a closed-set classifier with a CLIP-style model on roadway
  and dashcam-style scenes; run zero-shot recognition against open-vocabulary
  prompts; probe the failure cases. *Proves:* why open-vocabulary perception
  matters for long-tail safety scenarios — and how brittle prompt phrasing can
  be.

Lab 4 physically lives in this module and is referenced again in Module 2 as the
bridge into multimodal models.

---

## Using this on the job

**When someone pitches you an AI system,** ask for the workflow diagram before
the architecture diagram. Which step is being automated, what is the checkpoint,
and what is the current process's baseline number. A vendor who cannot produce
those three things has not deployed the system anywhere that measured it.

**Before you fund a pilot,** apply the check from 1.1: is the output cheaper to
verify than to produce? If verifying requires a human to redo the work, the
pilot will show a time saving that evaporates at scale.

**When you have low-dimensional tabular data,** the answer is often not a
network. The one-dimensional result in 1.2 is not an edge case; speed-density
curves, travel-time functions, and delay relationships are exactly the shape
where a spline wins and can be plotted for a review board.

**When you have imagery,** start from a pretrained encoder. Almost nobody in an
agency setting should be training a vision model from scratch, and the questions
that actually determine success are about domain shift and label quality, not
architecture.

**When you evaluate a perception product,** ask what happens to inputs outside
its label set. A softmax with no "none of the above" class always returns a
confident answer.

**When you report results,** report the spread across seeds and the performance
on the ugly subset. This is the difference between an engineering report and a
marketing claim, and it is noticed.

---

## Critical reading

- LeCun, Y., Bengio, Y., & Hinton, G. (2015). Deep learning. *Nature, 521*,
  436–444. — *The canonical overview. Read for the framing; note how little of
  it is about evaluation.*
- Bishop, C. M., & Bishop, H. (2024). *Deep Learning: Foundations and Concepts*,
  Ch. 6. — *The learned-versus-fixed basis argument in 1.2, done properly.*
- Rumelhart, D. E., Hinton, G. E., & Williams, R. J. (1986). Learning
  representations by back-propagating errors. *Nature, 323*, 533–536.
- Mikolov, T., Chen, K., Corrado, G., & Dean, J. (2013). Efficient estimation of
  word representations in vector space. *arXiv:1301.3781*.
- He, K., Zhang, X., Ren, S., & Sun, J. (2016). Deep residual learning for image
  recognition. *CVPR*. — *ResNet, the encoder in Lab 3.*
- Radford, A. et al. (2021). Learning transferable visual models from natural
  language supervision (CLIP). *ICML*. — *Read the zero-shot results, then read
  the limitations section, which is unusually candid.*
- Veres, M., & Moussa, M. (2020). Deep learning for intelligent transportation
  systems: A survey of emerging trends. *IEEE T-ITS, 21*(8), 3152–3168.
- Karlaftis, M. G., & Vlahogianni, E. I. (2011). Statistical methods versus
  neural networks in transportation research. *Transportation Research Part C,
  19*(3), 387–399. — *Fifteen years old and still the most useful thing on this
  list for deciding whether you need a network at all.*

---

## Exercises

1. **Workflow audit.** Take a process you have actually worked on. Write it as
   trigger → ingest → transform → act → checkpoint → record. Label every step
   with one of the six leverage labels, mark the steps where AI must not act
   alone, and place the checkpoint immediately before the first irreversible
   action. State the three baseline numbers for the current process: how long,
   how often wrong, how much.
2. **The dictionary.** Take a binary logit model from a paper or a project you
   know. Write out its scale parameter, its constants, and its utility
   difference in neural network vocabulary. Then say what would have to change
   for it to become a two-layer network, and whether that change would help.
3. **Find the crossover.** For a prediction problem you care about, count $D$.
   Work out $K^D$ against $M(D+2)+1$ for a defensible $K$ and $M$. Which side of
   the crossover are you on, and does that match what you were planning to do?
4. **Break the softmax.** Construct a route-choice example where adding a
   near-duplicate alternative produces a share prediction you would not defend
   to a client. Then say what you would do about it.
5. **Sanity-check an embedding.** After Lab 2, pick five road segments whose
   character you know. Look at their nearest neighbors in the learned space.
   Write down one thing the embedding clearly got right and one thing it got
   wrong, and propose a check that would have caught the second one before you
   trusted the space.

---

## Where this goes next

Module 2 takes embeddings as given and asks what happens when the model can
decide, for each element, which other elements to look at. That is attention,
and the transformers built from it are the reason the last few years happened.
The through-line is direct: a transformer is a machine that reads in embeddings,
transforms them, and writes out embeddings — which is why this module had to
come first.
