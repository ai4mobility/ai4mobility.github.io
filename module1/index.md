# Module 1 — Foundations and Representation Learning

*Weeks 1–3 of the {doc}`../syllabus` — Aug 27, Sept 3, and Sept 10, 2026.*

## Class meetings

| Date | Session topic | Due before class |
|---|---|---|
| Aug 27 | Course introduction; overview of AI for mobility; course expectations; project overview; example project topics and datasets | — |
| Sept 3 | Neural network basics and deep learning foundations | **Project interest survey** |
| Sept 10 | Representation learning, embeddings, transfer learning, contrastive learning, and mobility representations | Preliminary project idea memo; lab preparation as assigned |

## Overview

This module establishes the foundation for the rest of the course, and it does so in three
steps.

We open by mapping out what we mean by "AI" in the mobility context, surveying where AI is
actually being used in transportation today, and setting up the group project — the topics,
the datasets, and what a finishable project looks like.

We then build the **neural network** from the ground up: a composition of linear maps and
nonlinearities, trained by gradient descent on a loss. The on-ramp here is one you already
know. The logistic sigmoid at the heart of a neural unit is the same function as the binary
logit model used in mode choice; a neural network is what you get when you stop specifying the
utility function by hand and let the data learn it. That framing also makes the honest case
for *when not* to use a network — a fixed basis expansion is cheaper and more interpretable
until the input dimension gets high enough to make it impractical.

The third step is the idea that unifies almost all modern AI systems: **embeddings**, the
practice of representing words, images, road segments, and trajectories as learned vectors.
From there we get to the three moves that make embeddings useful in practice — **transfer
learning** (reuse a representation someone else paid to train), **contrastive learning**
(train on what is similar rather than on labels), and **multimodal embeddings (CLIP)**, which
put images and natural language in one shared space and open the door to zero-shot,
open-vocabulary perception for mobility. With embeddings in hand we are ready for transformers
and large language models in Module 2.

## Learning objectives

By the end of this module you will be able to:

- Distinguish among the major AI methodologies (classical ML, deep learning, computer vision, reinforcement learning, large foundation models) and identify which mobility problems each addresses.
- Recall the supervised-learning pipeline (data → model → loss → optimization → evaluation) and apply it to a small mobility dataset.
- Describe a neural network as alternating linear maps and nonlinear activations, and explain what the activation function contributes — including why the logistic sigmoid is the binary logit model you already use.
- Explain gradient descent and backpropagation at the level of what is being computed, and diagnose the common ways training fails: saturation and vanishing gradients, bad learning rates, poor initialization, overfitting.
- State the argument for a learned basis over a fixed one — a multilayer network scales with input dimension where a fixed basis expansion does not — and identify the low-dimensional problems where that argument does not apply.
- Explain what an **embedding** is and why dense, learned vector representations replaced hand-engineered features and one-hot encodings.
- Use **Word2Vec** to train word embeddings on text, observe analogy structure, and transfer the same algorithm to a real road network to produce **road-segment embeddings (Road2Vec)**.
- Use a pretrained **CNN (ResNet-50)** to extract image embeddings and inspect how semantically similar images cluster in the resulting vector space — the basic mechanics of **transfer learning**.
- Explain **contrastive learning** as supervision by similarity rather than by label, and describe what it buys you when labels are scarce, which in transportation is most of the time.
- Contrast **closed-set image classification** with **CLIP-style multimodal learning**, perform zero-shot recognition of open-world mobility scenes (flooded roadways, work zones, scooter riders, nighttime hazards), and reason about CLIP's failure modes and prompt sensitivity.
- Read AI-mobility headlines critically — separating real capability claims from hype.

## Topics

**Week 1 — Course introduction and the AI-for-mobility landscape (Aug 27)**

- What "AI" means in a transportation context, and what it does not
- Where AI is deployed in mobility today: vehicles, roadside, agency workflows, mobility services
- Course expectations, lab logistics, hardware, and how the semester is graded
- The group project: example topics, candidate datasets, and what makes a project finishable
- Reading capability claims critically: what was measured, on what data, against what baseline

**Week 2 — Neural network basics and deep learning foundations (Sept 3)**

- The supervised-learning pipeline: data → model → loss → optimization → evaluation
- From linear and logistic regression to the single neural unit
- Activation functions: sigmoid, tanh, ReLU — saturation, dynamic range, and why the choice matters
- The binary-logit on-ramp: the sigmoid you already use in mode choice, now as a network layer
- Multilayer networks; learned basis functions versus fixed basis expansions, and the parameter-count crossover
- Loss functions, gradient descent, and backpropagation
- Training in practice: initialization, learning rate, batch size, regularization, train/validation splits
- Underfitting, overfitting, and honest evaluation on mobility data
- Two results that argue *against* reaching for a network, and when they apply

**Week 3 — Representation learning and embeddings (Sept 10)**

- Hand-engineered features, one-hot encodings, and their limits
- Embeddings as dense learned vectors; distance and similarity in embedding space
- Word2Vec: skip-gram, negative sampling, and analogy structure
- Road2Vec: the same algorithm on random walks over a road network
- Image embeddings from a deep CNN; what different layers represent
- Transfer learning: pretrained encoders, feature extraction versus fine-tuning, and domain shift
- Contrastive learning: positives, negatives, and supervision without labels
- Multimodal embeddings and CLIP; zero-shot, open-vocabulary recognition
- Mobility representations: what should be embedded — segments, trajectories, OD pairs, scenes
- Visualizing and sanity-checking an embedding space before you trust it

## Contents

```{tableofcontents}
```

## Video lectures

| Lecture | Topic | Video |
|---|---|---|
| 1 | Course Overview + How AI Represents Words and Images (Embeddings) | [Watch on YouTube](https://www.youtube.com/@hao6247) |
| 2 *(next)* | Transformers and Large Language Models | *forthcoming* |

*(Replace with direct video links as each lecture is recorded.)*

## Recommended readings

- LeCun, Y., Bengio, Y., & Hinton, G. (2015). Deep learning. *Nature, 521*, 436–444.
- Bishop, C. M., & Bishop, H. (2024). *Deep Learning: Foundations and Concepts*, Ch. 6 (Deep Neural Networks). *(The learned-versus-fixed basis argument used in Week 2.)*
- Rumelhart, D. E., Hinton, G. E., & Williams, R. J. (1986). Learning representations by back-propagating errors. *Nature, 323*, 533–536.
- Mikolov, T., Chen, K., Corrado, G., & Dean, J. (2013). Efficient estimation of word representations in vector space. *arXiv:1301.3781*.
- He, K., Zhang, X., Ren, S., & Sun, J. (2016). Deep residual learning for image recognition. *CVPR*. *(ResNet — the image encoder used in Lab 3.)*
- Radford, A., Kim, J. W., Hallacy, C., Ramesh, A., Goh, G., Agarwal, S., … & Sutskever, I. (2021). Learning transferable visual models from natural language supervision (CLIP). *Proceedings of ICML*. *(The multimodal image–text model used in Lab 4.)*
- Veres, M., & Moussa, M. (2020). Deep learning for intelligent transportation systems: A survey of emerging trends. *IEEE Transactions on Intelligent Transportation Systems, 21*(8), 3152–3168.
- Karlaftis, M. G., & Vlahogianni, E. I. (2011). Statistical methods versus neural networks in transportation research. *Transportation Research Part C, 19*(3), 387–399.

## Labs

Four hands-on Jupyter notebooks accompany this module. All are runnable in Google Colab and use only open data.

- **{doc}`lab1` — Python + ML warmup.** Loads a synthetic traffic-flow dataset, visualizes the Greenshields fundamental diagram (speed vs density), and fits a simple model. The goal is to verify your environment and recall the supervised-learning pipeline before we dive into representation learning.
- **{doc}`lab2_word_embeddings` — From Word2Vec to Road2Vec.** Train word embeddings on a small text corpus, reproduce the `king − man + woman ≈ queen` analogy, then apply the *identical* Word2Vec machinery to random walks on a real road network around USF Tampa. You'll see that learned road-segment embeddings recover functional classification (arterial vs. local vs. highway) without ever being told the labels.
- **{doc}`lab3_image_embeddings` — Image embeddings with a deep CNN.** Load a pretrained ResNet-50, visualize feature maps across layers (edges → textures → parts → objects), extract 2048-dimensional embeddings for a handful of test images, and verify that semantically similar images (e.g., two stop signs) cluster in the embedding space. This is transfer learning in its simplest useful form: you are reusing a representation you did not pay to train.
- **{doc}`lab4_clip_vs_traditional_cv` — CLIP vs. traditional computer vision for mobility AI.** Compare a closed-set image classifier with a CLIP-style multimodal model on real roadway and dashcam-style scenes. Run zero-shot recognition against open-vocabulary prompts ("a flooded roadway", "a construction work zone", "a pedestrian crossing at night"), visualize image–text similarity in the shared embedding space, experiment with prompt engineering, and probe CLIP's failure cases. The lab closes with a discussion of mobility AI implications — why multimodal foundation models matter for long-tail safety scenarios that don't fit neatly into ImageNet-style label sets.

Two short interactive companions support the Week 2 session and are posted on Canvas: one
walks the sigmoid and tanh activations from the binary-logit starting point, the other works
through the learned-versus-fixed basis comparison and the point where a multilayer network
becomes the cheaper option.
