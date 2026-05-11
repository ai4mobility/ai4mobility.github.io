# Lecture 1.1 — Course Overview & Why AI for Mobility

```{admonition} Watch the recording
:class: tip
[Lecture 1.1 on YouTube](https://www.youtube.com/@hao6247) — *link will go live once the recording is posted.*
```

## Why this course exists

Transportation is being transformed by AI on three fronts: how we **sense** the system (cameras, lidars, V2X), how we **operate** vehicles (ADAS, autonomous driving, lane keeping), and how we **plan and manage** networks (simulation, digital twins, signal control, demand prediction).

This is not just hype — and that's exactly why a critical engineering perspective matters. The AI-for-mobility literature publishes impressive demos but also many results that don't replicate, don't deploy, or don't actually beat a well-tuned classical baseline. Part of what you'll learn in this course is to tell the difference.

## What we mean by "AI"

We'll use "AI" as a loose umbrella for several related technologies:

**Classical machine learning.** Linear and tree-based models, SVMs, clustering. Old, boring, and still the right answer for a surprising number of transportation problems — especially when the input is tabular sensor data and the model needs to be explainable.

**Deep learning.** Neural networks trained end-to-end. The dominant approach for vision, speech, and (increasingly) time-series. The default tool when the input is an image, a video, or raw sensor waveforms.

**Computer vision.** A specialized branch of deep learning — detecting and tracking objects in images and video. Central to traffic monitoring and autonomous perception. Module 2 lives here.

**Reinforcement learning.** Agents that learn by interacting with an environment. Used for signal control, autonomous driving policy, and ride-sharing dispatch. Powerful but notoriously hard to make reliable for safety-critical use.

**Large foundation models.** Vision-language models, LLMs, and multi-modal models. Beginning to appear in traffic engineering workflows for tasks like incident description and natural-language querying of traffic data.

Throughout the course we'll be honest about which tool fits which job. Sometimes that means deep learning is overkill.

## Where AI shows up in mobility today

A non-exhaustive map of the territory:

- **Perception for ADAS and AVs** — Tesla Autopilot, Waymo, Cruise, Mobileye: object detection, lane detection, depth estimation, trajectory prediction.
- **Traffic monitoring** — vehicle counts, classification, incident detection from roadside cameras or drones; AI dash cameras.
- **Driver monitoring** — distraction detection, fatigue estimation, gaze tracking.
- **Demand and travel-time prediction** — ride-hailing dispatch, origin-destination prediction, parking availability.
- **Signal control** — reinforcement-learning-based adaptive signal timing.
- **Simulation and digital twins** — neural surrogates for microsimulation, calibrated digital replicas of real corridors.
- **Maintenance and asset management** — pavement crack detection, sign inventory from imagery.

Each of these will get treatment somewhere in the next three modules.

## How this course is organized

- **Module 1** *(here)* — Foundations and ML refresher.
- **Module 2** — AI sensing: computer vision applied to traffic.
- **Module 3** — AI for driving automation and V2X connectivity.
- **Module 4** — AI traffic simulation and digital twins.

Each module has lecture notes (these pages), a recorded video walkthrough, a hands-on lab notebook you can run in Google Colab, and a small reading list.

## What we won't cover

To keep the scope tractable, this course doesn't dive deeply into:

- The theory of optimization or deep-learning architectures from first principles — see the {doc}`../resources` page for that.
- Full self-driving system engineering (hardware, sensor fusion at depth, safety cases).
- The policy, regulatory, and ethical questions around AI in mobility — these get a brief treatment but deserve a course of their own.

## A note on critical reading

A recurring theme of this course is *how to read AI-mobility papers honestly.* Ask of every result you encounter:

1. **What is the baseline?** Beating "naive linear regression" is not the same as beating a well-tuned ARIMA.
2. **What is the test set?** Was it geographically and temporally separated from training?
3. **What's the cost of failure?** A 95%-accurate model is fine for vehicle counting and catastrophic for emergency braking.
4. **Does the deployment story work?** Many published models assume compute or labeling resources that no real DOT has.

We'll come back to these questions repeatedly.

## What's next

Head to the {doc}`lab1` notebook to confirm your environment works and warm up on a small traffic-flow dataset.
