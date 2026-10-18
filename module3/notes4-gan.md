# 3.5 A forger and a critic, and a first scorecard

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 3 &middot; Section 3.5</span>
    <span class="notes-card-session">Session: Oct 22</span>
  </div>
  <p class="notes-card-lede">The third answer removes squared error altogether: a forger network makes heatmaps and a critic network tries to tell them from real ones. Then the first three answers are scored side by side on the same 400 held-out heatmaps, with measures that work for any generator, including one that gives no probabilities at all.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Read it before</h4>
      <ul>
      <li><a href="notes3-vae.html">3.4 A few hidden knobs: the VAE</a></li>
      </ul>
    </div>
    <div>
      <h4>Next session</h4>
      <ul><li><a href="../labs.html">Forward and reverse diffusion; training the denoiser</a></li></ul>
    </div>
  </div>
</div>

## What this section covers

- The forger-and-critic setup, and why it keeps fronts sharp
- The two-player loss, and what it means that it has no finish line
- Two measures for any generator: does it look real, and does it cover the variety?
- Whether a GAN's quality holds up across runs of the same code
- A scorecard for the first three answers, and the two ways its measures can be fooled
- Where you will meet GANs in transportation papers

## Remove the squared error

```{figure} ../_static/figures/GenGAN_Forger_Critic.png
:alt: Random numbers go into a forger that makes a fake heatmap. A fake and a real heatmap go into a critic that outputs the probability the heatmap is real. Dashed arrows: the forger is trained to fool the critic; the critic is trained to catch fakes.
:width: 100%

Two networks trained against each other. Nothing in the loss rewards an average.
```

Section 3.4 ended on a diagnosis: squared error rewards the average, and the average of sharp fronts is
a soft one. A generative adversarial network (GAN) removes squared error from the picture.

It has two networks. The **forger** (the *generator*, 244,289 weights here) takes 32 random
numbers and turns them into a heatmap. The **critic** (the *discriminator*, 135,745 weights)
looks at a heatmap and outputs the probability that it is real. They train in turns: the critic is
shown real heatmaps and the forger's fakes and learns to tell them apart; the forger learns to make
heatmaps the critic calls real.

No cell is ever compared with a "correct" value, so there is nothing to average. A blurry heatmap is
exactly the kind of thing a critic learns to catch, so blur is punished rather than rewarded. In traffic
terms the critic is a calibration check that learns what to look at: like an engineer comparing a
simulated speed contour with an observed one and saying *that one is not real*.

## The loss is a two-player game

$$
\min_G \; \max_D \;\; \mathbb{E}_{x \sim \text{data}}\big[\log D(x)\big] + \mathbb{E}_{z}\big[\log\big(1 - D(G(z))\big)\big]
$$

| symbol | here |
|---|---|
| $G$ | the forger (generator) |
| $D(x)$ | the critic's probability that heatmap $x$ is real |
| $z$ | 32 random numbers, drawn fresh each time |
| $G(z)$ | a fake heatmap |

*In words:* the critic scores points for calling real heatmaps real and fakes fake; the forger scores
points whenever the critic is wrong.

This is a game, not a hill to walk down. Each network's loss depends on the other, and a forger that is
improving can see its loss go *up* because the critic improved faster. The practical consequence is the
one that matters: **the loss does not tell you when you are done, or how good the samples are.**

:::{admonition} Going deeper &mdash; the loss that is actually trained
:class: dropdown
Early in training the critic wins easily, $D(G(z)) \approx 0$, and $\log(1 - D(G(z)))$ is nearly flat when
measured against the critic's raw score (before it is turned into a probability), so
the forger gets almost no gradient. In practice the forger instead maximises $\log D(G(z))$, the
"non-saturating" loss, which has the same goal and a strong gradient when the forger is losing. That is
the version trained on this page. Goodfellow et al. (2014), *Generative adversarial nets*, &sect;3.
:::

## Two measures for any generator

Without a meaningful loss, a GAN has to be judged from outside, by its samples. Two measures are
standard, and they work for every generator in this module, including ones that give no probabilities.

**Looks real (precision).** Around each real heatmap, draw a small neighbourhood: a ball reaching to its
third-nearest real neighbour. *Looks real* is the share of generated heatmaps that land inside at least
one of those neighbourhoods.

**Covers the variety (recall).** Do the same in reverse: neighbourhoods around generated heatmaps, and
the share of *real* heatmaps that land inside one. A forger that makes one perfect heatmap over and over
scores high on looks real and low on covers the variety. That failure has a name, *mode collapse*, and
it is the classic way GANs go wrong.

Distance between two heatmaps is the RMS difference in speed per cell, in mph, on the 3-mph grid. This
follows Kynkäänniemi et al. (2019), *Improved precision and recall metric for assessing generative
models*. To know what a good score is, score real heatmaps against real heatmaps the same way: that is the
reference. A model should land near it; a score far *above* it is a warning sign, not a triumph.

## Same code, three runs

```{figure} ../_static/figures/GenGAN_Trace.png
:alt: Two line charts over 6,000 training steps for three random seeds: looks real (precision) and covers the variety (recall), with a dashed line for real data scored the same way.
:width: 100%

The same GAN code run three times, scored on the validation heatmaps every 250 steps.
```

The same GAN (6,000 training steps) was run three times, changing only the random seed, and
scored on the validation heatmaps every 250 steps. At the end of training, looks real ranged from 0.927 to 0.945 across the three seeds and covers the variety from 0.892 to 0.912. Within the second half of training, across all three seeds, covers the variety moved between 0.86 and 0.93 from one check to the next.

On this data the runs agreed closely and none collapsed. GANs are known for unstable training on harder
problems (larger images, more varied data, longer runs), and this small, smooth dataset with a standard
recipe did not trigger it. Two lessons hold anyway. The loss told us none of this; only the outside
measures did, so *when* to stop is a decision made on validation data and reported. And we only know
that the runs agree because there were three: the spread across seeds belongs in any report of GAN
performance, including a vendor's.

## Three answers, side by side

```{figure} ../_static/figures/GenM_Lineup.png
:alt: Four rows of six heatmaps each: real test heatmaps, then the first six samples from the autoregressive transformer, the two-knob VAE and the GAN.
:width: 100%

First six samples from each model, not picked, all rounded to 3-mph bins.
```

Before any numbers, look. The VAE's fronts are soft, as section 3.4 explained. The autoregressive model and the
GAN keep them sharp. Sharpness is the part of quality the eye judges well. Coverage, whether all the
kinds of traffic in the data appear in the samples, is the part the eye cannot judge, so it needs the
table.

## A first scorecard

Every model below was trained on the same 3,200 heatmaps and is scored against the same
400 test heatmaps, with 400 samples per model and everything rounded to the same 3-mph bins.

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

- **Bits per cell** exists only for models that give an exact probability, which is a real advantage of
  generating one cell at a time. The VAE gives a lower bound; the GAN gives nothing.
- **Looks real** and **covers variety** are the two measures above. The first row, real validation
  heatmaps scored against real test heatmaps, is the reference. Every model row is scored against the test heatmaps too, which is why the GAN reads 0.900 on covers here but ended at 0.912 in the training plot, where it was scored against the validation heatmaps. Each measure has a characteristic way to be
  fooled. *Blur fools looks real:* an average heatmap sits close to many real ones, so the 2-knob VAE
  scores 0.998, above the reference, while covering only 0.085 of the
  real variety. *Noise fools covers:* very noisy samples have very large neighbourhoods, so even the
  independent marginals from section 3.1, which never look real (0.000), cover
  0.482. Read the two columns together, and with the front column.
- **Front** is the largest jump between road neighbours, averaged over heatmaps. Real heatmaps give
  39.6 mph on the test set and 38.4 on the validation set, so a
  difference of a mile per hour or two is noise. It shows the VAE's blur as one number.
- **Passes per heatmap** is the cost of making one: 400 for the
  autoregressive model, 20 for the local rule (one per time step, all road cells at once), one for the
  VAE and the GAN.

Three findings stand out. The autoregressive model covers the variety as well as real data does
(0.950 against 0.953). The GAN is close behind on both columns. And
the local rule, which scored well on bits per cell in section 3.2, makes noisy samples (fronts of
60.9 mph against a real 39.6), most likely because it draws
neighbouring road cells independently of each other: **a good likelihood does not guarantee good samples.** Its
high coverage (0.938) is the same noise effect as the marginals', which is why it sits so close
to the transformer's in that one column.

No row wins every column, and that is the lesson to keep. Which column matters is decided by the job:
coverage for a safety-testing generator, where missing a kind of event is the dangerous failure; passes
per heatmap for a what-if tool that must answer in a second; exact probabilities for flagging unusual
observations.

:::{admonition} Before you trust this result
:class: warning
**What is the baseline?** Real heatmaps scored against real heatmaps (looks real
0.945, covers 0.953) is the reference. The independent
marginals are not a clean floor (0.000 looks real but 0.482
covers), which is exactly why neither column can be read alone.

**How was the data split, and why is that honest?** The same split of whole heatmaps throughout. No choice used the test heatmaps: the GAN and the VAE trained
for fixed lengths, the transformer kept its best validation epoch, and the test heatmaps only report results.

**What does it do on the ugly cases?** The distance is crude: it rewards averages, and two heatmaps
with the same front shifted by one cell count as far apart. A model that copied its training data would look excellent on "looks
real", so check how close samples sit to their nearest training heatmap: real test heatmaps
3.93 mph, autoregressive 4.07, VAE 4.44,
GAN 5.23. None sits closer than real data does. And the GAN row is one seed of three.
:::

:::{admonition} Fit card &mdash; Generative adversarial network (GAN)
:class: tip
**Idea in one sentence.** Train a forger against a critic until the forger's fakes are hard to tell from
real data.

**Why it works.** The critic punishes anything that looks fake, blur included, so nothing in training
rewards an average.

**Fits these tasks.** Sharp synthetic data and data augmentation; trajectory generation, where Social GAN
(Gupta et al., 2018) is the best-known example; filling gaps in detector data (*generation*).

**Needs this data.** Thousands of examples, several training runs, and outside measures (precision and
recall, physics checks) to judge quality, because the loss will not.

**Breaks when.** Training wanders or collapses onto a few kinds of output on harder data (on this data
three seeds agreed); there is no likelihood to compare models with or to score how unusual an
observation is.

**Keep the classical method when.** A calibrated simulator already gives the variety you need, or you
need probabilities.
:::

## Where you will meet GANs

Transportation papers used GANs widely from about 2018 to 2022: for predicting pedestrian and vehicle
trajectories, for imputing missing detector data, and for generating driving scenarios. Read those
papers with this section's questions: what is the coverage, against what reference, and how many seeds?
For image generation, diffusion models have largely replaced GANs, and next session shows why: they keep
the GAN's sharpness without the two-player game.

## Check yourself

1. A vendor shows sharp, realistic synthetic trajectories from a GAN. Which two numbers do you ask for,
   and what would make you suspicious?
2. Pick a method for each, and justify it: (a) filling a 30-minute detector gap; (b) varied incident
   scenarios for training operators; (c) a what-if tool that must answer within a second.
3. Your GAN looks better at step 4,000 than at 6,000. What do you keep, and what do you report?

---

Next session: diffusion, the fourth answer &mdash; start from pure noise and clean it up step by step.
