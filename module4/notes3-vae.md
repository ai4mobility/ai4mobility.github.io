# 4.4 A few hidden knobs: the variational autoencoder

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 4 &middot; Section 4.4</span>
    <span class="notes-card-session">Session: Generative models, part 1</span>
  </div>
  <p class="notes-card-lede">The second answer: compress each heatmap into a few hidden numbers, learn to rebuild it from them, and make new heatmaps by drawing new numbers. A new heatmap now takes one pass instead of 400. With no labels, its knobs line up clearly with one of the simulator's own knobs and partly with another, and its blur can be measured and explained.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Read it before</h4>
      <ul>
      <li><a href="notes2-autoregressive.html">4.2 One cell at a time</a></li>
      <li><a href="notes2b-latent-variables.html">4.3 Latent variables: hidden causes, not hidden layers</a></li>
      </ul>
    </div>
    <div>
      <h4>Labs that go with it</h4>
      <ul><li><a href="../labs.html">VAE on traffic heatmaps; From VAE to diffusion</a></li></ul>
    </div>
  </div>
</div>

## What this section covers

- Macroscopic state reduction as the idea behind a latent-variable model
- The VAE's shape: an encoder that squeezes, a decoder that expands, and why the knobs need a spread
- The two-term loss, and what each term buys
- What the knobs learned on this data, checked against the simulator's real knobs
- Why the VAE blurs, measured: the decoder returns an average
- Whether more knobs fix it, and how the VAE compares with plain PCA
- How the knobs change when the training traffic changes, and what that means for collecting data (interactive companion)

## You already compress traffic states

```{figure} ../_static/figures/GenVAE_Five_Knobs.png
:alt: Five dials, starting density, upstream inflow, bottleneck capacity, bottleneck start and bottleneck length, feeding a CTM that produces a 400-number heatmap. A card asks whether a VAE given only the 400 numbers can find knobs like these.
:width: 100%

Every heatmap in this dataset was made by five knobs and a little noise.
```

Traffic engineering has always summarised a corridor with a few numbers. A fundamental diagram is three
parameters: free-flow speed, wave speed and jam density. A level of service is one letter. That habit
rests on a physical fact: because of conservation and the fundamental diagram, most of the numbers you
could measure on a road are decided by a few causes.

This dataset is the extreme case. Each heatmap was produced by the CTM from five knobs, drawn at random
for each run:

| knob | range in this dataset |
|---|---|
| starting density | 5&ndash;55% of jam density, plus cell-to-cell noise |
| upstream inflow | 45&ndash;95% of capacity (2,500 veh/h) |
| bottleneck capacity | 20&ndash;100% of capacity, at the downstream end |
| bottleneck starts | 1.6&ndash;5.5 minutes into the run |
| bottleneck lasts | 1.6&ndash;4.3 minutes |

Five numbers in, 400 out. Now suppose you were handed only the 400 numbers, with no
labels and no physics. Could a network find knobs like these by itself, and then turn new knob settings
into new heatmaps? That is the bet of a *latent-variable model*, and the variational autoencoder (VAE)
is the standard way to make it.

## Squeeze, then expand

```{figure} ../_static/figures/GenVAE_Hourglass.png
:alt: A real heatmap enters an encoder that narrows to two knobs; a decoder widens back to a 400-number reconstruction. To the right, generating: draw two numbers from a bell curve and run only the decoder.
:width: 100%

The VAE from the lab: 400 &rarr; 96 &rarr; 2 &rarr; 96 &rarr; 400. To generate, skip the encoder.
```

The VAE has two halves. The **encoder** squeezes a heatmap's 400 numbers through a hidden
layer of 96 down to 2 numbers, the *knobs* (in papers, the *latent variables* $z$). The **decoder**
expands 2 numbers back to 400. Training asks the decoder to rebuild the encoder's input, so the
two knobs are forced to carry whatever matters most about the heatmap.

**Why each knob has a spread as well as a value.** For every heatmap the encoder outputs a mean and a
spread for each knob: a small bell curve rather than a point. Training draws the knobs from that bell
curve before decoding. A plain autoencoder, with points only, is free to put each training heatmap at
its own isolated spot, and the space between spots means nothing. Spreads force nearby knob values to decode to similar heatmaps, because the KL term in the loss (below) stops
the encoder from shrinking the spreads to zero; so the whole knob space becomes usable.

**Generating.** Throw the encoder away. Draw two numbers from a standard bell curve, run the decoder
once, and you have a new heatmap. One forward pass, against 400 for the
autoregressive model of section 4.2.

## The loss: rebuild well, keep the knobs findable

$$
\text{loss} = \tfrac{1}{2} \sum_{i=1}^{400} (\hat{x}_i - x_i)^2 \;+\; \beta \cdot \mathrm{KL}\big(q(z \mid x)\,\|\,\mathcal{N}(0, I)\big)
$$

| symbol | in this heatmap |
|---|---|
| $x_i,\ \hat{x}_i$ | real and rebuilt speed in cell $i$, divided by 75 mph |
| $z$ | the 2 knobs |
| $q(z \mid x)$ | the bell curve the encoder puts the knobs in for heatmap $x$ |
| $\mathcal{N}(0, I)$ | a standard bell curve |
| $\beta$ | the weight on the second term: 0.6 in the lab |

*In words:* rebuild the heatmap well, but keep every heatmap's knobs inside one standard bell curve, so
that drawing from that bell curve later gives knobs the decoder knows what to do with.

The two terms pull against each other. The first wants as much detail as possible packed into the knobs.
The second, the KL divergence, charges for every heatmap whose knob bell curve strays from the standard
one. $\beta$ sets the exchange rate: raise it and the knob space gets tidier while rebuilds get worse.
The VAE-to-diffusion lab sweeps $\beta$ and measures the trade.

:::{admonition} Going deeper &mdash; where the loss comes from
:class: dropdown
The goal is to maximise $\log p(x)$, the probability of the real heatmaps, which cannot be computed
directly for a VAE. It has a lower bound, the *evidence lower bound* (ELBO):
$\log p(x) \ge \mathbb{E}_{q(z \mid x)}[\log p(x \mid z)] - \mathrm{KL}(q(z \mid x)\,\|\,p(z))$.
If the decoder is read as a Gaussian with fixed spread, $\log p(x \mid z)$ becomes a squared error, which
is the first term above. The lab reweights the KL term by $\beta$, so with $\beta$ = 0.6 the loss is not
exactly the negative ELBO; it leans toward detail. Kingma &amp; Welling (2014),
*Auto-encoding variational Bayes*. One consequence: a VAE gives a *bound* on the likelihood, not an exact
value, so it cannot be put on the bits-per-cell ladder of section 4.2.
:::

## What the knobs found

```{figure} ../_static/figures/GenVAE_Found_Knobs.png
:alt: Two scatter plots of the 400 test heatmaps in the two-knob space. Left, coloured by starting density, which changes smoothly along knob 1. Right, coloured by bottleneck capacity, which changes partly along knob 2.
:width: 100%

The encoder never saw the simulator's knobs. One shows up clearly, one partly.
```

To keep the test honest, the lab's architecture was retrained on the 3,200 training heatmaps
only (77,972 weights, $\beta$ = 0.6). Each dot is one of the 400 test
heatmaps, placed by the two knob values its encoder gives it, and coloured by a knob of the simulator
that made it.

- **Knob 1 tracks starting density**, correlation -0.94; the two knobs together
  explain 90% of its variance. It also tracks
  the heatmap's mean speed (+0.97): how congested the road is overall.
- **Knob 2 partly tracks bottleneck capacity**, correlation -0.57; the two
  knobs together explain 32% of its variance.
- **Upstream inflow is missing.** The best straight-line read-out of inflow from both knobs explains
  5% of its variance.

Nobody told the network about density or bottlenecks. Two knobs cannot hold five causes, and which ones it
kept was not chosen by us. Inflow is not invisible: below capacity it does not change the free-flow speed, but
it does change how fast queues grow and clear, and section 4.3 shows that one heatmap cuts its uncertainty roughly
in half. With two knobs it loses out to bigger causes; with eight, the VAE explains 43% of its variance. The
dataset does not store when the bottleneck starts or how long it lasts; section 4.3 regenerates both, and two
knobs explain 16% and 1% of their variance. The core idea still holds: a compression of the traffic state was
learned rather than written down.

Two cautions before anyone builds a "congestion index" on knob 1. The knobs have no fixed direction:
retrain the model and knob 1 may come out flipped or rotated into knob 2. And a learned knob has to
be compared against the obvious physical quantity, here mean speed, which may do the job more simply.

## Why the VAE blurs: the decoder returns an average

```{figure} ../_static/figures/GenVAE_Averaging.png
:alt: Four training heatmaps with fronts in different places, the average of twenty such heatmaps with a smeared front, and the decoder's output at the same knob values, which looks like the average.
:width: 100%

The decoder's output looks like the average of the heatmaps that share its knobs, not like any one of them. The
example is one of 200 random knob settings: among those where the decoder sits closest to its neighbours'
average, the one whose neighbours differ most.
```

VAE samples look soft. On this data the reason can be measured. Pick a knob setting, and find the
20 training heatmaps whose encoded knobs lie closest to it. Two knobs cannot pin down
everything, so those neighbours differ: their fronts sit in different places. Average them and the front
smears. Then decode the knob setting itself.

Over 200 random knob settings, the decoder's output was **2.98 mph** (median RMS per
cell) from the average of its 20 neighbours, but **8.68 mph** from a typical single
neighbour. Is that just because anything near a group sits close to the group's average? Check a real member:
a real neighbour sits 7.86 mph from the average of the other nineteen, and
11.18 mph from a typical one. The decoder is far closer to the average than any real member
is. The decoder produces the average.

That is not a training bug; it is what the loss asks for. If you must give one answer for a set of
possibilities and you are scored by squared error, the best answer is their average: the *conditional
mean*. Wherever the knobs leave something open, such as exactly where a queue front sits, the decoder
averages the possibilities, and an average of sharp fronts is a soft one. This is the same reason a
regression would have predicted 45 mph for the cell in section 4.2 that was either jammed or free.

When does it matter? An averaged forecast is often useful. It is harmful when the timing or position of
a front is the point: queue-spillback warnings, signal plans, incident detection. The average of "the
queue reaches the ramp" and "it does not" is a moderate slowdown that never happens.

## Is the blur just too few knobs?

A fair objection is that two knobs are simply too few. The same VAE was trained again with eight.

| rebuilding the 400 test heatmaps | RMS error per cell |
|---|---|
| the average heatmap, for every heatmap | 23.76 mph |
| PCA, 2 components | 9.85 mph |
| VAE, 2 knobs | 7.68 mph |
| PCA, 8 components | 4.91 mph |
| VAE, 8 knobs | 5.50 mph |

With two knobs the VAE rebuilds better than two-component PCA: the nonlinear decoder earns something.
With eight, plain PCA wins. The KL term costs the VAE accuracy; what it buys is a knob space you can
sample from. If all you need is compression, PCA is deterministic, instant, and its components never
flip between runs.

Rebuilding a heatmap you already have is not the same as making a new one. (A VAE "sample" here is the
decoder's output for randomly drawn knobs, so it is itself an average.) For new samples the
question is whether fronts stay sharp. *Front sharpness* here is the largest jump between road
neighbours in each heatmap, averaged over heatmaps, with everything rounded to the same 3-mph bins:

| | front sharpness |
|---|---|
| real test heatmaps | 39.6 mph |
| VAE, 2 knobs: rebuilt test heatmaps | 20.9 mph |
| VAE, 2 knobs: new samples | 22.5 mph |
| VAE, 8 knobs: new samples | 26.2 mph |

Both VAEs' samples have fronts well below the real 39.6 mph (22.5 and 26.2). More knobs rebuild better, but a new sample is still the decoder's average over whatever the knobs leave open.

:::{admonition} Before you trust this result
:class: warning
**What is the baseline?** For a compressor, the average heatmap (23.76 mph) and PCA with
the same number of components (9.85 and 4.91 mph). The VAE beats PCA
with 2 knobs and loses to it with 8.

**How was the data split, and why is that honest?** The same 3,200 / 400 /
400 split of whole heatmaps as section 4.2. The VAE in the lab was trained on all
4,000; the one on this page was retrained on the training heatmaps only, for a fixed 300 epochs, so the knob and
rebuild results are on heatmaps it never saw. No choice used the test heatmaps; they only report results.

**What does it do on the ugly cases?** New samples have softer fronts than real heatmaps. One of the
simulator's five causes, inflow, is invisible in the knobs. The knob directions are arbitrary and can
change between training runs. And as everywhere in this module, this is one simulator on one road.
:::

:::{admonition} Fit card &mdash; Variational autoencoder (VAE)
:class: tip
**Idea in one sentence.** Compress each example to a few knobs, learn to rebuild it from them, then
generate by drawing new knobs.

**Why it works.** The bottleneck forces the knobs to keep what varies most; the bell-curve term makes
the knob space safe to sample from.

**Fits these tasks.** Fast generation (one pass), compression, scenario exploration by turning knobs,
and anomaly flags: a heatmap the VAE cannot rebuild is unlike anything it trained on, a cheap way to
catch sensor faults or unusual incidents (*generation*, *extraction*).

**Needs this data.** Thousands of unlabelled examples from detector or trajectory archives, and a
rebuild error that matches what you care about.

**Breaks when.** The knobs do not pin down the details, so outputs are averages (soft fronts); knobs are
asked to mean something physical, which nothing guarantees.

**Keep the classical method when.** You already know the knobs (a calibrated CTM, a fundamental
diagram), or PCA's compression is good enough, as it is here at 8 components.
:::

(same-vae-different-traffic)=
## Same VAE, different traffic: the knobs depend on the data

Everything above used one dataset. What the knobs mean, how many of them get used, and what the model
generates all depend on the traffic it was trained on. The companion below trains one plain VAE
($\beta$ = 1) on 1,008-cell snapshots of the course's torus-grid network simulator: on light traffic,
on heavy congestion, on both, and on a mix where congestion is only 5% of the data. It then compares the
latent maps those diets produce. Its last tabs turn the results into rules for collecting VAE training data.

Four results to look for:

- One knob tracks the load every time, much like knob 1 above. The other knob picks up whatever pattern
  is left over: most often the signal clock in light traffic, and where the jam sits in heavy traffic.
- A light-only model throws heavy snapshots far outside the bell. A heavy-only model keeps light snapshots
  near its centre and still rebuilds them badly. The score, not the position on the map, is the alarm.
- With congestion at 5% of the training data, only 1.3&ndash;1.8% of generated networks are congested.
- With no near-capacity data, the model does worse on near-capacity traffic than a per-cell average table.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion &mdash; Same VAE, different traffic</span>
    <a href="../_static/companions/Same_VAE_Different_Traffic_Companion.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/Same_VAE_Different_Traffic_Companion.html"
          title="Same VAE, different traffic: how the training data shape a VAE's latent space" loading="lazy"></iframe>
</div>

## Check yourself

1. You need 1,000 synthetic corridor-days for a capacity study within an hour of computing. A VAE or
   the autoregressive model of section 4.2? What would you check before using the output?
2. Your VAE's samples look smooth and believable. A reviewer asks whether the queue fronts are
   realistic. What do you measure, and against what?
3. An agency wants each knob to mean something physical. When does that matter, and what could you do
   about it?
4. Your detector archive is 80% overnight free flow. What will a VAE trained on it generate, and what
   would you change in the data before training? (The companion's tabs 6 and 7 help.)

---

Next: {doc}`notes4-gan` &mdash; the third answer removes squared error altogether.
