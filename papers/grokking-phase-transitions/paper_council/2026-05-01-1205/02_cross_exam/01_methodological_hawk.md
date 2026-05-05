# Cross-Examination — The Methodological Hawk

**Paper:** CRISP: Unifying Grokking and Scaling Laws via Phase Transitions in Feature Space
**Reviewer:** The Methodological Hawk
**Date:** 2026-05-01
**Source reviews:** 01_methodological_hawk (self), 02_theory_critic, 05_adversarial_practitioner, 06_domain_expert_ml, 08_big_picture_editor, 09_naive_reader

---

## 1. Disagreements with At Least 2 Other Reviewers

### D1: F_eff(w) is a "post-hoc repair" vs "reconciliation hypothesis" (AGREE across 6 reviewers but DISAGREE on severity/framing)

- **My original position (W9, severity 3/5):** "F_eff(w) is introduced ad hoc to save a falsified prediction." Flagged as concerning but not fatal.
- **Theory Critic (W2, 3/5):** "F_eff(w) is a post-hoc reconciliation with no derivation... It could be curve-fitting."
- **Domain Expert (W2, 4/5):** "F_eff(w) introduced without derivation... A theory that cannot predict the direction of its primary observable's dependence on its main parameter is not a predictive theory."
- **Adversarial Practitioner (W3, 4/5):** "Post-Hoc F_eff(w) Rescue of Wrong Direction Prediction... This is reverse-engineering, not theory."
- **Big Picture Editor (W1, 4/5):** "The central prediction goes the wrong direction — and is patched post-hoc."
- **Naive Reader (W2, 3/5):** "F_eff(w) is introduced as a reconciliation, not a prediction."
- **Disagreement with Theory Critic:** I rated this 3/5, Theory Critic also 3/5 — but Domain Expert and Adversarial Practitioner rate it 4/5, and Big Picture Editor rates it 4/5. I may be underweighting this. The fact that 4 of 6 reviewers assign severity 4/5 suggests my 3/5 is too lenient. The issue is not just that F_eff(w) lacks derivation — it's that the theory's central prediction (n_c ∝ w) went the wrong direction and required a free parameter to fix. This is more serious than curve-fitting; it's theory accommodation.
- **Revised assessment:** Severity should be 4/5. The prediction went wrong direction, was patched with a free exponent, and that exponent (γ) is not independently validated.

### D2: F1 (Schaeffer smoothness test) is sufficient vs potentially insufficient

- **My original position:** Did not flag F1 as problematic.
- **Theory Critic (W7, 2/5):** "F1 is insufficiently specific... The test compares different outcome variables (test accuracy vs log-loss)."
- **Naive Reader (W3, severity 4/5 — highest severity):** "F1 (log-loss smoothness test) was not run or reported as a result... The paper uses the discontinuous accuracy metric as its primary criterion while acknowledging F1 addresses this concern. I don't understand why the authors didn't run F1 as a reported experiment."
- **Big Picture Editor (S2):** "Three built-in tests (Schaeffer smoothness, sub-critical extended training, feature decorrelation) are more than most phase-transition papers attempt."
- **Disagreement:** I accepted F1 as designed. Naive Reader and Theory Critic both raise concerns that I missed. The Naive Reader's point is particularly sharp: if F1 is a falsification test for a known artifact concern, why was the result not reported? This suggests either (a) the test was run and was inconclusive/negative and thus omitted, or (b) the test was not run. Either way is problematic for a paper that prominently features falsification tests.
- **Revised assessment:** F1 is potentially insufficient because the result was not reported. This should have been flagged in my review. The falsification test for the metric artifact concern is mentioned but its outcome is undisclosed.

### D3: Training horizon for F2 (sub-critical block) is permanent vs time-bounded

- **My original position:** Accepted F2 result (0/51 sub-critical runs grokked) as evidence of permanent block.
- **Adversarial Practitioner (W6, 3/5):** "0/51 sub-critical runs grokked at 10,000 steps — but grokking delays at sub-critical fractions are 8,333 steps. What happens at 20,000 steps? The block could be horizon-bounded, not permanent."
- **Theory Critic:** Does NOT flag this concern.
- **Domain Expert:** Does NOT flag this concern.
- **Naive Reader:** Does NOT flag this concern.
- **Disagreement:** I accepted the F2 result at face value. Adversarial Practitioner raises a legitimate concern: if sub-critical delays are 8,333 steps and max training is 10,000 steps, the "block" could simply be a horizon effect rather than a true permanent inability. I should have flagged this as an open question.
- **Revised assessment:** This is a legitimate concern that should be acknowledged. Extended training experiments (50,000+ steps) on sub-critical runs would distinguish "never" from "not yet."

### D4: n_c decreases with width — strength vs weakness framing

- **My original position:** Table 3 shows n_c monotonically *decreases* with width — opposite of naive prediction — requiring F_eff(w) patch. I flagged this in W9.
- **Big Picture Editor (S4, strength):** "The monotonic decrease in n_c with width (Table 3/Fig 3) is a surprising, testable finding that genuinely falsifies naive CRISP prediction."
- **Theory Critic (S4, strength):** "Identifying the n_c(w) direction reversal is intellectually honest."
- **Domain Expert (W1, weakness):** "n_c direction reversal undermines Theorem 2's predictive claim."
- **Adversarial Practitioner (W3, weakness):** "Post-Hoc F_eff(w) Rescue of Wrong Direction Prediction."
- **Disagreement on framing:** Big Picture Editor and Theory Critic frame the n_c-decreasing-with-width finding as a *strength* (surprising empirical result, intellectually honest). I framed it as a weakness requiring post-hoc patching. Domain Expert and Adversarial Practitioner agree with my framing. Who is right?
- **Analysis:** Both framings can be correct. The *finding* (n_c decreases with width) is surprising and valuable. The *theory's treatment* of it (F_eff(w) introduced post-hoc without derivation) is a weakness. The Big Picture Editor and Theory Critic are right that the empirical result is important. I am right that the theoretical reconciliation is post-hoc. The appropriate resolution: acknowledge the finding as genuine while acknowledging F_eff(w) needs first-principles derivation to be satisfying.

---

## 2. Issues Others Missed That I Now Want to Add

### O1: Hyperparameter grid is a single point (unique to my review)

No other reviewer explicitly flagged that the entire 120-run experiment uses exactly ONE learning rate (lr=0.03) and ONE weight decay (wd=0.3). This is not just a reproducibility issue — it's a validity issue. Grokking is known to be sensitive to optimization dynamics. If the phase transition phenomenon only occurs at lr=0.03 and not at lr=0.01 or lr=0.1, the theory's generality is compromised. I should elevate this from W8 (2/5) to at least 3/5.

**New severity: 3/5.** The theory claims general mechanisms but all experiments are at a single hyperparameter point.

### O2: No comparison against prior grokking baselines (unique to my review)

No other reviewer explicitly called for comparing against prior grokking interventions (Power et al. 2022, Nanda et al. 2023). The paper claims to explain grokking but does not demonstrate that its proposed mechanism (superposition-to-clean phase transition) outperforms or better explains the phenomenon than circuit competition or other alternatives. This is a significant gap for a theory paper.

### O3: 3 seeds provides no visibility into tail outcomes (partially shared but with different emphasis)

I argued W5: "3 seeds per condition is statistically underpowered for a binary 0/1 outcome — a grok rate of 33% (1/3) has a 95% CI of [4%, 78%]." Adversarial Practitioner flagged W7 ("Only 3 Seeds — Extreme Outcomes Possible in Production") but framed it as production viability. I framed it as a statistical inference problem. Neither explicitly quantified the CI width. The Naive Reader did not flag this. I should be more specific: with 3 Bernoulli trials, the CI is so wide that near-boundary conditions (e.g., w=32 at f=0.6: 33% grok rate) are indistinguishable from a 50/50 coin flip. The "sharp 0/1 phase boundary" claim is not statistically supported at boundary conditions.

---

## 3. My Positions That I'm Updating After Seeing Theirs

### U1: n_eff(t) severity confirmed — but I may have understated it

- **My original severity: 4/5**
- **All 6 reviewers flag this** (Theory Critic W1: 4/5, Naive Reader W1: 4/5, Adversarial Practitioner W2: 4/5, Domain Expert W3: 3/5, Big Picture Editor W3: 4/5, myself W1: 4/5)
- **Universal consensus:** This is the most consistently flagged concern.
- **Theory Critic makes an important point I didn't fully articulate:** "Theorem 1 proves a static phase transition in the energy landscape as a function of dataset size n. Grokking is a dynamic phenomenon. Without n_eff(t), Theorem 1 doesn't actually prove grokking is explained by this mechanism." My framing was about the delay explanation; Theory Critic's framing is about the theorem's scope — Theorem 1 only covers the static case, not the dynamic case.
- **Updated position:** n_eff(t) is not just a missing derivation — it's a gap that means Theorem 1 cannot actually explain grokking. This is closer to a fatal flaw than I initially assessed. Severity: 5/5.

### U2: F3 decorrelation test results — I underweighted the missing result

- **My original severity: 3/5** (W4: "F3 results not reported in the bundle")
- **Naive Reader severity: 5/5** (W3: "missing a key falsification result")
- **Domain Expert severity: 3/5** (W8)
- **Theory Critic severity: not explicitly rated but Q5 asks what correlation was observed**
- **My analysis:** The Naive Reader's 5/5 rating is justified. F3 is the test that most directly validates the mechanism (superposition-to-clean). F2 validates that n < n_c prevents generalization. F1 validates that the transition isn't a metric artifact. But F3 validates WHY the transition happens — the feature space changes at the same time as the behavior change. Without F3 results, the paper has validated the existence of a threshold (F2) and ruled out one artifact (F1), but not the proposed mechanism. This is not a minor omission.
- **Updated severity: 4/5** (from 3/5). The Naive Reader's 5/5 is defensible; my 3/5 was too lenient.

### U3: Single task validation severity — I'm aligned with the consensus now

- **My original severity: 4/5** (W3: "Only one task (mod-47) validates a theory claiming general mechanisms")
- **Adversarial Practitioner severity: 5/5** (W1: "This is the fundamental limitation")
- **Big Picture Editor severity: 3/5** (W5)
- **Theory Critic severity: 2/5** (W10)
- **My updated assessment:** I was correct to flag this as serious. The theory makes universal claims about phase transitions in feature space and connects to neural scaling laws across architectures. All validation is on a single synthetic task with 2-layer MLPs. The Domain Expert makes a point I didn't fully emphasize: the theory assumes F (latent feature count) is known for mod-47 (exactly 47), but for any real task F is unknown. The theory cannot be tested on tasks where F is not known a priori.
- **Updated position:** Severity 4/5 stands. The lack of task diversity is a fundamental limitation, not just a gap.

### U4: β = 2/3 corollary — I correctly flagged it but others elaborated the discrepancy more

- **My original severity: 3/5** (W10: "β = 2/3 not tested against real scaling law data")
- **Big Picture Editor severity: 3/5** (W2: "The β = 2/3 corollary is asserted, not demonstrated")
- **Domain Expert severity: 3/5** (W4: "Corollary 1 not validated empirically")
- **Theory Critic severity: 3/5** (W9: "β = 2/3 is not compared to established scaling law measurements")
- **Naive Reader severity: 4/5** (W7)
- **The Domain Expert makes a point I missed:** "Kaplan et al. 2020 report β ≈ 0.076–0.078 for language models, nowhere near 2/3." The paper claims β = 2/3 connects to scaling law literature, but the actual empirical scaling exponents from LLM studies are orders of magnitude different. The paper never discusses this discrepancy.
- **Updated position:** I should have emphasized the Kaplan discrepancy more prominently. β = 2/3 is not just untested — it contradicts established empirical results from the scaling law literature without explanation. This undermines the "unification" claim.

---

## 4. Claim/Weakness with the Most Reviewer Agreement (Consensus Signal)

### Consensus #1: n_eff(t) is undefined/unvalidated (ALL 6 reviewers flag this)

| Reviewer | Severity | Exact phrasing |
|----------|----------|----------------|
| Methodological Hawk | 4/5 | "n_eff(t) is handwaved as a conjecture, undermining the core mechanism" |
| Theory Critic | 4/5 | "n_eff(t) is admitted conjecture, but it is load-bearing" |
| Naive Reader | 4/5 | "n_eff(t) is described as a 'conjecture' but used as if it explains grokking timing" |
| Adversarial Practitioner | 4/5 | "n_eff(t) is a Conjecture, Not a Derivation" |
| Domain Expert | 3/5 | "n_eff(t) conjecture is central but undefined and unvalidated" |
| Big Picture Editor | 4/5 | "n_eff(t) is the core mechanism but is hand-waved" |

**Consensus strength: UNANIMOUS.** Every reviewer flags this. Average severity: 3.8/5. This is the clear consensus winner.

### Consensus #2: F_eff(w) is post-hoc/underived (ALL 6 reviewers flag this)

| Reviewer | Severity |
|----------|----------|
| Methodological Hawk | 3/5 → revised to 4/5 |
| Theory Critic | 3/5 |
| Naive Reader | 3/5 |
| Adversarial Practitioner | 4/5 |
| Domain Expert | 4/5 |
| Big Picture Editor | 4/5 |

**Consensus strength: UNANIMOUS.** Average severity: ~3.7/5. The theory's central prediction went wrong direction and was patched with an underived free parameter.

### Consensus #3: Single task/architecture validation (5 of 6 reviewers flag this)

| Reviewer | Severity |
|----------|----------|
| Methodological Hawk | 4/5 |
| Adversarial Practitioner | 5/5 |
| Big Picture Editor | 3/5 |
| Theory Critic | 2/5 |
| Domain Expert | 2/5 |

**Consensus strength: NEAR-UNANIMOUS (5/6).** Average severity: 3.2/5. Gap: Theory Critic and Domain Expert rate it lower (2/5), suggesting they see it as a limitation acknowledgment rather than a fatal flaw.

### Consensus #4: β = 2/3 not validated (5 of 6 reviewers flag this)

| Reviewer | Severity |
|----------|----------|
| Methodological Hawk | 3/5 |
| Theory Critic | 3/5 |
| Naive Reader | 4/5 |
| Big Picture Editor | 3/5 |
| Domain Expert | 3/5 |

**Consensus strength: NEAR-UNANIMOUS (5/6).** Average severity: 3.2/5. The corollary linking CRISP to scaling laws is untested and never compared to Kaplan et al. (β ≈ 0.076).

---

## Summary of Cross-Reviewer Dynamics

**My cross-examination conclusions:**

1. **I was too lenient on F_eff(w)** — revising severity from 3/5 to 4/5 given 4 of 6 reviewers assign 4/5
2. **I missed F1 reporting gap** — Naive Reader and Theory Critic both point out F1 result was not reported; I should have flagged this
3. **I missed training horizon concern for F2** — Adversarial Practitioner raises a legitimate point I didn't consider
4. **My unique contributions**: hyperparameter grid single point, no prior baseline comparison, statistical argument for why 3 seeds is underpowered for binary outcomes
5. **Universal consensus winner**: n_eff(t) is the biggest issue (6/6 reviewers, avg severity 3.8/5), followed by F_eff(w) (6/6, avg ~3.7/5)
6. **The n_c-decreasing-with-width finding** is both a strength (surprising empirical result) and a weakness (theory required post-hoc patching). The reviewers who call it a strength are right about the empirical finding; those who call it a weakness are right about the theoretical treatment.

---

**Final priority list for revision:**
1. **n_eff(t)** — define it quantitatively or reframe Theorem 1's scope (UNANIMOUS 6/6)
2. **F_eff(w)** — derive from first principles or acknowledge as empirical fit (UNANIMOUS 6/6)
3. **β = 2/3** — measure from data or compare to Kaplan/Hoffmann (5/6)
4. **F3 results** — report the actual correlation coefficient (5/6, avg severity ~3.5/5)
5. **Multi-task validation** — at minimum one additional task (5/6, avg severity ~3.2/5)
6. **Hyperparameter robustness** — multiple learning rates (unique contribution)
7. **Prior baseline comparison** — at minimum one re-implemented baseline (unique contribution)

— The Methodological Hawk
