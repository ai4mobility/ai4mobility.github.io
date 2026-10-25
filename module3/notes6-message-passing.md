(message-passing)=
# 3.6 Message passing and graph convolution

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 3 &middot; Section 3.6</span>
    <span class="notes-card-session">Session: Graph neural networks</span>
  </div>
  <p class="notes-card-lede">One message-passing layer does three things at every node at once: collect a message from each neighbor, aggregate the messages into one, and update the node's own vector. This page writes that rule down, runs it in the companion on street networks you generate, and fills it in the simplest way: a graph convolution, where the structure sets how much each neighbor counts. Max-pressure signal control turns out to be one.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Interactive companion on this page</h4>
      <ul>
      <li><a href="../_static/companions/GNN_On_A_Road_Network_Companion.html" target="_blank" rel="noopener">A GNN on a road network &#8599;</a></li>
      </ul>
    </div>
    <div>
      <h4>Notebook that goes with it</h4>
      <ul>
      <li><a href="lab5_graph_attention.html">Lab 5 &mdash; Attention on a road network</a></li>
      </ul>
    </div>
  </div>
</div>

One message-passing layer does three things at every node, all at once: collect a **message** from each
neighbor, **aggregate** the messages into one, and **update** the node's own vector. Stack layers and
repeat. The picture shows one layer at cell 5 of the grid from {doc}`3.2 <notes2-graph-basics>`.

```{figure} ../_static/figures/GNN2_Message_Passing_Cell5.png
:alt: A left-to-right diagram at cell 5. Four neighbors, cell 4 west and cell 8 south which feed cell 5, cell 6 east and cell 2 north which cell 5 feeds, each send a message through the same rule psi of h5, hj and e. The messages meet at an aggregate, a sum, mean or max, giving m5, and the update phi of h5 and m5 gives cell 5's new state for the next layer. Gray notes give the CTM's version of each slot, the flow across the face min of S and R, in minus out, and k plus delta k.
:width: 100%

Each neighbor sends one message through the same rule &psi;; the aggregate &oplus; folds them into one; the update &phi; combines it with cell 5's own state. The gray notes show the CTM's version of each slot ({doc}`3.8 <notes8-ctm>`).
```

## The general form

$$
m_i^{(l)} = \bigoplus_{j \in N(i)} \psi\big(h_i^{(l)},\, h_j^{(l)},\, e_{ji}\big)
\qquad
h_i^{(l+1)} = \phi\big(h_i^{(l)},\, m_i^{(l)}\big)
$$

| Symbol | In words | At cell 5 |
| --- | --- | --- |
| $h_i^{(l)}$ | node i's vector after l layers | cell 5's state: k = 30 veh/mi |
| $N(i)$ | the nodes joined to i | 4 and 8 feed cell 5; cell 5 feeds 6 and 2 |
| $e_{ji}$ | features of the edge between j and i | which side: feeds 5, or is fed by 5 |
| $\psi$ (psi) | the message rule, the same on every edge | the flow across that face |
| $\oplus$ | the aggregate: combines any number of messages, in any order | a sum: what flows in minus what flows out |
| $\phi$ (phi) | the update: combines the node's own vector with the aggregate | cell 5's new density |
| $m_i^{(l)}$ | the aggregated message | the net flow into cell 5 |

**In words:** every node collects one message per neighbor using the same rule, combines them with an
operation that does not care how many there are or in what order, and then updates itself. In a GNN, $\psi$
and $\phi$ are small neural networks. {doc}`3.8 <notes8-ctm>` shows that the cell transmission model fills
the same three slots with physics.

**Why the aggregate must ignore count and order.** Cell 5 has four neighbors and corner cell 7 has two. In
a real street network, there is no "first" neighbor of an intersection at all. So $\oplus$ must be an
operation like sum, mean or max, which gives an answer for any number of inputs in any order.

**Why the model fits any network size.** $\psi$ and $\phi$ are shared by every node, so the number of nodes
appears nowhere in the parameter count. A message rule that reads both ends of a link (6 features each) and
outputs 16 numbers has 208 weights, whether the network has 9 cells or all of Florida. Feed all 495 USF
intersections into an ordinary MLP instead, and its first layer alone needs 47,536 weights, which must be
retrained whenever the network changes.

:::{admonition} The litmus test: does the number of nodes appear in the parameter count?
:class: important
The GNNs in the companion below have 1,121 / 2,193 / 3,265 / 4,337 parameters at one through four layers,
and none of those numbers contain N. That is why the same trained weights ran on unseen networks of unseen
size.

Compare with what is common in the traffic-forecasting literature. A two-layer shared-weight block is
about 257 parameters *for any city*, while a learned adjacency built from node embeddings is 4,140
parameters at the 207 sensors of METR-LA and 6,500 at the 325 of PEMS-BAY, and a per-sensor embedding
table is larger still. The identity part is over sixteen times the shared part, and every one of those
numbers is a fact about one sensor in one city. Models built that way top the single-city leaderboards and
cannot be moved at all.
:::

## Run it on a network you generate

Work through the companion before the next equation. Every network in it is generated in your browser,
every number is computed live, and the regenerate button is the argument: press it and the intersections,
the degrees and the size all change while the same rule keeps running. Tab 2 lets you switch the aggregate
between sum, mean and max; tab 3 animates queue spillback against what an L-layer model can see; tab 4 is
a real training experiment on depth and aggregator choice; tab 5 is the attention layer of
{doc}`3.7 <notes7-graph-attention>`.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion — A GNN on a road network: one shared rule, any number of intersections</span>
    <a href="../_static/companions/GNN_On_A_Road_Network_Companion.html" target="_blank" rel="noopener">Open full screen ↗</a>
  </div>
  <iframe src="../_static/companions/GNN_On_A_Road_Network_Companion.html"
          title="A GNN on a road network" loading="lazy"></iframe>
</div>

The layer the companion runs fills the three slots like this:

```text
for every directed street segment v → u  (however many that is):
    m(v→u) = tanh( Wm · [ h_v ‖ h_u ‖ e(v→u) ] + bm )   ← message ψ

then at each intersection u, collapse however many arrived:
    a(u)   = mean over v in N(u) of m(v→u)              ← aggregate ⊕

and update:
    h_u'   = tanh( Wu · [ h_u ‖ a(u) ] + bu )           ← update φ
```

In tab 2 you can swap the mean for a sum or a max and watch what changes.

| Symbol | In transportation terms |
| --- | --- |
| `h_u` | the state carried for intersection u. On the first layer it is the measured quantity (speed, occupancy, queue); after that it is whatever the model has worked out about u and its surroundings. |
| `e(v→u)` | what this connection *is*: upstream or downstream, turn type, link length, lanes. Not which street it is, but what kind of street it is. |
| `Wm, bm` | the message weights. One set, shared by every segment in the city. This is the model. |
| `N(u)` | u's neighbors. Its size is the node's degree, 1 to 5 in a real street network. Nothing in `Wm` or `Wu` knows or cares. |

Notice what never appears: a rule for a four-leg intersection and a different one for a five-leg. The
per-connection rule always takes two nodes and one connection, and the varying part of the city is
absorbed by *how many times you call it*, the same way conservation of flow at a node is one equation
summed over however many approaches. Stack the layer L times and a one-hop rule becomes an L-hop model.

:::{admonition} Going deeper &mdash; the ceiling on what message passing can tell apart
:class: dropdown
Message passing sees a node only through the shape of its surroundings. If two intersections have the same
degree, and their neighbors have the same degrees, and so on outward, they receive identical messages at
every layer and no depth separates them. This is exactly the discriminating power of one-dimensional
Weisfeiler&ndash;Leman color refinement, and each layer is one round of it.

The practical consequence is that the fix is features, not depth: lanes, control type, speed limit,
distance to the nearest ramp. All of those are computable in any city, so unlike a learned per-sensor
embedding they cost you nothing in transferability. See Xu et al., *How Powerful are Graph Neural
Networks?* (ICLR 2019), which also explains why a sum aggregator reaches that ceiling while mean and max
fall short of it.
:::

## Filter 1: graph convolution, where the structure sets the weights

The two filters on this page and the next differ in only one thing: how much each neighbor counts. In a
graph convolution, the structure decides. The graph convolutional network (GCN; Kipf and Welling, 2017) is
the simplest learned version of message passing:

$$
h_i^{(l+1)} = \sigma\Big( W^{(l)} \sum_{j \in N(i) \cup \{i\}} \frac{h_j^{(l)}}{\sqrt{\tilde d_i\, \tilde d_j}} \Big)
$$

| Symbol | In words |
| --- | --- |
| $\tilde d_i$ | node i's number of links, plus one for itself (the self-loop from {doc}`3.2 <notes2-graph-basics>`) |
| $1/\sqrt{\tilde d_i \tilde d_j}$ | how much neighbor j counts: set by link counts only |
| $W^{(l)}$ | the one learned matrix in the layer, shared by every node |
| $\sigma$ | a nonlinearity, such as ReLU |

**In words:** average yourself and your neighbors, weighted only by how many links each one has, multiply
by one shared matrix, then squash. In the message-passing slots, the message is
$W h_j / \sqrt{\tilde d_i \tilde d_j}$, the aggregate is a sum, and the update is $\sigma$.

**At cell 5 and at a corner.** Cell 5 has four links plus itself, so $\tilde d = 5$; cells 2, 4, 6 and 8
each have three links plus themselves, so $\tilde d = 4$.

- Cell 5 gives each of its four neighbors $1/\sqrt{5 \times 4} = $ **0.224**, and itself $1/5 = $ **0.200**.
- Corner cell 1 has only two neighbors ($\tilde d = 3$). It gives cells 2 and 4 each
  $1/\sqrt{3 \times 4} = $ **0.289**, and itself $1/3 = $ **0.333**.

The same matrix W serves both; only the normalization changes. With 64 numbers per node, one GCN layer has
4,160 weights.

:::{admonition} Does graph convolution need every node to have the same neighbors?
:class: note
No. That requirement belongs to a CNN kernel, which has one weight per slot, so every pixel must have the
same layout of neighbors. A graph convolution has no slots. It shares one rule for all neighbors and adds
up whatever arrives, scaled by link counts. A three-leg intersection, a four-leg one and a five-leg one all
run through the same weights, the parameter count has no degree in it, and the computation grows with the
number of edges, so it scales to large networks.

What irregular neighborhoods do cost is different:

1. Every neighbor counts the same up to the degree scaling, so the layer cannot tell upstream from
   downstream, or a left turn from a through movement.
2. With a mean or max aggregate and identical inputs, it cannot even tell a three-leg intersection from a
   four-leg one. On the USF network, mean and max leave all 495 intersections identical after three
   layers, while a sum gives 263 distinct states. Add the number of legs as a node feature, or use a sum.
3. Nodes and edges of different kinds need their own weights (typed edges, as in R-GCN).
:::

## Max pressure is a graph convolution

You have met a fixed graph convolution before: **max-pressure signal control** (Varaiya, 2013). Use the
intersection's link graph from {doc}`3.2 <notes2-graph-basics>`: the 4 inbound and 4 outbound directed
links are the nodes, and the 12 turning movements are the edges.

```{figure} ../_static/figures/GNN2_Max_Pressure.png
:alt: Left, a four-leg intersection as a link graph with synthetic queues, inbound north 12, south 8, east 20 and west 15 vehicles, outbound north 5, south 10, east 18 and west 4, and turning ratios of 0.7 through, 0.2 right and 0.1 left; the movements leaving the west approach are gold. Middle, the pressure of an inbound link, w equals x of l minus the sum of r of l m times x of m; for the west approach 15 minus 15.1 equals minus 0.1; a table gives pressures east 15.2, north 2.4, south 0.5 and west minus 0.1, so east-west 15.1 against north-south 2.9, serve east-west. Right, the same steps named as a GNN layer, message, aggregate, update, readout and decision, with matrix form w equals I minus R times x and weights set by measured turning ratios, not learned.
:width: 100%

Left: the intersection's link graph with synthetic queues; the gold movements leave the west approach. Middle: the pressure calculation. Right: the same steps named as a GNN layer.
```

The pressure on an inbound link l is its own queue minus the queues it would feed, weighted by the turning
ratios:

$$
w_l = x_l - \sum_{m} r_{lm}\, x_m
\qquad
\text{phase pressure} = \sum_{l \in \text{phase}} s_l\, w_l
$$

| Symbol | In words |
| --- | --- |
| $x_l$ | queue on inbound link l (veh) |
| $x_m$ | queue on outbound link m (veh) |
| $r_{lm}$ | share of link l's traffic that turns into link m |
| $s_l$ | saturation flow of the movements served (equal here) |

**Worked example** (synthetic queues; turning ratios 0.7 through, 0.2 right, 0.1 left on every approach).
The west approach, which carries eastbound traffic, has a queue of 15. Its through movement feeds the east
exit (queue 18), its right turn feeds the south exit (10), and its left turn the north exit (5). Its
pressure is 15 &minus; (0.7 &times; 18 + 0.2 &times; 10 + 0.1 &times; 5) = **&minus;0.1**.

| Inbound link | Queue (veh) | Weighted downstream queue | Pressure |
| --- | --- | --- | --- |
| East approach | 20 | 4.8 | 15.2 |
| North approach | 12 | 9.6 | 2.4 |
| South approach | 8 | 7.5 | 0.5 |
| West approach | 15 | 15.1 | &minus;0.1 |

The east&ndash;west phase has pressure 15.2 &minus; 0.1 = **15.1** and the north&ndash;south phase
2.4 + 0.5 = **2.9**, so the controller serves east&ndash;west.

Now read it as a GNN layer. Each inbound link receives a **message** $r_{lm} x_m$ from each outbound link it
feeds, with a weight fixed by the measured turning ratio. The **aggregate** is a sum. The **update** is the
link's own queue minus that sum. In matrix form, $w = (I - R)\,x$: one fixed graph filter, the same shape
as a GCN layer, with weights set by traffic data instead of training. The phase pressure is a sum
**readout** over the links a phase serves, and the decision is an argmax.

Notice the west approach: it has the second-longest queue, but its pressure is about zero because its main
exit is nearly full. Serving it would only move the queue. A rule that looked at queues alone would miss
that; reading the neighbors catches it. Learned controllers build on the same idea: PressLight (2019) uses
pressure inside a reinforcement-learning reward, and CoLight (2019) uses graph attention between
neighboring intersections.

## What the GCN cannot see, and three fixes

Cell 4 sends traffic into cell 5, and cell 6 receives it. Yet the GCN gives both exactly 0.224, whatever
the traffic is doing. It cannot tell a queue coming at you from a queue you are feeding. Three ways to give
it that back, in order of how much they ask of the data:

1. **Edge features.** Put direction, lanes and turn type on each edge and let $\psi$ read them.
2. **Edge types.** Use one weight matrix for links that feed you and another for links you feed. DCRNN, the
   model that made the METR-LA benchmark famous, runs separate forward and backward diffusion for this
   reason.
3. **Attention.** Let the current traffic states set the weights. That is
   {doc}`3.7 <notes7-graph-attention>`.

## Three knobs you set

**1. The aggregate: sum, mean or max.** Pick it the way the physics combines things.

- Vehicles are conserved &rarr; **sum**.
- The worst bottleneck decides &rarr; **max**.
- You want the typical speed around a node &rarr; **mean**.

Two results from the companion show why the choice matters. Give all 495 USF intersections the same
starting vector, so only the wiring differs. After three layers, a sum produces 263 distinct node states;
mean and max stay at 1. On the other hand, when the true rule is spillback (a link follows its worst
downstream neighbor), max wins: test error 0.0101, against 0.0228 for sum and 0.0435 for mean. That gap,
4.3 times between max and mean, is bigger than the gain from going from one layer to four.

**2. Depth buys reach: one layer is one hop.** A CNN sees one more ring of pixels per layer; a GNN sees one
more hop of the network. So choose the number of layers from distance. A queue front moving at 11.7 mph
covers about 2.9 miles in 15 minutes: about 6 hops on detector stations half a mile apart, but about 49
hops on a graph with a node at every intersection 97 m apart. In the companion, a 1-layer model's error is
1.6 times the best depth's one step ahead and 2.4 times three steps ahead, because the disturbance now
starts outside what one hop can see.

**3. Too deep, and nodes look alike.** Each layer mixes a node with its neighbors. Repeat that too many
times and neighbors become copies of each other, like blurring an image again and again. This is called
**oversmoothing**. Skip connections and keeping the node's own vector in the update help, which is why
traffic models usually stack only a few graph layers and let information travel through time instead.

:::{admonition} Going deeper (optional) &mdash; why is it called "convolution"?
:class: dropdown
In signal processing on graphs, the eigenvectors of the graph Laplacian play the role of Fourier waves, and
a filter is a polynomial in the Laplacian. A polynomial of order K mixes nodes up to K hops apart, the
graph version of a K-tap kernel. ChebNet learns those polynomial coefficients. The GCN keeps only the
first-order term and ties its weights, which gives one hop per layer and one weight for every neighbor.
Max pressure's $(I - R)$ is also a first-order filter. On a graph, "convolution" means "the same local rule
everywhere," nothing more. Sources: Hammond et al. (2011); Defferrard et al. (2016); Kipf and Welling
(2017).
:::

:::{admonition} Before you trust this result
:class: important
**What is the baseline?** · **How was the data split, and why is that honest?** ·
**What does it do on the ugly cases?**

The companion's baseline is persistence (predict that nothing changes), plus the comparison across depths,
so that no depth takes credit for what one hop already achieves. The split is by **network**, not by time:
training and test are different street networks of different sizes, because a random time split within one
city would let a model memorize locations and still score well, which is the exact failure the litmus test
above is meant to catch. The ugly cases are the nodes whose bottleneck lies farther away than the model's
depth (they dominate the long-horizon error, and more data does not touch them), dead ends, where an
average over a single message does no smoothing, and the step where a bottleneck clears, when a learned
bias toward persistence is exactly wrong.

One caveat the companion states about itself: its ground truth is a rule we wrote down, so a model with
enough reach can nearly nail it. Real cross-city forecasting gains are far smaller. Take the shape of these
results, not their size.
:::

---

Next: {doc}`notes7-graph-attention` &mdash; letting the traffic states set the weights.
