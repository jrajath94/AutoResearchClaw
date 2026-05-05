# Statistical Rigor Review: SemCP v2
**Reviewer:** 04_statistical_rigorist | **Date:** 2026-05-05 | **Confidence:** 3/5

---

## EXECUTIVE SUMMARY

**Verdict:** CONDITIONAL ACCEPT with significant concerns about inference completeness

SemCP is statistically **sound in theorems** but suffers from **critical gaps in empirical validation**:
- Theorems 1–2 are valid conditional on stated assumptions
- Real experiments validate core claims but with **underspecified uncertainty quantification**
- No p-values, confidence intervals, or formal significance tests on coverage/set-size comparisons
- Sample sizes (300 ex/dataset, 3 seeds) adequate for descriptive but insufficient for causal claims
- Effect sizes and variability gaps suggest confounding factors not addressed

**Red Flag:** Authors claim "tightest valid coverage" without formal statistical tests to demonstrate superiority.

---

## STRENGTHS (4/5)

1. **Theorem 1 is mathematically sound with explicit conditions**
   The conditional coverage guarantee 1-α-1/(|I|+1) is properly conditioned on admissibility (true meaning in sampled set). Theorem 1 proof correctly invokes exchangeability under admissibility-selection conditioning → split-conformal → Jensen's marginalization. Authors honestly acknowledge marginal coverage is bounded by p_A. Exchangeability reasoning is subtle and correct—many CP papers get this wrong.

2. **Theorem 2 bandwidth optimization is rigorously derived**
   Sub-Gaussian variance derivation from contrastive RBF scoring. Closed-form σ* from ∂Var/∂σ=0 is valid. Empirically validated: matches grid-search within 5% (Section 5.3). Removes only hyperparameter; eliminates search cost. Concentration bound O(√(log(1/δ)/|I|)) is stated and reasonable.

---

3. **Empirical validity checks show no coverage violations**
   All three datasets show SemCP coverage ≤ theoretical bound (Table 1: -0.007 to +0.021). Achieves conditional coverage tightness within 1–2 percentage points on TriviaQA/SQuAD. Valid across 3 random seeds. No coverage guarantee broken empirically.

4. **Baseline tuning symmetry fixed in v2**
   All methods (ConU, SAFER, LofreeCP, TECP) tuned on same 20% held-out split. v1→v2 improvement: removes baseline asymmetry that could bias comparisons.

5. **M-SemCP unification is theoretically sound**
   Framework recovers ConU, LofreeCP, TECP as corners of τ∈{0.7, 0.5, 0.3} simplex. Generalization is principled, not ad-hoc.

---

## WEAKNESSES (9/10)

### W1 — NO FORMAL SIGNIFICANCE TESTS ON PRIMARY CLAIMS ⚠️ CRITICAL
- **Headline claim:** "SemCP achieves tightest valid conditional coverage"
- **Missing:** No t-test, Wilcoxon, or bootstrapped CI on coverage validity gaps
- **Available data:** Table 1 shows ±std errors (0.896±0.007 TriviaQA), but no pairwise comparison tests
- **Expected:** H₀ tests for coverage gap SemCP vs. each baseline; report p-values
- **Impact:** Cannot distinguish 0.007 TriviaQA gap from noise—headline unsubstantiated
- **Severity:** HIGH

### W2 — INADEQUATE EFFECT SIZE REPORTING
- **Set size increases without Hedges' g/Cohen's d:**
  - TriviaQA: SemCP 1.64 vs ConU 1.00 (+64% larger)
  - SQuAD: 1.14 vs 1.00 (+14%)
  - NQ-open: 3.54 vs 3.92 (-10%)
- **Missing:** Confidence intervals on percentage differences; statistical justification for "acceptable" tradeoff
- **Severity:** MEDIUM

### W3 — MULTIPLE TESTING UNCONTROLLED ⚠️ CRITICAL
- **Comparisons without adjustment:**
  - Coverage gaps: 3 datasets × 3 baselines = 9 tests
  - Set size: 3 datasets × 4 baselines = 12 tests
  - σ̂ vs grid-search: multiple threshold/dataset combinations
  - M-SemCP corner selection: 3 datasets
- **Total:** 24+ pairwise comparisons with α=0.05 per comparison
- **Expected false positives:** ~1–2 among comparisons
- **No mention of:** Bonferroni, FDR, pre-registered primary/secondary outcomes
- **Severity:** HIGH

### W4 — SAMPLE SIZE JUSTIFICATION ABSENT
- **Factual:** 300 examples/dataset, 3 seeds (seed 0,1,2)
- **Missing:** Power analysis or prospective justification for effect size detection
- **Effective n:** 3 seeds × 50 test split = 150 degrees of freedom; quite limited
- **Observed std:** 0.007–0.058 suggests high variance
- **Severity:** MEDIUM

### W5 — CONFIDENCE INTERVALS NOT REPORTED ⚠️ CRITICAL
- **Standard practice:** 95% CI on all point estimates (especially coverage guarantees)
- **Current state:** Point ± std (0.896±0.007) without lower/upper bounds or method
- **Correct approach:** Bootstrap CI or exact Clopper-Pearson for coverage proportions
- **Impact:** Cannot assess whether validity gaps are within acceptable tolerance
- **Severity:** HIGH—essential for probabilistic guarantees

### W6 — ADMISSIBILITY RATE NOT STATISTICALLY MODELED ⚠️ CRITICAL
- **Data:** p_A ranges 0.271 (NQ-open) to 0.811 (SQuAD)
- **Problems:**
  - No binomial CIs on p_A itself
  - No H₀ test on whether p_A differs from uniform baseline
  - NQ-open p_A=0.271 << 1-α=0.9: yet coverage 0.903—contradiction not addressed
- **Root cause:** Depends on NLI model quality (DeBERTa) not validated/sensitivity-tested
- **Severity:** HIGH—confounds interpretation

### W7 — HYPERPARAMETER TUNING NOT FULLY TRANSPARENT
- **Missing:**
  - Exact hyperparameter ranges searched for each baseline
  - Whether computational budget was equal across methods
  - Whether selection criteria were identical (coverage-tightness vs. set-size minimization)
  - Sensitivity: how much do baseline results change with different tuning?
- **Severity:** MEDIUM

### W8 — VARIANCE DECOMPOSITION NOT CHARACTERIZED
- **Observed:** Large set size std errors (SQuAD: 1.14±0.15, 13% relative)
- **Unanalyzed sources:**
  - Qwen sampling randomness (K=10, temp=1.0)
  - NLI clustering stochasticity
  - Calibration set sampling (50% split)
  - Seed effects
- **Impact:** Cannot prioritize improvements; uncertainty attribution unclear
- **Severity:** MEDIUM

### W9 — NO DISTRIBUTIONAL UNCERTAINTY ON THEOREM 2
- **Theorem 2:** σ̂ is optimal, matches grid-search ±5%
- **Missing:**
  - CI on σ̂ itself (how does it vary with calibration perturbation?)
  - Test for H₀: σ̂ = theoretical σ*
  - Empirical validation of variance bound O(√(log(1/δ)/|I|))
- **Impact:** "Plug-in optimal" presented as fact without distributional uncertainty
- **Severity:** MEDIUM

---

## SCORES (1–10, 10=best)

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Originality** | 8 | Novel semantic-aware conformal framework; covers standard methods as M-SemCP special cases. Theorem 1 properly conditions on admissibility (new). |
| **Quality** | 5 | Theorems are sound; empirical validation lacks formal tests, CIs, significance testing. Multiple testing uncontrolled. High variance on set sizes. |
| **Clarity** | 7 | Method/algorithm well-explained; proofs precise. Tables clear but missing standard statistical reporting (CIs, p-values, effect sizes). |
| **Significance** | 6 | Closes algorithm-theory gap (strong). Empirical improvements marginal and not formally tested. Downstream task impact unknown. |

**Average Quality:** 6.5/10 — Sound theory, incomplete empirical validation

---

## CRITICAL QUESTIONS (5+)

**Q1:** How do you justify "tightest valid coverage" headline without significance tests?
- SemCP gap: -0.007 (TriviaQA), +0.010 (SQuAD), +0.012 (NQ-open)
- ConU gap: +0.005, +0.084, +0.109
- Is apparent TriviaQA superiority statistically significant or noise? → **Required:** Paired t-test with p-value, 95% CI on difference

**Q2:** What is statistical power to detect coverage improvements?
- With n=300 (eff n≈150), can you detect 0.02 improvement with 80% power?
- Current stds: 0.007–0.058
- → **Required:** Post-hoc power analysis OR prospective justification

**Q3:** How do you reconcile NQ-open p_A=0.271 with theory claim that p_A<1-α breaks coverage?
- Theorem 1 conditions on "true meaning sampled" but p_A≈0.27 << 0.9
- Yet empirical coverage 0.903—contradiction?
- → **Required:** Formal admissibility analysis; does theorem apply?

**Q4:** Why does Theorem 2 variance bound not vary with |I|, when set sizes vary 1.14–3.54?
- Bandwidth derivation assumes sub-Gaussian, but depends on NLI quality
- How sensitive is σ̂ to NLI model (only DeBERTa tested)?
- → **Required:** Sensitivity on NLI embedding models; alternative models

**Q5:** Are 3 random seeds sufficient? Standard practice: 5–10 seeds.
- → **Required:** Justification for n=3 OR extension to 5+ seeds

**Q6:** What multiple testing correction applied to 24+ comparisons?
- → **Required:** Pre-registered primary/secondary outcomes OR Bonferroni/FDR adjusted p-values

**Q7:** How do baseline hyperparameter ranges compare?
- If ConU has 10 hyperparameters and SAFER has 2, tuning budget matters
- → **Required:** Transparent hyperparameter grids; equal computational budget justification

---

## FALSIFIABILITY TEST

| Claim | Test | Status |
|-------|------|--------|
| Coverage ≤ 1-α-1/(ℐ+1) | All datasets ✓ within bound | **VALID** |
| σ̂ matches grid-search ±5% | Reported match ✓ | **VALID** |
| Contrastive RBF reduces set size vs ConU | Empirical (1.64 vs 1.00 TriviaQA) but no significance test ⚠ | **UNRESOLVED** |
| M-SemCP recovers baselines at τ corners | Framework stated; recovery not empirically demonstrated ⚠ | **UNRESOLVED** |

**Failure modes:**
- If DeBERTa degrades: p_A < 1-α → marginal coverage fails (acknowledged)
- If embedding model changes: σ̂ vs σ* mismatch (untested; critical)
- If admissibility violated: Theorem 1 doesn't hold (NQ-open edge case)

---

## CONFIDENCE: 3/5

**Reducing factors:**
- No p-values/significance tests (−1.5)
- No CIs on coverage guarantees (−0.5)
- Multiple testing uncorrected (−0.5)
- Limited seeds n=3 (−0.5)
- NQ-open admissibility puzzle (−0.5)

**Increasing factors:**
- Theorem proofs sound (+1.0)
- Empirical coverage valid (+1.0)
- Plug-in bandwidth validated (+0.5)

---

## DECISION: CONDITIONAL ACCEPT

**For publication:** Requires addressing statistical gaps before acceptance.

**Mandatory revisions:**

1. **Formal hypothesis tests** (Wilcoxon/t-test, Bonferroni-corrected) on coverage gap and set size differences with p-values, 95% CIs

2. **Report 95% confidence intervals** on all point estimates (bootstrap or exact methods)

3. **Clarify NQ-open admissibility puzzle:** Why does Theorem 1 apply if p_A=0.271 << 0.9?

4. **Extend seeds to n=5+** and re-report error bars (or justify n=3 statistically)

5. **Declare multiple testing control:** Pre-register outcomes or apply Bonferroni/FDR; report adjusted p-values

**Strongly suggested:**

6. Variance decomposition (Qwen sampling, NLI clustering, calibration stochasticity)

7. Sensitivity analysis on NLI embedding models (not just DeBERTa)

8. Post-hoc power analysis for observed effects

9. M-SemCP empirical recovery verification at τ corners

10. Baseline hyperparameter transparency and equal computational budget justification

---

## FINAL REMARKS

SemCP presents solid theory with proper exchangeability handling and sound proofs. Empirical validation demonstrates validity but not superiority—conformal guarantees hold, but claimed advantages lack formal statistical support.

**For NeurIPS acceptance:** Statistical rigor requires significance tests, CIs, multiple testing control, and sensitivity analysis. Current descriptive statistics insufficient.

**Grade as-is:** 6.5/10 (Borderline → Conditional Accept pending revisions)

**Grade post-revisions:** 8/10 (Accept)