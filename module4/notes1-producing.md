# 4.1 Introduction to deep generative models

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 4 &middot; Section 4.1</span>
    <span class="notes-card-session">Session: Why generate</span>
  </div>
  <p class="notes-card-lede">Every model so far looked at data and returned a label. A generative model returns the data itself. This page says what that changes, what "realistic" has to mean for a traffic state, and lays out the four answers this module works through. It then gives the first answer in full: generate a heatmap one cell at a time, each cell drawn from a distribution that depends on every cell already decided, which is the training objective of the GPT in 2.4 with a new kind of token. The running example for the whole module is a set of 4,000 simulated speed heatmaps.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Read it before</h4>
      <ul>
      <li><a href="../module2/notes4-gpt.html">2.4 Building one: a GPT you can read</a></li>
      </ul>
    </div>
    <div>
      <h4>Labs that go with this module</h4>
      <ul><li><a href="../labs.html">VAE on traffic heatmaps; From VAE to diffusion</a></li></ul>
    </div>
  </div>
</div>

## What this section covers

- Four ordinary agency requests that need new data rather than a label
- The running example: 4,000 speed heatmaps from a cell transmission model
- Why "realistic" means getting the *joint* distribution right, shown by destroying it
- The plan for the module: one question, four answers
- The first answer, one cell at a time: the chain rule, and why any order of cells builds the same joint distribution
- Next-cell prediction over 25 speed bins, and why the training loss *is* the likelihood of the whole heatmap
- Training in one pass and generating in 400
- An exact score for a generator, bits per cell, against three baselines including a CTM-shaped rule; where the model
  is uncertain, and whether you can tell its samples from real ones

## Four requests that need a generator

Consider four things an agency or an automated-vehicle team asks for.

**Rare events.** An intersection has 40 recorded crashes. A safety model, or a test programme for an
automated vehicle, needs thousands of believable variations on them, and the real world will not
supply them on any useful timescale.

**Gaps.** A detector goes dark for an hour. The speeds you fill in have to agree with the detectors on
either side and with what the road was doing before the outage.

**What-if.** A lane closes at mile 12. What might the next twenty minutes look like? A digital twin
that answers with one forecast hides how uncertain the answer is; one that can produce many plausible
futures lets you plan for the bad ones.

**Sharing.** Trajectory data is valuable and personal. Synthetic trajectories that behave like real
drivers but belong to nobody could leave the agency where the real ones cannot.

None of these asks for a label. Each asks for *more data that looks real*. That is a different job
from every model in Modules 1 to 3, and it needs a different kind of model.

## The arrow turns around

```{figure} ../_static/figures/GenM_Predict_vs_Produce.png
:alt: Top, a speed heatmap goes into an encoder and head and one label comes out, p of y given x. Bottom, a prompt or nothing goes into a decoder and a whole heatmap comes out, p of x.
:width: 100%

Before: many numbers in, one number out. A generative model: nothing (or a prompt) in, every number out.
```

Every network you have trained so far learned $p(y \mid x)$: given an input $x$, the probability of
each label $y$. A CNN read an FL511 frame and said *congested*; BERT read a crash narrative and named
a manner of collision; the graph attention network read a road network and predicted a speed.

A generative model learns $p(x)$ itself, the distribution of the data, so that it can draw new $x$.
Sometimes it is steered by a condition, $p(x \mid \text{prompt})$, but the output is still a whole
data point, not a label.

**The running example.** The whole module uses one dataset, the one the VAE lab is built on: speed
heatmaps produced by a cell transmission model (CTM) with a triangular fundamental diagram
(free-flow speed 75 mph, wave speed 15 mph, jam density 200 veh/mi). Each heatmap
covers a 4-mile road for 9.6 minutes, pooled to 20 road cells
of 0.2 miles by 20 time steps of 28.8 seconds: **400
numbers per heatmap**. In the figures, the road runs up the page with downstream at the top, and time
runs to the right.

This is a physics simulation, not detector data, and that is deliberate. Because we know exactly how
every heatmap was made, we can check what a generative model has and has not learned. The price is
that nothing on these pages tells you how a model would do on a real, noisy detector feed.

The size of the problem changes too. Getting one label right was the old job. Now all 400
numbers have to be right, and right *together*. An FL511 frame is the same kind of object, only
bigger: 224 &times; 224 pixels &times; 3 colours = 150,528 numbers, 376
times the size of one heatmap.

## What "realistic" means: the joint

```{figure} ../_static/figures/GenM_Joint_vs_Marginals.png
:alt: Left, one real CTM heatmap with a clear queue front. Middle, one heatmap from the shuffled set, which looks like noise. Right, bars for one outlined cell across all 4,000 heatmaps, identical in the real and the shuffled set.
:width: 100%

Each panel is one heatmap from its set. The bars follow the outlined cell through all 4,000 heatmaps of each set: the same spread of speeds in both. The shockwave is gone all the same.
```

Here is an experiment that says what a generative model must get right. Take the 4,000
heatmaps. For each of the 400 cells separately, take that cell's 4,000 values and
deal them out to the 4,000 heatmaps in random order. Nothing is added or lost: every cell
ends up holding exactly the same 4,000 speeds it had before, only in different heatmaps.
What the shuffle destroys is every relationship between cells, because neighbouring cells in a
shuffled heatmap now come from different simulation runs.

The result, in the middle of the figure, is not a traffic state. In the real heatmaps, road cells next
to each other differ by **4.06 mph** on average and are correlated at
0.942. In the shuffled ones they differ by **25.63 mph** and are
correlated at 0.059: free flow sits next to a jam with no front between them.

Now follow one cell, the outlined one, through all 4,000 heatmaps (right of the figure).
In the real set it is below 30 mph in 43% of them, between 30 and
60 mph in 21%, and 60 mph or faster in 36%. In the shuffled
set the numbers are identical, because the shuffle only moved its values between heatmaps. The same
holds for every one of the 400 cells. This spread of one cell's speeds across the whole set is
called the cell's *marginal*, so the real and the shuffled set have the same 400 marginals.

One thing that trips people up: the two heatmaps on the left do not even have the same mix of colours.
They should not. A cell's spread of speeds belongs to the whole set of 4,000 heatmaps, not
to any one picture. The real heatmap shown was picked for its wide speed range and is mostly jammed
(71% of its cells are below 30 mph). A random heatmap from the shuffled set looks
like the set as a whole, where 45% of all cells are at 60 mph or faster.

The distribution of all 400
cells together, including how they move together, is the *joint*. The experiment shows that
everything a traffic engineer cares about lives in the joint. That queues grow backwards at a finite
wave speed, that a front is continuous, that a cell looks like its neighbours a moment earlier: none of
it is visible in any single cell. So when we say *generating a heatmap is drawing a sample from a joint
distribution*, the word "joint" carries the whole idea. A model that matches the marginals and nothing
else produces the middle panel.

:::{admonition} Going deeper &mdash; how big is the joint?
:class: dropdown
Round each speed to one of 25 bins 3 mph wide. A heatmap is then one choice out of $25^{400}$, about
$10^{559}$: a number with 560 digits. No table can list the probability of each one,
and almost all of them look like the shuffled panel. A generative model has to put nearly all of its
probability on the tiny fraction that look like traffic, using a few hundred thousand weights. The four
answers in this module are four ways of making that possible.
:::

:::{admonition} Before you trust this result
:class: warning
**What is the baseline?** The real heatmaps themselves. The shuffled set is built from them and keeps
each cell's distribution exactly, so any difference between the two panels is due to the dependence
between cells and nothing else.

**How was the data split, and why is that honest?** No model is trained here, so there is nothing to
split: all 4,000 heatmaps are used, and the shuffle uses a fixed random seed so the numbers
reproduce.

**What does it do on the ugly cases?** The neighbour difference is one summary. A generator could match
it and still be wrong, for example with smooth fields whose fronts move at the wrong speed. Later
sections add more checks for exactly that reason. And 92.6% of these heatmaps span more than 20 mph from their slowest to their fastest cell;
on a road that is free-flowing all day, the joint is much easier to fake.
:::

## One question, four answers

```{figure} ../_static/figures/GenM_Four_Answers.png
:alt: Four panels. One cell at a time (autoregressive); a few hidden knobs (VAE); a forger and a critic (GAN); clean up noise step by step (diffusion).
:width: 100%

Every generative model answers the same question in a different way.
```

The question for the rest of the module is always the same: *a traffic state has 400 numbers
that depend on each other, so how do you draw a realistic new one?* Each family of generative model is
one answer.

1. **One cell at a time** ({ref}`later on this page <gen-autoregressive>`). Decide the first cell, then the second
   given the first, and so on. This is how GPT writes text, applied to a heatmap.
2. **A few hidden knobs** ({doc}`4.6 <notes3b-vae-basics>`). Compress each heatmap into a few numbers, learn to
   rebuild it from them, then make new heatmaps by drawing new numbers. This is the variational
   autoencoder (VAE). Three steps lead up to it. Section {doc}`4.2 <notes2a-gaussians>` starts with the simplest
   hidden cause, one label that says which traffic regime made the data. Section {doc}`4.3 <notes2b-latent-variables>`
   sets out the general idea: a *latent variable*, a hidden cause you can draw from. Sections
   {doc}`4.4 <notes2c-autoencoders>` and {doc}`4.5 <notes2d-deep-autoencoders>` then build the plain autoencoder the VAE extends, from PCA to masked
   autoencoders.
3. **A forger and a critic** ({doc}`4.7 <notes4-gan>`). Train one network to make fakes and another to
   catch them, until the fakes are hard to catch. This is the generative adversarial network (GAN).
4. **Clean up noise, step by step** ({doc}`4.8 <notes6-diffusion-basics>`). Start from pure noise and remove a
   little at a time. This is diffusion. Sections 4.9 to 4.11 then follow it into practice: a model that turns a
   caption into a picture, the transportation papers that use diffusion, and where your own engineering knowledge
   can steer it.

Each answer fixes a weakness of the one before it, so the order matters. At the end of section 4.7 the first
three are scored side by side on the same held-out heatmaps.

(gen-autoregressive)=
## The first answer: one cell at a time

Now the first answer in full: generate a heatmap one cell at a time, each cell drawn from a distribution that depends
on every cell already decided. It is the training objective of the GPT in {doc}`2.4 <../module2/notes4-gpt>` with a
new kind of token. Every result below comes from a 379,033-weight transformer trained on 3,200 of the CTM heatmaps
and scored on 400 it never saw.

### Any order will do: the chain rule

```{figure} ../_static/figures/GenAR_Chain_Rule.png
:alt: Two 4 by 4 grids. Left, cells numbered row by row with the chain p(x1) p(x2 given x1) and so on. Right, the same cells numbered column by column with a different chain.
:width: 100%

Two orders, two different chains of conditionals, one joint distribution.
```

Language comes with an order: word one, word two, word three. A model that writes one word at a time,
each from the words before it, fits text naturally. A heatmap seems different. Which cell is first?

It does not matter, because of a rule from probability that holds for any set of variables. The joint
distribution of $N$ variables can always be written as a chain of conditionals:

$$
p(x_1, x_2, \dots, x_N) = p(x_1)\; p(x_2 \mid x_1)\; p(x_3 \mid x_1, x_2) \cdots p(x_N \mid x_1, \dots, x_{N-1})
$$

You may number the variables in any order you like before applying it. Row by row, column by column, a
spiral, or at random: each gives a different chain and every one is exactly equal to the same joint.
**The order is a choice you make, not a property of the data.**

Two things are easy to confuse here. A heatmap has no natural *sequence*, but it has very strong
*neighbourhoods*: a cell looks like the cells around it. Your convolution kernels in Module 1 and the
ViT patch grid in 2.7 were built on that. Order and locality are separate questions.

For traffic there is one axis that does come with a natural order: time. The rest of this page decodes
the heatmap **time step by time step**, and within a time step from upstream to downstream. Every cell
is then predicted from the whole past of the road plus the cells upstream of it at the same moment.

### Learning the conditionals is next-cell prediction

```{figure} ../_static/figures/GenAR_Next_Cell.png
:alt: Left, a test heatmap filled in up to one cell marked with a question mark. Middle, a causal transformer. Right, a bar chart giving a probability for each of 25 speed bins, with the bin that really happened marked.
:width: 100%

The model's answer for one cell of a test heatmap: a probability for each 3-mph speed bin. The cell shown is
the test cell, after the sixth time step, where the model splits its bets most evenly between jammed and free.
```

The model never sees the 400 conditionals as separate problems. It learns one function: *given the
cells decided so far, a distribution over the next cell.* The same weights produce $p(x_1)$,
$p(x_2 \mid x_1)$ and every conditional after them.

The function is the GPT of {doc}`2.4 <../module2/notes4-gpt>` with three changes. A token is a cell's
speed, not a word. There are 25 possible tokens: speeds rounded into bins
3 mph wide. And position means a place in the heatmap, not a place in a sentence.
The causal mask is unchanged: when the model predicts cell $i$ it can attend to cells $1$ to $i-1$ and
nothing later.

**Why bins, not one predicted speed.** A regression head would output one number, the model's average
guess. To *generate* you need a distribution: several possible speeds with their chances, so you can
draw from it. Cutting speed into bins turns each prediction into a choice among 25
alternatives, which is a multinomial logit, the model you already use for mode choice. The cost is that
nothing finer than 3 mph can be expressed.

The figure shows why the distribution matters. In this test heatmap the queue from the bottleneck at the downstream end is spreading back upstream, and
from the cells decided so far the model cannot tell whether it reaches this cell at this time step or a later one. It splits its bets: **0.45** on jammed (30 mph
or less) and **0.54** on free flow (48 mph or more), and almost nothing in
between. The queue did arrive; the bin that really happened received 0.34. A regression would
have answered with the average of these odds, about 45 mph, a speed this cell never takes. Most cells are nothing like this one: over all test cells, the median probability
given to the bin that really happened is 0.999.

**The labels are free.** The training label for each position is just the cell that comes next. Every
heatmap therefore supplies 400 labelled examples that nobody annotated: the same
self-supervision that let GPT and BERT learn from raw text.

### The training loss is the likelihood

The loss is cross-entropy on every cell, added up:

$$
\mathcal{L}(\theta) = -\sum_{i=1}^{400} \log p_\theta(x_i \mid x_1, \dots, x_{i-1}) = -\log p_\theta(x)
$$

| symbol | in this heatmap |
|---|---|
| $x_i$ | the speed bin of cell $i$: one of 25, 3 mph wide |
| $i$ | position in the time-first order, 1 to 400 |
| $p_\theta(x_i \mid \dots)$ | the probability the model gave to the bin that really happened |
| $\theta$ | the model's 379,033 weights |

*In words:* score each cell by how much probability the model gave to the bin that really happened, and
add up the surprise over all 400 cells. Because of the chain rule, that sum is exactly the
surprise of the whole heatmap.

That second equality is the payoff of the chain rule. Training on next-cell prediction is **maximum
likelihood for the joint distribution**, and it needs no labels. It is also the reason this family of
models can be scored exactly, which the next sections use.

:::{admonition} Going deeper &mdash; why the sum is the joint
:class: dropdown
Take logs of the chain rule. The log of a product is the sum of the logs, so
$\log p(x) = \sum_i \log p(x_i \mid x_{<i})$. Each term is conditioned on everything before it; drop
the conditioning and the sum becomes $\sum_i \log p(x_i)$, the marginals, which describe the
shuffled panel of the joint-versus-marginals figure above. Measured in bits (logs base 2), the average of
$-\log_2 p(x_i \mid x_{<i})$ over cells is the *bits per cell* used below.
:::

### Train in one pass, generate in 400

```{figure} ../_static/figures/GenAR_Train_vs_Generate.png
:alt: Left, training: a real heatmap goes in and all 400 next-cell guesses are checked in one forward pass. Right, generating: four snapshots of a sample from the trained model with 100, 200, 300 and 400 cells decided.
:width: 100%

The same network used two ways. The snapshots on the right are a real sample from the trained model.
```

In training you already have the real heatmap, so all 400 guesses can be checked in a single
forward pass: the causal mask makes sure guess $i$ only sees real cells $1$ to $i-1$. This is called
*teacher forcing*.

To generate there is no real heatmap. You draw cell 1, feed it back, draw cell 2, feed both back, and so
on: **400 forward passes in a row for one heatmap**. Engineering tricks make
each pass cheaper (the model can reuse what it computed for earlier cells), but they cannot remove the
sequence. These models train fast and sample slowly, and a real corridor-day has far more than
400 cells.

### How surprised is each model by real test heatmaps?

```{figure} ../_static/figures/GenAR_Bits_Ladder.png
:alt: Horizontal bars of bits per cell on the test heatmaps. Knows nothing 4.64; each cell on its own 3.20; a local CTM-shaped rule; the transformer.
:width: 100%

Bits per cell on 400 held-out heatmaps. Lower means the model is less surprised by real data.
```

Because the loss is the likelihood, an autoregressive model gives an exact score: how surprised it is
by real heatmaps it never trained on. We report it in **bits per cell**. One way to read bits: add them up over a whole heatmap, and the total is roughly how many yes/no answers it
takes to pin that heatmap down when the model's probabilities choose the questions. Bits per cell is that total
divided by 400.

The ladder has three baselines, all scored on the same test heatmaps and the same 3-mph bins.

- **Knows nothing: 4.64 bits.** Twenty-five equally likely bins; $2^{4.64} \approx 25$.
- **Each cell on its own: 3.20 bits.** Each cell's own histogram from the training
  heatmaps, cells independent. These are the marginals of the shuffle experiment above.
- **A local rule: 0.64 bits.** A small network (27,609 weights) that
  predicts each cell from three cells only: the speeds of itself and its two road neighbours one time step
  earlier, plus which road cell it is. Those are the cells a CTM update reads, but this is a limited version: one
  time step here is six CTM updates, free-flow traffic crosses three cells in one step, and in free flow the speed
  says nothing about density. It is a physics-shaped baseline, not a strawman.

The transformer, which may look at every cell already decided, reaches **0.40 bits per
cell**. Over a whole heatmap that is about 160 bits, against
1,279 for the marginals.

Two readings matter. First, most of the information is local: the CTM-shaped rule closes
91% of the gap between the marginals and the transformer. Second, the rest must
come from what the local rule cannot see. The transformer also sees the cell just decided upstream at
the same time step, cells further along the road, and the longer past, where clues such as whether the
downstream bottleneck has already switched on would show up. These experiments do not say which of those
it uses most; that would take a further test, such as hiding parts of the context and measuring the cost.

### Where the model pays its bits

```{figure} ../_static/figures/GenAR_Where_Bits_Go.png
:alt: A 20 by 20 map of average bits per cell over the test heatmaps; the first time step is darkest.
:width: 100%

The first time step and the downstream end are expensive. Elsewhere, the past mostly decides the future.
```

Averaging the surprise cell by cell over the test heatmaps shows where the uncertainty is. The first
time step costs **2.52 bits per cell**. Nothing earlier exists to lean on, so the
model must guess the road's starting state, and those 5% of the cells hold
**31% of all the bits**. The top row, the downstream end where the bottleneck sits,
costs 1.07 bits per cell after the first step: nothing upstream tells the model when
the bottleneck will switch on. Everywhere else costs 0.25.

That is what a traffic engineer would expect, and it has a practical echo: forecasts and simulations
are most uncertain where the initial state is poorly known, after a detector outage or in the first
minutes of a simulation run.

### Spot the fake

```{figure} ../_static/figures/GenAR_Spot_The_Fake.png
:alt: Eight heatmaps labelled A to H, four real held-out ones and four samples from the transformer, shuffled.
:width: 100%

Four held-out real heatmaps and the first four samples the model drew, shuffled. Not picked.
```

Try it before reading on: which four did the model make? Everything is rounded to the same 3-mph bins,
so rounding gives nothing away, and the samples were not chosen: they are the first four the model drew.

:::{admonition} Answer
:class: dropdown
The transformer made A, B, F, G. The real held-out heatmaps are C, D, E, H.
:::

Being hard to tell apart by eye is necessary and not nearly sufficient. People judge a handful of
samples on how sharp they look. They cannot see whether the model covers *all* the kinds of traffic in
the data, or whether it is quietly copying training heatmaps. Section 4.7 measures both.

:::{admonition} Before you trust this result
:class: warning
**What is the baseline?** Not "knows nothing", which any model beats, but the local CTM-shaped rule at
0.64 bits per cell. The transformer at 0.40 beats it; whether that
margin is worth 400 sequential passes per heatmap is a judgment about your
application.

**How was the data split, and why is that honest?** 3,200 / 400 / 400
whole heatmaps. Each heatmap is its own simulation run with its own knobs, so no test heatmap shares a
run with a training one. The model was kept at its best validation score and the test set was scored
once. That best score came at the last of 30 epochs: validation was still improving when
training stopped, so 0.40 bits per cell is not this model's limit, only what
30 epochs bought.

**What does it do on the ugly cases?** Copying: its samples sit 4.07 mph
(RMS per cell) from their nearest training heatmap, while real test heatmaps sit
3.93 mph from theirs, so it is not reproducing its training
data. The larger caveat is that everything here is one simulator on one road. A real detector feed has
sensor noise, incidents, lane changes and missing data, and the model has seen none of them.
:::

:::{admonition} Fit card &mdash; Autoregressive generation
:class: tip
**Idea in one sentence.** Generate one cell (or token) at a time, each drawn from a distribution that
depends on everything already decided.

**Why it works.** The chain rule makes any order an exact factorization of the joint; each step is an
ordinary classification, trained with free labels.

**Fits these tasks.** Generating traffic states or trajectories, forecasting (the unknown part comes last in
the order), and scoring how unusual an observation is (*generation*, *prediction*). A detector gap with data
after it needs a model that can also use the later cells, such as a masked, BERT-style one.

**Needs this data.** Many unlabelled examples from detector or trajectory archives; a choice of token
(what is one cell?) and of order.

**Breaks when.** Outputs are long (one pass per token); early mistakes are fed back and carried forward; the
chosen order fights the structure of the data; the unknown cells are not last in the order.

**Keep the classical method when.** A local physical rule already explains most of the variation (here
it closes most of the gap), or conservation must hold exactly, which no sampled model guarantees.
:::

### Two questions that come up

**Does the order matter in practice?** The same transformer was trained a second time, decoding road
cell by road cell (each cell's whole time history before moving downstream). Time first reached **0.40** bits per cell on the test heatmaps; road cell first reached **0.46**, with the same model, the same 30 epochs and the same data. Both are exact factorizations of the same joint, so with unlimited data and a big enough model they would meet. In this run, with one seed for each order and both still improving at the last epoch, time first was ahead. A plausible reason is that it follows cause and effect forward in time; one run does not prove it. Valid is not the same as equally easy to learn.

**Why draw from the distribution instead of taking the most likely bin?** Taking the top bin at every
step gives the blandest heatmap, not a typical one, for the same reason that no real vehicle drives the
"most likely trajectory". To get fields that look like the data you draw from the model's
probabilities, and then diversity becomes something you must measure. This is why generators have a
*temperature* setting that sharpens or flattens the distribution before drawing.

## Check yourself

1. Of the four requests at the top of this page, which would worry you most if the generated data were
   wrong in a way nobody noticed, and what kind of wrong would it be?
2. A vendor shows that every detector's speed histogram in their synthetic data matches the real one.
   What have they shown, and what have they not?
3. An AV team has 40 recorded near-misses at one intersection and wants 10,000. Which is harder to get
   right: samples that look real, or samples that cover the variety? How would you check each?
4. A colleague builds a "generator" that outputs each detector's most likely speed on its own. Name two
   things it gets wrong.
5. Your corridor data has a natural time order. What would you gain, and lose, by decoding road cell by
   road cell instead?

---

Next: {doc}`4.2 Gaussians and mixture models <notes2a-gaussians>` &mdash; one bell, then a mixture of bells: the
simplest model with a hidden cause. The hidden cause leads to the second answer, the VAE, which makes a heatmap in one
pass instead of 400.
