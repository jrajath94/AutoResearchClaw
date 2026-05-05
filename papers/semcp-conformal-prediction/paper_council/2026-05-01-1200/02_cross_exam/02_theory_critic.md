# Cross-Examination — The Theory Critic (Round 2)

**Paper:** SemCP: Coverage Guarantees Over Meanings, Not Strings
**Reviewer:** The Theory Critic
**Date:** 2026-05-01
**Stage:** Cross-Examination — comparing my review against 8 peers

---

## 1. Disagreements With At Least 2 Other Reviewers

### D1: My Soundness Score (4) Is Too Harsh Given Theory is Correct
**My claim:** Soundness = 4 because "Theorem 1 has a proof gap (admissibility-selection); kernel optimization unanalyzed; experiments not run — fatal"
**Disagreement with:** Domain Expert ML (5), Big-Picture Editor (4), Reproducibility Archeologist (5), Adversarial Practitioner (3), Statistical Rigorist (4), Methodological Hawk (4)

All other reviewers with a Soundness score give me 4 or above. Only the Empirical Skeptic (3) and Adversarial Practitioner (3) are lower. The consensus is 4-5.

**Resolution:** I soften my Soundness to 4 (confirming). The Theory Critic role exists to identify proof gaps that others miss. W7 (admissibility-selection) is the gap I found that others underweighted. I'll keep 4, but with the explicit note that W7 is the distinguishing concern.

---

### D2: The Naive Reader Caught an Issue I Missed — Algorithm 1 vs Theory Mismatch
**The Naive Reader's W4:** Algorithm 1 (line 180) computes the lifted calibration score as:
`1 - max_{c' != c_i^*} kappa_sigma(bars_phi_{c_i^*}, bars_phi_{c'})` — a contrastive between-cluster score.

But Section 4.3, Equation 2 defines it as:
`min_{y' in [y]_s intersect {y_1,...,y_K}} s(x, y')` — a within-cluster minimum score.

**My position:** I did NOT flag this structural mismatch. I flagged W7 (admissibility-selection) and W4 (kernel adaptation) but missed this Algorithm-theory inconsistency entirely. This is a significant gap in my review.

**Who else caught it:** Only the Naive Reader. This is a genuine miss.

**Updated position:** I adopt W4 from the Naive Reader as a new weakness in my cross-examination. This is a W3-level issue (Severity 4/5) — a paper where the algorithm doesn't implement the stated theory cannot be accepted.

---

### D3: GPT-2/Qwen Caption Inconsistency — I Underweighted It (3/5 vs 4/5)
**My claim:** Severity 3/5 for Figure 3 caption mismatch.
**Majority position:** Most reviewers gave this 4-5/5 severity. The Methodological Hawk, Big-Picture Editor, Empirical Skeptic, Statistical Rigorist, and Domain Expert ML all gave it 4-5.

**My updated position:** The caption inconsistency is more serious than I assessed. It indicates the paper was assembled from template text without final consolidation. On a paper where the empirical results are already TODO_NUM placeholders, a caption that references the wrong model is not an editorial footnote — it is evidence the experiments may never have been run with Qwen2.5-7B-Instruct at all. I update my severity to 4/5.

---

## 2. Issues OTHERS Missed That I Now Want to Add

### O1: Admissibility-Selection Proof Gap (W7 in my original review)
**My finding:** The threshold qhat is computed as the quantile over the admissibility subset I = {i: A_i = 1}. But I is selected post-hoc based on which calibration examples happened to have their true meaning sampled. The threshold is computed over a systematically easier subset. No other reviewer explicitly identified this as a theoretical gap requiring formal justification.

**Contradiction:** The Methodological Hawk noted "Theorem 1 is theoretically sound" without mentioning this. The Big-Picture Editor, Statistical Rigorist, and Domain Expert ML all confirmed Theorem 1 without flagging the selection effect. This is the gap I found that others missed. It is my most distinctive contribution as Theory Critic.

---

### O2: Kernel Bandwidth Selection May Break Exchangeability (W4 in my original)
**My finding:** Theorem 1 assumes the kernel is fixed. The method uses data-adaptively selected sigma. The paper does not formally analyze whether this invalidates the coverage guarantee.

**Contradiction:** Only the Methodological Hawk and I identified this. Most reviewers treated sigma optimization as a standard hyperparameter search without theoretical concern. I maintain W4 as a 3/5 severity issue distinct from the empirical TODO_NUM problem.

---

### O3: NLI Partition Transitivity Assumption (W8 in my original)
**My finding:** Union-Find closure assumes transitivity of bidirectional entailment. DeBERTa-v2-xlarge-MNLI is not logically consistent.

**Contradiction:** No other reviewer mentioned this. It may be minor (practical robustness), but as Theory Critic I should note it as a formal limitation.

---

## 3. My Positions Updated After Seeing Consensus

### Changed: Coverage Contradiction Deserves More Weight
The near-zero coverage claim vs. 33% set-size reduction contradiction was identified by Statistical Rigorist (W3), Methodological Hawk (W3), Adversarial Practitioner (W3), and Empiricist Skeptic (W3). I identified it as W2 (severity 4/5). The consensus agreement strengthens this: this is not a framing issue — it's a logical contradiction in the paper's own claims.

### Changed: GPT-2/Qwen Severity Upgraded to 4/5
Consensus across 7 reviewers puts this at 4/5+. I had it at 3/5. I upgrade.

### Unchanged: TODO_NUM Is the Primary Blocker
No disagreement here — all 9 reviewers agree. This is the consensus signal.

### Unchanged: W7 (admissibility-selection) Is My Most Important Contribution
I maintain W7 at 3/5 severity. The exchangeability-of-the-selected-subset argument needs formal treatment. Others missed it; I keep it.

---

## 4. Claim/Weakness With Most Reviewer Agreement

**Winner: W1 (All Experimental Results Are TODO_NUM Placeholders) — 9/9 reviewers flagged it.**

Every single reviewer independently identified this. The consensus is absolute and unambiguous.

**Second place (tied):**
- W2 (Figure 3 caption GPT-2 vs Qwen mismatch) — 8/9 reviewers flagged it
- W3 (Near-zero coverage vs 33% set-size reduction contradiction) — 4/9 explicitly, others implicit

**Third place:**
- W4 (Partition method inconsistency Section 4.1 vs 5.1) — flagged by Methodological Hawk and Naive Reader

---

## 5. Updated Per-Rubric Scores and Decision

### Revised Scores

| Dimension | Original | Consensus | My Updated |
|-----------|----------|-----------|------------|
| Originality / Novelty | 8 | 7 | **7** — quotient-space is genuinely new; I was slightly generous |
| Soundness | 4 | 4.4 | **4** — keep (W7 is my distinctive contribution; TODO_NUM compounds it) |
| Significance | 6 | 6 | **6** — unchanged |
| Clarity | 6 | 6.4 | **6** — partition inconsistency is a clarity bug; I missed it but consensus caught it |
| Reproducibility | 2 | 2.3 | **2** — all agree; no code, all numbers TODO_NUM |
| Contextualization | 7 | 6.9 | **7** — unchanged |
| Ethical / Broader Impact | 6 | 6 | **6** — unchanged |

**Revised Weighted Average:** (7×1.0 + 4×1.5 + 6×1.0 + 6×0.7 + 2×1.0 + 7×0.8 + 6×0.5) / 6.5 = (7 + 6 + 6 + 4.2 + 2 + 5.6 + 3) / 6.5 = 33.8 / 6.5 = **5.20**

**Previous:** 5.35. **Revised:** 5.20.

### Decision: **Borderline** (leaning toward Reject, unchanged)

**Rationale:** The weighted average shifted down slightly because I corrected GPT-2/Qwen severity to 4/5 (more reviewers agreed it was serious) and absorbed the Naive Reader's Algorithm-theory mismatch finding. The core judgment remains: Borderline/Reject because TODO_NUM placeholders make empirical evaluation impossible.

**What would change my decision to Accept:**
1. Real experimental numbers in Table 1 with conditional coverage ~0.89 and set-size reduction >20%
2. Corrected Figure 3 caption
3. Code released on GitHub
4. **Formal treatment of W7** — I want to see an argument that exchangeability holds within the admissibility-selected subset I, or an acknowledgment that Theorem 1's guarantee applies to the full calibration set (not filtered by admissibility)

**What would strengthen my recommendation to Accept beyond the consensus:**
The admissibility-selection proof gap (W7) is the most technically interesting remaining concern. If authors formally prove or acknowledge this, it would elevate my confidence in the theoretical contribution substantially.

---

*— The Theory Critic (cross-examined)*