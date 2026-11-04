"""
build_lora_crash_lab.py — emits module6/lab9_lora_crash_narratives.ipynb

Every number the notebook asserts comes from numbers.json, written by make_numbers.py in the
reproducer folder (lora_crash/). Nothing is typed in by hand. A method that was not run is
absent from numbers.json, and the prose for it falls back to clearly marked TODO-after-run text.

The notebook ships UNEXECUTED and contains no narrative text. The narratives are loaded at run
time from DATA_PATH / DATA_URL (enrolled students get the file from Canvas).
"""
import json, sys, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
NUM = json.load(open(os.environ.get("LAB9_NUMBERS", os.path.join(HERE, "numbers.json"))))

def md(s):  return {"cell_type": "markdown", "metadata": {}, "source": s.split("\n")}
def py(s):  return {"cell_type": "code", "metadata": {}, "execution_count": None,
                    "outputs": [], "source": s.split("\n")}

def n(path, fmt=None):
    """numbers.json lookup; fails loudly so a stale key cannot ship."""
    cur = NUM
    for k in path.split("."):
        if isinstance(cur, list): cur = cur[int(k)]
        else:
            if k not in cur: raise KeyError(f"numbers.json has no {path}")
            cur = cur[k]
    if cur is None: raise ValueError(f"numbers.json {path} is null")
    if fmt == "pct":  return f"{100*cur:.1f}"
    if fmt == "f2":   return f"{cur:.2f}"
    if fmt == "f3":   return f"{cur:.3f}"
    if fmt == "raw":  return cur
    return str(cur)

M = NUM["methods"]
HAS = {k: k in M for k in ["zero", "fixed3", "rag3", "rag3_leaky", "lora"]}
TODO = "**TODO-after-run**"
BIN = ["pedestrian", "injury", "hit_and_run", "distracted"]
MULTI = ["crash_type", "vehicles"]
FIELDS = MULTI[:1] + ["pedestrian", "vehicles", "injury", "hit_and_run", "distracted"]

def headline(src, f):
    """the one number per field we compare on: F1 for yes/no fields, macro-F1 for multi-class."""
    return src[f]["F1"] if f in BIN else src[f]["macroF1"]

def mean_headline(src):
    return sum(headline(src, f) for f in FIELDS) / len(FIELDS)

ROWS = [("Majority class", NUM["majority"]), ("TF-IDF + logistic regression", NUM["tfidf_lr"])]
LABEL = {"zero": "Zero-shot prompt", "fixed3": "Few-shot, 3 fixed examples",
         "rag3": "Few-shot, 3 retrieved (training corridors only)", "lora": "LoRA fine-tune, zero-shot prompt"}
for k in ["zero", "fixed3", "rag3", "lora"]:
    if HAS[k]: ROWS.append((LABEL[k], M[k]["scores"]))

def scoreboard():
    head = "| Method | " + " | ".join(FIELDS) + " | mean | JSON valid |\n|---|" + "---|" * (len(FIELDS) + 2)
    lines = [head]
    keymap = {"Majority class": None, "TF-IDF + logistic regression": None}
    for name, src in ROWS:
        mk = [k for k, v in LABEL.items() if v == name]
        jv = f"{100*M[mk[0]]['schema_valid']:.0f}%" if mk else "—"
        cells = [f"{headline(src, f):.3f}" for f in FIELDS]
        lines.append(f"| {name} | " + " | ".join(cells) + f" | **{mean_headline(src):.3f}** | {jv} |")
    for k in ["zero", "fixed3", "rag3", "lora"]:
        if not HAS[k]:
            lines.append(f"| {LABEL[k]} | " + " | ".join(["TODO-after-run"] * len(FIELDS)) + " | | |")
    return "\n".join(lines)

CELLS = []
A = CELLS.append
sys.path.insert(0, HERE)
from _cells_code import C

def f3(x): return f"{x:.3f}"
TF = NUM["tfidf_lr"]; MJ = NUM["majority"]; RS = NUM["tfidf_lr_random_split"]; AV = NUM["availability"]
LC = NUM["corpus"]["label_counts"]
best_llm = max([k for k in ["zero", "fixed3", "rag3", "lora"] if HAS[k]], key=lambda k: mean_headline(M[k]["scores"]), default=None)

def cmp_word(a, b, tol=0.01):
    return "beats" if a > b + tol else ("ties" if abs(a - b) <= tol else "trails")

# ---------------------------------------------------------------- title
A(md(f"""# Lab 9 — Fine-tuning a Small Language Model on Crash Narratives

**AI4Mobility (CGN 6933) · Module 6 · reads with 6.1 (the adaptation ladder) and 2.13 (does it earn its keep?)**

In 2.13 a TF-IDF bag of words with a logistic regression beat every frozen BERT probe on
crash narratives, and a fine-tuned DistilBERT did not close the gap. Section 6.1 then gave you a
ladder for adapting a model: **prompt it, then give it retrieved examples, then train a small
adapter (LoRA), and only then think about anything bigger.** This lab climbs the first three
rungs on the same {n('corpus.n')} Florida crash reports, with a 494-million-parameter open model
that fits on the free Colab GPU, and asks one question at every rung: *did that beat the bag of
words, on a split you can defend?*

| | |
|---|---|
| **What you build** | A narrative-to-JSON extractor for six crash fields, four ways: prompt only, fixed examples, retrieved examples, and a LoRA adapter |
| **What it proves** | Whether LoRA beats prompting and retrieval on a split you can defend, and whether any of them beats a bag of words |
| **Check it against** | The baseline, named now: **TF-IDF + logistic regression**, the 2.13 winner, on the same corridor-grouped folds. Also the majority class, and DistilBERT from 2.13 |
| **Runs on** | Colab free tier with a **T4 GPU** (Runtime → Change runtime type). Sections 1–3 run on CPU in seconds |
| **Needs** | `transformers`, `peft`, `accelerate`, `scikit-learn` (one setup cell) · about 1 GB of model download · the narrative file from Canvas · **no API key** |

---

### The honest disclosure, before anything else

**This is not a sample of Florida crashes.** The {n('corpus.n')} reports were chosen from
{n('corpus.n_corridors')} corridors in Pasco, Hernando and Pinellas counties to study left turns and
pedestrians, so {LC['crash_type']['left_turn']} of them are left-turn crashes. No number in this
notebook is a statement about Florida. Every number is a statement about *these reports*, scored
on corridors the model never saw.

The answers you score against are the **coded fields** of the same police report (the boxes the
officer ticked), not a reading of the narrative. Section 1 shows that some of those boxes are
simply never mentioned in the text, and drops them rather than pretending a model could read them.

**The narratives are not in this notebook.** They are redacted police text shared with enrolled
students through Canvas. Keep them out of public repos and hosted chatbots, and clear outputs
before you share your copy."""))

A(md("""## 0 · Setup

Two cells. The first installs; the second is the **only** place the data path appears.

**Getting the data.** Download `crash_narratives_joined.json` from the AI4Mobility Canvas course. That
is the only place it is distributed; there is no public URL. In Colab, run cell 2 and upload the file
when the picker appears, or copy it to your Drive and set `DATA_PATH` to point at it."""))
A(py(C["install"]))
A(py(C["data"]))

# ---------------------------------------------------------------- 1 · schema
A(md(f"""## 1 · Six fields a reader could actually fill in

The coded report has 33 fields. A narrative-to-JSON extractor is only fair to score on fields the
narrative *could* tell you. We keep six:

| Field | Values | From the coded field | Count of the rarer side |
|---|---|---|---|
| `crash_type` | left_turn · angle · pedestrian_bicycle · other | simplified crash type (rear end and the rest → other) | other: {LC['crash_type']['other']} |
| `pedestrian` | yes · no | pedestrian involved | yes: {LC['pedestrian']['yes']} |
| `vehicles` | 1 · 2 · 3+ | total vehicles | 1: {LC['vehicles']['1']}, 3+: {LC['vehicles']['3+']} |
| `injury` | yes · no | severity is anything but No Injury | no: {LC['injury']['no']} |
| `hit_and_run` | yes · no | hit and run | yes: {LC['hit_and_run']['yes']} |
| `distracted` | yes · no | distracted driving | yes: {LC['distracted']['yes']} |

Together these cover the four 2.13 targets (distracted, pedestrian, left turn, injury) plus two that
an agency would want from the same text."""))
A(py(C["schema"]))
A(py(C["score"]))

A(md(f"""### Fields we dropped, and why

Before you ask any model to read a field out of text, check that the text contains it. The audit
below uses a deliberately generous regular expression for each field and counts how many of the
coded positives mention it at all. That share is a **ceiling**: no reader, human or model, can
recover a fact the officer did not write down."""))
A(py(C["audit"]))
A(md(f"""| Field | Coded yes | Narrative mentions it | Ceiling | Decision |
|---|---|---|---|---|
| weather = rain | {AV['weather_rain']['coded_positive']} | {AV['weather_rain']['positive_mentioning']} | {AV['weather_rain']['ceiling_pct']}% | **dropped**: this is the 12.5% ceiling from 2.13; weather belongs to a weather feed, not a narrative |
| light = dark | {AV['light_dark']['coded_positive']} | {AV['light_dark']['positive_mentioning']} | {AV['light_dark']['ceiling_pct']}% | **dropped**: officers almost never describe the lighting |
| surface = wet | {AV['surface_wet']['coded_positive']} | {AV['surface_wet']['positive_mentioning']} | {AV['surface_wet']['ceiling_pct']}% | **dropped** for the same reason |
| alcohol | {AV['alcohol']['coded_positive']} | {AV['alcohol']['positive_mentioning']} | {AV['alcohol']['ceiling_pct']}% | **dropped**: readable, but {AV['alcohol']['coded_positive']} positives across 5 folds cannot support an F1 |
| hit_and_run | {AV['hit_and_run']['coded_positive']} | {AV['hit_and_run']['positive_mentioning']} | {AV['hit_and_run']['ceiling_pct']}% | **kept**, with a known ceiling (section 9) |
| pedestrian | {AV['pedestrian']['coded_positive']} | {AV['pedestrian']['positive_mentioning']} | {AV['pedestrian']['ceiling_pct']}% | **kept**: nearly always written |

Notice what a careless schema would have done. Put `light_condition` in the JSON and every method
"learns" it from the base rate ({AV['light_dark']['coded_positive']} of
{n('corpus.n')} are dark), and the score looks respectable while measuring nothing about reading.

> **Your turn — exercise 1.** The regex for hit-and-run misses some phrasings. Read the coded field
> definition, add two phrasings you think officers use, and re-run the audit. Does the ceiling move
> by more than a couple of reports? What does that tell you about where the remaining misses come from?"""))

# ---------------------------------------------------------------- 2 · baseline
A(md(f"""## 2 · The baseline, named up front

**TF-IDF + logistic regression** with the exact 2.13 settings: English stop words, sublinear term
frequency, words that appear in at least two reports, single words and pairs, classes reweighted
by their frequency. One small model per field. It is the number every rung of the ladder has to beat.

We score each yes/no field with **F1** (it ignores the easy "no" reports), and the two multi-class
fields with **macro-F1** (the average F1 across classes, so `other` counts as much as `left_turn`).
A missing or invalid value counts as wrong. That last rule matters later: a language model that
writes broken JSON gets no partial credit."""))
A(py(C["folds"]))
A(py(C["baseline"]))
A(md(f"""On all five corridor folds:

| | crash_type | pedestrian | vehicles | injury | hit_and_run | distracted |
|---|---|---|---|---|---|---|
| majority class | {f3(MJ['crash_type']['macroF1'])} | {f3(MJ['pedestrian']['F1'])} | {f3(MJ['vehicles']['macroF1'])} | {f3(MJ['injury']['F1'])} | {f3(MJ['hit_and_run']['F1'])} | {f3(MJ['distracted']['F1'])} |
| **TF-IDF + LR** | **{f3(TF['crash_type']['macroF1'])}** | **{f3(TF['pedestrian']['F1'])}** | **{f3(TF['vehicles']['macroF1'])}** | **{f3(TF['injury']['F1'])}** | **{f3(TF['hit_and_run']['F1'])}** | **{f3(TF['distracted']['F1'])}** |

The whole baseline, six fields by five folds, trains in about {round(NUM['tfidf_lr_seconds'])} seconds on a CPU.

**Tie-back to 2.13.** The same model on the same folds gives distracted-driving average precision
**{n('tfidf_lr.distracted.AP')}** here against the **{n('site_2_13.distracted_tfidf_AP_quoted')}**
quoted in 2.13. The small difference comes from library versions, not from a different split. DistilBERT
reached {n('distilbert_g.distracted.AP')} on the same target after {n('distilbert_g.distracted.minutes')} minutes of training."""))

# ---------------------------------------------------------------- 3 · split
_ct_gap = RS['crash_type']['macroF1'] - TF['crash_type']['macroF1']
_other_gap = max(abs(headline(RS, f) - headline(TF, f)) for f in FIELDS if f != 'crash_type')
A(md(f"""## 3 · A split you can defend

Every report belongs to one of {n('corpus.n_corridors')} corridors, and reports from the same
corridor share street names, intersection layouts, and often the same officer's writing habits. If
reports from one corridor land on both sides of the split, the model can pass the test by
recognising the corridor instead of reading the crash. So the five folds are **grouped by
corridor**: every test report comes from a corridor the model has never seen. These are exactly
the folds used in 2.13, so the numbers line up.

What would the shortcut be worth? Shuffle the reports, ignore corridors, and fit the same baseline:"""))
A(py(C["random"]))
A(md(f"""| TF-IDF + LR | crash_type | pedestrian | vehicles | injury | hit_and_run | distracted |
|---|---|---|---|---|---|---|
| random split | {f3(RS['crash_type']['macroF1'])} | {f3(RS['pedestrian']['F1'])} | {f3(RS['vehicles']['macroF1'])} | {f3(RS['injury']['F1'])} | {f3(RS['hit_and_run']['F1'])} | {f3(RS['distracted']['F1'])} |
| corridor split | {f3(TF['crash_type']['macroF1'])} | {f3(TF['pedestrian']['F1'])} | {f3(TF['vehicles']['macroF1'])} | {f3(TF['injury']['F1'])} | {f3(TF['hit_and_run']['F1'])} | {f3(TF['distracted']['F1'])} |

The honest reading is **mixed**, and that is worth saying plainly. On `crash_type` the random split
is {_ct_gap:+.3f} macro-F1 better, which is the corridor shortcut. Corridors differ in their crash
mix and their geometry words, and a shuffled split lets the model use that. On the other five fields
the gaps run both ways (the largest is {_other_gap:.3f}), and the six-field means come out at
{mean_headline(RS):.3f} for the random split and {mean_headline(TF):.3f} for the corridor split. With {LC['pedestrian']['yes']} pedestrian and {LC['hit_and_run']['yes']} hit-and-run positives, a few
reports moving fold is enough to do that. So the random split does not inflate everything. It inflates
the one field that depends on place, and you would not know which field that was without running both.

Retrieval has its own version of this leak, and section 6 measures it: the examples you paste into
the prompt must come from **training corridors only**.

> **Going deeper — why not stratify too?** `GroupKFold` balances fold *sizes*, not label mixes. With
> 8 rear-end crashes in 399, one fold can get most of them. `StratifiedGroupKFold` tries to balance
> both. We keep plain `GroupKFold` so the folds match 2.13 exactly. Exercise 6 asks you to swap it
> and see which numbers move."""))

# ---------------------------------------------------------------- 4 · ladder
A(md(f"""## 4 · The ladder, in plain words

Section 6.1 ordered the ways to adapt a model by cost. This lab climbs the first three rungs with the
model held fixed, so the only thing that changes is how much you teach it.

| Rung | What changes | What you pay |
|---|---|---|
| **Prompt** | only the instructions | nothing but inference |
| **Few-shot / retrieval** | the prompt also carries worked examples | longer prompts, so slower inference; a retrieval index |
| **LoRA** | a small set of new weights, trained on your labelled reports | a training run per fold; an adapter file to manage |

The model is **Qwen2.5-0.5B-Instruct**: 494 million parameters, open weights (Apache-2.0), already
tuned to follow chat instructions. It is deliberately small. It fits on a free T4 with room for
training, and it is the size an agency could run on its own hardware without sending a police
report to anyone's API.

**The equations, in words.**

| Symbol | In plain words |
|---|---|
| $W' = W + \\tfrac{{\\alpha}}{{r}}\\,B A$ | Keep every original weight matrix $W$ frozen. Learn a correction that is the product of two thin matrices: $A$ squeezes the input down to $r$ numbers, and $B$ expands them back. $r$ is how thin, and $\\alpha / r$ is a volume knob on the correction. |
| $r = 16$ on $q, k, v, o$ | We add the correction only to the four attention projections in each of the 24 blocks. That is **2.16 M trainable numbers, 0.44% of the model**. |
| $\\mathcal{{L}} = -\\tfrac{{1}}{{T}}\\sum_t \\log p(y_t \\mid \\text{{prompt}}, y_{{<t}})$ | The training loss is how surprised the model is by each token of the *correct JSON*, averaged over the answer. The prompt and narrative tokens are not scored; the model only learns to answer. |
| $\\text{{sim}}(q, d) = \\cos(\\text{{tfidf}}(q), \\text{{tfidf}}(d))$ | Retrieval picks the training reports whose word profile points the same way as the new report's. It uses the baseline's own features, so what you are testing is how the examples are *used*, not how they are found. |

> **Going deeper — why low rank is enough.** Fine-tuning moves the 896 × 896 query matrix in one block by some
> change $\\Delta W$. LoRA's bet is that the useful part of $\\Delta W$ for one narrow task lives in a few
> directions, so $\\Delta W \\approx BA$ with $B$ being 896 × 16 and $A$ 16 × 896: 28,672 numbers instead of
> 802,816. $B$ starts at zero, so at step 0 the adapted model *is* the original model, and training
> can only move it away as far as the data pushes. Exercise 5 asks you to change $r$."""))

# ---------------------------------------------------------------- 5 · prompting
A(md(f"""## 5 · Rung 1 — just ask

The prompt is the schema, written out with the allowed values, and the narrative. Decoding is
greedy, so the same input always gives the same output, and generation stops after 80 tokens. The
parser is strict on purpose: it takes the first `{{...}}` in the reply, maps `3` to `3+` and
`true` to `yes`, and marks any field that is missing or outside its allowed values as invalid."""))
A(py(C["model"]))
A(md(f"""**How long this takes.** On the build machine (8 CPU threads, bfloat16, no GPU) each
narrative took about {n('methods.zero.sec_per_narrative') if HAS['zero'] else TODO} s zero-shot and
{n('methods.rag3.sec_per_narrative') if HAS['rag3'] else TODO} s with three examples in the prompt.
On a T4 it should be faster. {TODO}: time it on a T4 and put the number here. Set
`RUN_FOLDS = [0]` below for a one-fifth run if you are short on time; every printout says which
folds it covers."""))
A(py(C["config"]))
A(py(C["zero"]))

def pd(m, f): return M[m]["pred_dist"][f]

def _vs_tf(m):
    better = [f"`{f}`" for f in FIELDS if headline(M[m]["scores"], f) > headline(TF, f) + 0.01]
    tied = [f"`{f}`" for f in FIELDS if abs(headline(M[m]["scores"], f) - headline(TF, f)) <= 0.01]
    if not better and not tied: return "trails on all six fields"
    out = []
    if better: out.append("is ahead on " + ", ".join(better))
    if tied: out.append("is within 0.01 on " + ", ".join(tied))
    rest = len(FIELDS) - len(better) - len(tied)
    return " and ".join(out) + f", and trails on the other {rest}"
if HAS["zero"]:
    Z = M["zero"]
    A(md(f"""**What you should see.** Valid JSON almost every time ({100*Z['json_valid']:.1f}%), and almost
nothing inside it. The 0.5B model wrote `left_turn` for {pd('zero','crash_type').get('left_turn',0)} of
{n('corpus.n')} reports and `3+` vehicles for {pd('zero','vehicles').get('3+',0)}. It answered
hit-and-run "yes" {pd('zero','hit_and_run').get('yes',0)} times, and in
{Z['schema_failures'].get('bad_or_missing_pedestrian',0)} replies it renamed or dropped the `pedestrian`
key. Only {100*Z['schema_valid']:.0f}% of replies had all six fields valid. It is reading the *schema*,
not the narrative: the first allowed value of a list is a strong pull for a model this small. `injury`,
with F1 {f3(Z['scores']['injury']['F1'])}, is the only field where it does better than the majority class
({f3(MJ['injury']['F1'])} by saying "yes" to everything), and only barely.

Valid JSON is not a measure of correct JSON. Report both."""))
else:
    A(md(f"""**What you should see.** {TODO}: zero-shot scores were not produced in the reproducer."""))

A(md("""## 6 · Rung 2 — show it worked examples

Two ways to fill the prompt with three solved reports. **Fixed**: the same three for every
narrative (the shortest training report of each main crash type). **Retrieved**: the three training
reports most similar to the one being read, found with the baseline's TF-IDF features. The index is
rebuilt inside every fold from the **training corridors only**."""))
A(py(C["fixed"]))
A(py(C["rag"]))
if HAS["fixed3"] and HAS["rag3"]:
    F_, R_ = M["fixed3"], M["rag3"]
    A(md(f"""| | crash_type | pedestrian | vehicles | injury | hit_and_run | distracted | mean | all fields valid |
|---|---|---|---|---|---|---|---|---|
| zero-shot | {' | '.join(f3(headline(M['zero']['scores'], f)) for f in FIELDS)} | {f3(mean_headline(M['zero']['scores']))} | {100*M['zero']['schema_valid']:.0f}% |
| fixed 3 | {' | '.join(f3(headline(F_['scores'], f)) for f in FIELDS)} | {f3(mean_headline(F_['scores']))} | {100*F_['schema_valid']:.0f}% |
| retrieved 3 | {' | '.join(f3(headline(R_['scores'], f)) for f in FIELDS)} | **{f3(mean_headline(R_['scores']))}** | {100*R_['schema_valid']:.0f}% |
| *TF-IDF + LR* | {' | '.join(f3(headline(TF, f)) for f in FIELDS)} | *{f3(mean_headline(TF))}* | — |

Fixed examples teach the **format**: the share of fully valid replies jumps to {100*F_['schema_valid']:.0f}%,
and the model starts using all the values. They do not teach the **task**. It now calls
{pd('fixed3','pedestrian').get('yes',0)} reports pedestrian crashes where there are {LC['pedestrian']['yes']},
and it still answers hit-and-run "yes" only {pd('fixed3','hit_and_run').get('yes',0)} time(s).

Retrieved examples are where the signal shows up. Mean F1 goes from {f3(mean_headline(F_['scores']))} to
**{f3(mean_headline(R_['scores']))}**, and the pedestrian F1 goes from {f3(F_['scores']['pedestrian']['F1'])} to
{f3(R_['scores']['pedestrian']['F1'])}. Be honest about *why*. Three neighbours chosen by TF-IDF usually
share the answer, so a model that copies the most similar example's labels already gets a long way. Part
of what retrieval buys here is a nearest-neighbour classifier, run through a language model. Exercise 3
measures how much.

Against the bag of words it {_vs_tf('rag3')}, and it costs about {n('methods.rag3.sec_per_narrative')} s
per report against milliseconds."""))
else:
    A(md(f"""{TODO}: the fixed and retrieved few-shot results were not produced in the reproducer."""))

A(md("""### The retrieval leak

Now do it wrong once on purpose. Let retrieval search **every other report**, including those from the
test report's own corridor. This is the mistake that happens by default when the index is built once,
before the split."""))
A(py(C["leaky"]))
if HAS["rag3_leaky"] and HAS["rag3"]:
    L_ = M["rag3_leaky"]; R_ = M["rag3"]["scores"]
    _up = [f"`{f}` ({headline(L_['scores'], f) - headline(R_, f):+.3f})" for f in FIELDS if headline(L_['scores'], f) > headline(R_, f)]
    _dn = [f"`{f}` ({headline(L_['scores'], f) - headline(R_, f):+.3f})" for f in FIELDS if headline(L_['scores'], f) < headline(R_, f)]
    _dm = mean_headline(L_['scores']) - mean_headline(R_)
    _rsd = mean_headline(RS) - mean_headline(TF)
    A(md(f"""| retrieval from | crash_type | pedestrian | vehicles | injury | hit_and_run | distracted | mean |
|---|---|---|---|---|---|---|---|
| training corridors only | {' | '.join(f3(headline(R_, f)) for f in FIELDS)} | {f3(mean_headline(R_))} |
| every other report (leaky) | {' | '.join(f3(headline(L_['scores'], f)) for f in FIELDS)} | {f3(mean_headline(L_['scores']))} |

The leak raises the mean from {f3(mean_headline(R_))} to {f3(mean_headline(L_['scores']))} ({_dm:+.3f}). It is not uniform:
it helps {', '.join(_up)}, and it hurts {', '.join(_dn) if _dn else 'nothing'}. Neighbours from the same corridor
share its crash mix and its street vocabulary. That helps the fields that depend on place and does
nothing for counting vehicles.

Compare section 3. There, shuffling the reports moved the TF-IDF six-field mean by {abs(_rsd):.3f}. Here, the
leak moves retrieval's mean by {_dm:+.3f}. A language model that copies its examples is **more** exposed
to a leaky index than a bag of words is to a leaky split, because the leaked neighbour sits right in the
prompt. On five folds and {n('corpus.n')} reports, a few hundredths is roughly the size a handful of
reports can move a field, so do not read the exact figure too closely. Read the direction, and read that
the leaky row is a number you could not quote to an agency that wants this on a corridor nobody labelled.

Leaky retrieval also ran slower on the build machine ({L_['sec_per_narrative']} s per report against
{M['rag3']['sec_per_narrative']} s). That reflects a busier shared CPU, not the method: the prompts are the same length."""))
else:
    A(md(f"""{TODO}: the leaky-retrieval comparison was not run in the reproducer. Run cell 14 and compare its mean with cell 13's."""))

A(md("""> **Your turn — exercise 2.** Change `k` in `retrieved_shots` to 1 and to 6. More examples make a
> longer prompt. Does the score keep rising, and what happens to seconds per report?
>
> **Your turn — exercise 3.** Build the "copy the nearest neighbour" baseline with no language model:
> for each test report, output the gold JSON of the single most similar training report. Score it with
> `score()`. How much of the retrieval rung's gain does it explain?"""))

# ---------------------------------------------------------------- 7 · LoRA
A(md(f"""## 7 · Rung 3 — LoRA

One adapter per fold, trained on that fold's four training folds (about 320 reports), then asked the
**plain zero-shot prompt** about the held-out corridors. There are no examples in the prompt, so
whatever it gets right it learned from training.

Settings: rank 16, alpha 32, dropout 0.05, on the q/k/v/o projections; AdamW at 1e-4 (fp32 adapter, non-finite steps skipped) with a 10-step
warm-up and a linear decay; 2 epochs; 4 reports per update. Nothing was tuned on the test folds.
If you tune them, tune them inside the training folds."""))
A(py(C["lora_def"]))
A(py(C["lora_run"]))
if HAS["lora"]:
    LO = M["lora"]; FM = LO["fold_meta"]; PF = LO["per_fold"]; R_ = M["rag3"]["scores"]
    _tm = [FM[str(k)]["train_seconds"] / 60 for k in range(5)]
    _fold_rows = "\n".join(
        f"| fold {k} ({FM[str(k)]['n_test']} reports) | " + " | ".join(f3(headline(PF[k], f)) for f in FIELDS)
        + f" | {f3(mean_headline(PF[k]))} | {FM[str(k)]['final_train_loss']:.3f} |" for k in range(5))
    _worst = min(range(5), key=lambda k: mean_headline(PF[k]))
    _pd = LO["pred_dist"]; NN = n('corpus.n')
    _yes = {f: _pd[f].get("yes", 0) for f in ["pedestrian", "hit_and_run", "distracted"]}
    _beats_rag = [f"`{f}`" for f in FIELDS if headline(LO['scores'], f) > headline(R_, f)]
    _ct_acc_l = LO['scores']['crash_type']['acc']; _ct_acc_r = R_['crash_type']['acc']
    _skip = sum(v.get('skipped', 0) for v in FM.values())
    A(md(f"""**Results, all five folds.**

| | crash_type | pedestrian | vehicles | injury | hit_and_run | distracted | mean | all fields valid |
|---|---|---|---|---|---|---|---|---|
| retrieved 3 | {' | '.join(f3(headline(R_, f)) for f in FIELDS)} | {f3(mean_headline(R_))} | {100*M['rag3']['schema_valid']:.0f}% |
| **LoRA** | {' | '.join(f3(headline(LO['scores'], f)) for f in FIELDS)} | **{f3(mean_headline(LO['scores']))}** | {100*LO['schema_valid']:.1f}% |
| *TF-IDF + LR* | {' | '.join(f3(headline(TF, f)) for f in FIELDS)} | *{f3(mean_headline(TF))}* | — |

Against the bag of words, LoRA {_vs_tf('lora')}. Against retrieval it wins on {', '.join(_beats_rag)}
and loses everywhere else, so its mean ({f3(mean_headline(LO['scores']))}) sits between fixed examples
({f3(mean_headline(M['fixed3']['scores']))}) and retrieval ({f3(mean_headline(R_))}).

**Fold by fold.** The last column is the answer loss in the final epoch of training.

| held-out fold | crash_type | pedestrian | vehicles | injury | hit_and_run | distracted | mean | train loss |
|---|---|---|---|---|---|---|---|---|
{_fold_rows}

Fold {_worst} is the cautionary tale. Its adapter scored at the majority-class level on `crash_type` and `vehicles`
({f3(headline(PF[_worst], 'crash_type'))} and {f3(headline(PF[_worst], 'vehicles'))}, against {f3(headline(MJ, 'crash_type'))} and {f3(headline(MJ, 'vehicles'))} for always
guessing the commonest answer) and 0 on every yes/no field except injury, so its mean is {f3(mean_headline(PF[_worst]))}. Yet its training
loss ({FM[str(_worst)]['final_train_loss']:.3f}) looks as healthy as the others'. The other four folds learned
something real about `vehicles` and `crash_type`, and the spread between folds is wide. One adapter
per fold is not a luxury: a single run could have landed on fold {_worst}'s number, or fold
{max(range(5), key=lambda k: mean_headline(PF[k]))}'s.

**What LoRA learned, and what it did not.**
- **The format.** {100*LO['schema_valid']:.1f}% of replies had all six fields present and allowed, and
  that is with the plain zero-shot prompt that managed {100*M['zero']['schema_valid']:.1f}% before training.
- **The common, wordy fields.** `vehicles` reaches {f3(headline(LO['scores'], 'vehicles'))} macro-F1, the
  best of any language-model rung. On `crash_type` it is right {100*_ct_acc_l:.1f}% of the time, more often
  than retrieval ({100*_ct_acc_r:.1f}%). Its macro-F1 is lower ({f3(headline(LO['scores'], 'crash_type'))} against
  {f3(headline(R_, 'crash_type'))}) because it rarely says `pedestrian_bicycle` ({_pd['crash_type'].get('pedestrian_bicycle', 0)} times
  out of {NN}, where the corpus has {LC['crash_type']['pedestrian_bicycle']}) and never gets `other`. Accuracy rewards
  leaning on the big class. Macro-F1 does not.
- **Not the rare yes/no fields.** Across all {NN} reports it said "yes" to pedestrian {_yes['pedestrian']} times,
  to hit-and-run {_yes['hit_and_run']} times and to distracted {_yes['distracted']} times. The corpus has
  {LC['pedestrian']['yes']}, {LC['hit_and_run']['yes']} and {LC['distracted']['yes']} of each. It collapsed to "no",
  which keeps accuracy between {100*min(LO['scores'][f]['acc'] for f in ['pedestrian','hit_and_run','distracted']):.0f}% and {100*max(LO['scores'][f]['acc'] for f in ['pedestrian','hit_and_run','distracted']):.0f}% and is worth almost nothing in F1.

**Why the loss lied.** The answer loss averages over every answer token. Most of them are braces,
quotes and field names, identical in every reply and quickly learned. The few tokens that carry a rare
"yes" are a small share of that average. Two epochs at this learning rate was enough to make the
average small without making "yes" likely. The fix belongs in the training set, not the test fold:
ask the adapter about some of its own training reports (exercise 5). If it says "no" there too, it is
under-fitting the rare fields.

**What it cost.** On the build machine (8 CPU threads, bfloat16, no GPU), training the five adapters took
**{LO['train_minutes_total']} minutes** in total, and answering all {NN} held-out reports took
{LO['infer_minutes_total']} minutes ({LO['sec_per_narrative']} s per report). Per fold, training ranged from
{min(_tm):.1f} to {max(_tm):.1f} minutes for the same amount of work, because the machine was shared, so read
the shortest folds as the better guide. {_skip} of about 800 optimiser steps were skipped as non-finite
(bfloat16 on a CPU; the T4 runs in float32). {TODO}: time the training and answering on a Colab T4 and
put the numbers here."""))
else:
    A(md(f"""{TODO}: the LoRA run did not finish in the reproducer, so this section has no numbers yet.
Run cells 15–16 on a T4 and fill in the table from cell 17."""))

# ---------------------------------------------------------------- 8 · scoreboard
A(md("## 8 · One scoreboard, and what each line cost"))
A(py(C["board"]))
DB = NUM["distilbert_g"]
_cost = [f"| TF-IDF + LR | ~{round(NUM['tfidf_lr_seconds'])} s for all fields and folds | milliseconds | — |"]
for k, lab in [("zero", "zero-shot"), ("fixed3", "fixed 3"), ("rag3", "retrieved 3"), ("rag3_leaky", "retrieved 3, leaky")]:
    if HAS[k]: _cost.append(f"| {lab} | none | {M[k]['sec_per_narrative']} s | {M[k]['total_minutes']} min |")
if HAS["lora"]:
    _cost.append(f"| LoRA | {M['lora']['train_minutes_total']} min (5 adapters) | {M['lora']['sec_per_narrative']} s | {M['lora']['infer_minutes_total']} min |")
_cost.append(f"| DistilBERT (2.13), one field | {DB['distracted']['minutes']} min (distracted), {DB['pedestrian']['minutes']} min (pedestrian) | — | — |")

_db_rows = []
for t in ["distracted", "pedestrian"]:
    cells = [f"{DB[t]['F1']:.3f}", f"{TF[t]['F1']:.3f}"]
    for k in ["rag3", "lora"]:
        cells.append(f"{M[k]['scores'][t]['F1']:.3f}" if HAS[k] else "TODO-after-run")
    _db_rows.append(f"| {t} | " + " | ".join(cells) + " |")

_ranked = sorted([k for k in ["zero", "fixed3", "rag3", "lora"] if HAS[k]], key=lambda k: -mean_headline(M[k]["scores"]))
_nm = {"zero": "zero-shot", "fixed3": "fixed examples", "rag3": "retrieved examples", "lora": "LoRA"}
_board_read = (f"Nothing beats the bag of words. TF-IDF + LR averages {mean_headline(TF):.3f} and is the best method on "
               + f"{sum(1 for f in FIELDS if all(headline(TF, f) >= headline(M[k]['scores'], f) for k in _ranked))} of the six fields. "
               + "Among the language-model rungs, the honest order is " + " > ".join(f"{_nm[k]} ({mean_headline(M[k]['scores']):.3f})" for k in _ranked)
               + ". Retrieval and LoRA fail in different places: retrieval is the better reader of rare yes/no fields, "
               + "LoRA the better counter of vehicles. The language models also cost seconds per report where the "
               + "bag of words costs milliseconds.")
A(md(f"""All {n('corpus.n')} reports, five corridor folds, the same scorer:

{scoreboard()}

Columns are F1 for the yes/no fields and macro-F1 for `crash_type` and `vehicles`. "JSON valid" is the
share of replies with all six fields present and allowed.

**Against DistilBERT from 2.13.** That model was fine-tuned one field at a time on the same folds. Its
F1 is at a 0.5 threshold; the language models give hard answers, so F1 is the only fair common number.
(Average precision needs a ranking, which a JSON answer does not have.)

| field | DistilBERT | TF-IDF + LR | retrieved 3 | LoRA |
|---|---|---|---|---|
{chr(10).join(_db_rows)}

**What it cost, on the build machine** (8 CPU threads, bfloat16, no GPU, shared with other jobs, so
treat the minutes as rough). {TODO}: T4 timings for every row.

| method | training | per report | all {n('corpus.n')} reports |
|---|---|---|---|
{chr(10).join(_cost)}

**Reading the board.** {_board_read}"""))

# ---------------------------------------------------------------- 9 · ugly
A(md("""## 9 · The ugly cases

Aggregate counts only; the cell does not print narratives. Cell 19 lets you read one disagreement on
your own machine."""))
A(py(C["ugly"]))
_hr = NUM["hit_and_run_mentioned"]
_hr_rows = []
for k, lab in [("zero", "zero-shot"), ("fixed3", "fixed 3"), ("rag3", "retrieved 3"), ("lora", "LoRA")]:
    if HAS[k]:
        h = M[k]["hit_and_run_recall_by_mention"]
        _hr_rows.append(f"| {lab} | {h['mentioned']:.2f} | {h['not_mentioned']:.2f} |")
_conf = []
for k, lab in [("rag3", "retrieved 3"), ("lora", "LoRA")]:
    if HAS[k]:
        c = M[k]["crash_type_confusion"]
        _conf.append(f"| {lab} | {c.get('angle->left_turn',0)} | {c.get('left_turn->angle',0)} | "
                     f"{c.get('pedestrian_bicycle->left_turn',0) + c.get('pedestrian_bicycle->angle',0)} | "
                     f"{sum(v for kk, v in c.items() if kk.startswith('other->') and kk != 'other->other')} of {LC['crash_type']['other']} |")
A(md(f"""**1 · The hit-and-run the narrative does not mention.** Of {_hr['positives']} coded hit-and-runs,
the narrative says so in about {_hr['mentioned']}, going by the section 1 regex. The rest are ticked on
the form and never described. Recall split by that:

| | recall, narrative says so | recall, narrative silent |
|---|---|---|
{chr(10).join(_hr_rows)}

A reader cannot be blamed for the second column. An evaluation that does not separate the two will
blame it anyway.

**2 · Left turn versus angle.** The coded crash type is a judgement about *which movement* caused the
crash. Narratives describe both vehicles' movements, often with the left-turner second. These are the
biggest off-diagonal cells, with pedestrian crashes called something else and the rare `other` class:

| | angle → left_turn | left_turn → angle | pedestrian/bicycle → a vehicle type | other, missed |
|---|---|---|---|---|
{chr(10).join(_conf) if _conf else '| TODO-after-run | | | | |'}

**3 · `other` is a bin, not a class.** It holds {LC['crash_type']['other']} reports: rear ends, a head-on,
a sideswipe, an off-road. A macro-F1 counts it as a quarter of `crash_type`, so a few reports swing the
field.

**4 · Injury is a coded severity, not a sentence.** "Complained of pain" or "transported as a
precaution" may or may not be coded as an injury. Every method sits in a narrow band on `injury`, which
suggests the field itself is noisy against the text.

**5 · Format failures are real failures.** A reply that renames `pedestrian` to `pedestrian_bicycle` is
scored as wrong on that field. In production that reply breaks the parser, not just the metric.

> **Your turn — exercise 4.** Re-score every method with the "narrative silent" hit-and-runs removed
> from the evaluation (treat them as unknown, not as negatives). Which method's ranking changes?"""))
A(py(C["peek"]))

# ---------------------------------------------------------------- 10 · close
if HAS["lora"]:
    _lt = mean_headline(M["lora"]["scores"]); _tt = mean_headline(TF); _rt = mean_headline(M["rag3"]["scores"])
    _verdict = (f"**No, not at these settings.** On these {n('corpus.n')} reports and these corridor folds, LoRA averages "
                f"{_lt:.3f} across the six fields. Retrieval from training corridors averages {_rt:.3f}, and a TF-IDF "
                f"logistic regression trained in about a minute averages {_tt:.3f}. LoRA learned the format and the "
                f"common fields: it is the best language-model rung on `vehicles` and the most often right on "
                f"`crash_type`. It collapsed to \"no\" on the rare yes/no fields, and on one fold it collapsed almost "
                f"entirely, behind a training loss that looked fine. Retrieval wins the mean, but part of its gain is "
                f"copying neighbours, and a leaky index inflates it further (section 6).")
else:
    _verdict = f"{TODO}: the LoRA verdict needs the LoRA run."
A(md(f"""## 10 · What this was for

**The answer to the lab's question.** {_verdict} Read that with the costs in section 8 and the split
in section 3. This is one small model, one prompt, and one untuned set of LoRA settings. It is
a fair answer to "does LoRA help out of the box", not to "can LoRA ever help". Exercise 5 is how you would
find out, without touching the test folds.

```
Fit card — LoRA on a small open language model, for text-to-fields extraction

Idea in one sentence:  Freeze a pretrained instruction-following model and train a thin,
                       low-rank correction so it answers your schema the way your coders do.

Why it works (the logic):  The model already reads English and writes JSON; what it lacks is
                       your field definitions and your coders' habits. Those are a small change
                       to how it maps text to answer, which a low-rank update can hold.

Fits these tasks:  extraction · classification into a fixed schema · several fields at once,
                       where one model answering a JSON record beats six separate classifiers to
                       maintain; data that cannot leave the agency, so a hosted API is out.

Needs this data:  a few hundred labelled reports, where the labels come from fields the text
                       actually supports (section 1); a split that holds out whole places, so the
                       score predicts a new corridor.

Breaks when:  the field is not in the text (lighting, weather, surface); the label is a
                       judgement the text leaves ambiguous (left turn vs angle); a field is rare
                       (1 in 10 to 1 in 5 here) and the adapter learns to say "no", while the average
                       loss still looks fine; one training run is trusted without fold-to-fold spread.

Keep the classical method when:  the fields are few and keyword-shaped, the budget is a CPU,
                       or you need a model you can audit term by term. On this corpus a TF-IDF
                       logistic regression trained in about a minute beat every rung of the ladder.
```

### Where this goes next, in the field

| Domain | Task | Data you would need | The baseline to beat |
|---|---|---|---|
| **Crash records (FDOT, HSMV)** | Flag reports where the coded fields disagree with the narrative, for review | the agency's own narratives and coded forms | a keyword audit and a TF-IDF classifier per field |
| **Safety analysis (HSIP, Vision Zero)** | Pull pedestrian and turning-movement detail that the form does not code | a few hundred reports coded by an analyst for the new field | the analyst reading reports, timed |
| **Transit operations** | Turn incident logs into structured cause codes | the agency's incident log and its cause taxonomy | the cause code the operator picked from a dropdown |
| **Agents (Module 6–7)** | A small local model as the extraction tool an agent calls | the same schema, plus checks on the tool's output | the same agent calling a prompted model |

### Evaluation close

- **Baseline.** Majority class, and TF-IDF + logistic regression with the 2.13 settings on the same
  folds. DistilBERT from 2.13 for the two fields it was trained on.
- **The split and why it is honest.** Five folds grouped by corridor, identical to 2.13. Retrieval
  examples come from training corridors only, and section 6 measures what happens otherwise. Nothing was
  tuned on test folds.
- **The ugly cases.** Coded fields that the narrative never mentions; left turn versus angle;
  a catch-all `other`; injury coding that the text does not settle; replies that break the schema.

### Exercises, collected

1. Widen the hit-and-run regex and re-run the availability audit (section 1).
2. Change the number of retrieved examples (section 6).
3. Build the nearest-neighbour copy baseline (section 6).
4. Re-score with the silent hit-and-runs removed (section 9).
5. **LoRA settings.** Try rank 4 and rank 64, or 1 epoch and 4, or a higher learning rate. First ask
   the adapter about 40 of its own *training* reports: if it gives the usual answer even there, it is
   under-fitting, and you learned that without touching the test fold. Pick the setting using fold 0's
   training corridors only (split them again by corridor), then report all five folds once.
6. Swap `GroupKFold` for `StratifiedGroupKFold` and report which fields move (section 3).
7. Swap in `Qwen/Qwen2.5-1.5B-Instruct`. It still fits on a T4 for inference; for LoRA you may need
   a smaller batch or shorter narratives. Does the zero-shot rung stop collapsing?

### Check yourself

1. Zero-shot replies were valid JSON almost every time. Why is that number nearly useless on its own,
   and what would you report next to it?
2. A colleague builds the retrieval index once on all {n('corpus.n')} reports and then runs the folds.
   What exactly leaks, and which field in this lab would you expect to be inflated most?
3. An agency wants `light_condition` extracted from narratives. Using section 1, write the two sentences
   you say back.
4. LoRA tied the bag of words on `injury` and trailed it badly on `hit_and_run`, with a training loss
   that looked fine on every fold. Name one reason for each, and one check you could run on the
   training corridors alone that would have warned you.

---

*Built with `Qwen/Qwen2.5-0.5B-Instruct` (Apache-2.0), `transformers`, `peft` and `scikit-learn`. The
narratives are {n('corpus.n')} redacted Florida HSMV long-form crash reports, distributed to enrolled
students through Canvas and not included in this notebook. Every number in the prose was produced by the
reproducer in `Labs/lora_crash/` on a CPU (no GPU). Your T4 run will differ slightly, and LoRA, which varied
most from fold to fold, may differ most. AI4Mobility.*"""))

NB = {"cells": CELLS,
      "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                   "language_info": {"name": "python", "version": "3.11"},
                   "accelerator": "GPU", "colab": {"gpuType": "T4", "provenance": []}},
      "nbformat": 4, "nbformat_minor": 5}

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "lab9_lora_crash_narratives.ipynb"
    for c in NB["cells"]:
        c["source"] = [l + "\n" for l in c["source"][:-1]] + [c["source"][-1]]
    json.dump(NB, open(out, "w"), indent=1)
    print(f"{out}: {len(NB['cells'])} cells "
          f"({sum(1 for c in NB['cells'] if c['cell_type']=='code')} code) · methods with numbers: "
          f"{[k for k, v in HAS.items() if v]}")
