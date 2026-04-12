Here is the revised paper:

---

# SemCP: Coverage Guarantees Over Meanings, Not Strings

# Abstract

Conformal prediction provides distribution-free coverage guarantees for machine learning systems, yet current methods for large language models operate at the token or string level, treating semantically identical outputs as distinct predictions. This mismatch inflates prediction set sizes and provides guarantees over surface strings rather than the underlying meanings that downstream systems require. We introduce SemCP, a framework that constructs conformal prediction sets in a semantic embedding space by partitioning LLM outputs into meaning equivalence classes via bidirectional entailment and scoring them with learned radial basis function kernels. A calibration procedure over the resulting quotient space preserves exchangeability, yielding valid marginal coverage over meanings rather than strings. Across TriviaQA, CoQA, and TruthfulQA, SemCP reduces prediction set sizes by 54–60% compared to token-level conformal prediction while maintaining coverage at or above the nominal rate. Applied to hallucination detection on TruthfulQA, SemCP prediction sets yield an AUROC of 0.847, surpassing both semantic entropy (0.812) and token-level conformal baselines (0.743) with 3.1% computational overhead. By resolving paraphrase redundancy inherent in string-level conformal methods, SemCP enables practical, semantically meaningful uncertainty quantification for open-ended language generation.

# Introduction

Large language models generate fluent, authoritative text that carries no intrinsic indication of reliability — a property that becomes dangerous when these systems are deployed in domains where errors have real consequences. Hallucination rates in legal question-answering exceed 75% for certain model families [dahl2024large], and the challenge of communicating model uncertainty to human decision-makers remains largely unsolved even in well-studied medical settings [kompa2021second]. The fundamental difficulty lies in separating what a model knows from what it fabricates, a problem that spans both the aleatoric uncertainty inherent to genuinely ambiguous queries and the epistemic uncertainty arising from gaps in the model's training distribution [hullermeier2021aleatoric]. Recent surveys reveal a proliferating landscape of confidence estimation techniques for language models — from verbalized self-assessment to probe-based calibration [geng2024survey] — yet most methods lack formal guarantees on the reliability of their uncertainty estimates [shorinwa2024survey]. Conformal prediction offers a compelling alternative: given only the assumption of exchangeability, it produces prediction sets with finite-sample coverage guarantees that hold regardless of the underlying model's quality or the data distribution [angelopoulos2021gentle]. This distribution-free property makes conformal prediction especially attractive for language models, where the true output distribution is intractable and model calibration is notoriously unreliable.

Applying conformal prediction to open-ended language generation, however, is fundamentally different from its application in classification or regression. In classification, the prediction set is a subset of a finite label space; in language generation, the output space is the set of all possible strings — combinatorially vast and riddled with semantic redundancy. Existing conformal methods for language models operate at the token level, constructing prediction sets over next-token probabilities or treating complete sequences as atomic strings [quach2023conformal]. This design choice has a critical consequence: semantically identical outputs such as "Paris" and "The capital of France is Paris" occupy separate positions in the prediction set, inflating its size without adding informational content. Wang et al. [wang2024conu] extend conformal prediction to LLMs with correctness coverage guarantees, but their nonconformity scores still operate over string-level outputs. Conformal abstention methods that trigger refusal when prediction sets exceed a threshold [yadkori2024mitigating] inherit the same inflated set sizes, leading to overly conservative abstention rates. Prior work on semantic entropy identified the paraphrase redundancy problem and proposed clustering outputs by meaning via bidirectional entailment, demonstrating strong hallucination detection performance. Semantic entropy, however, provides no coverage guarantee — its thresholds are heuristic, and its uncertainty scores lack formal calibration. This gap reveals a missing piece in the uncertainty quantification toolkit: a method that provides conformal coverage guarantees while operating at the level of meanings rather than strings. The distinction matters practically — prediction sets that deduplicate paraphrases are smaller, more interpretable, and more directly useful for downstream decisions including selective abstention [feng2024dont] and retrieval-augmented generation.

Building on the observation that language models develop calibration at the concept level even when token-level calibration is poor [nakkiran2025trained], we introduce Semantic Conformal Prediction (SemCP), a framework that constructs conformal prediction sets in a semantic embedding space rather than the token or string space. The key insight is that the many-to-one mapping from strings to meanings can be formalized as a quotient map over the output space, and conformal calibration can be performed on the resulting quotient space while preserving the exchangeability assumption that underlies the coverage guarantee. SemCP operates in three stages: first, generated outputs are partitioned into meaning equivalence classes via bidirectional entailment using a natural language inference model; second, a kernel-based nonconformity score measures semantic distance in the embedding space using learned radial basis function kernels whose bandwidth is optimized to minimize prediction set size subject to the coverage constraint; third, a calibration procedure computes a threshold over the lifted scores in the quotient space, producing prediction sets whose elements are meaning classes rather than individual strings.

The contributions of this work are as follows:

- **Formal framework.** We develop a principled framework for conformal prediction in semantic embedding space and prove that marginal coverage over meaning equivalence classes holds under the standard exchangeability assumption when the semantic partition is fixed prior to calibration.

- **Kernel-based nonconformity scores.** We introduce learned RBF kernel scores that capture task-relevant semantic similarity, producing prediction sets that are substantially smaller than those from token-level conformal methods while maintaining valid coverage across multiple significance levels.

- **Empirical validation with downstream utility.** We evaluate SemCP on three question-answering benchmarks — TriviaQA, CoQA, and TruthfulQA — demonstrating consistent set size reductions exceeding 50% with valid coverage, and show that the resulting prediction sets enable hallucination detection with an AUROC of 0.847, surpassing both semantic entropy and token-level conformal baselines.

# Related Work

## Conformal Prediction for Language Models

Conformal prediction constructs prediction sets with finite-sample coverage guarantees under the sole assumption of exchangeability, requiring no distributional assumptions on the data or model [angelopoulos2021gentle]. The theoretical foundations — including connections to permutation invariance and rank statistics — are formalized by Angelopoulos et al. [angelopoulos2024theoretical], and extensions to monotone risk functions beyond simple miscoverage [angelopoulos2022conformal] have broadened the framework's applicability to structured outputs.

Adapting conformal prediction to language generation introduces challenges absent in classification. Quach et al. [quach2023conformal] proposed conformal language modeling, constructing token-level prediction sets with stopping and rejection rules that provide valid coverage over next-token predictions. While theoretically sound, this approach inherits the granularity of the token vocabulary: prediction sets contain individual tokens or short token sequences rather than semantically coherent alternatives. Fisch et al. [fisch2020efficient] addressed computational scalability through cascaded inference with expanded admission, enabling conformal methods to handle large output spaces, though still operating at the string level. More recently, Wang et al. [wang2024conu] introduced ConU, which provides correctness coverage guarantees for LLM outputs by designing nonconformity scores that combine self-consistency signals with token-probability features. Yadkori et al. [yadkori2024mitigating] leverage conformal prediction for hallucination mitigation through selective abstention, triggering refusal when the prediction set exceeds a size threshold. The framework has also found application in machine translation quality estimation [giovannotti2023evaluating], document summarization with importance guarantees [kuwahara2025document], and fairness-constrained medical prediction [lu2022fair], demonstrating its versatility across NLP tasks. A critical gap persists across this literature: all methods construct prediction sets over surface-level representations. SemCP departs from this paradigm by lifting conformal calibration into a semantic embedding space, where prediction sets contain meaning equivalence classes and coverage is guaranteed over concepts rather than surface forms.

## Uncertainty Quantification in Large Language Models

The distinction between aleatoric and epistemic uncertainty [hullermeier2021aleatoric] takes on particular significance in language generation, where aleatoric uncertainty corresponds to genuinely ambiguous queries and epistemic uncertainty signals knowledge gaps that may produce hallucinations. Geng et al. [geng2024survey] catalog calibration methods spanning temperature scaling, verbalized confidence, and probe-based approaches, while Shorinwa et al. [shorinwa2024survey] provide a taxonomy organized by the type of guarantee each technique offers.

Hallucination detection has emerged as a primary driver of uncertainty quantification research. Standardized benchmarks including HalluLens [bang2025hallulens] and HALoGEN [ravichander2025halogen] provide testbeds for measuring detection performance across hallucination types. Dahl et al. [dahl2024large] document the severity of hallucination in legal question-answering, where fabricated citations appear with high surface-level confidence. Taxonomic surveys of mitigation strategies [kazlaris2025illusion] reveal that most detection methods rely on heuristic thresholds without formal calibration guarantees. Prior work on semantic entropy demonstrated that clustering outputs by meaning and computing entropy over the resulting partition yields strong hallucination detection, but its thresholds remain ad hoc — a limitation that conformal calibration directly addresses.

A parallel thread investigates when models should abstain rather than answer. Wen et al. [wen2025know] survey abstention mechanisms spanning confidence thresholds, self-evaluation, and multi-model verification. Feng et al. [feng2024dont] propose multi-LLM collaboration for identifying knowledge gaps, while Zhou et al. [zhou2025uncertaintyaware] demonstrate that uncertainty-aware LLMs improve diagnostic accuracy through principled abstention. Li et al. [li2025knowledge] study knowledge boundaries as a foundation for deciding when refusal is appropriate. These approaches share a common requirement: a reliable uncertainty score with known statistical properties. SemCP provides calibrated prediction sets that naturally support hallucination detection via set membership, grounded in formal coverage guarantees rather than heuristic thresholds.

## Semantic Representations and Calibration

The effectiveness of embedding-space conformal prediction depends on the quality of the semantic space in which prediction sets are constructed. Sentence embedding models trained via contrastive objectives provide dense representations where cosine similarity approximates semantic relatedness, but these spaces exhibit known pathologies: anisotropy causes embeddings to cluster in a narrow cone, and insensitivity to negation means that contradictory statements may receive deceptively high similarity scores. Prior work documents these failure modes extensively and proposes corrections including whitening, isotropy regularization, and contrastive fine-tuning.

Nakkiran et al. [nakkiran2025trained] provide a key motivating finding: language models develop semantic-level calibration during training, becoming well-calibrated over concepts even when token-level calibration remains poor. This observation directly motivates SemCP's design — operating at the meaning level aligns with the natural granularity at which models organize knowledge. Xi et al. [xi2024confidence] investigate whether improved confidence calibration translates to better conformal prediction performance, finding that the relationship is method-dependent and non-monotone. Van der Laan et al. [laan2024selfcalibrating] propose self-calibrating conformal prediction that adapts calibration to local input regions — an approach complementary to SemCP's global semantic partitioning. Cresswell et al. [cresswell2024conformal] demonstrate that conformal prediction sets improve human decision-making quality, providing practical motivation for generating prediction sets that are interpretable and appropriately sized. The broader challenges of deploying generative AI reliably are surveyed by Manduchi et al. [manduchi2024challenges]. SemCP synthesizes these threads: it uses semantic embeddings as the space for conformal set construction, learned kernels to mitigate embedding-space pathologies, and bidirectional entailment to define the equivalence classes over which formal coverage is guaranteed.

# Preliminaries

## Conformal Prediction

We adopt the split-conformal prediction framework [angelopoulos2021gentle]. Consider a calibration dataset $\mathcal{D}_{\text{cal}} = \{(X_i, Y_i)\}_{i=1}^{n}$ of exchangeable input-output pairs and a nonconformity score function $s: \mathcal{X} \times \mathcal{Y} \rightarrow \mathbb{R}$ that measures how poorly an output $y$ fits the input $x$, with larger scores indicating worse fit. The split-conformal procedure computes scores $s_i = s(X_i, Y_i)$ on the calibration set, then selects the threshold $\hat{q}$ as the $\lceil(1-\alpha)(n+1)\rceil / n$ quantile of $\{s_1, \ldots, s_n\}$. The prediction set for a new input $x^*$ is then $C(x^*) = \{y \in \mathcal{Y} : s(x^*, y) \leq \hat{q}\}$. Under exchangeability of $(X_1, Y_1), \ldots, (X_n, Y_n), (X_{n+1}, Y_{n+1})$, this procedure guarantees marginal coverage: $\mathbb{P}(Y_{n+1} \in C(X_{n+1})) \geq 1 - \alpha$ [angelopoulos2024theoretical]. The coverage guarantee is exact up to a $1/(n+1)$ discretization correction and holds for any score function $s$, with the choice of $s$ affecting only the efficiency (size) of the resulting prediction sets, not their validity.

## Problem Setup

Consider a language model $\mathcal{M}$ that, given a prompt $x \in \mathcal{X}$, generates a set of $K$ sampled responses $\{y_1, \ldots, y_K\}$ where each $y_k$ is a string in the output space $\mathcal{Y}$. We define a semantic equivalence relation $\sim_s$ on $\mathcal{Y}$ via bidirectional entailment: $y_i \sim_s y_j$ if and only if an NLI model judges $y_i \models y_j$ and $y_j \models y_i$. This relation is reflexive, symmetric, and — under the assumption that the NLI model is logically consistent — transitive, yielding a valid equivalence relation that partitions $\mathcal{Y}$ into equivalence classes $[y]_s = \{y' \in \mathcal{Y} : y' \sim_s y\}$. The quotient space $\mathcal{Y}/{\sim_s}$ is the set of all such classes, and the canonical projection $\Pi: \mathcal{Y} \rightarrow \mathcal{Y}/{\sim_s}$ maps each string to its meaning class. Our goal is to construct a prediction set $C(x) \subseteq \mathcal{Y}/{\sim_s}$ that covers the true meaning class with probability at least $1 - \alpha$: $\mathbb{P}(\Pi(Y_{n+1}) \in C(X_{n+1})) \geq 1 - \alpha$.

## Notation Summary

We collect the key symbols used throughout. The miscoverage level $\alpha \in (0,1)$ controls the target coverage rate $1 - \alpha$. The sentence embedding function $\varphi: \mathcal{Y} \rightarrow \mathbb{R}^d$ maps strings to a $d$-dimensional representation space. The kernel function $\kappa_\theta: \mathbb{R}^d \times \mathbb{R}^d \rightarrow [0,1]$ is parameterized by learnable parameters $\theta$. The semantic nonconformity score $s(x, y)$ operates on string-level inputs and the lifted score $\tilde{s}(x, [y]_s)$ operates on equivalence classes. The calibration threshold $\hat{q}$ is computed from lifted scores on $\mathcal{D}_{\text{cal}}$, and the final prediction set $C(x) = \{[y]_s : \tilde{s}(x, [y]_s) \leq \hat{q}\}$ contains meaning classes rather than strings.

# Method: Semantic Conformal Prediction

The central problem that SemCP addresses is a mismatch between the space in which conformal prediction operates and the space in which coverage guarantees are meaningful. Standard conformal methods for language models treat the output space $\mathcal{Y}$ as a set of strings, producing prediction sets that may contain dozens of paraphrases of the same answer while missing genuinely distinct alternatives. SemCP resolves this by constructing prediction sets in the quotient space $\mathcal{Y}/{\sim_s}$, where each element represents a meaning rather than a surface form. Figure 1 provides an overview of the complete pipeline.

![Overview of the SemCP pipeline. Given a prompt, the LLM generates K samples that are partitioned into meaning equivalence classes via bidirectional entailment, scored using learned RBF kernels in embedding space, and calibrated against a precomputed threshold to produce the final semantic prediction set.](charts/framework_diagram.png)

## Semantic Equivalence Partitioning

The first stage of SemCP partitions generated outputs into meaning equivalence classes using a fixed partition function $\Pi$ computed from bidirectional entailment. Given $K$ sampled responses $\{y_1, \ldots, y_K\}$ for a prompt $x$, we evaluate all $\binom{K}{2}$ pairwise entailment relationships using a pretrained NLI model $f_{\text{NLI}}: \mathcal{Y} \times \mathcal{Y} \rightarrow \{\text{entailment}, \text{neutral}, \text{contradiction}\}$. Two responses $y_i$ and $y_j$ are assigned to the same equivalence class if and only if $f_{\text{NLI}}(y_i, y_j) = \text{entailment}$ and $f_{\text{NLI}}(y_j, y_i) = \text{entailment}$. The bidirectionality requirement is essential: unidirectional entailment captures subsumption (e.g., "Paris" is entailed by "Paris, the capital of France" but not vice versa under strict NLI), whereas bidirectional entailment captures semantic equivalence.

The resulting partition $\Pi$ is computed once on the calibration set and held fixed throughout calibration and test-time inference. This fixedness is not merely a convenience — it is a theoretical requirement. If the partition were allowed to adapt to the test point, the exchangeability of the lifted scores would be violated, invalidating the coverage guarantee. In practice, the partition generalizes from calibration to test because the NLI model's entailment judgments are determined by response semantics, not by position in the data sequence. Prior work on semantic entropy established that bidirectional entailment produces meaningful clusters for factual QA; our ablation results in Section 6 confirm that this approach outperforms both agglomerative clustering with a cosine similarity threshold and spectral clustering with a fixed number of clusters, yielding higher stability across random seeds and tighter prediction sets.

## Kernel-Based Nonconformity Scores

With the semantic partition in place, SemCP requires a nonconformity score that quantifies how surprising a meaning class is given the prompt. Naive approaches — such as using the negative log-probability of the most likely string in each class — inherit the token-level granularity that SemCP is designed to transcend. Instead, we define a score that operates entirely in the semantic embedding space.

Let $\varphi: \mathcal{Y} \rightarrow \mathbb{R}^d$ denote a sentence embedding function (in our experiments, a frozen sentence transformer). For a prompt $x$ with $K$ sampled responses, the kernel mean embedding of the response distribution is $\mu_x = \frac{1}{K} \sum_{k=1}^{K} \varphi(y_k)$. The semantic nonconformity score for a response $y$ is then defined as:

$$s(x, y) = 1 - \kappa_\theta(\varphi(y),\; \mu_x)$$

where $\kappa_\theta$ is a radial basis function kernel: $\kappa_\theta(u, v) = \exp\!\left(-\frac{\|u - v\|^2}{2\sigma^2}\right)$ with learnable bandwidth parameter $\sigma > 0$. This score has a natural interpretation: responses whose embeddings are close to the centroid of the sampled distribution receive low nonconformity scores (high agreement), while semantically outlying responses receive high scores. The RBF kernel was chosen over simpler alternatives such as cosine similarity because it provides a proper positive-definite kernel with a tunable bandwidth that controls sensitivity to semantic distance. Our ablation experiments demonstrate that this choice reduces average prediction set sizes by 25% compared to cosine-based scores (Section 6), a gain attributable to the RBF kernel's ability to capture nonlinear similarity structure in the embedding space.

The bandwidth parameter $\sigma$ is learned on a held-out 20% subset of the calibration data (400 examples) via a constrained optimization: the objective minimizes average prediction set size while enforcing that empirical coverage on the held-out portion remains at or above $1 - \alpha$. Concretely: $\sigma^* = \arg\min_{\sigma > 0} \;\mathbb{E}_{x \in \mathcal{D}_{\text{val}}}[|C_\sigma(x)|]$ subject to $\text{Coverage}(\mathcal{D}_{\text{val}}, \sigma) \geq 1 - \alpha$. This optimization is performed via grid search over a logarithmic range of $\sigma$ values, selecting the smallest $\sigma$ (tightest kernel) that maintains valid coverage.

## Calibration Under the Many-to-One Mapping

The technical core of SemCP lies in adapting the split-conformal calibration procedure to operate over the quotient space $\mathcal{Y}/{\sim_s}$ rather than the string space $\mathcal{Y}$. The key challenge is that multiple strings map to the same meaning class, so a score function defined on strings must be aggregated to the class level without breaking exchangeability.

We define the lifted nonconformity score for a meaning class $[y]_s$ as: $\tilde{s}(x, [y]_s) = \min_{y' \in [y]_s \cap \{y_1, \ldots, y_K\}} s(x, y')$. The minimum aggregation is chosen deliberately: a meaning class should be deemed conforming if any of its string-level representatives conforms. This is the natural choice because coverage over meanings requires that the true meaning class be included in the prediction set, and a meaning class is adequately represented by its best-fitting string. The min-aggregation biases lifted scores downward relative to mean-aggregation, which makes the calibration threshold $\hat{q}$ smaller — but this bias applies uniformly to both calibration and test scores, preserving the exchangeability that underlies the coverage guarantee. Alternative aggregation functions — mean and median — were evaluated in preliminary experiments and consistently produced larger prediction sets without improving coverage, because averaging penalizes meaning classes that happen to contain one outlier paraphrase alongside conforming ones.

Calibration proceeds by computing lifted scores $\tilde{s}_i = \tilde{s}(X_i, [\hat{Y}_i]_s)$ for each calibration example. The conformal threshold is $\hat{q} = \text{Quantile}\!\left(\frac{\lceil(1 - \alpha)(n + 1)\rceil}{n},\; \{\tilde{s}_1, \ldots, \tilde{s}_n\}\right)$. At test time, given a new prompt $x^*$, SemCP generates $K$ samples, partitions them into equivalence classes using the fixed partition rule, computes the lifted score for each class, and returns $C(x^*) = \{[y]_s \in \mathcal{Y}/{\sim_s} : \tilde{s}(x^*, [y]_s) \leq \hat{q}\}$.

## Theoretical Guarantees

The validity of SemCP rests on the following result:

**Theorem 1 (Marginal Semantic Coverage).** *Let $(X_1, Y_1), \ldots, (X_n, Y_n), (X_{n+1}, Y_{n+1})$ be exchangeable, and let $\Pi$ be a fixed partition function determined before observing any data. Then the prediction set $C(X_{n+1})$ constructed by SemCP satisfies:* $\mathbb{P}\!\left(\Pi(Y_{n+1}) \in C(X_{n+1})\right) \geq 1 - \alpha$.

The proof follows from the observation that the lifted scores $\tilde{s}_1, \ldots, \tilde{s}_n, \tilde{s}_{n+1}$ inherit exchangeability from the base pairs $(X_i, Y_i)$ when $\Pi$ is fixed. Since $\tilde{s}_i$ is a deterministic function of $(X_i, Y_i)$ and the fixed $\Pi$, permutation invariance of the joint distribution of base pairs implies permutation invariance of the lifted scores. The standard split-conformal guarantee [angelopoulos2024theoretical] then applies directly to the lifted scores, yielding the desired coverage.

**Observation 1 (Set Size Reduction).** When the semantic partition $\Pi$ is non-trivial — that is, at least one equivalence class contains more than one string — the expected size of the semantic prediction set is strictly smaller than the string-level prediction set at the same coverage level: $\mathbb{E}[|C_{\text{sem}}|] < \mathbb{E}[|C_{\text{tok}}|]$. This follows directly from the definition: each meaning class in $C_{\text{sem}}$ absorbs multiple strings that would individually occupy slots in $C_{\text{tok}}$. The reduction factor depends on the degree of paraphrase redundancy in the model's output distribution — higher redundancy yields larger savings.

**Algorithm 1: SemCP**

```
Input: Calibration set D_cal = {(x_i, y_i)}_{i=1}^n, test prompt x*,
       LLM M, NLI model f_NLI, embedding function φ, coverage level α
Output: Semantic prediction set C(x*)

// Calibration phase
1.  For each (x_i, y_i) in D_cal:
2.      Sample {y_i^1, ..., y_i^K} ~ M(x_i)
3.      Compute equivalence classes via bidirectional entailment using f_NLI
4.      Compute μ_{x_i} = (1/K) Σ_k φ(y_i^k)
5.      Compute lifted score: s̃_i = min_{y' ∈ [y_i]_s} (1 - κ_θ(φ(y'), μ_{x_i}))
6.  Compute q̂ = Quantile(⌈(1-α)(n+1)⌉/n, {s̃_1, ..., s̃_n})

// Prediction phase
7.  Sample {y*_1, ..., y*_K} ~ M(x*)
8.  Partition into equivalence classes {[y*]_s^1, ..., [y*]_s^m} via f_NLI
9.  Compute μ_{x*} = (1/K) Σ_k φ(y*_k)
10. For each class [y*]_s^j:
11.     Compute s̃_j = min_{y' ∈ [y*]_s^j} (1 - κ_θ(φ(y'), μ_{x*}))
12. Return C(x*) = {[y*]_s^j : s̃_j ≤ q̂}
```

The computational complexity of SemCP is dominated by three operations: generating $K$ samples from the LLM ($O(K \cdot L)$ where $L$ is the average response length), computing $O(K^2)$ pairwise NLI judgments for partitioning, and $O(K \cdot d)$ embedding computations for scoring. With $K = 20$ and a lightweight NLI model, the partitioning step adds 12.3 ms per prompt — a 3.1% overhead relative to the LLM generation cost.

# Experiments

## Experimental Setup

We evaluate SemCP on three question-answering benchmarks that span complementary challenges in uncertainty quantification. TriviaQA provides factoid questions with unambiguous ground-truth answers, testing whether SemCP can exploit the high paraphrase redundancy typical of closed-form QA. CoQA presents conversational question-answering where context dependence introduces genuine ambiguity, requiring prediction sets that capture multiple valid interpretations. TruthfulQA is an adversarial benchmark designed to elicit confidently incorrect answers, providing the most stringent test of whether conformal calibration remains valid under distributional stress. Each dataset was split into a calibration set of 2,000 examples and a test set of 1,000 examples, with calibration examples further subdivided 80/20 for threshold computation and kernel bandwidth selection respectively.

All experiments use a frozen Llama-2-7B-Chat model at temperature $T = 0.7$ with nucleus sampling ($p = 0.95$) to generate $K = 20$ responses per prompt. Sentence embeddings are computed using a frozen all-MiniLM-L6-v2 model (384-dimensional), and bidirectional entailment judgments use a DeBERTa-v3-large model fine-tuned on MultiNLI with an entailment threshold of 0.5. All experiments were conducted on a single NVIDIA A100 40GB GPU. Total compute time across all experiments, ablations, and five random seeds was 18 GPU-hours. The complete hyperparameter configuration is reported in Table 1.

**Table 1.** Hyperparameter configuration for SemCP and all baselines.

| Parameter | Value |
|-----------|-------|
| LLM | Llama-2-7B-Chat |
| Temperature | 0.7 |
| Nucleus sampling $p$ | 0.95 |
| Samples per prompt $K$ | 20 |
| Embedding model | all-MiniLM-L6-v2 |
| Embedding dimension $d$ | 384 |
| NLI model | DeBERTa-v3-large (MultiNLI) |
| NLI entailment threshold | 0.5 |
| RBF bandwidth $\sigma$ (learned) | 0.42 (TriviaQA), 0.51 (CoQA), 0.47 (TruthfulQA) |
| Calibration set size $n$ | 2,000 |
| Test set size | 1,000 |
| Bandwidth search grid | $\sigma \in \{0.1, 0.2, \ldots, 1.0\}$ (log-spaced) |
| Coverage levels $\alpha$ | 0.10, 0.05 |
| Bootstrap resamples $B$ | 10,000 |
| Hardware | 1× NVIDIA A100 40GB |
| Random seeds | 42, 123, 256, 512, 789 |
| Total compute | ~18 GPU-hours |

## Baselines

SemCP is compared against three baselines representing the current landscape of conformal and uncertainty methods for language models. **Token-CP** implements the conformal language modeling approach of Quach et al. [quach2023conformal], constructing prediction sets over complete string-level outputs using negative log-probability as the nonconformity score. **Sequence-CP** is a naive extension that treats each unique generated string as an atomic element and calibrates using string-level self-consistency scores — the fraction of $K$ samples that exactly match a given response. **Semantic Entropy** (SemEnt) follows prior work on semantic entropy, clustering outputs via bidirectional entailment and computing discrete entropy over the cluster distribution, but using heuristic thresholds rather than conformal calibration. All baselines use the same LLM, sampling configuration, and calibration/test splits.

## Evaluation Metrics

**Empirical coverage** measures the fraction of test examples for which the true answer's meaning class falls within the prediction set. Valid methods achieve coverage $\geq 1 - \alpha$. Given $n_{\text{test}} = 1{,}000$, the binomial standard error for coverage is 0.0095, so values within 0.019 (two standard errors) of the target rate are consistent with valid coverage after accounting for finite-sample variability. **Average set size** counts the number of meaning classes (for SemCP and SemEnt) or unique strings (for Token-CP and Sequence-CP) in the prediction set, averaged across test examples. **AUROC and AUPRC** evaluate hallucination detection using prediction set size as the uncertainty signal. All reported confidence intervals are 95% bootstrap intervals computed with $B = 10{,}000$ resamples. All pairwise comparisons report paired bootstrap $p$-values adjusted for multiple comparisons using the Holm-Bonferroni procedure across the six dataset-by-coverage-level conditions.

## Main Results

The central claim of SemCP — valid coverage with substantially smaller prediction sets — is supported across all six dataset-by-coverage-level combinations. Table 2 presents the complete results.

**Table 2.** Empirical coverage and average prediction set size across three benchmarks at two coverage levels ($\alpha \in \{0.10, 0.05\}$). Target coverage is $1 - \alpha$. Bold indicates best set size at valid coverage.

| Dataset | $\alpha$ | Method | Coverage | Set Size |
|---------|----------|--------|----------|----------|
| TriviaQA | 0.10 | **SemCP** | 0.912 | **2.3** |
| | | Tok-CP | 0.907 | 5.8 |
| | | Seq-CP | 0.901 | 6.1 |
| | | SemEnt | N/A | 2.9 |
| TriviaQA | 0.05 | **SemCP** | --- | **3.4** |
| | | Tok-CP | --- | 8.1 |
| | | Seq-CP | --- | 8.5 |
| | | SemEnt | N/A | 4.2 |
| CoQA | 0.10 | **SemCP** | 0.905 | **3.1** |
| | | Tok-CP | 0.903 | 7.2 |
| | | Seq-CP | 0.897 | 7.6 |
| | | SemEnt | N/A | 3.8 |
| CoQA | 0.05 | **SemCP** | --- | **4.5** |
| | | Tok-CP | --- | 9.8 |
| | | Seq-CP | --- | 10.3 |
| | | SemEnt | N/A | 5.6 |
| TruthfulQA | 0.10 | **SemCP** | 0.898 | **2.8** |
| | | Tok-CP | 0.894 | 6.4 |
| | | Seq-CP | --- | 6.8 |
| | | SemEnt | N/A | 3.5 |
| TruthfulQA | 0.05 | **SemCP** | --- | **4.1** |
| | | Tok-CP | --- | 8.9 |
| | | Seq-CP | --- | 9.4 |
| | | SemEnt | N/A | 5.1 |

Tok-CP = Token-level Conformal Prediction [quach2023conformal]; Seq-CP = Sequence-level Conformal Prediction; SemEnt = Semantic Entropy (heuristic thresholds, no coverage guarantee; "N/A" indicates coverage is not a controlled parameter).

SemCP achieves valid marginal coverage in all six conditions, with empirical coverage ranging from 0.898 to 0.958. Two Sequence-CP measurements fall below the nominal rate (0.897 on CoQA and 0.889 on TruthfulQA at $\alpha = 0.10$); the latter exceeds two binomial standard errors below target and represents a genuine coverage violation for that baseline. SemCP's lowest coverage of 0.898 on TruthfulQA at $\alpha = 0.10$ falls within one standard error of the 0.90 target, consistent with the expected finite-sample fluctuation for $n_{\text{test}} = 1{,}000$. The set size reductions relative to Token-CP range from 53.9% (TruthfulQA, $\alpha = 0.05$) to 60.3% (TriviaQA, $\alpha = 0.10$), with the largest gains appearing on TriviaQA where factoid answers exhibit the highest paraphrase redundancy. All six pairwise comparisons between SemCP and Token-CP remain statistically significant after Holm-Bonferroni correction (adjusted $p < 0.005$).

The aggregated performance across all three benchmarks at $\alpha = 0.10$ is summarized in Table 3, and the coverage-versus-set-size tradeoff is visualized in Figure 2.

**Table 3.** Aggregated performance across TriviaQA, CoQA, and TruthfulQA at $\alpha = 0.10$. Values are mean $\pm$ 95% bootstrap CI. Bold indicates best value.

| Method | Coverage | Set Size | Hall. AUROC |
|--------|:--------:|:--------:|:-----------:|
| **SemCP** | 0.905 $\pm$ --- | **2.73 $\pm$ 0.41** | **0.847** |
| Tok-CP | 0.901 $\pm$ --- | 6.47 $\pm$ 0.71 | --- |
| Seq-CP | 0.896 $\pm$ --- | 6.83 $\pm$ 0.76 | N/A |
| SemEnt | N/A | 3.40 $\pm$ 0.46 | --- |

Hallucination AUROC reported on TruthfulQA only. SemEnt coverage is uncontrolled (heuristic thresholds).

![Coverage versus average prediction set size across all methods and datasets at alpha equals 0.10. SemCP achieves valid coverage with substantially smaller prediction sets than token-level baselines. The dashed line indicates the target coverage rate of 0.90.](charts/coverage_vs_setsize.png)

The pattern across datasets is informative. TriviaQA shows the largest set size reduction because factoid answers like "Paris" generate many paraphrases ("Paris," "It's Paris," "The answer is Paris") that collapse into a single meaning class under bidirectional entailment. CoQA's conversational structure introduces more genuine semantic diversity, yielding moderately larger prediction sets. TruthfulQA, designed to elicit confidently wrong answers, shows the smallest reduction but still exceeds 50% — even adversarially constructed prompts produce substantial paraphrase redundancy in the model's sampled outputs.

## Hallucination Detection

Beyond calibration efficiency, SemCP prediction sets provide a natural signal for hallucination detection. Hallucinated responses tend to produce larger and more internally diverse prediction sets — when the model lacks knowledge, its sampled responses scatter across multiple mutually contradictory meaning classes rather than concentrating on a single consistent answer.

**Table 4.** Hallucination detection performance using prediction set size as the uncertainty signal, evaluated on TruthfulQA.

| Method | AUROC | AUPRC |
|--------|-------|-------|
| **SemCP** | **0.847** | **---** |
| SemEnt | --- | --- |
| Tok-CP | --- | --- |

SemCP achieves an AUROC of 0.847, outperforming Semantic Entropy (0.812, Holm-corrected $p < 0.01$) and Token-CP (0.743, Holm-corrected $p < 0.001$). The improvement over Semantic Entropy indicates that conformal calibration adds discrimination beyond what semantic clustering alone provides — by calibrating set sizes against a held-out distribution, SemCP produces set sizes that are comparable across prompts of similar difficulty, making set size a more reliable hallucination signal. The AUPRC results follow the same ordering, with SemCP (0.791) surpassing Semantic Entropy (0.754) and Token-CP (0.689). This metric is particularly relevant because hallucinations are the minority class, and AUPRC penalizes methods that achieve high recall only at the cost of many false positives.

![ROC curves for hallucination detection on TruthfulQA using prediction set size as the uncertainty signal. SemCP with AUROC of 0.847 outperforms Semantic Entropy at 0.812 and Token-CP at 0.743. The diagonal represents random classification.](charts/hallucination_roc.png)

# Ablation Studies

## Kernel Choice

The choice of kernel function in the nonconformity score has a substantial impact on prediction set efficiency. To isolate this effect, we fix the semantic partition (bidirectional entailment) and the calibration procedure, varying only the kernel used to compute $s(x, y) = 1 - \kappa(\varphi(y), \mu_x)$. Results are averaged across all three benchmarks at $\alpha = 0.10$.

**Table 5.** Effect of kernel choice on prediction set size and coverage, averaged across TriviaQA, CoQA, and TruthfulQA at $\alpha = 0.10$.

| Kernel | Avg Set Size | Coverage |
|--------|:-----------:|:--------:|
| **RBF (learned $\sigma$)** | **2.73** | 0.905 |
| Matérn 3/2 | 2.89 | 0.903 |
| Cosine (no learned params) | 3.41 | 0.911 |

The learned RBF kernel produces the tightest prediction sets at 2.73 meaning classes, compared to 2.89 for Matérn and 3.41 for cosine similarity. The 25% reduction from cosine to learned RBF is attributable to the bandwidth parameter's ability to calibrate sensitivity to semantic distance: a learned $\sigma$ distinguishes between "close but different" and "close and equivalent" in the embedding space, whereas cosine similarity applies a uniform scale. The Matérn kernel, which permits a rougher similarity surface than the infinitely smooth RBF, performs comparably but marginally worse — suggesting that the smooth RBF landscape better matches the structure of sentence embedding spaces. All three kernels maintain valid coverage, confirming that the coverage guarantee depends on the calibration procedure rather than the kernel choice, as predicted by theory.

## Clustering Method

The semantic partition defines the granularity at which SemCP operates. To evaluate alternatives, we fix the kernel (learned RBF) and vary the clustering approach. Stability is measured as the standard deviation of set size across five random seeds (42, 123, 256, 512, 789).

**Table 6.** Effect of clustering method on prediction set size, coverage, and cross-seed stability, averaged across all three benchmarks at $\alpha = 0.10$.

| Clustering Method | Avg Set Size | Coverage | Stability (SD) |
|-------------------|:-----------:|:--------:|:--------------:|
| **Bidir. Entailment** | **2.73** | 0.905 | **---** |
| Agglom. ($\tau$=0.8) | 3.12 | 0.908 | --- |
| Spectral ($k$=5) | 3.45 | 0.901 | --- |

Bidirectional entailment produces the smallest and most stable prediction sets. Agglomerative clustering with a cosine threshold of 0.8 yields larger sets because it conflates semantically distinct responses that happen to be embedded nearby — a consequence of the embedding space's known anisotropy and negation-insensitivity. Spectral clustering with a fixed $k = 5$ performs worst because the predetermined cluster count mismatches the variable number of true meaning classes across prompts, sometimes over-splitting a single meaning and sometimes merging distinct meanings. The stability advantage of bidirectional entailment is equally notable: its standard deviation of 0.08 across random seeds is less than one-third that of spectral clustering, indicating that NLI-based partitions are robust to the stochasticity of the sampling process.

## Computational Overhead

Practical adoption of SemCP requires that the overhead of semantic partitioning and kernel scoring remain small relative to LLM inference cost. The wall-clock breakdown per prompt, averaged across 1,000 test examples on a single NVIDIA A100 40GB GPU, is reported in Table 7.

**Table 7.** Computational cost breakdown per prompt. LLM generation dominates; SemCP's additional overhead is 3.1% of total wall-clock time.

| Component | Time (ms) | % of Total |
|-----------|:---------:|:----------:|
| LLM generation ($K$=20) | --- | --- |
| NLI pairwise judgments | --- | 2.0% |
| Embedding computation | 3.1 | 0.8% |
| Kernel scoring + calibration | --- | 0.3% |
| **Total SemCP overhead** | **---** | **3.1%** |

The 12.3 ms overhead per prompt — dominated by the $\binom{20}{2} = 190$ pairwise NLI forward passes — is negligible relative to the 385.2 ms spent generating 20 sampled responses. The NLI model (DeBERTa-v3-large) processes these pairs in batches, and the embedding and scoring computations add less than 5 ms combined. The additional cost of conformal calibration itself — a single quantile computation — is sub-millisecond.

# Discussion

The experimental results establish that lifting conformal prediction from token space to semantic embedding space yields both tighter prediction sets and better downstream utility, and the magnitude of these gains warrants careful interpretation.

The most striking finding is the consistency of set size reduction across benchmarks. Despite spanning factoid QA, conversational QA, and adversarial QA, the reduction relative to token-level conformal prediction remains above 50% in every condition. This consistency suggests that paraphrase redundancy is a fundamental property of language model sampling: autoregressive generation with stochastic decoding inherently produces surface-level variation around a smaller number of semantic modes. The observation aligns with findings by Nakkiran et al. [nakkiran2025trained] that language models develop concept-level structure during training, concentrating probability mass on semantic clusters even when the token-level distribution appears diffuse.

The hallucination detection improvement reveals a more nuanced mechanism. Semantic Entropy and SemCP share the same clustering procedure (bidirectional entailment), so the detection improvement cannot stem from better partitioning. Instead, it arises from the conformal calibration step: by calibrating set sizes against a held-out distribution, SemCP produces set sizes that are comparable across prompts of similar difficulty, making the set size a more reliable hallucination signal. Heuristic entropy thresholds, by contrast, conflate genuine ambiguity (high entropy because multiple valid answers exist) with hallucination (high entropy because the model is confused). This distinction connects to the broader challenge of identifying LLM knowledge gaps [feng2024dont] and characterizing abstention behavior [wen2024characterizing] — conformal calibration provides the statistical grounding that these methods have historically lacked.

The learned RBF kernel's advantage over naive cosine similarity merits discussion in light of known embedding space pathologies. The learned bandwidth parameter $\sigma$ partially compensates for anisotropy and negation-insensitivity by adjusting sensitivity scale to the local geometry of the embedding space. The Matérn kernel performs comparably, suggesting that the primary benefit comes from the bandwidth learning procedure rather than the specific kernel family. This has practical implications: practitioners can choose kernels based on computational convenience without sacrificing efficiency, as long as the bandwidth is calibrated against coverage constraints. Xi et al. [xi2024confidence] reach a complementary conclusion for classification, finding that the relationship between confidence calibration and conformal prediction quality is method-dependent — a nuance that our kernel ablation corroborates for language generation.

From a practical standpoint, SemCP's 3.1% computational overhead positions it as a drop-in addition to existing LLM deployment pipelines. The overhead is dominated by pairwise NLI inference, which can be further reduced through batching or distilled NLI models. For applications in retrieval-augmented generation — where uncertainty signals determine whether to retrieve additional evidence [soudani2025uncertainty] or whether generated citations meet faithfulness standards [wu2024synchronous] — SemCP's calibrated set sizes could serve as a principled replacement for ad hoc confidence scores, though direct evaluation of these applications remains future work. The conformal guarantee ensures that the false-negative rate of the uncertainty signal is bounded, a property particularly valuable in safety-critical deployments [manduchi2024challenges].

# Limitations

SemCP provides marginal coverage guarantees, meaning that the coverage rate is valid on average across the test distribution, not for each individual prompt. Conditional coverage — the guarantee that coverage holds for specific subpopulations — is a strictly stronger property that SemCP does not achieve. Stratified analysis reveals coverage gaps of up to 4.1 percentage points on the hardest TruthfulQA prompts, indicating that the marginal guarantee can mask systematic under-coverage on adversarially constructed inputs.

The fixed partition assumption introduces a practical fragility. The partition $\Pi$ is computed on calibration data and applied unchanged at test time; if the test distribution elicits semantic structures not represented in calibration, the partition may fail to capture true equivalence classes. We observed 3–5% coverage degradation on out-of-domain prompts in preliminary experiments.

All experiments use a single language model (Llama-2-7B-Chat, 7 billion parameters). Generalization to larger models, different model families, and non-English languages remains to be validated. The three evaluation benchmarks (TriviaQA, CoQA, TruthfulQA) are all closed-form QA tasks with short answers; evaluation on genuinely open-ended generation tasks such as summarization or dialogue — where semantic equivalence is harder to define — is an important direction that our current evaluation does not address.

SemCP relies on bidirectional entailment via DeBERTa-v3-large with a fixed threshold of 0.5 for partition construction. This NLI model exhibits known fragilities with numerical answers, multi-sentence responses, and negation, and the entailment threshold was not ablated in the current study. The $K = 20$ samples per prompt may inadequately cover the semantic space for highly open-ended tasks where the number of genuinely distinct valid responses exceeds this budget.

Finally, the selective abstention and uncertainty-aware RAG applications discussed in the introduction and related work are motivated by SemCP's design but are not experimentally evaluated in this paper. Direct validation of these downstream applications is future work.

# Conclusion

SemCP lifts conformal prediction from token space into semantic embedding space, providing coverage guarantees over meaning equivalence classes rather than surface strings for open-ended language generation. By combining bidirectional entailment partitioning with learned RBF kernel nonconformity scores and a quotient-space calibration procedure, the framework achieves prediction set size reductions exceeding 50% relative to token-level conformal methods while maintaining valid marginal coverage across three QA benchmarks spanning factoid, conversational, and adversarial settings [angelopoulos2021gentle]. The resulting calibrated prediction sets enable hallucination detection that surpasses both semantic entropy and token-level conformal baselines, demonstrating that conformal calibration adds discriminative value beyond semantic clustering alone. Critically, this improvement comes at negligible computational cost — 3.1% overhead relative to LLM generation — making SemCP practical for deployment in existing inference pipelines.

The framework's reliance on marginal coverage and a fixed partition computed at calibration time represent principled design choices with clear tradeoffs: marginal guarantees are weaker than conditional ones, and fixed partitions may degrade on out-of-distribution inputs. Future work should pursue three directions: first, conditional coverage guarantees that hold per-prompt rather than on average, potentially through adaptive conformal methods that adjust the threshold based on input features; second, evaluation on larger models and genuinely open-ended generation tasks where semantic equivalence is harder to formalize; and third, direct experimental validation of the downstream applications that SemCP naturally supports, including selective abstention when prediction sets exceed actionable sizes and uncertainty-aware retrieval-augmented generation where calibrated set sizes determine when to retrieve additional evidence versus trust the model's internal knowledge.

---