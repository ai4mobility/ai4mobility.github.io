# 2.4 Building one: a GPT you can read

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 2 &middot; Section 2.4</span>
    <span class="notes-card-session">Session: Sept 17</span>
  </div>
  <p class="notes-card-lede">Section 2.3 showed the mechanism on a trained model's weights. This one writes it out. A complete decoder-only transformer in a single readable file &mdash; Q, K and V as three matrices, the scaled dot product, the causal mask, softmax implemented rather than imported &mdash; trained here on 42,650 vehicle-owner complaint narratives, and checked twice: against counting baselines, and against the same attention head re-derived in plain NumPy.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Interactive companion on this page</h4>
      <ul>
      <li><a href="../_static/companions/GPT_From_Scratch_Companion.html" target="_blank" rel="noopener">A GPT you can read &#8599;</a></li>
      <li><a href="../_static/code/gpt_from_scratch.py" download>gpt_from_scratch.py &#8595;</a></li>
      </ul>
    </div>
    <div>
      <h4>Read it after</h4>
      <ul>
      <li><a href="notes3-attention.html">2.3 Attention: the mechanism</a></li>
      </ul>
    </div>
  </div>
</div>

## What this section covers

- The whole forward pass of a GPT in six lines, and what each one does
- Q, K and V as three learned views of one vector &mdash; not three inputs
- The five lines of `scaled_dot_product_attention`: dot product, scale, mask, softmax, weighted sum
- What the causal mask is worth, measured by removing it
- Why nothing in the model depends on the batch size or the sequence length
- Softmax written out, and the one line in it that exists only to prevent `nan`
- The two checks every result on this page had to pass

## One objective, six lines

A transformer has exactly one training objective: given the words so far, put a probability on
every word that could come next. There is no second one. Everything a language model later does
for you &mdash; classify a complaint by component, pull a failure mode out of a crash narrative,
draft a work-zone memo &mdash; is this objective plus a small head bolted on afterwards.

The label costs nothing, which is the whole reason models of this kind could be scaled. It is
the input shifted one position left, the same self-supervision trick as the sliding window in
word2vec. Our corpus of **4,548,008 word tokens** is therefore 4,548,008 labelled examples that
nobody annotated.

And the model around that objective is small enough to read:

```python
x = tok_emb(idx) + pos_emb(pos)   # what each token is, plus where it sits
for blk in blocks:
    x = x + blk.attn(ln1(x))      # tokens read each other
    x = x + blk.mlp(ln2(x))       # each token, alone, non-linearly
logits = head(ln_f(x))            # D -> V, one score per word
loss   = cross_entropy(logits, y) # a multinomial logit over 6,000 alternatives
```

Read a block as one sentence: *copy the token forward unchanged, and add to it what it learned
by looking at other tokens, and what it worked out on its own.* The `+` is why deep stacks train
at all &mdash; the gradient has a path back to the input through no weight matrix. Normalising
*before* each sublayer rather than after is what removed the learning-rate warmup early
transformers needed.

## The five lines that are the transformer

Everything else in the file is scaffolding around these:

```python
scores  = q @ k.transpose(-2, -1)                   # 1  every query against every key
scores  = scores / math.sqrt(d_head)                # 2  the scale
scores  = scores.masked_fill(~mask, float("-inf"))  # 3  the causal mask
weights = softmax(scores, dim=-1)                   # 4  a probability per earlier token
out     = weights @ v                               # 5  the weighted average of the VALUES
```

**Why divide.** A dot product over `d_head = 32` dimensions has a spread of about &radic;32.
Measured on our model, the raw scores spread **16.01** and the scaled ones **2.83**. Without the
division the largest weight in a row is **0.877** instead of **0.512** &mdash; the row stops being
an average and becomes a lookup, and the gradient through softmax goes flat.

**Why &minus;&infin; and not a large negative number.** `exp(-inf)` is exactly zero, so a
forbidden token receives no weight and no gradient. Without the mask, **79.5%** of a row's weight
would land on tokens the model is supposed to be predicting.

**Why the softmax is written out.** `exp(800)` is `inf` in float32 and `inf/inf` is `nan`, and one
`nan` poisons every weight at the next backward pass. Subtracting the row maximum first is exact,
not an approximation, and it is the most common way a hand-written transformer dies.

## What the mask is worth

The mask is easy to describe and easy to underrate, so we removed it. The same one-layer model,
trained 800 steps, identical except for that one line:

| run | train loss | validation perplexity | what it generates |
|---|---|---|---|
| causal mask on | 4.26 | 66.3 | *the brake pedal is hard brake pedal to slow down even when they couldn't the floor* |
| mask removed | **0.13** | **1.14** | *the brake pedal pedal pedal pedal pedal pedal &hellip;* |

Note which number is *not* the alarm. The unmasked run's **held-out** perplexity is superb too.
The leak is in the architecture, not in the split, so no amount of care about train/test
separation catches it &mdash; a warning worth carrying back to any model you build where a feature
could encode the label. Only generation, where there is no future to read, exposes it. A loss that
drops too fast is a leak, not a breakthrough.

## Why the shapes never pin you down

Students usually picture a network as fixed wiring, which makes it hard to see how the same model
accepts one sentence of 15 tokens and a training batch of 32 &times; 64. The answer is in the
parameter shapes. This model's weights are `6000 x 128`, `64 x 128`, `128 x 128`, `512 x 128`,
`128 x 512` and `128` &mdash; and **not one of them contains B or T**.

`nn.Linear` multiplies the *last* dimension and treats every leading dimension as a batch
dimension, so a `(B, T, D)` tensor is B&middot;T independent vectors of length D. Feeding the MLP
the box and feeding it the flat stack give bit-identical answers (**0.000e+00**, at three
different shapes). The only operation that mixes across tokens is attention, and its `(B, H, T, T)`
matrix is *computed from the input*, never stored as a weight &mdash; which is exactly the
difference from the fixed adjacency matrix you would declare in a spatial model.

One thing does cap the length: `pos_emb` is a table with `block_size` rows, so position 64 has no
vector and `assert T <= self.cfg.block_size` fires. That is why GPT-2 stops at 1,024 tokens, and
why the position schemes in current long-context models have no per-position parameters at all.

## Does it beat the baseline?

A perplexity means nothing on its own. Perplexity is how many equally likely words the model is
effectively choosing between at each position, so a uniform guesser scores the vocabulary size.
Two counting baselines, neither with a single learned parameter, are what the machinery has to
earn its place against:

| model | validation perplexity | learned parameters |
|---|---|---|
| uniform guess | 6,000 | none |
| unigram (word frequency) | 453.2 | none &mdash; counts |
| bigram, add-k smoothed | 94.7 | none &mdash; counts |
| **this transformer** | **42.2** | 1,567,488 |

Counting the previous word alone gets you to 95. The transformer's contribution is the step from
there, bought with 1.5 million parameters and half an hour of CPU. Report the ratio, not the loss:
"still choosing between forty words" is a sentence an agency reviewer can argue with; a
cross-entropy of 3.74 is not.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion &mdash; A GPT you can read</span>
    <a href="../_static/companions/GPT_From_Scratch_Companion.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/GPT_From_Scratch_Companion.html"
          title="A GPT you can read: every step of a decoder-only transformer" loading="lazy"></iframe>
</div>

Nine tabs, every matrix from the trained model. Tab 5 is the one to spend time on: the same
attention matrix with the scale and the mask as two switches you can flip.

:::{admonition} Before you trust this result
:class: warning
**What is the baseline?** The unigram and bigram counters above, computed on the same split, the
same vocabulary and the same `<unk>` handling. A baseline computed any other way is not a baseline.

**How was the data split, and why is that honest?** By whole complaint, never mid-narrative, with
**306** verbatim duplicate narratives removed *before* splitting &mdash; re-filings and dealer form
letters repeat, and leaving them in would make validation measure memorisation. The vocabulary is
built on the training half only, so words the model never saw are honestly `<unk>`: 1.52% of
validation tokens.

**What does it do on the ugly cases?** It has read one inbox. Point it at a maintenance log and
perplexity collapses. At 1,567,488 parameters it is fluent inside a clause and incoherent across a
paragraph. And fluent is not true: nothing in the objective rewards a correct claim, only a likely
word, which is the failure mode to design around before any model output reaches an agency
document.
:::

## Run it yourself

<a href="../_static/code/gpt_from_scratch.py" download>gpt_from_scratch.py</a> is the whole model,
about 470 lines with the comments. It has no dependencies beyond PyTorch and NumPy, and four of
its five modes need no training:

```text
python3 gpt_from_scratch.py --explain    # the real matrices for one sentence
python3 gpt_from_scratch.py --overflow   # softmax nan, and the fix
python3 gpt_from_scratch.py --check      # one attention head, re-derived in NumPy
python3 gpt_from_scratch.py --baselines  # unigram and bigram perplexity
python3 gpt_from_scratch.py --train      # about 29 minutes on a laptop CPU
```

The corpus is the NHTSA complaint file from {doc}`Lab 2 <../module1/lab2_word_embeddings>`
(`nhtsa_adas_complaints.txt.gz`); put it beside the script, or in a `Labs/data/` folder next to
it, and `--train` reproduces the model this page argues from. `--size tiny` trains in a few
minutes if you want to watch the loss move before committing to the full run.

`--check` is worth reading even if you never run it. It takes the trained weights out of the
model and recomputes one attention head with nothing but NumPy &mdash; nine lines of plain
arithmetic &mdash; then asserts the answer matches PyTorch. It passes at **1.9e-07**. Autograd is
convenient, and it is also a place to hide; write this check for your own models.

---

Next: {doc}`notes5-bert` &mdash; four edits that turn this model into a BERT, the two games it is pretrained on, and how a pretrained encoder is adapted to a task.
