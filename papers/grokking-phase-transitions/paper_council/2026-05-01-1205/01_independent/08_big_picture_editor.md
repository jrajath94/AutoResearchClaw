# Review — The Big-Picture Editor

**Paper:** CRISP: Unifying Grokking and Scaling Laws via Phase Transitions in Feature Space
**Venue:** NeurIPS 2026
**Date:** 2026-05-01

---

## Summary

CRISP claims to unify grokking and neural scaling laws via a shared mechanism: a phase transition in feature representation from superposed to clean at a critical dataset size n_c. The theory yields a closed-form n_c = α · w · log(F) and a corollary β = 1/(1+ν) → 2/3 connecting the transition sharpness exponent to scaling law slope. Validation is on modular arithmetic (mod-47) with 120 runs across 5 widths.

**Bottom line:** The paper has a genuinely useful organizing idea — that grokking and scaling laws share a phase transition mechanism — but the theory's most surprising empirical result (n_c decreases with width) is explicitly a counter-prediction that required post-hoc修补 (F_eff(w)), and the most crisp quantitative prediction (β = 2/3) is untested. A solid Borderline that could become Accept with targeted follow-up experiments.

---

## Strengths

1. **Theorem 1 as conceptual glue.** The formal identification that grokking = a phase transition from superposition to clean features is useful organizing thinking. Even if the gradient-condition proof is mechanical, saying "grokking and scaling knees are the same phenomenon with different effective dataset sizes" gives researchers a single knob to think with. This will be cited.

2. **Falsification-conscious design.** Three built-in tests (Schaeffer smoothness, sub-critical extended training, feature decorrelation) are more than most phase-transition papers attempt. The claim "0/51 sub-critical runs grokked" (F2) is a strong clean negative result — exactly the kind of evidence that earns lasting credibility. Table 2's sharp 0/1 phase boundary is also compelling.

3. **Corollary 1 as transferable prediction.** β = 1/(1+ν) with ν → 1/2 → β → 2/3 is a specific, testable numerical prediction that, if confirmed, would make this paper influential beyond the mod-47 setup. The connection between transition sharpness and scaling exponent is the kind of cross-regime prediction that justifies publication.

4. **Sharp phase boundary in Table 2 / Fig 2.** The 0→1 transition from 0% to 100% grok rate over a narrow fraction range (especially at w=128: 0% at f=0.3 to 100% at f=0.4) is exactly what a true phase transition looks like. This is the paper's most visually striking empirical result and directly supports the theory.

5. **Fig 4 decorrelation evidence.** The claim that superposition index S(t) drops sharply at the same training step where test accuracy jumps is the right mechanistic story. If r > 0.8 holds across conditions, this is the causal story the theory needs.

---

## Weaknesses

1. **The central prediction goes the wrong direction — and is patched post-hoc.**
   - *Issue:* Naive CRISP theory predicts n_c ∝ w (increases with width). Table 3 shows n_c monotonically *decreases* with width. The reconciliation uses F_eff(w) = F · (w/w₀)^(−γ), γ > 1 — but this formula is introduced to explain the discrepancy, not derived from first principles.
   - *Where:* Section 3.3 / Table 3 / Discussion Section 6
   - *Severity:* 4/5 — this is the paper's most surprising empirical result and the theory cannot predict it.
   - *Resolution:* Either (a) derive F_eff(w) formally from the energy landscape framework, showing why wider networks have lower effective feature counts, or (b) acknowledge F_eff(w) as an empirical correction and validate it across 3+ different tasks.

2. **The β = 2/3 corollary is asserted, not demonstrated.**
   - *Issue:* The paper predicts β → 2/3 for large width as a corollary, but there is no comparison to neural scaling law literature (Kaplan et al. 2020 report β ≈ 0.076–0.078 for language models, nowhere near 2/3) and no empirical validation within the paper.
   - *Where:* Section 3.3 Corollary / Section 5 (Results) — no comparison to Kaplan or Hoffmann
   - *Severity:* 3/5 — this is the paper's most-exportable prediction but is untested.
   - *Resolution:* Fit β from the mod-47 scaling law data (Fig 5) and show it approaches 2/3 as width increases. Cite where β = 2/3 appears in the literature and where it doesn't, and explain the discrepancy.

3. **n_eff(t) is the core mechanism but is hand-waved.**
   - *Issue:* The connection from theory to grokking delay requires n_eff(t) (effective dataset utilization) increasing with training steps, crossing n_c, triggering the phase transition. The paper explicitly labels this a "conjecture" (Note, Section 3.2) but it is central to the entire narrative.
   - *Where:* Section 3.2, connection to grokking paragraph; also Discussion Section 6 "What theory gets wrong"
   - *Severity:* 4/5 — without a mechanism for n_eff(t) growth, the theory explains steady-state but not the temporal dynamics of grokking.
   - *Resolution:* Either derive n_eff(t) from first principles or present empirical evidence that n_eff tracks a measurable quantity (e.g., gradient norms, effective rank of activations).

4. **α calibration is circular.**
   - *Issue:* α is calibrated at w=256, then used to predict n_c at other widths. This is curve-fitting, not prediction. The paper's C2 claim ("closed-form n_c") is weakened by this dependence on empirical calibration at one width.
   - *Where:* Section 3.3 Note; Appendix B
   - *Severity:* 2/5 — a standard practice in theory papers, but worth flagging transparently.
   - *Resolution:* Hold out one width for true prediction, or show α is stable across widths when estimated from sub-critical dynamics.

5. **Single task, single architecture class.**
   - *Issue:* mod-47 arithmetic with 2-layer MLPs. No transformers, no convnets, no language tasks. Grokking has been observed in transformers doing modular arithmetic (Nanda et al. 2023); the theory should at least gesture toward why transformers would behave similarly.
   - *Where:* Section 4 (Experimental Design); Discussion "Future work: extend to transformers"
   - *Severity:* 3/5 — limits generalizability of the "phase transition" claim.
   - *Resolution:* Run at least one experiment with a different task family (e.g., parity, CIFAR-10) to show F_eff(w) and n_c behavior are robust.

6. **Decorrelation test (F3) requires r > 0.8 but doesn't report the actual value.**
   - *Issue:* F3 requires "r > 0.8 correlation" between n_c and S-drop, but the paper bundle doesn't report the observed correlation value. The falsification test is only as good as its actual measured threshold.
   - *Where:* Section 4, F3 description; Appendix B
   - *Severity:* 2/5 — easy to fix with a number.
   - *Resolution:* Report the observed r value per condition. If any condition fails r > 0.8, acknowledge it.

7. **Missing comparison to Kaplan et al. 2020 / Hoffmann et al. 2022 scaling results.**
   - *Issue:* The paper claims to unify grokking and scaling laws but never compares its β = 2/3 prediction to the empirical scaling exponents from large language model studies (β ≈ 0.076 for language, not 0.67). This gap is unexplained.
   - *Where:* Section 2 (Related Work); Section 3.3 Corollary discussion
   - *Severity:* 3/5 — undermines the "unification" claim.
   - *Resolution:* Either explain why β = 2/3 is specific to the mod-47 regime (small models, memorization-dominant) vs. the LLM regime (generalization-dominant), or drop the unification claim and position as "partial unification."

8. **The theory does not predict the critical fraction — it only fits it.**
   - *Issue:* The theory predicts n_c ∝ w · log(F) but F (latent feature count) is not known a priori for the mod-47 task. F_eff(w) is estimated by fitting, not derived. True predictive power would require knowing F from task structure alone.
   - *Where:* Section 3.3 / Table 3
   - *Severity:* 3/5 — limits predictive utility.
   - *Resolution:* Show that F can be estimated from the algebraic structure of the task (e.g., number of independent parity functions) and validate n_c across tasks with different F.

---

## Per-Rubric Scores

| Dimension | Score | Calibration Anchor |
|-----------|-------|-------------------|
| Originality / Novelty | 7 | Substantial conceptual advance — phase transition unification is genuinely new framing. Loses points because the F_eff(w) patch is post-hoc and β=2/3 is untested. |
| Soundness | 6 | Adequate methodology; 120 runs across 40 conditions is solid for a theory paper. F2 (0/51 negative result) is strong. F3 correlation not reported. α calibration issue is minor. |
| Significance | 7 | If β = 2/3 is confirmed, this changes how multiple subfields think about grokking and scaling simultaneously. The phase transition framing is a reusable conceptual lens. |
| Clarity | 8 | Clear structure, well-organized, figures are informative. Theory section is dense but readable. One sentence summary at department lunch: "grokking and scaling law knees are the same phase transition." |
| Reproducibility | 7 | Code and JSON logs released. Hyperparameters fully specified. α calibration procedure should be in the main paper, not just Appendix B. |
| Contextualization vs prior work | 6 | Good coverage of grokking literature. Misses comparison to empirical scaling law exponents (Kaplan, Hoffmann) which is critical for the unification claim. |
| Ethical / Broader Impact | 6 | Boilerplate but adequate. No concerns. |

**Weighted Average: (7×1.0 + 6×1.5 + 7×1.0 + 8×0.7 + 7×1.0 + 6×0.8 + 6×0.5) / 7.5 = 46.9 / 7.5 ≈ 6.25**

---

## Pointed Questions

1. **Forget the benchmarks — what's the one sentence that changes a researcher's mental model after reading this?**
   If the answer is "grokking is a phase transition," that's useful but not novel (Schaeffer et al. 2024 already proposed smoothness as falsification). If the answer is "n_c decreases with width because F_eff(w) shrinks," that IS novel — but it's a post-hoc explanation. Which sentence is the lasting contribution?

2. **If you had to make one bold quantitative prediction that your theory got right and prior theories got wrong, what would it be?**
   Prior theories predict n_c ∝ w or n_c ∝ constant. Your theory, post-patching, predicts n_c decreases with width. That's surprising. Has any prior grokking theory made this prediction? If not, is this a genuine prediction or an accommodation to data?

3. **The β = 2/3 prediction is your most exportable claim. Why isn't it validated in the paper?**
   Fig 5 shows the scaling law knee, but no fit of β is reported. What is the measured β from your data? Does it approach 2/3 as width increases? If not, what does the theory say about the regime where β ≠ 2/3?

4. **What is the mechanistic origin of n_eff(t) growth?**
   You say n_eff increases with training steps, triggering the phase transition. But what drives n_eff upward? If it's "the network learns more efficient representations," that's circular. If it's "gradient drift / ensembling," give me the story. Without this, grokking is explained by assertion, not mechanism.

5. **If I gave you a new task (e.g., CIFAR-10 classification) and told you the width and latent feature count, could you predict n_c without fitting any parameters at that task?**
   If yes: demonstrate it. If no: what is the minimum additional information needed? This is the test of whether the theory is predictive orcurve-fitting with extra steps.

6. **The decorrelation test (F3) — what correlation value did you actually measure?**
   Your falsification criterion is r > 0.8. If this is the pass/fail threshold, reporting the actual r values is not optional — it determines whether the paper's own falsification test passes or fails.

7. **Why does β = 2/3 not appear in Kaplan et al. 2020 (β ≈ 0.076 for language)?**
   The unification claim requires explaining this orders-of-magnitude discrepancy. Is the mod-47 regime fundamentally different from LLM scaling? If so, what determines which regime a model is in? If not, the unification claim is weakened.

8. **Is F_eff(w) = F · (w/w₀)^(−γ) derived or fitted?**
   If derived: show the derivation from the energy landscape. If fitted: say so explicitly. Calling it a "reconciliation hypothesis" without status (theory vs. fitting) creates ambiguity about whether the theory is confirmed or rescued.

---

## Falsifiability Test

**What evidence would change my decision?**

*Promote to Strong Accept:* Authors fit β from Fig 5 scaling data, show it approaches 2/3 as width increases from 32→128, and cite Kaplan/Hoffmann explaining why LLM scaling exponents differ (regime separation argument). OR authors hold out w=96 as a true prediction, show n_c matches within 20%, and release F_eff(w) estimation procedure.

*Demote to Borderline:* Authors fail to report the F3 correlation value (r unknown) — falsification test cannot be evaluated. OR comparison to Kaplan scaling exponents reveals the β = 2/3 prediction is regime-inconsistent with no explanation.

*Demote to Reject:* F3 decorrelation fails (r < 0.8 in ≥1 condition). OR β from mod-47 data does NOT approach 2/3. OR F_eff(w) is shown to be a fitted parameter with no theoretical grounding.

*Strong Reject:* The theory's central prediction (n_c direction with width) is shown to be a curve-fitting accommodation, not a genuine prediction, and the paper does not acknowledge this.

---

## Confidence

**3/5** — The conceptual framing is strong and the phase transition unification is a genuinely useful idea. The empirical results (sharp phase boundary, 0/51 negative result, n_c decreasing with width) are solid and surprising. But two critical predictions — F_eff(w) derivation and β = 2/3 — are either post-hoc or untested, which makes me uncertain whether the lasting contribution is the unifying concept or just the mod-47 observations. I need one of those predictions validated before I can commit to Accept.

---

## Decision

**Borderline** — The paper has a lasting conceptual contribution (phase transition unification) but incomplete empirical validation of its most exportable predictions. Accept if β = 2/3 is validated and F_eff(w) derivation is provided or acknowledged as fitting. Otherwise revise to Reject on the unification claim and reposition as a theory paper about mod-47 grokking.

**— The Big-Picture Editor**
