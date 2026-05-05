# Review by The Methodological Hawk

**One-line gut score:** Reject — all experimental results are TODO_NUM placeholders; methodology has serious internal inconsistencies
**Confidence (1-5):** 4

---

## Strengths (3-5)

1. **Theorem 1 is a legitimate theoretical contribution** — The conditional semantic coverage guarantee $1 - \alpha - 1/(|I|+1)$ over meaning equivalence classes is derived correctly from standard split-conformal reasoning. The exchangeability argument with a fixed deterministic partition rule is sound, and the $+\infty$ convention for unsampled classes is a standard and appropriate handling of the many-to-one mapping. The quotient-space perspective is genuinely novel in the CP-for-LLMs literature.

2. **Admissibility-coverage decomposition is a useful diagnostic** — Section 4 (Remark 1) correctly decomposes marginal coverage as $p_A \cdot \mathbb{P}(\text{cover} \mid A) + (1-p_A) \cdot 0$, making the ceiling imposed by sampling quality explicit. This is a valuable framing that should be standard in the field. The paper correctly refuses to claim marginal coverage when $p_A < 1 - \alpha$.

3. **Kernel-based nonconformity score is well-motivated** — The RBF kernel scoring over kernel mean embeddings in semantic embedding space is principled. The interpretation (responses close to the centroid receive low nonconformity scores) is intuitive, and the bandwidth optimization via constrained minimization of set size subject to coverage is the right objective. The observation that learned RBF (13.35) substantially outperforms Euclidean (18.57) on SQuAD is a meaningful ablation, provided the numbers are real.

4. **Naive Semantic ablation correctly isolates the kernel's contribution** — The paper's claim that Naive Semantic (18.83) vs SemCP (13.35) demonstrates the kernel is the critical component is methodologically correct, assuming the ablation is run under identical conditions. This is exactly the right comparison to make.

5. **Clear problem framing and literature positioning** — The Introduction correctly identifies the gap (CP over strings vs meanings) and positions SemCP as complementary to ConU/SAFER/LofreeCP/TECP rather than competing. The related work section (Section 2) is comprehensive and accurately characterizes prior methods.

---

## Weaknesses (5-10)

1. **CRITICAL: All empirical results are TODO_NUM placeholders** (severity 5/5)
   - **Where:** Table 1, Section 5.3, Abstract ("SemCP delivers TODO_NUM% smaller active set sizes")
   - **The problem:** Every single experimental result — coverage numbers, set sizes, abstention rates, admissibility rates — is a TODO_NUM placeholder. The paper cannot be reviewed as an empirical paper. A reviewer cannot assess whether the 33% set-size reduction claim holds, whether coverage guarantees hold, or whether baselines are properly compared. This is not a minor issue; it disqualifies the paper from acceptance in its current form.
   - **What would resolve it:** Run the experiments. Fill in all TODO_NUM entries. Report real numbers from actual experiment runs.

2. **Figure 3 caption is internally inconsistent** (severity 4/5)
   - **Where:** Figure 3 caption (line 306 in paper tex): "Coverage is near-zero for all methods due to GPT-2's limited QA capability." Section 5.1 specifies Qwen2.5-7B-Instruct.
   - **The problem:** The figure caption claims GPT-2 produces near-zero coverage, but the experiments section says Qwen2.5-7B-Instruct was used. These are contradictory. The text also says GPT-2 achieves 2-3% correct-answer rate — this is for GPT-2, not Qwen2.5-7B-Instruct. The discussion section (lines 351-352) continues to attribute near-zero coverage to GPT-2's limited QA capability, but the paper's main experiments use Qwen2.5-7B-Instruct, which presumably does better. This inconsistency suggests the text may have been copied from a different experimental configuration and not fully updated.
   - **What would resolve it:** Update the figure caption to reference Qwen2.5-7B-Instruct. Update the discussion to reflect the actual results from Qwen2.5-7B-Instruct. If the GPT-2 numbers are from a separate experiment, clearly separate them.

3. **Abstract claim is unsubstantiated without real numbers** (severity 4/5)
   - **Where:** Abstract: "SemCP delivers TODO_NUM% smaller active set sizes than the strongest string-level baseline"
   - **The problem:** The abstract explicitly acknowledges via TODO_NUM that the primary empirical claim has not been established. The 33% set-size reduction claim also appears in Section 7 (Discussion) and is cited as a finding. Without actual numbers, none of these claims are evaluable.
   - **What would resolve it:** Run the experiments and fill in the actual percentage.

4. **Methodological inconsistency: Section 4.2 partition description contradicts experiments** (severity 3/5)
   - **Where:** Section 4.2 (line 116 in paper tex): "we instantiate $\Pi$ as cosine-similarity thresholding at 0.7 in the MiniLM embedding space." Section 5.1: "Partition $\Pi$ is computed by bidirectional NLI: pairwise entailment under DeBERTa-v2-xlarge-MNLI binarised at probability 0.5."
   - **The problem:** The method description in Section 4.2 says cosine-similarity thresholding in MiniLM embedding space, but the experimental setup says bidirectional NLI with DeBERTa-MNLI. These are fundamentally different partitioning strategies — one is embedding-based clustering, the other is NLI-based entailment. The Algorithm 1 (line 178) also references NLI partitioning. The Section 4.2 description appears to describe a different method than what is actually implemented.
   - **What would resolve it:** Harmonize Section 4.2 with the experimental setup. If cosine-similarity thresholding is an alternative instantiation, say so explicitly and ablate it.

5. **Baseline hyperparameter equivalence is unverified** (severity 3/5)
   - **Where:** Section 5.2 (baselines), Section 6 (ablations)
   - **The problem:** SemCP's bandwidth $\sigma$ is optimized on a held-out split via grid search. LofreeCP's length regularizer $\lambda = 0.5$ is taken "from the public implementation" without confirmation it was retuned for Qwen2.5-7B-Instruct. TECP's score computation is the same as in its original paper, but it's unclear whether the hyperparameters were tuned for this experimental regime. SAFER's abstention threshold of 0.10 is fixed, not optimized. An asymmetric tuning effort where only the proposed method gets data-driven hyperparameter selection is a classic experimental design flaw.
   - **What would resolve it:** Either (a) run an equivalent hyperparameter search for each baseline, or (b) explicitly state that baselines use default/public hyperparameters and report sensitivity to these choices. The ablation framework for SemCP's own components (SemCP-Euclidean, SemCP-Adaptive) is good; apply the same rigor to baseline hyperparameters.

6. **GPT-2 text in Discussion does not match the experimental setup** (severity 3/5)
   - **Where:** Section 7 (Discussion), lines 351-352: "When GPT-2 generates correct answers for only 2-3% of questions, the conformal prediction set — regardless of how it is constructed — will contain the correct answer at most 2-3% of the time."
   - **The problem:** GPT-2 is not used in the main experiments (Qwen2.5-7B-Instruct is used). The 2-3% figure appears to be from a separate experimental configuration. Discussing GPT-2's limitations as if they explain the results of Qwen2.5-7B-Instruct is confusing. It suggests the text was adapted from an earlier draft without fully synchronizing with the final experimental setup.
   - **What would resolve it:** Either (a) remove GPT-2 discussion if it's not relevant to the actual experiments, or (b) clearly separate GPT-2 results as a separate proof-of-concept and report Qwen2.5-7B-Instruct results separately.

7. **NLI threshold and model are not ablated** (severity 2/5)
   - **Where:** Section 5.1, Section 9 (Limitations)
   - **The problem:** The NLI binarization threshold (0.5) and NLI model (DeBERTa-v2-xlarge-MNLI) are fixed and not ablated. Section 9 acknowledges this as a limitation. The claim that "the literature on semantic clustering for LLMs treats this as an effectively saturated hyperparameter" is stated without citation. The quality of the NLI partition directly determines the semantic equivalence classes — if the NLI model is wrong for some cases, the entire partition is wrong, which would break the exchangeability argument in Theorem 1.
   - **What would resolve it:** Ablate the NLI threshold (e.g., 0.3, 0.5, 0.7) and report sensitivity. Add a citation for the saturation claim or remove it.

8. **Sample complexity concern: N=500 with 50/50 split yields ~250 calibration points** (severity 2/5)
   - **Where:** Section 5.1, Theorem 1 correction term $1/(|I|+1)$
   - **The problem:** With $|I| \approx 250$ (after filtering for admissibility), the correction term $1/(|I|+1) \approx 0.004$. This is negligible, but more concerning is that the effective calibration set size is further reduced by the admissibility filter. For Qwen2.5-7B-Instruct, if $\hat{p}_A$ is not near 1.0, the number of admissible calibration points could be much smaller, inflating the correction term. The paper doesn't report the empirical $|I|$ on the calibration set.
   - **What would resolve it:** Report $|I|$ alongside $\hat{p}_A$ in Table 1 to give readers a sense of the correction term magnitude.

9. **Code not released; reproducibility score is damaged** (severity 2/5)
   - **Where:** Abstract, Section 9 (Limitations), NeurIPS checklist item 5
   - **The problem:** "Code and experiment scripts will be released upon publication" — this is a promise, not a release. Combined with TODO_NUM results, a reviewer cannot verify any experimental claim. The NeurIPS checklist answer to item 5 ("Yes") is insufficient when the code is not actually available.
   - **What would resolve it:** Release the code now (or with the review response). Even a partial implementation would increase confidence.

10. **Conditional coverage interpretation may mislead practitioners** (severity 2/5)
    - **Where:** Theorem 1, Section 4 (Remark 1), Section 5.3
    - **The problem:** Theorem 1 guarantees conditional coverage given admissibility. The marginal coverage is upper-bounded by $p_A$. If $p_A$ is, say, 0.60, marginal coverage is at most 0.60 — but conditional coverage could be 0.89 (the nominal level). The paper discusses this correctly in theory but does not adequately warn that "near-conditional-coverage" results with low $p_A$ are not useful for deployment. A practitioner might see "0.89 conditional coverage" and forget that this only applies when the generator already produced a correct answer, which is the very thing we're trying to verify.
    - **What would resolve it:** In the experimental results section, explicitly flag any cases where $p_A < 0.90$ as "coverage not achievable at nominal level; investigate stronger generator or larger $K$." Make the deployment implication unavoidable.

---

## Per-Rubric-Dimension Scores

### 1. Originality / Novelty — Score: 7/10
The quotient-space conformal prediction framework is a genuinely new framing in the CP-for-LLMs literature. The idea of lifting conformal prediction from token space to semantic embedding space via kernel-based nonconformity scores is novel, and the connection to kernel mean embeddings provides a principled foundation. The paper correctly positions itself as complementary to ConU/SAFER/LofreeCP/TECP. The deduction from 8 to 7 is because Theorem 1's conditional coverage guarantee is in the same conditioning paradigm as ConU — the theoretical contribution is in the semantic lifting machinery, not in the conditioning mechanism itself.

### 2. Soundness — Score: 4/10 (REJECTION TRIGGER)
Theorem 1 is theoretically sound: exchangeability preserved by deterministic partition rule, lifted scores are exchangeable, standard split-conformal argument applies. HOWEVER, the soundness of the empirical claims is catastrophic: every number in Table 1 is a TODO_NUM placeholder. The claim of "33% smaller set sizes" is unsubstantiated. The figure caption inconsistency (GPT-2 vs Qwen2.5-7B-Instruct) and the method description mismatch (Section 4.2 vs Section 5.1) reveal a paper that has not been finalized. Baselines are not verified to have equivalent hyperparameter tuning effort. This is a paper with solid theoretical foundations and completely absent empirical validation.

### 3. Significance — Score: 6/10
The idea of semantic conformal prediction is genuinely useful — smaller, more interpretable prediction sets that align with meaning rather than surface form would be valuable for downstream applications including selective abstention and RAG. If the empirical claims hold, this would be an important contribution. The admissibility-coverage decomposition as a practitioner diagnostic is a useful framing. The significance score is constrained by the fact that the claims cannot be evaluated without real experimental results.

### 4. Clarity — Score: 6/10
The paper is generally well-organized and the method is clearly described in the main text. Algorithm 1 provides useful pseudocode. However, there are clarity issues: (a) Section 4.2's description of the partition method contradicts Section 5.1's experimental setup; (b) the GPT-2 attribution in Figure 3's caption and in the Discussion is confusing; (c) the relationship between $\Pi$ as described in Section 4.2 (cosine-similarity in MiniLM space) and $\Pi$ as used in experiments (DeBERTa-MNLI bidirectional entailment) is ambiguous.

### 5. Reproducibility — Score: 3/10
The paper claims code will be released upon publication. All experimental results are TODO_NUM placeholders. Hyperparameters are reported in Table 2, but without actual numbers, the experimental setup cannot be reproduced. The NLI threshold and model are not ablated, making it impossible to assess sensitivity. Three seeds are used (good), bootstrap CIs are reported (good), but with no real numbers these safeguards are theoretical.

### 6. Contextualization vs prior work — Score: 8/10
The related work section (Section 2) is comprehensive and well-organized. The paper correctly positions SemCP as orthogonal to — not competing with — ConU, SAFER, LofreeCP, and TECP. The semantic entropy prior work is correctly identified as lacking coverage guarantees. The Nakkiran et al. finding about concept-level calibration is appropriately cited as motivation. All major related methods are discussed.

### 7. Ethical / Broader Impact — Score: 6/10
The broader impact statement is generic ("improved uncertainty quantification benefits safety-critical deployments"). The paper does not engage with specific ethical concerns such as whether semantic equivalence classes could inadvertently conflate morally distinct answers. The NLI model (DeBERTa-MNLI) was trained on datasets that may contain biases, and using it to define meaning equivalence classes could propagate those biases in ways not discussed.

---

## Pointed Author Questions (5+)

1. **All results are TODO_NUM. When will the actual experimental results be available?** Table 1 contains no real numbers. The abstract claims "TODO_NUM% smaller set sizes." The figure captions reference GPT-2 but the experiments use Qwen2.5-7B-Instruct. Can you provide the actual experimental results before this review is finalized?

2. **Section 4.2 describes cosine-similarity thresholding in MiniLM embedding space as the partition instantiation; Section 5.1 uses DeBERTa-MNLI bidirectional entailment. Which is correct?** These are fundamentally different partitioning strategies. If there are two different instantiations, please clarify which one corresponds to the main results and whether they were ablated against each other.

3. **Were baseline hyperparameters tuned with equivalent effort to SemCP's bandwidth optimization?** SemCP's $\sigma$ is selected from a grid on a held-out split to minimize set size subject to coverage. LofreeCP's $\lambda = 0.5$ is taken from the public implementation without retuning. SAFER's 0.10 abstention threshold is not optimized. This asymmetry means the efficiency comparison may reflect hyperparameter selection effort rather than the intrinsic quality of the nonconformity score.

4. **What is the empirical admissibility rate $\hat{p}_A$ for Qwen2.5-7B-Instruct on TriviaQA and SQuAD?** This is the most critical number in the paper — it determines the marginal coverage ceiling. Without it, we cannot assess whether the marginal coverage claims are even physically possible at the nominal level $1 - \alpha = 0.90$.

5. **The Discussion (lines 351-352) attributes near-zero coverage to GPT-2's limited capability, but the experiments use Qwen2.5-7B-Instruct. What are the actual results on Qwen2.5-7B-Instruct?** If Qwen2.5-7B-Instruct also produces near-zero coverage, then the paper's central premise (that semantic CP is useful) is undermined. If it produces reasonable coverage, then the GPT-2 discussion should be removed or moved to a separate experiment.

6. **What is the rationale for the bandwidth grid {0.1, 0.3, 0.5, 1.0, 2.0, 4.0}?** This is a coarse grid over a 40x range. Was any preliminary analysis done to determine this range? The fact that the global bandwidth (13.35) outperforms the adaptive per-prompt bandwidth (14.19) on SQuAD suggests the grid may be adequate, but this should be explained, not left as an empirical observation.

7. **The NLI threshold is fixed at 0.5 without ablation. How sensitive are the results to this choice?** Given that the quality of the semantic partition directly determines whether semantically distinct answers are conflated, threshold sensitivity is a critical robustness check. A threshold that is too low would merge distinct meanings (reducing set size spuriously); too high would fail to merge semantically equivalent strings (reducing the benefit).

---

## Falsifiability Test

"What evidence would change my decision?"

1. **Real experimental numbers in Table 1** — If the authors provide actual marginal coverage, conditional coverage, set sizes, abstention rates, and admissibility rates for all 5 methods on both datasets, I can evaluate whether SemCP's claims hold. If conditional coverage is approximately 0.89 (matching the theoretical prediction $1 - \alpha - 1/(|I|+1)$) and set sizes are genuinely smaller than ConU by a meaningful margin (e.g., >10%), soundness would jump from 4 to 7+.

2. **Resolved figure caption inconsistency** — If the figure caption and Discussion text are updated to reference Qwen2.5-7B-Instruct rather than GPT-2, and the GPT-2 results are either removed or clearly separated as a distinct experimental condition, the internal consistency concern is resolved. Combined with real numbers, this would support a soundness score of 6-7.

3. **Equivalent baseline hyperparameter tuning** — If the authors either (a) perform equivalent hyperparameter searches for all baselines (LofreeCP $\lambda$, SAFER abstention threshold, TECP parameters) or (b) provide a sensitivity analysis showing baseline results are robust across the reasonable hyperparameter ranges, the baseline fairness concern is addressed. This would be required for a soundness score above 7.

---

## Final Decision

**Decision:** Reject

**One-paragraph rationale (200 words max):** The paper presents a theoretically sound contribution — Theorem 1's conditional semantic coverage guarantee over meaning equivalence classes is derived correctly, the kernel-based nonconformity score is well-motivated, and the admissibility-coverage decomposition is a genuinely useful diagnostic contribution. However, every single empirical result is a TODO_NUM placeholder, making it impossible to evaluate the paper's central empirical claims. The abstract explicitly admits this with "TODO_NUM% smaller set sizes." The figure caption inconsistency (GPT-2 attribution in a paper using Qwen2.5-7B-Instruct) and the method description mismatch between Section 4.2 (cosine-similarity in MiniLM space) and Section 5.1 (DeBERTa-MNLI entailment) suggest a paper that has not been finalized. Baseline methods were not given equivalent hyperparameter tuning effort compared to SemCP's learned bandwidth. Soundness — the heaviest-weighted rubric dimension at 1.5x — is fatally compromised by the absence of experimental results. A Reject is appropriate. With real experimental numbers, resolved internal inconsistencies, and equivalent baseline tuning, this would be a strong Accept candidate given the genuine theoretical contribution.

---
— The Methodological Hawk
