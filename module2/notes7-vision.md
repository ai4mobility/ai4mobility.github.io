# 2.7 Transformers that see: ViT and multimodal

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 2 &middot; Section 2.7</span>
    <span class="notes-card-session">Session: Sept 17</span>
  </div>
  <p class="notes-card-lede">Cut an image into patches, call each one a token, and the architecture from 2.3 works without modification &mdash; which raises the question the paper had to answer: with convolution's built-in locality gone, does the model learn to look in sensible places? This section reads the attention weights on real road scenes, against the Grad-CAM you already built in Module 1, then takes the same model to a full-resolution camera frame, where it breaks, and shows how Swin repairs it.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Interactive companions on this page</h4>
      <ul>
      <li><a href="../_static/companions/ViT_Attention_Companion.html" target="_blank" rel="noopener">Where is it looking? Attention in a Vision Transformer &#8599;</a></li>
      <li><a href="../_static/companions/ViT_To_Swin_Companion.html" target="_blank" rel="noopener">From ViT to Swin: what a 224-pixel square cannot see &#8599;</a></li>
      </ul>
    </div>
    <div>
      <h4>Notebooks that go with it</h4>
      <ul>
      <li><a href="../module1/lab4_clip_vs_traditional_cv.html">Lab 4 &mdash; CLIP versus traditional computer vision</a></li>
      </ul>
    </div>
  </div>
</div>

## What this section covers

- Vision transformers: an image as a sequence of patches
- Inductive bias &mdash; what convolution gives you for free, and what data has to replace
- Attention distance, and reading a ViT map against a CNN Grad-CAM
- Where plain ViT breaks on a full-resolution camera frame, and how Swin's windows, shifted windows and patch merging fix it
- Vision&ndash;language models: contrastive alignment, captioning, visual question answering
- Multimodal foundation models on driving scenes and roadway imagery
- Deletion tests: how to check a saliency method before you publish one

*The written section is posted after the Sept 17 meeting. Until then the companion
below is the material &mdash; it is the assigned preparation and it carries every number
this section will argue from.*

## An image is worth 16&times;16 words

The sections before this one treat attention as machinery you configure. This one reads it
as evidence. *An image is worth 16&times;16 words* is the paper that made the transformer a vision
architecture, and it had to prove its own case: with a CNN's built-in locality removed, does
the model actually learn to look in sensible places? The paper answers with two measurements &mdash;
how far each attention head reaches, and a picture of what the class token drew from &mdash; and both
are reproduced here on three road scenes, one of them the same Florida stop-bar frame the
convolution slides and the Grad-CAM companion use.

Spend your time in three places. **Tab 2** ships the model's real query and key vectors, so
clicking a patch computes the attention weight in front of you; switch between a head that
reaches 17.7 px and one that reaches 107.3 px in the same block, and turn off the &divide;&radic;d scaling
to watch the softmax saturate. **Tab 3** is the paper's Figure 11 on our frames, run twice: the
authors' released weights give block 1 a head with an attention distance of 0.02 px and another
at 116.2 px, while the *same architecture* trained on ImageNet-1k alone has no local head in
block 1 at all. That single table is the paper's central claim &mdash; remove a CNN's inductive bias
and data is what puts it back &mdash; and it is the reason to think hard before fine-tuning a ViT on
four thousand of your own frames from a small-data checkpoint. **Tab 5** puts the ViT's map
beside a ResNet-50 Grad-CAM on the same pixels, same classes, same score: asked about the
traffic light, the ViT lands 2.09&times; its fair share of heat on the five signal heads and the CNN
lands 0.56&times;, below what random heat would give. Before you believe any of it, run tab 6's
deletion test &mdash; where you will find that the paper's own class-free rollout is *worse* than
random for a class the model does not already favour.

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
the point: the two checkpoints differ only in how much data they saw. The comparison is
honest because the architecture is held fixed and the pretraining corpus is the only variable.

**What does it do on the ugly cases?** Tab 6's deletion test is the ugly case. The paper's own
class-free attention rollout comes out worse than random for a class the model does not
already favour &mdash; so a published visualisation method can fail on exactly the classes you
care about, which in a roadway scene are the rare ones.
:::


(vit-to-swin)=
## Where plain ViT breaks on a real camera, and how Swin fixes it

```{figure} ../_static/figures/Swin_Dilemma.jpg
:alt: The same forward-camera frame fed to a ViT three ways. Squashed to 224 by 224 the child is a smudge less than half a patch tall; centre-cropped, the child is outside the image; at full resolution the child is visible but the frame becomes 9,196 tokens.
:width: 100%

Three ways to hand a 1928 &times; 1208 forward-camera frame to a ViT. Shrink it and the child is half a patch; crop it and the child is gone; keep every pixel and each layer compares 84.6 million pairs of tokens per head.
```

The ViT above reads a 224 &times; 224 square. No camera in this course delivers one. FL511's
roadside CCTV is mostly 720 &times; 480, an intersection camera 1920 &times; 1080, the forward camera
in the {ref}`scooter case <scooter-kid-case>` 1928 &times; 1208, and drone video like highD
4096 &times; 2160. Something has to give between the camera and the model, and on the scooter clip
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

---

Next: {doc}`notes8-evaluation` &mdash; whether any of it beats the method it would replace.
