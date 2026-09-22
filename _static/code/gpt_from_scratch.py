#!/usr/bin/env python3
"""
AI for Mobility - a GPT you can read, line by line.

WHAT THIS IS
    A complete decoder-only transformer ("GPT-like") language model in one file,
    with every step of attention written out: the three projections Q, K, V, the
    dot product, the 1/sqrt(d_head) scale, the causal mask, the softmax, the
    weighted sum of V, the multi-head split and merge, the residual path and the
    layer norms.  Nothing is delegated to torch.nn.MultiheadAttention or to
    torch.nn.functional.scaled_dot_product_attention.  If you want to know what a
    transformer does, it is all here, in about 300 lines of model code.

WHAT IT READS
    42,956 real vehicle-owner complaint narratives filed with NHTSA (ADAS,
    braking, steering, lighting and related components), lowercased, punctuation
    stripped - the same corpus the word2vec and BPE material in this course uses.
    The model's whole job is: given the words so far, put a probability on every
    word that could come next.  That is the only objective.  Everything an LLM
    later does for you - classify a complaint, extract a component, summarise a
    crash report - is this one objective plus a head bolted on afterwards.

HOW TO RUN IT
    python3 gpt_from_scratch.py --explain          # no training: print the real
                                                   # matrices for one sentence
    python3 gpt_from_scratch.py --train            # train (~15-40 min, CPU)
    python3 gpt_from_scratch.py --sample           # generate from a checkpoint
    python3 gpt_from_scratch.py --check            # NumPy re-derivation of one
                                                   # attention head, no framework
    python3 gpt_from_scratch.py --baselines        # unigram / bigram perplexity

    Add --size tiny for a laptop-friendly run, --size small (default), or
    --size base if you have a GPU.  --device cuda|mps|cpu is auto-detected.

WHERE THE NUMBERS COME FROM
    Nothing in the slides, notes or companion page for this file is typed in by
    hand.  gpt_walkthrough_numbers.py imports this module, runs it, and writes
    every matrix and every statistic the teaching material quotes.

Hao Zhou, CGN 6933 AI for Mobility, University of South Florida.
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
import os
import random
import re
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

HERE = Path(__file__).resolve().parent
CKPT = HERE / "gpt_from_scratch.pt"

# The corpus ships with the course materials.  Look next to this file first, then
# in the usual class-folder locations, so the script runs unchanged from either.
_CORPUS_NAME = "nhtsa_adas_complaints.txt.gz"
_CORPUS_CANDIDATES = [HERE / _CORPUS_NAME,
                      HERE / "Labs" / "data" / _CORPUS_NAME,
                      HERE / "data" / _CORPUS_NAME,
                      HERE.parent / "data" / _CORPUS_NAME]
CORPUS = next((p for p in _CORPUS_CANDIDATES if p.exists()), _CORPUS_CANDIDATES[0])


# ---------------------------------------------------------------------------
# 0.  Configuration
# ---------------------------------------------------------------------------
# Every number a transformer paper reports lives in one of these fields.  Read
# them once; the rest of the file only ever refers back to them.

@dataclass
class Config:
    vocab_size: int = 6000      # V  - how many distinct words the model knows
    block_size: int = 64        # T  - context length, in tokens
    n_layer: int = 4            # L  - how many transformer blocks, stacked
    n_head: int = 4             # H  - attention heads per block
    d_model: int = 128          # D  - width of the residual stream
    d_ff: int = 512             # 4D - width inside the MLP
    dropout: float = 0.1
    tie_weights: bool = True    # reuse the embedding table as the output head

    @property
    def d_head(self) -> int:    # dh - width of ONE head.  D = H * dh, always.
        assert self.d_model % self.n_head == 0, "d_model must divide by n_head"
        return self.d_model // self.n_head


SIZES = {
    "tiny":  dict(vocab_size=3000, block_size=32, n_layer=2, n_head=2, d_model=64,  d_ff=256),
    "small": dict(vocab_size=6000, block_size=64, n_layer=4, n_head=4, d_model=128, d_ff=512),
    "base":  dict(vocab_size=12000, block_size=128, n_layer=6, n_head=8, d_model=256, d_ff=1024),
}


# ---------------------------------------------------------------------------
# 1.  The tokenizer
# ---------------------------------------------------------------------------
# A GPT does not read text.  It reads integers.  A tokenizer is the (reversible)
# map between them.  Real GPTs use byte-pair encoding, which you met in the
# tokenization companion; here we use whole words so that every attention row
# you look at later is readable - "brake" is one token, not "br" + "ake".
#
# The cost of that choice is honest and worth stating to students: a word
# vocabulary cannot spell a word it never saw.  Every out-of-vocabulary word
# becomes <unk>, and we measure how often that happens.

UNK, EOS = "<unk>", "<eos>"


class WordTokenizer:
    def __init__(self, itos: list[str]):
        self.itos = itos
        self.stoi = {s: i for i, s in enumerate(itos)}
        self.unk_id = self.stoi[UNK]
        self.eos_id = self.stoi[EOS]

    @property
    def vocab_size(self) -> int:
        return len(self.itos)

    @classmethod
    def fit(cls, documents: list[str], vocab_size: int) -> "WordTokenizer":
        counts: dict[str, int] = {}
        for doc in documents:
            for w in doc.split():
                counts[w] = counts.get(w, 0) + 1
        # Deterministic: sort by frequency, then alphabetically to break ties.
        ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        itos = [UNK, EOS] + [w for w, _ in ranked[: vocab_size - 2]]
        return cls(itos)

    def encode(self, text: str, add_eos: bool = False) -> list[int]:
        ids = [self.stoi.get(w, self.unk_id) for w in text.split()]
        return ids + [self.eos_id] if add_eos else ids

    def decode(self, ids) -> str:
        return " ".join(self.itos[int(i)] for i in ids)


def load_corpus(path: Path = CORPUS, seed: int = 0):
    """Read the complaints, deduplicate, and split into train / validation.

    THE SPLIT IS THE HONEST PART.  Complaint narratives repeat verbatim across
    filings (re-filings, dealer form letters).  If the same narrative lands in
    both halves, validation perplexity measures memorisation, not language.  So
    we deduplicate on normalised text BEFORE splitting, and we split by whole
    document, never mid-narrative.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"corpus not found: {path}\nLooked in: "
            + ", ".join(str(c) for c in _CORPUS_CANDIDATES))
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8", errors="ignore") as fh:
        raw = [ln.strip() for ln in fh if ln.strip()]
    seen, docs = set(), []
    for line in raw:
        key = re.sub(r"\s+", " ", line.lower())
        if key in seen:
            continue
        seen.add(key)
        docs.append(key)
    rng = random.Random(seed)
    rng.shuffle(docs)
    n_val = max(1, int(0.10 * len(docs)))
    return docs[n_val:], docs[:n_val], dict(raw_lines=len(raw), unique=len(docs), n_val=n_val)


def as_token_stream(docs: list[str], tok: WordTokenizer) -> torch.Tensor:
    """One long 1-D tensor: every document, each closed by <eos>."""
    ids: list[int] = []
    for d in docs:
        ids.extend(tok.encode(d, add_eos=True))
    return torch.tensor(ids, dtype=torch.long)


# ---------------------------------------------------------------------------
# 2.  Softmax, implemented rather than imported
# ---------------------------------------------------------------------------
# softmax turns a row of arbitrary real scores into a row of probabilities that
# sums to 1.  You already use it under another name: this is the multinomial
# logit choice probability, with score s_j playing the role of utility V_j.
#
#       softmax(s)_j = exp(s_j) / sum_k exp(s_k)
#
# Written that way it overflows.  exp(800) is +inf in float32, and inf/inf is
# nan, and one nan poisons every weight in the model at the next backward pass.
# The fix is one line and it is exact, not an approximation: subtracting a
# constant from every score leaves the ratio unchanged, so subtract the row max.
# After that the largest exponent is exp(0) = 1 and nothing can overflow.

def softmax(scores: torch.Tensor, dim: int = -1) -> torch.Tensor:
    m = scores.max(dim=dim, keepdim=True).values      # the row max, detached below
    z = scores - m                                    # now every entry <= 0
    e = torch.exp(z)
    return e / e.sum(dim=dim, keepdim=True)


def naive_softmax(scores: torch.Tensor, dim: int = -1) -> torch.Tensor:
    """The textbook formula, for the overflow demonstration only."""
    e = torch.exp(scores)
    return e / e.sum(dim=dim, keepdim=True)


# ---------------------------------------------------------------------------
# 3.  Attention - the part everything else is scaffolding for
# ---------------------------------------------------------------------------
# One sentence: every token proposes a QUESTION (its query), advertises a
# KEY saying what it can answer, and carries a VALUE it will hand over.  Token i
# compares its question against every key, turns the comparison into weights,
# and takes that weighted average of the values.  Q, K and V are three different
# linear views of the SAME input vector - three different matrices, one input.
#
# In transportation terms: this is a weighted average over other locations, like
# a spatial filter - except the weights are not declared by you from a road
# network adjacency matrix.  They are computed from the content of the tokens,
# and they change every time the input changes.

def scaled_dot_product_attention(q, k, v, mask=None, dropout=None, return_weights=False):
    """The five lines that are the transformer.

    Shapes (B batch, H heads, T tokens, dh head width):
        q, k, v : (B, H, T, dh)
        mask    : (T, T) boolean, True where attention is ALLOWED
        returns : (B, H, T, dh)
    """
    d_head = q.size(-1)

    # (1) THE DOT PRODUCT.  scores[i, j] = q_i . k_j  - how well token j's key
    #     answers token i's question.  One matmul does all T*T of them at once:
    #     (B,H,T,dh) @ (B,H,dh,T) -> (B,H,T,T).
    scores = q @ k.transpose(-2, -1)

    # (2) THE SCALE.  A dot product of two dh-dimensional vectors with unit-ish
    #     entries has standard deviation ~sqrt(dh).  Feed raw scores of that size
    #     into softmax and one weight goes to 1.0 and the rest to 0 - attention
    #     collapses onto a single token and the gradient through softmax dies.
    #     Dividing by sqrt(dh) puts the scores back on a scale softmax can work
    #     with.  This is the "Scaled" in "Scaled Dot-Product Attention".
    scores = scores / math.sqrt(d_head)

    # (3) THE CAUSAL MASK.  A GPT predicts the next token, so token i may look at
    #     tokens 0..i and must not look at i+1..T-1.  Without this the model
    #     reads the answer off the input and validation loss goes to zero while
    #     the model has learned nothing - the language equivalent of leaking the
    #     future into a time-series split.  -inf, not a small number: softmax
    #     sends exp(-inf) to exactly 0, so the forbidden tokens get exactly no
    #     weight and no gradient.
    if mask is not None:
        scores = scores.masked_fill(~mask, float("-inf"))

    # (4) THE SOFTMAX, row by row.  Each row i becomes a probability distribution
    #     over "which earlier token do I read from".
    weights = softmax(scores, dim=-1)
    if dropout is not None:
        weights = dropout(weights)

    # (5) THE WEIGHTED SUM OF VALUES.  (B,H,T,T) @ (B,H,T,dh) -> (B,H,T,dh).
    out = weights @ v
    return (out, weights) if return_weights else (out, None)


class MultiHeadSelfAttention(nn.Module):
    """Q, K, V as three separate matrices, then H heads in parallel.

    Most production code fuses W_q, W_k, W_v into one (D, 3D) matrix for speed.
    Keeping them apart costs nothing in accuracy and makes the picture literal:
    three matrices, three projections of the same vector.
    """

    def __init__(self, cfg: Config):
        super().__init__()
        self.cfg = cfg
        self.W_q = nn.Linear(cfg.d_model, cfg.d_model, bias=False)   # (D, D)
        self.W_k = nn.Linear(cfg.d_model, cfg.d_model, bias=False)
        self.W_v = nn.Linear(cfg.d_model, cfg.d_model, bias=False)
        self.W_o = nn.Linear(cfg.d_model, cfg.d_model, bias=False)   # the merge
        self.attn_drop = nn.Dropout(cfg.dropout)
        self.resid_drop = nn.Dropout(cfg.dropout)
        # The mask is a constant, not a parameter: a lower-triangular block of
        # True.  Registered as a buffer so it moves to the GPU with the model.
        self.register_buffer(
            "causal_mask",
            torch.tril(torch.ones(cfg.block_size, cfg.block_size, dtype=torch.bool)),
            persistent=False,
        )
        self.last_weights = None      # kept for the figures; not used in training

    def forward(self, x, keep_weights: bool = False):
        B, T, D = x.shape
        H, dh = self.cfg.n_head, self.cfg.d_head

        # (a) THREE PROJECTIONS of the same input.  (B,T,D) -> (B,T,D) each.
        q = self.W_q(x)
        k = self.W_k(x)
        v = self.W_v(x)

        # (b) THE HEAD SPLIT.  Nothing is copied: the D numbers of each token are
        #     read as H groups of dh.  Head h only ever sees its own slice, so
        #     the heads cannot talk to each other until step (d).
        #     (B,T,D) -> (B,T,H,dh) -> (B,H,T,dh)
        q = q.view(B, T, H, dh).transpose(1, 2)
        k = k.view(B, T, H, dh).transpose(1, 2)
        v = v.view(B, T, H, dh).transpose(1, 2)

        mask = self.causal_mask[:T, :T]
        y, w = scaled_dot_product_attention(
            q, k, v, mask=mask, dropout=self.attn_drop, return_weights=keep_weights
        )
        if keep_weights:
            self.last_weights = w.detach()

        # (c) THE MERGE.  Put the heads back side by side: (B,H,T,dh) ->
        #     (B,T,H,dh) -> (B,T,D).  Concatenation, not addition.
        y = y.transpose(1, 2).contiguous().view(B, T, D)

        # (d) THE OUTPUT PROJECTION.  Until now every head's dh numbers sat in
        #     their own lane.  W_o is the only place the heads mix.
        return self.resid_drop(self.W_o(y))


# ---------------------------------------------------------------------------
# 4.  The rest of a block: MLP, layer norm, residual
# ---------------------------------------------------------------------------
# Attention moves information BETWEEN tokens.  It never transforms a token on its
# own - a weighted average of values is still a linear map.  The MLP is where
# each token is processed INDIVIDUALLY and non-linearly.  A transformer block is
# exactly those two operations, each wrapped in a residual connection.

class MLP(nn.Module):
    def __init__(self, cfg: Config):
        super().__init__()
        self.fc = nn.Linear(cfg.d_model, cfg.d_ff)      # widen  D -> 4D
        self.proj = nn.Linear(cfg.d_ff, cfg.d_model)    # narrow 4D -> D
        self.drop = nn.Dropout(cfg.dropout)

    def forward(self, x):
        return self.drop(self.proj(nn.functional.gelu(self.fc(x))))


class Block(nn.Module):
    """Pre-norm block, as in GPT-2 and everything after it.

        x = x + attention(norm(x))
        x = x + mlp(norm(x))

    The residual "+" is why 96-layer models train at all: the gradient has a path
    to the input that never passes through a weight matrix.  Normalising BEFORE
    the sublayer (rather than after, as in the 2017 paper) is what removed the
    learning-rate warmup that early transformers needed.
    """

    def __init__(self, cfg: Config):
        super().__init__()
        self.ln1 = nn.LayerNorm(cfg.d_model)
        self.attn = MultiHeadSelfAttention(cfg)
        self.ln2 = nn.LayerNorm(cfg.d_model)
        self.mlp = MLP(cfg)

    def forward(self, x, keep_weights: bool = False):
        x = x + self.attn(self.ln1(x), keep_weights=keep_weights)
        x = x + self.mlp(self.ln2(x))
        return x


# ---------------------------------------------------------------------------
# 5.  The model
# ---------------------------------------------------------------------------

class MiniGPT(nn.Module):
    def __init__(self, cfg: Config):
        super().__init__()
        self.cfg = cfg
        self.tok_emb = nn.Embedding(cfg.vocab_size, cfg.d_model)   # WHAT a token is
        self.pos_emb = nn.Embedding(cfg.block_size, cfg.d_model)   # WHERE it sits
        self.drop = nn.Dropout(cfg.dropout)
        self.blocks = nn.ModuleList([Block(cfg) for _ in range(cfg.n_layer)])
        self.ln_f = nn.LayerNorm(cfg.d_model)
        self.head = nn.Linear(cfg.d_model, cfg.vocab_size, bias=False)
        if cfg.tie_weights:
            # The same matrix reads tokens in and scores them on the way out.
            # Free, and it is what GPT-2 does.
            self.head.weight = self.tok_emb.weight
        self.apply(self._init)

    @staticmethod
    def _init(m):
        if isinstance(m, nn.Linear):
            nn.init.normal_(m.weight, mean=0.0, std=0.02)
            if m.bias is not None:
                nn.init.zeros_(m.bias)
        elif isinstance(m, nn.Embedding):
            nn.init.normal_(m.weight, mean=0.0, std=0.02)

    def n_params(self, non_embedding: bool = False) -> int:
        n = sum(p.numel() for p in self.parameters())
        if non_embedding:
            n -= self.tok_emb.weight.numel() + self.pos_emb.weight.numel()
        return n

    def forward(self, idx, targets=None, keep_weights: bool = False):
        B, T = idx.shape
        assert T <= self.cfg.block_size, f"context of {T} exceeds block_size"

        # ADDING the position vector to the token vector is the whole positional
        # encoding story.  Attention itself is permutation-equivariant: shuffle
        # the tokens and the outputs shuffle with them, unchanged.  Word order
        # enters the model here and nowhere else.
        pos = torch.arange(T, device=idx.device)
        x = self.drop(self.tok_emb(idx) + self.pos_emb(pos))

        for blk in self.blocks:
            x = blk(x, keep_weights=keep_weights)
        x = self.ln_f(x)
        logits = self.head(x)                       # (B, T, V) - one row per token

        loss = None
        if targets is not None:
            # Cross-entropy over V alternatives.  Identical in form to the
            # log-likelihood you maximise when you estimate a multinomial logit
            # model - here V is 6,000 "alternatives" and there are millions of
            # "choice observations", one per token position.
            loss = nn.functional.cross_entropy(
                logits.view(-1, logits.size(-1)), targets.reshape(-1)
            )
        return logits, loss

    @torch.no_grad()
    def generate(self, idx, max_new_tokens=40, temperature=1.0, top_k=40, eos_id=None):
        """Autoregression: predict one token, append it, predict again.

        Nothing else happens.  An LLM answering a question is this loop.
        """
        self.eval()
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -self.cfg.block_size:]      # keep the last T tokens
            logits, _ = self(idx_cond)
            logits = logits[:, -1, :] / temperature       # only the LAST position
            if top_k:
                v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                logits[logits < v[:, [-1]]] = -float("inf")
            probs = softmax(logits, dim=-1)
            nxt = torch.multinomial(probs, num_samples=1)
            idx = torch.cat([idx, nxt], dim=1)
            if eos_id is not None and int(nxt) == eos_id:
                break
        return idx


# ---------------------------------------------------------------------------
# 6.  Training
# ---------------------------------------------------------------------------

def get_batch(stream: torch.Tensor, cfg: Config, batch_size: int, device, gen=None):
    """Sample random windows.  x is tokens 0..T-1, y is tokens 1..T - the label
    is just the input shifted by one.  No human labelled anything, which is the
    entire reason models of this kind could be scaled at all."""
    ix = torch.randint(len(stream) - cfg.block_size - 1, (batch_size,), generator=gen)
    x = torch.stack([stream[i: i + cfg.block_size] for i in ix])
    y = torch.stack([stream[i + 1: i + 1 + cfg.block_size] for i in ix])
    return x.to(device), y.to(device)


@torch.no_grad()
def estimate_loss(model, streams, cfg, batch_size, device, iters=40, seed=1234):
    model.eval()
    out = {}
    for split, stream in streams.items():
        gen = torch.Generator().manual_seed(seed)
        losses = torch.zeros(iters)
        for i in range(iters):
            x, y = get_batch(stream, cfg, batch_size, device, gen=gen)
            _, loss = model(x, y)
            losses[i] = loss.item()
        out[split] = losses.mean().item()
    model.train()
    return out


def train(cfg: Config, steps=2000, batch_size=32, lr=3e-4, device="cpu",
          eval_every=100, seed=0, log_path=None, warmup=100):
    torch.manual_seed(seed)
    train_docs, val_docs, stats = load_corpus()
    tok = WordTokenizer.fit(train_docs, cfg.vocab_size)
    tr = as_token_stream(train_docs, tok)
    va = as_token_stream(val_docs, tok)
    unk_rate = float((va == tok.unk_id).float().mean())
    print(f"corpus: {stats['unique']:,} unique complaints "
          f"({stats['raw_lines'] - stats['unique']:,} duplicates dropped)")
    print(f"tokens: {len(tr):,} train / {len(va):,} val   vocab {tok.vocab_size:,}   "
          f"<unk> rate on val {unk_rate:.3%}")

    model = MiniGPT(cfg).to(device)
    print(f"model:  {model.n_params():,} parameters "
          f"({model.n_params(non_embedding=True):,} outside the embedding tables)")

    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.1,
                            betas=(0.9, 0.95))
    sched = torch.optim.lr_scheduler.LambdaLR(
        opt, lambda s: min((s + 1) / warmup, 1.0) * (0.5 * (1 + math.cos(math.pi * min(s / steps, 1.0))) * 0.9 + 0.1)
    )
    streams = {"train": tr, "val": va}
    history, t0 = [], time.time()
    model.train()
    for step in range(steps + 1):
        if step % eval_every == 0 or step == steps:
            lo = estimate_loss(model, streams, cfg, batch_size, device)
            rec = dict(step=step, train=lo["train"], val=lo["val"],
                       val_ppl=math.exp(lo["val"]), seconds=time.time() - t0)
            history.append(rec)
            print(f"step {step:5d}  train {lo['train']:.4f}  val {lo['val']:.4f}  "
                  f"val ppl {math.exp(lo['val']):7.1f}  [{rec['seconds']:.0f}s]")
            if log_path:
                Path(log_path).write_text(json.dumps(history, indent=1))
        if step == steps:
            break
        x, y = get_batch(tr, cfg, batch_size, device)
        _, loss = model(x, y)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        sched.step()

    torch.save(dict(model=model.state_dict(), cfg=asdict(cfg), itos=tok.itos,
                    history=history, corpus=stats, unk_rate=unk_rate), CKPT)
    print(f"saved {CKPT}")
    return model, tok, history


def load_trained(device="cpu"):
    ck = torch.load(CKPT, map_location=device, weights_only=False)
    cfg = Config(**ck["cfg"])
    model = MiniGPT(cfg).to(device)
    model.load_state_dict(ck["model"])
    model.eval()
    return model, WordTokenizer(ck["itos"]), ck


# ---------------------------------------------------------------------------
# 7.  Baselines - the evaluation close
# ---------------------------------------------------------------------------
# A perplexity means nothing on its own.  Perplexity is "how many equally likely
# words is the model effectively choosing between at each position": a uniform
# guesser over V words scores V.  These two baselines are what the transformer
# has to beat before any of its machinery has earned its place.

def count_baselines(cfg: Config, k=0.1):
    train_docs, val_docs, _ = load_corpus()
    tok = WordTokenizer.fit(train_docs, cfg.vocab_size)
    tr = as_token_stream(train_docs, tok).numpy()
    va = as_token_stream(val_docs, tok).numpy()
    V = tok.vocab_size

    uni = np.bincount(tr, minlength=V).astype(np.float64) + k
    uni /= uni.sum()
    uni_nll = float(-np.log(uni[va]).mean())

    # Bigram with add-k smoothing, held in a sparse dictionary.
    nxt: dict[int, dict[int, int]] = {}
    tot: dict[int, int] = {}
    for a, b in zip(tr[:-1], tr[1:]):
        a, b = int(a), int(b)
        nxt.setdefault(a, {})[b] = nxt.setdefault(a, {}).get(b, 0) + 1
        tot[a] = tot.get(a, 0) + 1
    nll = 0.0
    for a, b in zip(va[:-1], va[1:]):
        a, b = int(a), int(b)
        c = nxt.get(a, {}).get(b, 0)
        nll += -math.log((c + k) / (tot.get(a, 0) + k * V))
    bi_nll = nll / (len(va) - 1)

    return dict(vocab=V,
                uniform_ppl=float(V), uniform_nll=float(math.log(V)),
                unigram_nll=uni_nll, unigram_ppl=math.exp(uni_nll),
                bigram_nll=bi_nll, bigram_ppl=math.exp(bi_nll),
                add_k=k, val_tokens=int(len(va)))


# ---------------------------------------------------------------------------
# 8.  The NumPy mirror - one head, no framework
# ---------------------------------------------------------------------------
# Autograd is convenient and it is also a place to hide.  This function takes the
# TRAINED weights out of the model, re-derives one head's output with nothing but
# NumPy, and asserts the two agree.  If it passes, everything above is arithmetic
# you could do on paper - and the printed intermediates are the real ones.

def numpy_attention_head(model: MiniGPT, ids: torch.Tensor, layer=0, head=0, atol=1e-5):
    cfg = model.cfg
    dh, H = cfg.d_head, cfg.n_head
    sl = slice(head * dh, (head + 1) * dh)
    blk = model.blocks[layer]
    model.eval()

    with torch.no_grad():
        # Everything the block sees, up to its first LayerNorm.
        pos = torch.arange(ids.size(1))
        x = model.tok_emb(ids) + model.pos_emb(pos)
        for b in model.blocks[:layer]:
            x = b(x)
        xn = blk.ln1(x)
        ref, _ = scaled_dot_product_attention(
            *[t(xn).view(1, -1, H, dh).transpose(1, 2) for t in (blk.attn.W_q, blk.attn.W_k, blk.attn.W_v)],
            mask=blk.attn.causal_mask[: ids.size(1), : ids.size(1)], return_weights=True)
        ref_out = ref[0, head].numpy()

        X = xn[0].numpy()                                        # (T, D)
        Wq = blk.attn.W_q.weight.numpy()[sl].T                   # (D, dh)
        Wk = blk.attn.W_k.weight.numpy()[sl].T
        Wv = blk.attn.W_v.weight.numpy()[sl].T

    T = X.shape[0]
    Q, K, V = X @ Wq, X @ Wk, X @ Wv                             # (T, dh) each
    S = Q @ K.T                                                  # (T, T) dot products
    S = S / np.sqrt(dh)                                          # the scale
    S = np.where(np.tril(np.ones((T, T), bool)), S, -np.inf)     # the causal mask
    E = np.exp(S - S.max(axis=1, keepdims=True))                 # softmax, safely
    A = E / E.sum(axis=1, keepdims=True)
    OUT = A @ V                                                  # weighted sum of V

    err = float(np.abs(OUT - ref_out).max())
    assert err < atol, f"NumPy and PyTorch disagree by {err}"
    return dict(X=X, Q=Q, K=K, V=V, scores_raw=(Q @ K.T), scores=S, attn=A, out=OUT,
                Wq=Wq, Wk=Wk, Wv=Wv, max_abs_err=err, layer=layer, head=head)


# ---------------------------------------------------------------------------
# 9.  --explain : print the real matrices for one sentence
# ---------------------------------------------------------------------------

DEMO = ("the adaptive cruise control disengaged without warning and the vehicle "
        "accelerated toward the truck ahead")


def explain(sentence=DEMO, layer=0, head=0, query_word=None, device="cpu", trained=True):
    if trained and CKPT.exists():
        model, tok, _ = load_trained(device)
        tag = "TRAINED"
    else:
        cfg = Config(**SIZES["small"])
        train_docs, _, _ = load_corpus()
        tok = WordTokenizer.fit(train_docs, cfg.vocab_size)
        torch.manual_seed(0)
        model = MiniGPT(cfg).eval()
        tag = "UNTRAINED (run --train first for the trained version)"

    ids = torch.tensor([tok.encode(sentence)])
    words = [tok.itos[i] for i in ids[0].tolist()]
    T, cfg = ids.size(1), model.cfg
    qi = words.index(query_word) if query_word in words else T // 2

    print(f"\n=== {tag} ===")
    print(f"sentence     : {sentence}")
    print(f"tokens       : {T}   vocab {tok.vocab_size}   d_model {cfg.d_model} "
          f"= {cfg.n_head} heads x {cfg.d_head}")
    print(f"token ids    : {ids[0].tolist()}")

    d = numpy_attention_head(model, ids, layer=layer, head=head)
    print(f"\n--- layer {layer}, head {head}: shapes ---")
    print(f"  x (after LayerNorm)  {d['X'].shape}")
    print(f"  W_q slice for head   {d['Wq'].shape}   ->  Q {d['Q'].shape}")
    print(f"  scores = Q K^T       {d['scores'].shape}   (one row per token)")
    print(f"  output = A V         {d['out'].shape}")
    print(f"  NumPy vs PyTorch max abs difference: {d['max_abs_err']:.2e}")

    print(f"\n--- the query token is '{words[qi]}' (position {qi}) ---")
    print(f"  q[{qi}] first 8 of {cfg.d_head}: "
          f"{np.array2string(d['Q'][qi][:8], precision=3, floatmode='fixed')}")
    print(f"\n  {'j':>3} {'token':<14} {'q.k':>9} {'/sqrt(dh)':>10} {'masked':>9} {'softmax':>8}")
    for j in range(T):
        raw, sc = d["scores_raw"][qi, j], d["scores"][qi, j]
        mk = "-inf" if not np.isfinite(sc) else f"{sc:9.3f}"
        print(f"  {j:>3} {words[j]:<14} {raw:9.3f} {raw/np.sqrt(cfg.d_head):10.3f} "
              f"{mk:>9} {d['attn'][qi, j]:8.4f}")
    print(f"  row sums to {d['attn'][qi].sum():.6f}; "
          f"{int((d['attn'][qi] == 0).sum())} of {T} entries are exactly 0 (masked)")

    with torch.no_grad():
        logits, _ = model(ids)
    p = softmax(logits[0, -1], dim=-1)
    top = torch.topk(p, 8)
    print(f"\n--- what the model predicts after '{words[-1]}' ---")
    for prob, i in zip(top.values.tolist(), top.indices.tolist()):
        print(f"  {tok.itos[i]:<16} {prob:6.3%}")
    return d


def overflow_demo():
    """Why the max subtraction is not optional."""
    big = torch.tensor([[800.0, 799.0, 795.0]])
    print("scores               :", big.tolist()[0])
    print("naive exp/sum        :", naive_softmax(big).tolist()[0], " <- nan")
    print("max-subtracted       :", [round(v, 6) for v in softmax(big).tolist()[0]])
    print("torch.softmax        :", [round(v, 6) for v in torch.softmax(big, -1).tolist()[0]])


# ---------------------------------------------------------------------------
# 10. CLI
# ---------------------------------------------------------------------------

def pick_device(name="auto"):
    if name != "auto":
        return name
    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--train", action="store_true")
    ap.add_argument("--sample", action="store_true")
    ap.add_argument("--explain", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--baselines", action="store_true")
    ap.add_argument("--overflow", action="store_true")
    ap.add_argument("--size", default="small", choices=list(SIZES))
    ap.add_argument("--steps", type=int, default=2000)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--device", default="auto")
    ap.add_argument("--prompt", default="the adaptive cruise control")
    ap.add_argument("--sentence", default=DEMO)
    ap.add_argument("--layer", type=int, default=0)
    ap.add_argument("--head", type=int, default=0)
    ap.add_argument("--query-word", default=None)
    ap.add_argument("--log", default=None)
    a = ap.parse_args()
    dev = pick_device(a.device)
    cfg = Config(**SIZES[a.size])

    if a.train:
        train(cfg, steps=a.steps, batch_size=a.batch_size, lr=a.lr, device=dev,
              log_path=a.log)
    if a.baselines:
        print(json.dumps(count_baselines(cfg), indent=2))
    if a.overflow:
        overflow_demo()
    if a.explain:
        explain(a.sentence, layer=a.layer, head=a.head, query_word=a.query_word,
                device=dev if dev != "mps" else "cpu")
    if a.check:
        model, tok, _ = load_trained()
        ids = torch.tensor([tok.encode(a.sentence)])
        d = numpy_attention_head(model, ids, layer=a.layer, head=a.head)
        print(f"NumPy re-derivation of layer {a.layer} head {a.head} matches PyTorch "
              f"to {d['max_abs_err']:.2e}")
    if a.sample:
        model, tok, ck = load_trained(dev if dev != "mps" else "cpu")
        ids = torch.tensor([tok.encode(a.prompt)])
        out = model.generate(ids, max_new_tokens=50, temperature=0.9, top_k=40,
                             eos_id=tok.eos_id)
        print(tok.decode(out[0]))
    if not any([a.train, a.sample, a.explain, a.check, a.baselines, a.overflow]):
        ap.print_help()


if __name__ == "__main__":
    main()
