# Module 3 — Generative AI and World Models

*Generative models open on Oct 22. See the {doc}`../syllabus`. Graph neural networks, taught the week before, are now the last section of Module 2: {doc}`2.14 <../module2/notes15-gnn>`.*

## Class meetings

| Date | Session topic | Due before class |
|---|---|---|
| Oct 22 | Generative models, part 1: what changes when a model produces data; autoregressive generation, latent variables, VAE, GAN, and a first scorecard (3.1&ndash;3.5) | **Rotating project progress report: Team 4** |

## Overview

Everything so far has been discriminative: given data, predict a label or a value. Generative
models ask the harder question — what does the *distribution* of plausible traffic states look
like, and can we sample new ones from it?

This matters in transportation for an unglamorous reason: the situations we most need to plan
for are the ones we have the least data on. Crashes, evacuations, sensor failures, and unusual
demand patterns are rare by definition. Generative models offer a way to reason about, and
sometimes synthesize, the tail.

The transportation on-ramp here is **macroscopic state reduction**. You already accept that a
whole corridor's behavior can be summarized by a handful of numbers — density, flow, speed.
A latent-variable model does the same thing, except it learns which few numbers to keep. This
module builds from that idea through VAEs, GANs, and diffusion, and closes with world
models — the attempt to learn a simulator rather than write one.

## The module, page by page

:::{admonition} How to read this module
:class: tip
Sections 3.1&ndash;3.5 pair with the Oct 22 meeting; skim before, read properly after. Section 3.6
opens the VAE-and-diffusion session; diffusion and world models follow. Each page opens with a card naming its session.

Every result on these pages comes from one dataset, the 4,000 cell-transmission-model speed heatmaps
that the VAE lab is built on, split the same way everywhere, so the four answers to "how do you draw a
realistic traffic state?" can be compared directly. Section 3.6 adds one real PeMS detector. If you read only one page before class, read
{doc}`3.1 <notes1-producing>`: the joint-versus-marginals figure is the idea the rest builds on.
:::

<div class="practice-table-wrap">
<table class="practice-table notes-map">
<thead>
<tr><th style="width:30%">Page</th><th style="width:48%">What it covers</th><th style="width:22%">Labs</th></tr>
</thead>
<tbody>
<tr>
  <td><a href="notes1-producing.html"><strong>3.1 From predicting to producing</strong></a><br><em>Oct 22</em></td>
  <td>Four requests that need new data rather than a label; p(y | x) versus p(x); why a realistic traffic state is a matter of the <em>joint</em> distribution; the four answers.</td>
  <td>&mdash;</td>
</tr>
<tr>
  <td><a href="notes2-autoregressive.html"><strong>3.2 One cell at a time</strong></a><br><em>Oct 22</em></td>
  <td>The chain rule; next-cell prediction over 25 speed bins; why the training loss is the likelihood; bits per cell against a CTM-shaped baseline; where the model is uncertain.</td>
  <td>&mdash;</td>
</tr>
<tr>
  <td><a href="notes2b-latent-variables.html"><strong>3.3 Latent variables: hidden causes, not hidden layers</strong></a><br><em>Oct 22</em></td>
  <td>A latent representation (BERT, ViT) against a latent variable; the two-step story and the latent variables you already use; PCA becomes probabilistic PCA; finding hidden causes without labels, and which can be found; learning their distribution; generating and steering.</td>
  <td><a href="../labs.html">VAE on traffic heatmaps</a></td>
</tr>
<tr>
  <td><a href="notes3-vae.html"><strong>3.4 A few hidden knobs: the VAE</strong></a><br><em>Oct 22</em></td>
  <td>Macroscopic state reduction, learned; encoder, decoder and the two-term loss; the knobs it rediscovers; why it blurs, measured; VAE against PCA.</td>
  <td><a href="../labs.html">VAE on traffic heatmaps</a></td>
</tr>
<tr>
  <td><a href="notes4-gan.html"><strong>3.5 A forger, a critic, and a first scorecard</strong></a><br><em>Oct 22</em></td>
  <td>The two-player game; precision and recall for generators; how much a GAN wanders between runs; the first three answers scored on the same held-out heatmaps.</td>
  <td><a href="../labs.html">From VAE to diffusion</a></td>
</tr>
<tr>
  <td><a href="notes5-hidden-cause.html"><strong>3.6 One hidden cause: mixture models</strong></a><br><em>VAE and diffusion session</em></td>
  <td>One detector&rsquo;s speeds as two hidden regimes; the two-step recipe; the soft guess; fitting without labels (EM); the same idea on the heatmaps and where it breaks; mixture, VAE and diffusion as three choices of hidden cause.</td>
  <td>&mdash;</td>
</tr>
</tbody>
</table>
</div>

## Learning objectives

By the end of this module you will be able to:

- Explain latent-variable modeling as a learned generalization of macroscopic state reduction.
- Tell a latent representation (BERT, ViT) from a latent variable, and explain how a latent-variable model
  finds its hidden causes, learns their distribution, and uses it to generate.
- Describe the VAE — encoder, decoder, reconstruction loss, and the KL term — and interpret
  the structure of a latent space fitted to real traffic states.
- Contrast GAN and diffusion training dynamics, and explain why diffusion largely displaced
  GANs for high-fidelity generation.
- Explain forward and reverse diffusion, and state precisely what the denoising network is
  trained to predict.
- Describe what a world model is, and what "learning the simulator" would require for traffic.
- Assess a mobility world-model application — scenario generation, driving-video prediction,
  learned simulation — against what a calibrated conventional model already gives you.
- Evaluate a synthetic-data claim: does the generated data improve a downstream task relative
  to a classical generator or simple augmentation?

## Topics

- What changes when a model produces data: the joint distribution, and how to score a generator
- Autoregressive generation: the chain rule and next-cell prediction
- Latent variables, manifolds, and dimensionality reduction
- Autoencoders → variational autoencoders; the ELBO (referenced, not re-derived)
- Reading a latent space: structure, interpolation, and fragmentation
- Generative adversarial networks; mode collapse and training instability
- Forward and reverse diffusion; denoising diffusion probabilistic models
- What the denoiser actually learns, and why the conditional mean explains the blur
- Latent diffusion and conditional generation
- World models: learned dynamics, imagination-based rollout
- Synthetic data for rare events — and how to tell whether it helped
- Evaluating generative models when there's no ground-truth label

## Video lectures

*To be populated.* See the course [YouTube channel](https://www.youtube.com/@hao6247).

## Recommended readings

- Tipping, M. E., & Bishop, C. M. (1999). Probabilistic principal component analysis. *Journal of the Royal Statistical Society: Series B*, 61(3), 611–622.
- Kingma, D. P., & Welling, M. (2014). Auto-encoding variational Bayes. *ICLR*.
- Goodfellow, I., et al. (2014). Generative adversarial nets. *NeurIPS*.
- Ho, J., Jain, A., & Abbeel, P. (2020). Denoising diffusion probabilistic models. *NeurIPS*.
- Rombach, R., Blattmann, A., Lorenz, D., Esser, P., & Ommer, B. (2022). High-resolution image synthesis with latent diffusion models. *CVPR*.
- Ha, D., & Schmidhuber, J. (2018). World models. *NeurIPS*.
- Hafner, D., Lillicrap, T., Ba, J., & Norouzi, M. (2020). Dream to control: Learning behaviors by latent imagination. *ICLR*. *(Dreamer.)*

## Labs

- **VAE on traffic state heatmaps.** Train an image VAE on speed heatmaps generated by a cell
  transmission model, then read the latent space — what does the model choose to encode when
  forced through a narrow bottleneck, and what does it throw away?

- **From VAE to diffusion.** Rather than asserting that diffusion is better, this lab measures
  where the VAE actually breaks on the same traffic data, then motivates the diffusion
  formulation as a response to those specific, observed failures.

- **Training the denoiser.** Build and train the denoising network in numpy, then confront the
  payoff question: what is the network really predicting at each noise level, and why does the
  conditional-mean answer explain everything you see in the samples?
