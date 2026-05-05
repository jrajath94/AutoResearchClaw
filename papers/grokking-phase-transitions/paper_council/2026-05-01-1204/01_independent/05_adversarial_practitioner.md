# Review — The Adversarial Practitioner

**Paper:** CRISP: Unifying Grokking and Scaling Laws via Phase Transitions in Feature Space
**Persona:** The Adversarial Practitioner (production-skeptical, lab-to-deployment lens)
**Date:** 2026-05-01

---

## Framing Note

I read this paper asking: does this claim survive adversarial conditions — scale, operational variance, and the gap between controlled experiment and deployed artifact? Grokking is a fascinating phenomenon, but I have seen many beautiful lab results in ML die the moment they meet production traffic. My review flags the specific points where this work is fragile, and where I need more evidence before trusting it on the critical path.

---

## Strengths

**S1 — Clean experimental design with pre-registered falsification conditions.** The paper defines grokking as >90% test accuracy by 10,000 steps (Section Experimental Design), runs 120 independent runs across 5 widths and 8 fractions, and includes three explicit falsification tests (Schaeffer smoothness, sub-critical extended training, decorrelation). This is more rigorous than the typical ML paper. The sub-critical result (0/51 runs grokked below threshold) is particularly strong evidence for a sharp phase boundary. *Specific evidence:* Section Results — "0/51 sub-critical runs grokked."

**S2 — Theorem 1 provides genuine theoretical unification.** The claim that grokking corresponds to a superposition-to-clean-feature phase transition (Theorem 1, Appendix A) is a non-trivial conceptual link between two previously distinct phenomena. The proof sketch in Appendix A is structured and falsifiable. *Specific evidence:* Theorem 1 statement and Appendix A proof.

**S3 — Phase diagram is visually and quantitatively compelling.** Figure 2 (phase diagram heatmap) and Figure 3 (critical n_c vs width) show a coherent picture. The sharp 0/1 boundary in the heatmap is exactly what a phase transition prediction should look like, and the authors resist smoothing it. *Specific evidence:* Figure 2 and Figure 3, and the claim of sharp 0/1 boundary in Results.

**S4 — Built-in falsification tests are methodologically mature.** Many theory papers claim falsifiability but never specify what would kill them. CRISP specifies three tests a priori. The Schaeffer smoothness test, in particular, is a meaningful adversarial challenge to the phase transition account. *Specific evidence:* Section Key Claims, Claim 6.

**S5 — Honest reporting of theory-experiment mismatch with attempted reconciliation.** The paper explicitly states that n_c decreases with width (empirical) while Theorem 2 predicts n_c increases with width (theory). This is a serious discrepancy the authors do not paper over — they introduce F_eff(w) to reconcile. I respect that they acknowledged the reversal rather than quietly cherry-picking the match. *Specific evidence:* Results Section: "n_c DECREASES with width — opposite of n_c = α·w·log(F) prediction"; refined formula Section.

---

## Weaknesses

**W1 — Theory-experiment mismatch: n_c direction is reversed, F_eff(w) is post-hoc rationalization.**
- **(a) Issue:** Theorem 2 predicts n_c ∝ w (increases with width). The empirical data shows n_c decreases with width: w=32→1546, w=48→1325, w=64→1105, w=96→1105, w=128→884. This is not a minor discrepancy — it is a qualitative reversal. The reconciliation via F_eff(w) = F·(w/w0)^(-γ) with γ>1 is introduced specifically to flip the sign of the width dependence. This is a textbook post-hoc auxiliary hypothesis.
- **(b) Location:** Results Section, observed n_c values; refined formula Section; Theorem 2 in main text.
- **(c) Severity:** 4/5 — fundamental, but the authors acknowledge it. The reconciliation has not been independently validated and could begfitted to any monotonic dataset.
- **(d) Resolution:** Derive F_eff(w) from first principles before presenting it as a resolution, OR demonstrate that the reconciliation holds on a second, independent task (not just mod-47). The current version reads as if the theory was adjusted to fit the data after the fact.

**W2 — β = 2/3 prediction is never directly validated.**
- **(a) Issue:** The corollary that β = 1/(1+ν) → 2/3 for large width is the paper's primary theoretical prediction connecting to neural scaling laws. It is derived but never directly measured in the paper. No figure or table shows a scaling law fit yielding β ≈ 2/3.
- **(b) Location:** Corollary (main text), Section Results, Figure 5 (scaling law).
- **(c) Severity:** 3/5 — the corollary is a key bridge to scaling law literature, and its non-validation means the main theoretical contribution is asserted, not demonstrated.
- **(d) Resolution:** Fit a power law L ∝ n^(-β) to the data in Figure 5 and report the fitted β with confidence intervals. Show it is consistent with 2/3 within uncertainty.

**W3 — n_eff(t) is marked as a conjecture but used as a load-bearing claim.**
- **(a) Issue:** The paper's central mechanism explanation — that n_eff(t) grows as the network discovers clean features — is explicitly marked as "not formally proven; marked as empirically testable" (Theoretical Results). Yet this conjecture is used to explain grokking dynamics in multiple places (Section Results, Figure 4 caption). A reader cannot evaluate whether the proposed mechanism actually explains the observations.
- **(b) Location:** Theoretical Results section, Figure 4 caption.
- **(c) Severity:** 3/5 — the paper's explanatory power rests on this conjecture, and presenting it as near-certain in the results narrative while marking it unproven in the theory section creates an internal inconsistency.
- **(d) Resolution:** Either (i) run the Schaeffer smoothness test specifically against the n_eff(t) dynamics and report the outcome, or (ii) move the n_eff(t) conjecture to a dedicated future work section and reframe the paper's claims around what is actually proven (Theorem 1, Theorem 2, the phase boundary).

**W4 — Single task (mod-47) with no generalization evidence.**
- **(a) Issue:** The entire empirical base is one task: (a+b) mod 47. The paper's abstract and introduction make broad claims about "grokking" and "scaling laws" as general phenomena. Modular arithmetic is a very specific type of task (discrete, symmetric, low-dimensional input). I have seen many ML phenomena that appear universal in modular arithmetic but fail on anything with continuous inputs or real-world structure.
- **(b) Location:** Abstract, Experimental Design (task description), throughout.
- **(c) Severity:** 4/5 — at NeurIPS, claiming a general theory of grokking from a single arithmetic task is a high-risk bet. The reviewer must ask: does this hold on MNIST? on language modeling? on image classification?
- **(d) Resolution:** Run at least one additional task (e.g., matrix multiplication mod a different prime, or a simple image classification task) and show the same phase transition signature. Even a single confirmatory run on a second task would substantially strengthen the claim.

**W5 — Three seeds is insufficient for characterizing grokking variance.**
- **(a) Issue:** The paper uses 3 seeds per condition (42, 137, 256) for 120 total runs. Grokking is a threshold phenomenon — it either happens or it doesn't — and the boundary between grokking and non-grokking runs is sharp. With only 3 seeds, the estimated grokking probability at the boundary (f_c) is a very coarse estimate (0%, 33%, 66%, 100%). The 57.5% grokking rate reported is almost certainly a boundary effect. There is no reporting of within-condition variance.
- **(b) Location:** Experimental Design (seeds), Results (grokking rate).
- **(c) Severity:** 3/5 — the paper cannot distinguish between a true 50/50 boundary and a deterministic boundary with noisy measurement. This affects how I interpret the "sharpness" of the phase transition.
- **(d) Resolution:** Use at least 10 seeds per condition, especially near f_c. Report the empirical grokking probability curve with error bars near the critical fraction.

**W6 — α calibration is not derived from first principles and varies per task.**
- **(a) Issue:** Theorem 2 gives n_c = α·w·log(F) with α = (σ_x²/2λ)·(1+γ/(λw))^(-1). But the paper acknowledges α is "calibrated per task, not derived from first principles" (Prior Review). The actual fitted α values are never reported in the paper. Without knowing α for mod-47, Theorem 2 is not falsifiable for this task — any value of n_c can be fit by adjusting α.
- **(b) Location:** Theorem 2 statement, Prior Review notes.
- **(c) Severity:** 3/5 — for a paper with "built-in falsification tests," the main theoretical prediction has a free parameter that is not reported or independently determined.
- **(d) Resolution:** Report the fitted α for each width in Table 1 or Appendix B. Show that α is consistent across widths (as the theory predicts) or report the actual fitted values if they vary.

**W7 — The Schaeffer smoothness falsification test is described but results are not reported.**
- **(a) Issue:** The paper lists "Schaeffer smoothness" as one of three falsification tests (Claim 6). However, there is no section or figure reporting whether the Schaeffer test was actually run, and if so, what the outcome was. If it was run and supported the phase transition hypothesis, the result should be in the paper. If it was not run, this is a serious gap.
- **(b) Location:** Claim 6 (main text), Falsification Tests section.
- **(c) Severity:** 4/5 — a paper that advertises three falsification tests and then omits the results of one of them raises the question of whether the omitted test failed.
- **(d) Resolution:** Either (i) report the Schaeffer test results in a dedicated subsection, or (ii) explicitly state in the paper that this test is reserved for future work.

**W8 — Figure 5 (scaling law) is asserted but not fitted.**
- **(a) Issue:** Figure 5 reportedly shows "test loss vs training fraction across widths" (Results Summary). If this is a scaling law plot, it should display a fitted power law with reported β and R². The paper reports no such fit. Without fitting, the claim that the data follows a power law is visual assertion, not quantitative demonstration.
- **(b) Location:** Figure 5 caption and description.
- **(c) Severity:** 2/5 — this is a straightforward analysis the authors could have included.
- **(d) Resolution:** Fit L ∝ n^(-β) to the data in Figure 5 and report β and R². If the fit is poor, acknowledge this.

**W9 — Grokking criterion (>90% at 10,000 steps) is arbitrary.**
- **(a) Issue:** The paper sets the grokking threshold at >90% test accuracy by 10,000 steps. There is no justification for why 90% and not 85% or 95%, and no sensitivity analysis showing the results are robust to this choice. Given the sharp phase boundary observed, this threshold matters a great deal.
- **(b) Location:** Experimental Design (grokking criterion).
- **(c) Severity:** 2/5 — if the phase boundary is truly sharp, the exact threshold should not matter much, which means the authors should demonstrate this.
- **(d) Resolution:** Report grokking rates at 85%, 90%, 95% thresholds and show the phase boundary is stable across these choices.

**W10 — Hyperparameter sensitivity is not explored.**
- **(a) Issue:** The paper uses AdamW, lr=0.03, weight_decay=0.3 with no justification and no exploration of nearby hyperparameter settings. In grokking experiments, optimizer choice and learning rate can dramatically affect whether grokking occurs. A single hyperparameter setting with no ablation makes it impossible to know whether the observed phase transition is robust or an artifact of these specific choices.
- **(b) Location:** Experimental Design (optimizer), Appendix.
- **(c) Severity:** 3/5 — the authors acknowledge grokking is sensitive to optimization dynamics. Running at least one additional setting (e.g., lr=0.01 or lr=0.1) would demonstrate robustness.
- **(d) Resolution:** Run a 2×2 ablation over learning rate and weight decay near the reported values and show the phase boundary is consistent.

---

## Per-Rubric-Dimension Scores

| Dimension | Score | Calibration Anchor | Justification |
|---|---|---|---|
| **Originality / Novelty** | 7 | "Substantial conceptual advance" — a genuine unification of two previously distinct phenomena (grokking + scaling laws) through a shared phase transition mechanism, with formal theorems | The framework connects two active research areas. Theorem 1 is novel. The F_eff(w) reconciliation is less novel. |
| **Soundness** | 5 | "Methodology has serious gaps that compromise main claims" — between adequate and serious gaps | The n_c direction reversal without principled derivation of F_eff(w), unvalidated β=2/3, omitted Schaeffer test results, and single-task evidence are collectively serious. The methodology is strong within its narrow scope but the scope itself is the problem. |
| **Significance** | 6 | "Useful contribution within a niche" — the unification is important within the grokking/scaling law subfield | If the F_eff(w) reconciliation holds up, this is a significant contribution. But a single-task theory of grokking is currently a niche tool. |
| **Clarity** | 7 | "Clear, well-organized, easy to follow" | The paper is well-structured with clear theorems, a phase diagram, and explicit falsification conditions. The n_eff(t) vs n_c confusion and the F_eff(w) retrofitting reduce clarity slightly. |
| **Reproducibility** | 5 | "Critical hyperparameters or code missing" | The code is presumably released (not verified in this review). α values are not reported. Seeds are given (42, 137, 256). Without fitted α values, exact reproduction of the theory prediction is impossible. |
| **Contextualization** | 6 | "Adequate coverage; some misses" | The paper references standard grokking literature (Power et al., 2022) and scaling law literature (Kaplan et al., 2020). The F_eff(w) mechanism should engage more explicitly with the feature geometry literature (e.g., Elhage et al., 2022 on superposition). |
| **Ethical / Broader Impact** | 6 | "Boilerplate" | Standard broader impact statement. No specific concerns but no specific depth either. |

**Weighted Average:** (7×1.0 + 5×1.5 + 6×1.0 + 7×0.7 + 5×1.0 + 6×0.8 + 6×0.5) / (1.0+1.5+1.0+0.7+1.0+0.8+0.5) = (7+7.5+6+4.9+5+4.8+3) / 7.0 = 38.2 / 7.0 = **5.46**

---

## Pointed Questions for the Authors

**Q1 — Falsifiability of F_eff(w):** You claim F_eff(w) = F·(w/w0)^(-γ) with γ>1 reconciles the n_c direction reversal. What is the predicted value of n_c for width=256 under this formula? If I run width=256 and observe n_c ≈ 750 (extrapolating your decreasing trend), does that confirm or falsify the theory? Please specify the quantitative prediction before I run the experiment.

**Q2 — Why did you not report the Schaeffer test results?** You listed it as one of three falsification tests. If it was run, what was the outcome? If it was not run, why advertise it in the list of falsification conditions?

**Q3 — What is the fitted β from Figure 5?** The corollary predicts β → 2/3. Fit the power law L ∝ n^(-β) to your scaling law data and report the fitted exponent with 95% confidence interval. Does it overlap with 2/3?

**Q4 — How does your theory behave on a non-arithmetic task?** You have validated exclusively on (a+b) mod 47. If I run (a+b) mod 43, or MNIST digit classification, do I expect to see the same phase transition signature? What does your theory predict for a continuous input distribution?

**Q5 — What happens at width=256?** Your data shows a monotonically decreasing n_c. If this trend continues, width=256 should have n_c < 884. Is this physically plausible under your refined formula? At what width does your F_eff(w) go to zero, and what does that mean for the phase transition?

**Q6 — Grokking delay vs. n_eff(t):** Your Figure 6 shows grokking delay decreases with width and data. This is consistent with n_eff(t) growing faster for wider networks. But can you show the n_eff(t) trajectories directly? If I measure the effective feature count during training, does it track the predicted growth?

**Q7 — 0/51 sub-critical runs grokked: are these runs extended?** The paper says sub-critical extended training was a falsification test. Were the 51 non-grokking runs extended beyond 10,000 steps? If so, for how many steps, and did any of them eventually grok?

**Q8 — Why AdamW specifically?** Grokking is known to be sensitive to optimizer choice (SGD vs Adam behave very differently). What is the theoretical or empirical basis for choosing AdamW with lr=0.03? Would the phase transition survive a switch to SGD with similar effective learning rate?

---

## Falsifiability Test

**"What evidence would change my decision?"**

My current position is **Borderline / Accept** (leaning toward Accept). The following evidence would shift me:

- **Would move to Strong Accept:** Direct measurement of n_eff(t) during training that matches the predicted growth trajectory; Schaeffer test results confirming the phase transition smoothness; β fitted to Figure 5 data with CI overlapping 2/3; a second task showing the same phase transition.
- **Would move to Reject:** Running width=256 and finding n_c increases (not decreases), contradicting F_eff(w); Schaeffer test returning a negative result; F_eff(w) requiring γ < 1 to fit the data (which the text explicitly says is excluded); any single run at a sub-critical fraction grokking after extended training.
- **Would move to Strong Reject:** Formal proof that F_eff(w) cannot be derived from the stated assumptions; demonstration that the n_c = α·w·log(F) formula predicts the wrong sign for ANY width on mod-47, meaning the refined formula was purely post-hoc curve fitting.

The single most important experiment I would demand before Strong Accept: run the Schaeffer smoothness test and report the outcome. This is the paper's own falsification condition, and its omission is the clearest signal that the paper is not yet submission-ready.

---

## Confidence

**3/5.** I am confident in my reading of the paper's claims and the specific discrepancies I flagged (n_c direction, β non-validation, Schaeffer omission). I am less confident in my assessment of the theory's long-term validity because much depends on whether F_eff(w) is a genuine mechanism or an ad-hoc reconciliation. I would want to see the Schaeffer test results and a second-task validation before committing to a Strong Accept.

---

## Decision

**Borderline / Accept.** The paper makes a genuine conceptual contribution (unifying grokking and scaling laws via phase transitions), has a rigorous experimental design by ML standards, and acknowledges its main discrepancy (n_c direction reversal) rather than hiding it. These are real strengths.

However, the theory-experiment mismatch on n_c required a post-hoc reconciliation whose free parameters are not independently determined, the β = 2/3 prediction is unvalidated, the Schaeffer falsification test is listed but its results are not reported, and the entire empirical base is one arithmetic task. A Borderline Accept is appropriate at NeurIPS — this paper would benefit from another revision cycle focused on closing the theory-experiment gap and running the Schaeffer test. If the Schaeffer test is positive and a second task confirms the phase transition, this becomes an Accept.

---
*— The Adversarial Practitioner*
