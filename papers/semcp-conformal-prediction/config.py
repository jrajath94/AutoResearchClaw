from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Config:
    """Hyperparameters and condition registry for SemCP conformal prediction experiments."""

    # ── Dataset ──────────────────────────────────────────────────
    primary_dataset: str = "trivia_qa"
    secondary_dataset: str = "squad"
    max_samples: int = 1500
    num_candidates: int = 20           # K: responses generated per question
    max_response_length: int = 64      # max new tokens per generated response
    semantic_match_threshold: float = 0.7  # cosine sim threshold for "match"

    # ── Data split ratios ────────────────────────────────────────
    train_ratio: float = 0.34          # for training KernelScorer
    cal_ratio: float = 0.33            # for conformal calibration
    test_ratio: float = 0.33           # for evaluation

    # ── Pre-trained models (frozen, used for data prep) ──────────
    lm_name: str = "gpt2"
    embed_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    embed_dim: int = 384               # D: MiniLM-L6-v2 output dimension

    # ── KernelScorer training ────────────────────────────────────
    scorer_proj_dim: int = 128         # D': learned projection dimension
    scorer_lr: float = 0.001
    scorer_epochs: int = 15
    scorer_batch_size: int = 64
    triplet_margin: float = 0.3

    # ── Conformal prediction ─────────────────────────────────────
    alpha: float = 0.1                 # target miscoverage rate (1-α = 90% coverage)
    cluster_sim_threshold: float = 0.85  # cosine sim for semantic clustering (M2O)

    # ── Generation ───────────────────────────────────────────────
    generation_temperature: float = 0.8
    generation_top_p: float = 0.95

    # ── Experiment ───────────────────────────────────────────────
    seeds: List[int] = field(default_factory=lambda: [42, 123, 456])
    device: str = "cuda"
    time_budget_seconds: int = 600     # sandbox hard limit

    # ── Condition registry ───────────────────────────────────────
    conditions: List[Dict[str, str]] = field(default_factory=lambda: [
        {"name": "token_cp",           "class_name": "TokenLevelCP"},
        {"name": "naive_semantic_cp",  "class_name": "NaiveSemanticCP"},
        {"name": "semcp_proposed",     "class_name": "SemCP"},
        {"name": "semcp_variant",      "class_name": "SemCPVariant"},
        {"name": "semcp_no_m2o",       "class_name": "SemCPNoManyToOne"},
        {"name": "semcp_simplified",   "class_name": "SemCPSimplified"},
    ])

    def __post_init__(self) -> None:
        """Validate configuration invariants after initialization."""
        # Split ratios must sum to ~1.0
        total_ratio = self.train_ratio + self.cal_ratio + self.test_ratio
        if abs(total_ratio - 1.0) > 0.05:
            raise ValueError(
                f"Split ratios must sum to ~1.0, got {total_ratio:.3f} "
                f"(train={self.train_ratio}, cal={self.cal_ratio}, test={self.test_ratio})"
            )

        # Alpha must be in (0, 1)
        if not (0.0 < self.alpha < 1.0):
            raise ValueError(f"alpha must be in (0, 1), got {self.alpha}")

        # Num candidates must be positive
        if self.num_candidates < 2:
            raise ValueError(
                f"num_candidates must be >= 2 for pairwise scoring, got {self.num_candidates}"
            )

        # Cluster threshold must be in (0, 1)
        if not (0.0 < self.cluster_sim_threshold <= 1.0):
            raise ValueError(
                f"cluster_sim_threshold must be in (0, 1], got {self.cluster_sim_threshold}"
            )

        # Validate each condition entry has required keys
        required_keys = {"name", "class_name"}
        for i, cond in enumerate(self.conditions):
            missing = required_keys - set(cond.keys())
            if missing:
                raise ValueError(
                    f"Condition {i} missing required keys: {missing}. Got: {cond}"
                )

        # Ensure unique condition names
        names = [c["name"] for c in self.conditions]
        if len(names) != len(set(names)):
            raise ValueError(f"Duplicate condition names found in: {names}")

        # Ensure seeds are unique
        if len(self.seeds) != len(set(self.seeds)):
            raise ValueError(f"Duplicate seeds found in: {self.seeds}")

    @property
    def target_coverage(self) -> float:
        """Target coverage probability = 1 - alpha."""
        return 1.0 - self.alpha

    @property
    def n_conditions(self) -> int:
        """Number of registered experimental conditions."""
        return len(self.conditions)

    @property
    def n_seeds(self) -> int:
        """Number of random seeds for per-seed reporting."""
        return len(self.seeds)

    @property
    def condition_names(self) -> List[str]:
        """Ordered list of condition names for consistent reporting."""
        return [c["name"] for c in self.conditions]

    @property
    def condition_class_names(self) -> List[str]:
        """Ordered list of condition class names for registry lookup."""
        return [c["class_name"] for c in self.conditions]

    def get_dataset_names(self) -> List[str]:
        """Return list of dataset names to iterate over."""
        return [self.primary_dataset, self.secondary_dataset]

    def estimated_total_runs(self) -> int:
        """Total number of (dataset × condition × seed) runs for time estimation."""
        n_datasets = len(self.get_dataset_names())
        return n_datasets * self.n_conditions * self.n_seeds

    def time_per_run_budget(self) -> float:
        """Approximate seconds available per individual run, reserving 20% for overhead."""
        usable = self.time_budget_seconds * 0.80
        total_runs = self.estimated_total_runs()
        return usable / max(total_runs, 1)
