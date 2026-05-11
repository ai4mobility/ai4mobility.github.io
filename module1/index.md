# Module 1 — Foundations of AI for Mobility

## Overview

This module establishes the foundation for the rest of the course. We map out what we mean by "AI" in the mobility context, survey where AI is being used in transportation today, refresh the core machine-learning pipeline, and — most importantly — introduce the single idea that unifies almost all modern AI systems: **embeddings**, the practice of representing words, images, road segments, and trajectories as learned vectors of numbers. With embeddings in hand we will be ready to take on transformers and large language models in Module 2.

## Learning objectives

By the end of this module you will be able to:

- Distinguish among the major AI methodologies (classical ML, deep learning, computer vision, reinforcement learning, large foundation models) and identify which mobility problems each addresses.
- Recall the supervised-learning pipeline (data → model → loss → optimization → evaluation) and apply it to a small mobility dataset.
- Explain what an **embedding** is and why dense, learned vector representations replaced hand-engineered features and one-hot encodings.
- Use **Word2Vec** to train word embeddings on text, observe analogy structure, and transfer the same algorithm to a real road network to produce **road-segment embeddings (Road2Vec)**.
- Use a pretrained **CNN (ResNet-50)** to extract image embeddings and inspect how semantically similar images cluster in the resulting vector space.
- Read AI-mobility headlines critically — separating real capability claims from hype.

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
- Mikolov, T., Chen, K., Corrado, G., & Dean, J. (2013). Efficient estimation of word representations in vector space. *arXiv:1301.3781*.
- He, K., Zhang, X., Ren, S., & Sun, J. (2016). Deep residual learning for image recognition. *CVPR*. *(ResNet — the image encoder used in Lab 3.)*
- Veres, M., & Moussa, M. (2020). Deep learning for intelligent transportation systems: A survey of emerging trends. *IEEE Transactions on Intelligent Transportation Systems, 21*(8), 3152–3168.
- Karlaftis, M. G., & Vlahogianni, E. I. (2011). Statistical methods versus neural networks in transportation research. *Transportation Research Part C, 19*(3), 387–399.

## Labs

Three hands-on Jupyter notebooks accompany this module. All are runnable in Google Colab and use only open data.

- **{doc}`lab1` — Python + ML warmup.** Loads a synthetic traffic-flow dataset, visualizes the Greenshields fundamental diagram (speed vs density), and fits a simple model. The goal is to verify your environment and recall the supervised-learning pipeline before we dive into representation learning.
- **{doc}`lab2_word_embeddings` — From Word2Vec to Road2Vec.** Train word embeddings on a small text corpus, reproduce the `king − man + woman ≈ queen` analogy, then apply the *identical* Word2Vec machinery to random walks on a real road network around USF Tampa. You'll see that learned road-segment embeddings recover functional classification (arterial vs. local vs. highway) without ever being told the labels.
- **{doc}`lab3_image_embeddings` — Image embeddings with a deep CNN.** Load a pretrained ResNet-50, visualize feature maps across layers (edges → textures → parts → objects), extract 2048-dimensional embeddings for a handful of test images, and verify that semantically similar images (e.g., two stop signs) cluster in the embedding space.
