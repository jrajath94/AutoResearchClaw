"""Generate publication-quality figures for SemCP paper.

Reads experiment_output.log, parses AGGREGATE lines, produces 5 figures
at 300 DPI suitable for NeurIPS submission (3.25" or 6.75" wide).

Usage:
    python generate_figures.py [experiment_output.log]
"""
from __future__ import annotations

import re
import sys
import json
from pathlib import Path
from collections import defaultdict

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ── NeurIPS-compatible style ──────────────────────────────────────────
plt.rcParams.update({
    "font.size": 9,
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    "axes.labelsize": 10,
    "axes.titlesize": 11,
    "legend.fontsize": 8,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "axes.spines.top": False,
    "axes.spines.right": False,
})

OUTDIR = Path("artifacts/deliverables/charts")
OUTDIR.mkdir(parents=True, exist_ok=True)

# Method display names and colors
METHOD_LABELS = {
    "token_cp": "Token-CP",
    "naive_semantic_cp": "Naive Semantic",
    "semcp_proposed": "SemCP (Ours)",
    "semcp_variant": "SemCP-Adaptive",
    "semcp_no_m2o": "SemCP-NoM2O",
    "semcp_simplified": "SemCP-Euclidean",
}
METHOD_COLORS = {
    "token_cp": "#7f8c8d",
    "naive_semantic_cp": "#3498db",
    "semcp_proposed": "#e74c3c",
    "semcp_variant": "#e67e22",
    "semcp_no_m2o": "#9b59b6",
    "semcp_simplified": "#2ecc71",
}
DATASET_LABELS = {
    "trivia_qa": "TriviaQA",
    "squad": "SQuAD",
}


def parse_experiment_log(logpath: str) -> dict:
    """Parse AGGREGATE lines from experiment output log.

    Returns dict[dataset][method] = {metric: value, ...}
    """
    results = defaultdict(dict)
    agg_re = re.compile(
        r"AGGREGATE\s+"
        r"dataset=(\S+)\s+"
        r"condition=(\S+)\s+"
        r"(.+)"
    )
    with open(logpath) as f:
        for line in f:
            m = agg_re.search(line)
            if not m:
                continue
            dataset, condition, rest = m.group(1), m.group(2), m.group(3)
            metrics = {}
            for kv in re.finditer(r"(\w+)=([\d.eE+-]+(?:\([\d.eE+-]+\))?)", rest):
                key, val = kv.group(1), kv.group(2)
                # Handle "0.912(0.023)" format → mean, std
                paren = re.match(r"([\d.eE+-]+)\(([\d.eE+-]+)\)", val)
                if paren:
                    metrics[key] = float(paren.group(1))
                    metrics[key + "_std"] = float(paren.group(2))
                else:
                    metrics[key] = float(val)
            results[dataset][condition] = metrics
    return dict(results)


# ── Figure 1: Framework Diagram ───────────────────────────────────────

def fig1_framework_diagram():
    """Programmatic SemCP pipeline diagram."""
    fig, ax = plt.subplots(1, 1, figsize=(6.75, 2.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 2.5)
    ax.axis("off")

    boxes = [
        (0.3, 0.8, 1.4, 0.9, "Prompt\n$x$", "#ecf0f1"),
        (2.0, 0.8, 1.6, 0.9, "LLM\n(K samples)", "#dbeafe"),
        (4.0, 0.8, 1.8, 0.9, "NLI\nPartition $\\Pi$", "#fef3c7"),
        (6.2, 0.8, 1.8, 0.9, "RBF Kernel\nScoring", "#fce4ec"),
        (8.3, 0.8, 1.5, 0.9, "Conformal\nCalibration", "#d5f5e3"),
    ]

    for x, y, w, h, label, color in boxes:
        box = FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.1",
            facecolor=color, edgecolor="#2c3e50", linewidth=1.2
        )
        ax.add_patch(box)
        ax.text(x + w/2, y + h/2, label,
                ha="center", va="center", fontsize=8, fontweight="bold")

    # Arrows
    arrow_style = "Simple,tail_width=0.5,head_width=4,head_length=3"
    for i in range(len(boxes) - 1):
        x1 = boxes[i][0] + boxes[i][2]
        x2 = boxes[i+1][0]
        y_mid = boxes[i][1] + boxes[i][3] / 2
        ax.annotate("", xy=(x2, y_mid), xytext=(x1, y_mid),
                     arrowprops=dict(arrowstyle="->", color="#2c3e50", lw=1.5))

    # Output annotation
    ax.text(9.05, 0.5, "Semantic\nPrediction Set\n$\\hat{C}_{\\alpha}(x)$",
            ha="center", va="top", fontsize=8, fontstyle="italic", color="#e74c3c")

    # Title
    ax.text(5.0, 2.2, "SemCP: Conformal Prediction in Semantic Embedding Space",
            ha="center", va="center", fontsize=10, fontweight="bold")

    # Stage labels
    stages = ["Input", "Generation", "Equivalence\nClasses", "Nonconformity\nScores", "Coverage\nGuarantee"]
    for i, (x, y, w, h, _, _) in enumerate(boxes):
        ax.text(x + w/2, y - 0.15, stages[i],
                ha="center", va="top", fontsize=6.5, color="#7f8c8d")

    fig.savefig(OUTDIR / "fig1_framework.pdf")
    fig.savefig(OUTDIR / "fig1_framework.png")
    plt.close(fig)
    print(f"  Saved fig1_framework.pdf/.png")


# ── Figure 2: Coverage vs Set Size ────────────────────────────────────

def fig2_coverage_vs_setsize(results: dict):
    """Scatter plot: coverage (y) vs set size (x) per method, one subplot per dataset."""
    datasets = [d for d in ["trivia_qa", "squad"] if d in results]
    n = len(datasets)
    if n == 0:
        print("  [SKIP] fig2: no dataset results found")
        return

    fig, axes = plt.subplots(1, n, figsize=(3.25 * n, 2.8), squeeze=False)

    for idx, ds in enumerate(datasets):
        ax = axes[0, idx]
        ds_data = results[ds]

        for method, metrics in ds_data.items():
            cov = metrics.get("empirical_coverage", metrics.get("coverage"))
            ss = metrics.get("avg_set_size", metrics.get("set_size"))
            cov_std = metrics.get("empirical_coverage_std", metrics.get("coverage_std", 0))
            ss_std = metrics.get("avg_set_size_std", metrics.get("set_size_std", 0))

            if cov is None or ss is None:
                continue

            label = METHOD_LABELS.get(method, method)
            color = METHOD_COLORS.get(method, "#333")

            ax.errorbar(ss, cov, xerr=ss_std, yerr=cov_std,
                        fmt="o", color=color, label=label,
                        markersize=7, capsize=3, linewidth=1.2)

        # Target coverage line
        ax.axhline(y=0.9, color="#e74c3c", linestyle="--", alpha=0.6, linewidth=1)
        ax.text(ax.get_xlim()[1] * 0.95, 0.905, "$1-\\alpha$",
                ha="right", va="bottom", fontsize=7, color="#e74c3c")

        ax.set_xlabel("Avg. Prediction Set Size")
        ax.set_ylabel("Empirical Coverage")
        ax.set_title(DATASET_LABELS.get(ds, ds))

        if idx == n - 1:
            ax.legend(loc="lower right", fontsize=7, frameon=True, framealpha=0.9)

    fig.suptitle("Coverage vs. Efficiency Tradeoff", fontsize=11, fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig(OUTDIR / "fig2_coverage_vs_setsize.pdf")
    fig.savefig(OUTDIR / "fig2_coverage_vs_setsize.png")
    plt.close(fig)
    print(f"  Saved fig2_coverage_vs_setsize.pdf/.png")


# ── Figure 3: Method Comparison Bar Chart ─────────────────────────────

def fig3_method_comparison(results: dict):
    """Grouped bar chart: avg set size + coverage by method, colored by dataset."""
    datasets = [d for d in ["trivia_qa", "squad"] if d in results]
    if not datasets:
        print("  [SKIP] fig3: no results")
        return

    # Collect methods present in all datasets
    all_methods = []
    for ds in datasets:
        all_methods.extend(results[ds].keys())
    methods = list(dict.fromkeys(all_methods))  # preserve order, deduplicate

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.75, 2.8))

    x = np.arange(len(methods))
    width = 0.35
    ds_colors = ["#3498db", "#e67e22"]

    for i, ds in enumerate(datasets):
        sizes = []
        size_errs = []
        covs = []
        cov_errs = []
        for m in methods:
            if m in results[ds]:
                sizes.append(results[ds][m].get("avg_set_size", results[ds][m].get("set_size", 0)))
                size_errs.append(results[ds][m].get("avg_set_size_std", results[ds][m].get("set_size_std", 0)))
                covs.append(results[ds][m].get("empirical_coverage", results[ds][m].get("coverage", 0)))
                cov_errs.append(results[ds][m].get("empirical_coverage_std", results[ds][m].get("coverage_std", 0)))
            else:
                sizes.append(0); size_errs.append(0)
                covs.append(0); cov_errs.append(0)

        offset = (i - 0.5) * width
        ax1.bar(x + offset, sizes, width, yerr=size_errs,
                label=DATASET_LABELS.get(ds, ds), color=ds_colors[i],
                capsize=3, alpha=0.85, edgecolor="white")
        ax2.bar(x + offset, covs, width, yerr=cov_errs,
                label=DATASET_LABELS.get(ds, ds), color=ds_colors[i],
                capsize=3, alpha=0.85, edgecolor="white")

    labels = [METHOD_LABELS.get(m, m) for m in methods]
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, rotation=35, ha="right", fontsize=7)
    ax1.set_ylabel("Avg. Set Size")
    ax1.set_title("Prediction Set Size (lower is better)")
    ax1.legend(fontsize=7)

    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, rotation=35, ha="right", fontsize=7)
    ax2.set_ylabel("Empirical Coverage")
    ax2.set_title("Coverage (target $\\geq 0.90$)")
    ax2.axhline(y=0.9, color="#e74c3c", linestyle="--", alpha=0.6, linewidth=1)
    ax2.legend(fontsize=7)

    fig.suptitle("Method Comparison Across Datasets", fontsize=11, fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig(OUTDIR / "fig3_method_comparison.pdf")
    fig.savefig(OUTDIR / "fig3_method_comparison.png")
    plt.close(fig)
    print(f"  Saved fig3_method_comparison.pdf/.png")


# ── Figure 4: Ablation ────────────────────────────────────────────────

def fig4_ablation(results: dict):
    """Bar chart comparing SemCP variants (ablation study)."""
    ablation_methods = ["semcp_proposed", "semcp_variant", "semcp_no_m2o", "semcp_simplified"]
    datasets = [d for d in ["trivia_qa", "squad"] if d in results]
    if not datasets:
        print("  [SKIP] fig4: no results")
        return

    fig, ax = plt.subplots(1, 1, figsize=(4.5, 2.8))

    x = np.arange(len(ablation_methods))
    width = 0.35
    ds_colors = ["#3498db", "#e67e22"]

    for i, ds in enumerate(datasets):
        sizes = []
        errs = []
        for m in ablation_methods:
            if m in results[ds]:
                sizes.append(results[ds][m].get("avg_set_size", results[ds][m].get("set_size", 0)))
                errs.append(results[ds][m].get("avg_set_size_std", results[ds][m].get("set_size_std", 0)))
            else:
                sizes.append(0); errs.append(0)
        offset = (i - 0.5) * width
        ax.bar(x + offset, sizes, width, yerr=errs,
               label=DATASET_LABELS.get(ds, ds), color=ds_colors[i],
               capsize=3, alpha=0.85, edgecolor="white")

    labels = [METHOD_LABELS.get(m, m) for m in ablation_methods]
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=8)
    ax.set_ylabel("Avg. Set Size")
    ax.set_title("Ablation: Effect of Kernel Learning and M2O Calibration", fontsize=10)
    ax.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(OUTDIR / "fig4_ablation.pdf")
    fig.savefig(OUTDIR / "fig4_ablation.png")
    plt.close(fig)
    print(f"  Saved fig4_ablation.pdf/.png")


# ── Figure 5: Coverage by Semantic Complexity ─────────────────────────

def fig5_coverage_heatmap(results: dict):
    """Heatmap showing coverage × method × dataset."""
    datasets = [d for d in ["trivia_qa", "squad"] if d in results]
    if not datasets:
        print("  [SKIP] fig5: no results")
        return

    methods = list(METHOD_LABELS.keys())
    # Filter to methods that exist in results
    methods = [m for m in methods if any(m in results[ds] for ds in datasets)]

    data = np.zeros((len(methods), len(datasets)))
    for j, ds in enumerate(datasets):
        for i, m in enumerate(methods):
            if m in results[ds]:
                data[i, j] = results[ds][m].get("empirical_coverage", results[ds][m].get("coverage", 0))

    fig, ax = plt.subplots(1, 1, figsize=(3.5, 3.2))
    im = ax.imshow(data, cmap="RdYlGn", vmin=0.75, vmax=1.0, aspect="auto")

    ax.set_xticks(range(len(datasets)))
    ax.set_xticklabels([DATASET_LABELS.get(d, d) for d in datasets], fontsize=8)
    ax.set_yticks(range(len(methods)))
    ax.set_yticklabels([METHOD_LABELS.get(m, m) for m in methods], fontsize=8)

    # Annotate cells
    for i in range(len(methods)):
        for j in range(len(datasets)):
            val = data[i, j]
            color = "white" if val < 0.85 else "black"
            ax.text(j, i, f"{val:.3f}", ha="center", va="center", fontsize=8, color=color)

    # Target line annotation
    ax.set_title("Empirical Coverage by Method and Dataset", fontsize=10, fontweight="bold")
    cbar = fig.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("Coverage", fontsize=8)

    fig.tight_layout()
    fig.savefig(OUTDIR / "fig5_coverage_heatmap.pdf")
    fig.savefig(OUTDIR / "fig5_coverage_heatmap.png")
    plt.close(fig)
    print(f"  Saved fig5_coverage_heatmap.pdf/.png")


# ── Main ──────────────────────────────────────────────────────────────

def main():
    logpath = sys.argv[1] if len(sys.argv) > 1 else "experiment_output.log"
    print(f"Parsing {logpath}...")

    results = parse_experiment_log(logpath)

    if not results:
        print("WARNING: No AGGREGATE lines found in log. Generating framework diagram only.")
        fig1_framework_diagram()
        return

    print(f"Found results for {len(results)} dataset(s):")
    for ds, methods in results.items():
        print(f"  {ds}: {list(methods.keys())}")

    print("\nGenerating figures...")
    fig1_framework_diagram()
    fig2_coverage_vs_setsize(results)
    fig3_method_comparison(results)
    fig4_ablation(results)
    fig5_coverage_heatmap(results)

    # Also dump parsed results as JSON for paper update
    json_out = OUTDIR / "experiment_results.json"
    # Convert numpy types for JSON serialization
    clean = {}
    for ds, methods in results.items():
        clean[ds] = {}
        for m, metrics in methods.items():
            clean[ds][m] = {k: float(v) for k, v in metrics.items()}
    json_out.write_text(json.dumps(clean, indent=2))
    print(f"\nResults JSON saved to {json_out}")

    print("\nAll figures saved to", OUTDIR)


if __name__ == "__main__":
    main()
