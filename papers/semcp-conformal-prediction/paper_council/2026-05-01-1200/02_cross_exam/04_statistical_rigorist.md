# Cross-Exam Report — The Statistical Rigorist

**Paper:** SemCP: Coverage Guarantees Over Meanings, Not Strings
**Date:** 2026-05-01 (Cross-Exam)
**Reviewer:** The Statistical Rigorist

---

## 1. Disagreements with Other Reviewers

### D1: Soundness Score (Theory Critic, Domain Expert ML, Reproducibility Archeologist vs. Me)
**Their position:** Soundness = 5/10 ("Theorem 1 is correct; empirical methodology unverifiable but theory is sound")
**My original position:** Soundness = 4/10 ("Theorem 1 is correct, but all empirical results are TODO placeholders")

**My updated position after cross-exam:** I maintain Soundness = 4/10, but I now acknowledge the Theory Critic's point that the theorem proof has a genuine gap (admissibility-selection effect on exchangeability). However, I disagree with raising Soundness to 5 solely based on theorem correctness — the empirical methodology section is so severely compromised (TODO_NUM, figure caption mismatch, partition method inconsistency) that Soundness cannot recover to 5. The "methodology" dimension encompasses both theoretical derivation AND experimental design/execution. Both must be sound.

**Resolution:** I will add the Theory Critic's admissibility-selection concern as a new weakness in my review.

---

### D2: Reproducibility Score (Domain Expert ML, Reproducibility Archeologist vs. Me)
**Their position:** Reproducibility = 2/10 ("Cannot be reproduced — code not released, all numbers are placeholders")
**My original position:** Reproducibility = 3/10 ("Code not released but hyperparameters fully disclosed")

**My updated position:** I partially agree with the Domain Expert and Archeologist. The TODO_NUM placeholders and TODO_HOURS runtime information are legitimate penalties beyond just code non-release. However, the hyperparameter table is detailed (Table 2 is complete except for runtime), which distinguishes this from a purely "no information provided" scenario. I will revise Reproducibility to **2/10** to align with the majority position, but note that hyperparameter disclosure is a partial credit offset.

---

## 2. Issues Others Missed That I Now Add

### New W11: Exchangeability Argument for Admissibility-Selected Calibration Set Is Incomplete (added from Theory Critic)
**Severity:** 3/5
**Issue:** Theorem 1 computes the conformal quantile q-hat over the admissibility subset I = {i : A_i = 1}. But I is selected post-hoc based on which calibration examples happened to have their true meaning sampled — a random event correlated with the calibration labels. Standard split-conformal requires the calibration set to be fixed independently of threshold computation. The paper does not formally argue that exchangeability holds within the admissibility-selected subset. This is a genuine theoretical gap that I did not flag in my original review.

**Location:** Theorem 1 proof sketch, Section 4.4

---

### New W12: Baseline Hyperparameter Asymmetry Compromises Experimental Validity (added from Methodological Hawk)
**Severity:** 3/5
**Issue:** SemCP's bandwidth sigma is optimized via grid search on a held-out 20% split (minimize set size subject to coverage >= 1-alpha). LofreeCP's length regularizer lambda = 0.5 is taken "from the public implementation" without retuning. SAFER's abstention threshold of 0.10 is fixed, not optimized. This asymmetric tuning means SemCP has a data-adaptive advantage that baselines do not receive. The set-size efficiency comparison (SemCP: 13.35 vs Token-CP baseline: 19.89) may reflect hyperparameter selection effort, not intrinsic method quality.

**Location:** Section 5.2 baselines, Section 4.2 sigma optimization

---

### New W13: DeBERTa-v2-xlarge-MNLI Inference Cost Is Unaddressed (added from Adversarial Practitioner)
**Severity:** 2/5
**Issue:** O(K^2) pairwise NLI judgments per instance — for K=10, that's 100 NLI forward passes per calibration/test instance. The paper does not discuss latency, cost, or throughput of this pipeline. For production deployment at scale, this operational cost is a meaningful concern.

**Location:** Section 4.1; Algorithm 1 step 3

---

## 3. Consensus Signal — Weakness with Most Reviewer Agreement

The **TODO_NUM placeholder problem** has **9/9 unanimous agreement** as the primary rejection trigger. Every reviewer marks this as severity 5/5 or critical.

Secondary consensus (8/9 reviewers):
- **Figure 3 GPT-2/Qwen caption mismatch** — flagged by everyone except possibly some reviewers who subsumed it under "internal inconsistencies"
- **Near-zero coverage vs 33% set-size claim incoherence** — flagged by me, Methodological Hawk, Empirical Skeptic, Adversarial Practitioner, Big Picture Editor, Naive Reader

The claim/weakness with the most agreement beyond TODO_NUM is the **internal incoherence between near-zero coverage claim and the 33% set-size reduction claim**. Six reviewers (me, Methodological Hawk, Empirical Skeptic, Adversarial Practitioner, Big Picture Editor, Naive Reader) explicitly flag this as a contradiction, not just a clarity issue. This is the paper's most structurally incoherent claim.

---

## 4. Updated Per-Rubric Scores

| Dimension | Original | Revised | Change | Rationale |
|-----------|----------|---------|--------|-----------|
| Originality / Novelty | 7 | 7 | — | Unanimous; no new information changes this |
| Soundness | 4 | 4 | — | Maintain despite Theory Critic's push to 5 — methodology (experimental design) is equally weighted with theorem correctness |
| Significance | 6 | 6 | — | Unanimous framing; no new information |
| Clarity | 6 | 5 | -1 | I underweighted the GPT-2/Qwen mismatch severity; it is more than a "clarity issue" — it's a factual error. Also adding partition inconsistency (Section 4.1 vs 5.1) as noted by multiple reviewers |
| Reproducibility | 3 | 2 | -1 | Align with Domain Expert (2) and Reproducibility Archeologist (2); TODO_NUM and TODO_HOURS placeholders justify this |
| Contextualization vs Prior Work | 7 | 7 | — | Strong; no changes needed |
| Ethical / Broader Impact | 6 | 6 | — | Adequate |

**Revised Weighted Average:**
(7×1.0 + 4×1.5 + 6×1.0 + 5×0.7 + 2×1.0 + 7×0.8 + 6×0.5) / 6.5
= (7 + 6 + 6 + 3.5 + 2 + 5.6 + 3) / 6.5
= 33.1 / 6.5 = **5.09**

Original was 5.35. The downward revision reflects: (a) lowering Reproducibility, (b) lowering Clarity.

---

## 5. Decision

**Reject (revised from Reject)**

**Rationale unchanged but strengthened:**
The revised weighted average of 5.09 remains in Reject territory. The primary rejection trigger remains the TODO_NUM placeholders in Table 1 — this is unanimous across all 9 reviewers and cannot be resolved without running experiments. The decision is **Reject** with the same conditional acceptance path as my original review.

**Key additions from cross-exam:**
The Theory Critic's admissibility-selection concern (W11) is a genuine theoretical gap that I now incorporate. The Methodological Hawk's baseline hyperparameter asymmetry concern (W12) is well-founded and undermines the fairness of the set-size comparison. These strengthen the rejection case on methodological grounds beyond just missing numbers.

**Conditional acceptance path:** If authors run experiments, fix the GPT-2/Qwen caption mismatch, resolve the near-zero coverage incoherence, address the admissibility-selection theoretical gap, and release code — this would be a Borderline-to-Accept paper.

---

*— The Statistical Rigorist (Cross-Examined)*