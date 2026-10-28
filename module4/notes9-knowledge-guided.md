(knowledge-guided)=
# 4.13 How transportation knowledge guides diffusion

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 4 &middot; Section 4.13</span>
    <span class="notes-card-session">Session: Diffusion</span>
  </div>
  <p class="notes-card-lede">A diffusion model learns traffic only from its data, but you know things the data show weakly or not at all: a braking limit, a lane closure, the worth of one near-miss. This page shows five doors where that knowledge can enter a diffusion model, what your data must contain for each door, and how to test whether the knowledge helped. A worked test on a simulated road with four loop detectors adds one piece of knowledge at a time.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Read it before</h4>
      <ul>
      <li><a href="notes6-diffusion-basics.html">4.10 Diffusion models: the basics</a></li>
      <li><a href="notes8-diffusion-literature.html">4.12 Diffusion in the literature</a>: the papers, and five ways to get a dangerous scenario out</li>
      <li><a href="notes7-unclip.html">4.11 Reading unCLIP</a>, for the unCLIP-style prior and the crash-sketch run</li>
      </ul>
    </div>
    <div>
      <h4>Interactive companion</h4>
      <ul><li><a href="../_static/companions/Knowledge_Guided_Diffusion_Companion.html" target="_blank" rel="noopener">Five doors for transportation knowledge, and a worked test &#8599;</a>, mounted near the end of this page</li></ul>
    </div>
  </div>
</div>

## What this section covers

- The map: five doors where transportation knowledge can enter a diffusion model, and how to pick the door for a piece of knowledge
- Data first: what each door asks of your data, eight things to add to a dataset, and a diffusion-ready record
- Door ①: put a law into what the model generates
- Door ②: match a condition to the information it carries, and check that the network uses it
- Door ③: classifier-free guidance, engineering costs, and which way a cost should push for each task
- Door ④: paste measurements back in, project onto hard limits, or start from a classical draft
- Door ⑤: check, select and reweight the finished samples, and test them on a real task
- A worked test on four loop detectors, one piece of knowledge at a time, and how to show that knowledge helped
- Where it breaks, fit card, applications, the interactive companion, six questions and project ideas

A diffusion model learns what traffic looks like only from its training data. You know things the data may show weakly or not at all: a car cannot brake much harder than 1 g, vehicles are conserved on a road, a lane closure caps the flow, and a near-miss matters more than a thousand ordinary passes. This page shows **where that knowledge can enter a diffusion model, what your data must contain for each entry point, and how to test whether the knowledge helped.**

It builds on {doc}`4.10 Diffusion models: the basics <notes6-diffusion-basics>`, {doc}`4.12 Diffusion in the literature <notes8-diffusion-literature>`, {doc}`4.11 Reading unCLIP <notes7-unclip>`, and the {ref}`35-paper diffusion companion <diffusion-papers-library>`. It also takes three ideas from the *unCLIP and Conditional Generation* handout further: the two ways to steer the denoiser (train a condition in, or guide while sampling), the sorting of conditions by the kind of information they carry, and engineering costs as guides.

**After this page you should be able to:**

1. Name the five doors where transportation knowledge can enter a diffusion model, and say which ones need retraining.
2. Take one piece of knowledge (a law, a rule, a measurement, a context fact, a preference) and choose the right door for it.
3. List what your data must contain for each door: pairs, labels, masks, units, and an honest split.
4. Write an engineering cost for guidance, and say which way it should push for a given task.
5. Design a test that shows whether the knowledge helped, against a classical method.

**Symbols.** The same as {doc}`4.10 <notes6-diffusion-basics>` and {doc}`4.12 <notes8-diffusion-literature>`.

| Symbol | What it is |
| --- | --- |
| x | A clean example: a time–space speed map, a set of trajectories, a camera frame |
| z\_t | The noisy version of x after t noise steps (t = 1 … T) |
| g(z\_t, w, t, c) | The network's guess of the noise; w are its weights, c is the condition |
| x̂ | The clean example that this guess implies at step t |
| c, ∅ | The condition (a hint about x), and the "no condition" input used in its place |
| λ | Classifier-free guidance strength: how hard sampling leans on the condition |
| J(x), λ\_J | An engineering cost (low = what you want), and how hard sampling leans on it |
| m | A mask: 1 where a value is observed, 0 where the model must fill it in |

The sections on {ref}`door ③ <kg-door3>` and {ref}`door ④ <kg-door4>` also use α\_t (the share of signal variance left at step t, as in {ref}`4.10 <diffusion-math>`), y (observed values), γ (how far a physics step moves) and S (a physics smoother). The {ref}`worked example <kg-worked>` is synthetic: a simulated road where the true traffic state is known, so every number can be checked.

(kg-map)=
## The map: five doors for your knowledge

Knowledge can enter a diffusion model at five places. Two are set at training time and need retraining to change; three are added while or after sampling and can change from one run to the next. Your data sits under all five.

```{figure} ../_static/figures/HK_Five_Doors.png
:alt: A diagram titled: Knowledge enters at five doors; only the first two need retraining. Top panel, Train (changing these means retraining), holds two shaded doors: door 1, What you generate (x): actions plus a vehicle model, PCA, a time-space map; builds a law in, so every sample obeys it. Door 2, The condition c: map, signal phase, weather, settings, text; recorded with every training example (pairs). An arrow labelled trained model leads down to the middle panel, Sample (change these any time, no retraining). In it, three boxes form a loop: Noisy sample z_t (starts as pure noise), an arrow to Denoiser g (reads z_t, t and c), an arrow to Clean guess x-hat (what the guess implies), and an arrow from the clean guess back to the noisy sample labelled: next, less noisy sample; repeat until t = 0. Below the loop, door 3, Guide (lambda: lean harder on the condition; J(x-hat): slide downhill on an engineering cost; needs no new training data), and door 4, Hold fixed (paste observed values back in; project onto hard limits; start from a classical draft), each send an arrow up into the clean guess. An arrow labelled finished samples leads down to the bottom panel, After sampling, with door 5, Check, select, reweight: physics and rule checks, keep the best of many, weight samples to undo the steering. Under all three panels, a shaded box: Your data: every door draws on it. Context with every record, paired modalities, event labels (PET, crash type), masks and why values are missing, physical units, a split by site and time.
:width: 100%

Five doors for transportation knowledge (course diagram).
```

Door ③ acts on the clean guess x̂ at every denoising step. Door ④ holds values fixed in the sample at every step, or sets where sampling starts. Door ⑤ acts on the finished samples. {doc}`4.12 Diffusion in the literature <notes8-diffusion-literature>` counted five ways to get a dangerous scenario out. Here the lens is wider (any knowledge, not only danger): the representation becomes a door (①), and fill-in, hard limits and head starts share one door (④). Its five ways map onto the doors as: cost guidance → ③, head start and fill-in → ④, condition → ②, select → ⑤.

**Two questions help pick the door.** Does the knowledge describe *this one case* (a lane closure today) or *traffic in general* (a car cannot brake at 3 g)? And must it *always* hold, or only *usually*?

| Kind of knowledge | Transportation example | Where it goes |
| --- | --- | --- |
| A law that must always hold | Vehicle kinematics; two cars never occupy one spot | ① build it into x, or ④ project onto it |
| A rule that should usually hold | Speed limit; stay in lane; keep a gap | ③ cost guidance (a soft push) |
| A fact about this case, known before sampling | Lane closure; signal phase; weather; demand | ② condition (only if training examples carried it) |
| A measurement of this case | Detector readings; the first second of tracks | ④ paste it in, or ② condition on it |
| A preference for this task | Find near-misses; stress-test a planner | ③ cost guidance, then ⑤ reweight if you need rates |
| A classical model that gives a good draft | Adaptive smoothing; gravity model; IDM; a rule-made crash | ④ head start, or ② condition on its output |
| A sense of what is realistic | PET range; the 1 g limit; the fundamental diagram | ⑤ check and select (clip hard limits such as 1 g at ④ too) |

The door sections below ({ref}`door ① <kg-door1>` to {ref}`door ⑤ <kg-door5>`) take the doors one at a time, with the papers that use each. The {ref}`worked example <kg-worked>` tries five of these rows on one road where the truth is known.

(kg-data)=
## Data first: what each door asks of your data

Every door depends on data you prepare before training. Conditioning asks the most: each training example must carry its hint. Guidance asks the least about pairs, but its cost must be computable, in physical units, from the model's output.

| Door | Your data must contain | Transportation example | Without it |
| --- | --- | --- | --- |
| ① What you generate | Consistent units, frame rate and coordinates; the variables a law needs | Acceleration and yaw rate at 10 Hz in a lane-relative frame | Mixed scales; no way to build the law in |
| ② Condition | The hint stored with every training example, for the same case and time | Each dashcam clip with its signal phase, weather and speed limit | You cannot condition on what you did not record |
| ③ Guide | Values the cost can be computed from, and some examples near the region you steer toward | Positions in meters, so gaps, TTC and PET can be computed | The push goes where the data never were |
| ④ Hold fixed | A mask, a timestamp and an error estimate for every measurement | Which detector was down, when, and why | Wrong values pasted in as if exact; tests that hide the real outage pattern |
| ⑤ Check | Held-out real data by site and time, with engineering labels | Recorded near-misses with PET; police crash records | No way to tell plausible from real |

### Eight things to add to a transportation dataset before you train

1. **Keep the context with every record.** Signal phase and timing, speed limit, lane geometry, weather, light, work zones and incidents, on the same clock as the measurements. Context is what a condition reads. In [Scenario Diffusion](https://arxiv.org/abs/2311.02738), 0.895 of generated path points fell on drivable area with the map as a condition, and 0.411 without it (Table 1). And a condition can only ask for what the data contain: [MagicDrive](https://arxiv.org/abs/2310.02601) could not draw snow, and its night scenes came out too bright, because its training data had too little of either.
2. **Link the different records of one event.** A crash has a narrative, a sketch, coded police fields, and sometimes video or EDR data. Conditioning and an unCLIP-style prior learn from these pairs, so keep a case ID through de-identification. In the {ref}`course run of the unCLIP recipe <unclip-crash-run>` (207 training pairs), the narrative-to-sketch pairing was weak: the true sketch ranked 14th of 38 at the median, where chance is 19.5. Short, checkable fields (number of vehicles, maneuvers, crash type, directions) are worth testing as conditions beside the free text.
3. **Label events with engineering measures.** Store PET, TTC, minimum gap and peak deceleration for every interaction, and a crash type from a standard typology. Such labels become conditions or costs. [Wang et al.](https://arxiv.org/abs/2506.08459) condition on a wanted minimum gap, then ask for zero. [DiffScene](https://ojs.aaai.org/index.php/AAAI/article/view/32951) builds its test scenarios around three NHTSA pre-crash types. [Safe-Sim](https://arxiv.org/abs/2401.00391)'s cost sets a target time to collision with the tested vehicle.
4. **Record what is missing, and why.** A mask, the cause (detector down, occluded, outside the camera view), and the sensor error. [PMA-Diffusion](https://arxiv.org/abs/2512.06183) trains with masks and hides extra observed cells (a "double mask") so the model also learns to fill in detector rows that are always observed in the data. Trained only on sparse data, that cut its error in the sparsest case (5% of rows) from 0.0364 to 0.0289. Real outages are rarely random: if a detector fails more often in congestion, a test with random gaps flatters the model. [PriSTI](https://arxiv.org/abs/2302.09746)'s traffic gaps were injected at random, so test any imputer on your own real outage patterns before trusting it.
5. **Keep units, frames and scaling constants.** A cost is computed on the clean guess x̂ at every step, so the model's numbers must turn back into meters, seconds and mph. Store the normalization constants, the frame rate and the coordinate frame with the data.
6. **Keep the ordinary with the rare.** The model learns realism from ordinary traffic; steering finds the rare. Do not train on crashes alone. An unsteered model can be even rarer than reality: in the worked example of {doc}`4.12 <notes8-diffusion-literature>`, it made 29 conflicts per 100,000 samples, against 83 per 100,000 recorded interactions.
7. **Split by site and time, and keep real data for the final test.** Hold out whole corridors, intersections or days, as the course crash data does by corridor. A generated sample counts as evidence only after it improves a result on held-out real data.
8. **Mark simulated data as simulated.** Simulation widens the coverage of dangerous cases: [Nexus](https://arxiv.org/abs/2504.10485) trains partly on simulated safety-critical scenes. But simulated data carry the simulator's simplifications, and generated crashes still need checking: some of Nexus's have overlapping vehicle boxes. Keep a column that says where each example came from.

**How much data?** There is no universal number. For scale: [VBD](https://arxiv.org/abs/2404.02524) trained on 486,995 Waymo scenarios; DiffScene on 6,995 simulated trajectories; the course crash run on 207 pairs, where the narrative did not steer the generated sketch beyond chance.

### What a diffusion-ready record looks like

The rows below are made up, to show the columns. One row per road user per time step; the last columns carry the context, the mask and the event labels that the doors need.

```text
event_id,site_id,split,source,t_s,agent,x_m,y_m,v_mps,a_mps2,yaw_rate_rps,lane_id,signal_phase,speed_limit_mph,weather,light,observed,missing_reason,min_pet_s,min_ttc_s,event_type
E0412,INT-07,train,camera,12.3,veh_2,41.8,3.5,9.6,-3.1,0.00,EB_through,green,45,rain,night,1,,0.8,1.4,near_miss_left_turn
E0412,INT-07,train,camera,12.4,veh_2,,,,,,EB_through,green,45,rain,night,0,occluded_by_bus,0.8,1.4,near_miss_left_turn
E0412,INT-07,train,camera,12.3,veh_5,30.1,-6.2,4.1,0.6,0.21,WB_left,green,45,rain,night,1,,0.8,1.4,near_miss_left_turn
```

A one-page data card next to the file (what was recorded, units, clock, mask causes, labels, split, simulated or real) answers most of the questions above at once.

(kg-door1)=
## Door ① — choose what to generate: put the law in the representation

The surest way to make every sample obey a law is to generate something that cannot break it. Diffusion is a training method, not a network, so you are free to choose what x is. Six of the nine safety-scenario papers in the {ref}`diffusion papers companion <diffusion-papers-library>` do not generate positions at all. They generate each vehicle's acceleration and turn rate, and compute positions by rolling those actions through a simple vehicle model:

- next position = position + speed × (cos heading, sin heading) × Δt
- next speed = speed + acceleration × Δt; next heading = heading + turn rate × Δt

*In words:* the model chooses how hard to press the pedals and turn the wheel; physics decides where the car goes. A car can no longer jump sideways or teleport, at any guidance strength. It can still leave the road, hit another car, or roll backward unless its speed is clipped at zero. The actions themselves still need limits: a 3 g brake is a valid number to the vehicle model.

| What you generate | Knowledge it builds in | Papers | What it costs you |
| --- | --- | --- | --- |
| Actions rolled through a vehicle model | Positions follow physics; every path is one a car could physically drive | [CTG](https://arxiv.org/abs/2210.17366), [CTG++](https://arxiv.org/abs/2306.06344), Safe-Sim, VBD, [CCDiff](https://arxiv.org/abs/2412.17920), [LangTraj](https://arxiv.org/abs/2504.11521) | No skids or spins; action limits still needed |
| A few principal components of each path | Smooth, car-like paths | [MotionDiffuser](https://openaccess.thecvf.com/content/CVPR2023/html/Jiang_MotionDiffuser_Controllable_Multi-Agent_Motion_Prediction_Using_Diffusion_CVPR_2023_paper.html) (80 × 2 values → 10); the course left-turn example (58 → 20; physics failures under 1% at every guidance strength) | Paths outside the basis cannot be made |
| An autoencoder's latent | The structure the autoencoder learned | [AdvDiffuser](https://arxiv.org/abs/2410.08453): best-sample endpoint error (minSFDE) 931 m when diffusing raw trajectories vs 2.21 m in the latent (Table I) | Decoder errors; costs need a decode step |
| An on/off channel per vehicle and per signal | Vehicles enter and leave; lights change | [SceneDiffuser++](https://openaccess.thecvf.com/content/CVPR2025/html/Tan_SceneDiffuser_City-Scale_Traffic_Simulation_via_a_Generative_World_Model_CVPR_2025_paper.html) | It spawned vehicles onto the planner's route and into parking lots |
| A time–space map on fixed cells | Order in space and time; fits an image denoiser | PMA-Diffusion (100 ft × 1 s cells); the course CTM maps (0.2 mi × 28.8 s) | Cell size sets which waves you can see |
| Structure first, then values | Most origin–destination pairs carry no trips | [DiffODGen](https://arxiv.org/abs/2306.04873): first which tract pairs exchange commuters, then how many | Two models to train |

**Where it breaks.** A representation also limits what can be made. A unicycle model cannot slide. [SceneDiffuser](https://arxiv.org/abs/2412.12129) reuses the log's on/off mask, so no vehicle can enter or leave beyond what the log recorded. Choose the representation for the events you need, not only for the ones that are easy.

(kg-door2)=
## Door ② — train it in: match the condition to the information

A condition is any hint about x that you can hand the denoiser both in training and when you sample. The network learns what a hint means only from pairs, so the hint must sit in every training example ({ref}`Data first <kg-data>`). How it enters the network depends on its shape.

```{figure} ../_static/figures/HK_Four_Inlets.png
:alt: A diagram titled: A condition enters through one of four inlets, chosen by its shape. A column of three boxes runs down the middle: Noisy sample z_t, an arrow down to Denoiser block (repeated at every level of the network), an arrow down to Noise guess g. Four shaded inlets point into it. Left, top: Stack with the input, for hints on the same grid as x, e.g. a map raster or observed cells; its arrow goes into the noisy sample. Left, below: Side branch, added in, for dense layouts (maps, boxes), e.g. MagicDrive, Panacea, Cosmos; its arrow goes into the denoiser block. Right: Scale and shift, for one global setting, e.g. city, ego speed, CTM settings; and Cross-attention, for sets of agents, lanes, text, e.g. VBD, MotionDiffuser, LangTraj; both arrows go into the denoiser block.
:width: 100%

Four inlets for a condition (course diagram; the examples come from the 35-paper diffusion companion).
```

The training loss is the one from {ref}`4.10 <diffusion-training>` with one more input:

$$
L(\mathbf{w}) \;=\; \left\| \, g(\mathbf{z}_t, \mathbf{w}, t, \mathbf{c}) - \boldsymbol{\epsilon} \, \right\|^2
$$

*In words:* name the noise that was added, now with the hint c in view. For a share of the examples, c is swapped for a "no condition" input ∅ (a learned vector, or simply zeros), so one network can run with or without the hint. Ten to twenty percent is common (the course heatmap model drops its three settings, and MagicDrive its camera pose and text, 20% of the time); LangTraj drops its text and history half the time. Classifier-free guidance ({ref}`door ③ <kg-door3>`) needs this.

### Six kinds of information, and how each enters

| Information | How it enters | Papers that do it | Data you need | Check for |
| --- | --- | --- | --- | --- |
| **One global setting**: weather, city, demand, a lane-closure capacity, ego speed | A learned vector added to the time signal; scale and shift in every block | [SLEDGE](https://arxiv.org/abs/2403.17933) (city), [GAIA-2](https://arxiv.org/abs/2503.20523) (ego speed, curvature), [DiffTraj](https://arxiv.org/abs/2304.11582) (trip attributes), the course CTM model (three settings) | The setting stored with every example | A single number cannot say *where* (where the queue is) |
| **Text**: a crash narrative; "vehicle A yields to B" | Tokens from a text encoder, read by cross-attention | [LangTraj](https://arxiv.org/abs/2504.11521) (text cut minADE by 13.6%), MagicDrive and [Panacea](https://arxiv.org/abs/2311.16813) (weather, time of day) | Text written for every example | Counts, who-did-what, distances; LangTraj follows the history when the sentence disagrees with it |
| **A layout on a grid**: lane map, drivable area, 3D boxes drawn into the camera view | Stacked with the input, or a side branch added in (ControlNet) | Scenario Diffusion (map channels), MagicDrive (map branch), Panacea (19-channel layout), [Cosmos-Drive-Dreams](https://arxiv.org/abs/2506.09042) (HD-map video) | Maps registered to every sample | Misregistered or out-of-date maps |
| **Sets and relations**: other agents' histories, lane polylines, signal states, a detector graph, census tracts | An encoder makes tokens that cross-attention reads; graph layers; or an attention mask | VBD (agents, 256 polylines, 16 lights), MotionDiffuser, CCDiff (a time-to-collision mask), PriSTI and [DiffSTG](https://arxiv.org/abs/2301.13629) (sensor graph), DiffODGen (census and POI counts) | Synchronized tracks, maps and signal logs | Future data leaking into the history; missing agents |
| **Known parts of x**: the last second of tracks, detector rows, a goal | Joined to the noisy input with a mask, trained on masks like those met in use | [DJINN](https://arxiv.org/abs/2309.12508) (mixed masks), SceneDiffuser (many mask tasks), Nexus (zero-noise tokens), DiffSTG (history), PriSTI (a linear interpolation of what was observed) | The mask patterns you will meet in practice | Gaps unlike the training gaps |
| **Another model's embedding**: a CLIP embedding of a sketch or a camera view | Projected into tokens and into the time signal | unCLIP (a prior makes the embedding, a decoder draws from it), [LiDM](https://openaccess.thecvf.com/content/CVPR2024/papers/Ran_Towards_Realistic_Scene_Generation_with_LiDAR_Diffusion_Models_CVPR_2024_paper.pdf) (CLIP camera features; text swapped in) | Pairs to learn the bridge | What the embedding drops: counts, exact positions |

One model can take several rows at once. MagicDrive, for example, takes the map through a side branch, and each box and the text as tokens read by cross-attention.

### Four lessons from the papers

1. **The context can decide whether samples are usable.** Scenario Diffusion's map condition moved the share of path points on drivable area from 0.411 to 0.895. In the {ref}`worked example <kg-worked>`, three context numbers cut the fill-in error on a simulated road from 8.1 to 4.4 mph.
2. **Pick the inlet by the hint's shape.** GAIA-2's authors found ego speed and curvature steered the video more accurately through scale-and-shift than through cross-attention, because an action changes every part of the image. When MagicDrive's boxes were fed only as part of the map image, vehicle mIoU on its generated scenes fell to 5.50 (Table 4).
3. **Check that the network uses the hint.** In the {ref}`course run of unCLIP on crash sketches <unclip-crash-run>`, the first decoder received the sketch embedding at about one sixth of the strength of the time signal and learned to ignore it: two samples from the same seed, with and without the embedding, had pixel correlations of 0.64–0.70, so the embedding barely changed the picture. Scaling it up by √512 (about 23 times) made it matter about as much as the noise. Even then, every pipeline driven by the narrative stayed at chance, because the narrative–sketch pairing itself was weak ({ref}`Data first <kg-data>`). Always compare samples drawn with and without c.
4. **Conditioning cannot make what the pairs lack.** MagicDrive's snow never appears, because its data had almost none. A crash is too rare to pair with every scenario, which is why 8 of the 9 safety-scenario papers steer with guidance ({ref}`door ③ <kg-door3>`) instead.

(kg-door3)=
## Door ③ — steer while sampling: lean on a condition, push down a cost

Guidance changes each denoising step without retraining. It comes in two kinds: lean harder on a condition the model already understands (classifier-free guidance), or push the sample downhill on an engineering cost you write (cost guidance). The first needs a trained condition; the second needs a cost you can compute and take a slope of ({ref}`Write a cost that behaves <kg-cost>`).

### Classifier-free guidance: a dial on the condition

$$
g_{\lambda} \;=\; g(\mathbf{z}_t, \mathbf{w}, t, \varnothing) \;+\; (1+\lambda)\,\left[\, g(\mathbf{z}_t, \mathbf{w}, t, \mathbf{c}) - g(\mathbf{z}_t, \mathbf{w}, t, \varnothing) \,\right]
$$

*In words:* ask the network twice at each step, with the hint and without it, and step further in the direction the hint points. λ = 0 gives an ordinary conditional sample. λ > 0 leans harder on what the hint implies, and the samples become more alike.

Papers write the dial in different ways, so always read the formula. [DiffTraj](https://arxiv.org/abs/2304.11582) writes (1 + ω) ε(x | c) − ω ε(x | ∅) with ω = 3, which is λ = 3 here. MagicDrive uses a guidance scale of 2.0, CCDiff a weight between 1 and 2, and GAIA-2 a scale from 2 to 20, applied only to rare or unusual scenes. If MagicDrive follows Stable Diffusion's convention (scale = 1 + λ), its 2.0 means λ = 1.

**The condition does not have to be words.** CCDiff asks for two predictions: one where each vehicle reacts to the vehicles that affect it (its "causal parents"), and one where no vehicle reacts to anyone. The parents come from a time-to-collision check (3.0 s threshold) combined with attention weights. Guidance between the two then turns interaction up. Traffic knowledge (who affects whom) has become a dial.

**A dial is not information.** λ cannot add anything that c does not carry; it only leans harder on it. That can narrow the variety of samples or pull them off target. That is fine for "show me a typical scene under this closure", and harmful for "how uncertain is this queue estimate?". In the {ref}`worked example <kg-worked>`, λ = 3 on the correct context raised the fill-in error from 4.4 to 5.2 mph.

### Cost guidance: write the knowledge as a cost

Choose a cost J that is low for what you want, computed from the clean guess x̂ in physical units. At every step, change the noise guess so that the next, less noisy step slides downhill on J. This is the equation of {doc}`4.12 <notes8-diffusion-literature>` (in “Five ways to get a dangerous scenario out”), where the strength is written λ:

$$
g_{J} \;=\; g(\mathbf{z}_t, \mathbf{w}, t, \mathbf{c}) \;+\; \lambda_J \sqrt{1-\alpha_t}\; \nabla_{\mathbf{z}_t} J(\hat{\mathbf{x}})
$$

| Symbol | Meaning |
| --- | --- |
| J(x̂) | The engineering cost of the clean guess: meters, seconds or mph, scaled to have no units |
| λ\_J | How hard sampling leans on the cost, a number you choose |
| √(1 − α\_t) | Scales the push with the noise level: large early, small near the end |
| ∇\_{z\_t} J | The direction that would raise J fastest, found by backpropagating through the network |

*In words:* every step, score the clean guess with your cost and nudge the sample toward a lower score. Papers differ in where they push: CTG takes a few clipped Adam steps on the mean of the next, less noisy step; VBD and MotionDiffuser push on the clean guess x̂.

**A catalog of engineering costs from the papers**

| Cost J (low = wanted) | Knowledge it carries | What the paper found |
| --- | --- | --- |
| Speed above the limit, over time | Speed limits | CTG: rule violation 1.380 without guidance or filtering, 0.019 with both (Table II). CCDiff, with an over-speed cost on key vehicles only, met the speed rule about as often as CTG but left the road far less often (off-road 0.89 vs 4.23, Table 7) |
| Overlap or closeness between vehicles | No collisions | VBD: collisions 2.47% → 1.11%, no retraining (Table III). MotionDiffuser: overlap rate 0.008 with a repeller cost |
| Distance off the drivable area | Stay on the road | CTG and CCDiff use an off-road cost; CCDiff applies it only to the key vehicles |
| Distance from a target point | Reach a goal | MotionDiffuser: met targets and stayed realistic; fixing paths with an optimizer after sampling looked unrealistic (Table 2) |
| Overlaps, harsh acceleration, lane offset | Comfort and lane keeping | Nexus: three hand-written corrections at every step |
| Time to collision and relative speed toward the tested vehicle | An aimed threat to the tested vehicle (the crash type comes from a {ref}`head start <kg-head-start>`) | Safe-Sim: collisions in 43.2% of scenes vs 36.4% for STRIVE (Table 2) |
| Closest distance between two road users, plus a support cost | A near-miss, but only from set-ups real drivers accept | Course left-turn example. Conflict cost alone: conflicts in 0.97% of samples at λ\_J = 0.3, 26.64% at 1, 96.64% at 3. Adding the support cost cut the conflicts that began from too-short gaps at λ\_J = 1 from 40% to 0% |
| A learned danger score | Danger to the tested planner | AdvDiffuser, against a rule-based planner: the tested AV crashed in 11.03% of scenarios, while only 0.27% of background vehicles hit each other (Table II) |
| Code an LLM writes from a sentence | Any request in words | CTG++: GPT-4 writes the loss; nothing checks that the code means what you asked |

### The task decides which way the cost points

The same cost can be right for one task and wrong for the next. Penalizing collisions is right for your own vehicle's plan. For a forecast of other drivers, or for crash scenarios, it would delete the very events the task must represent.

| Task | Push toward | Push away from | Why |
| --- | --- | --- | --- |
| Plan for your own vehicle | Goal, comfort | Collisions, lane departures | The plan must be safe |
| Background traffic for a test | Traffic rules, realism | Collisions among background vehicles | The tested vehicle needs normal traffic around it |
| An adversary for a safety test | Closing in on the tested vehicle | Crashes with others; leaving the road | Danger must be aimed and plausible |
| Forecast of other road users | Nothing beyond physical limits | Nothing | A preference would bias the forecast and its uncertainty |
| Crash and near-miss scenarios | Short gaps, short PET | Set-ups outside the recorded range | Without the support cost, conflicts arise in ways no driver produced |
| Traffic state estimation | Agreement with measurements and physics | Nothing | A preference here becomes a bias in an agency report |

"No overlapping vehicles" is a law, not a preference, so it belongs in door ① or ④ for every task; MotionDiffuser's forecaster uses a repeller cost for it. The warning in the forecast row is about preferences such as "keep a safe gap", which would hide the real near-misses you are trying to forecast.

(kg-cost)=
### Write a cost that behaves

- **Use units, then scale them away.** Compute J from meters, seconds or mph on x̂, and divide by a typical size for that quantity (for example 1 m for a gap, 1 s for PET, 10 mph for speed), so one unit of J means a similar amount of "wrong" in every cost.
- **Make it smooth.** A hard rule ("gap below 2 m") has no slope almost everywhere. Use a soft version: softplus (a ramp with a rounded corner) for a threshold, and a smooth minimum (a soft version of "the smallest value") for the closest distance.
- **Limit the push.** CTG and MotionDiffuser clip their gradient steps. A push that is too strong breaks realism before it meets the goal.
- **Guide only the vehicles that matter.** CCDiff guides only the key agents. The share of agents whose realism and guidance pulls pointed in conflicting directions fell from about 9.1% (CTG) to about 4.8%.
- **A soft cost is not a guarantee.** It makes a violation less likely, not impossible. A law that must always hold belongs in door ① or ④.

### Rules against realism

Many papers that guide report the same tension. In CTG, more guidance steps cut rule violations but worsened realism and the failure rate (at its default setting, guidance plus filtering improved both). In the course left-turn example, strong steering made conflicts from gaps no driver accepted; a support cost closed that shortcut, and at λ\_J = 3 the next one opened (the through driver barely slowed: median slowdown about 0). Judge guided samples by **how** they reach the goal, not only by whether they reach it.

:::{admonition} Going deeper &mdash; what guidance does to frequencies
:class: dropdown

Cost guidance aims at a tilted version of the model's distribution, in which low-cost samples are more likely:

$$
p_J(\mathbf{x} \mid \mathbf{c}) \;\propto\; p(\mathbf{x} \mid \mathbf{c}) \; e^{-\lambda_J J(\mathbf{x})}
$$

A guided sample therefore says nothing about how often the scenario happens. To get back to the unguided model's frequencies (which can themselves be off: 29 against 83 conflicts per 100,000 in the left-turn example), each sample would need the weight

$$
\mathrm{weight}(\mathbf{x}) \;=\; \dfrac{p(\mathbf{x} \mid \mathbf{c})}{p_J(\mathbf{x} \mid \mathbf{c})} \;\propto\; e^{+\lambda_J J(\mathbf{x})}
$$

normalized over the samples. The sampler only approximates p\_J, so in practice frequency estimates use importance sampling with a proposal whose density is known, as in the *Generating Crash Data from Near-Misses* handout (steered crash share 0.58%, about 440 times the unsteered share, relative standard error 2.4%). Treating −λ\_J J as a log-probability is what turns classifier guidance into cost guidance: Dhariwal & Nichol (2021); [Chung et al. (2023)](https://arxiv.org/abs/2209.14687).
:::


(kg-door4)=
## Door ④ — hold it fixed: paste, project, or start from a draft

Some knowledge should not be a push but a fact the sample must keep. You can paste measurements back in, project the sample onto a hard limit, or start sampling from a classical model's draft. None of these needs retraining.

### Paste the measurements back in

$$
\mathbf{z}_t \;\leftarrow\; \mathbf{m} \odot \left( \sqrt{\alpha_t}\, \mathbf{y} + \sqrt{1-\alpha_t}\, \boldsymbol{\epsilon}^{\prime} \right) \;+\; (1-\mathbf{m}) \odot \mathbf{z}_t
$$

*In words:* y holds the observations (detector speeds, the logged history), m marks where they are, and ε′ is fresh noise. Before each denoising step, the observed cells are overwritten by the observation, noised to the step's level, and the model fills in the rest to match. In {ref}`4.10 <diffusion-steering>`, the course heatmap model filled a four-cell detector outage this way with 2.34 mph error, against 5.16 mph for interpolation.

Papers paste in different things: PMA-Diffusion pastes sparse detector rows and probe traces; SceneDiffuser keeps the logged history; SceneDiffuser++ keeps the test vehicle that a separate planner drives; SLEDGE keeps a real lane map and generates the traffic on it; [RoadFusion](https://arxiv.org/abs/2507.15346) uses a mask to say where a pavement defect may appear.

**Pasting assumes the measurement is right.** A biased detector is pasted in as truth. PMA-Diffusion's ground truth came from I-24 MOTION camera data masked on purpose, and real loop and GPS data add bias and time delay, which the paper assumed away.

### Project onto hard limits

- **Re-roll through the vehicle model at every step.** CTG and CCDiff recompute positions from the actions after each step, so door ①'s law holds throughout.
- **Clip the scene.** SceneDiffuser enforces constraints such as "no overlapping vehicles" at every denoising step. A no-collision constraint raised its composite realism score from 0.516 to 0.558; logged data scores 0.593 (Table 1).
- **Add a physics step.** After each step, PMA-Diffusion smooths only the missing cells along the free-flow and congested wave directions of traffic flow theory:

$$
\hat{\mathbf{x}} \;\leftarrow\; \mathbf{m} \odot \mathbf{y} \;+\; (1-\mathbf{m}) \odot \left[ (1-\gamma)\, \hat{\mathbf{x}} + \gamma\, S(\hat{\mathbf{x}}) \right]
$$

Here S is a smoother that knows the two wave speeds, and γ sets how far each step moves toward it. With a prior trained on complete maps, 5% of detector rows observed and no probe vehicles, PMA's mean squared error on hidden cells (speeds divided by a fixed maximum) was 0.1463 for physics smoothing alone, 0.0172 for diffusion fill-in, and 0.0167 with the physics step added (Table 2). The {ref}`worked example <kg-worked>` tries the same idea with the adaptive smoothing method: it helped when the model had only the detectors, and hurt once the model also had the context.

(kg-head-start)=
### Start from a classical draft

Run your classical model first, add noise up to a middle step, and let the diffusion model finish. The noise level decides how much of the draft survives: little noise keeps the draft, much noise keeps only its rough shape.

| Paper | The classical draft | What it found |
| --- | --- | --- |
| [CoDiffMob](https://arxiv.org/abs/2412.05000) | Rule-based daily trips that follow the city's real OD flows, run backward into noise | City flow match (CPC) 0.6842 vs 0.3992 for DiffTraj; without the draft, 0.3416 (Tables 1–2) |
| Safe-Sim | A rule-made crash sketch, noised partway | Collisions 23.9% → 29.0%; spread of collision points 1.62 → 5.44 m (Table 5) |
| DJINN | A scene edited by hand, noised to τ = 0.8 | Shown as editing examples; no number reported for this use |
| [DiffusionDrive](https://openaccess.thecvf.com/content/CVPR2025/html/Liao_DiffusionDrive_Truncated_Diffusion_Model_for_End-to-End_Autonomous_Driving_CVPR_2025_paper.html) | 20 anchor paths (clusters of training paths), lightly noised | 2 steps, 45 frames per second, driving score 88.1 (Table 2) |

A classical estimate can also enter as a condition instead (door ②). PriSTI hands its denoiser a linear interpolation of the observed readings plus the sensor graph; at the highest missing rate on METR-LA, with gaps in long blocks, its error was 4.67–34.11% lower than three earlier imputers (Fig. 5; an overall comparison, not split by component).

| Tool | What it guarantees | What it can break |
| --- | --- | --- |
| Paste measurements | Observed values are kept | Biased sensors are trusted; seams between pasted and generated cells |
| Project or clip | The limit holds after every step | Samples pushed away from what the model knows |
| Physics step | Smoothness along traffic waves | Wrong wave speeds smear real features |
| Head start | The draft's large-scale structure | The draft's errors survive; variety can shrink (CoDiffMob reports less diversity), though Safe-Sim's sketches made crashes more varied |

(kg-door5)=
## Door ⑤ — check, select, reweight

After sampling, your knowledge works as a judge. It can reject impossible samples, keep the most useful ones, or weight them back toward the model's own frequencies. These are three different jobs. Rejecting impossible samples changes frequencies least, but even it shifts the shares when failures cluster in one kind of event. Selecting and weighting change them on purpose.

### Check every sample against engineering knowledge

| Output | What to check | An example of the check catching something |
| --- | --- | --- |
| Trajectories | Deceleration within about 1 g, no reversing, plausible jerk, on the road, no overlapping vehicles | The physics judge of the *Generating Crash Data from Near-Misses* handout failed 95% of a VAE's generated crashes and 0% of real ones |
| Near-misses and conflicts | PET and TTC against recorded ones; the set-up (gap, speed) inside the recorded range; how the evasive action happens | Course left-turn example, conflict cost alone: at λ\_J = 3, 57% of conflicts began from a gap shorter than any recorded |
| Traffic states | Speeds between zero and free flow; congestion waves moving upstream at the wave speed; the fundamental diagram; vehicles conserved where flow and density exist | {ref}`Worked example <kg-worked>` |
| Camera and lidar data | A detector trained on real data, run on generated frames | [DrivingDiffusion](https://arxiv.org/abs/2310.07771): a pretrained BEVFusion scored object NDS 33.1 on generated frames vs 41.2 on real ones (Table 2) |
| OD matrices and trips | Totals against counts; share of empty pairs; trip-length distribution | DiffODGen: 24.9% of real New York tract pairs exchange commuters vs 33.0% in its generated matrix |

### Select the best of many

Many papers draw several samples and keep one. CTG keeps the best of several guided samples. LangTraj keeps the lowest-collision-loss sample of 64. SLEDGE keeps the busiest of 8 scenes. DiffusionDrive's learned score picks one of its 20 plans. [Challenger](https://arxiv.org/abs/2505.15880) scores candidates in a physics simulator and re-noises the best for five rounds. Cosmos-Drive-Dreams lets a vision-language model reject clips with visible errors (3% were discarded).

**Selection changes frequencies just as guidance does.** A set of "worst of eight" scenes cannot give a rate. If the output feeds a number such as crashes per year, count over all the samples you drew and use the selected ones only as test cases, or use a method built for rates, such as the importance sampling of the *Generating Crash Data from Near-Misses* handout.

### The final check is a real task

A generated sample counts as evidence only after it improves a result on held-out real data. The papers below test generated data on a real task and report one number you can check:

- [DiffTraj](https://arxiv.org/abs/2304.11582): a flow model trained on synthetic trips reached inflow MSE 4.55, against 4.33 when trained on real trips (Table 2): close to real data, not better. That makes it a stand-in for private data, not an improvement.
- [MagicDrive](https://arxiv.org/abs/2310.02601): adding its images raised a BEV segmentation model's vehicle mIoU by 4.34 (Table 3).
- [Cosmos-Drive-Dreams](https://arxiv.org/abs/2506.09042): generated rain and fog clips raised 3D lane-detection F1 on rainy and foggy test clips by 10.4% and 9.4% (Table 1).
- [DrivingDiffusion](https://arxiv.org/abs/2310.07771): frames focused on rare cases raised BEVFusion's NDS from 0.412 to 0.434 (Table 3).

Notice what these share: a classical or real-data baseline, a held-out real test set, and one number a reader can check.

(kg-worked)=
## Worked example: four detectors, one piece of knowledge at a time (synthetic)

On a simulated 4-mile road watched by four detectors, giving the diffusion model three context numbers (starting density, demand and the bottleneck's capacity) cut its error on the hidden cells from 8.1 to 4.4 mph. Context that was wrong by a quarter of its range raised the error to 15.0 mph, worse than straight-line interpolation. Physics knowledge helped only while the model knew little else.

### The road and the task

- **The road.** The course's 4,000 simulated speed maps (the CTM data of the VAE and diffusion labs): a 4-mile road over 9.6 minutes, free-flow speed 75 mph, congested wave speed 15 mph, jam density 200 veh/mi, drawn on 20 road cells × 20 time steps (each cell 0.2 mi × 28.8 s). Each map has its own starting density, demand at the upstream end, and a bottleneck at the downstream end with its own capacity, start and duration. In the 50 test maps, 43% of cells are below 40 mph.
- **The task.** Four loop detectors at mileposts 0.5, 1.5, 2.5 and 3.5 report speed at every time step. Fill in the other 320 cells of each map.
- **The model.** The course heatmap diffusion model from {doc}`4.10 <notes6-diffusion-basics>` (765,153 weights), not retrained. It learned the three settings as a condition, dropped 20% of the time, so it runs with or without them. Each estimate is the average of 8 fills of 1,000 denoising steps.
- **The test.** 50 test maps the model never saw, the same 50 as the gap-filling example in {ref}`4.10 <diffusion-steering>`. Every tuning choice was made on separate validation maps.

### The ladder

| Rung | Knowledge added | Door |
| --- | --- | --- |
| Linear interpolation | None | Classical baseline |
| Adaptive smoothing (ASM) | Traffic flow theory: speed patterns travel downstream at 75 mph in free flow and upstream at 15 mph in congestion | Classical baseline |
| Context only | Starting density, demand and bottleneck capacity; no detectors | ② condition |
| Detectors pasted in | The four detectors' readings | ④ fill in |
| + physics step | ASM's two wave speeds, applied after every step (share γ = 0.3) | ④ physics step |
| + head start | ASM's estimate, noised to step 500 of 1,000 | ④ head start |
| + context | The three settings, with the detectors pasted in | ② + ④ |
| + context, guidance 3 | The same, with λ = 3 | ② + ③ + ④ |
| + context with errors | Each setting off by a quarter of its range, up or down at random | ② (wrong) + ④ |
| + context + physics step | Both kinds of knowledge | ② + ④ |

Chosen on validation maps: ASM widths 0.2 mi and 0.25 min, switch speed 60 mph, switch width 40 mph; physics share γ = 0.3 (0.15 and 0.7 did worse); head start at step 500 (100, 250 and 700 did worse).

```{figure} ../_static/figures/HK_Ladder_Chart.png
:alt: Two horizontal bar charts side by side, titled: Right context halves the error; wrong context is worse than none. One row per rung, with the error on hidden cells in mph and the queue-length error in miles: linear interpolation 11.5 and 0.26; adaptive smoothing (true wave speeds) 9.1 and 0.14; diffusion, context only, no detectors 9.2 and 0.20; diffusion, detectors pasted in 8.1 and 0.13; plus physics step 7.2 and 0.12; plus head start from smoothing 6.4 and 0.09; plus context (three settings), the only blue row, 4.4 and 0.07; plus context, guidance 3, 5.2 and 0.08; plus context with errors 15.0 and 0.44; plus context plus physics step 5.1 and 0.08. Dashed marks in every row show the adaptive smoothing level.
:width: 100%

The ladder on 50 simulated test maps, 8 fills each (results in `genmodels/hk_knowledge/hk_results.json`). The left bars give the average error over the hidden cells; the right bars give the error in the length of road below 40 mph, averaged over time steps. Blue marks the detectors plus correct context.
```

```{figure} ../_static/figures/HK_Fill_Example.png
:alt: Five speed heatmaps of one simulated test map, titled: Three context numbers let the model place a queue that four detectors only glimpse. Milepost 0 to 4 runs up each panel and time 0 to 9.6 minutes across; colour runs from dark green (0 mph) to cream (75 mph); gold ticks mark the four detectors at mileposts 0.5, 1.5, 2.5 and 3.5. Truth (simulated): a slow band that rises from the lower left and a dark queue at the top right from about 4 minutes on. Interpolation, error on hidden cells 12.3 mph: blocky horizontal bands. Adaptive smoothing, 10.4 mph: smoother, with the queue at the top right. Diffusion, detectors only, 19.2 mph: a long congested band across the middle of the road. Diffusion plus context, 8.0 mph: close to the truth, with the downstream queue in place.
:width: 100%

One test map, picked by a rule (the one whose share of cells below 40 mph is closest to 30%). From the detectors alone, this fill invents a long congested band in the middle of the road; with the context, the fill places the downstream queue where it is.
```

| Rung | Truth inside the 8 fills' range (honest: 78%) | Beats adaptive smoothing (maps of 50) |
| --- | --- | --- |
| Context only | 79% | 23 |
| Detectors pasted in | 87% | 24 |
| + physics step | 64% | 32 |
| + head start | 86% | 46 |
| + context | 84% | 47 |
| + context, guidance 3 | 72% | 41 |
| + context with errors | 31% | 13 |
| + context + physics step | 52% | 49 |

The range is checked on hidden cells below free flow, as in {doc}`4.10 <notes6-diffusion-basics>`. With 8 fills, an honest range holds the truth about 7 times in 9 (78%).

### What the numbers say

1. **Detectors alone barely beat a good classical method.** Diffusion fill-in reached 8.1 mph against 9.1 mph for adaptive smoothing, and won on only 24 of 50 maps. Adaptive smoothing already carries the right traffic flow theory.
2. **Context is information the detectors cannot give.** The three settings cut the error to 4.4 mph and the queue-length error from 0.13 to 0.07 mi, and beat adaptive smoothing on 47 of 50 maps. Context alone, with no detectors, gave 9.2 mph. Neither source is enough by itself; together they halve the error.
3. **Physics helps most when the model knows little.** With detectors only, the physics step cut the error from 8.1 to 7.2 mph, and starting from the smoothing estimate cut it to 6.4 mph with half the denoising steps. Once the context was in, the physics step raised the error from 4.4 to 5.1 mph: it smoothed away detail the model had right.
4. **Wrong context is worse than none.** With each setting off by a quarter of its range, the error rose to 15.0 mph, above straight-line interpolation (11.5 mph), and the truth fell inside the fills' range only 31% of the time. The model was confidently wrong.
5. **The dial adds no information.** Guidance λ = 3 on the correct context raised the error from 4.4 to 5.2 mph.
6. **Check the spread, not only the average.** The physics step made the fills too alike: the truth fell inside their range 64% of the time (52% with context), against an honest 78%. A narrow band that misses the truth misleads an agency more than a wide one that admits doubt.

:::{admonition} Before you trust this example
:class: warning

- *Baseline:* linear interpolation, and adaptive smoothing with the road's true wave speeds, both tuned on validation maps.
- *Honest split:* the model saw only training maps; every setting (smoothing widths, physics share, head-start step) was chosen on validation maps; all scores come from 50 test maps used for nothing else.
- *Ugly cases:* the road is simulated, so adaptive smoothing and the physics step use exactly the right wave speeds, and the detectors have no noise or bias. On real roads both advantages shrink. The context is perfect in every run except the wrong-context one, and the bottleneck's start and duration were never given. With context, adaptive smoothing still won on 3 of the 50 maps. Fifty maps is a small test.
:::


The code and results are in the class folder under `genmodels/hk_knowledge`.

(kg-test)=
## Show that the knowledge helped

Adding knowledge is a design choice, and it needs a test like any other. The test is a ladder: start from the classical method and the plain model, add one piece of knowledge at a time, and hold everything else fixed. The {ref}`worked example <kg-worked>` is one such ladder.

1. **Start from two baselines.** The classical method an engineer would use today, tuned on the same validation data, and the same diffusion model with no added knowledge.
2. **Add one piece at a time.** Same data, same split, same number of samples and denoising steps. If two pieces go in together, you cannot tell which one helped.
3. **Score what the decision needs.** Queue length for a queue-warning sign, PET for a safety study, collisions and off-road rate for a planner test, not only an average error. Also check the spread: a 90% band from the samples should contain the true value about 90% of the time.
4. **Feed it wrong knowledge on purpose.** A stale map, a capacity off by a quarter, a mislabeled crash type. If small errors in the knowledge cause large errors in the output, you must know how good your knowledge is before you rely on it.
5. **Look at the ugly cases.** Which sites got worse, which cells, and which shortcuts guidance took.

:::{admonition} Before you trust a knowledge-guided generator
:class: warning

- *Baseline:* the classical method, tuned on the same validation data, and the same diffusion model without the knowledge.
- *Honest split:* held-out sites and days; every setting chosen on validation data only; outages and rare events as they really occur, not injected at random.
- *Ugly cases:* what happens when the knowledge is wrong, where guidance takes a shortcut, and whether the spread is too narrow to trust.
:::


(kg-breaks)=
## Where it breaks, fit card, and applications

### Where it breaks

1. **Wrong knowledge, followed faithfully.** A wrong wave speed, a stale map or a miscoded crash type is obeyed as if it were true. In the {ref}`worked example <kg-worked>`, settings off by a quarter of their range made the fill-in worse than straight-line interpolation (15.0 against 11.5 mph).
2. **Knowledge the data never paired.** You cannot condition on what was not recorded, and guidance toward it pushes the model where it has no data. In the course left-turn example, strong guidance produced conflicts from gaps no driver accepted.
3. **A preference treated as a fact.** A collision cost in a forecast, or a large λ in an uncertainty estimate, biases the result. Guidance and selection both change frequencies and narrow the variety of samples.
4. **Soft where it should be hard.** A cost makes violations rarer, not impossible: CTG's best speed-limit result still violates by 0.019. A law that must hold goes into the representation or a projection.
5. **Checks that pass for the wrong reason.** Every written check can pass while the mechanism is wrong, like the through driver who barely slows.
6. **Seams and leaks.** Pasted values can leave seams at the edge of the observed cells, and a "history" feature that peeks into the future makes any condition look good.
7. **The classical method was enough.** In the {ref}`worked example <kg-worked>`, adaptive smoothing with the right wave speeds came within 1 mph of diffusion fill-in from detectors alone (9.1 against 8.1 mph). On real I-24 data, PMA-Diffusion found smoothing alone far worse. Test before you assume either way.

### Fit card — knowledge-guided diffusion

| Field |  |
| --- | --- |
| Idea in one sentence | Put what transportation engineering already knows into the diffusion pipeline at the door that fits it: the representation, the condition, the guidance, a fixed value, or a check. |
| Why it works | The denoiser learns typical traffic from data; your knowledge adds the case-specific facts it cannot see and the laws and rules it learned only loosely, at the step where they act. |
| Fits these tasks | Generating or predicting several plausible outcomes under known constraints: scenarios for testing, detector gap filling, synthetic trips and OD matrices, sensor data for rare conditions. Leverage labels: generation, prediction. |
| Needs this data | Ordinary and rare examples with their context on the same clock; pairs for every condition; masks and their causes; physical units; a real test set split by site and time. Agencies hold detectors, signal logs and crash records; labs hold trajectory sets such as Waymo, nuScenes, highD and I-24 MOTION. |
| Breaks when | The knowledge is wrong or stale; the condition was never paired in training; a preference is applied where honest frequencies are needed; a law is entered as a soft cost. |
| Keep the classical method when | A physics-based estimator with known parameters already meets your accuracy (adaptive smoothing, a Kalman filter, a calibrated CTM); you need a rate rather than examples (extreme value theory, importance sampling); or you cannot test the generated data on a real downstream task. |

### Applications

| Domain | Task | Knowledge, and its door | Data | Classical baseline |
| --- | --- | --- | --- | --- |
| Traffic flow, agency practice | Fill detector gaps for performance reports | Readings → paste (④); incident and lane-closure logs → condition (②); wave speeds → physics step (④) | Loop detectors, incident logs, work-zone records | Adaptive smoothing; Kalman filter |
| Road safety | Near-miss scenarios at a signalized intersection | PET and gaps → cost (③); recorded set-ups → support cost (③); signal phase → condition (②); physics judge (⑤) | Camera trajectories, signal phase and timing, crash records | Extreme value theory on PET |
| ADAS and AV testing | Cut-ins for an ACC or lane-keeping test | Vehicle model → representation (①); TTC → adversary cost (③); rules → background cost (③) | Naturalistic driving (highD, Waymo), CAN data | Scenario libraries; rule-based adversaries |
| Consulting, planning | Synthetic trips for a corridor study | OD counts → head start (④) or condition (②); land use → condition (②) | LODES, household surveys, probe data | Gravity model; four-step model |
| Asset management | Rare pavement defects to train a detector | Defect type → text (②); where it may appear → mask (④) | Pavement images, distress surveys | Copy-paste augmentation |

(knowledge-guided-diffusion)=
## The five doors, hands on

A diffusion model learns traffic only from its data. This companion asks where your own knowledge as a transportation
engineer fits in. It walks through the five doors where knowledge can enter: what the model generates, the condition it
reads, guidance while it samples, values held fixed at every step, and checks on the finished samples. For each door it
lists what your data must contain, and it ends with how to test whether the knowledge helped.

Two &ldquo;Try it&rdquo; panels show a law built into what the model generates and a cost that tilts a distribution. The
worked example fills a simulated 4-mile road from four loop detectors, adding one kind of knowledge at a time, and lets
you open each of the 50 test maps. Three context numbers roughly halve the error, wrong context makes it worse than
straight-line interpolation, and a classical smoother with the right wave speeds is a hard baseline to beat. Read it
after the {ref}`diffusion papers companion <diffusion-papers-library>` in 4.12.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion &mdash; Five doors for transportation knowledge, and a worked test</span>
    <a href="../_static/companions/Knowledge_Guided_Diffusion_Companion.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/Knowledge_Guided_Diffusion_Companion.html"
          title="How transportation knowledge guides diffusion generation: data, conditions, guidance, fixed values and checks, with a worked example on four detectors" loading="lazy"></iframe>
</div>

(kg-practice)=
## Check yourself and project ideas

### Check yourself

1. An agency has three years of loop-detector data on a corridor and wants to fill gaps during incidents, but it never kept an incident log. Which door would carry the incident information, and what would the agency have to start recording first?
2. A colleague adds a collision-avoidance cost to a diffusion model that forecasts pedestrian paths at a crosswalk. What goes wrong? For which task would the same cost be right?
3. Your sketch generator seems to ignore the crash narrative. Describe two checks that tell apart a weak condition signal, a weak pairing, and too little data.
4. You want crash-like conflicts at a roundabout, but your data hold only 12 conflicts. Which doors are still open to you, and which number could you not report from the guided samples?
5. In the {ref}`worked example <kg-worked>`, three context numbers helped more than the physics step. Why? Describe a situation where you would expect the physics step to matter more.
6. A vendor says its diffusion model "respects traffic physics". Which three questions do you ask, and which door does each one probe?

### Project ideas with course data

- **Structured fields against free text.** On the course crash data, condition a sketch generator on a few coded fields (number of vehicles, maneuvers, crash type) and compare it with the narrative embedding, using the same corridor split and the ranking test of the {ref}`unCLIP crash run <unclip-crash-run>`.
- **A physics step on real detectors.** On PeMS data with real outage periods (not random gaps), compare adaptive smoothing, a Kalman filter, diffusion fill-in, and fill-in with a physics step.
- **Near-misses with a support cost.** Generate left-turn conflicts at one intersection with a conflict cost plus a support cost, and check PET, set-up support and braking behavior against recorded near-misses.
- **Is the work-zone log worth keeping?** Add lane-closure records as a condition for gap filling, and measure the gain on held-out days with closures.

### Where to go next

- {doc}`4.10 Diffusion models: the basics <notes6-diffusion-basics>`
- {doc}`4.11 Reading unCLIP: from a CLIP embedding back to an image <notes7-unclip>`
- {doc}`4.12 Diffusion in the literature: from image generators to safety scenarios <notes8-diffusion-literature>`
- The {ref}`diffusion papers companion <diffusion-papers-library>` (35 papers) in 4.12
- The *Generating Crash Data from Near-Misses* handout
- The *Generative Models in Transportation* handout
- The *unCLIP and Conditional Generation* handout

## References for 4.13

*Foundations:*

- Ho, Jain & Abbeel (2020). [Denoising Diffusion Probabilistic Models](https://arxiv.org/abs/2006.11239).
- Dhariwal & Nichol (2021). [Diffusion Models Beat GANs on Image Synthesis](https://arxiv.org/abs/2105.05233).
- Ho & Salimans (2022). [Classifier-Free Diffusion Guidance](https://arxiv.org/abs/2207.12598).
- Chung et al. (2023). [Diffusion Posterior Sampling for General Noisy Inverse Problems](https://arxiv.org/abs/2209.14687).
- Lugmayr et al. (2022). [RePaint: Inpainting using Denoising Diffusion Probabilistic Models](https://arxiv.org/abs/2201.09865).
- Perez et al. (2018). [FiLM: Visual Reasoning with a General Conditioning Layer](https://arxiv.org/abs/1709.07871).
- Zhang, Rao & Agrawala (2023). [Adding Conditional Control to Text-to-Image Diffusion Models](https://arxiv.org/abs/2302.05543) (ControlNet).
- Ramesh et al. (2022). [Hierarchical Text-Conditional Image Generation with CLIP Latents](https://arxiv.org/abs/2204.06125) (unCLIP).
- Bishop & Bishop (2024). *Deep Learning: Foundations and Concepts*, Chapter 20.

*Traffic flow:*

- Treiber & Helbing (2002). [An adaptive smoothing method for traffic state identification from incomplete information](https://arxiv.org/abs/cond-mat/0210050).
- Treiber, Kesting & Wilson (2011). [Reconstructing the traffic state by fusion of heterogeneous data](https://arxiv.org/abs/0909.4467).
- Daganzo (1994). The cell transmission model: A dynamic representation of highway traffic consistent with the hydrodynamic theory. *Transportation Research Part B* 28(4), 269–287.

*Transportation diffusion papers cited (details and figures in the {ref}`diffusion papers companion <diffusion-papers-library>`):* [CTG](https://arxiv.org/abs/2210.17366) · [CTG++](https://arxiv.org/abs/2306.06344) · [Safe-Sim](https://arxiv.org/abs/2401.00391) · [DiffScene](https://ojs.aaai.org/index.php/AAAI/article/view/32951) · [AdvDiffuser](https://arxiv.org/abs/2410.08453) · [VBD](https://arxiv.org/abs/2404.02524) · [CCDiff](https://arxiv.org/abs/2412.17920) · [LangTraj](https://arxiv.org/abs/2504.11521) · [Wang et al.](https://arxiv.org/abs/2506.08459) · [Scenario Diffusion](https://arxiv.org/abs/2311.02738) · [SceneDiffuser](https://arxiv.org/abs/2412.12129) · [SceneDiffuser++](https://openaccess.thecvf.com/content/CVPR2025/html/Tan_SceneDiffuser_City-Scale_Traffic_Simulation_via_a_Generative_World_Model_CVPR_2025_paper.html) · [SLEDGE](https://arxiv.org/abs/2403.17933) · [Nexus](https://arxiv.org/abs/2504.10485) · [MotionDiffuser](https://openaccess.thecvf.com/content/CVPR2023/html/Jiang_MotionDiffuser_Controllable_Multi-Agent_Motion_Prediction_Using_Diffusion_CVPR_2023_paper.html) · [DJINN](https://arxiv.org/abs/2309.12508) · [DiffusionDrive](https://openaccess.thecvf.com/content/CVPR2025/html/Liao_DiffusionDrive_Truncated_Diffusion_Model_for_End-to-End_Autonomous_Driving_CVPR_2025_paper.html) · [MagicDrive](https://arxiv.org/abs/2310.02601) · [Panacea](https://arxiv.org/abs/2311.16813) · [DrivingDiffusion](https://arxiv.org/abs/2310.07771) · [GAIA-2](https://arxiv.org/abs/2503.20523) · [LiDM](https://openaccess.thecvf.com/content/CVPR2024/papers/Ran_Towards_Realistic_Scene_Generation_with_LiDAR_Diffusion_Models_CVPR_2024_paper.pdf) · [Cosmos-Drive-Dreams](https://arxiv.org/abs/2506.09042) · [Challenger](https://arxiv.org/abs/2505.15880) · [PriSTI](https://arxiv.org/abs/2302.09746) · [DiffSTG](https://arxiv.org/abs/2301.13629) · [PMA-Diffusion](https://arxiv.org/abs/2512.06183) · [DiffODGen](https://arxiv.org/abs/2306.04873) · [CoDiffMob](https://arxiv.org/abs/2412.05000) · [DiffTraj](https://arxiv.org/abs/2304.11582) · [RoadFusion](https://arxiv.org/abs/2507.15346)

---

Next: world models, the last part of this module (coming soon), then the closing page
{doc}`Further reading: generative models in transportation <notes10-reading-library>`. Back to the {doc}`Module 4 map <index>`.
