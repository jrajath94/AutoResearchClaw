"""K-sweep ablation: re-run each method on the existing pool with K' < K samples.

Subsamples the K=10 sample pool down to K' ∈ {3, 5, 7, 10} per question
(without re-generating samples) and re-runs all methods. Shows how
admissibility, coverage, and set size scale with the sample budget.

Cheap re-analysis: takes a few minutes per dataset, no GPU needed.
"""
from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[0]))

from methods.base import CPSamplePool
from methods.conu import ConU
from semcp_v2 import SemCPv2
from baselines_tuned import TunedSAFER, TunedLofreeCP, TunedTECP


METHODS = {
    "semcp_v2": SemCPv2,
    "conu": ConU,
    "safer_tuned": TunedSAFER,
    "lofreecp_tuned": TunedLofreeCP,
    "tecp_tuned": TunedTECP,
}


def load_pools(base):
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


def subsample_pool(pool: CPSamplePool, k_keep: int, seed: int) -> CPSamplePool:
    """Truncate the sample pool to the first k_keep samples (deterministic)."""
    rng = np.random.default_rng(seed)
    K = len(pool.samples)
    if k_keep >= K:
        return deepcopy(pool)
    idx = rng.choice(K, size=k_keep, replace=False)
    idx = sorted(idx)

    samples = [pool.samples[i] for i in idx]
    sample_correct = [pool.sample_correct[i] for i in idx]
    # Re-compute cluster_ids restricted to subset (assume original ids extend)
    old_to_new = {}
    new_ids = []
    for i, c in zip(idx, [pool.cluster_ids[i] for i in idx]):
        if c not in old_to_new:
            old_to_new[c] = len(old_to_new)
        new_ids.append(old_to_new[c])
    n_clusters = len(old_to_new)
    cluster_correct = [False] * n_clusters
    cluster_reps = [""] * n_clusters
    for s_idx, c in enumerate(new_ids):
        if sample_correct[s_idx]:
            cluster_correct[c] = True
        if not cluster_reps[c]:
            cluster_reps[c] = samples[s_idx]
    embeddings = pool.embeddings[idx] if pool.embeddings is not None else None
    extra = dict(pool.extra) if isinstance(pool.extra, dict) else {}
    if "mean_token_nll" in extra:
        extra["mean_token_nll"] = [extra["mean_token_nll"][i] for i in idx]
    return CPSamplePool(
        qid=pool.qid, question=pool.question, samples=samples,
        references=pool.references, sample_correct=sample_correct,
        cluster_ids=new_ids, cluster_correct=cluster_correct,
        cluster_reps=cluster_reps, embeddings=embeddings, extra=extra,
    )


def run(method_name, pools, alpha, seed, cal_frac=0.5):
    cls = METHODS[method_name]
    method = cls()
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(pools))
    n_cal = int(len(idx) * cal_frac)
    cal = [pools[i] for i in idx[:n_cal]]
    test = [pools[i] for i in idx[n_cal:]]
    method.calibrate(cal, alpha)
    correct, sizes, abst, adm = [], [], [], []
    for p in test:
        pred = method.predict(p, alpha)
        correct.append(pred.correct_in_set)
        sizes.append(pred.set_size)
        abst.append(pred.abstained)
        adm.append(any(p.cluster_correct))
    correct = np.array(correct, dtype=bool)
    adm = np.array(adm, dtype=bool)
    return {
        "cov_marg": float(correct.mean()),
        "cov_cond": float(correct[adm].mean()) if adm.sum() else float("nan"),
        "set_size": float(np.mean(sizes)),
        "abstain": float(np.mean(abst)),
        "p_A": float(adm.mean()),
        "n_test": len(test),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool_base", required=True)
    ap.add_argument("--out_json", required=True)
    ap.add_argument("--k_grid", nargs="+", type=int, default=[3, 5, 7, 10])
    ap.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2])
    ap.add_argument("--alpha", type=float, default=0.10)
    args = ap.parse_args()

    pools = load_pools(args.pool_base)
    print(f"[k_sweep] {len(pools)} pools, K grid {args.k_grid}, "
          f"{len(args.seeds)} seeds, {len(METHODS)} methods")

    out = []
    for k in args.k_grid:
        sub = [subsample_pool(p, k, seed=42) for p in pools]
        for m in METHODS:
            for s in args.seeds:
                try:
                    r = run(m, sub, args.alpha, s)
                    r.update({"K": k, "method": m, "seed": s,
                              "alpha": args.alpha})
                    out.append(r)
                    print(f"  K={k} {m:<18} s={s} cov_cond={r['cov_cond']:.3f} "
                          f"sz={r['set_size']:.2f} p_A={r['p_A']:.3f}")
                except Exception as e:
                    print(f"  K={k} {m} s={s} FAIL: {e}")

    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_json).write_text(json.dumps(out, indent=2))
    print(f"[k_sweep] wrote {args.out_json}")


if __name__ == "__main__":
    main()
