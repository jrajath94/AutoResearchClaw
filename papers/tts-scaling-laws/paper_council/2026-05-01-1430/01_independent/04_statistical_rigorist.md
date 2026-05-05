# Statistical Rigorist Review — STAIR Paper

**Paper:** STAIR: Per-Problem Discrete Structure in Test-Time Compute Scaling for LLM Reasoning
**Date:** 2026-05-01
**Reviewer type:** Statistical Rigorist (Gelman/Ioannidis tradition)

---

## Calibration Anchor

I apply strict thresholds: acceptance requires honest uncertainty quantification, effect sizes with CIs that exclude zero, and multiple-testing corrections. Given this paper's claims are primarily about pattern detection (BIC model selection) rather than causal effects, I focus on whether the classification results and effect estimates are robust to sampling noise.

---

## Strengths

1. **Theorem is a genuine mathematical contribution** (Section 3, Theorem): The proof that log-concave critical-depth distributions imply smooth population curves even when individual curves are discrete is mathematically sound and non-trivial. This is a real contribution.

2. **Explicit separation of accuracy non-monotonicity from MI non-monotonicity** (Section 3, Proposition): The authors explicitly clarify they are NOT claiming DPI violation and are not estimating mutual information. This careful distinction is rare and commendable — it avoids a common pitfall in information-theoretic reasoning about LLMs.

3. **BIC-based model selection with multiple likelihood frameworks** (Section 4): Reporting results under both MSE-based and binomial-likelihood BIC across a range of thresholds (Δ ∈ {0, 1, 2, 3, 4, 6, 10}) is methodologically honest. This is what I want to see.

4. **Theoretical prediction about synthetic vs real divergence** (Key finding 4): The claim that computational depth (ρ=0.96) predicts scaling elbows on synthetic data but gzip/step count (ρ=0.147) does not on real GSM8K is a genuinely interesting finding that could guide future work.

5. **Conservative non-monotonicity prevalence estimate** (Key finding 3): Reporting 5.3-8.7% (not claiming 95% CI bounds) with explicit caveat that this is NOT MI non-monotonicity shows restraint.

---

## Weaknesses

### W1: Paired Wilcoxon p=0.23 reported as "matches fixed-budget-512 accuracy"
- **Issue:** The main real-world result (Key finding 6) says STAIR "matches fixed-budget-512 accuracy (0.075 vs 0.065, Δ+1.0%, paired Wilcoxon p=0.23)". A p-value of 0.23 means the difference is NOT statistically significant. This is being dressed as a win.
- **Where:** Abstract and Section 6 experimental results
- **Severity:** 4/5
- **Resolution:** Report as "no statistically significant difference detected (p=0.23)" with explicit CI on the accuracy difference, e.g., "Δ=1.0pp, 95% CI [-0.5pp, 2.5pp]". The token savings claim (75% fewer) is the real finding and should be tested independently with its own p-value.

### W2: S=8 samples per cell is likely underpowered for binomial BIC
- **Issue:** With only 8 Bernoulli trials per cell, the binomial likelihood estimate has enormous variance. The probability of misclassifying staircase vs sigmoid under the binomial model is not negligible.
- **Where:** Section 4: "S=8 independent samples (Bernoulli-trial model)"
- **Severity:** 5/5
- **Resolution:** Run a sensitivity analysis at S={16, 32, 64}. If results are stable across S, the claim is robust. If classification rates change substantially, the conclusion is sampling-noise-dependent.

### W3: Bootstrap CIs on the variation-subset results are extremely wide
- **Issue:** For Qwen-0.5B at τ=0.5, the bootstrap CI on the variation subset is [0.615, 1.000] — this is essentially "anywhere from 62% to 100%". The "99.3% best fit" headline comes from the overall set (which includes cells with zero variation, trivially favoring staircase), but the variation-subset CI is so wide as to be uninformative.
- **Where:** Key finding 2, with bootstrap CIs
- **Severity:** 4/5
- **Resolution:** Either (a) increase sample size to tighten CIs, or (b) report the CI width explicitly and acknowledge the uncertainty.

### W4: Multiple testing across 100 problems × 3 temperatures × 2 models — no correction reported
- **Issue:** The paper runs BIC model selection on 300 curves (100 problems × 3 temperatures). Under the Garden of Forking Paths model, every (problem, temperature) cell is a separate hypothesis test. No multiple-testing correction (Benjamini-Hochberg, Bonferroni) is applied or even mentioned.
- **Where:** Section 4 methodology and Key findings 1-2
- **Severity:** 5/5
- **Resolution:** Apply BH correction across the 300 model selection decisions. Report the false-discovery rate. Acknowledge that the high classification rates (97.7-99.3%) may partially reflect the multiple-testing structure.

### W5: BIC threshold Δ=2 is misapplied from Raftery's social-science scale
- **Issue:** The paper invokes Raftery's scale for BIC Δ=2 as "positive evidence" — but Raftery's guidelines were developed for logistic regression in social science with specific sample sizes and context. There is no validation that this threshold is appropriate for high-dimensional sigmoid vs low-dimensional staircase comparison in LLM scaling. The threshold choice may be data-snooped.
- **Where:** Section 4: BIC classification threshold discussion
- **Severity:** 3/5
- **Resolution:** Justify the threshold with theoretical grounding or show robustness across a clearly motivated range (e.g., BIC is widely used without fixed thresholds; report the actual Δ values and let readers assess).

### W6: The Theorem's log-concavity assumption is unmotivated
- **Issue:** Theorem 1 requires critical-depth distributions to be log-concave. The paper does not validate this assumption on real data. If the actual distribution of critical depths is multimodal or heavy-tailed, the Theorem's conclusions do not hold. The theorem is interesting but the empirical relevance is unestablished.
- **Where:** Section 3, Theorem statement and assumptions
- **Severity:** 3/5
- **Resolution:** Test log-concavity of critical-depth estimates empirically (e.g., using Baringhaus-Henze test or visual inspection). If it fails, note this and discuss what the population curve would look like under non-log-concave alternatives.

### W7: Token savings claim (75%) lacks statistical test
- **Issue:** Key finding 6 claims 75% fewer tokens (128.6 vs 512). This is an enormous claimed effect but there is no p-value, CI, or statistical test reported. We only have a single paired comparison on 100 problems. Under the null (no difference in token usage pattern), the observed ratio is deterministic given the allocator algorithm — but the variability across problems is not characterized.
- **Where:** Key finding 6 and Section 6 allocator comparison
- **Severity:** 4/5
- **Resolution:** Report per-problem token usage statistics (mean, SD, median, IQR). If the allocator is deterministic given the gzip proxy, characterize the distribution of token savings across problems.

### W8: GSM8K n=100 — limited scope for generalization claims
- **Issue:** The paper makes broad claims about "per-problem scaling curves" based on 100 GSM8K problems. GSM8K is a specific benchmark (grade-school math). The finding that 97.7-99.3% of curves favor staircase on GSM8K may not generalize to other domains (coding, reasoning, factuality).
- **Where:** Experimental setup and throughout discussion
- **Severity:** 3/5
- **Resolution:** Qualify generalization claims explicitly: "On GSM8K (n=100), we observe that...". Do not claim "per-problem scaling curves" universally without domain qualification.

### W9: No variance estimate across seeds for synthetic experiments
- **Issue:** The synthetic experiment uses 5 seeds but results are reported as point estimates (ρ=0.96) without variance across seeds. If the 5 seeds produce ρ values of {0.91, 0.94, 0.96, 0.98, 0.99}, the conclusion is stable. If they produce {0.72, 0.85, 0.96, 0.99, 1.00}, the median is stable but the variance is enormous.
- **Where:** Section 5 synthetic data results, Key finding 4
- **Severity:** 3/5
- **Resolution:** Report median and IQR or mean and SD of the correlation estimate across the 5 seeds.

### W10: Qwen models only — single model family
- **Issue:** All real experiments use Qwen2.5-0.5B and Qwen2.5-1.5B. These are small models (0.5B and 1.5B parameters). The findings may not hold for larger models (Claude, Gemini, GPT-4 class) where scaling behavior could differ qualitatively.
- **Where:** Throughout real LLM experiments
- **Severity:** 2/5 (lower severity because this is a practical constraint, but claims should be qualified)

---

## Per-Rubric Dimension Scores

| Dimension | Score | Calibration Anchor |
|-----------|-------|-------------------|
| **Originality / Novelty** | 7 | The staircase decomposition concept and BIC-based per-problem fitting is a non-obvious framing. Substantial conceptual advance over smooth-scaling priors. |
| **Soundness** | 5 | Methodology is adequate but S=8 samples, no multiple-testing correction, and the p=0.23 being reported as a win are serious gaps. The main claims are not fully trustworthy as presented. |
| **Significance** | 7 | If the findings are real, they have major implications for test-time compute research. The theorem alone is worth a paper. But generalization to larger models and diverse domains is unvalidated. |
| **Clarity** | 8 | Well-organized with clear definitions, theorem statement, and methodology. The Supplementary Materials must be referenced to verify the BIC details. |
| **Reproducibility** | 6 | BIC formulas are given but hyperparameters (temperature, seed, solver settings) partially specified. Code not explicitly mentioned as released. |
| **Contextualization vs Prior Work** | 7 | Good positioning vs Snell 2024, Brown 2024, Polyanskiy 2024. The gap between description complexity and computational depth is clearly articulated. |
| **Ethical / Broader Impact** | 6 | Standard Broader Impact statement; no specific ethical concerns flagged, which is acceptable for this type of theoretical/empirical work. |

**Weighted Average:** (7×1.0 + 5×1.5 + 7×1.0 + 8×0.7 + 6×1.0 + 7×0.8 + 6×0.5) / (1.0+1.5+1.0+0.7+1.0+0.8+0.5) = (7 + 7.5 + 7 + 5.6 + 6 + 5.6 + 3) / 6.5 = 41.7 / 6.5 = **6.42**

---

## Pointed Questions for the Authors

1. **The paired Wilcoxon test on the real GSM8K result yields p=0.23 (not significant). How do you justify reporting this as "matches fixed-budget-512 accuracy" rather than "no statistically significant difference detected"?** The token savings (75%) is the more defensible finding — was it tested independently?

2. **With S=8 samples per cell, what is the probability of misclassification under the binomial model when the true model is staircase (or sigmoid)?** Please run a simulation: fix the true elbow at τ=200 tokens, simulate S=8 draws at each of B=5 budget levels, and compute the empirical misclassification rate across 1000 simulations. If misclassification rate > 5%, the BIC claims are compromised.

3. **You run BIC model selection on 300 (problem, temperature) cells without any multiple-testing correction. Did you consider Benjamini-Hochberg correction across these 300 selection decisions? If the false-discovery rate is controlled at 5%, how many of the "97.7-99.3% staircase" cells would remain?**

4. **The bootstrap CI for Qwen-0.5B on the variation subset at τ=0.5 is [0.615, 1.000]. This is extremely wide. What would the CI look like with 10× more bootstrap resamples (e.g., B=1000 instead of B=100)?** If the CI remains this wide, the point estimate is not informative.

5. **You claim the theorem's log-concavity assumption is empirically justified "in practice" (line references unclear). Can you provide a test of log-concavity on the estimated critical-depth distribution from your real experiments? Which test, with what p-value?** If log-concavity fails, the theorem's conclusions are purely theoretical.

---

## Falsifiability Test

**What evidence would change my decision from Borderline to Accept (or vice versa)?**

From **Borderline to Accept** if:
- The authors run a sensitivity analysis showing that S=16 and S=32 produce the same qualitative conclusions (≥90% staircase classification rate)
- The paired Wilcoxon is re-reported as "no significant difference" and the token savings claim is properly characterized with per-problem statistics and a p-value
- Multiple-testing correction (e.g., BH at FDR=0.05) is applied and the staircase classification rate remains >80%
- The correlation across seeds (ρ values for synthetic) is reported as median [IQR] and is consistently high (IQR < 0.1)

From **Borderline to Reject** if:
- The S=8 sensitivity analysis shows classification rates drop substantially below 80% at higher S
- The bootstrap CI analysis with more resamples shows the variation-subset CI overlaps 50% (random)
- The non-monotonicity finding is not robust to multiple-testing correction across the 300 cells
- The token savings claim cannot be reproduced because the gzip proxy latency was not accounted for

---

## Confidence

**3/5** — I am confident in the mathematical contributions (Theorem is real, BIC methodology is sound in principle). I am NOT confident that the empirical findings are robust to sampling noise and multiple comparisons. The paper could be Acceptable with revisions to the statistical reporting, or could collapse if basic sensitivities fail.

---

## Decision

**Borderline (5.5–6.5)**

The mathematical contribution (Theorem + staircase decomposition framework) is substantial and genuinely novel. However, the statistical reporting is inadequate: S=8 is likely underpowered, p=0.23 is being misrepresented as equivalence, multiple-testing is unaddressed, and bootstrap CIs are unacceptably wide on key findings. The paper is worth a revision but not an acceptance in current form.

**Recommendation:** Reject with invitation to resubmit after addressing W1-W4 (statistical methodological gaps).

---

*— The Statistical Rigorist*
