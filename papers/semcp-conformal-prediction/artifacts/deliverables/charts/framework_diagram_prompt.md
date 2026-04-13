# Framework Diagram Prompt

**Paper**: SemCP: Coverage Guarantees Over Meanings, Not Strings

## Image Generation Prompt

A professional academic methodology diagram for a machine learning conference paper, vector-art flat design style with subtle drop shadows on a white background. Left-to-right horizontal data flow pipeline for "SemCP: Semantic Conformal Prediction."

Starting from the left: a rounded-corner box labeled "Prompt x" in dark grey (#333333) with a document icon, colored soft purple (#AA3377) fill with white text. A bold directional arrow flows right to a larger rounded box labeled "LLM" colored muted blue (#4477AA) with white text, containing a small subtitle "K=20 samples." From this box, K=5 visible short text snippets fan out as thin parallel lines representing sampled responses y_1 through y_K, each shown as small white rounded rectangles with grey (#666666) one-line text labels like "Paris", "The capital is Paris", "It's Paris", "France's capital", "Lyon" to illustrate paraphrase diversity.

These fan lines converge into the next stage: a rounded box labeled "Bidirectional Entailment" colored teal (#44AA99) with white text, with a small "NLI Model" annotation beneath in grey italic. Inside or adjacent, show 2-3 dashed rounded grouping outlines clustering the paraphrases into meaning equivalence classes [y]_s, with a warm yellow accent (#CCBB44) highlight on cluster boundaries. One cluster groups four Paris variants, another isolates "Lyon."

Arrow flows right to a box labeled "Kernel Scoring" in muted blue (#4477AA), with the equation "s(x,y) = 1 - κ_θ(φ(y), μ_x)" annotated below in small monospace font. A small embedding space visualization appears as a subtle 2D scatter with a centroid dot.

Final arrow flows to a box labeled "Conformal Calibration" in soft purple (#AA3377), with "threshold q̂" annotated, outputting to the rightmost rounded box labeled "Semantic Prediction Set C(x*)" with a warm yellow (#CCBB44) fill and dark text, showing the final output as meaning classes rather than strings. Below the pipeline, a thin horizontal bracket labeled "3.1% overhead vs. LLM generation" spans the three SemCP-specific stages. All arrows are dark grey (#444444) with pointed heads, consistent 2px stroke. Labels use clean sans-serif font, sizes hierarchical. No photorealism, no gradients except very subtle box shadows.

## Usage Instructions

1. Copy the prompt above into an AI image generator (DALL-E 3, Midjourney, Ideogram, etc.)
2. Generate the image at high resolution (2048x1024 or similar landscape)
3. Save as `framework_diagram.png` in the same `charts/` folder
4. Insert into the paper's Method section using:
   - LaTeX: `\includegraphics[width=\textwidth]{charts/framework_diagram.png}`
   - Markdown: `![Framework Overview](charts/framework_diagram.png)`
