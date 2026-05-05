# Cross-Examination: Adversarial Practitioner Review — CRISP Paper

**Paper:** CRISP: Unifying Grokking and Scaling Laws via Phase Transitions in Feature Space
**Reviewer:** The Adversarial Practitioner
**Date:** 2026-05-01
**Cross-Examination Phase**

---

## 1. Disagreements with Other Reviewers

### D1: F3 decorrelation test severity — vs. The Naive Reader

The Naive Reader (W3) rates the missing F3 result at **5/5 severity** — "missing a key falsification result." My original review did not assign a specific severity to the missing F3 result (I mentioned it as part of W2, the n_eff(t) conjecture discussion, but did not isolate it).

**My position:** The Naive Reader is correct that F3's missing result is a 5/5 issue. F3 is the only test that directly validates the proposed mechanism (superposition index S dropping at the same n_c where grokking occurs). Without the observed Pearson r value, the paper cannot claim that its falsification test passed. I downgraded this by conflating it with n_eff(t) discussion.

**Revised position:** I now rate the missing F3 result as a standalone 5/5 weakness. The decorrelation test is the causal mechanism test — it directly links the feature-space phase transition (S drop) to the behavioral transition (grokking onset). Without reporting r, the paper leaves its central mechanistic claim untested and unvalidated.

### D2: Single-task validation severity — partial agreement with The Methodological Hawk

The Methodological Hawk assigns single-task validation **4/5 severity** and frames it as a disqualifying gap for NeurIPS methodology. I assign it **5/5** as a fundamental limitation, but the Methodological Hawk is more pointed: "A single task in a single architecture class cannot support the scope of these claims."

**My position:** I agree with the 4/5 rating from the Hawk and the Big-Picture Editor (3/5). My 5/5 was too high — the single-task validation is serious but not inherently disqualifying if the theory is well-motivated and the empirical results are clean. The paper acknowledges the limitation in Section 6. A more calibrated rating is 4/5.

**Revised position:** Single-task validation is a 4/5 weakness (not 5/5). The limitation is real but acknowledged. What elevates it is that the paper makes universal claims (grokking mechanism, β = 2/3 connection to scaling laws) on the basis of one synthetic task.

### D3: F1 (Schaeffer smoothness test) — vs. The Theory Critic

The Theory Critic (W7) notes that F1 "is insufficiently specific" because it compares test accuracy (the grokking criterion) against log-loss (a different metric). The Theory Critic rates this 2/5.

**My position:** I did not independently flag F1 as a weakness. The Theory Critic is correct that the falsification test compares different outcome variables, which is technically imprecise. However, the logic is sound: if the apparent phase transition is purely a metric artifact from the hard 90% accuracy threshold, then using a smooth metric should eliminate the apparent sharpness. The test design is reasonable even if the framing is imprecise.

**Revised position:** I adopt the Theory Critic's point that F1's framing is imprecise (comparing accuracy vs. log-loss). This is a 2/5 weakness in precision, not a fundamental flaw. The test still correctly addresses the metric artifact hypothesis.

---

## 2. Issues Others Missed That I Want to Add

### I1: The F1 (log-loss smoothness test) result was never reported — NEW from my cross-review

The paper describes F1 in Section 4 as a falsification criterion but never reports the result. The Naive Reader (Q3) asks this directly: "Why was F1 (log-loss smoothness test) not run or reported as a result?" I did not flag this in my original review.

**Issue:** The Schaeffer smoothness test is specifically designed to rule out metric artifacts as the explanation for apparent phase transitions in grokking studies. If the log-loss also shows a sharp transition at the same n_c, the "metric artifact" confound is not falsified. The paper acknowledges F1 addresses this concern but never reports whether log-loss shows a transition. This means the metric artifact concern is neither confirmed nor ruled out.

**Severity:** 4/5 — the metric artifact concern is central to the credibility of the sharp 0/1 phase boundary claim.

### I2: Hyperparameter grid is a single learning rate — partially missed by me

I flagged this as W8 (Sub-Gaussian assumption) but framed it as a theoretical vulnerability. The Methodological Hawk correctly identifies this as a **methodology gap**: the entire 120-run experiment uses exactly one learning rate (lr=0.03, wd=0.3, 10,000 steps). No variation across learning rates, weight decay values, or other hyperparameters.

**Issue:** Grokking is known to be sensitive to optimization dynamics. If lr=0.03 produces grokking but lr=0.01 generalizes immediately without delay, or lr=0.1 produces different phase behavior, the theory's generality is compromised. The single hyperparameter point means the experiment is reproducible in the narrow sense but the phenomenon's robustness across optimization hyperparameters is untested.

**Severity:** 3/5 — not fatal for a theory paper but a significant gap for the "phase transition is a general mechanism" claim.

### I3: β = 2/3 corollary is never fitted from the scaling law data — NEW from my cross-review

The Naive Reader (W7, W5) raises this: Corollary 1 predicts β → 2/3, but Figure 5 shows a scaling curve with no power-law exponent fit and no reported β value. The Methodological Hawk also flags this (W10: 3/5).

**Issue:** The paper's most "exportable" prediction — that the transition sharpness exponent ν = 1/2 implies β = 1/(1+ν) = 2/3, connecting to neural scaling laws — is never validated within the paper. The connection to Kaplan et al. 2020 (β ≈ 0.076) is asserted but not explained. The paper predicts β = 2/3 without measuring whether the data actually supports it.

**Severity:** 4/5 — this is the paper's bridge to the scaling law literature and it is presented without empirical support.

### I4: Experimental n_c vs. theoretical n_c mismatch — NEW from my cross-review

The Naive Reader (W10) raises an important point I did not flag: the theory defines n_c as a sharp critical point in the energy landscape (theoretical optimum of E(Φ;n)), but the experimental n_c is defined as "the smallest n where ≥50% of seeds grok" (an empirical detection threshold across stochastic training runs). These are different quantities.

**Issue:** The gap between "theoretical n_c" and "observed n_c in experiments" is not bridged. The 50% grokking threshold across seeds is a population statistic that depends on the variance of training dynamics, not just the energy landscape optimum. A rigorous theory-to-experiment bridge would need to relate the theoretical phase transition point to the empirical detection threshold. The paper conflates these without justification.

**Severity:** 3/5 — this is a gap in the theory-to-empirics bridge, not a fatal flaw, but it means the quantitative predictions (Table 3 n_c values) may not be directly comparable to the theoretical n_c.

### I5: The 90% accuracy threshold is not justified against F1's own concern — partially missed by me

The Naive Reader (W6) points out that the hard 90% accuracy threshold is exactly the kind of discontinuous metric that the Schaeffer smoothness test (F1) warns against as a potential artifact. F1 says: if you replace accuracy with a smooth metric, the apparent transition should disappear if it's a metric artifact. But the paper uses the hard accuracy threshold as its primary criterion while acknowledging F1 addresses this concern.

**Issue:** The paper sets up the concern (hard threshold → metric artifact) and then uses the hard threshold as the primary grokking indicator without explaining why F1 does or doesn't pass. The authors acknowledge this tension in the F1 description but never report the result.

**Severity:** 4/5 — the hard threshold is the operational definition of grokking in the paper, so the F1 result directly validates or invalidates the primary experimental methodology.

---

## 3. My Positions Being Updated After Seeing Others

### P1: F3 decorrelation test is the most critical missing result — UPDATED

**Before:** I mentioned F3 in passing as part of W2 (n_eff conjecture) but did not assign it independent severity.

**After:** All reviewers agree F3 result is not reported. The Naive Reader rates it 5/5. The Theory Critic rates it 2/5 for a different reason (layer-wise PCA justification). The Big-Picture Editor rates it 2/5 but explicitly says "easy to fix with a number." Multiple reviewers flag this as the mechanism test whose result is missing.

**Updated position:** F3 decorrelation test not being reported is a 5/5 standalone weakness — it is the only test that directly validates the superposition-to-clean mechanism at the feature-space level. The F2 result (0/51 sub-critical) rules out "train longer" but does not confirm the specific phase transition mechanism. Without F3, the paper demonstrates a threshold effect exists but not that the feature-space mechanism is responsible.

### P2: Single-task validation is 4/5, not 5/5 — UPDATED

**Before:** I rated single-task validation 5/5 as "fundamental limitation."

**After:** The Methodological Hawk rates this 4/5 and frames it as "disqualifying at current scope" given NeurIPS methodology as primary filter. The Big-Picture Editor rates it 3/5. The Theory Critic rates it 2/5 for architecture generalization but does not flag task diversity specifically. The Naive Reader rates it 3/5 for missing comparison to prior grokking baselines.

**Updated position:** A more calibrated rating is 4/5. The limitation is serious and acknowledged, but a well-motivated theory on a single clean task can be a valid contribution if the methodology is rigorous. The single-task validation becomes a fatal flaw only if the theory's predictions are fragile to task choice — which is exactly what the F_eff(w) post-hoc patching suggests.

### P3: The sub-Gaussian assumption (W8) is a theoretical vulnerability, not an empirical one — UPDATED

**Before:** I rated W8 (sub-Gaussian assumption unverified) as a 3/5 weakness.

**After:** Several reviewers (Domain Expert W5, Theory Critic W4) discuss the concentration of measure assumptions in the proofs. The Domain Expert specifically flags that concentration bounds could be exponentially weak in width, making the theoretical bound vacuous at w=32.

**Updated position:** The sub-Gaussian assumption is more of a theoretical vulnerability than an empirical one. It matters for the rigor of Theorem 1 and Theorem 2, not for the empirical results. I should have framed it as a theoretical concern (proof rigor) rather than an empirical methodology gap. This does not change the severity rating (3/5) but changes the framing.

### P4: The 10,000 step training horizon (W6) is less concerning than I originally rated — UPDATED

**Before:** I rated W6 (10,000 step horizon) as 3/5 and suggested sub-critical runs might simply need more time.

**After:** The Methodological Hawk notes that Table 4 shows delays decrease with data and width — so sub-critical runs at low data fractions have the longest delays, and it's plausible those delays simply exceed the training horizon. However, F2 is specifically designed to test this, and the 0/51 result is genuinely striking. The Naive Reader agrees F2 is a strong clean negative result.

**Updated position:** F2 (0/51 sub-critical runs grokked) is the paper's strongest empirical result. The concern that delays might exceed the training horizon is legitimate but secondary — the key test is whether grokking occurs at all in sub-critical conditions, and 0/51 is a compelling answer. The 10,000 step horizon concern is real but speculative. The W6 severity should remain 3/5 but I should acknowledge the concern is speculative vs. the F2 result is a clean negative.

---

## 4. Claim/Weakness with Most Reviewer Agreement (Consensus Signal)

### Consensus Finding: n_eff(t) is the central load-bearing conjecture

**Agreement across all 5 reviewers:**
- The Adversarial Practitioner (my review): W2, n_eff(t) is a conjecture not a derivation, 4/5
- The Methodological Hawk: W1, n_eff(t) is handwaved as a conjecture, 4/5
- The Theory Critic: W1, n_eff(t) is admitted conjecture but load-bearing, 4/5
- The Domain Expert: W3, n_eff(t) conjecture is central but undefined and unvalidated, 3/5
- The Big-Picture Editor: W3, n_eff(t) is the core mechanism but is hand-waved, 4/5
- The Naive Reader: W1, n_eff(t) described as conjecture but used as if it explains grokking, 4/5

**Consensus signal:** All 6 reviewers flag n_eff(t) as a conjecture-level weakness. This is the strongest consensus across the review panel. The paper explicitly labels it a conjecture ("We do not prove this conjecture formally") but it is central to the entire dynamical story connecting static phase transitions to the temporal phenomenon of grokking.

**Implication:** The paper cannot claim that grokking is explained by the CRISP phase transition mechanism without a derived or measured n_eff(t). The theoretical contribution (Theorem 1: static phase transition) is substantively disconnected from the empirical phenomenon (grokking delay) by this unvalidated conjecture. This is the single most important gap to address.

### Secondary Consensus: F_eff(w) is post-hoc patching

**Agreement across reviewers:**
- The Adversarial Practitioner (my review): W3, post-hoc F_eff(w) rescue, 4/5
- The Methodological Hawk: W9, F_eff(w) introduced ad hoc to save a falsified prediction, 3/5
- The Theory Critic: W2, F_eff(w) is post-hoc reconciliation, 3/5
- The Domain Expert: W2, F_eff(w) introduced without derivation, 4/5
- The Big-Picture Editor: W1, F_eff(w) introduced to explain discrepancy not derived from first principles, 4/5
- The Naive Reader: W2, F_eff(w) is post-hoc curve fitting, 3/5

**Consensus signal:** All 6 reviewers identify F_eff(w) as a post-hoc addition that reconciles a wrong-direction prediction (naive CRISP: n_c ∝ w; observed: n_c decreases with w) without derivation. This is the second-strongest consensus.

### Tertiary Consensus: F3 decorrelation test result not reported

**Agreement across reviewers:**
- The Adversarial Practitioner: part of W2
- The Methodological Hawk: W4, F3 results not reported, 3/5
- The Theory Critic: W8, superposition index measured only on penultimate layer, 2/5
- The Domain Expert: W8, F3 decorrelation test results not reported, 3/5
- The Big-Picture Editor: W6, F3 requires r > 0.8 but doesn't report actual value, 2/5
- The Naive Reader: W3, F3 result not reported, 5/5

**Consensus signal:** 5 of 6 reviewers flag the missing F3 result as a weakness. The Naive Reader rates it 5/5 as the most critical gap. This is the mechanism test that directly validates the superposition-to-clean phase transition story.

---

## 5. Summary of Cross-Examination Findings

| Weakness | My Original Rating | Consensus Rating | Change |
|----------|-------------------|-----------------|--------|
| n_eff(t) conjecture | 4/5 | 4/5 across all 6 reviewers | Confirmed as top priority |
| F_eff(w) post-hoc patching | 4/5 | 3-4/5 across all 6 reviewers | Confirmed as second priority |
| F3 decorrelation result missing | Not explicitly rated | 2-5/5 (5/5 Naive Reader) | Now rated 5/5 standalone |
| Single-task validation | 5/5 | 3-4/5 | Revised to 4/5 |
| β = 2/3 not fitted | Not separately flagged | 3-4/5 | Now rated 4/5 |
| F1 log-loss result not reported | Not flagged | 2/5 | Now rated 4/5 |
| Hyperparameter single point | Not flagged as methodology gap | 2-3/5 | Now rated 3/5 |
| n_c experimental vs theoretical mismatch | Not flagged | 3/5 | Now rated 3/5 |
| 90% threshold vs F1 concern | Not flagged | 4/5 | Now rated 4/5 |

**Key shift:** My review focused heavily on single-task validation (W1, 5/5) and transformer extension (W5, 5/5) as the fundamental limitations. The cross-review reveals that n_eff(t) and F_eff(w) are the theoretical weak points with unanimous consensus, while the task/architecture scope is a acknowledged limitation that is more about framing than falsifiability. The F3 missing result (5/5, Naive Reader) is the most actionable gap — it requires only reporting a number, not new experiments.

---

*— The Adversarial Practitioner*
