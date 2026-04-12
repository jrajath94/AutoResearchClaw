# Research Goal: Semantic Conformal Prediction (SemCP)

## Topic

**Uncertainty quantification for open-ended language generation** — specifically, constructing conformal prediction sets that provide formal coverage guarantees over *meanings* (semantic equivalence classes) rather than over raw token sequences.

## Novel Angle

### What gap exists?

Current conformal prediction methods for LLMs fall into two camps that have not been bridged:

1. **Token-level conformal methods** (Conformal Language Modeling, ICLR 2024; TECP, 2025; ConU, EMNLP 2024) construct prediction sets over token sequences. These sets are combinatorially large and semantically redundant — "The cat sat on the mat" and "A cat was sitting on the mat" occupy separate slots despite conveying the same meaning. This redundancy inflates set sizes and weakens practical utility.

2. **Semantic uncertainty methods** (Semantic Entropy, Nature 2024; SINdex, 2025) cluster outputs by meaning using embedding similarity, but operate as heuristic detectors without formal coverage guarantees. They answer "is the model uncertain?" but cannot say "the true meaning is in this set with probability ≥ 1-α."

**No existing work constructs conformal prediction sets in embedding space with distribution-free coverage guarantees over semantic equivalence classes.** This is the gap SemCP fills.

### Why is this timely?

Three recent developments create the opportunity:

- **Conformal prediction for NLP has matured** — the TACL 2024 survey and ICLR/NeurIPS 2024-2025 papers establish the theoretical foundations, but all operate in token/string space.
- **Semantic entropy proved that meaning-level clustering is tractable** — but left the conformal guarantee on the table.
- **The Semantic Illusion problem** (arXiv 2025) showed that naive embedding similarity fails on RLHF-aligned hallucinations. SemCP must go beyond raw cosine similarity — our kernel-based nonconformity score with learned calibration directly addresses this.

### How does this differ from standard approaches?

| Aspect | Token-Level CP | Semantic Entropy | **SemCP (ours)** |
|--------|---------------|-----------------|-------------------|
| Space | Token/string | Embedding (heuristic) | **Embedding (formal)** |
| Coverage guarantee | ✅ Over strings | ❌ None | **✅ Over meanings** |
| Handles synonymy | ❌ Redundant sets | ✅ Clusters | **✅ Equivalence classes** |
| Handles polysemy | ❌ Conflates | Partially | **✅ Context-conditioned kernels** |
| Set size efficiency | Poor (combinatorial) | N/A (no sets) | **Tight (semantic dedup)** |
| Addresses Semantic Illusion | N/A | ❌ Vulnerable | **Partially (learned kernels)** |

## Scope

A single paper with three contributions:

1. **Theoretical framework**: Define SemCP — conformal prediction in embedding space with a semantic similarity kernel as the nonconformity score. Prove valid marginal coverage under exchangeability.
2. **Calibration algorithm**: A procedure that handles the many-to-one mapping from strings to meanings by calibrating on semantic equivalence classes (clustered via embedding proximity) rather than individual strings.
3. **Empirical validation**: Demonstrate on standard QA benchmarks that SemCP produces smaller, more semantically coherent prediction sets than token-level baselines, with applications to hallucination detection and selective abstention.

**Out of scope**: Full conditional coverage guarantees (known to be impossible without strong assumptions), training new LLMs, real-time deployment optimization.

## SMART Goal

> **Specific**: Develop SemCP, a conformal prediction framework that constructs prediction sets in embedding space (using a pre-trained sentence encoder), defines nonconformity scores via semantic similarity kernels, and provides provable marginal coverage guarantees (1-α) over meaning-level equivalence classes rather than token sequences.
>
> **Measurable**: (1) Prove marginal coverage ≥ 1-α holds empirically across α ∈ {0.05, 0.10, 0.20}; (2) Achieve ≥35% reduction in average prediction set size compared to token-level CP baselines (CLM, TECP) at equivalent coverage; (3) Demonstrate ≥5 percentage point improvement in hallucination detection AUROC over semantic entropy on TruthfulQA.
>
> **Achievable**: Uses pre-trained models only (sentence-transformers for embeddings, open LLMs for generation). Calibration runs on CPU. Experiments require ~500 GPU-minutes total (inference only, no training).
>
> **Relevant**: Addresses a clear gap at the intersection of two active research threads (conformal prediction + semantic uncertainty for LLMs). Directly applicable to trustworthy AI deployment.
>
> **Time-bound**: Complete draft within 6 weeks. Target venue: ICML 2026 or NeurIPS 2026.

## Constraints

- **Compute**: Single A100 GPU (or equivalent), max ~8 hours total GPU time for all experiments
- **Models**: Open-weight LLMs only (Llama-3-8B, Mistral-7B, Phi-3) for reproducibility; sentence-transformers (all-MiniLM-L6-v2 or GTE-large) for embeddings
- **Data**: Publicly available QA benchmarks (see Benchmark section below)
- **Software**: Python, PyTorch, HuggingFace Transformers, sentence-transformers. No proprietary APIs required.
- **Theory**: Marginal coverage only (not conditional). Exchangeability assumed for calibration data.

## Benchmark

### Primary Evaluation

| Benchmark | Source | Task | Metrics | Known SOTA |
|-----------|--------|------|---------|------------|
| **CoQA** | Stanford (Reddy et al., 2019) | Conversational QA | Coverage rate, avg set size, semantic set size | TECP reports coverage ≥ 1-α with ~3.2 avg set size at α=0.1 |
| **TriviaQA** | Joshi et al., 2017 | Open-domain QA | Coverage rate, avg set size, F1 of set members | TECP reports coverage ≥ 1-α with competitive set sizes |
| **TruthfulQA** | Lin et al., 2022 | Hallucination/truthfulness | AUROC for hallucination detection, coverage | Semantic entropy baseline ~0.79 AUROC |
| **Natural Questions (NQ-Open)** | Kwiatkowski et al., 2019 | Factoid QA | Coverage, set size, abstention accuracy | Used in semantic entropy evaluations |

### Evaluation Protocol

1. **Coverage validity**: Verify empirical coverage ≥ 1-α across calibration splits (500+ calibration examples, 1000+ test examples)
2. **Set efficiency**: Compare average prediction set size (# semantic equivalence classes) against token-level CP baselines
3. **Downstream utility**: Hallucination detection (AUROC), selective abstention (accuracy-coverage curve), and prediction set interpretability (human evaluation on 100 samples)

### Baselines

- **Token-level CP**: Conformal Language Modeling (CLM), TECP
- **Semantic uncertainty**: Semantic Entropy, SINdex
- **Naive embedding CP**: Standard split conformal with cosine distance (ablation to isolate kernel contribution)

## Success Criteria

A publishable result requires **all three**:

1. **Valid coverage**: SemCP achieves empirical coverage within ±2% of the target 1-α across all benchmarks and all tested α values. This is table stakes — conformal methods must maintain coverage.

2. **Meaningful set size reduction**: ≥35% smaller prediction sets than the best token-level CP baseline at equivalent coverage levels. This demonstrates the practical value of operating in semantic space. (The original target of 40-65% is aspirational; 35% is the minimum publishable threshold.)

3. **Downstream improvement**: At least one of:
   - Hallucination detection AUROC ≥ 0.84 on TruthfulQA (vs ~0.79 for semantic entropy)
   - Selective abstention: ≥3% accuracy improvement over baselines at 80% coverage
   - Qualitative demonstration that semantic prediction sets are more interpretable than token-level sets (human evaluation)

**Stretch goals** (strengthen but not required for publication):
- Theoretical analysis of when/why semantic CP produces tighter sets (information-theoretic bound)
- Robustness to embedding model choice (show results hold across 3+ embedding models)
- Application to uncertainty-aware RAG with measurable retrieval improvement

## Risk Factors

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Semantic Illusion: embedding similarity fails to separate hallucinations from faithful text | Medium-High | Use learned/fine-tuned kernels, not raw cosine. Position paper honestly about this limitation. |
| Set size reduction < 35% | Medium | Adjust semantic clustering threshold; try multiple embedding models; report results per-domain |
| Coverage violations due to embedding discretization | Low-Medium | Use conservative calibration with Bonferroni correction for clustering errors |
| Exchangeability violation in practice | Low | Use weighted conformal prediction variant; document conditions where assumption holds |

## Generated

2026-04-12T12:00:00-04:00
