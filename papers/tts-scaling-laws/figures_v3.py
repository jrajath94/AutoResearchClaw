"""Publication-quality V3 figures for the STAIRCASE paper.

Generates four NeurIPS-grade figures from real_results_v3/ data:

  fig_v3_per_budget.pdf
    3-panel figure showing population per-budget accuracy for:
      (a) Qwen3.6-35B-A3B on GSM8K
      (b) Llama 4 Scout on GSM8K
      (c) Qwen3.6-35B-A3B on MATH-500
    Bars show mean accuracy with 95% bootstrap CI. The smooth concave
    population shape that Theorem 1 predicts is visually striking.

  fig_v3_shape_r2_hist.pdf
    3-panel histogram of per-cell shape R^2: real vs IID-Bernoulli null
    overlaid for each experiment. The 0.7 threshold marked. Shows the
    massive separation between signal-bearing and noise distributions.

  fig_v3_example_cells.pdf
    6 example per-cell curves from Qwen3.6-35B-A3B GSM8K showing:
      3 high-R^2 staircase cells (> 0.85)
      3 low-R^2 noisy cells (< 0.30)
    Each subpanel labels the R^2 and best-split position.

  fig_v3_bic_diagnosis.pdf
    Bar chart contrasting BIC staircase rate vs Shape-R^2 rate, real vs
    IID-null, for all 3 experiments. Visualizes the methodological
    discovery: BIC fails identically on signal and noise; Shape R^2
    discriminates cleanly.

All figures use a colorblind-safe palette and remain legible in B&W.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# NeurIPS publication style
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "text.usetex": False,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.8,
})

# Colorblind-safe palette (Tol's vibrant)
C = {
    "blue":   "#0077BB",  # Qwen
    "orange": "#EE7733",  # Llama
    "teal":   "#009988",  # MATH-500
    "red":    "#CC3311",  # null
    "gray":   "#BBBBBB",  # baseline
    "green":  "#33BB55",  # accept
}

REPO = Path(__file__).resolve().parent
RESULTS = REPO / "real_results_v3"
FIG_OUT = REPO / "latex" / "figures_v3"
FIG_OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(REPO))
from analysis_v3 import staircase_shape_coefficient  # type: ignore


# ─────────────────────────────────────────────────────────────────────────────
# Data loading
# ─────────────────────────────────────────────────────────────────────────────


def load_experiment(name: str) -> dict:
    """Load (correct, accuracy, meta) for a given experiment name like
    'qwen3.6_35b-a3b_gsm8k' or 'llama4_scout_gsm8k'."""
    correct = np.load(RESULTS / f"results_{name}.npy")
    meta_path = RESULTS / f"results_{name}_meta.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    return {"correct": correct, "meta": meta, "name": name}


def per_budget_with_ci(correct: np.ndarray, n_boot: int = 1000):
    """Return per-budget mean accuracy plus 95% bootstrap CI across problems.
    Uses cluster-bootstrap over problems to respect per-problem clustering.
    correct shape: (problems, budgets, temps, samples)
    """
    p, b, t, s = correct.shape
    per_problem = correct.mean(axis=(2, 3))  # (problems, budgets)
    means = per_problem.mean(axis=0)
    rng = np.random.default_rng(42)
    boots = np.empty((n_boot, b))
    for i in range(n_boot):
        idx = rng.integers(0, p, size=p)
        boots[i] = per_problem[idx].mean(axis=0)
    lo = np.percentile(boots, 2.5, axis=0)
    hi = np.percentile(boots, 97.5, axis=0)
    return means, lo, hi


def shape_r2_distribution(correct: np.ndarray, S_per_cell: int, n_null_seeds: int = 5):
    """Compute shape R^2 for every (problem, temp) trajectory.
    For the IID-Bernoulli null, draws n_null_seeds realizations per cell.

    Returns:
        r2_real (array of length n_var): per-cell R^2 on real trajectories
        r2_null_pool (array of length n_var * n_null_seeds): pooled null R^2 (for histogram)
        null_frac_seed_means (float): mean across seeds of the per-seed >0.7 fraction.
                                       This MATCHES analysis_v3.py's headline reporting.
    """
    p, nb, nt, ns = correct.shape
    successes = correct.sum(axis=-1)
    r2_real, r2_null_pool = [], []
    per_seed_null_fracs = []
    for seed in range(n_null_seeds):
        rng = np.random.default_rng(20260504 + 1000 + seed)
        seed_r2_null = []
        for pi in range(p):
            for ti in range(nt):
                k_real = successes[pi, :, ti]
                if k_real.max() == k_real.min():
                    continue
                if seed == 0:
                    r2, _ = staircase_shape_coefficient(k_real, S_per_cell)
                    r2_real.append(r2)
                p_bar = float(k_real.sum() / max(nb * S_per_cell, 1))
                p_bar = float(np.clip(p_bar, 1e-3, 1.0 - 1e-3))
                k_null = rng.binomial(S_per_cell, p_bar, size=nb)
                r2n, _ = staircase_shape_coefficient(k_null, S_per_cell)
                seed_r2_null.append(r2n)
                r2_null_pool.append(r2n)
        seed_r2_null = np.asarray(seed_r2_null)
        per_seed_null_fracs.append(float((seed_r2_null > 0.7).mean()))
    return (np.asarray(r2_real), np.asarray(r2_null_pool),
            float(np.mean(per_seed_null_fracs)))


# ─────────────────────────────────────────────────────────────────────────────
# Figure 1: Per-budget population accuracy curves
# ─────────────────────────────────────────────────────────────────────────────


def fig_per_budget(experiments):
    fig, axes = plt.subplots(1, 3, figsize=(9.5, 2.6), sharey=False)
    titles = ["(a) Qwen3.6-35B-A3B / GSM8K",
              "(b) Llama 4 Scout / GSM8K",
              "(c) Qwen3.6-35B-A3B / MATH-500"]
    colors = [C["blue"], C["orange"], C["teal"]]
    for ax, exp, t, c in zip(axes, experiments, titles, colors):
        budgets = exp["meta"].get("budgets", [32, 64, 128, 256, 512, 1024])
        means, lo, hi = per_budget_with_ci(exp["correct"])
        ax.fill_between(budgets, lo, hi, color=c, alpha=0.18, linewidth=0)
        ax.plot(budgets, means, color=c, marker="o", lw=1.5, markersize=4.5)
        ax.set_xscale("log")
        ax.set_xticks(budgets)
        ax.set_xticklabels([str(b) for b in budgets], fontsize=7)
        ax.set_title(t, fontsize=9)
        ax.set_xlabel("token budget $t$", fontsize=8)
        ax.set_ylabel("population accuracy $\\bar{a}(t)$", fontsize=8)
        ax.set_ylim(-0.02, max(1.0, hi.max() + 0.05))
        ax.grid(True, axis="y", linestyle=":", alpha=0.4)
        # Annotate the empirical elbow (max curvature change)
        d2 = np.diff(np.diff(means))
        if len(d2) > 0:
            elbow_i = int(np.argmin(d2)) + 1  # +1 because diff shrinks
            elbow_b = budgets[elbow_i] if elbow_i < len(budgets) else budgets[-1]
            ax.axvline(elbow_b, color="black", linestyle="--", lw=0.6, alpha=0.5)
            ax.annotate(f"elbow $\\approx${elbow_b}",
                        xy=(elbow_b, means[elbow_i] if elbow_i < len(means) else means[-1]),
                        xytext=(8, -12), textcoords="offset points",
                        fontsize=7, ha="left", color="black", alpha=0.7)
    fig.suptitle("Population-level scaling curves (V3) — smooth, monotone, concave (Thm.~1 prediction)",
                 fontsize=10, y=1.04)
    plt.tight_layout()
    out = FIG_OUT / "fig_v3_per_budget.pdf"
    plt.savefig(out)
    plt.savefig(out.with_suffix(".png"))
    plt.close(fig)
    print(f"  -> {out}")


# ─────────────────────────────────────────────────────────────────────────────
# Figure 2: Shape R^2 histograms
# ─────────────────────────────────────────────────────────────────────────────


def fig_r2_histograms(experiments):
    fig, axes = plt.subplots(1, 3, figsize=(9.5, 2.7), sharey=True)
    titles = ["(a) Qwen3.6-35B-A3B / GSM8K",
              "(b) Llama 4 Scout / GSM8K",
              "(c) Qwen3.6-35B-A3B / MATH-500"]
    bins = np.linspace(0, 1, 21)
    for ax, exp, t in zip(axes, experiments, titles):
        S_per_cell = exp["meta"].get("samples_per_cell", 8)
        r2_real, r2_null, frac_null_mean = shape_r2_distribution(exp["correct"], S_per_cell)
        ax.hist(r2_null, bins=bins, alpha=0.55, label="IID-Bernoulli null",
                color=C["red"], edgecolor="white", linewidth=0.5, density=True)
        ax.hist(r2_real, bins=bins, alpha=0.65, label="real",
                color=C["blue"], edgecolor="white", linewidth=0.5, density=True)
        ax.axvline(0.7, color="black", linestyle="--", lw=1.0, alpha=0.7,
                   label="$R^2{=}0.7$ threshold")
        # Annotate the >0.7 fractions (mean over n_null_seeds for null,
        # to match analysis_v3.py headline reporting)
        frac_real = float((r2_real > 0.7).mean())
        frac_null = frac_null_mean
        ax.text(0.04, 0.95, f"real $>$0.7: {frac_real:.1%}",
                transform=ax.transAxes, fontsize=7.5, va="top",
                color=C["blue"], fontweight="bold")
        ax.text(0.04, 0.86, f"null $>$0.7: {frac_null:.1%}",
                transform=ax.transAxes, fontsize=7.5, va="top",
                color=C["red"], fontweight="bold")
        ax.text(0.04, 0.77, f"separation: {frac_real / max(frac_null, 0.001):.1f}$\\times$",
                transform=ax.transAxes, fontsize=7.5, va="top",
                color="black", fontweight="bold")
        ax.set_title(t, fontsize=9)
        ax.set_xlabel("staircase shape $R^2$ (per cell)", fontsize=8)
        if ax is axes[0]:
            ax.set_ylabel("density (variation subset)", fontsize=8)
            ax.legend(loc="upper right", fontsize=7, frameon=False)
        ax.set_xlim(0, 1)
        ax.grid(True, axis="y", linestyle=":", alpha=0.4)
    fig.suptitle("Per-cell staircase shape $R^2$ — real vs IID-Bernoulli null (variation subset)",
                 fontsize=10, y=1.04)
    plt.tight_layout()
    out = FIG_OUT / "fig_v3_shape_r2_hist.pdf"
    plt.savefig(out)
    plt.savefig(out.with_suffix(".png"))
    plt.close(fig)
    print(f"  -> {out}")


# ─────────────────────────────────────────────────────────────────────────────
# Figure 3: Example per-cell trajectories (6 cells)
# ─────────────────────────────────────────────────────────────────────────────


def fig_example_cells(exp):
    correct = exp["correct"]
    p, nb, nt, ns = correct.shape
    budgets = exp["meta"].get("budgets", [32, 64, 128, 256, 512, 1024])
    successes = correct.sum(axis=-1)  # (p, nb, nt)
    r2_arr = np.zeros((p, nt))
    for pi in range(p):
        for ti in range(nt):
            k = successes[pi, :, ti]
            if k.max() == k.min():
                r2_arr[pi, ti] = 0.0
            else:
                r2, _ = staircase_shape_coefficient(k, ns)
                r2_arr[pi, ti] = r2
    # Pick 3 high-R^2 (real staircases) and 3 low-R^2 (variation but low-R^2)
    flat = [(pi, ti, r2_arr[pi, ti]) for pi in range(p) for ti in range(nt)
            if successes[pi, :, ti].max() != successes[pi, :, ti].min()]
    high = sorted(flat, key=lambda x: -x[2])[:3]
    low = sorted([f for f in flat if f[2] < 0.30], key=lambda x: x[2])[:3]
    if len(low) < 3:
        low = sorted(flat, key=lambda x: x[2])[:3]
    examples = high + low

    fig, axes = plt.subplots(2, 3, figsize=(9.5, 4.6))
    for idx, ((pi, ti, r2), ax) in enumerate(zip(examples, axes.flat)):
        k = successes[pi, :, ti]
        acc = k / max(ns, 1)
        is_high = idx < 3
        col = C["blue"] if is_high else C["gray"]
        ax.plot(budgets, acc, color=col, marker="o", lw=1.5, markersize=5)
        # Best split annotation
        _, best_split = staircase_shape_coefficient(k, ns)
        if best_split > 0:
            ax.axvline(budgets[best_split - 1] * 1.4, color="black",
                       linestyle="--", lw=0.8, alpha=0.55)
        ax.set_xscale("log")
        ax.set_xticks(budgets)
        ax.set_xticklabels([str(b) for b in budgets], fontsize=7)
        ax.set_ylim(-0.05, 1.05)
        kind = "high-$R^2$ (staircase)" if is_high else "low-$R^2$ (noisy)"
        ax.set_title(f"problem {pi}, $\\tau$-idx={ti}\n{kind}, $R^2{{=}}${r2:.2f}",
                     fontsize=8)
        ax.set_xlabel("token budget", fontsize=8)
        if idx % 3 == 0:
            ax.set_ylabel("accuracy $\\hat{a}_i(t)$", fontsize=8)
        ax.grid(True, axis="y", linestyle=":", alpha=0.4)
    fig.suptitle(f"Example per-cell trajectories — {exp['name']} ($S{{=}}${ns})",
                 fontsize=10, y=1.00)
    plt.tight_layout()
    out = FIG_OUT / f"fig_v3_examples_{exp['name']}.pdf"
    plt.savefig(out)
    plt.savefig(out.with_suffix(".png"))
    plt.close(fig)
    print(f"  -> {out}")


# ─────────────────────────────────────────────────────────────────────────────
# Figure 4: BIC vs Shape R^2 -- the methodological discovery
# ─────────────────────────────────────────────────────────────────────────────


def fig_bic_vs_shape(experiments, stats_path: Path):
    stats = json.loads(stats_path.read_text())
    rows = []
    for exp in experiments:
        m = stats["models"].get(exp["name"], {})
        if not m:
            continue
        head = m.get("headline", {})
        prim = m.get("primary_tests", {}).get("staircase_shape_coefficient", {})
        nc = m.get("negative_control", {}).get("iid_bernoulli_null", {})
        rows.append({
            "name": exp["name"],
            "bic_real": head.get("staircase_rate_variation", float("nan")),
            "bic_null": m["negative_control"]["iid_bernoulli_null"].get("variation_mean", float("nan")),
            "r2_real": prim.get("frac_high_r2_variation", float("nan")),
            "r2_null": nc.get("shape_frac_high_r2_variation", float("nan")),
        })

    fig, ax = plt.subplots(figsize=(7.5, 3.8))
    n = len(rows)
    x = np.arange(n)
    bw = 0.18
    ax.bar(x - 1.5 * bw, [r["bic_real"] for r in rows], bw,
           label="BIC, real", color=C["blue"], alpha=0.95)
    ax.bar(x - 0.5 * bw, [r["bic_null"] for r in rows], bw,
           label="BIC, IID-null", color=C["blue"], alpha=0.45,
           hatch="//", edgecolor="white")
    ax.bar(x + 0.5 * bw, [r["r2_real"] for r in rows], bw,
           label="Shape $R^2{>}0.7$, real", color=C["green"], alpha=0.95)
    ax.bar(x + 1.5 * bw, [r["r2_null"] for r in rows], bw,
           label="Shape $R^2{>}0.7$, IID-null", color=C["green"], alpha=0.45,
           hatch="//", edgecolor="white")
    ax.set_xticks(x)
    pretty = {
        "qwen3.6_35b-a3b_gsm8k": "Qwen3.6-35B-A3B\nGSM8K",
        "llama4_scout_gsm8k": "Llama 4 Scout\nGSM8K",
        "qwen3.6_35b-a3b_math500": "Qwen3.6-35B-A3B\nMATH-500",
    }
    ax.set_xticklabels([pretty.get(r["name"], r["name"]) for r in rows], fontsize=8)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("variation-subset rate", fontsize=9)
    ax.set_title("BIC fails identically on real and noise; Shape $R^2$ discriminates",
                 fontsize=10)
    ax.grid(True, axis="y", linestyle=":", alpha=0.4)
    ax.legend(loc="upper right", fontsize=7.5, frameon=False, ncol=2)
    plt.tight_layout()
    out = FIG_OUT / "fig_v3_bic_vs_shape.pdf"
    plt.savefig(out)
    plt.savefig(out.with_suffix(".png"))
    plt.close(fig)
    print(f"  -> {out}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────


def main():
    print("[figures_v3] generating publication-quality V3 figures ...")
    experiments = [
        load_experiment("qwen3.6_35b-a3b_gsm8k"),
        load_experiment("llama4_scout_gsm8k"),
        load_experiment("qwen3.6_35b-a3b_math500"),
    ]
    fig_per_budget(experiments)
    fig_r2_histograms(experiments)
    fig_example_cells(experiments[0])  # Qwen3.6 GSM8K is the hero
    fig_bic_vs_shape(experiments, REPO / "revised_v3_stats.json")
    print("[figures_v3] DONE")


if __name__ == "__main__":
    main()
