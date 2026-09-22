# 2.3 Attention: the mechanism

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 2 &middot; Section 2.3</span>
    <span class="notes-card-session">Session: Sept 17</span>
  </div>
  <p class="notes-card-lede">A signal controller arbitrates among competing approaches, weighting each by how much demand it is carrying right now. Self-attention does the same thing over tokens, learns the weighting from data, and does it many times in parallel. This section is that mechanism, read off a real model rather than drawn &mdash; including the two-thirds of its heads that turn out to mean nothing at all.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Interactive companions on this page</h4>
      <ul>
      <li><a href="../_static/companions/Attention_Query_Companion.html" target="_blank" rel="noopener">Attention depends on which word is asking &#8599;</a></li>
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

- Self-attention as learned routing over a sequence
- Queries, keys and values; why the weights change with the asking word
- The scaled dot product: q&middot;k, the divide by &radic;d, and the softmax
- Multi-head attention, and what the heads specialise into
- Positional encoding &mdash; attention has no order until you give it one
- Why recurrence lost, and what the quadratic cost buys
- Reading an attention map honestly: sinks, positional heads, and attention &ne; importance

*The written section is posted after the Sept 17 meeting. Until then the companion
below is the material &mdash; it is the assigned preparation and it carries every number
this section will argue from.*

## Attention, from a real model's weights

Attention is the one mechanism in this module that everything else is built out of, and it is
usually taught with a figure that is quietly dishonest: a tidy arc diagram in which each word
attends to the single other word that explains it. This companion is built from a real model's
real weights, and it is the argument for why the tidy picture is the exception rather than the
rule.

The sentence is a transit incident log entry &mdash; *The stalled bus blocked the curb lane, and
passengers walked onto the roadway to reach the sidewalk* &mdash; run through `bert-base-uncased`,
with all 144 heads available to click. Tab 1 makes the central point: the weights depend on
**which word is asking**. Query `reach` and 0.452 of the row goes to `sidewalk`; query `walked`
and it splits, 0.247 to `roadway` against 0.235 to `sidewalk`; query `bus` and it spreads across
half the sentence. Same sentence, same head, three different pictures.

Tab 2 is the control, and it is what makes tab 1 evidence rather than decoration. Swap the two
destinations in the sentence and change nothing else: `reach`&rarr;`roadway` goes 0.148 to
**0.363** and `reach`&rarr;`sidewalk` goes 0.452 to **0.210**, while the `bus` and `lane` rows
move by at most 0.006. What moves shows the weights track the grammatical role; what does not
move shows the rest is not noise.

Then the honest part, on tab 4. Most heads in a trained transformer are not interpretable at
all: **72 of the 144 put more than half a row on `[CLS]` or `[SEP]`**, and 0.429 of all the
attention weight in the model lands on those two tokens. Another 13 are pure previous-word or
next-word heads &mdash; one of them sends a weight of 1.00 from every token to the next one, which
maxes out any naive "strongest attention" score and teaches nothing. Tab 3 shows where the
numbers come from: the q&middot;k dot product, the divide by &radic;d, the softmax, reproducing
the row exactly.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion &mdash; Attention depends on which word is asking</span>
    <a href="../_static/companions/Attention_Query_Companion.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/Attention_Query_Companion.html"
          title="Attention depends on which word is asking" loading="lazy"></iframe>
</div>

:::{admonition} Before you trust this result
:class: warning
**What is the baseline?** A head that looks impressive may be doing string matching or
position counting. Before reading meaning into a map, check it against the two degenerate
families: a head that parks its weight on `[CLS]`/`[SEP]`, and a head that always points one
position left or right.

**How was the data split, and why is that honest?** There is no split here &mdash; this is one
sentence and one model, which makes it a demonstration, not a result. The swap control is what
turns it into evidence, because it changes one thing and predicts in advance which rows should
move and which should not.

**What does it do on the ugly cases?** Head-averaged attention &mdash; the default in most
published figures &mdash; is 46% sink. Attention is not importance (Jain &amp; Wallace, 2019), and
a weight of 0.45 on a token whose value vector is small moves almost nothing.
:::

---

Next: {doc}`notes4-gpt` &mdash; the same five operations, written out in code and run on a model we trained here.
