# Cross-Examination: Big-Picture Editor

**Paper:** STAIR: Per-Problem Discrete Structure in Test-Time Compute Scaling for LLM Reasoning
**Date:** 2026-05-01
**Reviewer:** The Big-Picture Editor
**Cross-examining:** All 5 other reviewers (04_statistical_rigorist, 05_adversarial_practitioner, 06_domain_expert_ml, 07_reproducibility_archeologist, 09_naive_reader)

---

## 1. Disagreements with At Least 2 Other Reviewers

### D1: My W1 (zero-variation cells inflating headline number) — Only I raised this explicitly as a 5/5 severity issue
The Statistical Rigorist (W3) mentions wide bootstrap CIs on the variation subset but does not explicitly call out the zero-variation cell inflation mechanism. The Adversarial Practitioner (W7) mentions selection bias in the variation subset but frames it as a post-hoc selection issue rather than the specific zero-variation structure I identified.

**My position:** The mechanism is: 72% of cells have zero accuracy variation → both staircase and sigmoid reduce to a flat line → BIC prefers the 2-parameter staircase → the 99.3% headline is artificially inflated. This is a structural confound, not just "wide CIs" or "post-hoc selection."

**After cross-exam:** I maintain this as my most important empirical criticism. The Naive Reader and Reproducibility Archeologist both flag selection bias in the variation subset, which partially overlaps. But neither frames it precisely as zero-variation-cells-as-trivial-staircase. I hold my position.

### D2: The Theorem is the paper's most lasting contribution — I may be alone in this prioritization
I assigned W10 (Theorem underemphasized) at severity 2/5 and explicitly said "the Theorem is the sentence" in my pointed questions. The Domain Expert ML gives the Theorem a 6/10 on Originality but does not emphasize it as the primary contribution. The Reproducibility Archeologist calls it "the paper's most novel theoretical result" but does not say it should be the framing anchor.

**After cross-exam:** I see the Theorem as a 5-year insight and the empirical results as fragile pilot data. The other reviewers treat the Theorem as one strength among several. This is a genuine framing disagreement: should this be a theoretical paper with empirical illustrations, or an empirical paper with a theoretical ornament? I lean toward the former; the field will likely treat it as the latter unless the authors reframe.

### D3: Qwen-only experiments are a moderate concern, not fatal
I rated W9 (Qwen-only) at 3/5 severity. The Domain Expert ML (W4) also rates this 3/5. The Adversarial Practitioner (W10) rates it 4/5. The Reproducibility Archeologist flags it at 4/5 in their Falsifiability section.

**After cross-exam:** I may be underweighting this. The fact that ALL real experiments use small Qwen models (0.5B and 1.5B) while the field has moved to 7B+ for meaningful scaling law studies is a real limitation. I update my severity to 4/5.

---

## 2. Issues Others Missed That I Now Want to Add

### O1: Synthetic-vs-real divergence as a theoretical grounding problem (NEW)
**Not raised by any other reviewer.** The paper's most interesting empirical claim (circuit depth predicts elbows at ρ=0.96 on synthetic data) does NOT replicate on real GSM8K data (ρ=0.147, CI includes zero). If gzip does not predict real scaling elbows, the STAIR allocator's gzip proxy has no theoretical grounding for real deployments. The Domain Expert ML (W5) mentions "gzip as Kolmogorov proxy is not validated" but frames it as a measurement validity concern, not as a complete disconnect between the synthetic result and the real-world deployment. The Adversarial Practitioner (W4) asks about the failure log but not about this fundamental disconnect.

**Significance:** This is the gap between the paper's most compelling empirical contribution and its primary applied claim. Without replication, the STAIR allocator's theoretical basis on real tasks is asserted, not demonstrated.

### O2: The Theorem's implication for per-problem routing is not explained (NEW)
**Not raised by any other reviewer at sufficient depth.** Theorem 1 proves that under log-concave critical-depth distributions, the population elbow t* = mode(f_τ) is a population-level property. But the paper's core applied contribution is per-problem adaptive routing via STAIR. The Domain Expert ML (W10) catches this as a contradiction but frames it as "does the paper's main applied claim contradict the theorem?" The correct framing is: if the elbow is purely a population property, per-problem routing has no theoretical basis from Theorem 1 alone. The authors need to explicitly bridge Theorem 1 (population property) to per-problem routing (individual property). This is not a contradiction but a gap the paper fails to address.

**Significance:** The paper presents Theorem 1 as theoretical grounding for the STAIR framework, but Theorem 1 actually constrains when population curves are smooth — it does not justify per-problem discrete structure or the STAIR allocator. The theoretical bridge is missing.

---

## 3. My Positions Updated After Seeing Others

### U1: The Reproducibility Archeologist's W3 (gross accuracy levels) is the most devastating critique — I was wrong not to raise it
The Reproducibility Archeologist correctly identifies that Qwen-0.5B achieves 2-3% accuracy on GSM8K across all budgets. With S=8 samples, most cells have 0-2 successes. The BIC comparison on near-random binary outcomes is fitting noise. This is SEVERITY 5/5 and I completely missed it. I update my assessment: the empirical BIC results on real LLMs are potentially meaningless, not just unreliable.

**The critical test the Reproducibility Archeologist demands (and I now endorse):** Run BIC on shuffled labels. If staircase still wins >60% on random noise, the 97-99% rate is a artifact of the low-accuracy binary regime, not evidence of genuine discrete structure.

### U2: The code-paper discrepancy (N_PROBLEMS=40 vs 100) is a reproducibility red flag
The Reproducibility Archeologist (W1) found that real_experiment.py hardcodes N_PROBLEMS=40 and SAMPLES_PER_CELL=4, but the paper claims 100 problems with S=8. The 100-problem results exist only as stored .npy and JSON files with no reproducible script. This is not just a minor discrepancy — it calls into question whether the paper's headline numbers were generated by the code that was released. I update my Reproducibility score down from 5 to 3.

### U3: The variation-subset restriction is circular selection bias, not just "selection bias"
I framed W1 as "zero-variation cells inflating headline numbers." The Reproducibility Archeologist and the Adversarial Practitioner both frame it as "post-hoc selection bias." The more precise framing is: restricting to cells with variation is circular because those are exactly the cells where both models can potentially be distinguished, and at 2-3% accuracy with S=8, the cells with "variation" are cells where 1 out of 8 samples went a different direction — i.e., noise. The BIC then prefers staircase (simpler) on noise. I update my W1 to include this mechanism explicitly.

### U4: Missing Snell 2024 comparison is a more serious contextualization failure than I rated
I gave the contextualization a 7/10 and mentioned Snell 2024 was "correctly positioned." The Domain Expert ML (W3) gives it 4/5 severity and correctly notes that Snell's population-level power law is the most directly relevant prior work — and the paper does not compare STAIR's BIC decomposition against Snell's framework. If Snell's power-law model fits the aggregated data equally well, the per-problem staircase decomposition could be a statistical artifact. I update W3 (from my review) to 4/5 severity.

### U5: p=0.23 as equivalence is a specific named statistical error
I said "this is a statistical error with a name (TOST)" but did not pursue the full implications. The Statistical Rigorist and Adversarial Practitioner both flag this. After seeing both, I recognize the specific error: using p≥0.05 as evidence of equivalence is the "absence of evidence = evidence of absence" fallacy. The paper needs a TOST (two-one-sided t-tests) procedure with a pre-specified equivalence margin, not a Wilcoxon test. I maintain my W2 at 5/5 severity.

---

## 4. Consensus Signal — Claim/Weakness with Most Reviewer Agreement

### Consensus Finding 1 (5 of 6 reviewers): S=8 samples per cell is underpowered for binomial-likelihood BIC
- Statistical Rigorist: W2 (5/5) — "enormous variance," needs sensitivity analysis
- Naive Reader: W3 (4/5) — "degenerate log-likelihoods" when k=0 or k=8
- Domain Expert ML: W2 (3/5) — power analysis needed
- Adversarial Practitioner: W1 (4/5) — "insufficient for generalization claims"
- Reproducibility Archeologist: W3 (5/5) — 2-3% accuracy makes this worse
- Big-Picture Editor (me): W4 (4/5)

**Agreement level:** UNANIMOUS across all 6 reviewers. The Reproducibility Archeologist's framing is the most damning: at 2-3% accuracy with S=8, the binomial likelihood is essentially a Bernoulli trial with most cells having 0 or 1 success. The BIC comparison is not informative.

### Consensus Finding 2 (5 of 6 reviewers): p=0.23 misrepresented as equivalence
- Statistical Rigorist: W1 (4/5) — "dressed as a win"
- Naive Reader: (did not explicitly flag but asked about it in pointed questions Q2)
- Domain Expert ML: (mentioned in passing)
- Adversarial Practitioner: W3 (4/5) — "p > 0.05 is not evidence of equivalence"
- Reproducibility Archeologist: (mentioned but not as a primary weakness)
- Big-Picture Editor (me): W2 (5/5)

**Agreement level:** 5 of 6 explicitly flag this. The Naive Reader and Reproducibility Archeologist mention it less directly. This is a clear consensus: the paper uses a non-significant p-value as evidence of equivalence, which is a named statistical error (TOST is the correct approach).

### Consensus Finding 3 (4 of 6 reviewers): No multiple-testing correction
- Statistical Rigorist: W4 (5/5) — "Garden of Forking Paths"
- Adversarial Practitioner: W6 (3/5) — BIC threshold sensitivity not controlled
- Reproducibility Archeologist: W8 (2/5) — 9 hypothesis checks without correction
- Big-Picture Editor (me): W5 (4/5)

**Agreement level:** 4 of 6. The Domain Expert ML does not explicitly flag this; the Naive Reader mentions threshold sensitivity but not multiple-testing per se.

### Consensus Finding 4 (4 of 6 reviewers): Log-concavity assumption empirically unjustified
- Statistical Rigorist: W6 (3/5)
- Naive Reader: W1 (3/5)
- Domain Expert ML: W1 (4/5)
- Adversarial Practitioner: W2 (3/5)
- Big-Picture Editor (me): W7 (3/5)

**Agreement level:** 5 of 6 reviewers flag this, with the Reproducibility Archeologist mentioning it in passing. The Domain Expert ML gives it the highest severity (4/5). This is a genuine consensus that the Theorem's sufficient condition is unverified on real data.

### Consensus Finding 5 (4 of 6 reviewers): Zero-variation cells / variation-subset selection bias inflating headline numbers
- Adversarial Practitioner: W7 (4/5) — "post-hoc selection inflates staircase preference"
- Reproducibility Archeologist: W2 (3/5) — "circular selection bias"
- Big-Picture Editor (me): W1 (5/5) — "72% of cells trivially staircase because nothing changes"
- Domain Expert ML: W8 (3/5) — "bootstrap CI methodology unclear for variation subset"

**Agreement level:** 4 of 6 explicitly flag the variation-subset restriction as problematic. The Statistical Rigorist mentions wide CIs on the variation subset but not the zero-variation inflation mechanism.

### NOT consensus (divergent views):
- **Gzip proxy latency**: Adversarial Practitioner (W5, 2/5) and Reproducibility Archeologist (W7, 2/5) flag it. I rated it 3/5. Others mention it in passing. Low consensus.
- **Failure mode analysis for STAIR allocator**: Only Adversarial Practitioner (W4, 5/5) treats this as critical. Others do not mention it. Not consensus.
- **p99 latency reporting**: Only Adversarial Practitioner (W8, 5/5) treats this as critical. Others do not mention it. Not consensus.

---

## Summary of Updated Positions

| Issue | My Original View | Updated View After Cross-Exam |
|-------|-----------------|-------------------------------|
| S=8 underpowered | Serious (4/5) | Most critical empirical flaw; unanimous 5/6 reviewers agree |
| p=0.23 as equivalence | Statistical error (5/5) | Maintain; named error (TOST); 5/6 reviewers agree |
| Zero-variation inflation | Novel framing (5/5) | Maintain; add Reproducibility Archeologist's circular selection bias framing |
| Log-concavity | Unmotivated (3/5) | Upgrade to 4/5; 5/6 reviewers flag it |
| Qwen-only experiments | Moderate (3/5) | Upgrade to 4/5; single model family limits all real-LLM claims |
| Low accuracy regime (2-3%) | Not raised | ADD with 5/5 severity — Reproducibility Archeologist's insight is devastating |
| Code-paper discrepancy | Not raised | ADD with 4/5 severity — N_PROBLEMS=40 vs 100 undermines reproducibility |
| Snell 2024 comparison | Not flagged as key gap | Add at 4/5; most directly relevant prior work not compared |
| Synthetic-to-real disconnect | Not raised | ADD at 4/5; ρ=0.96 on synthetic does not replicate at ρ=0.147 on real |
| Theorem-per-problem routing gap | Not raised | ADD at 4/5; Theorem 1 shows population property, not individual |
| Theorem as primary contribution | Maintain framing (2/5 but structural) | Maintain; still the right 5-year insight |

---

## Bottom Line

**The most critical consensus:** S=8 + 2-3% accuracy + 100 problems = the empirical BIC results are uninterpretable without a negative control. The paper cannot be accepted without showing that shuffling labels does NOT produce 97-99% staircase preference.

**The most underappreciated issue:** The synthetic-vs-real divergence (ρ=0.96 vs ρ=0.147). This is the gap between the paper's most compelling empirical finding and its primary applied claim (the STAIR allocator on real tasks).

**The consensus framing for revision:** All 6 reviewers are in Borderline territory (5.5-6.5 range). The path to Accept is clear and unanimous across all reviewers: (1) sensitivity analysis at S={16, 32}, (2) negative control with shuffled labels, (3) BH-corrected BIC rates, (4) log-concavity test, (5) one larger model replication. The paper has a genuine theoretical contribution (Theorem 1) that deserves publication — but the empirical evidence for the applied claims does not currently support acceptance.

---

*Cross-exam completed. Saved to 02_cross_exam/08_big_picture_editor.md*