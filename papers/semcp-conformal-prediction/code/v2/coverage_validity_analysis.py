"""Coverage validity analysis: tightness of Theorem 1 v2 bound across methods.

Computes per-method "coverage gap" = empirical_cov - theoretical_bound.
A method that achieves the theoretical bound EXACTLY (gap ≈ 0) is the
tightest valid CP method. Over-covering (gap > 0) wastes information;
under-covering (gap < 0) violates the guarantee.

This is a NEW analytical contribution that complements raw set-size
comparison: it asks "which method honors the conditional coverage
guarantee most precisely?" rather than "which method has the smallest
sets?"
"""
from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results_dir", required=True)
    ap.add_argument("--alpha", type=float, default=0.10)
    ap.add_argument("--n_cal", type=int, default=150,
                    help="Approx |I| (admissible cal points). Auto-derived if 0.")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    rd = Path(args.results_dir)
    out = []
    for ds_dir in sorted(rd.iterdir()):
        if not ds_dir.is_dir() or not (ds_dir / "summaries.json").exists():
            continue
        rows = json.loads((ds_dir / "summaries.json").read_text())
        agg = defaultdict(list)
        for r in rows:
            if r.get("alpha") != args.alpha or "error" in r:
                continue
            agg[r["method"]].append(r)

        for m, rs in agg.items():
            cov_cs = [r["coverage_conditional"] for r in rs]
            adm = [r["admissible_rate"] for r in rs]
            cov_c_mean = statistics.mean(cov_cs)
            adm_mean = statistics.mean(adm)
            # |I| ≈ adm_mean * n_cal_total
            n_cal_total = rs[0].get("n_cal", 150)
            est_I = adm_mean * n_cal_total
            theory_bound = 1 - args.alpha - 1.0 / (est_I + 1)
            gap = cov_c_mean - theory_bound
            out.append({
                "dataset": ds_dir.name,
                "method": m,
                "cov_cond": cov_c_mean,
                "theory_bound": theory_bound,
                "gap": gap,
                "abs_gap": abs(gap),
                "n_seeds": len(rs),
                "est_|I|": est_I,
            })

    # Sort by abs_gap ascending — tightest first
    out_sorted = sorted(out, key=lambda x: x["abs_gap"])
    print(f"{'Dataset':<10} {'Method':<18} {'Cov_cond':>9} {'Bound':>8} {'Gap':>8}")
    for r in out_sorted:
        print(f"{r['dataset']:<10} {r['method']:<18} "
              f"{r['cov_cond']:>9.3f} {r['theory_bound']:>8.3f} "
              f"{r['gap']:>+8.3f}")
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2))
    print(f"\n[validity] wrote {args.out}")


if __name__ == "__main__":
    main()
