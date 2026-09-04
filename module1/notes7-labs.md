# Labs, practice, and further reading

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 1 &middot; Module 1 &middot; Practice</span>
    <span class="notes-card-session">Sessions: Aug 27 &ndash; Sept 10</span>
  </div>
  <p class="notes-card-lede">The four notebooks and what each one <em>proves</em>; how to use this module in front of a vendor or a review board; the reading list; and five exercises. Everything here is practice &mdash; the explanations live in sections 1.1&ndash;1.3.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Notebooks that go with it</h4>
      <ul>
      <li><a href="lab1.html">Lab 1 &mdash; Python and ML warmup</a></li>
      <li><a href="lab2_word_embeddings.html">Lab 2 &mdash; From Word2Vec to Road2Vec</a></li>
      <li><a href="lab3_image_embeddings.html">Lab 3 &mdash; Image embeddings with a deep CNN</a></li>
      <li><a href="lab4_clip_vs_traditional_cv.html">Lab 4 &mdash; CLIP versus traditional computer vision</a></li>
      </ul>
    </div>
  </div>
</div>

## Labs

Four notebooks accompany this module. All run in Google Colab and use open data.
What matters is not that they run — it is what each one proves.

- **{doc}`lab1` — Python and ML warmup.** Loads a synthetic traffic-flow
  dataset, plots the Greenshields fundamental diagram, and fits a simple model.
  *Proves:* your environment works, and the supervised-learning pipeline
  (data → model → loss → optimization → evaluation) is a thing you can execute
  end to end.
- **{doc}`lab2_word_embeddings` — From Word2Vec to Road2Vec.** Write skip-gram
  with negative sampling from scratch, train it on a small corpus and see the
  analogy structure appear, then hand the *same trainer* random walks on the real
  road network around USF Tampa. *Proves:* representation learning is not about
  language — functional class does fall out of context statistics without ever
  being labeled. *And then:* the same lab shows that plain latitude and longitude
  recover it just as well, because a uniform random walk mostly encodes where a
  place is, not what it does. Evaluating a representation against a free baseline
  is the habit the lab is really teaching.
- **{doc}`lab3_image_embeddings` — Image embeddings with a deep CNN.** Load a
  pretrained ResNet-50, visualize what each layer responds to, extract
  2048-dimensional embeddings, and check that semantically similar images
  cluster. *Proves:* transfer learning in its simplest useful form, and gives
  you a feel for what "the representation is already in there" means.
- **{doc}`lab4_clip_vs_traditional_cv` — CLIP versus traditional computer
  vision.** Compare a closed-set classifier with a CLIP-style model on roadway
  and dashcam-style scenes; run zero-shot recognition against open-vocabulary
  prompts; probe the failure cases. *Proves:* why open-vocabulary perception
  matters for long-tail safety scenarios — and how brittle prompt phrasing can
  be.

Lab 4 physically lives in this module and is referenced again in Module 2 as the
bridge into multimodal models.

---

## Using this on the job

**When someone pitches you an AI system,** ask for the workflow diagram before
the architecture diagram. Which step is being automated, what is the checkpoint,
and what is the current process's baseline number. A vendor who cannot produce
those three things has not deployed the system anywhere that measured it.

**Before you fund a pilot,** apply the check from 1.1: is the output cheaper to
verify than to produce? If verifying requires a human to redo the work, the
pilot will show a time saving that evaporates at scale.

**When you have low-dimensional tabular data,** the answer is often not a
network. The one-dimensional result in 1.2 is not an edge case; speed-density
curves, travel-time functions, and delay relationships are exactly the shape
where a spline wins and can be plotted for a review board.

**When you have imagery,** start from a pretrained encoder. Almost nobody in an
agency setting should be training a vision model from scratch, and the questions
that actually determine success are about domain shift and label quality, not
architecture.

**When you evaluate a perception product,** ask what happens to inputs outside
its label set. A softmax with no "none of the above" class always returns a
confident answer.

**When you report results,** report the spread across seeds and the performance
on the ugly subset. This is the difference between an engineering report and a
marketing claim, and it is noticed.

---

## Critical reading

- LeCun, Y., Bengio, Y., & Hinton, G. (2015). Deep learning. *Nature, 521*,
  436–444. — *The canonical overview. Read for the framing; note how little of
  it is about evaluation.*
- Bishop, C. M., & Bishop, H. (2024). *Deep Learning: Foundations and Concepts*,
  Ch. 6. — *The learned-versus-fixed basis argument in 1.2, done properly.*
- Rumelhart, D. E., Hinton, G. E., & Williams, R. J. (1986). Learning
  representations by back-propagating errors. *Nature, 323*, 533–536.
- Mikolov, T., Chen, K., Corrado, G., & Dean, J. (2013). Efficient estimation of
  word representations in vector space. *arXiv:1301.3781*.
- He, K., Zhang, X., Ren, S., & Sun, J. (2016). Deep residual learning for image
  recognition. *CVPR*. — *ResNet, the encoder in Lab 3.*
- Radford, A. et al. (2021). Learning transferable visual models from natural
  language supervision (CLIP). *ICML*. — *Read the zero-shot results, then read
  the limitations section, which is unusually candid.*
- Veres, M., & Moussa, M. (2020). Deep learning for intelligent transportation
  systems: A survey of emerging trends. *IEEE T-ITS, 21*(8), 3152–3168.
- Karlaftis, M. G., & Vlahogianni, E. I. (2011). Statistical methods versus
  neural networks in transportation research. *Transportation Research Part C,
  19*(3), 387–399. — *Fifteen years old and still the most useful thing on this
  list for deciding whether you need a network at all.*

---

## Exercises

1. **Workflow audit.** Take a process you have actually worked on. Write it as
   trigger → ingest → transform → act → checkpoint → record. Label every step
   with one of the six leverage labels, mark the steps where AI must not act
   alone, and place the checkpoint immediately before the first irreversible
   action. State the three baseline numbers for the current process: how long,
   how often wrong, how much.
2. **The dictionary.** Take a binary logit model from a paper or a project you
   know. Write out its scale parameter, its constants, and its utility
   difference in neural network vocabulary. Then say what would have to change
   for it to become a two-layer network, and whether that change would help.
3. **Find the crossover.** For a prediction problem you care about, count $D$.
   Work out $K^D$ against $M(D+2)+1$ for a defensible $K$ and $M$. Which side of
   the crossover are you on, and does that match what you were planning to do?
4. **Break the softmax.** Construct a route-choice example where adding a
   near-duplicate alternative produces a share prediction you would not defend
   to a client. Then say what you would do about it.
5. **Sanity-check an embedding.** After Lab 2, pick five road segments whose
   character you know. Look at their nearest neighbors in the learned space.
   Write down one thing the embedding clearly got right and one thing it got
   wrong, and propose a check that would have caught the second one before you
   trusted the space.

---

## Where this goes next

Module 2 takes embeddings as given and asks what happens when the model can
decide, for each element, which other elements to look at. That is attention,
and the transformers built from it are the reason the last few years happened.
The through-line is direct: a transformer is a machine that reads in embeddings,
transforms them, and writes out embeddings — which is why this module had to
come first.
