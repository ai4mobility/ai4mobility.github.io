# Module 4 — AI Traffic Simulation and Digital Twin

## Overview

Traffic simulation has been a workhorse of transportation engineering for decades — microsimulators like SUMO, VISSIM, and Aimsun let us evaluate signal plans, geometric changes, and operational strategies before building them. AI is now reshaping this space in two ways: (1) **learned components inside simulators** — neural car-following models, RL-based signal controllers, learned demand generators; and (2) **digital twins** — continuously calibrated real-time replicas of corridors and networks that ingest live sensor data.

## Learning objectives

By the end of this module you will be able to:

- Set up and run a basic microscopic traffic simulation in SUMO.
- Train a reinforcement-learning agent to control a single signalized intersection.
- Explain how neural network car-following and lane-changing models compare to calibrated classical models (IDM, Wiedemann, MOBIL).
- Describe what makes a "digital twin" different from a traditional offline simulation, and what real-world data and computation it requires.
- Critique a claimed RL-based traffic-control result — is it reproducible, does it transfer, does it beat actuated baselines?

## Topics

- Microscopic, mesoscopic, and macroscopic traffic simulation
- Calibration and validation of microsimulation models
- Neural car-following and lane-changing models
- Reinforcement learning for traffic signal control
- Multi-agent RL for coordinated signal networks
- Digital twins: architecture, data flows, calibration loops
- Online learning and model drift
- Surrogate models — replacing expensive simulators with neural emulators

## Video lectures

*To be populated.* See the course [YouTube channel](https://www.youtube.com/@hao6247).

## Recommended readings

- Treiber, Hennecke, & Helbing (2000). *Congested traffic states in empirical observations and microscopic simulations (Intelligent Driver Model).* Physical Review E.
- Wei et al. (2019). *PressLight: Learning Max Pressure Control to Coordinate Traffic Signals in Arterial Network.* KDD.
- Chen et al. (2020). *Toward A Thousand Lights: Decentralized Deep Reinforcement Learning for Large-Scale Traffic Signal Control.* AAAI.
- Saroj et al. (2021). *Development of a Connected Corridor Real-Time Data-Driven Traffic Digital Twin Simulation Model.* J. Transp. Eng. A.

## Lab

*Coming soon:* Use SUMO and a reinforcement-learning library to train a Q-learning signal controller on a single intersection, then compare its performance against a fixed-time baseline and a fully-actuated baseline.
