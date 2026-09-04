# 1.6 Representation learning and embeddings

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 1 &middot; Section 1.6</span>
    <span class="notes-card-session">Session: Sept 10</span>
  </div>
  <p class="notes-card-lede">One-hot encoding and its three failures; an embedding as a geometry; Word2Vec, and the same algorithm run on a road network; image embeddings and transfer learning; contrastive learning where labels are scarce; CLIP and the open-vocabulary long tail. Closes with the two questions that matter on the job: what is the unit being embedded, and how would you know the representation is any good.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Notebooks that go with it</h4>
      <ul>
      <li><a href="lab2_word_embeddings.html">Lab 2 &mdash; From Word2Vec to Road2Vec</a></li>
      <li><a href="lab3_image_embeddings.html">Lab 3 &mdash; Image embeddings with a deep CNN</a></li>
      <li><a href="lab4_clip_vs_traditional_cv.html">Lab 4 &mdash; CLIP versus traditional computer vision</a></li>
      </ul>
    </div>
  </div>
</div>


## One-hot, and its three failures

A neural network is a function from vectors of numbers to vectors of numbers. It
cannot ingest the string `"stop sign"` or a JPEG. Everything becomes numbers
first, and the question is *which* numbers.

The obvious answer is the one-hot vector: with a 50,000-word vocabulary, every
word is a vector of length 50,000 with a single 1. It works, and it fails three
ways.

1. **High-dimensional and sparse.** Wasteful to store and to compute with.
2. **No notion of similarity.** `"car"` and `"vehicle"` are exactly as different
   as `"car"` and `"banana"` — every pair is orthogonal. The geometry carries no
   information at all.
3. **No generalization.** A model trained on `"truck"` learns nothing
   transferable about `"semi-truck"`.

The same three failures apply to any categorical encoding you have used, and to
raw pixels for images, where a small change in lighting moves the vector
enormously without changing what the image means.

You have already worked around this. Road functional class is a categorical
variable that you would never leave one-hot in a model you cared about — you
would engineer features that capture what makes an arterial arterial. An
embedding is that instinct, automated and learned.

## An embedding is a geometry

An **embedding** is a fixed-length dense vector — typically a few hundred to a
few thousand dimensions — representing a word, a sentence, an image, a road
segment, a trajectory. The point of it is that the *geometry* of the space
encodes meaning:

- Things that mean similar things sit close together.
- Things that mean different things sit far apart.
- Directions in the space often correspond to interpretable axes of variation.

Nobody hand-engineers these vectors. They are learned by training a model on a
pretext task — predict the next word, predict a missing patch, match a caption
to an image — and then keeping the internal representation and throwing the
pretext task away.

This is the same conceptual move you make when you reduce a full traffic state
to a small vector of macroscopic descriptors. You accept a lossy summary because
the summary is the part that generalizes. The difference is that you chose the
descriptors and the network learns them.

## Word2Vec, and the same algorithm on a road network

The classic example is **Word2Vec** (Mikolov et al., 2013), and the idea is a
single sentence from linguistics:

> *"You shall know a word by the company it keeps."* — J. R. Firth, 1957

Word2Vec trains a shallow network to predict a word from its surrounding context
over billions of sentences. It never sees a dictionary or a part-of-speech tag.
Yet the resulting vectors satisfy relations like
$\text{vec}(\text{king}) - \text{vec}(\text{man}) + \text{vec}(\text{woman})
\approx \text{vec}(\text{queen})$, synonyms cluster, and antonyms sit on opposite
sides of meaningful axes. Rich structure, extracted from raw co-occurrence
statistics, with no labels.

Now the part that matters here: **the algorithm does not know its inputs were
words.** Replace "sentences of words" with "random walks across a road network"
and the same machinery produces **road-segment embeddings** that recover
functional classification — arterial, local, highway — without ever being told
the labels. Context in a corridor plays the role that context in a sentence
played. That is Lab 2, and it is the cheapest possible demonstration that the
representation idea transfers out of natural language.

## Image embeddings and transfer learning

The image story ran in parallel. A deep CNN trained on a large labeled dataset
learns a hierarchy: early layers respond to edges, color blobs, and oriented
textures; middle layers compose those into parts — wheels, faces, vehicle
silhouettes; late layers respond to whole-object concepts.

Take a pretrained network like **ResNet-50**, cut off the classification head,
and what remains is an *image encoder*: a function from a raw image to a
2048-dimensional vector. Those vectors have the same property as word
embeddings — semantically similar images land close together, even when the
network was trained on a completely different label set.

This is **transfer learning** in its simplest useful form, and it is the single
most practically important idea in this module for agency work: you are reusing
a representation you did not pay to train. The relevant follow-on questions are
whether to freeze the encoder and train only a head, or to fine-tune the whole
thing — and how far your imagery has drifted from what the encoder was trained
on. Florida roadside imagery at dusk in the rain is not ImageNet, and domain
shift is the reason a model that demoed well fails in deployment.

## Contrastive learning: supervision without labels

Contrastive learning trains on *similarity* rather than on labels: pull
representations of things that belong together closer, push everything else
apart. You need pairs that should match, not a labeled category for every
example.

In transportation this matters more than it does almost anywhere else, because
labels are the scarce resource. Nobody has a labeled dataset of every hazard
type on Florida's arterials. But you often have pairs that should match for
free — the same location photographed twice, two cameras seeing one incident, a
crash record and its narrative, a trajectory and the segment it traversed.
Contrastive learning is how those free pairs become a representation.

## CLIP: images and language in one space

The striking recent development is that images and text can be embedded into the
*same* space. **CLIP** is trained on image–caption pairs contrastively, so the
vector for a photo of a stop sign lands near the vector for the phrase
"a red octagonal traffic sign."

The consequence is **zero-shot, open-vocabulary recognition**. You do not train a
classifier for "flooded roadway"; you write the phrase and rank images by
similarity to it. For long-tail mobility safety scenarios — the situations that
matter most and appear in no label set — this is a genuine change in what is
possible, and it is the technical substrate under a great many of the "AI dash
camera" products on the market.

It is also where prompt sensitivity, and a fresh set of failure modes, enter the
picture. Lab 4 makes you find them yourself, which is the only way that lesson
lands.

## What is worth embedding in mobility

Almost every modern deep learning system in transportation decomposes the same
way:

1. **Encoder** — raw input (image, video frame, trajectory, segment, text) → embedding.
2. **Backbone** — work in embedding space (attention, graph network, MLP).
3. **Head** — embedding → output (a class, a number, a sentence).

Most of the engineering decisions you will make are about choosing, freezing, or
fine-tuning encoders. Which means the first design question in a mobility AI
project is usually: *what is the unit being embedded?* A road segment. A
trajectory. An OD pair. A whole scene. A five-minute traffic state. An incident
record. Choosing that unit wrong is more damaging than choosing the architecture
wrong, and it is a transportation decision, not a machine learning one.

## How to know a representation is any good

An embedding space is easy to produce and easy to over-trust. Before you build
anything on top of one, check it:

- **Does the neighborhood structure make sense?** Pick a handful of items you
  know well and look at their nearest neighbors. If two stop signs from
  different angles are not neighbors, stop.
- **Does a simple probe recover something you did not train on?** If a linear
  classifier on frozen embeddings can recover functional class, the information
  is genuinely in there.
- **Does the low-dimensional plot mislead you?** t-SNE and UMAP will produce
  attractive clusters from noise. Treat those pictures as hypotheses.
- **Does it transfer?** The real test is whether the representation helps on a
  task it was not trained for.

We come back to this with real measurements later in the course, on a
representation trained on traffic states rather than images.

:::{admonition} Before you trust this result
:class: important
**What is the baseline?** For an embedding, the baseline is the hand-engineered
feature set you would have built anyway. Learned representations frequently win;
they should still have to.

**How was the data split, and why is that honest?** If the encoder was pretrained
on data that overlaps your test set, your evaluation is contaminated and the
number is meaningless.

**What does it do on the ugly cases?** Night, rain, glare, occlusion,
construction, and the classes that appear twice in the whole dataset. Aggregate
accuracy hides exactly the cases that matter in safety work.
:::

---

Next: {doc}`notes7-labs` &mdash; the notebooks, the exercises, and what to carry into Module 2.
