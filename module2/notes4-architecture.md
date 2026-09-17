# 2.4 The transformer as a research architecture

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 2 &middot; Section 2.4</span>
    <span class="notes-card-session">Session: Sept 17</span>
  </div>
  <p class="notes-card-lede">The encoder stack does not know what a word is. Once you see that, the three decisions that matter become yours &mdash; what is one token, what may attend to what, and what "position" means in your problem. This section is the transformer pointed at detector series, trajectories and networks rather than at text, worked on 207 real loop detectors.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Interactive companions on this page</h4>
      <ul>
      <li><a href="../_static/companions/Transformer_As_Architecture_Companion.html" target="_blank" rel="noopener">Your own tokens: the transformer as a research architecture &#8599;</a></li>
      </ul>
    </div>
    <div>
      <h4>Read it after</h4>
      <ul>
      <li><a href="notes3-attention.html">2.3 Attention: the mechanism</a></li>
      </ul>
    </div>
  </div>
</div>

## What this section covers

- Encoder-only (BERT-style), decoder-only (GPT-style) and encoder&ndash;decoder designs
- Which mobility tasks each family suits
- Pretraining, scaling behaviour, and what &ldquo;emergent&rdquo; does and does not mean
- Designing your own tokens: what is one element of your sequence?
- Attention masks as a modelling choice &mdash; declared adjacency versus learned adjacency
- What &ldquo;position&rdquo; means when the axis is space, time, or neither
- Sizing the claim: the gap between no model and a model, against the gap between models

*The written section is posted after the Sept 17 meeting. Until then the companion
below is the material &mdash; it is the assigned preparation and it carries every number
this section will argue from.*

## Take the language out

The first two sections use a transformer the way it was built, on language. This one
takes the language out. The encoder stack does not know what a word is &mdash; it knows how to
let a set of vectors exchange information &mdash; so the three modelling decisions that matter
are yours: what is one token, what may attend to what, and what "position" means in your
problem. The companion works that through on three research problems at once: network-wide
traffic prediction, multimodal car-following, and infrastructure interdependency.

Everything measured on it runs on **METR-LA** &mdash; 207 real loop detectors on Los Angeles
freeways, five-minute speeds, March to June 2012. Tab 2 is the one to spend time in: pick
a detector and compare the neighbours you would *declare* from the road network against
the ones the data actually shows, separately in the morning peak, the evening peak, and
overnight. Across all 207 detectors those two sets agree only 44% of the time, and the
measured set is only 48% stable between the two peaks &mdash; which is the argument for letting
a model compute the adjacency rather than fixing it. Then read tab 5 before you propose a
transformer for your project: the naive baselines there were computed from scratch, and the
gap between *no model* and *a model* turns out to be four times the gap between the 2018
graph model and the 2023 state of the art.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion &mdash; Your own tokens: the transformer as a research architecture</span>
    <a href="../_static/companions/Transformer_As_Architecture_Companion.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/Transformer_As_Architecture_Companion.html"
          title="Your own tokens: the transformer as a research architecture" loading="lazy"></iframe>
</div>

:::{admonition} Before you trust this result
:class: warning
**What is the baseline?** Tab 5 computes them rather than citing them. On METR-LA the
distance between doing nothing and doing something is roughly four times the distance
between a 2018 graph model and the 2023 state of the art. If your proposed architecture is
not compared against the naive predictor, the headline number is not interpretable.

**How was the data split, and why is that honest?** Speed series from adjacent detectors on
the same corridor are nearly the same series. A random split over five-minute intervals puts
the same congestion event on both sides of the line; split by time, and say which period the
model never saw.

**What does it do on the ugly cases?** The measured neighbour set is only 48% stable between
the morning and evening peaks. A fixed adjacency is a modelling assumption that is wrong at
least half the day, and the incidents you care about are exactly the times it is most wrong.
:::

---

Next: {doc}`notes5-vision` &mdash; the same architecture with pixels as tokens.
