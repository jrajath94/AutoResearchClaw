"""Generate fig:cdf — the missing stress-test CDF figure referenced on line 255 of paper_v2.tex.

Produces 2-panel figure:
- (a) CDF of conditional coverage across 100 folds for each method, with 1-α-1/(|I|+1) threshold
- (b) Coverage stratified by question difficulty (admissibility-tercile proxy: n_cal_admissible)
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parents[2]
STRESS = REPO / "artifacts/v2_results/triviaqa/stress.json"
OUT_DIR = REPO / "artifacts/deliverables/charts"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT = OUT_DIR / "fig_stress_cdf.pdf"

# Reviewer-friendly palette (color-blind safe, tab10-based)
METHOD_STYLE = {
    "semcp_v2": {"label": "SemCP-v2", "color": "#1f77b4", "lw": 2.5, "ls": "-", "z": 5},
    "m_semcp": {"label": "M-SemCP", "color": "#ff7f0e", "lw": 2.0, "ls": "-", "z": 4},
    "conu": {"label": "ConU", "color": "#2ca02c", "lw": 1.5, "ls": "--", "z": 3},
    "safer_tuned": {"label": "SAFER (tuned)", "color": "#d62728", "lw": 1.5, "ls": "--", "z": 3},
    "lofreecp_tuned": {"label": "LoFreeCP (tuned)", "color": "#9467bd", "lw": 1.5, "ls": "--", "z": 3},
    "tecp_tuned": {"label": "TECP (tuned)", "color": "#8c564b", "lw": 1.5, "ls": "--", "z": 3},
}

ALPHA = 0.10


def main() -> None:
    plt.rcParams.update({
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "font.size": 10,
        "axes.labelsize": 11,
        "axes.titlesize": 11,
    })

    data = json.loads(STRESS.read_text())

    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(11, 4.0))

    # --- Panel (a): CDF of conditional coverage ---
    for method, runs in data.items():
        if method not in METHOD_STYLE:
            continue
        cov = np.array([r["cov_cond"] for r in runs])
        cov_sorted = np.sort(cov)
        cdf = np.arange(1, len(cov_sorted) + 1) / len(cov_sorted)
        s = METHOD_STYLE[method]
        ax_a.plot(cov_sorted, cdf, label=s["label"], color=s["color"],
                  lw=s["lw"], ls=s["ls"], zorder=s["z"])

    # Reference lines: 1-alpha and the finite-sample threshold
    n_admis = np.median([r.get("n_cal_admissible", 105) for r in data["semcp_v2"]])
    threshold = 1.0 - ALPHA - 1.0 / (n_admis + 1)
    ax_a.axvline(1.0 - ALPHA, color="black", ls=":", lw=1.0, alpha=0.7,
                 label=fr"$1-\alpha={1-ALPHA:.2f}$")
    ax_a.axvline(threshold, color="gray", ls="-.", lw=1.0, alpha=0.7,
                 label=fr"$1-\alpha-\frac{{1}}{{|I|+1}}\approx {threshold:.3f}$")
    ax_a.set_xlabel("Conditional Coverage")
    ax_a.set_ylabel("Empirical CDF (100 folds)")
    ax_a.set_title("(a) CDF of conditional coverage")
    ax_a.set_xlim(0.7, 1.01)
    ax_a.set_ylim(0, 1.05)
    ax_a.grid(True, alpha=0.3)
    ax_a.legend(loc="upper left", fontsize=8, ncol=1, framealpha=0.95)

    # --- Panel (b): coverage stratified by difficulty (n_cal_admissible terciles) ---
    # We use n_cal_admissible as a proxy: lower admissibility → harder fold
    runs_per_method = {m: data[m] for m in METHOD_STYLE if m in data}
    # Use semcp_v2's n_cal_admissible as the stratification axis (same folds)
    semcp_runs = data.get("semcp_v2", [])
    n_admis_arr = np.array([r.get("n_cal_admissible", np.nan) for r in semcp_runs])
    if np.all(np.isfinite(n_admis_arr)) and n_admis_arr.std() > 0:
        terciles = np.percentile(n_admis_arr, [33.33, 66.67])
        strata = ["Hard\n(low p_A)", "Medium", "Easy\n(high p_A)"]
        x_pos = np.arange(len(strata))
        width = 0.13
        n_methods = len(runs_per_method)
        for i, (method, runs) in enumerate(runs_per_method.items()):
            cov = np.array([r["cov_cond"] for r in runs])
            ad = np.array([r.get("n_cal_admissible", np.nan) for r in runs])
            stratum_means = []
            stratum_stds = []
            for j, _ in enumerate(strata):
                if j == 0:
                    mask = ad <= terciles[0]
                elif j == 1:
                    mask = (ad > terciles[0]) & (ad <= terciles[1])
                else:
                    mask = ad > terciles[1]
                if mask.sum() > 0:
                    stratum_means.append(cov[mask].mean())
                    stratum_stds.append(cov[mask].std())
                else:
                    stratum_means.append(np.nan)
                    stratum_stds.append(0.0)
            offset = (i - (n_methods - 1) / 2) * width
            s = METHOD_STYLE[method]
            ax_b.bar(
                x_pos + offset,
                stratum_means,
                width=width,
                yerr=stratum_stds,
                color=s["color"],
                alpha=0.85,
                label=s["label"],
                capsize=2,
                edgecolor="black",
                linewidth=0.4,
            )
        ax_b.axhline(1 - ALPHA, color="black", ls=":", lw=1.0, alpha=0.7)
        ax_b.set_xticks(x_pos)
        ax_b.set_xticklabels(strata)
        ax_b.set_ylabel("Conditional Coverage")
        ax_b.set_title("(b) Coverage by difficulty (admissibility tercile)")
        ax_b.set_ylim(0.7, 1.05)
        ax_b.grid(True, axis="y", alpha=0.3)
        ax_b.legend(loc="lower right", fontsize=8, ncol=2)
    else:
        ax_b.text(0.5, 0.5, "n_cal_admissible not stratifiable",
                  ha="center", va="center", transform=ax_b.transAxes)

    fig.suptitle("Stress Test: 100-Fold Cal/Test Resampling on TriviaQA (K=10, α=0.10)",
                 y=1.02, fontsize=11, fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUT, bbox_inches="tight", dpi=300)
    print(f"[stress-cdf] wrote {OUT}")


if __name__ == "__main__":
    main()
