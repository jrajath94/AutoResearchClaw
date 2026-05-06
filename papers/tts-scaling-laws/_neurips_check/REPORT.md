# NeurIPS 2026 Submission Readiness Report — STAIR / STAIRCASE

**Date**: 2026-05-06
**Verdict**: **BLOCK**
**Counts**: BLOCKER=1, MAJOR=3, MINOR=5, PASS=8

## Executive Summary

The paper is scientifically substantive (Theorem 1 + 7-step Prékopa proof, three V3 experiments with strong shape-R² separation, an honest V1 retraction, and a methodological BIC-bias discovery), is properly anonymized, uses neurips_2026.sty, and embeds a fully-formatted NeurIPS Paper Checklist with all 16 answer markers. However, the main body runs to ~13.5 pages — references begin on page 14 — versus the NeurIPS 2026 hard limit of 9 main pages. This is a desk-reject-grade violation. Until the main body is compressed to <=9 pages, the paper cannot be submitted to the main track.

## Findings by Severity

### BLOCKER
- **B1. Main-body page limit violated (9 -> ~13.5).** Bibliography begins on page 14 of the PDF; main text Sections 1–10 (Intro through Conclusion) end mid-page 14. NeurIPS 2026 main track allows 9 main-text pages; references/checklist/appendices are unlimited only after the main body closes. Fix: move §4.3 allocator detail, Table 4 (synthetic baselines), Figure 3 (BIC vs shape on null), and parts of §6.3/§6.4 to the appendix; tighten the abstract.
  - Location: pdf pp.1–14; main.tex lines 54–506 (intro through bibliography start).

### MAJOR
- **M1. Abstract is one ~38-line paragraph filling page 1.** Contains three numbered findings, V1 retraction, methodological discovery. Forces body to start on page 2 and increases page pressure. Lines 45–51.
- **M2. Em-dash density: 39 occurrences of `---` in 682 lines.** Mostly technical, but humanizer-relevant. Sample lines: 47, 48, 49, 50, 339, 348, 350. Replace ~10–15 with periods/commas.
- **M3. Bib has 25 entries, only 14 are cited.** Prune uncited keys to reduce desk-screen risk.

### MINOR
- **m1. Page-1 visual density** — wall-of-text first impression (see M1).
- **m2. Figure 1 subplot axis labels small at print size** — legible but tight (page 9).
- **m3. Tables 1 & 2 placement on page 8 ahead of §6.1 narrative** — minor flow issue.
- **m4. Confirm `thm:population` label exists in §3** (compile succeeded, so likely fine).
- **m5. Pre-flight detector said `checklist_present: false`** — false negative. Checklist is at line 596 with 16 answer markers (12 \answerYes, 3 \answerNA).

### PASS
- **P1. Style file**: neurips_2026.sty loaded (line 3).
- **P2. Anonymization**: \author{Anonymous Author(s)} (line 40); no author/email/repo leakage in main.tex.
- **P3. NeurIPS Paper Checklist**: present, properly formatted, 16 answer markers (lines 596–678).
- **P4. No \cite in abstract** (verified — 0).
- **P5. Reproducibility**: §5 Experimental Setup detailed; checklist Q5 = \answerYes.
- **P6. Broader Impact**: explicit §9 with energy/dual-use/equity/methodological-externality.
- **P7. Limitations**: explicit §8 (line 464).
- **P8. Numerical-claim spot-check (5/5 verified)** in revised_v3_stats.json:
  - 85.7% shape R²>0.7 (Qwen GSM8K, frac_high_r2_variation=0.857)
  - 98.0% (Llama 4 Scout MATH-500/GSM8K)
  - 87.3% (Qwen MATH-500, frac_high_r2_variation=0.873)
  - 36.4% token savings (tokens_saved_vs_max_pct=36.44)
  - 0.037 ms p99 gzip overhead (gzip_overhead_meta/p99_ms=0.0373)
  - 18.6% IID-Bernoulli null shape rate (vs 17.2% on Llama 4 Scout) — defensible.

## Per-critic notes

### Paper-detector
20 PDF pages letter; main.tex 682 lines; 14 cites; 25 bib entries; figures in figures/ and figures_v3/. Style neurips_2026.sty, anonymized, checklist embedded.

### Guideline auditor
- Page limit: VIOLATED (main ~13.5pp vs 9). BLOCKER.
- Anonymization, checklist, reproducibility, broader impact, limitations, no-abstract-cites, style file: all PASS.

### Humanizer critic
39 `---` em-dashes — high but mostly technical context. No detected instances of crucial / cutting-edge / delve / leverage / navigate / underscores / paradigm / tapestry / landscape / studies show / many researchers / in conclusion / it is important to note. No rule-of-three or "not only X but Y" patterns. Verdict: mostly clean prose, em-dash sweep recommended.

### Fact validator
- 5/5 numerical claims verified against revised_v3_stats.json (85.7%, 98.0%, 87.3%, 36.4%, 0.037ms, 18.6% null).
- 5/5 cited keys present in references.bib: kaplan2020scaling, snell2024scaling, polyanskiy2024it, raposo2024mixture, schuster2022calm. Plus brown2024scaling, hoffmann2022chinchilla, feng2024cot, li2019kolmogorov, cover2006elements, graves2016act, leviathan2023speculative, deepseek2025r1, openai2024o1 confirmed.

### Presentation critic
- p1 (read): title + abstract only; abstract dense (38 lines bold-marked), no figures. Wall-of-text first impression.
- p8 (read): Tables 1 + 2 fit cleanly, headers readable. Caption-above-table style.
- p9 (read): Figure 1 (population scaling, 3 subplots, 95% CI bands) + Figure 2 (per-cell shape R² histograms with red null overlay). Publication-quality. Axis labels small but legible.
- p15 (read): References clean, alphabetized; Appendix A (Binomial likelihood BIC) immediately follows.
- No widow/orphan headings; no equation rendering issues.

### Reader critic
- Contribution clarity: three findings + Thm 1 by abstract line 4. Strong.
- Selling the work: information-dense, well-structured, honest V1 retraction buys credibility.
- Related work: credible TTS / IT-of-reasoning positioning vs early-exit, speculative decoding, MoD.
- Experiments: 3 V3 models (Qwen3.6-35B GSM8K, Llama 4 Scout GSM8K, Qwen MATH-500) + S=32 sensitivity. Negative controls (IID-Bernoulli null) unusually strong.
- Limitations: explicit §8, honest about V1 retraction and dataset-dependent log-concavity.
- Non-specialist accessibility: Theorem statement concise; intuition repeated in abs/intro/discussion.
- Overall: strong reviewer fit; only obstacle is the page limit.

## Remediation order
1. **CUT MAIN BODY TO 9 PAGES.** Move synthetic Table 4 + §4.3 allocator detail + Figure 3 to appendix; tighten abstract; collapse §6.3/§6.4 narrative.
2. **Tighten abstract** (M1) — split or trim Finding (3) latency detail.
3. **Em-dash sweep** (M2) — drop 10–15 of the 39 occurrences.
4. **Prune references.bib** (M3) to only cited keys.
5. **Bump figure axis-label font** (m2) for camera-ready safety.

After remediation #1, re-run audit; verdict moves to SHIP-WITH-POLISH.
