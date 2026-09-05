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

## Interactive companion

The first topic on that list — what a token is, and what it costs — decides whether
everything after it is affordable. Work through this companion before class. The
tokenizer inside it is the real thing: the published `o200k_base` (current OpenAI
generation) and `r50k_base` (GPT-2) merge tables, byte-level BPE, verified
piece-for-piece against OpenAI's `tiktoken`. Type your own jargon into tab 3 and see
exactly what the model receives — then find three terms from your subfield that
fragment into three or more tokens.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion — Tokens: the unit a language model actually reads</span>
    <a href="../_static/companions/Tokenization_Companion.html" target="_blank" rel="noopener">Open full screen ↗</a>
  </div>
  <iframe src="../_static/companions/Tokenization_Companion.html"
          title="Tokens: the unit a language model actually reads" loading="lazy"></iframe>
</div>

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

- **Cross-attention sanity check.** Build a small cross-attention model on paired mobility
  data and ask a question we can actually answer: *does the attention pattern we expect
  actually emerge?* The lab runs a three-tier sanity check — does the model learn the task,
  does attention concentrate where the physics says it should, and does the interpretation
  survive a control condition. The result is instructive: attention heads often behave as
  routers rather than as the tidy alignment maps that published figures suggest, which is a
  useful corrective before you read your next attention visualization.

- Module 1's **{doc}`Lab 4 — CLIP vs. traditional computer vision <../module1/lab4_clip_vs_traditional_cv>`** is the bridge into this module.
  If you skipped it, run it first — the multimodal embedding space it builds is the foundation
  for everything in the vision-language section here.
