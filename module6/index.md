# Module 6 — AI for Autonomous Driving and Connectivity

*Week 10 of the {doc}`../syllabus` — Oct 29, 2026.*

## Class meetings

| Date | Session topic | Due before class |
|---|---|---|
| Oct 29 | AI for vehicle intelligence and driver-assistance systems: longitudinal control, lane-keeping, vehicle data, and transportation system applications | **First project progress report** · *rotating project progress report or project clinic* |

## Overview

This module covers AI's role in the vehicle itself — advanced driver assistance systems
(ADAS), automated driving stacks, and the connectivity layer that lets vehicles share
information with each other and with infrastructure (V2X). We focus on how AI components plug
into the perception–prediction–planning–control pipeline, what they are good at, and where
they fail.

The emphasis here leans toward **production vehicle intelligence** rather than research
prototypes. Lane-keeping assist and adaptive cruise control are already deployed at scale and
already changing traffic flow; open-source stacks like Openpilot make that behavior
inspectable; and CAN bus and telematics data make it measurable. That combination — a real
system you can read the code of, running on a real vehicle, producing data you can analyze —
is rare and worth exploiting.

## Learning objectives

By the end of this module you will be able to:

- Map the major components of an automated-driving stack (perception, localization, prediction,
  planning, control) and identify where AI is used in each.
- Describe how production ADAS features — lane-keeping assist, adaptive cruise control,
  automatic emergency braking — work, and how learned components change them.
- Analyze trajectory-prediction approaches: social pooling, graph neural networks, and
  transformer-based predictors.
- Read CAN bus and telematics data from a production vehicle and extract control behavior.
- Reason about the safety, efficiency, and equity implications of ADAS and AV adoption on
  traffic flow, including string stability in mixed traffic.
- Explain V2X technologies and how AI is applied to cooperative perception, cooperative
  driving, and connected signal control.

## Topics

- Architecture of modern automated-driving stacks: modular vs. end-to-end
- Perception fusion: camera + lidar + radar
- Behavior prediction: model-based vs. learned
- Motion planning under uncertainty
- Lane-keeping and longitudinal control with neural networks
- Openpilot as a readable production-grade stack
- CAN bus, telematics, and vehicle data extraction
- Imitation learning and end-to-end driving
- String stability and the traffic-flow consequences of commercial ACC
- V2V, V2I, V2X protocols (DSRC, C-V2X)
- Cooperative perception and cooperative driving
- Mixed-traffic dynamics: how automated vehicles interact with human drivers
- Safety, verification, and validation

## Video lectures

*To be populated.* See the course [YouTube channel](https://www.youtube.com/@hao6247).

## Recommended readings

- Yurtsever, E., Lambert, J., Carballo, A., & Takeda, K. (2020). A survey of autonomous driving: Common practices and emerging technologies. *IEEE Access*.
- Bojarski, M., et al. (2016). End to end learning for self-driving cars. *arXiv:1604.07316*. *(NVIDIA PilotNet — historical but illustrative.)*
- Casas, S., Gulino, C., Suo, S., Luo, K., Liao, R., & Urtasun, R. (2020). Implicit latent variable model for scene-consistent motion forecasting. *ECCV*.
- Milanés, V., & Shladover, S. E. (2014). Modeling cooperative and autonomous adaptive cruise control dynamic responses using experimental data. *Transportation Research Part C, 48*, 285–300.
- Talebpour, A., & Mahmassani, H. S. (2016). Influence of connected and autonomous vehicles on traffic flow stability and throughput. *Transportation Research Part C, 71*, 143–163.

## Labs

- **Reading a production driving stack.** Work through the Openpilot longitudinal and lateral
  control paths, then examine CAN/telematics traces from a vehicle running it. The question is
  not "how would you build this" but "what is this system actually doing, and how would you
  know if it were doing it badly?"

- **A lane-keeping policy from camera images.** Train a small CNN policy on front-camera
  frames, evaluate it in simulation, and analyze the failure cases — particularly the ones that
  look fine on aggregate metrics.

*Hardware sessions use the instructor's comma 3x development device. No student is required to
install hardware on a personal vehicle or to operate a vehicle for this course.*
