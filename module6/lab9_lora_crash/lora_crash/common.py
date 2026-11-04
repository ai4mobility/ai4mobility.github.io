"""Shared definitions for the M6 LoRA crash-narrative lab reproducer.
The notebook copies these definitions verbatim; keep them in sync."""
import json, re, numpy as np
from sklearn.model_selection import GroupKFold

D = json.load(open("crash_narratives_joined.json"))
TEXTS = [r["text"] for r in D]
GROUPS = np.array([r["corridor"] for r in D])

def crash_type(r):
    t = r["S4_CRASH_TYPE_SIMPLIFIED"]
    return {"Left Turn": "left_turn", "Angle": "angle",
            "Pedestrian": "pedestrian_bicycle", "Bicycle": "pedestrian_bicycle"}.get(t, "other")

def vehicles(r):
    n = int(r["TOTAL_NUMBER_OF_VEHICLES"]); return "3+" if n >= 3 else str(n)

yn = lambda b: "yes" if b else "no"
FIELDS = {   # field -> (allowed values, how it is read off the coded record)
 "crash_type":  (["left_turn", "angle", "pedestrian_bicycle", "other"], crash_type),
 "pedestrian":  (["yes", "no"], lambda r: yn(r["S4_IS_PEDESTRIAN_INVOLVED"] == "Y")),
 "vehicles":    (["1", "2", "3+"], vehicles),
 "injury":      (["yes", "no"], lambda r: yn(r["S4_CRASH_SEVERITY"] != "No Injury")),
 "hit_and_run": (["yes", "no"], lambda r: yn(r["S4_IS_HIT_AND_RUN"] == "Y")),
 "distracted":  (["yes", "no"], lambda r: yn(r["S4_IS_DISTRACTED"] == "Y")),
}
GOLD = [{f: fn(r) for f, (_, fn) in FIELDS.items()} for r in D]

FOLDS = list(GroupKFold(n_splits=5).split(np.arange(len(D)), None, GROUPS))

SPEC = """Read the police crash narrative and fill in this JSON record. Use only these values:
crash_type: "left_turn" (a vehicle turning left), "angle" (vehicles on crossing paths, no left turn), "pedestrian_bicycle" (a pedestrian or cyclist was struck), or "other"
pedestrian: "yes" if a pedestrian was involved, else "no"
vehicles: "1", "2", or "3+" (motor vehicles involved)
injury: "yes" if anyone was injured or killed, else "no"
hit_and_run: "yes" if a driver left the scene, else "no"
distracted: "yes" if a driver was distracted or inattentive, else "no"
Answer with the JSON object only."""

def gold_json(i):
    return json.dumps(GOLD[i])

def messages(text, shots=()):
    """shots: list of (narrative, json_string) pairs shown before the question."""
    m = [{"role": "system", "content": SPEC}]
    for t, a in shots:
        m += [{"role": "user", "content": "Narrative:\n" + t}, {"role": "assistant", "content": a}]
    m.append({"role": "user", "content": "Narrative:\n" + text})
    return m

def parse(s):
    """Return (record or None, valid_json, valid_schema)."""
    mm = re.search(r"\{.*?\}", s, re.S)
    if not mm: return None, False, False
    try: d = json.loads(mm.group(0))
    except Exception: return None, False, False
    if not isinstance(d, dict): return None, False, False
    rec = {}
    ok = True
    for f, (vals, _) in FIELDS.items():
        v = str(d.get(f, "")).strip().lower()
        if v in ("true",): v = "yes"
        if v in ("false",): v = "no"
        if f == "vehicles" and v.isdigit(): v = "3+" if int(v) >= 3 else v
        if v not in vals: ok = False; v = None
        rec[f] = v
    return rec, True, ok

def score(preds, idx=None):
    """preds: list aligned with D (None where not predicted). Missing/invalid values count as wrong."""
    from sklearn.metrics import f1_score, precision_score, recall_score
    idx = list(range(len(D))) if idx is None else list(idx)
    out = {}
    for f, (vals, _) in FIELDS.items():
        g = [GOLD[i][f] for i in idx]
        p = [(preds[i] or {}).get(f) or "__missing__" for i in idx]
        acc = float(np.mean([a == b for a, b in zip(g, p)]))
        if vals == ["yes", "no"]:
            gy = [x == "yes" for x in g]; py = [x == "yes" for x in p]
            out[f] = {"acc": round(acc, 3), "F1": round(float(f1_score(gy, py, zero_division=0)), 3),
                      "P": round(float(precision_score(gy, py, zero_division=0)), 3),
                      "R": round(float(recall_score(gy, py, zero_division=0)), 3)}
        else:
            out[f] = {"acc": round(acc, 3),
                      "macroF1": round(float(f1_score(g, p, labels=vals, average="macro", zero_division=0)), 3)}
    return out
