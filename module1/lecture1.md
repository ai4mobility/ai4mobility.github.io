# Lecture 1 — Course Overview, and How AI Represents Words and Images

```{admonition} Watch the recording
:class: tip
[Lecture 1 on YouTube](https://www.youtube.com/@hao6247) — *link will go live once the recording is posted.*
```

This first lecture has two parts. **Part 1** sets up the course: what we mean by "AI" in the mobility context, where it shows up today, and how to read the literature critically. **Part 2** introduces the single most important concept that underpins almost everything that follows — **embeddings**, the way modern AI represents words, images, and (as we'll see in later modules) road networks, trajectories, and traffic states as vectors of numbers. We need this idea in hand *before* we talk about transformers and large language models in the next lecture, because transformers are essentially machines that read in, transform, and write out embeddings.

## Why this course exists

Transportation is being transformed by AI on three fronts: how we **sense** the system (cameras, lidars, V2X), how we **operate** vehicles (ADAS, autonomous driving, lane keeping), and how we **plan and manage** networks (simulation, digital twins, signal control, demand prediction).

This is not just hype — and that's exactly why a critical engineering perspective matters. The AI-for-mobility literature publishes impressive demos but also many results that don't replicate, don't deploy, or don't actually beat a well-tuned classical baseline. Part of what you'll learn in this course is to tell the difference.

## Part 1 — Course Overview

### What we mean by "AI"

We'll use "AI" as a loose umbrella for several related technologies:

**Classical machine learning.** Linear and tree-based models, SVMs, clustering. Old, boring, and still the right answer for a surprising number of transportation problems — especially when the input is tabular sensor data and the model needs to be explainable.

**Deep learning.** Neural networks trained end-to-end. The dominant approach for vision, speech, and (increasingly) time-series. The default tool when the input is an image, a video, or raw sensor waveforms.

**Computer vision.** A specialized branch of deep learning — detecting and tracking objects in images and video. Central to traffic monitoring and autonomous perception. Module 2 lives here.

**Reinforcement learning.** Agents that learn by interacting with an environment. Used for signal control, autonomous driving policy, and ride-sharing dispatch. Powerful but notoriously hard to make reliable for safety-critical use.

**Large foundation models.** Vision-language models, LLMs, and multi-modal models. Beginning to appear in traffic engineering workflows for tasks like incident description and natural-language querying of traffic data.

Throughout the course we'll be honest about which tool fits which job. Sometimes that means deep learning is overkill.

### Where AI shows up in mobility today

A non-exhaustive map of the territory:

- **Perception for ADAS and AVs** — Tesla Autopilot, Waymo, Cruise, Mobileye: object detection, lane detection, depth estimation, trajectory prediction.
- **Traffic monitoring** — vehicle counts, classification, incident detection from roadside cameras or drones; AI dash cameras.
- **Driver monitoring** — distraction detection, fatigue estimation, gaze tracking.
- **Demand and travel-time prediction** — ride-hailing dispatch, origin-destination prediction, parking availability.
- **Signal control** — reinforcement-learning-based adaptive signal timing.
- **Simulation and digital twins** — neural surrogates for microsimulation, calibrated digital replicas of real corridors.
- **Maintenance and asset management** — pavement crack detection, sign inventory from imagery.

Each of these will get treatment somewhere in the next three modules.

### How this course is organized

- **Module 1** *(here)* — Foundations and ML refresher.
- **Module 2** — AI sensing: computer vision applied to traffic.
- **Module 3** — AI for driving automation and V2X connectivity.
- **Module 4** — AI traffic simulation and digital twins.

Each module has lecture notes (these pages), a recorded video walkthrough, a hands-on lab notebook you can run in Google Colab, and a small reading list.

### What we won't cover

To keep the scope tractable, this course doesn't dive deeply into:

- The theory of optimization or deep-learning architectures from first principles — see the {doc}`../resources` page for that.
- Full self-driving system engineering (hardware, sensor fusion at depth, safety cases).
- The policy, regulatory, and ethical questions around AI in mobility — these get a brief treatment but deserve a course of their own.

### A note on critical reading

A recurring theme of this course is *how to read AI-mobility papers honestly.* Ask of every result you encounter:

1. **What is the baseline?** Beating "naive linear regression" is not the same as beating a well-tuned ARIMA.
2. **What is the test set?** Was it geographically and temporally separated from training?
3. **What's the cost of failure?** A 95%-accurate model is fine for vehicle counting and catastrophic for emergency braking.
4. **Does the deployment story work?** Many published models assume compute or labeling resources that no real DOT has.

We'll come back to these questions repeatedly.

## Part 2 — How AI Represents Words and Images: Embeddings

Before we can talk meaningfully about transformers, large language models, or vision-language models in the next lecture, we need to settle one question: **how does a neural network see a word, or a picture, in the first place?**

A neural network is fundamentally a function that maps vectors of numbers to vectors of numbers. It cannot ingest the literal string `"stop sign"` or a JPEG file. Everything has to become numbers first. The question is *which* numbers — and the answer that has reshaped the field over the last fifteen years is: **learned, dense, low-dimensional vectors called embeddings.**

### The naive baseline: one-hot encoding

The obvious way to turn a word into numbers is the one-hot vector. If your vocabulary has 50,000 words, every word is a vector of length 50,000 with a single 1 and 49,999 zeros. Each word gets its own dimension.

This works, but it has three crippling problems:

1. **High-dimensional and sparse.** Computation is wasteful; storage is wasteful.
2. **No notion of similarity.** The vectors for `"car"` and `"vehicle"` are mathematically just as different as `"car"` and `"banana"` — every pair is orthogonal. The geometry carries no meaning.
3. **No generalization.** A model trained on `"truck"` learns nothing transferable about `"semi-truck"`.

For images the analog is even worse: raw pixel intensities are extremely high-dimensional and small shifts in lighting or viewpoint move the vector enormously without changing what the image *means*.

### The big idea: learn a dense vector where geometry encodes meaning

An **embedding** is a fixed-length vector — typically a few hundred to a few thousand dimensions — that represents a word, a sentence, an image, a road segment, or any other discrete object. The key property is that the *geometry* of the embedding space encodes semantic relationships:

- Items that mean similar things sit close together.
- Items that mean different things sit far apart.
- Directions in the space often correspond to meaningful axes of variation (gender, tense, vehicle size, road functional class, …).

Crucially, no one hand-engineers these vectors. They are **learned** from data by training a model on a pretext task (predict the next word, predict missing pixels, match captions to images) and then keeping the internal representations.

### Word embeddings: Word2Vec

The classic example is **Word2Vec** (Mikolov et al., 2013). The idea is captured in a single slogan from linguistics:

> *"You shall know a word by the company it keeps."* — J. R. Firth, 1957

Word2Vec trains a shallow neural network to predict a word from its surrounding context (or vice versa) over billions of sentences. It never sees a dictionary, never sees a part-of-speech label. Yet the embeddings it produces have stunning properties:

- `vec("king") − vec("man") + vec("woman") ≈ vec("queen")`
- `vec("Paris") − vec("France") + vec("Italy") ≈ vec("Rome")`
- Synonyms cluster; antonyms sit on opposite sides of meaningful axes.

This was a turning point. It showed that **rich, structured semantic knowledge can be extracted from raw co-occurrence statistics**, without labels.

**Why this matters for mobility:** the same algorithm doesn't care that its inputs were words. Replace "sentences of words" with "random walks across a road network," and the algorithm learns **road-segment embeddings** that capture functional class, connectivity, and neighborhood structure — without ever being told which segments are arterials versus locals. That's the journey of Lab 2: from Word2Vec to Road2Vec.

### Image embeddings: deep CNNs

The image-side story unfolded in parallel. A **deep convolutional neural network** (CNN) trained on a large labeled image dataset like ImageNet learns, layer by layer, a hierarchy of visual features:

- Early layers detect edges, color blobs, and oriented textures.
- Middle layers compose those into parts: wheels, faces, vehicle silhouettes.
- Late layers respond to whole-object concepts: stop sign, sedan, pedestrian.

If you take a pretrained CNN like **ResNet-50** and cut off the final classification head, what's left is an **image encoder**: a function that maps a raw image to a fixed-length vector (2048-dimensional for ResNet-50). These vectors have the same magical property as word embeddings — semantically similar images land close together in the vector space, even when the network was trained on a completely different label set.

This is why "image embeddings" are the workhorse of modern computer vision pipelines, including the perception stacks of ADAS and AV systems we'll study in Module 2. Detection, retrieval, anomaly detection, fine-tuning to a custom dataset, road hazard classification — they all start from a pretrained embedding.

### Multimodal embeddings: a glimpse ahead

The most striking recent development is that we can now train models like **CLIP** to put images *and* text in the **same** embedding space. The vector for an image of a stop sign sits near the vector for the phrase `"a red octagonal traffic sign"`. This enables zero-shot classification, natural-language retrieval over image databases, and is the technical substrate behind a lot of the "AI dash camera" and traffic-monitoring products on the market. We will come back to CLIP-style models in Module 2.

### Why embeddings are the right frame for this course

Almost every modern deep-learning system in transportation can be decomposed into:

1. **Encoder** — turns raw input (image, video frame, trajectory, road segment, text) into an embedding.
2. **Backbone** — does work in embedding space (transformer attention, graph network, MLP).
3. **Head** — turns the embedding into the final output (a class, a number, a generated sentence).

Most of the engineering decisions you'll make as an AI-mobility practitioner are about choosing or fine-tuning encoders. Once you understand embeddings, the architectures that follow — transformers, LLMs, vision-language models, graph neural networks — are mostly variations on the theme of "how should we manipulate vectors in embedding space."

That is what makes this the right starting point.

## What's next

You have **three hands-on notebooks** for this module — please run all three before our next class meeting:

1. **{doc}`lab1`** — *Python + ML warmup.* Confirms your environment works and recalls the supervised-learning pipeline on a small traffic-flow dataset.
2. **{doc}`lab2_word_embeddings`** — *From Word2Vec to Road2Vec.* Train word embeddings on a small text corpus, observe the famous `king − man + woman ≈ queen` analogy, then apply the *identical* algorithm to random walks on a real road network around USF Tampa and discover that the learned road-segment vectors recover functional classification without supervision.
3. **{doc}`lab3_image_embeddings`** — *How a Deep CNN Produces Image Embeddings.* Load a pretrained ResNet-50, visualize what each convolutional layer responds to, extract 2048-dimensional image embeddings, and verify that semantically similar images (e.g., two stop signs from different angles) cluster in embedding space.

After these labs you'll have hands-on intuition for *what* embeddings are. In Lecture 2 we'll see how the **transformer** architecture takes these embeddings as input and reshapes the entire field.
