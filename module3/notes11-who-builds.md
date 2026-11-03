(who-builds-the-graph)=
# 3.10 Who builds the transportation graph?

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 3 &middot; Section 3.10</span>
    <span class="notes-card-session">Session: Graph neural networks</span>
  </div>
  <p class="notes-card-lede">On a road network the map gives you the graph. After a hurricane, nobody gives you one, and building it is often the hardest part of the project. This page asks whether a model can learn the graph by itself, the way a transformer learns who attends to whom; why that is harder for a transportation system than for a sentence; and what to do when the graph is the hard part. It closes with a real test: a transformer asked to discover perimeter control, which did not.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Read it before</h4>
      <ul>
      <li><a href="notes1-graph-data.html">3.1 Graphs everywhere in transportation</a>, for the post-storm signal and the illustrative coastal city</li>
      <li><a href="notes3-one-view.html">3.3 One view of every network</a>, for masks as "who may read whom"</li>
      <li><a href="notes7-graph-attention.html">3.7 Graph attention</a>, for the road as the attention mask</li>
      </ul>
    </div>
    <div>
      <h4>Companion and notebook</h4>
      <ul>
      <li><a href="../_static/companions/Who_Builds_The_Graph_Companion.html" target="_blank" rel="noopener">Who builds the transportation graph? &#8599;</a>, on this page</li>
      <li><a href="lab8_agency_graph.html">Lab 8 &mdash; Building a graph from agency documents</a></li>
      </ul>
    </div>
  </div>
</div>

## What this section covers

- Attention as a learned graph, and a mask as the edges you hand it; a new graph for each input against one graph for
  the whole dataset
- Why a post-storm graph is harder to learn than a sentence: few events, links that hide until something fails,
  things that fail together, and nodes of many kinds
- Two graphs: the dependency facts you should write down, and the task relevance a model can learn
- A ladder of four rungs, from a given graph to a learned one, and what Module 3's experiments say about it
- A recipe for the post-storm graph, with Lab 8's numbers for its first steps
- A case study: why a transformer that could hold a perimeter did not discover one, and three levers for links that
  are hard to learn

Section {doc}`3.1 <notes1-graph-data>` said that real transportation graphs are implicit and that building them is
often the hard part. Sections {doc}`3.6 <notes6-message-passing>` and {doc}`3.7 <notes7-graph-attention>` then took
the graph as given: the road network is the mask, and the model learns only how much each neighbor counts. This page
goes back to the hard part. It asks when a model can learn the edges as well, and what to do when it cannot.

**After this page you should be able to:**

1. Say what a mask hands an attention model, and what the model must learn when the mask is taken away.
2. Explain why links in a post-storm system rarely show in the data, and why things that fail together are not
   necessarily linked.
3. Choose how much of the graph to give a model for a given task and data set, and name the checks a learned edge
   must pass before anyone acts on it.
4. Explain why a link that matters only after a joint action, such as holding traffic at a perimeter, is very hard
   for reinforcement learning to discover, and which lever changes which research question.

(who-builds-the-graph-companion)=
## The interactive companion

Work through the eight tabs in order. Tab 1 puts the three rules of section 3.7 side by side on cell 5 and lets you
turn the vectors of a small learned adjacency. Tab 2 shows which edges of the coastal city the data can see on a
normal day, when a substation trips, and when surge floods a pump. Tab 3 keeps the same nodes and changes the task.
Tab 4 is the ladder, with the measurements from the GNN companion and Lab 5. Tab 5 is the recipe, with Lab 8's
results. Tabs 6 and 7 are the perimeter-control case and why its link is so hard to learn. Tab 8 holds the fit card
and the questions.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion &mdash; Who builds the transportation graph?</span>
    <a href="../_static/companions/Who_Builds_The_Graph_Companion.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/Who_Builds_The_Graph_Companion.html"
          title="Who builds the transportation graph: learned graphs, post-storm interdependencies and a perimeter-control case study" loading="lazy"></iframe>
</div>

(who-builds-the-graph-findings)=
## What the measurements say

| Where | What was handed to the model | Result |
| --- | --- | --- |
| GNN companion, tab 5 (spillback rule, 6 seeds) | The same 10-weight attention layer with no mask, the road as mask, the road with direction | Test error 0.0839, 0.0556, 0.0286; predicting no change scores 0.0870 |
| Lab 5, merge rule (6 seeds) | All neighbors (mean), upstream neighbors only, learned attention | 0.0214, 0.0122 (same 2,193 parameters), 0.0110 (4,401 parameters) |
| Lab 8, two agency documents | A 12-relation schema and an entity table; the language model reads the edges | Typed precision 0.79, recall 0.84 on a 67-edge gold set; a co-occurrence baseline has precision 0.45 |
| Torus, 12 &times; 12 signals | Every signal can attend to every other; trained from a copy of max-pressure | 5.42 trips per step against max-pressure's 5.31 and the hand-built gate's 5.90 (load 0.45); no gating |

- **Knowing who the neighbors are was worth more than learning how much they count.** On roads and in Lab 5, the
  mask did most of the work, and attention added a little on top.
- **A link shows in the data only when it changes the outcome.** A feeder's link to its signals shows only when the
  feeder fails. The boundary signals' link to downtown showed only when someone held traffic, and under max-pressure
  nobody ever did.
- **The transformer could represent the perimeter, and keep it, but not find it.** Trained to copy the gate, its
  boundary signals put 0.49&ndash;0.59 of their attention on the 36 downtown tokens, where an even spread gives 0.25.
  Trained from max-pressure, they stayed at 0.25. Its critic still learned that a full downtown means fewer trips
  ahead (correlation &minus;0.76): knowing is not acting.

:::{admonition} Before you trust these results
:class: warning

- *Baseline:* predicting no change in the companion and Lab 5, a fixed upstream aggregator in Lab 5, a co-occurrence
  baseline in Lab 8, and two-phase max-pressure and the hand-built gate on the torus.
- *Honest split:* the companion and Lab 5 test on street networks never seen in training, Lab 5 at an unseen size; Lab
  8's gold set was frozen before either model run and labeled by one annotator; every torus number is 32 test runs on
  seeds not used in training.
- *Ugly cases:* the companion and Lab 5 learn rules written in code, so trust the order of the results, not their
  size. Each torus training run used one seed, and gaps of 1&ndash;2% between trained policies are about the size of
  seed-to-seed noise; the budget was 31 rounds, 83 minutes on two CPU cores.
:::

## Where to go next

- {doc}`Lab 8 — Building a Graph from Agency Documents <lab8_agency_graph>`: the first steps of the recipe on FDOT
  District 7's signal SOP and Sarasota County's 2024 after-action report.
- {doc}`Practice, exercises, and further reading <notes10-labs>`: what the labs and companions prove, and the
  questions this module arms you with.

---

Next: {doc}`Practice, exercises, and further reading <notes10-labs>`. Back to the {doc}`Module 3 map <index>`.
