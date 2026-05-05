# Cross-Examination: The Naive Reader

**Original Review:** /Users/rj/research-claw/papers/grokking-phase-transitions/paper_council/2026-05-01-1205/01_independent/09_naive_reader.md
**Date:** 2026-05-01
**Cross-Examining Against:** Methodological Hawk, Theory Critic, Adversarial Practitioner, Domain Expert ML, Big Picture Editor

---

## 1. Disagreements with At Least 2 Other Reviewers

### D1: F3 is MISSING, not just unreported — this is a fatal falsification gap

**My position (original):** W3 — F3 decorrelation test result is not reported. Severity 5/5.

**Disagreement with Methodological Hawk (W4):** The Hawk rates this 3/5 and frames it as "F3 decorrelation test results not reported in the bundle." But my original framing was sharper: the test is described but its outcome is absent. This is not a documentation gap — it means the paper's own stated falsification criterion cannot be evaluated. If F3 failed (r < 0.8), the paper would be claiming a mechanism (superposition → clean) that isn't supported.

**Disagreement with Big Picture Editor (W6):** The Editor rates this 2/5, calling it "easy to fix with a number." I disagree — the F3 test is the only one that directly validates the proposed mechanism at feature-space level. F1 and F2 falsify alternative explanations; F3 positively confirms the theory's mechanism. Missing it is not minor.

**Cross-reviewer consensus:** ALL 5 other reviewers flag F3 as unreported. However, only I (Naive Reader) and the Hawk rate it 3-5/5 severity. The Adversarial Practitioner, Domain Expert, and Big Picture Editor give it lower severity (2/5). This disagreement matters: I see F3's absence as undermining the paper's core mechanistic claim; others see it as a documentation issue.

---

### D2: The 90% accuracy threshold is itself a methodological confound that F1 was supposed to address

**My position (original):** W6 — The 90% test accuracy threshold for "grokking" is a discontinuous metric, which is exactly what the Schaeffer smoothness test (F1) warns about as a potential artifact. F1 says if you replace accuracy with a smooth metric (log-loss), the apparent transition should disappear if it's a metric artifact. But F1 is not reported.

**No other reviewer raised this specific point.** The Methodological Hawk (W8) mentions hyperparameter grid as single point but not this. No other reviewer flags that the primary outcome metric is discontinuous and that F1's absence means we cannot rule out metric artifact.

**Disagreement:** I believe this is more serious than other reviewers appreciate. The paper's most striking empirical result — the sharp 0/1 phase boundary — could be an artifact of the hard 90% threshold, not a genuine phase transition. Without F1's log-loss result, this confound is unresolved.

---

## 2. Issues Others Missed That I Now Want to Add

### O1: The theory-measurement gap in n_c definition (NEW)

No other reviewer explicitly flagged that the theoretical n_c (sharp critical point in energy landscape) is a different quantity from the experimental n_c (smallest n where >=50% of seeds grok). The theory defines n_c as a deterministic optimum; the experiment measures a stochastic population threshold. This gap is never bridged. I missed this in my original review but now see it as fundamental — the theory and experiment are measuring different things.

**Updated position:** This is at least 4/5 severity and should be in my top weaknesses.

### O2: nu approaching 1/2 from above has a consequence for beta that is never discussed (NEW)

**My original W5:** nu = 1/2 + O(w^(-1)) means nu is slightly greater than 1/2 for finite w. But the text says nu --> 1/2 as width increases (approaching from above). The consequence for beta (which would be slightly less than 2/3 for finite w) is not discussed.

**No other reviewer mentioned this.** However, the Big Picture Editor (their W2) does flag that β = 2/3 is "asserted, not demonstrated" — which connects to my point about beta never being measured empirically. But none of them caught the directionality subtlety: the theory predicts nu > 1/2 for finite width, hence beta < 2/3, yet no one discusses what measured beta values would confirm or refute this.

### O3: Section 3.2 "Connection to grokking" is narrative not theorem — and this is worse than I thought (NEW)

**My original W9:** Section 3.2 reads as a narrative, not a theorem. After reading the other reviews, I see this more clearly: the section presents the grokking delay as if it follows from the theory, but the only support cited is "if grokking delay correlates with |n - n_c|, this provides indirect evidence" — and no such correlation analysis is reported. This is not just a clarity issue; it's a central mechanistic claim that is asserted without any supporting analysis.

---

## 3. My Positions Updated After Seeing Others

### U1: The n_c decreasing with width is the single most important issue — I understated it

**My original W2:** F_eff(w) is introduced as a reconciliation, not a prediction. Severity 3/5.

**After reading others:** Theory Critic (W3), Adversarial Practitioner (W3), Domain Expert (W1), and Big Picture Editor (W1) ALL flag this as 3-4/5. The Domain Expert calls it "a theory that cannot predict the direction of its primary observable's dependence on its main parameter is not a predictive theory." The Adversarial Practitioner calls it "reverse-engineering, not theory."

I still think I correctly identified it, but I should have rated it 4/5 not 3/5. The fact that the theory's most surprising empirical finding (n_c decreases with width) is a post-hoc accommodation — not a prediction — is the central soundness problem.

### U2: The single-task validation is more serious than I thought

**My original assessment:** W2 (F_eff(w) post-hoc) seemed more central.

**After reading Adversarial Practitioner (W1):** "This is the fundamental limitation. A theory that works on mod-47 but fails on real tasks is not useful." The Adversarial Practitioner gives this 5/5 severity — the highest any reviewer gave any issue.

I now think the single-task limitation (all 120 runs on mod-47) combined with the theory's general claims about grokking and scaling laws is a disqualifying scope mismatch. I should have flagged this more prominently in my original review.

### U3: The training horizon concern for F2 is valid

**My original assessment:** I treated F2's 0/51 sub-critical result as strong evidence.

**After reading Adversarial Practitioner (W6):** "0/51 sub-critical runs grokked at 10,000 steps — but grokking delays at sub-critical fractions are 8,333 steps (Table 4). What happens at 20,000 steps? 50,000 steps? The block could be horizon-bounded, not permanent."

I had not considered this. The fact that delays at sub-critical fractions approach the training horizon (8,333 steps at f=0.5 vs. 10,000 max training) means F2 could be showing "not yet" rather than "never." I should add this caveat to my F2 assessment.

---

## 4. Claim/Weakness with Most Reviewer Agreement (Consensus Signal)

### Highest consensus: F_eff(w) is post-hoc patching

**Reviewers citing F_eff(w) as a key weakness:**
- Naive Reader (W2): "post-hoc curve fitting"
- Methodological Hawk (W9): "ad hoc to save a falsified prediction"
- Theory Critic (W2): "post-hoc reconciliation"
- Adversarial Practitioner (W3): "post-hoc rationalization of a wrong prediction"
- Domain Expert (W2): "introduced without derivation"
- Big Picture Editor (W1): "patched post-hoc"

**All 6 reviewers flag this issue.** Severity ratings: 3-4/5 across all. This is the most consistent criticism in the batch.

### Second highest consensus: n_eff(t) is undefined/unvalidated conjecture

**Reviewers citing n_eff(t):**
- Naive Reader (W1)
- Methodological Hawk (W1)
- Theory Critic (W1)
- Adversarial Practitioner (W2)
- Domain Expert (W3)
- Big Picture Editor (W3)

**All 6 reviewers flag this issue.** The na_eff(t) is load-bearing but admitted as conjecture. This is the second most consistent criticism.

### Third highest consensus: F3 decorrelation results not reported

**Reviewers citing F3:**
- Naive Reader (W3, 5/5)
- Methodological Hawk (W4, 3/5)
- Domain Expert (W8, 3/5)
- Big Picture Editor (W6, 2/5)

**4 out of 6 reviewers flag this.** The Naive Reader (me) gives it highest severity (5/5); the Big Picture Editor gives it lowest (2/5).

### Fourth highest consensus: β = 2/3 is untested

**Reviewers citing this:**
- Naive Reader (W7)
- Methodological Hawk (W10)
- Theory Critic (W9)
- Domain Expert (W4)
- Big Picture Editor (W2)

**5 out of 6 reviewers flag this.** Only the Adversarial Practitioner doesn't explicitly call out β = 2/3 untested.

---

## Summary

| Issue | Reviewers Citing | Avg Severity | Consensus Level |
|-------|-----------------|--------------|-----------------|
| F_eff(w) post-hoc patching | 6/6 | 3.5/5 | HIGHEST |
| n_eff(t) conjecture | 6/6 | 3.5/5 | HIGHEST |
| F3 not reported | 4/6 | 3.3/5 | MEDIUM |
| β = 2/3 untested | 5/6 | 3.0/5 | HIGH |
| Single task validation | 4/6 | 4.0/5 | MEDIUM-HIGH |
| n_c decreasing with width | 4/6 | 3.8/5 | MEDIUM-HIGH |

**The single most important consensus:** The paper's central empirical finding (n_c decreases with width) contradicts its own theorem's prediction, and the resolution (F_eff(w)) is post-hoc. This is the core soundness problem that all reviewers identify.

---

*The Naive Reader*