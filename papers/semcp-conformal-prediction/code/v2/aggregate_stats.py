"""
Aggregate SemCP v2 results across 3 seeds.

Reads:
    artifacts/v2_results/{triviaqa,squad,nq_open}/summaries.json
    artifacts/v2_results/triviaqa_alpha/summaries.json
    artifacts/v2_results/{triviaqa,squad,nq_open}/k_sweep.json
    artifacts/v2_results/triviaqa/stress.json

Writes:
    artifacts/v2_revision/aggregated_results.json
    artifacts/v2_revision/aggregated_table.tex
    artifacts/v2_revision/aggregated_table.md
    artifacts/v2_revision/k_sweep_aggregated.csv
    artifacts/v2_revision/stress_aggregated.json

Usage:  python code/v2/aggregate_stats.py
"""

from __future__ import annotations

import json
import sys
import warnings
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = REPO_ROOT / "artifacts" / "v2_results"
OUT_DIR = REPO_ROOT / "artifacts" / "v2_revision"
OUT_DIR.mkdir(parents=True, exist_ok=True)

DATASETS = ["triviaqa", "squad", "nq_open"]
ALPHA_VARIATION_DIR = RESULTS_DIR / "triviaqa_alpha"

METRIC_KEYS = [
    "coverage_marginal",
    "coverage_conditional",
    "set_size_active",
    "abstain_rate",
    "admissible_rate",
    "q_hat",
    "sigma",
]

# Method display order (consistent across tables)
METHOD_ORDER = [
    "semcp_v2",
    "m_semcp",
    "conu",
    "safer_tuned",
    "lofreecp_tuned",
    "tecp_tuned",
]

PRETTY_METHOD = {
    "semcp_v2": "SemCP-v2",
    "m_semcp": "M-SemCP",
    "conu": "CoNU",
    "safer_tuned": "SAFER (tuned)",
    "lofreecp_tuned": "LoFreeCP (tuned)",
    "tecp_tuned": "TECP (tuned)",
}

PRETTY_DATASET = {
    "triviaqa": "TriviaQA",
    "squad": "SQuAD",
    "nq_open": "NaturalQuestions",
}

PRETTY_METRIC = {
    "coverage_marginal": "Cov$_{\\mathrm{marg}}$",
    "coverage_conditional": "Cov$_{\\mathrm{cond}}$",
    "set_size_active": "$|\\mathcal{C}|$",
    "abstain_rate": "Abstain",
    "admissible_rate": "Admis.",
    "q_hat": "$\\hat q$",
    "sigma": "$\\sigma$",
    "validity_gap": "Validity gap",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _safe_float(x: Any) -> float | None:
    if x is None:
        return None
    try:
        v = float(x)
        if np.isnan(v):
            return None
        return v
    except (TypeError, ValueError):
        return None


def bootstrap_ci(values: np.ndarray, n_boot: int = 1000, seed: int = 0) -> tuple[float, float]:
    """Percentile bootstrap CI on the mean of `values`. Returns (lo, hi)."""
    values = values[np.isfinite(values)]
    if len(values) == 0:
        return (float("nan"), float("nan"))
    if len(values) == 1:
        return (float(values[0]), float(values[0]))
    rng = np.random.default_rng(seed)
    boot_means = np.empty(n_boot, dtype=float)
    n = len(values)
    for i in range(n_boot):
        idx = rng.integers(0, n, size=n)
        boot_means[i] = values[idx].mean()
    lo, hi = np.percentile(boot_means, [2.5, 97.5])
    return float(lo), float(hi)


def aggregate_metric(values: list[float]) -> dict[str, float]:
    arr = np.array([v for v in values if v is not None and np.isfinite(v)], dtype=float)
    if arr.size == 0:
        return {"mean": float("nan"), "std": float("nan"), "ci_lo": float("nan"),
                "ci_hi": float("nan"), "n": 0, "values": []}
    lo, hi = bootstrap_ci(arr)
    return {
        "mean": float(arr.mean()),
        "std": float(arr.std(ddof=0)) if arr.size > 1 else 0.0,
        "ci_lo": lo,
        "ci_hi": hi,
        "n": int(arr.size),
        "values": arr.tolist(),
    }


def get_n_admissible_cal(rec: dict, n_cal: int) -> int | None:
    """Pull n_admissible_cal from aux_log if present; else estimate from admissible_rate."""
    aux = rec.get("aux_log") or {}
    n_adm = aux.get("n_admissible_cal")
    if n_adm is not None:
        return int(n_adm)
    # fallback: round(admissible_rate * n_cal). Note: admissible_rate is computed
    # on test, but in this experiment cal & test draw from same population — so it's
    # an unbiased estimate of P(A) and thus of E[n_admissible_cal / n_cal].
    rate = rec.get("admissible_rate")
    if rate is None:
        return None
    return int(round(float(rate) * n_cal))


def validity_gap(rec: dict) -> float | None:
    """Per-seed validity gap: cov_cond - (1 - alpha - 1/(n_admissible_cal+1)).

    Positive => over-covers vs target lower bound (good for validity).
    """
    cov = _safe_float(rec.get("coverage_conditional"))
    alpha = _safe_float(rec.get("alpha"))
    n_cal = rec.get("n_cal", rec.get("n", 150))
    n_adm = get_n_admissible_cal(rec, int(n_cal))
    if cov is None or alpha is None or n_adm is None or n_adm <= 0:
        return None
    target = 1.0 - alpha - 1.0 / (n_adm + 1)
    return cov - target


# ---------------------------------------------------------------------------
# 1. Aggregate summaries (main + alpha sweep)
# ---------------------------------------------------------------------------


def load_summaries() -> list[dict]:
    """Returns flat list of result dicts, each tagged with `dataset`."""
    out: list[dict] = []
    for ds in DATASETS:
        path = RESULTS_DIR / ds / "summaries.json"
        if not path.exists():
            warnings.warn(f"missing summaries: {path}")
            continue
        with path.open() as f:
            recs = json.load(f)
        for r in recs:
            r2 = dict(r)
            r2["dataset"] = ds
            out.append(r2)
    # alpha sweep
    apath = ALPHA_VARIATION_DIR / "summaries.json"
    if apath.exists():
        with apath.open() as f:
            for r in json.load(f):
                r2 = dict(r)
                r2["dataset"] = "triviaqa"  # alpha sweep is on triviaqa
                out.append(r2)
    else:
        warnings.warn(f"missing alpha sweep summaries: {apath}")
    return out


def aggregate_summaries(records: list[dict]) -> dict:
    """Group by (dataset, method, alpha), aggregate over seeds."""
    groups: dict[tuple[str, str, float], list[dict]] = defaultdict(list)
    for r in records:
        key = (r["dataset"], r["method"], float(r["alpha"]))
        groups[key].append(r)

    aggregated: dict[str, dict] = {}
    for (dataset, method, alpha), recs in sorted(groups.items()):
        seeds = sorted(int(r["seed"]) for r in recs)
        per_metric: dict[str, dict] = {}
        for m in METRIC_KEYS:
            vals = [_safe_float(r.get(m)) for r in recs]
            per_metric[m] = aggregate_metric(vals)
        # validity gap
        gap_vals = [validity_gap(r) for r in recs]
        per_metric["validity_gap"] = aggregate_metric(gap_vals)

        gkey = f"{dataset}|{method}|alpha={alpha}"
        aggregated[gkey] = {
            "dataset": dataset,
            "method": method,
            "alpha": alpha,
            "seeds": seeds,
            "n_seeds": len(seeds),
            "metrics": per_metric,
        }
    return aggregated


# ---------------------------------------------------------------------------
# 2. K-sweep aggregation
# ---------------------------------------------------------------------------


def aggregate_k_sweep() -> pd.DataFrame:
    rows: list[dict] = []
    for ds in DATASETS:
        path = RESULTS_DIR / ds / "k_sweep.json"
        if not path.exists():
            warnings.warn(f"missing k_sweep: {path}")
            continue
        with path.open() as f:
            recs = json.load(f)
        df = pd.DataFrame(recs)
        df["dataset"] = ds
        rows.append(df)
    if not rows:
        return pd.DataFrame()
    df_all = pd.concat(rows, ignore_index=True)

    # k_sweep may use cov_cond / set_size as field names
    cov_field = "cov_cond" if "cov_cond" in df_all.columns else "coverage_conditional"
    size_field = "set_size" if "set_size" in df_all.columns else "set_size_active"

    grp = df_all.groupby(["dataset", "method", "K"], as_index=False).agg(
        coverage_conditional_mean=(cov_field, "mean"),
        coverage_conditional_std=(cov_field, "std"),
        set_size_mean=(size_field, "mean"),
        set_size_std=(size_field, "std"),
        n_seeds=("seed", "nunique"),
    )
    # std with single seed -> NaN; replace with 0
    grp[["coverage_conditional_std", "set_size_std"]] = grp[
        ["coverage_conditional_std", "set_size_std"]
    ].fillna(0.0)
    return grp.sort_values(["dataset", "method", "K"]).reset_index(drop=True)


# ---------------------------------------------------------------------------
# 3. Stress test aggregation (TriviaQA only, 100 folds)
# ---------------------------------------------------------------------------


def aggregate_stress(alpha: float = 0.1) -> dict:
    out: dict[str, dict] = {}
    for ds in DATASETS:
        path = RESULTS_DIR / ds / "stress.json"
        if not path.exists():
            warnings.warn(f"missing stress: {path}")
            continue
        with path.open() as f:
            stress = json.load(f)
        per_method: dict[str, dict] = {}
        for method, folds in stress.items():
            cov_vals = np.array([float(f["cov_cond"]) for f in folds], dtype=float)
            size_vals = np.array([float(f["set_size"]) for f in folds], dtype=float)
            absten = np.array([float(f.get("abstain", np.nan)) for f in folds], dtype=float)
            target = 1.0 - alpha
            pass_rate = float((cov_vals >= target).mean())
            per_method[method] = {
                "n_folds": int(len(folds)),
                "cov_cond_mean": float(cov_vals.mean()),
                "cov_cond_std": float(cov_vals.std(ddof=0)),
                "cov_cond_min": float(cov_vals.min()),
                "cov_cond_max": float(cov_vals.max()),
                "set_size_mean": float(size_vals.mean()),
                "set_size_std": float(size_vals.std(ddof=0)),
                "abstain_mean": float(np.nanmean(absten)) if absten.size else float("nan"),
                "pass_rate_at_1minus_alpha": pass_rate,
                "alpha": alpha,
            }
        out[ds] = per_method
    return out


# ---------------------------------------------------------------------------
# 4. LaTeX / markdown table writers (alpha=0.1 main results)
# ---------------------------------------------------------------------------


def _fmt(mean: float, std: float, prec: int = 3) -> str:
    if not np.isfinite(mean):
        return "--"
    return f"{mean:.{prec}f} $\\pm$ {std:.{prec}f}"


def _fmt_md(mean: float, std: float, prec: int = 3) -> str:
    if not np.isfinite(mean):
        return "--"
    return f"{mean:.{prec}f} ± {std:.{prec}f}"


def _select_main(aggregated: dict, alpha: float = 0.1) -> dict:
    return {
        k: v for k, v in aggregated.items() if abs(v["alpha"] - alpha) < 1e-9
    }


def write_latex_table(aggregated: dict, out_path: Path) -> None:
    main = _select_main(aggregated, 0.1)
    cols = ["coverage_conditional", "set_size_active", "abstain_rate", "validity_gap"]
    header = (
        "Dataset & Method & "
        + " & ".join(PRETTY_METRIC[c] for c in cols)
        + " \\\\"
    )

    lines: list[str] = []
    lines.append("% Auto-generated by code/v2/aggregate_stats.py — do not edit by hand.")
    lines.append("\\begin{table}[t]")
    lines.append("\\centering")
    lines.append(
        "\\caption{Main results at $\\alpha=0.1$, aggregated across 3 seeds "
        "(mean $\\pm$ std). Validity gap = $\\widehat{\\mathrm{cov}}_{\\mathrm{cond}}"
        " - (1-\\alpha - 1/(n_{\\mathrm{adm,cal}}+1))$; positive values are valid.}"
    )
    lines.append("\\label{tab:main_v2}")
    lines.append("\\begin{tabular}{ll" + "c" * len(cols) + "}")
    lines.append("\\toprule")
    lines.append(header)
    lines.append("\\midrule")

    for ds in DATASETS:
        first = True
        for method in METHOD_ORDER:
            key = f"{ds}|{method}|alpha=0.1"
            if key not in main:
                continue
            entry = main[key]
            ds_cell = PRETTY_DATASET[ds] if first else ""
            cells = [ds_cell, PRETTY_METHOD.get(method, method)]
            for c in cols:
                m = entry["metrics"].get(c, {"mean": float("nan"), "std": float("nan")})
                cells.append(_fmt(m["mean"], m["std"]))
            lines.append(" & ".join(cells) + " \\\\")
            first = False
        lines.append("\\midrule")
    if lines[-1] == "\\midrule":
        lines[-1] = "\\bottomrule"
    else:
        lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    lines.append("\\end{table}")

    out_path.write_text("\n".join(lines) + "\n")


def write_markdown_table(aggregated: dict, out_path: Path) -> None:
    main = _select_main(aggregated, 0.1)
    cols = [
        "coverage_marginal",
        "coverage_conditional",
        "set_size_active",
        "abstain_rate",
        "admissible_rate",
        "q_hat",
        "sigma",
        "validity_gap",
    ]

    lines = ["# SemCP v2 — Aggregated Results (alpha = 0.1)\n"]
    lines.append("Mean ± std across 3 seeds. 95% bootstrap CIs in JSON.\n")

    header = ["Dataset", "Method", "n_seeds"] + [PRETTY_METRIC[c].replace("$", "").replace("\\mathrm", "")
                                                  .replace("{", "").replace("}", "")
                                                  .replace("\\hat q", "q_hat")
                                                  .replace("|\\mathcal C|", "set_size")
                                                  for c in cols]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "---|" * len(header))

    for ds in DATASETS:
        for method in METHOD_ORDER:
            key = f"{ds}|{method}|alpha=0.1"
            if key not in main:
                continue
            entry = main[key]
            row = [PRETTY_DATASET[ds], PRETTY_METHOD.get(method, method), str(entry["n_seeds"])]
            for c in cols:
                m = entry["metrics"].get(c, {"mean": float("nan"), "std": float("nan")})
                row.append(_fmt_md(m["mean"], m["std"]))
            lines.append("| " + " | ".join(row) + " |")

    # alpha sweep section
    alpha_keys = [k for k, v in aggregated.items()
                  if v["dataset"] == "triviaqa" and abs(v["alpha"] - 0.1) > 1e-9]
    if alpha_keys:
        lines.append("\n## Alpha sweep on TriviaQA (alpha != 0.1)\n")
        lines.append("| Method | alpha | Cov_cond | set_size | abstain | validity_gap |")
        lines.append("|---|---|---|---|---|---|")
        for k in sorted(alpha_keys, key=lambda x: (aggregated[x]["alpha"], aggregated[x]["method"])):
            v = aggregated[k]
            mm = v["metrics"]
            lines.append(
                f"| {PRETTY_METHOD.get(v['method'], v['method'])} | {v['alpha']:.2f} | "
                f"{_fmt_md(mm['coverage_conditional']['mean'], mm['coverage_conditional']['std'])} | "
                f"{_fmt_md(mm['set_size_active']['mean'], mm['set_size_active']['std'])} | "
                f"{_fmt_md(mm['abstain_rate']['mean'], mm['abstain_rate']['std'])} | "
                f"{_fmt_md(mm['validity_gap']['mean'], mm['validity_gap']['std'])} |"
            )

    out_path.write_text("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# 5. Summary print
# ---------------------------------------------------------------------------


def print_final_summary(aggregated: dict, k_df: pd.DataFrame, stress: dict) -> None:
    print("=" * 72)
    print("SemCP v2 — Aggregation Summary")
    print("=" * 72)

    n_combos = len(aggregated)
    print(f"\nAggregated (dataset, method, alpha) combinations: {n_combos}")
    by_seeds = defaultdict(int)
    for v in aggregated.values():
        by_seeds[v["n_seeds"]] += 1
    for k in sorted(by_seeds):
        print(f"  {by_seeds[k]} groups have {k} seed(s)")

    # Headline: SemCP_v2 conditional coverage on each dataset (alpha=0.1)
    print("\nHEADLINE — SemCP-v2 conditional coverage @ alpha=0.1 (mean ± std [95% boot CI]):")
    for ds in DATASETS:
        key = f"{ds}|semcp_v2|alpha=0.1"
        if key not in aggregated:
            print(f"  {PRETTY_DATASET[ds]:>18}: MISSING")
            continue
        m = aggregated[key]["metrics"]["coverage_conditional"]
        print(f"  {PRETTY_DATASET[ds]:>18}: {m['mean']:.4f} ± {m['std']:.4f}  "
              f"[{m['ci_lo']:.4f}, {m['ci_hi']:.4f}]  n_seeds={aggregated[key]['n_seeds']}")

    # Validity gap
    print("\nVALIDITY GAP (mean ± std) per (dataset, method) @ alpha=0.1:")
    print(f"  {'Dataset':<18} {'Method':<18} {'gap (mean±std)':<20} {'n':<3}")
    for ds in DATASETS:
        for method in METHOD_ORDER:
            key = f"{ds}|{method}|alpha=0.1"
            if key not in aggregated:
                continue
            g = aggregated[key]["metrics"]["validity_gap"]
            tag = ""
            if np.isfinite(g["mean"]):
                tag = "  VALID" if g["mean"] >= 0 else "  UNDER"
            print(f"  {PRETTY_DATASET[ds]:<18} {PRETTY_METHOD.get(method, method):<18} "
                  f"{g['mean']:+.4f} ± {g['std']:.4f}{tag}  n={g['n']}")

    # K sweep saturation: low K vs high K (data sweeps K in {3,5,7,10})
    if not k_df.empty:
        Ks_present = sorted(k_df["K"].unique().tolist())
        K_low = Ks_present[0]
        K_high = Ks_present[-1]
        # Also check if K=20 is present; otherwise compare lowest vs highest available
        if 20 in Ks_present:
            K_high = 20
        print(f"\nK-SWEEP SATURATION — coverage_conditional at K={K_low} vs K={K_high}:")
        if K_high < 20:
            print(f"  (K=20 not present in k_sweep.json; K only swept over {Ks_present}.)")
        for ds in DATASETS:
            sub = k_df[k_df["dataset"] == ds]
            if sub.empty:
                continue
            print(f"\n  {PRETTY_DATASET[ds]}:")
            print(f"    {'method':<18} {f'K={K_low} cov':<22} {f'K={K_high} cov':<22} "
                  f"{f'K={K_low} size':<22} {f'K={K_high} size':<22}")
            for method in METHOD_ORDER:
                ms = sub[sub["method"] == method]
                if ms.empty:
                    continue
                k_lo_row = ms[ms["K"] == K_low]
                k_hi_row = ms[ms["K"] == K_high]

                def fmt_row(df_):
                    if df_.empty:
                        return "--", "--"
                    r = df_.iloc[0]
                    return (
                        f"{r['coverage_conditional_mean']:.3f}±{r['coverage_conditional_std']:.3f}",
                        f"{r['set_size_mean']:.3f}±{r['set_size_std']:.3f}",
                    )
                cov_lo, sz_lo = fmt_row(k_lo_row)
                cov_hi, sz_hi = fmt_row(k_hi_row)
                print(f"    {PRETTY_METHOD.get(method, method):<18} {cov_lo:<22} {cov_hi:<22} "
                      f"{sz_lo:<22} {sz_hi:<22}")

    # Stress test
    if "triviaqa" in stress:
        print("\nSTRESS TEST (TriviaQA, 100-fold) @ alpha=0.1:")
        print(f"  {'Method':<18} {'cov_cond mean±std':<24} {'pass_rate>=0.9':<14} {'n_folds':<8}")
        for method in METHOD_ORDER:
            s = stress["triviaqa"].get(method)
            if s is None:
                continue
            print(f"  {PRETTY_METHOD.get(method, method):<18} "
                  f"{s['cov_cond_mean']:.4f} ± {s['cov_cond_std']:.4f}     "
                  f"{s['pass_rate_at_1minus_alpha']:.3f}         {s['n_folds']}")

    print("\n" + "=" * 72)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    print(f"[aggregate_stats] reading from: {RESULTS_DIR}")
    print(f"[aggregate_stats] writing to:   {OUT_DIR}")

    records = load_summaries()
    if not records:
        print("ERROR: no summary records loaded.", file=sys.stderr)
        return 1
    print(f"[aggregate_stats] loaded {len(records)} summary records")

    aggregated = aggregate_summaries(records)
    print(f"[aggregate_stats] aggregated into {len(aggregated)} (dataset, method, alpha) groups")

    # Outputs
    json_out = OUT_DIR / "aggregated_results.json"
    with json_out.open("w") as f:
        json.dump(aggregated, f, indent=2, default=float)
    print(f"  wrote {json_out}")

    tex_out = OUT_DIR / "aggregated_table.tex"
    write_latex_table(aggregated, tex_out)
    print(f"  wrote {tex_out}")

    md_out = OUT_DIR / "aggregated_table.md"
    write_markdown_table(aggregated, md_out)
    print(f"  wrote {md_out}")

    # K-sweep
    k_df = aggregate_k_sweep()
    csv_out = OUT_DIR / "k_sweep_aggregated.csv"
    k_df.to_csv(csv_out, index=False)
    print(f"  wrote {csv_out}  ({len(k_df)} rows)")

    # Stress
    stress = aggregate_stress(alpha=0.1)
    stress_out = OUT_DIR / "stress_aggregated.json"
    with stress_out.open("w") as f:
        json.dump(stress, f, indent=2, default=float)
    print(f"  wrote {stress_out}")

    # Final summary
    print_final_summary(aggregated, k_df, stress)

    print("\nOutput files:")
    for p in [json_out, tex_out, md_out, csv_out, stress_out]:
        print(f"  {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
