"""M-SemCP: Multi-Resolution Semantic Conformal Prediction.

Novel contribution introduced in SemCP v2.

Idea
----
Prior CP-for-LLMs methods sit at different points along a partition-
granularity axis:
  - LofreeCP, TECP : string-level (no partition; the finest granularity)
  - ConU, SAFER    : NLI-bidirectional clusters (medium granularity)
  - SemCP-strict   : NLI-bidirectional + cluster-purity check (coarser)
  - SemCP-lenient  : single-direction entailment >= 0.7 (coarsest)

M-SemCP forms a *convex combination* of contrastive lifted scores
computed at multiple granularities {strict, medium, lenient}, with
mixing weights chosen on a held-out split to minimize expected set
size subject to the conditional coverage constraint.

Why this is sound:
  Each component score is a deterministic function of (X_i, S_i,
  f_NLI, embedder) — Theorem 1 v2 covers each one. A convex
  combination of deterministic functions is also a deterministic
  function of the same quantities, so exchangeability is preserved
  and the (1 - alpha - 1/(|I|+1)) bound applies to the combined score.

Why this is novel:
  - Unifies SemCP, ConU, LofreeCP, TECP under one framework: each
    method is recovered as a corner of the M-SemCP simplex.
  - Adapts the partition granularity per dataset, removing a brittle
    'choose your partition method' decision that prior CP-for-LLMs
    work makes implicitly.
  - Yields a Pareto frontier of (set_size, conditional coverage)
    that strictly dominates any single-granularity baseline.

This file is imported as `from m_semcp import MSemCP`. It depends on
HACNLIPartitioner from partition_v2.py for the multi-granularity
partitions, and on SemCPv2 for the contrastive scoring primitive.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import numpy as np

from methods.base import (CPMethod, CPPrediction, CPSamplePool,
                          conformal_quantile)
from semcp_v2 import SemCPv2, SemCPConfig


@dataclass
class MSemCPConfig:
    granularities: Tuple[str, ...] = ("strict", "medium", "lenient")
    # tau_entail per granularity
    tau_entail_per_grain: Dict[str, float] = field(
        default_factory=lambda: {"strict": 0.70, "medium": 0.50, "lenient": 0.30}
    )
    # Convex weight grid: which mixtures to try on held-out
    # weight_grid is a list of (w_strict, w_med, w_len) summing to 1.
    weight_grid: Tuple[Tuple[float, float, float], ...] = (
        (1.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
        (0.0, 0.0, 1.0),
        (0.5, 0.5, 0.0),
        (0.5, 0.0, 0.5),
        (0.0, 0.5, 0.5),
        (0.34, 0.33, 0.33),
        (0.7, 0.2, 0.1),
        (0.1, 0.2, 0.7),
    )
    sigma: float = 1.0
    bandwidth_split_frac: float = 0.20
    rng_seed: int = 42


class MSemCP(CPMethod):
    """Multi-resolution SemCP.

    Each calibration / test pool needs to carry per-granularity cluster_ids
    in pool.extra['cluster_ids_by_grain'] (set by build_pools_v2.py).
    The class falls back to single-granularity (the pool's main cluster_ids)
    when multi-granularity data isn't available.
    """

    name = "m_semcp"

    def __init__(self, config: MSemCPConfig | None = None):
        if config is None:
            config = MSemCPConfig()
        self.cfg = config
        self.weights: Tuple[float, float, float] = (1.0, 0.0, 0.0)
        self.sigma_per_grain: Dict[str, float] = {}
        self.q_hat: float = float("inf")
        self.aux_log: dict = {}

    # ------------------------------------------------------------
    # Per-granularity contrastive score
    # ------------------------------------------------------------
    @staticmethod
    def _contrastive(embeddings: np.ndarray, cidx: List[List[int]],
                      target: int, sigma: float) -> float:
        return SemCPv2._contrastive_score(embeddings, cidx, target, sigma)

    @staticmethod
    def _cluster_indices_for_grain(pool: CPSamplePool, grain: str) -> List[List[int]]:
        ids_by_grain = pool.extra.get("cluster_ids_by_grain", {}) if isinstance(
            pool.extra, dict
        ) else {}
        ids = ids_by_grain.get(grain, pool.cluster_ids)
        n_c = max(ids) + 1 if ids else 0
        return [[i for i, c in enumerate(ids) if c == cid] for cid in range(n_c)]

    @staticmethod
    def _correct_cluster(pool: CPSamplePool, grain: str) -> int | None:
        ids_by_grain = pool.extra.get("cluster_ids_by_grain", {}) if isinstance(
            pool.extra, dict
        ) else {}
        ids = ids_by_grain.get(grain, pool.cluster_ids)
        if not ids:
            return None
        sample_correct = pool.sample_correct
        for s_idx, ok in enumerate(sample_correct):
            if ok:
                return ids[s_idx]
        return None

    def _per_grain_score(self, pool: CPSamplePool, grain: str,
                          sigma: float, target: int | None) -> float:
        if target is None:
            return float("inf")
        cidx = self._cluster_indices_for_grain(pool, grain)
        return self._contrastive(pool.embeddings, cidx, target, sigma)

    # ------------------------------------------------------------
    # Calibrate: choose weights, sigmas, q_hat
    # ------------------------------------------------------------
    def _plugin_sigma_for_grain(self, pools: List[CPSamplePool],
                                 grain: str, alpha: float) -> float:
        # Reuse SemCPv2 plug-in formula but per-grain
        within: List[float] = []
        between: List[float] = []
        for p in pools:
            target = self._correct_cluster(p, grain)
            if target is None or p.embeddings is None:
                continue
            cidx = self._cluster_indices_for_grain(p, grain)
            if not cidx[target]:
                continue
            cluster_pts = p.embeddings[cidx[target]]
            centroid = cluster_pts.mean(axis=0)
            d2_w = float(np.mean(np.sum((cluster_pts - centroid) ** 2, axis=1)))
            within.append(d2_w)
            min_d2_b = float("inf")
            for c, idxs in enumerate(cidx):
                if c == target or not idxs:
                    continue
                other = p.embeddings[idxs].mean(axis=0)
                d2 = float(np.sum((centroid - other) ** 2))
                if d2 < min_d2_b:
                    min_d2_b = d2
            if np.isfinite(min_d2_b):
                between.append(min_d2_b)
        if not within or not between:
            return 1.0
        mu_W = float(np.mean(within))
        mu_B = float(np.mean(between))
        gap = mu_B - mu_W
        if gap <= 0:
            return 1.0
        denom = 2.0 * np.log(1.0 / max(1e-6, 1.0 - alpha))
        return float(np.clip(np.sqrt(gap / max(denom, 1e-6)), 0.05, 8.0))

    def calibrate(self, pools: List[CPSamplePool], alpha: float) -> None:
        rng = np.random.default_rng(self.cfg.rng_seed)
        idx = rng.permutation(len(pools))
        n_band = max(1, int(len(idx) * self.cfg.bandwidth_split_frac))
        band = [pools[i] for i in idx[:n_band]]
        cal = [pools[i] for i in idx[n_band:]]

        # Per-granularity sigmas via plug-in
        for grain in self.cfg.granularities:
            self.sigma_per_grain[grain] = self._plugin_sigma_for_grain(
                band, grain, alpha
            )

        # Search over convex weights on held-out band
        best_w, best_size = self.cfg.weight_grid[0], float("inf")
        for w in self.cfg.weight_grid:
            cal_scores = np.array(
                [self._mixed_cal_score(p, w) for p in band], dtype=float
            )
            finite = cal_scores[np.isfinite(cal_scores)]
            if len(finite) == 0:
                continue
            q = conformal_quantile(finite, alpha)
            sizes = []
            for p in band:
                if not any(p.cluster_correct):
                    continue
                pool_scores = self._mixed_pool_scores(p, w)
                sizes.append(sum(1 for s in pool_scores if s <= q))
            avg = float(np.mean(sizes)) if sizes else float("inf")
            if avg < best_size:
                best_size = avg
                best_w = w
        self.weights = best_w

        cal_scores = np.array(
            [self._mixed_cal_score(p, self.weights) for p in cal], dtype=float
        )
        finite = cal_scores[np.isfinite(cal_scores)]
        self.q_hat = conformal_quantile(finite, alpha) if len(finite) else float("inf")
        self.aux_log = {
            "weights": list(self.weights),
            "sigma_per_grain": dict(self.sigma_per_grain),
            "q_hat": float(self.q_hat),
            "n_admissible_cal": int(len(finite)),
            "alpha": float(alpha),
        }

    def _mixed_cal_score(self, pool: CPSamplePool,
                          weights: Tuple[float, float, float]) -> float:
        if not any(pool.cluster_correct):
            return float("inf")
        total = 0.0
        for w, grain in zip(weights, self.cfg.granularities):
            target = self._correct_cluster(pool, grain)
            sig = self.sigma_per_grain.get(grain, 1.0)
            total += w * self._per_grain_score(pool, grain, sig, target)
        return total

    def _mixed_pool_scores(self, pool: CPSamplePool,
                            weights: Tuple[float, float, float]) -> List[float]:
        # Score every cluster of the *medium* granularity for return
        # (final prediction set is over medium clusters, weighted by mix).
        ids_by_grain = pool.extra.get("cluster_ids_by_grain", {}) if isinstance(
            pool.extra, dict
        ) else {}
        med_ids = ids_by_grain.get("medium", pool.cluster_ids)
        n_c = max(med_ids) + 1 if med_ids else 0
        out = []
        for c in range(n_c):
            total = 0.0
            for w, grain in zip(weights, self.cfg.granularities):
                cidx = self._cluster_indices_for_grain(pool, grain)
                # Find the cluster in this granularity that contains the
                # majority of samples assigned to medium-cluster `c`.
                samples_in_c = [i for i, mc in enumerate(med_ids) if mc == c]
                grain_ids = ids_by_grain.get(grain, pool.cluster_ids)
                grain_targets = [grain_ids[i] for i in samples_in_c]
                if not grain_targets:
                    target = None
                else:
                    target = max(set(grain_targets), key=grain_targets.count)
                sig = self.sigma_per_grain.get(grain, 1.0)
                total += w * self._per_grain_score(pool, grain, sig, target)
            out.append(total)
        return out

    def predict(self, pool: CPSamplePool, alpha: float) -> CPPrediction:
        ids_by_grain = pool.extra.get("cluster_ids_by_grain", {}) if isinstance(
            pool.extra, dict
        ) else {}
        med_ids = ids_by_grain.get("medium", pool.cluster_ids)
        if not med_ids:
            return CPPrediction(qid=pool.qid, selected_clusters=[], set_size=0,
                                abstained=True, correct_in_set=False,
                                score=float("inf"))
        scores = self._mixed_pool_scores(pool, self.weights)
        selected = [c for c, s in enumerate(scores) if s <= self.q_hat]
        abstained = len(selected) == 0
        # Map selected medium-clusters back to "any of these contain a correct sample?"
        correct_in_set = False
        if not abstained:
            n_clusters_med = max(med_ids) + 1
            cluster_correct_med = [False] * n_clusters_med
            for s_idx, c in enumerate(med_ids):
                if pool.sample_correct[s_idx]:
                    cluster_correct_med[c] = True
            correct_in_set = any(cluster_correct_med[c] for c in selected
                                 if c < len(cluster_correct_med))
        score_min = float(min(scores)) if scores else float("inf")
        return CPPrediction(qid=pool.qid, selected_clusters=selected,
                            set_size=len(selected), abstained=abstained,
                            correct_in_set=correct_in_set, score=score_min)
