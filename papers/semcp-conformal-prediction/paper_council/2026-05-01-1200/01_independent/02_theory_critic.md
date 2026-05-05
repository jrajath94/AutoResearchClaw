# Theory Critic Review — SemCP

**Paper:** SemCP: Coverage Guarantees Over Meanings, Not Strings
**Venue:** NeurIPS 2026
**Reviewer:** The Theory Critic

---

## Summary

This paper proposes SemCP, a conformal prediction framework operating in semantic embedding space rather than token space, using bidirectional NLI to partition outputs into meaning equivalence classes and RBF kernels for nonconformity scoring. The core theoretical contribution is a conditional coverage guarantee (Theorem 1) given an admissibility event. The primary concern is that the paper's central empirical results are TODO_NUM placeholders — the experiments have not been run. This fundamentally undermines the review, as I cannot assess whether the theory is validated. I must also flag an internal contradiction: the paper claims both "near-zero coverage for all methods" (Discussion, Section 7) and "33% smaller set sizes than string-level baseline" (Abstract). The latter claim requires meaningful coverage to be interpretable.

---

## Strengths

1. **Theorem 1 is nontrivial and correctly structured.** The conditional coverage guarantee 1-alpha-1/(|I|+1) given admissibility is a genuine split conformal result. The proof structure (exchangeability + fixed partition rule -> conditional coverage via the augmented tuple view in Remark 2) is sound in principle. The admissibility event decomposition is a useful diagnostic for practitioners.

2. **The quotient-space framing is original.** While conformal prediction over strings is established (Quach 2023, Fisch 2020), the idea of using bidirectional NLI to construct semantic equivalence classes as the conformal space is novel. This is not merely an engineering change — it requires rethinking the nonconformity score and the coverage event. The formalization in Section 4.3 (lifted scores via min-aggregation) is precise.

3. **Remark 1 correctly identifies the marginal coverage ceiling.** The paper acknowledges that p_A (admissibility probability) upper-bounds marginal coverage. This is an honest limitation statement and helps practitioners understand when the method is relevant and deployable.

4. **Section 4.1 correctly argues that Pi is not data-adaptive.** The claim that the deterministic NLI partition preserves exchangeability is correct — as long as the partition function does not depend on the calibration labels. The paper explicitly notes this preservation, which is necessary for Theorem 1 to apply.

5. **Min-aggregation reasoning is principled.** The paper provides a clear justification for min-aggregation: a meaning class should be deemed conforming if any of its string-level representatives conforms. The argument that min biases downward uniformly (affecting calibration and test symmetrically, thus preserving exchangeability) is correct.

---

## Weaknesses

### W1: Experiments Not Run — Central Empirical Claims Are Placeholders
**Issue:** Table 1, Section 5.3, and the 33% set-size-reduction claim (Abstract, Section 7) are TODO_NUM placeholders. Without actual numbers, I cannot verify any empirical claim.
**Location:** Table 1 (all metrics), Section 5.3 (main results), Abstract ("33% smaller set sizes"), Discussion ("33% set size reduction"), Key Claims section.
**Severity:** 5/5 — This is a rejection-level flaw. A paper with unrun experiments cannot be accepted at NeurIPS.
**Resolution:** Run all experiments and report actual numbers with confidence intervals.

### W2: Internal Contradiction — Near-Zero Coverage vs. 33% Set-Size Reduction
**Issue:** The paper simultaneously claims (a) all methods achieve near-zero coverage due to low generator quality (Discussion, Section 7) and (b) SemCP achieves 33% smaller set sizes than Token-CP (Abstract, Key Claims). If coverage is near zero, set size is irrelevant — a trivial predictor (empty set) also has minimum set size. The 33% reduction claim implicitly assumes meaningful coverage.
**Location:** Discussion Section 7 vs. Abstract.
**Severity:** 4/5 — This is a fundamental logical inconsistency. The paper must clarify whether coverage is meaningful enough to evaluate set-size tradeoffs.
**Resolution:** Distinguish between datasets where SemCP achieves useful coverage (where set-size comparison is valid) and datasets where it does not. Report separate analyses.

### W3: Figure 3 Caption / Model Inconsistency
**Issue:** Figure 3 caption states "near-zero coverage for all methods due to GPT-2's limited QA capability," but Section 5.1 specifies the generator is Qwen2.5-7B-Instruct. This is a direct factual error.
**Location:** Fig 3 caption, Section 5.1.
**Severity:** 3/5 — An editorial error that suggests the paper was assembled from multiple drafts without consolidation.
**Resolution:** Correct the caption to Qwen2.5-7B-Instruct or clarify if GPT-2 results are reported separately.

### W4: Kernel Bandwidth Selection May Break Exchangeability
**Issue:** Section 4.2 states sigma is optimized via grid search on a held-out 20% split to minimize set size subject to coverage >= 1-alpha. The conformal guarantee (Theorem 1) assumes the nonconformity score is fixed before calibration. If sigma is selected post-hoc based on calibration-set coverage, exchangeability of the calibrated threshold is not guaranteed. The paper acknowledges a feasibility constraint but does not analyze the effect of this data-dependent selection on coverage.
**Location:** Section 4.2, Algorithm 1.
**Severity:** 3/5 — The theory-lemma gap: Theorem 1 assumes a fixed kernel; the method uses a data-adaptively selected one.
**Resolution:** Either (a) include sigma selection inside the calibration loop with a nested conformal procedure, or (b) prove the grid-search selection does not invalidate exchangeability, or (c) acknowledge this as an empirical heuristic.

### W5: Admissibility Probability p_A Is Unbounded Below — No Finite-N Guarantee
**Issue:** Theorem 1 guarantees conditional coverage given admissibility, but provides no lower bound on p_A. With K=10 samples and complex semantic spaces, p_A could be arbitrarily small. The paper notes this implicitly via "near-zero coverage" but does not bound p_A theoretically.
**Location:** Theorem 1, Remark 1, Section 7.
**Severity:** 3/5 — The guarantee is conditional on an event whose probability is unspecified.
**Resolution:** Provide a lower bound on p_A in terms of K, semantic space complexity, and model's marginal probability of sampling the correct meaning class.

### W6: NLI Threshold Fixed at 0.5, Not Justified
**Issue:** Section 4.1 binarizes bidirectional entailment at 0.5. The Limitations section admits this was not ablated. This is a critical sensitivity parameter: too low and distinct meanings merge; too high and the same meaning fragments.
**Location:** Section 4.1, Limitations item 3.
**Severity:** 3/5 — Without ablation, the method's sensitivity to this threshold is unknown.
**Resolution:** Ablate over threshold values and report sensitivity analysis.

### W7: Theorem 1 Proof Sketch — Admissibility-Selection Effect Is Unresolved
**Issue:** The proof sketch invokes the standard split-conformal result on the lifted scores, but does not address the selection bias introduced by conditioning on the admissibility set I. Here, I is selected post-hoc based on which calibration examples happened to have their true meaning sampled. The threshold is computed over a subset of calibration points that are systematically easier. The paper does not formally argue that exchangeability holds within this subset.
**Location:** Theorem 1 proof sketch, Section 4.4.
**Severity:** 3/5 — A genuine theoretical gap requiring formal justification.
**Resolution:** Explicitly show that conditional on A_i=1 for all i in I, the lifted scores remain exchangeable, or derive the correct coverage correction term for this selection effect.

### W8: NLI Partition Transitivity Is Assumed But NLI Models Are Not Transitive
**Issue:** The paper assumes bidirectional entailment is transitive ("under the assumption that the NLI model is logically consistent"). DeBERTa-v2-xlarge-MNLI is not logically consistent — NLI models are known to have non-transitive behavior. The Union-Find closure can produce equivalence classes that violate actual semantic equivalence.
**Location:** Section 3, Problem Setup.
**Severity:** 2/5 — Theoretical concern; practically, DeBERTa MNLI is fairly robust on this.
**Resolution:** Either prove robustness of coverage guarantee to partition errors, or explicitly bound the partition error probability.

### W9: The "33% Set Size Reduction" Is Meaningless Without Coverage Floor
**Issue:** If coverage is 0%, set size reduction is trivially achieved by predicting the empty set. The 33% figure must come with a coverage floor (e.g., coverage >= 0.90). No such floor is specified in the claim.
**Location:** Abstract, Discussion, Key Claims.
**Severity:** 4/5 — Misleading under the near-zero coverage regime.
**Resolution:** Restate the claim conditional on coverage >= 1-alpha being achieved.

### W10: Code Not Released — Reproducibility Standard Not Met
**Issue:** The NeurIPS checklist states "Code and experiment scripts will be released upon publication." This does not meet the reproducibility standard. Reviewers cannot verify the algorithm as described.
**Location:** NeurIPS checklist, Section 5.1.
**Severity:** 3/5 — NeurIPS standard requires code at review time.
**Resolution:** Release code now, not upon publication.

---

## Per-Rubric-Dimension Scores

| Dimension | Score | Calibration Anchor |
|-----------|-------|-------------------|
| Originality / Novelty | 8 | Genuinely new quotient-space conformal framework; not incremental over prior CP-for-LLM work |
| Soundness | 4 | Theorem 1 has a proof gap (admissibility-selection); kernel optimization unanalyzed; experiments not run — fatal |
| Significance | 6 | If 33% claim holds at meaningful coverage, useful UQ contribution; limited by 2 QA datasets and 7B model |
| Clarity | 6 | Mostly clear; Figure 3 caption error and W2 contradiction hurt |
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