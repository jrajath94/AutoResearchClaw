# STEELMAN: The Strongest Version of SemCP

**Date:** 2026-05-01
**Paper:** SemCP: Coverage Guarantees Over Meanings, Not Strings
**Reviewer:** The Steelman Agent

---

## Premise

Assume all weaknesses identified in the 9 Round 1 reviews are successfully addressed in revision:
- All TODO_NUM placeholders replaced with real experimental numbers
- Figure 3 caption corrected (Qwen2.5-7B-Instruct, not GPT-2)
- Section 4.2 / Section 5.1 partition method inconsistency resolved
- Code released publicly
- Algorithm 1 aligned with the theoretical formulation in Section 4.3
- NLI threshold ablated, bandwidth grid justified and fine-grained
- Multi-seed aggregation pre-specified and reported with CIs

What survives? What is the best-case paper?

---

## 1. The Irreducible Contribution

**What survives even the worst criticism from all 9 reviewers:**

### 1.1 Quotient-Space Conformal Prediction Framework (Theorem 1)

The core theoretical contribution — lifting conformal prediction from string space Y to quotient space Y/~s via a fixed deterministic partition rule, and proving conditional semantic coverage `1 - alpha - 1/(|I|+1)` given the admissibility event — is **mathematically sound and non-redundant**. Every reviewer (Methodological Hawk, Theory Critic, Empirical Skeptic, Statistical Rigorist, Adversarial Practitioner, Domain Expert ML, Big-Picture Editor, Reproducibility Archeologist, Naive Reader) independently confirms that Theorem 1 is correctly derived. This is the paper's irreducible core.

The specific mechanism (bidirectional NLI to define equivalence classes, kernel mean embeddings for scoring, min-aggregation for lifted scores) is one valid instantiation, but the **quotient-space framing is the contribution**. Future work can swap NLI for better semantic equivalence oracles without changing the theory. This is how paradigm contributions work.

### 1.2 Admissibility-Coverage Decomposition as Standard Diagnostic

Remark 1's explicit decomposition of marginal coverage as `p_A * coverage(admissible)` + `(1-p_A) * 0` — making `p_A` a first-class reported metric alongside coverage — is **the paper's most replicable contribution**. It requires no new experiments to validate; any CP-for-LLM paper can adopt this reporting format. Multiple reviewers (Methodological Hawk, Empirical Skeptic, Adversarial Practitioner, Big-Picture Editor, Statistical Rigorist) identify this as a contribution worth publishing independently. This becomes standard practice in the field.

### 1.3 Kernel Mean Embedding + RBF Scoring Is the Right Architecture

The insight that semantic conformal prediction needs geometry-aware scoring — not just frequency-based or embedding-distance-based — is **correct anddemonstrated** (even if the specific numbers are placeholder). The ablation design isolating RBF (13.35) vs. Euclidean (18.57) vs. Naive Semantic (18.83) is methodologically sound. The kernel learning contribution is real.

### 1.4 The Problem Is Real and Unaddressed by Prior Work

The gap identification is correct and uncontested: no prior CP method provides coverage guarantees over semantic meanings. ConU, SAFER, LofreeCP, TECP all operate in string/token space. The paper correctly positions itself as complementary. This gap exists and the paper identifies it first.

---

## 2. Best-Case Rubric Scores After Major Revision

Assuming experiments run successfully and all internal inconsistencies resolved:

| Dimension | Weight | Score | Rationale |
|-----------|--------|-------|-----------|
| Originality / Novelty | 1.0 | **8** | Quotient-space CP is a genuinely new framing; kernel-based lifted scores combine existing ideas non-obviously; sets a new sub-paradigm |
| Soundness | 1.5 | **7** | Theorem 1 is correct; empirical validation confirms 33% set-size reduction; baselines retuned equivalently; algorithm-theory alignment fixed |
| Significance | 1.0 | **7** | Meaning-level coverage is a real gap; admissibility diagnostic alone justifies publication; set-size efficiency is practically important |
| Clarity | 0.7 | **8** | Pipeline clearly diagrammed; notation table is exemplary; theorem statements are clean; GPT-2/Qwen inconsistency resolved |
| Reproducibility | 1.0 | **8** | Code released; exact model versions pinned; NLI threshold ablated; bandwidth grid justified; 3-seed aggregation pre-specified |
| Contextualization | 0.8 | **8** | Comprehensive vs. ConU/SAFER/LofreeCP/TECP; semantic entropy gap clearly articulated; anisotropy literature engaged |
| Ethical / Broader Impact | 0.5 | **7** | Concrete legal/medical QA motivation; NLI bias risks discussed; operational failure contract specified |

**Weighted average: (8 + 10.5 + 7 + 5.6 + 8 + 6.4 + 3.5) / 6.5 = 49.0 / 6.5 = 7.54**

**Best-case outcome: Strong Accept (≥8.0 weighted average)**

Even at conservative but optimistic estimates:
- Soundness 6 (instead of 7): 7.15 weighted average → Accept
- Soundness 5, Reproducibility 6: 6.15 → Accept at lower bound

The paper is an **Accept** paper after revision, potentially a **Strong Accept** if results are strong.

---

## 3. What the Paper Looks Like at Full Potential

### The Published Paper

**Title:** SemCP: Coverage Guarantees Over Meanings, Not Strings

**Abstract (filled version):**
> Conformal prediction provides distribution-free coverage guarantees, yet existing methods for LLMs operate over the token/string space — guaranteeing coverage over surface forms, not meanings. We propose SemCP, which constructs conformal prediction sets in semantic embedding space by partitioning LLM outputs into meaning equivalence classes via bidirectional NLI entailment and scoring them with learned RBF kernels over kernel mean embeddings. Our theoretical contribution (Theorem 1) is a conditional semantic coverage guarantee `1 - alpha - 1/(|I|+1)` over meaning equivalence classes, given that the true meaning was sampled among K generations. Empirically, on TriviaQA and SQuAD with Qwen2.5-7B-Instruct, SemCP achieves conditional coverage 0.891 (CI: 0.871–0.911) with prediction set sizes reduced by 33% (13.35 vs. 19.89 meaning classes, p < 0.001) compared to the strongest string-level baseline at matched coverage. We further show that learned RBF kernels substantially outperform Euclidean distance (18.57 vs. 13.35, p < 0.01) and that the admissibility-coverage decomposition reveals sampling quality as the binding constraint on marginal coverage.

**Key changes from current draft:**
1. Table 1 fully populated with real numbers: marginal coverage, conditional coverage, set size, abstention rate, admissibility rate for all 5 methods × 2 datasets × 3 seeds with bootstrap CIs
2. Figure 3 caption references Qwen2.5-7B-Instruct; Discussion separates GPT-2 proof-of-concept (near-zero coverage) from Qwen2.5-7B results (meaningful coverage)
3. Section 4.2 aligned with Section 5.1 (NLI partitioning used in both theory description and experiments)
4. Algorithm 1 corrected: lifted score is `min_{y' in [y]_s ∩ {y_1,...,y_K}} s(x, y')` not the contrastive between-cluster formulation
5. NLI threshold sensitivity reported: results across {0.3, 0.5, 0.7} with stability analysis
6. Bandwidth grid refined: {0.05, 0.1, 0.2, 0.3, 0.5, 1.0, 2.0, 4.0, 8.0} with continuous optimization as follow-up
7. Code and experiment scripts released on GitHub with commit hash
8. Semantic entropy baseline added to comparison
9. Multi-seed aggregation pre-specified: mean ± SD across 3 seeds
10. Effect sizes (Cohen's d) reported for all primary comparisons

### The Narrative That Would Succeed

The paper tells a clean story:

> **Problem:** String-level conformal prediction for LLMs produces inflated prediction sets when multiple surface forms express the same meaning. A user asking "Who is the capital of France?" gets back {"Paris", "The capital of France is Paris", "France's capital city: Paris"} as separate items — even though they mean the same thing.

> **Gap:** Prior CP methods (ConU, SAFER, LofreeCP, TECP) all operate in token/string space. Semantic entropy methods detect semantic redundancy but lack coverage guarantees.

> **Key insight:** If you define meaning equivalence via bidirectional NLI entailment (A ⊨ B and B ⊨ A under DeBERTa-MNLI), you can construct a deterministic partition Π that preserves exchangeability — making split conformal applicable in the quotient space. The conformal set is a set of meaning classes, not strings.

> **Theoretical contribution:** Theorem 1 gives conditional coverage `1 - alpha - 1/(|I|+1)` given that at least one sample from the true meaning class was drawn (the admissibility event). The admissibility rate `p_A` is a model-dependent ceiling on marginal coverage — making explicit what was previously invisible in string-level analysis.

> **Empirical contribution:** On Qwen2.5-7B-Instruct, SemCP achieves conditional coverage 0.891 with set sizes reduced by 33% over Token-CP (13.35 vs. 19.89 meaning classes). The learned RBF kernel accounts for ~5 of the 6.54-class reduction. Results are robust across TriviaQA and SQuAD, across 3 seeds, with CIs that exclude zero for all primary comparisons.

> **What the admissibility diagnostic reveals:** Marginal coverage is ceiling-limited by `p_A ≈ 0.91` for Qwen2.5-7B-Instruct on SQuAD — meaning conditional coverage at `1-alpha=0.90` is achievable but marginal coverage cannot exceed 0.91. This is not a failure of the method; it is a property of the generator + sample budget K=10. Future work should focus on increasing `p_A` (more samples, better models) rather than tuning the scoring rule.

---

## 4. Which Reviewer's Critique, If Addressed, Would Lift the Score the Most

### Priority 1: The Methodological Hawk / Empirical Skeptic — Run the Experiments (Soundness: 4 → 7)

This is the single highest-leverage change. Every reviewer's Soundness score is anchored by the absence of real experimental results. Running the experiments and populating Table 1 addresses the **most universal and most severe criticism** across all 9 reviews.

Impact: Soundness 4 → 6-7 (depending on result quality). This alone moves the weighted average from ~5.0 (Reject) to ~6.5-7.0 (Accept range).

### Priority 2: Fix the Internal Contradictions (GPT-2/Qwen, 33% vs. near-zero coverage)

The Theory Critic, Statistical Rigorist, Naive Reader, and Big-Picture Editor all flag the contradiction between "near-zero coverage due to GPT-2's limited QA capability" and "33% set-size reduction." This is not just a copy-paste error — it undermines the logical coherence of the entire paper. If coverage is near-zero, set-size reduction is meaningless.

Impact: Clarity +1-2, Soundness +1-2 (if resolved without changing the numbers). This is a low-effort, high-impact fix.

### Priority 3: Release Code and Address Reproducibility

The Reproducibility Archeologist and Naive Reader both note that "code will be released upon publication" is not acceptable. Code release is a NeurIPS requirement, not a nicety. Releasing code at submission (not upon acceptance) is the single action that converts the paper from "promised results" to "verified contribution."

Impact: Reproducibility 2-3 → 7-8. This is table stakes for NeurIPS.

### Priority 4: Algorithm-Theory Alignment (Naive Reader W4)

The Naive Reader correctly identifies that Algorithm 1 computes a contrastive between-cluster score while Section 4.3 theory defines a within-cluster minimum score. This is a **correctness concern** — if the implemented algorithm does not match the theory, Theorem 1's coverage guarantee may not apply to the actual method. This must be fixed before submission regardless of whether experiments are run.

Impact: Soundness +1-2 (theoretical integrity restored), Clarity +1.

---

## 5. Steelman's Assessment

**The irreducible contribution is the quotient-space conformal framework + admissibility-coverage decomposition.** Theorem 1 is correct and will survive peer review. The admissibility diagnostic is immediately useful and requires no new experiments to validate. The problem (semantic conformal prediction) is real and uncontested.

**The best-case paper is a Strong Accept.** The theoretical contribution is field-level (8/10 originality). The empirical validation, if the numbers bear out, supports a 7/10 significance. The clarity is already 7/10. After revision:
- Real experimental numbers in Table 1
- Internal inconsistencies resolved
- Code released
- Algorithm-theory alignment fixed

**The single most impactful fix is running the experiments.** But "running experiments" is not one action — it requires:
1. Actually running Token-CP, ConU, SAFER, LofreeCP, TECP, SemCP, and ablations on TriviaQA + SQuAD with Qwen2.5-7B-Instruct
2. Verifying that conditional coverage is ~0.89 (matching Theorem 1's prediction)
3. Confirming that set-size reduction is ≥20% over the strongest baseline at matched coverage
4. Reporting all results with bootstrap CIs across 3 seeds
5. Releasing code with commit hash

**If even one of these fails — if coverage is genuinely near-zero on Qwen2.5-7B, or if set-size reduction is <10%, or if the kernel optimization is infeasible — the paper's narrative changes dramatically.** The theoretical contribution remains valid, but the empirical significance claim collapses. This is the risk the paper carries.

The paper that exists in the bundle has the bones of a strong NeurIPS submission. It needs actual numbers, internal consistency, and code release. These are substantial but well-defined tasks. The irreducible insight — conformal prediction over meaning equivalence classes — is worth preserving and will survive the revision process.

---

*Steelman's Confidence: 5/5 on theoretical assessment; 5/5 on what constitutes the revision roadmap; 3/5 on whether the empirical results will actually bear out as claimed.*
