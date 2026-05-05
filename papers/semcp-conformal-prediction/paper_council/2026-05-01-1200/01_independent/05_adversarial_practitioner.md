# Independent Review — The Adversarial Practitioner

**Paper:** SemCP: Coverage Guarantees Over Meanings, Not Strings
**Date:** 2026-05-01
**Reviewer Role:** The Adversarial Practitioner — production viability, edge cases, failure mode analysis

---

## STRENGTHS

**1. Quotient-Space Formalism Is Principled and Novel**
The paper's core insight — treating the string-to-meaning mapping as a quotient map and performing conformal calibration on the quotient space Y/~s — is a genuine conceptual contribution. The theoretical derivation of conditional semantic coverage (Theorem 1) is sound: exchangeability argument holds, the fixed-partition rule is correctly identified as non-data-adaptive, and the admissibility conditioning is cleanly separated from the conformal machinery. This is not engineering dressed up as theory. (Theorem 1 proof sketch, Section 4.3, Remark 1.)

**2. Admissibility-Coverage Decomposition Is operationally critical**
Most CP-for-LLM papers bury the fact that marginal coverage is upper-bounded by p_A. This paper makes it a first-class diagnostic: marginal coverage, conditional coverage, and admissibility rate reported together, so a practitioner immediately sees whether the bottleneck is sampling (low p_A) or calibration (conformal step). This prevents "90% coverage" headlines that hide a 15% admissibility rate. (Section 5.3 analysis; main results table design.)

**3. Learned Kernel vs Frequency Score Distinction Is Real and Quantified**
Figure 4 ablation shows a clean decomposition: SemCP (learned RBF) = 13.35 vs. SemCP-Euclidean = 18.57 vs. Naive Semantic = 18.83 on SQuAD. The kernel learning accounts for ~5 points of set-size reduction over raw clustering. This validates the added complexity — three distinct contributions (a) semantic partitioning, (b) scoring geometry, (c) kernel learning are isolated and measured. (Section 7, Figure 4.)

**4. Graceful Degradation Contract Is Well-Specified**
The paper explicitly defines how SemCP fails: when the true meaning class has no sampled representative, the lifted score is +infinity and the class is excluded. This is a clean, auditable failure contract — the operator knows exactly what happens when p_A is low. No silent performance collapse, no confusing output. (Section 4.3, Algorithm 1 lines 5-6.)

**5. NLI-Based Partitioning Is Appropriately Scoped**
Bidirectional entailment via DeBERTa-v2-xlarge-MNLI with Union-Find is the right choice for defining semantic equivalence classes. The paper correctly notes this is a fixed rule (not data-adaptive), preserving exchangeability. Transitivity closure via Union-Find is the standard approach and is correctly applied. (Section 4.1, line 116, Algorithm 1.)

---

## WEAKNESSES

**W1. EXPERIMENTS NOT RUN — Paper Is Not Submittable in Current Form**
Severity: 5/5
All empirical results in Table 1 are TODO_NUM placeholders. The paper literally cannot be reviewed for correctness — the central quantitative claim (33% set-size reduction on SQuAD) has no supporting evidence. Figure captions describe results that do not exist in the paper. This is a blocker for any review.
*Location:* Table 1, Section 5.3, Figure 3 caption, abstract ("TODO_NUM\% smaller")
*Resolution:* Run experiments and populate real numbers before review submission.

**W2. Figure 3 Caption References GPT-2; Experiments Use Qwen2.5-7B-Instruct**
Severity: 4/5
Figure 3 caption explicitly states "Coverage is near-zero for all methods due to GPT-2's limited QA capability" but experimental setup (Section 5.1) specifies Qwen2.5-7B-Instruct. This is a direct factual contradiction. If Qwen2.5-7B-Instruct is the actual model used, the near-zero coverage claim is either outdated text or a different experiment's caption copied in.
*Location:* Figure 3 caption, line 306; Section 5.1 generator paragraph, line 213
*Resolution:* Update caption to reference Qwen2.5-7B-Instruct, or explain which results use which model.

**W3. Near-Zero Coverage Contradicts the 33% Set-Size Reduction Claim**
Severity: 4/5
The Discussion (line 351) states: "Coverage is near-zero for all methods due to GPT-2's limited QA capability." Yet the abstract and Section 7 claim "33% smaller set sizes" — a 33% reduction is only meaningful if the baseline achieves non-trivial coverage. If both baselines have near-zero coverage, the set-size comparison is meaningless: comparing empty sets to slightly smaller empty sets.
*Location:* Abstract, line 27; Discussion, line 351; Section 7, line 99
*Resolution:* If Qwen2.5-7B-Instruct produces near-zero coverage (p_A << 0.90), remove or qualify the 33% claim. If it produces meaningful coverage, update the Discussion.

**W4. Code Not Released — Reproducibility Score Capped**
Severity: 3/5
"Code and experiment scripts will be released upon publication" is a reproducibility concern. Without released code, the claim that the kernel optimization, NLI partitioning, and lifted scoring pipeline can be reproduced is unverifiable. The NeurIPS checklist item 5 is addressed by a promise, not evidence.
*Location:* Abstract, line 27; Conclusion, line 115; NeurIPS checklist item 5
*Resolution:* Release code at submission time, not upon publication.

**W5. TODO_HOURS Placeholder in Hyperparameter Table**
Severity: 2/5
Table 2 (hyperparameters) contains "TODO_HOURS" for total wall-clock time. This signals experiments were not fully documented at draft time and suggests the full experimental matrix may not have been executed.
*Location:* Table 2, line 221; Section 5.1 hardware paragraph
*Resolution:* Fill in actual runtime.

**W6. Bandwidth Grid Is Coarse and Not Justified**
Severity: 3/5
Bandwidth grid is {0.1, 0.3, 0.5, 1.0, 2.0, 4.0} — 6 values over 2 orders of magnitude with no justification or sensitivity analysis. A production practitioner implementing this on a new domain has no guidance on bandwidth selection. The adaptive bandwidth ablation (SemCP-Adaptive: 14.19) performs slightly worse than globally optimized bandwidth (13.35), but the global optimization uses only 6 candidate values — this could be a discretization artifact.
*Location:* Section 4.2, line 130; Section 5.1 embeddings paragraph, line 217
*Resolution:* Use finer grid or continuous optimization. Add sensitivity analysis.

**W7. NLI Threshold Fixed at 0.5 With No Ablation**
Severity: 3/5
The binarization threshold for bidirectional NLI is fixed at 0.5 with no justification and no sensitivity analysis. This threshold directly controls partition granularity. The paper explicitly acknowledges this as a limitation (line 367) but does not report which threshold was used in the main experiments.
*Location:* Section 4.1, line 115; Limitations bullet 3, line 367
*Resolution:* Report threshold value in main text. Add sensitivity sweep.

**W8. DeBERTa-v2-xlarge-MNLI Is a Heavy Operational Dependency**
Severity: 3/5
The NLI model is DeBERTa-v2-xlarge-MNLI (86B parameters) — significantly larger than the generator (Qwen2.5-7B). At inference: O(K^2) pairwise judgments per instance — for K=10, that's 100 NLI forward passes per calibration/test instance. The paper does not discuss latency, cost, or throughput of this pipeline, nor what happens when the NLI model is unavailable or rate-limited at 3am.
*Location:* Section 4.1; Algorithm 1 step 3; Complexity analysis, line 194
*Resolution:* Report latency breakdowns. Discuss fallback strategies for NLI unavailability.

**W9. K=10 Samples May Be Insufficient for Production Tail Coverage**
Severity: 3/5
The paper uses K=10 samples per prompt. For production deployment, p99 tail coverage matters. With K=10, the admissibility event fires with probability p_A^10 for i.i.d. correct samples — if the per-sample correctness rate is 0.3, p_A ≈ 0.028. The paper reports p_A but does not model tail behavior as a function of K.
*Location:* Section 5.1 K=10 specification; Table 1 admissibility rate column
*Resolution:* Analyze how p_A scales with K. Recommend minimum K for target p_A.

**W10. Only Two Closed-Form QA Benchmarks — Scope of Evidence Is Narrow**
Severity: 3/5
Evaluates on TriviaQA and SQuAD v1.1 only — both closed-form extractive QA tasks. The paper identifies open-ended generation tasks (summarization, dialogue, code generation) as future work but does not evaluate on any of these. A practitioner in code generation or medical dialogue cannot extrapolate from these results.
*Location:* Section 5.1 datasets paragraph; Limitations bullet 2, line 365
*Resolution:* Evaluate on at least one open-ended generation task, or explicitly scope claims to extractive QA.

---

## PER-RUBRIC-DIMENSION SCORES

| Dimension | Score | Calibration Anchor |
|-----------|-------|-------------------|
| 1. Originality / Novelty | 7 | Substantial conceptual advance: quotient-space CP with kernel-based lifted scores is novel. The conditional coverage theorem is a genuine theoretical contribution. |
| 2. Soundness | 3 | Experiments are not run (TODO_NUM placeholders). Theory is correct but unverifiable empirically. Figure 3 caption/model mismatch is a factual error. Score could recover to 6+ if experiments are run. |
| 3. Significance | 6 | Important contribution within the subfield of CP-for-LLMs. If 33% set-size reduction holds with real numbers, this is practically significant. The admissibility decomposition is broadly useful. |
| 4. Clarity | 6 | Well-organized, notation table is helpful, algorithm pseudocode is clean. Figure-caption inconsistency (GPT-2 vs Qwen) is a clarity bug. Mostly readable. |
| 5. Reproducibility | 4 | Code promised "upon publication" — no code released. Hyperparameter table has TODO_HOURS. Without code, reproducibility is limited to paper description. |
| 6. Contextualization vs prior work | 6 | Strong related work covering ConU, SAFER, LofreeCP, TECP. SemCP correctly positioned as complementary. Some semantic entropy prior work could be discussed more directly. |
| 7. Ethical / Broader Impact | 6 | Adequate boilerplate coverage. Legal QA hallucination >75% motivation is real. No specific negative impacts identified — appropriate for UQ infrastructure. |

**Weighted Average:** (7×1.0 + 3×1.5 + 6×1.0 + 6×0.7 + 4×1.0 + 6×0.8 + 6×0.5) / (1.0+1.5+1.0+0.7+1.0+0.8+0.5) = (7 + 4.5 + 6 + 4.2 + 4 + 4.8 + 3) / 6.5 = 33.5 / 6.5 = **5.15**

**Decision threshold:** 5.15 falls in the **Reject** range (4.0–5.5). The single dimension scoring "3" on Soundness is a rejection trigger per rubric rules (≤4 on any single dimension triggers rejection). Note: Soundness is artificially depressed by TODO_NUM placeholders — if experiments are run and factual errors corrected, Soundness would likely be 6-7.

---

## POINTED QUESTIONS FOR THE AUTHORS

1. **"Near-zero coverage" vs the 33% claim:** The Discussion states all methods achieve near-zero coverage due to GPT-2's limited capability, but the abstract claims 33% set-size reduction. These two statements are contradictory: a 33% reduction is only meaningful if baseline prediction sets are non-empty and meaningfully large. Please clarify: (a) which model produced the results reported as "33% smaller," and (b) what are actual baseline and SemCP coverage numbers on Qwen2.5-7B-Instruct?

2. **NLI model failure modes in production:** DeBERTa-v2-xlarge-MNLI is a heavy dependency — at inference you run 100 NLI forward passes per calibration/test instance. What is the p99 latency of this pipeline on your target hardware? When the NLI API is rate-limited or errors out, does the system fall back to string-level CP, abstain, or fail entirely? What is the operator runbook for the 3am failure scenario?

3. **Bandwidth selection as a production hyperparameter:** Your grid has 6 values over 2 orders of magnitude. In a new domain (medical records, legal contracts, code generation), how should a practitioner choose sigma? The paper acknowledges the constraint can be infeasible (GPT-2 2-3% correct answer rate) — what is the recommended sigma when the constraint is infeasible? Defaulting to smallest set size without coverage guarantee is dangerous.

4. **What is the minimum K for production deployment?** With K=10 and p_A as admissibility rate, marginal coverage is upper-bounded by p_A. If a practitioner targets 90% marginal coverage and their model achieves 30% per-sample correctness, p_A ≈ 0.028 — effectively zero. What is the minimum K you'd recommend for a production system? Have you analyzed how p_A scales with K?

5. **Figure 3 caption says GPT-2 but experiments use Qwen2.5-7B:** This is a factual inconsistency that needs resolution. Was there a GPT-2 experiment later replaced with Qwen2.5-7B? Or is the caption leftover text? Please clarify which results correspond to which model.

---

## FALSIFIABILITY TEST

**"What evidence would change my decision from Reject to Accept?"**

Evidence that would shift the score:
1. **Actual experimental numbers** — Table 1 populated with real values. If SemCP achieves conditional coverage ≈ 0.89 (as Theorem 1 guarantees) and set sizes of ~13 on SQuAD vs ~20 for ConU, this is a real improvement.
2. **Resolution of the GPT-2/Qwen mismatch** — Figure 3 caption corrected to reference Qwen2.5-7B-Instruct. Near-zero coverage claim reconciled with actual results.
3. **Code released before/with submission** — A GitHub link with a working implementation. "Upon publication" promise is not acceptable for NeurIPS-level reproducibility.
4. **NLI threshold sensitivity** — A small table showing how partition granularity and set sizes change across NLI thresholds {0.3, 0.5, 0.7}.
5. **Latency breakdown** — p50/p95/p99 latency characterization of the full pipeline.

**Evidence that would shift from Reject to Strong Reject:**
1. Experiments are run and show no meaningful set-size advantage for SemCP over ConU (the 33% claim does not replicate).
2. The GPT-2/Qwen mismatch persists after correction, indicating deeper factual inconsistency.
3. Code is not released even after acceptance notification.
4. Near-zero coverage generalizes to Qwen2.5-7B-Instruct, making the entire experimental evaluation uninformative.

---

## CONFIDENCE

**3/5**

The theory is solid and the paper's conceptual framework is strong. However, I cannot render a confident judgment because the central empirical results are TODO_NUM placeholders. I have strong evidence that the theory is correct, but the empirical verification is absent. My confidence would rise to 4+ if experiments were run and the Figure 3 caption inconsistency were resolved.

---

## DECISION

**Reject (conditional on experiments being run)**

The theoretical contribution is real and valuable. The admissibility-coverage decomposition is the right way to present CP-for-LLM results. The learned kernel contribution is demonstrated in ablation.

However, the paper cannot be accepted in its current form: TODO_NUM placeholders mean central quantitative claims are unverified. Figure 3 caption is a factual error suggesting the paper was assembled from multiple drafts. If the authors resolve these issues — run the experiments, fix the caption, release code — this is an Accept. As submitted, it is a Reject that is one experiment run away from being a strong Accept.

---

*— The Adversarial Practitioner*