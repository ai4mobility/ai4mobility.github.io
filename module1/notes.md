# Module 1 Notes — Foundations and Representation Learning

*Sessions: Aug 27, Sept 3, Sept 10, 2026. This chapter builds the three things
the rest of the course stands on: a way of describing where AI actually enters a
transportation task, a neural network built from a model you already use, and
the representation idea that unifies almost everything after it.*

:::{admonition} How to read this chapter
:class: tip
The chapter is split into seven pages. Use the map below, or the sidebar, to go
straight to the one you need — each page opens with a card telling you which
session it belongs to, which interactive companions are embedded in it, and
which notebooks go with it.

Read **{doc}`1.1 <notes1-workflow>` before the first meeting** — you will be
choosing a project on Aug 27 and this is the vocabulary that makes that choice
possible. Section 1.2 (four pages) and section 1.3 pair with the Sept 3 and
Sept 10 meetings; skim before, read properly after, run the labs in between.

The interactive companions embedded here are the same pages posted on Canvas.
They are not decoration: several of the results argued in this chapter are only
convincing if you move the sliders yourself.
:::

---

## The map

<div class="practice-table-wrap">
<table class="practice-table notes-map">
<thead>
<tr><th style="width:26%">Page</th><th style="width:44%">What it covers</th><th style="width:30%">Companions &amp; notebooks</th></tr>
</thead>
<tbody>
<tr>
  <td><a href="notes1-workflow.html"><strong>1.1 AI and the workflow</strong></a><br><em>Aug 27</em></td>
  <td>Five families of AI; workflow anatomy; the six leverage labels; the checkpoint rule; the Traffic Incident Management case; reading a capability claim.</td>
  <td><a href="../_static/companions/TIM_AI_Workflow_Case.html" target="_blank" rel="noopener">TIM as an AI workflow &#8599;</a><br><a href="../_static/companions/AI_Workflow_Companion.html" target="_blank" rel="noopener">Anatomy of an AI workflow &#8599;</a><br><a href="lab1.html">Lab 1</a></td>
</tr>
<tr>
  <td><a href="notes2-networks.html"><strong>1.2 From the logit to the network</strong></a><br><em>Sept 3</em></td>
  <td>The binary logit <em>is</em> a sigmoid; tanh; softmax <em>is</em> the MNL; IIA; saturation; the loss function; stacking layers; two results that argue against a network; what one costs.</td>
  <td><a href="../_static/companions/Sigmoid_Tanh_Companion.html" target="_blank" rel="noopener">Sigmoid, tanh, softmax &#8599;</a><br><a href="../_static/companions/Multilayer_Networks_Companion.html" target="_blank" rel="noopener">Multilayer networks &#8599;</a><br><a href="lab1.html">Lab 1</a></td>
</tr>
<tr>
  <td><a href="notes3-learning.html"><strong>1.2 How a network learns</strong></a><br><em>Sept 3</em></td>
  <td>Weights, biases and activations one at a time; when one boundary is not enough; backpropagation traced number by number; where training goes wrong, measured.</td>
  <td><a href="../_static/companions/Neural_Networks_and_Backprop_Companion.html" target="_blank" rel="noopener">Network basics and backprop &#8599;</a><br><a href="lab1.html">Lab 1</a></td>
</tr>
<tr>
  <td><a href="notes4-cnn.html"><strong>1.2 Convolution, and a network that sees</strong></a><br><em>Sept 3</em></td>
  <td>Convolution from a moving average; weight sharing; a worked case &mdash; a child on a scooter, seen by a stock detector.</td>
  <td><a href="../_static/companions/Convolution_Kernels_Companion.html" target="_blank" rel="noopener">Convolution kernels &#8599;</a><br><a href="../_static/companions/Scooter_Kid_CNN_Case.html" target="_blank" rel="noopener">The scooter-kid case &#8599;</a><br><a href="lab3_image_embeddings.html">Lab 3</a></td>
</tr>
<tr>
  <td><a href="notes5-cnn-in-practice.html"><strong>1.2 Choosing a network, and interrogating it</strong></a><br><em>Sept 3 &amp; 10</em></td>
  <td>Which architecture, and what it costs in parameters, latency and roadside power; saliency maps and the honest limits of what they prove.</td>
  <td><a href="../_static/companions/CNN_Architectures_Companion.html" target="_blank" rel="noopener">CNN architectures &#8599;</a><br><a href="../_static/companions/Saliency_Maps_Companion.html" target="_blank" rel="noopener">Saliency maps &#8599;</a><br><a href="lab3_image_embeddings.html">Lab 3</a></td>
</tr>
<tr>
  <td><a href="notes6-embeddings.html"><strong>1.3 Representation learning and embeddings</strong></a><br><em>Sept 10</em></td>
  <td>One-hot and its three failures; embeddings as geometry; Word2Vec &rarr; Road2Vec; transfer learning; contrastive learning; CLIP; how to check a representation.</td>
  <td><em>No companion &mdash; the work is in the notebooks</em><br><a href="lab2_word_embeddings.html">Lab 2</a>, <a href="lab3_image_embeddings.html">Lab 3</a>, <a href="lab4_clip_vs_traditional_cv.html">Lab 4</a></td>
</tr>
<tr>
  <td><a href="notes7-labs.html"><strong>Labs, practice, and further reading</strong></a><br><em>All three sessions</em></td>
  <td>What each notebook proves; using this on the job; the reading list; five exercises; where this goes next.</td>
  <td>All four notebooks</td>
</tr>
</tbody>
</table>
</div>

---

## 1.0 The problem this module solves

Transportation is being reshaped by AI on three fronts: how we **sense** the
system (cameras, lidar, radar, V2X, probe data), how we **operate** vehicles
(ADAS, lane keeping, driving automation), and how we **plan and manage**
networks (simulation, digital twins, signal control, demand prediction).

That is the optimistic framing, and it is broadly true. It is also exactly why a
critical engineering perspective matters. The AI-for-mobility literature
publishes impressive demonstrations alongside a large number of results that do
not replicate, do not deploy, or do not actually beat a well-tuned classical
baseline. A significant part of what you should get out of this course is the
ability to tell those apart — quickly, and in front of a vendor.

So this module has an unusual shape for an AI course. It starts not with a model
but with a *process*, because the first decision you will make in practice is
never "which architecture" — it is "which step of this workflow is safe to hand
over, and how would I prove the result was any good." Only then do we build a
neural network, and only then do we get to the representation idea.

---

Start here: {doc}`notes1-workflow`.
