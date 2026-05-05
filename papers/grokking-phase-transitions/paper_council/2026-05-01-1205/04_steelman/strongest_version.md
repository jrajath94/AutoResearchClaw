# CRISP Steelman — Strongest Version of the Paper

**Paper:** CRISP: Unifying Grokking and Scaling Laws via Phase Transitions in Feature Space
**Date:** 2026-05-01
**Review Bundle:** 6 independent reviews + 5 cross-examinations

---

## IRREDUCIBLE CONTRIBUTION

**What survives even the worst criticism — the part that cannot be denied:**

### 1. The static phase transition theorem is sound (Theorem 1)

Every reviewer who engaged with the proofs acknowledged they are correct. The Theory Critic (who gave Soundness 5/10) explicitly stated: "Theorem 1 correctly characterizes a bimodal energy landscape... The proof via gradient conditions and intermediate value theorem is sound for the stated energy functional." The Domain Expert confirmed "the formal proof sketch... correctly identifies two classes of critical points (superposed vs. clean)." Even the most critical reviewers accepted the static theorem's correctness.

**This is not mod-47 specific.** The energy landscape framework and the proof that E(Φ;n) has two classes of minima is a general result about representation learning, not a finding about modular arithmetic.

### 2. F2 (0/51 sub-critical runs grokked) is a genuine, striking falsification result

This was the most praised empirical result across all reviews. The Big Picture Editor called it "exactly the kind of evidence that earns lasting credibility." The Adversarial Practitioner said "this is how you build confidence: show that your theory survives attempts to falsify it." The Naive Reader (who gave the harshest overall scores) called it "the kind of concrete negative result that makes a theory falsifiable rather than unfalsifiable."

This result cannot be explained away. The paper establishes a clean binary: below a data threshold, generalization never emerges regardless of training time. This is real and valuable regardless of what the theory says about n_eff(t) or F_eff(w).

### 3. The sharp 0/1 phase boundary is a genuine empirical discovery

At w=128, grokking jumps from 0% at f=0.3 to 100% at f=0.4. Every reviewer called this the paper's most visually striking result. The Naive Reader said "I could show this figure to a non-expert and they would understand why this suggests a phase transition." The Domain Expert called it "convincing evidence that grokking is threshold-driven rather than gradual."

Even if the theory requires patching (F_eff(w)), the empirical finding is real: there is a sharp, near-deterministic phase boundary separating memorization from generalization.

### 4. The n_c decreases with width finding is a genuine empirical surprise

The paper's central empirical finding — n_c monotonically decreases from 1,546 (w=32) to 884 (w=128) — is real, repeated, and consistent across seeds. The Big Picture Editor (who overall was critical) called this "a surprising, testable finding that genuinely falsifies naive CRISP prediction." The Theory Critic called it "intellectually honest." Regardless of whether F_eff(w) is derived or patched, the empirical trend is a genuine discovery that demands explanation.

### 5. The CRISP organizing concept is reusable intellectual infrastructure

The framing — "grokking and scaling law knees are the same phase transition" — gives researchers a single conceptual lens to reason about two previously separate phenomena. The Big Picture Editor predicted "this will be cited" and the Naive Reader said "at a department lunch, one sentence summary: grokking and scaling law knees are the same phase transition." Even if every specific quantitative prediction were wrong, the conceptual unification is a lasting contribution.

---

## STRONGEST VERSION

**If all weaknesses were addressed, what would this paper look like:**

### n_eff(t) Formally Derived from Training Dynamics

In the strengthened version, n_eff(t) is not a conjecture but a derived quantity. The paper derives n_eff(t) from PAC-Bayes principles or accumulated Fisher information:

**n_eff(t) = (1/t) ∑_{s=1}^{t} Tr(∇² log p_θ_s(D))**, or equivalently, the effective sample size from gradient covariance tracking. This makes the connection between training dynamics and phase transition rigorous. The paper shows empirically that n_eff(t) trajectories cross n_c at the observed grokking delay across 10 representative runs, with crossing step correlated r > 0.9 with generalization onset.

### F_eff(w) Derived from Spectral Analysis of Task

Instead of introducing F_eff(w) = F·(w/w₀)^(-γ) as an ad-hoc reconciliation, the paper derives it from the eigenvalue spectrum of the task Gram matrix. Specifically:

**F_eff(w) = ∑_i λ_i / (λ_i + c·w⁻¹)**

where λ_i are eigenvalues of the feature covariance matrix. This is derived from the condition number analysis of the superposition solution. The paper shows empirically that F_eff(w) measured from PCA on trained networks matches this functional form with no free parameters beyond those in the theory.

### F3 Decorrelation Test: r > 0.8 Reported

The paper reports F3 explicitly: Pearson correlation between superposition index S drop step and grokking onset step across all 69 grokking runs is r = 0.87 (p < 10⁻⁸). The Naive Reader (who rated missing F3 as 5/5) would be satisfied: the mechanism is confirmed. Figure 4 shows overlay of S(t) and test accuracy curves with aligned x-axes, demonstrating the superposition-to-clean transition occurs at the same training step as behavioral generalization.

### β = 2/3 Measured from Scaling Law Data

The paper fits a power law L ∝ n^(-β) to the clean regime (n > n_c) in Figure 5. For w=128 (where the transition is sharpest), the fitted β = 0.71 ± 0.08, approaching the theoretical 2/3 as width increases. For w=32, β = 0.58 ± 0.12. The paper explicitly addresses the Kaplan et al. (β ≈ 0.076) discrepancy: the CRISP β = 2/3 is a **transitional scaling exponent** in the phase transition regime (memorization-to-generalization crossover), not the same regime as LLM compute-optimal scaling. Regime separation is explicit: Kaplan measures β in the generalization-dominated regime; CRISP measures β at the transition. The paper shows theoretically that β → 2/3 at criticality but β → 0.5 (Chinchilla) in the clean asymptotic regime.

### Validation on 3+ Tasks

The paper validates on:
1. **(a+b) mod 47** — original task, 2-layer MLP
2. **Modular parity: (a·b) mod 31** — different prime, same architecture family
3. **Sparse parity: parity of 5 out of 20 input bits** — different function class, superposition structure differs

Across all three tasks, n_c decreases with width (confirming F_eff(w) is not task-specific artifact) and the phase boundary sharpness follows Δn/n_c = O(w^(-1/2)). F3 decorrelation passes on all three tasks. This establishes the mechanism is not an artifact of modular arithmetic structure.

### α Derived from First Principles, Not Calibrated

The expression α = (σ²/2λ)·(1 + γ/(λw))⁻¹ is computed from:
- σ²: empirical variance of feature activations (measured from random init, before training)
- λ, γ: interference penalty and entropic regularization (hyperparameters that appear in the theory, not fitted to n_c)

The paper holds out w=128 as a true prediction: α computed from theory and random init statistics predicts n_c at w=128 to within 12% (884 predicted vs. 884 observed). This is genuine predictive success, not curve-fitting.

---

## BEST-VERSION RUBRIC SCORES

**Estimated scores after all major revisions:**

| Dimension | Current Avg | Best-Version Estimate | Rationale |
|-----------|-------------|----------------------|-----------|
| **Originality** | 6.5 | **8/10** | Phase transition unification is genuinely novel; n_c decreases with width is a surprising discovery that required theory revision; β = 2/3 as transitional scaling exponent connecting to both grokking and LLM regimes |
| **Soundness** | 5.3 | **7/10** | Static theorem is sound; n_eff(t) is derived (not conjectured); F_eff(w) is derived from spectral analysis; F3 passes with r > 0.8; β is fitted from data; multi-task validation confirms mechanism |
| **Significance** | 6.5 | **8/10** | If β = 2/3 is validated and multi-task confirmation achieved, this becomes influential across grokking, scaling laws, and phase transition communities; practical dataset sizing recommendation (n ≈ 1.2-1.5 n_c) becomes actionable |
| **Clarity** | 7.5 | **8/10** | Table 1 is called a model of clarity; theory section is dense but honest about what's proved vs. conjectured; figures are clear; would improve with n_eff(t) definition and F_eff(w) derivation made explicit |
| **Reproducibility** | 8.0 | **9/10** | Already exemplary; reproduce.py, JSON logs, 120 runs, seeds specified; deduct 1 point only because code not personally verified |
| **Contextualization** | 6.3 | **7/10** | Good grokking literature coverage; Kaplan discrepancy explicitly addressed with regime separation argument; lottery ticket connection added; would gain points for explicit theory vs. LLM regime mapping |
| **Ethical** | 6.5 | **7/10** | Standard but adequate; would improve with discussion of how CRISP informs training pipeline design |

**Best-version weighted average:** (8×1.0 + 7×1.5 + 8×1.0 + 8×0.7 + 9×1.0 + 7×0.8 + 7×0.5) / 6.5 = (8 + 10.5 + 8 + 5.6 + 9 + 5.6 + 3.5) / 6.5 = 50.2 / 6.5 ≈ **7.7 → Strong Accept**

---

## WHAT THE AUTHORS SHOULD NOT CHANGE

**The core contribution that is solid regardless of reviewer pressure:**

### 1. Theorem 1 and the phase transition framing

The static proof that E(Φ;n) has two classes of minima (superposed vs. clean) is correct and load-bearing. Even the harshest reviewer (Adversarial Practitioner) acknowledged "the core insight (phase transition from superposition to clean features)... is compelling and likely correct in spirit." This is not worth changing — it is the paper's most durable contribution.

### 2. The F2 result (0/51 sub-critical runs grokked)

This is the paper's strongest empirical result. It is a genuine, repeatable falsification test that survived scrutiny from 6 reviewers. Do not soften this claim. The 0/51 result is evidence that grokking is not "just train longer" — it establishes a true threshold phenomenon.

### 3. The n_c decreases with width empirical finding

Every reviewer acknowledged this is a genuine empirical finding. Even if the theoretical explanation (F_eff(w)) is weak in the current version, the empirical fact that wider networks require less data to generalize (not more) is real and worth preserving. The n_c decreasing with width is surprising, counter-predicted by naive theory, and demands explanation. Future theories must account for it.

### 4. The sharp 0/1 phase boundary

The visual evidence of a crisp phase transition in Table 2 and Figure 2 is compelling and reproducible. This is the kind of result that will be shown in future talks and cited as evidence for threshold phenomena in deep learning.

### 5. Table 1 (the predictions table)

The Naive Reader called this "a model of clarity and teachability." Six predictions with formulas, observables, tolerances, and falsification criteria is exactly how theory papers should present themselves. This structure should be preserved.

### 6. The general research direction

The idea that grokking and scaling laws share a phase transition mechanism is the paper's overarching thesis. Even if the specific quantitative predictions require revision, the unifying conceptual framework is valuable and worth pursuing. Reviewer pressure to narrow scope should be resisted — the ambition to unify two seemingly unrelated phenomena is a strength, not a weakness.

---

## WHAT MUST CHANGE (Non-Negotiable for Accept)

The cross-examination revealed unanimous consensus on three issues that must be addressed:

1. **n_eff(t)** — must be derived or explicitly removed as a central claim. The paper cannot present a dynamic story about grokking timing when the link between static theorem and dynamic phenomenon is labeled "conjecture."

2. **F_eff(w)** — must be derived from the theory or acknowledged as empirical correction. Calling it a "reconciliation hypothesis" without status (theory vs. fitting) is not acceptable.

3. **F3 decorrelation result** — the paper states r > 0.8 is the pass/fail threshold, then does not report the observed r value. This is not optional to fix. Either report r and show it passes, or acknowledge failure and redesign the experiment.

4. **β = 2/3 measurement** — the most exportable prediction in the paper is asserted without empirical support. Fitting β from Figure 5 and showing it approaches 2/3 with increasing width would resolve this.

---

## Summary

The irreducible core of CRISP is:
- **Theorem 1 (sound)**: The energy landscape E(Φ;n) has two classes of minima — superposed and clean
- **F2 result (compelling)**: 0/51 sub-critical runs grokked — grokking is not "just train longer"
- **Phase diagram (real)**: Sharp 0/1 boundary at w=128 from 0% at f=0.3 to 100% at f=0.4
- **n_c decreasing with width (genuine)**: Wider networks generalize with less data — a real empirical surprise

The paper's ambition (unifying grokking and scaling laws via phase transitions) is valuable and worth preserving. The current execution has significant gaps (n_eff conjecture, F_eff(w) post-hoc, F3 missing, β untested) but the core insight is correct. After revision along the lines described above, this would be a strong Accept paper with lasting impact.

**Estimated current score:** Borderline (5.5-6.4 range)
**Estimated best-version score:** Strong Accept (7.5-8.0 range)