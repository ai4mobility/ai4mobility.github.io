# 4.9 One hidden cause: mixture models

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 4 &middot; Section 4.9</span>
    <span class="notes-card-session">Session: VAE and diffusion</span>
  </div>
  <p class="notes-card-lede">Before the VAE and diffusion, the simplest model with a hidden cause. A real detector's speeds come from two traffic regimes the detector never records; a mixture model finds them, guesses which one made each reading, and makes new readings in two steps. The same recipe, scaled to the 400-cell heatmaps, shows exactly why a single hidden label is not enough, and sets up the VAE and diffusion as two better choices of hidden cause.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Read it before</h4>
      <ul>
      <li><a href="notes1-producing.html">4.1 From predicting to producing</a></li>
      <li><a href="notes2b-latent-variables.html">4.3 Latent variables: hidden causes, not hidden layers</a></li>
      <li><a href="notes3-vae.html">4.7 A few hidden knobs: the VAE</a></li>
      </ul>
    </div>
    <div>
      <h4>Labs that go with it</h4>
      <ul><li>None for this section; the diffusion labs follow it</li></ul>
    </div>
  </div>
</div>

## What this section covers

- A real detector's speeds, and why one bell curve describes them badly
- The two-step recipe: draw a hidden cause, then draw the data from it
- The soft guess: which hidden cause made this reading?
- Fitting without labels: the EM loop
- The same idea on the 400-cell CTM heatmaps, and where it breaks
- One recipe, three hidden causes: the mixture, the VAE and diffusion side by side

## One detector, two kinds of traffic

```{figure} ../_static/figures/GenMix_Two_Humps.png
:alt: A histogram of five-minute speeds at one detector, with a narrow hump near 70 mph and a wide hump from about 10 to 40 mph. A single dashed bell curve peaks near 48 mph, where the data has almost no readings. Two solid bell curves, one per hump, follow the data. A side panel compares the share of June readings between 43 and 53 mph with what each model predicts.
:width: 100%

One detector on I-405 northbound in Los Angeles, May 2012. One bell curve puts its peak where the road almost never is.
```

The data is one loop detector from Caltrans PeMS, District 7, as packaged by the authors of the STGCN paper (Yu,
Yin &amp; Zhu, 2018): station 772455 on I-405 northbound in Los Angeles, one average speed every five
minutes, on the 44 weekdays of May and June 2012. Of the 228 stations in that dataset it is the most congested:
43% of its readings are below 40 mph, against 11%
for the median station. That is the whole selection rule. Everything below is fitted on the 23 weekdays of
May (6,624 readings) and checked on the 21 weekdays of June (6,048), a later month
the model never saw.

The histogram has two humps: a narrow one near 70 mph and a wide one from about 10 to 40. Summarise it the
usual way, with a mean and a standard deviation, and you have in effect fitted one bell curve:
48.4 &plusmn; 22.9 mph. Its most likely speed, about 48 mph, is
one of the rarest speeds at this detector. In June, only **2.6%** of readings fell
within 5 mph of it (43&ndash;53 mph). The bell curve predicts
**17%**.

Fit two bell curves instead, one per hump:

| regime | share of readings | mean | spread |
|---|---|---|---|
| congested | 52% | 28.4 mph | 13.0 mph |
| free flow | 48% | 70.2 mph | 2.0 mph |

The two-regime model predicts 5.1% of June readings in that 10-mph band. That is closer to
the real 2.6%, but still about twice too many: the congested hump is not really bell-shaped.
Every reading came from one regime or the other, but the detector never records which. That missing piece of
information is a **hidden cause** (in papers, a *latent variable*).

## Make a reading in two steps

```{figure} ../_static/figures/GenMix_Two_Steps.png
:alt: Three boxes. Step 1, roll for the regime, shows a bar split 52 percent congested and 48 percent free flow. Step 2 draws a speed from that regime's bell curve. The result is a recorded speed. Below, the first eight draws of the recipe with the hidden regime above and the recorded speed below, and the share below 40 mph for June, the recipe and one bell curve.
:width: 100%

How the model thinks the data was made. The top row of draws is hidden in real data; the detector only records the bottom row.
```

A model with a hidden cause describes how the data could have been made, in two steps:

1. Draw the hidden cause: roll a weighted die for the regime, congested 52% of the time and
   free flow 48%.
2. Draw the data from that cause: a speed from that regime's bell curve.

Run the recipe 6,048 times, as many readings as the June weekdays hold, and
42.9% of the made-up readings are below 40 mph, against
40.5% in June and 35.4% for one bell curve. The model stores
no readings at all, only five numbers: one share, two means and two spreads.

Written as one line, the probability of a reading adds up every way it could have been made:

$$
p(x) = \sum_{k} \pi_k \, p(x \mid k)
$$

| symbol | at this detector |
|---|---|
| $x$ | one five-minute speed reading, mph |
| $k$ | the regime, congested or free flow; hidden |
| $\pi_k$ | the share of readings from regime $k$: 0.52 and 0.48 |
| $p(x \mid k)$ | regime $k$'s bell curve: 28 &plusmn; 13 or 70 &plusmn; 2 mph |

*In words:* a reading could have come from either regime, so its probability is the sum over both routes:
how often the regime happens, times how likely this speed is under that regime.

**You may have used this already.** A *latent class choice model* has exactly this form. Travellers belong to
classes you cannot observe; $\pi_k$ is the share of each class, and $p(x \mid k)$ is that class's own logit model
of the choice $x$. A mixture of bell curves is the same idea with speeds in place of choices.

## Which regime made this reading?

```{figure} ../_static/figures/GenMix_Soft_Guess.png
:alt: Left, the probability that a reading came from the congested regime, plotted against speed. It stays near 100 percent up to about 62 mph and drops to near zero by 66 mph, crossing 50 percent at 63.7 mph. Right, the average of that probability by hour of day over the June weekdays, near zero overnight, high from 7 am to about 7 pm.
:width: 100%

The soft guess. It is a probability, not a label, and it was never shown the time of day.
```

The recipe runs forwards, from regime to speed. Bayes' rule runs it backwards: given a speed, how likely is each
regime to have made it?

$$
P(k \mid x) = \frac{\pi_k \, p(x \mid k)}{\sum_j \pi_j \, p(x \mid j)}
$$

For each regime, multiply how often it happens by how likely this speed is under its bell curve, then rescale so
the regimes add to one. At this detector a 30 mph reading is congested with probability 100%
and a 70 mph reading with probability 0.1%. The uncertain readings are a narrow band near the
50/50 point, **63.7 mph**: 63 mph gives 78%, 64 mph gives
35%. The band is narrow because free flow at this detector is tight,
70 &plusmn; 2 mph, so even 60 mph is far more likely to be a congested
reading. Over the June readings, 95% get a guess above 99% one way or the other,
and only 1.0% land between 20% and 80%.

The output is a probability for each regime, a **soft label**, not a hard one. That matters for the fitting loop
below, and it is the same kind of object as the VAE encoder's output in section 4.7.

**A check the model could not cheat on.** The model never saw the time of day. Average its soft guess over the
21 June weekdays, hour by hour: it is at most 1% overnight,
70% from 6 to 7 am, above 97% from 7 am to 4 pm, at least
76% until 7 pm, and 34% from 7 to 8 pm. It found this road's
peak periods from speeds alone. Like the VAE's knobs in section 4.7, the hidden cause it learned lines up with
something real, though nobody labelled it.

## Fitting without labels: the EM loop

```{figure} ../_static/figures/GenMix_EM_Loop.png
:alt: Left, a loop: start with a poor guess, E-step guess soft labels, M-step refit each regime, repeat. Right, the mean speed of the two regimes plotted against iteration. Starting at 45 and 55 mph they pull apart and settle at 28.4 and 70.2 mph.
:width: 100%

The EM loop on the May readings, from a deliberately poor start.
```

If each reading came with its regime, fitting would be easy: average the congested readings, average the free-flow
ones, count how many of each. The labels are missing, so the **expectation-maximization (EM)** algorithm goes
round a loop:

- **E-step.** With the current bell curves, compute every reading's soft label.
- **M-step.** Refit each regime's share, mean and spread, counting each reading by its soft label: a reading that
  is 70% congested counts 0.7 toward the congested bell and 0.3 toward the free-flow one.
- Repeat until nothing changes.

Started from a deliberately poor guess, two bells at 45 and
55 mph, the two means were within 0.5 mph of their final values by iteration
14 and stopped changing after 27. Three other starting guesses,
including a lopsided one, reached the same answer. On harder data different starts often reach different answers,
so it is standard practice to run several and keep the best fit on the training data. Latent class choice models
are often estimated with the same loop; only the refit step changes.

:::{admonition} Going deeper &mdash; what EM is climbing
:class: dropdown
The goal is to make $\log p(x) = \log \sum_k \pi_k \, p(x \mid k)$, summed over the training readings, as large as
possible. A log of a sum is awkward to maximise directly. For any soft labels $q(k)$,
$\log p(x) \ge \sum_k q(k) \log \frac{\pi_k \, p(x \mid k)}{q(k)}$: the *evidence lower bound* (ELBO). The E-step
sets $q$ to the Bayes soft guess, which makes the bound touch the true value; the M-step then pushes the bound
up. So every round of EM can only improve the fit to the training data. The VAE of section 4.7 trains on the same
bound. With continuous knobs the exact soft guess can no longer be computed, so an encoder network learns to
approximate it, and gradient descent replaces the loop. Bishop &amp; Bishop (2024), *Deep Learning: Foundations
and Concepts*, chapters 15 and 19.
:::

**How many regimes?** Two was a choice. Held-out data can judge it: the average log-probability of the June
readings, measured in bits saved per reading compared with one bell curve.

| regimes | bits saved per June reading | means (mph) |
|---|---|---|
| 1 | &mdash; | 48.4 |
| 2 | 0.89 | 28.4, 70.2 |
| 3 | 0.97 | 25.5, 62.4, 70.3 |
| 4 | 1.02 | 13.8, 29.0, 60.9, 70.3 |
| 5 | 1.02 | 13.8, 29.0, 59.7, 70.2, 70.4 |

Almost all of the gain comes from going from one regime to two. Four regimes help a little more: stop-and-go near
14 mph, slow traffic near 29, a recovering band near
61 and free flow near 70. A fifth adds almost nothing; it splits free
flow in two. Two regimes are the simplest story; four describe this detector a little better.

## 400 cells, one hidden class

```{figure} ../_static/figures/GenMix_Heatmap_Classes.png
:alt: Top row, the typical heatmaps of four hidden classes, from a large queue to free flow, with the share of training heatmaps in each. Bottom row, one heatmap drawn from each class, which keeps the overall pattern but is speckled cell by cell. A panel lists bits per cell on the test heatmaps and the average jump between road neighbours.
:width: 100%

The CTM heatmaps as a mixture of 50 classes. The four classes shown are, after sorting all classes from
slowest to fastest average speed, the largest one in each quarter; the samples are the first draw from each.
```

Now the running example of sections 4.1&ndash;4.8: the 4,000 CTM speed heatmaps, each 400 cells on
the 25 speed bins of 3 mph, with the same 3,200 / 400 / 400 split. The recipe is
unchanged. Each heatmap belongs to one hidden class; each class has its own histogram over the 25 bins for every
one of the 400 cells. To make a heatmap, pick a class, then draw every cell from that class's
histograms. $p(x \mid k)$ is now the product of the 400 cells' probabilities under class $k$, and EM fits
it exactly as before. Two details: a small pseudo-count is added to every histogram so that no bin ever gets
probability zero, and both it and the number of classes were chosen on the validation heatmaps
(50 classes, pseudo-count 0.1).

One class is exactly the "each cell on its own" baseline of section 4.2. So the bits-per-cell ladder shows what a
single shared hidden label buys:

| model | bits per cell, test heatmaps |
|---|---|
| each cell on its own (1 class) | 3.20 |
| 3 classes | 2.27 |
| 50 classes | 1.84 (1.83&ndash;1.84 over three starts) |
| the local rule of section 4.2 | 0.64 |
| the transformer of section 4.2 | 0.40 |

A shared class closes about half of the gap between "each cell on its own" and the transformer. The cells now
agree on the big picture: whether there is a queue, roughly how big, roughly where. The average jump between
neighbouring road cells in a new sample falls from 24.9 mph (each cell on its own) to
9.0 mph with 50 classes. Real test heatmaps jump 3.8 mph.
The rest is speckle: inside a class, each cell is still drawn on its own.

Two things look familiar from earlier pages. A class's *typical* heatmap, the expected speed in every cell, is an
average over the heatmaps in that class; where their fronts sit in slightly different places, the average front is
soft, which is the VAE's blur from section 4.7 in another form. And with 400 cells of evidence, the soft
guess is almost always certain: 97% of the test heatmaps are assigned to one class with more
than 99% probability.

## Where one hidden label breaks

```{figure} ../_static/figures/GenMix_Where_It_Breaks.png
:alt: Bits per cell against the number of classes on a log scale. The training curve keeps falling. The validation curve falls to a minimum near 50 classes and then rises. A separate point for one class per training heatmap shows 0.79 bits on training heatmaps and 2.47 on validation. A side panel notes that looks-real is 0.003 or less for every mixture.
:width: 100%

More classes keep helping on the heatmaps the model trained on, and stop helping on new ones. Pseudo-count 0.1 for
every curve point with two or more classes; the separate point uses its own best pseudo-count.
```

Why not simply use more classes? On the training heatmaps more classes always help. On the validation heatmaps
the curve flattens between about 20 and 50 classes, at 1.86 bits per cell, and then turns
back up. At the extreme, one class per training heatmap (3,200 classes, nothing left
to fit) scores 0.79 bits per cell on the training heatmaps and 2.47 on
validation. It has memorized.

The reason is in the traffic. A queue can end at any road cell and start at any minute; congested states vary
*smoothly*. A list of labels can only cover a smooth range by listing more and more cases, each seen in fewer
training heatmaps.

There is a second limit that more classes do not fix. On the scorecard of section 4.8, the 50-class
mixture covers the variety well (recall 0.98&ndash;0.99 over three
starts) but its samples never look real: precision is 0.003 or less for every
mixture tried. It is the same pattern as the local rule on that scorecard: noise fools "covers the variety" but not
"looks real". Inside a class the cells are drawn independently, so neighbouring cells do not agree.

So a better generator needs two things: a hidden cause that can vary smoothly, and a way to make all the cells
agree. The next two models are two answers.

## One recipe, three hidden causes

```{figure} ../_static/figures/GenMix_Three_Hidden_Causes.png
:alt: A table with three rows, mixture, VAE and diffusion, and four columns: the hidden cause, going from data to the hidden cause, going from the hidden cause to data, and the likelihood.
:width: 100%

Same recipe, three choices of hidden cause.
```

Every model in this table draws a hidden cause and then makes the data from it. What changes is the hidden cause,
and with it how hard each direction is.

- **Mixture.** One label. Going back from data to the hidden cause is exact: Bayes' rule, the soft guess. So is the
  likelihood: a sum over the classes, which is why the mixture can go on the bits-per-cell ladder.
- **VAE** (section 4.7). A few continuous knobs. The sum over classes becomes an integral over every possible knob
  setting, which cannot be computed. So the VAE learns an encoder to make the guess, and trains on a lower bound,
  the ELBO. That is why section 4.7 could not put the VAE on the bits ladder.
- **Diffusion** (next). The hidden cause is a chain of noisier and noisier copies of the heatmap, each the same size
  as the data. Going from data to hidden cause needs no learning at all: you add noise. All the learning goes into
  the reverse, removing the noise a little at a time. Like the VAE, it trains on a lower bound.

The richer the hidden cause, the harder the step back. Diffusion's trick is to make that step trivial and put all
the work into generating.

:::{admonition} Before you trust this result
:class: warning
**What is the baseline?** For the detector, one bell curve: the two-regime model is
0.89 bits per June reading better. For the heatmaps, each cell on its own
(3.20 bits per cell), with the local rule (0.64) and the transformer
(0.40) of section 4.2 for scale.

**How was the data split, and why is that honest?** The detector model was fitted on May and checked on June, a
later month it never saw; splitting readings at random would have let neighbouring five-minute readings sit on both
sides. The heatmaps use the same 3,200 / 400 / 400 split of whole heatmaps as section
4.2; the number of classes and the pseudo-count were chosen on validation, and the test heatmaps only report.

**What does it do on the ugly cases?** Bell curves are the wrong shape for speed regimes: they put
0.8% of the probability below 0 mph and still over-predict the in-between speeds
(5.1% against a real 2.6%). June data prefers four regimes to two. The
heatmap samples are speckled. And this is one detector, chosen for being congested, and one simulator.
:::

:::{admonition} Fit card &mdash; Mixture model (latent class model)
:class: tip
**Idea in one sentence.** Each example comes from one of a few hidden groups, and each group has its own simple
distribution.

**Why it works.** Given the group, the data is simple; the shared group is what makes things vary together.

**Fits these tasks.** Regime detection, traveller or driver segments, clustering trips or crashes, and flags for
odd readings: something unlikely under every group is unlike anything in the training data (*classification*,
*generation*).

**Needs this data.** Unlabelled examples, from hundreds upward: detector archives, trajectories, survey responses.
And a decision about how many groups, checked on held-out data.

**Breaks when.** The variation is smooth rather than grouped (more groups only memorize); the shape assumed for each
group is wrong; the parts of an example must agree with each other beyond what the group fixes.

**Keep the classical method when.** A fixed speed threshold or a fundamental-diagram breakpoint already separates
the regimes, and the agency needs the same rule at every detector.
:::

## Where you will meet this

| domain | the hidden cause | data | classical baseline |
|---|---|---|---|
| Traffic flow | the regime: free flow, congested, stop-and-go | loop and radar detector archives | a fixed speed threshold or fundamental-diagram breakpoint |
| Travel behaviour | the traveller class in a latent class choice model | revealed- or stated-preference surveys | a logit model with segments set by income, age or trip purpose |
| Road safety | the crash type behind a crash record (latent class analysis) | crash reports: road, weather, vehicle and person fields | cross-tabulations by the crash-type field |
| Driving automation | the driver type behind a car-following trajectory | trajectory datasets such as NGSIM or highD | a car-following model calibrated per driver, then thresholds on its parameters |

Two extensions are worth knowing by name. A **hidden Markov model** lets the regime itself follow a chain in time,
so the regime five minutes ago informs the one now; the soft guess above ignores time entirely. And **mixture
density networks** let a neural network output the shares, means and spreads, so the mixture can change with
inputs such as time of day or weather.

## Check yourself

1. A colleague fits two regimes to every detector in the district and uses each detector's 50/50 point as its
   congestion threshold. What do you check before this goes into a report?
2. You have mode-choice data from 400 commuters and suspect two kinds of travellers. When would you fit a latent
   class model rather than splitting them by income?
3. Your 50-class heatmap mixture covers the variety well but its samples do not look real. A
   teammate proposes 3,000 classes. What happens, and what would you change instead?

---

Next: diffusion, the third row of the table.
