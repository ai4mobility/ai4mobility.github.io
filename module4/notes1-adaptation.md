# 4.1 The adaptation ladder: what your corpus actually needs

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 4 &middot; Section 4.1</span>
    <span class="notes-card-session">Session: Oct 1</span>
  </div>
  <p class="notes-card-lede">&ldquo;We should fine-tune a model on our corpus&rdquo; is the most common sentence in a transportation AI project, and it names three different operations that want different things. This section is the decision rule: what each rung of the adaptation ladder changes, what it costs, which one your problem actually needs, and what has to be true before you are allowed to climb. Most problems people reach for fine-tuning to solve are retrieval problems.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Read it after</h4>
      <ul>
      <li><a href="../module2/notes4-gpt.html">2.4 Building one: a GPT you can read</a> &mdash; what you would be fine-tuning, exactly</li>
      <li><a href="../module2/notes7-evaluation.html">2.7 Does it earn its keep?</a> &mdash; the standard this section holds you to</li>
      </ul>
    </div>
    <div>
      <h4>Before you train anything</h4>
      <ul>
      <li>Run the prompt-only baseline</li>
      <li>Run the classical baseline</li>
      <li>Write down the number that would make you stop</li>
      </ul>
    </div>
  </div>
</div>

## What this section covers

- The three different operations people call &ldquo;fine-tuning,&rdquo; and how to tell which one you want
- The adaptation ladder, rung by rung, with what each one changes and what it needs
- Why a retrieval pipeline beats a fine-tune for most agency-document problems
- What actually changes in the code when you move from training a model to adapting one &mdash; starting with the tokenizer, which is no longer yours
- Whether your corpus is big enough, and whether you are allowed to use it
- What &ldquo;it worked&rdquo; has to mean, including the check almost nobody runs

## Three things called fine-tuning

Before choosing a method, name the goal. These are not variations on one technique; they change
different things and need different data.

**Continued pretraining** keeps the next-token objective from {doc}`2.4 <../module2/notes4-gpt>`
and simply runs it over your domain text, starting from pretrained weights instead of random
ones. It changes how the model *writes* &mdash; its vocabulary, its register, what it finds
plausible. It needs raw text and no labels at all, and it needs a lot of it.

**Instruction or supervised fine-tuning** trains on pairs: a request and the response you wanted.
It changes what the model *does with a request* &mdash; the format it answers in, the steps it
takes. It needs curated pairs, which is the expensive part everyone underestimates, and it
teaches format far more reliably than it teaches facts.

**Task-head fine-tuning** throws the language-model head away and attaches a classifier or an
extractor. It changes what the model *outputs* &mdash; six component codes, a severity level, a
span of text. It needs labels, and it is the one that pays most often in this field. Assignment 2
and the crash-narrative work are both this.

A useful test: if you cannot say which of the three you mean, you do not yet have a problem
statement, and no amount of GPU time will fix that.

## The ladder

Each rung is more expensive than the one above it, in money, in time, and in how much can go
wrong quietly. The practical skill is refusing to climb further than the problem requires.

| Rung | What it changes | What it needs | Reach for it when |
| --- | --- | --- | --- |
| **Prompting** | Nothing in the model. The instructions and examples in the context. | A written spec of the task and a handful of examples. Hours. | Always first. It is the baseline every other rung has to beat, and it often is not beaten. |
| **Retrieval (RAG)** | Nothing in the model. What is *in* the context at answer time. | The documents, chunked and indexed, plus a retriever you evaluate separately. | The answer lives in a document. Anything that must cite a manual, a standard, a report, or a log. |
| **Task head** | A new output layer, and usually the top blocks. | Labels. Hundreds to a few thousand. | The output is a fixed set of categories or spans, and you have labelled examples. |
| **LoRA / adapters** | A small number of added weights; the base model stays frozen. | Labels or pairs, plus a GPU for tens of minutes. | The task head is not enough and you need the generator itself to behave differently, without a full training budget. |
| **Full fine-tune** | Every weight. | More data, more compute, and a plan for what breaks. | You have a genuinely large, genuinely different corpus and evidence that the rungs above it failed. |
| **Continued pretraining** | Every weight, on raw text, before you even have a task. | Domain text at a scale that is rare outside an agency data warehouse. | The domain's *language* is far from anything the base model saw, and you have the text to prove it. |

Two things this table is trying to say at once. The cheap rungs change the *context*, not the
weights, which means they are reversible, auditable, and updatable on the afternoon a standard
changes. The expensive rungs change the weights, which means the knowledge is baked in, undated,
and impossible to cite.

## Why retrieval usually wins here

The problems that come up in this field &mdash; what does the manual say about this taper length,
which reports mention this failure mode, what did the district decide last time &mdash; share a
shape. The answer exists, in a document, and the user needs to be shown *where*. Fine-tuning is a
bad fit for that shape three separate ways: the model cannot cite what it absorbed, it cannot be
updated without retraining, and it will answer confidently when the document says nothing at all.

Hold on to the negative result from {doc}`2.7 <../module2/notes7-evaluation>`: on 399 real Florida
crash narratives, the question &ldquo;what was the weather?&rdquo; has a **12.5% recall ceiling**
before any model is involved, because the narratives simply do not say. No amount of adaptation
lifts a ceiling that the corpus imposes. Check what your text contains before you ask who should
read it.

## If you do adapt: what changes in the code

{doc}`2.4 <../module2/notes4-gpt>` ends with three edits that turn the from-scratch model into an
encoder, a classifier, or a model over non-language tokens. Moving from *our* model to a
*pretrained* one changes three more things, and the first is the one that surprises people.

**The tokenizer is not yours anymore.** You inherit the base model's byte-pair vocabulary, and
your jargon has to live in it. Before anything else, measure the damage: how many tokens does the
base tokenizer spend on *signalized*, *spillback*, *superelevation*, a route shield, an FPID
number? This is {doc}`2.1 <../module2/notes1-tokens>` pointed at your own corpus, and it is a
real decision with two bad options. Add tokens and you must resize the embedding matrix, where
the new rows arrive random and untrained beside rows that have seen billions of tokens. Do
nothing and every mention of your core concepts costs four tokens and arrives fragmented.

**The learning rate and the duration flip.** Training from scratch used 1e-3 for thousands of
steps. Adaptation runs one or two passes at something nearer 1e-5, because you are nudging a
model that already works rather than building one that does not. The failure mode also flips:
from scratch, the risk is that nothing is learned; adapting, the risk is that something is
*unlearned*.

**Choose which parameters move.** LoRA freezes the base weights and trains a small low-rank
addition beside them &mdash; Hu et al. (2022) report adapting a 175-billion-parameter model with
roughly four orders of magnitude fewer trainable parameters. For this course that matters for a
blunt reason: it fits on hardware you have, and it leaves the original weights intact, so the
comparison against the un-adapted model is always available.

## Is your corpus big enough, and may you use it?

**Size.** The corpora that produced the base models are measured in hundreds of billions of
tokens. The complaint corpus behind {doc}`2.4 <../module2/notes4-gpt>` is **4,548,008** tokens
&mdash; large enough to train a small model from scratch to a real result, and small by the
standards of continued pretraining by a factor no amount of care closes. Gururangan et al. (2020)
is the reference worth reading here: domain-adaptive pretraining pays when the domain is far from
the pretraining distribution *and* unlabelled domain text is plentiful, and task-adaptive
pretraining on a small, task-relevant slice is often the better buy.

**Licence.** This catches people every semester. The MUTCD is a federal publication and free to
use. The Highway Capacity Manual is copyrighted by TRB and is not, however convenient it would be.
Agency reports, FDOT standards, NTSB dockets, TRID abstracts and 311 text all have different
answers. Check before you ingest, not after you present.

**People in the text.** Crash narratives, complaint filings and 311 records contain names,
addresses, plate fragments and medical detail. De-identify before the text goes anywhere near a
model or an index, and if the data is identifiable, the course's IRB-before-collection rule
applies exactly as it does to the capstone.

## What &ldquo;it worked&rdquo; has to mean

Held-out perplexity on domain text is necessary and nowhere near sufficient &mdash; it tells you
the model finds your text less surprising, not that anyone is better off. Three numbers, on a
downstream task, or the result does not count:

| Comparison | Why it is there |
| --- | --- |
| The frozen base model with a decent prompt | The rung above. Most adaptations do not beat it, and finding that out is the point. |
| The classical method it would replace | Keyword search, a rule set, a regex, a human protocol. The thing that already exists. |
| Your adapted model | Only meaningful beside the other two. |

And one more, which almost nobody runs: **the forgetting check.** Score the adapted model on
something outside your domain that it could do before. If that number has collapsed, you did not
adapt a general model &mdash; you traded one away, and you should know the price you paid.

| Fit card — adapting a pretrained language model to a domain corpus | |
| --- | --- |
| **Idea in one sentence** | Start from a model that already knows the language, and change the smallest thing that gets the behaviour you need — the context, the output layer, or a small set of added weights. |
| **Why it works** | The expensive, general competence is already paid for. Domain adaptation only has to move the model a short distance, so the cheapest intervention that covers that distance is the right one. |
| **Fits these tasks** | Classifying or extracting from agency free text; answering questions grounded in manuals and reports; drafting to a house format. *Leverage: extraction · classification · retrieval · generation.* |
| **Needs this data** | For the cheap rungs, documents and a written task spec. For the expensive ones, labels in the hundreds to thousands, or raw domain text at a scale most groups do not have. Plus a held-out set built from real queries, not a public benchmark. |
| **Breaks when** | The answer is not in the corpus at all; the corpus is too small for the rung chosen; the tokenizer fragments the domain vocabulary; the model is asked to cite what it absorbed; general ability is quietly lost. |
| **Keep the classical method when** | Keyword search over a well-indexed document set already answers the question — and for a small standards library it very often does. The task is a lookup with a defensible, auditable answer. Or the output has to be explained to a review board line by line. |

:::{admonition} Before you trust this result
:class: important
**What is the baseline?** The frozen base model with a prompt, and the classical method. An
adaptation reported without both is a claim about effort, not about performance.

**How was the data split, and why is that honest?** Agency text is written by a small number of
people to a small number of templates, so a random split leaks style and phrasing across it.
Split by document, by author, by district or by period — and say which, and why.

**What does it do on the ugly cases?** The records where the field is blank, the abbreviation is
local, the narrative is two lines long. Report the ceiling the corpus imposes before you report
the score.
:::

## Check yourself

1. An agency wants a system that answers questions about its work-zone standards, citing the
   clause. Which rung, and what would have to be true for the answer to be a different one?
2. You have 800 labelled maintenance tickets and want to route incoming ones into six categories.
   Name the rung, the baseline you have to beat, and the split you would use.
3. Your fine-tuned model scores better on domain perplexity and worse on the downstream task than
   the frozen base model. What are the two most likely explanations, and which measurement
   separates them?
4. A colleague proposes continued pretraining on 3 million tokens of district memos. Give the two
   questions you would ask before agreeing, and say what answer would change your mind.

*The lab for this section &mdash; adapting a small language model to a transportation corpus, with
the prompt and retrieval baselines run first &mdash; is in development. Its model shortlist is
being piloted against the free Colab tier so that every step is runnable without a lab GPU.*

---

Next: the retrieval pipeline this section keeps pointing at, and how to evaluate the retriever on
its own before judging a single answer.
