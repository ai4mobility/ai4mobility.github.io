(diffusion-basics)=
# 4.11 Diffusion models: the basics

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 4 &middot; Section 4.11</span>
    <span class="notes-card-session">Session: VAE and diffusion</span>
  </div>
  <p class="notes-card-lede">Diffusion, built up from Bishop&rsquo;s math with every step kept plain. A fixed encoder adds noise until nothing is left; a network learns to remove it one small step at a time; and sampling turns fresh static into a new traffic state. This page works the math on two real I-405 detectors and the course heatmaps, answers where a prompt comes in when generation starts from pure noise, scores diffusion against the VAE, and ends with where it should not be trusted.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Read it before</h4>
      <ul>
      <li><a href="notes2e-copying.html">4.6 Stopping the copy</a>: the denoising autoencoder</li>
      <li><a href="notes3b-vae-basics.html">4.8 Variational autoencoders: the basics</a></li>
      <li><a href="notes2a-gaussians.html">Before 4.3: Gaussians and their mixtures</a>, if bells are rusty</li>
      </ul>
    </div>
    <div>
      <h4>Labs</h4>
      <ul><li><a href="../labs.html">From VAE to diffusion; Training the denoiser</a></li></ul>
    </div>
  </div>
</div>

## What this section covers

- The math in Bishop&rsquo;s notation: a fixed encoder that adds noise, the jump to any step, and the three arrows of the diffusion picture
- Training: the algorithm, why the loss is &#8214;g &minus; &epsilon;&#8214;&sup2;, and why naming the noise teaches denoising
- Sampling: the algorithm, a traced run, why many small steps beat one big jump, and where a prompt fits in
- How many steps, and what each one costs
- Diffusion and the VAE scored on the same heatmaps
- Steering: scenarios, guidance and filling gaps without retraining
- Where it breaks, fit card, applications, a summary, a label-the-picture exercise and nine questions

A diffusion model makes a new traffic state by starting from pure static and removing a little noise at a time, many times over. Each small step is an easy cleaning job. Together, the steps rebuild the sharp queue fronts that a VAE blurs. The first three sections build the math, following Bishop &amp; Bishop&rsquo;s *Deep Learning* (Chapter 20): the noise-adding encoder, how the denoising network is trained, and how it turns pure noise into a new sample. The rest test it on traffic data and say where it fits.

This page comes after the autoencoder pages ({doc}`4.4–4.6 <notes2c-autoencoders>`) and {doc}`4.8 Variational autoencoders: the basics <notes3b-vae-basics>`. It uses the same two running examples, so you can compare the three models on the same data:

- **Real data.** Two I-405 N detectors 0.73 mi apart in Los Angeles (PeMS, May–June 2012), the pair from {doc}`4.4 <notes2c-autoencoders>`. Each reading is just two speeds, so you can see every point on one plot.
- **Synthetic data.** The course's 4,000 speed heatmaps (road segment × time) simulated with the cell transmission model (CTM), the same heatmaps as 4.4&ndash;4.8.

**After this page you should be able to:**

1. Write the noise-adding process in Bishop’s notation, and explain why its encoder is a fixed distribution, not a single point.
2. Tell apart the three steps in the diffusion picture: the fixed forward step, the exact reverse step that needs the clean data, and the learned reverse step that does not.
3. Explain why the training loss is ‖g − ε‖², why it is a useful learning signal, and build one training example by hand.
4. Walk through the sampling algorithm, say why many small steps beat one big jump, and explain what decides the sample when it starts from pure noise, and where a prompt fits in.
5. Judge when diffusion fits a transportation task, and when a VAE, a simulator, or a simple rule is the better tool.

**A note on words and symbols.** *Static* means pure random noise, like an untuned TV. The *noise level* or *step* t runs from 0 (clean data) to T (pure static). The *denoiser*, or *decoder*, is the neural network that learns to remove noise. In the autoencoder and VAE pages, the latents z were a few numbers squeezed out of the data. In a diffusion model, the latents z₁, …, z\_T are noisy versions of the data themselves, the same size as the data: there is no squeeze. The symbols follow Bishop & Bishop, *Deep Learning* (2024), Chapter 20: x is the clean data, zₜ the latent after t steps, βₜ the noise added at step t, αₜ = (1 − β₁)⋯(1 − βₜ), which sets how much of x is left after t steps, and g(zₜ, w, t) the network with weights w. Many papers and code libraries write x₀, xₜ and ᾱₜ instead of x, zₜ and αₜ.

(diffusion-math)=
## The math: a fixed encoder and a learned decoder

A diffusion model is a latent-variable model with two halves. The *encoder* adds noise in many small steps and is fixed: nothing in it is learned. The *decoder* removes the noise one step at a time and is a trained neural network. This section writes both halves in the notation of Bishop & Bishop, *Deep Learning*, Chapter 20.

**One step of noise.** Take a clean reading x and blend it with fresh random noise, separately for each value. Repeat this T times. Step t turns zₜ₋₁ into zₜ (with z₀ = x):

$$
z_t \;=\; \sqrt{1-\beta_t}\; z_{t-1} \;+\; \sqrt{\beta_t}\; \epsilon_t
$$

| Symbol | What it is here |
| --- | --- |
| x | the clean data: one detector reading (two standardized speeds) or one heatmap (400 cells) |
| zₜ | the noisy version after t steps, t = 1, …, T. These are the *latent variables* |
| εₜ | fresh static at step t: random numbers from a standard bell, mean 0 and spread 1 |
| βₜ | the amount of noise (a variance) added at step t, set by hand: small for almost every step |
| T | the number of steps: 1,000 in the course models |

*In words:* each step keeps √(1 − βₜ) of the previous state and adds a little noise. Written as a probability distribution, the step is a bell centred on the shrunk previous state: q(zₜ | zₜ₋₁) = N(zₜ | √(1 − βₜ) zₜ₋₁, βₜ I). Each step depends only on the step before it, so z₁, …, z\_T form a *Markov chain*.

**Why these two numbers.** The first one shrinks the state toward zero; the second adds noise. If a value has variance v before a step, it has variance (1 − βₜ) v + βₜ after it, which is always closer to 1. So step after step the mean slides to 0 and the variance to 1. After enough steps, every reading, whatever it was, has become the same thing: a standard bell.

**The schedule.** The βₜ values are chosen by hand and grow along the chain, β₁ < β₂ < … < β\_T: tiny steps at first, big ones at the end. The course models use the cosine schedule (Nichol & Dhariwal, 2021):

| Step t | βₜ (noise added at this step) | αₜ (share of the variance still from x) | √αₜ (how much of x is left: signal) | √(1 − αₜ) (noise) |
| --- | --- | --- | --- | --- |
| 1 | 0.00004 | 1.000 | 1.000 | 0.006 |
| 100 | 0.0005 | 0.972 | 0.986 | 0.167 |
| 500 | 0.0031 | 0.494 | 0.703 | 0.711 |
| 900 | 0.0195 | 0.024 | 0.155 | 0.988 |
| 1,000 | 0.999 | 0.000 | 0.000 | 1.000 |

The last two steps are the exception. The cosine schedule caps βₜ at 0.999, so β₉₉₉ = 0.75 and β₁,₀₀₀ = 0.999 wipe out the little signal that is left (Nichol & Dhariwal, 2021). That makes z\_T a standard bell for all practical purposes: at t = 1,000, α is about 2.4 × 10⁻⁹.

**Jump straight to step t.** A sum of bell-shaped noises is again a bell, so the t small steps collapse into one formula:

$$
z_t \;=\; \sqrt{\alpha_t}\; x \;+\; \sqrt{1-\alpha_t}\; \epsilon, \qquad \alpha_t \;=\; \prod_{\tau=1}^{t} (1-\beta_\tau)
$$

As a distribution, q(zₜ | x) = N(zₜ | √αₜ x, (1 − αₜ) I). Here √αₜ is how much of the clean reading is left after t steps, and αₜ is the share of zₜ’s variance that still comes from x (many papers write αₜ as ᾱₜ and the data as x₀). Training uses this shortcut: to make z₅₀₀ you do not have to run 500 steps.

**Worked example: one reading, one jump.** Take the 16:30 reading on Monday 7 May 2012 from {doc}`4.4 <notes2c-autoencoders>`: (70, 18) mph. The upstream detector is fast and the downstream one is crawling: the back of a queue sits between them.

1. Standardize with the May mean (50.45, 48.41 mph) and spread (22.05, 22.94 mph): x = ((70 − 50.45) / 22.05, (18 − 48.41) / 22.94) = (0.89, −1.33).
2. Draw static: ε = (−0.59, 0.63).
3. Look up step 500 in the table: √α = 0.703 and √(1 − α) = 0.711.
4. Mix: z₅₀₀ = (0.703 × 0.89 + 0.711 × (−0.59), 0.703 × (−1.33) + 0.711 × 0.63) = (0.21, −0.49).
5. Back on the mph scale, z₅₀₀ is (55.1, 37.2) mph: the gold dot in the t = 500 panel below.

From (55, 37) alone you cannot tell whether it came from a queue reading like (70, 18), a transition reading or a slow one. That is the problem the decoder has to solve.

```python
import numpy as np
alpha = 0.494                      # alpha_t at t = 500 (cosine schedule)
x = np.array([0.89, -1.33])        # the 16:30 reading, standardized
eps = np.array([-0.59, 0.63])      # the static draw
z = np.sqrt(alpha) * x + np.sqrt(1 - alpha) * eps
print(z.round(2))                  # expect [ 0.21 -0.49]
```

```{figure} ../_static/figures/DB_Cloud_Forward.png
:alt: Six scatter plots of the 6,624 May readings of the I-405 detector pair at steps t = 0, 100, 300, 500, 700 and 1,000; the two clusters spread and merge into one round cloud
:width: 100%

Adding noise turns the two-regime cloud into one round bell: all 6,624 May readings of the I-405 pair (5-minute speeds), noised to step t.
```

**Read the picture.** At t = 0 the May readings sit in two clusters: free flow at both detectors (around 70 mph) and slow at both (below 40 mph). A thin arm hangs down from the free-flow cluster where the back of a queue sits between the detectors. By t = 300 the arm has dissolved; by t = 700 the clusters have merged; at t = 1,000 the cloud is one round bell. The correlation between the two detectors falls from 0.92 (t = 0) to 0.46 (t = 500) to 0.01 (t = 1,000). For a heatmap the same recipe noises all 400 cells at once (top row of the figure further below). Noisy values need not be physical: at t = 500, 16% of heatmap 224’s noisy cells fall outside 0–75 mph.

**The encoder is a distribution, not a point.** Run the encoder twice on the same reading and you get two different zₜ, because the static differs. Like the VAE, and unlike the plain autoencoder, the encoder gives each input a whole bell of possible latents.

|  | Autoencoder | VAE | Diffusion |
| --- | --- | --- | --- |
| What the encoder gives for one x | one point, z = f(x) | a bell, q(z \| x) = N(μ(x), σ²(x)) | a bell at every step, q(zₜ \| x) = N(√αₜ x, (1 − αₜ) I) |
| Is the encoder learned? | yes | yes: a network outputs μ and σ | no: fixed by the schedule, no weights |
| Size of the latents | a few numbers | a few numbers | the same size as x, T times over |
| Where all inputs end up | scattered points with holes between | near a standard bell (pulled there by the KL term) | a standard bell at t = T, for all practical purposes (the schedule makes sure) |

The last row is the key to generation. Every training reading ends at the same standard bell, so a new sample can start from a fresh draw of that bell.

(diffusion-arrows)=
**The picture: three kinds of arrow.**

```{figure} ../_static/figures/DB_Graphical_Model.png
:alt: Four circles in a row: x (clean data), z_(t-1), z_t and z_T (pure static), joined left to right by red arrows, the fixed forward step q(z_t | z_(t-1)). A dashed green arrow above runs from z_t back to z_(t-1), labelled q(z_(t-1) | z_t, x): the exact way back when x is known, the answer key, training only. A solid blue arrow below runs the same way, labelled p(z_(t-1) | z_t, w): the learned decoder, which never sees x.
:width: 100%

The diffusion process as a graphical model, after Bishop &amp; Bishop (2024), Figure 20.2.
```

- **Red, q(zₜ | zₜ₋₁): the forward encoder** from above. Fixed, known exactly, adds a little noise at each step.
- **Blue, p(zₜ₋₁ | zₜ, w): the decoder** we want, a bell whose centre a neural network with weights w computes. It sees only the noisy state zₜ and the step t, never the clean x. It is what makes new samples.
- **Green, q(zₜ₋₁ | zₜ, x): the reverse step when the clean x is known.** Given both the noisy state and the clean reading it came from, Bayes’ rule gives the exact distribution of the state one step earlier. It is a bell centred on a weighted mix of x and zₜ.

|  | Green: q(zₜ₋₁ \| zₜ, x) | Blue: p(zₜ₋₁ \| zₜ, w) |
| --- | --- | --- |
| Needs the clean data x? | yes | no |
| Learned? | no: an exact formula | yes: network weights w |
| Available when? | only for training data, where x is known | always, including when making new data |
| Role | the answer key | the student |

Green is exact but useless for generating, because a new sample has no x yet. Blue is usable but has to be learned. **Training makes blue imitate green, averaged over all the training data** ({ref}`next section <diffusion-training>`). Why not compute the way back without x directly? Because q(zₜ₋₁ | zₜ) averages over every clean reading that could have produced zₜ, which means knowing the whole distribution of the data: the very thing we want to learn.

Almost every exact reverse step is tiny. For the worked example at t = 500, the green step puts 99.5% of its weight on z₅₀₀ and 0.4% on x, and moves the reading by less than 0.1 mph (plus a random spread of about 1.2–1.3 mph). Undoing the noise takes the whole chain of 1,000 steps.

```{figure} ../_static/figures/DB_Two_Halves.png
:alt: Top row: test heatmap 224 getting noisier from t = 0 to t = 1,000. Bottom row: a new heatmap appearing from static as the trained network removes noise
:width: 100%

A fixed recipe adds noise; a trained network removes it. Top: test heatmap 224, the example of 4.8. Bottom: a new heatmap made from fresh static.
```

The same two halves on the course heatmaps: the red chain on top (fixed), the blue chain below (learned), which turns fresh static into a new heatmap.

:::{admonition} Going deeper &mdash; the green step exactly
:class: dropdown
Bayes’ rule combines the forward step q(zₜ | zₜ₋₁) with the jump q(zₜ₋₁ | x); both are bells, so the result is a bell: q(zₜ₋₁ | zₜ, x) = N(mₜ, σₜ² I), with mₜ = \[√αₜ₋₁ βₜ / (1 − αₜ)\] x + \[√(1 − βₜ) (1 − αₜ₋₁) / (1 − αₜ)\] zₜ and σₜ² = βₜ (1 − αₜ₋₁) / (1 − αₜ). At t = 500 the two weights are 0.0044 and 0.9954, and σₜ = 0.056 in standardized units. Bishop & Bishop, Section 20.2.
:::


(diffusion-training)=
## Training the decoder: learn to name the noise

Training never runs the 1,000-step chain. It takes one clean reading, jumps to a random step in one go, mixes in static it drew itself, and asks the network to name that static. You know the right answer because you made it.

```{figure} ../_static/figures/DB_Training_Loop.png
:alt: Eight boxes in a loop: 1 clean reading x, here (70, 18) mph; 2 pick a step t at random, here 500; 3 draw static epsilon, here (-0.59, 0.63); 4 mix them with the jump formula, here z_t = (0.21, -0.49); 5 the network sees z_t and t and outputs g(z_t, w, t), the only learned box; 6 score the guess, loss = squared length of g minus epsilon, with a dashed arrow from box 3 marked the answer key; 7 nudge the weights w by backpropagation; 8 repeat with a new reading, t and epsilon.
:width: 100%

One round of training: eight steps, and only step 5 learns.
```

Only box 5 learns. Boxes 1 to 4 build a training example for free, and boxes 6 and 7 are ordinary network training from Module 1.

**The algorithm.** Bishop & Bishop’s Algorithm 20.1, in plain steps:

```text
Training (Bishop & Bishop, Algorithm 20.1)
Input:  training data {x}; noise schedule β₁, …, β_T
Output: network weights w

for t = 1, …, T: αₜ = (1 − β₁)(1 − β₂)⋯(1 − βₜ)
repeat
    x ← a clean example from the training data
    t ← a step drawn at random from 1, …, T
    ε ← fresh static from a standard bell N(0, I)
    zₜ ← √αₜ · x + √(1 − αₜ) · ε        # jump to step t
    L(w) ← ‖g(zₜ, w, t) − ε‖²           # score the guess
    one optimizer step on w to lower L(w)
until the loss stops falling
return w
```

Line by line: the αₜ values are fixed numbers, worked out once from the schedule before training starts. Each pass of the loop draws three random things (a training example, a step, a static draw) and builds the noisy latent with the jump formula of {ref}`the math section <diffusion-math>`. The network g sees only zₜ and t, and is graded on its guess of ε. In practice each pass uses a batch: the 2-D model took 512 readings per pass, the heatmap model 64 heatmaps.

**The loss.**

$$
\mathcal{L}(w) \;=\; \big\lVert\, g(z_t, w, t) - \epsilon \,\big\rVert^2
$$

| Symbol | What it is here |
| --- | --- |
| ε | the static you drew: the answer key |
| g(zₜ, w, t) | the network’s guess of that static, from the noisy latent zₜ and the step t |
| w | the network’s weights, the only thing that learns |
| L(w) | the squared error, averaged over many examples, steps and static draws |

*In words:* the network is graded on how well it names the noise that was mixed in.

**Why this loss? From “imitate green” to “name the noise”.** {ref}`The picture of three arrows <diffusion-arrows>` set the goal: the learned blue step p(zₜ₋₁ | zₜ, w) should imitate the exact green step q(zₜ₋₁ | zₜ, x). Three short moves turn that goal into the loss above.

1. *Match the centres.* Both steps are bells whose spreads are fixed in advance, so the only thing training can change is blue’s centre. Making blue match green means making blue’s centre match green’s. Bishop & Bishop derive this from the evidence lower bound, the same bound that trained the VAE: it splits into one term per step (plus a reconstruction term at the last step), and each term measures how far blue is from green.
2. *Write green’s centre with the noise.* Green’s centre is a mix of x and zₜ. The jump formula says x = (zₜ − √(1 − αₜ) ε) / √αₜ. Swap that in, and green’s centre becomes (1 / √(1 − βₜ)) · (zₜ − βₜ / √(1 − αₜ) · ε). Everything in it is known when you generate, except ε: the noise that was mixed in.
3. *Give blue the same form, with a guess of the noise.* Blue’s centre is the same expression with the network’s guess g in place of ε:

$$
\mu(z_t, w, t) \;=\; \frac{1}{\sqrt{1-\beta_t}} \left( z_t \;-\; \frac{\beta_t}{\sqrt{1-\alpha_t}}\; g(z_t, w, t) \right)
$$

Now the squared distance between the two centres is ‖g − ε‖² times a number that depends only on the step t (in the bound, about 0.50 at t = 1, 0.003 at t = 500 and 0.01 at t = 900). Ho et al. (2020) dropped that number, which gives every step the same weight, and found that this gave better-looking samples (at the cost of a slightly worse likelihood score). That leaves the loss above. For the worked example at t = 500, green’s centre written both ways (with x, or with ε) comes to (0.213, −0.494): the swap in move 2 is exact.

So the loss is not an arbitrary choice. A network that names the noise well makes a blue step whose centre matches the green one, at every step.

**Why it is a useful learning signal.**

- *The answer is exact and free.* You drew ε, so every example comes with its label. No one annotates anything.
- *One reading becomes endless questions.* Each reading gives a different question at every step t and with every static draw, so 6,624 May readings never run out of fresh training pairs.
- *It is cheap.* The jump formula makes zₜ directly, so one example costs one network pass. The 1,000-step chain is never run in training.
- *It is plain regression.* Squared error against a known target, as in Module 1. Unlike the VAE, there is no encoder to train and no KL term to balance, because the encoder is fixed.

**Why naming the noise teaches denoising.** Rearrange the jump formula with the guess g in place of ε, and you get a guess of the clean data: x̂ = (zₜ − √(1 − αₜ) g) / √αₜ. Naming the noise and recovering the clean data are the same task. This is the denoising autoencoder of {doc}`4.6 <notes2e-copying>` with two changes: the noise runs from almost none to pure static, and the network is told the step t. A diffusion decoder is a denoising autoencoder trained at 1,000 noise levels at once.

**Worked example: one training pair.** From {ref}`the worked example <diffusion-math>`, the input is z₅₀₀ = (0.21, −0.49) with t = 500, and the answer key is ε = (−0.59, 0.63).

- Before training, the network guesses g = (0.14, −0.33). L = (−0.59 − 0.14)² + (0.63 + 0.33)² = 0.53 + 0.92 = 1.45.
- After training (12,000 passes of 512 May readings, 30 seconds on 2 CPU threads), it guesses g = (0.31, −0.52). L = (−0.59 − 0.31)² + (0.63 + 0.52)² = 0.81 + 1.32 = 2.13.

The trained network does *worse* on this one pair. Over all 6,624 May readings, though, training cut the average loss:

| Step t | Guess “no noise” (g = 0) | Network before training | After training |
| --- | --- | --- | --- |
| 100 | 2.00 | 1.94 | 1.11 |
| 500 | 2.00 | 1.00 | 0.61 |
| 900 | 2.01 | 0.05 | 0.05 |

Guessing zero scores about 2, because ε holds two numbers with spread 1 each. The untrained network already scores well at t = 900, and that is not learning: at t = 900 the latent is 99% static (noise multiplier 0.988 in the schedule table), and the course network’s output format (v, in the Going deeper box below) starts out close to “the latent is all noise”. Training pays off where the latent still carries a signal, at t = 100 and t = 500. Do not compare losses across steps, though: an error in the clean-data guess x̂ shows up in the noise guess multiplied by √αₜ / √(1 − αₜ), which is 5.9 at t = 100 but only 0.16 at t = 900. At t = 900 a guess that is far off in mph still names the noise almost perfectly, because the latent is almost all noise. Why the one pair got worse, and why the average loss stays well above zero, is the most important idea on this page.

**The guess is an average.** For our pair, the trained network’s guess of the clean reading, x̂, is about (50, 45) mph, not (70, 18). Thousands of May readings could have produced the noisy point (55, 37) at t = 500. With squared error, the best single answer to a question with many right answers is their average, so the network answers with the average of those readings. That is also why the loss cannot reach zero: when several clean readings fit zₜ, the noise that was mixed in cannot be pinned down.

```{figure} ../_static/figures/DB_Guess_2D.png
:alt: Scatter of all May readings with the 16:30 reading marked; arrows from its noisy versions at t = 900, 500, 300 and 100 to the best guess at each level, plus a table of the guesses and how many readings each averages
:width: 100%

The best guess of the clean reading is an average: the 16:30 reading (gold star) noised to several levels; each arrow ends at the best possible guess.
```

The figure noises the 16:30 reading to several levels. At each level it computes the best possible guess exactly: a weighted average of all 6,624 May readings, where readings that could more easily have produced the noisy point get more weight. At t = 900 the average spans essentially all of them. At t = 500 it spans about 4,700, at t = 300 about 600, at t = 100 about 77, and at t = 20 only about 11 readings, all near (70, 18). The trained network’s guesses land within 1 mph of these exact averages at every level.

This is why the decoder works in small steps. At the noisiest steps the average spans every regime; near the end it spans a handful of nearly identical readings, so it is sharp. Sampling ({ref}`next section <diffusion-sampling>`) walks down this ladder one step at a time, moving only a little toward each guess.

```{figure} ../_static/figures/DB_Guess_Heatmap.png
:alt: Six noisy versions of test heatmap 224 (top) and the course model's guess of the clean heatmap at each level (bottom), sharpening from a blurry average at t = 1,000 to a sharp front at t = 20
:width: 100%

The heatmap guess sharpens as the noise shrinks: test heatmap 224 noised to six levels (top) and the course model&rsquo;s guess of the clean heatmap (bottom).
```

The heatmap model behaves the same way. The *front* of a heatmap is its largest speed jump between neighbouring road cells: the edge where a queue begins. Over all 400 test heatmaps, the guess sharpens as the noise shrinks. At t = 1,000 the guess’s front is 16.6 mph, close to the 15.0-mph front of the heatmap you get by averaging all training heatmaps cell by cell. It reaches 31.7 mph at t = 500, 38.6 mph at t = 100 and 39.6 mph at t = 20, the same as real heatmaps. For heatmap 224 in the figure, the front goes from 15 to 39 mph, against 42 mph in the clean heatmap. A single heatmap’s front jumps around a little; the 400-heatmap average rises steadily.

**How the network knows the step.** The step t is an input, turned into a pattern of sine and cosine waves and added inside the network, so one network serves all 1,000 noise levels. The 2-D network is a small fully connected network with 58,498 weights. The heatmap network is a U-Net: a convolutional network that shrinks the 20 × 20 heatmap to 5 × 5 and grows it back. It has 765,153 weights and was trained for 10,000 passes of 64 heatmaps (68 minutes on 2 CPU threads).

:::{admonition} Going deeper &mdash; why naming the noise means finding the average, and the v output
:class: dropdown
With squared error, the best possible guess of anything is its average given what you see: the conditional mean from the {doc}`warm-up page <notes2a-gaussians>`. So the best g is the average noise given zₜ, and through the jump formula that is the same as the average clean reading given zₜ. In the figure, each May reading x gets a weight proportional to exp(−‖zₜ − √αₜ x‖² / (2(1 − αₜ))): how likely that reading, noised to step t, is to land on zₜ. With the weights scaled to add up to 1, “readings averaged” is 1 / Σw², the effective number of readings. Minus the noise guess, −g (the direction from zₜ toward √αₜ x̂), points uphill on the density of the noisy data at step t, a direction called the *score* (Song & Ermon, 2019; Bishop & Bishop, Section 20.3). The course models output v = √αₜ ε − √(1 − αₜ) x instead of the noise itself (Salimans & Ho, 2022), and are graded on v. That carries the same information: the noise guess is g = √(1 − αₜ) zₜ + √αₜ v̂, which is the “starts out as all noise” behaviour above when v̂ is near zero. Grading on v is the same as grading on the noise with a weight of 1/αₜ, which is larger on the noisiest steps.
:::


:::{admonition} Before you trust this result
:class: warning
*Baselines:* guessing zero noise, the untrained network, and the exact best guess (the weighted average of all May readings), which is the most any network could achieve on these data. *Split:* the losses above are measured on the May readings the network trained on, so they show what training achieved, not how well the model generalizes; {ref}`Sampling <diffusion-sampling>` and {ref}`the scorecard <diffusion-scorecard>` score the generated samples on data no model saw. *Ugly cases:* the worked pair is a queue-between reading, about 3% of May, and the trained guess for it is the middle of the May cloud. A low average loss can hide large misses on exactly the rare states an engineer cares about. And a low loss says only that one-step guesses are good: whether the samples are good must be checked separately.
:::


(diffusion-sampling)=
## Sampling: from pure noise to a new traffic state

To make a new reading or heatmap, draw fresh static z\_T and run the learned blue step from t = T down to t = 1. At each step the network names the noise in zₜ, the algorithm moves to the blue centre, and it adds a little fresh static. The bottom row of the two-halves heatmap figure in {ref}`the math section <diffusion-math>` is one such run.

**The algorithm.** Bishop & Bishop’s Algorithm 20.2:

```text
Sampling (Bishop & Bishop, Algorithm 20.2)
Input:  trained network g(z, w, t); schedule β₁, …, β_T
Output: a new sample x

z_T ← fresh static from N(0, I)              # pure noise
for t = T, …, 2:
    μ ← (zₜ − βₜ/√(1 − αₜ) · g(zₜ, w, t)) / √(1 − βₜ)
    ε ← fresh static from N(0, I)
    zₜ₋₁ ← μ + √βₜ · ε                        # step back
x ← (z₁ − β₁/√(1 − α₁) · g(z₁, w, 1)) / √(1 − β₁)
return x
```

Line by line:

- *Start.* z\_T is a fresh draw from the standard bell. {ref}`The math section <diffusion-math>` showed that the forward process carries every training example to this bell, so a fresh draw looks just like real data noised to step T.
- *Move to the blue centre.* This is the formula from {ref}`Training <diffusion-training>`: subtract a small dose of the network’s noise guess from zₜ, then scale up slightly to undo the shrink of the forward step. (The very first reverse steps are the exception: with β₁,₀₀₀ = 0.999, the step at t = 1,000 keeps only 3% of z\_T and adds fresh static of spread 1.0.) Put another way, it is a weighted mix of zₜ and the network’s clean-data guess x̂, with almost all the weight on zₜ (99.5% at t = 500, as in the green step).
- *Add fresh static.* The blue step is a bell, not a point, so the algorithm draws from it: its centre plus static of spread √βₜ.
- *Finish.* The last step adds no static. Its output is the new sample.

Each pass calls the same network once. Nothing here is learned or new: all the learning happened in training.

**A traced run.** One run of the algorithm on the 2-D detector model, all 1,000 steps. The latent zₜ is shown on the mph scale (turned back with the May mean and spread) only so that you can read it; until the last steps it is not a speed.

| Step t | Latent zₜ on the mph scale | Network’s guess of the clean reading, x̂ (mph) |
| --- | --- | --- |
| 1,000 | (15.1, 53.7) | (50.6, 47.8) |
| 900 | (57.4, 27.5) | (48.8, 46.3) |
| 700 | (30.1, 56.5) | (45.0, 43.5) |
| 500 | (47.2, 49.7) | (52.6, 50.5) |
| 300 | (53.3, 59.8) | (65.8, 66.2) |
| 100 | (68.7, 71.6) | (69.4, 70.3) |
| 1 | (69.7, 70.7) | (69.7, 70.7) |

For the first half of the run the latent jumps around while the guess stays in the middle of the May cloud, between 43 and 53 mph: the latent is mostly static, so the network can only say “somewhere in May”. Between t = 500 and t = 300 the guess commits to free flow, and by t = 100 it is within half a mph of where the run ends: (69.7, 70.7) mph, free flow at both detectors.

**Why many small steps, not one big jump.** The trained network gives a clean-data guess x̂ at any step. So why not start at t = T, take one guess and stop? Because at t = T that guess is the average of every training reading.

```{figure} ../_static/figures/DB_One_Jump_vs_Steps.png
:alt: Four scatter plots of 6,048 readings each: June 2012 real readings, one bell fitted to May, diffusion in one big jump (all draws on one spot), and diffusion in 1,000 small steps (both regimes and the queue arm)
:width: 100%

One big jump lands on the average; small steps keep every regime. Each panel: 6,048 readings of the I-405 pair; models fitted on May only.
```

All four panels are scored against June 2012, which no model saw. The three dashed boxes count the regimes: free flow at both detectors, slow at both, and the queue between them (fast upstream, slow downstream).

- **June 2012 (the target).** 54% free flow, 34% slow, 2.6% queue between.
- **One bell fitted to May** (the {doc}`warm-up page <notes2a-gaussians>`). It fills the empty gap between the regimes and nearly misses the queue arm (0.5%). It also puts 13% of its draws outside 0–80 mph.
- **Diffusion, one big jump.** 97% of the 6,048 draws land within 2 mph of (50.5, 48.5) mph, a reading this road almost never produces: only 0.4% of May readings sit within 5 mph of it at both detectors.
- **Diffusion, 1,000 small steps.** The same network, called 1,000 times: 51% free flow, 37% slow, 3.6% queue between.

**Read the two scores together.** *Looks real* is the share of generated readings that land close to some real reading. *Covers variety* is the share of real readings that have a generated reading close by. (Both scores are defined in {doc}`4.9 <notes4-gan>`. “Close” is set by neighbours. For looks real, it is the distance from a real reading to its third-nearest real neighbour. For covers variety, it is the distance from a generated reading to its third-nearest generated neighbour, so when every draw sits on one spot, that distance shrinks to almost nothing. Distances are in mph on the two detectors.) The one big jump scores 0.999 on looks real, because the average point sits next to a few real transition readings, but it covers 0.008 of the variety: every draw is the same draw. With 1,000 small steps the scores are 0.955 and 0.977, close to simply replaying the May readings (0.969 and 0.979).

This is the VAE’s blur in its purest form: a VAE decoder makes a heatmap in one pass, and one pass returns an average. Many small steps avoid it. The guess x̂ can be a blurry average, but each step moves zₜ only a little toward it, and the next step asks again with a less noisy zₜ. By the time the sample commits to a regime, the guess has become sharp: in the traced run, the guess commits between t = 500 and t = 300 and is within half a mph of the end by t = 100. You already trust this idea from traffic simulation. The CTM never jumps from the starting state to minute 10 in one formula; it takes many short, local time steps. A diffusion model also takes many small, simple steps, but along noise level instead of clock time.

(diffusion-prompt)=
**Where does the new sample come from, and where is the prompt?** Here is the puzzle. Generation starts from pure Gaussian noise, which holds no information about traffic. So how does the model know which way to go, or what kind of data to make? Image generators take a prompt (“a foggy freeway at night”), yet the training algorithm above never mentions one. The short answer: what to make is stored in the weights w, learned from the training data; the noise only supplies randomness. Three facts make this precise.

*1. The training data decide what kind of data can come out.* The network learned one thing: at each noise level, its best guess x̂ of the clean data, which is the average of the training examples that could have produced zₜ (see {ref}`Training <diffusion-training>`). Because it is an average of training readings, it never leaves the range the data span. At high noise it sits at the overall May average, which can be an empty spot (as the one big jump showed); as the noise shrinks, it moves onto real readings. Every step moves zₜ a little toward the current guess, like following a compass.

```{figure} ../_static/figures/DB_Direction_Field.png
:alt: Four panels at t = 900, 500, 200 and 50: lines from 150 noisy May readings to the network's guess of each clean reading; at t = 900 all guesses sit near the May average, at t = 50 each sits next to its own reading
:width: 100%

At every step, the network says which way the data lie: 150 May readings noised to step t (open end of each line) and the network&rsquo;s guess of the clean reading (dot).
```

At t = 900 every guess lands near the May average: the 150 guesses spread only about 4 mph, and the median distance from a guess to the true reading is 22.0 mph. As the noise shrinks the compass sharpens: 6.3 mph at t = 500, 2.7 at t = 200 and 1.3 at t = 50, where the guesses spread about 22 mph, as much as the May readings themselves. Whatever static you start from, every step pulls toward May readings on this freeway. Nobody tells the model the direction; it reads the direction off zₜ at each step. A model trained on May I-405 readings can only make readings like them.

*2. The random draws decide which sample comes out.* Training fixed what can come out; the random numbers drawn during sampling pick one sample from it. Which random numbers matter depends on the sampler. DDIM, a sampler that adds no fresh static (see “How many steps?” below), draws only the starting static z\_T, so each starting point always becomes the same reading. Run DDIM from every point of a fine grid of starting static, and colour each start by where it ends.

```{figure} ../_static/figures/DB_Static_Map.png
:alt: Left: a grid of starting static coloured by the kind of traffic each start becomes, with circles at 1 and 2 spreads and four nearby starts A to D. Right: the readings they become, with A to D marked
:width: 100%

Each patch of static becomes one kind of traffic: deterministic sampling (DDIM, 100 steps) from every point of a 241 &times; 241 grid of starting static, 2-D detector model.
```

The bell of static splits into patches, one per kind of traffic. The share of the bell that ends in each regime is close to the shares in the May readings the model learned from: 50.9% free flow at both detectors (May: 51.4%), 37.2% slow at both (May: 37.2%) and 3.5% queue between (May: 3.4%). The centre of the bell sits on the border between free flow and slow, so tiny differences decide. Neighbouring starts A to D lie only 0.14 apart, yet A ends slow (33.4, 32.5 mph), B in between (43.9, 36.7 mph: neither free flow nor slow), and C and D in free flow (60.7, 56.1 and 65.2, 66.7 mph).

The DDPM algorithm above works differently: the fresh static added at every step makes almost all of the choice. With this schedule the very first reverse step (t = 1,000) keeps only 3% of z\_T and adds new static of spread 1.0, so the start is nearly forgotten. Run DDPM 2,000 times from each of four starts, as far apart as (−2, −2) and (+2, +2), with the same fresh static along the way, and all four end in the same mix: about 50% free flow, 38% slow and 4% queue between.

Either way, the random numbers work like a seed, not like a prompt. They pick one sample, and drawn at random they give each kind of traffic about as often as the training data do.

*3. A prompt is an extra input you train with.* The model in the training and sampling sections is *unconditional*: it learns p(x), the distribution of all its training data, so no prompt appears anywhere. To control what comes out, give the network one more input c, the prompt, and train on pairs (x, c). The network becomes g(zₜ, w, t, c), and the training algorithm is unchanged, except that each example brings its own c. The course heatmap model does exactly this, with c = the three CTM settings behind each heatmap ({ref}`Steering <diffusion-steering>`). Text-to-image models do it with captions: the training data are images paired with their captions, and a text encoder turns each caption into numbers that the network reads alongside zₜ and t. The course model hides the settings for a random 20% of training heatmaps, and many text-to-image models do the same with their captions, so one network learns to answer with and without the prompt. With a prompt, the guess x̂ becomes the average of the training examples that both fit zₜ and carry that c, so every step is pulled toward, say, heavy-scenario heatmaps instead of toward all heatmaps. Guidance ({ref}`Steering <diffusion-steering>`) uses the gap between the two answers to follow the prompt more closely.

| What decides … | Unconditional model (this section) | Conditional model (Steering below; text-to-image) |
| --- | --- | --- |
| what kind of data can come out | the training data | the training data |
| which kind of state you get | the random draws (only the starting static for DDIM; mostly the fresh static along the way for DDPM) | mainly the prompt c |
| the exact sample | the random draws | the same |

So the training algorithm above is right not to mention a prompt: it trains the unconditional model. At sampling time the prompt adds no new knowledge: it picks a part of what the network learned in training. A prompt for something absent from the training data, such as an incident in a month without incidents, has nothing to pick.

(diffusion-steps)=
**How many steps?** You do not have to visit all 1,000 levels. A shortcut called DDIM (denoising diffusion implicit models; Song et al., 2021) jumps from t = 1,000 to t = 960 to t = 920 and so on. At each jump it takes the network’s clean-data guess x̂ and its noise guess g, and recombines them with the jump formula at the next, lower step:

$$
z_{t-1} \;=\; \sqrt{\alpha_{t-1}}\; \hat{x} \;+\; \sqrt{1-\alpha_{t-1}}\; g(z_t, w, t)
$$

*In words:* this is the jump formula of {ref}`the math section <diffusion-math>` with the network’s guesses in place of the unknown clean data and noise, one level lower (for a bigger jump, put the next step in place of t − 1). It adds no fresh static, so the same starting static always gives the same sample, which is what the static map above relies on. Fewer, bigger steps make each step cruder, and with very few steps the samples drift back toward the average.

```{figure} ../_static/figures/DB_Steps_Chart.png
:alt: Line chart of covers variety against the number of sampling steps on a log scale from 1 to 1,000. Both models score near 0 with 1 step; the detector pair reaches 0.92 at 10 steps and about 0.97 to 0.98 from 25 steps; the heatmap model reaches 0.73 at 5 steps and about 0.90 from 25 steps. Dashed lines mark real data scored against real data: 0.98 for the detector pair, 0.95 for the heatmaps.
:width: 100%

Covers variety against the number of sampling steps (6,048 samples per step count for the detector pair, 400 heatmaps for the heatmap model).
```

With one step both models collapse to the average. With 5 steps they already cover most of the variety, and by 25 steps they are at or near their best, close to the ceiling set by real data scored against real data (the dashed lines).

```{figure} ../_static/figures/DB_Steps.png
:alt: Six rows of five heatmap samples drawn with 1, 2, 5, 10, 25 and 1,000 steps; 1 and 2 steps give blurry averages, 25 and 1,000 steps give sharp queues
:width: 100%

Fewer steps give blurrier samples; about 25 steps already match 1,000. The course diffusion model, no settings given: the first five of 400 samples drawn with each number of steps.
```

**The price is time.** One sample takes one network pass per step (two with guidance; see {ref}`Steering <diffusion-steering>`). On 2 CPU threads the course model makes 400 heatmaps in 0.8 s with 1 step, 22 s with 25 steps and 898 s (15 minutes) with all 1,000. A VAE makes a sample in one decoder pass. For 400 small heatmaps this hardly matters; for a city-wide network over a day, or for a video, it does.

:::{admonition} Going deeper &mdash; the samplers in the course code
:class: dropdown
The algorithm above is DDPM (denoising diffusion probabilistic models; Ho et al., 2020), with fresh static at every step. The course code computes the same blue centre from the clean-data guess x̂, clipped to the physical speed range (the same formula rearranged, which avoids multiplying by 1/√(1 − βₜ) = 31.6 at t = 1,000), and uses the green step’s spread σₜ (the going-deeper box in {ref}`the math section <diffusion-math>`) instead of √βₜ; Ho et al. found the two choices work about equally well. DDIM drops the fresh static. The course heatmap model adds fresh static at every step count; the detector-pair sweep uses DDIM below 1,000 steps and DDPM at all 1,000 (the traced run and the 1,000-step panel of the one-jump figure), and the static map uses DDIM with 100 steps. Both samplers reach the same family of samples. Bishop & Bishop, Sections 20.2–20.3.
:::


:::{admonition} Before you trust this result
:class: warning
*Baselines:* one bell fitted to May, and May replayed as is (a perfect copy machine, the ceiling for the 2-D test); for heatmaps, real data scored against real data. *Split:* every 2-D model is fitted on the 23 May weekdays and scored on the 21 June weekdays, later days it never saw. *Ugly cases:* the queue arm is only about 3% of readings, and the model comes close to May’s share (3.6% vs 3.4%), a bit above June’s 2.6%. The static map and the compass figure exist only because this model is 2-D; for a 400-cell heatmap you cannot draw them, and you check what comes out by scoring the samples ({ref}`next section <diffusion-scorecard>`). This is one detector pair on one freeway for two months, and each sample is a single 5-minute reading with no time order.
:::


(diffusion-scorecard)=
## How good are the samples? Diffusion and the VAE on the same heatmaps

Scored against the same 400 test heatmaps, diffusion’s samples come close to real data on both scores (0.958 looks real, 0.900 covers variety). The 2-latent VAE’s samples look real (0.998) but cover only 0.085 of the variety. Diffusion pays for this with 25 to 1,000 network passes per sample, against one for the VAE.

**Why the VAE blurs and diffusion does not.** A VAE makes a new heatmap in one pass of its decoder. When several training heatmaps get almost the same latents, that pass returns their average ({ref}`4.8, Where it breaks <vae-basics-breaks>`), and queues that start in different places average into a smear. Diffusion makes each heatmap in many small steps, each moving only a little toward the current guess. By the time a heatmap commits to a queue, the guess has become sharp (see {ref}`Training <diffusion-training>` and {ref}`Sampling <diffusion-sampling>`), so its fronts stay sharp.

```{figure} ../_static/figures/DB_VAE_vs_Diffusion.png
:alt: Three rows of four speed heatmaps: real test heatmaps, VAE samples and diffusion samples, with the front of each
:width: 100%

The VAE softens the queue fronts; diffusion keeps them sharp. Same 4-mile road; in each row, the first 4 of 400 heatmaps with a queue over a tenth of the cells.
```

| Generator | Looks real | Covers variety | Front (mph) | Median distance to the nearest training heatmap (mph) |
| --- | --- | --- | --- | --- |
| Real heatmaps (the reference) | 0.945 | 0.953 | 39.6 | 3.93 |
| VAE, 2 latents (β = 0.6) | 0.998 | 0.085 | 22.5 | 4.44 |
| VAE, 8 latents | 0.995 | 0.453 | 26.2 | 4.69 |
| Diffusion, 1,000 steps | 0.958 | 0.900 | 39.2 | 3.97 |

Each generator made 400 samples. Distances are root-mean-square (RMS) speed differences per cell, on the course’s 3-mph grid. In the reference row, the two scores compare the 400 validation heatmaps with the 400 test heatmaps; the front and nearest-training distance are those of the test heatmaps. With 25 steps instead of 1,000, diffusion scores 0.963 and 0.907, with a 39.5-mph front ({ref}`How many steps? <diffusion-steps>`).

**Read the table.**

- **Fronts.** The VAE’s fronts are about 17 mph softer than real ones. Diffusion’s are within 0.4 mph.
- **Looks real against covers variety.** The VAE plays safe. Its samples are plausible, average-looking heatmaps, so almost all of them look real, but they bunch in the middle and miss most of the variety: 0.085 with 2 latents, 0.453 with 8. Diffusion gives up a little on looks real (0.958, about the level of real heatmaps) and gains a lot on variety (0.900).
- **Nearest training heatmap: is it copying?** A generator that replays its training data sits much closer to the training heatmaps than new real heatmaps do. Diffusion’s median is 3.97 mph against 3.93 for real test heatmaps, so there is no wholesale copying. Look closer, though: 7% of its samples (28 of 400) sit within 0.42 mph of a training heatmap, against 5% of real test heatmaps. All 28 are plain free-flow heatmaps with no cell below 30 mph, and plain free flow matches many training heatmaps without any copying. So this check finds no sign that heatmaps with queues are being copied. With little data, copying does happen: in the longer handout *Deep Generative Models: VAE and Diffusion*, a diffusion model trained on one dashcam clip replayed training frames in 4 of 32 samples.

**It learns the training mix, not the test mix.** 57% of diffusion samples have a queue over a tenth of their cells, the same as the 3,200 training heatmaps (56.5%). The 400 test heatmaps happen to be lighter (48%). Average speeds: training 48.8 mph, diffusion 48.5 mph, test 51.3 mph. A generator should do exactly this. It is also a warning: it learns your training data’s mix of conditions, gaps and biases included. A diffusion model trained on a month without incidents will not invent incidents.

:::{admonition} Before you trust this result
:class: warning
*Baselines:* the VAE with 2 and with 8 latents, and real heatmaps scored the same way (the ceiling). *Split:* every model was trained on the 3,200 training heatmaps and scored against 400 test heatmaps it never saw; the reference row uses the 400 validation heatmaps. *Ugly cases:* everything here is simulated (the CTM on one 4-mile road), so “looks real” means “looks like this simulator”. The two scores use a nearest-neighbour rule on RMS speed (Kynkäänniemi et al., 2019), which ignores where in the heatmap the differences sit. 400 samples per model is enough to rank these generators, not to split hairs between 0.900 and 0.907.
:::


(diffusion-steering)=
## Steering the generator: scenarios, guidance and filling gaps

A trained diffusion model can do more than draw random traffic. Tell it the conditions and it draws that scenario. Show it the cells you observed and it fills in the rest, with no retraining.

**Ask for a scenario.** During training, the heatmap model also saw the three CTM settings behind each heatmap: starting density, upstream inflow and bottleneck capacity. For a random 20% of training heatmaps, those settings were hidden, so the same network learned to work with them and without them. To ask for a scenario, you hand it the settings along with the static.

```{figure} ../_static/figures/DB_Steer.png
:alt: Three rows of four heatmaps: fresh CTM runs with the heavy settings, diffusion samples given the heavy settings, and diffusion samples with no settings
:width: 100%

Given the settings, diffusion draws the scenario you asked for. &ldquo;Heavy&rdquo;: 35% of jam density at the start, inflow at 90% of capacity, bottleneck at 30% of capacity.
```

Asked for the heavy scenario (35% of jam density at the start, inflow at 90% of capacity, bottleneck at 30% of capacity), the model’s samples have 55.3% of cells below 30 mph. 400 fresh CTM runs with the same settings have 56.8%. Without the settings, the model draws the general mix (34.5%). Scored against the fresh CTM runs, the conditioned samples look real 0.833 and cover 0.83 of the variety. A second batch of CTM runs scores 0.863 and 0.91 against the first, which is the ceiling. For a moderate scenario (20%, 75% and 55%) the match is closer still: 5.3% of cells below 30 mph in both, and average speeds of 66.9 mph (diffusion) against 67.1 mph (CTM). These samples used 100 steps. The settings do not say where the bottleneck starts or how long it lasts, so one setting describes a family of heatmaps, not one heatmap.

**Guidance: turn the condition up.** *Classifier-free guidance* (Ho & Salimans, 2021) asks the network twice at every step, once with the settings and once without. It then pushes the guess further in the direction the settings point: g = g\_without + (1 + λ)(g\_with − g\_without), where g is the network’s noise guess. The guidance strength λ is a number you choose. (It is “classifier-free” because it needs no separate classifier network.)

| Heavy scenario | Looks real | Covers variety | Spread of the queue share across samples |
| --- | --- | --- | --- |
| Diffusion, λ = 0 | 0.833 | 0.830 | 0.125 |
| Diffusion, λ = 1 | 0.900 | 0.698 | 0.086 |
| Diffusion, λ = 3 | 0.920 | 0.557 | 0.071 |
| A second batch of CTM runs (the ceiling) | 0.863 | 0.910 | 0.087 |

The *queue share* is the share of a heatmap’s cells below 30 mph; its spread is the standard deviation across the 400 samples. Stronger guidance makes the samples more typical of the scenario and less varied. At λ = 0 the queue share spreads more than in the CTM (0.125 against 0.087), so some samples drift from the scenario. At λ = 1 the spread matches, but the variety drops to 0.698. No single λ matches the CTM on every column. For a stress test you want the variety (λ = 0). For “show me a typical heavy day” you might turn it up.

**Fill a gap.** Before the network looks at each step, overwrite the cells you observed with the real observation, noised to that step’s level. The network then fills the rest so that it roughly fits what you saw. The fills use all 1,000 steps. This is the *replacement* method: the model needs no retraining and never saw a gap during training. RePaint (Lugmayr et al., 2022) is a refined version of the same idea.

```{figure} ../_static/figures/DB_Fill.png
:alt: Heatmap 224: the truth, the view with road cells 8 to 11 hidden, linear interpolation across the gap, and two diffusion fills
:width: 100%

Filling a detector outage without retraining: heatmap 224 with road cells 8&ndash;11 (0.8 mi) dark the whole time.
```

| Gap (50 test heatmaps, 8 fills each) | Classical baseline | Baseline error (mph) | Average of 8 fills (mph) | Fill wins on |
| --- | --- | --- | --- | --- |
| Outage: road cells 8–11 (0.8 mi) dark for all 9.6 minutes | linear interpolation between the neighbouring road cells | 5.16 | 2.34 | 41 of 50 |
| Next 3.8 minutes: time steps 12–19 unknown | persistence: the last observed time step carried forward | 17.66 | 9.55 | 43 of 50 |

Errors are RMS speed differences over the hidden cells. On heatmap 224 the outage error is 7.1 mph for interpolation and 1.8 mph for the averaged fills. (The longer *Deep Generative Models* handout reports 2.03 and 9.12 mph for the same two gaps; it used an earlier, smaller diffusion model.)

The spread of the 8 fills is a built-in uncertainty estimate. If the spread were honest, the truth would land inside the range of 8 fills about 78% of the time (7 in 9). On cells below free flow, it lands inside 88.7% of the time for the outage. That spread is a little too wide, so it is cautious, and the misses fall evenly on both sides (5.6% of cells slower than every fill, 5.2% faster). For the next 3.8 minutes it lands inside 88.6% of the time, but the misses lean one way: the truth is slower than every fill on 9.7% of cells and faster on only 1.6%. On average these fills run 3.2 mph too fast, so the forecast tends to underestimate congestion. (Free-flow cells are left out of this check, because truth and fills tie at 75 mph.)

:::{admonition} Before you trust this result
:class: warning
*Baselines:* linear interpolation and persistence are the first things an agency would try, not the strongest. A stronger classical method, such as the adaptive smoothing method of {doc}`4.6 <notes2e-copying>` or a Kalman filter, was not run here, so treat the margins as upper bounds. *Split:* the 50 test heatmaps were never seen in training. *Ugly cases:* the data are simulated and the gaps are tidy blocks. The scenario settings exist only because a simulator made the data. Real detector data carry no such labels, so you would condition on what you can measure, such as time of day, weather or an incident flag.
:::


(diffusion-breaks)=
## Where it breaks

Diffusion fixes the VAE’s blur, not its other limits. It learns only what its training data hold, it is slow, it can copy when data are scarce, and nothing in it knows traffic physics.

1. **It cannot invent what the data never showed.** A diffusion model learns the training distribution, mix and all ({ref}`the scorecard <diffusion-scorecard>`). Trained on everyday traffic, it will not produce a credible crash, an incident on a road that never had one, or a hurricane evacuation. Steering ({ref}`above <diffusion-steering>`) changes how often a kind of sample appears, not what the model knows. Do not wait years for crashes to pile up, but do not just sample more either. Use physics, sample rare cases on purpose and correct for doing so, and use real crash records (see *Generating Crash Data from Near-Misses*).
2. **It is slow.** One sample costs one network pass per step: 898 s for 400 small heatmaps with all 1,000 steps on 2 CPU threads. Fewer steps ({ref}`How many steps? <diffusion-steps>`) cut that 40-fold here. For large outputs, such as a city-wide network or a video, people run the diffusion on an autoencoder’s compact latents instead of the raw data. Those latents are still a small grid (for example 64 × 64 × 4 numbers for a 512 × 512 image), not two numbers. This is *latent diffusion* (Rombach et al., 2022), the idea behind Stable Diffusion.
3. **It can copy, most of all with little data.** The best possible guess of {ref}`Training <diffusion-training>` is a weighted average of the training readings, and at very low noise it snaps to the nearest one. A network that matched it everywhere would only replay its training set. Real networks make new samples because they cannot match it exactly; with little data they come closer. Evidence: the dashcam replays in the longer *Deep Generative Models* handout. The heatmap model here shows no sign of copying heatmaps with queues ({ref}`the scorecard <diffusion-scorecard>`).
4. **It knows no physics.** Nothing in the loss conserves vehicles or keeps flow and density on the fundamental diagram. The samples look like CTM output only because the training data were CTM output. The course models clip each clean guess to a physical speed range; without such rules a sample can hold impossible values. Some research models add a physics step to the sampler: PMA-Diffusion (Transportation Research Part C, 2026) adds a traffic smoothing step.
5. **There are no latents to read.** A VAE at least has a few latents (the “knobs” of {doc}`4.7–4.8 <notes3b-vae-basics>`). A diffusion model’s latents are the noisy data themselves, as large as the data, and nothing in them is a cause or a parameter you can interpret. To learn which factors drive pedestrian–AV conflicts, a generator is the wrong tool (the longer *Deep Generative Models* handout explains why).
6. **Good scores can mislead.** Looks real and covers variety measure distance to real data, not correctness. The one big jump scored 0.999 on looks real ({ref}`Sampling <diffusion-sampling>`). Read both scores together, and add a physics or domain check.

:::{admonition} Before you trust any diffusion result in your project
:class: warning
1. Score the samples against held-out real data the model never saw, on both looks real and covers variety.
2. Run the copying check: the distance from each sample to its nearest training example, against the same distance for new real data.
3. Run a physics check: speeds in range, queue fronts that travel upstream at a plausible wave speed (15 mph in this CTM), flow and density near the fundamental diagram.
4. Compare the mix of conditions in the samples with the data, and ask whether the data’s mix is the one you need.
5. Beat a simple baseline: a bell or mixture of bells, interpolation, or the simulator itself.
:::


(diffusion-fit)=
## Fit card and applications

Reach for diffusion when you need many sharp, varied, realistic samples of something you have lots of data on, or need to fill gaps in it. Keep the simulator or the classical estimator when it already answers the question.

**Fit card — Diffusion model**

- **Idea in one sentence:** learn to remove a little noise at a time; to generate, start from static and remove noise step by step.
- **Why it works (the logic):** each small step moves only a little toward the network’s current guess, and by the time a sample commits to one kind of state the guess has become sharp, so the result stays sharp and varied; the training labels are free because you add the noise yourself.
- **Fits these tasks:** synthetic traffic states and test scenarios, filling detector or camera gaps, sets of possible futures for short-term prediction, extra examples of rare classes for perception. Leverage labels: *generation*, *prediction*.
- **Needs this data:** thousands of examples of the same shape (speed heatmaps, trajectories, images). No labels are needed to generate; condition labels (scenario settings, time of day, weather) only to steer. Agencies (detector archives), AV fleets and simulators have such data.
- **Breaks when:** data are few (it copies), the target lies outside the data (crashes, a road it never saw), speed matters (tens to a thousand passes per sample), or physics must hold exactly.
- **Keep the classical method when:**
  - a calibrated simulator (CTM, SUMO) already answers the question;
  - you need one best estimate, not a set of possibilities (interpolation, adaptive smoothing, a Kalman filter);
  - you need interpretable causes (regression, discrete choice);
  - a written rule already catches a known failure.

**The three models side by side**, on the course heatmaps:

|  | Autoencoder | VAE | Diffusion |
| --- | --- | --- | --- |
| What the latents are | a few numbers per heatmap | a few numbers, pulled toward a standard bell | the noisy heatmap itself (400 numbers) |
| How it makes a new heatmap | not by design | draw latents from the bell, decode once | draw static, denoise 25 to 1,000 times |
| Samples (looks real / covers variety) | 0.910 / 0.212, with a bell fitted to its latents afterwards ({ref}`4.8 <vae-basics-cannot-generate>`) | 0.998 / 0.085 with 2 latents | 0.958 / 0.900 |
| Cost per sample | one decoder pass | one decoder pass | 25 to 1,000 network passes |
| Best at | compressing, cleaning, flagging the unusual | a smooth, small summary you can walk through | sharp, varied samples, scenarios and gap filling |

**Applications in transportation.**

| Domain | Task | Data it needs | Classical baseline | Example |
| --- | --- | --- | --- | --- |
| Traffic operations (agency TSM&O) | Fill missing detector speeds across a network | loop or radar speeds, months of archive | interpolation, adaptive smoothing, Kalman filter | [PriSTI](https://arxiv.org/abs/2302.09746) (Liu et al., 2023), tested on METR-LA and PEMS-BAY speeds |
| Traffic flow | Estimate the full speed field of a corridor from sparse detectors and probe vehicles | trajectory-grade data such as I-24 MOTION | adaptive smoothing, traffic flow models | [PMA-Diffusion](https://arxiv.org/abs/2512.06183) (Liu, Jin & Choi, Transportation Research Part C, 2026): beats its baselines at 5% visibility |
| Driving automation and ADAS | A set of possible futures for nearby vehicles, for planning | logged trajectories (e.g., Waymo Open Motion) | constant-velocity or kinematic prediction | [MotionDiffuser](https://arxiv.org/abs/2306.03083) (Jiang et al., CVPR 2023) |
| Road safety and AV testing | Controllable traffic scenarios, e.g., “make the lead car cut in” | logged scenarios plus rules to steer by | scripted scenarios in a simulator | [CTG](https://arxiv.org/abs/2210.17366) (Zhong et al., ICRA 2023) |
| Asset management and disaster response | More examples of rare damage classes (potholes, storm damage) | a small labelled image set | collect more images, copy-and-paste augmentation | RoadFusion and post-disaster image editing (*Generative Models in Transportation* applications handout) |

For each of these, the *Generative Models in Transportation* applications handout gives the catch and a “Before you trust it” box.

(diffusion-summary)=
## Summary and practice

**Diffusion in seven lines.**

1. A diffusion model is a latent-variable model with two halves: a fixed encoder that adds noise step by step, and a learned decoder that removes it step by step.
2. Like the VAE’s, the encoder is a distribution, not a point: zₜ = √αₜ x + √(1 − αₜ) ε, and at t = T every input has become the same standard bell.
3. The exact way back, q(zₜ₋₁ | zₜ, x), needs the clean data. The learned step p(zₜ₋₁ | zₜ, w) imitates it without x, and matching the two comes down to one plain loss, ‖g(zₜ, w, t) − ε‖²: name the noise you mixed in. Labels are free, and naming the noise is the same as denoising.
4. The network’s best guess of the clean data is an average of everything that fits zₜ: broad at high noise, narrow at low noise.
5. So one big jump lands on the overall average (blur), and many small steps keep every regime sharp.
6. Sampling starts from fresh static and repeats the learned step. The training data decide what can come out, the random draws decide which sample, and a prompt is an extra input that has to be trained in. About 25 steps were enough here, but every sample still costs many network passes.
7. Diffusion learns its training data’s distribution. It can steer and fill gaps, but it cannot invent crashes it never saw, and it knows no physics.

### Label the picture

Name each blank in one or two words, then say in one sentence what it does.

```{figure} ../_static/figures/DB_Label_Picture.png
:alt: A diagram with six blanks: box A, for example (70, 18) mph, leads through arrow B to the noisy latent z_t at step t, which leads with more noise to box C at t = 1,000. From z_t an arrow leads down to box D, whose input is z_t and t; D leads to box E, its output, which leads to box F, used during training only.
:width: 100%

Fill in the blanks: what each part of a diffusion model does.
```

:::{admonition} Answers
:class: dropdown
A: the clean data x, here one clean reading. B: add noise, the fixed encoder: z&#8348; = &radic;&alpha;&#8348; x + &radic;(1 &minus; &alpha;&#8348;) &epsilon;.
C: pure static z_T: no trace of the reading is left. D: the denoiser network g(z&#8348;, w, t), the only learned part.
E: its guess of the noise, g (equivalently, its guess of the clean data, x&#770;). F: the loss, &#8214;g &minus; &epsilon;&#8214;&sup2;, which compares the guess with the static that was actually added.
:::

### Check yourself

There is no single right answer to the first eight; each asks for a judgment you could defend to an engineer.

1. Your district has 18 months of 5-minute speeds from 300 detectors, and 6% of the readings are missing because of outages. A colleague proposes a diffusion model to fill the gaps. Which baseline would you run first, how would you split the data so the comparison is honest, and what would make you distrust the fills?
2. A consultant shows 10,000 diffusion-made crash scenarios for an intersection with no recorded crash in five years. The model was trained on two years of the intersection’s near-miss video. Would you use the scenarios to estimate its crash frequency? What would you ask for first?
3. You need 50,000 realistic corridor speed heatmaps to stress-test a ramp-metering algorithm, and you already have a calibrated CTM of the corridor. Would you train a diffusion model? Why or why not?
4. Your diffusion model’s samples score 0.99 on looks real and 0.20 on covers variety. What is the likely cause, and what would you change?
5. A diffusion model trained on 300 dashcam clips from one city makes samples that sit closer to a training clip than new real clips do. What does that tell you, and why does it matter for privacy and for testing?
6. A traffic management center wants a gap-filled speed map of 2,000 detectors every 30 seconds on one server. What would you measure before choosing diffusion, and what are your options if it is too slow?
7. You want to know which factors make AV–pedestrian conflicts more severe at mid-block crossings. A classmate suggests training a diffusion model on the video and reading the factors from it. What would you suggest instead, and why?
8. A classmate says: “The model starts from pure random noise, so the course’s freeway heatmap model could also make an arterial heatmap with traffic signals, if we just found the right starting noise.” Is that right? What would you need in order to get arterial heatmaps on request?
9. (This one has a single answer.) Noise the worked example of {ref}`the math section <diffusion-math>`, x = (0.89, −1.33) with ε = (−0.59, 0.63), to step t = 900 instead of 500, using the schedule table. What is z₉₀₀? About where would the trained network’s guess of the clean reading land, and why?

### Where to go next

- The longer handout *Deep Generative Models: VAE and Diffusion*: the 1-D detector experiment, and real dashcam and FL511 camera cases.
- The forward-diffusion and decoder-training labs ({doc}`all labs <../labs>`): build the noise schedule and train a small denoiser yourself.
- *Generating Crash Data from Near-Misses*: why sampling a generator is not enough for rare events, and what to do instead.
- *Generative Models in Transportation* (applications handout) and the {ref}`reading library <generative-reading-library>` on the Module 4 page.
- The {ref}`diffusion papers companion <diffusion-papers-library>` on the Module 4 page: this page&rsquo;s recipe inside 35 transportation papers, each with its architecture figure and how it is trained, sampled and steered.
- The {ref}`unCLIP crash companion <unclip-crash-run>` on the Module 4 page: the three unCLIP steps (pair, decoder, prior) run on the course crash narratives and sketches, with every result and three problems worth knowing.
- The {ref}`knowledge-guided diffusion companion <knowledge-guided-diffusion>` on the Module 4 page: five doors where transportation knowledge can enter a diffusion model (what it generates, the condition, guidance, values held fixed, checks), what your data must contain for each, and a worked test on four loop detectors.
- Bishop & Bishop, *Deep Learning: Foundations and Concepts* (2024), Chapter 20.

## References for 4.11

- Bishop, C. M., & Bishop, H. (2024). [*Deep Learning: Foundations and Concepts*](https://www.bishopbook.com/), Chapter 20, Diffusion Models (Sections 20.1–20.4). Springer.
- Sohl-Dickstein, J., et al. (2015). [Deep unsupervised learning using nonequilibrium thermodynamics](https://arxiv.org/abs/1503.03585). ICML.
- Ho, J., Jain, A., & Abbeel, P. (2020). [Denoising diffusion probabilistic models](https://arxiv.org/abs/2006.11239). NeurIPS.
- Song, Y., & Ermon, S. (2019). [Generative modeling by estimating gradients of the data distribution](https://arxiv.org/abs/1907.05600). NeurIPS.
- Song, J., Meng, C., & Ermon, S. (2021). [Denoising diffusion implicit models](https://arxiv.org/abs/2010.02502). ICLR.
- Nichol, A., & Dhariwal, P. (2021). [Improved denoising diffusion probabilistic models](https://arxiv.org/abs/2102.09672). ICML. (The cosine schedule.)
- Salimans, T., & Ho, J. (2022). [Progressive distillation for fast sampling of diffusion models](https://arxiv.org/abs/2202.00512). ICLR. (The v output.)
- Ho, J., & Salimans, T. (2021). [Classifier-free diffusion guidance](https://arxiv.org/abs/2207.12598). NeurIPS 2021 Workshop on Deep Generative Models and Downstream Applications.
- Lugmayr, A., et al. (2022). [RePaint: Inpainting using denoising diffusion probabilistic models](https://arxiv.org/abs/2201.09865). CVPR.
- Rombach, R., et al. (2022). [High-resolution image synthesis with latent diffusion models](https://arxiv.org/abs/2112.10752). CVPR.
- Kynkäänniemi, T., et al. (2019). [Improved precision and recall metric for assessing generative models](https://arxiv.org/abs/1904.06991). NeurIPS. (“Looks real” and “covers variety”.)
- Liu, M., et al. (2023). [PriSTI: A conditional diffusion framework for spatiotemporal imputation](https://arxiv.org/abs/2302.09746). ICDE.
- Liu, L., Jin, Z., & Choi, S. (2026). [PMA-Diffusion: A physics-guided mask-aware diffusion framework for traffic state estimation from sparse observations](https://arxiv.org/abs/2512.06183). Transportation Research Part C, 190, 105801.
- Jiang, C., et al. (2023). [MotionDiffuser: Controllable multi-agent motion prediction using diffusion](https://arxiv.org/abs/2306.03083). CVPR.
- Zhong, Z., et al. (2023). [Guided conditional diffusion for controllable traffic simulation](https://arxiv.org/abs/2210.17366). ICRA.
- Detector data: PeMSD7(M), as packaged with Yu, Yin & Zhu (2018), [STGCN](https://github.com/VeritasYin/STGCN_IJCAI-18), stations 717790 and 772455 on I-405 N.

Every number on this page comes from models trained on two real PeMS detectors on I-405 (May&ndash;June 2012) and on
the course's 4,000 CTM heatmaps. The heatmaps are simulated; the detector readings are real.

---

Next: world models, the last part of this module. Back to the {doc}`Module 4 map <index>`.
