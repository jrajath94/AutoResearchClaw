"""Entry point for the grokking phase-transition experiment.

Runs all 6 conditions across 3 seeds on modular arithmetic,
reporting per-seed and aggregate metrics.
"""

import math
import random
import time

import numpy as np
import torch

from experiment_config import Config
from data import get_dataloaders
from training import (
    MLPBaseline,
    TransformerBaseline,
    PhaseTransitionProposed,
    CriticalSizeVariant,
    NoAdaptiveRegAblation,
    SimplifiedMetricAblation,
)

try:
    from experiment_harness import ExperimentHarness
except ImportError:
    class ExperimentHarness:
        def __init__(self, time_budget=600):
            self._start = time.time()
            self._budget = time_budget
            self._metrics = {}
        def should_stop(self):
            return (time.time() - self._start) > self._budget * 0.80
        def check_value(self, value, name=""):
            if value is None:
                return False
            if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
                return False
            return True
        def report_metric(self, name, value):
            self._metrics[name] = value
        def finalize(self):
            import json
            with open("results.json", "w") as f:
                json.dump(self._metrics, f, indent=2, default=str)

def set_seed(seed: int) -> None:
    """Set all random seeds for full reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

def _pilot_estimate(config, vocab_size, seq_len, num_classes, device):
    """Time one epoch of MLPBaseline (cheapest) and extrapolate."""
    set_seed(0)
    pilot_cond = MLPBaseline(config, vocab_size, seq_len, num_classes)
    pilot_model = pilot_cond.build_model().to(device)
    pilot_opt = pilot_cond.configure_optimizer(pilot_model)
    train_loader, _, _, _, _ = get_dataloaders(config, 0)

    t0 = time.time()
    pilot_cond.train_epoch(pilot_model, train_loader, pilot_opt, device)
    one_epoch_s = time.time() - t0

    avg_epoch_s = one_epoch_s * 3.0
    estimated_total = 6 * 3 * config.epochs * 0.5 * avg_epoch_s
    return estimated_total, one_epoch_s

def _maybe_scale_config(config: Config, estimated_total: float) -> Config:
    """If estimated runtime exceeds budget, return a scaled-down Config."""
    if estimated_total <= 500:
        return config
    scale = 450.0 / max(estimated_total, 1.0)
    new_epochs = max(200, int(config.epochs * scale))
    new_max_time = min(config.max_time_per_condition, int(80 * scale + 20))
    print(f"SCALING: reducing epochs {config.epochs} -> {new_epochs} to fit budget")
    return Config(
        prime=config.prime,
        operation=config.operation,
        train_fraction=config.train_fraction,
        sparse_parity_n=config.sparse_parity_n,
        sparse_parity_k=config.sparse_parity_k,
        sparse_parity_samples=config.sparse_parity_samples,
        dataset_name=config.dataset_name,
        d_model=config.d_model,
        n_heads=config.n_heads,
        n_layers=config.n_layers,
        dropout=config.dropout,
        mlp_hidden=config.mlp_hidden,
        batch_size=config.batch_size,
        lr=config.lr,
        weight_decay=config.weight_decay,
        epochs=new_epochs,
        max_time_per_condition=new_max_time,
        eval_interval=config.eval_interval,
        superposition_interval=config.superposition_interval,
        superposition_sample_size=config.superposition_sample_size,
        adaptive_reg_lambda=config.adaptive_reg_lambda,
        fixed_reg_lambda=config.fixed_reg_lambda,
        critical_size_constant=config.critical_size_constant,
    )

def main() -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    config = Config()

    harness = ExperimentHarness(time_budget=600)

    print("METRIC_DEF: primary_metric=final_test_accuracy "
          "direction=maximize format=.4f")
    print("METRIC_DEF: secondary_metric=grok_step_ratio "
          "direction=minimize format=.2f")

    dummy_seed = config.seeds[0]
    _, _, vocab_size, seq_len, num_classes = get_dataloaders(config, dummy_seed)

    estimated_total, one_epoch_s = _pilot_estimate(
        config, vocab_size, seq_len, num_classes, device
    )
    print(f"TIME_ESTIMATE: {estimated_total:.0f}s "
          f"(1 MLP epoch={one_epoch_s:.4f}s, device={device})")

    config = _maybe_scale_config(config, estimated_total)

    cond_args = (config, vocab_size, seq_len, num_classes)
    CONDITIONS = [
        MLPBaseline(*cond_args),
        TransformerBaseline(*cond_args),
        PhaseTransitionProposed(*cond_args),
        CriticalSizeVariant(*cond_args),
        NoAdaptiveRegAblation(*cond_args),
        SimplifiedMetricAblation(*cond_args),
    ]

    print(f"REGISTERED_CONDITIONS: {[c.name for c in CONDITIONS]}")
    print(f"CONFIG: epochs={config.epochs}, device={device}, "
          f"prime={config.prime}, d_model={config.d_model}, "
          f"train_fraction={config.train_fraction}")

    TOTAL_BUDGET = 600
    global_start = time.time()
    all_results = {}

    for cond in CONDITIONS:
        elapsed = time.time() - global_start
        if elapsed > TOTAL_BUDGET * 0.90 or harness.should_stop():
            print(f"GLOBAL_TIME_BUDGET: skipping {cond.name} "
                  f"(elapsed={elapsed:.0f}s)")
            continue

        print(f"\n{'=' * 60}")
        print(f"CONDITION: {cond.name}")
        print(f"{'=' * 60}")
        seed_results = []

        for seed in config.seeds:
            elapsed = time.time() - global_start
            if elapsed > TOTAL_BUDGET * 0.90 or harness.should_stop():
                print(f"  TIME_BUDGET: skipping seed {seed} "
                      f"(elapsed={elapsed:.0f}s)")
                break

            print(f"  SEED: {seed}")
            set_seed(seed)
            train_loader, test_loader, _, _, _ = get_dataloaders(config, seed)

            result = cond.run(train_loader, test_loader, seed, device)
            seed_results.append(result)

            acc = result["final_test_acc"]
            grok_ratio = result["grok_step_ratio"]
            grok_step = result["grok_step"]
            total_steps = result["total_steps"]

            if harness.check_value(acc, "final_test_accuracy"):
                harness.report_metric(
                    f"{cond.name}_seed{seed}_final_test_accuracy", acc
                )
            if grok_ratio != float("inf"):
                if harness.check_value(grok_ratio, "grok_step_ratio"):
                    harness.report_metric(
                        f"{cond.name}_seed{seed}_grok_step_ratio", grok_ratio
                    )

            grok_ratio_str = f"{grok_ratio:.2f}" if grok_ratio != float("inf") else "inf"
            grok_step_str = f"{grok_step}" if grok_step != float("inf") else "inf"
            print(f"    final_test_accuracy = {acc:.4f}")
            print(f"    grok_step_ratio     = {grok_ratio_str}")
            print(f"    grok_step           = {grok_step_str}")
            print(f"    total_steps         = {total_steps}")

        if seed_results:
            accs = [r["final_test_acc"] for r in seed_results]
            ratios = [
                r["grok_step_ratio"]
                for r in seed_results
                if r["grok_step_ratio"] != float("inf")
            ]
            mean_acc = float(np.mean(accs))
            std_acc = float(np.std(accs))
            mean_ratio = float(np.mean(ratios)) if ratios else float("inf")

            if harness.check_value(mean_acc, "mean_acc"):
                harness.report_metric(
                    f"{cond.name}_mean_final_test_accuracy", mean_acc
                )
            if mean_ratio != float("inf"):
                if harness.check_value(mean_ratio, "mean_grok_ratio"):
                    harness.report_metric(
                        f"{cond.name}_mean_grok_step_ratio", mean_ratio
                    )

            ratio_str = f"{mean_ratio:.2f}" if mean_ratio != float("inf") else "inf"
            print(f"  AGGREGATE {cond.name}: "
                  f"acc={mean_acc:.4f}\u00b1{std_acc:.4f}  "
                  f"grok_ratio={ratio_str}")

            all_results[cond.name] = {
                "mean_acc": mean_acc,
                "std_acc": std_acc,
                "mean_grok_ratio": mean_ratio,
                "per_seed": seed_results,
            }

    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    print(f"{'Condition':<30} {'Accuracy':>14} {'Grok Ratio':>12}")
    print("-" * 58)
    for name, res in all_results.items():
        acc_str = f"{res['mean_acc']:.4f}\u00b1{res['std_acc']:.4f}"
        ratio_str = (
            f"{res['mean_grok_ratio']:.2f}"
            if res["mean_grok_ratio"] != float("inf")
            else "inf"
        )
        print(f"{name:<30} {acc_str:>14} {ratio_str:>12}")

    if all_results:
        best_name, best_res = max(
            all_results.items(), key=lambda kv: kv[1]["mean_acc"]
        )
        print(f"\nBEST: {best_name} with "
              f"final_test_accuracy={best_res['mean_acc']:.4f}")
        harness.report_metric("best_condition", best_name)
        harness.report_metric("best_final_test_accuracy", best_res["mean_acc"])
    else:
        print("\nNo conditions completed within time budget.")

    total_elapsed = time.time() - global_start
    print(f"\nTOTAL_TIME: {total_elapsed:.1f}s")

    harness.finalize()

if __name__ == "__main__":
    main()