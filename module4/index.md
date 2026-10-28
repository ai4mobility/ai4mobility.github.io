# Module 4 — Deep Generative Models: VAE, Diffusion, and World Models

*Part I, AI Foundations Through a Transportation Lens. The class schedule is on the {doc}`../syllabus` page.*

## Session topics

- **Generative models, part 1:** what changes when a model produces data; autoregressive generation, latent
  variables, VAE, GAN, and a first scorecard (4.1&ndash;4.3, 4.7&ndash;4.9)
- **Autoencoders:** from PCA worked by hand to deep, sparse, denoising and masked autoencoders (4.4&ndash;4.6)
- **VAE and diffusion:** one hidden cause, from mixture models to the VAE (4.10), then diffusion (4.11); world
  models follow

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
module builds from that idea through autoencoders, VAEs, GANs, and diffusion, and closes with world
models — the attempt to learn a simulator rather than write one.

## The module, page by page

:::{admonition} How to read this module
:class: tip
Read the pages in order; each builds on the one before. Sections 4.1&ndash;4.3 set up the question and the idea of a
hidden cause. Sections 4.4&ndash;4.6 build the plain autoencoder, from PCA worked by hand to masked autoencoders.
Sections 4.7 and 4.8 are the VAE (4.8 takes it one step at a time, with a VAE trained on real detector data), and 4.9 is
the GAN, scored side by side with it. Section 4.10 opens the VAE-and-diffusion session, and
4.11 is diffusion, built up from Bishop&rsquo;s math on the I-405 pair and the heatmaps; world models follow. Each page opens with a card naming its session. If multivariate Gaussians are
rusty, start with the warm-up page before 4.3: it revisits one bell, slicing, fitting and mixtures of bells on three
I-405 detectors, one of them the detector of 4.10.

Most results on these pages come from one dataset, the 4,000 cell-transmission-model speed heatmaps that the VAE lab
is built on, split the same way everywhere, so the four answers to "how do you draw a realistic traffic state?" can
be compared directly. Section 4.4 adds two real PeMS detectors on I-405, small enough to work by hand; 4.5 and 4.6 add
a synthetic fundamental diagram; 4.8 adds real daily flow curves from 170 PeMS District 8 stations; 4.10 adds one
real PeMS detector; 4.11 returns to the I-405 pair of 4.4. The companion in 4.5 uses the I-405 pair, the
fundamental diagram and the heatmaps; the one in 4.7 adds a second simulator, a grid network; the one in 4.8 lets you turn the three knobs of a VAE trained
on the District 8 flow curves. If you read only one
page before class, read {doc}`4.1 <notes1-producing>`: the joint-versus-marginals figure is the idea the rest builds
on.
:::

<div class="practice-table-wrap">
<table class="practice-table notes-map">
<thead>
<tr><th style="width:30%">Page</th><th style="width:48%">What it covers</th><th style="width:22%">Labs</th></tr>
</thead>
<tbody>
<tr>
  <td><a href="notes1-producing.html"><strong>4.1 From predicting to producing</strong></a><br><em>Generative models, part 1</em></td>
  <td>Four requests that need new data rather than a label; p(y | x) versus p(x); why a realistic traffic state is a matter of the <em>joint</em> distribution; the four answers.</td>
  <td>&mdash;</td>
</tr>
<tr>
  <td><a href="notes2-autoregressive.html"><strong>4.2 One cell at a time</strong></a><br><em>Generative models, part 1</em></td>
  <td>The chain rule; next-cell prediction over 25 speed bins; why the training loss is the likelihood; bits per cell against a CTM-shaped baseline; where the model is uncertain.</td>
  <td>&mdash;</td>
</tr>
<tr>
  <td><a href="notes2a-gaussians.html"><strong>Before 4.3: Gaussians and their mixtures</strong></a><br><em>Warm-up, read before 4.3 and the VAE</em></td>
  <td>One bell in one, two and three dimensions; every Gaussian as a reshaped round one; slicing, squashing and fitting a bell; why one bell fails over a whole day and what a mixture of bells does instead; where each idea returns in the VAE and diffusion (interactive companion).</td>
  <td>&mdash;</td>
</tr>
<tr>
  <td><a href="notes2b-latent-variables.html"><strong>4.3 Latent variables: hidden causes, not hidden layers</strong></a><br><em>Generative models, part 1</em></td>
  <td>A latent representation (BERT, ViT) against a latent variable; the two-step story and the latent variables you already use; PCA becomes probabilistic PCA; finding hidden causes without labels, and which can be found; learning their distribution; generating and steering.</td>
  <td><a href="../labs.html">VAE on traffic heatmaps</a></td>
</tr>
<tr>
  <td><a href="notes2c-autoencoders.html"><strong>4.4 Autoencoders: keep a few numbers, rebuild the rest</strong></a><br><em>Autoencoders</em></td>
  <td>Encoder, latents, decoder and the rebuild loss; a data-driven compression, not a theory-based one; PCA worked by hand on two real I-405 detectors; the linear autoencoder and why it can only find PCA; one training step by hand and in PyTorch.</td>
  <td>&mdash;</td>
</tr>
<tr>
  <td><a href="notes2d-deep-autoencoders.html"><strong>4.5 Deep autoencoders: bending the line</strong></a><br><em>Autoencoders</em></td>
  <td>Nonlinear layers that bend the line; what a manifold is; the price of depth; a synthetic fundamental diagram, and whether the one latent is density; PCA against a deep autoencoder on the heatmaps; choosing the number of latents; reusing latents for another task; inside the latent layer, from PCA to the VAE (interactive companion).</td>
  <td>&mdash;</td>
</tr>
<tr>
  <td><a href="notes2e-copying.html"><strong>4.6 Stopping the copy: sparse, denoising and masked autoencoders</strong></a><br><em>Autoencoders</em></td>
  <td>Why a good rebuild proves little; the sparse penalty; denoising against a tuned blur and the ASM, and why its arrows lead to diffusion; masked autoencoders, BERT's idea for heatmaps, filling detector gaps; where autoencoders break, fit card and applications.</td>
  <td><a href="../labs.html">Training the denoiser</a></td>
</tr>
<tr>
  <td><a href="notes3-vae.html"><strong>4.7 A few hidden knobs: the VAE</strong></a><br><em>Generative models, part 1</em></td>
  <td>Macroscopic state reduction, learned; encoder, decoder and the two-term loss; from the plain autoencoder to the VAE; the knobs it rediscovers; why it blurs, measured; VAE against PCA; how the knobs change with the training traffic (interactive companion).</td>
  <td><a href="../labs.html">VAE on traffic heatmaps</a></td>
</tr>
<tr>
  <td><a href="notes3b-vae-basics.html"><strong>4.8 Variational autoencoders: the basics</strong></a><br><em>Generative models, part 1</em></td>
  <td>The VAE one step at a time: from the autoencoder to a generator; three knobs of a VAE trained on real PeMS flow curves (interactive companion); a small cloud and the reparameterization trick; the loss and where it comes from; a &beta; sweep; generating and steering; where it breaks, including events missing from the training data.</td>
  <td><a href="../labs.html">VAE on traffic heatmaps</a></td>
</tr>
<tr>
  <td><a href="notes4-gan.html"><strong>4.9 A forger, a critic, and a first scorecard</strong></a><br><em>Generative models, part 1</em></td>
  <td>The two-player game; precision and recall for generators; how much a GAN wanders between runs; the first three answers scored on the same held-out heatmaps.</td>
  <td><a href="../labs.html">From VAE to diffusion</a></td>
</tr>
<tr>
  <td><a href="notes5-hidden-cause.html"><strong>4.10 One hidden cause: mixture models</strong></a><br><em>VAE and diffusion session</em></td>
  <td>One detector&rsquo;s speeds as two hidden regimes; the two-step recipe; the soft guess; fitting without labels (EM); the same idea on the heatmaps and where it breaks; mixture, VAE and diffusion as three choices of hidden cause.</td>
  <td>&mdash;</td>
</tr>
<tr>
  <td><a href="notes6-diffusion-basics.html"><strong>4.11 Diffusion models: the basics</strong></a><br><em>VAE and diffusion session</em></td>
  <td>The fourth answer, in Bishop&rsquo;s notation: a fixed encoder that adds noise; the three arrows of the diffusion picture; why the loss is &ldquo;name the noise&rdquo;; sampling from pure static, and where a prompt fits in; diffusion against the VAE on the same heatmaps; scenarios, guidance and gap filling; where it breaks.</td>
  <td><a href="../labs.html">From VAE to diffusion; Training the denoiser</a></td>
</tr>
<tr>
  <td><strong>Coming: world models</strong></td>
  <td>Learning the simulator instead of writing it: learned dynamics and imagined rollouts, and how to judge one against a calibrated conventional model.</td>
  <td>&mdash;</td>
</tr>
</tbody>
</table>
</div>

(generative-reading-library)=
## Reading library: generative models in transportation

What do researchers actually do with these models in transportation? This library answers with
34 papers, grouped by eight problems: several possible futures for road users, trip and OD data you
can share, crashes and near-misses for testing automated vehicles, rare cases in ADAS and crash data,
detector gaps, digital twins built from a few cameras, lidar generated from a camera, and storm damage
from a small dataset, plus three surveys. Each card shows the paper&rsquo;s key figure and answers the
same five questions: what it generates, from what, with which model, how the output is steered, and
what it is used for. A small diagram marks the move each paper makes: **sample** (more of the same),
**steer** (more of what you ask for), or **fill in** (complete what you saw).

Use it alongside this module. After 4.7 to 4.9, filter by **VAE** and **GAN** to see where those models
are still used; after the diffusion session, filter by **Diffusion**, the family most papers since 2023
use. Read the **Watch out** line on every card: it names the trap, such as a realism score that says
nothing about safety, or synthetic trips that are not automatically private. End at **What the papers
share**, which lists the four steps most of these papers follow.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Reading library &mdash; Thirty-four papers on generative models in transportation</span>
    <a href="../_static/companions/Generative_Models_Reading_Library.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/Generative_Models_Reading_Library.html"
          title="Thirty-four papers on generative models in transportation, and what each one generates" loading="lazy"></iframe>
</div>

(diffusion-papers-library)=
## How diffusion works in 35 transportation papers

The reading library above asks what each paper generates. This companion asks how the diffusion part works. It takes
the recipe of {doc}`4.11 <notes6-diffusion-basics>` into 35 published papers: safety-critical driving scenarios,
whole-scene simulation, motion prediction and planning, camera and lidar data for automated driving, traffic data
(detector gaps, OD flows, trips), and road-damage images. Each card shows the paper&rsquo;s architecture figure and
answers six questions in the same order: what is noised, what the network reads besides the noisy data, which network
does the denoising, how it is trained, how it samples, and how the output is steered.

Read it after 4.11, and keep one idea from that page in mind: diffusion is a way to train a network, not a network.
The same recipe runs on a transformer that denoises vehicle paths and on a U-Net that denoises camera images. Filter by
**Steering** to compare how papers push a model of normal traffic toward conflicts, or by **Denoises in** to see which
papers first compress their data. End at **How a hint reaches the model**: the five places a hint (a map, a sentence,
a cost, observed values, a draft) can enter the sampling loop, and which route fits which transportation job.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Diffusion papers &mdash; How diffusion works in thirty-five transportation papers</span>
    <a href="../_static/companions/Diffusion_Transportation_Papers_Companion.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/Diffusion_Transportation_Papers_Companion.html"
          title="How diffusion works in thirty-five transportation papers: what is noised, the network, training, sampling and steering" loading="lazy"></iframe>
</div>

(unclip-crash-run)=
## unCLIP on crash reports: a worked run

The unCLIP recipe behind DALL&middot;E 2 trains three models: a pairing between two kinds of data, a decoder that
redraws one kind from its embedding, and a prior that bridges from the other kind. This companion runs all three on the
course crash data, turning an officer&rsquo;s narrative into a 64 &times; 64 crash sketch, and reports how each step
was trained and how well it did. The full pipeline lands at chance, and the page shows why: the pairing step is the weak
link. It also walks through three problems worth knowing before you train your own conditional generator: a decoder
that ignored its condition, data that looked different at the size the model sees it, and a prior that learned no variety.

Read it after {doc}`4.11 <notes6-diffusion-basics>`. Every sketch on the page was drawn by the models; no real sketch,
narrative or personal detail from the course dataset appears. If you are enrolled, look up any crash ID in your copy of
the dataset to compare an output with the real sketch.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Worked run &mdash; unCLIP on crash reports: from a narrative to a sketch</span>
    <a href="../_static/companions/UnCLIP_Crash_Companion.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/UnCLIP_Crash_Companion.html"
          title="unCLIP on crash reports: pairing, decoder and prior trained on crash narratives and sketches, with every result" loading="lazy"></iframe>
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
- Autoencoders: PCA as the linear autoencoder, deep autoencoders and manifolds, choosing the number of latents
- Stopping the copy: sparse, denoising and masked autoencoders; filling detector gaps
- Variational autoencoders; the ELBO (referenced, not re-derived)
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
- Bishop, C. M., & Bishop, H. (2024). *Deep Learning: Foundations and Concepts*. Springer. Chapter 19, sections 19.1.1&ndash;19.1.5 (autoencoders).
- Vincent, P., Larochelle, H., Bengio, Y., & Manzagol, P.-A. (2008). Extracting and composing robust features with denoising autoencoders. *ICML*.
- He, K., Chen, X., Xie, S., Li, Y., Dollár, P., & Girshick, R. (2022). Masked autoencoders are scalable vision learners. *CVPR*.
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
