# Big-Picture Editor Review: SemCP

**Paper:** SemCP: Coverage Guarantees Over Meanings, Not Strings
**Venue:** NeurIPS 2026
**Reviewer:** The Big-Picture Editor

---

## Summary One-Liner

A theoretically interesting but empirically hollow paper that poses a genuine gap (semantic conformal prediction) while failing to provide a single number from an actual experiment — making it impossible to assess whether the claimed 33% set-size reduction or near-zero coverage is real.

---

## 3-5 Strengths

1. **Theoretical Problem Identification (Section 1-2):** The paper correctly identifies a real and underappreciated gap: conformal prediction for LLMs operates over strings, but guarantees over strings are semantically vacuous when multiple surface forms express the same meaning. This is a legitimate problem worth solving. The conditioning-paradigm unification (Remark 1) is a clean diagnostic contribution.

2. **Quotient-Space Formalization (Section 3-4):** The formalization of the string-to-meaning mapping as a quotient map with a fixed partition rule and the proof that exchangeability is preserved (Remark 2) is correct and non-trivial. The lifted score construction via `min` aggregation is technically sound.

3. **RBF Kernel Insight (Ablation, Fig 4):** The finding that a learned RBF kernel (13.35 on SQuAD) substantially outperforms Euclidean distance (18.57) is a genuine empirical observation that could matter in practice. This is the one result in the paper that could survive contact with reality.

4. **Admissibility Decomposition (Remark 1, Section 5.3):** The explicit decomposition of marginal coverage into `p_A * coverage(admissible)` is genuinely useful for practitioners. Reporting both marginal and conditional coverage alongside admissibility rate should become standard practice.

5. **Complementary Positioning (Section 7, Discussion):** The paper correctly frames SemCP as orthogonal to ConU/SAFER/LofreeCP — semantic lifting vs. conditioning/abstention — and identifies the natural integration as future work. This intellectual honesty is commendable.

---

## 5-10 Weaknesses

### W1: ALL EXPERIMENTAL RESULTS ARE PLACEHOLDERS
- **Issue:** Table 1 contains exclusively `TODO_NUM` entries. Not a single experimental number is real.
- **Where:** Table 1 (all rows, all columns), Section 5.3, the abstract ("TODO_NUM% smaller"), the 33% claim in the Discussion.
- **Severity:** 5/5 — This is a complete blocker. The paper cannot be evaluated empirically. Every claim about set-size reduction, near-zero coverage, or comparison to baselines is unverifiable.
- **Resolution:** Run the experiments. Populate Table 1 with actual numbers.

### W2: FIGURE CAPTION SAYS "GPT-2" BUT EXPERIMENTS USE "Qwen2.5-7B-Instruct"
- **Issue:** Figure 3 caption states "Coverage is near-zero for all methods due to GPT-2's limited QA capability" but the experimental setup (Section 5.1) specifies Qwen2.5-7B-Instruct. The text in Section 7 also discusses GPT-2's 2-3% correct-answer rate.
- **Where:** Fig 3 caption, Section 5.1, Section 7 (Discussion paragraph 3).
- **Severity:** 4/5 — This is not a minor typo. It suggests the paper text was written for one model and incompletely revised for another. The entire near-zero coverage narrative hinges on model quality.
- **Resolution:** Reconcile the text. If GPT-2 results exist, report them. If the experiments used Qwen, revise all references to GPT-2 and clarify what the Qwen admissibility rate `p_A` actually is.

### W3: THEOREM 1 COVERAGE IS CONDITIONAL, NOT MARGINAL
- **Issue:** Theorem 1 guarantees `1 - alpha - 1/(|I|+1)` conditional on the admissibility event `A`. The abstract and much of the framing imply this is a strong guarantee, but marginal coverage is upper-bounded by `p_A`. On a weak model, this is a near-vacuous guarantee.
- **Where:** Theorem 1, Abstract, Section 1 (contribution 1), Section 4.4.
- **Severity:** 3/5 — The paper does discuss this in Remark 1, but the abstract leads with the conditional guarantee as if it were the main result. The gap between the stated guarantee and what a practitioner actually gets is underemphasized.
- **Resolution:** Make the conditional-vs-marginal distinction more prominent. Add a practitioner-facing paragraph explaining what the guarantee actually delivers for a model with `p_A = 0.5`.

### W4: EMBEDDING SPACE CHOICE IS UNJUSTIFIED
- **Issue:** SemCP uses all-MiniLM-L6-v2 (frozen, 384-d) as the embedding space but the paper itself acknowledges known pathologies: anisotropy, negation insensitivity. No evidence is provided that this embedding space is appropriate for the specific QA tasks used.
- **Where:** Section 5.1 (embeddings), Section 2 (semantic representations paragraph).
- **Severity:** 3/5 — The learned RBF kernel is supposed to compensate, but the kernel is optimized over only 6 discrete bandwidth values on a held-out 20% split of 500 training examples (effectively ~33 examples). This is a thin justification.
- **Resolution:** Justify embedding choice with ablations or prior literature. Report the anisotropy diagnostics for this embedding on these specific outputs.

### W5: NLI PARTITION FIDELITY IS UNCHARACTERIZED
- **Issue:** The bidirectional NLI partition is the foundation of the entire method, but its accuracy — measured against a ground-truth semantic equivalence labeling — is never reported. How often does DeBERTa-v2-xlarge-MNLI incorrectly cluster two strings?
- **Where:** Section 4.1, Section 5.1, Section 6 (Limitations).
- **Severity:** 3/5 — An imperfect partition means the "meaning classes" are not actually semantic equivalence classes, which undermines the theoretical guarantee (which assumes perfect bidirectionally-entailed equivalence).
- **Resolution:** Add a human evaluation or a curated test set measuring NLI partition precision/recall against ground-truth semantic equivalence.

### W6: BANDWIDTH OPTIMIZATION IS UNDERSPECIFIED
- **Issue:** The bandwidth optimization minimizes set size subject to coverage >= 1-alpha on a held-out 20% training split. But the constraint can be infeasible when generator quality is low (GPT-2: 2-3% correct). The paper defaults to some value in this regime but doesn't specify what value or how it's chosen.
- **Where:** Section 4.2 ("in this regime, sigma defaults"), Section 5.1, Algorithm 1.
- **Severity:** 3/5 — In the regime where the paper's claims are most relevant (weaker models, near-zero coverage), the kernel is essentially unconstrained. The "learned" aspect doesn't apply there.
- **Resolution:** Specify the default bandwidth explicitly. Report the constraint feasibility rate during bandwidth optimization.

### W7: CODE NOT RELEASED
- **Issue:** The paper claims "Code and run logs are released for reproducibility" but the code is not available (no repository link in the paper; the NeurIPS checklist answer is "upon publication").
- **Where:** Abstract, NeurIPS checklist item 5, Algorithm 1.
- **Severity:** 2/5 — This is a reproducibility score hit. The paper cannot be independently verified before publication.
- **Resolution:** Release the code with the paper submission.

### W8: 33% SET-SIZE REDUCTION CLAIM IS UNVERIFIABLE
- **Issue:** The Discussion claims "33% reduction in prediction set size on SQuAD (13.35 vs 19.89 for Token-CP)" but since all Table 1 numbers are TODO_NUM, this specific number is also fabricated.
- **Where:** Abstract, Discussion Section 7.
- **Severity:** 4/5 — This is the paper's primary empirical claim and it cannot be verified.
- **Resolution:** Run the experiments.

### W9: Naive Semantic BASELINE IS INTERNAL (NOT FROM PRIOR WORK)
- **Issue:** The "Naive Semantic" baseline (18.83 vs 13.35) is an ablation variant introduced in this paper, not a published prior method. Claiming the learned kernel "substantially outperforms" it is an internal comparison, not a comparison to existing art.
- **Where:** Section 6 (ablation), Discussion.
- **Severity:** 2/5 — The ablation is fine internally, but the framing in Discussion ("the learned kernel is the critical component") overstates what an internal ablation establishes.
- **Resolution:** Clarify that this is an ablation, not a comparison to prior work.

---

## Per-Rubric-Dimension Scores

| Dimension | Score | Calibration Anchor | Justification |
|---|---|---|---|
| **Originality / Novelty** | 7 | Substantial conceptual advance | The quotient-space conformal prediction framing is genuinely new; kernel-based lifted scores are a non-obvious combination. The 5-year test: the semantic lifting idea will outlive the specific benchmark. |
| **Soundness** | 4 | Serious gaps compromise main claims | Theorem 1 is technically correct but conditional; the empirical grounding is entirely missing (all TODO_NUM). The figure caption / model mismatch is a serious text coherence problem. Cannot assess validity of the 33% reduction claim. |
| **Significance** | 6 | Useful within subfield | If the experiments bore out the 33% set-size reduction at matched coverage, this would be important for every practitioner deploying CP on LLMs. The admissibility decomposition alone is worth publishing as a short paper. |
| **Clarity** | 7 | Clear, well-organized | The method section is carefully written. Notation is consistent. The quotient-space formalization is clean. Deductions for the GPT-2 / Qwen inconsistency and TODO placeholders. |
| **Reproducibility** | 3 | Critical code missing | No code repository link. All numbers are TODO_NUM. The paper explicitly says code will be released upon publication, which means at submission time there is nothing to reproduce. |
| **Contextualization vs Prior Work** | 7 | Strong coverage | Comprehensive discussion of ConU, SAFER, LofreeCP, TECP, semantic entropy. The complementary positioning is intellectually honest and well-argued. |
| **Ethical / Broader Impact** | 6 | Boilerplate | Standard broader impact statement is present but generic. No specific ethical concerns raised. Adequate, not excellent. |

**Weighted Average:** (7*1.0 + 4*1.5 + 6*1.0 + 7*0.7 + 3*1.0 + 7*0.8 + 6*0.5) / (1.0+1.5+1.0+0.7+1.0+0.8+0.5) = (7 + 6 + 6 + 4.9 + 3 + 5.6 + 3) / 6.5 = 35.5 / 6.5 = **5.46**

This is a **Reject** range (4.0-5.5), driven primarily by Soundness (all experiments placeholders) and Reproducibility (no code).

---

## 5+ Pointed Questions

1. **The placeholder problem:** Table 1 contains exclusively TODO_NUM entries. If I asked you to send me one real number from your experiments right now, could you? If not, what exactly needs to happen before the paper can be evaluated? What is the timeline?

2. **GPT-2 vs Qwen inconsistency:** The Figure 3 caption says "GPT-2's limited QA capability" and the Discussion (line 351) says "GPT-2 generates correct answers for only 2-3% of questions," but the experiments section specifies Qwen2.5-7B-Instruct. Which model produced the results in Table 1? Were GPT-2 experiments run and discarded? Or are the Qwen results also near-zero coverage?

3. **What is p_A for Qwen2.5-7B-Instruct on TriviaQA and SQuAD?** The entire paper's empirical narrative pivots on near-zero coverage being caused by low generator quality. But you never report the admissibility rate for the model you actually use. Is p_A > 0.90? Is it < 0.50? Without this number, I cannot evaluate whether your conditional coverage guarantee is meaningful or vacuous for your setup.

4. **The 33% claim:** You state SemCP delivers "33% smaller set sizes than the strongest string-level baseline at matched conditional coverage." Since Table 1 is all placeholders, where does 13.35 vs 19.89 come from? Did you run Token-CP on SQuAD? Did you run SemCP? Both? Neither?

5. **The NLI partition is unvalidated:** Your theoretical guarantee assumes the partition Pi is a perfect semantic equivalence relation. But DeBERTa-v2-xlarge-MNLI at 0.5 threshold is not a perfect semantic equivalence oracle. What is the pairwise accuracy of your NLI partition against human-annotated ground-truth semantic equivalence? How much does partition noise degrade your coverage guarantee in practice?

6. **The learned kernel is optimized on 33 calibration examples:** You hold out 20% of the training split (~33 examples) to optimize bandwidth over 6 discrete values subject to a coverage constraint that may be infeasible. How stable is the selected bandwidth across seeds? Have you tested whether the grid resolution (only 6 values spanning 0.1 to 4.0) is sufficient?

7. **Forget the benchmarks — what is the one sentence that changes a researcher's mental model after reading this paper?** If the answer is "conformal prediction sets can be smaller when you deduplicate by meaning," I would agree this is true but not publish-it-at-NeurIPS new. If the answer is something about the quotient-space formalization preserving exchangeability, I'd agree it's non-trivial. What do you believe is the irreducible insight?

---

## Falsifiability Test

**What evidence would change my decision?**

- **Strong Accept:** Experiments show 33%+ set-size reduction at matched conditional coverage (>0.89) AND marginal coverage >0.80 on Qwen2.5-7B-Instruct with actual reported p_A > 0.85. Code released and independently reproducible.

- **Accept:** Experiments show 15-25% set-size reduction with valid coverage on one dataset. Kernel insight replicated. Code released.

- **Borderline:** Experiments show set-size reduction but coverage is marginal (< 0.85) or inconsistent across datasets. Internal ablation is compelling but external validation missing.

- **Reject:** Any one of: (a) experiments are never run and paper is submitted with TODO_NUM placeholders; (b) Qwen results show p_A < 0.50, making the conditional guarantee vacuous for the main experiments; (c) code remains unreleased.

- **Strong Reject:** (a) The 33% reduction claim is fabricated (numbers from preliminary experiments not in the actual paper); (b) Figure 3 caption and experimental setup are irreconcilable and the paper is internally inconsistent; (c) No code at submission.

**Currently:** I cannot move beyond **Reject** because there is not a single real number in the experimental section. My belief state is that the paper has a genuine theoretical contribution (quotient-space conformal prediction) but I cannot verify whether the empirical claims are real or aspirational.

---

## Confidence

**4/5** — I am highly confident in the theoretical analysis (the quotient-space formalization and exchangeability preservation are correct) and highly confident in my assessment that the paper has no empirical grounding. The TODO_NUM problem is unambiguous. My uncertainty is in how to calibrate the significance of the contribution given the missing experiments — the gap the paper identifies is real, but I cannot assess whether the proposed solution actually works.

---

## Decision: **Reject**

**Reasoning:** The paper identifies a genuine and important gap (semantic conformal prediction) and makes a technically sound theoretical contribution. The quotient-space formalization with kernel-based lifted scores is the right way to think about this problem. The admissibility-coverage decomposition alone is worth a short paper.

However, the paper cannot be evaluated empirically because there are no empirical results. All Table 1 entries are `TODO_NUM`. The figure caption says "GPT-2" while the experiments use "Qwen." The abstract claims "33% smaller set sizes" from experiments that appear not to have been run. This is not a paper that is "technically fine but needs more experiments" — it is a paper with a placeholder where the empirical contribution should be.

Under NeurIPS reviewer guidelines ("technically rigorous, intellectually generous"), I am being technically rigorous by noting that a paper whose central empirical claim cannot be verified must be rejected. I am being intellectually generous by noting that the theoretical framing is correct and the problem is real, so a revised version with actual numbers could be competitive.

**Recommendation to authors:** Run the experiments. Populate Table 1. Reconcile the GPT-2/Qwen inconsistency. Release code. Then resubmit. The bones of a strong paper are here.

---

*— The Big-Picture Editor*