# Module 2 — Transformers, LLMs, and Multimodal Models

*Sept 17, Oct 8 and Oct 15, 2026, with section 2.5 from the Sept 24 meeting. The {doc}`../syllabus` schedules this module in week 4; the vision and multimodal half ran in weeks 7 and 8.*

## Class meetings

| Date | Session topic | Due before class |
|---|---|---|
| Sept 17 | Transformers, large language models, vision-language models, and multimodal foundation models | **Confirmed project team and topic**; short assignment as assigned |
| Oct 8 | Vision transformers: patches, training, attention distance and attention maps; Swin and MobileViT | Baseline method / data acquisition plan |
| Oct 15 | ViT extensions: ConvNeXt, cross-attention and multimodal transformers, DETR's object queries, fusing traffic streams and their history | **Final project proposal** |

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

The second half points the same machinery at pixels and then at several inputs at once. A Vision
Transformer reads a camera frame as a sequence of patches; Swin, MobileViT and ConvNeXt each bring
back the locality it gave up. Cross-attention lets one sequence read another &mdash; a narrative
reading its diagram, a translated alert reading its source &mdash; and DETR turns it into learned
questions that find vehicles. The module ends at a signalized intersection, where a camera, loops,
probe-vehicle CAN and connected-vehicle messages have to be lined up in time and space, read in the
right direction, and given a memory, before any of them is worth fusing.

## The module, page by page

:::{admonition} How to read this module
:class: tip
Sections 2.1&ndash;2.4, 2.6 and 2.13 pair with the Sept 17 meeting, 2.5 with Sept 24, 2.7 and the
Swin and MobileViT parts of 2.8 with Oct 8, and the rest of 2.8 through 2.12 with Oct 15; skim before,
read properly after. Each page opens with a card naming its session and the interactive companions
embedded in it.

The companions are the same pages posted on Canvas, and they are not decoration — most of the
results argued in these sections are only convincing if you move the sliders yourself. If you
read only one before class, read {doc}`2.1 Tokens <notes1-tokens>`: what a token is decides
whether everything after it is affordable.

The sections run in the order the machine does — what goes *in* (2.1), what comes out the
other side (2.2), the mechanism in between (2.3), one whole model written out in code (2.4),
how its encoder cousin is pretrained and adapted (2.5), then the architecture pointed at your
own data (2.6) and at pixels (2.7), and how locality comes back (2.8). Then two inputs: one
sequence reading another (2.9), questions that are learned rather than written (2.10), every
sensor at an intersection (2.11) and their history (2.12). The module ends on the question of
whether any of it beats the method it would replace (2.13).
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
  <td><a href="notes5-bert.html"><strong>2.5 BERT: pretrain on text nobody labelled, then adapt</strong></a><br><em>Sept 24</em></td>
  <td>Four edits from a GPT to a BERT; three embedding tables; masked-word and next-sentence pretraining and what each really learns; why scale is what transfers; the four ways to attach a head; frozen, fine-tuned and domain-adapted, each against counting words.</td>
  <td><a href="../_static/companions/BERT_Training_Companion.html" target="_blank" rel="noopener">How BERT learns &#8599;</a><br><a href="../_static/code/bert_from_scratch.py" download>bert_from_scratch.py</a></td>
</tr>
<tr>
  <td><a href="notes6-architecture.html"><strong>2.6 The transformer as a research architecture</strong></a><br><em>Sept 17</em></td>
  <td>Encoder-only, decoder-only and encoder&ndash;decoder designs; pretraining and scaling; designing your own tokens; attention masks as a modelling choice; sizing a claim against the naive baseline.</td>
  <td><a href="../_static/companions/Transformer_As_Architecture_Companion.html" target="_blank" rel="noopener">Your own tokens &#8599;</a></td>
</tr>
<tr>
  <td><a href="notes7-vision.html"><strong>2.7 Transformers that see: the Vision Transformer</strong></a><br><em>Oct 8</em></td>
  <td>Training a ViT to classify a frame, and why its loss is a logit likelihood; blocks, heads and attention distance; what data buys against CNNs, on ImageNet and on FL511 frames; attention maps against Grad-CAM, and the deletion test.</td>
  <td><a href="../_static/companions/ViT_Attention_Companion.html" target="_blank" rel="noopener">Where is it looking? &#8599;</a><br><a href="../module4/lab6_vit_finetune.html">Lab 6</a></td>
</tr>
<tr>
  <td><a href="notes8-locality.html"><strong>2.8 Locality returns: Swin, MobileViT and ConvNeXt</strong></a><br><em>Oct 8 &amp; 15</em></td>
  <td>Where plain ViT breaks on a full-resolution camera; Swin's windows, shifts and merges; MobileViT's two hops on a phone-sized CNN; ConvNeXt as the control experiment; a camera-to-alert pipeline that uses convolution, attention and classical code.</td>
  <td><a href="../_static/companions/ViT_To_Swin_Companion.html" target="_blank" rel="noopener">From ViT to Swin &#8599;</a><br><a href="../_static/companions/MobileViT_Receptive_Field_Companion.html" target="_blank" rel="noopener">MobileViT &#8599;</a></td>
</tr>
<tr>
  <td><a href="notes9-cross-attention.html"><strong>2.9 Cross-attention: one sequence reads another</strong></a><br><em>Oct 15</em></td>
  <td>Early fusion, late fusion and cross-attention; queries from one sequence, keys and values from another; a zero-shot test on crash narratives and diagrams against OCR; the encoder&ndash;decoder with every token drawn, and how training reaches the encoder.</td>
  <td><a href="../_static/companions/Cross_Attention_Companion.html" target="_blank" rel="noopener">At the merge &#8599;</a><br><a href="../_static/companions/Cross_Attention_Architecture_Companion.html" target="_blank" rel="noopener">Encoder to decoder &#8599;</a></td>
</tr>
<tr>
  <td><a href="notes10-detr.html"><strong>2.10 DETR: learned queries that find objects</strong></a><br><em>Oct 15</em></td>
  <td>Object queries as cross-attention with learned questions; Hungarian matching as the transportation problem; NMS without NMS; where DETR breaks; designing your own queries for mobility outputs.</td>
  <td><a href="../_static/companions/DETR_Companion.html" target="_blank" rel="noopener">How DETR detects &#8599;</a></td>
</tr>
<tr>
  <td><a href="notes11-streams.html"><strong>2.11 Many streams, one intersection</strong></a><br><em>Oct 15</em></td>
  <td>A camera-plus-CAN model that writes a crash warning; what an encoder must hand over; four streams, four clocks, one map; who reads whom with masks, gates and a null token; the lane-anchor hub, sized like CTM cells; fifteen published fusion models and the recipe most of them share.</td>
  <td><a href="../_static/companions/Multimodal_Cross_Attention_Companion.html" target="_blank" rel="noopener">Camera, CAN and cross-attention &#8599;</a><br><a href="../_static/companions/Multimodal_Fusion_Papers_Companion.html" target="_blank" rel="noopener">Fifteen fusion papers &#8599;</a></td>
</tr>
<tr>
  <td><a href="notes12-history.html"><strong>2.12 Where history enters</strong></a><br><em>Oct 15</em></td>
  <td>Three places the past can enter cross-attention; the GRU as exponential smoothing with a learned dial; the temporal transformer; history as keys and values; a carried memory and a learned Kalman gain.</td>
  <td>&mdash;</td>
</tr>
<tr>
  <td><a href="notes13-evaluation.html"><strong>2.13 Does it earn its keep?</strong></a><br><em>Sept 17</em></td>
  <td>Eight claimed encoder capabilities run against 399 real Florida crash narratives, each against the classical method it would replace; grouped splits; hallucination and grounding; latency and cost.</td>
  <td><a href="../_static/companions/Crash_Narrative_BERT_Companion.html" target="_blank" rel="noopener">Does BERT earn its keep? &#8599;</a></td>
</tr>
<tr>
  <td><a href="notes14-labs.html"><strong>Practice, exercises, and further reading</strong></a><br><em>Sept 17 &ndash; Oct 15</em></td>
  <td>What the labs prove; the Module 1 bridge lab; the five questions this module arms you with; where transformers go in Modules 3, 4 and 7.</td>
  <td><a href="../module1/lab4_clip_vs_traditional_cv.html">Lab 4</a>, <a href="../module4/lab6_vit_finetune.html">Lab 6</a>, cross-attention sanity check</td>
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
- Explain why a plain vision transformer struggles with full-resolution camera frames, and how
  Swin's windowed attention and feature pyramid fix it; say when a plain ViT or a CNN is still
  the better choice.
- Apply a pretrained LLM or VLM to a mobility task — incident description, scene
  summarization, document extraction — and characterize where it fails.
- Explain how a vision transformer is trained to classify a frame, measure where it reads, and
  test an attention map or a Grad-CAM with a deletion test before trusting it.
- Explain cross-attention as one sequence querying another, and choose between early fusion, late
  fusion and cross-attention for a pair of mobility data sources.
- Design learned queries for a mobility output, as DETR does for objects: decide what one answer
  is, and whether answers need matching.
- Line up multi-rate traffic streams (video, loops, CAN, connected-vehicle messages) in time and
  space before fusing them, and choose where a model carries their history.
- Evaluate a claim about foundation models in transportation: what was actually measured, on
  what data, against what baseline.

## Topics

- Tokenization, context windows, and what a "token" costs
- Self-attention, multi-head attention, positional encoding
- Encoder-only (BERT-style), decoder-only (GPT-style), and encoder–decoder designs
- Pretraining, scaling behavior, and what "emergent" does and doesn't mean
- Vision transformers: images as sequences of patches
- Training a ViT for classification; attention distance; attention maps against Grad-CAM
- Hierarchical vision transformers (Swin) for high-resolution camera frames; CNN&ndash;transformer hybrids (MobileViT); ConvNeXt
- Cross-attention; early fusion, late fusion, and the encoder&ndash;decoder
- Object queries and set prediction (DETR)
- Fusing traffic streams: per-stream encoders, time and space alignment, masks, gates, and a lane-anchor hub
- History in multimodal models: GRU, temporal transformer, keys and values, carried memory
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
- Liu, Z., et al. (2021). Swin Transformer: Hierarchical vision transformer using shifted windows. *ICCV*.
- Radford, A., et al. (2021). Learning transferable visual models from natural language supervision. *ICML*. *(CLIP — introduced in Module 1, Lab 4.)*
- Alayrac, J.-B., et al. (2022). Flamingo: A visual language model for few-shot learning. *NeurIPS*.
- Carion, N., Massa, F., Synnaeve, G., Usunier, N., Kirillov, A., & Zagoruyko, S. (2020). End-to-end object detection with transformers. *ECCV*. *(DETR.)*
- Li, J., Li, D., Xiong, C., & Hoi, S. (2022). BLIP: Bootstrapping language-image pre-training for unified vision-language understanding and generation. *ICML*.
- Mehta, S., & Rastegari, M. (2022). MobileViT: Light-weight, general-purpose, and mobile-friendly vision transformer. *ICLR*.
- Liu, Z., Mao, H., Wu, C.-Y., Feichtenhofer, C., Darrell, T., & Xie, S. (2022). A ConvNet for the 2020s. *CVPR*. *(ConvNeXt.)*
- Bishop, C. M., & Bishop, H. (2024). *Deep Learning: Foundations and Concepts*. Springer. Chapter 12 (transformers, cross-attention, the encoder&ndash;decoder).

## Labs

Full descriptions, setup notes, and every lab in the course are on the
{doc}`All Labs <../labs>` page. What each one *proves* is on
{doc}`Practice, exercises, and further reading <notes14-labs>`.

| Notebook | What you build | Read alongside |
| --- | --- | --- |
| {doc}`Lab 4 — CLIP vs. traditional computer vision <../module1/lab4_clip_vs_traditional_cv>` | Zero-shot recognition of open-world mobility scenes with a late-fusion dual encoder | 2.7, 2.9 |
| {doc}`Lab 6 — Fine-tuning a Vision Transformer <../module4/lab6_vit_finetune>` | ViT-Tiny fine-tuned on FL511 Tampa Bay camera frames, from a frozen probe to full fine-tuning | 2.7 |
| Cross-attention sanity check *(in development)* | A small cross-attention model on paired mobility data, plus the three-tier check on whether the expected pattern actually emerges | 2.9, 2.11 |

Lab 4 physically lives in Module 1 and is the bridge into this module; if you skipped it, run
it first. Lab 6 lives in Module 4, where fine-tuning is the topic, and reads with 2.7.

## Course dataset

{doc}`Florida Hurricane Transportation Posts <../hurricane-dataset>` holds 2,425 real posts about
roads, evacuation traffic, fuel and transit during Hurricanes Helene and Milton, each with the images
its author attached. Text and pixels for the same moment, so BERT, ViT, CLIP and fusion can all be
tried on the same items. The page explains what is in it and what to watch out for; the files
themselves are on Canvas for enrolled students.

## Interactive companions

Fifteen interactive companions support this module. Each is embedded in the section it belongs to and
is also linked here.

- <a href="../_static/companions/Tokenization_Companion.html" target="_blank" rel="noopener">Tokens: the unit a language model actually reads</a> &mdash; embedded in <a href="notes1-tokens.html">2.1 Tokens</a>
- <a href="../_static/companions/Word2Vec_to_BERT_Companion.html" target="_blank" rel="noopener">From word2vec to BERT: what a contextual vector buys you</a> &mdash; embedded in <a href="notes2-contextual.html">2.2 From static to contextual vectors</a>
- <a href="../_static/companions/Attention_Query_Companion.html" target="_blank" rel="noopener">Attention depends on which word is asking</a> &mdash; embedded in <a href="notes3-attention.html">2.3 Attention: the mechanism</a>
- <a href="../_static/companions/GPT_From_Scratch_Companion.html" target="_blank" rel="noopener">A GPT you can read: every step, on a model trained here</a> &mdash; embedded in <a href="notes4-gpt.html">2.4 Building one</a>
- <a href="../_static/companions/BERT_Training_Companion.html" target="_blank" rel="noopener">How BERT learns: pretrain on text nobody labelled, then adapt</a> &mdash; embedded in <a href="notes5-bert.html">2.5 BERT</a>
- <a href="../_static/companions/Transformer_As_Architecture_Companion.html" target="_blank" rel="noopener">Your own tokens: the transformer as a research architecture</a> &mdash; embedded in <a href="notes6-architecture.html">2.6 The transformer as a research architecture</a>
- <a href="../_static/companions/ViT_Attention_Companion.html" target="_blank" rel="noopener">Where is it looking? Attention in a Vision Transformer</a> &mdash; embedded in <a href="notes7-vision.html">2.7 Transformers that see</a>
- <a href="../_static/companions/ViT_To_Swin_Companion.html" target="_blank" rel="noopener">From ViT to Swin: what a 224-pixel square cannot see</a> &mdash; embedded in <a href="notes8-locality.html#vit-to-swin">2.8 Locality returns</a>
- <a href="../_static/companions/MobileViT_Receptive_Field_Companion.html" target="_blank" rel="noopener">How far can one pixel see? MobileViT's two hops</a> &mdash; embedded in <a href="notes8-locality.html#mobilevit">2.8 Locality returns</a>
- <a href="../_static/companions/Cross_Attention_Companion.html" target="_blank" rel="noopener">Cross-attention at the merge: one set of tokens asks, another answers</a> &mdash; embedded in <a href="notes9-cross-attention.html">2.9 Cross-attention</a>
- <a href="../_static/companions/Cross_Attention_Architecture_Companion.html" target="_blank" rel="noopener">One decoder position, every encoder token</a> &mdash; embedded in <a href="notes9-cross-attention.html#encoder-decoder">2.9 Cross-attention</a>
- <a href="../_static/companions/DETR_Companion.html" target="_blank" rel="noopener">How DETR detects: 100 learned questions, one answer per vehicle</a> &mdash; embedded in <a href="notes10-detr.html">2.10 DETR</a>
- <a href="../_static/companions/Multimodal_Cross_Attention_Companion.html" target="_blank" rel="noopener">Camera, CAN and cross-attention: training a model that writes a crash warning</a> &mdash; embedded in <a href="notes11-streams.html">2.11 Many streams, one intersection</a>
- <a href="../_static/companions/Multimodal_Fusion_Papers_Companion.html" target="_blank" rel="noopener">Fifteen fusion papers, and the recipe most of them share</a> &mdash; embedded in <a href="notes11-streams.html#fusion-papers">2.11 Many streams, one intersection</a>
- <a href="../_static/companions/Crash_Narrative_BERT_Companion.html" target="_blank" rel="noopener">Does BERT earn its keep on crash narratives?</a> &mdash; embedded in <a href="notes13-evaluation.html">2.13 Does it earn its keep?</a>

The crash-narrative companion uses long-form narratives from real Florida crash reports. The
narratives are de-identified before any model sees them, and no report is republished as a
file. Section 2.9's cross-attention test uses the course's de-identified release of narratives
paired with the officer's diagrams; this site reports aggregate results only, and the release
itself is on Canvas for enrolled students.
