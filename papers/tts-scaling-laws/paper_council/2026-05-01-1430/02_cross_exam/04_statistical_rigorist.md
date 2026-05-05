# Cross-Examination Report — Statistical Rigorist

**Reviewer:** The Statistical Rigorist
**Date:** 2026-05-01
**Source reviews:** 04 (self), 05 (Adversarial Practitioner), 06 (Domain Expert ML), 07 (Reproducibility Archeologist), 08 (Big-Picture Editor), 09 (Naive Reader)

---

## 1. Disagreements with at least 2 other reviewers

### D1: S=8 sample size — severity disagreement on an agreed-upon problem
**My position:** W2 (Severity 5/5): S=8 Bernoulli trials produce enormous variance in binomial likelihood estimates. BIC comparison on these noisy outcomes is unreliable without sensitivity analysis.

**Other reviewers flagging this:**
- **Big-Picture Editor** W4: "S=8 samples per cell makes the binomial BIC unreliable" (severity 4/5)
- **Adversarial Practitioner** W1: "S=8 samples/cell minimum for binomial-likelihood BIC to be trustworthy" (severity 4/5)
- **Domain Expert ML** W2: "S=8 is likely underpowered for binomial-likelihood BIC" (severity 3/5)
- **Naive Reader** W3: "S=8 samples per cell may be insufficient for binomial-likelihood BIC" (severity 4/5)

**Agreement count: 5 of 6 reviewers.** All except Reproducibility Archeologist explicitly flag S=8 as a problem.

**My disagreement:** I maintained 5/5 severity. Others rated 3-4/5. This is a disagreement on severity calibration, not on the existence of the problem. After seeing the Reproducibility Archeologist's W3 (near-random accuracy at 2-6%), I now recognize my original severity was actually **too low** — the compound problem (S=8 AND near-random accuracy) is far more damaging than S=8 alone.

**Updated position:** S=8 with 2-6% accuracy means cells have expected 0-2 successes out of 8 trials. The binomial likelihood is degenerate in this regime. Severity 5+/5.

---

### D2: Near-random accuracy levels — I MISSED this compound issue
**My original position:** Did not explicitly flag gross accuracy levels (2-6% on GSM8K) as a separate concern from S=8.

**Other reviewers flagging this:**
- **Reproducibility Archeologist** W3: "Qwen-0.5B achieves 2-3% accuracy on GSM8K across all budgets... at these accuracy levels, with S=8 samples, most cells have 0-2 correct samples out of 8. The accuracy curves being fit are extremely noisy binary outcomes. The BIC model comparison on these near-random curves is essentially fitting noise." (severity 5/5)
- **Big-Picture Editor** W1: "72% of cells have ZERO accuracy variation — they are trivially better fit by a flat/staircase function because nothing changes" (severity 5/5)

**Agreement count: 3 reviewers (RA, BPE, DE partially)**

**My updated position:** This is a new issue I must add. At 2-6% accuracy with S=8, the expected number of successes per cell is 0.16-0.52. Most cells have zero or one success. The BIC comparison between staircase and sigmoid on these degenerate outcomes is meaningless. RA's suggested falsification test (shuffle labels before BIC fitting) is the correct remedy.

---

### D3: p=0.23 misrepresentation — consensus on the problem, disagreement on severity
**My original position:** W1 (Severity 4/5): p=0.23 means NOT statistically significant. Cannot be reported as "matches" equivalence. Paper uses absence of evidence as evidence of equivalence.

**Other reviewers flagging this:**
- **Big-Picture Editor** W2: "p=0.23 result dressed as 'matches fixed-budget-512 accuracy' is misleading" (severity 5/5)
- **Adversarial Practitioner** W3: "p=0.23 is misrepresented as 'matches' accuracy" (severity 4/5)

**Agreement count: 3 reviewers**

**My disagreement:** I rated 4/5; BPE rated 5/5. My calibration was correct — the error is correctable and not fatal, but it is a statistical mistake that should be fixed. The token savings (75%) is the legitimate finding and should be foregrounded instead.

---

### D4: Multiple-testing correction — consensus on the problem, disagreement on framing
**My original position:** W4 (Severity 5/5): No Benjamini-Hochberg correction across 300 BIC decisions. Garden of Forking Paths.

**Other reviewers flagging this:**
- **Big-Picture Editor** W5: "No multiple-testing correction undermines the headline claims" (severity 4/5)
- **Adversarial Practitioner** W6: "Multiple comparisons across BIC Δ thresholds not controlled" (severity 3/5)
- **Reproducibility Archeologist** W8: "Multiple comparisons not corrected (9 tests)" (severity 2/5)

**Agreement count: 4 reviewers**

**My disagreement:** RA gave this 2/5 (lower severity), AP 3/5, BPE 4/5. I maintain 5/5 as the correct severity because the BIC classification is the paper's primary empirical claim. If BH correction at FDR=0.05 reduces the staircase rate below 60%, the empirical paper collapses. This is the single most important falsifiability test.

---

## 2. Issues OTHERS Missed That I Now Want to Add

### O1: BIC threshold flatness suggests penalty-dominance, not signal
**Reproducibility Archeologist** W5 identified: BIC threshold sensitivity is essentially flat (98.7% at Δ=0 vs 99.7% at Δ=10). RA interprets this as "classification being dominated by the penalty term rather than genuine signal."

**Why I missed this:** I flagged W5 (threshold misapplied) but did not examine what flat sensitivity across Δ ∈ {0,1,2,3,4,6,10} implies. RA's diagnostic insight is more sophisticated.

**Added to my cross-examination:** If BIC prefers staircase regardless of Δ, the classification may be driven by model complexity differences (2-parameter staircase vs. 3-parameter sigmoid) rather than genuine likelihood differences. This requires a negative control (shuffled labels) to distinguish real signal from penalty-driven artifact.

---

### O2: Theorem 1 conclusion vs. per-problem routing — theoretical gap
**Domain Expert ML** W10 identified: "Theorem 1 proves that under log-concave F_τ, the population elbow t* = mode(f_τ) is determined by the population distribution, not individual problems. But the paper's core applied contribution is per-problem adaptive routing via STAIR. If the elbow is purely a population property, per-problem routing has no theoretical basis from Theorem 1 alone."

**Why I missed this:** I focused on log-concavity assumption (W6) but did not examine whether the Theorem's conclusion actually supports the applied framework.

**Added to my cross-examination:** The paper needs to clarify whether it assumes (a) individual problems have different critical depths (consistent with Theorem's framework) or (b) the elbow is purely a population property (which would make per-problem routing unjustified). This is a genuine theoretical gap that needs resolution before the paper's applied claims are credible.

---

### O3: N_PROBLEMS=40 vs 100 code-data mismatch
**Reproducibility Archeologist** W1 identified: real_experiment.py hardcodes N_PROBLEMS=40 and SAMPLES_PER_CELL=4, but the paper abstract and reanalysis_stratified.json report 100 problems with 8 samples/cell.

**Why I missed this:** I did not have access to the code. RA's code inspection identified a reproducibility violation invisible from the paper text alone.

**Added to my cross-examination:** The exact inference script for the 100-problem, S=8 experiments is not released. The published code uses different constants. This undermines verification of the core empirical results.

---

### O4: Token savings claim lacks per-problem characterization
**My original position (W7):** Token savings claim (75%) lacks statistical test — only single paired comparison on 100 problems.

**Cross-review finding:** No other reviewer explicitly calls for per-problem token usage statistics. AP asks about failure logs but not token distribution. BPE asks about wall-clock time including gzip overhead but not token variability.

**Why this matters:** STAIR allocator is deterministic given the gzip proxy. The 75% is a population average. If token savings are concentrated (20% of problems save 90%, 80% save 0%), the practical deployment story differs from a uniform 75% reduction. This needs distributional reporting (mean, SD, median, IQR across problems).

---

## 3. My Own Positions Updated After Seeing Others

### P1: Multiple-testing correction is the MOST critical issue (upgraded)
**My original:** W4 at 5/5 severity — no BH correction across 300 cells.

**Updated:** RA's W5 (flat BIC threshold sensitivity) adds urgency. Combined with no BH correction, the 97.7-99.3% headline could be inflated by both multiple-testing structure AND penalty-dominance artifact. The path from Borderline to Accept now runs through multiple-testing correction as the single most important fix.

**Revised concern:** The combination of (a) no multiple-testing correction, (b) flat threshold sensitivity, and (c) near-random accuracy with S=8 means the high staircase rates may be entirely artifacts. A shuffled-label negative control is mandatory.

---

### P2: Token savings (75%) should be foregrounded; accuracy equivalence demoted
**My original:** W7 at 4/5 — token savings lacks statistical test, but the claim is interesting.

**Updated after BPE W2:** "p > 0.05" is not evidence of equivalence. The paper should demote the accuracy claim ("matches accuracy") and promote token savings. STAIR saves compute with no detected accuracy cost — this is a meaningful practical result when correctly stated.

**Revised position:** Report as "no significant accuracy difference detected (p=0.23)" with explicit CI. The token savings is the finding.

---

### P3: Theorem 1 is the paper's primary contribution (aligned with BPE W10)
**My original:** Acknowledged Theorem as genuine contribution but did not comment on paper structure.

**Updated after BPE W10:** "The Theorem is the paper's most lasting contribution but is underemphasized... if I had to summarize this paper in one sentence at a department lunch, the Theorem is the sentence."

**Revised position:** I agree with BPE. The paper structure (foregrounding empirical BIC results, burying the Theorem) is suboptimal. The Theorem is the irreducible insight; the empirical results are pilot-grade evidence. The paper should be reframed around Theorem 1, with empirical results as illustrative supporting evidence.

---

### P4: GSM8K n=100 generalization scope — was too lenient
**My original:** W8 at 3/5 severity.

**Updated after BPE W3 and others:** Paper title and abstract make broad claims about LLM reasoning in general. Experiments are on 100 GSM8K problems with two small Qwen models. This requires explicit scope qualification (4/5 severity).

**Revised position:** Title/abstract should say "On GSM8K (n=100, Qwen-0.5B/1.5B), we observe..." not broad "per-problem discrete structure in test-time compute scaling."

---

## 4. Consensus Signal: Claim/Weakness with Most Reviewer Agreement

### Strongest consensus (5/6 reviewers): S=8 sample size insufficient for binomial-likelihood BIC

| Reviewer | Position | Severity |
|---|---|---|
| Statistical Rigorist (me) | S=8 underpowered for binomial BIC | 5/5 |
| Big-Picture Editor | S=8 makes binomial BIC unreliable | 4/5 |
| Adversarial Practitioner | Sample size insufficient (S=8, n=100) | 4/5 |
| Domain Expert ML | S=8 likely underpowered | 3/5 |
| Naive Reader | S=8 may be insufficient | 4/5 |
| Reproducibility Archeologist | [Via W3: near-random accuracy compounds the problem] | 5/5 |

**Consensus score: 5/6 reviewers flagging this issue; average severity ≈ 4.2/5**

**Why this is the consensus signal:** This is not a niche statistical concern — it is the foundational reliability issue for the main empirical claim. At S=8 with 2-6% accuracy, cells have expected 0-2 successes. The binomial likelihood is degenerate and BIC comparison cannot be trusted.

**Secondary consensus (4/6):** p=0.23 misused as equivalence claim (Statistical Rigorist, Big-Picture Editor, Adversarial Practitioner, Domain Expert ML)

**Secondary consensus (4/6):** Log-concavity assumption unvalidated (Statistical Rigorist, Big-Picture Editor, Adversarial Practitioner, Naive Reader)

---

## Priority Path to Accept

**CRITICAL (mandatory or paper collapses):**
1. Shuffled-label negative control: if staircase still wins >60% on shuffled data, the 97-99% rates are artifacts
2. Benjamini-Hochberg correction across 300 BIC decisions: if corrected rate drops below 60%, empirical claim fails
3. Test on larger model (>7B) with >30% accuracy: establish phenomenon is not artifact of near-random binary outcomes

**MAJOR (significant improvement):**
4. S={16, 32, 64} sensitivity analysis
5. Validate log-concavity empirically (Baringhaus-Henze test)
6. Clarify theoretical bridge between Theorem 1 and per-problem STAIR routing (DE W10)
7. Correct code-data mismatch (N_PROBLEMS=40 vs 100)

**MODERATE (meaningful improvement):**
8. Rephrase accuracy equivalence claim
9. Report per-problem token statistics
10. Reframe paper around Theorem 1 as primary contribution

---

*Cross-examination completed by The Statistical Rigorist*
