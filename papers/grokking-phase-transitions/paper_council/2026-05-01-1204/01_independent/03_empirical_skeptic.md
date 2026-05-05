# Empirical Skeptic Review — CRISP: Unifying Grokking and Scaling Laws

**Paper**: CRISP: Unifying Grokking and Scaling Laws via Phase Transitions in Feature Space
**Reviewer**: The Empirical Skeptic
**Date**: 2026-05-01

---

## 3–5 Strengths (Grounded in Specific Claims/Figures/Sections)

1. **Novel conceptual unification with formal structure.** The claim that grokking and neural scaling laws share a common mechanism — a phase transition from superposition to clean features in representation space — is genuinely original. Theorem 1 provides an existence proof, Theorem 2 derives n_c = α·w·log(F). This is a nontrivial theoretical contribution that goes beyond curve-fitting. (Abstract, Theorems 1–2)

2. **Three falsification tests are built in, not bolted on.** The paper explicitly proposes Schaeffer smoothness, sub-critical extended training, and decorrelation as falsification tests. This is rare in empirical ML — most papers don't pre-register what would convince them they are wrong. The sub-critical result (0/51 runs grokked below the critical fraction) is a clean, quantitative rejection of the null. (Section on Falsification Tests, Figure 2)

3. **Sharp 0/1 phase boundary is a clean empirical result.** The observation that grokking exhibits a sharp rather than gradual phase transition — with grok rate dropping essentially to 0 below the critical fraction — is empirically robust across all five widths tested. This is shown in the phase diagram heatmap (Figure 2) and the sub-critical control experiments. At minimum, the phase transition framing is well-supported.

4. **Experimental design is reasonably thorough for a single task.** 120 total runs spanning 5 widths and 8 fractions with 3 seeds per condition provides a non-trivial landscape survey. The monotonic decrease in grokking delay with width and data fraction (Figure 6) is internally consistent. (Experimental Design section, 120 runs)

5. **The F_eff(w) reconciliation attempt is intellectually honest about its own limitations.** The paper explicitly acknowledges that empirical n_c decreases with width (contradicting Theorem 2's predicted increase) and proposes F_eff(w) = F·(w/w0)^(-γ) to reconcile. Marking n_eff(t) as an unproven conjecture, and marking projected values with †, shows some awareness of the gap between theory and empirics. (Section reconciling n_c direction, n_eff(t) marked as conjecture)

---

## 5–10 Weaknesses

### Weakness 1: Single-task empire — all generalization claims are fantasy
- **Issue**: The entire empirical base is (a+b) mod 47, a single synthetic arithmetic task. Every claim about "grokking," "phase transitions," "scaling laws," and "superposition→clean-feature" dynamics is validated on exactly one task.
- **Where**: Abstract, Experimental Design, all figures
- **Severity**: 5/5 — This is a reject-level concern. A theory of grokking that only explains one task at one dataset size is a theory of that task. I cannot distinguish whether the phase transition framework is a genuine mechanistic account vs. a post-hoc story that fits mod-47.
- **Resolution**: Test the framework on at minimum 2–3 additional tasks (e.g., modular arithmetic mod a different prime, permutation parity, simple NLP tasks) with comparable width/fraction sweeps. If n_c doesn't follow the same functional form, the theory is task-specific.

### Weakness 2: n_c direction contradiction — theory vs. empirics reconciled post-hoc
- **Issue**: Theorem 2 predicts n_c ∝ w (n_c increases with width). Empirically, n_c *decreases* with width: from 1546 at w=32 to 884 at w=128. This is not a minor discrepancy — it's a qualitative reversal.
- **Where**: Theorem 2 (prediction) vs. Results Section / Figure 3 (empirical n_c values)
- **Severity**: 4/5 — The F_eff(w) explanation is plausible, but it is introduced *after* the contradiction is observed. There is no independent validation that F_eff(w) actually shrinks with width as claimed. γ is fit to explain the data, not predicted from first principles.
- **Resolution**: Directly measure F_eff(w) (e.g., via representation similarity analysis or probing) to confirm it actually decreases with width. Show that the functional form of F_eff(w) is consistent across independent datasets, not just calibrated to fit the n_c anomaly.

### Weakness 3: α is calibrated, not derived — theory lacks predictive power
- **Issue**: The key constant α = (σ_x²/2λ)·(1+γ/(λw))^(-1) contains unmeasured or unspecified parameters (σ_x², λ). The paper effectively fits α per task rather than predicting it from first principles.
- **Where**: Theorem 2, α characterization in revision notes
- **Severity**: 3/5 — This is a moderate concern. Calibrated constants are common in physics-inspired theory, but they make the theory descriptive rather than predictive. I cannot use Theorem 2 to forecast n_c for a new task without fitting α first.
- **Resolution**: Specify reasonable physical bounds on σ_x² and λ (from data distribution and regularization strength respectively) and show that the resulting range of n_c predictions brackets the observed values.

### Weakness 4: β = 2/3 corollary never directly validated
- **Issue**: The paper derives β = 1/(1+ν) → 2/3 as a corollary, but never reports a direct measurement of β. The scaling exponent is central to linking phase transition sharpness to scaling law behavior, yet it is treated as a theoretical prediction without empirical confirmation.
- **Where**: Corollary (Section on Theoretical Results), scaling law figure (Figure 5)
- **Severity**: 3/5 — The corollary is a major claim (connecting phase transition sharpness to the neural scaling law exponent). If it cannot be measured independently, its truth is unverifiable from this data.
- **Resolution**: Fit β directly from the test loss vs. training fraction curve across widths and report the fitted values. Show they are consistent with 2/3 within uncertainty.

### Weakness 5: n_eff(t) is labeled a conjecture, not a theorem — results may not be predictive
- **Issue**: n_eff(t) — the effective feature count over training — is described as "empirically testable" but is neither formally derived nor validated against held-out predictions. The paper treats it as a plausible mechanism without establishing its truth.
- **Where**: Section noting n_eff(t) as conjecture
- **Severity**: 3/5 — A mechanism proposed but unvalidated is a hypothesis, not a result. If n_eff(t) is wrong, the entire reconciliation of the n_c direction puzzle is on borrowed time.
- **Resolution**: Design an experiment where n_eff(t) predicts a novel phenomenon (e.g., a specific step at which representational geometry should shift), test it, and report the outcome.

### Weakness 6: 3 seeds per condition — variance estimates are essentially unusable
- **Issue**: With 3 seeds per condition, the paper cannot estimate the variance of its critical fraction estimates. The reported n_c values (1546, 1325, 1105, 1105, 884) are point estimates. For the grokking rate binary variable, 3 Bernoulli trials give enormous confidence intervals.
- **Where**: Experimental Design (seeds: 3 per condition)
- **Severity**: 3/5 — At 57.5% grokking rate across 3 seeds, the 95% CI on the true grokking probability is roughly [35%, 78%]. This means some of the reported "sharp phase boundaries" may be less sharp than they appear.
- **Resolution**: Run at minimum 10 seeds per condition for key conditions. Report median and interquartile range for n_c, not just point estimates.

### Weakness 7: No out-of-distribution evaluation for any robustness claim
- **Issue**: The paper makes no OOD evaluation whatsoever. All claims about phase transitions and scaling laws are tested on in-distribution data from the mod-47 task. There is no covariate shift, no label shift, no concept drift testing.
- **Where**: Entire results section
- **Severity**: 4/5 — For a paper claiming a general mechanistic account of grokking, the absence of any OOD evaluation is a major gap. I cannot assess whether the phase transition framework would predict anything about generalization to different data distributions.
- **Resolution**: Evaluate on at least one OOD variant: e.g., mod-47 trained, mod-53 tested; or train on one random seed's data split and test on another's.

### Weakness 8: Single architecture — no evidence the results are architecture-general
- **Issue**: All experiments use a 2-layer MLP with one-hot encoding. There is no evidence the phase transition dynamics, the n_c functional form, or the β scaling exponent hold for other architectures (CNNs, transformers, deeper networks).
- **Where**: Experimental Design (2-layer MLP, one-hot encoding)
- **Severity**: 3/5 — Grokking is observed in transformers (Power et al., 2022). If the CRISP framework cannot predict grokking behavior in transformers, its generality claim is undermined.
- **Resolution**: Run at least one comparable experiment with a transformer or deeper MLP and show the same phase transition signature.

### Weakness 9: Grokking criterion (90% test accuracy by 10,000 steps) is a soft threshold
- **Issue**: The paper defines grokking as >90% test accuracy by end of 10,000 steps, but does not report what happens at 15,000 or 20,000 steps for the "non-grokking" runs. Some runs may simply be slow rather than genuinely non-grokking.
- **Where**: Grokking criterion definition, results (non-grokking runs)
- **Severity**: 2/5 — Moderate concern. The sub-critical control (extended training) partially addresses this, but the extension is only to 10,000 steps and only for sub-critical conditions. Supra-critical conditions that fail to grok by 10,000 steps are not checked.
- **Resolution**: Run a subset of supra-critical non-grokking runs out to 20,000+ steps to confirm they genuinely plateau below threshold.

---

## Per-Rubric-Dimension Scores

| Dimension | Score | Calibration Anchor |
|-----------|-------|-------------------|
| Originality / Novelty | 8 | A genuinely new conceptual frame (phase transition unification), not just a better fit to existing data. The theorems are non-trivial. |
| Soundness | 5 | The methodology is adequate for the in-distribution task, but serious gaps compromise the generalizability claims: single task, single architecture, n_c direction reversal unexplained, β not measured, 3 seeds insufficient for variance estimates. |
| Significance | 7 | If the framework generalizes beyond mod-47, it would be a substantial contribution to understanding deep learning training dynamics. The 2/3 scaling exponent corollary is potentially important. |
| Clarity | 7 | Well-organized with clear theorem statements and figure captions. The reconciliation of the n_c direction reversal is clearly explained, even if the underlying concern remains. |
| Reproducibility | 6 | 120 runs, 3 seeds, optimizer settings given. However, α requires fitting, F_eff(w) requires calibration, and no code is released. A determined reproducer could replicate but not predict. |
| Contextualization vs prior work | 6 | Adequate coverage of grokking literature and scaling law literature separately, but the integration point (why phase transitions unify them) could be better positioned against Power et al. and other grokking mechanistic accounts. |
| Ethical / Broader Impact | 6 | Standard boilerplate. No specific concerns but nothing distinctive. |

**Weighted Average**: (8×1.0 + 5×1.5 + 7×1.0 + 7×0.7 + 6×1.0 + 6×0.8 + 6×0.5) / (1.0+1.5+1.0+0.7+1.0+0.8+0.5) = (8 + 7.5 + 7 + 4.9 + 6 + 4.8 + 3) / 6.5 = 41.2 / 6.5 ≈ **6.34**

---

## 5+ Pointed Questions for the Authors

1. **Direct replication demand**: You claim n_c = α·w·log(F). If I give you a new task — (a+b) mod 53 with the same 2-layer MLP setup — what is your predicted n_c for w=64 before you run the experiment? If you cannot answer without fitting α first, your theory is descriptive, not predictive. What would it take to make it predictive?

2. **Independent evidence for F_eff(w) shrinkage**: You argue that F_eff(w) shrinks with width to explain why n_c decreases while Theorem 2 predicts it increases. What is your independent evidence that F_eff actually behaves this way? Have you measured representation similarity, probing accuracy, or other proxy metrics for F_eff across widths? If not, why should I believe this explanation over the simpler reading that Theorem 2 is wrong?

3. **Transformer experiments**: Grokking was first characterized in transformers (Power et al., 2022). Your entire experimental base is a 2-layer MLP. Have you attempted any transformer experiments? If the phase transition framework is truly general, it should produce grokking signatures in transformers. If it doesn't, what is the scope of your claim?

4. **Why mod-47 specifically?**: What guarantees that the phase transition signature you observe is not an artifact of mod-47's particular modular arithmetic structure? Have you tried mod-43, mod-59, or a non-modular arithmetic task? The entire edifice rests on one task — this is a serious generalization concern.

5. **β measurement**: Your Corollary predicts β → 2/3 for large width. Have you attempted to fit β directly from your loss-vs-fraction curves? What value do you get? If you haven't measured it, on what basis should I believe the corollary?

6. **Seed variance on the phase boundary**: With 3 seeds per condition, you have essentially no variance estimate for n_c. For the w=96 condition, n_c=1105. What is the standard deviation across your 3 seeds? If one seed gives n_c=800 and another gives n_c=1500, your "sharp" phase boundary is actually quite noisy.

---

## Falsifiability Test: What Evidence Would Change My Decision?

This is the acid test of empirical credibility. I pre-specify what would convince me the paper's claims are wrong:

- **If** mod-53 with the same setup shows n_c *increasing* with width (opposite direction) → the F_eff(w) reconciliation fails and Theorem 2's direction error is fatal
- **If** a transformer experiment with comparable setup shows no sharp phase transition → the mechanism is architecture-specific and the "unification" claim is overbroad
- **If** fitting β directly from the data gives β ≈ 0.5 or β ≈ 0.8 (not near 2/3) → the corollary is unsupported
- **If** measuring F_eff(w) independently (via probing or representation analysis) shows F_eff *increases* or is constant with width → the post-hoc explanation is false
- **If** 10-seed replication shows n_c variance is >50% of the mean across widths → the "sharp phase boundary" is actually a noisy statistical artifact

**What would elevate my assessment**: A paper that runs the same framework on 3 diverse tasks (mod-47, a permutation task, an NLP task) and shows the same n_c functional form with independently estimated α would move me to Accept. Evidence of the phase transition in a transformer would move me substantially.

---

## Confidence

**4/5** — I have a clear picture of the paper's empirical basis and its limitations. I am confident the paper is NOT strong accept (due to single-task base and n_c direction reversal). I am reasonably confident it is in Borderline/Accept territory given the theoretical novelty and clean phase boundary results, but a single-task paper cannot cross into Strong Accept without generalization evidence.

---

## Decision: **Borderline**

**Rationale**: The paper has genuine theoretical novelty — the phase transition unification of grokking and scaling laws is a creative, non-incremental contribution that deserves publication-level attention. The three falsification tests and the sharp 0/1 phase boundary are credible empirical results. However, the single-task empirical base, the unresolved n_c direction contradiction, the unmeasured β, the calibration-not-derivation problem for α, and the absence of any OOD evaluation mean the paper's grand claims (unifying grokking and scaling laws generally) are not supported by the evidence presented.

The paper's theoretical core is interesting enough to warrant publication *as a single-task empirical study with theoretical contribution* — but it should be positioned and scoped accordingly. The current framing overstates generalizability.

**Recommended path to Accept**: (1) Run experiments on 2 additional tasks (mod-53, permutation parity) and show the same functional form holds; (2) directly measure β and report the fit; (3) independently measure F_eff(w) to validate the n_c reconciliation; (4) increase to 10 seeds per condition and report variance; (5) evaluate on at least one OOD variant.

---

*— The Empirical Skeptic*
