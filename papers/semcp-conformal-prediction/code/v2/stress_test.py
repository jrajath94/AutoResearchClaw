"""100-fold cal/test resampling stress test for empirical coverage validity.

For each method on each dataset, run 100 independent random cal/test
splits. Plot the empirical conditional coverage CDF and verify that the
distribution sits at or above the theoretical bound 1-α-1/(|I|+1).

This addresses council weakness "no per-question conditional coverage
verification" — the figure would show the spread of empirical conditional
coverage across resamples, demonstrating that the guarantee holds in
distribution, not just on average.

Run on the pre-built pool .json + .npz (no GPU required after pools exist).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[0]))

from methods.base import CPSamplePool
from methods.conu import ConU
from semcp_v2 import SemCPv2
from baselines_tuned import TunedSAFER, TunedLofreeCP, TunedTECP


METHOD_REGISTRY = {
    "semcp_v2": SemCPv2,
    "conu": ConU,
    "safer_tuned": TunedSAFER,
    "lofreecp_tuned": TunedLofreeCP,
    "tecp_tuned": TunedTECP,
}


def load_pools(base: str):
    with open(base + ".json") as f:
        meta = json.load(f)
    npz = np.load(base + ".npz")
    pools = []
    for i, m in enumerate(meta):
        emb = npz[f"emb_{i}"]
        pools.append(CPSamplePool(
            qid=m["qid"], question=m["question"], samples=m["samples"],
            references=m["references"], sample_correct=m["sample_correct"],
            cluster_ids=m["cluster_ids"], cluster_correct=m["cluster_correct"],
            cluster_reps=m["cluster_reps"], embeddings=emb,
            extra=m.get("extra", {}),
        ))
    return pools


def split_cal_test(pools, frac, seed):
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(pools))
    n_cal = int(len(idx) * frac)
    return [pools[i] for i in idx[:n_cal]], [pools[i] for i in idx[n_cal:]]


def run_one_split(method_name, pools, alpha, seed):
    cls = METHOD_REGISTRY[method_name]
    method = cls()
    cal, test = split_cal_test(pools, 0.5, seed)
    method.calibrate(cal, alpha)
    correct, sizes, abstained, admissible = [], [], [], []
    for p in test:
        pred = method.predict(p, alpha)
        correct.append(pred.correct_in_set)
        admissible.append(any(p.cluster_correct))
        sizes.append(pred.set_size)
        abstained.append(pred.abstained)
    correct = np.array(correct, dtype=bool)
    admissible = np.array(admissible, dtype=bool)
    if admissible.sum() == 0:
        return None
    return {
        "cov_cond": float(correct[admissible].mean()),
        "cov_marg": float(correct.mean()),
        "set_size": float(np.mean(sizes)),
        "abstain": float(np.mean(abstained)),
        "n_cal_admissible": int(sum(1 for p in cal if any(p.cluster_correct))),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool_base", required=True)
    ap.add_argument("--out_json", required=True)
    ap.add_argument("--out_pdf", required=True)
    ap.add_argument("--methods", nargs="+", default=list(METHOD_REGISTRY.keys()))
    ap.add_argument("--n_folds", type=int, default=100)
    ap.add_argument("--alpha", type=float, default=0.10)
    args = ap.parse_args()

    pools = load_pools(args.pool_base)
    print(f"[stress] {len(pools)} pools, {args.n_folds} folds, {len(args.methods)} methods")

    out = {}
    for m in args.methods:
        out[m] = []
        for f in range(args.n_folds):
            r = run_one_split(m, pools, args.alpha, seed=f * 17 + 1)
            if r is not None:
                out[m].append(r)
        covs = [r["cov_cond"] for r in out[m]]
        print(f"  {m:<18} cov_cond mean={np.mean(covs):.3f} std={np.std(covs):.3f} "
              f"min={np.min(covs):.3f} q05={np.percentile(covs, 5):.3f}")

    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_json).write_text(json.dumps(out, indent=2))

    # Plot CDFs
    fig, ax = plt.subplots(figsize=(7, 4))
    palette = {"semcp_v2": "#2E86AB", "conu": "#E76F51",
                "safer_tuned": "#F4A261", "lofreecp_tuned": "#264653",
                "tecp_tuned": "#8B5CF6"}
    display = {"semcp_v2": "SemCP", "conu": "ConU",
                "safer_tuned": "SAFER", "lofreecp_tuned": "LofreeCP",
                "tecp_tuned": "TECP"}
    for m in args.methods:
        if not out[m]:
            continue
        covs = sorted([r["cov_cond"] for r in out[m]])
        cdf = np.arange(1, len(covs) + 1) / len(covs)
        ax.plot(covs, cdf, label=display.get(m, m),
                color=palette.get(m, "gray"), lw=2)
    # Theoretical bound (approximate, assumes ~p_A * 150 admissible cal points)
    ax.axvline(1 - args.alpha, ls="--", color="gray", label=f"$1-\\alpha = {1 - args.alpha}$")
    ax.set_xlabel("Empirical conditional coverage")
    ax.set_ylabel("CDF over 100 resamples")
    ax.set_title(f"Stress test: 100-fold cal/test conditional coverage CDF")
    ax.legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig(args.out_pdf, bbox_inches="tight")
    print(f"[stress] wrote {args.out_pdf}, {args.out_json}")


if __name__ == "__main__":
    main()
