# Paper Revision Integration Plan

This document specifies **exactly which lines** of `paper.tex` will change, in what order, and with what content. When experimental data arrives, the integration is mechanical: read this plan, run the Edit tool with the specified replacements, recompile.

---

## A. Files involved

- `deliverables/paper.tex` — the source of truth for the submission
- `deliverables/PAPER_REPLACEMENTS.tex` — text replacements for existing paragraphs
- `deliverables/PAPER_ADDITIONS.tex` — new sections to insert
- `deliverables/PAPER_S_DEFINITION_FIX.tex` — Definition 1 update for the S metric
- `deliverables/PAPER_REFERENCES_ADDITIONS.bib` — three new \bibitem entries
- `deliverables/figures_v2/{mod47,mod31,mod59}/*.png` — new figures
- `deliverables/figures_v2/*/analysis.json` — measured numbers

---

## B. Edit operations (in dependency order)

### B.1 — Abstract replacement (lines 49-60)

**Action:** Replace the entire `\begin{abstract}...\end{abstract}` block with the version in `PAPER_REPLACEMENTS.tex`.

**TBD substitutions** in the new abstract:
- `\F3bestr` → fill with the largest |r| among S candidates from analysis.json
- `\Gammafit` → fill with measured γ from spectral fit

### B.2 — Contributions block replacement (lines 81-89)

**Action:** Replace `\paragraph{Contributions.}` block with the version in `PAPER_REPLACEMENTS.tex`.

**TBD:** placeholders for `r` and `γ` already use `\F3bestr` / `\Gammafit` macros.

### B.3 — Definition 1 update (lines 134-143)

**Action:** Replace the existing `\begin{definition}{Representation Regimes}` block with the updated definition from `PAPER_S_DEFINITION_FIX.tex`. The definition now uses **per-class hidden activations** as the canonical features.

### B.4 — "Connection to grokking" paragraph (lines 173-179)

**Action:** Replace the conjectural framing with the calibrated version from `PAPER_REPLACEMENTS.tex` (refers to §3.3 for the Fisher-based definition).

### B.5 — Insert §3.3 (after §3.2 proof, around line 187)

**Action:** Insert §3.3 "Effective Sample Size n_eff(t) from Fisher Information" from `PAPER_ADDITIONS.tex` immediately after the proof of Theorem 1.

### B.6 — Insert §3.4 (after §3.3, before existing §3.3 "Critical Dataset Size")

**Action:** Insert §3.4 "Spectral Derivation of F_eff(w)" from `PAPER_ADDITIONS.tex`. Note: this means the existing "§3.3 Critical Dataset Size" should be renumbered to §3.5 (or kept as §3.3 with the new subsections inserted appropriately — TBD on numbering).

### B.7 — Update the existing "Reconciling theory with data" paragraph (lines 393-405)

**Action:** Replace with the calibrated version from `PAPER_REPLACEMENTS.tex` that references §3.4 spectral derivation.

### B.8 — Insert §5.6, §5.7, §5.8, §5.9 (after §5.5 "Scaling with Width", around line 465)

**Action:** Insert four new subsections from `PAPER_ADDITIONS.tex`:
- §5.6 — F3 decorrelation result
- §5.7 — Multi-task validation
- §5.8 — Transformer validation
- §5.9 — Finite-size scaling collapse

### B.9 — Insert §6.1, §6.2 (after §6 discussion content, before Conclusion)

**Action:** Insert from `PAPER_ADDITIONS.tex`:
- §6.1 — Regime separation for β
- §6.2 — Compute-optimal width recipe

### B.10 — Update prediction status table at end of §3

**Action:** Insert the prediction status table from `PAPER_ADDITIONS.tex` at end of theory section (replaces or augments existing Table 1).

### B.11 — Add bibliography entries (before \end{thebibliography} around line 609)

**Action:** Insert the three new \bibitem entries from `PAPER_REFERENCES_ADDITIONS.bib`:
- jacot2018ntk
- roy2007effective
- cardy1996scaling

### B.12 — Run `render_paper_numbers.py` and \input the macros file

**Action:** Generate `paper_numbers.tex` from `analysis.json` files; add `\input{paper_numbers.tex}` after the package imports near top of paper.tex.

---

## C. Verification checklist (after compile)

- [ ] LaTeX compiles cleanly (no undefined references)
- [ ] All `\F3*` and `\NEff*` macros are defined
- [ ] All numbers in tables match analysis.json values (manual cross-check)
- [ ] Figure references resolve (Fig 7, 8, 9, supp)
- [ ] Bibliography includes Jacot, Roy & Vetterli, Cardy
- [ ] Page count under NeurIPS 9-page limit (check with `pdfinfo paper.pdf | grep Pages`)
- [ ] No `\TBD` or `[TBD]` placeholders remaining

---

## D. Acceptance gate (re-run paper-council mental model)

After the integration, ask: would the council still mark each item as "must-fix"?

- **P1.1 (n_eff(t)):** Now defined via Fisher trace, measured with `r = [filled]`. ✅
- **P1.2 (F3 r):** Now reported with `r = [filled]` for the best metric. ✅
- **P1.3 (F_eff(w)):** Now derived from spectral entropy, `γ` measured independently. ✅
- **P2.1 (β):** Fitted with bootstrap CI, regime separation argument added. ✅
- **P2.2 (multi-task):** mod-31, mod-59, mul-mod-31, transformer added. ✅
- **P3.1 (calibration):** Abstract rewritten, status table added. ✅
- **P3.2 (response memo):** RESPONSE_MEMO.md drafted. ✅

If all are ✅, the paper has cleared the council's accept gate.

---

## E. Risk register

| Risk | Mitigation |
|---|---|
| F3 `r < 0.8` | Honestly report `r`, frame mechanism as "candidate"; check across all 4 S metrics |
| Spectral `γ` doesn't match curve-fit `γ` | Report both, treat as approximate agreement; this is still better than free parameter |
| β fit far from 2/3 | Frame regime-separation more strongly; cite Chinchilla |
| Multi-task direction inconsistent | Report honestly; scope claim to {mod-p add, mod-p mul} only |
| Sweep crashes mid-run | Existing v1 results provide fallback for phase diagram numbers |
| Time runs out | Submit revision with whatever data is available + honest status table |
