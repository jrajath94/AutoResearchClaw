"""Central hyperparameter store for the grokking phase-transition experiment.

Renamed from config.py to avoid shadowing the stdlib/pip 'config' package.
"""

from dataclasses import dataclass, field
from typing import List

@dataclass(frozen=True)
class Config:
    """Immutable experiment configuration."""

    # ── Task / dataset ──────────────────────────────────────────────
    prime: int = 23
    operation: str = "addition"
    train_fraction: float = 0.5
    sparse_parity_n: int = 40
    sparse_parity_k: int = 3
    sparse_parity_samples: int = 10000
    dataset_name: str = "modular_arithmetic"

    # ── Model architecture ──────────────────────────────────────────
    d_model: int = 64
    n_heads: int = 2
    n_layers: int = 1
    dropout: float = 0.0
    mlp_hidden: int = 128

    # ── Training ────────────────────────────────────────────────────
    lr: float = 1.0e-3
    weight_decay: float = 1.0
    epochs: int = 2000
    batch_size: int = 256
    eval_interval: int = 20
    superposition_interval: int = 20

    # ── Superposition & phase-transition ────────────────────────────
    superposition_sample_size: int = 264
    adaptive_reg_lambda: float = 0.10
    fixed_reg_lambda: float = 0.10
    critical_size_constant: float = 2.5

    # ── Experiment control ──────────────────────────────────────────
    seeds: List[int] = field(default_factory=lambda: [42, 137, 256])
    max_time_per_condition: int = 80
    device: str = "cuda"