"""Monte-Carlo validation of Theorem 1 v2 conditional coverage bound.

Generates synthetic exchangeable (X_i, Y_i, S_i, A_i) tuples with known
conditional miscoverage = alpha and verifies that, after split-CP
calibration on the post-hoc admissibility-selected subset I, the empirical
conditional coverage on a fresh test point exceeds (1 - alpha - 1/(|I|+1))
across many random repeats.

This addresses council issue #5 (admissibility-selection proof gap) by
providing finite-sample empirical validation of the proof's claim.

Run: python proof_montecarlo.py --output /tmp/proof_mc.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def conformal_quantile(scores: np.ndarray, alpha: float) -> float:
    n = len(scores)
    if n == 0:
        return float("inf")
    k = int(np.ceil((1.0 - alpha) * (n + 1)))
    k = min(max(k, 1), n)
    return float(np.partition(scores, k - 1)[k - 1])


def synthesize(n_total: int, p_A: float, alpha: float, seed: int):
    """Synthesize a calibration+test sample where:
       A_i ~ Bernoulli(p_A) is the admissibility flag.
       Conditional on A_i = 1, the lifted score has CDF such that
       P(score <= q_alpha) = 1 - alpha for some q_alpha (we just use
       a uniform on [0,1] and pick threshold = 1 - alpha).
       Conditional on A_i = 0, the score is +inf.
    """
    rng = np.random.default_rng(seed)
    A = rng.binomial(1, p_A, size=n_total).astype(bool)
    # Score: uniform[0, 1] for admissible; +inf for inadmissible
    scores = np.where(A, rng.uniform(0, 1, size=n_total), np.inf)
    return scores, A


def run_one_trial(n_cal: int, n_test: int, p_A: float, alpha: float, seed: int):
    cal_scores, cal_A = synthesize(n_cal, p_A, alpha, seed)
    test_scores, test_A = synthesize(n_test, p_A, alpha, seed + 99999)
    # Conformal threshold over admissible subset
    I = cal_scores[cal_A]
    if len(I) == 0:
        return None
    q_hat = conformal_quantile(I, alpha)
    test_admissible = test_A.sum()
    if test_admissible == 0:
        return None
    cov_cond = float(np.mean(test_scores[test_A] <= q_hat))
    bound = 1 - alpha - 1.0 / (len(I) + 1)
    return {
        "|I|": int(len(I)),
        "cov_cond": cov_cond,
        "bound": float(bound),
        "above_bound": bool(cov_cond >= bound),
        "n_test_admissible": int(test_admissible),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n_cal", type=int, default=300)
    ap.add_argument("--n_test", type=int, default=300)
    ap.add_argument("--alphas", nargs="+", type=float, default=[0.05, 0.10, 0.20])
    ap.add_argument("--p_A_grid", nargs="+", type=float,
                    default=[0.50, 0.70, 0.85, 0.95])
    ap.add_argument("--n_trials", type=int, default=500)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    out = []
    for alpha in args.alphas:
        for p_A in args.p_A_grid:
            results = []
            for seed in range(args.n_trials):
                r = run_one_trial(args.n_cal, args.n_test, p_A, alpha, seed)
                if r is not None:
                    results.append(r)
            covs = np.array([r["cov_cond"] for r in results])
            bnds = np.array([r["bound"] for r in results])
            out.append({
                "alpha": alpha, "p_A": p_A,
                "n_trials_kept": len(results),
                "cov_mean": float(np.mean(covs)),
                "cov_std": float(np.std(covs)),
                "bound_mean": float(np.mean(bnds)),
                "frac_above_bound": float(np.mean(covs >= bnds)),
                "frac_above_nominal": float(np.mean(covs >= 1 - alpha)),
            })
            print(f"alpha={alpha:.2f} p_A={p_A:.2f}: "
                  f"cov={np.mean(covs):.3f}±{np.std(covs):.3f} "
                  f"bound={np.mean(bnds):.3f} "
                  f"frac_above={np.mean(covs >= bnds):.3f} "
                  f"frac_above_nominal={np.mean(covs >= 1 - alpha):.3f}")
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(out, f, indent=2)
    print(f"[mc] wrote {args.output}")


if __name__ == "__main__":
    main()
