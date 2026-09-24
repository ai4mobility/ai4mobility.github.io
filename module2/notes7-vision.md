# 2.7 Transformers that see: ViT and multimodal

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 2 &middot; Section 2.7</span>
    <span class="notes-card-session">Session: Sept 17</span>
  </div>
  <p class="notes-card-lede">Cut an image into patches, call each one a token, and the architecture from 2.3 works without modification &mdash; which raises the question the paper had to answer: with convolution's built-in locality gone, does the model learn to look in sensible places? This section reads the attention weights on real road scenes, against the Grad-CAM you already built in Module 1.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Interactive companions on this page</h4>
      <ul>
      <li><a href="../_static/companions/ViT_Attention_Companion.html" target="_blank" rel="noopener">Where is it looking? Attention in a Vision Transformer &#8599;</a></li>
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

---

Next: {doc}`notes8-evaluation` &mdash; whether any of it beats the method it would replace.
