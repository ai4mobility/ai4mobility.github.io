# 2.2 From static to contextual vectors

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 2 &middot; Section 2.2</span>
    <span class="notes-card-session">Session: Sept 17</span>
  </div>
  <p class="notes-card-lede">Module 1 ended with one fixed vector per word, per image, per road segment. That is a real limitation: <em>median</em> means one thing in a crash narrative and another in a statistics table, and a static vector cannot tell them apart. This section is the model that gives a word a different vector every time it appears &mdash; and the measurement of what that is actually worth on a real agency task.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Interactive companions on this page</h4>
      <ul>
      <li><a href="../_static/companions/Word2Vec_to_BERT_Companion.html" target="_blank" rel="noopener">From word2vec to BERT &#8599;</a></li>
      </ul>
    </div>
    <div>
      <h4>Read it after</h4>
      <ul>
      <li><a href="../module1/notes5-embeddings.html">1.5 Representation learning and embeddings</a></li>
      <li><a href="../module1/lab2_word_embeddings.html">Lab 2 &mdash; From Word2Vec to Road2Vec</a></li>
      </ul>
    </div>
  </div>
</div>

## What this section covers

- Why one vector per word fails: polysemy in transportation text
- Contextual embeddings &mdash; a vector per <em>occurrence</em>, not per word
- Masked language modelling: the task that forces a model to read context
- Encoder-only models (BERT) and what the twelve blocks do, layer by layer
- Frozen features versus fine-tuning, and what each costs
- The senses that <em>do not</em> separate, and why that matters for crash text

*The written section is posted after the Sept 17 meeting. Until then the companion
below is the material &mdash; it is the assigned preparation and it carries every number
this section will argue from.*

## One vector per word, or one per occurrence

Module 1 left every word with one vector, for ever. This companion is the model that
stops doing that, opened up: the wordpiece table that *is* word2vec, the twelve encoder
blocks stacked on top of it, and the fill-in-the-blank training task that forces the model
to read context in the first place. Drag the layer slider on tab 3 and watch the three senses
of `light` &mdash; a dashboard warning light, a lamp on the vehicle, a traffic signal &mdash; pull apart
across 42,956 real NHTSA complaint narratives.

Then the page changes the question. Tabs 4&ndash;7 stop asking how good the description is and give
the model a job: route a complaint to one of six component codes that NHTSA analysts have
already assigned. Four rungs are measured on one honest split &mdash; word counts, averaged GloVe,
frozen BERT, fine-tuned BERT &mdash; and **the frozen pretrained model loses to counting words**,
80.6% against 91.4%. Only fine-tuning, which lets all twelve blocks move, gets past it, at
93.0% and about 880 times the training cost. Train the last layer yourself on tab 6 and see
how little of the model has to move; then look at what the control column does to that 93%
before you believe anyone's benchmark, including this one.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion &mdash; From word2vec to BERT: what a contextual vector buys you</span>
    <a href="../_static/companions/Word2Vec_to_BERT_Companion.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/Word2Vec_to_BERT_Companion.html"
          title="From word2vec to BERT: what a contextual vector buys you" loading="lazy"></iframe>
</div>

:::{admonition} Before you trust this result
:class: warning
**What is the baseline?** Counting words. TF-IDF with logistic regression reaches 91.4% on
the component-code task, and the frozen pretrained encoder everyone reaches for first reaches
80.6%. A contextual representation is not automatically a better one &mdash; state the classical
baseline before you report the neural number, not after.

**How was the data split, and why is that honest?** Complaints about the same vehicle,
written from the same template, are not independent observations. Check what the control
column on tab 7 does to the 93% before treating that number as the model's performance on
text it has never seen.

**What does it do on the ugly cases?** The senses that separate here &mdash; a dashboard light
against a traffic signal &mdash; live in different topical neighbourhoods. Two senses that both
sit inside traffic engineering separate far less, and that is the case you will actually meet
in crash narratives and work-zone logs.
:::

---

Next: {doc}`notes3-attention` &mdash; the mechanism that makes the context reading possible.
