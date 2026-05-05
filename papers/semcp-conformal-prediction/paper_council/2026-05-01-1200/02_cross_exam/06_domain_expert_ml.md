# Cross-Examination Report — The Domain Expert (ML/Systems)

**Paper:** SemCP: Coverage Guarantees Over Meanings, Not Strings
**Date:** 2026-05-01
**Review Cycle:** Cross-examination phase

---

## 1. Disagreements with at Least 2 Other Reviewers

### D1. Partition Method Inconsistency Is Algorithm-Theory Mismatch (NOT Just Clarity)
**My original position:** I flagged W2 (Figure 3 caption) and W3 (Discussion conflates models) but treated the Section 4.1 vs Section 5.1 partition description as a WEAK issue (I buried it in W9 as "NLI model choice not justified").

**Other reviewers who flagged this as CRITICAL:**
- **The Naive Reader (W2, severity 4/5):** Section 4.1 says "cosine-similarity thresholding at 0.7 in MiniLM embedding space." Section 5.1 says "bidirectional entailment under DeBERTa-v2-xlarge-MNLI binarised at probability 0.5." These are fundamentally different operations. One uses embedding cosine similarity; the other uses NLI entailment.
- **The Methodological Hawk (W4, severity 3/5):** "Section 4.2 says cosine-similarity thresholding in MiniLM space, but Section 5.1 says DeBERTa-MNLI bidirectional entailment. These are fundamentally different partitioning strategies."
- **The Reproducibility Archeologist (W3, severity 3/5):** "Section 4.1 says cosine-similarity thresholding at 0.7. Section 5.1 says bidirectional entailment under DeBERTa. These produce different equivalence partitions."

**My updated position:** This is NOT just a clarity issue. It is a fundamental methodological ambiguity. If Section 4.2's description (cosine-similarity thresholding) is the theoretically described method and Section 5.1's description (NLI entailment) is what was actually run, the paper describes two different methods in two different sections. The Naive Reader goes further and identifies this as an algorithm-theory mismatch: Algorithm 1 line 180 computes the lifted calibration score as a contrastive between-cluster score, while Section 4.3 defines it as a within-cluster minimum score. These are solving different problems.

**Revised assessment:** Upgrade the partition inconsistency to a CRITICAL (5/5) methodological issue, not a MEDIUM clarity issue.

---

### D2. Theorem 1 Exchangeability Argument Has a Genuine Gap
**My original position:** I rated the exchangeability argument as SOUND (S4 in strengths) and gave it a clean bill of health.

**Other reviewers who identified the gap:**
- **The Theory Critic (weakness 3, severity 3/5):** "The threshold qhat is computed as the quantile over the admissibility subset I = {i : A_i = 1}. But I is selected based on which calibration examples happened to have their true meaning sampled — a random event correlated with the calibration labels. Standard split-conformal requires the calibration set to be fixed independently of the threshold computation. The paper does not formally argue that exchangeability holds within this subset."
- **The Naive Reader (W4, severity 4/5):** Algorithm 1 computes `1 - max_{c' != c_i^*} kappa_sigma(...)` — a contrastive between-cluster score. Section 4.3 defines the lifted score as `min_{y' in [y]_s} s(x, y')` — a within-cluster minimum score. "The algorithm and the theory are solving different problems. I could not implement SemCP from this paper."

**My updated position:** I was WRONG to give the exchangeability argument a clean bill of health. The Theory Critic identifies a genuine theoretical gap: computing qhat over a post-hoc selected admissibility subset introduces selection bias that is not addressed in the proof sketch. Additionally, the Naive Reader identifies an algorithm-theory mismatch (not just a clarity issue) where Algorithm 1 and Section 4.3 define the lifted score differently. Both issues are legitimate.

**Revised assessment:** Soundness score should be 2-3 (not 5). The theory has a genuine gap AND the empirical foundation is missing.

---

### D3. Near-Zero Coverage vs 33% Set-Size Reduction Are Mutually Incoherent
**My original position:** I flagged this as W3 (severity 4/5) but framed it as a "clarify which model" issue.

**Other reviewers who identified the incoherence:**
- **The Statistical Rigorist (W3, severity 5/5):** "The paper claims 33% set size reduction (13.35 vs 19.89 Token-CP). But Section 7 says all methods get near-zero coverage due to low generator quality. If coverage is near zero, set size comparisons are meaningless."
- **The Empirical Skeptic (W3, severity 4/5):** "The Discussion claims '33% reduction on SQuAD (13.35 vs 19.89)' but no '19.89 Token-CP' number exists in any table."
- **The Big-Picture Editor (W3, severity 4/5):** "The 33% set-size reduction claim presupposes measurable coverage. If coverage is near-zero for both SemCP and Token-CP, the set-size comparison is meaningless."

**My updated position:** I correctly identified the contradiction but underestimated its severity. This is not merely a model-name inconsistency — it is a logical incoherence between two major claims. The paper cannot simultaneously claim (a) near-zero coverage due to generator limitations and (b) meaningful 33% set-size reduction. These are mutually exclusive experimental regimes.

---

## 2. Issues Others Missed That I Now Want to Add to My Review

### NEW-A: Embedding Anisotropy Correction Literature Is Absent
No other reviewer explicitly identified the missing embedding anisotropy literature. The paper uses frozen embeddings (all-MiniLM-L6-v2) and acknowledges anisotropy as a known pathology (Section 4.2 discussion), but does not cite the correction literature (whitening, isotropy regularization). Key papers (Ethayarajh 2019, Mueller et al. 2022) are missing. This is a gap in contextualization vs prior work.

**Severity:** MEDIUM (3/5)

### NEW-B: DeBERTa-v2-xlarge-MNLI Is a Heavy Operational Dependency (O(K^2) Inference Cost)
The Methodological Hawk, Naive Reader, and Reproducibility Archeologist all mention the NLI model but none quantify the inference cost. At K=10 samples, the pipeline runs O(K^2) = 100 pairwise NLI forward passes per calibration/test instance. With a 1.9B parameter NLI model, this is a significant operational burden that has latency and cost implications for production deployment. I flagged this as W8 but underestimated its severity — it should be 4/5.

**Severity:** MEDIUM-HIGH (4/5) — operational feasibility concern for production systems

### NEW-C: Bandwidth Grid Is Too Coarse for Disciplinary Deployment
Multiple reviewers mention the coarse grid as a minor issue, but none note the fundamental problem: with only 6 candidate values over 2 orders of magnitude, the "optimized" bandwidth could be a discretization artifact. The SemCP-Adaptive result (14.19) performing slightly worse than globally optimized (13.35) suggests the global optimization is not finding a meaningful optimum — it's just picking the least-bad discretized value. For a paper claiming the kernel is the "critical component," this is a meaningful methodology concern.

**Severity:** MEDIUM (3/5)

---

## 3. My Own Positions Updating After Seeing the Consensus

### UPDATE-1: Soundness score should drop from 5 to 3
**Original:** I gave Soundness 5/10, noting "Theory is correct but unverifiable empirically."
**Consensus signal:** All 9 reviewers agree experiments are not run. 8/9 flag the Figure 3 caption as a factual error. 3+ reviewers identify genuine theoretical gaps (exchangeability under admissibility-selection, algorithm-theory mismatch). Given that:
- Theorem 1 has a legitimate proof gap (Theory Critic)
- Algorithm 1 contradicts Section 4.3 (Naive Reader)
- All empirical results are TODO_NUM (unanimous)
- The GPT-2/Qwen mismatch is a factual error suggesting draft assembly from multiple sources (Methodological Hawk, Statistical Rigorist)

A Soundness score of 3/10 is more calibrated than 5/10. The theory is partially correct but has unresolved gaps, AND the empirical foundation is entirely absent.

### UPDATE-2: My weighted average should be REJECT, not BORDERLINE
**Original:** Weighted average 5.3, Borderline
**Recalculated with Soundness 3:**
- Originality 7 × 1.0 = 7.0
- Soundness 3 × 1.5 = 4.5
- Significance 6 × 1.0 = 6.0
- Clarity 7 × 0.7 = 4.9
- Reproducibility 2 × 1.0 = 2.0
- Contextualization 6 × 0.8 = 4.8
- Ethical 7 × 0.5 = 3.5
- **Total: 32.7 / 6.5 = 5.03**

5.03 is in the Reject range (4.0–5.5), not Borderline. My original Borderline assessment was based on an overly generous Soundness score.

### UPDATE-3: My Decision should be REJECT, not BORDERLINE
**Original:** Borderline (precludes Accept — experiments are the blocking issue)
**Updated:** Reject. The consensus among 8/9 reviewers is clear: without experimental results, this paper cannot be accepted. The Theory Critic's identification of a genuine proof gap in Theorem 1's exchangeability argument further undermines the theoretical foundation enough to tip the decision from Borderline to Reject.

---

## 4. Claim/Weakness with Most Reviewer Agreement (Consensus Signal)

### UNANIMOUS Agreement (9/9 reviewers):
**TODO_NUM placeholders in Table 1 — ALL empirical results are missing**
Every reviewer independently identified this as the critical blocking issue. This is the strongest consensus signal in the review set.

### Near-Unanimous Agreement (8/9 reviewers):
**Figure 3 caption says GPT-2, experiments use Qwen2.5-7B-Instruct**
Eight reviewers flagged this as a factual inconsistency (severity 4-5/5). Only the Theory Critic did not separately flag this (though their theory weaknesses indirectly support the same concern).

### Strong Agreement (4+ reviewers):
1. **Near-zero coverage contradicts 33% set-size reduction:** Methodological Hawk, Statistical Rigorist, Empirical Skeptic, Big-Picture Editor, Naive Reader
2. **Partition method inconsistency across sections:** Methodological Hawk, Reproducibility Archeologist, Naive Reader
3. **NLI threshold not ablated:** Methodological Hawk, Adversarial Practitioner, Big-Picture Editor, Statistical Rigorist
4. **Code not released:** All reviewers implicitly or explicitly noted this
5. **Exchangeability argument gap (admissibility-selection):** Theory Critic, Naive Reader

### Summary Table of Consensus:

| Issue | Reviewers Endorsing | Severity |
|-------|-------------------|----------|
| TODO_NUM placeholders | ALL 9 | 5/5 |
| Figure caption model mismatch | 8/9 | 4-5/5 |
| Near-zero coverage vs 33% claim incoherence | 5/9 | 4-5/5 |
| Partition rule inconsistency | 3/9 | 3-4/5 |
| NLI threshold not ablated | 4/9 | 2-3/5 |
| Code not released | All who note reproducibility | 3-4/5 |
| Algorithm-theory mismatch | 2/9 (Theory Critic, Naive Reader) | 4/5 |
| Exchangeability gap (admissibility-selection) | 2/9 (Theory Critic) | 3/5 |

---

## 5. Updated Per-Rubric Scores and Decision

### Revised Scores

| Dimension | Original Score | Revised Score | Reason for Change |
|-----------|--------------|---------------|------------------|
| Originality / Novelty | 7 | **7** | Unchanged. Consensus confirms quotient-space CP is genuinely novel. |
| Soundness | 5 | **3** | Theorem 1 has proven exchangeability gap; Algorithm 1 contradicts theory text; all empirical results missing |
| Significance | 6 | **5** | Near-zero coverage contradicts 33% claim; method's usefulness on actual experiments is unverified |
| Clarity | 7 | **6** | Partition method inconsistency and algorithm-theory mismatch hurt clarity |
| Reproducibility | 2 | **2** | Unchanged. Code promised "upon publication," TODO_NUM results everywhere |
| Contextualization vs Prior Work | 6 | **6** | Unchanged. Missing anisotropy correction literature cited by me only. |
| Ethical / Broader Impact | 7 | **7** | Unchanged |

### Revised Weighted Average

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|---------|
| Originality / Novelty | 7 | 1.0 | 7.0 |
| Soundness | 3 | 1.5 | 4.5 |
| Significance | 5 | 1.0 | 5.0 |
| Clarity | 6 | 0.7 | 4.2 |
| Reproducibility | 2 | 1.0 | 2.0 |
| Contextualization vs Prior Work | 6 | 0.8 | 4.8 |
| Ethical / Broader Impact | 7 | 0.5 | 3.5 |
| **Total** | | **6.5** | **31.0** |

**Revised Weighted Average: 31.0 / 6.5 = 4.77**

### Revised Decision: **REJECT**

**Rationale:** The revised weighted average of 4.77 falls in the Reject range (4.0–5.5). The Soundness dimension drops from 5 to 3 after acknowledging (a) the exchangeability argument gap identified by the Theory Critic, (b) the algorithm-theory mismatch identified by the Naive Reader, and (c) the unanimous absence of experimental results. This is a stronger Reject than my original Borderline assessment.

**What would change the decision to Borderline/Accept:**
1. Experiments run with real numbers showing conditional coverage ~0.89 and set sizes meaningfully smaller than baselines
2. Figure 3 caption corrected to Qwen2.5-7B-Instruct
3. Theorem 1 proof revised to address the admissibility-selection exchangeability argument
4. Algorithm 1 aligned with Section 4.3's lifted score definition
5. Partition method unified and consistent across all sections
6. Code released before camera-ready

---

*— The Domain Expert (ML/Systems), cross-examined*
