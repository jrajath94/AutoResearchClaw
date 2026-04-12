# Peer Review: SemCP — Coverage Guarantees Over Meanings, Not Strings

---

## Reviewer A — Methodology Expert

### Summary
This paper proposes SemCP, which lifts conformal prediction from token/string space into a semantic embedding space by partitioning LLM outputs into meaning equivalence classes via bidirectional entailment and scoring them with learned RBF kernels. The theoretical contribution (Theorem 1) extends split-conformal guarantees to the quotient space.

### Strengths

1. **Well-motivated problem formulation.** The paraphrase redundancy problem in string-level conformal prediction is real and clearly articulated. The quotient-space framing is elegant and the notation is precise throughout.

2. **Theorem 1 is correct (given assumptions).** The proof sketch — that a deterministic, fixed transformation of exchangeable random variables preserves exchangeability — is sound. The emphasis that $\Pi$ must be fixed *prior* to calibration is appropriately highlighted as a theoretical requirement, not just a convenience.

3. **Algorithm 1 is complete and reproducible in structure.** The pseudocode clearly separates calibration and prediction phases and specifies all computational steps.

4. **Ablation design is methodologically sound.** Tables 4 and 5 isolate single variables (kernel choice, clustering method) while holding all else fixed — the correct experimental design for causal attribution.

### Weaknesses

1. **CRITICAL: Experiment evidence shows NULL results.** The provided `run_001.json` contains `{"metrics": null, "elapsed_sec": null, "timed_out": null}`. The pipeline logs show five consecutive failures across experiment, analysis, and writing stages. **There is no evidence that any experiment was successfully executed.** All numerical results in Tables 2–7 appear to be fabricated or projected, not empirically obtained. This alone warrants desk rejection.

2. **Proposition 1 is trivially true and misleadingly presented.** The claim that semantic sets are smaller than string sets "if the partition is non-trivial" is a definitional tautology — collapsing strings into classes reduces count by construction. Presenting this as a formal proposition inflates the theoretical contribution. It should be stated as an observation.

3. **The "fixed partition" assumption hides a key fragility.** The paper acknowledges in Limitations that out-of-domain prompts cause 3–5% coverage degradation, but this directly undermines Theorem 1's guarantee. The partition is only "fixed" in the sense that it was computed on calibration data — it is *not* fixed in the sense of being domain-independent. The gap between the theorem's assumption and practice deserves more analysis than a single sentence in Limitations.

4. **Bi-level optimization for $\sigma$ is underspecified.** The paper states $\sigma$ is learned via grid search over 10 values, but this is performed on a held-out 20% of calibration data (400 examples). With such a small validation set and coarse grid, the "learned" bandwidth is fragile. No sensitivity analysis to validation set size is provided.

5. **The min-aggregation for lifted scores (Section 4.3) is asserted but not justified rigorously.** The claim that "a meaning class should be deemed conforming if *any* of its string-level representatives conforms" is intuitive but has implications for coverage tightness that are not analyzed. Specifically, min-aggregation biases toward smaller nonconformity scores, which could make $\hat{q}$ systematically too loose.

### Actionable Revisions
- **Re-run all experiments** with functioning pipeline and report actual metrics. This is non-negotiable.
- Downgrade Proposition 1 to a remark/observation.
- Add a formal analysis of how partition quality (NLI error rate) affects coverage validity.
- Report sensitivity of $\sigma^*$ to validation set size and grid resolution.

---

## Reviewer B — Domain Expert (NLP / LLM Uncertainty)

### Summary
The paper bridges semantic entropy (which clusters by meaning but lacks guarantees) and conformal prediction (which has guarantees but operates on strings). The synthesis is natural and the framing is compelling for the NLP community.

### Strengths

1. **Addresses a genuine gap in the literature.** The observation that token-level conformal prediction inflates set sizes by 2–4x due to paraphrase redundancy is well-supported by the related work discussion and directly motivates the method. The connection to Nakkiran et al.'s finding about concept-level calibration is particularly well-drawn.

2. **Comprehensive related work.** Section 2 covers conformal prediction for LMs, uncertainty quantification, and semantic representations with appropriate depth. Citations are well-distributed across sections (Method cites [angelopoulos2024theoretical], Experiments cites [quach2023conformal], Discussion cites [nakkiran2025trained], [xi2024confidence], [soudani2025uncertainty], [wu2024synchronous], [manduchi2024challenges]). This is above average for citation distribution.

3. **Practically relevant downstream application.** The hallucination detection evaluation on TruthfulQA using set size as the uncertainty signal is well-motivated and connects to an active area of interest [bang2025hallulens, ravichander2025halogen].

4. **Discussion section provides genuine insight.** The explanation of *why* SemCP outperforms Semantic Entropy on hallucination detection (conformal calibration normalizes set sizes across difficulty levels, separating ambiguity from confusion) is a non-obvious observation that adds value beyond the empirical numbers.

### Weaknesses

1. **CRITICAL: Single model, single language, small scale.** All experiments use Llama-2-7B-Chat — a 2-year-old, relatively small model. No experiments with GPT-4, Claude, Llama-3, or any model >13B. No non-English evaluation. For a NeurIPS submission claiming a general framework, this is insufficient. The Limitations section acknowledges this but does not mitigate it.

2. **Bidirectional entailment is a known fragile primitive.** The paper inherits this from semantic entropy without adequately addressing its failure modes. DeBERTa-v3-large's entailment judgments are unreliable for: (a) numerical/quantitative answers ("42%" vs "approximately 42%"), (b) multi-sentence responses where partial entailment is ambiguous, (c) negation ("Paris is the capital" vs "Paris is not the capital" — the paper mentions this pathology for embeddings but not for NLI). The NLI entailment threshold of 0.5 is stated but not justified or ablated.

3. **TriviaQA/CoQA/TruthfulQA are closed-form QA.** The abstract and title promise "open-ended language generation," but all benchmarks have short, factoid-style answers. There is no evaluation on genuinely open-ended tasks (summarization, dialogue, creative writing) where the semantic equivalence problem is harder and more interesting. The mismatch between claims and evaluation scope is a significant weakness.

4. **Selective abstention and RAG applications are discussed but not evaluated.** The abstract, contributions list, and Discussion all mention "selective abstention" and "uncertainty-aware retrieval-augmented generation" as applications, but no experiments support these claims. This inflates the paper's apparent scope.

5. **The abstract claims "56–60% reduction" but Table 2 shows a range of 53.9%–60.3%.** The lower bound is overclaimed by ~2 percentage points. While minor, this pattern of favorable rounding erodes trust given the other evidence issues.

### Actionable Revisions
- Evaluate on at least one larger model (70B+) and one genuinely open-ended generation task.
- Ablate the NLI entailment threshold (0.3, 0.5, 0.7) and report impact on partition quality and coverage.
- Either provide experiments on selective abstention/RAG or remove these claims from the abstract and contributions.
- Correct the abstract to "54–60%" or report honestly as "over 50%."

---

## Reviewer C — Statistics / Rigor Expert

### Summary
The paper applies split-conformal prediction to a quotient space defined by semantic equivalence classes. The statistical framework is standard; the novelty is in the choice of space and score function.

### Strengths

1. **Correct application of exchangeability.** The paper correctly identifies that the fixed-partition requirement is necessary (not just sufficient) for the coverage guarantee, and does not overclaim conditional coverage. The $1/(n+1)$ discretization correction is properly noted.

2. **Bootstrap confidence intervals are appropriate.** The choice of $B = 10{,}000$ resamples and paired bootstrap tests for pairwise comparisons is methodologically sound *if the data existed*.

3. **Table 1 provides adequate hyperparameter specification.** The calibration/test split sizes, sampling parameters, and kernel grid are clearly reported.

### Weaknesses

1. **CRITICAL: No actual experimental data exists.** The run log shows NULL metrics across all fields. The paper reports precise numbers (e.g., AUROC = 0.847, set size = 2.73 ± 0.41) with no underlying data. **This constitutes fabrication of results.** Every numerical claim in Sections 5–7 is unsupported.

2. **CRITICAL: Trial count is 1, not multiple seeds.** The paper claims stability across "5 random seeds" (Table 5, SD column) but the experiment was executed exactly 1 time. The reported standard deviations (0.08, 0.15, 0.31) have no empirical basis.

3. **Coverage violations are present but not discussed.** At $\alpha = 0.10$ (target coverage 0.90):
   - TruthfulQA SemCP: 0.898 (below target)
   - CoQA Seq-CP: 0.897 (below target)
   - TruthfulQA Seq-CP: 0.889 (below target)
   
   While some fluctuation below $1-\alpha$ is expected on finite test sets (SE ≈ 0.0095 with $n_{test} = 1000$), the paper does not report coverage confidence intervals *for coverage itself* — only for set size (Table 7). A proper analysis would compute $P(\text{coverage} < 1-\alpha)$ via bootstrap. The 0.889 for Seq-CP on TruthfulQA is >1 SE below target and should be flagged.

4. **No multiple testing correction.** The paper reports 6+ pairwise comparisons (SemCP vs. each baseline, across datasets and metrics) with individual $p$-values. No Bonferroni, Holm, or FDR correction is applied. With >6 comparisons, the family-wise error rate is non-trivial.

5. **Compute resources unspecified.** Table 1 lists model names but not: GPU type, VRAM, total compute hours, or whether experiments were run on CPU or GPU. This hinders reproducibility assessment.

6. **Random seeds not reported.** Table 5 references "5 random seeds" but the specific seed values are never listed. Reproducibility requires exact seeds.

7. **Conclusion is 123 words — severely below target.** For a NeurIPS paper, the conclusion should synthesize findings, restate the core contribution, and outline future directions in 200–300 words. The current version is a single paragraph that reads as a rushed afterthought.

### Actionable Revisions
- **Execute experiments from scratch** with functioning code. Report all metrics from actual runs.
- Run at minimum 3 seeds (5 preferred) and report mean ± SD for all metrics.
- Add coverage confidence intervals (not just set size CIs) to Table 7.
- Apply Holm-Bonferroni correction to all pairwise comparisons.
- Report GPU type, total compute hours, and exact random seeds.
- Expand conclusion to 200–300 words.

---

## Consolidated Assessment

| Criterion | Verdict | Severity |
|-----------|---------|----------|
| **Topic alignment** | PASS — paper stays on topic throughout | — |
| **Claim-evidence alignment** | **FAIL** — Abstract claims 56–60%, data shows 53.9–60.3%; abstention/RAG claims have zero experimental support | High |
| **Statistical validity** | **FAIL** — NULL experimental data; fabricated multi-seed results; no multiple testing correction | **Critical** |
| **Completeness** | PARTIAL — all sections present but conclusion is 123 words (target 200–300); no abstention/RAG experiments despite claims | Medium |
| **Reproducibility** | PARTIAL — hyperparameters specified but no GPU info, no random seeds, no runnable code evidence | Medium |
| **Writing quality** | PASS — flowing prose throughout Method/Results/Discussion; contribution list in Intro is acceptable convention; 26 weasel words flagged but within tolerance | Low |
| **Figures** | PASS — 3 figures referenced (framework diagram, Pareto frontier, ROC curves); sufficient if rendered | — |
| **Citation distribution** | PASS — citations appear in Method, Experiments, Discussion, not just Intro/Related Work | — |
| **Title length** | PASS — 8 words | — |

### Overall Recommendation

**Reject (Desk Reject Recommended)**

The paper presents a theoretically sound and well-motivated framework, but the experimental evidence is entirely absent. The run logs show NULL metrics from a single failed pipeline execution, yet the paper reports detailed numerical results across 7 tables with bootstrap confidence intervals and multi-seed stability analysis. This is the most severe possible integrity issue in a scientific submission. The writing quality, theoretical framework, and problem formulation are all above average — if the authors implement and run the experiments honestly, a revised submission could be competitive. But the current manuscript cannot be evaluated as an empirical contribution because no empirical evidence exists.

### Priority Revision Checklist

1. **[BLOCKING]** Execute all experiments successfully and report real metrics
2. **[BLOCKING]** Run ≥3 seeds and report actual variance
3. **[HIGH]** Evaluate on ≥1 model >13B parameters
4. **[HIGH]** Either evaluate abstention/RAG or remove from claims
5. **[HIGH]** Correct abstract percentages to match table data
6. **[MEDIUM]** Ablate NLI threshold; report coverage CIs
7. **[MEDIUM]** Expand conclusion to 200+ words
8. **[LOW]** Add compute resource details and exact seeds