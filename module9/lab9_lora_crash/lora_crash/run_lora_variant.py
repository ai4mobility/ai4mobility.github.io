"""Exploratory: one LoRA variant on ONE fold, plus a train-side check.
Usage: python run_lora_variant.py TAG FOLD EPOCHS LR
Writes preds_lora_<TAG>.jsonl (held-out fold) and lora_<TAG>_meta.json, including predictions on
40 of the fold's own TRAINING reports, so under- vs over-fitting is diagnosed without the test fold."""
import json, sys, time, os, torch
torch.set_num_threads(8)
import numpy as np
from common import FOLDS, TEXTS, messages, parse, score
from llm_core import load, generate, lora_train
tag, k, ep, lr = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
tr, te = FOLDS[k]
tok, model = load()
pm, train_s, last_loss = lora_train(tok, model, list(tr), epochs=ep, lr=lr, log=lambda s: print(f"{tag} fold {k}", s, flush=True))
rng = np.random.default_rng(1); chk = sorted(rng.choice(list(tr), 40, replace=False).tolist())
tp = {}
for i in chk:
    rec, vj, vs = parse(generate(tok, pm, messages(TEXTS[i]))); tp[int(i)] = rec
json.dump({"train_check_scores": score(tp, chk)}, open(f"lora_{tag}_traincheck.json", "w"), indent=1)
print("train-side check", score(tp, chk), flush=True)
t0 = time.time()
with open(f"preds_lora_{tag}.jsonl", "w") as f:
    for i in te:
        out = generate(tok, pm, messages(TEXTS[i])); rec, vj, vs = parse(out)
        f.write(json.dumps({"i": int(i), "fold": k, "pred": rec, "valid_json": vj, "valid_schema": vs}) + "\n"); f.flush()
json.dump({"fold": k, "epochs": ep, "lr": lr, "train_seconds": round(train_s, 1), "infer_seconds": round(time.time() - t0, 1),
           "final_train_loss": round(last_loss, 4), "skipped": pm.skipped, "train_check": chk},
          open(f"lora_{tag}_meta.json", "w"), indent=1)
print("done", flush=True)
