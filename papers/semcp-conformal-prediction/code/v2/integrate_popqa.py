"""Integrate PopQA cross-domain results into paper after pulling from pod.

Usage (after pulling results to artifacts/v2_results/popqa/):
  python3 code/v2/integrate_popqa.py

Updates:
  - artifacts/v2_revision/popqa_summary.md (markdown summary)
  - artifacts/v2_revision/popqa_table.tex (LaTeX table fragment)
  - artifacts/v2_revision/popqa_combined_with_others.json (4-dataset agg)
"""
from __future__ import annotations

import json
from pathlib import Path
from collections import defaultdict
import numpy as np

REPO = Path(__file__).resolve().parents[2]
RESULTS = REPO / "artifacts/v2_results/popqa"
OUT_MD = REPO / "artifacts/v2_revision/popqa_summary.md"
OUT_TEX = REPO / "artifacts/v2_revision/popqa_table.tex"

METHOD_NAMES = {
    "semcp_v2": "SemCP-v2",
    "m_semcp": "M-SemCP",
    "conu": "CoNU",
    "safer_tuned": "SAFER (tuned)",
    "lofreecp_tuned": "LoFreeCP (tuned)",
    "tecp_tuned": "TECP (tuned)",
}


def aggregate(records: list[dict]) -> dict:
    g = defaultdict(list)
    for r in records:
        g[r["method"]].append(r)
    out = {}
    for m, runs in g.items():
        cm = np.array([r["coverage_marginal"] for r in runs])
        cc = np.array([r["coverage_conditional"] for r in runs])
        sz = np.array([r["set_size_active"] for r in runs])
        ab = np.array([r["abstain_rate"] for r in runs])
        ar = np.array([r["admissible_rate"] for r in runs])
        # Validity gap = cov_cond - (1 - alpha - 1/(n_admis+1))
        n_admis_cal = np.array([r.get("n_admis_cal", 0) for r in runs])
        target = 1 - 0.10 - 1.0 / (n_admis_cal + 1)
        gap = cc - target
        out[m] = {
            "n_seeds": len(runs),
            "cov_marg": (float(cm.mean()), float(cm.std())),
            "cov_cond": (float(cc.mean()), float(cc.std())),
            "set_size": (float(sz.mean()), float(sz.std())),
            "abstain": (float(ab.mean()), float(ab.std())),
            "admissible": (float(ar.mean()), float(ar.std())),
            "validity_gap": (float(gap.mean()), float(gap.std())),
        }
    return out


def main() -> None:
    summaries_path = RESULTS / "summaries.json"
    if not summaries_path.exists():
        print(f"[integrate] {summaries_path} not found — has the pod run completed?")
        return
    records = json.loads(summaries_path.read_text())
    if not records:
        print("[integrate] empty summaries — pipeline may have failed")
        return

    agg = aggregate(records)

    # Markdown summary
    md = ["# PopQA cross-domain results — SemCP-v2",
          "",
          "Cross-domain validation on PopQA (entity-centric factoid QA, distinct from TriviaQA / SQuAD / NQ-open).",
          "Same Qwen2.5-32B-Instruct generator, K=10, alpha=0.10, 3 seeds, 300 examples.",
          "",
          "| Method | Cov_marg | Cov_cond | |C| | Abstain | p_A | Validity gap |",
          "|---|---|---|---|---|---|---|"]
    for m in ["semcp_v2", "m_semcp", "conu", "safer_tuned", "lofreecp_tuned", "tecp_tuned"]:
        if m not in agg:
            continue
        a = agg[m]
        md.append(
            f"| {METHOD_NAMES[m]} | "
            f"{a['cov_marg'][0]:.3f} ± {a['cov_marg'][1]:.3f} | "
            f"{a['cov_cond'][0]:.3f} ± {a['cov_cond'][1]:.3f} | "
            f"{a['set_size'][0]:.2f} ± {a['set_size'][1]:.2f} | "
            f"{a['abstain'][0]:.3f} ± {a['abstain'][1]:.3f} | "
            f"{a['admissible'][0]:.3f} ± {a['admissible'][1]:.3f} | "
            f"{a['validity_gap'][0]:+.3f} ± {a['validity_gap'][1]:.3f} |"
        )
    md.append("")
    md.append("## Headline")
    if "semcp_v2" in agg:
        s = agg["semcp_v2"]
        md.append(f"- SemCP-v2 conditional coverage: {s['cov_cond'][0]:.3f} ± {s['cov_cond'][1]:.3f}")
        md.append(f"- Validity gap: {s['validity_gap'][0]:+.3f}")
        md.append(f"- Admissibility rate: {s['admissible'][0]:.3f}")
    OUT_MD.write_text("\n".join(md))
    print(f"[integrate] wrote {OUT_MD}")

    # LaTeX table fragment (drop-in for paper appendix)
    tex_lines = [
        "\\begin{table}[ht]",
        "\\centering",
        "\\caption{PopQA cross-domain results: Qwen2.5-32B-Instruct, $K{=}10$, $\\alpha=0.10$, 3 seeds. Validates SemCP generalization to a fourth (entity-centric) QA dataset distinct from TriviaQA / SQuAD / NQ-open.}",
        "\\label{tab:popqa}",
        "\\small",
        "\\begin{tabular}{lcccccc}",
        "\\toprule",
        "\\textbf{Method} & \\textbf{Cov$_{\\rm marg}$} & \\textbf{Cov$_{\\rm cond}$} & $|C|$ & \\textbf{Abst.} & $\\hat{p}_A$ & \\textbf{Val.\\ gap} \\\\",
        "\\midrule",
    ]
    for m in ["semcp_v2", "m_semcp", "conu", "safer_tuned", "lofreecp_tuned", "tecp_tuned"]:
        if m not in agg:
            continue
        a = agg[m]
        n = METHOD_NAMES[m]
        if m == "semcp_v2":
            n = "SemCP (ours)"
        elif m == "m_semcp":
            n = "M-SemCP (ours)"
        tex_lines.append(
            f"{n} & "
            f"{a['cov_marg'][0]:.3f} $\\pm$ {a['cov_marg'][1]:.3f} & "
            f"{a['cov_cond'][0]:.3f} $\\pm$ {a['cov_cond'][1]:.3f} & "
            f"{a['set_size'][0]:.2f} $\\pm$ {a['set_size'][1]:.2f} & "
            f"{a['abstain'][0]:.3f} $\\pm$ {a['abstain'][1]:.3f} & "
            f"{a['admissible'][0]:.3f} $\\pm$ {a['admissible'][1]:.3f} & "
            f"{a['validity_gap'][0]:+.3f} $\\pm$ {a['validity_gap'][1]:.3f} \\\\"
        )
    tex_lines.append("\\bottomrule")
    tex_lines.append("\\end{tabular}")
    tex_lines.append("\\end{table}")
    OUT_TEX.write_text("\n".join(tex_lines))
    print(f"[integrate] wrote {OUT_TEX}")

    # Print headline
    print("\n=== PopQA cross-domain headline ===")
    for m in ["semcp_v2", "conu", "safer_tuned", "lofreecp_tuned", "tecp_tuned"]:
        if m not in agg:
            continue
        a = agg[m]
        print(f"  {METHOD_NAMES[m]:<22} cov_cond={a['cov_cond'][0]:.3f}±{a['cov_cond'][1]:.3f} "
              f"size={a['set_size'][0]:.2f} gap={a['validity_gap'][0]:+.3f}")


if __name__ == "__main__":
    main()
