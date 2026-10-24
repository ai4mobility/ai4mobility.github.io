# 2.7 Transformers that see: the Vision Transformer

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 2 &middot; Section 2.7</span>
    <span class="notes-card-session">Session: Oct 8</span>
  </div>
  <p class="notes-card-lede">Cut a camera frame into 16-pixel patches, call each one a token, add a [CLS] token, and the encoder from 2.3 classifies images. This section trains one to read congestion from FL511 frames, shows why the ViT paper needed 303 million images to pass the best CNNs on ImageNet, and measures where a ViT looks, against the Grad-CAM you built in Module 1.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Interactive companion on this page</h4>
      <ul>
      <li><a href="../_static/companions/ViT_Attention_Companion.html" target="_blank" rel="noopener">Where is it looking? Attention in a Vision Transformer &#8599;</a></li>
      </ul>
    </div>
    <div>
      <h4>Notebooks that go with it</h4>
      <ul>
      <li><a href="../module6/lab6_vit_finetune.html">Lab 6 &mdash; Fine-tuning a Vision Transformer</a></li>
      <li><a href="../module1/lab4_clip_vs_traditional_cv.html">Lab 4 &mdash; CLIP versus traditional computer vision</a></li>
      </ul>
    </div>
  </div>
</div>

## What this section covers

- How a ViT is trained to classify a frame, and why its loss is a logit likelihood
- Blocks, heads, and attention distance: how far one head reads
- Inductive bias: what convolution builds in, and what a ViT must learn from data
- ViT against CNNs on ImageNet and on our own FL511 frames
- A short recap of Grad-CAM, as the bridge to attention maps
- Attention maps: the `[CLS]` row, patches that hog it, rollout, class relevance, and the deletion test

(vit-training)=
## How a ViT learns to classify a frame

```{figure} ../_static/figures/ViT_Train_Pipeline.png
:alt: Top, pre-training on ImageNet-21k, then fine-tuning on FL511 frames with a new linear head. Below, one training step on an I-75 frame: tokens, 12 blocks, the [CLS] output, a linear head, three class probabilities, the loss.
:width: 100%

A ViT is pre-trained on millions of images by a large lab and then fine-tuned briefly by you, and both times the answer comes from the `[CLS]` token alone.
```

{doc}`2.1 <notes1-tokens>` made each 16 &times; 16 patch a token; add one more, `[CLS]`, and the
encoder from {doc}`2.3 <notes3-attention>` runs unchanged. In the figure, a 224 &times; 224 I-75 frame
becomes 196 patch tokens plus `[CLS]`, twelve blocks run, and only the `[CLS]` output is kept, 192
numbers in ViT-Tiny, because training makes it the token that carries the answer. A linear head turns
it into three scores (light, moderate, heavy traffic) and softmax into probabilities.

Nobody trains a ViT from nothing on a few thousand frames. Stage 1 is done once by a large lab: the ViT
paper used ImageNet-21k, 14 million images in 21k classes. Stage 2 is yours, in
{doc}`Lab 6 <../module6/lab6_vit_finetune>`: attach a new linear head of 192 &times; 3 + 3 = **579**
weights and fine-tune everything on 1,375 FL511 daylight frames for three epochs. The loss is one you
have estimated before:

$$\mathcal{L} = -\frac{1}{N}\sum_{n} \log \operatorname{softmax}\big(W z_0^{(n)} + b\big)_{y_n}$$

$z_0^{(n)}$ is the `[CLS]` output for frame $n$; $W$ and $b$ are the head's 3 &times; 192 weights and
3 biases; $y_n$ is the observed class; $N$ is the frames in a batch (16 in Lab 6). **In words:** push
up the probability of the observed class &mdash; maximum likelihood for a multinomial logit, with
congestion classes as the alternatives and the 192 numbers in `[CLS]` as the attributes. Unlike a
mode-choice model's, these attributes are learned too, by the gradient flowing into all twelve blocks.

The new head starts at zeros, so every class begins at 1/3, a loss of 1.10 (= ln 3). After the
fine-tune the frame in the figure (13 vehicles counted: heavy) gets p(heavy) = 0.98, a loss of 0.02
&mdash; but it is a training frame; on unseen cameras the model is right 71.2% of the time. The model
name records the whole history: `vit_tiny_patch16_224.augreg_in21k_ft_in1k` was pre-trained on
ImageNet-21k and fine-tuned on ImageNet-1k, the first thing to check when a vendor quotes an accuracy.

## Inside the encoder: how far a head reads

ViT-B/16, the model behind every attention measurement here, passes 197 tokens of 768 numbers through 12
blocks in series: block 5 sees only what block 4 handed it. Inside each block, 12 heads read the same
tokens in parallel, each with its own query, key and value of 64 numbers (768 &divide; 12) and its own
197 &times; 197 map, like twelve operators in a traffic management centre watching one video wall for
different things. Heads split the width; they do not add to it. That makes 144 maps.

```{figure} ../_static/figures/Attention_Distance_How.png
:alt: The I-75 frame with the dark-SUV patch as the query and shading where block 1, head 3 reads, beside a table of weights times distances summing to 68.5 px.
:width: 100%

Attention distance is an attention-weighted average of how far a patch reads: 68.5 px for the SUV patch in block 1, head 3, and 73.6 px over every patch.
```

The paper's first measurement asks how far each head reads. Feed the I-75 frame to ViT-B/16 with the
authors' weights and take one query, patch #105, the dark SUV. In block 1, head 3, its row splits its
reading across the 196 patches (`[CLS]` dropped, the row renormalised to sum to 1): its own patch takes
the largest share, 0.086, but 0.783 is spread over 191 others, so weight every distance and add:

$$d_h = \frac{1}{196}\sum_{i}\sum_{j} a^{h}_{ij}\,\lVert p_i - p_j \rVert$$

$a^h_{ij}$ is the share of patch $i$'s attention that head $h$ puts on patch $j$; $p_i$ is the centre
of patch $i$ in pixels of the 224 &times; 224 frame, so a distance runs from 0 to 294 px; the sum covers
all 196 query patches. **In words:** a row of $a^h$ is a trip-distribution row, the distances are the
skim, and $d_h$ is the head's **average trip length** &mdash; 68.5 px for the SUV, 73.6 px over all
queries. A head that reads only its own patch scores zero, as block 1, head 5 does here.

Follow the SUV patch upward. Its nearest-reading head goes 0 &rarr; 20 &rarr; 45 &rarr; 77 px in blocks
1, 4, 8 and 12, so no local head is left at the top, while the farthest reads 92 to 117 px in each,
from the first block on &mdash; which no early CNN layer can do. Over the whole frame the mean dips
from 71 to 55 px in block 2, then climbs to 125 px by block 12. The distance is where a head *does*
read on average, not the farthest it *could*; and far is not the same as useful: in block 8 the
farthest head puts 86.8% of the SUV's reading on the top row of patches, mostly sky and only 7.1% of
the frame, a pattern that returns in the {ref}`attention maps <attention-maps>`.

## An image is worth 16&times;16 words

*An image is worth 16&times;16 words*, the paper that made the transformer a vision architecture, had
to prove its own case: with a CNN's built-in locality removed, does the model learn to look in sensible
places? It answers with how far each head reaches and a picture of what the class token drew from, and
the companion below reproduces both on three road scenes, one of them the Florida stop-bar frame of
{doc}`1.3 <../module1/notes3-cnn>` and the Grad-CAM companion.

```{figure} ../_static/figures/ViT_vs_CNN_Reach.png
:alt: Left, mean attention distance of every ViT-B/16 head by block: green dots (pre-trained on ImageNet-21k) include a purely local head in block 1; hollow gold dots (ImageNet-1k only) do not. Right, ResNet-50's receptive field by stage.
:width: 100%

Locality is learned by a ViT and built into a CNN: with 14 million images the ViT finds local heads in block 1, with 1.3 million it never does.
```

Nobody told the green model that nearby pixels matter; it found out from data. ResNet-50 gets
locality for free: a unit can see at most 7 px after the first layer, 35 after the first stage, 427
after the last. A built-in assumption is a head start when data is scarce and a ceiling when it is plentiful,
like a cell-transmission cell that talks only to its neighbours.

Spend your time in three places. **Tab 2** ships the model's real query and key vectors, so clicking a
patch computes the attention weight in front of you; switch between a head that reaches 17.7 px and one
that reaches 107.3 px in the same block, and turn off the &divide;&radic;d scaling to watch the softmax
saturate. **Tab 3** holds the numbers behind the figure, the paper's Figure 11 on our frames, run twice:
the authors' released weights give block 1 a head with an attention distance of 0.02 px and another at
116.2 px, while the *same architecture* trained on ImageNet-1k alone has no local head in block 1 at
all. Remove a CNN's inductive bias and data is what puts it back &mdash; the reason to think hard before
fine-tuning a ViT on four thousand of your own frames from a small-data checkpoint. **Tab 5** puts the
ViT's map beside a ResNet-50 Grad-CAM on the same pixels, same classes, same score: asked about the
traffic light, the ViT lands 2.09&times; its fair share of heat on the five signal heads and the CNN
lands 0.56&times;, below what random heat would give. Before you believe any of it, run tab 6's
deletion test &mdash; where blanking the top patches of the paper's own class-free rollout first
makes the ViT *more* sure of "traffic light", a class it does not already favour. Both are taken
apart {ref}`below <attention-maps>`.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion &mdash; Where is it looking? Attention in a Vision Transformer</span>
    <a href="../_static/companions/ViT_Attention_Companion.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/ViT_Attention_Companion.html"
          title="Where is it looking? Attention in a Vision Transformer" loading="lazy"></iframe>
</div>

:::{admonition} Before you trust this result
:class: warning
**What is the baseline?** Two of them, and the page runs both. Random heat is the floor for
any saliency claim &mdash; the CNN's 0.56&times; on the signal heads is *below* it. And the ResNet-50
Grad-CAM from {doc}`1.4 <../module1/notes4-cnn-in-practice>` is the incumbent method the ViT
map has to beat on the same pixels and the same score.

**How was the data split, and why is that honest?** Nothing here is trained by you, which is
the point: the two ViT-B/16 checkpoints differ mainly in how much data they saw (the ImageNet-1k
one is torchvision's, with its own recipe). The comparison is honest because the architecture is
held fixed and the pretraining corpus is the main variable.

**What does it do on the ugly cases?** Tab 6's deletion test is the ugly case. Blanking the top
patches of the paper's own class-free rollout first raises p(traffic light), to 4.28&times; its start
at 10% blanked against 0.97&times; for random: for a class the model does not already favour,
rollout's top patches are not its evidence &mdash; so a published visualisation method can fail on
exactly the classes you care about, which in a roadway scene are the rare ones.
:::

(vit-vs-cnn)=
## What data buys: ImageNet, then our own frames

On ImageNet-1k alone (1.3 million images) the 2020 ViT landed mid-pack: ViT-B/16 scored 77.9, 0.4
points below a ResNet-152 from five years earlier, and ViT-L/16, with three and a half times the
parameters, scored 76.5 &mdash; overfitting, not missing capacity. (ViT at 384 px, CNNs at 224 px,
so the gap is approximate.) Pre-trained on JFT-300M, Google's internal set of 303 million images,
ViT-L/16 reached 87.76, edging past BiT-L, a ResNet-152 four times wider, at 14.6&times; less
pre-training compute (ViT paper, Table 2). The same network climbs 76.5 &rarr; 85.30 &rarr; 87.76
from ImageNet-1k to ImageNet-21k to JFT, eleven points from data alone:
"the convolutional inductive bias is useful for smaller datasets," in the paper's words.

```{figure} ../_static/figures/ViT_vs_CNN_FL511.png
:alt: Bars of daylight accuracy on unseen FL511 cameras for ResNet-18 and ViT-Tiny from scratch, and ResNet-18, DeiT-Tiny and ViT-Tiny pretrained then fine-tuned, against a dashed always-"moderate" line.
:width: 100%

From scratch the ViT learns nothing usable from our frames; pretrained, both architectures jump more than twenty points, and what separates them is mostly what they were pre-trained on.
```

Now Lab 6's task, light, moderate or heavy from one FL511 frame, one split for every network: 1,101
daylight frames from 277 cameras train, 274 frames from 69 other training cameras choose the learning
rate, and 591 daylight and 296 after-dark frames from 148 unseen cameras test. From scratch, ResNet-18
reaches 43.8%, about 7 points above always answering "moderate" (36.4%); ViT-Tiny, given three
learning rates to the CNN's one, reaches 35.2%, and even its best learning rate picked on the test set,
which you must never do, gets 40.1%. Pretrained, the order is not CNN versus transformer: ViT-Tiny
pre-trained on ImageNet-21k leads at 68.9%, DeiT-Tiny (same size, ImageNet-1k only) trails at 63.6%,
ResNet-18 sits at 65.5%, and a 5.3-point spread on one seed is within what a second seed could move.
(All sit below Lab 6's 71.2% because 20% of its training cameras are held out here to pick the
learning rate, and every run uses the same light augmentation.) The architecture question is
mostly a question of which pre-trained weights you can get.

| | CNN (ResNet) | ViT |
|---|---|---|
| Built-in assumption | Nearby pixels matter; same filter everywhere | None: every patch talks to every patch |
| What one early layer sees | 7 px after conv1, 35 px after layer1 | Anywhere (block-1 heads 0&ndash;116 px) |
| From scratch on ~1,000 of our frames | Learns something (43.8% vs 36.4%) | Learns nothing usable; wants 14 M+ images or heavy augmentation |
| With good pre-trained weights | Strong, cheap, well understood | Equal or better; transfers well |
| Cost as frames grow | About linear in pixels | Quadratic in tokens ({doc}`2.8 <notes8-locality>`) |

:::{admonition} Fit card &mdash; ViT for classification
:class: tip
**Idea in one sentence.** Cut the frame into patches, let every patch attend to every other, classify from the `[CLS]` token.

**Why it works.** No locality is built in, so with enough data it learns which regions matter, near or far.

**Fits these tasks.** One label per frame: congestion level, weather, road-surface condition, a flooded lane (*classification*).

**Needs this data.** Pre-trained weights (read the model name) plus a few thousand labelled frames from your own cameras, split by camera.

**Breaks when.** Trained from scratch on small data; objects shrink to a few pixels at 224 px; very high-resolution input.

**Keep the classical method when.** A loop or radar already gives the count, or a pretrained CNN is as good and cheaper on your box.
:::

:::{admonition} Before you trust this result
:class: warning
**What is the baseline?** On ImageNet, the strongest CNNs on the *same* pre-training data. On our
frames, always "moderate" (36.4%) and a ResNet-18 trained the same way on the same split.

**How was the data split, and why is that honest?** Ours is by camera, never by frame, with the
learning rate chosen on held-out training cameras, never on the test set. JFT-300M is Google-internal:
nobody outside can re-run that pre-training.

**What does it do on the ugly cases?** ImageNet photographs centre one large object; a 720 &times; 480
CCTV frame at night does not. After dark, never seen in training, the pretrained models score 61.5%
(ResNet-18), 65.9% (DeiT-Tiny) and 67.9% (ViT-Tiny) &mdash; on one seed, against labels from a
detector's vehicle counts that fail after dark (Lab 6).
:::

(attention-maps)=
## Where did it look? Attention maps against Grad-CAM

The classifier reads only `[CLS]`, so the map that matters is `[CLS]`'s row, and the yardstick is the
Grad-CAM you already use for CNNs.

### First, a CNN recap

A CNN channel is one filter's answer at every location. A ResNet-18 conv1 filter is
7 &times; 7 &times; 3 = 147 weights; over a brake light on the stop-bar frame its products add to 15.04,
one number (2.74 after BatchNorm and ReLU), and sliding it everywhere gives a "red light" feature map.
Stages 2 to 4 each halve the grid and double the channels, up to 512, so a stage-4 cell covers 32 px
yet can be influenced by a region 435 px wide.

```{figure} ../_static/figures/GradCAM_Two_Classes.png
:alt: The Florida stop-bar frame twice with ResNet-18 Grad-CAM heat: asked "traffic light", heat on the mast arm and signal heads; asked "sports car", heat on the back of the lead car.
:width: 100%

Same frame, same CNN, two questions, two maps: a Grad-CAM map answers a question about one class, not about the image.
```

{ref}`Grad-CAM <saliency-maps>` turns stage 4 into a map for one class. At 672 &times; 416 stage 4 is
512 maps of 21 &times; 13 = 273 cells, and "traffic light", the top class, scores 8.33:

$$\alpha_k^c = \frac{1}{Z}\sum_{i,j}\frac{\partial y^c}{\partial A^k_{ij}},\qquad L^c = \mathrm{ReLU}\Big(\sum_k \alpha_k^c A^k\Big)$$

$A^k$ is stage-4 map $k$, $y^c$ the class score before softmax, $Z$ the 273 cells, $\alpha_k^c$ how
much the class depends on map $k$. **In words:** weight each map by how much the score rises with it,
add, keep the positive part. Before the ReLU, the 273 cells add to 8.32, which plus the last
layer's bias is the score: the map splits the score across locations, as a utility splits into attribute contributions. **Fair
share** is a box's share of the heat over its share of the frame (1.00&times; = spread evenly). Two
cautions carry over to every map below: a signal head is about 7 px wide and a cell 32, so the blob is
interpolation; and a map shows where evidence sits, not why the model is right.

### The `[CLS]` row, and the patches that hog it

Attention weights come free with the forward pass. In block 12, head 3, row 0 of the 197 &times; 197
matrix is `[CLS]`'s split of its reading; drop its weight on itself and fold the other 196 into the
14 &times; 14 grid. No class is named, so the map is the same whatever you ask. The frame here is a
queued arterial with a white SUV in the left foreground, a wing mirror at the right edge and a motorcyclist on the
ramp beside the queue &mdash; a stock photograph we cannot republish, so its maps are described. Head
3's largest weight is 0.046, and 34 patches hold half its reading.

Block 12's twelve heads disagree, so tools average them, and the average's four brightest patches are
background: gantry, sky, far trees. They are exactly the four whose vectors enter block 12 at
14.6&ndash;17.1&times; the median patch's length, every other patch being under twice the median: 2% of
the frame holding 19% of the averaged map, and 73% of head 5's reading. On all 13 course frames, 4 to
14 such patches (2&ndash;7% of the frame) hold 19&ndash;47%. It is the parking on `[SEP]` from
{doc}`2.3 <notes3-attention>` again: Darcet et al. (ICLR 2024) call these high-norm tokens,
low-information patches used as scratch space, and fix them with spare *register* tokens. Weight is not
content, either: weighting head 5's row by its value vectors' length cuts its share on the four from
73% to 24%.

### Same pixels: Grad-CAM, rollout and class relevance

A raw `[CLS]` map ("where did `[CLS]` read, for no class") is not comparable with Grad-CAM ("what
raised this class"). Feed the same 224 &times; 224 pixels to ResNet-50 and the ViT and ask about two
classes both rank in their top six, "cab" (ImageNet's label nearest the SUV) and "car mirror".
**Grad-CAM** follows the question: 2.01&times; on the SUV for "cab", 3.05&times; on the mirror for "car
mirror", its two maps correlating at only r = 0.54. **Attention rollout** (Abnar &amp; Zuidema, 2020)
chains all twelve blocks, head-averaged with the identity added for the skip connection; with no class
named, one map serves every class: 1.36&times; on the SUV, 1.21&times; on the mirror. **Class
relevance** (after Chefer, Gur &amp; Wolf, 2021) weights each attention map by the class score's gradient
before chaining; it moves with the question (r = 0.70) but lands only 1.04&times; and 1.20&times;. The
raw head-averaged row puts 0.49&times; on the SUV and 1.73&times; on the band of gantry and sky.

Grad-CAM wins this frame; on the companion's stop-bar frame the ranking flips, 2.09&times; against
0.56&times;. The two frames are reported separately, never pooled: one frame decides nothing, and nor
does one input size &mdash; in the recap's ResNet-18 (not this ResNet-50), four of the five signal
heads are under 3 px wide at 224 &times; 224 and the "traffic light" map puts 1.07&times; on them,
against 2.30&times; at 672 &times; 416. Asked "motor scooter", Grad-CAM puts 0.83&times; on the
motorcyclist, 3 px wide at 224: no map here can point at him.

### Does the map show what was used?

```{figure} ../_static/figures/AttnMap_Deletion.png
:alt: Left, p(cab) relative to its start as top-ranked patches are blanked, one curve per map plus random controls. Right, each map's score against random on 13 course frames.
:width: 100%

A map is a claim about what the model used; blanking what it ranks first tests the claim, and on this frame the class-free raw `[CLS]` row fails it.
```

The **deletion test** checks the claim: blank the patches a map ranks highest (set them to the mean
pixel) and watch the class probability, against blanking in random order on the same model. Asked
about "cab", class relevance takes p to 0.06&times; its start by 50% blanked and rollout to 0.01&times;
by 30%; Grad-CAM wobbles (0.39&times; at 10%, 0.93&times; at 20%) because blanking also removes evidence
for rival classes; and blanking the raw row's top patches makes the model *more* sure, 1.52&times; at
30%, because they are the four high-norm patches. Over 13 frames, each model explaining its own top
class, relevance beats random on 13, rollout 12, Grad-CAM 11, the raw row 10. But rollout is not
class-specific: it points at what the model needs for the classes it already favours. So the
companion's Tab 6, asking the stop-bar frame about "traffic light", which the ViT ranks only fourth
there, finds that blanking rollout's top patches first *raises* p(traffic light), to 4.28&times; at
10% blanked, while random blanking leaves it at 0.97&times;.

The strongest test needs no map. {doc}`Lab 6 <../module6/lab6_vit_finetune>` cropped the camera banner
off every FL511 frame and retrained: accuracy on unseen cameras moved from 71.2% to 69.2%, a 2-point
answer no map can give.

:::{admonition} Fit card &mdash; ViT attention maps
:class: tip
**Idea in one sentence.** The `[CLS]` row is a free map of where the classifier read; rollout chains it through the blocks, class relevance adds the class.

**Why it works.** The head reads only `[CLS]`, which gathers from the patches through exactly these weights.

**Fits these tasks.** Auditing camera models for shortcuts: does a CCTV congestion model read vehicles or the banner, a pedestrian classifier the person or the crosswalk paint (*judgment*).

**Needs this data.** The model's weights, your frames, boxes for what matters, a deletion test.

**Breaks when.** Objects under one 16-px patch; high-norm patches soak up the weight; one head read as "the" answer.

**Keep the classical method when.** A crop-and-retrain or occlusion test answers it directly, or a validated CNN with Grad-CAM exists.
:::

:::{admonition} Before you trust this result
:class: warning
**What is the baseline?** Blanking in random order, same model, same frame; and for a ViT map,
Grad-CAM compared with class relevance for the same class on the same pixels, never with raw attention.

**How was the data split, and why is that honest?** Nothing is trained, so nothing leaks: 13 course
frames, each model on its own top class, scored within a model and never across, because the two
models react differently to grey squares.

**What does it do on the ugly cases?** Grey squares are images neither model trained on, so part of
every drop is a reaction to them; rollout can win by blanking the whole scene; and a 3-px motorcyclist
is invisible to every map.
:::

## Check yourself

1. A district has 900 labelled frames of flooded versus dry roadway from its own CCTV and no
   pre-trained weights it may use. ViT or CNN, and why?
2. Your Lab 6 congestion ViT's averaged attention map lights up the banner burned into the FL511
   frames. Is it reading the banner? What would settle it?
3. A vendor shows a ViT attention map glowing on a pedestrian as proof its ADAS "sees pedestrians".
   What do you ask before accepting it?

Every ViT run on road frames here used a 224 &times; 224 square, which no camera in this course delivers.

---

Next: {doc}`notes8-locality` &mdash; plain ViT on a full-resolution camera, and the three ways locality comes back.
