from __future__ import annotations

import math
from typing import List

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from config import Config
from data import ConformalDataset


# ─────────────────────────────────────────────────────────────
# Learnable component: KernelScorer
# ─────────────────────────────────────────────────────────────


class KernelScorer(nn.Module):
    """Learns an embedding projection and RBF kernel bandwidth for
    semantic similarity scoring.

    Input:  emb_a [B, D], emb_b [B, D]   where D = embed_dim (384)
    Output: nonconformity scores [B]       in [0, 1)
    """

    def __init__(self, embed_dim: int, proj_dim: int = 128) -> None:
        super().__init__()
        self.projector = nn.Sequential(
            nn.Linear(embed_dim, proj_dim),   # [*, D] -> [*, D']
            nn.ReLU(),
            nn.Linear(proj_dim, proj_dim),    # [*, D'] -> [*, D']
        )
        self.log_bandwidth = nn.Parameter(torch.zeros(1))  # learnable sigma (log-scale)
        self.proj_dim = proj_dim

    def project(self, emb: torch.Tensor) -> torch.Tensor:
        """Project embeddings through the learned MLP.

        Args:
            emb: [..., D] supports arbitrary leading dimensions

        Returns:
            [..., D'] projected embeddings
        """
        return self.projector(emb)

    def kernel_sim(self, emb_a: torch.Tensor, emb_b: torch.Tensor) -> torch.Tensor:
        """Compute RBF kernel similarity in projected space.

        Args:
            emb_a: [B, D]
            emb_b: [B, D]

        Returns:
            [B] kernel similarity values in (0, 1]
        """
        proj_a = self.project(emb_a)                           # [B, D']
        proj_b = self.project(emb_b)                           # [B, D']
        sigma = torch.exp(self.log_bandwidth).clamp(min=1e-4)  # scalar > 0
        dist_sq = ((proj_a - proj_b) ** 2).sum(dim=-1)         # [B]
        return torch.exp(-dist_sq / (2 * sigma ** 2))          # [B]

    def forward(self, emb_a: torch.Tensor, emb_b: torch.Tensor) -> torch.Tensor:
        """Compute nonconformity score = 1 - kernel_sim.

        Args:
            emb_a: [B, D]
            emb_b: [B, D]

        Returns:
            [B] nonconformity scores in [0, 1)
        """
        return 1.0 - self.kernel_sim(emb_a, emb_b)


# ─────────────────────────────────────────────────────────────
# Base conformal predictor (template method pattern)
# ─────────────────────────────────────────────────────────────


class BaseConformalPredictor:
    """Abstract base defining the conformal prediction pipeline.

    Pipeline: fit -> compute_cal_scores -> calibrate -> predict -> run metrics

    Subclasses override specific methods to implement different
    scoring strategies, calibration procedures, or prediction set
    construction rules.
    """

    def __init__(self, config: Config, device: str) -> None:
        self.config = config
        self.device = device
        self.threshold: float | None = None  # populated by calibrate()

    def fit(self, train_data: ConformalDataset, config: Config) -> None:
        """Default no-op. Subclasses with learnable params override."""
        _ = train_data, config

    def compute_nonconformity_scores(self, data: ConformalDataset) -> torch.Tensor:
        """Compute nonconformity scores for all candidates.

        Args:
            data: ConformalDataset

        Returns:
            [N, K] tensor of scores (higher = more nonconforming)
        """
        raise NotImplementedError(
            "Each condition must define its own scoring strategy"
        )

    def compute_cal_scores(self, cal_data: ConformalDataset) -> torch.Tensor:
        """Extract per-example calibration scores.

        For each calibration example, returns the minimum nonconformity score
        among all semantically-matched candidates. Returns inf if no candidates
        match the reference.

        Args:
            cal_data: calibration split

        Returns:
            [N_cal] tensor of calibration scores
        """
        all_scores = self.compute_nonconformity_scores(cal_data)  # [N_cal, K]
        cal_scores: List[float] = []

        for i in range(len(cal_data)):
            matched = cal_data.semantic_labels[i].to(self.device)  # [K] bool
            if matched.any():
                cal_scores.append(all_scores[i][matched].min().item())
            else:
                cal_scores.append(float("inf"))

        return torch.tensor(cal_scores, dtype=torch.float32)

    def calibrate(self, cal_scores: torch.Tensor, alpha: float) -> float:
        """Compute the conformal quantile threshold.

        Uses the finite-sample valid quantile: ceil((n+1)(1-alpha))/n

        Args:
            cal_scores: [N_cal] calibration scores (may contain inf)
            alpha: target miscoverage rate

        Returns:
            threshold (scalar float)
        """
        finite_mask = cal_scores < float("inf")
        finite = cal_scores[finite_mask]
        n = len(finite)

        if n == 0:
            self.threshold = float("inf")
            return float("inf")

        q_level = min(math.ceil((n + 1) * (1 - alpha)) / n, 1.0)
        threshold = torch.quantile(finite, q_level).item()
        self.threshold = threshold
        return threshold

    def construct_prediction_set(
        self,
        scores: torch.Tensor,
        data: ConformalDataset,
        threshold: float,
    ) -> torch.Tensor:
        """Construct prediction sets by thresholding scores.

        Default: include candidate j if score_j <= threshold.

        Args:
            scores: [N, K] nonconformity scores
            data: ConformalDataset (unused in base, used by overrides)
            threshold: calibrated threshold

        Returns:
            [N, K] bool tensor
        """
        return scores <= threshold

    def run_metrics(
        self,
        cal_data: ConformalDataset,
        test_data: ConformalDataset,
        alpha: float,
    ) -> dict:
        """Full pipeline: calibrate on cal_data, predict on test_data.

        Returns dict with coverage, avg_set_size, avg_semantic_size, threshold.
        """
        # 1. Calibration
        cal_scores = self.compute_cal_scores(cal_data)
        threshold = self.calibrate(cal_scores, alpha)

        # 2. Test scoring and prediction
        test_scores = self.compute_nonconformity_scores(test_data)
        pred_sets = self.construct_prediction_set(
            test_scores, test_data, threshold
        )

        # 3. Empirical coverage
        labels_on_device = test_data.semantic_labels.to(pred_sets.device)
        covered = (pred_sets & labels_on_device).any(dim=1)
        coverage = covered.float().mean().item()

        # 4. Average raw set size
        avg_set_size = pred_sets.float().sum(dim=1).mean().item()

        # 5. Semantic set size
        sem_sizes: List[int] = []
        for i in range(len(test_data)):
            if pred_sets[i].any():
                included_embs = test_data.embeddings[i][pred_sets[i].cpu()]
                cids = self._cluster_by_semantics(
                    included_embs.to(self.device),
                    self.config.cluster_sim_threshold,
                )
                sem_sizes.append(int(cids.max().item()) + 1)
            else:
                sem_sizes.append(0)
        avg_semantic_size = float(np.mean(sem_sizes))

        return {
            "coverage": coverage,
            "avg_set_size": avg_set_size,
            "avg_semantic_size": avg_semantic_size,
            "threshold": threshold,
            "n_cal": len(cal_data),
            "n_test": len(test_data),
        }

    # Alias so callers using the blueprint name also work
    def evaluate(
        self,
        cal_data: ConformalDataset,
        test_data: ConformalDataset,
        alpha: float,
    ) -> dict:
        """Alias for run_metrics (blueprint compatibility)."""
        return self.run_metrics(cal_data, test_data, alpha)

    def _cluster_by_semantics(
        self, embeddings: torch.Tensor, threshold: float
    ) -> torch.Tensor:
        """Greedy single-pass clustering by cosine similarity.

        Args:
            embeddings: [M, D] embeddings to cluster
            threshold: cosine similarity threshold for same-cluster

        Returns:
            [M] tensor of cluster IDs (0-indexed)
        """
        M = embeddings.shape[0]
        if M == 0:
            return torch.tensor([], dtype=torch.long)

        normed = F.normalize(embeddings, dim=-1)
        sim = normed @ normed.T

        cluster_ids = torch.full(
            (M,), -1, dtype=torch.long, device=embeddings.device
        )
        next_id = 0

        for i in range(M):
            if cluster_ids[i] >= 0:
                continue
            cluster_ids[i] = next_id
            for j in range(i + 1, M):
                if cluster_ids[j] < 0 and sim[i, j].item() > threshold:
                    cluster_ids[j] = next_id
            next_id += 1

        return cluster_ids


# ─────────────────────────────────────────────────────────────
# CONDITION 1: Token-level baseline
# ─────────────────────────────────────────────────────────────


class TokenLevelCP(BaseConformalPredictor):
    """Baseline 1: Conformal prediction using sequence-level log-probability.

    Operates entirely in token probability space. The nonconformity score
    is the negated, temperature-scaled average log-probability of the
    generated response. No semantic embeddings are used for scoring.
    """

    def __init__(self, config: Config, device: str) -> None:
        super().__init__(config, device)
        self.temperature: float = 1.0
        self.best_temperatures: dict = {}

    def fit(self, train_data: ConformalDataset, config: Config) -> None:
        """Optimize temperature via grid search on training data.

        Finds temperature that minimizes |empirical_coverage - (1-alpha)|.
        """
        raw_scores = -train_data.log_probs.to(self.device)  # [N_train, K]
        labels = train_data.semantic_labels.to(self.device)  # [N_train, K]

        best_temp = 1.0
        best_err = float("inf")

        for temp in [0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 3.0]:
            scaled = raw_scores / temp

            # Build quick calibration scores
            quick_cal: List[float] = []
            for i in range(len(train_data)):
                mask = labels[i]
                if mask.any():
                    quick_cal.append(scaled[i][mask].min().item())

            if len(quick_cal) < 10:
                continue

            cal_t = torch.tensor(quick_cal)
            n = len(cal_t)
            q = min(math.ceil((n + 1) * (1 - config.alpha)) / n, 1.0)
            thr = torch.quantile(cal_t, q).item()

            # Estimate coverage on same data (heuristic proxy)
            covered = 0
            for i in range(len(train_data)):
                mask = labels[i]
                if mask.any() and scaled[i][mask].min().item() <= thr:
                    covered += 1

            emp_cov = covered / max(len(train_data), 1)
            err = abs(emp_cov - (1 - config.alpha))

            if err < best_err:
                best_err = err
                best_temp = temp

        self.temperature = best_temp

    def compute_nonconformity_scores(
        self, data: ConformalDataset
    ) -> torch.Tensor:
        """Negated, temperature-scaled log-probability.

        Higher score -> less likely -> more nonconforming.

        Returns:
            [N, K] scores
        """
        lp = data.log_probs.to(self.device)
        scores = -lp / self.temperature
        scores = scores.clamp(min=0.0, max=50.0)
        return scores.detach()

    def _compute_coverage_at_temp(
        self,
        scores: torch.Tensor,
        labels: torch.Tensor,
        alpha: float,
        temp: float,
    ) -> float:
        """Internal helper: estimate coverage at a given temperature."""
        scaled = scores / temp
        cal: List[float] = []
        for i in range(scores.shape[0]):
            if labels[i].any():
                cal.append(scaled[i][labels[i]].min().item())

        if len(cal) < 2:
            return 0.0

        cal_t = torch.tensor(cal)
        n = len(cal_t)
        q = min(math.ceil((n + 1) * (1 - alpha)) / n, 1.0)
        thr = torch.quantile(cal_t, q).item()
        covered = sum(1 for s in cal if s <= thr)
        return covered / len(cal)


# ─────────────────────────────────────────────────────────────
# CONDITION 2: Naive semantic baseline
# ─────────────────────────────────────────────────────────────


class NaiveSemanticCP(BaseConformalPredictor):
    """Baseline 2: Cosine distance to trimmed centroid.

    Uses embedding space but with a naive centroid-distance nonconformity
    score. No kernel, no M2O calibration, no learning.
    """

    def __init__(self, config: Config, device: str) -> None:
        super().__init__(config, device)
        self.trim_fraction: float = 0.1

    def compute_nonconformity_scores(
        self, data: ConformalDataset
    ) -> torch.Tensor:
        """1 - cosine_sim(candidate, trimmed_centroid).

        Returns:
            [N, K] scores in [0, ~2]
        """
        embs = data.embeddings.to(self.device)  # [N, K, D]
        N, K, D = embs.shape

        centroids = self._trimmed_centroid(embs)               # [N, D]

        embs_n = F.normalize(embs, dim=-1)                     # [N, K, D]
        cent_n = F.normalize(centroids, dim=-1)                # [N, D]
        sims = (embs_n * cent_n.unsqueeze(1)).sum(dim=-1)      # [N, K]

        scores = (1.0 - sims).clamp(min=0.0)                  # [N, K]
        return scores.detach()

    def _trimmed_centroid(self, embeddings: torch.Tensor) -> torch.Tensor:
        """Compute centroid after removing outlier candidates.

        Args:
            embeddings: [N, K, D]

        Returns:
            [N, D] trimmed centroids
        """
        N, K, D = embeddings.shape

        # Initial centroid
        centroids = embeddings.mean(dim=1)

        # Distance from each candidate to centroid
        dists = torch.norm(
            embeddings - centroids.unsqueeze(1), dim=-1
        )  # [N, K]

        # Trim threshold
        n_trim = max(1, int(K * self.trim_fraction))
        sorted_d, _ = dists.sort(dim=1)
        thresholds = sorted_d[:, K - n_trim]  # [N]

        # Mask inliers
        include = dists <= thresholds.unsqueeze(1)  # [N, K] bool

        # Recompute centroid from inliers
        masked = embeddings * include.unsqueeze(-1).float()
        counts = include.float().sum(dim=1, keepdim=True).clamp(min=1)
        result = masked.sum(dim=1) / counts.squeeze(1).unsqueeze(-1)

        return result

    def _cosine_distance_to_centroid(
        self, embs: torch.Tensor, centroids: torch.Tensor
    ) -> torch.Tensor:
        """Batched cosine distance.

        Args:
            embs: [N, K, D]
            centroids: [N, D]

        Returns:
            [N, K] cosine distances
        """
        e = F.normalize(embs, dim=-1)
        c = F.normalize(centroids, dim=-1).unsqueeze(1)
        return 1.0 - (e * c).sum(dim=-1)


# ─────────────────────────────────────────────────────────────
# CONDITION 3: SemCP proposed (full method)
# ─────────────────────────────────────────────────────────────


class SemCP(BaseConformalPredictor):
    """PROPOSED: Semantic Conformal Prediction.

    RBF kernel density scoring in a learned projected embedding space,
    combined with many-to-one (M2O) calibration that clusters semantically
    equivalent responses.

    Overrides: fit, compute_nonconformity_scores, compute_cal_scores,
    construct_prediction_set.
    """

    def __init__(self, config: Config, device: str) -> None:
        super().__init__(config, device)
        self.scorer = KernelScorer(
            embed_dim=config.embed_dim,
            proj_dim=config.scorer_proj_dim,
        ).to(device)

    def fit(self, train_data: ConformalDataset, config: Config) -> None:
        """Train KernelScorer with triplet margin-ranking loss.

        Learns an embedding projection and kernel bandwidth that make
        matched candidates have lower nonconformity scores than unmatched.
        """
        self.scorer.train()
        optimizer = torch.optim.Adam(
            self.scorer.parameters(), lr=config.scorer_lr
        )

        for epoch in range(config.scorer_epochs):
            epoch_loss = 0.0
            n_batches = 0

            for anchor, pos, neg in train_data.get_triplets(
                config.scorer_batch_size
            ):
                anchor = anchor.to(self.device)
                pos = pos.to(self.device)
                neg = neg.to(self.device)

                # Nonconformity scores: lower = more conforming
                s_pos = self.scorer(anchor, pos)   # [B]
                s_neg = self.scorer(anchor, neg)    # [B]

                # Want s_neg > s_pos + margin
                target = torch.ones(anchor.shape[0], device=self.device)
                loss = F.margin_ranking_loss(
                    s_neg, s_pos, target, margin=config.triplet_margin
                )

                # NaN/divergence guard
                if torch.isnan(loss) or loss.item() > 100:
                    print(
                        f"  [SemCP] WARNING: loss={loss.item():.4f} "
                        f"at epoch {epoch}, skipping batch"
                    )
                    continue

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                epoch_loss += loss.item()
                n_batches += 1

        self.scorer.eval()

    def compute_nonconformity_scores(
        self, data: ConformalDataset
    ) -> torch.Tensor:
        """Kernel density scoring in projected embedding space.

        For each candidate, computes 1 - mean(RBF_kernel_similarity)
        to all other candidates. Outlier responses get high scores.

        Returns:
            [N, K] scores in [0, 1]
        """
        embs = data.embeddings.to(self.device)
        N, K, D = embs.shape
        scores = torch.zeros(N, K, device=self.device)
        sigma = torch.exp(self.scorer.log_bandwidth).clamp(min=1e-4).detach()

        with torch.no_grad():
            proj = self.scorer.project(embs)  # [N, K, D']

            for i in range(N):
                p_i = proj[i]  # [K, D']

                # Pairwise squared Euclidean distance
                diff = p_i.unsqueeze(0) - p_i.unsqueeze(1)  # [K, K, D']
                dist_sq = (diff ** 2).sum(dim=-1)             # [K, K]

                # RBF kernel values
                kernel_vals = torch.exp(
                    -dist_sq / (2 * sigma ** 2)
                )  # [K, K]

                # Mean kernel similarity excluding self
                eye_mask = torch.eye(K, device=self.device, dtype=torch.bool)
                mean_sim = (
                    kernel_vals.masked_fill(eye_mask, 0.0).sum(dim=1) / (K - 1)
                )  # [K]

                scores[i] = 1.0 - mean_sim

        return scores.detach()

    def compute_cal_scores(self, cal_data: ConformalDataset) -> torch.Tensor:
        """Many-to-one calibration via semantic clustering.

        Clusters candidates by semantic similarity and uses cluster-level
        scores (min within cluster containing best match).

        Returns:
            [N_cal] cluster-level calibration scores
        """
        all_scores = self.compute_nonconformity_scores(cal_data)
        cal_scores: List[float] = []

        for i in range(len(cal_data)):
            embs_i = cal_data.embeddings[i].to(self.device)
            scores_i = all_scores[i]
            labels_i = cal_data.semantic_labels[i].to(self.device)

            # 1. Cluster candidates
            cluster_ids = self._cluster_by_semantics(
                embs_i, self.config.cluster_sim_threshold
            )

            # 2. Find matched candidates
            matched_idx = labels_i.nonzero(as_tuple=True)[0]
            if len(matched_idx) == 0:
                cal_scores.append(float("inf"))
                continue

            # 3. Best match = lowest score among matches
            matched_scores = scores_i[matched_idx]
            best_match_pos = matched_idx[matched_scores.argmin()]
            target_cluster = cluster_ids[best_match_pos].item()

            # 4. Cluster score = min within that cluster
            cluster_mask = cluster_ids == target_cluster
            cluster_score = scores_i[cluster_mask].min().item()
            cal_scores.append(cluster_score)

        return torch.tensor(cal_scores, dtype=torch.float32)

    def construct_prediction_set(
        self,
        scores: torch.Tensor,
        data: ConformalDataset,
        threshold: float,
    ) -> torch.Tensor:
        """Select entire semantic clusters, not individual candidates.

        A cluster is included if its min-member score <= threshold.

        Returns:
            [N, K] bool
        """
        N, K = scores.shape
        pred_sets = torch.zeros(N, K, dtype=torch.bool, device=scores.device)

        for i in range(N):
            embs_i = data.embeddings[i].to(self.device)
            cluster_ids = self._cluster_by_semantics(
                embs_i, self.config.cluster_sim_threshold
            )
            n_clusters = cluster_ids.max().item() + 1

            for c in range(n_clusters):
                cmask = cluster_ids == c
                cluster_score = scores[i][cmask].min().item()
                if cluster_score <= threshold:
                    pred_sets[i][cmask] = True

        return pred_sets


# ─────────────────────────────────────────────────────────────
# CONDITION 4: SemCP variant (adaptive bandwidth)
# ─────────────────────────────────────────────────────────────


class SemCPVariant(SemCP):
    """Variant: SemCP with per-candidate adaptive kernel bandwidth.

    Instead of a single learned global bandwidth sigma, each candidate j
    uses sigma_j = median distance to its k nearest neighbors in projected
    space. This captures varying local densities.

    Inherits M2O calibration and cluster-level prediction sets from SemCP.
    Only overrides compute_nonconformity_scores.
    """

    def __init__(self, config: Config, device: str) -> None:
        super().__init__(config, device)
        self.k_neighbors: int = 5

    def compute_nonconformity_scores(
        self, data: ConformalDataset
    ) -> torch.Tensor:
        """Kernel density with per-candidate adaptive bandwidth.

        sigma_j = median of k-NN distances for candidate j.

        Returns:
            [N, K] scores
        """
        embs = data.embeddings.to(self.device)
        N, K, D = embs.shape
        scores = torch.zeros(N, K, device=self.device)
        k_nn = min(self.k_neighbors, K - 1)

        with torch.no_grad():
            proj = self.scorer.project(embs)  # [N, K, D']

            for i in range(N):
                p_i = proj[i]  # [K, D']

                # Pairwise Euclidean distances
                dists = torch.cdist(
                    p_i.unsqueeze(0), p_i.unsqueeze(0)
                ).squeeze(0)  # [K, K]

                # Adaptive bandwidth: median of k-NN distances
                sorted_d, _ = dists.sort(dim=1)
                knn_dists = sorted_d[:, 1 : k_nn + 1]           # [K, k_nn]
                adaptive_bw = knn_dists.median(dim=1).values     # [K]
                adaptive_bw = adaptive_bw.clamp(min=1e-4)

                # Kernel with per-candidate bandwidth
                bw_sq = (adaptive_bw ** 2).unsqueeze(1)          # [K, 1]
                kernel_vals = torch.exp(-dists ** 2 / (2 * bw_sq))  # [K, K]

                # Mean kernel sim excluding self
                eye_mask = torch.eye(K, device=self.device, dtype=torch.bool)
                mean_sim = (
                    kernel_vals.masked_fill(eye_mask, 0.0).sum(dim=1)
                    / (K - 1)
                )

                scores[i] = 1.0 - mean_sim

        return scores.detach()

    def _compute_adaptive_bandwidth(
        self, dists: torch.Tensor, k: int
    ) -> torch.Tensor:
        """Extract per-candidate bandwidth from k-NN distances.

        Args:
            dists: [K, K] pairwise distance matrix
            k: number of nearest neighbors

        Returns:
            [K] bandwidth values
        """
        sorted_d, _ = dists.sort(dim=1)
        knn = sorted_d[:, 1 : k + 1]
        bw = knn.median(dim=1).values.clamp(min=1e-4)
        return bw


# ─────────────────────────────────────────────────────────────
# CONDITION 5: Ablation - no many-to-one
# ─────────────────────────────────────────────────────────────


class SemCPNoManyToOne(SemCP):
    """Ablation: SemCP kernel scoring WITHOUT many-to-one calibration.

    Uses the same learned kernel density scoring as SemCP, but reverts
    calibration and prediction set construction to individual-candidate
    level. No semantic clustering in calibration or prediction.

    Key differences from SemCP:
    - compute_cal_scores: no clustering, uses min-score among all matches
    - construct_prediction_set: individual thresholding, not cluster-level
    """

    def __init__(self, config: Config, device: str) -> None:
        super().__init__(config, device)
        # Same KernelScorer, same training. Only calibration differs.

    def compute_cal_scores(self, cal_data: ConformalDataset) -> torch.Tensor:
        """Standard calibration WITHOUT semantic clustering.

        Min nonconformity among all matched candidates, no cluster grouping.

        Returns:
            [N_cal] individual-level calibration scores
        """
        all_scores = self.compute_nonconformity_scores(cal_data)
        cal_scores: List[float] = []

        for i in range(len(cal_data)):
            matched = cal_data.semantic_labels[i].to(self.device)
            if matched.any():
                cal_scores.append(all_scores[i][matched].min().item())
            else:
                cal_scores.append(float("inf"))

        return torch.tensor(cal_scores, dtype=torch.float32)

    def construct_prediction_set(
        self,
        scores: torch.Tensor,
        data: ConformalDataset,
        threshold: float,
    ) -> torch.Tensor:
        """Select individual candidates, NOT clusters.

        Each candidate j is included independently if score_j <= threshold.

        Returns:
            [N, K] bool
        """
        return scores <= threshold

    def _standard_quantile(
        self, scores: torch.Tensor, alpha: float
    ) -> float:
        """Compute conformal quantile on raw scores (helper).

        Args:
            scores: [N] scores (may contain inf)
            alpha: miscoverage rate

        Returns:
            threshold value
        """
        finite = scores[scores < float("inf")]
        n = len(finite)
        if n == 0:
            return float("inf")
        q_level = min(math.ceil((n + 1) * (1 - alpha)) / n, 1.0)
        return torch.quantile(finite, q_level).item()


# ─────────────────────────────────────────────────────────────
# CONDITION 6: Ablation - simplified scoring
# ─────────────────────────────────────────────────────────────


class SemCPSimplified(SemCP):
    """Ablation: Raw pairwise Euclidean distance instead of kernel.

    Replaces the learned RBF kernel scoring with mean pairwise Euclidean
    distance on raw embeddings (no projection, no bandwidth learning).
    Keeps M2O calibration structure but overrides clustering to use
    Euclidean-distance-based grouping (consistent with the scoring metric).

    This tests the importance of kernel smoothing and learned projections.

    Key differences from SemCP:
    - __init__: no KernelScorer created
    - fit: computes distance normalization stats + Euclidean cluster threshold
    - compute_nonconformity_scores: raw Euclidean distance, not kernel density
    - compute_cal_scores: M2O clustering via Euclidean distance (not cosine)
    - construct_prediction_set: cluster-level selection via Euclidean distance
    - _cluster_by_euclidean: Euclidean-space clustering for M2O consistency
    """

    def __init__(self, config: Config, device: str) -> None:
        # Skip SemCP.__init__ which creates KernelScorer
        BaseConformalPredictor.__init__(self, config, device)
        self.distance_scale: float = 1.0
        self.median_dist: float = 1.0
        # Euclidean distance threshold for clustering, derived from
        # the cosine threshold during fit() to ensure consistency
        self.euclidean_cluster_threshold: float = 1.0

    def fit(self, train_data: ConformalDataset, config: Config) -> None:
        """Compute normalization statistics and Euclidean cluster threshold.

        No learnable parameters. Estimates median pairwise distance
        for score normalization, and converts the cosine similarity
        cluster threshold to an equivalent Euclidean distance threshold
        for consistent M2O clustering.
        """
        embs = train_data.embeddings.to(self.device)  # [N, K, D]
        N, K, D = embs.shape

        # Sample random pairs to estimate median distance
        flat = embs.reshape(-1, D)
        n_flat = len(flat)
        n_pairs = min(2000, n_flat * (n_flat - 1) // 2)

        idx_a = torch.randint(0, n_flat, (n_pairs,), device=self.device)
        idx_b = torch.randint(0, n_flat, (n_pairs,), device=self.device)

        with torch.no_grad():
            dists = torch.norm(flat[idx_a] - flat[idx_b], dim=-1)

        self.median_dist = dists.median().item()
        self.distance_scale = 1.0 / max(self.median_dist, 1e-6)

        # Convert cosine sim threshold to Euclidean distance threshold.
        # For unit vectors: ||a-b||^2 = 2(1 - cos(a,b))
        # So cos_sim >= T  <=>  ||a-b|| <= sqrt(2(1-T))
        # For non-unit vectors, we use normalized embeddings in clustering,
        # so this relationship holds exactly.
        cos_threshold = config.cluster_sim_threshold
        self.euclidean_cluster_threshold = float(
            (2.0 * (1.0 - cos_threshold)) ** 0.5
        )

    def compute_nonconformity_scores(
        self, data: ConformalDataset
    ) -> torch.Tensor:
        """Mean pairwise Euclidean distance on raw embeddings.

        No kernel, no projection. Higher distance = more of an outlier.

        Returns:
            [N, K] normalized distance scores
        """
        embs = data.embeddings.to(self.device)
        N, K, D = embs.shape
        scores = torch.zeros(N, K, device=self.device)

        with torch.no_grad():
            for i in range(N):
                e_i = embs[i]  # [K, D]

                # Pairwise Euclidean distances
                dists = torch.cdist(
                    e_i.unsqueeze(0), e_i.unsqueeze(0)
                ).squeeze(0)  # [K, K]

                # Mean distance excluding self
                eye_mask = torch.eye(K, device=self.device, dtype=torch.bool)
                sum_dists = dists.masked_fill(eye_mask, 0.0).sum(dim=1)
                mean_dists = sum_dists / (K - 1)

                # Scale by median distance
                scores[i] = mean_dists * self.distance_scale

        return scores.detach()

    def compute_cal_scores(self, cal_data: ConformalDataset) -> torch.Tensor:
        """M2O calibration using Euclidean-distance-based clustering.

        Overrides SemCP's cosine-based M2O to use Euclidean clustering,
        ensuring the clustering metric is consistent with the scoring metric.

        Returns:
            [N_cal] cluster-level calibration scores
        """
        all_scores = self.compute_nonconformity_scores(cal_data)
        cal_scores: List[float] = []

        for i in range(len(cal_data)):
            embs_i = cal_data.embeddings[i].to(self.device)
            scores_i = all_scores[i]
            labels_i = cal_data.semantic_labels[i].to(self.device)

            # Cluster using Euclidean distance (consistent with scoring)
            cluster_ids = self._cluster_by_euclidean(
                embs_i, self.euclidean_cluster_threshold
            )

            matched_idx = labels_i.nonzero(as_tuple=True)[0]
            if len(matched_idx) == 0:
                cal_scores.append(float("inf"))
                continue

            # Best match = lowest score among matches
            matched_scores = scores_i[matched_idx]
            best_match_pos = matched_idx[matched_scores.argmin()]
            target_cluster = cluster_ids[best_match_pos].item()

            # Cluster score = min within that cluster
            cluster_mask = cluster_ids == target_cluster
            cluster_score = scores_i[cluster_mask].min().item()
            cal_scores.append(cluster_score)

        return torch.tensor(cal_scores, dtype=torch.float32)

    def construct_prediction_set(
        self,
        scores: torch.Tensor,
        data: ConformalDataset,
        threshold: float,
    ) -> torch.Tensor:
        """Select entire Euclidean-distance clusters, not individual candidates.

        Uses Euclidean-based clustering (consistent with scoring metric)
        rather than the cosine-based clustering inherited from SemCP.

        Returns:
            [N, K] bool
        """
        N, K = scores.shape
        pred_sets = torch.zeros(N, K, dtype=torch.bool, device=scores.device)

        for i in range(N):
            embs_i = data.embeddings[i].to(self.device)
            cluster_ids = self._cluster_by_euclidean(
                embs_i, self.euclidean_cluster_threshold
            )
            n_clusters = cluster_ids.max().item() + 1

            for c in range(n_clusters):
                cmask = cluster_ids == c
                cluster_score = scores[i][cmask].min().item()
                if cluster_score <= threshold:
                    pred_sets[i][cmask] = True

        return pred_sets

    def _cluster_by_euclidean(
        self, embeddings: torch.Tensor, dist_threshold: float
    ) -> torch.Tensor:
        """Greedy single-pass clustering by Euclidean distance.

        Groups candidates whose pairwise Euclidean distance is below
        dist_threshold. This is consistent with the Euclidean distance
        scoring used by this ablation.

        Args:
            embeddings: [M, D]
            dist_threshold: max Euclidean distance for same-cluster

        Returns:
            [M] cluster IDs (0-indexed)
        """
        M = embeddings.shape[0]
        if M == 0:
            return torch.tensor([], dtype=torch.long)

        # Pairwise Euclidean distances
        dists = torch.cdist(
            embeddings.unsqueeze(0), embeddings.unsqueeze(0)
        ).squeeze(0)  # [M, M]

        cluster_ids = torch.full(
            (M,), -1, dtype=torch.long, device=embeddings.device
        )
        next_id = 0

        for i in range(M):
            if cluster_ids[i] >= 0:
                continue
            cluster_ids[i] = next_id
            for j in range(i + 1, M):
                if cluster_ids[j] < 0 and dists[i, j].item() < dist_threshold:
                    cluster_ids[j] = next_id
            next_id += 1

        return cluster_ids

    def _pairwise_euclidean(self, embs: torch.Tensor) -> torch.Tensor:
        """Pairwise Euclidean distance matrix.

        Args:
            embs: [K, D]

        Returns:
            [K, K] distance matrix
        """
        return torch.cdist(
            embs.unsqueeze(0), embs.unsqueeze(0)
        ).squeeze(0)
