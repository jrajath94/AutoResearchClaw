# ADVERSARIAL PRACTITIONER REVIEW: SemCP v2

**Persona**: Production-readiness auditor, edge-case hunter, failure-mode analyst  
**Focus**: Deployment brittleness, hyperparameter sensitivity, latency, robustness  
**Date**: 2026-05-05

---

## EXECUTIVE SUMMARY

SemCP v2 achieves tight coverage validity (gaps within ±0.021 of bound) and removes the primary hyperparameter via closed-form bandwidth selection. However, critical failure modes and production readiness gaps persist:

- **NQ-open admits only 27.1% of test cases** (p_A=0.271), making coverage unattainable per paper's own theory
- **No runtime diagnostic** to detect admissibility failure before deploying to production
- **K=10 hard-coded** with no principled selection rule; entropy-dependent guidance missing
- **Sub-Gaussian assumption** for Theorem 2 unvalidated empirically
- **Latency analysis absent**; inference cost per query unknown
- **NLI dependency** (DeBERTa-v3-large: ≥100 forward passes per calibration/test instance) causes operational brittleness

**Recommendation**: CONDITIONAL ACCEPT — requires mandatory fixes to admissibility diagnostics, failure-mode characterization, and assumption validation before production deployment.

---

## STRENGTHS (5)

### 1. Tight Coverage Validity
Achieves conditional coverage gaps of -0.007 to +0.021 versus theoretical bound of 0.891. This is not just soundness but empirical alignment with theory—genuinely rare in conformal prediction. The coverage is predictably tight, not accidentally valid.

### 2. Bandwidth Hyperparameter Elimination
Theorem 2's closed-form plug-in σ* matches grid-search within 5%. This removes the primary tunable hyperparameter and is critical for production systems where per-dataset hyperparameter tuning is expensive and error-prone. Automated selection is a real win.

### 3. Unified Framework (M-SemCP)
Recovers ConU, TECP, and LofreeCP as corners of a convex simplex over 3 NLI granularities {τ∈{0.7,0.5,0.3}}. Elegant unification that validates the semantic partitioning approach and clarifies relationships between prior methods. Not ad-hoc.

### 4. O(K log K) Computational Efficiency
HAC-NLI with prefilter avoids O(K²) pairwise NLI cost. K=10 becomes feasible. Transitivity correction addresses a non-trivial clustering problem (intransitive NLI edges).

### 5. Reproducibility Maturity
Claims traced to JSON artifacts, checklist 15/15, no unfilled TODOs. v1→v2 improvements systematically address every feedback point. Paper feels complete from an organizational standpoint.

---

## WEAKNESSES (9)

### 1. **CRITICAL: Admissibility Failure Undiagnosed at Runtime**

Theorem 1 conditions on "true meaning is sampled" but never defines what "true meaning" is mathematically. Is it an oracle partition? A semantic ground truth independent of NLI model output? 

The paper states (Sec 6): **"If p_A < 1-α, marginal coverage unattainable—invest in generator."** This is a hard constraint, not a tunable parameter. Yet:
- **Zero runtime diagnostic** provided to detect p_A < 1-α before deployment
- Practitioners will deploy, silently produce invalid guarantees, never know why
- This is a binary validity switch that breaks the entire promise of the method

**Production impact**: Admissibility is a dealbreaker, not a limitation. Deploying without detection is dangerous.

### 2. **Catastrophic Failure on NQ-open (p_A=0.271)**

| Dataset | p_A | Status |
|---------|-----|--------|
| TriviaQA | 0.707 | ✅ Marginal coverage feasible |
| SQuAD | 0.811 | ✅ Marginal coverage feasible |
| NQ-open | **0.271** | ❌ 73% inadmissible |

NQ-open is a standard open-domain QA benchmark. On 73% of test cases, the method is forced to abstain or return empty sets. The paper acknowledges this but **does not investigate why**:
- Is semantic partitioning too coarse for open-ended outputs?
- Does DeBERTa-v3-large-mnli systematically misclassify on open-domain QA?
- Does Qwen2.5-32B simply not generate diverse enough candidates?

**Without diagnosis, there is no fix, and SemCP is unusable on open-domain QA.**

### 3. **NLI Model Dependency Underspecified**

DeBERTa-v3-large-mnli + gte-Qwen2-7B is a specific stack. Appendix D claims "sensitivity checked" but results are not in the bundle. Unknown:
- Does DeBERTa make systematic errors on technical QA?
- What happens with medical, legal, or code-generation domains?
- NLI models are known to exploit spurious correlations and break on paraphrases

**Missing ablations:**
- Swap DeBERTa-v3 → T5-large-mnli, RoBERTa-mnli
- Swap embeddings → all-MiniLM, sentence-transformers
- Per-domain NLI model validation

### 4. **K=10 is Empirically Constrained, Not Principled**

Ablation (Appendix E) shows K∈{3,5,7,10} but **no guidance on insufficiency**. Paper acknowledges: "higher-entropy queries may need K>10" but:
- "Entropy" is undefined (query entropy? output variance? logit entropy?)
- No K(entropy) curve or lookup table
- Production systems cannot hard-code K=10 for all domains

**What should practitioners do with MMLU, SQuAD-Adversarial, or code generation (higher variance)?** No answer.

### 5. **Contrastive RBF Kernel Lacks Robustness Analysis**

Score: s̃(X,C,S,σ) = 1 - max_c' κσ(φ̄c, φ̄c')

The **max** operation is sensitive to outlier cluster embeddings:
- If one cluster has extreme centroid (5σ outlier), it dominates all predictions
- Can inflate |C(X)| arbitrarily
- No analysis of RBF behavior under distribution shift or adversarial perturbations

**Missing:**
- Outlier detection and mitigation
- Adversarial robustness test
- Distribution-shift stress test

### 6. **Theorem 2 Assumes Sub-Gaussian Embeddings (Unvalidated)**

Closed-form σ* derives from sub-Gaussian variance assumption. Are gte-Qwen2-7B outputs sub-Gaussian? **No empirical test provided.**

If embeddings have heavy tails (bimodal, exponential), the closed-form σ* is suboptimal and the "5% match to grid-search" claim is misleading.

**Required validation:**
- Kolmogorov-Smirnov test: H0 = ||φ|| ~ N(μ, σ²)
- Q-Q plots
- Robust alternative if rejected (e.g., MAD-based σ*)

### 7. **Calibration Split (50/50 on 300 examples) Limits Confidence**

TriviaQA: 150 calibration samples. The quantile ⌈(1-α)(|I|+1)/|I|⌉ has variance O(1/√150). Standard errors (±0.007–±0.058) are **driven by dataset size, not method quality**. Finite-sample concentration analysis missing.

**Risk**: Results may not generalize to 100K+ examples or high-α regimes.

### 8. **Set Size Inflation Under Distribution Shift Not Addressed**

Results are in-distribution (fixed LLM, temperature=1.0). If temperature increases to 2.0 or model outputs shift, what happens?
- Variance minimization in Theorem 2 assumes fixed embedding distribution
- Mismatch between calibration and test degrades σ*
- No OOD stress test provided

### 9. **Transitivity Correction in HAC-NLI Underspecified**

Paper mentions "transitivity-corrected HAC" but **doesn't define the correction** or quantify its impact. If NLI edges are intransitive (A≡B, B≡C, but A≠C), how is this handled? Clustering with non-transitive similarity is non-standard and needs rigor.

---

## SCORES (1-10 scale)

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Originality (Orig)** | 8 | Novel semantic partitioning + contrastive kernel. Theorem 1 closure is new. M-SemCP unification clever. Docked 2: NLI + conformal is natural; not breakthrough. |
| **Quality (Qual)** | 7 | Solid math, tight empirical alignment. Major gaps: admissibility brittleness undiagnosed, assumptions unvalidated, K=10 hard-coded. Hides failure modes in discussion. |
| **Clarity (Clar)** | 7 | Well-written overall. Hides failure modes: "If p_A < 1-α" buried in Sec 6. NQ-open collapse unexplained. Algorithm 1 clear; Theorem 1 conditioning vague. |
| **Significance (Sig)** | 6 | Incremental for CP-for-LLMs. Tight coverage is nice. Practical impact limited by NLI dependency, admissibility brittleness, K constraints. Unlikely to shift production practice without reliability fixes. |

**Weighted Average**: ~7.0 (solid paper with significant production gaps)

---

## 5+ CRITICAL QUESTIONS

### Q1: Admissibility Measurement at Inference Time
How should practitioners diagnose p_A < 1-α before deployment? Paper says "invest in generator" but provides no metrics. Should we estimate p̂_A on held-out calibration? What's variance of p̂_A with |I|=150? How large should CI_upper be before aborting?

### Q2: Why Does NQ-open Collapse to p_A=0.271?
TriviaQA/SQuAD are extraction QA. NQ-open is open-ended. Is semantic partitioning too coarse? Does DeBERTa misclassify on open-domain? Does Qwen2.5 generate insufficiently diverse candidates? **Root cause analysis is missing**—without it, no fix is possible.

### Q3: Sub-Gaussian Validation for gte-Qwen2-7B
Is σ* valid if embeddings violate sub-Gaussianity? Provide:
- K-S test (H0 = normality), p-value
- Q-Q plots
- If rejected, compute robust σ* (MAD-based) and compare

### Q4: K Selection Rule for New Domains
Define "entropy" formally (query entropy? output diversity? logit variance?). Provide:
- K(entropy) curve or lookup table
- Validation on MMLU, SQuAD-Adversarial, or high-variance benchmarks
- Minimum K recommendation for target marginal coverage

### Q5: Inference-Time Latency Breakdown
8 hours total is reported; per-query cost is missing. Provide:
- Time for NLI clustering per query
- Time for contrastive RBF scoring
- Total vs baselines
- Is <500ms achievable for real-time QA?

### Q6: RBF Kernel Robustness to Outliers
Does max_c' dominate all set sizes if a cluster has extreme embedding? Can adversarial inputs inflate |C(X)| via embedding manipulation? Provide empirical robustness test.

---

## FALSIFIABILITY TEST

**Core Hypothesis:**  
SemCP provides valid, tight coverage guarantees across diverse QA domains with automatic bandwidth and fixed K=10.

### Test Protocol

**Test 1: Admissibility Threshold**
- Report p̂_A with 95% CI on NQ-open and a new OOD dataset
- **Fail condition:** p̂_A + CI_upper < 1-α → coverage unattainable
- **Current status:** NQ-open already failing (p̂_A=0.271)

**Test 2: Theorem 2 Optimality**
- Compute σ* via Theorem 2 vs σ_oracle = argmin_σ Var(s̃) on test
- **Fail condition:** |σ* - σ_oracle| / σ_oracle > 15% → sub-Gaussianity violated
- **Required:** K-S test with p > 0.05 for normality

**Test 3: K-Sufficiency for High-Entropy Queries**
- Run K∈{5,10,15,20} on MMLU open-ended + SQuAD-Adversarial
- **Fail condition:** K=10 fails coverage on >5% of queries
- **Required:** Entropy-dependent K recommendation

**Test 4: Robustness to OOD**
- Shift temperature 1.0 → 2.0, keep σ* fixed
- **Fail condition:** Coverage gap increases >0.03 or set size inflates >30%

---

## CONFIDENCE & DECISION

### Overall Confidence: **2.5 / 5**

| Factor | Score | Assessment |
|--------|-------|------------|
| **Mathematical Soundness** | 4/5 | ✅ Proofs appear correct; tight alignment on TriviaQA/SQuAD |
| **Empirical Robustness** | 2/5 | ⚠️ NQ-open p_A=0.271; K unjustified; assumptions unvalidated |
| **Production Readiness** | 1.5/5 | ❌ No diagnostics; NLI sensitivity unknown; latency hidden |
| **Generalization** | 2.5/5 | ⚠️ Works on extraction QA; breaks on open-domain; undiagnosed |

---

## DECISION: CONDITIONAL ACCEPT WITH MAJOR REVISIONS

### Mandatory Revisions (blocking acceptance)

1. **Diagnose NQ-open collapse (p_A=0.271)**
   - Root-cause analysis: NLI failure? Partitioning coarseness? Sampling diversity?
   - Either fix for open-domain QA or explicitly scope to extraction QA
   - Add p_A values for 5+ new domains

2. **Add runtime admissibility diagnostics**
   - Algorithm to estimate p̂_A with 95% CI at inference time
   - Warning: "p̂_A + CI_upper < 1-α → abort deployment"
   - Variance analysis of p̂_A estimation

3. **Validate sub-Gaussianity (Theorem 2)**
   - K-S test (p-value), Q-Q plots
   - If rejected: provide robust σ* (MAD-based) and compare

### Strongly Recommended

4. **Replace K=10 with principled selection**
   - Define entropy formally
   - K(entropy) curve or table
   - Validation on high-variance benchmarks

5. **Report inference latency breakdown**
   - Per-query costs (NLI, RBF, quantile)
   - Comparison to baselines
   - Recommendation: <500ms

6. **Ablate NLI model dependency**
   - Alternative NLI models + embeddings
   - Per-domain sensitivity

---

## BOTTOM LINE

**What works:** Tight coverage, bandwidth automation, framework unification, reproducibility.

**What breaks:** NQ-open (p_A=0.271), no failure detection, K unjustified, assumptions unvalidated, latency unknown.

**Verdict:** Mathematically sound but operationally brittle. Practitioners deploying on open-domain QA will silently produce invalid guarantees. The checklist-perfect tone obscures this.

**Path forward:** Diagnose NQ-open, add diagnostics, validate assumptions, justify K. Then it's publication-ready.

---

*— The Adversarial Practitioner, 2026-05-05*