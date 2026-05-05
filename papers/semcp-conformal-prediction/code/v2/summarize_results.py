"""Print a quick text summary of v2 results once experiments finish.
Useful for reading results directly without running figure regeneration.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
import statistics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results_dir", required=True)
    ap.add_argument("--alpha", type=float, default=0.10)
    args = ap.parse_args()

    rd = Path(args.results_dir)
    print(f"\n{'=' * 70}\nSemCP v2 — Results Summary (α = {args.alpha})\n{'=' * 70}")
    if not rd.exists():
        print(f"Results dir {rd} not found.")
        return

    for ds_dir in sorted(rd.iterdir()):
        if not ds_dir.is_dir():
            continue
        sf = ds_dir / "summaries.json"
        if not sf.exists():
            continue
        rows = json.loads(sf.read_text())
        agg = defaultdict(list)
        for r in rows:
            if r.get("alpha") != args.alpha or "error" in r:
                continue
            agg[r["method"]].append(r)

        print(f"\n--- Dataset: {ds_dir.name} ---")
        print(f"{'Method':<20} {'Cov_marg':>10} {'Cov_cond':>10} {'|C|':>8} {'Abst':>6} {'p_A':>6}")
        for m in ("semcp_v2", "m_semcp", "conu", "safer_tuned",
                  "lofreecp_tuned", "tecp_tuned"):
            if m not in agg:
                continue
            rs = agg[m]
            cov_m = statistics.mean(r["coverage_marginal"] for r in rs)
            cov_c = statistics.mean(r["coverage_conditional"] for r in rs)
            sz = statistics.mean(r["set_size_active"] for r in rs)
            abst = statistics.mean(r["abstain_rate"] for r in rs)
            p_a = statistics.mean(r["admissible_rate"] for r in rs)
            print(f"{m:<20} {cov_m:>10.3f} {cov_c:>10.3f} {sz:>8.2f} {abst:>6.3f} {p_a:>6.3f}")
    print(f"\n{'=' * 70}\n")


if __name__ == "__main__":
    main()
