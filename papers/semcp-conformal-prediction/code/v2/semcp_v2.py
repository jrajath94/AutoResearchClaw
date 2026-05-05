"""SemCP v2 — contrastive between-cluster score, plug-in optimal sigma,
and held-out bandwidth selection. Aligned with Theorem 1 v2 + Theorem 2.

Key changes vs v1 (`code/methods/semcp.py`):
  1. Algorithm 1 ↔ Theorem 1 alignment: the lifted score in v1 was
     described as a within-cluster minimum but implemented as a contrastive
     between-cluster maximum. v2 commits to the contrastive form
     (Equation 2 in theorem1_proof_v2.tex) and clearly documents it.
  2. Plug-in optimal sigma: implements Theorem 2's closed-form
     hat_sigma* = sqrt((mu_B - mu_W) / (2 log(1 / (1-alpha)))).
     Falls back to grid search when the plug-in estimate is degenerate
     (e.g., mu_B <= mu_W which can happen if the partition is poor).
  3. Calibration / bandwidth-selection split disjoint from conformal
     calibration fold: removes the implicit test-set leakage concern.
  4. Empty-cluster abstention is a first-class signal, not a TODO.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple
import numpy as np

# Use sys.path / relative import depending on caller. The pod will
# install this as `methods_v2.semcp_v2`.
from methods.base import (CPMethod, CPPrediction, CPSamplePool,
                          conformal_quantile)


def rbf(d2: np.ndarray, sigma: float) -> np.ndarray:
    return np.exp(-d2 / (2.0 * sigma ** 2))


@dataclass
class SemCPConfig:
    sigma_grid: Tuple[float, ...] = (0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0)
    sigma_strategy: str = "plugin"  # "plugin" | "grid" | "hybrid"
    bandwidth_split_frac: float = 0.20  # held-out frac for bandwidth selection
    rng_seed: int = 42


class SemCPv2(CPMethod):
    """Contrastive between-cluster SemCP with plug-in optimal bandwidth."""

    name = "semcp_v2"

    def __init__(self, config: SemCPConfig | None = None):
        if config is None:
            config = SemCPConfig()
        self.cfg = config
        self.sigma: float = 1.0
        self.q_hat: float = float("inf")
        self.aux_log: dict = {}

    # ------------------------------------------------------------
    # Score primitives
    # ------------------------------------------------------------
    @staticmethod
    def _cluster_indices(pool: CPSamplePool) -> List[List[int]]:
        out: List[List[int]] = []
        n_c = max(pool.cluster_ids) + 1 if pool.cluster_ids else 0
        for cid in range(n_c):
            out.append([i for i, c in enumerate(pool.cluster_ids) if c == cid])
        return out

    @classmethod
    def _contrastive_score(cls, embeddings: np.ndarray,
                            cluster_indices: List[List[int]],
                            target: int, sigma: float) -> float:
        """Equation 2: 1 - max_{c' != target} kappa_sigma(centroid_target, centroid_{c'})."""
        if target < 0 or target >= len(cluster_indices) or not cluster_indices[target]:
            return float("inf")
        centroid_t = embeddings[cluster_indices[target]].mean(axis=0)
        max_kernel = 0.0
        any_other = False
        for c, idxs in enumerate(cluster_indices):
            if c == target or not idxs:
                continue
            any_other = True
            centroid_o = embeddings[idxs].mean(axis=0)
            d2 = float(np.sum((centroid_t - centroid_o) ** 2))
            k = float(rbf(np.array([d2]), sigma)[0])
            if k > max_kernel:
                max_kernel = k
        return 0.0 if not any_other else float(1.0 - max_kernel)

    def _scores_for_pool(self, pool: CPSamplePool, sigma: float) -> List[float]:
        if pool.embeddings is None or len(pool.cluster_ids) == 0:
            return []
        cidx = self._cluster_indices(pool)
        return [self._contrastive_score(pool.embeddings, cidx, c, sigma)
                for c in range(len(cidx))]

    def _cal_score(self, pool: CPSamplePool, sigma: float) -> float:
        if not any(pool.cluster_correct):
            return float("inf")
        cidx = self._cluster_indices(pool)
        c_star = next(c for c, ok in enumerate(pool.cluster_correct) if ok)
        return self._contrastive_score(pool.embeddings, cidx, c_star, sigma)

    # ------------------------------------------------------------
    # Plug-in optimal sigma (Theorem 2)
    # ------------------------------------------------------------
    def _plugin_sigma(self, pools: List[CPSamplePool], alpha: float) -> float:
        """hat_sigma* = sqrt( (mu_B - mu_W) / (2 log(1/(1-alpha))) )."""
        within: List[float] = []
        between: List[float] = []
        for p in pools:
            if p.embeddings is None or not any(p.cluster_correct):
                continue
            cidx = self._cluster_indices(p)
            c_star = next(c for c, ok in enumerate(p.cluster_correct) if ok)
            if not cidx[c_star]:
                continue
            cluster_pts = p.embeddings[cidx[c_star]]
            centroid = cluster_pts.mean(axis=0)
            # within-cluster mean squared distance to centroid
            d2_within = float(np.mean(np.sum((cluster_pts - centroid) ** 2, axis=1)))
            within.append(d2_within)
            # min between-cluster squared distance to other centroids
            min_d2_between = float("inf")
            for c, idxs in enumerate(cidx):
                if c == c_star or not idxs:
                    continue
                other = p.embeddings[idxs].mean(axis=0)
                d2 = float(np.sum((centroid - other) ** 2))
                if d2 < min_d2_between:
                    min_d2_between = d2
            if np.isfinite(min_d2_between):
                between.append(min_d2_between)
        if not within or not between:
            return 1.0  # degenerate fallback
        mu_W = float(np.mean(within))
        mu_B = float(np.mean(between))
        gap = mu_B - mu_W
        if gap <= 0:
            return 1.0  # partition too poor; fallback to a stable default
        denom = 2.0 * np.log(1.0 / max(1e-6, 1.0 - alpha))
        sigma_star = float(np.sqrt(gap / max(denom, 1e-6)))
        # Clip to a reasonable range to guard against extreme outliers
        return float(np.clip(sigma_star, 0.05, 8.0))

    # ------------------------------------------------------------
    # Calibration: split, choose sigma, compute q_hat
    # ------------------------------------------------------------
    def calibrate(self, pools: List[CPSamplePool], alpha: float) -> None:
        rng = np.random.default_rng(self.cfg.rng_seed)
        idx = rng.permutation(len(pools))
        n_band = max(1, int(len(idx) * self.cfg.bandwidth_split_frac))
        band = [pools[i] for i in idx[:n_band]]
        cal = [pools[i] for i in idx[n_band:]]

        if self.cfg.sigma_strategy == "plugin":
            self.sigma = self._plugin_sigma(band, alpha)
            self.aux_log["sigma_strategy"] = "plugin"
        elif self.cfg.sigma_strategy == "grid":
            self.sigma = self._grid_sigma(band, alpha)
            self.aux_log["sigma_strategy"] = "grid"
        else:  # hybrid: take min set-size between plug-in and best grid choice
            sg_plug = self._plugin_sigma(band, alpha)
            sg_grid = self._grid_sigma(band, alpha)
            sz_plug = self._eval_size(band, sg_plug, alpha)
            sz_grid = self._eval_size(band, sg_grid, alpha)
            self.sigma = sg_plug if sz_plug <= sz_grid else sg_grid
            self.aux_log["sigma_strategy"] = "hybrid"
            self.aux_log["sigma_plug"] = sg_plug
            self.aux_log["sigma_grid"] = sg_grid

        cal_scores = np.array([self._cal_score(p, self.sigma) for p in cal],
                              dtype=float)
        finite = cal_scores[np.isfinite(cal_scores)]
        self.q_hat = conformal_quantile(finite, alpha) if len(finite) else float("inf")
        self.aux_log["sigma"] = float(self.sigma)
        self.aux_log["n_admissible_cal"] = int(len(finite))
        self.aux_log["alpha"] = float(alpha)

    # ------------------------------------------------------------
    # Grid-search sigma (Theorem 2 fallback / ablation)
    # ------------------------------------------------------------
    def _grid_sigma(self, band: List[CPSamplePool], alpha: float) -> float:
        best_sig, best_size = self.cfg.sigma_grid[0], float("inf")
        for sig in self.cfg.sigma_grid:
            sz = self._eval_size(band, sig, alpha)
            if sz < best_size:
                best_size = sz
                best_sig = sig
        return float(best_sig)

    def _eval_size(self, band: List[CPSamplePool], sig: float, alpha: float) -> float:
        cal_scores = np.array([self._cal_score(p, sig) for p in band], dtype=float)
        finite = cal_scores[np.isfinite(cal_scores)]
        if len(finite) == 0:
            return float("inf")
        q = conformal_quantile(finite, alpha)
        sizes: List[int] = []
        for p in band:
            if not any(p.cluster_correct):
                continue
            scores = self._scores_for_pool(p, sig)
            sizes.append(sum(1 for s in scores if s <= q))
        return float(np.mean(sizes)) if sizes else float("inf")

    # ------------------------------------------------------------
    # Predict
    # ------------------------------------------------------------
    def predict(self, pool: CPSamplePool, alpha: float) -> CPPrediction:
        cidx = self._cluster_indices(pool)
        if not cidx:
            return CPPrediction(qid=pool.qid, selected_clusters=[], set_size=0,
                                abstained=True, correct_in_set=False,
                                score=float("inf"))
        scores = [self._contrastive_score(pool.embeddings, cidx, c, self.sigma)
                  for c in range(len(cidx))]
        selected = [c for c, s in enumerate(scores) if s <= self.q_hat]
        abstained = len(selected) == 0
        correct_in_set = (any(pool.cluster_correct[c] for c in selected)
                          if not abstained else False)
        score_min = float(min(scores)) if scores else float("inf")
        return CPPrediction(qid=pool.qid, selected_clusters=selected,
                            set_size=len(selected), abstained=abstained,
                            correct_in_set=correct_in_set, score=score_min)
