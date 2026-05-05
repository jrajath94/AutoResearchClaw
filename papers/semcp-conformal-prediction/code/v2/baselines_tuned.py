"""Tuned-baseline wrappers for ConU, SAFER, LofreeCP, TECP.

Council issue: SemCP tunes sigma on a held-out 20% split; baselines used
fixed/default hyperparameters (e.g., SAFER abstain_min_freq=0.10,
LofreeCP lambda=0.5 from public repo). This is an unfair comparison.

These wrappers add tunable hyperparameters to each baseline and select
them on the SAME held-out split SemCPv2 uses for sigma. We keep the
original (untuned) baselines available as `*_paperdefault` for an
appendix sensitivity table.
"""
from __future__ import annotations

from typing import List, Sequence
import numpy as np

from methods.base import (CPMethod, CPPrediction, CPSamplePool,
                          conformal_quantile)


# -----------------------------------------------------------------------
# Helper: held-out bandwidth-selection split — must match SemCPv2 exactly.
# -----------------------------------------------------------------------

def _split_band_cal(pools: List[CPSamplePool], frac: float, seed: int):
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(pools))
    n_band = max(1, int(len(idx) * frac))
    band = [pools[i] for i in idx[:n_band]]
    cal = [pools[i] for i in idx[n_band:]]
    return band, cal


# -----------------------------------------------------------------------
# Tuned SAFER: search abstain_min_freq on band split
# -----------------------------------------------------------------------
class TunedSAFER(CPMethod):
    name = "safer_tuned"
    grid = (0.05, 0.10, 0.15, 0.20, 0.25)
    band_frac: float = 0.20
    rng_seed: int = 42

    def __init__(self):
        self.q_hat = float("inf")
        self.abstain_min_freq = 0.10
        self.aux_log: dict = {}

    @staticmethod
    def _freq_scores(pool: CPSamplePool) -> List[float]:
        if not pool.cluster_ids:
            return []
        K = len(pool.cluster_ids)
        n_clusters = max(pool.cluster_ids) + 1
        counts = np.bincount(pool.cluster_ids, minlength=n_clusters)
        return [1.0 - c / K for c in counts]

    @classmethod
    def _cal_score(cls, pool: CPSamplePool) -> float:
        if not any(pool.cluster_correct):
            return float("inf")
        sc = cls._freq_scores(pool)
        c = next(c for c, ok in enumerate(pool.cluster_correct) if ok)
        return sc[c]

    def calibrate(self, pools: List[CPSamplePool], alpha: float) -> None:
        band, cal = _split_band_cal(pools, self.band_frac, self.rng_seed)
        cal_scores = np.array([self._cal_score(p) for p in cal], dtype=float)
        finite = cal_scores[np.isfinite(cal_scores)]
        self.q_hat = conformal_quantile(finite, alpha) if len(finite) else float("inf")
        # Tune abstain_min_freq on band: minimize average size on
        # admissible-band points subject to coverage >= 1-alpha.
        best_t, best_score = self.grid[0], float("inf")
        for t in self.grid:
            self.abstain_min_freq = t
            sizes, cov = [], []
            for p in band:
                pred = self._predict_one(p)
                if pred.abstained:
                    continue
                sizes.append(pred.set_size)
                cov.append(pred.correct_in_set)
            if sizes and np.mean(cov) >= 1.0 - alpha:
                if np.mean(sizes) < best_score:
                    best_score = float(np.mean(sizes))
                    best_t = t
        self.abstain_min_freq = best_t
        self.aux_log = {"abstain_min_freq": best_t,
                        "q_hat": float(self.q_hat)}

    def _predict_one(self, pool: CPSamplePool) -> CPPrediction:
        scores = self._freq_scores(pool)
        if not scores:
            return CPPrediction(qid=pool.qid, selected_clusters=[], set_size=0,
                                abstained=True, correct_in_set=False,
                                score=float("inf"))
        selected = [c for c, s in enumerate(scores) if s <= self.q_hat]
        if not selected:
            best_freq = 1.0 - min(scores)
            if best_freq < self.abstain_min_freq:
                return CPPrediction(qid=pool.qid, selected_clusters=[],
                                    set_size=0, abstained=True,
                                    correct_in_set=False,
                                    score=float(min(scores)))
            best = int(np.argmin(scores))
            selected = [best]
        correct_in_set = any(pool.cluster_correct[c] for c in selected)
        return CPPrediction(qid=pool.qid, selected_clusters=selected,
                            set_size=len(selected), abstained=False,
                            correct_in_set=correct_in_set,
                            score=float(min(scores)))

    def predict(self, pool: CPSamplePool, alpha: float) -> CPPrediction:
        return self._predict_one(pool)


# -----------------------------------------------------------------------
# Tuned LofreeCP: search lambda on band split
# -----------------------------------------------------------------------
class TunedLofreeCP(CPMethod):
    name = "lofreecp_tuned"
    grid = (0.0, 0.25, 0.5, 1.0, 2.0)
    band_frac: float = 0.20
    rng_seed: int = 42

    def __init__(self):
        self.q_hat = float("inf")
        self.lam = 0.5
        self.aux_log: dict = {}

    def _string_scores(self, pool: CPSamplePool) -> List[float]:
        from collections import Counter
        if not pool.samples:
            return []
        K = len(pool.samples)
        counts = Counter(pool.samples)
        out = []
        for y in pool.samples:
            p_hat = counts[y] / K
            R = np.log1p(len(y) / 10.0)
            out.append(-np.log(max(p_hat, 1e-12)) + self.lam * R)
        return out

    def _cal_score(self, pool: CPSamplePool) -> float:
        if not any(pool.sample_correct):
            return float("inf")
        sc = self._string_scores(pool)
        idxs = [i for i, ok in enumerate(pool.sample_correct) if ok]
        return float(min(sc[i] for i in idxs))

    def calibrate(self, pools: List[CPSamplePool], alpha: float) -> None:
        band, cal = _split_band_cal(pools, self.band_frac, self.rng_seed)
        # Tune lambda on band by minimizing held-out set size at correct-coverage
        best_lam, best_size = self.grid[0], float("inf")
        for lam in self.grid:
            self.lam = lam
            cs = np.array([self._cal_score(p) for p in band], dtype=float)
            finite = cs[np.isfinite(cs)]
            if len(finite) == 0:
                continue
            q_band = conformal_quantile(finite, alpha)
            sizes, covs = [], []
            for p in band:
                if not any(p.cluster_correct):
                    continue
                scores = self._string_scores(p)
                selected_strs = [i for i, s in enumerate(scores) if s <= q_band]
                clusters = sorted(set(p.cluster_ids[i] for i in selected_strs))
                sizes.append(len(clusters))
                covs.append(any(p.cluster_correct[c] for c in clusters))
            if sizes and np.mean(covs) >= 1.0 - alpha:
                if np.mean(sizes) < best_size:
                    best_size = float(np.mean(sizes))
                    best_lam = lam
        self.lam = best_lam
        cs = np.array([self._cal_score(p) for p in cal], dtype=float)
        finite = cs[np.isfinite(cs)]
        self.q_hat = conformal_quantile(finite, alpha) if len(finite) else float("inf")
        self.aux_log = {"lambda": best_lam, "q_hat": float(self.q_hat)}

    def predict(self, pool: CPSamplePool, alpha: float) -> CPPrediction:
        scores = self._string_scores(pool)
        if not scores:
            return CPPrediction(qid=pool.qid, selected_clusters=[], set_size=0,
                                abstained=True, correct_in_set=False,
                                score=float("inf"))
        selected_strs = [i for i, s in enumerate(scores) if s <= self.q_hat]
        clusters = sorted(set(pool.cluster_ids[i] for i in selected_strs))
        abstained = len(clusters) == 0
        correct_in_set = (any(pool.cluster_correct[c] for c in clusters)
                          if not abstained else False)
        return CPPrediction(qid=pool.qid, selected_clusters=clusters,
                            set_size=len(clusters), abstained=abstained,
                            correct_in_set=correct_in_set,
                            score=float(min(scores)))


# -----------------------------------------------------------------------
# Tuned TECP: tune temperature scaling on log-probs
# -----------------------------------------------------------------------
class TunedTECP(CPMethod):
    name = "tecp_tuned"
    grid = (0.5, 1.0, 1.5, 2.0)
    band_frac: float = 0.20
    rng_seed: int = 42

    def __init__(self):
        self.q_hat = float("inf")
        self.temp = 1.0
        self.aux_log: dict = {}

    def _string_scores(self, pool: CPSamplePool) -> List[float]:
        lp = pool.extra.get("mean_token_nll") if isinstance(pool.extra, dict) else None
        if lp is not None and len(lp) == len(pool.samples):
            return [float(x) / max(self.temp, 1e-3) for x in lp]
        # fallback: -log freq
        from collections import Counter
        if not pool.samples:
            return []
        K = len(pool.samples)
        counts = Counter(pool.samples)
        return [-float(np.log(max(counts[y] / K, 1e-12))) for y in pool.samples]

    def _cal_score(self, pool: CPSamplePool) -> float:
        if not any(pool.sample_correct):
            return float("inf")
        sc = self._string_scores(pool)
        idxs = [i for i, ok in enumerate(pool.sample_correct) if ok]
        return float(min(sc[i] for i in idxs))

    def calibrate(self, pools: List[CPSamplePool], alpha: float) -> None:
        band, cal = _split_band_cal(pools, self.band_frac, self.rng_seed)
        best_t, best_size = self.grid[0], float("inf")
        for t in self.grid:
            self.temp = t
            cs = np.array([self._cal_score(p) for p in band], dtype=float)
            finite = cs[np.isfinite(cs)]
            if len(finite) == 0:
                continue
            q_band = conformal_quantile(finite, alpha)
            sizes, covs = [], []
            for p in band:
                if not any(p.cluster_correct):
                    continue
                scores = self._string_scores(p)
                selected_strs = [i for i, s in enumerate(scores) if s <= q_band]
                clusters = sorted(set(p.cluster_ids[i] for i in selected_strs))
                sizes.append(len(clusters))
                covs.append(any(p.cluster_correct[c] for c in clusters))
            if sizes and np.mean(covs) >= 1.0 - alpha:
                if np.mean(sizes) < best_size:
                    best_size = float(np.mean(sizes))
                    best_t = t
        self.temp = best_t
        cs = np.array([self._cal_score(p) for p in cal], dtype=float)
        finite = cs[np.isfinite(cs)]
        self.q_hat = conformal_quantile(finite, alpha) if len(finite) else float("inf")
        self.aux_log = {"temp": best_t, "q_hat": float(self.q_hat)}

    def predict(self, pool: CPSamplePool, alpha: float) -> CPPrediction:
        scores = self._string_scores(pool)
        if not scores:
            return CPPrediction(qid=pool.qid, selected_clusters=[], set_size=0,
                                abstained=True, correct_in_set=False,
                                score=float("inf"))
        selected_strs = [i for i, s in enumerate(scores) if s <= self.q_hat]
        clusters = sorted(set(pool.cluster_ids[i] for i in selected_strs))
        abstained = len(clusters) == 0
        correct_in_set = (any(pool.cluster_correct[c] for c in clusters)
                          if not abstained else False)
        return CPPrediction(qid=pool.qid, selected_clusters=clusters,
                            set_size=len(clusters), abstained=abstained,
                            correct_in_set=correct_in_set,
                            score=float(min(scores)))
