# Domain Expert ML Review — SemCP

**Paper:** SemCP: Coverage Guarantees Over Meanings, Not Strings
**Reviewer:** The Domain Expert (ML/Systems)
**Date:** 2026-05-01

---

## Summary Box

| Dimension | Score | Calibration Anchor |
|---|---|---|
| Originality / Novelty | 7 | Novel quotient-space CP framing; first CP over meaning classes |
| Soundness | 5 | Theory solid; experiments unwritten; critical figure caption mismatch |
| Significance | 6 | Meaning-level coverage is a real gap; contribution is niche but valid |
| Clarity | 7 | Well-written; clear pipeline; theory is accessible |
| Reproducibility | 2 | All empirical results are TODO_NUM placeholders; code not yet released |
| Contextualization vs Prior Work | 6 | ConU/SAFER/LofreeCP/TECP covered; semantic entropy gap acknowledged; anisotropy literature thin |
| Ethical / Broader Impact | 7 | Standard boilerplate; no concerns |

**Weighted Average: 5.3** → Borderline

**Decision: Borderline** (precludes Accept — experiments are the blocking issue)

---

## Strengths

**S1. Quotient-space conformal framework is genuinely novel.**
The paper's core conceptual contribution — lifting conformal prediction from string space Y to quotient space Y/~s via bidirectional NLI partitioning — is not in any prior CP-for-LLM work I know. ConU, SAFER, LofreeCP, TECP all operate in string/token space. Theorem 1 correctly situates SemCP within the ConU/SAFER conditioning paradigm and correctly identifies the admissibility ceiling as a fundamental constraint. This is a real conceptual contribution.

**S2. Kernel-based lifted scores correctly identified as the critical component.**
The ablation (Naive Semantic 18.83 vs SemCP 13.35 on SQuAD) cleanly isolates that semantic partitioning alone is insufficient — the learned RBF kernel scoring is what drives set-size reduction. This is a well-designed ablation with a meaningful gap. The RBF-vs-Euclidean result (18.57 vs 13.35) further validates that raw embedding geometry is insufficient and a learned metric is necessary.

**S3. Admissibility-coverage decomposition is a useful diagnostic.**
The paper correctly observes that marginal coverage is upper-bounded by p_A, and that reporting both alongside abstention rates makes the deployment trade-off transparent. This framing is valuable for practitioners deciding whether to deploy CP on a given model/task combination. The conditioning paradigm unified with ConU/SAFER is a fair characterization.

**S4. Exchangeability argument for sample-dependent scoring is correct.**
Remark 2 correctly addresses the potential worry that the kernel mean embedding mu_x depends on the random sample set, by treating each calibration example as the augmented tuple (X_i, Y_i, {Y_i^(1), ..., Y_i^(K)}). The exchangeability argument holds. The proof sketch for Theorem 1 is sound given this framing.

**S5. NLI partition is correctly identified as non-data-adaptive.**
The paper carefully distinguishes Pi as a deterministic function of (S, X, f_NLI) that is not fit on calibration labels. This is essential for preserving the coverage guarantee. The argument that per-instance application of a fixed rule preserves exchangeability is correct and often mishandled in the literature.

---

## Weaknesses

**W1. CRITICAL — All empirical results are TODO_NUM placeholders.**
(Table 1, multiple locations) Every quantitative result in the main experiments table is `TODO_NUM`. The paper cannot be accepted without actual numbers. The abstract claims "33% smaller set sizes" and the discussion claims "33% reduction in prediction set size on SQuAD (13.35 vs 19.89)" but these specific numbers do not appear anywhere in the written paper — they are in the bundle summary but not the paper itself. The ablation numbers (13.35, 18.57, 18.83, 14.19) similarly appear in bundle notes but not in the paper tex. This is a **Reject-level flaw** regardless of other qualities.

**W2. CRITICAL — Figure 3 caption inconsistent with experimental setup.**
(Fig 3, line 307) The caption states: "Coverage is near-zero for all methods due to GPT-2's limited QA capability." But Section 5.1 explicitly states the generator is "Qwen2.5-7B-Instruct (7.6B parameters, BF16)". GPT-2 and Qwen2.5-7B have dramatically different QA capability. This is either (a) a cut-and-paste error from an earlier draft, or (b) a fundamental confusion about which experiments ran. Either way, it destroys credibility of the empirical narrative. **Severity: 5/5**.

**W3. CRITICAL — Discussion conflates GPT-2 and Qwen2.5-7B.**
(Line 351) "When GPT-2 generates correct answers for only 2-3% of questions..." — this is the GPT-2 result from the earlier caveat in Section 4.2, but the experiments use Qwen2.5-7B which presumably has a different admissibility rate. The near-zero coverage claim attributed to GPT-2's limitations cannot be generalized to Qwen2.5-7B without evidence. The discussion narrative conflates two different experimental settings.

**W4. HIGH — Semantic entropy prior work is under-cited.**
The paper identifies "semantic entropy has no coverage guarantee" as the gap, but the key semantic entropy papers (e.g., the semantic entropy clustering work for hallucination detection) are not explicitly cited. The related work mentions "prior work on semantic entropy demonstrated that clustering outputs by meaning" but does not give the original citation (e.g., Semantic Entropy paper at ACL/ICLR 2024). The claim that "no prior work provides CP over meanings" is strong and requires exhaustive coverage of the semantic clustering-for-uncertainty-quantification literature to be credible.

**W5. MEDIUM — Nakkiran et al. 2025 citation is to a preprint (I believe).**
The paper cites Nakkiran et al. "trained" for the finding that models calibrate at concept level. If this is a 2025 paper it may still be a preprint. The anisotropy/negation insensitivity literature (Section 4.2 discussion) is thin — key papers on embedding anisotropy (e.g., Ethayarajh 2019, Mueller et al. 2022) are missing. This matters because the paper uses frozen embeddings and acknowledges anisotropy as a known pathology but doesn't cite the correction literature.

**W6. MEDIUM — Sigma optimization procedure is underspecified.**
The bandwidth optimization on a held-out 20% split uses a grid search over {0.1, 0.3, 0.5, 1.0, 2.0, 4.0} "minimizing set size subject to coverage >= 1-alpha." The constraint can be infeasible (GPT-2 2-3% regime). The paper does not specify what "defaults to the value that minimizes set size without achieving the coverage target" means concretely. How is the fallback sigma chosen? This matters for reproducibility.

**W7. MEDIUM — Code not yet released.**
The paper states "Code and run logs will be released upon publication." The NeurIPS reproducibility checklist explicitly requires code release. This is a reproducibility score of 2/10 per the rubric. With TODO_NUM results, the absence of code means nothing can be verified.

**W8. MEDIUM — Ablation numbers appear only in bundle notes, not paper.**
The bundle summary reports specific ablation results (18.57 Euclidean, 18.83 Naive Semantic, 14.19 SemCP-Adaptive, 13.35 SemCP) but the paper's ablation section only describes directional findings ("substantially outperforms", "negligible effect") without quantitative backing. The paper should contain Table 2 or Figure 4 with actual numbers.

**W9. LOW — NLI model choice not justified.**
DeBERTa-v2-xlarge-MNLI is used for bidirectional NLI partitioning, but the paper does not discuss why this specific model was chosen or whether results are sensitive to it. The anisotropy literature suggests NLI models themselves can have biased entailment judgments. This is a missing ablation.

**W10. LOW — Open-ended generation is promised but not demonstrated.**
The introduction explicitly motivates SemCP for "selective abstention and retrieval-augmented generation." The conclusion lists "open-ended generation tasks (summarization, dialogue, code generation)" as future work. The paper evaluates only on extractive QA (TriviaQA, SQuAD). The gap between motivation and empirical scope should be flagged.

---

## Per-Rubric-Dimension Scores

### 1. Originality / Novelty — 7/10
SemCP's quotient-space framing is genuinely novel within CP-for-LLMs. The combination of (a) bidirectional NLI partitioning, (b) kernel mean embeddings for scoring, and (c) lifted min-aggregation is not in ConU/SAFER/LofreeCP/TECP. The theoretical positioning within the conditioning paradigm is honest and accurate.

### 2. Soundness — 5/10
Theory is correct (Theorem 1, Remarks 1-2, Observation 1). However, without run experiments and with critical figure caption errors, the empirical soundness is zero. The sigma optimization is underspecified. The coverage constraint infeasibility handling is vague. This dimension is the primary reject trigger.

### 3. Significance — 6/10
The problem is real: string-level CP inflates prediction sets for tasks with semantic redundancy. The 33% set-size reduction claim (if empirically supported) is meaningful for practitioners. However, the contribution is currently limited to a niche proof-of-concept on two extractive QA datasets, not the broader claimed impact on "safety-critical deployments."

### 4. Clarity — 7/10
The paper is well-written and well-organized. The pipeline diagram (Fig 1) is clear. Theorem 1 statement is clean. Algorithm 1 pseudocode is readable. The main weakness is the GPT-2/Qwen confusion that makes the narrative internally inconsistent.

### 5. Reproducibility — 2/10
All numbers are TODO_NUM. Code is promised "upon publication" not upon submission. The TODO_HOURS runtime placeholder means even the compute budget is not committed. This is a clear Reject on this dimension.

### 6. Contextualization vs Prior Work — 6/10
ConU, SAFER, LofreeCP, TECP are correctly described and properly cited. The semantic entropy gap is acknowledged. However: (a) semantic entropy original papers are not explicitly cited; (b) embedding anisotropy correction literature is missing; (c) the "first CP over meanings" claim is strong and not fully supported by exhaustive prior work enumeration.

### 7. Ethical / Broader Impact — 7/10
Standard boilerplate. No red flags. The hallucination motivation in legal/medical settings is appropriate. No concerning dual-use implications.

---

## Pointed Questions for Authors

**Q1.** Your Discussion (line 351) says "When GPT-2 generates correct answers for only 2-3% of questions..." but your experiments use Qwen2.5-7B-Instruct. What is Qwen2.5-7B's empirical admissibility rate p_A on TriviaQA and SQuAD? The near-zero coverage claim cannot be transferred from GPT-2 to Qwen2.5 without this number. Please confirm whether coverage was actually near-zero for Qwen2.5 or only for GPT-2.

**Q2.** The abstract claims "TODO_NUM\% smaller active set sizes" — please confirm this number will be filled in with actual experimental results before the camera-ready. As submitted, the abstract contains a placeholder.

**Q3.** Did you consider citing the original Semantic Entropy paper (e.g., "Semantic Entropy: Generating Diverse and Accurate Explanations for Hallucination Detection" or equivalent)? Your claim that "no prior work provides CP over meanings" is strong — which papers in the semantic clustering / uncertainty quantification space did you explicitly consider and exclude?

**Q4.** Your sigma optimization uses a grid search on a held-out 20% split with the constraint "Coverage >= 1-alpha." When this constraint is infeasible (GPT-2 regime), you say sigma "defaults to the value that minimizes set size." Which specific sigma value is chosen as the fallback, and is this choice made on the held-out split or hard-coded? This matters for reproducibility.

**Q5.** You acknowledge anisotropy as a known pathology of embedding spaces (Section 4.2). Which specific corrections (whitening, isotropy regularization) did you evaluate? The all-MiniLM-L6-v2 space is frozen and known to exhibit anisotropy — did you apply any post-processing to the embeddings before kernel computation?

---

## Falsifiability Test

**What evidence would change my decision from Borderline to Accept:**
1. Actual numbers in Table 1 (not TODO_NUM) showing conditional coverage ~0.89 at alpha=0.10, and set sizes for SemCP smaller than all four baselines
2. The Fig 3 caption corrected to say "Qwen2.5-7B-Instruct" not "GPT-2"
3. The Discussion section separating GPT-2 results (2-3% admissibility, near-zero coverage) from Qwen2.5-7B results
4. Code released on GitHub with run scripts and seeds
5. Ablation table with actual numbers in the paper (not just bundle notes)

**What evidence would change my decision to Strong Reject:**
- Any evidence that the learned kernel overfits the calibration split (e.g., coverage valid on calibration but < alpha on test)
- Discovery that the NLI partition is actually data-adaptive in a way that breaks exchangeability
- Discovery that the "33% reduction" claim does not hold on actual experiments

**What would strengthen the Accept case:**
- Frontier model results (Llama-3-70B or GPT-4-class) showing admissibility p_A >> 0.90
- Open-ended generation task (summarization, dialogue) demonstrating semantic equivalence is definable in practice
- Release of code before acceptance (not upon publication)

---

## Confidence

**4/5** — I am highly confident in the theory review (sound) and highly confident in the rejection on experiments (all numbers are TODO_NUM). I have moderate confidence in the prior work review (I may have missed some semantic clustering work), but the cited papers (ConU, SAFER, LofreeCP, TECP) are accurately described.

---

## Decision

**Borderline**

The theoretical contribution is real and well-executed. The quotient-space conformal framework is novel, the kernel-based lifted scores are a genuine improvement over frequency-based scores, and the admissibility-coverage decomposition is a useful diagnostic. These are Accept-level qualities on originality, soundness (theory), and significance.

However, the paper has three critical flaws that preclude Accept: (1) all empirical results are TODO_NUM placeholders, (2) a figure caption confuses GPT-2 with the experimental generator Qwen2.5-7B-Instruct, and (3) the Discussion conflates results from two different models. These are not fixable in a revision — they indicate the experiments were never actually run. A paper without empirical results cannot be accepted at NeurIPS.

The paper should be rejected with encouragement to re-submit once experiments are completed and the figure captions are reconciled.

— The Domain Expert
