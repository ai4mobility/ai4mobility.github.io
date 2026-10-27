# 4.3 Latent variables: hidden causes, not hidden layers

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 4 &middot; Section 4.3</span>
    <span class="notes-card-session">Session: Generative models, part 1</span>
  </div>
  <p class="notes-card-lede">Before the VAE, the idea it rests on. You have met "latent" before: the vectors BERT and a ViT compute inside. A latent variable is something else. It is a hidden cause that the model assumes made the data, and it comes with a distribution you can draw from. This page follows four questions on the CTM heatmaps, where all five true causes are known: what a latent variable is, how a model finds one without labels, how the distribution of the hidden cause is learned, and how it is used to make a new heatmap.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Read it before</h4>
      <ul>
      <li><a href="../module2/notes5-bert.html">2.5 BERT: pretrain, then adapt</a></li>
      <li><a href="../module2/notes7-vision.html">2.7 Transformers that see: the Vision Transformer</a></li>
      <li><a href="notes2-autoregressive.html">4.2 One cell at a time</a></li>
      <li><a href="notes2a-gaussians.html">Before 4.3: Gaussians and their mixtures</a></li>
      </ul>
    </div>
    <div>
      <h4>Labs that go with it</h4>
      <ul><li><a href="../labs.html">VAE on traffic heatmaps</a></li></ul>
    </div>
  </div>
</div>

## What this section covers

- Two things called "latent": a representation, computed from the data, and a latent variable, assumed to have made it
- The two-step story behind every latent-variable model, and the latent variables you already use
- The smallest step from one to the other: PCA becomes probabilistic PCA
- Finding a hidden cause without labels, and which causes can be found at all
- Learning the distribution of the hidden cause: build it in, or fit it afterwards
- Generating: draw the cause, then the data, and steer by choosing where to draw
- The whole story in one table: mixture, probabilistic PCA, VAE and diffusion

## Two things called "latent"

```{figure} ../_static/figures/GenLV_Two_Latents.png
:alt: Two panels. Left, latent representation: a test heatmap goes through an encoder trained for one task to two numbers, then a head that outputs bottleneck capacity 31 percent, true 34 percent. Bullets say it is computed from the input, the same every time, has no distribution to draw from and no way back to a heatmap. Right, latent variable: two knobs are drawn from a standard bell, a decoder turns them into a new heatmap, and a dashed arrow back is labelled a guess with a spread. Bullets say it is assumed to have made the data, comes with a distribution, and can make new data.
:width: 100%

Left, an encoder trained for one task, the way a ViT is fine-tuned. Right, a latent-variable model. The heatmap on the left is one test heatmap chosen by a rule (strong bottleneck, starting density nearest 30% of jam density). The one on the right is the decoder's output for the first draw from the bell.
```

"Latent" means hidden. This course has used the word for two different things.

A **latent representation** is what a network computes from its input on the way to an answer. BERT computes 768
numbers for every token. The ViT of {doc}`2.7 <../module2/notes7-vision>` computes 192 numbers in its `[CLS]` slot
and reads the congestion class from them. They are latent because nobody sees them: they are neither the input nor
the output. But they are computed *from* the data. Give the network the same camera frame twice and you get the same
192 numbers twice.

A **latent variable** points the other way. It is a hidden cause that the model assumes *made* the data. The model
says: first something we cannot see was settled (the traffic regime, the demand, the bottleneck), and then the data
we can see were produced from it. A latent variable comes with a distribution, which says how often each value of the
hidden cause happens. So you can draw new values of it, run them through the part of the model that makes data, and
get new data.

| | latent representation | latent variable |
|---|---|---|
| examples | BERT's token vectors, a ViT's `[CLS]`, an autoencoder's code | the regime in a mixture (4.6), the knobs of a VAE (4.4), diffusion's noise |
| which way the arrow points | data → numbers: computed from the input | cause → data: assumed to have made the input |
| for one input | one exact vector, every time | a guess with a spread |
| a distribution to draw from | none | yes, part of the model |
| can it make new data? | no: no distribution, and BERT and ViT have no way back to the input | yes: draw the cause, then the data |
| size | large: 768 per token in BERT-base, 192 in ViT-Tiny's `[CLS]` | usually small: one label, two knobs (diffusion is the exception) |
| what it keeps | whatever its training task needed | whatever best explains the data |

The last row can be measured. Take one encoder body, 400 &rarr; 96 &rarr; 2, and train it three ways on the 3,200
training heatmaps. Then ask what its two numbers know about the simulator's own knobs. *R²* here is the share of a
knob's variation that the best straight line through the two numbers explains, fitted on the training heatmaps and
scored on the 400 test heatmaps.

| two numbers from the same encoder body, trained to &hellip; | R² starting density | R² bottleneck capacity | rebuilding the heatmap from them (RMS per cell) |
|---|---|---|---|
| predict bottleneck capacity: one task, like a fine-tuned ViT | 0.25 | 0.85 | 19.6 mph |
| rebuild the heatmap: a plain autoencoder | 0.82 | 0.17 | 7.29 mph |
| rebuild it and keep every code inside one bell: the VAE of section 4.4 | 0.90 | 0.32 | 7.68 mph |

For the task encoder, a decoder was trained afterwards on its frozen numbers. For scale, answering every heatmap
with the average heatmap is 23.76 mph off.

The task code keeps what its task needs, capacity, and little else: nothing can rebuild a heatmap from it. That is
the BERT and ViT situation. Now look at the last two rows. The plain autoencoder and the VAE keep much the same
things. So what makes the VAE's two numbers latent variables, and the autoencoder's a representation, is not what
they contain. It is what the model says about them. The VAE gives them a distribution and a way to make data from
them; the autoencoder gives them neither. The rest of this page takes that difference apart.

## The hidden cause comes first

Every latent-variable model tells the same two-step story about how one piece of data was made:

1. Draw the hidden cause $z$ from its distribution.
2. Draw the data $x$ from what that cause makes.

The CTM heatmaps were made exactly this way. For each run, five knobs were drawn at random (starting density, upstream
inflow, bottleneck capacity, when the bottleneck starts, how long it lasts), and the CTM turned them into 400 speeds.
Section 4.4 shows the five knobs as dials. Here the data maker is the CTM, written down from physics, and the knobs
are known. A latent-variable model has to learn both from the 400 speeds alone.

Written as one line, the probability of a heatmap adds up every way it could have been made:

$$
p(x) = \int p(z)\, p(x \mid z)\, dz
$$

| symbol | in the CTM heatmaps |
|---|---|
| $x$ | one heatmap: 400 speeds |
| $z$ | the hidden cause: the knob setting that made it |
| $p(z)$ | how often each knob setting happens: here, each knob drawn at random from its range |
| $p(x \mid z)$ | the heatmaps that knob setting can make: the CTM, plus each run's random starting pattern |
| $p(x)$ | how likely this heatmap is, overall |

*In words:* a heatmap could have come from many knob settings, so its probability adds them all up: how often each
setting happens, times how likely that setting is to make this heatmap. When the hidden cause is a label, as in the
mixture of section 4.6, the integral becomes a sum.

**You already use latent variables.** Transportation models have had hidden causes for decades:

| model you know | the latent variable, never observed | what you observe |
|---|---|---|
| binary logit or probit | each option's utility | the choice |
| ordered probit for crash severity | the injury propensity | the KABCO level |
| latent class choice model | the traveller's class | the choices |
| Kalman-filter traffic state estimation | the true density on each segment | noisy detector counts |
| OD estimation | the trip table | link counts |
| hybrid choice (ICLV) model | attitudes, such as concern for safety | survey answers and choices |

In every one of these, you named the hidden cause before fitting the model. What is new in AI is that nobody names it
in advance. The model is told only what kind of hidden cause to use and how many numbers it has. It has to work out
what they should mean.

## The smallest step: PCA becomes probabilistic PCA

```{figure} ../_static/figures/GenLV_PCA_PPCA.png
:alt: Top, the average heatmap with number 1 set to minus 2, 0 and plus 2, going from fully jammed to free flow, and with number 2 set to minus 2, 0 and plus 2, adding a queue at the downstream end. Bottom left, PCA as a representation: heatmap to two scores. Bottom right, probabilistic PCA: four speckled sample heatmaps drawn with noise, and two smooth ones without it, with their scores.
:width: 100%

Top: what each of the two numbers does to the average heatmap. Bottom: the same two directions, used two ways. The samples are the first draws.
```

You may have used principal component analysis (PCA) to squeeze many correlated measurements into a few scores. On
the 3,200 training heatmaps, two directions hold 81.8% of the variation. Those two scores are a
representation: computed from each heatmap, the same every time, and that is all.

**Probabilistic PCA** (Tipping &amp; Bishop, 1999) uses the same two directions but tells a two-step story:

1. Draw two numbers from a standard bell.
2. Start from the average heatmap, add each direction times its number, then add noise to every cell. Fitted to these
   heatmaps, the noise is about 10 mph per cell.

That small change turns the two numbers into latent variables. On the 400 test heatmaps, three things happen.

- **Nothing new is computed for a heatmap.** Probabilistic PCA's best guess of the two numbers is the PCA score,
  put on the bell's scale and multiplied by 1.000 and 0.997: the same two numbers. Starting density reads off
  either one with the same R², 0.93.
- **The guess now has a spread.** It is 0.025 and 0.074, where the bell's spread is 1. With 400 cells of
  evidence, the two numbers are pinned down tightly.
- **The model can make new heatmaps.** Draw two numbers, map them, add the noise.

The top row of the figure shows what the two numbers mean. Number 1 is how congested the road is overall; it tracks
starting density. Number 2 is whether, and how early, a queue builds at the downstream bottleneck; it partly tracks how
strong that bottleneck is (R² 0.22).

The samples show what such a simple data maker costs. With the noise, 17% of cells fall outside 0&ndash;75 mph:
a bell does not know that speeds have limits. Those samples look real 0.220 of the time on the scorecard of
section 4.5. Without the noise they are smooth averages: they look real (0.875) but cover almost none of the
variety (0.033). The VAE of section 4.4 keeps the story and replaces "average plus two straight directions" with a
network.

:::{admonition} Going deeper &mdash; probabilistic PCA in symbols
:class: dropdown
The model is $x = \mu + W z + \varepsilon$, with $z \sim \mathcal{N}(0, I)$ and noise $\varepsilon \sim \mathcal{N}(0, \sigma^2 I)$,
so every heatmap is a draw from $\mathcal{N}(\mu,\, W W^\top + \sigma^2 I)$: a bell whose shape is set by two directions.
The best fit has a formula: the columns of $W$ are the top PCA directions, each scaled by $\sqrt{\lambda_k - \sigma^2}$, and
$\sigma^2$ is the average of the variances PCA throws away. The guess for one heatmap is again a bell,
$p(z \mid x) = \mathcal{N}\big(M^{-1} W^\top (x - \mu),\ \sigma^2 M^{-1}\big)$ with $M = W^\top W + \sigma^2 I$. Let the noise
shrink to zero and the guess becomes the PCA score with no spread: PCA is the noise-free limit of probabilistic PCA.
Tipping &amp; Bishop (1999), *Probabilistic principal component analysis*; Bishop &amp; Bishop (2024), chapter 16.
:::

## Finding a hidden cause without labels

```{figure} ../_static/figures/GenLV_Find_Loop.png
:alt: A loop. Posit what kind of hidden cause and how many, then guess for each example which values of the hidden cause could have made it, then refit the data maker so the guessed causes explain their examples better, repeat, and name the causes afterwards. Below, the loop in three models: a mixture with Bayes' rule and re-averaging, probabilistic PCA with a projection and a formula, and a VAE with an encoder and a decoder network.
:width: 100%

One loop, three models. Nothing in it uses a label.
```

Nobody tells the model what the hidden cause is. Every latent-variable model in this module finds it with the same
loop:

- **Guess.** For each example, ask which values of the hidden cause could have made it. This is the step back from data
  to cause, $p(z \mid x)$.
- **Refit.** Change the data maker, and the distribution of the hidden cause, so that the guessed causes explain their
  examples better.
- **Repeat** until nothing changes.

Two things are found at once. For each heatmap, its value of the hidden cause comes from the guess. For the whole
dataset, what each hidden number *does* to a heatmap comes from the refit. Neither comes with a name. You name them
afterwards, by checking them against things you can measure. In section 4.6 the two regimes found at one I-405
detector, 28.4 and 70.2 mph, are checked against the clock, which the model never saw: they line up with
the peak periods. Here, the numbers can be checked against the simulator's own knobs.

The three models differ most in how hard the guess is. For a mixture it is Bayes' rule, exact; the loop is the EM
algorithm of section 4.6. For probabilistic PCA it is a formula, exact. For a VAE no formula exists, so an encoder
network learns to make the guess, and it is trained together with the decoder by gradient descent.

### Which hidden causes can be found?

```{figure} ../_static/figures/GenLV_Which_Knobs.png
:alt: A bar table with the five simulator knobs as rows, sorted by how much each moves a heatmap. Starting density moves a heatmap 54.1 mph, bottleneck capacity 20.5, upstream inflow 19.6, bottleneck start 17.8, bottleneck length 8.8. Spread left after one heatmap 0.12, 0.50, 0.46, 0.27, 0.68. Found by a 2-knob VAE, R squared 0.90, 0.32, 0.05, 0.16, 0.01. Found by an 8-knob VAE 0.95, 0.59, 0.43, 0.67, 0.19.
:width: 100%

Five true causes, three questions: how much does it move a heatmap, how well could anyone pin it down from one
heatmap, and how much of it did the VAE find?
```

On real data you cannot check a discovered cause against the truth. Here you can, because all five knobs are known.
(The dataset stores three of them. The other two, when the bottleneck starts and how long it lasts, were regenerated
exactly from the dataset's random seed.) For each knob, three measurements:

- **How much it moves a heatmap.** Set the knob to each end of its range, keep everything else, run the CTM again, and
  measure the change. Starting density moves a heatmap by 54.1 mph per cell; bottleneck length by
  only 8.8.
- **How well one heatmap pins it down, for anyone.** Run the CTM 200,000 more times with random knobs. For each
  test heatmap, take the 100 runs that look most like it, and see how spread out their knob values are, as a share of
  the knob's full spread. This is an estimate of the true $p(z \mid x)$: the best guess any model could make. Starting
  density is pinned down to 0.12 of its spread. Bottleneck length keeps 0.68: a heatmap says little about
  how long the bottleneck lasted.
- **How much the VAE found.** The R² of each knob from the VAE's numbers: the 2-knob VAE of section 4.4, and the same
  VAE with 8 knobs.

Three lessons come out of it.

1. **A model finds the causes that move the data most and that the data pin down best, as far as its number of knobs
   allows.** Two knobs hold starting
   density (0.90) and part of bottleneck capacity (0.32). Eight knobs add bottleneck start (0.67), more of capacity
   (0.59) and upstream inflow (0.43).
2. **Missing is not the same as invisible.** One heatmap does say something about upstream inflow: its spread falls to
   0.46 of its range. Yet the 2-knob VAE keeps almost none of it (R² 0.05). Inflow was not hidden from the model;
   it lost the competition for two slots to bigger causes. With eight slots it comes back.
3. **A cause that leaves a faint trace stays hidden.** Bottleneck length moves the heatmap least and is the hardest to
   pin down even with the simulator in hand; eight knobs recover only 0.19 of it. Before blaming a model for missing a
   cause, check whether the data carry it.

A discovered latent variable is therefore not "the true cause". It is the most useful summary of the data for the
number of slots it was given. And a model can be sure of its own knobs while saying little about the knobs you care
about: the VAE's guess of its two numbers for a test heatmap has a median spread of 0.16 and 0.37, against the bell's 1.

## Learning the distribution of the hidden cause

```{figure} ../_static/figures/GenLV_Codes_vs_Bell.png
:alt: Left, the two numbers of a plain autoencoder for 3,200 training heatmaps form a large irregular cloud from about minus 12 to 5 and minus 18 to 6; the standard bell's circles are a small spot near the top. Middle, the VAE's numbers fill a disk close to the bell's circles, with rings marking bell draws that land where no training heatmap sits, mostly outside the 2-spread circle. Right, a table of holes, looks-real and covers-variety for four ways to draw.
:width: 100%

The codes of the 3,200 training heatmaps, darker for higher starting density. Gold circles: where a standard bell
draws, at one and two spreads. Each panel has its own scale.
```

A latent-variable model has two distributions to learn: how often each hidden cause happens, $p(z)$, and what data
each cause makes, $p(x \mid z)$. The models in this module split that work differently.

- **Mixture (section 4.6): both are learned.** Each round of EM refits the regimes' shares (here 52% congested,
  48% free flow) and each regime's own bell.
- **Probabilistic PCA, VAE and diffusion: $p(z)$ is not learned at all.** It is fixed to a standard bell (for
  diffusion, to pure noise). All the learning goes into the data maker, which has to bend that bell into the shape of
  the data. You do not learn where the hidden cause lives. You choose where it lives, and learn how to map it to data.

For that choice to work, the codes of real heatmaps have to sit where the bell draws. The figure checks this for two
models with the same 400 &rarr; 96 &rarr; 2 &rarr; 96 &rarr; 400 shape.

- **A plain autoencoder has no reason to use the bell.** Its codes are centred at (-0.42, -2.09) with spreads
  of 2.81 and 5.04. Only 12% of them fall inside the bell's 2-spread circle, where a true bell puts
  86%. Draw from the bell and decode, and every draw lands in the same small part of the cloud: the samples look real
  (1.000) but cover only 0.025 of the variety. It makes one kind of heatmap.
- **The VAE's KL term pulls the codes onto the bell** (section 4.4 explains how). Its codes are centred at
  (0.03, -0.09) with spreads 0.97 and 0.89, and 95% sit inside the circle. The match is not perfect. The codes are more
  bunched than a true bell, so 15.5% of bell draws land in *holes*: places farther from every training code than
  99% of training codes are from their nearest neighbour. Those are the rings in the figure.

There is a second way: let the autoencoder train freely, then fit a distribution to its codes afterwards. Four ways to
draw 400 heatmaps, scored against the test heatmaps:

| how the two numbers are drawn | holes | looks real | covers the variety |
|---|---|---|---|
| plain autoencoder + standard bell | 1.0% | 1.000 | 0.025 |
| plain autoencoder + one bell fitted to its codes afterwards | 14.5% | 0.910 | 0.212 |
| plain autoencoder + ten bells fitted to its codes afterwards | 1.8% | 0.985 | 0.083 |
| VAE + standard bell | 15.5% | 0.998 | 0.085 |
| *for scale: real validation heatmaps* | | 0.945 | 0.953 |

A bell fitted afterwards covers more of the variety than the VAE (0.212 against 0.085) but looks less real
(0.910) and has about as many holes. Ten bells fitted afterwards leave almost no holes (1.8%) and roughly match
the VAE on the other two scores. So on this data, fitting a distribution to a plain autoencoder's codes afterwards works about as
well as building it in with the KL term. This two-stage recipe is how latent diffusion, the method behind Stable
Diffusion, works at scale: an autoencoder squeezes images into codes, then a diffusion model learns the distribution
of the codes (Rombach et al., 2022).

Every row covers little of the variety, because every row shares a two-number decoder that returns averages
(section 4.4). A better distribution for the codes cannot fix a data maker that blurs.

:::{admonition} Going deeper &mdash; why the VAE leaves holes
:class: dropdown
The KL term pulls each heatmap's own little bell, $q(z \mid x)$, toward the standard bell. What a fresh draw needs is
that the *pool* of all those little bells, $q(z) = \frac{1}{N}\sum_n q(z \mid x_n)$ (the *aggregate posterior*), matches
the standard bell. The first only nudges the second, and the rebuild term pulls the other way, so the pool ends up
more bunched than the bell and draws from the bell's edges land in holes. Two standard fixes: learn the prior as well,
for instance as a mixture of bells (Tomczak &amp; Welling, 2018, *VAE with a VampPrior*), or fit it after training
(Ghosh et al., 2020, *From variational to deterministic autoencoders*), as in the table above. Hoffman &amp; Johnson
(2016), *ELBO surgery*, splits the KL term to show this gap.
:::

## Generating: draw the cause, then the data

```{figure} ../_static/figures/GenLV_Generate.png
:alt: Left, a five by five grid of heatmaps decoded at knob values from minus 2 to plus 2: number 1 runs from jammed on the left to free flow on the right, number 2 adds a downstream queue toward the top. Right, four heatmaps drawn from the part of the knob space where heavy-start heatmaps sit, and bars of average speed: steered draws 28.3 mph, real heavy-start test heatmaps 25.7, draws from the whole bell 48.7, all real test heatmaps 51.3.
:width: 100%

Left: the VAE's knob space as a map, each heatmap the decoder's output at one grid point. Right: drawing knobs only
where heavy-start heatmaps sit. The four steered heatmaps are the first four draws.
```

Generating from a latent-variable model is the two-step story run forward. Papers call it *ancestral sampling*:
draw $z$ from $p(z)$, then run the data maker. For the VAE: draw two numbers from the bell, run the decoder once.

The left of the figure shows why this works. Every point of the knob space decodes to a heatmap, and nearby points
decode to similar heatmaps. Number 1 runs from a jammed road (left) to free flow (right). As number 2 rises (up the
map), a queue appears at the downstream bottleneck. A draw from the bell picks a point on this map.

**Steering.** Because the hidden cause has a distribution and a place on the map, you can choose where to draw. Take
the 698 training heatmaps whose starting density is at least 45% of jam density, fit a bell to their codes, and
draw 400 knob settings from that bell instead of the standard one:

| | average speed of a heatmap |
|---|---|
| steered draws | 28.3 mph |
| real heavy-start test heatmaps | 25.7 mph |
| draws from the whole bell | 48.7 mph |
| all real test heatmaps | 51.3 mph |

Choosing where to draw is the simplest way to ask a generator for a kind of scenario: heavy congestion, a strong
bottleneck, a late breakdown. Which part of the map holds which traffic must be found from real examples first, as it
was here, and the result checked against real examples of that kind.

None of this is possible with BERT's or a ViT's vectors: there is no distribution to draw them from and no decoder
back to a sentence or a camera frame. (BERT can fill in a masked word, which makes one piece of text from the rest of
it. That is not drawing a hidden cause.) And not every generator needs a latent variable. The transformer of section
4.2 makes heatmaps one cell at a time with none at all.

## The whole story in one table

| | mixture (4.6) | probabilistic PCA (4.3) | VAE (4.4) | diffusion (next) |
|---|---|---|---|---|
| the hidden cause $z$ | one label: the regime or class | a few numbers | a few numbers | a noisy copy of the data, the same size |
| its distribution $p(z)$ | learned shares | fixed: a standard bell | fixed: a standard bell | fixed: pure noise |
| the data maker $p(x \mid z)$ | that class's own bell | average + straight directions + noise | a decoder network | a denoising network, many small steps |
| the guess $p(z \mid x)$ | Bayes' rule, exact | a formula, exact | an encoder network, approximate | add noise: nothing to learn |
| how it is fitted | the EM loop | a formula | gradient descent on a lower bound | gradient descent on a lower bound |
| exact probability of a heatmap? | yes | yes | a lower bound only | a lower bound only |
| to make a new heatmap | pick a class, draw from it | draw two numbers, map, add noise | draw numbers, decode once | draw noise, clean it up step by step |

Read down any column and you have the four questions of this page. Read across the "guess" row and you see the
trade: from mixture to VAE, a richer hidden cause makes the step back from data to cause harder, until a network has
to learn it. Diffusion makes that step trivial and puts all the learning into the data maker.

## Where it breaks

- **Discovered causes follow variation, not meaning.** With two slots, inflow lost out to bigger causes. A knob you care
  about may not be among the ones the model keeps.
- **The numbers are not unique.** Rotate probabilistic PCA's two numbers and the fit is exactly as good; a VAE's knobs
  can come out flipped or mixed between training runs (section 4.4). Never write a rule on "knob 1" without checking it
  against a quantity you can measure.
- **The distribution can miss the codes.** The plain autoencoder's codes sit far from the bell; the VAE leaves
  15.5% of its draws in holes.
- **The data maker can be too simple.** Probabilistic PCA's bells put speeds below 0 and above 75 mph; the VAE's decoder
  returns averages.
- **It learns one place.** Knobs found on one corridor's heatmaps describe that corridor. Moved to another, with
  different geometry and demand, both the map and the data maker need checking again.

:::{admonition} Before you trust this result
:class: warning
**What is the baseline?** For what the numbers keep: the same encoder body trained for a task, and as a plain
autoencoder. For what can be found at all: the simulator itself, run 200,000 more times. For samples: the real
validation heatmaps (0.945 looks real, 0.953 covers the variety) and the scorecard of section 4.5.

**How was the data split, and why is that honest?** The same 3,200 / 400 / 400 split of whole heatmaps
as everywhere in Module 4. Every network, every fitted distribution and every steering bell saw only the training
heatmaps; every R², hole share and score is on the test heatmaps. The extra simulator runs use fresh random seeds,
none from the dataset.

**What does it do on the ugly cases?** Nothing finds bottleneck length well. The VAE's bell sends 15.5% of
its draws into holes. Steered draws average 28.3 mph against 25.7 for the real heavy-start heatmaps. R² is a
straight-line read-out, so a curved one could find more. The task encoder and the plain autoencoder were trained with
one seed. A second seed moved the details but not the story: the task encoder kept capacity (R² 0.78) and none of
starting density, and 16% of the autoencoder's codes fell inside the circle. And this is one simulator on one road.
:::

:::{admonition} Fit card &mdash; Latent-variable model
:class: tip
**Idea in one sentence.** Assume each example was made from a few hidden causes, learn how often each cause happens
and what data it makes, then generate by drawing causes.

**Why it works.** A few hidden numbers forced to explain many observed ones end up holding the biggest sources of
variation, and a known distribution over them makes them something you can draw from.

**Fits these tasks.** Scenario generation, filling gaps in detector data, flagging unusual traffic states (anything
the model finds unlikely), finding regimes or segments without labels, compressing traffic states
(*generation*, *extraction*, *classification*).

**Needs this data.** Thousands of unlabelled examples of the same shape (detector archives, trajectories, crash
records), and something measurable to check the hidden causes against afterwards.

**Breaks when.** The cause you care about moves the data little; the hidden numbers are asked to mean something
physical; the distribution of the hidden cause does not match where the codes actually sit.

**Keep the classical method when.** You already know the causes and the data maker: a calibrated CTM, a fundamental
diagram, a Kalman filter on a known traffic model. Or when PCA's compression already does the job.
:::

## Where you will meet this

| domain | the hidden cause | data | classical baseline |
|---|---|---|---|
| Traffic flow | the true traffic state behind noisy detectors; the regime | loop and radar archives, probe speeds | a Kalman filter on a CTM or LWR model; speed thresholds |
| Driving automation | the scenario behind a recorded drive: lead-vehicle speed, cut-in gap, braking | Waymo Open Dataset, highD, fleet logs | hand-written scenario catalogues and parameter sweeps in simulation |
| Road safety | a crash propensity, or crash types | crash reports | ordered probit models; latent class analysis |
| Travel behaviour | attitudes, traveller classes | travel surveys, smart-card records | hybrid choice and latent class choice models |
| Agency practice | the true count behind a failed detector | count stations with gaps | filling from neighbouring days or stations |

## Check yourself

1. A colleague says BERT's 768-number token vectors are latent variables, so the team can sample new crash narratives
   from them. What is missing for that to be true?
2. Your 2-knob VAE, trained on a corridor's speed heatmaps, does not seem to encode on-ramp demand at all. Before you
   conclude that the demand does not matter, what would you check?
3. You need 500 synthetic heavy-congestion days for a stress test. Would you train a model on heavy days only, or steer
   a model trained on all days? What would you check either way?

---

Next: {doc}`notes3-vae` &mdash; the VAE in full: the encoder, the two-term loss, and why its heatmaps blur.
