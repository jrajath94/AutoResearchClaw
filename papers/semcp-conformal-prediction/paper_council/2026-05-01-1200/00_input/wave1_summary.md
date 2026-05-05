# Wave 1 Summary: 9 Independent Reviews

## Verdict Distribution
- REJECT: 1 (Methodological Hawk, 2/5 confidence)
- CONDITIONAL ACCEPT: 5 (Theory Critic, Statistical Rigorist, Adversarial Practitioner, Empirical Skeptic, Naive Reader) — avg 3/5 confidence
- WEAK ACCEPT: 2 (Domain Expert, Big Picture Editor) — avg 3.75/5 confidence

**Average Score: 7.0/10 | Average Confidence: 3.1/5 | Consensus: BORDERLINE**

## Strongest Consensus Points (6+ reviewers agree)

### ✅ STRENGTHS CONFIRMED
1. **Theory-practice alignment exceptional** — empirical coverage gaps ±0.02 from Theorem 1 bound on TriviaQA/SQuAD
2. **Reproducibility exemplary** — CLAIM_AUDIT.md, 3-seed validation, anonymous code ready
3. **Semantic-level framing novel** — genuine problem (token-space vs semantic-space CP)
4. **Plug-in bandwidth clever** — Theorem 2 closes only hyperparameter tuning need
5. **M-SemCP unification elegant** — recovers ConU/TECP/LofreeCP as corners

### ❌ WEAKNESSES CONFIRMED
1. **NQ-open collapse (p_A=0.27)** — 73% inadmissible; silently breaks guarantees on hard distributions (6/9 flagged)
2. **Clarity gaps on fundamentals** — Theorem 1 notation (α, |I|) undefined; CP background missing; HAC-NLI underspecified (5/9 flagged)
3. **Generalization unvalidated** — only factoid QA; K=10 arbitrary; no OOD tests; embedding dependency single point of failure (4/9 flagged)
4. **Empirical gains inconsistent** — 64% set-size inflation on TriviaQA (regression not improvement), 5% on SQuAD, 0% on NQ-open (4/9 flagged)
5. **Statistical rigor gaps** — no significance tests, no CIs on probabilistic claims, 24+ comparisons uncorrected (3/9 flagged)

## Critical Disagreements

| Reviewer | Position | Rationale |
|----------|----------|-----------|
| **Methodological Hawk** | REJECT | Table 1 unfilled (TODO_NUM); hyperparameter tuning asymmetry suspicious |
| **Domain Expert ML** | WEAK ACCEPT | Novelty + reproducibility outweigh empirical gains; borderline |
| **Big Picture Editor** | ACCEPT | Paradigm-shift framing matters more than current gains |
| **Empirical Skeptic** | WEAK PASS | Brittleness on NQ-open is "refutation not confirmation" of main claim |

## Blocking Issues (Must Fix for Acceptance)

### P0 — Theory
1. **Theorem 2 incomplete** — notation undefined (μ̄μ, μ̄W), derivation absent, sub-Gaussian constants missing. Proof must be complete + empirically validated.

### P0 — Empirical
2. **NQ-open admissibility collapse undiagnosed** — p_A=0.27 is root cause of failure; must explain why or scope claims to "easy factoid QA only"
3. **K=10 budget unjustified** — no sensitivity analysis on high-entropy questions; arbitrary constraint

### P1 — Clarity
4. **Theorem 1 notation undefined** — α and |I| never defined in paper; readers cannot assess coverage guarantee
5. **Conformal prediction background missing** — 50% of readers blocked on foundational concepts
6. **Admissibility-selection conditioning unexplained** — load-bearing assumption; failure risk unmeasured

### P1 — Reproducibility
7. **RNG non-determinism** — seed=42 hardcoded in algorithm; breaks σ* reproducibility across experiment seeds
8. **Hardware/software pinning incomplete** — no CUDA/cuDNN/PyTorch versions; floating-point order non-deterministic

## Questions Raised (Consensus across reviewers)

1. **Why does NQ-open fail?** Is it task difficulty (p_A inherent) or NLI model brittleness (DeBERTa-specific)?
2. **What is the actual practical impact?** Set-size inflation on easy tasks negates gains; admissibility constraint makes marginal coverage unattainable on hard tasks.
3. **Is NLI model dependency fatal?** Single point of failure (DeBERTa-v3-large); no ablation on alternative NLI models.
4. **Can M-SemCP actually blend?** Empirically it selects corners; formal proof or ablation needed.
5. **How much of the result is generator quality (p_A) vs. kernel design?** Ablation study comparing different generators + NLI models needed.

## Falsifiability Tests (Reviewers Validated)

- ✅ **Tight coverage claim:** Empirically confirmed on TriviaQA/SQuAD (gap ≈ 0), falsified on NQ-open (still valid but not tight)
- ❌ **"Comparable set sizes" claim:** FALSIFIED — 64% inflation on TriviaQA, sets are larger not comparable
- ⚠️ **"Generalizable framework" claim:** INDETERMINATE — only 3 datasets, all factoid QA; OOD evidence absent

---

## Reviewer Confidence Breakdown

**High Confidence (4+/5):**
- Domain Expert ML (4/5) — "SOTA positioning clear"
- Big Picture Editor (3.5/5 → round to 4) — "Framing impact 5-year vision"

**Medium Confidence (3/5):**
- Theory Critic, Statistical Rigorist, Empirical Skeptic, Naive Reader — "Theory solid, empirics mixed"

**Low Confidence (≤2.5/5):**
- Methodological Hawk (2/5) — "Table 1 unfilled; cannot verify"
- Adversarial Practitioner (2.5/5) — "Production deployment risky"
- Reproducibility Archaeologist (2/5) — "Non-determinism breaks claims"

---

## Synthesis for Deliberation (Wave 2)

**Cross-Exam Focus:** 
- Hawk vs. Others: Why is methodological rigor (hyperparameter tuning, table completeness) not blocking acceptance?
- Skeptic vs. Others: How do reviewers rationalize NQ-open failure as "still valid" vs. "refutation"?
- Practitioner vs. Others: Is production brittleness acceptable for a theory paper?

**Red-Team Targets:**
1. Claim: "SemCP achieves tightest valid conditional coverage" — TRUE on TriviaQA/SQuAD, FALSE on NQ-open (still valid but gap +0.012)
2. Claim: "Plug-in bandwidth removes tuning" — PARTIALLY TRUE (σ̂ matches grid-search 5%) but assumes sub-Gaussian (unvalidated)
3. Claim: "M-SemCP unifies CP variants" — OBSERVATION not theorem; empirically selects corners, no blending

**Steelman Targets:**
1. NQ-open is an *upper bound on difficulty* for open-domain QA; even achieving 0.9 coverage with p_A=0.27 is theoretically impressive
2. Reproducibility checklist (15/15 passed) + honest admissibility reporting (no obfuscation) earns trust recovery
3. Novelty (semantic-space framing) justifies borderline accept despite empirical limitations
