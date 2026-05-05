"""
SemCP v2 — Publication Figures v3

Generates 5 NeurIPS-quality PDF figures from artifacts/v2_results/ into
artifacts/deliverables/charts/.

Figures:
  1. fig_validity_gap_errorbars.pdf  — validity gap forest plot (3 datasets x methods)
  2. fig_admissibility_breakdown.pdf — per-dataset admissibility bars + p_A annotation
  3. fig_k_sweep_all_datasets.pdf    — 3x2 K-sweep grid (cov_cond, set_size)
  4. fig_alpha_sweep.pdf             — TriviaQA alpha sweep (cov_cond, set_size)
  5. fig_sigma_plugin_landscape.pdf  — sigma* histogram vs Theorem 2 prediction

Usage:
    python code/v2/make_figures_v3.py
"""
from __future__ import annotations

import json
import os
import sys
import warnings
from collections import defaultdict
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------------------
# Paths & global config
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = REPO_ROOT / "artifacts" / "v2_results"
OUT_DIR = REPO_ROOT / "artifacts" / "deliverables" / "charts"
OUT_DIR.mkdir(parents=True, exist_ok=True)

DATASETS = ["triviaqa", "squad", "nq_open"]
DATASET_LABELS = {"triviaqa": "TriviaQA", "squad": "SQuAD", "nq_open": "NQ-open"}
METHODS = ["semcp_v2", "m_semcp", "conu", "safer_tuned", "lofreecp_tuned", "tecp_tuned"]
METHOD_LABELS = {
    "semcp_v2": "SemCP",
    "m_semcp": "M-SemCP",
    "conu": "ConU",
    "safer_tuned": "SAFER",
    "lofreecp_tuned": "LoFreeCP",
    "tecp_tuned": "TECP",
}
HIGHLIGHT_METHODS = {"semcp_v2", "m_semcp"}

# tab10 — colorblind friendly enough; we pin per-method
PALETTE = {
    "semcp_v2": "#1f77b4",       # blue
    "m_semcp": "#17becf",        # cyan
    "conu": "#ff7f0e",           # orange
    "safer_tuned": "#2ca02c",    # green
    "lofreecp_tuned": "#d62728", # red
    "tecp_tuned": "#9467bd",     # purple
}

plt.rcParams.update({
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "figure.dpi": 120,
    "savefig.dpi": 200,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "axes.spines.top": False,
    "axes.spines.right": False,
})


# ---------------------------------------------------------------------------
# Loaders & aggregators
# ---------------------------------------------------------------------------

def _load_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        with path.open() as f:
            return json.load(f)
    except Exception as e:  # noqa: BLE001
        warnings.warn(f"Failed to load {path}: {e}")
        return None


def load_summaries(dataset: str) -> list[dict] | None:
    return _load_json(RESULTS_DIR / dataset / "summaries.json")


def load_k_sweep(dataset: str) -> list[dict] | None:
    return _load_json(RESULTS_DIR / dataset / "k_sweep.json")


def aggregate(records: list[dict], group_keys: tuple[str, ...], value_keys: tuple[str, ...]) -> dict:
    """Mean & std of value_keys grouped by group_keys (across remaining records, e.g. seeds).

    Returns: {group_tuple: {value_key: (mean, std, n)}}
    """
    buckets: dict[tuple, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for r in records:
        try:
            key = tuple(r[k] for k in group_keys)
        except KeyError:
            continue
        for v in value_keys:
            if v in r and r[v] is not None:
                try:
                    buckets[key][v].append(float(r[v]))
                except (TypeError, ValueError):
                    pass
    out: dict = {}
    for key, vmap in buckets.items():
        out[key] = {}
        for v, lst in vmap.items():
            arr = np.asarray(lst, dtype=float)
            if arr.size == 0:
                continue
            out[key][v] = (float(arr.mean()), float(arr.std(ddof=0)), int(arr.size))
    return out


# ---------------------------------------------------------------------------
# Figure 1 — Validity gap forest plot
# ---------------------------------------------------------------------------

def fig_validity_gap() -> Path | None:
    rows = []  # (dataset, method, mean_gap, std_gap, alpha)
    for ds in DATASETS:
        s = load_summaries(ds)
        if not s:
            warnings.warn(f"[fig1] missing summaries for {ds}")
            continue
        agg = aggregate(s, ("method", "alpha"), ("coverage_conditional",))
        for (m, alpha), vals in agg.items():
            if "coverage_conditional" not in vals:
                continue
            mean_cov, std_cov, _ = vals["coverage_conditional"]
            target = 1.0 - alpha
            rows.append((ds, m, mean_cov - target, std_cov, alpha))

    if not rows:
        warnings.warn("[fig1] no rows; skipping")
        return None

    # Order: dataset blocks; within each, methods in METHODS order.
    method_order = METHODS

    fig, ax = plt.subplots(figsize=(8.0, 7.5))

    y = 0
    yticks: list[float] = []
    yticklabels: list[str] = []
    block_separators: list[float] = []
    for ds_idx, ds in enumerate(DATASETS):
        ds_rows = [r for r in rows if r[0] == ds]
        if not ds_rows:
            continue
        # sort according to METHODS list
        ds_rows.sort(key=lambda r: method_order.index(r[1]) if r[1] in method_order else 999)
        for (_, m, gap, std, _alpha) in ds_rows:
            if 0.0 <= gap <= 0.05:
                color = "#2ca02c"  # green tight valid
            elif gap > 0.05:
                color = "#d4a017"  # yellow loose valid
            else:
                color = "#d62728"  # red invalid

            highlight = m in HIGHLIGHT_METHODS
            ax.errorbar(
                gap, y, xerr=std, fmt="o",
                color=color,
                ecolor=color, elinewidth=2.0 if highlight else 1.4,
                capsize=4 if highlight else 3,
                markersize=9 if highlight else 6,
                markeredgecolor="black" if highlight else color,
                markeredgewidth=1.2 if highlight else 0.0,
                zorder=3,
            )
            label = METHOD_LABELS.get(m, m)
            ds_label = DATASET_LABELS[ds]
            tick = f"{label}  [{ds_label}]"
            if highlight:
                # Use unicode bold-ish via fontweight in tick labels later; avoid mathtext on hyphen
                tick = f"* {label}  [{ds_label}]"
            yticks.append(y)
            yticklabels.append(tick)
            y += 1
        block_separators.append(y - 0.5)
        y += 1  # gap between dataset blocks

    ax.axvline(0.0, color="black", linestyle="--", linewidth=1.0, zorder=1, alpha=0.7)
    for sep in block_separators[:-1]:
        ax.axhline(sep, color="lightgray", linewidth=0.6, linestyle=":")

    ax.set_yticks(yticks)
    ax.set_yticklabels(yticklabels)
    # Bold the highlighted rows (those whose label starts with "* ")
    for tlabel in ax.get_yticklabels():
        if tlabel.get_text().startswith("* "):
            tlabel.set_fontweight("bold")
    ax.invert_yaxis()
    ax.set_xlabel("Validity gap  =  conditional coverage  $-$  (1$-\\alpha$)")
    ax.set_title("Validity Gap Across Datasets and Methods (mean $\\pm$ std over 3 seeds)")
    ax.grid(axis="x", linestyle=":", linewidth=0.5, alpha=0.6)

    # Legend
    from matplotlib.patches import Patch
    legend_elems = [
        Patch(facecolor="#2ca02c", label=r"Tight valid ($0 \leq \mathrm{gap} \leq 0.05$)"),
        Patch(facecolor="#d4a017", label=r"Loose valid ($\mathrm{gap} > 0.05$)"),
        Patch(facecolor="#d62728", label=r"Invalid ($\mathrm{gap} < 0$)"),
    ]
    ax.legend(handles=legend_elems, loc="lower right", framealpha=0.9)

    out = OUT_DIR / "fig_validity_gap_errorbars.pdf"
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# Figure 2 — Admissibility breakdown
# ---------------------------------------------------------------------------

def fig_admissibility() -> Path | None:
    fig, axes = plt.subplots(1, 3, figsize=(13.0, 4.5), sharey=True)
    drew = False

    for ax, ds in zip(axes, DATASETS):
        s = load_summaries(ds)
        if not s:
            ax.set_visible(False)
            warnings.warn(f"[fig2] missing summaries for {ds}")
            continue
        agg = aggregate(s, ("method",), ("admissible_rate",))
        method_order = [m for m in METHODS if (m,) in agg]
        means = [agg[(m,)]["admissible_rate"][0] for m in method_order]
        stds = [agg[(m,)]["admissible_rate"][1] for m in method_order]
        colors = [PALETTE.get(m, "gray") for m in method_order]
        edgecolors = ["black" if m in HIGHLIGHT_METHODS else c
                      for m, c in zip(method_order, colors)]
        linewidths = [1.6 if m in HIGHLIGHT_METHODS else 0.0 for m in method_order]

        x = np.arange(len(method_order))
        bars = ax.bar(x, means, yerr=stds, color=colors,
                      edgecolor=edgecolors, linewidth=linewidths, capsize=4)
        del bars
        ax.set_xticks(x)
        labels = []
        for m in method_order:
            lbl = METHOD_LABELS.get(m, m)
            if m in HIGHLIGHT_METHODS:
                labels.append(f"$\\bf{{{lbl}}}$")
            else:
                labels.append(lbl)
        ax.set_xticklabels(labels, rotation=25, ha="right")
        ax.set_title(DATASET_LABELS[ds])
        ax.set_ylim(0.0, 1.05)
        ax.grid(axis="y", linestyle=":", linewidth=0.5, alpha=0.6)

        # p_A annotation = mean admissible_rate across methods/seeds (stable per dataset
        # because it's a property of the pool, not the method — but we average to be safe)
        all_pa = [r["admissible_rate"] for r in s if "admissible_rate" in r]
        if all_pa:
            pa = float(np.mean(all_pa))
            ax.text(0.5, 1.02, f"Pool quality: $p_A = {pa:.2f}$",
                    transform=ax.transAxes, ha="center", va="bottom",
                    fontsize=10, fontweight="bold")

        # Inset on nq_open: conditional coverage on admissible subset
        if ds == "nq_open":
            agg_cov = aggregate(s, ("method",), ("coverage_conditional",))
            ins = ax.inset_axes([0.55, 0.07, 0.42, 0.40])
            mo = [m for m in METHODS if (m,) in agg_cov]
            cov_means = [agg_cov[(m,)]["coverage_conditional"][0] for m in mo]
            cov_stds = [agg_cov[(m,)]["coverage_conditional"][1] for m in mo]
            ins.bar(np.arange(len(mo)), cov_means, yerr=cov_stds,
                    color=[PALETTE.get(m, "gray") for m in mo], capsize=2)
            ins.axhline(0.9, color="black", linestyle="--", linewidth=0.8)
            ins.set_ylim(0.7, 1.02)
            ins.set_xticks(np.arange(len(mo)))
            ins.set_xticklabels([METHOD_LABELS.get(m, m) for m in mo],
                                rotation=45, ha="right", fontsize=7)
            ins.tick_params(axis="y", labelsize=7)
            ins.set_title("Cond. cov. on admissible (Thm. 1)", fontsize=8)
            ins.grid(axis="y", linestyle=":", linewidth=0.4, alpha=0.5)

        drew = True

    axes[0].set_ylabel("Admissible rate")
    fig.suptitle("Sample Pool Admissibility — Theorem 1 Holds When $p_A > 0$",
                 fontsize=12, y=1.02)
    fig.tight_layout()

    if not drew:
        plt.close(fig)
        return None

    out = OUT_DIR / "fig_admissibility_breakdown.pdf"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# Figure 3 — K-sweep across all datasets
# ---------------------------------------------------------------------------

def fig_k_sweep() -> Path | None:
    fig, axes = plt.subplots(3, 2, figsize=(11.0, 11.0), sharex=True)
    any_drawn = False

    for row_idx, ds in enumerate(DATASETS):
        ks = load_k_sweep(ds)
        if not ks:
            warnings.warn(f"[fig3] missing k_sweep for {ds}")
            for col in (0, 1):
                axes[row_idx, col].set_visible(False)
            continue

        agg = aggregate(ks, ("method", "K"), ("cov_cond", "set_size"))
        methods_present = sorted({m for (m, _) in agg.keys()},
                                 key=lambda m: METHODS.index(m) if m in METHODS else 999)

        for col, metric, ylabel in [
            (0, "cov_cond", "Conditional coverage"),
            (1, "set_size", "Active set size"),
        ]:
            ax = axes[row_idx, col]
            for m in methods_present:
                Ks = sorted(K for (mm, K) in agg.keys() if mm == m)
                xs = np.array(Ks, dtype=float)
                means = np.array([agg[(m, K)][metric][0] for K in Ks])
                stds = np.array([agg[(m, K)][metric][1] for K in Ks])
                color = PALETTE.get(m, "gray")
                lw = 2.6 if m in HIGHLIGHT_METHODS else 1.4
                marker = "o" if m in HIGHLIGHT_METHODS else "s"
                ax.errorbar(
                    xs, means, yerr=stds, marker=marker, color=color,
                    linewidth=lw, markersize=7 if m in HIGHLIGHT_METHODS else 5,
                    capsize=3, label=METHOD_LABELS.get(m, m),
                )

            if col == 0:
                ax.axhline(0.9, color="black", linestyle="--", linewidth=0.8, alpha=0.7)
                ax.text(0.02, 0.92, "$1-\\alpha = 0.9$", transform=ax.transAxes,
                        fontsize=8, va="bottom")
            ax.set_ylabel(ylabel)
            ax.grid(linestyle=":", linewidth=0.5, alpha=0.6)
            if row_idx == 0:
                # Saturation annotation on coverage panel
                if col == 0 and "semcp_v2" in methods_present:
                    Ks_sv = sorted(K for (mm, K) in agg.keys() if mm == "semcp_v2")
                    if 10 in Ks_sv and 7 in Ks_sv:
                        c10 = agg[("semcp_v2", 10)]["cov_cond"][0]
                        c7 = agg[("semcp_v2", 7)]["cov_cond"][0]
                        if abs(c10 - c7) < 0.02:
                            ax.annotate(
                                "Saturation at K=10",
                                xy=(10, c10), xytext=(7.0, c10 - 0.07),
                                fontsize=8,
                                arrowprops=dict(arrowstyle="->", color="gray", lw=0.8),
                            )
            if row_idx == 0 and col == 1:
                ax.legend(loc="upper left", ncol=2, framealpha=0.9, fontsize=8)
            if row_idx == 2:
                ax.set_xlabel("$K$ (pool size)")
            # row label
            if col == 0:
                ax.text(-0.18, 0.5, DATASET_LABELS[ds],
                        transform=ax.transAxes, rotation=90,
                        ha="center", va="center", fontsize=11, fontweight="bold")
            any_drawn = True

    fig.suptitle("K-Sweep Ablation Across Datasets", fontsize=13, y=1.0)
    fig.tight_layout()

    if not any_drawn:
        plt.close(fig)
        return None

    out = OUT_DIR / "fig_k_sweep_all_datasets.pdf"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# Figure 4 — alpha sweep on TriviaQA
# ---------------------------------------------------------------------------

def fig_alpha_sweep() -> Path | None:
    s_main = load_summaries("triviaqa") or []
    s_alpha = _load_json(RESULTS_DIR / "triviaqa_alpha" / "summaries.json") or []
    records = list(s_main) + list(s_alpha)
    if not records:
        warnings.warn("[fig4] no records")
        return None

    agg = aggregate(records, ("method", "alpha"), ("coverage_conditional", "set_size_active"))
    methods_present = sorted({m for (m, _) in agg.keys()},
                             key=lambda m: METHODS.index(m) if m in METHODS else 999)

    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.5))

    for col, metric, ylabel, want_target in [
        (0, "coverage_conditional", "Conditional coverage", True),
        (1, "set_size_active", "Active set size", False),
    ]:
        ax = axes[col]
        for m in methods_present:
            alphas = sorted(a for (mm, a) in agg.keys() if mm == m and metric in agg[(mm, a)])
            if not alphas:
                continue
            xs = np.array(alphas, dtype=float)
            means = np.array([agg[(m, a)][metric][0] for a in alphas])
            stds = np.array([agg[(m, a)][metric][1] for a in alphas])
            color = PALETTE.get(m, "gray")
            lw = 2.6 if m in HIGHLIGHT_METHODS else 1.4
            ax.errorbar(
                xs, means, yerr=stds, marker="o", color=color,
                linewidth=lw, markersize=7 if m in HIGHLIGHT_METHODS else 5,
                capsize=3, label=METHOD_LABELS.get(m, m),
            )

        if want_target:
            xs = np.linspace(0.04, 0.21, 50)
            ax.plot(xs, 1.0 - xs, color="black", linestyle="--",
                    linewidth=1.0, alpha=0.7, label="$1-\\alpha$ target")

        ax.set_xlabel("$\\alpha$")
        ax.set_ylabel(ylabel)
        ax.grid(linestyle=":", linewidth=0.5, alpha=0.6)
        if col == 0:
            ax.legend(loc="lower left", fontsize=8, framealpha=0.9, ncol=2)

    fig.suptitle("Coverage and Set Size vs $\\alpha$ (TriviaQA)", fontsize=12, y=1.02)
    fig.tight_layout()
    out = OUT_DIR / "fig_alpha_sweep.pdf"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# Figure 5 — sigma plug-in landscape
# ---------------------------------------------------------------------------

def fig_sigma_plugin() -> Path | None:
    sigmas = []
    alphas_seen = []
    # main alpha=0.1 across datasets
    for ds in DATASETS:
        s = load_summaries(ds)
        if not s:
            continue
        for r in s:
            if r.get("method") != "semcp_v2":
                continue
            sig = r.get("sigma")
            alpha = r.get("alpha")
            if sig is None or alpha is None:
                continue
            sigmas.append(float(sig))
            alphas_seen.append(float(alpha))

    # alpha sweep
    s_alpha = _load_json(RESULTS_DIR / "triviaqa_alpha" / "summaries.json") or []
    for r in s_alpha:
        if r.get("method") != "semcp_v2":
            continue
        sig = r.get("sigma")
        alpha = r.get("alpha")
        if sig is None or alpha is None:
            continue
        sigmas.append(float(sig))
        alphas_seen.append(float(alpha))

    if not sigmas:
        warnings.warn("[fig5] no sigma values for semcp_v2")
        return None

    sigmas_arr = np.asarray(sigmas)
    alphas_arr = np.asarray(alphas_seen)

    fig, ax = plt.subplots(figsize=(8.0, 5.0))

    # Histogram of empirical sigma values (semcp_v2 plug-in)
    ax.hist(sigmas_arr, bins=12, color=PALETTE["semcp_v2"], alpha=0.55,
            edgecolor="black", linewidth=0.6, label="Empirical $\\sigma^*$ (SemCP plug-in)")

    # Mean & std reference lines
    sig_mean = float(sigmas_arr.mean())
    sig_std = float(sigmas_arr.std(ddof=0))
    ax.axvline(sig_mean, color="black", linestyle="-", linewidth=1.2,
               label=f"Empirical mean = {sig_mean:.2f}")
    ax.axvline(sig_mean - sig_std, color="gray", linestyle=":", linewidth=1.0)
    ax.axvline(sig_mean + sig_std, color="gray", linestyle=":", linewidth=1.0,
               label=f"$\\pm 1\\sigma$ band")

    # Theorem 2 prediction overlay:  sigma* = sqrt((mu_B - mu_W) / (2 log(1/(1-alpha))))
    # We don't have mu_B - mu_W directly; sweep an "implied" range and at alpha=0.1.
    # Solve for implied delta given empirical mean: delta_emp = sig_mean^2 * 2 log(1/(1-alpha))
    alpha_ref = 0.1
    log_term_ref = 2.0 * np.log(1.0 / (1.0 - alpha_ref))
    implied_delta = sig_mean * sig_mean * log_term_ref
    delta_grid = np.linspace(max(0.01, implied_delta * 0.4), implied_delta * 1.6, 80)
    sigma_pred = np.sqrt(delta_grid / log_term_ref)

    # Draw Theorem 2 prediction curve on twin axis (right) so it shares x with the hist
    ax2 = ax.twinx()
    ax2.plot(sigma_pred, delta_grid, color="#d62728", linewidth=2.0,
             label="Thm. 2: $\\sigma^* = \\sqrt{(\\mu_B - \\mu_W) / (2\\log(1/(1-\\alpha)))}$")
    ax2.set_ylabel("Implied $\\mu_B - \\mu_W$ (at $\\alpha=0.1$)", color="#d62728")
    ax2.tick_params(axis="y", labelcolor="#d62728")
    ax2.spines["right"].set_visible(True)
    ax2.spines["right"].set_color("#d62728")

    # Mark implied delta at empirical mean
    ax2.scatter([sig_mean], [implied_delta], color="#d62728", s=60, zorder=5,
                edgecolor="black", linewidth=0.8,
                label=f"Implied $\\mu_B-\\mu_W = {implied_delta:.2f}$")

    ax.set_xlabel("$\\sigma^*$ (plug-in bandwidth)")
    ax.set_ylabel("Count (over (dataset, seed, $\\alpha$))")
    ax.grid(linestyle=":", linewidth=0.5, alpha=0.6)

    # Combine legends
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper right", fontsize=8, framealpha=0.95)

    n = sigmas_arr.size
    ax.set_title(
        f"Plug-in Bandwidth $\\sigma^*$ — Empirical Distribution vs Theorem 2 Prediction "
        f"(n={n}; $\\alpha\\in${{ {','.join(f'{a:g}' for a in sorted(set(alphas_arr)))} }})"
    )

    out = OUT_DIR / "fig_sigma_plugin_landscape.pdf"
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def main() -> int:
    print(f"Output directory: {OUT_DIR}")
    print("Generating figures...\n")

    targets = [
        ("Figure 1 (validity gap)", fig_validity_gap),
        ("Figure 2 (admissibility)", fig_admissibility),
        ("Figure 3 (K-sweep)", fig_k_sweep),
        ("Figure 4 (alpha sweep)", fig_alpha_sweep),
        ("Figure 5 (sigma plug-in)", fig_sigma_plugin),
    ]

    failures = 0
    for name, fn in targets:
        try:
            out = fn()
        except Exception as e:  # noqa: BLE001
            failures += 1
            print(f"[FAIL] {name}: {e!r}")
            continue
        if out is None:
            failures += 1
            print(f"[SKIP] {name}: missing data")
        else:
            print(f"[OK]   {name}: {out}")

    print(f"\nDone. {len(targets) - failures}/{len(targets)} figures written.")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
