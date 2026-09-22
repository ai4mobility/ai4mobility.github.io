# Practice, exercises, and further reading

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 2 &middot; Practice</span>
    <span class="notes-card-session">Session: Sept 17</span>
  </div>
  <p class="notes-card-lede">What the module's lab <em>proves</em>, the bridge lab from Module 1 you should run first, and where transformers go from here. Everything on this page is practice &mdash; the explanations live in sections 2.1&ndash;2.6.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Notebooks that go with it</h4>
      <ul>
      <li><a href="../module1/lab4_clip_vs_traditional_cv.html">Lab 4 &mdash; CLIP versus traditional computer vision</a></li>
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

**Cross-attention sanity check.** Build a small cross-attention model on paired mobility
data and ask a question we can actually answer: *does the attention pattern we expect
actually emerge?* The lab runs a three-tier sanity check &mdash; does the model learn the task,
does attention concentrate where the physics says it should, and does the interpretation
survive a control condition.

*Proves:* attention heads often behave as routers rather than as the tidy alignment maps
that published figures suggest. That is the same finding section 2.3 reaches on a pretrained
model from the other direction, and it is a useful corrective before you read your next
attention visualization. Setup notes and difficulty are on the {doc}`All Labs <../labs>` page.

**{doc}`Lab 4 — CLIP vs. traditional computer vision <../module1/lab4_clip_vs_traditional_cv>`**
physically lives in Module 1 and is the bridge into this module. If you skipped it, run it
first &mdash; the multimodal embedding space it builds is the foundation for everything in
section 2.6.

## Using this on the job

Module 2 is the module a vendor conversation will land on. Three questions carry most of the
weight, and each has a section behind it:

- **What is one token, and how many of them is this going to be?** Section 2.1. A price and a
  latency budget follow from the answer, and jargon-heavy agency text fragments badly.
- **What is the classical method this replaces, and has anyone run it?** Sections 2.2 and 2.7.
  On two different real corpora in this module, counting words beats a frozen pretrained
  encoder.
- **What is the split?** Section 2.7. Agency text is written by a small number of people
  working from templates; a random split measures the template, not the model.

The workflow framing those questions sit inside &mdash; the anatomy, the six leverage labels, the
checkpoint rule &mdash; is in {doc}`Module 7 §7.1 <../module7/notes>`.

## Where this goes next

This module stops at using a pretrained transformer as it comes. {doc}`Module 4 <../module4/index>`
is about changing that: retrieval-augmented generation, parameter-efficient fine-tuning, RLHF,
and agentic systems that call tools. {doc}`Module 3 <../module3/index>` takes the generative
half &mdash; the decoder-only models sketched in section 2.5 &mdash; into diffusion and world models.

The reading list for this module is on the {doc}`module page <index>`.

---

Next: {doc}`Module 3 — Generative AI and World Models <../module3/index>`.
