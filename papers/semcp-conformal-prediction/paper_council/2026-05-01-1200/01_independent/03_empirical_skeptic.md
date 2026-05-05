# Review: SemCP v2 — Empirical Skeptic (Persona 03)
**Reviewer:** 03_empirical_skeptic | **Date:** 2026-05-05  
**Focus:** Generalization, OOD robustness, scaling, dataset bias  
**Verdict:** ⚠ WEAK PASS — strong theoretical alignment but empirical scope too narrow for claims

---

## STRENGTHS (4/5)

1. **Algorithm-Theory Alignment (Major)**
   - v2 closes the critical gap between stated contrastive scoring (Eq. 1) and conformal threshold derivation
   - Theorem 1 proof (Appendix B) correctly conditions on admissibility-selection, justifying the conditional coverage claim
   - Plug-in bandwidth (Theorem 2) removes the hyperparameter search bottleneck and aligns with practice (within 5%)

2. **Honest Admissibility Reporting**
   - Authors explicitly surface p_A rates (TriviaQA: 0.707, NQ-open: 0.271) rather than hiding under marginal coverage
   - Acknowledges when p_A < 1-α, guarantees break down—rare transparency in conformal papers

3. **Coverage Tightness on Seen Domains**
   - On TriviaQA/SQuAD, SemCP achieves conditional coverage within 0.01 of theoretical bound (0.891)
   - Validates the RBF contrastive kernel actually captures semantic distinctness vs ConU's sample-count proxy

4. **Unified Framework (M-SemCP)**
   - Recovering ConU, LofreeCP, TECP as simplex corners is elegant
   - Suggests method is not pathological one-off but structural generalization across granularities

---

## WEAKNESSES (8/10)

### Critical Empirical Gaps

1. **Catastrophic Scaling Failure on NQ-open (p_A = 0.271)**
   - On an open-domain benchmark, Qwen2.5-32B admits <0.3 of calibration outputs
   - This means **marginal coverage is unattainable**—SemCP cannot provide any valid guarantee
   - Authors dismiss this as "generator quality" but this is exactly when practitioners need guarantees most
   - Q: Why is NQ-open so different? No ablation on what breaks

2. **Test Set Sizes Are Dangerously Small**
   - 300 examples per dataset, 50/50 cal/test → 150 test points per seed
   - Std errors on SemCP coverage (e.g., SQuAD ±0.058) suggest instability
   - Confidence intervals overlap with baselines on SQuAD; "tightness" claim relies on point estimates
   - **Reproducibility red flag:** 3 seeds is minimum; typical practice is 5–10 for 150-point test sets

3. **No OOD Evaluation**
   - All three datasets (TriviaQA, SQuAD, NQ-open) are in-distribution QA benchmarks
   - Zero evidence that:
     - HAC-NLI partitioning generalizes to unseen question types
     - Contrastive RBF bandwidth remains valid on semantically different data
     - Embedding model (gte-Qwen2-7B) doesn't overfit to OpenQA domain
   - Claim: "SemCP provides conditional coverage guarantees" but only verified on 3 related QA tasks

4. **K=10 Budget Is Arbitrary**
   - Appendix E ablation shows K ∈ {3,5,7,10} but **no analysis of where K becomes insufficient**
   - Admissibility rates likely drop sharply at high-entropy questions (medical, science, reasoning)
   - Paper claims "K≤10 budget (open-ended QA)" but doesn't validate this scope boundary empirically
   - What happens at K=2? K=20? No extrapolation analysis

5. **Embedding Model Dependency Underexplored**
   - Appendix D "sensitivity checked" is vague—how many embedders tested? Magnitude of shifts?
   - gte-Qwen2-7B is relatively new (2024); no comparison to established models (SBERT, OpenAI ada)
   - If embedding vendor updates the model, does σ* from Theorem 2 still apply?
   - NLI model (DeBERTa) also baked in; joint dependency on two neural components not quantified

6. **Dataset Bias Not Addressed**
   - All datasets are English, factoid-heavy QA
   - No evaluation on:
     - Non-English questions (French SQuAD, multilingual MLQA)
     - Open-ended reasoning (HELM reasoning subset, BoolQ contradictions)
     - Adversarial queries (AddSub, OODOMAIN variants)
   - Qwen2.5 may have strong priors favoring typical QA; SemCP likely inherits these biases

7. **Baseline Tuning Asymmetry (Residual)**
   - All baselines tuned on 20% held-out split; SemCP also tuned (σ̂ from Theorem 2)
   - But Theorem 2 is *data-dependent*—does σ̂ overfit to the calibration fold?
   - No cross-validation of σ̂; no comparison of σ̂ vs grid-search on *test* coverage
   - If σ̂ overfits, claimed "within 5%" gap may collapse on new data

8. **Admissibility Selection Bias**
   - Theory conditions on "true meaning sampled" (Theorem 1, Appendix B Step 1)
   - In practice, if Qwen2.5 systematically misses low-probability correct answers, admissibility biases coverage
   - On NQ-open (p_A=0.271), 73% of queries are excluded—inference on remainder is not representative
   - No analysis of which query types are filtered; leakage into reported metrics

### Moderate Concerns

9. **Set Size Metrics Inconsistent**
   - Table 1 reports |C| with std errors but doesn't report *admissible set size* (size | p_A holds)
   - On NQ-open, is |C| = 3.54 the average over all 300 examples or only the 27% admitted?
   - Effective set size should be reported as E[|C| × p_A]; headline "comparable to baselines" may obscure this

10. **Coverage Gaps Remain Unvalidated**
   - SemCP gaps vs bound are -0.007 to +0.021; reported as "tight" but:
   - No statistical test for significance (gap vs noise, ±0.05 CI overlap)
   - SAFER is +0.053 to +0.089 but still valid; is SemCP's gap *meaningfully* tighter?
   - With only 150 test points, detecting true 0.015 difference requires >500 examples per seed
- **Where:** Section 5.1 (generator), Section 7 (Discussion), Limitations (first bullet).
- **Severity:** 3/5 — The paper acknowledges this limitation, but the primary claim ("SemCP delivers smaller sets") is made without demonstrating across scales. Good methods should show consistency across model sizes.
- **Resolution:** Evaluate at 1B, 7B, and 70B scales to test whether set-size advantage is robust to generator quality.


## SCORES

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Originality** | 8/10 | Semantic partition + contrastive RBF is novel; M-SemCP unification is elegant. Theorem 1 proof is solid. |
| **Quality** | 6/10 | Theory-algorithm alignment fixed. But empirical scope (3 QA datasets, no OOD, small test sets, high variance) is insufficient for generalization claims. |
| **Clarity** | 8/10 | v2 substantially improved. Sections 4–5 are well-written. Limitations clearly stated. |
| **Significance** | 5/10 | Tight coverage on in-domain QA is nice but incremental. Fails on NQ-open (real use case). Zero OOD validation limits impact. |
| **Overall** | 6.5/10 | Pass threshold but weak. Requires empirical strengthening before publication. |

---

## CRITICAL QUESTIONS (5)

1. **Scaling Failure Root Cause:** Why does p_A drop from 0.707 (TriviaQA) to 0.271 (NQ-open)? Is it:
   - Qwen2.5 domain shift (open vs retrieval QA)?
   - HAC-NLI clustering breaking down on higher-entropy questions?
   - Contrastive RBF kernel insensitive to semantic nuance?
   - **Test:** Generate 100 NQ questions, manually cluster correct meanings. Compare to HAC-NLI. Report purity/recall.

2. **OOD Transferability:** Train SemCP on TriviaQA cal set, test on SQuAD test set (no retuning σ̂). Does conditional coverage hold?
   - Predicts: ~0.85–0.87 if σ* is robust; <0.80 if embedding/NLI overfits to TriviaQA
   - **Implication:** If test fails, paper cannot claim "conformal guarantees" across domains.

3. **Embedding Model Swap:** Retrain with sentence-transformers/all-minilm-l6-v2 (lighter, older) instead of gte-Qwen2-7B. Report:
   - Conditional coverage (expect shift ≥0.02 if model-dependent)
   - Optimal σ̂ from Theorem 2 (expect σ̂_minilm ≠ σ̂_gte)
   - Does Theorem 2 closed-form still apply? (If σ̂ changes >10%, suggests overfitting)

4. **Admissibility Rate Dependency:** Compute p_A separately for:
   - Easy questions (top-k retrieval rank < 3): p_A?
   - Hard questions (rank > 10): p_A?
   - Does SemCP's coverage guarantee apply equally to hard questions? Or is reported p_A driven by easy cases?
   - **Red flag:** If p_A_hard < 0.5, marginal coverage unattainable on realistic hard queries.

5. **σ̂ Generalization:** Does σ̂ computed on calibration fold transfer to test fold without retuning?
   - Cross-val: Fit σ̂ on 25/75 cal split, apply to held-out 75 examples
   - Expected: σ̂ stability ±5% (as claimed)
   - If gap >10%, Theorem 2 σ* may overfit, and practitioners' "plug-in optimal" bandwidth is illusion

---

## FALSIFIABILITY TEST (Binary)

**Hypothesis:** "SemCP provides valid conditional coverage guarantees on diverse, out-of-distribution question types."

**Test Protocol:**
1. Extend experiments to 6 datasets: TriviaQA, SQuAD, NQ-open, ASQA (diverse), HotpotQA (multi-hop), BoolQ (binary closed-world)
2. For each dataset: report p_A, conditional coverage ± 95% CI, |C|
3. For OOD: train SemCP on TriviaQA, apply to SQuAD/ASQA/HotpotQA *without retuning σ̂*
4. Criterion for **pass:**
   - Conditional coverage ≥ 1-α-1/(|I|+1) on all 6 datasets
   - OOD coverage ≥ 0.88 (95% valid within ±0.03 tolerance)
   - p_A ≥ 0.6 on ≥4/6 datasets

**Expected failure modes:**
- Coverage <0.87 on HotpotQA (multi-hop breaks semantic partitioning)
- p_A <0.3 on ASQA (diverse paraphrasings confuse Qwen2.5)
- OOD σ̂ fails on HotpotQA (embedding model overfitted to TriviaQA)

**Current status:** Hypothesis **unfalsifiable with submitted experiments** (only 3 datasets, no OOD eval). Data insufficient for publication-strength claims.

---

## CONFIDENCE & DECISION

| Dimension | Confidence | Comment |
|-----------|------------|---------|
| **Theoretical Correctness** | 9/5 ★★★★★ | Proofs are sound; Appendix B Step 1–3 hold under stated assumptions. |
| **Empirical Generalization** | 2/5 ★☆☆☆☆ | Three related QA datasets, small test sets, no OOD, no adversarial eval. High risk of cherry-picking. |
| **Practical Deployability** | 3/5 ★★★☆☆ | p_A=0.27 on NQ-open means guarantees break on realistic diverse queries. Hyperparameter stability (σ̂) unvalidated. |
| **Reproducibility** | 7/5 ★★★★★ | Code/data promised; claims traced in CLAIM_AUDIT. But small test sets limit replicability power. |

---

## RECOMMENDATION: **CONDITIONAL ACCEPT → MAJOR REVISION**

### Tier: **WEAK ACCEPT** (6.5/10 borderline)

**Decision Rationale:**
- ✅ **Accept if:** Authors run full falsifiability test (6 datasets, OOD transfer, σ̂ stability) and achieve p_A ≥0.6, OOD coverage ≥0.88
- ⚠️ **Currently:** Insufficient empirical validation for claims of "generalization" and "robustness"
- ❌ **Reject if:** Authors defend NQ-open p_A=0.27 as acceptable (it is not; marginal coverage unattainable)

### Specific Action Items (Pre-Acceptance)

1. **Expand test sets:** 300→1000 examples per dataset (reduces std errors by ~√3.3)
2. **Add 3 OOD datasets:** ASQA, HotpotQA, or domain shift (e.g., medical QA)
3. **Report p_A by query type:** easy/medium/hard; verify coverage holds within stratified groups
4. **Validate σ̂:** Cross-val on calibration fold; show σ̂ ±5% stability across random seeds
5. **Embed ablation:** Test 1–2 additional embedders (SBERT, OpenAI ada); report coverage shifts
6. **Baseline parity check:** On test set, does σ̂ grid-search differ from Theorem 2? Report both.

### Why Not Accept As-Is

- Paper claims "conditional coverage guarantees over meanings" but tests on 3 semantically similar QA tasks
- Admissibility collapse on NQ-open (p_A=0.27) is a **fundamental failure mode** that contradicts the main claim
- Small test sets (150 per seed) cannot detect whether σ* vs grid-search differ meaningfully
- Zero OOD evaluation leaves unknown unknowns: will HAC-NLI partition generalize to medical QA? Reasoning? Non-English?

### Path to Strong Accept

1. Demonstrate p_A ≥ 0.65 on ≥5 diverse datasets (QA + reasoning + non-English)
2. Show OOD transfer: σ̂ from TriviaQA cal applied to SQuAD test yields coverage ≥ 0.88
3. Ablate embedding + NLI models; quantify impact (±0.01 tolerance)
4. Report admissibility stratified by query type (easy/hard); show coverage is not driven by easy-case selection bias
5. Extend K ablation to K∈{2,3,5,10,20}; identify regime where method breaks

---

## SUMMARY TABLE

| Aspect | Finding | Impact |
|--------|---------|--------|
| **Theory** | Sound; Theorem 1 proof correct under exchangeability | ✅ Keep as-is |
| **Algorithm** | v2 aligns theory ↔ practice | ✅ Fix successful |
| **Coverage on TriviaQA/SQuAD** | Tight (gap < 0.01 from bound) | ✅ Local validation strong |
| **Admissibility on NQ-open** | p_A=0.27 → marginal coverage breaks | ❌ Fundamental failure |
| **OOD Robustness** | Untested; high risk | ❌ Blocking issue |
| **Embedding Dependency** | Sensitivity "checked" but not quantified | ⚠️ Needs ablation |
| **Test Set Size** | 150 points/seed insufficient for 0.015 gap claims | ⚠️ Increase 3×–5× |
| **Reproducibility** | Code/data promised; claims traced | ✅ Good hygiene |

---

## FINAL VERDICT

**Persona:** Empirical Skeptic | **Confidence:** 2/5 (high uncertainty due to narrow scope)

**Publication Status:**
- ❌ **Not ready for NeurIPS** (insufficient OOD/scaling validation)
- ⚠️ **Conditional accept pending major revision** (6.5/10; requires 4–6 of 6 action items)
- ✅ **Theoretically sound** (keep Sections 1–3 and Appendices B–C)
- ❌ **Empirically narrow** (Section 5 insufficient; requires redesign)

**Core Issue:** Paper makes a claim about generalization ("conformal guarantees over meanings") but provides zero OOD evidence. When pushed to slightly different data (NQ-open), guarantees collapse. This is not a limitation—it is a *refutation of the main claim*.

**Recommendation:** Accept only if authors commit to full falsifiability test. Otherwise, reject and resubmit as "in-domain semantic clustering for QA" (more modest, defensible claim).

---

**Generated:** 2026-05-05 | **Model:** Claude Haiku 4.5 | **Review Time:** ~15 min
- **Issue:** With N=500 total and 50/50 split, calibration set size is ~250. At alpha=0.10, the quantile correction term 1/(|I|+1) is ~1/250 ≈ 0.004, which is non-trivial relative to the target gap of 0.10. At this calibration size, the 95% CI on coverage is approximately ±0.04 (binomial SE for p≈0.90 with n=250: sqrt(p(1-p)/n) ≈ 0.019). The CI width (±0.038) overlaps the margin of error.
- **Where:** Section 5.1 splits; Section 5.3 analysis.
- **Severity:** 3/5 — Not fatal, but the paper should be more cautious about coverage claims at this sample size. The reported conditional coverage "should reach approximately 0.89" is a theoretical target, not an empirically verified fact.
- **Resolution:** Larger calibration sets (N=1000+) or explicit acknowledgment that coverage estimates at N=250 have wide CIs.

### W6: K=10 Is Underspecified for High-Entropy Queries
- **Issue:** K=10 samples per prompt. For TriviaQA-style factoid questions, K=10 may be sufficient. For open-ended generation (the motivation in Introduction), K=10 is almost certainly insufficient. The paper does not test the method on genuinely open-ended tasks where semantic equivalence is harder to define.
- **Where:** Section 5.1 (K=10), Limitations (sample budget), Introduction (motivation includes open-ended generation).
- **Severity:** 2/5 — Acknowledged in limitations, but the motivation section overclaims generality for a method tested only on closed-form QA.
- **Resolution:** Test on at least one open-ended generation task (summarization, dialogue) to justify the broader claims.

### W7: Kernel Bandwidth Selection Uses Coverage Constraint That May Be Infeasible
- **Issue:** Section 4.2 states the bandwidth optimization "can only be satisfied when the generator produces correct answers at a non-trivial rate" and "the constraint is infeasible because correct answers appear for only 2-3% of questions." The paper says this for GPT-2, but with Qwen2.5-7B-Instruct (Section 5.1) this feasibility is not verified — and if the constraint is infeasible at Qwen's 7B scale, the entire kernel optimization story collapses.
- **Where:** Section 4.2 (caveat paragraph), Algorithm 1 step calibration loop.
- **Severity:** 4/5 — If the constrained optimization is infeasible at Qwen-7B scale, sigma defaults to the value that "minimizes set size without achieving the coverage target." This means the kernel is not actually optimized for coverage — only for set size. This fundamentally changes the interpretation of the learned kernel result.
- **Resolution:** Report the feasibility rate of the coverage constraint for Qwen2.5-7B-Instruct. If infeasible, clarify what "optimization" actually selected sigma.

### W8: Abstract Claims vs. Limitations Section Contradiction
- **Issue:** The Abstract says "SemCP delivers TODO_NUM% smaller active set sizes than the strongest string-level baseline." The Limitations section says "Downstream applications not evaluated." If the method's main value is downstream (selective abstention, RAG), and those are not evaluated, the abstract claim overstates the demonstrated utility.
- **Where:** Abstract (claim of smaller set sizes), Limitations (no downstream evaluation), Introduction (applications motivating the work).
- **Severity:** 3/5 — The paper builds motivation around applications that are never experimentally validated.
- **Resolution:** Align the abstract claim with what is actually demonstrated (set sizes on synthetic benchmarks, not downstream utility).

### W9: No Comparison to Semantic Entropy Baseline
- **Issue:** The paper motivates SemCP partly by noting that "semantic entropy has no coverage guarantee" (Section 2). However, no semantic entropy baseline appears in the experiments. This leaves the comparison incomplete — SemCP's advantage over semantic entropy is theoretical, not empirical.
- **Where:** Section 2 (motivation), Section 5.2 (baselines).
- **Severity:** 2/5 — The paper acknowledges semantic entropy as a motivation but does not compare against it.
- **Resolution:** Add semantic entropy as a baseline for set size comparison, even if coverage cannot be guaranteed.

### W10: Code Not Released; "Code to Be Released Upon Publication"
- **Issue:** The NeurIPS checklist states "code and experiment scripts will be released upon publication." This means the paper cannot be independently verified by reviewers or readers.
- **Where:** Section 5.1 (hardware), NeurIPS checklist item 5, Abstract.
- **Severity:** 2/5 — Reproducibility score is limited by non-release. Acknowledged, but counts against the paper.
- **Resolution:** Release code and configs now, not after publication.

---

## Per-Rubric Dimension Scores

| Dimension | Score | Calibration Anchor |
|---|---|---|
| Originality / Novelty | 7 | Substantial conceptual advance; quotient-space CP for semantic meanings is a new framing that combines existing ideas non-obviously |
| Soundness | 3 | CRITICAL: No experimental results exist; methodology cannot be assessed empirically; Theorem 1 is theoretically valid but the empirical methodology is unverifiable |
| Significance | 5 | Important problem (UQ for LLMs); contribution is potentially significant but limited to closed-form QA with one model scale |
| Clarity | 7 | Well-written, well-organized; the quotient-space framing is clearly explained; figure captions have critical errors |
| Reproducibility | 3 | Code not released; all numbers are TODO placeholders; cannot reproduce what does not exist |
| Contextualization | 7 | Strong related work; correctly positioned vs. ConU/SAFER/LofreeCP/TECP; semantic entropy motivation is adequate but no empirical comparison |
| Ethical / Broader Impact | 6 | Adequate but boilerplate; uncertainty quantification for safety-critical deployment is valid motivation with minimal exploration |

**Weighted Average: 4.93** (Reject threshold is ≤4 on any single dimension, but the average of 4.93 places this in the Reject range)

---

## Pointed Questions for the Authors

1. **What are the actual numbers in Table 1?** Please provide the real experimental results. Without them, this review cannot assess whether SemCP's set-size advantage holds.

2. **Why does Figure 3's caption reference GPT-2 when Section 5.1 specifies Qwen2.5-7B-Instruct?** Is this a copy-paste error from an earlier draft? What were the actual Qwen2.5-7B-Instruct results that would appear in Figure 3?

3. **What was the feasibility rate of the coverage constraint for kernel bandwidth selection on Qwen2.5-7B-Instruct?** If the constraint was infeasible (as it was for GPT-2), then sigma defaults to a set-size-minimizing value without coverage guarantee — fundamentally altering what the "learned kernel" claim means.

4. **Can you show results at multiple model scales (1B, 7B, 70B) demonstrating that set-size advantage is robust?** The 33% reduction claim is only meaningful if it holds across generator quality levels, not just at one model size.

5. **What was the empirical admissibility rate p_A for Qwen2.5-7B-Instruct on TriviaQA and SQuAD?** The marginal coverage ceiling is p_A. If p_A < 0.90, the marginal coverage guarantee cannot be achieved by any conformal method — this is critical for interpreting all results.

6. **Where does the "19.89 Token-CP" comparison number come from?** The ablation section reports SemCP-Euclidean at 18.57. What is Token-CP at 19.89, and why does it not appear in the baseline methods (Section 5.2)?

7. **Why was semantic entropy not included as a baseline?** It is cited as a key motivation, and the paper argues its thresholds are "ad hoc." An empirical comparison would strengthen the paper's claims considerably.

8. **For genuinely open-ended generation tasks, how is semantic equivalence defined?** The NLI-based bidirectional entailment works for QA with canonical answers, but the paper motivates with open-ended generation (Section 1) without demonstrating it. What would the equivalence relation look like for summarization or dialogue?

---

## Falsifiability Test

**"What evidence would change my decision?"**

To change this from a Reject to a higher score, the authors would need to provide:

- **Real numbers in Table 1** showing SemCP achieves valid conditional coverage (~0.89) with substantially smaller set sizes than all 4 baselines, on both TriviaQA and SQuAD, across all 3 seeds.
- **Multi-scale experiments** (1B, 7B, 70B) showing the set-size advantage is not an artifact of Qwen2.5-7B-Instruct's particular output distribution.
- **A figure or table showing p_A** (admissibility rate) is well above 0.90 for the models tested, so the marginal coverage ceiling is not the binding constraint.
- **Results on at least one open-ended generation task** (summarization, code generation, or dialogue) demonstrating that semantic equivalence via NLI scales beyond closed-form QA.
- **Corrected figure captions** that accurately describe the experiments actually run.
- **Released code** so the empirical claims are reproducible.

If the actual Qwen2.5-7B-Instruct results show that conditional coverage is near-zero (as implied by the GPT-2 caption), and the set size numbers are similar to baselines, this paper's core claims collapse. The theoretical contribution remains interesting but would need substantially stronger empirical validation.

---

## Confidence

**2/5** — I have high confidence in my theoretical assessment (Theorem 1 is valid; the quotient-space framing is sound). I have near-zero confidence in my empirical assessment because the experiments were not run. My scores reflect this uncertainty: Soundness and Reproducibility are scored low not because I found fatal methodological flaws, but because there are no experiments to assess.

---

## Decision

**Reject**

The paper cannot be reviewed empirically. All numbers are TODO_NUM placeholders. A theoretical contribution of this quality deserves a thorough empirical evaluation before review. The quotient-space conformal prediction framework is genuinely novel and the conditional coverage theorem is correct — but NeurIPS requires empirical validation, and the paper in its current form does not provide it.

The figure caption inconsistency (GPT-2 vs. Qwen2.5-7B-Instruct) and the disconnect between the 33% set-size-reduction claim and the actual ablation numbers (13.35 vs. 18.57, with no 19.89 baseline in the tables) are additional red flags that the submitted artifact may not match the described experiments.

**Recommendation:** Accept with Major Revision after experiments are run and all TODO_NUM placeholders are replaced with real numbers. The theoretical foundation is solid enough to warrant another look once the empirical holes are filled.

---

— The Empirical Skeptic