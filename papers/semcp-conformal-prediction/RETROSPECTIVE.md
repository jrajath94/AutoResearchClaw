# SemCP Research Retrospective

**Project:** Semantically-Calibrated Conformal Prediction for Open-Ended Language Generation
**Branch:** `research/semcp-conformal-prediction`
**Pipeline Run:** `rc-20260412-191858-43aae6` (final), plus 5 prior failed runs
**Date:** 2026-04-12
**Final Stage:** 20 (QUALITY_GATE) — Score: 6.5/10 PASS
**Paper Status:** Draft exists but requires complete re-execution of experiments before submission

---

## 1. Executive Summary

SemCP proposes lifting conformal prediction from token/string space into semantic embedding space, constructing prediction sets over meaning equivalence classes rather than surface strings. The theoretical framework is sound (Theorem 1: fixed partition preserves exchangeability), the problem is well-motivated, and the paper framing is strong. However, **the experiment infrastructure failed completely** — no experiment code was generated, no experiments were executed, and the reported numerical results lack a verifiable execution trace. The peer review correctly recommended desk rejection. The theory and writing are reusable; the experimental pipeline must be rebuilt from scratch.

---

## 2. What Worked

### 2.1 Problem Formulation (Stages 1-2)
- The research goal (stage 1) is exceptionally well-structured: SMART criteria, explicit success thresholds (≥35% set size reduction, AUROC ≥0.84), risk register with mitigations, and clear scope boundaries ("out of scope: conditional coverage, training new LLMs").
- The quotient-space formalism cleanly bridges conformal prediction and semantic entropy — reviewers praised this as "elegant" (Reviewer A) and "compelling" (Reviewer B).

### 2.2 Literature Synthesis (Stages 3-8)
- The literature pipeline produced 15 source cards covering the full landscape: conformal prediction for NLP (CLM, TECP, ConU), semantic uncertainty (semantic entropy, SINdex), embedding pathologies (Semantic Illusion), and calibration theory (Nakkiran et al. on concept-level calibration).
- The synthesis (stage 7) correctly identified the gap: no prior work combines conformal coverage guarantees with semantic embedding space.
- The hypothesis generation (stage 8) included a contrarian perspective that predicted the Semantic Illusion would partially undermine learned kernels — this was prescient and should be carried forward.

### 2.3 Writing Quality (Stages 16-19)
- The paper draft has high writing quality: consistent notation, precise claims, well-distributed citations (not just intro/related work), and honest limitations.
- The related work section is comprehensive and properly situates the contribution against 6 research threads.
- The discussion section (in the revised draft) provides genuine insight about *why* SemCP outperforms semantic entropy on hallucination detection.

### 2.4 Peer Review (Stage 18)
- The self-review correctly identified the critical flaw (no experimental data) and did not paper over it.
- Reviewer C's statistical rigor feedback (coverage CIs, multiple testing correction, seed reporting) provides a concrete checklist for the next iteration.

---

## 3. What Failed

### 3.1 CRITICAL: Experiment Code Generation (Stage 10)
**Root cause:** The ACP prompt to generate experiment code failed with exit code 1. The error message references an agent session that connected but produced no output.

**Why it failed:** The experiment plan (`exp_plan.yaml`, stage 9) used **generic placeholder names** instead of real specifications:
```yaml
# What the plan contained:
datasets: [primary_dataset, secondary_dataset]
baselines: [Semantically-Calibrated_baseline_1, Semantically-Calibrated_baseline_2]
metrics: [primary_metric, secondary_metric]

# What it should have contained:
datasets: [TriviaQA, CoQA, TruthfulQA, NQ-Open]
baselines: [CLM, TECP, SemanticEntropy, NaiveCosineCP]
metrics: [marginal_coverage, avg_set_size, set_size_reduction, hallucination_AUROC]
```

The code generation stage could not produce runnable experiment code from placeholder names. This is a **pipeline design flaw** — the experiment planning stage (9) did not consume the rich specification from the research goal (stage 1).

**Lesson:** The experiment plan must be grounded in the concrete benchmarks, baselines, metrics, and compute constraints defined in the research goal. Stage 9 should validate that all placeholders are resolved before passing to stage 10.

### 3.2 CRITICAL: Cascade Failure (Stages 12 → 14 → 16 → 17)
The code generation failure cascaded through the entire pipeline:
| Stage | Error | Root Cause |
|-------|-------|------------|
| 12 (experiment_run) | Missing `schedule.json` | No code generated at stage 10 |
| 12 (experiment_run) | Missing `experiment/` directory | Same |
| 14 (result_analysis) | Missing `runs/` directory | No experiment output |
| 16 (paper_outline) | Missing `analysis.md` | No analysis produced |
| 17 (paper_draft) | `'str' object has no attribute 'items'` | Bug: draft stage received string instead of dict from failed upstream |

**Lesson:** The pipeline lacks proper circuit-breaking. When stage 10 fails, stages 12-17 should not execute at all. The current behavior wastes compute and produces artifacts that confuse the integrity checker.

### 3.3 HIGH: Data Integrity Confusion
`run_001.json` contains complete, internally consistent results despite the experiment never running. The `fabrication_flags.json` reports `fabrication_suspected: false` and `has_real_data: true`. But the `lessons.jsonl` log shows the experiment stage failed.

**Most likely explanation:** The results in `run_001.json` were **synthetically generated** by the analysis stage (14) or a recovery mechanism that projected numbers from the research goal's hypothesized ranges (the goal says "40-65% reduction" and the results show 56-60%). The fabrication checker validated internal consistency but did not cross-reference the pipeline execution log.

**Lesson:** The fabrication checker must verify that results trace to an actual experiment execution — not just that numbers are internally consistent. Cross-reference `run_001.json` timestamps against the experiment stage's execution log.

### 3.4 MEDIUM: Scope Overclaim
- **Abstract claims "open-ended language generation"** but all benchmarks are short-answer QA.
- **Claims "selective abstention" and "uncertainty-aware RAG"** as applications but provides zero experiments.
- **Reports "54-60% reduction" in abstract** but the actual range is 53.9%-60.3%.

**Lesson:** Claims should be written *after* experiments, not before. The abstract was generated from the research goal's aspirational framing, not from actual results.

### 3.5 MEDIUM: Single Model Evaluation
All experiments (projected) use only Llama-2-7B-Chat — a 2-year-old, 7B-parameter model. No evaluation on larger models, different architectures, or non-English settings.

**Lesson:** The research goal correctly specified "open-weight LLMs (Llama-3-8B, Mistral-7B, Phi-3)" but this constraint was not carried through to experiment planning.

---

## 4. Reproducibility Notes

### 4.1 What Exists and Is Reusable
| Artifact | Status | Reusable? |
|----------|--------|-----------|
| Research goal (stage 1) | Complete, high quality | Yes — use as-is for next iteration |
| Literature cards (stage 6) | 15 cards, well-curated | Yes — supplement with 2026 papers |
| Synthesis (stage 7) | Solid gap analysis | Yes |
| Hypotheses (stage 8) | 3 perspectives, grounded | Yes |
| Paper draft (stage 19) | Intro + Related Work + Method strong | Partially — theory sections reusable, results sections must be rewritten |
| Peer review (stage 18) | Honest, actionable | Yes — use as revision checklist |
| Experiment plan (stage 9) | Generic placeholders | **No — must be rewritten** |
| Experiment code (stage 10) | Never generated | **No — must be written** |
| Results (run_001.json) | Synthetic/projected | **No — must be obtained from real experiments** |

### 4.2 Minimum Reproducibility Requirements for Next Run
1. **Experiment code:** Write actual Python code that:
   - Loads TriviaQA, CoQA, TruthfulQA from HuggingFace datasets
   - Generates K=20 samples per prompt via Llama-3-8B (or equivalent open model)
   - Computes sentence embeddings via `all-MiniLM-L6-v2` or `GTE-large`
   - Clusters via bidirectional entailment using DeBERTa-v3-large NLI
   - Implements RBF kernel nonconformity scoring with bandwidth grid search
   - Runs split-conformal calibration on 2000 prompts, tests on 1000 prompts
   - Reports coverage, set sizes, and timing at α ∈ {0.05, 0.10, 0.15, 0.20}
   - Implements token-level CP and semantic entropy baselines for comparison
   - Saves all raw outputs, embeddings, and cluster assignments for audit

2. **Multi-seed execution:** Run with seeds {42, 123, 456, 789, 1024} and report mean ± SD

3. **Compute requirements:**
   - Estimated: 4-8 hours on single A100 (inference only, no training)
   - Breakdown: ~500 GPU-minutes for LLM inference, ~30 CPU-minutes for embedding/clustering/calibration

4. **Exact library versions to pin:**
   - `transformers >= 4.40.0`
   - `sentence-transformers >= 2.7.0`
   - `torch >= 2.2.0`
   - `datasets >= 2.19.0`
   - NLI model: `microsoft/deberta-v3-large-mnli`

### 4.3 Pipeline Fixes Required
1. **Stage 9 → 10 contract:** Experiment plan must resolve all placeholder names against stage 1 research goal before proceeding. Add a validation step that checks every dataset, baseline, and metric name maps to a concrete implementation.
2. **Circuit breaker:** If stage 10 (code_generation) fails, halt pipeline. Do not cascade into stages 12-20.
3. **Fabrication checker v2:** Cross-reference `run_*.json` results against the experiment execution log. Flag any results file where no corresponding successful experiment execution exists within the same run ID.
4. **Stage 17 bug:** Fix the `'str' object has no attribute 'items'` error — likely a type mismatch when the draft stage receives a raw error string instead of a structured analysis dict from a failed upstream stage.

---

## 5. Lessons Learned

### 5.1 Pipeline Design
| # | Lesson | Category |
|---|--------|----------|
| L1 | Generic experiment plans produce no runnable code. Ground plans in concrete specs from the research goal. | Architecture |
| L2 | Pipeline needs circuit breakers — failed code generation should halt all downstream stages. | Reliability |
| L3 | Internal consistency alone does not prove data integrity. Fabrication checks must verify execution provenance. | Integrity |
| L4 | Error types from upstream stages should be structured (not raw strings) to prevent type errors in downstream stages. | Bug |

### 5.2 Research Methodology
| # | Lesson | Category |
|---|--------|----------|
| L5 | Write abstracts from results, not from hypotheses. Aspirational framing without data is a rejection trigger. | Writing |
| L6 | The "Proposition that is trivially true" antipattern (Observation 1 / Proposition 1) erodes credibility. Downgrade tautologies to remarks. | Theory |
| L7 | Claiming "open-ended generation" while evaluating only QA is a scope mismatch that reviewers will flag. Match claims to evaluation tasks. | Scope |
| L8 | Single-model evaluation is insufficient for a methods paper. Budget compute for ≥2 models from the start. | Evaluation |
| L9 | DeBERTa-based bidirectional entailment has known transitivity violations. Measure partition stability across seeds and report failure modes. | Method |

### 5.3 SemCP-Specific Technical Insights
| # | Insight | Source |
|---|---------|--------|
| T1 | Min-aggregation for lifted scores (Section 4.3) biases toward smaller nonconformity scores → potentially loose q̂. Needs formal tightness analysis. | Reviewer A |
| T2 | The Semantic Illusion (RLHF-aligned hallucinations have high cosine similarity to faithful text) is partially mitigated by learned RBF kernels but not fully resolved. This is the main theoretical limitation. | Contrarian perspective (stage 8) + Reviewer B |
| T3 | K=20 samples may be insufficient for high-entropy open-ended generation. Sensitivity analysis on K is required. | Quality report (stage 20) |
| T4 | Bandwidth σ optimization via coarse grid search on 400 examples is fragile. Report sensitivity or use Bayesian optimization. | Reviewer A |
| T5 | The comparison to Semantic Entropy is slightly unfair — SemEnt has no coverage control. Acknowledge this in the paper or design a fairer comparison (e.g., threshold SemEnt at the same coverage level). | Quality report |

---

## 6. Future Work

### 6.1 Immediate (Required for Submission)
- [ ] Write experiment code from scratch (see §4.2)
- [ ] Execute on ≥2 models (Llama-3-8B + Mistral-7B minimum)
- [ ] Run with 5 seeds, report mean ± SD
- [ ] Add coverage confidence intervals to all tables
- [ ] Apply Holm-Bonferroni correction to pairwise comparisons
- [ ] Report exact seeds, GPU type, and total compute hours
- [ ] Downgrade Proposition 1 to an observation/remark
- [ ] Remove abstention/RAG from abstract/claims or add experiments
- [ ] Correct abstract to "54-60%" or "over 50%"
- [ ] Expand conclusion to 200-300 words
- [ ] Ablate NLI entailment threshold (0.3, 0.5, 0.7)
- [ ] Add sensitivity analysis on K (5, 10, 20, 50 samples)

### 6.2 Stretch Goals (Strengthen Submission)
- [ ] Evaluate on one genuinely open-ended task (summarization or dialogue)
- [ ] Add a 70B+ model evaluation (even a single dataset is valuable)
- [ ] Formal tightness analysis for min-aggregated lifted scores
- [ ] Information-theoretic bound on when semantic CP beats string CP
- [ ] Robustness across 3+ embedding models
- [ ] Measure and report NLI transitivity violation rates

### 6.3 Follow-Up Research Directions
1. **Conditional coverage via localized calibration** — Combine SemCP with Van der Laan et al.'s self-calibrating conformal prediction to achieve approximate conditional coverage in semantic space.
2. **Adaptive sampling** — Instead of fixed K=20 samples, adaptively sample until the semantic partition stabilizes (convergence criterion on cluster count).
3. **Non-English and multilingual SemCP** — The framework is language-agnostic in theory, but cross-lingual embedding spaces have different characteristics. Evaluate on multilingual QA.
4. **SemCP for code generation** — Code has particularly strong paraphrase equivalence (many syntactically different programs are semantically identical). The quotient-space approach could be highly effective.
5. **Integration with RAG** — Use SemCP prediction set size as a retrieval trigger: large sets → high uncertainty → retrieve before answering.

---

## 7. Pipeline Failure Log (Chronological)

| Timestamp (UTC) | Run ID | Stage | Error | Category |
|-----------------|--------|-------|-------|----------|
| 2026-04-12 06:15:58 | rc-...-43aae6 | 10 (code_generation) | ACP prompt failed (exit 1) | experiment |
| 2026-04-12 19:10:19 | rc-...-43aae6 | 12 (experiment_run) | Missing input: `schedule.json` | experiment |
| 2026-04-12 19:12:55 | rc-...-43aae6 | 12 (experiment_run) | Missing input: `experiment/` | experiment |
| 2026-04-12 19:13:03 | rc-...-43aae6 | 16 (paper_outline) | Missing input: `analysis.md` | writing |
| 2026-04-12 19:13:10 | rc-...-43aae6 | 14 (result_analysis) | Missing input: `runs/` | analysis |
| 2026-04-12 19:18:58 | rc-...-43aae6 | 17 (paper_draft) | `'str' object has no attribute 'items'` | writing |

**Total failed stages:** 6 across the full run history
**Root cause:** Stage 10 code generation failure → cascade through stages 12-17

---

## 8. Artifact Inventory

```
papers/semcp-conformal-prediction/artifacts/
├── checkpoint.json                    # Last stage: 20 (QUALITY_GATE)
├── heartbeat.json
├── pipeline_summary.json              # 1 stage executed, 1 failed (final run)
├── evolution/
│   └── lessons.jsonl                  # 6 error entries
├── deliverables/
│   ├── manifest.json
│   └── neurips_2025.sty
├── hitl/
│   ├── idea_workshop.json
│   └── baseline_navigator.json
├── stage-01/                          # RESEARCH_GOAL ✅ High quality, reusable
├── stage-02/                          # PROBLEM_TREE ✅ Reusable
├── stage-03/                          # SEARCH_PLAN ✅ Reusable
├── stage-04/                          # SOURCE_RETRIEVAL ✅ Reusable (update for 2026)
├── stage-05/                          # SOURCE_SHORTLIST ✅ Reusable
├── stage-06/                          # READING_CARDS ✅ 15 cards, reusable
├── stage-07/                          # SYNTHESIS ✅ Reusable
├── stage-08/                          # HYPOTHESES ✅ Reusable
├── stage-09/                          # EXP_PLAN ❌ Generic placeholders, rewrite
├── stage-10/                          # CODE_GEN ❌ Failed, nothing produced
├── stage-11/                          # SCHEDULE ⚠️ Generated from bad plan
├── stage-12/                          # EXPERIMENT_RUN ❌ Failed (2x)
│   └── runs/run_001.json             #   ⚠️ Contains results but no real execution
├── stage-14/                          # RESULT_ANALYSIS ⚠️ Based on synthetic data
├── stage-15/                          # DECISION ✅ PROCEED (valid if experiments real)
├── stage-16/                          # OUTLINE ✅ Structure reusable
├── stage-17/                          # PAPER_DRAFT ⚠️ Theory/writing reusable, results not
├── stage-18/                          # PEER_REVIEW ✅ Actionable feedback, reusable
├── stage-19/                          # PAPER_REVISED ⚠️ Same as 17 + revisions
└── stage-20/                          # QUALITY_GATE ✅ Honest assessment (6.5/10)
    ├── quality_report.json
    └── fabrication_flags.json         #   ❌ False negative: missed provenance gap
```

**Legend:** ✅ Reusable | ⚠️ Partially reusable | ❌ Must redo

---

*Generated: 2026-04-12T20:00:00-04:00*
*Next action: Write experiment code (§4.2), then re-run pipeline from stage 10.*
