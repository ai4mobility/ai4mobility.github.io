# 2.10 DETR: a hundred questions, one answer per vehicle

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 2 &middot; Section 2.10</span>
    <span class="notes-card-session">Session: ViT extensions and fusion</span>
  </div>
  <p class="notes-card-lede">A detector must return a list of unknown length, one box per vehicle. DETR asks 100 learned questions that read the frame through the cross-attention of 2.9, trained so each vehicle is claimed by exactly one. This section opens the decoder on a real Florida intersection, measures where it breaks, and turns it into a design move for your own problems: decide what one answer is, and give it a query.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Interactive companion on this page</h4>
      <ul>
      <li><a href="../_static/companions/DETR_Companion.html" target="_blank" rel="noopener">How DETR detects &#8599;</a></li>
      </ul>
    </div>
    <div>
      <h4>Read it first</h4>
      <ul>
      <li><a href="notes9-cross-attention.html">2.9 Cross-attention: one sequence reads another</a></li>
      <li><a href="notes3-attention.html">2.3 Attention: the mechanism</a></li>
      </ul>
    </div>
  </div>
</div>

## What this section covers

- One frame, two detectors, one backbone; DETR's four parts, three you already know
- Object queries: what one is, how it reads the frame through cross-attention, why each finds a favourite place
- Training: match first, then grade &mdash; Hungarian matching as the transportation problem
- NMS without NMS: how the queries settle duplicates among themselves, and what survives
- Where DETR breaks: the 100-query ceiling, small vehicles, training cost
- Your problem, your queries: four query designs for mobility

## One frame, two detectors, one backbone

```{figure} ../_static/figures/DETR_Two_Detectors.jpg
:alt: One dashcam frame twice: Faster R-CNN's 239 boxes before NMS, stacked several deep on every car, and DETR's 32 answers, about one box per object.
:width: 100%

Same frame, same ResNet-50: Faster R-CNN returns 239 boxes at score 0.5 or above and needs NMS to keep 24; DETR returns 32 answers and deletes nothing. Photo: Michael Rivera, CC BY 4.0 (Wikimedia Commons).
```

Counting turning movements or measuring a queue starts by turning a frame into a list of objects of
unknown length. You met the classical answer in the Faster R-CNN of the
{ref}`scooter case <scooter-kid-case>`: propose far too many boxes, then delete overlaps with a
hand-written rule, non-maximum suppression (NMS), with an overlap (IoU) threshold someone has to choose.
On a dashcam frame of a Jacksonville intersection, Faster R-CNN returns 239 boxes at score 0.5 or
above, and class-wise NMS at IoU 0.5 keeps 24. DETR returns 32 answers and deletes nothing: it was
trained so that each object is claimed once. Both sit on the same ResNet-50 (23.5 million weights; see
{ref}`1.4 <cnn-architectures>`), and in all they weigh 41.5 million against 41.8 million.

The IoU threshold is not harmless: queued cars at a stop bar overlap, and at a threshold of 0.3 NMS can
delete the second car of a tight queue. DETR has no such knob, but has its own queue problem
({ref}`below <detr-query-zones>`).

## DETR in four parts, three you know

```{figure} ../_static/figures/DETR_Architecture.png
:alt: Frame, ResNet-50, a 24 by 42 token grid, encoder; 100 learned queries enter a decoder that reads the tokens; two heads give each a class and a box.
:width: 100%

A CNN, a BERT-style encoder and a cross-attention decoder; what is new is the 100 learned queries, the "no object" class and set matching. Photo: Michael Rivera, CC BY 4.0 (Wikimedia Commons).
```

**The CNN.** The 1920 &times; 1080 frame is resized to 1333 &times; 750, ResNet-50 turns it into a
24 &times; 42 grid of 2,048-number vectors, and a 1 &times; 1 convolution shrinks each to 256 numbers:
1,008 tokens, each covering a 32 &times; 32-pixel square, plus a code for its row and column. **The
encoder** is a BERT-style encoder ({doc}`2.5 <notes5-bert>`): every token
reads every other, six layers deep, about a million pairs per head on this frame. **The decoder** is the
new part: 100 learned query vectors, the same 100 for every frame, which in each of six layers read each
other and then the encoded tokens. That is the cross-attention of {doc}`2.9 <notes9-cross-attention>`:
the queries ask, the frame answers. **Two small heads** turn each query into a class (one of 91 COCO
ids, or &empty;, "no object") and a box. That gives 100 answers at once, none generated word by word and
none deleted afterwards: query 71 says "car" at 1.00, query 2 "nothing here" at 0.98.

## Cross-attention, back again: the query asks, the cells answer

```{figure} ../_static/figures/DETR_XAttn_Mechanism.png
:alt: Query 71 becomes a 32-number question; on the frame's grid of cells its weight concentrates on gold-outlined cells over a white SUV.
:width: 100%

Query 71 scores all 1,008 cells, and most of its weight lands on the 18 cells under the SUV it ends up boxing, 1.8% of the frame. Photo: Michael Rivera, CC BY 4.0 (Wikimedia Commons).
```

In 2.9 a word of a crash narrative asked and the patches of the officer's diagram answered. Here query
71, at the last decoder layer, asks the 1,008 cells of the frame. **The query asks:** its 256 numbers,
times $W_Q$, become a question of 32 numbers per head. **The cells answer:** each becomes a key (what it
advertises, plus a code for where it is) and a value (what it hands over). **Score, softmax, average:**
$q \cdot k$ for every cell, a softmax over the 1,008 scores, a weighted average of the values, added
back to the query. Averaged over the 8 heads, 61% of the weight lands on the 18 cells under the SUV; in
2.9 the label head put a narrative word's weight on the few patches printing it, 80.3&times; their share
of the diagram. Same mechanism, same behaviour: the one asking finds the few places that answer it, and leaves carrying what the frame shows
there. The equation is 2.9's, unchanged:

$$
\text{CrossAttn}(X, Z) = \text{softmax}\!\left(\frac{(XW_Q)(ZW_K)^\top}{\sqrt{d}}\right) ZW_V
$$

$X$ asks and $Z$ answers (table below); $W_Q, W_K, W_V$ make the question, the keys and the values; $d$
is the head size; the softmax runs across the cells, so each query's weights sum to one.

| | Crash report (2.9): narrative reads diagram | DETR: queries read the frame |
|---|---|---|
| $X$, who asks | 102 narrative tokens (one example narrative) | 100 object queries, learned |
| $Z$, who answers | 577 diagram patches | 1,008 image cells (this frame) |
| weights per head, per layer | 58,854 | 100,800 |
| head size; heads, layers | 64; 12, 12 | 32 ($\sqrt{d}$ about 5.7); 8, 6 |
| cross-attention parameters | 28.4 M of 224 M | 1.6 M of 41.5 M |
| $X$ leaves with | words that carry the diagram | one object's evidence &rarr; class, box |

**In words:** put the 100 queries where the words were and the frame's cells where the diagram's patches
were; nothing else changes. "Where" enters on both sides: the cells' keys carry their 2-D position code,
the queries their learned position. Why do the queries ask? Swap the roles and the output has one row
per cell, 1,008 answers instead of one per object. This is the fourth of 2.9's four places
cross-attention lives: the questions are themselves learned parameters.

(detr-object-queries)=
## What is an object query?

```{figure} ../_static/figures/DETR_Query_Places.png
:alt: Six panels, one per query, each dot one box centre on one FL511 frame; each query's dots cluster in its own region, and q82's sit on the right edge.
:width: 100%

Six of DETR's 100 queries on 600 FL511 frames: each keeps returning to its own part of the picture, and nobody told it where to look.
```

Physically, a query is 256 numbers stored in the model like any other weight, not computed from the
image: the same 100 come in with every frame, 25,600 numbers in all, and they are why DETR can return at
most 100 objects. In the decoder each query has two parts. Its **position part** is that learned vector,
added again before every attention step, so a query never forgets which question it is. Its **content
part** starts empty and is rewritten by each layer: what the query has found so far. Because the content
starts empty, all a query brings to layer 1 is its position, which is why each ends up specialising in a
region and a box size (Carion et al., 2020, Fig. 7).

Nobody gives a query a job. The figure runs the paper's weights on 600 Tampa Bay FL511 frames from
{doc}`Lab 6 <../module6/lab6_vit_finetune>`, every prediction plotted: q63 works the upper left, q58 the
centre, q75 the right side, and q82 sits on the right edge and never names anything. Across all hundred,
the median query's box centres lie a typical 0.27 frame widths from their mean, against 0.41 for a
query that answered anywhere; 1 of 100 never fires; the average frame gets 7.4 confident answers.
(The 224-pixel Lab 6 images are enlarged, so small vehicles are soft.)

You know a hand-drawn version of this: the video detection zones a technician draws at a signal. **An
object query is a detection zone that training placed, and that moves and resizes to whatever vehicle is
in front of it.** The analogy also says how it fails. A hand-drawn zone fails when the camera is bumped;
a query fails when a re-aimed camera puts vehicles where the favourite places do not reach, or piles
them onto a few queries. The check is the figure above, redrawn on the new camera.

## How a query works: three steps, six times

```{figure} ../_static/figures/DETR_Decoder_Layer.png
:alt: One decoder layer: self-attention among queries, cross-attention to the frame, feed-forward, then a graded draft; repeated six times.
:width: 100%

The queries read each other, then the frame, then update themselves; six times, with a draft answer graded after every layer.
```

**Self-attention:** the 100 queries read each other, 10,000 weights per head; here a query can see
another already claiming a car. **Cross-attention:** they read the frame, 100,800 weights per head.
**Feed-forward:** each updates itself, on its own. After every layer the heads give a draft class and
box, and in training every draft is graded. Two real queries on the same dark car show what six
repetitions buy. At layer 1 q65 is surer than q55, 0.87 against 0.78, but its box is worse. By layer 4
q65 has backed off to 0.25 and q55 has climbed to 0.99; at layer 6 their boxes overlap the car at IoU
0.90 (q55) and 0.28 (q65). Nothing deleted q65's box: the queries settled it between themselves. The
drafts do not show which step did it; the DETR paper credits the self-attention among queries.

## 100 questions, a handful of answers

Every frame gets exactly 100 answers, most of them "no object". On the Jacksonville frame 32 queries
name something at 0.5 or above and 18 are more than 90% sure there is nothing for them. In a parking lot
seen from the air, 42 name something and only 1 is that sure of nothing: every question is busy, and 100
is a hard budget ({ref}`limits <detr-limits>`).

:::{admonition} Before you trust this result
:class: warning
**What is the baseline?** Faster R-CNN R50-FPN, same ResNet-50, same resize, with class-wise NMS at IoU
0.5.

**How was the data split, and why is that honest?** There is none: the companion's eight openly licensed
photographs have no labels, so these are counts of what each detector said, not accuracy.

**What does it do on the ugly cases?** The parking lot and the I-35 and I-95 frames hold more vehicles
than DETR names; see the limits below.
:::

(detr-matching)=
## Training: match first, then grade

```{figure} ../_static/figures/DETR_Matching.png
:alt: Two vehicles, A and B, each with a dashed label box, a gold box for the matched query and dotted boxes for other drafts.
:width: 100%

Layer 1's drafts: one query per vehicle is graded as that vehicle (gold); every other draft on it is graded "should have said nothing" (dotted). Photo: Michael Rivera, CC BY 4.0 (Wikimedia Commons).
```

The 100 answers come in no order, and this frame has 13 labelled road users, not 100. So DETR first
decides which query is supposed to be which vehicle, and only then grades. The figure uses layer 1's
rough draft, where the duplicates are; the labels stand in for an annotator (Faster R-CNN's road users
at score 0.7 or above).

| Vehicle | Draft | Cost | Graded as |
|---|---|---|---|
| A | q55 | &minus;0.40 | car A |
| A | q65 | +0.66 | &empty; |
| A | q43 | +1.14 | &empty; |
| B | q71 | &minus;0.62 | car B |
| B | q95 | +0.61 | &empty; |

Each vehicle gets one query; every other draft on it is graded &empty;. **That is the lesson that
teaches the model not to duplicate.** q65 says "car" at 0.87, surer than q55, but its box is worse, and
the cost weighs both. 13 queries are graded on class and box, the other 87 on saying &empty;:

$$
\hat\sigma = \arg\min_{\sigma} \sum_i C\big(y_i,\ \hat y_{\sigma(i)}\big),
\qquad
C = -\hat p(c_i) + 5\,\lVert b_i - \hat b \rVert_1 + 2\,\big(1 - \text{GIoU}(b_i, \hat b)\big)
$$

- $y_i = (c_i, b_i)$ &mdash; labelled road user $i$: its class and box (centre, width, height as shares of the frame).
- $\sigma$ &mdash; a plan: which query answers for which vehicle, at most one each; $\hat\sigma$ is the cheapest.
- $C$ &mdash; the cost of one pairing: low if the query already says the right class and draws a close box.
- $\hat p(c_i)$ &mdash; the query's probability for the vehicle's class.
- $\lVert b_i - \hat b \rVert_1$, GIoU &mdash; how far the box is off, and how well the boxes overlap; 5 and 2 are the paper's weights.

**In words:** find the cheapest one-to-one pairing of vehicles and answers, grade each pair, and grade
every unpaired answer as "should have said nothing". You have solved this before: each vehicle supplies
one unit, each query absorbs at most one, moving a unit costs $C$. That is the transportation problem
with unit supplies (Hitchcock, 1941), solved exactly by Kuhn's Hungarian method (1955); a tracker solves
it every frame when it links new detections to existing tracks.

:::{admonition} Going deeper &mdash; the whole loss
:class: dropdown
$$
\mathcal{L} = \sum_{\text{matched}} \Big[-\log \hat p(c_i) + 5\,\lVert b_i - \hat b \rVert_1 + 2\,\big(1 - \text{GIoU}\big)\Big] + 0.1 \sum_{\text{unmatched}} -\log \hat p(\varnothing)
$$

**L1 and GIoU together:** L1 treats 4 px off on a distant car like 4 px off on a bus; GIoU is scale-free
and still has a gradient when boxes do not overlap (Rezatofighi et al., 2019). **0.1 on &empty;:** in a
typical image 90 or more of the 100 queries are unmatched; at full weight those easy lessons swamp the
real ones. **After every decoder layer:** each layer's draft is matched and graded too (auxiliary
losses), which is why the drafts on this page are readable. Source: Carion et al., 2020, &sect;3.1 and
&sect;4.
:::

## Why a set? Three grading rules

The companion trained a small DETR three times on a **synthetic** drone view of a four-lane road (16
queries, 292,263 weights, 12,000 steps, same data and seed), changing only the grading rule:
*Hungarian*; an *ordered list* (vehicles sorted by lane and position, handed to queries 0, 1, 2 in
order); and *top-3*, the YOLO-style rule making each vehicle the target of its three cheapest queries.
On 1,000 fresh scenes:

| Rule | AP50 | after NMS | duplicate pairs per scene |
|---|---|---|---|
| Hungarian (DETR) | 95.2 | 96.0 | 0.67 |
| Ordered list | 97.1 | 97.1 | 0.01 |
| Top-3 per vehicle | 30.7 | 65.0 | 16.28 |

On scenes like the training ones the ordered list *wins*: this toy road has a reading order. But no
training scene held more than 12 vehicles; at 16 the list finds 51.7% of them and Hungarian 80.7%, at
24, 12.8% against 51.7%. A list ties a query to a rank; a set ties it to whatever is in its part of the
road. A camera frame has no reading order, so DETR matches sets.

:::{admonition} Before you trust this result
:class: warning
**What is the baseline?** The other two rules, same model, data, seed and steps.

**How was the data split, and why is that honest?** Fresh scenes from the same generator, 1,000 for the
table and 200 per crowd size: fair between rules, silent about real cameras.

**What does it do on the ugly cases?** Crowds beyond training reverse the ranking, and top-3 is
handicapped with 16 queries (recall 65.6% at 8 vehicles).
:::

## NMS without NMS: the queries talk

```{figure} ../_static/figures/DETR_Duplicates_By_Layer.png
:alt: Duplicate pairs falling over six decoder layers on eight frames; beside it, query 55's attention on the cells of one car.
:width: 100%

Duplicates fade as the queries read each other, and the winning query spends 54% of its reading on its own car. Photo: Michael Rivera, CC BY 4.0 (Wikimedia Commons).
```

In every decoder layer the queries read each other (self-attention) before they read the image, so a
query can see another claiming a car and back off. Count the pairs NMS would delete (same-class
confident answers overlapping at IoU above 0.5): on Jacksonville 27 at layer 1 fall to 3 at layer 6, on
I-95 in Miami 19 to 2, and the other six frames have the same shape. On COCO the paper finds NMS helps
the first decoder layer and slightly hurts the last. Each answer reads its own object: 126 small
vehicles covering under 1% of the grid (median 0.6%) get a median 52% of their query's last-layer
cross-attention (compare the ViT maps of {doc}`2.7 <notes7-vision>`).

What survives matters for counts. The queries settle duplicates within a class far better than across
classes: where the line between two COCO classes is blurry, one SUV can be claimed as "car" by one query
and "truck" by another. Jacksonville keeps 8 such pairs at layer 6, which class-wise NMS would not
remove either. On the early-1970s Shirley Highway frame at dusk, same-class duplicates fall from 17 to
2, but pairs of any class are 17 at layer 1 and still 17 at layer 6.

(detr-query-zones)=
## Each query learns a zone

On 1,000 fresh scenes the synthetic-road DETR's 16 queries split the road four per lane, each owning a
stretch, with 97% of a query's answers in its most frequent lane (about 25% with no preference), just as
the real DETR's queries kept to their places on FL511. So **capacity is per zone, not per frame.** Queue
8 cars in one lane and recall is 26.5%; spread the same 8 two per lane and it is 99.6% (200 scenes
each). Random training scenes almost never packed one lane that tightly, which is the lesson: a
queue-length detector must be trained on full, spilling-back queues.

Spend your time in three places in the companion. **2 &middot; 100 questions**: slide the score
threshold, then switch to *Faster R-CNN: raw boxes* and *after NMS*. **4 &middot; Inside the decoder**:
step the layers and watch the duplicates go; click a box for its cross-attention map. **5 &middot; Train
one yourself**: the mini-DETR was trained offline and runs live in your browser; nothing trains there,
but every box is computed in front of you. Drag vehicles, add trucks, press *Queue 8 cars in one lane*.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion &mdash; How DETR detects: 100 learned questions, one answer per vehicle</span>
    <a href="../_static/companions/DETR_Companion.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/DETR_Companion.html"
          title="How DETR detects: 100 learned questions, one answer per vehicle" loading="lazy"></iframe>
</div>

:::{admonition} Before you trust this result
:class: warning
**What is the baseline?** For duplicates, class-wise NMS at IoU 0.5: each pair counted is one it would
delete. For zones, the same 8 cars spread two per lane.

**How was the data split, and why is that honest?** Duplicates: eight unlabelled photographs, so counts,
not accuracy. Zones: synthetic road scenes fresh from the generator, silent about real cameras.

**What does it do on the ugly cases?** Car/truck double claims survive to layer 6, and class-wise NMS
would not catch them; a full lane queue drops recall to 26.5%.
:::

(detr-limits)=
## Where DETR breaks

**The ceiling.** Tile the Jacksonville frame 1, 4, 9 and 16 times, same picture, same scale. DETR names
29, 79, 92, then 91, flat below its 100 queries; more queries means retraining. Faster R-CNN names 209
at its default 1,000 proposals and 316 with the budget scaled, a setting, not retraining. **Small
vehicles.** In the parking lot DETR names 37 vehicles to Faster R-CNN's 78, and almost the whole gap is
vehicles under 40 px tall, 3 against 45. Miami is the exception: 32 against 56, but 0 against 5 under 40
px. DETR reads one grid at stride 32; Faster R-CNN's feature pyramid reads maps up to 8 times finer. On
COCO the paper reports the same AP as its Faster R-CNN-FPN+ baseline, 42.0, but 20.5 against 26.6 on
small objects and 61.1 against 53.4 on large. **Training cost.** 500 epochs on COCO. Running is fine: 3.05 s against 4.12 s per 1333 &times;
750 frame on 2 CPU threads, 83% of DETR's time in the ResNet-50.

:::{admonition} Before you trust this result
:class: warning
**What is the baseline?** Faster R-CNN R50-FPN, same backbone and resize; in the tiling test also with
its proposal budget raised.

**How was the data split, and why is that honest?** No labels on these photographs, so counts, not
accuracy; the COCO numbers are the paper's.

**What does it do on the ugly cases?** Tiling a large frame is the usual workaround, at the cost of
vehicles cut by tile edges. Night, occluded queues and car/truck confusion are not measured here.
:::

## What DETR started

What lasted is not the box but learned queries, trained with set matching, each claiming one thing.
**The fixes:** *Deformable DETR* (ICLR 2021), each query reads a few sampled points on several scales:
better on small objects, 10&times; fewer epochs. *RT-DETR* (CVPR 2024): 53.1 AP on COCO at 108 FPS on a
T4 GPU, no NMS. *RF-DETR* (Roboflow, 2025): a DINOv2 backbone under a real-time DETR. *YOLOv10* (NeurIPS
2024) trains one-to-many and one-to-one heads and deploys the NMS-free one. **Queries beyond boxes:**
*MOTR* (ECCV 2022), a track query follows one vehicle across frames; *MapTR* (ICLR 2023), a query
answers with one lane divider or crosswalk; *BEVFormer* (ECCV 2022), bird's-eye grid queries read six
cameras; *Grounding DINO* (ECCV 2024), a text prompt such as "downed signal head" steers the queries;
52.5 AP zero-shot on COCO.

(query-designs)=
## Your problem, your queries

```{figure} ../_static/figures/DETR_Query_Design.png
:alt: Tokens Z and queries X meet in cross-attention; a decision on whether answers have fixed identities leads to assigned queries or free queries with matching.
:width: 100%

What you observe answers, what you want answered asks, and one question decides between assigned queries and free queries with matching.
```

The design move works far beyond cameras. What you observe becomes tokens $Z$: camera cells, detector
readings in 5-minute cells, narrative words, CAN signals. What you want answered becomes queries $X$,
**one query per answer**; each reads the observations and a small head turns it into its answer. To the
three questions of {doc}`2.6 <notes6-architecture>` (what is a token, what may attend to what, what does
position mean), add a fourth: *what is one answer?*

Then one decision: **do the answers have fixed identities?** If yes (the 12 turning movements at an
intersection, every link of a corridor, every map cell), give each an *assigned* query with its position
built in, trained against its own label, with no matching, as BEVFormer's grid cells are. If the answers
are only a count you cannot know in advance (vehicles, incidents, platoons), use DETR's recipe: more
*free* queries than you will ever need, Hungarian matching, and &empty; for the spares.

**Four query designs for mobility.** Design proposals, not results: check the literature before you
build one.

| Problem | Tokens $Z$ | Queries $X$ | One answer | Labels from | Baseline today |
|---|---|---|---|---|---|
| Vehicles in a crash report | narrative words + diagram patches | 8 free, matched | one unit: role, maneuver, direction, point of impact, or &empty; | the report's coded vehicle fields | analyst coding |
| Incidents on a freeway corridor | detector station &times; 5-min cells + 511 event text | 10 free, matched | milepost, start, end, type, or &empty; | agency incident logs | California algorithm + operator reports |
| Turning movements at a signal | camera cells over one cycle | 12 assigned movements | vehicles per movement per cycle | manual counts | video detection zones |
| Link speeds on a CCTV corridor | cells from every camera on the corridor | one assigned per link | speed or density on that link | probe speeds or detectors | the probe-speed feed |

Read the last two columns first. **The catch is labels:** a set loss needs a labelled set for every
training example, and COCO's cover about 1.5 million hand-drawn object instances. If you cannot fill in
where your labels come from and what the agency does today, the architecture does not matter.

:::{admonition} Fit card &mdash; DETR (set-prediction detection)
:class: tip
**Idea in one sentence.** 100 learned queries read a CNN-plus-transformer encoding of the frame, and matching trains each object to one query, so no NMS.

**Why it works.** One-to-one matching punishes a second answer; the queries see each other in every decoder layer and back off.

**Fits these tasks.** Counting and locating where duplicates cost (turning-movement, pedestrian counts); set outputs beyond boxes (*extraction*, *classification*).

**Needs this data.** Frames with box labels, hundreds to thousands to fine-tune from COCO weights; a GPU to train.

**Breaks when.** More objects than queries; vehicles under about 40 px; little training compute; car/truck overlap.

**Keep the classical method when.** A loop or video detection zone already counts well; CPU-only edge latency; a YOLO model meets the target.
:::

## Applications: where the bar is set today

| Domain | Task | Data | Classical baseline |
|---|---|---|---|
| Traffic operations | turning-movement and queue counts (*extraction*) | CCTV, a few hundred labelled frames per view | manual counts; video detection zones |
| Road safety | pedestrians and cyclists for near-miss (TTC, PET) studies (*extraction*) | intersection or drone video, hand-checked tracks | manual conflict observation |
| Drones, air mobility | parking occupancy from aerial images (*extraction*) | drone tiles, many labelled vehicles each | manual counts; Faster R-CNN on tiles |
| Agencies | post-storm inventory: downed signs, signal heads, debris (*classification*) | patrol-vehicle imagery, few labels per class | windshield survey; open-vocabulary triage + review |

The last column is the bar. In the drone row the ceiling bites: tile the image, or pick a detector
without one. In the agency row try open-vocabulary detection first; you will never have COCO-sized
labels for downed signal heads.

:::{admonition} Before you trust this result
:class: warning
**What is the baseline?** A same-size detector trained the classical way (Faster R-CNN, or a YOLO-family
model with NMS), plus what the agency does today: a loop count, a manual video count.

**How was the data split, and why is that honest?** By camera and time of day, never by random frame:
neighbouring frames of one video are nearly identical, and a random split leaks them into the test set.

**What does it do on the ugly cases?** More objects than queries; vehicles under 40 px; night; occluded
queues, where learned suppression and an IoU threshold are both guessing; vehicles with two names
(pickup, SUV, van).
:::

## Check yourself

1. A county wants to count occupied spaces in a 600-space park-and-ride from one drone photograph, and a
   vendor offers a DETR-based counter. What do you ask before buying, and how would you change the setup
   to stay under the query ceiling?
2. Your camera feeds a tracker that counts turning movements at a left-turn bay with a 10-vehicle queue.
   Which DETR behaviour worries you more, duplicates or misses, and how would you test it with 2 hours
   of video?
3. The county also has a stall map of the lot and wants occupancy per stall. Free queries with matching,
   or assigned queries? What does each query carry, and is the 100-query ceiling still a problem?

---

Next: {doc}`notes11-streams` &mdash; from one camera to every sensor at an intersection: who reads whom.
