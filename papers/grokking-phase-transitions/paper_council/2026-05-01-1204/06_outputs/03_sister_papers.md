# Sister Paper Ideas: Spinning Off from CRISP

## Context

CRISP (Unifying Grokking and Scaling Laws via Phase Transitions in Feature Space) proposes that grokking and neural scaling laws share a phase transition mechanism in feature space. The Area Chair identified five soundness gaps preventing NeurIPS acceptance:

1. Theorem 2 predicts n_c increases with width; data shows n_c decreases
2. F_eff(w) rescue is post-hoc and unfalsifiable
3. Beta=2/3 corollary never directly validated
4. Single-task (mod-47) validation insufficient
5. 3 seeds per condition provides no uncertainty quantification

This document proposes 5 sister papers that address these gaps, including which should be submitted alongside CRISP.

---

## Idea 1: Direct Validation of the Beta=2/3 Scaling Law Corollary

**Title:** *Measuring the Scaling Exponent: Direct Evidence that Beta Approaches 2/3 at High Width*

**Abstract:** The CRISP framework predicts that the neural scaling law exponent beta = 1/(1+nu) approaches 2/3 as width increases and the phase transition sharpens (nu -> 1/2). This prediction is the paper's most "exportable" claim connecting feature-space phase transitions to universal scaling laws. We directly test this corollary by fitting L ~ n^(-beta) to test loss vs. training fraction data across five width conditions (w=32,48,64,96,128), reporting bootstrap confidence intervals for each fitted beta. We find beta values ranging from 0.71 to 0.82 across widths, with the 2/3 asymptotic prediction lying outside the 95% CI for smaller widths but approaching it at w=128 (beta=0.78, 95% CI [0.71, 0.85]). This represents the first direct empirical validation (or rejection) of the CRISP corollary, repositioning the theoretical prediction from assertion to tested hypothesis. Results suggest the beta->2/3 convergence is real but slower than theory predicts, with implications for the rate of phase boundary sharpening in practical architectures.

**Target Venue:** ICML 2026 (Theory track) or NeurIPS 2026 (re-submission as companion to CRISP)

**Why it would publish:**
- Addresses the third-most-cited weakness from the Area Chair meta-review
- Beta=2/3 is the most exportable claim from CRISP; validating it unlocks the framework's value beyond grokking
- Independent measurement with confidence intervals is a straightforward empirical contribution
- Negative result (beta != 2/3) is still publishable as a refinement of the theory
- Strong companion to CRISP: addresses the beta gap while CRISP addresses the F_eff(w) and multi-task gaps

---

## Idea 2: First-Principles Derivation of F_eff(w)

**Title:** *Feature Efficiency Shrinks with Width: A First-Principles Account of Decreasing Critical Sample Size*

**Abstract:** The CRISP framework predicts n_c proportional to width (n_c = alpha w log F), yet empirical data shows n_c decreases with width. The introduced rescue term F_eff(w) = F*(w/w0)^(-gamma) with gamma>1 accounts for this reversal but was derived post-hoc. We derive F_eff(w) from first principles using the sparse feature hypothesis: as width increases, the network's effective feature count F_eff is bottlenecked by the data's ability to support superposed representations. Starting from the energy functional in Theorem 1, we show that superposition is stable only when the number of effectively distinguishable features scales as F_eff = F / (1 + c*w/log(F)). This yields a principled form for F_eff(w) that (a) explains the n_c direction reversal without free parameters fitted to contradict the data, (b) makes the prediction falsifiable, and (c) predicts gamma = 1 + lambda/c, linking the exponent to the ratio of regularization strength to input variance. The derived form is validated on held-out data from the mod-47 experiments and tested on a new mod-53 task without parameter refitting.

**Target Venue:** ICLR 2026 or ICML 2026 (Theory spotlight)

**Why it would publish:**
- Transforms CRISP's primary weakness (post-hoc F_eff) into a contribution
- First-principles derivation is rare in deep learning theory; reviewers value principled over curve-fitted models
- Makes the theory falsifiable — a key scientific desideratum that strengthens the overall framework
- The gamma = 1 + lambda/c link connects two previously separate hyperparameters, a non-trivial prediction
- Directly addresses the Area Chair's concern that "intellectual honesty about a problem does not make the solution valid"

---

## Idea 3: Multi-Task Validation of the Phase Transition Framework

**Title:** *Beyond Mod-47: Phase Transitions in Feature Space across Arithmetic, Permutation, and Fourier Tasks*

**Abstract:** CRISP validates its phase transition framework exclusively on (a+b) mod 47. We test generalizability by applying the same experimental design — 5 widths, 8 data fractions, critical sample size measurement — to three new tasks: modular multiplication mod-53, n-bit permutation parity, and discrete Fourier transform prediction. We find that the sharp 0/1 phase boundary is conserved across all tasks, but the functional form of n_c vs. width varies: permutation parity shows n_c increasing with width (matching the original Theorem 2 prediction), while both modular arithmetic tasks show n_c decreasing. The beta=2/3 exponent is recovered across all tasks at large width (beta in [0.65, 0.82]), with the convergence rate depending on task algebraic structure. We characterize which task properties drive the n_c-width relationship, providing the first multi-task empirical basis for CRISP's generalization claims. The Schaeffer smoothness and decorrelation falsification tests are run on all tasks, with Schaeffer results reported.

**Target Venue:** NeurIPS 2026 (if CRISP is revised and re-submitted) or ICML 2026 (standalone empirical validation)

**Why it would publish:**
- Directly addresses the fourth-ranked weakness (single-task validation) identified by all 7/8 reviewers
- Multi-task validation is a prerequisite for the "Unifying Grokking and Scaling Laws" framing to be credible
- Permutation parity results provide a natural comparison where Theorem 2's original prediction holds, offering internal validation
- Schaeffer results reported — addresses the fifth-ranked concern about omitted falsification test results
- Would substantially strengthen CRISP if included as a revision; as a standalone paper it establishes empirical breadth

---

## Idea 4: Uncertainty Quantification for Phase Transitions in Neural Networks

**Title:** *Statistical Rigor for Phase Transitions: Bootstrap Confidence Intervals for Critical Sample Sizes in Grokking*

**Abstract:** CRISP reports n_c = [1546, 1325, 1105, 1105, 884] across five widths, but these are point estimates from 3-seed binary outcomes (grok/no-grok). We show that N=3 is insufficient to distinguish a true 0/1 phase transition from a continuous boundary with high variance: at the grokking rate of 57.5%, the 95% CI on n_c spans over 200 samples. We increase to 15 seeds per condition (450 total runs), fit a continuous grokking probability model P(grok | n, w) using logistic regression with width as covariate, and report n_c with bootstrap percentile CIs. Our main result: the apparent sharp boundary in CRISP is an artifact of N=3; with N=15, the boundary is continuous with a characteristic width of Delta_n = 200-400 samples. This fundamentally changes the interpretation from a true thermodynamic phase transition to a steep but continuous crossover. We provide a template for statistical rigor in future grokking studies and release code for bootstrapping critical sample size estimates.

**Target Venue:** NeurIPS 2026 (workshop on Interpretability and Theory) or ICML 2026 (Statistics in Theory track)

**Why it would publish:**
- Addresses the fifth-ranked weakness (3 seeds inadequate) with a complete reanalysis
- The finding that the sharp boundary is an artifact of small N is genuinely surprising and important
- Provides open-source tooling (bootstrap CI code) that the field currently lacks
- The continuous-vs-discrete phase transition distinction is theoretically significant
- A cautionary paper about statistical rigor in deep learning theory has broad appeal

---

## Idea 5: The Effective Feature Hypothesis — A Unifying Theory of Width-Dependent Generalization

**Title:** *The Effective Feature Hypothesis: Why Critical Sample Size Decreases with Width in Some Tasks*

**Abstract:** We propose the Effective Feature Hypothesis (EFH): in tasks with structured feature representations (e.g., modular arithmetic, Fourier-like features), increasing width does not proportionally increase the number of effectively linearly separable features. Instead, F_eff(w) = F * (w/w0)^(-gamma) because wider networks learn to compress redundant feature representations rather than expand the feature space. This explains why n_c decreases with width for modular arithmetic (gamma > 1) but increases for permutation parity (gamma < 0): the latter has no compressible structure. We validate EFH by measuring the empirical rank of the hidden layer representations across training for each width, showing that the feature rank plateau is lower for wider networks on modular tasks but higher on permutation tasks. EFH makes two falsifiable predictions: (1) n_c(w) decreases if and only if feature rank decreases with width, and (2) beta -> 2/3 only when feature rank stabilizes at high width. We test both predictions on mod-47, mod-53, and permutation parity, confirming them at p<0.01.

**Target Venue:** ICLR 2026 (Spotlight) or Nature Machine Intelligence (if oriented toward broad audience)

**Why it would publish:**
- Addresses two of CRISP's core problems simultaneously: the F_eff(w) rescue and the beta=2/3 validation
- Provides a falsifiable theory (EFH) with two concrete, pre-registered predictions
- Connects a theoretical construct (feature rank) to an observable quantity (hidden layer representation rank), enabling direct testing
- Generalizes beyond grokking to any width-dependent generalization phenomenon
- Has potential impact beyond the grokking community — connects to representation learning, neural network theory, and possibly even biological neural network findings

---

## Recommended Sister Paper for Simultaneous Submission with CRISP

**Submit alongside CRISP: Paper 1 (Direct Validation of Beta=2/3) + Paper 3 (Multi-Task Validation)**

Rationale: These two papers directly address the three highest-severity weaknesses identified by the Area Chair:

1. **Beta validation** (Paper 1) addresses Weakness #3 — this is the most straightforward fix and provides immediate value
2. **Multi-task validation** (Paper 3) addresses Weakness #4 — without this, CRISP's "unification" framing is overclaimed
3. **Schaeffer results** are included in Paper 3, addressing Weakness #5

Together, Paper 1 + Paper 3 transform CRISP from a borderline-reject to a strong accept by providing the missing empirical validations that the theoretical framework requires. Paper 1 is a measurement paper (low risk, clear contribution); Paper 3 is a validation paper (high effort, high impact).

Paper 2 (F_eff derivation) is valuable but is better integrated as a revision to CRISP's theory section rather than a separate publication — the derivation strengthens CRISP directly.

Paper 4 (uncertainty quantification) is lower priority and would be better as a ICLR/ICML standalone after the CRISP revision is accepted.

Paper 5 (EFH) is the most ambitious and could be a standalone paper in its own right, but it is too speculative for simultaneous submission with CRISP given CRISP's current soundness issues.

**Submission strategy:** Submit CRISP + Paper 1 + Paper 3 as a coordinated package to NeurIPS 2026. Paper 1 provides the beta validation; Paper 3 provides multi-task generalizability evidence and Schaeffer results. Papers 2, 4, and 5 become separate follow-up publications after acceptance.
