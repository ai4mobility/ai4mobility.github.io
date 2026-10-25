# 3.5 From tokens to node embeddings

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 3 &middot; Section 3.5</span>
    <span class="notes-card-session">Session: Graph neural networks</span>
  </div>
  <p class="notes-card-lede">A word is not a number, so in Module 2 we built a recipe to turn words into vectors: tokenize, look up an input embedding, add context, predict. A graph uses the same recipe. This page builds a node's vector in two steps: its own raw features become an input embedding, and then reading its neighbors turns that into a contextual embedding.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Interactive companion for this module</h4>
      <ul>
      <li><a href="../_static/companions/GNN_On_A_Road_Network_Companion.html" target="_blank" rel="noopener">A GNN on a road network &#8599;</a> &mdash; embedded in <a href="notes6-message-passing.html">3.6</a></li>
      </ul>
    </div>
    <div>
      <h4>Notebooks that go with it</h4>
      <ul>
      <li><a href="../module1/lab2_word_embeddings.html">Lab 2 &mdash; From Word2Vec to Road2Vec</a>: the lookup-table node embedding compared below</li>
      <li><a href="lab5_graph_attention.html">Lab 5 &mdash; Attention on a road network</a></li>
      </ul>
    </div>
  </div>
</div>

:::{admonition} Pause and answer
:class: tip
When did we last feed a neural network something that is not a number? How did we handle it?
:::

The answer is language. A word is not a number, so we built a recipe to turn words into vectors. A graph
needs the same recipe.

## The recipe you already know

1. **Tokenize.** Cut the text into pieces. BERT cuts "The stalled bus blocked the curb lane" into 7 word
   tokens, plus [CLS] and [SEP]: 9 tokens.
2. **Build a vocabulary.** List every token the model can see and give each one an ID. BERT's vocabulary has
   30,522 entries.
3. **Look up the input embedding.** Each ID picks its own row in a table of 30,522 &times; 768 learned
   numbers. Now every token is a vector of 768 numbers, and the sentence is a 9 &times; 768 table. BERT's
   paper calls these token embeddings; position and segment embeddings are added to them.
4. **Add context.** Transformer layers let each token read the others. Their outputs, often called hidden
   states or **contextual embeddings**, differ by sentence: "shoulder" gets one vector in "stopped on the
   shoulder" and another in "a shoulder check before merging."
5. **Predict.** A head scores every entry in the vocabulary and picks the most likely one: the next word for
   GPT, the masked word for BERT.

ViT used the same recipe for images, with one change at step 2. A 16 &times; 16 color patch is already 768
numbers (16 &times; 16 pixels &times; 3 colors), so there is no vocabulary. A learned linear layer turns
each patch into its **patch embedding**, and a 224 &times; 224 FL511 frame becomes a 197 &times; 768 table
(196 patches plus [CLS]).

## The same recipe for a graph

```{figure} ../_static/figures/GNN2_Same_Recipe.png
:alt: A table of four steps, token, input embedding, contextual embedding and prediction, in three rows. Language, BERT and GPT, a word piece with an ID in a vocabulary, a token embedding looked up as a row of 768 numbers, transformer layers where every token reads all, and the next or masked word picked from the vocabulary. Images, ViT, a 16 by 16 patch of 768 pixel values, a patch embedding from a linear layer, transformer layers where every patch reads all, and an image label such as congested or not. Graphs, GNN, a node such as a detector, cell, asset or record, a node embedding h zero from a linear layer of d numbers, message passing where each node reads its neighbors only, and a node, edge or graph answer. Only the contextual step changes who reads whom.
:width: 100%

Read each row left to right. The graph row reuses every step; the only real change is who reads whom in step 3.
```

| Step | Language (BERT, GPT) | Images (ViT) | Graphs (GNN) |
| --- | --- | --- | --- |
| Token | a word piece | a 16 &times; 16 patch | a node: detector, road cell, intersection, asset, record |
| Raw input | a token ID from the vocabulary | 768 pixel values | node features: volume, lanes, length, density&hellip; |
| Input embedding | token embedding: look up a row, 768 numbers | patch embedding: linear projection to 768 numbers | node embedding $h^{(0)}$: linear projection to d numbers (a lookup only for categories such as asset type) |
| Who reads whom | every token (GPT: earlier tokens only) | every patch (Swin: its window) | the node's neighbors in A |
| Contextual embedding | transformer layers | transformer layers | message-passing layers |
| Output | next or masked word | image label | a node, edge or graph answer ({doc}`3.4 <notes4-questions>`) |

:::{admonition} A note on terms
:class: note
"Input embedding" is the standard name for the vector a token enters the network with; the transformer
paper uses it, and ViT calls it the patch embedding. GNN papers usually write it as $h^{(0)}$ and call it
the initial node representation, or the input features after an input projection. The vectors after the
message-passing layers are called node representations or node embeddings. These notes borrow BERT's word
"contextual" for them, because they play the same role.
:::

Two things carry over directly, and one changes.

- **Carries over: every token gets a vector, then the vectors mix.** That is the whole job of the network:
  build a representation of each node that knows about its surroundings, so that a small head can answer
  the question.
- **Carries over: prediction can still be "pick from a list."** Link prediction asks: which node does this
  node connect to? Score every candidate node and pick the most likely, just as GPT scores every word in its
  vocabulary. The set of nodes plays the role of the vocabulary. Word2vec's skip-gram scored a word and its
  context the same way.
- **Changes: who reads whom.** BERT and ViT let every token read every other token. A graph tells you who
  may read whom. This is the one piece of the recipe that the graph hands you for free.

## Step 1: from raw features to an input embedding

Each node arrives with a handful of measurements in mixed units.

- A **road cell**: length (mi), lanes, speed limit (mph), current density (veh/mi/ln).
- An **intersection**: entering volume (veh/h), approach lanes, cycle length (s), green share for the main
  street.
- A **detector**: the last hour of 5-minute speeds, plus time of day.

The input layer turns those few numbers into a vector of d numbers, with the same weights for every node:

$$
h_i^{(0)} = W_{\text{in}}\, x_i + b
$$

| Symbol | In words | Example |
| --- | --- | --- |
| $x_i$ | node i's raw features | cell 5: [0.1 mi, 1 lane, 65 mph, 30 veh/mi] |
| $W_{\text{in}}, b$ | a learned matrix and bias, shared by every node | d &times; 4 numbers, plus d |
| $h_i^{(0)}$ | node i's input embedding | d numbers: 768 in BERT and ViT; 16 in the course's road-network companion |

**In words:** every node passes its own measurements through the same small layer and comes out as a vector
of a fixed size. Two practical notes:

- **Scale the features first.** Volumes in thousands and lane counts of 1 to 4 should be standardized before
  they meet the same weights.
- **Categories use a lookup table.** Asset type (substation, signal, pump) or functional class has no numeric
  meaning, so each category gets its own learned row, exactly like a word in BERT's vocabulary. The row is
  added to, or joined with, the projected numbers.

## Nodes can come from different modalities

Nothing says every node must hold the same kind of data. Around one intersection, a graph can join a
traffic camera, a loop detector, the signal controller's event log, crash reports, a weather station and
the road segments themselves. Each kind of data gets **its own encoder** that ends in the same vector size
d: a ViT for camera frames, a 1-D CNN or GRU for a detector's speed series, a sequence encoder for
controller events, BERT for crash narratives, a small MLP for weather and road attributes. After that,
every node is just d numbers, and message passing mixes them along the edges.

```{figure} ../_static/figures/GNN2_Multimodal_Nodes.png
:alt: Left, six raw data types each with its own encoder ending in d numbers, an FL511 camera frame through a ViT, the last hour of detector speeds through a 1-D CNN or GRU, signal controller events through a sequence encoder, a crash report narrative through BERT, weather station readings through a small MLP, and road segment attributes through an MLP plus a lookup. Right, one graph around an intersection joining the controller, four approach segments, a camera, two detectors, a crash report and a weather node, with edges labeled controls, watches, sits on, happened on and affects.
:width: 100%

Each kind of data has its own encoder that ends in the same d numbers. In the graph, edges say which camera watches which segment, which detector sits on it, and where a crash happened.
```

This is the graph version of the multimodal fusion you saw with cross-attention in
{doc}`2.9 <../module2/notes9-cross-attention>`&ndash;{doc}`2.11 <../module2/notes11-streams>`. There,
tokens from different sources met in one attention layer. Here, the graph says which camera watches which
approach, which detector sits on which segment, and which crash report happened at which intersection, so
each node mixes only with the sources that are physically related to it. The hurricane data graph in
{doc}`3.1 <notes1-graph-data>` is the same idea at agency scale: SOP text, app photos and spreadsheet rows
each need their own encoder before they can sit in one graph.

## Look up a node, or compute it?

You have already built node embeddings once. In the Road2Vec lab, random walks on the USF network fed
word2vec, and every intersection got its own row in a table. That treats each intersection ID as a word in
a vocabulary. A GNN instead computes each vector from the node's features and its neighbors.

|  | Road2Vec (a lookup table) | GNN (computed) |
| --- | --- | --- |
| Size | 495 &times; 64 = 31,680 numbers | 736 numbers for a 2-layer network, 6 inputs, 16 wide |
| A new city | no rows for its intersections | runs as is |
| Rush hour vs 3 a.m. | the same vector | a new vector every 5 minutes |
| What it learned | mostly geography: functional-class purity 0.664, below plain latitude and longitude at 0.678 | whatever the training task needs |

This is the same step as word2vec to BERT ({doc}`2.2 <../module2/notes2-contextual>`). Word2vec gives
"shoulder" one vector for every sentence. BERT gives it a new vector in each sentence. A GNN gives an
intersection a new vector in each traffic snapshot.

## Step 2: from input embeddings to contextual embeddings

After step 1, a node knows only itself. Cell 5's vector says "30 veh/mi, one lane" and nothing about the
queue building in cell 6. Two cells with the same features get the same vector, even if one feeds a jam
and the other feeds an empty road.

Step 2 fixes this the way a transformer does: each node reads other nodes and mixes what it reads into its
own vector. On a graph, a node reads only its neighbors, and it repeats this once per layer. After one
layer, cell 5 knows about cells 2, 4, 6 and 8. After two layers, it knows about the corners too.

There are two ways to decide how much each neighbor counts, and they mirror the two families you already
know.

- **Convolution:** the weights are fixed by the graph's structure, such as how many links each node has, or
  by known physics. Like a CNN kernel, the weights do not look at the traffic.
  ({doc}`3.6 <notes6-message-passing>`)
- **Attention:** the weights are computed from the nodes' current vectors with queries and keys. Like BERT
  and ViT, a neighbor counts more when its state is relevant right now. ({doc}`3.7 <notes7-graph-attention>`)

---

Next: {doc}`notes6-message-passing` &mdash; the layer that does the mixing.
