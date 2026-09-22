# Module 2 — Transformers, LLMs, and Multimodal Models

*Week 4 of the {doc}`../syllabus` — Sept 17, 2026.*

## Class meetings

| Date | Session topic | Due before class |
|---|---|---|
| Sept 17 | Transformers, large language models, vision-language models, and multimodal foundation models | **Confirmed project team and topic**; short assignment as assigned |

## Overview

Module 1 ended with embeddings — a single fixed vector per word, per image, per road
segment. That's a real limitation: "turn" means something different on a signal timing sheet
than it does in a lane-change trajectory, and a static vector can't tell them apart.

**Attention** solves this by letting every element of a sequence look at every other element
and decide what it needs. A transportation reader already has intuition for this: a signal
controller arbitrates among competing approaches, weighting each by how much demand it is
carrying right now. Self-attention does the same thing over tokens, learns the weighting from
data, and does it many times in parallel.

This module covers the architecture that resulted, the large language models built from it,
and the vision-language models that extend it across modalities — plus an honest accounting of
what these systems cannot do for transportation problems.

## The module, page by page

:::{admonition} How to read this module
:class: tip
All seven sections pair with the Sept 17 meeting; skim before, read properly after. Each page
opens with a card naming its session and the interactive companion embedded in it.

The companions are the same pages posted on Canvas, and they are not decoration — most of the
results argued in these sections are only convincing if you move the sliders yourself. If you
read only one before class, read {doc}`2.1 Tokens <notes1-tokens>`: what a token is decides
whether everything after it is affordable.

The sections run in the order the machine does — what goes *in* (2.1), what comes out the
other side (2.2), the mechanism in between (2.3), one whole model written out in code (2.4),
then the architecture pointed at your own data (2.5), at pixels (2.6), and finally at the
question of whether it beats the method it would replace (2.7).
:::

<div class="practice-table-wrap">
<table class="practice-table notes-map">
<thead>
<tr><th style="width:26%">Page</th><th style="width:44%">What it covers</th><th style="width:30%">Companions &amp; notebooks</th></tr>
</thead>
<tbody>
<tr>
  <td><a href="notes1-tokens.html"><strong>2.1 Tokens: the unit a model actually reads</strong></a><br><em>Sept 17</em></td>
  <td>Subword tokenization; byte-pair encoding as a design; what transportation jargon costs when it fragments; context windows, latency and price; an image as a sequence of patches.</td>
  <td><a href="../_static/companions/Tokenization_Companion.html" target="_blank" rel="noopener">Tokens &#8599;</a></td>
</tr>
<tr>
  <td><a href="notes2-contextual.html"><strong>2.2 From static to contextual vectors</strong></a><br><em>Sept 17</em></td>
  <td>Why one vector per word fails; a vector per <em>occurrence</em>; masked language modelling; encoder-only models layer by layer; frozen features versus fine-tuning, and what each is worth against counting words.</td>
  <td><a href="../_static/companions/Word2Vec_to_BERT_Companion.html" target="_blank" rel="noopener">Word2vec to BERT &#8599;</a><br><a href="../module1/lab2_word_embeddings.html">Lab 2</a></td>
</tr>
<tr>
  <td><a href="notes3-attention.html"><strong>2.3 Attention: the mechanism</strong></a><br><em>Sept 17</em></td>
  <td>Self-attention as learned routing; queries, keys and values; the scaled dot product; multi-head attention and positional encoding; how to read an attention map honestly.</td>
  <td><a href="../_static/companions/Attention_Query_Companion.html" target="_blank" rel="noopener">Attention depends on the query &#8599;</a></td>
</tr>
<tr>
  <td><a href="notes4-gpt.html"><strong>2.4 Building one: a GPT you can read</strong></a><br><em>Sept 17</em></td>
  <td>The same five operations as code: Q, K and V as three projections; the scaled dot product; the causal mask and what a missing one costs; softmax written out; how the shapes stay free of B and T; baselines before conclusions.</td>
  <td><a href="../_static/companions/GPT_From_Scratch_Companion.html" target="_blank" rel="noopener">A GPT you can read &#8599;</a><br><a href="../_static/code/gpt_from_scratch.py" download>gpt_from_scratch.py</a></td>
</tr>
<tr>
  <td><a href="notes5-architecture.html"><strong>2.5 The transformer as a research architecture</strong></a><br><em>Sept 17</em></td>
  <td>Encoder-only, decoder-only and encoder&ndash;decoder designs; pretraining and scaling; designing your own tokens; attention masks as a modelling choice; sizing a claim against the naive baseline.</td>
  <td><a href="../_static/companions/Transformer_As_Architecture_Companion.html" target="_blank" rel="noopener">Your own tokens &#8599;</a></td>
</tr>
<tr>
  <td><a href="notes6-vision.html"><strong>2.6 Transformers that see: ViT and multimodal</strong></a><br><em>Sept 17</em></td>
  <td>Images as patch sequences; what inductive bias buys and what data has to replace; attention distance against a CNN Grad-CAM; vision&ndash;language models; deletion tests.</td>
  <td><a href="../_static/companions/ViT_Attention_Companion.html" target="_blank" rel="noopener">Where is it looking? &#8599;</a><br><a href="../module1/lab4_clip_vs_traditional_cv.html">Lab 4</a></td>
</tr>
<tr>
  <td><a href="notes7-evaluation.html"><strong>2.7 Does it earn its keep?</strong></a><br><em>Sept 17</em></td>
  <td>Eight claimed encoder capabilities run against 399 real Florida crash narratives, each against the classical method it would replace; grouped splits; hallucination and grounding; latency and cost.</td>
  <td><a href="../_static/companions/Crash_Narrative_BERT_Companion.html" target="_blank" rel="noopener">Does BERT earn its keep? &#8599;</a></td>
</tr>
<tr>
  <td><a href="notes8-labs.html"><strong>Practice, exercises, and further reading</strong></a><br><em>Sept 17</em></td>
  <td>What the cross-attention lab proves; the Module 1 bridge lab; the three questions this module arms you with; where transformers go in Modules 3 and 4.</td>
  <td>Cross-attention sanity check, <a href="../module1/lab4_clip_vs_traditional_cv.html">Lab 4</a></td>
</tr>
</tbody>
</table>
</div>

Start with {doc}`2.1 Tokens: the unit a model actually reads <notes1-tokens>`.

## Learning objectives

By the end of this module you will be able to:

- Explain self-attention and multi-head attention as learned routing over a sequence, and why
  it displaced recurrence for long-range dependencies.
- Distinguish encoder-only, decoder-only, and encoder–decoder architectures, and identify
  which mobility tasks each suits.
- Describe how a vision transformer tokenizes an image, and how vision-language models align
  visual and textual representations.
- Apply a pretrained LLM or VLM to a mobility task — incident description, scene
  summarization, document extraction — and characterize where it fails.
- Evaluate a claim about foundation models in transportation: what was actually measured, on
  what data, against what baseline.

## Topics

- Tokenization, context windows, and what a "token" costs
- Self-attention, multi-head attention, positional encoding
- Encoder-only (BERT-style), decoder-only (GPT-style), and encoder–decoder designs
- Pretraining, scaling behavior, and what "emergent" does and doesn't mean
- Vision transformers: images as sequences of patches
- Vision-language models: contrastive alignment, captioning, visual question answering
- Multimodal foundation models applied to driving scenes and roadway imagery
- Hallucination, grounding, and why fluent output is not evidence of correctness
- Latency, cost, and deployment constraints for transformer inference

## Video lectures

*To be populated.* See the course [YouTube channel](https://www.youtube.com/@hao6247).

## Recommended readings

- Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, Ł., & Polosukhin, I. (2017). Attention is all you need. *NeurIPS*.
- Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of deep bidirectional transformers for language understanding. *NAACL-HLT*.
- Brown, T., et al. (2020). Language models are few-shot learners. *NeurIPS*. *(GPT-3.)*
- Dosovitskiy, A., et al. (2021). An image is worth 16×16 words: Transformers for image recognition at scale. *ICLR*. *(Vision Transformer.)*
- Radford, A., et al. (2021). Learning transferable visual models from natural language supervision. *ICML*. *(CLIP — introduced in Module 1, Lab 4.)*
- Alayrac, J.-B., et al. (2022). Flamingo: A visual language model for few-shot learning. *NeurIPS*.

## Labs

Full descriptions, setup notes, and every lab in the course are on the
{doc}`All Labs <../labs>` page. What each one *proves* is on
{doc}`Practice, exercises, and further reading <notes8-labs>`.

| Notebook | What you build | Read alongside |
| --- | --- | --- |
| Cross-attention sanity check *(in development)* | A small cross-attention model on paired mobility data, plus the three-tier check on whether the expected pattern actually emerges | 2.3, 2.4 |
| {doc}`Lab 4 — CLIP vs. traditional computer vision <../module1/lab4_clip_vs_traditional_cv>` | Zero-shot recognition of open-world mobility scenes | 2.5 |

Lab 4 physically lives in Module 1 and is the bridge into this module. If you skipped it, run
it first.

## Interactive companions

Seven interactive companions support the Sept 17 session. Each is embedded in the section it
belongs to and is also linked here.

- <a href="../_static/companions/Tokenization_Companion.html" target="_blank" rel="noopener">Tokens: the unit a language model actually reads</a> &mdash; embedded in <a href="notes1-tokens.html">2.1 Tokens</a>
- <a href="../_static/companions/Word2Vec_to_BERT_Companion.html" target="_blank" rel="noopener">From word2vec to BERT: what a contextual vector buys you</a> &mdash; embedded in <a href="notes2-contextual.html">2.2 From static to contextual vectors</a>
- <a href="../_static/companions/Attention_Query_Companion.html" target="_blank" rel="noopener">Attention depends on which word is asking</a> &mdash; embedded in <a href="notes3-attention.html">2.3 Attention: the mechanism</a>
- <a href="../_static/companions/GPT_From_Scratch_Companion.html" target="_blank" rel="noopener">A GPT you can read: every step, on a model trained here</a> &mdash; embedded in <a href="notes4-gpt.html">2.4 Building one</a>
- <a href="../_static/companions/Transformer_As_Architecture_Companion.html" target="_blank" rel="noopener">Your own tokens: the transformer as a research architecture</a> &mdash; embedded in <a href="notes5-architecture.html">2.5 The transformer as a research architecture</a>
- <a href="../_static/companions/ViT_Attention_Companion.html" target="_blank" rel="noopener">Where is it looking? Attention in a Vision Transformer</a> &mdash; embedded in <a href="notes6-vision.html">2.6 Transformers that see</a>
- <a href="../_static/companions/Crash_Narrative_BERT_Companion.html" target="_blank" rel="noopener">Does BERT earn its keep on crash narratives?</a> &mdash; embedded in <a href="notes7-evaluation.html">2.7 Does it earn its keep?</a>

The crash-narrative companion uses long-form narratives from real Florida crash reports. The
narratives are de-identified before any model sees them, and no report is republished as a
file.
