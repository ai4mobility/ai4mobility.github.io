# 1.3 How a network learns

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 1 &middot; Section 1.3</span>
    <span class="notes-card-session">Session: Sept 3</span>
  </div>
  <p class="notes-card-lede">Inside the box, continuing section 1.2. What a weight, a bias and an activation each do, one at a time; why one boundary is not enough; backpropagation traced number by number on a congestion classifier; where training goes wrong, measured; and the same machinery pointed at a regression question.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Interactive companions on this page</h4>
      <ul>
      <li><a href="../_static/companions/Neural_Networks_and_Backprop_Companion.html" target="_blank" rel="noopener">Neural network basics and backpropagation &#8599;</a></li>
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

(how-a-network-learns)=
## The parts, one at a time

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

## When one boundary is not enough

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

## How the parameters actually move

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

## Where training goes wrong, measured

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

## The same machinery, a different question

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

---

Next: {doc}`notes4-cnn` rewires the same neuron so it can look at a camera frame.
