# 2.8 Locality returns: Swin, MobileViT and ConvNeXt

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 2 &middot; Section 2.8</span>
    <span class="notes-card-session">Sessions: Oct 8 &amp; 15</span>
  </div>
  <p class="notes-card-lede">The Vision Transformer of 2.7 reads a 224-pixel square with global attention and no built-in sense of what is near what. Three designs put locality back: Swin attends inside small shifting windows, MobileViT tucks a little attention inside a phone-sized CNN, and ConvNeXt rebuilds a 2015 ResNet with transformer-era choices and no attention at all. The section closes on a camera-to-alert pipeline where convolution, attention and classical code each do what suits the signal.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Interactive companions on this page</h4>
      <ul>
      <li><a href="../_static/companions/ViT_To_Swin_Companion.html" target="_blank" rel="noopener">From ViT to Swin: what a 224-pixel square cannot see &#8599;</a></li>
      <li><a href="../_static/companions/MobileViT_Receptive_Field_Companion.html" target="_blank" rel="noopener">How far can one pixel see? MobileViT &#8599;</a></li>
      </ul>
    </div>
    <div>
      <h4>Notebooks that go with it</h4>
      <ul>
      <li><a href="../module4/lab6_vit_finetune.html">Lab 6 &mdash; Fine-tuning a Vision Transformer</a></li>
      </ul>
    </div>
  </div>
</div>

## What this section covers

- Where plain ViT breaks on a full-resolution camera frame: resolution, cost and scale
- Swin: windows, shifted windows, patch merging, and the one cost equation
- MobileViT: convolution, then attention over unfolded patches &mdash; two hops to every pixel, measured on Florida road frames
- Why fewer attention pairs is not faster on a phone; the licence check before shipping
- ConvNeXt: the control experiment that rebuilds a ResNet with Swin's choices and matches or passes it
- A camera-to-alert pipeline that uses convolution, attention and classical code, each where it fits

## Three ways to put locality back

Before coordinating a corridor, a signal engineer asks how far each controller needs to see and
what it costs to let it see further. A CNN answers *not far, and cheaply*: reach grows one ring per
layer. The plain ViT of {doc}`2.7 <notes7-vision>` answers *everywhere, at once*, and must learn
locality from data. Each of the three designs below borrows from both answers.

(vit-to-swin)=
## Where plain ViT breaks on a real camera, and how Swin fixes it

```{figure} ../_static/figures/Swin_Dilemma.jpg
:alt: The same forward-camera frame fed to a ViT three ways. Squashed to 224 by 224 the child is a smudge less than half a patch tall; centre-cropped, the child is outside the image; at full resolution the child is visible but the frame becomes 9,196 tokens.
:width: 100%

Three ways to hand a 1928 &times; 1208 forward-camera frame to a ViT. Shrink it and the child is half a patch; crop it and the child is gone; keep every pixel and each layer compares 84.6 million pairs of tokens per head.
```

The ViT of {doc}`2.7 <notes7-vision>` reads a 224 &times; 224 square. No camera in this course
delivers one. FL511's roadside CCTV is mostly 720 &times; 480, an intersection camera
1920 &times; 1080, the forward camera in the {ref}`scooter case <scooter-kid-case>` 1928 &times; 1208,
and drone video like highD 4096 &times; 2160. Something has to give between the camera and the model, and on the scooter clip
each option fails in a way you can measure. Squash the frame into the square and the child, at
first sight, is 6.7 by 1.6 pixels: less than half of one 16-pixel patch, and shorter than a patch
in 72 of the 111 frames it is tracked. Use the standard classification preprocessing instead
(resize, then keep the central 224 &times; 224) and the child is not in the picture at all in 96 of
those 111 frames, because children enter a forward camera's view from the side of the road. Keep
every pixel and the child survives, 2.3 patches tall, but the frame is now 9,196 tokens and global
attention compares every pair of them: 84.6 million comparisons per head, per layer, against 38,809
for the square.

Those are the first two limits: resolution and cost. The third is scale. A ViT hands a detector one
feature grid, at stride 16, in every layer, while the child grows 7.65&times; taller in 5.55 seconds as
the car closes. A CNN never had these problems, because it reads locally and builds a pyramid of
maps at strides 4, 8, 16 and 32. The ViT paper says plainly what was traded away: transformers "lack
some of the inductive biases inherent to CNNs, such as translation equivariance and locality."

```{figure} ../_static/figures/Swin_Three_Wirings.png
:alt: Three 14 by 14 token grids. A CNN position reads its 9 neighbours, a ViT token reads all 196, a Swin token reads the 49 in its window. Below, the CNN and Swin hand a head four feature maps at strides 4, 8, 16 and 32; the ViT hands it one grid at stride 16.
:width: 100%

Swin keeps attention's content-dependent weights and gives back the CNN's locality and its pyramid of maps.
```

Swin gets both back with three moves. **Windows:** cut the token grid into 7 &times; 7 windows and run
attention inside each one, so every token is compared with 49 others instead of all of them.
**Shifted windows:** in every second block, move the window grid by three tokens, so tokens on
either side of a border land in the same window and information crosses it. **Merging:** between
stages, fuse each 2 &times; 2 block of tokens into one, which builds the same four strides ResNet-50
has. That last move is what makes Swin a drop-in backbone: a detector or segmenter built for
ResNet can take Swin without changing its head. A transportation way to hold the first two is a
county signal system run as coordination zones. Controllers coordinate within their zone, never
with every controller in the county, and redrawing the zone boundaries every other cycle lets a
platoon that crossed a boundary sit inside one zone next time.

```{figure} ../_static/figures/Swin_Arch_Reach.png
:alt: A time-space diagram: a 63-token stretch of one 121-token row of the stage-3 grid against six blocks of alternating regular and shifted windows; the band that can influence one token near the centre widens from 7 to 42 tokens.
:width: 100%

Alternating borders widen a token's reach by one window per block: the cell-transmission model's speed limit, with a window as the cell and a block as the time step.
```

Read it as a time&ndash;space diagram. After the first block a token near the centre draws on its
own window, 7 tokens; after the shifted block, 14; then 21, 28, 35 and 42, which is 672 px of road
from stage 3's six blocks alone. Six 3 &times; 3 convolutions reach 13 tokens; ViT reaches all 121 in
its first block, at the quadratic price.

The one equation is the cost of an attention layer, from the Swin paper:

$$
\Omega(\text{MSA}) = 4hwC^2 + 2(hw)^2C
\qquad\qquad
\Omega(\text{W-MSA}) = 4hwC^2 + 2M^2\,hwC
$$

Here $h \times w$ is the token grid (76 &times; 121 on the forward camera at stride 16), $C$ the
numbers per token, and $M = 7$ the window side. **In words:** the first term projects every token into
a query, key and value, and is the same in both. Only the second term changes: global attention pays
for the square of the token count, windowed attention for the token count times 49. Measured on two
CPU threads, going from 224 &times; 224 to 1080p made ResNet-50 35&times; slower, Swin-T 44&times; and
ViT-S 143&times;, while the pixels grew 41&times;.

Spend your time in three places in the companion below. **Tab 1** feeds the scooter frame to a ViT
three ways; switch to *Resize + centre-crop* and watch the child leave the picture, then scrub the
111-frame chart underneath. **Tab 4** is the mechanism: step Swin-T through its 12 blocks on the
real frame, watch the gold window shift and the dashed region of influence grow, then switch to
ViT-S (the whole frame from block 1) and ResNet-50 (427 px after its last layer) on the same
token. **Tab 6** asks which backbone each of four cameras in this course actually needs, and its
calculator takes your own camera's resolution.

Two results in the companion cut against the headline, and both matter. At FL511's 720 &times; 480,
plain ViT-S ran *faster* than Swin-T on the same CPU (0.68 s against 1.08 s): below about one
megapixel the pair term is not yet the bill, and window bookkeeping has overhead. And on COCO
detection, ConvNeXt-T, a ResNet rebuilt with Swin's design and training choices, ties Swin-T at 50.4
box AP and runs faster. The lesson is not that transformers beat CNNs. It is that locality, a
feature pyramid and a modern training recipe win on high-resolution perspective cameras, whether the
blocks are attention or convolution.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion &mdash; From ViT to Swin: what a 224-pixel square cannot see</span>
    <a href="../_static/companions/ViT_To_Swin_Companion.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/ViT_To_Swin_Companion.html"
          title="From ViT to Swin: what a 224-pixel square cannot see" loading="lazy"></iframe>
</div>

:::{admonition} Fit card &mdash; Swin
:class: tip
**Idea in one sentence.** Attention inside small shifting windows, merged into a four-level feature pyramid.

**Why it works.** Weights computed from the content, like ViT; locality and four scales, like a CNN; a cost that grows with pixels instead of pixels squared.

**Fits these tasks.** Boxes or masks on full-resolution camera frames: vulnerable road users from a forward camera, turning-movement counts from an intersection camera, lane and pavement maps (*extraction*, *classification*).

**Needs this data.** ImageNet-pretrained weights, plus hundreds to thousands of box- or pixel-labelled frames from your own cameras, split by camera.

**Breaks when.** Latency or power is tight on a roadside or in-vehicle box; objects are only a few pixels tall even at stride 4; you train from scratch on a small dataset.

**Keep the classical method when.** You need one label per frame (a plain ViT or CNN at 224 is enough, as in Lab 6), the edge accelerator is built around convolution, or you only need volumes (loops and radar already count).
:::

:::{admonition} Before you trust this result
:class: warning
**What is the baseline?** ResNet-50 at matched compute. On COCO detection (Cascade Mask R-CNN, Swin
paper Table 2b) Swin-T reaches 50.5 box AP against ResNet-50's 46.3 at 745 G against 739 G FLOPs,
but runs at 15.3 against 18.0 frames per second. A plain ViT (DeiT-S) needed deconvolution layers
bolted on to enter the comparison at all, and scored 48.0 while costing more.

**How was the data split, and why is that honest?** The accuracy numbers are COCO validation photos,
everyday scenes rather than Florida roads, so they rank backbones but say nothing about your cameras.
The timings in the companion use random weights on two CPU threads: they compare backbones fairly
with each other, but they do not predict a GPU or an edge accelerator.

**What does it do on the ugly cases?** Nobody has measured that for you. Night, rain, glare and a
pedestrian six pixels tall are not in either number. Before Swin goes on a county's cameras, re-run
the comparison on that county's footage, with whole cameras held out of training.
:::

(mobilevit)=
## MobileViT: a phone-sized CNN that borrows attention for reach

Swin gives a transformer a CNN's locality. MobileViT goes the other way: it starts from MobileNetV2,
a CNN built to run on a phone, and inserts small transformer blocks for reach. A lane-keeping or
forward-collision camera needs it: whether the dashes far up the image continue the lane, or
whether a red light on the left of the car ahead pairs with the one on the right, is a question about
pixels far apart. A 3 &times; 3 convolution links only neighbours; attention over every pixel costs
too much for a phone.

A MobileViT block makes **two hops**. First, a local *n* &times; *n* convolution (*n* = 3 in the
paper) lets every cell summarise its neighbourhood. Then **unfold**: cut the map into *h* &times; *w*
patches (2 &times; 2 in the paper) and gather the cells at the *same position* inside every patch
into one sequence. Attention inside each sequence carries those summaries across the whole map.
Finally **fold** the cells back onto the grid, and a fusion convolution mixes each cell with its
neighbours and with the block's input. MobileViT-S has three such blocks, at strides 8, 16 and 32.
Think of a dispatcher who never sees the road but hears from every patrol unit,
each of which has looked around its own beat.

Spend your time in three places. **Tab 1** is the mechanism: click a cell of the 24 &times; 24 map,
step through the block, then switch to 4 &times; 4 patches with a 3 &times; 3 kernel and watch holes
open. **Tab 2** follows the lead car's right brake light on a Florida stop-bar frame through
MobileNetV2 and MobileViT-S; set the depth to *stride 8, after MobileViT block 1* and read
the lift table. **Tab 4** sets the saving beside measured latency.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion &mdash; How far can one pixel see? MobileViT's two hops</span>
    <a href="../_static/companions/MobileViT_Receptive_Field_Companion.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/MobileViT_Receptive_Field_Companion.html"
          title="How far can one pixel see? MobileViT's two hops" loading="lazy"></iframe>
</div>

The one equation is what attention over unfolded patches costs:

$$
\text{pairs per attention layer} = P \cdot N^2 = \frac{(HW)^2}{P}
$$

$H \times W$ is the feature map in cells (32 &times; 56 at stride 8 for a 448 &times; 256 frame),
$P = h \cdot w$ the cells per patch and so the number of attention sequences, and $N = HW/P$ the
patches, which is the tokens in each sequence. **In words:** unfold splits one all-to-all problem
into $P$ smaller ones, so 2 &times; 2 patches cut the bill by 4 at every stride: 802,816 pairs against
3,211,264 per head, per transformer layer, in MobileViT-S's first block on that frame. The catch is that two hops tile the map only if
the patch side is no wider than the kernel, $h \le n$ &mdash; patrol units spaced farther apart than
their beats leave road nobody reports on. With 3 &times; 3 kernels, two hops from the centre cell
reach all 576 cells with 2 &times; 2 patches, but 289 with 4 &times; 4. The paper found the rule by
experiment: MobileViT-XS with patch sides (2, 2, 2) scored 74.8% ImageNet top-1 at 7.28 ms on an
iPhone 12; with (8, 4, 2), 73.8% at 5.93 ms.

**How far does one feature actually reach?** Tab 2 measures *sensitivity*: how strongly each input
pixel can move the feature vector at one point (a gradient, after Luo et al.). A braking detector
needs both lights, and the lead car's left brake light is 132 px from the right one, outside every
convolution's reach at stride 8. Before any attention, MobileViT-S puts nothing on it. One block
later it gets 6.0&times; its share of the image area. MobileNetV2 cannot reach it at stride 8, and at
stride 32 gives it 0.31&times;. The honest counterpoint: the red signal heads get 0.87&times; after
block 1, no special attention at all. These are ImageNet weights; the block *can* reach the signals,
but nothing taught it that a signal matters to a braking car. Reach belongs to the architecture; what
flows through it depends on training.

One frame can mislead, so tab 3 repeats the measurement on 64 Tampa Bay FL511 frames from the Lab 6
collection, one per camera, following the centre pixel. Medians: before block 1, half of
MobileViT-S's sensitivity lies within 7 px; after it, within 50 px (24 to 72 across frames), with 53.9%
of the sensitivity outside the square any convolution could reach, so only attention carried it there.
MobileNetV2 spreads that far only at stride 32 (68 px).

**What the reach costs.** Fewer pairs is not faster. On an iPhone 12 the paper reports MobileNetV2 at
0.92 ms and MobileViT-XS at 7.28 ms for classification, 2.3 against 12.6 ms for detection at
320 &times; 320: phone runtimes are tuned for convolution, and unfold, fold and small attention
matrices run slowly on them. On the companion's CPU at 256 &times; 256, MobileViT-XS took 46.9 ms
against MobileNetV2's 21.1 ms with fewer parameters (2.32 M against 3.50 M). The time buys accuracy:
74.8% top-1 for MobileViT-XS and 78.4% for MobileViT-S, against the 71.878% torchvision publishes for
these MobileNetV2 weights. Measure on the device you will ship to.

Where it fits: a braking alert on a phone or dash camera (*classification*), labelled from CAN or
IMU, against red-blob detection plus pairing rules; queue extent from an FL511 camera
(*extraction*), against loop occupancy and shockwave estimates. Check first: timm's MobileViT
weights (`mobilevit_*.cvnets_in1k`) carry the non-free cvnets licence, which limits what you may
build on them, so read it before a class project or a product ships.

:::{admonition} Fit card &mdash; MobileViT
:class: tip
**Idea in one sentence.** Convolutions summarise each neighbourhood, attention among same-position cells of every patch spreads the summaries across the image, and a fusion convolution merges global and local.

**Why it works.** Two hops reach every pixel when the patch is no wider than the kernel, at 1/*P* of the cost of all-pixel attention, and every cell keeps its own token instead of being squashed into a 16 &times; 16 patch.

**Fits these tasks.** On-device classification, detection or segmentation where a local cue needs scene context: paired brake lights, lane continuity, queue extent (*classification*, *extraction*).

**Needs this data.** As for a MobileNet: ImageNet-pretrained weights plus a few thousand labelled frames from your cameras. The context needs no extra labels.

**Breaks when.** The runtime has no fast attention; patches grow wider than the kernel; the weights' licence limits your use.

**Keep the classical method when.** The cue is purely local (a sign crop, a plate) and latency is tight: use a MobileNet. Lanes are clean and the camera fixed: an edge detector and a lane fit are cheaper and easier to audit.
:::

:::{admonition} Before you trust this result
:class: warning
**What is the baseline?** MobileNetV2 with ImageNet weights. MobileViT-S is built from the same
blocks, so the comparison isolates the transformer blocks.

**How was the data split, and why is that honest?** Nothing is trained or tuned and no labels are
used: two forward-camera frames and 64 roadside frames, one per camera, so neither network was fitted
to them. It measures the architecture, not a task.

**What does it do on the ugly cases?** Unknown. Sensitivity is a gradient around one image, not a
decision; the weights are generic ImageNet ones; the FL511 frames come from one late-afternoon sweep.
Fine-tune on driving data, then occlude the cue, before claiming the model uses it.
:::

(convnext)=
## ConvNeXt: Swin, minus the attention

```{figure} ../_static/figures/ConvNeXt_Ladder.png
:alt: A ladder of ImageNet top-1 accuracy: ResNet-50 at 76.1, a gold bar for the modern training recipe to 78.8, then green bars for Swin's design choices written as convolutions, ending at 82.0, past a dashed line at Swin-T's 81.3.
:width: 100%

Copy Swin's recipe and design into a ResNet-50 one step at a time, never adding attention, and it passes Swin-T at the same compute; almost half the gain is the recipe alone.
```

Swin's COCO result invites the conclusion that attention beats convolution. In 2022 a team at Facebook
AI Research and Berkeley tested it (Liu et al., *A ConvNet for the 2020s*): a before-and-after study
that changes ResNet-50 one treatment at a time, copying Swin's choices, and never adds attention. The
gold bar changes only the recipe, to the one Swin was trained with: 300 epochs instead of 90, AdamW,
heavy augmentation. That alone is 76.1 to 78.8, 2.7 of the ladder's 5.9 points. The green bars,
+3.2 more, are Swin's design written as convolution: a 4 &times; 4 stride-4 stem is the patch
embedding, a depthwise convolution mixes space one channel at a time as attention's weighted sum
does, and a 7 &times; 7 kernel is the 7 &times; 7 window. The finished network reaches 82.0 against
Swin-T's 81.3, both at 4.5 GFLOPs.

It holds beyond classification. On COCO (Cascade Mask R-CNN, 3&times; schedule) ConvNeXt-T and Swin-T
tie at 50.4 box AP, at 13.5 against 12.2 frames per second on the paper's GPU, and on the Swin
timings' two-thread CPU a 720 &times; 480 FL511 frame takes ConvNeXt-T 0.50 s against Swin-T's 1.08 s. One caution: the
ConvNeXt paper lists Swin-T at 50.4 and 12.2 FPS where the Swin paper's own table says 50.5 at 15.3,
so compare numbers within one paper.

Two lessons. For your own project: train the baseline with the same recipe as your new model, or you
may be measuring the recipe. For the rest of the module: if a CNN can match Swin on images, the reason
to keep building transformers is the **token**. A token can be masked and filled back in, as in
{doc}`2.5 <notes5-bert>`, read by a query, and mixed with words, lidar points or CAN signals in one
architecture. A CNN can feed a transformer, as DETR does, but the token is the common currency, and
{doc}`2.9 <notes9-cross-attention>` starts there: cross-attention between tokens of different kinds.

:::{admonition} Fit card &mdash; ConvNeXt
:class: tip
**Idea in one sentence.** A ResNet rebuilt with Swin's training recipe and design choices, convolution everywhere.

**Why it works.** Locality and a four-stage pyramid, like Swin; a 7 &times; 7 depthwise convolution does the spatial mixing Swin's windows do.

**Fits these tasks.** A backbone for labels, boxes or masks on camera frames, especially on edge hardware (*classification*, *extraction*).

**Needs this data.** ImageNet-pretrained weights plus hundreds to thousands of labelled frames from your own cameras.

**Breaks when.** The model must also take text prompts, lidar or CAN, so a transformer goes on top anyway.

**Keep the classical method when.** ResNet-50 already meets the accuracy target on your cameras, or you only need counts (loops, radar).
:::

:::{admonition} Before you trust this result
:class: warning
**What is the baseline?** Swin-T at the same compute, and the old ResNet-50 retrained with the new
recipe: the control that separates what the recipe bought from what the design bought.

**How was the data split, and why is that honest?** ImageNet and COCO validation photos, held out
for every backbone alike, but not Florida roads. The CPU timings rank backbones, not devices.

**What does it do on the ugly cases?** Not measured: night, rain and glare are in neither paper. Ask
any vendor for the same recipe, the same compute, a camera-disjoint split and the night frames.
:::

(camera-to-alert)=
## One camera, one alert: three kinds of computation

```{figure} ../_static/figures/Camera_To_Alert_Pipeline.png
:alt: Two lanes: at each camera, a feed check, a convolution backbone, an attention decoder and a tracker; at the TMC, attention-based event reasoning, an operator check and the alert. Each learned stage is tagged with its classical cousin.
:width: 100%

Local pixels get convolution, long-range relations get attention, and known rules stay classical.
```

In a deployed system convolution and attention are not rivals. Follow one FL511 camera to an alert.
The top lane runs on every frame, so it must be cheap. The **feed check** is classical: live, on the
road, day or night? In one September sweep about 491 of the 717 Tampa Bay
feeds returned a live frame. The **backbone** is convolution, because edges, wheels and lane paint are
local. The **decoder** is attention: each object query scans the whole feature map to decide what is
one object, as in RT-DETR. The **tracker** is classical: a Kalman filter follows each object across
frames, and a homography maps its pixels to lane and milepost. The bottom lane works across the
corridor, where attention earns its cost: **event reasoning** relates a stopped car at one camera to
slowing at an upstream detector, and which pairs matter changes with the situation. An **operator** verifies before the alert goes out.

Each learned stage has a classical cousin: the backbone learns kernels like the Sobel kernel you ran
over the CTM speed field; the decoder replaces non-maximum suppression; event reasoning generalises the
California algorithm, which compares one fixed detector pair, where attention learns which pairs to
compare. Three caveats. Many TMCs still use rules for event reasoning (stopped-vehicle timers,
California-type comparisons), so the figure shows where attention *fits*, not what a TMC runs. A
YOLO-class detector would draw the decoder as convolution plus NMS, though recent YOLO versions contain
attention too. And a ByteTrack-style Kalman tracker is still the common deployed default.

## Check yourself

1. A city wants a phone app that warns transit drivers when the vehicle ahead brakes, at 30 frames per
   second. MobileNetV2 or MobileViT-XS? What would you measure before the app ships?
2. A colleague wants to swap Lab 6's ViT-Tiny for Swin-T "because Swin is better." For one congestion
   label per FL511 frame, what does the switch buy, and what does it cost?
3. The TMC wants the pipeline's top lane in each roadside cabinet, on a Jetson Orin Nano. Which
   backbone would you shortlist, and which stage is hardest to move to the edge?

---

Next: {doc}`notes9-cross-attention` &mdash; when the tokens come from two different sources: one sequence reads another.
