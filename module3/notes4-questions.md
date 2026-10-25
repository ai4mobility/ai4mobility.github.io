# 3.4 Three kinds of questions you can ask a graph

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 3 &middot; Section 3.4</span>
    <span class="notes-card-session">Session: Graph neural networks</span>
  </div>
  <p class="notes-card-lede">Every graph problem asks its question about a node, about an edge, or about the whole graph. Name the level first: it decides what one training sample is and which labels you must collect. This page gives transportation examples at each level, from a dark signal after a storm to whether a city's network is about to percolate.</p>
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

Every graph problem asks its question at one of three levels: about a **node**, about an **edge**, or about
the **whole graph**. Name the level first. It decides what one training sample is and which labels you
must collect. Each level can ask a yes/no question (classification) or a how-much question (regression).
How a model answers at each level is in {doc}`3.9 <notes9-classification>`; this page is about the
questions.

```{figure} ../_static/figures/GNN2_Three_Levels.png
:alt: Three copies of the same small graph. Node level, one node highlighted in gold, one answer per node, for example is this signal dark right now, or the speed at a failed detector, like BERT labeling each token. Edge level, one pair of nodes highlighted, one answer per pair, for example does this substation feed this signal, or trips from zone i to zone j, like word2vec scoring a pair. Graph level, the whole graph highlighted, one answer per graph, for example is the downtown grid near gridlock, or minutes until an incident clears, like the CLS token or global average pooling.
:width: 100%

The gold part is what the answer is about: one node, one pair of nodes, or the whole graph.
```

## Node level: one answer per node

- **Is the signal at this intersection dark?** After a hurricane, a signal goes dark when its power feed is
  out. If the signals on both sides of it on the same corridor are dark, it probably is too.
  *(classification)*
- **What is the missing value at this node?** A loop detector fails and reports nothing, but the detectors
  upstream and downstream still report. Estimate its speed from them. *(regression)*
- **Will this intersection saturate in the next 15 minutes?** Agencies that run automated traffic signal
  performance measures (ATSPM) log split failures every cycle, so the labels already exist.
  *(classification)*
- **What will the speed be at every detector 15 to 60 minutes ahead?** This is the most common traffic GNN
  task, and METR-LA is the benchmark most papers report. *(regression)*

## Edge level: one answer per pair of nodes

- **Does a connection exist?** Which substation feeds this traffic signal? The electric utility holds that
  table; the county often does not. *(link prediction)*
- **How strong is the connection?** How many trips go from zone i to zone j? How strongly does delay at one
  intersection carry into the next? *(regression)*
- **How do two infrastructure systems depend on each other?** If this pump station loses power, does this
  road segment flood? Power, stormwater and traffic are separate networks joined by edges that nobody draws
  on one map. *(classification: critical or not)*
- **Will this pair of road users conflict?** In the intersection graph of {doc}`3.1 <notes1-graph-data>`,
  will the post-encroachment time between the turning car and the pedestrian drop below a threshold such as
  1.5 s? *(classification)*

## Graph level: one answer for the whole graph

- **Is the downtown grid near gridlock?** *(classification)*
- **Is the network about to percolate?** Keep only the roads that are still running near free-flow speed.
  They form connected clusters. As congestion grows, the largest free-flowing cluster can suddenly break
  into pieces, the way a percolation transition does in physics; Li and colleagues (PNAS, 2015) measured
  this on Beijing's road network. Will that break happen in the next 30 minutes? *(classification)*
- **How long until this network breaks down?** Given the current state and demand, how many minutes until
  speeds collapse? *(regression)*
- **How soon will an incident clear?** A crash blocks two of four lanes on a freeway. Make each lane of each
  0.1-mile cell a node, with edges for moving forward and for changing lanes. How many minutes until every
  lane is back to normal speed? *(regression)*
- **How far will a disaster cascade?** One substation fails. How many signals go dark, how many road
  segments flood, how many shelters lose access? *(regression)*

```{figure} ../_static/figures/GNN_Infrastructure_Graph.png
:alt: An illustrative neighborhood as a graph with five node types, substation, traffic signal, stormwater pump, road segment and shelter, and four edge types, powers, drains, meters flow onto and connects. Substation 1 fails. In hop 1 signals A and B go dark and the stormwater pump stops; in hop 2 road 2, a low road, floods; in hop 3 the shelter loses its direct route, while a detour via road 3, fed by substation 2 and signal C, stays open.
:width: 100%

An illustrative coastal neighborhood. When substation 1 fails, signals A and B go dark and the pump stops (hop 1), road 2 floods (hop 2), and the shelter loses its direct route (hop 3).
```

At graph level, one sample is one **snapshot** of the whole network. A single city over a year gives you
thousands of snapshots. Gridlock, percolation and major cascades are rare in real data, so their labels
usually come from a simulator.

## One storm, three levels

The same hurricane data can feed all three levels. The level you pick decides the labels you need.

| Level | The question | One sample | Labels come from |
| --- | --- | --- | --- |
| Node | Is this signal dark right now? | one signal at one time | field damage reports, signal status in the traffic management system |
| Edge | Does this substation feed this signal? | one substation&ndash;signal pair | the utility's feeder records |
| Graph | How many hours until 90% of signals are powered again? | the whole county at one time | restoration logs from past storms |

---

Next: {doc}`notes5-node-embeddings` &mdash; turning each node into a vector, the way language turned each
word into one.
