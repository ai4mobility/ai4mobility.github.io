"""LoRA per corridor fold: train on 4 folds, decode the held-out fold zero-shot. Writes preds_lora.jsonl."""
import json, sys, time, os, torch
torch.set_num_threads(8)
from common import FOLDS, TEXTS, messages, parse
from llm_core import load, generate, lora_train
fn = "preds_lora.jsonl"; meta = "lora_meta.json"
done_folds = set(json.loads(l)["fold"] for l in open(fn)) if os.path.exists(fn) else set()
M = json.load(open(meta)) if os.path.exists(meta) else {}
for k, (tr, te) in enumerate(FOLDS):
    if k in done_folds: continue
    tok, model = load()
    pm, train_s, last_loss = lora_train(tok, model, list(tr), log=lambda s: print(f"fold {k}", s, flush=True))
    t0 = time.time(); rows = []
    for i in te:
        out = generate(tok, pm, messages(TEXTS[i])); rec, vj, vs = parse(out)
        rows.append({"i": int(i), "fold": k, "pred": rec, "valid_json": vj, "valid_schema": vs, "raw": out})
    with open(fn, "a") as f:
        for r in rows: f.write(json.dumps(r) + "\n")
    M[str(k)] = {"train_seconds": round(train_s, 1), "infer_seconds": round(time.time() - t0, 1),
                 "n_train": len(tr), "n_test": len(te), "final_train_loss": round(last_loss, 4), "skipped": pm.skipped}
    json.dump(M, open(meta, "w"), indent=1); print("fold", k, M[str(k)], flush=True)
    del pm, model; import gc; gc.collect()
