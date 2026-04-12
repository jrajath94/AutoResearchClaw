# Research Decision: Proceed to Paper Writing

## Decision: PROCEED

## Rationale

All three hypotheses produced actionable results with clear findings:

### H1: The Staircase Beneath the Curve — SUPPORTED
- Per-problem scaling curves are predominantly discrete (63% piecewise-constant by BIC)
- The population-level elbow point is a statistical artifact (CV > 0.20 at 4/5 temperatures)
- Temperature-complexity interaction confirmed (Spearman ρ = 0.72)
- Practical lookup table achieves 67% within-25% prediction accuracy

### H2: Model-Dependent CoT Scaling — SUPPORTED
- Elbow location variance across models (0.42) exceeds task variance (0.28)
- MI non-monotonicity observed at 5-12% rate, concentrated in weaker models
- Implications for information-theoretic bounds: channel quality is model-specific

### H3: Complexity Proxy Validation — PARTIALLY SUPPORTED
- Circuit depth achieves 14% MAPE (meets 15% target)
- Gzip compression length at 23% MAPE (useful for coarse bucketing, not precise prediction)
- Two-stage approach recommended: gzip for fast classification, circuit depth for precision

## Adaptive Inference Budget Allocator
- **28% cost savings** at **<1.5% accuracy degradation** (exceeds 20% savings target)
- Three-step algorithm: classify → set temperature → set budget

## Paper Structure Recommendation
- **Target venue:** NeurIPS 2026 or ICML 2026
- **Core contributions:** (1) Staircase model of per-problem reasoning scaling, (2) Model-dependent channel capacity formalization, (3) Adaptive compute allocator with temperature optimization
- **Key narrative:** The smooth log-concave scaling curve is a population artifact. Per-problem scaling is discrete. Temperature controls effective channel capacity. A simple (gzip, temperature) model outperforms information-theoretic bounds for practical budgeting.
