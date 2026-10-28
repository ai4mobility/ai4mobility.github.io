(vae-basics)=
# 4.8 Variational autoencoders

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 4 &middot; Section 4.8</span>
    <span class="notes-card-session">Session: The VAE and the GAN</span>
  </div>
  <p class="notes-card-lede">The VAE one step at a time, with the math kept light. An autoencoder can rebuild a traffic state but cannot make a new one; a VAE fixes that with two changes, a small cloud instead of a point in the middle and one extra term in the loss. This page walks through both on the course heatmaps, turns three knobs of a VAE trained on real PeMS flow, tunes &beta;, shows how the knobs change with the traffic a VAE is trained on, and ends with where a VAE should not be trusted.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Read it before</h4>
      <ul>
      <li><a href="notes2b-latent-variables.html">4.4 Latent variables: hidden causes, not hidden layers</a></li>
      <li><a href="notes2c-autoencoders.html">4.5&ndash;4.7 Autoencoders</a></li>
      </ul>
    </div>
    <div>
      <h4>Interactive companions</h4>
      <ul>
      <li><a href="../_static/companions/VAE_Three_Knobs.html" target="_blank" rel="noopener">Three knobs of a traffic VAE &#8599;</a>, in the running-example section</li>
      <li><a href="../_static/companions/Same_VAE_Different_Traffic_Companion.html" target="_blank" rel="noopener">Same VAE, different traffic &#8599;</a>, just before Where it breaks</li>
      </ul>
    </div>
  </div>
</div>

## What this section covers

- From the autoencoder to the VAE: why a plain autoencoder cannot generate, and the VAE idea in three steps
- The running example, and three knobs of a VAE trained on real PeMS flow curves (interactive companion)
- Why a plain autoencoder's latents leave no map of where to draw, measured with two scores
- The VAE fix: a small cloud instead of a point, and the reparameterization trick
- The loss: rebuild error plus a charge for clouds that stray from the prior; where it comes from (the ELBO)
- The &beta; knob: detail against order, from a sweep of six trainings
- What the knobs learn, how to generate, and how to steer
- How the knobs change with the training traffic, and what that means for collecting data (interactive companion)
- Where it breaks: blur, knobs that are not causes, no physics, and nothing outside the training data
- Fit card, applications, a summary, a label-the-picture exercise and nine judgment questions

(vae-basics-ae-to-vae)=
## From the autoencoder to the VAE

An autoencoder can rebuild a traffic state from a few latents, but it cannot make a new one. A VAE is an autoencoder trained so that its latents follow a distribution we choose in advance. Because we know that distribution, we can draw new latents from it and decode them into new, realistic data.

```{figure} ../_static/figures/VB_AE_to_VAE.png
:alt: Three lanes. Autoencoder: a heatmap goes through the encoder to one exact point among the training latents, then through the decoder to a rebuilt heatmap; latents land wherever rebuilding is easiest, with no rule for drawing new ones. VAE training: the encoder returns a centre and a spread, a random point z = mu + sigma times epsilon from that small cloud is decoded, and a penalty keeps every cloud near the gold prior N(0, I). VAE generating: no input; draw z from the prior and run only the decoder to get a new heatmap that looks like the training data.
:width: 100%

From autoencoder to VAE: a point becomes a cloud. The course models on one test heatmap; same shape for both, 400 &rarr; 96 &rarr; 2 &rarr; 96 &rarr; 400.
```

**What you already have.** The autoencoder of {doc}`4.5–4.7 <notes2c-autoencoders>` squeezes each input x into a few latents z and rebuilds it: x → z → x̂. It is trained only to rebuild. So each x gets one exact point z, placed wherever rebuilding is easiest.

**What it cannot do.** To make a new heatmap you need new latents. The autoencoder never says where its latents live: their spread and shape are whatever training happened to produce, with empty gaps between them. Pick a z at random and you may land far from every training example, in a region the decoder never learned. The section {ref}`Why a plain autoencoder cannot generate <vae-basics-cannot-generate>` measures this.

**The VAE idea in three steps.**

1. **Choose the latent distribution before training.** This is the **prior**: a standard Gaussian, N(0, I). It is a bell curve centred at 0 with spread 1 on every knob.
2. **Map each input to a small cloud, not a point.** The encoder returns a Gaussian with centre μ and spread σ. The decoder is trained so that every point in the cloud rebuilds something close to the input.
3. **Charge clouds that stray from the prior.** A penalty in the loss keeps all the clouds near N(0, I), so together they fill it.

Generating is then two steps: draw z from N(0, I), and decode it.

:::{admonition} Key idea
:class: tip
An autoencoder learns a position for each input. A VAE learns a *distribution* for its latents. Sample z from that distribution, and the decoder returns a new example that looks as if it came from the same distribution as the training data.
:::

**Is "the autoencoder's latents are not Gaussian" the right motivation?** Mostly, with two refinements.

- You can fit a distribution to an autoencoder's latents after training, and it partly works. The section {ref}`Why a plain autoencoder cannot generate <vae-basics-cannot-generate>` tries it, and latent diffusion models do exactly this with a much stronger model than one bell curve. So the shape of the latent distribution is not the whole story.
- What the VAE adds is a decoder trained on the space *around* every example, not only on single points, so random draws mostly land where the decoder knows what to do. And the distribution to draw from is fixed by design, not fitted after the fact.

**A caveat from the start.** "New" means new combinations inside the range of the training data. A VAE trained on ordinary traffic produces ordinary-looking traffic. It cannot be trusted to invent events it has never seen, such as a crash or a rare corner case. {ref}`Where it breaks <vae-basics-breaks>` returns to this.

(vae-basics-example)=
## The running example: a new traffic state from a few knobs

A variational autoencoder (VAE) learns two things from data: a few hidden numbers that explain each example, and a way to turn those numbers back into a full example. Once it has both, you can make new examples that look like the real ones.

Our running example is one you already know: speed heatmaps from the Cell Transmission Model (CTM). Each heatmap covers 20 road cells (4 miles) by 20 time steps (9.6 minutes), so it is 400 speed numbers. We use 4,000 of them. The CTM made each one from five inputs (starting density, inflow, bottleneck capacity, and when the bottleneck starts and how long it lasts) plus a random cell-to-cell pattern in the starting density, up to ±15% of jam density per cell. This is simulation data, not detector data.

**Why this is hard.** You cannot make a realistic heatmap by drawing each of the 400 cells on its own. In the simulated heatmaps, two neighbouring road cells differ by 4.06 mph on average. Draw every cell independently and neighbours differ by 25.63 mph: salt-and-pepper noise that no road produces. The 400 numbers depend on each other, and a generator has to keep that dependence.

**The comparison.** You already own a generator that keeps this dependence for free: the CTM. Give it five numbers and conservation plus the fundamental diagram produce a whole, consistent heatmap. A VAE also turns a few numbers into a whole heatmap, but it gets there from the opposite direction. The CTM is theory-based: its inputs are physical quantities and its rules are the traffic mechanism. The VAE is purely data-driven: it does not try to rebuild the mechanism or discover the physical causes. It only learns to produce data that look like the data it was shown.

|  | The CTM (you know it) | A VAE (this page) |
| --- | --- | --- |
| What goes in | 5 named inputs (density, inflow, capacity, start, length) | a few unnamed numbers, called **z** |
| What turns them into a heatmap | physics: conservation + the fundamental diagram | a learned neural network, the **decoder** |
| Where good input values come from | you choose them | the model learns a range of typical values: a bell curve |
| What it needs | calibration to a site | thousands of example heatmaps |
| What its numbers mean | physical quantities you can name and measure | whatever training finds useful; not guaranteed to be flow, density or OD |
| What it is trying to do | reproduce the traffic mechanism (theory-based) | reproduce what the data look like (purely data-driven); no claim about the mechanism |

We call the numbers in z the **latents**, short for latent variables. In class we also call them **knobs**: turn one and the output changes. Papers also say *latent code* or *latent dimensions*. Unlike the CTM's inputs, nobody tells the VAE what each knob means. It has to find useful ones on its own, and they need not be flow, density or OD.

(vae-three-knobs)=
### See it on real traffic: three knobs

Our heatmaps come from a simulator. To see what knobs look like on real data, we trained a small VAE with 3 latents on daily flow curves from Caltrans PeMS District 8 (San Bernardino and Riverside, California): 170 detector stations, July and August 2016. Each example is one station on one day, 96 flows (one per 15 minutes) in veh/h. The encoder squeezes a day into 3 knobs. The decoder turns any 3 knobs back into a full 24-hour curve. The test days are new days at the same 170 stations, not new stations.

```{figure} ../_static/figures/VB_Three_Knobs.png
:alt: Three panels, one per knob. Turning knob 1 from minus 2 to plus 2 raises midday flow while the commute peaks fade; knob 2 changes night and late-evening traffic; knob 3 raises traffic overall and shifts the peaks. Below, a table of correlations between each knob and properties of the day on 1,968 test station-days: knob 3 correlates 0.93 with daily volume and 0.95 with morning peak flow; mean occupancy reaches at most 0.54. Retraining from another random start moves the volume knob to knob 1, then knob 2.
:width: 100%

Three knobs, turned one at a time: a VAE with 3 latents on real PeMS District 8 flow (170 stations, July&ndash;August 2016). In each panel the other two knobs stay at 0.
```

**Try it** in the interactive version below. Turn one dial and the whole day's curve changes at once. Load a real test day and see which knob setting rebuilds it.

What to notice:

- **One knob moves the whole day.** Each knob changes all 96 flows together, smoothly. The decoder has learned which parts of the day rise and fall together, so a single number reshapes the full curve. That is why we call latents knobs.
- **Three knobs are enough to rebuild a day.** On the 12 test days, 3 knobs rebuild a station-day with an RMS error of 280 veh/h per 15-minute bin, against 344 veh/h for PCA with 3 components and 1,341 veh/h for the average curve.
- **A knob need not be flow, density or OD.** Knob 3 comes close to "how much traffic" (correlation 0.93 with daily volume), but turning it also moves the peaks. No knob tracks density: mean occupancy, the detector's stand-in for density, never reaches a correlation of 0.7 with any knob, and a straight-line read-out from all three knobs explains only about a third of it (R² of 0.30 to 0.33 over three training runs). No knob is the balance between the evening and morning peaks either, a rough trace of which way trips run (straight-line R² of 0.37 to 0.42). The information is not missing: a more flexible read-out recovers more of it, mostly because the knobs also encode which kind of station a day came from. It is spread across the knobs instead of getting one of its own.
- **The knobs are not fixed.** Train again from another random start and the "volume" knob shows up as knob 1 in one run and knob 2 in the next, with its sign flipped. The model keeps whatever directions help it rebuild the data. Naming them is your job, and the names may not hold.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion &mdash; Three knobs of a traffic VAE</span>
    <a href="../_static/companions/VAE_Three_Knobs.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/VAE_Three_Knobs.html"
          title="Three knobs of a traffic VAE: turn each latent and watch a whole day of flow change" loading="lazy"></iframe>
</div>

(vae-basics-ae-heatmaps)=
## The autoencoder on our heatmaps

Here is the plain autoencoder, trained on our heatmaps. With only 2 latents, it rebuilds the test heatmaps with a typical (RMS) error of about 7 mph per cell.

```{figure} ../_static/figures/GenVAE_Hourglass.png
:alt: The hourglass: a real heatmap enters an encoder that narrows 400 to 96 to 2 numbers; a decoder widens 2 to 96 to 400 and outputs a rebuilt heatmap. On the right: to generate, draw 2 numbers from a bell curve and run only the decoder.
:width: 100%

The course VAE: 400 &rarr; 96 &rarr; 2 &rarr; 96 &rarr; 400. To generate, skip the encoder.
```

Read the picture from left to right:

- **Encoder.** A small neural network. It reads the 400 speeds, passes them through a layer of 96 units, and outputs 2 numbers.
- **The latents, z.** Those 2 numbers. Everything the decoder will know about this heatmap must fit in them.
- **Decoder.** A mirror network, 2 to 96 to 400, that turns the latents back into a heatmap.
- **Training.** Show the network thousands of heatmaps and adjust its weights so each rebuilt heatmap lands close to its input. No labels are needed: the input is its own target.

The picture is the full VAE we build toward. A plain autoencoder is the same hourglass without the bell curve on the right and without the second line of the loss.

**How much do 2 numbers keep?** The models were trained on 3,200 heatmaps and scored on 400 they never saw.

| Rebuilding the 400 test heatmaps from... | Error per cell (RMS) |
| --- | --- |
| nothing: the average heatmap, used for every heatmap | 23.76 mph |
| PCA, 2 components | 9.85 mph |
| a plain autoencoder, 2 numbers | 7.29 mph |

If you have met PCA, it is the straight-line version of this idea: an autoencoder whose encoder and decoder are plain matrix multiplications. The neural network can bend, so it does better with the same 2 numbers.

Why do 2 numbers go so far? Because a road's 400 speeds are not free. Conservation and the fundamental diagram tie each cell to its neighbours, so a few causes decide most of the picture. The same habit sits behind every fundamental diagram you have fitted: three parameters summarise a whole corridor.

So far this is **compression**, not generation. To make a *new* heatmap you would have to invent new latents and decode them. The {ref}`next section <vae-basics-cannot-generate>` shows why that goes wrong for a plain autoencoder.

(vae-basics-cannot-generate)=
## Why a plain autoencoder can rebuild, but cannot generate

A plain autoencoder puts each heatmap's latents wherever rebuilding is easiest, so after training there is no rule for where new latents should come from. Draw latents from the obvious choice, a standard bell curve, and the results cover only 2.5% of the real variety.

```{figure} ../_static/figures/VB_Codes_vs_Bell.png
:alt: Left: the plain autoencoder's training latents form a wide, lopsided cloud; the standard bell's rings cover a small patch near the top, 12 percent of latents sit inside the 2-spread ring, and four heatmaps decoded from bell draws look much alike, covering 2.5 percent of the real variety. Right: the VAE's latents sit around the bell's rings, 95 percent inside the 2-spread ring, and four decoded bell draws vary from free flow to heavy congestion; they look real (0.998) but cover 8.5 percent of the variety.
:width: 100%

A plain autoencoder leaves no map of where to draw: 1,600 of the 3,200 training heatmaps, placed by their 2 latents. Gold rings: the standard bell.
```

Read the left panel first. Each dot is one training heatmap, placed by its 2 numbers and coloured by its starting density. Nothing in training told the autoencoder where to put its latents, so the cloud is wide and lopsided: its spread is 2.8 along number 1 and 5.0 along number 2, not 1. Only 12% of the training latents sit inside the bell's 2-spread ring (the circle of radius 2 around the centre), where a true bell would put 86%. Draws from the bell all land in one small patch, so the four heatmaps decoded from them look much alike.

The right panel is the VAE of {ref}`the next section <vae-basics-cloud>`. Its latents sit around the bell, so bell draws land among real latents and decode to heatmaps that range from free flow to heavy congestion.

**Two scores used from here on.** Each compares 400 generated heatmaps with the 400 test heatmaps.

- **Looks real** (precision): the share of generated heatmaps that land close to some real heatmap.
- **Covers variety** (recall): the share of real heatmaps that have a generated heatmap close to them.

A good generator scores high on both. For scale, real validation heatmaps scored against the test heatmaps get 0.945 and 0.953.

**Can you fix the autoencoder afterwards?** Yes, partly: fit a bell to its latents after training and draw from that.

| How the latents are drawn | Looks real | Covers variety |
| --- | --- | --- |
| autoencoder + the standard bell | 1.000 | 0.025 |
| autoencoder + a bell fitted to its latents afterwards | 0.910 | 0.212 |
| VAE + the standard bell | 0.998 | 0.085 |
| real validation heatmaps, for scale | 0.945 | 0.953 |

The fitted bell covers more variety, but its samples look less real. 14.5% of its draws fall in empty space between latents, and the plain autoencoder's decoder was never trained on the space around its latents. The VAE's bell draws hit empty space about as often (15.5%), but its decoder learned that space during training, so they still look real. Fitting a distribution to the latents afterwards is a real strategy: latent diffusion models, such as Stable Diffusion, do exactly that with a far stronger model than one bell. The VAE takes the other route. It builds the rule into training, so the map of where to draw exists by design. To check all this hands on, use the companion at the end of {ref}`4.6 <autoencoder-latent-layer>`: its last tab uses the plain autoencoder and the VAE of this page. The {ref}`next section <vae-basics-cloud>` shows how, and {ref}`Where it breaks <vae-basics-breaks>` explains why its samples still cover so little variety.

(vae-basics-cloud)=
## The VAE fix: a small cloud instead of a point

A plain autoencoder maps each input x to one exact point z. A VAE's encoder maps x to a **small cloud** instead: a Gaussian distribution over z, with a centre **μ** and a spread **σ** for each knob. During training, the decoder is handed a *random point from that cloud* and must rebuild x from it. So every point in the cloud, not only its centre, learns to decode to something close to x. Later, any point in or near that cloud can be decoded into a new heatmap similar to x, and the gaps between the clouds of different heatmaps fill with sensible in-between states.

```{figure} ../_static/figures/VB_Soft_Guess.png
:alt: A test heatmap enters the encoder, which outputs a centre mu of minus 0.249 and minus 0.054 and a spread sigma of 0.085 and 0.221. Two fresh bell numbers epsilon combine with them as z equals mu plus sigma times epsilon. Three draws land inside the cloud in the knob plane and decode to three heatmaps that sit 6.8, 4.2 and 1.7 mph from the heatmap decoded at the centre, while two random test heatmaps differ by 28.1 mph.
:width: 100%

The VAE encoder returns a small cloud, not a point: one test heatmap through the course VAE (2 knobs, &beta; = 0.6).
```

Follow one test heatmap through the picture. The CTM made it with a starting density of 30% of jam and a bottleneck at 34% of capacity; its mean speed is 40.7 mph.

1. **Encode.** The encoder returns μ = (−0.249, −0.054) and σ = (0.085, 0.221). It is surer about knob 1 than about knob 2.
2. **Draw noise.** Take ε, two fresh numbers from a standard bell (centre 0, spread 1).
3. **Shift and scale.** Set z = μ + σ × ε. Draw 3 used ε = (−0.51, −0.27), so z = (−0.249 + 0.085 × (−0.51), −0.054 + 0.221 × (−0.27)) = (−0.292, −0.114).
4. **Decode.** The three draws decode to heatmaps 1.7 to 6.8 mph from the heatmap decoded at the centre. Two random test heatmaps typically differ by 28.1 mph (median). Moving inside the cloud changes the traffic state a little; in these draws it never jumps to a different regime.

The plain autoencoder gives the same heatmap one point, (0.09, 0.64), every time.

**Why the cloud helps generation.** During training the decoder never sees exactly the same latent point twice for a heatmap. It must turn every point near μ into something close to that heatmap. Clouds of similar heatmaps overlap, so the space between training heatmaps fills in with sensible in-between states. {ref}`The loss <vae-basics-loss>` adds the second half: a rule that keeps all the clouds near one standard bell, which is the map you draw from.

**A bridge you know.** A Kalman filter for traffic state estimation returns an estimate and its uncertainty, not just a number. The VAE encoder does the same for the hidden knobs, in one pass: μ is the estimate, σ the uncertainty.

**Why write z = μ + σ × ε?** Training follows gradients (Module 1): it nudges each weight in the direction that lowers the loss. A bare random draw, "pick some z from the cloud", has no ordinary gradient, so the error at the decoder could not reach μ and σ (workarounds exist, but their gradients are very noisy). Written this way, the randomness sits in ε, which training leaves alone, while μ and σ are ordinary encoder outputs that the gradient can reach.

:::{admonition} Key idea: the reparameterization trick
:class: tip
Do not sample z directly. Sample the noise ε from a standard Gaussian, then compute **z = μ + σ × ε**. The result is the same random draw from the cloud, but now μ and σ sit in an ordinary formula, so training can adjust them. Every VAE uses this trick.
:::

:::{admonition} Going deeper &mdash; why an encoder at all?
:class: dropdown
For one heatmap, the exact soft guess over the knobs can be computed by brute force: decode every knob setting on a 161 × 161 grid and score each by how well it rebuilds the heatmap and how likely it is under the prior. That is 25,921 decoder passes per heatmap with 2 knobs, and about 4.5 × 10¹⁷ with 8. The encoder learns to make the guess in one pass. On the 400 test heatmaps its centre lands within one exact spread of the exact centre 92.5% of the time, and its spreads are 0.80 and 0.94 times the exact ones (medians): a little overconfident. One network that guesses for every input is called *amortized inference*; Kingma and Welling (2014) call the encoder a recognition model.
:::

(vae-basics-loss)=
## The loss: rebuild well, stay near the prior

The VAE learns by lowering one number per heatmap with two parts: how badly it rebuilds the heatmap, plus a charge, weighted by β, for how far that heatmap's cloud deviates from the prior, the standard Gaussian N(0, I) chosen at the {ref}`start of this page <vae-basics-ae-to-vae>`.

$$
\text{loss} \;=\; \tfrac{1}{2}\sum_{i=1}^{400}\big(\hat{x}_i - x_i\big)^2 \;+\; \beta\,\mathrm{KL}\big(q(z \mid x)\,\big\|\,\mathcal{N}(0, I)\big)
$$

| Symbol | What it is in our heatmaps |
| --- | --- |
| xᵢ and x̂ᵢ | real and rebuilt speed in road–time cell i, divided by 75 mph |
| sum over i = 1 to 400 | add up over all 400 cells of the heatmap |
| z | the 2 knobs |
| q(z \| x) | the cloud the encoder puts heatmap x in: centre μ, spread σ |
| N(0, I) | the prior: a standard Gaussian (bell curve), centre 0 and spread 1 for every knob |
| KL( · ‖ · ) | the Kullback–Leibler divergence: how different two bell curves are, in units called nats |
| β | the weight on the second term: 0.6 in the course model |

*In words:* rebuild every heatmap well, but pay for every cloud that deviates from the prior, so that later, draws from the prior land where the decoder knows what to do.

**What the bell term charges.** For one knob, the charge depends only on the cloud's centre and spread:

| One knob's cloud | Charge (nats) |
| --- | --- |
| centre 0, spread 1: exactly the bell | 0.000 |
| centre 1, spread 1: shifted | 0.500 |
| centre 2, spread 1: shifted further | 2.000 |
| centre 0, spread 0.5: twice as sure | 0.318 |
| centre 0, spread 0.1 | 1.808 |
| centre 0, spread 0.01: almost a point | 4.105 |

Two things cost: sitting off-centre, and being too sure. The charge keeps rising as a cloud shrinks toward a point (4.1 nats at spread 0.01), which pushes a VAE away from becoming a plain autoencoder. With a very small β it gets close (see {ref}`The β knob <vae-basics-beta>`).

**The heatmap of {ref}`the cloud section <vae-basics-cloud>`, priced out** (with draw 1, ε = (0.74, 1.95), almost two spreads out on knob 2; β = 0.6):

- Rebuild term: 4.01. That is a rebuilt heatmap 10.6 mph (RMS per cell) from the real one.
- Bell term: 2.00 nats for knob 1 and 1.04 for knob 2, so 3.04 in total.
- Loss: 4.01 + 0.6 × 3.04 = 5.83.

Knob 1 costs more even though its centre (−0.249) is close to 0. Its spread is only 0.085, so almost all of its charge is for certainty. Over the 400 test heatmaps the average charge is 1.86 nats for knob 1 and 0.98 for knob 2: the encoder pays more to be precise about the knob that matters most.

The two terms pull against each other. The rebuild term wants as much detail as possible packed into the knobs. The bell term wants every cloud to look like the standard bell. β sets the exchange rate, and the {ref}`next section <vae-basics-beta>` shows what it does.

:::{admonition} Going deeper &mdash; where the loss comes from
:class: dropdown
A generative model would ideally maximise log p(x), the probability of the real heatmaps. For a VAE that cannot be computed during training (it needs an integral over every knob setting), but it has a lower bound, the *evidence lower bound* (ELBO): log p(x) ≥ E\[log p(x | z)\] − KL(q(z | x) ‖ p(z)), where p(z) is the prior, with the average taken over the encoder's cloud; training estimates that average with one draw per heatmap. If the decoder is read as a bell curve around x̂, −log p(x | z) becomes a squared error (plus a constant): the first term. The KL between a knob's cloud and the standard bell has a closed form, ½(μ² + σ² − 1 − ln σ²), which produced the price list above. Dividing the loss by β shows what β means: it is the same as assuming a decoder bell with variance β, so the loss equals β times the negative ELBO of that decoder, up to a constant that does not depend on the weights. With speeds divided by 75 mph, β = 0.6 assumes about 58 mph of noise per cell, far more than the real 7.7 mph rebuild error: one more reason to treat β as a knob to tune, not a physical quantity. Read that way, on the course model the ELBO sits a median 0.27 nats per heatmap below the exact log p(x) computed on the grid of the {ref}`going-deeper box on the encoder <vae-basics-cloud>`. Sources: Kingma and Welling (2014), *Auto-encoding variational Bayes*; Bishop and Bishop (2024), *Deep Learning*, chapter 19.
:::

(vae-basics-beta)=
## The $\beta$ knob: detail against order

β decides how much detail the knobs may keep. A small β gives sharper rebuilds and samples, but the latents only loosely follow the bell. A large β makes the latents hug the bell, blurs everything, and past a point switches a knob off entirely.

```{figure} ../_static/figures/VB_Beta.png
:alt: Three columns for beta 0.05, 0.6 and 3. At 0.05 the training latents spread beyond the bell's rings; at 0.6 they sit around the rings; at 3 they collapse onto a horizontal line. Below each, four heatmaps decoded from the same four bell draws, then rebuild error 7.35, 7.68 and 10.57 mph; knobs in use 2, 2 and 1; inside the 2-spread ring 70, 95 and 100 percent; samples cover variety 17.7, 8.5 and 0.0 percent; front sharpness 27.5, 22.5 and 19.5 mph.
:width: 100%

&beta; trades rebuild detail for an orderly knob space: the same network and data, only &beta; changed; latents of 1,600 training heatmaps. Gold rings: the bell.
```

To make this picture, the course network was trained six times on the same 3,200 heatmaps with the same settings. Only β changed. The β = 0.6 row is the course model itself. The scores here use the test heatmaps to show the trade; to choose β for a real model, score the candidates on validation heatmaps instead.

| β | Rebuild error (mph) | Knobs in use | Training latents inside the 2-spread ring | Samples cover variety | Front sharpness (mph) |
| --- | --- | --- | --- | --- | --- |
| 0.05 | 7.35 | 2 | 70% | 17.7% | 27.5 |
| 0.2 | 7.41 | 2 | 87% | 10.7% | 26.6 |
| 0.6, the course model | 7.68 | 2 | 95% | 8.5% | 22.5 |
| 1, the standard weighting | 8.25 | 2 | 97% | 7.2% | 22.4 |
| 3 | 10.57 | 1 | 100% | 0.0% | 19.5 |
| 12 | 12.18 | 1 | 100% | 0.0% | 18.4 |

For scale, real test heatmaps have a front sharpness of 39.6 mph, and a true bell puts 86% of its draws inside the 2-spread ring. *Front sharpness* is the largest speed jump between neighbouring road cells in each heatmap, averaged over heatmaps: a real queue front is a sharp jump. Every row still "looks real" (0.93 to 0.998), so that score cannot tell these models apart.

Three lessons:

1. **A little bell term goes a long way.** At β = 0.05 the latents already sit on the bell's scale (70% inside the ring, against 12% for the plain autoencoder), rebuilds are almost as good as the autoencoder's 7.29 mph, and samples cover the most variety.
2. **More β means wider clouds, and wider clouds mean more averaging.** Tight clouds become expensive, so the encoder reports wider ones: the typical spread on its surer knob grows from 0.05 at β = 0.05 to 0.16 at β = 0.6 and 0.61 at β = 12. The decoder must then serve many heatmaps from overlapping regions, and its best answer is their average. Fronts soften. {ref}`Where it breaks <vae-basics-breaks>` shows this averaging directly.
3. **Too much β switches a knob off.** At β = 3 and 12, knob 2 costs 0.00 nats: its cloud is the bell itself for every heatmap, so it carries no information and the decoder ignores it. The latents collapse onto a line. The surviving knob tracks starting density (correlation magnitude 0.95): the model keeps the biggest cause and drops the rest. Papers call a switched-off knob an inactive latent, a form of *posterior collapse*.

A second training seed repeats the pattern: rebuild errors within 0.13 mph, one knob off at β = 3 and 12, and the most coverage at the smallest β (18.2%). Coverage at β = 0.6 and 1 swaps order on that seed (4.5% and 8.0%), so treat differences of a few points as noise.

The practical rule: **β is a knob you tune against a scorecard, not a constant you copy.** The standard VAE weighting is β = 1, and the course model uses 0.6; on this data the scorecard favoured smaller values. Larger values are what the β-VAE (Higgins et al., 2017) uses to push each knob toward one separate factor of variation. {ref}`Where it breaks <vae-basics-breaks>` explains why that still does not make a knob a cause.

(vae-basics-knobs)=
## What the knobs learn, and how to generate

Nobody told the VAE about density or bottlenecks, yet its knob 1 tracks starting density (correlation −0.94) and knob 2 partly tracks bottleneck capacity (−0.57). To generate, draw two numbers from the bell and run only the decoder: one pass per new heatmap.

```{figure} ../_static/figures/VB_Knob_Map.png
:alt: Left: 400 test heatmaps placed at their latents, dense ones on the left and light ones on the right, with 25 gold squares on a grid. Right: the decoder's heatmap at each square; congestion fades to free flow moving right along knob 1, and the queue at the downstream bottleneck grows moving up knob 2.
:width: 100%

Every point in the knob plane decodes to a traffic state. Left: the 400 test heatmaps by their latents. Right: the decoder at 25 knob settings (the gold squares).
```

On the left, each dot is a test heatmap placed at its encoder centre μ and coloured by its starting density. On the right is the decoder's output at each gold square. Move right along knob 1 and the road empties, from heavy congestion to free flow. Move up knob 2 and the queue from the downstream bottleneck (the top edge of each heatmap) grows. The space between the dots is not empty: every point we decoded gives a smooth, believable traffic state.

**Which simulator inputs did the knobs pick up?** The table gives the share of each input's variation that a straight-line read-out from the knobs explains on the test heatmaps.

| What the CTM was given | 2 knobs | 8 knobs |
| --- | --- | --- |
| starting density | 90% | 95% |
| bottleneck capacity | 32% | 59% |
| bottleneck start | 16% | 67% |
| upstream inflow | 5% | 43% |
| bottleneck length | 1% | 19% |

Two knobs cannot hold five inputs plus the random starting pattern. The model keeps starting density, by far the biggest mover: changing it across its range moves a heatmap by 54.1 mph (median RMS per cell). Among the rest, the order is not simply by size of effect. Inflow moves a heatmap about as much as bottleneck capacity (19.6 and 20.5 mph), yet the 2 knobs explain 5% of it; with 8 knobs they explain 43%. Which causes win the slots is decided by the data and the training, not by you.

**Generating, and steering.** A random bell draw gives a random traffic state. You can also choose where to draw. Take the latents of the 698 training heatmaps that started heavy (density at least 45% of jam), fit a small bell around them, and draw from that instead:

| Where the knobs were drawn | Mean speed of the heatmaps |
| --- | --- |
| the whole standard bell | 48.7 mph |
| around the heavy-start latents | 28.3 mph |
| real heavy-start test heatmaps, for comparison | 25.7 mph |
| all real test heatmaps, for comparison | 51.3 mph |

Steering moves the output most of the way toward heavy traffic, but not all the way.

**Two cautions before you name a knob.** First, knob directions are arbitrary: retrain and knob 1 may come out flipped, or rotated into knob 2. Second, compare a learned knob with the obvious physical quantity. The two knobs explain 94% of the variation in mean speed across heatmaps, so knob 1 is largely "how congested overall", which mean speed already tells you.

(same-vae-different-traffic)=
## Same VAE, different traffic: the knobs depend on the data

Everything above used one dataset of heatmaps. What the knobs mean, how many of them get used, and what the model
generates all depend on the traffic it was trained on. The companion below trains one plain VAE
($\beta$ = 1) on 1,008-cell snapshots of the course's torus-grid network simulator: on light traffic,
on heavy congestion, on both, and on a mix where congestion is only 5% of the data. It then compares the
latent maps those diets produce. A physics tab checks whether generated networks move like real
traffic, and the last tabs turn the results into rules for collecting VAE training data.

Five results to look for:

- One knob tracks the load every time, much like knob 1 above. The other knob picks up whatever pattern
  is left over: most often the signal clock in light traffic, and where the jam sits in heavy traffic.
- A light-only model throws heavy snapshots far outside the bell. A heavy-only model keeps light snapshots
  near its centre and still rebuilds them badly. The score, not the position on the map, is the alarm.
- With congestion at 5% of the training data, only 1.3&ndash;1.8% of generated networks are congested.
- With no near-capacity data, the model does worse on near-capacity traffic than a per-cell average table.
- Generated networks carry more flow than real ones at the same load. The decoder scatters vehicles
  instead of queuing them, and neither the score nor the latent map shows it; a physics check does.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion &mdash; Same VAE, different traffic</span>
    <a href="../_static/companions/Same_VAE_Different_Traffic_Companion.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/Same_VAE_Different_Traffic_Companion.html"
          title="Same VAE, different traffic: how the training data shape a VAE's latent space" loading="lazy"></iframe>
</div>

(vae-basics-breaks)=
## Where it breaks

The VAE fails in four ways you should expect: its samples blur because the decoder returns an average, its knobs are not causes, nothing in its loss knows traffic physics, and it can only generate inside the range of the data it was trained on.

### Blur: the decoder returns an average

```{figure} ../_static/figures/VB_Blur.png
:alt: Four of the 20 training heatmaps that the encoder puts at almost the same two knobs have queue fronts in different places. Their average has a smeared front, and the decoder’s output at those knobs looks like the average. Over 200 random knob settings the decoder’s output was 2.98 mph from the average of its neighbours and 8.68 mph from a typical one; a real neighbour sits 7.86 mph from the average of the others.
:width: 100%

Why the VAE blurs: 20 training heatmaps that the encoder puts at almost the same 2 knobs, their average, and the decoder&rsquo;s output there.
```

Pick a knob setting and find the 20 training heatmaps whose latents sit closest to it. Two knobs cannot pin down everything, so these neighbours differ: their queue fronts sit in different places. Over 200 random knob settings, the decoder's output was 2.98 mph (RMS per cell) from the **average** of its 20 neighbours, but 8.68 mph from a typical single neighbour. A real neighbour, for comparison, sits 7.86 mph from the average of the other nineteen. The decoder is far closer to the average than a typical real neighbour is.

This is not a bug; it is what squared error asks for. Suppose a cell is jammed at 10 mph half the time and free at 70 mph the other half. The single guess with the smallest squared error is 40 mph, a speed that never happens. Wherever the knobs leave something open, such as exactly where a front sits, the decoder averages the possibilities, and an average of sharp fronts is a soft one. Real test heatmaps have a front sharpness of 39.6 mph; samples from the 2-knob VAE have 22.5, and from an 8-knob VAE 26.2. More knobs help a little; they do not fix it.

When does it matter? An averaged state is often fine for a capacity study. It is harmful when the timing or position of a front is the point: queue-spillback warnings, incident detection, signal plans. The average of "the queue reaches the ramp" and "it does not" is a moderate slowdown that never happens. Diffusion models, next in the course, avoid this averaging by generating in many small steps.

### Knobs are not causes

Even here, where we know the five inputs that made the data, the knobs mix them, drop some, and change direction between training runs. On real data you have no list of true causes to check against. So a VAE trained on, say, dashcam video of automated vehicles meeting pedestrians will rebuild the video, but it will not tell you which factors drive the interaction. To find factors, name candidate features, measure them, and test them with a model built for that question: a regression or choice model, a controlled simulation, or an experiment.

### Nothing in the loss knows physics

The loss scores how close the speeds are, cell by cell. It does not check conservation or wave speeds. A sample can look plausible and still contain a front that moves faster than any wave the fundamental diagram allows. For the CTM used here, admissible wave speeds run from −15 mph (a queue growing upstream) to +75 mph (free flow). The VAE Traffic Lab lets you referee generated heatmaps against that band.

### It generates only inside the data it has seen

A VAE samples from the distribution of its training data, and it is trustworthy only inside that distribution. The prior N(0, I) covers the region where the training latents sit. A draw far out in the bell's tail has no training heatmap near it, and the decoder's answer there is a guess. Even draws from the bell itself land in empty space between training latents 15.5% of the time on our data (see {ref}`above <vae-basics-cannot-generate>`).

This matters most for the events transportation engineers care about. A crash, a queue spilling onto an arterial, or a detector failing during a storm is rare or absent in ordinary data. A VAE trained on ordinary traffic will not invent such events reliably; it generates more ordinary traffic, or, when pushed toward the edge, impossible traffic that only looks real. Waiting years for enough crashes to train on is too reactive. Rare events need methods built for them, such as near-miss data combined with physics rules and importance sampling; the handout *Generating Crash Data from Near-Misses* covers them.

:::{admonition} Before you trust these results
:class: warning
*Baseline:* for rebuilding, the average heatmap (23.76 mph) and PCA with the same number of components (9.85 mph at 2; at 8, PCA's 4.91 mph beats the 8-knob VAE's 5.50). For generating, real heatmaps scored the same way. *Split:* the 4,000 heatmaps were split by whole heatmap into 3,200 training, 400 validation and 400 test heatmaps, and every model saw only the 3,200. Scores and rebuild errors are on the 400 test heatmaps; where latents sit (inside the ring) is measured on the training latents. The course model's β = 0.6 was fixed before the sweep in {ref}`The β knob <vae-basics-beta>`, which is shown for illustration only. *Ugly cases:* one simulator on one 4-mile road, so this is synthetic data; samples have soft fronts; inflow is nearly invisible with 2 knobs; knob directions change between runs; coverage moves by several points between training seeds; and nothing here tests events outside the training data.
:::

## Fit card and applications

Use a VAE when you need many plausible examples fast, compact latents for other models, or a cheap "this looks unusual" flag. Do not use it to find causes.

| Fit card | Variational autoencoder (VAE) |
| --- | --- |
| Idea in one sentence | Compress each example to a few knobs with an uncertainty, learn to rebuild it, and generate by drawing new knobs from a bell. |
| Why it works | The bottleneck keeps what varies most; the noise and the bell term make the knob space smooth and safe to draw from. |
| Fits these tasks | Many plausible states in one pass each; compressing traffic states or sensor frames; flagging inputs it cannot rebuild; compact latents for other models. Leverage labels (the course's six, from Week 1): **generation**, **extraction**. |
| Needs this data | Thousands of unlabelled examples of one kind (detector heatmaps, trajectories, camera frames); a clean picture of "normal" if you will flag anomalies; a rebuild error that matches what you care about. |
| Breaks when | Details the knobs leave open get averaged (soft fronts, faded small objects); β is set without a scorecard; knobs are read as causes; it is asked for events missing from its training data, such as crashes; physics matters and nothing enforces it. |
| Keep the classical method when | You already know the causes (a calibrated CTM or fundamental diagram); PCA compresses well enough (8 components beat the 8-knob VAE here); a written rule catches the failure you know about. |

| Task | Data it needs | Classical baseline | Where VAEs show up |
| --- | --- | --- | --- |
| **Traffic flow:** draw many plausible corridor states for a capacity or reliability study | detector speed or flow heatmaps | CTM or LWR runs with sampled inputs; replaying historical days | the course model: one decoder pass per new state |
| **Agency practice:** flag broken camera or detector feeds | frames or days known to be normal | written checks: flat lines, smears, out-of-range values | the longer VAE-and-diffusion handout: a VAE trained only on clean FL511 frames scored AUC 0.97; a one-line smear rule scored 0.9996 |
| **Driving automation:** predict several possible futures for nearby road users | trajectory sets such as Waymo Open, highD, NGSIM | constant-velocity or physics-based prediction | conditional VAEs: DESIRE (Lee et al., 2017), Trajectron++ (Salzmann et al., 2020) |
| **Driving automation:** compress camera frames into a few latents that a planner or simulator works on | dashcam or simulator video | hand-designed features: lane offset, gaps, speeds | World Models (Ha and Schmidhuber, 2018) used a VAE on a car-racing game; latent diffusion (Rombach et al., 2022) generates inside an autoencoder's latent space |
| **Road safety:** screen intersection trajectories for unusual movements worth a human look | drone or camera trajectories | time-to-collision or post-encroachment-time thresholds | no standard tool yet: an idea to test, with the cautions of {ref}`Where it breaks <vae-basics-breaks>` |

Note the agency row: the written rule beat the VAE. A VAE flag is worth having for failures nobody has written a rule for yet.

## Summary and practice

**The VAE in eight lines.**

1. An autoencoder squeezes a heatmap into a few latents and rebuilds it; 2 latents rebuild our test heatmaps with a typical (RMS) error of 7.29 mph.
2. It cannot generate, because nothing says where its latents live: only 12% sit inside the bell's 2-spread ring.
3. A VAE encoder returns a cloud, a centre μ and a spread σ; training decodes a random point z = μ + σ × ε.
4. The loss is rebuild error plus β times a charge for every cloud that strays from the standard bell.
5. β trades detail for order. Tune it against a scorecard; too much switches knobs off.
6. To generate, draw z from the prior N(0, I) and decode once. To steer, choose where you draw.
7. Samples blur because the decoder returns an average; knobs are not causes; nothing enforces physics.
8. A VAE generates only inside the range of its training data. Do not rely on it for crashes or other corner cases it has never seen.

### Label the picture

```{figure} ../_static/figures/VB_Label_Step.png
:alt: A diagram of one VAE training step with six blanks. A heatmap x goes into box A, which feeds boxes B and C; B, C and box D (fresh at every step) combine as z = B + C times D; z goes into box E, which outputs the rebuilt x-hat; the rebuilt x-hat is compared with x in the rebuild error; box F, below C, is the second part of the loss.
:width: 100%

Fill in the blanks: one training step of a VAE.
```

Word bank: encoder · decoder · the centre μ · the spread σ · noise ε from a standard bell · the bell term (KL).

:::{admonition} Answers
:class: dropdown
A: encoder. B: the centre &mu;. C: the spread &sigma;. D: noise &epsilon; from a standard bell, fresh at every step.
E: decoder. F: the bell term, the KL between the encoder's cloud and the standard bell.
:::

### Check yourself

1. You need 2,000 synthetic corridor-days for a reliability study by tomorrow. Your VAE's samples look real (0.998) but cover 8.5% of the variety. Is it fit for this purpose? What would you check before using it?
2. A colleague trains a VAE on detector data with β = 4 and reports that "knob 2 does nothing". What most likely happened, and what would you try?
3. For one heatmap your VAE returns μ = (1.2, −0.3) and σ = (0.05, 0.9). Which knob is the encoder sure about? Which knob costs more in the bell term, and why?
4. An agency wants to flag faulty loop detectors with a VAE's rebuild error. What must the training days contain, and what simpler method must the VAE beat before anyone deploys it?
5. A classmate trains a VAE on dashcam clips of automated vehicles meeting pedestrians and finds that knob 3 tracks pedestrian crossing speed. Can the paper claim crossing speed is a dominant factor in these interactions? What evidence would support that claim?
6. You must compress a year of 5-minute detector data for storage and quick similarity search. When would you choose PCA over a VAE?
7. A team wants to train a queue-spillback warning on VAE-generated scenarios. What would go wrong, and which number on this page warns you?
8. A city wants to train a VAE on two years of video from one intersection and use it to generate crash scenarios for testing a new warning system. What will the VAE most likely produce, and what would you ask for instead?
9. Your detector archive is 80% overnight free flow. What will a VAE trained on it generate, and what would you change in the data before training? (Tabs 6 and 8 of the {ref}`Same VAE, different traffic <same-vae-different-traffic>` companion help.)

### Where to go next

- Back: {doc}`4.4 Latent variables <notes2b-latent-variables>` and {doc}`4.5–4.7 Autoencoders <notes2c-autoencoders>`. Ahead: {doc}`4.9 <notes4-gan>` scores this VAE against a GAN, and {doc}`4.10 <notes6-diffusion-basics>` shows how diffusion avoids the blur.
- The VAE Traffic Lab ({doc}`all labs <../labs>`): look inside the encoder, shift a heatmap and watch its latents move, and referee generated heatmaps against the admissible wave speeds.
- The VAE-to-Diffusion Lab: why VAEs blur when an outcome can go two ways.
- The longer handout, *Deep Generative Models: VAE and Diffusion*: diffusion models, and VAEs on real dashcam and FL511 camera data.
- The {ref}`interactive three-knob figure <vae-three-knobs>` on this page: turn the knobs of a VAE trained on real PeMS flow curves.
- The handout Generating Crash Data from Near-Misses: what to use when the events you need are rare.

## References for 4.8

- Kingma, D. P., and Welling, M. (2014). Auto-encoding variational Bayes. ICLR. [arXiv:1312.6114](https://arxiv.org/abs/1312.6114)
- Bishop, C. M., and Bishop, H. (2024). *Deep Learning: Foundations and Concepts*. Springer. Chapter 19, Autoencoders.
- Higgins, I., et al. (2017). β-VAE: Learning basic visual concepts with a constrained variational framework. ICLR. [ICLR 2017 paper](https://mlanthology.org/iclr/2017/higgins2017iclr-beta)
- Lee, N., et al. (2017). DESIRE: Distant future prediction in dynamic scenes with interacting agents. CVPR. [arXiv:1704.04394](https://arxiv.org/abs/1704.04394)
- Salzmann, T., Ivanovic, B., Chakravarty, P., and Pavone, M. (2020). Trajectron++: Dynamically-feasible trajectory forecasting with heterogeneous data. ECCV. [arXiv:2001.03093](https://arxiv.org/abs/2001.03093)
- Ha, D., and Schmidhuber, J. (2018). World models. [arXiv:1803.10122](https://arxiv.org/abs/1803.10122)
- Rombach, R., et al. (2022). High-resolution image synthesis with latent diffusion models. CVPR. [arXiv:2112.10752](https://arxiv.org/abs/2112.10752)
- Guo, S., Lin, Y., Feng, N., Song, C., and Wan, H. (2019). Attention based spatial-temporal graph convolutional networks for traffic flow forecasting. AAAI. [doi:10.1609/aaai.v33i01.3301922](https://doi.org/10.1609/aaai.v33i01.3301922). Source of the PEMS08 data set used in the three-knob figure.
- Caltrans Performance Measurement System (PeMS), District 8 detector data. [pems.dot.ca.gov](https://pems.dot.ca.gov)

Every number on this page comes from models trained on the course's 4,000 CTM heatmaps, except the three-knob
figure and its companion, which use PeMS District 8 detector data, and the Same VAE, different traffic companion,
which uses the course's torus-grid network simulator.

---

Next: {doc}`4.9 Generative Adversarial Networks (GAN) <notes4-gan>`. Back to the {doc}`Module 4 map <index>`.
