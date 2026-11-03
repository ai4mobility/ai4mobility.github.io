(agent-context)=
# 5.4 Context: what the model reads

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 5 &middot; Section 5.4</span>
    <span class="notes-card-session">Session: How an agent works</span>
  </div>
  <p class="notes-card-lede">A language model has no memory between calls. Every time the harness asks for the next step, it sends everything again: the instructions, the tool descriptions, the whole history. That bundle is the context. This section measures the context of our recorded SUMO runs, shows why a longer context is not a better one, and teaches the milestone paper on bringing knowledge in from outside, retrieval-augmented generation (RAG), in depth.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Read it first</h4>
      <ul>
      <li><a href="notes2-loop.html">5.2 A model in a loop</a></li>
      <li><a href="../module2/notes5-bert.html">2.5 BERT</a> (the retriever's encoder)</li>
      </ul>
    </div>
    <div>
      <h4>Used again in</h4>
      <ul>
      <li><a href="index.html">Module 5 &mdash; skills, memory, and planning (the second session)</a></li>
      <li><a href="../module6/index.html">Module 6 &mdash; Evaluation and fine-tuning</a></li>
      </ul>
    </div>
  </div>
</div>

## What this section covers

- What the model reads on every call, measured on a recorded run
- Why the context grows at every step, and what that costs
- Lost in the middle: why more context is not better context
- Five ways to keep the context useful, and what each one costs
- Summaries that drop the rule that mattered, measured
- Keeping the loop light: why a longer context lowers accuracy, and three questions about what an agent reads
- Milestone paper: **retrieval-augmented generation (RAG)**
- RAG for a safety analyst, and where retrieval breaks

## What the model reads on every call

```{figure} ../_static/figures/AGC_Context_Stack.png
:alt: Two stacked bars. Step 1 reads 510 tokens: instructions 80, tool descriptions 382, task 48. Step 10 reads 2,298 tokens: the same three parts plus 1,788 tokens of earlier replies and results.
:width: 100%

The context of the longest recorded run (condition D, seed 0) at its first and last step, counted with the model's own tokenizer.
```

The longest of our recorded runs ({doc}`5.2 <notes2-loop>`) ran out of steps after ten calls. At step 1 the model
read 510 tokens: 80 of instructions, 382 describing the three tools, and 48 for the task. At step 10 it read 2,298:
the same 510, plus 1,788 tokens of history, every reply the model wrote and every result the harness pasted back.

Two things follow. The tool descriptions are three-quarters of the first call, and they are sent again on every
call; give an agent ten tools and they dominate. And the model keeps nothing between calls. If the harness drops
something from this text, the model has never seen it.

## The context grows at every step

```{figure} ../_static/figures/AGC_Growth.png
:alt: Tokens read at each step for every recorded run, rising in nearly straight lines from 510 at step 1; the longest run reaches 2,298 at step 10. A box gives the arithmetic: about 206 tokens added per step, so step k reads about 510 plus 206 times k minus 1.
:width: 100%

Every recorded run reads more at every step, by about one reply and one result each time.
```

Each step adds about 206 tokens in our runs (116 to 310): one reply and one tool result. So step *k* reads about
510 + 206·(*k* − 1), and the total read over *n* steps is

$$
\text{total read} \;\approx\; n\,F \;+\; \Delta\,\frac{n(n-1)}{2},
$$

with *F* = 510 tokens read at every step and Δ = 206 tokens added per step. **In words:** the first term is the fixed
part, re-read every step; the second grows with the square of the number of steps, so doubling the steps roughly
quadruples the reading. For our ten-step run the formula gives 5,100 + 9,270 = 14,370 tokens; we measured 14,723,
against 906 tokens written, about 16 read for each one written. That is cost and time, because every token read is
paid for, and it is attention: the longer the text, the more there is to get lost in.

(lost-in-the-middle)=
## Lost in the middle

```{figure} ../_static/figures/AGC_LITM.png
:alt: Accuracy against the position of the passage holding the answer among 20 passages. The curve starts at 75.8 percent in the first position, falls to 53.8 percent in the tenth, and rises to 63.2 percent in the last. A dashed line at 56.1 percent marks the score with no passages; another at 88.3 percent marks the score with only the answer passage.
:width: 100%

GPT-3.5-Turbo answers 2,655 questions with 20 retrieved passages, one of which holds the answer (Liu et al., 2024, Table 6). With the answer in the middle, it does worse than with no passages at all.
```

If the context grows, can we keep everything and let the model sort it out? Liu and colleagues (Stanford,
UC Berkeley and Samaya AI; *Transactions of the ACL*, 2024) tested exactly that. Give a model a question and
twenty passages, one of which contains the answer, and move the answer passage from the first slot to the last.

The accuracy curve is a U. The model does best when the answer is at the start (75.8%) or the end (63.2%), and
worst in the middle (53.8% in the tenth slot). That middle score is below the 56.1% the model gets with no
passages at all: nineteen passages of distraction cost more than the one useful passage gave. The paper reports the
same pattern for most of the models it tested.

For an agent, position is a design choice. The task and the rules belong at the start, the latest result at the
end, and the middle is where old, unimportant steps sit, or better, where they leave the context.

## Five ways to keep the context useful

| Move | What it does | In a transportation agent |
|---|---|---|
| **Leave it out** | send only what this step needs | return the average delay, not the 2,786-vehicle trip file |
| **Look it up** | keep knowledge outside; fetch the relevant part | retrieve the manual section on left-turn phasing when it is asked about |
| **Summarize** | replace old steps with a short summary | "tested 6 plans; best valid so far 54/22" instead of six full results |
| **Split the work** | give a sub-task its own short context | one agent screens the crash records; another writes the memo from its findings |
| **Clear old results** | replace tool results older than a few steps with a placeholder; keep the model's own steps | older simulation results become "[output omitted]" |

All five are harness design, and each has a cost. Leaving out can drop something you needed. Retrieval can bring
back the wrong page. Clearing can drop a rule that appeared only in an old result. Splitting the work comes later in {doc}`this module <index>`. And summaries can drop the one rule
that mattered, which we measured.

## Summaries can drop the rule

Summarizing is the obvious fix for a growing context, so we tested it. We gave the record of our longest run (the
ten-step condition-D run, 1,877 tokens as a record) to the same small model and asked for a summary the agent could
use instead of the record, in at most 60 words: six times with a plain request, and six times adding "Copy every
timing limit exactly, with its number."

| Asked to summarize run D/0 in at most 60 words, 6 times each | Plain request | "Copy every timing limit exactly" |
|---|---|---|
| Kept the 21 s pedestrian minimum (shown once, at step 1) | 1 of 6 | 1 of 6 |
| Kept the 120 s cycle maximum (in the last two errors) | 3 of 6 | 5 of 6 |
| Mentioned pedestrians at all | 0 of 6 | 0 of 6 |

The pedestrian minimum survived once in each set of six, and the word "pedestrian" never appeared. The cycle
maximum did much better. Look at where each rule sat: the pedestrian minimum appeared once, in the first tool
result, deep in the middle of the record by step 10; the cycle maximum appeared in the last two error messages, at
the end. That is the U-shape of {ref}`lost in the middle <lost-in-the-middle>` again, inside a summary. The summaries also
ran to 82 words on average against a limit of 60, and several mixed up which plan gave which delay.

:::{admonition} Before you trust this result
:class: important
**What is the baseline?** The same request without the instruction to keep limits.

**How was the data split, and why is that honest?** One recorded run, twelve summaries, six per instruction, all
with the same model that ran the agent.

**What does it do on the ugly cases?** A larger model would likely keep more; we did not measure it. The lesson does
not depend on the size of the model: a summary is a new context that nobody checked.
:::

The fix that always works is to keep rules out of the summary: put them in the instructions, repeat them where they
apply, and enforce them in the harness, as condition C of {doc}`5.2 <notes2-loop>` did.

(keeping-the-loop-light)=
## Keeping the loop light

```{figure} ../_static/figures/AGC_Feed_Less.png
:alt: Left, accuracy against context length from 1K to 32K tokens on the NoLiMa benchmark. GPT-4o stays near 98 percent up to 2K tokens and falls to 69.7 percent at 32K; Llama 3.1 8B falls from 65.7 percent at 1K to 14.2 percent at 32K. A dashed line marks our SUMO agent's context at step 10, 2,298 tokens. Right, three questions with measured token counts: one SUMO run's raw trip file is 481,729 tokens against 74 for the tool's summary; the same intersection record is 326 tokens as HTML, 244 as JSON and 186 as Markdown; after ten steps the recorded run carried 1,788 tokens of history against 89 for a note of the timings it tested.
:width: 100%

Feed it less, and it thinks more clearly. Leaving out what a step does not need saves the most; plain text and a short note save more.
```

Lost in the middle is about *where* a fact sits. Length is a second problem: a longer context lowers accuracy even
when the fact is easy to reach.

**Length alone costs accuracy.** NoLiMa (Modarressi et al., ICML 2025) hides one fact in a long text and words the
question so that it shares almost no words with the fact. With 1K tokens of text around the fact, GPT-4o answers
98.1% correctly; with 32K tokens, 69.7%. Llama 3.1 8B falls from
65.7% to 14.2%. Both models claim a 128K-token window, and 10
of the 12 models tested scored half or less of their short-text score at 32K. Other studies point the same way.
Chroma tested 18 models: every one answered better from a focused prompt of about 300 tokens than from the full
113,000-token version of the same question (Hong et al., 2025). Du et al. (2025) measured drops of 13.9% to 85% as the
input grew, even when the model could find the evidence perfectly. And giving one task over many turns instead of
all at once lowered scores by 39% on average (Laban et al., ICLR 2026). The window printed on the box is not the length
a model uses well. In NoLiMa the smaller Llama also drops sooner; the model in our runs is smaller still, and we did
not measure it.

**Three questions about what the agent reads.** Our SUMO agent gives a measured number for each, counted with its own
tokenizer.

1. **Only what this step needs?** One SUMO run of the current plan 50/30 writes a trip file of
   481,729 tokens for 2,786 vehicles, 14.7 times our model's
   32,768-token window. The tool returns 74 tokens: the cycle, the vehicle
   count, the average delay and the delay per approach. This is the biggest saving, and it is a harness decision.
2. **Plain text?** The same intersection record costs 326 tokens as an HTML page,
   244 as JSON and 186 as Markdown. Format helps, but far less than leaving
   things out.
3. **Can it write a note, and drop the rest?** After ten steps, run D/0 carried 1,788
   tokens of history. A note of the timings it tested is 89 tokens:
   "current 50/30 = 21.5 s/veh. Tested: 60/30 21.7, 65/30 21.6, 70/30 21.7, 75/30 21.4. Best so far: 75/30 at 21.4 s/veh." The history already held a timing that passed the check, 75/30 at
   21.4 s/veh from step 8. The agent never submitted it. It spent its last two steps on 80/30 and 85/30,
   which break the 120 s cycle limit, and ran out of steps.

A notes app such as Obsidian keeps notes as Markdown files on your own disk that an agent can read and edit, which
covers questions 2 and 3. Question 1 is up to whoever writes the tools.

**Clear old results before you summarize.** For a long loop, the cheapest move is to keep the model's own reasoning
and actions and replace tool results older than a few steps with a short placeholder. JetBrains researchers compared
this with asking a model to summarize the old steps, on coding agents fixing real GitHub issues (SWE-bench Verified).
Clearing roughly halved the cost of keeping everything and solved about as many issues as summarizing: 54.8% against
53.8% for Qwen3-Coder 480B, for example. The summarizing agents also ran longer, 52 turns against 44 for Gemini 2.5
Flash (Lindenbauer et al., 2025). Anthropic's guide to context calls clearing tool results "one of the safest lightest
touch forms of compaction" (Anthropic, 2025). Clearing deletes but never rewrites, so unlike the summaries above
it cannot mix up which timing gave which delay. It can still drop a rule that appeared only in an old result, like the 21 s
pedestrian minimum in our step-1 result. The fix is the same as for summaries: rules go in the instructions and the
harness.

**What clearing does not fix.** In the check-then-retry runs of {doc}`5.5 <notes5-architectures>` (seed 0), from
step 6 to step 10 the model wrote that each new delay was "lower than the 21.5 seconds" when it was 21.7 or 22.2.
That sentence is the model's own text, so clearing old tool results keeps it, and the model re-read it at every step.
Laban et al. describe the same pattern in long conversations: when a model takes a wrong turn, it gets lost and does
not recover. Two things help: a check outside the model, as the harness did when it rejected each submission, and a
fresh start from a short note that the harness has checked.

:::{admonition} Before you trust this result
:class: important
**What is the baseline?** For the token counts, the same content with nothing left out (the trip file) or in another
format. For the curve, each model's own score on short texts.

**How was the data split, and why is that honest?** The token counts are measurements, not a trained model. They are
exact for these texts and this tokenizer (Qwen2.5-1.5B); another tokenizer, or another HTML page, gives another count.
The curve is one benchmark task, on models other than ours. The clearing result comes from coding agents, not traffic
ones.

**What does it do on the ugly cases?** We did not test the note in a run, so we do not know whether our model would
have submitted 75/30 after reading it. And clearing can drop a rule that lived only in an old result.
:::

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
  tool with permissions ({doc}`5.3 <notes3-tools>`), not copied into an index that anyone with access to the
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
fix it. That is evaluation, and it is {doc}`Module 6 <../module6/index>`.

| Fit card — context and retrieval | |
| --- | --- |
| **Idea in one sentence** | Decide what the model reads on every call; keep large or changing knowledge in a searchable index and fetch only the relevant part. |
| **Why it works** | The model answers from what is in front of it; an index can be updated, cited and checked, and weights cannot. |
| **Fits these tasks** | Manuals, policies, past studies, data dictionaries, long histories of tool results. *Leverage: retrieval.* |
| **Needs this data** | Clean documents split at headings, with titles and dates, and test questions with known answers. |
| **Breaks when** | The index is stale, pieces are cut badly, the answer is buried in a long context, or a summary drops a rule. |
| **Keep the classical method when** | The answer is a lookup in a table or a database query; then call a tool, not a retriever. |

## Check yourself

1. Your agent's tenth step reads 9,000 tokens, and the pedestrian limit appears once, near the start of a long tool
   result. Name two harness changes that make it harder to lose.
2. A colleague proposes fine-tuning a model on the district's design manual "so it knows the manual". Using the
   hot-swap result, make the case for an index instead, and name one case where fine-tuning would still help.
3. Your RAG assistant answers a question about a crash modification factor correctly but cites the wrong chapter.
   Is that a pass or a fail? Why?
4. An agent helps a TMC operator review last night's incidents, and each incident record arrives as a 40-page PDF
   export from the CAD system. Which of the three questions in {ref}`keeping the loop light <keeping-the-loop-light>`
   does this setup fail, and what would you change first?

## Sources

- Lewis, P., et al. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. *NeurIPS*.
  [arXiv:2005.11401](https://arxiv.org/abs/2005.11401).
- Liu, N. F., et al. (2024). Lost in the middle: How language models use long contexts. *Transactions of the ACL*
  12. [arXiv:2307.03172](https://arxiv.org/abs/2307.03172).
- Modarressi, A., et al. (2025). NoLiMa: Long-context evaluation beyond literal matching. *ICML*, Table 3.
  [arXiv:2502.05167](https://arxiv.org/abs/2502.05167).
- Hong, K., Troynikov, A., & Huber, J. (2025). [Context rot: How increasing input tokens impacts LLM
  performance](https://www.trychroma.com/research/context-rot). Chroma technical report.
- Du, Y., et al. (2025). Context length alone hurts LLM performance despite perfect retrieval.
  [arXiv:2510.05381](https://arxiv.org/abs/2510.05381).
- Laban, P., Hayashi, H., Zhou, Y., & Neville, J. (2026). LLMs get lost in multi-turn conversation. *ICLR*.
  [arXiv:2505.06120](https://arxiv.org/abs/2505.06120).
- Lindenbauer, T., et al. (2025). The complexity trap: Simple observation masking is as efficient as LLM
  summarization for agent context management. NeurIPS 2025 Workshop on Deep Learning for Code in the Agentic Era.
  [arXiv:2508.21433](https://arxiv.org/abs/2508.21433).
- Anthropic (2025). [Effective context engineering for AI
  agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents).
- Qwen Team (2024). Qwen2.5-1.5B-Instruct, the model in the recorded runs and the summary test.
- Fried, D., & Neubig, G. (2026). [CMU 11-768 AI Agents](https://www.cmu-agents.com/), lectures on context and
  retrieval.

---

Next: skills, memory and planning, the second half of {doc}`this module <index>`: what an agent keeps between tasks.
