# code cells for the notebook, kept apart from the prose so they can be diffed against the reproducer
C = {}
C["install"] = r'''# ===========================================================================
#  CELL 1 — install and check the runtime. Safe to re-run.
# ===========================================================================
import subprocess, sys
# transformers>=4.56 for the `dtype=` argument used below; peft for LoRA. No API key anywhere.
subprocess.run([sys.executable, "-m", "pip", "install", "--quiet",
                "transformers>=4.56", "peft>=0.17", "accelerate", "scikit-learn"], check=True)

import torch, transformers, peft, sklearn
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
# A T4 has no fast bfloat16, so on the GPU we run the 0.5B model in float32 (2 GB, fits easily).
# On a CPU with bfloat16 support, bfloat16 halves the memory and roughly doubles the speed.
DTYPE = torch.float32 if DEVICE == "cuda" else torch.bfloat16
torch.manual_seed(0)
print("torch", torch.__version__, "· transformers", transformers.__version__, "· peft", peft.__version__)
print("device:", torch.cuda.get_device_name(0) if DEVICE == "cuda" else "CPU only", "· dtype:", DTYPE)
if DEVICE == "cpu":
    print("No GPU. In Colab: Runtime > Change runtime type > T4 GPU. Sections 1-3 are fine on CPU; "
          "sections 4-6 will be slow (see the timing table in section 7).")'''

C["data"] = r'''# ===========================================================================
#  CELL 2 — load the narratives. ONE place to point at the file.
# ===========================================================================
import os, json, urllib.request

# The narratives are course data, distributed ONLY through Canvas. There is no public copy and no URL.
#   1. Download crash_narratives_joined.json from the AI4Mobility Canvas course.
#   2. Either upload it when the file picker appears below, or put it somewhere and set DATA_PATH.
DATA_PATH = "crash_narratives_joined.json"   # e.g. "/content/drive/MyDrive/ai4mobility/crash_narratives_joined.json"
DATA_URL  = ""                               # leave empty: the course does not host this file publicly

if not os.path.exists(DATA_PATH):
    if DATA_URL:
        urllib.request.urlretrieve(DATA_URL, DATA_PATH)
    else:
        try:
            from google.colab import files           # Colab: a file picker appears below this cell
            print("Upload crash_narratives_joined.json (download it from Canvas first)")
            DATA_PATH = next(iter(files.upload()))
        except ImportError:
            raise FileNotFoundError("Download crash_narratives_joined.json from Canvas, put it next to "
                                    "this notebook, or set DATA_PATH above.")

D = json.load(open(DATA_PATH))
TEXTS  = [r["text"] for r in D]
GROUPS = [r["corridor"] for r in D]
print(f"{len(D)} reports · {len(set(GROUPS))} corridors · "
      f"median narrative {sorted(len(t.split()) for t in TEXTS)[len(D)//2]} words")
# These are redacted police narratives shared for this course only. Do not paste them into a
# public repo, a forum, or a hosted chatbot, and clear this notebook's outputs before you share it.'''

C["schema"] = r'''# ===========================================================================
#  CELL 3 — the schema: six fields, each read off a coded field of the same report.
# ===========================================================================
import re, collections, numpy as np

def crash_type(r):
    return {"Left Turn": "left_turn", "Angle": "angle", "Pedestrian": "pedestrian_bicycle",
            "Bicycle": "pedestrian_bicycle"}.get(r["S4_CRASH_TYPE_SIMPLIFIED"], "other")
def vehicles(r):
    k = int(r["TOTAL_NUMBER_OF_VEHICLES"]); return "3+" if k >= 3 else str(k)
yn = lambda b: "yes" if b else "no"

FIELDS = {   # field -> (allowed values, how the answer key is read off the coded report)
 "crash_type":  (["left_turn", "angle", "pedestrian_bicycle", "other"], crash_type),
 "pedestrian":  (["yes", "no"], lambda r: yn(r["S4_IS_PEDESTRIAN_INVOLVED"] == "Y")),
 "vehicles":    (["1", "2", "3+"], vehicles),
 "injury":      (["yes", "no"], lambda r: yn(r["S4_CRASH_SEVERITY"] != "No Injury")),
 "hit_and_run": (["yes", "no"], lambda r: yn(r["S4_IS_HIT_AND_RUN"] == "Y")),
 "distracted":  (["yes", "no"], lambda r: yn(r["S4_IS_DISTRACTED"] == "Y")),
}
GOLD = [{f: fn(r) for f, (_, fn) in FIELDS.items()} for r in D]
gold_json = lambda i: json.dumps(GOLD[i])

for f in FIELDS:
    print(f"{f:12s}", dict(collections.Counter(g[f] for g in GOLD).most_common()))'''

C["score"] = r'''# ===========================================================================
#  CELL 4 — one scorer for every method. A missing or invalid value counts as WRONG.
# ===========================================================================
from sklearn.metrics import f1_score, precision_score, recall_score

def score(preds, idx):
    out = {}
    for f, (vals, _) in FIELDS.items():
        g = [GOLD[i][f] for i in idx]
        p = [(preds[i] or {}).get(f) or "__missing__" for i in idx]
        if vals == ["yes", "no"]:
            gy, py_ = [x == "yes" for x in g], [x == "yes" for x in p]
            out[f] = {"F1": f1_score(gy, py_, zero_division=0),
                      "P": precision_score(gy, py_, zero_division=0), "R": recall_score(gy, py_, zero_division=0)}
        else:
            out[f] = {"F1": f1_score(g, p, labels=vals, average="macro", zero_division=0)}   # macro-F1
    out["mean"] = {"F1": float(np.mean([out[f]["F1"] for f in FIELDS]))}
    return out

SCORES = {}
def show(name, s):
    SCORES[name] = s
    print(f"{name:34s}" + "".join(f"{f[:11]:>12s}" for f in list(FIELDS) + ["mean"]))
    print(" " * 34 + "".join(f"{s[f]['F1']:12.3f}" for f in list(FIELDS) + ["mean"]))'''

C["audit"] = r'''# ===========================================================================
#  CELL 5 — availability audit: is the field even WRITTEN in the narrative?
# ===========================================================================
AUDIT = {   # field: (coded positive, a generous regex for "the officer wrote about it")
 "weather = rain":  (lambda r: r["WEATHER_CONDITION"] == "Rain", r"rain|wet|shower|storm|drizzl|downpour"),
 "light = dark":    (lambda r: r["LIGHT_CONDITION"].startswith("Dark"), r"\bdark|night|street ?light|headlight|lighting"),
 "surface = wet":   (lambda r: r["ROAD_SURFACE_CONDITION"] == "Wet", r"\bwet|rain|slick|hydroplan|standing water"),
 "alcohol":         (lambda r: r["S4_IS_ALCOHOL_RELATED"] == "Y", r"alcohol|impair|\bDUI|\bBAC\b|breath|intoxicat|beer|drunk|sobriety"),
 "hit_and_run":     (lambda r: r["S4_IS_HIT_AND_RUN"] == "Y", r"fled|left the scene|leave the scene|unknown (?:vehicle|driver)|did not stop|failed to remain"),
 "pedestrian":      (lambda r: r["S4_IS_PEDESTRIAN_INVOLVED"] == "Y", r"pedestrian|non-?motorist|NM ?0?\d|walking|crosswalk"),
}
print(f"{'field':16s}{'coded yes':>10s}{'...mentioned':>14s}{'ceiling':>9s}")
for name, (pos, rx) in AUDIT.items():
    P = [r for r in D if pos(r)]
    hit = sum(bool(re.search(rx, r["text"], re.I)) for r in P)
    print(f"{name:16s}{len(P):10d}{hit:14d}{100*hit/max(1,len(P)):8.1f}%")'''

C["folds"] = r'''# ===========================================================================
#  CELL 6 — the split: five folds, grouped by corridor. Same folds as 2.13.
# ===========================================================================
from sklearn.model_selection import GroupKFold
FOLDS = list(GroupKFold(n_splits=5).split(np.arange(len(D)), None, GROUPS))
for k, (tr, te) in enumerate(FOLDS):
    assert not set(GROUPS[i] for i in tr) & set(GROUPS[i] for i in te)   # no corridor on both sides
    print(f"fold {k}: test {len(te):3d} reports from {len(set(GROUPS[i] for i in te))} corridors")
ALL = np.arange(len(D))'''

C["baseline"] = r'''# ===========================================================================
#  CELL 7 — the baseline, named up front: majority class, then TF-IDF + logistic regression
#  with exactly the settings that won section 2.13.
# ===========================================================================
import time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

def tfidf():
    return TfidfVectorizer(stop_words="english", sublinear_tf=True, min_df=2, ngram_range=(1, 2))

def classical(folds):
    pred = [dict() for _ in D]
    for tr, te in folds:
        v = tfidf(); Xtr = v.fit_transform([TEXTS[i] for i in tr]); Xte = v.transform([TEXTS[i] for i in te])
        for f in FIELDS:
            m = LogisticRegression(max_iter=2000, class_weight="balanced").fit(Xtr, [GOLD[i][f] for i in tr])
            for i, p in zip(te, m.predict(Xte)): pred[i][f] = p
    return pred

maj = [None] * len(D)
for tr, te in FOLDS:
    mc = {f: collections.Counter(GOLD[i][f] for i in tr).most_common(1)[0][0] for f in FIELDS}
    for i in te: maj[i] = mc
show("majority class", score(maj, ALL))

t0 = time.time(); PRED = {"tfidf_lr": classical(FOLDS)}
show("TF-IDF + logistic regression", score(PRED["tfidf_lr"], ALL))
print(f"\n(all six fields, all five folds, in {time.time()-t0:.0f} s)")'''

C["random"] = r'''# ===========================================================================
#  CELL 8 — the split you cannot defend: shuffle the reports, ignore corridors.
# ===========================================================================
from sklearn.model_selection import KFold
shuffled = list(KFold(5, shuffle=True, random_state=0).split(ALL))
show("TF-IDF + LR, RANDOM split", score(classical(shuffled), ALL))
show("TF-IDF + LR, corridor split", SCORES["TF-IDF + logistic regression"])'''

C["model"] = r'''# ===========================================================================
#  CELL 9 — the small open model, the prompt, and a strict parser.
# ===========================================================================
from transformers import AutoTokenizer, AutoModelForCausalLM
MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"     # 494M parameters, Apache-2.0, about 1 GB download
tok = AutoTokenizer.from_pretrained(MODEL_ID)
def load_model():
    return AutoModelForCausalLM.from_pretrained(MODEL_ID, dtype=DTYPE).to(DEVICE).eval()
model = load_model()

SPEC = """Read the police crash narrative and fill in this JSON record. Use only these values:
crash_type: "left_turn" (a vehicle turning left), "angle" (vehicles on crossing paths, no left turn), "pedestrian_bicycle" (a pedestrian or cyclist was struck), or "other"
pedestrian: "yes" if a pedestrian was involved, else "no"
vehicles: "1", "2", or "3+" (motor vehicles involved)
injury: "yes" if anyone was injured or killed, else "no"
hit_and_run: "yes" if a driver left the scene, else "no"
distracted: "yes" if a driver was distracted or inattentive, else "no"
Answer with the JSON object only."""

def messages(text, shots=()):
    m = [{"role": "system", "content": SPEC}]
    for t, a in shots:                              # worked examples: a narrative and its answer
        m += [{"role": "user", "content": "Narrative:\n" + t}, {"role": "assistant", "content": a}]
    return m + [{"role": "user", "content": "Narrative:\n" + text}]

@torch.no_grad()
def generate(m, msgs, max_new=80):
    enc = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt",
                                  return_dict=True).to(DEVICE)
    out = m.generate(**enc, max_new_tokens=max_new, do_sample=False, pad_token_id=tok.eos_token_id)
    return tok.decode(out[0, enc["input_ids"].shape[1]:], skip_special_tokens=True)

def parse(s):
    """-> (record or None, parsed as JSON?, every field present with an allowed value?)"""
    mm = re.search(r"\{.*?\}", s, re.S)
    if not mm: return None, False, False
    try: d = json.loads(mm.group(0))
    except Exception: return None, False, False
    if not isinstance(d, dict): return None, False, False
    rec, ok = {}, True
    for f, (vals, _) in FIELDS.items():
        v = str(d.get(f, "")).strip().lower()
        v = {"true": "yes", "false": "no"}.get(v, v)
        if f == "vehicles" and v.isdigit(): v = "3+" if int(v) >= 3 else v
        if v not in vals: ok, v = False, None
        rec[f] = v
    return rec, True, ok

print(f"{sum(p.numel() for p in model.parameters()):,} parameters on {DEVICE}")
print("prompt tokens, system part only:", len(tok(SPEC)["input_ids"]))'''

C["config"] = r'''# ===========================================================================
#  CELL 10 — how much to run. The whole lab is 5 folds; one fold is a fair quick look.
# ===========================================================================
RUN_FOLDS = [0, 1, 2, 3, 4]      # set to [0] for a ~1/5-size run; every table then says which folds it covers
EVAL = np.concatenate([FOLDS[k][1] for k in RUN_FOLDS])
VALID, SECS = {}, {}

def run_prompting(name, shots_for):
    """shots_for(train_idx) -> function(i) returning the worked examples for test report i."""
    pred, ok_json, ok_schema, t0 = [None] * len(D), [], [], time.time()
    for k in RUN_FOLDS:
        tr, te = FOLDS[k]; pick = shots_for(tr)
        for i in te:
            rec, vj, vs = parse(generate(model, messages(TEXTS[i], pick(i))))
            pred[i] = rec; ok_json.append(vj); ok_schema.append(vs)
        print(f"  {name}: fold {k} done, {time.time()-t0:.0f} s")
    PRED[name], VALID[name], SECS[name] = pred, (np.mean(ok_json), np.mean(ok_schema)), (time.time()-t0)/len(EVAL)
    print(f"valid JSON {100*np.mean(ok_json):.1f}% · every field valid {100*np.mean(ok_schema):.1f}% · "
          f"{SECS[name]:.2f} s per narrative")
    show(name, score(pred, EVAL))
    show("TF-IDF + LR, same folds", score(PRED["tfidf_lr"], EVAL))'''

C["zero"] = r'''# ===========================================================================
#  CELL 11 — rung 1: zero-shot. The schema, the narrative, nothing else.
# ===========================================================================
run_prompting("zero-shot", lambda tr: (lambda i: ()))'''

C["fixed"] = r'''# ===========================================================================
#  CELL 12 — rung 1b: three fixed worked examples, the shortest training report of each main type.
# ===========================================================================
def fixed_shots(tr):
    shots = []
    for ct in ["left_turn", "angle", "pedestrian_bicycle"]:
        j = min([i for i in tr if GOLD[i]["crash_type"] == ct], key=lambda i: len(TEXTS[i]))
        shots.append((TEXTS[j], gold_json(j)))
    return lambda i: shots
run_prompting("few-shot, fixed 3", fixed_shots)'''

C["rag"] = r'''# ===========================================================================
#  CELL 13 — rung 2: retrieval. Three most similar TRAINING-corridor reports as the examples.
# ===========================================================================
def retrieved_shots(tr, k=3):
    tr = np.array(tr); v = tfidf(); X = v.fit_transform([TEXTS[i] for i in tr])   # fit on training corridors only
    def pick(i):
        sim = (X @ v.transform([TEXTS[i]]).T).toarray().ravel()
        top = tr[np.argsort(-sim)[:k]][::-1]                 # most similar sits nearest the question
        return [(TEXTS[j], gold_json(j)) for j in top]
    return pick
run_prompting("few-shot, retrieved 3", retrieved_shots)'''

C["leaky"] = r'''# ===========================================================================
#  CELL 14 (optional, ~same time as cell 13) — the leak: retrieve from EVERY other report,
#  including the test report's own corridor. Run it once, so you know what it looks like.
# ===========================================================================
def leaky_shots(tr, k=3):
    def pick(i):
        others = [j for j in range(len(D)) if j != i]
        return retrieved_shots(others, k)(i)
    return pick
run_prompting("retrieved 3, LEAKY", leaky_shots)'''

C["lora_def"] = r'''# ===========================================================================
#  CELL 15 — rung 3: LoRA. Freeze all 494M weights; learn a thin correction on the attention layers.
# ===========================================================================
from peft import LoraConfig, get_peft_model

def lora_train(train_idx, r=16, alpha=32, epochs=2, lr=1e-4, accum=4, seed=0):
    torch.manual_seed(seed); rng = np.random.default_rng(seed)
    pm = get_peft_model(load_model(), LoraConfig(r=r, lora_alpha=alpha, lora_dropout=0.05, task_type="CAUSAL_LM",
                                                 target_modules=["q_proj", "k_proj", "v_proj", "o_proj"]))
    params = [p for p in pm.parameters() if p.requires_grad]
    for p in params: p.data = p.data.float()     # the adapter itself always trains in fp32
    opt = torch.optim.AdamW(params, lr=lr)
    total = epochs * int(np.ceil(len(train_idx) / accum))
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1.0, (s + 1) / 10) * max(0.0, 1 - s / total))
    inner, losses = pm.base_model.model, []
    pm.train()
    for ep in range(epochs):
        order = rng.permutation(train_idx)
        for b in range(0, len(order), accum):
            for i in order[b:b + accum]:
                p = tok.apply_chat_template(messages(TEXTS[i]), add_generation_prompt=True, tokenize=False)
                pi = tok(p, add_special_tokens=False)["input_ids"]
                ai = tok(gold_json(i) + "<|im_end|>", add_special_tokens=False)["input_ids"]
                ids = torch.tensor([pi + ai], device=DEVICE)
                # The loss counts ONLY the answer tokens. We also project only those positions to the
                # 151,936-word vocabulary, which is what keeps this inside a free-tier memory budget.
                h = inner.model(input_ids=ids).last_hidden_state[:, len(pi) - 1:-1]
                loss = torch.nn.functional.cross_entropy(inner.lm_head(h).float()[0], ids[0, len(pi):])
                if not torch.isfinite(loss): continue      # guard: one bad step must not poison the adapter
                (loss / accum).backward(); losses.append(loss.item())
            if torch.isfinite(torch.nn.utils.clip_grad_norm_(params, 1.0)): opt.step()
            sched.step(); opt.zero_grad()
        print(f"    epoch {ep+1}: mean answer loss {np.mean(losses[-len(train_idx):]):.3f}")
    pm.print_trainable_parameters()
    return pm.eval()'''

C["lora_run"] = r'''# ===========================================================================
#  CELL 16 — train one adapter per fold on the four training folds, then answer the held-out fold
#  with the plain zero-shot prompt. No examples in the prompt: whatever it knows, it learned.
# ===========================================================================
pred, ok_json, ok_schema, t0 = [None] * len(D), [], [], time.time()
for k in RUN_FOLDS:
    tr, te = FOLDS[k]; print(f"fold {k}: training on {len(tr)} reports")
    pm = lora_train(list(tr))
    for i in te:
        rec, vj, vs = parse(generate(pm, messages(TEXTS[i])))
        pred[i] = rec; ok_json.append(vj); ok_schema.append(vs)
    del pm; print(f"  fold {k} done, {time.time()-t0:.0f} s so far")
PRED["LoRA"], VALID["LoRA"] = pred, (np.mean(ok_json), np.mean(ok_schema))
print(f"valid JSON {100*np.mean(ok_json):.1f}% · every field valid {100*np.mean(ok_schema):.1f}%")
show("LoRA", score(pred, EVAL))
show("TF-IDF + LR, same folds", score(PRED["tfidf_lr"], EVAL))'''

C["board"] = r'''# ===========================================================================
#  CELL 17 — one scoreboard, same folds for everyone.
# ===========================================================================
order = ["tfidf_lr", "zero-shot", "few-shot, fixed 3", "few-shot, retrieved 3", "retrieved 3, LEAKY", "LoRA"]
print(f"folds {RUN_FOLDS} · {len(EVAL)} test reports · F1 (macro-F1 for crash_type and vehicles)\n")
print(f"{'':24s}" + "".join(f"{f[:11]:>12s}" for f in list(FIELDS) + ["mean"]) + f"{'valid':>8s}")
for name in [o for o in order if o in PRED]:
    s = score(PRED[name], EVAL)
    v = f"{100*VALID[name][1]:7.0f}%" if name in VALID else "      —"
    print(f"{name[:24]:24s}" + "".join(f"{s[f]['F1']:12.3f}" for f in list(FIELDS) + ["mean"]) + v)'''

C["ugly"] = r'''# ===========================================================================
#  CELL 18 — the ugly cases, counted (no narrative text is printed).
# ===========================================================================
HR_RX = AUDIT["hit_and_run"][1]
hr = [i for i in EVAL if GOLD[i]["hit_and_run"] == "yes"]
said = [i for i in hr if re.search(HR_RX, TEXTS[i], re.I)]
silent = [i for i in hr if i not in said]
print(f"hit-and-run positives in these folds: {len(hr)} · narrative says so: {len(said)} · silent: {len(silent)}")
for name in [o for o in order if o in PRED]:
    rec = lambda ids: np.mean([(PRED[name][i] or {}).get("hit_and_run") == "yes" for i in ids]) if ids else float("nan")
    print(f"  {name[:24]:24s} recall when the narrative says so {rec(said):.2f} · when it is silent {rec(silent):.2f}")

print("\ncrash_type confusions (gold -> predicted), counts:")
for name in [o for o in order if o in PRED]:
    c = collections.Counter((GOLD[i]["crash_type"], (PRED[name][i] or {}).get("crash_type") or "invalid")
                            for i in EVAL)
    worst = [(f"{g}->{p}", n) for (g, p), n in c.most_common() if g != p][:4]
    print(f"  {name[:24]:24s}", worst)'''

C["peek"] = r'''# ===========================================================================
#  CELL 19 (optional) — read ONE disagreement yourself. Clear this output before sharing the notebook.
# ===========================================================================
SHOW = False                                   # set True on your own machine only
name = "LoRA" if "LoRA" in PRED else "few-shot, retrieved 3"
wrong = [i for i in EVAL if (PRED[name][i] or {}).get("crash_type") != GOLD[i]["crash_type"]]
print(f"{len(wrong)} crash_type misses for {name}")
if SHOW and wrong:
    i = wrong[0]
    print("gold:", GOLD[i]["crash_type"], "· predicted:", (PRED[name][i] or {}).get("crash_type"))
    print(TEXTS[i][:300], "...")'''
