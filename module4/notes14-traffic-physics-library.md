(traffic-physics-library)=
# 4.14 How traffic flow theory gets into AI models

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 4 &middot; Section 4.14</span>
    <span class="notes-card-session">Session: Generative models in transportation</span>
  </div>
  <p class="notes-card-lede">Sections 4.11 and 4.12 put traffic knowledge into generative models. This page asks the same question of every kind of AI model in recent research: state estimation, forecasting, car-following, lane changing, and signal, ramp and platoon control. It is a reading library of 38 papers from 2021 to 2026, read in full, plus 64 more listed. They are sorted by the role traffic theory plays and by where it plugs into the model.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Read it after</h4>
      <ul>
      <li><a href="notes9-knowledge-guided.html">4.11 How transportation knowledge guides diffusion</a> and <a href="notes13-knowledge-ae-vae.html">4.12 How transportation knowledge guides AE and VAE</a>, for the places knowledge can enter a generative model</li>
      </ul>
    </div>
    <div>
      <h4>Interactive companion</h4>
      <ul><li><a href="../_static/companions/Traffic_Physics_AI_Library.html" target="_blank" rel="noopener">Reading library &#8599;</a>, on this page</li></ul>
    </div>
  </div>
</div>


Every paper in this library answers two questions. **Is the traffic theory still there when the finished model
runs?** And **where does it plug in**: the training data, the model itself, the loss, the moment the model runs, or a
check afterwards? The answers sort the papers into four groups.

- **1 Theory guides training.** An LWR or IDM error added to the loss, a rule such as string stability, a simulator
  that makes the training data. When the model runs, the theory is gone.
- **2 Theory stays in the model.** Layers built like a conservation law, a CTM or METANET model run as a layer, a
  traffic model whose errors a network learns to correct, or a safety layer that fixes each action as it is taken.
- **3 Theory tests the AI.** A trained model is checked for the waves, stable platoons and fundamental diagram it
  should produce.
- **4 AI learns the theory.** Symbolic regression and LLM agents propose the equation from data.

Each card shows the paper&rsquo;s key figure, the same five facts, the results with numbers checked against the paper,
and a **Watch out** line. Filter by your own task to find a starting point. Then read **What each way guarantees**,
near the end: only a property built into the model, or forced on every output, holds every time. Group 1 makes it
likely. The shock-speed test in {doc}`4.12 <notes13-knowledge-ae-vae>` showed the same thing on the course heatmaps.

(traffic-physics-library-companion)=
<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Reading library &mdash; How traffic flow theory gets into AI models</span>
    <a href="../_static/companions/Traffic_Physics_AI_Library.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/Traffic_Physics_AI_Library.html"
          title="How traffic flow theory gets into AI models: a reading library of 38 papers" loading="lazy"></iframe>
</div>

**Two other ways into these ideas.** For generative models only, with a worked test on the course heatmaps, go back
to {doc}`4.11 <notes9-knowledge-guided>` and {doc}`4.12 <notes13-knowledge-ae-vae>`. For generative models organized by
transportation problem, see the reading library in {doc}`4.13 <notes10-reading-library>`.

---

Next: {doc}`4.15 World models <notes11-world-models>` &mdash; generators that produce a future which responds to your
actions. Back to the {doc}`Module 4 map <index>`.
