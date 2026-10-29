# Practice, exercises, and further reading

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 3 &middot; Practice</span>
    <span class="notes-card-session">Sessions: all of Module 3</span>
  </div>
  <p class="notes-card-lede">What the labs and the companion that go with this module <em>prove</em>, the module in six lines, the questions it arms you with, and where to read further. Everything on this page is practice &mdash; the explanations live in sections 3.1&ndash;3.9.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Notebooks that go with it</h4>
      <ul>
      <li><a href="lab5_graph_attention.html">Lab 5 &mdash; Attention on a road network</a></li>
      <li><a href="lab8_agency_graph.html">Lab 8 &mdash; Building a graph from agency documents</a></li>
      <li><a href="../module1/lab2_word_embeddings.html">Lab 2 &mdash; From Word2Vec to Road2Vec</a> (the bridge from Module 1)</li>
      </ul>
    </div>
    <div>
      <h4>Every lab in the course</h4>
      <ul>
      <li><a href="../labs.html">All Labs &mdash; the full directory &#8599;</a></li>
      </ul>
    </div>
  </div>
</div>

## What the labs and the companion prove

**{doc}`Lab 5 — Attention on a Road Network <lab5_graph_attention>`** reads with
{doc}`3.6 <notes6-message-passing>` and {doc}`3.7 <notes7-graph-attention>`. One message-passing layer, six
ways to combine what the neighbors send: mean, sum, max, attention, and two that encode what you know at no
cost in parameters &mdash; the worst downstream neighbor (queues back up) and the average upstream one (flow
arrives from upstream). They are compared on two traffic rules, with an optional third. *Proves:* the right
set of neighbors matters more than learning the weights. On the merge rule, reading only upstream links
takes the error from 0.0214 to 0.0122 for free; attention gets to 0.0110 with twice the parameters. On the
spillback rule, attention only ties the worst-downstream rule (0.0080 against 0.0081). The optional part
tests a rule where the neighbor that matters flips with the receiving link's own density, the case that
separates static GAT from GATv2. Runs in a few minutes with nothing to install.

**{doc}`Lab 8 — Building a Graph from Agency Documents <lab8_agency_graph>`** reads with
{doc}`3.1 <notes1-graph-data>`. It builds the implicit graph that 3.1 describes from two real documents:
FDOT District 7's traffic-signal SOP (the plan) and Sarasota County's 2024 after-action report (what
happened). A table is already an edge list: the AAR's responsibility matrix gives 167 edges once you split
"N/A" and "Parks, Recreation, and Natural Resources" correctly and merge the several names of one
organization. Prose needs a model: Claude, given a 12-relation schema and an entity table, reads each page
into typed edges with exact quotes. *Proves:* the model finds 84% of a 67-edge gold set at 79% precision,
against a co-occurrence baseline that is wrong more than half the time; two independent runs share 138 of
their 175 distinct edges; and the automatic checks remove no wrong edge on the gold pages, because a wrong
reading with a real quote passes them all. Only a labeled sample tells you the reading is right. Runs in
under a minute with no API key; the SOP PDF is not posted, only the text of the ten pages the lab reads.

**The companion, {doc}`embedded in 3.6 <notes6-message-passing>`.** Tab 2 gives every intersection the same
input and lets you switch the aggregate between sum, mean and max: only the sum tells the intersections
apart. Tab 3 animates queue spillback against what an L-layer model can see. Tab 4 trains a GNN in PyTorch
on a spillback rule and tests it on networks it never saw, at sizes it never saw: depth and aggregator
choice. Tab 5 is the 10-weight attention layer of {doc}`3.7 <notes7-graph-attention>`, with and without the
road mask.

**{doc}`Lab 2 — From Word2Vec to Road2Vec <../module1/lab2_word_embeddings>`** lives in Module 1 and is the
bridge into this module: it builds the USF street network of {doc}`3.1 <notes1-graph-data>` and the
lookup-table node embedding that {doc}`3.5 <notes5-node-embeddings>` compares a GNN against.

## The module in six lines

1. Much transportation data is a graph: things (nodes) plus connections (edges). Roads, detectors, road
   users at an intersection, power feeds and agency records all fit, and in practice the graph is often
   implicit until someone builds it.
2. A graph is stored as a node table X (N &times; d), an adjacency matrix A (N &times; N) or an edge list,
   plus optional edge and graph features. Put the node where the state you care about lives; a road block
   can be a node, and then intersections become edges.
3. RNNs, CNNs and transformers are graph models on a chain, a grid and a complete graph; masks and
   cross-attention change that graph. A GNN takes the graph from the problem.
4. Questions come at three levels: node, edge, graph. The level decides the sample and the labels.
5. The recipe is the one from language: give every node an input embedding (one encoder per modality if
   needed), then let the vectors mix through message passing (message, aggregate, update). Convolution fixes
   the mixing weights by structure or physics, as max pressure does; attention computes them from the
   states, usually inside the graph's mask.
6. The CTM already does message passing with derived rules. A GNN keeps the steps and fits the rules, so it
   earns its place where nobody can write the rule down.

## Check yourself

1. A county wants to know, two hours after landfall, which of its 600 signals are dark. Crews have checked
   80. Which level of task is this? What are your nodes and edges, which edge type matters most, and who
   holds the data for it?
2. A crash blocks two of four lanes on I-275. You want to predict how many minutes until speeds on all lanes
   return to normal. What is one training sample, where do the labels come from, and what simple baseline
   must the model beat?
3. Max pressure serves the phase with the largest pressure. Which part of it is the message, which the
   aggregate, which the readout? What would a learned version change, and what data would it need?
4. You want to warn, 30 minutes ahead, that a city's network is about to percolate. What can you compute
   today with no learning, and what exactly would the GNN predict?
5. After a storm, damage reports, contractor logs and work orders describe the same signals but share no
   common ID. Which of the three routes in {doc}`3.1 <notes1-graph-data>` would you try first to build the
   graph, and how would you check the links it finds?
6. For predicting travel time on each direction of every arterial segment downtown, what are the nodes, and
   what are the edges? There is more than one defensible answer; defend yours with the state you want to
   predict.

## Exercise &mdash; read a model's parameter count

Take any network-scale traffic forecasting paper or product sheet. Find the parameter count, or reconstruct
it from the architecture description. Does the number of sensors appear in it? Then answer three questions
in writing: could this be run on your network without retraining; what is the baseline the paper compares
against; and was the reported split across time or across networks. Most published results answer the
third question in a way that makes the first one moot.

## On the job

When a vendor offers a network-wide prediction, ask what a node is in their model, and what happens when you
add a detector. The answers tell you whether you are buying a model of traffic or a model of their training
city. Then ask for the persistence baseline on your own data &mdash; if they have not computed it, neither
has anyone else, and the improvement they are quoting has no denominator.

When the job is after a storm, ask first where the edges will come from. A model that predicts dark signals
from their feeders needs the feeder-to-signal table, and that table usually sits with the utility, not the
agency.

## Further reading

- Gilmer et al., "Neural message passing for quantum chemistry," ICML 2017 (arXiv 1704.01212). The general
  message-passing form of {doc}`3.6 <notes6-message-passing>`.
- Kipf and Welling, "Semi-supervised classification with graph convolutional networks," ICLR 2017 (arXiv
  1609.02907). The GCN.
- Veličković et al., "Graph attention networks," ICLR 2018 (arXiv 1710.10903); Brody, Alon and Yahav, "How
  attentive are graph attention networks?" ICLR 2022 (arXiv 2105.14491). GAT and GATv2: check which one a
  paper means.
- Xu, Hu, Leskovec and Jegelka, "How powerful are graph neural networks?" ICLR 2019 (arXiv 1810.00826). Why
  sum can tell apart what mean and max cannot.
- Ying et al., "Do transformers really perform badly for graph representation?" NeurIPS 2021 (Graphormer);
  Rampášek et al., "Recipe for a general, powerful, scalable graph transformer," NeurIPS 2022 (GraphGPS).
  Graph transformers.
- Carion et al., "End-to-end object detection with transformers," ECCV 2020. DETR's object queries and
  cross-attention, read as graphs in {doc}`3.3 <notes3-one-view>`.
- Li, Yu, Shahabi and Liu, "Diffusion convolutional recurrent neural network," ICLR 2018 (arXiv 1707.01926).
  DCRNN and the METR-LA graph. Ask how the graph was built and how the data were split.
- Guo et al., "Attention based spatial-temporal graph convolutional networks for traffic flow forecasting,"
  AAAI 2019 (ASTGCN); Zheng et al., "GMAN: A graph multi-attention network for traffic prediction," AAAI
  2020. Two ways to use attention on a road graph.
- Varaiya, "Max pressure control of a network of signalized intersections," Transportation Research Part C,
  2013; Wei et al., PressLight (KDD 2019) and CoLight (CIKM 2019).
- Daganzo, "The cell transmission model," Transportation Research Part B, 1994; Jin and Zhang, merge model,
  Transportation Research Part B, 2003.
- Li et al., "Percolation transition in dynamical traffic network with evolving critical bottlenecks," PNAS,
  2015.
- Mazloumian, Geroliminis and Helbing, "The spatial variability of vehicle densities as determinant of urban
  network capacity," Phil. Trans. R. Soc. A, 2010. Why the same average density can mean different networks.
- Bishop and Bishop, *Deep Learning: Foundations and Concepts* (Springer, 2024), chapter 13. The textbook
  treatment of graph neural networks.

*Numbers on these pages come from the course's GNN companion, Lab 5, the Road2Vec lab and the GNN figure
reproducers. The grid snapshot, the intersection scene, the queues in the max-pressure example, the
hurricane system and the 5 &times; 5 grid snapshots are synthetic or illustrative; the USF and METR-LA
networks are real.*

## Where this goes next

{doc}`Module 4 <../module4/index>` turns from predicting to producing: models that generate traffic states,
trajectories and images. Graphs come back in Part II. One of the three routes for building an implicit
graph is reading links out of text, and {doc}`Module 5 <../module5/index>` puts a language model in a loop
with tools, which is how that reading gets done at agency scale.

---

Next: {doc}`Module 4 — Deep Generative Models <../module4/index>`.
