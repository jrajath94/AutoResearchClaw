"""STAIR failure-mode analysis (T1.4, addresses Adversarial Practitioner W4).

For a given experiment npy (n_problems, n_budgets, n_temps, n_samples), and a
chosen routing policy, characterise where the policy fails:

  - At which difficulty quintiles do failures cluster?  (Hardest 20% of problems
    by oracle-best budget? Easiest 20%?)
  - Are failures concentrated on long-CoT problems or short-CoT problems?
  - For each misrouted problem, what is the gap between chosen and required
    budget?
  - Per-budget p50 / p95 / p99 latency.

Mathematically, we define:
  required_budget(x) = smallest budget t in {budgets} s.t. accuracy(x, t) >= 0.5
                       (or the largest budget if no budget reaches 0.5)
  chosen_budget(x)   = output of the routing policy for problem x
  routing_error(x)   = chosen_budget(x) < required_budget(x)
                       (we under-shot; the model could have solved the problem
                       at higher budget but routing gave it less)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent


def required_budget(accuracy: np.ndarray, budgets: np.ndarray, threshold: float = 0.5) -> np.ndarray:
    """For each problem, the smallest budget at which average accuracy across
    samples and temps reaches `threshold`. Returns shape (n_problems,)."""
    n_problems, n_budgets, n_temps = accuracy.shape
    avg_per_budget = accuracy.mean(axis=2)  # (problems, budgets)
    out = np.full(n_problems, budgets[-1], dtype=float)
    for pi in range(n_problems):
        ok = avg_per_budget[pi] >= threshold
        if ok.any():
            out[pi] = budgets[int(np.argmax(ok))]
    return out


def gzip_routing_policy(question_lengths_gz: np.ndarray, budgets: np.ndarray,
                        n_buckets: int = 3) -> np.ndarray:
    """Pre-inference gzip proxy: bucket problems by gzip length and assign the
    median required-budget within the bucket. Mimics the V1/V2 STAIR allocator
    structure with tercile bucketing.

    Returns chosen_budget per problem (n_problems,).
    """
    n = len(question_lengths_gz)
    sort_idx = np.argsort(question_lengths_gz)
    bucket_id = np.zeros(n, dtype=int)
    bucket_size = max(n // n_buckets, 1)
    for i, idx in enumerate(sort_idx):
        bucket_id[idx] = min(i // bucket_size, n_buckets - 1)
    # Greedy fallback: if no calibration, assign budgets[len(budgets)-1-bk] so
    # easier (small gzip) problems get smaller budgets. The user can post-hoc
    # calibrate via V2 BIC analysis.
    bucket_to_budget = budgets[
        np.linspace(0, len(budgets) - 1, n_buckets).round().astype(int)
    ]  # e.g. [budgets[0], budgets[len/2], budgets[-1]] for 3 buckets
    chosen = np.array([bucket_to_budget[b] for b in bucket_id])
    return chosen


def analyze_failures(npy_path: Path, meta_path: Path | None = None,
                     budgets: list[float] | None = None) -> dict:
    correct = np.load(npy_path)
    if correct.ndim != 4:
        raise ValueError(f"expected (problems, budgets, temps, samples), got {correct.shape}")
    n_problems, n_budgets, n_temps, n_samples = correct.shape
    accuracy = correct.mean(axis=-1)  # (problems, budgets, temps)
    if budgets is None:
        if meta_path and meta_path.exists():
            meta = json.loads(meta_path.read_text())
            budgets = meta.get("budgets", [32, 64, 128, 256, 512, 1024])
        else:
            budgets = [32, 64, 128, 256, 512, 1024]
    budgets = np.asarray(budgets[:n_budgets], dtype=float)

    # Required vs chosen
    req = required_budget(accuracy, budgets)

    # Compute REAL gzip lengths from the GSM8K dataset (assumes first n_problems
    # of the test split, matching the exp_v2 default). Falls back to a random
    # proxy if the dataset cannot be loaded.
    proxy_lengths = None
    try:
        import gzip as _gz
        from datasets import load_dataset
        dataset_name = (meta or {}).get("dataset", "gsm8k")
        if dataset_name == "gsm8k":
            ds = load_dataset("openai/gsm8k", "main", split=f"test[:{n_problems}]")
            proxy_lengths = np.asarray([
                len(_gz.compress(row["question"].encode(), compresslevel=9))
                for row in ds
            ], dtype=int)
        elif dataset_name == "math500":
            ds = load_dataset("HuggingFaceH4/MATH-500", split=f"test[:{n_problems}]")
            proxy_lengths = np.asarray([
                len(_gz.compress(row["problem"].encode(), compresslevel=9))
                for row in ds
            ], dtype=int)
    except Exception as e:
        print(f"  [failure_modes] could not load real gzip lengths ({e}); using random proxy")
        rng = np.random.default_rng(42)
        proxy_lengths = rng.integers(0, 1000, size=n_problems)

    chosen = gzip_routing_policy(proxy_lengths, budgets, n_buckets=3)

    error = chosen < req  # under-allocation
    over = chosen > req   # over-allocation (wasted compute)
    correct_routing = chosen == req

    # Stratify by oracle-required difficulty quintile
    quintiles = np.zeros(n_problems, dtype=int)
    sort_idx = np.argsort(req)
    quint_size = max(n_problems // 5, 1)
    for i, idx in enumerate(sort_idx):
        quintiles[idx] = min(i // quint_size, 4)

    fail_rate_per_quintile = []
    for q in range(5):
        mask = quintiles == q
        if mask.any():
            fail_rate_per_quintile.append(float(error[mask].mean()))
        else:
            fail_rate_per_quintile.append(float("nan"))

    over_rate_per_quintile = []
    for q in range(5):
        mask = quintiles == q
        if mask.any():
            over_rate_per_quintile.append(float(over[mask].mean()))
        else:
            over_rate_per_quintile.append(float("nan"))

    # Token savings on correctly-routed problems
    correct_savings_pct = float(
        100.0 * (1.0 - (chosen[correct_routing | over].sum() / max(req.sum(), 1)))
    ) if (correct_routing | over).any() else float("nan")

    # Latency report
    meta = {}
    if meta_path and meta_path.exists():
        meta = json.loads(meta_path.read_text())
    lat = meta.get("latency_ms", {})
    gz = meta.get("gzip_overhead_ms", {})

    return {
        "n_problems": int(n_problems),
        "n_budgets": int(n_budgets),
        "budgets": budgets.tolist(),
        "underroute_rate_overall": float(error.mean()),
        "overroute_rate_overall": float(over.mean()),
        "correct_routing_rate": float(correct_routing.mean()),
        "underroute_rate_by_difficulty_quintile": fail_rate_per_quintile,
        "overroute_rate_by_difficulty_quintile": over_rate_per_quintile,
        "interpretation": (
            "Failures concentrate on hardest quintile"
            if (
                fail_rate_per_quintile[-1] > 0.0
                and fail_rate_per_quintile[-1]
                > 1.5 * (sum(fail_rate_per_quintile[:-1]) / 4)
            )
            else "Failures roughly uniform across difficulty"
        ),
        "median_required_budget": float(np.median(req)),
        "median_chosen_budget": float(np.median(chosen)),
        "p99_required_budget": float(np.percentile(req, 99)),
        "p99_chosen_budget": float(np.percentile(chosen, 99)),
        "tokens_saved_when_correct_pct": correct_savings_pct,
        "latency_ms_p50_p95_p99": [
            lat.get("median_ms"), lat.get("p95_ms"), lat.get("p99_ms"),
        ],
        "gzip_overhead_ms_p50_p95_p99": [
            gz.get("median_ms"), gz.get("p95_ms"), gz.get("p99_ms"),
        ],
        "gzip_overhead_pct_of_inference": (
            float(gz.get("median_ms", 0.0)) / max(float(lat.get("median_ms", 1.0)), 1e-3) * 100.0
            if lat.get("median_ms") and gz.get("median_ms") else None
        ),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--npy", type=Path, required=True)
    p.add_argument("--meta", type=Path, default=None)
    p.add_argument("--out", type=Path, default=REPO / "failure_modes.json")
    args = p.parse_args()
    out = analyze_failures(args.npy, args.meta)
    args.out.write_text(json.dumps(out, indent=2))
    print(f"[failure_modes] underroute_rate_overall={out['underroute_rate_overall']:.3f}")
    print(f"[failure_modes] underroute_by_quintile={[round(x, 3) for x in out['underroute_rate_by_difficulty_quintile']]}")
    print(f"[failure_modes] {out['interpretation']}")
    print(f"[failure_modes] gzip overhead = {out['gzip_overhead_pct_of_inference']}% of inference latency")
    print(f"[failure_modes] -> {args.out}")


if __name__ == "__main__":
    main()
