(unclip)=
# 4.9 Reading unCLIP: from a CLIP embedding back to an image

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 4 &middot; Section 4.9</span>
    <span class="notes-card-session">Session: Diffusion</span>
  </div>
  <p class="notes-card-lede">unCLIP, the model behind DALL&middot;E 2, makes an image from a caption in two moves. A prior guesses the CLIP image embedding that a matching image would have, and a diffusion decoder turns that embedding into pixels. This page reads the paper with that split in mind: how the decoder learns with no hand labels, why it needs a prior, and what CLIP&rsquo;s embedding quietly drops on Tampa camera frames. It ends by running the same recipe on crash narratives and sketches.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Read it before</h4>
      <ul>
      <li><a href="notes6-diffusion-basics.html">4.8 Diffusion models: the basics</a></li>
      <li><a href="../module1/notes5-embeddings.html">1.5 Representation learning and embeddings</a> (CLIP) and <a href="../module1/lab4_clip_vs_traditional_cv.html">Lab 4</a></li>
      </ul>
    </div>
    <div>
      <h4>Interactive companion</h4>
      <ul><li><a href="../_static/companions/UnCLIP_Crash_Companion.html" target="_blank" rel="noopener">unCLIP on crash reports: from a narrative to a sketch &#8599;</a>, mounted in <a href="#unclip-crash-run">the pair-then-generate section</a> below</li></ul>
    </div>
  </div>
</div>

## What this section covers

- The big idea: a prior picks a CLIP image embedding, a diffusion decoder draws it, and the one equation that justifies the split
- Two facts about CLIP that drive the whole design, checked on 662 FL511 camera frames
- Just enough diffusion to read the paper
- The decoder: how every image labels itself, one training step, how c_img gets into the U-Net, and why it must sample rather than regress
- What the decoder shows about CLIP, and three failures that matter on the road
- The prior: why the decoder needs one, and its autoregressive and diffusion versions
- The paper&rsquo;s Figure 2 read with the six questions, and its results with what to trust
- Where it breaks, fit card and applications
- The recipe beyond images, with a worked run on crash narratives and sketches; a summary and seven questions

unCLIP makes an image from a caption in two moves. First, a **prior** guesses the CLIP image embedding that a matching image would have. Then a diffusion **decoder** turns that embedding into pixels. unCLIP is the model behind DALL·E 2 ([Ramesh et al., 2022](https://arxiv.org/abs/2204.06125)), and its name says what the decoder does: it runs CLIP's image encoder backwards.

This page spends most of its time on two questions:

1. How can a diffusion model be trained to turn a CLIP image embedding back into an image?
2. Why does the decoder need a prior, and how does the prior work?

**Read first.** You know CLIP from Module 1 ({doc}`1.5 <../module1/notes5-embeddings>` and {doc}`Lab 4 <../module1/lab4_clip_vs_traditional_cv>`) and Assignment 2. For diffusion, {ref}`Just enough diffusion <unclip-diffusion>` below gives just enough. The full story is in {doc}`4.8 Diffusion models: the basics <notes6-diffusion-basics>`, especially its sections on {ref}`training <diffusion-training>` and on {ref}`where the prompt comes in <diffusion-prompt>`.

**After this page you should be able to:**

1. Redraw Figure 2 of the paper and say, for each block, what it learns, what is frozen, and what passes along each arrow.
2. Explain how the decoder is trained with no hand labels: every image supplies its own target embedding.
3. Explain why running CLIP backwards needs a generator that samples, not a regression network.
4. Explain why the prior is needed, and how its two versions (autoregressive and diffusion) work.
5. Judge when a two-stage generator like this fits a transportation task, and what its CLIP embedding will quietly drop. Apply the same recipe to another pair of transportation data, such as a crash narrative and its sketch.

**A note on symbols.** The paper writes zᵢ for the CLIP image embedding and zₜ for the CLIP text embedding. In 4.8, zₜ means something else: the image after t steps of noise. This page keeps 4.8's meaning and renames the two CLIP embeddings c\_img and c\_txt. We use c because each embedding plays the role of 4.8's prompt c: c\_img prompts the decoder, and c\_txt prompts the prior.

| This page | The paper | What it is |
| --- | --- | --- |
| x | x | an image |
| y | y | its caption |
| c\_img | zᵢ | the CLIP image embedding of x: 1,024 numbers in the paper's CLIP |
| c\_txt | zₜ | the CLIP text embedding of y |
| zₜ | xₜ | the image after t steps of noise (4.8, Bishop & Bishop Ch. 20) |
| ε | ε | the static mixed in |
| g(zₜ, w, t, c) | ε\_θ | the decoder network's guess of the static; w = its weights |
| f | f\_θ | the prior network |
| λ | s − 1, where s = "guidance scale" | guidance strength |

(unclip-big-idea)=
## The big idea: decide what the image is about, then draw it

unCLIP splits caption-to-image into two learned steps joined by one vector: caption → **prior** → CLIP image embedding c\_img → **decoder** → image.

**Why you might care.** Say a perception team needs pictures of a rare scene: "a cyclist crossing against the light at dusk, seen from a signal-mounted camera." Writing that sentence takes ten seconds. Waiting for a camera to record it can take years. A text-to-image model is one way to make candidate pictures. Whether they are good enough to train on is a separate question (see {ref}`Where it breaks on the road <unclip-breaks>`).

**You have seen this split before.** Automated-vehicle testing describes a scenario at three levels (Menzel et al., 2018, from the PEGASUS project). A *functional* scenario is words: "a vehicle cuts in on a freeway." A *logical* scenario gives parameter ranges, and a *concrete* scenario fixes one value per parameter, which a simulator then renders. unCLIP has the same shape: words, then a compact description, then pixels. One difference matters. In PEGASUS an engineer chooses the parameters (cut-in gap, speed). In unCLIP the compact description is 1,024 numbers learned by CLIP. None of them is "the gap" or "the light state," and you cannot read them off like parameters.

```{figure} ../_static/figures/UC_Overview.png
:alt: Two columns of boxes. Left column, headed Generating an image, top to bottom: Caption y, for example "a traffic camera view of an intersection at night"; an arrow marked words to the CLIP text encoder (frozen, grey), which turns the caption into c_txt; an arrow marked c_txt, plus the caption's tokens, to the Prior (learned, blue), which draws one c_img that an image fitting the caption could have; an arrow marked c_img: 1,024 numbers to the Decoder (diffusion, learned), which draws a 64 x 64 image whose CLIP embedding is c_img and also reads the caption; an arrow marked 64 x 64 image to Two upsamplers (diffusion, learned), 64 to 256 to 1024, which see neither c_img nor the caption; out comes a 1024 x 1024 image. Right column, headed Training only: Training pair: image x, caption y, about 250 million (DALL-E set); an arrow marked image x to the CLIP image encoder (frozen), which writes c_img for every real training image. Two dashed arrows run from the CLIP image encoder to the left column: one into the Prior, marked prior's target, and one into the Decoder, marked decoder's prompt.
:width: 100%

unCLIP: the path that generates an image (left) and the frozen encoder that supplies the training targets (right).
```

Read the left column top to bottom to make an image. The right column runs only during training: frozen CLIP turns each real image into the c\_img that the prior must learn to produce and that the decoder must learn to draw.

**The key equation.** The paper justifies the split in one line:

$$
P(x \mid y) \;=\; P(x \mid c_{\mathrm{img}},\, y)\;\cdot\; P(c_{\mathrm{img}} \mid y)
$$

| Symbol | What it is here |
| --- | --- |
| y | a caption, e.g. "a traffic camera view of an intersection at night" |
| x | an image |
| c\_img | the CLIP image embedding of x: 1,024 numbers in the paper |
| P(x \| y) | all the images that fit caption y, with their chances: many images fit one caption |
| P(c\_img \| y) | **the prior:** the embeddings that images fitting y would have |
| P(x \| c\_img, y) | **the decoder:** the images whose CLIP embedding is c\_img and that fit y |

*In words:* to draw an image for a caption, first draw an embedding for the caption, then draw an image for that embedding.

*Why it holds.* The frozen CLIP encoder computes c\_img from x, so once x is known, c\_img is known too. So asking for x and c\_img together is the same as asking for x alone: P(x | y) = P(x, c\_img | y). The chain rule then splits P(x, c\_img | y) into the two factors.

*What it tells you about the design.* Both factors are **distributions**, not functions. Many embeddings fit one caption, and many images share one embedding. So both the prior and the decoder must be generators that *sample* an answer, not networks that return the single best answer. {ref}`The decoder <unclip-decoder>` and {ref}`the prior <unclip-prior>` sections show why that matters.

(unclip-clip)=
## CLIP: the frozen dictionary above the dotted line

The top half of the paper's Figure 2 is plain CLIP, trained once and then **frozen**. unCLIP never changes a CLIP weight. It only uses CLIP's two encoders as fixed tools.

**What you already know.** CLIP has an image encoder and a text encoder. It was trained on (image, caption) pairs so that a matching pair points the same way (high cosine) and a mismatched pair does not. This is the contrastive objective of Module 1 ({doc}`1.5 <../module1/notes5-embeddings>` and {doc}`Lab 4 <../module1/lab4_clip_vs_traditional_cv>`) and Assignment 2.

**What unCLIP takes from CLIP.**

- The *image encoder* turns any image x into c\_img. During training it supplies the target embedding for every image.
- The *text encoder* turns any caption y into c\_txt. The prior reads it as one of its inputs.

The paper's CLIP is larger than the one you used in class: a ViT-H/16 image encoder that reads 256 × 256 images, a 24-block text transformer, about 650 million training images, and embeddings of 1,024 numbers. The prior and decoder were trained on a different set: about 250 million images from the DALL·E dataset (Appendix C).

**Two facts about CLIP drive everything below.** You can check both on Florida camera data with the course's smaller CLIP (ViT-B/32, 512 numbers). The figure uses 662 FL511 snapshots from three Tampa intersections (one every three minutes, Oct 26, 2026) and five captions such as "a traffic camera view of an intersection at night."

```{figure} ../_static/figures/UC_Caption_Image_Gap.png
:alt: Range chart of cosine similarity between CLIP embeddings, axis from 0 to 1. Each frame and its most similar other frame (662 frames): 0.91 to 1.00, median 0.97. Two frames from different intersections (146,080 pairs): 0.18 to 0.91, median 0.67. Two different captions (10 pairs): 0.71 to 0.96. Each caption and its best-matching frame (5 captions): 0.29 to 0.36, far to the left of all the other ranges.
:width: 100%

A caption lands far from every image, even the image it describes best. 662 FL511 snapshots from three Tampa intersections and five captions, course CLIP (ViT-B/32).
```

1. **Images that look alike land almost on top of each other,** even when their traffic differs. Every frame has another frame at cosine 0.914 or more (median 0.968). The 1.00 at the top of the range is one camera sending the same frame twice. {ref}`The decoder section <unclip-sampler>` shows why this forces the decoder to be a sampler.
2. **A caption lands far from every image,** even the frame it describes best: cosine 0.36 at most. Frames from two different intersections are closer to each other than that (median 0.67), and the five captions sit close to one another (0.71 to 0.96). Text and images live in two separate regions, a pattern known as the modality gap (Liang et al., 2022). {ref}`The prior section <unclip-prior>` shows why this forces unCLIP to have a prior.

The gap does not stop CLIP from working. CLIP's training only asks a matching pair to score higher than the mismatched pairs in the same batch; it never asks text and image to land on the same point. So the ranking can be right while the gap stays. It is right here: at the Fowler Ave camera, all ten frames that score highest on the night caption were taken after sunset. The caption carries the right information, in the wrong place.

(unclip-diffusion)=
## Just enough diffusion

A diffusion model learns one skill, removing noise, and generates by using that skill many times on pure static. Four ideas are all you need for unCLIP. Each one is worked out in full in {doc}`4.8 <notes6-diffusion-basics>`.

1. **Noise is added by a fixed recipe.** Take a clean image x, draw static ε, and blend them to a chosen noise level t: zₜ = √αₜ x + √(1 − αₜ) ε. A small t leaves the image nearly clean; t = T leaves pure static. Nothing here is learned. unCLIP's decoder uses T = 1,000 levels.
2. **The network learns to name the noise.** A network g sees the noisy image zₜ and the level t, and guesses ε. The loss is the squared error between its guess and the real ε. You drew ε yourself, so the answer key comes free with every training example.
3. **Sampling runs the skill backwards.** Start from pure static. At each step, the network guesses the noise and a small part of it is removed. Many small steps later (250 for unCLIP's decoder), an image remains.
4. **A prompt is just one more input.** Give the network a prompt c, so it becomes g(zₜ, w, t, c), and train on pairs (x, c). Every step is then pulled toward images that fit c. If c is hidden for a share of training examples, one network learns to work with and without it. *Guidance* then asks it both ways at each step and pushes further toward the prompt: g = g\_without + (1 + λ)(g\_with − g\_without). In words: see how far the prompt moves the answer, then move λ times further in that direction.

One more fact from {doc}`4.8 <notes6-diffusion-basics>` matters below. At any step, the network's best guess of the clean image is a weighted **average** of the training images that could have produced zₜ. When the noise is heavy, that guess is a blur. A sample is not that guess, though. Each step removes only part of the noise, which rules out some candidates, so the guess sharpens step by step until one sharp image is left. {ref}`The decoder section <unclip-sampler>` shows why this matters: for traffic, a single best guess erases the cars.

**Where diffusion appears in unCLIP.** Twice. The decoder is a conditional diffusion model whose prompt c is the CLIP image embedding. The diffusion prior is a conditional diffusion model whose "image" is the CLIP image embedding itself, with the caption as its prompt.

(unclip-decoder)=
## The decoder: training a diffusion model to run CLIP backwards

The decoder is a conditional diffusion model whose main prompt is c\_img. The frozen CLIP image encoder writes that prompt for every training image, so no one has to label anything.

### The trick: every image labels itself

Take any image x from the training set and run it through CLIP's frozen image encoder. Out comes c\_img, and (c\_img, x) is a training pair: "this embedding came from this image." Nobody has to label anything, so the decoder can learn from all 250 million images. (The paper's decoder also reads each image's caption, dropped half the time. A decoder that used c\_img alone could be trained on images with no captions at all.)

You have seen this shape in the course notes on autoencoders ({doc}`4.4 <notes2c-autoencoders>`): an autoencoder, x → code → x. Here the encoder is CLIP, trained earlier for a different job and then frozen. The code is CLIP's 1,024 numbers. Only the decoder is trained, and it is a diffusion model instead of a network that returns one image.

### One training step

```{figure} ../_static/figures/UC_Decoder_Training.png
:alt: Flow diagram. Training image x (CLIP sees 256 x 256; the decoder, 64 x 64) splits two ways. Left: the frozen CLIP image encoder gives c_img, 1,024 numbers; an arrow labelled c_img: the prompt (set to null 10% of the time) goes into the U-Net. Right: draw a level t from 1 to 1,000 and static epsilon the size of x, then mix them into a noisy image z_t = root(alpha_t) x + root(1 - alpha_t) epsilon; an arrow labelled z_t and t goes into the U-Net. The U-Net g, the only learned box (blue), reads z_t, t, c_img and the caption and outputs a guess of epsilon. The guess goes to the loss, the squared length of guess minus epsilon, squared error as in 4.8; a dashed arrow from the static box brings epsilon, the answer key, to the loss. Last box: nudge w; then a new x, t and epsilon.
:width: 100%

Decoder training, one pass: only the U-Net learns.
```

Only the U-Net learns. The image, the frozen encoder and the static build each training example for free, and the dashed arrow carries the answer key.

$$
\mathcal{L}(w) \;=\; \big\lVert\, g(z_t,\, w,\, t,\, c_{\mathrm{img}},\, y) \;-\; \epsilon \,\big\rVert^2, \qquad z_t \;=\; \sqrt{\alpha_t}\; x \;+\; \sqrt{1-\alpha_t}\; \epsilon
$$

| Symbol | What it is here |
| --- | --- |
| x | a training image, 64 × 64 pixels for the base decoder |
| c\_img | the CLIP image embedding of that same x: the main prompt (the caption y is a second one, left empty half the time) |
| t, ε | a noise level drawn at random, and static drawn fresh |
| zₜ | the noisy image the network sees |
| g | the decoder network: GLIDE's U-Net, 3.5 billion weights |
| w | its weights, the only thing that learns |

*In words:* this is 4.8's loss (guess the noise), except that the network is also told the CLIP embedding of the image it is cleaning.

```text
Training the unCLIP decoder: one pass
x     <- an image from the training set
y     <- its caption
c_img <- CLIP image encoder(x)    # frozen
10% of the time: c_img <- null   # see Guidance, below
50% of the time: y <- empty
t     <- a level drawn from 1..1000
eps   <- fresh static, same size as x
z_t   <- sqrt(a_t)*x + sqrt(1-a_t)*eps
L(w)  <- |g(z_t, w, t, c_img, y) - eps|^2
one optimizer step on w
```

**Why this teaches the network to invert CLIP.** At a high noise level, zₜ shows almost nothing of x. The one clue left is c\_img. To name the noise well, the network must therefore learn what images with that embedding look like. At a low noise level, zₜ shows the details itself and c\_img matters less. So the embedding steers the big choices (which objects, what kind of scene, what style), while the exact layout and the fine details come from the noise. Run backwards from pure static, this network turns c\_img into an image.

### How c\_img gets into the network

```{figure} ../_static/figures/UC_Decoder_UNet.png
:alt: Diagram of GLIDE's U-Net (3.5 billion weights), which cleans a 64 x 64 image and guesses the static that was added to it. Top, where c_img comes from: while training, the frozen CLIP image encoder on the clean x; when generating, the prior, from the caption. Door 1, added to the time signal: step t goes through a sinusoid and an MLP into a time signal; c_img goes through a projection from 1,024 to 2,048 numbers and is added to it, giving a conditioning vector of 2,048 numbers (GLIDE also adds the caption's last token). Door 2, extra attention tokens: c_img goes through a projection into 4 tokens, which join the 256 tokens from the GLIDE text encoder (24 layers, learned; the caption y is dropped 50% of the time), making 260 context tokens of 2,048 numbers each. Middle: the noisy image z_t, a 64 x 64 x 3 FL511 frame plus static, enters the U-Net, whose blocks run 64x64 (512 channels), 32x32 (1,024), 16x16 (1,536), three at 8x8 (2,048), then back up through 16x16, 32x32 and 64x64, with skip connections copying features across. Every block reads the conditioning vector; the blocks at 32, 16 and 8 are marked attn and also read the 260 tokens. Out comes a guess of epsilon, 64 x 64 x 3, scored by the loss, the squared length of guess minus epsilon, against the static we drew: no hand labels needed. Bottom left, door 1 inside one ResBlock: features h, GroupNorm, times a scale plus a shift, then SiLU, conv and so on; the conditioning vector goes through a linear layer to a scale and a shift for each channel. Bottom right, door 2 inside one attention layer (16 x 16 shown): the 256 image positions ask, and each reads 256 + 260 = 516 answers (keys and values) from the image positions and the 260 context tokens; only image positions ask, the tokens only answer, as in DETR.
:width: 100%

How the decoder&rsquo;s U-Net reads the CLIP image embedding: c_img gets in twice.
```

Read the figure in three passes.

1. **Ignore c\_img.** The U-Net is the plain denoiser of {doc}`4.8 <notes6-diffusion-basics>`. A noisy image and its step t go in; a guess of the static comes out. The squared error against the static we drew trains every green box. No image needs a hand label: we drew the static ourselves, and frozen CLIP writes c\_img.
2. **Door 1.** c\_img is projected to 2,048 numbers and added to the time signal. Every ResBlock turns that vector into a scale and a shift for each channel, so c\_img nudges every feature map in the network.
3. **Door 2.** c\_img also becomes 4 extra tokens beside the 256 caption tokens. In each attention layer, every image position can look up these 260 tokens, as DETR's queries look up the encoder's tokens.

The picture of zₜ is illustrative: a real FL511 frame shrunk to 64 × 64, with synthetic static; no network was run. Two details come from GLIDE's and ADM's designs rather than from the unCLIP paper itself: the caption's last token is also added to the time signal, and the time signal is 2,048 numbers wide (four times the 512 base channels).

The decoder is GLIDE's U-Net with two inputs added (paper, Section 2.1):

- **Through the time signal.** The level t enters as an embedding that every block of the U-Net reads. unCLIP passes c\_img through a learned projection and *adds* it to that time embedding, so every block also hears c\_img.
- **As four extra tokens.** c\_img is also projected into four tokens and appended to the caption tokens from GLIDE's text encoder. The U-Net's attention layers let each image position read these tokens, as cross-attention did in Modules 2 and 3.

The caption path from GLIDE stays. The authors hoped it would carry what CLIP misses, such as which color belongs to which object. They found it offers little help with that (Sections 2.1 and 7 of the paper).

(unclip-sampler)=
### Why the inverse must be a sampler, not a regression

CLIP keeps what captions talk about, not where each car is. So many images share almost the same embedding. At Fowler Ave and 50th St, frames taken at 10:25 and 10:28 am sit at cosine 0.987, the second most similar of 16,653 pairs of daylight frames. Yet the near lanes changed: the white van and the dark car are gone, and a silver car has appeared. The detector counts 3 vehicles against 9, most of them small cars far up the road.

```{figure} ../_static/figures/UC_One_Embedding_Many_Frames.png
:alt: Top row: four frames from the FL511 camera at Fowler Ave / 50th St, Tampa, Oct 26, 2026: 10:25 am, this frame, 3 vehicles detected; 10:28 am, cosine 0.987, 9 vehicles; 10:19 am, cosine 0.977, 9 vehicles; 9:48 am, cosine 0.975, 3 vehicles. The road, buildings and sky look the same; the cars differ. Bottom left: the pixel average of the 8 frames closest in CLIP space (cosine 0.969 to 0.987), where the road and buildings stay sharp. Bottom right: a zoom on the near lanes, where the 3 to 12 vehicles per frame fade to ghosts.
:width: 100%

Frames CLIP calls almost the same point, and their pixel average. FL511 camera at Fowler Ave / 50th St, Tampa, Oct 26, 2026.
```

Now suppose you trained a plain network to map c\_img to an image with squared error, like the autoencoders in the course notes. For one embedding it must return one image, and the image with the smallest squared error is the *average* of all images with that embedding. That is the VAE's blur from {ref}`4.6 <vae-basics-breaks>`. The pixel average of the 8 frames nearest in CLIP space shows what it looks like. The road and buildings stay sharp, because every frame agrees on them. Every vehicle fades to a ghost, because the frames disagree. For traffic this is a bad failure: the average erases exactly the objects you care about.

The diffusion decoder learns the whole set, P(x | c\_img), and draws one member of it. Run it twice from different static and you get two different sharp frames, both fitting the same embedding. The paper calls the decoder "non-deterministic" for this reason (Section 1). *A caveat on the figure:* no decoder was trained here. The 8 nearest frames stand in for "all images with this embedding," and their average stands in for what a squared-error decoder would learn.

(unclip-guidance)=
### Guidance, and the 64 → 256 → 1024 cascade

**Guidance.** In training, c\_img is replaced by a null value 10% of the time and the caption is dropped 50% of the time. One network thus learns to work with and without each input, which is what guidance needs ({ref}`Just enough diffusion <unclip-diffusion>`). The paper reports guidance as a *scale* s, where s = 1 + λ in 4.8's terms. Its MS-COCO results use s = 1.25 for the decoder (λ = 0.25). *Read critically:* Section 5.1 of the paper says 5%, not 10%. The two agree if the drops are independent: 10% × 50% = 5% of training steps see the caption without c\_img, which is the text-only task Section 5.1 describes.

**The cascade.** The decoder above makes a 64 × 64 image. Two more diffusion models enlarge it: 64 → 256 (700 million weights) and 256 → 1024 (300 million). Each one's prompt is the smaller image, not c\_img and not the caption. During training that smaller image is slightly damaged first (a blur, or a mix of blur, noise and compression), so the upsampler learns to repair what the stage before it gets wrong. They use convolutions only, no attention.

One consequence is worth remembering. c\_img shapes only the 64 × 64 picture. Everything finer is invented by upsamplers that never see the embedding or the caption. The paper suspects that starting from 64 × 64 is why complex scenes lack detail, and suggests a larger base decoder as the fix (Section 7).

(unclip-microscope)=
## What the decoder shows about CLIP

A decoder that inverts CLIP is also a microscope for CLIP: decode an embedding, and you see what CLIP kept. The paper uses it five ways (Sections 3 and 4).

| Probe | How it works | What it shows |
| --- | --- | --- |
| Variations (Fig. 3) | Encode a real image to c\_img, then decode it several times from different static | Kept in every version: the objects and the style. Changed: layout, shapes, small details. Whatever changes was never in c\_img. |
| Interpolation (Fig. 4) | Decode points on the path between two images' embeddings | A smooth blend of the content and style of both images |
| Text diffs (Fig. 5) | Move c\_img in the direction c\_txt("a photo of a modern house") − c\_txt("a photo of a victorian house") | An edit in words, with no retraining: the house modernizes, the scene stays |
| Typographic attack (Fig. 6) | An apple with a paper label reading "iPod": CLIP's zero-shot label is iPod at 99.98% | The decoder still draws apples, and never an iPod. The embedding still holds "apple"; only CLIP's label ranking was fooled. |
| PCA (Fig. 7) | Keep only the first k principal components of c\_img (k = 20 to 320), then decode | The first components hold the coarse scene ("food in a container"), later ones the exact objects ("tomatoes and a bottle") |

A note on the variations. To keep the original layout, the authors first recover the starting static that would decode back to the exact image ("DDIM inversion"). Decoding from that static with no randomness rebuilds the original. Adding randomness step by step (a sampler setting the paper calls η > 0) gives variations that wander further as η grows. The pair (c\_img, starting static) is a complete code for the image: c\_img holds what CLIP sees, and the static holds the rest.

**Three failures** (Section 7 of the paper). The authors trace the first two to CLIP's embedding, and the third to the decoder:

- **Binding.** For "a red cube on top of a blue cube," unCLIP swaps the colors more often than GLIDE does (Fig. 14). Its reconstructions also mix up which object has which color, and get relative sizes wrong (Fig. 15). The authors suspect CLIP's embedding records *red, blue, cube, on top* without fixing which goes with which.
- **Spelling.** "A sign that says deep learning" gives signs with garbled letters (Fig. 16). The authors suspect CLIP's embedding does not hold exact spelling, and the way captions are split into word pieces hides the spelling from the model too.
- **Small things in big scenes.** Busy scenes such as Times Square come out with little detail (Fig. 17). Here the paper blames the 64 × 64 starting image, not CLIP.

All three matter on the road. A signal head is a binding problem: which light is lit, for which approach. A sign is a spelling problem. A child on a scooter at the edge of a dashcam frame is a small thing in a big scene, and *where* the child is matters most. Assignment 2 tested that with the course's CLIP: the true caption ("… in the oncoming lane") beat the deliberately wrong one ("… on the sidewalk") by only 0.0024. A margin that small suggests CLIP's embedding holds little about where the child is, so a decoder fed that embedding may put the child anywhere.

(unclip-prior)=
## The prior: from a caption to an image embedding

The decoder needs c\_img, but when you generate you have only a caption. The prior closes that gap: given a caption y, it draws a c\_img that a matching image could have.

### Why not hand the decoder the caption's own embedding?

There are two reasons, and you have already met both.

**The caption lands in the wrong place.** {ref}`The CLIP section <unclip-clip>` showed that c\_txt sits far from every image embedding: cosine 0.36 at most on the FL511 frames, while any frame has a neighbor at 0.91 or more. The decoder was trained only on image embeddings, so c\_txt is an input it never saw. The paper tried it anyway (Section 5.1). Fed c\_txt as if it were c\_img, the decoder makes reasonable images, but it scored worst of three small test models. The scores and the comparison are in {ref}`Results <unclip-results>`.

**One caption fits many images.** "A traffic camera view of an intersection at night" fits the night frames at Fowler Ave (37 were taken after 6:54 pm, about sunset) and every night frame at every other intersection. Each has its own embedding. A network that returned one best embedding for the caption would return the average of all of them, a point that may belong to no real image: the ghost of {ref}`the decoder section <unclip-sampler>`, one level up. So the prior must *sample* too.

This is the scenario ladder of {ref}`the big idea <unclip-big-idea>`. A caption is like a functional scenario: words that fit a whole family of scenes. The prior picks one member of the family, as a point in CLIP's space, much as a concrete scenario fixes one value for each parameter.

**Training data come free again.** Run each (image, caption) pair through frozen CLIP and you get (c\_txt, c\_img). The prior learns P(c\_img | y) from all of them, with no hand labels. The paper tried two kinds of generator for it.

```{figure} ../_static/figures/UC_Two_Priors.png
:alt: Two rows. Autoregressive prior, which writes c_img as 319 tokens, one at a time: a prefix of caption tokens, c_txt and a fit token set to high, followed by bucket tokens b1, b2, b3 up to b319 (the PCA components, coarsest first), all over a transformer with a causal mask in which each token reads only the tokens to its left. Each b is one of 1,024 buckets; read the 319 buckets, undo the PCA, and out comes c_img. Diffusion prior, which cleans all 1,024 numbers at once, 64 times: a sequence of caption tokens and c_txt (the prompt), step t and the noisy c_img (this step), and a read-out token (the answer slot), over a transformer with a causal mask; the output at the read-out token is the guess of the clean c_img, 1,024 numbers, with a squared-error loss. A note: generating starts from pure static and runs 64 steps, each one less noisy; draw two c_img this way and keep the one with the larger dot product with c_txt.
:width: 100%

The two priors: what each transformer reads and writes.
```

Both priors are transformers that read the caption and c\_txt. The first writes c\_img as a sentence of bucket tokens; the second cleans a noisy c\_img and reads its answer from one extra token.

(unclip-ar-prior)=
### Version 1: the autoregressive prior (GPT on a compressed embedding)

1. **Compress with PCA.** Keep the first 319 of the 1,024 principal components of c\_img. The average error of rebuilding c\_img from them is under 1%. It works because this CLIP was trained with sharpness-aware minimization (SAM, a training method, not Segment Anything), which left its embeddings using far fewer than 1,024 directions. This is the PCA from the autoencoder notes ({doc}`4.4 <notes2c-autoencoders>`).
2. **Turn numbers into tokens.** Split the range of each of the 319 numbers into 1,024 buckets. c\_img becomes a sentence of 319 tokens from a vocabulary of 1,024, largest component first.
3. **Predict token by token.** A transformer with a causal mask, the GPT of Module 2, predicts each bucket from the ones before it. It reads a prefix first: the caption's tokens, c\_txt, and one token for how well caption and image fit (below).
4. **Ask for a good fit.** In training, that extra token holds the dot product c\_img · c\_txt, cut into buckets. A higher value means the caption describes the image better. When generating, the authors draw this value from the top half of the values seen in training. They tried the top 50%, 30%, 15% and 5%; the top half was best in every test.

Because the largest components come first, the coarse scene is decided first and the details last, as in the PCA probe of {ref}`What the decoder shows about CLIP <unclip-microscope>`. Compressing 1,024 numbers to 319 tokens cut the tokens to predict by about three times and made training more stable.

### Version 2: the diffusion prior (diffusion on 1,024 numbers)

Here the thing being noised and cleaned is c\_img itself, a vector of 1,024 numbers, not an image.

- **The network is a transformer, not a U-Net.** The paper does not say why. A likely reason: a U-Net's convolutions assume that neighboring values belong together, which is true of pixels and false of the entries of an embedding.
- **Its input is one short sequence,** in this order: the caption's tokens, c\_txt, an embedding of the step t, the noisy embedding c\_img⁽ᵗ⁾, and one final *read-out* token. The transformer's output at that last token is its guess of the clean c\_img. It plays the role of BERT's \[CLS\] token from Module 2, but sits last: under a causal mask, only the last position can read everything before it.
- **It predicts the clean embedding, not the noise.** The authors found this works better than naming the noise:

$$
\mathcal{L}(w) \;=\; \big\lVert\, f(c_{\mathrm{img}}^{(t)},\, w,\, t,\, y,\, c_{\mathrm{txt}}) \;-\; c_{\mathrm{img}} \,\big\rVert^2
$$

| Symbol | What it is here |
| --- | --- |
| c\_img | the CLIP image embedding of a training image: the target |
| c\_img⁽ᵗ⁾ | that embedding after t steps of noise |
| y, c\_txt | the caption's tokens and its CLIP text embedding: the prompt |
| f | the prior network, a transformer with 1 billion weights w; t is the noise level, as in the decoder |

*In words:* given a noisy image embedding and the caption, guess the clean image embedding.

- **Pick the better of two.** The diffusion prior has no fit token. Instead it draws two candidates for c\_img and keeps the one with the larger dot product with c\_txt: CLIP acts as the judge.
- **Engineering details.** The embedding is multiplied by 17.2 so its spread matches pixel values scaled to \[−1, 1\]; that lets the noise schedules tuned for images be reused. Training uses 1,000 noise levels; generating takes 64 steps.

|  | Autoregressive prior | Diffusion prior |
| --- | --- | --- |
| What it writes | 319 bucket tokens, one at a time | all 1,024 numbers at once, refined over 64 steps |
| Network | transformer with a causal mask | transformer with a causal mask |
| Reads | caption tokens, c\_txt and a fit token, as a prefix | caption tokens, c\_txt, step t and the noisy c\_img |
| Gets a good fit by | asking for a high dot product | drawing two and keeping the higher dot product |
| Size and training | 1 billion weights, 1 million training steps of 4,096 examples | 1 billion weights, 600,000 training steps of 4,096 examples |

The diffusion prior beat the autoregressive prior at a comparable size and with less training compute (Section 5.1). Like the decoder, both priors see no text 10% of the time in training, so guidance is possible. In their aesthetic test, though, the authors found that guiding the prior hurt, and guided only the decoder (Section 5.5). {ref}`Results <unclip-results>` gives the diffusion prior's results.

(unclip-figure2)=
## Reading Figure 2 with the six questions

Figure 2 is drawn for **generation**, not for training. That is the first thing to notice, because it hides the trick that makes training possible.

**The visual code.** Blue means the text side and brown means the image side. The caption's vector is blue. The prior turns it into a brownish vector: an *image* embedding. In the top prior box, the arcs over the circles are causal attention, one token reading the ones before it (the autoregressive prior). In the bottom prior box, and in the decoder, each column of circles is one denoising step, drifting from blue toward brown (diffusion). The dotted line separates CLIP's own training (above) from unCLIP (below).

**What the figure leaves out.** The frozen CLIP *image* encoder appears only above the line. Yet during training it is the busiest part of unCLIP: it writes the target c\_img for every image, for both {ref}`the decoder <unclip-decoder>` and {ref}`the prior <unclip-prior>`. The two upsamplers are left out too.

The course's six reading questions, answered for unCLIP:

| Question | unCLIP's answer |
| --- | --- |
| 1. What is one token, physically? | Decoder: one position of the U-Net's image grid, plus 4 tokens made from c\_img and the caption's word pieces. AR prior: one bucket of one PCA component. Diffusion prior: a whole vector each (caption pieces, c\_txt, step t, noisy c\_img, read-out). |
| 2. How wide is each arrow? | caption → c\_txt: 1,024 numbers · prior → c\_img: 1,024 · decoder → 64 × 64 × 3 · upsamplers → 256 × 256 × 3 → 1024 × 1024 × 3 |
| 3. Where does information mix, and how? | Decoder: convolutions mix nearby pixels (built-in locality); attention at the 32, 16 and 8 grids lets image positions read the c\_img and caption tokens (learned); c\_img added to the time signal reaches every block. Prior: self-attention over its short sequence (learned). The two CLIP encoders never mix; they meet only at a dot product. |
| 4. What is the head, and its loss? | Decoder: a noise guess, squared error. Diffusion prior: the read-out token's clean c\_img, squared error. AR prior: a softmax over 1,024 buckets, cross-entropy. CLIP: the contrastive loss, used only to train CLIP. |
| 5. What is pretrained or frozen? | CLIP, both encoders, frozen. The prior, decoder and two upsamplers are trained separately, each on its own loss; nothing is trained end to end. |
| 6. Delete a block: does the ablation agree? | Delete the prior and feed c\_txt instead: clearly worse ({ref}`Results <unclip-results>`). Feed only the caption: worst of all (Fig. 8). Delete the decoder's caption path: not tested; the authors say only that it did not fix binding. Swap the AR prior for the diffusion prior: better. |

(unclip-results)=
## Results, and whether to trust them

unCLIP matched GLIDE on realism, fell slightly behind on following the caption, and gave much more varied images. GLIDE is the fair comparison: the same team's text-to-image diffusion model, with the same 3.5-billion-weight decoder but no CLIP embedding.

**Image quality on MS-COCO** (Table 2). FID compares a set of generated images with a set of real ones; lower is better. *Zero-shot* means no model below was trained on MS-COCO.

| Model | Zero-shot FID on MS-COCO 256 × 256 |
| --- | --- |
| DALL·E (2021) | about 28 |
| GLIDE (2021) | 12.24 |
| unCLIP, autoregressive prior | 10.63 |
| unCLIP, diffusion prior | 10.39 |

**People's judgments** (Table 1). Raters saw a unCLIP image and a GLIDE image and picked one (or "not sure"). With the diffusion prior, unCLIP won 48.9% of the time on photorealism (± 3.1 points) and 45.3% on matching the caption (± 3.0): about even, and slightly behind. On diversity, comparing two 4 × 4 grids of samples, unCLIP won 70.5% (± 2.8). The AR prior did worse on all three (47.1%, 41.1%, 62.6%).

**Does the prior earn its place?** (Section 5.1). The authors trained two small models, a decoder that reads c\_txt and a small unCLIP stack, and scored three ways of generating on one test set:

| Way of generating (small models) | FID |
| --- | --- |
| Decoder trained on c\_txt instead of c\_img (no prior) | 9.16 |
| Diffusion prior + decoder (the unCLIP stack) | 7.99 |
| The unCLIP decoder handed c\_txt as if it were c\_img (no prior) | 16.55 |

Raters also preferred the full stack over the decoder trained on c\_txt: 57.0% of the time for photorealism and 53.1% for caption match (± 3.1). So the prior helps, and skipping it by feeding the decoder an input it never saw hurts most.

**Why the variety survives guidance** (Section 5.3, Fig. 9). Turn up guidance in GLIDE and its samples converge: same camera angle, same colors. In unCLIP the content is already fixed in c\_img by the prior before the decoder starts. Decoder guidance then only sharpens the rendering: lighting and shadows improve while the scenes stay different. FID, which punishes a lack of variety, worsens far less for unCLIP than for GLIDE as guidance grows (Fig. 11).

:::{admonition} Before you trust this result
:class: warning
- *Baseline:* GLIDE is strong and fair: same team, same decoder size, and also trained on the DALL·E image set. The older models in the FID table are weaker baselines.
- *Split:* the test captions are MS-COCO validation captions, and no model trained on MS-COCO. Sampling settings were tuned with a small model that predicts human photorealism votes, then frozen for all three human tests. That small model is a linear probe on a CLIP (ViT-L/14), so a CLIP helped judge a CLIP-based generator (Appendix A).
- *Ugly cases:* the paper's own failures are binding, spelling and detail in busy scenes ({ref}`see above <unclip-microscope>`). FID scores a whole set of images; it never checks whether one image shows what its caption says. Nothing here tests road scenes, and nothing shows that unCLIP images make good training data for a detector. The showcase images in the paper's Figure 1 come from a production model, not the one in the tables: trained longer, on a larger, filtered dataset (Appendix C).
:::

(unclip-breaks)=
## Where it breaks on the road, fit card and applications

**Where it breaks**

- **The embedding drops what safety needs.** CLIP keeps the scene, not the vehicle count, the exact positions, the signal state or the small road user. At Fowler Ave, two frames with 3 and 9 vehicles sat at cosine 0.987. The decoder can only put back what the embedding holds. Variations of a real near-miss frame can quietly lose the near miss.
- **It generates only inside its training data.** Like the VAE, unCLIP is trustworthy only where its 250 million web images were dense. A pole-camera view of a work zone at night in rain is rare on the web. If the training images never showed a scene, the prior has no embedding to draw for it, and the decoder never learned to draw it. Generated images are not a substitute for recording real rare events.
- **No labels come with the picture.** A generated frame has no boxes, no counts, no ground truth. To train a detector on it, someone or something must still label it.
- **Plausible is not correct.** Nothing makes lane geometry, sign designs or shadows obey the real world, and each frame is made alone, so there is no motion between frames.
- **It is expensive.** About 5.5 billion weights across prior, decoder and upsamplers, and for each image two prior runs of 64 steps, then 250 + 27 + 15 decoder and upsampler steps (Appendix C). Guidance runs the decoder twice at each of its steps. This is a data-center model, not a roadside one.

**Fit card — unCLIP (a prior and a diffusion decoder on CLIP embeddings)**

| Field |  |
| --- | --- |
| Idea in one sentence | Generate in two steps: sample a CLIP image embedding for the caption, then sample an image for that embedding. |
| Why it works (the logic) | A frozen encoder labels every image with its own embedding, so the decoder learns embedding → image from images alone (captions optional) and the prior learns caption → embedding from captioned pairs. Both sample, so both keep variety. |
| Fits these tasks | Drafting scenes from words, variations of a real frame, edits by text ("day" → "night"), seeing what an embedding keeps. Leverage: *generation*, plus *judgment* when used as a probe. |
| Needs this data | Images for the decoder (frozen CLIP writes its prompt; captions optional); image–caption pairs for the prior; a pretrained CLIP. Paper scale: about 250 million pairs and large GPU clusters, so big labs. Agencies have camera frames but few captions. |
| Breaks when | The detail that matters is small, counted, spelled or tied to one object; the scene is rare on the web; you need labels, geometry or physics that hold. |
| Keep the classical method when | You need labeled, physically consistent scenes (a simulator such as CARLA renders them with ground truth); you need real rare events (near-miss surrogate measures with extreme value theory); you only need similar *real* images (CLIP search over your own archive is cheaper, and every image is real). |

**Applications**

| Domain | Task | Which piece of unCLIP | Data it needs | Classical baseline |
| --- | --- | --- | --- | --- |
| ADAS and perception | Many versions of a rare real frame (a night cut-in, a scooter near a crosswalk) to stress-test a detector | CLIP encoder + decoder (variations) | A decoder fine-tuned on dashcam frames and conditioned on c\_img only, so no captions are needed | Simulator renders with labels; ordinary augmentation (flip, brightness, blur) |
| Road safety, agency cameras | Audit what a CLIP-based alert system can and cannot notice before buying it | Decoder as a microscope ({ref}`see above <unclip-microscope>`) | The agency's camera archive and the vendor's encoder | Manual review of the frames it got wrong |
| Post-storm damage | Turn photos of a dry road into "the same road, flooded" to stress-test a flood classifier. The edit gives the image-level label; any box or mask must be redrawn and checked. | Text diffs ({ref}`see above <unclip-microscope>`) | Photos of the roads; a caption for the change | Ordinary augmentation; collect more after the next storm |
| Research: world models | Plan in a compact space, then render with diffusion | The two-stage idea itself | Driving video with actions | Physics-based simulators |

The last row is real. Wayve's GAIA-1 world model for driving ([Hu et al., 2023](https://arxiv.org/abs/2309.17080)) has the same two-stage shape: an autoregressive transformer predicts the next frame's image tokens from past video, text and actions (speed and curvature), and a video diffusion decoder renders those tokens into frames. Kandinsky 2.1 uses an unCLIP-style diffusion prior that maps CLIP text embeddings to CLIP image embeddings, then decodes in a compressed latent space ([Diffusers docs](https://huggingface.co/docs/diffusers/main/api/pipelines/kandinsky)), and Stable unCLIP fine-tuned Stable Diffusion 2.1 to also accept CLIP image embeddings, for text-guided image variations ([Diffusers docs](https://huggingface.co/docs/diffusers/main/en/api/pipelines/stable_unclip)). Many other text-to-image models skip the prior and let the decoder read the caption's tokens directly through cross-attention, as Latent Diffusion does ([Rombach et al., 2022](https://arxiv.org/abs/2112.10752)).

(unclip-recipe)=
## The recipe beyond images: pair, then generate the missing half

unCLIP is a recipe for any two kinds of data that describe the same event. First learn how the two kinds pair up. Then learn to generate one kind from the other.

```{figure} ../_static/figures/UC_Pair_Then_Generate.png
:alt: Three panels and a pipeline, worked on the course crash data: 350 Florida reports, 288 with both the officer's narrative and the crash sketch. Panel 1, learn the pairing (CLIP-style, on matched pairs): narrative to text encoder to c_txt, and crash sketch to image encoder to c_img, with c_txt and c_img pulled together; the same crash's narrative and sketch are pulled together and other crashes pushed apart; the pair itself is the label; needs matched pairs. Panel 2, learn to redraw a sketch (decoder: a U-Net trained by diffusion): sketch to the frozen image encoder to c_img, the prompt; sketch plus static to a U-Net that reads c_img, which outputs a guess of the static, scored by a loss against the static; every sketch writes its own prompt, so no narrative is needed; needs sketches only, any number. Panel 3, learn the bridge (prior: a transformer trained by diffusion): narrative to the frozen text encoder to c_txt; c_img plus static to a prior that reads c_txt, which outputs a guess of c_img, scored by a loss against c_img; the target is the c_img of the same crash's sketch, from the frozen image encoder; needs matched pairs. Bottom, generating a sketch for a new narrative (no sketch exists yet): new narrative to text encoder to c_txt to prior (3) to c_img to decoder (2), which starts from pure static, to a sketch draft. Shortcut: skip the prior and train the decoder on c_txt directly; it is simpler, but needs pairs for all decoder training, and in the paper's small test it scored a little worse (FID 9.16 against 7.99 with the prior; lower is better).
:width: 100%

unCLIP as a recipe on the course crash data: learn the pairing, learn to redraw a sketch from its own embedding, learn the bridge; then draft a sketch for a new narrative.
```

**The three steps, on crash reports.** The course crash dataset has 288 Florida reports with both the officer's narrative and the crash sketch.

1. **Learn the pairing.** Train a text encoder and an image encoder together, CLIP-style, so that a crash's narrative and its sketch point the same way and different crashes point apart. The pair itself is the label.
2. **Learn to redraw a sketch from its own embedding.** Freeze the image encoder. Add static to a sketch and train a U-Net to guess the static, told the sketch's own c\_img. This is {ref}`the decoder section <unclip-decoder>` with sketches in place of photos. Every sketch writes its own prompt, so any sketch can be used, with or without a narrative.
3. **Learn the bridge.** Freeze the text encoder too. Train a prior to turn the narrative's c\_txt into the c\_img of the same crash's sketch ({ref}`the prior section <unclip-prior>`). Of the two generators, only this one needs pairs.

To draft a sketch for a new narrative: narrative → text encoder → prior → c\_img → decoder → sketch.

**One detail to get right.** It is tempting to describe unCLIP as "train a decoder to rebuild the sketch from the narrative's embedding." That is the shortcut, and it works. The paper tested it: in its small test, a decoder trained on c\_txt scored FID 9.16, against 7.99 for prior + decoder ({ref}`Results <unclip-results>`). unCLIP proper splits the job differently. The decoder only ever sees the sketch's *own* embedding, and the jump from words to sketch happens in the prior. That split lets the decoder learn from sketches that have no narrative, and it keeps tools such as the variations and the microscope of {ref}`What the decoder shows about CLIP <unclip-microscope>`.

**Diffusion is a training recipe, not a network.** "Diffusion" names how a generator is trained (add static, learn to remove it) and how it generates (start from static, remove it step by step). The network inside is chosen to fit the data: unCLIP uses a U-Net for images and a transformer for a 1,024-number embedding. For the other direction, sketch → narrative, the output is text. There the usual generator is a GPT-style model that writes one token at a time, like the {ref}`autoregressive prior <unclip-ar-prior>`.

**Other pairs in transportation**

| Same event, two kinds of data | Where pairs come from | What you could generate | Watch out for |
| --- | --- | --- | --- |
| Crash narrative ↔ crash sketch | Police reports (course data: 288 pairs) | A sketch draft from a narrative, or a narrative from a sketch | Which vehicle did what is a binding problem ({ref}`see above <unclip-microscope>`): a draft may swap V1 and V2 |
| Dashcam video ↔ vehicle signals (speed, steering, braking) | Instrumented-vehicle logs | A plausible signal trace for a clip, or a clip for a trace | A generated trace must still obey vehicle dynamics |
| Camera image ↔ lidar scan | Open driving datasets such as nuScenes and Waymo Open | Lidar-like depth for a camera-only vehicle | Distances are safety-critical: plausible is not accurate |

:::{admonition} Before you try it on the course data
:class: warning
- *Scale.* CLIP learned its pairing from 400 million pairs; the course data has 288. Start from a pretrained CLIP and fine-tune it, and treat the result as practice with the pipeline, not as a sketch generator you can trust.
- *What the embedding keeps.* The pairing step keeps only what helps tell one crash from another. A detail that rarely separates crashes, such as the exact rest position of a vehicle, may never make it into the embedding, and then no decoder can put it back.
- *A generated sketch is not evidence.* It shows a scene that fits the words, not what happened. Use it as a draft or a teaching aid, never as a reconstruction.
:::

(unclip-crash-run)=
## unCLIP on crash reports: a worked run

The recipe above trains three models: a pairing between two kinds of data, a decoder that redraws one kind from its
embedding, and a prior that bridges from the other kind. This companion runs all three on the course crash data,
turning an officer&rsquo;s narrative into a 64 &times; 64 crash sketch, and reports how each step was trained and how
well it did. The full pipeline lands at chance, and the page shows why: the pairing step is the weak link. It also
walks through three problems worth knowing before you train your own conditional generator: a decoder that ignored its
condition, data that looked different at the size the model sees it, and a prior that learned no variety.

Every sketch on the page was drawn by the models; no real sketch, narrative or personal detail from the course dataset
appears. If you are enrolled, look up any crash ID in your copy of the dataset to compare an output with the real sketch.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion &mdash; unCLIP on crash reports: from a narrative to a sketch</span>
    <a href="../_static/companions/UnCLIP_Crash_Companion.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/UnCLIP_Crash_Companion.html" title="unCLIP on crash reports: pairing, decoder and prior trained on crash narratives and sketches, with every result" loading="lazy"></iframe>
</div>

(unclip-summary)=
## Summary and practice

- unCLIP = frozen CLIP + a **prior** (caption → c\_img) + a diffusion **decoder** (c\_img → 64 × 64 image) + two diffusion upsamplers (→ 1024 × 1024).
- **The decoder** is an ordinary conditional diffusion model whose prompt is c\_img. Frozen CLIP labels every training image with its own embedding, so no hand labels are needed. It must sample, not regress, because many images share one embedding: a single best answer would be a ghost.
- **The prior** exists because a caption's embedding sits far from every image embedding, and because one caption fits many images. The autoregressive version compresses c\_img with PCA and writes it as 319 tokens, GPT-style. The diffusion version denoises the 1,024 numbers with a transformer that predicts the clean embedding. The diffusion version is better and cheaper.
- What CLIP keeps (the objects, the kind of scene, the style), the decoder can draw. What CLIP likely drops (counts, exact positions, which attribute goes with which object, spelling), it cannot. Busy scenes also lose detail, which the paper blames on the 64 × 64 start. The same three steps (learn the pairing, learn to redraw from an embedding, learn the bridge) work for any two kinds of data about one event, such as a crash narrative and its sketch.

### Check yourself

1. Figure 2 hides how the decoder and the prior are trained. Redraw its lower half and add the training arrows. For each model, where does its target c\_img come from, and which boxes are frozen?
2. An agency asks for 2,000 synthetic night images of wrong-way drivers on freeway ramps, to train a detector. Which part of unCLIP would you rely on, which would you distrust, and what would you check before anyone trains on the images?
3. Your agency holds three years of CCTV frames but no captions. Which of unCLIP's models could you train on those frames alone, and which could you not? Why?
4. A colleague proposes to drop the prior and feed c\_txt straight to the decoder, "since CLIP puts text and images in one space." Answer with the FL511 numbers from {ref}`the CLIP section <unclip-clip>` and the paper's ablation from {ref}`Results <unclip-results>`.
5. A vendor's dashcam alert system runs on a CLIP-like encoder, and the vendor also gives you its decoder. Design a one-hour test that shows whether the system can "see" a child on a scooter at the edge of the frame. What would count as a pass?
6. Give two reasons to build a lane-keeping test set in a simulator such as CARLA rather than with an unCLIP-style generator, and one reason to prefer the generator.
7. An agency holds 20,000 scanned crash sketches, but only 300 of their reports have the narrative typed into a database. Using the three steps of {ref}`the recipe section <unclip-recipe>`, which step can use all 20,000 sketches and which can use only the 300 pairs? Would you take the shortcut of training the decoder on the narrative's embedding instead? Why or why not?

### Where to go next

- {doc}`4.8 Diffusion models: the basics <notes6-diffusion-basics>` for every diffusion step used here, and the *Training the denoiser* lab ({doc}`all labs <../labs>`).
- The *Generative models in transportation* handout for uses organized by transportation problem.
- World models later in the course: GAIA-1 reuses unCLIP's two-stage shape for driving video.

(unclip-references)=
## References for 4.9

- Ramesh, A., Dhariwal, P., Nichol, A., Chu, C., & Chen, M. (2022). [Hierarchical text-conditional image generation with CLIP latents](https://arxiv.org/abs/2204.06125). arXiv:2204.06125. *The paper; figure, section and table numbers above refer to it.*
- Radford, A., et al. (2021). [Learning transferable visual models from natural language supervision](https://arxiv.org/abs/2103.00020) (CLIP).
- Nichol, A., et al. (2021). [GLIDE: Towards photorealistic image generation and editing with text-guided diffusion models](https://arxiv.org/abs/2112.10741).
- Ho, J., Jain, A., & Abbeel, P. (2020). [Denoising diffusion probabilistic models](https://arxiv.org/abs/2006.11239).
- Bishop, C. M., & Bishop, H. (2024). *Deep Learning: Foundations and Concepts*, Chapter 20. Springer.
- Liang, W., et al. (2022). [Mind the gap: Understanding the modality gap in multi-modal contrastive representation learning](https://arxiv.org/abs/2203.02053). NeurIPS 2022.
- Menzel, T., Bagschik, G., & Maurer, M. (2018). [Scenarios for development, test and validation of automated vehicles](https://arxiv.org/abs/1801.08598). IEEE Intelligent Vehicles Symposium.
- Hu, A., et al. (2023). [GAIA-1: A generative world model for autonomous driving](https://arxiv.org/abs/2309.17080).
- Rombach, R., et al. (2022). [High-resolution image synthesis with latent diffusion models](https://arxiv.org/abs/2112.10752).

*Data and code for the FL511 figures.* 662 FL511 snapshots from three Tampa cameras (Fowler Ave / 50th St CAM324, Bruce B. Downs / Bearss CAM244, BBD / Tampa Palms CAM247), saved every three minutes on Oct 26, 2026 (genmodels/fl511\_gen). CLIP = openai/clip-vit-base-patch32, the {doc}`Lab 4 <../module1/lab4_clip_vs_traditional_cv>` checkpoint. Vehicle counts come from the course's Faster R-CNN run in the same folder. Reproducers: genmodels/unclip/ (embed\_clip.py, uc\_numbers.py, uc\_figures.py, uc\_equations.py).

---

Next: {doc}`4.10 Diffusion in the literature: from image generators to safety scenarios <notes8-diffusion-literature>`. Back to the {doc}`Module 4 map <index>`.
