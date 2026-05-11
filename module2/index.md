# Module 2 — AI Sensing for Traffic Monitoring

## Overview

Computer vision has become the dominant sensing modality for traffic monitoring. In this module we cover how convolutional and transformer-based networks are used to detect, track, classify, and count vehicles and pedestrians; how data is collected from roadside cameras, drones, and AI dash cameras; and how to evaluate detector quality in ways that map to real transportation needs (counts, speeds, queue lengths) — not just generic mAP scores.

## Learning objectives

By the end of this module you will be able to:

- Describe the architecture and training data behind modern object detectors (YOLO, RT-DETR, DINO).
- Train and fine-tune a vehicle detector on traffic-camera footage.
- Track detected vehicles across frames (SORT, ByteTrack, BoT-SORT) and extract counts and speeds.
- Identify failure modes of camera-based traffic monitoring (occlusion, night-time, glare, perspective distortion) and discuss mitigations.
- Connect detection outputs to downstream traffic-engineering measures: volumes by class, turning movement counts, queue lengths, incident flags.

## Topics

- Image data pipelines and annotation
- Two-stage vs single-stage detectors; modern transformer-based detectors
- Multi-object tracking and re-identification
- AI dash cameras and edge deployment
- Drone-based monitoring and bird's-eye trajectory extraction
- Hazard and incident detection
- Evaluation metrics that matter for transportation (count error, speed error) vs computer-vision metrics (mAP)

## Video lectures

*To be populated.* See the course [YouTube channel](https://www.youtube.com/@hao6247).

## Recommended readings

- Redmon et al. (2016). *You Only Look Once: Unified, Real-Time Object Detection.* CVPR.
- Carion et al. (2020). *End-to-End Object Detection with Transformers (DETR).* ECCV.
- Wojke, Bewley, & Paulus (2017). *Simple Online and Realtime Tracking with a Deep Association Metric (DeepSORT).* ICIP.
- Survey papers on vehicle detection and tracking for ITS (recent, choose based on year of study).

## Lab

*Coming soon:* Train a YOLO vehicle detector on a publicly available traffic-camera dataset, then use ByteTrack to extract counts and turning-movement statistics.
