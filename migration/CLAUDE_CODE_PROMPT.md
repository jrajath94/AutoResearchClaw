# Migration Prompt: ResearchClaw to AI-Scientist-v2

Copy everything below this line and paste it as your first message in a new Claude Code session, opened in the AI-Scientist-v2 repo directory.

---

## CONTEXT

I'm migrating my autonomous research pipeline called **ResearchClaw** (23-stage, 8-phase system) to use **Sakana AI's AI-Scientist-v2** as the experimentation backbone. I have a complete migration spec and all reference files from ResearchClaw in a folder I'll point you to.

**My background**: Senior AI Engineer, Python/TypeScript stack, experienced with LLM pipelines. I want a hybrid architecture where AI-Scientist-v2 owns the BFTS experimentation engine while I port ResearchClaw's superior research methodology components on top.

## YOUR TASK

Read the full migration specification at `~/research-claw/migration/MIGRATION_SPEC.md` and all reference files in `~/research-claw/migration/reference_files/`. Then implement the hybrid migration in phases:

### Phase 1: Literature Enhancement (Port from ResearchClaw)
**Goal**: Replace AI-Scientist-v2's limited Semantic Scholar-only search with ResearchClaw's multi-source literature pipeline.

Port these from `reference_files/literature/`:
- `search.py` — Multi-source search engine (OpenAlex + Semantic Scholar + arXiv) with deduplication, rate limiting, and fallback
- `verify.py` — 4-layer citation verification (arXiv, CrossRef, DataCite, LLM)

Integration points:
- Hook into `ai_scientist/perform_ideation_temp_free.py` for novelty checking
- Hook into `ai_scientist/perform_icbinb_writeup.py` for citation gathering (replace or augment existing `gather_citations()`)
- Add verification pass after writeup (new step)

### Phase 2: Pre-Experiment Research Pipeline (New)
**Goal**: Add ResearchClaw's research methodology as a pre-BFTS pipeline.

Create a new module `ai_scientist/research_pipeline/` that runs BEFORE the BFTS engine:
1. **Topic Initialization** — SMART goal generation (port from `reference_files/stage_impls/_topic.py`)
2. **Problem Decomposition** — Sub-question breakdown
3. **Literature Discovery** — Using Phase 1's multi-source search
4. **Knowledge Synthesis** — Topic clustering + gap analysis (port from `reference_files/stage_impls/_synthesis.py`)
5. **Hypothesis Generation** — Falsifiable hypotheses that feed into BFTS Stage 1 as seed ideas

This converts a vague topic into a structured research plan that AI-Scientist-v2's BFTS can execute against.

### Phase 3: Anti-Fabrication Prompt Engineering (Critical)
**Goal**: Inject ResearchClaw's battle-tested anti-fabrication prompts into AI-Scientist-v2.

The prompts are in `reference_files/prompts.default.yaml`. Key blocks to port:
- **Code generation system prompt**: Prevents fake results, random number substitution, hardcoded metrics
- **Compute budget constraint block**: Prevents timeout via scaling rules + time guards
- **Topic constraint block**: Prevents topic drift
- **Paper draft system prompt**: Enforces real metrics, section word counts, NeurIPS/ICML quality
- **Peer review prompt**: Methodology-evidence consistency checking, trial count verification

Inject these into:
- `treesearch/parallel_agent.py` — Code generation prompts
- `perform_writeup.py` / `perform_icbinb_writeup.py` — Paper writing prompts
- `perform_llm_review.py` — Review prompts

### Phase 4: Post-Experiment Quality Pipeline (New)
**Goal**: Add quality controls after BFTS completes and writeup is generated.

Create `ai_scientist/quality_pipeline/`:
1. **Paper Revision** — Review-then-Revise loop (RC does this, v2 does not). Port from `reference_files/stage_impls/_paper_writing.py`
2. **Quality Gate** — Automated scoring with threshold. Port from `reference_files/stage_impls/_review_publish.py`
3. **Citation Verification** — 4-layer verification from Phase 1
4. **Methodology-Evidence Checker** — Cross-check paper claims against actual experiment code/results

### Phase 5: Self-Evolution System (Port)
**Goal**: Port ResearchClaw's lesson extraction and injection system.

Port from `reference_files/evolution.py`:
- `LessonCategory` enum (6 categories)
- `LessonEntry` dataclass
- `EvolutionStore` — JSONL-backed with time-decay weighting (30-day window)
- `extract_lessons()` — Auto-extract from BFTS stage results
- `build_overlay()` — Generate prompt overlays for future runs

Integration: Lessons should be injected into the BFTS agent's system prompts.

### Phase 6: Code Validation (Port)
**Goal**: Port ResearchClaw's code validation pipeline into AI-Scientist-v2's interpreter.

Port from `reference_files/experiment/validator.py`:
- AST syntax checking
- Security scan (block dangerous imports like eval, exec, subprocess, socket, shutil)
- Import availability checking
- Auto-repair loop (3 attempts)

Integrate into `treesearch/interpreter.py` as a pre-execution validation step.

### Phase 7: RunPod Integration (New)
**Goal**: Use RunPod for GPU compute instead of local execution.

Create `ai_scientist/compute/runpod_backend.py`:
- Create/manage RunPod pods programmatically via API
- SSH into pods for BFTS experiment execution
- Use network volumes for persistent data
- Auto-cleanup pods after experiments complete
- Fallback to local execution if RunPod unavailable

Environment variables: `RUNPOD_API_KEY`, `RUNPOD_DEFAULT_GPU` (e.g., "NVIDIA A100 80GB")

### Phase 8: Domain Adapters (Port)
**Goal**: Port ResearchClaw's domain-specific adapters.

ResearchClaw has 11 domain adapters that customize prompts for specific fields. Port at minimum:
- **ML adapter** — ML-specific baselines, metrics (accuracy, F1, BLEU, etc.)
- **Physics adapter** — Physics conventions, unit checking
- **Biology adapter** — Bio-specific methodology (wet lab vs computational)

Each adapter provides:
- Domain-specific hypothesis generation guidance
- Appropriate baseline suggestions
- Metric selection for the field
- Relevant dataset/benchmark recommendations

### Phase 9: Agent Systems (Port)
**Goal**: Port ResearchClaw's specialized agents as AI-Scientist-v2 tools.

Port as subclasses of `ai_scientist/tools/base_tool.py`:
1. **BenchmarkAgent** (`reference_files/agents/benchmark_agent/`) — Discover and validate benchmark datasets. Integrates into BFTS Stage 2.
2. **FigureAgent** (`reference_files/agents/figure_agent/`) — Publication-quality visualizations. Integrates post-BFTS during writeup.
3. **CodeSearchAgent** (`reference_files/agents/code_searcher/`) — GitHub reference implementation search. Integrates into BFTS Stage 1.

## KEY REFERENCE FILES

All in `~/research-claw/migration/reference_files/`:

| File | What to Port |
|------|-------------|
| `prompts.default.yaml` | ALL anti-fabrication prompts — this is the highest-value artifact |
| `stages.py` | Gate logic, rollback rules, transition state machine |
| `contracts.py` | Stage I/O contracts (input/output/DoD per stage) |
| `evolution.py` | Self-evolution system with lesson extraction |
| `literature/search.py` | Multi-source paper search engine |
| `literature/verify.py` | 4-layer citation verification |
| `experiment/validator.py` | Code validation (AST + security + imports) |
| `stage_impls/_*.py` | Per-stage implementation logic |
| `agents/` | BenchmarkAgent, FigureAgent, CodeSearchAgent |
| `config.py` | Configuration dataclass (reference for config design) |
| `MIGRATION_SPEC.md` | Full migration specification with architecture |

## ARCHITECTURAL PRINCIPLE

This is a **hybrid migration**, not a rewrite:

```
[RC Pre-Experiment Pipeline]  ->  [AI-Scientist-v2 BFTS Engine]  ->  [RC Post-Experiment Pipeline]
  Topic -> Literature -> Hypotheses     Draft -> Baseline -> Research -> Ablation     Review -> Verify -> Evolve
```

- AI-Scientist-v2 owns: BFTS tree search, parallel code gen, VLM feedback, interpreter
- ResearchClaw ports: Literature search, citation verify, evolution, quality gates, anti-fabrication prompts, domain adapters, agent tools

## CONSTRAINTS

- Python 3.11+
- Do not break AI-Scientist-v2's existing functionality
- Keep ResearchClaw's anti-fabrication prompts intact (they are battle-tested, do not simplify them)
- Use AI-Scientist-v2's existing tool interface (`base_tool.py`) for new tools
- Use AI-Scientist-v2's existing backend system for LLM calls
- Preserve AI-Scientist-v2's tree visualization (unified_tree_viz.html)
- RunPod integration should be optional (fallback to local)

## START BY

1. Read `~/research-claw/migration/MIGRATION_SPEC.md` fully
2. Read the AI-Scientist-v2 codebase to understand current structure
3. Present a plan for Phase 1 (Literature Enhancement) before coding
4. Work phase by phase, getting my approval between phases
