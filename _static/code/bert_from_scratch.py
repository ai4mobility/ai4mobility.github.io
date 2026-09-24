#!/usr/bin/env python3
"""
AI for Mobility - a BERT you can read, line by line.

WHAT THIS IS
    The sequel to gpt_from_scratch.py.  Same corpus, same tokenizer idea, same
    attention function, same block - and four edits that turn a GPT into a BERT:

      EDIT 1  the causal mask goes.  Every token may read every other token, left
              AND right.  The only mask left hides [PAD] slots.        (section 3)
      EDIT 2  a third embedding table - the SEGMENT table - is added to the token
              and position tables, so the model knows which of two text spans a
              token belongs to.                                        (section 5)
      EDIT 3  the training pair changes.  GPT's label was "the next word".  BERT's
              labels are (a) the words we hid, and (b) whether span B really
              followed span A.                                         (section 6)
      EDIT 4  two heads on top: a masked-word head that scores all V words at
              every hidden slot, and a 2-way next-sentence head that reads only
              the [CLS] slot.                                          (section 5)

    Nothing else changes.  If you understood the GPT file you already understand
    ninety percent of this one.

WHAT IT READS
    The same 42,956 NHTSA complaint narratives as gpt_from_scratch.py (ADAS,
    braking, steering, lighting ...), lowercased, punctuation and digits stripped.
    Narratives that also appear in the 4,200-complaint component dataset used for
    fine-tuning are REMOVED first, so no fine-tuning test complaint was ever seen
    during pretraining - not even unlabelled.

HOW TO RUN IT
    python3 bert_from_scratch.py --train                   # MLM + NSP pretraining
    python3 bert_from_scratch.py --train --no-nsp          # MLM only (the RoBERTa recipe)
    python3 bert_from_scratch.py --train --nsp-weight 0.1  # NSP counted at a tenth
    python3 bert_from_scratch.py --fill "the car [MASK] hard when the light turned red" --no-nsp
                    # fill blanks with the MLM-only checkpoint; drop --no-nsp to use MLM + NSP
    Add --max-seconds 150 to pause a run and resume it on the next call.

Hao Zhou, CGN 6933 AI for Mobility, University of South Florida.
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
import random
import re
import time
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

HERE = Path(__file__).resolve().parent

_CORPUS_NAME = "nhtsa_adas_complaints.txt.gz"
_HOLDOUT_NAME = "nhtsa_component_complaints.jsonl.gz"


def _find(name):
    cands = [HERE / name, HERE / "Labs" / "data" / name, HERE / "data" / name,
             HERE.parent / "data" / name]
    return next((p for p in cands if p.exists()), cands[0])


CORPUS, HOLDOUT = _find(_CORPUS_NAME), _find(_HOLDOUT_NAME)


def ckpt_path(nsp: bool, nsp_weight: float = 1.0) -> Path:
    if nsp and nsp_weight != 1.0:
        return HERE / f"bert_from_scratch_nspw{nsp_weight:g}.pt"
    return HERE / ("bert_from_scratch.pt" if nsp else "bert_from_scratch_mlm_only.pt")


# ---------------------------------------------------------------------------
# 0.  Configuration - identical to the GPT file's "small" size, plus one field
# ---------------------------------------------------------------------------

@dataclass
class Config:
    vocab_size: int = 6000      # V
    block_size: int = 64        # T  - [CLS] A [SEP] B [SEP] must fit in 64 slots
    n_layer: int = 4            # L
    n_head: int = 4             # H
    d_model: int = 128          # D
    d_ff: int = 512             # 4D
    n_segments: int = 2         # NEW: segment A or segment B
    dropout: float = 0.1

    @property
    def d_head(self) -> int:
        assert self.d_model % self.n_head == 0
        return self.d_model // self.n_head


# ---------------------------------------------------------------------------
# 1.  The tokenizer - whole words, plus BERT's five special tokens
# ---------------------------------------------------------------------------
# [PAD]  fills unused slots so a batch is rectangular.  Attention never reads it.
# [UNK]  any word outside the 6,000 most frequent.
# [CLS]  always slot 0.  Its final vector is what the next-sentence head reads,
#        and later what a classification head reads.  It has no meaning of its
#        own - it is a seat reserved for "a summary of the whole input".
# [SEP]  closes span A and closes span B.
# [MASK] the blank in fill-in-the-blank.  It exists only during pretraining.

PAD, UNK, CLS, SEP, MASK = "[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"
SPECIALS = [PAD, UNK, CLS, SEP, MASK]


def normalise(text: str) -> str:
    """Same treatment as the ADAS corpus: lowercase, letters only."""
    return " ".join(re.findall(r"[a-z]+", text.lower()))


class WordTokenizer:
    def __init__(self, itos):
        self.itos = list(itos)
        self.stoi = {s: i for i, s in enumerate(self.itos)}
        self.pad_id, self.unk_id, self.cls_id, self.sep_id, self.mask_id = \
            (self.stoi[s] for s in SPECIALS)

    @property
    def vocab_size(self):
        return len(self.itos)

    @classmethod
    def fit(cls, docs, vocab_size):
        counts = {}
        for d in docs:
            for w in d.split():
                counts[w] = counts.get(w, 0) + 1
        ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        return cls(SPECIALS + [w for w, _ in ranked[: vocab_size - len(SPECIALS)]])

    def encode(self, text):
        out = []
        for w in text.split():
            out.append(self.mask_id if w == MASK.lower() or w == MASK
                       else self.stoi.get(w, self.unk_id))
        return out

    def decode(self, ids):
        return " ".join(self.itos[int(i)] for i in ids)


def load_corpus(seed: int = 0):
    """Deduplicate, drop anything in the fine-tuning dataset, split by document."""
    with gzip.open(CORPUS, "rt", encoding="utf-8", errors="ignore") as fh:
        raw = [ln.strip() for ln in fh if ln.strip()]
    held = set()
    if HOLDOUT.exists():
        with gzip.open(HOLDOUT, "rt", encoding="utf-8") as fh:
            for ln in fh:
                held.add(normalise(json.loads(ln)["text"]))
    seen, docs, n_held = set(), [], 0
    for line in raw:
        key = normalise(line)
        if not key or key in seen:
            continue
        seen.add(key)
        if key in held:
            n_held += 1
            continue
        docs.append(key)
    rng = random.Random(seed)
    rng.shuffle(docs)
    n_val = max(1, int(0.10 * len(docs)))
    stats = dict(raw_lines=len(raw), unique=len(seen), removed_overlap=n_held,
                 kept=len(docs), n_val=n_val, n_train=len(docs) - n_val)
    return docs[n_val:], docs[:n_val], stats


# ---------------------------------------------------------------------------
# 2.  Softmax - unchanged from the GPT file
# ---------------------------------------------------------------------------

def softmax(scores, dim=-1):
    m = scores.max(dim=dim, keepdim=True).values
    e = torch.exp(scores - m)
    return e / e.sum(dim=dim, keepdim=True)


# ---------------------------------------------------------------------------
# 3.  Attention - unchanged, except for WHICH mask it is handed   (EDIT 1)
# ---------------------------------------------------------------------------
# GPT handed this function a lower-triangular mask: token i may read 0..i.
# BERT hands it a padding mask: token i may read every slot that holds a real
# token, on BOTH sides.  That one change is what "Bidirectional" in the name
# means - and it is why BERT cannot be trained on "predict the next word": with
# the whole sentence visible, the next word is sitting right there in the input.

def scaled_dot_product_attention(q, k, v, mask=None, dropout=None, return_weights=False):
    d_head = q.size(-1)
    scores = q @ k.transpose(-2, -1) / math.sqrt(d_head)     # (B,H,T,T)
    if mask is not None:
        scores = scores.masked_fill(~mask, float("-inf"))
    weights = softmax(scores, dim=-1)
    if dropout is not None:
        weights = dropout(weights)
    out = weights @ v
    return (out, weights) if return_weights else (out, None)


class MultiHeadSelfAttention(nn.Module):
    def __init__(self, cfg: Config):
        super().__init__()
        self.cfg = cfg
        self.W_q = nn.Linear(cfg.d_model, cfg.d_model, bias=False)
        self.W_k = nn.Linear(cfg.d_model, cfg.d_model, bias=False)
        self.W_v = nn.Linear(cfg.d_model, cfg.d_model, bias=False)
        self.W_o = nn.Linear(cfg.d_model, cfg.d_model, bias=False)
        self.attn_drop = nn.Dropout(cfg.dropout)
        self.resid_drop = nn.Dropout(cfg.dropout)
        # GPT registered a causal_mask buffer here.  BERT has none.   <- EDIT 1
        self.last_weights = None

    def forward(self, x, pad_mask, keep_weights=False):
        B, T, D = x.shape
        H, dh = self.cfg.n_head, self.cfg.d_head
        q = self.W_q(x).view(B, T, H, dh).transpose(1, 2)
        k = self.W_k(x).view(B, T, H, dh).transpose(1, 2)
        v = self.W_v(x).view(B, T, H, dh).transpose(1, 2)
        # pad_mask is (B, T): True for a real token.  Broadcast it over heads and
        # over query rows, so EVERY query may read EVERY real key.       <- EDIT 1
        mask = pad_mask[:, None, None, :]                     # (B,1,1,T)
        y, w = scaled_dot_product_attention(q, k, v, mask=mask, dropout=self.attn_drop,
                                            return_weights=keep_weights)
        if keep_weights:
            self.last_weights = w.detach()
        y = y.transpose(1, 2).contiguous().view(B, T, D)
        return self.resid_drop(self.W_o(y))


# ---------------------------------------------------------------------------
# 4.  MLP and block - unchanged
# ---------------------------------------------------------------------------

class MLP(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.fc = nn.Linear(cfg.d_model, cfg.d_ff)
        self.proj = nn.Linear(cfg.d_ff, cfg.d_model)
        self.drop = nn.Dropout(cfg.dropout)

    def forward(self, x):
        return self.drop(self.proj(nn.functional.gelu(self.fc(x))))


class Block(nn.Module):
    """Pre-norm, exactly as in the GPT file.  (The 2018 BERT normalised AFTER each
    sublayer - "post-norm".  Same parameters, same count; pre-norm simply trains
    more forgivingly at small scale, so we keep the GPT file's block untouched.)"""

    def __init__(self, cfg):
        super().__init__()
        self.ln1 = nn.LayerNorm(cfg.d_model)
        self.attn = MultiHeadSelfAttention(cfg)
        self.ln2 = nn.LayerNorm(cfg.d_model)
        self.mlp = MLP(cfg)

    def forward(self, x, pad_mask, keep_weights=False):
        x = x + self.attn(self.ln1(x), pad_mask, keep_weights=keep_weights)
        x = x + self.mlp(self.ln2(x))
        return x


# ---------------------------------------------------------------------------
# 5.  The model: THREE embedding tables in, TWO heads out     (EDITS 2 and 4)
# ---------------------------------------------------------------------------

class MiniBERT(nn.Module):
    def __init__(self, cfg: Config):
        super().__init__()
        self.cfg = cfg
        self.tok_emb = nn.Embedding(cfg.vocab_size, cfg.d_model)    # WHAT the token is
        self.pos_emb = nn.Embedding(cfg.block_size, cfg.d_model)    # WHERE it sits
        self.seg_emb = nn.Embedding(cfg.n_segments, cfg.d_model)    # WHICH span  <- EDIT 2
        self.drop = nn.Dropout(cfg.dropout)
        self.blocks = nn.ModuleList([Block(cfg) for _ in range(cfg.n_layer)])
        self.ln_f = nn.LayerNorm(cfg.d_model)

        # HEAD 1 - masked-word head.  A small transform, then a score for every
        # word in the vocabulary.  The scoring matrix is the embedding table
        # itself (tied), exactly as GPT's output head was.            <- EDIT 4
        self.mlm_transform = nn.Linear(cfg.d_model, cfg.d_model)
        self.mlm_ln = nn.LayerNorm(cfg.d_model)
        self.mlm_bias = nn.Parameter(torch.zeros(cfg.vocab_size))

        # HEAD 2 - next-sentence head.  Reads ONLY slot 0, the [CLS] slot, through
        # a "pooler" (D -> D, tanh), then scores two classes.        <- EDIT 4
        self.pooler = nn.Linear(cfg.d_model, cfg.d_model)
        self.nsp_head = nn.Linear(cfg.d_model, 2)
        self.apply(self._init)

    @staticmethod
    def _init(m):
        if isinstance(m, nn.Linear):
            nn.init.normal_(m.weight, mean=0.0, std=0.02)
            if m.bias is not None:
                nn.init.zeros_(m.bias)
        elif isinstance(m, nn.Embedding):
            nn.init.normal_(m.weight, mean=0.0, std=0.02)

    def n_params(self):
        return sum(p.numel() for p in self.parameters())

    def encode(self, idx, seg, pad_mask, keep_weights=False):
        """The backbone: ids in, one D-vector per slot out.  This is the part you
        keep when you fine-tune; both heads below are thrown away."""
        B, T = idx.shape
        pos = torch.arange(T, device=idx.device)
        # Three lookups, ADDED.  Not concatenated: the three tables share the same
        # D columns, and the sum is what the first block sees.         <- EDIT 2
        x = self.drop(self.tok_emb(idx) + self.pos_emb(pos) + self.seg_emb(seg))
        for blk in self.blocks:
            x = blk(x, pad_mask, keep_weights=keep_weights)
        return self.ln_f(x)                                         # (B, T, D)

    def mlm_logits(self, h):
        z = self.mlm_ln(nn.functional.gelu(self.mlm_transform(h)))
        return z @ self.tok_emb.weight.T + self.mlm_bias             # (.., V)

    def nsp_logits(self, h):
        return self.nsp_head(torch.tanh(self.pooler(h[:, 0])))      # (B, 2)

    def forward(self, idx, seg, pad_mask, mlm_labels=None, nsp_labels=None):
        h = self.encode(idx, seg, pad_mask)
        # Score only the hidden slots.  Labels are -100 everywhere else, and
        # cross_entropy ignores -100: 85% of the slots contribute NO loss at all.
        sel = mlm_labels.ne(-100) if mlm_labels is not None else None
        out = {}
        if sel is not None:
            logits = self.mlm_logits(h[sel])                        # (n_masked, V)
            out["mlm_loss"] = nn.functional.cross_entropy(logits, mlm_labels[sel])
            out["mlm_correct"] = (logits.argmax(-1) == mlm_labels[sel]).sum()
            out["mlm_n"] = sel.sum()
        if nsp_labels is not None:
            nl = self.nsp_logits(h)
            out["nsp_loss"] = nn.functional.cross_entropy(nl, nsp_labels)
            out["nsp_correct"] = (nl.argmax(-1) == nsp_labels).sum()
        return out


# ---------------------------------------------------------------------------
# 6.  The training pair                                          (EDIT 3)
# ---------------------------------------------------------------------------
# GPT:  x = tokens 0..T-1,  y = tokens 1..T.  One line.
# BERT: build  [CLS] A [SEP] B [SEP],  where B either really followed A in the
#       same complaint (IsNext, label 0) or was cut from a random OTHER complaint
#       (NotNext, label 1).  Then hide 15% of the real tokens.
#
# The paper is explicit that a "sentence" here is "an arbitrary span of
# contiguous text, rather than an actual linguistic sentence" (Devlin et al.
# 2019, section 3).  That is lucky for us: our corpus has no punctuation left,
# so spans are all we could cut anyway.

IS_NEXT, NOT_NEXT = 0, 1


class PairSampler:
    def __init__(self, docs_ids, cfg, seed=0):
        self.docs = [d for d in docs_ids if len(d) >= 12]
        self.cfg, self.rng = cfg, random.Random(seed)
        self.budget = cfg.block_size - 3            # [CLS] ... [SEP] ... [SEP]

    def spans(self, force=None, doc_index=None):
        """Return (A, B, label).  force=IS_NEXT/NOT_NEXT pins the label."""
        r = self.rng
        d = self.docs[doc_index if doc_index is not None else r.randrange(len(self.docs))]
        s = r.randint(4, len(d) - 4)                 # the cut point
        la = min(s, r.randint(8, 40))
        A = d[s - la: s]
        lb = min(self.budget - la, len(d) - s)
        label = force if force is not None else (IS_NEXT if r.random() < 0.5 else NOT_NEXT)
        if label == IS_NEXT:
            B = d[s: s + lb]
        else:
            while True:
                e = self.docs[r.randrange(len(self.docs))]
                if e is not d and len(e) >= lb:
                    break
            st = r.randint(0, len(e) - lb)
            B = e[st: st + lb]
        return A, B, label


def pack(A, B, tok: WordTokenizer, T: int):
    ids = [tok.cls_id] + A + [tok.sep_id] + B + [tok.sep_id]
    seg = [0] * (len(A) + 2) + [1] * (len(B) + 1)
    n = len(ids)
    ids += [tok.pad_id] * (T - n)
    seg += [0] * (T - n)
    return ids, seg, n


def mask_tokens(ids: torch.Tensor, n_real: torch.Tensor, tok: WordTokenizer,
                gen: torch.Generator, rate=0.15):
    """BERT's masking rule, section 3.1 of the paper.

    Choose 15% of the REAL word slots (never [CLS], [SEP] or [PAD]).  Of those:
        80%  -> replaced by [MASK]
        10%  -> replaced by a random word
        10%  -> left exactly as they were
    and the model must recover the original word at all of them.

    Why not always [MASK]?  Because [MASK] never appears when the model is used.
    The 10% random and 10% unchanged slots mean the model can never be sure a
    visible word is genuine, so it has to build a good vector for EVERY token,
    not just for the blanks.
    """
    B, T = ids.shape
    special = (ids == tok.cls_id) | (ids == tok.sep_id) | (ids == tok.pad_id)
    chosen = (torch.rand(B, T, generator=gen) < rate) & ~special
    labels = torch.full_like(ids, -100)
    labels[chosen] = ids[chosen]
    roll = torch.rand(B, T, generator=gen)
    x = ids.clone()
    to_mask = chosen & (roll < 0.8)
    to_rand = chosen & (roll >= 0.8) & (roll < 0.9)
    x[to_mask] = tok.mask_id
    rand_words = torch.randint(len(SPECIALS), tok.vocab_size, (B, T), generator=gen)
    x[to_rand] = rand_words[to_rand]
    return x, labels, dict(masked=int(to_mask.sum()), random=int(to_rand.sum()),
                           kept=int((chosen & (roll >= 0.9)).sum()), chosen=int(chosen.sum()),
                           real=int((~special).sum()))


def make_batch(sampler, tok, cfg, batch_size, gen, force=None):
    rows = [sampler.spans(force=force) for _ in range(batch_size)]
    packed = [pack(A, B, tok, cfg.block_size) for A, B, _ in rows]
    ids = torch.tensor([p[0] for p in packed])
    seg = torch.tensor([p[1] for p in packed])
    n = torch.tensor([p[2] for p in packed])
    pad_mask = torch.arange(cfg.block_size)[None, :] < n[:, None]
    x, mlm_labels, _ = mask_tokens(ids, n, tok, gen)
    nsp = torch.tensor([r[2] for r in rows])
    return x, seg, pad_mask, mlm_labels, nsp


# ---------------------------------------------------------------------------
# 7.  Training - the GPT loop with two losses added together
# ---------------------------------------------------------------------------

@torch.no_grad()
def evaluate(model, sampler_val, tok, cfg, batch_size=64, iters=30, seed=1234, nsp=True):
    model.eval()
    sampler_val.rng = random.Random(seed)
    gen = torch.Generator().manual_seed(seed)
    ml = mc = mn = nl = nc = nn_ = 0.0
    for _ in range(iters):
        x, seg, pm, y, ns = make_batch(sampler_val, tok, cfg, batch_size, gen)
        o = model(x, seg, pm, mlm_labels=y, nsp_labels=ns if nsp else None)
        ml += float(o["mlm_loss"]) * int(o["mlm_n"])
        mc += int(o["mlm_correct"]); mn += int(o["mlm_n"])
        if nsp:
            nl += float(o["nsp_loss"]) * batch_size
            nc += int(o["nsp_correct"]); nn_ += batch_size
    model.train()
    r = dict(mlm_loss=ml / mn, mlm_acc=mc / mn, mlm_ppl=math.exp(ml / mn))
    if nsp:
        r.update(nsp_loss=nl / nn_, nsp_acc=nc / nn_)
    return r


def train(cfg: Config, steps=6000, batch_size=32, lr=1e-3, warmup=300, seed=0,
          use_nsp=True, eval_every=250, log_path=None, threads=None, max_seconds=None,
          nsp_weight=1.0):
    """max_seconds lets a long run be split into sessions: the full training
    state (weights, optimiser, schedule, every random-number generator) is saved
    to a resume file, and the next call carries on exactly where it stopped."""
    if threads:
        torch.set_num_threads(threads)
    torch.manual_seed(seed)
    train_docs, val_docs, stats = load_corpus()
    tok = WordTokenizer.fit(train_docs, cfg.vocab_size)
    tr_ids = [tok.encode(d) for d in train_docs]
    va_ids = [tok.encode(d) for d in val_docs]
    s_tr, s_va = PairSampler(tr_ids, cfg, seed), PairSampler(va_ids, cfg, seed + 1)
    va_flat = [t for d in va_ids for t in d]
    unk_rate = sum(t == tok.unk_id for t in va_flat) / len(va_flat)
    print(f"corpus {stats}")
    print(f"val <unk> rate {unk_rate:.3%}")

    model = MiniBERT(cfg)
    print(f"model {model.n_params():,} parameters   nsp={use_nsp}")
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01, betas=(0.9, 0.98))
    sched = torch.optim.lr_scheduler.LambdaLR(
        opt, lambda s: min((s + 1) / warmup, 1.0) *
        (0.5 * (1 + math.cos(math.pi * min(s / steps, 1.0))) * 0.9 + 0.1))
    gen = torch.Generator().manual_seed(seed)
    history, start, spent = [], 0, 0.0
    import os
    resume = Path(os.environ.get("BERT_RESUME_DIR", HERE)) / (ckpt_path(use_nsp, nsp_weight).stem + ".resume")
    if resume.exists():
        st = torch.load(resume, map_location="cpu", weights_only=False)
        model.load_state_dict(st["model"]); opt.load_state_dict(st["opt"])
        sched.load_state_dict(st["sched"]); gen.set_state(st["gen"])
        torch.set_rng_state(st["torch_rng"]); s_tr.rng.setstate(st["py_rng"])
        history, start, spent = st["history"], st["step"], st["spent"]
        print(f"resumed at step {start}")
    t0 = time.time() - spent
    model.train()
    for step in range(start, steps + 1):
        if max_seconds and time.time() - t0 - spent > max_seconds and step % 50 == 0:
            torch.save(dict(model=model.state_dict(), opt=opt.state_dict(),
                            sched=sched.state_dict(), gen=gen.get_state(),
                            torch_rng=torch.get_rng_state(), py_rng=s_tr.rng.getstate(),
                            history=history, step=step, spent=time.time() - t0), resume)
            print(f"paused at step {step}", flush=True)
            return None, tok, history
        if step % eval_every == 0 or step == steps:
            ev = evaluate(model, s_va, tok, cfg, nsp=use_nsp)
            ev.update(step=step, seconds=round(time.time() - t0, 1), lr=sched.get_last_lr()[0])
            history.append(ev)
            print(json.dumps(ev), flush=True)
            if log_path:
                Path(log_path).write_text(json.dumps(history, indent=1))
        if step == steps:
            break
        x, seg, pm, y, ns = make_batch(s_tr, tok, cfg, batch_size, gen)
        o = model(x, seg, pm, mlm_labels=y, nsp_labels=ns if use_nsp else None)
        # The whole of BERT's objective: two cross-entropies, added.
        loss = o["mlm_loss"] + (nsp_weight * o["nsp_loss"] if use_nsp else 0.0)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        sched.step()

    torch.save(dict(model=model.state_dict(), cfg=asdict(cfg), itos=tok.itos,
                    history=history, corpus=stats, unk_rate=unk_rate, use_nsp=use_nsp,
                    steps=steps, batch_size=batch_size, lr=lr, warmup=warmup,
                    minutes=(time.time() - t0) / 60, nsp_weight=nsp_weight), ckpt_path(use_nsp, nsp_weight))
    print(f"saved {ckpt_path(use_nsp, nsp_weight)}  {(time.time() - t0) / 60:.1f} min")
    return model, tok, history


def load_trained(nsp=True):
    ck = torch.load(ckpt_path(nsp), map_location="cpu", weights_only=False)
    cfg = Config(**ck["cfg"])
    model = MiniBERT(cfg)
    model.load_state_dict(ck["model"])
    model.eval()
    return model, WordTokenizer(ck["itos"]), ck


# ---------------------------------------------------------------------------
# 8.  Fill in the blank
# ---------------------------------------------------------------------------

@torch.no_grad()
def fill(model, tok, text, k=5):
    """Predict every [MASK] in a single span, reading both sides."""
    ids = tok.encode(normalise(text.replace("[MASK]", " maskxx ")).replace("maskxx", "[mask]"))
    ids = [tok.cls_id] + ids[: model.cfg.block_size - 2] + [tok.sep_id]     # one span only
    n = len(ids)
    x = torch.tensor([ids + [tok.pad_id] * (model.cfg.block_size - n)])
    seg = torch.zeros_like(x)
    pm = torch.arange(model.cfg.block_size)[None, :] < n
    h = model.encode(x, seg, pm)
    out = []
    for pos in (x[0] == tok.mask_id).nonzero().flatten().tolist():
        p = softmax(model.mlm_logits(h[0, pos]), -1)
        top = torch.topk(p, k)
        out.append([(tok.itos[i], float(v)) for v, i in zip(top.values, top.indices)])
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--train", action="store_true")
    ap.add_argument("--no-nsp", action="store_true")
    ap.add_argument("--steps", type=int, default=6000)
    ap.add_argument("--threads", type=int, default=None)
    ap.add_argument("--log", default=None)
    ap.add_argument("--max-seconds", type=float, default=None)
    ap.add_argument("--nsp-weight", type=float, default=1.0)
    ap.add_argument("--fill", default=None)
    a = ap.parse_args()
    if a.train:
        train(Config(), steps=a.steps, use_nsp=not a.no_nsp, log_path=a.log, threads=a.threads,
              max_seconds=a.max_seconds, nsp_weight=a.nsp_weight)
    if a.fill:
        model, tok, _ = load_trained(nsp=not a.no_nsp)
        for i, cands in enumerate(fill(model, tok, a.fill)):
            print(f"[MASK] #{i + 1}: " + "  ".join(f"{w} {p:.3f}" for w, p in cands))
    if not (a.train or a.fill):
        ap.print_help()


if __name__ == "__main__":
    main()
