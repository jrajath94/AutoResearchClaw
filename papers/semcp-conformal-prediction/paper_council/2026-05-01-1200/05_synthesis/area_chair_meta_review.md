# Area Chair Meta-Review: SemCP — Coverage Guarantees Over Meanings, Not Strings

**Paper:** SemCP: Coverage Guarantees Over Meanings, Not Strings
**Venue:** NeurIPS 2026
**Area Chair:** synthesized from 9 independent reviews + 5 cross-examinations
**Date:** 2026-05-01

---

## Final Calibrated Decision: **REJECT**

**Weighted Average (Bayesian):** 5.0 (Reject range: 4.0–5.5)
**Confidence in verdict:** Very High — 9/9 reviewers flag the same fatal flaw
**Consensus score:** Unanimous on primary rejection trigger; strong majority on secondary issues

---

## Decision Rationale

This paper proposes SemCP, a conformal prediction framework operating in semantic embedding space via bidirectional NLI partitioning and kernel-based lifted scores. Theorem 1 (conditional semantic coverage guarantee) is technically sound. The admissibility-coverage decomposition is a genuinely useful diagnostic contribution. The quotient-space conformal framing is novel within CP-for-LLMs.

However, the paper cannot be accepted in its current form. All nine reviewers independently identified the same fatal flaw: **every empirical result in Table 1 is a `TODO_NUM` placeholder**. The central quantitative claim — "33% smaller set sizes" — has no supporting evidence. A paper that submits placeholder results as a completed NeurIPS submission cannot be evaluated, let alone accepted.

The rejection is not a verdict on the paper's potential. The theoretical foundation is solid. With real experiments, resolved contradictions, and released code, this would be a competitive submission. As submitted, it is a **Reject** with a clear path to resubmission.

---

## Rubric Dimension Scores (Bayesian Aggregation with Confidence Weighting)

| Dimension | Mean Score | Consensus | Confidence Weight | Notes |
|-----------|-----------|-----------|-----------------|-------|
| Originality / Novelty | 7.1 | Strong | High | Quotient-space CP framing is genuinely novel; all reviewers agree |
| Soundness | 3.3 | Very Strong | Very High | Theorem 1 has a proof gap (admissibility-selection); experiments absent; algorithm-theory mismatch |
| Significance | 5.9 | Strong | High | Important subfield contribution if results hold; admissibility decomposition alone is publishable |
| Clarity | 5.7 | Moderate-Strong | Moderate | GPT-2/Qwen mismatch, partition inconsistency, Algorithm-theory gap create multiple contradictions |
| Reproducibility | 2.2 | Very Strong | Very High | No code released; all numbers are TODO_NUM; TODO_HOURS placeholder |
| Contextualization vs Prior Work | 6.7 | Strong | Moderate | Strong coverage of ConU/SAFER/LofreeCP/TECP; semantic entropy citation gap noted |
| Ethical / Broader Impact | 6.3 | Strong | Low | Adequate boilerplate; not a decision factor |

**Weighted Average:** `(7.1×1.0 + 3.3×1.5 + 5.9×1.0 + 5.7×0.7 + 2.2×1.0 + 6.7×0.8 + 6.3×0.5) / 6.5` = **5.0**

**Decision boundary:** 5.0 falls in the Reject range (4.0–5.5). Soundness (weight 1.5) is the dominant factor, with multiple reviewers recording 2–3 on this dimension due to the combination of missing experiments and theoretical gaps.

---

## Meta-Review (750 words)

### The Paper's Core Contribution

SemCP addresses a genuine and underappreciated problem in conformal prediction for LLMs: standard CP operates over token strings, but multiple surface forms can express the same meaning. A conformal set that guarantees coverage over strings is not the same as a conformal set that guarantees coverage over meanings.

The paper's solution — lifting CP from string space Y to a quotient space Y/~s via bidirectional NLI partitioning — is conceptually correct and technically novel. Theorem 1 correctly derives a conditional coverage guarantee given the admissibility event (the true meaning was sampled among K draws). The admissibility-coverage decomposition in Remark 1 is the paper's most practically valuable contribution: it explicitly separates the sampling quality (p_A, a property of the generator and sample budget) from calibration quality (a property of the scoring rule), giving practitioners a principled diagnostic for attributing failure modes. This framing should become standard in the CP-for-LLMs literature.

The kernel-based lifted score (RBF kernel over kernel mean embeddings in semantic embedding space) is well-motivated. The ablation isolating the learned kernel's contribution over Euclidean distance (13.35 vs 18.57 on SQuAD) is the right empirical decomposition, assuming the numbers are real.

### Why This Is a Reject

**The primary rejection trigger is unanimous and unambiguous: every empirical result is a TODO_NUM placeholder.** All nine reviewers independently flagged this. Table 1, which should contain the main results comparing 5 methods across 2 datasets with 5 metrics each, contains exclusively `TODO_NUM` entries. The abstract's central empirical claim ("TODO_NUM% smaller set sizes") explicitly admits the results have not been established. This is not a paper that "needs more experiments" — it is a paper where the empirical contribution has not been executed.

**The second major concern is a factual inconsistency that suggests the paper was assembled from multiple drafts without final consolidation.** The Figure 3 caption references "GPT-2's limited QA capability," but Section 5.1 explicitly specifies Qwen2.5-7B-Instruct as the generator. Eight of nine reviewers flagged this. The Discussion section continues to analyze GPT-2's 2–3% correctness rate as if it explained the experimental results, but these are different experimental configurations that were never reconciled.

**The third major concern is a logical incoherence within the paper's own claims.** The paper simultaneously asserts (a) near-zero coverage for all methods due to low generator quality (Discussion, Section 7) and (b) 33% smaller set sizes than the string-level baseline (Abstract). If coverage is near-zero, conformal sets collapse to empty sets — set size comparisons are meaningless. A trivial predictor (always output the empty set) achieves minimum set size with zero coverage. The 33% claim is only interpretable when both SemCP and baselines achieve meaningful coverage, which the paper's own text denies.

**A fourth concern, identified by the Theory Critic and Naive Reader, is a structural inconsistency between Algorithm 1 and the theory in Section 4.3.** Algorithm 1 computes a contrastive between-cluster score (`1 - max_{c' != c_i^*} kappa_sigma(...)`), while Section 4.3 defines the lifted score as a within-cluster minimum (`min_{y' in [y]_s} s(x, y')`). These are structurally different operations. An implementer following Algorithm 1 would not reproduce the method described in the theory. This is not a clarity issue — it is a correctness issue.

**A fifth concern is a theoretical proof gap identified by the Theory Critic.** Theorem 1 computes the conformal quantile q-hat over the admissibility subset I = {i : A_i = 1}, where A_i is the event that the true meaning was sampled. But I is selected post-hoc based on which calibration examples happened to have their true meaning sampled — a random event. Standard split-conformal requires the calibration set to be fixed independently of threshold computation. The paper does not formally argue that exchangeability holds within the admissibility-selected subset. This is a genuine theoretical gap requiring either a formal proof or an explicit acknowledgment of the heuristic nature of the implemented procedure.

### What This Paper Needs

The good news is that every identified concern is fixable:

1. **Run the experiments.** Populate Table 1 with real numbers. Report mean ± SD across 3 seeds with 95% bootstrap CIs.
2. **Fix the figure caption.** Update Figure 3 caption to reference Qwen2.5-7B-Instruct. Reconcile or remove the GPT-2 discussion.
3. **Resolve the logical incoherence.** Clarify what coverage SemCP achieves on Qwen2.5-7B-Instruct. If coverage is meaningful, the near-zero coverage claim was for a different model and should be removed or clearly separated.
4. **Align Algorithm 1 with Section 4.3.** Either correct the algorithm to implement the stated theory, or revise the theory to match the algorithm.
5. **Address the admissibility-selection proof gap.** Either prove exchangeability is preserved within the admissible subset, or explicitly note the selection effect and its implications.
6. **Release code.** A GitHub link with working implementation, not a promise to release upon publication.
7. **Equivalent hyperparameter tuning for baselines.** SemCP's bandwidth is optimized on held-out data; baselines should receive equivalent tuning effort or a sensitivity analysis.

With these fixes, the paper has a strong theoretical contribution and a meaningful empirical story. As submitted, it does not.

---

## TOP 5 Issues Ranked by Severity

### Issue 1: All Empirical Results Are TODO_NUM Placeholders
**Severity:** 5/5 — Critical (unanimous 9/9 reviewers)
**Consensus level:** Absolute
**What it is:** Every cell in Table 1 is `TODO_NUM`. The abstract explicitly contains "TODO_NUM% smaller." The Discussion cites "13.35 vs 19.89 for Token-CP" as if these numbers exist, but Table 1 is empty.
**Impact:** The central empirical claim cannot be evaluated. The paper cannot be reviewed as an empirical paper.
**Fix:** Run experiments. Populate Table 1 with actual numbers with uncertainty estimates.

### Issue 2: Figure 3 Caption References GPT-2; Experiments Use Qwen2.5-7B-Instruct
**Severity:** 4/5 — Major (flagged by 8/9 reviewers)
**Consensus level:** Very Strong
**What it is:** Figure 3 caption says "near-zero coverage for all methods due to GPT-2's limited QA capability." Section 5.1 specifies Qwen2.5-7B-Instruct. These are different models with different capability profiles. The entire analysis of "why coverage is near-zero" is tied to a model not used in the experiments.
**Impact:** Raises questions about what experiments were actually run. Suggests the paper was assembled from template text without final consolidation.
**Fix:** Update caption to reference Qwen2.5-7B-Instruct. Reconcile or remove GPT-2 discussion.

### Issue 3: Near-Zero Coverage Claim Contradicts 33% Set-Size Reduction
**Severity:** 4/5 — Major (flagged by 4–6/9 reviewers at high severity)
**Consensus level:** Strong
**What it is:** The paper claims both near-zero coverage (due to low generator quality) and 33% smaller set sizes. Set size reduction is only meaningful when both methods achieve non-trivial coverage. If coverage is near-zero, conformal sets collapse to empty sets and set size comparisons are between zeros.
**Impact:** A logical impossibility within the same experimental run. The numbers appear to come from different experimental configurations that were never reconciled.
**Fix:** Clarify the coverage regime. If Qwen2.5-7B-Instruct achieves meaningful coverage, remove the near-zero claim. If it does not, remove the 33% claim or contextualize it as a projection from the ablation study.

### Issue 4: Algorithm 1 Does Not Match Section 4.3 Theory
**Severity:** 4/5 — Major (identified by Naive Reader, corroborated by Theory Critic and cross-examined reviews)
**Consensus level:** Moderate (2–3/9 reviewers explicitly, but the issue is unambiguous from text)
**What it is:** Algorithm 1 line 180 computes `1 - max_{c' != c_i^*} kappa_sigma(...)` — a contrastive between-cluster score. Section 4.3 Equation 2 defines the lifted score as `min_{y' in [y]_s} s(x, y')` — a within-cluster minimum score. These are structurally different.
**Impact:** An implementer following Algorithm 1 would not reproduce the method described in the theory. The method being evaluated is ambiguous.
**Fix:** Reconcile Algorithm 1 with Section 4.3. State the correct procedure unambiguously.

### Issue 5: Admissibility-Selection Proof Gap in Theorem 1
**Severity:** 3/5 — Moderate (identified by Theory Critic, corroborated by Statistical Rigorist and Big-Picture Editor after cross-examination)
**Consensus level:** Moderate (2–3/9 reviewers, but technically substantive)
**What it is:** Theorem 1 computes the conformal quantile q-hat over the admissibility subset I = {i : A_i = 1}, where A_i = {true meaning was sampled}. I is selected post-hoc based on which calibration examples happened to have their true meaning sampled — a random event. Standard split-conformal requires the calibration set to be fixed independently of threshold computation. The paper does not formally argue that exchangeability holds within the admissibility-selected subset.
**Impact:** Theorem 1's coverage guarantee may not hold for the implemented algorithm due to selection bias in threshold computation.
**Fix:** Either prove exchangeability is preserved within the admissibility-selected subset, or acknowledge this as a heuristic and characterize the deviation empirically.

---

## What the Paper Must Fix Before Resubmission

1. **Run all experiments and replace TODO_NUM placeholders with real numbers.** Report mean ± SD across 3 seeds with 95% bootstrap CIs. This is non-negotiable.
2. **Fix Figure 3 caption to reference Qwen2.5-7B-Instruct.** Remove or separate GPT-2 results from the main experimental narrative.
3. **Resolve the near-zero coverage vs. 33% set-size reduction incoherence.** The paper cannot assert both in the same experimental context without clarification.
4. **Align Algorithm 1 with Section 4.3.** The pseudocode and the theory must describe the same procedure.
5. **Address the admissibility-selection proof gap in Theorem 1.** Provide a formal argument that exchangeability holds within the admissible subset, or revise the theorem to explicitly account for the selection effect.
6. **Release code at submission.** A GitHub repository with commit hash and working experiment scripts. "Upon publication" is not an open-access commitment.
7. **Equivalent hyperparameter tuning for baselines.** SemCP's bandwidth is optimized via grid search on held-out data; baselines using off-the-shelf hyperparameters creates an unfair comparison.

**Note to authors:** The theoretical contribution is real and the problem is genuine. The admissibility-coverage decomposition alone is worth publishing. With the empirical foundation in place and the identified issues resolved, this is a strong Accept candidate.

---

*Area Chair synthesis based on 9 independent reviews and 5 cross-examination updates from the Paper Council review council.*
