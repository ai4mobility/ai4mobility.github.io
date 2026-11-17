"""Model loading, generation, retrieval and LoRA training (mirrored in the notebook)."""
import time, torch, numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import AutoTokenizer, AutoModelForCausalLM
from common import TEXTS, GOLD, messages, gold_json

MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DTYPE = torch.float32 if DEVICE == "cuda" else torch.bfloat16   # T4 has no fast bf16; CPU with AVX512-BF16 does
MAX_NEW = 80

def load(model_id=MODEL_ID):
    tok = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id, dtype=DTYPE).to(DEVICE).eval()
    return tok, model

@torch.no_grad()
def generate(tok, model, msgs):
    enc = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt", return_dict=True).to(DEVICE)
    out = model.generate(**enc, max_new_tokens=MAX_NEW, do_sample=False, pad_token_id=tok.eos_token_id)
    return tok.decode(out[0, enc["input_ids"].shape[1]:], skip_special_tokens=True)

def fixed_shots(train_idx):
    """One shortest training example per main crash type: the same 3 shots for every test narrative in the fold."""
    shots = []
    for ct in ["left_turn", "angle", "pedestrian_bicycle"]:
        c = [i for i in train_idx if GOLD[i]["crash_type"] == ct]
        j = min(c, key=lambda i: len(TEXTS[i]))
        shots.append((TEXTS[j], gold_json(j)))
    return shots

class Retriever:
    """TF-IDF nearest neighbours, fit on TRAINING corridors only."""
    def __init__(self, train_idx):
        self.idx = np.array(train_idx)
        self.v = TfidfVectorizer(stop_words="english", sublinear_tf=True, min_df=2, ngram_range=(1, 2))
        self.X = self.v.fit_transform([TEXTS[i] for i in train_idx])
    def shots(self, text, k=3):
        s = (self.X @ self.v.transform([text]).T).toarray().ravel()
        top = self.idx[np.argsort(-s)[:k]][::-1]        # most similar example sits closest to the question
        return [(TEXTS[j], gold_json(j)) for j in top]

def lora_train(tok, model, train_idx, r=16, alpha=32, epochs=2, lr=1e-4, accum=4, seed=0, log=print):
    from peft import LoraConfig, get_peft_model
    torch.manual_seed(seed); rng = np.random.default_rng(seed)
    cfg = LoraConfig(r=r, lora_alpha=alpha, lora_dropout=0.05, task_type="CAUSAL_LM",
                     target_modules=["q_proj", "k_proj", "v_proj", "o_proj"])
    pm = get_peft_model(model, cfg)
    params = [p for p in pm.parameters() if p.requires_grad]
    for p in params: p.data = p.data.float()          # keep the small adapter in fp32 even when the base is bf16
    skipped = 0
    opt = torch.optim.AdamW(params, lr=lr, weight_decay=0.0)
    total = epochs * int(np.ceil(len(train_idx) / accum))
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1.0, (s + 1) / 10) * max(0.0, 1 - s / total))
    pm.train(); step = 0; t0 = time.time(); losses = []
    inner = pm.base_model.model                       # the Qwen2ForCausalLM with LoRA layers inside
    for ep in range(epochs):
        order = rng.permutation(train_idx)
        for b in range(0, len(order), accum):
            for i in order[b:b + accum]:
                p = tok.apply_chat_template(messages(TEXTS[i]), add_generation_prompt=True, tokenize=False)
                pi = tok(p, add_special_tokens=False)["input_ids"]
                ai = tok(gold_json(i) + "<|im_end|>", add_special_tokens=False)["input_ids"]
                ids = torch.tensor([pi + ai], device=DEVICE)
                # loss on the answer tokens only; project only those hidden states to the vocabulary
                h = inner.model(input_ids=ids).last_hidden_state[:, len(pi) - 1:-1]
                loss = torch.nn.functional.cross_entropy(inner.lm_head(h).float()[0], ids[0, len(pi):])
                if not torch.isfinite(loss): skipped += 1; continue   # guard: one bad example must not poison the adapter
                (loss / accum).backward(); losses.append(loss.item())
            gn = torch.nn.utils.clip_grad_norm_(params, 1.0)
            if torch.isfinite(gn): opt.step()
            else: skipped += 1
            sched.step(); opt.zero_grad(); step += 1
            if step % 20 == 0: log(f"  epoch {ep+1} step {step}/{total} loss {np.mean(losses[-80:]):.3f} {time.time()-t0:.0f}s skipped {skipped}")
    pm.eval()
    pm.skipped = skipped
    return pm, time.time() - t0, float(np.mean(losses[-80:]))
