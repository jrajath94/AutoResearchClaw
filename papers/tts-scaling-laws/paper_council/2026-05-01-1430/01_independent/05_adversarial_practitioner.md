# Adversarial Practitioner Review — STAIR Paper

**Reviewer:** The Adversarial Practitioner
**Paper:** STAIR: Per-Problem Discrete Structure in Test-Time Compute Scaling for LLM Reasoning
**Date:** 2026-05-01
**Venue:** NeurIPS 2025

---

## Falsifiability Test (First)

Before anything else: **What evidence would change my decision?**

Show me:
1. 24 hours of production traffic with STAIR on the inference path, with p99 latency breakdowns
2. Results on 3+ model families (Claude, Gemini, GPT) beyond Qwen
3. Failure case analysis: what breaks when compute budget routing is wrong?
4. Robustness to distribution shift (ood inputs, adversarial prompts)
5. Monitoring/alerting/runbook for the 3am scenario when STAIR misroutes

If the paper can't point to any of this — it's a lab result wearing a production costume.

---

## Strengths

**S1. Theorem that reconciles discrete individuals with smooth population curves (Section 3)**
The proof that log-concave critical-depth distributions yield smooth population accuracy is the most intellectually honest part of the paper. It correctly identifies why decades of scaling law work that modeled curves as smooth weren't obviously wrong — the population average hides the discreteness. This is a genuine theoretical contribution that resolves an apparent contradiction.

**S2. Empirical quantification of accuracy non-monotonicity (Section 4 / finding #3)**
The claim that 5.3-8.7% of cells show accuracy non-monotonicity due to budget-level answer truncation is specific, measured, and clearly not a DPI violation. This is a real phenomenon that standard smooth-curve models miss. The distinction from mutual-information non-monotonicity is correctly drawn and important.

**S3. Circuit depth as a better predictor than description length on synthetic data (finding #4, ρ=0.96 vs ρ=0.38)**
The synthetic data experiments correctly isolate the variable (sequential computation depth) and show a strong correlation with scaling elbows. This is a well-designed controlled experiment that identifies a meaningful distinction between computational and Kolmogorov complexity.

**S4. The BIC framework is methodologically explicit**
Using both MSE-based and binomial-likelihood BIC with multiple Δ thresholds (0, 1, 2, 3, 4, 6, 10) is more rigorous than cherry-picking a single threshold. The Raftery scale citation provides defensible ground. Showing results are robust across the full Δ range (Figure 7 implicit from the approach) would strengthen this.

**S5. Token reduction claim with real model (finding #6)**
On Qwen-1.5B, matching fixed-budget-512 accuracy at 75% fewer tokens (128.6 vs 512) on real GSM8K is a concrete operational win. The paired Wilcoxon test is appropriate. If this held at scale with p99 latency reporting, this would be a Strong Accept.

---

## Weaknesses

**W1. Sample size insufficient for generalization claims**
- **Issue:** 100 GSM8K problems, 8 samples/cell, 2 model sizes (both Qwen family)
- **Where:** Section 4 (experimental setup), all generalization claims in abstract and introduction
- **Severity:** 4/5
- **What would resolve:** 500+ problems, 3+ model families, 30+ samples/cell minimum for binomial-likelihood BIC to be trustworthy. The bootstrap CI on Qwen-0.5B variation subset [0.615, 1.000] is unacceptably wide — the true proportion could be anywhere from 62% to 100%.

**W2. Log-concavity assumption never validated on real problem distributions**
- **Issue:** Theorem 1 assumes critical-depth distribution is log-concave. This is central to the paper's theoretical contribution, but no empirical validation is provided.
- **Where:** Section 3 (theorem), the Open Questions list in paper_bundle correctly flags this as unverified
- **Severity:** 3/5
- **What would resolve:** Fit a log-concave distribution to real critical-depth estimates (from the staircase fits) and report the goodness-of-fit. If it fails, the theorem still holds as a sufficient condition but the population smoothness claim becomes less grounded.

**W3. p-value of 0.23 is misrepresented as "matches" accuracy**
- **Issue:** The claim "STAIR matches fixed-budget-512 accuracy (Δ+1.0%, paired Wilcoxon p=0.23)" uses p=0.23 as evidence of equivalence. This is not what p=0.23 means.
- **Where:** Finding #6 (abstract), Section on real LLM inference
- **Severity:** 4/5
- **What would resolve:** Apply an equivalence test (TOST procedure) with a pre-specified equivalence margin. Report the actual effect size confidence interval. "p > 0.05" is not evidence of equivalence — it's evidence of no detected difference, which is not the same thing when you're claiming a practical deployment result.

**W4. No failure mode analysis for the allocator**
- **Issue:** STAIR reduces tokens by 75% but there's zero analysis of what happens when it misroutes. In production, a wrong routing decision that truncates a problem the model was about to solve correctly is a silent failure — no alert, no rollback.
- **Where:** STAIR Framework (Section 4), allocator evaluation
- **Severity:** 5/5 — this is the adversarial practitioner's core concern. "Matches accuracy at 75% fewer tokens" in production means you're betting 25% of tokens can solve what 100% solved. What is the failure log?
- **What would resolve:** Case analysis of misrouted problems. What is the per-problem failure rate when STAIR undershoots? Is it randomly distributed or concentrated on hard problems? What is the cost-of-error?

**W5. gZIP proxy operational cost is ignored**
- **Issue:** "Zero model forward passes for routing" is claimed, but gzip computation over input problems is not free. For a production system handling 10K+ queries/second, the gzip-on-input pass for routing has non-trivial latency and compute cost.
- **Where:** Section 4, "zero model forward passes for routing" claim
- **Severity:** 2/5 — minor if routing is infrequent, severe if this is per-query
- **What would resolve:** Report gzip latency in ms per query at p50/p99. Is it cached? What is the memory footprint for the corpus of problems being routed?

**W6. Multiple comparisons across BIC Δ thresholds not controlled**
- **Issue:** Results are presented as robust across Δ ∈ {0, 1, 2, 3, 4, 6, 10} but there's no reporting of how findings change across these thresholds. With 7 threshold values × 2 BIC variants × 2 models × 3 temperatures, the reader cannot assess stability.
- **Where:** Section 4 (BIC classification), all BIC-based results
- **Severity:** 3/5
- **What would resolve:** A supplementary table or figure showing the proportion favoring staircase across all Δ values. If it varies dramatically (e.g., 40% at Δ=0, 99% at Δ=10), the claims are threshold-dependent and the choice of Δ=2 needs justification beyond "Raftery scale positive evidence."

**W7. Selection bias in "variation subset" analysis**
- **Issue:** The 87.3-93.1% figure is restricted to the 28% of cells that show any accuracy variation. This is a post-hoc selection that inflates the staircase preference — cells with no variation are trivially staircase (constant function fits perfectly) but are excluded.
- **Where:** Finding #2 (abstract), BIC classification results
- **Severity:** 4/5
- **What would resolve:** Report the staircase preference rate on ALL cells, not just the variation subset. The 97.7-99.3% figure includes no-variation cells, but the more meaningful 87.3-93.1% should also be contextualized with the no-variation baseline rate.

**W8. No p99/tail latency reporting anywhere**
- **Issue:** All latency results appear to be mean or median. For production deployment of test-time compute routing, what matters is p99 — when the model needs more tokens and STAIR says "done," what is the tail behavior?
- **Where:** No section addresses tail latency
- **Severity:** 5/5 — Without p99 data, this paper cannot be evaluated for production deployment. The adversarial practitioner rejects papers that only report means when tails determine on-call burden.
- **What would resolve:** Per-budget p50/p95/p99 latency breakdowns. At minimum, a statement that p99 < 2x mean for the routing decisions.

**W9. No adversarial robustness testing**
- **Issue:** The paper makes no mention of how STAIR behaves under distribution shift, adversarial inputs, or out-of-distribution problems. If the critical-depth distribution shifts (new problem types, harder benchmarks), does the routing fail gracefully or catastrophically?
- **Where:** Entirely absent from the paper
- **Severity:** 3/5
- **What would resolve:** Evaluation on held-out benchmarks (e.g., MATH-level problems, GSM8K-hard). Degradation curves when problem difficulty increases beyond training distribution.

**W10. Qwen-only results with no cross-model validation**
- **Issue:** All real-model results are on Qwen2.5-0.5B and Qwen2.5-1.5B. These are small dense models. The findings say nothing about instruction-tuned models, mixture-of-experts, or frontier models (Claude, GPT, Gemini).
- **Where:** Experimental setup, all real-model claims
- **Severity:** 4/5
- **What would resolve:** At minimum, one experiment on a different model family. Ideally: one frontier model (GPT-4 class) and one instruction-tuned model to show the phenomenon isn't Qwen-specific.

---

## Per-Rubric Scores and Calibration

| Dimension | Score | Calibration Anchor |
|-----------|-------|-------------------|
| **Originality / Novelty** | 7 | Substantial conceptual advance: the discrete-vs-population distinction is genuinely new. Not a new paradigm (10) but clearly above incremental (4). |
| **Soundness** | 5 | Serious methodology gaps compromise core claims. BIC threshold sensitivity (W6), selection bias in variation subset (W7), p=0.23 as equivalence (W3), small n (W1), unvalidated log-concavity (W2). The main theoretical contribution (Theorem) is sound. The empirical claims are weakened by these issues. |
| **Significance** | 7 | If the token reduction claim holds at scale, this is high significance for inference cost. The per-problem discrete structure finding, if robust, changes how we model test-time compute scaling. However, Qwen-only and 100-problem n limits current impact claims. |
| **Clarity** | 7 | Well-structured, well-motivated. The staircase vs sigmoid distinction is clearly explained. Theorem is clearly stated. Some sections (BIC formulas, Proposition on non-monotonicity) require re-reading but are comprehensible. |
| **Reproducibility** | 5 | Code not released (as of this review). Experimental details present but S=8 and n=100 are insufficient to reproduce reliably. No seeds reported. No model checkpoints. The gzip proxy routing has no latency characterization. |
| **Contextualization** | 6 | Strong on scaling laws and adaptive inference literature. Misses prior work on early exit strategies in vision/transformers that have similar "per-example adaptive compute" ideas. Correctly positions vs. Brown 2024, Snell 2024. |
| **Ethical / Broader Impact** | 6 | Boilerplate broader impact statement. No consideration of dual-use (adversarial routing to minimize compute on safety-critical queries). No discussion of environmental impact of 24,000 inference calls for a single paper. |

**Weighted average:** (7×1.0 + 5×1.5 + 7×1.0 + 7×0.7 + 5×1.0 + 6×0.8 + 6×0.5) / 6.5 = (7 + 7.5 + 7 + 4.9 + 5 + 4.8 + 3) / 6.5 = 39.2 / 6.5 = **6.03**

---

## Pointed Questions for Authors

**Q1.** Theorem 1 assumes critical-depth distribution is log-concave. What happens to the smoothness guarantee when the distribution is multimodal (e.g., a mixture of easy and hard problem clusters)? Have you tested real critical-depth distributions for log-concavity?

**Q2.** Your "matches accuracy at 75% fewer tokens" claim uses p=0.23. What was your pre-specified equivalence margin? If you didn't specify one before the experiment, this is a post-hoc rationalization. Please provide the TOST procedure results with an equivalence bound.

**Q3.** What is the failure log for the STAIR allocator? Specifically: when STAIR terminates early and the problem would have been solved correctly at higher token budget, what does that failure distribution look like? Is it concentrated on specific problem types, or uniformly random?

**Q4.** You test on 100 GSM8K problems. GSM8K has 1,319 training and 1,319 test problems. Why 100? What happens to your BIC proportions when n=500? If the staircase proportion drops to 60% at larger n, your 97.7-99.3% claim is a small-sample artifact.

**Q5.** Your bootstrap CI for the variation subset at τ=0.5 on Qwen-0.5B is [0.615, 1.000] — this is essentially uninterpretable. What is the minimum n needed to get a 95% CI width of ±0.05 on the staircase proportion? Have you run a power analysis?

**Q6.** "Zero model forward passes for routing" via gzip proxy — what is the actual latency at p99 for a single query? At 10K queries/second? The gzip-on-input is not free. What is the memory footprint of storing gzip representations for routing?

**Q7.** All real-model experiments are Qwen2.5-0.5B and Qwen2.5-1.5B — small dense models. Have you tested on any instruction-tuned model? On any model larger than 1.5B? The critical-depth distribution almost certainly shifts with model size and training methodology.

**Q8.** What is your plan for when the model's API behavior changes (rate limits, output distribution drift, deprecation)? Your entire routing policy is built on a fixed BIC model — what is the monitoring and retraining runbook?

---

## Falsifiability (Expanded)

The paper claims STAIR "matches accuracy at 75% fewer tokens in production-like conditions." What would falsify this?

1. **Show me p99 latency:** If p99 token-generation latency with STAIR exceeds 2× fixed-budget-512 p99, the token reduction claim is misleading — you've saved mean tokens at the cost of tail latency.
2. **Test on ood distribution:** If staircase preference drops below 70% on MATH problems (harder than GSM8K), the generalization claim fails.
3. **Cross-model replication:** If Claude-3.5-Haiku or GPT-4o-mini shows <60% staircase preference, the finding is Qwen-specific and the theory needs revision.
4. **Failure case analysis:** If >10% of STAIR's early terminations occur on problems where the model was in the middle of a correct reasoning trace (detectable via intermediate answer state matching), the allocator is cutting off valid computation.

---

## Confidence

**3/5**

I am confident in the theoretical contribution (Theorem) and the empirical observation that per-problem scaling curves are not smooth sigmoids. I am not confident that the findings generalize beyond Qwen small models, beyond 100-problem n, or to production traffic patterns. The methodological issues (W1-W10) are real but not fatalthree — the paper can be fixed with larger n, equivalence testing, and failure mode analysis.

---

## Decision

**Borderline (5.5-6.5 on rubric, ~6.03 weighted average)**

This is a Borderline. The core insight is real and valuable: per-problem test-time compute scaling is discrete, not smooth. The theory is sound. The empirical methodology has serious gaps that are correctable: larger n, cross-model validation, proper equivalence testing, failure mode analysis.

**Borderline, not Reject**, because the theoretical contribution is genuine and the discrete-vs-population distinction is the kind of finding that, if robust, changes how the field models scaling. But "if robust" is doing enormous work here — the paper doesn't yet demonstrate robustness.

**Recommendation to authors:** The paper needs a major revision with (1) n≥500 on real models, (2) cross-model validation, (3) proper equivalence testing, (4) failure mode analysis, (5) p99 latency reporting, and (6) monitoring/rollback discussion before it deserves Accept.

---

*— The Adversarial Practitioner*