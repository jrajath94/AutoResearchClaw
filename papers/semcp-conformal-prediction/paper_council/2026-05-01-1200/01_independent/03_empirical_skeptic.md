# Review — The Empirical Skeptic

**Paper:** SemCP: Coverage Guarantees Over Meanings, Not Strings
**Reviewer:** The Empirical Skeptic
**Date:** 2026-05-01

---

## Summary

Theoretical framework with an interesting quotient-space conformal prediction idea, but **all empirical results are TODO_NUM placeholders**. I cannot assess generalization claims from numbers that do not exist. The paper is not ready for review in its current state.

---

## Strengths

1. **Quotient-space conformal framing is original and theoretically sound.** Theorem 1 correctly derives conditional coverage 1-alpha-1/(|I|+1) given the admissibility event. The exchangeability preservation argument through per-instance application of a fixed partition rule is valid and non-trivial. (Section 4.4, Theorem 1 proof sketch, Remark 2)

2. **Admissibility-coverage decomposition is a genuinely useful diagnostic.** Reporting p_A alongside coverage explicitly is good practice. It makes transparent that marginal coverage is ceiling-limited by sampling quality, not calibration quality. This is a point the field has underappreciated. (Remark 1, Section 5.3 analysis)

3. **RBF kernel scoring vs. Euclidean distance ablation is meaningful.** The claim that learned kernels substantially outperform raw embedding distance (13.35 vs. 18.57 on SQuAD) isolates a real contribution — semantic partitioning alone is insufficient; geometry-aware scoring matters. (Section 6, Fig 4)

4. **Cross-method theoretical positioning is clear.** The paper correctly situates its conditional coverage guarantee within the ConU/SAFER/LofreeCP conditioning paradigm, and explicitly acknowledges that SemCP's semantic lifting is complementary to (not competitive with) these sampling-conditioning mechanisms. (Section 4.4 Remark 1, Discussion)

5. **Limitations section is honest and specific.** Six explicit limitations are named, including model scale, benchmark scope, NLI threshold sensitivity, and missing downstream evaluation. This level of specificity is rare and appreciated.

---

## Weaknesses

### W1: ALL EXPERIMENTAL RESULTS ARE PLACEHOLDERS (CRITICAL)
- **Issue:** Table 1 contains exclusively TODO_NUM entries. The abstract's central empirical claim ("33% smaller set sizes") has no supporting evidence in the submitted artifact.
- **Where:** Table 1 (all rows), Abstract ("SemCP delivers TODO_NUM% smaller active set sizes"), Section 5.3 analysis referencing numbers that don't exist.
- **Severity:** 5/5 — A paper without experiments cannot be reviewed for empirical validity.
- **Resolution:** Run the experiments and populate Table 1 with real numbers before review.

### W2: Figure 3 Caption References Wrong Model
- **Issue:** The caption states "near-zero coverage for all methods due to GPT-2's limited QA capability" but Section 5.1 specifies Qwen2.5-7B-Instruct. These are different models with different capability profiles.
- **Where:** Figure 3 caption; inconsistent with Section 5.1 experimental setup.
- **Severity:** 4/5 — An incorrect caption raises questions about what else was copy-pasted without verification. The near-zero coverage claim is also in serious tension with the 33% set-size-reduction claim (you cannot measure set size reduction if coverage is near-zero).
- **Resolution:** Correct the caption; reconcile the near-zero coverage discussion with the set-size claims.

### W3: 33% Set Size Reduction Claim Is Internally Inconsistent
- **Issue:** The Discussion (Section 7) claims "33% reduction in prediction set size on SQuAD (13.35 vs. 19.89 for Token-CP)" but the ablation section (Section 6) reports "SemCP-Euclidean: 18.57" as the alternative kernel method. There is no "19.89 Token-CP" number in any table.
- **Where:** Section 7; referencing numbers not present in Table 1 or any experimental section.
- **Severity:** 4/5 — The paper's central empirical contribution is stated with specific numbers that appear to be fabricated or referenced from a different version of the manuscript.
- **Resolution:** Either produce the actual comparison number or remove the claim.

### W4: Single-Model, Single-Scale Evaluation Limits Generalization Assessment
- **Issue:** All experiments use Qwen2.5-7B-Instruct. No scaling study. No frontier model evaluation. The 33% set-size reduction claim could be model-specific.
- **Where:** Section 5.1 (generator), Section 7 (Discussion), Limitations (first bullet).
- **Severity:** 3/5 — The paper acknowledges this limitation, but the primary claim ("SemCP delivers smaller sets") is made without demonstrating across scales. Good methods should show consistency across model sizes.
- **Resolution:** Evaluate at 1B, 7B, and 70B scales to test whether set-size advantage is robust to generator quality.

### W5: N=250 Cal/Test Split Per Seed Is Small for Coverage Estimation
- **Issue:** With N=500 total and 50/50 split, calibration set size is ~250. At alpha=0.10, the quantile correction term 1/(|I|+1) is ~1/250 ≈ 0.004, which is non-trivial relative to the target gap of 0.10. At this calibration size, the 95% CI on coverage is approximately ±0.04 (binomial SE for p≈0.90 with n=250: sqrt(p(1-p)/n) ≈ 0.019). The CI width (±0.038) overlaps the margin of error.
- **Where:** Section 5.1 splits; Section 5.3 analysis.
- **Severity:** 3/5 — Not fatal, but the paper should be more cautious about coverage claims at this sample size. The reported conditional coverage "should reach approximately 0.89" is a theoretical target, not an empirically verified fact.
- **Resolution:** Larger calibration sets (N=1000+) or explicit acknowledgment that coverage estimates at N=250 have wide CIs.

### W6: K=10 Is Underspecified for High-Entropy Queries
- **Issue:** K=10 samples per prompt. For TriviaQA-style factoid questions, K=10 may be sufficient. For open-ended generation (the motivation in Introduction), K=10 is almost certainly insufficient. The paper does not test the method on genuinely open-ended tasks where semantic equivalence is harder to define.
- **Where:** Section 5.1 (K=10), Limitations (sample budget), Introduction (motivation includes open-ended generation).
- **Severity:** 2/5 — Acknowledged in limitations, but the motivation section overclaims generality for a method tested only on closed-form QA.
- **Resolution:** Test on at least one open-ended generation task (summarization, dialogue) to justify the broader claims.

### W7: Kernel Bandwidth Selection Uses Coverage Constraint That May Be Infeasible
- **Issue:** Section 4.2 states the bandwidth optimization "can only be satisfied when the generator produces correct answers at a non-trivial rate" and "the constraint is infeasible because correct answers appear for only 2-3% of questions." The paper says this for GPT-2, but with Qwen2.5-7B-Instruct (Section 5.1) this feasibility is not verified — and if the constraint is infeasible at Qwen's 7B scale, the entire kernel optimization story collapses.
- **Where:** Section 4.2 (caveat paragraph), Algorithm 1 step calibration loop.
- **Severity:** 4/5 — If the constrained optimization is infeasible at Qwen-7B scale, sigma defaults to the value that "minimizes set size without achieving the coverage target." This means the kernel is not actually optimized for coverage — only for set size. This fundamentally changes the interpretation of the learned kernel result.
- **Resolution:** Report the feasibility rate of the coverage constraint for Qwen2.5-7B-Instruct. If infeasible, clarify what "optimization" actually selected sigma.

### W8: Abstract Claims vs. Limitations Section Contradiction
- **Issue:** The Abstract says "SemCP delivers TODO_NUM% smaller active set sizes than the strongest string-level baseline." The Limitations section says "Downstream applications not evaluated." If the method's main value is downstream (selective abstention, RAG), and those are not evaluated, the abstract claim overstates the demonstrated utility.
- **Where:** Abstract (claim of smaller set sizes), Limitations (no downstream evaluation), Introduction (applications motivating the work).
- **Severity:** 3/5 — The paper builds motivation around applications that are never experimentally validated.
- **Resolution:** Align the abstract claim with what is actually demonstrated (set sizes on synthetic benchmarks, not downstream utility).

### W9: No Comparison to Semantic Entropy Baseline
- **Issue:** The paper motivates SemCP partly by noting that "semantic entropy has no coverage guarantee" (Section 2). However, no semantic entropy baseline appears in the experiments. This leaves the comparison incomplete — SemCP's advantage over semantic entropy is theoretical, not empirical.
- **Where:** Section 2 (motivation), Section 5.2 (baselines).
- **Severity:** 2/5 — The paper acknowledges semantic entropy as a motivation but does not compare against it.
- **Resolution:** Add semantic entropy as a baseline for set size comparison, even if coverage cannot be guaranteed.

### W10: Code Not Released; "Code to Be Released Upon Publication"
- **Issue:** The NeurIPS checklist states "code and experiment scripts will be released upon publication." This means the paper cannot be independently verified by reviewers or readers.
- **Where:** Section 5.1 (hardware), NeurIPS checklist item 5, Abstract.
- **Severity:** 2/5 — Reproducibility score is limited by non-release. Acknowledged, but counts against the paper.
- **Resolution:** Release code and configs now, not after publication.

---

## Per-Rubric Dimension Scores

| Dimension | Score | Calibration Anchor |
|---|---|---|
| Originality / Novelty | 7 | Substantial conceptual advance; quotient-space CP for semantic meanings is a new framing that combines existing ideas non-obviously |
| Soundness | 3 | CRITICAL: No experimental results exist; methodology cannot be assessed empirically; Theorem 1 is theoretically valid but the empirical methodology is unverifiable |
| Significance | 5 | Important problem (UQ for LLMs); contribution is potentially significant but limited to closed-form QA with one model scale |
| Clarity | 7 | Well-written, well-organized; the quotient-space framing is clearly explained; figure captions have critical errors |
| Reproducibility | 3 | Code not released; all numbers are TODO placeholders; cannot reproduce what does not exist |
| Contextualization | 7 | Strong related work; correctly positioned vs. ConU/SAFER/LofreeCP/TECP; semantic entropy motivation is adequate but no empirical comparison |
| Ethical / Broader Impact | 6 | Adequate but boilerplate; uncertainty quantification for safety-critical deployment is valid motivation with minimal exploration |

**Weighted Average: 4.93** (Reject threshold is ≤4 on any single dimension, but the average of 4.93 places this in the Reject range)

---

## Pointed Questions for the Authors

1. **What are the actual numbers in Table 1?** Please provide the real experimental results. Without them, this review cannot assess whether SemCP's set-size advantage holds.

2. **Why does Figure 3's caption reference GPT-2 when Section 5.1 specifies Qwen2.5-7B-Instruct?** Is this a copy-paste error from an earlier draft? What were the actual Qwen2.5-7B-Instruct results that would appear in Figure 3?

3. **What was the feasibility rate of the coverage constraint for kernel bandwidth selection on Qwen2.5-7B-Instruct?** If the constraint was infeasible (as it was for GPT-2), then sigma defaults to a set-size-minimizing value without coverage guarantee — fundamentally altering what the "learned kernel" claim means.

4. **Can you show results at multiple model scales (1B, 7B, 70B) demonstrating that set-size advantage is robust?** The 33% reduction claim is only meaningful if it holds across generator quality levels, not just at one model size.

5. **What was the empirical admissibility rate p_A for Qwen2.5-7B-Instruct on TriviaQA and SQuAD?** The marginal coverage ceiling is p_A. If p_A < 0.90, the marginal coverage guarantee cannot be achieved by any conformal method — this is critical for interpreting all results.

6. **Where does the "19.89 Token-CP" comparison number come from?** The ablation section reports SemCP-Euclidean at 18.57. What is Token-CP at 19.89, and why does it not appear in the baseline methods (Section 5.2)?

7. **Why was semantic entropy not included as a baseline?** It is cited as a key motivation, and the paper argues its thresholds are "ad hoc." An empirical comparison would strengthen the paper's claims considerably.

8. **For genuinely open-ended generation tasks, how is semantic equivalence defined?** The NLI-based bidirectional entailment works for QA with canonical answers, but the paper motivates with open-ended generation (Section 1) without demonstrating it. What would the equivalence relation look like for summarization or dialogue?

---

## Falsifiability Test

**"What evidence would change my decision?"**

To change this from a Reject to a higher score, the authors would need to provide:

- **Real numbers in Table 1** showing SemCP achieves valid conditional coverage (~0.89) with substantially smaller set sizes than all 4 baselines, on both TriviaQA and SQuAD, across all 3 seeds.
- **Multi-scale experiments** (1B, 7B, 70B) showing the set-size advantage is not an artifact of Qwen2.5-7B-Instruct's particular output distribution.
- **A figure or table showing p_A** (admissibility rate) is well above 0.90 for the models tested, so the marginal coverage ceiling is not the binding constraint.
- **Results on at least one open-ended generation task** (summarization, code generation, or dialogue) demonstrating that semantic equivalence via NLI scales beyond closed-form QA.
- **Corrected figure captions** that accurately describe the experiments actually run.
- **Released code** so the empirical claims are reproducible.

If the actual Qwen2.5-7B-Instruct results show that conditional coverage is near-zero (as implied by the GPT-2 caption), and the set size numbers are similar to baselines, this paper's core claims collapse. The theoretical contribution remains interesting but would need substantially stronger empirical validation.

---

## Confidence

**2/5** — I have high confidence in my theoretical assessment (Theorem 1 is valid; the quotient-space framing is sound). I have near-zero confidence in my empirical assessment because the experiments were not run. My scores reflect this uncertainty: Soundness and Reproducibility are scored low not because I found fatal methodological flaws, but because there are no experiments to assess.

---

## Decision

**Reject**

The paper cannot be reviewed empirically. All numbers are TODO_NUM placeholders. A theoretical contribution of this quality deserves a thorough empirical evaluation before review. The quotient-space conformal prediction framework is genuinely novel and the conditional coverage theorem is correct — but NeurIPS requires empirical validation, and the paper in its current form does not provide it.

The figure caption inconsistency (GPT-2 vs. Qwen2.5-7B-Instruct) and the disconnect between the 33% set-size-reduction claim and the actual ablation numbers (13.35 vs. 18.57, with no 19.89 baseline in the tables) are additional red flags that the submitted artifact may not match the described experiments.

**Recommendation:** Accept with Major Revision after experiments are run and all TODO_NUM placeholders are replaced with real numbers. The theoretical foundation is solid enough to warrant another look once the empirical holes are filled.

---

— The Empirical Skeptic