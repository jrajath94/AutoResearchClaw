# Paper Bundle — STAIR: Per-Problem Discrete Structure in Test-Time Compute Scaling for LLM Reasoning

**Paper:** STAIR_paper_neurips.pdf (15 pages)
**Target venue:** NeurIPS 2025
**Date:** 2026-05-01

---

## Title & Authors
**STAIR: Per-Problem Discrete Structure in Test-Time Compute Scaling for LLM Reasoning**
Anonymous Author(s)

---

## Abstract

Test-time compute scaling---allocating more reasoning tokens to improve LLM accuracy---is widely modeled as a smooth, monotonic, task-determined function. We present evidence challenging all three assumptions. We introduce **STAIR** (Staircase Test-time Adaptive Inference Routing), a framework that decomposes population-level scaling curves into per-problem components via Bayesian Information Criterion (BIC) model selection and optimizes compute allocation through complexity-stratified temperature tuning.

**Key findings:**
1. On real LLMs (Qwen2.5-0.5B and Qwen2.5-1.5B), 97.7--99.3% of per-problem scaling curves are better fit by piecewise-constant functions than smooth sigmoids under both MSE-based and binomial-likelihood BIC
2. Restricted to the 28% of (problem, temperature) cells with any accuracy variation: 87.3--93.1% (Qwen-0.5B 95% bootstrap CI [0.983, 1.000] overall, [0.615, 1.000] on variation subset at τ=0.5; Qwen-1.5B [0.957, 0.993] overall, [0.737, 1.000] on variation subset)
3. Accuracy non-monotonicity (explicitly NOT mutual-information non-monotonicity) occurs in 5.3--8.7% of real cells, driven by budget-level answer truncation
4. On synthetic data, sequential computation depth predicts scaling elbows far more accurately than description-length proxies (ρ=0.96 vs ρ=0.38); on real GSM8K (n=100), gzip and step count are both weak predictors (gzip--steps ρ=0.147, 95% CI [-0.088, 0.383])
5. On synthetic data, STAIR allocator reduces elbow prediction MAPE by 35% relative to five baselines
6. On real GSM8K (Qwen-1.5B), STAIR matches fixed-budget-512 accuracy (0.075 vs 0.065, Δ+1.0%, paired Wilcoxon p=0.23) while using 75% fewer tokens (128.6 vs 512)

**Theorem (population smooth from discrete individuals):** Under log-concave critical-depth distributions, the population curve is smooth even when every individual curve is discrete.

---

## Section 1: Introduction (pp. 1-2)

**Problem:** Test-time compute scaling (allocating reasoning tokens to improve LLM accuracy) is widely modeled as smooth, monotonic, task-determined. Three untested assumptions:
1. **Smoothness** — does the log-concave curve hold per-problem or only in population expectation?
2. **Task-determination** — is the elbow set by task complexity or model's "channel quality"?
3. **Description complexity** — is Kolmogorov complexity (description length) the right measure, or does computational depth matter more?

**Four contributions claimed:**
1. Per-problem staircase decomposition (97.7-99.3% of curves better described by piecewise-constant vs smooth, on 100 GSM8K problems at 3 temperatures, S=8 samples/cell)
2. Accuracy non-monotonicity (5.3-8.7% of cells) — explicitly not claiming DPI violation; no MI estimation
3. Computational vs. description complexity (circuit depth ρ=0.96 vs gzip ρ=0.38 on synthetic; weak correlation on real GSM8K)
4. STAIR allocator (35% MAPE improvement on synthetic; matches fixed-budget-512 accuracy at 75% fewer tokens on real)

---

## Section 2: Related Work (p. 2)

**Scaling laws:** Training-time scaling (Kaplan 2020, Hoffmann 2022) well-established. Test-time analogs: Snell 2024 (test-time compute vs parameter scaling), Brown 2024 (extended-thinking models), Jones 2021 (board games). All model curve as smooth and monotonic.

**Information theory and reasoning:** Polyanskiy 2024 (channel coding foundations), Feng 2024 (CoT as iterative refinement), Li 2019 (Kolmogorov complexity). STAIR extends by distinguishing computational from description complexity.

**Adaptive inference:** Early exit (Graves 2016, Schuster 2022), speculative decoding (Leviathan 2023), mixture-of-depths (Raposo 2024). STAIR uses pre-inference gzip proxy with zero model forward passes for routing; benchmarks against confidence-adaptive stopping and oracle-best baseline.

---

## Section 3: Theoretical Framework (pp. 3-4)

**Definition 1 (Per-problem accuracy function):** For problem x with solution y*, a(t|x) = Pr[y* | r_t, x] — probability of correctness given reasoning trace of length t.

**Definition 2 (1-Staircase function):** a(t|x) is 1-staircase with critical depth τ(x) if a(t|x) = α_0 for t < τ(x) and a(t|x) = α_1 > α_0 for t ≥ τ(x).

**Definition 3 (Population elbow):** Population accuracy is ā(t) = E_x[a(t|x)]. Population elbow is t* = arg max_t |ā''(t)|.

**Theorem (Smooth population from discrete individuals):** Let each problem x_i have 1-staircase accuracy with critical depth τ_i ~ F_τ with log-concave PDF f_τ. Then:
1. ā(t) = α_0 + (α_1 - α_0)F_τ(t) is monotone increasing, concave
2. t* = mode(f_τ)
3. Elbow is a property of population distribution, not any individual problem

*Proof uses Prékopa's theorem on log-concave distributions.*

**Proposition (Accuracy non-monotonicity prevalence):** If model has per-step probability p of producing accuracy decrease (truncation, reasoning drift, or autoregressive error), probability of observing ≥1 non-monotonic step in T budget levels is 1 - (1-p)^T. Note: concerns empirical accuracy, not mutual information; DPI not violated.

**Key prediction:** Even if every individual problem has a discrete staircase scaling curve, the population average can appear smooth.

---

## Section 4: Method — STAIR Framework (pp. 4-6)

### Per-Problem BIC Classification

For each problem x_i and budget t ∈ {t_1, ..., t_B}:
- Estimate accuracy â_i(t) from S=8 independent samples (Bernoulli-trial model)
- Fit two competing models:

**Piecewise-constant (staircase):** â_i(t) = α_0·1[t < τ_i] + α_1·1[t ≥ τ_i], 2 effective parameters, τ_i found by brute-force search over B-1 interior positions. Selection is discrete, not continuous DOF.

**Logistic sigmoid:** â_i(t) = L/(1 + e^{-k(t-t_0)}), 3 continuous parameters fit via bounded nonlinear least squares.

**BIC formulas:**
- BIC_MSE = n·ln(RSS/n) + p·ln(n)
- BIC_Bin = -2 Σ [k_i(t_j)·ln(phat_j) + (S-k_i(t_j))·ln(1-phat_j)] + p·ln(B)

Classification: "staircase" at threshold Δ=2 if BIC_sigmoid - BIC_staircase > 2 ("positive evidence" on Raftery scale). Results reported under both likelihood choices and Δ ∈ {0, 1, 2, 3, 4, 6, 10}.

**Elbow definition:** Staircase elbow = τ_i (split location). Sigmoid elbow = t_0 (midpoint). Both on same token-budget scale.

### Cross-Model Divergence and Non-Monotonicity

[Section 4 content continues but was cut off in source]

---

## Experimental Setup

### Synthetic Data
- 800 problems, 4 factorial conditions, 5 seeds
- Sequential computation depth vs description-length (gzip) as elbow predictors

### Real LLM Inference
- Models: Qwen2.5-0.5B and Qwen2.5-1.5B
- Benchmark: 100 GSM8K problems
- Conditions: 5 token budgets × 3 temperatures × 8 samples/cell
- Total: 24,000 inference calls

### Baselines for Allocator Comparison
1. Fixed budget (512 tokens)
2. Confidence-adaptive stopping
3. Oracle-best baseline
4. Five other baselines for MAPE comparison on synthetic data

---

## Key Results Summary

| Finding | Evidence |
|--------|----------|
| 97.7-99.3% per-problem curves favor staircase over sigmoid | BIC analysis on 300 curves (100 problems × 3 temperatures) |
| 87.3-93.1% on variation subset | Restricted to 28% of cells with accuracy variation |
| 5.3-8.7% accuracy non-monotonicity | Real (problem, temperature) cells |
| Circuit depth ρ=0.96 (synthetic) vs gzip ρ=0.38 | Synthetic elbow prediction |
| gzip-step correlation ρ=0.147, 95% CI [-0.088, 0.383] | Real GSM8K, n=100 |
| 35% MAPE improvement | STAIR allocator vs 5 baselines on synthetic |
| +1.0% accuracy at 75% fewer tokens | Qwen-1.5B on GSM8K vs fixed-budget-512 |

---

## Figures

- **Figure 1 (Staircase):** [Caption not provided in extracted pages]
- **Figure 2 (BIC comparison):** [Caption not provided]
- **Figure 3 (Heatmap):** [Caption not provided]
- **Figure 4 (Proxy):** [Caption not provided]
- **Figure 5 (Pareto):** [Caption not provided]
- **Figure 6 (Temperature):** [Caption not provided]
- **Figure 7 (BIC):** [Caption not provided]

---

## Open Questions / Unverified Claims

1. Theorem 1 assumes log-concavity of critical-depth distribution — is this justified empirically?
2. BIC threshold Δ=2 ("positive evidence" on Raftery scale) — why this value specifically?
3. 8 samples per cell (S=8) — is this sufficient for binomial-likelihood BIC accuracy?
4. GSM8K with 100 problems — sufficient for the generalization claims?
5. Qwen models only — do findings hold for other model families (Claude, Gemini, GPT)?
6. Allocator uses pre-inference gzip proxy — what is the actual latency overhead?
7. "Zero model forward passes for routing" — but what is the gzip computation cost?