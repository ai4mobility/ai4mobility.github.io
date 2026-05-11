# Module 3 — AI for Driving Automation and Connectivity

## Overview

This module covers AI's role in the vehicle itself — Advanced Driver Assistance Systems (ADAS), automated driving stacks, and the connectivity layer that lets vehicles share information with each other and with infrastructure (V2X). We focus on how AI components plug into the broader perception–prediction–planning–control pipeline, what they're good at, and where they fail.

## Learning objectives

By the end of this module you will be able to:

- Map the major modules of an automated-driving stack (perception, localization, prediction, planning, control) and identify where AI is used in each.
- Describe how production ADAS features (lane-keeping assist, adaptive cruise control, automatic emergency braking) work — and how AI changes them.
- Analyze trajectory-prediction approaches (social pooling, graph neural networks, transformer-based predictors).
- Reason about the safety, efficiency, and equity implications of AV adoption on traffic flow.
- Explain V2X (V2V, V2I) technologies and how AI is being applied to cooperative perception, cooperative driving, and connected signal control.

## Topics

- Architecture of modern automated-driving stacks (modular vs end-to-end)
- Perception fusion: camera + lidar + radar
- Behavior prediction: model-based vs learned
- Motion planning under uncertainty
- Lane-keeping and longitudinal control with neural networks
- Imitation learning and end-to-end driving
- V2V, V2I, V2X protocols (DSRC, C-V2X)
- Cooperative perception and cooperative driving
- Mixed-traffic dynamics: how AVs interact with human drivers
- Safety, verification, and validation

## Video lectures

*To be populated.* See the course [YouTube channel](https://www.youtube.com/@hao6247).

## Recommended readings

- Yurtsever et al. (2020). *A Survey of Autonomous Driving: Common Practices and Emerging Technologies.* IEEE Access.
- Bojarski et al. (2016). *End to End Learning for Self-Driving Cars.* (NVIDIA PilotNet — historical but illustrative.)
- Casas et al. (2020). *Implicit Latent Variable Model for Scene-Consistent Motion Forecasting.* ECCV.
- Talebpour & Mahmassani (2016). *Influence of connected and autonomous vehicles on traffic flow stability and throughput.* Transportation Research Part C.

## Lab

*Coming soon:* Train a small CNN-based lane-keeping policy from front-camera images, evaluate it in a simulator, and analyze failure cases.
