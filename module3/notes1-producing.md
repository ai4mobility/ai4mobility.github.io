# 3.1 From predicting to producing

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 3 &middot; Section 3.1</span>
    <span class="notes-card-session">Session: Oct 22</span>
  </div>
  <p class="notes-card-lede">Every model so far looked at data and returned a label. A generative model returns the data itself. This page says what that changes, what "realistic" has to mean for a traffic state, and lays out the four answers this module works through. The running example for the whole module is a set of 4,000 simulated speed heatmaps.</p>
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
from every model in Modules 1 and 2, and it needs a different kind of model.

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
:alt: Left, a real CTM heatmap with a clear queue front. Right, the same 400 cells each drawn independently from their own distribution, which looks like noise.
:width: 100%

Each cell on the right has exactly the right distribution of speeds. The shockwave is gone.
```

Here is an experiment that says what a generative model must get right. Take the 4,000
heatmaps. For each of the 400 cells separately, shuffle that cell's value across the
4,000 heatmaps. A shuffle keeps every cell's own spread of speeds exactly: each cell's average and standard deviation are
unchanged, apart from computer rounding. What it destroys is every relationship between cells.

The result, on the right of the figure, is not a traffic state. In the real heatmaps, road cells next
to each other differ by **4.06 mph** on average and are correlated at
0.942. In the shuffled ones they differ by **25.63 mph** and are
correlated at 0.059: free flow sits next to a jam with no front between them.

The distribution of a single cell is called its *marginal*. The distribution of all 400
cells together, including how they move together, is the *joint*. The experiment shows that
everything a traffic engineer cares about lives in the joint. That queues grow backwards at a finite
wave speed, that a front is continuous, that a cell looks like its neighbours a moment earlier: none of
it is visible in any single cell. So when we say *generating a heatmap is drawing a sample from a joint
distribution*, the word "joint" carries the whole idea. A model that matches the marginals and nothing
else produces the right-hand panel.

:::{admonition} Going deeper &mdash; how big is the joint?
:class: dropdown
Round each speed to one of 25 bins 3 mph wide. A heatmap is then one choice out of $25^{400}$, about
$10^{559}$: a number with 560 digits. No table can list the probability of each one,
and almost all of them look like the right-hand panel. A generative model has to put nearly all of its
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

1. **One cell at a time** ({doc}`3.2 <notes2-autoregressive>`). Decide the first cell, then the second
   given the first, and so on. This is how GPT writes text, applied to a heatmap.
2. **A few hidden knobs** ({doc}`3.3 <notes3-vae>`). Compress each heatmap into a few numbers, learn to
   rebuild it from them, then make new heatmaps by drawing new numbers. This is the variational
   autoencoder (VAE).
3. **A forger and a critic** ({doc}`3.4 <notes4-gan>`). Train one network to make fakes and another to
   catch them, until the fakes are hard to catch. This is the generative adversarial network (GAN).
4. **Clean up noise, step by step** (next session). Start from pure noise and remove a little at a time.
   This is diffusion.

Each answer fixes a weakness of the one before it, so the order matters. At the end of section 3.4 the first
three are scored side by side on the same held-out heatmaps.

## Check yourself

1. Of the four requests at the top of this page, which would worry you most if the generated data were
   wrong in a way nobody noticed, and what kind of wrong would it be?
2. A vendor shows that every detector's speed histogram in their synthetic data matches the real one.
   What have they shown, and what have they not?

---

Next: {doc}`notes2-autoregressive` &mdash; the first answer, one cell at a time, and an exact way to
score it.
