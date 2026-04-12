Good, there's already a `papers/tts-scaling-laws/` directory with a full pipeline. Let me read the existing paper draft and key artifacts to build on what's already there.

That second review is for a different paper (SemCP, conformal prediction). Let me read the full STAIR outline from stage-16.

Let me write the improved outline, accounting for the actual experimental evidence.

Here's a summary of the outline:

## STAIR Paper Outline v2 — Key Decisions

### Method Name: **STAIR** (Staircase Test-time Adaptive Inference Routing)

### 3 Candidate Titles

| # | Title | Mem. | Spec. | Nov. | Best For |
|---|-------|:---:|:---:|:---:|----------|
| 1 | **STAIR: Discrete Scaling Laws for Test-Time Compute in LLM Reasoning** | 5 | 4 | 4 | NeurIPS main track |
| 2 | **STAIR: Why Thinking More Helps in Steps, Not Slopes** | 5 | 3 | 5 | Workshop/oral/Twitter |
| 3 | **STAIR: Predicting When Extra Reasoning Stops Helping via Channel Capacity** | 4 | 5 | 4 | IT-focused venues |

### Critical Addition: Data Reconciliation

I flagged **inconsistent numbers** between `analysis.md` and `decision.md` — this must be resolved before drafting. The outline uses the most conservative (defensible) number for each claim.

### Narrative Strategy

Rather than overselling H1/H2 (which narrowly miss pre-registered thresholds), the outline leads with the **strongest results** — H3's circuit depth proxy (10.7% MAPE, ρ=0.96) and the allocator's 35% MAPE reduction. H1/H2 are framed as "evidence that opens the door" rather than definitive proofs.

### Structure: 9 sections, ~5700 words, ≥35 citations, 5-7 figures, 4 tables

Written to `/Users/rj/research-claw/papers/tts-scaling-laws/artifacts/stage-16/outline_v2.md`.