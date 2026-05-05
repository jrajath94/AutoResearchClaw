# Red-Team Attack Document: CRISP Paper
**Target:** CRISP: Unifying Grokking and Scaling Laws via Phase Transitions in Feature Space
**Date:** 2026-05-01
**Red-Team Posture:** Adversarial — find failure modes, identify retractability triggers

---

## TOP 3 CLAIMS TO ATTACK

### CLAIM 1: Grokking = Phase Transition in Feature Space (Theorem 1 + n_eff(t) Conjecture)

**The claim:** As effective dataset utilization n_eff(t) increases with training steps and crosses critical threshold n_c, the globally stable minimum shifts from superposition (S = Theta(1)) to clean (S = O(F^-2)), causing grokking. Theorem 1 proves such a phase transition exists in the energy landscape.

#### What would REFUTE this claim experimentally or theoretically?

**Experimental refutation:**
- Measure n_eff(t) during training (via gradient norms, effective rank of activations, or accumulated Fisher information). If n_eff(t) does NOT monotonically increase and cross n_c at the observed grokking onset step, the conjecture collapses.
- Run F3 decorrelation test: if Pearson r < 0.8 between superposition index S drop and grokking onset, the mechanism is not confirmed.
- Extended training (50,000+ steps) on 10+ sub-critical runs: if ANY sub-critical run groks after 10,000 steps, the "permanent block" interpretation fails. Current F2 result (0/51 at 10,000 steps) is only a horizon-bounded result.

**Theoretical refutation:**
- Prove that n_eff(t) is NOT monotonically increasing under standard optimization (AdamW/SGD) for the mod-47 task.
- Show that the energy landscape has only ONE minimum class (not two), eliminating the basis for a phase transition.

#### Reductio-ad-absurdum: push the methodology to its extreme

**Extreme 1:** Train for 1,000,000 steps on sub-critical data. If grokking occurs at step 500,000, the theory's "permanent block at n < n_c" is wrong. The 0/51 result at 10,000 steps is consistent with "sub-critical models grok slowly" not "sub-critical models never grok."

**Extreme 2:** n_eff(t) is never defined. Define n_eff(t) = training_steps (trivial rebranding). Then the "mechanism" is: as training proceeds, the phase transition triggers. But this just restates that grokking happens when it happens — it explains nothing.

**Extreme 3:** The theory requires sub-Gaussian feature assumptions. At width w=32 with F=47 features, if activations have heavy tails (which neural network activations often do), the concentration-of-measure arguments in Appendix A fail. The bound Delta_n/n_c = O(w^(-nu)) could be exponentially weak in width, making the transition effectively invisible at studied widths.

#### Retractability test: if this finding were disproven, what else in the paper collapses?

**If grokking is NOT a phase transition in feature space:**
- Theorem 1 becomes a curiosity (two minima exist) without dynamical interpretation
- The entire narrative of Section 3.2 ("Connection to grokking") is unsupported
- The F3 decorrelation test fails as a mechanism validation
- The "sharp 0/1 phase boundary" becomes a metric artifact (potentially) rather than a physical transition
- The closed-form n_c loses its theoretical motivation (it would be an empirical formula without the phase transition grounding)
- Corollary 1 (beta = 2/3) is disconnected from any physical mechanism

**Collapse severity: TOTAL.** The paper's entire contribution is the phase transition framing. Without it, the paper is 120 runs on mod-47 with an empirical formula for n_c.

---

### CLAIM 2: n_c decreases with width via F_eff(w) = F * (w/w_0)^(-gamma), gamma > 1

**The claim:** Critical dataset size n_c monotonically decreases with width (Table 3: 1,546 at w=32 down to 884 at w=128). The theory originally predicted n_c increases with width (n_c = alpha * w * log(F)). The resolution is an effective feature count that shrinks with width faster than width grows.

#### What would REFUTE this claim experimentally or theoretically?

**Experimental refutation:**
- Run the same experiment on mod-31 (different prime, same task family). If n_c INCREASES with width for mod-31, the F_eff(w) reconciliation is task-specific post-hoc fitting, not a general law.
- Run on mod-47 with a 1-layer MLP or a transformer. If n_c increases with width for these architectures, F_eff(w) is an artifact of the 2-layer MLP geometry.
- Validate F_eff(w) independently: measure the effective feature count in activations (via PCA effective rank) at each width. If effective feature count does NOT decrease with width as F_eff(w) predicts, the formula is curve-fitting.

**Theoretical refutation:**
- Derive F_eff(w) from first principles and show gamma must be > 1 from the CRISP energy landscape. If no derivation exists, the parameter is free and the theory is unfalsifiable for this direction of n_c(w).
- Show that for any width regime, naive CRISP (n_c proportional to w) holds — the apparent decrease is noise or a finite-width artifact.

#### Reductio-ad-absurdum: push the methodology to its extreme

**Extreme 1:** The theory predicted n_c proportional to w (increases). The data shows the opposite. The theory was patched by adding a free exponent gamma that is fitted to make the prediction match the data. This is the definition of post-hoc curve fitting. If gamma were fitted per-task, per-architecture, or per-regime, the theory makes no genuine predictions — it can accommodate any data.

**Extreme 2:** F_eff(w) implies feature efficiency improves with width. But for very wide networks (w >> 128), does F_eff(w) continue decreasing? At what width does naive CRISP (n_c proportional to w) dominate again? The theory does not specify a crossover width. This means the theory cannot make predictions for transformers (w >> 1000) where the direction of n_c(w) is unknown.

**Extreme 3:** alpha is calibrated at w=256 then used to predict n_c at w=32, 48, 64, 96, 128. If alpha must be calibrated at a single width to make predictions at other widths, the theory has no predictive power for unseen widths. True out-of-sample prediction would require alpha to be estimated from first principles (from sigma, lambda, gamma) without any fitting to observed n_c values.

**Extreme 4:** Table 3 shows n_c PLATEAUS from w=96 to w=64 (both at f_c=0.5, n_c=1,105). If the theory predicts monotonic decrease, a plateau is already a deviation from theory. Push to w=256: does n_c continue decreasing, plateau, or reverse and increase? The theory does not predict.

#### Retractability test: if this finding were disproven, what else in the paper collapses?

**If n_c does NOT decrease with width (or increases with width on another task):**
- The F_eff(w) reconciliation is falsified
- The direction reversal was a task-specific observation, not a general law
- The paper's most surprising empirical finding (counter to naive prediction) becomes an unexplained anomaly
- Theorem 2's "closed-form n_c" loses its primary empirical validation
- The practical implication ("train at n ~ 1.2-1.5 n_c") still holds if n_c is empirically measurable, but the theoretical framework for WHY n_c has the form it does is undermined

**Collapse severity: PARTIAL.** The experimental results (Tables 2, 4, the phase diagram) are still valid observations about grokking. But the theoretical contribution (explaining WHY grokking occurs via phase transitions in feature space) is weakened without the n_c direction reversal as a confirmed prediction of the theory.

---

### CLAIM 3: beta = 2/3 corollary connecting CRISP to neural scaling laws

**The claim:** In the large-width limit, the sharpening exponent nu approaches 1/2, yielding beta = 1/(1+nu) approaches 2/3. This connects the phase transition sharpness to neural scaling law exponents, unifying grokking and scaling laws.

#### What would REFUTE this claim experimentally or theoretically?

**Experimental refutation:**
- Fit beta from the scaling curve in Figure 5. If the fitted beta is NOT 2/3 (or close to it as width increases from 32 to 128), the corollary fails.
- The paper never reports a power-law fit of the scaling curve. Without measuring beta, the claim that beta approaches 2/3 is unsubstantiated.
- Compare to established scaling law literature: Kaplan et al. 2020 report beta ~ 0.076 for language models. If CRISP's beta = 2/3 is correct, it must explain why LLM scaling exponents differ by an order of magnitude. The paper never addresses this discrepancy.

**Theoretical refutation:**
- Show that nu does NOT approach 1/2 with width in the CRISP framework — perhaps nu approaches a different value, yielding a different beta.
- Prove that beta = 2/3 is specific to the mod-47 / 2-layer MLP regime and does not generalize.

#### Reductio-ad-absurdum: push the methodology to its extreme

**Extreme 1:** beta = 2/3 appears in the paper as a corollary but is never measured. The paper predicts an exponent that connects to a major literature (neural scaling laws) without ever testing it. This is the most "exportable" claim in the paper, and it is the least validated. If a reviewer asked "what is the measured beta from your data?" the authors cannot answer.

**Extreme 2:** The unification claim requires explaining why LLM scaling exponents (~0.08) are so different from CRISP's predicted 2/3. If the answer is "regime separation" (small memorization-dominant models vs. large generalization-dominant models), the paper must specify the crossover point. Without this, "unification" is false — the paper shows a different mechanism for a different regime, not a unifying framework.

**Extreme 3:** The corollary beta = 1/(1+nu) with nu approaching 1/2 is derived from Theorem 2's transition width scaling. But Theorem 2's derivation contains approximations (the "approximately equals" step in solving Delta_E(n_c) = 0) with unquantified relative error. For w=32 and F=47, the corrections could be O(1), making the entire exponent derivation unreliable at the studied widths.

#### Retractability test: if this finding were disproven, what else in the paper collapses?

**If beta is NOT 2/3, or if beta cannot be meaningfully fitted from the data:**
- Corollary 1 is retracted
- The "unification with neural scaling laws" claim is weakened or false
- The paper's significance for the scaling law literature is eliminated
- The bridge between phase transition sharpness (nu) and scaling exponents is not实证 validated
- However: the core grokking results (phase diagram, F2, Tables 2-4) remain valid. The paper still contributes to grokking understanding even if the scaling law connection is dropped.

**Collapse severity: PARTIAL.** The significance score drops from 8/10 to 6/10. The paper is still a contribution to grokking but not a cross-regime unifying framework.

---

## FAILURE MODES TO IDENTIFY

### Failure Mode 1: If F_eff(w) is NOT decreasing with width in a different task, does the whole theory collapse?

**Failure mode analysis:**

F_eff(w) is the reconciliation for the direction reversal. If mod-31 produces n_c INCREASING with width (opposite of mod-47), then:
- F_eff(w) cannot be a universal property of width scaling
- The theory either needs a task-specific parameter that absorbs n_c(w) direction, or
- The observed decrease in n_c(w) for mod-47 is an artifact of that specific task

**Specific test:** Run 20-seed sweeps at w=32 and w=128 on mod-31. If n_c(w=128) > n_c(w=32), F_eff(w) is falsified as a universal claim.

**What survives:** Theorem 1 (phase transition existence) is still valid. The static phase transition result does not depend on F_eff(w). What fails is the quantitative prediction of n_c direction and the reconciliation mechanism.

---

### Failure Mode 2: If n_eff(t) is simply "training steps" rebranded, is the mechanism just a restatement?

**Failure mode analysis:**

n_eff(t) is never defined. If it is simply t (training steps), then:
- "n_eff(t) increases with training" = "training proceeds with time"
- "n_eff(t) crosses n_c" = "the model has been trained enough"
- "This triggers a phase transition" = "at some point the model generalizes"

This is a restatement of "grokking happens after enough training" with physics vocabulary. The mechanism is vacuous.

**Specific test:** Define n_eff(t) as accumulated gradient norm or Fisher information. Compute it from the JSON logs. Plot n_eff(t) for grokking vs non-grokking runs. If the crossing point of n_eff(t) with n_c does NOT align with the observed grokking onset step, the conjecture is empty.

**What survives:** If n_eff(t) cannot be given operational meaning, Theorem 1 still proves a static phase transition at n_c. What fails is the dynamical interpretation — grokking is not derived from the theory, only consistent with it.

---

### Failure Mode 3: If F3 decorrelation test shows no correlation, what happens to the superposition mechanism claim?

**Failure mode analysis:**

F3 requires r > 0.8 between the superposition index S drop and grokking onset. This is the ONLY test that directly validates the proposed mechanism (superposition -> clean phase transition causes grokking). F1 and F2 rule out alternative explanations; F3 confirms the theory's specific mechanism.

If F3 fails (r < 0.8 or not computed):
- The paper cannot claim the phase transition in feature space is causally linked to behavioral grokking
- The mechanism could be: grokking occurs but NOT via the superposition-to-clean transition
- Alternative: grokking is caused by something else (implicit regularization, circuit competition, etc.) that happens to coincide with the n_c threshold

**Specific test:** Compute Pearson r for all 40 conditions (width x fraction). Report the distribution. If ANY condition has r < 0.8, F3 fails. If the paper never computed r, the falsification test is incomplete.

**What survives:** The sharp phase boundary (Table 2) and the F2 result (0/51 sub-critical block) are still valid. Grokking has a sharp threshold at n_c. What fails is the specific mechanistic story connecting feature space geometry to behavior.

---

### Failure Mode 4: If a different modular task (mod-31 instead of mod-47) produces n_c INCREASING with width, is the result task-specific?

**Failure mode analysis:**

The paper studies ONE task: (a+b) mod 47. All 120 runs are on this task. The theory makes general claims about grokking and scaling laws. If mod-31 shows n_c increasing with width:
- The F_eff(w) direction is specific to mod-47 (or to modular arithmetic with prime 47)
- The "unification" framing collapses — the theory only describes one task
- The scope of the paper must be recharacterized as "mod-47 grokking in 2-layer MLPs"

**Specific test:** Run the full sweep on mod-31 at w=32 and w=128. Compare n_c direction. If opposite, the generalizability claim is falsified.

**What survives:** Theorem 1 may still hold (phase transition exists) but its empirical manifestation (n_c direction) is task-dependent. The practical implication (train at n ~ 1.2-1.5 n_c) still holds if n_c is measured empirically.

---

## OVERARCHING ATTACKS

### Overarching Attack 1: Is the "phase transition" framing just a metaphor, or is there genuine mathematical formalism?

**The attack:**

Theorem 1 proves that global minima of E(Phi; n) fall into two classes (superposed vs. clean) and that there exists some n_c where the energy ordering flips. This is a statement about the existence of two minima and a crossing point.

But is this a PHASE TRANSITION in the statistical physics sense?

A true phase transition requires:
1. A order parameter (S(Phi) — superposition index — is this the order parameter?)
2. A thermodynamic limit (w -> infinity — does the paper have a genuine thermodynamic limit?)
3. Non-analyticity in the limit (does Delta_n/n_c -> 0 require w -> infinity?)

The paper shows Delta_n/n_c = O(w^(-nu)). As w -> infinity, this goes to 0, which is the sharpness condition. But at w=32, 48, 64, 96, 128 (the studied widths), the transition is broadened by O(w^(-nu)). The "sharp 0/1 phase boundary" at w=128 (0% at f=0.3, 100% at f=0.4) is sharp in practice but not in theory — the bound only guarantees it sharpens with width, not that it is sharp at any finite width.

**The core question:** Does Theorem 1 actually PROVE a phase transition, or does it just show two local minima exist and one becomes preferred at large n?

The intermediate value theorem argument establishes a sign change in Delta_E(n) = E_clean - E_superposed. But this does not require a sharp transition — it could be a smooth crossover. The sharpness (Delta_n/n_c -> 0) only emerges in the limit w -> infinity.

**Retractability trigger:** If the paper's "phase transition" is actually a smooth crossover at all finite widths, the framing is metaphorical, not formal. The paper would be making a stronger claim (sharp phase transition) than it has proven (two minima with width-dependent sharpness).

---

### Overarching Attack 2: Does Theorem 1 actually PROVE a phase transition, or does it just show two local minima exist?

**The attack:**

Theorem 1 states: For n < n_c, global minimum is superposed. For n > n_c, global minimum is clean.

What it PROVES: At n < n_c and n > n_c, there are two distinct classes of minima (by gradient conditions). By continuity of Delta_E(n) = E_clean - E_superposed, there exists some n_c where Delta_E(n_c) = 0.

What it does NOT PROVE: That n_c is a sharp threshold (as opposed to a smooth crossover). That the transition occurs at the predicted n_c value. That the transition width Delta_n goes to zero as w -> infinity (only that it scales as O(w^(-nu))). That training dynamics actually traverse from one minimum to the other.

The proof establishes the STRUCTURE of the energy landscape but not the DYNAMICS of the phase transition, and not the QUANTITATIVE location of n_c except via Theorem 2's derived formula.

**The critical gap:** The proof uses gradient condition characterization and intermediate value theorem. This is correct for establishing existence of a crossing. But the Schaeffer et al. 2024 smoothness test (F1) is specifically designed to rule out whether apparent transitions in grokking are metric artifacts. The paper describes F1 but never reports whether log-loss also shows a transition. If log-loss shows no transition (or a gradual one), the "sharp phase transition" interpretation is undermined regardless of what the energy landscape says.

**Retractability trigger:** If F1 (log-loss test) shows a gradual transition rather than a sharp one, the energy landscape analysis does not map to observable behavior. The theorem is mathematically correct but empirically irrelevant.

---

### Overarching Attack 3: Does the theory predict or postdict n_c(w) direction?

**The attack:**

Theorem 2 predicts n_c proportional to w (increases with width). This is the theory's prospective prediction. The data shows the opposite. F_eff(w) was introduced to reconcile.

If a theory's central prediction goes the wrong direction, and the resolution is a free parameter (gamma) without derivation, the theory is NOT predictive. It is curve-fitting with physics vocabulary.

The specific sequence:
1. Theory: n_c = alpha * w * log(F) — predicts n_c increases with w
2. Data: n_c decreases with w (Table 3)
3. Reconciliation: F_eff(w) = F * (w/w_0)^(-gamma), gamma > 1, introduced without derivation
4. New prediction: n_c = alpha * w * log(F_eff(w)) — now predicts n_c decreases with w

This is post-hoc accommodation. The theory was modified to fit the data, not the data confirming a prediction.

**The adversarial question:** If gamma were not a free parameter, could the original theory have predicted the direction reversal? The answer is no — gamma was introduced specifically to flip the prediction.

**What this means for retractability:** If a reviewer asks "what would falsify CRISP?" the honest answer must include: "if n_c increases with width in a different task or architecture." But the paper currently has no mechanism to explain WHY n_c would increase with width in any setting — its only explanation is the post-hoc F_eff(w) that was introduced specifically to handle the opposite direction.

---

## SUMMARY: TOP RETRACTABILITY TRIGGERS

| Trigger | Condition | What Collapses |
|---------|-----------|----------------|
| T1 | F3 decorrelation test fails (r < 0.8) | Superposition-to-clean mechanism claim |
| T2 | n_eff(t) defined as training steps | Dynamical mechanism is vacuous restatement |
| T3 | mod-31 shows n_c increasing with width | F_eff(w) is task-specific, not universal |
| T4 | F1 log-loss test shows gradual transition | "Sharp phase transition" is metric artifact |
| T5 | Beta fitted from Fig 5 is NOT ~2/3 | Scaling law unification claim |
| T6 | Sub-critical run groks after 10,000+ steps | "Permanent block at n < n_c" is wrong |
| T7 | F_eff(w) cannot be derived from first principles | Theory is post-hoc accommodation, not prediction |

---

## CONSENSUS VULNERABILITIES (from 6-reviewer cross-exam)

All 6 reviewers agree on the following weaknesses, ranked by severity:

1. **n_eff(t) is undefined/conjecture** (6/6 reviewers) — Severity avg 3.8/5
2. **F_eff(w) is post-hoc without derivation** (6/6) — Severity avg 3.7/5
3. **F3 decorrelation test result not reported** (4/6) — Severity avg 3.5/5
4. **Beta = 2/3 corollary not validated** (5/6) — Severity avg 3.2/5
5. **Single-task validation** (4/6) — Severity avg 3.2/5

These are the highest-confidence attack surfaces.

---

## RED-TEAM VERDICT

**This paper is RETRACTABLE post-publication if:**

1. Extended training on sub-critical runs produces ANY grokking after 10,000 steps
2. F3 decorrelation correlation is measured and r < 0.5
3. A second task (mod-31, parity, CIFAR-10) shows n_c INCREASING with width
4. Beta fitted from scaling data is not approximately 2/3 and the paper has not acknowledged regime limitations
5. F_eff(w) derivation remains future work — it is never provided

**The paper's strongest defense** is the F2 result (0/51 sub-critical grokked) combined with the sharp phase boundary in Table 2. These are clean empirical results that would survive most attacks. The theoretical framework is where the paper is most vulnerable.

**Bottom line for retractability:** The phase transition framing is compelling but THEOREM 1 does not prove grokking is caused by the phase transition — it only proves the phase transition exists in the energy landscape. The link via n_eff(t) is an admitted conjecture. Without n_eff(t) being derived or measured, the paper's central mechanism claim is unproven. This is not a retraction-level flaw in the current form (the paper is transparent about n_eff(t) as conjecture), but it means the paper's strongest contribution is the empirical results, not the theory.
