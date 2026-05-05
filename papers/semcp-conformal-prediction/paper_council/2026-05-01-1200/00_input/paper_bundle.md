# Paper Bundle — SemCP

## Metadata
- **Title:** SemCP: Coverage Guarantees Over Meanings, Not Strings
- **Authors:** Anonymous
- **Venue:** NeurIPS 2026
- **Source:** artifacts/deliverables/paper.tex

---

## Abstract
Conformal prediction provides distribution-free coverage guarantees, yet existing methods for LLMs operate over the token/string space. SemCP constructs conformal prediction sets in semantic embedding space by partitioning LLM outputs into meaning equivalence classes via bidirectional NLI and scoring them with learned RBF kernels. Claims: (1) conditional coverage 1-α-1/(|I|+1) over meaning classes (Theorem 1); (2) 33% smaller set sizes than string-level baseline on SQuAD; (3) empirical comparison of 5 CP methods on TriviaQA+SQuAD with Qwen2.5-7B-Instruct.

---

## Section-by-Section Summary

### 1. Introduction
- Problem: string-level CP inflates prediction sets; guarantees are over surface strings, not meanings
- Motivation: hallucination rates >75% in legal QA; need formal uncertainty quantification
- Gap: semantic entropy has no coverage guarantee; no prior work provides CP over meanings
- Solution: SemCP — quotient-space conformal prediction with kernel-based nonconformity scores
- Three contributions stated clearly

### 2. Related Work
- CP for LMs: Quach 2023 (token-level), Fisch 2020 (cascaded), Yadkori 2024 (abstention)
- Recent CP methods: ConU (correctness coverage), SAFER (abstention-aware), LofreeCP (logit-free), TECP (token-entropy)
- UQ for LLMs: calibration methods, hallucination detection benchmarks
- Semantic representations: embedding anisotropy, negation insensitivity; Nakkiran 2025 finding that models calibrate at concept level

### 3. Preliminaries
- Split conformal framework: exchangeability assumption, nonconformity scores, threshold quantile
- Problem setup: language model generates K samples; semantic equivalence via bidirectional entailment; quotient space Y/~s
- Notation summary table

### 4. Method (SemCP)
**4.1 Semantic Equivalence Partitioning**
- Pi is deterministic fixed function; bidirectional entailment using DeBERTa-v2-xlarge-MNLI
- Equivalence classes computed per-instance via Union-Find
- Important claim: Pi is NOT data-adaptive; preserves exchangeability

**4.2 Kernel-Based Nonconformity Scores**
- s(x,y) = 1 - kappa_theta(phi(y), mu_x) where mu_x is kernel mean embedding of K samples
- RBF kernel with learnable bandwidth sigma
- sigma optimization: grid search over {0.1, 0.3, 0.5, 1.0, 2.0, 4.0} on held-out 20% split; minimizes set size subject to coverage >= 1-alpha
- Important caveat: constraint infeasible when correct-answer rate is very low (GPT-2 2-3%); sigma defaults

**4.3 Calibration Under Many-to-One Mapping**
- Lifted score: min over strings in the meaning class that were sampled
- Classes with no sampled representative get +infinity (graceful degradation)
- min aggregation chosen over mean/median (produces smaller sets in preliminary experiments)
- Calibration threshold: standard split-conformal quantile

**4.4 Theoretical Guarantees**
- Theorem 1 (Conditional Semantic Coverage): exchangeability + fixed partition rule → conditional coverage >= 1-alpha-1/(|I|+1) given admissibility event A = {true meaning in sampled set}
- Remark 1: marginal coverage ceiling = admissibility probability p_A
- Remark 2: sample-dependent scoring preserves exchangeability (augmented tuple view)
- Observation 1: set size reduction when partition is non-trivial

**Algorithm 1** (SemCP pseudocode): calibration loop, prediction step

**Complexity**: O(K·L) generation + O(K²) NLI + O(K·d) embedding

### 5. Experiments
**5.1 Setup**
- Datasets: TriviaQA (factoid, aliases) + SQuAD v1.1 (extractive span, context)
- Generator: Qwen2.5-7B-Instruct; K=10; T=1.0; nucleus p=0.95; max 64 tokens
- Partition: DeBERTa-v2-xlarge-MNLI; bidirectional entailment binarized at 0.5; Union-Find
- Embeddings: all-MiniLM-L6-v2 (frozen, 384-d)
- Bandwidth grid: {0.1, 0.3, 0.5, 1.0, 2.0, 4.0}
- Splits: N=500 per dataset, 50/50 cal/test, 3 seeds (0,1,2), bootstrap 1000
- Alpha = 0.10

**5.2 Baselines**
- ConU: same NLI partition + frequency score s = 1 - freq/K
- SAFER: ConU-style + abstention rule (freq < 0.10 threshold)
- LofreeCP: logit-free score using empirical frequency + length regularizer
- TECP: token-entropy score via teacher-forced NLL

**5.3 Main Results**
- Table 1: marginal coverage, conditional coverage, set size, abstention rate, admissibility rate
- **CRITICAL**: All results have TODO_NUM / TODO_HOURS placeholders — experiments not yet run
- Figure 3: method comparison; caption says "near-zero coverage for all methods due to GPT-2's limited QA capability" (but paper uses Qwen2.5-7B-Instruct)

**5.4 Analysis**
- Coverage validity: conditional column is primary indicator for SemCP/ConU/SAFER
- Marginal coverage ceiling: p_A upper bounds marginal coverage
- Set size reduction: kernel-based vs frequency-based scoring
- Abstention: SAFER only explicit abstention

### 6. Ablation Studies
- SemCP-NoM2O: without many-to-one aggregation
- SemCP-Euclidean: learned RBF vs Euclidean distance
- SemCP-Adaptive: per-prompt bandwidth
- Naive Semantic: clustering without kernel scoring
- Findings: learned RBF substantially outperforms Euclidean; many-to-one effect is negligible at low match rates

### 7. Discussion
- 33% set size reduction (13.35 vs 19.89 Token-CP on SQuAD) — this is a stated finding
- Near-zero coverage: fundamental constraint when generator quality is low
- Relationship to concurrent methods: SemCP is complementary to ConU/SAFER/LofreeCP/TECP
- Future work: frontier models, adaptive conformal, threshold ablation, open-ended generation

### 8. Limitations
1. Model scale (Qwen2.5-7B vs 70B+ frontier)
2. Benchmark scope (only 2 closed-form QA datasets)
3. NLI threshold fixed at 0.5, not ablated
4. Fixed partition assumption
5. Sample budget K=10
6. Downstream applications not evaluated

### 9. Conclusion
- Theorem 1 conditional coverage; conditioning paradigm unified with ConU/SAFER
- Admissibility-coverage decomposition as practitioner diagnostic
- Code to be released

### Appendix: NeurIPS Paper Checklist
- All 12 items addressed; code to be released; no new datasets; no human subjects

---

## Key Claims (Numbered)
1. Theorem 1: SemCP attains conditional coverage >= 1-alpha-1/(|I|+1) over meaning classes given admissibility
2. 33% set size reduction on SQuAD (13.35 vs 19.89 for Token-CP)
3. Marginal coverage is upper-bounded by admissibility probability p_A
4. RBF kernel substantially outperforms Euclidean distance (18.57 vs 13.35 on SQuAD)
5. Many-to-one aggregation has negligible effect at low paraphrase redundancy
6. Learned kernel is the critical component (Naive Semantic: 18.83 vs SemCP: 13.35)

---

## Experimental Conditions
- alpha = 0.10
- K = 10 samples per prompt
- Datasets: TriviaQA (N=500 val), SQuAD v1.1 (N=500 val)
- 3 random seeds (0, 1, 2)
- 50/50 cal/test split
- 1000 bootstrap resamples for CI

---

## Figures
1. **Fig 1 (framework)**: Pipeline diagram — LLM generates K samples → NLI partition → kernel scoring → conformal calibration → prediction set of meaning classes
2. **Fig 3 (method comparison)**: Left = avg set size (lower=better); Right = empirical coverage. Caption: "near-zero coverage for all methods due to GPT-2's limited QA capability" — BUT paper uses Qwen2.5-7B-Instruct, not GPT-2. **This is a discrepancy.**
3. **Fig 4 (ablation)**: Effect of kernel learning and many-to-one calibration

---

## Tables
1. **Tab hyperparams**: Full experimental hyperparameters
2. **Tab main_results**: All 5 methods × 2 datasets × 5 metrics — ALL TODO_NUM placeholders

---

## Prior Reviews
- None found in artifacts/

---

## Critical Issues Flagged
1. **EXPERIMENTS NOT RUN**: All empirical results (Table 1) are TODO_NUM placeholders. The paper cannot be reviewed properly without actual numbers.
2. **Figure caption inconsistency**: Fig 3 caption mentions "GPT-2" but the experiments section specifies "Qwen2.5-7B-Instruct"
3. **Near-zero coverage claim**: Discussion says all methods get near-zero coverage due to low generator quality, but this contradicts the 33% set-size-reduction claim which requires meaningful coverage to measure
4. **TODO_HOURS**: Experimental runtime placeholder in Table hyperparams
5. **Code not yet released**: "Code and experiment scripts will be released upon publication" — hurts reproducibility score
