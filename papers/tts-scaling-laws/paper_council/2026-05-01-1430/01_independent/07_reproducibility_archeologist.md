# Review: STAIR — Per-Problem Discrete Structure in Test-Time Compute Scaling for LLM Reasoning
**Reviewer:** The Reproducibility Archeologist
**Date:** 2026-05-01
**Target:** NeurIPS 2025 (paper targets 2025, reviewing against NeurIPS 2026 rubric)

---

## Reproducibility Checklist Score: 58/100

**Code Released:** Yes — Python code for synthetic experiments is fully present
**Configs Released:** Yes — config.py is complete and explicit
**Data Pipeline:** Partial — synthetic data generator released; GSM8K via `datasets` library
**Seeds Reported:** Yes — 5 seeds [0,1,2,3,4] in config.py
**Compute Reported:** No — GPU-hours, total run cost, energy estimates all absent
**Real LLM Code:** Discrepancy — real_experiment.py hardcoded N_PROBLEMS=40, not 100 as in paper

---

## 3-5 Strengths

1. **Theorem 1 is a genuine contribution.** The proof that a smooth population curve can emerge from discrete per-problem staircases under log-concavity is the paper's most novel theoretical result. The use of Prékopa's theorem is appropriate and the claim is precisely stated. (Paper Section 3, Theorem 1)

2. **Full synthetic experimental pipeline is reproducible.** config.py contains every hyperparameter (lines 13-171), data.py has the full synthetic data generator with 2x2 factorial structure, methods.py implements all 7 conditions, and evaluation.py has the metrics. A competent grad student can regenerate the synthetic results from what's published.

3. **BIC framework is cleanly implemented.** The two-model comparison (piecewise-constant vs logistic sigmoid) with explicit BIC formulas in Section 4 and dual likelihood variants (MSE and binomial) in the appendix is methodologically honest. BIC threshold sensitivity analysis (paper Appendix, real_results_v2/reanalysis_stratified.json) is a good practice.

4. **Population vs per-problem distinction is clearly articulated.** The introduction's three questions (smoothness, task-determination, description complexity) are well-scoped and falsifiable. The paper correctly distinguishes accuracy non-monotonicity from MI non-monotonicity and explicitly disclaims DPI violation.

5. **Cross-seed aggregation is standard.** Five seeds with cross-seed CV reporting and Wilcoxon signed-rank tests for pairwise comparisons follow best practices (evaluation.py lines 364-402).

---

## 5-10 Weaknesses

### W1: Real LLM experiment setup mismatch
**Issue:** real_experiment.py hardcodes `N_PROBLEMS=40` and `SAMPLES_PER_CELL=4`, but the paper abstract and reanalysis_stratified.json report 100 problems with 8 samples/cell. The 100-problem, 8-sample results exist only as stored .npy files and JSON summaries — there is no reproducible script that reproduces those exact numbers.
**Where:** experiment/real_experiment.py (line 28: `N_PROBLEMS = 40`, line 31: `SAMPLES_PER_CELL = 4`) vs paper abstract claiming "100 GSM8K problems, S=8 samples/cell" and real_results_v2/reanalysis_stratified.json showing "total_pairs": 300 = 100 problems × 3 temperatures.
**Severity:** 4/5
**What would resolve it:** Release the actual inference script that generated real_results_v2 with correct constants (N_PROBLEMS=100, SAMPLES_PER_CELL=8), or explain the discrepancy.

### W2: BIC analysis restricted to cells WITH variation — circular selection bias
**Issue:** The paper reports 87.3-93.1% staircase win rate on a "variation subset" (the 28% of cells with any accuracy range > 1/S). This subset was defined post-hoc as cells where the two model families are "empirically separable." But this selection itself biases the comparison: if a curve has zero variation, both staircase and sigmoid fit a flat line and BIC will prefer the simpler (2-parameter) staircase. The 87-93% number may be inflated by this design.
**Where:** Paper abstract ("restricted to the 28% of (problem, temperature) cells with any accuracy variation"), reanalysis_stratified.json lines 11-23 and 173-186.
**Severity:** 3/5
**What would resolve it:** Report the BIC win rate on ALL cells, not just the variation subset. Clarify whether the "variation subset" analysis was pre-specified or data-snooped. Show the distribution of accuracy ranges across all cells.

### W3: Gross accuracy levels undermine curve-shape analysis
**Issue:** Qwen-0.5B achieves 2-3% accuracy on GSM8K across all budgets (real_results_v2_summary.json lines 17-22). Qwen-1.5B achieves 1.9-6.5%. At these accuracy levels, with S=8 samples, most budget-temperature cells have 0-2 correct samples out of 8. The accuracy curves being fit are extremely noisy binary outcomes. The BIC model comparison on these near-random curves is essentially fitting noise.
**Where:** real_results_v2_summary.json ("accuracy": {"32": 0.02, "512": 0.02875} for Qwen-0.5B); paper Section 5 and real_results_v2/reanalysis.json showing overall BIC win rates of 99.3% (Qwen-0.5B) and 97.7% (Qwen-1.5B).
**Severity:** 5/5 — This is the most serious empirical concern. A competent reviewer would ask: are these high BIC rates for staircase real signal or artifact of near-random accuracy?
**What would resolve it:** (a) Report the distribution of per-cell success counts. (b) Run the BIC comparison on shuffled labels as a negative control. (c) Use larger models (e.g., Qwen2.5-7B or GPT-4 class) where accuracy curves have meaningful shape. (d) Explicitly acknowledge that the 97-99% rates may be inflated at low accuracy regimes.

### W4: No GPU-hours or compute cost reporting
**Issue:** The paper reports "24,000 inference calls" but provides no estimate of GPU-hours, total experiment time, or financial cost. The NeurIPS reproducibility checklist requires "total compute used." For a paper about scaling laws and inference efficiency, this is a glaring omission.
**Where:** Paper Section 5 ("Total: 24,000 inference calls"); experiment/real_experiment.py line 8 ("Time: ~25 minutes total") — but this is for 40 problems, not 100.
**Severity:** 3/5
**What would resolve it:** Report GPU-hours, total experiment walltime, and approximate cloud compute cost for the 100-problem experiments.

### W5: BIC threshold sensitivity reported in JSON but not in paper
**Issue:** real_results_v2/reanalysis_stratified.json contains a full BIC threshold sensitivity analysis (thr_0 through thr_10) that is not discussed in the paper. At thr=0, the win rates are 98.7% (Qwen-0.5B) and 97.0% (Qwen-1.5B). At thr=10, they are 99.7% and 98.0%. The fact that the result is essentially unchanged across a 10-fold range of thresholds is worth discussing — it either shows robustness or that the classification is dominated by the penalty term rather than the likelihood.
**Where:** real_results_v2/reanalysis_stratified.json lines 527-555; not referenced in the paper.
**Severity:** 2/5
**What would resolve it:** Add a paragraph in the appendix or supplementary materials discussing threshold sensitivity and what drives the classification decision.

### W6: GSM8K complexity proxy validation uses a different sample size than main results
**Issue:** The complexity proxy analysis (gzip vs step count correlation ρ=0.147, n=100) is based on all 100 GSM8K problems. But the main BIC analysis restricted to the "variation subset" uses only 29 (Qwen-0.5B) or 55 (Qwen-1.5B) problems. The validation and the main experiment use different problem subsets, making the complexity-proxy analysis not directly supportive of the BIC results.
**Where:** reanalysis_stratified.json lines 12-23 (variation subset sizes) vs lines 347-426 (complexity proxy analysis on all 100).
**Severity:** 3/5
**What would resolve it:** Report the complexity-proxy correlation within the variation subset, or use the same 100-problem set for both the BIC analysis and the proxy validation.

### W7: "Zero forward passes for routing" obscures gzip cost
**Where:** Paper abstract and Section 5 claim "zero model forward passes for routing." The gzip computation is O(n) in problem text length but this cost is not quantified. For a paper about inference efficiency, the actual latency overhead of the gzip proxy should be disclosed.
**Severity:** 2/5
**What would resolve it:** Report mean/std gzip computation time per problem. Is it microseconds? Milliseconds? At what problem text length?

### W8: Multiple comparisons not corrected
**Issue:** The paper tests 3 models × 3 temperatures for BIC rates, plus multiple hypothesis thresholds in the config. The hypothesis discrimination score (evaluation.py line 311-361) checks 9 separate predictions without multiplicity correction. With 9 tests at α=0.05, the family-wise error rate is not controlled.
**Where:** config.py lines 118-126 (9 hypothesis thresholds); evaluation.py compute_discrimination_score.
**Severity:** 2/5
**What would resolve it:** Apply Bonferroni or Holm-Bonferroni correction for the 9 hypothesis checks, or acknowledge this as a limitation.

---

## Per-Rubric-Dimension Scores

| Dimension | Score | Calibration Anchor |
|---|---|---|
| **Originality / Novelty** | **7** | Substantial conceptual advance: the per-problem discrete structure finding and the theorem connecting discrete individuals to smooth populations is genuinely new. Substantial extension of prior test-time scaling work. |
| **Soundness** | **5** | Methodology is adequate for synthetic experiments but has serious gaps for real LLM experiments. Gross accuracy levels (2-6% on GSM8K) with S=8 samples make BIC curve-fitting on noisy binary outcomes unreliable. The variation-subset restriction is post-hoc and potentially biased. |
| **Significance** | **7** | Important findings within the test-time compute subfield. If the staircase hypothesis holds at higher accuracy regimes, the implications for inference optimization are significant. The theorem is a useful theoretical contribution. |
| **Clarity** | **7** | Well-organized, clearly written. The three research questions in the introduction are crisp. The distinction between accuracy and MI non-monotonicity is carefully handled. Some figures lack descriptive captions in the extracted text. |
| **Reproducibility** | **5** | Synthetic experiments fully reproducible. Real LLM experiments have a code-data mismatch (N_PROBLEMS=40 in script vs 100 in paper). No compute reporting. GSM8K via `datasets` library is non-deterministic across versions. The code for the exact 100-problem, S=8 experiments is not released. |
| **Contextualization vs Prior Work** | **7** | Good coverage of test-time scaling literature (Snell 2024, Brown 2024, Jones 2021), information theory (Polyanskiy 2024, Li 2019), and adaptive inference (Graves 2016, Leviathan 2023, Raposo 2024). Correctly positions vs SOTA. |
| **Ethical / Broader Impact** | **6** | Standard boilerplate discussion. The paper does not address potential dual-use concerns of inference optimization (could be used to scale up harmful content generation more efficiently). No mention of environmental impact of 24,000 LLM calls. |

**Weighted Average:** (7×1.0 + 5×1.5 + 7×1.0 + 7×0.7 + 5×1.0 + 7×0.8 + 6×0.5) / (1.0+1.5+1.0+0.7+1.0+0.8+0.5) = **6.09**

**Decision: Borderline** (5.5-6.5 range)

---

## 5+ Pointed Questions for Authors

1. **The variation subset (W2):** The 87.3-93.1% staircase win rate is computed on only 28% of cells — those with any accuracy variation. What is the staircase win rate on ALL cells? And was the "variation subset" analysis pre-specified or motivated by seeing that the overall rate was lower than desired?

2. **Accuracy levels (W3):** Qwen-0.5B achieves 2-3% accuracy on GSM8K. With S=8 samples, most cells have ≤1 success. How much of the 97-99% BIC staircase win rate survives a negative control where you shuffle the success/failure labels before fitting? If BIC still prefers staircase on random noise, the result is meaningless.

3. **The N_PROBLEMS discrepancy (W1):** real_experiment.py uses N_PROBLEMS=40 but the paper claims 100. Which script generated the results in real_results_v2/? Can you release the exact inference script with correct constants?

4. **Generalization beyond Qwen:** All real experiments use Qwen2.5-0.5B and Qwen2.5-1.5B. Do the findings hold for larger models (7B+) or different families (Claude, Gemini, Llama)? The small-model accuracy regime (2-6%) is fundamentally different from the high-accuracy regime where scaling laws were originally established.

5. **The 35% MAPE claim on synthetic data:** Table 3 / Figure X shows 35% MAPE reduction. What is the absolute MAPE for each baseline? A 35% relative reduction from a baseline of MAPE=200% is very different from a 35% reduction from MAPE=20%. Please report absolute numbers.

6. **Theorem 1's log-concavity assumption:** The theorem requires that critical depths τ_i are drawn from a log-concave distribution. What evidence supports this assumption for real reasoning tasks? Is it tested, or assumed for convenience?

7. **Cross-model divergence significance:** The cross-model elbow divergence of 0.244 (Wilcoxon p=0.028) is reported as evidence for task-determination. With only 100 problems, a p-value of 0.028 is barely significant after multiple comparisons across temperatures and models. What is the p-value after Bonferroni correction for the 6 pairwise comparisons (2 models × 3 temperatures)?

---

## Falsifiability Test

**"What evidence would change my decision?"**

- **Release the actual inference script for the 100-problem, S=8 experiments** with correct constants → upgrades reproducibility score from 5 to 7, raises soundness to 6
- **Run a negative control** (shuffle labels before BIC fitting) → if staircase still wins >60% on shuffled data, the 97-99% rates are noise, and I downgrade soundness to 3
- **Report results on a larger model** (e.g., Qwen2.5-7B or Llama-3-8B) with >30% accuracy on GSM8K → if staircase wins at high accuracy too, the finding generalizes and significance rises to 8
- **Report absolute MAPE values** for the 35% claim → without absolute numbers, the improvement is uninterpretable
- **Correct the compute reporting**: GPU-hours and total experiment time for both synthetic and real experiments → required for NeurIPS reproducibility checklist compliance

---

## Confidence: 3/5

My confidence in this review is **3/5** (moderate). The key uncertainty is the extent to which the real LLM results are driven by genuine signal vs. artifacts of low-accuracy binary outcomes. Without access to the negative control (shuffled labels) or larger-model results, I cannot definitively judge whether the 97-99% staircase rates are scientifically meaningful. The synthetic experiments are solid and reproducible.

---

## Decision: **Borderline**

The paper has genuine strengths — a novel theorem, a well-motivated hypothesis, complete synthetic experimental code, and a theoretically sophisticated framing. However, the real LLM evidence is severely compromised by near-random accuracy levels (2-6%) with S=8 samples, creating a circular analysis where the variation-subset restriction selects the cells where noise makes the two models indistinguishable and BIC picks the simpler one. The BIC threshold sensitivity being essentially flat is consistent with the classification being dominated by the penalty term rather than genuine signal.

**Recommendation:** The paper is worth accepting as a **Borderline** paper with an invitation to revise. The authors should (1) run and report the negative control, (2) release the correct real-inference script, (3) include a larger model if possible, and (4) report absolute MAPE values. If the authors can demonstrate that the staircase preference survives a shuffled-label negative control at a larger model scale, this becomes a strong Accept.

— The Reproducibility Archeologist