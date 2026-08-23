# Module 5 — Mobility Sensing and Edge AI

*Weeks 8 and 9 of the {doc}`../syllabus` — Oct 15 and Oct 22, 2026.*

## Class meetings

| Date | Session topic | Due before class |
|---|---|---|
| Oct 15 | AI for mobility sensing: computer vision, vehicle-based sensing, roadside sensing, radar, lidar, and related transportation data sources | **Final project proposal** · *rotating project progress report* |
| Oct 22 | Edge AI and hardware-integrated mobility systems: edge devices, embedded computing, vehicle computing platforms, and AI robotics | Project progress materials as assigned · *rotating project progress report* |

## Overview

Computer vision has become the dominant sensing modality for traffic monitoring. This module
covers how convolutional and transformer-based networks detect, track, classify, and count
vehicles and pedestrians, and how to evaluate detector quality in terms a transportation
engineer cares about — counts, speeds, queue lengths — rather than generic mAP scores.

The sensing half is organized around where the sensor sits, because that decides what you can
measure. **Roadside sensing** — fixed cameras, drones, radar, lidar, Wi-Fi and Bluetooth
readers — gives you a complete picture of one location. **Vehicle-based sensing** — dashcams,
AI cameras, CAN and telematics streams, probe fleets — gives you a thin sample of everywhere,
which turns out to be the right trade for asset inventory, pavement and sign condition, and
corridor-wide travel time. Neither substitutes for the other, and knowing which question each
can answer is most of the skill.

The second half is about where the model actually runs. A detector that needs a datacenter GPU
is not a roadside product. **Edge AI** is the engineering discipline of getting a useful model
onto a device with a power budget, a thermal limit, and no reliable backhaul. That includes
the embedded accelerators on a pole, the **vehicle computing platforms** that carry a
production driving stack, and the small **AI robotics** platforms we use in class to make the
sense–compute–act loop concrete. This is where the course's hardware sessions live.

## Learning objectives

By the end of this module you will be able to:

- Describe the architecture and training data behind modern object detectors (YOLO, DETR-family, RT-DETR).
- Train or fine-tune a vehicle detector on traffic-camera footage.
- Track detected vehicles across frames (SORT, DeepSORT, ByteTrack) and extract counts and speeds.
- Identify failure modes of camera-based monitoring — occlusion, night, glare, perspective
  distortion, weather — and discuss mitigations.
- Compare camera, radar, lidar, and Wi-Fi/Bluetooth sensing on cost, coverage, accuracy, and
  privacy exposure.
- Choose between roadside and vehicle-based sensing for a given measurement problem, and state
  the sampling bias each one introduces.
- Connect detection outputs to transportation measures: volumes by class, turning movement
  counts, queue lengths, incident flags.
- Quantize or compress a model and deploy it to an edge device, then measure the accuracy and
  latency you traded away.
- Describe the compute hierarchy a mobility AI system runs on — embedded accelerator, vehicle
  computing platform, gateway, cloud — and place a workload on it for defensible reasons.

## Topics

- Image data pipelines and annotation; dataset bias in roadway imagery
- Two-stage vs. single-stage detectors; transformer-based detectors
- Multi-object tracking and re-identification
- Drone-based monitoring and bird's-eye trajectory extraction
- Hazard and incident detection
- Radar and lidar for traffic sensing; sensor fusion basics
- Wi-Fi and Bluetooth probe sensing: penetration rates, sampling bias, privacy
- Vehicle-based sensing: dashcams and AI cameras, forward-camera crops, CAN and telematics streams, probe and fleet data
- Roadside versus vehicle-based coverage: complete-at-a-point versus thin-everywhere, and which transportation questions each can answer
- Related agency data sources and how sensing output joins them: ATMS/ATSPM feeds, crash and asset inventories, work-zone and 511 feeds
- Evaluation metrics that matter for transportation (count error, speed error) vs. computer-vision metrics (mAP)
- Edge hardware: NVIDIA Jetson, AI dash cameras, embedded accelerators, microcontroller-class devices
- Vehicle computing platforms: automotive SoCs, the comma 3x development device, in-vehicle compute and power budgets
- AI robotics as a teaching platform: the sense → compute → act loop on M5Stack desktop robots
- Model compression: quantization, pruning, distillation; INT8 inference
- Power, thermal, and bandwidth constraints; on-device vs. backhaul decisions
- Privacy by design at the edge — what should never leave the device

## Video lectures

*To be populated.* See the course [YouTube channel](https://www.youtube.com/@hao6247).

## Recommended readings

- Redmon, J., Divvala, S., Girshick, R., & Farhadi, A. (2016). You only look once: Unified, real-time object detection. *CVPR*.
- Carion, N., et al. (2020). End-to-end object detection with transformers. *ECCV*. *(DETR.)*
- Wojke, N., Bewley, A., & Paulus, D. (2017). Simple online and realtime tracking with a deep association metric. *ICIP*. *(DeepSORT.)*
- Howard, A. G., et al. (2017). MobileNets: Efficient convolutional neural networks for mobile vision applications. *arXiv:1704.04861*.
- Jacob, B., et al. (2018). Quantization and training of neural networks for efficient integer-arithmetic-only inference. *CVPR*.
- A recent survey on vehicle detection and tracking for ITS — choose one from the current year.

## Labs

- **Vehicle detection and tracking.** Train a YOLO detector on a public traffic-camera dataset,
  then use ByteTrack to extract counts and turning-movement statistics. Compare your counts
  against manual ground truth and report count error, not mAP.

- **Deploy it to the edge.** Take the detector you just trained, quantize it, and run it on a
  Jetson. Measure what you lost in accuracy and what you gained in latency and power — then
  decide whether you would put it on a pole.

*Hardware sessions use instructor-provided equipment. See the {doc}`../prerequisites` page.*
