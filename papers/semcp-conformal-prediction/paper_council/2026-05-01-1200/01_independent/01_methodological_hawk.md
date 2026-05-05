# SemCP Methodological Review: Experimental Design Rigor, Baseline Fairness, Statistical Confounds

**Persona:** 01_methodological_hawk  
**Review Date:** 2026-05-05  
**Venue:** NeurIPS 2025  
**Paper:** "SemCP: Coverage Guarantees Over Meanings, Not Strings"

---

## STRENGTHS (5)

### 1. **Rigorous Statistical Reporting Across Multiple Seeds**
The paper reports results across 3 random seeds (0, 1, 2) with mean ± standard deviation and bootstrap 95% confidence intervals (1000 resamples). This is solid statistical practice that enables variance estimation. The reporting format makes sampling variability transparent.

### 2. **Explicit Admissibility Decomposition (Honest Failure Mode Admission)**
Rather than hiding the admissibility constraint, the paper transparently reports:
- Marginal coverage = p_A × conditional coverage
- Admissibility rate p_A explicitly stated in results
- Upper bound on marginal coverage directly tied to generator quality

This decomposition clarifies that coverage failure at the marginal level is a sampling problem, not a calibration problem.

### 3. **Fair Baseline Experimental Setup**
All five methods (SemCP, ConU, SAFER, LofreeCP, TECP) use:
- Same generator: Qwen2.5-7B-Instruct
- Same partition: Bidirectional NLI via DeBERTa-v2-xlarge-MNLI
- Same cal/test split (50/50 with seeds 0,1,2)
- Same K=10 samples, temperature=1.0

This isolation of the score function as the differentiating factor is methodologically sound.

### 4. **Theorem 1 States Assumptions Explicitly**
The conditional coverage guarantee is stated with clear assumptions:
- Exchangeability of (X_i, Y_i, S_i)
- Deterministic partition rule π (fixed before data)
- Admissibility conditioning (true meaning must be sampled)

Remarks 1-2 clarify the marginal/conditional relationship and sample-dependent scoring. This is theoretically rigorous.

### 5. **Ablation Studies on Component Contributions**
The paper includes ablations on:
- Kernel choice (RBF vs. Euclidean distance): 13.35 vs. 18.57 on SQuAD
- Many-to-one aggregation (SemCP vs. SemCP-NoM2O): negligible on Qwen
- Naive semantic baseline: 18.83 vs. 13.35

These isolate which components drive the results.

---

## WEAKNESSES (10)

### 1. **CRITICAL: Results Table Entirely Unfilled with Placeholder Values**
**Location:** Table 1 (Main results), lines 284–296  
**Severity:** CRITICAL  
**Issue:** The main results table contains only `TODO_NUM` placeholders for coverage, set sizes, abstention rates, and admissibility rates. The paper claims "real experiments" but all empirical claims are untestable.

**Fix:** Complete all experimental runs and populate Table 1 with actual numbers.

---

### 2. **Hyperparameter Tuning Asymmetry Across Methods**
**Location:** Section 5.1 (Embeddings and kernels), lines 217–218  
**Severity:** HIGH  
**Issue:** The RBF bandwidth σ is explicitly tuned on a held-out 20% split via grid search over {0.1, 0.3, 0.5, 1.0, 2.0, 4.0}, optimizing to minimize set size subject to coverage ≥ 1-α. The paper does not clearly state whether baseline methods (ConU, SAFER, LofreeCP, TECP) undergo equivalent tuning.

**Fix:** Tune all methods equally on the same held-out split, or fix all hyperparameters a priori with sensitivity analysis.

---

### 3. **Admissibility-Induced Calibration Set Shrinkage Not Fully Accounted**
**Location:** Theorem 1, Algorithm 1 (lines 154–186)  
**Severity:** MEDIUM-HIGH  
**Issue:** SemCP calibrates only on admissible examples: I = {i: s̃_i < ∞}. With p_A ≈ 0.7–0.8 and n=250 calibration examples, |I| ≈ 175–200. The discretization correction 1/(|I|+1) ≈ 0.0057 is non-negligible but not analyzed for finite-sample variance of σ̂.

**Fix:** Report |I| explicitly, analyze finite-sample variance of σ̂ and q̂, verify coverage holds with actual discretization correction.

---

### 4. **NLI Equivalence Threshold Not Ablated**
**Location:** Section 5.1 (Semantic partition), lines 215–216  
**Severity:** HIGH  
**Issue:** The NLI binarization threshold is fixed at 0.5 with no ablation. This threshold entirely determines the equivalence classes and thus set sizes. Changes to 0.3 or 0.7 could substantially alter coverage-vs-set-size trade-off.

**Fix:** Ablate NLI threshold ∈ {0.3, 0.5, 0.7} and report sensitivity of coverage and set size.

---

### 5. **Paraphrase Redundancy Metrics Unfilled; M2O Contribution Unclear**
**Location:** Section 5.3 (Key findings), line 301  
**Severity:** MEDIUM  
**Issue:** The paper states "average of TODO_NUM clusters per question on TriviaQA and TODO_NUM on SQuAD." Many-to-one (M2O) aggregation is theoretically justified but empirically unclear. The paper admits "minimal effect" on GPT-2, but actual Qwen results not reported.

**Fix:** Report actual average clusters per question on TriviaQA and SQuAD; compare SemCP vs SemCP-NoM2O and quantify M2O's contribution for Qwen.

---

### 6. **Generator Quality as Lurking Variable; No Robustness Ablation**
**Location:** Section 5.1, Table 1  
**Severity:** MEDIUM  
**Issue:** Admissibility p_A ≈ 0.7–0.8 on TriviaQA/SQuAD for Qwen. No ablation on weaker generators (smaller LLM, lower temperature) to test whether SemCP's kernel-based scoring (the novel contribution) helps robustly or only when p_A is high.

**Fix:** Run experiments on a weaker generator and report p_A and coverage decompositions.

---

### 7. **Calibration Set Size Small; Finite-Sample Effects Not Analyzed**
**Location:** Section 5.1 (Splits and seeds), line 219  
**Severity:** MEDIUM  
**Issue:** 500 examples → 250 calibration → ≈175–200 admissible examples. Bandwidth estimate σ̂ has large variance; grid search over 6 values is coarse. Discretization correction and quantile estimation variance not discussed.

**Fix:** Report 95% CI on σ̂ and q̂; verify coverage holds under finite-sample effects.

---

### 8. **RBF Kernel Choice Unjustified; No Comparison to Alternatives**
**Location:** Section 4.2 (Kernel-based nonconformity scores), lines 124–131  
**Severity:** MEDIUM  
**Issue:** RBF kernel chosen without comparing to Matérn, Laplace, or polynomial kernels. The advantage of RBF is not established.

**Fix:** Compare RBF vs. at least one alternative kernel and report set size and coverage differences.

---

### 9. **Bandwidth Optimization Timing Ambiguity; Potential Train-Test Mismatch**
**Location:** Section 4.2, lines 217–218  
**Severity:** MEDIUM  
**Issue:** Bandwidth optimized on a mixed pool of admissible and inadmissible examples, then applied to calibration set of only admissible examples. If admissibility rate varies by dataset, σ optimized on mixed distribution may not be optimal for admissible-only distribution.

**Fix:** Clarify whether σ optimization is on (a) separate 20% hold-out, (b) 50% of calibration, or (c) both; report impact on finite-sample variance.

---

### 10. **Generalizability Limited to Extractive QA; No Open-Ended Generation**
**Location:** Section 7 (Limitations), lines 365–366  
**Severity:** MEDIUM  
**Issue:** Evaluation only on short factoid QA (TriviaQA, SQuAD). NLI-based partitioning and MiniLM embeddings may not transfer to summarization, dialogue, or code generation where semantic equivalence is ill-defined.

**Fix:** Evaluate on at least one open-ended task (e.g., XSum summarization) and report challenges.

---

## SCORES

| Dimension | Score | Justification |
|-----------|-------|---|
| **Originality** | 7/10 | Quotient-space framing novel; kernel-based NLI scoring combines prior art. Theorem 1 incremental over split-conformal. |
| **Quality** | 5/10 | Theoretical contribution sound; experimental design careful in principle. BUT: results unfilled, hyperparameter tuning asymmetric, design choices unjustified. |
| **Clarity** | 7/10 | Well-written overall. Marred by TODO_NUM placeholders and ambiguities in bandwidth optimization. |
| **Significance** | 6/10 | Addresses real problem (paraphrase redundancy); narrow scope (short QA only); empirical gains unverifiable. |

---

## CRITICAL QUESTIONS (5+)

**Q1: Exchangeability Under Sample-Dependent Scoring**
Remark 2 argues augmenting examples as (X_i, Y_i, {Y_i^(1),...,Y_i^(K)}) preserves exchangeability. But with K=10, does high variance of empirical kernel mean μ_x affect the assumption?

**Q2: Transitivity of NLI Equivalence**
NLI models are not logically consistent. How does NLI intransitivity affect validity of the equivalence relation and coverage guarantee?

**Q3: Admissibility Definition: Reference-Match vs. NLI-Based**
Is admissibility A_i checked via string matching to reference or via NLI equivalence to partition? Does the latter introduce circular dependence on the 0.5 threshold?

**Q4: Why Grid Search Over {0.1, 0.3, 0.5, 1.0, 2.0, 4.0}?**
How sensitive are results to this fixed grid? If true σ* = 0.25 (not in grid), does algorithm incur set-size penalty?

**Q5: Coverage Constraint Binding or Slack?**
Is the coverage constraint "coverage ≥ 1-α on held-out data" binding for all grid values? If slack, kernel choice becomes less critical.

**Q6: Baseline Hyperparameter Tuning Parity**
For ConU, SAFER, LofreeCP, TECP: report whether hyperparameters were (a) fixed a priori, (b) tuned on same held-out split as SemCP, or (c) tuned differently.

**Q7: Admissibility-Stratified Results**
Report results separately for high-admissibility (p_A > 0.75) and low-admissibility (p_A < 0.75) questions. Does SemCP advantage persist in both regimes?

---

## FALSIFIABILITY TEST

**Claim:** "SemCP delivers TODO_NUM% smaller active set sizes than the strongest string-level baseline at matched conditional coverage."

**Falsification Criterion:**
1. Table 1 filled with actual numbers.
2. Let (C_strong - C_sem) / C_strong × 100 = claimed reduction %.
3. If actual reduction < 10%, or if baselines have equal/better set sizes at valid coverage, claim is falsified.

**Current Status:** UNFALSIFIABLE (results not filled).

---

## CONFIDENCE & DECISION

**Confidence: 2/5**

**DECISION: REJECT**

**Reasons:**
1. **Blocker:** Main results table (Table 1) contains only `TODO_NUM` placeholders. Empirical claims are untestable.
2. **Methodological Concerns:**
   - Hyperparameter tuning potentially asymmetric.
   - NLI threshold fixed without ablation (controls equivalence relation).
   - RBF kernel choice unjustified; no alternatives compared.
   - Small calibration set (|I| ≈ 175–200); finite-sample effects not analyzed.
3. **Narrow Scope:** Only short factoid QA; no open-ended generation.

**Path to Acceptance:**
1. Populate Table 1 with complete experimental results.
2. Justify hyperparameter tuning parity or report sensitivity analysis.
3. Ablate NLI threshold (0.3, 0.5, 0.7) and document impact.
4. Compare RBF vs. alternative kernels (Matérn, Laplace).
5. Report |I| explicitly and verify coverage with finite-sample correction.
6. Optionally: include one open-ended task (summarization).

---

**Reviewer:** 01_methodological_hawk  
**Confidence:** 2/5  
**Overall Assessment:** Reject (unfilled results + methodological confounds)

