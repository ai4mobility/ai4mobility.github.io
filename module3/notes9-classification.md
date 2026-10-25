(graph-classification)=
# 3.9 Node, edge and graph classification

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 3 &middot; Section 3.9</span>
    <span class="notes-card-session">Session: Graph neural networks</span>
  </div>
  <p class="notes-card-lede">The message-passing layers are a backbone: they return one contextual vector per node. A small head on top answers the question at the level you need &mdash; one answer per node, per pair of nodes, or for the whole network. This page builds the three heads, shows why a graph model can tell apart two networks that every average says are the same, and closes the method with where it breaks and its fit card.</p>
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

The message-passing layers are a **backbone**: after L layers they return one contextual vector per node,
$h_i^{(L)}$, each carrying what its node saw L hops out. A small **head** on top answers the question at the
level you need ({doc}`3.4 <notes4-questions>`). You met backbones and heads in Modules 1 and 2 (BERT's
four heads in {doc}`2.5 <../module2/notes5-bert>`); a GNN is the same pattern.

```{figure} ../_static/figures/GNN_MP_Three_Heads.png
:alt: Left, a small street graph after the backbone, each intersection holding a short vector, with the note that the backbone is L message-passing layers and each vector holds what its node saw L hops out. Right, three heads. Node head, the same small layer on every vector, answering saturated or not for every intersection, like BERT labeling every token. Edge head, combine the two end vectors and score the pair, answering will this link spill back or does it exist, like word2vec and CLIP scoring a pair. Graph head, pool all vectors with a sum, mean or max, answering is the whole network near gridlock, like the CLS token or a CNN's global average pool.
:width: 100%

The same backbone vectors feed three heads: one answer per node, per pair of nodes, or for the whole network.
```

## Node classification: one answer per node

Apply the same small layer to every node's final vector:

$$
\hat y_i = \operatorname{softmax}\big(W_{\text{node}}\, h_i^{(L)}\big)
$$

**In words:** each node's vector goes through one shared layer and comes out as class probabilities, such
as powered or dark. This is BERT labeling every token.

- **Example:** after a storm, is each signal dark? The node is the signal; its features can include the
  outage status of its area, its traffic management system status and nearby field reports.
- **Training:** cross-entropy on the nodes that have labels. Often only some nodes are labeled (the signals
  crews have already checked), and the model fills in the rest. That is called semi-supervised node
  classification.
- **Baseline to beat:** the most recent field report, or a majority vote of the neighboring signals.

## Edge classification and link prediction: one answer per pair

Combine the two end vectors, then score the pair. There are two versions, and it matters which one you
have.

$$
\hat y_{ij} = \operatorname{softmax}\big(W_{\text{edge}}\,[\,h_i^{(L)},\, h_j^{(L)},\, e_{ij}\,]\big)
\qquad
s_{ij} = \sigma\big(h_i^{(L)} \cdot h_j^{(L)}\big)
$$

- **Edge classification (left):** the edge exists and you want to label it. Join the two node vectors and
  the edge's own features, then classify. Will the turning car and the pedestrian conflict? Will this
  left-turn movement spill back this cycle? Is this power-to-pump dependency critical?
- **Link prediction (right):** you do not know whether the edge exists. Score every candidate pair with a
  dot product and a sigmoid, the same score word2vec's skip-gram used. Train on the edges you know plus
  randomly drawn non-edges, which is word2vec's negative sampling again. Does this substation feed this
  signal? Which damage report and which work order describe the same signal? This is how a model helps
  make an implicit graph explicit ({doc}`3.1 <notes1-graph-data>`).
- **Baseline to beat:** for the substation question, "the nearest substation feeds it."

Pick the decision threshold from the costs, not at 0.5. A false positive sends a crew to a signal that was
never on that feeder. A false negative leaves a dark signal off the restoration list. The second is a
safety problem.

## Graph classification: one answer for the whole network

Pool all node vectors into one graph vector g, then classify it:

$$
g = \sum_{i \in V} h_i^{(L)}
\qquad
\hat y = \operatorname{softmax}\big(W_{\text{graph}}\, g\big)
$$

The pooling can be a sum, a mean, a max, or an attention-weighted sum. The pooled vector plays the role of
BERT's [CLS] token or a CNN's global average pooling. Two example questions:

- **Is the downtown grid near gridlock?** Baseline to beat: the macroscopic fundamental diagram (MFD).
  Average network density is a graph readout: mean pooling with zero message-passing layers.
- **Is the network about to percolate?** Keep only the links still running near free-flow speed, and watch
  the largest connected cluster they form. Near a critical level of congestion, that cluster breaks apart
  quickly. Measuring today's clusters needs no learning at all: it is a connected-components calculation on
  the speed map. Predicting whether the break will happen in the next 30 minutes, from today's state and
  demand, is the graph-classification task.

```{figure} ../_static/figures/GNN_MP_Same_Numbers.png
:alt: Two 5 by 5 street grids with 40 links each, 8 full at 0.90 of jam density and the rest free at 0.25. In A, the eight full links form a closed ring around one block, where every car waits on the car ahead. In B, the same eight full links are scattered, each surrounded by empty road. Without edges A and B are identical, mean 0.38, standard deviation 0.26, the same histogram and the same MFD point. One message-passing layer, am I full times how many full links touch me, then a sum readout gives A 16 and B 0; the largest connected jam is 8 links against 1.
:width: 100%

Two synthetic snapshots of a 5 &times; 5 street grid with the same 40 link densities, arranged differently. Only a model that reads the edges can tell them apart.
```

**Why the graph matters here: same 40 numbers, different network.** Take a synthetic 5 &times; 5 street
grid with 40 links, 8 of them full (0.90 of jam density) and the rest free (0.25). Arrange the 8 full links
two ways. In snapshot A they form a closed ring around one block, where every car waits on the car ahead and
nothing drains: gridlock. In snapshot B they are scattered, each surrounded by empty road. Both snapshots
have mean density 0.38, standard deviation 0.26, and the same histogram, so the MFD sees two identical
networks. One hand-set message-passing layer ("am I full, and how many full links touch me?") followed by a
sum readout gives **16 for A and 0 for B**. The largest connected jam is 8 links in A and 1 link in B: the
same cluster idea that percolation measures. The difference was never in the numbers. It was in who is next
to whom.

## Regression uses the same heads

For a how-much question, keep the head and change the output and the loss: one number instead of class
probabilities, and squared error instead of cross-entropy.

| Level | Classification example | Regression example |
| --- | --- | --- |
| Node | Is this signal dark? | Speed at a failed detector |
| Edge | Will the car and the pedestrian conflict? | Trips from zone i to zone j |
| Graph | Will the network percolate in 30 minutes? | Minutes until incident congestion clears |

## The three heads side by side

|  | Node head | Edge head | Graph head |
| --- | --- | --- | --- |
| What it reads | one node's vector | two end vectors (+ edge features) | all node vectors, pooled |
| Like | BERT labeling each token | word2vec and CLIP scoring a pair | [CLS], global average pooling |
| One training sample | a node in a snapshot | a pair in a snapshot | a whole snapshot |
| Baseline to beat | last report, neighbor majority | nearest asset, existing records | MFD average density, today's cluster sizes |

## Where it breaks

The failure that matters most for an agency is often not accuracy but transferability, and the litmus test
in {doc}`3.6 <notes6-message-passing>` catches it at a glance: does the number of nodes appear in the
parameter count? The rest of the list:

- **The graph is wrong.** Edges are missing or wrong, which is common when the graph is implicit and had to
  be built from records ({doc}`3.1 <notes1-graph-data>`).
- **Neighbors that need different weights get one.** Upstream and downstream, or a left turn and a through
  movement, are interchangeable to the model unless edge features or edge types say otherwise.
- **Influence travels farther than the layers reach.** A queue that starts six hops away is invisible to a
  three-layer model.
- **The degree distribution shifts between cities** while the aggregate is a sum, or two intersections are
  structurally identical and operationally nothing alike.
- **The real coupling is off the network.** A detour, a special event or weather links places that no road
  edge joins.

| Fit card &mdash; message-passing graph neural network | |
| --- | --- |
| **Idea in one sentence** | Each node collects a message from every neighbor with one shared rule, combines them, and updates itself; a small head reads the result per node, per edge or per graph. |
| **Why it works** | The graph says who can influence whom, so the model does not have to learn it; a shared local rule runs on any network size and any number of neighbors, and L layers turn a one-hop rule into an L-hop model. |
| **Fits these tasks** | Network speed forecasts, saturation and spillback warnings, missing-sensor estimates, road-user conflict warnings, outage spread, finding unrecorded dependencies, gridlock and percolation risk. *Leverage: prediction, classification, retrieval.* |
| **Needs this data** | Node features on a graph you can defend; labels on some nodes, edges or snapshots; months of detector or signal logs, asset and utility inventories, trajectories, or a calibrated simulator. **More than one network**, if transfer is ever the goal. |
| **Breaks when** | Edges are missing or wrong; neighbors that need different weights get one; influence travels farther than the layers reach; N appears in the parameter count; the new city differs from the training city. |
| **Keep the classical method when** | One corridor with known physics (CTM, Kalman filter); the network average answers the question (MFD); today's state is a graph calculation (connected components, max pressure); a per-sensor time-of-day average already meets the accuracy the decision needs; or the answer is a lookup in a table you already have. |

:::{admonition} Before you trust a graph model
:class: important
**What is the baseline?** · **How was the data split, and why is that honest?** ·
**What does it do on the ugly cases?**

**Baseline:** does it beat the simple rule in the last row of the table of heads above, and "tomorrow looks
like today"? **Split:** were the test days, or the test networks, kept apart from training? Nodes in the
same snapshot share information through their edges, so a random split of nodes leaks answers. Split by
day or by area. **Ugly cases:** how does it do on storm days, incident days, and graphs with missing edges?
:::

---

Next: {doc}`notes10-labs` &mdash; the lab, the questions this module arms you with, and further reading.
