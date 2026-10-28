# 4.6 Deep autoencoders: bending the line

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 4 &middot; Section 4.6</span>
    <span class="notes-card-session">Session: Autoencoders</span>
  </div>
  <p class="notes-card-lede">Put nonlinear layers inside the decoder and the straight line of 4.5 can bend. On a synthetic fundamental diagram, one latent then cuts PCA's flow error from 315 to 47&ndash;87 veh/h, yet the latent turns out to be the network's own coordinate, not density. On the heatmaps, depth helps again; this page also shows how to choose the number of latents, and when the latents help another task.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Read it before</h4>
      <ul>
      <li><a href="notes2c-autoencoders.html">4.5 Autoencoders: keep a few numbers, rebuild the rest</a></li>
      </ul>
    </div>
    <div>
      <h4>Interactive companion on this page</h4>
      <ul><li><a href="../_static/companions/Autoencoder_Latent_Companion.html" target="_blank" rel="noopener">Inside the latent layer &#8599;</a></li></ul>
    </div>
  </div>
</div>

## What this section covers

- The deep autoencoder (Bishop's Figure 19.2): nonlinear layers that let the decoder trace a curve
- What a manifold is, with the fundamental diagram and the heatmaps as examples
- The price of depth: local minima, and choosing $M$ before training
- Example 1, a synthetic fundamental diagram: PCA's straight line against a bent one, and whether the one latent is
  density
- Example 2, the heatmaps: PCA against a deep autoencoder with the same number of latents
- How to choose the number of latents $M$, and whether theory can pick it
- Whether the latents help other tasks, and when to keep PCA
- Inside the latent layer, hands on (interactive companion)

{doc}`Section 4.5 <notes2c-autoencoders>` showed why a two-layer network can only draw a straight line: its decoder
is linear. Put nonlinear layers inside the decoder as well, and the output can follow a curve. That is Bishop's
Figure 19.2, a *deep autoencoder*: two successive mappings, $F_1$ from the data to the latents and $F_2$ back.

```{figure} ../_static/figures/AEB_Deep_Net.png
:alt: A row of layers, 2 inputs (density and flow), two tanh layers of 64, one linear latent, two tanh layers of 64, and 2 linear outputs, with brackets marking F1, the encoder, and F2, the decoder. On the right, two small sketches: a linear decoder draws a straight line through curved data; tanh layers in F2 follow the curve.
:width: 100%

Bishop and Bishop (2024), Figure 19.2, sized for the fundamental-diagram example below.
```

The latent layer and the outputs can stay linear. The tanh layers between them do the bending. As $z$ slides
through its range, $\mathbf{y} = F_2(z)$ now traces a curve in data space instead of a line. With $M$ latents, it
traces a curved $M$-dimensional surface: a *manifold*. So a deep autoencoder is a nonlinear PCA. PCA is the special
case where the curve is straight.

## What is a manifold?

A smooth surface with few dimensions that sits inside a space with many. Zoom in on any small piece and it looks
flat, the way a town map can ignore the Earth's curve.

```{figure} ../_static/figures/AEB_Manifold.png
:alt: Left, synthetic fundamental-diagram points in the density-flow plane lying near the triangular curve, with six numbered gold dots marking positions along it and an inset showing that a small piece of the curve is nearly straight. Right, a curved sheet drawn in 3-D with dots on it, and two arrows z1 and z2 along the sheet as its coordinates.
:width: 100%

Two manifolds. Left: fundamental-diagram readings lie near a 1-D curve in a 2-D plane. Right: heatmaps lie near a
curved sheet of few dimensions in a 400-D space, drawn here in 3-D.
```

The fundamental diagram is the traffic example. Each reading is a point in the 2-D (density, flow) plane, yet real
readings lie near a 1-D curve, so one number, the position along the curve, pins each one down. Our heatmaps are
points in a 400-D space, but the simulator makes each one from five settings plus some random starting traffic, so
they lie near a surface of few dimensions inside it. A deep autoencoder's decoder is its guess at that surface,
and the latents are coordinates on it.

## The price of depth

The loss now has poor valleys (*local minima*) where training can stop, so different random starts give different
answers. You must also choose $M$ before training. PCA has neither problem. It has one best answer, and one fit
gives every direction at once, ranked by the variance each one explains. So with PCA you can pick $M$ after the fit:
keep the top $M$ directions for any $M$, and read the share of variance they explain off the eigenvalues, as in
{doc}`4.5 <notes2c-autoencoders>`. With an autoencoder, each $M$ is a new training run. How to choose it comes after
Example 2.

## Example 1: the fundamental diagram, on synthetic data

Detector readings in the (density, flow) plane lie near a curve, not a line. Flow rises with density up to
capacity, then falls as the queue packs in. **The points here are synthetic, not real detector readings**, so that
the true curve and every point's true density are known. We drew 3,000 of them from the triangular fundamental
diagram the course's CTM uses: free-flow speed 75 mph, wave speed 15 mph and jam density 200 veh/mi/ln, so capacity
is 2,500 veh/h/ln at 33.3 veh/mi/ln. We then added random noise to every point, like a detector's measurement
error (spread 3 veh/mi/ln in density and 100 veh/h/ln in flow), trained on 2,400 points and tested on 600. Both
models keep one latent per point.

```{figure} ../_static/figures/AEB_FD_Bend.png
:alt: Two panels of flow against density on the 600 synthetic test points. Left, PCA rebuilds every point onto one straight slate line along the congested branch; free-flow points are rebuilt far away, flow error 315 veh/h, free flow 682. Right, the deep autoencoder rebuilds points along a green bent line that follows both branches, flow error 87 veh/h, with a small shelf of misplaced points near the peak.
:width: 100%

One number per point, synthetic data. Grey lines join a test point to its rebuild.
```

PCA's straight line keeps 80% of the variance, yet misses flow by 315 veh/h. On the free-flow branch it misses by
682 veh/h, because the line runs along the congested branch. The deep autoencoder bends its line around the peak.
Five random starts gave flow errors of 47 to 87 veh/h. The figure shows the start with the lowest *training* loss,
which happened to be the worst on test, at 87 veh/h: still about a quarter of PCA's error. Its worst error is a
single congested point (99 veh/mi/ln, 1,505 veh/h/ln) that the encoder sent to the wrong end of the curve. That one
point is 64% of the squared flow error; without it the error is 52 veh/h. Near the peak, where the two branches
meet, a small shelf of states is also misplaced. The spread across starts is the local-minimum risk in action.

### Is the one latent density?

Traffic theory says that one number, density, fixes the state on the fundamental diagram, and the autoencoder
agrees that one number is enough. But is its number density? The data are synthetic, so we know every point's true
density and can check. The figure colours each test point by its latent, and plots the latent against true density.

```{figure} ../_static/figures/AEB_FD_Latent.png
:alt: Left, flow against density with test points coloured by their latent z from light sand, about minus 3, to dark green, about 4; the decoder's curve is thick where readings use it and dotted where no reading's z falls, cutting across the empty middle of the plane. Right, the latent against true density; congested points fall from about 4 near the critical density to about minus 3 near jam density; free-flow points sit in separate pieces. Rank correlation 0.996 on congested points, 0.84 on all points.
:width: 100%

Left: where the latent lives on the curve. Right: the latent against each point's true density.
```

On the congested branch, $z$ falls as density rises, almost without exception: the rank correlation is 0.996 in
size. A rank correlation (Spearman's) asks only whether two lists come in the same order. A value of 1 means a
higher density always comes with a lower $z$, or always with a higher one, at any pace. So on that branch $z$ is
density, flipped and unevenly stretched. The free-flow branch is a different story. The network cut it into
pieces, parked them at different places along $z$, and put congested states between them. Over all points the rank
correlation falls to 0.84.

All five random starts did the same: 0.995 to 0.996 on the congested branch, 0.83 to 0.85 over all points, and the
free-flow branch always in pieces. So **the latent is the network's own coordinate along the curve, not density.**
The loss only scores the rebuild, and every coordinate that rebuilds equally well scores the same. The dotted lines
show a price: $z$ values between the pieces decode to states between the branches, which no road produces. The
VAE of {doc}`4.8 <notes3b-vae-basics>` takes up that problem. With real detector data there is no true density to compare
against, so you could not even run this check: do not read latents as physical variables.

## Example 2: the heatmaps

The same pattern holds with 400 numbers per traffic state. Here the deep autoencoder has the course's shape,
400 &rarr; 96 &rarr; $M$ &rarr; 96 &rarr; 400, with ReLU activations. Errors are RMS per cell on the 400 test heatmaps:

| Latents kept ($M$) | PCA (mph) | Deep autoencoder (mph) |
| --- | --- | --- |
| 0 (the average heatmap) | 23.76 | 23.76 |
| 2 | 9.85 | 7.29 |
| 8 | 4.91 | 2.87 |

With the same number of latents, the deep autoencoder's error is 26% lower at 2 and 41% lower at 8. The gain is
spread over all cells, and queue fronts (the 10% of cells where speed changes most between neighbours, at least
14.6 mph) stay the hardest cells for both: at 8 latents, 9.3 mph for PCA against 5.5 mph for the autoencoder. The
2-latent autoencoder is the course model of the VAE lab and of the companion at the end of this page; it drew the
first figure of {doc}`4.5 <notes2c-autoencoders>`.

## How many latents? Choosing M

$M$ is not something the data tell you before training. It is a setting you choose, like the number of hidden
units or the learning rate. The standard way is to train with several values of $M$ and score each one's rebuild
error on validation data, heatmaps the model never trained on. Then take the smallest $M$ past which the error stops
falling much, or the smallest $M$ that meets the accuracy your task needs.

```{figure} ../_static/figures/AEB_Choose_M.png
:alt: Rebuild error on the 400 validation heatmaps against M from 1 to 32 on a log scale. The deep autoencoder (green, mean of three starts, small dots for each start) falls steeply from 9.6 mph at M = 1 to 3.7 at M = 4, then slowly to 2.1 at 32. PCA (slate, dashed) falls from 12.0 to 2.3. A sand band marks M = 5, the number of simulator settings; a dotted line shows PCA needs 24 directions to match the autoencoder's 8.
:width: 100%

Choosing $M$ on validation heatmaps: one training run per $M$ for the autoencoder, one fit for every $M$ with PCA.
```

On the heatmaps the deep autoencoder's error falls fast up to $M$ = 4, from 9.6 mph with one latent to 3.7 mph with
four. After that it falls slowly: 3.4 mph at 5, 2.8 at 8 and 2.1 at 32. So $M$ = 4 to 8 is a sensible choice here,
and past that each extra latent buys little. PCA needs 24 directions to match what the autoencoder does with 8. (The
chart scores validation heatmaps with three fresh starts per $M$, so its values at 2 and 8 differ slightly from the
test-set table above.)

**Can theory pick M?** It can suggest where to look. The fundamental diagram has one state variable, density, so
$M$ = 1 is the natural guess, and Example 1 showed that one latent is enough there. Our simulator makes each heatmap
from five settings (starting density, inflow, bottleneck capacity, bottleneck start and length) plus random starting
traffic, and the curve bends near $M$ = 4 to 5. But theory gives a guess, not the answer. Some settings barely change
a heatmap (the bottleneck's length changes it least). Real data carry effects that no theory lists, such as sensor
noise, incidents and weather. And the latents need not line up with the theory's variables anyway, as Example 1
showed. PCA is easier: one fit gives every eigenvalue, so you read the share of variance that the top $M$ directions
keep and choose $M$ without retraining.

## Do the latents help other tasks?

Yes, and that is a main reason to train an autoencoder. Train it once on unlabelled data, then feed its latents to
a small model for a task: a classifier, a predictor, a clustering. This reuse is called *representation learning*,
the same pretrain-then-reuse idea as the pretrained backbones of Module 1 and BERT in Module 2.

But do the latents do the job a classifier's hidden layer does? A classifier is trained with labels, so its hidden
layer pulls the classes apart and throws away whatever does not help tell them apart. An autoencoder sees no
labels. Its latents keep whatever helps the rebuild most, which means the largest variations in the data, whether
or not they matter for your label.

To test this, each heatmap gets two labels from the simulator's settings, which we know because the data are
simulated. *Heavy start*: the road starts at 30% of jam density or more (60 veh/mi/ln), against light. *Severe
bottleneck*: the bottleneck lets through less than 60% of capacity (1,500 veh/h/ln), against mild. The figure plots
the 400 test heatmaps in two 2-number spaces: the course's 2-latent autoencoder, and a classifier with the same
encoder shape (400 &rarr; 96 &rarr; 2) trained on the 3,200 labelled training heatmaps to tell severe from mild.
"Best straight line" is the test accuracy of a logistic regression fitted in that plane on the training heatmaps.

```{figure} ../_static/figures/AEB_Downstream.png
:alt: Three scatter plots of the 400 test heatmaps. Left, the autoencoder's two latents coloured by starting traffic; heavy starts cluster at the top, light starts below; a straight line gets 93% right against 57% for guessing the larger class. Middle, the same latents coloured by bottleneck severity; severe and mild are mixed; 64% against 53%. Right, a classifier's two hidden numbers, trained to tell severe from mild; the points lie along one line with mild at one end and severe at the other; 91% against 53%.
:width: 100%

Two numbers per test heatmap. Left and middle: the autoencoder's latents. Right: a classifier's two hidden numbers.
```

| Two numbers per test heatmap | Heavy vs light start | Severe vs mild bottleneck |
| --- | --- | --- |
| Guessing the larger class | 57% | 53% |
| Autoencoder latents (no labels in training) | 93% | 64% |
| PCA, 2 directions | 95% | 66% |
| Classifier trained on severity: its 2 hidden numbers | 72% | 91% |
| Classifier trained on starting traffic: its 2 hidden numbers | 98.5% | 51% |
| For reference: all 400 cells, straight line | 99.5% | 80% |

The autoencoder's latents sort heatmaps by how much traffic starts on the road, the change that moves the most
cells. So a straight line in its latent plane tells heavy from light starts 93% of the time. The latents barely see
how severe the bottleneck is: 64%, against 53% for always guessing "severe". The classifier trained on severity gets
91%, and in exchange keeps less of the starting traffic (72%). Trained on starting traffic instead, a classifier's
two numbers keep nothing about severity (51%). PCA, which also keeps the largest variations, behaves like the
autoencoder. So the two share a spirit, squeezing the input into a few numbers, but not a goal: **each keeps what
its own loss rewards.**

**When to reuse latents.** Reuse them when labels are few and your label follows a large variation in the data.
With only 100 labelled heatmaps, a straight line on the 8-latent autoencoder of Example 2 called heavy starts right
97% of the time, against 96% for the same classifier trained from scratch on those 100. For bottleneck severity it
reached 77%, against 81% from scratch (averages over five random draws of 100). The 2-latent autoencoder did worse
on both, 93% and 65%. So first check whether your label is visible in the latents, with a quick straight-line test
like this one. When it is not, train or fine-tune for the task, as Module 1 did with pretrained backbones and
Module 2 with BERT.

**When to keep PCA.** If the data lie close to a flat sheet, as the two-detector cloud of 4.5 does, PCA is as good.
It is also exact, fast, the same on every run, and it ranks its directions by importance. Reach for depth when the
data bend, and show the bend with a validation curve.

(autoencoder-latent-layer)=
## Inside the latent layer: from PCA to the VAE, hands on

The companion below lets you check the claims of 4.5 and of this page one step at a time, starting from a model
you already know. It begins with PCA on the two I-405 detectors (here over 2,112 readings, so its numbers differ
slightly from the six-reading example), trains the same model as a two-layer network in your browser, bends it with
depth on a synthetic fundamental diagram, and then asks whether you can draw new latents. Its last tab uses the
module's 2-latent autoencoder and the VAE of {doc}`4.8 <notes3b-vae-basics>`, so it doubles as the bridge to that page. The
companion calls the latents *codes*, the word AI papers use.

Five results to look for:

- PCA is an autoencoder with a straight-line decoder. A two-layer network trained on the rebuild loss lands on the
  same line, with the same 4.41 mph RMS error per station.
- Each reading's latent is computed from the input with the current weights, so every training step moves all of
  the latents.
- With tanh and with no activation, the network rebuilds equally well, but its latents end on very different
  scales: from &minus;0.24 to 0.23, against &minus;2.41 to 1.48. Nothing in the rebuild loss decides where the latents
  live.
- A deep autoencoder bends the line to follow the fundamental diagram. But latents between its clumps decode to
  states no road produces, and latents drawn from a standard bell curve miss the real mix of densities by 45%.
- The VAE pulls its latents into the bell: 94.6% of its training latents sit inside the radius-2 circle, against
  11.7% for the plain autoencoder on these heatmaps.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion &mdash; Inside the latent layer</span>
    <a href="../_static/companions/Autoencoder_Latent_Companion.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/Autoencoder_Latent_Companion.html"
          title="Inside the latent layer: from PCA to autoencoders to the VAE" loading="lazy"></iframe>
</div>

:::{admonition} Before you trust this result
:class: warning
**What is the baseline?** PCA with the same number of latents, and for the heatmaps the average heatmap
(23.76 mph). For the label tests, guessing the larger class, and a classifier trained for the label.

**How was the data split, and why is that honest?** The fundamental diagram used 2,400 training and 600 test points.
The heatmaps were split by whole heatmap into 3,200 training, 400 validation and 400 test heatmaps (seed 7, as in
the VAE lab). Every model saw only the training heatmaps; the curve for choosing $M$ scores validation heatmaps only,
and the label tests fit their straight lines on training heatmaps and score test heatmaps.

**What does it do on the ugly cases?** The fundamental diagram and the heatmaps are synthetic: one simulator, one
uniform 4-mile road. Queue fronts are the worst cells for both PCA and the autoencoder. Results move between random
starts: 47 to 87 veh/h on the same data. And a latent that tracks density on one branch says nothing on the other.
:::

## Check yourself

1. A district wants to store 5-minute speeds from 300 detectors more cheaply, and to rebuild them later. Would you
   start with PCA or a deep autoencoder? Which number would you compute first to decide?
2. You have three years of unlabelled corridor heatmaps and only 120 heatmaps labelled "incident" or "no incident".
   Would you fit the classifier on autoencoder latents or train it from scratch? What would you check about the
   latents first?

---

Next: {doc}`4.7 Stopping the copy <notes2e-copying>` &mdash; when the middle is as wide as the input, the network can simply copy. Four ways
to stop it.
