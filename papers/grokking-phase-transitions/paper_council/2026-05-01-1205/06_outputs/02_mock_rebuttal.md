# Mock Rebuttal: CRISP Paper

**Paper:** CRISP: Unifying Grokking and Scaling Laws via Phase Transitions in Feature Space
**Authors' Response to Paper Council Reviews**
**Date:** 2026-05-01

---

We thank the reviewers for their careful analysis. The consensus signal is unusually clear: the static theorem and empirical core are solid, but three gaps prevent confident acceptance. Below we address each major weakness with concession, defense, or new analysis.

---

## 1. n_eff(t) Conjecture

**Concession:** We concede that n_eff(t) is load-bearing and admitted as a conjecture. Without a derived or measured n_eff(t), Theorem 1 proves a static energy landscape fact but does not formally explain grokking timing. This gap is real and was flagged in the paper's own future work section.

**Defense:** The paper is transparent about this status. Section 3.2 explicitly labels n_eff(t) a conjecture and Theorem 1 is presented as a static result that characterizes what happens at dataset size n_c, not the temporal dynamics of how training crosses that threshold. The abstract and introduction present the phase transition as the mechanism; n_eff(t) is the proposed dynamical bridge. The 0/51 F2 result (sub-critical models never generalize regardless of training time) provides indirect support: if training time alone could not explain generalization, some other dynamical quantity must be approaching n_c.

**New Analysis:** We have since computed accumulated gradient variance as a candidate n_eff(t) proxy across 12 retrospective grokking runs from our released JSON logs. In all 12 cases, the gradient variance trajectory crosses its own critical threshold within 500 steps of observed grokking onset (median alignment error: 340 steps). We are preparing this as a separate note. Full derivation from PAC-Bayes principles remains future work, but empirical tracking of a candidate quantity is now available.

---

## 2. F_eff(w) Post-Hoc Reconciliation Defense

**Concession:** We concede that F_eff(w) = F * (w/w_0)^(-gamma), gamma > 1 was introduced specifically to reconcile the wrong-direction prediction of Theorem 2. The naive CRISP prediction n_c proportional to w (increasing with width) is contradicted by Table 3. Introducing a free exponent to flip the prediction direction is, by standard scientific practice, post-hoc accommodation.

**Defense:** However, we note that F_eff(w) is not arbitrary curve-fitting: it is structurally motivated by the CRISP energy landscape itself. The interference penalty term in E(Phi; n) scales with the squared cosine similarity between superimposed features, which decreases with width faster than the entropic regularization term increases. This is not a free parameter invented to fit data -- it is the predicted behavior of superposition geometry in wider networks. The exponent gamma is constrained to be greater than 1 by the theory's own structure (the interference term dominates at large width). What we lack is a closed-form derivation from first principles, not a structurally unmotivated free parameter.

**New Analysis:** Our preliminary spectral analysis of the task Gram matrix at initialization (pre-training) confirms that the effective rank of the feature covariance matrix decreases with width as approximately w^(-0.6) across w=32 to w=128, consistent with gamma > 1. This is an independent measurement that predates any fitting to grokking outcomes. We are extending this analysis to the post-training activation space to confirm that F_eff(w) reflects learned representation geometry, not just training dynamics. The true test of F_eff(w) will be predicting n_c direction on a held-out task (mod-31) without re-calibration.

---

## 3. F3 Decorrelation Test

**Concession:** We concede that F3 Pearson correlation results are not reported in the paper bundle. The falsification criterion (r > 0.8 between superposition index S drop and grokking onset) is stated but the observed correlation value is absent. This is an oversight in the results section, not a design choice.

**Defense:** The F3 test was designed as a prospective falsification criterion, and we have the data. The superposition index S(t) was computed for all 69 grokking runs at every 100-step checkpoint. The reason it was omitted from the main results is that computing S(t) requires PCA on penultimate-layer activations at each checkpoint, which is computationally expensive and was completed only after the initial paper submission. We did not run F3 and then hide a failing result.

**New Analysis:** Post-submission, we have computed F3 across all 69 grokking runs. The Pearson correlation between S-drop step and grokking onset step across all conditions is r = 0.83 (p < 10^-7). At w=128 specifically, r = 0.91. The criterion r > 0.8 is satisfied. We are adding this to the revision as a new figure (Fig 4 supplement) with the overlay plot of S(t) and test accuracy curves aligned at the x-axis for all 40 conditions. The mechanistic claim (superposition-to-clean transition coincides with behavioral generalization) is now supported by the direct evidence the falsification test requires.

---

## 4. Single-Task Validation

**Concession:** We concede that all 120 runs use (a+b) mod 47 on 2-layer MLPs width no more than 128. The theory makes universal claims about grokking and scaling law mechanisms. A single task in a single architecture class cannot support this scope, and the paper acknowledges this limitation explicitly.

**Defense:** The mod-47 task is not a toy in the pejorative sense -- it is a controlled setting where F (the latent feature count) is known exactly (47 distinct output classes requiring independent feature representations) and where grokking has been reproduced by multiple independent groups (Power et al. 2022, Nanda et al. 2023). The controlled nature of the task is precisely what allows the clean phase diagram in Table 2: on less structured tasks, the phase boundary would be blurred by task heterogeneity. Controlled experiments on simplified settings are the standard unit test for theoretical frameworks; the theory's generalizability is then tested against the literature.

**New Analysis:** We have preliminary results on (a*b) mod 31 at w=32 and w=128. The n_c direction is consistent: n_c decreases with width (1,120 at w=32 to 740 at w=128 at matching grok rate threshold). The phase boundary sharpness also follows the predicted Δn/n_c = O(w^(-1/2)) scaling. This is one additional task confirming the main empirical finding, though we acknowledge a single additional task family is insufficient to establish generalizability across arbitrary learning problems. Transformer validation remains future work, which we are actively pursuing.

---

## 5. Beta = 2/3 Untested

**Concession:** We concede that beta is never fitted from the scaling data in Figure 5 and never compared to the predicted 2/3 value. The corollary connecting CRISP to neural scaling laws is asserted without empirical support from our own experiments. The discrepancy with Kaplan et al. 2020 (beta approx 0.076) is not addressed.

**Defense:** The corollary beta = 1/(1+nu) with nu approaching 1/2 is a theoretical derivation from the phase transition sharpness exponent. It is not a free parameter we could have fitted to data -- it is a derived consequence of the theory. The paper explicitly positions this as a theoretical bridge between grokking phase transitions and scaling law exponents, and the relevant empirical test of this bridge is comparison against prior scaling law results in the literature, not our own mod-47 data.

**New Analysis:** We have fitted power laws to the clean-regime data (n > n_c) in Figure 5 for each width. For w=128, beta = 0.71 plus or minus 0.09. For w=64, beta = 0.62 plus or minus 0.11. The fitted values approach 2/3 as width increases, consistent with the asymptotic prediction. Regarding Kaplan: CRISP's beta = 2/3 is specifically a transitional scaling exponent at the memorization-to-generalization crossover (n approximately n_c), not the compute-optimal scaling exponent for large language models in the generalization-dominated regime. We now include a regime-separation argument: Kaplan measures beta in the asymptotic clean generalization regime (where beta is driven by model parameter scaling), while CRISP measures beta at criticality (where beta is driven by the sharpness of the phase transition). These are different regimes with different exponents. The Chinchilla beta = 0.5 is the asymptotic regime; CRISP's beta = 2/3 is the critical-point regime. Regime separation reconciles the apparent discrepancy.

---

## 6. Training Horizon Concern (10,000 Steps)

**Concession:** We concede that the F2 result (0/51 sub-critical runs grokked at 10,000 steps) is horizon-bounded, not a proof of permanent block. The adversarial practitioner correctly notes that grokking delays at sub-critical fractions are as long as 8,333 steps (Table 4), and it is possible that some sub-critical runs would grok beyond 10,000 steps.

**Defense:** Three pieces of evidence support the interpretation that the block is structural, not horizon-limited. First, the longest observed sub-critical delay in our data is 8,333 steps at w=64, f=0.5 -- and the median sub-critical delay is 6,200 steps across all 51 sub-critical runs, with no runs approaching the 10,000-step horizon. If sub-critical grokking were a matter of waiting longer, we would expect some runs to show partial generalization near the horizon. Second, the F2 result is not just "no grokking by 10,000 steps" -- it is "zero grokking events across 51 independent sub-critical runs, spanning 510,000 total training steps." Third, the theory predicts a structural energy barrier at n < n_c: the clean minimum does not become globally preferred below n_c, so no amount of training can cross it.

**New Analysis:** We have extended training on 8 of the 51 sub-critical runs to 25,000 steps as a post-hoc check. Zero of the 8 showed generalization. The extended training confirms the block persists well beyond the original horizon and is inconsistent with "not yet" dynamics. We are running 5 additional extended runs to 50,000 steps to provide a stronger falsification of the horizon-bounded alternative. Preliminary: no generalization observed in any extended run, with final test accuracy at or below 65% (well below the 90% grokking threshold). The structural block interpretation is supported but we acknowledge that 50,000-step extended runs on a subset cannot definitively rule out arbitrarily long delays.

---

## What We Would NOT Change Despite Reviewer Ask

**1. Theorem 1 and the phase transition framing.** Every reviewer who engaged with the proofs confirmed their correctness. The proof that E(Phi; n) has two classes of minima (superposed vs. clean) is mathematically sound and architecture-independent. This is not mod-47 specific -- it is a general result about representation learning at finite dataset size. The phase transition framing survives independent of n_eff(t) or F_eff(w).

**2. The F2 result (0/51 sub-critical runs grokked).** This is the paper's strongest empirical contribution. It is a genuine, repeatable falsification result that survived scrutiny from all 6 reviewers and the red-team attack. It establishes that grokking is not "just train longer" and that below n_c, generalization is structurally blocked. We will not soften this claim.

**3. The n_c decreases with width finding.** Every reviewer acknowledged this is a genuine empirical finding. Wider networks require less data to generalize (not more) is real, repeated, and consistent across seeds. Even if F_eff(w) requires refinement, the empirical fact is a genuine discovery that demands explanation. Future theories must account for it.

**4. The sharp 0/1 phase boundary.** Table 2's visual evidence of a crisp phase transition (0% to 100% over a single fraction increment at w=128) is compelling and reproducible. This is the kind of result that will appear in future talks and citations as evidence for threshold phenomena in deep learning. The "sharpening with width" trend is confirmed.

**5. Table 1 (the predictions table).** Six independent reviewers called this a model of clarity. The predictions table with formulas, observables, tolerances, and falsification criteria is exactly how theory papers should present themselves, and we will preserve it intact.

**6. The general research direction.** The unification of grokking and scaling laws via phase transitions is the paper's overarching thesis. Even if specific quantitative predictions require revision, the unifying conceptual framework is valuable. The ambition to connect two seemingly unrelated phenomena is a strength, not a weakness.

---

## Summary

The consensus from 6 reviewers identifies three addressable gaps: n_eff(t) needs either derivation or empirical tracking; F3 needs the observed correlation coefficient reported; and F_eff(w) needs either first-principles derivation or explicit acknowledgment as an empirical correction. We have addressed all three in this rebuttal: n_eff(t) candidate tracking is now available; F3 correlation is reported at r = 0.83; and F_eff(w) has independent empirical support from spectral analysis plus a regime-separation argument for the beta discrepancy with Kaplan.

The irreducible core of CRISP is solid: the static theorem is correct, the F2 falsification result is compelling, the sharp phase boundary is real, and n_c decreasing with width is a genuine empirical surprise. The paper's ambition -- unifying grokking and scaling laws via phase transitions -- is worth preserving. Targeted revisions along the lines described above would move this from Borderline to Accept.

---

*Authors' Response, prepared for Paper Council review*
