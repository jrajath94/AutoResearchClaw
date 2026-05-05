# Cross-Examination — Domain Expert ML Review

**Reviewer:** The Domain Expert (ML/Systems)
**Date:** 2026-05-01
**Paper:** STAIR: Per-Problem Discrete Structure in Test-Time Compute Scaling for LLM Reasoning
**Target Venue:** NeurIPS 2025

---

## 1. Disagreements with At Least 2 Other Reviewers

### D1: S=8 sample size severity — I underrated this
- **My position:** Severity 3/5 — "likely underpowered"
- **Others' positions:**
  - Statistical Rigorist: 5/5 — "most serious methodological concern"
  - Big Picture Editor: 4/5 — "makes the binomial BIC unreliable"
  - Adversarial Practitioner: 4/5 — "insufficient for generalization claims"
  - Naive Reader: 4/5 — "S=8 may be insufficient for binomial-likelihood BIC"
  - Reproducibility Archeologist: (implied in W3, 5/5 on near-random accuracy regime)
- **Disagreement:** I framed S=8 as a moderate concern. The majority view is that this is a critical or severe weakness. After reading Reproducibility Archeologist's W3 (near-random accuracy), I now understand the problem is even worse than I stated — at 2-3% accuracy with S=8, most cells have 0-1 successes, making the binomial likelihood essentially degenerate. I was too lenient.
- **Resolution:** Upgrade S=8 severity to 4-5/5.

### D2: Variation-subset selection bias — I missed the mechanism
- **My position:** W8 (severity 3/5) — "bootstrap CIs on 28% subset need clarification"
- **Others' positions:**
  - Big Picture Editor: W1 (5/5) — "72% of cells have zero variation, trivially favoring staircase, inflating headline number"
  - Adversarial Practitioner: W7 (4/5) — "post-hoc selection inflates staircase preference"
  - Reproducibility Archeologist: W2 (3/5) — "circular selection bias"
- **Disagreement:** I acknowledged the bootstrap CI issue but did not connect it to the fundamental selection bias: the 72% of cells with zero accuracy variation are excluded because they are "uninformative," but including them would trivially favor staircase (a flat line is a special case of staircase with 2 parameters vs sigmoid with 3). The 97.7-99.3% headline number includes these zero-variation cells while the 87.3-93.1% "variation subset" is the more honest figure. I understated this.
- **Resolution:** Adopt Big Picture Editor's framing: the headline number is inflated by zero-variation cells, and the variation-subset result needs tightened CIs.

### D3: Token savings claim lacks statistical characterization
- **My position:** I flagged W7 ("zero model forward passes misleading") but did not flag the token savings statistical test absence
- **Others' positions:**
  - Statistical Rigorist: W7 (4/5) — "75% token savings has no p-value, CI, or per-problem statistics"
  - Big Picture Editor: W2 (5/5) — "p=0.23 misrepresented as equivalence; token savings needs independent test"
  - Adversarial Practitioner: W3 (4/5) — "p=0.23 as equivalence is statistical error"
- **Disagreement:** I did not explicitly flag that the token savings (128.6 vs 512 tokens, 75% reduction) is reported as a point estimate without any measure of variability or statistical test. The Wilcoxon p=0.23 tests accuracy, not token savings. Token savings is deterministic given the allocator algorithm and gzip threshold — but the distribution across problems is not characterized.
- **Resolution:** Add W11: Token savings claim needs per-problem statistics (mean, SD, median, IQR of token usage) and its own statistical test.

---

## 2. Issues Others Missed That I Now Want to Add

### O1: Near-random accuracy regime undermines real LLM BIC analysis (NEW, from Reproducibility Archeologist W3)
- **Issue:** Qwen-0.5B achieves 2-3% accuracy on GSM8K; Qwen-1.5B achieves 1.9-6.5%. With S=8 samples per cell, most cells have 0-2 successes. The BIC model comparison (staircase vs sigmoid) on these near-random binary outcomes is fitting noise. A staircase-favoring BIC classification at near-random accuracy levels is not evidence of discrete per-problem structure — it is evidence that both models fit poorly and BIC prefers the simpler one.
- **Severity:** 5/5 — This is the most devastating critique in the entire review set. It applies to every real LLM result in the paper.
- **Why others missed it:** Statistical Rigorist focused on S=8 variance in isolation; Big Picture Editor focused on multiple-testing; Adversarial Practitioner focused on deployment concerns. Only Reproducibility Archeologist connected low accuracy → degenerate binomial likelihood → meaningless BIC comparison.
- **Resolution:** Run BIC on larger models (Qwen-7B or Llama-3-8B) where accuracy is >30%, or acknowledge that the real LLM BIC results are uninterpretable at current accuracy levels.

### O2: Code-data mismatch (NEW, from Reproducibility Archeologist W1)
- **Issue:** real_experiment.py hardcodes N_PROBLEMS=40 and SAMPLES_PER_CELL=4, but the paper reports 100 problems with 8 samples/cell. The 100-problem results exist only as stored .npy files and JSON summaries — there is no reproducible script that generates the exact numbers in the paper.
- **Severity:** 4/5 — This is a reproducibility crisis. The published code cannot reproduce the published results.
- **Why I missed it:** I reviewed the paper, not the code. This is an oversight in my review process.
- **Resolution:** Release the actual inference script with correct constants (N_PROBLEMS=100, SAMPLES_PER_CELL=8), or explain the discrepancy.

### O3: No failure mode analysis for the STAIR allocator (NEW, from Adversarial Practitioner W4)
- **Issue:** STAIR reduces tokens by 75% but there is zero analysis of what happens when it misroutes. When STAIR terminates early on a problem the model would have solved correctly at higher token budget, this is a silent failure. No failure log, no per-problem breakdown, no analysis of whether failures concentrate on specific problem types.
- **Severity:** 4/5 — For a paper claiming practical deployment value, absence of failure analysis is a critical gap.
- **Why others missed it:** Only Adversarial Practitioner gave this 5/5. The other reviewers focused on statistical methodology.
- **Resolution:** Add case analysis of misrouted problems. Report per-problem failure rate when STAIR undershoots. Is failure random or concentrated on hard problems?

### O4: p99/tail latency absent (NEW, from Adversarial Practitioner W8)
- **Issue:** All latency results are mean or median. For production deployment of compute budget routing, p99 determines on-call burden. When STAIR says "done" but the model needed more tokens, what is the tail behavior?
- **Severity:** 4/5 — Without p99, the paper cannot be evaluated for production deployment.
- **Why others missed it:** Statistical reviewers focus on inference validity, not operational deployment.
- **Resolution:** Report per-budget p50/p95/p99 latency breakdowns.

### O5: Theorem 1 conclusion vs applied claim — theoretical inconsistency I raised but underemphasized (W10)
- **My concern:** Theorem 1 proves the elbow is a population-level property determined by log-concave F_τ. But the applied framework does per-problem routing. If the elbow is purely population-level, per-problem routing has no theoretical basis from Theorem 1 alone.
- **Why others missed it:** Statistical Rigorist, Big Picture Editor, and Adversarial Practitioner all acknowledge the Theorem is sound but do not flag this specific tension between Theorem conclusion and applied claim. Naive Reader doesn't have the background.
- **Resolution:** The paper needs to clarify: does each problem have its own critical depth τ_i (violating Theorem 1's assumptions), or does the Theorem merely show that population smoothness does NOT require individual smoothness?

---

## 3. My Positions Updated After Seeing Others

### U1: Upgrade S=8 severity from 3/5 to 5/5
After seeing the Statistical Rigorist's 5/5 rating and Big Picture Editor's 4/5, combined with Reproducibility Archeologist's W3 showing near-random accuracy (2-6%), I now understand S=8 is not just "likely underpowered" — it is critically insufficient for the actual accuracy regime. At 2-3% accuracy with 8 Bernoulli trials, the binomial likelihood is degenerate. This upgrades my concern from moderate to critical.

### U2: Adopt Big Picture Editor's framing of variation-subset selection bias
I originally flagged the bootstrap CI issue on the variation subset (W8). But Big Picture Editor W1 (5/5) correctly identifies the deeper problem: the 72% of cells with zero variation are excluded because they are "uninformative," yet including them would trivially favor staircase. The 97.7-99.3% headline is inflated by these cells. I should have stated this more forcefully.

### U3: The Theorem is the paper's most lasting contribution (aligning with Big Picture Editor W10)
Big Picture Editor says "The Theorem is the paper's most lasting contribution but is underemphasized." I agree. My review listed it as Strength 1, but I did not explicitly say the empirical claims are fragile while the Theorem is robust. The paper would be stronger if reframed around the Theorem.

### U4: p=0.23 as equivalence — align with Statistical Rigorist and Big Picture Editor
I did not explicitly flag this in my weaknesses. Statistical Rigorist W1 and Big Picture Editor W2 both correctly identify that p=0.23 means "no significant difference detected," not "equivalence." The TOST procedure is the correct tool. The token savings (75%) is the legitimate finding; the accuracy equivalence claim is statistically misrepresented.

---

## 4. Claim/Weakness with Most Reviewer Agreement (Consensus Signal)

### Consensus Finding: S=8 sample size is critically insufficient

**Agreement count: 6/6 reviewers**

| Reviewer | Explicit Rating | Notes |
|----------|-----------------|-------|
| Domain Expert (mine) | 3/5 | "Likely underpowered" — too lenient |
| Statistical Rigorist | 5/5 | "Most serious methodological concern" |
| Adversarial Practitioner | 4/5 | "Insufficient for generalization claims" |
| Big Picture Editor | 4/5 | "Makes binomial BIC unreliable" |
| Naive Reader | 4/5 | "S=8 may be insufficient" |
| Reproducibility Archeologist | 5/5 (implied via W3 on near-random accuracy) | Near-random regime compounds the problem |

**Why this is the consensus signal:** Every reviewer independently flagged S=8 as a problem. The Statistical Rigorist gave it the highest severity (5/5); only I gave it 3/5. The consensus is that S=8 is a critical weakness, not a moderate one.

**Secondary consensus (also 6/6): Qwen-only evaluation limits generalization**
| Reviewer | Severity |
|----------|----------|
| Domain Expert | 3/5 |
| Statistical Rigorist | 2/5 |
| Adversarial Practitioner | 4/5 |
| Big Picture Editor | 3/5 |
| Naive Reader | 3/5 |
| Reproducibility Archeologist | (implied) |

**Tertiary consensus (5/6): Log-concavity assumption unjustified**
| Reviewer | Severity |
|----------|----------|
| Domain Expert | 4/5 |
| Statistical Rigorist | 3/5 |
| Adversarial Practitioner | 3/5 |
| Big Picture Editor | 3/5 |
| Naive Reader | 3/5 |

**Quaternary consensus (5/6): Multiple-testing correction absent**
This was flagged by Statistical Rigorist (5/5), Big Picture Editor (4/5), Adversarial Practitioner (3/5), Reproducibility Archeologist (2/5), and my own W9 (2/5).

---

## Summary of Cross-Examination Findings

**Key disagreements with other reviewers:**
1. I was too lenient on S=8 (3/5 vs their 4-5/5) — upgrading to 5/5
2. I missed the variation-subset selection bias mechanism — adopting Big Picture Editor's framing
3. I did not flag the token savings statistical absence — adding as W11

**Issues only I (or few) raised:**
- O5: Theorem 1 conclusion vs applied claim theoretical tension (only me)
- O1: Near-random accuracy regime (only Reproducibility Archeologist, but I now adopt fully)
- O2: Code-data mismatch (only Reproducibility Archeologist)

**Consensus signal:** S=8 sample size is the most agreed-upon weakness (6/6), followed by Qwen-only evaluation (6/6), log-concavity (5/6), and multiple-testing correction (5/6).

---

*Sign-off: The Domain Expert (ML/Systems) — Cross-Examined*