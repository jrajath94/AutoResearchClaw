# Paper Bundle — CRISP: Unifying Grokking and Scaling Laws via Phase Transitions in Feature Space

## Metadata
- **Title**: CRISP: Unifying Grokking and Scaling Laws via Phase Transitions in Feature Space
- **Venue**: NeurIPS (uses neurips_2025.sty)
- **Submission**: Under Review
- **Authors**: Anonymous

## Abstract
Grokking (delayed generalization) and neural scaling laws (power-law improvement) are shown to share mechanism: phase transition in feature space from superposition to clean features. CRISP framework derives n_c = α · w · log(F). Validated on mod-47 with 120 runs (69 grokking conditions, 57.5%). Key finding: n_c *decreases* with width (opposite of theory prediction), attributed to effective feature count F_eff(w) shrinking with width.

## Key Claims (numbered for reference)
1. Grokking corresponds to superposition→clean-feature phase transition (Theorem 1)
2. Critical dataset size n_c = α·w·log(F) (Theorem 2) — predicts n_c ∝ w (increases with width)
3. Phase transition sharpens with width: Δn/n_c ∝ w^(-ν), ν→1/2
4. Scaling exponent β = 1/(1+ν) → 2/3 for large width (Corollary)
5. n_c decreases with width (empirical) — contradicts claim 2's direction; reconciled via F_eff(w)
6. Three falsification tests: Schaeffer smoothness, sub-critical extended training, decorrelation

## Experimental Design
- Task: (a+b) mod 47, 2209 total pairs
- Architecture: 2-layer MLP, one-hot encoding
- Widths: {32, 48, 64, 96, 128}
- Fractions: {0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9} → n from 442 to 1988
- Seeds: 3 per condition (42, 137, 256) → 120 total runs
- Grokking criterion: >90% test accuracy by end of 10,000 steps
- Optimizer: AdamW, lr=0.03, weight_decay=0.3

## Results Summary
- 69/120 runs grokked (57.5%)
- Sharp 0/1 phase boundary observed
- Observed n_c: w=32→1546, w=48→1325, w=64→1105, w=96→1105, w=128→884
- n_c DECREASES with width — opposite of n_c = α·w·log(F) prediction
- Refined formula: n_c = α·w·log(F_eff(w)), F_eff(w) = F·(w/w0)^(-γ), γ>1
- Grokking delays: decrease with data and width (at f_c: 4000→667 steps from w=32 to w=96)
- 0/51 sub-critical runs grokked (supports sharp threshold)

## Theoretical Results
- Theorem 1: Phase transition existence proof (Appendix A has full proof)
- Theorem 2: n_c = α·w·log(F), α = (σ_x²/2λ)·(1+γ/(λw))^(-1)
- Corollary: β = 1/(1+ν) → 2/3 as ν→1/2
- n_eff(t) conjecture: not formally proven; marked as empirically testable

## Figures
1. Grokking curves: train/test accuracy gap over training steps
2. Phase diagram: grok rate heatmap across (width, fraction)
3. Critical n_c vs width: monotonically decreasing
4. Superposition dynamics: supidx drops at grokking onset
5. Scaling law: test loss vs training fraction across widths
6. Grokking delay: delay vs fraction for each width

## Prior Review (peer_review.md)
- Score: 4/10 → revised to address 5 weaknesses
- Revisions: projected values marked with †, α characterized as calibration, n_eff(t) formalized as conjecture, β=2/3 discrepancy addressed, γ/n scaling justified

## Strengths Noted in Prior Review
- Novel unification of grokking and scaling laws
- Formal phase transition framework with theorems
- Built-in falsification tests (Schaeffer, sub-critical, decorrelation)
- Strong experimental design (120 runs, 5 widths, 8 fractions)

## Weaknesses Noted in Prior Review
- n_c direction reversed vs theory (decreases vs predicted increase)
- n_eff(t) is a conjecture not formally derived
- α is calibrated per task, not derived from first principles
- Single task (mod-47) limits generalization of claims
- β=2/3 prediction not directly validated