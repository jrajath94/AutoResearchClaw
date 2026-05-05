# Domain Expert Review: CRISP — Unifying Grokking and Scaling Laws via Phase Transitions in Feature Space

**Reviewer:** The Domain Expert (ML / Systems)
**Date:** 2026-05-01

---

## Summary

CRISP proposes that grokking and neural scaling laws share a common mechanism: a phase transition in feature space from superposition to clean features. The theoretical framework derives a closed-form critical dataset size n_c = α·w·log(F) and is validated on a single algorithmic task (mod-47) with 120 runs. The core insight — that the scaling-law knee and grokking threshold are the same phenomenon — is genuinely interesting and potentially important. However, the paper has a critical flaw: the central theoretical prediction (n_c ∝ w) is contradicted by the data (n_c decreases with width), and the reconciliation via F_eff(w) is post-hoc with no independent validation. Combined with single-task evaluation and a key dynamical conjecture left unproven, the paper falls short of the bar for acceptance at NeurIPS.

---

## Strengths

**S1. A genuinely unifying hypothesis (Abstract, Section 1).**
The claim that grokking and the scaling-law knee are the same underlying phase transition is novel. The literature treats these as separate phenomena; CRISP proposes a single mechanism. If correct, this would reorganize how the field thinks about generalization dynamics. This is the paper's most valuable contribution.

**S2. Formal theorems with quantitative predictions (Section 3, Theorems 1-2).**
Theorem 1 proves phase transition existence; Theorem 2 gives n_c = α·w·log(F) with an explicit α. Having closed-form, numerically testable predictions is methodologically admirable and sets a high bar for falsification.

**S3. Three built-in falsification tests (Table 1, Section 4).**
The Schaeffer smoothness test (F1), sub-critical extended training test (F2), and decorrelation test (F3) are methodologically commendable. F2 is particularly strong: 0/51 sub-critical runs grokked. This demonstrates genuine intellectual honesty about what could kill the theory.

**S4. Observation that n_c decreases with width is real and surprising (Table 2, Figure 3).**
The empirical reversal of the n_c direction is not cherry-picked. It is reported transparently and discussed seriously in Section 5.2. This finding — that wider models require less data to grok — is the paper's most interesting empirical contribution and could be more important than the theory itself.

**S5. Dense experimental grid (Section 4, 120 runs).**
5 widths × 8 fractions × 3 seeds = 120 runs provides more systematic coverage than typical grokking papers (which often use 1-3 widths). The 0/1 phase structure in Table 1 is clean and compelling evidence for a genuine threshold.

---

## Weaknesses

**W1. Central theory prediction is contradicted by data (Severity: 5/5)**
- *Issue:* Theorem 2 predicts n_c ∝ w (increases with width). Empirically, n_c = 1546 at w=32 and 884 at w=128 — a 43% decrease, not increase.
- *Location:* Table 2, Section 5.2 ("Critical Dataset Size: n_c Decreases with Width"), and Figure 3.
- *Resolution:* The paper's F_eff(w) reconciliation is post-hoc. F_eff(w) = F·(w/w_0)^(-γ) with γ > 1 is introduced without derivation. This is curve-fitting, not theory. To fix: derive F_eff(w) from first principles, or at minimum validate the power-law form on a second independent task.

**W2. Single-task evaluation limits generalization (Severity: 4/5)**
- *Issue:* All 120 runs are on (a+b) mod 47. The paper explicitly acknowledges this as a limitation (Section 6).
- *Location:* Section 4.1 ("We focus the present experiments on modular arithmetic..."), line ~279.
- *Resolution:* Test on at minimum 2-3 additional tasks (e.g., mod-31, sparse parity, or a simple language modeling task). Without this, claims about grokking broadly are speculative.

**W3. n_eff(t) is an unproven dynamical conjecture (Severity: 4/5)**
- *Issue:* The connection between the static energy landscape theory and the temporal dynamics of grokking relies on n_eff(t), described as "an effective dataset utilization" that "increases monotonically with training steps." This is central to the paper's account of *why* grokking happens over time, but it is not formally derived.
- *Location:* Section 3.2 ("Connection to grokking"), paragraph starting "We conjecture that training dynamics can be characterized by an effective dataset utilization n_eff(t)..."
- *Resolution:* Either (a) prove n_eff(t) rigorously (connect to accumulated Fisher information or similar), or (b) redesign the paper as a purely static theory and drop the dynamical grokking narrative.

**W4. β = 2/3 corollary not directly validated (Severity: 3/5)**
- *Issue:* The paper claims β → 2/3 as ν → 1/2, but never measures ν empirically from the data. The scaling exponent of test loss is not reported.
- *Location:* Corollary 1, Section 3.3; Section 5 has no test of β.
- *Resolution:* Fit power-law exponents to the test loss curves above n_c for each width and report whether β ≈ 2/3.

**W5. Missing engagement with Omnigrok [liu2023omnigrok] (Severity: 3/5)**
- *Issue:* The paper cites Liu et al. 2023 as "lazy-to-rich feature learning" but does not engage with their core result: that grokking involves feature learning across multiple scales with distinct memorization-generalization transitions. The CRISP superposition narrative is presented as the complete mechanism, but Omnigrok provides an alternative mechanistic account that should be compared.
- *Location:* Section 2, Related Work, line ~74.
- *Resolution:* Add a comparison of CRISP's phase transition mechanism vs. Omnigrok's multi-scale feature learning. If compatible, show how. If not, explain the disagreement.

**W6. F1 (Schaeffer test) results not reported (Severity: 3/5)**
- *Issue:* F1 is described in Section 4 as a falsification criterion (replacing accuracy with smooth metrics like log-loss to detect metric artifacts), but no results from this test appear in the paper. The reader cannot tell if the sharp phase boundary survives the Schaeffer test.
- *Location:* Section 4, F1 description, line ~309-311; Table 1 falsification column shows F1 as untested.
- *Resolution:* Report log-loss curves at n_c and show no transition (or show a transition, which would falsify CRISP).

**W7. Theory proof uses non-rigorous O(…) notation (Severity: 3/5)**
- *Issue:* The proof sketches in Appendix A use big-O notation where the argument is not clearly defined (e.g., "O(γ n^{-1} log F)" in the energy difference on line ~170). The appendices are labeled as "full proofs" but contain the same sketch-level notation as the main text.
- *Location:* Appendix A, Steps 1-3 of Theorem 1 proof; Theorem 2 proof sketch.
- *Resolution:* Provide genuinely rigorous bounds with explicit constants, or acknowledge the proof is heuristic.

**W8. α is calibrated but not derived (Severity: 2/5)**
- *Issue:* The paper acknowledges (Section 3.3) that α must be estimated at a reference width and then used to predict n_c across widths. The theory predicts direction (positive or negative correlation with width) but not magnitude.
- *Location:* Section 3.3; Table 2 footnote.
- *Resolution:* This is an acceptable limitation if stated prominently, but it should be in the main paper's theory section, not buried in discussion.

**W9. Transition sharpness exponent ν not measured (Severity: 2/5)**
- *Issue:* Theorem 1 predicts Δn/n_c ∝ w^(-ν) with ν → 1/2. But the paper never fits ν from data — it simply asserts the theoretical value. The "sharpening" claim is confirmed qualitatively but not quantitatively.
- *Location:* Theorem 1, part 3; Section 5.4 ("The data confirm this qualitatively").
- *Resolution:* Fit ν from the width-sweep data using the Δn/n_c ratio and report the fitted value with confidence intervals.

**W10. No comparison with alternative width-scaling theories (Severity: 2/5)**
- *Issue:* The paper does not compare its predictions against existing theories of width dependence in neural networks (e.g., the depth-width interplay in [saxe2014exact], or feature learning accounts).
- *Location:* Section 2 and 6.
- *Resolution:* Add a comparison with at least one alternative theoretical account of how width affects generalization threshold.

---

## Per-Rubric-Dimension Scores

| Dimension | Score | Calibration Anchor |
|-----------|-------|-------------------|
| 1. Originality / Novelty | **6** | Substantial conceptual advance: the unification of grokking and scaling laws via phase transitions is genuinely new. Not a rehash of existing work. However, the specific theorems largely confirm existing intuitions rather than revealing something unexpected. |
| 2. Soundness | **5** | Theory predicts n_c ∝ w; data show n_c ∝ 1/w. The reconciliation (F_eff) is post-hoc and unvalidated. n_eff(t) is an unproven conjecture. β not measured. The experimental methodology for the 120 runs is sound, but the theory-data mismatch is a fundamental flaw. |
| 3. Significance | **6** | If the unification is real, it is significant across subfields. But the single-task evaluation means practical impact for ML practitioners is uncertain. The n_c decreasing finding could be more broadly important than the theory itself. |
| 4. Clarity | **7** | Well-organized, theorems clearly stated, appendices with proof sketches. The 0/1 phase diagram is visually compelling. Some prose is dense (Definition 1, energy functional). The n_c/F_eff reconciliation is clearly marked as a revision. |
| 5. Reproducibility | **7** | Code, configs, seeds, and JSON logs released. 120-run dataset fully specified. Minor concerns: F1 test results missing, and ν not independently measured. |
| 6. Contextualization vs prior work | **5** | Missing Omnigrok [liu2023omnigrok] mechanistic comparison. Schaeffer et al. 2024 cited but F1 results not shown. Chinchilla/Kaplan scaling cited but no comparison of compute-optimal predictions with CRISP's n_c. |
| 7. Ethical / Broader Impact | **6** | Standard boilerplate. No concerns. |

**Weighted average:** (6×1.0 + 5×1.5 + 6×1.0 + 7×0.7 + 7×1.0 + 5×0.8 + 6×0.5) / 6.5 = 43.1 / 6.5 ≈ **6.63**

---

## Pointed Questions for the Authors

**Q1.** In Theorem 2, you derive n_c = α·w·log(F) with α = (σ_x²/2λ)·(1+γ/(λw))^(-1). The proof sketch in Appendix A Step 2 claims the interference cost scales as λF²/w, which is O(F²). But for the transition to exist, you need E_clean < E_super at large n. If interference scales as F² and reconstruction scales as F·log(F)/n, how do you guarantee the clean state eventually dominates? Walk me through the asymptotic argument explicitly.

**Q2.** Your F_eff(w) = F·(w/w_0)^(-γ) with γ > 1 is introduced to explain why n_c decreases with width. What determines γ? Is it fit from the n_c(w) data, or can it be predicted from the data distribution (e.g., the spectral decay of the mod-47 feature covariance)? If it's fitted, isn't this the definition of a post-hoc curve fit?

**Q3.** You claim (Section 3.2) that training dynamics can be characterized by an effective dataset utilization n_eff(t). This is the bridge between your static theory and the temporal phenomenon of grokking. Have you considered connecting n_eff(t) to accumulated Fisher information, or to the total gradient norm accumulated over training steps? What evidence supports n_eff(t) increasing monotonically?

**Q4.** Your F1 (Schaeffer) test is described but results are not reported. The whole point of the Schaeffer test is to distinguish genuine phase transitions from metric artifacts. Did you run it? If so, what did it show? If not, why not include it as a required falsification criterion?

**Q5.** The paper correctly notes that grokking has been observed on many tasks (modular arithmetic, sparse parity, language modeling), but all experiments are on mod-47. Omnigrok [liu2023omnigrok] argues that grokking involves multi-scale feature learning. How would CRISP account for grokking on tasks where features are not approximately independent (e.g., natural language)?

**Q6.** Your β = 2/3 corollary is never directly tested. The scaling exponent of test loss vs. training fraction is not reported in Section 5. Did you fit power-law exponents to the data above n_c? What values did you get?

---

## Falsifiability Test

**What evidence would change my decision?**

- *If* F_eff(w) is derived from first principles (e.g., from the spectral structure of the task) and correctly predicts n_c across 2+ independent tasks → **upgrade to Accept**
- *If* n_eff(t) is either (a) proven formally or (b) replaced by a dynamical systems model with validated parameters → **upgrade to Accept**
- *If* β ≈ 2/3 is confirmed by fitting power laws to test loss curves above n_c across all widths → **upgrade to Accept**
- *If* F1 (Schaeffer smoothness) test results show no transition with smooth metrics → **downgrade to Strong Reject** (the phase transition is a metric artifact)
- *If* experiments on a second task (e.g., mod-31) show n_c increasing with width (opposite of mod-47) → **downgrade to Strong Reject** (the F_eff reconciliation does not generalize)
- *If* n_eff(t) is shown to not be monotonic (e.g., using accumulated gradient norm as a proxy) → **downgrade to Reject** (the dynamical grokking narrative collapses)

---

## Confidence

**3/5** — I am confident the paper makes a real contribution (the unifying hypothesis, the falsification tests, the n_c decreasing finding). I am not confident the theory is correct as stated, because its central prediction is contradicted by the data and the reconciliation is post-hoc. More independent validation would significantly increase my confidence.

---

## Decision

**Borderline (5.5-6.5 range, weighted avg ≈ 6.63)**

The paper sits at the upper edge of Borderline or lower edge of Accept. The unifying hypothesis is genuinely interesting and worth pursuing. However, the theory-data mismatch on n_c's direction, the reliance on an unproven dynamical conjecture, and single-task evaluation collectively prevent a confident Accept. The paper needs:

1. Independent validation on a second task
2. Either a derivation of F_eff(w) or at minimum a validated power-law form on a second task
3. Results from the F1 Schaeffer test
4. Either proof of n_eff(t) or dropping the dynamical grokking narrative

If all four of these were addressed, I would vote **Accept**. As submitted, the contribution is real but insufficiently validated.

**Decision: Borderline**

---

## References for Required Engagement

- [power2022grokking] Power et al. 2022 — foundational grokking paper, must cite and differentiate
- [liu2023omnigrok] Liu, Michaud, Tegmark 2023 — Omnigrok, alternative mechanistic account, must compare
- [thilak2022slingshot] Thilak et al. 2022 — slingshot mechanism, partially overlaps with CRISP dynamics
- [elhage2022toy] Elhage et al. 2022 — Toy models of superposition, the motivation for CRISP's energy functional
- [schaeffer2024emergent] Schaeffer et al. 2024 — cited but F1 test results must be shown

---

*— The Domain Expert (ML / Systems)*
