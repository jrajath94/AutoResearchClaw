# ResearchClaw → AI-Scientist-v2 Migration Specification

## Executive Summary

Migrate the ResearchClaw autonomous research pipeline (23-stage, 8-phase system) to use Sakana AI's AI-Scientist-v2 framework as the execution backbone. The goal is to preserve ResearchClaw's research methodology, domain expertise, prompt engineering, and quality controls while leveraging AI-Scientist-v2's superior Best-First Tree Search (BFTS) experimentation engine.

---

## 1. WHAT RESEARCHCLAW IS

### 1.1 Core Identity
- **Full name**: ResearchClaw v0.3.2
- **Purpose**: Fully autonomous academic research pipeline — topic to paper
- **Language**: Python 3.11+, pure stdlib LLM client (no httpx/requests)
- **Dependencies**: pyyaml, rich, arxiv, numpy (core); matplotlib, scipy, huggingface-hub (optional)

### 1.2 The 23-Stage Pipeline (8 Phases)

```
Phase A: Research Scoping
  1: TOPIC_INIT           — Define SMART research question
  2: PROBLEM_DECOMPOSE    — Break into >=4 prioritized sub-questions

Phase B: Literature Discovery
  3: SEARCH_STRATEGY      — Multi-source search plan (OpenAlex, Semantic Scholar, arXiv)
  4: LITERATURE_COLLECT   — Execute search, collect >=20 candidate papers
  5: LITERATURE_SCREEN    — [GATE] Relevance + quality dual screening
  6: KNOWLEDGE_EXTRACT    — Structured knowledge cards per paper

Phase C: Knowledge Synthesis
  7: SYNTHESIS            — Topic clustering + research gap analysis
  8: HYPOTHESIS_GEN       — Generate >=2 falsifiable hypotheses

Phase D: Experiment Design
  9: EXPERIMENT_DESIGN    — [GATE] Full experiment protocol (baselines, ablations, metrics)
  10: CODE_GENERATION     — Multi-file Python experiment project + validation
  11: RESOURCE_PLANNING   — GPU/time scheduling

Phase E: Experiment Execution
  12: EXPERIMENT_RUN      — Execute in sandbox/docker/SSH/Colab
  13: ITERATIVE_REFINE    — Edit-Run-Evaluate improvement loop (<=10 iterations)

Phase F: Analysis & Decision
  14: RESULT_ANALYSIS     — Statistical analysis with real metrics
  15: RESEARCH_DECISION   — PROCEED/PIVOT/ITERATE decision

Phase G: Paper Writing
  16: PAPER_OUTLINE       — Section-level paper plan
  17: PAPER_DRAFT         — Full 5000-6500 word NeurIPS/ICML-style paper
  18: PEER_REVIEW         — Multi-perspective simulated review (2+ reviewers, scored 1-10)
  19: PAPER_REVISION      — Address all review comments

Phase H: Finalization
  20: QUALITY_GATE        — [GATE] Automated quality scoring
  21: KNOWLEDGE_ARCHIVE   — Retrospective + lessons learned
  22: EXPORT_PUBLISH      — Charts + final export
  23: CITATION_VERIFY     — 4-layer citation verification (arXiv, CrossRef, DataCite, LLM)
```

### 1.3 Gate Stages (3 Approval Checkpoints)
| Gate | Stage | On Reject, Rollback To |
|------|-------|------------------------|
| Literature Quality | 5 | Stage 4 (re-collect) |
| Experiment Design | 9 | Stage 8 (re-hypothesize) |
| Paper Quality | 20 | Stage 16 (rewrite from outline) |

### 1.4 Stage Contracts
Every stage has an I/O contract (see `reference_files/contracts.py`):
- `input_files`: what it reads
- `output_files`: what it must produce
- `dod`: Definition of Done
- `error_code`: diagnostic identifier (E01-E23)
- `max_retries`: retry budget per stage

### 1.5 Key Differentiators from Generic AI Research Systems
1. **Literature-first methodology**: Stages 3-6 do real API-based paper discovery (OpenAlex 10K/day, Semantic Scholar 1K/5min, arXiv)
2. **Citation verification**: 4-layer verification catches hallucinated references
3. **Self-evolution**: Lessons extracted from failures, time-decay weighted (30-day window), injected as prompt overlays
4. **Multi-domain support**: 11 domain adapters (ML, Physics, Biology, Chemistry, Neuroscience, Robotics, Economics, Math, Security, etc.)
5. **Human-in-the-loop**: 6 intervention modes (full-auto, gate-only, checkpoint, step-by-step, co-pilot, custom)
6. **Methodology-evidence consistency**: Peer review specifically checks claims against actual experiment code/results
7. **Anti-fabrication prompts**: Extensive prompt engineering to prevent fake results, random number substitution, hallucinated metrics

---

## 2. WHAT AI-SCIENTIST-V2 IS

### 2.1 Architecture
- **Repository**: https://github.com/SakanaAI/AI-Scientist-v2
- **Core**: 3-phase macro-pipeline (Ideation, Experimentation via BFTS, Paper Generation)
- **Built on**: AIDE (WecoAI) tree search framework
- **Key achievement**: First AI-generated paper accepted at ICLR 2025 workshop

### 2.2 The 4-Stage BFTS Experimentation Engine
```
Stage 1: Draft/Exploration (max 20 iters) — Generate initial approaches, 3 root nodes
Stage 2: Baseline Comparison (max 12 iters) — Establish competitive baselines
Stage 3: Research/Improvement (max 12 iters) — Core research contribution
Stage 4: Ablation Studies (max 18 iters) — Validate via ablation
```

Each stage uses Best-First Tree Search with:
- Parallel workers (default 4)
- VLM feedback loop (critiques plots, flags buggy nodes)
- Debug retry mechanism (max depth 3, probability 0.5)
- Multi-seed evaluation (3 seeds per node)

### 2.3 Key Components
| Component | File | Size | Purpose |
|-----------|------|------|---------|
| AgentManager | `treesearch/agent_manager.py` | 51KB | Stage orchestrator |
| Parallel Agent | `treesearch/parallel_agent.py` | 109KB | BFTS algorithm |
| Journal | `treesearch/journal.py` | - | Tree data structure |
| Interpreter | `treesearch/interpreter.py` | - | Code execution sandbox |
| LLM Backend | `treesearch/backend/` | - | Multi-provider routing |
| Writeup | `perform_writeup.py` / `perform_icbinb_writeup.py` | - | Paper generation |
| Review | `perform_llm_review.py` / `perform_vlm_review.py` | - | Automated review |
| Ideation | `perform_ideation_temp_free.py` | - | Idea generation |
| Semantic Scholar | `tools/semantic_scholar.py` | - | Literature search |

### 2.4 Configuration (`bfts_config.yaml`)
```yaml
exec:
  timeout: 3600          # 1hr per code execution
agent:
  type: parallel
  num_workers: 4
  stages:
    stage1_max_iters: 20
    stage2_max_iters: 12
    stage3_max_iters: 12
    stage4_max_iters: 18
  code:
    model: anthropic.claude-3-5-sonnet-20241022-v2:0  # Bedrock
    temp: 1.0
    max_tokens: 12000
  feedback:
    model: gpt-4o-2024-11-20
    temp: 0.5
  vlm_feedback:
    model: gpt-4o-2024-11-20
  search:
    max_debug_depth: 3
    debug_prob: 0.5
    num_drafts: 3
```

### 2.5 LLM Support
- OpenAI (gpt-4o, o1, o3-mini, gpt-4.1)
- Anthropic direct + Bedrock + Vertex AI
- Google Gemini
- DeepSeek
- HuggingFace
- OpenRouter
- Ollama (local)

### 2.6 Cost per Run: ~$22-30

---

## 3. MAPPING: RESEARCHCLAW to AI-SCIENTIST-V2

### 3.1 Pipeline Stage Mapping

| ResearchClaw Stage | AI-Scientist-v2 Equivalent | Migration Strategy |
|--------------------|---------------------------|-------------------|
| **1-2: Topic + Decompose** | `perform_ideation_temp_free.py` | Wrap RC's topic_init + decompose as ideation preprocessor |
| **3-6: Literature Discovery** | `tools/semantic_scholar.py` (limited) | **EXTEND** — Port RC's multi-source search (OpenAlex, S2, arXiv) + screening + knowledge extraction |
| **7-8: Synthesis + Hypothesis** | Part of ideation | **EXTEND** — Port RC's synthesis + hypothesis gen as post-ideation |
| **9: Experiment Design** | Implicit in BFTS Stage 1 | **INTEGRATE** — Inject RC's experiment design as Stage 1 seed |
| **10: Code Generation** | BFTS agent generates code | **REPLACE** — Use AI-Scientist-v2's tree search code gen (superior) |
| **11: Resource Planning** | Not present | **ADD** — Port as pre-experiment resource check |
| **12-13: Experiment Run + Refine** | BFTS Stages 1-4 (core engine) | **REPLACE** — AI-Scientist-v2's BFTS is fundamentally better |
| **14: Result Analysis** | `log_summarization.py` | **EXTEND** — Port RC's statistical analysis as post-BFTS analysis |
| **15: Research Decision** | Not present (always proceeds) | **ADD** — Port PROCEED/PIVOT decision logic |
| **16-17: Outline + Draft** | `perform_writeup.py` / `perform_icbinb_writeup.py` | **EXTEND** — Inject RC's anti-fabrication prompts into v2's writeup |
| **18: Peer Review** | `perform_llm_review.py` + `perform_vlm_review.py` | **EXTEND** — Port RC's methodology-evidence consistency checking |
| **19: Paper Revision** | Not present (single-pass writeup) | **ADD** — Port RC's review-then-revision loop |
| **20: Quality Gate** | Not present | **ADD** — Port quality scoring + gate logic |
| **21: Knowledge Archive** | Not present | **ADD** — Port evolution/lesson extraction |
| **22: Export + Charts** | `perform_plotting.py` (partial) | **EXTEND** — Port RC's figure agent + chart generation |
| **23: Citation Verify** | Citation gathering exists, no verification | **ADD** — Port 4-layer citation verification |

### 3.2 What AI-Scientist-v2 Does Better (REPLACE)
- **Experiment execution**: BFTS tree search >> RC's linear edit-run-eval loop
- **Code generation**: Parallel exploration with 4 workers >> single-shot generation
- **Visual feedback**: VLM critiques plots (RC has no equivalent)
- **Debug retry**: Probabilistic debug with backtracking >> simple retry

### 3.3 What ResearchClaw Does Better (PORT)
- **Literature discovery**: Multi-source API search >> single Semantic Scholar
- **Citation verification**: 4-layer verification >> none
- **Self-evolution**: Lesson extraction + time-decay injection >> none
- **Quality gates**: 3 approval checkpoints >> none
- **Anti-fabrication**: Extensive prompt engineering >> basic prompts
- **Paper revision**: Review-then-revise loop >> single-pass writeup
- **Domain adapters**: 11 domain-specific adapters >> generic
- **Methodology-evidence checking**: Peer review cross-checks code vs claims >> basic review

---

## 4. RESEARCHCLAW'S AGENT SYSTEMS (TO PORT)

### 4.1 BenchmarkAgent
- **Purpose**: Discover, select, acquire, and validate benchmark datasets
- **Sub-agents**: Surveyor, Selector, Acquirer, Validator, Orchestrator
- **Integration point**: Should feed into AI-Scientist-v2's Stage 2 (Baseline)
- **Files**: `reference_files/agents/benchmark_agent/`

### 4.2 FigureAgent
- **Purpose**: Generate publication-quality visualizations
- **Sub-agents**: Decision, Renderer, Nano Banana (Gemini image gen), Integrator
- **Integration point**: Post-BFTS, during writeup phase
- **Files**: `reference_files/agents/figure_agent/`

### 4.3 CodeAgent (Code Searcher)
- **Purpose**: Search GitHub for reference implementations
- **Integration point**: During BFTS Stage 1 (Draft) to bootstrap with real patterns
- **Files**: `reference_files/agents/code_searcher/`

### 4.4 ACP Client
- **Purpose**: Agent Client Protocol bridge for external coding agents (Claude Code, Codex, etc.)
- **Integration point**: Optional enhancement for BFTS code generation
- **Files**: `reference_files/acp_client.py`

---

## 5. RESEARCHCLAW'S PROMPT ENGINEERING (CRITICAL TO PORT)

### 5.1 Anti-Fabrication Prompts (in `prompts.default.yaml`)
The most valuable IP — these prevent LLMs from hallucinating results:

**Code Generation prompt** enforces:
- REAL algorithms (gradient descent, Adam, SGD) using numpy, NOT random.uniform() faking
- REAL objective/loss functions with proper mathematical formulas
- REAL optimization loops with gradient computation
- Convergence stopping criteria (not fixed iteration counts)
- Explicit anti-patterns list (13 specific fabrication patterns blocked)
- NumPy 2.x compatibility checks

**Paper Draft prompt** enforces:
- Every metric must EXACTLY match provided experiment output
- NeurIPS/ICML submission quality (5000-6500 words)
- Section-level minimum word counts
- Figure 1 prominence requirement
- Strong baselines mandate
- Ablation study requirement
- Honest limitations acknowledgment
- Contribution clarity in Abstract AND Introduction

**Peer Review prompt** enforces:
- Methodology-evidence consistency cross-checking
- Trial count verification (catches "100 trials" claims when 1 was run)
- Paper length verification against conference standards
- Scoring rubric (1-10 with explicit criteria)

**Topic Constraint block** prevents topic drift:
- Prohibits treating setup/infrastructure as research contribution
- Prohibits presenting debugging logs as findings
- Requires every section to connect to core research question

### 5.2 Compute Budget Constraint Block
Embedded in experiment prompts to prevent timeout:
- Scaling rules for large condition counts
- Mandatory TIME_ESTIMATE printing
- Time guard implementation requirement (stop at 80% budget)

---

## 6. RESEARCHCLAW'S SELF-EVOLUTION SYSTEM (TO PORT)

### 6.1 Architecture
```
LessonCategory (6 types):
  SYSTEM      — Environment/network/timeout
  EXPERIMENT  — Code execution failures
  WRITING     — Paper quality issues
  ANALYSIS    — Statistical/metric problems
  LITERATURE  — Search/citation issues
  PIPELINE    — Stage orchestration failures

LessonEntry fields:
  stage: str
  category: LessonCategory
  severity: "info" | "warning" | "error"
  description: str
  timestamp: datetime

EvolutionStore:
  - JSONL-backed persistent storage
  - append_many(lessons)
  - build_overlay(stage_name, max_lessons=5) -> prompt text
  - Time-decay weighting (30-day window, exponential decay)
```

### 6.2 How It Works
1. After each pipeline run, `extract_lessons()` scans stage results for failures/warnings
2. Lessons stored in `evolution/lessons.jsonl`
3. Before each stage in future runs, `build_overlay()` generates a prompt snippet with relevant lessons
4. Recent lessons weighted higher (exponential decay over 30 days)
5. This creates a continuous improvement loop across runs

---

## 7. RUNPOD USAGE PLAN

ResearchClaw currently uses local/SSH/Docker execution. For AI-Scientist-v2 migration:

### 7.1 Recommended RunPod Setup
| Resource | Purpose | Spec |
|----------|---------|------|
| **GPU Pod** | BFTS experiment execution | A100 80GB or H100, 4 workers need ~32GB each |
| **Network Volume** | Persistent experiment data | 100GB+ for datasets + results |
| **Serverless Endpoint** | On-demand experiment runs | Auto-scale 0 to N for burst |

### 7.2 Template Configuration
```yaml
# RunPod template for AI-Scientist-v2
image: pytorch/pytorch:2.2.0-cuda12.1-cudnn8-devel
ports: ["8888/http", "22/tcp"]
volume_mount: /workspace
env:
  OPENAI_API_KEY: "${OPENAI_API_KEY}"
  ANTHROPIC_API_KEY: "${ANTHROPIC_API_KEY}"
  S2_API_KEY: "${S2_API_KEY}"
  CUDA_VISIBLE_DEVICES: "0,1,2,3"
```

### 7.3 Integration Strategy
- Use RunPod's API to create pods programmatically
- SSH into pods for experiment execution (replaces RC's ssh_sandbox)
- Store results on network volumes for persistence across runs
- Use serverless endpoints for cost-efficient burst compute

---

## 8. MIGRATION GOALS & SUCCESS CRITERIA

### 8.1 Primary Goals
1. **Preserve research quality**: Anti-fabrication prompts, citation verification, methodology-evidence checking
2. **Upgrade experiment engine**: Replace RC's linear execution with AI-Scientist-v2's BFTS
3. **Maintain literature depth**: Keep multi-source search (OpenAlex + S2 + arXiv)
4. **Add visual feedback**: Leverage AI-Scientist-v2's VLM loop (RC doesn't have this)
5. **Keep self-evolution**: Port lesson extraction + time-decay overlay injection
6. **RunPod integration**: GPU compute via RunPod pods/endpoints instead of local/SSH

### 8.2 Non-Goals (Do Not Port)
- HITL system (AI-Scientist-v2 is fully autonomous)
- OpenClaw bridge (not relevant)
- MCP server (can be rebuilt later if needed)
- Colab Drive backend (replaced by RunPod)
- MetaClaw bridge (replaced by AI-Scientist-v2's own tool system)

### 8.3 Success Criteria
| Metric | Target |
|--------|--------|
| End-to-end pipeline completion | Topic to PDF paper in single run |
| Citation verification pass rate | >=90% of citations verified real |
| Experiment execution | BFTS with >=3 parallel workers on RunPod |
| Paper quality score | >=6/10 on automated review |
| Cost per run | <=$50 (experiments + LLM calls) |
| Domain coverage | At least ML, Physics, Biology adapters |

---

## 9. REFERENCE FILES INCLUDED

```
migration/reference_files/
  stages.py                    # 23-stage state machine (port gate logic)
  contracts.py                 # Stage I/O contracts (port to BFTS stages)
  executor.py                  # Stage dispatch table (reference for integration)
  runner.py                    # Pipeline orchestration (reference)
  config.py                    # RCConfig dataclass (reference for config design)
  llm_client.py                # LLM client with fallback chain
  acp_client.py                # Agent Client Protocol bridge
  evolution.py                 # Self-evolution system (PORT THIS)
  adapters.py                  # Adapter protocols
  config.researchclaw.example.yaml  # Full config template
  prompts.default.yaml         # ALL prompts (CRITICAL — port anti-fabrication)
  RESEARCHCLAW_CLAUDE.md       # Project overview
  RESEARCHCLAW_AGENTS.md       # Agent configuration
  pyproject.toml               # Dependencies
  stage_impls/                 # Per-stage implementation (reference)
    _topic.py
    _literature.py
    _synthesis.py
    _experiment_design.py
    _code_generation.py
    _execution.py
    _analysis.py
    _paper_writing.py
    _review_publish.py
  experiment/
    sandbox.py               # Code execution sandbox
    validator.py             # AST + security + import validation
  literature/
    search.py                # Multi-source paper search (PORT THIS)
    verify.py                # Citation verification (PORT THIS)
  agents/
    benchmark_agent/         # Benchmark discovery agent
    figure_agent/            # Scientific visualization agent
    code_searcher/           # GitHub code search agent
```

---

## 10. ARCHITECTURE DECISION: HYBRID APPROACH

The recommended migration is NOT a full rewrite. It is a **hybrid** where:

1. **AI-Scientist-v2 owns experimentation** (BFTS tree search, code gen, execution)
2. **ResearchClaw owns research methodology** (literature, citations, evolution, quality gates)
3. **New glue code** connects RC's pre-experiment pipeline to v2's BFTS engine and RC's post-experiment pipeline to v2's writeup

```
[RC Pre-Experiment]          ->  [AI-Scientist-v2 BFTS]           ->  [RC Post-Experiment]
 Topic -> Literature -> Hypotheses   Draft -> Baseline -> Research -> Ablation   Review -> Verify -> Evolve
           |                              |                              |
   RC Domain Adapters           v2 Parallel Workers              RC Evolution Store
   RC Multi-Source Search       v2 VLM Feedback                  RC Citation Verify
   RC Knowledge Cards           v2 Debug Retry                   RC Anti-Fabrication
```

This preserves the best of both systems while avoiding a risky full rewrite.
