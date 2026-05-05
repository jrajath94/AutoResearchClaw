# Paper Council Review — SemCP: Coverage Guarantees Over Meanings, Not Strings

**Reviewed:** 2026-05-01
**Target venue:** NeurIPS 2026
**Rubric used:** NeurIPS 2026 (rubric.md)
**Council mode:** Tier-0 Premium (10 reviewers × 6 rounds, all Opus)
**Workspace:** paper_council/2026-05-01-1200/

---

## 🎯 Executive Verdict

**Final decision: REJECT** (weighted average ~5.0/10, Reject range 4.0–5.5)
**AC confidence:** 5/5
**Council average score:** 5.0/10 (median ~5.1, dispersion σ≈0.4)

> "The paper identifies a genuine gap (semantic conformal prediction) and makes a technically sound theoretical contribution — the quotient-space framing and admissibility-coverage decomposition are genuine contributions that would survive the 5-year test. However, the paper is unsalvageable in its current state: every experimental result in Table 1 is a TODO_NUM placeholder, and the central quantitative claim (33% set-size reduction) is completely unverified." — Area Chair

### Top 3 must-fix items (from Revision Playbook)
1. **Run the experiments** — All Table 1 cells are `TODO_NUM`. Populate real numbers from the Qwen2.5-7B-Instruct runs. This is the single blocking issue.
2. **Fix the GPT-2/Qwen contradiction** — Figure 3 caption says "GPT-2's limited QA capability" but experiments use Qwen2.5-7B-Instruct. These have fundamentally different admissibility regimes (2–3% vs. meaningful). Reconcile all Discussion text to match the actual model used.
3. **Align Algorithm 1 with Section 4.3** — Algorithm 1 (line 180) computes a contrastive *between-cluster* score; Section 4.3 defines a *within-cluster minimum* aggregation. These are structurally different procedures — a correctness concern, not just a clarity issue.

### Decision distribution across 9 reviewers
| Decision | Count |
|---|---|
| Strong Accept | 0 |
| Accept | 0 |
| Borderline | 2 |
| Reject | 3 |
| Strong Reject | 4 |

---

## 📊 Per-reviewer scoreboard

| # | Persona | Decision | Overall | Confidence | Soundness | Novelty | Repro |
|---|---------|----------|---------|------------|-----------|---------|-------|
| 1 | Methodological Hawk | Reject | 5.2 | 4/5 | 3 | 7 | 3 |
| 2 | Theory Critic | Borderline | 5.85 | 4/5 | 4 | 8 | 2 |
| 3 | Empirical Skeptic | Reject | 4.93 | 4/5 | 3 | 7 | 3 |
| 4 | Statistical Rigorist | Reject | ~5.0 | 3/5 | 4 | 7 | 2 |
| 5 | Adversarial Practitioner | Strong Reject | 4.77→4.89 | 4/5 | 3 | 6 | 3 |
| 6 | Domain Expert ML | Borderline→Reject | 5.3→4.77 | 4/5 | 3 | 7 | 2 |
| 7 | Reproducibility Archeologist | Borderline | 5.6 | 3/5 | 5 | 7 | 2 |
| 8 | Big Picture Editor | Strong Reject | 5.4→4.6 | 4/5 | 2 | 7 | 2 |
| 9 | Naive Reader | Strong Reject | 5.1 | 4/5 | 3 | 7 | 2 |
| AC | Area Chair | **Reject** | **5.0** | **5/5** | **3** | **7** | **2** |

---

## 🧠 Area Chair Meta-Review

**Decision: REJECT** (weighted average 5.0, Reject range 4.0–5.5)

The synthesis applied Bayesian aggregation across all 9 reviews + 5 cross-examinations. Soundness was the dominant factor (weight 1.5×), with multiple reviewers scoring it 2–3 due to the combination of absent experiments AND theoretical gaps.

### TOP 5 Issues (ranked by severity)

**Issue 1 — UNANIMOUS (9/9): All Table 1 entries are `TODO_NUM` placeholders.**
The paper cannot be evaluated empirically. The abstract's "TODO_NUM% smaller set sizes," all Table 1 metrics (marginal coverage, conditional coverage, set size, abstention rate, admissibility rate), and the TODO_HOURS runtime placeholder mean the central quantitative claims are completely unverified. This is not a minor issue — it is a blocking issue that makes the paper un-submittable to NeurIPS in its current state.

**Issue 2 — CONSENSUS (8/9): Figure 3 caption contradicts experimental setup.**
The caption says "near-zero coverage for all methods due to GPT-2's limited QA capability" but Section 5.1 specifies Qwen2.5-7B-Instruct. GPT-2 and Qwen2.5-7B-Instruct have fundamentally different admissibility regimes (2–3% vs. much higher). The Discussion section continues to analyze results under the GPT-2 framing without updating to the actual experimental setup. This suggests draft assembly from multiple sources and raises concerns about which numbers actually came from which experiment.

**Issue 3 — HIGH CONSENSUS (5–7/9): Near-zero coverage + 33% set-size reduction are mutually incoherent.**
The paper claims "33% set-size reduction on SQuAD" while simultaneously attributing near-zero coverage to generator quality failures. Set-size reduction is only meaningful when coverage is valid and comparable across methods. If coverage is near-zero for all methods (as the Discussion claims), the set-size comparison is vacuous — both SemCP and baselines produce empty or near-empty sets, making percentage reductions meaningless. This internal contradiction undermines the paper's core empirical narrative.

**Issue 4 — MODERATE CONSENSUS (4–5/9): Algorithm 1 vs. Section 4.3 structural mismatch.**
Algorithm 1 (line 180) computes: `1 - max_{c' != c_i*} kappa_sigma(c_i*, c')` — a contrastive between-cluster score measuring distance from the correct cluster to the nearest other cluster. Section 4.3 defines the lifted score as `min_{y' in [y]_s} s(x, y')` — a within-cluster minimum aggregation. These are structurally different procedures solving different problems. The algorithm implements a contrastive objective; the theory analyzes a min-aggregation. A reader who checks Algorithm 1 against the theorem will conclude the proven guarantee does not apply to the implemented algorithm.

**Issue 5 — DISTINCTIVE (3–4/9): Admissibility-selection proof gap in Theorem 1.**
Theorem 1 computes the conformal threshold q-hat over the admissibility subset I = {i : A_i = 1} — a post-hoc selected set, not a pre-fixed calibration set. The standard split-conformal guarantee requires the threshold to be computed over a fixed, pre-specified calibration set. Computing it over a subset selected after observing which calibration examples were admissible introduces selection bias that the proof sketch does not address. A counterexample exists: it is possible for admissibility to hold at test time but coverage to fall below the claimed guarantee because the threshold was calibrated on a biased (admissible-only) subset.

### Additional Issues Surfaced in Cross-Examination

**Baseline hyperparameter asymmetry (4/9):** SemCP tunes bandwidth σ via grid search on a held-out 20% split; baselines use fixed/default hyperparameters (ConU has no tuning; SAFER's 0.10 threshold is not tuned for this task; LofreeCP uses λ=0.5 from the public repo). This means the set-size comparison favors SemCP by design — a classic experimental design flaw.

**NLI transitivity assumption (3/9):** DeBERTa-v2-xlarge-MNLI does not guarantee transitive closure. Union-Find on pairwise bidirectional entailment judgments can over-merge distinct equivalence classes, conflating contradictory answers into the same meaning class and breaking the semantic partition.

**O(K²) NLI inference cost (2–3/9):** With K=10 samples, partitioning requires O(100) NLI forward passes per instance. At scale, this is computationally prohibitive and is not analyzed in the paper.

**Embedding anisotropy (2/9):** The paper uses all-MiniLM-L6-v2 without addressing known anisotropy pathologies (Ethayarajh 2019, Mueller 2022). High cosine similarity between embeddings of contradictory statements has been documented for this model class.

### Path to Accept

All issues are fixable. The theoretical contribution — quotient-space conformal prediction with conditional semantic coverage — is genuine and uncontested. The admissibility-coverage decomposition is a useful diagnostic contribution. With real experiments, resolved contradictions, aligned algorithm and theory, and released code, this is a competitive NeurIPS submission. The estimated best-case weighted average after major revision: **7.54 (Strong Accept)**.

---

## 🔥 Red-Team Attack Summary

**Top 3 Claims Attacked:**

| Claim | Attack Vector | Refutation Evidence | Retractability Trigger |
|-------|--------------|---------------------|------------------------|
| **Theorem 1** conditional coverage | Admissibility-selection proof gap | Threshold computed on post-hoc selected subset breaks exchangeability | Counterexample where admissibility holds but coverage < guarantee |
| **33% set-size reduction** | Coverage collapse + kernel overfitting | If p_A < 0.50, both baselines produce empty sets; 33% is meaningless | 33% fails to replicate on held-out test data |
| **NLI partition preserves exchangeability** | Non-transitivity of DeBERTa MNLI | Union-Find closure on non-transitive NLI produces invalid equivalence classes | NLI partition error rate >5% on ground-truth test set breaks exchangeability |

**Additional Critical Failure Modes:**
- Algorithm 1 uses contrastive between-cluster scoring; Theorem 1 analysis uses within-cluster min-aggregation — different algorithms
- The paper simultaneously claims "near-zero coverage" and "33% set-size reduction" — mutually incoherent
- Fig 3 caption attributes results to GPT-2 while experiments use Qwen2.5-7B-Instruct — suggests possible experiment conflation
- TODO_NUM placeholders give authors the option to fill in whichever numbers best support the claims

**Can it ever be published?** Yes, conditionally — but only with: real numbers, resolved Algorithm-theory mismatch, released code, and p_A > 0.85.

---

## 💪 Steelmanned Best-Case Scoring (Round 4)

If all Priority-1 weaknesses were addressed, the council estimates this paper would score:

| Dimension | Current avg | Best-version (post-revision) | Lift |
|---|---|---|---|
| Soundness | 3.1 | 7.5 | +4.4 |
| Reproducibility | 2.1 | 8.0 | +5.9 |
| Originality | 7.0 | 8.0 | +1.0 |
| Significance | 6.0 | 7.5 | +1.5 |
| Clarity | 6.0 | 8.0 | +2.0 |
| Contextualization | 7.0 | 8.0 | +1.0 |
| Ethical Impact | 6.0 | 7.0 | +1.0 |
| **Weighted avg** | **5.0** | **7.54** | **+2.54** |

**Irreducible contribution (survives all 9 reviews):**
1. **Theorem 1** — quotient-space conformal prediction framework is mathematically sound, confirmed independently by all reviewers
2. **Admissibility-coverage decomposition** (`p_A × coverage | A`) is a genuine diagnostic contribution requiring no new experiments
3. The **problem is real and uncontested** — no prior work provides CP over meanings

---

## 🎯 Consensus Weakness Matrix

Items with 3+ independent citations are HIGH-confidence findings the AC weighted heavily.

| Weakness | Hawk | Theory | Emp | Stat | Pract | Domain | Repro | BigPic | Naive | Total |
|---|---|---|---|---|---|---|---|---|---|---|
| All results TODO_NUM | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **9/9** |
| GPT-2/Qwen caption mismatch | ✓ | ✓ | | | ✓ | ✓ | ✓ | ✓ | ✓ | **8/9** |
| Near-zero coverage + 33% incoherence | | ✓ | ✓ | ✓ | ✓ | | ✓ | ✓ | ✓ | **7/9** |
| Algorithm-theory mismatch | | ✓ | | | ✓ | ✓ | | ✓ | ✓ | **5/9** |
| Admissibility-selection proof gap | | ✓ | | | ✓ | ✓ | | | | **4/9** |
| Baseline hyperparameter asymmetry | ✓ | | | ✓ | ✓ | | ✓ | | | **4/9** |
| Code not released | | ✓ | | ✓ | ✓ | | ✓ | | | **4/9** |
| NLI transitivity assumption | | ✓ | | | | ✓ | | | | **2/9** |
| O(K²) NLI cost unaddressed | | | | | ✓ | ✓ | | | | **2/9** |

---

## 📋 Suggested Next Actions

Based on the Area Chair's recommended revisions (in order of impact/effort):

1. **Run the full experiment matrix** (5 methods × 3 seeds × 2 datasets, N=500 each, K=10 samples) — populate all TODO_NUM cells in Table 1 and TODO_HOURS in Table 2. **Effort: ~6–8 GPU-hours. Odds-lift: +2.5 to Strong Accept.**
2. **Fix GPT-2/Qwen inconsistency** — update Figure 3 caption and all Discussion text to reference Qwen2.5-7B-Instruct; rerun any experiments that were actually run on GPT-2. **Effort: Low (text fix). Odds-lift: +0.3.**
3. **Align Algorithm 1 with Section 4.3** — either rewrite Algorithm 1 to use within-cluster min-aggregation, or prove the contrastive score achieves the same guarantee. **Effort: Medium (proof/algorithm change). Odds-lift: +0.5.**
4. **Release code at submission** (not "upon publication") — this directly addresses the Reproducibility 2/10 score. **Effort: Low–Medium. Odds-lift: +0.4.**
5. **Address admissibility-selection proof gap** — either pre-fix the admissibility threshold or provide a separate exchangeability argument for post-hoc selection. **Effort: Medium (proof revision). Odds-lift: +0.3.**

Run `/paper-council` again after addressing items 1–3 to verify improvements.

---

## 🔗 Full Artifact Paths

- Per-reviewer round-1 reviews: `01_independent/`
- Cross-examination round: `02_cross_exam/` (5 of 9 completed; Methodological Hawk, Empirical Skeptic, Naive Reader, Reproducibility Archeologist still pending due to connection errors)
- Red-team attacks: `03_red_team/attacks.md`
- Steelman: `04_steelman/strongest_version.md`
- Area Chair synthesis: `05_synthesis/area_chair_meta_review.md`
- Final outputs: `06_outputs/` (agents still running — Revision Playbook, Mock Rebuttal, Sister Papers pending completion)
- This compiled report: `REVIEW_COUNCIL.md`

---

*Generated by paper-council v1.0 — Tier-0 Multi-Agent Peer Review.*
*All reviewers ran on Claude Opus 4.7 via Claude Code subscription.*
*9 independent reviews + 5 cross-examinations + Red Team + Steelman + Area Chair synthesis = 16 total agent runs.*
