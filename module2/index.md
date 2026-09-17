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

## Interactive companions

Five companions this week. The first is about what goes *into* a transformer and
the second about what comes out the other side; the third takes the language out
altogether and asks what the architecture is good for in your own research. The
fourth opens the machine up mid-run and reads the attention weights themselves, on
road scenes, against the Grad-CAM you already built in Module 1. The fifth stops
asking how the machine works and asks whether it is worth using — on 399 real
Florida crash reports, against the classical method each task would otherwise use.

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

Module 1 left every word with one vector, for ever. The second companion is the model that
stops doing that, opened up: the wordpiece table that *is* word2vec, the twelve encoder
blocks stacked on top of it, and the fill-in-the-blank training task that forces the model
to read context in the first place. It then measures what that buys, on 42,956 real NHTSA
complaint narratives in which `light` genuinely means three different things — a dashboard
warning light, a lamp on the vehicle, and a traffic signal. Drag the layer slider on tab 4
and watch the three senses pull apart. Then settle tab 5 for yourself: three representations
are measured on the same occurrences, two of them fail, and they fail at *different* things.
Decide which one you would deploy — and say what the task would have to be for the cheaper
one to win.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion — From word2vec to BERT: what a contextual vector buys you</span>
    <a href="../_static/companions/Word2Vec_to_BERT_Companion.html" target="_blank" rel="noopener">Open full screen ↗</a>
  </div>
  <iframe src="../_static/companions/Word2Vec_to_BERT_Companion.html"
          title="From word2vec to BERT: what a contextual vector buys you" loading="lazy"></iframe>
</div>

The first two companions use a transformer the way it was built, on language. The third
takes the language out. The encoder stack does not know what a word is — it knows how to
let a set of vectors exchange information — so the three modelling decisions that matter
are yours: what is one token, what may attend to what, and what "position" means in your
problem. The page works that through on three research problems at once: network-wide
traffic prediction, multimodal car-following, and infrastructure interdependency.

Everything measured on it runs on **METR-LA** — 207 real loop detectors on Los Angeles
freeways, five-minute speeds, March to June 2012. Tab 2 is the one to spend time in: pick
a detector and compare the neighbours you would *declare* from the road network against
the ones the data actually shows, separately in the morning peak, the evening peak, and
overnight. Across all 207 detectors those two sets agree only 44% of the time, and the
measured set is only 48% stable between the two peaks — which is the argument for letting
a model compute the adjacency rather than fixing it. Then read tab 5 before you propose a
transformer for your project: the naive baselines there were computed from scratch, and the
gap between *no model* and *a model* turns out to be four times the gap between the 2018
graph model and the 2023 state of the art.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion — Your own tokens: the transformer as a research architecture</span>
    <a href="../_static/companions/Transformer_As_Architecture_Companion.html" target="_blank" rel="noopener">Open full screen ↗</a>
  </div>
  <iframe src="../_static/companions/Transformer_As_Architecture_Companion.html"
          title="Your own tokens: the transformer as a research architecture" loading="lazy"></iframe>
</div>

The first three companions treat attention as machinery you configure. The fourth reads it
as evidence. *An image is worth 16×16 words* is the paper that made the transformer a vision
architecture, and it had to prove its own case: with a CNN's built-in locality removed, does
the model actually learn to look in sensible places? The paper answers with two measurements —
how far each attention head reaches, and a picture of what the class token drew from — and both
are reproduced here on three road scenes, one of them the same Florida stop-bar frame the
convolution slides and the Grad-CAM companion use.

Spend your time in three places. **Tab 2** ships the model's real query and key vectors, so
clicking a patch computes the attention weight in front of you; switch between a head that
reaches 17.7 px and one that reaches 107.3 px in the same block, and turn off the ÷√d scaling
to watch the softmax saturate. **Tab 3** is the paper's Figure 11 on our frames, run twice: the
authors' released weights give block 1 a head with an attention distance of 0.02 px and another
at 116.2 px, while the *same architecture* trained on ImageNet-1k alone has no local head in
block 1 at all. That single table is the paper's central claim — remove a CNN's inductive bias
and data is what puts it back — and it is the reason to think hard before fine-tuning a ViT on
four thousand of your own frames from a small-data checkpoint. **Tab 5** puts the ViT's map
beside a ResNet-50 Grad-CAM on the same pixels, same classes, same score: asked about the
traffic light, the ViT lands 2.09× its fair share of heat on the five signal heads and the CNN
lands 0.56×, below what random heat would give. Before you believe any of it, run tab 6's
deletion test — where you will find that the paper's own class-free rollout is *worse* than
random for a class the model does not already favour.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion — Where is it looking? Attention in a Vision Transformer</span>
    <a href="../_static/companions/ViT_Attention_Companion.html" target="_blank" rel="noopener">Open full screen ↗</a>
  </div>
  <iframe src="../_static/companions/ViT_Attention_Companion.html"
          title="Where is it looking? Attention in a Vision Transformer" loading="lazy"></iframe>
</div>

The first four companions are about the machine. The fifth is about the decision. Eight
things people routinely claim a BERT-style encoder can do with crash reports — contextual
representations, entity extraction, relation extraction, contributing-factor identification,
classification, semantic search, clustering, extractive question answering — run one at a
time against **399 real Florida long-form crash narratives** from twenty corridors in Pasco,
Hernando and Pinellas counties, de-identified first, then joined back to the coded crash
record so every claim can be scored against a field a human already filled in. Each task is
also run with the classical method it would replace, on a five-fold split grouped by
corridor, because a random split puts crashes from the same intersection — often the same
trooper, the same template — on both sides of the line.

The results do not all go the way the diagram implies, and that is the point. **TF-IDF with
logistic regression beats every frozen-BERT probe on all four classification targets**, and a
fine-tuned DistilBERT does not close the gap either (0.488 average precision against 0.619,
for 35 minutes of training instead of under a second). Raw `bert-base` embeddings are *worse
than guessing* as a search index. The k-means clusters split on whether the trooper writes
`V01` or `V1`. And the question "what was the weather?" has a recall ceiling of 12.5% before
any model is chosen, because the officer already recorded it in a checkbox and had no reason
to write it again.

Read panel 6 with the search box open — type your own words, then click a prepared query and
compare what each one surfaces. Then bring one answer to class: **name the one task on this
page where you would actually deploy the encoder in an agency workflow, and say what number
on the page convinced you.**

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion — Does BERT earn its keep on crash narratives?</span>
    <a href="../_static/companions/Crash_Narrative_BERT_Companion.html" target="_blank" rel="noopener">Open full screen ↗</a>
  </div>
  <iframe src="../_static/companions/Crash_Narrative_BERT_Companion.html"
          title="Does BERT earn its keep on crash narratives?" loading="lazy"></iframe>
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
