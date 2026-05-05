# Cross-Examination: The Big-Picture Editor

**Paper:** SemCP: Coverage Guarantees Over Meanings, Not Strings
**Reviewer:** The Big-Picture Editor
**Date:** 2026-05-01
**Cross-Exam Period:** After reading all 8 other independent reviews

---

## 1. Disagreements with At Least 2 Other Reviewers

### D1: Theorem 1 Proof Has an Unresolved Selection Effect Gap (disagrees with 02_theory_critic)

**My original position:** I rated Theorem 1 as correct and the exchangeability argument as sound. I did not flag the admissibility-selection effect as a gap.

**Theory Critic's claim (02):** "The proof sketch invokes the standard split-conformal result on the lifted scores but does not address the selection bias introduced by conditioning on the admissibility set I. In standard split-conformal, the calibration set is fixed before threshold computation. Here, the admissibility set I is selected post-hoc based on which calibration examples happened to have their true meaning sampled. This creates a selection effect: the threshold is computed over a subset of calibration points that are systematically easier."

**My updated position:** The Theory Critic is correct. The admissibility subset I is not fixed before observing the data — it is a random variable that depends on which calibration examples happened to produce a correct sample. Computing qhat over this post-hoc selected subset introduces a selection bias that is not addressed in the proof sketch. The standard split-conformal argument requires the calibration set to be exchangeable with the test point before threshold computation. Conditioning on admissibility changes the distribution of the admissible subset in a way that is not trivially handled. I now agree this is a genuine theoretical gap (Severity 3) that requires either (a) a formal proof that exchangeability is preserved within the admissible subset, or (b) a revised theorem statement that accounts for the selection effect explicitly.

### D2: Baseline Hyperparameter Tuning Asymmetry (disagrees with 01_methodological_hawk)

**My original position:** I did not raise baseline hyperparameter tuning as a concern. I noted only that code was not released and experiments were not run.

**Methodological Hawk's claim (01):** "SemCP's bandwidth sigma is optimized on a held-out split via grid search. LofreeCP's length regularizer lambda=0.5 is taken from the public implementation without confirmation it was retuned for Qwen2.5-7B-Instruct. TECP's score computation is the same as in its original paper, but it's unclear whether the hyperparameters were tuned for this experimental regime. SAFER's abstention threshold of 0.10 is fixed, not optimized. An asymmetric tuning effort where only the proposed method gets data-driven hyperparameter selection is a classic experimental design flaw."

**My updated position:** This is a legitimate concern I missed. If only SemCP receives data-driven hyperparameter optimization while baselines use off-the-shelf defaults, the efficiency comparison is unfair. The set-size advantage (13.35 vs 18.57 vs 18.83) could partially reflect hyperparameter selection asymmetry rather than intrinsic method quality. I now rate this as Severity 3. The resolution requires either equivalent tuning effort for all baselines, or explicit sensitivity analysis showing baseline results are robust across reasonable hyperparameter ranges.

### D3: NLI Partition Transitivity Assumption Is Practically Unjustified (disagrees with 02_theory_critic)

**My original position:** I accepted the Union-Find closure over bidirectional NLI as a reasonable instantiation of the partition rule without questioning the transitivity assumption.

**Theory Critic's claim (02):** "DeBERTa-v2-xlarge-MNLI is not logically consistent — NLI models are known to have non-transitive behavior due to annotation artifacts and dataset biases. The Union-Find closure over pairwise NLI judgments can therefore produce equivalence classes that violate actual semantic equivalence."

**My updated position:** This is a valid concern. If bidirectional entailment at threshold 0.5 produces A entails B and B entails C but not A entails C (a known NLI inconsistency pattern), the Union-Find closure will force A and C into the same equivalence class despite the model's own judgments suggesting otherwise. The paper acknowledges the NLI threshold is fixed and not ablated, but does not analyze the consequence of partition error on coverage. If the NLI partition conflates distinct meanings (false positive in the equivalence relation), coverage could be compromised because strings with different meanings would be treated as exchangeable. This needs theoretical analysis (robustness bound on partition error) or empirical validation (sensitivity of results to NLI threshold).

### D4: Algorithm 1 Does Not Match the Theory (disagrees with 09_naive_reader)

**My original position:** I described Algorithm 1 as clear and readable without noticing a structural mismatch with Section 4.3.

**Naive Reader's claim (09):** "Algorithm 1 line 180 says the lifted score for calibration is `1 - max_{c' != c_i^*} kappa_sigma(bars_phi_{c_i^*}, bars_phi_{c'})` where c_i^* is the correct cluster. But the text (Section 4.3, Equation 2) defines the lifted score as `min_{y' in [y]_s intersect {y_1,...,y_K}} s(x,y')` where s(x,y) = 1 - kappa_theta(phi(y), mu_x) and mu_x is the kernel mean embedding of ALL K samples. These are structurally different: one computes a contrast score between clusters; the other computes the minimum score within a cluster relative to the sample centroid. The algorithm and the theory are solving different problems."

**My updated position:** The Naive Reader is correct and this is more serious than I initially rated it. The contrastive between-cluster formulation in Algorithm 1 is fundamentally different from the within-cluster min-aggregation in the theory. The theory says a meaning class is conforming if ANY of its string representatives has low nonconformity. The algorithm says a cluster is conforming if it contrasts well with the nearest incorrect cluster. These are opposite optimization directions. I now rate this as Severity 4 — an implementer following Algorithm 1 would not reproduce the method described in the theory. This needs explicit resolution by the authors: either the algorithm is corrected to match the theory, or the theory is revised to match the algorithm.

---

## 2. Issues Others Missed That I Now Want to Add

### IA1: The Admission of Incomplete Experiments Should Trigger Immediate Rejection

Multiple reviewers (01, 02, 03, 04, 05, 06, 07, 09) independently identified TODO_NUM placeholders as the primary weakness. However, none framed this as a systemic integrity issue. The paper's abstract contains TODO_NUM placeholders while the NeurIPS checklist item 5 says "Code and run logs are released for reproducibility" — this is a direct factual contradiction. The paper presents unfalsified empirical claims as if they were established findings (33% reduction, coverage near 0.89, set sizes of 13.35). A paper that submits TODO_NUM as real-looking results is not ready for review; it is an intent-to-submit dressed as a completed submission. No amount of theoretical quality can compensate for submitting placeholder results.

### IA2: Semantic Entropy Prior Work Is Under-Cited

The paper identifies "semantic entropy has no coverage guarantee" as the gap it fills, and Domain Expert ML (06) correctly notes that the original semantic entropy papers (e.g., ACL/ICLR 2024 on hallucination detection via semantic entropy clustering) are not explicitly cited. The claim that "no prior work provides CP over meanings" is strong and requires exhaustive enumeration of semantic clustering / uncertainty quantification literature. I also missed the anisotropy correction literature (Ethayarajh 2019, Mueller et al. 2022) — the paper uses frozen MiniLM embeddings and acknowledges anisotropy as a known pathology but does not engage with the correction literature.

### IA3: The "33% Set-Size Reduction" Is Incompatibly Married to "Near-Zero Coverage"

The paper claims both "33% smaller set sizes than the strongest string-level baseline" and "near-zero coverage for all methods due to low generator quality." These cannot both be true in the same experiment. If coverage is near-zero, conformal sets collapse to empty sets — all methods produce set size 0, and the 33% comparison is between zeros. This is not a minor inconsistency; it is a logical impossibility in the same experimental run. The paper must clarify whether the 33% claim is (a) from a different experiment than the near-zero coverage observation, (b) hypothetical projections from the ablation study, or (c) fabricated. I raised this as W3 but underweighted its severity — it should be a Severity 5 reject-level issue because it suggests the numbers in the paper come from different experimental configurations that were never reconciled.

### IA4: The Many-to-One Calibration Logic Implies a Hidden Assumption About Calibration Set Composition

The paper computes the conformal threshold qhat over the admissible subset I (calibration examples where the true meaning was sampled). This means qhat is fit on a biased subset — only "easy" calibration examples where the generator happened to produce a correct answer. The theory does not explicitly address what this selection bias does to the validity of the threshold. In standard split-conformal, the calibration set is representative of the test distribution. Here, the admissible subset is systematically easier than the full calibration set. If the inadmissible calibration examples (where no correct answer was sampled) have systematically different score distributions, qhat is biased downward, leading to anti-conservative coverage. This is related to the Theory Critic's selection effect concern but is distinct — it is about the statistical properties of the threshold, not just the exchangeability argument.

---

## 3. My Own Positions Updated After Seeing the Consensus

### UC1: Soundness Score Should Be Lower (from 3 to 2)

**Original:** I rated Soundness 3/10, citing the TODO_NUM problem as the primary issue but assuming the theory was sound and experiments just needed to be run.

**Consensus signal:** The Theory Critic identified a genuine gap in Theorem 1's proof (admissibility selection effect). The Naive Reader identified a critical Algorithm-theory mismatch. The Methodological Hawk identified asymmetric baseline tuning. These are not just missing experiments — they are methodological issues that affect how the theory would perform if experiments were run. I now believe Soundness should be 2/10: the TODO_NUM problem is fatal, the proof has an unaddressed gap, and the Algorithm-theory mismatch means we do not know what method is actually being evaluated.

### UC2: Clarity Score Should Be Lower (from 7 to 5)

**Original:** I rated Clarity 7/10, noting minor issues but finding the paper mostly well-organized.

**Consensus signal:** Seven out of eight reviewers noted the GPT-2 vs Qwen2.5-7B-Instruct inconsistency in Figure 3. Three reviewers (09_naive_reader, 01_methodological_hawk, 02_theory_critic) noted the partition method inconsistency between Section 4.1 and Section 5.1. The Naive Reader identified the Algorithm-theory mismatch. These are not minor clarity issues — they are factual inconsistencies that make it unclear what method was actually evaluated. A score of 7/10 implies "mostly clear, some sections require re-reading." The actual state is "internally contradictory in multiple places, unclear what method was implemented." Revised Clarity: 5/10.

### UC3: Reproducibility Score Should Be Lower (from 4 to 2)

**Original:** I rated Reproducibility 4/10, noting code was promised upon publication and methods were described in sufficient detail.

**Consensus signal:** Every reviewer rated Reproducibility at 2-4/10. The TODO_NUM placeholders mean even the experimental setup cannot be verified. The figure caption referencing the wrong model means we cannot trust what experiments were run. Code is not released. The NeurIPS checklist claim of released code is contradicted by the paper text. Revised Reproducibility: 2/10.

---

## 4. The Claim/Weakness with the Most Reviewer Agreement (Consensus Signal)

### Consensus Weakness: All Empirical Results Are TODO_NUM Placeholders

**Agreement:** ALL 9 reviewers flagged this as critical (Severity 4-5/5). The only variation was whether to call it Severity 4 or 5, and whether the rating should be "Reject" or "Borderline with path to Accept."

**Citation count:** 9/9 reviewers noted this weakness.

**Implication:** This is not a controversial or close call. The paper's empirical foundation does not exist in any verifiable form. Any revision of this paper must begin with running the experiments.

### Secondary Consensus: Figure 3 Caption References Wrong Model

**Agreement:** 8/9 reviewers (all except 07_reproducibility_archeologist, who focused on different issues) flagged the GPT-2 vs Qwen2.5-7B-Instruct inconsistency.

**Citation count:** 8/9 reviewers.

**Implication:** This is not a minor typo — it suggests the paper was assembled from template text without final consistency checking. Combined with the TODO_NUM problem, it raises a broader concern about the integrity of the experimental narrative.

### Tertiary Consensus: Near-Zero Coverage Claim Contradicts 33% Set-Size Reduction

**Agreement:** 4/9 reviewers (03_empirical_skeptic, 04_statistical_rigorist, 05_adversarial_practitioner, 08_big_picture_editor) flagged this as a critical internal incoherence. 3 others noted it at lower severity.

**Citation count:** 7/9 total (4 at high severity, 3 at medium).

**Implication:** The paper cannot simultaneously claim meaningful set-size reduction and near-zero coverage — these are logically incompatible in the same experiment. This suggests the numbers come from different experimental configurations that were never reconciled.

---

## 5. Updated Per-Rubric Scores and Decision

### Updated Scores

| Dimension | Original Score | Revised Score | Reason for Change |
|-----------|---------------|---------------|-------------------|
| **Originality / Novelty** | 7 | 7 | No change — quotient-space CP framing is genuinely novel; consensus 7-8 |
| **Soundness** | 3 | 2 | Theorem 1 has unaddressed selection effect gap; Algorithm-theory mismatch identified; experiments absent |
| **Significance** | 6 | 6 | No change — if experiments hold, 33% set-size reduction is meaningful; admissibility decomposition is useful |
| **Clarity** | 7 | 5 | GPT-2/Qwen mismatch, partition method inconsistency, Algorithm-theory mismatch create multiple unresolved contradictions |
| **Reproducibility** | 4 | 2 | All numbers are TODO_NUM; code not released; figure caption wrong model; cannot be reproduced |
| **Contextualization vs Prior Work** | 7 | 7 | Strong related work; semantic entropy citation gap noted but does not change score |
| **Ethical / Broader Impact** | 6 | 6 | No change — adequate boilerplate |

**Revised Weighted Average:** `(7*1.0 + 2*1.5 + 6*1.0 + 5*0.7 + 2*1.0 + 7*0.8 + 6*0.5) / 6.5` = `(7 + 3.0 + 6 + 3.5 + 2 + 5.6 + 3) / 6.5` = `30.1 / 6.5` = **4.6**

### Revised Decision: Reject

**Decision boundary:** 4.6 falls in the Reject range (4.0-5.5).

**Rationale:** The theoretical contribution (quotient-space conformal prediction, admissibility decomposition, kernel-based lifted scores) is genuine and would be valuable if empirically validated. However, the paper in its current form has:

1. No experimental results — all Table 1 entries are TODO_NUM placeholders
2. A figure caption that references the wrong model (GPT-2 instead of Qwen2.5-7B-Instruct)
3. A logical impossibility: near-zero coverage claims coexist with a 33% set-size reduction claim
4. An unresolved theoretical gap: the admissibility selection effect in Theorem 1's proof
5. A critical Algorithm-theory mismatch: Algorithm 1 and Section 4.3 define different procedures
6. No released code

The Theory Critic's identification of the selection effect gap and the Naive Reader's identification of the Algorithm-theory mismatch are issues I originally missed and now consider serious. The asymmetric baseline tuning concern from the Methodological Hawk is also valid and was absent from my original review.

**What would change the decision to Accept:** The authors would need to (1) run all experiments and populate Table 1 with real numbers, (2) resolve the Algorithm-theory mismatch, (3) address the admissibility selection effect in Theorem 1's proof, (4) fix the Figure 3 caption, (5) reconcile the near-zero coverage claim with the 33% set-size reduction claim, (6) release code, and (7) perform equivalent hyperparameter tuning for all baselines.

**Path to future submission:** This paper has the bones of a strong contribution. The theoretical framework is novel and correct. The admissibility-coverage decomposition is a useful diagnostic. If the experiments are run and the above issues are addressed, this could be a competitive submission. As submitted, it is a Reject.

---

*— The Big-Picture Editor, updated after cross-examination*