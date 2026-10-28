(gan)=
# 4.7 Generative Adversarial Networks (GAN)

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 4 &middot; Section 4.7</span>
    <span class="notes-card-session">Session: The VAE and the GAN</span>
  </div>
  <p class="notes-card-lede">The third answer replaces the hand-written loss with a learned one. Squared error needs a partner to compare with, and a generator fed random numbers has none; a GAN trains a second network, the critic, to judge whether a sample looks real, and trains the generator against it. This page builds the two losses in Bishop&rsquo;s notation, watches the two networks play on a real I-405 detector pair, uses the critic as an add-on that sharpens an autoencoder, and scores the first three answers side by side on the same held-out heatmaps.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Read it before</h4>
      <ul>
      <li><a href="notes3b-vae-basics.html">4.6 Variational autoencoders (VAE)</a></li>
      <li><a href="notes2c-autoencoders.html">4.4 Autoencoders</a>, for the detector pair</li>
      </ul>
    </div>
    <div>
      <h4>Read it after</h4>
      <ul><li><a href="notes6-diffusion-basics.html">4.8 Diffusion models: the basics</a></li></ul>
    </div>
  </div>
</div>

## What this section covers

- Why a learned loss: squared error needs a partner, and a generator from random numbers has none
- The picture (Bishop Figure 17.1 with traffic heatmaps), and the discriminator as a binary logit model
- The two losses: cross-entropy for the critic, and the saturating and non-saturating losses for the generator
- Training as two players taking turns, watched on a real detector pair, and why the losses have no finish line
- What goes wrong (strands, wandering, a critic off its data) and what balance does
- The critic as an add-on loss that sharpens a decoder
- Judging a GAN from outside, and a first scorecard for the autoregressive model, the VAE and the GAN
- Where it breaks, fit card, applications, a summary and six questions

A generative adversarial network (GAN) is a training method. It keeps the generator you already know, a decoder that turns random numbers into data, and replaces the hand-written loss with a second network that learns to judge whether its output looks real. The two networks are trained together, each against the other.

This page comes after {doc}`4.6 Variational autoencoders (VAE) <notes3b-vae-basics>` and before {doc}`4.8 Diffusion models <notes6-diffusion-basics>`. It goes slowly through three things: why a learned loss is needed, how its two losses are built, and how the two networks train against each other. It ends with the first scorecard of this module, which puts the GAN beside the autoregressive model and the VAE on the same held-out heatmaps.

By the end you should be able to:

- say why squared error cannot train a generator that starts from random numbers
- write the discriminator's loss and the generator's loss, and say in words what each one rewards
- trace where each network's gradient comes from during training
- read GAN training curves, and say why the loss cannot tell you when to stop
- say when a critic helps as an add-on to a reconstruction loss, and when a GAN is the wrong tool

### Words and symbols

The symbols follow Bishop and Bishop (2024), *Deep Learning*, Chapter 17, which is the course textbook. The classroom words are the ones used on the course site.

| Symbol | Bishop's name | Classroom word | On this page |
| --- | --- | --- | --- |
| $\mathbf{z}$ | latent variable, drawn from N(0, I) | random input | 2 random numbers (detector pair) or 32 (heatmaps), drawn fresh every time |
| $\mathbf{g}(\mathbf{z}, \mathbf{w})$ | generator, with weights w | forger | turns z into one fake reading or one fake heatmap |
| $\mathbf{x}$ | a data vector | a reading or a heatmap | (upstream, downstream) speed in mph, or a 20 × 20 speed heatmap |
| $d(\mathbf{x}, \phi)$ | discriminator, with weights φ | critic | the probability that x is real |
| $t$ | target: 1 = real, 0 = synthetic | label | what the critic is trained to predict |
| $E_{\text{GAN}}(\mathbf{w}, \phi)$ | GAN error function | the score of the game | the critic lowers it; the forger raises it |

One caution on the word *critic*. In everyday GAN talk it means the discriminator, and this page uses it that way. In the Wasserstein GAN papers it means a specific variant whose output is a score, not a probability ({ref}`Fixes you will meet in papers <gan-fixes>`).

### Two running examples

The same two datasets run through the autoencoder, VAE and diffusion pages ({doc}`4.4 <notes2c-autoencoders>`, {doc}`4.6 <notes3b-vae-basics>` and {doc}`4.8 <notes6-diffusion-basics>`), so you can compare the methods on the same data.

1. **Real: one detector pair on I-405 N.** PeMSD7(M) 5-minute speeds at station 717790 (upstream) and station 772455 (downstream), 0.73 mi apart, on 44 weekdays in May and June 2012. Models are fitted on May (6,624 readings) and scored on June (6,048 readings). Each reading is one point with two numbers, so every real reading, every fake and the critic's whole judgment fit on one plot. In May, 51.4% of readings are free-flowing at both stations (55 mph or more), 37.2% are slow at both (under 40 mph), and 3.4% show a **queue between the stations**: fast upstream, slow downstream.
2. **Synthetic: 4,000 CTM speed heatmaps.** Each is 20 road cells × 20 time steps (4 miles × 9.6 minutes) from the course's cell transmission model, split into 3,200 training, 400 validation and 400 test heatmaps. These are simulated, not observed, and they show the sharp shockwave fronts that a good generator has to keep.

(gan-why)=
## Why a learned loss?

```{figure} ../_static/figures/GB_Two_Lanes.png
:alt: Two lanes of boxes. Top lane, autoencoder or VAE: x, one real heatmap; encoder; z, a few latents; decoder; x-hat, the rebuilt x; a dashed arrow back to x labelled: loss, compare x-hat with the same x, cell by cell (squared error). Bottom lane, generator trained as a GAN: z, a random draw; generator g(z, w); x-tilde, a fake heatmap, with the note no partner heatmap to compare with; discriminator d(x, phi), learned, highlighted; P(real), the loss comes from it. Real heatmaps, many and unpaired, feed the discriminator from below; question asked: does x-tilde look like these?
:width: 100%

Where the training signal comes from. An autoencoder or VAE compares its output with the same input; a generator fed random numbers has nothing to compare with, so a learned discriminator supplies the loss.
```

The autoencoder's loss needs a partner: the heatmap it was asked to rebuild. A generator that starts from a random draw has no partner, so the loss has to come from somewhere else: a network that has learned what real traffic looks like.

### The loss you already know

In the autoencoder and the VAE, the decoder's loss compares its output x̂ with the input x it was given: the same heatmap, cell by cell. Every training example brings its own answer key. That pairing is what makes the loss computable.

### Problem one: squared error rewards the average

{doc}`4.6 <notes3b-vae-basics>` diagnosed this. When several outputs are plausible for the same latents, the output with the lowest squared error is their average, and the average of many sharp fronts is one soft front. In the {ref}`first scorecard <gan-heatmap-scorecard>` below, the 2-knob VAE's samples have fronts of 22.5 mph (the largest jump between neighbouring road cells, averaged over heatmaps), against 39.6 mph in real test heatmaps.

(gan-no-answer-key)=
### Problem two: random numbers come with no answer key

A generator starts from a random draw z, not from a real heatmap. No heatmap belongs to a given z, so there is nothing to compare its output with. The simplest way to force squared error onto it is to pair each z with a randomly drawn real example. The figure shows what that teaches, using the same generator networks the GANs on this page use.

```{figure} ../_static/figures/GB_No_Target.png
:alt: Left: a scatter of May speed readings, upstream against downstream station, in three groups (free flow at both, slow at both, a queue between); every output of the squared-error generator sits on one point at the average, (50.6, 48.4) mph. Right: three rows of three heatmaps: real test heatmaps with sharp fronts, the squared-error generator making the same blurry average three times, and the course GAN making varied sharp heatmaps.
:width: 100%

Left: the I-405 pair. Right: CTM heatmaps (time runs left to right over 9.6 minutes, upstream at the bottom of 4 miles). Median RMS difference between two heatmaps of a set: 1.9 mph for the squared-error generator, 25.2 mph for real test heatmaps, 28.3 mph for the GAN. The first three of each set are shown, not picked.
```

- **Detector pair.** After 20,000 rounds, all 6,048 outputs sit at (50.6, 48.4) mph, with a spread of 0.06 mph. That is the May average, (50.5, 48.4) mph, and the road is almost never in that state: only 0.4% of May readings lie within 5 mph of it at both stations, because it falls between free flow and congestion.
- **Heatmaps.** The 244,289-weight generator of the course GAN, trained for 6,000 rounds this way, makes 400 near-copies of one heatmap: every output lies within 1.9 mph RMS of the training-average heatmap. Its fronts reach 15.4 mph, against 39.6 mph for real heatmaps and 40.0 mph for the GAN.

In words: when the target is random, the best single answer is the average target, so every z learns the same answer. This is problem one taken to its end. With no information about which example to rebuild, the average is all that is left.

:::{admonition} Key idea
:class: tip

Squared error asks "is this close to *that* example?" A generator needs the question "is this like *the* examples?" Only the second question makes sense without a pairing.
:::


### What we want: a judgment, not a distance

Often what matters is whether a generated heatmap looks like real traffic, not whether it matches one particular original. Engineers make that judgment all the time. Shown a simulated speed contour beside observed ones, a reviewer can say "that one is not real" without naming the observed day it should have matched.

The GAN trains a network to make that judgment and uses its verdict as the generator's loss. The judge is an ordinary classifier, and its labels come free: 1 for a real heatmap, 0 for one the generator made. In Bishop's words, this "turns the unsupervised density modelling problem into a form of supervised learning" (section 17.1).

:::{admonition} Key idea
:class: tip

A GAN is a training method, not a new network shape. The generator can be the same network as a VAE decoder: in the course heatmap GAN it is a stack of transpose convolutions, exactly the shape of a decoder. What changes is where its loss comes from.
:::


Each generator in this module solves the missing answer key differently. The VAE builds pairs with an encoder (x → z → x̂). Diffusion builds pairs by adding known noise to real data, so the noise is the answer key. The GAN gives up on pairs and learns a judge instead.

(gan-picture)=
## The picture

```{figure} ../_static/figures/GB_Picture.png
:alt: z, 32 random numbers, goes into the generator g(z, w) with 244,289 weights, which makes a stack of synthetic heatmaps labelled t = 0. A stack of real CTM heatmaps is labelled t = 1. Both stacks feed the discriminator d(x, phi) with 135,745 weights, whose output t is P(t = 1): how sure it is that x is real. A red band in each heatmap marks a queue.
:width: 100%

Bishop &amp; Bishop Figure 17.1, redrawn with the course CTM heatmaps. The weight counts are those of the course heatmap GAN, scored in the {ref}`heatmap scorecard <gan-heatmap-scorecard>` below.
```

The whole method is in this one figure: a generator makes fakes, and a discriminator is trained to tell them from real heatmaps. The numbers are from the GAN trained on the course heatmaps, scored in the {ref}`heatmap scorecard <gan-heatmap-scorecard>`.

Walk through it part by part.

1. **z, the random input.** 32 numbers drawn from a standard bell, N(0, I) (Bishop eq. 17.1), new ones every time. It plays the role the VAE's latents play when a VAE generates: a point in latent space.
2. **The generator g(z, w).** Turns z into a 20 × 20 heatmap. Its only job is to make heatmaps the discriminator will call real.
3. **Synthetic heatmaps, labelled t = 0.** Fresh fakes every round, so the discriminator always judges the generator's latest work.
4. **Real heatmaps, labelled t = 1.** The 3,200 training heatmaps. They are never matched to particular fakes.
5. **The discriminator d(x, φ).** A convolutional classifier with one output: the probability that its input is real (Bishop eq. 17.4).
6. **t, the target.** The label the discriminator is trained to predict.

Three things the figure does not show, and all three matter.

- **The discriminator judges each heatmap on its own.** It is trained on batches of many, but it never gets a fake and a real heatmap side by side to compare. Its verdict on each one rests on what real heatmaps look like in general, learned from thousands of them. (A technical footnote: the course critic uses batch normalisation, so during training the other heatmaps in a batch nudge each verdict slightly.)
- **The generator never sees a real heatmap.** Everything it learns about real traffic arrives as a gradient passed back through the discriminator ({ref}`Where the gradient goes <gan-gradient>`).
- **After training, the discriminator is thrown away** (Bishop section 17.1). Only the generator is kept: draw z, run g once, and you have a new heatmap.

The detector-pair GAN used below has the same shape at a smaller size: z is 2 numbers, the generator has 33,666 weights, and the discriminator has 33,537.

(gan-logit)=
### The bridge: the discriminator is a binary logit model

You have estimated binary logit models, such as the probability of a crash given site features, P = 1 / (1 + e^(−V)) with a linear utility V fitted by maximum likelihood. The discriminator is the same model with two changes: the utility is a neural network, and the two alternatives are *real* and *synthetic*.

$$
d(\mathbf{x}, \phi) \;=\; P(t = 1 \mid \mathbf{x}) \;=\; \sigma\big(s(\mathbf{x}, \phi)\big) \;=\; \frac{1}{1 + e^{-s(\mathbf{x}, \phi)}}
$$

| Symbol | Here |
| --- | --- |
| $s(\mathbf{x}, \phi)$ | the discriminator network's raw score for x: its utility, or logit |
| $\sigma$ | the logistic sigmoid, the same S-curve as the binary logit |
| $d(\mathbf{x}, \phi)$ | the probability that x is real; 0.5 means "cannot tell" |
| $\phi$ | the discriminator's weights (135,745 for the heatmaps) |

*In words:* the discriminator is a binary logit whose utility is a deep network, choosing between "real" and "synthetic" for each heatmap.

Its loss, {ref}`below <gan-critic-loss>`, is the negative log-likelihood of that logit: the cross-entropy you minimise whenever you estimate a logit model. One thing has no counterpart in a crash model. The synthetic class is produced by another model that keeps changing, so this classifier is always chasing a moving target.

(gan-loss)=
## How the loss is designed

A GAN has two losses built from one number, d, the discriminator's probability that its input is real. The discriminator is trained to push d up on real data and down on fakes. The generator is trained to push d up on its fakes.

(gan-critic-loss)=
### The discriminator's loss: ordinary cross-entropy

The discriminator is a classifier, so it is trained with the classifier's usual loss (Bishop eq. 17.5):

$$
E(\mathbf{w}, \phi) \;=\; -\frac{1}{N} \sum_{n=1}^{N} \big\{ t_n \ln d_n + (1 - t_n) \ln (1 - d_n) \big\}
$$

Every real example has t = 1 and every fake has t = 0, so the sum splits into a real part and a fake part (Bishop eq. 17.6):

$$
E_{\mathrm{GAN}}(\mathbf{w}, \phi) \;=\; -\frac{1}{N_{\mathrm{real}}} \sum_{n \in \mathrm{real}} \ln d(\mathbf{x}_n, \phi) \;-\; \frac{1}{N_{\mathrm{synth}}} \sum_{n \in \mathrm{synth}} \ln\big(1 - d(\mathbf{g}(\mathbf{z}_n, \mathbf{w}), \phi)\big)
$$

| Symbol | Here |
| --- | --- |
| $t_n$ | 1 if example n is real, 0 if the generator made it |
| $d_n$, $d(\mathbf{x}_n, \phi)$ | the discriminator's probability that example n is real |
| $\mathbf{x}_n$ | a real reading (detector pair) or a real heatmap |
| $\mathbf{g}(\mathbf{z}_n, \mathbf{w})$ | a fake made from the random draw $\mathbf{z}_n$ |
| $N_{\text{real}}$, $N_{\text{synth}}$ | real and fake examples in one mini-batch: 256 each for the detector pair, 64 each for the heatmaps |
| $E_{\text{GAN}}(\mathbf{w}, \phi)$ | the score of the game: low when the discriminator is right |

*In words:* the discriminator pays −ln d for every real example and −ln(1 − d) for every fake. Each payment is near zero when it is right and confident, and large when it is confident and wrong.

One number is worth remembering. If the discriminator cannot tell at all, it says d = 0.5 for everything and pays ln 2 = 0.693 on each average, so $E_{\text{GAN}}$ = 2 ln 2 = 1.386. The {ref}`training section <gan-training>` calls this the *cannot-tell level*.

**Worked example.** Take the detector-pair GAN of the {ref}`six snapshots <gan-watch>` after 100 training rounds, and score three readings with its critic. The values of d are read from the critic's map at the nearest half-mph point.

| Reading (upstream, downstream) | Label t | Critic's d | What the critic pays |
| --- | --- | --- | --- |
| near (70, 70) mph, free flow at both stations | 1 (real) | 0.880 | −ln 0.880 = 0.128 |
| (70, 18) mph, a queue between the stations, Monday 7 May 2012, 16:30 | 1 (real) | 0.567 | −ln 0.567 = 0.567 |
| (49.8, 35.5) mph, the first fake of round 100 | 0 (fake) | 0.397 | −ln(1 − 0.397) = 0.506 |

$E_{\text{GAN}}$ for this tiny batch is the average real payment plus the fake payment: (0.128 + 0.567) / 2 + 0.506 = 0.85, well below the cannot-tell level of 1.386.

Notice that the critic is not equally sure about every kind of real reading. At round 100 it gives May's free-flow readings an average d of 0.87, but readings that are slow at both stations only 0.49, even though they are 37% of May. What sets d is the balance between real readings and fakes nearby, not the amount of data ({ref}`Why it is a game <gan-game>`): at round 100 many fakes sat close to the slow cluster, and few near free flow.

(gan-generator-loss)=
### The generator's loss: the same score, pushed the other way

Both networks are trained on the one score $E_{\text{GAN}}$, in opposite directions (Bishop eqs. 17.7 and 17.8):

$$
\Delta \phi \;=\; -\lambda \, \nabla_{\phi} E_{\mathrm{GAN}}(\mathbf{w}, \phi), \qquad \Delta \mathbf{w} \;=\; +\lambda \, \nabla_{\mathbf{w}} E_{\mathrm{GAN}}(\mathbf{w}, \phi)
$$

Here λ is the learning rate. The minus sign makes the discriminator step downhill on $E_{\text{GAN}}$, and the plus sign makes the generator step uphill. Any gain for one is a loss for the other, which is why Bishop calls it a zero-sum game.

Only the fake part of $E_{\text{GAN}}$ depends on the generator's weights w; the real heatmaps are what they are. So raising $E_{\text{GAN}}$ means lowering the average of ln(1 − d) over fakes. Written as a loss the generator lowers, this is Bishop's eq. 17.9:

$$
\text{saturating:}\quad L_{\mathrm{G}}(\mathbf{w}) \;=\; \frac{1}{N_{\mathrm{synth}}} \sum_{n \in \mathrm{synth}} \ln\big(1 - d(\mathbf{g}(\mathbf{z}_n, \mathbf{w}), \phi)\big)
$$

*In words:* make the discriminator less sure that each fake is fake.

This version has a flaw that shows up whenever the critic gets well ahead of the generator, which is common early in training on images. The critic then rejects the fakes easily, and d(g(z)) sits near 0. There, ln(1 − d) is nearly flat, so the generator hardly moves. The fix used in practice is Bishop's eq. 17.10, written here as a loss the generator lowers:

$$
\text{non-saturating:}\quad L_{\mathrm{G}}(\mathbf{w}) \;=\; -\frac{1}{N_{\mathrm{synth}}} \sum_{n \in \mathrm{synth}} \ln d(\mathbf{g}(\mathbf{z}_n, \mathbf{w}), \phi)
$$

*In words:* make the discriminator sure that each fake is real. The goal is the same, but the push is strongest exactly when the generator is losing. Every GAN on this page uses it. Strictly, the game is then no longer zero-sum, because the generator's loss is no longer exactly the negative of the critic's; its resting point is the same.

```{figure} ../_static/figures/GB_Logit_Curves.png
:alt: Two curves against the critic's raw score s for a fake, from minus 6 to 6. The non-saturating loss minus ln d falls steadily from 6 to 0, with slope minus 0.99 where d is 0.01. The saturating loss ln(1 minus d) is flat near 0 on the left, slope minus 0.01, and falls only once s is large. A shaded band on the left marks d below 0.1, where the critic has got ahead of the generator.
:width: 100%

Bishop Figure 17.3, redrawn against the critic's raw score s (its logit), where the flat stretch shows. Computed from the two formulas.
```

How hard each loss pushes a fake towards "real", measured as the size of the loss's slope with respect to the critic's raw score s (both slopes are negative, so both losses push d up):

| The critic's d for a fake | Saturating push, = d | Non-saturating push, = 1 − d | How many times stronger |
| --- | --- | --- | --- |
| 0.01 (sure it is fake) | 0.01 | 0.99 | 99 |
| 0.1 | 0.1 | 0.9 | 9 |
| 0.5 (cannot tell) | 0.5 | 0.5 | 1 |
| 0.9 | 0.9 | 0.1 | 0.11 |

**Measured: a critic with a head start.** In the ordinary runs of the {ref}`six snapshots <gan-watch>` the critic never got far ahead by itself (d on fakes was 0.52 at round 0 and 0.41 at round 100), so this test forces it. On the detector pair, train the critic alone for 300 rounds against the untrained generator, whose fakes all sit near (52, 47) mph. The critic then gives real readings d = 0.98 and fakes d = 0.013, on average. From those same weights, play on with each generator loss.

| After the head start | Saturating, ln(1 − d) | Non-saturating, −ln d |
| --- | --- | --- |
| Push on one fake (average size of the loss's gradient) | 0.17 | 11.4 |
| Plain gradient descent: median distance the fakes moved in 10 rounds | 0.1 mph | 9.3 mph |
| Plain gradient descent: median distance moved in 100 rounds | 1.0 mph | 92 mph (overshot) |
| Adam: median distance moved in 10 rounds | 5.3 mph | 5.3 mph |

The saturating push is 67 times weaker. (The slope table gives about 76 at d = 0.013; the measured ratio differs because each fake has its own d. Pushes are in standardized units.) With plain gradient descent that is the whole story at the start: after 10 rounds the saturating generator has moved its fakes 0.1 mph, the non-saturating one 9.3 mph. With Adam, which every other GAN on this page uses, the two start at the same pace, because Adam divides each step by the gradient's own recent size.

Neither loss guarantees a good finish. With plain gradient descent, the stronger push overshot: by round 100 the non-saturating fakes had left the data entirely (*looks real* 0.00), and at round 3,000 they covered less of June than the slow starter did (0.44 against 0.98). The fix removes the stall at the start; it does not remove the need to choose the step size.

:::{admonition} Going deeper &mdash; where d and 1 − d come from
:class: dropdown

With d = σ(s), the chain rule gives d/ds ln(1 − σ(s)) = −σ(s) = −d, and d/ds (−ln σ(s)) = −(1 − σ(s)) = −(1 − d). Both are negative, so both losses fall as s rises: they push the same way. Only the size differs. It is the same algebra that gives a logit model's familiar gradient (y − p)x. Bishop section 17.1.2 discusses this and other fixes (least-squares GAN, instance noise, Wasserstein GAN).
:::


(gan-gradient)=
### Where the gradient goes

The two losses are lowered in two separate turns. The diagram shows what each turn changes and which way its gradient flows.

```{figure} ../_static/figures/GB_Two_Turns.png
:alt: Two vertical flows. Turn 1, the critic's turn: z, generator held fixed, fake x-tilde labelled t = 0 and real x labelled t = 1 into the discriminator, which is updated; lower E_GAN, cross-entropy, eq. 17.6; the gradient stops at the discriminator. Turn 2, the forger's turn: fresh z, generator updated, fake x-tilde with no real data this turn, discriminator held fixed, lower minus ln d(x-tilde), eq. 17.10; the gradient passes back through the fixed discriminator and the fake into the generator.
:width: 100%

The two turns of one training round (Bishop section 17.1). Dashed blue: where the gradient flows.
```

**Turn 1, the critic's turn.** The fakes are treated as fixed data, like any labelled example. The gradient of $E_{\text{GAN}}$ reaches the discriminator's weights φ and stops there. The generator is not changed.

**Turn 2, the forger's turn.** No real data is used. The chain rule runs from the loss, through the discriminator, into each fake x̃, and from there into the generator's weights w. The discriminator's weights are not stepped, but its gradient with respect to its *input* is what reaches the generator: for every fake, it says which small change would make it look more real. Backpropagation through g turns that advice into a change of w.

:::{admonition} Key idea
:class: tip

The discriminator is a loss function that learns. Its gradient with respect to its input is the generator's only teacher: the generator never sees a real heatmap.
:::


In PyTorch the two turns take five lines of code. The `.detach()` is what stops turn 1's gradient at the fake:

```python
fake = G(torch.randn(256, 2))
# turn 1: the critic. detach() = treat fakes as data
lD = bce(D(x), one) + bce(D(fake.detach()), zero)
optD.zero_grad(); lD.backward(); optD.step()
# turn 2: the forger. -ln d, only G is stepped
lG = bce(D(G(torch.randn(256, 2))), one)
optG.zero_grad(); lG.backward(); optG.step()
```

Here `bce` is binary cross-entropy on the critic's raw score, `one` and `zero` are the labels, and `x` is a batch of 256 real readings. Two things to check if you run it. Between turns, only one network's weights change. Turn 2 also leaves gradients sitting on D, which is why turn 1 starts with `optD.zero_grad()`.

(gan-training)=
## Training: two players taking turns

The key idea of a GAN is that the generator's loss is not fixed. The generator is graded by a judge who is learning at the same time, from the generator's own latest mistakes. Training is therefore a game played in rounds, not a walk downhill on one loss.

(gan-round)=
### One round, in plain steps

Bishop section 17.1 and Goodfellow et al. (2014, Algorithm 1) describe the same loop. Goodfellow writes it with k critic steps per round; both use k = 1.

```text
for round = 1, 2, 3, ...
  # critic's turn (generator held fixed)
  repeat k times:
    take 256 real readings          (t = 1)
    make 256 fakes from fresh z     (t = 0)
    one step on phi: lower E_GAN
  # forger's turn (critic held fixed)
  make 256 fakes from fresh z
  one step on w: lower -ln d(fake)
keep g; throw d away
```

The detector-pair GAN steps both networks with Adam, a version of gradient descent that scales each step by the gradient's recent size. It uses step size 0.0002 and β₁ = 0.5 (a shorter memory of past gradients than Adam's usual 0.9), the settings of the DCGAN paper (Radford et al., 2016). Each round draws a fresh batch of real readings and fresh fakes, so no batch is reused.

(gan-watch)=
### Watch the game on the detector pair

Because each reading has only two numbers, the critic's whole judgment can be drawn as a map: for every possible (upstream, downstream) pair, the probability d that it is real. The figure shows the map, the fakes, and the push each fake receives at six moments of one run.

```{figure} ../_static/figures/GB_Game_Snapshots.png
:alt: Six panels at rounds 0, 100, 300, 1,000, 3,000 and 20,000. Each shows the critic's probability d over the plane of upstream and downstream speed (orange looks fake, white cannot tell, green looks real), May readings in grey, fakes in gold and arrows for the push on 40 fakes. At round 0 the fakes are a blob near (52, 47) mph; at round 100 the map is strongly coloured and the arrows point towards green; by round 1,000 the map is nearly white and the fakes lie on thin strands through the data.
:width: 100%

Plain recipe (k = 1), seed 0. Arrows: the direction that raises ln d fastest for 40 fakes, all panels on one scale. Covers = the share of June readings with a fake close by ({ref}`Two measures <gan-measures>`); real May against real June scores 0.979.
```

- **Round 0.** The untrained generator puts every fake in a small blob near (52, 47) mph, spread under 1 mph. The untrained critic gives both real readings and fakes d = 0.52 on average.
- **Round 100.** The critic has learned something: d averages 0.68 on May readings and 0.41 on fakes. Its map is green over free flow and the queue corner, and orange over the middle and upper left, where the fakes are and real readings are not. The arrows point out of the orange and towards the green.
- **Round 300.** The fakes have been pushed into a band along the diagonal, from slow to free flow. The critic now marks the band's empty stretches in orange and the uncovered queue corner, lower right, in faint green.
- **Round 1,000.** Fakes reach all three regimes, with 4.9% in the queue corner (3.4% of May). The map is nearly flat: d averages 0.50 on both, and the median push is about a fifth of its round-100 size.
- **Rounds 3,000 to 20,000.** The critic stays between 0.49 and 0.51 on both real and fake readings for the rest of the run. Yet the fakes lie on thin strands instead of filling the clouds, and their shape changes from check to check. By round 20,000 the median push is under 1% of its round-100 size.

This is what training two networks against each other looks like. The critic paints where fakes are too many (orange) and too few (green). The generator moves its fakes up that map. The map flattens because the fakes moved, and the critic redraws it from the new fakes.

The flat map at the end is not proof that the generator has won. A critic that takes one small step per round has not learned to tell a thin strand from the cloud around it, so it says 0.5 and stops teaching. Bishop describes the same trap for mode collapse, where the generator makes only part of the data's variety: the critic "assigns the value 0.5 to these instances, and training ceases" (section 17.1.2). {ref}`When the game goes wrong <gan-balance>` shows a fix.

(gan-game)=
### Why it is a game, not a descent

Each network's loss depends on both networks' weights. When the generator improves, the critic's job gets harder and its loss rises. When the critic improves, the generator's loss rises even though its fakes did not change. So, in Bishop's words, "there is no metric of progress because the objective can go up as well as down during training" (section 17.1.2).

The game does have a resting point. If the generator's fakes come from exactly the data's distribution, the best a critic can do is say d = 0.5 everywhere. Then $E_{\text{GAN}}$ = 2 ln 2 = 1.386 and the generator's loss is −ln 0.5 = 0.693: the cannot-tell level of {ref}`the critic's loss <gan-critic-loss>`.

**The bridge: user equilibrium.** You have met this kind of resting point in traffic assignment. In Wardrop's user equilibrium, no driver can shorten their trip by switching routes alone. At the GAN's resting point, neither network can lower its own loss alone. Both are reached by iterating: the method of successive averages shifts a shrinking share of trips towards the current shortest paths, and a GAN moves each network a small step against the other's current state.

The analogy has a limit, and it matters. User equilibrium has one convex function underneath it (Beckmann's formulation), and with increasing link costs and shrinking steps the iterations descend that function to the equilibrium. The GAN game has no such function, so its steps can circle or drift instead of settling. That is exactly what the later rounds of the {ref}`six snapshots <gan-watch>` show.

:::{admonition} Going deeper &mdash; what the generator is really minimising
:class: dropdown

Hold the generator fixed. The best possible critic is the one below, where $p_{\text{data}}$ is the density of real readings and $p_G$ the density of fakes (Bishop exercise 17.1; Goodfellow et al. 2014, Proposition 1). Where the generator puts too many fakes, d⋆ is below 0.5; where it puts too few, above 0.5. That is the orange and green of the {ref}`six snapshots <gan-watch>`.

$$
d^{\star}(\mathbf{x}) \;=\; \frac{p_{\mathrm{data}}(\mathbf{x})}{p_{\mathrm{data}}(\mathbf{x}) + p_{\mathrm{G}}(\mathbf{x})}
$$

Put d⋆ back into $E_{\text{GAN}}$ and you get 2 ln 2 − 2 JS($p_{\text{data}}$, $p_G$), where JS, the Jensen-Shannon divergence, measures how different two distributions are and is zero only when they are equal. A generator that raises $E_{\text{GAN}}$ against the best critic is therefore lowering JS: pulling its distribution onto the data's. This reading is exact for the original, saturating loss; the non-saturating loss shares its resting point but not this formula. (If you work Bishop's exercise 17.1: its eq. 17.17 has the opposite sign, and it calls the sum of the two KL terms the Jensen-Shannon divergence, which is twice the JS used here.) In practice the critic is never the best possible one, which is why training can stall at 0.5 with the wrong fakes.
:::


(gan-losses)=
### Reading the losses: there is no finish line

```{figure} ../_static/figures/GB_Loss_Trace.png
:alt: Four line charts. Left, the detector pair: the critic's and generator's losses sit on the cannot-tell lines 1.386 and 0.693 from about round 500 to 20,000, while coverage below swings between about 0.2 and 0.8. Right, the course heatmap GAN: the losses stay well away from the cannot-tell lines, while both sample scores rise steadily towards the real-versus-real line.
:width: 100%

Left: the plain recipe on the detector pair, checked every 50 rounds up to round 1,000 and every 250 after, fakes scored against June. Right: the course heatmap GAN, checked every 250 rounds against the 400 validation heatmaps. Dotted line: real data scored against real data (May against June on the left; validation against test heatmaps on the right).
```

On the detector pair (left), from round 1,000 on, the critic's loss stays between 1.382 and 1.394 and the generator's between 0.674 and 0.712, a whisker from the cannot-tell levels. Over the same rounds, *covers the variety* swings between 0.16 and 0.77. The losses say "done" the whole time; the samples say otherwise.

On the heatmaps (right) it is the reverse. The critic's loss never comes near 1.386 (it ranges from 0.20 to 1.09), and the generator's ranges from 0.86 to 3.68: the critic is still winning batch by batch. Yet the samples improve steadily, to *looks real* 0.927 and *covers* 0.912 at round 6,000, against 0.945 and 0.953 when real validation heatmaps are scored against the test heatmaps.

A loss near the cannot-tell level does not mean good samples, and a loss far from it does not mean bad ones. The losses only report the balance between two players. Quality has to be measured from outside, on the samples ({ref}`Judging a GAN <gan-measures>`), and two practical rules follow:

- **Read the two outside measures together.** On the left, coverage peaked at round 150 (0.958), but at that check *looks real* was 0.27 and 57% of the fakes lay outside 0 to 80 mph. That peak is noise fooling the coverage measure ({ref}`Two measures <gan-measures>`), not a good generator.
- **Decide when to stop with a validation measure, and report it.** Keep the best checkpoint by that measure, not necessarily the last one. Choose it on held-out data (for the detector pair, some May days kept aside), never on the data you report results on.

(gan-balance)=
### When the game goes wrong, and what balance does

**The critic lags, and the fakes settle on strands.** Run the plain recipe with three seeds. At round 10,000, *covers the variety* is 0.40, 0.52 and 0.29, and over the checks at rounds 5,000 to 10,000 it never rises above 0.53. Between rounds 1,000 and 10,000 none got above 0.59. Higher readings at rounds 100 to 300 are not better generators: at those checks the looks-real score was only 0.27 to 0.85, because noisy fakes inflate coverage. From round 1,000 on, the critic's average d stayed between 0.48 and 0.52 on both real readings and fakes.

**Give the critic more turns.** Since the generator only learns what its critic can see, the obvious repair is to let the critic catch up before each generator step. With k = 5 critic steps per round, the same three seeds reach 0.73, 0.85 and 0.92 at round 10,000. Every k = 5 run beats every plain run, at three times the compute per round (6 network steps instead of 2).

```{figure} ../_static/figures/GB_Seeds.png
:alt: Left: coverage over 10,000 rounds for three seeds of the plain recipe (gold, mostly 0.2 to 0.55) and three seeds with five critic steps per round (green, mostly 0.6 to 0.95). Right: the share of fakes with a queue between the stations, near the May (3.4%) and June (2.6%) lines for all six runs.
:width: 100%

Three seeds of each recipe. Seeds 1 and 2 are checked every 100 rounds up to round 1,000 and every 1,000 after; seed 0 of each recipe every 50 rounds up to round 1,000 and every 250 after. Dotted lines: real May readings scored against June, and the May queue share; dashed line: the June queue share.
```

Two cautions. First, k = 5 helps but does not settle the game: in two of its three seeds, the lowest and highest checks between rounds 5,000 and 10,000 are still 0.33 and 0.43 apart (from 0.50 to 0.92 for seed 2). Second, the losses cannot tell the two recipes apart. At round 10,000 the critic's loss is 1.386 to 1.389 under the plain recipe and 1.382 to 1.386 under k = 5, while coverage differs by a factor of two.

```{figure} ../_static/figures/GB_Game_Snapshots_k5.png
:alt: The same six-panel layout for five critic steps per round. The critic's map is strongly coloured, with large orange and green regions, including a green corner at slow upstream and fast downstream speed where no real reading falls.
:width: 100%

k = 5, seed 0, at the same moments as the {ref}`six snapshots <gan-watch>`, except that the last panel is round 10,000.
```

With more turns, the critic has strong opinions. At round 100 it gives the queue reading (70, 18) mph d = 0.85, against 0.57 under the plain recipe, because the generator is under-producing that state (1.3% of fakes against 3.4% of May readings). A sure critic gives a strong push there, and the share of fakes in the queue corner rises to 2.4% by round 300 and 2.8% by round 1,000.

**The critic's verdict where there is no data.** Look at the last panel. The critic gives d = 0.92 at (10, 60) mph, a corner where no May reading falls: not one has upstream speed under 30 mph and downstream speed over 50. It was never shown data there, so its verdict means nothing. Yet the strongest pushes in that panel act on the slowest fakes and point left and upward, into empty space that the critic marks as real. A critic knows what real data looks like only where it has seen real data and fakes. Elsewhere it can steer the generator anywhere, which is one way a GAN produces confident nonsense.

**Rare states held up here, so check yours.** The queue between the stations survived in all six runs: 2.8% to 3.5% of fakes at round 10,000, against 3.4% of May readings and 2.6% of June. On this pair the damage was to coverage inside the common states, not to the rare one. That will not hold for every dataset. A rare state appears only a few times in each batch, so a critic that takes one step per round can be slow to learn it. Count each regime in your samples rather than assuming it is there.

**A critic that wins too early.** The {ref}`head-start test <gan-generator-loss>` shows the saturating loss's weak push, and why the optimizer matters for how much it hurts.

(gan-fixes)=
### Fixes you will meet in papers

Many GAN papers since 2014 are about keeping the game balanced. On this data, the fix that clearly helped was giving the critic more turns. Three others, each tried with one seed, lifted coverage a little (seed 1's 0.52 under the plain recipe became 0.63 to 0.64) without stopping the wandering. One seed is a hint, not a result.

| Fix | What it changes | Detector pair: covers at round 10,000 (lowest to highest, rounds 5,000 to 10,000) |
| --- | --- | --- |
| Plain recipe, for reference | nothing | 0.40, 0.52, 0.29 over three seeds (0.16 to 0.53) |
| Non-saturating generator loss (Goodfellow et al., 2014; Bishop eq. 17.10) | how hard a losing generator is pushed | used in every run here |
| Several critic steps per round, k = 5 (Goodfellow et al., 2014, Algorithm 1; Arjovsky et al., 2017 use 5) | gives the critic time to catch up | 0.73, 0.85, 0.92 over three seeds (0.50 to 0.94) |
| Critic steps 5 times larger than the generator's (two time-scale rule, Heusel et al., 2017) | the same idea, at lower cost | seed 1: 0.64 (0.48 to 0.64 at rounds 6,000, 8,000 and 10,000) |
| Gradient penalty on real readings, "R1" (Mescheder et al., 2018) | keeps the critic smooth near real data | seed 1: 0.63 (0.42 to 0.84), but looks real fell to 0.91 and the queue share rose to 6.0% |
| Step sizes shrinking to zero (cosine), the idea behind MSA | lets the game settle | seed 1: 0.63 at round 10,000 of 20,000 (0.43 to 0.63); 0.58 at the end |
| Wasserstein critic with a gradient penalty (Arjovsky et al., 2017; Gulrajani et al., 2017; Bishop eq. 17.11) | the critic outputs a score, not a probability, and the loss tracks a distance between the two distributions | not tried here |
| Spectral normalisation (Miyato et al., 2018) | caps how steep the critic can be | not tried here |

The shrinking step sizes deserve a note. They are what makes the method of successive averages converge in traffic assignment, and here they did not make the game settle within 20,000 rounds. That fits {ref}`Why it is a game <gan-game>`: assignment has a convex function underneath it, and the GAN game does not.

The Wasserstein GAN is where the word *critic* comes from. Its critic gives an unbounded score instead of a probability, and Arjovsky et al. report that its loss follows sample quality, which the original loss does not. It is a common next step when a plain GAN will not settle.

(gan-two-ways)=
## Two ways to use a critic

The critic is a loss, so it can go wherever a loss goes. The sections above used it alone, to train a generator from random numbers. It is just as often added to a loss you already have, to fix that loss's blur.

### On its own: a generator from random numbers

This is the GAN of the sections above. Nothing pairs a fake with a real example, so the critic is the only source of training signal. Use it when you want new samples and have no input to rebuild: synthetic detector days, extra training images, varied scenarios.

(gan-add-on)=
### As an add-on: sharpen a decoder that already has a target

When there is a paired target, as in an autoencoder, a translation task or super-resolution, keep the squared error and add the critic with a weight γ:

$$
L(\mathbf{w}) \;=\; \mathrm{MSE}(\hat{\mathbf{x}}_n, \mathbf{x}_n) \;+\; \gamma\,\big(-\ln d(\hat{\mathbf{x}}_n, \phi)\big), \qquad \hat{\mathbf{x}}_n = \mathbf{g}(\mathbf{e}(\mathbf{x}_n), \mathbf{w})
$$

| Symbol | Here |
| --- | --- |
| $\mathbf{x}_n$ | a real CTM heatmap to be rebuilt |
| $\mathbf{e}(\mathbf{x}_n)$ | the encoder's latents for it (4 numbers here) |
| $\hat{\mathbf{x}}_n = \mathbf{g}(\mathbf{e}(\mathbf{x}_n), \mathbf{w})$ | the decoder's rebuilt heatmap |
| MSE | mean squared error over the 400 cells, with speeds divided by 75 mph (γ is on that scale) |
| $-\ln d(\hat{\mathbf{x}}_n, \phi)$ | the non-saturating critic term of {ref}`the generator's loss <gan-generator-loss>`, computed on the rebuilt heatmap |
| $\gamma$ | how much the critic counts against the squared error; γ = 0 is a plain autoencoder |

*In words:* stay close to this heatmap, and look like real traffic. The first term keeps the output faithful to its own input. The second punishes the blur that the first term rewards. The critic is trained alongside, exactly as in the {ref}`training section <gan-training>`, with real heatmaps as t = 1 and rebuilt ones as t = 0. Here w stands for the weights of both the encoder and the decoder.

You will meet this use often, sometimes inside models that are not called GANs:

- **pix2pix** (Isola et al., 2017) translates one image into another, such as a street-scene label map into a photo, with an L1 loss plus a critic.
- **SRGAN** (Ledig et al., 2017) adds a critic to super-resolution, so upscaled images keep fine texture.
- **VAE-GAN** (Larsen et al., 2016) puts a critic on a VAE's output.
- **The autoencoder inside latent diffusion** (Rombach et al., 2022, the model behind Stable Diffusion) is "trained by combination of a perceptual loss and a patch-based adversarial objective" (their section 3.1). So the diffusion models of {doc}`4.8 <notes6-diffusion-basics>` often decode through a decoder that a critic helped train.

**Measured: the critic as an add-on, on the CTM heatmaps.** Take an autoencoder with 4 latents. Its encoder has 145,348 weights, and its decoder (154,689 weights) is the course GAN's generator with a 4-number input. Train it for 6,000 rounds with squared error alone, then again with the critic term at four weights, keeping everything else the same, seed included. Score each on the 400 test heatmaps.

```{figure} ../_static/figures/GB_Adv_AE.png
:alt: Left: front sharpness against reconstruction RMS error for five critic weights: gamma 0 at 4.28 mph and 33.3 mph; gamma 0.001 at 4.78 and 38.4; 0.003 at 5.13 and 37.9; 0.01 at 5.30 and 36.3; 0.03 at 6.17 and 38.3; a dotted line at 39.6 mph for real heatmaps. Right: three real test heatmaps, rebuilt with squared error only (softer fronts) and with gamma 0.001 (sharper fronts).
:width: 100%

Left: RMS error on the test heatmaps against front sharpness (the largest jump between neighbouring road cells, averaged over heatmaps, with speeds rounded to 3-mph bins as in the course scorecard). Right: the first three test heatmaps, rebuilt with γ = 0 and with γ = 0.001, the weight whose validation fronts came closest to real. One seed per weight.
```

Squared error alone rebuilds the heatmaps with 4.28 mph RMS error but softens their fronts to 33.3 mph, against 39.6 mph in the real ones. The smallest critic weight, γ = 0.001, lifts the fronts to 38.4 mph for 0.5 mph more error. Larger weights did not sharpen further (36.3 to 38.3 mph) and kept adding error, up to 6.17 mph at γ = 0.03.

This is the *perception-distortion trade-off* (Blau and Michaeli, 2018): an output cannot be both as close as possible to its own input and as realistic as possible, and γ picks the point between them. Which point is right depends on the job. A dashboard that must show where today's queue is wants low error. A training set for a model that detects shockwave fronts wants realistic fronts. And a sharp front is not guaranteed to sit in the right place: the critic rewards a front that looks real, and only the squared-error term ties it to this heatmap.

### Critics with a condition, and critics beyond images

The same trick works whenever you can say what "real" means.

- **Conditional GAN** (Mirza and Osindero, 2014; Bishop section 17.1). Give both networks a condition c, such as the CTM settings, the time of day or the weather. The generator makes a heatmap for that c, and the critic judges "real for this c?". This is how a GAN is steered, much as {ref}`4.8 <diffusion-steering>` steers diffusion with settings.
- **CycleGAN** (Zhu et al., 2017; Bishop section 17.2.1). Two generators and two critics translate between two collections that are not paired, such as daytime and night-time dashcam frames, with a cycle-consistency loss that makes the round trip return the original. CyCADA (Hoffman et al., 2018) used this idea to make frames from a driving video game look like real city streets (GTA5 to Cityscapes), so that a perception model trained on synthetic frames works better on real ones.
- **Adversarial imitation (GAIL)** (Ho and Ermon, 2016). The generator is a driving policy, and the critic tells human driving from the policy's driving by judging what the car does in each situation (state-action pairs). Kuefler et al. (2017) trained highway driving policies this way on NGSIM US-101 and I-80 trajectories, and found lower collision and off-road rates than the other learned policies they compared, though behavioural cloning did better over short horizons.

(gan-judging)=
## Judging a GAN from the outside, and where it breaks

Since the losses cannot judge ({ref}`Reading the losses <gan-losses>`), a GAN is judged by its samples, with the same measures used for every generator in this module.

(gan-measures)=
### Two measures and one traffic check

- **Looks real (precision).** Around each real reading, draw a small neighbourhood that reaches to its third-nearest real neighbour. *Looks real* is the share of fakes that land inside at least one of them.
- **Covers the variety (recall).** The same in reverse: neighbourhoods around the fakes, and the share of real readings that land inside one. A generator that makes one perfect reading over and over scores high on looks real and near zero on covers. That failure is *mode collapse*.
- **Traffic regimes.** The share of samples that are free at both stations, slow at both, or show a queue between, compared with the data. A model can score well on both measures and still get a rare regime wrong.

The two measures follow Kynkäänniemi et al. (2019). Here distance is in mph, with 6,048 fakes against the 6,048 June readings, as in {ref}`4.8 <diffusion-scorecard>`; the {ref}`heatmap scorecard <gan-heatmap-scorecard>` below uses the same measures on whole heatmaps. Each can be fooled, so read them together: an average fools *looks real*, and noise fools *covers* (see the table).

(gan-pair-scorecard)=
### Scorecard on the detector pair

| Generator, scored against June | Looks real | Covers the variety | Queue between (% of samples) | Slow at both (%) |
| --- | --- | --- | --- | --- |
| Real May readings (the reference) | 0.969 | 0.979 | 3.4 | 37.2 |
| One 2-D bell fitted to May | 0.712 | 0.974 | 0.5 | 27.9 |
| Squared-error generator ({ref}`no answer key <gan-no-answer-key>`) | 1.000 | 0.000 | 0.0 | 0.0 |
| GAN, plain recipe, three seeds, round 10,000 | 0.970 to 0.979 | 0.29 to 0.52 | 2.8 to 3.3 | 37.1 to 40.1 |
| GAN, k = 5, three seeds, round 10,000 | 0.967 to 0.978 | 0.73 to 0.92 | 3.2 to 3.5 | 36.4 to 37.9 |
| Diffusion, 1,000 steps ({doc}`4.8 <notes6-diffusion-basics>`) | 0.955 | 0.977 | 3.6 | 37.5 |

For comparison, June itself has 2.6% queue readings and 33.6% slow at both.

The GAN's fakes look as real as real readings do, and their regime shares are close to the data's (37 to 40% slow at both, against 37.2% in May). But even the better recipe covers less of June than diffusion does on the same pair, and how much less depends on the seed. The bell shows *covers* fooled by noise: 0.974, while 13.1% of its samples fall outside 0 to 80 mph. The squared-error generator shows *looks real* fooled by an average.

On the CTM heatmaps the picture is better for the GAN. In the {ref}`heatmap scorecard <gan-heatmap-scorecard>` below, the course GAN covers 0.900 of the test heatmaps, the same as diffusion with 1,000 steps, with fronts of 40.0 mph against 39.6 mph in real heatmaps, and its three seeds agree closely. The same method can be steady on one dataset and wander on another.

:::{admonition} Before you trust this result
:class: warning

**What is the baseline?** Real May readings scored against June (0.969 and 0.979), and diffusion on the same pair (0.955 and 0.977).

**How was the data split, and why is that honest?** Fit on May, score on June, whole weekdays, never mixed. Every GAN row is read at a fixed round, 10,000, not at its best check: picking the best check by its June score would let the test data choose the model.

**What does it do on the ugly cases?** Within one run, coverage moved by as much as 0.43 between checks at rounds 5,000 to 10,000, and it differed between seeds too, so any single number hides a range. The fakes are not copies: the median fake sits 0.12 to 0.21 mph from its nearest May reading, against 0.14 mph for real June readings. And the measures use straight-line distance in mph, so they say nothing about whether a speed pair is physically possible.
:::


(gan-heatmap-scorecard)=
### A first scorecard on the CTM heatmaps

```{figure} ../_static/figures/GenM_Lineup.png
:alt: Four rows of six heatmaps each: real test heatmaps, then the first six samples from the autoregressive transformer, the two-knob VAE and the GAN.
:width: 100%

First six samples from each model, not picked, all rounded to 3-mph bins.
```

The detector pair is one test; the course heatmaps are another, and here the GAN is scored against the first two
answers of this module. Before any numbers, look. The VAE's fronts are soft, as {doc}`4.6 <notes3b-vae-basics>`
explained. The autoregressive model of {ref}`4.1 <gen-autoregressive>` and the GAN keep them sharp. Sharpness is
the part of quality the eye judges well. Coverage, whether all the kinds of traffic in the data appear in the samples,
is the part the eye cannot judge, so it needs the table.

Every model below was trained on the same 3,200 heatmaps and is scored against the same 400 test heatmaps, with 400
samples per model and everything rounded to the same 3-mph bins.

| model | Bits per cell | Looks real | Covers variety | Front (mph) | Passes per heatmap |
|---|---|---|---|---|---|
| Real vs real (reference) | — | 0.945 | 0.953 | 38.4 | — |
| Autoregressive transformer | 0.40 | 0.907 | 0.950 | 39.1 | 400 |
| VAE, 2 knobs | bound only | 0.998 | 0.085 | 22.5 | 1 |
| VAE, 8 knobs | bound only | 0.995 | 0.453 | 26.2 | 1 |
| GAN (seed 0) | none | 0.927 | 0.900 | 40.0 | 1 |
| Local CTM-shaped rule | 0.64 | 0.020 | 0.938 | 60.9 | 20 |
| Independent marginals | 3.20 | 0.000 | 0.482 | 67.6 | 0 |

How to read it, column by column.

- **Bits per cell** exists only for models that give an exact probability, which is a real advantage of generating one
  cell at a time. The VAE gives a lower bound; the GAN gives nothing.
- **Looks real** and **covers variety** are the two measures of {ref}`Two measures <gan-measures>`. The first row, real
  validation heatmaps scored against real test heatmaps, is the reference. *Blur fools looks real:* an average heatmap
  sits close to many real ones, so the 2-knob VAE scores 0.998, above the reference, while covering only 0.085 of the
  real variety. *Noise fools covers:* very noisy samples have very large neighbourhoods, so even the independent
  marginals of {doc}`4.1 <notes1-producing>`, which never look real (0.000), cover 0.482. Read the two columns
  together, and with the front column.
- **Front** is the largest jump between road neighbours, averaged over heatmaps. Real heatmaps give 39.6 mph on the test
  set and 38.4 on the validation set, so a difference of a mile per hour or two is noise. It shows the VAE's blur as one
  number.
- **Passes per heatmap** is the cost of making one: 400 for the autoregressive model, 20 for the local rule (one per time
  step, all road cells at once), one for the VAE and the GAN.

Three findings stand out. The autoregressive model covers the variety as well as real data does (0.950 against 0.953).
The GAN is close behind on both columns. And the local rule, which scored well on bits per cell in
{ref}`4.1 <gen-autoregressive>`, makes noisy samples (fronts of 60.9 mph against a real 39.6), most likely because it
draws neighbouring road cells independently of each other: **a good likelihood does not guarantee good samples.**

Unlike the detector pair, this GAN was steady. The same code (6,000 training steps) run with three seeds ended at looks
real 0.927 to 0.945 and covers 0.892 to 0.912 against the validation heatmaps, and in the second half of training
covers stayed between 0.86 and 0.93 in all three runs.

No row wins every column, and that is the lesson to keep. Which column matters is decided by the job: coverage for a
safety-testing generator, where missing a kind of event is the dangerous failure; passes per heatmap for a what-if tool
that must answer in a second; exact probabilities for flagging unusual observations.

:::{admonition} Before you trust this result
:class: warning

**What is the baseline?** Real heatmaps scored against real heatmaps (looks real 0.945, covers 0.953) is the reference.
The independent marginals are not a clean floor (0.000 looks real but 0.482 covers), which is exactly why neither column
can be read alone.

**How was the data split, and why is that honest?** The same split of whole heatmaps throughout. No choice used the test
heatmaps: the GAN and the VAE trained for fixed lengths, the transformer kept its best validation epoch, and the test
heatmaps only report results.

**What does it do on the ugly cases?** The distance is crude: it rewards averages, and two heatmaps with the same front
shifted by one cell count as far apart. A model that copied its training data would look excellent on "looks real", so
check how close samples sit to their nearest training heatmap: real test heatmaps 3.93 mph, autoregressive 4.07, VAE
4.44, GAN 5.23. None sits closer than real data does. And the GAN row is one seed of three.
:::

(gan-breaks)=
### Where it breaks

- **It wanders, and it depends on the seed.** Report the spread over several seeds and the rule used to pick the checkpoint.
- **A lagging critic lets the fakes collapse onto strands**, while both losses sit at the cannot-tell level.
- **Off the data, the critic's verdict is arbitrary**, and it can push fakes towards states nobody observed ({ref}`When the game goes wrong <gan-balance>`).
- **There is no likelihood.** A GAN cannot say how unusual a reading is, so it cannot flag incidents or anomalies by itself. Use a model that gives probabilities: a mixture, an autoregressive model, or a VAE's bound.
- **There is no physics.** A heatmap that fools the critic can still break conservation of vehicles or show a wave moving faster than traffic allows. Check samples against traffic flow theory, as in the course's VAE lab.
- **It imitates only the data it saw.** Like the VAE, a GAN trained on May 2012 at one I-405 pair learns that site and that month. It cannot produce crash states nobody recorded, and it is not validated at another site until you test it there.

(gan-fit)=
## Fit card and applications

:::{admonition} Fit card &mdash; Generative adversarial training
:class: tip

**Idea in one sentence.** Train a generator against a learned critic, so its loss asks "does this look real?" instead of "is this close to that example?".

**Why it works.** The critic is a binary logit on real against fake. Its gradient tells each fake which way looks more real, and nothing in the loss rewards an average.

**Fits these tasks.** Sharp synthetic samples with no input to rebuild; an add-on loss that sharpens reconstruction, translation or super-resolution; unpaired translation, such as simulator frames to real-looking ones; imitating driving behaviour from trajectories. Leverage labels: *generation*, and *prediction* when the samples are futures (trajectories).

**Needs this data.** Thousands of examples of "real" (heatmaps, frames, trajectories), with no labels or pairs for the plain GAN. Also a held-out set and outside measures (looks real, covers the variety, physics checks), because the loss cannot judge, and the compute for several seeds.

**Breaks when.** Training wanders or collapses onto strands or a few kinds of output. Rare states can be under-produced, because each batch holds only a few of them (on the detector pair the queue state survived, so count yours). There is no likelihood, so it cannot score how unusual an observation is. The critic only knows what real data looked like, so it cannot certify physics (conservation of vehicles, admissible wave speeds) or corner cases nobody recorded.

**Keep the classical method when.** A calibrated simulator (CTM, SUMO) already gives the variety you need with the physics guaranteed. You need probabilities, as in crash-frequency models or extreme-value analysis of surrogate measures. You must explain *why*, since a GAN's random inputs have no physical meaning. (If you simply want sharp samples without the two-player game, the other option is a diffusion model, {doc}`4.8 <notes6-diffusion-basics>`.)
:::


**Where it is used in transportation.**

| Domain | Task | Data it needs | Classical baseline |
| --- | --- | --- | --- |
| Traffic flow | Network-wide filling of detector gaps: an LSTM generator and critic on flow and density matrices ([Liang et al., 2018](https://arxiv.org/abs/1801.03818), Seattle and San Diego loop detectors) | Loop-detector time series with gaps | Interpolation, matrix completion; their baseline was a Bayesian network |
| Driving automation | Human-like highway driving policies for simulation, by adversarial imitation ([Kuefler et al., 2017](https://arxiv.org/abs/1701.06699), NGSIM US-101 and I-80) | Vehicle trajectories (NGSIM, highD) | IDM car-following with MOBIL lane changes |
| ADAS perception | Making synthetic driving frames look real before training a segmentation model ([CyCADA, Hoffman et al., 2018](https://arxiv.org/abs/1711.03213), GTA5 to Cityscapes) | Unpaired synthetic and real frames | Collect and label more real frames; domain randomisation |
| Road safety | Several plausible future paths for each pedestrian ([Social GAN, Gupta et al., 2018](https://arxiv.org/abs/1803.10892)) | Pedestrian tracks from video | Constant-velocity and social-force models |
| Agency practice | A use to try, not yet established: a conditional GAN or a critic-sharpened decoder to enlarge a small set of post-storm road-damage photos | Labelled damage photos, by damage type | Ordinary augmentation (flips, crops, brightness); more field photos |

(gan-summary)=
## Summary and check yourself

Six things to keep.

1. **Squared error needs a partner.** A generator fed random numbers has none. Forced onto random partners, it learns the average: every output within 0.5 mph of the May average on the detector pair, every heatmap within 1.9 mph RMS of the average heatmap.
2. **A GAN learns its loss.** The discriminator is a binary logit on real against fake (Bishop eq. 17.4), and its cross-entropy is the game's score $E_{\text{GAN}}$ (eq. 17.6).
3. **One score, two players.** The critic lowers $E_{\text{GAN}}$, and in the original game the generator raises the same score. In practice the generator lowers −ln d instead (eq. 17.10), which pushes far harder when the critic is sure: 11.4 against 0.17 after a critic head start.
4. **The generator learns only through the critic.** Its one source of information about real traffic is the critic's gradient with respect to each fake. Where the critic has seen no data, that gradient can point anywhere.
5. **Training is a game with no finish line.** On the detector pair the critic's loss sat within 0.01 of the cannot-tell level (1.386) from round 1,000 on, while coverage swung between 0.16 and 0.77. Judge from outside, on held-out data, over several seeds.
6. **Balance and placement matter.** Five critic steps per round lifted coverage at round 10,000 from 0.29–0.52 to 0.73–0.92. Used as an add-on, the critic sharpened an autoencoder's fronts from 33.3 to 38.4 mph (real: 39.6) for 0.5 mph more error.

### Check yourself

1. A vendor shows sharp synthetic dashcam frames from a GAN, with a training curve whose two losses settled at 1.39 and 0.69. What does that curve tell you about the frames, and which two numbers would you ask for instead?
2. In two sentences, explain to a colleague why the autoencoder's squared error cannot train a generator that starts from random numbers.
3. You need many synthetic detector days that include the rare *queue between the stations* state, to test a ramp-metering rule. Why might a GAN under-produce that state, and how would you check whether it did?
4. A colleague's GAN on intersection trajectories gives d = 0.5 for everything after round 2,000, and they say it has converged. What do you check before agreeing?
5. Pick a method for each, and justify it: (a) rebuilding compressed probe-speed heatmaps so that their shockwave fronts stay sharp, to train a front-detection model; (b) thousands of synthetic detector days that must conserve vehicles; (c) simulator camera frames made to look real, to train a vehicle detector.
6. Your GAN looks best at round 4,000 and worse at 10,000. What do you keep, how do you choose it honestly, and what do you report?

### References

- Bishop, C. M. and Bishop, H. (2024). *Deep Learning: Foundations and Concepts*, Chapter 17. Springer. The course textbook; equation numbers on this page are Bishop's.
- Goodfellow, I. et al. (2014). [Generative adversarial nets](https://arxiv.org/abs/1406.2661). NeurIPS.
- Radford, A., Metz, L. and Chintala, S. (2016). [Unsupervised representation learning with deep convolutional GANs (DCGAN)](https://arxiv.org/abs/1511.06434). ICLR.
- Mirza, M. and Osindero, S. (2014). [Conditional generative adversarial nets](https://arxiv.org/abs/1411.1784).
- Arjovsky, M., Chintala, S. and Bottou, L. (2017). [Wasserstein GAN](https://arxiv.org/abs/1701.07875). ICML.
- Gulrajani, I. et al. (2017). [Improved training of Wasserstein GANs](https://arxiv.org/abs/1704.00028). NeurIPS.
- Heusel, M. et al. (2017). [GANs trained by a two time-scale update rule converge to a local Nash equilibrium](https://arxiv.org/abs/1706.08500). NeurIPS.
- Mescheder, L., Geiger, A. and Nowozin, S. (2018). [Which training methods for GANs do actually converge?](https://arxiv.org/abs/1801.04406) ICML.
- Miyato, T. et al. (2018). [Spectral normalization for generative adversarial networks](https://arxiv.org/abs/1802.05957). ICLR.
- Kynkäänniemi, T. et al. (2019). [Improved precision and recall metric for assessing generative models](https://arxiv.org/abs/1904.06991). NeurIPS.
- Blau, Y. and Michaeli, T. (2018). [The perception-distortion tradeoff](https://arxiv.org/abs/1711.06077). CVPR.
- Isola, P. et al. (2017). [Image-to-image translation with conditional adversarial networks (pix2pix)](https://arxiv.org/abs/1611.07004). CVPR.
- Ledig, C. et al. (2017). [Photo-realistic single image super-resolution using a GAN (SRGAN)](https://arxiv.org/abs/1609.04802). CVPR.
- Larsen, A. B. L. et al. (2016). [Autoencoding beyond pixels using a learned similarity metric (VAE-GAN)](https://arxiv.org/abs/1512.09300). ICML.
- Zhu, J.-Y. et al. (2017). [Unpaired image-to-image translation using cycle-consistent adversarial networks (CycleGAN)](https://arxiv.org/abs/1703.10593). ICCV.
- Rombach, R. et al. (2022). [High-resolution image synthesis with latent diffusion models](https://arxiv.org/abs/2112.10752). CVPR.
- Ho, J. and Ermon, S. (2016). [Generative adversarial imitation learning](https://arxiv.org/abs/1606.03476). NeurIPS.
- Hoffman, J. et al. (2018). [CyCADA: Cycle-consistent adversarial domain adaptation](https://arxiv.org/abs/1711.03213). ICML.
- Kuefler, A. et al. (2017). [Imitating driver behavior with generative adversarial networks](https://arxiv.org/abs/1701.06699). IEEE Intelligent Vehicles Symposium.
- Gupta, A. et al. (2018). [Social GAN: Socially acceptable trajectories with generative adversarial networks](https://arxiv.org/abs/1803.10892). CVPR.
- Liang, Y. et al. (2018). [A deep generative adversarial architecture for network-wide spatial-temporal traffic state estimation](https://arxiv.org/abs/1801.03818). arXiv preprint.

*Data:* PeMSD7(M) speeds from the STGCN repository (Yu, Yin and Zhu, 2018, [Spatio-temporal graph convolutional networks](https://arxiv.org/abs/1709.04875), IJCAI), I-405 N stations 717790 and 772455; CTM heatmaps from the course's cell transmission model. Every number on this page was computed by the reproducer scripts in the course folder (`genmodels/gan_basics/`), or is quoted from the course scorecard (`genmodels/numbers.json`) and {doc}`4.8 <notes6-diffusion-basics>`.

---

Next: {doc}`4.8 Diffusion models: the basics <notes6-diffusion-basics>` &mdash; the fourth answer keeps the GAN's
sharpness without the two-player game: its answer key is the noise it added itself. Back to the {doc}`Module 4 map <index>`.
