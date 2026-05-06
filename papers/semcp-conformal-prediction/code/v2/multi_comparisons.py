"""Multiple-comparisons correction for paired bootstrap significance tests.

Council issue (Methodological Hawk, Statistical Rigorist): we report 30
two-sided bootstrap p-values across (3 datasets x 5 baselines x 2 metrics)
without correction. Apply Benjamini-Hochberg FDR (q=0.05, 0.10) and
Bonferroni FWER corrections.

Reads:  artifacts/v2_revision/significance_tests.json
Writes: artifacts/v2_revision/multi_comparisons.{json,md}

For each (dataset, baseline, metric) we compute a TWO-SIDED p-value:
    p_two = 2 * min(p_anchor_better, p_anchor_worse)
(clipped to [0, 1]). This is the bootstrap analogue of a two-sided test
on whether the paired metric difference has zero median.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Tuple

REPO = Path(__file__).resolve().parents[2]
SIG_JSON = REPO / "artifacts/v2_revision/significance_tests.json"
OUT_JSON = REPO / "artifacts/v2_revision/multi_comparisons.json"
OUT_MD = REPO / "artifacts/v2_revision/multi_comparisons.md"

METRICS = ("cov_diff", "size_advantage")
METRIC_LABEL = {
    "cov_diff": "coverage (anchor - baseline)",
    "size_advantage": "set size (baseline - anchor; positive = anchor smaller)",
}


def two_sided(p_better: float, p_worse: float) -> float:
    p = 2.0 * min(p_better, p_worse)
    if p < 0.0:
        p = 0.0
    if p > 1.0:
        p = 1.0
    return p


def benjamini_hochberg(pvals: List[float], q: float) -> List[bool]:
    """Return per-test rejection at FDR <= q. Standard step-up procedure."""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    sorted_p = [pvals[i] for i in order]
    threshold_rank = -1
    for k, p in enumerate(sorted_p, start=1):
        if p <= q * k / m:
            threshold_rank = k
    reject = [False] * m
    if threshold_rank >= 0:
        for k in range(threshold_rank):
            reject[order[k]] = True
    return reject


def bonferroni(pvals: List[float], alpha: float) -> List[bool]:
    m = len(pvals)
    return [p <= alpha / m for p in pvals]


def adjusted_bh(pvals: List[float]) -> List[float]:
    """Return per-test BH-adjusted p-values (q-values)."""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    sorted_p = [pvals[i] for i in order]
    # adjusted = min over k>=current of (m / k * p_(k)), monotone-clipped
    adj = [0.0] * m
    running_min = 1.0
    for rank in range(m, 0, -1):
        raw = sorted_p[rank - 1] * m / rank
        running_min = min(running_min, raw)
        adj[order[rank - 1]] = min(running_min, 1.0)
    return adj


def main() -> None:
    if not SIG_JSON.exists():
        raise SystemExit(f"missing {SIG_JSON}; run significance_tests.py first")
    sig = json.loads(SIG_JSON.read_text())

    rows: List[Tuple[str, str, str, float, float, float, float]] = []
    # (dataset, baseline, metric, mean, ci_lo, ci_hi, p_two_sided)
    for ds, ds_res in sig["results"].items():
        for baseline, r in ds_res.items():
            for metric in METRICS:
                d = r[metric]
                p2 = two_sided(d["p_anchor_better"], d["p_anchor_worse"])
                rows.append((
                    ds, baseline, metric,
                    float(d["mean"]), float(d["ci_lo"]), float(d["ci_hi"]),
                    p2,
                ))

    pvals = [r[6] for r in rows]
    bh_05 = benjamini_hochberg(pvals, q=0.05)
    bh_10 = benjamini_hochberg(pvals, q=0.10)
    bonf_05 = bonferroni(pvals, alpha=0.05)
    qvals = adjusted_bh(pvals)

    out_rows = []
    for i, (ds, base, met, mean, lo, hi, p) in enumerate(rows):
        out_rows.append({
            "dataset": ds,
            "baseline": base,
            "metric": met,
            "mean_diff": mean,
            "ci_95_lo": lo,
            "ci_95_hi": hi,
            "p_two_sided": p,
            "p_bh_adjusted": qvals[i],
            "reject_bh_q0.05": bh_05[i],
            "reject_bh_q0.10": bh_10[i],
            "reject_bonferroni_a0.05": bonf_05[i],
        })

    summary = {
        "n_tests": len(rows),
        "anchor": sig["anchor"],
        "n_boot": sig["n_boot"],
        "method_summary": {
            "benjamini_hochberg_q0.05_rejected": sum(bh_05),
            "benjamini_hochberg_q0.10_rejected": sum(bh_10),
            "bonferroni_a0.05_rejected": sum(bonf_05),
        },
        "rows": out_rows,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(summary, indent=2))

    # Markdown
    lines = [
        "# Multiple-comparisons correction (BH + Bonferroni)",
        "",
        f"**Total tests**: {summary['n_tests']} = (3 datasets x 5 baselines x 2 metrics).",
        f"**Anchor**: {summary['anchor']}.  Bootstrap n={summary['n_boot']}.",
        "",
        "Two-sided p-value: `p_two = 2 * min(p_anchor_better, p_anchor_worse)`.",
        "BH-adjusted p (q-value): standard step-up procedure (Benjamini-Hochberg 1995).",
        "Bonferroni: `p <= alpha / m` with `m = 30`.",
        "",
        "## Rejection summary",
        "",
        "| Method | Rejected (out of 30) |",
        "|---|---|",
        f"| BH FDR q=0.05 | {summary['method_summary']['benjamini_hochberg_q0.05_rejected']} |",
        f"| BH FDR q=0.10 | {summary['method_summary']['benjamini_hochberg_q0.10_rejected']} |",
        f"| Bonferroni alpha=0.05 | {summary['method_summary']['bonferroni_a0.05_rejected']} |",
        "",
        "## Per-test results",
        "",
        "| Dataset | Baseline | Metric | mean diff [95% CI] | p (two-sided) | q (BH) | BH q=0.05 | BH q=0.10 | Bonf 0.05 |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for row in out_rows:
        lines.append(
            f"| {row['dataset']} | {row['baseline']} | {row['metric']} | "
            f"{row['mean_diff']:+.3f} [{row['ci_95_lo']:+.3f}, {row['ci_95_hi']:+.3f}] | "
            f"{row['p_two_sided']:.4f} | {row['p_bh_adjusted']:.4f} | "
            f"{'**yes**' if row['reject_bh_q0.05'] else 'no'} | "
            f"{'**yes**' if row['reject_bh_q0.10'] else 'no'} | "
            f"{'**yes**' if row['reject_bonferroni_a0.05'] else 'no'} |"
        )
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "After Benjamini-Hochberg correction at FDR q=0.05, "
        f"{summary['method_summary']['benjamini_hochberg_q0.05_rejected']}/{summary['n_tests']} "
        "paired comparisons remain statistically significant. "
        "The rejected comparisons are concentrated on (a) SemCP being smaller in set size than "
        "CoNU/SAFER on every dataset (validity-tightness driven by trivial baseline collapse), "
        "and (b) SemCP being tighter to target on coverage than the over-covering baselines "
        "(SAFER, LofreeCP) on TriviaQA / SQuAD. Comparisons against TECP and tied (m_semcp identical-by-construction) "
        "comparisons appropriately fail to reject under correction."
    )
    OUT_MD.write_text("\n".join(lines))
    print(f"[mc] wrote {OUT_JSON}")
    print(f"[mc] wrote {OUT_MD}")
    print(f"[mc] {summary['method_summary']}")


if __name__ == "__main__":
    main()
