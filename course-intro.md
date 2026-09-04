# Week 1 — Course Introduction

*Aug 27, 2026 — the first meeting of the {doc}`syllabus`. This session sets up the
vocabulary, the project, and the standard of proof the rest of the course is held to.*

---

## Why this course has the shape it does

Transportation is being reshaped by AI on three fronts: how we **sense** the
system (cameras, lidar, radar, V2X, probe data), how we **operate** vehicles
(ADAS, lane keeping, driving automation), and how we **plan and manage**
networks (simulation, digital twins, signal control, demand prediction).

That is the optimistic framing, and it is broadly true. It is also exactly why a
critical engineering perspective matters. The AI-for-mobility literature
publishes impressive demonstrations alongside a large number of results that do
not replicate, do not deploy, or do not actually beat a well-tuned classical
baseline. A significant part of what you should get out of this course is the
ability to tell those apart — quickly, and in front of a vendor.

So the course opens by being precise about what "AI" covers, and by fixing the
questions you will ask of every result you meet — before any model gets built.
Module 1 then builds the neural network and the representation idea; the
applied modules take those into sensing, driving, simulation and agency
practice.

---

## Before the first class

Fill this out before we meet on **Aug 27**. It takes about 12 minutes, and what comes back
decides how fast the labs move, how project teams get formed, and which examples this course
leads with.

Answer honestly rather than impressively — "never done it" is a useful answer and it costs you
nothing. Nothing here is graded on content. The section on what feels uncomfortable about using
AI is anonymized: names are stripped before those answers are read as a set, and the aggregate
goes on screen in the first class without attribution.

The survey stores nothing on its own and sends nothing anywhere. When you finish it, it hands
you a block of text — copy that into the **"Before We Start"** submission in Canvas.

<div class="resource-callout">
  <strong><a href="_static/companions/AI4Mobility_Intake_Survey.html" target="_blank" rel="noopener">Open the survey full screen &#8599;</a></strong>
  — it is long, and it fills in more comfortably outside the frame below. Either way your
  progress is saved in your own browser as you go, so you can stop and come back to it.
</div>

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Intake survey — Before We Start</span>
    <a href="_static/companions/AI4Mobility_Intake_Survey.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="_static/companions/AI4Mobility_Intake_Survey.html" title="Before We Start — intake survey" loading="lazy"></iframe>
</div>

---

## Five families, and which job each is for

We use "AI" as a loose umbrella. It is worth being precise about what sits under
it, because the families have genuinely different failure modes.

**Classical machine learning.** Linear and tree-based models, SVMs, clustering.
Old, unglamorous, and still the right answer for a surprising number of
transportation problems — especially when the input is tabular sensor data and
somebody has to explain the model to a review board.

**Deep learning.** Neural networks trained end-to-end. The dominant approach for
vision, speech, and increasingly time series. The default when the input is an
image, a video, or a raw sensor waveform.

**Computer vision.** A specialized branch of deep learning: detecting and
tracking objects in images and video. Central to traffic monitoring and to
vehicle perception. Module 5 lives here.

**Reinforcement learning.** Agents that learn by interacting with an
environment. Used for signal control, driving policy, and dispatch. Powerful,
and notoriously hard to make reliable for anything safety-critical.

**Large foundation models.** LLMs, vision-language models, multimodal models.
Now appearing in agency workflows for incident description, document search,
report drafting, and natural-language querying of traffic data.

Throughout the course we will be honest about which tool fits which job.
Sometimes that means deep learning is overkill, and saying so is a professional
skill rather than a failure of ambition.

<div class="resource-callout">
<strong>Where AI enters a task &mdash; the workflow framing.</strong> The other half of
this session was the vocabulary the whole semester uses: a task written as
<strong>trigger &rarr; ingest &rarr; transform &rarr; act &rarr; checkpoint &rarr; record</strong>, each step
labelled with one of six kinds of leverage &mdash; <strong>extraction &middot; classification &middot;
generation &middot; retrieval &middot; prediction &middot; judgment</strong> &mdash; and the human review placed
immediately before the first irreversible action. That material is operations
material, so it is written up with the operations module: see
<a href="module7/notes.html">Module 7 &sect;7.1</a> for the anatomy, the six labels, the
checkpoint rule, and the worked Traffic Incident Management case.
</div>

---

## What your graduate training already buys you

A recurring worry in a course like this is that the transportation background is
the thing being replaced. It is not, and the workflow framing in
{doc}`Module 7 <module7/notes>` is what makes that concrete.

Traffic flow theory tells you what a plausible output looks like, which is how
you catch a model that has learned something absurd. Statistics tells you
whether a difference is real. The four-step model and simulation experience tell
you what a validation gate is and how it fails. Design manuals tell you what the
constraint actually is, not what the data suggests. Safety analysis tells you
what the cost of a false negative is. Field data collection tells you how dirty
real data is before anyone cleans it. TSM&O practice tells you who has to act on
the output and how fast. Programming and writing turn all of that into something
that runs and something that persuades.

The scarce skill in this field is not building the model. It is knowing which
step is safe to automate and how to prove the result. That is a transportation
engineering skill, and you are most of the way to having it.

---

## Reading a capability claim

Every result you meet — in a paper, a vendor deck, or a press release — gets the
same four questions:

1. **What is the baseline?** Beating "naive linear regression" is not the same
   as beating a well-tuned ARIMA, and beating a fixed-time signal plan is not
   the same as beating a properly configured actuated controller.
2. **What is the test set?** Was it separated from the training data
   *geographically and temporally*, or is it a random split of one corridor on
   one week, in which case the model may simply have memorized that week?
3. **What is the cost of failure?** 95% accuracy is fine for vehicle counting
   and catastrophic for emergency braking. The number means nothing until you
   know which side of that line you are on.
4. **Does the deployment story work?** Many published models assume compute,
   connectivity, or labeling budgets that no real agency has.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion — Your first AI workflow</span>
    <a href="_static/companions/AI_Workflow_Companion.html" target="_blank" rel="noopener">Open full screen ↗</a>
  </div>
  <iframe src="_static/companions/AI_Workflow_Companion.html"
          title="Your first AI workflow" loading="lazy"></iframe>
</div>

---

## What else this session covered

- What "AI" means in a transportation context, and what it does not
- Where AI is deployed in mobility today: vehicles, roadside, agency workflows, mobility services
- Course expectations, lab logistics, hardware, and how the semester is graded
- The group project: example topics, candidate datasets, and what makes a project finishable
- Reading capability claims critically: what was measured, on what data, against what baseline

The module map, the grading weights and the full schedule are in the
{doc}`syllabus`; the project timeline and deliverables are in the
{doc}`capstone/index`.

---

Next: {doc}`module1/index` — AI foundations, starting Sept 3.
