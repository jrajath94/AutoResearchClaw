# Synthesized Research Hypotheses for SemCP

---

## Preamble: Key Tensions Across Perspectives

Before presenting the final hypotheses, I want to name three genuine disagreements that emerged across the innovator, pragmatist, and contrarian perspectives. These are not resolvable by compromise — they represent real scientific uncertainty that the experiments below are designed to adjudicate.

**Tension 1: Is embedding space a reliable foundation?** The innovator and pragmatist treat sentence embeddings as a usable (if imperfect) semantic representation. The contrarian argues that anisotropy, non-transitivity, and negation-blindness make them fundamentally unreliable for coverage guarantees. This is an empirical question, and Final Hypothesis 1 is designed to resolve it.

**Tension 2: Is set size reduction the right objective?** The pragmatist optimizes for smaller prediction sets. The contrarian argues that smaller sets destroy calibration signal and may harm downstream task performance. This cannot be settled by theory — it requires head-to-head comparison on operational metrics, which Final Hypothesis 2 addresses.

**Tension 3: Where does conformal prediction stop being meaningful?** The contrarian's strongest point is that "coverage over meanings" may be vacuous for open-ended generation where ground truth does not exist. The pragmatist implicitly restricts scope to factual QA. Final Hypothesis 3 maps this boundary explicitly rather than assuming either position.

---

## Final Hypothesis 1: Embedding-Space Conformal Prediction With Isotropic Correction and Adversarial Stress Testing

*Synthesizes: Pragmatist H1 (BERTScore nonconformity), Contrarian CH1 (embedding collapse critique), Innovator H3 (adversarial robustness)*

**Claim:** BERTScore-based nonconformity scores produce conformal prediction sets that are genuinely 20-35% smaller than token-level log-probability sets at valid coverage — but only after isotropic correction of the embedding space, and only on inputs without adversarial semantic perturbations. On adversarially constructed inputs (negation, entity swaps), uncorrected SemCP loses at least 8 percentage points of coverage, while isotropically-corrected SemCP loses at most 4.

**Why this synthesis:** The pragmatist's BERTScore approach is the simplest viable implementation — no TDA, no optimal transport, just a well-validated similarity metric. But the contrarian's embedding collapse critique is too well-evidenced to ignore. Rather than assuming embeddings work or assuming they fail, we test both the uncorrected and corrected versions against both clean and adversarial data. This produces a 2x2 matrix that maps the actual reliability boundary.

**Methodology:**
1. Model: Llama-3-8B via vLLM. Datasets: TriviaQA (1000 cal / 1000 test) + a negation-augmented variant (200 examples where 20% of candidates have key facts negated).
2. Compute four nonconformity score variants:
   - (a) Token-level negative log-prob (baseline)
   - (b) 1 - BERTScore-F1 with raw DeBERTa-large embeddings
   - (c) 1 - BERTScore-F1 with whitened embeddings (ZCA whitening on calibration set, following Gao et al., 2021)
   - (d) 1 - BERTScore-F1 with whitened embeddings + adversarial calibration (shift each calibration embedding epsilon toward its nearest different-meaning neighbor)
3. Calibrate all four at alpha=0.10. Evaluate on clean TriviaQA test set and negation-augmented test set.
4. Measure: empirical coverage, mean prediction set size (semantic clusters at BERTScore > 0.92), anisotropy of embedding distribution (measured as explained variance ratio of top-10 PCA components).

**Measurable Predictions:**
- On clean TriviaQA: all four methods achieve valid coverage (0.89-0.92). Raw BERTScore sets are 30-50% smaller than token-level. Whitened BERTScore sets are 20-35% smaller (honest reduction after removing anisotropy artifact). The gap between raw and whitened reveals the anisotropy tax.
- On negation-augmented TriviaQA: raw BERTScore coverage drops to 0.80 or below (confirming the contrarian's critique). Whitened BERTScore coverage drops to 0.84-0.87. Adversarially-calibrated whitened BERTScore maintains 0.88+.
- Anisotropy metric: top-10 PCA components explain more than 60% of variance in raw embeddings (confirming anisotropy), dropping below 40% after whitening.

**Failure Conditions:**
- If raw and whitened BERTScore sets are within 5% of each other in size on clean data, anisotropy is not a meaningful confounder and the contrarian's critique is overblown.
- If adversarial calibration inflates sets by more than 35% on clean data, the robustness-efficiency tradeoff is unfavorable and adversarial calibration is not practical.
- If all semantic-score variants fail to achieve at least 15% set size reduction over token-level on clean data, the core SemCP premise is falsified.

**Resources:** 1x A100, ~30 minutes. Generation (~18 min), BERTScore + whitening (~3 min), calibration + evaluation (~2 min), adversarial perturbation (~30 sec).

**Unresolved Disagreement:** The innovator argues for more exotic scores (TDA persistence, Wasserstein quotient). This hypothesis deliberately uses the simplest possible semantic score. If BERTScore with isotropic correction already works well, exotic alternatives may be unnecessary. If it fails on adversarial data even with correction, that motivates the innovator's more ambitious approaches as a follow-up — but the simple baseline must be established first.

---

## Final Hypothesis 2: Set Size Reduction vs. Downstream Task Performance — The Honest Evaluation

*Synthesizes: Pragmatist H3 (hallucination detection), Contrarian CH2 (redundancy is information), Pragmatist H2 (cluster-then-calibrate)*

**Claim:** SemCP's meaning-level prediction sets and token-level prediction sets serve different operational purposes. For hallucination detection (binary: is the output factual?), SemCP matches or slightly outperforms token-level methods. For selective abstention (ordinal: how uncertain should I be?), token-level sets provide better-calibrated uncertainty signals due to their richer probability mass information. The optimal approach is a hybrid: use cluster-level sets for hallucination flagging, but report intra-cluster string counts as an auxiliary calibration signal for abstention.

**Why this synthesis:** The contrarian's point that collapsing paraphrases destroys the 15:2 ratio information is genuinely important and under-explored. But the pragmatist's observation that conformal thresholds provide principled hallucination detection is also valid. Rather than arguing about which is better in general, we measure both on both tasks and let the data resolve it. The hybrid prediction — that different tasks want different levels of semantic abstraction — is more interesting than either pure position.

**Methodology:**
1. Dataset: TruthfulQA (400 cal / 417 test). Model: Llama-3-8B, 1 primary + 10 sampled responses per question.
2. Construct three prediction set types:
   - (a) Token-level: include strings with log-prob above conformal threshold.
   - (b) SemCP cluster-level: cluster responses (agglomerative, cosine threshold 0.3 on MiniLM embeddings), calibrate at cluster level. Report set = set of meaning clusters.
   - (c) Hybrid: SemCP cluster-level sets, but annotated with intra-cluster string counts (e.g., {meaning_A: 8 strings, meaning_B: 2 strings}).
3. Task 1 — Hallucination detection: for each method, use the nonconformity score as a binary hallucination detector. Compute AUROC against TruthfulQA truthfulness labels. For the hybrid, test whether adding the string-count ratio as a second feature improves AUROC (logistic regression on score + ratio vs. score alone).
4. Task 2 — Selective abstention: retain top-k% of examples by confidence (inverse of set size for token/cluster; inverse of max-cluster string count for hybrid). Measure retained-set accuracy at 70% and 50% retention rates.
5. Task 3 — Uncertainty-error correlation: Spearman rho between prediction set size and binary correctness for each method.

**Measurable Predictions:**
- Hallucination AUROC: SemCP cluster-level achieves 0.71-0.76, token-level achieves 0.68-0.73, hybrid achieves 0.74-0.79. SemCP and hybrid are within 3 points of SelfCheckGPT baseline (0.74-0.78). The hybrid's second feature (string count ratio) improves AUROC by 2-4 points over cluster-level alone.
- Selective abstention at 70% retention: token-level retained accuracy exceeds SemCP cluster-level by 2-5 percentage points. Hybrid matches or exceeds token-level by incorporating both signals.
- Uncertainty-error Spearman rho: token-level rho >= 0.40, SemCP cluster-level rho 0.28-0.38, hybrid rho >= 0.42.

**Failure Conditions:**
- If SemCP cluster-level wins on both hallucination detection AND abstention, the contrarian's "redundancy is information" thesis is wrong and set size reduction is a genuine operational improvement.
- If token-level wins on both tasks, SemCP provides no operational benefit and set size reduction is indeed a vanity metric.
- If the hybrid shows no improvement over the better of the two pure methods on either task, the synthesis is unnecessary complexity.

**Resources:** 1x A100, ~15-20 minutes. TruthfulQA is small (817 examples); generation and scoring are the same infrastructure as Final Hypothesis 1.

**Unresolved Disagreement:** The contrarian argues that semantic equivalence is task-dependent ("Barack Obama" vs. "Obama"). This experiment uses a fixed clustering threshold and a single task domain. If results are strong, the next question is whether the threshold needs per-task adaptation — but establishing baseline performance on any one task comes first.

---

## Final Hypothesis 3: Mapping the Boundary — Where Conformal Coverage Is Meaningful vs. Vacuous

*Synthesizes: Contrarian CH3 (coverage vacuous for open-ended generation), Pragmatist H2 (cluster-then-calibrate as practical solution), Innovator H2 (Wasserstein quotient for continuous meaning spaces)*

**Claim:** SemCP achieves valid and informative coverage (small sets, correct coverage, meaningful conditional coverage) on closed-form QA tasks, but prediction sets become either vacuously large or conditionally miscalibrated as tasks become more open-ended. The boundary is quantifiable: SemCP works when the expected number of semantically distinct valid responses per prompt is fewer than 5, and fails when it exceeds 10. This boundary can be predicted from a simple pre-experiment statistic (response diversity index: mean pairwise cosine distance among 20 sampled responses).

**Why this synthesis:** The contrarian's most powerful argument is that "coverage over meanings" is undefined when the meaning space is unbounded. Rather than contesting this philosophically, we operationalize it: measure SemCP's performance across a spectrum of task openness, identify where it breaks, and provide a simple diagnostic that practitioners can use to decide whether SemCP applies to their use case. This is more useful than either the claim "SemCP works universally" or "SemCP never works for open-ended tasks."

**Methodology:**
1. Three datasets spanning a task-openness spectrum:
   - Closed: TriviaQA (factual QA, single correct answer). 500 cal / 500 test.
   - Medium: ELI5 (open-ended explanation, multiple valid approaches). 500 cal / 500 test.
   - Open: WritingPrompts (creative story continuation, effectively unbounded). 500 cal / 500 test.
2. Model: Mistral-7B via vLLM. Generate 20 candidate responses per prompt (nucleus sampling, p=0.95, temperature=1.0).
3. For each dataset, compute:
   - Response Diversity Index (RDI): mean pairwise cosine distance among 20 responses, averaged over all prompts. This is the pre-experiment diagnostic.
   - SemCP prediction sets using cluster-then-calibrate (Final Hypothesis 1's best method, likely whitened BERTScore).
   - Token-level prediction sets (baseline).
4. Evaluate: marginal coverage, conditional coverage by prompt difficulty decile (measured by model perplexity), mean set size, set size as fraction of total candidates (vacuity measure).

**Measurable Predictions:**
- TriviaQA (RDI expected ~0.25): Valid marginal coverage (0.89-0.92), valid conditional coverage (all deciles within 5% of nominal), set size 35-55% smaller than token-level. SemCP works as advertised.
- ELI5 (RDI expected ~0.45): Marginal coverage holds (0.89-0.92), but conditional coverage degrades — hardest 20% of prompts have coverage below 0.80. Set size reduction shrinks to 15-25%. SemCP is partially useful but requires caveats.
- WritingPrompts (RDI expected ~0.60): Either (a) prediction sets include more than 70% of candidates (vacuously large), or (b) conditional coverage on the hardest 30% of prompts drops below 0.65 while marginal coverage stays at 0.90. Set size reduction vs. token-level is less than 10%. SemCP provides little value.
- The RDI threshold for "SemCP works" (valid conditional coverage within 5% of nominal for all deciles) falls between 0.30 and 0.50.

**Failure Conditions:**
- If SemCP achieves valid conditional coverage on all three datasets, the contrarian's "vacuous for open-ended tasks" thesis is wrong. This would be a strong positive result for SemCP.
- If SemCP fails even on TriviaQA (conditional miscoverage or no set size reduction), the method has fundamental problems beyond task openness.
- If RDI does not predict SemCP viability (e.g., two datasets with similar RDI have dramatically different SemCP performance), then task openness is not the operative variable and the boundary is elsewhere.

**Resources:** 1x A100, ~30 minutes. Three datasets x 500 examples x 20 candidates = 30,000 generations, feasible with vLLM batching in ~20 minutes. Embedding and clustering add ~5 minutes.

**Unresolved Disagreement:** The innovator's Wasserstein quotient approach could theoretically handle continuous meaning spaces (which is precisely what fails on WritingPrompts). If Final Hypothesis 3 confirms the boundary, the Wasserstein approach becomes the natural follow-up for extending SemCP beyond closed-form QA — but it requires significantly more theoretical development and is not testable within the 30-minute budget.

---

## Execution Plan and Dependencies

```
Phase 1 (25-30 min, 1 GPU):
  Final H1 — Embedding reliability + isotropic correction
  ├── Establishes: which nonconformity score to use for H2 and H3
  └── Resolves: anisotropy critique (Contrarian CH1)

Phase 2 (15-20 min, 1 GPU):
  Final H2 — Set size vs. downstream performance
  ├── Requires: best score from H1
  ├── Establishes: whether SemCP helps operationally, not just metrically
  └── Resolves: "redundancy is information" critique (Contrarian CH2)

Phase 3 (25-30 min, 1 GPU):
  Final H3 — Task-openness boundary mapping
  ├── Requires: best method from H1 + H2
  ├── Establishes: SemCP's honest scope of applicability
  └── Resolves: "vacuous for open-ended" critique (Contrarian CH3)

Total: ~70-80 minutes sequential on 1 GPU, or ~30 min parallel on 3 GPUs.
```

---

## What We Learn From Each Outcome

| If... | Then... | Impact |
|---|---|---|
| H1 shows whitening matters a lot | SemCP's claimed gains are inflated; honest reduction is 20-35%, not 40-65% | Revises central claim; still publishable but more honest |
| H1 shows adversarial inputs break coverage | SemCP needs robustness extensions before deployment | Opens follow-up on adversarial calibration |
| H2 shows token-level wins on abstention | Set size is a vanity metric; hybrid approach needed | Reframes contribution from "smaller sets" to "task-appropriate sets" |
| H2 shows hybrid wins everywhere | Best of both worlds exists; neither pure approach is optimal | Strongest possible paper: novel method + practical wisdom |
| H3 maps a clear RDI boundary | SemCP has an honest scope; practitioners can self-diagnose | Most citable result: boundary condition paper |
| H3 shows SemCP works even on open-ended tasks | Contrarian wrong; SemCP is more general than expected | Strongest positive result for SemCP |

The meta-insight across all three hypotheses: the most impactful SemCP paper is not one that claims universal improvement, but one that honestly characterizes when semantic conformal prediction helps, when it does not, and why. Mapping failure modes is more valuable than hiding them.