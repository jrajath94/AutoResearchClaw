# SemCP Paper Outline — NeurIPS 2025

---

## Candidate Titles

| # | Title | Words | Memorability | Specificity | Novelty Signal | Total |
|---|-------|-------|:---:|:---:|:---:|:---:|
| 1 | **SemCP: Conformal Prediction in Embedding Space for Calibrated Language Generation** | 10 | 4 | 5 | 4 | **13** |
| 2 | **SemCP: Coverage Guarantees Over Meanings, Not Strings** | 8 | 5 | 4 | 5 | **14** |
| 3 | **SemCP: Semantically-Calibrated Conformal Prediction Sets for Open-Ended LLM Generation** | 11 | 3 | 5 | 4 | **12** |

**Recommendation:** Title 2. The contrast "meanings, not strings" is punchy, immediately conveys the core insight, and will stand out in a proceedings table of contents. Title 1 is the safe fallback if reviewers prefer precision over memorability.

---

## Paper Structure & Detailed Outline

### 0. Abstract
**Target:** 190-210 words | **Structure:** PMR+

| Sentence | Role | Content |
|----------|------|---------|
| S1 | Problem | Conformal prediction for LLMs operates at the token level, producing prediction sets of surface strings that conflate paraphrases with genuinely distinct meanings. |
| S2 | Gap | This yields prediction sets 2-4× larger than necessary and provides no semantic coverage guarantee. |
| S3 | Method (name drop) | We introduce **SemCP**, which constructs prediction sets in a semantic embedding space, grouping outputs into meaning equivalence classes via bidirectional entailment and scoring them with learned similarity kernels. |
| S4 | Key insight | A calibration procedure accounts for the many-to-one mapping from strings to meanings, preserving exchangeability under the fixed semantic partition. |
| S5 | Result 1 | SemCP achieves valid marginal coverage (≥1−α) while reducing prediction set sizes by **56-60%** across TriviaQA, CoQA, and TruthfulQA. |
| S6 | Result 2 | Applied to hallucination detection, SemCP prediction sets yield AUROC **0.847**, outperforming semantic entropy (0.812) and token-level CP (0.743), with only 3.1% computational overhead. |

---

### 1. Introduction
**Target:** 850-1000 words (4 paragraphs) | **Citations:** 10-12

**Paragraph 1 — Motivation (200-250 words)**
- Goal: Establish that uncertainty quantification for LLMs is critical and unsolved
- Open with the deployment risk: LLMs generate confidently wrong outputs
- Conformal prediction is the principled framework: distribution-free, finite-sample coverage
- But applying CP to open-ended generation is fundamentally harder than classification
- Evidence: cite deployment failures, hallucination rates in production systems
- Key refs: Angelopoulos & Bates (2023) CP tutorial; Ji et al. (2023) hallucination survey

**Paragraph 2 — Gap (250-300 words)**
- Goal: Show that token-level CP is semantically wasteful
- Token-level CP builds prediction sets over next-token probabilities or full sequences as strings
- Problem 1: "Paris" and "The capital is Paris" are treated as distinct predictions
- Problem 2: Set sizes explode because paraphrases are not deduplicated
- Problem 3: Coverage guarantee is over strings, not meanings — semantically vacuous
- Connect to semantic entropy work (Kuhn et al., 2023) which identified the paraphrase problem but didn't provide conformal guarantees
- Key refs: Quach et al. (2024) token-CP; Ravfogel et al. (2023); Kumar et al. (2023) conformal LM; Kuhn et al. (2023) semantic entropy; Mohri & Hashimoto (2024)

**Paragraph 3 — Our Approach (200-250 words)**
- Goal: Introduce SemCP at a high level
- Key insight: construct prediction sets in embedding space, not token space
- Three components: (1) semantic equivalence partitioning via bidirectional entailment, (2) kernel-based nonconformity scores in embedding space, (3) calibration under many-to-one string→meaning mapping
- The partition is fixed before calibration → exchangeability preserved → coverage valid
- Learned RBF kernels capture task-relevant similarity beyond naive cosine distance

**Paragraph 4 — Contributions (150-200 words)**
- Goal: Crisp, enumerated contribution list
- **C1:** Formal framework for conformal prediction in semantic embedding space with proof of valid marginal coverage under string-to-meaning quotient maps
- **C2:** Kernel-based nonconformity score using learned RBF kernels that reduce prediction set sizes by 56-60% vs. token-level CP
- **C3:** Empirical validation on TriviaQA, CoQA, TruthfulQA demonstrating coverage + efficiency
- **C4:** Downstream applications — hallucination detection (AUROC 0.847), selective abstention, uncertainty-aware RAG

---

### 2. Related Work
**Target:** 700-800 words | **Citations:** ≥18 unique refs | **Subsections:** 3

**2.1 Conformal Prediction for Language Models (250-280 words)**
- Split-conformal prediction basics (Vovk et al., 2005; Papadopoulos et al., 2002)
- Token-level CP for text generation (Quach et al., 2024; Kumar et al., 2023)
- Conformal risk control (Angelopoulos et al., 2024)
- Conformal for structured prediction (Fisch et al., 2021; Deutschmann et al., 2024)
- **Differentiator:** All prior work operates over string/token spaces; SemCP operates in embedding space with semantic equivalence classes

**2.2 Uncertainty Quantification in LLMs (250-280 words)**
- Predictive entropy and verbalized confidence (Kadavath et al., 2022)
- Semantic entropy via bidirectional entailment (Kuhn et al., 2023)
- Hallucination detection methods (Manakul et al., 2023; Varshney et al., 2023)
- Selective prediction / abstention (Geifman & El-Yaniv, 2017; Ren et al., 2023)
- **Differentiator:** Semantic entropy lacks coverage guarantees; SemCP provides them. Hallucination detectors are heuristic; SemCP is calibrated.

**2.3 Embedding Spaces and Semantic Similarity (200-240 words)**
- Sentence embeddings (Reimers & Gurevych, 2019; Gao et al., 2021)
- Kernel methods on embeddings (Muandet et al., 2017)
- NLI-based semantic equivalence (Williams et al., 2018; Kuhn et al., 2023)
- **Differentiator:** SemCP uses embeddings not just for similarity but as the space in which conformal sets are constructed, with learned kernels calibrated for coverage efficiency

---

### 3. Preliminaries
**Target:** 400-500 words | **Goal:** Establish notation shared across all subsequent sections

- **3.1 Conformal Prediction** — Setup: exchangeable data, split-conformal framework, nonconformity scores, quantile threshold q̂, coverage guarantee P(Y_{n+1} ∈ C(X_{n+1})) ≥ 1−α
- **3.2 Problem Setup** — LLM generates response set {y₁,...,y_K} for prompt x; define semantic equivalence relation ∼_s via bidirectional entailment; quotient space Y/∼_s
- **3.3 Notation Table** — Symbols: α, q̂, s(x,y), κ(·,·), [y]_s (equivalence class), Π (partition function)

---

### 4. Method: Semantic Conformal Prediction
**Target:** 1200-1400 words | **Goal:** Full technical description as flowing narrative

**4.1 Semantic Equivalence Partitioning (300-350 words)**
- Define the partition function Π: Y → Y/∼_s
- Bidirectional entailment: y_i ∼_s y_j iff NLI(y_i, y_j) = entailment AND NLI(y_j, y_i) = entailment
- Properties: reflexive, symmetric, transitive → valid equivalence relation
- Fixed partition computed on calibration set, applied unchanged to test
- Evidence link: Finding 3 — bidirectional entailment outperforms agglomerative and spectral clustering

**4.2 Kernel-Based Nonconformity Scores (350-400 words)**
- Define embedding function φ: Y → ℝ^d (sentence transformer)
- Semantic nonconformity score: s(x, y) = 1 − κ_θ(φ(y), μ_x) where μ_x is the kernel mean embedding of the response distribution
- Kernel choice: RBF κ_θ(u,v) = exp(−‖u−v‖² / 2σ²) with learned bandwidth σ
- Training the kernel: minimize prediction set size on held-out calibration data subject to coverage constraint (bi-level optimization)
- Evidence link: Finding 2 — learned RBF outperforms cosine by 25% in set size

**4.3 Calibration Under Many-to-One Mapping (300-350 words)**
- The key technical challenge: standard CP assumes scores are over the output space directly, but we score equivalence classes
- Define the lifted score: s̃(x, [y]_s) = min_{y' ∈ [y]_s} s(x, y')
- Calibration: compute q̂ on calibration set using lifted scores
- Prediction set: C(x) = {[y]_s : s̃(x, [y]_s) ≤ q̂}
- This is a set of meaning equivalence classes, not strings

**4.4 Theoretical Guarantees (250-300 words)**
- **Theorem 1 (Marginal Coverage):** If (X_i, Y_i) are exchangeable and Π is fixed, then P([Y_{n+1}]_s ∈ C(X_{n+1})) ≥ 1 − α
- Proof sketch: exchangeability of lifted scores follows from exchangeability of base pairs + fixed partition; standard split-conformal guarantee applies
- **Proposition 1 (Set Size Reduction):** Under mild conditions on the partition, |C_sem| ≤ |C_token| with equality iff all equivalence classes are singletons
- Discussion of when the bound is tight vs. loose

**Algorithm 1: SemCP Pseudocode**
```
Input: calibration set D_cal, test prompt x*, LLM M, α
1. Generate K samples from M(x*) for each calibration prompt
2. Compute semantic partitions Π via bidirectional entailment
3. Compute lifted nonconformity scores s̃ on D_cal
4. Compute threshold q̂ = Quantile(⌈(1−α)(|D_cal|+1)⌉ / |D_cal|, {s̃_i})
5. Generate K samples from M(x*)
6. Partition into equivalence classes via Π
7. Return C(x*) = {[y]_s : s̃(x*, [y]_s) ≤ q̂}
```

---

### 5. Experiments
**Target:** 900-1100 words

**5.1 Experimental Setup (300-350 words)**
- **Datasets:** TriviaQA (closed QA), CoQA (conversational QA), TruthfulQA (adversarial)
- **LLM:** Specify model(s), temperature, number of samples K=20
- **Baselines:** Token-level CP (Quach et al., 2024), naive sequence CP, semantic entropy (Kuhn et al., 2023)
- **Metrics:** Empirical coverage, average set size, AUROC/AUPRC for hallucination detection
- **Calibration/test split:** 2000 cal / 1000 test with bootstrap CIs (B=10000)
- **Table 1: Hyperparameters** — kernel bandwidth, NLI model, embedding dim, α values

**5.2 Main Results: Coverage and Set Size (300-350 words)**
- Evidence link: Finding 1 table — all six dataset×α combinations
- Headline: 56-60% set size reduction with valid coverage across all settings
- Statistical significance: paired t-test p < 0.001 for set sizes
- Figure 1: Coverage vs. set size Pareto curves for SemCP vs. baselines
- Figure 2: Calibration plot (empirical coverage vs. target 1−α)

**5.3 Downstream Application: Hallucination Detection (300-400 words)**
- Evidence link: Finding 4 — AUROC 0.847 vs. 0.812 (semantic entropy) vs. 0.743 (token CP)
- Method: binary classifier using |C(x)| and whether C(x) contains contradictory classes
- Figure 3: ROC curves for hallucination detection across methods
- Discussion of why conformal calibration gives better thresholds than entropy

---

### 6. Analysis & Ablations
**Target:** 600-800 words

**6.1 Kernel Ablation (200-250 words)**
- Evidence link: Finding 2 — RBF vs. Matérn vs. cosine
- Table: kernel comparison with coverage and set size
- Analysis of why learned bandwidth matters

**6.2 Clustering Method Ablation (200-250 words)**
- Evidence link: Finding 3 — bidirectional entailment vs. agglomerative vs. spectral
- Stability analysis across random seeds

**6.3 Computational Cost (150-200 words)**
- Evidence link: Finding 5 — 3.1% overhead, 12.3ms per sample
- Table: wall-clock breakdown (generation, embedding, clustering, calibration)
- Comparison with semantic entropy compute cost

**6.4 Conditional Coverage Analysis (100-150 words)**
- Stratify by prompt difficulty; report coverage per stratum
- Acknowledge gap up to 0.041 on TruthfulQA hard prompts

---

### 7. Discussion
**Target:** 450-550 words

- **Connection to semantic entropy** (150 words): SemCP subsumes semantic entropy by providing calibrated thresholds instead of heuristic ones; discuss when the extra guarantees matter (safety-critical vs. casual)
- **The Semantic Illusion problem** (150 words): RLHF-aligned hallucinations have high embedding similarity to truthful text; learned kernels partially mitigate but don't solve; connect to concurrent work on representation engineering
- **Broader implications** (150 words): Conformal prediction in embedding spaces may generalize beyond LLMs to any setting where outputs have many-to-one structure (e.g., program synthesis, molecular generation)

---

### 8. Limitations
**Target:** 250-300 words | 5 specific limitations

1. **Marginal, not conditional coverage** — guarantees are average-case; hard prompts may have coverage below 1−α (up to 0.041 gap observed)
2. **Fixed partition assumption** — partition computed once on calibration data; if test-time semantic structure differs, coverage may degrade
3. **Calibration distribution shift** — 3-5% coverage degradation observed on out-of-domain prompts; no distribution-shift robustness guarantee
4. **Open-ended generation sparsity** — K=20 samples may not cover the semantic space for creative/open prompts; set sizes can exceed 10
5. **NLI model dependence** — bidirectional entailment quality depends on the NLI model; errors propagate to partition quality

---

### 9. Conclusion
**Target:** 150-200 words

- Summary (2-3 sentences): SemCP lifts conformal prediction from token space to embedding space, providing the first coverage guarantees over semantic meanings. It reduces prediction set sizes by 56-60% and enables superior hallucination detection.
- Future work (2-3 sentences): Conditional coverage via conformal risk control; adaptive partitioning that refines equivalence classes online; extending to multi-turn dialogue and long-form generation.

---

### 10. Figures & Tables Plan

| ID | Type | Content | Section | Purpose |
|----|------|---------|---------|---------|
| Fig 1 | Plot | Coverage vs. set size Pareto frontier | §5.2 | Visual headline result |
| Fig 2 | Plot | Calibration plot (empirical vs. target coverage) | §5.2 | Validates coverage guarantee |
| Fig 3 | Plot | ROC curves for hallucination detection | §5.3 | Application result |
| Fig 4 | Diagram | SemCP pipeline overview | §4 | Method clarity |
| Tab 1 | Table | Hyperparameters | §5.1 | Reproducibility |
| Tab 2 | Table | Main results (6 dataset×α combos) | §5.2 | Headline numbers |
| Tab 3 | Table | Hallucination detection comparison | §5.3 | Application comparison |
| Tab 4 | Table | Kernel ablation | §6.1 | Ablation |
| Tab 5 | Table | Clustering ablation | §6.2 | Ablation |
| Tab 6 | Table | Computational cost breakdown | §6.3 | Practicality |

---

### 11. Citation Plan (≥30 unique refs)

| Section | Min Citations | Key References |
|---------|:---:|---|
| Introduction | 10 | Angelopoulos & Bates 2023, Ji et al. 2023, Kuhn et al. 2023, Quach et al. 2024, Kumar et al. 2023 |
| Related Work | 18 | Vovk et al. 2005, Papadopoulos 2002, Fisch et al. 2021, Kadavath et al. 2022, Manakul et al. 2023, Reimers & Gurevych 2019, Gao et al. 2021, Muandet et al. 2017, Williams et al. 2018, Geifman & El-Yaniv 2017, Ren et al. 2023, Deutschmann et al. 2024, Mohri & Hashimoto 2024, Ravfogel et al. 2023, Varshney et al. 2023 |
| Method | 4 | Kuhn et al. 2023 (entailment), Muandet et al. 2017 (kernel mean embedding) |
| Experiments | 5 | Baseline method papers |
| Discussion | 3 | Representation engineering, concurrent work |

---

### Word Budget Summary

| Section | Target Words | % of Total |
|---------|:-----------:|:----------:|
| Abstract | 200 | 2.5% |
| Introduction | 950 | 12.0% |
| Related Work | 750 | 9.5% |
| Preliminaries | 450 | 5.7% |
| Method | 1300 | 16.5% |
| Experiments | 1000 | 12.7% |
| Analysis/Ablations | 700 | 8.9% |
| Discussion | 500 | 6.3% |
| Limitations | 275 | 3.5% |
| Conclusion | 175 | 2.2% |
| **Total body** | **~6300** | — |
| Appendix (proofs, extra tables) | ~1500 | supplementary |

**NeurIPS 2025 limit:** 9 pages main + unlimited appendix. At ~700 words/page with figures, 6300 words + 6 figures/tables fits comfortably in 9 pages.

---