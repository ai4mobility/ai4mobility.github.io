(knowledge-ae-vae)=
# 4.12 How transportation knowledge guides AE and VAE

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 4 &middot; Section 4.12</span>
    <span class="notes-card-session">Session: Generative models in transportation</span>
  </div>
  <p class="notes-card-lede">A generated time&ndash;space heatmap makes sense to a traffic engineer only if its shockwaves do: sharp fronts, each moving at the speed the shock formula gives it. This page tests that on the course&rsquo;s CTM heatmaps, shows why a plain VAE smears the back of a queue, and tries four places where traffic flow theory can enter an autoencoder: what it generates, its decoder, its loss, and checks after sampling. It closes by asking whether a GAN&rsquo;s discriminator could learn the physics instead.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Read it before</h4>
      <ul>
      <li><a href="notes3b-vae-basics.html">4.6 Variational autoencoders (VAE)</a>, for the 2-latent heatmap VAE used here</li>
      <li><a href="notes4-gan.html">4.7 Generative Adversarial Networks (GAN)</a>, for the discriminator</li>
      <li><a href="notes9-knowledge-guided.html">4.11 How transportation knowledge guides diffusion</a>, the same question for diffusion</li>
      </ul>
    </div>
    <div>
      <h4>Interactive companion</h4>
      <ul><li><a href="../_static/companions/Traffic_Knowledge_AE_VAE_Companion.html" target="_blank" rel="noopener">How to integrate traffic domain knowledge to guide AE/VAE generation &#8599;</a>, on this page</li></ul>
    </div>
  </div>
</div>

## What this section covers

- Two tests for a physical heatmap: the band every wave stays in, and the shock formula where a speed heatmap can check it
- Why squared error turns the back of a queue into a ramp, on five live CTM runs
- Four places for traffic knowledge: what you generate, the decoder, the loss, and checks after sampling
- The same VAE trained with four losses, and a GAN built three ways
- A decoder that is the CTM itself, with the shock formula drawn on the live run
- Repair after sampling, the fit card, applications and questions

{doc}`4.11 <notes9-knowledge-guided>` asked where transportation knowledge can enter a diffusion model. This page asks
the same of the autoencoder family and the GAN, using one law you can check by eye: a shockwave must have a clear
boundary and move at the right speed. The data are the course&rsquo;s 4,000 synthetic CTM speed heatmaps, split
3,200 / 400 / 400 as everywhere in this module, and the model is the 2-latent heatmap VAE of
{doc}`4.6 <notes3b-vae-basics>`.

**After this page you should be able to:**

1. Check a generated time&ndash;space heatmap against the shock formula, and say which fronts a speed heatmap cannot check, and why.
2. Explain why squared error turns the back of a queue into a ramp.
3. Name four places traffic knowledge can enter an AE or VAE, and say which ones guarantee the physics and which only push toward it.
4. Decide whether a physics rule belongs in the generator, in the loss, in a check after sampling, or in a discriminator.

(knowledge-ae-vae-companion)=
## The interactive companion

Work through the six tabs in order. Tab 1 sets up the two tests and lets you slow the clock of a real heatmap on
purpose, to see which test notices. Tab 2 runs the CTM in your browser to show the blur. Tab 3 maps the four places,
with a live count of vehicles conserved when you generate cumulative counts N(x, t) instead of speeds. Tab 4 trains
the same VAE four ways and then swaps the rebuild loss for a discriminator. Tab 5 makes the CTM the decoder; tab 6
repairs draws and closes with the fit card.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion &mdash; How to integrate traffic domain knowledge to guide AE/VAE generation</span>
    <a href="../_static/companions/Traffic_Knowledge_AE_VAE_Companion.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/Traffic_Knowledge_AE_VAE_Companion.html"
          title="Shockwave tests for generated traffic heatmaps, four places for traffic knowledge in an autoencoder, and a GAN comparison" loading="lazy"></iframe>
</div>

(knowledge-ae-vae-results)=
## What the tests found

| Generator | Rebuild error (mph) | Front sharpness of draws (mph) | Test 1: edges flagged | Test 2: congested fronts at &minus;15 mph |
| --- | --- | --- | --- | --- |
| Real CTM test heatmaps | &mdash; | 40.0 | 8.1% | 76.2% |
| Plain VAE | 7.56 | 23.1 | 6.2% | 66.8% |
| Front-weighted loss | 7.84 | 30.9 | 7.3% | 68.9% |
| Edge-matching loss | 8.10 | 29.6 | 7.6% | 68.3% |
| Wave-speed penalty | 7.63 | 22.8 | 5.5% | 68.6% |
| Simulator decoder (the CTM) | 7.79 | 35.9 | 5.8% | 77.4% |
| GAN, the VAE&rsquo;s decoder network | &mdash; | 42.9 | 18.4% | 46.9% |
| GAN, shock map shown to the discriminator | &mdash; | 39.3 | 11.5% | 71.0% |
| GAN, convolutional generator | &mdash; | 35.3 | 9.0% | 71.1% |

400 draws per model, first training seed; the companion shows the second seed beside it. Test 1 is the share of strong
edges moving outside &minus;15 to +75 mph. Test 2 is the share of fronts with congestion on both sides that move at
&minus;15 &plusmn; 3.75 mph, as the shock formula requires on the straight congested branch of the course&rsquo;s
fundamental diagram.

- **A loose test can pass wrong physics.** Slow the clock of the real heatmaps by 1.5&times; and every front moves too
  slowly, yet test 1 flags only 1.4% of edges. Test 2 catches it: 17.5% of congested fronts at &minus;15 mph.
- **The plain VAE is right on average, but loose and blurred.** Its wave-speed penalty encoded only test 1, which the
  plain VAE rarely failed, so it changed little. Check what is broken before you add a penalty, and penalize that.
- **Building the simulator in gives the physics by construction.** The CTM decoder&rsquo;s congested fronts pass test 2
  as often as real ones, and its draws are far sharper at about the same rebuild error. Repairing plain-VAE draws to
  their nearest CTM run does the same after sampling: sharpness 23.4 &rarr; 31.6 mph, test 2 68.0% &rarr; 78.4%.
- **A discriminator buys sharpness, not physics.** It learns the shock rule only when it is shown the rule, and then
  the generator partly dodges by drawing fewer kinds of traffic. Put a rule you can write down in the generator; keep
  a discriminator for what you cannot write down.

:::{admonition} Before you trust these results
:class: warning

- *Baseline:* the same 2-latent VAE with the plain loss, same split and seed; every loss and every GAN was trained twice (seeds 0 and 1).
- *Honest split:* all models trained on the 3,200 training heatmaps; rebuild error is measured on the 400 test heatmaps, which were used for nothing else, and draws are compared with those test heatmaps.
- *Ugly cases:* the heatmaps are synthetic CTM output, so the simulator decoder has exactly the right physics; on real detector data it would miss capacity drop and stop-and-go waves. Pooling to 20 &times; 20 cells makes real heatmaps fail test 1 on 8.1% of edges and test 2 on 23.8% of congested fronts, so only clear excesses count. Heatmaps that start congested, where several waves meet, are the hard cases.
:::

The code and results are in the class folder under `genmodels/kg_companion`; its README lists where every number
comes from.

## Where to go next

- {doc}`4.11 How transportation knowledge guides diffusion <notes9-knowledge-guided>`: the same question for diffusion,
  with five doors for knowledge and what each asks of your data.
- {doc}`4.13 How transportation research uses generative models <notes10-reading-library>`: 34 papers on generative
  models in transportation, grouped by the problem they address.

---

Next: {doc}`4.13 How transportation research uses generative models <notes10-reading-library>`. Back to the
{doc}`Module 4 map <index>`.
