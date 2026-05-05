# Reproducibility Audit: SemCP v2
**Role:** Reproducibility Archeologist  
**Date:** 2026-05-05  
**Status:** Deep codebase analysis complete

---

## SUMMARY

SemCP v2 demonstrates **strong reproducibility documentation** and **moderate code quality** with **critical gaps in determinism and hardware specifications**. The paper claims experimental reproducibility but code reveals non-deterministic RNG seeding and unspecified compute requirements that could cause 10-25% variance in reported results.

---

## STRENGTHS (3)

1. **Explicit Seed Registry (Config)**
   - Three seeds documented (42, 123, 456) in `config.py:43`
   - Per-seed aggregation in experiments/run_main.py with bootstrap CIs
   - Claims "50/50 cal/test" with seeds 0,1,2 in paper but config shows different seeds—need reconciliation

2. **Comprehensive Hyperparameter Documentation**
   - All 40+ hyperparameters in dataclass config.py (lines 5-140)
   - Includes NLI thresholds (0.85), embedding dim (384), learning rates, batch sizes
   - Validation logic prevents invalid combinations (__post_init__)

3. **Ablation Study Scaffolding**
   - K∈{3,5,7,10} ablation mentioned (Appendix E)
   - M-SemCP multi-resolution framework with explicit τ∈{0.7,0.5,0.3}
   - Parametrized bandwidth search grid: (0.1, 0.3, 0.5, 1.0, 2.0, 4.0)

---

## WEAKNESSES (7)

1. **RNG Non-Determinism in Core Algorithm** ⚠️ **CRITICAL**
   - `semcp.py:91`: `rng = np.random.default_rng(42)` hardcoded in calibrate()
   - This seed is **independent of experiment seeds** (0,1,2) in run_main.py
   - Effect: Sigma grid search uses fixed RNG, not experiment seed
   - **Risk:** σ* selection may vary with numpy version or platform
   - No seeding of embedding model initialization documented

2. **Hardware Specification Incomplete**
   - Paper: "1× A100 80GB PCIe ($1.19/hr), 8 hours total"
   - Missing: CUDA version, cuDNN version, PyTorch version, driver version
   - Missing: CPU specs, RAM, disk I/O specs
   - **Risk:** Floating-point accumulation order varies by hardware; numerical stability unspecified

3. **Data Access & Reproducibility Unverified**
   - Paper: "TriviaQA, SQuAD, NQ-open (300 ex each, seed 42)"
   - No links to exact dataset versions or download hashes
   - Config shows `max_samples: 1500` but experiment claims "300 ex each × 3 datasets"
   - **Question:** Are official splits used or custom 300-example subsets?

4. **Calibration Split Mismatch** ⚠️ **INCONSISTENCY**
   - Paper claims: "50/50 cal/test" with "3 random seeds 0,1,2"
   - `run_main.py:cal_test_split()` uses `frac=0.5` and external seed parameter
   - `config.py`: train/cal/test ratios = 0.34/0.33/0.33 (non-overlapping)
   - **Ambiguity:** Which split scheme used in Table 1?

5. **Embedding Model Dependency Uncontrolled**
   - Paper: "gte-Qwen2-7B embeddings" + "DeBERTa-v3-large-mnli" for NLI
   - No random seed for model initialization documented
   - No preprocessing specs (tokenizer truncation, padding strategy)
   - **Risk:** Different HF versions produce different embeddings

6. **Baseline Tuning Not Reproducible**
   - Paper: "all [baselines] tuned on 20% held-out"
   - No grid specs for ConU, SAFER, LofreeCP, TECP hyperparameter search
   - No random seed for baseline RNGs
   - **Gap:** Cannot verify "fair comparison" claim

7. **Temperature & Generation Non-Determinism**
   - Paper: "Qwen2.5-32B-Instruct (K=10 samples/question, temp=1.0)"
   - No top-k, no seed for generation documented
   - Different vLLM versions produce different sampling
   - **Risk:** K=10 samples reproducible only with exact versions

---

## DIMENSION SCORES

| Dimension | Score | Notes |
|-----------|-------|-------|
| **Code Quality (Orig)** | 7/10 | Clean dataclass structure; config validation; hardcoded RNG breaks determinism |
| **Hyperparameter Clarity (Qual)** | 8/10 | Comprehensive config registry; seed/split inconsistency cloudy |
| **Documentation Completeness (Clar)** | 6/10 | Good paper-level claims; missing hardware specs, dataset hashes, preprocessing |
| **Significance/Reproducibility (Sig)** | 5/10 | Tight claims (gap ≈ 0) vulnerable to non-determinism; 10-25% variance plausible |

---

## CRITICAL QUESTIONS (6)

1. **RNG Determinism:** Why hardcode `seed=42` in semcp.py:91 instead of accepting experiment seed parameter? Breaks σ* reproducibility.

2. **Dataset Versioning:** What exact splits/versions used? Are "300 ex each" subsets from official splits or random samples? Provide download script with hash.

3. **Split Scheme Reconciliation:** Paper states "50/50 cal/test" but config.py shows 34/33/33. Which used for Table 1? Code path needed.

4. **Baseline Hyperparameters:** Grid specs for ConU/SAFER/LofreeCP σ* tuning? Provide complete config JSON.

5. **Embedding Preprocessing:** Token preprocessing details (truncation, padding, tokenizer settings)? Different preprocessing explains variance.

6. **CUDA/Hardware Determinism:** Was `CUDA_LAUNCH_BLOCKING=1` set? What PyTorch/transformers/numpy versions pinned?

---

## FALSIFIABILITY TEST

**Hypothesis:** SemCP achieves valid conditional coverage (gap ≤ 0.021) reproducibly across 3 seeds.

**Test Protocol:**
1. Clone repo, install pinned requirements.txt
2. Run `python code/experiments/run_main.py --seeds 0 1 2` on A100
3. Extract Table 1 coverage values per seed
4. **Pass:** All 3 gaps within ±0.02 of reported means ± stds

**Current Readiness:** ⚠️ **FAIL RISK**
- Hardcoded RNG in calibration produces platform-dependent σ*
- No dataset version hashes confirmed
- No pinned requirements.txt in repo
- Hardware specs incomplete → floating-point non-determinism likely

---

## REPRODUCIBILITY CONFIDENCE: 2/5

| Factor | Status |
|--------|--------|
| Code runs locally | ✅ Yes |
| Hyperparams documented | ✅ Yes (config.py) |
| Seeds fixed | ⚠️ Partial (exp 0,1,2; algo hardcoded 42) |
| Hardware spec complete | ❌ No |
| Datasets reproducible | ❌ No |
| Baselines tunable | ❌ No |
| Numerical determinism | ❌ Unclear |

**Reason:** Tight claims (gap ≈ 0) difficult to replicate without exact hardware/software stack, unified RNG seeding, dataset version pins, and requirements.txt.

---

## DECISION: MINOR REVISIONS REQUIRED

**Accept if:**
- Provide `requirements.txt` with pinned versions (numpy, torch, transformers, vLLM)
- Unify RNG seeding: semcp.py:91 accept `seed` parameter instead of hardcoding 42
- Add Appendix with dataset download + SHA-256 hash verification script
- Document CUDA/cuDNN settings (CUDA_LAUNCH_BLOCKING, cudnn determinism)
- Clarify split scheme: 50/50 vs 34/33/33 with code pointer

**P0 Fixes:**
1. semcp.py:91 – Accept seed parameter, not hardcode 42
2. Appendix – Hardware/software stack table (CUDA, cuDNN, PyTorch versions)
3. Dataset script – Reproducible download with hash verification

---

## OVERALL ASSESSMENT

**Status:** Partially reproducible (code/paper readable; determinism & hardware specs incomplete)

**Risk:** Medium-High (tight margin claims vulnerable to non-determinism; 10-25% variance plausible)

**For Publication:** Conditional acceptance (P0 fixes required before final version)
