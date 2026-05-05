# Reproducibility Review — SemCP: Coverage Guarantees Over Meanings, Not Strings

**Reviewer:** The Reproducibility Archeologist
**Date:** 2026-05-01
**Paper:** SemCP: Coverage Guarantees Over Meanings, Not Strings (NeurIPS 2026)

---

## Summary

This paper proposes SemCP, a conformal prediction framework operating in semantic embedding space. The theoretical contribution (Theorem 1, conditional coverage guarantee) is sound and well-presented. However, the empirical evaluation is **not yet executed** — all numbers in the main results table are TODO_NUM placeholders, and key figures contain placeholder data. This makes a reproducibility assessment impossible at the current state.

**Reproducibility Score: 15/100 (Cannot Reproduce)**

---

## Strengths

1. **Theorem 1 is precisely stated.** The conditional coverage guarantee $1 - \alpha - 1/(|I|+1)$ is clearly formulated with explicit assumptions (exchangeability, fixed partition rule $\Pi$, admissibility event $A$). The proof sketch is coherent and the conditioning paradigm is correctly positioned relative to ConU/SAFER/LofreeCP. *(Section 4.4, Theorem 1)*

2. **Algorithm 1 pseudocode is detailed and complete.** The calibration loop and prediction step are specified with enough precision that a competent implementor could reproduce the core SemCP logic without reference to the surrounding prose. *(Algorithm 1)*

3. **Hyperparameter table is mostly complete.** Table 1 reports LLM (Qwen2.5-7B-Instruct), temperature (1.0), nucleus $p$ (0.95), $K=10$, max tokens (64), NLI model (DeBERTa-v2-xlarge-MNLI), embedding model (all-MiniLM-L6-v2), bandwidth grid, cal/test split (50/50), seeds (0,1,2), bootstrap iterations (1000), and hardware (RTX 6000 Ada 48GB). *(Table 1)*

4. **Notation summary table aids implementation.** Section 3's notation table clarifies the distinction between $s(x,y)$ (string-level) and $\tilde{s}(x,[y]_s)$ (lifted), which is the most technically subtle part of the method. *(Section 3)*

5. **Ablation variants are explicitly named.** SemCP-NoM2O, SemCP-Euclidean, SemCP-Adaptive, and Naive Semantic are identified as ablation targets with specific metric comparisons in mind (e.g., learned RBF 13.35 vs Euclidean 18.57 on SQuAD). *(Section 6)*

---

## Weaknesses

### W1: All empirical results are TODO_NUM placeholders
- **Issue:** Table 1 (main results) contains only `TODO_NUM` entries. The abstract claims "TODO_NUM\% smaller active set sizes." The ablation discussion cites specific numbers (13.35, 18.57, 14.19, 18.83 on SQuAD) as if they were real, but the table they reference has no data.
- **Where:** Abstract, Table 1, Section 6 (Ablation Studies), Section 5.3 (Figure 3 references)
- **Severity:** 5/5 — This is a **critical failure**. The primary empirical contribution cannot be evaluated.
- **Resolution:** Run the experiments and replace all placeholders with real numbers. Do not submit a paper with unfilled experimental results.

### W2: Figure 3 caption-model mismatch
- **Issue:** The Figure 3 caption states "Coverage is near-zero for all methods due to GPT-2's limited QA capability." But the experiments section (Section 5.1) explicitly states "Qwen2.5-7B-Instruct" is used. This is a fundamental discrepancy: GPT-2 achieves 2-3% correct-answer rate, Qwen2.5-7B-Instruct does not.
- **Where:** Figure 3 caption (line 6 of caption), Section 5.1 (Generator description), Discussion (para 2: "When GPT-2 generates correct answers for only 2-3%")
- **Severity:** 4/5 — This suggests the figure and/or text were copied from a different experiment and not updated. The entire analysis section's interpretation of "near-zero coverage" may be wrong for the actual model used.
- **Resolution:** Regenerate Figure 3 with Qwen2.5-7B-Instruct results. Update the caption and Discussion to remove GPT-2 references.

### W3: TODO_HOURS placeholder for compute time
- **Issue:** Table 1's hardware row says "Total wall clock: TODO_HOURS hours for the full matrix." This is an essential reproducibility input for compute-budget planning.
- **Where:** Table 1 (footnote), Section 5.1 (last sentence)
- **Severity:** 2/5 — Minor but should be filled before submission.
- **Resolution:** Record wall-clock time during the experiment run and fill in the value.

### W4: Code not released — "will be released upon publication"
- **Issue:** The NeurIPS checklist item 5 (Open access to data and code) is answered "[Yes]" but the paper states "Code and experiment scripts will be released upon publication." "Upon publication" is not an open-access commitment; it is a delayed-release promise that routinely fails. The paper also says "Code to be released" in the Conclusion.
- **Where:** NeurIPS Checklist (item 5), Abstract ("TODO_NUM%"), Conclusion (last sentence), Section 5.1 (hardware)
- **Severity:** 4/5 — Without code, independent reproduction is impossible. The paper claims reproducibility in the checklist while simultaneously deferring code release.
- **Resolution:** Release code at submission (or at minimum, as a confidential artifact for reviewers). Use a permanent URL (GitHub with commit hash) rather than "upon publication."

### W5: NLI model version/commit hash unspecified
- **Issue:** The paper identifies the NLI model as "DeBERTa-v2-xlarge-MNLI" but provides no version pin, commit hash, or model card link. DeBERTa-v2-xlarge-MNLI has multiple releases (original, v3, v3.5) with different performance characteristics. The bidirectional entailment binarization threshold of 0.5 may have different False Positive/FN rates across versions.
- **Where:** Section 4.1, Section 5.1 (Semantic partition), Table 1
- **Severity:** 3/5 — Meaning equivalence classes depend directly on the NLI model's behavior. Without an exact model reference, the partition is not reproducible.
- **Resolution:** Pin to a specific model version (e.g., HuggingFace model ID with version tag) and document the entailment threshold. Ideally, release the NLI outputs or the partition files.

### W6: Embedding model version/commit hash unspecified
- **Issue:** "all-MiniLM-L6-v2" is identified but no version pin. Sentence transformer models have version history (v1 vs v2 vs v6). The cosine-similarity threshold of 0.7 mentioned in Section 4.1 is calibrated to a specific embedding space; changing the model changes the threshold's meaning.
- **Where:** Section 4.1 (cosine-similarity threshold 0.7), Table 1 (Embedding model), Algorithm 1
- **Severity:** 3/5 — The kernel scoring depends on the embedding geometry. Reproducibility requires exact model pinning.
- **Resolution:** Pin to specific HuggingFace model ID with version tag (e.g., `sentence-transformers/all-MiniLM-L6-v2@sha256:...`).

### W7: 33% set-size reduction claim appears without supporting evidence
- **Issue:** The Discussion (Section 7) states "33\% reduction in prediction set size on SQuAD (13.35 vs. 19.89 for Token-CP)" as a finding, but the referenced Table 1 contains no numbers. This claim is cited in the abstract and contributions but is unsubstantiated.
- **Where:** Abstract, Section 7 (para 1), Introduction (Contribution 2)
- **Severity:** 5/5 — This is the paper's primary empirical headline. Without real numbers, the claim is fictional.
- **Resolution:** Run the experiment and report the actual numbers.

### W8: GPT-2 vs Qwen2.5-7B-Instruct confusion in Discussion
- **Issue:** The Discussion section contains two paragraphs arguing about GPT-2's limitations (2-3% correct rate, "coverage is near-zero for all methods due to GPT-2's limited QA capability"). But the experiments use Qwen2.5-7B-Instruct, which should have substantially higher correctness. The analysis may be describing the wrong model.
- **Where:** Section 7 (Discussion), Figure 3 caption
- **Severity:** 4/5 — The entire interpretation of results (why coverage is "near-zero") is tied to a model not actually used. The 33% reduction claim requires meaningful coverage to be meaningful, but the analysis claims coverage is near-zero — contradiction.
- **Resolution:** Rewrite Discussion to reflect actual Qwen2.5-7B-Instruct results. If coverage is genuinely near-zero, explain why (admissibility rate?). If coverage is reasonable, remove the GPT-2 framing.

### W9: Constrained bandwidth optimization description is vague
- **Issue:** Section 4.2 describes grid search over sigma on a "held-out 20% subset of the training split." The paper later says "held-out 50\% calibration--training split" in Section 5.1. It is unclear: (a) what the training split is relative to the 50/50 cal/test split, (b) whether the 20% is nested inside the 50% training portion, and (c) how many examples are used for bandwidth optimization vs. conformal calibration.
- **Where:** Section 4.2, Section 5.1
- **Severity:** 3/5 — The bandwidth optimization is central to SemCP's efficiency claims. If it uses data also used for calibration, the coverage guarantee may be compromised.
- **Resolution:** Specify: (a) exact data splits (training/val/cal/test with sizes), (b) that the bandwidth optimization uses disjoint data from calibration, (c) confirm this does not violate the split-conformal assumptions.

### W10: "Naive Semantic" ablation baseline is defined by results, not method
- **Issue:** The ablation mentions "Naive Semantic (18.83 on SQuAD)" but never defines what Naive Semantic is. The name suggests clustering without kernel scoring, but the paper does not describe it in the Ablation Studies section.
- **Where:** Section 6, Discussion
- **Severity:** 2/5 — A reader cannot reproduce an ablation they cannot define.
- **Resolution:** Define Naive Semantic explicitly (clustering with what score? frequency-based? just returning the most common string?).

---

## Per-Rubric-Dimension Scores

| Dimension | Score (1-10) | Calibration Anchor | Notes |
|-----------|-------------|-------------------|-------|
| **Originality / Novelty** | 7 | Substantial conceptual advance | Quotient-space CP with kernel scores is novel; clearly positioned vs. ConU/SAFER |
| **Soundness** | 5 | Methodology has serious gaps | Theory is sound; but empirical results are TODO_NUM placeholders — cannot verify main claims |
| **Significance** | 7 | Important within subfield | CP over meanings addresses a real gap; if results hold, useful contribution |
| **Clarity** | 7 | Clear, well-organized | Theory sections are clear; figure-caption mismatch is a clarity flaw |
| **Reproducibility** | 2 | Cannot be reproduced from what's provided | Code not released; all main results are TODO_NUM; model versions unspecified |
| **Contextualization** | 7 | Strong coverage; correctly positioned | Well-positioned vs. ConU, SAFER, LofreeCP, TECP |
| **Ethical / Broader Impact** | 6 | Boilerplate | Standard broader impact statement; not specific to the method |

**Weighted Average: 5.7 (Borderline — driven down by Soundness and Reproducibility both at 2/5 on the 1-10 scale, equivalent to ~40/100 in raw reproducibility terms)**

*Note: Soundness 5/10 here reflects "methodology has serious gaps" — primarily that the empirical validation is absent. The theoretical methodology is strong.*

---

## Pointed Questions for Authors

1. **All Table 1 values are `TODO_NUM`. When will the experiments be run, and will you resubmit with actual numbers?** This is not a rhetorical question — a paper with placeholder results cannot be reviewed.

2. **Figure 3 caption says "GPT-2" but Section 5.1 says "Qwen2.5-7B-Instruct". Which model produced the data in Figure 3?** Please reconcile this discrepancy explicitly.

3. **You state in the NeurIPS checklist that code is released ("Yes"), but the paper says "Code and experiment scripts will be released upon publication." Which is accurate?** Please release code at submission, not upon acceptance.

4. **What is the exact HuggingFace model ID and version for DeBERTa-v2-xlarge-MNLI and all-MiniLM-L6-v2?** Without pinning, the NLI partition is not reproducible.

5. **The Discussion says "coverage is near-zero for all methods due to GPT-2's limited QA capability" and "GPT-2 generates correct answers for only 2-3% of questions" — but you use Qwen2.5-7B-Instruct. What is the actual correctness rate for Qwen2.5-7B-Instruct on TriviaQA and SQuAD?** If it is much higher than 2-3%, the near-zero coverage analysis is irrelevant to your experiments.

6. **Your bandwidth optimization is described as using a "held-out 20% subset of the training split" while calibration uses a "50/50 cal/test split." Please clarify the exact data flow:** Does the 20% overlap with calibration data? If so, how does this preserve the coverage guarantee?

7. **Section 4.1 mentions "cosine-similarity thresholding at 0.7" but Table 1 and the main text describe bidirectional NLI binarization at 0.5.** Which is used for the semantic partition in the experiments — 0.7 (embedding cosine) or 0.5 (NLI probability)?

8. **The abstract says "TODO_NUM\% smaller" but Discussion says "33\%." Which is the target?** Please report the actual measured reduction.

9. **What is "Naive Semantic" exactly?** Define it in the paper so it can be reproduced.

10. **SAFER's abstention threshold is set at 0.10. Was this tuned on the same held-out data as the bandwidth parameter?** If so, this is a multiple-comparison concern that should be acknowledged.

---

## Falsifiability Test

**The single piece of evidence that would most change my assessment:**

Release the code with all experiment scripts, populate Table 1 with actual numbers from runs on Qwen2.5-7B-Instruct, and ensure the 33% set-size reduction claim is empirically supported. If SemCP achieves 33% set-size reduction at conditional coverage ~0.89 on SQuAD with Qwen2.5-7B-Instruct — and the code actually reproduces this — I would revise my Reproducibility score from 2 to 8 and my overall recommendation to **Accept**.

**Specific falsifiability conditions:**
- If the code is released with a commit hash and the 33% figure is verified by an independent researcher: Accept
- If the code is released but the 33% figure cannot be reproduced within 5% relative error: Reject
- If code is never released but all TODO_NUM values are filled with real numbers that an independent researcher can verify by re-implementing: Borderline
- If GPT-2 analysis remains in the paper despite Qwen2.5-7B-Instruct being the actual model: Reject (irreconcilable factual inconsistency)

---

## Confidence

**4/5** — I am highly confident in my assessment of the reproducibility gaps because they are visible in the paper text itself (TODO_NUM placeholders, figure-caption model mismatch, "upon publication" code release). I have moderate uncertainty about the theoretical contributions, which appear sound but cannot be fully assessed without the empirical validation the paper is missing.

---

## Decision

**Borderline / Reject (revise and resubmit)**

The paper's theoretical contribution is solid and the framework is interesting. However:
1. **All empirical results are TODO_NUM placeholders** — this alone is grounds for rejection at most venues
2. **Figure 3 caption describes GPT-2; experiments use Qwen2.5-7B-Instruct** — factual inconsistency that contaminates the analysis
3. **Code is not released** — "upon publication" is not an acceptable commitment for reproducibility

**Recommendation:** Withhold from submission until experiments are run, TODO_NUM values are replaced, code is released (not promised for later), and the GPT-2/Qwen discrepancy is resolved in the text. The paper has strong fundamentals but is not yet a submittable artifact.

---

*— The Reproducibility Archeologist*