"""Entry point for SemCP conformal prediction experiments.

Runs ALL conditions across datasets and seeds, prints standardized output.
No CLI arguments — all conditions are iterated internally.
"""
from __future__ import annotations

import math
import time

import numpy as np
import torch

from config import Config
from data import prepare_full_dataset
from models import (
    TokenLevelCP,
    NaiveSemanticCP,
    SemCP,
    SemCPVariant,
    SemCPNoManyToOne,
    SemCPSimplified,
)
from train import run_condition, aggregate_seed_results, format_metric

# Experiment harness — pre-installed in sandbox, graceful fallback locally
try:
    from experiment_harness import ExperimentHarness
    HAS_HARNESS = True
except ImportError:
    HAS_HARNESS = False


# ─────────────────────────────────────────────────────────────
# Condition class registry (NO argparse — iterate all in loop)
# ─────────────────────────────────────────────────────────────

CONDITION_REGISTRY = {
    "TokenLevelCP": TokenLevelCP,
    "NaiveSemanticCP": NaiveSemanticCP,
    "SemCP": SemCP,
    "SemCPVariant": SemCPVariant,
    "SemCPNoManyToOne": SemCPNoManyToOne,
    "SemCPSimplified": SemCPSimplified,
}


def main() -> None:
    config = Config()
    device = config.device if torch.cuda.is_available() else "cpu"
    time_budget = config.time_budget_seconds

    # Initialize experiment harness if available
    harness = None
    if HAS_HARNESS:
        harness = ExperimentHarness(time_budget=time_budget)

    # ── 1. Print metric definitions ──────────────────────────
    print("METRIC_DEF avg_set_size lower_is_better")
    print("METRIC_DEF empirical_coverage higher_is_better")
    print("METRIC_DEF avg_semantic_size lower_is_better")

    # ── 2. Print registered conditions ───────────────────────
    cond_names = [c["name"] for c in config.conditions]
    print(f"REGISTERED_CONDITIONS {','.join(cond_names)}")

    # ── 3. Time budget setup ─────────────────────────────────
    start_time = time.time()
    all_results = {}
    datasets = config.get_dataset_names()

    # ── 4. Pilot run for time estimate ───────────────────────
    # Run one fast condition to estimate total runtime
    pilot_start = time.time()
    pilot_data = prepare_full_dataset(
        Config(max_samples=min(50, config.max_samples)),
        datasets[0],
        device,
    )
    pilot_metrics = run_condition(TokenLevelCP, config, pilot_data, config.seeds[0], device)
    pilot_elapsed = time.time() - pilot_start

    # Estimate: pilot was on 50 samples; full run scales linearly with N
    scale_factor = config.max_samples / min(50, config.max_samples)
    estimated_per_run = pilot_elapsed * scale_factor
    # SemCP/variants take ~3-5x longer than TokenLevelCP due to training
    avg_multiplier = 3.0
    total_runs = config.estimated_total_runs()
    estimated_total = estimated_per_run * avg_multiplier * total_runs
    print(f"TIME_ESTIMATE: {estimated_total:.0f}s "
          f"(pilot={pilot_elapsed:.1f}s, runs={total_runs}, "
          f"budget={time_budget}s)")

    # If estimated time exceeds budget, reduce max_samples
    if estimated_total > time_budget * 0.8:
        reduced = max(100, int(config.max_samples * (time_budget * 0.7) / estimated_total))
        print(f"SCALING: Reducing max_samples from {config.max_samples} to {reduced} "
              f"to fit time budget")
        config = Config(max_samples=reduced)

    # ── 5. Main experiment loop: datasets x conditions x seeds ──
    for dataset_name in datasets:
        print(f"\n{'=' * 60}")
        print(f"DATASET: {dataset_name}")
        print(f"{'=' * 60}")

        # Time guard — skip entire dataset if too little time remains
        elapsed = time.time() - start_time
        if elapsed > time_budget * 0.90:
            print(f"TIME_BUDGET_EXCEEDED: Skipping dataset {dataset_name} "
                  f"(elapsed={elapsed:.0f}s / {time_budget}s)")
            continue

        # Check harness
        if harness is not None and harness.should_stop():
            print(f"HARNESS_STOP: Stopping before dataset {dataset_name}")
            break

        # Prepare full dataset once per dataset (expensive step)
        data_start = time.time()
        full_data = prepare_full_dataset(config, dataset_name, device)
        data_elapsed = time.time() - data_start

        n_total = len(full_data)
        n_with_match = int(full_data.semantic_labels.any(dim=1).sum().item())
        avg_matches = float(full_data.semantic_labels.float().sum(dim=1).mean().item())
        print(f"DATA_STATS total={n_total} with_semantic_match={n_with_match} "
              f"avg_matches_per_q={avg_matches:.1f} "
              f"K={config.num_candidates} D={config.embed_dim} "
              f"prep_time={data_elapsed:.1f}s")

        # ── Iterate over conditions ──────────────────────────
        for cond_info in config.conditions:
            cond_name = cond_info["name"]
            cond_cls_name = cond_info["class_name"]

            # Time budget guard at condition level
            elapsed = time.time() - start_time
            remaining = time_budget - elapsed
            if remaining < time_budget * 0.05:
                print(f"TIME_BUDGET_EXCEEDED: Skipping {cond_name} "
                      f"(elapsed={elapsed:.0f}s / {time_budget}s)")
                continue

            if harness is not None and harness.should_stop():
                print(f"HARNESS_STOP: Stopping before {cond_name}")
                break

            print(f"\n--- Condition: {cond_name} ({cond_cls_name}) ---")
            condition_class = CONDITION_REGISTRY[cond_cls_name]
            seed_results = []

            # ── Iterate over seeds ───────────────────────────
            for seed in config.seeds:
                # Per-seed time check
                if time.time() - start_time > time_budget * 0.9:
                    print(f"TIME_BUDGET_WARNING: Skipping seed={seed} for {cond_name}")
                    break

                if harness is not None and harness.should_stop():
                    print(f"HARNESS_STOP: Stopping at seed={seed}")
                    break

                seed_start = time.time()
                try:
                    metrics = run_condition(
                        condition_class, config, full_data, seed, device
                    )
                except Exception as e:
                    print(f"ERROR: {cond_name} seed={seed} failed: {e}")
                    continue

                seed_elapsed = time.time() - seed_start

                # NaN/Inf check on all numeric metrics
                has_bad_value = False
                for mk, mv in metrics.items():
                    if isinstance(mv, float) and (math.isnan(mv) or math.isinf(mv)):
                        if mk not in ("threshold",):  # threshold=inf is valid (no matches)
                            has_bad_value = True
                            print(f"SKIP: NaN/Inf detected in {mk}={mv} "
                                  f"for {cond_name} seed={seed}")

                if has_bad_value:
                    continue

                # Report to harness if available
                if harness is not None:
                    for metric_name in ("coverage", "avg_set_size", "avg_semantic_size"):
                        val = metrics.get(metric_name, 0.0)
                        if harness.check_value(val, metric_name):
                            harness.report_metric(metric_name, val)

                # Per-seed output
                print(
                    f"RESULT seed={seed} dataset={dataset_name} "
                    f"condition={cond_name} "
                    f"avg_set_size={metrics['avg_set_size']:.4f} "
                    f"empirical_coverage={metrics['coverage']:.4f} "
                    f"avg_semantic_size={metrics['avg_semantic_size']:.4f} "
                    f"threshold={metrics['threshold']:.4f} "
                    f"coverage_valid={metrics['coverage_valid']} "
                    f"time={seed_elapsed:.1f}s"
                )

                seed_results.append(metrics)

            # ── Aggregate across seeds ───────────────────────
            if seed_results:
                agg = aggregate_seed_results(seed_results)

                size_str = format_metric(
                    agg["avg_set_size_mean"], agg["avg_set_size_std"]
                )
                cov_str = format_metric(
                    agg["coverage_mean"], agg["coverage_std"]
                )
                sem_str = format_metric(
                    agg["avg_semantic_size_mean"], agg["avg_semantic_size_std"]
                )

                print(
                    f"AGGREGATE dataset={dataset_name} condition={cond_name} "
                    f"avg_set_size={size_str} "
                    f"coverage={cov_str} "
                    f"semantic_size={sem_str} "
                    f"validity_rate={agg['validity_rate']:.2f} "
                    f"n_seeds={len(seed_results)}"
                )

                all_results[(dataset_name, cond_name)] = agg

    # ── 6. Print summary table ───────────────────────────────
    total_time = time.time() - start_time
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")

    header = (
        f"{'Condition':<25} {'Dataset':<15} "
        f"{'Set Size':>15} {'Coverage':>15} {'Sem Size':>15} {'Valid':>6}"
    )
    print(header)
    print("-" * len(header))

    for (ds, cond), agg in sorted(all_results.items()):
        sz = format_metric(agg["avg_set_size_mean"], agg["avg_set_size_std"])
        cov = format_metric(agg["coverage_mean"], agg["coverage_std"])
        sem = format_metric(
            agg["avg_semantic_size_mean"], agg["avg_semantic_size_std"]
        )
        vr = f"{agg['validity_rate']:.0%}"
        print(f"{cond:<25} {ds:<15} {sz:>15} {cov:>15} {sem:>15} {vr:>6}")

    print(f"\nTotal runtime: {total_time:.1f}s ({total_time / 3600:.2f}h)")
    print(f"Completed {len(all_results)} condition-dataset combinations")

    # ── 7. Finalize harness ──────────────────────────────────
    if harness is not None:
        harness.finalize()
        print("HARNESS: results.json written")


if __name__ == "__main__":
    main()
