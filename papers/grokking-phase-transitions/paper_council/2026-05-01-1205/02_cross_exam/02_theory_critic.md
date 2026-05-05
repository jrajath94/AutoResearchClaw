# Cross-Examination — The Theory Critic

**Paper:** CRISP: Unifying Grokking and Scaling Laws via Phase Transitions in Feature Space
**Reviewer:** The Theory Critic
**Date:** 2026-05-01
**Phase:** 02_cross_exam

---

## 1. Disagreements with At Least 2 Other Reviewers

### D1: W6 (phase boundary softness at w=32) is not a significant concern
**My position (W6, severity 2/5):** Table 2 shows 33% grok rate at w=32, f=0.6. This contradicts the "sharp 0/1 phase boundary" framing, but is consistent with the theoretical prediction Δn/n_c = O(w^(−ν)) sharpening with width.

**The Naive Reader (S4):** Calls the phase diagram "visually unambiguous" and the "sharp 0/1 boundary" a "striking result." The naive reader treats the sharp boundary as a strength, not a concern.

**The Domain Expert (S3):** Also treats the "near-deterministic phase boundary" as strong empirical evidence, citing "grok rates jumping from 0% to 100% within a single fraction increment."

**Implication:** My W6 (flagging softness at w=32) is a minority position. The majority view treats the phase boundary as empirically clear. I may be over-stating this concern — the paper correctly says "increasingly sharp with width," and the w=32 behavior is consistent with finite-width smoothing rather than a fundamental flaw.

**Revised assessment:** W6 severity should be lowered to 1/5. The "sharp" qualifier in the paper is qualified by width, and the data supports this qualification.

---

### D2: The training horizon concern (sub-critical block might be time-bounded, not permanent) is legitimate
**My position:** I did not raise this concern.

**The Adversarial Practitioner (W6, severity 3/5):** "F2 claims 0/51 sub-critical runs grokked as evidence that sub-critical models never generalize. But maximum training is 10,000 steps. What if grokking delay exceeds this horizon?" Points out that Table 4 shows delays of 8,333 steps at sub-critical fractions — within the training horizon.

**The Methodological Hawk (W5, severity 3/5):** Also flags this, noting that "3 seeds per condition is statistically underpowered for a binary 0/1 outcome" — extended training could produce different outcomes.

**Resolution needed:** The paper should run at least 5 sub-critical runs to 20,000+ steps to establish permanence of the block, not just within-horizon absence. This is a legitimate gap I missed.

---

## 2. Issues Others Missed That I Now Want to Add

### O1: Concentration of measure at finite width (my W4)
The Methodological Hawk, Adversarial Practitioner, and Domain Expert all discuss n_eff(t) and F_eff(w) as the primary theoretical concerns, but none flag that the concentration-of-measure arguments in Appendix A may be vacuous at w=32. The O(w^(−ν)) bound hides constants that could make the transition extremely broad at small widths. This is a distinct theoretical concern that should be added to the cross-examination record.

### O2: Layer-wise PCA justification (my W8)
None of the other reviewers flag that S(Φ) is computed on penultimate-layer activations only. The Adversarial Practitioner mentions F3 (decorrelation) as a strength, but doesn't question whether penultimate-layer measurement is representative of full-network superposition dynamics. This is a methodological gap in the F3 falsification test that the paper does not address.

### O3: Theorem 2 relative error bound (my W5)
The Methodological Hawk flags α calibration as a concern, and the Domain Expert flags the approximation in the proof sketch. But none explicitly ask: what is the relative error |n_c(true) − n_c(approx)| / n_c(true) for w=32, F large? This is a concrete question that would test whether the log(F) term is even meaningful at the parameter regime studied.

---

## 3. My Positions Updated After Seeing Others

### U1: Statistical power (3 seeds) is more serious than I flagged
My review did not flag the 3-seed statistical power issue as a primary concern. The Methodological Hawk (W5, severity 3/5) and Adversarial Practitioner (W7, severity 3/5) both flag this. For a binary 0/1 outcome, 3 seeds gives enormous CIs ([4%, 78%] for 1/3 grok rate). The "sharp 0/1 boundary" claim requires more seeds to be statistically credible near the transition.

**Updated position:** Add statistical power as a significant concern (severity 3/5) alongside the theoretical gaps.

### U2: F1 (log-loss smoothness test) is more problematic than I flagged
My W7 called F1 "insufficiently specific" with severity 2/5. The Naive Reader (W6, severity 4/5) and Methodological Hawk (implicitly, through emphasis on the F1/F2/F3 design) flag this more seriously. The paper uses a hard 90% accuracy threshold as the grokking criterion while simultaneously running F1 to test whether the transition is a metric artifact — but F1 is not actually reported as a result. This is a gap between the paper's falsification design and its reporting.

### U3: β = 2/3 vs Kaplan exponents — this is a consensus concern
All reviewers except my own flag the lack of comparison between β = 2/3 and the established scaling law literature (Kaplan et al. 2020 report β ≈ 0.076, not 0.67). The Big-Picture Editor (W2, severity 3/5), Domain Expert (W4, severity 3/5), and Naive Reader (W7, severity 4/5) all flag this. My own review flagged it (W9) but I did not emphasize it sufficiently. This is a significant weakness that undermines the paper's "unification" claim.

---

## 4. Claim/Weakness with Most Reviewer Agreement (Consensus Signal)

### Strongest Consensus: n_eff(t) is load-bearing but undefined/unvalidated

**Agreement across all 6 reviewers:**

| Reviewer | n_eff(t) concern | Severity |
|----------|-----------------|----------|
| Theory Critic (self) | W1 — load-bearing but admitted as conjecture | 4/5 |
| Methodological Hawk | W1 — handwaved, undermining core mechanism | 4/5 |
| Adversarial Practitioner | W2 — conjecture not derivation | 4/5 |
| Domain Expert | W3 — central but undefined and unvalidated | 3/5 |
| Big-Picture Editor | W3 — core mechanism but hand-waved | 4/5 |
| Naive Reader | W1 — "conjecture" but used as if explaining grokking | 4/5 |

**All 6 reviewers flag n_eff(t) as a central weakness.** This is the clearest consensus signal in the review bundle. It is also the most fatal to the paper's core claim: Theorem 1 proves a static phase transition, but grokking is a dynamic phenomenon, and the link between them (n_eff(t)) is explicitly admitted as unproven.

**Secondary consensus (5/6 reviewers):** F_eff(w) is post-hoc, not derived. The Big-Picture Editor, Domain Expert, Methodological Hawk, Adversarial Practitioner, and Naive Reader all flag this. I flag it as W2. The direction reversal of n_c with width (opposite of Theorem 2's prediction) required an ad-hoc parameter introduction without derivation.

**Tertiary consensus (4/6 reviewers):** F3 decorrelation results not reported. The Naive Reader (W3, severity 5/5 — missing key falsification result), Methodological Hawk (W4, severity 3/5), Domain Expert (W8, severity 3/5), and Big-Picture Editor (W6, severity 2/5) all flag this. The Adversarial Practitioner treats F3 as a strength (S5), but does not note the missing correlation value.

---

## 5. Summary of Cross-Examination Findings

1. **My W6 (phase boundary softness at w=32) is a minority position.** The majority view treats the phase boundary as sharp and compelling. I should lower this concern.

2. **I missed the training horizon concern** that the Adversarial Practitioner and Methodological Hawk raised. Sub-critical block permanence is not established — only within-horizon absence.

3. **I should add three issues others missed:** concentration-of-measure vacuity at finite width (my W4), layer-wise PCA justification (my W8), and explicit relative error bounds for Theorem 2 (my W5).

4. **My confidence in the theoretical framework (4/5)** is higher than other reviewers (3/5). I should reconsider whether the n_eff(t) gap justifies this higher confidence given that it is load-bearing and admitted as conjecture.

5. **The consensus signal is clear:** n_eff(t) is the primary weakness (6/6), F_eff(w) is post-hoc (5/6), F3 results missing (4/6). The paper's theoretical contributions are real but the core mechanism linking statics to dynamics is not proven.

---

## 6. Updated Decision Note

After cross-examination: **Borderline** is the correct landing spot. The consensus on n_eff(t) as a load-bearing unproven conjecture is the strongest signal. The paper's theoretical framework (Theorem 1, phase transition in feature space) is legitimate, but its application to grokking dynamics rests on an unvalidated conjecture. Accept would require at minimum: (a) empirical tracking of n_eff(t) trajectories across training, or (b) a heuristic derivation with experimental validation, plus (c) reporting of F3 correlation values.

---

— The Theory Critic