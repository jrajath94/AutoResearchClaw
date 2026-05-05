# Naive Reader Review — CRISP: Unifying Grokking and Scaling Laws

**Paper:** CRISP: Unifying Grokking and Scaling Laws via Phase Transitions in Feature Space
**Reviewer:** The Naive Reader (1st-year PhD student)
**Date:** 2026-05-01

---

## STRENGTHS

1. **The central insight is genuinely educational.** The paper's core claim — that grokking and neural scaling laws share a mechanism (superposition→clean-feature phase transition) — is explained with enough motivation in Section 1 to make a naive reader curious. I wanted to keep reading.

2. **Theorem 1 gives a concrete anchor.** Having a formal statement of the phase transition existence (Theorem 1, with proof in Appendix A) gives me something to grip. Even though I can't verify the proof, the structure (preconditions → conclusion) is familiar from coursework and helps me trust the framework.

3. **Falsification tests are clearly advertised.** Section 4 lists three concrete tests (Schaeffer smoothness, sub-critical extended training, decorrelation). As a naive reader, I appreciate that the authors pre-committed to what would falsify their theory. This is good scientific practice.

4. **Experimental design is transparent.** Table of hyper-parameters, seed choices, grokking criterion (>90% test accuracy), and the 120-run breakdown (69 grokking, 51 sub-critical) are all stated upfront. I can mentally trace the pipeline.

5. **Figure 2 (phase diagram heatmap) is the best teaching tool in the paper.** Seeing grokking rate as a function of width and data fraction visually delivers the "sharp 0/1 phase boundary" claim better than any equation could.

---

## WEAKNESSES

### W1: The central theory predicts the WRONG direction of the width effect
- **Issue:** Theorem 2 predicts n_c ∝ w (increases with width). But empirically, n_c *decreases* with width (Section 3, Figure 3: w=32→1546, w=128→884). This is not a minor discrepancy — it's directionally opposite.
- **Where:** Section 3, Results; Figure 3; reconciled in Section 3.1 via F_eff(w)
- **Severity:** 5/5 (this is the paper's main empirical contribution and it directly contradicts the theory)
- **Resolution:** The paper introduces F_eff(w) = F·(w/w0)^(-γ), γ>1 as a rescue hypothesis. But: (a) w0 is never defined or fitted, (b) γ is not reported for mod-47, (c) the functional form of F_eff is asserted, not derived. A naive reader cannot verify this reconciliation.

### W2: λ in Theorem 2 is never defined
- **Issue:** Theorem 2 states n_c = α·w·log(F) where α = (σ_x²/2λ)·(1+γ/(λw))^(-1). λ appears without definition.
- **Where:** Theorem 2, Section 2
- **Severity:** 4/5 — without λ, I cannot compute α or verify the log dependence on F
- **Resolution:** Define λ in the main text or appendix. Is it a regularization coefficient? A eigenvalue? Give units and typical values.

### W3: supidx appears in Figure 4 without introduction
- **Issue:** Figure 4 caption uses "supidx" — I have no idea what this measures. Is it a superposition norm? An index? A dimension?
- **Where:** Figure 4, Section 3 (Superposition dynamics)
- **Severity:** 3/5 — I can't evaluate Figure 4's contribution to the argument
- **Resolution:** Define supidx in Section 2 or the figure caption. A one-sentence definition would suffice.

### W4: n_eff(t) is called a "conjecture" but used as a result
- **Issue:** The paper states n_eff(t) is "empirically testable, not formally proven" (Section 2, Theorem remarks). But n_eff(t) drives the scaling law analysis. A naive reader wonders: how much does the paper depend on this unproven claim?
- **Where:** Section 2 (theory); Section 3 (scaling exponent β)
- **Severity:** 3/5 — undermines confidence in the β = 2/3 corollary
- **Resolution:** Clearly demarcate which results depend on n_eff(t) conjecture vs. proven theorems. Quantify sensitivity.

### W5: β = 2/3 corollary is derived but never directly validated
- **Issue:** The paper derives β = 1/(1+ν) → 2/3 as ν→1/2 as a corollary of Theorem 2. But no direct empirical measurement of β is reported. The scaling exponent is only indirectly supported.
- **Where:** Corollary, Section 2; Section 3 (scaling law analysis)
- **Severity:** 3/5 — the headline scaling law prediction is untested
- **Resolution:** Fit β directly from the test loss vs. training fraction data and report the fitted value with confidence intervals.

### W6: F_eff(w) form is asserted, not derived from first principles
- **Issue:** F_eff(w) = F·(w/w0)^(-γ) with γ>1 is introduced to reconcile theory with data. But where does the power-law form come from? Why (w/w0)^(-γ) specifically?
- **Where:** Section 3.1
- **Severity:** 4/5 — this is the paper's main theoretical rescue move and it feels like curve-fitting
- **Resolution:** Either derive F_eff from the theoretical framework or show the fit is robust across multiple functional forms.

### W7: What is "Schaeffer smoothness"? Not defined in the paper
- **Issue:** Section 4 lists "Schaeffer smoothness" as a falsification test. I've never encountered this term. Is it a smoothness measure? A metric? A dataset property?
- **Where:** Section 4 (Falsification tests)
- **Severity:** 3/5 — I cannot evaluate whether this test is meaningful
- **Resolution:** Define Schaeffer smoothness in the main text or cite the original source.

### W8: The revised paper marks projected values with † — but how do I distinguish them from empirical?
- **Issue:** The prior review notes that revisions "projected values marked with †." I don't know which numbers in the paper are projected vs. empirical. The paper itself doesn't explain the † notation legend.
- **Where:** Throughout results tables
- **Severity:** 2/5 — minor but creates confusion for a naive reader
- **Resolution:** Add a legend: "† denotes projected values from theory" at the start of results tables.

---

## PER-RUBRIC SCORES

| Dimension | Score (1-10) | Calibration Anchor |
|---|---|---|
| **Originality / Novelty** | 8 | The unification of grokking + scaling laws via feature-space phase transitions is a genuinely new framing. Not a new paradigm (10) but a substantial conceptual advance (8). |
| **Soundness** | 5 | Heavy weight (1.5). The n_c direction reversal is a serious gap. n_eff(t) is unproven. F_eff(w) is asserted. Methodology for fitting γ and w0 is opaque. 0/51 sub-critical runs grokked is strong but the theory-experiment mismatch is not fully resolved. |
| **Significance** | 7 | If the phase transition framework holds, it matters for both grokking and scaling law research. Important within the subfield (8) but single-task (mod-47) limits cross-subfield generalizability (6→7). |
| **Clarity** | 6 | Mostly clear but: supidx undefined, λ undefined, Schaeffer smoothness undefined, † notation unexplained. A naive reader gets stuck in 3-4 specific places. |
| **Reproducibility** | 6 | Hyperparameters reported. Code not explicitly mentioned as released. Seed list given (42, 137, 256). Sufficient to reproduce if I could run 120 training runs — but no compute budget estimate. |
| **Contextualization vs prior work** | 6 | The paper positions itself vs. grokking literature and scaling law literature. But F_eff(w) form and Schaeffer test suggest prior work I can't trace. Some misses noted in prior review. |
| **Ethical / Broader Impact** | 6 | Standard boilerplate. No specific concerns but also no thoughtful discussion of what the phase transition framework means for practice. |

**Weighted Average:** (8×1.0 + 5×1.5 + 7×1.0 + 6×0.7 + 6×1.0 + 6×0.8 + 6×0.5) / 6.5 = (8 + 7.5 + 7 + 4.2 + 6 + 4.8 + 3) / 6.5 = 40.5 / 6.5 ≈ **6.2**

---

## POINTED QUESTIONS

1. **What does supidx in Figure 4 actually measure?** You use it to argue that superposition dynamics show a sharp drop at grokking onset, but you never define it. Is it the number of superimposed features? A norm of the representation? The term is never introduced.

2. **In Theorem 2, what is λ?** You write α = (σ_x²/2λ)·(1+γ/(λw))^(-1) but λ appears without definition. Without knowing what λ is, I can't compute α or verify the log(F) scaling.

3. **How did you fit γ and w0 in F_eff(w) = F·(w/w0)^(-γ)?** You claim γ>1 but you never report the fitted values. Are these free parameters fit per-width, or one global fit? If per-width, how many free parameters does that introduce?

4. **What is "Schaeffer smoothness"?** You list it as a falsification test but I've never encountered this term. Is it a smoothness metric on the data distribution? A property of the task? A citation would help.

5. **The β=2/3 corollary is never directly measured.** You derive it from the theory, but do you fit β from your data? Figure 5 shows test loss vs. training fraction — can you extract a β estimate from that? What value do you get?

6. **What stops n_c from going to zero at large width?** Your data shows n_c decreasing with width, and F_eff(w) explains this. But is there a width where grokking should disappear entirely? Does your theory predict a critical width?

7. **Why only 3 seeds?** Your grokking criterion (>90% test accuracy) is binary, but training dynamics are noisy. With only 3 seeds per condition, how stable is the grokking rate estimate? What is the standard error?

---

## FALSIFIABILITY TEST

**Question: What evidence would change my decision from Accept to Reject (or vice versa)?**

I would change my vote to **Reject** if:
- A follow-up experiment on a different task (e.g., mod-prime arithmetic, permuted MNIST) fails to show n_c decreasing with width, AND the F_eff(w) reconciliation doesn't hold.
- The F_eff(w) power-law form is shown to be a post-hoc fit with no theoretical grounding — e.g., if γ can take any value and still fit equally well.
- More than 0/51 sub-critical runs grok after extended training (currently 0/51 is strong evidence for the sharp threshold, but if even 1-2 sub-critical runs grok, the "sharp 0/1 boundary" claim weakens).

I would upgrade to **Accept** if:
- The authors fit β directly from their data and get β ≈ 0.67 (matching the 2/3 prediction), with confidence intervals that exclude 0.5.
- They show F_eff(w) derivation from first principles, not just curve-fitting.
- They release code and I reproduce the 120 runs with consistent grokking rates.

---

## CONFIDENCE

**3/5** — I am a naive reader. I cannot evaluate the mathematical proofs in Appendix A. I am relying on the paper's internal consistency and the peer review history. My main concern (W1: n_c direction reversal) is real but I recognize the authors have attempted to address it via F_eff(w). I am uncertain whether F_eff(w) is a genuine theoretical insight or an ad-hoc rescue.

---

## DECISION

**Borderline (5.5-6.5 range → Borderline)**

The weighted average of 6.2 sits in the Borderline range. The core theoretical framework is novel and valuable, but the soundness dimension is genuinely weak: the main empirical finding (n_c decreases with width) directly contradicts the theory's prediction (n_c increases with width). The reconciliation via F_eff(w) is plausible but insufficiently justified for an Accept.

If the F_eff(w) form were derived from first principles and β were directly fitted, this would be an Accept. As-is, the paper is learnable and the story is compelling, but the methodology gaps are too large to ignore at acceptance time.

**Recommendation:** Borderline — encourage major revision on soundness issues (W1, W2, W5, W6).

---

*— The Naive Reader*
