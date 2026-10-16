# 2.11 Many streams, one intersection

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 2 &middot; Section 2.11</span>
    <span class="notes-card-session">Session: Oct 15</span>
  </div>
  <p class="notes-card-lede">In 2.9 one sequence asked and one answered. A signalized intersection has four streams &mdash; camera, loops, probe-vehicle CAN and connected-vehicle messages &mdash; each with its own rate, clock and map, and which should ask depends on the task. This section starts with a model that reads synthetic camera and CAN clips to write a crash warning, then works out what encoders hand over, how streams line up and who reads whom. The answer is a graph.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Interactive companion on this page</h4>
      <ul>
      <li><a href="../_static/companions/Multimodal_Cross_Attention_Companion.html" target="_blank" rel="noopener">Camera, CAN and cross-attention &#8599;</a></li>
      </ul>
    </div>
    <div>
      <h4>Notebooks that go with it</h4>
      <ul>
      <li><a href="../module7/lab5_graph_attention.html">Lab 5 &mdash; Attention on a road network</a></li>
      <li>Cross-attention sanity check &mdash; <em>in development</em></li>
      </ul>
    </div>
  </div>
</div>

## What this section covers

- A camera-plus-CAN model, trained in three stages on synthetic clips, that writes a crash warning, against radar time-to-collision
- What an encoder must hand over, and why a CSV of CAN data is not language
- Four streams, four clocks: every token stamped with when, where and how sure, because a stale position is a wrong position
- Who reads whom: blocks masked, gated or off; a null token; a hub that keeps the cost linear
- Lane &times; distance anchors, sized like the cell transmission model's cells and joined by typed edges

(two-sensors)=
## Two sensors, one sentence

A car already records a forward camera and a CAN bus carrying speed, pedals, wheel speeds and the ACC
radar's range to the car ahead. The companion trains a 348,290-parameter multimodal language model, on
the Flamingo recipe, to read 2 seconds of both and write one line such as *lead vehicle braking .
driver not braking . collision in 2 s*. The clips are **synthetic** on purpose, since no public dataset
has real crashes with synchronized video and CAN: IDM following plus a reaction time and a
friction-limited deceleration $a \le \mu g$, in five scenarios that put the evidence in different
sensors. The price is a 48 &times; 48-pixel cartoon camera and a model that learns this simulator, not
real roads.

**The words ask, the sensors answer.** Each word's query takes one softmax over 128 video patches and
8 CAN windows. A Kalman filter fuses radar and camera with weights fixed by noise covariances; here
the weights change with every word, so *wheels* can lean on the CAN window where ABS kicked in and
*cutting* on the frames where a car crosses the lane line.

Training runs in three stages. Stage 1 trains the language model alone and is fluent and useless: it
writes *lead vehicle braking . driver not braking . no conflict* for 100.0% of the 3,000 test clips,
as a large LLM would with a crash question and no image. Stage 2 freezes it and trains the encoders
and cross-attention behind Flamingo's gate, which starts closed; exact-sentence accuracy goes from
8.9% to 86.3%. Stage 3 unfreezes everything: 87.0%.

Then two measurements disagree. CAN is 5.9% of the tokens, yet *stopped* puts 91.3% of its
cross-attention there and *wheels* 82.2%, while *cutting* puts 9.2% there and reads the video.
But retrained without video, the CAN-only model writes 83.7% of reports exactly right (87.0% with
both) and catches 88.6% of collisions (86.8%), because the radar's range travels on CAN; the
camera mainly cuts false alarms, from 188 to 109. **Where a word looks does not prove it needs that
sensor.** Mask CAN at run time and the reports stay fluent, but only 35.1% of collisions are caught,
about half what a video-only model manages (69.6%); mask the video instead and only 0.1% of outputs
are even well-formed sentences, although CAN alone was almost enough. Without modality dropout, a
fused model does not fall back on the sensor it still has.

On these synthetic clips, the classical baseline is radar time-to-collision with an alarm below 3.5 s,
tuned on the validation clips. F1 is 86.6% against 61.1%; for collisions within 1 s the model catches
92.6% against 51.8%, and on cut-ins 89.3% against 30.2%. But TTC catches more collisions with a stopped car ahead (97.5% against 91.7%, with 105 false
alarms against 14), needs no training data, cannot hallucinate, and fails in ways you can write down.

Spend your time in three places. In **tab 4**, click *wheels* in a low_friction clip and *cutting* in
a cut_in clip, and watch the weight move between CAN and video. **Tab 5** sets those shares beside the
delete-a-sensor table. **Tab 6** splits recall by seconds to impact and by scenario against radar TTC:
decide whether this model belongs in the warning loop or behind it.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion &mdash; Camera, CAN and cross-attention</span>
    <a href="../_static/companions/Multimodal_Cross_Attention_Companion.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/Multimodal_Cross_Attention_Companion.html"
          title="Camera, CAN and cross-attention: training a model that writes a crash warning" loading="lazy"></iframe>
</div>

:::{admonition} Fit card &mdash; Multimodal language model for vehicle data
:class: tip
**Idea in one sentence.** Encode each sensor into tokens; a language model reads them through cross-attention while it writes.

**Why it works.** The weights depend on the query, so fusion is decided per word; the staged recipe reuses a pretrained language model.

**Fits these tasks.** Triaging harsh-braking events, explaining an AEB activation, drafting a crash narrative from recorder data and video (*generation*, *extraction*, *classification*).

**Needs this data.** Synchronized video and CAN; analyst-checked sentences; thousands of clips.

**Breaks when.** Sensors drift out of sync; the camera or CAN DBC changes; events are rarer than in training; the text is confident about what it did not see.

**Keep the classical method when.** The decision is one alarm with a hard deadline: radar TTC is transparent, certifiable and fast. Put the language model behind it, for triage.
:::

:::{admonition} Before you trust this result
:class: warning
**What is the baseline?** Radar TTC with a tuned threshold on the same clips, and the stage-1 model with no sensors: what fluency alone is worth.

**How was the data split, and why is that honest?** Different simulator seeds, so no trajectory is in two sets; but one simulator and one camera, so it says nothing about real roads.

**What does it do on the ugly cases?** The simulator has no rain, night or occlusion; some misses are irreducible because the reaction has not happened yet; and a sentence can be fluent and wrong.
:::

(encoder-handover)=
## What the encoders must hand over

Must the two sides match? Take *Is the right lane blocked?* from BERT-base, 6 tokens of 768 numbers,
and a ViT-L/16 image, 196 patches of 1,024. Neither pair has to agree; only the query and key widths
must, 64 per head, because their dot product is taken. The output has the asker's length and is
**added** to the words ($h \leftarrow h + Z$), not substituted. Same length? No. Same key width? Yes.

```{figure} ../_static/figures/XEnc_Handover.png
:alt: Three panels: words reading one pooled vector all get the same answer; shuffled patches give the same output; word2vec gives "right" one vector, a transformer two.
:width: 100%

Cross-attention can only retrieve what the encoder already wrote into each token: a sequence rather than a summary, its position, and its context.
```

**Cross-attention retrieves; it never creates.** Hand over one pooled vector and the softmax over one
key is 1.0 for every word, so all six get the same answer. Hand over tokens without position and
nothing recovers it: shuffling the 196 patches changes the output by about
3 &times; 10<sup>&minus;16</sup>, rounding. For text and images, freeze strong pretrained encoders and
train only the bridge, but CLIP-style encoders are weak on orientation, counts and relative position
(Tong et al., 2024), exactly what *which lane?* asks.

Token counts are two dials, not a balance. The output sets the queries (6 words, 100 DETR object
queries, 40,000 bird's-eye cells); the smallest thing the task must see sets the keys (196 patches for
a ViT at 224 pixels, 576 for LLaVA at 336, and 11,520 for ten seconds of dashcam at 2 frames per second
and 576 tokens a frame). The cost is the product; the usual fix is itself cross-attention, as
Flamingo's 64 learned queries read every patch and hand on only 64.

Traffic data that arrives as text is not language. Through the GPT-4o tokenizer one CAN row is 22
tokens; a speed of 65.37 becomes *65*, *.*, *37*, and 65.38 ends in an unrelated ID. One synthetic
minute at 10 Hz is 13,799 tokens as text against 120 half-second patches. Removing the language model
from three LLM-based forecasters held or improved their accuracy (Tan et al., 2024). Text tokens are
the right call when the data really are symbols, such as CAN message IDs, signal event logs or incident
codes; for numbers, bin the values into a vocabulary (Chronos) rather than spelling out digits.

**One token is the smallest thing you would want to look up:** half a second of all CAN signals, one
detector's recent history, one connected vehicle's last few seconds. Feed numbers in as numbers;
stamp every token with time, sensor, place and modality, on one clock and one map, in metres; mark
missing as missing, never zero, because 0 mph is a jam; probe the encoder alone before fusing.
Identity carries a lot: a plain MLP with *which sensor, what time, which day* embeddings rivalled
complex spatio-temporal graph networks (STID). There is no CLIP for traffic yet.

:::{admonition} Before you trust this result
:class: warning
**What is the baseline?** Half-second patches of the same six signals over the same minute.

**How was the data split, and why is that honest?** No split: these are tokenizer counts, not accuracies, so nothing can leak.

**What does it do on the ugly cases?** More signals or a faster bus grow both counts; the ratio is this log's, not a law of CAN.
:::

(sensors-to-tokens)=
## Four streams, four clocks

The rest of this section uses an **example intersection, a stated synthetic configuration**: four
approaches, each with a 64 m left-turn bay and two through lanes; two exit lanes per leg; free-flow
35 mph; one camera; stop-bar loops in every entry lane, advance loops in every through lane; 10 probe
vehicles reporting CAN; 30 vehicles sending basic safety messages (BSMs). The model updates once a
second and reads the last 2 s.

Every reading must answer when, where and how sure. Rates differ &mdash; camera 25 frames per second,
BSMs about 10 Hz, CAN IDs on their own cycles, loop events at 0.1 s &mdash; but clocks are the
dangerous difference: a BSM's time is specified as UTC within &plusmn;1 ms, a CAN frame carries no
time at all, a controller is only as right as its last sync. And trust: PeMS's user-guide example station was 41%
observed, the rest imputed and indistinguishable unless the token says so.

Each stream gets its own encoder. **Video** tokens can be patches (about 8,000 for a full-HD frame),
placed in the image but not on the road; ground cells in metres; or one token per tracked road user,
compact but blind to a missed pedestrian. **BSMs** are nearly tokens: convert position to metres from
the MAP reference point, keep the accuracy (the proposed federal rule asks for 1.5 m), and stitch
tracks across the temporary ID, which changes about every 5 minutes. **CAN** is decoded with a DBC
file, each signal's last value held on one grid with a freshness flag; beware, ego status alone
matched the best open-loop planners on nuScenes (Zhai et al., 2023). **Loops** come from the
controller's event log, one token per detector per cycle as in ATSPMs; a freeway's 5-minute bin
carries an imputed flag and its age, since the newest complete bin describes traffic about 300 s old.
How a history becomes one vector: {doc}`2.12 <notes12-history>`.

**Stamp time where it is measured,** not where it arrives. DAIR-V2X pairs a vehicle frame and a
roadside frame only if they are within 10 ms (30 ms relaxed), and priced the lag: roadside lidar one
or two frames older, about 100 or 200 ms, cut late-fusion 3D detection from 41.90 to 40.21 and 35.29 AP. A controller clock 2 s fast is worse
than noise: the model learns the offset as behaviour and breaks the day someone fixes it.

```{figure} ../_static/figures/STT_Stale_Position.png
:alt: Position error against BSM age on synthetic tracks, log scale: used as received, the median error crosses the 1.5 m accuracy line within 0.2 s and reaches 13.49 m at 1 s; moved forward by speed, and by speed and acceleration, the medians stay between 0.01 and 0.33 m.
:width: 100%

A BSM used as it arrived is metres wrong within a few tenths of a second; carried forward by its own speed and acceleration, it is a few centimetres off at 0.3 s and under 40 cm (95th percentile) a full second old (synthetic car-following tracks, no GNSS error).
```

At 35 mph a vehicle covers 1.56 m in 100 ms: the whole 1.5 m position budget, spent on latency. Carry
each message to the update time with its own kinematics:

$$\hat{x}(t_0) = x_m + v_m\,\Delta + \tfrac{1}{2}\,a_m\,\Delta^2, \qquad \Delta = t_0 - t_m$$

$t_m$ is when the BSM was measured (its secMark field), $t_0$ the model's update time, $x_m$ the
position along the lane at $t_m$ in metres, and $v_m$, $a_m$ the speed and acceleration the message
reports. **In words:** a position is true only when it was measured; move it to now. On synthetic IDM
tracks without GNSS error, a message 0.3 s old is off by a median 4.04 m as received and 0.02 m
corrected. Turns, stops and hard braking make real errors larger, but correcting costs far less than
the budget, and ignoring age far more. What is left goes in as data: every token keeps its age, and
anything not yet arrived is masked.

Space is the other half: a homography maps camera pixels to a flat road (a camera bumped by wind
silently moves every token), BSMs and probes become metres from the MAP reference point, and loops
come from the detector plan. One update then holds 874 tokens &mdash; 784 patches from 4
sampled frames, 20 loops, 40 CAN patches from 10 probes, 30 BSM tracks built from 600 messages &mdash;
each with a different age.

:::{admonition} Fit card &mdash; Your own traffic-stream encoders, aligned
:class: tip
**Idea in one sentence.** Each stream becomes a short token sequence from its own encoder, every token stamped with when, where and how sure.

**Why it works.** Attention can only match what is comparable; one clock and one map make "same moment, same lane" easy to find.

**Fits these tasks.** Crash warning, queue and spillback detection, detector health, travel time (*prediction*, *classification*, *retrieval*).

**Needs this data.** Months of unlabelled logs; synced clocks; MAP geometry, detector plans, camera calibration; a few labelled events.

**Breaks when.** Clocks drift, a camera moves, IDs rotate, imputed values pass as real, or one stream becomes a shortcut.

**Keep the classical method when.** One sensor already answers it: an ATSPM split-failure count, a detector incident algorithm, a TTC threshold.
:::

:::{admonition} Before you trust this result
:class: warning
**What is the baseline?** The same model on perfectly synced streams, and each stream alone.

**How was the data split, and why is that honest?** By intersection and by day, never by window: neighbouring windows share almost everything.

**What does it do on the ugly cases?** Build them, as DAIR-V2X did: inject clock offsets, drop a stream, rotate the IDs, and measure what breaks.
:::

(who-reads-whom)=
## Who reads whom

Signal timing needs one answer per phase, a crash warning one per vehicle, detector health one per
loop: three askers of the same streams. Write them as an asks-by-answers table. 2.9's
translator has four blocks with three on (English never reads Spanish); four streams have sixteen,
four on the diagonal and twelve cross-stream. Early fusion switches on all sixteen, a single
cross-attention one. Every design is a choice of blocks.

```{figure} ../_static/figures/FFus_Block_Types.png
:alt: A four-by-four asks-by-answers table of video, loops, CAN and BSMs, each block marked self, gate, mask or off; inside one block, each loop reads only the patches over its lane.
:width: 100%

Each block is masked (physics decides), gated (the data decide, sample by sample), both, or off.
```

A **mask** carries engineering knowledge: a loop in lane 3 cannot see lane 5. A **gate** carries what
you cannot decide in advance: the camera is the best queue sensor at noon, the loops at night in rain.
**Off**, like a missing graph edge, claims a block carries nothing. All of it needs stamps &mdash;
which stream, when, where &mdash; so that lane 3's loop and lane 3's patches share a place code instead
of the model learning camera calibration from the task loss. The equation is 2.9's cross-attention
with two additions:

$$h_i \leftarrow h_i + g_i \sum_j \text{softmax}_j\!\left(\frac{q_i \cdot k_j}{\sqrt{d}} + M_{ij}\right) v_j$$

$i$ is one asking token (the stop-bar loop in lane 3), $j$ every answering token, $q$, $k$, $v$ the
question, advertisement and answer, $d$ the numbers per head. $M_{ij}$ is 0 if $i$ may read $j$ and
$-\infty$ if the geometry says no, like the look-back mask; $g_i$ is a gate from 0 to 1 computed from
$i$'s own context, open for one sample and shut for the next. **In words:** score every allowed token,
average what comes back, then decide how much to add. In a toy case with three patches over the
query's lane and three over the opposing approach, 0.49 of the weight goes the wrong way without the
mask; with it, the own-lane patches get 0.60, 0.27 and 0.13.

```{figure} ../_static/figures/FFus_Read_Nothing.png
:alt: Three toy panels: four BSMs share all the weight about equally; with a null key the null takes 0.72; a gate of 0.05 scales the whole block's output.
:width: 100%

Softmax must spend all its weight somewhere; a null key with value zero, or a gate, lets a query read almost nothing.
```

**Let a query read nothing.** A multinomial logit's probabilities add to one: leave out the no-travel
option and everyone must go somewhere. A query facing four useless BSMs likewise spends all its
weight, about a quarter each. The fix is the opt-out alternative, a learned null key with value zero:
with a toy null score of 2.5 it takes 0.72, leaving 0.28. Models invent one when given none: 2.9's
translator parked 0.09 to 0.32 of each Spanish word's row on the end mark.

:::{admonition} Going deeper &mdash; why softmax can't abstain
:class: dropdown
With a null key of learned score $s_0$, the share of a query's weight that reaches the real keys is

$$\text{share on real keys} = \frac{\sum_j e^{s_j}}{e^{s_0} + \sum_j e^{s_j}}$$

If every real score is far below $s_0$, the share goes to zero; without the null it is always exactly
one. The null scales every real key's weight by the same factor, so their ratios are unchanged: the
keys decide how much is read, where a gate decides from the query's side. (BERT's [SEP] habit: Clark
et al., 2019.)
:::

**Many patches drown a few loops.** Of the 874 tokens, 784 are patches. In one pool before training,
shares follow token counts, 0.88 to the camera and 0.03 to the loops (measured, random weights); a
two-level softmax, within each stream and then across streams plus "none", starts every stream at 0.2.
**A hub keeps the cost linear.** One pool costs 874 &times; 874 = 763,876 scores per head per layer,
0.80 of them the camera reading itself. The learned-query family &mdash; DETR's object queries,
BEVFormer's grid cells, the Perceiver's latents &mdash; lets a fixed set of anchors read every stream
and each other instead.

```{figure} ../_static/figures/FFus_Hub.png
:alt: 784 video, 20 loop, 40 CAN and 30 BSM tokens feed 116 anchor tokens, which task queries ask.
:width: 100%

In the fusion layers 116 anchors read the 874 sensor tokens and each other, and each task brings its own queries.
```

That costs 114,840 scores per head per fusion layer, about 6.7 times fewer. The saving is in the fusion
layers only: there the patches stop reading each other, but each stream's own encoder runs in both
designs. Who asks the anchors follows one rule: **the query side is whatever your output is indexed by.**

| Task | One answer per | Asks | Answers |
|---|---|---|---|
| Signal timing | phase | one query per phase | the lane anchors it serves |
| Crash warning | vehicle, every update | one query per vehicle, from its CAN tokens | neighbours' BSMs, nearby anchors |
| Detector health | loop | each loop's token | the patches over its lane, not the anchors |

Two rows go around the hub: a crash warning also reads the neighbours' BSMs directly, because it needs
detail a 16-metre cell blurs, and detector health must not ask anchors that already hold the loop's
own reading. Plan for two more failures: the video gate may never open when brake pressure already
predicts the crash (the greedy-modality problem), and streams do go missing, so train with whole
streams dropped at random (ModDrop).

:::{admonition} Fit card &mdash; One pool, masks and gates
:class: tip
**Idea in one sentence.** Put every stream's tokens in one pool and decide, block by block, who may read whom.

**Why it works.** Physics sets the masks; gates and a null token let each query skip a stream, sample by sample.

**Fits these tasks.** Camera, loops, CAN and V2X at one site: queues, warnings, detector checks (*prediction*, *classification*).

**Needs this data.** Streams on one clock and one map; task labels; days with each stream missing, real or simulated.

**Breaks when.** Clocks drift; one stream is a shortcut; a big stream drowns small ones; the pool's cost grows with its square.

**Keep the classical method when.** Detector-based queue estimates or actuated control already work; fuse only when no single sensor can answer.
:::

:::{admonition} Before you trust this result
:class: warning
**What is the baseline?** The best single stream, and late fusion of per-stream models; fusion that beats neither is not earning its cost.

**How was the data split, and why is that honest?** Whole days and intersections held out, never random seconds, which are near-copies of their neighbours.

**What does it do on the ugly cases?** Test night, rain, failed loops, low connected-vehicle penetration, and blanked camera tokens: if the score holds, the camera is unused.
:::

(lane-anchor-hub)=
## The lane-anchor hub

What should the anchors be? DETR's free queries suit objects that can be anywhere; lanes are known in
advance. Tied to the road, an anchor has a physical meaning, sensors can be masked to it, and the
design transfers between intersections.

```{figure} ../_static/figures/FFus_Lane_Anchors.png
:alt: The eastbound approach cut into 16 m lane cells and four bay cells, with loops in specific cells, a camera region, and conflict-zone, exit-lane and crosswalk tokens.
:width: 100%

Entry lanes cut into lane &times; distance cells (96), plus one token per exit lane (8), conflict zone (8) and crosswalk (4): 116 anchors.
```

Through lanes are cut into ten 16 m cells over a 160 m approach, the 64 m bay into four. Phases are
read-outs, not anchors: a protected-permissive left lane is served by two phases, so a phase is a
query pooling the lanes it serves. With cells rather than one anchor per lane, queue length is a count
of occupied cells. How long should a cell be? Daganzo sized the **cell transmission model**'s cells so
a vehicle at free-flow speed crosses at most one per time step. Anchors face the same problem with
news, which moves one cell per round of anchor attention when anchors read only their neighbours:

$$\Delta x \ge \frac{v_f\,\Delta t}{L}$$

$\Delta x$ is the cell length (m), $v_f$ the free-flow speed (m/s), $\Delta t$ the time between updates
(s), $L$ the rounds of anchor-to-anchor attention per update. **In words:** cells must be long enough
that $L$ rounds of news keep up with a vehicle at free-flow speed. At 35 mph, 15.6 m/s, one update a
second and one round, cells need at least 15.6 m (two rounds allow 7.8 m); the example uses 16 m. At a
measured 40 mph the bound is 17.9 m, and 16 m cells then need two rounds. It binds only where no sensor
sees.

Each anchor starts every update from *who it is*, built from attributes (position, distance to the
stop bar, allowed movements, signal group, detectors), never a bare ID that fits one intersection
only; *what the signal is doing*, from SPaT, whose end times under actuated control are
bounds, not promises; and *what it remembers*, its own last vector, so a queue hidden behind a bus
does not vanish. Each stream reads through its own mask: the camera via cell outlines projected into
the image, loops via the detector layout plan, BSMs and CAN via positions matched to cells every
update, where an empty cell means no equipped vehicle, not no traffic.

```{figure} ../_static/figures/FFus_Anchor_Edges.png
:alt: Eastbound through and bay cells as nodes, linked by along-lane, across-lane, entry-to-exit, conflict and concurrent-phase edges.
:width: 100%

Five edge types among anchors, each a claim about how traffic moves.
```

Along the lane a queue grows backwards, a shockwave; across lanes, a left-turn queue spills from the
bay into the through lane; a full exit lane stops the discharge. With 116 anchors all pairs is only
13,456 scores per head, so edges need not save compute; they carry theory. Add one learned number per
edge type per head to the score, $\text{softmax}_j\big(q_i \cdot k_j/\sqrt{d} + b_{\text{type}(i,j)}\big)$,
started positive for along the lane and negative for no relation; a mask is the case $b = -\infty$.
The model can still learn a relation you did not draw, and the CTM rule becomes a sizing guide.

:::{admonition} Fit card &mdash; Lane-anchor hub
:class: tip
**Idea in one sentence.** A fixed set of lane-cell tokens reads every stream, talks along the lane graph, and answers each task's queries.

**Why it works.** Every stream meets in one physical frame; cost grows with anchors &times; tokens.

**Fits these tasks.** Queue and spillback estimates, phase timing, warnings, camera health (*prediction*, *classification*).

**Needs this data.** A MAP-style lane map, the detector layout plan, camera calibration, synced clocks; labels per task.

**Breaks when.** The map is out of date (a work zone, a restriping); cells are too short for the update rate; a camera moves.

**Keep the classical method when.** Detector-based queue estimates and actuated control meet the need, or the CTM itself does the job.
:::

The anchors are now nodes of different kinds joined by edges of different kinds, with attention on
each edge: a heterogeneous graph with graph attention. That is where {doc}`Module 7 <../module7/notes>`
picks up in {ref}`graph neural networks <graph-neural-networks>`, starting from the cell transmission
model, and where {doc}`Lab 5 <../module7/lab5_graph_attention>` puts attention on a road network. How
a stream's history becomes one token, with a GRU or a temporal transformer, is
{doc}`2.12 <notes12-history>`.

## Check yourself

1. Your agency wants an in-vehicle warning 2 s before rear-end crashes. Using the companion's comparison with radar TTC, argue for or against putting the multimodal model in the warning loop, and say what belongs there instead.
2. A fused queue model works at its training intersection and fails at the next one down the corridor. Name two design choices from this section that could cause it, and a test that would catch each.
3. A colleague proposes one anchor per lane, 32 instead of 116, "to save compute". The camera's own encoder spends 153,664 attention scores per head per layer on its four frames each update. Is compute a good reason? What do you lose?

---

Next: {doc}`notes12-history` &mdash; where the past enters: three paths into cross-attention.
