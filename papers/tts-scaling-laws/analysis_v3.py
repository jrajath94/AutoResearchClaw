"""STAIR V3 statistical analysis — applies the V2 statistics pipeline to the
new V3 inference results (Qwen3.6-35B-A3B, Llama 4 Scout, Qwen3-4B local).

Input: real_results_v3/results_<model>_<dataset>.npy  (n_problems, n_budgets, n_temps, n_samples)
Output: revised_v3_stats.json containing:

  - Headline staircase rate (overall, variation subset, BH-corrected variation)
  - Negative-control shuffled-label rate
  - Snell power-law BIC comparison
  - Baringhaus-Henze log-concavity test on tau distribution
  - TOST equivalence test for STAIR vs fixed-budget-best
  - p99 latency from the meta JSON
  - per-budget accuracy curves

This script is the analysis-side partner to experiment/real_experiment_v2.py.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

# Reuse the V2 statistical primitives unchanged
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analysis_v2 import (  # type: ignore
    bic_from_ll, benjamini_hochberg, fit_staircase, fit_sigmoid,
    fit_snell_powerlaw, select_per_cell, log_concavity_baringhaus_henze,
    tost_equivalence,
)
from scipy import stats  # for Spearman trend test


# ─────────────────────────────────────────────────────────────────────────────
# Penalty-bias-free per-cell tests (replace BIC headline; BIC is now diagnostic)
# ─────────────────────────────────────────────────────────────────────────────


def spearman_trend_pvalue(k_traj: np.ndarray, S: int) -> float:
    """One-sided Spearman test: is accuracy monotonically increasing with budget?

    Returns the one-tailed p-value (small p means real upward trend, NOT a
    flat or noisy curve). This test is NOT subject to BIC's DOF-penalty bias
    because it makes no parametric assumption.
    """
    accuracies = k_traj / max(S, 1)
    if accuracies.std() < 1e-9:
        return 1.0
    rho, p_two = stats.spearmanr(np.arange(len(accuracies)), accuracies)
    # one-sided test for positive trend
    return float(p_two / 2.0) if rho > 0 else float(1.0 - p_two / 2.0)


def staircase_shape_coefficient(k_traj: np.ndarray, S: int) -> tuple[float, int]:
    """Variance fraction captured by the best single split (R² for the
    staircase model). High R² (>0.7) = curve concentrates its variance in one
    discrete jump = staircase-like. Low R² = variance spread across multiple
    transitions = smoother shape.

    Returns (r_squared, best_split_idx).
    """
    a = k_traj / max(S, 1)
    if a.std() < 1e-9:
        return 0.0, 0
    total_var = float(np.var(a) * len(a))
    best_split, best_explained = 0, 0.0
    for split in range(1, len(a)):
        left, right = a[:split], a[split:]
        n_l, n_r = len(left), len(right)
        # variance reduction from splitting: total - (within-segment SS)
        ss_within = float(((left - left.mean()) ** 2).sum() + ((right - right.mean()) ** 2).sum())
        explained = total_var - ss_within
        if explained > best_explained:
            best_explained = explained
            best_split = split
    r_squared = float(best_explained / max(total_var, 1e-9))
    return r_squared, best_split

REPO = Path(__file__).resolve().parent
RESULTS_DIR = REPO / "real_results_v3"


def analyze_v3(npy_path: Path, meta_path: Path | None = None,
               q: float = 0.05, n_neg_seeds: int = 5) -> dict:
    """V3 raw-array analysis: input shape is (n_problems, n_budgets, n_temps, n_samples).

    We aggregate per-cell to success counts (n_problems, n_budgets, n_temps),
    then run the V2 BIC + negative-control + log-concavity pipeline.
    """
    correct = np.load(npy_path)
    if correct.ndim == 4:
        n_problems, n_budgets, n_temps, n_samples = correct.shape
        successes = correct.sum(axis=-1).astype(np.int64)
    elif correct.ndim == 3:
        # Already aggregated; assume the values are mean accuracy in [0,1] and
        # samples_per_cell must be supplied externally via meta.
        n_problems, n_budgets, n_temps = correct.shape
        n_samples = 8
        successes = np.rint(correct * n_samples).astype(np.int64)
    else:
        raise ValueError(f"unexpected ndim {correct.ndim}")
    S = int(n_samples)

    # Reconstruct the budget grid from meta if available; else use defaults
    if meta_path and meta_path.exists():
        meta = json.loads(meta_path.read_text())
        budgets = np.asarray(meta.get("budgets", [32, 64, 128, 256, 512, 1024]), dtype=float)
    else:
        meta = {}
        budgets = np.asarray([32, 64, 128, 256, 512, 1024], dtype=float)
    if len(budgets) != n_budgets:
        budgets = np.asarray([2 ** (5 + i) for i in range(n_budgets)], dtype=float)

    # ── Per-cell BIC selection (now demoted to diagnostic; primary tests are
    # the Spearman trend test and staircase shape coefficient added below)
    favored, has_var, pvals, tau_bs, n_succ = [], [], [], [], []
    delta_pow_minus_step = []
    spearman_pvals, shape_r2 = [], []
    for p_idx in range(n_problems):
        for t_idx in range(n_temps):
            k_traj = successes[p_idx, :, t_idx]
            res = select_per_cell(k_traj, S, budgets)
            favored.append(res["favored"] == "staircase")
            has_var.append(res["has_variation"])
            pvals.append(res["p_lrt_sig_vs_step"])
            tau_bs.append(res["tau_budget"])
            n_succ.append(res["n_successes_total"])
            delta_pow_minus_step.append(res["delta_bic_pow_minus_step"])
            spearman_pvals.append(spearman_trend_pvalue(k_traj, S))
            r2, _ = staircase_shape_coefficient(k_traj, S)
            shape_r2.append(r2)
    favored = np.array(favored)
    has_var = np.array(has_var)
    pvals = np.array(pvals)
    tau_bs = np.array(tau_bs)
    delta_pow = np.array(delta_pow_minus_step)
    spearman_pvals = np.array(spearman_pvals)
    shape_r2 = np.array(shape_r2)

    overall_rate = float(favored.mean())
    var_rate = float(favored[has_var].mean()) if has_var.any() else float("nan")
    bh_var = benjamini_hochberg(pvals[has_var], q=q) if has_var.any() else np.array([], dtype=bool)
    var_bh = float((favored[has_var] & ~bh_var).mean()) if has_var.any() else float("nan")

    # ── Negative control I: budget-permutation null (preserves multiset of counts).
    # Weak control: tests whether the *order* of successes-vs-budgets matters,
    # but a curve like {0,0,7,7,7,7} stays staircase-fittable after shuffling.
    rates_overall, rates_var, rates_var_bh = [], [], []
    for seed in range(n_neg_seeds):
        rng = np.random.default_rng(20260504 + seed)
        f_, h_, pv_ = [], [], []
        for p_idx in range(n_problems):
            for t_idx in range(n_temps):
                k = successes[p_idx, :, t_idx].copy()
                rng.shuffle(k)
                r = select_per_cell(k, S, budgets)
                f_.append(r["favored"] == "staircase")
                h_.append(r["has_variation"])
                pv_.append(r["p_lrt_sig_vs_step"])
        f_ = np.array(f_); h_ = np.array(h_); pv_ = np.array(pv_)
        rates_overall.append(float(f_.mean()))
        if h_.any():
            rates_var.append(float(f_[h_].mean()))
            bh = benjamini_hochberg(pv_[h_], q=q)
            rates_var_bh.append(float((f_[h_] & ~bh).mean()))

    # ── Negative control II: IID-Bernoulli null at the trajectory mean.
    # Strong control: destroys any budget->accuracy relationship completely.
    # If staircase still wins at the same rate here, BIC's penalty alone is
    # driving classification. If staircase wins at a much lower rate, we have
    # evidence of genuine per-problem discrete structure.
    rates_iid_overall, rates_iid_var = [], []
    iid_shape_r2_var = []  # also compute shape R^2 on the null to compare
    iid_frac_high_r2_var = []
    for seed in range(n_neg_seeds):
        rng = np.random.default_rng(20260504 + 1000 + seed)
        f_, h_, r2_ = [], [], []
        for p_idx in range(n_problems):
            for t_idx in range(n_temps):
                k_orig = successes[p_idx, :, t_idx]
                p_bar = float(k_orig.sum() / max(len(k_orig) * S, 1))
                p_bar = float(np.clip(p_bar, 1e-3, 1.0 - 1e-3))
                k_iid = rng.binomial(S, p_bar, size=len(k_orig))
                r = select_per_cell(k_iid, S, budgets)
                f_.append(r["favored"] == "staircase")
                h_.append(r["has_variation"])
                r2, _ = staircase_shape_coefficient(k_iid, S)
                r2_.append(r2)
        f_ = np.array(f_); h_ = np.array(h_); r2_ = np.array(r2_)
        rates_iid_overall.append(float(f_.mean()))
        if h_.any():
            rates_iid_var.append(float(f_[h_].mean()))
            iid_shape_r2_var.append(float(np.mean(r2_[h_])))
            iid_frac_high_r2_var.append(float((r2_[h_] > 0.7).mean()))

    # ── Log-concavity test on tau (variation subset)
    tau_lc = tau_bs[has_var]
    lc = log_concavity_baringhaus_henze(tau_lc.tolist())

    # ── TOST equivalence: per-problem accuracy at the chosen oracle-best budget
    # vs. fixed-budget-largest
    accuracy = successes / max(S, 1)
    last_budget_acc = accuracy[:, -1, :]  # (problems, temps)
    success_mask = accuracy >= 0.5
    chosen_budget = np.zeros(n_problems)
    chosen_acc = np.zeros(n_problems)
    for pi in range(n_problems):
        # Pick first budget at any temp where the model first succeeds (>=50%)
        # If multiple temps work, pick lowest budget index
        any_success = success_mask[pi].any(axis=1)  # (n_budgets,)
        if any_success.any():
            bi = int(np.argmax(any_success))
            chosen_budget[pi] = budgets[bi]
            chosen_acc[pi] = accuracy[pi, bi].max()  # max across temps
        else:
            chosen_budget[pi] = budgets[-1]
            chosen_acc[pi] = accuracy[pi, -1].max()
    diffs_pp = (chosen_acc - last_budget_acc.max(axis=1)) * 100.0
    tost = tost_equivalence(diffs_pp, eps_low=-2.0, eps_high=2.0)

    # ── Per-budget mean accuracy (the staircase shape)
    per_budget_acc = accuracy.mean(axis=(0, 2)).tolist()

    return {
        "model_npy": str(npy_path),
        "n_problems": int(n_problems),
        "n_budgets": int(n_budgets),
        "n_temps": int(n_temps),
        "samples_per_cell": int(S),
        "budgets": budgets.tolist(),
        "n_cells": int(len(favored)),
        "n_with_variation": int(has_var.sum()),
        "frac_with_variation": float(has_var.mean()),
        "headline": {
            "staircase_rate_overall": overall_rate,
            "staircase_rate_variation": var_rate,
            "staircase_rate_variation_bh_corrected": var_bh,
            "bh_q": q,
        },
        "primary_tests": {
            "spearman_trend_test": {
                "frac_significant_overall": float((spearman_pvals < 0.05).mean()),
                "frac_significant_variation": (
                    float((spearman_pvals[has_var] < 0.05).mean()) if has_var.any() else float("nan")
                ),
                "frac_bh_significant_variation": (
                    float(benjamini_hochberg(spearman_pvals[has_var], q=q).mean()) if has_var.any() else float("nan")
                ),
                "interpretation": "Fraction of cells where accuracy increases monotonically with budget at α=0.05; this is a non-parametric test free of BIC's DOF-penalty bias.",
            },
            "staircase_shape_coefficient": {
                "mean_r2_overall": float(np.mean(shape_r2)),
                "mean_r2_variation": float(np.mean(shape_r2[has_var])) if has_var.any() else float("nan"),
                "median_r2_variation": float(np.median(shape_r2[has_var])) if has_var.any() else float("nan"),
                "frac_high_r2_variation": (
                    float((shape_r2[has_var] > 0.7).mean()) if has_var.any() else float("nan")
                ),
                "interpretation": "Mean R² for the best single-split staircase model. R²>0.7 means most variance is captured by ONE discrete jump, supporting the staircase claim. R² is dimensionless and not subject to BIC's penalty.",
            },
        },
        "negative_control": {
            "n_seeds": int(n_neg_seeds),
            "permutation_shuffle": {
                "overall_mean": float(np.mean(rates_overall)) if rates_overall else float("nan"),
                "variation_mean": float(np.mean(rates_var)) if rates_var else float("nan"),
                "variation_bh_mean": float(np.mean(rates_var_bh)) if rates_var_bh else float("nan"),
                "ci_95_variation": (
                    [float(np.percentile(rates_var, 2.5)), float(np.percentile(rates_var, 97.5))]
                    if len(rates_var) >= 2 else [float("nan"), float("nan")]
                ),
                "note": "Budget permutation preserves multiset of success counts (weak control).",
            },
            "iid_bernoulli_null": {
                "overall_mean": float(np.mean(rates_iid_overall)) if rates_iid_overall else float("nan"),
                "variation_mean": float(np.mean(rates_iid_var)) if rates_iid_var else float("nan"),
                "ci_95_variation": (
                    [float(np.percentile(rates_iid_var, 2.5)), float(np.percentile(rates_iid_var, 97.5))]
                    if len(rates_iid_var) >= 2 else [float("nan"), float("nan")]
                ),
                "shape_r2_mean_variation": (
                    float(np.mean(iid_shape_r2_var)) if iid_shape_r2_var else float("nan")
                ),
                "shape_frac_high_r2_variation": (
                    float(np.mean(iid_frac_high_r2_var)) if iid_frac_high_r2_var else float("nan")
                ),
                "note": "IID-Bernoulli at trajectory mean fully destroys budget-accuracy relationship (strong control). Shape R^2 on null lets us see if real shape R^2 is meaningfully above chance.",
            },
            "delta_real_vs_iid_variation": (
                float(var_rate - np.mean(rates_iid_var))
                if (rates_iid_var and np.isfinite(var_rate)) else float("nan")
            ),
            "interpretation": (
                "PASS: real >> iid-bernoulli (signal carries real per-problem structure)"
                if (rates_iid_var and np.isfinite(var_rate) and (var_rate - np.mean(rates_iid_var) > 0.10))
                else "WEAK: real ≈ iid-bernoulli (BIC penalty drives classification, not signal)"
            ),
        },
        "snell_powerlaw_baseline": {
            "powerlaw_wins_overall": int(np.sum(delta_pow < 0)),
            "powerlaw_wins_variation": int(np.sum(delta_pow[has_var] < 0)),
        },
        "log_concavity_test": lc,
        "tost_vs_max_budget": {
            **tost,
            "median_chosen_budget": float(np.median(chosen_budget)),
            "mean_chosen_budget": float(np.mean(chosen_budget)),
            "tokens_saved_vs_max_pct": float(100.0 * (1.0 - np.mean(chosen_budget) / float(budgets[-1]))),
        },
        "per_budget_accuracy_curve": per_budget_acc,
        "latency_meta": meta.get("latency_ms", {}),
        "gzip_overhead_meta": meta.get("gzip_overhead_ms", {}),
        "produced_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }


def main():
    out = {"models": {}, "produced_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    if not RESULTS_DIR.exists():
        print(f"[v3] {RESULTS_DIR} does not exist yet")
        return
    npys = sorted(RESULTS_DIR.glob("results_*.npy"))
    if not npys:
        print(f"[v3] no results files yet in {RESULTS_DIR}")
        return
    for npy_path in npys:
        if "_meta" in npy_path.stem or "accuracy_" in npy_path.stem or "successes_" in npy_path.stem:
            continue
        if ".ckpt" in npy_path.name:  # checkpoint shadow files
            continue
        meta_path = npy_path.with_name(npy_path.stem + "_meta.json")
        key = npy_path.stem.replace("results_", "")
        try:
            analysis = analyze_v3(npy_path, meta_path)
            out["models"][key] = analysis
            head = analysis["headline"]
            nc = analysis["negative_control"]
            primary = analysis.get("primary_tests", {})
            shape = primary.get("staircase_shape_coefficient", {})
            print(f"[v3] {key}:")
            print(f"     real_var (BIC)        = {head['staircase_rate_variation']:.3f}")
            print(f"     real_var (BH-corr)    = {head['staircase_rate_variation_bh_corrected']:.3f}")
            print(f"     permutation null      = {nc['permutation_shuffle']['variation_mean']:.3f}")
            print(f"     IID-Bernoulli null    = {nc['iid_bernoulli_null']['variation_mean']:.3f}")
            print(f"     delta_real-vs-iid     = {nc['delta_real_vs_iid_variation']:.3f}")
            print(f"     SHAPE R^2 mean        = {shape.get('mean_r2_variation', float('nan')):.3f}  "
                  f"(null: {nc['iid_bernoulli_null'].get('shape_r2_mean_variation', float('nan')):.3f})")
            print(f"     SHAPE frac R^2>0.7    = {shape.get('frac_high_r2_variation', float('nan')):.3f}  "
                  f"(null: {nc['iid_bernoulli_null'].get('shape_frac_high_r2_variation', float('nan')):.3f})")
            print(f"     log-conc B-H p        = {analysis['log_concavity_test'].get('p_value', float('nan')):.3f}")
            print(f"     >>> {nc['interpretation']}")
        except Exception as e:
            print(f"[v3] ERR processing {npy_path}: {e}")
            out["models"][key] = {"error": str(e)}
    out_path = REPO / "revised_v3_stats.json"
    out_path.write_text(json.dumps(out, indent=2, default=float))
    print(f"[v3] wrote {out_path}")


if __name__ == "__main__":
    main()
