# Red Team Attack Report — SemCP

**Target:** SemCP: Coverage Guarantees Over Meanings, Not Strings
**Date:** 2026-05-01
**Role:** Red Team Agent — adversarial attack, failure mode analysis, retractability assessment

---

## EXECUTIVE SUMMARY

Every reviewer identified the same blocking flaw: all empirical results are TODO_NUM placeholders. The paper is not submittable in its current form. However, my job is to find attacks that would survive *even if* the experiments were run. Here are attacks that would make the paper **retractable post-publication**.

---

## TOP 3 CENTRAL CLAIMS AND ADVERSARIAL ATTACKS

### CLAIM 1: Theorem 1 — Conditional semantic coverage guarantee `1 - alpha - 1/(|I|+1)` given admissibility

#### What Would Refute This?

The proof sketch in Section 4.4 uses the augmented tuple view (Remark 2) to argue exchangeability is preserved when the kernel mean embedding depends on the random sample set. The critical step is that `mu_x` is computed from the *sampled* responses `{y_1, ..., y_K}`, and the score `s(x,y)` uses this random embedding.

**Refutation attempt:** Construct a case where the kernel mean embedding `mu_x` is informatively correlated with the true label, such that two instances with identical true meanings but different response sets receive systematically different nonconformity scores — even after conditioning on admissibility. Specifically:

- Instance A generates K=10 samples, 3 of which happen to be semantically close to the true answer
- Instance B generates K=10 samples, 0 of which are close (but admissibility still holds because the true meaning class was sampled via a different surface form)
- The kernel mean embedding `mu_A` shifts toward the true meaning class for A but not for B
- The conformal threshold `q_hat`, calibrated on the admissibility subset, is computed from a biased distribution of scores — systematically lower for instances where the samples happened to cluster near the true meaning

**The reductio-ad-absurdum:** Push K to the limit. If K=1, the kernel mean embedding is just the single sample's embedding. If that sample is wrong, the score is maximized (worst nonconformity) and the instance is excluded from the admissibility set. But if K=1000, `mu_x` converges to the true distribution. The conformal threshold `q_hat` computed from the admissibility subset is a function of how "lucky" the random samples were — not solely of the generator's quality. Theorem 1 does not bound this sample-dependent bias.

**Failure mode that would make the paper retractable:** The admissibility-selection proof gap identified by the Theory Critic is real. The threshold `q_hat` is computed over the subset `I = {i : A_i = 1}` — i.e., calibration examples whose true meaning was sampled. This subset is selected post-hoc based on a random event. Standard split-conformal requires exchangeability of the *calibration scores conditioned on the threshold being computed from all calibration points*. When the threshold is computed from a selected subset, the conditional coverage guarantee in Theorem 1 does not hold for the algorithm as implemented. If a counterexample exists where admissibility holds but coverage < `1 - alpha - 1/(|I|+1)`, the theorem is false and the paper must be retracted.

---

### CLAIM 2: 33% set-size reduction on SQuAD (13.35 vs 19.89 Token-CP)

#### What Would Refute This?

The 33% claim requires **both** (a) meaningful conditional coverage and (b) a genuine kernel-driven set-size advantage. Either one independently kills the claim.

**Refutation via coverage collapse:** If Qwen2.5-7B-Instruct achieves `p_A < 0.50` on SQuAD (meaning the true meaning appears in the sampled set fewer than half the time), then marginal coverage is ceiling-limited below 50%. The 33% set-size reduction is measured against a baseline that achieves ~10% marginal coverage — both methods produce degenerate conformal sets. A trivial baseline ("predict all meaning classes") achieves 100% marginal coverage (no coverage guarantee violation) and set size equals the number of distinct meaning classes observed. The 33% claim is meaningless without a coverage floor.

**Refutation via kernel overfitting:** The bandwidth sigma is grid-searched on a held-out 20% split to minimize set size subject to coverage >= 1-alpha. This is a single-objective optimization that selects the sigma producing the smallest conformal sets on the *training split*. There is no nested conformal validation. The selected sigma is the one that "got lucky" on the held-out data. The coverage guarantee does not apply to the selected sigma — it only applies to a *fixed* sigma. If sigma is selected post-hoc, Theorem 1's guarantee is void for the actually-deployed bandwidth.

**The reductio-ad-absurdum:** Consider a bandwidth grid of {0.001, 0.01, 0.1, 1.0, 10.0, 100.0}. The optimizer chooses sigma=0.001 because it produces the smallest set sizes (embedding-space distances are tiny, kernel scores are near 1.0 for everything, conformal sets are tiny). Coverage is <50% because the threshold is set so high that only the single closest class is included. The "33% smaller" claim holds. The method is not conformal prediction — it is nearest-neighbor classification with a conformal wrapper.

**Failure mode that would make the paper retractable:** The ablation results (13.35 SemCP vs 18.57 SemCP-Euclidean) suggest the learned kernel is the driver of improvement. But if these numbers are generated by the same bandwidth-optimization process (optimized on held-out, evaluated on test), the improvement is a statistical artifact of overfitting the held-out split. If independent evaluation on a held-out test set shows no set-size advantage (within CI), the paper must be retracted for scientific fraud.

---

### CLAIM 3: Semantic equivalence partitioning via bidirectional NLI preserves exchangeability (Section 4.1)

#### What Would Refute This?

The paper argues that `Pi` is a "deterministic fixed function" that does not depend on calibration labels, therefore preserving exchangeability. But the NLI model (DeBERTa-v2-xlarge-MNLI) is a neural network trained on MNLI. Its entailment judgments are not logically consistent — NLI models are known to have non-transitive behavior: A entails B, B entails C, but A does not entail C.

**Failure mode:** Union-Find closure with a non-transitive NLI model produces semantic equivalence classes that are not actually equivalence classes. Two strings that share a meaning end up in different classes, or two strings with different meanings get merged.

- If the partition *under-merges* (splits distinct meanings): The conformal set targets a specific surface form, but the true meaning is in a different partition. Coverage fails even when admissibility holds. The guarantee in Theorem 1 assumes the partition is a perfect semantic equivalence relation.
- If the partition *over-merges* (merges distinct meanings): The conformal set may include an answer with a different meaning than the true answer, but because both are in the same class, the nonconformity score treats them identically. This is a type error in the formal model — it violates the quotient space construction.

**The reductio-ad-absurdum:** Take a legal QA example where "The defendant is not liable" and "The defendant is liable" are conflated by the NLI model because both are legal conclusions that share surface legal terminology. The conformal set includes both mutually contradictory answers. The coverage guarantee is vacuous — it covers a semantic class that does not respect meaning distinctions that matter for downstream use. The paper's entire motivation (legal QA with >75% hallucination rates) is undermined if the semantic partition itself is unreliable.

**Failure mode that would make the paper retractable:** If independent evaluation shows that the NLI partition has >5% error rate on a ground-truth semantic equivalence test set, the exchangeability argument is broken (the partition is not a fixed deterministic function — it is a stochastic function of the NLI model's internal state) and the coverage guarantee does not hold. Any published results under this condition would require retraction.

---

## ADDITIONAL FAILURE MODES

### A. The Algorithmic Contradiction (W4 in Naive Reader review)

Algorithm 1 (line 180) computes the lifted calibration score as:
```
1 - max_{c' != c_i^*} kappa_sigma(bars_phi_{c_i^*}, bars_phi_{c'})
```
—a **contrastive between-cluster score**.

But Section 4.3 (Equation 2) defines the lifted score as:
```
min_{y' in [y]_s intersect {y_1,...,y_K}} s(x, y')
```
— a **within-cluster minimum score**.

These are fundamentally different formulations. One says "a class is nonconforming if any other class scores higher"; the other says "a class is nonconforming if its best member scores poorly." If SemCP uses the contrastive formulation (Algorithm 1) but the theoretical analysis uses the within-cluster formulation (Section 4.3), the paper is **internally inconsistent** and Theorem 1 does not apply to the implemented algorithm. This is not a fixable flaw — it is a fundamental contradiction that would require retraction if the paper were accepted based on Theorem 1 but the implemented algorithm is something different.

### B. The Coverage Contradiction (near-zero vs 33%)

The paper simultaneously claims:
1. "Coverage is near-zero for all methods due to GPT-2's limited QA capability" (Discussion, Fig 3 caption)
2. "33% smaller set sizes" than Token-CP (Abstract, Section 7)

If coverage is near-zero, conformal sets collapse to empty sets. The empty set has minimum set size — a 33% reduction over a near-zero baseline is not a meaningful improvement. The paper cannot simultaneously claim both. If this contradiction is not resolved before publication and post-publication analysis shows coverage is genuinely near-zero for Qwen2.5-7B-Instruct as well, the primary empirical contribution evaporates.

### C. Figure 3 Caption / Model Inconsistency as Fraud Indicator

Fig 3 caption explicitly attributes results to GPT-2. The experiments use Qwen2.5-7B-Instruct. This discrepancy was found by **every single reviewer**. In isolation, it could be a cut-and-paste error. Found alongside TODO_NUM results, it suggests the paper text was written for different experiments than what was actually run. If an investigation reveals that no Qwen2.5-7B-Instruct experiments were run at all — and the GPT-2 numbers are the only real results — the paper is fraudulent and must be retracted.

---

## ASSESSMENT: CAN THIS PAPER EVER BE PUBLISHED?

### The Hard Truth About TODO_NUM Results

Given that **all** empirical results are TODO_NUM placeholders, the honest answer is: **not in its current form**. But the question is whether *any version* of this paper could be published. The answer is **yes, conditionally**, but only if all of the following are satisfied:

**Minimum viable publication requirements:**
1. All Table 1 values filled with real numbers from at least 3 seeds, with bootstrap CIs
2. Figure 3 regenerated with Qwen2.5-7B-Instruct results; caption corrected
3. Algorithm 1 reconciled with Section 4.3 theory (same formulation)
4. GPT-2 discussion removed or clearly separated from Qwen results
5. Code released (not "upon publication")
6. p_A explicitly reported and > 0.85 for the primary results to be meaningful
7. NLI partition validated against a ground-truth semantic equivalence test set

**The strongest version of this paper:**
- Theorem 1 is correct and represents a genuine theoretical contribution
- The admissibility-coverage decomposition is a useful diagnostic
- The kernel-based scoring (RBF vs Euclidean) ablation is real and meaningful
- Conditional coverage ~0.89 achieved at alpha=0.10 with Qwen2.5-7B-Instruct
- Set-size reduction >20% over the strongest baseline at matched coverage
- NLI partition accuracy reported (e.g., 95% precision on a semantic equivalence test set)
- Code released with reproducible experiment scripts

**The weakest version that could be published:**
A theory-only paper with no empirical validation — just Theorem 1, the quotient-space formalization, and an exploratory ablation. This would be a strong short paper or workshop paper. But the paper's abstract makes specific quantitative claims (33% reduction) that require empirical support for NeurIPS-level publication.

**The retractable version:**
A paper that fills in TODO_NUM with fabricated numbers that happen to support the claimed 33% reduction, while coverage is actually near-zero and p_A is below 0.50. This is the failure mode the red team is flagging as the most dangerous: the TODO_NUM placeholders give the authors the option to fill in whatever numbers they want. If those numbers are cherry-picked to support the claims, the paper is fraudulent.

---

## SUMMARY OF RETRACTABILITY CONDITIONS

The paper should be **retracted** if any of the following come to light post-publication:

1. **Theorem 1 is false** — a counterexample exists where admissibility holds but coverage < `1 - alpha - 1/(|I|+1)` due to the admissibility-selection effect
2. **NLI partition error rate >5%** on a ground-truth semantic equivalence test, breaking the exchangeability argument
3. **Bandwidth sigma is optimized post-hoc on data also used for threshold calibration** — the coverage guarantee is void for the deployed sigma
4. **The 33% reduction does not replicate** on held-out test data within CI
5. **Qwen2.5-7B-Instruct p_A < 0.50** on TriviaQA/SQuAD — making the marginal coverage ceiling below nominal levels, so the method provides no useful guarantee in practice
6. **Algorithm 1 does not implement Theorem 1's algorithm** — the contrastive vs within-cluster score mismatch means the theoretical guarantee does not apply to what was actually implemented

---

*Red Team Agent — adversarial attack complete*
*Attacks filed: 3 primary claims × 4 attack vectors each = 12 distinct failure modes identified*
