# Red Team Attacks on CRISP

## TOP 3 CLAIMS UNDER ATTACK

---

### ATTACK 1: Theorem 2 — n_c = α·w·log(F) predicts the WRONG direction

**The claim (precise):**
Theorem 2 states: `n_c = α·w·log(F)` where `α = (σ_x²/2λ)·(1+γ/(λw))^(-1)`

This predicts `n_c ∝ w` — the critical dataset size **increases** with network width.

**What the data actually show:**
- w=32 → n_c=1546
- w=48 → n_c=1325
- w=64 → n_c=1105
- w=96 → n_c=1105
- w=128 → n_c=884

**n_c DECREASES with width.** The theory and data are directionally opposite.

**What would REFUTE it:**
- Any measurement of n_c at a width larger than 128 (e.g., w=256, w=512) that continues the decreasing trend would confirm the data contradict the theory.
- A single additional task (e.g., mod-53) where n_c decreases with width would suggest the Theorem 2 direction error is not specific to mod-47.
- If n_c for w=64 is significantly higher than n_c for w=128 on a second independent modulus, the directional failure is confirmed.

**Failure mode making the paper RETRACTABLE:**
If a public replication (by any group) on mod-53 or mod-101 shows n_c **increasing** with width, Theorem 2 is falsified. The paper must then either (a) admit the theory was wrong from the start, or (b) produce a first-principles derivation of F_eff(w) that was **not** fitted to the 5-width empirical data. A failed Theorem 2 takes the entire "unification" narrative with it, because the scaling law derivation depends on the n_c formula.

**Retraction Risk: HIGH**

The direction reversal is acknowledged by all 8 reviewers as the paper's #1 scientific problem. It is not a minor quantitative discrepancy — it is a qualitative contradiction. Every review that flags soundness concerns cites this as the primary cause.

---

### ATTACK 2: F_eff(w) = F·(w/w0)^(-γ) is unfalsifiable within the same dataset

**The claim (precise):**
The paper introduces a "refined formula": `n_c = α·w·log(F_eff(w))` where `F_eff(w) = F·(w/w0)^(-γ)` with γ>1.

This rescue hypothesis explains the n_c direction reversal by positing that effective feature count **shrinks** with width, overwhelming the `w` factor in the formula.

**What would REFUTE it:**
- Independent measurement of F_eff(w) via representation probing, linear separability analysis, or feature attribution metrics showing F_eff does NOT decrease with width (or increases/is constant).
- If γ is fitted to the 5 n_c values and the fitted residuals show no improvement over a simpler n_c ∝ 1/w fit, F_eff(w) adds nothing.
- If w0 and γ are simultaneously fitted to 5 data points (w=32,48,64,96,128), the degrees of freedom are too many — the fit has essentially zero predictive power.
- A mod-53 experiment where n_c still decreases but F_eff(w) would need a **negative** γ to fit (contradicting the γ>1 assumption), proving the form is task-specific curve-fitting.

**Failure mode making the paper RETRACTABLE:**
If anyone demonstrates that F_eff(w) was posited **after** observing the n_c direction reversal, and that γ/w0 were fitted to the same data used to test Theorem 2, the paper's theoretical narrative is post-hoc rationalization. This is the "garden of forking paths" made mathematical — every time the data contradicts the theory, a new free parameter absorbs the discrepancy.

**Retraction Risk: HIGH**

The F_eff(w) rescue is called "post-hoc curve-fitting" by the Theory Critic, "textbook post-hoc auxiliary hypothesis" by the Adversarial Practitioner, and "unfalsifiable within the same dataset" by the Statistical Rigorist. If this is identified as such by a public reviewer, it undermines the paper's core credibility — it becomes a story that can accommodate any data.

---

### ATTACK 3: Corollary — β → 2/3 is asserted but NEVER measured

**The claim (precise):**
Corollary states: `β = 1/(1+ν) → 2/3 as ν → 1/2`

This connects the phase transition sharpness exponent ν to the neural scaling law exponent β, predicting that test loss scales as `L ∝ n^(-2/3)` for large width.

**What would REFUTE it:**
- Fitting `L ∝ n^(-β)` to the test loss vs. training fraction data in Figure 5 and obtaining β ≠ 2/3 (e.g., β ≈ 0.5 or β ≈ 0.9).
- If the fitted β has confidence intervals wide enough to include values far from 2/3 (e.g., CI [0.4, 0.9]), the prediction is unvalidated.
- If the scaling law fit is poor (low R²), the power-law form itself is not established.

**Failure mode making the paper RETRACTABLE:**
The β=2/3 corollary is the paper's most "exportable" claim — the bridge from grokking to the scaling laws literature. If a public reviewer fits β from Figure 5 data and finds β ≠ 2/3, the corollary collapses. The paper loses its primary connection to the scaling law literature, leaving only the grokking-specific contribution. If the fit is poor or the measured β contradicts 2/3 by >0.15, the paper should be retracted because the main exportable implication is false.

**Retraction Risk: MEDIUM**

This is rated MEDIUM (not HIGH) because the corollary is explicitly marked as derived, not measured. However, 5 out of 8 reviewers flag β=2/3 non-validation as a serious gap. The claim is presented prominently, and if a reviewer demonstrates the fitted exponent is e.g., ~0.5 (common in some scaling law literature), the paper's broader impact claim fails. The corollary being unvalidated is a scientific gap, but the theory itself is not mathematically wrong — only unconfirmed.

---

## THE SINGLE MOST DANGEROUS FLAW

**The F_eff(w) rescue, fully executed.**

Here is the failure mode that would destroy the paper's credibility publicly:

A reviewer or replicator points out: *"Theorem 2 makes a clear directional prediction (n_c increases with width). The data show the opposite. The authors respond by introducing F_eff(w) = F·(w/w0)^(-γ) with γ>1 to flip the sign. But this parameter was introduced SPECIFICALLY to explain the observed contradiction — it was not predicted in advance, not derived from first principles, and not validated on any held-out data. With 5 data points (w=32,48,64,96,128) and 2 free parameters (w0, γ), this is a fit to noise. More critically: the theory's central equation now becomes `n_c = α·w·log(F_eff(w))`, but F_eff(w) is defined by the data it is meant to explain. There is no independent measurement of F_eff. The theory is unfalsifiable: any monotonic dataset can be accommodated by choosing γ appropriately."*

This is the "unfalsifiable theory" attack. It does not require showing the data are wrong — it requires showing the theory has been constructed to be consistent with any data. The paper's own falsification infrastructure (Claim 6: "three falsification tests") cannot be applied to F_eff(w) because F_eff(w) is not an independently measurable quantity.

**If pointed out publicly, this would undermine the paper's core contribution** (the unification claim) because the paper cannot produce a clean, falsifiable prediction. Every reviewer has flagged this as the most serious concern. A single public demonstration that the F_eff(w) form was retrofitted rather than predicted would invalidate the paper's central theoretical narrative.

---

## IS THE F_eff(w) RESCUE SCIENTIFIC OR AD-HOC?

**Verdict: AD-HOC**

Criteria for scientific rescue (post-hoc theory modification):

1. **Pre-registration**: Was F_eff(w) proposed BEFORE examining the width-dependence data? No. It was introduced in response to the n_c direction reversal.

2. **Independent predictiveness**: Does F_eff(w) make predictions on held-out data? No. γ and w0 are fitted to the same 5-width dataset that Theorem 2 is tested against.

3. **Derivation from first principles**: Is F_eff(w) derived from the phase transition physics, or is it an empirically-motivated power law? It is asserted as `F·(w/w0)^(-γ)` with no derivation from the energy functional in Theorem 1.

4. **Degrees of freedom**: With 5 data points and 2 free parameters (w0, γ), the fit has effectively zero statistical power. Any monotonic decreasing trend can be fit by a power law with appropriate exponents.

5. **Alternative forms considered**: The paper does not report testing alternative functional forms for F_eff(w) (exponential, logarithmic, step-function). The choice of power law is not justified.

6. **Physical interpretation**: γ>1 means effective features shrink faster than width grows. There is no mechanical model of WHY wider networks would have fewer effective features — this contradicts typical accounts of width increasing feature diversity.

**Conclusion**: The F_eff(w) rescue fails the scientific rescue test at every point. It is a parameter salvage operation, not a theory correction. The paper acknowledges this ("F_eff(w) reconciles") but intellectual honesty does not make it valid.

---

## SUMMARY TABLE

| Claim | Core Prediction | Empirical Outcome | Refutation Evidence | Retraction Risk |
|---|---|---|---|---|
| Theorem 2 | n_c ∝ w (increases) | n_c decreases with width | mod-53 shows n_c increasing; F_eff(w) fitted post-hoc | HIGH |
| F_eff(w) | F_eff shrinks with width (γ>1) | Introduced to fix Theorem 2 | F_eff measured independently; alternative functional forms; degrees of freedom analysis | HIGH |
| β = 2/3 corollary | Test loss scaling exponent → 2/3 | Never directly measured | Power law fit to Figure 5 gives β ≠ 2/3 | MEDIUM |

---

*Red team attack complete. All three attacks are supported by cross-reviewer consensus. The F_eff(w) rescue is the paper's most vulnerable point — if challenged publicly, it exposes the theory as accommodation rather than prediction.*
