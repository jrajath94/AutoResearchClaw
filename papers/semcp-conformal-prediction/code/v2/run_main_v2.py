"""Main experiment runner — v2 with the unified method registry,
including SemCPv2 (plug-in sigma), tuned baselines, and M-SemCP.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from pathlib import Path
from typing import Dict, List

import numpy as np

# Make both the v1 utils and v2 modules available
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[0]))

from methods.base import CPSamplePool, CPMethod
from methods.conu import ConU
from methods.safer import SAFER
from methods.lofreecp import LofreeCP
from methods.tecp import TECP
from utils.metrics import coverage_summary
from semcp_v2 import SemCPv2
from m_semcp import MSemCP
from baselines_tuned import TunedSAFER, TunedLofreeCP, TunedTECP


METHOD_REGISTRY = {
    "semcp_v2": SemCPv2,
    "m_semcp": MSemCP,
    "conu": ConU,
    "safer_paper": SAFER,
    "safer_tuned": TunedSAFER,
    "lofreecp_paper": LofreeCP,
    "lofreecp_tuned": TunedLofreeCP,
    "tecp_paper": TECP,
    "tecp_tuned": TunedTECP,
}


def load_pools(base: str) -> List[CPSamplePool]:
    with open(base + ".json") as f:
        meta = json.load(f)
    npz = np.load(base + ".npz")
    pools = []
    for i, m in enumerate(meta):
        emb = npz[f"emb_{i}"]
        pools.append(CPSamplePool(
            qid=m["qid"], question=m["question"], samples=m["samples"],
            references=m["references"], sample_correct=m["sample_correct"],
            cluster_ids=m["cluster_ids"], cluster_correct=m["cluster_correct"],
            cluster_reps=m["cluster_reps"], embeddings=emb,
            extra=m.get("extra", {}),
        ))
    return pools


def split_cal_test(pools: List[CPSamplePool], frac: float, seed: int):
    rng = random.Random(seed)
    idx = list(range(len(pools)))
    rng.shuffle(idx)
    n_cal = int(len(idx) * frac)
    return [pools[i] for i in idx[:n_cal]], [pools[i] for i in idx[n_cal:]]


def run_one(method_name: str, pools, alpha: float, seed: int, cal_frac: float):
    cls = METHOD_REGISTRY[method_name]
    method: CPMethod = cls()
    cal, test = split_cal_test(pools, cal_frac, seed)
    t0 = time.time()
    method.calibrate(cal, alpha)
    t_cal = time.time() - t0

    correct, sizes, abst, adm = [], [], [], []
    raw = []
    t0 = time.time()
    for p in test:
        pred = method.predict(p, alpha)
        correct.append(pred.correct_in_set)
        sizes.append(pred.set_size)
        abst.append(pred.abstained)
        adm.append(any(p.cluster_correct))
        raw.append({"qid": p.qid, "set_size": pred.set_size,
                    "abstained": pred.abstained,
                    "correct_in_set": pred.correct_in_set,
                    "score": pred.score, "admissible": adm[-1]})
    t_predict = time.time() - t0

    summary = coverage_summary(correct, sizes, adm, abst, seed=seed)
    summary.update({
        "method": method_name, "alpha": alpha, "seed": seed,
        "t_calibrate_s": t_cal, "t_predict_s": t_predict,
        "n_test": len(test), "n_cal": len(cal),
        "q_hat": float(getattr(method, "q_hat", float("nan"))),
        "aux_log": getattr(method, "aux_log", {}),
    })
    if hasattr(method, "sigma"):
        summary["sigma"] = float(method.sigma)
    return summary, raw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool_base", required=True)
    ap.add_argument("--output_dir", required=True)
    ap.add_argument("--alphas", nargs="+", type=float, default=[0.10])
    ap.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2])
    ap.add_argument("--methods", nargs="+",
                    default=["semcp_v2", "m_semcp", "conu",
                             "safer_tuned", "lofreecp_tuned", "tecp_tuned"])
    ap.add_argument("--cal_frac", type=float, default=0.5)
    args = ap.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    pools = load_pools(args.pool_base)
    print(f"[run] {len(pools)} pools loaded")

    summaries = []
    for m_name in args.methods:
        if m_name not in METHOD_REGISTRY:
            print(f"[run] WARN unknown method '{m_name}', skipping")
            continue
        for a in args.alphas:
            for s in args.seeds:
                try:
                    summ, raw = run_one(m_name, pools, a, s, args.cal_frac)
                    summaries.append(summ)
                    raw_path = os.path.join(
                        args.output_dir, f"raw_{m_name}_a{a}_s{s}.json"
                    )
                    with open(raw_path, "w") as f:
                        json.dump(raw, f)
                    print(f"  [{m_name} a={a} s={s}] "
                          f"cov_cond={summ['coverage_conditional']:.3f} "
                          f"sz={summ['set_size_active']:.2f} "
                          f"abs={summ['abstain_rate']:.2f} "
                          f"sig={summ.get('sigma','-'):.3f}" if isinstance(summ.get("sigma"), float) else
                          f"  [{m_name} a={a} s={s}] cov={summ['coverage_conditional']:.3f}")
                except Exception as e:
                    print(f"  [{m_name} a={a} s={s}] FAIL: {e}")
                    summaries.append({"method": m_name, "alpha": a, "seed": s,
                                      "error": str(e)})

    out_path = os.path.join(args.output_dir, "summaries.json")
    with open(out_path, "w") as f:
        json.dump(summaries, f, indent=2)
    print(f"[run] wrote {len(summaries)} summaries -> {out_path}")


if __name__ == "__main__":
    main()
