(graph-neural-networks)=
# 3.1 Graphs everywhere in transportation

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 3 &middot; Section 3.1</span>
    <span class="notes-card-session">Session: Graph neural networks</span>
  </div>
  <p class="notes-card-lede">Much transportation data is neither a sequence nor an image. It is a set of things plus the connections between them: a graph. This page shows where graphs turn up in research and in agency practice, from a street network to the records an agency keeps about one traffic signal after a hurricane, and why the graph usually has to be built before any model can use it.</p>
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
      <li><a href="../module1/lab2_word_embeddings.html">Lab 2 &mdash; From Word2Vec to Road2Vec</a>: the USF street network on this page</li>
      </ul>
    </div>
  </div>
</div>

So far in this course, data has come in two tidy shapes. A **sequence** is a line of items: the words in
a crash narrative, or 5-minute speeds at one detector. An **image** is a grid of pixels from a dash
camera or an FL511 traffic camera.

Much transportation data has neither shape. It is a set of things plus the connections between them.
That shape is a **graph**. In a graph there is no fixed "next item" or "pixel to the left." Each thing
can have any number of connections, and the connections often carry the most important information.

## Graphs in research

| Data | The things (nodes) | The connections (edges) | A question you might ask |
| --- | --- | --- | --- |
| Urban road network | Intersections | Road segments between them | Which intersections will back up next? |
| Freeway detector network (METR-LA: 207 loop detectors in Los Angeles) | Detectors | Detectors close to each other by road | What will the speed be at each detector in 30 minutes? |
| Transit network | Stops and stations | Routes serving consecutive stops | Where will one late bus cause missed transfers? |
| Lane graph in an HD map | Lane segments | "Can drive into", "can change lane to" | Which lane will this vehicle take? |
| Traffic scene at an intersection | Vehicles, pedestrians, cyclists | Pairs close enough to interact | Will the turning car and the pedestrian conflict? |
| Origin&ndash;destination demand | Zones | Trips between zones, weighted by volume | Which zone pairs will grow fastest? |
| Interdependent infrastructure | Substations, signals, pumps, road segments, shelters | "Powers", "drains", "controls", "connects" | If this substation fails, which signals go dark? |

### Real networks are irregular

Below are two real graphs. On the left is the street network around USF Tampa from the Road2Vec lab:
495 intersections and 717 road links from OpenStreetMap. It has 72 dead ends, 285 three-leg and 114
four-leg intersections, so 77 percent of intersections do not have four legs.

On the right is the METR-LA detector graph used in most traffic-forecasting papers. Nobody drew its
edges on a map. Its builders (the DCRNN paper) computed a weight from the road distance $d$ between every
pair of detectors, $\exp(-(d/\sigma)^2)$, and dropped the pairs with a weight below 0.1. That leaves
1,515 directed edges among 207 detectors. The threshold is a modeling choice, and it decides what the
model can see.

```{figure} ../_static/figures/GNN2_Real_Networks.png
:alt: Left, the street network around USF Tampa from OpenStreetMap, 495 intersections and 717 road links, each intersection colored by its number of legs, 72 with one leg, 23 with two, 285 with three, 114 with four and 1 with five, so 77 percent are not four-way. Right, the 207 METR-LA loop detectors in Los Angeles joined by 1,515 directed edges, an edge kept when the Gaussian weight of the road distance is at least 0.1.
:width: 100%

Left: the USF Tampa street network (OpenStreetMap), colored by number of legs. Right: the METR-LA detector graph rebuilt the DCRNN way from road distances. Neither has a fixed number of neighbors per node.
```

### A graph can change every tenth of a second

At an intersection, each road user is a node, and each pair close enough to interact is an edge. The
edge carries the pair's relative state: distance, closing speed, and a surrogate safety measure such as
post-encroachment time (PET). In the figure (positions and times are illustrative), the riskiest edge
joins a right-turning car and a pedestrian in the crosswalk. A cyclist beside the same car forms a
second, "right-hook" edge. The pedestrian waiting at the corner has no edge yet, because no vehicle path
comes near. A model can label each edge: will this pair conflict in the next few seconds?

```{figure} ../_static/figures/GNN2_Intersection_Interactions.png
:alt: Left, a plan view of an intersection, car V1 turning right across a crosswalk with pedestrian P1 in it, cyclist C riding on in the bike lane beside V1, a second car V2, a bus B and a waiting pedestrian P2. Right, the same moment as a graph, road users as nodes and interacting pairs as edges colored by post-encroachment time, V1 to P1 at 1.2 seconds in red, V1 to C at 2.0 seconds, two longer gaps of 4.1 and 3.5 seconds, and P2 with no edge yet.
:width: 100%

Each road user is a node and each interacting pair an edge, built fresh from trajectories at every frame. The edge color shows the pair's post-encroachment time (illustrative values).
```

To build this graph at a real intersection you need trajectories of every road user at a high frame
rate (a roadside camera or lidar with a tracker, or drone video), plus a rule for which pairs become
edges, such as a distance and closing-speed threshold.

### Infrastructure is a graph of graphs

Power, traffic signals, stormwater and roads are each a network. Dependency edges join them: a
substation powers signals and pumps, a pump drains road segments, a signal controls an intersection. A
hurricane hits several layers at once, and failures travel along the edges that join the layers.

```{figure} ../_static/figures/GNN2_Hurricane_Infrastructure.png
:alt: Four stacked network layers, a power grid with substations S1 and S2, traffic signals G1 to G4, stormwater pumps P1 and P2, and roads R1 to R6 with a shelter SH, joined by dependency edges labeled powers, controls and drains. Wind trips S1 and storm surge floods P1; signals G1 and G2 go dark, P1 stops, R3 floods, and the shelter keeps one route through R4 and R5.
:width: 100%

An illustrative coastal city. Wind trips substation S1 and surge floods pump P1; the effects travel down the dependency edges to two dark signals and a flooded road, while the shelter keeps one route. Nobody sees that cascade by looking at one layer.
```

## Graphs in agency practice: the data after a hurricane

After a hurricane, what an agency knows about one traffic signal is spread over a dozen places. The
records come in different formats and sit with different people. Together they form a graph, even
though nobody stores them as one.

```{figure} ../_static/figures/GNN2_Hurricane_Data_Graph.png
:alt: At the center, one signal after the storm, asking whether it is dark, damaged or on a generator. Around it, eleven data sources, each with its format and holder. The signal hurricane SOP and the generator deployment SOP, PDF documents from the FDOT district. eSTORM Lite damage records, app records with photos and GPS from FDOT field teams. A signal and damage tracking spreadsheet from district traffic operations. The signal asset inventory, an asset database held by the county or city. The dark-signal traffic control procedure of the sheriff or police. The electric utility's outage and restoration data. Contractors' generator and repair logs. Emergency work orders and DDIR forms for FDOT and FHWA. The traffic management center's live ATMS signal status. Law enforcement's 911 and CAD incident log. Solid lines join sources that share an ID such as a signal ID, a generator number, a work order number or an FPID; dashed lines join sources linked only by a place, a time or a sentence in a procedure.
:width: 100%

Each card is a data source, colored by who holds it. Solid lines share an ID; dashed lines connect only through a place, a time or a sentence in a procedure.
```

Three things to notice in the figure:

- **Different formats.** Procedures are PDF documents: the district's signal hurricane SOP, its generator
  deployment procedure, and law enforcement's own procedure for dark signals. Field damage reports are
  app records with photos and GPS (FDOT District 7 uses eSTORM Lite). Status lives in spreadsheets,
  asset databases, a live traffic management system, a utility's outage map, contractors' logs and
  reimbursement forms.
- **Different hands.** The district, the county or city that maintains the signal, the electric utility,
  contractors, law enforcement and the federal reimbursement process each hold a piece.
- **Different kinds of links.** Some records share an ID: a signal or controller ID, a generator tracking
  number, a work order number, a financial project ID (FPID). Many share only a place, a time, or a
  sentence in a procedure.

## Real graphs are often implicit

Nobody hands you the adjacency matrix. In real infrastructure and traffic systems, the graph is usually
**implicit**: the dependencies are not written down as a table of node pairs. They are scattered across
records kept in different formats, and many are described only in words (for example, a procedure saying
which signals get generators first) or known only to the people who run the system. Sarasota County's
after-action report on the 2024 hurricanes is a good example: it asks for a pre-season inventory of
which utility meter feeds which critical facility, because that list of edges was missing when it was
needed.

So building the graph is often the hard part of the project, before any neural network is trained.
Three routes you will meet:

1. **Match records** that describe the same thing by location, time and name (entity resolution). For
   example, link a 911 incident to a dark-signal report when they fall within 50 m and an hour of each
   other, then check a random sample by hand.
2. **Read links out of text**, for example by having a language model extract "who does what to which
   asset" from SOPs and work orders.
3. **Predict missing edges** from the ones you know (link prediction, sections
   {doc}`3.4 <notes4-questions>` and {doc}`3.9 <notes9-classification>`), and estimate how strong each
   dependency is.

{doc}`Lab 8 <lab8_agency_graph>` runs routes 1 and 2 on two real documents: FDOT District 7's traffic-signal
SOP (one of the sources in the figure above) and the Sarasota County after-action report named in this
section. It scores the resulting graph against a labeled sample.

:::{admonition} The point
:class: tip
In every example, the state of one node depends on its neighbors. A congested intersection matters
because of where its queue spills. A dark signal matters because of the feeder it hangs on and the
corridor it controls. A model for this data must read the connections, and in practice someone must
first find them.
:::

---

Next: {doc}`notes2-graph-basics` &mdash; nodes, edges, and how a computer stores a graph.
