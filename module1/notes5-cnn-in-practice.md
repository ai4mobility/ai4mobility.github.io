# 1.2 (continued) &mdash; Choosing a network, and interrogating it

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 1 &middot; Section 1.2 &mdash; part 4 of 4</span>
    <span class="notes-card-session">Sessions: Sept 3 &amp; Sept 10</span>
  </div>
  <p class="notes-card-lede">The engineering half of convolution. Which architecture fits which mobility task and what each one costs in parameters, latency and roadside power; then saliency maps &mdash; what the network is actually looking at, and the honest limits of that answer. The saliency material is Sept 10 content, kept here so the CNN thread stays in one place.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Interactive companions on this page</h4>
      <ul>
      <li><a href="../_static/companions/CNN_Architectures_Companion.html" target="_blank" rel="noopener">CNN architectures and what they cost &#8599;</a></li>
      <li><a href="../_static/companions/Saliency_Maps_Companion.html" target="_blank" rel="noopener">Saliency maps &#8599;</a></li>
      </ul>
    </div>
    <div>
      <h4>Notebooks that go with it</h4>
      <ul>
      <li><a href="lab3_image_embeddings.html">Lab 3 &mdash; Image embeddings with a deep CNN</a></li>
      </ul>
    </div>
  </div>
</div>

(cnn-architectures)=
## Which network, and what it costs

You have now set the nine numbers of a kernel by hand, stacked kernels into a
layer, and watched a whole detector run over real footage. One question is left,
and it is the one you will actually be asked in a project meeting: *which*
network. A vendor's proposal says "a ResNet-50 backbone." A Jetson spec sheet
says "MobileNet at 30 fps." The eighteen years between LeNet-5 and ResNet are
worth an hour of your time not as history but because each architecture is a
*priced* answer to a specific problem, and those prices have not changed.

**The arc, in four steps.** LeNet-5 (1998) read handwritten digits on bank
cheques with **61,706** parameters, and the template it established — convolve,
subsample, convolve, subsample, classify — is the template every network below
still follows. AlexNet (2012) added no new operation: it made the same idea
**990 times** larger, replaced tanh with ReLU, added dropout, and trained on two
GPUs. The winning top-5 error on the ImageNet challenge fell from 28.2% in 2010
to 16.4%. Then 2014 produced two opposite answers in the same competition: VGG
fixed every kernel at 3 × 3 and made depth the only knob, arriving at **138.4
million** parameters; GoogLeNet went the other way, using 1 × 1 bottlenecks and
deleting the large dense head, and beat VGG's error with **21 times** fewer
parameters. ResNet (2015) reached 3.57% with the skip connection, and that one
idea is in essentially every vision model you will download.

**Parameters and compute are not the same resource.** This is the first thing to
internalise, because it decides which architecture your constraint rules out. In
AlexNet, **96.0%** of the parameters sit in the three dense layers at the end and
they perform **8.2%** of the arithmetic. VGG-16 is more extreme: **89.4%** of
parameters, **0.8%** of the compute. GoogLeNet and ResNet delete that head
entirely and replace it with a global average pool — ResNet-50 is down to 8.0%
and 0.05% — which is why ResNet-152 has *fewer* parameters than VGG-16 while
being nine times deeper. The working rule: **if your constraint is memory, look
at the head; if it is latency, look at the early convolutions**, where the
feature maps are still large and every filter is applied tens of thousands of
times.

**Two pieces of arithmetic explain most of the rest.** First, stacking. Two
3 × 3 convolutions in a row see the same 5 × 5 window as one 5 × 5 convolution,
and three see the same 7 × 7 window — but at 256 channels in and out, the
5 × 5 layer costs 1,638,400 weights against the pair's 1,179,648 (**28% fewer**),
and the 7 × 7 costs 3,211,264 against 1,769,472 (**45% fewer**). You also gain a
non-linearity between them. Fewer weights *and* more expressive power for the
same field of view is why every architecture after 2014 is built from 3 × 3
convolutions. Second, the bottleneck. A 1 × 1 convolution has no spatial extent
at all — it looks at one position across all channels and mixes them, a learned
change of basis on the channel axis. Wrap the expensive 3 × 3 in a 1 × 1 that
narrows the channels and a 1 × 1 that widens them back, and for one block at
ResNet's stage-1 width the cost drops from 1,179,648 weights to **69,632** —
**16.9 times cheaper**, in parameters and in arithmetic alike.

**The skip connection, and what it actually fixes.** The usual explanation is
"it stops gradients vanishing," and that is half true in a way worth measuring.
Push a 128 × 128 patch of the stop-bar frame through stacks of plain 3 × 3 blocks
with normalisation switched off, and the gradient arriving at layer 1 falls from
2.95 at 8 convolution layers to **0.092** at 56 — a **32-fold** collapse. Add
skip connections and it goes the other way and *explodes*, to roughly
$2 \times 10^{5}$, because each skip adds its input straight back and nothing
rescales the sum. Neither stack is usable, which is exactly why real ResNets put
batch normalisation in every block. Keep both halves of that result: the skip
fixes the vanishing direction and creates the exploding one.

The deeper problem is the one normalisation does not fix. Suppose the best thing
an extra block could do is *nothing* — pass its input through unchanged. Write
the mapping the block should compute as $H(x)$:

$$
\text{plain: } y = H(x)
\qquad\qquad
\text{residual: } y = x + F(x), \text{ so } F(x) = H(x) - x
$$

where $x$ is the block's input feature map, $y$ its output, $H$ the function you
wish it would learn, and $F$ the *correction* the residual block learns instead.
Both forms can represent the same functions; this is not about capacity. But if
the useful $H$ is near the identity, then $F$ is near zero, and driving a stack
of weights toward zero is something gradient descent does easily. With batch
normalisation on in both arms and the residual branch initialised at zero, the
residual stack starts the pass-through task at an error of **exactly 0.000000**
at every depth, while a plain stack starts near 0.7 — and after 400 training
steps the plain stack has still not reached where the residual one *began*.
Worse, the plain stack gets **worse with depth**: 0.0097 at 8 convolution layers,
**0.0787** at 56, an eight-fold degradation for seven times the depth. Overfitting
cannot explain that, because overfitting *lowers* training error. The skip
connection does not make a network more expressive. It makes "do nothing" free,
so that adding depth can no longer hurt.

**What the whole family costs, measured.** Single-thread CPU, batch of one,
224 × 224 input; multiply-adds counted over convolution and dense layers;
accuracies are the published ImageNet validation figures for these exact
checkpoints.

| | parameters | G mult-adds | CPU ms | checkpoint | ImageNet top-1 |
|---|---:|---:|---:|---:|---:|
| LeNet-5 (1998) | 61.7 k | 0.0004 | 0.6 | — | — |
| AlexNet (2012) | 61.1 M | 0.71 | 38.0 | 244 MB | 56.5% |
| VGG-16 (2014) | 138.4 M | 15.47 | 404.1 | 553 MB | 71.6% |
| GoogLeNet (2014) | 6.6 M | 1.50 | 78.1 | 52 MB | 69.8% |
| ResNet-18 (2015) | 11.7 M | 1.81 | 56.3 | 47 MB | 69.8% |
| ResNet-50 (2015) | 25.6 M | 4.09 | 120.7 | 103 MB | 76.1% |
| ResNet-152 (2015) | 60.2 M | 11.51 | 312.1 | 242 MB | 78.3% |
| MobileNetV3-L (2019) | 5.5 M | 0.22 | 26.1 | 22 MB | 74.0% |

Read the last row against the third. MobileNetV3-Large is **more accurate** than
VGG-16 for **one seventy-first** of the compute, 25 times fewer parameters and a
checkpoint 25 times smaller. That single comparison is the entire argument for
the 2014–2019 architecture work, and the reason nobody deploys VGG.

Two cautions about that table, both worth carrying into a procurement
conversation. **"FLOPs" is not a defined unit**: the ResNet paper quotes
ResNet-50 at $3.8 \times 10^{9}$, this measurement gives $4.09 \times 10^{9}$
multiply-adds, and counting a multiply and an add separately gives
$8.2 \times 10^{9}$. Three numbers, one network. **"Depth" is not defined
either**: ResNet-50 is named for 50 layers and traces 54 convolution and dense
layers; GoogLeNet is described as "22 layers deep" and contains 58.

**And now the part that matters more than any of it.** Run all seven pretrained
networks on the frames from your convolution lab and read the *labels*, not the
ranking. Searching all **1,000** ImageNet class names for `person`, `pedestrian`,
`human`, `child` and `cyclist` returns nothing — there is no pedestrian class.
On the night-crossing frame, whose entire subject is a person standing in the
road, VGG-16 answers `traffic light` with probability **0.93** and ResNet-152
answers `spotlight`. Nor does the benchmark ranking survive the trip: on the
Florida stop-bar frame, ResNet-18 (69.8% top-1) answers `sports car` while
ResNet-152 (78.3%) answers `amphibian`, and AlexNet answers `warplane`. One
frame is not an evaluation, but it is a warning that a two-point gap on a
photo-tagging benchmark tells you very little about your corridor.

So these models are not classifiers *for you*. They are **backbones**: you
discard the 1,000-class head, keep the convolution stack that learned edges,
textures and object parts from 1.2 million photographs, and train a small new
head on your own label space with your own few hundred labelled frames. That is
transfer learning, it is the subject of the next section, and it is why the
architecture question is worth caring about at all — the backbone you choose sets
the cost floor for everything you build on top of it. You are buying the stack,
not the answers.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion — CNN architectures: LeNet to ResNet, and how to choose</span>
    <a href="../_static/companions/CNN_Architectures_Companion.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/CNN_Architectures_Companion.html"
          title="CNN architectures: LeNet to ResNet, and how to choose" loading="lazy"></iframe>
</div>

The second tab is where to spend your time: pick any of the eight networks and
every real layer is drawn to scale, with height the size of its feature map and
width its channel count, so the funnel from 224 × 224 × 3 down to 7 × 7 × 2048 is
visible at a glance. Click a block for its parameters, arithmetic and receptive
field, then recolour the whole stack by *where the parameters are* and by *where
the compute is* and watch AlexNet's dense head light up under one and vanish
under the other. The fifth tab runs the predictions above on all five frames, and
the sixth asks you four questions about a deployment and assembles a
recommendation out of these measurements — argue with it.

:::{admonition} Before you trust this result
:class: important
**What is the baseline?** For an accuracy claim about a new architecture, the
honest baseline is the previous generation *at the same cost*, not the previous
generation at any cost. ResNet-152 buys 2.2 points of ImageNet top-1 over
ResNet-50 for 2.8 times the compute; whether that is a good trade is a question
about your deployment, not about the models. And the baseline for the task as a
whole may not be a network at all — a fixed camera and a vehicle count still
belong to frame differencing.

**How was the data split, and why is that honest?** Every accuracy in the table
is on the ImageNet-1k validation set, held out from training. That is honest for
photographs of objects and says nothing about your corridor: the frames those
models were trained on are web photographs, and a benchmark split cannot tell you
about a distribution shift it never contained. Two of the five frames used here
are not US roads, and the page says so rather than letting them stand as
evidence.

**What does it do on the ugly cases?** The night frame is the test that matters,
and every model on this page fails it in the same way — not by scoring low, but by
returning a confident label for the wrong object, because the right word does not
exist in its vocabulary. Before you evaluate a backbone, check that its label
space can express the thing you need to detect. A model cannot be wrong about a
class it does not have.
:::

(saliency-maps)=
## What the network is actually looking at

One question survives everything above, and it does not go away when the
detector works. A network hands you a number — a class score, a lane offset, a
predicted queue — and no reasons. This belongs with the detection block on
**Sept 10**, but it sits here because it uses the same frame and the same
backbone you have spent this section taking apart.

Start from what you would normally do. When you fit a crash frequency model you
read the coefficients: AADT positive, shoulder width negative, lighting not
significant. That table is most of what makes the model defensible in a report —
it is how you argue the model learned the road and not the sample. A ResNet-50
has 25.6 million weights and not one of them is "the lane line." There is no
coefficient table. What there *is* is a derivative: the score the network
produced is a differentiable function of every pixel and of every intermediate
feature, so you can ask **which parts of this frame, if they changed, would
change the answer.** Drawn as a heat map over the frame, that derivative is a
**saliency map**.

**The mechanism, in one pass each way.** Run the frame forward and stop at the
last convolutional layer, which still knows *where* things are — for a 672 × 416
input, ResNet-50 leaves you 2048 feature maps of **13 × 21** cells each. Finish
the forward pass and pick out one number: the score for one class. Differentiate
*that number and nothing else* backward to those feature maps, average each map's
gradient over the 273 cells to get one weight per map, then add the maps up with
those weights and keep the positive part. The result is a 13 × 21 grid of heat,
stretched over the frame for display. That is Grad-CAM (Selvaraju et al., ICCV
2017); Bishop's Figure 10.15 is from that paper.

**One frame, two questions.** Run it on the stop-bar frame from the convolution
section — the black coupé at the bar, the mast arm above it — with a stock
ImageNet ResNet-50, unmodified. Differentiate the score for `traffic light` and
the signal heads carry **4.66 times** the heat their pixel area would earn them by
chance, while the lead car sits at 0.92, meaning no enrichment at all.
Differentiate `sports car` on the same pixels with the same weights and those
numbers swap: **0.03** on the signal heads, **2.59** on the lead car. Nothing
changed but the number we differentiated. Both class probabilities are tiny —
1.8% and 0.9% — because a cluttered arterial is not an ImageNet photograph with
one object in the middle. Saliency does not need a confident prediction, only a
score to differentiate, and heat is not confidence.

**The resolution is the result.** Those 273 cells are all the spatial
information there is. One cell covers 32 × 32 input pixels, about 25 pixels of
the raw frame — using the detector's own boxes and two known widths, roughly
**0.21 m** on the road at the lead car's bumper and about **1.4 m** up at the mast
arm. A twelve-inch signal head is therefore **a fifth of one cell**, and two
adjacent heads are 1.8 cells apart. A deep-layer saliency map cannot point at a
signal head, a small sign, or a lane line; anything smoother than the cell grid
was drawn by an interpolation filter. Keep this the next time a vendor shows you
a heat map centred on a pedestrian.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion — Saliency maps: what is the network actually looking at?</span>
    <a href="../_static/companions/Saliency_Maps_Companion.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/Saliency_Maps_Companion.html"
          title="Saliency maps: what is the network actually looking at?" loading="lazy"></iframe>
</div>

Switch the class on the second tab and watch both numbers move; then switch the
rendering to *true cell size* and watch the blob become 273 squares. The fourth
tab is where the argument is.

**Lane lines, and a model that was right for the wrong reason.** No stock network
has a lane-line class, so the companion trains one: a small CNN that reads one
forward-facing frame and predicts the car's lateral offset from the lane centre,
the quantity inside every lane-keeping controller. The frames are **synthetic** —
drawn from a pinhole camera model, and labelled as such throughout — because that
buys two things no real corpus does. We know the exact pixels of every painted
marking, so "how much of the heat is on the paint" becomes a number; and we can
build one specific trap on purpose. The trap is a continuous sound wall whose
shadow edge sits at a fixed distance from the lane, which makes it a *perfect*
proxy for the lane — bigger and higher-contrast than the paint, and exactly as
informative. NVIDIA's PilotNet paper (Bojarski et al., 2017) reported the
opposite outcome, a steering network attending to lane markings and road edges
without being told they exist; both outcomes come from the same corpus-shaped
pressure.

Two networks, identical architecture, identical initial weights,
**208,129** parameters each, 6,000 training frames each. The only difference is
which corridor supplied the frames. Both are then validated the way most people
validate: a random held-out split of their own data. Model A, trained where the
shadow wanders, lands at **0.023 m** RMSE. Model B, trained where the wall is,
lands at **0.037 m**. Both crush the predict-the-mean baseline of 0.70 m and both
beat a non-learned fit to the two painted lines at 0.22 m. Nothing here looks
wrong. Now move to a corridor where the shadow is decorrelated from the lane:
Model A is unchanged at 0.023 m and Model B collapses to **0.486 m** — a factor
of thirteen, and worse than the fifteen-line least-squares fit it had beaten by
an order of magnitude. Its error tracks how far the shadow moved, at 0.167 m of
error per metre of shadow displacement, R² = 0.52 over 1,597 frames.

Here is why this section exists. On a frame where the two models agree with the
truth and with each other to within a centimetre, the saliency maps already
separate them: Model A puts **3.24 times** its share of the heat on the painted
markings and only 0.35 on the shadow edge — it has actively learned to ignore a
large, high-contrast feature — while Model B puts 1.57 on the paint and **2.34**
on the shadow. Every scalar you would normally look at says they are the same
model. The map says they are not, from one frame, before any of the evidence
above was measured.

**The check that comes first.** None of this means anything until you know the
picture depends on the trained model at all. Take Model A, throw away the learned
weights in its head and last convolutional block, replace them with random ones,
and recompute the map: mean correlation with the trained map is **−0.06** across
200 frames, so it does depend on the model. That test is from Adebayo et al.
(NeurIPS 2018), who found that several widely used and visually convincing
saliency methods are independent of both the model and the data — they behave
like edge detectors, which need neither training data nor a model. A pass
licenses the page above and nothing wider: run the randomisation test on your own
setup before you put a heat map in a report.

:::{admonition} Before you trust this result
:class: important
**What is the baseline?** Predicting the training mean gives 0.70 m of lane-offset
error; a non-learned least-squares fit to the two painted lines gives 0.22 m and
is immune to the trap, because a person told it what a lane line is. Both networks
beat both baselines on their own data, which is exactly why neither looked
suspicious. For the saliency map itself the baseline is an edge detector — that is
what the randomisation check is testing against.

**How was the data split, and why is that honest?** It was not honest, and that is
the finding. A random held-out split only tests generalisation to *the same
corridor*. The shortcut is a property of the whole dataset, so every split of it
inherits the shortcut. The split with any power here is by corridor: train where
the wall is, test where it is not. The same applies to your own data — splitting a
year of one district's dashcam video at random tells you almost nothing about the
next district.

**What does it do on the ugly cases?** Model B returns 0.486 m of error in a 3.6 m
lane, and the errors are correlated with the scene rather than random, which is the
failure mode a controller can least tolerate. Note also what saliency did and did
not do: it raised the alarm from a single frame, cheaply, and it proved nothing.
The shifted-corridor experiment proved it, expensively. Use the first to decide
where to spend the second, and never present a heat map as evidence that a
perception system is safe.
:::

---

Next: {doc}`notes6-embeddings` asks what the numbers going *into* any of these models should be.
