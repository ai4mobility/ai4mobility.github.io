(agent-rag)=
# 7.2 Retrieval (RAG): looking things up in agency documents

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 7 &middot; Section 7.2</span>
    <span class="notes-card-session">Session: Context, RAG, and memory</span>
  </div>
  <p class="notes-card-lede">Some knowledge is too long to send on every call, or changes too often to train into a model: design manuals, SOPs, past studies. Keep it outside the model and look up only the part a question needs. This section reads the milestone paper behind that idea, retrieval-augmented generation (RAG), in depth; applies it to a safety analyst's documents; lists where retrieval breaks; and ends with a hands-on companion that builds RAG on FDOT District 7's hurricane signal SOP and shows what RAG cannot do.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Read it first</h4>
      <ul>
      <li><a href="notes1-context.html">7.1 Context: what the model reads</a></li>
      <li><a href="../module2/notes5-bert.html">2.5 BERT</a> (the retriever's encoder)</li>
      </ul>
    </div>
    <div>
      <h4>Used again in</h4>
      <ul>
      <li><a href="index.html">Module 7 &mdash; memory</a> (recall from stored text that the work itself wrote)</li>
      <li><a href="../module8/index.html">Module 8 &mdash; AI-ready data</a> (documents split well and kept current)</li>
      </ul>
    </div>
  </div>
</div>

## What this section covers

- Milestone paper: **retrieval-augmented generation (RAG)**
- RAG for a safety analyst
- Where retrieval breaks, and a fit card for context and retrieval
- Hands-on: RAG on the District 7 signal SOP, step by step; what RAG cannot do; and from RAG to an agent that reads
  (interactive companion)

## Milestone paper: retrieval-augmented generation

A language model keeps its facts in its weights. You cannot easily correct one fact, you cannot ask where a fact
came from, and sometimes the model invents one. **Retrieval-augmented generation** (Lewis, Perez, Piktus, Petroni,
Karpukhin, Goyal, Küttler, Lewis, Yih, Rocktäschel, Riedel and Kiela; Facebook AI Research, University College
London and New York University; NeurIPS 2020) gives the model a second memory that is just text: an index of 21
million 100-word passages of Wikipedia. For every question, a **retriever** finds the most relevant passages and a
**generator** writes the answer with them in front of it.

The paper calls the weights the *parametric* memory and the index the *non-parametric* memory. Keep those two
words. When an agency asks for a model that "knows" its design manual, the question is which memory the manual
should live in. Usually, the answer is the index.

```{figure} ../_static/figures/AGC_RAG.png
:alt: A question goes through a BERT question encoder; the top passages by dot product are fetched from a frozen passage index; a BART generator reads the question with each passage, and a weighted vote over passages gives the answer. A dashed line shows that only the question encoder and the generator are trained, on the answer alone.
:width: 100%

RAG's mechanism (Lewis et al., 2020, Fig. 1), redrawn with a transportation question. The passages shown are illustrative; the machinery is the paper's.
```

**The retriever.** Two BERT encoders, the same kind of model as in {doc}`2.5 <../module2/notes5-bert>`, turn the
question and every passage into vectors. The passages are encoded once, ahead of time, into an index. For a
question, the retriever returns the passages whose vectors have the largest dot product with the question's
vector: the same dot product as in attention, used here to search a library. Training used the top 5 or 10.

**The generator.** BART, a text-to-text transformer, reads the question joined to each retrieved passage and
writes an answer.

**Training.** Nobody tells the model which passage is the right one. It is trained only to produce the right answer,
and the question encoder learns to fetch passages that help. The passage encoder and the index stay frozen, which
means the library can be rebuilt without touching the model.

**Two ways to use the passages.** The probability of an answer *y* to a question *x* sums over the retrieved
passages *z*:

$$
p(y \mid x) \;\approx\; \sum_{z \in \text{top-}k} p(z \mid x)\; p(y \mid x, z)
$$

**In words:** the answer is a vote among the retrieved passages, weighted by how relevant each one looked to the
retriever. **RAG-Sequence** lets each passage write a whole answer and then votes, as in the equation.
**RAG-Token** votes again at every word, so different words can lean on different passages; that helps when an
answer must combine several sources.

:::{admonition} Going deeper &mdash; the retriever's score and the token-level vote
:class: dropdown
The retriever scores a passage by $p(z \mid x) \propto \exp\!\big(d(z)^\top q(x)\big)$, where $q(x)$ is the
question's BERT vector and $d(z)$ the passage's: a softmax over dot products, the same form as attention. Finding
the top-*k* among 21 million vectors is a maximum inner product search, done with a nearest-neighbour index
(FAISS). RAG-Token moves the sum inside the product over the answer's words:

$$
p(y \mid x) \;\approx\; \prod_{i=1}^{N} \sum_{z \in \text{top-}k} p(z \mid x)\; p(y_i \mid x, z, y_{1:i-1}) .
$$

The only training signal is $-\log p(y \mid x)$ on the answer; no label says which passage was right.
:::

**What the results say.**

| Task (measure) | Best model without retrieval | RAG-Sequence | Strongest comparison in the paper |
|---|---|---|---|
| Natural Questions (exact match) | 36.6, T5-11B+SSM | 44.5 | 41.5, DPR |
| FEVER, 3 classes (accuracy) | 64.0, BART | 72.5 | 76.8, best published, trained on evidence labels |
| Jeopardy questions judged more factual | 7.1%, BART | 42.7%, RAG-Token | – |

On Natural Questions, real questions people typed into Google, RAG answers 44.5% exactly right, against 36.6% for
an 11-billion-parameter model without retrieval; RAG's generator has about 400 million. On FEVER, checking whether a
claim is supported, it comes within about four points of the best published system, which was trained on labels
of which evidence to read.

:::{admonition} Before you trust this result
:class: important
**What is the baseline?** Closed-book models up to 11 billion parameters, and pipelines that retrieve and then
read as two separate steps (DPR).

**How was the data split, and why is that honest?** The standard benchmark test sets.

**What does it do on the ugly cases?** On the standard TriviaQA split, the simpler DPR pipeline (57.9) beats RAG
(56.8). And RAG's retriever was not learned from scratch: it started from DPR, which had already been trained to
find passages for two of these same datasets, Natural Questions and TriviaQA, so part of the retrieval quality was
bought in advance.
:::

**Swap the index, change the answer.** This is the experiment that matters most for agencies.

```{figure} ../_static/figures/AGC_Hotswap.png
:alt: Bars for 82 world leaders who changed between 2016 and 2018. With the index matching the year, 70 and 68 percent are answered correctly; with the other year's index, 12 and 4 percent.
:width: 85%

The answers follow the index, not the weights (Lewis et al., 2020, Section 4.5).
```

The authors took 82 world leaders who changed between 2016 and 2018 and asked the same model "Who is the" followed
by each position, once with a 2016 Wikipedia index and once with a 2018 index. With the index matching the year,
it was right 70% and 68% of the time; with the other year's index, 12% and 4%. The promise: when the design manual
is revised, rebuild the index and the agent knows the new rule. The warning: if the index still holds the old
manual, the agent will quote the old rule, confidently.

## RAG for a safety analyst

A safety analyst asks: what does our guidance say about crash modification factors for a road diet, and which of
our past studies used one?

- **What to index.** The documents the analyst already reads and trusts: the safety manual's chapters, the
  agency's crash-data dictionary, past safety studies. Split them where their authors split them, at headings,
  not every 100 words; a passage cut halfway through a table is worse than useless. Keep the section title with
  every piece so the retriever can match it.
- **What the answer must carry.** The document, section and date of every passage it used, so the engineer can
  open the source. That turns "the model said" into "chapter 13 says".
- **What to keep out.** Crash records that name people or give their addresses. Records are queried through a
  tool with permissions ({doc}`5.3 <../module5/notes3-tools>`), not copied into an index that anyone with access to the
  assistant can search. The index is a copy, and every copy is one more place personal data can leak from.

## Where retrieval breaks

| Failure | What happens | What to do |
|---|---|---|
| **Stale index** | the old manual is quoted | rebuild on every revision; test with a question whose answer changed |
| **Wrong piece** | a passage cut mid-table, or the right term in the wrong chapter | split at headings; keep titles; check the top results by hand |
| **Collapse** | the retriever returns the same passages for every question | in the paper, it happened on story writing, and results fell to the no-retrieval level |
| **Buried answer** | the right passage is retrieved but sits in the middle of a long context | retrieve fewer, better passages; put the best one first |

The common defence is a small set of test questions with known answers, run every time the index or the harness
changes. Check the retriever on its own first: if the right passage is not in the top results, no generator can
fix it. That is evaluation, and {doc}`Module 8 <../module8/index>` comes back to building such test sets from past cases.

| Fit card — context and retrieval | |
| --- | --- |
| **Idea in one sentence** | Decide what the model reads on every call; keep large or changing knowledge in a searchable index and fetch only the relevant part. |
| **Why it works** | The model answers from what is in front of it; an index can be updated, cited and checked, and weights cannot. |
| **Fits these tasks** | Manuals, policies, past studies, data dictionaries, long histories of tool results. *Leverage: retrieval.* |
| **Needs this data** | Clean documents split at headings, with titles and dates, and test questions with known answers. |
| **Breaks when** | The index is stale, pieces are cut badly, the answer is buried in a long context, a summary drops a rule, or the question is not a lookup at all (a plan, a complete list, something missing). |
| **Keep the classical method when** | The answer is a lookup in a table or a database query; then call a tool, not a retriever. |

(rag-sop-companion)=
## RAG on the signal SOP: build it, test it, and see what it cannot do

The companion below builds RAG one step at a time on a document District 7 uses: the FDOT D7 Traffic Signals SOP for
hurricanes (v1.5, June 2025), pages 5–11. You split the SOP into pieces and watch which rules get cut in half, turn
each piece into 384 numbers with a small sentence model, search the pieces by keyword, by meaning or both, build the
prompt and paste it into Claude, and let a checker test the citations in the answer. Every number about the SOP is
computed from its text.

Three results to look for:

- **Keyword search is hard to beat when the question uses the SOP's own words.** On 12 such questions, the classical
  method (BM25) found the rule as often as the embedding model, or more often. Asked in field words ("backup power
  units" for generators), every method drops, and a field-to-SOP glossary helps less on new questions than on the
  questions it was written from (tab 8).
- **Search always returns something.** No similarity cutoff separates the questions the SOP answers from the ones it
  does not (tab 6).
- **RAG is for lookups.** A plan, a sequence of steps, a complete list, something that is missing, or a judgment about
  the whole SOP needs many pieces spread over many sections, and the top three pieces hold almost none of them
  (tab 7). Tab 7 also covers what to expect when you give a document to a chat assistant, with an exercise that
  compares Claude's answers given no document, three pieces, and the whole SOP.
- **An agent reads in steps that depend on each other.** Tab 10 lets you play the agent on the SOP with
  `list_sections`, `search` and `open_section`, compares one search, a fixed workflow, the whole SOP and a scripted
  harness on the same question, walks one MUTCD lane-closure question through Part 6, and shows where transportation
  knowledge goes in the harness.

Meaning search on a question you type yourself loads a 45 MB model into your browser from the internet; everything
else works offline.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion &mdash; RAG on the signal SOP</span>
    <a href="../_static/companions/RAG_On_The_Signal_SOP_Companion.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/RAG_On_The_Signal_SOP_Companion.html"
          title="RAG on the signal SOP: how an agent looks things up" loading="lazy"></iframe>
</div>

## Check yourself

1. A colleague proposes fine-tuning a model on the district's design manual "so it knows the manual". Using the
   hot-swap result, make the case for an index instead, and name one case where fine-tuning would still help.
2. Your RAG assistant answers a question about a crash modification factor correctly but cites the wrong chapter.
   Is that a pass or a fail? Why?
3. A district engineer gives a chat assistant the 7-page signal SOP and asks for a plan for the 72 hours before
   landfall. Later the district puts all its SOPs, manuals and after-action reports into one project and asks the same
   question. Why can the second answer be worse even though the assistant has more documents, and what would you ask
   for instead?

## Sources

- Lewis, P., et al. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. *NeurIPS*.
  [arXiv:2005.11401](https://arxiv.org/abs/2005.11401).
- Robertson, S. E., Walker, S., Jones, S., Hancock-Beaulieu, M., & Gatford, M. (1995). Okapi at TREC-3. *TREC-3*
  (BM25, the keyword search in the companion).
- Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. *EMNLP*
  (the family of the companion's all-MiniLM-L6-v2 model).
- Edge, D., et al. (2024). From local to global: A graph RAG approach to query-focused summarization.
  [arXiv:2404.16130](https://arxiv.org/abs/2404.16130) (why plain RAG fails on whole-document questions).
- FDOT District 7 (2025). Traffic Signals Standard Operating Procedures Reference Guide, v1.5, pages 5–11 (the
  companion's document).
- Fried, D., & Neubig, G. (2026). [CMU 11-768 AI Agents](https://www.cmu-agents.com/), lectures on context and
  retrieval.

---

Next: memory, what an agent keeps from one task to the next, completes {doc}`Module 7 <index>`. That section is
still to be written; until then, the handout *Memory for AI Agents in Transportation Agencies* covers it.
