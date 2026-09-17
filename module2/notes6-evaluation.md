# 2.6 Does it earn its keep?

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 2 &middot; Section 2.6</span>
    <span class="notes-card-session">Session: Sept 17</span>
  </div>
  <p class="notes-card-lede">A transformer is only worth its cost if it beats the method it would replace, on data the agency actually has. This section is that test, run eight ways on 399 real Florida crash narratives &mdash; and the classical baseline wins more often than the literature would lead you to expect.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Interactive companions on this page</h4>
      <ul>
      <li><a href="../_static/companions/Crash_Narrative_BERT_Companion.html" target="_blank" rel="noopener">Does BERT earn its keep on crash narratives? &#8599;</a></li>
      </ul>
    </div>
    <div>
      <h4>Read it after</h4>
      <ul>
      <li><a href="notes2-contextual.html">2.2 From static to contextual vectors</a></li>
      </ul>
    </div>
  </div>
</div>

## What this section covers

- Hallucination, grounding, and why fluent output is not evidence of correctness
- Grouped splits: what a random split leaks in agency text
- Frozen features, fine-tuning, and what each costs in wall-clock time
- Ceilings that are in the data, not in the model
- Latency, cost, and deployment constraints for transformer inference
- Reading a foundation-model claim about transportation: what was measured, on what data, against what baseline

*The written section is posted after the Sept 17 meeting. Until then the companion
below is the material &mdash; it is the assigned preparation and it carries every number
this section will argue from.*

## Does BERT earn its keep?

The first four sections are about the machine. This one is about the decision. Eight
things people routinely claim a BERT-style encoder can do with crash reports &mdash; contextual
representations, entity extraction, relation extraction, contributing-factor identification,
classification, semantic search, clustering, extractive question answering &mdash; run one at a
time against **399 real Florida long-form crash narratives** from twenty corridors in Pasco,
Hernando and Pinellas counties, de-identified first, then joined back to the coded crash
record so every claim can be scored against a field a human already filled in. Each task is
also run with the classical method it would replace, on a five-fold split grouped by
corridor, because a random split puts crashes from the same intersection &mdash; often the same
trooper, the same template &mdash; on both sides of the line.

The results do not all go the way the diagram implies, and that is the point. **TF-IDF with
logistic regression beats every frozen-BERT probe on all four classification targets**, and a
fine-tuned DistilBERT does not close the gap either (0.488 average precision against 0.619,
for 35 minutes of training instead of under a second). Raw `bert-base` embeddings are *worse
than guessing* as a search index. The k-means clusters split on whether the trooper writes
`V01` or `V1`. And the question "what was the weather?" has a recall ceiling of 12.5% before
any model is chosen, because the officer already recorded it in a checkbox and had no reason
to write it again.

Read panel 6 with the search box open &mdash; type your own words, then click a prepared query and
compare what each one surfaces. Then bring one answer to class: **name the one task on this
page where you would actually deploy the encoder in an agency workflow, and say what number
on the page convinced you.**

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion &mdash; Does BERT earn its keep on crash narratives?</span>
    <a href="../_static/companions/Crash_Narrative_BERT_Companion.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/Crash_Narrative_BERT_Companion.html"
          title="Does BERT earn its keep on crash narratives?" loading="lazy"></iframe>
</div>

:::{admonition} Before you trust this result
:class: warning
**What is the baseline?** TF-IDF and logistic regression, run on the same folds, and it wins
on all four classification targets &mdash; in under a second against 35 minutes. This page exists
because the baseline is the finding.

**How was the data split, and why is that honest?** Five folds grouped by corridor. Crashes
from one intersection share a trooper and often a template, so a random split leaks the
writing style across the fold boundary and inflates every number on the page.

**What does it do on the ugly cases?** Worse than the summary suggests, and in an instructive
way: the weather question has a 12.5% recall ceiling that no model can lift, because the
information was never in the text. Before choosing a method, check whether the field you want
was ever written down.
:::

---

Next: {doc}`notes7-labs` &mdash; the lab, the reading list, and where this goes in Module 4.
