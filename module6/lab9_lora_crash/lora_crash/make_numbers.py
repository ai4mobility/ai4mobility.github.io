"""Collect every number the notebook quotes into numbers.json. Methods that were not run are simply absent,
so the builder fails loudly instead of quoting a stale or invented value."""
import json, os, collections, platform, numpy as np, torch, transformers, peft, sklearn
from common import D, GOLD, FIELDS, FOLDS, score

B = json.load(open("results_baseline.json"))
G = json.load(open("../inputs/M2_Transformers_LLMs_Multimodal/Tokens_BERT_GPT/crash_bert_experiments/results_g.json"))
N = {"corpus": {k: B[k] for k in ["n", "n_corridors", "fold_sizes", "label_counts"]},
     "availability": B["availability"],
     "majority": B["majority"], "tfidf_lr": B["tfidf_lr"], "tfidf_lr_seconds": B["tfidf_lr_seconds"],
     "tfidf_lr_left_turn_AP": B["tfidf_lr_left_turn_AP"],
     "tfidf_lr_random_split": B.get("tfidf_lr_random_split"), "tfidf_lr_per_fold": B.get("tfidf_lr_per_fold"),
     "distilbert_g": {t: {k: G[t][k] for k in ["AP", "F1", "P", "R", "base_rate", "minutes"]} for t in ["distracted", "pedestrian"]},
     "site_2_13": {"distracted_tfidf_AP_quoted": 0.619, "distilbert_distracted_AP_quoted": 0.488,
                   "note": "quoted from the published 2.13 page; recomputed here as tfidf_lr.distracted.AP"},
     "runtime": {"device": "CPU only (no GPU on the build machine), 8 threads, bfloat16",
                 "python": platform.python_version(), "torch": torch.__version__,
                 "transformers": transformers.__version__, "peft": peft.__version__, "sklearn": sklearn.__version__,
                 "model": "Qwen/Qwen2.5-0.5B-Instruct", "max_new_tokens": 80, "decoding": "greedy",
                 "t4_tested": False},
     "methods": {}}

def load(fn):
    return [json.loads(l) for l in open(fn)] if os.path.exists(fn) else []

for m in ["zero", "fixed3", "rag3", "rag3_leaky", "lora"]:
    rows = load(f"preds_{m}.jsonl")
    if len(rows) != len(D):
        print(m, "incomplete:", len(rows), "/", len(D))
        if m == "lora" and rows and os.path.exists("lora_meta.json"):
            # partial run: score only the folds that finished, next to the other methods on the SAME reports
            meta = json.load(open("lora_meta.json")); done = sorted(int(k) for k in meta)
            idx = [i for k in done for i in FOLDS[k][1]]
            lp = [None] * len(D)
            for r in rows: lp[r["i"]] = r["pred"] if r["valid_json"] else None
            same = {"lora": score(lp, idx)}
            for mm in ["fixed3", "rag3"]:
                rr = load(f"preds_{mm}.jsonl"); pp = [None] * len(D)
                for r in rr: pp[r["i"]] = r["pred"] if r["valid_json"] else None
                same[mm] = score(pp, idx)
            tfp = json.load(open("results_baseline.json"))
            N["lora_partial"] = {"folds_done": done, "n_scored": len(idx), "fold_meta": meta,
                                 "scores_same_reports": same,
                                 "tfidf_lr_per_fold": [tfp["tfidf_lr_per_fold"][k] for k in done],
                                 "schema_valid": round(float(np.mean([r["valid_schema"] for r in rows])), 3),
                                 "pred_dist": {f: dict(collections.Counter(str((r["pred"] or {}).get(f)) for r in rows).most_common()) for f in FIELDS}}
        continue
    preds = [None] * len(D)
    for r in rows: preds[r["i"]] = r["pred"] if r["valid_json"] else None
    e = {"n_scored": len(rows), "scores": score(preds),
         "json_valid": round(float(np.mean([r["valid_json"] for r in rows])), 3),
         "schema_valid": round(float(np.mean([r["valid_schema"] for r in rows])), 3),
         "per_fold": [score(preds, te) for _, te in FOLDS]}
    if "sec" in rows[0]:
        e["sec_per_narrative"] = round(float(np.mean([r["sec"] for r in rows])), 2)
        e["total_minutes"] = round(sum(r["sec"] for r in rows) / 60, 1)
    # failure anatomy, aggregate only
    bad = collections.Counter()
    for r in rows:
        if not r["valid_json"]: bad["no_parseable_json"] += 1
        elif not r["valid_schema"]:
            for f, v in (r["pred"] or {}).items():
                if v is None: bad[f"bad_or_missing_{f}"] += 1
    e["schema_failures"] = dict(bad)
    e["pred_dist"] = {f: dict(collections.Counter(str((r["pred"] or {}).get(f)) for r in rows).most_common()) for f in FIELDS}
    # crash_type confusion
    cm = collections.Counter((GOLD[r["i"]]["crash_type"], (r["pred"] or {}).get("crash_type") or "invalid") for r in rows)
    e["crash_type_confusion"] = {f"{g}->{p}": c for (g, p), c in sorted(cm.items())}
    N["methods"][m] = e
    if m == "lora":
        meta = json.load(open("lora_meta.json"))
        e["fold_meta"] = meta
        e["train_minutes_total"] = round(sum(v["train_seconds"] for v in meta.values()) / 60, 1)
        e["infer_minutes_total"] = round(sum(v["infer_seconds"] for v in meta.values()) / 60, 1)
        e["sec_per_narrative"] = round(sum(v["infer_seconds"] for v in meta.values()) / len(D), 2)
        e["config"] = {"r": 16, "alpha": 32, "dropout": 0.05, "targets": "q,k,v,o", "epochs": 2, "lr": 1e-4, "adapter_dtype": "fp32", "first_attempt_note": "lr 2e-4 with bf16 adapter diverged to NaN at step ~80 of fold 0 on CPU; restarted",
                       "grad_accum": 4, "trainable_params": 2162688, "total_params": 496195456}

# tfidf crash_type confusion + hit-and-run misses split by whether the narrative mentions leaving
import re
from common import TEXTS
rx = r"fled|left the scene|leave the scene|unknown (?:vehicle|driver)|did not stop|failed to remain"
hr = [i for i in range(len(D)) if GOLD[i]["hit_and_run"] == "yes"]
N["hit_and_run_mentioned"] = {"positives": len(hr), "mentioned": sum(bool(re.search(rx, TEXTS[i], re.I)) for i in hr)}
for m in N["methods"]:
    rows = {r["i"]: r for r in load(f"preds_{m}.jsonl")}
    N["methods"][m]["hit_and_run_recall_by_mention"] = {
        k: round(float(np.mean([((rows[i]["pred"] or {}).get("hit_and_run") == "yes") for i in hr
                                 if bool(re.search(rx, TEXTS[i], re.I)) == want])), 3)
        for k, want in [("mentioned", True), ("not_mentioned", False)]}
json.dump(N, open("numbers.json", "w"), indent=1)
print("methods in numbers.json:", list(N["methods"]))
