(one-view-of-every-network)=
# 3.3 One view of every network: sequences and images are graphs too

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 3 &middot; Section 3.3</span>
    <span class="notes-card-session">Session: Graph neural networks</span>
  </div>
  <p class="notes-card-lede">Every network in Modules 1 and 2 does the same thing: each token takes a weighted mix of what some other tokens carry. Only two choices differ &mdash; which tokens it may read, and how much each one counts. Draw &ldquo;may read&rdquo; as lines and every one of those networks is a graph: the RNN a chain, the CNN a grid, the transformer a complete graph. A graph neural network is the version where the graph comes from the problem.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Interactive companion for this module</h4>
      <ul>
      <li><a href="../_static/companions/GNN_On_A_Road_Network_Companion.html" target="_blank" rel="noopener">A GNN on a road network &#8599;</a> &mdash; embedded in <a href="notes6-message-passing.html">3.6</a></li>
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
This page needs everything before it: the convolution of {doc}`1.3 <../module1/notes3-cnn>`, the
recurrence of {doc}`2.12 <../module2/notes12-history>`, self-attention in 2.3&ndash;2.8 and
cross-attention in 2.9&ndash;2.11. It puts all of them in one picture.
:::

## Every network so far is one update

Take away the names and every layer you have met does one job: it lets each token take in what some other
tokens carry. A token can be a word piece, a camera patch, a time&ndash;space cell or a detector station.
The picture below shows it for one station on a freeway.

```{figure} ../_static/figures/EMC_One_Update.png
:alt: Left, station 8 now reads stations 7, 9, 10 and its own reading five minutes earlier, each arrow labeled with a weight a. Right, the update h_i equals the sum over j in N(i) of a_ij times W times v_j, with N(i) marked choice 1, who may be read, and a_ij marked choice 2, how much j counts.
:width: 100%

One update covers every network so far: token i becomes a weighted mix of what its allowed neighbors carry. The weights shown are made up.
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

**In words:** each token becomes a weighted mix of what its allowed neighbors carry. Choose who may be read
and how the weights are set, and you have chosen an architecture. A real layer also adds a nonlinearity
and keeps some of the token's own state, but that does not change the two choices.

## Who may read whom is a graph

Draw each token as a dot. Draw a line from token j to token i when i may read j. What you get is a graph.
RNNs, CNNs and transformers are graph models whose graph was chosen for you.

```{figure} ../_static/figures/GNN2_Architectures_As_Graphs.png
:alt: Four panels, each with one gold node and the nodes it reads. RNN, a chain of time steps, reading the step before with the same weights at every step. CNN, a grid of pixels, reading its 3 by 3 window with one weight per slot. Transformer, every pair joined, reading every token with weights from Q dot K. GNN, the road map's graph, reading its road neighbors by convolution or attention.
:width: 100%

In each panel, the gold node reads the nodes joined to it by gold lines. Only the GNN's wiring comes from the problem itself.
```

- **A sequence is a chain.** Take 5-minute speeds at one detector. Each time step is a node, joined to the
  step before it. An RNN passes its state along that chain with the same weights at every step.
- **An image is a grid.** Each pixel is a node joined to the pixels around it. A 3 &times; 3 CNN kernel
  reads a pixel's 8 neighbors and the pixel itself. The 3 &times; 3 grid of road cells in
  {doc}`3.2 <notes2-graph-basics>` is a tiny image, and the time&ndash;space diagram you ran a kernel over
  in {doc}`1.3 <../module1/notes3-cnn>` is a grid graph too.
- **Self-attention uses a complete graph.** In BERT every word reads every other word. In ViT every
  16 &times; 16 patch of an FL511 frame reads every other patch. Every pair is joined.
- **A road network is whatever the roads say.** An intersection reads only the intersections a car can
  reach from it directly.

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
| Graph convolution ({doc}`3.6 <notes6-message-passing>`) | a detector, a road cell, an intersection | its neighbors on the road | fixed in advance by how many links each node has |
| Graph attention ({doc}`3.7 <notes7-graph-attention>`) | the same | its neighbors on the road | computed from the content |

Read the last two rows against the rest. A graph convolution keeps the CNN's habit: the weights are fixed
before the data arrive. Graph attention takes BERT's habit: the weights are computed from the content.
The only new thing in either is where $N(i)$ comes from. It is not a pixel grid and not "everyone". It is
the road network you already manage.

## Attention patterns are graphs too

Only self-attention without a mask is a complete graph. The masks and variants you have already met each
change the graph.

```{figure} ../_static/figures/GNN2_Attention_As_Graphs.png
:alt: Four panels. Self-attention in BERT and ViT, a complete graph where every token reads every token. A causal mask in GPT, a directed graph pointing forward in time where token t reads tokens 1 to t and no edges point backward. Cross-attention in the DETR decoder, a bipartite graph where four object queries (100 in DETR) read every cell of the image feature grid from the encoder, with dashed lines showing that the queries also self-attend. Graph attention on a road graph, where the road is the mask, a node reads only its road neighbors, and pairs with no road link are crossed out as masked.
:width: 100%

Self-attention joins every pair; a causal mask keeps only forward edges; DETR's cross-attention joins object queries to the image feature grid; graph attention keeps only road neighbors.
```

- **A mask deletes edges that should not exist.** GPT's causal mask lets token t read only tokens 1 to t,
  so the complete graph becomes a directed graph that points only forward in time. A padding mask deletes
  the edges to padding tokens. Swin's windows keep only the edges inside each window.
- **Cross-attention joins two different sets of nodes.** Queries come from one set and keys and values from
  another, so every edge runs between the two sets and none runs inside a set. This is a **bipartite
  graph**. In the multimodal crash-warning example of {doc}`2.9 <../module2/notes9-cross-attention>`, text
  or CAN tokens read video tokens.
- **DETR uses both.** Its encoder runs self-attention over the image feature grid (a complete graph over the
  grid positions). Its decoder has 100 object queries. The queries self-attend among themselves (a complete
  graph over 100 nodes) and cross-attend to every position of the encoder's feature grid (a complete
  bipartite graph between the two sets).
- **Graph attention takes the mask from the problem.** A node may attend only to its neighbors in the road
  graph, so the adjacency matrix is the mask. {doc}`3.7 <notes7-graph-attention>` shows what that buys.

## Two dials make every architecture

```{figure} ../_static/figures/EMC_Two_Dials.png
:alt: A map with two axes. Vertical, who may talk, from a few fixed neighbors to everyone. Horizontal, how much each one counts, from fixed in advance to computed from the content. Bottom left, RNN, CNN and graph convolution. Top left, the dense layer: 600,100 weights where 8 convolution filters need 80. Right, self-attention and cross-attention near the top, Swin and graph attention near the bottom.
:width: 100%

Two dials make every architecture: who may talk, and how the weights are set. Graph convolution sits with the CNN; graph attention sits with Swin, a fixed set of neighbors with weights computed from the content.
```

This is the sense in which a graph neural network is the general form. Every point on that map is the same
update, with a particular graph and a particular rule for the weights. A graph network leaves both choices
open. Give it everyone-reads-everyone and computed weights, and you have self-attention. Give it the road
and fixed weights, and you have a graph convolution.

:::{admonition} Where the one picture is too neat
:class: note
- **A CNN has a different weight for each slot.** The upstream tap and the downstream tap of a 3-tap kernel
  are different numbers. As a graph, a 3 &times; 3 CNN has nine *kinds* of edge, one per slot. A plain
  graph convolution has one weight for every neighbor, so on a pixel grid it can only blur; it cannot find
  an edge in an image. The fix is to tell the edges apart. On a road the obvious kinds are upstream and
  downstream, and {doc}`3.7 <notes7-graph-attention>` shows that knowing direction is worth more than
  attention itself.
- **Position is what you add back after you throw the graph away.** When every token reads every token,
  the wiring says nothing about order, so BERT and ViT add position embeddings
  ({doc}`2.1 <../module2/notes1-tokens>`, {doc}`2.7 <../module2/notes7-vision>`). In a graph network the
  edges carry the structure. Swin's relative position bias ({doc}`2.8 <../module2/notes8-locality>`) is
  already a feature on an edge.
- **Cross-attention is a graph with two kinds of node.** Queries sit on one side, keys and values on the
  other, and the edges go one way. The lane-anchor hub of {doc}`2.11 <../module2/notes11-streams>` is the
  same idea with many kinds of node.
:::

## Why we need a more general model

Each older model leans on a regular shape, and transportation networks are not regular.

- **A CNN kernel needs a fixed number of slots in a fixed order.** In the grid, the corners have only 2
  neighbors, so a 3 &times; 3 kernel needs padding at the edges. In the real USF street network,
  intersections touch anywhere from 1 to 5 road links, and 77 percent do not have exactly four. There is
  no fixed layout to put in slots.
- **An RNN expects one predecessor.** Cell 5 receives traffic from two cells, 4 and 8.
- **A transformer can read anything, but it starts out treating every pair alike.** It must learn from data
  that cell 9 cannot pass traffic directly to cell 5. The road map tells you that for free.

A graph neural network keeps the best idea of each. Like a CNN or an RNN, it applies one shared rule
everywhere. Like attention, it accepts any number of neighbors in any order. And it takes who-reads-whom
from the problem itself: the road network, the power feed, the shared record ID.

:::{admonition} The point
:class: tip
A GNN is the general case. Give it a chain and it behaves like an RNN; give it a grid and a slot for each
neighbor and it behaves like a CNN; give it a complete graph with attention and it is a transformer. What
is new is that you hand it the graph.
:::

---

Next: {doc}`notes4-questions` &mdash; node, edge and graph questions.
