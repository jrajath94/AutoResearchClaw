# CRISP Revision Playbook

**Paper:** CRISP: Unifying Grokking and Scaling Laws via Phase Transitions in Feature Space
**Date:** 2026-05-01
**Reviewer Consensus:** 6 reviewers, 5 top issues, Accept conditional on 3 criteria

---

## Priority 1 — Must-Fix (Accept Gate)

### P1.1 — Define or empirically measure `n_eff(t)`
- **Location:** Equation 3 / Section 3 (Mechanism) / wherever `n_eff(t)` is first introduced and used in derivations
- **Current text:** `[citation needed]` — `n_eff(t)` introduced as a central mechanism variable but never defined or measured
- **Proposed fix:**
  - Option A (theoretical): Derive `n_eff(t)` from feature-space dynamics — e.g., `n_eff(t) = N * (1 - ||w(t) - w*|| / ||w(0) - w*||)` or equivalent explicit form tied to training dynamics
  - Option B (empirical): Report `n_eff(t)` computed from feature-space effective dimensionality across training checkpoints (e.g., covariance eigenvalue drop-off). Add Figure/Table showing `n_eff(t)` over training steps for all model sizes.
  - If Option A is chosen, show that it recovers observed phase transition boundaries without parameter fitting.
  - Remove or qualify any claim that this mechanism is "derived" until a derivation exists. Frame as "motivated by" if using Option B.
- **Effort:** 4–6 hours (analysis + new experiments + figure)
- **Odds-lift:** Critical — 5/5 reviewers flagged this. Fixing or acknowledging the conjecture status is the difference between R&R and reject.

---

### P1.2 — Report F3 correlation value or explicitly acknowledge mechanism unconfirmed
- **Location:** Section 4 (Mechanism validation), specifically where criterion `r > 0.8` is stated and F3 is discussed
- **Current text:** Criterion set: "r > 0.8 required to confirm decorrelation mechanism." No value reported.
- **Proposed fix:**
  - Compute and report the empirical correlation coefficient for F3 (actual r-value, not just threshold check). If r < 0.8, state explicitly: "The F3 decorrelation mechanism remains unconfirmed in our experiments (r = X < 0.8). This is a limitation."
  - Do not elide this. Reviewers noticed the missing value — it signals that the test may have failed.
  - If re-running experiments yields r > 0.8, report cleanly. If not, frame as future work or empirical observation, not confirmed mechanism.
- **Effort:** 1–2 hours (computation + text update)
- **Odds-lift:** High — directly addresses a 4/5 severity issue that reviewers explicitly called out as a gap.

---

### P1.3 — Derive `F_eff(w)` from first principles or reposition as empirical correction
- **Location:** Equation 2 / Section 2.2 (Scaling law formulation) / any claim that F_eff(w) is derived from theory
- **Current text:** `F_eff(w)` used to predict scaling behavior in the wrong direction (model disagrees with prediction), then patched post-hoc.
- **Proposed fix:**
  - Option A (derivation): Show explicitly how `F_eff(w)` follows from the phase transition framework — what physical assumption yields this functional form? Fill in the gap in the derivation chain.
  - Option B (reposition): Retitle/reframe `F_eff(w)` as an empirical correction term rather than a first-principles prediction. E.g., "We observe a consistent offset that we model as F_eff(w) = ..." Change the framing from "theory predicts X" to "theory + empirical calibration."
  - Do not claim first-principles derivation if the derivation does not exist.
- **Effort:** 3–5 hours (derivation work or rewriting + reviewer response)
- **Odds-lift:** High — 4/5 severity and directly undermines the paper's core theoretical contribution.

---

## Priority 2 — Strong-Recommend (Substantially Improves Competitiveness)

### P2.1 — Test or qualify the `beta = 2/3` prediction
- **Location:** Section 3 (Phase transition scaling), Equation X or where beta exponent is introduced and compared to Kaplan et al.
- **Current text:** `beta = 2/3` predicted; Kaplan et al. find ~0.076. No reconciliation provided.
- **Proposed fix:**
  - Run ablation or theoretical analysis showing conditions under which beta = 2/3 emerges vs. Kaplan's regime.
  - If the two regimes are incompatible, acknowledge: "Our beta prediction applies to feature-space phase transitions and does not conflict with Kaplan's parameter-count scaling, as these describe different regimes."
  - Alternatively, drop the beta claim and replace with a tested prediction.
- **Effort:** 2–4 hours (analysis + potential additional experiments)
- **Odds-lift:** Medium-High — 3/5 severity but leaves the paper open to "theory contradicts established result without justification."

---

### P2.2 — Multi-task validation (beyond single-task)
- **Location:** Section 5 (Experiments) / Conclusion — current validation on single task is insufficient for a general theory claim
- **Current text:** `[citation needed]` — results reported on a single task/architecture.
- **Proposed fix:**
  - Run at least 2–3 additional tasks (e.g., different function approximation, different model families) to demonstrate generalizability.
  - If budget is limited, use existing published datasets and report both positive and negative results.
  - Explicitly scope the claim: "We validate on X tasks; extension to Y is left to future work."
- **Effort:** 4–8 hours (new experiments + analysis)
- **Odds-lift:** Medium — 3/5 severity. A general theory without multi-task evidence will be challenged in the discussion.

---

## Priority 3 — Nice-to-Have (Polish and Reviewer Goodwill)

### P3.1 — Tighten abstract/executive summary to set correct expectations
- **Location:** Abstract / Intro paragraph — ensure language matches what is actually derived vs. empirically observed
- **Current text:** Claims likely overstate "theory" vs. "observed"
- **Proposed fix:** Replace strong theory claims with calibrated language: "We propose a framework," "We observe phase transitions," "We derive" only where derivation exists.
- **Effort:** 1 hour
- **Odds-lift:** Low-Medium — preempts reviewer fatigue and signals intellectual honesty.

---

### P3.2 — Add reviewer response memo structure
- **Location:** Author response / response letter
- **Current text:** N/A
- **Proposed fix:** For each Priority 1 item, draft a 2–3 sentence explanation of what changed and why. Reviewers respond better when changes are visible and explicitly tied to their feedback.
- **Effort:** 1–2 hours
- **Odds-lift:** Low — goodwill, not a substantive fix.

---

## Summary Matrix

| # | Item | Severity | Effort (hrs) | Accept Gate? |
|---|------|----------|--------------|--------------|
| P1.1 | Define or measure `n_eff(t)` | 5/5 | 4–6 | Yes |
| P1.2 | Report F3 correlation value | 4/5 | 1–2 | Yes |
| P1.3 | Derive or reposition `F_eff(w)` | 4/5 | 3–5 | Yes |
| P2.1 | Qualify/test beta = 2/3 | 3/5 | 2–4 | No |
| P2.2 | Multi-task validation | 3/5 | 4–8 | No |
| P3.1 | Calibrate abstract language | 2/5 | 1 | No |
| P3.2 | Reviewer response structure | 1/5 | 1–2 | No |

**Total minimum effort for Accept:** ~8–13 hours
**Total full effort:** ~15–27 hours

**Recommended order:** P1.1 → P1.2 → P1.3 → P2.1 → P2.2 → P3.1 → P3.2