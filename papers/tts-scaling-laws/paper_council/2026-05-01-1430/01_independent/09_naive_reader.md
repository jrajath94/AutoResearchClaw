# Naive Reader Review — STAIR: Per-Problem Discrete Structure in Test-Time Compute Scaling

**Reviewer:** The Naive Reader (1st-year PhD student)
**Paper:** STAIR_paper_neurips.pdf
**Date:** 2026-05-01
**Target:** NeurIPS 2026

---

## Calibration Note
~50% accept bar. I am calibrated to "is this paper learnable?" — not "is this paper Nobel-level novelty?" I try to flag where I got genuinely confused and where I had to re-read. If I had to re-read something 3+ times, it is a weakness even if experts find it obvious.

---

## Strengths

1. **Problem is clearly motivated with three testable assumptions (Section 1, pp. 1-2).** I appreciated that the paper names the three untested assumptions (smoothness, task-determination, description complexity) explicitly. This made it easy to understand what the paper was actually challenging. Most papers I've read bury their research questions in the third paragraph.

2. **Theorem (Section 3, p. 3-4) provides genuine theoretical insight.** The result that "every individual problem has discrete staircase scaling but population average is smooth" is counterintuitive and well-stated. The intuition (line 73: "even if every individual problem has a discrete staircase scaling curve, the population average can appear smooth") made me want to read the proof. The use of Prekopa's theorem is named, so I know where to look if I need the formal treatment.

3. **Figure 1 (Staircase) and Figure 3 (Heatmap) appear well-integrated into the narrative.** Figures are referenced in the flow of the argument (e.g., "Figure 1 illustrates this decomposition" type language). I could visualize what the staircase function looks like before reading the experimental section.

4. **Key findings are stated as numbered bullets (Abstract, pp. 1-2) with specific statistics.** The 97.7-99.3% figure is bold and specific. Even if I don't fully understand BIC yet, I understand this is a strong claim that the paper will back up with evidence. This helps me decide whether to trust the paper before diving into methods.

5. **Section 2 (Related Work) provides structured context.** The three groupings (scaling laws, information theory, adaptive inference) gave me a map of the literature before the paper's own contribution. I did not feel thrown into unfamiliar work without citation anchors.

---

## Weaknesses

### W1: Log-concavity assumption is asserted, not justified
**Issue:** Theorem 1 (p. 4) requires critical depth distribution to have log-concave PDF f_tau. The paper says this "justifies" the theorem but never checks whether real critical-depth distributions are actually log-concave.
**Where:** Section 3, Theorem 1 statement and proof (p. 4); also Open Question 1 (p. 10)
**Severity:** 3/5 — The theorem could be vacuous if the assumption fails for real distributions. The paper acknowledges this in Open Questions but does not even simulate a non-log-concave case to bound the error.
**Resolution:** Add empirical validation that critical-depth distributions on real tasks are approximately log-concave, or prove the theorem extends to broader distribution families.

### W2: BIC formulas lack a worked numerical example
**Issue:** The BIC_MSE and BIC_Bin formulas (p. 5) are presented without a single example of actual numbers. I had to re-read Definition 1 and the Bernoulli-trial model paragraph three times to understand what k_i(t_j) and phat_j actually represent.
**Where:** Section 4, BIC formulas (p. 5)
**Severity:** 4/5 — This is core methodology. If I cannot trace through one small example, I cannot verify the classification results myself. The paper gives me equations but not the computation.
**Resolution:** Add a single worked example: one problem, two budget levels, S=3 samples, showing how the two BIC values are computed and compared.

### W3: S=8 samples per cell may be insufficient for binomial-likelihood BIC
**Issue:** With only 8 samples per cell, the binomial-likelihood estimate phat_j = k_i(t_j)/S has substantial variance. BIC_Bin uses phat_j inside a log-likelihood, and small counts in either bucket (k=0 or k=8) produce degenerate log-likelihoods. The paper does not discuss this.
**Where:** Section 4, "S=8 independent samples" (p. 4); BIC_Bin formula (p. 5); Open Question 3 (p. 10)
**Severity:** 4/5 — The key claim (97.7-99.3% staircase preference) rests on BIC being reliable. If S=8 produces noisy phat estimates, the BIC comparison could be dominated by sampling noise rather than true model structure.
**Resolution:** Add a simulation: vary S in {4, 8, 16, 32}, report classification accuracy and stability. Show S=8 converges.

### W4: GSM8K n=100 is borderline for population-level generalization claims
**Issue:** The paper generalizes from 100 GSM8K problems to "per-problem discrete structure" as a property of LLM reasoning. Section 1 calls this a population-level phenomenon, but 100 problems is a small sample.
**Where:** Experimental Setup, Real LLM Inference (p. 7); Abstract claim 1 (p. 2)
**Severity:** 3/5 — I understand 100 problems is standard for GSM8K evaluation, but the paper makes strong claims about 97.7-99.3% of curves. If the distribution of problem complexities in GSM8K is not representative, the percentages could shift.
**Resolution:** Acknowledge this limitation explicitly and discuss what distribution of problem types the 100 GSM8K problems represent.

### W5: Qwen-only evaluation limits external validity
**Issue:** All real experiments use Qwen2.5-0.5B and Qwen2.5-1.5B. Jones 2021 (board games), Snell 2024 (test-time scaling) used different models. The paper's findings may be architecture-specific.
**Where:** Experimental Setup (p. 7); Open Question 5 (p. 10)
**Severity:** 3/5 — The paper acknowledges this in Open Questions, but does not even argue why Qwen is a reasonable representative. Is there something about Qwen's training that makes it a conservative choice?
**Resolution:** Provide 1-2 sentences on why Qwen models are representative of the broader class.

### W6: "Zero model forward passes for routing" glosses over gzip cost
**Issue:** Section 4 states STAIR uses "pre-inference gzip proxy with zero model forward passes." But gzip itself is not free. For a routing decision that happens before every inference call, the overhead matters.
**Where:** Section 4, routing description (p. 6); Open Question 6 (p. 10)
**Severity:** 3/5 — The token savings (+1.0% accuracy at 75% fewer tokens) only matter if gzip overhead doesn't eat the gains. I cannot evaluate the practical utility without timing numbers.
**Resolution:** Add latency comparison (gzip proxy latency vs. one model forward pass) and show gzip overhead is negligible.

### W7: Accuracy non-monotonicity claim is ambiguous in mechanism
**Issue:** Proposition (Section 3, p. 4) explains non-monotonicity via "budget-level answer truncation." But the paper does not show this is the actual mechanism — it could be reasoning drift, or simply sampling variance with S=8.
**Where:** Proposition, p. 4; Key finding 3 (Abstract, p. 2)
**Severity:** 3/5 — The claim "5.3-8.7% accuracy non-monotonicity" is used to argue against monotonic assumptions. But without knowing the mechanism, I cannot evaluate whether this is a genuine phenomenon or an artifact.
**Resolution:** Add an ablation: for cells showing non-monotonicity, trace the actual answer strings. Is answer truncation reproducible at the same budget? Is the non-monotonicity in the same direction?

### W8: Table column headers are not defined in the bundle
**Issue:** The results table (Section Key Results Summary) has entries like "MAPE improvement" and "paired Wilcoxon p=0.23" without defining what MAPE stands for or what the paired comparison is between.
**Where:** Key Results Summary table (p. 8)
**Severity:** 2/5 — MAPE is defined in the text but the table appears before the text that defines it. As a naive reader, I had to search backward to check.
**Resolution:** Add column headers or footnotes to the table. Move MAPE definition earlier.

### W9: Figures 1-7 have no captions in the bundle
**Issue:** The bundle lists Figures 1-7 but provides no caption text. I cannot evaluate whether the figures are self-contained or whether I would understand them without the full paper PDF.
**Where:** Figures section (p. 9)
**Severity:** 2/5 — For reproducibility, I need to know what each figure shows and how to read it. Without captions, I cannot assess figure quality.
**Resolution:** Include figure captions in the supplementary or add a figure guide.

### W10: Theorem proof is a one-line citation to Prekopa's theorem
**Issue:** Theorem 1 proof (p. 4) says "Proof uses Prekopa's theorem on log-concave distributions." This is the entire proof. I cannot verify the steps.
**Where:** Section 3, Theorem 1 proof (p. 4)
**Severity:** 4/5 — Even as a naive reader, I expect to be able to trace a proof. The theorem is central to the paper's theoretical contribution. A one-line citation is insufficient.
**Resolution:** Add at minimum a 5-7 step sketch: state Prekopa's theorem, show how the assumptions apply, derive the monotone increasing property, derive concavity, show t* = mode.

---

## Per-Rubric-Dimension Scores

| Dimension | Score (1-10) | Calibration Anchor | Rationale |
|---|---|---|---|
| 1. Originality / Novelty | 7 | "Substantial conceptual advance" | New framing of per-problem discrete structure; challenges three entrenched assumptions. Not a new paradigm (10) but clearly above incremental (4). |
| 2. Soundness | 6 | "Adequate methodology; some concerns flagged" | BIC approach is valid; S=8 and log-concavity gaps are real but not fatal. Main claims could survive revision. |
| 3. Significance | 7 | "Important within subfield; will be cited heavily" | If findings replicate, adaptive inference routing is a meaningful practical contribution. |
| 4. Clarity | 6 | "Mostly clear; some sections require re-reading" | Core narrative is clear. But BIC formulas need worked example; theorem proof needs sketch; table headers need labels. |
| 5. Reproducibility | 5 | "Sufficient detail to reproduce" | Synthetic data setup is described; real data uses standard benchmarks; but no code release mentioned, no seeds reported, no S=8 sample count justification. |
| 6. Contextualization vs prior work | 7 | "Strong coverage; correctly positioned" | Three related-work categories are well-organized. Main misses are around Snell 2024 and Jones 2021 methodology gaps. |
| 7. Ethical / Broader Impact | 6 | "Boilerplate" | Standard broader impact statement; no specific ethical concerns for LLM reasoning work; not thoughtful enough to hit 8. |

**Weighted Average:** (7×1.0 + 6×1.5 + 7×1.0 + 6×0.7 + 5×1.0 + 7×0.8 + 6×0.5) / 5.5 = (7 + 9 + 7 + 4.2 + 5 + 5.6 + 3) / 5.5 = **40.8 / 5.5 ≈ 7.4**

**Decision range:** 6.5–8.0 → **Accept**

---

## Pointed Questions (Actually Basic)

1. **What does symbol B mean in the BIC formula?** The paper uses B as the number of budget levels but never defines it. I had to infer B = number of token budgets from context. Please define explicitly: B = number of distinct token budgets tested.

2. **In BIC_Bin, what is phat_j exactly?** Is it k_i(t_j)/S (fraction correct at budget t_j)? And is k_i the number of correct samples? The notation is introduced in the Bernoulli-trial model paragraph but not in the formula itself. I had to read Definition 1 to connect the two.

3. **Why Δ=2 specifically for BIC threshold?** The paper cites Raftery's scale but does not explain why "positive evidence" (Δ>2) is the right threshold for this problem. Would "strong evidence" (Δ>6) change the 97.7-99.3% claim significantly? This seems easy to test.

4. **What does "sequential computation depth" mean for real problems?** On synthetic data, circuit depth is well-defined. On GSM8K, the paper uses "step count" — but whose step count? The model's? A post-hoc annotator's? If step count is defined by the specific CoT prompting used, the ρ=0.96 result may be brittle.

5. **If individual curves are discrete staircase, why use sigmoid as the baseline?** The paper compares staircase vs. sigmoid. But sigmoid is a 3-parameter continuous model — if individual curves are discrete, sigmoid is misspecified from the start. Would a 1-step model (a(t) = alpha_0 for all t) also beat sigmoid?

6. **Can you show one complete classification example?** Take one problem, show the 8 samples at 3 temperatures, compute both BIC values, show the comparison. This would resolve W2 entirely.

7. **What is the runtime of the gzip proxy in practice?** If the gzip proxy is "zero model forward passes" but takes 500ms per problem and the model inference takes 200ms, the overhead is not negligible. Can you report actual wall-clock times?

---

## Falsifiability Test

**"What evidence would change my decision?"**

My current decision is **Accept**, primarily because the conceptual framework is sound and the empirical evidence on synthetic data is strong. I would change to **Borderline** if:
- A follow-up simulation shows S=8 produces unstable BIC classification (e.g., bootstrapped classification flips more than 20% of the time across random seeds)
- A reviewer shows that critical-depth distributions on real GSM8K problems are clearly not log-concave and the population curve does NOT appear smooth
- The paper's Qwen-only claim fails to replicate on even one additional model family (e.g., Llama-3B), showing the staircase structure is architecture-specific

I would change to **Strong Accept** if:
- The authors provide a worked BIC example (W2 resolved)
- A sensitivity analysis across S ∈ {4, 8, 16, 32} shows S=8 is sufficient for stable classification
- At least one additional benchmark dataset (e.g., MATH) shows similar staircase dominance percentages

I would change to **Reject** if:
- The authors cannot reproduce their BIC percentages when S is increased to 16 or 32
- Log-concavity is tested and rejected on real problem distributions
- The token savings (+1.0% accuracy at 75% fewer tokens) fail to replicate on a held-out test set of 200+ problems

---

## Confidence

**3/5** — I am confident in the readability assessment and most weaknesses. I am less confident in the soundness assessment because I lack the statistical background to evaluate whether S=8 is sufficient for binomial-likelihood BIC without a simulation. I would want to see a sensitivity analysis before calling this a strong accept.

---

## Decision

**Accept**

The paper offers a genuine conceptual contribution (discrete per-problem structure vs. smooth population curves) that is learnable by a naive reader and supported by both theory and empirical evidence. The main weaknesses — BIC worked example, S=8 justification, log-concavity validation — are addressable with modest additions. If the authors address W2, W3, and W10 in revision, this could be a strong accept.

---

*The Naive Reader (1st-year PhD student)*
