# Final Synthesized Hypotheses

After integrating the innovator's bold framings, the pragmatist's engineering discipline, and the contrarian's structural critiques, I converge on **3 final hypotheses**. Each represents a genuine point of tension across the three perspectives — not a diluted compromise, but a sharpened version that absorbs the strongest objections.

---

## Hypothesis 1: The Staircase Beneath the Curve — Per-Problem Reasoning Scaling Is Discrete, and the "Elbow" Is a Population Artifact Controllable by Temperature

### What This Combines

| Source | Contribution |
|--------|-------------|
| **Contrarian H2** | Core claim: smooth scaling curves are averaging artifacts over step-function per-problem curves |
| **Innovator H1** | Phase transition framing: some problems have discrete "insight thresholds" |
| **Innovator H3** | Temperature as the primary control variable for effective channel capacity |
| **Pragmatist H1** | Gzip compression as a cheap proxy for per-problem difficulty bucketing |

### Synthesized Claim

The population-average scaling curve's apparent smoothness and "elbow point" are artifacts of aggregating over a population of problems, each of which exhibits a **discrete transition** from unsolvable to solvable at a problem-specific critical reasoning depth `d_i`. The distribution of these critical depths — not any single information-theoretic bound — determines the population curve's shape. Furthermore, decoding temperature shifts the entire distribution of critical depths: higher temperature lowers `d_i` for hard problems (by enabling exploration past local optima) while raising it for easy problems (by injecting unnecessary noise). The practical consequence: a two-parameter model `(gzip_length, temperature)` can predict per-problem compute budgets better than the target paper's single-parameter information-theoretic bound.

### Why This Is Stronger Than Any Single Perspective

The contrarian correctly identifies that the elbow may be a measurement artifact, but offers no constructive replacement. The innovator's temperature hypothesis provides the mechanism: temperature controls the *shape* of the per-problem transition distribution, and therefore the apparent elbow location. The pragmatist's gzip proxy provides the engineering path: bucket problems by compression length, optimize temperature per bucket, and you have a deployable inference budget allocator.

### Unresolved Disagreement

The contrarian and innovator disagree on whether the per-problem curves are true step functions (contrarian) or exhibit bimodal MI distributions with some residual smoothness (innovator). This experiment can adjudicate: if per-problem curves are better fit by logistic sigmoids than piecewise-constant functions at every temperature, both are partially wrong and the target paper's smooth model survives at the individual-problem level.

### Experimental Design

1. **Problems:** 300 from GSM8K, stratified into 3 gzip-length terciles (100 each).
2. **Temperatures:** 5 values (0.0, 0.3, 0.5, 0.8, 1.2).
3. **Reasoning budgets:** 8 token limits (64, 128, 192, 256, 384, 512, 768, 1024).
4. **Trajectories:** 64 per (problem, temperature, budget) cell.
5. For each problem × temperature, fit both a piecewise-constant model (1–2 steps) and a logistic model to the accuracy-vs-budget curve. Compare via BIC.
6. For the population average at each temperature, compute the apparent elbow and its coefficient of variation under 50× bootstrap resampling.

### Measurable Predictions

| # | Prediction | Threshold |
|---|-----------|-----------|
| P1 | Per-problem curves are better fit (lower BIC) by piecewise-constant than logistic | >55% of problems across all temperatures |
| P2 | The population-level elbow point's CV under bootstrap resampling exceeds 0.20 | CV > 0.20 at ≥3 of 5 temperatures |
| P3 | Optimal temperature varies systematically by gzip tercile | Spearman ρ between gzip tercile and τ* exceeds 0.6 |
| P4 | A (gzip_tercile, τ) lookup table predicts per-problem critical depth within 25% | >60% of held-out problems |

### Failure Conditions

- If the logistic model wins BIC for >70% of problems: the staircase hypothesis is rejected; per-problem scaling really is smooth.
- If bootstrap CV < 0.10: the elbow is a stable, genuine property of the task class, not a population artifact.
- If optimal temperature is constant (±0.1) across gzip terciles: temperature does not interact with problem complexity, and the innovator's thermodynamic bound is wrong.

### Resource Estimate

300 problems × 5 temps × 8 budgets × 64 trajectories = 768K short generations (~128 tokens avg). At ~3K tok/s on vLLM/A100: **~55 minutes**. This is tight but feasible within 60 minutes by using Llama-3-8B with sequences capped at 128 tokens per trajectory. The analysis (BIC fitting, bootstrap) adds <5 minutes.

---

## Hypothesis 2: CoT Scaling Is Model-Dependent, Not Task-Dependent — MI Non-Monotonicity as the Diagnostic

### What This Combines

| Source | Contribution |
|--------|-------------|
| **Contrarian H1** | Core challenge: the channel coding model predicts task-dependent scaling, but CoT is distribution steering, which predicts model-dependent scaling |
| **Contrarian H1** | MI non-monotonicity test as the discriminating experiment |
| **Innovator H2** | Anti-scaling regime: performance actively degrades past a critical length |
| **Pragmatist H2** | Early-layer divergence as a practical, online proxy for MI saturation |

### Synthesized Claim

The target paper's channel coding model makes a strong implicit prediction: the elbow point is primarily a function of the *task's* complexity, not the *model's* architecture. We claim this is wrong. The elbow point is **model-dependent** because CoT generation is distribution steering (not signal decoding), and different models have different probability landscape geometries. The diagnostic signature is **MI non-monotonicity**: if the accumulated mutual information between reasoning prefixes and the correct answer decreases at any step (the model "steers away" before correcting), the channel coding model's data processing inequality is violated, confirming that CoT is constructive rather than extractive. Furthermore, the early-layer KL divergence signal (pragmatist H2) provides a *practical* detector for these MI-decreasing steps — when early and final layers diverge sharply, the model is in a "steering correction" phase where the current reasoning step is undoing damage from a previous one.

### Why This Is Stronger Than Any Single Perspective

The contrarian identifies the theoretical vulnerability but proposes only a diagnostic test. The innovator's anti-scaling hypothesis provides the extreme case: not just MI non-monotonicity but actual accuracy degradation. The pragmatist's layer-divergence signal provides the engineering bridge: if we can detect MI-decreasing steps in real-time, we can build an early stopping mechanism that is aware of non-monotonicity (stop when MI plateaus, but *not* during a correction phase where MI temporarily dips before recovering).

### Unresolved Disagreement

The contrarian and the target paper fundamentally disagree on whether CoT is information extraction or distribution steering. This experiment cannot fully resolve the philosophical question, but it can falsify the channel coding model's key empirical prediction (MI monotonicity). If MI is empirically monotonic, the channel coding model survives as a useful approximation even if the underlying mechanism is different. If MI is non-monotonic, the model needs revision regardless of mechanism.

The innovator and pragmatist disagree on whether anti-scaling (active accuracy *degradation*) exists or whether longer reasoning merely wastes tokens. This experiment tests both: we measure both MI trajectory and final accuracy as a function of forced reasoning length.

### Experimental Design

1. **Problems:** 200 from GSM8K (correctly solvable by both models at some reasoning length).
2. **Models:** Llama-3-8B and Mistral-7B-v0.3 (similar parameter count, different architecture and training).
3. **Trajectories:** 50 per problem per model, at natural (unforced) CoT length.
4. **MI measurement:** For each trajectory, compute `P(correct_answer | S_{1:t})` at each reasoning step `t` by evaluating the log-probability of the correct final answer conditioned on the reasoning prefix. Plot the MI trajectory.
5. **Layer divergence:** For Llama-3-8B, extract KL(layer-8 logits || layer-32 logits) at each generation step. Correlate with MI trajectory.
6. **Forced-length extension:** For 100 problems, force CoT to 2× and 3× the natural stopping length. Measure accuracy degradation.

### Measurable Predictions

| # | Prediction | Threshold |
|---|-----------|-----------|
| P1 | MI is non-monotonic (∃ step where accumulated MI decreases) | >25% of correctly-solved problems on ≥1 model |
| P2 | Elbow points differ across models by >35% on the same problems | For >50% of problems where both models solve correctly |
| P3 | At 2× natural CoT length, accuracy drops by ≥3pp (anti-scaling) | Across the 100 forced-extension problems |
| P4 | Layer-divergence spikes predict MI-decreasing steps | AUROC > 0.65 for classifying MI-decreasing vs. MI-increasing steps |

### Failure Conditions

- If MI is monotonically non-decreasing for >85% of problems on both models: the channel coding model's DPI holds empirically, and the distribution-steering alternative loses its diagnostic advantage.
- If elbow points agree across models within 15% for >75% of problems: scaling is task-dependent, vindicating the target paper's framework and undermining the model-dependence claim.
- If accuracy at 2× length doesn't drop by >1pp: anti-scaling doesn't exist in practice, and the log-concave bound's asymptotic flatness is the full story.
- All four failures together would be a strong confirmation of the target paper. Each individual failure is informative on its own.

### Resource Estimate

200 problems × 2 models × 50 trajectories = 20K generations (natural length, ~256 tokens avg) + 100 problems × 2 models × 50 trajectories × 2 extended lengths = 20K additional generations. Total ~40K generations at ~256 tokens = ~10M tokens. At ~2.5K tok/s on A100: **~25 minutes** for inference. Layer extraction adds ~30% overhead for the Llama runs: **~30 minutes total**.

---

## Hypothesis 3: Circuit Depth, Not Kolmogorov Complexity, Governs Reasoning Scaling — With a Practical Compression-Based Detector

### What This Combines

| Source | Contribution |
|--------|-------------|
| **Contrarian H3** | Core claim: circuit depth (sequential computation steps) is the right complexity measure, not Kolmogorov complexity (description length) |
| **Pragmatist H1** | Gzip compression as a cheap proxy — but this time testing whether it fails when K and depth diverge |
| **Pragmatist H3** | Majority-vote saturation as an alternative measurement surface that avoids per-step MI estimation |
| **Innovator H4** | Hidden-state probing to measure "dark reasoning" that may track circuit depth better than token-level analysis |

### Synthesized Claim

The target paper's results hold on benchmarks where Kolmogorov complexity and circuit depth are confounded. When these are deliberately decorrelated, **circuit depth will predict reasoning scaling (elbow points, majority-vote saturation rates) while Kolmogorov complexity will not**. Furthermore, gzip compression — the pragmatist's proposed proxy — will fail specifically on the decorrelated tasks, revealing it as a proxy for description length (which it literally is) rather than computational depth. The constructive replacement: a **step-count proxy** (count the number of sequential operations in the minimal algorithm for the task, estimable by humans or by prompting an LLM to outline the solution steps) will predict scaling curves with higher fidelity.

### Why This Is Stronger Than Any Single Perspective

The contrarian identifies the conceptual vulnerability (K ≠ depth) but doesn't provide a practical alternative metric. The pragmatist's gzip proxy is elegant but, if the contrarian is right, will fail exactly where it matters most. By combining both, we get a *diagnostic* experiment: test gzip on the decorrelated tasks, and when it fails, demonstrate that the step-count proxy succeeds. This converts a theoretical critique into a practical engineering recommendation.

The pragmatist's majority-vote saturation framework (H3) provides a cleaner measurement surface than per-step MI estimation: instead of measuring information gain per reasoning step (noisy, requires prefix log-probabilities), measure how fast majority voting saturates (straightforward accuracy measurement). The saturation rate γ from the pragmatist's power-law model should correlate with circuit depth, not K.

### Unresolved Disagreement

There is a genuine three-way tension:
- The **target paper** says K governs everything.
- The **contrarian** says circuit depth governs everything.
- The **pragmatist** says we just need a cheap proxy that works empirically, and doesn't care which theoretical construct is "right."

This experiment can settle the first two but not the third — if the step-count proxy works, the pragmatist will (correctly) adopt it without caring about the circuit complexity theory behind it. The theoretical question of *why* circuit depth works (is the transformer really simulating circuits?) remains open.

### Experimental Design

1. **Task construction** (the critical piece):
   - **High-K, Low-depth (100 problems):** Large lookup / recall tasks. E.g., "What is the capital of [obscure country]?" (high K — specific facts), "What is the 5th element of the sequence [long predefined sequence]?" Format: the answer requires retrieving a specific datum, not multi-step computation.
   - **Low-K, High-depth (100 problems):** Iterative computation with tiny program descriptions. E.g., "Starting with x=7, repeatedly apply x → (3x+1)/2 if odd, x/2 if even, for 15 steps. What is x?" (K is ~20 bytes; depth is 15 sequential steps). Also: multi-step logic chains, string rewriting with specified iteration counts.

2. **Measurements per problem:**
   - Gzip compression length of the problem statement.
   - Human-annotated step count (minimum sequential operations). For scale, use LLM-generated step counts validated on a 20-problem calibration set.
   - Majority-vote accuracy at N = 1, 3, 5, 9, 17, 33 samples (temperature 0.7).
   - Elbow point: the N at which marginal accuracy gain per doubling drops below 1pp.
   - Saturation exponent γ from power-law fit.

3. **Analysis:** Compute correlations between (gzip_length, step_count) and (elbow_point, γ). If circuit depth is the right measure, step_count will dominate; if K is right, gzip will dominate; if neither works, we're in the pragmatist's worst case.

### Measurable Predictions

| # | Prediction | Threshold |
|---|-----------|-----------|
| P1 | Elbow point correlates with step count | r > 0.65 across all 200 problems |
| P2 | Elbow point decorrelates from gzip length on this task set | r < 0.35 |
| P3 | On the high-K/low-depth bucket specifically, gzip predicts poorly | r < 0.25 within bucket |
| P4 | Saturation exponent γ is predictable from step count | R² > 0.60 via simple regression |
| P5 | Step-count proxy matches empirical elbow within 25% | >65% of held-out problems (40 per bucket) |

### Failure Conditions

- If gzip length predicts elbow points at r > 0.55 even on the decorrelated task set: Kolmogorov complexity (or its proxy) is the better predictor, and the circuit depth alternative is rejected.
- If step count predicts no better than gzip (Δr < 0.1): the two complexity measures are either both wrong or both right in ways that don't help disambiguate the theory.
- If neither measure achieves r > 0.4: the scaling behavior is model-specific rather than task-intrinsic, which would confirm the contrarian H1 (model-dependence) and invalidate the entire enterprise of task-complexity-based inference budgeting.

### Resource Estimate

200 problems × 6 sample counts × 64 trajectories per N = 76.8K generations. Average ~200 tokens each = ~15M tokens. At ~3K tok/s: **~20 minutes on A100**. Task construction and step-count annotation: ~30 minutes of human effort (or 5 minutes with LLM-assisted annotation + calibration). Total: **<30 minutes compute + 30 minutes prep**.

---

## Summary: How the Three Hypotheses Interlock

```
                    ┌─────────────────────────────┐
                    │    TARGET PAPER CLAIMS:      │
                    │  Log-concave MI bounds on    │
                    │  test-time compute, governed │
                    │  by Kolmogorov complexity    │
                    └──────────┬──────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                 ▼
    ┌─────────────────┐ ┌────────────┐ ┌──────────────────┐
    │   H1: Is the    │ │ H2: Is the │ │  H3: Is the      │
    │   curve even    │ │ model even │ │  complexity       │
    │   smooth?       │ │ right?     │ │  measure right?   │
    │                 │ │            │ │                    │
    │  Tests:         │ │ Tests:     │ │ Tests:            │
    │  - Per-problem  │ │ - MI mono- │ │ - K vs. circuit   │
    │    staircase    │ │   tonicity │ │   depth on        │
    │  - Elbow stab-  │ │ - Model    │ │   decorrelated    │
    │    ility under  │ │   depend-  │ │   tasks           │
    │    resampling   │ │   ence     │ │ - Gzip vs. step-  │
    │  - Temperature  │ │ - Anti-    │ │   count proxy     │
    │    interaction  │ │   scaling  │ │                    │
    └─────────────────┘ └────────────┘ └──────────────────┘
```

**If H1 succeeds:** The framework needs revision at the measurement level — work at per-problem granularity, not population averages.

**If H2 succeeds:** The framework needs revision at the model level — CoT is constructive, not extractive, and inference budgets must be model-specific.

**If H3 succeeds:** The framework needs revision at the complexity measure — replace K with circuit depth.

**If all three fail:** The target paper is more robust than any of us expected, and the log-concave MI bound on test-time compute is a genuine, universal, practically useful result. That would be the most surprising and important outcome of all.

`★ Insight ─────────────────────────────────────`
**The meta-design principle:** These three hypotheses are structured as a **fault tree analysis** of the target paper. Each one isolates a single layer of the theoretical stack (measurement surface, generative model, complexity measure) and tests it independently. This means the experimental results are *compositional* — you learn something regardless of which combination of outcomes you get. The 8 possible outcome combinations (3 binary hypotheses) each tell a different story about what kind of theory test-time compute scaling actually needs. That combinatorial informativeness is what makes this a strong research proposal rather than just three disconnected experiments.
`─────────────────────────────────────────────────`