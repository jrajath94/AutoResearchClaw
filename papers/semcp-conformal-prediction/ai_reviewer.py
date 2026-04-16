"""AI Paper Reviewer using MiniMax API.

Usage:
    export MINIMAX_API_KEY="your-token-here"
    python ai_reviewer.py artifacts/deliverables/paper.pdf

Produces a NeurIPS-style structured review with scores on:
- Quality, Clarity, Significance, Originality (1-4 each)
- Overall rating (1-6)
- Detailed strengths, weaknesses, questions, and improvement suggestions.

Extracts text from PDF, sends to MiniMax with a NeurIPS reviewer prompt,
and writes the structured review to disk.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import requests

# Extract text from PDF using pymupdf (pre-installed in .venv)
try:
    import fitz  # pymupdf
except ImportError:
    print("ERROR: pymupdf not installed. Run: pip install pymupdf")
    sys.exit(1)


MINIMAX_API_URL = "https://api.minimaxi.com/v1/text/chatcompletion_v2"


NEURIPS_REVIEWER_PROMPT = """You are a Program Committee member for NeurIPS 2026, one of the most
selective machine learning venues (acceptance rate ~25%). You are a domain
expert known for rigorous, fair, and constructive reviews that reliably
separate groundbreaking contributions from incremental work.

Produce a world-class peer review following the exact NeurIPS 2025/2026
reviewer template. Match the rigor, tone, and depth of top-tier reviews.

**REQUIRED REVIEW STRUCTURE** (follow exactly):

## Summary
Concise 3-5 sentence factual summary of the paper's claims, method, and
results. No evaluation - just state what the paper does.

## Strengths
Use bold subheaders for each strength category. Provide 2-3 concrete
strengths per category with specific evidence from the paper:
- **Technical novelty and innovation**: what is genuinely new?
- **Experimental rigor and validation**: what is done well?
- **Clarity of presentation**: what is communicated effectively?
- **Significance of contributions**: why does this matter?

## Weaknesses
Use bold subheaders. For each weakness, cite specific page/section/line
numbers and explain why it matters. Be direct but constructive:
- **Technical limitations or concerns**
- **Experimental gaps or methodological issues**
- **Clarity or presentation issues**
- **Missing related work or comparisons**

## Detailed Comments
Provide substantive technical discussion (300+ words) covering:
- **Technical soundness evaluation**: are the claims rigorously supported?
  Check theorems, proofs, and assumptions. Identify any gaps.
- **Experimental evaluation assessment**: are the experiments sufficient
  to support the claims? Are baselines appropriate? Are error bars
  meaningful? Are there missing ablations?
- **Comparison with related work**: how does this compare quantitatively
  and conceptually to the most relevant prior work?
- **Discussion of broader impact and significance**: who benefits? What
  is the likely influence on the field?

## Questions for Authors
List 6-10 specific, technical questions. These should be questions a
reviewer would genuinely want answered during rebuttal - not rhetorical
critiques. Number them Q1, Q2, etc.

## Scores
Provide ALL of the following on separate lines:
- **Quality**: X/4 with one-sentence justification
- **Clarity**: X/4 with one-sentence justification
- **Significance**: X/4 with one-sentence justification
- **Originality**: X/4 with one-sentence justification
- **Soundness**: X/4 with one-sentence justification
- **Presentation**: X/4 with one-sentence justification
- **Contribution**: X/4 with one-sentence justification
- **Confidence**: X/5 (1=guess, 5=absolutely certain)
- **Overall**: X/6 where:
  * 6 = Strong Accept (flawless, groundbreaking impact)
  * 5 = Accept (solid, high impact)
  * 4 = Weak Accept (reasons to accept outweigh reject)
  * 3 = Weak Reject (reasons to reject outweigh accept)
  * 2 = Reject (technical flaws, weak evaluation)
  * 1 = Strong Reject (unaddressed ethical issues or known results)

## Overall Assessment
5-8 sentences stating your final recommendation. Explain:
1. The core contribution in one sentence
2. Whether the evidence supports the claims
3. Whether the work advances the state of the art
4. Specific conditions under which you would change your score
5. Final recommendation

## Confidence Justification
Explain why you assigned your confidence score. Did you read everything?
Are you an expert in this specific subfield?

**TONE GUIDELINES**:
- Be direct. NeurIPS reviewers do not hedge.
- Cite specific line numbers, equations, tables, and figures.
- Identify overclaims and underclaims explicitly.
- When criticizing, propose what would fix the issue.
- Do not pad. Every sentence should carry information.
- Treat the authors as serious researchers deserving serious feedback.

**RED FLAGS to check explicitly**:
- Are results statistically significant with proper error bars?
- Are baselines current (not 5+ years old)?
- Is the experimental setup reproducible (seeds, hyperparameters, hardware)?
- Are there fabricated or cherry-picked numbers?
- Does the paper claim more than the evidence supports?
- Are there missing ablations that would isolate the contribution?
- Is the math rigorous, with all assumptions stated?
- Are the figures informative and non-misleading (e.g., y-axis ranges)?
"""


PERSONAS = {
    "theorist": "You emphasize theoretical rigor: theorem statements, proof validity, assumptions, and mathematical precision. You are skeptical of claims not backed by proofs.",
    "empiricist": "You emphasize experimental rigor: benchmark coverage, baseline strength, statistical significance, and reproducibility. You are skeptical of claims not backed by strong experiments.",
    "skeptic": "You are a domain expert who looks for overclaims, missing comparisons, and weak scholarship. You reward honest negative results and penalize fabricated or unsupported claims.",
}


def extract_pdf_text(pdf_path: str, max_pages: int = 20) -> str:
    """Extract plain text from the first N pages of a PDF."""
    doc = fitz.open(pdf_path)
    pages = []
    for i, page in enumerate(doc):
        if i >= max_pages:
            break
        pages.append(f"=== Page {i + 1} ===\n{page.get_text()}")
    doc.close()
    return "\n\n".join(pages)


def _call_minimax(messages: list, api_key: str, model: str) -> dict:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": messages, "max_tokens": 8192, "temperature": 0.3}
    resp = requests.post(MINIMAX_API_URL, headers=headers, json=payload, timeout=600)
    resp.raise_for_status()
    return resp.json()


def review_paper(pdf_path: str, api_key: str, model: str = "MiniMax-M2") -> dict:
    """Run 3 reviewer personas + meta-review, simulating a NeurIPS review panel."""
    print(f"Extracting text from {pdf_path}...")
    paper_text = extract_pdf_text(pdf_path)
    print(f"  Extracted {len(paper_text):,} characters")

    reviews = {}
    for persona_name, persona_desc in PERSONAS.items():
        print(f"\n>>> Reviewer {persona_name.upper()} generating review...")
        sys_prompt = NEURIPS_REVIEWER_PROMPT + f"\n\n**Your Persona**: {persona_desc}"
        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": f"Please review the following paper:\n\n{paper_text}"},
        ]
        data = _call_minimax(messages, api_key, model)
        content = data["choices"][0]["message"]["content"]
        reviews[persona_name] = {"review": content, "usage": data.get("usage", {})}
        print(f"    Done ({len(content):,} chars)")

    # Meta-review: synthesize the 3 reviews
    print(f"\n>>> Meta-reviewer synthesizing final recommendation...")
    meta_prompt = """You are the NeurIPS Area Chair. Three expert reviewers
have submitted reviews. Write a meta-review that:
1. Summarizes the consensus and divergences across reviews
2. Identifies the 3 most important issues to address
3. Provides a final accept/reject recommendation with score X/6
4. Lists concrete conditions under which the paper would be accepted
Be decisive. Area Chairs do not hedge."""
    reviews_concat = "\n\n---\n\n".join(
        f"## REVIEWER {name.upper()}\n\n{r['review']}" for name, r in reviews.items()
    )
    meta_messages = [
        {"role": "system", "content": meta_prompt},
        {"role": "user", "content": reviews_concat},
    ]
    meta_data = _call_minimax(meta_messages, api_key, model)
    meta_content = meta_data["choices"][0]["message"]["content"]

    return {
        "reviews": reviews,
        "meta_review": meta_content,
        "meta_usage": meta_data.get("usage", {}),
        "model": model,
    }


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python ai_reviewer.py <paper.pdf> [--model MiniMax-M2]")
        return 1

    pdf_path = sys.argv[1]
    if not Path(pdf_path).is_file():
        print(f"ERROR: file not found: {pdf_path}")
        return 1

    api_key = os.environ.get("MINIMAX_API_KEY")
    if not api_key:
        print("ERROR: set MINIMAX_API_KEY environment variable")
        return 1

    model = "MiniMax-M2"
    if "--model" in sys.argv:
        model = sys.argv[sys.argv.index("--model") + 1]

    result = review_paper(pdf_path, api_key, model=model)

    out_md = Path(pdf_path).with_suffix(".reviews.md")
    sections = [f"# NeurIPS-Style Panel Review ({result['model']})\n",
                f"**Paper:** {pdf_path}\n"]
    for name, r in result["reviews"].items():
        sections.append(f"\n---\n\n# Reviewer: {name.capitalize()}\n\n{r['review']}\n")
    sections.append(f"\n---\n\n# Area Chair Meta-Review\n\n{result['meta_review']}\n")
    out_md.write_text("\n".join(sections))
    print(f"\nPanel review saved to: {out_md}")

    out_json = Path(pdf_path).with_suffix(".reviews.json")
    out_json.write_text(json.dumps(result, indent=2))
    print(f"Raw JSON saved to: {out_json}")

    print("\n" + "=" * 70)
    print("AREA CHAIR META-REVIEW")
    print("=" * 70)
    print(result["meta_review"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
