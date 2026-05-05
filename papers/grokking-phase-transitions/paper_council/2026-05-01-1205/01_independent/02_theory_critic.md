# Theory Critic Review — CRISP Paper

**Paper:** CRISP: Unifying Grokking and Scaling Laws via Phase Transitions in Feature Space
**Reviewer:** The Theory Critic
**Date:** 2026-05-01

---

## 1. Strengths

**S1 — Theorem 1 correctly characterizes a bimodal energy landscape.**
The paper establishes that global minima of E(Φ;n) fall into two distinct classes—superposed (S = Θ(1)) and clean (S = O(F⁻²))—with a sharp phase boundary. The proof via gradient conditions and intermediate value theorem is sound for the stated energy functional. This is a genuine contribution to understanding grokking mechanistically.

**S2 — Closed-form n_c (Theorem 2) is a falsifiable prediction.**
The formula n_c = α · w · log(F) makes concrete, testable quantitative predictions about how critical dataset size scales with width and latent feature count. This is more than handwaving—it invites direct experimental refutation. The authors correctly identify three falsification tests (F1, F2, F3), showing methodological awareness.

**S3 — The F2 result (0/51 sub-critical runs grokked) is a striking experimental result.**
If genuine, this provides strong evidence that grokking is governed by a sharp threshold phenomenon, not merely extended training. The claim is specific enough to be checked by any replicator. This is how theory should interface with experiment.

**S4 — Identifying the n_c(w) direction reversal is intellectually honest.**
The naive CRISP prediction is n_c ∝ w (increases with width). The paper observes the opposite. Rather than dismissing this as noise, the authors attempt reconciliation via F_eff(w). This honesty about theory-experiment mismatch strengthens rather than weakens the paper.

**S5 — The connection to scaling law exponent β = 2/3 is a clean corollary.**
If one accepts ν = 1/2 (transition sharpness exponent), the derived β = 1/(1+ν) = 2/3 connects cleanly to established scaling law literature. The corollary is non-trivial and potentially testable against prior Chinchilla-family results.

---

## 2. Weaknesses

**W1 — n_eff(t) is admitted conjecture, but it is load-bearing.**
*Issue:* Theorem 1 proves a static phase transition in the energy landscape as a function of dataset size n. Grokking is a dynamic phenomenon (generalization long after memorization). The connection requires n_eff(t) — the effective dataset utilization growing with training steps — to cross n_c at the right moment. This is explicitly flagged as "conjecture, not formally derived" (Section 3.2, Note).
*Location:* Section 3.2, p.6; Appendix A has no proof of n_eff(t).
*Severity:* 4/5 — Without n_eff(t), Theorem 1 doesn't actually prove grokking is explained by this mechanism.
*Resolution:* Either (a) derive n_eff(t) from the optimization dynamics, or (b) explicitly frame the claim as "a sufficient condition exists" rather than "the mechanism."

**W2 — F_eff(w) is a post-hoc reconciliation with no derivation.**
*Issue:* To explain why n_c decreases with width (opposite of naive prediction), the paper introduces F_eff(w) = F · (w/w₀)^(−γ), γ > 1. This is not derived from any principle — it is introduced specifically to make the theory fit the data.
*Location:* Section 3.3, "Reconciliation," p.10; Conclusion mentions "derive F_eff(w) from first principles" as future work.
*Severity:* 3/5 — This is a hypothesis with one free parameter (γ), but it is not tested independently. It could be curve-fitting.
*Resolution:* Validate F_eff(w) on a different task/architecture, or derive it from the geometry of superposition.

**W3 — α is calibrated at w=256, then used predictively at other widths.**
*Issue:* The paper uses a two-step procedure: (1) calibrate α from w=256 runs, (2) predict n_c at other widths. If α is truly a task-dependent constant (Claim 2, Theorem 2), it should be constant across widths. Calibrating at one width and validating at others is circular.
*Location:* Section 3.3, Note, p.10; Table 3 doesn't show prediction error bars.
*Severity:* 3/5 — The theory's predictive power is undermined if the free parameter is fit to one data point.
*Resolution:* Either estimate α from first principles (the expression (σ²/2λ) · (1 + γ/(λw))⁻¹ suggests this is possible) or use a separate calibration set.

**W4 — Concentration of measure assumptions are not verified at finite width.**
*Issue:* Theorem 1's transition width bound Δn/n_c = O(w^(−ν)) relies on concentration of measure. The paper doesn't verify that the constants hidden in O() are small enough to be meaningful at w=32 (the smallest width). The bound could be exponentially weak in width.
*Location:* Appendix A, Theorem 1 proof; Theorem 2 statement.
*Severity:* 3/5 — A bound of the form O(w^(−ν)) with unknown constants is not falsifiable.
*Resolution:* Provide explicit rate constants or check that the bound is non-vacuous at w=32.

**W5 — Theorem 2 derivation of n_c uses approximations whose regime of validity is unclear.**
*Issue:* The derivation solves ΔE(n_c) = 0 and simplifies to n_c ≈ (γ/(λc)) · w · log(F). The ≈ sign hides corrections of unknown order. The paper does not bound the relative error.
*Location:* Appendix A, Theorem 2 proof, solving ΔE(n_c) = 0 step.
*Severity:* 3/5 — For w=32 and F presumably large, the corrections could be O(1), making the log term unreliable.
*Resolution:* State the relative error bound explicitly or show the approximation is tight for the parameter regime studied.

**W6 — The "sharp" phase boundary in experiments is less sharp than claimed.**
*Issue:* Table 2 shows that for w=32, at f=0.6, the grok rate is 33% (not 0% or 100%). The transition is not a clean 0/1 boundary at smaller widths. This contradicts the "sharp phase transition" framing.
*Location:* Table 2, w=32 row; Section 5, "Sharp 0/1 phase boundary."
*Severity:* 2/5 — The paper claims sharp boundary but the data shows noise/softness at small widths, consistent with the theoretical Δn/n_c → 0 only as w → ∞.
*Resolution:* Qualify the "sharp" claim to "increasingly sharp with width."

**W7 — F1 (Schaeffer smoothness) is insufficiently specific.**
*Issue:* The paper claims that if the apparent transition is a metric artifact, log-loss should show no transition. But the metric is test accuracy — log-loss is not used as the grokking criterion elsewhere. The falsification test compares different outcome variables.
*Location:* Section 4, F1 description; Table 1.
*Severity:* 2/5 — The test doesn't falsify the mechanism, it falsifies a specific artifact hypothesis. The logic is correct but the framing is imprecise.
*Resolution:* State more precisely which metric artifact is being tested and why log-loss is the right discriminator.

**W8 — The superposition index S(Φ) is computed on penultimate-layer activations only.**
*Issue:* The paper measures S via PCA on penultimate-layer activations. Whether this is sufficient to detect superposition in the full network is not established. Superposition could occur in earlier layers while later layers remain unaffected.
*Location:* Appendix B, "superposition index computation."
*Severity:* 2/5 — The measurement protocol may miss the relevant superposition dynamics.
*Resolution:* Check layer-wise PCA decomposition or provide justification for why penultimate layer is representative.

**W9 — β = 2/3 is not compared to established scaling law measurements.**
*Issue:* The paper derives β → 2/3 from the theory, but Kaplan et al. 2020 and follow-ups report different exponents (often ~1/N^1 or broken power laws). The paper doesn't discuss whether 2/3 is consistent with prior empirical findings.
*Location:* Corollary 1; Section 2 (Related Work).
*Severity:* 3/5 — If the predicted exponent contradicts established empirical scaling laws, the corollary is weakened.
*Resolution:* Compare the predicted β = 2/3 against empirical scaling exponents from prior work and discuss any discrepancy.

**W10 — Only 2-layer MLPs tested; generalization to transformers is speculative.**
*Issue:* Section 6 (Limitations) notes only 2-layer MLPs w≤128 are studied. Section 7 (Conclusion) mentions extending to transformers and larger tasks as "future work." But if the phase transition mechanism depends on the geometry of superposition in MLPs, it may not transfer to attention-based architectures.
*Location:* Section 6; Section 7.
*Severity:* 2/5 — The practical significance is limited if the mechanism is architecture-specific.
*Resolution:* Either provide evidence (theoretical or empirical) that the mechanism survives in transformers, or narrow the claims.

---

## 3. Per-Rubric Scores

| Dimension | Score | Calibration Anchor |
|-----------|-------|--------------------|
| 1. Originality / Novelty | 7 | Substantial conceptual advance — phase transition framing unifying grokking and scaling laws is genuinely new. Not SOTA-defining (no new proof technique) but nontrivial. |
| 2. Soundness | 5 | Serious concerns — n_eff(t) is load-bearing but admitted as conjecture; F_eff(w) is post-hoc reconciliation; α calibration is circular across widths. The central theorems do not cover the dynamic phenomenon they purport to explain. |
| 3. Significance | 6 | Important within subfield — grokking is poorly understood; if the mechanism is correct, it would be cited heavily. Practical utility limited by architecture restriction. |
| 4. Clarity | 7 | Clear and well-organized — proofs are in appendix, main text is accessible. Some notation overload in Section 3. |
| 5. Reproducibility | 8 | Code, data, configs, seeds all released. 120 runs, JSON logs. Strong reproducibility. |
| 6. Contextualization vs prior work | 7 | Strong coverage — correctly positions vs Elhage, Schaeffer, Nanda. Some missing: β=2/3 vs Kaplan et al. exponents. |
| 7. Ethical / Broader Impact | 6 | Standard boilerplate impact statement. No specific concerns. |

**Weighted average:** (7×1.0 + 5×1.5 + 6×1.0 + 7×0.7 + 8×1.0 + 7×0.8 + 6×0.5) / (1.0+1.5+1.0+0.7+1.0+0.8+0.5) = (7 + 7.5 + 6 + 4.9 + 8 + 5.6 + 3) / 5.5 = 42 / 5.5 ≈ **7.64**

---

## 4. Pointed Questions for the Authors

**Q1 — In Appendix A, Theorem 1, the proof uses concentration of measure to bound the transition width. What is the explicit dependence on width in the concentration inequality? Specifically, does the bound remain non-vacuous for w=32 at the sample sizes studied (n ≤ 2209)?**

**Q2 — Theorem 2 derives n_c by solving ΔE(n_c) = 0. What is the relative error of the approximation n_c ≈ (γ/(λc)) · w · log(F) for the parameter regime in the experiments? Can you provide a bound on |n_c(true) − n_c(approx)| / n_c(true)?**

**Q3 — n_eff(t) is central to the paper's claim that grokking = phase transition. Has any derivation been attempted? Is n_eff(t) monotonically increasing in training steps under AdamW? If so, from what principle does this follow?**

**Q4 — F_eff(w) = F · (w/w₀)^(−γ) with γ > 1 has one free parameter. How does γ depend on the task architecture? Can you predict n_c for a different task (e.g., mod-43 instead of mod-47) using the same γ? Or is γ re-fitted?**

**Q5 — In the F3 decorrelation test, what is the exact PCA procedure? The paper says "penultimate-layer activations" but superposition could occur in earlier layers. Did the authors check layer-wise decorrelation? If not, why is penultimate layer sufficient?**

**Q6 — Table 2 shows that at w=32, f=0.6, grok rate is 33%, not 0% or 100%. This contradicts the "sharp 0/1 phase boundary" claim. How does this soften affect the theoretical prediction that the transition sharpens with width? Is this consistent with the Δn/n_c = O(w^(−ν)) bound?**

**Q7 — The paper claims β = 2/3 is a corollary, but standard neural scaling laws (Kaplan et al. 2020) report exponents around −0.076 per log parameter, not 2/3. Are these the same β? The paper conflates the dataset-size scaling exponent with the width-scaling exponent. Clarify.**

**Q8 — α is calibrated at w=256, then n_c is "predicted" at other widths. If α is truly constant across widths, the correct procedure is to estimate α from first principles (the expression contains σ², λ, γ which are estimable) or from a separate calibration set. Why was w=256 used as the only calibration point?**

---

## 5. Falsifiability Test

**What evidence would change my decision from Borderline/Accept to Reject?**

The paper sits at the boundary of Accept/Borderline. My assessment hinges on one core question: Is the phase transition mechanism in Theorem 1 actually responsible for grokking, or is it a coincidental correlate?

**Evidence that would trigger Reject:**

- *A single counterexample run where n < n_c but the model generalizes* — this would directly falsify the claim that n_c is the critical threshold. The F2 result (0/51 sub-critical runs) is currently the paper's strongest evidence; one exception would be fatal.

- *Measurement of n_eff(t) showing it does not cross n_c at the grokking step* — if n_eff(t) is measured (e.g., via gradient norms or effective rank) and it does not correlate with the generalization timing, the conjecture collapses.

- *Independent validation of F_eff(w) failing* — if F_eff(w) predicts n_c on a different task (e.g., CIFAR-10 classification or a different modular operation) and misses significantly, the reconciliation is curve-fitting.

- *Superposition index S(Φ) not dropping at grokking onset in a properly controlled run* — the F3 test is the cleanest mechanistic prediction: if S doesn't drop when generalization emerges, the mechanism is falsified.

**Evidence that would strengthen the paper toward Accept:**

- *Formal derivation of n_eff(t)* — even a heuristic derivation with experimental validation would remove the main conjecture flag.

- *Independent prediction of n_c on a held-out task* — using α estimated from mod-47 to predict grokking threshold on mod-43, with successful prediction, would eliminate the circularity concern.

- *Layer-wise PCA showing superposition clears in all layers simultaneously* — confirming the penultimate layer measurement is representative.

---

## 6. Confidence

**4/5** — I am confident in the assessment that the paper's core insight (phase transition in feature space) is real and the static theorem is correctly proved. I am less confident that n_eff(t) connects properly to the dynamics of grokking, and that F_eff(w) is more than post-hoc fitting. The experimental results are solid (120 runs, three seeds, three falsification tests). The theoretical framework has promise but requires further derivation to be fully persuasive.

---

## 7. Decision

**Borderline / Accept (leaning toward Accept)**

**Rationale:** The paper has genuine theoretical substance (a theorem, a closed-form prediction, three falsification tests) and executed experiments (120 runs, sharp phase boundaries). The main weakness — n_eff(t) as conjecture — is honestly flagged. The F_eff(w) reconciliation is post-hoc but the authors acknowledge it. Given NeurIPS's "intellectually generous" standard, the contributions are sufficient to accept if the authors can convincingly address the circularity in α calibration and provide at least a heuristic derivation of n_eff(t). If the reviewers press on the n_eff(t) gap, the paper should be accepted with "accept contingent on addressing Soundness concerns in Appendix."

---

— The Theory Critic
