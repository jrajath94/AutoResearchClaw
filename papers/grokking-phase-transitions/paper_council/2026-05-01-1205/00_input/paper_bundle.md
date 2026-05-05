# Paper Context Bundle — CRISP Paper

## Metadata
- **Title:** CRISP: Unifying Grokking and Scaling Laws via Phase Transitions in Feature Space
- **Authors:** Anonymous (Under Review)
- **Venue:** NeurIPS 2025 (neurips_2025.sty)
- **Date:** 2026-05-01

---

## Abstract
Grokking (sudden generalization long after memorization) and neural scaling laws (smooth power-law improvement with data) are treated as distinct. We prove they share a common mechanism: a phase transition in the network's internal feature representation, from superposed to clean features, at a critical dataset size n_c.
- Introduces CRISP (Critical Superposition Phase transition), an energy-landscape framework with explicit interference penalty, inspired by Elhage et al. 2022 toy models of superposition
- Main result: closed-form n_c = α · w · log(F) where w=width, F=latent features, α=task-dependent constant
- Corollary: β = 1/(1+ν) connects sharpening exponent ν to scaling law slope
- Validated on modular arithmetic (mod-47) with 120 runs (5 widths × 8 fractions × 3 seeds)
- Key finding: n_c *decreases* with width — opposite of naive CRISP prediction — attributed to effective feature count F_eff(w) that shrinks with width

---

## Section-by-Section Summary

### 1. Introduction
Two phenomena: (1) Grokking — delayed emergence of generalization after memorization; (2) Neural scaling laws — power-law test loss vs dataset size with characteristic "knee" points.
Four contributions:
- C1: Formal proof that grokking = superposition→clean phase transition (Theorem 1)
- C2: Closed-form n_c = α·w·log(F) for critical dataset size (Theorem 2)
- C3: Three built-in falsification tests (Schaeffer smoothness, sub-critical extended training, feature decorrelation)
- C4: 120-run validation on mod-47, showing n_c decreases with width (counter to naive prediction)

### 2. Related Work
- Grokking: Power et al. 2022, Nanda et al. 2023 (circuit competition), Liu et al. 2023 (delayed feature learning), Thilak et al. 2022 (slingshot dynamics)
- Neural scaling: Kaplan et al. 2020, Hoffmann et al. 2022 (Chinchilla/compute-optimal), Caballero et al. 2023 (broken scaling), Bahri et al. 2024
- Phase transitions: Saxe et al. 2014, Goldt et al. 2020, Schaeffer et al. 2024 (smoothness test as falsification)
- Superposition: Elhage et al. 2022 (toy models)

### 3. Theory (CRISP Framework)

#### 3.1 Representation Energy Landscape
E(Φ;n) = Σᵢ ℓᵢ(φᵢ;D) + λ Σᵢ≠ⱼ |<φᵢ,φⱼ>|² − (γ/n) Σᵢ log||φᵢ||²
Three terms: reconstruction loss + interference penalty + entropic regularization (scales as 1/n)
Two classes of minima: Superposition (F > w features, interference patterns) vs Clean (near-orthogonal subspaces)

Superposition index: S(Φ) = 1/(F(F−1)) Σᵢ≠ⱼ |<φ̂ᵢ,φ̂ⱼ>|²

#### 3.2 Phase Transition Existence (Theorem 1)
- For n < n_c: global minimum is superposed (S = Θ(1))
- For n > n_c: global minimum is clean (S = O(F⁻²))
- Transition sharpens with width: Δn/n_c = O(w^(−ν)), ν > 0

Connection to grokking: n_eff(t) (effective dataset utilization) increases with training steps; when it crosses n_c, the globally stable minimum shifts from superposition to clean, requiring traversal of an energy barrier → characteristic delay between memorization and generalization.

Connection to scaling laws: Same transition explains knee. For n < n_c (superposition regime), test loss decreases slowly. For n > n_c (clean features), rapid power-law generalization.

Note: n_eff(t) is presented as a conjecture, not formally derived.

#### 3.3 Critical Dataset Size (Theorem 2)
n_c = α · w · log(F)
where α = (σ²/2λ) · (1 + γ/(λw))⁻¹
Transition width: Δn = n_c · C · w^(−ν), ν = 1/2 + O(w⁻¹)

naive prediction: n_c ∝ w (increases with width)
BUT experiments show: n_c DECREASES with width

Reconciliation: refined formula n_c = α · w · log(F_eff(w)) where F_eff(w) = F · (w/w₀)^(−γ), γ > 1. Wider networks learn more efficient/better feature bases, reducing effective feature count faster than width increases.

Note: α is calibrated empirically at w=256, then used to predict n_c at other widths.

#### Corollary (Scaling Exponent)
β = 1/(1+ν), with ν → 1/2 for large width → β → 2/3

### 4. Experimental Design
- Task: (a+b) mod 47, 47² = 2,209 pairs, one-hot encoding
- 2-layer MLPs, widths {32, 48, 64, 96, 128}, fractions {0.2..0.9}
- 3 seeds per condition (42, 137, 256) → 120 total runs
- AdamW, lr=0.03, wd=0.3, 10,000 steps
- Grokking criterion: >90% test accuracy by end of training
- Grokking delay: steps from 99% train accuracy to 90% test accuracy
- Observed n_c: smallest training set size where ≥50% of seeds grok

Three falsification tests:
- F1 (Schaeffer smoothness): If apparent transition is metric artifact, log-loss should show no transition
- F2 (Sub-critical extended training): If merely about training long enough, sub-critical runs should eventually grok. Result: 0/51 sub-critical runs grokked
- F3 (Decorrelation): If mechanism is superposition→clean, then superposition index S must drop at same n_c where grokking observed. Requires r > 0.8 correlation

### 5. Results

**Phase Diagram (Table 2 / Fig 2):**
- 69/120 runs exhibited grokking (57.5%)
- Sharp 0/1 phase boundary separating memorization from generalization
- For w=32: transition spans f=0.6→0.7 (soft, with 33% at f=0.6)
- For w=128: transition is a single step from 0% at f=0.3 to 100% at f=0.4

**Critical Dataset Size (Table 3):**
| Width | f_c | n_c (observed) | Direction |
|---|---|---|---|
| 32 | 0.7 | 1,546 | — |
| 48 | 0.6 | 1,325 | decrease |
| 64 | 0.5 | 1,105 | decrease |
| 96 | 0.5 | 1,105 | plateau |
| 128 | 0.4 | 884 | decrease |

KEY FINDING: n_c decreases monotonically with width (opposite of naive prediction n_c ∝ w)

**Grokking Delays (Table 4):**
- Delays decrease with data: at w=64, delay drops from 8,333 (f=0.5) to <1,000 (f≥0.7)
- Delays decrease with width: at f=0.5, delay drops from 8,333 (w=64) to 1,333 (w=128)

**Scaling with Width (Fig 3):**
43% reduction in data requirement when quadrupling width from 32→128

### 6. Discussion
- Practical implication: 0/51 sub-critical runs grokked; training at n ≈ (1.2–1.5)n_c is efficient operating point
- Relationship to existing theories: circuit competition = competition between two energy minima; logarithmic F-dependence reflects high-dimensional packing geometry
- What theory gets right: sharp phase transition at critical n
- What theory gets wrong: direction of n_c(w); treated as refinement via F_eff(w)
- Limitations: sub-Gaussian assumption, F must be known/estimated, α calibrated per task family, only 2-layer MLPs w≤128

### 7. Conclusion
CRISP explains grokking as phase transition; validated on mod-47. Key surprise: n_c decreases with width. Future: derive F_eff(w) from first principles, extend to transformers and larger tasks.

### Appendix A: Full Proofs
- Theorem 1 proof: gradient condition characterization → two classes of critical points → energy comparison via intermediate value theorem → concentration of measure for transition width
- Theorem 2 proof: solving ΔE(n_c) = 0 → simplified to n_c ≈ (γ/(λc)) · w · log(F)
- Corollary proof: test loss decomposition in clean regime → effective scaling exponent

### Appendix B: Experimental Details
Full hyperparameter table; superposition index computation via PCA on penultimate-layer activations; n_c identification procedure

### NeurIPS Paper Checklist (all Yes/NA)
- Claims: Yes
- Limitations: Yes (Section 6)
- Theory assumptions: Yes (Appendix A)
- Experimental reproducibility: Yes
- Open access: Yes (reproduce.py, JSON logs)
- Code of ethics: Yes

---

## Explicit Claims (Numbered)
1. Grokking = phase transition from superposition to clean features (Theorem 1, C1)
2. Critical dataset size n_c = α · w · log(F) (Theorem 2, C2)
3. Transition sharpens with width: Δn/n_c = O(w^(−ν)) (Theorem 2)
4. Scaling exponent β = 1/(1+ν), with ν → 1/2 → β → 2/3 (Corollary 1)
5. 0/51 sub-critical runs grokked (F2 falsification result)
6. n_c decreases with width (Table 3 — contradicts naive theory)
7. Grokking delay decreases with both data and width (Table 4)
8. F_eff(w) = F · (w/w₀)^(−γ), γ > 1 (reconciliation hypothesis)

---

## Experimental Conditions
- Task: (a+b) mod 47, 2209 total pairs
- Architectures: 2-layer MLP, one-hot encoding
- Widths: {32, 48, 64, 96, 128}
- Training fractions: {0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9}
- Seeds: 3 (42, 137, 256) per condition
- Total: 120 runs
- Grokking criterion: >90% test accuracy by 10,000 steps
- Prior runs available in artifacts/code/results/

---

## Figures and Tables

### Tables
- **Table 1** (Predictions): Testable predictions of CRISP — grokking threshold, scaling knee, sharpening, scaling exponent, sub-critical block, decorrelation
- **Table 2** (Full results): Grok rate (%) for all 40 conditions — sharp 0/1 boundary
- **Table 3** (nc observed): Observed critical dataset size per width — n_c DECREASES with w
- **Table 4** (Delays): Mean grokking delay across conditions

### Figures
- **Fig 1** (Grokking curves): Training/test accuracy curves, gap between memorization and generalization
- **Fig 2** (Phase diagram): Heatmap of grok rate vs width and fraction — sharp diagonal boundary shifting leftward
- **Fig 3** (Critical nc): n_c as function of width — monotonically decreasing
- **Fig 4** (Superposition dynamics): Superposition index S(t) during training — drops sharply at grokking onset
- **Fig 5** (Scaling law): Final test loss vs training fraction — pronounced knee at n_c
- **Fig 6** (Grokking delay): Delay vs training fraction per width — transition sharpens with width

---

## Prior Reviews
- **Prior review** (deliverables/peer_review.md): Score 4→10 after revisions. Applied fixes: placeholders→projected values, α characterization clarified, n_eff(t) as conjecture, β=2/3 discrepancy addressed, γ/n scaling justified

---

## Venue Detection
- paper.tex uses \usepackage{neurips_2025}
- Target: NeurIPS 2025 (submitted)
- Rubric: NeurIPS 2026 (current call for papers)
