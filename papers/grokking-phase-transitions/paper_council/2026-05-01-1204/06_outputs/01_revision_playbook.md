# Revision Playbook — CRISP (grokking-phase-transitions)

**Source:** Area Chair Meta-Review, 2026-05-01
**Current verdict:** Borderline-Reject (weighted soundness avg: 4.875)
**Target:** Borderline-Accept (requires all Priority 1 items completed)

---

## Priority 1 — Must-Fix for Acceptance

### 1.1 — Fix n_c Direction Reversal (Theorem 2)
- **Location:** Section 3 / Theorem 2 and Figure 4 data
- **Current text:** n_c = alpha * w * log(F) — predicts n_c increases with width
- **Problem:** Empirical data shows n_c monotonically decreases: 1546 (w=32) to 884 (w=128)
- **Proposed fix:** Derive corrected formula from Theorem 1 energy functional. Re-estimate alpha from data with the corrected functional form. If no first-principles derivation is possible, acknowledge the mismatch explicitly and reposition Theorem 2 as a theoretical prediction contradicted by data — do NOT quietly absorb the discrepancy with post-hoc parameters.
- **Effort:** 8–12 hours (theory derivation + re-fit)
- **Odds lift:** HIGH — this is the #1 rejection trigger across all 8 reviewers. Fixing it removes the primary barrier to acceptance.

---

### 1.2 — Resolve F_eff(w) Post-Hoc Problem
- **Location:** Section 3, introduced to reconcile n_c direction mismatch
- **Current text:** F_eff(w) = F*(w/w0)^(-gamma) with gamma > 1 (free parameters w0, gamma)
- **Problem:** 5 data points, 2 free parameters, zero predictive power. Cannot be independently measured. Makes the theory unfalsifiable.
- **Proposed fix (choose one):**
  - (a) **Derive from first principles** from the energy functional in Theorem 1 — derive w0 and gamma physically, not by fitting
  - (b) **Pre-register as secondary hypothesis** — acknowledge it is a data-driven speculation to be tested in future work, not a confirmed result
  - (c) **Remove F_eff(w) entirely** and report Theorem 2 as contradicted
- **Effort:** 4–8 hours (for pre-registration); 12–16 hours (for first-principles derivation)
- **Odds lift:** HIGH — 8/8 reviewers cite this as severity 5/5. Addressing it is necessary for any chance of acceptance.

---

### 1.3 — Report or Remove Schaeffer Falsification Test
- **Location:** Falsification infrastructure (advertised 3 tests, only 2 reported)
- **Current text:** Three falsification tests are described; Schaeffer smoothness results omitted
- **Problem:** Advertises infrastructure it does not fully deliver — creates suspicion the omitted test failed
- **Proposed fix:** Run the Schaeffer test and report results. If results are ambiguous, report them as ambiguous with explanation. If results contradict the theory, report the contradiction. Under no circumstances should a falsification test be silently omitted.
- **Effort:** 2–4 hours (analysis + write-up)
- **Odds lift:** MEDIUM-HIGH — 5/8 reviewers flagged this. Addressing it removes a lingering credibility gap.

---

## Priority 2 — Strong Recommendation

### 2.1 — Directly Validate Beta = 2/3 Corollary
- **Location:** Theory section corollary (most exportable claim)
- **Current text:** Asserted but never measured from test loss data
- **Proposed fix:** Fit L ~ n^(-beta) to Figure 5 data across all widths. Report fitted beta with 95% bootstrap CI. If CI overlaps 2/3, claim is validated. If not, reposition as a theoretical prediction pending future experimental confirmation.
- **Effort:** 3–5 hours (data fit + uncertainty quantification)
- **Odds lift:** MEDIUM — severity 3–4/5; directly validates the paper's most generalizable claim.

### 2.2 — Multi-Task Validation (at least 1 held-out task)
- **Location:** All experimental sections; currently single-task (mod-47)
- **Current text:** All 120 runs on (a+b) mod 47
- **Proposed fix:** Run identical 5-width, 8-fraction grid on at least one additional task (mod-53, permutation parity, or CIFAR-10 parity). Fit alpha per task; verify n_c functional form and F_eff power-law exponent are consistent across tasks.
- **Effort:** 8–16 hours (additional experiments + analysis)
- **Odds lift:** HIGH — 7/8 reviewers flag single-task validation as insufficient for a claimed general theory.

### 2.3 — Increase Seeds to 10+ per Condition
- **Location:** Experimental design / all figures reporting n_c
- **Current text:** 3 seeds per condition; no uncertainty bounds
- **Proposed fix:** Run minimum 10 seeds per condition (40 conditions = 400 runs). Report n_c with 95% bootstrap CIs. Quantify phase boundary sharpness with a continuous model.
- **Effort:** 16–24 hours (compute) + 2–4 hours (analysis/write-up)
- **Odds lift:** MEDIUM — 5/8 reviewers flag this; directly addresses the "preliminary observation, not result" criticism.

---

## Priority 3 — Nice-to-Have

### 3.1 — Strengthen Prior Work Contextualization
- **Location:** Related work / introduction
- **Current text:** Some prior work on grokking cited; scaling law connections underexplored
- **Proposed fix:** Add explicit comparison to Chizat & Bach (2020) on phase transitions in optimal transport, and to power-law scaling in deep learning generalization (Friedman et al., arXiv variants). Better position CRISP as connecting two previously separate literatures.
- **Effort:** 4–6 hours (lit review + writing)
- **Odds lift:** LOW-MEDIUM — would strengthen contextualization score from ~6 to ~7-8.

### 3.2 — Add Real-World Generalization Experiment
- **Location:** Experimental sections
- **Current text:** All experiments on synthetic modular arithmetic tasks
- **Proposed fix:** Test on one real-world domain (e.g., image classification with varying label noise) to demonstrate that phase transition mechanism is not artifact of modular arithmetic structure.
- **Effort:** 8–12 hours
- **Odds lift:** LOW — would broaden significance claims but not blocking for acceptance.

### 3.3 — Clarify Unified Framing vs. Validated Framework
- **Location:** Abstract, introduction, conclusion
- **Current text:** Claims to "unify grokking and neural scaling laws"
- **Proposed fix:** Use conditional language in abstract and conclusion: "We propose a framework that predicts a shared phase transition mechanism; validation on mod-47 and mod-53 tasks confirms the qualitative predictions." Reserve "unifies" for when multi-task validation is complete.
- **Effort:** 1–2 hours (prose revision)
- **Odds lift:** LOW — minor claim adjustment; more about honest framing than fixing a technical gap.

---

## Summary Table

| # | Priority | Issue | Effort (hrs) | Odds Lift |
|---|----------|-------|-------------|-----------|
| 1.1 | P1 | Theorem 2 n_c direction reversal | 8–12 | HIGH |
| 1.2 | P1 | F_eff(w) post-hoc rescue | 4–16 | HIGH |
| 1.3 | P1 | Omitted Schaeffer test results | 2–4 | MEDIUM-HIGH |
| 2.1 | P2 | Beta=2/3 corollary not measured | 3–5 | MEDIUM |
| 2.2 | P2 | Single-task validation only | 8–16 | HIGH |
| 2.3 | P2 | 3 seeds, no uncertainty quantification | 16–24 | MEDIUM |
| 3.1 | P3 | Prior work contextualization gaps | 4–6 | LOW-MEDIUM |
| 3.2 | P3 | No real-world domain validation | 8–12 | LOW |
| 3.3 | P3 | Overclaiming unification | 1–2 | LOW |

**Minimum viable revision for Borderline-Accept:** Items 1.1, 1.2, 2.1, 2.2 (plus 1.3 for credibility). Complete these before resubmission.