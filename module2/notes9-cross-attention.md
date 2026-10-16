# 2.9 Cross-attention: one sequence reads another

<div class="notes-card">
  <div class="notes-card-head">
    <span class="notes-card-eyebrow">Module 2 &middot; Section 2.9</span>
    <span class="notes-card-session">Session: Oct 15</span>
  </div>
  <p class="notes-card-lede">BERT reads text, a ViT reads images, and neither knows the other exists. Cross-attention connects them with one change to attention: the questions come from one sequence, the keys and values from another. This section tests it on real Florida crash narratives and diagrams, where a 224-million-parameter model loses to OCR and a word count, then opens the encoder&ndash;decoder on a traveler alert translated into Spanish.</p>
  <div class="notes-card-cols">
    <div>
      <h4>Interactive companions on this page</h4>
      <ul>
      <li><a href="../_static/companions/Cross_Attention_Companion.html" target="_blank" rel="noopener">Cross-attention at the merge &#8599;</a></li>
      <li><a href="../_static/companions/Cross_Attention_Architecture_Companion.html" target="_blank" rel="noopener">One decoder position, every encoder token &#8599;</a></li>
      </ul>
    </div>
    <div>
      <h4>Notebooks that go with it</h4>
      <ul>
      <li><a href="../module1/lab4_clip_vs_traditional_cv.html">Lab 4 &mdash; CLIP, the late-fusion dual encoder</a></li>
      <li>Cross-attention sanity check &mdash; <em>in development</em></li>
      </ul>
    </div>
  </div>
</div>

## What this section covers

- Early fusion, late fusion and cross-attention: where two inputs meet
- The mechanism: queries from one sequence, keys and values from the other
- Cross-attention with one query is a multinomial logit
- Who asks fixes the output shape, and the four places cross-attention lives
- A zero-shot test on crash narratives and diagrams: what it wins, costs and actually reads
- The encoder&ndash;decoder with every token drawn, and how training reaches the encoder
- Three ways to get the weights, and which fits a mobility project

## Why two encoders are not enough

A Florida long-form crash report holds two records of one event: the officer's narrative and the
officer's diagram. A records reviewer reads them side by side to catch reports where they disagree; a
safety analyst searching three years of reports for left-turners struck by opposing through
traffic needs both at once.

Every encoder so far reads one kind of input. BERT turns the narrative into one vector per WordPiece token
({doc}`2.5 <notes5-bert>`); a ViT turns the diagram, squashed to 384 &times; 384, into 577 vectors, 576
patches plus `[CLS]` ({doc}`2.7 <notes7-vision>`). Each tower's self-attention mixes only its own
tokens. The test data here is 288 de-identified Florida crash narratives paired with the officer's
diagram, released to the class on Canvas (350 reports, 288 with a diagram). If you are enrolled, the
data and the full crash-report material are on Canvas; this page reports aggregate results and token
counts only.

(fusion-vs-cross-attention)=
## Fusion vs cross-attention: where the inputs meet

```{figure} ../_static/figures/XAttn_Fusion_Compare.png
:alt: Three wirings of narrative tokens and diagram patches: one transformer over a joint 679-token sequence; two towers compared by a cosine; a cross-attention block in each of 12 text layers reading the ViT's patches.
:width: 100%

*Fusion* only means combining two inputs; the designs differ in where the inputs meet, and cross-attention is one way to fuse, not a rival to fusion.
```

**Early fusion** glues narrative tokens and diagram patches into one sequence for one transformer:
everything reads everything, both ways. **Late fusion** keeps two towers that never touch and compares
one summary vector from each. That is CLIP ({doc}`1.5 <../module1/notes5-embeddings>`,
{doc}`Lab 4 <../module1/lab4_clip_vs_traditional_cv>`): cheap, because each side is encoded once and
stored, but no word ever meets a patch, so what the narrative says about where a vehicle was must
survive being averaged into one vector. **Cross-attention** keeps the towers apart, but inside every
text layer the words ask the diagram.

| | Early fusion | Late fusion | Cross-attention |
|---|---|---|---|
| Who reads whom | every token &harr; every token | nobody: two summaries meet once | each word &rarr; every patch |
| Word&ndash;patch weights per head, for one 102-token narrative &times; 577 patches | 117,708 (both directions) | 0 | 58,854 |
| Reuse a stored side for a new pair? | no | yes, both sides | the diagram side only |

When a vendor "fuses camera and CAN data", ask where the two streams first exchange information.

## The mechanism: one change from self-attention

Picture an investigator with the narrative in hand and the diagram on the desk: every phrase sends a
question to the drawing. The roles of {doc}`2.3 <notes3-attention>` stay; only their source changes. The
asking word supplies the **query**; the answering patches supply the **keys** (what each patch
advertises) and the **values** (what it hands over if chosen).

$$
\text{CrossAttn}(X, Z) = \text{softmax}\!\left(\frac{(XW_Q)(ZW_K)^\top}{\sqrt{d}}\right) ZW_V
$$

- $X$ &mdash; the narrative's token vectors at this layer: 102 &times; 768 for one example narrative of 102 WordPiece tokens (the median narrative has 176).
- $Z$ &mdash; the diagram's patch vectors from the ViT: 577 &times; 768.
- $W_Q, W_K, W_V$ &mdash; learned, 768 &times; 64 per head, 12 heads per layer.
- $\sqrt{d}$ &mdash; $\sqrt{64} = 8$, which keeps the softmax from saturating.

**In words:** each word turns itself into a question, scores every patch, and takes home the weighted
average of what the patches hand over. Write $X$ where $Z$ is and you are back to self-attention.

For that narrative the table is a rectangle: 102 &times; 577 = 58,854 weights per head per layer,
8,474,976 across BLIP's 144 cross-attention heads for one pair; 28.4 M of BLIP's 224 M parameters are cross-attention. Each row
spends 100% of its weight even when nothing in the diagram answers the question.

:::{admonition} Going deeper &mdash; the gate, the masks, and why K and V share a source
:class: dropdown
Flamingo adds cross-attention to a frozen language model as
$x \leftarrow x + \tanh(\alpha)\cdot\text{CrossAttn}(x, Z)$ with $\alpha$ starting at 0, so at step zero
the model *is* the original language model. No causal mask is needed, since the whole diagram exists
before any word reads it. K and V share a source because both describe the answerer: where to look, and
what comes back. Bishop &amp; Bishop (2024), &sect;12.3.4 and Fig. 12.19; Alayrac et al. (2022).
:::

## Cross-attention at the merge

A vehicle on an on-ramp needs two answers: *who will I follow?* and *who has to let me in?* In the
companion those are two learned query vectors of 16 numbers; the answerers are the surrounding vehicles
(distance ahead, lane, speed) plus a map token carrying the posted speed. The scenes are synthetic, the
labels come from a written rule, and the model never saw where to look. Two questions give two answers
whether the scene holds three vehicles or thirty: a fixed-size output from an input of any size.

Spend your time in three places. In **tab 2**, press *Cut-in in progress*. Once the cutting-in vehicle
is across, the rule says 55 mph and the model answers 50.0 mph, splitting 0.69 and 0.30 between new and
old leader: soft attention averages close competitors into a speed nobody is driving. **Tab 3** is the
bridge to discrete choice: tastes in the query, each alternative's attributes in the keys, and
$q \cdot k$ is the systematic utility, the softmax is the multinomial logit, $1/\sqrt{d}$ plays the scale $\mu$. But tastes are computed ($q = W_Q x$),
closer to a mixed logit; attention returns the expected outcome, never a choice; and *Add a "blue bus"*
shows IIA comes along, so a vehicle seen by two overlapping cameras gets about twice the say. **Tab 5:**
remove the map token on the 5,670 test scenes with no leader within 100 m and the follow-speed error
goes from 1.12 to 19.0 mph. A sum-to-one layer cannot say "nothing here".

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion &mdash; Cross-attention at the merge</span>
    <a href="../_static/companions/Cross_Attention_Companion.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/Cross_Attention_Companion.html"
          title="Cross-attention at the merge: one set of tokens asks, another set answers" loading="lazy"></iframe>
</div>

:::{admonition} Before you trust this result
:class: warning
**What is the baseline?** The posted speed, no model (follow-speed error 14.86 mph), and the fair one:
the same token encoder with equal weights (6.36 mph). Cross-attention reaches 1.43 mph.

**How was the data split, and why is that honest?** The 20,000 test scenes are fresh from the generator:
honest about whether the mechanism can learn a selection rule from answers alone, silent about real
ramps. The rule itself scores zero error: if you know the rule, write it down.

**What does it do on the ugly cases?** Fed 24 vehicles after training on 3 to 8, it puts 0.43 of its
weight on the right one, down from 0.84 at 8 vehicles, silently. With one of four seeds, the follow
question looked at the right token in only 16.1% of scenes: report the spread.
:::

## Who asks fixes the shape

```{figure} ../_static/figures/XAttn_Shapes.png
:alt: A square table over one narrative's 102 tokens and 577 patches, split into words-ask-patches (102 by 577, BLIP's direction), patches-ask-words (577 by 102) and the ViT's own 577-by-577 block.
:width: 100%

Rows ask and columns answer, so the direction is a design decision you make from the output you need.
```

You get one output per row. Let the **words ask** (102 &times; 577) to score the pair; let the
**patches ask** (577 &times; 102) to point at the place a phrase describes. Glue all 679 tokens into one
sequence and the off-diagonal blocks of plain self-attention *are* cross-attention, computed with the
same $W_Q, W_K, W_V$ as the rest, at 461,041 weights per head for the whole square: single-stream models such as ViLT, and LLaVA-style models under a causal mask, fuse this way.

```{figure} ../_static/figures/XAttn_Families.png
:alt: Four panels: dual encoder with a cosine; fusion encoder with words reading patches in 12 layers; decoder with gated cross-attention to video and CAN tokens; learned queries reading camera features.
:width: 100%

Same mechanism, four wirings: ask of any multimodal model who asks, who answers, and how many questions there are.
```

A **dual encoder** (CLIP, BLIP's ITC head) has no cross-attention. A **fusion encoder** (ALBEF, BLIP's
ITM head) lets the words ask the image in every layer: the model tested next. A **decoder** asks with the
token being written: the original Transformer, Flamingo, the course's dashcam-and-CAN crash-warning
model. In the fourth family the questions are **learned**: DETR's 100 object queries, BLIP-2's 32,
BEVFormer's one per bird's-eye-view cell asking the six cameras what is above it.

(cross-attention-test)=
## The crash-report test: find each narrative's diagram

The model is **BLIP base** (Li et al., 2022): a ViT-B/16 and a BERT-base with cross-attention in all 12
text layers, 224 M parameters, fine-tuned on COCO photos and captions, used as downloaded; all 288 pairs
are test pairs. It scores a pair by late fusion of two summary vectors (ITC) or by cross-attention
through 12 layers (ITM). Each narrative picks its own diagram from a pool: its own plus 15 random
others, or plus up to 7 from the same corridor, which share street names.

| Top-1 (288 narratives; 287 have a same-corridor pool) | random pool of 16 | same corridor, up to 8 |
|---|---|---|
| Chance | 6.25% | 13.2% |
| CLIP ViT-B/32, late fusion (first 77 tokens) | 11% | 17% |
| BLIP late fusion (ITC) | 14% | 17% |
| **BLIP cross-attention (ITM)** | **30%** | **25%** |
| OCR the diagram (Tesseract) + shared words | 68% | 42% |

Reading patches word by word beats comparing summaries, 30% against 14%. But OCR the diagram and count
the words it shares with the narrative, with no neural network doing the matching, and you win both
columns. Nor are the
probabilities calibrated: the median match probability is 3.4% for a narrative and its own diagram,
0.15% for an unrelated one.

**What it costs.** Late fusion encodes each diagram and narrative once, 576 passes, and all 82,944 pair
scores are one matrix multiply: about 4 minutes on two CPU threads. Cross-attention needs a pass per
pair, 0.38 s each, about 8.7 hours, growing with the *product* of the collections. BLIP's own fix is to
retrieve with late fusion and re-rank the short list. Here late fusion's top 16 out of 288 holds the
right diagram only 13% of the time, and re-ranking cannot recover what retrieval never found.

**Arrows or labels?** Score each narrative against its own diagram, original against edited, then
against an *unrelated* diagram: a preference that survives there comes from the text alone.

| Edit to the narrative | original wins, own diagram | unrelated diagram |
|---|---|---|
| Swap north &harr; south, east &harr; west | 50% of 286 | 52% |
| Swap vehicle 1 &harr; vehicle 2 | 62% of 265 | 59% |
| Replace street names with "the road" | 82% of 282 | 53% |

Contradict every arrow and the model does not notice. The vehicle swap's preference lives in the text
(96% of these narratives name vehicle 1 first). Only erasing street names moves the score, and only
against the right diagram: the model matched by reading **street labels**, the OCR baseline's signal,
not who went which way. It shows inside too. In 275 of 288 pairs Tesseract finds narrative words printed
on the diagram, 4,188 occurrences. Divide a word's weight on the patches showing it by those patches'
share of the picture (the *lift*): 17 of 144 heads exceed 3&times;, the best, layer 4 head 3, reaches
80.3&times;, and the same patches draw 2.8&times; from the narrative's other words. Averaged over all heads
the lift is 2.8&times;: the specialist vanishes in the average. An attention map is evidence to test with
an intervention, like the edits, not an explanation.

## Where it breaks on crash reports

**The squash:** at 384 pixels, printed words shrink from 11 to 5.9 px (median across the release); long
street names in clean type survive, hand-drawn arrows do not. **The domain:** photos and one-sentence
captions against CAD drawings, a north symbol not always up, and 139-word narratives (median).
**Length:** 176 WordPiece tokens (median), and one narrative runs past BERT's 512; CLIP stops at 77, which only 8 of 350
narratives fit. **Scale:** millions of cross-attention weights against 288 pairs. **The easy input
wins:** here street names; in the course's dashcam-and-CAN model, trained on simulated clips, CAN alone
wrote 83.7% of reports exactly right against 87.0% with both sensors. Tiling and chunking fix the first and third; geometry needs hard negatives that differ only in
direction.

| Cross-attention in mobility | Who asks &rarr; who answers | Classical baseline |
|---|---|---|
| ADAS perception (*extraction*) | bird's-eye-view cells &rarr; six cameras (BEVFormer) | inverse perspective mapping, lidar grid |
| Motion prediction (*prediction*) | each road user &rarr; lane centerlines (MTR, Wayformer) | constant velocity, lane following |
| Traffic flow (*prediction*) | 15-, 30-, 60-minute horizons &rarr; past detector window | persistence, historical average |
| Traffic operations (*extraction*) | an operator's question &rarr; a CCTV frame | fixed video analytics, detector alarms |

:::{admonition} Fit card &mdash; Cross-attention fusion
:class: tip
**Idea in one sentence.** Each token of one input builds a query and reads all the tokens of another input.

**Why it works.** Matching happens token by token inside the layers, before anything is summarised, so the token that matters can change with every scene.

**Fits these tasks.** Pair verdicts such as narrative&ndash;diagram consistency (once trained on hard negatives), questions about a CCTV frame, camera&ndash;CAN fusion, bird's-eye-view grids from six cameras (*judgment*, *classification*, *extraction*, *prediction*).

**Needs this data.** Many time-synchronised paired examples of both sources, and pretrained towers on both sides.

**Breaks when.** Pairs are few, inputs are out of domain, one input carries an easy shortcut, or nothing relevant is present and no token means "nothing here".

**Keep the classical method when.** A cheap signal settles it (OCR plus a string match), you must score millions of pairs, or the selection rule is known and stable, as in ACC target selection or gap acceptance.
:::

:::{admonition} Before you trust this result
:class: warning
**What is the baseline?** Chance and an OCR word match, which no network beat; BLIP's own late fusion
and CLIP isolate what the cross-attention layers add.

**How was the data split, and why is that honest?** Zero-shot: nothing was trained on crash reports, so
all 288 pairs are test pairs, and the label head was chosen on all of them, not on one example.

**What does it do on the ugly cases?** In same-corridor pools cross-attention falls from 30% to 25%, and
the edits show it ignores directions entirely. Hand-drawn and aerial-photo diagrams were not split out.
:::

(encoder-decoder)=
## The encoder&ndash;decoder, with every token drawn

Cross-attention was invented for the third family, the encoder&ndash;decoder of Bishop's Fig. 12.20.
Here every token of that figure is drawn, on a public English&rarr;Spanish translator built like it
(MarianMT, `Helsinki-NLP/opus-mt-en-es`: 6 + 6 layers, 8 heads, 512 numbers per vector). Its weights are
used as downloaded; decoding is set to greedy, one most-likely token per pass, so each pass can be drawn
(the checkpoint's default four-candidate search writes *Trabajo de carretera*).

```{figure} ../_static/figures/EncDec_Unpacked.png
:alt: The encoder turns the nine tokens of "Road work ahead, right lane closed." into Z, nine vectors of 512 numbers; every decoder layer takes keys and values from Z, and each new Spanish token is fed back.
:width: 100%

Z is nine vectors, one per English token, not one summary, and every decoder layer reads all nine.
```

$Z$ is 9 &times; 512 and grows with the alert; one vector per sentence was the bottleneck of the older
recurrent translators. The **same $Z$ enters all six decoder layers**, and the output is the input
shifted by one: the position holding &lang;start&rang; predicts "Trabajo". In each decoder layer, masked
self-attention lets a Spanish position read itself and earlier ones only (10 &times; 10); **cross-attention** takes
queries from the Spanish positions $H$ and keys and values from $Z$ &mdash; the equation above with $H$
for $X$ &mdash; with no mask (10 &times; 9); then an MLP. One real row, layer 5, head 8, the position
about to write "derecho": $q \cdot k$ for "right" is 50.37, divided by 8 it is 6.30, and the softmax puts
0.977 on "right". All four cross-attention matrices, $W_Q$, $W_K$, $W_V$ and the output matrix $W_O$,
**belong to the decoder layer**: 1,050,624 per layer,
6.3 M of the model's 77.9 M. The encoder owns none.

```{figure} ../_static/figures/EncDec_Who_Reads_2.png
:alt: Arcs and a 10-by-9 table of real layer-5 weights from each Spanish token to the nine English tokens, with gold boxes on the word a translator would link.
:width: 100%

Each Spanish word's heaviest English token is the one a translator would link it to, six of six, and the arcs cross where the word order flips.
```

"derecho" takes 0.58 from "right" and "carril" 0.47 from "lane"; "Trabajo" puts 0.32 on "work", then
"carretera" 0.52 on "Road". A word-one-to-word-one rule fails on the first swap, so every output
position needs its own query. Spare weight parks on the end mark, 0.09 to 0.32 of each word row, like
`[SEP]` in BERT. The layer drawn was chosen on 24 *other* alerts (98 hand links): layer 5 puts its
largest weight on the linked word 89% of the time, layers 1 and 2 0% and 1%.

Generating, the encoder runs **once** and the decoder once per Spanish token, 10 passes re-reading the
same $Z$; training, with the correct Spanish known, all 10 run in **one masked pass**. The companion
animates one head turning a short incident description into a lane-closure message, with hand-chosen
vectors and a scripted output, so its numbers illustrate rather than measure. Step through its six stages, then select the &lsaquo;start&rsaquo; and *Right*
positions and compare how two queries spread over the same encoder memory.

<div class="companion-embed">
  <div class="companion-embed-bar">
    <span>Interactive companion &mdash; One decoder position, every encoder token</span>
    <a href="../_static/companions/Cross_Attention_Architecture_Companion.html" target="_blank" rel="noopener">Open full screen &#8599;</a>
  </div>
  <iframe src="../_static/companions/Cross_Attention_Architecture_Companion.html"
          title="One decoder position, every encoder token" loading="lazy"></iframe>
</div>

### Training, and the three recipes

```{figure} ../_static/figures/EncDec_Training_Signal.png
:alt: The loss flows back through the decoder and reaches Z only through W_K and W_V; bars show the gradient reaching Z from each decoder layer; three freezing regimes list their trainable counts.
:width: 100%

Z is read only by $W_K$ and $W_V$, so they are the only road by which the encoder learns it was wrong.
```

Take one SGD step (learning rate 0.001). **Train everything:** 77.4 M weights move and $Z$ changes by up
to 0.054, on entries with a spread of about 0.25. **Freeze the encoder:** 25.2 M trainable, $Z$
identical, yet $W_Q$, $W_K$, $W_V$ still learn, as decoder weights.
**Cross-attention only:** 6.3 M. The trap: Marian's encoder and decoder share one word-embedding table, so
freezing only the six encoder layers leaves 58.5 M trainable and $Z$ still moves, by up to 0.014.

Three recipes supply the weights. **From scratch:** the original Transformer (4.5 million sentence
pairs), Whisper (680,000 hours of audio), this translator. **Pretrain the whole model**, then fine-tune:
T5, BART; t5-small ships with its 6.29 M cross-attention weights. **Warm-start from parts:** join two
BERT-base models and 28.4 M new cross-attention weights start random. For Spanish DMS and 511 alerts,
fine-tune a working translator on the agency's approved messages; for crash narratives into coded
fields, start from T5 or BART; for dashcam hazard descriptions, freeze a vision&ndash;language model's
two big parts and tune its bridge.

:::{admonition} Going deeper &mdash; freeze the encoder, or train everything?
:class: dropdown
The studies disagree, which is the lesson. T5: all parameters 26.98 BLEU, gradual unfreezing 26.71.
BERT2BERT: a BERT encoder over a random decoder, 26.0 to 30.1. Imamura &amp; Sumita: a BERT encoder and a
new decoder trained at once reached 0.1&ndash;0.4 BLEU; freezing BERT first gave 28.9 against 27.22 for a
plain Transformer. **Rule of thumb:** new, random parts on a pretrained encoder: freeze it first,
unfreeze later, let validation decide; a model pretrained as a whole: fine-tune everything. Raffel et al.
(2020); Rothe et al. (2020); Imamura &amp; Sumita (2019).
:::

### Where it breaks: it read the right word

```{figure} ../_static/figures/EncDec_Breaks.png
:alt: Three mistranslated alerts (hombro, discapacitado, Acelera), each with the attention row that wrote the wrong word.
:width: 100%

In all three failures the attention looked right and the output was still wrong.
```

*Hombro* is a person's shoulder, written from a row with 0.76 on "shoulder": the decoder read the right
word and chose the everyday sense, as with *discapacitado* (0.62 on "Disabled"). Both survive the
model's default four-candidate search. The dangerous one is *Acelera*, speed up, for "Crash ahead":
greedy decoding took "A" at 0.17 over "Cho" at 0.11 and never revisited it; the default search writes
"Choque adelante". Three alerts read by hand are not an error rate, but they show where to look.

:::{admonition} Fit card &mdash; Encoder&ndash;decoder transformer
:class: tip
**Idea in one sentence.** An encoder reads the whole input once; a decoder writes the output one token per pass, reading the encoder's tokens in every layer.

**Why it works.** Each output position picks its own input tokens, so order and length can change between input and output.

**Fits these tasks.** One sequence into another: translating alerts, crash narrative &rarr; coded fields, radio audio &rarr; text (*generation*, *extraction*).

**Needs this data.** Paired input&ndash;output sequences: many from scratch, far fewer from a model pretrained as a whole.

**Breaks when.** Domain words have everyday senses, safety phrases are rare in training, or greedy decoding commits to a bad first token.

**Keep the classical method when.** Messages come from a fixed approved list: a reviewed table of translations is exact, auditable and free.
:::

:::{admonition} Before you trust this result
:class: warning
**What is the baseline?** For the text, the checkpoint's own four-candidate search and, for sign
messages, a reviewed lookup table; for the weights, the layer rule (89% of links at layer 5, 0% at 1).

**How was the data split, and why is that honest?** Nothing was trained. The drawn layer was picked on 24
other alerts, so the picture was not chosen for looking good. The one-step demo shows *what* is updated,
not which regime is better.

**What does it do on the ugly cases?** All three failures had attention on the right word. Audit
translated alerts by their text &mdash; a required-term glossary, back-translation, review of the
approved set &mdash; not by their attention maps.
:::

## Check yourself

1. A state DOT wants every new crash report flagged when the narrative's directions disagree with the
   diagram. Is BLIP's cross-attention head, used as here, fit for that? What would you change, and which
   test on this page would show it worked?
2. An ACC system picks its target vehicle with a hand-written rule that has worked for a decade. A vendor
   proposes a cross-attention selector. What would you ask for, and which ugly case would you test first?
3. A vendor's alert translator shows every Spanish word attending to the right English word, as evidence
   its messages are safe for a dynamic message sign. What would you audit instead, and when would you keep
   a reviewed lookup table?

---

Next: {doc}`notes10-detr` &mdash; the same cross-attention with the questions learned instead of written: DETR's object queries asking a camera frame what is there.
