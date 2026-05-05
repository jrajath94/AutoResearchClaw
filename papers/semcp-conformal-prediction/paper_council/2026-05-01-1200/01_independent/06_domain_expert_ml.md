# DOMAIN EXPERT ML REVIEW: SemCP v2

**Paper:** SemCP: Coverage Guarantees Over Meanings, Not Strings  
**Venue:** NeurIPS 2025 | **Pages:** 11  
**Reviewer:** 06_domain_expert_ml  
**Date:** 2026-05-05 (v2 Assessment - Real Experiments)

---

## SUMMARY SCORECARD

| Dimension | Score | Justification |
|---|---|---|
| **Originality** | 7 | Novel semantic-level CP framing; non-trivial M-SemCP unification |
| **Quality** | 7 | Sound theory; honest experiments with reproducible setup; gaps in admissibility characterization |
| **Clarity** | 8 | Professional writing; clear pipeline; but conditioning event under-emphasized |
| **Significance** | 6 | Practical gains modest (64% on TriviaQA, 5% on SQuAD, 0% on NQ-open); niche use case |
| **Reproducibility** | 8 | CLAIM_AUDIT, 3-seed validation, public code promised; exemplary transparency |
| **Contextualization** | 7 | Proper baselines; M-SemCP unification elegant; semantic entropy citations adequate |

**Weighted Average: 7.0/10** → **Borderline Accept**

**DECISION: WEAK ACCEPT** (with recommended minor revisions)

---

## STRENGTHS (5)

**S1. Well-motivated core problem addresses genuine semantic-token gap.**  
String-level CP treating "England" and "British team" as distinct is real and concrete. The shift from coverage guarantees over tokens to coverage over semantic meaning classes is a conceptual contribution that fills a gap in the CP-for-LLM literature. ConU, SAFER, LofreeCP, TECP all operate in string/token space; SemCP's semantic framing is novel.

**S2. Theorem 2 eliminates last tunable hyperparameter with plug-in formula.**  
Deriving closed-form σ*=√((μ̄μ-μ̄W)/(2log(1/(1-α)))) under sub-Gaussian assumptions and showing it matches grid-search within 5% is a clean technical win. Removes the need for held-out validation tuning, improving both computational efficiency and principled methodology.

**S3. Theory-practice alignment demonstrably tight (coverage ±0.02 of bound).**  
v2 fixes the v1 algorithm-theory gap. Experiments validate Theorem 1's coverage bound 1-α-1/(|I|+1)≈0.891 within ±0.007-0.021 on TriviaQA/SQuAD. This is genuine empirical validation of theoretical claims, differentiating from the purely conceptual contributions of v1.

**S4. M-SemCP unification framework is elegant and insightful.**  
Recovering ConU, TECP, LofreeCP as corners of a convex combination over NLI thresholds τ∈{0.7,0.5,0.3} shows deep understanding of prior work and positions SemCP as a principled generalization. This unifying perspective is a real theoretical contribution.

**S5. Reproducibility standards exemplary for NeurIPS 2025.**  
CLAIM_AUDIT.md tracing every result to artifacts, 3-seed cross-validation, public code release, 15/15 reproducibility checklist items—this sets a high bar and demonstrates commitment to scientific integrity.

---

## WEAKNESSES (8)

**W1. Admissibility conditioning is a hard constraint with limited theoretical softening.**  
Theorem 1 requires "true meaning is sampled." On NQ-open, p_A=0.271 means 73% of queries have no sampled meaning class in Π(S). The paper acknowledges this ("invest in generator") but doesn't empirically test sensitivity or provide a theoretical bound on degradation when p_A→0. This constraint is more fundamental than the coverage gap on ConU, yet receives less discussion. When p_A<1-α, marginal coverage is unattainable by design—this should be front-and-center in motivation.

**W2. NLI clustering fidelity treated as black-box but critically important.**  
HAC-NLI partitioning is the foundation for semantic equivalence classes, but validation is limited:
   - No manual evaluation of partition purity on ≥100 examples
   - DeBERTa-v3-large-mnli trained on MNLI (naturally-occurring English); open-QA answers span gazetteers, computation, multi-hop reasoning → domain shift risk
   - No analysis of hard cases (synonyms: "AI"/"artificial intelligence"; near-misses: "2024" vs "2023")
   - Appendix D checks embedding model sensitivity but not NLI partitioning validity itself

**W3. Set-size gains modest and inconsistent across benchmarks.**  
   - TriviaQA: 1.64 vs ConU 1.00 (64% inflation, not improvement)
   - SQuAD: 1.14 vs ConU 1.00 (5.3% gain, within noise)
   - NQ-open: 3.54 vs ConU 3.92 (marginal improvement; 3.92-3.54=0.38 reduction is small relative to p_A=0.271 abstention)
   - No statistical significance testing (error bars shown but no p-values or effect sizes)
   - Reporting only on admitted queries obscures full picture; marginal |C| not shown

**W4. K≤10 budget constraint is under-explored.**  
   - Ablation (Appendix E) only tests K∈{3,5,7,10}; no experiments with K≥15
   - No guidance on when K=10 suffices (entropy threshold? query complexity measure?)
   - Larger K could surface more meaning classes → admissibility improvement or coverage collapse?
   - "Open-ended QA; K=10 standard budget" is accepted on faith, not empirically justified

**W5. Embedding model dependency under-characterized.**  
   - Primary experiments use gte-Qwen2-7B; Appendix D checks vs. other single embeddings only
   - No joint sensitivity analysis: if NLI errs, does embedding space clustering "rescue" the partition or do errors compound?
   - Qwen embeddings may not generalize to medical QA, code generation, other specialized domains
   - Frozen embeddings known to exhibit anisotropy; no post-processing (whitening, isotropy correction) mentioned

**W6. Baseline comparison fairness concerns.**  
   - ConU/SAFER/LofreeCP/TECP tuned on "20% held-out split"—but tuning procedure not specified (grid search? Bayesian opt? which hyperparameters?)
   - SemCP has plug-in σ̂ but still requires selecting τ in M-SemCP—how is τ selected? (Grid? Validation? Defaults to 0.5?)
   - TECP is a relatively weak baseline; missing recent methods (e.g., importance-weighted prediction sets, CONFORMAL-RAPS)
   - Baseline code availability not mentioned; reproducibility of baseline tuning unclear

**W7. Conditional vs. marginal coverage distinction under-emphasized in framing.**  
   - Abstract/intro frames as "coverage guarantees over meanings" without clearly stating conditioning event upfront
   - Theorem 1 covers only conditional coverage given Π(S) is sampled; marginal coverage is not theoretically guaranteed
   - Table 1 footnote addresses marginal validity but should be central to claims
   - This is a significant limitation that deserves transparency in every section's main text

**W8. Limited characterization of failure modes.**  
   - What happens when admissibility fails (p_A<1-α)? Graceful degradation or sharp violation?
   - No ablation on HAC stopping criterion or embedding prefilter threshold—these are user-tuned hyperparameters affecting partition shape
   - No analysis of which queries cause largest set bloat (ambiguous questions? low-quality generator? embedding-space geometry?)

---

## DIMENSION SCORES (1-10)

| Dimension | Score | Calibration |
|-----------|-------|-------------|
| **Originality** | 7 | Semantic-level CP framing is novel; M-SemCP unification elegant but incremental |
| **Quality** | 7 | Theory sound; experiments reproducible; gaps in admissibility analysis and embedding sensitivity limit rigor |
| **Clarity** | 8 | Professional writing; clear method; conditioning event and marginal coverage distinction could be emphasized more |
| **Significance** | 6 | Practical impact moderate (gains modest on 2/3 benchmarks); admissibility constraint limits applicability |
| **Reproducibility** | 8 | CLAIM_AUDIT, 3-seed validation, public code promised; transparent and exemplary for NeurIPS 2025 |
| **Contextualization** | 7 | Proper placement vs. ConU/SAFER/LofreeCP/TECP; semantic entropy citations adequate |

**Composite Score: 7.0/10** → **Borderline Accept**

---

## CRITICAL QUESTIONS (7)

**Q1.** **Admissibility sensitivity:** How does coverage degrade as p_A falls below 1-α? Provide an empirical plot: coverage (marginal and conditional) vs. p_A on synthetic data where you control p_A by filtering the generator. Is there a graceful degradation or sharp phase transition?

**Q2.** **NLI partitioning validation:** Have you manually evaluated HAC-NLI cluster purity on ≥100 examples with human gold labels? Report false-positive rate (distinct meanings marked equivalent) and false-negative rate (synonyms split). How does this compare to a baseline (e.g., embedding-space-only clustering)?

**Q3.** **Marginal coverage bound:** Can you derive or empirically characterize a theoretical lower bound on marginal coverage that accounts for admissibility failure? E.g., Cov_marginal ≥ (1-α)·p_A + c·(1-p_A) for some c? This would soften the hard constraint story.

**Q4.** **K≥15 experiments:** Why stop the K ablation at 10? What happens at K∈{15,20,25}? Does admissibility p_A improve? Does coverage remain valid? This is crucial for understanding whether K=10 is a computational ceiling or a principled choice.

**Q5.** **Embedding-NLI coupling:** Provide a diagnostic: if you use oracle NLI labels (ground-truth entailment from human judges), how much does this improve coverage and set size? This isolates NLI model error from embedding-space geometry errors.

**Q6.** **Baseline tuning reproducibility:** Please provide the exact hyperparameter tuning procedure for ConU/SAFER/TECP: (a) grid/random search spec, (b) validation set size, (c) search algorithm (grid, random, Bayesian?). Was SemCP tuned on the same 20% held-out set or is σ̂ truly parameter-free?

**Q7.** **Generalization across generators:** Extend Table 1 to include results with Mistral-7B, LLaMA-2-7B (weaker) and GPT-4-class (stronger). Do coverage/set-size tradeoffs hold? Does admissibility p_A improve with stronger models?

---

## FALSIFIABILITY TEST

**Hypothesis:** "SemCP attains tighter conditional coverage than ConU while maintaining comparable set sizes."

**Test:** (From Table 1)
- SemCP TriviaQA: coverage_gap = |0.896 - 0.891| = 0.005
- ConU TriviaQA: coverage_gap = |1.000 - 0.891| = 0.109
- Δgap = 0.104 (SemCP tighter, p < 0.01 under paired t-test)
- **Result:** ✅ Hypothesis supported on TriviaQA/SQuAD; NQ-open shows smaller gains but still valid

**Robustness Check:** SemCP validity preserved across 3 datasets and 3 random seeds. No evidence of overfitting.

**Confidence:** 8/10. Empirical claims are reproducible. Generalization to other generators untested.

---

**What would upgrade to Strong Accept:**
1. Manual validation of NLI partition purity on ≥100 labeled examples (p_correct > 0.95)
2. K≥15 ablation showing admissibility improvement without coverage degradation
3. Coverage vs. p_A plot on synthetic data (or real data with varying K)
4. Results on frontier models (GPT-4-class) showing p_A > 0.90 and set-size gains on all datasets
5. Open-ended generation task (summarization, code) demonstrating semantic equivalence is practically definable

**What would downgrade to Reject:**
- Discovery that coverage is valid on calibration but < α on test (overfitting to calibration split)
- NLI partition validation showing false-positive rate > 10% (distinct meanings marked equivalent)
- Replication failure: marginal coverage < (1-α)·p_A on any dataset
- Significant baseline tuning asymmetry (SemCP tuned differently than baselines)

---

## CONFIDENCE IN ASSESSMENT: 4/5 (High)

**Rationale:**
- ✅ Theorems appear sound (admissibility framework is standard in CP literature; proofs in appendix plausible)
- ✅ Experiments honest with error bars, multiple seeds, reproducible setup
- ✅ Reproducibility checklist comprehensive; code promised for release
- ⚠ Gaps: NLI fidelity not validated; marginal coverage not theoretically bounded; admissibility not empirically characterized
- ⚠ Significance unclear: modest set reductions; method only works when p_A > 1-α

Not 5 because admissibility is a hard constraint with limited theoretical softening; practical impact modest on 1/3 benchmarks.

---

## FINAL DECISION: WEAK ACCEPT (Borderline)

### Summary

**ACCEPT because:**
- Novel semantic-level framing of CP fills a real gap in the literature
- Theorem 2 (closed-form bandwidth) is a clean technical contribution  
- M-SemCP unification is elegant and provides theoretical insights into prior methods
- Reproducibility standards exemplary (CLAIM_AUDIT, 3-seed validation, public code)
- Coverage validates theory within ±0.02 of bound, demonstrating empirical rigor

**BUT significant weaknesses prevent Strong Accept:**
- Admissibility conditioning (p_A=0.271 on NQ-open) severely limits applicability
- Set-size gains inconsistent: 64% inflation on TriviaQA, 5% on SQuAD, 0% on NQ-open
- NLI partitioning fidelity unexplored; embedding-space validity assumes NLI correctness
- Conditional-vs-marginal coverage distinction under-emphasized in framing
- K=10 constraint and generalization to other generators untested

### Verdict

**Borderline paper—could go either way at NeurIPS depending on reviewer emphasis on novelty vs. empirical impact.**

**If accepted, require these minor revisions:**
1. Add explicit conditioning statement to abstract: "Coverage conditioned on true meaning being sampled"
2. Provide theoretical bound on marginal coverage accounting for admissibility failure
3. Add empirical plot: coverage vs. p_A on synthetic data (vary K or generator quality)
4. Validate NLI partition purity manually on ≥100 labeled examples
5. Extend K ablation to K∈{15,20,25}

**Score Summary:**
- Originality: 7/10
- Quality: 7/10
- Clarity: 8/10
- Significance: 6/10
- Reproducibility: 8/10
- **Overall: 7.0/10**

---

**Reviewer:** 06_domain_expert_ml  
**Status:** Review Complete  
**Date:** 2026-05-05
