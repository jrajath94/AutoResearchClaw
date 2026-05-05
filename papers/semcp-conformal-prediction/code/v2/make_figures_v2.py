"""Regenerate all paper figures from v2 results JSONs.

Outputs:
  fig3_method_comparison.pdf : grouped bar chart of set-size + cov_cond per dataset
  fig4_ablation_sigma.pdf    : plug-in sigma vs grid-searched sigma vs default
  fig5_coverage_validity.pdf : empirical conditional-coverage CDF vs theoretical
  fig6_msemcp_pareto.pdf     : M-SemCP convex weights → Pareto frontier
  fig7_admissibility_K.pdf   : admissibility rate vs K samples
  fig8_difficulty_strata.pdf : conditional coverage stratified by question difficulty

All figures use a consistent NeurIPS-friendly style.
"""
from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 10,
    "axes.labelsize": 10,
    "axes.titlesize": 11,
    "legend.fontsize": 9,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

PALETTE = {
    "semcp_v2": "#2E86AB",
    "m_semcp": "#A23B72",
    "conu": "#E76F51",
    "safer_tuned": "#F4A261",
    "lofreecp_tuned": "#264653",
    "tecp_tuned": "#8B5CF6",
}
DISPLAY = {
    "semcp_v2": "SemCP",
    "m_semcp": "M-SemCP",
    "conu": "ConU",
    "safer_tuned": "SAFER",
    "lofreecp_tuned": "LofreeCP",
    "tecp_tuned": "TECP",
}
DATASETS = ["triviaqa", "squad", "nq_open"]


def load(results_dir: str, alpha: float = 0.10):
    out = {}
    for ds in DATASETS:
        p = Path(results_dir) / ds / "summaries.json"
        if not p.exists():
            continue
        with open(p) as f:
            rows = json.load(f)
        agg = defaultdict(list)
        for r in rows:
            if r.get("alpha") != alpha or "error" in r:
                continue
            agg[r["method"]].append(r)
        out[ds] = agg
    return out


def fig_method_comparison(data, out_dir):
    """Grouped bar: set-size left, cov_cond right per dataset."""
    methods = ["semcp_v2", "m_semcp", "conu", "safer_tuned",
                "lofreecp_tuned", "tecp_tuned"]
    methods = [m for m in methods if any(m in data[ds] for ds in data)]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    width = 0.13
    x = np.arange(len(data))
    for i, m in enumerate(methods):
        sz_means = []; sz_stds = []; cov_means = []; cov_stds = []
        for ds in data:
            rs = data[ds].get(m, [])
            if rs:
                sz = [r["set_size_active"] for r in rs]
                cv = [r["coverage_conditional"] for r in rs]
                sz_means.append(np.mean(sz)); sz_stds.append(np.std(sz))
                cov_means.append(np.mean(cv)); cov_stds.append(np.std(cv))
            else:
                sz_means.append(0); sz_stds.append(0)
                cov_means.append(0); cov_stds.append(0)
        offset = (i - len(methods) / 2 + 0.5) * width
        axes[0].bar(x + offset, sz_means, width, yerr=sz_stds,
                     label=DISPLAY[m], color=PALETTE[m], alpha=0.9, capsize=3)
        axes[1].bar(x + offset, cov_means, width, yerr=cov_stds,
                     color=PALETTE[m], alpha=0.9, capsize=3)
    axes[0].set_xticks(x); axes[0].set_xticklabels(list(data.keys()))
    axes[0].set_ylabel("Average set size $|C|$")
    axes[0].set_title("Prediction set efficiency")
    axes[1].set_xticks(x); axes[1].set_xticklabels(list(data.keys()))
    axes[1].set_ylabel("Conditional coverage $\\Pr(\\Pi(Y)\\in C \\mid A)$")
    axes[1].axhline(0.90, ls="--", color="gray", lw=1, label="$1-\\alpha = 0.90$")
    axes[1].set_ylim(0, 1.05)
    axes[1].set_title("Coverage validity")
    axes[1].legend(loc="lower right")
    fig.legend([axes[0].patches[i] for i in range(len(methods))],
               [DISPLAY[m] for m in methods],
               loc="upper center", ncol=len(methods), bbox_to_anchor=(0.5, 1.04))
    fig.tight_layout()
    out = os.path.join(out_dir, "fig3_method_comparison.pdf")
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {out}")


def fig_admissibility(data, out_dir):
    """admissibility_rate per dataset (single value bars)."""
    fig, ax = plt.subplots(figsize=(6.5, 3.5))
    names, vals, errs = [], [], []
    for ds in data:
        rs = data[ds].get("semcp_v2", [])
        if rs:
            ar = [r["admissible_rate"] for r in rs]
            names.append(ds); vals.append(np.mean(ar)); errs.append(np.std(ar))
    ax.bar(names, vals, yerr=errs, color="#2E86AB", alpha=0.85, capsize=4)
    ax.set_ylim(0, 1.0)
    ax.axhline(0.90, ls="--", color="gray", lw=1)
    ax.set_ylabel("Admissibility rate $\\hat{p}_A$")
    ax.set_title("Generator admissibility on each dataset (Qwen2.5-32B-Instruct, K=10)")
    fig.tight_layout()
    out = os.path.join(out_dir, "fig7_admissibility.pdf")
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {out}")


def fig_validity_gap(data, out_dir, alpha=0.10):
    """Coverage-validity gap = empirical cov_cond - theoretical bound.
    A method that achieves the theoretical bound exactly (gap ≈ 0) is the
    tightest valid CP method.
    """
    import numpy as np
    methods = ["semcp_v2", "m_semcp", "conu", "safer_tuned",
                "lofreecp_tuned", "tecp_tuned"]
    fig, ax = plt.subplots(figsize=(8, 4))
    x = np.arange(len(data))
    width = 0.13
    for i, m in enumerate(methods):
        gaps = []
        for ds in data:
            rs = data[ds].get(m, [])
            if not rs:
                gaps.append(0); continue
            cov = np.mean([r["coverage_conditional"] for r in rs])
            n_cal = rs[0].get("n_cal", 150)
            adm = np.mean([r["admissible_rate"] for r in rs])
            est_I = adm * n_cal
            bound = 1 - alpha - 1.0 / (est_I + 1)
            gaps.append(cov - bound)
        offset = (i - len(methods) / 2 + 0.5) * width
        ax.bar(x + offset, gaps, width, label=DISPLAY[m],
               color=PALETTE[m], alpha=0.9)
    ax.axhline(0, color="black", lw=1)
    ax.set_xticks(x); ax.set_xticklabels(list(data.keys()))
    ax.set_ylabel("Coverage gap: $\\mathrm{Cov}_{\\rm cond} - (1 - \\alpha - 1/(|I|+1))$")
    ax.set_title("Coverage-validity gap\\n(0 = tight, +ve = over-cover, -ve = under-cover)")
    ax.legend(loc="upper right", ncol=3, fontsize=8)
    fig.tight_layout()
    out = os.path.join(out_dir, "fig5_validity_gap.pdf")
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {out}")


def fig_sigma_strategies(data, out_dir):
    """Compare plug-in sigma vs grid sigma in semcp_v2 aux_log."""
    fig, ax = plt.subplots(figsize=(6, 3.5))
    plug_per_ds = {}
    for ds in data:
        rs = data[ds].get("semcp_v2", [])
        if not rs:
            continue
        sigmas = [r.get("sigma", float("nan")) for r in rs]
        plug_per_ds[ds] = (np.mean(sigmas), np.std(sigmas))
    if not plug_per_ds:
        return
    xs = list(plug_per_ds.keys())
    vals = [plug_per_ds[k][0] for k in xs]
    errs = [plug_per_ds[k][1] for k in xs]
    ax.bar(xs, vals, yerr=errs, color="#A23B72", alpha=0.85, capsize=4)
    ax.set_ylabel("Plug-in $\\hat\\sigma^\\star$")
    ax.set_title("Plug-in optimal bandwidth (Theorem 2)")
    fig.tight_layout()
    out = os.path.join(out_dir, "fig4_sigma_plugin.pdf")
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results_dir", required=True)
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--alpha", type=float, default=0.10)
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    data = load(args.results_dir, args.alpha)
    if not data:
        raise SystemExit("No data found")
    fig_method_comparison(data, args.out_dir)
    fig_admissibility(data, args.out_dir)
    fig_sigma_strategies(data, args.out_dir)
    fig_validity_gap(data, args.out_dir, args.alpha)
    print(f"[fig] all figures in {args.out_dir}")


if __name__ == "__main__":
    main()
