(jepa-further-reading)=
# Further reading: JEPA and V-JEPA 2

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 4 &middot; Further reading after 4.12</span>
    <span class="notes-card-session">Optional, for the world-models session</span>
  </div>
  <p class="notes-card-lede">The world models of 4.12 predict the next observation. A JEPA (Joint-Embedding Predictive Architecture) predicts only a compact description of it, so it is free to drop glare, raindrops and other detail nobody can predict. This page explains the idea and the three Meta models built on it: I-JEPA for images, V-JEPA for video, and V-JEPA 2, which adds robot actions and plans toward a goal image. A small car-following example shows an autoencoder keeping the glare while a JEPA keeps the gap, an unprotected JEPA collapsing, and planning in the JEPA's latent space. It closes with JEPA papers in driving, trajectories and traffic forecasting.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Read it after</h4>
      <ul>
      <li><a href="notes11-world-models.html">4.12 World models</a>, for the world-model loop and its three families</li>
      <li><a href="notes2d-deep-autoencoders.html">4.5 Deep autoencoders</a>, for masked autoencoders</li>
      </ul>
    </div>
    <div>
      <h4>Interactive companion</h4>
      <ul><li><a href="#jepa-companion">JEPA world models</a>: masking, live training and planning, embedded below the worked example (<a href="../_static/companions/JEPA_World_Models_Companion.html" target="_blank" rel="noopener">full screen &#8599;</a>)</li></ul>
    </div>
  </div>
</div>

## What this page covers

- Why a world model might predict a description of the future instead of its pixels
- Three ways to learn from unlabeled data, and where JEPA sits among them
- The JEPA recipe: context encoder, predictor, slow target encoder, and the collapse every JEPA must avoid
- I-JEPA (images), V-JEPA (video) and V-JEPA 2 (a million hours of video, then robot actions and planning)
- A worked example on a synthetic car-following sensor, with an interactive companion that runs it in your browser
- JEPA papers in transportation, where it breaks, how it compares with the models of this module, a fit card and seven questions

(jepa-start)=
## Before you start

The world models in {doc}`4.12 <notes11-world-models>` learn to predict the next observation: the next camera frame, or the vehicle count on every link. JEPA (Joint-Embedding Predictive Architecture) makes a different bet. It predicts a compact *description* of what comes next, and it never tries to draw the frame itself.

This reading explains that idea and the three Meta models built on it: I-JEPA for images, V-JEPA for video, and V-JEPA 2, which adds robot actions and uses the model to plan. A small worked example on car following runs through the same steps at a size you can check by hand.

**After this reading you should be able to:**

1. Explain, with a dashcam example, why predicting a description of the future is different from predicting its pixels.
2. Draw the JEPA diagram (context encoder, target encoder, predictor) and say what each part does.
3. Explain *collapse*, the failure every JEPA must avoid, and the two common ways to prevent it.
4. Describe how I-JEPA, V-JEPA and V-JEPA 2 hide parts of their input during training, and what each model showed.
5. Explain how V-JEPA 2 plans actions by matching its prediction to a picture of the goal, and map that loop onto a driving task.
6. Decide when a JEPA-style world model fits a transportation task, and when a pixel-predicting world model or a classical model is the better choice.

**Symbols.** We follow the papers' notation so you can read them directly. One change from 4.12: there, z was the latent state; here it is the embedding s, as in the I-JEPA paper. (The V-JEPA 2 paper writes it z again; {ref}`the V-JEPA 2 section <jepa-vjepa2>` points out the switch.)

| Symbol | Meaning | Driving example |
| --- | --- | --- |
| $x$ | context: the part of the input the model sees | the last 2 seconds of dashcam video |
| $y$ | target: the part it must predict | the next 1 second of video, or a hidden patch of the frame |
| $E_\theta$ | context encoder, with weights θ | a vision transformer |
| $E_{\bar\theta}$ | target encoder: a slow-moving copy of $E_\theta$, with weights $\bar\theta$ | the same network with slightly older weights |
| $s_x = E_\theta(x)$ | embedding of the context: a vector of numbers | "pickup 30 m ahead, closing at 2 m/s", stored as numbers |
| $s_y = E_{\bar\theta}(y)$ | embedding of the target | the same kind of vector for the next second |
| $P_\phi$, $\hat{s}_y$ | predictor, with weights φ, and its guess of $s_y$ | — |
| $\Delta_y$ | where or when the target is | "1 s ahead", "the patch at row 3, column 5" |
| $a$, $p$ | action, and the agent's own state (pose) | ego acceleration; ego speed from the CAN bus |

**Prerequisites.** Autoencoders and masked autoencoders ({doc}`4.4 <notes2c-autoencoders>`–{doc}`4.5 <notes2d-deep-autoencoders>`), the world-model loop, its three families and model-predictive control ({doc}`4.12 <notes11-world-models>`), BERT's masked pretraining ({doc}`2.5 <../module2/notes5-bert>`), and the Vision Transformer's patch tokens ({doc}`2.7 <../module2/notes7-vision>`). In {ref}`4.12's table of three families <wm-what>`, V-JEPA 2 sat in the last row, "prediction without pictures". This reading opens that row up.

(jepa-why)=
## Why predict in latent space

A world model that predicts pixels must draw every detail of the next frame, including details nobody could predict and no driver needs. JEPA predicts only a compact description of the next frame, so it is free to drop those details.

**One second of dashcam video.** You are behind a pickup on I-275 at dusk, and the model must say what the camera will see one second from now. Sort what it would have to predict:

| Part of the next frame | Predictable from the last few frames? | Does a driver or controller need it? |
| --- | --- | --- |
| The pickup is about 2 m closer and drifting toward the lane line | yes | yes |
| The lane markings continue and curve right | yes | yes |
| The signal 200 m ahead is still red | mostly | yes |
| The exact pattern of oncoming headlight glare on the windshield | no | no |
| Raindrops, leaves moving in the median trees, sensor noise | no | no |
| The plate number of a car that has not yet come into view | no | no |

A pixel loss weights every pixel equally, and much of the change between video frames often comes from the last three kinds of detail. A model trained to predict pixels therefore spends most of its effort on the part that is both unpredictable and useless.

**What happens when you predict pixels anyway.** There are two outcomes, and you have met both in this module.

- A *deterministic* predictor (regression on pixels) outputs the average of all the futures it cannot tell apart. The glare and the rain average into a blur, just as {doc}`4.7 <notes4-gan>` showed that an average of futures can be a state that never happens.
- A *generative* predictor (the diffusion and token models behind GAIA and Cosmos in {ref}`4.12 <wm-milestones>`) draws sharp, believable details by sampling them. That is useful when a person must watch the output, but it costs model capacity and compute. When the V-JEPA 2 team planned robot actions with the Cosmos video model, each action took 4 minutes to choose; their latent model took 16 seconds while scoring 10 times as many candidate plans ({ref}`V-JEPA 2 <jepa-vjepa2>`).

**LeCun's proposal.** In his 2022 position paper *A Path Towards Autonomous Machine Intelligence*, Yann LeCun argued that a world model used for planning should predict in an abstract representation that keeps what is predictable and drops the rest. He called the design a **Joint-Embedding Predictive Architecture (JEPA)**: encode the present, encode the future, and train a predictor to map one embedding to the other.

**You already know a hand-built version.** The cell transmission model (CTM) never predicts which car changes lanes or what color it is. It describes the road by one number per cell, density, and its update rule predicts the next densities from the current ones. In JEPA terms, density is a chosen embedding and the CTM update is the predictor. JEPA learns both the description and the update from raw sensor data, instead of being handed them by traffic flow theory.

**How this differs from the masked autoencoder of {doc}`4.5 <notes2d-deep-autoencoders>`.** A masked autoencoder hides patches and rebuilds them *in pixels*. JEPA keeps the hiding but scores the guess *in embedding space*. That single change is the subject of the rest of this reading.

(jepa-families)=
## Three ways to learn from unlabeled data

All three families below learn an encoder from data nobody labeled. They differ in one thing: what the loss compares. A generative model compares pixels; a joint-embedding model compares the embeddings of two views of the same scene; a JEPA compares a *predicted* embedding with the actual one.

```{figure} ../_static/figures/JP_Families.png
:alt: Three panels read bottom-up. (a) Generative: x goes through an encoder and a decoder to a predicted y in pixels, compared with the real y. (b) Joint-embedding: x and y each go through an encoder, and the loss pulls the two embeddings together. (c) JEPA: x goes through a context encoder and a predictor, which also receives the target position; y goes through a target encoder with a stop-gradient; the loss compares the predicted and actual embeddings.
:width: 100%

Only a JEPA predicts an embedding. After LeCun (2022) and Assran et al. (2023), Figure 2.
```

Read each panel from the bottom up: inputs, then encoders, then what the loss compares at the top. The JEPA panel is the generative panel with its decoder replaced by a predictor that works on embeddings, and with the target passed through an encoder of its own.

**(a) Generative.** These are the models of this module: the autoencoder and masked autoencoder (4.4–4.5), the VAE, diffusion, and the video world models of 4.12. Their strength is that you can look at the output. Their cost is that every pixel of y counts in the loss, the unpredictable ones too.

**(b) Joint-embedding.** You met one in Module 1: CLIP pulls together the embeddings of an image and its caption. Image-only versions such as SimCLR and DINO make two "views" of one picture by cropping, flipping and shifting its colors, then pull their embeddings together. Two weaknesses follow:

- **Collapse.** If the encoder maps every input to the same vector, the two embeddings always match and the loss is perfect. Contrastive methods prevent this by also pushing apart embeddings of *different* scenes (CLIP does it with the other captions in the batch); other methods add a penalty that keeps the embeddings spread out.
- **Hand-made views carry hand-made assumptions.** A color shift teaches the encoder that color does not matter. For a traffic camera that is exactly wrong: the color of a signal head is the information.

**(c) JEPA.** It takes the hiding-and-predicting task from (a), so it needs no hand-made views, and the comparison in embedding space from (b), so it never has to draw pixels. It inherits (b)'s collapse problem, which {ref}`the JEPA recipe <jepa-recipe>` solves.

|  | (a) Generative | (b) Joint-embedding | (c) JEPA |
| --- | --- | --- | --- |
| Loss compares | predicted pixels with real pixels | embeddings of two views | predicted embedding with actual embedding |
| Needs hand-made views or pairs? | no | yes | no |
| Can collapse? | no: the pixels anchor it | yes | yes |
| Can you look at its prediction? | yes | there is no prediction | not directly |
| Spends effort on unpredictable detail? | yes | no | no |

The I-JEPA paper draws all three as **energy-based models**: a network that outputs a small number (low energy) when x and y belong together and a large one when they do not. The loss in each panel is that energy. {ref}`The V-JEPA 2 section <jepa-vjepa2>` reuses this word, because V-JEPA 2 plans by searching for actions that make the energy small.

(jepa-recipe)=
## The JEPA recipe

A JEPA trains two networks with gradients, a context encoder and a predictor, and keeps a third, the target encoder, as a slowly updated copy of the first. The loss compares the predicted embedding of the hidden part with its actual embedding. Without a guard, that loss has a useless perfect solution, so every JEPA also needs a way to prevent collapse.

```{figure} ../_static/figures/JP_Training_Step.png
:alt: A patched dashcam frame with some patches hidden. The visible patches go to the context encoder and then the predictor, which also receives the hidden patches' positions. The whole frame goes to the target encoder, whose embeddings of the hidden patches are kept as the target. An L1 loss compares the two; a dashed arrow marks the target encoder as a slow copy (EMA) of the context encoder, and the target path carries a stop-gradient.
:width: 100%

One training step of I-JEPA and V-JEPA, drawn on one dashcam frame: learning flows back only along the top path. After Assran et al. (2023), Figure 3.
```

Walk through one step on a dashcam frame cut into a grid of patches, as the Vision Transformer does ({doc}`2.7 <../module2/notes7-vision>`):

1. **Hide some patches.** The shaded ones become the target y; the rest are the context x.
2. **Encode the context.** The context encoder sees only the visible patches and outputs one embedding per patch, $s_x$.
3. **Predict.** The predictor receives $s_x$ plus a placeholder token for each hidden patch, marked with that patch's position ($\Delta_y$). It outputs a guess $\hat{s}_y$ for each hidden patch's embedding.
4. **Make the target.** The target encoder sees the *whole* frame and embeds every patch; the embeddings of the hidden patches become $s_y$. Masking happens after this encoder, not before, so each target embedding is computed with the full scene in view.
5. **Score and learn.** The loss is the distance between $\hat{s}_y$ and $s_y$. Gradients update the predictor and the context encoder. The target encoder is never trained directly: after each step its weights move a small step toward the context encoder's.

### The key equation

$$
\min_{\theta,\ \phi}\ \Big\|\, P_\phi\big(E_\theta(x),\ \Delta_y\big)\;-\;\mathrm{sg}\big(E_{\bar\theta}(y)\big)\,\Big\|_1
$$

| Symbol | What it means here |
| --- | --- |
| $x$, $y$ | the visible patches (context) and the hidden patches (target) of the same frame or clip |
| $E_\theta$ | the context encoder; θ are its weights |
| $E_{\bar\theta}$ | the target encoder, whose weights $\bar\theta$ are a slow average of $\theta$ |
| $P_\phi$ | the predictor; φ are its weights |
| $\Delta_y$ | the positions of the hidden patches, so the predictor knows *which* patch to predict |
| $\mathrm{sg}(\cdot)$ | stop-gradient: treat this value as a fixed number during the update |
| $\lVert\cdot\rVert_1$ | L1 distance: the sum of absolute differences, number by number |

**In words:** adjust the encoder and the predictor so that, from the visible part of a scene, the predictor can guess the embedding of the hidden part. This is the form used by V-JEPA and V-JEPA 2; I-JEPA uses the squared distance instead of L1.

(jepa-collapse)=
### Collapse, and two ways to prevent it

Look at the equation again. If both encoders output the same constant vector for every input, and the predictor passes it through, the loss is exactly zero. The model has "learned" nothing, yet its training curve looks perfect. This is **collapse**, and the {ref}`worked example <jepa-worked>` shows it happening in under 500 steps.

Two families of fixes are in use:

| Fix | How it works | Used by |
| --- | --- | --- |
| **Asymmetry: stop-gradient plus a slow target encoder** | The target is treated as fixed during each update, and the target encoder trails the context encoder as an exponential moving average (EMA). The predictor keeps chasing a target that has not yet collapsed. | BYOL (2020); I-JEPA (EMA rate 0.996 rising to 1.0); V-JEPA; V-JEPA 2 (fixed at 0.99925) |
| **Regularize the embeddings** | Add a penalty that keeps each embedding coordinate spread out across a batch and the coordinates uncorrelated, so a constant output is expensive. | VICReg (2022), the option LeCun's 2022 paper favors; LeJEPA's SIGReg (2025), which pushes embeddings toward a round bell curve and removes the need for EMA and stop-gradient |

The first fix is a training trick that works well in practice but has little theory behind it. The second is easier to analyze. LeJEPA's authors call their version "heuristics-free" because it needs no stop-gradient, no teacher network and no schedules, and their implementation is about 50 lines of code.

:::{admonition} Going deeper &mdash; why the slow copy works, and what JEPA learns first
:class: dropdown

*EMA.* The target encoder's weights follow $\bar\theta \leftarrow \tau\bar\theta + (1-\tau)\theta$ after every step, with τ close to 1. The V-JEPA paper gives a one-dimensional argument: if the predictor were always the best possible one, the encoder's gradient would be the gradient of how *unpredictable* the target still is (its median absolute deviation, given the context). Lowering that requires the encoder to keep information about the scene, not discard it. The slow target lets the predictor stay close to that best predictor while the encoder changes. This is a motivation, not a proof.

*What gets learned first.* Littwin et al. (2024) analyzed deep linear networks and found that a JEPA learns first the features that are most *predictive* of the target (high regression coefficients), while a masked autoencoder learns first the features with the most *variance*. In a dashcam frame, glare has high variance but predicts little; the gap to the lead vehicle has modest variance but predicts a lot. The {ref}`worked example <jepa-worked>` shows a related, simpler effect.

Sources: Bardes et al. (2024), Section 3.1; Littwin et al. (2024).
:::

(jepa-ijepa)=
## I-JEPA: JEPA on images

I-JEPA (Assran et al., CVPR 2023) was the first large test of the recipe. From one large context block of an image, it predicts the embeddings of four target blocks. With a frozen encoder and one trained linear layer, its best ImageNet model reached 81.1%, and its ViT-H/14 beat a masked autoencoder of the same size (79.3% vs 77.2%) after 300 training epochs instead of 1,600.

**The mobility problem.** A state DOT has years of unlabeled images from hundreds of roadside cameras (the FL511 frames of Lab 6 are a sample) and only a few thousand labeled ones. Self-supervised pretraining learns an encoder from the unlabeled pile; a small model trained on the labeled set then reads off the answer, such as "lane blocked" or "camera fogged".

```{figure} ../_static/figures/JP_IJEPA_Masking.png
:alt: Three 16 by 16 patch grids over a drawn road scene. Left: the image as patches. Middle: four large target blocks shaded, together covering most of the road and hiding whole vehicles. Right: the context block, with the targets and a border strip greyed out, leaving about a quarter of the image visible.
:width: 100%

I-JEPA hides four large blocks and predicts them from one big context block; block sizes follow the paper's default ranges (Assran et al., 2023, Section 3 and Figure 4).
```

**What each network sees.** The context encoder, a standard Vision Transformer, gets only the patches of panel 3. The target encoder gets the whole image and embeds all 256 patches; the embeddings of the patches in panel 2 are the targets. The predictor is a narrow transformer (384 numbers wide) that is run four times, once per target block, each time told which positions to fill.

**Two design choices made the difference.** The paper tested each one by changing it and measuring how well a classifier trained on only 1% of ImageNet's labels does on top of the frozen encoder:

| What was changed | Result with the I-JEPA choice | Result with the alternative |
| --- | --- | --- |
| How to hide (ViT-B/16) | 4 large target blocks, 1 big context block: **54.2%** | one quadrant predicts the other three: 15.5%; one large block: 20.2%; random patches: 17.6% |
| Where to compute the loss (ViT-L/16) | in embedding space: **66.9%** | in pixel space, same masking, even with 800 epochs instead of 500: 40.7% |

The first row says the targets must be big enough to hold meaning, a whole vehicle rather than a few pixels of its bumper that neighboring patches would give away, and that the context must be large and spread out: one huge target with a thin frame of context also failed. The second row is the {ref}`opening argument <jepa-why>`, measured: the same model trained to predict pixels learned a much weaker encoder.

**Results on ImageNet** (linear probe: freeze the encoder, train one linear layer on all labels; the same idea as the {ref}`linear head of 1.5 <linear-head>`):

| Method | Encoder | Training epochs | Linear probe, all labels | 1% of labels (probe or fine-tuning, whichever works better) |
| --- | --- | --- | --- | --- |
| MAE (pixels) | ViT-H/14 | 1,600 | 77.2% | 71.5% |
| I-JEPA | ViT-H/14 | 300 | 79.3% | 73.3% |
| I-JEPA, 448-pixel input | ViT-H/16 | 300 | 81.1% | 77.3% |

**Cost.** Computing targets with a second encoder makes each I-JEPA step about 7% slower than an MAE step, but it needs about 5 times fewer steps. The ViT-H/14 trained on 16 A100 GPUs in under 72 hours.

**What the embedding keeps.** To see what a predicted embedding contains, the authors trained a separate generative model to turn predictions back into images. Across several samples, the object parts and their pose stayed the same, such as the top of a car in the right place, while textures and background changed from sample to sample. The predicted embedding carries the *what and where*, not the pixel detail.

**What this means for a traffic camera.** ImageNet photos are centered on one large object; a traffic camera frame holds dozens of small vehicles seen from a fixed, high angle. The masking ranges above were tuned for ImageNet, and a 15–20% block of a highway camera frame may hold six cars or none. Expect to retune the block sizes for your camera geometry, and test on your own frames before trusting ImageNet numbers.

(jepa-vjepa)=
## V-JEPA: JEPA on video

V-JEPA (Bardes et al., 2024) applied the recipe to video clips. It hides about 90% of each clip, always the same spatial blocks in every frame, and predicts the hidden parts' embeddings with an L1 loss. Trained on 2 million public videos with no labels, text or pretrained image encoder, its largest frozen model scored 81.9% on Kinetics-400, 72.2% on Something-Something v2 and 77.9% on ImageNet.

**The mobility problem.** An intersection camera records 24 hours a day. What matters for safety is motion: who is turning, who is yielding, who just accelerated into the conflict zone. A single frame cannot show this, so an image model like I-JEPA is not enough. You need an encoder that learns how things move, again without labels.

```{figure} ../_static/figures/JP_VJEPA_Tubes.png
:alt: Five 8 by 8 patch grids for frames 1-2, 3-4, 5-6, 7-8 and 15-16 of one clip. The same patches, about 90 percent, are shaded in every slice. Below, a small cube shows one token: a tubelet of 2 frames by 16 by 16 pixels; a 16-frame clip at 224 by 224 pixels becomes 1,568 tokens.
:width: 100%

V-JEPA hides the same patches in every frame, so the model cannot copy from a neighboring frame (tubelet size and mask ratio from Bardes et al., 2024, Sections 3.2–3.3).
```

**Tokens become tubelets.** V-JEPA keeps the Vision Transformer but makes each token a small box of video: 2 consecutive frames by 16 × 16 pixels. A 16-frame clip (frames sampled every 4th, about 3 seconds) at 224 × 224 pixels becomes 1,568 tokens.

**Hide tubes, not specks.** Video is redundant: a patch hidden in frame 5 is almost the same as the visible patch in frame 6, so random specks can be filled in by copying. V-JEPA therefore hides the *same* spatial blocks in every frame. Each clip is masked twice, once with each of two mask types, and the model predicts both (the target embeddings are computed once and shared). Block aspect ratios are between 0.75 and 1.5:

- *short-range*: the union of 8 blocks, each covering 15% of a frame;
- *long-range*: the union of 2 blocks, each covering 70% of a frame.

Because the blocks overlap and are united, about 90% of the clip is hidden on average.

**Pixels or embeddings, measured again.** The authors trained the same ViT-L/16 twice on the same 2 million videos, once predicting normalized pixels (as a video masked autoencoder does) and once predicting embeddings:

| Target of the prediction | Kinetics-400, frozen | Something-Something v2, frozen | ImageNet, frozen | Kinetics-400, fine-tuned |
| --- | --- | --- | --- | --- |
| pixels | 68.6% | 66.0% | 73.3% | 85.4% |
| embeddings (V-JEPA) | 73.7% | 66.2% | 74.8% | 85.6% |

With the encoder frozen, predicting embeddings helped most on Kinetics-400 (+5.1 points), less on ImageNet (+1.5) and barely on SSv2 (+0.2); after full fine-tuning the two were almost equal. Its advantage is an encoder that is useful *as it comes*, which matters when you cannot afford to fine-tune a billion-parameter model for every traffic task.

**How a frozen encoder is read out.** V-JEPA's evaluations freeze the encoder and train a small *attentive probe*: a cross-attention layer with one learned query that looks over all the patch embeddings and pools them into one vector, followed by a small classifier. It is the learned-query idea of {doc}`DETR (2.10) <../module2/notes10-detr>` with a single query. V-JEPA 2 uses a deeper version, four transformer blocks with the cross-attention last. Probes like this produce the classification results below, and they are how you would attach a new traffic task to a frozen encoder.

**What the benchmarks test.** Kinetics-400 classifies actions that are often visible in one frame ("playing basketball"); Something-Something v2 (SSv2) needs motion ("pushing something from left to right" versus "from right to left"). A lane change to the left versus to the right is an SSv2-type question; "there is a bus in the frame" is a Kinetics-type question.

(jepa-vjepa2)=
## V-JEPA 2: scaling up, then learning to act

V-JEPA 2 (Assran et al., June 2025) does two things. It scales V-JEPA's pretraining from 2 million videos to over 1 million hours, and it then turns the frozen video encoder into an action-conditioned world model, **V-JEPA 2-AC**, using under 62 hours of robot video. That model picked and placed objects with robot arms in two labs whose scenes it had never seen, with no task-specific training and no reward.

```{figure} ../_static/figures/JP_VJEPA2_Stages.png
:alt: Three stages left to right. Stage 1, pretrain on video only: over a million hours of internet video and a million images; hide about 90 percent of each clip and predict its embeddings; result, a frozen encoder of about one billion weights. Stage 2, post-train with actions: under 62 hours of robot video with arm poses; the frozen encoder embeds each frame; result, a 300-million-weight action-conditioned predictor. Stage 3, plan: current frame, arm pose and goal image; search for actions whose imagined embedding is closest to the goal's; execute the first action and plan again.
:width: 100%

V-JEPA 2 in three stages: watch video, learn what actions do, then plan. After Assran et al. (2025), Figures 1, 2 and 7.
```

The split is the point of the design. Stage 1 needs huge amounts of data but no actions, and video without actions is plentiful. Stage 2 needs actions, which are scarce, but it only has to learn how actions change an embedding the encoder already knows how to make.

### Stage 1: pretrain on a million hours of video

The objective is V-JEPA's ({ref}`previous section <jepa-vjepa>`). What changed is scale, and the paper measures each step on the average accuracy over six frozen-encoder tasks:

| Ingredient | V-JEPA | V-JEPA 2 | Average accuracy over 6 tasks |
| --- | --- | --- | --- |
| Data | 2 million videos (VideoMix2M) | 22 million videos and images (VideoMix22M) | 84.2 → 85.2 |
| Encoder | ViT-L, 300 million weights | ViT-g, about 1 billion weights | → 86.7 |
| Training length | 90,000 steps | 252,000 steps | → 87.5 |
| Clip size | 16 frames at 256 × 256 | up to 64 frames at 384 × 384 | → 88.2 |

- **The data.** VideoMix22M combines Something-Something v2 (168 hours), Kinetics (614 hours), HowTo100M (134,000 hours), a curated part of YT-Temporal-1B (listed at 1.6 million hours across 19 million clips) and 1 million ImageNet images, each image repeated to make a 16-frame still video. The YouTube part was filtered by retrieval toward scenes that resemble the benchmark training sets, which by itself added 1.4 points.
- **Progressive resolution.** Training the ViT-g on 64-frame, 384 × 384 clips from the start would take roughly 60 GPU-years. Instead it trains on 16-frame, 256 × 256 clips and switches to longer, sharper clips only in the last 12,000 steps, for 8.4 times less GPU time.
- **Positions.** Patch positions in time, height and width are encoded by rotating parts of each embedding (3D-RoPE), which the authors found kept the largest models stable.

**Results.**

| Task | What it tests | V-JEPA 2 |
| --- | --- | --- |
| Something-Something v2, frozen encoder and attentive probe | recognizing motion | 77.3% top-1 |
| Epic-Kitchens-100 action anticipation, frozen encoder and probe | naming the action that starts 1 s later | 39.7 recall-at-5, 44% above the previous best |
| PerceptionTest, with an 8-billion-parameter language model trained on top of the encoder (reported after fine-tuning) | answering questions about a video | 84.0% |
| TempCompass, same language model (zero-shot) | questions about order and timing | 76.9% |

Anticipating an action 1 second ahead is the closest benchmark to a traffic question such as "will this pedestrian step off the curb?". Notice, though, that the pretraining mix was not built for driving: it has no dashcam or traffic-camera collection, only whatever driving clips happen to appear in Kinetics and YouTube. {ref}`The research section <jepa-transport>` shows what happened when others adapted it to dashcam video.

### Stage 2: learn what actions do (V-JEPA 2-AC)

The encoder is now frozen. A new predictor learns how an action changes the embedding of the next frame.

- **Data.** The DROID dataset: about 23,000 teleoperated runs of a 7-joint Franka arm, successes and failures alike, with no reward and no task label. Keeping only clips at least 4 seconds long leaves under 62 hours. Each clip is sampled at 4 frames per second, giving 16 frames of 256 × 256.
- **Action and pose.** The pose $p_k$ is the gripper's state: 3 numbers for position, 3 for orientation, 1 for open or closed. The action $a_k$ is simply the change in pose between two frames, so no one had to label actions.
- **Encoding.** The frozen encoder embeds each frame on its own, giving a 16 × 16 grid of 1,408-number embeddings per frame.
- **Predictor.** A 300-million-weight transformer (24 layers, 16 heads, 1,024 wide). Its attention is *block-causal*: the tokens of one time step can look at the frame, action and pose tokens of that step and of earlier steps, never later ones. That rule makes it a model of cause and effect forward in time.
- **Notation.** The paper writes the frame embedding as $z_k$ and the pose as $s_k$. Here we keep s for embeddings, as in the earlier sections, and write the pose as $p_k$.

$$
\mathcal{L}(\phi)=\frac{1}{T}\sum_{k=1}^{T}\big\|\hat{s}_{k+1}-s_{k+1}\big\|_1\;+\;\big\|P_\phi(a_{1:2};\ s_1,\ p_1)-s_{3}\big\|_1
$$

**In words:** learn to predict the next frame's embedding, $\hat{s}_{k+1}$, from the real past (T = 15 such predictions per 4-second clip; the first term, called *teacher forcing*), and also learn to predict two frames ahead when the middle frame is the model's own guess (second term, a *rollout*). The second term trains the predictor to cope with its own mistakes, which is what it faces when it imagines a plan. {ref}`4.12's first failure mode <wm-breaks>`, errors that compound over the horizon, is the reason for it.

(jepa-plan)=
### Stage 3: plan by minimizing an energy

To use the model, you show it a picture of the goal. Planning then means searching for the actions whose imagined result looks most like the goal *in embedding space*.

$$
a^{*}_{1},\ldots,a^{*}_{T}\;=\;\underset{a_1,\ldots,a_T}{\arg\min}\;\Big\|\,P_\phi\big(a_{1:T};\ s_k,\ p_k\big)-s_{\text{goal}}\,\Big\|_1
$$

| Symbol | What it means here |
| --- | --- |
| $a_1, \ldots, a_T$ | a candidate plan: T actions in a row |
| $s_k = E(x_k)$, $p_k$ | the embedding of the current frame and the arm's current pose |
| $P_\phi(a_{1:T};\ s_k,\ p_k)$ | the embedding the predictor imagines after carrying out the plan |
| $s_{\text{goal}} = E(x_{\text{goal}})$ | the embedding of the goal image |
| $\lVert\cdot\rVert_1$ | L1 distance: this is the *energy* of the plan |
| $\arg\min$ | keep the plan with the lowest energy |

**In words:** among the plans you try, keep the one whose imagined future is closest to the goal picture, measured on embeddings, not pixels. Compare the {ref}`planning equation of 4.12 <wm-uses>`: there you maximized imagined reward; here you minimize imagined distance to a goal.

```{figure} ../_static/figures/JP_Planning_Loop.png
:alt: The current frame and the goal image each pass through the frozen encoder. Inside a cross-entropy-method box, four steps form a loop repeated 10 rounds: sample action plans, imagine their result with the predictor, score each by the L1 energy to the goal embedding, and refit the sampler to the best plans. The best plan's first action is executed; the arm moves and the next frame starts the loop again.
:width: 100%

One planning step of V-JEPA 2-AC: it plans by matching an imagined future to a goal image. After Assran et al. (2025), Figure 7 and Section 3.2.
```

The search inside one planning step is the **cross-entropy method (CEM)**: draw many plans from a Gaussian per action (starting at mean 0, variance 1), score each with the energy, refit the Gaussians to the best ones, and repeat. The paper used 800 plans per round, kept the best 10, ran 10 rounds, and looked only one action ahead, which it found enough for these fairly greedy tasks. After the last round, the mean of the Gaussians is the plan. Only its first action is executed; then the robot looks again and plans again. That is receding-horizon control, the same loop as ramp-metering MPC with METANET in {ref}`4.12 <wm-uses>`, except that the model is learned and the target is a picture.

### Results

Neither lab appears in DROID (the arms are the same Franka model), the camera was an uncalibrated low-resolution RGB camera, and each sampled action was capped at about 13 cm of gripper motion. Single-goal reaching ended within 4 cm of the goal. Success rates over 10 trials per task, averaged over the two labs:

| Method | Reach | Grasp: cup | Grasp: box | Reach with object: cup | Reach with object: box | Pick-and-place: cup | Pick-and-place: box |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Octo (imitation-learned policy, fine-tuned on all of DROID) | 100% | 15% | 0% | 15% | 70% | 15% | 10% |
| V-JEPA 2-AC | 100% | 65% | 25% | 75% | 75% | 80% | 65% |

For pick-and-place the model was given three goal images in sequence (object grasped, object near its target, object placed) and switched between them after 4, 10 and 4 steps.

The comparison with a pixel-predicting world model was run in Lab 2, with both models planning by CEM on one RTX 4090 GPU:

| World model | Plans scored per round | Time to choose one action | Reach | Grasp: cup | Grasp: box | Pick-and-place: cup | Pick-and-place: box |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Cosmos (latent video diffusion, 7B, fine-tuned on DROID) | 80 | 4 minutes | 80% | 0% | 20% | 0% | 0% |
| V-JEPA 2-AC | 800 | 16 seconds | 100% | 60% | 20% | 80% | 50% |

At 4 minutes per action, one Cosmos pick-and-place run would take over an hour. Predicting embeddings instead of video made the search about 15 times faster while it scored 10 times as many plans.

**Limits the authors report.**

- **Camera placement.** Actions are given in the robot's coordinates, and the model must infer those axes from a single camera. Its inferred axes rotated as the camera moved around the robot, and the team tried several camera positions by hand before picking one.
- **Long horizons.** Prediction errors grow with every imagined step, and the number of possible plans grows exponentially with the horizon. The reported plans look one step ahead, and pick-and-place needed hand-given sub-goal images.
- **Goals as images.** In practice goals are more naturally stated in words.

**What it would take for driving.** Read the same design with a car in place of the arm:

| Part | Robot arm in the paper | Driving counterpart | What changes |
| --- | --- | --- | --- |
| Stage 1 video | 1M+ hours of internet video | fleet dashcam video, no CAN signals needed | the pretraining video should include driving ({ref}`research section <jepa-transport>`) |
| Stage 2 data | 62 h of DROID with gripper poses | drives with logged CAN: acceleration, steering, speed | action variety matters, as in {ref}`4.12's data section <wm-data-needs>` |
| Action a | change in gripper pose, capped at about 13 cm | acceleration and steering change | limits come from vehicle dynamics and comfort |
| Pose p | gripper position, orientation, opening | ego speed, yaw rate | — |
| Goal | a picture of the finished task | a frame at the desired gap or lane position, or a cost such as progress plus safety margin | most driving goals are not pictures |
| Time per decision | 16 s per action | about 0.1 s | needs a far smaller model or a learned policy distilled from the planner |
| Safety | not in the energy | must be | a collision is not just "far from the goal picture" |

:::{admonition} Going deeper &mdash; why a block-causal predictor, and why only a two-step rollout
:class: dropdown

*Block-causal.* During training the predictor sees all 16 frames at once, which makes training fast; the attention mask stops step k from seeing steps after k, so one pass gives 15 next-step predictions. At planning time the same network is run step by step.

*Two-step rollout.* Differentiating through longer imagined rollouts is costly and unstable, so the rollout term looks only two steps ahead: the gradient passes through one recurrent step. It is a cheap way to teach the model what its own output looks like as an input.

*An energy landscape you can look at.* For one reaching task the authors swept a single action over a grid and plotted the energy. It was smooth and roughly bowl-shaped, with its minimum near (0, −0.05) m while the true action was (0, −0.1) m: close, not exact. A smooth bowl is what makes a sampling search like CEM work.

Source: Assran et al. (2025), Sections 3.1, 3.2 and 4.2, Figure 9.
:::

(jepa-worked)=
## Worked example: a small JEPA world model for car following

On synthetic car-following data, a JEPA encoder that is only ever asked to predict the next frame's embedding recovers the gap and the closing speed (probe R² 0.99), while an autoencoder of the same size recovers none of either. Without protection the same JEPA collapses within 500 training steps. Planning toward one goal frame in the JEPA's latent space held a 25 m gap as closely as a classical controller that measures the gap (2.7 m vs 3.0 m RMS error), with no collisions in 40 drives, but with about five times the jerk. An autoencoder's latent space used the same way crashed in 28 of 40 drives.

**The question.** Can a model that never sees the gap, only a noisy sensor, learn a description of the scene good enough to plan with? And what does each piece of the JEPA recipe contribute?

### Setup (synthetic data, built to show the mechanism)

- **Hidden state.** The gap g to the lead vehicle and the closing speed Δv = lead speed − ego speed, in half-second steps. The lead vehicle's speed wanders at random, and it brakes hard (3 m/s² for 2–4 s) about once every 50 s.
- **Logged driver.** An ACC-like rule plus random exploration and occasional overrides, so the logged actions vary, as {ref}`4.12's data section <wm-data-needs>` requires.
- **Sensor frame.** 64 numbers per frame. Gap and closing speed are mixed into all 64; so are six *nuisance* causes (think glare, vibration, road texture), each drawn fresh every frame with a standard deviation of 2, larger than the gap's 1.5 and the closing speed's 1.1 in the same units. Gap and closing speed explain 13% of the variance of the 64 values. Everything is linear on purpose, so the same experiment runs live in the companion.
- **Three stages, as in V-JEPA 2.** Stage 1: 400 drives of 100 s (80,000 frames), no actions recorded. Stage 2: 20 more drives (4,000 frames, 5% of stage 1) with the driver's acceleration, used to train an action-conditioned predictor in each frozen latent space with the teacher-forcing and two-step rollout loss of {ref}`V-JEPA 2-AC <jepa-vjepa2>`. Stage 3: 40 new test drives of 60 s, starting 40–60 m behind the lead.
- **Five encoders, each turning 64 numbers into 2.** An autoencoder (rebuild $x_t$); a pixel predictor (predict all 64 numbers of $x_{t+1}$ through 2 numbers); and three JEPAs that predict the next frame's embedding: with no protection, with stop-gradient plus an EMA target encoder (τ = 0.99), and with a spread-and-decorrelation penalty instead.
- **Classical baseline.** A two-gain gap controller, a = 0.2 (g − 25) + 0.7 Δv, given the true gap and closing speed, as a radar would.

```{figure} ../_static/figures/JP_Sensor.png
:alt: A heatmap of 64 sensor values over 60 seconds that looks like noise, above a line chart of the hidden gap and closing speed for the same drive.
:width: 100%

One synthetic drive: the gap and closing speed are in every frame but explain only 13% of the variance of the 64 values.
```

### Result 1: what the two latents keep

To judge each encoder, a straight-line *probe* is fitted from its 2 latents to the true gap, on half of 100 held-out drives, and scored on the other half. Labels are used only here, to grade, never to train the encoder.

| Encoder | Trained to | Probe R², gap | Probe R², closing speed | Spread of the latents |
| --- | --- | --- | --- | --- |
| reference: best straight line through all 64 values | — | 0.99 | 0.99 | — |
| autoencoder | rebuild $x_t$ | none (−0.05) | none (0.00) | 0.52 |
| pixel predictor | predict the 64 values of $x_{t+1}$ | 0.99 | 0.98 | 0.36 |
| JEPA, no protection | predict the embedding of $x_{t+1}$ | none (collapsed) | 0.06 | 0.003 |
| JEPA, stop-gradient + EMA | predict the embedding of $x_{t+1}$ | 0.99 | 0.99 | 1.90 |
| JEPA, spread + decorrelation penalty | predict the embedding of $x_{t+1}$ | 0.99 | 0.99 | 1.11 |

```{figure} ../_static/figures/JP_Latents.png
:alt: Three scatter plots of 3,000 held-out frames placed by their two latents and colored by the true gap. Autoencoder: a round cloud with colors mixed, probe R squared 0. JEPA without protection: every frame on one point. JEPA with stop-gradient and EMA: a smooth color gradient, probe R squared 0.99.
:width: 100%

Rebuilding the frame keeps the glare; predicting the next frame's latents keeps the gap.
```

The autoencoder must rebuild the frame, so its two latents go to the directions of largest variance, which are mixtures of the nuisance causes. A predictor of the next frame cannot use the glare, which is fresh every frame, so its latents go to what carries over from one frame to the next: gap and closing speed. This is related to, but not the same as, Littwin et al.'s finding in {ref}`the recipe section <jepa-recipe>`, which compares predicting embeddings with predicting pixels of the same target. Here the next paragraph shows that predicting the next frame, in either form, is what removes the glare.

The pixel predictor gets there too. In this toy, *predicting the next frame*, in pixels or in embeddings, is what strips out the glare. What the JEPA adds is that it never has to output the glare: 0.385 of the pixel predictor's 0.412 average error per value (93%) is glare and noise that no model could predict, so that loss says almost nothing about how good the latents are. In real video the pixel predictor would also have to blur or invent the unpredictable details ({ref}`opening section <jepa-why>`).

### Result 2: collapse happens fast, and looks like success

```{figure} ../_static/figures/JP_Collapse.png
:alt: Two log-scale training curves over 3,000 steps. Without protection the loss falls to about 0.002 and the latent spread to about 0.003. With stop-gradient and EMA, and with the spread penalty, the loss stays near 0.1 to 0.3 and the spread near 1 to 2.
:width: 100%

Without protection the loss falls toward zero because the encoder stops encoding: collapse looks like success on a loss curve.
```

With no protection, the loss fell from 0.68 to 0.003 in 500 steps, and the latents shrank to a single point. Judged by its loss curve alone, it is the best model in the table. With stop-gradient and EMA, nothing pins the size of the latents, so their spread drifts (between 1.4 and 2.3 after the first 1,000 steps) while the probe stays at 0.99. The penalty holds the spread near 1.

### Result 3: when the autoencoder is fine

```{figure} ../_static/figures/JP_Sweep.png
:alt: Probe R squared for the gap against the strength of each nuisance cause, from 0.25 to 3. The JEPA line stays at 0.99 throughout, on the ceiling of a straight line through all 64 values. The autoencoder line is 0.99 at 0.25, 0.97 at 0.5, 0.78 at 1.0, and below zero, drawn as 0, from 1.5 on. A dashed line marks the setting used in the example, 2.
:width: 100%

As the glare grows, the autoencoder's 2 latents stop seeing the gap; the JEPA's do not.
```

Strength here is the standard deviation of each nuisance cause, in units where the gap's is about 1.5. When the nuisance is much weaker than the gap (0.25 and 0.5), the autoencoder's latents capture the gap (R² 0.99 and 0.97). At 1.0 it already drops to 0.78, because six nuisance causes together outweigh the gap, and from 1.5 on it is gone. The JEPA stays at 0.99 throughout. Reconstruction works when the thing you need is also the biggest thing in the data; prediction works when the thing you need is the thing that persists.

### Result 4: planning toward a goal frame

The goal is one sensor frame recorded at a 25 m gap with zero closing speed, glare included. Every 0.5 s each latent planner encodes the current frame, tries 200 acceleration plans 4 s long with 5 CEM rounds, executes the first step and re-plans.

```{figure} ../_static/figures/JP_Planning.png
:alt: Gap to the lead vehicle over a 60-second test drive with two lead braking events shaded. The classical controller and the JEPA latent planner both settle near the 25 m goal; the autoencoder latent planner drifts out to about 77 m and then collides at 29 seconds. Below, the JEPA planner's acceleration is visibly jerkier than the classical controller's.
:width: 100%

Planning toward a goal frame works in the JEPA latent and fails in the autoencoder's latent (one synthetic test drive).
```

| Controller | What it sees | Collisions (of 40 drives) | RMS gap error after the first 20 s | Closest approach (worst of the 40 drives) | RMS jerk |
| --- | --- | --- | --- | --- | --- |
| classical two-gain controller | true gap and closing speed | 0 | 3.0 m | 12.1 m | 0.6 m/s³ |
| JEPA latent planner | sensor frames only | 0 | 2.7 m | 13.5 m | 3.1 m/s³ |
| pixel-predictor latent planner | sensor frames only | 0 | 2.9 m | 8.1 m | 3.2 m/s³ |
| autoencoder latent planner | sensor frames only | 28 | the other 12 drifted far off (RMS error 153 m) | 3.0 m in the 12 without a collision | 1.6 m/s³ |

The goal frame is encoded by the same encoder as the live frames. The JEPA encoder maps it to "25 m, matching speed" and ignores its glare; the autoencoder maps it to its glare, so its planner chases a target that has nothing to do with the gap.

The JEPA planner's jerk has two sources. About half comes from the sampling search itself: the same CEM planner given the exact state and exact kinematics, a check in the reproducer, still had an RMS jerk of 1.5 m/s³. The rest comes from re-planning from one noisy frame every half second. Nothing in the energy rewards comfort, while the classical controller is a fixed linear rule on exact inputs.

:::{admonition} Before you trust this result
:class: warning

**What is the baseline?** A classical gap controller with perfect measurements, and an autoencoder of the same size as the reconstruction baseline.

**How was the data split, and why is that honest?** The four data sets (stage 1, stage 2, probe drives, planning drives) are separate random drives with different seeds. The goal frame has its own glare.

**What does it do on the ugly cases?** Every planning drive includes the lead's random wandering, and 30 of the 40 include at least one hard brake; the closest approach column is the safety check. What the toy leaves out: lighting that changes slowly through a drive (predictable but useless, so a JEPA would keep it), occlusion, other road users, and futures that branch. It is linear, so even one 100-s drive gives an R² of 0.97: it cannot show why V-JEPA 2 needed a million hours. It shows the mechanism, not the scale.
:::

**Reproduce it.** Scripts, results and figures are in the class folder under `genmodels/jepa/` (about 1 minute on a laptop CPU; no GPU or deep-learning library needed). The {ref}`companion below <jepa-companion>` runs the same experiment in your browser.

(jepa-companion)=
## Interactive companion

The companion runs three parts of this page live. Tab 1 hides patches of a road scene the way I-JEPA and V-JEPA do and measures how much each scheme gives away. Tab 2 trains five small encoders on the car-following sensor of the {ref}`worked example <jepa-worked>`, including a JEPA that collapses. Tab 3 plans 60-second drives toward a goal frame, as V-JEPA 2 plans robot actions, beside a classical gap controller. It runs a smaller version of the worked example, so its numbers differ slightly from those above.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion &mdash; JEPA world models: predict the description, not the picture</span>
    <a href="../_static/companions/JEPA_World_Models_Companion.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/JEPA_World_Models_Companion.html"
          title="JEPA world models: masking, live training and planning in latent space" loading="lazy"></iframe>
</div>

(jepa-transport)=
## After V-JEPA 2, and JEPA in transportation research

Since V-JEPA 2, the JEPA line has moved three ways: simpler training without the EMA trick, richer patch-level features, and new kinds of targets. In transportation, JEPA-style training has reached LiDAR perception, end-to-end driving, driver monitoring, GPS trajectories and loop-detector networks, with clear gains in perception and planning and two instructive negative results.

### Other JEPA models, newest first

| Date | Model | What changed | Headline result |
| --- | --- | --- | --- |
| Oct 2026 | [H-JEPA](https://arxiv.org/abs/2610.06805) (Zhang et al.) | a stack of action-conditioned JEPAs, each predicting farther ahead in its own latent space, as LeCun's 2022 paper proposed | navigation success in Visual AntMaze 18% → 73% |
| Mar 2026 | [V-JEPA 2.1](https://arxiv.org/abs/2603.14482) (Mur-Labadia et al., Meta FAIR) | the loss also scores *visible* tokens; self-supervision applied at several encoder depths; one tokenizer per modality for images and video | real-robot grasping success 20 points above V-JEPA 2-AC; SSv2 77.7% |
| Mar 2026 | [LeWorldModel](https://arxiv.org/abs/2603.19312) (Maes et al.) | a JEPA world model trained end to end from pixels with two loss terms and no EMA; about 15 million weights, one GPU, a few hours | plans up to 48 times faster than world models built on large pretrained encoders |
| Dec 2025 | [VL-JEPA](https://arxiv.org/abs/2512.10942) (Chen et al.) | for vision and language: predicts the *embedding* of the answer text instead of generating it word by word | beats ordinary token-by-token training with the same vision encoder and data, using 50% fewer trainable weights |
| Nov 2025 | [LeJEPA](https://arxiv.org/abs/2511.08544) (Balestriero and LeCun) | SIGReg replaces EMA and stop-gradient ({ref}`see the recipe <jepa-collapse>`) | 79% ImageNet linear probe with a ViT-H/14 |
| Nov 2024 | [DINO-WM](https://arxiv.org/abs/2411.04983) (Zhou et al., ICML 2025) | skips stage 1: keeps a pretrained image encoder (DINOv2) frozen and trains only an action-conditioned predictor for planning | an early demonstration of planning in a pretrained feature space |

### JEPA in transportation research

| Paper | Data | What is predicted | Result against its baseline | Domain |
| --- | --- | --- | --- | --- |
| [AD-L-JEPA](https://arxiv.org/abs/2501.04969) (Zhu et al., AAAI 2026) | LiDAR: KITTI3D, Waymo, ONCE | embeddings of hidden bird's-eye-view cells; variance penalty against collapse | +2.98 mAP on ONCE after pretraining on 500K frames; 1.9–2.7× fewer GPU-hours and 2.8–4× less GPU memory than Occupancy-MAE | ADAS perception |
| [LAW](https://arxiv.org/abs/2406.08481) (Li et al., ICLR 2025) | nuScenes, NAVSIM, CARLA | next-frame scene features from current features plus the planned trajectory (JEPA-like, though not framed as JEPA, and with no EMA) | NAVSIM driving score (PDMS) 77.5 → 84.6 when the latent prediction task is added | end-to-end driving |
| [Drive-JEPA](https://arxiv.org/abs/2601.22032) (Wang et al., 2026) | V-JEPA 2 encoder, further pretrained on 330 h of front-camera driving video; tested on NAVSIM | V-JEPA objective on driving clips | same simple planner design on different pretrained encoders, each fine-tuned with it: ResNet-34 76.0, DINOv2 76.1, SigLIP 83.4, V-JEPA 2 86.1, driving-adapted 89.0 PDMS; full system 93.3 | end-to-end driving |
| [AD-E2E-JEPA](https://arxiv.org/abs/2609.34085) (Zhu, Zhang, LeCun and Choromanska, 2026) | NAVSIM | action-conditioned JEPA world model, SIGReg-regularized; plans toward a goal | with no driving policy trained and the logged future frames given as goals (a test of the world model, not a deployable driver): EPDMS 67.3 / 72.9 (256 / 8,192 candidate trajectories), 0.8 s per 256-candidate rollout; its pretrained part lifts imitation learning from 80.2 to 85.4 | driving world model |
| [TriDrive](https://arxiv.org/abs/2609.33000) (Wang et al., 2026, MOTIF Lab, USF) | 197.2 h of naturalistic BATON driving, the AIDE benchmark, an on-road study | uses frozen V-JEPA 2 road embeddings beside driver kinematics and CAN signals (it reuses the encoder; it is not trained as a JEPA) | warning probe AUROC 0.725 vs 0.563 for an openpilot-based baseline (whole systems compared, not the encoder alone), at 5 Hz on a comma four with an external GPU | driver monitoring |
| [T-JEPA](https://arxiv.org/abs/2406.12913) (Li et al., SIGSPATIAL 2024) | GPS traces: Porto taxis, T-Drive, GeoLife; Foursquare check-ins | embeddings of hidden trajectory segments | mean rank on GeoLife 1.047 vs 1.256 for the contrastive TrajCL (lower is better); slightly worse on Porto (1.074 vs 1.014) | mobility data |
| [Feng et al.](https://arxiv.org/abs/2609.31680) (2026) | METR-LA, PEMS-BAY, PEMS03/04/07/08 | embedding of the forecast window from the history window (LeJEPA objective) | helps STGCN (up to 8.26% lower MAE on PEMS-BAY), hurts ASTGCN (10.36% higher MAE on PEMS08) | traffic forecasting |
| [Pavuluri et al.](https://arxiv.org/abs/2608.01336) (2026), "Asleep at the Wheel" | nuScenes, Waymo, BDD100K | V-JEPA 2 prediction error used as a "novelty" score to pick fleet clips for review | AP 0.89 when test clips come from other datasets, but 0.29 against a chance level of 0.24 within nuScenes alone; a supervised probe on the same embeddings reached 0.50 | data curation |

**Three lessons from this table.**

1. **Video pretraining transfers to driving, and driving video helps more.** With the same simple planner design, the V-JEPA 2 encoder beat the image encoders by 2.7 to 10 PDMS points, and 330 hours of dashcam video added about 3 more. Stage 1 does not need to start from driving data, but it benefits from ending on it.
2. **It is not a free win for detector networks.** On the same PEMS and METR-LA data, JEPA pretraining helped one graph forecaster and hurt another. Test it on your backbone and your network before you claim it helps.
3. **"Hard to predict" is not "rare and important".** The novelty score mostly detected which city and camera a clip came from. A high JEPA prediction error flags anything unfamiliar, including harmless changes of camera. Split by source when you evaluate, as every "Before you trust this result" box in this course asks.

A search of the main transportation journals in October 2026 found no JEPA papers; nearly all of this work appears in computer-vision, robotics and machine-learning venues. Traffic operations, signal control and roadside cameras are open territory.

(jepa-breaks)=
## Where it breaks

A JEPA's strength, predicting only a compact description, is also the source of most of its weaknesses: you cannot look at what it predicts, and it keeps whatever is predictable, whether or not it matters.

1. **There is nothing to look at.** A video world model's imagined future can be watched and judged by an engineer; a JEPA's is a list of numbers. Checking it takes probes, decoders trained after the fact, or task results. For an agency that must explain a decision, this is a real cost.
2. **Predictable is not the same as relevant.** Slowly changing sunlight, a billboard's schedule, the shadow of an overpass: all predictable, all kept. The worked example's glare was dropped only because it was fresh every frame.
3. **Unpredictable is not the same as irrelevant.** A pedestrian stepping out from behind a parked van is unpredictable until the moment it happens. An objective that rewards predictable content gives no special room to rare, sudden events, which are the ones safety work cares about. Check rare-event performance directly; do not assume it.
4. **One future, not a spread.** LeCun's 2022 design includes a latent variable for what the context cannot determine, but V-JEPA 2-AC's predictor is deterministic. When the lead driver may or may not brake, it predicts one embedding, a kind of average. {ref}`4.12 <wm-key-equation>` explained why averaged futures mislead.
5. **Collapse can be silent.** Full collapse shows up as a near-zero loss; partial collapse, where only a few directions of the embedding stay alive, does not. Track the spread of the embeddings and a probe on a held-out labeled set during training.
6. **Goals and safety are not built in.** V-JEPA 2-AC's goal is a picture and its energy is a distance. Driving goals are rarely pictures, and "far from the goal" says nothing about a near-collision on the way there. Constraints must be added outside the energy.
7. **Slow and short-sighted for driving.** 16 seconds per action, plans one action deep, and sub-goal images for anything longer. A car needs decisions in about a tenth of a second over a horizon of several seconds.
8. **The camera matters.** V-JEPA 2-AC's inferred action axes rotated as the camera moved around the robot. A model trained on one dashcam mounting may misread actions on another; trained on internet video, it has seen little from a pole-mounted traffic camera.
9. **Prediction error is not automatically a novelty detector.** In the one study that tested it ("Asleep at the Wheel", a 2026 preprint with 83 test clips from a single dataset), the error mostly flagged unfamiliar cameras and cities, not unusual events.
10. **Stage 1 is out of reach for most labs.** By the paper's own figures, pretraining the largest model on long, sharp clips would take about 60 GPU-years, and the progressive trick cuts that by 8.4 times, to roughly 7. For a class project or a thesis, start from the released encoders and spend your compute on stage 2 and on evaluation.

(jepa-discussion)=
## Discussion: JEPA beside the world models and generators you know

JEPA is not a new kind of network; it is a choice of *what to compare in the loss*. Put that choice next to whether a model takes actions, and every model of Module 4 finds its place.

```{figure} ../_static/figures/JP_Map.png
:alt: A two by two map. Columns: the loss compares pixels or tokens; the loss compares embeddings. Rows: takes actions (a world model); no actions (an encoder or a generator). Top left: video world models such as GAIA-1 and 2, Cosmos and Genie, which you can watch but which are slow to plan with. Top right, highlighted: JEPA world models such as V-JEPA 2-AC, DINO-WM, LeWorldModel, AD-E2E-JEPA and H-JEPA. Bottom left: the generative models of 4.4 to 4.11, such as the autoencoder, MAE, VAE, GAN and diffusion. Bottom right: JEPA encoders such as I-JEPA, V-JEPA, V-JEPA 2 stage 1, LeJEPA and VL-JEPA. Dreamer and the RSSM of the 4.12 torus example straddle the two top cells: they step in latent space but are trained by rebuilding x. Below the grid, the columns read: loss compares pixels or tokens; loss compares embeddings.
:width: 100%

The models of Module 4, placed by what their loss compares and whether they take actions.
```

Read across the top row: both are world models, and they differ only in whether the imagined future is drawn or described. Read down the right column: the same JEPA training gives an encoder (stage 1 of V-JEPA 2) and, with actions added, a world model (stage 2). The {ref}`4.12 torus model <wm-torus>` sits on the line: it steps forward in latent space like a JEPA but is trained by rebuilding the link counts, like a generator.

|  | Autoencoder, MAE | VAE, diffusion | Video world model (GAIA, Cosmos) | Dreamer-style latent model (4.12 torus) | JEPA world model (V-JEPA 2-AC) |
| --- | --- | --- | --- | --- | --- |
| Trained to | rebuild x or its hidden parts | generate x from noise or a latent | generate the next frames | rebuild $x_t$ and predict the next latent | predict the next embedding |
| Takes actions | no | no | yes | yes | yes |
| Gives several possible futures | no | yes | yes | yes (random latent) | no (one prediction) |
| Can you watch its prediction? | yes | yes | yes, sharply | yes, through the decoder | no |
| Cost to plan with | — | — | high (4 min per action, {ref}`V-JEPA 2 <jepa-vjepa2>`) | low | lower (16 s per action; still slow for driving) |
| Best at | compressing, filling gaps | generating realistic samples | simulations people watch; synthetic data | control with a known reward | pretraining encoders; planning toward goals |

**Why use a JEPA at all?**

- **You have far more video than labels.** Stage 1 needs no labels and no actions, and the frozen encoder serves many tasks through small probes.
- **The details you need are a small part of what the sensor records.** The worked example's 13% is a stand-in for a dashcam frame in which the lead vehicle's motion matters and the sky does not.
- **You need to plan quickly.** Searching in embedding space is far cheaper than generating video for every candidate plan.

**When a generative world model is the better choice.** When people must see the imagined future (a stakeholder review, a safety case), when you need synthetic sensor data to train or test perception, or when the spread of possible futures matters, as in the what-if analysis of 4.12.

**When to keep the classical method.** When the state is measured (a radar gap, loop-detector counts, signal phases) and a physical model exists (car following, the CTM, HCM procedures), the learned model must beat a strong, cheap and explainable baseline. In the worked example it did not: the two-gain controller came within 0.3 m of the JEPA planner's gap error, with one fifth of its jerk. JEPA earns its place when the state is buried in raw sensor data that no one has turned into variables.

**Hybrids worth trying.** Use a frozen V-JEPA 2 encoder as the perception front end of a classical controller (embeddings in, estimated gap out, through a small probe). Or use JEPA embeddings as the condition of a diffusion generator, the unCLIP idea of {doc}`4.9 <notes7-unclip>`: the JEPA says *what* happens, the generator draws *how it looks*.

(jepa-fit)=
### Fit card

:::{admonition} Fit card &mdash; JEPA (joint-embedding predictive architecture)
:class: tip

**Idea in one sentence.** Learn an encoder by predicting the embedding of a hidden or future part of the data from the visible part, never its pixels.

**Why it works.** Unpredictable detail cannot help the prediction, so the encoder keeps what persists and predicts (objects, motion, gaps); stop-gradient with a slow target encoder, or a spread penalty, rules out the constant-output solution.

**Fits these tasks.** Pretraining encoders for camera, LiDAR and trajectory data with few labels; anticipating maneuvers; planning toward goals in a learned space. Leverage labels: *prediction*, *classification*, *extraction*.

**Needs this data.** Raw video, LiDAR sweeps, trajectories or sensor series; large and unlabeled, plus a small action-labeled set for planning; no labels to pretrain, a small labeled set to probe; from vehicle fleets, DOT camera networks, naturalistic driving studies and dashcam vendors.

**Breaks when.** The detail that matters is sudden and unpredictable; predictable but useless content dominates; collapse goes unnoticed; goals are not pictures; decisions need safety constraints and sub-second latency; the camera differs from training.

**Keep the classical method when.** The state is measured and a physical model exists (a radar gap with a car-following controller, detector counts with the CTM): cheaper, smoother, explainable.
:::

(jepa-summary)=
## Summary, check yourself, and references

### Summary

1. **A JEPA predicts a description, not a picture.** It predicts the embedding of a hidden or future part of the data from the visible part, so it is free to drop what cannot be predicted, such as glare or moving leaves.
2. **The recipe has three networks.** A context encoder and a predictor are trained; a target encoder, a slow EMA copy of the context encoder, makes the targets. V-JEPA and V-JEPA 2 score the guess with an L1 distance in embedding space.
3. **Collapse is the built-in failure.** Constant outputs make the loss zero. Stop-gradient with a slow target encoder (I-JEPA, V-JEPA, V-JEPA 2) or a penalty that keeps embeddings spread out (VICReg, LeJEPA's SIGReg) prevents it.
4. **I-JEPA** predicts four large target blocks from one big context block. It beat a masked autoencoder of the same size on frozen-encoder tests (79.3% vs 77.2% on ImageNet) with about a fifth of the training epochs; the same model trained on pixels did far worse (40.7% vs 66.9% with 1% of labels).
5. **V-JEPA** turns video into tubelets and hides the same blocks in every frame, about 90% of each clip, so the model must predict motion rather than copy it.
6. **V-JEPA 2** pretrains a 1-billion-weight encoder on over 1 million hours of video, then trains a 300-million-weight action-conditioned predictor on under 62 hours of robot video, then plans by searching for the actions whose imagined embedding is closest to a goal image's. It chose robot actions in 16 s where a video-generation world model needed 4 minutes.
7. **The worked example** showed the mechanism: rebuilding a frame keeps its biggest source of change (glare), predicting the next frame keeps what persists (the gap); an unprotected JEPA collapsed in 500 steps; planning in the JEPA latent held the gap as well as a classical controller, with five times its jerk, while the autoencoder's latent crashed in 28 of 40 drives.
8. **In transportation**, JEPA training has helped LiDAR perception and end-to-end driving, a JEPA-pretrained encoder has been used inside a driver-monitoring system, results for detector-network forecasting are mixed, and in one study its prediction error was a poor novelty detector. When the state is measured and a physical model exists, keep the classical method.

### Check yourself

1. A DOT has three years of video from 400 freeway cameras and 2,000 frames labeled "lane blocked". Would you pretrain a masked autoencoder or a JEPA, and how would you check that the encoder learned something useful *before* paying for more labels?
2. Your JEPA's training loss falls to almost zero in the first hour. What two quantities do you check, and what are the two families of fixes if the check fails?
3. A colleague proposes V-JEPA 2-AC-style planning for adaptive cruise control on a test vehicle that has a radar. Using the worked example, argue for or against.
4. For a stakeholder meeting about a new signal plan, the agency wants to *see* what the model expects at the intersection. Would you build a JEPA world model or a generative video world model? What would you lose with the other choice?
5. A fleet operator wants to flag unusual dashcam clips by their JEPA prediction error. What does the "Asleep at the Wheel" result tell you to change in how the flagging is evaluated?
6. Which part of V-JEPA 2's design would need the biggest change before it could plan freeway lane changes in real time, and why?
7. In the worked example the autoencoder was fine when the glare was weak. Name one transportation sensor where reconstruction would keep the quantity you need, and one where it would not.

(jepa-references)=
### References

**The core papers**

- LeCun, Y. (2022). [A Path Towards Autonomous Machine Intelligence](https://openreview.net/forum?id=BZ5a1r-kVsf), version 0.9.2. OpenReview.
- Assran, M., et al. (2023). [Self-Supervised Learning from Images with a Joint-Embedding Predictive Architecture](https://arxiv.org/abs/2301.08243) (I-JEPA). CVPR 2023.
- Bardes, A., et al. (2024). [Revisiting Feature Prediction for Learning Visual Representations from Video](https://arxiv.org/abs/2404.08471) (V-JEPA).
- Assran, M., et al. (2025). [V-JEPA 2: Self-Supervised Video Models Enable Understanding, Prediction and Planning](https://arxiv.org/abs/2506.09985). Code and released encoders: [github.com/facebookresearch/vjepa2](https://github.com/facebookresearch/vjepa2).

**Collapse and why JEPA works**

- Grill, J.-B., et al. (2020). [Bootstrap Your Own Latent](https://arxiv.org/abs/2006.07733) (BYOL). NeurIPS 2020.
- Bardes, A., Ponce, J., and LeCun, Y. (2022). [VICReg: Variance-Invariance-Covariance Regularization for Self-Supervised Learning](https://arxiv.org/abs/2105.04906). ICLR 2022.
- Balestriero, R., and LeCun, Y. (2025). [LeJEPA: Provable and Scalable Self-Supervised Learning Without the Heuristics](https://arxiv.org/abs/2511.08544).
- Littwin, E., et al. (2024). [How JEPA Avoids Noisy Features: The Implicit Bias of Deep Linear Self Distillation Networks](https://arxiv.org/abs/2407.03475).

**After V-JEPA 2**

- Mur-Labadia, L., et al. (2026). [V-JEPA 2.1: Unlocking Dense Features in Video Self-Supervised Learning](https://arxiv.org/abs/2603.14482).
- Maes, L., et al. (2026). [LeWorldModel: Stable End-to-End Joint-Embedding Predictive Architecture from Pixels](https://arxiv.org/abs/2603.19312).
- Chen, D., et al. (2025). [VL-JEPA: Joint Embedding Predictive Architecture for Vision-language](https://arxiv.org/abs/2512.10942).
- Zhang, W., et al. (2026). [H-JEPA: End-to-End Learning of Hierarchical World Models for Visual Planning](https://arxiv.org/abs/2610.06805).
- Zhou, G., Pan, H., LeCun, Y., and Pinto, L. (2025). [DINO-WM: World Models on Pre-trained Visual Features enable Zero-shot Planning](https://arxiv.org/abs/2411.04983). ICML 2025.
- Agarwal, N., et al. (2025). [Cosmos World Foundation Model Platform for Physical AI](https://arxiv.org/abs/2501.03575).

**Transportation applications**

- Zhu, H., et al. (2026). [Self-Supervised Representation Learning with Joint Embedding Predictive Architecture for Automotive LiDAR Object Detection](https://arxiv.org/abs/2501.04969) (AD-L-JEPA). AAAI 2026.
- Li, Y., et al. (2025). [Enhancing End-to-End Autonomous Driving with Latent World Model](https://arxiv.org/abs/2406.08481) (LAW). ICLR 2025.
- Wang, L., et al. (2026). [Drive-JEPA: Video JEPA Meets Multimodal Trajectory Distillation for End-to-End Driving](https://arxiv.org/abs/2601.22032).
- Zhu, H., Zhang, W., LeCun, Y., and Choromanska, A. (2026). [AD-E2E-JEPA: A Joint-Embedding Predictive Architecture for End-to-End Autonomous Driving](https://arxiv.org/abs/2609.34085).
- Wang, Y., et al. (2026). [TriDrive: Joint Driver, Vehicle, and Road Modeling for Forecasting and Driver Monitoring](https://arxiv.org/abs/2609.33000).
- Li, L., Xue, H., Song, Y., et al. (2024). [T-JEPA: A Joint-Embedding Predictive Architecture for Trajectory Similarity Computation](https://arxiv.org/abs/2406.12913). ACM SIGSPATIAL 2024.
- Feng, Y., et al. (2026). [Does Joint-Embedding Predictive Architecture Pretraining Help Time Series Forecasting?](https://arxiv.org/abs/2609.31680)
- Pavuluri, A., et al. (2026). [Asleep at the Wheel: JEPA's Limitations in Evaluating Novel Driving Data](https://arxiv.org/abs/2608.01336).

**In this course:** {ref}`1.5 <linear-head>` (linear probes), {doc}`2.5 <../module2/notes5-bert>` (BERT's masking), {doc}`2.7 <../module2/notes7-vision>` (Vision Transformer), {doc}`2.10 <../module2/notes10-detr>` (DETR's learned queries), {doc}`4.4 <notes2c-autoencoders>`–{doc}`4.5 <notes2d-deep-autoencoders>` (autoencoders and masked autoencoders), {doc}`4.7 <notes4-gan>` (why an average of futures misleads), {doc}`4.9 <notes7-unclip>` (unCLIP), {doc}`4.12 <notes11-world-models>` (world models). The worked example's scripts are in the course folder under `genmodels/jepa/`; the {ref}`companion <jepa-companion>` runs it live.

---

Previous: {doc}`4.12 World models <notes11-world-models>`. Next: {doc}`Further reading: generative models in transportation <notes10-reading-library>` &mdash; the closing page of the module. Back to the {doc}`Module 4 map <index>`.
