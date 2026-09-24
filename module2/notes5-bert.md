# 2.5 BERT: pretrain on text nobody labelled, then adapt

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 2 &middot; Section 2.5</span>
    <span class="notes-card-session">Session: Sept 24</span>
  </div>
  <p class="notes-card-lede">Section 2.4 built a GPT. Four edits turn it into a BERT: every token may read both sides, a third embedding table marks which span a token is in, the training label becomes "the words we hid" plus "did span B follow span A", and two new heads sit on top. This section trains that model on the same complaint narratives, plays both pretraining games with it, and then attaches four different heads to the real <code>bert-base-uncased</code> &mdash; one for each kind of transportation text task.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Interactive companion on this page</h4>
      <ul>
      <li><a href="../_static/companions/BERT_Training_Companion.html" target="_blank" rel="noopener">How BERT learns &#8599;</a></li>
      <li><a href="../_static/code/bert_from_scratch.py" download>bert_from_scratch.py &#8595;</a></li>
      </ul>
    </div>
    <div>
      <h4>Read it after</h4>
      <ul>
      <li><a href="notes4-gpt.html">2.4 Building one: a GPT you can read</a></li>
      <li><a href="notes2-contextual.html">2.2 From static to contextual vectors</a></li>
      </ul>
    </div>
  </div>
</div>

## What this section covers

- The four edits that separate a BERT from the GPT you already read
- The model: three embedding tables added together, a stack of blocks, one vector per token
- Pretraining game one, masked words: the 15% and 80/10/10 rule, and what reading both sides is worth
- Pretraining game two, next-sentence prediction: what it actually learns, and what it costs the first game
- The recipe, and why scale &mdash; not the recipe &mdash; is what transfers
- The four ways to attach a head: classify a text, compare two, extract a span, tag every word
- Frozen, fine-tuned, or pretrained further on your own text

## Four edits from a GPT

<a href="../_static/code/bert_from_scratch.py" download>bert_from_scratch.py</a> is
`gpt_from_scratch.py` with four changes, and its header lists them line by line. The attention
function, the block, the softmax and the training loop are untouched.

| | GPT (2.4) | BERT (this section) |
|---|---|---|
| **1 · who may read whom** | each token reads itself and the tokens before it | every real token reads every other real token; only `[PAD]` is masked |
| **2 · the starting vector** | token table + position table | token + position + **segment** table |
| **3 · the training label** | the next word, at every position | about 15% of the words, hidden; and whether span B really followed span A |
| **4 · the heads** | one: score the next word | two: score every hidden word; IsNext / NotNext from the `[CLS]` slot |

Edit 1 is the *B* in the name, for *bidirectional*, and it forces the other three. With the whole
sentence visible, "predict the next word" is no longer a task &mdash; the next word is sitting in
the input, which is exactly the leak you measured in 2.4 when the causal mask was removed. So BERT
needs different training games.

The starting vector for slot *i* is the sum of three lookups:

$$\mathbf{x}_i = E_{\text{tok}}[w_i] + E_{\text{seg}}[s_i] + E_{\text{pos}}[i]$$

*what* the token is, *which span* it belongs to, and *where* it sits. The segment table has two
rows and exists so that one input can carry two passages, packed as
`[CLS] span A [SEP] span B [SEP]`. The `[CLS]` slot is a seat reserved for a summary of the whole
input; it has no meaning of its own until a loss is attached to it.

## Game one: hide a word, guess it from both sides

Choose 15% of the real word slots. Replace 80% of those with `[MASK]`, 10% with a random word, and
leave 10% alone; then ask the model for the original word at every chosen slot:

$$\mathcal{L}_{\text{MLM}} = -\sum_{i \in M} \log P\left(x_i \mid x_{\setminus M}\right)$$

$M$ is the set of chosen slots and $x_{\setminus M}$ is everything left showing, on both sides. The
softmax behind $P$ is a multinomial logit with one alternative per vocabulary word. *In words:* make
the hidden word probable using only its neighbours. There is no way to win without reading them,
and attention is the only way to read them, so the game builds context into every vector as a side
effect.

Measured over 200 training batches, the rule chose **15.0%** of real slots and split them
**80.1 / 9.8 / 10.2**. The random and unchanged slots exist because `[MASK]` never appears when the
model is used: if every chosen word were `[MASK]`, the model could trust every visible word and
build good vectors only at the blanks. The cost is that each step grades about **239** words, where a
GPT step on the same batch shape grades **2,048**.

Does reading both sides help? We hid one word at a time, 4,000 times, in 406 complaints that neither
this model nor 2.4's GPT ever trained on:

| method | first guess correct |
|---|---|
| most frequent word (counting) | 8.8% |
| most frequent word after the left neighbour (counting) | 22.6% |
| **most frequent word between the two neighbours (counting, no learned parameters)** | **40.5%** |
| 2.4's GPT, left side only | 31.2% |
| our BERT, right side cut off | 21.1% |
| **our BERT, both sides** | **33.0%** |

Both halves of that table matter. The same weights go from 21.1% to 33.0% when the right side is
shown &mdash; that is what bidirectional buys. And a count table beats every network on the job the
networks were trained for. Filling a blank is the *game*, not the goal: a count table cannot hand
you a vector to classify or search with. Whether the vectors are worth anything is a separate
question, answered below.

## Game two: did span B follow span A?

Half the time B is the text that really followed A in the same complaint; half the time it comes
from a random other complaint. A two-way head reads the `[CLS]` vector, and the paper simply adds the
two losses: $\mathcal{L} = \mathcal{L}_{\text{MLM}} + \lambda\,\mathcal{L}_{\text{NSP}}$ with
$\lambda = 1$.

Our model reached **78.0%** on held-out pairs. Then we tested it on pairs it was never trained on.
When B was the same complaint's two spans in the **wrong order**, it still said "IsNext"
**64.4%** of the time. When B came from the **most similar other complaint**, **70.4%**. It had
learned *same topic?*, not *does this follow?* &mdash; the diagnosis ALBERT (Lan et al., 2020) made
of NSP at full scale.

The second game also cost the first. With $\lambda = 1$ the model finished at **15.2%** masked-word
accuracy, against **35.2%** for the same network trained on masked words alone. At the end of
training the NSP loss's gradient was as large as the MLM loss's (norms 2.11 and 1.76), and both
share one clipping budget of 1.0. With $\lambda = 0.1$ the masked-word curve tracked the MLM-only run
and NSP was learned about as well. That is our 1.6-million-parameter model's result, not a law about
BERT &mdash; the original paper found removing NSP hurt, RoBERTa found it matched or slightly helped
&mdash; but the lesson travels: when one network trains on two objectives, weight them deliberately
and plot each loss separately.

## The recipe, and what scale buys

The method is the 2.4 training loop with two losses: AdamW, warm-up then decay, gradient clipping,
dropout 0.1, GELU. The difference is scale. Published bert-base read 3.3 billion words for a million
steps of 128,000 tokens on 16 TPU chips over four days. Ours read 3.9 million words for 10,000 steps
of 2,048 slots in 39 minutes on two CPU threads: between 63 and 6,250 times smaller on every measure
the companion plots.

The test of whether our pretraining produced anything worth transferring: route a complaint to one
of six NHTSA components with 60, 300 or 2,940 labelled examples.

| labelled complaints | 60 | 300 | 2,940 |
|---|---|---|---|
| TF-IDF + logistic regression | **68.2%** | **84.6%** | **91.1%** |
| bert-base, frozen (never fine-tuned) | 52.3% | 70.7% | 82.7% |
| our model, pretrained, fine-tuned | 48.6% | 75.1% | 87.5% |
| our model, **random start**, fine-tuned | 55.7% | 77.5% | 88.5% |
| our model, pretrained, frozen | 40.9% | 55.6% | 66.5% |

*Means of three draws of the labelled set.*

Our 39 minutes of pretraining did not transfer: fine-tuning from it was no better than starting
from random weights, at any label budget. The real bert-base, used frozen, beats ours frozen by
12 to 16 points &mdash; what transfers is learned from billions of words. And counting words wins
every column, because the component names are sitting in the complaints. **Download a pretrained
checkpoint; do not pretrain your own on an agency's worth of text.**

## Four ways to attach a head

The paper's Figure 4 reduces every downstream task to two decisions: how to pack the input, and
which output slots a tiny new head reads. Everything else is the pretrained encoder, fine-tuned end
to end. Here are all four, each on real NHTSA text with `bert-base-uncased`:

| template | packed input | head reads | our task | result |
|---|---|---|---|---|
| **A** classify one text | `[CLS] text [SEP]` | `[CLS]` | complaint → one of six components | 93.0% (TF-IDF 91.4%) |
| **B** compare two texts | `[CLS] A [SEP] B [SEP]` | `[CLS]` | do two complaints concern the same component? | 78.8% |
| **C** extract a span | `[CLS] question [SEP] text [SEP]` | every token: start and end scores | "How fast was the vehicle going?" | 100% with units present |
| **D** tag every word | `[CLS] text [SEP]` | every token | mark driver-assistance feature names | 96.3% of generic names |

The heads are tiny &mdash; 1,538 parameters for templates B and C, 2,307 for D &mdash; and the
column that matters is not the last one. Each template came with a control, and each control says
the same thing:

- **A.** Delete every word of the six label names from the complaints and fine-tuned BERT falls to
  86.2%, below TF-IDF's 87.0% (the Sept 17 result in {doc}`2.2 <notes2-contextual>`).
- **B.** Classifying each complaint alone with TF-IDF and comparing the two labels scores **92.2%**,
  well above the fine-tuned pair model. It had the richer label: a component, not just "same or
  not". When you already hold the richer label, use it.
- **C.** The speed labels came from a rule, "a number followed by *mph*". Delete the word *mph* and
  the fine-tuned model answers "no answer" on **every** test narrative it had just solved perfectly.
  A naive first-number rule scores 58.2% on the same control.
- **D.** Trained on generic names only, the tagger found **0 of 132** mentions of brand names it was
  never shown &mdash; Autopilot, EyeSight, full self driving. It did find unlisted plurals and
  shortenings, because those share words with its training labels.

With fine-tuning, **your labels are the specification**. The model learns exactly what the labelling
rule marked, so if you need it to generalise beyond that rule, the rule has to be broader than what
you want the model to learn.

## Frozen, fine-tuned, or pretrained further

Frozen, the backbone is a fixed feature extractor and only the head trains. Fine-tuned, every weight
moves a little (the paper's range: learning rate 2e-5 to 5e-5, 2 to 4 epochs). On the six-component
task a frozen bert-base reached 80.6% and a fine-tuned one 93.0%; the frozen `[CLS]` vector alone
managed 66.8%, because pretraining only ever asked it about next-sentence prediction. **Frozen, average
the token vectors; fine-tuned, use `[CLS]`.**

The third depth is *domain-adaptive pretraining* (Gururangan et al., 2020): keep playing the
masked-word game on your own unlabelled text before fine-tuning. Three hundred steps on the complaint
corpus (614,400 tokens, 39 minutes) cut perplexity on held-out complaints from 15.5 to 9.7, and moved
WikiText's top-1 from 63.2% to 61.4% &mdash; no broad forgetting yet, but the ordinary-English guesses
are already shifting. It also made the model *worse* on airbag complaints, which the adaptation text
does not contain. The model adapts to the text you give it, including its gaps.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion &mdash; How BERT learns</span>
    <a href="../_static/companions/BERT_Training_Companion.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/BERT_Training_Companion.html"
          title="How BERT learns: pretrain on text nobody labelled, then adapt it" loading="lazy"></iframe>
</div>

Nine tabs. Tab 2 runs the trained model in your browser: hide any word in a held-out complaint, then
cut off the right side and watch the guesses get worse. Tab 5 holds all four heads, each with its
control, and tab 7 carries the same two games over to detectors, trajectories and signal logs.

:::{admonition} Before you trust this result
:class: warning
**What is the baseline?** Counting, every time: the two-neighbour count table for masked words,
TF-IDF + logistic regression for classification, the labelling rule itself for spans and tags. Each
is computed on the same split as the model it is compared with.

**How was the data split, and why is that honest?** By whole complaint, with duplicates removed
before splitting. The 1,388 narratives that also appear in the six-component set were removed from
pretraining, so no fine-tuning test complaint was seen even unlabelled. Pairs for template B were
built only inside their own split.

**What does it do on the ugly cases?** The controls above are the ugly cases: label words deleted,
units deleted, names the labels never covered, a corpus with no airbag complaints. On each one the
model does what its training data told it and nothing more. Build that control before you report
the headline number.
:::

## Run it yourself

<a href="../_static/code/bert_from_scratch.py" download>bert_from_scratch.py</a> needs only PyTorch
and NumPy and reads the same complaint file as 2.4 (`nhtsa_adas_complaints.txt.gz`, from
{doc}`Lab 2 <../module1/lab2_word_embeddings>`):

```text
python3 bert_from_scratch.py --train              # MLM + NSP, about 40 minutes on a laptop CPU
python3 bert_from_scratch.py --train --no-nsp     # masked words only
python3 bert_from_scratch.py --train --nsp-weight 0.1
python3 bert_from_scratch.py --fill "the brake pedal went to the [MASK] and the car would not stop" --no-nsp
```

If `nhtsa_component_complaints.jsonl.gz` is not beside the script, the overlap with the
six-component set is not removed, and your numbers will differ slightly from the ones above.
`--max-seconds` pauses a run and saves everything needed to resume it, which lets you train in
short sessions.

---

Next: {doc}`notes6-architecture` &mdash; the same blocks pointed at detector series, trajectories and networks instead of words.
