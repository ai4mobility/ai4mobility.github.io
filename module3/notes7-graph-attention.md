(graph-attention)=
# 3.7 Graph attention: the road as the attention mask

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 3 &middot; Section 3.7</span>
    <span class="notes-card-session">Session: Graph neural networks</span>
  </div>
  <p class="notes-card-lede">Graph attention is the attention of BERT and ViT with one change: the softmax runs only over a node's neighbors in the graph. The road becomes the attention mask. This page works the weights out at cell 5 of the grid, shows them flip from upstream to downstream as the cell fills, and asks when the mask is worth keeping. On roads, the evidence says almost always.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Interactive companion for this module</h4>
      <ul>
      <li><a href="../_static/companions/GNN_On_A_Road_Network_Companion.html" target="_blank" rel="noopener">A GNN on a road network &#8599;</a> &mdash; tab 5, embedded in <a href="notes6-message-passing.html">3.6</a></li>
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

A graph convolution ({doc}`3.6 <notes6-message-passing>`) fixes how much each neighbor counts before any
traffic arrives. Attention computes those weights from the traffic itself. The figure shows the
difference at cell 5 of the grid, using the densities below as a share of jam density.

```{figure} ../_static/figures/GNN2_Conv_vs_Attention_Cell5.png
:alt: Three copies of the 3 by 3 grid with densities as a share of jam density, cell 1 0.1, cell 2 0.2, cell 3 0.25, cell 4 0.15, cell 5 0.15, cell 6 0.5, cell 7 0.07, cell 8 0.12 and cell 9 0.35, and the weight cell 5 gives each other cell. Convolution, the grid says who and link counts say how much, 0.224 to each of cells 2, 4, 6 and 8 and 0.200 to itself, whatever the traffic is doing. Graph attention, the grid says who and Q dot K says how much, cell 4 0.337, cell 8 0.323, cell 6 0.205 and cell 2 0.134: nearly empty, cell 5 listens to the cells that feed it. Full attention, nobody says who, all eight other cells get weight, and the corner cells, which cannot pass traffic to cell 5, take 47 percent of it.
:width: 100%

Left: a GCN gives cells 2, 4, 6 and 8 the same weight. Middle: graph attention keeps the grid's neighbors and computes the weights from the states. Right: without a mask, corner cells that cannot pass traffic to cell 5 take 47 percent of the weight.
```

## The rule

$$
\alpha_{ij} = \operatorname*{softmax}_{j \in N(i)} \Big( \frac{q_i \cdot k_j}{\sqrt{d}} \Big)
\qquad
h_i^{(l+1)} = \sum_{j \in N(i)} \alpha_{ij}\, v_j
$$

| Symbol | In words | At cell 5 |
| --- | --- | --- |
| $q_i = W_Q h_i$ | what node i is asking: "am I filling up?" | $q_5 = [-0.35,\ 1.00]$ when cell 5 is at 0.15 of jam density |
| $k_j = W_K [h_j, e_{ji}]$ | what neighbor j offers, including which side it is on | $k_6 = [2.00,\ 1.00]$ for downstream cell 6 |
| $v_j$ | what neighbor j sends | cell j's density |
| $\alpha_{ij}$ | how much i listens to j; the weights sum to 1 | 4: 0.337, 8: 0.323, 6: 0.205, 2: 0.134 |
| $\sqrt{d}$ | the same scaling as in BERT | $\sqrt{2}$ here |

**In words:** each node scores its neighbors by how well what they offer matches what it is asking, turns
the scores into weights that sum to 1, and takes the weighted mix. It is the attention of
{doc}`2.3 <../module2/notes3-attention>`, with the softmax limited to the road neighbors. In the
message-passing slots of {doc}`3.6 <notes6-message-passing>`, the message is $\alpha_{ij} v_j$ and the
aggregate is a sum; the weights are what changes.

**A worked example.** Use the grid's densities as a share of jam density: cell 4 at 0.15, cell 8 at 0.12,
cell 6 at 0.50, cell 2 at 0.20, and cell 5 itself at 0.15. A small attention layer with 10 hand-set weights
(the one in tab 5 of the companion) gives cell 6 the score
(&minus;0.35 &times; 2.00 + 1.00 &times; 1.00) / &radic;2 = 0.212 and cell 4 the score 0.707. After the
softmax, cell 5 gives 0.337 to cell 4, 0.323 to cell 8, 0.205 to cell 6 and 0.134 to cell 2. It is nearly
empty, so it listens to the cells that feed it.

## The weights change with the traffic

Slide cell 5's own density and the ranking flips:

- Cell 5 nearly empty (0.05 of jam density): it listens upstream. Cell 4 gets the most weight, **0.368**.
- Cell 5 nearly full (0.95): it listens downstream. Cell 6 gets **0.503**.
- The flip happens when cell 5 reaches 0.325 of jam density.

A traffic engineer would expect exactly this. In free flow, what arrives from upstream decides your future.
In congestion, whether downstream can take your vehicles decides it. That is the CTM's sending and
receiving split ({doc}`3.8 <notes8-ctm>`), now learned instead of written down. A GCN cannot make this
flip, because its weights never look at the states.

The price: with 64 numbers per node, an attention layer with separate Q, K and V matrices has 12,480
weights, three times a GCN layer.

## In code: one line added to BERT's attention

On the two-dials map of {doc}`3.3 <notes3-one-view>`, graph attention sits next to Swin: the road fixes who
may be read, and the content sets the weights. In code it is one line added to the attention of
{doc}`2.3 <../module2/notes3-attention>`:

```python
scores = Q @ K.T / d**0.5                           # every pair, as in BERT
scores = scores.masked_fill(A == 0, float('-inf'))  # road neighbors only
alpha  = scores.softmax(dim=-1)                     # weights sum to 1
H_new  = alpha @ V
```

```{figure} ../_static/figures/GNN_Who_Reads_Whom.png
:alt: Three panels. BERT or ViT, seven words all joined to each other, with an all-ones 7 by 7 table. Swin on a 4 by 4 grid of patches in four 2 by 2 windows, with a block-diagonal 16 by 16 table, 64 of 256 entries on. A street network of 8 intersections and 10 road links, intersection 5 joined to 2, 4, 6 and 7, with a sparse 8 by 8 table, 28 of 64 entries on.
:width: 100%

The table A in the code above, for three architectures. BERT and ViT: every token reads every token, so the table is all ones. Swin: only the window (a toy 4 &times; 4 grid; Swin uses 7 &times; 7 windows). A street network: only the intersections a car reaches directly. In all three, a token also reads itself.
```

With A all ones this is BERT or ViT. A lower-triangular A gives GPT's causal mask
({doc}`2.4 <../module2/notes4-gpt>`). Window blocks give Swin. The road's adjacency, with each node also
reading itself, gives graph attention. Keep those self-links: a node with no neighbor at all (a detector
that no other detector is close to by road, say) would otherwise leave the softmax an empty row with no
answer. The mask is the teaching version. Graph libraries compute scores only along the edges that exist,
which is why they scale to a whole city where every-pair attention would not.

:::{admonition} Going deeper &mdash; which "graph attention"? Read the paper carefully
:class: dropdown
The original graph attention network (Veličković et al., ICLR 2018), which most papers cite as "GAT," does
not use separate queries and keys. It scores each edge with one shared weight matrix and one attention
vector, and as a result every node ranks its neighbors in the same order, whichever node is asking. Brody,
Alon and Yahav call this *static* attention (*How Attentive are Graph Attention Networks?*, ICLR 2022). It
can never make the flip above. The query&ndash;key version on this page, where the ranking can change with
the asking node's own state, is the GATv2 and graph transformer line. When a paper says "GAT," check which
one. The optional last part of Lab 5 measures the difference on a traffic rule where the neighbor that
matters flips with the receiving link's own density.
:::

## Do we always apply a mask before graph attention?

No, but it is the usual default when the graph is known and trusted. Practice falls into three groups:

| Practice | Who reads whom | Where the graph enters | Examples |
| --- | --- | --- | --- |
| Masked graph attention | neighbors in A only | the mask is built in: scores are computed only along existing edges | GAT, GATv2, TransformerConv |
| Graph transformer | every node | structure is added back as biases or encodings, such as hop distance, edge type and node degree | Graphormer |
| Hybrid | both, side by side | each block runs a local message-passing layer next to a global attention layer | GraphGPS |

In masked graph attention you never apply the mask as a separate step: the layer only ever computes scores
for the edges in the graph, which is also why it scales to large graphs. Full attention costs a score for
every pair of nodes. That is 42,849 pairs for METR-LA's 207 detectors, which is affordable, but far too many
for a statewide road network. Traffic forecasting uses both styles. GMAN (2020) lets every sensor attend to
every other sensor and feeds in spatial embeddings learned from the road graph. ASTGCN (2019) multiplies a
learned spatial-attention matrix into a graph convolution over the road graph.

The evidence from the companion and Lab 5 explains why the mask is the default for roads. In tab 5, the
same 10-weight attention layer was trained three ways and tested on street networks it had never seen
(synthetic networks, a spillback rule, 6 seeds). With no road mask the error was 0.0839, barely better than
predicting no change at all (0.0870). With the road mask it fell to 0.0556, and adding direction on the
edges took it to 0.0286, with the same ten weights. Lab 5 found the same order on a merge rule: telling the
model which neighbors matter (reading only upstream links) cut the error from 0.0214 to 0.0122, 43 percent,
at no cost in parameters, and learning attention weights on top cut a further 10 percent, to 0.0110, with
twice the parameters. On the spillback rule, attention only tied the fixed "worst downstream neighbor" rule
(0.0080 against 0.0081).

:::{admonition} Before you trust this result
:class: important
**What is the baseline?** · **How was the data split, and why is that honest?** ·
**What does it do on the ugly cases?**

Two baselines: persistence (predict that nothing changes), and, the one that bites, a fixed aggregator that
encodes what a traffic engineer already knows (queues back up from the worst downstream link; flow arrives
from upstream). Beating a plain mean proves nothing; beating the engineer's rule is the bar. The split is
by network: the test networks were never seen in training, and the companion reports 6 seeds. The ugly
case is a rule where the neighbor that matters depends on the receiving link's own state; static attention
cannot represent it, which is what the optional part of Lab 5 tests. As in {doc}`3.6 <notes6-message-passing>`,
the ground truth is a rule written down in code, so take the ordering of the results, not their size.
:::

## The filters at a glance

|  | Who node i reads | How much each neighbor counts | Learned | Closest cousin |
| --- | --- | --- | --- | --- |
| Max pressure | the links a movement feeds | fixed by measured turning ratios | nothing | a GCN layer with physics weights |
| Convolution (GCN) | its neighbors in A | fixed by link counts | W only | a CNN with a frozen, equal-weight kernel |
| Graph attention | its neighbors in A | computed from the states ($q \cdot k$) | $W_Q, W_K, W_V$ | Swin: a fixed window with attention inside |
| Full attention (graph transformer) | every node | computed from the states, plus structural biases | $W_Q, W_K, W_V$ | BERT, ViT |

---

Next: {doc}`notes8-ctm` &mdash; the model you already know that has been passing messages all along.
