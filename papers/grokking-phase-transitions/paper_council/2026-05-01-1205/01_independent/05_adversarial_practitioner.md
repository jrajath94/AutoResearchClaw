# Adversarial Practitioner Review — CRISP Paper

**Paper:** CRISP: Unifying Grokking and Scaling Laws via Phase Transitions in Feature Space
**Reviewer:** The Adversarial Practitioner
**Date:** 2026-05-01

---

## Per-Rubric Scores

| Dimension | Score | Calibration Anchor |
|-----------|-------|-------------------|
| Originality / Novelty | 7 | Substantial conceptual advance; the superposition→clean framing connecting grokking and scaling laws is genuinely novel. However, Elhage et al. 2022 toy models are foundational — this is extension, not new paradigm. |
| Soundness | 5 | **Rejection trigger.** Theory is elegant but (a) n_eff(t) is a conjecture not a derivation, (b) F_eff(w) is post-hoc rationalization of a wrong prediction, (c) the single task (mod-47) leaves huge generalization risk. Methodology gaps are fatal for a theory paper. |
| Significance | 6 | If correct, would be important within the theoretical ML subfield. Limited utility as-is — needs confirmation on non-toy tasks andarchitectures beyond 2-layer MLPs. |
| Clarity | 8 | Well-organized, proofs are readable, figures are clear. The phased diagram (Fig 2) is particularly effective. |
| Reproducibility | 7 | Code and reproduce.py released. Hyperparams fully specified. 3 seeds is minimal but acceptable. Sufficient to verify the core phenomenon. |
| Contextualization vs Prior Work | 7 | Good coverage of grokking literature and scaling laws. Missing: broader phase transition literature in statistical physics (e.g., mean field theory of learning). Some connections to physics community work (Saxe et al. 2014, Goldt et al. 2020) cited correctly. |
| Ethical / Broader Impact | 6 | Standard boilerplate. No specific safety/robustness discussion relevant to production deployment. |

**Weighted Average:** (7×1.0 + 5×1.5 + 6×1.0 + 8×0.7 + 7×1.0 + 7×0.8 + 6×0.5) / 5.5 = **6.14**

---

## 3-5 Strengths (Grounded in Specific Claims)

1. **Sharp Phase Boundary Observation (Fig 2, Table 2):** The 0/1 crispness of the grokking boundary — 0% at f=0.3, 100% at f=0.4 for w=128 — is striking and provides compelling empirical evidence that this is a true phase transition, not a smooth crossover. This kind of sharp threshold behavior is exactly what you look for in production systems to know when a system will generalize vs memorizes.

2. **Three Falsification Tests (Section 4, F1-F3):** The authors built in Schaeffer smoothness test (F1), sub-critical block (F2), and feature decorrelation (F3) as first-class experimental components. F2's result — 0/51 sub-critical runs grokked after extended training — is the kind of evidence that makes a production engineer trust a theory. This is how you build confidence: show that your theory survives attempts to falsify it.

3. **Closed-Form Critical Dataset Size (Theorem 2):** n_c = α·w·log(F) gives actionable predictions. In production, knowing the critical data threshold lets you size your training set efficiently. The connection to scaling law exponent β = 2/3 is a clean theoretical bridge between grokking and scaling laws.

4. **Grokking Delay Scaling (Table 4):** The finding that delays decrease with both data and width is practically useful — it tells you that wider models will generalize faster, which is actionable for training pipeline design. 43% data reduction from 32→128 width (Fig 3) is a concrete efficiency win.

5. **Superposition Index Measurement (Appendix B, Fig 4):** Direct measurement of S(t) during training and showing it drops at the same n_c where grokking occurs (F3 requires r>0.8 correlation) is methodologically sound. This is exactly the kind of mechanistic linking that makes a theory trustworthy rather than just curve-fitting.

---

## 5-10 Weaknesses

### W1: Single Toy Task Validation
- **Issue:** All 120 runs are on (a+b) mod 47, a single modular arithmetic task. Production ML systems encounter diverse task distributions. The theory claims general mechanistic validity but is validated on one synthetic task.
- **Where:** Section 4 (Experimental Design), Table 2 — all conditions use mod-47.
- **Severity:** 5/5 — This is the fundamental limitation. A theory that works on mod-47 but fails on real tasks is not useful. The authors acknowledge this in Section 6 ("only 2-layer MLPs w≤128") but do not address the task diversity gap.
- **Resolution:** Validate on at minimum: (a) different modular primes (mod-23, mod-97), (b) other grokking tasks (permuted pixel patterns, PrimePath), (c) different function classes beyond addition mod N.

### W2: n_eff(t) is a Conjecture, Not a Derivation
- **Issue:** The core mechanistic link — that effective dataset utilization increases with training steps and crosses n_c — is asserted as a conjecture (Section 3.2, Note). Without a formal derivation, this is a just-so story.
- **Where:** Section 3.2, Note: "n_eff(t) is presented as a conjecture, not formally derived."
- **Severity:** 4/5 — The qualitative behavior is plausible, but the quantitative predictions depend on this. If n_eff(t) doesn't actually track n_c the way the theory assumes, the whole grokking mechanism collapses.
- **Resolution:** Derive n_eff(t) from first principles or provide an information-theoretic bound on its growth rate with training steps.

### W3: Post-Hoc F_eff(w) Rescue of Wrong Direction Prediction
- **Issue:** Theorem 2 predicts n_c ∝ w (increases with width), but Table 3 shows n_c DECREASES with width. The paper introduces F_eff(w) = F·(w/w₀)^(−γ), γ>1 as a "reconciliation." This is reverse-engineering, not theory.
- **Where:** Section 3.3, Table 3 — the key finding is that n_c decreases with width, opposite of naive prediction.
- **Severity:** 4/5 — The theory made a wrong prediction and patched it. While the refinement is plausible, it has no independent validation. Production track record: theories that require post-hoc parameter fitting to match data have poor out-of-sample performance.
- **Resolution:** Predict F_eff(w) from first principles OR show that F_eff(w) calibration at one width successfully predicts n_c at other widths without re-calibration.

### W4: α Calibrated Per Task Family
- **Issue:** α = (σ²/2λ)·(1+γ/(λw))⁻¹ is described as task-dependent. In production, you rarely know the task family in advance. The theory cannot make absolute predictions for novel tasks.
- **Where:** Section 3.3: "α is calibrated empirically at w=256, then used to predict n_c at other widths." Section 6 Limitations: "α calibrated per task family."
- **Severity:** 3/5 — This is a significant practical limitation. Without a task-agnostic way to estimate α, the theory's predictive power is limited to tasks similar to mod-47.
- **Resolution:** Establish bounds on α across task families, or show that α depends on measurable task properties (e.g., function class complexity, input dimensionality).

### W5: 2-Layer MLPs Only — No Transformers or Attention
- **Issue:** All experiments use 2-layer MLPs with width ≤128. Modern production systems are dominated by transformers with attention layers, layernorm, residual connections. Superposition dynamics in transformers may be fundamentally different.
- **Where:** Section 4 (Experimental Design): "Architectures: 2-layer MLP, one-hot encoding." Section 6 Limitations: "only 2-layer MLPs w≤128."
- **Severity:** 5/5 — This is a production viability killer. The paper's future work explicitly mentions "extend to transformers." Until this is done, the theory is incomplete.
- **Resolution:** Validate on small transformers (e.g., 2-layer, 4-head attention) on the same mod-47 task.

### W6: 10,000 Step Training Horizon — Sub-Critical "Proof" May Be Time-Bounded
- **Issue:** F2 claims 0/51 sub-critical runs grokked as evidence that sub-critical models never generalize. But maximum training is 10,000 steps. What if grokking delay exceeds this horizon?
- **Where:** Section 4, F2: "51 sub-critical runs." Appendix B: "10,000 steps."
- **Severity:** 3/5 — The paper shows delay decreases with data and width (Table 4). At sub-critical data fractions, delays are longest. It's plausible delays simply exceed the training horizon, not that they're truly blocked forever.
- **Resolution:** Run extended training (50,000+ steps) on at least a subset of sub-critical runs to establish that the block is permanent, not just horizon-limited.

### W7: Only 3 Seeds — Extreme Outcomes Possible in Production
- **Issue:** With 3 seeds per condition (42, 137, 256), the variance estimate is extremely noisy. In production with millions of runs, rare seeds with anomalous behavior dominate failure modes.
- **Where:** Section 4: "3 seeds per condition." Table 4 delay values have high variance.
- **Severity:** 3/5 — p99 failure is what matters in production. 3 seeds gives no visibility into the tail.
- **Resolution:** Minimum 10 seeds, ideally 30, for variance estimation. Report not just means but percentiles.

### W8: Sub-Gaussian Assumption — Unverified
- **Issue:** Theorem proofs rely on sub-Gaussian feature assumptions (Section 6, Appendix A). In practice, neural network activations can have heavy tails, especially at large width. If this assumption is violated, concentration-of-measure arguments in Appendix A fail.
- **Where:** Appendix A: concentration of measure arguments. Section 6: "sub-Gaussian assumption."
- **Severity:** 3/5 — This is a theoretical vulnerability. Heavy-tailed activations would smooth out the predicted sharp phase transition.
- **Resolution:** Verify activation distributions empirically across widths. Show sub-Gaussian or bounded moment conditions hold for mod-47 trained networks.

### W9: No Discussion of Inference-Time Generalization
- **Issue:** The paper studies training dynamics but says nothing about whether the "clean feature" phase generalizes at inference time under distribution shift. In production, models face covariate shift, label noise, and adversarial inputs.
- **Where:** Entire paper focuses on training-time phase transition. No inference robustness analysis.
- **Severity:** 3/5 — For production deployment, training-time generalization is necessary but not sufficient.
- **Resolution:** Test generalization under distribution shift (e.g., mod-47 with different primes at test time).

---

## Pointed Questions for Authors

1. **n_eff(t) Conjecture:** You state n_eff(t) (effective dataset utilization) increases with training steps, and crossing n_c triggers the phase transition. This is the mechanistic heart of the theory. What information-theoretic bound governs its growth? Without this, grokking remains a just-so story. Have you tried deriving n_eff(t) from PAC-Bayes or MDL principles?

2. **F_eff(w) Reverse Engineering:** Theorem 2 predicts n_c ∝ w. Your experiments show n_c decreases with w. You introduce F_eff(w) = F·(w/w₀)^(−γ) to reconcile. Is there ANY first-principles derivation of F_eff(w), or is it a free parameter fitted to save the theory? If the latter, this is curve-fitting, not theory.

3. **Training Horizon Effect on F2:** 0/51 sub-critical runs grokked at 10,000 steps — but grokking delays at sub-critical fractions are 8,333 steps (Table 4). What happens at 20,000 steps? 50,000 steps? The block could be horizon-bounded, not permanent. Please run extended training on at least 5 sub-critical runs to distinguish "never" from "not yet."

4. **Transformer Validation:** Your future work explicitly mentions extending to transformers. Given that all production language models are transformers, why is this not in scope for the current paper? The 2-layer MLP limitation severely limits practical relevance. What preliminary experiments do you have on attention-based architectures?

5. **α Task-Dependence in Practice:** How would a practitioner estimate α for a novel task? If α must be calibrated per task family, the theory cannot make absolute predictions for new domains. Is there any correlation between α and measurable task properties (e.g., function output diversity, input entropy)?

---

## Falsifiability Test

**"What evidence would change my decision?"**

For **Strong Accept**, I need:
- Validation on at least 3 diverse tasks (different function classes, not just different mod-N primes)
- Extension to small transformers (2-layer, 4-head) showing same phase transition mechanism
- Extended training (50,000 steps) on 10+ sub-critical runs confirming permanent block
- Formal derivation of n_eff(t) or at minimum an information-theoretic bound on its growth
- Predictive (not post-hoc) validation of F_eff(w) — calibrate at w=32, predict w=128

For **Accept**, I need:
- Same mod-47 task but with 10+ seeds showing same qualitative behavior
- Acknowledgment that current theory is for 2-layer MLPs on synthetic tasks only

For **Borderline**, current state is acceptable if:
- Paper reframes as "theory and validation in 2-layer MLPs" with clear scope bounds
- Future work section is expanded with concrete transformer plans

For **Reject**: Current state already triggers my soundness concern (5/10 — serious methodology gaps).

**My bar for production viability:**
A theory paper earns Accept for production relevance when it can make actionable predictions for unseen tasks and architectures. CRISP cannot yet do this — it predicts n_c direction wrong for the very setting it was derived on (width scaling), uses a conjecture for its core mechanism, and is validated exclusively on a single synthetic task with limited architecture class.

---

## Confidence

**3/5** — I find the core insight (phase transition from superposition to clean features as the mechanism unifying grokking and scaling laws) compelling and likely correct in spirit. However, the execution has significant gaps that prevent me from endorsing this as a production-ready theory. The theory is elegant but the empirical grounding is too narrow and the wrong-direction prediction patching undermines confidence.

---

## Decision: **Borderline**

**Weighted average 6.14** places this in the Borderline zone (5.5-6.5). The core strengths — sharp phase boundary, falsification tests, closed-form predictions — are real. But W1 (single task), W2 (n_eff conjecture), W3 (post-hoc F_eff), and W5 (MLP-only) are serious gaps for a theory paper.

**Bottom line:** This is a promising theoretical framework that needs broader empirical validation before it can guide production systems. The authors should either (a) expand to multiple tasks and transformer architectures, or (b) clearly scope the paper as "theory and validation for 2-layer MLPs on modular arithmetic" which would lower significance but improve honesty about scope.

---

*— The Adversarial Practitioner*
