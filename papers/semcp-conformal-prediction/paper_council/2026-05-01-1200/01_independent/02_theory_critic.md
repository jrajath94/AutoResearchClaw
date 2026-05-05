# THEORY CRITIC REVIEW: SemCP v2
**Venue:** NeurIPS 2025 | **Date:** 2026-05-05 | **Persona:** 02_theory_critic

---

## EXECUTIVE SUMMARY

SemCP proposes semantic conformal prediction for LLMs by partitioning outputs into meaning equivalence classes (HAC-NLI clustering) and applying CP with a contrastive between-cluster RBF kernel. The paper claims Theorem 1 (conditional coverage 1-α-1/(|I|+1)) and Theorem 2 (closed-form optimal bandwidth σ*). **Verdict: Empirically validated on TriviaQA but with significant proof gaps, clustering robustness concerns, and a critical admissibility bottleneck (p_A) that limits practical utility.**

---

## STRENGTHS (3)

### 1. **Clear Problem Formulation & Motivation**
The semantic-vs-string-space distinction is well-articulated and important. Standard CP on LLM samples treats "the capital of France is Paris" and "Paris is the capital of France" as distinct, inflating set sizes artificially. Semantic coverage is a genuine and under-explored problem in the CP literature.

**Supporting evidence:** v1→v2 improvements table explicitly traces all feedback, showing systematic problem-solving rather than ad-hoc patching.

### 2. **Theorem 1 Empirical Validation on TriviaQA**
Achieves coverage 0.896±0.007 vs predicted bound 1-α-1/(|I|+1)≈0.891. Gap of -0.007 is remarkably tight, suggesting the theoretical construction aligns with practice on at least one real dataset.

**Concern:** Tightness only validated on 1 of 3 datasets (SQuAD ±0.058 interval, NQ-open valid but not exceptionally tight). Overstating as "tightest valid coverage" without caveating dataset variability.

### 3. **Removes Conformal Hyperparameter Tuning**
Theorem 2's closed-form bandwidth σ* = √((μ̄μ-μ̄W)/(2log(1/(1-α)))) claims to eliminate grid search for σ. If proven correctly, this simplifies the method and improves reproducibility. Claimed "within 5% of grid search" (Appendix E, not shown in bundle).

**Caveat:** Proof and constants (sub-Gaussian parameter K) not detailed in bundle; generalization to other kernels/contrastive scores unclear.

---

## WEAKNESSES (8)

### 1. **Theorem 1 Proof Rigor: Exchangeability Given Clustering**
**Critical gap:** The proof structure claims "exchangeability under admissibility-selection conditioning," but doesn't formally address: **If HAC-NLI clustering has error rate ε_cluster (false negatives: semantically identical outputs in different clusters), how does this propagate to coverage?**

Conformal prediction's coverage guarantee assumes score exchangeability. If clustering places two semantically identical outputs {y₁, y₂} into separate clusters c₁, c₂, then:
- They become separate *distinct* elements in the partition Π(S)
- CP guarantees apply individually to c₁ and c₂, not to the meaning {y₁, y₂}
- The coverage theorem's implicit assumption that "true meaning is sampled" breaks

**Impact:** Without bounding ε_cluster or proving it's negligible, the coverage guarantee is conditional on an unvalidated assumption. This is the **highest-priority theoretical weakness**.

### 2. **Theorem 2: Undefined Notation & Missing Sub-Gaussian Constants**
**Issue:** The formula σ* = √((μ̄μ-μ̄W)/(2log(1/(1-α)))) uses undefined terms:
- What is μ̄μ exactly? (between-cluster mean pairwise distance?)
- What is μ̄W? (within-cluster mean distance? Zero if singleton?)
- Sub-Gaussian parameter K for RBF kernel not specified

The variance minimization derivation ∂Var_σ(s̃)/∂σ=0 is stated but not shown. For a contrastive score s̃(X,C,S,σ) = 1 - max_c' κσ(φ̄c, φ̄c'), the variance of the max of correlated RBF kernels is complex and requires explicit handling.

**Impact:** Difficult to verify Theorem 2 or to extend the formula to other contrastive scores or kernels. Concentr. bound O(√(log(1/δ)/|I|)) mentioned but not tied to the final σ* formula.

**Evidence gap:** Grid search validation mentioned (Appendix E) but not provided in bundle. "Within 5%" is vague—on which datasets? How was grid search tuned?

### 3. **Admissibility as Implicit Performance Ceiling**
**Major practical constraint:** Admissibility rates p_A on NQ-open (0.271) and TriviaQA (0.707) reveal that the method's coverage is **fundamentally bottlenecked by generator quality**, not algorithm design.

Marginal coverage ≤ p_A + (1-p_A)·(1-α) ≈ p_A + (1-p_A)·0.9 (assuming α=0.1).

For NQ-open: max achievable coverage ≤ 0.271 + 0.729·0.9 ≈ 0.928. Observed SemCP 0.903, which aligns perfectly.

**Problem:** The paper acknowledges "if p_A < 1-α, marginal coverage unattainable" (Limitation) but doesn't emphasize that on NQ-open, p_A=0.271 is the *actual* performance ceiling. The algorithm can't improve coverage beyond what the generator provides. This makes the empirical improvements on NQ-open (3.54 vs 3.92 set size) marginal and potentially within noise.

**Paper's framing:** "Invest in generator" is appropriate but sidesteps the question: *Is SemCP adding value when p_A is the bottleneck?* Ablating generator quality (e.g., Qwen2.5-32B vs. 7B vs. Llama) would clarify.

### 4. **Clustering Robustness Not Analyzed**
HAC-NLI with "transitivity-corrected" clustering is mentioned as O(K log K), but:
- No empirical validation of clustering quality (precision/recall on semantic equivalence)
- No sensitivity test: if NLI model corruption is introduced, how degraded is coverage?
- Single embedding model (gte-Qwen2-7B); appendix D mentions sensitivity check but details omitted

**Risk:** If clustering is unreliable, the whole semantic coverage framework collapses. This deserves ablation.

### 5. **M-SemCP Unification is an Observation, Not a Theorem**
**Claim:** "M-SemCP recovers ConU, LofreeCP, TECP as special cases by varying τ ∈ {0.7, 0.5, 0.3}."

**Problem:** 
- No formal proof that τ=0.7 exactly recovers ConU (would require showing algorithm reduces to ConU with proof)
- No ablation showing M-SemCP performance vs individual τ values
- Statement that M-SemCP "frequently selects single granularity (corner of simplex)" suggests these are actually *different* algorithms, not the same algorithm with different parameters

**Evidence gap:** Table 1 shows only SemCP, ConU, SAFER, LofreeCP, TECP—no M-SemCP results. Without empirical comparison, the unification claim is conceptual, not validated.

**Impact on novelty:** If the unification is true but unproven, the paper undersells its theoretical contribution. If it's false (i.e., M-SemCP is just ConU with Pr > 0.7), the generality claim is inflated.

### 6. **Baseline Inconsistencies: ConU |C|=1.00 on TriviaQA/SQuAD**
ConU consistently outputs |C|=1.00 on TriviaQA and SQuAD, while SemCP outputs 1.64 and 1.14 respectively.

**Possible explanations (not addressed):**
1. ConU is not tuned correctly (but paper says "all tuned on 20% held-out")
2. ConU degenerates to always selecting a single element on these datasets
3. ConU and SemCP are scoring different objects (strings vs meanings), so comparison is inherently unfair

Without clarity, it's unclear whether SemCP's larger sets represent a fair trade-off (larger sets for semantic coverage) or a measurement artifact.

### 7. **Limited Experimental Scope: K=10, Single LLM, Single Embedding**
- **K=10:** Only 10 samples per question. For high-entropy queries (e.g., "list movies in the 1990s"), 10 may not capture the output distribution. Ablation in Appendix E (mentioned, not shown) should clarify impact.
- **Single LLM:** Qwen2.5-32B only. Generalization to Llama 3, GPT-4, smaller models (where clustering may fail due to output repetition) unexplored.
- **Single embedding model:** gte-Qwen2-7B. What about BAAI/bge, OpenAI text-embedding-3? Appendix D sensitivity check mentioned but not detailed.

**Impact:** Claims about SemCP's superiority may not generalize beyond this specific experimental regime.

### 8. **Proof Completeness: Appendices Referenced but Not Provided**
The bundle references:
- **Appendix B:** Theorem 1 proof (3-step outline given, full derivation absent)
- **Appendix C:** Theorem 2 variance derivation and concentration bounds (absent)
- **Appendix D:** Embedding sensitivity analysis (absent)
- **Appendix E:** K ablation and bandwidth validation (absent)

A review can only assess what's presented. Assuming correctness of appendices that aren't shown is a risk. The Theorem 1 proof outline is too compressed to verify rigor of exchangeability argument.

---

## QUANTITATIVE SCORES (1-10 scale)

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Originality** | 7 | Clear problem (semantic CP), valid technical approach (clustering + contrastive scoring). Prior art comparison weak (no ConU/TECP derivations shown for comparison). |
| **Quality** | 6 | Theorem 1 empirically validated on TriviaQA (strong), but Theorem 2 proof incomplete, clustering robustness unanalyzed, proof rigor gaps. Experiments real but limited scope (K=10, 1 LLM). |
| **Clarity** | 6 | Algorithm 1 is clear, main results understandable. But Theorem 2 notation (μ̄μ, μ̄W) undefined; Appendices critical but absent; M-SemCP motivation vague; baseline inconsistencies unexplained. |
| **Significance** | 5 | Semantic coverage is important, but practical utility limited by p_A bottleneck. On NQ-open (p_A=0.271), marginal gains are incremental. Unification (M-SemCP) could be significant if proven, but isn't yet. |

---

## CRITICAL QUESTIONS (5+)

### Q1: Clustering Error Propagation [HIGHEST PRIORITY]
*How does the false-negative rate of HAC-NLI clustering (semantically identical outputs in different clusters) impact the coverage guarantee? Specifically, if ε_cluster is the clustering error rate, what is the breakdown of coverage guarantee into:*
- *Coverage from algorithm (Theorem 1)*
- *Coverage loss from clustering errors*

*Can you provide a bound or empirical measurement of ε_cluster on your test set?*

### Q2: Theorem 2 Notation & Derivation
*In σ* = √((μ̄μ-μ̄W)/(2log(1/(1-α)))):*
- *Define μ̄μ and μ̄W precisely (as functions of embedding clusters φ̄c, φ̄c'?)*
- *What is the sub-Gaussian parameter K in the RBF kernel?*
- *Is this formula specific to the contrastive RBF score, or does it generalize to other contrastive kernels?*

### Q3: M-SemCP Unification Proof
*Provide formal statements (with proofs) that:*
- *M-SemCP with τ=0.7 (or corresponding weight vector) recovers ConU exactly*
- *Similarly for τ=0.5→TECP, τ=0.3→LofreeCP*
- *Or clarify that these are "inspired by" rather than "recover" these methods.*
- *Show M-SemCP performance (coverage/set size) vs individual methods.*

### Q4: Admissibility Bottleneck Ablation
*On NQ-open with p_A=0.271, what is the coverage improvement if:*
- *Generator quality is increased (e.g., Qwen2.5-72B instead of -32B)?*
- *More samples K are used (K=20, K=50)?*
- *This clarifies whether SemCP's utility on low-p_A datasets is real or marginal.*

### Q5: Baseline Fairness
*ConU yields |C|=1.00 consistently on TriviaQA/SQuAD while SemCP yields 1.64/1.14. Either:*
- *ConU is broken on these datasets (proof of tuning procedure?)*
- *ConU and SemCP optimize different objectives (string vs semantic), making comparison unfair*
- *Explain the discrepancy and adjust headline claims accordingly.*

### Q6: Generalization Beyond Qwen2.5-32B
*Provide results on:*
- *Llama 3 (or another recent open model)*
- *A smaller model (7B) to test scaling*
- *GPT-4 (closed-box, but establishes applicability)*
- *Current scope (single LLM) is insufficient for a method paper.*

### Q7: NLI Model Sensitivity (Appendix D Details)
*You mention "sensitivity checked in Appendix D." Provide results comparing:*
- *gte-Qwen2-7B (current)*
- *BAAI/bge-large-en-v1.5 or OpenAI text-embedding-3-large*
- *What's the coverage/set size variance across embedding models?*

---

## FALSIFIABILITY TEST

### Falsifiable Theorem Claims
✅ **Theorem 1:** Conditional coverage = 1-α-1/(|I|+1)
- **Test:** On calibration set I, count elements scoring ≤ q̂; check empirical coverage
- **Result:** TriviaQA passes (0.896 vs 0.891), SQuAD/NQ-open valid but less tight
- **Status:** Partially falsified (only tight on 1/3 datasets; looseness on others not explained)

✅ **Theorem 2:** σ* matches grid-search within 5%
- **Test:** Run grid search on held-out set; compare empirical optimal σ_grid to σ*
- **Result:** Claimed in Appendix E (not shown); cannot verify
- **Status:** Unverifiable from bundle (appendix missing)

✅ **Set Size Claim:** "SemCP produces comparable or smaller sets"
- **Test:** Compare |C| across methods
- **Result:** True on NQ-open (3.54 vs 3.92), but false or unclear on TriviaQA/SQuAD vs ConU
- **Status:** Partially falsified (ConU baseline inconsistency)

### Non-Falsifiable/Observation Claims (Not Theorems)
❌ **"Contrastive RBF captures semantic distinctness better"** — Qualitative, no metric
❌ **"M-SemCP recovers prior methods as corners"** — Stated as observation not theorem; no formal proof provided
❌ **"HAC-NLI with transitivity correction is superior"** — No comparison to k-means, spectral clustering

---

## CONFIDENCE ASSESSMENT

**Overall confidence in correctness: 3/5 (Medium)**

### Breakdown by Component
| Component | Confidence | Notes |
|-----------|-----------|-------|
| **Theorem 1 (Coverage guarantee)** | 4/5 | Empirically validated on TriviaQA, but proof gap on clustering error; SQuAD/NQ-open valid but loose |
| **Theorem 2 (Bandwidth formula)** | 2/5 | Notation undefined, derivation not shown, sub-Gaussian constants absent; cannot verify |
| **HAC-NLI algorithm** | 3/5 | Clustering quality not validated; robustness to embedding/NLI model errors unclear |
| **M-SemCP unification** | 1/5 | Stated as observation not theorem; no formal proofs or empirical comparison provided |
| **Experimental results** | 4/5 | Real datasets, proper splits, reproducible (though compute-intensive); limited scope (K=10, 1 LLM, 1 embedding) |

### Key Uncertainties
1. **Clustering impact (±2 points):** If clustering error >> signal, whole approach fails
2. **Theorem 2 applicability (±1 point):** If proof has gaps, bandwidth may not be truly optimal
3. **Generalization (±1 point):** Limited to Qwen2.5, gte-Qwen2, specific datasets; unknown on other LLMs/models

---

## DECISION & RECOMMENDATIONS

### Recommendation: **CONDITIONAL ACCEPT** with major revisions

**Rationale:**
- ✅ Addresses real problem (semantic CP) with novel approach
- ✅ Theorem 1 empirically tight on TriviaQA
- ✅ Real experiments (v1→v2 improvement)
- ❌ Theorem 2 proof incomplete; Theorem 1 proof has gap on clustering error
- ❌ M-SemCP unification is observation, not theorem
- ❌ Limited experimental scope; baseline inconsistencies
- ❌ p_A bottleneck severely limits practical utility

### Required Changes for Acceptance
1. **[CRITICAL]** Analyze clustering error propagation: Bound or measure ε_cluster and its impact on coverage. This is the paper's foundational assumption.

2. **[CRITICAL]** Complete Theorem 2 proof: Define μ̄μ, μ̄W; provide sub-Gaussian bounds; show derivation of σ*. Include Appendix C in submission.

3. **[MAJOR]** Clarify M-SemCP unification: Either prove it rigorously (Appendix B') or reframe as an "inspired by" observation, not a recovery. Include empirical M-SemCP results in Table 1.

4. **[MAJOR]** Generalization experiments: Provide results on ≥1 additional LLM (Llama 3, 7B model, or GPT-4) and ≥1 additional embedding model. Appendices D & E must be included.

5. **[MODERATE]** Explain baseline anomaly: Why ConU |C|=1.00 on TriviaQA/SQuAD? If unfair comparison, adjust headline claims.

6. **[MODERATE]** p_A bottleneck ablation: Show how coverage scales with K, LLM size, etc. Clarify practical utility on low-p_A datasets.

### Strength if Revised
With these revisions, the paper would be a solid methodological contribution: semantic CP is novel, Theorem 1 is validated, Theorem 2 removes hyperparameter, and real experiments (properly generalized) would be convincing.

---

## SUMMARY TABLE

| Aspect | Status | Evidence |
|--------|--------|----------|
| **Problem importance** | Strong | Semantic vs string-space distinction well-motivated |
| **Theorem 1 validity** | Medium | Tight on TriviaQA (gap -0.007), loose on NQ-open (+0.012); clustering error impact unanalyzed |
| **Theorem 2 completeness** | Weak | Formula stated; derivation & constants missing |
| **Algorithm clarity** | Good | HAC-NLI and contrastive score well-described, but robustness not validated |
| **Experimental rigor** | Medium | Real datasets, proper methodology; limited scope (K=10, 1 LLM) |
| **Claim-evidence alignment** | Medium | Main results shown; appendices (proofs, ablations) absent; M-SemCP unproven |
| **Falsifiability** | Good | Core theorems are testable; claimed validations (Appendices D-E) not provided |

---

**Review Date:** 2026-05-05  
**Reviewer Persona:** 02_theory_critic (Mathematical Rigor & Proof Completeness)
| Reproducibility | 2 | Code not released; all empirical results are TODO_NUM placeholders; cannot be reproduced |
| Contextualization vs Prior Work | 7 | Strong coverage of CP for LMs; correctly positions SemCP vs ConU/SAFER/LofreeCP/TECP |
| Ethical / Broader Impact | 6 | Generic boilerplate; adequate but not thoughtful |

**Weighted Average:** (8x1.0 + 4x1.5 + 6x1.0 + 6x0.7 + 2x1.0 + 7x0.8 + 6x0.5) / 6.5 = (8 + 6 + 6 + 4.2 + 2 + 5.6 + 3) / 6.5 = 34.8 / 6.5 = **5.35 — Borderline to Reject**

---

## Pointed Questions for the Authors

1. **Theorem 1 (exchangeability under admissibility selection):** The threshold qhat is computed as the quantile over the admissibility subset I = {i: A_i = 1}. But I is selected based on which calibration examples happened to have their true meaning sampled — a random event correlated with the calibration labels. Standard split-conformal requires the calibration set to be fixed independently of threshold computation. Please justify formally why computing qhat over the post-hoc selected subset I does not break the exchangeability argument. If it cannot be justified, Theorem 1's coverage guarantee does not hold for the implemented algorithm.

2. **W2 (contradiction):** The paper simultaneously claims "33% set size reduction" and "near-zero coverage for all methods." If coverage is near zero, any trivial predictor (empty set) also achieves minimum set size. Please resolve: Is coverage meaningful on SQuAD or not? If coverage < 1-alpha, what does the 33% reduction claim refer to?

3. **W4 (kernel adaptation):** In Section 4.2, sigma is grid-searched on a held-out 20% calibration split to minimize set size subject to coverage >= 1-alpha. Theorem 1 assumes the kernel is fixed. How does the data-dependent sigma selection interact with the conformal calibration threshold? Does the coverage guarantee still hold? If not, does the paper have a theoretical analysis of the deviation?

4. **W5 (p_A lower bound):** What is your theoretical lower bound on p_A? With K=10 samples and complex semantic spaces, p_A could be near zero. Empirically, what fraction of SQuAD/TriviaQA examples have p_A >= 0.9? If p_A is low for most examples, Theorem 1 provides a guarantee for a rare event that is uninformative for practitioners.

5. **Figure 3 caption:** The caption references "GPT-2" but Section 5.1 specifies "Qwen2.5-7B-Instruct." Which model generated the data shown in Figure 3? Was any experiment run with GPT-2, or is this a copy-paste error from a prior draft?

6. **NLI threshold (0.5):** DeBERTa-v2-xlarge-MNLI outputs probabilities. What is the empirical distribution of bidirectional entailment scores for true positives (same meaning, different surface forms) vs. false positives (different meaning, high surface overlap)? How sensitive is the partition to the 0.5 threshold?

7. **NLI partition transitivity:** The Union-Find closure assumes transitivity of bidirectional entailment. DeBERTa MNLI is not logically consistent. Can you construct an example where A entails B, B entails C, but A does not entail C? What is the effect on the coverage guarantee when the partition places two strings in different classes when they share a meaning?

---

## Falsifiability Test

**What evidence would change my decision?**

If **Strong Accept**: Theorem 1 uses a genuinely novel proof technique; experiments run and confirm 33% set-size reduction at coverage >= 1-alpha; code released; p_A is bounded away from zero for realistic domains; the admissibility-selection proof gap is formally resolved.

If **Strong Reject**: Theorem 1 contains a proof error (admissibility-selection breaks exchangeability); or experiments reveal that coverage is <50% on SQuAD/TriviaQA even with SemCP, making the conformal guarantee vacuous; or the NLI partition collapses into a single class for >90% of examples.

**Specific falsification condition for Theorem 1:** Construct a counterexample where the true meaning is in the sampled set (admissibility holds) but conditional coverage < 1-alpha-1/(|I|+1). If such a counterexample exists, Theorem 1 is false.

**Specific falsification condition for the 33% claim:** If coverage on SQuAD is below 0.80 (the nominal 1-alpha) for SemCP, the 33% set-size reduction is not meaningful — a degenerate predictor (always predict all classes) would also "reduce" set size relative to a baseline that predicts all strings.

---

## Confidence

**4/5** — I am highly confident in the theoretical analysis (Theorem 1 is structurally sound but has an unresolved admissibility-selection gap) and highly confident that the experiments are not run (TODO_NUM placeholders are explicit). I am moderately confident in the internal contradiction analysis (the paper's own text is self-contradictory on coverage). I have lower confidence on W4-W5 because I am evaluating based on incomplete experimental data.

---

## Decision

**Borderline (leaning toward Reject)**

**Reasoning:** The theoretical contribution (Theorem 1 + quotient-space conformal framework) is genuine and novel, earning a 7-8 on originality. However, the Soundness score is driven to 4 by two fatal issues: (1) the experiments are not run, making the primary empirical claims unfalsifiable at review time, and (2) there is an internal contradiction between the near-zero coverage claim and the 33% set-size reduction claim. I cannot recommend acceptance of a paper where the central empirical results are placeholders and where the paper simultaneously asserts that those results are near-zero.

If the experiments are run and the 33% reduction holds at coverage >= 0.90, with the internal contradiction resolved and the admissibility-selection proof gap addressed, I would upgrade to **Accept**.

**— The Theory Critic**