# 2.1 Tokens: the unit a model actually reads

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 2 &middot; Section 2.1</span>
    <span class="notes-card-session">Session: Sept 17</span>
  </div>
  <p class="notes-card-lede">Before a transformer can attend to anything, something has to decide what the pieces <em>are</em>. This section is about that decision &mdash; how text is cut into subword tokens, what happens to transportation jargon when it is, and why the answer sets the price of everything that comes after it.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Interactive companions on this page</h4>
      <ul>
      <li><a href="../_static/companions/Tokenization_Companion.html" target="_blank" rel="noopener">Tokens: the unit a language model actually reads &#8599;</a></li>
      </ul>
    </div>
    <div>
      <h4>Read it after</h4>
      <ul>
      <li><a href="../module1/notes5-embeddings.html">1.5 Representation learning and embeddings</a></li>
      </ul>
    </div>
  </div>
</div>

## What this section covers

- Tokenization: characters, words, and the subword compromise
- Byte-pair encoding &mdash; a vocabulary is designed, not discovered
- What transportation jargon costs when it fragments
- Context windows, and what a token costs in latency and money
- Tokenizing things that are not words: an image as a sequence of patches

*The written section is posted after the Sept 17 meeting. Until then the companion
below is the material &mdash; it is the assigned preparation and it carries every number
this section will argue from.*

## What a token is, and what it costs

What a token is, and what it costs, decides whether everything after it is
affordable. Work through this companion before class. The tokenizer inside it is
the real thing: the published `o200k_base` (current OpenAI generation) and
`r50k_base` (GPT-2) merge tables, byte-level BPE, verified piece-for-piece
against OpenAI's `tiktoken`. Type your own jargon into tab 3 and see exactly what
the model receives &mdash; then find three terms from your subfield that fragment
into three or more tokens.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion &mdash; Tokens: the unit a language model actually reads</span>
    <a href="../_static/companions/Tokenization_Companion.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/Tokenization_Companion.html"
          title="Tokens: the unit a language model actually reads" loading="lazy"></iframe>
</div>

---

Next: {doc}`notes2-contextual` &mdash; what the model does with those tokens once it has them.
