## Hypothesis 1: Compression-Length Proxy for Elbow Point Prediction

**Concrete Claim:** The elbow point where additional chain-of-thought reasoning stops improving accuracy can be predicted — without running any CoT at all — using the **gzip compression length** of the problem statement as a cheap proxy for Kolmogorov complexity. Specifically, a simple linear regression `T_elbow = α · len(gzip(prompt)) + β` will predict the optimal reasoning token budget per-query within 20% of the empirically observed elbow point.

**Why This Is Achievable with Limited Compute:**
- gzip compression is essentially free (microseconds per problem).
- The expensive part is building the calibration set: run one model on ~500 problems across 3 task types (arithmetic, logic, coding) at 5 different max-token budgets (e.g., 64, 128, 256, 512, 1024 tokens), record accuracy at each budget, and fit the elbow via piecewise-linear regression. This is ~12,500 generations of short sequences on a 7–8B model.
- Total estimated wall-clock: **15–20 minutes on a single A100** with Llama-3-8B and vLLM batching.
- The linear regression fit itself takes seconds.

**Rationale Based on Proven Techniques:**
- Gzip compression length is a well-established, empirically validated proxy for Kolmogorov complexity (see: Jiang et al., 2023 "Low-Resource Text Classification: A Parameter-Free Classification Method with Compressors" — gzip-based classification achieved competitive NLP results).
- The target paper's theoretical framework explicitly conditions on bounded Kolmogorov complexity `K`. If their bounds are correct, then any monotonic proxy for `K` should correlate with the elbow point. Gzip length is the simplest such proxy.
- Gap 3 from the synthesis identifies the missing link between theoretical scaling curves and deployable inference budgeting. This hypothesis fills that gap with the simplest possible engineering solution.

**Measurable Prediction and Failure Condition:**
- **Prediction:** The Pearson correlation between `len(gzip(prompt))` and empirically measured `T_elbow` will exceed `r = 0.70` across a held-out test set of 150 problems (50 per task type). The regression will predict elbow points within 20% relative error for >65% of test problems.
- **Failure condition:** If `r < 0.45` or if the 20%-accuracy threshold is met for <40% of test problems, the hypothesis is rejected. This would indicate that surface-level problem complexity is a poor proxy for the computational depth required to solve it, and more sophisticated features (e.g., dependency parse depth, number of variables) are needed.

**Resource Requirements:**
| Resource | Amount |
|----------|--------|
| GPU | 1× A100 (40GB sufficient) |
| Model | Llama-3-8B-Instruct (open weights) |
| Inference framework | vLLM for batched generation |
| Dataset | GSM8K (arithmetic), ProntoQA (logic), HumanEval-lite (coding) — all publicly available |
| Total generations | ~12,500 (calibration) + ~3,750 (test) |
| Wall-clock time | ~20 minutes inference + 5 minutes analysis |

---

## Hypothesis 2: Early-Layer Confidence Divergence as a Real-Time Stopping Signal

**Concrete Claim:** You can build a practical, zero-overhead early stopping mechanism for chain-of-thought generation by monitoring the **KL divergence between the output distribution at an early layer and the final layer** during generation. When this divergence drops below a threshold (the early and final layers "agree"), the model has extracted most available information from further reasoning, and generation can be stopped. This will save **30%+ tokens** on average while losing **<2 percentage points** of accuracy compared to full-length generation.

**Why This Is Achievable with Limited Compute:**
- No training required — this is a pure inference-time heuristic applied to an existing model.
- Computing the early-layer logits requires a single additional forward pass through a partial network, or (more efficiently) caching intermediate activations that many inference frameworks already expose.
- Evaluation: run the same 500-problem calibration set from Hypothesis 1, comparing full-length CoT accuracy vs. early-stopped CoT accuracy at 3–4 different KL thresholds.
- Total estimated time: **20–25 minutes on a single A100** (the early-layer extraction adds ~15% overhead per generation, offset by shorter average sequences).

**Rationale Based on Proven Techniques:**
- Early-exit methods are well-established in the efficient inference literature (Schuster et al., 2022 "Confident Adaptive Language Modeling"; Elbayad et al., 2020). These typically use per-token confidence to skip layers within a single forward pass. We extend this idea to the *sequence level*: instead of skipping layers per token, we use layer agreement as a signal to stop *generating more tokens*.
- The target paper frames CoT as iterative channel coding where each step adds mutual information. The layer-agreement signal is a practical proxy for "the current reasoning step is no longer adding new information" — when early and late layers agree, the model's representation has converged and additional tokens are redundant.
- Gap 5 identifies the unexplored connection between information-theoretic bounds and practical verification. This hypothesis provides a lightweight, engineering-friendly version of that connection: layer divergence as an online estimate of marginal information gain.

**Measurable Prediction and Failure Condition:**
- **Prediction:** At the optimal KL threshold (selected on the calibration set), early stopping will: (a) reduce average generation length by ≥30%, and (b) reduce accuracy by ≤2 percentage points, across all 3 task types on the held-out test set.
- **Secondary prediction:** The token savings will be *inversely correlated* with task difficulty — easy problems (low gzip complexity) will see 50%+ savings, while hard problems will see <15% savings, consistent with the target paper's log-concave scaling model.
- **Failure condition:** If accuracy drops by >5pp at any threshold that achieves ≥20% token savings, or if the optimal threshold varies so dramatically across task types that no single threshold works, the hypothesis is rejected. The first failure would indicate that layer agreement is a poor proxy for reasoning sufficiency; the second would indicate the signal is task-specific and not generalizable.

**Resource Requirements:**
| Resource | Amount |
|----------|--------|
| GPU | 1× A100 (40GB sufficient) |
| Model | Llama-3-8B-Instruct with hooks for intermediate layer logits |
| Inference framework | HuggingFace Transformers (need layer access; vLLM doesn't easily expose this) |
| Dataset | Same as Hypothesis 1: GSM8K, ProntoQA, HumanEval-lite |
| Modification | ~50 lines of Python to extract layer-16 logits and compute online KL |
| Wall-clock time | ~25 minutes inference + 10 minutes threshold sweep and analysis |

---

## Hypothesis 3: Majority-Vote Saturation Curves Follow Predictable Power Laws Per-Task-Bucket

**Concrete Claim:** For a given model and task, the accuracy of **majority voting over `N` independent CoT samples** (a simple, well-understood test-time compute scaling method) follows a power law `Acc(N) = A - B · N^(-γ)` where the exponent `γ` is predictable from two cheap-to-measure features: (1) the model's single-sample accuracy on that task category, and (2) the average pairwise disagreement rate among 5 pilot samples. A simple lookup table mapping `(single_acc, disagreement)` → `γ` will predict the majority-vote saturation curve well enough to determine the cost-optimal `N` per problem.

**Why This Is Achievable with Limited Compute:**
- Majority voting is the simplest possible test-time scaling method — no special prompting, no process reward models, no tree search. Just sample multiple times and take the mode.
- The pilot phase (5 samples per problem) is cheap: 500 problems × 5 samples = 2,500 generations.
- The full curve fitting phase: 200 problems × 32 samples each = 6,400 generations. Short CoT (≤256 tokens each).
- Total: ~8,900 generations. Estimated **15 minutes on A100** with vLLM.

**Rationale Based on Proven Techniques:**
- Majority voting (self-consistency; Wang et al., 2023) is already the standard baseline for test-time compute scaling. The power-law form for accuracy-vs-samples is empirically observed but not well-characterized per-task.
- The target paper's log-concave MI bound predicts that marginal information per additional reasoning trace should decrease. For majority voting, each independent sample is a noisy observation of the correct answer, and classical results from voting theory (Condorcet's jury theorem) predict power-law convergence when individual accuracy > 0.5. The exponent depends on the "signal strength" — exactly what single-sample accuracy and disagreement rate capture.
- Gap 3 identifies the need for practical inference budgeting. This hypothesis provides the simplest possible version: a lookup table that tells you "for this type of problem with this baseline accuracy, you need N samples and adding more is wasteful."

**Measurable Prediction and Failure Condition:**
- **Prediction:** The fitted `γ` exponent will be predictable from `(single_acc, disagreement)` with `R² > 0.75` across task buckets. The predicted cost-optimal `N*` (where marginal accuracy gain per sample drops below 0.1pp) will match the empirically optimal `N*` within ±3 samples for >70% of task buckets.
- **Failure condition:** If `R² < 0.50` for the `γ` prediction, or if the lookup table's `N*` recommendation is off by >2× for >40% of buckets, the hypothesis is rejected. This would indicate that the saturation dynamics depend on features not captured by accuracy and disagreement alone (e.g., the specific error distribution matters, not just its rate).

**Resource Requirements:**
| Resource | Amount |
|----------|--------|
| GPU | 1× A100 |
| Model | Llama-3-8B-Instruct |
| Inference framework | vLLM (batched sampling, temperature=0.7) |
| Dataset | GSM8K (800 problems, stratified by difficulty), ProntoQA (200), MBPP (200) |
| Total generations | ~8,900 (pilot + curve fitting) |
| Wall-clock time | ~15 min inference + 10 min curve fitting (scipy) |

---

`★ Insight ─────────────────────────────────────`
**Engineering philosophy behind these hypotheses:** Each one follows a deliberate pattern — take the target paper's theoretical insight (log-concave MI bounds, diminishing returns, Kolmogorov complexity dependence) and find the *cheapest possible empirical proxy* that captures the same signal. Hypothesis 1 replaces Kolmogorov complexity with gzip length. Hypothesis 2 replaces mutual information measurement with layer-agreement monitoring. Hypothesis 3 replaces the full channel-coding framework with Condorcet-style voting theory. The goal is to find which theoretical insight survives the compression down to a practical, deployable heuristic — because that's what actually ships.
`─────────────────────────────────────────────────`