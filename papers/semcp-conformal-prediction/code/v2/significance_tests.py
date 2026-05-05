"""Paired bootstrap significance tests for SemCP-v2 vs baselines.

Loads per-item raw_*.json files (one per method/dataset/seed) and performs
paired bootstrap on (qid-matched) pairs to compute:
  - p-value: Pr(SemCP-v2 conditional coverage > baseline cond. coverage)
  - p-value: Pr(SemCP-v2 set size <= baseline set size at matched coverage)
  - 95% CI of paired metric differences

Output: artifacts/v2_revision/significance_tests.{json,md}
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
RESULTS = REPO / "artifacts/v2_results"
OUT_JSON = REPO / "artifacts/v2_revision/significance_tests.json"
OUT_MD = REPO / "artifacts/v2_revision/significance_tests.md"

DATASETS = ["triviaqa", "squad", "nq_open"]
METHODS = ["semcp_v2", "m_semcp", "conu", "safer_tuned", "lofreecp_tuned", "tecp_tuned"]
ANCHOR = "semcp_v2"
N_BOOT = 5000


def load_per_item(dataset: str, method: str, seed: int) -> list[dict]:
    p = RESULTS / dataset / f"raw_{method}_a0.1_s{seed}.json"
    if not p.exists():
        return []
    return json.loads(p.read_text())


def paired_metrics(anchor_items: list[dict], baseline_items: list[dict]) -> dict:
    """Match items by qid, return paired metric differences."""
    a = {it["qid"]: it for it in anchor_items}
    b = {it["qid"]: it for it in baseline_items}
    common = sorted(set(a.keys()) & set(b.keys()))
    n = len(common)
    if n == 0:
        return {}

    # Filter to admissible items only (where Theorem 1 applies)
    admis = [q for q in common if a[q].get("admissible", True)]
    n_admis = len(admis)

    cov_diff = []  # 1 if anchor in_set and baseline not, -1 if opposite, 0 same
    size_diff = []
    for q in admis:
        ai, bi = a[q], b[q]
        # Indicator for "correct in set" = conditional coverage on admissible item
        ac = int(ai.get("correct_in_set", False))
        bc = int(bi.get("correct_in_set", False))
        cov_diff.append(ac - bc)
        size_diff.append(ai.get("set_size", 0) - bi.get("set_size", 0))
    return {
        "n_paired_admis": n_admis,
        "cov_diff": cov_diff,
        "size_diff": size_diff,
    }


def bootstrap_pvalue(diffs: list[float], n_boot: int = N_BOOT,
                     rng: np.random.Generator | None = None) -> dict:
    """Paired bootstrap. Tests whether mean(diffs) > 0 (anchor better)."""
    rng = rng or np.random.default_rng(2026)
    arr = np.array(diffs, dtype=float)
    n = len(arr)
    if n == 0:
        return {"mean": 0.0, "ci_lo": 0.0, "ci_hi": 0.0, "p_anchor_better": 0.5}
    boot_means = np.array([
        arr[rng.integers(0, n, size=n)].mean() for _ in range(n_boot)
    ])
    return {
        "mean": float(arr.mean()),
        "std": float(arr.std()),
        "ci_lo": float(np.percentile(boot_means, 2.5)),
        "ci_hi": float(np.percentile(boot_means, 97.5)),
        "p_anchor_better": float((boot_means > 0).mean()),
        "p_anchor_worse": float((boot_means < 0).mean()),
    }


def main() -> None:
    rng = np.random.default_rng(2026)
    output: dict = {"anchor": ANCHOR, "n_boot": N_BOOT, "results": {}}

    for ds in DATASETS:
        ds_results = {}
        for baseline in METHODS:
            if baseline == ANCHOR:
                continue
            # Pool per-item differences across all 3 seeds
            all_cov_diff: list[int] = []
            all_size_diff: list[float] = []
            n_pairs_per_seed = []
            for seed in range(3):
                anc = load_per_item(ds, ANCHOR, seed)
                bas = load_per_item(ds, baseline, seed)
                if not anc or not bas:
                    continue
                pm = paired_metrics(anc, bas)
                if pm:
                    all_cov_diff.extend(pm["cov_diff"])
                    all_size_diff.extend(pm["size_diff"])
                    n_pairs_per_seed.append(pm["n_paired_admis"])
            if not all_cov_diff:
                continue
            cov_test = bootstrap_pvalue(all_cov_diff, rng=rng)
            size_test = bootstrap_pvalue([-d for d in all_size_diff], rng=rng)  # smaller is better
            ds_results[baseline] = {
                "n_paired_admis_per_seed": n_pairs_per_seed,
                "cov_diff": cov_test,  # positive = anchor covers more often
                "size_advantage": size_test,  # positive = anchor smaller
            }
        output["results"][ds] = ds_results

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(output, indent=2))
    print(f"[sig] wrote {OUT_JSON}")

    # Markdown summary
    lines = [
        "# Paired bootstrap significance tests: SemCP-v2 vs baselines",
        "",
        f"Anchor: **{ANCHOR}**. Test: paired bootstrap (n_boot={N_BOOT}) on qid-matched admissible items, pooled across 3 seeds.",
        "",
        "**Reading guide:**",
        "- `cov_diff` = anchor's per-item correct-in-set indicator MINUS baseline's. Positive ⇒ anchor covers more often.",
        "- `size_advantage` = baseline's set size MINUS anchor's. Positive ⇒ anchor is *smaller*.",
        "- `p_anchor_better` = bootstrap probability the metric difference is positive.",
        "",
    ]
    for ds in DATASETS:
        lines.append(f"## {ds}")
        lines.append("")
        lines.append("| Baseline | N pairs | Δ coverage (mean [95% CI]) | p(SemCP covers more) | Δ -size (smaller is better) | p(SemCP smaller) |")
        lines.append("|---|---|---|---|---|---|")
        for baseline, r in output["results"].get(ds, {}).items():
            cov = r["cov_diff"]
            sz = r["size_advantage"]
            n_total = sum(r["n_paired_admis_per_seed"])
            lines.append(
                f"| {baseline} | {n_total} | "
                f"{cov['mean']:+.3f} [{cov['ci_lo']:+.3f}, {cov['ci_hi']:+.3f}] | "
                f"{cov['p_anchor_better']:.3f} | "
                f"{sz['mean']:+.2f} [{sz['ci_lo']:+.2f}, {sz['ci_hi']:+.2f}] | "
                f"{sz['p_anchor_better']:.3f} |"
            )
        lines.append("")

    # One-line headline summary per (dataset)
    lines.append("## One-line headlines")
    for ds in DATASETS:
        lines.append(f"### {ds}")
        for baseline, r in output["results"].get(ds, {}).items():
            cp = r["cov_diff"]["p_anchor_better"]
            sp = r["size_advantage"]["p_anchor_better"]
            cov_judgement = (
                "covers more" if cp > 0.95 else
                "covers less" if cp < 0.05 else
                "tied"
            )
            sz_judgement = (
                "smaller" if sp > 0.95 else
                "larger" if sp < 0.05 else
                "tied"
            )
            lines.append(
                f"- vs **{baseline}**: SemCP {cov_judgement} on coverage (p={cp:.3f}), "
                f"{sz_judgement} on set size (p={sp:.3f})."
            )
        lines.append("")

    OUT_MD.write_text("\n".join(lines))
    print(f"[sig] wrote {OUT_MD}")

    # Console headline summary
    print("\n=== Significance test headlines ===")
    for ds in DATASETS:
        print(f"  {ds}:")
        for baseline, r in output["results"].get(ds, {}).items():
            cp = r["cov_diff"]["p_anchor_better"]
            sp = r["size_advantage"]["p_anchor_better"]
            print(f"    vs {baseline:<18}: p(more cov)={cp:.3f}  p(smaller |C|)={sp:.3f}")


if __name__ == "__main__":
    main()
