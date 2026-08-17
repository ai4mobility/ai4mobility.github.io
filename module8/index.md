# Module 8 — Safety, Agency Practice, and Responsible Use

*Weeks 12 and 13 of the {doc}`../syllabus`.*

## Overview

This module covers the two places where AI in mobility meets professional accountability.

The first is **safety analysis**. Crashes are rare, under-reported, and lagging — which is why
the field has spent decades building surrogate measures from conflicts and near-misses. AI
makes those measures cheap to compute at scale from video. It does not, by itself, make them
valid. The interesting question is not whether you can detect a conflict, but whether the
conflicts you detect predict the crashes you care about.

The second is **agency practice**: report generation, manual and standards QA, planning
support, and the document-heavy work that consumes a large share of professional engineering
time. This is where AI's productivity gains are most immediate and where the oversight
question is sharpest, because the failure mode is a fluent, confident, wrong document that
looks exactly like a right one.

The module closes on responsible use and on the economics — what an AI mobility workflow
actually costs to run, and whether it beats the classical approach it replaced.

## Learning objectives

By the end of this module you will be able to:

- Compute surrogate safety measures (time-to-collision, post-encroachment time) from trajectory
  data, and state precisely what they do and do not establish about crash risk.
- Describe crash precursor and conflict detection from video, and design a validation strategy
  against crash records.
- Apply AI to an agency document workflow — report drafting, manual QA, planning support — with
  a human oversight step you can defend.
- Reason about privacy in mobility data: faces, plates, MAC addresses, and the
  re-identifiability of trajectory data.
- Estimate the cost of an AI mobility workflow — inference, latency, maintenance — and judge
  whether it is worth it relative to the classical baseline.
- Articulate where professional accountability sits when an AI system is in the decision loop.

## Topics

- Surrogate safety measures: TTC, PET, deceleration rate to avoid crash
- Traffic conflict techniques and their long-standing validation problem
- Crash precursor detection from video; trajectory extraction and calibration
- Validating surrogate measures against crash records
- AI for report generation, document QA, and standards checking
- Planning support and scenario summarization
- Interpretability and meaningful human oversight — versus oversight theater
- Privacy and de-identification in mobility data; trajectory re-identification
- IRB considerations for student and agency data collection
- Bias and equity in mobility datasets and deployed systems
- Tokenomics: inference cost, latency budgets, total cost of ownership
- Evaluating a vendor claim; procurement and maintenance reality

## Video lectures

*To be populated.* See the course [YouTube channel](https://www.youtube.com/@hao6247).

## Recommended readings

- Tarko, A. P. (2018). Surrogate measures of safety. In *Safe Mobility: Challenges, Methodology and Solutions*. Emerald Publishing.
- Gettman, D., & Head, L. (2003). Surrogate safety measures from traffic simulation models. *Transportation Research Record, 1840*, 104–115.
- Zheng, L., Ismail, K., & Meng, X. (2014). Traffic conflict techniques for road safety analysis: Open questions and some insights. *Canadian Journal of Civil Engineering, 41*(7), 633–641.
- de Montjoye, Y.-A., Hidalgo, C. A., Verleysen, M., & Blondel, V. D. (2013). Unique in the crowd: The privacy bounds of human mobility. *Scientific Reports, 3*, 1376.
- Bender, E. M., Gebru, T., McMillan-Major, A., & Shmitchell, S. (2021). On the dangers of stochastic parrots: Can language models be too big? *FAccT*.

## Labs

- **Surrogate safety from video.** Extract trajectories from an intersection video, compute TTC
  and PET distributions, and then do the part that usually gets skipped: state what would have
  to be true for these numbers to predict crashes at this location, and check whether it is.

- **An agency document workflow.** Build an AI-assisted workflow for a real document task —
  drafting a section of a report, checking a submittal against a standard — and design the
  verification step. Then measure how long the workflow takes end to end, including your
  verification, and compare it honestly to doing it by hand.
