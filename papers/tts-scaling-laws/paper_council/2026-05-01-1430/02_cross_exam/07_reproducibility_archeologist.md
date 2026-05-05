# Cross-Examination Report — Reproducibility Archeologist

**Paper:** STAIR: Per-Problem Discrete Structure in Test-Time Compute Scaling for LLM Reasoning
**Cross-Exam Reviewer:** The Reproducibility Archeologist
**Date:** 2026-05-01
**Output path:** /Users/rj/research-claw/papers/tts-scaling-laws/paper_council/2026-05-01-1430/02_cross_exam/07_reproducibility_archeologist.md

---

## 1. Disagreements with 2+ Other Reviewers

### D1: My W3 (near-random accuracy) is the most serious issue — others rated it too low

**My position (Severity 5/5):** Qwen-0.5B achieves 2-3% accuracy on GSM8K, Qwen-1.5B achieves 1.9-6.5%. With S=8 samples, most cells have 0-2 correct out of 8. BIC model comparison on near-random binary outcomes is fitting noise, not signal. The 97-99% staircase rates may be entirely artifacts of low-accuracy regimes.

**Reviewers who partially agree:**
- **Big-Picture Editor** (W1): Flagged "72% of cells have ZERO accuracy variation" and "bootstrap CI is [0.615, 1.000] — uninterpretable" — but framed it as classification setup artifact, not as near-random accuracy undermining the entire analysis.
- **Domain Expert ML** (W8): Mentioned "near-random accuracy" as selection bias concern but not as a fundamental validity issue.
- **Adversarial Practitioner** (W1): Flagged wide bootstrap CI but not the near-random accuracy as the core problem.

**Disagreement:** The Big-Picture Editor, Domain Expert ML, and Adversarial Practitioner all rate this as 3-4/5 severity. I maintain it is 5/5 because the BIC comparison on near-random outcomes is not just "noisy" — it is potentially meaningless. A shuffled-label negative control would be expected to show staircase "winning" at similar rates when fitting noise with a simpler model.

**Why others missed this:** They focused on the statistical fixes (S=8 sensitivity, BH correction) without asking whether the dependent variable (accuracy at 2-6%) has sufficient signal to support any curve-fitting at all.

---

### D2: I flagged N_PROBLEMS=40 mismatch — nobody else caught this

**My position:** real_experiment.py hardcodes N_PROBLEMS=40 and SAMPLES_PER_CELL=4, but the paper and reanalysis_stratified.json claim 100 problems with S=8. The actual inference script for the 100-problem/S=8 experiments was never released. This is not just a reproducibility gap — it suggests the real experiments went through an unreported pipeline.

**Reviewers who partially agree:**
- **Statistical Rigorist** (W1): Flagged p=0.23 misrepresentation
- **Big-Picture Editor** (W1): Flagged zero-variation cells inflating headline numbers
- **Adversarial Practitioner** (W4): Flagged no failure mode analysis for allocator

**Disagreement:** None of the other reviewers identified the code/paper N_PROBLEMS discrepancy. This is the Reproducibility Archeologist's unique catch. The Statistical Rigorist and Big-Picture Editor flagged the statistical issues around sample size and multiple testing, but the actual code-data mismatch in the repository went unnoticed by others.

---

### D3: BIC threshold sensitivity flatness — I found it others didn't mention

**My position (W5, Severity 2/5):** The real_results_v2/reanalysis_stratified.json shows BIC win rates are essentially flat across Δ ∈ {0, 1, 2, 3, 4, 6, 10} (e.g., Qwen-0.5B: 98.7% at thr=0, 99.7% at thr=10). This flatness suggests the classification is driven by the penalty term (2-parameter vs 3-parameter model) rather than genuine likelihood differences. This is worth noting but others didn't flag it.

**Disagreement:** This observation appears nowhere else in the reviews. The Naive Reader asked about Δ=2 threshold justification, and the Domain Expert ML mentioned BIC threshold justification, but none noticed the JSON contains the sensitivity data that would address this — and that the flatness is actually a concerning signal.

---

## 2. Issues Others Missed That I Now Want to Add

### New Issue A: Negative control absent — the most critical gap

After reading the other reviews, I realize my W3 (near-random accuracy) implies a specific empirical test that none of the other reviewers demanded: **run BIC on shuffled labels**. If you shuffle success/failure labels before curve-fitting, the simpler (2-parameter) staircase model should outperform the 3-parameter sigmoid on noise. If the shuffled case also shows 97%+ staircase preference, the entire empirical claim collapses.

**The other reviewers implied the result might be fragile (S=8, BH correction needed), but none demanded the specific negative control that would definitively distinguish signal from artifact.**

### New Issue B: The variation subset + near-random accuracy combination is doubly circular

**Reviewer consensus:** Multiple reviewers (Big-Picture Editor W1, Adversarial Practitioner W7, my W2) identified that the "variation subset" (28% of cells with any accuracy variation) is post-hoc selection bias.

**What others missed:** When combined with my W3 (near-random accuracy), the circularity is two layers deep:
1. First layer: Select cells with any variation (bias toward simpler models)
2. Second layer: On those selected cells, accuracy is still near-random (2-6%), so the "variation" is itself mostly noise

None of the other reviewers connected these two weaknesses explicitly. The Adversarial Practitioner flagged W7 (selection bias in variation subset) and W1 (sample size), but treated them as separate issues.

### New Issue C: Absolute MAPE values absent — W10 in my original review, not reinforced by others

My W10 (35% MAPE claim without absolute values) was unique to my review. The Big-Picture Editor and others mention the synthetic results and BIC classification rates, but none asked: "What is the absolute MAPE for each baseline?" A 35% relative reduction from MAPE=200% is different from MAPE=20%. **This issue was not reinforced by any other reviewer.**

---

## 3. My Positions Updated After Seeing Others

### Updated Position U1: Severity of S=8 concern — staying at 5/5 but with refinement

**Original:** I gave W3 (near-random accuracy) Severity 5/5, which encompasses S=8 being insufficient.

**After reading others:** The Statistical Rigorist (W2, 5/5), Big-Picture Editor (W4, 4/5), Domain Expert ML (W2, 3/5), Naive Reader (W3, 4/5), and Adversarial Practitioner (W1, 4/5) ALL flagged S=8 as a concern. Four of five other reviewers agree S=8 is problematic. I now believe my 5/5 severity for W3 is correct and well-supported by the full reviewer panel.

**However:** The Big-Picture Editor and Statistical Rigorist frame S=8 as "results might be noisy." I frame it more severely: "near-random accuracy with S=8 makes the analysis equivalent to fitting noise." The other reviewers don't go as far as I do on the negative control demand.

### Updated Position U2: The "no multiple-testing correction" concern is now consensus

**Original:** I gave W8 (multiple comparisons not corrected) Severity 2/5.

**After reading others:** The Statistical Rigorist (W4, 5/5), Big-Picture Editor (W5, 4/5), and Adversarial Practitioner (W6, 3/5) all flagged multiple-testing as a major concern. The consensus is that 300 BIC model selection decisions without correction is a serious gap.

**My update:** I should have rated this higher. The Statistical Rigorist's framing (Garden of Forking Paths) is more precise than my "9 hypothesis checks in evaluation.py" framing. I defer to the Statistical Rigorist on this issue and update my severity estimate to 4/5.

### Updated Position U3: p=0.23 misrepresentation — fully aligned with consensus

**Original:** I did not explicitly flag W1 (p=0.23 misrepresentation) in my review — it was implicitly covered under my W3 (near-random accuracy undermining everything).

**After reading others:** The Statistical Rigorist (W1, 4/5), Big-Picture Editor (W2, 5/5), and Adversarial Practitioner (W3, 4/5) all clearly and correctly identified this as a serious misrepresentation. I now see this should have been an explicit W in my review.

**My update:** Add explicit flagging of this issue. The token savings (75%) is the legitimate claim; the "matches accuracy" framing using p=0.23 is not.

### Updated Position U4: Accept vs Borderline — I am now more uncertain

**Original:** My decision was Borderline (5.5-6.5).

**After reading others:** The Naive Reader said Accept, the Statistical Rigorist said Borderline (reject with resubmit), the Big-Picture Editor said Borderline (reject with resubmit), the Domain Expert ML said Borderline (major revision), and the Adversarial Practitioner said Borderline.

**My update:** The Naive Reader's Accept is puzzling given the same weaknesses I identified. I suspect the Naive Reader may not have fully appreciated the severity of near-random accuracy (2-6%) with S=8 — they rated W3 as 4/5 but still said Accept. I am now more confident that Borderline is the correct call, and I would not move toward Accept without the negative control (shuffled labels) and a larger model (>30% accuracy).

---

## 4. Claim/Weakness with Most Reviewer Agreement (Consensus Signal)

### Consensus Weakness: S=8 samples insufficient for binomial-likelihood BIC

**Agreement level:** 5 out of 6 reviewers flagged this.

| Reviewer | Issue | Severity |
|----------|-------|----------|
| Statistical Rigorist | W2: S=8 underpowered for binomial BIC | 5/5 |
| Big-Picture Editor | W4: S=8 makes BIC unreliable | 4/5 |
| Domain Expert ML | W2: S=8 samples likely underpowered | 3/5 |
| Naive Reader | W3: S=8 may be insufficient for binomial-likelihood BIC | 4/5 |
| Adversarial Practitioner | W1: 8 samples/cell insufficient for generalization | 4/5 |
| Reproducibility Archeologist | W3 (via near-random accuracy): S=8 + 2-6% accuracy = noise fitting | 5/5 |

**The consensus is clear and strong.** S=8 is the most uniformly agreed-upon weakness. The fix (run S={16, 32, 64} sensitivity) is well-understood by all reviewers.

### Second-tier consensus: p=0.23 misrepresentation as equivalence

| Reviewer | Issue | Severity |
|----------|-------|----------|
| Statistical Rigorist | W1: p=0.23 reported as "matches accuracy" | 4/5 |
| Big-Picture Editor | W2: p=0.23 dressed as equivalence is misleading | 5/5 |
| Domain Expert ML | (implied via methodology concerns) | — |
| Adversarial Practitioner | W3: p=0.23 is misrepresented as "matches" | 4/5 |
| Naive Reader | (did not explicitly flag) | — |
| Reproducibility Archeologist | (not explicitly flagged — I now add it) | — |

### Third-tier consensus: Log-concavity assumption empirically unjustified

| Reviewer | Issue | Severity |
|----------|-------|----------|
| Statistical Rigorist | W6: Log-concavity unmotivated | 3/5 |
| Big-Picture Editor | W7: Log-concavity assumption unmotivated empirically | 3/5 |
| Domain Expert ML | W1: Critical-depth log-concavity unjustified | 4/5 |
| Naive Reader | W1: Log-concavity assumption asserted not justified | 3/5 |
| Adversarial Practitioner | W2: Log-concavity never validated | 3/5 |
| Reproducibility Archeologist | (implied in theorem concern) | — |

---

## 5. Summary of Cross-Examination Findings

**Unique contributions from Reproducibility Archeologist:**
1. N_PROBLEMS=40 vs 100 code-data mismatch (W1)
2. Near-random accuracy (2-6%) making BIC analysis equivalent to noise-fitting (W3) — more severe framing than others
3. BIC threshold sensitivity flatness indicating penalty-dominated classification (W5)
4. Absolute MAPE values absent (W10)

**Issues I now want to add after seeing others:**
- Explicit flag of p=0.23 misrepresentation (consensus issue I did not make explicit)
- The "doubly circular" nature of variation-subset selection + near-random accuracy (layered weakness nobody connected)

**Positions I'm updating:**
- Multiple-testing correction severity: 2/5 → 4/5 (consensus with Statistical Rigorist and Big-Picture Editor)
- p=0.23 should be explicit W in my review
- Accept vs Borderline: more confident in Borderline after seeing Naive Reader's lenient Accept

**Consensus signal:** S=8 is the clearest agreement point across reviewers. The fix is straightforward (run sensitivity at higher S) and if the result survives, the paper's empirical contribution becomes credible.

---

*— The Reproducibility Archeologist*
*Cross-Examination complete*
