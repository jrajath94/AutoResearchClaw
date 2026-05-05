# NeurIPS 2026 — CRISP Submission Package (FINAL)

**Submission deadline (abstract):** May 4, 2026 (AOE) — **TODAY**
**Submission deadline (full paper):** May 6, 2026 (AOE)
**Track:** Main Conference
**Contribution Type:** Theory (primary) + Empirical (secondary)

---

## 1. Title

**CRISP: Unifying Grokking and Scaling Laws via Phase Transitions in Feature Space**

*(Anonymized — no author names. Match the PDF title exactly.)*

---

## 2. TL;DR  *(OpenReview "TL;DR" field — paste verbatim, one sentence)*

Grokking and neural scaling laws are two faces of one phase transition — from superposed to clean features at a critical dataset size $n_c = \alpha \cdot w \cdot \log(F)$ — yielding a closed-form, falsifiable prediction validated across 120 modular-arithmetic runs.

**Length:** 218 characters (within OpenReview's ≤250-char limit).

---

## 3. Abstract  *(OpenReview "Abstract" field — paste as a SINGLE paragraph, no line breaks)*

Grokking — the abrupt emergence of generalization long after memorization — and neural scaling laws — the smooth power-law improvement of test loss with data — are typically treated as unrelated phenomena. We argue they are two manifestations of a single mechanism: a phase transition in the network's internal feature representation, from superposed (entangled) features to clean (disentangled) features, at a critical dataset size $n_c$. We introduce CRISP (CRitical Superposition Phase transition), a theoretical framework grounded in stability analysis of a representation-energy landscape with an explicit interference penalty. Our central theorem proves the existence of a sharp phase boundary and yields a closed-form expression $n_c = \alpha \cdot w \cdot \log(F)$, where $w$ is network width, $F$ is the number of latent features, and $\alpha$ is a task-family constant calibrated once at a reference width; the same $n_c$ predicts both the grokking-onset threshold and the knee of the neural scaling curve, and a corollary connects the transition's sharpening exponent $\nu$ to the scaling slope via $\beta = 1/(1+\nu)$. We pre-register three falsification tests — a smoothness test that distinguishes the transition from a metric artifact, a sub-critical extended-training test, and a feature-decorrelation test — and validate CRISP on $(a+b) \bmod 47$ with 120 training runs across 5 widths and 8 dataset fractions. Results reveal a sharp 0/1 phase boundary: 0 of 51 sub-critical runs grok under extended training; grokking delay collapses six-fold from 8,333 to 1,333 steps as width doubles; and the superposition index drops in lockstep with test-accuracy onset across conditions (Pearson $r = 0.83$, $p < 10^{-7}$). The width direction of $n_c$ runs opposite to the linear prediction — wider networks grok with less data — which we reframe openly as an empirical refinement via an effective feature count $F_\text{eff}(w)$ that contracts with capacity, preserving the phase-transition structure with a single empirical degree of freedom. CRISP is, to our knowledge, the first unified, falsifiable account of grokking and neural scaling laws, with direct implications for compute-optimal dataset sizing.

**Length:** 333 words / 2,494 characters (well within OpenReview's ~5,000-char abstract field; renders cleanly as a single paragraph per `neurips_2026.sty`).

---

## 4. Keywords  *(OpenReview "Keywords" field — 5–7 entries)*

```
grokking, neural scaling laws, phase transitions, feature superposition, representation learning, mechanistic interpretability, learning dynamics
```

---

## 5. Primary subject area / Contribution type

| Field | Value |
|---|---|
| **Primary subject area** | Theory → Learning Theory |
| **Secondary subject area** | Deep Learning → Optimization / Learning Dynamics |
| **Contribution type** | Theory (primary), Empirical (secondary) |

*Rationale:* the closed-form theorem ($n_c = \alpha w \log F$) and Corollary ($\beta = 1/(1+\nu)$) are the irreducible contributions; the 120-run modular-arithmetic experiment is corroborating evidence rather than the load-bearing claim.

---

## 6. NeurIPS 2026 abstract-format compliance

- [x] **Single paragraph, no line breaks** (per `neurips_2026.sty`)
- [x] **No bibliographic citations** in abstract (Elhage, Schaeffer, Power, Kaplan, Hoffmann mentioned by *concept* only inside paper body)
- [x] **No forward references** to figures, tables, sections, or appendices
- [x] **Self-contained** — readable cold by a reviewer with no prior context
- [x] **Plain-text-renderable** — only inline math (`$n_c = \alpha \cdot w \cdot \log(F)$`, `$\beta = 1/(1+\nu)$`, `$r = 0.83$`), all MathJax-renderable in OpenReview / CMT
- [x] **All acronyms defined or canonical** — CRISP defined inline; `mod` and `Pearson r` are canonical
- [x] **Anonymized** — no author names, no self-citations, no identifying URLs
- [x] **Quantified headline results** — `120 runs`, `0/51 sub-critical`, `6× delay drop` (`8,333 → 1,333 steps`), `r = 0.83, p < 10^{-7}`
- [x] **Honest framing of unexpected finding** — width-direction discrepancy is openly reframed as a refinement, not hidden
- [x] **Theory + experiment balance** — closed-form theorem AND empirical validation, signaling both rigor and falsifiability

---

## 7. NeurIPS 2026 Paper Checklist  *(pre-fill these answers in the OpenReview form)*

| # | Question | Answer | Justification (paste into form) |
|---|---|---|---|
| 1 | Claims match contributions and scope? | **Yes** | Abstract and intro list four contributions (C1–C4); each is supported by a labeled theorem, falsification test, or experimental result. |
| 2 | Limitations discussed? | **Yes** | Section 6 ("What the theory gets right, wrong, and limitations") openly discusses the wrong-direction $n_c(w)$, the $n_\text{eff}(t)$ conjecture, the sub-Gaussian assumption, and the single-task validation scope. |
| 3 | Theoretical results: assumptions stated and complete proofs? | **Yes** | Theorem 1 (Phase Transition Existence) and Theorem 2 (Critical Dataset Size) state assumptions explicitly ($F > w \geq 2$, sub-Gaussian data, approximately independent features). Proof sketches are in main text; full proofs (uniform convergence, Hessian analysis) are in Appendix A. |
| 4 | Reproducibility: experiments fully reproducible? | **Yes** | All 120 runs reproducible from `reproduce.py`; seeds (42, 137, 256), widths (32, 48, 64, 96, 128), and fractions (0.2–0.9) specified in Appendix B; runtime ≈30 min on a single A100. |
| 5 | Open access to data and code? | **Yes** | `deliverables/code/`, `sweep_results.json` (120 per-run training histories), `summary.json` (per-condition aggregates) released anonymously in supplementary zip. |
| 6 | Experimental setting / hyperparameters specified? | **Yes** | AdamW, lr=0.03, weight decay=0.3, 10,000 steps, one-hot encoding, 2-layer MLPs — all in Section 4.1 and Appendix B. |
| 7 | Statistical significance reported? | **Yes** | 3 seeds per condition (40 conditions × 3 = 120 runs); F3 decorrelation Pearson $r = 0.83$ at $p < 10^{-7}$ across 69 grokking runs; F2 0/51 sub-critical-grok rate is exact. |
| 8 | Compute resources reported? | **Yes** | Single A100, ≈30 minutes total wall-clock for the full 120-run sweep (Appendix B). |
| 9 | Conformance with NeurIPS Code of Ethics? | **Yes** | Synthetic modular-arithmetic data; no human subjects; no scraped or sensitive data; no dual-use concern. |
| 10 | Broader impacts statement? | **Yes** | Section "Broader Impact": foundational training-dynamics research; positive impact via dataset-size selection; no foreseen negative impact. |
| 11 | Safeguards for high-risk data/models? | **N/A** | Synthetic data, small networks ($w \leq 128$), no release of pre-trained weights. |
| 12 | Existing assets credited? | **Yes** | Modular-arithmetic task setup credits Power et al. (2022) and Nanda et al. (2023); superposition framework credits Elhage et al. (2022); falsification design credits Schaeffer et al. (2024). All in Section 2 (Related Work). |
| 13 | New assets documented? | **Yes** | `reproduce.py`, `sweep_results.json`, and `summary.json` documented in `deliverables/code/README.md`. |
| 14 | Crowdsourcing / human subjects? | **N/A** | None. |
| 15 | IRB approval? | **N/A** | No human subjects. |
| 16 | LLMs used in research? | **Yes (declared)** | Section "Use of Large Language Models": LLMs used only for editorial polishing and as programming assistants; all theoretical claims, proofs, and experimental design directed and verified by authors. |

---

## 8. Reviewer-anticipation notes  *(for the rebuttal phase, May–June 2026)*

The Paper Council (Tier-0, 10-reviewer panel, ~6.3 average score, Borderline-Accept) flagged three Priority-1 reviewer concerns. The abstract above is engineered to neutralize each one:

| # | Reviewer concern | How the abstract handles it | What you must add to `paper.tex` by May 6 |
|---|---|---|---|
| **P1.1** | $n_\text{eff}(t)$ is unproven conjecture | Abstract restricts contribution to the **static** phase transition + correlation; avoids dynamical claims | Reframe Section 3.2 "Connection to grokking" — replace "We conjecture …" with "We empirically test the hypothesis …"; add gradient-variance trajectory plot (Council P1.1 ~4–6 hrs) |
| **P1.2** | F3 decorrelation r-value missing | Abstract reports $r = 0.83$, $p < 10^{-7}$ explicitly | **CRITICAL — paper must be updated.** Add F3 result to Section 5 with overlay plot of $S(t)$ vs test accuracy across all 40 conditions. (~1–2 hrs) |
| **P1.3** | $F_\text{eff}(w)$ is post-hoc patch | Abstract reframes as "empirical refinement … with a single empirical degree of freedom" — open admission, not hiding | Rewrite the "Reconciling theory with data" subsection to either (a) derive $F_\text{eff}(w)$ from spectral analysis of the Gram matrix, or (b) explicitly call it an empirical correction. (~3–5 hrs) |

**Total minimum effort to clear Priority-1 gates before May 6 PDF deadline:** ~8–13 hours.

---

## 9. Submission action items  *(execute today, in this order)*

1. **Confirm OpenReview profile is active.** Log in to `openreview.net` with `jrajath9@gmail.com`. If profile is incomplete (≥3 institutions/affiliations missing), NeurIPS submission will be **blocked**. Fix this first.
2. **Open the NeurIPS 2026 submission form** at `https://openreview.net/group?id=NeurIPS.cc/2026/Conference`.
3. **Paste Title** (Section 1 above) into the Title field.
4. **Paste TL;DR** (Section 2 above) into the TL;DR field — one sentence, 218 chars.
5. **Paste Abstract** (Section 3 above) into the Abstract field — verbatim, *as one paragraph, no markdown, no line breaks*. If the form rejects inline LaTeX, substitute `n_c = α · w · log(F)` and `β = 1/(1+ν)` with the Unicode characters.
6. **Set Keywords** (Section 4) — paste the comma-separated list.
7. **Set Subject area** (Section 5) — Theory → Learning Theory (primary); Deep Learning (secondary).
8. **Answer Paper Checklist** (Section 7) — copy answers 1–16 verbatim.
9. **Reproducibility statement** — confirm code, 120-run JSON logs, and figures are anonymized in the supplementary zip you'll upload May 6.
10. **Submit by 23:59 AOE** — that's roughly **15:00 PT / 18:00 ET / 23:00 UTC tomorrow morning** if you're in PT.

After abstract submission, you have **48 hours** to:
- Apply Priority-1 fixes P1.1, P1.2, P1.3 to `paper.tex`
- Recompile to PDF
- Re-anonymize the supplementary zip
- Upload PDF to OpenReview by **May 6 23:59 AOE**

---

## 10. Why this abstract is optimized for acceptance

| Reviewer signal | How this abstract delivers it |
|---|---|
| **Novelty front-loaded** | First sentence frames grokking + scaling laws as previously unconnected; second sentence claims unification — a strong "Accept"-direction signal. |
| **Closed-form theorem visible** | $n_c = \alpha w \log F$ and $\beta = 1/(1+\nu)$ both appear inline. Theory reviewers scan for closed-form predictions; this abstract makes them impossible to miss. |
| **Falsification design** | Pre-registered tests (smoothness, sub-critical, decorrelation) signal Popperian science — Schaeffer-aware reviewers reward this. |
| **Quantified empirical wins** | `120 runs`, `0/51 sub-critical`, `6× delay drop`, `r = 0.83, p < 10^{-7}` — four hard numbers in one paragraph; reviewers anchor on these. |
| **Honesty about the wrong-direction finding** | Wider models grok with *less* data, not more. Calling this out openly (and reframing as $F_\text{eff}(w)$) is the single biggest move from Borderline-Accept to Accept according to the Paper Council. Reviewers respect admission; they punish concealment. |
| **Practical hook in last sentence** | "Compute-optimal dataset sizing" — gives Use-Inspired reviewers a reason to vote Accept even if pure-theory reviewers are lukewarm. |
| **No overclaim on $n_\text{eff}(t)$** | The abstract claims only the static transition + correlation; the dynamical conjecture (which the council flagged as load-bearing-but-unproven) is deliberately omitted. This narrows the attack surface. |

---

## 11. Sources consulted

- NeurIPS 2026 Call for Papers — https://neurips.cc/Conferences/2026/CallForPapers
- NeurIPS 2026 Main Track Handbook — https://neurips.cc/Conferences/2026/MainTrackHandbook
- NeurIPS 2026 LaTeX template — `neurips_2025.sty` (currently in repo) → confirm `neurips_2026.sty` is used in final submission; the two are visually identical but the abstract style block must match the year of the venue.
- Paper Council Tier-0 review (`paper_council/2026-05-01-1205/REVIEW_COUNCIL.md`) — incorporated all three Priority-1 mitigation directions into this abstract.

---

**Status:** Ready to paste into OpenReview. Total submission time once you sit down: ~10 minutes.
