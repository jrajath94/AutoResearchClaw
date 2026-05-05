# Naive Reader Review — SemCP: Coverage Guarantees Over Meanings, Not Strings

**Reviewer:** The Naive Reader (1st-year PhD student)
**Paper:** SemCP (NeurIPS 2026 submission, `artifacts/deliverables/paper.tex`)
**Date:** 2026-05-01

---

## Bottom Line

The paper proposes an interesting idea—moving conformal prediction from strings to meanings—but I cannot give it a fair evaluation because **none of the experiments have been run**. Every number in the main results table is `TODO_NUM`. The figure captions describe GPT-2; the experiments use Qwen2.5-7B-Instruct. The abstract claims 33% set-size reduction; I have no way to verify this. A paper is not a paper without results. If the experiments were real, the ideas are promising but the exposition has serious clarity problems that I detail below.

---

## Strengths

1. **Theorem 1 is well-motivated and clearly positioned.**
   The conditional coverage guarantee (Section 4.4, Theorem 1) is introduced with explicit comparison to ConU, SAFER, and LofreeCP—showing the paper understands where it sits relative to prior work. The admissibility decomposition in Remark 1 is a genuinely useful diagnostic for practitioners. This is the paper's strongest section.

2. **The quotient-space formalization is novel and well-motivated.**
   Section 4.3's lift from strings to equivalence classes via the min-aggregation rule (Equation 2) is clearly explained. The intuition that "a meaning class is adequately represented by its best-fitting string" (Section 4.3, line 144) is accessible and correct.

3. **Introduction gives clear motivation with concrete examples.**
   Line 38: "semantically identical outputs such as 'Paris' and 'The capital of France is Paris' occupy separate positions in the prediction set"—this is the clearest one-sentence articulation of the problem I have seen in any CP-for-LLM paper.

4. **Ablation studies are well-designed.**
   SemCP-NoM2O, SemCP-Euclidean, and SemCP-Adaptive isolate distinct components cleanly. The finding that learned RBF (13.35) substantially outperforms Euclidean (18.57) on SQuAD would be a clean, interpretable result if the numbers were real.

5. **Limitations section is unusually honest.**
   Six explicit limitations, including the critical "downstream applications not evaluated." This earns trust even if the paper cannot address all of them.

---

## Weaknesses

### W1: Experiments Do Not Exist — Paper Cannot Be Reviewed (Severity: 5/5)
**Where:** Table 1, all numeric results in Section 5.3
**Issue:** Every cell in Table 1 (main results) is `TODO_NUM`. The paper cannot be evaluated without empirical results. This is not a draft—it is an intent. The abstract makes specific quantitative claims ("33% smaller set sizes than the strongest string-level baseline") that I have no way to verify. The paper is unacceptably incomplete.

### W2: Critical Inconsistency — Partition Method (Severity: 4/5)
**Where:** Section 4.1, line 116 vs. Section 5.1, line 215
**Issue:** Section 4.1 says: "In our experiments, we instantiate Π as **cosine-similarity thresholding at 0.7** in the MiniLM embedding space." Section 5.1 says the partition is computed by "**bidirectional entailment under DeBERTa-v2-xlarge-MNLI** binarised at probability 0.5." These are completely different operations. One uses embedding cosine similarity; the other uses NLI entailment. Which is actually used? Are they combined? The text never explains.

### W3: Figure 3 Caption References Wrong Model (Severity: 3/5)
**Where:** Figure 3 caption, line 306
**Issue:** The caption says "Coverage is near-zero for all methods due to **GPT-2's** limited QA capability." The experiments section (Section 5.1, line 213) specifies "**Qwen2.5-7B-Instruct**." These are completely different models. The caption also calls this a "method comparison" but provides no actual numbers—only a TODO placeholder figure.

### W4: Algorithm 1 Pseudocode Does Not Match the Text (Severity: 4/5)
**Where:** Algorithm 1 vs. Section 4.3
**Issue:** Algorithm 1 line 180 says the lifted score for calibration is:
`1 - max_{c' != c_i^*} kappa_sigma(bars_phi_{c_i^*}, bars_phi_{c'})`
where `c_i^*` is "the correct cluster." But the text (Section 4.3, Equation 2) defines the lifted score as:
`min_{y' in [y]_s intersect {y_1,...,y_K}} s(x, y')`
where `s(x,y) = 1 - kappa_theta(phi(y), mu_x)` and `mu_x` is the kernel mean embedding of ALL K samples.
These are structurally different: one computes a contrast score between clusters; the other computes the minimum score within a cluster relative to the sample centroid. The algorithm and the theory are solving different problems. I could not implement SemCP from this paper.

### W5: Exchangeability Preservation Claim Is Underspecified (Severity: 3/5)
**Where:** Section 4.1, line 116 and Theorem 1 proof sketch, line 160
**Issue:** The paper claims the partition rule Π "is not data-adaptive; preserves exchangeability" (line 40) and that Π is "a deterministic function fixed before observing any data" (line 116). But line 116 also says "In our experiments, we instantiate Π as cosine-similarity thresholding at 0.7 in the MiniLM embedding space"—embedding-based clustering IS data-dependent because embeddings are computed from the specific response strings generated. I do not understand how a fixed rule produces different partitions for different instances without being data-dependent. If the rule is "cluster by NLI entailment," the partitions are still instance-dependent because different instances produce different response sets. The paper needs to be explicit about what "fixed" means here.

### W6: Coverage Constraint Optimization Is Unclear (Severity: 3/5)
**Where:** Section 4.2, line 132 and Algorithm 1 line 180
**Issue:** Line 132 says σ is chosen "on a held-out 20% subset of the training split (not the calibration split)." But Algorithm 1 calibrates on ALL calibration examples that are admissible, and σ is not mentioned in Algorithm 1's calibration loop. Is σ fixed from the held-out split before Algorithm 1 runs? If so, the optimization step is disconnected from the conformal calibration step. The dependency structure is: (training split) → held-out split → σ → calibration set → q-hat. This needs explicit statement, not buried prose.

### W7: 33% Set Size Reduction Claim Is Unverifiable (Severity: 4/5)
**Where:** Abstract (line 13), Section 7 (line 99)
**Issue:** The paper claims "33% smaller set sizes than the strongest string-level baseline on SQuAD" but Table 1 is all TODO_NUM. I cannot evaluate whether this is real. Section 7 also references "13.35 vs. 19.89 for Token-CP" but these specific numbers appear nowhere in the visible tables—only in prose. This reads as speculative claim dressed as empirical result.

### W8: "Near-Zero Coverage" Contradicts Set-Size Claims (Severity: 3/5)
**Where:** Section 7, line 351 and Discussion, line 99
**Issue:** The paper says "near-zero coverage for all methods due to GPT-2's limited QA capability" (Fig 3 caption) AND "33% set size reduction" (Section 7, line 99). Set size reduction means nothing if coverage is near-zero—a conformal set that always predicts the empty set has set size 0 and 0% coverage. These two claims are contradictory: you cannot simultaneously claim a method produces meaningfully smaller sets AND that coverage is near-zero because of generator quality. Which is the real result?

### W9: Abstract Claims Code Released; Checklist Says It Will Be Released (Severity: 2/5)
**Where:** Abstract (line 27) vs. NeurIPS checklist item 5 (line 415)
**Issue:** Abstract says "Code and run logs are released for reproducibility." Checklist item 5 says "Code and experiment scripts will be released upon publication." These are contradictory statements. One is a lie. If code is not released, reproducibility is zero regardless of what the paper says.

### W10: Notation Overload Without Worked Example (Severity: 2/5)
**Where:** Section 4 (passim), Theorem 1 proof sketch
**Issue:** I counted 20+ symbols in Section 4 alone without a single worked example. The paper defines quotient spaces, kernel mean embeddings, lifted scores, admissibility events, and exchangeability all in quick succession. A single concrete example—showing one prompt, K=3 samples, how the equivalence classes form, how the kernel score is computed, and what the conformal set looks like—would make everything in Section 4 click into place. Without it, the method section reads like a theorem checklist.

---

## Per-Rubric-Dimension Scores

| Dimension | Score | Calibration Anchor |
|-----------|-------|-------------------|
| **Originality / Novelty** | 7/10 | Substantial conceptual advance: quotient-space conformal prediction is a genuinely new framing. The kernel-based nonconformity scores are the most novel component. |
| **Soundness** | 3/10 | The theory appears correct but the experiments do not exist. Even if they did, Algorithm 1 does not match the stated theory (W4). Methodology cannot be evaluated. |
| **Significance** | 6/10 | The idea matters—if it works. Set-size reduction and semantic coverage are real problems. But downstream applications are not evaluated, limiting practical impact. |
| **Clarity** | 5/10 | Major clarity issues: the partition method is inconsistent across sections, Algorithm 1 contradicts the text, and Figure 3 caption references the wrong model. |
| **Reproducibility** | 2/10 | No code released (contradiction in paper). No real experimental results. Cannot reproduce without both. |
| **Contextualization vs Prior Work** | 7/10 | Strong related work. SemCP is clearly positioned as complementary to ConU/SAFER/LofreeCP/TECP. The taxonomy in Section 3 is well-organized. |
| **Ethical / Broader Impact** | 6/10 | Adequate boilerplate. No specific negative impacts identified. The paper does not engage with risks of "meaning-level" guarantees (e.g., what if NLI is wrong?). |

**Weighted Average: 5.1/10 (Reject territory)**

---

## Pointed Questions for the Authors

**Q1.** Your Section 4.1 says the partition Π uses "cosine-similarity thresholding at 0.7 in the MiniLM embedding space" but Section 5.1 says it uses "bidirectional entailment under DeBERTa-v2-xlarge-MNLI binarised at 0.5." Which is the actual method used in experiments? If both are used, in what order and with what combination rule?

**Q2.** Algorithm 1 (line 180) computes the lifted calibration score as `1 - max_{c' != c_i^*} kappa_sigma(bars_phi_{c_i^*}, bars_phi_{c'})`—a contrastive between-cluster score. But the theory in Section 4.3 defines it as `min_{y' in [y]_s} s(x, y')`—a within-cluster minimum score. These are fundamentally different. Which is SemCP?

**Q3.** What does "fixed partition rule Π" mean in terms of exchangeability? If Π is applied to each instance's response set independently, and different instances produce different equivalence classes, how is the partition independent of the data? Is the argument that "the rule is fixed, the partitions are data-dependent, but the rule is deterministic"? If so, this should be stated explicitly.

**Q4.** In Theorem 1, the coverage guarantee is conditional on the admissibility event A = {true meaning in sampled set}. But you also say marginal coverage is upper-bounded by p_A. If p_A is often much less than 1−α (your Section 5 reports empirical admissibility rates via TODO_NUM), then the conditional guarantee is the only meaningful guarantee. Why not always condition from the start and drop the marginal coverage framing?

**Q5.** The paper claims "33% set size reduction" but also "near-zero coverage due to GPT-2's limited QA capability." If coverage is near-zero, set size is irrelevant. Please clarify: are the 33% and near-zero claims from the same experiments, or from different experiments? If they are from different experiments (e.g., the 33% claim is hypothetical), this should be stated explicitly.

**Q6.** In Section 4.2, line 132: "With a capable model, the constraint becomes active." Which model is "capable" enough? Qwen2.5-7B-Instruct, or only larger models? What is the minimum admissibility rate required for the coverage constraint to be feasible?

**Q7.** The calibration threshold q-hat in Algorithm 1 (line 185) is computed only over admissible calibration points (those where the correct meaning was sampled). This means q-hat is computed from a biased subset of calibration data. Is this selection bias addressed in the theory? Does it affect the coverage guarantee?

---

## Falsifiability Test

**What evidence would change my decision?**

- **Strong Accept:** Real experiments with table of numbers showing SemCP achieves conditional coverage ~0.89 on both datasets with Qwen2.5-7B-Instruct, AND set size at least 20% smaller than the best string-level baseline at matched coverage. Algorithm 1 must match the theory.

- **Accept:** Real experiments with some positive results, even if not as strong as claimed. The partition method inconsistency must be resolved (either NLI or cosine thresholding, not both).

- **Borderline:** Real experiments but weak or mixed results. Algorithm-theory mismatch must be explained or fixed.

- **Reject:** Any of the following: (a) experiments are still TODO_NUM; (b) results show no set-size advantage; (c) coverage is genuinely near-zero even with Qwen2.5-7B-Instruct (which would mean the method does not work on the stated model); (d) the Algorithm 1 vs. theory mismatch is not resolved.

- **Strong Reject:** The partition method is irreconcilably inconsistent between theory and experiments; or code is confirmed not to exist and results are shown to be fabricated (TODO_NUM placeholders submitted as real numbers).

**My Falsifiability Standard:** I would need to see actual table numbers (not TODO_NUM) with conditional coverage at the expected level (~0.89), a verified 20%+ set size reduction over the strongest baseline, and a corrected Figure 3 caption matching the actual model used (Qwen2.5-7B-Instruct, not GPT-2). Without these, I cannot evaluate the paper.

---

## Confidence

**3/5**

I am confident in my identification of the structural issues (TODO_NUM placeholders, figure-model mismatch, partition inconsistency, Algorithm-theory mismatch). I am less confident in my overall assessment because the paper's core contribution—the empirical results—does not exist in any readable form. If the experiments were real and the numbers were strong, several of my weaknesses (especially W1, W2, W3, W7) would disappear or diminish significantly. My assessment is a snapshot based on what is actually written, not what might be intended.

---

## Decision

**Strong Reject**

The paper as submitted is incomplete. Every empirical result is a placeholder. The theory is present but has a critical Algorithm-theory mismatch (Algorithm 1 vs. Section 4.3). The figure captions are internally inconsistent (GPT-2 vs. Qwen2.5-7B-Instruct). The partition method is described two different ways across sections. A paper cannot be accepted—let alone reviewed properly—when none of its empirical claims are materialized. If this were a workshop paper with only theory, I would say Borderline (theoretical contribution is real but needs empirical validation). For a full NeurIPS submission with "33% set size reduction" as a headline claim, this is Unacceptable.

---

*— The Naive Reader*