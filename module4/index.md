# Module 4 — Deep Generative Models: VAE, Diffusion, and World Models

*Part I, AI Foundations Through a Transportation Lens. The class schedule is on the {doc}`../syllabus` page.*

## Session topics

- **Why generate:** what changes when a model produces data, and the first answer, one cell at a time (4.1&ndash;4.2)
- **Hidden causes:** Gaussians and their mixtures (warm-up), one hidden cause behind a detector&rsquo;s speeds, and
  latent variables in general (4.3&ndash;4.4)
- **Autoencoders:** from PCA worked by hand to deep, sparse, denoising and masked autoencoders (4.5&ndash;4.7)
- **The VAE and the GAN:** the second and third answers, and a first scorecard (4.8&ndash;4.9)
- **Diffusion:** the basics, unCLIP, diffusion in the transportation literature, and knowledge-guided generation
  (4.10&ndash;4.13); world models follow

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
module builds from that idea: one hidden label first (mixture models), then latent variables in general,
autoencoders, the VAE, the GAN and diffusion, and then diffusion in practice. It closes with world models — the
attempt to learn a simulator rather than write one.

## The module, page by page

:::{admonition} How to read this module
:class: tip
Read the pages in order; each builds on the one before. The module has five parts, and each page opens with a card
naming its part.

- **Why generate (4.1&ndash;4.2)** sets up the question and gives the first answer: one cell at a time.
- **Hidden causes (4.3&ndash;4.4)** starts with one hidden label, the traffic regime behind a detector&rsquo;s
  speeds, and grows it into the general idea of a latent variable. If multivariate Gaussians are rusty, read the
  warm-up page first: it uses the same I-405 detector as 4.3.
- **Autoencoders (4.5&ndash;4.7)** builds the plain autoencoder, from PCA worked by hand to masked autoencoders.
- **The VAE and the GAN (4.8&ndash;4.9)** are the second and third answers, scored side by side.
- **Diffusion (4.10&ndash;4.13)** is the fourth answer. 4.10 builds it from Bishop&rsquo;s math. 4.11 shows how
  unCLIP gives the decoder a condition, 4.12 how transportation papers use diffusion for safety scenarios, and 4.13
  where your own engineering knowledge can steer it.

World models come next. The {doc}`closing page <notes10-reading-library>` holds a reading library of 34 papers on
generative models in transportation.

Most results on these pages come from one dataset, the 4,000 cell-transmission-model speed heatmaps that the VAE lab
is built on, split the same way everywhere, so the four answers to "how do you draw a realistic traffic state?" can
be compared directly. Section 4.3 adds one real PeMS detector; 4.5 adds two real PeMS detectors on I-405, small
enough to work by hand; 4.6 and 4.7 add a synthetic fundamental diagram; 4.8 adds real daily flow curves from 170
PeMS District 8 stations and a second simulator, a grid network; 4.10 returns to the I-405 pair of 4.5; 4.11 uses the
course crash reports; 4.12 a synthetic left-turn world; and 4.13 the heatmaps again, seen through four detectors. If
you read only one page before class, read {doc}`4.1 <notes1-producing>`: the joint-versus-marginals figure is the
idea the rest builds on.
:::

<div class="practice-table-wrap">
<table class="practice-table notes-map">
<thead>
<tr><th style="width:30%">Page</th><th style="width:48%">What it covers</th><th style="width:22%">Labs</th></tr>
</thead>
<tbody>
<tr>
  <td><a href="notes1-producing.html"><strong>4.1 From predicting to producing</strong></a><br><em>Why generate</em></td>
  <td>Four requests that need new data rather than a label; p(y | x) versus p(x); why a realistic traffic state is a matter of the <em>joint</em> distribution; the four answers.</td>
  <td>&mdash;</td>
</tr>
<tr>
  <td><a href="notes2-autoregressive.html"><strong>4.2 One cell at a time</strong></a><br><em>Why generate</em></td>
  <td>The first answer. The chain rule; next-cell prediction over 25 speed bins; why the training loss is the likelihood; bits per cell against a CTM-shaped baseline; where the model is uncertain.</td>
  <td>&mdash;</td>
</tr>
<tr>
  <td><a href="notes2a-gaussians.html"><strong>Before 4.3: Gaussians and their mixtures</strong></a><br><em>Warm-up, read before 4.3 and the VAE</em></td>
  <td>One bell in one, two and three dimensions; every Gaussian as a reshaped round one; slicing, squashing and fitting a bell; why one bell fails over a whole day and what a mixture of bells does instead; where each idea returns in the VAE and diffusion (interactive companion).</td>
  <td>&mdash;</td>
</tr>
<tr>
  <td><a href="notes5-hidden-cause.html"><strong>4.3 One hidden cause: mixture models</strong></a><br><em>Hidden causes</em></td>
  <td>One detector&rsquo;s speeds as two hidden regimes; the two-step recipe; the soft guess; fitting without labels (EM); the same idea on the heatmaps and where one hidden label breaks; mixture, VAE and diffusion as three choices of hidden cause.</td>
  <td>&mdash;</td>
</tr>
<tr>
  <td><a href="notes2b-latent-variables.html"><strong>4.4 Latent variables: hidden causes, not hidden layers</strong></a><br><em>Hidden causes</em></td>
  <td>A latent representation (BERT, ViT) against a latent variable; the two-step story and the latent variables you already use; PCA becomes probabilistic PCA; finding hidden causes without labels, and which can be found; learning their distribution; generating and steering.</td>
  <td><a href="../labs.html">VAE on traffic heatmaps</a></td>
</tr>
<tr>
  <td><a href="notes2c-autoencoders.html"><strong>4.5 Autoencoders: keep a few numbers, rebuild the rest</strong></a><br><em>Autoencoders</em></td>
  <td>Encoder, latents, decoder and the rebuild loss; a data-driven compression, not a theory-based one; PCA worked by hand on two real I-405 detectors; the linear autoencoder and why it can only find PCA; one training step by hand and in PyTorch.</td>
  <td>&mdash;</td>
</tr>
<tr>
  <td><a href="notes2d-deep-autoencoders.html"><strong>4.6 Deep autoencoders: bending the line</strong></a><br><em>Autoencoders</em></td>
  <td>Nonlinear layers that bend the line; what a manifold is; the price of depth; a synthetic fundamental diagram, and whether the one latent is density; PCA against a deep autoencoder on the heatmaps; choosing the number of latents; reusing latents for another task; inside the latent layer, from PCA to the VAE (interactive companion).</td>
  <td>&mdash;</td>
</tr>
<tr>
  <td><a href="notes2e-copying.html"><strong>4.7 Stopping the copy: sparse, denoising and masked autoencoders</strong></a><br><em>Autoencoders</em></td>
  <td>Why a good rebuild proves little; the sparse penalty; denoising against a tuned blur and the ASM, and why its arrows lead to diffusion; masked autoencoders, BERT&rsquo;s idea for heatmaps, filling detector gaps; where autoencoders break, fit card and applications.</td>
  <td><a href="../labs.html">Training the denoiser</a></td>
</tr>
<tr>
  <td><a href="notes3b-vae-basics.html"><strong>4.8 Variational autoencoders</strong></a><br><em>The VAE and the GAN</em></td>
  <td>The second answer, one step at a time: from the autoencoder to a generator; three knobs of a VAE trained on real PeMS flow curves (interactive companion); a small cloud and the reparameterization trick; the loss and where it comes from; a &beta; sweep; what the knobs learn, generating and steering; how the knobs change with the training traffic (interactive companion); where it breaks, including events missing from the training data.</td>
  <td><a href="../labs.html">VAE on traffic heatmaps</a>; <a href="lab7_four_answers.html">Lab 7: four ways to predict</a></td>
</tr>
<tr>
  <td><a href="notes4-gan.html"><strong>4.9 A forger and a critic, and a first scorecard</strong></a><br><em>The VAE and the GAN</em></td>
  <td>The third answer, one step at a time: why the loss has to be learned (squared error rewards the average, and a generator fed random numbers has no answer key); the critic and how its two losses are built; the forger and the critic trained against each other, round by round, on an I-405 detector pair; why the losses have no finish line, and how to keep the game balanced; a critic as an add-on to a reconstruction loss; precision and recall for generators; the first three answers scored on the same held-out heatmaps.</td>
  <td><a href="../labs.html">From VAE to diffusion</a></td>
</tr>
<tr>
  <td><a href="notes6-diffusion-basics.html"><strong>4.10 Diffusion models: the basics</strong></a><br><em>Diffusion</em></td>
  <td>The fourth answer, in Bishop&rsquo;s notation: a fixed encoder that adds noise; the three arrows of the diffusion picture; why the loss is &ldquo;name the noise&rdquo;; sampling from pure static, and where a prompt fits in; diffusion against the VAE on the same heatmaps; scenarios, guidance and gap filling; where it breaks.</td>
  <td><a href="../labs.html">From VAE to diffusion; Training the denoiser</a>; <a href="lab7_four_answers.html">Lab 7: four ways to predict</a></td>
</tr>
<tr>
  <td><a href="notes7-unclip.html"><strong>4.11 Reading unCLIP: from a CLIP embedding back to an image</strong></a><br><em>Diffusion</em></td>
  <td>How DALL&middot;E 2 turns a caption into a picture: CLIP as a frozen dictionary; a diffusion decoder trained to run CLIP backwards; why the way back must be a sampler, not a regression; the prior that bridges a caption to an image embedding; reading the paper&rsquo;s figure; the recipe beyond images, pair then generate the missing half, run on crash narratives and sketches (interactive companion).</td>
  <td>&mdash;</td>
</tr>
<tr>
  <td><a href="notes8-diffusion-literature.html"><strong>4.12 Diffusion in the literature: from image generators to safety scenarios</strong></a><br><em>Diffusion</em></td>
  <td>The papers that taught diffusion to make images, then the move from pictures to driving scenarios: what the models learn from, five ways to get a dangerous scenario out, the key safety papers and their figures, a worked example at one intersection, from scenario to sensor data, and how to judge a generated scenario (interactive companion: 35 papers).</td>
  <td>&mdash;</td>
</tr>
<tr>
  <td><a href="notes9-knowledge-guided.html"><strong>4.13 How transportation knowledge guides diffusion</strong></a><br><em>Diffusion</em></td>
  <td>Five doors where engineering knowledge can enter: what you generate, the condition, guidance while sampling, values held fixed, and checks on the samples; what each door asks of your data; a worked test that fills a road from four loop detectors; how to show the knowledge helped (interactive companion).</td>
  <td>&mdash;</td>
</tr>
<tr>
  <td><strong>Coming: 4.14 World models</strong></td>
  <td>Learning the simulator instead of writing it: learned dynamics and imagined rollouts, and how to judge one against a calibrated conventional model.</td>
  <td>&mdash;</td>
</tr>
<tr>
  <td><a href="notes10-reading-library.html"><strong>Further reading: generative models in transportation</strong></a><br><em>Closing page</em></td>
  <td>A reading library of 34 papers grouped by eight transportation problems, each with its key figure and the same five questions: what it generates, from what, with which model, how it is steered, and what it is used for (interactive companion).</td>
  <td>&mdash;</td>
</tr>
</tbody>
</table>
</div>

## Learning objectives

By the end of this module you will be able to:

- Explain latent-variable modeling as a learned generalization of macroscopic state reduction.
- Work PCA by hand as the simplest autoencoder, train a two-layer autoencoder one step at a time, and explain why it
  can only find PCA.
- Explain what depth buys an autoencoder (a curved manifold) and what it costs, choose the number of latents on
  validation data, and explain why a latent is not a physical variable.
- Explain the copying trap and the three ways out (sparse, denoising and masked autoencoders), and judge a learned
  gap filler against a classical baseline such as adaptive smoothing.
- Fit a two-regime mixture to detector speeds, and explain the soft guess and how EM fits it without labels.
- Tell a latent representation (BERT, ViT) from a latent variable, and explain how a latent-variable model
  finds its hidden causes, learns their distribution, and uses it to generate.
- Describe the VAE — encoder, decoder, reconstruction loss, and the KL term — and interpret
  the structure of a latent space fitted to real traffic states.
- Contrast GAN and diffusion training dynamics, and explain why diffusion largely displaced
  GANs for high-fidelity generation.
- Explain forward and reverse diffusion, and state precisely what the denoising network is
  trained to predict.
- Explain how unCLIP turns a caption into an image (pairing, decoder, prior), and apply the same pair-then-generate
  recipe to two kinds of transportation data, such as crash narratives and sketches.
- Read a diffusion paper with six questions (what is noised, what the network reads, which network, how it is
  trained, how it samples, how it is steered), and judge a generated safety scenario.
- Name where transportation knowledge can enter a diffusion model, what each entry point needs from the data, and
  how to show that the knowledge helped.
- Describe what a world model is, and what "learning the simulator" would require for traffic.
- Assess a mobility world-model application — scenario generation, driving-video prediction,
  learned simulation — against what a calibrated conventional model already gives you.
- Evaluate a synthetic-data claim: does the generated data improve a downstream task relative
  to a classical generator or simple augmentation?

## Topics

- What changes when a model produces data: the joint distribution, and how to score a generator
- Autoregressive generation: the chain rule and next-cell prediction
- Mixture models: one hidden cause, the soft guess, and EM
- Latent variables, manifolds, and dimensionality reduction
- Autoencoders: PCA as the linear autoencoder, deep autoencoders and manifolds, choosing the number of latents
- Stopping the copy: sparse, denoising and masked autoencoders; filling detector gaps
- Variational autoencoders; the ELBO (referenced, not re-derived)
- Reading a latent space: structure, interpolation, and fragmentation
- Generative adversarial networks; mode collapse and training instability
- Forward and reverse diffusion; denoising diffusion probabilistic models
- What the denoiser actually learns, and why the conditional mean explains the blur
- Latent diffusion and conditional generation; unCLIP and the pair-then-generate recipe
- Diffusion for safety-critical driving scenarios: guidance, head starts, filling in, conditions and selection
- Transportation knowledge in diffusion: representation, conditions, cost guidance, hard limits and checks
- World models: learned dynamics, imagination-based rollout
- Synthetic data for rare events — and how to tell whether it helped
- Evaluating generative models when there's no ground-truth label

## Video lectures

*To be populated.* See the course [YouTube channel](https://www.youtube.com/@hao6247).

## Recommended readings

- Tipping, M. E., & Bishop, C. M. (1999). Probabilistic principal component analysis. *Journal of the Royal Statistical Society: Series B*, 61(3), 611–622.
- Bishop, C. M., & Bishop, H. (2024). *Deep Learning: Foundations and Concepts*. Springer. Chapter 19, sections 19.1.1&ndash;19.1.5 (autoencoders).
- Vincent, P., Larochelle, H., Bengio, Y., & Manzagol, P.-A. (2008). Extracting and composing robust features with denoising autoencoders. *ICML*.
- He, K., Chen, X., Xie, S., Li, Y., Dollár, P., & Girshick, R. (2022). Masked autoencoders are scalable vision learners. *CVPR*.
- Kingma, D. P., & Welling, M. (2014). Auto-encoding variational Bayes. *ICLR*.
- Goodfellow, I., et al. (2014). Generative adversarial nets. *NeurIPS*.
- Ho, J., Jain, A., & Abbeel, P. (2020). Denoising diffusion probabilistic models. *NeurIPS*.
- Ho, J., & Salimans, T. (2021). Classifier-free diffusion guidance. *NeurIPS Workshop on Deep Generative Models and Downstream Applications*.
- Ramesh, A., Dhariwal, P., Nichol, A., Chu, C., & Chen, M. (2022). Hierarchical text-conditional image generation with CLIP latents. *arXiv:2204.06125*. *(unCLIP, DALL&middot;E 2.)*
- Zhong, Z., et al. (2023). Guided conditional diffusion for controllable traffic simulation. *ICRA*. *(CTG.)*
- Rombach, R., Blattmann, A., Lorenz, D., Esser, P., & Ommer, B. (2022). High-resolution image synthesis with latent diffusion models. *CVPR*.
- Ha, D., & Schmidhuber, J. (2018). World models. *NeurIPS*.
- Hafner, D., Lillicrap, T., Ba, J., & Norouzi, M. (2020). Dream to control: Learning behaviors by latent imagination. *ICLR*. *(Dreamer.)*

## Labs

- **{doc}`Lab 7 — Four ways to predict the next 5 seconds <lab7_four_answers>`** (available). Train regression,
  a conditional VAE, a word-by-word translator and diffusion on the same 20,000 simulated intersection trajectories,
  with the same encoder and the same training budget, and score them against a referee that knows what really could
  happen next. Squared error alone returns the average future, which leaves the pavement 22.5% of the time; diffusion
  uses the same kind of loss, plus a noisy draft of the answer, to draw futures that almost never do. Reads with 4.8
  and 4.10.

- **VAE on traffic state heatmaps.** Train an image VAE on speed heatmaps generated by a cell
  transmission model, then read the latent space — what does the model choose to encode when
  forced through a narrow bottleneck, and what does it throw away?

- **From VAE to diffusion.** Rather than asserting that diffusion is better, this lab measures
  where the VAE actually breaks on the same traffic data, then motivates the diffusion
  formulation as a response to those specific, observed failures.

- **Training the denoiser.** Build and train the denoising network in numpy, then confront the
  payoff question: what is the network really predicting at each noise level, and why does the
  conditional-mean answer explain everything you see in the samples?
