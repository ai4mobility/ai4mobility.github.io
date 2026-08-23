# Module 7 — Traffic Simulation, Digital Twins, and Operations

*Week 11 of the {doc}`../syllabus` — Nov 5, 2026.*

## Class meetings

| Date | Session topic | Due before class |
|---|---|---|
| Nov 5 | AI for traffic simulation, digital twins, and traffic operations: SUMO/CARLA, signal control, and transportation system management | Project progress update · *rotating project progress report* |

## Overview

Traffic simulation has been a workhorse of transportation engineering for decades —
microsimulators like SUMO, VISSIM, and Aimsun let us evaluate signal plans, geometric changes,
and operational strategies before building them. AI is reshaping this space in two ways:
**learned components inside simulators** (neural car-following models, RL-based signal
controllers, learned demand generators), and **digital twins** — continuously calibrated
real-time replicas of corridors and networks that ingest live sensor data.

CARLA extends the same idea to the sensor level, rendering camera, lidar, and radar streams
for driving-stack development. Between SUMO and CARLA you can test a claim at either the
network scale or the vehicle scale, which is exactly what a well-posed mobility question
usually requires.

The module closes with an application that matters in Florida specifically: modeling
evacuation and hurricane mobility, where the demand patterns fall far outside anything in the
calibration data.

## Learning objectives

By the end of this module you will be able to:

- Set up and run a basic microscopic traffic simulation in SUMO.
- Train a reinforcement-learning agent to control a signalized intersection, and compare it
  honestly against fixed-time and fully-actuated baselines.
- Explain how neural car-following and lane-changing models compare to calibrated classical
  models (IDM, Wiedemann, MOBIL).
- Describe what makes a digital twin different from an offline simulation, and what data,
  calibration loop, and computation it requires.
- Use CARLA to generate sensor data for a perception or control component.
- Identify where AI fits into day-to-day transportation systems management and operations —
  signal retiming, ramp metering, incident detection and response, performance measurement —
  and what data an agency would already have to have.
- Reason about simulating conditions outside the calibration range — evacuation, incident, and
  hurricane mobility scenarios.
- Critique a claimed RL traffic-control result: is it reproducible, does it transfer, does it
  beat an actuated baseline that was actually tuned?

## Topics

- Microscopic, mesoscopic, and macroscopic simulation
- Calibration and validation of microsimulation models
- Neural car-following and lane-changing models
- Reinforcement learning for traffic signal control
- Multi-agent RL for coordinated signal networks
- Digital twins: architecture, data flows, calibration loops
- Transportation systems management and operations (TSM&O): where the AI actually lands —
  automated signal performance measures, adaptive and retiming workflows, ramp metering,
  incident detection and response, work-zone and event management
- Operational data an agency already owns: ATSPM, ATMS logs, detector health, probe travel times
- Online learning and model drift
- Surrogate models — replacing expensive simulators with neural emulators
- CARLA and sensor-level simulation for driving stacks
- Sim-to-real transfer and its failure modes
- Evacuation and hurricane mobility modeling

## Video lectures

*To be populated.* See the course [YouTube channel](https://www.youtube.com/@hao6247).

## Recommended readings

- Treiber, M., Hennecke, A., & Helbing, D. (2000). Congested traffic states in empirical observations and microscopic simulations. *Physical Review E, 62*(2), 1805–1824. *(The Intelligent Driver Model.)*
- Dosovitskiy, A., Ros, G., Codevilla, F., López, A., & Koltun, V. (2017). CARLA: An open urban driving simulator. *CoRL*.
- Wei, H., Chen, C., Zheng, G., Wu, K., Gayah, V., Xu, K., & Li, Z. (2019). PressLight: Learning max pressure control to coordinate traffic signals in arterial network. *KDD*.
- Chen, C., et al. (2020). Toward a thousand lights: Decentralized deep reinforcement learning for large-scale traffic signal control. *AAAI*.
- Saroj, A. J., Roy, S., Guin, A., & Hunter, M. (2021). Development of a connected corridor real-time data-driven traffic digital twin simulation model. *Journal of Transportation Engineering, Part A*.

## Labs

- **RL signal control in SUMO.** Train a Q-learning controller on a single intersection, then
  compare it against a fixed-time baseline *and* a properly tuned actuated baseline. The second
  comparison is the one that usually deflates the result, which is why it's the point of the lab.

- **Sensor simulation in CARLA.** Generate camera and lidar streams for a scenario you design,
  and use them to test a perception component from Module 5. Then ask what the simulator is
  systematically failing to represent.
