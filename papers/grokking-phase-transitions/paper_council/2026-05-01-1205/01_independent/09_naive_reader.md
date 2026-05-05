# Naive Reader Review: CRISP Paper

**Paper:** CRISP: Unifying Grokking and Scaling Laws via Phase Transitions in Feature Space
**Reviewer:** The Naive Reader (1st-year PhD student)
**Date:** 2026-05-01

---

## Calibration Note

I am calibrated to "is this paper learnable?" -- I evaluate whether the paper teaches me the framework clearly, whether implicit assumptions are visible, and whether the story holds together without requiring prior expertise in phase transitions or superposition. I expect ~50% of papers I read to clear this bar.

---

## Strengths

**S1. Table 1 is a model of clarity and teachability.**
The table consolidates all six testable predictions with columns for Formula, Observable, Tolerance, and Falsification Criterion. This is the most useful table in the paper -- I knew exactly what the theory claimed before reading the theory section. Each prediction is concrete enough that I could imagine running the experiment myself. This is what a theory paper should do.

**S2. The abstract is honest about the surprising finding.**
The abstract explicitly states that n_c *decreases* with width, "contrary to the naive linear prediction." Authors who bury contradictions in the main text rather than flagging them up front lose my trust. This transparency made me read the reconciliation carefully rather than feeling tricked.

**S3. Falsification tests are integrated into the experimental design (Section 4), not added as an afterthought.**
I appreciate that F1, F2, and F3 are described before the results, not invoked after. Specifically, F2 (0/51 sub-critical runs grokked) is exactly the kind of concrete negative result that makes a theory falsifiable rather than unfalsifiable. The criterion "0 sub-critical runs should grok" is a clean binary test.

**S4. The phase diagram (Table 2 / Figure 2) is visually unambiguous.**
The sharp 0/1 boundary is clear: for w=128, grok rate jumps from 0% at f=0.3 to 100% at f=0.4. This is a striking result that requires no statistics to see. I could show this figure to a non-expert and they would understand why this suggests a phase transition.

**S5. The Discussion section explicitly addresses "what theory gets wrong."**
The paper admits that the naive prediction n_c = alpha * w * log(F) predicts the wrong sign for the width dependence. This intellectual honesty is rare and makes me more willing to trust the other claims.

---

## Weaknesses

**W1. n_eff(t) is described as a "conjecture" but used as if it explains grokking timing (Section 3.2, para 2).**
The connection between training steps and the phase transition is the most important link for explaining grokking, but the paper explicitly says "We do not prove this conjecture formally." The mechanism is: training --> n_eff(t) increases --> crosses n_c --> phase transition --> generalization. But n_eff(t) is never defined, and the paper says a "rigorous dynamical theory" is "important future work." As a reader, I am asked to accept the core story (grokking = phase transition) without the dynamical underpinning. The claim is labeled a conjecture, but the abstract and introduction present it as established fact. **Severity: 4/5**

**W2. F_eff(w) is introduced as a reconciliation, not a prediction.**
The key finding (n_c decreases with width) contradicts the naive formula n_c = alpha * w * log(F). The paper resolves this by redefining F to F_eff(w) = F * (w/w_0)^(-gamma) with gamma > 1. But this is post-hoc curve fitting: the theory predicted one thing, the data showed another, so a new parameter was introduced to fit the data. I could not tell from reading the theory section that this refinement was coming. The paper essentially says: "our theory predicted n_c should increase with w, but it doesn't, so we add a width-dependent effective feature count." This is a significant ad-hoc adjustment. **Severity: 3/5**

**W3. F3 (decorrelation test) result is not reported.**
F3 requires Pearson correlation r > 0.8 between the superposition index S drop point and the grokking onset. The paper reports F1 (log-loss smoothness) and F2 (0/51 sub-critical block) results, but F3 is described but not reported. I looked in the results section and Appendix B and found no mention of the actual r value. The paper claims S "drops sharply" at grokking onset (Fig 4 caption), but I cannot verify the quantitative correlation threshold. This is the test that most directly validates the *mechanism* (superposition-to-clean), not just the existence of a threshold. **Severity: 5/5** -- missing a key falsification result.

**W4. The proof sketches are too compressed; I had to trust the appendix was complete without actually verifying it.**
The proof sketch for Theorem 1 ends with "The full proof with uniform convergence bounds and Hessian analysis at the critical point is in Appendix A." The sketch itself has about 10 lines. I cannot follow the proof structure from the sketch, and the appendix is long. I could not tell whether the proof was solid or hand-wavy without spending several hours on the appendix. For a paper making formal proof claims, this is a problem. **Severity: 3/5**

**W5. nu = 1/2 + O(w^(-1)) appears in Theorem 2, but in Corollary 1 the text says "For large width, nu --> 1/2, predicting beta --> 2/3."**
There is a mismatch: Theorem 2 gives nu = 1/2 + O(w^(-1)) which means nu is slightly greater than 1/2 for finite w. But Corollary 1 says nu --> 1/2 as width increases, meaning nu approaches 1/2 from above. Both are consistent, but the text doesn't explain this subtlety, and the consequence for beta (which would be slightly less than 2/3 for finite w) is not discussed. The scaling exponent beta is never measured in the experiments -- I cannot check whether beta ~= 2/3 or beta ~= something else. **Severity: 2/5**

**W6. The 90% test accuracy threshold for "grokking" is not justified.**
The paper uses a hard 90% accuracy threshold as the grokking criterion (Section 4, "Grokking indicator"). This is a discontinuous metric, which is exactly what the Schaeffer smoothness test (F1) warns against as a potential artifact. F1 says: if you replace accuracy with a smooth metric (log-loss), the apparent transition should disappear if it's a metric artifact. But the paper uses the discontinuous accuracy metric as its primary criterion while acknowledging F1 addresses this concern. I don't understand why the authors didn't run F1 as a reported experiment, or explain what happened if they did. **Severity: 4/5**

**W7. The corollary connecting beta to the sharpening exponent is not validated experimentally.**
Corollary 1 predicts beta --> 2/3 for large width. This is a bridge between the phase transition theory and neural scaling laws. But there is no measurement of beta in the results. Figure 5 shows the scaling law curve (test loss vs training fraction) but does not fit a power law exponent or report beta. The paper predicts beta = 1/(1+nu) = 2/3, but provides no empirical estimate of beta. This is the main corollary linking CRISP to scaling laws, and it is not tested. **Severity: 4/5**

**W8. The notation for the superposition index S(Phi) is introduced in Section 3.1 and used throughout, but the subscript "avg" on ||Phi|| notation in the appendix doesn't appear consistently with the main text.**
In Eq. 5 (main text), S(Phi) is defined as a sum over i != j of |<hat(phi)_i, hat(phi)_j>|^2. In the appendix proof, the same quantity is referenced but the notation for average norm ||Phi||_avg appears without being defined in the main text. I had to infer from context. **Severity: 2/5**

**W9. Section 3.2 "Connection to grokking" reads as a narrative, not a theorem.**
The mechanism described (n_eff(t) increasing with training steps until it crosses n_c) is presented as a conjecture. The phrase "We conjecture that training dynamics can be characterized by an effective dataset utilization n_eff(t)" is honest, but the section then proceeds to describe the grokking delay as if it follows from the theory. The only support is "if grokking delay correlates with |n - n_c|, this provides indirect evidence." But no such correlation analysis is reported. The section reads as plausible storytelling rather than theory. **Severity: 3/5**

**W10. The definition of n_c used in experiments (smallest n where >= 50% of seeds grok) does not appear in the theory section.**
The theory defines n_c as a sharp critical point in the energy landscape. But the experimental n_c is defined as a grokking threshold across seeds. These are different quantities: one is a theoretical optimum of the energy landscape, the other is an empirical detection threshold. The gap between "theoretical n_c" and "observed n_c in experiments" is not bridged. **Severity: 3/5**

---

## Per-Rubric-Dimension Scores

### 1. Originality / Novelty: **7/10**
**Calibration anchor:** 6 = clear improvement/extention, combines existing ideas in non-obvious ways; 8 = substantial conceptual advance.
The unification of grokking and scaling laws via a phase transition mechanism is genuinely novel framing. The energy landscape formalism (Section 3.1) is an extension of Elhage et al. 2022 toy models to a fuller framework with interference penalty and entropic regularization. The closed-form n_c and the connection beta = 1/(1+nu) are new results. However, the core mechanism (superposition-to-clean phase transition) draws heavily on existing work (Elhage et al., Schaeffer et al.), so the advance is in unification and derivation, not in identifying the phenomenon.

### 2. Soundness: **6/10**
**Calibration anchor:** 6 = adequate methodology; some concerns flagged but not fatal; 8 = strong methodology, minor improvements possible.
The empirical methodology is solid (120 runs, 3 seeds, clear criteria). However: (a) F3 decorrelation test result is not reported; (b) the theory has an ad-hoc refinement (F_eff(w)) to match data; (c) beta is never measured empirically; (d) n_eff(t) is an unproven conjecture that is central to the grokking explanation. These are significant gaps in a paper whose main contribution is a theoretical framework. Score 6 reflects "adequate with notable gaps."

### 3. Significance: **8/10**
**Calibration anchor:** 8 = important within the subfield; will be cited heavily; 10 = will change practice/theory across multiple subfields.
If the core claim holds -- that grokking and scaling law knees share a phase transition mechanism -- this is a genuinely important unification. The practical implication (train at n ~ 1.2-1.5 n_c) is potentially valuable. The result that n_c decreases with width is surprising and worth following up. This would be cited heavily in the training dynamics / grokking literature.

### 4. Clarity: **7/10**
**Calibration anchor:** 8 = clear, well-organized, easy to follow; 6 = mostly clear; some sections require re-reading.
The paper is generally well-organized. Table 1 is excellent. The theory section is dense but honest about what is proved vs conjectured. My main confusion was: (a) n_eff(t) appears without definition; (b) F_eff(w) appears as a surprise post-hoc; (c) the F3 result is missing. The appendix is very long and I could not verify the proofs quickly. Overall, a well-organized paper that requires re-reading in places.

### 5. Reproducibility: **9/10**
**Calibration anchor:** 10 = code, data, configs, seeds all released; verified working; 8 = code+configs released; data accessible.
Full reproduction script (reproduce.py), JSON logs for all 120 runs, seeds, hyperparameters, and evaluation criteria are all disclosed. This is among the most reproducible papers I could imagine. Deduct 1 point only because I cannot personally verify the code runs without downloading and executing it.

### 6. Contextualization vs prior work: **7/10**
**Calibration anchor:** 8 = strong coverage; correctly positioned vs SOTA; 6 = adequate coverage; some misses.
The related work section covers grokking, scaling laws, phase transitions, and superposition. The positioning of CRISP vs circuit competition (Nanda et al.) and slingshot dynamics (Thilak et al.) is clear. One gap: the paper claims circuit competition = competition between two energy minima, but does not quantify this mapping. The Schaeffer 2024 paper on emergent abilities is cited as context but the relationship to CRISP (both involve sharp transitions) is not fully articulated. Overall strong but not comprehensive.

### 7. Ethical / Broader Impact: **7/10**
**Calibration anchor:** 8 = adequate coverage; 6 = boilerplate.
The broader impact statement is specific about positive applications (dataset sizing) and does not make inflated claims. No ethical concerns identified. The statement is brief but honest rather than generic boilerplate.

---

## Pointed Questions for the Authors

**Q1. What is the exact definition of n_eff(t)?**
The paper says n_eff(t) is "loosely analogous to the accumulated Fisher information" but never defines it. Without a definition, I cannot evaluate whether the conjecture is plausible. Can you provide an explicit formula for n_eff(t) in terms of the network weights and training data at step t? Or at minimum, a pseudocode algorithm for computing it?

**Q2. How was the correlation threshold r > 0.8 for F3 computed, and what was the observed value?**
F3 requires r > 0.8 between the superposition index S drop point and the grokking onset. The paper describes this test but does not report the actual correlation value. What is it? If it wasn't computed, why not?

**Q3. Why was F1 (log-loss smoothness test) not run or reported as a result?**
F1 is described in Section 4 as a falsification criterion: if the apparent phase transition is a metric artifact from the hard 90% accuracy threshold, then log-loss should show no transition. The paper says "replacing accuracy with a smooth metric (e.g., log-loss, Brier score) should eliminate the apparent transition if it is a metric artifact." Was this test actually performed? If so, what was the result? If not, why not include it given that it directly addresses a known concern about grokking studies?

**Q4. What is the empirical estimate of beta from the scaling law data (Figure 5)?**
The corollary predicts beta --> 2/3 for large width. Figure 5 shows final test loss vs training fraction, but no power-law fit is shown and no beta value is reported. Can you report the measured beta from your data? Does it match 2/3?

**Q5. How is the "observed n_c" (smallest n where >= 50% of seeds grok) related to the theoretical n_c (the critical point of the energy landscape)?**
The theory defines n_c as a sharp optimum in the energy landscape. The experiments measure a grokking threshold across seeds. These are different quantities: the theoretical n_c is an optimum of E(Phi; n), while the observed n_c is an empirical population threshold. What is the formal relationship? Why should the theoretical n_c correspond to the 50% grokking threshold across stochastic training runs?

---

## Falsifiability Test: "What Evidence Would Change My Decision?"

**On the core claim (grokking = phase transition in feature space):**
- If F2 (sub-critical extended training) showed even 1/51 sub-critical runs grokking, I would reject the claim that n_c is a sharp threshold. Currently 0/51 supports the claim strongly.
- If F3 showed that the superposition index S does NOT drop at the same n_c as grokking onset (r < 0.8), I would reject the specific superposition-to-clean mechanism, though the sharp threshold might still exist.
- If F1 showed that log-loss also exhibits a sharp transition at the same n_c, this would suggest the transition is a metric artifact (despite the paper claiming the opposite), which would weaken the physical interpretation.

**On the n_c decreasing with width finding:**
- If follow-up experiments on a different task (e.g., sparse parity, not just mod-47) showed n_c increasing with width, I would treat the current result as specific to the modular arithmetic task.
- If experiments on transformers showed the same trend, I would upgrade my confidence significantly.

**On the beta = 2/3 corollary:**
- If beta were measured to be 0.5 or 1.0 instead of 2/3, I would reject the specific form of the corollary while accepting that a scaling exponent exists.
- If no power-law regime is observed in test loss vs data size, the corollary is untestable and the connection to scaling laws is speculative.

**On the n_eff(t) conjecture:**
- If someone showed that a defined n_eff(t) (e.g., via Fisher information or other) does NOT correlate with grokking delay, the dynamical story connecting training steps to n_c would collapse.

---

## Confidence: **3/5**

I am confident in my evaluation of the empirical results (Table 2, Table 3, Table 4, Figure 2 -- these are clear and well-presented). I am less confident in my evaluation of the theory because: (a) I cannot verify the appendix proofs quickly; (b) n_eff(t) is undefined; (c) F_eff(w) is ad-hoc; (d) beta is never measured. These theory-empirical gaps mean I cannot fully assess whether the theory is correct or whether it is a post-hoc story that fits the data. I give the paper a 3/5 for confidence.

---

## Decision: **Borderline (5.5-6.5 range)**

**Reasoning:** The paper has genuine strengths -- clear organization, honest reporting of contrary results, strong reproducibility, and a genuinely novel unifying claim. The empirical results are clean and well-presented. However, the theory has significant gaps: (1) the central mechanism (n_eff(t)) is unproven; (2) the main finding (n_c decreases with width) required an ad-hoc refinement; (3) F3 decorrelation test result is missing; (4) the beta corollary is never measured; (5) F1 log-loss test was not reported. These gaps matter because the paper's main contribution is the theory, not just the experiments.

A Borderline recommendation reflects that this is a potentially important unification with a solid empirical core but incomplete theoretical validation. It could become a strong Accept if: (i) F3 correlation is reported; (ii) n_eff(t) is either defined or removed as a central claim; (iii) beta is measured from the data; (iv) F_eff(w) is either derived from first principles or positioned more carefully as a data-driven refinement rather than a theory prediction.

---

*The Naive Reader*
