# Review — The Statistical Rigorist

**Paper**: CRISP: Unifying Grokking and Scaling Laws via Phase Transitions in Feature Space
**Reviewer**: The Statistical Rigorist
**Date**: 2026-05-01

---

## Strengths

1. **Pre-registered falsification architecture (Section on Schaeffer, sub-critical, decorrelation tests)**
   - The authors explicitly state three falsification tests. This is commendable and rare. However (see W7), the success criteria for each test are not pre-specified with operational definitions.

2. **120-run experimental budget with systematic grid**
   - 5 widths × 8 fractions × 3 seeds is a principled sweep. The total design is not cherry-picked; it covers a meaningful region of (w, f) space.

3. **Sharp 0/1 phase boundary observation (0/51 sub-critical runs grokked)**
   - The claim that NO sub-critical runs grokked is a strong qualitative result. If this holds under replication, it is meaningful evidence for a sharp threshold.

4. **Formal theorem statement (Theorem 1, Appendix A)**
   - The phase transition existence proof is presented formally. I did not audit the proof, but the structure is appropriate for the claim.

5. **Binary outcome clarity**
   - Grokking is defined clearly: >90% test accuracy by step 10,000. This eliminates ambiguity about the endpoint.

---

## Weaknesses

### W1. N=3 seeds per condition is fundamentally insufficient for variance estimation
- **Issue**: With exactly 3 seeds (42, 137, 256) per condition, any variance estimate is based on N=2 degrees of freedom (the sample variance formula with N-1). This is not a robust estimate. You cannot estimate a distribution from 3 draws.
- **Where**: Experimental Design (3 seeds); Results Summary (n_c values reported as point estimates)
- **Severity**: 5/5 — This is the most critical flaw. All quantitative claims (n_c estimates, scaling exponents, phase boundary sharpness) derive from 3-seed averages with no uncertainty quantification.
- **Resolution**: Run each condition with ≥10 seeds. Report median and IQR (not mean ± SD, which assumes normality). For binary grokking outcomes, report binomial confidence intervals (Wilson or Clopper-Pearson).

### W2. No confidence intervals on ANY reported quantity
- **Issue**: n_c values (1546, 1325, 1105, 1105, 884 for w=32,48,64,96,128) are reported as exact integers with no uncertainty bounds. These are not informative without 95% CIs.
- **Where**: Results Summary, Figure 3 (n_c vs width)
- **Severity**: 5/5 — An n_c of 1546 ± 200 is a meaningful result. An n_c of 1546 with CI [884, 2200] is uninformative. I cannot tell which case applies.
- **Resolution**: Bootstrap CIs across seeds (10,000x resample with replacement). Report the 2.5th and 97.5th percentiles per width.

### W3. Post-hoc theory rescue: F_eff(w) introduced after data contradicted prediction
- **Issue**: Theorem 2 predicts n_c ∝ w (increases with width). The empirical result shows n_c *decreases* with width (884 to 1546 across w=128 to w=32). The authors introduce F_eff(w) = F·(w/w0)^(-γ), γ>1 to reconcile. This is a post-hoc modification.
- **Where**: Results Summary ("reconciled via F_eff(w)"); Theorem 2 and revised formula
- **Severity**: 4/5 — This is the garden of forking paths made concrete. When theory and data conflict, a new parameter is introduced. Without pre-registration of F_eff(w), this is unfalsifiable.
- **Resolution**: Pre-specify the effective feature count hypothesis before running the experiment. Or, acknowledge this as an exploratory finding requiring independent validation.

### W4. Binary outcome with N=3: grokking probability is essentially unestimable
- **Issue**: Grokking is binary (grokked: yes/no). With 3 seeds per condition, you have at most 3 Bernoulli trials. The grokking rate of 57.5% (69/120) is an aggregate across conditions, not a per-condition estimate. Per-condition estimates have N=3.
- **Where**: 69/120 runs grokked (57.5%); grok rate heatmap (Figure 2)
- **Severity**: 4/5 — The phase diagram (Figure 2) shows a heatmap of grok rates per (w, f) cell. Each cell is based on 3 binary outcomes. The "boundary" between grokking and non-grokking is drawn through cells with N=3.
- **Resolution**: Replicate each condition ≥20 times. Fit a proper threshold model (e.g., logistic regression on fraction with uncertainty).

### W5. α is calibrated, not derived — theory is not tested on its own terms
- **Issue**: The paper states α is "calibration" not first-principles. Theorem 2's n_c = α·w·log(F) has a free parameter α that absorbs all the task-specific physics. This means the theory cannot make quantitative predictions; it only predicts qualitative trends (direction of n_c vs w).
- **Where**: "α characterized as calibration" (peer review revision notes)
- **Severity**: 3/5 — The theory is partly phenomenological. The calibration approach is legitimate for applied work, but it means the paper cannot make genuine out-of-sample predictions. Any new task requires re-calibration.
- **Resolution**: Derive α from first principles or show α is approximately constant across tasks. Validate the n_c ∝ w·log(F) form on at least one held-out task.

### W6. β = 2/3 corollary is derived, not measured
- **Issue**: The paper derives β = 1/(1+ν) → 2/3 as ν → 1/2. But ν is never independently measured. The corollary is a theoretical consequence, not an empirical validation.
- **Where**: Corollary statement; scaling law analysis (Figure 5)
- **Severity**: 3/5 — This is standard theoretical work, but the paper presents it alongside empirical results in a way that blurs the line. Readers may infer β=2/3 is measured.
- **Resolution**: Explicitly label the β=2/3 prediction as theoretical. Report the measured ν from power-law fits to the data.

### W7. Falsification tests lack pre-specified success criteria
- **Issue**: The paper lists three falsification tests (Schaeffer smoothness, sub-critical extended training, decorrelation) but does not specify what constitutes passing or failing each test.
- **Where**: "Three falsification tests: Schaeffer smoothness, sub-critical extended training, decorrelation"
- **Severity**: 3/5 — Without operationalized criteria, "falsification tests" are aspirational. What p-value threshold? What effect size? What sample size?
- **Resolution**: Pre-register the success criterion for each test (e.g., "decorrelation score must exceed 0.8 at n_c").

### W8. Single task (mod-47) limits all generalization claims
- **Issue**: The entire experimental basis is one task: (a+b) mod 47 with 2209 pairs. All theorems, all empirical results, all falsification tests are on this single task.
- **Where**: "Validated on mod-47"; "Single task (mod-47) limits generalization of claims"
- **Severity**: 4/5 — Phase transitions may be task-specific. The claim of "unifying grokking and scaling laws" requires demonstration across multiple tasks.
- **Resolution**: Validate on at least 2-3 additional tasks (e.g., modular arithmetic with different primes, permutation tasks).

### W9. The phase transition "sharpness" claim is unsubstantiated
- **Issue**: The paper claims a "sharp 0/1 phase boundary." With 3 seeds per (w, f) cell, the sharpness is inferred, not measured. The difference between p(grok)=0 and p(grok)=1 could be a single seed's variance.
- **Where**: "Sharp 0/1 phase boundary observed"; 0/51 sub-critical runs grokked
- **Severity**: 3/5 — The 0/51 result is suggestive but N=3 per cell cannot establish sharpness. The sharp/fuzzy distinction requires a continuous measure of grokking probability.
- **Resolution**: Fit a continuous probability model (e.g., logistic or Probit) across fraction and estimate the slope at the boundary. Report the slope's 95% CI.

---

## Per-Rubric-Dimension Scores

### 1. Originality / Novelty: 7/10
Calibration anchor: "Substantial conceptual advance over the closest prior work" (8) vs "Clear improvement / extension; combines existing ideas in non-obvious ways" (6).

**Justification**: The unification of grokking and neural scaling laws via a shared phase transition mechanism is genuinely novel. The formal theorem structure is also novel in this literature. I deduct one point because the single-task validation limits the scope of the "unification" claim — a true unification should apply across multiple tasks.

### 2. Soundness: 4/10 ⚠️ REJECTION TRIGGER
Calibration anchor: "Methodology has serious gaps that compromise main claims" (4) vs "Methodology is fundamentally flawed; results untrustworthy" (2).

**Justification**: The N=3 seed design produces unquantifiable uncertainty on the central quantity n_c. The post-hoc F_eff(w) modification without pre-registration is methodologically troubling. A field-standard power analysis for detecting a phase transition boundary would require ≥10 seeds per condition. The paper's main empirical contribution (the n_c vs width relationship) is based on N=3 with no uncertainty quantification. This is not acceptable for a methodological contribution.

### 3. Significance: 6/10
Calibration anchor: "Useful contribution within a niche" (6) vs "Important within the subfield; will be cited heavily" (8).

**Justification**: If validated, this would be a significant unification. The niche (grokking + scaling laws) is specific but active. The contribution is genuine, but the single-task limitation means practitioners cannot yet use this framework for prediction.

### 4. Clarity: 7/10
Calibration anchor: "Clear, well-organized, easy to follow" (8) vs "Mostly clear; some sections require re-reading" (6).

**Justification**: The paper is well-structured with clear theorems and appendices. The figures are informative. The main tension (theory vs empirical n_c direction) is clearly presented. One deduction for the β=2/3 corollary being presented alongside empirical results in a way that implies measurement rather than derivation.

### 5. Reproducibility: 4/10
Calibration anchor: "Critical hyperparameters or code missing" (4) vs "Sufficient detail in paper to reproduce" (6).

**Justification**: The paper does not release code, data, or configs. The optimizer settings (AdamW, lr=0.03, wd=0.3) are given, but initialization seeds, hardware specs, and the exact grokking criterion implementation are not. N=3 seed design means reproducibility is especially critical — another lab would need to replicate the exact same design to compare variance estimates. Without code, this is impossible.

### 6. Contextualization vs Prior Work: 6/10
Calibration anchor: "Adequate coverage; some misses" (6) vs "Strong coverage; correctly positioned vs SOTA" (8).

**Justification**: The paper cites relevant grokking literature and scaling law literature. The unification framing is novel. However, the F_eff(w) mechanism (shrinking effective feature count with width) should be connected to prior work on width-dependent effective capacity in MLPs.

### 7. Ethical / Broader Impact: 6/10
Calibration anchor: "Boilerplate" (6) vs "Adequate coverage" (8).

**Justification**: No Broader Impact section is present (likely removed for anonymity). The paper does not discuss risks or societal implications. Standard boilerplate would score 6; no section at all is below that.

**Weighted Average**: (7×1.0 + 4×1.5 + 6×1.0 + 7×0.7 + 4×1.0 + 6×0.8 + 6×0.5) / 6.0 = (7 + 6 + 6 + 4.9 + 4 + 4.8 + 3) / 6.0 = 35.7 / 6.0 = **5.95 → Borderline**

---

## Pointed Questions for Authors

1. **"With 3 seeds per condition (N=3), the standard error of a binary proportion is at best sqrt(p(1-p)/3). For a grokking rate near 50%, this is ±0.29 — meaning any reported grok rate has an uncertainty of roughly ±29 percentage points. How does this affect the sharpness of your phase boundary?"**

2. **"The theory predicts n_c ∝ w (increases). You observe n_c decreases with width. You introduce F_eff(w) = F·(w/w0)^(-γ) with γ>1. Was this functional form pre-registered? If not, what alternative forms did you consider, and why did you reject them?"**

3. **"In Figure 2 (grok rate heatmap), each cell represents 3 binary outcomes. What is the binomial 95% confidence interval for a cell with 2/3 grokking rate? For 1/3? For 0/3?"**

4. **"You report n_c values as exact integers: 1546, 1325, 1105, 1105, 884. These appear to come from interpolating a fitted boundary. What is the uncertainty on this boundary estimate? Have you bootstrapped this?"**

5. **"The paper claims a 'sharp 0/1 phase boundary.' What is the minimum slope you could detect with N=3 per cell? Have you conducted a power analysis for the sharpness claim?"**

6. **"α is calibrated, not derived. For a new task (e.g., mod-53), how would a practitioner use this framework to predict n_c? Would they need to re-run the full experiment?"**

7. **"You state 0/51 sub-critical runs grokked. What defines 'sub-critical'? Is this the same as 'below the fitted n_c boundary'? If so, this is circular — you cannot falsify your boundary estimate using the same data that defined it."**

---

## Falsifiability Test

**What evidence would change my decision?**

To move from **Borderline → Accept**, the authors would need to:

- **Re-run the full 5×8 grid with ≥10 seeds per condition (40 conditions × 10 seeds = 400 runs)**
- **Report n_c with bootstrap 95% CIs (10,000x resample with replacement)**
- **Pre-register F_eff(w) as a secondary hypothesis before fitting; show the data favors it over the original n_c ∝ w form via model selection (AIC/BIC)**
- **Validate on at least one held-out task (e.g., mod-31 or a permutation task)**
- **Release code and all 400+ run configs for independent verification**

If, with 10+ seeds, the n_c vs width relationship replicates as monotonically decreasing, and the F_eff(w) form is pre-registered and confirmed, I would upgrade to **Accept** on Soundness (6/10).

If the new data shows n_c is consistent with the original n_c ∝ w prediction, or if CIs are wide enough to include both directions, I would downgrade to **Reject** (3/10 Soundness).

---

## Confidence

**3/5**

My confidence is limited because I am reviewing a paper bundle, not the full paper. I have not seen:
- The actual Figures (I have descriptions only)
- The full Theorem 1 proof (Appendix A referenced but not included)
- The exact text of the Schaeffer, sub-critical, and decorrelation falsification tests
- The exact code or configuration used

My assessment is based entirely on the meta-description in the paper bundle. A direct review of the paper itself would be required for a definitive judgment, particularly on the theorem proofs and the figure quality.

---

## Decision

**Borderline → Reject (pending replication with proper seed count)**

The paper has genuine conceptual novelty and an admirable falsification architecture. However, the N=3 seed design produces unquantifiable uncertainty on the central empirical claim (the n_c vs width relationship). A result with no confidence intervals is not a result — it is a preliminary observation. The post-hoc introduction of F_eff(w) to reconcile contradictory theory and data is methodologically concerning.

**If the authors can reproduce the key findings (n_c decreases with width, F_eff(w) mechanism) with 10+ seeds and proper uncertainty quantification, I would reconsider this paper seriously for Accept.**

The framework is worth developing. The current data is insufficient to support the strong theoretical claims.

---

— The Statistical Rigorist
