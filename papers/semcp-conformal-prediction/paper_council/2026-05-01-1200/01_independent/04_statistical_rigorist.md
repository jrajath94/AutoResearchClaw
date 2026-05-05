# Statistical Rigorist Review — SemCP

**Paper:** SemCP: Coverage Guarantees Over Meanings, Not Strings
**Reviewer:** The Statistical Rigorist
**Date:** 2026-05-01

---

## Strengths

1. **Theorem 1 is properly stated with conditions made explicit.**
   The conditional coverage guarantee 1-alpha-1/(|I|+1) is conditioned on the admissibility event A = {true meaning in sampled set}. The paper correctly flags that marginal coverage is bounded by p_A (Remark 1). This is honest uncertainty quantification — the authors do not overclaim marginal coverage.

2. **Exchangeability reasoning is correctly applied.**
   Section 4.1 explicitly argues that the fixed partition Pi is NOT data-adaptive, preserving exchangeability. Section 4.4 Remark 2 correctly identifies that sample-dependent scoring preserves exchangeability via the augmented tuple view. These are subtle but important distinctions that many CP papers get wrong.

3. **Admissibility-coverage decomposition is a useful practitioner diagnostic.**
   The separation of p_A (admissibility rate, a property of the generator and sample budget K) from conditional coverage (a property of the scoring rule) gives practitioners a principled way to attribute failure modes. This is a genuinely useful framing.

4. **RBF kernel learning problem is well-specified.**
   Grid search over {0.1, 0.3, 0.5, 1.0, 2.0, 4.0} on a held-out 20% split, minimizing set size subject to coverage >= 1-alpha, is a clear and reproducible specification. The constraint infeasibility caveat (GPT-2 2-3% correct answer rate) is appropriately flagged.

5. **Ablation structure is appropriate.**
   The 5-variant ablation (SemCP-NoM2O, SemCP-Euclidean, SemCP-Adaptive, Naive Semantic, SemCP-Full) targets the right architectural choices. The finding that learned RBF substantially outperforms Euclidean (18.57 vs 13.35 on SQuAD) is a meaningful component decomposition.

---

## Weaknesses

### W1 — ALL EMPIRICAL RESULTS ARE TODO_NUM PLACEHOLDERS
**Issue:** Table 1, Figure 3, and all reported numbers are unfilled placeholders. The paper cannot be evaluated empirically. A 33% set-size reduction is claimed but no actual numbers exist.
**Location:** Section 5.3, Table 1, Figure 3, Appendix
**Severity:** 5/5 (fatal)
**Resolution:** Run all experiments and fill in actual numbers with 95% bootstrap CIs across all 3 seeds.

### W2 — FIGURE 3 CAPTION USES WRONG MODEL
**Issue:** Fig 3 caption says "near-zero coverage for all methods due to GPT-2's limited QA capability" but Section 5.1 specifies experiments use Qwen2.5-7B-Instruct. This is a direct factual inconsistency.
**Location:** Figure 3 caption vs. Section 5.1
**Severity:** 4/5
**Resolution:** Correct the caption to reference Qwen2.5-7B-Instruct, or verify whether a GPT-2 baseline run was also conducted.

### W3 — MARGINAL COVERAGE AND SET SIZE REDUCTION ARE MUTUALLY INCOHERENT AT NEAR-ZERO COVERAGE
**Issue:** The paper claims 33% set size reduction (13.35 vs 19.89 Token-CP on SQuAD). But Section 7 Discussion says "all methods get near-zero coverage due to low generator quality." If coverage is near zero, set size comparisons are meaningless — conformal sets collapse to empty sets regardless of scoring rule. These claims cannot both be true simultaneously.
**Location:** Section 7 vs. Abstract and Key Claim 2
**Severity:** 5/5
**Resolution:** Clarify the coverage regime. If coverage is near zero, the 33% reduction claim must be contextualized or removed. If coverage is meaningful, the near-zero claim must be corrected.

### W4 — NO CONFIDENCE INTERVALS REPORTED FOR ANY RESULT
**Issue:** No standard deviations, CIs, or uncertainty measures are reported for coverage, set size, or any metric. "33% smaller" has no error bars. This makes all comparisons uninterpretable.
**Location:** Throughout Section 5
**Severity:** 4/5
**Resolution:** Report mean ± SD across 3 seeds × bootstrap 1000. Compute 95% CIs for all primary metrics.

### W5 — THREE SEEDS BUT NO MULTI-SEED AGGREGATION DESCRIBED
**Issue:** Section 5.1 specifies 3 seeds (0,1,2) but provides no description of how results are aggregated. Is the reported number the mean across seeds? Median? Best seed? This is a garden of forking paths for the results.
**Location:** Section 5.1
**Severity:** 3/5
**Resolution:** Pre-specify: "We report mean across seeds with 95% bootstrap CI from 3 independent runs."

### W6 — MULTIPLE COMPARISONS ACROSS 5 METHODS × 2 DATASETS WITHOUT CORRECTION
**Issue:** The paper compares 5 methods across 2 datasets. If any informal model selection was done (e.g., bandwidth grid chosen to minimize set size on both datasets), the family-wise error is uncontrolled. No multiple-testing correction is mentioned.
**Location:** Section 5.3 (Table 1)
**Severity:** 3/5
**Resolution:** Report adjusted p-values or at minimum acknowledge the multiple comparisons implicitly made.

### W7 — CODE NOT YET RELEASED
**Issue:** "Code and experiment scripts will be released upon publication" is explicitly stated. The paper cannot be independently verified.
**Location:** Section 9 Conclusion; Appendix NeurIPS Checklist
**Severity:** 3/5
**Resolution:** Release code now, or provide a detailed supplementary with exact hyperparameters, NLI model checkpoint, and embedding model version.

### W8 — NLI THRESHOLD FIXED AT 0.5 NOT ABLATED
**Issue:** DeBERTa-v2-xlarge-MNLI bidirectional entailment threshold is fixed at 0.5 throughout, yet the paper identifies this as a design choice in Limitations (item 3). With 5 kernel bandwidth values × 3 seeds × multiple datasets, the threshold is a significant unexamined variable.
**Location:** Section 4.1, Section 8 Limitations item 3
**Severity:** 2/5
**Resolution:** Run sensitivity analysis over threshold ∈ {0.3, 0.4, 0.5, 0.6, 0.7}.

### W9 — K=10 SAMPLE BUDGET IS LOW FOR RARE MEANING CLASSES
**Issue:** With K=10 samples and NLI partition generating potentially large equivalence classes, many meaning classes will have zero sampled representatives. The paper acknowledges this (classes with no representative get +infinity), but does not quantify how often this occurs. The admissibility rate p_A is the binding constraint on marginal coverage.
**Location:** Section 4.3, Section 5.3 Table 1 (admissibility rate column)
**Severity:** 2/5
**Resolution:** Report the empirical admissibility rate explicitly. If p_A ≪ 0.9, the marginal coverage ceiling is the dominant concern.

### W10 — NO EFFECT SIZE FOR 33% SET SIZE REDUCTION
**Issue:** Key claim: "33% smaller set sizes than string-level baseline on SQuAD." The absolute numbers (13.35 vs 19.89) suggest a difference of 6.54 items. But the denominator is unclear — is this tokens? Meaning classes? The 33% figure without variance makes this claim uninterpretable.
**Location:** Abstract, Section 7 Discussion, Key Claim 2
**Severity:** 3/5
**Resolution:** Report effect size: (19.89 - 13.35) / pooled_SD, with CI. Clarify whether set size unit is tokens or meaning classes.

---

## Per-Rubric Scores

| Dimension | Score | Calibration Anchor |
|-----------|-------|-------------------|
| Originality / Novelty | 7 | Substantial conceptual advance: first CP framework over semantic embedding space with coverage guarantees. The quotient-space formulation is genuinely novel. |
| Soundness | 4 | **Reject trigger.** Theorem 1 is correct, but all empirical results are TODO placeholders. Cannot verify methodology claims without data. The Fig 3/GPT-2 inconsistency further undermines confidence. |
| Significance | 6 | Useful contribution to a niche subfield (conformal prediction for LLMs). 33% set size reduction is potentially impactful if it replicates with proper CIs. |
| Clarity | 6 | Mostly clear. Theorem statements are well-structured. But TODO placeholders, the Fig 3 inconsistency, and the near-zero coverage contradiction hurt clarity. |
| Reproducibility | 3 | **Reject trigger.** Code not released. All numbers are placeholders. Experimental details are specified but cannot be verified. |
| Contextualization vs Prior Work | 7 | Strong coverage of CP-for-LMs literature. ConU, SAFER, LofreeCP, TECP all properly cited and positioned. The relationship to semantic entropy (no coverage guarantee) is correctly identified as gap. |
| Ethical / Broader Impact | 6 | Adequate boilerplate. Legal QA hallucination motivation is concrete but underdeveloped. |

**Weighted Average:** (7×1.0 + 4×1.5 + 6×1.0 + 6×0.7 + 3×1.0 + 7×0.8 + 6×0.5) / (1.0+1.5+1.0+0.7+1.0+0.8+0.5) = (7 + 6 + 6 + 4.2 + 3 + 5.6 + 3) / 6.5 = 34.8 / 6.5 = **5.35**

---

## Pointed Questions for Authors

1. **The near-zero coverage claim (Section 7) directly contradicts the 33% set-size reduction claim (Abstract).** If coverage is near zero, conformal sets collapse to the empty set for all methods, making set size comparisons meaningless. Which is true, and under what conditions? Please provide empirical breakdown of coverage by dataset.

2. **Figure 3 caption references GPT-2, but experiments use Qwen2.5-7B-Instruct.** Was a GPT-2 baseline run conducted? If so, where are those results? If not, why is GPT-2 mentioned?

3. **How exactly are the 3 seeds aggregated?** Mean? Median? Best-of-3? The paper specifies 3 seeds but never states the aggregation rule. If you selected the seed producing the best result, this is a form of reporting bias.

4. **What is the empirical admissibility rate p_A on each dataset?** This is the binding ceiling on marginal coverage. If p_A ≈ 0.5 on TriviaQA and SQuAD, then marginal coverage cannot exceed 0.5 regardless of the scoring rule — this should be the lead result, not buried in Table 1.

5. **The bandwidth grid search minimizes set size subject to coverage >= 1-alpha on a held-out 20% split.** What is the pass rate of this constraint? Section 4.2 mentions it becomes infeasible at very low correct-answer rates. How often was the constraint infeasible in your calibration data? What sigma value was used as default when it failed?

---

## Falsifiability Test

**What evidence would change my decision?**

To move from **Reject** toward **Accept**, I would need to see:

- All TODO_NUM placeholders replaced with actual numbers with 95% bootstrap CIs across 3 seeds
- Marginal coverage ≥ 0.85 (at alpha=0.10) with lower CI bound ≥ 0.80 on both datasets
- Set size reduction with Cohen's d and 95% CI that excludes zero
- Figure 3 caption corrected to match the Qwen2.5-7B-Instruct model
- Admissibility rate p_A explicitly reported as a primary metric
- Code repository link with reproducible experiment scripts

If, after running the experiments, coverage is genuinely near zero (~0.1 or below), I would revise the Significance score to 3/5 and recommend rejection on grounds that the method provides no useful coverage guarantee in practice on these benchmarks.

If the 33% set size reduction is real but only conditional on admissibility, I would recommend revision to clearly separate the two claims and reframe the contribution as a set-size efficiency improvement conditioned on meaningful coverage.

---

## Confidence

**3/5** — The theoretical contribution (Theorem 1, exchangeability arguments, admissibility decomposition) is solid and well-structured. The empirical component cannot be evaluated due to placeholders. I have medium confidence that the method works as claimed, but cannot distinguish signal from noise without actual numbers.

---

## Decision

**Reject (4.0–5.5 weighted average)**

**Primary reason:** The paper's empirical foundation is entirely composed of TODO placeholders. The most critical claims — 33% set size reduction, near-zero coverage, marginal coverage validity — are mutually contradictory and unverifiable. Without experimental data, I cannot assess whether the RBF kernel learning actually helps, whether coverage is meaningful, or whether the 33% figure is real or noise.

**Secondary reason:** The Figure 3 / GPT-2 inconsistency indicates the manuscript was assembled from template text without final consistency checking, raising concerns about review quality more broadly.

**Conditional acceptance path:** If authors run the experiments, fix the contradictions, and demonstrate meaningful conditional coverage (not near-zero) with the kernel-based scoring substantially outperforming frequency-based scoring, I would upgrade to Borderline or Accept depending on effect sizes and CIs.

---

*— The Statistical Rigorist*