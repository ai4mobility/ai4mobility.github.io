# 4.5 Deep autoencoders: bending the line, stopping the copy

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 4 &middot; Section 4.5</span>
    <span class="notes-card-session">Session: Autoencoders</span>
  </div>
  <p class="notes-card-lede">Put nonlinear layers inside the decoder and the straight line of 4.4 can bend. On a synthetic fundamental diagram, one latent then cuts PCA's flow error from 315 to 47&ndash;87 veh/h, yet the latent turns out to be the network's own coordinate, not density. On the heatmaps, depth helps again; the page shows how to choose the number of latents, and when the latents help another task. Then the trap: with as many latents as inputs, an autoencoder can simply copy, and a near-perfect rebuild proves nothing. Beyond a narrow middle there are three standard ways out: charge for every latent that fires (sparse), feed in noise and score against the clean heatmap (denoising), or hide most of the heatmap and score only what was hidden (masked, BERT's idea). The denoiser halves the best tuned blur's error; the masked autoencoder halves the classical gap filler's. The page closes with where autoencoders break, a fit card and applications.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Read it before</h4>
      <ul>
      <li><a href="notes2c-autoencoders.html">4.4 Autoencoders: keep a few numbers, rebuild the rest</a></li>
      <li><a href="../module2/notes5-bert.html">2.5 BERT: pretrain, then adapt</a>, for the masking idea</li>
      </ul>
    </div>
    <div>
      <h4>Companion and lab</h4>
      <ul><li><a href="../_static/companions/Autoencoder_Latent_Companion.html" target="_blank" rel="noopener">Inside the latent layer &#8599;</a>, on this page</li>
      <li><a href="../labs.html">Training the denoiser</a>, for the denoising idea behind diffusion</li></ul>
    </div>
  </div>
</div>

## What this section covers

- The deep autoencoder (Bishop's Figure 19.2): nonlinear layers that let the decoder trace a curve
- What a manifold is, with the fundamental diagram and the heatmaps as examples, and the price of depth
- Example 1, a synthetic fundamental diagram: PCA's straight line against a bent one, and whether the one latent is
  density
- Example 2, the heatmaps: PCA against a deep autoencoder with the same number of latents; how to choose $M$
- Whether the latents help other tasks, and when to keep PCA
- Inside the latent layer, hands on (interactive companion)
- The copying trap, and why a good rebuild proves little in 400 dimensions
- The sparse autoencoder: a price on every latent that fires
- The denoising autoencoder: corrupt the input, rebuild the clean version; and why its arrows lead to diffusion
- The masked autoencoder: BERT's self-supervision for heatmaps, used to fill detector gaps
- Where autoencoders break, a fit card, applications in transportation, and the topic in seven lines

{doc}`Section 4.4 <notes2c-autoencoders>` showed why a two-layer network can only draw a straight line: its decoder
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
{doc}`4.4 <notes2c-autoencoders>`. With an autoencoder, each $M$ is a new training run. How to choose it comes after
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
VAE of {doc}`4.6 <notes3b-vae-basics>` takes up that problem. With real detector data there is no true density to compare
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
first figure of {doc}`4.4 <notes2c-autoencoders>`.

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

**When to keep PCA.** If the data lie close to a flat sheet, as the two-detector cloud of 4.4 does, PCA is as good.
It is also exact, fast, the same on every run, and it ranks its directions by importance. Reach for depth when the
data bend, and show the bend with a validation curve.

(autoencoder-latent-layer)=
## Inside the latent layer: from PCA to the VAE, hands on

The companion below lets you check the claims of 4.4 and of this page one step at a time, starting from a model
you already know. It begins with PCA on the two I-405 detectors (here over 2,112 readings, so its numbers differ
slightly from the six-reading example), trains the same model as a two-layer network in your browser, bends it with
depth on a synthetic fundamental diagram, and then asks whether you can draw new latents. Its last tab uses the
module's 2-latent autoencoder and the VAE of {doc}`4.6 <notes3b-vae-basics>`, so it doubles as the bridge to that page. The
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

(stopping-the-copy)=
## The copying trap

If $z$ has as many latents as the input has numbers, copying $x$ is a perfect answer to the loss.
{doc}`Section 4.4 <notes2c-autoencoders>` showed it: two hidden units for two speeds gave 0.04 mph error and
learned nothing about the road. Something has to make copying a bad answer. There are four standard ways.

```{figure} ../_static/figures/AEB_Four_Ways.png
:alt: Four cards. 1, use few latents, an hourglass, loss the squared error, sections 4.4 to 4.5. 2, penalise the latents, a wide middle where only 3 of 11 units fire, loss plus lambda times the sum of the absolute latents. 3, corrupt the input, a noisy heatmap in and the clean heatmap as the target. 4, hide most of the input, 6 of 25 patches shown and the error scored on the hidden part.
:width: 100%

The four constraints of Bishop and Bishop (2024), sections 19.1.1 to 19.1.5.
```

Section 4.4 and the first half of this page used the first: fewer latents than input numbers. The rest of this
page covers the other three. In the
three lines of PyTorch from 4.4, each one changes a single line: the sparse penalty adds a term to the loss (3),
denoising changes what goes into the encoder (1), and masking changes which cells the loss scores (3).

## Copying in 400 dimensions

On the heatmaps, take an *over-complete* network, one that is wider in the middle than at its ends:
400 &rarr; 512 &rarr; 400, with ReLU. Trained only to rebuild clean heatmaps, it reaches 1.49 mph on the test
heatmaps after 200 passes, better than any bottleneck above. Has it learned traffic, or learned to copy? Neither,
quite. Fed a checkerboard of 30 and 70 mph cells, a pattern no road produces, it misses by 29.6 mph. A true copier
would miss by 0, and simply answering 50 mph everywhere would miss by 20, so it is not a copier. Fed noisy heatmaps,
it lands 3.49 mph from the truth, so by luck it removes some noise.

```{figure} ../_static/figures/AEB_Copy_Drift.png
:alt: Left, a second copy of the over-complete network trained longer; its error on clean heatmaps falls from 2.46 to 1.49, 1.17 and 1.11 mph after 50, 200, 1,000 and 3,000 passes, while its output from a noisy heatmap drifts from 3.63 and 3.47 up to 4.60 and 6.73 mph from the truth; the noisy input itself is 8.61 mph off. Right, a checkerboard of 30 and 70 mph cells and the outputs of the over-complete network and the 8-latent bottleneck, both a smooth free-flow heatmap about 29.6 and 29.7 mph off.
:width: 100%

Left: the same network trained longer. Right: a pattern it never saw.
```

Now train a second copy of the same network for longer, checking it as it goes. The clean rebuild keeps improving:
1.49, then 1.17, then 1.11 mph after 200, 1,000 and 3,000 passes. But the same network's output for a noisy
heatmap gets steadily worse: 3.47, then 4.60, then 6.73 mph from the truth. The loss only asks for a good rebuild of
heatmaps like the training ones. It says nothing about any other input, so that behaviour is left to chance and to
when you stop. **A good rebuild of training-like heatmaps proves little.** The fixes below write the behaviour you
want into the objective itself.

## Regularising z: the sparse autoencoder

Keep the wide layer of 512 latents, but charge for every one that fires. This is Bishop's equation (19.2):

$$
\tilde{E}(\mathbf{w}) = E(\mathbf{w}) + \lambda \sum_{k=1}^{K} |z_k|
$$

| Symbol | Meaning |
| --- | --- |
| $E(\mathbf{w})$ | the rebuild loss of 4.4 |
| $z_k$ | latent $k$, the activation of hidden unit $k$ for one heatmap (ReLU, so 0 or more) |
| $K$ | the number of latents, here 512 |
| $\lambda$ | the price per unit of activation, set by you |

*In words:* each heatmap pays for every unit it uses, so it uses only the few it needs. Different heatmaps may use
different units. Note that the penalty acts on the activations $z$, not on the weights $\mathbf{w}$ as weight
decay does.

| &lambda; | Units firing per heatmap (of 512) | Units used by any test heatmap | Rebuild error (mph) | Output from a noisy input, error (mph) |
| --- | --- | --- | --- | --- |
| 0 | 182 | 230 | 1.51 | 3.39 |
| 0.003 | 46 | 136 | 1.86 | 3.52 |
| 0.01 | 26 | 82 | 2.16 | 3.75 |
| 0.03 | 13 | 36 | 2.88 | 4.22 |
| 0.1 | 4 | 5 | 5.56 | 6.83 |

&lambda; is a dial for how many latents are in use. At &lambda; = 0.03 each heatmap uses about 13 units, and the rebuild
error equals the 8-latent bottleneck's (2.88 against 2.87 mph). The difference is that each heatmap picks its own
units from a menu of 36. At &lambda; = 0.1 only 5 units are ever used: a tiny fixed set of latents again. Sparsity alone
did not buy noise removal here; the last column gets worse as &lambda; grows. For that, change the task (next
section). The &lambda; = 0 row is a fresh run of the copier's recipe from a different random start, which is why it
differs slightly from the copier's 1.49 and 3.49 mph.

:::{admonition} Going deeper &mdash; why |z| gives exact zeros
:class: dropdown
The L1 penalty $\lambda|z|$ pushes each activation toward zero with the same force $\lambda$, however small it
already is. An L2 penalty $\lambda z^2$ pushes with force $2\lambda z$, which fades near zero, so it shrinks
activations without switching them off. With ReLU units, an activation pushed below zero switches off exactly. That
is why sparse autoencoders use $|z|$. The VAE of {doc}`4.6 <notes3b-vae-basics>` regularises $z$ in yet another way: it
asks the latents to look like draws from a bell curve. Sources: Bishop and Bishop (2024), sections 9.2.2 and 19.1.3.
:::

## Denoising autoencoders: corrupt the input, rebuild the clean version

Feed the network a noisy heatmap but score its output against the clean one (Vincent et al., 2008). Copying now
earns the full noise as its error, so the network has to learn what traffic looks like. With the same
400 &rarr; 512 &rarr; 400 shape that can copy, the denoiser cuts 10 mph of noise per cell down to 2.50 mph: half the
error of the best tuned blur.

```{figure} ../_static/figures/AEB_Denoise.png
:alt: Left, synthetic fundamental diagram with blue arrows; each arrow starts at a point near the curve and points back toward the true green curve, from both sides. Right, four heatmaps of one test case, the clean truth, the noisy input at 9.3 mph from the truth, a tuned blur at 4.4 mph with softened queue fronts, and the denoising autoencoder at 1.8 mph with sharp fronts; over all 400 test heatmaps, blur 5.00 and denoiser 2.50 mph.
:width: 100%

Left: where a denoiser moves each point (synthetic data). Right: one test heatmap with 10 mph of noise per cell.
```

The left panel shows what a denoiser learns, drawn on the synthetic fundamental diagram (a two-input denoiser with
three tanh layers of 64 units, no bottleneck). Each arrow starts at a point and ends where the denoiser moves it.
The arrows point back to the curve from both sides. So the network has learned where real traffic states lie. We
added noise of the size it trained with, about 19 veh/mi/ln and 240 veh/h/ln, to 600 test points. The denoiser cut
their median distance to the true curve from 0.22 to 0.02 (in units of the data's spread). The same network trained
without noise left that distance at 0.22: it copied.

The right panel is one test heatmap. The blur softens the noise and the queue fronts alike. The denoiser removes
the noise and keeps the fronts.

$$
E(\mathbf{w}) = \sum_{n=1}^{N} \big\lVert \mathbf{y}(\tilde{\mathbf{x}}_n,\mathbf{w}) - \mathbf{x}_n \big\rVert^2, \qquad \tilde{\mathbf{x}}_n = \mathbf{x}_n + \boldsymbol{\varepsilon}_n
$$

| Symbol | Meaning |
| --- | --- |
| $\mathbf{x}_n$ | the clean heatmap: the target |
| $\boldsymbol{\varepsilon}_n$ | noise added to every cell: Gaussian, spread 10 mph, drawn fresh each time the heatmap is used |
| $\tilde{\mathbf{x}}_n$ | the corrupted input (clipped to 0 to 75 mph) |
| $\mathbf{y}(\tilde{\mathbf{x}}_n, \mathbf{w})$ | the network's output from the corrupted input |

*In words:* the input is dirty and the target is clean, so the only way to score well is to know what clean traffic
looks like. This is Bishop's equation (19.3). The training code differs from the copier's by one line:

```python
for xb in loader:                                          # clean heatmaps, speed / 75 mph
    noisy = (xb + torch.randn_like(xb) * 10 / 75).clamp(0, 1)   # fresh noise every time
    y = model(noisy)
    loss = 0.5 * ((y - xb) ** 2).sum(1).mean()           # scored against the CLEAN heatmap
    opt.zero_grad(); loss.backward(); opt.step()
```

**Results on the 400 test heatmaps** (10 mph noise per cell; after clipping, the noisy heatmaps sit 8.61 mph from
the truth). "Queue fronts" are the 10% of cells where speed changes most between neighbouring cells, at least
14.6 mph. Settings marked "tuned on validation" were chosen on 400 separate validation heatmaps, never on the test
heatmaps.

| Method | All cells (mph) | Queue-front cells (mph) |
| --- | --- | --- |
| No cleaning: the noisy input | 8.61 | 9.34 |
| Gaussian blur, tuned on validation (spread 0.75 cells in space, 1 step in time) | 5.00 | 8.19 |
| ASM, the Treiber&ndash;Helbing adaptive smoothing method, tuned on validation | 5.18 | 8.47 |
| Over-complete autoencoder trained on clean inputs (the copier above) | 3.49 | 5.50 |
| Denoising autoencoder, same shape | **2.50** | **4.79** |

The denoiser beat the tuned blur on all 400 test heatmaps. The ASM is a widely used traffic method for smoothing
detector data. It averages along the directions in which traffic waves travel: downstream at free-flow speed,
upstream at the congested wave speed. It did no better than a plain blur here, probably because every cell is
observed; it is built for filling between sparse detectors, which is the masking problem below.

Three honest caveats. First, fronts stay the hardest cells for every method. Second, the denoiser always smooths a
little: given a clean heatmap, it returns one 2.08 mph away (the copier: 1.49). Third, it generalises to a noise
level it never saw, but only so far: at 20 mph of noise it gives 4.15 mph, against 8.40 for the blur.

:::{admonition} Going deeper &mdash; the arrows are a score
:class: dropdown
For small noise, the best possible denoiser moves a point by about $\sigma^2 \nabla \log p(\tilde{\mathbf{x}})$:
the noise variance times the direction in which traffic states become more likely. That direction is called the
*score*. So training a denoiser is a way to learn the score of the data without ever writing $p(\mathbf{x})$ down
(Vincent, 2011). Diffusion models build on exactly this: they start from pure noise and apply many small denoising
steps, each following the learned arrows a little, until a new realistic heatmap appears. Sources: Vincent (2011),
*A connection between score matching and denoising autoencoders*; Bishop and Bishop (2024), sections 19.1.4 and 20.3.
:::

## Masked autoencoders: BERT's idea for heatmaps and detector data

Hide most of the input and train the network to fill in what is missing. This is BERT's self-supervision, moved
from words to image patches (He et al., 2022). For traffic it has an immediate use: detectors fail, and an agency
needs the missing speeds anyway.

```{figure} ../_static/figures/AEB_MAE_Pipeline.png
:alt: Six numbered steps on one 20 by 20 heatmap. 1 and 2, cut it into 25 patches of 4 by 4 cells and hide 19 at random. 3, an encoder sees only the 6 visible patches plus where each sits. 4, the decoder gets 25 slots, the 6 encoded patches in green and 19 copies of one learned mask token in gold. 5, it predicts all 25 patches. 6, the loss scores only the 19 hidden patches against the truth.
:width: 100%

A masked autoencoder on one test heatmap, after He et al. (2022) and Bishop and Bishop (2024), Figure 19.5.
```

**The bridge from BERT.** In {doc}`Module 2 <../module2/notes5-bert>`, BERT learned language by hiding words and
predicting them. A masked autoencoder does the same with patches, with three changes.

| | BERT (Module 2) | Masked autoencoder |
| --- | --- | --- |
| Unit | a word token | an image patch; here 4 &times; 4 cells, 0.8 mi &times; about 2 min |
| Share hidden | 15% | 75%; here 76% (19 of 25) |
| What the encoder sees | every token, hidden ones mostly replaced by `[MASK]` | only the visible patches; hidden ones are left out |
| Where mask tokens enter | the encoder's input | the decoder's input only |
| Training target | the hidden words | the hidden patches, by squared error |
| What you keep | the encoder, for fine-tuning | the encoder for fine-tuning, or the whole model as a gap filler |

**Why hide so much?** He et al. (2022) argue that images are redundant: neighbouring pixels nearly agree, and so do
neighbouring cells in a heatmap. Hide 15% and most gaps can be filled by averaging nearby cells, which teaches
little. Hide 75% and the network has to learn larger patterns, such as how queues form and travel. Leaving the
hidden patches out of the encoder also makes training cheap: here the encoder handles 6 tokens instead of 25.

$$
E(\mathbf{w}) = \sum_{n=1}^{N} \frac{1}{|H_n|}\sum_{i \in H_n} \big( y_i(\mathbf{x}_n^{\text{vis}},\mathbf{w}) - x_{n,i} \big)^2
$$

| Symbol | Meaning |
| --- | --- |
| $\mathbf{x}_n^{\text{vis}}$ | the visible patches of heatmap $n$ (6 of 25), with their positions |
| $H_n$ | the hidden cells of heatmap $n$; a new random set each time it is used |
| $\lvert H_n \rvert$ | how many cells are hidden (19 patches &times; 16 = 304 cells) |
| $y_i$ | the network's speed for hidden cell $i$ |
| $x_{n,i}$ | the true speed in that cell |

*In words:* show the network a few patches, ask for the rest, and score it only on what it could not see. The
visible cells are given, so scoring them would reward copying.

Our model is a small version of He et al. (2022): an encoder of 4 transformer layers (width 96) and a decoder of 2
(width 64), 560,592 weights in all. It trained for 400 passes over the 3,200 training heatmaps, with a new random
mask every time, in about 12 minutes on two CPU cores.

```{figure} ../_static/figures/AEB_Masked.png
:alt: Two rows of four heatmaps; the fills keep the visible cells as given. Top row, random patches hidden as in training, what the model sees, the ASM fill 11.7 mph off on the hidden cells with a wide fuzzy queue band, the masked autoencoder fill 6.2 mph off with a sharper band, and the truth. Bottom row, three of five road segments dark, never seen in training, ASM 10.2 and masked autoencoder 7.2 mph off.
:width: 100%

Two test heatmaps. Grey cells with a cross are hidden; "mph off" is the RMS error on the hidden cells.
```

In the top row the classical fill blurs the queue into a wide, fuzzy band. In the bottom row it nearly loses the
queue at the downstream end. The masked autoencoder places both queues about right. Only its hidden cells count: as
He et al. (2022) do, the figure shows the visible cells as given, because the loss never trains the model to rebuild
them.

**Results on the 400 test heatmaps**, RMS over hidden cells only. The baselines use only the visible cells. The
ASM's smoothing widths were tuned on the validation heatmaps.

| Method | Random 76% hidden: all (mph) | Random: queue fronts (mph) | Outage, 3 of 5 segments dark: all (mph) | Outage: queue fronts (mph) |
| --- | --- | --- | --- | --- |
| Mean of the visible cells | 16.03 | &mdash; | 16.39 | &mdash; |
| ASM (Treiber&ndash;Helbing), tuned | 12.39 | 22.82 | 13.03 | 24.06 |
| Masked autoencoder | **6.01** | **11.51** | **8.59** | **16.75** |

On random masks, like those it trained on, the masked autoencoder halves the ASM's error and beats it on 89% of
test heatmaps. The outage test hides less, 60% of cells, and its encoder sees 10 patches instead of 6. Yet it is
harder: whole road segments stay dark for the whole window, a pattern the model never saw in training. Its error
rises from 6.0 to 8.6 mph, and the ASM wins on 26% of heatmaps. The comparison also favours the ASM a little,
because the ASM's settings were re-tuned on outage-shaped validation masks while the autoencoder was not retrained.
We did not train an outage version here, but the standard advice applies: **train on the gaps you expect to
face**, for example with outage-shaped masks.

Two more cautions. A fill-in is a plausible guess, not a measurement: mark imputed values in any dataset an agency
publishes. And these heatmaps come from one simulator on one uniform road. A real corridor has ramps, uneven
detector spacing and incidents, so the model must be retrained, and re-tested, on that corridor's own data.

## Where autoencoders break

Autoencoders pay off where traffic data have far less freedom than their raw numbers suggest. They fail in five
recognisable ways, each seen on this page or the one before.

1. **A small average error can hide the cases you care about.** PCA's 4.29 mph on I-405 hid the queue-edge moments:
   3.8% of readings missed by more than 10 mph. Every cleaning and filling method on this page was worst at queue
   fronts. Score the cells that matter, not only the average.
2. **A latent is not a physical variable.** The fundamental-diagram latent above kept density's order on the
   congested branch only. A latent is a coordinate the network chose, not a measurement or a cause.
3. **Different runs give different answers.** Five random starts on the same data gave 47 to 87 veh/h. Report the
   spread, not the best run.
4. **New conditions break it quietly.** An outage pattern it never trained on raised the masked autoencoder's error
   from 6.0 to 8.6 mph. A model trained on simulated or one-corridor data must be re-tested on the corridor where it
   will run.
5. **It cannot generate.** A plain autoencoder's latents leave gaps, so randomly drawn latents may decode to
   something no road produces. The companion earlier on this page measures this: only 12% of a plain autoencoder's
   training latents fall inside the circle of radius 2 where 86% of draws from a standard bell curve land, against
   95% for a VAE. That is the problem the VAE of {doc}`4.6 <notes3b-vae-basics>` solves.

:::{admonition} Before you trust these results
:class: warning
**What is the baseline?** For cleaning, a Gaussian blur and the Treiber&ndash;Helbing ASM, both tuned on validation
data, and the noisy input itself (8.61 mph). For filling, the mean of the visible cells and the tuned ASM.

**How was the data split, and why is that honest?** The heatmaps were split by whole heatmap into 3,200 training,
400 validation and 400 test heatmaps (seed 7, as in the VAE lab). Every model saw only the training heatmaps, every
tuned setting was chosen on validation, and every score is on test. Test noise and test masks were drawn once, with
fixed seeds.

**What does it do on the ugly cases?** The heatmaps are synthetic: one simulator, one uniform 4-mile road. Queue
fronts are the worst cells for every method. The outage test is a pattern none of the models trained on. And
results move between random starts.
:::

:::{admonition} Fit card &mdash; Autoencoders: bottleneck, sparse, denoising, masked
:class: tip
**Idea in one sentence.** Rebuild traffic data through a narrow, penalised or corrupted path, so the network must
learn the data's structure instead of copying it.

**Why it works.** Traffic data have few real degrees of freedom: speeds move together and queues travel at steady
wave speeds. A constrained network can rebuild only what is shared across many examples, so it fills noise and gaps
with typical structure.

**Fits these tasks.** Compressing traffic states; cleaning noisy speeds; filling detector gaps; flagging states it
cannot rebuild (broken sensors, incidents); pretraining an encoder when labels are scarce (*extraction*,
*prediction* for filling gaps, *classification* for flags).

**Needs this data.** Thousands of unlabelled examples of one kind (detector heatmaps, trajectories, dashcam frames);
clean, complete examples to corrupt or mask; a test set from the place it will run.

**Breaks when.** Test data differ from training (a new corridor, sensor, noise level or outage pattern); the score
averages away the cells that matter; a latent is read as a physical quantity; you need new samples (use a VAE).

**Keep the classical method when.** A linear summary is enough (PCA is exact, repeatable and ranked); regression from
neighbouring detectors or the ASM fills gaps well enough and is easier to audit; the result must obey conservation
or other physics; you have only a few hundred examples.
:::

## Autoencoders in transportation practice

| Domain | Task | Autoencoder idea | Data | Classical baseline |
| --- | --- | --- | --- | --- |
| Traffic flow; agency practice | Fill missing loop-detector data | Masked or denoising autoencoder over space &times; time, e.g. [Asadi and Regan (2019)](https://arxiv.org/abs/1904.12413) on PeMS Bay Area loops | 5-minute speed or flow from neighbouring detectors | Regression from neighbouring loops, as in PeMS ([Chen et al., 2003](https://trid.trb.org/view/683990)); the ASM |
| Traffic flow | Short-term flow prediction | A stacked autoencoder learns features, then a predictor uses them (Lv et al., 2015) | PeMS flow series | Time-series models such as ARIMA |
| Agency practice | Detector health checks | Flag readings the autoencoder cannot rebuild | Volume, occupancy and speed per detector | Rule-based checks on volume and occupancy series ([Chen et al., 2003](https://trid.trb.org/view/683990)) |
| ADAS and driving automation | Pretrain a camera encoder without labels | Masked autoencoder on unlabelled dashcam frames, then fine-tune for detection | Fleet dashcam video | A backbone pretrained on ImageNet (Module 1, transfer learning) |
| Road safety | Flag unusual driving and near-misses | Rebuild error on vehicle time series (speed, acceleration, steering) | CAN bus or naturalistic driving data | Fixed thresholds, such as hard-braking rules |
| Air mobility | Group flight paths into typical flows; spot outliers | Cluster the autoencoder latents of resampled ADS-B tracks, e.g. Olive et al. (2020) | ADS-B trajectories around an airport | Distance-based clustering of tracks |

## Autoencoders in seven lines

1. An autoencoder rebuilds its input through a few latents. The loss is the rebuild error, so the data are their
   own labels.
2. PCA is the linear autoencoder: encode z = u&#8321;&#7488;(x &minus; m), decode m + u&#8321;z. Its average squared error is the sum
   of the dropped eigenvalues.
3. A two-layer network trained on the same loss finds PCA's answer, even with tanh, because its linear decoder can
   only draw a flat sheet.
4. Training is a loop: forward pass, loss, chain rule back to every weight, a small step downhill, averaged over
   many examples.
5. Nonlinear layers inside the decoder bend the sheet: a nonlinear PCA. On the fundamental diagram the flow error
   fell from 315 to 47&ndash;87 veh/h; on heatmaps, from 9.85 to 7.29 mph with 2 latents. The latents are the
   network's own coordinates, not traffic variables, and they help another task only when its label follows the
   largest variations.
6. With as many latents as inputs, it can copy. Use fewer latents, penalise them (sparse), corrupt the input
   (denoising) or hide most of it (masking).
7. A denoiser learns arrows that point back to real traffic, the seed of diffusion models. Masking is BERT's
   self-supervision for heatmaps, and it fills detector gaps.

## Label the picture

```{figure} ../_static/figures/AEB_Label_Step.png
:alt: One denoising training step drawn with six numbered blank labels, a clean heatmap, an arrow marked plus noise to a noisy heatmap, an encoder shape, a gold box, a decoder shape, an output heatmap, and a bracket marking the loss as a squared error between blank 6 and blank 1. A word bank lists latents z, corrupted input x tilde, decoder, encoder, output y, and clean heatmap x, the target.
:width: 100%

Fill in blanks 1 to 6 from the word bank.
```

Then answer: what would you change to turn this into a masked autoencoder?

:::{admonition} Answers
:class: dropdown
1, clean heatmap x (the target); 2, corrupted input x&#771;; 3, encoder; 4, latents z; 5, decoder; 6, output y. To make it a
masked autoencoder, replace "+ noise" with "hide most of the patches": the encoder sees only the visible patches,
the decoder fills in mask tokens for the hidden ones, and the loss compares 6 with 1 on the hidden cells only.
:::

## Check yourself

1. A district wants to store 5-minute speeds from 300 detectors more cheaply, and to rebuild them later. Would you
   start with PCA or a deep autoencoder? Which number would you compute first to decide?
2. You have three years of unlabelled corridor heatmaps and only 120 heatmaps labelled "incident" or "no incident".
   Would you fit the classifier on autoencoder latents or train it from scratch? What would you check about the
   latents first?
3. A colleague trains an autoencoder with 512 latents on 400-cell heatmaps and presents its 1.5 mph rebuild error
   as proof that it "understands traffic". Which test would you run before believing it?
4. You have a year of complete speeds from 50 detectors, and your detectors fail in long blocks: a whole station for
   hours. How would you train a masked autoencoder for this, and which baseline must it beat?
5. A denoising autoencoder trained on freeway probe speeds is moved to a signalised arterial. What could go wrong,
   and how would you find out before it matters?
6. When would you choose the ASM over a masked autoencoder to fill gaps in a dataset your agency publishes?

## References for 4.4&ndash;4.5

- Bishop, C. M. and Bishop, H. (2024). *Deep Learning: Foundations and Concepts*. Springer. Sections 16.1 and 19.1;
  sections 19.1.1 to 19.1.5 cover the ideas of 4.4 and this page in about five pages.
- Bourlard, H. and Kamp, Y. (1988). Auto-association by multilayer perceptrons and singular value decomposition.
  *Biological Cybernetics*, 59, 291&ndash;294.
- Baldi, P. and Hornik, K. (1989). Neural networks and principal component analysis: learning from examples without
  local minima. *Neural Networks*, 2(1), 53&ndash;58.
- Vincent, P., Larochelle, H., Bengio, Y. and Manzagol, P.-A. (2008). Extracting and composing robust features with
  denoising autoencoders. *ICML*.
- Vincent, P. (2011). A connection between score matching and denoising autoencoders. *Neural Computation*, 23(7),
  1661&ndash;1674.
- He, K., Chen, X., Xie, S., Li, Y., Doll&aacute;r, P. and Girshick, R. (2022). Masked autoencoders are scalable
  vision learners. *CVPR*.
- Devlin, J., Chang, M.-W., Lee, K. and Toutanova, K. (2019). BERT: pre-training of deep bidirectional transformers
  for language understanding. *NAACL*.
- Treiber, M. and Helbing, D. (2002). Reconstructing the spatio-temporal traffic dynamics from stationary detector
  data. *Cooper@tive Tr@nsport@tion Dyn@mics*, 1, 3.1&ndash;3.24.
- Chen, C., Kwon, J., Rice, J., Skabardonis, A. and Varaiya, P. (2003).
  [Detecting errors and imputing missing data for single-loop surveillance systems](https://trid.trb.org/view/683990).
  *Transportation Research Record*, 1855, 160&ndash;167.
- Lv, Y., Duan, Y., Kang, W., Li, Z. and Wang, F.-Y. (2015). Traffic flow prediction with big data: a deep learning
  approach. *IEEE Transactions on Intelligent Transportation Systems*, 16(2), 865&ndash;873.
- Asadi, R. and Regan, A. (2019). [A convolution recurrent autoencoder for spatio-temporal missing data
  imputation](https://arxiv.org/abs/1904.12413). arXiv:1904.12413.
- Olive, X. et al. (2020). [Deep trajectory clustering with autoencoders](https://hal-enac.archives-ouvertes.fr/hal-02916241v1).
  *ICRAT 2020*.
- Data: PeMSD7(M) 5-minute speeds, as packaged by Yu, B., Yin, H. and Zhu, Z. (2018), Spatio-temporal graph
  convolutional networks, *IJCAI* ([repository](https://github.com/VeritasYin/STGCN_IJCAI-18)).

---

Next: {doc}`4.6 Variational autoencoders (VAE) <notes3b-vae-basics>` &mdash; give the latents a distribution, and the decoder becomes a generator.
