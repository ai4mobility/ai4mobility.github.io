"""Classical baseline (the 2.13 winner), majority class, and the availability audit."""
import json, re, time, numpy as np, collections
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score
from common import D, TEXTS, GOLD, FIELDS, FOLDS, score

out = {"n": len(D), "n_corridors": len(set(r["corridor"] for r in D)),
       "fold_sizes": [len(te) for _, te in FOLDS],
       "label_counts": {f: dict(collections.Counter(g[f] for g in GOLD)) for f in FIELDS}}

# majority class, fit per training fold
maj = [None]*len(D)
for tr, te in FOLDS:
    m = {f: collections.Counter(GOLD[i][f] for i in tr).most_common(1)[0][0] for f in FIELDS}
    for i in te: maj[i] = dict(m)
out["majority"] = score(maj)

# TF-IDF + logistic regression, one model per field, same settings as stage_c_classify.py
t0 = time.time()
pred = [dict() for _ in D]; prob_yes = {f: np.zeros(len(D)) for f in FIELDS}
for tr, te in FOLDS:
    v = TfidfVectorizer(stop_words="english", sublinear_tf=True, min_df=2, ngram_range=(1, 2))
    Xtr = v.fit_transform([TEXTS[i] for i in tr]); Xte = v.transform([TEXTS[i] for i in te])
    for f in FIELDS:
        ytr = [GOLD[i][f] for i in tr]
        m = LogisticRegression(max_iter=2000, class_weight="balanced", C=1.0).fit(Xtr, ytr)
        p = m.predict(Xte)
        for i, pi in zip(te, p): pred[i][f] = pi
        if "yes" in m.classes_:
            prob_yes[f][te] = m.predict_proba(Xte)[:, list(m.classes_).index("yes")]
out["tfidf_lr"] = score(pred)
out["tfidf_lr_seconds"] = round(time.time() - t0, 2)
for f, (vals, _) in FIELDS.items():
    if vals == ["yes", "no"]:
        y = np.array([GOLD[i][f] == "yes" for i in range(len(D))])
        out["tfidf_lr"][f]["AP"] = round(float(average_precision_score(y, prob_yes[f])), 3)

# same targets as 2.13 (stage_c), to tie back: left_turn is crash_type == left_turn
y_lt = np.array([GOLD[i]["crash_type"] == "left_turn" for i in range(len(D))]).astype(int)
plt_ = np.zeros(len(D))
for tr, te in FOLDS:
    v = TfidfVectorizer(stop_words="english", sublinear_tf=True, min_df=2, ngram_range=(1, 2))
    Xtr = v.fit_transform([TEXTS[i] for i in tr]); Xte = v.transform([TEXTS[i] for i in te])
    plt_[te] = LogisticRegression(max_iter=2000, class_weight="balanced").fit(Xtr, y_lt[tr]).predict_proba(Xte)[:, 1]
out["tfidf_lr_left_turn_AP"] = round(float(average_precision_score(y_lt, plt_)), 3)

# availability audit: is the field even written in the narrative?
AUD = {
 "weather_rain": (lambda r: r["WEATHER_CONDITION"] == "Rain", r"rain|wet|shower|storm|drizzl|downpour"),
 "light_dark":   (lambda r: r["LIGHT_CONDITION"].startswith("Dark"), r"\bdark|night|street ?light|headlight|lighting"),
 "surface_wet":  (lambda r: r["ROAD_SURFACE_CONDITION"] == "Wet", r"\bwet|rain|slick|hydroplan|standing water"),
 "alcohol":      (lambda r: r["S4_IS_ALCOHOL_RELATED"] == "Y", r"alcohol|impair|\bDUI|\bBAC\b|breath|intoxicat|beer|drunk|sobriety"),
 "hit_and_run":  (lambda r: r["S4_IS_HIT_AND_RUN"] == "Y", r"fled|left the scene|leave the scene|unknown (?:vehicle|driver)|did not stop|failed to remain"),
 "pedestrian":   (lambda r: r["S4_IS_PEDESTRIAN_INVOLVED"] == "Y", r"pedestrian|non-?motorist|NM ?0?\d|walking|crosswalk"),
}
out["availability"] = {}
for k, (pos, rx) in AUD.items():
    P = [r for r in D if pos(r)]
    hit = sum(1 for r in P if re.search(rx, r["text"], re.I))
    out["availability"][k] = {"coded_positive": len(P), "positive_mentioning": hit,
        "ceiling_pct": round(100 * hit / max(1, len(P)), 1),
        "any_narrative_mentioning": sum(1 for r in D if re.search(rx, r["text"], re.I))}
json.dump(out, open("results_baseline.json", "w"), indent=1)
print(json.dumps({k: out[k] for k in ["majority", "tfidf_lr", "tfidf_lr_left_turn_AP", "availability"]}, indent=1))

# the split you cannot defend: shuffled 5-fold, same model
from sklearn.model_selection import KFold
pr = [dict() for _ in D]
for tr, te in KFold(5, shuffle=True, random_state=0).split(np.arange(len(D))):
    v = TfidfVectorizer(stop_words="english", sublinear_tf=True, min_df=2, ngram_range=(1, 2))
    Xtr = v.fit_transform([TEXTS[i] for i in tr]); Xte = v.transform([TEXTS[i] for i in te])
    for f in FIELDS:
        p = LogisticRegression(max_iter=2000, class_weight="balanced").fit(Xtr, [GOLD[i][f] for i in tr]).predict(Xte)
        for i, pi in zip(te, p): pr[i][f] = pi
out["tfidf_lr_random_split"] = score(pr)
# per-fold spread of the corridor split
out["tfidf_lr_per_fold"] = [score(pred, te) for _, te in FOLDS]
json.dump(out, open("results_baseline.json", "w"), indent=1)
print("random split", json.dumps(out["tfidf_lr_random_split"]))
