"""Dataset generation for modular arithmetic and sparse parity.

ModularArithmeticDataset: deterministic combinatorial — enumerates all p^2
    operand pairs, selects a subset by index, computes (a op b) mod p.
    Vocabulary = {0..p-1}, sequence length = 2, num_classes = p.

SparseParityDataset: stochastic binary — generates random binary vectors
    of length n, selects k secret positions, label = XOR of secrets.
    Vocabulary = {0,1}, sequence length = n, num_classes = 2.

The two datasets have fundamentally different data generation logic
(exhaustive enumeration vs random sampling) and different label
computation (modular arithmetic vs parity/XOR).
"""

import itertools
from typing import Tuple

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader

from experiment_config import Config

class ModularArithmeticDataset(Dataset):
    """Deterministic combinatorial dataset: all p^2 operand pairs (a, b).

    Enumerates the full Cartesian product {0..p-1} x {0..p-1}, selects
    a subset by index array, and computes labels via modular arithmetic.
    No randomness in data generation — randomness comes only from the
    index selection in the caller.
    """

    def __init__(self, config: Config, indices: np.ndarray) -> None:
        p = config.prime

        # Exhaustive enumeration of all p^2 pairs in canonical order
        all_pairs = np.array(
            list(itertools.product(range(p), range(p))), dtype=np.int64
        )  # [p^2, 2]

        pairs = all_pairs[indices]  # [N, 2]

        # Modular arithmetic label: (a + b) % p or (a * b) % p
        a_col, b_col = pairs[:, 0], pairs[:, 1]
        labels = (a_col + b_col) % p
        if config.operation != "addition":
            labels = (a_col * b_col) % p

        self.x = torch.tensor(pairs, dtype=torch.long)    # [N, 2]
        self.y = torch.tensor(labels, dtype=torch.long)    # [N]
        self.prime = p
        self.n_total_pairs = p * p

    def __len__(self) -> int:
        return self.x.size(0)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.x[idx], self.y[idx]

    def describe(self) -> str:
        return (f"ModularArithmetic(p={self.prime}, n={len(self)}, "
                f"total_pairs={self.n_total_pairs})")

class SparseParityDataset(Dataset):
    """Stochastic binary dataset: random vectors with XOR parity labels.

    Generates random binary vectors of length n using a seeded RNG,
    selects k secret bit positions (also via RNG), and computes label
    as the parity (XOR) of the secret positions. Each instantiation
    with a different seed produces different secret positions AND
    different input samples.
    """

    def __init__(self, config: Config, num_samples: int, seed: int) -> None:
        rng = np.random.default_rng(seed)
        n = config.sparse_parity_n
        k = config.sparse_parity_k

        # Randomly select k secret positions from n bits
        secret_positions = sorted(
            rng.choice(n, size=k, replace=False).tolist()
        )

        # Random binary matrix — each row is an n-dimensional binary vector
        X = rng.integers(0, 2, size=(num_samples, n))    # [N, n]

        # Parity label: XOR of the k secret bit positions
        Y = X[:, secret_positions].sum(axis=1) % 2       # [N]

        self.x = torch.tensor(X, dtype=torch.long)        # [N, n]
        self.y = torch.tensor(Y, dtype=torch.long)        # [N]
        self.secret_positions = secret_positions
        self.n_bits = n
        self.k_secret = k

    def __len__(self) -> int:
        return self.x.size(0)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.x[idx], self.y[idx]

    def describe(self) -> str:
        return (f"SparseParity(n={self.n_bits}, k={self.k_secret}, "
                f"samples={len(self)}, secrets={self.secret_positions})")

def _build_modular_arithmetic(config: Config, seed: int):
    """Build train/test datasets for modular arithmetic."""
    p = config.prime
    total = p * p
    vocab_size = p
    seq_len = 2
    num_classes = p

    all_idx = np.arange(total)
    rng = np.random.default_rng(seed)
    rng.shuffle(all_idx)

    n_train = int(total * config.train_fraction)
    train_ds = ModularArithmeticDataset(config, all_idx[:n_train])
    test_ds = ModularArithmeticDataset(config, all_idx[n_train:])
    return train_ds, test_ds, vocab_size, seq_len, num_classes

def _build_sparse_parity(config: Config, seed: int):
    """Build train/test datasets for sparse parity."""
    vocab_size = 2
    seq_len = config.sparse_parity_n
    num_classes = 2

    n_total = config.sparse_parity_samples
    n_train = int(n_total * config.train_fraction)

    train_ds = SparseParityDataset(config, n_train, seed)
    test_ds = SparseParityDataset(config, n_total - n_train, seed + 1000)
    return train_ds, test_ds, vocab_size, seq_len, num_classes

def get_dataloaders(
    config: Config,
    seed: int,
) -> Tuple[DataLoader, DataLoader, int, int, int]:
    """Build train / test DataLoaders for the configured task."""

    if config.dataset_name == "modular_arithmetic":
        train_ds, test_ds, vocab_size, seq_len, num_classes = (
            _build_modular_arithmetic(config, seed)
        )
    else:
        train_ds, test_ds, vocab_size, seq_len, num_classes = (
            _build_sparse_parity(config, seed)
        )

    train_loader = DataLoader(
        train_ds,
        batch_size=config.batch_size,
        shuffle=True,
        drop_last=False,
    )
    test_loader = DataLoader(
        test_ds,
        batch_size=config.batch_size,
        shuffle=False,
    )

    return train_loader, test_loader, vocab_size, seq_len, num_classes