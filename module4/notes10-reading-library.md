(generative-reading-library)=
# Further reading: generative models in transportation

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 4 &middot; Closing page</span>
    <span class="notes-card-session">Read alongside the whole module</span>
  </div>
  <p class="notes-card-lede">What do transportation researchers actually do with generative models? This page answers with a reading library of 34 papers, grouped by eight transportation problems. Each card shows the paper&rsquo;s key figure and asks the same five questions, so you can compare the VAE, GAN and diffusion papers side by side and find a starting point for your own project.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Read it after</h4>
      <ul>
      <li><a href="notes3b-vae-basics.html">4.6 Variational autoencoders (VAE)</a> and <a href="notes4-gan.html">4.7 Generative Adversarial Networks (GAN)</a>, for the VAE and GAN papers</li>
      <li><a href="notes6-diffusion-basics.html">4.8 Diffusion models: the basics</a>, for the diffusion papers</li>
      </ul>
    </div>
    <div>
      <h4>Interactive companion</h4>
      <ul><li><a href="../_static/companions/Generative_Models_Reading_Library.html" target="_blank" rel="noopener">Reading library &#8599;</a>, on this page</li></ul>
    </div>
  </div>
</div>


What do researchers actually do with these models in transportation? This library answers with
34 papers, grouped by eight problems: several possible futures for road users, trip and OD data you
can share, crashes and near-misses for testing automated vehicles, rare cases in ADAS and crash data,
detector gaps, digital twins built from a few cameras, lidar generated from a camera, and storm damage
from a small dataset, plus three surveys. Each card shows the paper&rsquo;s key figure and answers the
same five questions: what it generates, from what, with which model, how the output is steered, and
what it is used for. A small diagram marks the move each paper makes: **sample** (more of the same),
**steer** (more of what you ask for), or **fill in** (complete what you saw).

Use it alongside this module. After 4.6 and 4.7, filter by **VAE** and **GAN** to see where those models
are still used; after the diffusion pages, filter by **Diffusion**, the family most papers since 2023
use. Read the **Watch out** line on every card: it names the trap, such as a realism score that says
nothing about safety, or synthetic trips that are not automatically private. End at **What the papers
share**, which lists the four steps most of these papers follow.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Reading library &mdash; Thirty-four papers on generative models in transportation</span>
    <a href="../_static/companions/Generative_Models_Reading_Library.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/Generative_Models_Reading_Library.html"
          title="Thirty-four papers on generative models in transportation, and what each one generates" loading="lazy"></iframe>
</div>

**Two other ways into the papers.** For how the diffusion part of a paper works (what is noised, what the network
reads, how it is trained, sampled and steered), use the {ref}`diffusion papers companion <diffusion-papers-library>`
in {doc}`4.10 <notes8-diffusion-literature>`. For the applications in more depth, organised by transportation problem,
see the handout *Generative Models in Transportation*.

---

Back to the {doc}`Module 4 map <index>`.
