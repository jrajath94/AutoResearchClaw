"""CRISP transformer validation: 1-layer transformer on (a + b) mod p.

Cross-architecture validation requested by paper council (P2.2).  Following
the canonical Nanda et al. 2023 setup: 1 transformer block, attention head
of dim w/heads, learned positional embeddings, 3-token sequence "[a] [b] [=]"
predicting the answer.  Records the same superposition / Fisher / grokking
metrics as the MLP version so post-hoc analysis is uniform across both
architectures.

Usage:
    python reproduce_transformer.py \\
        --output-dir results/transformer_mod47 \\
        --widths 64 96 128 \\
        --fractions 0.3 0.4 0.5 0.6 0.7 \\
        --seeds 42 137 256
"""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


P_DEFAULT = 47
WIDTHS = [64, 96, 128]
FRACTIONS = [0.3, 0.4, 0.5, 0.6, 0.7]
SEEDS = [42, 137, 256]
STEPS = 10_000
EVAL_EVERY = 100
LR = 1e-3
WD = 1.0           # heavy weight decay common in Nanda setup
GROK_THRESHOLD = 0.90
MEMORIZE_THRESHOLD = 0.99


# ============================================================================
# Tiny transformer (1 block, multi-head attention, MLP)
# ============================================================================
class TinyTransformer(nn.Module):
    """1-block transformer for sequence "[a, b, =]" predicting label.

    Vocab size = p + 1 (p number tokens + 1 "=" separator).
    Sequence length = 3.
    Predicts next-token at position 2 (the "=" position).
    """

    def __init__(self, p: int, width: int, n_heads: int = 4) -> None:
        super().__init__()
        assert width % n_heads == 0, "width must be divisible by n_heads"
        self.p = p
        self.width = width
        self.n_heads = n_heads
        self.head_dim = width // n_heads

        self.tok_embed = nn.Embedding(p + 1, width)         # tokens 0..p-1 plus "="
        self.pos_embed = nn.Embedding(3, width)             # 3 positions

        self.W_q = nn.Linear(width, width, bias=False)
        self.W_k = nn.Linear(width, width, bias=False)
        self.W_v = nn.Linear(width, width, bias=False)
        self.W_o = nn.Linear(width, width, bias=False)

        self.mlp_in = nn.Linear(width, 4 * width)
        self.mlp_out = nn.Linear(4 * width, width)

        self.head = nn.Linear(width, p, bias=False)         # outputs over p classes

    def forward(self, a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
        """a, b: (batch,) int tensors; returns logits at the '=' position (batch, p)."""
        eq = torch.full_like(a, fill_value=self.p)
        seq = torch.stack([a, b, eq], dim=1)                # (B, 3)
        pos = torch.arange(3, device=seq.device).unsqueeze(0).expand_as(seq)
        x = self.tok_embed(seq) + self.pos_embed(pos)       # (B, 3, w)

        # ---- Attention block (no causal mask: small task, full attention)
        B, T, W = x.shape
        q = self.W_q(x).view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        k = self.W_k(x).view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        v = self.W_v(x).view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        attn_logits = (q @ k.transpose(-1, -2)) / math.sqrt(self.head_dim)
        attn = attn_logits.softmax(dim=-1)
        h = (attn @ v).transpose(1, 2).reshape(B, T, W)
        h = self.W_o(h)
        x = x + h                                           # residual

        # ---- MLP block
        m = self.mlp_out(F.relu(self.mlp_in(x)))
        x = x + m
        return self.head(x[:, 2, :])                        # logits at "=" position

    @property
    def readout_weight(self) -> torch.Tensor:
        return self.head.weight                             # (p, w)

    @property
    def embed_a(self) -> torch.Tensor:
        """Number-token embeddings -- p rows of shape (p, w)."""
        return self.tok_embed.weight[: self.p]              # (p, w)

    @property
    def embed_b(self) -> torch.Tensor:
        """Same embedding table -- but distinguish by position."""
        return self.tok_embed.weight[: self.p]              # same as embed_a here

    @torch.no_grad()
    def hidden_per_class(self, p: int) -> torch.Tensor:
        """Mean post-attention representation at "=" position per output class."""
        device = self.tok_embed.weight.device
        all_a = torch.arange(p, device=device).repeat_interleave(p)
        all_b = torch.arange(p, device=device).repeat(p)
        labels = (all_a + all_b) % p

        eq = torch.full_like(all_a, fill_value=self.p)
        seq = torch.stack([all_a, all_b, eq], dim=1)
        pos = torch.arange(3, device=device).unsqueeze(0).expand_as(seq)
        x = self.tok_embed(seq) + self.pos_embed(pos)

        B, T, W = x.shape
        q = self.W_q(x).view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        k = self.W_k(x).view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        v = self.W_v(x).view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        attn = ((q @ k.transpose(-1, -2)) / math.sqrt(self.head_dim)).softmax(dim=-1)
        h = (attn @ v).transpose(1, 2).reshape(B, T, W)
        h_eq = (x + self.W_o(h))[:, 2, :]                   # (p^2, w) post-attn at "="

        per_class = torch.zeros(p, h_eq.shape[1], device=device)
        for c in range(p):
            mask = labels == c
            per_class[c] = h_eq[mask].mean(0)
        return per_class


# ============================================================================
# Metrics (re-imports from reproduce_v2 logic, inlined for portability)
# ============================================================================
@torch.no_grad()
def superposition_index(M: torch.Tensor, axis: str = "row") -> float:
    if axis == "col":
        M = M.T
    norms = M.norm(dim=1, keepdim=True).clamp_min(1e-12)
    M_hat = M / norms
    G = M_hat @ M_hat.T
    F_ = G.shape[0]
    off = G.pow(2).sum() - torch.diagonal(G).pow(2).sum()
    return float(off / (F_ * (F_ - 1)))


@torch.no_grad()
def effective_rank_gram(M: torch.Tensor) -> float:
    G = M @ M.T
    eig = torch.linalg.eigvalsh(G).clamp_min(0)
    eig_norm = eig / (eig.sum() + 1e-12)
    H = -(eig_norm * (eig_norm + 1e-12).log()).sum()
    return float(torch.exp(H))


def fisher_trace(model: nn.Module, a: torch.Tensor, b: torch.Tensor,
                 y: torch.Tensor) -> float:
    model.train(False)
    n = len(a)
    total = 0.0
    for j in range(n):
        model.zero_grad(set_to_none=True)
        logits = model(a[j:j + 1], b[j:j + 1])
        loss = F.cross_entropy(logits, y[j:j + 1])
        loss.backward()
        sq = sum((p.grad.detach() ** 2).sum().item()
                 for p in model.parameters() if p.grad is not None)
        total += sq
    model.zero_grad(set_to_none=True)
    return total / max(n, 1)


def grad_sq_norm(model: nn.Module) -> float:
    return sum((p.grad.detach() ** 2).sum().item()
               for p in model.parameters() if p.grad is not None)


# ============================================================================
# Single run
# ============================================================================
def run_single(width: int, frac: float, seed: int, p: int, steps: int,
               eval_every: int, device: torch.device,
               fisher_subsample: int = 32) -> dict:
    torch.manual_seed(seed); np.random.seed(seed)

    pairs = torch.tensor([(a, b) for a in range(p) for b in range(p)], dtype=torch.long)
    labels = (pairs[:, 0] + pairs[:, 1]) % p
    g = torch.Generator().manual_seed(seed)
    perm = torch.randperm(len(pairs), generator=g)
    pairs, labels = pairs[perm], labels[perm]

    n_train = int(round(frac * len(pairs)))
    a_tr, b_tr = pairs[:n_train, 0].to(device), pairs[:n_train, 1].to(device)
    a_te, b_te = pairs[n_train:, 0].to(device), pairs[n_train:, 1].to(device)
    y_tr, y_te = labels[:n_train].to(device), labels[n_train:].to(device)

    model = TinyTransformer(p=p, width=width).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=WD)

    hist = {
        "step": [], "train_acc": [], "test_acc": [], "train_loss": [], "test_loss": [],
        "S_W_out": [], "S_tok_embed": [], "S_H_class": [],
        "eff_rank_W_out": [], "eff_rank_tok_embed": [],
        "fisher_trace": [], "cum_grad_sq": [],
    }
    cum_grad_sq = 0.0
    grok_step = mem_step = None

    for step in range(1, steps + 1):
        model.train()
        logits = model(a_tr, b_tr)
        loss = F.cross_entropy(logits, y_tr)
        opt.zero_grad(); loss.backward()
        cum_grad_sq += grad_sq_norm(model)
        opt.step()

        if step % eval_every == 0 or step == steps:
            with torch.no_grad():
                tr_logits = model(a_tr, b_tr)
                te_logits = model(a_te, b_te)
                tr_acc = (tr_logits.argmax(-1) == y_tr).float().mean().item()
                te_acc = (te_logits.argmax(-1) == y_te).float().mean().item()
                tr_loss = F.cross_entropy(tr_logits, y_tr).item()
                te_loss = F.cross_entropy(te_logits, y_te).item()

            S_out = superposition_index(model.readout_weight, axis="row")
            S_tok = superposition_index(model.embed_a, axis="row")
            H_class = model.hidden_per_class(p)
            S_h = superposition_index(H_class, axis="row")

            er_W = effective_rank_gram(model.readout_weight)
            er_t = effective_rank_gram(model.embed_a)

            sub_idx = torch.randperm(
                n_train, generator=torch.Generator().manual_seed(seed + step)
            )[: min(fisher_subsample, n_train)]
            ft = fisher_trace(model, a_tr[sub_idx], b_tr[sub_idx], y_tr[sub_idx])

            hist["step"].append(step)
            hist["train_acc"].append(round(tr_acc, 6))
            hist["test_acc"].append(round(te_acc, 6))
            hist["train_loss"].append(round(tr_loss, 6))
            hist["test_loss"].append(round(te_loss, 6))
            hist["S_W_out"].append(round(S_out, 8))
            hist["S_tok_embed"].append(round(S_tok, 8))
            hist["S_H_class"].append(round(S_h, 8))
            hist["eff_rank_W_out"].append(round(er_W, 4))
            hist["eff_rank_tok_embed"].append(round(er_t, 4))
            hist["fisher_trace"].append(round(ft, 8))
            hist["cum_grad_sq"].append(round(cum_grad_sq, 6))

            if mem_step is None and tr_acc >= MEMORIZE_THRESHOLD:
                mem_step = step
            if grok_step is None and mem_step is not None and te_acc >= GROK_THRESHOLD:
                grok_step = step

    S_drop_steps: dict = {}
    for key in ("S_W_out", "S_tok_embed", "S_H_class"):
        traj = hist[key]
        S0 = traj[0] if traj else 0.0
        drop = None
        for st, S in zip(hist["step"], traj):
            if S < 0.5 * S0:
                drop = st
                break
        S_drop_steps[f"{key}_drop_step"] = drop

    delay = (grok_step - mem_step) if (grok_step and mem_step) else None
    return {
        "width": width, "train_frac": frac, "seed": seed,
        "task": f"transformer_add_mod_{p}",
        "n_train": n_train,
        **hist,
        "grokked": grok_step is not None,
        "grok_step": grok_step, "mem_step": mem_step, "delay": delay,
        **S_drop_steps,
        "final_test_acc": hist["test_acc"][-1] if hist["test_acc"] else 0.0,
        "final_test_loss": hist["test_loss"][-1] if hist["test_loss"] else float("inf"),
    }


# ============================================================================
# Main
# ============================================================================
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", default="results_transformer")
    ap.add_argument("--p", type=int, default=P_DEFAULT)
    ap.add_argument("--widths", nargs="+", type=int, default=WIDTHS)
    ap.add_argument("--fractions", nargs="+", type=float, default=FRACTIONS)
    ap.add_argument("--seeds", nargs="+", type=int, default=SEEDS)
    ap.add_argument("--steps", type=int, default=STEPS)
    ap.add_argument("--eval-every", type=int, default=EVAL_EVERY)
    ap.add_argument("--fisher-subsample", type=int, default=32)
    args = ap.parse_args()

    out = Path(args.output_dir); out.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[transformer] device={device}  p={args.p}")
    print(f"  widths={args.widths}  fractions={args.fractions}  seeds={args.seeds}")

    all_results: dict = {}
    total = len(args.widths) * len(args.fractions) * len(args.seeds)
    i = 0
    t_start = time.time()

    for w in args.widths:
        for f in args.fractions:
            for s in args.seeds:
                i += 1
                key = f"w{w}_f{f}_s{s}_xfmr{args.p}"
                run_path = out / f"run_{key}.json"
                if run_path.exists():
                    all_results[key] = json.loads(run_path.read_text())
                    print(f"[{i:3d}/{total}] {key} (resumed)", flush=True)
                    continue
                t0 = time.time()
                r = run_single(
                    width=w, frac=f, seed=s, p=args.p,
                    steps=args.steps, eval_every=args.eval_every,
                    device=device, fisher_subsample=args.fisher_subsample,
                )
                run_path.write_text(json.dumps(r, indent=2))
                all_results[key] = r
                dt = time.time() - t0
                eta = (time.time() - t_start) / i * (total - i)
                print(
                    f"[{i:3d}/{total}] {key}  grok={r['grokked']}  "
                    f"S_H={r['S_H_class'][-1]:.4f}  S_tok={r['S_tok_embed'][-1]:.4f}  "
                    f"dt={dt:.1f}s  eta={eta/60:.1f}min", flush=True
                )
                # Update aggregate after each run too
                (out / f"sweep_xfmr_mod{args.p}.json").write_text(
                    json.dumps(all_results, indent=2))

    (out / f"sweep_xfmr_mod{args.p}.json").write_text(json.dumps(all_results, indent=2))
    print(f"[transformer] done.  total time = {(time.time() - t_start) / 60:.1f} min")


if __name__ == "__main__":
    main()
