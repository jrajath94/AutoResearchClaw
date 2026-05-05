# Review — CRISP: Unifying Grokking and Scaling Laws via Phase Transitions in Feature Space

**Reviewer:** The Big-Picture Editor
**Date:** 2026-05-01

---

## Irreducible Insight (Big-Picture Lens)

The paper's core claim — that grokking and neural scaling laws share a single mechanistic root (a phase transition in feature space from superposition to clean features) — is a genuinely interesting idea. Whether it survives 5 years depends entirely on whether the feature-space phase transition story generalizes beyond (a+b) mod 47. Right now that is an open question, not a resolved one.

---

## Strengths

1. **Unification is real and non-trivial.** The paper does not merely observe that both phenomena involve "learning features." It identifies a specific mathematical structure — the superposition-to-clean transition as a sharp phase boundary — and shows that grokking timing and scaling exponents flow from the same mechanism. Theorem 1 is a genuine contribution to theory. (Section 2, Abstract, Figure 4)

2. **Three falsification tests are built in, not bolted on.** The Schaeffer smoothness criterion, sub-critical extended training (0/51 grokked), and decorrelation test are integrated into the framework. This is rare. Most papers in this space claim their theory is falsifiable but never operationalize what would kill it. The sub-critical result (Section 3.3, Figure 6) is particularly strong evidence for a sharp threshold. (Figures 4-6, Section 3.3)

3. **The β = 2/3 corollary connects to established scaling law literature.** If the scaling exponent for test loss genuinely emerges as 2/3 from the phase transition framework, this bridges two large literatures that rarely talk to each other. The derivation in Section 3.2 and the Corollary is the paper's most exportable claim — it applies beyond grokking if correct. (Section 3.2, Corollary)

4. **Experimental design is thorough for a single task.** 120 runs across 5 widths and 8 fractions, with 3 seeds, 10,000 steps, and a clear grokking criterion (>90% test accuracy). The grok rate heatmap (Figure 2) is the most complete phase diagram I've seen for this phenomenon. (Section 2, Figure 2)

5. **The paper correctly identifies that n_c decreases with width — and doesn't hide it.** The fact that empirical n_c goes 1546→1325→1105→1105→884 as width increases (opposite of Theorem 2's prediction) is prominently discussed. The F_eff(w) reconciliation is a non-trivial theoretical move. The authors deserve credit for not burying the contradiction. (Section 3.1, Figure 3)

---

## Weaknesses

### W1: Theory predicts the wrong direction for n_c vs. width
**Issue:** Theorem 2 states n_c = α·w·log(F), implying n_c ∝ w (increases with width). Empirically, n_c decreases monotonically: 1546 (w=32) → 884 (w=128). This is not a minor discrepancy — it is the opposite direction.
**Where:** Theorem 2 (Section 3.1), Figure 3, Abstract ("n_c decreases with width (opposite of theory prediction)").
**Severity:** 5/5 — This is the paper's most serious scientific problem. The theory makes a clear, directional prediction that is contradicted by data.
**Resolution:** Either (a) Theorem 2 is wrong and needs to be re-derived with corrected assumptions, or (b) the F_eff(w) rescue is made rigorous with a first-principles derivation of why F_eff shrinks with width, not just curve-fitting to explain away the contradiction. The current treatment reads as post-hoc rationalization.

### W2: F_eff(w) is introduced without derivation from underlying principles
**Issue:** The refined formula n_c = α·w·log(F_eff(w)) with F_eff(w) = F·(w/w0)^(-γ) (γ>1) is calibrated against the very data it is meant to explain. There is no mechanical model of *why* effective feature count would shrink with width.
**Where:** Section 3.1, lines addressing the n_c discrepancy.
**Severity:** 4/5 — Without a theory of F_eff, the paper has a curve-fitting story dressed as a mechanism.
**Resolution:** Derive F_eff(w) from the network's optimization dynamics. Why does width *reduce* effective feature count? This should follow from the phase transition physics, not be appended as an experimental footnote.

### W3: Single-task validation (mod-47) is insufficient for a general theory
**Issue:** The entire framework — theorems, phase transition claims, falsification tests, scaling exponents — is validated on a single task. Mod-47 is a well-known grokking benchmark, but it is still one task. The paper's title and abstract heavily imply generality ("Unifying Grokking and Scaling Laws" — plural).
**Where:** Abstract, Section 2 (experimental design), throughout.
**Severity:** 4/5 — The paper makes universal claims about neural network learning dynamics based on one experimental domain. This is a textbook case of "fits the one demo" generalization risk.
**Resolution:** At minimum, demonstrate the phase transition on 2-3 additional tasks (e.g., different moduli, different function classes like parity or compositional tasks). The theorems themselves might be general; the empirical support is not.

### W4: n_eff(t) remains a conjecture — the paper's most dynamic quantity is its least rigorously grounded
**Issue:** n_eff(t) (effective sample size over training) is central to the framework's story about how grokking unfolds temporally, but it is explicitly marked as a conjecture, not derived. The temporal dynamics of the phase transition are thus hand-waved.
**Where:** Section 3 (n_eff(t) conjecture), mentioned in abstract and results.
**Severity:** 3/5 — This is the mechanism's *engine*, and it runs on an unproven conjecture.
**Resolution:** Either prove n_eff(t) formally or clearly demarcate it as empirical curve-fitting with a proposed functional form. Reviewers and readers need to know which parts are theorem-proven, which are conjecture, and which are curve-fits.

### W5: α is calibrated, not derived — the theory's core parameter lacks first-principles grounding
**Issue:** α = (σ_x²/2λ)·(1+γ/(λw))^(-1) involves parameters (σ_x², λ) that are not connected to any measurable network property. It is fitted, not derived.
**Where:** Theorem 2, Section 3.1 (α characterization).
**Severity:** 3/5 — The scaling law's central equation has a free parameter that cannot be independently predicted or tested.
**Resolution:** Either connect α to optimizable/measurable quantities in the network, or acknowledge α as a task-specific calibration constant with limited theoretical reach.

### W6: β = 2/3 is not directly validated
**Issue:** The paper's most potentially impactful corollary — that the neural scaling exponent β → 2/3 for large width — is never directly measured. The scaling exponent emerges from the theory but the paper never fits a scaling law to its own data and checks if β ≈ 2/3.
**Where:** Corollary (Section 3.2), Figure 5 (scaling law plot).
**Severity:** 3/5 — This is the bridge to the scaling laws literature, and it is asserted rather than demonstrated.
**Resolution:** Fit test loss vs. training fraction for each width, extract β, and report whether it approaches 2/3. Even a noisy estimate would be more convincing than zero validation.

### W7: The paper does not engage with alternative explanations of grokking
**Issue:** Grokking has multiple competing theories: (a) late-time lottery ticket emergence, (b) data phase transitions (Power et al.), (c) mutual information compression, (d) spectral mechanisms. The paper cites some but does not systematically argue why the feature-space phase transition account is superior or compatible with these alternatives.
**Where:** Related work / discussion — appears to be missing a dedicated comparison section.
**Severity:** 3/5 — Without positioning against alternatives, the paper cannot establish that its framework is the *right* explanation vs. one among several.
**Resolution:** A dedicated discussion section comparing the feature-space phase transition account to at least 2-3 alternative grokking theories, explaining where they converge, diverge, and whether the empirical results discriminate between them.

### W8: "Grokking criterion" (>90% test accuracy) is arbitrary
**Issue:** The paper uses >90% test accuracy at 10,000 steps as the grokking criterion, but does not justify this threshold or test sensitivity to it. The entire grokking rate heatmap (Figure 2) depends on this cutoff.
**Where:** Section 2 (grokking criterion), Figure 2.
**Severity:** 2/5 — This is a minor methodological concern for a reviewer with my bar, but it matters for reproducibility.
**Resolution:** Ablate over criterion thresholds (e.g., 85%, 90%, 95%) and show the phase diagram is robust. Or justify the 90% threshold theoretically.

### W9: No code or reproducibility materials released
**Issue:** The rubric awards 8/10 for "Code+configs released; data accessible." The paper has no associated GitHub link, no mention of released training seeds, and the prior review notes the code is not publicly available.
**Where:** Reproducibility section (or lack thereof).
**Severity:** 2/5 — The paper explicitly claims reproducibility in the abstract framing but does not walk the walk.
**Resolution:** Release code, configs, training seeds, and the full 120-run dataset. This would be a strong contribution to the community given the cost of these runs.

### W10: The paper is written TO the rubric rather than FROM thinking
**Issue:** The overall structure feels engineered to hit NeurIPS checklist boxes (theorems, falsification tests, figures per rubric dimension) rather than being the natural shape of a compelling scientific narrative. The theorems feel like they were retrofitted to justify empirical observations.
**Where:** Throughout — particularly the "three falsification tests" framing which reads as defensive.
**Severity:** 2/5 — This is a stylistic concern from my perspective, but it is real. The best papers in 5 years will not look like they were assembled from a checklist.
**Resolution:** Let the narrative breathe. The grokking story is interesting enough to stand on its own without being dressed as a NeurIPS submission.

---

## Per-Rubric-Dimension Scores

| Dimension | Score | Calibration Anchor |
|---|---|---|
| **Originality / Novelty** | 6 | Substantial conceptual advance — the unification is real and non-obvious. Not quite paradigm-reorganizing (10) because the empirical grounding is too narrow. Clear improvement over existing grokking theories. |
| **Soundness** | 5 | Heavy concerns: Theorem 2's directional prediction is contradicted by data, F_eff(w) is curve-fitting, n_eff(t) is unproven. Not a rejection (4) because the experimental execution is careful and the falsification tests are genuine. |
| **Significance** | 6 | If the β=2/3 and n_c predictions hold up more broadly, this is an 8. Right now it is a 6 — useful contribution within the grokking/scaling intersection, not yet demonstrated outside it. |
| **Clarity** | 7 | Well-organized, figures are clear, theorems are stated formally. Docked points for the F_eff rescue feeling rushed and for the theorem-proof structure obscuring the underlying intuition. |
| **Reproducibility** | 5 | 120 runs with 3 seeds is described, but no code, no configs, no released data. The description is sufficient to reproduce *in principle* but not in practice. |
| **Contextualization vs prior work** | 6 | Good coverage of grokking literature; adequate on scaling laws. Missing systematic comparison with competing grokking theories (see W7). |
| **Ethical / Broader Impact** | 6 | Standard broader impact statement — not boilerplate, but not memorable either. No specific concerns. |

**Weighted Average:** (6×1.0 + 5×1.5 + 6×1.0 + 7×0.7 + 5×1.0 + 6×0.8 + 6×0.5) / (1.0+1.5+1.0+0.7+1.0+0.8+0.5) = (6 + 7.5 + 6 + 4.9 + 5 + 4.8 + 3) / 7.0 = **37.2 / 7.0 ≈ 5.3**

**Adjusted Soundness Score (post-revision):** I assign a temporary +0.5 to Soundness for the projected-value and α-characterization revisions mentioned in the prior review, recognizing the authors attempted to address concerns. This brings Soundness to 5.5 → weighted average ≈ 5.5.

---

## Pointed Questions

1. **Forget the benchmarks — what is the one sentence that changes a researcher's mental model after reading this paper?** If you cannot write it in one clear sentence for a department lunch, the paper is not ready.

2. **Theorem 2 predicts n_c ∝ w. Your data shows n_c ∝ w^(-0.5). You have introduced F_eff(w) to explain this. Can you write down a single equation, derived from first principles, that predicts n_c(w) without fitting a free parameter to your own data?** If not, you have a post-hoc rationalization, not a theory.

3. **What is the most specific, concrete falsification of the CRISP framework that you have personally considered — not a generic "wrong prediction" but a specific experimental design with specific observable outcomes that would kill the theory?**

4. **You claim grokking corresponds to a phase transition in feature space. Have you directly measured the feature-space representation (e.g., using linear probing, PCA, or SUPIDX) at multiple timepoints during training to show the transition from superposition to clean features? Figure 4 shows supidx dropping — but is this a phase transition or just network convergence?** (Figure 4, Section 3.3)

5. **The β=2/3 corollary is the paper's most exportable claim beyond grokking. Have you fit a scaling law to your own data? What is the measured β across widths? If it is not 2/3, why does the corollary matter?**

6. **You validate on mod-47. What would break your theory if you ran mod-53 or mod-101? What specific prediction would change, and have you designed experiments to check it?**

7. **Your three falsification tests (Schaeffer smoothness, sub-critical extended training, decorrelation) are presented as built-in. Which of these tests is most likely to fail first if the theory is wrong? Which is most likely to be challenged by future work?**

8. **n_eff(t) is described as "empirically testable" but is never actually tested against held-out predictions. Can you state what n_eff(t) predicts for the 10,000-step training curves of a network at f < f_c that you have NOT trained? If not, this is a curve-fit, not a conjecture.**

---

## Falsifiability Test

**What evidence would change my decision?**

*Strong Accept:* A follow-up paper from a different group demonstrates the phase transition mechanism on 3+ tasks (different from mod-47), directly measures feature-space representations over training time, and confirms both n_c(w) behavior and β ≈ 2/3 independently. That follow-up paper would not exist without this one.

*Strong Reject:* A single follow-up experiment on mod-53 (a different modulus) shows n_c *increases* with width (matching Theorem 2's literal prediction) and the phase diagram has no sharp boundary. This would suggest the F_eff(w) rescue is wrong and the phase transition story is specific to mod-47, not a general mechanism. I would also reject if someone demonstrates that the "superposition" signal in supidx (Figure 4) is an artifact of the particular one-hot encoding, not a genuine feature-space phenomenon.

*Borderline outcome:* If a follow-up shows grokking on another task but with a *different* critical exponent (not 2/3), the theory survives in form but the specific corollary fails. That keeps the paper Accept-level — interesting mechanism, wrong details.

---

## Confidence

**4/5**

My confidence is high that the empirical observations are real (120 runs, careful design). My confidence is lower that the theoretical framework is correct as stated — Theorem 2's directional failure and the F_eff(w) rescue are significant red flags. The single-task validation gap is real but not fatal for a theory paper. I would not bet my reputation on the β=2/3 corollary without more validation.

---

## Decision

### **Borderline**

The paper has a real, non-trivial insight (unification of grokking and scaling laws via feature-space phase transitions) that could matter in 5 years. The empirical execution is careful and the falsifiability infrastructure is genuine. However, the theory's most direct prediction (n_c ∝ w) contradicts the data, the rescue mechanism (F_eff(w)) is post-hoc, and the entire framework rests on a single task. The β=2/3 corollary — the paper's most exportable and potentially impactful claim — is never directly validated.

**My recommendation:** Accept at Borderline with mandatory revision requests:
1. Derive F_eff(w) from first principles, not curve-fitting
2. Demonstrate the phase transition on at least 2 additional tasks
3. Measure β from the data (fit the scaling law) and report the value
4. Clearly demarcate which claims are theorem-proven, which are conjecture, and which are fits

If the authors can deliver items 1 and 2 in revision, this becomes a Strong Accept. Right now it is too early to tell.

---

*— The Big-Picture Editor*
