from __future__ import annotations

import random
from typing import Dict, List, Tuple

import numpy as np
import torch

from config import Config
from data import ConformalDataset


def set_seed(seed: int) -> None:
    """Set random seeds across all libraries for reproducibility.

    Configures Python, NumPy, and PyTorch RNGs. Also sets deterministic
    CUDNN mode (slightly slower but reproducible).
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def split_dataset(
    full_data: ConformalDataset,
    config: Config,
    seed: int,
) -> Tuple[ConformalDataset, ConformalDataset, ConformalDataset]:
    """Split dataset into train/cal/test using a seeded permutation.

    Uses a separate RandomState to avoid polluting the global RNG.
    The split preserves exchangeability — critical for conformal
    prediction's coverage guarantee.

    Args:
        full_data: complete ConformalDataset
        config: Config with train_ratio, cal_ratio, test_ratio
        seed: random seed for reproducible splits

    Returns:
        (train_data, cal_data, test_data) tuple of ConformalDataset
    """
    N = len(full_data)
    rng = np.random.RandomState(seed)
    perm = rng.permutation(N)

    n_train = int(N * config.train_ratio)
    n_cal = int(N * config.cal_ratio)
    # Remainder goes to test (handles rounding)

    train_idx = perm[:n_train]
    cal_idx = perm[n_train : n_train + n_cal]
    test_idx = perm[n_train + n_cal :]

    return (
        full_data.subset(train_idx),
        full_data.subset(cal_idx),
        full_data.subset(test_idx),
    )


def run_condition(
    condition_class,
    config: Config,
    full_data: ConformalDataset,
    seed: int,
    device: str,
) -> dict:
    """Run a single condition with a single seed: split -> fit -> calibrate -> test.

    Args:
        condition_class: one of the BaseConformalPredictor subclasses
        config: experiment configuration
        full_data: full pre-computed ConformalDataset
        seed: random seed for this run
        device: torch device string

    Returns:
        dict of metrics including coverage, avg_set_size, avg_semantic_size,
        threshold, and coverage_valid flag
    """
    # 1. Set seed for full reproducibility
    set_seed(seed)

    # 2. Split into train/cal/test
    train_data, cal_data, test_data = split_dataset(full_data, config, seed)

    # 3. Move splits to device
    train_data = train_data.to(device)
    cal_data = cal_data.to(device)
    test_data = test_data.to(device)

    # 4. Instantiate and fit the predictor
    predictor = condition_class(config, device)
    predictor.fit(train_data, config)

    # 5. Run full pipeline: calibrate on cal, predict on test
    metrics = predictor.evaluate(cal_data, test_data, config.alpha)

    # 6. Coverage validity flag (with 0.05 tolerance for finite-sample variation)
    target = 1.0 - config.alpha
    metrics["coverage_valid"] = bool(metrics["coverage"] >= target - 0.05)

    return metrics


def aggregate_seed_results(seed_results: List[dict]) -> dict:
    """Compute mean and std for all numeric metrics across seeds.

    Args:
        seed_results: list of per-seed metric dicts

    Returns:
        dict with {metric}_mean, {metric}_std for each numeric metric,
        plus validity_rate (fraction of seeds with valid coverage)
    """
    if not seed_results:
        return {}

    agg: Dict[str, float] = {}

    # Identify numeric (non-bool) keys from the first result
    numeric_keys = [
        k
        for k in seed_results[0]
        if isinstance(seed_results[0][k], (int, float))
        and not isinstance(seed_results[0][k], bool)
    ]

    for key in numeric_keys:
        vals = [r[key] for r in seed_results]
        agg[f"{key}_mean"] = float(np.mean(vals))
        agg[f"{key}_std"] = float(np.std(vals))

    # Fraction of seeds with valid coverage
    valid = [r.get("coverage_valid", False) for r in seed_results]
    agg["validity_rate"] = sum(1 for v in valid if v) / max(len(valid), 1)

    return agg


def format_metric(mean: float, std: float, decimals: int = 4) -> str:
    """Format a metric as 'mean +/- std' with specified decimal places.

    Args:
        mean: mean value
        std: standard deviation
        decimals: number of decimal places

    Returns:
        Formatted string like '0.9012+/-0.0234'
    """
    return f"{mean:.{decimals}f}\u00b1{std:.{decimals}f}"
