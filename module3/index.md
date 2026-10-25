# Module 3 — A Unified View: Graph Neural Networks

*Part I, AI Foundations Through a Transportation Lens. The class schedule is on the {doc}`../syllabus` page.*

## Session topics

- **Graph neural networks:** every network so far as one update on a graph; nodes and edges on a road network;
  the cell transmission model as message passing; aggregators and depth; graph attention

## Overview

Modules 1 and 2 introduced one architecture after another: the dense layer, the convolution, the recurrent
network, self-attention, Swin's windows, and cross-attention. This module puts all of them in one picture.
Each one lets a token mix in what some other tokens carry; only *who may be read* and *how much each counts*
differ. Draw "may read" as lines, and every one of those networks is a graph. A **graph neural network** is
the version where the graph comes from the problem itself.

In transportation that problem is often the road network. Detectors, road segments or intersections become
the nodes, and the roads and turning movements that join them become the edges. The cell transmission model
already works this way: each cell is updated from what its neighbours send, by one rule shared everywhere. A
graph network learns that kind of rule from data. Because the rule is shared, a model whose parameter count
does not depend on the number of nodes can be moved to another city. **Graph attention** is the attention of
BERT and ViT, with the road network deciding who may read whom.

## The module, page by page

:::{admonition} How to read this module
:class: tip
The module is one section page, the interactive companion embedded in it, and one lab. Skim
{doc}`3.1 <notes1-gnn>` before class and read it properly after, then run Lab 5. The section leans on
everything before it, so keep {doc}`1.3 <../module1/notes3-cnn>` (convolution) and the attention sections of
{doc}`Module 2 <../module2/index>` at hand.
:::

<div class="practice-table-wrap">
<table class="practice-table notes-map">
<thead>
<tr><th style="width:26%">Page</th><th style="width:44%">What it covers</th><th style="width:30%">Companions &amp; notebooks</th></tr>
</thead>
<tbody>
<tr>
  <td><a href="notes1-gnn.html"><strong>3.1 One view of every network: graph neural networks</strong></a><br><em>Graph neural networks</em></td>
  <td>Every network so far as one update with two choices: who may be read, and how much each counts. Who-reads-whom as a graph; what a node is on a road network; the cell transmission model as message passing; depth and aggregators; graph attention; the parameter-count test for moving a model to another city.</td>
  <td><a href="../_static/companions/GNN_On_A_Road_Network_Companion.html" target="_blank" rel="noopener">A GNN on a road network &#8599;</a><br><a href="lab5_graph_attention.html">Lab 5</a></td>
</tr>
</tbody>
</table>
</div>

Start with {doc}`3.1 One view of every network <notes1-gnn>`.

## Learning objectives

By the end of this module you will be able to:

- Describe every architecture in Modules 1 and 2 as one update with two choices &mdash; who may be
  read, and how the weights are set &mdash; and say what a node and an edge should be when the system
  is a road network.
- Explain message passing as one shared rule applied per connection, choose a graph network's
  depth and aggregator from the traffic problem, and tell whether a network model can move to
  another city from its parameter count.
- Explain graph attention as transformer attention restricted to the road's connections, and say when it
  earns its extra parameters over a fixed aggregator that carries what you already know about traffic.

## Topics

- One view of every network: who may be read, and how much each counts; graph convolution and graph attention on that map
- Nodes as tokens on a road network: detectors, directed road segments, intersections; the line graph
- The cell transmission model as message passing; aggregators (sum, mean, max, attention) as modelling choices, and depth as reach
- Transferability: does the number of nodes appear in the parameter count?
- Graph attention: BERT's attention with the road network as the mask; static (GAT) versus dynamic (GATv2)
  attention

## Video lectures

*To be populated.* See the course [YouTube channel](https://www.youtube.com/@hao6247).

## Recommended readings

- Bishop, C. M., & Bishop, H. (2024). *Deep Learning: Foundations and Concepts*. Springer. Chapter 13 (graph neural networks).
- Veličković, P., Cucurull, G., Casanova, A., Romero, A., Liò, P., & Bengio, Y. (2018). Graph attention networks. *ICLR*.
- Xu, K., Hu, W., Leskovec, J., & Jegelka, S. (2019). How powerful are graph neural networks? *ICLR*.
- Brody, S., Alon, U., & Yahav, E. (2022). How attentive are graph attention networks? *ICLR*. *(GATv2.)*

## Labs

Full descriptions, setup notes, and every lab in the course are on the {doc}`All Labs <../labs>` page.

| Notebook | What you build | Read alongside |
| --- | --- | --- |
| {doc}`Lab 5 — Attention on a Road Network <lab5_graph_attention>` | One message-passing layer with six aggregators on two traffic rules: where a learned weighting beats a fixed one, and where the right set of neighbours beats both | 3.1 |

**Inside Lab 5:** one
message-passing layer, six ways to combine what the neighbours send: mean, sum, max, attention, and two
that encode what you know at no cost in parameters &mdash; the worst downstream neighbour (queues back
up) and the average upstream one (flow arrives from upstream). *Proves:* the right set of neighbours
matters more than learning the weights. On the merge rule, reading only upstream links takes the error
from 0.0214 to 0.0122 for free; attention gets to 0.0110 with twice the parameters. On the spillback rule,
attention only ties the worst-downstream rule (0.0080 against 0.0081). Runs in about three minutes with
nothing to install.

## Interactive companion

- <a href="../_static/companions/GNN_On_A_Road_Network_Companion.html" target="_blank" rel="noopener">A GNN on a road network: one shared rule, any number of intersections</a> &mdash; embedded in <a href="notes1-gnn.html">3.1 One view of every network</a>
