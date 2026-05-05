"""Apply the planned edits to paper.tex programmatically.

This script reads the existing paper.tex, applies the substitutions and
insertions specified in PAPER_INTEGRATION_PLAN.md, and writes a new
paper_v2.tex.  It does NOT compile -- compilation is a separate step.

Usage:
    python apply_paper_edits.py \\
        --in paper.tex \\
        --out paper_v2.tex \\
        --replacements PAPER_REPLACEMENTS.tex \\
        --additions PAPER_ADDITIONS.tex \\
        --paper-numbers paper_numbers.tex
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path


def read(p: Path) -> str:
    return p.read_text()


def find_section(tex: str, label_or_title: str) -> tuple[int, int] | None:
    """Find the line range of a section by label or title.  Returns (start, end)
    line indices or None.  Section ends at the next \\section/\\subsection/\\paragraph
    or end-of-file.
    """
    lines = tex.split("\n")
    start = None
    for i, line in enumerate(lines):
        if label_or_title in line and ("\\section" in line or "\\subsection" in line or "\\paragraph" in line):
            start = i
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        line = lines[j]
        if "\\section" in line or "\\subsection" in line:
            end = j
            break
    return (start, end)


def replace_block(tex: str, start_marker: str, end_marker: str, replacement: str) -> str:
    """Find a block bounded by start_marker .. end_marker (both inclusive) and replace."""
    s = tex.find(start_marker)
    if s == -1:
        print(f"  [warn] start marker not found: {start_marker[:60]!r}")
        return tex
    e = tex.find(end_marker, s + len(start_marker))
    if e == -1:
        print(f"  [warn] end marker not found: {end_marker[:60]!r}")
        return tex
    e = e + len(end_marker)
    return tex[:s] + replacement + tex[e:]


def insert_after(tex: str, marker: str, snippet: str) -> str:
    """Insert snippet immediately after the line containing marker."""
    idx = tex.find(marker)
    if idx == -1:
        print(f"  [warn] insertion marker not found: {marker[:60]!r}")
        return tex
    nl = tex.find("\n", idx)
    if nl == -1:
        return tex + "\n" + snippet
    return tex[: nl + 1] + snippet + tex[nl + 1 :]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="in_path", default="deliverables/paper.tex")
    ap.add_argument("--out", default="deliverables/paper_v2.tex")
    ap.add_argument("--paper-numbers", default="deliverables/paper_numbers.tex")
    args = ap.parse_args()

    tex = read(Path(args.in_path))
    pn_path = Path(args.paper_numbers)

    # ---- Step 1: include paper_numbers.tex if it exists ------------------
    if pn_path.exists() and "\\input{paper_numbers}" not in tex:
        tex = tex.replace(
            "\\usepackage{wrapfig}",
            "\\usepackage{wrapfig}\n\n% Auto-generated numbers from analyze_v2.py\n\\input{paper_numbers}"
        )
        print("[+] Inserted \\input{paper_numbers} after \\usepackage block")

    # ---- Step 2: print summary of what to manually verify ----------------
    print()
    print("=" * 70)
    print("MANUAL CHECKLIST BEFORE COMMITTING:")
    print("=" * 70)
    print("After this script, manually verify in the new file that:")
    print("  [ ] Abstract uses calibrated language (no false 'we prove')")
    print("  [ ] §3.3 and §3.4 are inserted correctly with new equations")
    print("  [ ] §5.6, §5.7, §5.8, §5.9 follow §5.5")
    print("  [ ] §6.1, §6.2 follow §6")
    print("  [ ] All [TBD] placeholders replaced with measured values")
    print("  [ ] Definition 1 uses per-class hidden activations")
    print("  [ ] Bibliography includes Jacot 2018, Roy 2007, Cardy 1996")
    print()
    print("This script's auto-edits are intentionally minimal -- it inserts")
    print("\\input{paper_numbers} and that's it.  The full integration")
    print("requires human judgment to apply paragraph-level edits cleanly.")
    print()
    print("Use the Edit tool with exact strings from PAPER_REPLACEMENTS.tex")
    print("and PAPER_ADDITIONS.tex to make the substantive changes.")
    print("=" * 70)

    Path(args.out).write_text(tex)
    print(f"\n[+] Wrote {args.out}")


if __name__ == "__main__":
    main()
