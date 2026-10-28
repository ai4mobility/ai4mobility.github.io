(diffusion-literature)=
# 4.12 Diffusion in the literature: from image generators to safety scenarios

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 4 &middot; Section 4.12</span>
    <span class="notes-card-session">Session: Diffusion</span>
  </div>
  <p class="notes-card-lede">The recipe that turns a sentence into a picture now generates driving scenarios, including the rare, dangerous ones that safety testing needs. Part A reads the handful of papers that taught diffusion to make images, one change at a time. Part B shows how transportation research reuses the same recipe for agent motion, whole scenes and camera or LiDAR data, works one synthetic left-turn example, and lists the checks a generated scenario must pass before you trust it.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Read it before</h4>
      <ul>
      <li><a href="notes6-diffusion-basics.html">4.10 Diffusion models: the basics</a></li>
      <li><a href="notes7-unclip.html">4.11 Reading unCLIP</a>: from a CLIP embedding back to an image</li>
      </ul>
    </div>
    <div>
      <h4>Interactive companion</h4>
      <ul><li><a href="../_static/companions/Diffusion_Transportation_Papers_Companion.html" target="_blank" rel="noopener">How diffusion works in 35 transportation papers &#8599;</a>, mounted after Part B</li></ul>
    </div>
  </div>
</div>

## What this section covers

- The map: the three things every milestone diffusion paper changed
- Part A: DDPM, guidance, latent diffusion, text-to-image, transformer denoisers, ControlNet and video, each with what it means for transportation
- Part B: how a driving scenario becomes something a diffusion model can generate, and four patterns across 35 transportation papers
- The interactive companion: how diffusion works in 35 transportation papers
- Safety scenarios: the data the models learn from, five ways to get a dangerous scenario out, and the key papers, five of them up close
- A worked example: steering a scenario model toward conflicts at one synthetic left-turn intersection
- From scenario to sensor data: models that draw camera video and LiDAR from a road layout
- Judging a generated scenario, where it breaks, fit card, applications, six questions and four project ideas

The training recipe that lets a model turn a sentence into a picture is now used to generate driving scenarios, including the rare, dangerous ones that safety testing needs. This page follows that path in two parts. Part A walks through the handful of papers that taught diffusion models to make images. Part B shows how transportation research reuses the same recipe, with most of the space on generating driving and intersection scenarios for safety.

This page comes after {doc}`4.10 Diffusion models: the basics <notes6-diffusion-basics>`, which built one noise step, the training loss and sampling on real I-405 speeds and the course's CTM heatmaps. Here we do not re-derive any of that; we read papers. It also builds on the *Generating Crash Data from Near-Misses* handout, which explained why a generated crash is not a crash rate. That point comes back in {ref}`Judging a generated scenario <dlit-judging>`.

**After this page you can:**

1. Say what each milestone paper changed (the data, where the denoising happens, or how the output is steered) and why that change mattered.
2. Explain how a text prompt, a road layout or a safety cost gets into a diffusion model.
3. Describe how a driving or intersection scenario is turned into something a diffusion model can generate, and what data that takes.
4. Read a scenario-generation paper and ask the right questions: what is generated, what steers it, and how realism and danger were judged.
5. Decide when diffusion is the right tool for a safety study, and when a simulator, a crash database or extreme-value statistics is the better one.

**Words and symbols.** We keep the notation of 4.10. Papers use different letters for the same things, so here is the translation:

| On this page (and in 4.10) | In most papers | What it is |
| --- | --- | --- |
| x | x₀ | A clean training example: an image, or a scenario |
| z\_t | x\_t | The noisy version of x after t noise steps |
| g(z\_t, w, t) | ε\_θ(x\_t, t) | The network's guess of the noise; w are its weights |
| c | c, y | The condition: a class label, a caption, a road map |
| λ | w, s, "guidance scale" | How hard sampling is pushed toward the condition |

Each paper in Part A gets the same four lines: the problem it solved, what changed, what it showed, and why it matters for transportation.

(dlit-map)=
## The map: three questions every paper answers

Almost every diffusion paper since 2020 changed one of three things: how the model learns and samples, where the denoising runs, or how the output is steered. Reading a new paper, ask which of the three it changed. That one question tells you most of what is new.

```{figure} ../_static/figures/DL_Milestones.png
:alt: Three columns of boxes joined by downward arrows. Column 1, how it learns and samples: DDPM, 2020 (name the noise; 1,000 steps), then DDIM and Improved DDPM, 2021 (faster sampler; cosine schedule), then flow matching, 2022 to 2023 (straighter paths from noise). Column 2, where the denoising runs: pixels, 2020 to 2021 (DDPM, ADM: every pixel), then latent space, 2022 (Stable Diffusion: a VAE shrinks the image first), then transformers, 2023 to 2024 (DiT, SD3, Flux: patches become tokens, no U-Net). Column 3, how the output is steered: classifier guidance, 2021 (ADM: a second network pushes toward a label), then classifier-free, 2021 (train with and without the condition; push on the gap), then text prompts, 2022 (GLIDE, DALL·E 2, Imagen: a text encoder feeds the net), then layouts and boxes, 2023 (ControlNet, GLIGEN: edges, depth, boxes as conditions), then better captions, 2023 (DALL·E 3: retrain on long, detailed synthetic captions). Arrows from the bottom of all three columns lead into a band at the bottom, Part B, transportation research reuses all three, with two boxes: trajectories, CTG, 2023 on (a map and safety rules steer the agents), and sensor views, MagicDrive, 2024 on (a road layout and boxes steer the cameras).
:width: 100%

Every milestone paper changed one of three things. Milestone papers grouped by what they changed; years of the main publication.
```

Read each column top to bottom: each box kept what came before it and changed one thing. Part B reuses all three columns. A scenario model is trained like DDPM, often denoises with a transformer, and is steered with the same guidance ideas, only with a road map or a safety rule in place of a caption.

(dlit-part-a)=
## Part A: how diffusion learned to make images

In about four years, six ideas took diffusion from 32×32 thumbnails to photorealistic 1024×1024 images drawn from a sentence. Each is told below as the problem, what changed, what it showed, and what it means for transportation.

One measuring stick first. Most papers report **FID** (Fréchet Inception distance). It passes real and generated images through a pretrained image network and compares the two clouds of features. Lower is better. FID compares models only on the same dataset.

### Learn to name the noise (2020–2021)

[DDPM](https://arxiv.org/abs/2006.11239) (Ho, Jain & Abbeel, NeurIPS 2020) made diffusion work. Earlier versions of the idea gave poor samples. DDPM trained one network to name the noise at a random step, with plain squared error and no weighting, over T = 1,000 steps. That is the loss in {ref}`4.10, Training <diffusion-training>`. It reached an FID of 3.17 on CIFAR-10, the best unconditional score at the time, and made 256×256 faces, bedrooms and churches.

[Score-based SDEs](https://arxiv.org/abs/2011.13456) (Song et al., ICLR 2021) showed that the noise guess and the *score* are the same direction (the going-deeper box in {ref}`4.10, Training <diffusion-training>`), in continuous time. That is why papers say "score-based" and "diffusion" for one family.

Two 2021 papers cut the cost of sampling. [DDIM](https://arxiv.org/abs/2010.02502) (Song, Meng & Ermon, ICLR 2021) kept the trained network and changed only the sampler: it skips steps and runs 10 to 50 times faster. [Improved DDPM](https://arxiv.org/abs/2102.09672) (Nichol & Dhariwal, ICML 2021) added the cosine noise schedule the course models use. It also learned each step's spread, so 50 to 100 steps gave good samples. [Consistency models](https://arxiv.org/abs/2303.01469) (Song et al., ICML 2023) later went to a single step.

*For transportation:* every scenario model in Part B trains the DDPM way. Sampling cost matters when a test campaign needs tens of thousands of scenarios.

(dlit-guidance)=
### Steer the sample: guidance (2021–2022)

[Diffusion Models Beat GANs](https://arxiv.org/abs/2105.05233) (Dhariwal & Nichol, NeurIPS 2021) introduced **classifier guidance**. Diffusion still trailed GANs on ImageNet, with no way to trade variety for quality. The fix: a separately trained classifier looks at the noisy image, and at each step its gradient pushes the noise guess toward the requested class. With guidance, ImageNet 256×256 FID fell from 10.94 to 4.59, the first time diffusion beat the best GAN. Turning the guidance up traded diversity for fidelity.

[Classifier-free guidance](https://arxiv.org/abs/2207.12598) (Ho & Salimans; NeurIPS 2021 workshop, full paper 2022) dropped the second network. One network learns with and without the condition, because the condition is hidden at random during training. Hiding it 10% or 20% of the time worked about equally; 50% was worse. At sampling, ask twice and push on the gap, exactly as in {ref}`4.10, Steering <diffusion-steering>`: g = g\_without + (1 + λ)(g\_with − g\_without). A little guidance gave the best FID; strong guidance gave the most typical-looking images.

Papers write the strength differently. Ho & Salimans' w is our λ. GLIDE and Stable Diffusion use a "guidance scale" s = 1 + λ, so Stable Diffusion's common default of 7.5 means λ = 6.5.

*For transportation:* guidance is the main lever in Part B. Replace the classifier's gradient with the gradient of any smooth cost, such as "these two cars are close", and you have a safety-critical scenario generator ({ref}`safety scenarios <dlit-safety>`).

### Denoise a compressed picture: latent diffusion (2022)

[Latent Diffusion Models](https://arxiv.org/abs/2112.10752) (Rombach et al., CVPR 2022) asked why every pixel of a large image should be denoised hundreds of times. They trained an autoencoder once, then ran diffusion on its latents. They tried shrinking factors f from 1 to 32 and found f = 4 and 8 best; f = 8 turns a 512×512×3 image into 64×64×4. Text and layouts enter through cross-attention. Semantic maps, which line up with the image cell by cell, are stacked onto the latent instead.

[Stable Diffusion v1](https://github.com/CompVis/stable-diffusion) is the openly released version: an 860M-weight U-Net and a frozen 123M-weight CLIP ViT-L/14 text encoder, trained on subsets of LAION-2B(en). Its later v1 checkpoints hid the text 10% of the time to enable classifier-free guidance ([model card](https://huggingface.co/CompVis/stable-diffusion-v1-4)).

*For transportation:* the AE and VAE of {doc}`4.5–4.8 <notes2c-autoencoders>` become a component, and driving-video generators ({ref}`sensor data <dlit-sensor>`) denoise latents too, since six cameras of video dwarf one photo. Note the two ways a condition enters. A bird's-eye road map lines up with the scene, so it can be stacked; a list of boxes or a sentence does not, so the network attends to it.

### Read a sentence: text to image (2022–2023)

- [GLIDE](https://arxiv.org/abs/2112.10741) (Nichol et al., ICML 2022) built a 3.5B-weight text-conditional diffusion model. Human raters preferred classifier-free guidance over guidance by a CLIP model, for both realism and caption match.
- [DALL·E 2](https://arxiv.org/abs/2204.06125) (Ramesh et al., 2022) used two stages. A *prior* turns the caption into a CLIP image embedding; a diffusion decoder draws a 64×64 image from it; two diffusion upsamplers take it to 256 and then 1024 pixels.
- [Imagen](https://arxiv.org/abs/2205.11487) (Saharia et al., NeurIPS 2022) read prompts with a frozen T5-XXL, a language model trained on text only. It reached FID 7.27 on COCO without training on COCO. Growing the text encoder helped far more than growing the image network.
- [DALL·E 3](https://cdn.openai.com/papers/dall-e-3.pdf) (Betker et al., 2023) attacked prompt following. Web captions are short and sloppy, so the model was retrained on 95% long, descriptive captions written by a captioning model and 5% originals.

*For transportation:* a pretrained language model can read a scenario description. But your labels are the captions, and they limit control. A crash file labelled only "rear-end" cannot be steered by "rear-end at dusk on a wet curve". DALL·E 3's answer, rewriting the labels richly, is open to you too.

### Bigger denoisers, straighter paths (2023–2024)

[DiT](https://arxiv.org/abs/2212.09748) (Peebles & Xie, ICCV 2023) replaced the U-Net with a vision transformer over latent patches. FID fell steadily as compute grew, reaching 2.27 on ImageNet 256×256 with guidance (9.62 without).

[Flow matching](https://arxiv.org/abs/2210.02747) (Lipman et al., ICLR 2023) and [rectified flow](https://arxiv.org/abs/2209.03003) (Liu, Gong & Liu, ICLR 2023) train the network to predict a velocity along a straight path from noise to data. Straight paths need fewer steps. [Stable Diffusion 3](https://arxiv.org/abs/2403.03206) (Esser et al., ICML 2024) combined rectified flow with a transformer that gives text and image tokens separate weights but one joint attention. It scaled to 8B weights and three text encoders. Flux (Black Forest Labs, 2024) is a 12B-weight model in the same line ([architecture report](https://arxiv.org/abs/2507.09595)).

*For transportation:* a scenario is already a set of tokens (agents × time steps), so most scenario models in Part B denoise with a transformer.

(dlit-control)=
### Control with maps and boxes (2023)

[ControlNet](https://arxiv.org/abs/2302.05543) (Zhang, Rao & Agrawala, ICCV 2023) adds a picture-shaped condition (edges, depth, segmentation, pose) to a frozen Stable Diffusion. It trains a copy of the encoder that reads the condition, joined to the locked model through zero-initialized layers, so training starts from the unchanged model. It worked with fewer than 50,000 training pairs and with over a million. [GLIGEN](https://arxiv.org/abs/2301.07093) (Li et al., CVPR 2023) places objects by bounding box: it freezes the model and adds new gated attention layers that read each box and its phrase.

*For transportation:* these are the templates for "draw this road with these vehicles here". MagicDrive and similar models ({ref}`sensor data <dlit-sensor>`) feed a road map and 3D boxes the same way. Because the base model stays frozen, a few thousand labelled agency images can be enough to add control.

### From pictures to video (2022–2023)

[Video Diffusion Models](https://arxiv.org/abs/2204.03458) (Ho et al., NeurIPS 2022) stretched the image U-Net over space and time and trained on images and videos together. [Stable Video Diffusion](https://arxiv.org/abs/2311.15127) (Blattmann et al., 2023) trained in three stages: images, then low-resolution video from 580M clips filtered to 152M, then high-resolution fine-tuning on a small, clean set.

*For transportation:* driving world models generate dashcam video this way. The hard part is time: the same truck must stay the same truck for the whole clip.

### The papers at a glance

| Paper | What it changed | Reused in transportation as |
| --- | --- | --- |
| DDPM, 2020 | Train by naming the noise | The training recipe of every scenario model |
| DDIM, Improved DDPM, 2021 | Fewer sampling steps; cosine schedule | Affordable test campaigns |
| Classifier guidance (ADM), 2021 | A gradient pushes each step toward a label | Cost guidance toward conflicts |
| Classifier-free guidance, 2021 | One network, with and without the condition | Steering by labels, maps or text |
| Latent diffusion, Stable Diffusion, 2022 | Denoise an autoencoder's latents | Latent video and LiDAR generators |
| GLIDE, DALL·E 2, Imagen, 2022 | A text encoder feeds the denoiser | Scenarios described in words |
| DALL·E 3, 2023 | Better captions, not a new network | Richer labels for your own data |
| DiT, 2023; SD3 and Flux, 2024 | Transformer denoisers; straighter flow paths | Agent-token denoisers |
| ControlNet, GLIGEN, 2023 | Frozen model plus a map or box branch | Road-layout and 3D-box control |
| Video diffusion, 2022–2023 | Denoise space and time together | Dashcam and multi-camera world models |

(dlit-part-b)=
## Part B: from pictures to scenarios

To generate a driving scenario with diffusion, you change what x is and what c is. The training loop, the sampler and the guidance stay the same.

An image is a grid: height × width × three colours. A scenario is also a grid: agents × time steps × state, where the state is position, heading and speed. You have drawn one row of that grid many times: one agent's positions over time is a trajectory on a time–space diagram. The {ref}`worked example <dlit-worked>` draws its scenarios exactly that way.

|  | Image generation | Scenario generation |
| --- | --- | --- |
| x, what is generated | Pixels: height × width × 3 | Agents × time steps × (x, y, heading, speed), sometimes actions instead |
| c, the condition | A caption | The lane map, the agents' recent past, a rule, a sentence |
| The denoiser | A U-Net or a transformer over image patches | A transformer whose tokens are agents and time steps, attending to map tokens |
| Steering | Classifier-free guidance toward the caption | Guidance with a cost (collision, off-road, a traffic rule), or fixing some agents and filling in the rest |
| Checking a sample | FID; human raters | Realism scores against logged traffic; collision and off-road rates; time-to-collision |

**What gets generated.** Transportation papers use diffusion at four levels. This page covers the first three; the *Generative Models in Transportation* applications handout covers city-scale and traffic-state uses.

| Level | What is generated | Examples | Safety use |
| --- | --- | --- | --- |
| Agent motion | Future trajectories of every agent, given the map and their recent past | CTG, MotionDiffuser, VBD, Safe-Sim | Stress-test a planner with reacting traffic |
| Whole scenes | Where agents start, sometimes the lanes too, plus their motion | Scenario Diffusion, SceneDiffuser, SLEDGE | New test scenes beyond the recorded logs |
| Sensor data | Camera video or LiDAR for a given layout | MagicDrive, Panacea, LidarDM ({ref}`sensor data <dlit-sensor>`) | Test perception and end-to-end driving |
| City-scale mobility | GPS trajectories, trips | [DiffTraj](https://arxiv.org/abs/2304.11582) (Zhu et al., NeurIPS 2023) | Synthetic data that protects privacy; not a safety tool |

One design choice divides the motion papers. Some generate positions directly, so a sample can break physics, for example by stopping faster than tyres allow. Others, such as [CTG](https://arxiv.org/abs/2210.17366), generate each vehicle's actions (acceleration and yaw rate) and roll them through a simple unicycle model, so every trajectory is kinematically consistent by construction. The {ref}`worked example <dlit-worked>` takes a third route: it generates positions, but only in a space compressed from real trajectories.

**One recipe, six questions.** The course companion {ref}`How diffusion works in 35 transportation papers <diffusion-papers-library>`, mounted below, reads scenario, sensor-data and traffic-data papers with the same six questions. The figure shows where each question sits in the recipe. The {ref}`key papers <dlit-key-papers>` below use the same numbers.

```{figure} ../_static/figures/DL_Recipe_Six_Questions.png
:alt: Two rows of boxes. Top row, training, repeated on recorded data: box 1, recorded x (paths, images, speeds), arrow to noisy z_t (x plus noise at step t), arrow to box 3, the denoiser network (reads z_t, t and c), arrow to box 4, graded guess (noise, clean x, or velocity). A dashed box 2, condition c (map, history, boxes, text), points up into the denoiser. Bottom row, sampling, generate something new: pure noise (or a noised proposal), arrow to box 5, same network, many small steps (remove a little noise each step, reading c), arrow to generated x (a scenario, video, or speed field). Box 6, steering (guidance cost, labels, fixed values), points down into the sampling box.
:width: 100%

Training (top) and sampling (bottom) are the same in every paper. What changes is what is noised (1), what the network reads besides the noisy data (2), the network itself (3), what its output is graded against (4), how it samples (5) and how it is steered (6).
```

Put the 35 papers side by side and four patterns stand out:

- **The network follows the data.** 16 papers denoise with a U-Net, 15 with a transformer, and 4 do not say. Trajectory and scene models mostly use transformers that attend across agents and time. Camera and LiDAR models mostly reuse an image U-Net, often Stable Diffusion's.
- **Big data is compressed first.** 12 papers denoise an autoencoder's latents, among them nearly every camera and LiDAR generator. Trajectory models usually denoise the raw numbers, which are small to begin with.
- **Three ways to grade, one idea.** 15 papers grade the network on the noise, 11 on the clean data, 4 on a velocity, and 5 do not say. As {ref}`4.10 <diffusion-training>` showed, these carry the same information.
- **Steering is where the transportation problem lives.** 12 papers push every step with a cost or a classifier, including 8 of the 9 safety-scenario papers. Sampling takes from 2 steps (DiffusionDrive) to 500 (PMA-Diffusion).

(diffusion-papers-library)=
## How diffusion works in 35 transportation papers

The {ref}`reading library <generative-reading-library>` on the closing page of this module asks what each paper
generates. This companion asks how the diffusion part works. It takes the recipe of {doc}`4.10 <notes6-diffusion-basics>`
into 35 published papers: safety-critical driving scenarios, whole-scene simulation, motion prediction and planning,
camera and lidar data for automated driving, traffic data (detector gaps, OD flows, trips), and road-damage images.
Each card shows the paper&rsquo;s architecture figure and answers the six questions of the recipe figure above, in the
same order: what is noised, what the network reads besides the noisy data, which network does the denoising, how it
is trained, how it samples, and how the output is steered.

Keep one idea from 4.10 in mind: diffusion is a way to train a network, not a network. The same recipe runs on a
transformer that denoises vehicle paths and on a U-Net that denoises camera images. Filter by **Steering** to compare
how papers push a model of normal traffic toward conflicts, or by **Denoises in** to see which papers first compress
their data. End at **How a hint reaches the model**: the five places a hint (a map, a sentence, a cost, observed
values, a draft) can enter the sampling loop, and which route fits which transportation job.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion &mdash; How diffusion works in 35 transportation papers</span>
    <a href="../_static/companions/Diffusion_Transportation_Papers_Companion.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/Diffusion_Transportation_Papers_Companion.html"
          title="How diffusion works in thirty-five transportation papers: what is noised, the network, training, sampling and steering" loading="lazy"></iframe>
</div>

(dlit-safety)=
## Generating driving and intersection scenarios for safety

A safety test needs the scenarios that recorded traffic rarely shows: the left-turner who misjudges the gap, the pedestrian behind the bus. Diffusion helps in two places. A scenario model generates the motion of every agent and can be steered toward conflicts (the first four parts below). A sensor model then draws what cameras or LiDAR would record in that scenario ({ref}`the last part <dlit-sensor>`).

(dlit-data)=
### What the models learn from

Most scenario models learn from automated-vehicle logs, not from the intersection datasets traffic engineers use.

| Dataset | What it records | Used by (papers in this section) |
| --- | --- | --- |
| [Waymo Open Motion](https://arxiv.org/abs/2104.10133) | Over 100,000 scenes of 20 s at 10 Hz; over 570 h in six US cities | MotionDiffuser, SceneDiffuser, VBD, LangTraj |
| nuScenes | 5.5 h of driving in two cities (as described in the CTG paper) | CTG, Safe-Sim, AdvDiffuser, CCDiff |
| nuPlan | Driving logs built for testing planners | SLEDGE, LangTraj, Safe-Sim (testing) |
| Argoverse 2 | 250,000 scenarios, six regions, 763 h | Scenario Diffusion |
| [INTERACTION](https://arxiv.org/abs/1910.03088) | Drone and traffic-camera video of roundabouts, signalized and stop-controlled intersections and merges; includes near-collisions and a few slight real collisions | DJINN |
| [inD](https://arxiv.org/abs/1911.07602) | Drone video of four German intersections: over 11,500 road users in about 10 h | none |
| [rounD](https://levelxdata.com/round-dataset/) | Drone video of three German roundabouts: about 13,740 road users | none |
| [SinD](https://arxiv.org/abs/2209.02297) | One two-phase signalized intersection in Tianjin: 7 h, over 13,000 road users (62.6% pedestrians, cyclists and other vulnerable users), signal states, red-light violations | none |

The empty cells are the point. Of the 17 diffusion scenario papers checked for this page, only [DJINN](https://arxiv.org/abs/2309.12508) trains on INTERACTION, and none uses inD, rounD or SinD. Diffusion models have been trained on rounD to predict trajectories ([Westny & Olofsson, 2024](https://arxiv.org/abs/2403.11643)), but, as far as we found, not to generate safety scenarios. None of the 17 reports post-encroachment time (PET) either; they measure collisions, off-road driving and time-to-collision. Intersection data and the conflict measures of traffic safety are an open lane for a transportation engineer ({ref}`project ideas <dlit-check>`).

(dlit-five-ways)=
### Five ways to get a dangerous scenario out

A model trained on everyday traffic samples everyday traffic, which is almost always safe. Every paper adds a step that tilts sampling toward danger. There are five main ways.

```{figure} ../_static/figures/DL_Five_Routes.png
:alt: The sampling loop drawn left to right: start (pure noise) leads to the denoiser network (reads z_t, t and c), which leads to the clean guess x-hat (this step's best guess of x). An arrow labelled next step, a little less noise, loops from the clean guess back to the denoiser; after the last step the clean guess leads to the finished samples. Five numbered boxes show where a hint can enter: 2, head start (a draft, partly noised), points into the start; 4, condition (map, tracks, layout, text, label), drawn dashed, points into the network; 1, guide (a cost: collision, off-road), points into the clean guess; 3, fill in (paste observed values), points up into the clean guess; 5, select (keep the best of many), points up into the finished samples. Legend: a dashed box is built in when the network is trained and needs the hint paired with x; a solid box is added when you generate, after training.
:width: 100%

The five ways below, placed on the sampling loop. Only way 4 changes training: the hint must be paired with each training example. The other four are added when you sample. A crash is too rare in the logs to pair, which is why 8 of the 9 safety-scenario papers in the companion use way 1. Conditioning works when the hint is something every example carries: a sentence people wrote about each scenario (LangTraj), or the smallest gap between two vehicles, which Wang et al. then ask to be zero.
```

**1. Add a cost to every denoising step.** This is the most common route, and the one the worked example uses. Choose a cost J that is low for the scenario you want, such as the closest distance between two vehicles. At every step, change the noise guess so that the clean-scenario guess slides downhill on J:

$$
\tilde{g} \;=\; g(z_t,\, w,\, t) \;+\; \lambda\,\sqrt{1-\alpha_t}\;\; \nabla_{z_t}\, J(\hat{x}), \qquad \hat{x} \;=\; \dfrac{z_t - \sqrt{1-\alpha_t}\; g(z_t, w, t)}{\sqrt{\alpha_t}}
$$

| Symbol | Meaning |
| --- | --- |
| g(z\_t, w, t) | The network's guess of the noise, as in 4.10 |
| x̂ | The clean scenario that guess implies at this step: every agent's positions over time |
| J(x̂) | The cost, in metres or seconds: low for the scenario you want |
| ∇\_{z\_t} J | The direction that would raise J fastest, found by backpropagating through the network |
| λ | Guidance strength, a number you choose |
| √(1 − α\_t) | Scales the push with the noise level: large early, small near the end |

*In words:* this is classifier guidance ({ref}`Steer the sample <dlit-guidance>`) with a cost in place of the classifier. Adding the gradient to the noise guess moves the next, less noisy step toward lower cost. The costs in the papers are rule scores in signal temporal logic ([CTG](https://arxiv.org/abs/2210.17366)), distance, collision and time-to-collision to the tested vehicle ([Safe-Sim](https://arxiv.org/abs/2401.00391)), a learned adversarial reward ([AdvDiffuser](https://arxiv.org/abs/2410.08453)), and a loss that GPT-4 writes from a sentence ([CTG++](https://arxiv.org/abs/2306.06344)).

:::{admonition} Going deeper &mdash; where the plus sign comes from
:class: dropdown
Classifier guidance subtracts √(1 − α\_t) ∇ log p(y | z\_t) from the noise guess, which pushes uphill on the probability of the wanted outcome y. Treat "dangerous" as more likely the lower the cost: p(y | x) ∝ exp(−J(x)). Then −∇ log p = ∇J, and the minus becomes a plus. The cost is evaluated at the clean guess x̂ rather than at z\_t, because a distance between two cars means nothing in a scenario that is mostly noise. MotionDiffuser does the same. Dhariwal & Nichol (2021); Chung et al. (2023), [Diffusion Posterior Sampling](https://arxiv.org/abs/2209.14687).
:::


**2. Pick an adversary and give it a head start.** Safe-Sim picks one nearby agent as the adversary, by lane or by distance. It starts denoising from a noised copy of a rule-based plan for the chosen collision type, so the model only finishes the job. [VBD](https://arxiv.org/abs/2404.02524) steers an agent toward its predicted behaviour most likely to collide with the tested vehicle's plan.

**3. Fix some values and let the model fill in the rest.** [SceneDiffuser](https://arxiv.org/abs/2412.12129) treats every task as filling in one agents × time × features grid: fix a cutting-in vehicle's path, and the model fills in traffic that fits around it. [Scenario Diffusion](https://arxiv.org/abs/2311.02738) describes chosen agents with tokens for position, heading and speed. [Nexus](https://arxiv.org/abs/2504.10485) sets an attacker's goal at the target vehicle's future position.

**4. Condition on a label or a sentence.** [LangTraj](https://arxiv.org/abs/2504.11521) trains with classifier-free guidance on about 140,000 Waymo and nuPlan scenarios whose interactions people labelled (the paper rounds this to 150,000), including "intersection yielding". DJINN steers with a classifier that recognises cut-ins. As with DALL·E 3, the labels limit the control.

**5. Generate many and keep the worst.** CTG keeps the best of several guided samples. [SLEDGE](https://arxiv.org/abs/2403.17933) generates eight traffic samples and keeps the densest.

(dlit-key-papers)=
### The key papers

| Paper | Generates | Steered by | Trained on | What it showed |
| --- | --- | --- | --- | --- |
| CTG (Zhong et al., ICRA 2023) | Each vehicle's actions, rolled through a vehicle model, in closed loop | Traffic-rule costs; best of several samples | nuScenes | Speed-limit violations 0.019, against 0.188 for the BITS model; share of agents that collide or leave the road 0.165 against 0.256 |
| [MotionDiffuser](https://arxiv.org/abs/2306.03083) (Jiang et al., CVPR 2023) | Joint futures of several agents (a predictor) | Any smooth cost on the clean guess | Waymo Open Motion | A 5 m "repeller" cost cut overlaps between predicted agents from 0.059 to 0.008 |
| Scenario Diffusion (Pronovost et al., NeurIPS 2023) | Whole scenes: boxes and short trajectories | Tokens describing chosen agents | Argoverse 2, plus 6 million internal scenarios | 89.5% of generated trajectory waypoints on the drivable area, against 90.0% for real ones; at an intersection, a stopped or moving token flips which approach gets right of way |
| Safe-Sim (Chang et al., ECCV 2024) | Motion of reacting agents, one of them the adversary | Collision, speed and time-to-collision costs; head start | nuScenes; tested on nuPlan too | With a rule-based planner, 43.2% of agents were involved in collisions at realism 0.38, against 36.4% at 0.85 for STRIVE (lower realism number = more realistic) |
| SLEDGE (Chitta et al., ECCV 2024) | Lane graph and where agents start; motion from IDM car-following | Keep hard routes and dense traffic | nuPlan | The PDM-Closed planner failed in 0.26 of replayed 500 m routes and 0.49 of hard generated 500 m scenes (0.06 on replayed 100 m routes) |
| SceneDiffuser (Jiang et al., NeurIPS 2024) | Starting scene and closed-loop motion | Fill-in; hard constraints; constraints written by hand or by Gemini | Waymo Open Motion | Waymo sim-agents realism 0.703, against 0.819 for the logged data itself |
| VBD (Huang et al., IEEE T-ITS 2026) | 8-s control sequences for all agents, closed loop | Goals; conflict prior; game-theoretic guidance | Waymo Open Motion | Realism 0.720 on the same benchmark; at a stop-controlled intersection, goal guidance makes one vehicle run the stop sign and another yield |
| AdvDiffuser (Xie et al., 2024 preprint) | Background vehicles' paths, through a dynamics model | Gradient of a learned adversarial reward | nuScenes | Tested vehicle collided in 11.03% of runs, against 8.45% on replayed logs |
| [DiffScene](https://ojs.aaai.org/index.php/AAAI/article/view/32951) (Xu et al., AAAI 2025) | One safety-critical vehicle's path in the CARLA simulator | Distance, collision, route-blocking and natural-speed costs | 6,995 simulated, not real, trajectories | Over 75% average collision rate across three NHTSA pre-crash intersection types: crossing, red-light running, right turn |
| [CCDiff](https://arxiv.org/abs/2412.17920) (Lin et al., CVPR 2025) | Closed-loop futures | Guidance only on the causally key agents | nuScenes | Controllability 0.74 at realism 0.76; CTG 0.56 at 0.77; STRIVE 0.85 at 0.13 (both scores 0 to 1, higher is better) |
| LangTraj (Chang et al., ICCV 2025) | Scene-level motion | Sentences, plus collision guidance | About 140,000 labelled Waymo and nuPlan scenarios | Collision rate 0.04 unguided, 0.41 guided; map adherence fell from 0.81 to 0.70 |
| [Wang et al.](https://arxiv.org/abs/2506.08459) (Stanford, 2025 preprint) | Sensor-error sequences that make the tested vehicle crash at a four-way intersection | Retrained on its own closest calls | HighwayEnv simulator | 21.34% of samples collided, against 1.45 × 10⁻⁶ for random sampling |

**Where to start reading.** Read CTG first: it is the template, with costs, a vehicle model and closed loop. Read Safe-Sim for an adversary inside a reacting simulation, and for its honest limitation: "the adversarial agent unrealistically collides with non-adversarial agents before reaching the ego agent… some scenarios result in collisions where the ego planner is not at fault." For intersections, read DiffScene and Wang et al.; both run in simulators, not on recorded intersections.

**The trade-off every paper meets.** Steering harder makes more collisions and less realistic traffic. CCDiff's table shows it across methods, and LangTraj's within one model: guidance multiplied collisions about tenfold while map adherence fell. The worked example below measures the same trade-off on one intersection.

**Do not compare collision rates across papers.** CTG and Safe-Sim count the share of agents that collide; CCDiff counts scenarios with at least one collision; AdvDiffuser counts the tested or background vehicles involved; SLEDGE's failure rate adds leaving the road, driving the wrong way and stalling. The realism scores differ too, and the Waymo benchmark changes its definition from year to year.

**Inside five of the key papers.** The table above says what each paper showed. The five below were chosen because together they use all five ways {ref}`above <dlit-five-ways>`. The table answers the six questions of {ref}`Part B <dlit-part-b>` for each; the figures are the papers' own architecture figures.

| Question | CTG | Safe-Sim | VBD | CCDiff | SceneDiffuser |
| --- | --- | --- | --- | --- | --- |
| 1. What is noised | Each vehicle's actions (acceleration, yaw rate) | 3.2 s of actions per vehicle | 8 s of actions for up to 64 agents at once | All agents' actions, 52 steps of 0.1 s | 128 agents × 91 time steps × position, heading, size, type |
| 2. Condition, and how it enters | Map raster and past states, added in every block | Map raster and about 1 s of history, as in CTG | Agents, map and traffic lights as tokens, read by cross-attention | History, map, and a causal graph used as an attention mask | Map and signal tokens by scale-and-shift; known cells stacked with the input |
| 3. Denoiser | 1-D convolutional U-Net | 1-D convolutional U-Net | Transformer across agents and time | Transformer, 15.4 million parameters | Transformer alternating time and agents |
| 4. Graded on | Clean trajectory; 100 noise steps | Clean trajectory; 100 noise steps | Clean trajectory; 50 noise steps | Clean actions; 100 noise steps | v-prediction (a mix of noise and clean data) |
| 5. Sampling | 100 steps; re-plans at 2 Hz | 100 steps; 20 samples per vehicle, one kept | 50 DDPM steps (1.48 s) or 5 DDIM steps (0.16 s) | 100 steps; about 20 ms per frame per agent | 16 steps, or 1 step per 0.1-s simulation step |
| 6. Steering (which of the five ways) | Rule cost; best of several (1, 5) | Cost toward the tested car; noised crash sketch (1, 2) | Goal, collision and game costs (1) | Classifier-free guidance; costs on key agents only (4, 1) | Fill-in; hard constraints (3) |

**CTG: rules added only at sampling time.**

```{figure} ../_static/figures/DL_Paper_CTG.png
:alt: CTG Figure 2 in three bands. Input: the context c (a map of an intersection with vehicles), noisy actions tau_a^k drawn as a jagged line, which a function f turns into states tau_s^k (a vehicle and its path), and STL rules phi. Middle: an encoder F_theta reads c; the diffusion model p_theta reads the encoder output and the noisy actions and states and outputs a mean mu; a guide J(mu), built from the STL rules, takes mu and returns a gradient that is added to mu. Output: the less noisy actions tau_a^(k-1), which f turns into states tau_s^(k-1).
:width: 100%

One denoising step: the noisy actions (and the states they imply) and the encoded map and history go into the diffusion model; a guide built from a traffic rule shifts its prediction before the next, cleaner step. Figure 2 of [Zhong et al. (2023)](https://arxiv.org/abs/2210.17366).
```

CTG learns how nuScenes drivers choose acceleration and turn rate over the next few seconds. Positions come from rolling those actions through a simple vehicle model, so every sample is drivable. At each of 100 denoising steps, a traffic rule written in signal temporal logic (for example, always below the speed limit) gives a score whose gradient nudges the plan. **Found:** on the speed-limit rule, plain samples violated it by 1.380; with guidance and best-of-several filtering, by 0.019, while realism and failure rate also improved (Table II).

**Safe-Sim: an adversary with a head start.**

```{figure} ../_static/figures/DL_Paper_SafeSim.png
:alt: Safe-Sim Figure 2 in three parts. Left, the scenario: an ego car (yellow), an adversary car (red) and a non-adversary car (blue) on a road, with a star at the collision point; J_Adv links the adversary to the ego car's path and J_Reg links the non-adversary car. Middle, adversary-car guided diffusion: a noisy plan tau_K is denoised step by step to tau_0, with guidances J applied between tau_k and tau_(k-1). Right, the guidance functions: J_Reg, made of J_Route (lane margin) and J_gc (Gaussian distance), and J_Adv, made of J_Coll (collision distance) and J_Control (relative speed and time to collision).
:width: 100%

One adversary car's plan is denoised from noise to a clean path. At each step, guidance pulls it toward a collision with the tested vehicle, while lane and distance terms keep traffic realistic. Figure 2 of [Chang et al. (2024)](https://arxiv.org/abs/2401.00391).
```

Safe-Sim replays a real nuScenes scene, but a CTG-style model drives the other cars and re-plans twice a second. One chosen car is pushed at every step toward the tested vehicle, at a chosen relative speed or time to collision. To pick a front, side or rear crash, a rule-made sketch of it is partly noised and then denoised, so it keeps its shape but becomes drivable. **Found:** starting from these noised sketches raised the collision rate from 23.9% to 29.0%, and the variance of the collision points from 1.62 m to 5.44 m, so the crashes were more varied (Table 5).

**VBD: one transformer for the whole scene.**

```{figure} ../_static/figures/DL_Paper_VBD.png
:alt: VBD Figure 2. The scene context (cars, pedestrians and cyclists, map polylines, traffic lights, the road) becomes agent and map tokens that feed a scene encoder of query-centric attention layers. Its output is the condition for two parts: a behavior predictor (cross-attention layers that also read static end-goal anchors) that outputs agent-wise marginal trajectories, and a denoiser (self-attention and cross-attention layers). The denoiser's input is the noisy trajectories u-tilde and x-tilde, passed through an encoder and added to a position embedding of the noise level k. The denoiser outputs scene-consistent joint plans; red dashed arrows show optional guidance from the predicted trajectories and from a cost J.
:width: 100%

A transformer scene encoder turns agents, map polylines and traffic lights into tokens; the denoiser turns noisy joint plans for every agent into plans that fit together, optionally guided by a cost. Figure 2 of [Huang et al. (2026)](https://arxiv.org/abs/2404.02524).
```

VBD noises and denoises the accelerations and yaw rates of up to 64 road users over 8 seconds as one array. The transformer looks across agents and across time, and reads the encoded scene through cross-attention. Steering adds cost gradients on the denoiser's clean guess: reach a goal, avoid collisions, or play a pursuit–evasion game against another car. **Found:** a collision-avoidance cost added only at sampling cut collisions from 2.47% to 1.11%, with no retraining (Table III).

**CCDiff: steer only the vehicles that matter.**

```{figure} ../_static/figures/DL_Paper_CCDiff.png
:alt: CCDiff Figure 2. Left, the initial conditions: a scenario layout at an intersection with ego agents (green) and 1-hop, 2-hop and 3+-hop entities (red, purple, blue). Histories tau and maps c go into a scene encoder, which outputs predicted actions. A causal reasoner builds a factored causal graph G (motion histories, intervention actions, reward objectives), which feeds back into the scene encoder (causal composition) and into an importance ranking that picks the top-k agents to guide. The diffusion model takes the predicted actions and the top-k guidance and produces the generated scenarios (future trajectories), marked controllable, safety-critical and realistic, with a closed-loop update arrow back to the scene encoder.
:width: 100%

Histories and the map feed a scene encoder and a causal reasoner. The causal graph ranks the key agents, and the diffusion model guides only those, in closed loop. Figure 2 of [Lin et al. (2025)](https://arxiv.org/abs/2412.17920).
```

CCDiff works out which vehicles affect each other, from time-to-collision checks and attention weights, and lets each vehicle attend only to the vehicles that affect it. Training sometimes removes the graph, so the model also learns a no-interaction version; classifier-free guidance blends the two. Collision costs then push only the top-ranked key agents. **Found:** guiding only the key agents cut the share of agents whose realism push and guidance push point in opposite directions from about 9.1% (CTG) to about 4.8% (Table 7, Appendix C.1).

**SceneDiffuser: fill in a table, one step per simulation step.**

```{figure} ../_static/figures/DL_Paper_SceneDiffuser.png
:alt: SceneDiffuser Figure 3 in two parts. Left, the global context encoder: roadgraph and traffic-signal features are projected and concatenated into keys and values, and a few latent tokens act as queries in cross-attention to give a small global context. Right, the transformer denoiser backbone: the scene tensor z_t (agents A by time tau by features D) and a local context of known cells are projected and concatenated, with position encodings for t and tau, then fused with the global context by cross-attention and adaptive layer norm. A repeated block applies self-attention over time and then over agents, and a final projection gives the denoised scene tensor (A by tau by D).
:width: 100%

A context encoder compresses the road graph and traffic signals into a few tokens, which steer a transformer that alternates attention over time and over agents to denoise the scene table. Figure 3 of [Jiang et al. (2024)](https://arxiv.org/abs/2412.12129).
```

SceneDiffuser stores a scene as one table, agents × time steps × features, and turns every task into filling in: known cells stay fixed and the model fills the rest. In closed-loop simulation it keeps a future plan that is noisier further ahead, and removes one noise step per 0.1-s simulation step instead of re-running all 16. Rules such as no overlapping vehicles are enforced by clipping at every step. **Found:** in closed loop this scored 0.673 on the Waymo realism metric, against 0.492 for full re-sampling at every step (Table 2).

(dlit-worked)=
### Worked example: steering a scenario model at one intersection (synthetic)

On a synthetic left turn where the truth is known, guidance raised conflicts from 3 in 10,000 samples to almost every sample. The harder it steered, the more of those conflicts arose in ways no recorded driver produced.

**The intersection.** We reuse the permissive left turn of the *Generating Crash Data from Near-Misses* handout: a turner crosses one oncoming through car (35 mph on average), whose driver brakes if the turner would block the lane. Everything is simulated, so every driver's true behaviour is known. The model learns from 400,000 interactions, about seven years at that handout's 55,000 a year. They hold 328 conflicts (PET under 1 s), 4 of them crashes.

**A scenario as data.** Each interaction becomes two time–space traces over 7 s, one point every 0.25 s: the through car's distance to the conflict point, and the turner's distance along its path. That is 58 numbers. Then we compress first, as Stable Diffusion does with its autoencoder and MotionDiffuser does with PCA. Each trace is cut to its leading principal components, 12 for the through car and 8 for the turner: the linear autoencoder of {doc}`4.5 <notes2c-autoencoders>`. They rebuild the traces to about a millimetre.

**The model.** A small network with 638,228 weights learns to name the noise in those 20 numbers, exactly as in {doc}`4.10 <notes6-diffusion-basics>`: cosine schedule, T = 1,000 steps, 20,000 training passes of 1,024 scenarios (31 minutes on two CPU cores). Sampling uses 50 steps.

**The steering.** The conflict cost J is the closest distance between the two cars over the 7 s, smoothed so it has a gradient. A second set of runs adds a *support cost*: a penalty whenever the turner's accepted gap is shorter than any gap in the data, 3.0 s. Both enter through the guidance equation {ref}`above <dlit-five-ways>`.

**The checks.** Every scenario, recorded or generated, gets the same four checks:

- *PET*, by the rule of the *Generating Crash Data from Near-Misses* handout. On all 400,000 training interactions it labels conflicts and crashes exactly as the simulator does.
- *Physics:* no reversing, no braking harder than 1 g or accelerating harder than 0.5 g, no implausible speeds, no turner speed change larger than any recorded.
- *Set-up support:* the accepted gap and the through car's speed lie inside the recorded range.
- *Looks real*, the score from {ref}`4.10 <diffusion-scorecard>`.

```{figure} ../_static/figures/DL_TimeSpace.png
:alt: Five time-space panels and a key. Each panel plots the through car's distance to the conflict point in metres against time since the turner starts (0 to 7 s); a sand band marks when the turner is in the through car's lane, and a grey band just below zero marks the conflict area. Top left, recorded, an everyday turn: PET 2.68 s, accepted gap 6.2 s, through car slowed 0.0 m/s. Top middle, recorded, a near-miss: PET 0.49 s, accepted gap 3.8 s, slowed 2.4 m/s. Bottom left, generated with the conflict and support cost at lambda 1, passes every check: PET 0.85 s, gap 4.2 s, slowed 6.2 m/s. Bottom middle, conflict and support cost at lambda 3, passes every check but never slows: PET 0.56 s, gap 4.9 s, slowed 0.0 m/s. Bottom right, conflict cost only at lambda 3, gap shorter than any recorded: a crash (PET at or below 0) from an accepted gap of 2.6 s, drawn in gold. Top right, the key: gold marks a set-up no recorded driver produced, and the line inside the grey band while the sand band is open means a crash.
:width: 100%

Recorded and generated scenarios as time–space diagrams. The bottom-middle scenario passes every check, yet its through car never slows while the turner blocks the lane. The bottom-right one starts from a 2.6 s gap, shorter than any recorded.
```

```{figure} ../_static/figures/DL_Guidance_Sweep.png
:alt: Line chart on a log scale from 0.01% to 100%: the share of generated scenarios with PET under 1 s against guidance strength lambda (0, 0.3, 0.5, 1, 2, 3 and 10, shown as categories). Conflict cost, all conflicts (solid grey): 0.029% unsteered, 0.97% at 0.3, 4.87% at 0.5, 26.64% at 1, 77.08% at 2, 96.64% at 3, 98.33% at 10. Conflict cost, passes every check (dashed grey): 0.029%, 0.91%, 4.14%, 14.3%, 32.45%, 36.62%, 37.76%. Conflict plus support cost, passes every check (blue): 18.04% at 1, 56.1% at 2, 76.71% at 3, 67.7% at 10. A dotted line marks recorded traffic at 0.083%. A note at lambda 3: share passing every check, conflict cost 36.62%, conflict plus support cost 76.71%.
:width: 100%

A support cost doubles the steered conflicts that pass every check. Synthetic left-turn world: 100,000 unsteered samples and 10,000 per steered run (`results.json` in the reproducer).
```

The grey lines use the conflict cost alone; the blue line adds the support cost. "Passes every check" means PET under 1 s, physics and set-up support all pass.

**How the conflicts arise.** The share of conflicts is half the story. The other half is how they happen:

| Scenarios | Conflicts starting from a gap shorter than any recorded | Through car's slowdown before the conflict point (median) | Conflicts that look real |
| --- | --- | --- | --- |
| Recorded, 100,000 held out | 0% | 4.6 m/s | 0.63 |
| Unsteered, 100,000 | 0% | 4.9 m/s | 0.72 |
| Conflict cost, λ = 0.5 | 13% | 5.3 m/s | 0.56 |
| Conflict cost, λ = 1 | 40% | 3.8 m/s | 0.28 |
| Conflict cost, λ = 3 | 57% | 0.05 m/s | 0.06 |
| Conflict + support cost, λ = 1 | 0% | 4.6 m/s | 0.42 |
| Conflict + support cost, λ = 3 | 0.8% | about 0 | 0.16 |

**What the numbers say.**

1. **Unsteered, the model is as rare as the data, or rarer.** It made 29 conflicts and no crash in 100,000 samples, against 83 conflicts and 3 crashes in 100,000 recorded interactions. A diffusion model trained on everyday traffic under-samples its own tail. Overall it looks as real as recorded traffic (0.90 against 0.89).
2. **Gentle steering is cheap.** At λ = 0.3 about 1 sample in 100 is a conflict, some 30 times the unsteered share, and nearly all pass every check.
3. **Strong steering takes shortcuts.** At λ = 3, 97% of samples are conflicts and 82% are crashes. But most of those conflicts start from a gap no turner accepted in the data, and the through car barely slows. Physics never broke: under 1% of samples failed it at every strength, because the compressed traces always keep a car's shape. What broke is how the conflict happens.
4. **Closing one shortcut opens the next.** The support cost keeps gaps inside the recorded range, and at λ = 3 it doubles the share that passes every check. But the through car still does not slow, while recorded drivers in this world always start braking, if sometimes late, when the turner blocks. Every check we wrote down passes, yet the mechanism is wrong. Only at λ = 1 do the support-cost conflicts brake like recorded ones.
5. **The share is set by λ, not by traffic.** Any conflict share from 0.03% to 98% is available by turning one number. None of them is a crash rate ({ref}`Judging a generated scenario <dlit-judging>`).

:::{admonition} Before you trust this example
:class: warning
- *Baseline:* 100,000 recorded interactions held out from training (83 conflicts, 3 crashes) and the unsteered model.
- *Honest split:* every score uses held-out recorded data; the PCA basis and the model saw only the training interactions.
- *Ugly cases:* the never-slowing drivers and the short gaps above. And the world itself is synthetic: real drivers vary more than its rules, so a real study must measure the braking behaviour, not assume it.
:::


The code, results and figures are in the course files under `diffusion_scenarios_worked_example`.

(dlit-sensor)=
### From scenario to sensor data

A trajectory scenario tests a planner that reads object lists. To test a perception system, or an end-to-end driving policy that reads raw camera images, you also need the images. Since 2023 a family of diffusion models draws them from a road layout, using the ControlNet and GLIGEN ideas of {ref}`Control with maps and boxes <dlit-control>`.

```{figure} ../_static/figures/DL_Two_Stage_Pipeline.png
:alt: Five boxes left to right joined by arrows: scenario model (agents and map, steered toward a conflict), road layout (bird's-eye map and 3D boxes, frame by frame), renderer (a diffusion model draws camera video or LiDAR), tested system (a detector or a driving policy), failures (missed objects, collisions). The scenario model and the renderer are highlighted. A dashed line from the tested system leads to a dashed box: open question, does a failure here predict a real one? No study found so far shows that it does.
:width: 100%

Two stages: generate the scenario, then render what the sensors see. Examples: SafeMVDrive and Challenger (2025 preprints).
```

The pipeline runs left to right. The renderer is the newer, less tested half.

| Model | What it draws | Steered by | What was shown |
| --- | --- | --- | --- |
| [MagicDrive](https://arxiv.org/abs/2310.02601) (Gao et al., ICLR 2024) | Six camera views of one moment, from Stable Diffusion | Road map through a ControlNet-like branch; 3D boxes, camera pose and text through cross-attention | Adding generated images to nuScenes training raised a camera-only BEVFusion detector from 32.88 to 35.40 mAP. On generated validation images the same detector scored 12.30 mAP, against 23.54 on real ones. |
| [Panacea](https://arxiv.org/abs/2311.16813) (Wen et al., CVPR 2024) | Six-camera video | Layout sequence (boxes, depth, road map) through ControlNet; text | StreamPETR NDS: 46.9 on real data, 36.1 on generated data only, 49.2 on both. |
| [DrivingDiffusion](https://arxiv.org/abs/2310.07771) (Li et al., ECCV 2024) | Six-camera video | 3D layout, text, a prompt per object | Can edit objects to stage rare events "such as collision"; separately, 6,000 synthetic frames aimed at long-tail cases (small or close vehicles, unusual headings) raised BEVFusion NDS from 0.412 to 0.434. |
| [LidarDM](https://arxiv.org/abs/2404.02903) (Zyrianov et al., ICRA 2025) | LiDAR video | Bird's-eye map; traffic from a simulator | A CenterPoint detector scored 56.4% mAP on generated LiDAR and 59.7% on real. |
| [GAIA-2](https://arxiv.org/abs/2503.20523) (Wayve, 2025) | Up to five camera views | Ego speed and curvature, agent boxes, weather, time, road type | Aimed at testing with "emergency braking, or hazardous crossings"; results shown as examples and training curves. |
| [Cosmos-Drive-Dreams](https://arxiv.org/abs/2506.09042) (Ren et al., 2025) | Camera video and LiDAR | A rendered map video with boxes, lanes, signs and lights; weather prompts | Generated rain and fog clips raised 3D lane-detection F1 in rain from 0.458 to 0.506. |

**Inside MagicDrive: each condition enters the way its shape suits.**

```{figure} ../_static/figures/DL_Paper_MagicDrive.png
:alt: MagicDrive Figure 3. On the left, a text prompt (A driving scene, then a description), the camera pose, object boxes and a road map, drawn as stacked layers. The prompt goes to a frozen text encoder, the camera pose and the boxes to trainable encoders; these join in one sequence embedding (camera, text, box 1 to box n) that enters a U-Net by cross-attention. The road map goes to a trainable map encoder that also reads the sequence embedding and is added into the U-Net. The U-Net blocks are frozen, with added cross-view attention, and denoise six camera views of noise; on the right, two generated six-view scenes, one for a plain driving scene and one with rain. A legend marks cross-view attention, cross-attention injection, additive encoder injection, and the trainable and frozen parts.
:width: 100%

Text and camera pose, the 3D boxes and the top-down road map are each encoded their own way and fed into a frozen Stable Diffusion U-Net that denoises all six camera views; cross-view attention keeps neighbouring views consistent. Figure 3 of [Gao et al. (2024)](https://arxiv.org/abs/2310.02601).
```

The road map is a grid, so it enters through an added branch (the ControlNet idea of {ref}`Part A <dlit-control>`). The boxes are a list, so each box becomes a token read by cross-attention, like the words of the caption. Only the new parts are trained; the Stable Diffusion U-Net stays frozen. The choice matters: feeding the boxes only as part of the map image, instead of through their own encoder, left vehicle segmentation on generated scenes at 5.50 mIoU (Table 4). The limit is the data: MagicDrive cannot draw what nuScenes lacks, so its night images come out too bright and requested snow does not appear.

Two 2025 preprints run the whole pipeline. [SafeMVDrive](https://arxiv.org/abs/2505.17727) steers trajectories toward danger, then renders six-camera video. It renders near-collisions rather than collisions, because "existing multi-view video generators struggle to render realistic collision events." Its scenarios raised the UniAD planner's 3-second collision rate from 0.007 to 0.303. [Challenger](https://arxiv.org/abs/2505.15880) generates trajectories with diffusion, checks them in a physics simulator, then renders them; UniAD's collision rate rose from 0.32% to 3.95%.

Read these numbers with two cautions. First, the detector gains come from adding generated data to real data; generated data alone did worse (Panacea, MagicDrive). Second, both pipelines test planners open-loop on generated video. No study we found shows that a failure on generated sensor data predicts a failure on the road. NVIDIA's own Cosmos report puts it plainly: current world models "fall short as reliable simulators of the physical world" ([Cosmos](https://arxiv.org/abs/2501.03575)).

(dlit-judging)=
## Judging a generated scenario

Judge every generated scenario on five questions, and never read the share of dangerous scenarios as a crash rate.

| Question | How the papers measure it | What a traffic-safety engineer adds |
| --- | --- | --- |
| Is it realistic? | The [Waymo sim-agents](https://arxiv.org/abs/2305.12032) realism score: from 1.1 s of history, 32 rollouts of 8 s per scene, scored on how likely the logged future is under them, for motion, interaction and map features. Distance between driving-profile histograms (CTG). FID for sensor data. | A physics check: no braking beyond what tyres allow, no reversing. A set-up check: speeds and gaps inside the range ever recorded. The "looks real" score from 4.10. |
| Is it dangerous in a way that matters? | Collision rate, off-road rate, time-to-collision (TTC) | Post-encroachment time (PET), deceleration needed to avoid a crash, and the conflict type: left-turn opposing, rear-end, angle |
| Is the set varied? | Coverage and diversity scores | "Covers variety" from 4.10; and whether the conflicts arise in different ways (a late brake, a short gap, a red-light runner) |
| Did the steering do what was asked? | Controllability (CCDiff), rule violation (CTG) | The share of scenarios that meet the request and pass every check above |
| Whose fault is it? | Rarely measured; Safe-Sim notes that some of its collisions were not the tested planner's fault | Could a competent driver have avoided it? A test of a planner should not count collisions no one could avoid. |

**Not a crash rate.** Steering changes frequencies; that is its purpose. A model steered toward conflicts produces conflicts at whatever share the steering strength sets, so that share says nothing about how often they happen on the road. Wang et al. make the gap concrete: random sampling produced a collision once in about 700,000 runs, while 21% of the samples from their diffusion model, retrained on its own closest calls, collided (both figures for one approach direction). To turn steered samples into a frequency, each sample needs a weight for how much more likely the steering made it: the importance sampling of the *Generating Crash Data from Near-Misses* handout and of NADE and D2RL. None of the diffusion papers in {ref}`the key papers <dlit-key-papers>` reports such weights.

:::{admonition} Before you trust a generated safety scenario
:class: warning
- *Baseline:* compare with replayed real logs and with scripted scenarios in a simulator. A planner that already fails 8% of replayed logs (AdvDiffuser's replay baseline) needs no generator to find its first failures.
- *Honest split:* train the generator on some intersections and test on others; for sensor data, measure the tested system on held-out real data, not only on generated data.
- *Ugly cases:* look at the generated crashes one by one. Count the ones that break physics, start from a set-up never recorded, or could not have been avoided by anyone.
:::


(dlit-breaks)=
## Where it breaks

Most failures come from steering past what the data support. Nine to watch for:

1. **It cannot invent behaviour it never saw.** Steering reweights what the model learned; it adds no knowledge. VBD says it plainly: it was "trained on real-world traffic datasets with only normal conditions." In the {ref}`worked example <dlit-worked>` the unsteered model made fewer conflicts than the data held.
2. **Strong steering leaves the data.** Realism falls as conflicts rise: CCDiff and LangTraj report it, and in the worked example "looks real" fell from 0.90 unsteered to 0.06 at λ = 3.
3. **The cheapest route is not the realistic one.** Guidance moves whatever is easiest to move. In the worked example it first shortened the turner's gap, then removed the through driver's braking. Check how conflicts arise, not only that they arise.
4. **Physics is not guaranteed.** A model that generates positions can draw motion no car can make. The remedies: generate controls through a vehicle model (CTG), compress with real trajectories (the worked example), or replay in a physics simulator (Challenger).
5. **Collisions nobody could avoid.** An adversary that hits other agents first, or hits the tested vehicle from nowhere, tests nothing. Safe-Sim reports both.
6. **Open loop.** A scenario that does not react to the tested vehicle measures something other than safety in traffic. Both sensor pipelines in {ref}`From scenario to sensor data <dlit-sensor>` test planners this way.
7. **Sensor renderers drift.** Cosmos lists a "lack of object permanence". MagicDrive's night images are "not as dark as real images", and it "cannot generate unseen weathers". SafeMVDrive avoids rendering collisions at all.
8. **The data come from somewhere else.** The large datasets come from automated-vehicle fleets in a few cities. A model trained there carries their road geometry and driving habits; a Tampa intersection is a different distribution.
9. **It is slow.** Each sample takes many network passes. Safe-Sim reports 104.5 s per scenario (STRIVE, 427.2 s); CTG++ about a minute.

(dlit-fit)=
## Fit card and applications

**Fit card: diffusion for safety scenario generation**

| Field | Answer |
| --- | --- |
| Idea in one sentence | Learn what recorded scenarios look like by learning to remove noise from them, then generate new ones and steer each denoising step toward the dangerous corner. |
| Why it works (the logic) | At every noise level the denoiser's guess is an average of real scenarios that fit, so samples stay near recorded behaviour. Guidance tilts each step toward low cost, so rare situations come out far more often than in the data. |
| Fits these tasks | Stress-testing ADAS and automated-driving planners in simulation; finding the set-ups where a design produces conflicts; rare cases for perception training data. Leverage labels: generation, and prediction for motion forecasting. |
| Needs this data | Trajectories with a map (drone or roadside video, AV logs), recorded at 10 Hz or more, many thousands of interactions of the kind you want to stress. No labels for an unconditional model; labels or descriptions to condition on. AV companies, public datasets, and agencies with roadside sensors hold it. |
| Breaks when | The dangerous behaviour never appears in the data; the steering pushes past what the data support; a share of generated crashes is read as a crash rate; the tested vehicle's reactions do not change what the other agents do (open-loop replay). |
| Keep the classical method when | You need a frequency or a crash rate (extreme-value statistics on surrogate measures, crash models, importance sampling); the conflict is simple enough to describe with a few parameters and sweep in a simulator; you need factors you can explain to an engineer or a court. |

**Applications**

| Domain | Task | Data it needs | Classical baseline |
| --- | --- | --- | --- |
| Driving automation and ADAS | Find the cut-ins and crossings that make an automatic-braking or unprotected-left-turn planner fail | AV logs with maps; a simulator to replay them | Scripted test scenarios with parameter sweeps; NADE-style importance sampling |
| Road safety at intersections | Show which phasing, sight lines or speeds produce left-turn conflicts, before a crash history builds up | Drone or roadside trajectories at the site or similar sites | Surrogate safety measures with extreme-value statistics; FHWA's SSAM on microsimulation output |
| Perception for agencies | Footage of rare events (wrong-way drivers, debris, flooded lanes) to test a vendor's video analytics before purchase | Agency camera feeds plus labelled examples | Staged tests and manual review of recorded events |
| Automated-vehicle perception | Add rare objects and weather to detector training data | Multi-camera or LiDAR data with 3D boxes | Copy-paste augmentation; collecting more real data |

(dlit-check)=
## Practice and project ideas

### Check yourself

1. A vendor reports that its diffusion-generated scenarios made your automatic-braking system collide in 4% of runs. Name three things you would ask before you accept that number.
2. You have three months of drone video at one signalized intersection and want left-turn conflicts for a phasing study. Would you use guided diffusion, a microsimulation sweep, or extreme-value statistics on PET? Defend the choice, and say what each could not tell you.
3. In the {ref}`worked example <dlit-worked>` the support cost fixed the short gaps, and the through driver then stopped braking. Design one more cost or check that would catch this. What data would you need to set it?
4. Your detector gained 2.5 mAP after you added MagicDrive-style images to training. Your agency wants it to detect wrong-way drivers on I-275. What evidence would convince you the gain carries over?
5. A classmate wants to condition a scenario model on police-report crash types. What will limit the control she gets? (Think of DALL·E 3.)
6. Why do both sensor pipelines in {ref}`From scenario to sensor data <dlit-sensor>` render near-collisions instead of collisions? What does that mean for what they can test?

### Project ideas

- *PET-guided generation at a real intersection.* Train a small scenario model like the {ref}`worked example <dlit-worked>` on left turns from inD or SinD, steer it with a PET-based cost, and report conflicts by type with the four checks. None of the 17 papers in {ref}`What the models learn from <dlit-data>` used these datasets or PET.
- *Fix the mechanism.* Extend the worked example's reproducer with a response cost (the through driver's braking must look like recorded braking). Measure how the passing share and the mechanism change with λ.
- *Rare conditions on Florida cameras.* Start from the 2,949 FL511 frames of {doc}`Lab 6 <../module6/lab6_vit_finetune>`. Add rain or flooded lanes with a ControlNet-style image model, and test a classifier only on held-out real frames.
- *From steered samples to a rate (PhD level).* Combine the worked example with the importance sampling of the *Generating Crash Data from Near-Misses* handout: weight each steered sample by how much the steering raised its probability, and see whether the weighted crash rate recovers the world's true rate. The hard part is the weight, which needs the model's likelihood.

### Where to go next

- {doc}`4.13 How transportation knowledge guides diffusion <notes9-knowledge-guided>`: five doors where
  transportation knowledge can enter a diffusion model (what it generates, the condition, guidance, values held fixed,
  checks), what your data must contain for each, and a worked test on four loop detectors.
- The {ref}`reading library <generative-reading-library>` on the closing page of this module: 34 papers on generative
  models in transportation, grouped by the problem they address.
- The *Generating Crash Data from Near-Misses* handout: why sampling a generator is not enough for rare events, and
  what to do instead.

(dlit-references)=
## References for 4.12

All links were opened on Oct 27, 2026.

**Course materials**

- Bishop, C. M., & Bishop, H. (2024). *Deep Learning: Foundations and Concepts*, Chapter 20 (Diffusion models). Springer.
- {doc}`4.10 Diffusion models: the basics <notes6-diffusion-basics>`; the AI for Mobility handouts *Generating Crash Data from Near-Misses* and *Generative Models in Transportation* (applications).
- AI for Mobility companion: {ref}`How diffusion works in 35 transportation papers <diffusion-papers-library>` (on this page): each paper's architecture figure, the six questions answered, and how a hint reaches the model. The paper figures in {ref}`The key papers <dlit-key-papers>` and {ref}`From scenario to sensor data <dlit-sensor>` come from it.

**Part A: image diffusion**

- Ho, J., Jain, A., & Abbeel, P. (2020). [Denoising diffusion probabilistic models](https://arxiv.org/abs/2006.11239). NeurIPS 2020.
- Song, Y., et al. (2021). [Score-based generative modeling through stochastic differential equations](https://arxiv.org/abs/2011.13456). ICLR 2021.
- Song, J., Meng, C., & Ermon, S. (2021). [Denoising diffusion implicit models](https://arxiv.org/abs/2010.02502). ICLR 2021.
- Nichol, A., & Dhariwal, P. (2021). [Improved denoising diffusion probabilistic models](https://arxiv.org/abs/2102.09672). ICML 2021.
- Dhariwal, P., & Nichol, A. (2021). [Diffusion models beat GANs on image synthesis](https://arxiv.org/abs/2105.05233). NeurIPS 2021.
- Ho, J., & Salimans, T. (2022). [Classifier-free diffusion guidance](https://arxiv.org/abs/2207.12598). Short version: NeurIPS 2021 Workshop on Deep Generative Models.
- Nichol, A., et al. (2022). [GLIDE: Towards photorealistic image generation and editing with text-guided diffusion models](https://arxiv.org/abs/2112.10741). ICML 2022.
- Rombach, R., et al. (2022). [High-resolution image synthesis with latent diffusion models](https://arxiv.org/abs/2112.10752). CVPR 2022.
- CompVis. [Stable Diffusion](https://github.com/CompVis/stable-diffusion) (code and README) and [v1-4 model card](https://huggingface.co/CompVis/stable-diffusion-v1-4).
- Ramesh, A., et al. (2022). [Hierarchical text-conditional image generation with CLIP latents](https://arxiv.org/abs/2204.06125) (DALL·E 2).
- Saharia, C., et al. (2022). [Photorealistic text-to-image diffusion models with deep language understanding](https://arxiv.org/abs/2205.11487) (Imagen). NeurIPS 2022.
- Betker, J., et al. (2023). [Improving image generation with better captions](https://cdn.openai.com/papers/dall-e-3.pdf) (DALL·E 3). OpenAI.
- Peebles, W., & Xie, S. (2023). [Scalable diffusion models with transformers](https://arxiv.org/abs/2212.09748). ICCV 2023.
- Lipman, Y., et al. (2023). [Flow matching for generative modeling](https://arxiv.org/abs/2210.02747). ICLR 2023.
- Liu, X., Gong, C., & Liu, Q. (2023). [Flow straight and fast: Learning to generate and transfer data with rectified flow](https://arxiv.org/abs/2209.03003). ICLR 2023.
- Song, Y., et al. (2023). [Consistency models](https://arxiv.org/abs/2303.01469). ICML 2023.
- Esser, P., et al. (2024). [Scaling rectified flow transformers for high-resolution image synthesis](https://arxiv.org/abs/2403.03206) (Stable Diffusion 3). ICML 2024.
- Greenberg, O. (2025). [Demystifying Flux architecture](https://arxiv.org/abs/2507.09595). arXiv.
- Zhang, L., Rao, A., & Agrawala, M. (2023). [Adding conditional control to text-to-image diffusion models](https://arxiv.org/abs/2302.05543) (ControlNet). ICCV 2023.
- Li, Y., et al. (2023). [GLIGEN: Open-set grounded text-to-image generation](https://arxiv.org/abs/2301.07093). CVPR 2023.
- Ho, J., et al. (2022). [Video diffusion models](https://arxiv.org/abs/2204.03458). NeurIPS 2022.
- Blattmann, A., et al. (2023). [Stable Video Diffusion: Scaling latent video diffusion models to large datasets](https://arxiv.org/abs/2311.15127).
- Chung, H., et al. (2023). [Diffusion posterior sampling for general noisy inverse problems](https://arxiv.org/abs/2209.14687). ICLR 2023.

**Part B: scenarios and safety**

- Zhong, Z., et al. (2023). [Guided conditional diffusion for controllable traffic simulation](https://arxiv.org/abs/2210.17366) (CTG). ICRA 2023.
- Zhong, Z., et al. (2023). [Language-guided traffic simulation via scene-level diffusion](https://arxiv.org/abs/2306.06344) (CTG++). CoRL 2023.
- Jiang, C. M., et al. (2023). [MotionDiffuser: Controllable multi-agent motion prediction using diffusion](https://arxiv.org/abs/2306.03083). CVPR 2023.
- Pronovost, E., et al. (2023). [Scenario Diffusion: Controllable driving scenario generation with diffusion](https://arxiv.org/abs/2311.02738). NeurIPS 2023.
- Niedoba, M., et al. (2023). [A diffusion-model of joint interactive navigation](https://arxiv.org/abs/2309.12508) (DJINN). NeurIPS 2023.
- Chang, W.-J., et al. (2024). [Safe-Sim: Safety-critical closed-loop traffic simulation with diffusion-controllable adversaries](https://arxiv.org/abs/2401.00391). ECCV 2024.
- Chitta, K., Dauner, D., & Geiger, A. (2024). [SLEDGE: Synthesizing driving environments with generative models and rule-based traffic](https://arxiv.org/abs/2403.17933). ECCV 2024.
- Huang, Z., et al. (2026). [Versatile behavior diffusion for generalized traffic agent simulation](https://arxiv.org/abs/2404.02524) (VBD). IEEE Transactions on Intelligent Transportation Systems.
- Xie, Y., et al. (2024). [AdvDiffuser: Generating adversarial safety-critical driving scenarios via guided diffusion](https://arxiv.org/abs/2410.08453). arXiv.
- Jiang, C. M., et al. (2024). [SceneDiffuser: Efficient and controllable driving simulation initialization and rollout](https://arxiv.org/abs/2412.12129). NeurIPS 2024.
- Xu, C., Petiushko, A., Zhao, D., & Li, B. (2025). [DiffScene: Diffusion-based safety-critical scenario generation for autonomous vehicles](https://ojs.aaai.org/index.php/AAAI/article/view/32951). AAAI 2025.
- Lin, H., et al. (2025). [Causal composition diffusion model for closed-loop traffic generation](https://arxiv.org/abs/2412.17920) (CCDiff). CVPR 2025.
- Zhou, Y., et al. (2025). [Decoupled diffusion sparks adaptive scene generation](https://arxiv.org/abs/2504.10485) (Nexus). ICCV 2025.
- Chang, W.-J., et al. (2025). [LangTraj: Diffusion model and dataset for language-conditioned trajectory simulation](https://arxiv.org/abs/2504.11521). ICCV 2025.
- Wang, J., Schlichting, M. R., Delecki, H., & Kochenderfer, M. J. (2025). [Diffusion models for safety validation of autonomous driving systems](https://arxiv.org/abs/2506.08459). arXiv.
- Westny, T., & Olofsson, B. (2024). [Diffusion-based environment-aware trajectory prediction](https://arxiv.org/abs/2403.11643). arXiv.
- Zhu, Y., et al. (2023). [DiffTraj: Generating GPS trajectory with diffusion probabilistic model](https://proceedings.neurips.cc/paper_files/paper/2023/hash/cd9b4a28fb9eebe0430c3312a4898a41-Abstract.html). NeurIPS 2023.
- Montali, N., et al. (2023). [The Waymo Open Sim Agents Challenge](https://arxiv.org/abs/2305.12032). NeurIPS 2023 Datasets and Benchmarks.
- Ettinger, S., et al. (2021). [Large scale interactive motion forecasting for autonomous driving: The Waymo Open Motion Dataset](https://arxiv.org/abs/2104.10133). ICCV 2021.
- Zhan, W., et al. (2019). [INTERACTION dataset](https://arxiv.org/abs/1910.03088). arXiv.
- Bock, J., et al. (2020). [The inD dataset: A drone dataset of naturalistic road user trajectories at German intersections](https://arxiv.org/abs/1911.07602). IEEE IV 2020.
- Krajewski, R., Moers, T., Bock, J., Vater, L., & Eckstein, L. (2020). [The rounD dataset: A drone dataset of road user trajectories at roundabouts in Germany](https://levelxdata.com/round-dataset/). IEEE ITSC 2020.
- Xu, Y., et al. (2022). [SIND: A drone dataset at signalized intersection in China](https://arxiv.org/abs/2209.02297).

**Part B: sensor data**

- Gao, R., et al. (2024). [MagicDrive: Street view generation with diverse 3D geometry control](https://arxiv.org/abs/2310.02601). ICLR 2024.
- Wen, Y., et al. (2024). [Panacea: Panoramic and controllable video generation for autonomous driving](https://arxiv.org/abs/2311.16813). CVPR 2024.
- Li, X., et al. (2024). [DrivingDiffusion: Layout-guided multi-view driving scenarios video generation with latent diffusion model](https://arxiv.org/abs/2310.07771). ECCV 2024.
- Zyrianov, V., et al. (2025). [LidarDM: Generative LiDAR simulation in a generated world](https://arxiv.org/abs/2404.02903). ICRA 2025.
- Russell, L., et al. (2025). [GAIA-2: A controllable multi-view generative world model for autonomous driving](https://arxiv.org/abs/2503.20523). Wayve technical report.
- NVIDIA (2025). [Cosmos world foundation model platform for physical AI](https://arxiv.org/abs/2501.03575).
- Ren, X., et al. (2025). [Cosmos-Drive-Dreams: Scalable synthetic driving data generation with world foundation models](https://arxiv.org/abs/2506.09042).
- Zhou, J., et al. (2025). [SafeMVDrive: Multi-view safety-critical driving video synthesis in the real world domain](https://arxiv.org/abs/2505.17727). arXiv.
- Xu, Z., et al. (2025). [Challenger: Affordable adversarial driving video generation](https://arxiv.org/abs/2505.15880). arXiv.

Numbers quoted on this page come from the pages and tables named in the text. The worked example is synthetic; its
numbers come from the reproducer in the course files (`diffusion_scenarios_worked_example`).

---

Next: {doc}`4.13 How transportation knowledge guides diffusion <notes9-knowledge-guided>`. Back to the {doc}`Module 4 map <index>`.
