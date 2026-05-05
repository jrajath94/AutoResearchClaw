# Naive Reader Review: SemCP v2
**Persona:** 09_naive_reader (Clarity, Exposition, Implicit Assumptions, Jargon, Readability)  
**Date:** 2026-05-05  
**Bundle:** SemCP v2 Coverage Guarantees Over Meanings, Not Strings

---

## EXECUTIVE SUMMARY

The paper tackles a real problem (semantic equivalence in conformal prediction) and now includes real experiments on three datasets (TriviaQA, SQuAD, NQ-open). The results are credible: SemCP achieves tighter conditional coverage than baselines while maintaining reasonable set sizes. However, critical clarity gaps prevent a naive reader—someone without conformal prediction expertise—from understanding what the method is, why it works, or whether the assumptions are realistic. This is an expert-oriented paper that could become accessible with modest exposition work.

---

## STRENGTHS (Clarity & Communication)

1. **Clear problem statement with strong intuition:** The opening immediately identifies the semantic equivalence problem ("treating semantically identical outputs as distinct inflates set sizes"). A reader unfamiliar with conformal prediction can still grasp why this matters: "Paris" vs. "The capital of France is Paris" should be treated as the same answer, not two different ones.

2. **Concrete methods summary at scannable level:** Algorithm 1 structure (HAC partition → contrastive score → threshold → predict) is follow-able. The three-step flow is easy to scan, and pseudo-code is appropriately detailed without overwhelming notation.

3. **Strong empirical results presentation:** Table 1 is clean and comparison-friendly (SemCP vs. ConU vs. SAFER). Reporting ±stddev and explicit validity gaps (e.g., "−0.007 to +0.021 vs bound") is transparent and quantitative. This builds reader confidence in results.

4. **Honest treatment of failure modes:** Discussion of when SemCP breaks down (p_A < 1−α) and explicit limitations (embedding dependency, K≤10 budget) shows sophistication. The paper doesn't oversell findings.

5. **v1→v2 improvements table is confidence-building:** Directly addressing previous feedback (GPT-2→Qwen, real data, O(K log K) algorithm) with a visible change log is excellent practice. Readers can see the paper improved materially.

---

## WEAKNESSES (Clarity & Exposition Gaps)

1. **Theorem 1 notation undefined (critical accessibility blocker):**
   The paper states "1-α-1/(|I|+1)" as the coverage bound without ever defining:
   - What is α? (Presumably miscoverage level, e.g., 0.05, but never stated)
   - What is |I|? (Presumably calibration set size, but never defined)
   - Why this specific functional form? (Appears arbitrary; no intuition provided)
   
   A naive reader cannot assess the coverage guarantee without these definitions. This alone breaks the paper's accessibility to ~50% of target audience.

2. **Conformal prediction background entirely assumed:**
   The paper launches into "conformal prediction," "split-conformal," "admissibility," "exchangeability" without explaining what problem CP solves or why these concepts matter. A reader unfamiliar with Barber et al. (2019) or Vovk's framework will miss core intuition. A 2-3 sentence plain-English definition ("CP is a framework for generating prediction sets with coverage guarantees; it works by...") before Algorithm 1 would unlock the paper for 60% more readers.

3. **HAC-NLI clustering severely underspecified:**
   "3-stage clustering with embedding prefilter + purity check" is vague. Naive reader questions:
   - What distance metric drives agglomeration?
   - What explicitly are the three stages? (The bundle says "preprocessing, clustering, filtering" but doesn't define each)
   - What is "purity check" exactly? (Transitivity correction, but never unpacked)
   - What are the key hyperparameters and how sensitive is partitioning to them?
   
   The bundle references "Appendix D: sensitivity checked" but provides zero preview of findings in main text.

4. **Contrastive RBF score motivation missing:**
   The score s̃(X,C,S,σ) = 1 − max_c′ κσ(φ̄c, φ̄c′) is presented without explanation of *why* this captures "semantic distinctness." Naive reader asks:
   - Why is max RBF to nearest cluster the right penalty?
   - What does "contrastive" mean here? (Typically implies positive/negative pairs; none are defined)
   - How does RBF bandwidth σ relate to semantic similarity? (Narrower σ = stricter matching, but never explained)
   - Why not other scoring schemes (average RBF, margin-based, etc.)?
   
   The paper claims this "captures semantic distinctness vs ConU sample-count approach" but provides zero intuition.

5. **M-SemCP unification unvalidated:**
   The paper claims "recovers ConU, LofreeCP, TECP as special cases" via convex combinations of τ∈{0.7, 0.5, 0.3}. But:
   - No formula shown for the convex combination.
   - Which τ maps to which baseline?
   - Are the three τ values fixed, data-driven, or tuned?
   - Why exactly three? (Appears ad hoc)
   
   This is interesting but completely scaffolding-free.

6. **"True meaning is sampled" assumption is load-bearing but unquantified:**
   Theorem 1's coverage guarantee assumes "true meaning is sampled" (among the K=10 LLM outputs). Naive reader questions:
   - What if the oracle answer is a paraphrase that HAC misses?
   - How robust is coverage if NLI model (DeBERTa) errs?
   - What is the realistic probability this holds on TriviaQA/SQuAD/NQ-open?
   
   This is a critical assumption that directly impacts whether the coverage guarantee applies in practice, yet failure risk is not quantified.

7. **Admissibility-selection conditioning never explained:**
   Theorem 1 proof references "exchangeability under admissibility-selection conditioning" (Appendix B). Main text never explains:
   - What is admissibility exactly?
   - Why condition on it?
   - How does this differ from standard CP conditioning?
   
   A reader cannot evaluate whether this is a straightforward application of existing theory or a novel contribution.

8. **Theorem 2 bandwidth derivation undermotivated:**
   The closed-form σ* = √((μ̄μ−μ̄W)/(2log(1/(1−α)))) appears without:
   - Definitions: What are μ̄μ and μ̄W? (Within/between-cluster variance, but never stated)
   - Intuition: Why does variance minimization lead to valid bandwidth? (Tighter threshold → smaller sets, but why valid?)
   - Validity of assumptions: Sub-Gaussian for RBF outputs ∈ [0,1]? (RBF has exponential tails, not Gaussian)
   
   The empirical result "matches grid-search within 5%" is reassuring but doesn't validate the theory.

9. **Experimental setup choices unjustified:**
   - Why 50/50 calibration/test? (Standard, but not justified)
   - Why seed 42 with 3 seeds total? (Low for high-variance QA; confidence intervals missing)
   - Why K=10? (Mentioned as "open-ended QA budget" but no preview of K∈{3,5,7,10} ablation from Appendix E)
   - Why temperature=1.0? (Maximal randomness; trade-offs vs. lower temps not discussed)

10. **Implicit comparison assumptions not addressed:**
    Paper compares to ConU, SAFER, LofreeCP, TECP but never discusses:
    - Are these the only semantic-aware CP variants? Or most relevant?
    - Were baselines tuned equally? (Bundle says "all tuned same split" but doesn't show tuning sensitivity)
    - Why no comparison to e.g., simple majority voting over sampled outputs?

---

## SCORES (1-10 scale)

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Originality (Orig)** | 8 | Novel mapping to semantic space via HAC-NLI + Theorem 2 closed-form bandwidth are non-trivial. Limits: M-SemCP unification feels incremental; theoretical novelty is moderate (applies existing CP machinery to new domain). |
| **Quality (Qual)** | 7 | Real experiments on 3 credible datasets (TriviaQA, SQuAD, NQ-open) with proper baseline tuning. Limitations: small dataset sizes (300 ex each), only 3 random seeds (low for high-variance QA), no downstream task evaluation. No reproducibility blockers (code promised). |
| **Clarity (Clar)** | 5 | **Major accessibility failure.** Strengths: empirical results clearly presented (Table 1), strong problem motivation. Weaknesses: conformal prediction not explained, Theorem 1 notation undefined, contrastive score motivation missing, admissibility-selection conditioning unexplained, HAC-NLI underspecified, M-SemCP framework unvalidated. Paper is written for experts, not accessible to domain outsiders. |
| **Significance (Sig)** | 6 | Solves real problem (set size inflation from semantic equivalence). Impact contingent on: (a) how often semantic equivalence matters in practice vs. sampling variance, (b) adoption of NLI-based partitioning (embedding dependency is a barrier), (c) generalization beyond QA. Scope is currently narrow (QA only, K≤10). |

---

## CRITICAL QUESTIONS FOR AUTHORS

### Q1: Define α and |I| in Theorem 1 explicitly.
**Why this matters:** A naive reader cannot assess the coverage guarantee without definitions. Is α the miscoverage level (e.g., 0.05)? Is |I| the calibration set size? Why this functional form?

### Q2: What does "true meaning is sampled" mean precisely?
**Why this matters:** This assumption gates the coverage guarantee. Does it mean the oracle is in the K=10 samples, or in the same NLI equivalence class? What if the oracle is a novel paraphrase? What is the realistic probability this holds on TriviaQA/SQuAD/NQ-open?

### Q3: Why does max RBF to nearest cluster capture "semantic distinctness"?
**Why this matters:** The contrastive score motivation is missing. Why is this form better than alternatives (e.g., average RBF, margin-based)? How does RBF bandwidth σ relate to semantic similarity?

### Q4: How are the three HAC stages defined, and how sensitive is the final partition to choices?
**Why this matters:** "3-stage clustering with prefilter + purity check" is too vague. What distance metrics? What thresholds? What does Appendix D sensitivity show?

### Q5: Why do τ∈{0.7, 0.5, 0.3} recover ConU, LofreeCP, TECP exactly?
**Why this matters:** M-SemCP framework is interesting but unvalidated. Show the convex combination formula. Are τ values fixed or data-driven?

### Q6: Is the sub-Gaussian assumption reasonable for bounded RBF outputs [0,1]?
**Why this matters:** Theorem 2 uses sub-Gaussian concentration, but RBF has exponential tails, not Gaussian. Does the proof still hold? What is the practical impact?

### Q7: How sensitive is coverage to NLI model errors?
**Why this matters:** DeBERTa partitions semantic space but has errors. If it mislabels contradictions, does coverage still hold? What is the degradation curve as NLI accuracy decreases?

### Q8: Why is K=10 sufficient, and what does the K∈{3,5,7,10} ablation show?
**Why this matters:** K=10 is stated as "open-ended QA budget" but not validated. Does Appendix E show why 10 is optimal?

---

## FALSIFIABILITY TEST

**Main Claim:** "SemCP attains conditional coverage 1-α-1/(|I|+1) over meaning classes given true meaning is sampled."

**Falsification approach:**
1. Construct test set where true meanings are deliberately *not* in K=10 samples (e.g., novel paraphrases not covered by generator).
2. Measure empirical coverage: does it drop below predicted bound?
3. If yes, the assumption "true meaning is sampled" is violated in practice.

**Current status:** Not falsified, but untested. The three datasets (TriviaQA, SQuAD, NQ-open) are closed-answer QA where responses are relatively fixed. More adversarial/open-ended domains would reveal limits.

**Suggested experiment:** Create synthetic dataset with intentionally paraphrased oracle answers + K=10 samples that *miss* the oracle paraphrase. Report coverage degradation.

---

## CONFIDENCE IN ASSESSMENT

**Confidence: 3/5**

**Why low?**
- Review is constrained to the **paper_bundle.md** summary, not the full paper or appendices.
- Key proofs (Appendix B, C) and sensitivity analyses (Appendix D, E) are referenced but not read.
- Jargon like "admissibility," "transitivity-corrected clustering," "between-cluster RBF" are opaque from summary alone.

**Why not lower?**
- Empirical results and clarity gaps are visible in the bundle.
- Structure and claimed contributions are clear enough to identify weaknesses objectively.

**Recommendation:** This assessment should be read alongside the full paper and appendices to resolve ambiguities.

---

## DECISION & RECOMMENDATION

### Summary
The paper tackles a real problem (semantic equivalence in conformal prediction) with novel theory (Theorem 2 closed-form bandwidth) and practical framework (M-SemCP). Empirical results are now credible: SemCP achieves tighter conditional coverage than baselines while maintaining reasonable set sizes on three real datasets.

**However, critical clarity gaps prevent a naive reader from understanding:**
- What conformal prediction is (assumed knowledge)
- How Theorem 1's coverage bound is defined (notation never explained)
- Why the contrastive RBF score works (intuition missing)
- Whether key assumptions are realistic ("true meaning is sampled" not quantified)

### Recommendation: **CONDITIONAL ACCEPT** with mandatory exposition revisions

**Pre-publication fixes (priority order):**
1. Add 3-sentence plain-English explanation of conformal prediction before Algorithm 1.
2. Define α, |I| in Theorem 1 explicitly (state before theorem, not after).
3. Explain contrastive RBF score intuition: why max-RBF-to-nearest-cluster captures semantic distinctness (Section 4.2).
4. Add brief preview of Appendix D findings (HAC sensitivity) in main text.
5. Show M-SemCP convex combination formula and τ→baseline mappings (Section 4).
6. Quantify failure risk: how often does oracle paraphrase miss K=10 samples? (Expected Table or brief analysis).

**Why conditional accept, not reject?**
- Empirical contribution is genuine and problem is well-motivated.
- Fixes are additive (explanations, definitions), not destructive (removals/reworking).
- Theory appears sound based on visible results; clarity is the bottleneck.
- v1→v2 progress shows authors are responsive to feedback.

**Why not accept as-is?**
- Reader unfamiliar with CP cannot reproduce or assess main claims.
- Load-bearing assumptions ("true meaning is sampled") not quantified.
- Paper prioritizes results over intuition, reducing accessibility below venue standard.

### Confidence in recommendation: **4/5**
- High confidence in clarity gaps (objective, visible in bundle).
- Moderate confidence in technical soundness (appendices not read; proofs assumed correct).
- Strong confidence in empirical contribution (Table 1 is clear).

---

## FINAL ASSESSMENT

| Dimension | Rating | Comment |
|-----------|--------|---------|
| **Would naive reader understand problem?** | 80% | Clear motivation (semantic equivalence), but CP background assumed. |
| **Would naive reader understand solution?** | 40% | Algorithm 1 is scannable; theoretical justification is opaque. |
| **Would naive reader trust results?** | 75% | Empirical results well-presented; assumptions not quantified. |
| **Would naive reader recommend acceptance?** | 60% | Interesting work; clarity revisions required before publication. |

**Key takeaway:** The paper is currently written for experts (familiar with CP, NLI, QA). A 10% effort in exposition (definitions, intuitions, assumption quantification) would make it accessible to 90% of readers. This investment is worthwhile for a top-tier venue.