# Module 3 — A Unified View: Graph Neural Networks

*Part I, AI Foundations Through a Transportation Lens. The class schedule is on the {doc}`../syllabus` page.*

## Session topics

- **Graph neural networks:** graph-structured data in transportation research and agency practice; nodes,
  edges and the adjacency matrix; every network so far as a graph model; node, edge and graph questions;
  node embeddings; message passing with convolution and attention; the cell transmission model as message
  passing; node, edge and graph classification

## Overview

Much transportation data is neither a sequence nor an image. A street network, a set of freeway detectors,
the road users at an intersection, the power feeds behind the traffic signals, the records an agency keeps
after a hurricane: each is a set of things plus the connections between them. That shape is a **graph**,
and in real systems the graph is often implicit until someone builds it.

Modules 1 and 2 already used graphs without saying so. An RNN reads a chain, a CNN reads a grid, and
self-attention reads a complete graph in which every token sees every other one. A **graph neural network**
is the general case: you hand it the graph from the problem. It turns each node into a vector, the way BERT
turns each word into one, and then lets each node read its neighbors through **message passing**: collect a
message from every neighbor, aggregate them, update. In a **graph convolution** the structure sets how much
each neighbor counts, as max-pressure signal control does; in **graph attention** the traffic states set
it, with the road as the attention mask. The cell transmission model fills the same three slots with rules
derived from the fundamental diagram, which is the clearest way to see what a GNN learns and where it can
be trusted. A small head on top answers the question per node, per pair of nodes, or for the whole network.

## The module, page by page

:::{admonition} How to read this module
:class: tip
Nine section pages, one interactive companion (embedded in 3.6) and one lab. Sections 3.1&ndash;3.4 need
no learning at all: they are about data, vocabulary and questions. Sections 3.5&ndash;3.9 build the model.
Skim the module before class and read it properly after, then run the companion and Lab 5. Keep
{doc}`1.3 <../module1/notes3-cnn>` (convolution) and the attention sections of
{doc}`Module 2 <../module2/index>` at hand.
:::

<div class="practice-table-wrap">
<table class="practice-table notes-map">
<thead>
<tr><th style="width:26%">Page</th><th style="width:44%">What it covers</th><th style="width:30%">Companions &amp; notebooks</th></tr>
</thead>
<tbody>
<tr>
  <td><a href="notes1-graph-data.html"><strong>3.1 Graphs everywhere in transportation</strong></a><br><em>Graph neural networks</em></td>
  <td>Road, detector, transit and lane graphs; an intersection scene as a graph; infrastructure as a graph of graphs in a hurricane; one signal's data after a storm; why real graphs are implicit and three ways to build them.</td>
  <td><a href="../module1/lab2_word_embeddings.html">Lab 2</a> (the USF network)</td>
</tr>
<tr>
  <td><a href="notes2-graph-basics.html"><strong>3.2 Graph basics</strong></a><br><em>Graph neural networks</em></td>
  <td>Nodes, edges, degree and features on a 3 &times; 3 grid of road cells; the node table, adjacency matrix and edge list; a road as a node or an edge (the line graph); heterogeneous graphs.</td>
  <td>&mdash;</td>
</tr>
<tr>
  <td><a href="notes3-one-view.html"><strong>3.3 One view of every network</strong></a><br><em>Graph neural networks</em></td>
  <td>Every network so far as one update with two choices; RNN, CNN and transformer as graph models; masks, cross-attention and DETR as graphs; why a more general model is needed.</td>
  <td>&mdash;</td>
</tr>
<tr>
  <td><a href="notes4-questions.html"><strong>3.4 Three kinds of questions</strong></a><br><em>Graph neural networks</em></td>
  <td>Node, edge and graph questions: dark signals, feeder links, conflicts, gridlock, percolation, incident clearance, disaster cascades; what one sample is at each level.</td>
  <td>&mdash;</td>
</tr>
<tr>
  <td><a href="notes5-node-embeddings.html"><strong>3.5 From tokens to node embeddings</strong></a><br><em>Graph neural networks</em></td>
  <td>The language recipe applied to a graph; input embeddings from raw features; one encoder per modality; Road2Vec's lookup table against a computed embedding; contextual embeddings.</td>
  <td><a href="../module1/lab2_word_embeddings.html">Lab 2</a></td>
</tr>
<tr>
  <td><a href="notes6-message-passing.html"><strong>3.6 Message passing and graph convolution</strong></a><br><em>Graph neural networks</em></td>
  <td>Message, aggregate, update; the parameter-count test for moving a model to another city; the GCN at cell 5; max pressure as a graph convolution; aggregators, depth and oversmoothing.</td>
  <td><a href="../_static/companions/GNN_On_A_Road_Network_Companion.html" target="_blank" rel="noopener">A GNN on a road network &#8599;</a><br><a href="lab5_graph_attention.html">Lab 5</a></td>
</tr>
<tr>
  <td><a href="notes7-graph-attention.html"><strong>3.7 Graph attention</strong></a><br><em>Graph neural networks</em></td>
  <td>Attention with the road as the mask; weights that flip from upstream to downstream as a cell fills; GAT versus GATv2; masked attention, graph transformers and hybrids; what the mask is worth.</td>
  <td>Companion tab 5<br><a href="lab5_graph_attention.html">Lab 5</a></td>
</tr>
<tr>
  <td><a href="notes8-ctm.html"><strong>3.8 The CTM already passes messages</strong></a><br><em>Graph neural networks</em></td>
  <td>One CTM step at cell 5 as message, aggregate and update; the CTM and a GNN slot by slot; derived rules against fitted rules; shared supply at a merge.</td>
  <td>&mdash;</td>
</tr>
<tr>
  <td><a href="notes9-classification.html"><strong>3.9 Node, edge and graph classification</strong></a><br><em>Graph neural networks</em></td>
  <td>One backbone, three heads; link prediction; same 40 numbers, different network; where it breaks; the fit card.</td>
  <td>&mdash;</td>
</tr>
<tr>
  <td><a href="notes10-labs.html"><strong>Practice, exercises, and further reading</strong></a><br><em>All of Module 3</em></td>
  <td>What Lab 5 and the companion prove; the module in six lines; judgment questions; reading a model's parameter count; questions for a vendor; further reading.</td>
  <td><a href="lab5_graph_attention.html">Lab 5</a><br><a href="../labs.html">All labs</a></td>
</tr>
</tbody>
</table>
</div>

Start with {doc}`3.1 Graphs everywhere in transportation <notes1-graph-data>`.

## Learning objectives

By the end of this module you will be able to:

- Recognize graph-structured data in transportation research and agency practice, say what the nodes and
  edges should be for a given question, and explain why the graph often has to be built from scattered
  records before any model can use it.
- Describe every architecture in Modules 1 and 2 as a graph model &mdash; one update with two choices, who
  may be read and how the weights are set &mdash; and say what a graph neural network adds.
- Frame a problem at the node, edge or graph level, and name the sample, the labels and the baseline that
  level requires.
- Explain message passing as one shared rule applied per connection, read a graph convolution and graph
  attention as two ways of setting the weights, and choose the aggregator and depth from the traffic
  problem.
- Map the cell transmission model onto message passing, and use that map to say where a learned graph
  model can be trusted and where the classical model should be kept.
- Tell from a model's parameter count whether it can move to another city.

## Topics

- Graph-structured data: road and detector networks, intersection scenes, interdependent infrastructure,
  agency records after a hurricane; implicit graphs and how to build them
- Graph basics: nodes, edges, degree, features, the adjacency matrix and the edge list; the line graph;
  heterogeneous graphs
- One view of every network: RNN, CNN and transformer as graph models; masks, cross-attention and DETR as
  graphs
- Node, edge and graph tasks
- Node embeddings: input embeddings, one encoder per modality, lookup versus computed embeddings
- Message passing: message, aggregate, update; graph convolution (GCN) and max pressure; aggregators, depth
  and oversmoothing
- Graph attention: the road as the attention mask; static (GAT) versus dynamic (GATv2) attention; graph
  transformers
- The cell transmission model as message passing: derived versus fitted rules
- Node, edge and graph classification; link prediction; transferability

## Video lectures

*To be populated.* See the course [YouTube channel](https://www.youtube.com/@hao6247).

## Recommended readings

- Bishop, C. M., & Bishop, H. (2024). *Deep Learning: Foundations and Concepts*. Springer. Chapter 13 (graph neural networks).
- Gilmer, J., Schoenholz, S. S., Riley, P. F., Vinyals, O., & Dahl, G. E. (2017). Neural message passing for quantum chemistry. *ICML*.
- Kipf, T. N., & Welling, M. (2017). Semi-supervised classification with graph convolutional networks. *ICLR*.
- Veličković, P., Cucurull, G., Casanova, A., Romero, A., Liò, P., & Bengio, Y. (2018). Graph attention networks. *ICLR*.
- Xu, K., Hu, W., Leskovec, J., & Jegelka, S. (2019). How powerful are graph neural networks? *ICLR*.
- Brody, S., Alon, U., & Yahav, E. (2022). How attentive are graph attention networks? *ICLR*. *(GATv2.)*
- Varaiya, P. (2013). Max pressure control of a network of signalized intersections. *Transportation Research Part C: Emerging Technologies*.
- Li, D., Fu, B., Wang, Y., Lu, G., Berezin, Y., Stanley, H. E., & Havlin, S. (2015). Percolation transition in dynamical traffic network with evolving critical bottlenecks. *PNAS*, 112(3), 669&ndash;672.

More, with a note on what to look for in each, is on the {doc}`practice page <notes10-labs>`.

## Labs

Full descriptions, setup notes, and every lab in the course are on the {doc}`All Labs <../labs>` page.

| Notebook | What you build | Read alongside |
| --- | --- | --- |
| {doc}`Lab 5 — Attention on a Road Network <lab5_graph_attention>` | One message-passing layer with six aggregators on two traffic rules: where a learned weighting beats a fixed one, and where the right set of neighbors beats both | 3.6, 3.7 |

**Inside Lab 5:** one
message-passing layer, six ways to combine what the neighbors send: mean, sum, max, attention, and two
that encode what you know at no cost in parameters &mdash; the worst downstream neighbor (queues back
up) and the average upstream one (flow arrives from upstream). *Proves:* the right set of neighbors
matters more than learning the weights. On the merge rule, reading only upstream links takes the error
from 0.0214 to 0.0122 for free; attention gets to 0.0110 with twice the parameters. On the spillback rule,
attention only ties the worst-downstream rule (0.0080 against 0.0081). Runs in a few minutes with
nothing to install.

## Interactive companion

- <a href="../_static/companions/GNN_On_A_Road_Network_Companion.html" target="_blank" rel="noopener">A GNN on a road network: one shared rule, any number of intersections</a> &mdash; embedded in <a href="notes6-message-passing.html">3.6 Message passing and graph convolution</a>; tab 5 goes with <a href="notes7-graph-attention.html">3.7 Graph attention</a>
