(ctm-message-passing)=
# 3.8 The cell transmission model already passes messages

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 3 &middot; Section 3.8</span>
    <span class="notes-card-session">Session: Graph neural networks</span>
  </div>
  <p class="notes-card-lede">Message, aggregate and update are nothing new. If you have run the cell transmission model, you have run a message-passing network: one CTM time step at cell 5 of the grid fills the same three slots, with rules derived from the fundamental diagram instead of fitted to data. That one word, derived versus fitted, is the whole trade between the two.</p>
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

Can a learned model stand in for a model you would otherwise write down? The honest way to answer is to
show that the classical traffic model *already is* the neural architecture. That puts the two on the same
footing instead of pitting a tuned network against a strawman. {doc}`1.3 <../module1/notes3-cnn>` does this
for a **corridor**, where Newell's model and the cell transmission model turn out to be convolutions. This
page does it for a **network**, where the cell transmission model (Daganzo, 1994) turns out to be a graph
neural network.

Here is one CTM time step at cell 5 of the grid from {doc}`3.2 <notes2-graph-basics>`, written in the three
message-passing slots of {doc}`3.6 <notes6-message-passing>`.

```{figure} ../_static/figures/GNN2_CTM_Grid_Update.png
:alt: Left, the 3 by 3 grid with each cell's density; cell 5 at 30 vehicles per mile becomes 32.0 at the next step. Arrows on cell 5's four faces carry the face flows, 1,125 vehicles per hour in from the west, the minimum of 1,125 and 1,250, 900 in from the south, 750 out to the east, the minimum of 1,125 and 750 because cell 6 is filling up, and 1,125 out to the north. Right, three boxes. Message: the flow across each face, the minimum of the demand toward it and the supply from it, with u 75 miles per hour, w 15 miles per hour, jam density 200 vehicles per mile and capacity 2,500 vehicles per hour. Aggregate: a sum, because vehicles are conserved, 2,025 in minus 1,875 out equals plus 150 vehicles per hour. Update: old density plus the change, 30 plus delta t over delta x times 150 equals 32.0 vehicles per mile.
:width: 100%

One CTM step at cell 5: four face flows (message), in minus out (aggregate), and the density update from 30 to 32.0 veh/mi (update).
```

## One CTM step at cell 5

**Setup.** One lane per cell and the course CTM parameters: free-flow speed u = 75 mi/h, wave speed
w = 15 mi/h, jam density K<sub>j</sub> = 200 veh/mi, capacity 2,500 veh/h, time step &Delta;t = 4.8 s,
cell size &Delta;x = 0.1 mi. Densities from the node table: cell 5 at 30 veh/mi; its west neighbor (cell 4)
at 30, south (8) at 24, east (6) at 100 and north (2) at 40. In this snapshot, half of each cell's traffic
heads east and half heads north, and each cell splits its free space evenly between the two directions it
receives from.

**Step 1: a message on every face.** The flow across each face is the smaller of what the upstream cell
wants to send in that direction and what the downstream cell can take from that direction. Sending is
S(k) = min(u&middot;k, capacity); receiving is R(k) = min(capacity, w&middot;(K<sub>j</sub> &minus; k)).

- West &rarr; 5: cell 4 wants to send half of 2,250 = 1,125 veh/h east; cell 5 can take half of
  2,500 = 1,250. **1,125** crosses.
- South &rarr; 5: cell 8 wants to send half of 1,800 = 900 north; cell 5 can take 1,250. **900** crosses.
- 5 &rarr; east: cell 5 wants to send 1,125 east, but cell 6, filling up at 100 veh/mi, can take only half
  of 1,500 = 750. **750** crosses.
- 5 &rarr; north: cell 5 wants to send 1,125 north; cell 2 can take half of 2,400 = 1,200. **1,125**
  crosses.

**Step 2: aggregate at cell 5.** Add what comes in and subtract what goes out:
(1,125 + 900) &minus; (750 + 1,125) = 2,025 &minus; 1,875 = **+150 veh/h**.

**Step 3: update cell 5.** Over one 4.8-second step on a 0.1-mile cell, a net inflow of 150 veh/h adds
2 veh/mi:

$$
k_5(t+1) = k_5(t) + \frac{\Delta t}{\Delta x}\Big(\sum_{j \to 5} y_{j5} - \sum_{5 \to j} y_{5j}\Big)
= 30 + \frac{4.8\ \text{s}}{0.1\ \text{mi}} \times 150\ \tfrac{\text{veh}}{\text{h}}
= 32.0\ \tfrac{\text{veh}}{\text{mi}}
$$

| Symbol | In words |
| --- | --- |
| $k_5(t)$ | density in cell 5 at step t (veh/mi) |
| $y_{j5}$, $y_{5j}$ | flow across the face from j into 5, and from 5 into j (veh/h) |
| $\Delta t / \Delta x$ | how much one step of net flow changes the density |

**In words:** each cell collects one flow per face with the same min rule, adds them up with a sign for
direction, and updates its density. That is message, aggregate, update. Every one of the nine cells does
the same thing at the same time, which is exactly what one message-passing layer does.

## The CTM and a GNN, slot by slot

```text
CTM, at one cell
────────────────
y      = min{ S(k_up), R(k_here) }   ← one rule, per connection
k(t+1) = k + Σ in − Σ out            ← conservation, however many faces

GNN, at one node
────────────────
m(j→i) = ψ(h_i, h_j, e_ji)           ← one rule, per connection
h_i'   = φ(h_i, ⊕ over j of m)       ← ⊕ takes however many messages
```

| Slot | CTM | GNN |
| --- | --- | --- |
| Node state $h_i$ | cell density $k_i$ | a learned vector |
| Edge feature $e_{ji}$ | which side: inflow (+) or outflow (&minus;) | direction, lanes, turn type, signal state |
| Message $\psi$ | flow = min(sending, receiving), derived from the fundamental diagram | a small neural network, fitted to data |
| Aggregate $\oplus$ | sum, because vehicles are conserved | sum, mean, max, or attention |
| Update $\phi$ | old density plus a change: k + (&Delta;t/&Delta;x) &times; net | a neural network, often old vector plus a change |
| One layer | one time step: a vehicle moves at most one cell (u&Delta;t/&Delta;x = 1) | one hop |
| Parameters | u, w, K<sub>j</sub>, &Delta;t, &Delta;x, the same for 9 cells or 90,000 | shared weights, with no N in the count |
| Where the rule holds | wherever the fundamental diagram holds | as far as the training data resembles the new case |

Nobody asks how many parameters the CTM has *for a given network*. The sending and receiving functions are
one pair of functions applied at every cell; the network decides only how many times you call them and who
talks to whom. A GNN is exactly that, with the per-connection rule **fitted** instead of **derived**.

## What the analogy teaches

1. **One CTM time step is one message-passing layer.** Run K steps and information travels K cells, because
   the CFL condition caps each step at one cell. That is exactly why one GNN layer reaches one hop, and why
   depth buys reach.
2. **The update adds a change to the old state.** The CTM writes k + &Delta;k. Many GNNs do the same,
   h + f(m), which is a residual (skip) connection, the same idea as in ResNet. It also slows
   oversmoothing.
3. **The aggregate follows the physics.** The CTM sums because vehicles are conserved. When you pick
   $\oplus$ for a GNN, ask the same question: what does the real system do with what arrives?
4. **The corners are the irregular part.** Corner cell 7 has no inflow at all, and corner cell 3 has no
   outflow. The same update law still works there, because a sum over zero or two faces is still a sum.
   That is the property a GNN keeps on real, irregular road networks.
5. **Derived rules vs fitted rules.** The CTM's message rule is derived, so it is right everywhere its
   fundamental diagram holds: you re-estimate a few parameters and take the topology from the network file.
   A GNN's rules are fitted, so they are right only as far as the new city or the new day resembles the
   training data. A GNN earns its place where nobody can write the rule down: mixed traffic, signal
   control, incidents, weather, or power and roads interacting.

:::{admonition} Going further &mdash; when supply must be shared
:class: note
In the snapshot above, cell 5 has room for everything that arrives. Now take a simple merge, where cells A
and B both feed cell C (capacity 2,500 veh/h). If A wants to send 2,250 and B 1,500, the total of 3,750 is
more than C can take, so C's supply must be **shared**. Split in proportion to demand (Jin and Zhang,
2003), A sends 1,500 and B sends 1,000. The message on A &rarr; C now depends on what B is sending. A share
that depends on the neighbors' states is exactly what an attention softmax computes
({doc}`3.7 <notes7-graph-attention>`), which is why attention suits merges.
:::

---

Next: {doc}`notes9-classification` &mdash; putting a head on the message-passing layers to answer node,
edge and graph questions.
