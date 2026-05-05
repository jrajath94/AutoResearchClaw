# Cross-Examination Review — The Adversarial Practitioner (Updated)

**Paper:** SemCP: Coverage Guarantees Over Meanings, Not Strings
**Date:** 2026-05-01 (Cross-Examination Round)
**Original Review:** `/Users/rj/research-claw/papers/semcp-conformal-prediction/paper_council/2026-05-01-1200/01_independent/05_adversarial_practitioner.md`

---

## 1. Disagreements with At Least 2 Other Reviewers

### D1: GPT-2/Qwen Mismatch Is a Factual Error, Not Just a Clarity Issue

**My position (original):** W2 severity 4/5 — direct factual contradiction between Figure 3 caption and experimental setup.

**Theory Critic (02) treats it as a copy-paste issue but does not escalate to severity 4+.**
> "This is a concrete factual error that suggests copy-paste from a prior draft." — Theory Critic, severity 4

**Empirical Skeptic (03) agrees on severity 4/5:**
> "An incorrect caption raises questions about what else was copy-pasted without verification." — Empirical Skeptic

**Methodological Hawk (01) and Statistical Rigorist (04) both assign severity 4/5.**

**Disagreement:** My position matches 7 of 9 reviewers (all who flag this). The Naive Reader (09) gives it only severity 3/5. The Big Picture Editor (08) gives it severity 3/5 — treating it as "rushed preparation" rather than a factual error. I maintain severity 4/5 because a figure caption that names the wrong model is a factual claim about what experiment was run, not merely a presentation issue.

---

### D2: Near-Zero Coverage vs 33% Set-Size Reduction Contradiction

**My position (original):** W3 severity 4/5 — these two claims are mutually incoherent; set size reduction is meaningless at near-zero coverage.

**Statistical Rigorist (04) independently arrives at identical conclusion with severity 5/5:**
> "Marginal coverage and set size reduction are mutually incoherent at near-zero coverage. If coverage is near zero, set size comparisons are meaningless." — Statistical Rigorist, severity 5/5

**Big Picture Editor (08) also flags this with severity 4/5:**
> "Near-zero coverage contradicts set-size claim... you cannot simultaneously claim a method produces meaningfully smaller sets AND that coverage is near-zero." — Big Picture Editor

**Empirical Skeptic (03) flags it as severity 4/5.**
> "You cannot measure set size reduction if coverage is near-zero." — Empirical Skeptic

**Disagreement:** Three reviewers (Empirical Skeptic, Statistical Rigorist, Big Picture Editor) independently flag the same incoherence. The Theory Critic (02) mentions near-zero coverage but does not flag this as a critical contradiction — only as a TODO_NUM issue. I disagree with any reviewer who treats these as separable concerns. They are logically incompatible claims in the same document.

---

### D3: Kernel Bandwidth Grid Is Too Coarse

**My position (original):** W6 severity 3/5 — 6 values over 2 orders of magnitude is insufficient guidance.

**Naive Reader (09) independently raises a related concern:**
> "Bandwidth grid is {0.1, 0.3, 0.5, 1.0, 2.0, 4.0} — 6 values over 2 orders of magnitude with no justification." — Naive Reader (corroborates W6)

**Reproducibility Archeologist (07) flags the bandwidth optimization procedure as unclear:**
> "The relationship between training split, calibration set, and held-out set for bandwidth optimization is not clearly delineated." — Reproducibility Archeologist, severity 3/5

**Disagreement:** Only 3 reviewers flag this issue. The other 6 either accept the grid as-is or do not comment. I maintain that a coarser-than-necessary grid is a real practical limitation — a production system implementing SemCP has no guidance on bandwidth selection for new domains. This is a legitimate practitioner concern that others underweight.

---

### D4: Algorithm 1 Does Not Match Section 4.3 Theory

**My position (updated after seeing Naive Reader's analysis):** This is a more serious structural inconsistency than I originally assessed.

**Naive Reader (09) W4:**
> "Algorithm 1 computes contrastive between-cluster score; Section 4.3 defines within-cluster minimum score. These are structurally different." — Naive Reader, severity 4/5

**I did not flag this in my original review.** After reading the Naive Reader's analysis, I find the discrepancy concrete:
- Section 4.3, Equation 2: `min_{y' in [y]_s intersect {y_1,...,y_K}} s(x, y')` — within-cluster minimum
- Algorithm 1 line 180: `1 - max_{c' != c_i^*} kappa_sigma(bars_phi_{c_i^*}, bars_phi_{c'})` — contrastive between-cluster score

**Disagreement with my original review:** I rated Soundness 3 primarily on TODO_NUM grounds. I did not identify the Algorithm-theory mismatch as a separate structural issue. The Naive Reader's severity 4/5 on this point is warranted and I am incorporating it.

---

## 2. Issues Others Missed That I Want to Add

### I1: DeBERTa-v2-xlarge-MNLI Is a Heavy Operational Dependency (W8)

I raised W8 on the NLI model's O(K^2) inference cost (100 NLI forward passes per calibration/test instance with K=10). **No other reviewer flagged this as an operational production concern.** The Methodological Hawk (01), Statistical Rigorist (04), and Theory Critic (02) all focused on the NLI threshold sensitivity and transitivity assumptions, but none addressed the inference latency and throughput implications for production deployment.

**Why this matters:** A practitioner reading this paper would implement SemCP and immediately encounter a latency bottleneck they cannot debug without explicit documentation. The paper provides no p50/p95/p99 latency characterization.

### I2: K=10 Tail Coverage Analysis Missing (W9)

I raised W9 on K=10 being potentially insufficient for tail coverage. **No other reviewer modeled the tail behavior explicitly.** The Theory Critic (02) mentions p_A as a ceiling but does not analyze how p_A scales with K.

**Concrete math:** If per-sample correctness is 0.30, p_A = 0.30^10 ≈ 0.000059 — effectively zero. A production system targeting 90% marginal coverage with a 30% per-sample correct model needs K >> 10 to achieve meaningful admissibility rates. The paper's K=10 budget is not analyzed for tail behavior.

### I3: NLI Partition Transitivity Assumption Is Underanalyzed

I stated the transitivity closure via Union-Find is "correctly applied" — this was too weak. The Theory Critic (02) raises this explicitly (severity 3/5) and it is a genuine gap:

> "DeBERTa-v2-xlarge-MNLI is not logically consistent — NLI models are known to have non-transitive behavior due to annotation artifacts and dataset biases." — Theory Critic

**I partially agree but disagree on severity.** I think the severity is 2-3, not 5. The Union-Find closure is a standard and reasonable approach even with imperfect transitivity. But the paper does not analyze how partition errors propagate to coverage guarantee violations.

---

## 3. My Positions Updated After Seeing Consensus

### Soundness Score

**Original:** 3/10 (primarily due to TODO_NUM and figure caption mismatch)

**Updated after consensus:** 3/10 is correct. 7 of 9 reviewers assign Soundness ≤ 5. The Algorithm-theory mismatch (Naive Reader's W4) is a genuine structural issue I undercounted. The TODO_NUM problem is universal.

However, I want to explicitly note: **the theory (Theorem 1, exchangeability arguments, admissibility decomposition) is sound.** The Soundness score of 3 reflects the empirical verification being absent, not a fatal theoretical flaw. If the experiments were run and the results held, Soundness would be 6-7.

### Weighted Average Recalculation

Using updated assessments:
| Dimension | Original | Updated | Rationale |
|---|---|---|---|
| Originality / Novelty | 7 | 7 | Consensus: 7-8 range; no change needed |
| Soundness | 3 | 3 | Universal agreement this dimension is compromised; Algorithm-theory mismatch adds justification |
| Significance | 6 | 6 | Consensus: 5-7 range; maintaining 6 with TODO_NUM caveat |
| Clarity | 6 | 5 | Adding Algorithm-theory mismatch and partition rule inconsistency; downgraded |
| Reproducibility | 4 | 3 | Universal agreement this is severely compromised; code not released |
| Contextualization | 6 | 6 | Consensus: 6-8 range; maintain 6 |
| Ethical / Broader Impact | 6 | 6 | No change |

**Updated WA:** `(7×1.0 + 3×1.5 + 6×1.0 + 5×0.7 + 3×1.0 + 6×0.8 + 6×0.5) / 6.5 = (7 + 4.5 + 6 + 3.5 + 3 + 4.8 + 3) / 6.5 = 31.8 / 6.5 ≈ **4.89**`

**Decision: Reject** (4.89 falls below 5.0 threshold)

---

## 4. Claim/Weakness With Most Reviewer Agreement (Consensus Signal)

**UNANIMOUS: TODO_NUM placeholders in all empirical results** — all 9 reviewers flag this with severity 4-5/5.

This is the strongest consensus signal in this review cycle. Every reviewer — regardless of theoretical orientation, concern style, or score level — identifies the absence of experimental results as the primary blocking issue.

**Secondary consensus (7 of 9):** Figure 3 caption inconsistency (GPT-2 vs Qwen2.5-7B-Instruct) and Section 5.1/Discussion text inconsistency.

**Tertiary consensus (4 of 9):** Near-zero coverage claim is mutually incoherent with the 33% set-size reduction claim.

---

## 5. Final Updated Scores and Decision

| Dimension | Score | Calibration Anchor |
|---|---|---|
| Originality / Novelty | 7 | Substantial conceptual advance; quotient-space CP is genuinely novel |
| Soundness | 3 | Theory is correct but unverifiable; empirical methodology cannot be assessed; Algorithm-theory mismatch adds structural concern |
| Significance | 6 | Important contribution if empirical results hold; admissibility decomposition is broadly useful |
| Clarity | 5 | Algorithm-theory mismatch and partition rule inconsistency are real clarity bugs |
| Reproducibility | 3 | Code not released; all numbers are placeholders; hyperparameter table has TODO_HOURS |
| Contextualization vs Prior Work | 6 | Strong coverage of ConU/SAFER/LofreeCP/TECP; semantic entropy gap acknowledged |
| Ethical / Broader Impact | 6 | Adequate boilerplate |

**Weighted Average: 4.89 — Reject**

**Decision: Reject**

**Rationale unchanged from original:** The theoretical contribution is real and the admissibility-coverage decomposition is valuable. However, the paper cannot be accepted without experimental results. The Algorithm-theory mismatch (identified by Naive Reader, now incorporated) adds a structural clarity concern that compounds the TODO_NUM problem.

**Conditional upgrade path:** If authors complete experiments, resolve the Algorithm 1 vs Section 4.3 discrepancy, fix all figure captions, and release code, this is an Accept. The theoretical foundation is sound enough to warrant another look.

---

*Cross-exam review completed. Disagreements incorporated: D1-D4. New issues added: I1-I3. Scores updated: Soundness 3 sustained with additional justification; Clarity 6→5; Reproducibility 4→3. WA revised from 5.15 to 4.89.*

— The Adversarial Practitioner (Cross-Examined)