(gaussians-warmup)=
# Before 4.3: Gaussians and their mixtures

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 4 &middot; Warm-up</span>
    <span class="notes-card-session">Read before 4.3 and the VAE</span>
  </div>
  <p class="notes-card-lede">The VAE and diffusion are built from one ingredient: the Gaussian. Every time they draw a sample, add noise or score a rebuild, a Gaussian does the work. This page is the warm-up: what a Gaussian looks like in more than one dimension, how to slice it, squash it and fit it, and how a mixture of Gaussians describes traffic that switches between regimes. Everything runs on three real loop detectors on I-405, and the interactive companion lets you turn every knob yourself.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Read it before</h4>
      <ul>
      <li><a href="notes1-producing.html">4.1 From predicting to producing</a></li>
      </ul>
    </div>
    <div>
      <h4>Labs that go with it</h4>
      <ul><li>None; the interactive companion at the end of this page</li></ul>
    </div>
  </div>
</div>

## What this page covers

- One bell in one, two and three dimensions: a centre, and a covariance that is almost never round
- Every Gaussian as a reshaped round one, x = &mu; + L&epsilon;, the way the VAE and diffusion draw samples
- Slicing (conditional), squashing (marginal) and fitting (maximum likelihood)
- Why one bell fails over a whole day, and what a mixture of bells does instead
- Where each of these ideas comes back in the VAE and in diffusion

## Three detectors, two slices of data

Three loop detectors on I-405 northbound in Los Angeles: A, then B 0.29 mi downstream, then C 0.44 mi further. C is
the detector of section 4.3. Each reports a five-minute average speed, over 44 weekdays of May and June 2012 (PeMS,
as packaged in PeMSD7(M)). Every model on this page is fitted on May and checked on June.

Each five-minute moment is one point: (speed at B, speed at C). At night (0:00&ndash;4:55 am) traffic runs in one
regime, free flow, and one bell describes it well. Over a whole day traffic switches between regimes, and one bell
does not.

## One bell, in more than one dimension

```{figure} ../_static/figures/GM_Gaussian_1D_2D_3D.png
:alt: Three panels. Left, a histogram of night speeds at detector C with a bell curve, centre 69.9 mph and spread 1.7 mph. Middle, night readings at B and C with tilted elliptical contours, the centre, the long and short axes, and the spread of each detector marked. Right, a 3D cloud of readings at A, B and C with an ellipsoid at one sigma, stretched along A.
:width: 100%

Night free flow. Each detector has its own spread (B 1.4, C 1.7, A 4.3 mph), and B and C lean together (r = 0.73), so the contours tilt.
```

$$
\mathcal{N}(\mathbf{x} \mid \boldsymbol{\mu}, \boldsymbol{\Sigma}) = \frac{1}{(2\pi)^{D/2}\,|\boldsymbol{\Sigma}|^{1/2}} \exp\left\{-\tfrac{1}{2}(\mathbf{x}-\boldsymbol{\mu})^{\mathsf{T}}\boldsymbol{\Sigma}^{-1}(\mathbf{x}-\boldsymbol{\mu})\right\}
$$

Here $\mathbf{x}$ is one reading ($D$ speeds), $\boldsymbol{\mu}$ the centre and $\boldsymbol{\Sigma}$ the covariance:
each detector's variance on the diagonal, how pairs lean together off it. *In words:* the density drops with the
distance from the centre, measured in the bell's own units (the Mahalanobis distance). Points at the same distance
have the same density, so the contours are ellipses (Bishop &amp; Bishop, 2024, Sec. 3.2).

A normal distribution is not a set of circles. Two night readings about 2.6 mph from the centre make the point:
(72, 72) goes with the lean and has 44% of the peak density; (72, 68) goes against it and has 0.7%, about 65 times
less likely.

## Every Gaussian is a reshaped round one

```{figure} ../_static/figures/GM_Reshape_Normal.png
:alt: Four scatter panels of the same 400 random draws. Round noise; then stretched by each detector's spread into an upright ellipse; then leaning into a tilted ellipse; then shifted to the night centre. Three gold points can be followed through all four panels.
:width: 100%

Round, diagonal and tilted are one family. The VAE and diffusion draw every sample this way.
```

$$
\mathbf{x} = \boldsymbol{\mu} + \mathbf{L}\,\boldsymbol{\varepsilon}, \qquad \boldsymbol{\varepsilon} \sim \mathcal{N}(\mathbf{0}, \mathbf{I}), \qquad \mathbf{L}\mathbf{L}^{\mathsf{T}} = \boldsymbol{\Sigma}
$$

The VAE's reparameterization trick is this recipe with an encoder computing the centre and a diagonal spread,
$\mathbf{z} = \boldsymbol{\mu}(\mathbf{x}) + \boldsymbol{\sigma}(\mathbf{x}) \odot \boldsymbol{\varepsilon}$. Diffusion's
noising step is the same recipe again, $\mathbf{x}_t = \sqrt{\bar\alpha_t}\,\mathbf{x}_0 + \sqrt{1-\bar\alpha_t}\,\boldsymbol{\varepsilon}$.
Both keep their bells round or diagonal for a practical reason: a full covariance over a 20 &times; 96 speed heatmap
(1,920 numbers) would hold 1,844,160 entries.

## Slice, squash and fit

**Slice (the conditional).** Detector C fails one night and B still reports 68 mph. Slicing the night bell at
B = 68 gives C a narrower bell, 67.8 &plusmn; 1.2 mph instead of C's own 69.9 &plusmn; 1.7. For a Gaussian the slice's
centre moves along a straight line in B: conditioning *is* least-squares regression (Bishop &amp; Bishop, Sec. 3.2.4).

**Squash (the marginal).** Ignore B and keep C's own entries of $\boldsymbol{\mu}$ and $\boldsymbol{\Sigma}$. Nothing to
compute (Sec. 3.2.5).

**Fit (maximum likelihood).** The bell that makes the readings most probable has the sample mean as its centre and
the sample covariance as its spread (Sec. 3.2.7). With the spread fixed, the log of a bell is a constant minus the
squared error, so maximum likelihood *is* least squares. That one line is why a VAE trained on squared error assumes
a Gaussian decoder, and why diffusion trains on squared error on the noise.

:::{admonition} Before you trust this result
:class: warning
**What is the baseline?** Filling C with its own night mean, which needs no neighbour.

**How was the data split, and why is that honest?** The night bell was fitted on May nights and tested on all 1,260
June night readings, days it never saw. Filling C from B cuts the error (RMSE) from 1.69 to 1.05 mph.

**What does it do on the ugly cases?** The 98 June readings with B near 68 mph had C = 67.2 &plusmn; 0.8 mph; the slice
said 67.8 &plusmn; 1.2, right direction but a little high and too wide, because real night speeds are not a perfect
bell. And the night bell knows nothing about the evening peak: tab 3 of the companion shows what the whole-day
model says instead.
:::

## When one bell is not enough: mixtures

```{figure} ../_static/figures/GM_One_Bell_Fails.png
:alt: Two scatter plots of all-day speeds at B against C. Left, one bell's contours stretch along the diagonal with its peak at about 49 and 48 mph, where few readings sit. Right, a mixture of three bells follows the free-flow cluster, the congested cluster and the transitions.
:width: 100%

One bell puts its peak where traffic almost never is: it expects 9.3% of readings within 5 mph of its peak, and only 0.8% of June readings landed there. Three bells expect 1.1%.
```

Each regime on its own is roughly bell-shaped, and the day is a pool of readings from all regimes. So the density of
the pool is a weighted sum of bells, one per regime (Bishop &amp; Bishop, Sec. 3.2.9):

$$
p(\mathbf{x}) = \sum_{k=1}^{K} \pi_k \, \mathcal{N}(\mathbf{x} \mid \boldsymbol{\mu}_k, \boldsymbol{\Sigma}_k), \qquad \sum_{k} \pi_k = 1
$$

The weights $\pi_k$ say how often each regime happens. Fitted to May by EM, three bells take 0.47 (free flow,
around 70 mph at both detectors), 0.40 (congested, around 22&ndash;24 mph) and 0.13 (the transitions in between). The
same formula is a two-step recipe for making a reading: pick a regime with probability $\pi_k$, then draw from its
bell. Discrete-choice readers know this shape as a latent class model.

```{figure} ../_static/figures/GM_Mixture_Three_Views.png
:alt: Three panels of the same three-bell mixture. Left, each component's rings in its own colour with its weight. Middle, the contours of the summed density. Right, the density as a surface, with a tall narrow free-flow spike cut off and a lower congested hill.
:width: 100%

Each bell and its weight, the mixture, and the mixture as a surface. Every bell holds a volume of exactly its weight, so the narrow free-flow bell is tall.
```

On June readings, the mixture scores 1.92 bits per reading better than one bell; four bells gain 2.05 and six gain
2.17, so the gains flatten. A better score does not make a bell a physical regime: the "in between" bell is a
catch-all for transitions.

## From mixtures to the VAE and diffusion

The VAE and diffusion are mixtures of Gaussians with a richer hidden cause.

| Idea on this page | In the VAE | In diffusion |
|---|---|---|
| The round bell $\mathcal{N}(\mathbf{0}, \mathbf{I})$ | the prior $p(\mathbf{z})$ | the starting noise |
| $\mathbf{x} = \boldsymbol{\mu} + \mathbf{L}\boldsymbol{\varepsilon}$ | the reparameterization trick | the forward noising step |
| Slice | the decoder $p(\mathbf{x} \mid \mathbf{z})$ | each reverse step $p(\mathbf{x}_{t-1} \mid \mathbf{x}_t)$ |
| Squash | $p(\mathbf{x}) = \int p(\mathbf{x} \mid \mathbf{z})\,p(\mathbf{z})\,d\mathbf{z}$ has no closed form, hence the ELBO | the noised data $q(\mathbf{x}_t \mid \mathbf{x}_0)$ has one |
| Maximum likelihood = squared error | the reconstruction loss | the noise-prediction loss |
| Mixture and soft guess | infinitely many bells, one per $\mathbf{z}$; the encoder is a soft guess over $\mathbf{z}$ | noised data are one round bell per training reading; the best denoiser is a soft guess over them |

Tab 6 of the companion shows both rows of the last line on the same two detectors: a small decoder network whose
bells, one per value of a one-dimensional $z$, score 2.22 bits per June reading better than one bell, and the
exact mixture of 6,624 round bells that adding noise turns the May readings into.

(gaussians-companion)=
## Interactive companion: Gaussians and their mixtures

Six tabs, one per idea above, all on the same three detectors. Results to look for:

- In two dimensions only 39% of a perfect bell lies inside its 1&sigma; ring, not 68%. Real June night readings put
  51% there: they are more peaked than a perfect bell.
- Play the reshaping in tab 2 and follow the three gold draws from round noise to the night bell. The D slider counts
  the numbers in one full covariance: 3 for two detectors, 210 for twenty, 1,844,160 for a 1,920-cell heatmap.
- Slice the whole-day mixture at B = 35 mph in tab 3. The three-bell answer is lopsided: a sharp peak near 39 mph and
  a long shoulder down to about 20 mph from the in-between bell. A few June readings near 35 mph do sit in that
  shoulder; the night bell's slice, 1.2 mph wide, would rule them out.
- In tab 5, try to beat the EM fit's June score by moving the weights, centres and spreads. Cutting the free-flow
  weight to 0.15 makes the congested hill dominate.
- In tab 6, click a reading near (30, 30) mph: the z values that could have made it form a narrow bell, which is what
  a VAE encoder learns to output.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion &mdash; Gaussians and their mixtures</span>
    <a href="../_static/companions/Gaussians_Mixtures_Companion.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/Gaussians_Mixtures_Companion.html"
          title="Gaussians and their mixtures: one bell, slicing, fitting, mixing, and the link to the VAE and diffusion" loading="lazy"></iframe>
</div>

## Check yourself

1. Detector C fails at 5:30 pm while B reads 35 mph. A colleague fills C with the slice of the night bell. What does
   that fill claim about its own certainty, and which model would you use instead?
2. A city wants 10,000 synthetic five-minute snapshots of a 20-detector corridor. Before fitting a Gaussian mixture
   with full covariances, what would you count, and what would make you switch to a VAE or diffusion?
3. A trajectory predictor outputs one Gaussian per future second and scores well on a highway dataset. You will use
   it near signalized intersections. What would you test first, and what failure do you expect?

---

Next: {doc}`4.3 One hidden cause: mixture models <notes5-hidden-cause>`, where detector C&rsquo;s two regimes become a hidden cause.
