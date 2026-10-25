# 2.12 Where history enters

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 2 &middot; Section 2.12</span>
    <span class="notes-card-session">Session: ViT extensions and fusion</span>
  </div>
  <p class="notes-card-lede">A driver, or an operator in a traffic management center, never fuses only the present: each carries what happened over the last minutes. This section shows the three places a model can carry the past into cross-attention &mdash; baked into each stream's token, kept as keys and values the current query can search, or carried as a memory rewritten every second &mdash; starting from the recurrent network you know and ending at a learned gate that rediscovers the Kalman gain.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Read it first</h4>
      <ul>
      <li><a href="notes11-streams.html">2.11 Many streams, one intersection</a></li>
      <li><a href="notes3-attention.html">2.3 Attention: the mechanism</a></li>
      </ul>
    </div>
    <div>
      <h4>Where it leads</h4>
      <ul>
      <li><a href="notes13-evaluation.html">2.13 Does it earn its keep?</a></li>
      <li><a href="../module3/notes1-gnn.html">3.1 One view of every network: graph neural networks</a></li>
      </ul>
    </div>
  </div>
</div>

## What this section covers

- Why history matters when what a sensor sees now is not the whole traffic state
- The GRU: exponential smoothing with a learned dial; five ways to turn a BSM track into one token
- The temporal transformer, why the field moved to it, and where the GRU stays
- History as keys and values: a query that finds the past moments it needs
- A carried memory written with attention and kept with a gate, and a learned Kalman gain
- Which path to use when, and how each one breaks

(three-paths)=
## Three places the past can enter

In traffic flow theory the density along a road is a complete state: know it everywhere and the past
adds nothing. No sensor gives you that: a stop-bar camera sees the first 8 queued vehicles, a loop one
point. History matters exactly as far as what you see now is not the whole state. When the
camera reads 8, its maximum, the queue could be 9 or 30, and only the last few minutes can say which:
the vehicles counted in and out since the end of the queue was last visible.

```{figure} ../_static/figures/HP_Three_Paths.png
:alt: A camera token queries cross-attention for the queue now, fed by a temporal transformer over the last 30 s, 300 s of age-tagged stored tokens, or four carried memory tokens.
:width: 100%

The past can enter before fusion (summarized into the token), during it (stored keys and values the query searches), or around it (a memory rewritten every second).
```

All three run below on one synthetic TMC question: how many vehicles are queued now, when the camera
sees only the first 8? Path 1 first needs a stream's history turned into one token; start with the
encoder you know.

(gru-history-token)=
## One history, one token: the GRU

A connected vehicle's last 3 s of basic safety messages are 30 messages of 5 numbers; cross-attention
wants one token of 768. ViT's patch embedding assumes inputs of one size, all present, all at once.
Traffic histories break all three: a vehicle that entered radio range 1.2 s ago has 12 messages, not
30; some BSMs never arrive; a roadside unit wants a fresh token after every message.

```{figure} ../_static/figures/GRU_Cell.png
:alt: Left, exponential smoothing as a one-unit recurrent network with a fixed alpha. Right, the GRU cell with the same blend, alpha replaced by an update gate computed from the new message and the old summary.
:width: 100%

A GRU keeps exponential smoothing's blend and replaces the analyst's fixed &alpha; with a logit recomputed for every number at every message.
```

Exponential smoothing is a one-unit recurrent network: the new estimate is $\alpha$ times the new
reading plus $1-\alpha$ times the old one, with $\alpha$ fixed by the analyst, say 0.3. For BSM speed no
single $\alpha$ is right: cruising wants heavy smoothing, brake onset wants new messages to take over.
The gated recurrent unit (GRU; Cho and colleagues, 2014) keeps the blend and lets the data set the dial:

$$
h_t = (1 - z_t)\odot h_{t-1} + z_t \odot \tilde{h}_t,
\qquad
z_t = \sigma\!\left(W_z x_t + U_z h_{t-1} + b_z\right)
$$

- $x_t$ &mdash; BSM $t$: speed, acceleration, position, time stamp, gap since the previous message
- $h_t$ &mdash; the summary of the vehicle's track after BSM $t$ (64 numbers here)
- $\tilde{h}_t$ &mdash; the candidate: what BSM $t$ alone suggests the summary should be
- $z_t$ &mdash; the *write share*, per number: 0 holds, 1 overwrites; a binary logit of the new message and the old summary
- $\odot$ &mdash; multiply number by number

**In words:** each new BSM nudges the summary, and a logit decides, number by number, how hard.
(PyTorch calls $z$ the share *kept*; here $z_t$ is the share written, so it lines up with $\alpha$.)

Trained on the synthetic tracks below, the GRU learned the policy you would want: in one test window its
average write share sat at 0.55 while the car still accelerated, peaked at 0.72 just 0.3 s after braking
began, and fell to 0.44 as the speed settled. Individual numbers' gates ranged from 0.01 to 1.00.

**The last state is the token.** The same cell reads message 1, then 2, up to 30; the final summary,
projected to 768, is the token. Keep the GRU small: 768 wide it has 1,785,600 weights; 128 wide plus a
projection, 150,912. Recurrent encoders were the default for years, from DCRNN (2018, a graph
convolution inside a GRU cell; graph networks are in {ref}`section 3.1 <graph-neural-networks>`) to Waymo's MultiPath++
(2022, LSTMs).

**Gaps and streaming: read only arrivals.** A fixed-slot encoder turns a lost message into a zero plus
a flag, and must learn that zero means lost. A GRU sees only arrivals, each with its gap,
and at a roadside unit each arriving BSM updates that vehicle's state in place: the state is the whole
memory. The price: steps run in order, and over hundreds of steps early messages fade.

### Five ways to turn a track into one token, head to head

Flatten gives every slot its own weights; a 1D CNN slides a window along the track; PointNet encodes
each message alone and keeps the maximum of each number; attention lets every message read every other;
the GRU reads in order. Data: **synthetic** tracks of a connected vehicle following a lead
vehicle under the Intelligent Driver Model, sampled at 10 Hz like a BSM stream, with noise. Task: from
the last 3 s, predict the speed 3 s later. **The lead vehicle is never shown.** Same head, same budget.

| encoder | a lost message is | no loss | 30% lost | hard braking |
|---|---|---|---|---|
| ridge regression, 5 hand features | &mdash; | 1.484 | 1.497 | 2.913 |
| flatten + Linear | zero + flag | 1.345 | 1.418 | 2.592 |
| 1D CNN | zero + flag | 1.312 | 1.372 | 2.529 |
| PointNet | left out; time as input | 1.356 | 1.384 | 2.669 |
| attention | masked out; time as input | 1.315 | 1.353 | 2.523 |
| plain RNN | left out; gap as input | 1.324 | 1.354 | 2.537 |
| GRU | left out; gap as input | 1.314 | 1.35 | 2.477 |

*Root-mean-square error, m/s, mean of 3 seeds over 5,075 test windows; hard braking: the 337 windows
where speed fell by more than 5 m/s in the next 3 s.*

The encoders land within 0.044 m/s of each other and cut ridge's error by 8.6% (PointNet) to 11.6% (1D
CNN): learning the encoder helps; which one barely matters. With 30% of messages lost, flatten's error
rose 5.4% and the CNN's 4.6%, against 2.7% for the GRU, 2.9% for attention and 2.1% for PointNet: in
relative terms, reading only arrivals pays (in absolute error the CNN, 1.372, still edges PointNet,
1.384). On hard braking every error nearly doubles, ridge's included: partly because those windows were
picked by their outcome, and partly because the cause, the vehicle in front, is not in this history.

:::{admonition} Fit card &mdash; Recurrent history encoder (GRU)
:class: tip
**Idea in one sentence.** Read a history one message at a time; the final gated summary is the token.

**Why it works.** A learned gate sets, per number, how much each message changes the summary: hold through noise, react to events.

**Fits these tasks.** Streaming BSM or CAN at a roadside unit or on an ECU; irregular, variable-length histories (*prediction*, *classification*).

**Needs this data.** Time-stamped messages with gaps kept, not filled; thousands of labelled windows; synced clocks.

**Breaks when.** Histories run to hundreds of steps (patch first); training must run in parallel; the answer is not in the history.

**Keep the classical method when.** A few hand features carry the signal (on the synthetic tracks, the best encoder beat ridge by only 11.6%), or the history is complete and fixed, like 12 five-minute loop bins: try an MLP first.
:::

:::{admonition} Before you trust this result
:class: warning
**What is the baseline?** Ridge on five hand-made features, 1.484 m/s; holding the current speed
scores 2.82, extrapolating the current acceleration 1.7.

**How was the data split, and why is that honest?** By drive, 230 / 35 / 35, so no window overlaps
across splits. Nothing was tuned per encoder, so gaps of a few thousandths are not a ranking.

**What does it do on the ugly cases?** On hard braking the GRU's error is 1.9 times its average; no
history encoder adds information that is not in the input.
:::

(temporal-transformer)=
## Did transformers replace the GRU?

Mostly, yes: from about 2020, traffic and motion forecasters mixed time with attention (GMAN, Scene
Transformer, PatchTST). The openpilot driving software carried a 512-number GRU state in 2019; its
December 2025 release reads past vision features with causal attention. But the move was not about
accuracy: on the tracks above the GRU scored 1.314 m/s and the temporal transformer 1.315.

```{figure} ../_static/figures/HP_Chain_vs_Meeting.png
:alt: Left, recurrent cells reading 30 messages strictly in order. Right, 30 messages all connected to each other and to a summary token, 900 pairs per layer.
:width: 100%

A GRU is a chain, where message 1 reaches the token only by surviving 29 later updates; a temporal transformer is a meeting, where every message is one hop from the summary.
```

The "attention" row above is a temporal transformer, and it is path 1: the transformer of
{doc}`2.5 <notes5-bert>` and {doc}`2.7 <notes7-vision>` pointed along time. A Linear layer turns each
BSM into a token, as ViT does a patch. Each token is told its time, because self-attention reads a set:
without a time tag, braking then speeding up looks like speeding up then braking. A learned summary
token, BERT's `[CLS]` trick, collects the window. For an output after every message, add the causal
mask of {doc}`2.4 <notes4-gpt>`. Each layer computes

$$
\alpha_{ij} = \operatorname{softmax}_j\!\left(\frac{q_i \cdot k_j}{\sqrt{d}}\right),
\qquad
e_i' = \sum_{j} \alpha_{ij}\, v_j
$$

- $e_i'$ &mdash; the new token of BSM $i$
- $q_i$, $k_j$, $v_j$ &mdash; what message $i$ looks for, what $j$ offers, what $j$ hands over; $d$ the query width
- $\alpha_{ij}$ &mdash; how much message $i$ reads message $j$; each row adds up to 1

**In words:** each message's new token is a weighted average of all 30, with weights it computes
itself; since {doc}`2.3 <notes3-attention>`, only the meaning of $i$ and $j$ changed. The one trained
here has 2 layers, 4 heads and 64 numbers: 67,392 weights, 4.9 times the GRU's 13,632.

### Same window, two ways to remember

```{figure} ../_static/figures/GVT_Same_Window.png
:alt: One synthetic braking window: speed, the GRU's write share over time, and the transformer's layer-2 attention, two heads on the braking and two on the newest message.
:width: 100%

The GRU decides as each message arrives; the transformer waits for all 30, then looks back (synthetic window).
```

The hardest braking, &minus;3.0 m/s&sup2;, comes 1.0 s before now. What the GRU did not write in, it
cannot look up later. The transformer looks back: in layer 2, two heads put 79% and 74% of their weight on messages 0.5 to 1.0 s old, around the hardest braking,
and two put 74% and 75% on the newest message &mdash; trend and anchor in separate heads. Over all
5,075 test windows, 77% of layer 2 fell on the last second, against 33% for an equal share. **The GRU decides at write time; the transformer at read time.**

### What each costs, and where the GRU stays

With accuracy tied, choose on cost. **Training:** a GRU over $T$ messages is $T$ steps that wait for
each other; the two-layer transformer is 2 rounds over all $T$ at once. On a GPU that is why the field
moved, but only there: on the 2-core CPU used here the GRU trained faster, 103.1 against 248.8 s per
seed. **One block for everything:** the same attention mixes BSMs, other vehicles, lanes and a camera.
**Streaming** is where the GRU stays:

| one new message arrives | after 30 BSMs | after 1,000 CAN steps |
|---|---|---|
| GRU: one cell update | 13,248 | 13,248 |
| transformer: re-read the window | 2,287,232 | 322,433,792 |
| transformer: causal mask + key/value cache | 73,536 | 321,856 |

*Multiply-adds per new message on modules the size of the two trained encoders; counts, not timings.*

The cache grows by 256 numbers per message, and at 1,000 steps each update costs 24.3 times the GRU's:
on an ECU with fixed memory, that is the problem minGRU and Mamba (train in parallel, run like a GRU)
were built to solve. At scale, path 1 splits the work: eight video frames of 196 patches are 2,458,624
pairs per layer, 319,872 with TimeSformer's divided attention; 10 s of CAN at 100 Hz are 1,000,000
pairs, 400 once cut into 20 half-second patches (PatchTST).

:::{admonition} Fit card &mdash; Temporal transformer
:class: tip
**Idea in one sentence.** Every message in the window reads every other; a summary token collects them into the stream's token.

**Why it works.** Learned queries find the moments that matter anywhere in the window, and training runs in parallel.

**Fits these tasks.** Histories trained offline on GPUs; mixing time with agents, lanes and sensors (*prediction*, *classification*).

**Needs this data.** As for the GRU, plus a time tag on every token; more data for 4.9 times the weights.

**Breaks when.** Raw windows are long (patch first); it must refresh after every message on fixed memory.

**Keep the classical method when.** A few hand features carry the signal (on the synthetic tracks it beat ridge by 11.4%); for long-horizon forecasting a one-layer linear model (DLinear) beat transformer forecasters on nine benchmarks.
:::

:::{admonition} Before you trust this result
:class: warning
**What is the baseline?** The GRU it would replace, same tracks, head and budget: 1.314 against 1.315
m/s, seed ranges overlapping.

**How was the data split, and why is that honest?** The same split by drive; the attention shares are
measured over all test windows, not just the one drawn.

**What does it do on the ugly cases?** On hard braking the GRU is slightly better, 2.477 against 2.523.
A model sold as better "because it uses a transformer" owes you this comparison.
:::

(history-as-keys)=
## Path 2: history as keys and values

Path 1 decides what to keep before anyone asks; path 2 waits for the question. Keep one token per
second for the last 300 s, each carrying that second's camera count (capped at 8), loop counts and
signal, the vehicles counted in and out since, and its age; the current second queries all 300. Age
tags let sensors on different clocks share one buffer (the clock problem of {doc}`2.11 <notes11-streams>`).

```{figure} ../_static/figures/HP_Buffer_Attention.png
:alt: Top, the true queue over the last 300 s rising past the camera's cap of 8. Bottom, the query's attention by layer: layer 1 peaks sharply about 152 s back, the last time the end of the queue was in view; layer 2 spreads over the earlier stretch when the queue was short.
:width: 100%

Never told which past seconds matter, the query reads the ones when the camera could still see the end of the queue (synthetic approach).
```

Why there? The input-output method, written with Newell's cumulative curves:

$$
Q(t) = Q(\tau) + \big[A(t) - A(\tau)\big] - \big[D(t) - D(\tau)\big]
$$

- $Q(t)$ &mdash; vehicles queued now; $Q(\tau)$ &mdash; the queue at a past second $\tau$ when the camera saw its end
- $A$, $D$ &mdash; cumulative counts at the advance loop and at the stop-bar loop

**In words:** every second when the camera saw the end of the queue offers one estimate of the queue
now, and its stored token carries both halves.

In the second drawn, the true queue is 15, the camera reads 8, the end was last in view 152 s ago, and
the model answers 14.5. Over test seconds whose last clear view was half a minute to five minutes old,
79% of layer 2's attention went to seconds when the camera saw the end of the queue, which are 36% of
the buffer. Nobody labelled them. Only about 5% of layer 1 and 2.5% of layer 2 landed within 5 s of the
latest one: it averages many, and with them the camera's off-by-one errors.

:::{admonition} Fit card &mdash; History as keys and values
:class: tip
**Idea in one sentence.** Store the recent past as age-tagged tokens; the current query reads the ones it needs.

**Why it works.** The answer often sits at a past moment you can look up, and attention finds such moments unprompted.

**Fits these tasks.** State estimation from intermittent views; sensors on different clocks (*prediction*, *retrieval*).

**Needs this data.** Time stamps on every sensor; a buffer longer than the gaps that matter.

**Breaks when.** The useful moment is older than the buffer.

**Keep the classical method when.** The physics is a conservation law and the counts are good: input-output counting with a camera reset averaged 0.54 vehicles on the synthetic approach, the buffer 1.061.
:::

:::{admonition} Before you trust this result
:class: warning
**What is the baseline?** Input-output counting with a camera reset on the same synthetic seconds:
0.54 vehicles overall against the buffer's 1.061, and 1.408 against 1.504 when the end of the queue
was last seen 2 to 5 minutes earlier.

**How was the data split, and why is that honest?** By episode, 400 / 50 / 100 synthetic runs of 30
minutes, 3 seeds; the attention shares cover all test seconds whose last clear view was half a minute
to five minutes old, not only the second drawn.

**What does it do on the ugly cases?** Beyond the 300-s buffer the error jumps to 6.1 vehicles; and
attention on the in-view seconds shows where the query read, not that it needed them.
:::

(carried-memory)=
## Path 3: the operator's whiteboard

You do not replay the last hour of video every time a camera refreshes. You keep a whiteboard: the
northbound queue runs past the camera and is still growing; the lane 2 advance loop is undercounting.
Each new report is read against the board, then the board is updated. Path 3 works the same way.

```{figure} ../_static/figures/HP_Memory_Loop.png
:alt: Four memory tokens and four new sensor tokens feed a write block with a GRU gate; a task query reads the updated memory and outputs the queue now; the memory is carried to the next second.
:width: 100%

Carry a summary, not the tape: four tokens, written with attention and read by the task query, at a fixed cost per second.
```

Four memory tokens are carried from second to second. **Write:** each cross-attends to the second's
new tokens and the other memory tokens, and updates. **Read:** a task query cross-attends to the memory
and the new tokens, and a small head gives the queue. Second 1,700 costs what second 1 cost, and there
is no horizon; but what the memory did not keep is gone.

### Write with attention, keep with a gate

$$
u_j = \text{CrossAttn}\big(m_j;\ \text{new tokens},\ m_1,\dots,m_4\big),
\qquad
m_j \leftarrow (1 - z_j)\odot m_j + z_j \odot \tilde{m}_j
$$

- $m_j$ &mdash; memory token $j$: 32 numbers carried from second to second
- $u_j$ &mdash; what memory token $j$ read this second
- $z_j$ &mdash; the write share, per number: 0 keeps the memory, 1 overwrites it
- $\tilde{m}_j$ &mdash; the candidate; $z_j$, $\tilde{m}_j$ come from $u_j$, $m_j$ as in the GRU

**In words:** the GRU update from earlier, except that its input is what the memory token chose to read
(as in slot attention).

The trained memory (also given the running count of vehicles in minus out as a token) wrote with an
average share of 0.38 while the camera saw the end of the queue and 0.18 once the queue ran past the
view: write hard when the camera tells you the answer, hold and add the counts when it does not. A
straight-line read of the memory explains 87% of the queue's variance. One oddity: all four tokens
learned the same gate and collapsed into copies, as nothing pushed them to specialize.

**One slot per thing you track** is the tracker's fix. MOTR carries one query per object into the next
frame, the object queries of {doc}`2.10 <notes10-detr>` with a life span: a car hidden behind a truck
keeps its slot rather than returning as a "new" car. At an intersection, one slot per approach queue,
vehicle or waiting pedestrian, like lines on the whiteboard.

### Head to head: the queue past the camera

The **synthetic** approach has one through lane, fixed-time cycles of 80 to 120 s, demand peaking at a
volume-to-capacity ratio of 0.85 to 1.15, slightly noisy loops, and the 8-vehicle camera. Path 1 is a
transformer over the last 30 s, path 2 the 300-s buffer, path 3 a GRU and the 4-token memory. The
classical baseline is input-output counting, reset to the camera whenever it reads 6 or fewer.

```{figure} ../_static/figures/HP_Queue_Head_To_Head.png
:alt: Error in vehicles, log scale, against time since the end of the queue was last in view; the window and buffer jump past their length, the memories track input-output counting.
:width: 100%

Windows and buffers fail once the last clear view falls outside them; carried memories do not, and only match input-output counting with a camera reset (synthetic data).
```

Slice before you average: with the end of the queue in view (60.5% of test seconds) every method is
nearly perfect, the camera alone included. The 30-s window is off by 0.65 vehicles up to 30 s, then
jumps to 4.9; the buffer's error grows from 0.48 (up to 30 s) to 1.5 (2 to 5 minutes), then jumps to
6.1. The memories never run out of
past: beyond 5 minutes the GRU is off by 2.6 vehicles and the 4-token memory by 2.3. Input-output
counting with a camera reset is best or tied almost everywhere: 2.3 beyond 5 minutes, 0.54 overall,
against 0.60 for the best learned memory. Against a conservation law with decent counts, a learned
memory can at best learn to behave like the classical method.

### How much past? A learned Kalman gain

Every write gate decides how much of the past to keep. You know a principled answer: the Kalman gain.

```{figure} ../_static/figures/HP_Gate_Kalman.png
:alt: Weight on the past against surprise: the learned gate drops early in clear weather and late in rain; the Kalman weights and the no-incident gate are flat.
:width: 100%

A gate trained on squared error lands on the Kalman weight, and drops the past after a surprise only if its training data held incidents (synthetic toy).
```

A **synthetic** approach speed drifts slowly and jumps 15 to 25 mph when an incident starts; a camera
reads it with 1 mph of noise in clear weather, 6 mph in rain. A gate that sees rain and surprise,
trained only on squared error, keeps 0.64 of the past in steady clear weather and 0.87 in rain; a Kalman
filter that knows the noise keeps 0.61 and 0.92. Then it does what the textbook filter
cannot: a big surprise in clear weather drops the weight on the past to 0.03, while in rain it holds
until the surprise passes about 14 mph. In seconds 0 to 9 after a jump in clear weather, that cut the
error from 5.01 mph (Kalman) to 0.74; in steady rain the filter wins, 1.88 against 2.12. Trained without
incidents, the gate stays flat near the Kalman weights: it learns how much history to trust only from
situations in its training data.

:::{admonition} Going deeper &mdash; why a gate finds 1 &minus; K
:class: dropdown
Treat the past summary $h$ and the new reading $y$ as unbiased estimates of the same speed with
independent errors of variance $P$ and $R$. Blend them as $g\,h + (1-g)\,y$, where $g$ is the weight on
the past (the GRU's $1 - z_t$). The expected squared error is

$$
g^2 P + (1-g)^2 R, \qquad \text{smallest at} \qquad g = \frac{R}{P+R} = 1 - K,
$$

the Kalman filter's weight on its prediction. A gate that sees cues about $P$ and $R$ learns that ratio
as a function of them: rain raises $R$; a big surprise or a long gap raises $P$. KalmanNet (Revach and
colleagues, 2022) keeps the filter's equations and learns only the gain.
:::

## Where it breaks

- **Copycat.** A model given its own past may learn to repeat it; ChauffeurNet kept only the car's
  current position, not its past motion, in half its training examples to stop this.
- **Drift.** A memory that only adds and subtracts never fixes its mistakes: counting in and out with
  no camera was off by 3.3 vehicles on average, against 0.54 with a camera reset.
- **Horizon and spillback.** Windows and buffers forget what is older than their length; a queue over
  the advance loop breaks the counts every method here leans on (not simulated).
- **Step-by-step training.** A memory trains second by second, never in parallel across time like a
  window.

## Which path, when

| | 1 &middot; bake into the token | 2 &middot; keys and values | 3 &middot; carried memory |
|---|---|---|---|
| **Keeps** | one summary per stream | every past token, as measured | a few tokens, rewritten each second |
| **Horizon** | the window (30 s here) | the buffer (300 s here) | none, but it can drift |
| **Cost per new second** | re-read the window: 31 &times; 31 pairs per layer | one query &times; 300 keys per layer | 4 &times; 9 pairs to write, 9 to read |
| **Use it when** | the past that matters is short | the answer sits at one past moment | the state builds up over minutes |

Real systems mix them. Start from the classical estimator, given to the model as one more token.

:::{admonition} Fit card &mdash; Carried memory
:class: tip
**Idea in one sentence.** Carry a few learned tokens from second to second; read them to answer, write into them what is new.

**Why it works.** A gate sets, per number, how much each new second changes the memory: hold through noise, overwrite on a clear view &mdash; a learned Kalman gain.

**Fits these tasks.** Queue and state estimation, tracking through occlusion, incident status at a TMC (*prediction*, support for *judgment*).

**Needs this data.** Long continuous logs in order, the state labelled or simulated, every sensor time-stamped.

**Breaks when.** Nothing ever resets it; its inputs are biased; training never shows what should move its gate.

**Keep the classical method when.** The physics is exact and the counts are good: input-output counting with a camera reset scored 0.54 vehicles on the synthetic approach, the best learned memory 0.60.
:::

:::{admonition} Before you trust this result
:class: warning
**What is the baseline?** For the queue, the camera alone (3.5 vehicles overall) and input-output
counting with a camera reset (0.54), which nothing learned beat. For the gate, a Kalman filter.

**How was the data split, and why is that honest?** By episode, as for path 2: 150,000 test seconds,
3 seeds per model, errors sliced by time out of view. The gate toy has one
training seed. Both are synthetic: they show mechanisms, not field accuracy.

**What does it do on the ugly cases?** 12% of test seconds had the end of the queue out of view for over
5 minutes, where windows and buffers fail. Harder cases were never generated: no queue reached the
advance loop, and detector errors were mild.
:::

## Check yourself

1. A TMC wants a model that warns when a freeway queue is about to reach an off-ramp. Which path would
   you start with, what would you give it as input, and what would reset it?
2. A vendor's queue detector runs a temporal transformer over the last 10 s of video. Under what demand
   would you expect it to fail, and how would you test that before you buy?
3. A roadside unit tracks 60 connected vehicles entering and leaving radio range and refreshes a queue
   estimate after every BSM. Which history encoder would you give each vehicle, and why?

---

Next: {doc}`notes13-evaluation` &mdash; whether any of it beats the method it would replace.
