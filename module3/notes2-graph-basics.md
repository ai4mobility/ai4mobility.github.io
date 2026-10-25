# 3.2 Graph basics: nodes, edges and the whole graph

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 3 &middot; Section 3.2</span>
    <span class="notes-card-session">Session: Graph neural networks</span>
  </div>
  <p class="notes-card-lede">The vocabulary of graphs, with no learning yet. One example runs through the rest of the module: a 3 &times; 3 grid of road cells, the picture traffic flow theory uses for a cell transmission model. This page shows the pieces of a graph, the three tables a computer stores it in, and the first modeling decision you make: what is a node?</p>
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

A graph is a set of **nodes** joined by **edges**. That is the whole definition.

The running example is a **3 &times; 3 grid of road cells**. Each cell is 0.1 mile on a side. In this
snapshot, traffic moves east and north. The cells are numbered 1 to 9 from the north-west corner, so
cell 5 is in the center. Each cell is a node. Each face that traffic can cross from one cell into the
next is a directed edge.

```{figure} ../_static/figures/GNN2_Grid_Graph.png
:alt: Left, nine square road cells in a 3 by 3 grid, numbered 1 to 9 from the north-west corner, each with a density, cell 1 20, cell 2 40, cell 3 50, cell 4 30, cell 5 30, cell 6 100, cell 7 15, cell 8 24 and cell 9 70 vehicles per mile; traffic moves east and north. Right, the same cells as a graph with 9 nodes and 12 directed edges, labeled node, node feature, directed edge 4 to 5, neighbors of 5 (2, 4, 6 and 8, joined by gold edges), edge features, graph features, and corner cell 7 with in-degree 0 and out-degree 2.
:width: 100%

Left: nine road cells with their densities (synthetic). Right: the same cells as a graph, with each piece of graph vocabulary labeled. The gold edges are cell 5's.
```

## The pieces

| Term | Meaning | In the grid |
| --- | --- | --- |
| Node (vertex) | One thing with its own state | A cell, 1 to 9 |
| Edge (link) | A connection between two nodes | Traffic can cross from cell 4 into cell 5 |
| Directed edge | i &rarr; j is not the same as j &rarr; i | 4 &rarr; 5 exists; 5 &rarr; 4 does not, because traffic moves east |
| Undirected edge | The connection works both ways | Two counties that share a border |
| Weighted edge | The edge carries a number | Face width, lanes, or capacity (veh/h) |
| Neighbors, $N(i)$ | Nodes joined to i by an edge | $N(5) = \{2, 4, 6, 8\}$: cells 4 and 8 send traffic into 5; cell 5 sends to 6 and 2 |
| Degree | How many edges touch a node | Cell 5: in-degree 2, out-degree 2. Corner cell 7: in-degree 0, out-degree 2 |
| Node features | Numbers that describe a node | Density k (veh/mi), lanes, cell length |
| Edge features | Numbers that describe an edge | Face width, lanes, signal state |
| Graph $G = (V, E)$ | All nodes V and all edges E together | The whole grid: 9 nodes, 12 directed edges |
| Graph features | Numbers about the whole graph | Time of day, weather, an incident flag |

Degree varies even on a tidy grid. The center cell touches 4 cells, the cells in the middle of each side
touch 3, and the corners touch 2. Real road networks vary much more ({doc}`3.1 <notes1-graph-data>`).

## Storing a graph: three tables

```{figure} ../_static/figures/GNN2_Grid_Adjacency.png
:alt: Three tables for the grid. A node table with one row per cell and its density in vehicles per mile. A 9 by 9 adjacency matrix with rows labeled from cell and columns labeled to cell; row 5 has ones in columns 2 and 6 (out-degree 2) and column 5 has ones in rows 4 and 8 (in-degree 2); 12 of 81 entries are 1. An edge list with one row per directed edge, its from cell, to cell and direction, east or north.
:width: 100%

The node table, the adjacency matrix (row 5 and column 5 outlined) and the edge list for the grid.
```

**1. The node table X.** One row per node, one column per feature. With N nodes and d features, X is
N &times; d. Here N = 9, and the first feature is density.

| Cell | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| k (veh/mi) | 20 | 40 | 50 | 30 | 30 | 100 | 15 | 24 | 70 |

**2. The adjacency matrix A.** An N &times; N table that says which pairs are connected.

$$
A_{ij} =
\begin{cases}
1 & \text{if an edge runs from node } i \text{ to node } j \\
0 & \text{otherwise}
\end{cases}
$$

**In words:** a row is where traffic leaves, a column is where it arrives. Row 5 has 1s in columns 2 and
6, because cell 5 sends traffic north and east. Column 5 has 1s in rows 4 and 8, because cells 4 and 8
send traffic into cell 5. Adding up a row gives the out-degree; adding up a column gives the in-degree.

Three variations you will meet in papers:

- **Undirected graph:** A is symmetric, $A_{ij} = A_{ji}$.
- **Weighted graph:** the 1 becomes a number, such as lanes, capacity, or a weight that falls with road
  distance (the METR-LA graph in {doc}`3.1 <notes1-graph-data>`).
- **Self-loops:** a 1 on the diagonal, $A_{ii} = 1$, when a node should also read its own state. You
  will see this again in the graph convolution of {doc}`3.6 <notes6-message-passing>`.

**3. The edge list.** Only the edges that exist, one row each. The grid has 12: six eastward, (1, 2),
(2, 3), (4, 5), (5, 6), (7, 8), (8, 9), and six northward, (4, 1), (5, 2), (6, 3), (7, 4), (8, 5),
(9, 6). Edge features ride along on each row.

Why keep an edge list when the matrix says the same thing? Real networks are sparse. The grid's matrix
has 12 ones out of 81 entries (15 percent), but the USF street network's matrix has 245,025 entries and
only 0.6 percent of them are ones. Graph software such as PyTorch Geometric stores the edge list for
this reason.

## A road can be a node or an edge

A street map gives you two natural graphs, and it is worth getting this straight early.

- **Intersections as nodes.** Each road block between two intersections is an edge. This is the graph
  you would draw first.
- **Road blocks as nodes.** Now each block is a node, and two blocks are joined when they meet at an
  intersection. The intersection has turned into edges: where d blocks meet, it produces d(d &minus; 1)/2
  edges, one for each pair of blocks. This second graph is called the **line graph**.

On a small 2 &times; 3 street grid, the first graph has 6 nodes (intersections) and 7 edges (blocks). The
second has 7 nodes (blocks) and 10 edges. The same physical intersection is a node in one graph and a
bundle of edges in the other.

```{figure} ../_static/figures/GNN2_Node_Or_Edge.png
:alt: Three panels of the same 2 by 3 street grid. On the map, 6 intersections I1 to I6 and 7 road blocks b1 to b7. Intersections as nodes, 6 nodes and 7 edges, each block an edge between its two intersections. Blocks as nodes, the line graph, 7 nodes and 10 edges joining pairs of blocks that meet; intersection I2, where three blocks meet, becomes three gold edges, and d blocks meeting give d times d minus 1 over 2 edges.
:width: 100%

The same streets three ways. In the line graph (right), intersection I2, where three blocks meet, becomes the three gold edges.
```

Which one is right? Neither. The rule is: **put the node where the state you care about lives.**

| The state you want to know | Make this the node |
| --- | --- |
| Speed at a sensor | The detector station |
| Density or travel time on a road | The directed road block (or each CTM cell) |
| Queue or signal phase | The intersection |
| Turning delay or spillback on one movement | The directed link, so each movement becomes an edge |
| Outage duration | The county, or the power feeder |
| Pump or signal status after a storm | The infrastructure asset |

Direction splits a road. Northbound and southbound I-275 at the same mile marker carry different states,
so they are two nodes. Granularity is also your choice, just as whole words versus word pieces was for a
tokenizer: one link can be one node, or ten 0.1-mile cells. Our 3 &times; 3 grid already made the
"road as node" choice: the cells are pieces of road, and the faces between them are the edges.

Zoom into one four-leg intersection with directed links as nodes, and its 12 turning movements become the
edges. Max-pressure signal control in {doc}`3.6 <notes6-message-passing>` uses exactly this graph.

```{figure} ../_static/figures/GNN_Two_Tokenizations.png
:alt: Three panels. A four-leg intersection with two-way roads. The same intersection as a graph with the intersection as a node, 5 nodes and 4 edges. The same intersection with each directed road link as a node, 4 inbound and 4 outbound, joined by 12 turning movements colored through, left and right.
:width: 100%

One intersection, two graphs. With intersections as nodes, the roads are the edges. With directed road links as nodes, the 12 turning movements are the edges, each able to carry a turn volume.
```

## Nodes and edges of different kinds

The grid has one kind of node and one kind of edge. Many agency systems mix kinds. The hurricane system
in {doc}`3.1 <notes1-graph-data>` has substations, signals, pumps, road segments and shelters, joined by
edges such as **powers**, **drains**, **controls** and **connects**. The hurricane data graph mixes
procedures, app records, spreadsheets and forms, joined by shared IDs, places and times. A graph with
typed nodes and typed edges is called a **heterogeneous graph**. Each edge type usually needs its own
message rule, because "powers" and "connects" do not pass the same kind of information. The lane-anchor
hub of {doc}`2.11 <../module2/notes11-streams>` was already one: lane cells of different kinds joined by
edges of different kinds.

---

Next: {doc}`notes3-one-view` &mdash; why the networks of Modules 1 and 2 are graph models too.
