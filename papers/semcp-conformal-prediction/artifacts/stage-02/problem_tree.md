# Sub-Question Decomposition: SemCP Research

## Source

**Topic:** Semantically-Calibrated Conformal Prediction for Open-Ended Language Generation

**Parent Goal:** Construct conformal prediction sets in embedding space that provide valid marginal coverage over meanings (not strings), achieving ≥35% smaller prediction sets than token-level methods, validated on CoQA, TriviaQA, and TruthfulQA.

**Landscape Context:** Bridges the gap between Semantic Entropy (Nature 2024, meaning-level clustering without coverage guarantees) and token-level conformal methods (TECP 2025, CLM ICLR 2024, which provide guarantees in the wrong space). Must address the Semantic Illusion challenge (2025) showing naive embeddings fail on RLHF-aligned hallucinations.

---

## Sub-Questions

### SQ1: Semantic Equivalence Partitioning
**How should we define and compute semantic equivalence classes over open-ended LLM outputs such that the partition is stable, computationally tractable, and robust to RLHF-induced embedding distortions?**

- What embedding space (sentence-transformers, LLM hidden states, task-specific fine-tuned encoders) produces clusters that best align with human meaning judgments?
- What clustering algorithm (agglomerative with semantic similarity threshold, spectral clustering on kernel matrix, or the bidirectional entailment approach from Semantic Entropy) yields stable equivalence classes?
- How do we handle the granularity problem — "Paris" and "Paris, the capital of France" are semantically equivalent for a geography question but not for a style-sensitive task?
- Can we quantify partition sensitivity: if the equivalence threshold shifts by ε, how much does the conformal set change?

### SQ2: Nonconformity Score Design
**What nonconformity score function in embedding space yields valid coverage while maximizing statistical efficiency (smallest prediction sets)?**

- Should the score be based on (a) distance to the centroid of the calibration cluster, (b) kernel density estimation in embedding space, (c) likelihood under a learned generative model in the latent space, or (d) a hybrid of generation probability and semantic distance?
- How does the score interact with the many-to-one mapping? If 5 distinct strings map to one meaning, does the aggregate probability mass of that meaning need to be incorporated into the score?
- What kernel function (RBF, Matérn, learned neural kernel) on the embedding space gives the tightest prediction sets while maintaining exchangeability assumptions?
- Critical: Can we design a score that is robust to the Semantic Illusion — where RLHF-aligned hallucinations have high embedding similarity to faithful outputs? This likely requires going beyond cosine similarity to learned discriminative kernels.

### SQ3: Coverage Guarantee Proofs
**Under what formal conditions does SemCP achieve valid marginal coverage at level 1−α over semantic equivalence classes, and what are the necessary modifications to standard conformal prediction theory?**

- Standard CP assumes exchangeable scalar nonconformity scores. When we aggregate strings into meaning classes, does exchangeability still hold? (Likely yes if the equivalence partition is fixed before calibration, but needs formal argument.)
- What is the precise coverage statement? "The true meaning is contained in the prediction set with probability ≥ 1−α" — but "true meaning" needs a formal definition when the reference answer itself admits paraphrases.
- Does the many-to-one mapping from strings to meanings introduce a multiple-testing or selection bias that inflates coverage? If so, what correction (Bonferroni-like or more sophisticated) is needed?
- Can we prove a conditional coverage result (coverage conditional on semantic difficulty) or only marginal? What assumptions would conditional coverage require?
- What is the theoretical prediction set size reduction from deduplication alone, as a function of the paraphrase rate in the sampled outputs?

### SQ4: Downstream Application Protocols
**How should SemCP prediction sets be used for hallucination detection, selective abstention, and uncertainty-aware RAG, and what are the right evaluation metrics for each?**

- **Hallucination detection:** If the prediction set at level α=0.1 contains meanings that contradict each other, this signals the model is uncertain in a semantically meaningful way. How does this compare to semantic entropy's AUROC on TruthfulQA?
- **Selective abstention:** What is the optimal policy — abstain when |prediction set| > k, or when the set's semantic diameter exceeds a threshold? What is the accuracy-coverage tradeoff curve vs. token-level baselines?
- **Uncertainty-aware RAG:** When the SemCP prediction set is large, retrieve additional documents and re-generate. Does this closed-loop system improve final answer quality? What retrieval strategy (query the semantic centroid of the set? query the most uncertain meaning?) works best?
- **Metric design:** AUROC for hallucination detection, accuracy@coverage for abstention, and EM/F1 with retrieval-augmented re-generation for RAG. Are these sufficient or do we need a new metric that captures semantic set quality?

### SQ5: Computational Scalability
**What is the computational overhead of SemCP relative to token-level CP, and can it be made practical for real-time inference?**

- Embedding N sampled completions is O(N) forward passes through the encoder. For N=20 samples per prompt, is this latency acceptable?
- Clustering N embeddings is cheap (O(N²) pairwise similarity for N=20 is trivial), but does the calibration set computation scale? If calibration uses 5K prompts × 20 samples = 100K embeddings, what is the memory/time cost?
- Can we amortize the embedding computation by using the LLM's own hidden states (last-layer representations) instead of a separate encoder? This would save N encoder forward passes but may compromise semantic quality.
- Is there an online/streaming version of SemCP that updates the calibration set incrementally as new data arrives?

---

## Priority Ranking

| Rank | Sub-Question | Rationale | Dependency |
|------|-------------|-----------|------------|
| **P0** | SQ1: Equivalence Partitioning | Everything downstream depends on a well-defined, stable partition. If equivalence classes are noisy, coverage guarantees are meaningless and set sizes are inflated. This is the foundational design choice. | None |
| **P0** | SQ2: Nonconformity Score | The score determines both validity (coverage) and efficiency (set size). Must be co-designed with SQ1's partition. The Semantic Illusion robustness requirement makes this the hardest technical challenge. | SQ1 |
| **P1** | SQ3: Coverage Proofs | Required for the paper's theoretical contribution. However, if SQ1 and SQ2 are well-designed, the proofs may follow from standard CP theory with minor modifications. Start proof sketches early to catch fundamental issues. | SQ1, SQ2 |
| **P2** | SQ4: Downstream Applications | These are the "so what" of the paper — they demonstrate practical value. But they're evaluation protocols, not core methodology. Can be designed in parallel with SQ2-SQ3 and executed after. | SQ1, SQ2, SQ3 |
| **P3** | SQ5: Scalability | Important for practical adoption but not for the core contribution. If SemCP works but is 3× slower than token-level CP, it's still publishable. Optimize after validating the method works. | SQ1, SQ2 |

---

## Risks

| Risk | Severity | Probability | Mitigation |
|------|----------|-------------|------------|
| **Semantic Illusion undermines the entire approach** — RLHF-aligned models produce hallucinations that are embedding-indistinguishable from faithful outputs, making semantic clustering meaningless for exactly the cases where it matters most | **Critical** | Medium (35%) | Use learned discriminative kernels trained on (faithful, hallucinated) pairs rather than pretrained cosine similarity. If this fails, scope the paper to non-RLHF models or factoid QA where hallucinations are more separable. |
| **Equivalence partition instability** — small perturbations to the clustering threshold cause large changes in prediction set membership, making the method fragile | **High** | Medium (30%) | Use hierarchical clustering with a data-driven threshold selection (e.g., Kuhn et al.'s bidirectional entailment from Semantic Entropy). Report sensitivity analysis across threshold values. |
| **Coverage guarantee requires exchangeability that doesn't hold** — if the equivalence partition is data-dependent (learned from the same data used for calibration), exchangeability breaks | **High** | Low (15%) | Use a fixed, pre-specified partition (e.g., entailment-based) or split data into partition-learning and calibration sets. The sample-splitting reduces statistical efficiency but preserves validity. |
| **Set size reduction is modest (<35%)** — if the model rarely produces paraphrases (low paraphrase rate), deduplication gives little benefit over token-level sets | **Medium** | Medium (25%) | Increase the number of sampled completions (N=50 instead of 20) to increase paraphrase diversity. If reduction is still <35%, reframe the contribution around the *interpretability* of semantic sets rather than their size. |
| **Computational cost is prohibitive** — requiring N=20+ samples per prompt plus embedding and clustering makes SemCP 10×+ slower than single-pass inference | **Low** | Low (15%) | This is the same cost as Semantic Entropy (which is already published and accepted). Use LLM hidden states instead of a separate encoder to cut latency. Batch efficiently on GPU. |
| **Evaluation contamination** — CoQA/TriviaQA may be in LLM training data, inflating performance and making coverage guarantees vacuous | **Medium** | Medium (30%) | Use held-out time-split subsets or newly constructed evaluation prompts. Report calibration curves to verify that coverage is genuine, not an artifact of memorization. |