# Cross-Examination — The Big-Picture Editor

**Paper:** CRISP: Unifying Grokking and Scaling Laws via Phase Transitions in Feature Space
**Reviewer:** The Big-Picture Editor
**Date:** 2026-05-01
**Session:** Cross-examining 5 other independent reviews

---

## 1. Disagreements with at least 2 Other Reviewers

### D1: F_eff(w) is post-hoc repair, not theory — Theory Critic, Domain Expert, Methodological Hawk, Adversarial Practitioner ALL agree

My position: I flagged this as severity 4/5 and framed it as a "reconciliation" that needs derivation or acknowledgment.

**Disagreement:** The Theory Critic calls it severity 3/5 and frames it as "a hypothesis with one free parameter" but stops short of calling it fatal. The Domain Expert and Methodological Hawk agree with my 4/5 severity. The Adversarial Practitioner calls it 4/5 and explicitly calls it "reverse-engineering, not theory."

**My updated position:** After cross-examination, I strengthen my view: F_eff(w) is the paper's most serious flaw because it means the theory cannot predict the direction of its primary observable's dependence on its main parameter (width). The Theory Critic's more lenient 3/5 seems inconsistent with his own W2 framing — if a theory's central prediction goes the wrong direction and is patched with a free exponent, that's not a hypothesis, it's curve-fitting.

### D2: The β = 2/3 corollary is untested — all 5 reviewers agree implicitly

My position: I flagged this as 3/5, calling it "the paper's most exportable prediction but untested."

**Cross-examination finding:** None of the reviewers report measuring β from Figure 5. The Naive Reader (W7) explicitly calls out that "beta is never measured in the experiments." The Domain Expert (W4) notes the paper "never fits a power law to its scaling curve." This is unanimous concern I initially under-weighted at 3/5 — I now think it should be 4/5 given how central the corollary is to the unification claim.

### D3: 3 seeds is statistically underpowered for binary 0/1 outcomes — Methodological Hawk and Adversarial Practitioner explicitly flag this

My position: I did not independently flag the seed count as a weakness (I mentioned reproducibility but not seed count per se).

**Disagreement:** The Methodological Hawk provides the quantitative argument: with 3 Bernoulli trials, a 33% grok rate has 95% CI [4%, 78%] — indistinguishable from a coin flip. The Adversarial Practitioner (W7) independently flags the "p99 failure is what matters in production" argument. The Naive Reader does not flag this but the Domain Expert scores Reproducibility 9/10 despite this gap.

**My updated position:** I should have flagged this. The "sharp 0/1 phase boundary" claim rests on near-deterministic outcomes at w=128 but becomes noisy at w=32 (33% at f=0.6). With more seeds, the boundary sharpness could be questioned more rigorously. I now add this to my concerns.

---

## 2. Issues Others Missed That I Now Want to Add

### NEW-1: The β = 2/3 corollary conflicts with Kaplan et al. 2020 (β ≈ 0.076) without explanation

**Not raised by others.** I flagged "Missing comparison to Kaplan et al. 2020 / Hoffmann et al. 2022" (severity 3/5) but did not connect it to the β discrepancy. The Theory Critic raises this in Q7 but frames it as a clarification question, not a weakness. The Domain Expert raises β = 2/3 not validated but does not compare to empirical scaling literature.

**The issue:** The paper claims β = 2/3 connects CRISP to neural scaling laws. But Kaplan et al. 2020 report β ≈ 0.076 for language models — orders of magnitude different. The paper never reconciles this. If the corollary is to be believed as a "unification," it must explain why LLM scaling exponents are ~0.08 not ~0.67. Without this explanation, the unification claim is undermined.

**Severity:** 3/5 — I'm promoting this from my original 3/5 to a more central concern after seeing no other reviewer address it directly.

### NEW-2: The 90% accuracy threshold is itself a discontinuous metric that F1 warns against

**Not raised by others.** The Naive Reader (W6) raises the related point that "the 90% test accuracy threshold for 'grokking' is not justified" but does not connect it to the F1 Schaeffer smoothness test. The Methodological Hawk raises hyperparameter grid as a single point but not this specific metric issue.

**The issue:** F1 says: replace the hard accuracy metric with a smooth metric (log-loss) and the apparent transition should disappear if it's a metric artifact. But the paper uses the hard 90% accuracy threshold as its primary grokking criterion while citing F1 as a falsification test. The paper never reports whether F1 was actually run and what its result was. This is different from F3 not being reported — F3 is described but results absent; F1 is described as passed but never shown.

**Severity:** 3/5 — I'm adding this as a methodological gap in the falsification design.

### NEW-3: The abstract and introduction overstate the theory's maturity

**Not raised by others as a separate issue** — this is my editorial observation from reading the full paper context.

**The issue:** My review says "the abstract explicitly states that n_c decreases with width, contrary to the naive linear prediction" — which I praised as intellectually honest. But the abstract also presents n_eff(t) as if it explains grokking dynamics, when it is explicitly labeled a conjecture in the paper. The introduction frames Theorem 1 as establishing grokking = phase transition, when the dynamical link (n_eff(t)) is admitted conjecture. This creates a framing-execution gap.

**Severity:** 2/5 — minor but worth noting for a theory paper.

---

## 3. My Positions Updated After Seeing Others'

### UPDATE-1: I should have scored Soundness lower

My original Soundness: 6/10

The Methodological Hawk gave 5/10. The Theory Critic gave 5/10. The Adversarial Practitioner gave 5/10. The Domain Expert gave 5/10. Every other reviewer except the Naive Reader (6/10) scored Soundness at or below my 6.

**My updated position:** 5/10 is more accurate. The F3 decorrelation test results are not reported, n_eff(t) is the load-bearing conjecture that is central but undefined, F_eff(w) is post-hoc, and β is untested. These are not minor gaps — they are fundamental issues for a theory paper whose contribution is the theory itself.

### UPDATE-2: I under-weighted the single-task validation concern

My original severity for single task: 3/5

The Adversarial Practitioner gave this 5/5 (calling it "rejection trigger"). The Methodological Hawk gave 4/5. The Naive Reader did not flag it as major. The Domain Expert flagged it as part of W9 but at 2/5.

**My updated position:** The single-task validation is more serious than I assessed. A theory claiming general mechanisms of grokking and scaling, validated exclusively on mod-47 with 2-layer MLPs, is a theory about one task, not a general theory. I now align with the 4-5/5 severity from the other reviewers.

### UPDATE-3: The Theory Critic's "Borderline/Accept leaning Accept" is an outlier I disagree with

The Theory Critic gave a weighted average of ~7.64 and a decision of "Borderline/Accept (leaning toward Accept)." All other reviewers (Methodological Hawk, Domain Expert, Adversarial Practitioner, Naive Reader, and myself) landed at Borderline with scores in the 5.5-6.5 range.

**My disagreement:** The Theory Critic's leniency seems to rest on (a) the static theorem being "correctly proved" and (b) honest flagging of n_eff(t) as conjecture. But a theorem about static energy landscapes that doesn't actually explain the dynamic phenomenon it claims to explain is not sufficient for acceptance at NeurIPS. The Theory Critic acknowledges "the main conjecture flag" but still leans Accept — I lean the other way. The experimental design gaps (single task, no F3 results, post-hoc F_eff(w)) are disqualifying at current scope.

---

## 4. Claim/Weakness with Most Reviewer Agreement (Consensus Signal)

**Strongest consensus: F3 decorrelation test results are not reported** (flagged by 4 of 5 reviewers)

- Methodological Hawk: "F3 decorrelation test results not reported in the bundle" (severity 3/5)
- Adversarial Practitioner: "F3 requires Pearson correlation r > 0.8... the paper never reports the actual correlation value" (W3, severity 5/5 — highest he gives)
- Domain Expert: "F3 decorrelation test results not reported... the key evidence for it is missing from the results" (W8, severity 3/5)
- Naive Reader: "F3 (decorrelation test) result is not reported... missing a key falsification result" (W3, severity 5/5 — highest he gives)

I flagged this only at 2/5 — I was wrong. This is the mechanism-validation gap. The entire story (superposition → clean phase transition causing grokking) rests on F3 passing, and the paper doesn't report whether it did.

**Second strongest consensus: n_eff(t) is central but undefined/conjecture**

All 6 reviewers (including myself) flag n_eff(t) as a concern. Severity ranges from 3/5 to 4/5. This is the most uniformly acknowledged weakness.

**Third strongest consensus: n_c decreases with width (opposite of naive prediction) requiring post-hoc F_eff(w)**

5 of 6 reviewers flag this. The Naive Reader calls it "post-hoc curve fitting" at severity 3/5. My 4/5 is the highest. The Adversarial Practitioner calls it "reverse-engineering, not theory" at 4/5. The Domain Expert calls it the paper's "central empirical finding but it directly contradicts the theorem it claims to validate" at 4/5.

---

## Summary of Cross-Examination Findings

| Finding | Reviewers Agreeing | My Original Position | Updated Position |
|---------|-------------------|---------------------|------------------|
| F3 results not reported | 4/5 | 2/5 (too low) | Promoted to 4/5 |
| n_eff(t) undefined/conjecture | 6/6 (unanimous) | 4/5 | Maintained at 4/5 |
| F_eff(w) post-hoc | 5/6 | 4/5 | Maintained, Theory Critic disagrees at 3/5 |
| Single task validation | 4/6 | 3/5 (too low) | Promoted to 4/5 |
| β = 2/3 untested | 5/6 | 3/5 (too low) | Promoted to 4/5 |
| Missing Kaplan comparison | 1/6 (only me) | 3/5 | NEW issue, 3/5 |
| 3 seeds underpowered | 2/5 | Not flagged | NEW issue from cross-exam, 3/5 |
| Soundness score | 5/6 reviewers ≤ 6/10 | 6/10 (too high) | Revised to 5/10 |

---

**Decision remains: Borderline** — but my confidence in this decision is now higher after seeing the cross-reviewer agreement. The consensus signal on F3, n_eff(t), and F_eff(w) is clear. The paper needs (1) F3 correlation reported, (2) n_eff(t) derived or removed as central claim, (3) either derivation of F_eff(w) or reframe as empirical correction. Without these, Borderline is correct.

**— The Big-Picture Editor**