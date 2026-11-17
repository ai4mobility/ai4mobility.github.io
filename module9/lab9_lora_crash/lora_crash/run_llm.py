"""Prompting methods over all 5 corridor folds. Writes preds_<method>.jsonl (predictions only, no narrative text)."""
import json, sys, time, os, torch
torch.set_num_threads(8)
from common import FOLDS, TEXTS, messages, parse
from llm_core import load, generate, fixed_shots, Retriever
methods = sys.argv[1].split(",")
tok, model = load()
for meth in methods:
    fn = f"preds_{meth}.jsonl"; done = set()
    if os.path.exists(fn): done = {json.loads(l)["i"] for l in open(fn)}
    f = open(fn, "a")
    for k, (tr, te) in enumerate(FOLDS):
        shots = fixed_shots(tr) if meth == "fixed3" else None
        ret = Retriever(tr) if meth == "rag3" else None
        if meth == "rag3_leaky":   # the WRONG way, for the split section: neighbours from every other narrative
            import numpy as np; ret = None
        for i in te:
            if int(i) in done: continue
            if meth == "rag3_leaky":
                s = Retriever([j for j in range(len(TEXTS)) if j != i]).shots(TEXTS[i])
            else:
                s = shots if meth == "fixed3" else (ret.shots(TEXTS[i]) if meth == "rag3" else ())
            t0 = time.time(); out = generate(tok, model, messages(TEXTS[i], s)); dt = time.time() - t0
            rec, vj, vs = parse(out)
            f.write(json.dumps({"i": int(i), "fold": k, "pred": rec, "valid_json": vj, "valid_schema": vs,
                                "sec": round(dt, 2), "raw": out}) + "\n"); f.flush()
        print(meth, "fold", k, "done", flush=True)
