"""CRISP v2: fully-instrumented reproduction script.

Adds the metrics required by the NeurIPS 2026 revision checklist:
  - True superposition index S(W_out) at every checkpoint  (closes F3 gap)
  - Fisher information trace tr(F_hat(t))                  (defines n_eff(t))
  - Accumulated gradient variance int ||g(s)||^2 ds        (alt n_eff proxy)
  - Effective rank of W_out W_out^T                        (drives F_eff(w))
  - Weight snapshot at final step                          (spectral analysis)

Backward-compatible JSON schema: all original fields preserved; new fields
are added without breaking parse_and_plot.py.

Usage:
    python reproduce_v2.py --output-dir results_v2/

Hardware: ~2 minutes per run on A40 GPU; ~4-5 min on Mac CPU.
Total: 120 runs * 2 min = ~4 GPU-hours.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


# -------- Defaults (mod-47 task, matches v1 paper sweep) ----------------------
P_DEFAULT = 47
WIDTHS = [32, 48, 64, 96, 128]
FRACTIONS = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
SEEDS = [42, 137, 256]
STEPS = 10_000
EVAL_EVERY = 100                    # 10x finer than v1 (was 1000)
LR = 0.03
WD = 0.3
GROK_THRESHOLD = 0.90
MEMORIZE_THRESHOLD = 0.99


# ============================================================================
# Models
# ============================================================================
class ModAddMLP(nn.Module):
    """Two-layer MLP with one-hot input on (a + b) mod p."""

    def __init__(self, width: int, p: int) -> None:
        super().__init__()
        self.p = p
        self.fc1 = nn.Linear(2 * p, width, bias=True)
        self.fc2 = nn.Linear(width, p, bias=True)

    def forward(self, x_ab: torch.Tensor) -> torch.Tensor:
        a = F.one_hot(x_ab[:, 0], self.p).float()
        b = F.one_hot(x_ab[:, 1], self.p).float()
        x = torch.cat([a, b], dim=-1)
        h = F.relu(self.fc1(x))
        return self.fc2(h)

    @property
    def readout_weight(self) -> torch.Tensor:
        """W_out: (p, width).  Each row = readout direction for one class."""
        return self.fc2.weight                              # shape (p, w)

    @property
    def embed_a(self) -> torch.Tensor:
        """W_in_a: (width, p).  Each column = embedding direction for token 'a=i'."""
        return self.fc1.weight[:, : self.p]                 # shape (w, p)

    @property
    def embed_b(self) -> torch.Tensor:
        """W_in_b: (width, p).  Each column = embedding direction for token 'b=i'."""
        return self.fc1.weight[:, self.p :]                 # shape (w, p)

    @torch.no_grad()
    def hidden_per_class(self, p: int) -> torch.Tensor:
        """Mean hidden activation per (a+b mod p) class on the full Cartesian grid.

        Returns: (p, width) -- the average h(a,b) over pairs sharing the same label.
        Used for measuring "feature collapse" in the hidden representation.
        """
        device = self.fc1.weight.device
        all_pairs = torch.tensor(
            [(a, b) for a in range(p) for b in range(p)], dtype=torch.long, device=device
        )
        a = F.one_hot(all_pairs[:, 0], p).float()
        b = F.one_hot(all_pairs[:, 1], p).float()
        h = F.relu(self.fc1(torch.cat([a, b], dim=-1)))     # (p^2, w)
        labels = (all_pairs[:, 0] + all_pairs[:, 1]) % p
        per_class = torch.zeros(p, h.shape[1], device=device)
        for c in range(p):
            mask = labels == c
            per_class[c] = h[mask].mean(0)
        return per_class                                    # (p, w)


# ============================================================================
# Datasets
# ============================================================================
def build_modular_dataset(p: int, op: str, seed: int) -> tuple[torch.Tensor, torch.Tensor]:
    """op in {'add', 'mul'}.  Returns shuffled (pairs, labels)."""
    pairs = torch.tensor([(a, b) for a in range(p) for b in range(p)], dtype=torch.long)
    if op == "add":
        labels = (pairs[:, 0] + pairs[:, 1]) % p
    elif op == "mul":
        labels = (pairs[:, 0] * pairs[:, 1]) % p
    else:
        raise ValueError(f"Unknown op: {op}")
    g = torch.Generator().manual_seed(seed)
    perm = torch.randperm(len(pairs), generator=g)
    return pairs[perm], labels[perm]


def split_train_test(pairs, labels, frac):
    n_train = int(round(frac * len(pairs)))
    return pairs[:n_train], labels[:n_train], pairs[n_train:], labels[n_train:]


# ============================================================================
# Metrics
# ============================================================================
@torch.no_grad()
def superposition_index(M: torch.Tensor, axis: str = "row") -> float:
    """S(M) = (1/F(F-1)) sum_{i!=j} |<m_hat_i, m_hat_j>|^2

    Computes averaged squared cosine similarity between rows (axis='row')
    or columns (axis='col') of M.  Range [0, 1]; 0 = orthogonal, 1 = collinear.

    Generalizes Eq. (3) of paper to any feature-bearing matrix.  We compute
    this on multiple candidate representations to identify *where* the
    superposition->clean transition lives:
      - S(W_out, axis='row')    : output-class readout directions
      - S(W_in_a, axis='col')   : input embedding for token 'a'
      - S(W_in_b, axis='col')   : input embedding for token 'b'
      - S(H_class, axis='row')  : per-class mean hidden activations
    """
    if axis == "col":
        M = M.T
    norms = M.norm(dim=1, keepdim=True).clamp_min(1e-12)
    M_hat = M / norms
    G = M_hat @ M_hat.T
    F_ = G.shape[0]
    off = G.pow(2).sum() - torch.diagonal(G).pow(2).sum()
    return float(off / (F_ * (F_ - 1)))


@torch.no_grad()
def effective_rank_gram(W_out: torch.Tensor) -> float:
    """exp( H(sigma_normalized) ) where sigma = eigenvalues of W_out W_out^T.

    Equivalent to the entropic effective rank used in Roy & Vetterli 2007.
    For F_eff(w) derivation: this drops as wider models discover Fourier basis.
    """
    G = W_out @ W_out.T
    eig = torch.linalg.eigvalsh(G).clamp_min(0)
    eig_norm = eig / (eig.sum() + 1e-12)
    H = -(eig_norm * (eig_norm + 1e-12).log()).sum()
    return float(torch.exp(H))


@torch.no_grad()
def effective_rank_activations(h: torch.Tensor) -> float:
    """Backward-compat: effective rank of activations (used by v1)."""
    h_centered = h - h.mean(0, keepdim=True)
    _, s, _ = torch.linalg.svd(h_centered, full_matrices=False)
    s = s / (s.sum() + 1e-12)
    H = -(s * (s + 1e-12).log()).sum()
    return float(torch.exp(H))


def fisher_trace(model: nn.Module, x: torch.Tensor, y: torch.Tensor,
                 batch: int = 64) -> float:
    """tr(F_hat) = E[ ||grad log p(y|x; theta)||^2 ].

    Empirical Fisher: average squared gradient norm over training data.
    This is the n_eff(t) building block (PAC-Bayes / MLE asymptotics).
    """
    model.train(False)
    n = len(x)
    total_sq = 0.0
    for j in range(n):
        model.zero_grad(set_to_none=True)
        logits = model(x[j:j + 1])
        loss = F.cross_entropy(logits, y[j:j + 1])
        loss.backward()
        sq = sum((p.grad.detach() ** 2).sum().item()
                 for p in model.parameters() if p.grad is not None)
        total_sq += sq
    model.zero_grad(set_to_none=True)
    return total_sq / max(n, 1)


def grad_sq_norm(model: nn.Module) -> float:
    """||g||^2 for the most recent backward pass.  Cheap; called every step."""
    return sum((p.grad.detach() ** 2).sum().item()
               for p in model.parameters() if p.grad is not None)


def compute_acc_loss(model, x, y):
    with torch.no_grad():
        logits = model(x)
        loss = F.cross_entropy(logits, y).item()
        acc = (logits.argmax(-1) == y).float().mean().item()
    return acc, loss


# ============================================================================
# Single run
# ============================================================================
def run_single(width: int, frac: float, seed: int, p: int, op: str,
               steps: int, eval_every: int,
               device: torch.device, fisher_subsample: int = 256) -> dict:
    """Returns dict ready for JSON serialization."""
    torch.manual_seed(seed)
    np.random.seed(seed)

    pairs, labels = build_modular_dataset(p=p, op=op, seed=seed)
    x_tr, y_tr, x_te, y_te = split_train_test(pairs, labels, frac)
    x_tr, y_tr = x_tr.to(device), y_tr.to(device)
    x_te, y_te = x_te.to(device), y_te.to(device)

    model = ModAddMLP(width, p=p).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=WD)

    hist = {
        "step": [], "train_acc": [], "test_acc": [],
        "train_loss": [], "test_loss": [],
        # Multiple S candidates -- council requested mechanism validation
        "S_W_out": [], "S_W_in_a": [], "S_W_in_b": [], "S_H_class": [],
        # Effective ranks of representation matrices
        "eff_rank_W_out": [], "eff_rank_W_in_a": [], "eff_rank_act": [],
        # n_eff(t) building blocks
        "fisher_trace": [], "cum_grad_sq": [],
    }
    cum_grad_sq = 0.0
    grok_step: int | None = None
    mem_step: int | None = None
    n_train = len(x_tr)

    for step in range(1, steps + 1):
        model.train()
        logits = model(x_tr)
        loss = F.cross_entropy(logits, y_tr)
        opt.zero_grad(); loss.backward()
        cum_grad_sq += grad_sq_norm(model)
        opt.step()

        if step % eval_every == 0 or step == steps:
            tr_acc, tr_loss = compute_acc_loss(model, x_tr, y_tr)
            te_acc, te_loss = compute_acc_loss(model, x_te, y_te)

            # ---- Multiple S candidates ------------------------------------
            S_out = superposition_index(model.readout_weight, axis="row")
            S_a   = superposition_index(model.embed_a,        axis="col")
            S_b   = superposition_index(model.embed_b,        axis="col")
            H_class = model.hidden_per_class(p)
            S_h   = superposition_index(H_class,              axis="row")

            # ---- Effective ranks ------------------------------------------
            er_W   = effective_rank_gram(model.readout_weight)
            er_in  = effective_rank_gram(model.embed_a.T)     # (p, w) matrix Gram
            x_sub = x_tr[: min(512, n_train)]
            with torch.no_grad():
                a = F.one_hot(x_sub[:, 0], p).float()
                b = F.one_hot(x_sub[:, 1], p).float()
                h_acts = F.relu(model.fc1(torch.cat([a, b], dim=-1)))
            er_a = effective_rank_activations(h_acts)

            # ---- Fisher trace (PAC-Bayes effective sample size building block)
            sub_idx = torch.randperm(
                n_train, generator=torch.Generator().manual_seed(seed + step)
            )[: min(fisher_subsample, n_train)]
            ft = fisher_trace(model, x_tr[sub_idx], y_tr[sub_idx])

            hist["step"].append(step)
            hist["train_acc"].append(round(tr_acc, 6))
            hist["test_acc"].append(round(te_acc, 6))
            hist["train_loss"].append(round(tr_loss, 6))
            hist["test_loss"].append(round(te_loss, 6))
            hist["S_W_out"].append(round(S_out, 8))
            hist["S_W_in_a"].append(round(S_a, 8))
            hist["S_W_in_b"].append(round(S_b, 8))
            hist["S_H_class"].append(round(S_h, 8))
            hist["eff_rank_W_out"].append(round(er_W, 4))
            hist["eff_rank_W_in_a"].append(round(er_in, 4))
            hist["eff_rank_act"].append(round(er_a, 4))
            hist["fisher_trace"].append(round(ft, 8))
            hist["cum_grad_sq"].append(round(cum_grad_sq, 6))

            if mem_step is None and tr_acc >= MEMORIZE_THRESHOLD:
                mem_step = step
            if grok_step is None and mem_step is not None and te_acc >= GROK_THRESHOLD:
                grok_step = step

    # Compute S-drop step for *each* candidate representation.  The one with
    # the cleanest correlation to grok_step identifies the locus of the
    # phase transition (this is what F3 actually validates).
    S_drop_steps: dict = {}
    for key in ("S_W_out", "S_W_in_a", "S_W_in_b", "S_H_class"):
        traj = hist[key]
        S0 = traj[0] if traj else 0.0
        drop_step: int | None = None
        for st, S in zip(hist["step"], traj):
            if S < 0.5 * S0:
                drop_step = st
                break
        S_drop_steps[f"{key}_drop_step"] = drop_step

    W_out_final = model.readout_weight.detach().cpu().tolist()
    W_in_a_final = model.embed_a.detach().cpu().tolist()
    W_in_b_final = model.embed_b.detach().cpu().tolist()
    delay = (grok_step - mem_step) if (grok_step and mem_step) else None

    return {
        "width": width, "train_frac": frac, "seed": seed,
        "task": f"{op}_mod_{p}", "n_train": n_train,
        **hist,
        "grokked": grok_step is not None,
        "grok_step": grok_step, "mem_step": mem_step,
        "delay": delay,
        **S_drop_steps,
        "final_test_acc": hist["test_acc"][-1] if hist["test_acc"] else 0.0,
        "final_test_loss": hist["test_loss"][-1] if hist["test_loss"] else float("inf"),
        "W_out_final": W_out_final,
        "W_in_a_final": W_in_a_final,
        "W_in_b_final": W_in_b_final,
    }


# ============================================================================
# Aggregation
# ============================================================================
def aggregate(results: dict) -> dict:
    per_cond: dict = {}
    for r in results.values():
        key = f"w{r['width']}_f{r['train_frac']}"
        per_cond.setdefault(key, []).append(r)

    summary = {}
    grokked_total = 0
    for key, runs in per_cond.items():
        rate = sum(r["grokked"] for r in runs) / len(runs)
        mean_acc = float(np.mean([r["final_test_acc"] for r in runs]))
        delays = [r["delay"] for r in runs if r["delay"] is not None]
        summary[key] = {
            "grok_rate": rate,
            "mean_test_acc": round(mean_acc, 4),
            "mean_delay": float(np.mean(delays)) if delays else None,
            "mean_S_W_out_final": round(
                float(np.mean([r["S_W_out"][-1] for r in runs])), 6),
            "mean_S_W_in_a_final": round(
                float(np.mean([r["S_W_in_a"][-1] for r in runs])), 6),
            "mean_S_H_class_final": round(
                float(np.mean([r["S_H_class"][-1] for r in runs])), 6),
            "mean_eff_rank_W_out_final": round(
                float(np.mean([r["eff_rank_W_out"][-1] for r in runs])), 4),
            "mean_eff_rank_W_in_final": round(
                float(np.mean([r["eff_rank_W_in_a"][-1] for r in runs])), 4),
        }
        grokked_total += sum(r["grokked"] for r in runs)

    return {
        "total_runs": len(results),
        "grokked_runs": grokked_total,
        "grokking_rate": grokked_total / max(len(results), 1),
        "per_condition": summary,
    }


# ============================================================================
# Main
# ============================================================================
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", default="results_v2")
    ap.add_argument("--p", type=int, default=P_DEFAULT, help="prime modulus")
    ap.add_argument("--op", default="add", choices=["add", "mul"])
    ap.add_argument("--widths", nargs="+", type=int, default=WIDTHS)
    ap.add_argument("--fractions", nargs="+", type=float, default=FRACTIONS)
    ap.add_argument("--seeds", nargs="+", type=int, default=SEEDS)
    ap.add_argument("--steps", type=int, default=STEPS)
    ap.add_argument("--eval-every", type=int, default=EVAL_EVERY)
    ap.add_argument("--fisher-subsample", type=int, default=256)
    ap.add_argument("--save-weights", action="store_true",
                    help="save W_out_final in JSON (~50KB per run)")
    args = ap.parse_args()

    out = Path(args.output_dir); out.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[reproduce_v2] device={device}  p={args.p}  op={args.op}")
    print(f"  widths={args.widths}  fractions={args.fractions}  seeds={args.seeds}")
    print(f"  steps={args.steps}  eval_every={args.eval_every}")

    all_results: dict = {}
    total = len(args.widths) * len(args.fractions) * len(args.seeds)
    i = 0
    t_start = time.time()

    for w in args.widths:
        for f in args.fractions:
            for s in args.seeds:
                i += 1
                t0 = time.time()
                r = run_single(
                    width=w, frac=f, seed=s, p=args.p, op=args.op,
                    steps=args.steps, eval_every=args.eval_every,
                    device=device, fisher_subsample=args.fisher_subsample,
                )
                if not args.save_weights:
                    r.pop("W_out_final", None)
                    r.pop("W_in_a_final", None)
                    r.pop("W_in_b_final", None)
                key = f"w{w}_f{f}_s{s}_{args.op}{args.p}"
                all_results[key] = r
                dt = time.time() - t0
                eta = (time.time() - t_start) / i * (total - i)
                print(
                    f"[{i:3d}/{total}] {key}  grok={r['grokked']}  "
                    f"S_W_out={r['S_W_out'][-1]:.4f}  "
                    f"S_H_class={r['S_H_class'][-1]:.4f}  "
                    f"dt={dt:.1f}s  eta={eta/60:.1f}min"
                )

    (out / f"sweep_{args.op}{args.p}.json").write_text(
        json.dumps(all_results, indent=2))
    (out / f"summary_{args.op}{args.p}.json").write_text(
        json.dumps(aggregate(all_results), indent=2))
    print(f"[reproduce_v2] done.  total time = {(time.time() - t_start) / 60:.1f} min")


if __name__ == "__main__":
    main()
