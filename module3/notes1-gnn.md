(graph-neural-networks)=
# 3.1 One view of every network: graph neural networks

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 3 &middot; Section 3.1</span>
    <span class="notes-card-session">Session: Graph neural networks</span>
  </div>
  <p class="notes-card-lede">Every network in Modules 1 and 2 does the same thing: each token takes a weighted mix of what some other tokens carry. Only two choices differ &mdash; which tokens it may read, and how much each one counts. Draw &ldquo;may read&rdquo; as lines and every one of those networks is a graph. A graph neural network is the version where the graph comes from the problem. That makes it both the summary of Modules 1 and 2 and the right tool when the thing you model is a road network.</p>
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

:::{admonition} Why this comes after Modules 1 and 2
:class: tip
It needs everything before it: the convolution of {doc}`1.3 <../module1/notes3-cnn>`, the recurrence
of {doc}`2.12 <../module2/notes12-history>`, self-attention in 2.3&ndash;2.8 and cross-attention in 2.9&ndash;2.11.
The first half puts all of them in one picture. The second half uses that picture to read a road
network.
:::

## Every network so far is one update

Take away the names and every layer you have met does one job: it lets each token take in what some
other tokens carry. A token can be a word piece, a camera patch, a time&ndash;space cell or a detector
station. The picture below shows it for one station on a freeway.

```{figure} ../_static/figures/EMC_One_Update.png
:alt: Left, station 8 now reads stations 7, 9, 10 and its own reading five minutes earlier, each arrow labelled with a weight a. Right, the update h_i equals the sum over j in N(i) of a_ij times W times v_j, with N(i) marked choice 1, who may be read, and a_ij marked choice 2, how much j counts.
:width: 100%

One update covers every network so far: token i becomes a weighted mix of what its allowed neighbours carry. The weights shown are made up.
```

$$
h_i \;\leftarrow\; \sum_{j \in N(i)} a_{ij}\, W\, v_j
$$

| Symbol | In transportation terms |
| --- | --- |
| $v_j$ | what token j carries: a station's last hour of speeds, a word piece's vector, a camera patch |
| $N(i)$ | the tokens that token i is allowed to read &mdash; **choice 1** |
| $a_{ij}$ | how much token j counts for token i &mdash; **choice 2** |
| $W$ | one linear map, the same for every token |
| $h_i$ | token i's new state, which now carries context |

**In words:** each token becomes a weighted mix of what its allowed neighbours carry. Choose who may be
read and how the weights are set, and you have chosen an architecture. A real layer also adds a
nonlinearity and keeps some of the token's own state, but that does not change the two choices.

## Who may read whom is a graph

Draw each token as a dot. Draw a line from token j to token i when i may read j. What you get is a
graph. The same lines can be written as a table, A: a 1 in row i, column j when i reads j, and a 0
otherwise.

```{figure} ../_static/figures/GNN_Who_Reads_Whom.png
:alt: Three panels. BERT or ViT, seven words all joined to each other, with an all-ones 7 by 7 table. Swin on a 4 by 4 grid of patches in four 2 by 2 windows, with a block-diagonal 16 by 16 table, 64 of 256 entries on. A street network of 8 intersections and 10 road links, intersection 5 joined to 2, 4, 6 and 7, with a sparse 8 by 8 table, 28 of 64 entries on.
:width: 100%

Three architectures as graphs. BERT and ViT: every token reads every token, so the table is all ones. Swin: only the window (a toy 4 &times; 4 grid; Swin uses 7 &times; 7 windows). A street network: only the intersections a car reaches directly. In all three, a token also reads itself.
```

Here is every network in Modules 1 and 2 written the same way.

| Network | A node is | Who it may read, $N(i)$ | How much each counts, $a_{ij}$ |
| --- | --- | --- | --- |
| Dense layer (MLP) | one input number | every input | one learned weight for every pair |
| CNN ({doc}`1.3 <../module1/notes3-cnn>`) | a pixel, or a time&ndash;space cell | a fixed 3 &times; 3 window | one learned weight per window slot, the same everywhere |
| RNN, GRU ({doc}`2.12 <../module2/notes12-history>`) | one time step | the step before, through a running state | learned once, the same at every step |
| BERT, ViT (2.3, 2.5, 2.7) | a word piece; a 16 &times; 16 patch | every token | computed from the content: softmax of $q \cdot k / \sqrt{d}$ |
| GPT ({doc}`2.4 <../module2/notes4-gpt>`) | a word piece | every earlier token | computed from the content |
| Swin ({doc}`2.8 <../module2/notes8-locality>`) | a patch | the tokens in its own window | computed from the content |
| Cross-attention, DETR (2.9, 2.10) | a query, and the tokens of another source | every token in the other source | computed from the content |
| Graph convolution (this section) | a detector, a road segment, an intersection | its neighbours on the road | fixed in advance by how many links each node has |
| Graph attention (this section) | the same | its neighbours on the road | computed from the content |

Read the last two rows against the rest. A graph convolution keeps the CNN's habit: the weights are
fixed before the data arrive. Graph attention takes BERT's habit: the weights are computed from the
content. The only new thing in either is where $N(i)$ comes from. It is not a pixel grid and not
&ldquo;everyone&rdquo;. It is the road network you already manage.

```{figure} ../_static/figures/EMC_Two_Dials.png
:alt: A map with two axes. Vertical, who may talk, from a few fixed neighbours to everyone. Horizontal, how much each one counts, from fixed in advance to computed from the content. Bottom left, RNN, CNN and graph convolution. Top left, the dense layer: 600,100 weights where 8 convolution filters need 80. Right, self-attention and cross-attention near the top, Swin and graph attention near the bottom.
:width: 100%

Two dials make every architecture: who may talk, and how the weights are set. Graph convolution sits with the CNN; graph attention sits with Swin, a fixed set of neighbours with weights computed from the content.
```

This is the sense in which a graph neural network is the general form. Every point on that map is the
same update, with a particular graph and a particular rule for the weights. A graph network leaves both
choices open. Give it everyone-reads-everyone and computed weights, and you have self-attention. Give it
the road and fixed weights, and you have a graph convolution.

:::{admonition} Where the one picture is too neat
:class: note
- **A CNN has a different weight for each slot.** The upstream tap and the downstream tap of a 3-tap
  kernel are different numbers. As a graph, a 3 &times; 3 CNN has nine *kinds* of edge, one per slot.
  A plain graph convolution has one weight for every neighbour, so on a pixel grid it can only blur;
  it cannot find an edge in an image. The fix is to tell the edges apart. On a road the obvious kinds
  are upstream and downstream, and the companion below shows that knowing direction is worth more
  than attention itself.
- **Position is what you add back after you throw the graph away.** When every token reads every
  token, the wiring says nothing about order, so BERT and ViT add position embeddings
  ({doc}`2.1 <../module2/notes1-tokens>`, {doc}`2.7 <../module2/notes7-vision>`). In a graph network the edges carry the
  structure. Swin's relative position bias ({doc}`2.8 <../module2/notes8-locality>`) is already a feature on an
  edge.
- **Cross-attention is a graph with two kinds of node.** Queries sit on one side, keys and values on
  the other, and the edges go one way. The lane-anchor hub of {doc}`2.11 <../module2/notes11-streams>` is the
  same idea with many kinds of node.
:::

## What is a node? The same question as &ldquo;what is a token?&rdquo;

BERT's designers chose the word piece as the token. ViT's chose a 16 &times; 16 square. A graph
network asks you to make that choice again, and nobody has made it for you. The rule is the one a
tokenizer follows: **make a node of the thing whose state you want to read out.**

```{figure} ../_static/figures/GNN_Two_Tokenizations.png
:alt: Three panels. A four-leg intersection with two-way roads. The same intersection as a graph with the intersection as a node, 5 nodes and 4 edges. The same intersection with each directed road link as a node, 4 inbound and 4 outbound, joined by 12 turning movements coloured through, left and right.
:width: 100%

One intersection, two graphs. With intersections as nodes, the roads are the edges. With directed road links as nodes, the turning movements are the edges: 8 nodes and 12 movements. Pick the one whose nodes carry the state you want to predict.
```

- **Speed at a sensor:** make the detector station the node. The METR-LA data set in
  {doc}`2.6 <../module2/notes6-architecture>` is 207 detectors, each with about six and a half road neighbours.
- **Density or travel time on a road:** make the directed road segment the node. On the map a
  segment is an edge between two intersections; in the graph network it is a node, and the turning
  movements become its edges. This is called the *line graph*.
- **A queue or a signal phase:** make the intersection the node, or each movement.
- **Direction splits a road.** Northbound and southbound at the same milepost carry different
  states, so they are two nodes.
- **Granularity is your choice,** just as whole words versus word pieces is: one link can be one
  node, or ten 0.1-mile cells.

## From one picture to a road network

Section {doc}`2.11 <../module2/notes11-streams>` already ended at a graph: lane cells of different kinds joined
by edges of different kinds, with attention on each edge. The rest of this section starts that idea
again from traffic flow theory and asks a narrow question: **can a learned model stand in for a model
you would otherwise write down?**

The honest way to answer is to show that the classical traffic model *already is* the neural
architecture. That puts the two on the same footing instead of pitting a tuned network against a
strawman. {doc}`1.3 <../module1/notes3-cnn>` does this for a **corridor**, where Newell's model and the
cell transmission model turn out to be convolutions. This section does it for a **network**, where the
cell transmission model turns out to be a graph neural network.

## When the thing you are modelling is a network

A corridor is a line, and a convolution slides along it. A city is not a line. If
you want to forecast queue spillback across a signalised grid, or work out how
far an incident's impact reaches, or estimate speeds at intersections where you
have no detector, the object you are modelling is a graph: intersections joined
by streets, each intersection with its own number of connections and its own
geometry.

The obvious first attempt — flatten the network into a long vector and fit a
network to it — fails for a reason worth stating plainly. The parameter count
becomes a function of how many intersections you have, the model is tied to one
specific ordering of them, and it cannot be run on any other city, or even on the
same city after a detector is added. That is the problem a graph neural network
solves, and it solves it with a move you already use.

**The bridge: the cell transmission model is already a graph neural network.**

```text
CTM, at one cell
────────────────
y      = min{ S(n_up), R(n_here) }   ← one rule, per connection
n(t+1) = n + Σ in − Σ out            ← conservation, however many legs

GNN, at one node
────────────────
m(v→u) = ψ(h_v, h_u, e_vu)           ← one rule, per connection
h_u'   = φ(h_u, ⊕ over v of m)       ← ⊕ eats however many messages
```

Nobody asks how many parameters the CTM has *for a given network*. It has four —
free-flow speed, backward wave speed, capacity, jam density — whether it runs on
three cells or thirty thousand. The sending and receiving functions are one pair
of functions applied at every cell; the network decides only how many times you
call them and who talks to whom. A GNN is exactly that, with the per-connection
function **fitted** instead of **derived**.

That one word is the whole trade. The CTM transfers to any city because its rule
came out of a conservation law and is therefore correct everywhere; you
re-estimate four parameters and the topology comes from the network file. A GNN's
rule came out of data, so it transfers only as far as the data it saw. Everything
that follows is about how much of what it learned was physics and how much was
bookkeeping about particular sensors.

Work through the companion before the equation. Every network on the page is
generated in your browser, every number is computed live from it, and the
regenerate button is the argument: press it and the intersections, the degrees
and the size all change while the same rule keeps running.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion — A GNN on a road network: one shared rule, any number of intersections</span>
    <a href="../_static/companions/GNN_On_A_Road_Network_Companion.html" target="_blank" rel="noopener">Open full screen ↗</a>
  </div>
  <iframe src="../_static/companions/GNN_On_A_Road_Network_Companion.html"
          title="A GNN on a road network" loading="lazy"></iframe>
</div>

## The rule, written once

```text
for every directed street segment v → u  (however many that is):
    m(v→u) = tanh( Wm · [ h_v ‖ h_u ‖ e(v→u) ] + bm )

then at each intersection u, collapse however many arrived:
    a(u)   = mean over v in N(u) of m(v→u)

and update:
    h_u'   = tanh( Wu · [ h_u ‖ a(u) ] + bu )
```

| Symbol | In transportation terms |
| --- | --- |
| `h_u` | the state vector carried for intersection u. On the first layer it is the measured quantity — speed, occupancy, queue; after that it is whatever the model has worked out about u and its surroundings. |
| `e(v→u)` | what this connection *is*: upstream or downstream, turn type, link length, lanes, whether one phase serves the movement. Not which street it is — what kind of street it is. |
| `m(v→u)` | the message: what v's condition means *for u specifically*, given the kind of connection between them. |
| `Wm, bm` | the message weights. One set, shared by every segment in the city. This is the model. |
| `N(u)` | u's neighbours. Its size is the node's degree — 1 to 5 in a real street network. Nothing in `Wm` or `Wu` knows or cares. |

**In words:** for each street touching this intersection, work out what the far
end's condition means for this end; average those meanings, whatever their
number; use the average to update what you believe about this intersection.

Notice what never appears. There is no rule for a four-leg intersection and a
different one for a five-leg. The per-connection function always takes exactly
two nodes and one connection, and the varying part of the city is absorbed by
*how many times you call it* — the same way conservation of flow at a node is one
equation summed over however many approaches, not a different equation per
geometry. Stack the layer L times and a one-hop rule becomes an L-hop model:
that, and nothing more mysterious, is how a local rule reproduces a jam that
crosses the whole network.

:::{admonition} Going deeper — the ceiling on what message passing can tell apart
:class: dropdown
Message passing sees a node only through the shape of its surroundings. If two
intersections have the same degree, and their neighbours have the same degrees,
and so on outward, they receive identical messages at every layer and no depth
separates them. This is exactly the discriminating power of one-dimensional
Weisfeiler–Leman colour refinement, and each layer is one round of it.

The practical consequence is that the fix is features, not depth: lanes, control
type, speed limit, distance to the nearest ramp, betweenness centrality. All of
those are computable in any city, so unlike a learned per-sensor embedding they
cost you nothing in transferability. See Xu et al., *How Powerful are Graph
Neural Networks?* (ICLR 2019), which also explains why a sum aggregator reaches
that ceiling while mean and max fall short of it — a gap the companion lets you
reproduce in a street network in about ten seconds.
:::

## Graph attention: BERT's weights on the road's wiring

On the two-dials map, graph attention sits next to Swin: the road fixes who may be read, and the
content sets the weights. In code it is one line added to the attention of {doc}`2.3 <../module2/notes3-attention>`:

```python
scores = Q @ K.T / d**0.5                           # every token scores every token, as in BERT
scores = scores.masked_fill(A == 0, float('-inf'))  # only road neighbours may be read
alpha  = scores.softmax(dim=-1)                     # weights over the allowed neighbours sum to 1
H_new  = alpha @ V
```

With A all ones this is BERT or ViT. A lower-triangular A gives GPT's causal mask
({doc}`2.4 <../module2/notes4-gpt>`). Window blocks give Swin. The road's adjacency, with each node also reading
itself, gives graph attention. Keep those self-links: in the METR-LA road graph six detectors have no
neighbour at all, and a softmax over an empty row has no answer. The mask is the teaching version.
Graph libraries compute scores only along the edges that exist, which is why they scale to a whole
city where every-pair attention would not.

:::{admonition} Going deeper &mdash; which &ldquo;graph attention&rdquo;?
:class: dropdown
The original graph attention network (Veličković et al., ICLR 2018) does not use separate queries and
keys. It scores each edge with one shared weight matrix and one attention vector, and as a result every
node ranks its neighbours in the same order, whichever node is asking. Brody, Alon and Yahav call this
*static* attention (*How Attentive are Graph Attention Networks?*, ICLR 2022). The query&ndash;key
version above, where the ranking can change with the asking node's own state, is the GATv2 and graph
transformer line. The optional last part of Lab 5 measures the difference on a traffic rule where the
neighbour that matters flips with the receiving link's own density.
:::

## Three results worth carrying out of the companion

Tab 4 of the companion is a real experiment, not an illustration: a GNN trained
in PyTorch on a queue-spillback rule, then tested on **networks it had never
seen, at sizes it had never seen**. The reproducers sit beside the page as
`gnn_roadnet.py` and `sweep.py`, with `attn_roadnet.py` behind tab 5.

- **Depth buys reach, and you need as much as the horizon demands.** At a
  one-step horizon a single layer is within 1.6× of the best depth — one hop is
  all the problem needs. At a three-step horizon that same single layer is 2.4×
  worse, because the disturbance now starts outside what it can see. Substitute
  your own numbers: a disturbance travels about the backward wave speed times
  your forecast horizon, so the hops you need is that distance over your mean
  link length. Pick depth from the traffic, then check whether the architecture
  can actually reach that far.
- **The aggregator is a modelling choice, not a hyperparameter.** Same
  architecture, same depth, same data — swapping mean for max was worth 4.3×,
  a bigger gain than going from one layer to four. The ground-truth rule takes a
  max over downstream neighbours, because a queue backs up from the *worst* road
  you feed into, not the average one. Sum when the quantity is conserved, mean
  when it is an intensive state, max when a bottleneck governs, attention when
  the weighting is the thing you do not know.
- **Attention is a learned aggregator, and the street network is worth more than
  the learning.** Tab 5 runs a transformer layer over the road graph and fits it
  in your browser. Restricting the softmax to streets that exist takes test RMSE
  from 0.0839 to 0.0556; adding which way each street runs takes it to 0.0286 —
  both free, same ten parameters. Full attention over every pair of
  intersections, with the map withheld, beats a persistence baseline by 4%. The
  topology is not a constraint you impose on the model. It is the most valuable
  feature you own, and it is already in the link–node inventory.
- **Structure enters through the wiring, and it can be switched off by
  accident.** Give every intersection the identical input feature and a mean
  aggregator with no edge feature leaves the entire city holding one single
  distinct state at *every* depth — a mean of identical messages is the same
  number whether two streets meet or five. Turn the edge feature on and the city
  separates on the first layer. The asymmetry of the network is information, and
  a model can be built that throws it away.

## Where it breaks

The failure that matters most for an agency is not accuracy, it is
transferability, and it is visible in one glance at a parameter count.

> **The litmus test: does the number of nodes appear in the parameter count?**

The GNNs in the companion have 1,121 / 2,193 / 3,265 / 4,337 parameters at one
through four layers, and none of those numbers contain N — which is why the same
trained weights ran on unseen networks of unseen size. Compare with what is
common in the traffic-forecasting literature: a two-layer shared-weight block is
about 257 parameters *for any city*, while a learned adjacency built from node
embeddings is 4,140 parameters at the 207 sensors of one well-known benchmark and
6,500 at the 325 of another, and a per-sensor embedding table is larger still.
The identity part is over sixteen times the shared part, and every one of those
numbers is a fact about one sensor in one city. Models built that way top the
single-city leaderboards and cannot be moved at all.

The rest of the list: neighbours that are not interchangeable while nothing in
the edge features says so; a degree distribution that shifts between cities while
the aggregator is a sum; two intersections that are structurally identical and
operationally nothing alike; and coupling that does not travel along the network
at all, which is what a detour, a special event or weather does.

| Fit card — message-passing graph neural network | |
| --- | --- |
| **Idea in one sentence** | Learn one rule for what a single connection means, apply it to every connection, collapse whatever arrives at each node, repeat — so the size and shape of the network live in the wiring rather than the weights. |
| **Why it works** | Pairwise messages have fixed arity, so one function covers three-leg and five-leg alike; a permutation-invariant reduction absorbs varying degree; L layers compose a one-hop rule into an L-hop model. |
| **Fits these tasks** | Link speed and travel-time forecasting, sensor imputation, incident impact extent, network state estimation, cascading-failure and resilience analysis. *Leverage: prediction, classification.* |
| **Needs this data** | A network with attributes describing *what things are* (lanes, control, capacity, turn geometry, distance), plus a time series of node or link states. Labels come free when the target is a future measured state. Critically: **more than one network**, if transfer is ever the goal. |
| **Breaks when** | N appears in the parameter count; edge features do not encode role; degree shifts under a sum aggregator; the horizon needs more hops than the depth provides; the real coupling is off-network. |
| **Keep the classical method when** | The network is small enough to fit per-location models — a dozen intersections on one corridor means a dozen models, and skip all of this. The dynamics you need are already a conservation law: the CTM is derived, correct everywhere, and takes four parameters rather than three thousand. Or a per-sensor historical average by time-of-day already meets the accuracy the decision needs, which on quiet days it very often does. |

:::{admonition} Before you trust this result
:class: important
**What is the baseline?** · **How was the data split, and why is that honest?** ·
**What does it do on the ugly cases?**

The baseline here is persistence — predict that nothing changes — plus the
comparison across depths, so that no depth takes credit for what one hop already
achieves. The split is by **network**, not by time: training and test are
different graphs of different sizes, because a random time split within one city
would let a model memorise locations and still score well, which is the exact
failure this is meant to detect. The ugly cases are the nodes whose bottleneck
lies further away than the model's depth — they dominate the long-horizon error
and more data does not touch them — plus dead ends, where an average over a
single message carries no smoothing, and the step where a bottleneck clears,
when a learned bias toward persistence is exactly wrong.

One caveat the companion states about itself: its ground truth is a rule we wrote
down, so a model with enough reach can nearly nail it. Real cross-city
forecasting gains are far smaller. Take the shape of these results, not their
magnitude.
:::

## Two things to carry out of this section

**Exercise — read a model's parameter count.** Take any network-scale traffic
forecasting paper or product sheet. Find the parameter count, or reconstruct it
from the architecture description. Does the number of sensors appear in it? Then
answer three questions in writing: could this be run on your network without
retraining; what is the baseline the paper compares against; and was the reported
split across time or across networks. Most published results answer the third
question in a way that makes the first one moot.

**On the job.** When a vendor offers a network-wide prediction, ask what a node
is in their model, and what happens when you add a detector. The answers tell you
whether you are buying a model of traffic or a model of their training city. Then
ask for the persistence baseline on your own data — if they have not computed it,
neither has anyone else, and the improvement they are quoting has no
denominator.
