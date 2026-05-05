# Domain Expert (ML/Systems) Review: CRISP

**Paper:** CRISP: Unifying Grokking and Scaling Laws via Phase Transitions in Feature Space
**Reviewer:** The Domain Expert
**Date:** 2026-05-01

---

## 1. Strengths

1. **Phase-transition reframing of grokking (Theorem 1, Section 3.2):** The paper's core conceptual move—connecting grokking to a phase transition in feature space—is well-motivated and builds on the superposition hypothesis of Elhage et al. 2022. The formal proof sketch in Appendix A correctly identifies two classes of critical points (superposed vs. clean) and uses an intermediate-value-theorem argument to establish a sign change in energy difference. This is a legitimate theoretical contribution to the mechanistic interpretability literature on grokking.

2. **Three falsification tests (Section 3.3 / F1-F3):** The paper explicitly incorporates Schaeffer et al. 2024's smoothness test (F1), sub-critical extended training (F2), and decorrelation (F3). The F2 result (0/51 sub-critical runs grokked) is a strong empirical finding that provides genuine evidence against the "just train longer" confound. F1 and F3 are appropriate checks for metric artifacts and mechanistic validity.

3. **Sharp 0/1 phase boundary (Table 2, Section 5.1):** Table 2 shows a near-deterministic phase boundary across all 40 conditions, with grok rates jumping from 0% to 100% within a single fraction increment for most widths. This is the paper's strongest empirical result and provides convincing evidence that grokking is threshold-driven rather than gradual.

4. **Grokking delay trends (Table 4, Section 5.3):** Table 4 documents clear systematic trends: delays decrease with both data and width. At w=64, delay drops from 8,333 steps at f=0.5 to <1,000 at f≥0.7. At f=0.5, delay drops from 8,333 (w=64) to 1,333 (w=128). These quantitative trends are valuable and reproducible given the released code and JSON logs.

5. **Reproducibility package:** The paper ships reproduce.py, sweep_results.json (120 runs), and summary.json with full hyperparameter tables. A single A100 reproduces the full sweep in ~30 minutes. This earns the "code+configs+data" tier and substantially exceeds NeurIPS reproducibility standards.

---

## 2. Weaknesses

### W1: n_c direction reversal undermines Theorem 2's predictive claim
**Issue:** Theorem 2 predicts n_c = α · w · log(F): n_c should increase with width. Table 3 shows the opposite: n_c decreases monotonically from 1,546 (w=32) to 884 (w=128).
**Location:** Theorem 2 (Section 3.3), Table 3 (Section 5.2), Figure 3 (Section 5.4)
**Severity:** 4/5 — This is the paper's central empirical finding but it directly contradicts the theorem it claims to validate. The paper reframes this as "refinement" via F_eff(w), but this is a post-hoc rationalization, not a derivation.
**Resolution:** Either (a) derive F_eff(w) from first principles before presenting it as a resolution, or (b) acknowledge that Theorem 2 requires modification and present the refined formula as the main theoretical contribution.

### W2: F_eff(w) introduced without derivation
**Issue:** Equation 8 (Section 3.3) introduces F_eff(w) = F · (w/w_0)^(−γ) to reconcile the reversed n_c direction. No derivation from the CRISP framework is provided. The text explicitly concedes: "We leave the derivation of F_eff(w) from first principles to future work." This is curve-fitting with an extra free parameter (γ).
**Location:** Section 3.3, paragraph "Reconciling theory with data"; Discussion Section 6
**Severity:** 4/5 — A theory that cannot predict the direction of its primary observable's dependence on its main parameter is not a predictive theory.
**Resolution:** Derive F_eff(w) from the CRISP energy landscape. The dependence of effective feature count on width is a substantive question that deserves a substantive answer.

### W3: n_eff(t) conjecture is central but undefined and unvalidated
**Issue:** The connection between Theorem 1 (static phase transition) and grokking (dynamic phenomenon) relies on n_eff(t)—an effective dataset utilization that increases with training steps. The paper acknowledges this is a conjecture ("We do not prove this conjecture formally"). Critically, n_eff(t) is never defined quantitatively, never computed from the experiments, and no evidence is provided for its monotonicity claim.
**Location:** Section 3.2, paragraph "Connection to grokking"
**Severity:** 3/5 — Without n_eff(t), Theorem 1 does not actually explain grokking. The paper presents a static phase transition as if it explains a dynamic phenomenon, but the link is assumed rather than proven.
**Resolution:** Either define n_eff(t) precisely (e.g., as accumulated Fisher information, effective parameter count, or similar) and validate it against the grokking delay data, or reframe the paper as demonstrating compatibility between static phase transitions and dynamic grokking rather than deriving the latter from the former.

### W4: Corollary 1 (β → 2/3) not validated empirically
**Issue:** Corollary 1 claims that in the large-width limit, the scaling exponent β → 2/3. The paper never fits a power law to its scaling curve (Figure 5) to estimate β. The prediction appears without empirical support, and the relationship to actual neural scaling law literature (Kaplan et al. 2020 report β ≈ 0.076–0.076 for language models) is not discussed.
**Location:** Section 3.3, Corollary 1; Figure 5 (scaling law curve)
**Severity:** 3/5 — The corollary is presented as a major theoretical contribution but the implied prediction (β = 2/3) is neither measured in the experiments nor connected to the empirical scaling law literature.
**Resolution:** Fit β from the mod-47 data and compare to 2/3, or explicitly note that testing this prediction requires larger-scale experiments beyond the scope of the paper.

### W5: Theorem 2 proof sketch contains handwavy steps
**Issue:** The proof sketch in Section 3.3 states that solving the critical condition yields n_c ≈ (γ/(λc)) · w · log F. But c (defined as the constant in σ² ≈ c/w) is never specified, and the step from Eq. 716 to Eq. 720 in Appendix A requires c to cancel exactly in a way that depends on assuming the interference cost scales as Fnum²/w. This requires specific frame geometry assumptions that are stated as approximate. The "complete derivation" in Appendix A was not provided in the main text proof sketch.
**Location:** Theorem 2 proof sketch; Appendix A, proof of Theorem 2
**Severity:** 3/5 — The proof is not fully rigorous as written. The gap between "proof sketch" and the actual derivation in the appendix needs more explicit linking.
**Resolution:** Tighten the proof sketch to explicitly state each assumption and why it holds for the mod-47 setting.

### W6: Missing engagement with lottery ticket hypothesis and sparse training literature
**Issue:** The paper does not cite or engage with the lottery ticket hypothesis (Frankle & Carbin, ICLR 2019) or the broader iterative magnitude pruning literature. The finding that wider networks generalize with less data has direct overlap with width-dependent ticket finding thresholds, which the paper should position against.
**Location:** Related Work, Section 2
**Severity:** 2/5 — Niche but relevant for ML/Systems readers who will ask about this connection.
**Resolution:** Add a paragraph in Related Work discussing the relationship between CRISP's phase transition and ticket-finding-threshold dependence on width.

### W7: Figure 5 scaling law knee is asserted but not quantified
**Issue:** Figure 5 shows a scaling curve with a visible knee, but the paper never reports the fitted knee location or compares it against the predicted n_c from Table 3. Without quantification, "the knee aligns with n_c" is a visual assertion.
**Location:** Figure 5, Section 5 (figure caption); Discussion Section 6
**Severity:** 2/5 — The unification claim (grokking threshold = scaling law knee) is the paper's central theoretical promise but is not verified by overlaying the predicted n_c on the empirical knee.
**Resolution:** Fit the knee location from Figure 5 and compare against the n_c values in Table 3.

### W8: F3 decorrelation test results not reported
**Issue:** F3 requires Pearson correlation r > 0.8 between the superposition index drop and grokking onset. Table 1 lists this as a falsification criterion, but the Results section never reports the observed correlation value or shows the PCA-based superposition dynamics for all conditions. Figure 4 is shown but no quantitative correlation is reported.
**Location:** Section 3.3 (F3 criterion); Section 5 (results); Figure 4
**Severity:** 3/5 — The mechanistic claim (superposition → clean) is the paper's core theory but the key evidence for it is missing from the results.
**Resolution:** Report the Pearson correlation across all conditions explicitly. If it fails the r > 0.8 threshold, disclose this.

### W9: Generalization to transformers and natural language is speculative
**Issue:** The paper claims the framework "suggests deriving F_eff(w) from first principles, extending to transformers and larger-scale tasks" as future work. But the theory's assumptions (sub-Gaussian data, F known/estimated, 2-layer MLPs only, w ≤ 128) are so restrictive that extending to transformers is non-trivial. The paper conflates algorithmic tasks (modular arithmetic, where F is known) with natural language (where F is not known).
**Location:** Conclusion Section 7; Discussion Section 6
**Severity:** 2/5 — The scope of the contribution is much narrower than the framing suggests.
**Resolution:** Restructure the framing to present CRISP as a theory for low-dimensional algorithmic tasks rather than a general theory of neural network training dynamics.

### W10: α calibration procedure undermines predictive test
**Issue:** The text states α is "calibrated empirically at a single reference width (w = 256) and then used to predict n_c at other widths." Since w = 256 is outside the experimental range (32–128), this is effectively calibrating on a different setting. If α is fit per-width, the theory becomes unfalsifiable because you can always adjust α to match any observed n_c.
**Location:** Section 3.3, paragraph "We note that α is a task-family-specific constant"
**Severity:** 4/5 — Predictive theories require out-of-sample prediction. Calibrating on one width and predicting others is valid only if w = 256 is truly held out. The paper does not clarify whether this is a true hold-out or whether α was adjusted until the fit worked.
**Resolution:** Use w = 256 as the reference, fit α from that single width, then predict n_c for w = 32, 48, 64, 96, 128 without adjustment. Report the prediction error explicitly.

---

## 3. Per-Rubric-Dimension Scores

| Dimension | Score | Calibration Anchor |
|-----------|-------|-------------------|
| **Originality / Novelty** | 6 | Substantial conceptual contribution: unifying grokking and scaling laws via phase transitions is a novel framing. However, the superposition mechanism is directly from Elhage et al. 2022, and phase transitions in learning were established by Saxe et al. 2014 and Goldt et al. 2020. The contribution is best described as an extension of existing ideas rather than a new paradigm. |
| **Soundness** | 5 | The theory makes a specific quantitative prediction (n_c ∝ w) that is contradicted by data. F_eff(w) is introduced as a post-hoc reconciliation without derivation. n_eff(t) is a central conjecture that is undefined and unvalidated. The proof sketches are suggestive but not rigorous enough for a field-standard methodology. The 0/51 F2 result is strong but the overall theory-data agreement is weak. |
| **Significance** | 6 | If correct, the phase-transition mechanism for grokking would be important within the grokking/superposition subfield. The practical compute-budgeting implication (training at 1.2–1.5 n_c is efficient) is useful. However, restricted to 2-layer MLPs on modular arithmetic; the path to transformers and language is speculative. |
| **Clarity** | 8 | Well-organized, well-written, with detailed appendix proofs. The four contributions are clearly stated. Figures are clear and captions are informative. The theoretical framework is laid out in stages. |
| **Reproducibility** | 9 | Full code, 120-run JSON logs, hyperparameter tables, seeds, and a 30-minute A100 runtime. This is exemplary reproducibility. |
| **Contextualization vs prior work** | 5 | Cites Power et al. 2022, Nanda et al. 2023, Liu et al. 2023, Thilak et al. 2022 for grokking. Cites Kaplan et al. 2020, Hoffmann et al. 2022, Caballero et al. 2023, Bahri et al. 2024 for scaling laws. Cites Elhage et al. 2022 for superposition. Notable omissions: lottery ticket hypothesis (Frankle & Carbin, ICLR 2019) given width-dependent generalization parallels; the phase-transition-in-learning literature (Saxe et al. 2014, Goldt et al. 2020) is cited but under-integrated. The Milman & Schechtman 1986 citation for the log(F) dependence is eccentric—the standard reference for high-dimensional sphere packing is the Johnson-Lindenstrauss lemma or covering number results, not an asymptotic normed spaces text. |
| **Ethical / Broader Impact** | 7 | Standard boilerplate broader impact statement. Adequate but not thoughtful—does not discuss the implications of the theory for practitioners designing training pipelines, or the implications for the emergent abilities debate beyond citing Schaeffer et al. 2024. |

**Weighted average:** (6×1.0 + 5×1.5 + 6×1.0 + 8×0.7 + 9×1.0 + 5×0.8 + 7×0.5) / 6.5 = (6 + 7.5 + 6 + 5.6 + 9 + 4 + 3.5) / 6.5 ≈ 41.6 / 6.5 ≈ **6.4 → Borderline**

---

## 4. Pointed Questions for Authors

1. **n_eff(t) is the linchpin of your theory but is never defined or measured.** Can you specify n_eff(t) quantitatively (e.g., as accumulated Fisher information, effective parameter count, or similar)? What would it mean for your theory if n_eff(t) plateaus before reaching n_c? Is there any empirical evidence from the training curves that n_eff(t) is monotonically increasing?

2. **Theorem 2 predicts n_c ∝ w, but Table 3 shows the opposite relationship.** You introduce F_eff(w) = F · (w/w₀)^(−γ) to resolve this, but γ is never fit or validated. Is there any reason to prefer γ > 1 over other functional forms? How would your theory be falsified if n_c turned out to increase with width in a different architecture family?

3. **The decorrelation test (F3) requires r > 0.8 but you never report the actual Pearson correlation.** What is the observed correlation across conditions? If it is below 0.8, what does this imply for the superposition-to-clean mechanism as the解释 of grokking?

4. **You claim β → 2/3 in Corollary 1, but you never fit β from your data.** Figure 5 shows a scaling curve—can you report the fitted β and its standard error? How does your measured β compare to 2/3, and what would it mean if it matched the Chinchilla prediction (β ≈ 0.5 for compute-optimal scaling) instead?

5. **α is calibrated at w = 256, which is outside your experimental range (32–128).** Is this calibration truly out-of-sample, or was it adjusted based on the observed n_c values at other widths? If the latter, the theory is not being predictively tested. Have you considered whether F_eff(w) could absorb the α calibration entirely, making α redundant?

6. **Your theory requires knowing F (the number of latent features).** For modular arithmetic this is exactly 47, but for language models or image classification, F is unknown. How would you estimate F for a task where it is not known a priori? Does your theory make any qualitative predictions that are robust to misestimation of F?

7. **You cite Milman & Schechtman 1986 for the claim that R^w admits exp(Θ(w)) near-orthogonal vectors.** This is an obscure citation for a standard result in high-dimensional geometry. The covering number of the unit sphere and the Johnson-Lindenstrauss lemma are the standard references for this. Why not use those?

---

## 5. Falsifiability Test: What Evidence Would Change My Decision?

**If I believed the paper:** I would want to see (a) F_eff(w) derived from the CRISP energy landscape rather than assumed; (b) n_eff(t) defined and measured, showing its trajectory crossing n_c at the observed grokking delays; (c) the F3 decorrelation test reported quantitatively with r > 0.8; (d) β fitted from Figure 5 and shown to be consistent with the theory's prediction; and (e) α calibrated out-of-sample at w = 256 and shown to predict n_c for w = 32, 48, 64, 96, 128 without adjustment.

**If I did not believe the paper:** The central issue is that Theorem 2's main prediction (n_c ∝ w) is contradicted by the data, and the resolution (F_eff(w)) is added without derivation. If future experiments on a different task (e.g., sparse parity, character-level language modeling) also show n_c increasing with width (contradicting F_eff(w)), the entire F_eff reconciliation collapses. Similarly, if n_eff(t) can be measured and shown not to correlate with grokking delay, the dynamical explanation of grokking fails. If F3 decorrelation is measured and r < 0.5, the superposition mechanism is not supported.

**What would shift my score significantly:** (a) A derivation of F_eff(w) from the theory would move Soundness from 5 to 7. (b) Reporting and passing F3 would move Soundness to 7. (c) Fitting β from Figure 5 and showing it near 2/3 would support the Corollary and move Significance from 6 to 7. (d) Out-of-sample prediction of n_c at different widths using a single calibrated α would be a genuine predictive success.

---

## 6. Confidence

**3/5** — I am confident in my assessment of the empirical results (they are clearly reported and reproducible). I am less confident in my assessment of the theoretical derivations because the proof sketches are suggestive but leave gaps. The n_eff(t) conjecture and F_eff(w) introduction are the most significant concerns, but without access to referee-level discussion with the authors, I cannot determine whether these are fatal or addressable.

---

## 7. Decision

**Borderline**

The paper has a genuine contribution: a well-motivated theoretical framework connecting phase transitions in feature space to grokking and scaling laws, validated on a clean experimental setup with strong reproducibility. The 0/51 sub-critical result is a compelling falsification of the "just train longer" confound, and the sharp 0/1 phase boundary in Table 2 is strong empirical evidence for a threshold effect.

However, the theory's central quantitative prediction is contradicted by data, and the resolution is introduced without derivation. This is not a fatal flaw—the phase-transition reframing of grokking may still be correct even if the specific functional form of n_c requires refinement—but it means the paper's most ambitious claims (C2: closed-form n_c, Corollary 1: β = 2/3) are not adequately supported.

A revised version that: (a) derives F_eff(w) from the CRISP energy landscape, (b) defines and measures n_eff(t), (c) reports the F3 decorrelation quantitatively, and (d) fits β from the data, would be a strong Accept. In its current form, the paper is a Borderline that could become Acceptable with targeted revisions to the theory-data alignment.

---

*— The Domain Expert*
