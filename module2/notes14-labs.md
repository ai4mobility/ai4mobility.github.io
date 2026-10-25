# Practice, exercises, and further reading

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 2 &middot; Practice</span>
    <span class="notes-card-session">Sessions: all of Module 2</span>
  </div>
  <p class="notes-card-lede">What the labs that go with this module <em>prove</em>, the bridge lab from Module 1 you should run first, the questions this module arms you with, and where transformers go from here. Everything on this page is practice &mdash; the explanations live in sections 2.1&ndash;2.13.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Notebooks that go with it</h4>
      <ul>
      <li><a href="../module1/lab4_clip_vs_traditional_cv.html">Lab 4 &mdash; CLIP versus traditional computer vision</a></li>
      <li><a href="../module6/lab6_vit_finetune.html">Lab 6 &mdash; Fine-tuning a Vision Transformer</a></li>
      <li>Cross-attention sanity check &mdash; <em>in development</em></li>
      </ul>
    </div>
    <div>
      <h4>Every lab in the course</h4>
      <ul>
      <li><a href="../labs.html">All Labs &mdash; the full directory &#8599;</a></li>
      </ul>
    </div>
  </div>
</div>

## What each lab proves

**{doc}`Lab 4 — CLIP vs. traditional computer vision <../module1/lab4_clip_vs_traditional_cv>`**
physically lives in Module 1 and is the bridge into this module. If you skipped it, run it
first. CLIP is the late-fusion dual encoder of section 2.9: two towers that meet only at the end,
which is the baseline every cross-attention design on these pages has to beat.

**{doc}`Lab 6 — Fine-tuning a Vision Transformer <../module6/lab6_vit_finetune>`** lives in
Module 6, where fine-tuning is the topic, and reads with section 2.7: it fine-tunes the ViT-Tiny
that 2.7 dissects on FL511 camera frames. *Proves:* a fine-tune's accuracy splits cleanly into what
the pretrained features gave you for free and what you had to buy by unfreezing &mdash; and that an
after-dark score can rise while the model gets worse, because the label source failed first.

**{doc}`Lab 5 — Attention on a Road Network <../module3/lab5_graph_attention>`** goes with
{doc}`Module 3 <../module3/index>`, where graph neural networks are the topic.

**Cross-attention sanity check** *(in development)*. Build a small cross-attention model on
paired mobility data and ask a question you can actually answer: *does the attention pattern we
expect actually emerge?* The lab runs a three-tier sanity check &mdash; does the model learn the
task, does attention concentrate where the physics says it should, and does the interpretation
survive a control condition.

*Proves:* attention heads often behave as routers rather than as the tidy alignment maps
that published figures suggest. That is the finding sections 2.3, 2.7 and 2.9 reach on pretrained
models from the other direction, and it is a useful corrective before you read your next
attention visualization. Setup notes and difficulty are on the {doc}`All Labs <../labs>` page.

## Using this on the job

Module 2 is the module a vendor conversation will land on. Five questions carry most of the
weight, and each has a section behind it:

- **What is one token, and how many of them is this going to be?** Section 2.1. A price and a
  latency budget follow from the answer, and jargon-heavy agency text fragments badly.
- **What is the classical method this replaces, and has anyone run it?** Sections 2.2, 2.5 and 2.13.
  On two different real corpora in this module, counting words beats a frozen pretrained
  encoder; in section 2.9, OCR and a word match beat a 224-million-parameter vision&ndash;language model.
- **What is the split?** Section 2.13. Agency text is written by a small number of people
  working from templates; a random split measures the template, not the model. For cameras,
  split by camera (sections 2.7 and 2.10).
- **Where do the streams first exchange information?** Sections 2.9 and 2.11. "Fuses camera and
  CAN" can mean two summaries compared once or every token reading every other. Then ask what
  happens when one stream is removed: where a model attends does not prove what it uses.
- **What does a heat map actually show?** Sections 2.7 and 2.9. An attention map or a Grad-CAM is a
  claim to test with a deletion or an edit, not an explanation.

The workflow framing those questions sit inside &mdash; the anatomy, the six leverage labels, the
checkpoint rule &mdash; is in {doc}`5.1 The workflow is the unit of work <../module5/notes1-workflow>`.

## Where this goes next

Apart from the fine-tuning in section 2.5 and Lab 6, this module uses pretrained transformers as
they come. Part II of the course is about changing that: {doc}`Module 5 <../module5/index>` puts a
model in a loop with tools and retrieval, and {doc}`Module 6 <../module6/index>` fine-tunes it.
{doc}`Module 4 <../module4/index>` takes the generative half &mdash; the decoder-only models sketched
in section 2.6 &mdash; into diffusion and world models. The lane-anchor hub of section 2.11 is a graph
with attention on its edges, which is where {doc}`Module 3 <../module3/index>` picks up: every network in this
module drawn as one update on a graph, and then the road network as that graph.

The reading list for this module is on the {doc}`module page <index>`.

---

Next: {doc}`Module 3 — A Unified View: Graph Neural Networks <../module3/index>`.
