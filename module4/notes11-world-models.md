(world-models)=
# 4.12 World models

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 4 &middot; Section 4.12</span>
    <span class="notes-card-session">Session: World models</span>
  </div>
  <p class="notes-card-lede">Every model so far in this module produces one sample that looks like the data. A world model produces a future that responds to what you do: give it the present state and an action, and it returns the next state, again and again. This page covers why transportation needs one, the milestone systems from 2018 to the 2026 world models that test driving software, the four parts and how they are trained, the data they need, five transportation jobs, and a what-if analysis of real ADAS takeovers. A worked example on the course torus network shows that the variety of actions in the log decides whether the model can answer a what-if question at all.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Read it before</h4>
      <ul>
      <li><a href="notes3b-vae-basics.html">4.6 Variational autoencoders (VAE)</a>, for the loss this page builds on</li>
      <li><a href="notes6-diffusion-basics.html">4.8 Diffusion models: the basics</a></li>
      <li><a href="notes8-diffusion-literature.html">4.10 Diffusion in transportation literature</a>, for generated safety scenarios</li>
      </ul>
    </div>
    <div>
      <h4>Read it after</h4>
      <ul>
      <li><a href="notes12-jepa.html">Further reading: JEPA and V-JEPA 2</a>, for world models that predict a description of the next frame instead of its pixels</li>
      <li><a href="notes10-reading-library.html">Further reading: generative models in transportation</a>, the closing page of the module</li>
      </ul>
    </div>
  </div>
</div>

## What this section covers

- Why a world model: the simulators you already build by hand, and the what-if question earlier models could not answer
- What a world model is: the key equation, how it extends the models of this module, four uses and three families
- Milestones, from Craik (1943) and Dyna (1991) to the 2026 world models that test driving software
- How one is built: encoder, dynamics, decoder and heads, and a training loss that is the VAE loss with a learned prior
- A worked example on the course torus network: two world models, one trained on a single timing plan, one on varied plans
- What data trains a world model, and why the actions in the log must vary
- Five transportation jobs: closed-loop testing, planning, simulating road users, rare scenarios, traffic operations
- What-if simulation for safety: turning a real ADAS takeover into "what if the driver had been 1 s or 2 s late?"
- Where it breaks, how it compares with the autoencoder, VAE, GAN and diffusion, a fit card, a summary and seven questions

A **world model** is a generative model of *what happens next*. You give it the present state of the world and an action, and it produces the next state. Run it again on its own output and you get a whole future. That lets you try a decision inside the model before you try it on a real road. The name sounds grander than the thing: "world" means only the slice of the world your task needs, such as one intersection, one corridor, or the next few seconds around one car.

This is the last section of Module 4. The autoencoder, the VAE, the GAN and diffusion ({doc}`4.4 <notes2c-autoencoders>` to {doc}`4.8 <notes6-diffusion-basics>`) each produce **one** sample x, such as a speed heatmap or a pair of detector speeds, that looks like the data. A world model reuses the same parts to produce a **sequence** x₁, x₂, x₃, … that responds to what you do.

Two examples show the difference:

- **Driving.** A VAE trained on dashcam frames draws one plausible frame. A world model, given the steering and pedal inputs, draws the next five seconds: the lead car brakes, the gap closes, our car slows down.
- **An intersection.** A diffusion model draws one plausible snapshot of where the vehicles are. A world model, given the signal phases, plays out how the queue on each approach grows on red and discharges on green over the next few cycles.

In both, the key difference is the same: a world model predicts the **future motion sequence**, and that sequence depends on the actions you choose.

By the end you should be able to:

1. Explain why planning, control, testing and safety analysis in transportation need a model that answers "what happens if I do *a*?"
2. Draw the four parts of a world model (encoder, dynamics, decoder, heads) and say which earlier model each part borrows from.
3. Name the milestone works, from Ha and Schmidhuber (2018) to today's driving world models, and say what each one added.
4. Say what data a world model needs, and why logged agency data usually lacks the most important ingredient: varied actions.
5. Judge when a learned world model is worth it, and when a classical simulator (SUMO, CTM, CARLA) is still the better tool.
6. Explain how a world model could turn a real ADAS takeover into what-if questions (what if the driver had responded 1 s or 2 s later, or not at all?) and what it would take to trust the answers.

### Words and symbols

| Symbol | What it is | Transportation example |
| --- | --- | --- |
| $x_t$ | the observation at time t. Same x as on the earlier pages, now with a clock | a dashcam frame; the densities on every link of a network; one lidar sweep |
| $a_t$ | the action taken at time t | steering and pedal; a signal phase; a perimeter gate open or closed |
| $z_t$ | the latent state at time t. Same idea as the autoencoder and VAE latents | a compact summary of the scene |
| $h_t$ | the memory the model carries from step to step | a pedestrian now hidden behind a bus, still remembered |
| $r_t$ | a reward, or any quantity read off the state | trips completed per minute; a near-miss flag |
| $H$ | the horizon: how many steps the model runs ahead | 5 s of driving; one hour of network operation |

Three words mean the same thing in the papers: a **rollout**, an **imagined** future, and a **dream** are all the model running forward on its own outputs, with no new data from the real world.

One more distinction runs through the whole page. A **simulator** is built from rules that people wrote (car-following, signal logic, conservation of vehicles). A **world model** is learned from data. Both answer the same question, what happens next if I do this, so the interesting choice is which one to trust for which job.

(wm-why)=
## Why a world model?

Every operating decision in transportation is a bet on the future. If I retime this signal, meter this ramp, or brake now, what happens next? Answering that takes a model that accepts an **action** and returns the **future it causes**. That is all a world model is.

### You already use world models: you build them by hand

Transportation engineering is full of models that take the present state and an action and return the next state. We just call them simulators or analysis methods.

| Model you know | State it tracks | Action it accepts | What it returns |
| --- | --- | --- | --- |
| ACC design with car-following kinematics | gap, ego speed, leader speed | ego acceleration | next gap and speeds |
| Cell transmission model (CTM) | density in every cell of a corridor | ramp-metering rate, signal green | next densities |
| HCM signalized-intersection method | arrival flow, saturation flow | cycle length, green split | delay, queue |
| SUMO or VISSIM | every vehicle's position and speed | signal plan, routing, speed limit | every vehicle's next position |
| CARLA | a full 3-D scene with sensors | steering, throttle, brake | next camera and lidar frames |

Each row is a box with the same plugs: **state in, action in, next state out**. A world model is that same box, **learned from data instead of written by hand**.

```{figure} ../_static/figures/WM_Loops.png
:alt: Two loops share one controller (ADAS or signal timing). On the left, the imagined loop: the controller sends "try an action" to a world model learned from logs and gets back an imagined result; this loop is fast, cheap and safe to fail. On the right, the real loop: the controller acts on the real road and sees what happened; this loop is slow, costly and unsafe to fail.
:width: 100%

A controller can try actions in a world model before acting on the road.
```

The controller can go around the left loop many times for each trip around the right loop. Only the action that looked best in imagination is sent to the road.

### Four pressures push us to learn the box from data

1. **The world is too rich to write rules for.** No one can write the rule that turns a dashcam frame at a busy Tampa intersection (scooters, a delivery van double-parked, rain on the lens) into the next frame. CARLA renders a cartoon of that scene, and a perception model trained on the cartoon often fails on the real thing (the *sim-to-real gap*). A model learned from real video starts from the real thing.
2. **Trial and error on real roads is unsafe and slow.** Reinforcement learning needs thousands to millions of tries. An automated vehicle cannot learn to avoid crashes by crashing, and an agency cannot test fifty timing plans on a live corridor. A world model lets the controller try its actions *in imagination* first, where a crash costs nothing.
3. **The data is huge, and the label is free.** Fleets and dashcams record millions of hours of video together with speed and steering from the vehicle's CAN bus. Nobody has to label it: the target for "predict the next second" is simply the next second. This is the same self-supervision that trained {doc}`BERT <../module2/notes5-bert>` and the masked autoencoder of {doc}`4.5 <notes2d-deep-autoencoders>`.
4. **The cases that matter are rare.** Testing an ADAS feature on the scenario where a cyclist swerves out from behind a parked truck means waiting a long time to see it on the road. A world model can be *steered* into that scenario and then rolled forward to see what the vehicle would do. {ref}`4.10 <dlit-five-ways>` showed five ways to steer a diffusion model toward a dangerous scenario; a world model does the same for a future that keeps reacting to what the vehicle does.

### The one question earlier models could not answer

The models in this module each answer a different question about traffic:

- A **VAE or diffusion model** answers: *what does a typical speed heatmap look like?*
- A **forecaster** (the transformer and graph-network forecasters of {doc}`Module 2 <../module2/index>` and {doc}`Module 3 <../module3/index>`) answers: *what will the next hour look like if things carry on as usual?*
- A **world model** answers: *what will the next hour look like if I do this?*

The last question is the one a controller, a planner or a safety tester actually has. It is a **what-if** question, and it needs the action as an input.

(wm-what)=
## What a world model is

A world model is a **learned, conditional generative model of the next state**. It takes what has happened so far plus the action you are about to take, and returns a *spread* of possible next states. Feed its output back in, step after step, and it produces a whole imagined future for any action plan you hand it.

```{figure} ../_static/figures/WM_One_Step.png
:alt: Left to right. The measured densities now (x_t) and the signal phases for the next 10 s (a_t) go into the world model, which returns the next densities as an imagined spread (x_t+1). That output and the phases for the 10 s after (a_t+1) go into the world model again, which returns x_t+2, and so on. Each imagined state goes back in as the next input; nothing new is measured.
:width: 100%

One step of a world model, chained into an imagined future. Example: the density on every link of a network, and the signal phases that will run.
```

Read it left to right: one measured state and one action go in, a spread of next states comes out, and that output becomes the next input. Swap the action boxes for a different signal plan and the whole imagined future changes.

(wm-key-equation)=
### The key equation

$$
\hat{x}_{t+1}\;\sim\; p_\theta\left(x_{t+1}\mid x_1,\ldots,x_t,\ a_1,\ldots,a_t\right)
$$

| Symbol | What it means here |
| --- | --- |
| $\hat{x}_{t+1}$ | the next state the model produces. The hat means *made by the model*, not measured |
| $\sim$ | "is drawn from": the model returns a spread of next states, not one number |
| $p_\theta$ | the world model itself; θ are its weights, learned from logged data |
| $x_1, \ldots, x_t$ | everything observed so far (detector readings, camera frames) |
| $a_1, \ldots, a_t$ | every action taken so far, including $a_t$, the one about to be taken |

**In words:** given everything we have seen and done, here is the spread of what we will see next.

Why a spread and not one answer? From the same queue under the same green, drivers turn and react differently, so the same start and the same action lead to different futures. A model that returns one answer returns the average future, and {ref}`4.7 <gan-why>` showed that an average can be a state that never happens (half a vehicle in each lane). That is why world models are built from the generative models of this module, not from plain regression.

(wm-compare)=
### What it adds to the models you already know

| Model | What it learns | Knows about time? | Takes an action? | The question it answers |
| --- | --- | --- | --- | --- |
| Autoencoder | x → z → x | no | no | how do I compress this heatmap? |
| VAE, GAN, diffusion | $p(x)$ | no | no | what does a typical heatmap look like? |
| Conditional diffusion (unCLIP, scenario generators) | $p(x \mid c)$ | partly: some generate whole trajectories, but not step by step | a condition c, but not a decision that plays out over time | what crash sketch fits this narrative? |
| Forecaster | $p(x_{t+1} \mid \text{past } x)$ | yes | no | what happens next if things carry on as usual? |
| **World model** | $p(x_{t+1} \mid \text{past } x, \text{past } a)$ | **yes** | **yes** | **what happens next if I do this?** |

Notice the last row is the earlier rows with two things added: a clock and an action. A world model is therefore **a job, not an architecture**. Any generator from this module can do the job once you train it on pairs of the form (past + action → next state). {doc}`4.7 <notes4-gan>` made the same kind of point about the GAN, which is a training method rather than a network: what matters is which part of the data is given and which part is predicted. The {ref}`milestones <wm-milestones>` below show that the landmark systems used, in turn, a VAE, a recurrent latent model, token transformers and diffusion.

(wm-uses)=
### Four ways to use one

1. **Simulate.** Roll it forward under a plan and watch: closed-loop testing of an ADAS feature, or a what-if for a new timing plan.
2. **Plan.** Try many action sequences in imagination, keep the best, take its first action, observe, and plan again. You know this as **model predictive control (MPC)**. Classical ramp-metering MPC uses the METANET traffic-flow model to predict the corridor; a world model plays METANET's role, learned from data instead of calibrated by hand.
3. **Train a policy inside it.** Let an RL controller practice thousands of episodes in imagination (the Dreamer idea, in the {ref}`milestones <wm-milestones>`). Only the finished policy is tried on the real system.
4. **Generate data.** Produce rare, labeled sequences, such as a jaywalker at dusk or a lane closure at the peak, to train and test perception and prediction models.

The planning use has a one-line objective. It is worth seeing because it shows exactly where the world model sits inside the controller:

$$
a^*_t,\ldots,a^*_{t+H-1}\;=\;\arg\max_{a_t,\ldots,a_{t+H-1}}\;\sum_{k=1}^{H}\hat{r}_{t+k}
$$

**In words:** among the action plans you try, keep the one whose *imagined* future collects the most reward: vehicles served, delay saved, distance kept from the lead vehicle. Every $\hat{r}$ comes from the model, so the plan can only be as good as the model's imagination. H is the horizon: how far ahead you look.

### Three families of world models

| Family | What it predicts | Has a decoder? | Examples (see the milestones) | Strength | Weakness |
| --- | --- | --- | --- | --- | --- |
| Observation space ("video") | compressed tokens of the next camera frames, lidar sweeps or maps, always decoded to pixels or points | yes, to pixels or points | GAIA-1 and GAIA-2, Genie, Cosmos | you can watch it and audit it by eye | expensive; spends effort on pixels that do not matter, such as cloud shapes |
| Latent space, for control | the next latent state; decodes only when you want to look | yes, but planning can skip it | World Models (2018), PlaNet, Dreamer, MILE | cheap enough to imagine thousands of futures | the latent is not a physical quantity you can read |
| Prediction without pictures | an embedding, or only reward and value | no | MuZero, V-JEPA 2 | no effort wasted on irrelevant detail | cannot be checked by looking at it |

The last row is opened up in {doc}`Further reading: JEPA and V-JEPA 2 <notes12-jepa>`, after this page.

### Words that sound alike

- A **digital twin** is a replica of one specific system (this corridor, this bridge) kept in sync with live data. A world model can be the engine inside a twin; the twin is the whole system around it: data feeds, calibration, dashboards.
- "**An LLM has a world model**" is loose talk about the knowledge inside a language model. It is not this page's meaning.
- A **3-D scene generator** builds an explorable scene. Unless it also takes actions and predicts how the scene changes, it is a scene generator, not a world model in this sense.

(wm-milestones)=
## Milestones: from a model in the head to world models that test cars

The idea is more than 80 years old. What changed after 2018 is that the generative models of this module made the inner model **learnable from raw sensor data**. Since 2023, driving companies have turned those models into test tracks for automated driving.

```{figure} ../_static/figures/WM_Eras.png
:alt: Four eras, left to right, years not drawn to scale. Era 1, the idea of an inner model, 1943 to 1991: Craik 1943, Dyna 1991; what it added, practise on a model, not on the world. Era 2, latent models for control, 2018 to 2025: World Models 2018, PlaNet 2019, Dreamer 1 to 3 2020 to 2025, MuZero 2020, MILE (driving) 2022, Dreamer 4 2025; learn it from pixels, decide inside it. Era 3, generative video models, 2023 to 2025: GAIA-1 2023, Sora 2024, Genie 2024, DIAMOND 2024, GAIA-2 2025, Cosmos 2025, V-JEPA 2 2025, Genie 3 2025; real video at scale, looks right is not is right. Era 4, test tracks for driving, late 2025 to 2026: GAIA-3 2025, Waymo model 2026, Cosmos 3 2026, GAIA-4 2026, Genie 4 2026; test driving software before it meets a road.
:width: 100%

World models moved from training game agents to testing cars. Years are when each work appeared.
```

The bottom line of each band is what that era added. The tables below give each work's parts, data and result.

### Era 1: the idea (1943–1991)

The psychologist Kenneth Craik put the whole field in one sentence in 1943 ([*The Nature of Explanation*, ch. 5](https://cpcontacts.markhuckvale.com/research/hp/Craik_NOE_Chapter_5.pdf)):

> "If the organism carries a 'small-scale model' of external reality and of its own possible actions within its head, it is able to try out various alternatives, conclude which is the best of them, react to future situations before they arise …"

Richard Sutton's **Dyna** ([1991](https://doi.org/10.1145/122344.122377)) made it an algorithm. The agent learns a lookup table of (state, action) → (reward, next state) from experience, then practices on transitions replayed from that table. In the textbook maze example (Sutton and Barto, 2nd ed., Example 8.1), the agent with no planning needed about 25 episodes to learn the maze; with 5 imagined steps per real step it needed about 5, and with 50 only 3. **Imagined experience can stand in for real experience**, if the model is right.

### Era 2: learned latent models for control (2018–2025)

| Work | What it sees (x) and does (a) | Parts | Trained on | What it showed |
| --- | --- | --- | --- | --- |
| [World Models](https://arxiv.org/abs/1803.10122), Ha and Schmidhuber, 2018 | 64×64 game frames; steering, gas, brake | **VAE** (frame → 32 latents) + recurrent network that predicts the next latent + a linear controller with 867 weights | 10,000 rollouts of random play | CarRacing score 906 ± 21 (best earlier: 838). A Doom agent trained *only inside the dream* worked in the real game |
| [PlaNet](https://arxiv.org/abs/1811.04551), Hafner et al., 2019 | 64×64 frames; joint torques | Encoder + **RSSM** (a recurrent memory plus a random latent) + decoder + reward head; plans by trying 1,000 action sequences 12 steps ahead | 6 simulated control tasks | Matched strong model-free agents with about 200× less interaction |
| [Dreamer](https://arxiv.org/abs/1912.01603) (2020), [V2](https://arxiv.org/abs/2010.02193) (2021), [V3](https://arxiv.org/abs/2301.04104) (Nature 2025) | frames; game or robot actions | RSSM + an actor and a critic trained **only on imagined rollouts** | 20 control tasks; 55 Atari games; 150+ tasks | V2: first agent at human level on Atari learning inside a world model. V3: one fixed setting across all domains; first to collect Minecraft diamonds from scratch |
| [MuZero](https://arxiv.org/abs/1911.08265), Schrittwieser et al., 2020 | board or game frames; moves | Encoder + dynamics that predicts **only reward, value and policy** (never the frame) + tree search | self-play | Matched AlphaZero in Go, chess and shogi "without any knowledge of the game rules" |
| [MILE](https://arxiv.org/abs/2210.07729), Hu et al. (Wayve), 2022 | car cameras lifted to a bird's-eye view; acceleration and steering | RSSM-style world model + bird's-eye-view decoder + driving policy, trained together | 32 hours of expert driving in CARLA | In an unseen town and weather, driving score 61.1 vs 46.5 for the best prior method (31% higher) |
| [Dreamer 4](https://arxiv.org/abs/2509.24527), Hafner et al., 2025 | Minecraft video; keyboard and mouse | tokenizer + dynamics transformer, 2B parameters together, real time on one GPU | 2,541 hours of recorded play, **no new interaction** | First agent to reach Minecraft diamonds purely from offline data (0.7% of episodes) |

**What this era established:** a small latent model is enough to *decide* well, even when its decoded pictures are blurry. MILE carried the recipe into driving.

### Era 3: generative video world models (2023–2025)

| Work | What it sees (x) and does (a) | Parts | Trained on | What it showed |
| --- | --- | --- | --- | --- |
| [GAIA-1](https://arxiv.org/abs/2309.17080), Wayve, 2023 | one front camera; speed and curvature, plus text | Image **tokenizer** (576 tokens a frame) + 6.5B next-token **transformer** + **video diffusion decoder** (about 9.4B parameters in total) | 4,700 hours of London driving, 2019–2023 | Driving video can be modelled like language: loss fell along a scaling law, as for LLMs |
| [Sora report](https://openai.com/index/video-generation-models-as-world-simulators/), OpenAI, 2024 | video; **no action input** | Video compressor + **diffusion transformer** over space-time patches | not disclosed | Up to a minute of video; the report itself shows wrong physics, such as glass that does not shatter properly |
| [Genie](https://arxiv.org/abs/2402.15391), Google DeepMind, 2024 | platform-game video; **8 actions it invented itself** | VQ-VAE video tokenizer + *latent action model* + masked transformer; about 11B | 30,000 hours of internet gameplay with **no action labels** | Actions can be learned from video that never recorded them |
| [GameNGen](https://arxiv.org/abs/2408.14837) and [DIAMOND](https://arxiv.org/abs/2405.12399), 2024 | game frames; key presses | **Diffusion** model that draws the next frame from past frames and the action | DOOM played by an RL agent; Atari; 87 hours of CS:GO | DOOM playable at 20 frames a second; DIAMOND best agent trained entirely inside a world model on Atari 100k |
| [GAIA-2](https://arxiv.org/abs/2503.20523), Wayve, 2025 | up to 5 surround cameras; ego speed and curvature, other agents' 3-D boxes, weather, time of day, road layout | Video tokenizer + 8.4B transformer trained with **flow matching** (a cousin of diffusion) | about 25 million 2-second clips from the UK, US and Germany | Controllable surround video, including rare and safety-critical scenes |
| [Cosmos](https://arxiv.org/abs/2501.03575), NVIDIA, 2025 | video, text; camera and robot actions | Open "world foundation models": tokenizers + **diffusion** and **autoregressive** families (4B–14B) | 100 million clips cut from 20 million hours of video; a driving version on about 20,000 hours of 6-camera clips | A public base model that others fine-tune for their own robot or vehicle |
| [V-JEPA 2](https://arxiv.org/abs/2506.09985), Meta, 2025 | video; robot-arm actions | Encoder + predictor working **in embedding space only**, no pixels | over 1 million hours of internet video + under 62 hours of robot video | Planned pick-and-place zero-shot in new labs (80% success for a cup vs 15% for a baseline) |
| [Genie 3](https://deepmind.google/discover/blog/genie-3-a-new-frontier-for-world-models/), Google DeepMind, 2025 | text prompt; navigation actions | not disclosed | not disclosed | Interactive worlds at 720p, 24 frames a second, consistent for a few minutes (company blog) |

**What this era established:** the generators of this module (VAE-style tokenizers, transformers, diffusion) scale to world models of real video. It also showed the catch: a video that *looks* right can still break physics.

### Era 4: world models as the test track for automated driving (late 2025–2026)

The newest systems are aimed squarely at **validating driving software**. Most are announced in company blogs without papers, so read their numbers as claims, not as measured results.

| Work | What is new | Source |
| --- | --- | --- |
| GAIA-3, Wayve, Dec 2025 | 15B-parameter latent diffusion world model; aimed at evaluation: safety-critical counterfactuals and NCAP-style tests | [company blog](https://wayve.ai/thinking/gaia-3/) |
| Waymo World Model, Feb 2026 | Built on Genie 3; generates **camera and lidar**; controlled by driving actions, scene layout and language; shows scenes almost impossible to capture at scale (a tornado, driving out of a raging fire) | [company blog](https://waymo.com/blog/2026/02/the-waymo-world-model-a-new-frontier-for-autonomous-driving-simulation) |
| GAIA-4, Wayve, Aug 2026 | **Closed loop**: the driving software's choices change what its sensors see next (other road users replay their logged paths unless reactive agents are switched on); generates radar as well as camera | [company blog](https://wayve.ai/thinking/gaia-4/) |
| Cosmos 3 (mid-2026), Genie 4 (Oct 2026) | General-purpose world models that also output sound and accept language steering | [NVIDIA](https://blogs.nvidia.com/blog/cosmos-3-physical-ai-open-world-foundation-model/), [Google DeepMind](https://deepmind.google/blog/genie-4-a-new-generation-of-world-simulation/) |

**What to take from the whole history:**

1. The structure has barely changed since 2018: **compress the observation, predict the next compressed state from the action, decode if you need to look.** Only the parts got bigger.
2. Each part came from a model you have met: the VAE (World Models), the recurrent network and the transformer (Dreamer, GAIA-1), the VQ tokenizer (Genie), and diffusion (DIAMOND, GAIA-2 and later).
3. The use moved from *training a controller* (games and robots) to *testing a controller* (driving). For transportation, the second use is the one that matters most today.

(wm-built)=
## How a world model is built

Most of the milestone systems share the same four parts (MuZero and V-JEPA 2 leave out the decoder). An **encoder** compresses what the sensors see. A **dynamics model** steps the compressed state forward, given an action. A **decoder** turns a compressed state back into something you can look at. **Heads** read off the quantities you care about: vehicles served, a collision, a lane departure. Each part is a model you have already met.

```{figure} ../_static/figures/WM_Four_Parts.png
:alt: One step of the torus example in three columns. 1, encode now: link counts now (x_t) go through the encoder (compress) to the latent now (z_t). 2, step forward: the latent, the signal phases for the next block (a_t) and the memory so far (h_t) go into the dynamics, a recurrent cell, which outputs the next memory h_t+1. 3, predict and decode: the prior turns h_t+1 into a guess of z_t+1, which feeds the decoder (next link counts) and the reward head (vehicles served). A dashed box, used only while training, shows the real x_t+1 going through the encoder to the posterior z_t+1, tied to the prior by a KL term.
:width: 100%

Four parts: encode the present, step it forward, decode what you need. One step of the torus example below; the dashed box is used only while training.
```

When the model imagines, only the solid path runs: the prior's guess of the next latent goes straight to the decoder and the head. The dashed box needs the real next observation, so it can only run on logged data.

| Part | What it does | Borrowed from | In the torus example below | In GAIA-2 |
| --- | --- | --- | --- | --- |
| Encoder | compresses one observation into features | the autoencoder and VAE encoder; the VQ tokenizer | 168 link counts → 256 features | a video tokenizer that shrinks video 32× in space and 8× in time |
| Dynamics | steps the state forward: (memory, latent, action) → next memory and next latent | the recurrent network (Dreamer), the transformer (GAIA, Genie), diffusion (DIAMOND, GAIA-2) | a recurrent cell with 200 memory numbers + 32 random latents | an 8.4B transformer trained with flow matching |
| Decoder | turns the state back into an observation | the VAE decoder; a diffusion decoder (GAIA-1) | 168 links × 8 possible counts (0–7; only 0–6 occur) | the tokenizer's decoder, back to 5 camera videos |
| Heads | read a quantity of interest off the state | the backbone-and-head idea from {doc}`Module 1 <../module1/index>` | vehicles that crossed an intersection | (none published; driving versions add collision and progress scores) |

### Two parts per step: a memory and a surprise

The dynamics model in Dreamer-style world models carries two things from step to step:

- **$h_t$, the memory.** A deterministic summary of everything so far: how long each approach has been red, where the queues are building. It is updated by a recurrent cell.
- **$z_t$, the random latent.** The part of the next state that could not be predicted: which way the drivers at the head of each queue happen to turn. It is drawn from a distribution, so two imagined futures from the same start can branch apart, just as two real days do.

This split is the RSSM of PlaNet. The memory keeps long rollouts stable; the random part keeps them honest about uncertainty.

(wm-loss)=
### The key equation: how it is trained

$$
\begin{aligned}
\mathcal{L}(\theta)=\sum_t\Big[\;&\underbrace{-\ln p_\theta(x_t\mid h_t,z_t)}_{\text{reconstruct what you saw}}\;\;\underbrace{-\ln p_\theta(r_t\mid h_t,z_t)}_{\text{predict the reward}}\\[4pt]
&+\;\underbrace{\mathrm{KL}\big(q_\theta(z_t\mid h_t,x_t)\,\Vert\,p_\theta(z_t\mid h_t)\big)}_{\text{guess after looking}\;\approx\;\text{guess before looking}}\;\Big]
\end{aligned}
$$

| Symbol | What it means here |
| --- | --- |
| $x_t$, $r_t$ | the logged observation and reward at step t (link counts; vehicles that crossed) |
| $h_t$ | the memory, built from all earlier latents and actions |
| $z_t$ | the random latent at step t |
| $q_\theta(z_t \mid h_t, x_t)$ | the **posterior**: the latent the model infers *after* seeing $x_t$ (the encoder's job) |
| $p_\theta(z_t \mid h_t)$ | the **prior**: the latent the model predicts *before* seeing $x_t$, from memory and action alone (the dynamics' job) |
| $\mathrm{KL}(q \,\Vert\, p)$ | how far apart the two guesses are, in nats |

**In words:** reconstruct what you saw, predict the reward, and make your *before-looking* guess about each step match your *after-looking* guess.

This is the VAE loss of {ref}`4.6 <vae-basics-loss>` with one change. There, the KL term pulled the encoder's latent toward a fixed bell curve N(0, I). Here it pulls toward the model's *own prediction* of that latent. The prior **is** the dynamics model, so shrinking the KL term is the same thing as learning to predict the future in latent space.

(wm-modes)=
### Two modes: observing and imagining

|  | Training (observing a log) | Imagining (a rollout) |
| --- | --- | --- |
| What comes in each step | the real $x_t$ and the logged $a_t$ | only the planned $a_t$ |
| Where $z_t$ comes from | the posterior q (it has seen $x_t$) | the prior p (nothing has been seen) |
| What you use the outputs for | the three loss terms | the imagined $\hat{x}$ and $\hat{r}$ |

A typical use runs both: **observe** a few real steps so the memory locks onto the current state, then **imagine** forward under each candidate plan.

:::{admonition} Going deeper &mdash; why the prior, why weight the KL, why a separate memory
:class: dropdown

*Why imagine with the prior?* During a rollout there is no $x_{t+1}$ to encode, so the posterior cannot be computed; the prior is the only thing left. Training must therefore make the prior good, which is the KL term's job.

*Why weight the KL term?* If every nat of information stored in z costs a full nat of KL, the model may store nothing and fall back on the average. Practice lowers the price: DreamerV3 weights the two directions of the KL by 1 and 0.1 (an earlier preprint used 0.5 and 0.1) and stops penalizing the KL once it falls below 1 nat ("free bits"). The torus example below uses an overall KL weight of 0.3, split 0.8/0.2 between the two directions, with the same 1-nat floor.

*Why a separate deterministic h?* A purely random state forgets; PlaNet found that a deterministic path is needed to remember over many steps.

Source: Hafner et al., PlaNet (2019) and DreamerV3 (2023/2025).
:::

(wm-torus)=
### Worked example: a world model of the course torus network

**The question.** Can a world model learned from logs tell an operator which signal plan to run, without ever running the plan? And what happens if the logs come from a single timing plan?

**The system** (synthetic: the course torus simulator, `traffic_sim/torus_sim.py`). 42 signalized intersections on a 6 × 7 grid that wraps around, 168 one-lane links of 6 cells. Vehicles move by Rule 184 and turn at random; none enter or leave. One world-model step is one signal block of 10 simulator steps.

- **x:** vehicles on each of the 168 links (0–6: six cells plus a one-vehicle entrance buffer that can fill only when the first cell is empty)
- **a:** the phase at each of the 42 intersections for the block (east–west or north–south green)
- **r:** vehicles that crossed an intersection during the block

**Two logs of the same size.** Each has 500 runs of 40 blocks (20,000 block-to-block transitions) at loads from 0.25 to 0.65 vehicles per cell. Only the signals differ.

| Log | What the signals did | Transportation analogy |
| --- | --- | --- |
| A, one timing plan | every intersection alternates EW and NS green every block (1:1) | an agency log under the same plan every day |
| B, varied plans | each run uses one plan for 10 blocks, then another for 30. EW and NS blocks each 1–3; offsets none, checkerboard or random; 10% of intersection-blocks flipped at random | a log with deliberate exploration |

**The model.** The four-part model in the diagram above, with 1.08 million weights. One copy was trained on each log for 8,000 updates (10–11 minutes on two laptop-class CPU cores). The two copies are identical except for the log they saw.

**The test.** 12 new start states at load 0.45. Each model observes 10 blocks of the alternating plan, then imagines the next 20 blocks under each of 11 plans (4 dreams per start). The simulator runs the same plans from the same states twice, with new random turns.

#### Result 1: after a plan switch

```{figure} ../_static/figures/WM_Switch_Rollout.png
:alt: Two panels against signal block, from minus 10 to 20, one start state at load 0.45. Blocks minus 10 to 0 run the alternating 1:1 plan and are observed by the models; from block 1 the plan is EW green for 3 blocks, NS green for 1. Left, share of vehicles on north-south links: the real runs and model B's dreams climb in a saw-tooth to about 0.95 after each run of three EW greens and drop on each NS green; model A's dreams hover between about 0.6 and 0.75. Right, vehicles crossing per simulator step: real and model B collapse from about 30 to about 3 to 5 in each cycle; model A stays between about 25 and 30.
:width: 100%

Real and imagined share of vehicles on north&ndash;south links (left) and network throughput (right) after switching to EW 3:1. Real: 8 simulator runs; models: 8 dreams each.
```

From one start state (8 simulator runs and 8 dreams per model): under EW 3:1, the north–south links fill during each run of three EW greens until about 96% of all vehicles sit on them. Throughput then collapses from about 30 to about 5 vehicles per step: turning vehicles cannot enter the full north–south links (spillback), until the NS green releases them. **Model B**, which saw uneven splits in its log, imagines the same saw-tooth: its dreams peak at about 94%, and it predicts 18.3 vehicles per step against 17.9 real. **Model A** never saw two EW greens in a row. Its dreams hover near 67% and it predicts 27.6 vehicles per step, 54% too high.

```{figure} ../_static/figures/WM_Network_Maps.png
:alt: Three maps of the 6 by 7 torus at block 19, after three east-west greens in a row, links colored by vehicles on the link from 0 to 6. Real simulator (one run): north-south links mostly full, east-west links mostly empty. World model B (mean of 8 dreams): the same pattern, north-south links full and east-west links nearly empty. World model A (mean of 8 dreams): vehicles spread over both directions, with east-west links half full.
:width: 100%

Network maps at block 19, after three east&ndash;west greens in a row: the real simulator, model B and model A.
```

The maps show the same thing link by link. B's imagined network has full north–south links and nearly empty east–west ones, as the real one does. A spreads the vehicles out as if the plan had never changed.

#### Result 2: ranking eleven plans

```{figure} ../_static/figures/WM_Plan_Ranking.png
:alt: Network throughput in vehicles crossing per simulator step for 11 signal plans, from 12 new start states at load 0.45. Real simulator from best to worst: 29.6 for alternate 1:1, 28.8 for checkerboard 1:1, 25.6 for 2:2, 22.7 for EW 2:1, 21.3 for random phases, 20.7 for 3:3, 18.2 for EW 3:1 and NS 1:3, 16.0 for 4:4, 14.9 for EW 4:1 and 3.1 for EW only. Model B, trained on varied plans, sits close to the real value on every plan except EW only, where it predicts 6.1. Model A, trained on one plan, predicts between 25.7 and 29.5 for every plan. Random phases, 4:4, EW 4:1 and EW only are shaded as plans never run in either log.
:width: 100%

Network throughput by signal plan: the real simulator, model B and model A. Shaded rows are plans never run in either log.
```

- **Model B ordered all 11 plans as the simulator did.** (EW 3:1 and NS 1:3 are tied in the simulator, so the order of that one pair is luck.) On the 7 plan types its log actually ran, its average error was 0.5 vehicles per step (about 2% of throughput); on the 4 it never ran, including random phases, 1.2.
- **Model A put every plan between 25.7 and 29.5 vehicles per step**, while the real range was 3.1 to 29.6. It got its own plan right (29.55 vs 29.58) and little else: its average error was 4.5 on the plan types in log B and 13.0 on the absent ones. Asked what switching from 1:1 to 3:3 would cost, A answers 2.9 vehicles per step (10%); the simulator says 8.9 (30%).
- **Even B has a limit.** EW 4:1 and 4:4 never appear as plans in its log, yet it predicted them well. The log was not silent on them: random flips and plan switches left single intersections on one phase for 4 or more blocks 13% of the time. For *EW only* (the whole network held on one phase for 20 blocks, which never happens in its log) it predicted 6.1 vehicles per step against 3.1 real: twice the truth.

**Speed.** Imagining all 44 futures (11 plans × 4 dreams, 20 blocks each) took 0.6 s. The pure-Python simulator needs about 13 s for the same 44 runs, so the model is about 20× faster here; a compiled simulator would narrow that gap.

:::{admonition} Before you trust this result
:class: warning

**What is the baseline?** The simulator itself is the ground truth, and {ref}`Where it breaks <wm-breaks>` adds a persistence forecast ("nothing changes").

**How was the data split, and why is that honest?** The test uses start states and random turns the models never saw. The four plan types absent from both logs (random phases, 4:4, EW 4:1 and EW only) test extrapolation.

**What does it do on the ugly cases?** "EW only" puts B off by a factor of two. Long horizons are worse ({ref}`Where it breaks <wm-breaks>`). Other loads and other network sizes were not tested. Every number here comes from a simulator, not real traffic.
:::

**The lesson is requirement 3 of {ref}`the data section <wm-data-needs>`, measured.** Same architecture, same amount of data, same training: only the variety of the actions in the log differs, and that alone decides whether the model can answer a what-if question.

(wm-data)=
## What data trains a world model

A world model learns from **sequences of observations and actions, logged at a steady rate, in which the actions actually vary**. The first two conditions are routine engineering. The third is where most transportation data falls short.

### One training example is a tape, not a picture

The VAE and diffusion pages ({doc}`4.6 <notes3b-vae-basics>`, {doc}`4.8 <notes6-diffusion-basics>`) trained on single samples x. A world model trains on a tape:

$$
x_1,\ a_1,\ x_2,\ a_2,\ x_3,\ a_3,\ \ldots,\ x_T
$$

plus, if you want a head, the quantity you care about at each step ($r_1, r_2, \ldots$).

Nobody labels it. The target for each step is simply the next observation on the tape. That is why world models can use thousands of hours of fleet video that no one will ever annotate.

(wm-data-needs)=
### Five things the tape needs

| Requirement | Why it matters | What goes wrong without it | Transportation example |
| --- | --- | --- | --- |
| 1. A fixed time step, with observation and action aligned | the model learns "this action, then that change" | the action appears to cause a change that happened before it | CAN bus at 100 Hz, camera at 10–30 Hz, signal events at 0.1 s: resample all to one clock |
| 2. The action is recorded | no action column, no what-if question | you get a forecaster, not a world model | ego speed and steering from CAN; phase changes from high-resolution signal-controller event logs (the data behind ATSPM dashboards) |
| 3. **The actions vary** | the model can only learn the effect of actions it has seen | it answers every what-if as if you had kept doing what the log did | an agency log where every weekday ran the same time-of-day timing plan |
| 4. Enough volume and variety of scenes | the dynamics differ by site, weather, demand | it works on the training corridor and fails one exit away | from 33 hours (comma2k19) to about 20,000 hours (Cosmos's driving set) of driving |
| 5. The rare events you care about | a model cannot produce what it has (almost) never seen | rare scenes come out blurred toward ordinary ones | crashes, near-misses, wrong-way drivers, flooding |

Requirement 3 deserves a transportation translation. Estimating how drivers respond to a toll from a year in which the toll never changed is impossible, and every economist knows it. A world model trained on logs from one timing plan faces exactly the same problem. The {ref}`worked example <wm-torus>` measures it.

### Public driving datasets that fit the tape format

| Dataset | What x is | What a is | Size | Note |
| --- | --- | --- | --- | --- |
| [comma2k19](https://arxiv.org/abs/1812.05752) | front camera, GNSS | steering and speed from the CAN bus | over 33 h of commuting on I-280, California | small, but the actions are real driver inputs |
| [nuScenes](https://arxiv.org/abs/1903.11027) | 6 cameras, lidar, 5 radars | ego pose (speed, yaw) | 1,000 scenes × 20 s (about 5.6 h) | the most used benchmark for driving world models |
| [nuPlan](https://arxiv.org/abs/2106.11810) | cameras, lidar, tracked agents | ego trajectory | about 1,300–1,500 h from 4 cities | built for planning; NAVSIM is a 2 Hz subset |
| [Waymo Open Motion](https://arxiv.org/abs/2104.10133) | tracks of every agent + map | every agent's motion | over 100,000 scenes of 20 s, 6 US cities | the base of the Waymo Sim Agents challenge |
| [Argoverse 2](https://www.argoverse.org/av2.html) | tracks + map (motion set) | every agent's motion | 250,000 scenarios of 11 s (763 h), 6 US cities |  |
| [OpenDV-YouTube](https://arxiv.org/abs/2403.09630) | front-camera video | **none** (text commands added later) | 1,747 h from over 240 cities | large and varied, but no action column |
| [CARLA](https://arxiv.org/abs/1711.03938) | any simulated sensor | any action, including unsafe ones | unlimited | cartoon visuals: the sim-to-real gap |

The pattern is clear: **the largest video collections have no action column, and logged-action datasets top out around a thousand hours.** The field's answer is to pre-train on the big action-free video, then fine-tune action conditioning on the small logged set. Vista did this, taking action labels only from nuScenes. Genie went further and invented its own latent actions from unlabeled gameplay.

### Traffic-operations data

For network operations the tape looks like this:

- **x:** detector volumes and occupancies (PeMS-style, 30 s to 5 min), probe speeds, queue lengths from video.
- **a:** signal timing, ramp-metering rates, variable speed limits, lane closures, incident-response actions.

The observations are plentiful. The weak spot is requirement 3: the actions barely vary, and when they do (a peak-hour plan), they change at the same moment the demand changes. The model cannot tell the plan's effect from the rush hour's.

### How to get action variety

1. **Vary the actions on purpose.** Alternate timing plans across comparable days; small, safe perturbations of a ramp-metering rate. RL calls this *exploration*; agencies would call it a before-after study done carefully.
2. **Pool sites that run different plans**, but the sites also differ in geometry and demand, so check what the model is really learning.
3. **Add simulation for the actions you cannot try** (SUMO, CARLA, the course torus), and remember the model will then copy the simulator's habits along with its physics.
4. **Collect rare events where they concentrate:** near-miss hot spots from roadside video, fleet dashcams triggered by hard braking.

(wm-applications)=
## World models in transportation

World models do five jobs in transportation today. **Testing driving software** and **planning inside the vehicle** are the most mature. **Traffic operations** is the youngest and the most open for research, and the one closest to this program. The leverage-label column uses the course's six labels ({doc}`5.1 <../module5/notes1-workflow>`): extraction, classification, generation, retrieval, prediction, judgment.

| Job | What x is | What a is | Leverage label | Maturity | Classical method it competes with |
| --- | --- | --- | --- | --- | --- |
| {ref}`Closed-loop testing of AV/ADAS <wm-app-testing>` | camera, lidar, radar | the driving software's own commands | generation, judgment | industry use since 2025 | log replay, CARLA, test-track scenarios |
| {ref}`Planning inside the vehicle <wm-app-planning>` | bird's-eye features or camera | candidate trajectories | prediction, judgment | research, many papers | optimization planners with constant-velocity or IDM prediction |
| {ref}`Simulating other road users <wm-app-agents>` | tracks of every agent + map | each agent's next move | generation, prediction | benchmarked (Waymo challenge) | rule-based driver models in SUMO or VISSIM (Krauss, Wiedemann, IDM) |
| {ref}`Rare and safety-critical scenarios <wm-app-rare>` | scenes and trajectories | a hazard to inject | generation | research and industry | crash reconstruction; surrogate measures with EVT |
| {ref}`Traffic operations <wm-app-operations>` | detector or image states of an intersection or network | phases, metering rates | prediction, judgment | early research | SUMO, CTM or METANET with MPC; Webster; max-pressure |

(wm-app-testing)=
### Closed-loop testing of automated driving

**The problem.** Replaying a recorded drive tests the software *open loop*: the car in the log does what the human did, whatever the software decides, and the other vehicles never react. A test is only meaningful if the software's choices change what happens next.

**How a world model helps.** Start from a real log, let the driving software act, and let the world model generate what the sensors would see after that action, including futures that never happened.

**What has been done.**

- [DriveArena](https://arxiv.org/abs/2408.00415) (ICCV 2025) put a traffic manager and an image generator around a camera-based driving model. UniAD scored 0.91 (PDM score) on logged nuScenes clips. Driving DriveArena's own routes in closed loop, it covered on average only 13.7% of each route before failing (4 routes, preliminary). Part of the drop comes from the new routes themselves: open loop on those scenes it already scored 0.64. Still, the gap shows why closed-loop testing matters.
- [GAIA-2](https://arxiv.org/abs/2503.20523) creates two kinds of hazard: *ego-induced* ones by feeding an unsafe action (steering toward oncoming traffic) and *other-agent* ones by placing 3-D boxes where a vehicle should cut in.
- [UniSim](https://arxiv.org/abs/2308.01898) (Waabi, CVPR 2023) rebuilds a recorded scene so actors can be added, removed or moved. A detector trained only on its renders scored 41.4 mAP, against 40.9 when trained on real data.
- In 2026 the [Waymo World Model](https://waymo.com/blog/2026/02/the-waymo-world-model-a-new-frontier-for-autonomous-driving-simulation) (camera and lidar) and Wayve's [GAIA-4](https://wayve.ai/thinking/gaia-4/) (camera and radar, with the driving software in the loop) became the companies' simulation engines. Neither has a paper yet.

**The catch.** A test can only find failures the world model can render. A video that looks right can still be physically wrong: a braking distance too short, a pedestrian who vanishes behind a bus and never reappears.

(wm-app-planning)=
### Planning inside the vehicle

**The problem.** A planner must choose a trajectory for the next few seconds. Classical planners predict the other road users with simple physics (constant velocity, IDM) and then optimize.

**How a world model helps.** It plays the prediction model in a model-predictive loop, exactly as in {ref}`the planning equation <wm-uses>`: imagine the future of each candidate trajectory, score it, keep the best.

**What has been done.**

- [Drive-WM](https://arxiv.org/abs/2311.17918) (CVPR 2024) imagines the 6-camera video for each candidate maneuver, runs a detector and a map model on the imagined video, and picks the safest. On nuScenes, choosing by imagination gave an average error of 0.80 m and a collision rate of 0.26%, against 1.02 m and 0.93% for a random choice (with the true driving command: 0.72 m and 0.22%).
- [Think2Drive](https://arxiv.org/abs/2402.16720) (ECCV 2024) trained a policy inside a DreamerV3-style world model and reported a driving score of 56.8 and 98.6% route completion on CARLA Leaderboard v2 test routes, against 0.7 and 1.0% for a model-free agent. Caveat: it was given perfect bird's-eye maps, not camera images.
- [LAW](https://arxiv.org/abs/2406.08481) (ICLR 2025) used next-frame prediction only as a training signal for an end-to-end planner; on nuScenes it cut the error from 0.71 m to 0.61 m and the collision rate from 0.41% to 0.30%.
- [MILE](https://arxiv.org/abs/2210.07729) ({ref}`milestones <wm-milestones>`) learned the world model and the driving policy together from 32 hours of expert driving in CARLA.

**The catch.** Most of these numbers are *open loop*: they compare a plan with what the human did in the log. And expert logs never show what happens after a bad action, so the model may not know ({ref}`requirement 3 <wm-data-needs>` again).

(wm-app-agents)=
### Simulating the other road users

**The problem.** The vehicles in SUMO and VISSIM follow hand-written car-following and lane-change rules (Krauss in SUMO, Wiedemann in VISSIM; IDM and MOBIL in many research codes). They are predictable and polite, and a learning agent finds their weak spots. In [Waymax](https://arxiv.org/abs/2310.08710), an RL agent trained against IDM vehicles collided almost four times as often (25% vs 6.5% of episodes) when tested against replays of the real logged drivers.

**How a world model helps.** Learn how *all* the agents in a scene move together, from real trajectories, and roll them forward around the vehicle under test.

**What has been done.**

- [TrafficSim](https://arxiv.org/abs/2101.06557) (Uber, CVPR 2021): 0.50% of actors in a collision over 12-second scenarios, against 1.19% for IDM, though it broke traffic rules more often than IDM did.
- The [Waymo Open Sim Agents Challenge](https://arxiv.org/abs/2305.12032) made this a benchmark. Given 1.1 s of history, a model must roll out up to 128 agents for 8 s, 32 times per scene. It is scored on how likely the real log is under the simulated spread of speeds, accelerations, gaps, collisions, time-to-collision and off-road events.
- [SMART](https://arxiv.org/abs/2405.15677) (NeurIPS 2024) treats each agent's next move as a token, like a word in a sentence. Trained only on nuPlan, it still scored 0.7210 on Waymo data it had never seen (0.7614 when trained on Waymo).
- [SceneDiffuser++](https://arxiv.org/abs/2506.21976) (Waymo, CVPR 2025) uses diffusion to simulate whole trips of 60 s, including agents entering and leaving and the signal states. It is much closer to real data than IDM overall, but its collision term is *worse* than IDM's.

**The catch.** Errors compound over long rollouts, and realistic *average* behavior is not the same as realistic behavior in the rare conflicts that matter for safety. Scores from different versions of the challenge metric cannot be compared.

(wm-app-rare)=
### Rare and safety-critical scenarios

**The problem.** The scenarios that matter for safety are the ones you rarely record. {ref}`4.10 <dlit-safety>` showed diffusion models that generate dangerous driving scenarios, and {ref}`4.9 <unclip-crash-run>` drafted crash sketches from narratives. A world model adds reaction, step by step: what happens next, and what the automated vehicle would have done.

**What has been done.**

- [STRIVE](https://arxiv.org/abs/2112.05077) (CVPR 2022) searched the latent space of a learned traffic model for accident-prone variations of real scenes. A rule-based planner collided in 27.4% of the generated scenes, against 1.2% of ordinary ones.
- [Challenger](https://arxiv.org/abs/2505.15880) (2025) generated adversarial trajectories, checked them with a vehicle-dynamics model, and rendered them as video. UniAD's collision rate rose from 0.32% to 3.95%.
- [DriveDreamer-2](https://arxiv.org/abs/2403.06845) turns a sentence ("a vehicle abruptly cuts in") into agent trajectories and then into multi-camera video.
- [Cosmos-Drive-Dreams](https://arxiv.org/abs/2506.09042) (NVIDIA, 2025) generated rain and fog versions of driving clips; a 3-D lane detector trained with them improved its F1 score by 10.4% in rain and 9.4% in fog.

**The catch.** The warning of {ref}`4.6 <vae-basics-breaks>` applies in full: a model trained on ordinary driving produces rare events only as well as its data covers them. A generated near-miss is a hypothesis, not evidence. It counts only after it improves a result on held-out real data.

(wm-app-operations)=
### Traffic operations: signals, ramps and networks

**The problem.** Agencies choose timing plans, metering rates and speed limits with calibrated simulators (SUMO, VISSIM) or macroscopic models (CTM, METANET). Calibration is slow, and RL controllers need far more simulated trials than anyone can afford.

**How a world model helps.** Learn the intersection's or network's response to control actions from data, then plan or train a controller inside it.

**What has been done** (this area is still thin):

- [Dai et al.](https://doi.org/10.1631/FITEE.2200323) (2022) trained a DreamerV2 world model on 64×64 images of vehicle positions at an intersection in SUMO, then trained the signal policy in imagination. Under a demand that starts at its peak and then falls (all four test patterns load the same 1,000 vehicles), average trip delay was 56.3 s, against 106.8 s for fixed-time (Webster) and 97.3 s for actuated control. Under steady demand the gain was small (37.8 s vs 41.3 s).
- [ModelLight](https://arxiv.org/abs/2111.08067) (2021) learned an ensemble of intersection models and matched the best baseline with one-tenth of the simulator interaction.
- [MuJAM](https://arxiv.org/abs/2208.00659) (2024) learned MuZero-style latent dynamics on a graph of lanes from small synthetic networks and ran them, without retraining, on 3,971 signals in Manhattan (with synthetic demand).
- [Airaldi et al.](https://arxiv.org/abs/2311.08820) (2023) used METANET itself as a *grey-box* world model: its parameters, started 30% wrong, were tuned by RL inside an MPC ramp-metering controller. Total time spent fell from about 1,100 to about 700 vehicle-hours in about 20 episodes.
- [Yousefzadeh et al.](https://arxiv.org/abs/2404.07446) (2024) trained a graph-attention surrogate of single intersections on tens of thousands of hours of SUMO runs of a 9-intersection corridor (the paper gives both 40,000 and 400,000 hours), with average errors of roughly 0.4–1.2 vehicles per 20-s interval, fast enough to sit inside a timing optimizer.

**The catch.** Almost every one of these learned from **simulator output, not real traffic**, so it inherits the simulator's assumptions. One 2025 preprint on world-model signal control (arXiv 2511.00549) carries an author note saying its reported gains came from an incorrect traffic-volume scaling factor: a reminder to check results in this young area carefully. A course study of RL perimeter control on the same torus network needed about 83 minutes of simulator-driven training for 31 PPO iterations; replacing the simulator with a learned world model is one way to cut that cost, and the {ref}`worked example <wm-torus>` is a first step in that direction.

(wm-whatif)=
## What-if simulation for safety analysis: the takeover question

A crash database records what went wrong. A takeover log records what *almost* went wrong. A world model can turn each logged takeover into a family of what-ifs (what if the driver had taken over 1 s later, or 2 s later?) and so measure how close each event came to a crash. Safety researchers already ask such questions with physics-based reconstructions. A world model could ask them of thousands of real events, straight from video and vehicle logs.

### The question for one event

Take one clip from the MOTIF Lab's [ADAS-TO dataset](https://www.motiflab.net/projects/adas-to/) ([Wang et al., ITSC 2026](https://arxiv.org/abs/2603.06986)): 20 s of front-camera video and openpilot logs, centred on the moment the driver took control back from the ADAS. Then ask:

- What if the driver had taken over **Δ seconds later** (Δ = 1 s, 2 s), with the ADAS in control until then? Or had not taken over at all, leaving the ADAS to its own limits?
- Would the event have become a crash? If not, how close would it have come (closest gap, minimum time-to-collision, distance out of the lane)?

The answers over a range of Δ form an **outcome-versus-delay curve** for that one event. Its key number is the event's **takeover margin Δ\***: the smallest extra delay that makes a crash likely. A large margin means the driver had time to spare. A margin under a second means the outcome hung on the driver being quick.

```{figure} ../_static/figures/WM_WhatIf_Steps.png
:alt: Left to right. The event: an ADAS-TO clip, video and vehicle logs from 10 s before up to the takeover, a real event. Step 1, observe: the world model reads the clip, so its latents describe this event (abduction). Step 2, edit the action: three branches, on time (the driver acts as recorded), 1 s later (the ADAS drives 1 s longer) and 2 s later (the ADAS drives 2 s longer). Step 3, imagine: each branch is imagined N times, giving P(crash given delta equals 0), P(crash given delta equals 1 s) and P(crash given delta equals 2 s). Bottom: the takeover margin delta star is the smallest delay at which P(crash) passes p star.
:width: 100%

One recorded takeover becomes a family of what-ifs: observe, edit, imagine.
```

The world model reads the real clip once. Each edited takeover time gets its own set of imagined futures, and the share that end in contact traces the event's outcome-versus-delay curve.

(wm-whatif-equation)=
### The key equation

$$
\hat{P}(\text{crash}\mid e,\Delta)=\frac{1}{N}\sum_{n=1}^{N}\mathbf{1}\Big[\min_t\,\text{gap}_n(t;e,\Delta)\le 0\Big]
$$

$$
\Delta^*(e)=\min\big\{\Delta:\ \hat{P}(\text{crash}\mid e,\Delta)\ge p^*\big\}
$$

| Symbol | What it means here |
| --- | --- |
| $e$ | one recorded takeover event (one ADAS-TO clip) |
| $\Delta$ | the extra delay added to the driver's takeover, in seconds |
| $N$ | the number of imagined futures per delay |
| $\text{gap}_n(t; e, \Delta)$ | in imagined future n, the distance to the obstacle at time t (lead vehicle, lane edge, barrier) |
| $\mathbf{1}[\cdot]$ | 1 if the statement in brackets is true, 0 if not |
| $p^*$ | the probability you choose to call "likely", such as 0.5 |

**In words:** start the world model from the real event, delay the driver's action by Δ, and imagine the future N times. The share of futures in which the gap closes to zero estimates the crash probability. The takeover margin is the first delay at which that share passes $p^*$.

### A what-if is a counterfactual, and it has three steps

In causal reasoning, a question about *this* event under a *different* action is a **counterfactual**. Judea Pearl splits answering one into three steps, and each maps onto a world model:

1. **Observe (Pearl's "abduction").** Run the world model over the recorded clip up to the takeover. Its latents now describe this particular event: how hard the lead car braked, the curve ahead, the glare on the windshield.
2. **Edit ("action").** Replace the logged actions from the takeover on. The ADAS keeps control for Δ more seconds (openpilot logs its own planned trajectory, so the edit can use what the system intended to do), and then the driver's inputs begin.
3. **Imagine ("prediction").** Roll forward N times and read the outcome from the heads: gap, time-to-collision, lane position.

This is the "observe, then imagine" of {ref}`the two modes <wm-modes>` with one change: the actions in the imagined part are not the ones in the log.

### The classical version, and a worked illustration

Safety researchers have run counterfactual simulations for years without any learned model. They take an event's recorded motion, replace a driver's response with a delayed or modeled one, and re-simulate the physics:

- [Bärgman et al. (2017)](https://pubmed.ncbi.nlm.nih.gov/28315616) re-simulated 34 rear-end crashes from the SHRP2 naturalistic driving study, with and without forward-collision warning and automatic braking. For the warning, the share of crashes avoided changed a lot with the driver-behavior model they assumed (much less so for automatic braking, which does not wait for the driver). The driver model is not a detail.
- Waymo ([Scanlon et al., 2021](https://pubmed.ncbi.nlm.nih.gov/34700249)) reconstructed 72 fatal crashes from Chandler, Arizona (2008–2017) and put its driving software in place of each human. In the role of the driver who started the crash, it avoided every collision; in the role of the driver who had to respond, it avoided the collision in 82% of simulations and reduced its severity in another 10%.
- UN Regulation 157, for automated lane keeping, defines a reference careful human driver who needs 0.4 s to judge the risk and 0.75 s more to start braking. [Olleja et al. (2025)](https://pubmed.ncbi.nlm.nih.gov/39914089) ran such reference drivers counterfactually on 38 real cut-in near-crashes; one model reacted late enough to turn three near-crashes into crashes.

None of these uses a learned world model, and we found no published study yet that re-simulates a real takeover with a delayed driver using one. That is an open research question.

Here is the physics version on a **synthetic** rear-end event (all inputs are assumptions, chosen inside the range ADAS-TO reports). Both cars travel at 15 m/s (54 km/h, close to ADAS-TO's mean speed of 54.9 km/h) with an 18 m gap (1.2 s headway). The lead car brakes; the ADAS responds gently at 2 m/s². In the "recorded" event the driver takes over 1.0 s after the lead starts braking and brakes at 7 m/s². The what-if keeps the ADAS in control for Δ more seconds.

```{figure} ../_static/figures/WM_Takeover_Curve.png
:alt: Closest gap to the lead car in metres against the extra delay before the driver takes over, from 0 to 2.5 s, for three lead braking levels. Lead braking 4 metres per second squared: the gap falls from about 16 m to about 1.3 m at 2.5 s, no contact. Lead braking 5: from 14.3 m to contact at 1.9 s. Lead braking 6: from about 10.7 m to contact at 1.3 s.
:width: 100%

Synthetic kinematic what-if: with the lead braking at 5 m/s&sup2;, a takeover 1.9 s later ends in a crash. Computed by `takeover_whatif.py` in the course folder (`genmodels/world_models/whatif/`).
```

Each line is one version of the event. Moving right means the driver takes over later; the closest gap shrinks until the cars touch.

- With the lead braking at 5 m/s², the on-time takeover keeps a closest gap of 14.3 m. One second later it is 5.9 m. From 1.9 s later the cars touch (at 1.8 s they stop 2 cm apart): at 2.0 s the impact speed is 15 km/h, at 2.5 s 28 km/h.
- With the lead braking at 6 m/s² the margin is only 1.3 s; with 4 m/s² there is no contact even 2.5 s late.

Three lessons carry over to real events:

1. **The curve is steep near the margin.** A fraction of a second separates a near-miss from a 30 km/h impact.
2. **The margin belongs to the event, not to the driver.** No single rule such as "a 2 s reaction is fine" holds across events.
3. **For a straight-road rear-end with a logged lead vehicle, physics is enough.** Keep the classical method here; it is exact, fast and explainable.

### Where a world model is needed

1. **Other road users who would have reacted.** A cut-in car, a merging truck or a pedestrian would respond to a late ego vehicle. Kinematic replay keeps them on their recorded paths.
2. **Lateral and perception-limited takeovers.** Steering was the first action in 25.3% of ADAS-TO takeovers, and infrastructure degradation (worn markings, work zones) appeared in 47.4% of its safety-critical cases. What happens 1 s later depends on the road ahead, which is in the video, not in a kinematic table.
3. **Scale.** About 16,000 clips cannot be reconstructed by hand. A world model starts from the raw clip.
4. **A spread, not one answer.** Many imagined futures give a crash probability, not a single yes or no.

### From single events to crash frequency and severity

Researchers and agencies want two numbers about an ADAS feature: **how often** its takeovers would end in crashes if drivers were slow, and **how bad** those crashes would be. What-if simulation can get there in three steps:

1. **Every event, every delay.** For each takeover e in the dataset and each extra delay Δ, estimate $\hat{P}(\text{crash} \mid e, \Delta)$, and for the imagined futures that crash, the impact speed.
2. **Weight the delays by how often drivers are that late.** If p(Δ) is the share of drivers who respond Δ seconds later than the recorded one, the expected number of crashes per takeover is the average over events of $\sum_\Delta p(\Delta)\,\hat{P}(\text{crash} \mid e, \Delta)$. Multiply by takeovers per mile and you have crashes per million miles.
3. **Turn impact speeds into severity.** Injury-risk curves link the change in speed at impact to the chance of injury, so the spread of imagined impact speeds becomes a spread of injury outcomes.

"Fails to take over" is the far end of the delay axis: the ADAS keeps control until its own limits, so the world model must imagine what the ADAS alone would do. That is the hardest case, and the one with the least data.

The weak link is p(Δ). It describes real drivers, so it must come from data on real drivers (takeover-time studies, driver-monitoring logs, simulator experiments), not from the world model. Across 129 studies, mean takeover times ranged from 0.69 s to 19.8 s (average 2.72 s) and depended on urgency, distraction and how the request was given (Zhang et al., 2019), so p(Δ) is not one number. A crash-frequency estimate is only as good as the delay distribution it is weighted by.

### What ADAS-TO gives, and what is still missing

| What the analysis needs | What ADAS-TO has | What is missing |
| --- | --- | --- |
| Video and controls on one clock | front camera (526×330) and openpilot logs, at 10 or 100 Hz | &mdash; |
| The takeover moment | every clip aligned at the moment control returns; first action labeled (brake 39.6%, steering 25.3%) | a separate time for the system's takeover request |
| The obstacle | radar lead vehicle in about half the clips (49.8%) | tracks of other road users; lateral obstacles only from video |
| What the ADAS would have done | openpilot's own plan is logged | its behavior beyond its limits |
| Late takeovers (action variety, {ref}`requirement 3 <wm-data-needs>`) | the logs show what drivers actually did; deliberately varied delays are absent | driving-simulator or test-track runs with controlled delays |
| Crashes | safety-critical clips flagged by TTC < 3 s or headway < 0.8 s (285 in the paper; 749 reviewed in the latest release), not crashes | the model must extrapolate to contact it has never seen |
| Driver state | no cabin video | why the driver was late can be imposed, not explained |

### What to be careful about

1. **A late driver is not the same driver shifted in time.** In naturalistic rear-end emergencies, drivers start braking once the lead car looms fast enough, and react faster the more urgent the situation is (Markkula et al., 2016); with less time, takeovers are faster but worse in quality (Gold et al., 2013). Shifting the recorded inputs by Δ is the simplest assumption; a driver-response model that depends on urgency is better.
2. **Say what the ADAS does during the delay.** Its logged plan covers the first moments, but many takeovers happen exactly because the system is at its limit.
3. **Others react too.** If the other road users stay on their logged paths, the margin can be wrong in either direction.
4. **Contact is outside the training data.** Read the crash from geometry (a gap head, like the torus example's throughput head), not from generated pixels. A model trained on crash-free driving can smooth the crash away: the warning of {ref}`4.6 <vae-basics-breaks>` again.
5. **A counterfactual cannot be observed.** Check the method where truth exists: on naturally late takeovers in similar situations, on simulator runs with controlled delays, and against physics where physics is enough.
6. **Report a range.** Treat margins as a way to rank events and generate hypotheses, not as a crash count.

### What it could be used for

- **Rank takeover contexts by margin:** by trigger (brake or steer), speed, weather, road condition. Which ADAS limits leave drivers the least time?
- **Set warning and monitoring thresholds:** how early must a takeover request come, or how soon must a driver-monitoring alert fire, so that a typical late response still leaves margin?
- **Complement extreme value theory:** EVT extrapolates the tail statistically across many near-misses; what-if simulation extrapolates each event mechanistically. When the two agree, trust grows.
- **A new surrogate safety measure:** the takeover margin Δ\*, in seconds, alongside time-to-collision and post-encroachment time.

:::{admonition} Before you trust this result
:class: warning

**What is the baseline?** A kinematic reconstruction of the same event, where one is possible.

**How was the data split, and why is that honest?** Validate on events, drivers and vehicles the world model never saw, and on simulator runs whose delays were set on purpose, so the true outcome of each delay is known.

**What does it do on the ugly cases?** Look hardest at takeovers with reacting neighbors, lateral takeovers on degraded roads, and any delay longer than those seen in training.
:::

(wm-breaks)=
## Where it breaks

World models fail in six predictable ways. The torus example shows three of them in numbers; the papers on {ref}`transportation uses <wm-applications>` show the rest.

### 1. Errors compound over the horizon

Each imagined step is built on the previous imagined step, so small errors feed on themselves. The torus model, tested on 100 held-out runs with varied plans:

```{figure} ../_static/figures/WM_Horizon.png
:alt: Two panels against blocks imagined ahead, 1 to 30, over 100 held-out episodes with varied plans. Left, throughput error in vehicles per step: model B open loop rises from about 0.95 to about 1.5; model B one step ahead, re-observing the real network before every block, stays near 1.0; persistence (no change) sits near 4; model A open loop swings between about 4 and 6.5. Right, vehicles gained or lost as a percentage of the fleet: model B rises from 2.4% to 6.9%, model A from about 6% to 19.4%; the real network is exactly 0.
:width: 100%

Throughput error (left) and vehicles gained or lost (right) against the number of blocks imagined ahead.
```

- Imagining open loop, model B's throughput error grew from 0.95 vehicles per step after one block to about 1.3 after two and about 1.5 after thirty. Re-observing the real network before every block kept it near 1.0. The gap between the two green curves *is* the compounding error.
- Both stayed far below the persistence forecast ("nothing changes", about 4 vehicles per step), so the model still earns its place.
- Model A, used on plans unlike its log, was worse than persistence at every horizon.

**What helps:** re-observe often (MPC re-plans at every step for exactly this reason), keep the horizon as short as the decision allows, and train the model on multi-step predictions, not only one-step ones (PlaNet proposed this as "overshooting").

### 2. Physics is not built in

The torus is closed: the real vehicle count never changes. The imagined one does. Model B gained or lost 2.4% of the fleet after one block and 6.9% after 30 (right panel). Model A, off its training distribution, drifted by 19%. In video world models the same failure looks like a car that melts into the road or a pedestrian who never comes back from behind a bus; the Sora report shows glass that does not shatter properly.

**What helps:** check the invariants you know (count the vehicles), build them into the decoder (predict flows between links, not counts, so conservation holds by construction), or keep a physics model and learn only what it misses.

### 3. It cannot answer for actions it never saw

The {ref}`worked example <wm-torus>` measured this: the model trained on one timing plan predicted every plan to work like that plan, and even the model trained on varied plans was off by a factor of two for the one plan far outside its log. A world model does not know what it does not know, and it will answer anyway.

**What helps:** varied actions in the data ({ref}`requirement 3 <wm-data-needs>`); an ensemble of models whose disagreement flags unfamiliar actions (ModelLight used one); refusing to plan outside the range of logged actions.

### 4. It confuses cause and correlation

In a log, actions are not chosen at random. A controller switches to the peak plan *because* demand is rising; a driver brakes *because* the car ahead braked. A model trained on such logs can learn that the peak plan causes congestion, or that braking causes the lead car to slow. Imitation learning has a close cousin of this problem, called *causal confusion* (de Haan et al., 2019).

**What helps:** logs with actions varied independently of conditions (requirement 3 again), and tests that change one action while holding the scene fixed.

### 5. A controller trained inside it learns to exploit it

A policy trained in imagination looks for whatever earns reward, including the model's mistakes. Ha and Schmidhuber's Doom agent found ways to make the dreamed monsters never fire, and they had to make the dream noisier to stop it. The Waymax result in {ref}`Simulating the other road users <wm-app-agents>` is the same problem with hand-written agents instead of a learned model.

**What helps:** a noisier or ensemble dream, short imagined horizons, and always a final test on the real system or a trusted simulator.

### 6. Looking right is not the same as being right

Video world models are often scored with image-quality measures (FID, FVD). Those reward realism, not correct dynamics. Planning results are often scored open loop, against the human's choice in the log. DriveArena's UniAD result (0.91 open loop on nuScenes; only 13.7% of route length covered in closed loop) shows how far apart these can be.

**What helps:** judge a world model by the decision it supports. The plan ranking in the worked example is that kind of test: does planning with the model pick the plan that is actually best, and does it get the size of the difference right?

(wm-discussion)=
## Discussion: why a world model, and how it compares with what you have learned

A world model is **not a fifth kind of generative model**. It is the generative models of this module put to work on a different question. The autoencoder, VAE, GAN and diffusion pages asked *what does the data look like?* A world model asks *what happens next if I do this?*

### Same machinery, different question

|  | Autoencoder | VAE | GAN | Diffusion | World model |
| --- | --- | --- | --- | --- | --- |
| What it learns | a compressed code that rebuilds x | p(x), through a latent with a prior | a sampler that a learned critic cannot tell from the data | p(x), by learning to remove noise step by step | p(next state \| past states, actions) |
| Training signal | reconstruction error | reconstruction + KL to N(0, I) | the critic's judgment | denoising error | reconstruction + KL to *its own prediction* (+ reward) |
| Knows about time? Takes an action? | no, no | no, no | no, no | no, no (it can take a condition) | **yes, yes** |
| What you get out | a copy of x | new samples of x | new samples of x | new samples of x, possibly steered | a future that **responds to your actions** |
| Its role inside world models | the encoder and decoder (tokenizers) | the latent state with a prior (World Models 2018; the RSSM) | a sharper decoder (DriveGAN, 2021) | the dynamics or the decoder (DIAMOND, GAIA-1 and -2, Cosmos) | &mdash; |
| A transportation question it answers | compress a speed heatmap | what does a plausible heatmap look like? | what does a realistic-looking one look like? | what scene fits this description? | how will this corridor respond to that plan? |

Read down the last column and the rest of the module falls into place:

- **The training data is the same idea as before.** Several pages of this module trained a model to predict a hidden part of the data from a given part: the masked autoencoder of {doc}`4.5 <notes2d-deep-autoencoders>` fills hidden heatmap cells from the visible ones, and unCLIP in {doc}`4.9 <notes7-unclip>` drafts a crash sketch from its narrative. A world model's hidden part is the next state, and its given part is the past **plus the action**.
- **The KL term is the same idea as before.** In the VAE it pulled the latent toward a fixed bell curve. In an RSSM-style world model it pulls the latent toward the model's own forecast, which is how the dynamics are learned.
- **The generator is interchangeable.** VAE, token transformer, GAN, diffusion: each has been the engine of a published world model. Choose the engine for the same reasons as before: diffusion for sharp, varied outputs; tokens for long sequences; a small latent when speed matters more than pictures.

### Why use a world model at all?

Use one when three things are true at once:

1. **The question is a what-if about an action**: a plan to choose, a controller to train, software to test.
2. **The rules are too complex or too unknown to write down**: pixels, pedestrians, the joint behavior of 128 drivers.
3. **You have long logs in which the actions vary**, or a simulator that can supply them.

Then a world model gives you something no earlier model in this module could: a place to **try actions and watch the consequences**, as many times as you like, with nobody at risk. That is Craik's "small-scale model" built from data.

### When to keep the classical simulator

The skeptical engineer's questions still decide the matter. Keep the physics-based model (CTM, METANET, car-following, a calibrated SUMO network) when:

- **A physical law must hold exactly.** CTM conserves vehicles by construction. A learned model only conserves them as well as it was trained to ({ref}`Where it breaks <wm-breaks>` measures the drift in the worked example).
- **The decision must be explained or certified.** A capacity or a free-flow speed means something to a reviewer. A latent does not: decoding a VAE or a world model does not reveal which factors *caused* a crash or a queue.
- **The action is new.** A new lane, a new interchange, a timing plan the corridor has never run: a calibrated physics model extrapolates by its equations; a learned model has no data there.
- **Data is small.** A few weeks of detector data calibrate a fundamental diagram; they do not train a world model.

The best current practice is often a **hybrid**: a physics model whose parameters are learned (METANET tuned inside MPC, in {ref}`traffic operations <wm-app-operations>`), a learned surrogate trained on a calibrated simulator to make it fast, or a learned model of only the part the physics misses, such as driver behavior on top of conservation of vehicles.

(wm-fit)=
### Fit card

:::{admonition} Fit card &mdash; World models
:class: tip

**Idea in one sentence.** Learn how a system's state responds to actions from logged sequences, then roll that model forward to test or choose actions.

**Why it works.** The next observation is a free label; a compact latent makes rollouts cheap; a learned prior keeps track of uncertainty, so imagined futures branch as real ones do.

**Fits these tasks.** Closed-loop testing of driving software, planning (MPC), training controllers in imagination, rare-scenario generation, what-if safety analysis of real events. Leverage labels: *generation*, *prediction*, *judgment*.

**Needs this data.** Time-aligned observation&ndash;action sequences in which the actions vary; hours (a small model) to thousands of hours (video); no labels; from fleets, controller event logs, or simulators.

**Breaks when.** Asked about actions or conditions missing from the data; rolled out far beyond its training horizon; a physical law must hold exactly; the event of interest is rare.

**Keep the classical method when.** The physics is known and can be calibrated, the decision needs an explanation, the action is new, or the data is small.
:::

(wm-summary)=
## Summary, check yourself, and references

### Summary

1. A world model answers **"what happens next if I do this?"** It is a conditional generative model of the next state, given the past and an action, rolled forward on its own output.
2. Transportation engineers already use hand-built world models: CTM, METANET, SUMO, CARLA. A learned one is worth it when the rules are too complex to write down and the logs are long and varied.
3. Four parts: **encoder, dynamics, decoder, heads.** Each comes from a model you have met: the VAE, the recurrent network or transformer, diffusion, the backbone and head.
4. For a latent (RSSM) world model, training is the VAE loss with the KL term pulled toward the model's **own prediction** (which is how the dynamics are learned), plus a reward term. Token and diffusion world models train with their own losses.
5. The data is a tape of observations and actions. The decisive requirement is that **the actions vary**: the torus model trained on one timing plan thought every plan worked like that one.
6. In transportation the mature uses are closed-loop testing and planning for automated driving; traffic operations is young and open.
7. Watch for compounding error, broken physics, unseen actions, causal confusion, exploitation, and scores that reward looks over decisions. Keep the classical model when physics is known, explanation is required, the action is new, or the data is small.
8. For safety, a world model's most promising use may be the what-if: start from a real takeover, delay or remove the driver's response, and imagine the outcome. The event's takeover margin, weighted by how late real drivers are, leads to crash frequency and severity, but every step needs checking against data where the truth is known.

### Check yourself

1. Your district has three years of 5-minute detector data on a corridor and signal timing that changed only by time of day (AM, midday and PM plans). A consultant proposes training a world model to choose a new PM plan. What two questions about the data would you ask first, and what would you propose if the answers are bad?
2. An ADAS supplier reports that its lane-keeping feature drove 10 million miles inside a world model without a lane departure. What would you need to know about that world model, and about how the test was run, before counting those miles as evidence?
3. For a ramp-metering study on I-275 you can use METANET-based MPC, a learned world model, or a hybrid. Which would you choose for a first deployment, what data does each need, and what would change your choice?
4. In the worked example, model B predicted 15.4 vehicles per step for EW 4:1 (real 14.9) but 6.1 for "EW only" (real 3.1). Explain the difference using what was, and was not, in its log.
5. Over 30 imagined blocks, model B gained or lost about 7% of a fleet that never changes. Suggest one change to the model's outputs that would make conservation hold by construction, and say what it costs.
6. A student hopes to read, from the latent variables of a world model trained on intersection video, which factors cause near-misses. What can the latents tell her, and what can't they?
7. You want to estimate how many ADAS-TO takeovers would have become crashes if drivers had been 1 s slower. Which takeovers could you analyze with a kinematic reconstruction alone, which need a world model, and what data about real drivers would you need before reporting a crash frequency?

(wm-references)=
### References

**Ideas and milestones**

- Craik, K. J. W. (1943). [*The Nature of Explanation*, ch. 5](https://cpcontacts.markhuckvale.com/research/hp/Craik_NOE_Chapter_5.pdf). Cambridge University Press.
- Sutton, R. S. (1991). [Dyna, an integrated architecture for learning, planning, and reacting](https://doi.org/10.1145/122344.122377). *ACM SIGART Bulletin* 2(4).
- Ha, D., and Schmidhuber, J. (2018). [World Models](https://arxiv.org/abs/1803.10122). NeurIPS 2018 version: "Recurrent World Models Facilitate Policy Evolution".
- Hafner, D., et al. (2019). [Learning Latent Dynamics for Planning from Pixels (PlaNet)](https://arxiv.org/abs/1811.04551). ICML.
- Hafner, D., et al. [Dreamer](https://arxiv.org/abs/1912.01603) (ICLR 2020), [DreamerV2](https://arxiv.org/abs/2010.02193) (ICLR 2021), [DreamerV3](https://arxiv.org/abs/2301.04104) (*Nature* 2025), [Dreamer 4](https://arxiv.org/abs/2509.24527) (2025).
- Schrittwieser, J., et al. (2020). [MuZero](https://arxiv.org/abs/1911.08265). *Nature* 588.
- LeCun, Y. (2022). [A Path Towards Autonomous Machine Intelligence](https://openreview.net/forum?id=BZ5a1r-kVsf). Position paper.
- Hu, A., et al. (2022). [MILE: Model-Based Imitation Learning for Urban Driving](https://arxiv.org/abs/2210.07729). NeurIPS.
- Hu, A., et al. (2023). [GAIA-1](https://arxiv.org/abs/2309.17080). Russell, L., et al. (2025). [GAIA-2](https://arxiv.org/abs/2503.20523). Wayve.
- Brooks, T., et al. (2024). [Video generation models as world simulators](https://openai.com/index/video-generation-models-as-world-simulators/). OpenAI.
- Bruce, J., et al. (2024). [Genie: Generative Interactive Environments](https://arxiv.org/abs/2402.15391). ICML. Google DeepMind blogs: [Genie 3](https://deepmind.google/discover/blog/genie-3-a-new-frontier-for-world-models/) (2025), [Genie 4](https://deepmind.google/blog/genie-4-a-new-generation-of-world-simulation/) (2026).
- Valevski, D., et al. (2024). [GameNGen](https://arxiv.org/abs/2408.14837). Alonso, E., et al. (2024). [DIAMOND](https://arxiv.org/abs/2405.12399). NeurIPS.
- NVIDIA (2025). [Cosmos World Foundation Model Platform for Physical AI](https://arxiv.org/abs/2501.03575).
- Assran, M., et al. (2025). [V-JEPA 2](https://arxiv.org/abs/2506.09985). Meta.

**Transportation applications**

- Driving world models and closed-loop testing: DriveGAN (Kim et al., CVPR 2021, arXiv 2104.15060), [DriveDreamer](https://arxiv.org/abs/2309.09777), [DriveDreamer-2](https://arxiv.org/abs/2403.06845), [Drive-WM](https://arxiv.org/abs/2311.17918), [GenAD and OpenDV](https://arxiv.org/abs/2403.09630), [Vista](https://arxiv.org/abs/2405.17398), [OccWorld](https://arxiv.org/abs/2311.16038), [Copilot4D](https://arxiv.org/abs/2311.01017), [UniSim](https://arxiv.org/abs/2308.01898), [DriveArena](https://arxiv.org/abs/2408.00415), [Waymo World Model blog](https://waymo.com/blog/2026/02/the-waymo-world-model-a-new-frontier-for-autonomous-driving-simulation), [GAIA-3 blog](https://wayve.ai/thinking/gaia-3/), [GAIA-4 blog](https://wayve.ai/thinking/gaia-4/).
- Planning: [Think2Drive](https://arxiv.org/abs/2402.16720), [LAW](https://arxiv.org/abs/2406.08481), [WoTE](https://arxiv.org/abs/2504.01941), [Epona](https://arxiv.org/abs/2506.24113).
- Simulating road users: [TrafficSim](https://arxiv.org/abs/2101.06557), [TrafficBots](https://arxiv.org/abs/2303.04116), [Trajeglish](https://arxiv.org/abs/2312.04535), [SMART](https://arxiv.org/abs/2405.15677), [Waymo Open Sim Agents Challenge](https://arxiv.org/abs/2305.12032), [Waymax](https://arxiv.org/abs/2310.08710), [SceneDiffuser++](https://arxiv.org/abs/2506.21976).
- Safety scenarios: [STRIVE](https://arxiv.org/abs/2112.05077), [Challenger](https://arxiv.org/abs/2505.15880), [Cosmos-Drive-Dreams](https://arxiv.org/abs/2506.09042).
- Traffic operations: [Dai et al. 2022](https://doi.org/10.1631/FITEE.2200323), [ModelLight](https://arxiv.org/abs/2111.08067), [MuJAM](https://arxiv.org/abs/2208.00659), [Airaldi et al. 2023](https://arxiv.org/abs/2311.08820), [Yousefzadeh et al. 2024](https://arxiv.org/abs/2404.07446).
- Failure modes: de Haan, P., et al. (2019). [Causal Confusion in Imitation Learning](https://arxiv.org/abs/1905.11979). NeurIPS.

**What-if (counterfactual) safety analysis**

- Wang, Y., Xu, Y., Sun, J., and Zhou, H. (2026). [ADAS-TO: A Large-Scale Multimodal Naturalistic Dataset and Empirical Characterization of Human Takeovers during ADAS Engagement](https://arxiv.org/abs/2603.06986). ITSC. Dataset page: [MOTIF Lab](https://www.motiflab.net/projects/adas-to/).
- Pearl, J., Glymour, M., and Jewell, N. P. (2016). [Causal Inference in Statistics: A Primer](https://bayes.cs.ucla.edu/PRIMER/primer-ch4.pdf), §4.2.4 (abduction, action, prediction). Wiley.
- Bärgman, J., Boda, C.-N., and Dozza, M. (2017). [Counterfactual simulations applied to SHRP2 crashes](https://pubmed.ncbi.nlm.nih.gov/28315616). *Accident Analysis & Prevention* 102.
- Scanlon, J. M., et al. (2021). [Waymo simulated driving behavior in reconstructed fatal crashes within an autonomous vehicle operating domain](https://pubmed.ncbi.nlm.nih.gov/34700249). *Accident Analysis & Prevention* 163.
- Olleja, P., Markkula, G., and Bärgman, J. (2025). [Validation of human benchmark models for automated driving system approval: How competent and careful are they really?](https://pubmed.ncbi.nlm.nih.gov/39914089). *Accident Analysis & Prevention* 213.
- Markkula, G., et al. (2016). [A farewell to brake reaction times? Kinematics-dependent brake response in naturalistic rear-end emergencies](https://pubmed.ncbi.nlm.nih.gov/27450793). *Accident Analysis & Prevention* 95.
- Zhang, B., et al. (2019). [Determinants of take-over time from automated driving: A meta-analysis of 129 studies](https://research.tudelft.nl/en/publications/determinants-of-take-over-time-from-automated-driving-a-meta-anal). *Transportation Research Part F* 64.
- Gold, C., et al. (2013). ["Take over!" How long does it take to get the driver back into the loop?](https://mediatum.ub.tum.de/doc/1308108/file.pdf) HFES Annual Meeting.
- Related newer work: [Roy-Singh et al. (2025), Fractional Collisions](https://arxiv.org/abs/2506.07540) (probabilistic counterfactual responses over SHRP2 and Nexar scenes); [Jing et al. (2026), CounterScene](https://arxiv.org/abs/2603.21104) (counterfactual interventions on other road users inside a generative world model).

**Surveys to read next**

- Guan, Y., et al. (2024). [World Models for Autonomous Driving: An Initial Survey](https://arxiv.org/abs/2403.02622).
- Feng, T., et al. (2025). [A Survey of World Models for Autonomous Driving](https://arxiv.org/abs/2501.11260).
- Ding, J., et al. [Understanding World or Predicting Future? A Comprehensive Survey of World Models](https://arxiv.org/abs/2411.14499).

*Data and code:* the worked example uses the course torus simulator (`traffic_sim/torus_sim.py`), and every number in it was computed by the reproducer scripts in the course folder (`genmodels/world_models/`). The takeover illustration is synthetic and comes from `whatif/takeover_whatif.py` in the same folder. The ADAS-TO figures (shares of brake and steering takeovers, lead-vehicle coverage, safety-critical counts) are quoted from Wang et al. (2026) and the dataset page.

---

Next: {doc}`Further reading: JEPA and V-JEPA 2 <notes12-jepa>` &mdash; world models that predict a description of the next frame instead of its pixels, with a car-following example you can run in your browser. After it, {doc}`Further reading: generative models in transportation <notes10-reading-library>` is the closing page of the module, a reading library of 34 papers that use these generators on transportation problems. Back to the {doc}`Module 4 map <index>`.
