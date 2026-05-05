# Theory Critic Review — CRISP: Unifying Grokking and Scaling Laws

**Paper**: CRISP: Unifying Grokking and Scaling Laws via Phase Transitions in Feature Space
**Reviewer**: The Theory Critic
**Date**: 2026-05-01

---

## Summary

CRISP proposes a phase transition framework unifying grokking and neural scaling laws. The paper's core theoretical contribution — a formula for critical dataset size n_c = α·w·log(F) — predicts n_c ∝ w (increases with width), yet the empirical data shows n_c decreases with width. The reconciliation via F_eff(w) is post-hoc curve-fitting that reads more like parameter salvage than derivation. The formal theorems exist but their assumptions are either unrealizable or unstated. This is a theoretically interesting framework with significant foundational issues.

---

## Strengths

1. **Theorem 1 (phase transition existence) — Appendix A proof structure**
   The paper correctly identifies that grokking involves a sharp 0/1 phase boundary rather than gradual generalization, and Theorem 1 provides a formal existence proof. The 0/51 sub-critical grokking runs (Section 3) offer genuine empirical support for a crisp threshold. This is a meaningful conceptual contribution.

2. **Sharp experimental design with 120 runs across 5 widths and 8 fractions**
   The grokking criterion (>90% test accuracy by step 10,000) is explicit and verifiable. The phase diagram (Figure 2) clearly shows the 0/1 boundary structure. 3 seeds per condition is minimal but acceptable for physics-style phase transition experiments.

3. **Three built-in falsification tests ( Schaeffer smoothness, sub-critical extended training, decorrelation)**
   This is rare and commendable. The Schaeffer test in particular tests whether the phase transition is artifacts of the modular arithmetic structure, directly engaging the most plausible alternative explanation.

4. **Grokking delay decreases with width — correctly attributed**
   Section 3 finding that grokking delay drops from 4000→667 steps (w=32→96) is real and important. The paper correctly does not overclaim this as support for any particular theory.

5. **Explicit statement that n_eff(t) is a conjecture, not a theorem**
   The paper honestly marks this as "empirically testable" rather than proved. This is intellectually honest and I respect it.

---

## Weaknesses

### W1: Theorem 2 prediction is contradicted by data — F_eff(w) is post-hoc curve-fitting
- **Issue**: Theorem 2 predicts n_c ∝ w (increases with width). Observed n_c: w=32→1546, w=48→1325, w=64→1105, w=96→1105, w=128→884 — a monotonically decreasing sequence.
- **Where**: Section 3, Figure 3, Theorem 2
- **Severity**: 5/5 — this is the paper's central quantitative prediction, and it goes the wrong direction.
- **Resolution**: Either (a) derive F_eff(w) from first principles rather than positing it to fit the data, or (b) acknowledge that the theory is qualitatively correct (phase transition exists) but quantitatively wrong for finite widths, and focus the paper on the qualitative contribution.

### W2: F_eff(w) = F·(w/w0)^(-γ) has unconstrained free parameters with no independent measurement
- **Issue**: The "effective feature count" is introduced to explain the n_c direction reversal, but F_eff(w) is defined by this equation and γ is fit to the same data used to test the theory. No independent measurement or derivation of γ is provided.
- **Where**: Section 3, Equation n_c = α·w·log(F_eff(w))
- **Severity**: 4/5 — this transforms the theory from falsifiable to unfalsifiable within the same dataset.
- **Resolution**: Either (a) derive F_eff(w) from the network architecture and training dynamics, or (b) measure F_eff independently via probe networks or feature attribution methods.

### W3: n_eff(t) conjecture used to support key claims without formal derivation
- **Issue**: The paper states n_eff(t) is "not formally proven; marked as empirically testable." Yet n_eff(t) is used in the scaling law analysis and Figure 5's test loss vs training fraction fit.
- **Where**: Section 2.2, Figure 5
- **Severity**: 3/5 — the paper acknowledges the limitation, but the conjecture is load-bearing for the main scaling law result.
- **Resolution**: Either prove n_eff(t) formally or present it as a hypothesis to be tested, removing it from the core theory chain until validated.

### W4: α = (σ_x²/2λ)·(1+γ/(λw))^(-1) is calibrated, not derived from first principles
- **Issue**: α contains σ_x² (input variance) and λ (a regularization parameter). These are not derived from the theory but fit per-task. The formula cannot predict n_c for a new task without calibration.
- **Where**: Theorem 2, Section 3 calibration discussion
- **Severity**: 3/5 — limits the theory's predictive power to the observed task only.
- **Resolution**: Either derive α from fundamental quantities (learning rate, batch size, network initialization) or clearly state the theory is calibration-dependent and demonstrate cross-task transfer.

### W5: Single task (mod-47) limits all generalization claims
- **Issue**: Every claim — Theorem 1, Theorem 2, the scaling law, F_eff(w) — is tested on one modular arithmetic task. Modular arithmetic has special structure (discrete operations, Fourier-like features) that may not generalize to image classification, language modeling, or other domains.
- **Where**: Section 2.1 (experimental design)
- **Severity**: 4/5 — the paper's title implies a general theory ("Unifying Grokking and Scaling Laws"), but all evidence is from a single task.
- **Resolution**: Test on at least 2-3 diverse tasks (e.g., one permutation tasks, one image task) before claiming generality.

### W6: β = 2/3 prediction (Corollary) is never directly validated
- **Issue**: The paper derives β = 1/(1+ν) → 2/3 as a corollary, but I see no direct measurement of β in the results. The scaling exponent appears in the theory but not as a tested prediction.
- **Where**: Corollary, Section 3 (scaling exponent discussion)
- **Severity**: 3/5 — a derived prediction that is presented but not tested.
- **Resolution**: Measure β independently by fitting the scaling law across widths and comparing to the predicted 2/3 value.

### W7: Theorem assumptions not surfaced — I cannot verify they hold for MLPs on mod-47
- **Issue**: Appendix A presumably contains the proof of Theorem 1, but the paper does not state the assumptions. For a theory critic, this is critical: does the proof require convexity? Lipschitz continuity? Infinite width? All of the above are violated by 2-layer ReLU MLPs.
- **Where**: Appendix A, Theorem 1
- **Severity**: 4/5 — a theorem is only as good as its assumptions. I cannot evaluate validity without the assumptions.
- **Resolution**: Add an explicit "Assumptions of Theorem 1" section in the main text, with a discussion of which hold for the experimental setting.

### W8: Grokking criterion (>90% by step 10,000) may conflate different phenomena
- **Issue**: The >90% threshold is chosen without justification. Does a network that reaches 89% at step 10,000 not "grok"? The criterion gates whether a run counts as grokking and therefore affects n_c measurement. Small changes in the threshold could shift the phase boundary substantially.
- **Where**: Section 2.1, grokking criterion
- **Severity**: 2/5 — a concern but not fatal; the paper should at minimum show robustness to this choice.
- **Resolution**: Report n_c for multiple thresholds (85%, 90%, 95%) to show the phase boundary is not an artifact of the cutoff.

### W9: ν→1/2 asymptotics claimed but only verified at widths {32,48,64,96,128}
- **Issue**: The paper claims Δn/n_c ∝ w^(-ν) with ν→1/2 as w→∞. But widths up to 128 are far from the asymptotic regime. No formal justification for why width 128 is sufficient for asymptotics.
- **Where**: Section 2 (phase transition sharpening)
- **Severity**: 3/5 — asymptotic claims require either proof of convergence rate or widths much larger than those tested.
- **Resolution**: Either provide a convergence rate bound or test widths up to 512 or 1024.

### W10: n_eff(t) and F_eff(w) conflated in the theoretical narrative
- **Issue**: n_eff(t) is about effective sample size during training dynamics; F_eff(w) is about effective feature count as a function of width. These are distinct quantities with distinct derivations, yet the paper's narrative sometimes treats them as the same concept or implies one explains the other.
- **Where**: Sections 2.2 and 3, the "Refined formula" paragraph
- **Severity**: 2/5 — clarity issue, but the conceptual conflation could mislead readers about what the theory actually predicts.
- **Resolution**: Add a glossary distinguishing n_eff(t), F_eff(w), and F (theoretical feature count) explicitly.

---

## Rubric Dimension Scores

| Dimension | Score | Calibration Anchor |
|-----------|-------|-------------------|
| Originality / Novelty | 7 | Substantial conceptual advance — phase transition framing of grokking is genuinely new. Docked for the reconciliation-via-curve-fitting problem. |
| Soundness | 5 | Serious gaps — Theorem 2's central prediction goes the wrong direction. F_eff(w) post-hoc. n_eff(t) is conjecture. Assumptions unstated. Methodology for measuring F_eff is absent. |
| Significance | 6 | Important within the grokking subfield. The unification with scaling laws is compelling but limited to one task. Would be cited by grokking researchers. |
| Clarity | 6 | Mostly clear. Main theoretical claims are stated. But assumptions of theorems missing from main text; readers must consult Appendix A. n_eff/F_eff distinction confusing. |
| Reproducibility | 6 | 120 runs, 3 seeds, code presumably released. But F_eff fitting procedure is underspecified — how exactly is γ fit? |
| Contextualization | 5 | Adequate coverage of grokking literature. Schaeffer test is good. But the relationship to other phase transition theories in physics/melting is not discussed. |
| Ethical / Broader Impact | 6 | Standard NeurIPS boilerplate. Not thoughtful or specific to this work, but not concerning either. |

**Weighted Average: (7×1.0 + 5×1.5 + 6×1.0 + 6×0.7 + 6×1.0 + 5×0.8 + 6×0.5) / 6.5 = 43.5 / 6.5 ≈ 6.69**

---

## Pointed Questions for the Authors

1. **In Lemma 3, step 4 uses a union bound over training iterates — is the independence assumption justified for SGD?** SGD iterates are Markov chains, not independent draws. What correction factor or mixing time assumption is required?

2. **Theorem 1 assumes phase transition exists for the specific loss landscape of mod-47. What prevents the observed sharp boundary from being an artifact of the discrete modular structure?** The Schaeffer test addresses this but does not prove it away — what does Theorem 1 actually prove given a continuous loss surface with discrete data?

3. **How is γ in F_eff(w) = F·(w/w0)^(-γ) actually measured?** If γ is fit to the same n_c(w) data that Theorem 2 is tested against, the theory is unfalsifiable by construction. Please specify the fitting procedure and its degrees of freedom.

4. **Theorem 2's derivation of α = (σ_x²/2λ)·(1+γ/(λw))^(-1) uses what assumptions about the optimization dynamics?** AdamW with lr=0.03 and weight_decay=0.3 does not appear in the formula. Is the theory trained with gradient descent in the limit of infinite training steps, or does it account for the actual optimizer?

5. **Figure 5's scaling law fit uses n_eff(t) as input — since n_eff(t) is a conjecture, how much does the scaling law result depend on n_eff(t) being correctly specified?** If n_eff(t) is wrong by a constant factor, does the β exponent change?

6. **The grokking criterion requires >90% test accuracy by step 10,000. What happens to n_c if the criterion is >85% or >95%?** If n_c changes substantially, the phase boundary is threshold-dependent rather than a sharp property of the learning dynamics.

7. **How does Theorem 2's n_c ∝ w prediction fail so dramatically (decreasing vs increasing) at widths 32-128?** Is there a crossing width w* where the direction should reverse? If so, where is it and why isn't it observed?

8. **The paper claims grokking is "superposition→clean-feature" but provides no direct measurement of superposition (e.g., representation sparsity, probe accuracy for polysemantic features).** What is the evidence that superposition is actually present and then resolved?

---

## Falsifiability Test

**What evidence would change my decision?**

- **Theorem 2 falsification**: If n_c were measured for width {256, 512, 1024} and still decreased, F_eff(w) would need a first-principles derivation, not just curve-fitting. If n_c increased with width at some width > 128, Theorem 2 would be partially vindicated and F_eff(w) would need to explain why the direction reverses.

- **n_eff(t) falsification**: If a controlled experiment (e.g., with a known target n_eff(t) from a teacher-student setup) showed n_eff(t) does not track actual learning dynamics, the scaling law analysis in Figure 5 would need revision.

- **F_eff(w) falsification**: If probe networks trained to measure feature quality showed F_eff(w) does NOT follow the (w/w0)^(-γ) form, the refined formula is curve-fitting, not theory.

- **β = 2/3 falsification**: If scaling exponent β were measured directly and found to be ≠ 2/3 (e.g., β ≈ 0.5 or β ≈ 1.0), the Corollary collapses and the asymptotic theory needs revision.

- **Generalization falsification**: If the same phase transition structure and n_c formula were tested on a non-modular task (e.g., permutation parity, image classification) and n_c showed the same behavior, the theory would be general. If it failed, all generality claims dissolve.

**The paper's current status**: Falsifiable in principle (the three tests are good), but F_eff(w) rescue is too flexible. A truly falsifiable theory cannot add free parameters to explain away every contradiction.

---

## Confidence

**3/5** — I am confident in the weaknesses I identified (especially W1-W4, W7). I am less confident in the severity assessment because I have not seen Appendix A's proof details, which could either validate or invalidate many of my concerns. I would need to read the full proofs before a final decision.

---

## Decision

**Borderline (5.5-6.5)** — leaning toward Accept

**Reasoning**: The paper makes a genuine conceptual contribution — the phase transition framing of grokking is important and the 0/1 boundary is real. The built-in falsification tests are a best-practice I want to reward. However, the central quantitative prediction of Theorem 2 is wrong in direction, and the "fix" (F_eff) is post-hoc. This is not yet a publishable theory; it is a promising empirical framework that needs theoretical grounding.

**Path to Accept**: Derive F_eff(w) from first principles (not curve-fitting); state Theorem 1's assumptions explicitly in the main text; validate β = 2/3 independently; test on one additional task.

**Why not Strong Accept**: The F_eff(w) issue is fatal for the theory's credibility. A theory that predicts the wrong sign for its main quantitative result, and is then rescued by a post-hoc free parameter, is not a proven theory.

**Why not Reject**: The empirical findings (sharp phase boundary, 0/51 sub-critical failures, n_c decreasing) are real and valuable regardless of the current theory's state. The phase transition framing will influence the field's thinking about grokking. The paper is worth publishing as an empirical contribution with a speculative theory.

— The Theory Critic
