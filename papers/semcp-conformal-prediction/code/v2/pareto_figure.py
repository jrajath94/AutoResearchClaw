"""Pareto plot: tightness of conditional coverage vs effective set size.

x-axis: |Cov_cond - (1 - α)| — distance from nominal target
y-axis: effective set size = (1 - abstain) * |C|

Pareto-optimal methods sit in the lower-left corner: tight valid coverage
AND small effective sets. Methods that over-cover (SAFER) are far right;
methods with small abstain rates and small sets but slightly under-cover
(LofreeCP, TECP) are near the bottom.
"""
from __future__ import annotations

import argparse
import json
import statistics as st
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


PALETTE = {"semcp_v2": "#2E86AB", "m_semcp": "#A23B72",
            "conu": "#E76F51", "safer_tuned": "#F4A261",
            "lofreecp_tuned": "#264653", "tecp_tuned": "#8B5CF6"}
DISPLAY = {"semcp_v2": "SemCP", "m_semcp": "M-SemCP",
            "conu": "ConU", "safer_tuned": "SAFER",
            "lofreecp_tuned": "LofreeCP", "tecp_tuned": "TECP"}
DS_MARKER = {"triviaqa": "o", "squad": "s", "nq_open": "^"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results_dir", required=True)
    ap.add_argument("--alpha", type=float, default=0.10)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    rd = Path(args.results_dir)
    fig, ax = plt.subplots(figsize=(7.5, 5))

    nom = 1 - args.alpha
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
            cov = st.mean(r["coverage_conditional"] for r in rs)
            sz = st.mean(r["set_size_active"] for r in rs)
            abst = st.mean(r["abstain_rate"] for r in rs)
            eff_sz = (1 - abst) * sz
            x = abs(cov - nom)
            ax.scatter(x, eff_sz, color=PALETTE.get(m, "gray"),
                        marker=DS_MARKER.get(ds_dir.name, "o"),
                        s=80, alpha=0.85, edgecolors="black", lw=0.5,
                        label=f"{DISPLAY.get(m, m)}@{ds_dir.name}")

    ax.set_xlabel("Coverage tightness $|{\\rm Cov}_{\\rm cond} - (1-\\alpha)|$ (lower = tighter)")
    ax.set_ylabel("Effective set size $(1 - \\rm{abstain}) \\cdot |C|$")
    ax.set_title("Pareto frontier: coverage tightness vs efficiency")
    ax.axvline(0, ls=":", color="gray", lw=0.7)
    # Build deduplicated legend
    handles, labels = ax.get_legend_handles_labels()
    seen = set()
    uniq_h = []
    uniq_l = []
    for h, l in zip(handles, labels):
        method = l.split("@")[0]
        if method in seen:
            continue
        seen.add(method)
        uniq_h.append(h); uniq_l.append(method)
    ax.legend(uniq_h, uniq_l, loc="upper right", fontsize=9, ncol=2)
    fig.tight_layout()
    fig.savefig(args.out, bbox_inches="tight")
    print(f"[pareto] wrote {args.out}")


if __name__ == "__main__":
    main()
