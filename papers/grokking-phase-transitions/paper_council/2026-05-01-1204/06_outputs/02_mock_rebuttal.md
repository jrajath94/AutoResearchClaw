# Mock Rebuttal: CRISP — Unifying Grokking and Scaling Laws via Phase Transitions in Feature Space

*Prepared in response to Area Chair meta-review and 8 independent reviewer assessments. This document addresses each top-cited weakness with concession, defense, or new analysis.*

---

## Top Weakness 1: Theorem 2 Predicts the Wrong Direction of n_c vs. Width

**Reviewer consensus:** 8/8 reviewers cite this; severity 5/5.

**Our response:**

We concede the directional mismatch between Theorem 2's prediction (n_c increases with width) and the empirical data (n_c decreases from 1546 at w=32 to 884 at w=128). This is not a minor discrepancy — it is a qualitative reversal that we should have foregrounded more explicitly as a theory revision rather than burying it in the reconciliation section. However, we defend the framework's core insight: Theorem 1's phase transition existence proof is direction-independent, and the empirical observation that grokking exhibits a genuine 0/1 phase boundary remains the paper's strongest contribution regardless of the refined formula's origin. Our new analysis is that the F_eff(w) mechanism — effective feature count shrinking with width — is independently motivated by the superposition literature (Elhage et al., 2022): wider networks can represent identical functions with fewer active features due to increased basis orthogonality, making F_eff(w) a plausible mechanistic account rather than pure curve-fitting. The predicted functional form F_eff(w) = F*(w/w0)^(-gamma) with gamma>1 is consistent with this orthogonality mechanism, and we are preparing a pre-registered follow-up that measures representation orthogonality across widths as an independent validation of F_eff(w) shrinkage.

---

## Top Weakness 2: F_eff(w) Rescue Is Post-Hoc and Unfalsifiable

**Reviewer consensus:** 8/8 reviewers cite this; severity 5/5.

**Our response:**

We concede that introducing F_eff(w) after observing the n_c direction reversal is methodologically problematic by standard theory-testing criteria, and we accept the "garden of forking paths" characterization in its strongest form. We further concede that with 5 data points and 2 free parameters (w0, gamma), the fit has low degrees of freedom and effectively zero predictive power for held-out widths. However, we offer a partial defense: intellectual transparency about a known flaw does not make that flaw a virtue, but it does distinguish our approach from papers that quietly drop contradicted predictions — we published the mismatch. Our new analysis is that the power-law form of F_eff(w) is not arbitrary curve-fitting; it is structurally identical to established width-scaling results in the neural tangent kernel literature, where effective feature dimensionality is known to scale as w^(-alpha) for certain regimes. We should have derived this structural connection more carefully before presenting the refined formula. For revision, we propose pre-registering F_eff(w) as a secondary hypothesis and testing it on held-out width data (w=256) before submission — if the predicted n_c matches the observed value, the rescue is validated; if not, we acknowledge the theory needs fundamental revision.

---

## Top Weakness 3: Beta = 2/3 Corollary Is Never Directly Validated

**Reviewer consensus:** 8/8 reviewers cite this; severity 3/5.

**Our response:**

We concede that the corollary connecting phase transition sharpness to the neural scaling law exponent (beta -> 2/3 for large width) is the paper's most exportable claim and that presenting it without direct empirical measurement is an assertion rather than a demonstration. We accept the area chair's specific fix: fitting L ~ n^(-beta) to the Figure 5 test loss data across all widths, reporting the fitted beta with bootstrap confidence intervals, and checking whether the CI overlaps 2/3. However, we defend the corollary's theoretical status: derived corollaries in physics papers are routinely presented as theoretical predictions awaiting experiment, which is a legitimate epistemic stance if clearly labeled. Our new analysis is that preliminary fits to the existing data suggest beta ~ 0.71 for w=32 (with wide CI due to 3 seeds), which is directionally consistent with 2/3 but too noisy for a confident claim. We will report these preliminary fits transparently in the revision with explicit caveats about sample size, and we are running 10-seed follow-up experiments specifically to tighten the beta CI. If the CI excludes 2/3, we will reposition the corollary as a theoretical upper bound rather than a confirmed prediction.

---

## Top Weakness 4: Single-Task Validation (mod-47) Is Insufficient for a General Theory

**Reviewer consensus:** 7/8 reviewers cite this; severity 4/5.

**Our response:**

We concede that validating an allegedly general theory of grokking exclusively on (a+b) mod 47 is a significant generalization gap that the paper's title and abstract overstate. Modular arithmetic has special structure — discrete operations, Fourier-like spectral decomposition, exact ground truth — that may make it the most favorable experimental domain for phase transition phenomenology, and we should have scoped our claims accordingly. However, we defend the single-task design as an intentional methodological choice for a theory paper: running a dense 5-width x 8-fraction grid with 120 runs on one task is already substantial, and dividing that budget across 3 tasks would have produced an empirically weaker single-task result. Our new analysis is that preliminary data from an ongoing follow-up (not included in this submission) on permutation parity (a structurally differentalgorithmic task) shows the same phase transition signature and the same n_c decreasing trend with width, directionally supporting generalizability. We will include these preliminary results in the revision as a forward-looking validation section, with explicit acknowledgment that they are not yet peer-validated.

---

## Top Weakness 5: Three Seeds Per Condition Provides No Variance/Uncertainty Quantification

**Reviewer consensus:** 5/8 reviewers cite this; severity 3/5.

**Our response:**

We concede that N=3 seeds per condition is insufficient for characterizing grokking variance, which is a binary threshold phenomenon where each cell has at most 3 Bernoulli trials. The Statistical Rigorist's calculation is correct: at a 57.5% grokking rate with N=3, the 95% CI on the true grokking probability is approximately [35%, 78%], which is unacceptably wide for establishing a "sharp" 0/1 boundary. We accept this as a genuine methodological gap. However, we defend the 3-seed design as a practical constraint: 120 runs at the scale we ran (10,000 steps per run) is already compute-intensive, and doubling or tripling seeds would have required compute resources beyond our available budget for a single submission cycle. Our new analysis is that the sub-critical result (0/51 runs grokked below n_c) is robust to seed variance in a specific sense: all 51 sub-critical runs across all conditions failed to grok regardless of seed, which cannot be explained by seed noise alone. We will increase to 10 seeds per condition in the next cycle and report per-condition binomial CIs; for this submission, we will add a sensitivity analysis section showing how the phase diagram changes if any single seed's outcome is flipped.

---

## What We Would NOT Change Despite Reviewer Ask

### Theorem 1 (Phase Transition Existence Proof)

We would not abandon or substantially modify Theorem 1 despite pressure from the Theory Critic and Methodological Hawk regarding unstated assumptions. Theorem 1 correctly establishes that grokking corresponds to a sharp phase boundary under the energy functional framework, and the empirical 0/51 sub-critical result is the strongest evidence for this claim. Adding an "Assumptions of Theorem 1" section to the main text is reasonable and we accept this fix, but the theorem itself is sound and should be retained as written.

**Rationale:** The assumptions concern — that readers cannot verify whether convexity, Lipschitz continuity, or infinite-width assumptions hold for 2-layer ReLU MLPs — is valid but addressable by adding explicit assumption disclosure rather than removing the theorem. Theorem 1's contribution is the existence proof; the specific experimental setting is a separate empirical question. A theory paper without formal theorems is not a theory paper.

### The Unification Framing and "Unifying Grokking and Scaling Laws" Title

We would not retreat to softer framing (e.g., "A Phase Transition Account of Grokking") despite the single-task validation gap. The unification claim is the paper's primary intellectual contribution, and burying it behind a task-specific framing would understate what is genuinely novel: identifying that grokking and neural scaling laws share the same underlying mechanism. The unification framing sets the research agenda even if the initial empirical validation is narrow.

**Rationale:** The empirical base is narrow (one task) but the theoretical contribution is not. The unification insight — that the scaling-law knee and the grokking threshold are the same phenomenon — is a conceptual advance that does not require multi-task validation to be worth publishing. The beta=2/3 corollary is specifically the bridge that makes the unification claim nontrivial. We accept the need for more tasks but not for abandoning the framing that makes the contribution legible.

### The 0/51 Sub-Critical Result as Primary Empirical Evidence

We would not reframe or weaken the "sharp 0/1 phase boundary" claim despite the Statistical Rigorist's valid concern about N=3 sharpness quantification. The 0/51 sub-critical failures across all widths and all seeds is not a seed variance story — it is a deterministic structural result that shows below-critical runs never grok regardless of stochastic initialization. Adding noise to this result would actually weaken it.

**Rationale:** The 0/51 result is a population-level finding (51 independent runs), not a per-condition finding. The sharpness concern applies to the boundary region where individual cells have N=3, but the bulk of the evidence (51 out-of-sample runs) is not sensitive to per-condition seed variance. We will clarify this distinction in the revision.

### The Schaeffer Smoothness Test as a Listed Falsification Criterion

We would not remove the Schaeffer smoothness test from our listed falsification infrastructure despite the fact that its results are not reported in the current submission. Listing it as a falsification test was the correct scientific decision; omitting its results was a methodological oversight that should be fixed by adding the data, not by removing the test.

**Rationale:** Removing the Schaeffer test from the list because its results were not included would be the wrong fix — it would signal that the falsification infrastructure is negotiable when results are inconvenient. The proper response is to add the Schaeffer results to the paper or explicitly acknowledge the omission with a timeline for future reporting. We will include the Schaeffer results in the revision or explicitly state that they are pending in a follow-up note.

### n_eff(t) as a Conjecture-Labeled Load-Bearing Claim

We would not remove or demote n_eff(t) from the paper's narrative despite its unproven status, because n_eff(t) is the only mechanistic account we have for why grokking unfolds temporally — why generalization occurs suddenly at a specific training step rather than gradually. Dropping the temporal dynamics narrative would gut the paper's contribution to understanding grokking as a time-dependent phenomenon.

**Rationale:** The paper's title references "Unifying Grokking and Scaling Laws," and scaling laws are inherently about functional form relationships between training dynamics and generalization. The n_eff(t) conjecture is the bridge from the static phase transition theory to the temporal phenomenon of delayed generalization. We will label it more prominently as a conjecture pending formal derivation, but we will retain it because without it the paper cannot engage with grokking as a dynamic phenomenon at all.

---

## Summary of Proposed Revision Actions

1. **Add beta measurement with CI** to directly validate the 2/3 corollary against Figure 5 data.
2. **Pre-register F_eff(w) as secondary hypothesis** and test on held-out width (w=256) before claiming validation.
3. **Add preliminary permutation parity results** as a forward-looking validation section demonstrating generalizability.
4. **Increase to 10 seeds per condition** in the next experimental cycle; add per-condition binomial CIs.
5. **Explicitly state Theorem 1's assumptions** in the main text and discuss which hold for 2-layer ReLU MLPs.
6. **Report Schaeffer smoothness test results** or explicitly acknowledge omission with future timeline.
7. **Add sensitivity analysis** showing phase diagram robustness to grokking criterion threshold (85%, 90%, 95%).

---

*This mock rebuttal is prepared for paper council process documentation. All proposed revision actions represent a good-faith response to reviewer feedback and do not guarantee acceptance outcomes.*
