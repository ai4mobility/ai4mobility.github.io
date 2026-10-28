(autoencoders-pca)=
# 4.4 Autoencoders: keep a few numbers, rebuild the rest

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 4 &middot; Section 4.4</span>
    <span class="notes-card-session">Session: Autoencoders</span>
  </div>
  <p class="notes-card-lede">An autoencoder squeezes a traffic state into a few numbers, the latents, and rebuilds the whole state from them. This page starts with the simplest one, PCA, worked by hand on two real I-405 detectors, then builds the same compression as a two-layer network and trains it one step at a time. Trained with its loss, the network lands exactly on PCA's answer, and the reason why sets up the deep autoencoders of 4.5.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Read it before</h4>
      <ul>
      <li><a href="../module1/notes2-learning.html">1.2 How a network learns</a> (backpropagation)</li>
      <li><a href="notes2b-latent-variables.html">4.3 Latent variables: hidden causes, not hidden layers</a></li>
      </ul>
    </div>
    <div>
      <h4>Interactive companion</h4>
      <ul><li><a href="../_static/companions/Autoencoder_Latent_Companion.html" target="_blank" rel="noopener">Inside the latent layer &#8599;</a>, mounted in 4.5; its first two tabs follow this page</li></ul>
    </div>
  </div>
</div>

## What this section covers

- What an autoencoder is: an encoder, a few latents, a decoder, and a loss that compares the output with the input
- Why a few numbers can rebuild a whole traffic state, and five reasons to want them
- PCA worked by hand on six real readings from two I-405 detectors: the definition, the five steps, what it keeps and what it drops
- The linear autoencoder: a two-layer network that can only rediscover PCA, and why
- One training step by hand (forward, loss, backward, update), the same step in PyTorch, and where training ends

An autoencoder is a network trained to rebuild its own input through a narrow middle. The input $x$ goes into
an **encoder**, which outputs a few numbers, the **latent variables** (latents for short), written $z$. A
**decoder** turns $z$ back into $y$, a copy of $x$. The loss is just the rebuild error, so no labels are needed.

:::{admonition} A note on words
:class: note
These pages call $z$ the *latents* throughout. AI papers often call it the *code*. Earlier modules called a
learned vector like this a *representation* or an *embedding* (BERT's contextual embeddings are one kind). In a
plain autoencoder the latents are simply numbers the encoder computes from $x$. The VAE of
{doc}`4.6 <notes3b-vae-basics>` gives them a probability distribution, which makes them latent variables in the full
statistical sense of {doc}`4.3 <notes2b-latent-variables>`.
:::

Sections 4.4 and 4.5 climb from the simplest autoencoder to the ones used today:

1. PCA, worked by hand, as a reminder of how it works (this page).
2. A two-layer network that rediscovers PCA, trained step by step with its loss (this page).
3. Deeper nonlinear networks, which can follow curved data that PCA cannot ({doc}`4.5 <notes2d-deep-autoencoders>`).
4. Four ways to stop a network from simply copying $x$: few latents, sparse latents, a denoising task, and a
   masking task, the BERT idea ({ref}`4.5 <stopping-the-copy>`).

They come right before the VAE of {doc}`4.6 <notes3b-vae-basics>`, which asks the next question: can the latents be
used to generate new traffic states?

**Running examples, smallest first.** Speeds at two neighbouring detectors on I-405 North in Los Angeles: real
PeMS data, small enough to work by hand. The fundamental diagram: a curve that a straight line cannot follow. And
the module's 4,000 simulated speed heatmaps of a 4-mile road, each 20 road cells &times; 20 time steps, made with
the cell transmission model (CTM).

**How to read the math.** Each idea has one key equation with every symbol named, for everyone. The *Going
deeper* boxes are optional and can be skipped.

## Keep a few numbers, rebuild the rest

A traffic management center logs speeds every few minutes from hundreds of detectors. One 4-mile corridor over
about 10 minutes, as in our heatmaps, is already 400 numbers: 20 road cells &times; 20 time steps. Most of those
numbers move together. When a queue forms, a whole block of cells slows at once. So a few numbers might be enough
to rebuild all 400. An autoencoder learns which few numbers to keep.

**The bridge.** You already compress traffic this way, using physics. The LWR model describes a road with one
density field plus a fundamental diagram. The macroscopic fundamental diagram describes a whole network with one
number, its accumulation. An autoencoder learns the compression from data instead of from a theory.

:::{admonition} Key idea: learned from data, not from theory
:class: important
LWR and the MFD keep the numbers that a theory picks. An autoencoder is told nothing about density or
accumulation. It tries ways to squeeze the data and keeps whichever rebuilds the data best. So it is a
**data-driven** method, not a theory-based compression or a set of hand-picked features. The catch is that what
it keeps need not match any variable from traffic theory. Section {doc}`4.5 <notes2d-deep-autoencoders>` checks
this on the fundamental diagram.
:::

```{figure} ../_static/figures/AEB_Hourglass.png
:alt: A 20 by 20 speed heatmap enters an encoder that narrows to a gold box of two latents, here minus 3.81 and minus 2.91; a decoder widens back to a rebuilt heatmap that is off by 4.5 mph per cell. A bracket underneath says the loss compares y with x itself.
:width: 100%

An autoencoder, after Bishop and Bishop (2024), Figures 19.1 and 19.2, on one test heatmap: the module's
2-latent autoencoder squeezes 400 speeds into 2 latents and rebuilds them to within 4.5 mph per cell. Heatmaps:
upstream at the bottom, time to the right, dark is slow.
```

Read the picture from left to right. The encoder squeezes the input $x$ ($D$ numbers) into the latents $z$ ($M$
numbers, with $M$ smaller than $D$). The decoder expands $z$ back into $y$, which has $D$ numbers again. Training
compares $y$ with $x$ itself, so the data are their own labels. This is called *self-supervised* learning. Bishop
calls the network an *auto-associative* mapping. The heatmap shown is a good case: the median test heatmap is
rebuilt to within 5.8 mph.

$$
E(\mathbf{w}) = \frac{1}{2}\sum_{n=1}^{N} \big\lVert \mathbf{y}(\mathbf{x}_n,\mathbf{w}) - \mathbf{x}_n \big\rVert^2
$$

| Symbol | Meaning on these pages |
| --- | --- |
| $\mathbf{x}_n$ | the $n$-th traffic state: 2 detector speeds, or the 400 cells of a heatmap (mph) |
| $\mathbf{y}(\mathbf{x}_n, \mathbf{w})$ | the network's rebuilt copy of $\mathbf{x}_n$ |
| $\mathbf{w}$ | every weight and bias in the encoder and the decoder |
| $N$ | the number of training examples (readings or heatmaps) |
| $\lVert \mathbf{y} - \mathbf{x} \rVert^2$ | the squared differences, added over all $D$ numbers |
| $E(\mathbf{w})$ | the loss: the total squared rebuild error |

*In words:* add up the squared rebuild error over every training example, then change the weights to make that
total small. This is Bishop's equation (19.1). We report errors as an RMS per number, in mph. RMS means
root-mean-square: square every error, average them, then take the square root. It is the typical size of one
cell's rebuild error.

## Why would anyone want this?

A few numbers that rebuild a whole traffic state are useful in five ways:

- **Store and send less.** A few latents per corridor snapshot, instead of 400 speeds, are cheap to archive or to
  send from the roadside.
- **Feed other models.** The latents are a compact input for other models, such as a travel-time predictor or a
  clustering of traffic states. Section {doc}`4.5 <notes2d-deep-autoencoders>` tests when this works and when it
  does not.
- **Flag the unusual.** A state the model cannot rebuild is unlike its training data, which can flag an incident
  or a broken detector.
- **Clean and fill.** Section {ref}`4.5 <stopping-the-copy>` turns the same idea into tools that remove noise and
  fill detector gaps.
- **Learn without labels.** Training needs only raw data, so an encoder can learn from years of unlabelled
  detector data or dashcam video, then serve a task with few labels (the masked autoencoders of 4.5).

## PCA, worked by hand on two detectors

PCA is the simplest autoencoder. It keeps the direction that explains the most variance: the one along which the
data spread out most. On two I-405 North detectors, that direction is "both stations slow down together". It keeps
80% of the variation in six readings, and 96% over all 44 weekdays.

**The data.** Stations 717790 (upstream) and 772455 (downstream) sit 0.73 mi apart on I-405 North in West Los
Angeles. PeMS logs their average speed every 5 minutes. We take six readings from Monday 7 May 2012, rounded to
whole mph so the arithmetic stays short. Each reading is a point $\mathbf{x}$ = (upstream speed, downstream speed).

| Time | Upstream (mph) | Downstream (mph) | What the road is doing |
| --- | --- | --- | --- |
| 06:00 | 72 | 69 | free flow |
| 07:00 | 26 | 27 | morning queue covers both stations |
| 09:00 | 23 | 22 | morning queue covers both stations |
| 11:30 | 55 | 45 | recovering |
| 16:30 | 70 | 18 | the back of the afternoon queue sits between the stations |
| 20:00 | 71 | 71 | free flow |

**The definition.** Project every reading onto a line through the mean: those projections are the gold dots in
the figure below. PCA picks the line along which the gold dots spread out the most. Their variance along the line
is the variance that the line explains.

$$
\mathbf{u}_1 = \arg\max_{\lVert \mathbf{u} \rVert = 1} \; \frac{1}{N}\sum_{n=1}^{N} \big( \mathbf{u}^{\top}(\mathbf{x}_n - \mathbf{m}) \big)^2
$$

*In words:* $\mathbf{u}$ is a direction of length 1, $\mathbf{m}$ is the mean reading, and
$\mathbf{u}^{\top}(\mathbf{x}_n - \mathbf{m})$ is how far along that line reading $n$'s gold dot sits. Turn the
line around the mean, measure how spread out the gold dots are at each angle, and keep the angle where the spread
is largest.

```{figure} ../_static/figures/AEB_PCA_Definition.png
:alt: Left, a scatter of upstream against downstream speed with six dark green readings, a green line through the mean, gold dots where each reading projects onto the line, and dashed lines for what is lost; the 16:30 reading at 70 and 18 mph is rebuilt far away at 49 and 38 mph. Grey background, all 12,672 readings along the diagonal. Right, kept and lost variance against the angle of the line; kept peaks at 722.3 at 46.5 degrees, where lost is smallest, 175.5; they always add to 897.8.
:width: 100%

PCA's definition, measured on the six readings. Left: the first principal direction (green line), each reading's
projection on it (gold) and what is lost (dashed); grey, all 12,672 weekday readings. Right: the spread of the gold
dots (kept) and the average squared loss (lost) for every angle of the line.
```

In the left panel each dark green dot is a reading. The green line is the first principal direction, drawn
through the mean. PCA keeps one number per reading, how far along the line its gold dot falls, and the gold dot is
also the rebuild from that one number. The dashed line is what is lost.

The right panel turns the line through every angle. The spread of the gold dots peaks at 46.5&deg;, at
722.3 mph&sup2;. At the same angle the lost part, the dashed lines, is smallest, because kept and lost always add up
to the same total, 897.8 mph&sup2;. Neither station alone is a good summary: the upstream axis (0&deg;) keeps
434.5, the downstream axis (90&deg;) 463.3. The five steps below find 46.5&deg; without trying every angle.

**The five steps.**

1. **Centre.** Subtract the mean $\mathbf{m}$ = (52.83, 42.00) mph from every reading. The 06:00 reading becomes
   (19.17, 27.00).
2. **Covariance.** S = (1/N) &Sigma; (x&#8345; &minus; m)(x&#8345; &minus; m)&#7488; = [[434.5, 273.0], [273.0, 463.3]] mph&sup2;. The diagonal holds each
   station's variance. The off-diagonal 273.0 says the two stations rise and fall together. Dividing by N &minus; 1
   instead of N changes no direction.
3. **Directions.** The eigenvectors of S are the principal directions, and each eigenvalue is the variance along
   its direction. For a 2 &times; 2 matrix [[a, b], [b, c]] there is a short formula:
   &lambda; = (a + c)/2 &plusmn; &radic;(((a &minus; c)/2)&sup2; + b&sup2;) = 448.9 &plusmn; 273.4. So &lambda;&#8321; = 722.3 and
   &lambda;&#8322; = 175.5 mph&sup2;. The first direction is u&#8321; &prop; (b, &lambda;&#8321; &minus; a) = (273.0, 287.8), or (0.688, 0.726)
   at unit length. &lambda;&#8321; is 80.5% of the total variance, 897.8 mph&sup2;.
4. **Encode.** z = u&#8321;&#7488;(x &minus; m). For 06:00: 0.688 &times; 19.17 + 0.726 &times; 27.00 = 32.8.
5. **Decode.** x&#770; = m + z u&#8321;. For 06:00: (52.83 + 32.8 &times; 0.688, 42.00 + 32.8 &times; 0.726) = (75.4, 65.8) mph,
   about 3 mph off at each station.

| Time | Reading x (mph) | Latent z | Rebuilt x&#770; (mph) | Error x &minus; x&#770; (mph) | Squared error (mph&sup2;, from unrounded values) |
| --- | --- | --- | --- | --- | --- |
| 06:00 | (72, 69) | 32.8 | (75.4, 65.8) | (&minus;3.4, 3.2) | 21.9 |
| 07:00 | (26, 27) | &minus;29.3 | (32.6, 20.7) | (&minus;6.6, 6.3) | 83.6 |
| 09:00 | (23, 22) | &minus;35.0 | (28.7, 16.6) | (&minus;5.7, 5.4) | 62.1 |
| 11:30 | (55, 45) | 3.7 | (55.4, 44.7) | (&minus;0.4, 0.3) | 0.2 |
| 16:30 | (70, 18) | &minus;5.6 | (49.0, 37.9) | (21.0, &minus;19.9) | 839.3 |
| 20:00 | (71, 71) | 33.5 | (75.9, 66.3) | (&minus;4.9, 4.7) | 45.9 |

Steps 4 and 5 are exactly the encoder and the decoder of the autoencoder above:

$$
z = \mathbf{u}_1^{\top}(\mathbf{x}-\mathbf{m}) \qquad\qquad \hat{\mathbf{x}} = \mathbf{m} + \mathbf{u}_1\, z
$$

| Symbol | Meaning |
| --- | --- |
| $\mathbf{x}$ | one reading: (upstream speed, downstream speed), mph |
| $\mathbf{m}$ | the mean reading, mph |
| $\mathbf{u}_1$ | the first principal direction, a vector of length 1 |
| $z$ | the latent: one number per reading, in mph along $\mathbf{u}_1$ |
| $\hat{\mathbf{x}}$ | the rebuilt reading, mph |

*In words:* the encoder measures how far the reading sits along the main direction. The decoder walks that far
along the line, starting from the mean.

**What PCA keeps, and what it drops.** The average squared error per reading is 1,053.0 / 6 = 175.5 mph&sup2;,
which is exactly &lambda;&#8322;. PCA throws away the variance along the second direction and nothing else. That is
9.37 mph RMS per station. The second direction, u&#8322; = (&minus;0.726, 0.688), measures the gap between the two
stations. At 16:30 the gap is the whole story: the back of the queue sits between the stations, so the downstream
station is slow and the upstream one is not. That one reading is 80% of the squared error.

Over all 12,672 readings, the first direction keeps 96.1% of the variance and the RMS error falls to 4.29 mph.
Yet 3.8% of readings still miss by more than 10 mph at one station. Those are the moments when a queue's edge sits
between the detectors: often what an operator most wants to see. Choosing how many numbers to keep is a judgment
about what you can afford to lose.

**Choosing how many directions.** With $M$ of $D$ directions kept, the average squared error is the sum of the
$D - M$ dropped eigenvalues. One fit ranks every direction by the variance it explains, so with PCA you choose $M$
after the fit, by reading the eigenvalues. Section {doc}`4.5 <notes2d-deep-autoencoders>` shows that a deep
autoencoder cannot do this.

Check it yourself (the output should read 722.3 and 175.5, then (0.688, 0.726), then 9.37):

```python
import numpy as np
X = np.array([[72,69],[26,27],[23,22],[55,45],[70,18],[71,71]], float)
m = X.mean(0)
S = (X - m).T @ (X - m) / len(X)          # covariance, divided by N
lam, U = np.linalg.eigh(S)                # eigenvalues, smallest first
u1 = U[:, -1] * np.sign(U[:, -1].sum())   # first direction, pointing to "both faster"
z = (X - m) @ u1                          # encoder: one number per reading
Xhat = m + np.outer(z, u1)                # decoder
print(lam[::-1].round(1), u1.round(3), np.sqrt(((X - Xhat)**2).mean()).round(2))
```

:::{admonition} Going deeper &mdash; why eigenvectors?
:class: dropdown
PCA picks the unit vector $\mathbf{u}$ that makes the variance of $z = \mathbf{u}^{\top}(\mathbf{x} - \mathbf{m})$
as large as possible. That variance is $\mathbf{u}^{\top}\mathbf{S}\mathbf{u}$. Maximising it subject to
$\mathbf{u}^{\top}\mathbf{u} = 1$, with a Lagrange multiplier, gives $\mathbf{S}\mathbf{u} = \lambda\mathbf{u}$. So
$\mathbf{u}$ must be an eigenvector of $\mathbf{S}$, and the variance it keeps is its eigenvalue: pick the largest.
The same direction also gives the smallest rebuild error. Each reading's squared distance from the mean splits
into a part along $\mathbf{u}$ (kept) and a part across it (lost), so keeping the most variance means losing the
least. With $M$ of $D$ directions kept, the average squared error is the sum of the $D - M$ dropped eigenvalues.
Source: Bishop and Bishop (2024), *Deep Learning*, section 16.1.
:::

## The linear autoencoder: a two-layer network that rediscovers PCA

Build the network of the first figure with two layers of weights and one hidden unit, and train it with the same
loss. It lands on PCA's answer. Adding a tanh to the hidden unit does not change that. This is Bishop's
Figure 19.1, drawn here with $D$ = 2 inputs and $M$ = 1 hidden unit.

```{figure} ../_static/figures/AEB_Linear_Net.png
:alt: Two input nodes, upstream and downstream speed, connect through weights w1 to one gold hidden unit z, with a = w1 dot x plus b1 and z = h(a); z connects through weights w2 to two outputs, the rebuilt speeds. A box on the right says that whatever h is, the decoder y = b2 + w2 z is linear, so every rebuild lies on one straight line.
:width: 100%

Bishop and Bishop (2024), Figure 19.1, for our two detectors: two inputs, one hidden unit, two outputs.
```

The network has seven numbers to learn: two encoder weights $\mathbf{w}_1$, one encoder bias $b_1$, two decoder
weights $\mathbf{w}_2$ and two decoder biases $\mathbf{b}_2$. One forward pass is three lines:

$$
a = \mathbf{w}_1^{\top}\mathbf{x} + b_1 \qquad z = h(a) \qquad \mathbf{y} = \mathbf{w}_2\, z + \mathbf{b}_2
$$

| Symbol | Meaning |
| --- | --- |
| $\mathbf{x} = (x_1, x_2)$ | one reading, scaled: (speed &minus; 50 mph) / 25 mph at each station |
| $\mathbf{w}_1, b_1$ | encoder: 2 weights and 1 bias |
| $a$ | the hidden unit's input, one number |
| $h$ | the activation: tanh, or none at all (the *linear* autoencoder) |
| $z$ | the latent: one number per reading |
| $\mathbf{w}_2, \mathbf{b}_2$ | decoder: 2 weights and 2 biases |
| $\mathbf{y} = (y_1, y_2)$ | the rebuilt reading, scaled |

*In words:* mix the two speeds into one number, squash it with $h$, then spread that number back out along the
direction $\mathbf{w}_2$.

**Why it can only find PCA.** Look at the last line. The decoder is linear, so every output is $\mathbf{b}_2$ plus
some multiple of $\mathbf{w}_2$. As $z$ varies, $\mathbf{y}$ slides along one straight line in the (upstream,
downstream) plane, whatever $h$ is. Training can only choose which line, and where each reading lands on it. The
line with the smallest squared error is PCA's first direction through the mean. The activation $h$ moves points
*along* the line; it cannot bend the line. With $M$ hidden units the line becomes a flat $M$-dimensional sheet, and
the best sheet is the span of the first $M$ principal directions.

Bourlard and Kamp (1988) proved that nonlinear hidden units do not help here. Baldi and Hornik (1989) showed that
the linear network's loss has no poor valleys to get stuck in, so training reaches PCA's subspace. Bishop draws
the practical lesson: there is no advantage in a two-layer network for dimensionality reduction. PCA, computed
with the singular value decomposition, gives the same subspace exactly, in finite time. It also orders the
directions by importance and makes them perpendicular; the network's weight vectors need not be either. So why
build the network at all? Because it is the template. Section {doc}`4.5 <notes2d-deep-autoencoders>` adds layers,
and then it can do what PCA cannot.

## Training the two layers with the loss

Training repeats one move. Run a reading forward, measure the loss, send the error backward to get a slope for
each of the seven numbers, then step each number downhill. After 30,000 such steps, the tanh network rebuilds the
six readings with 9.37 mph RMS error per station: PCA's error, to two decimals.

```{figure} ../_static/figures/AEB_Train_Curve.png
:alt: Left, rebuild error against training step on a log scale; the tanh network and the network with no activation both fall from about 19 mph to PCA's 9.37 mph line by about step 100 and stay there, while a network with 2 hidden units falls to 0.04 mph. Right, the tanh curve with a gold band where the six trained readings sit, all with the largest absolute input 0.26, where tanh is nearly straight.
:width: 100%

Left: the error falling during training (the six readings; Adam, learning rate 0.01). Right: where the trained
network uses tanh.
```

The left panel shows the error falling during training. The right panel shows where the trained network uses
tanh: only in the gold band near zero, where tanh is almost straight. The rest of this section explains both.

### One step by hand

Scale the 16:30 reading, (70, 18) mph: x = ((70 &minus; 50)/25, (18 &minus; 50)/25) = (0.80, &minus;1.28). Start from
small made-up weights: w&#8321; = (0.4, 0.1), b&#8321; = 0, w&#8322; = (0.5, 0.2), b&#8322; = (0, 0). Use a learning rate
&eta; = 0.5.

**Forward.**

1. a = w&#8321;&#7488;x + b&#8321; = 0.4 &times; 0.80 + 0.1 &times; (&minus;1.28) + 0 = 0.192
2. z = tanh(0.192) = 0.1897
3. y = w&#8322;z + b&#8322; = (0.5 &times; 0.1897, 0.2 &times; 0.1897) = (0.095, 0.038). In mph that is (52.4, 50.9); the real
   reading is (70, 18).
4. E = &frac12;&#8214;y &minus; x&#8214;&sup2;, the loss above for this one reading. Written out:

$$
\begin{aligned}
E &= \tfrac{1}{2}\,\lVert \mathbf{y}-\mathbf{x} \rVert^2 = \tfrac{1}{2}\big[(y_1-x_1)^2 + (y_2-x_2)^2\big] \\
  &= \tfrac{1}{2}\big[(0.095-0.80)^2 + (0.038-(-1.28))^2\big] \\
  &= \tfrac{1}{2}\big[(-0.705)^2 + 1.318^2\big] = \tfrac{1}{2}\,(0.497 + 1.737) = 1.117
\end{aligned}
$$

*In words:* subtract the real reading from the rebuild, number by number, square each gap, add them up and halve
the total. The &frac12; only makes the slopes below tidier.

**Backward.** The chain rule carries the error from the loss back to each weight:

$$
\frac{\partial E}{\partial \mathbf{w}_2} = (\mathbf{y}-\mathbf{x})\,z \qquad
\frac{\partial E}{\partial a} = \mathbf{w}_2^{\top}(\mathbf{y}-\mathbf{x})\,\big(1-z^2\big) \qquad
\frac{\partial E}{\partial \mathbf{w}_1} = \frac{\partial E}{\partial a}\,\mathbf{x}
$$

| Quantity | Formula | Value |
| --- | --- | --- |
| error at the output | y &minus; x | (&minus;0.705, 1.318) |
| slope for w&#8322; | (y &minus; x) z | (&minus;0.134, 0.250) |
| slope for b&#8322; | y &minus; x | (&minus;0.705, 1.318) |
| error sent back to z | w&#8322;&#7488;(y &minus; x) = 0.5 &times; (&minus;0.705) + 0.2 &times; 1.318 | &minus;0.089 |
| error after passing through tanh | &times; (1 &minus; z&sup2;) = &times; 0.964 | &minus;0.0858 |
| slope for w&#8321; | &minus;0.0858 &times; x | (&minus;0.069, 0.110) |
| slope for b&#8321; | &minus;0.0858 | &minus;0.086 |

*In words:* each weight's slope is the error that reaches it times the signal that flowed through it. The factor
(1 &minus; z&sup2;) is the slope of tanh, and it is the only place the activation enters training. If |a| were large,
tanh would be flat, (1 &minus; z&sup2;) would be near 0, and the encoder would barely learn: the saturation problem from
{doc}`Module 1 <../module1/notes2-learning>`.

**Update.** New = old &minus; &eta; &times; slope. So w&#8321; = (0.4, 0.1) &minus; 0.5 &times; (&minus;0.069, 0.110) = (0.434, 0.045),
b&#8321; = 0.043, w&#8322; = (0.567, 0.075) and b&#8322; = (0.353, &minus;0.659). Run the reading forward again: the rebuild
moves from (52.4, 50.9) to (63.4, 34.1) mph, toward the real (70, 18). Its loss falls from 1.117 to 0.243.

PyTorch computes the same slopes automatically. Three lines, marked (1) to (3), are the whole autoencoder:
encoder, decoder and loss. Check it (it should print 1.117 and the slopes in the table):

```python
import torch
x = torch.tensor([0.80, -1.28])
w1 = torch.tensor([0.4, 0.1], requires_grad=True); b1 = torch.tensor(0.0, requires_grad=True)
w2 = torch.tensor([0.5, 0.2], requires_grad=True); b2 = torch.zeros(2, requires_grad=True)
z = torch.tanh(w1 @ x + b1)             # (1) encoder
y = w2 * z + b2                         # (2) decoder
E = 0.5 * ((y - x) ** 2).sum()          # (3) loss: the formula above, one reading
E.backward()                            # the chain rule, done for you
print(round(E.item(), 3), w1.grad, b1.grad, w2.grad, b2.grad)
```

Keep these three lines in mind for the rest of the autoencoder pages, because every variant changes exactly one of
them. A deep autoencoder makes lines (1) and (2) longer. A denoising autoencoder changes what goes into line (1). A
masked autoencoder changes which cells line (3) scores.

### From one step to a trained network

**Average over the readings.** One reading pulls the weights toward itself. After the step above, the loss added
over all six readings actually rose, from 3.595 to 3.889. Real training averages the six slopes before it steps.
With the same start and &eta; = 0.5, that averaged step lowers the six-reading loss from 3.595 to 2.641. With
thousands of readings, each step averages over a random handful of them: stochastic gradient descent.

**Where it ends.** After 30,000 steps with Adam, a popular version of gradient descent that adapts the step size
for each weight (left panel of the figure):

- One hidden unit with tanh: 9.37 mph, the same as PCA. Its decoder direction w&#8322; points along (0.688, 0.726):
  PCA's u&#8321;, to three decimals.
- One hidden unit with no activation: 9.37 mph as well.
- On all 12,672 readings (6,000 steps, three random starts): tanh 4.295 to 4.300 mph, PCA 4.29 mph. Close to PCA,
  never below it.

How did tanh end up acting like no activation at all? Look at the trained weights. The encoder shrank to
w&#8321; = (0.125, 0.131), so the largest |a| over the six readings is 0.26 (right panel), where tanh is almost straight:
tanh(0.26) = 0.254. The decoder grew to w&#8322; = (3.865, 4.075) to undo the shrink. The network used tanh only where
it is linear, because a straight line is the best it can draw anyway.

**A warning sign.** Give the same network 2 hidden units, as many as there are inputs (the slate curve). Its error
drops to 0.04 mph, because it simply copies x. That is a near-perfect score, and the network has learned nothing
about the road. Section {ref}`4.5 <stopping-the-copy>` shows how hard this trap is to see in 400 dimensions, and four
ways around it.

:::{admonition} Before you trust this result
:class: warning
**What is the baseline?** PCA with the same number of latents: one direction, 9.37 mph per station on the six
readings and 4.29 mph on all 12,672. The networks are judged by how close they come to it.

**How was the data split, and why is that honest?** There is no split here: PCA and the networks are fitted and
scored on the same readings, because they are compared on the very error they minimise, not on prediction. The
next two pages use held-out test data.

**What does it do on the ugly cases?** The average hides them. 16:30, with the back of a queue between the
stations, is 80% of the six-reading error, and over all weekdays 3.8% of readings still miss by more than 10 mph at
one station.
:::

## Check yourself

1. Using m = (52.83, 42.00) and u&#8321; = (0.688, 0.726), encode and decode the 07:00 reading by hand; you should get its
   row in the table above. Then do the same for 16:30, and explain in traffic terms why its error is so much larger.
2. Your PCA rebuild of a corridor has a 4 mph RMS error. Your manager wants to use the rebuilt speeds to report
   queue lengths. What would you check before you agree?

---

Next: {doc}`4.5 Deep autoencoders <notes2d-deep-autoencoders>` &mdash; put nonlinear layers inside the decoder, and the line can bend.
