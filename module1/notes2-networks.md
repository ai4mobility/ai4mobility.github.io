# 1.2 Neural networks, starting from the logit you already use

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 1 &middot; Section 1.2 &mdash; part 1 of 3</span>
    <span class="notes-card-session">Session: Sept 3</span>
  </div>
  <p class="notes-card-lede">The neural network built out of a model you already use. The binary logit <em>is</em> a sigmoid; softmax <em>is</em> the multinomial logit, with three consequences that follow; the loss function is not a detail; stacking layers buys a basis that moves. Ends honestly &mdash; two results that argue against reaching for a network at all, and what one actually costs.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Interactive companions on this page</h4>
      <ul>
      <li><a href="../_static/companions/Sigmoid_Tanh_Companion.html" target="_blank" rel="noopener">Sigmoid, tanh and softmax &#8599;</a></li>
      <li><a href="../_static/companions/Multilayer_Networks_Companion.html" target="_blank" rel="noopener">Multilayer networks and learnable basis functions &#8599;</a></li>
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


## The binary logit is a sigmoid

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

## tanh, and why it is not simply better

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

## Softmax is the multinomial logit

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

## An aside worth the detour: exploration in signal control

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

## IIA does not disappear because you called it a network

Softmax inherits independence of irrelevant alternatives, and the classic
red-bus/blue-bus problem survives the rebranding intact. With route travel times
of 18, 21, and 26 minutes and $\mu = 0.35$: adding a *duplicate* of route B
leaves the A:C odds ratio at 16.4446, **unchanged** — while B's combined share
jumps from 24.8% to 39.8% and A drops from 70.9% to 56.8%.

If you have ever explained to a client why the nested logit exists, you have
already explained a limitation of the softmax output layer. Knowing the failure
in one vocabulary means you know it in the other.

## Saturation, and the detector pegged at jam occupancy

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

## The loss function is not a detail

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

## Stacking layers: a basis that moves

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

## Two results that argue against reaching for a network

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

## What it costs

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

---

Next: {doc}`notes3-learning` opens the box &mdash; what each part does, and how the parameters actually move.
