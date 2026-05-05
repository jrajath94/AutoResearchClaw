#!/usr/bin/env bash
# End-to-end paper finalization. Run after sweeps complete.
#
# Usage: ./finalize_paper.sh
#
# Pipeline:
#   1. Pull JSONs from RunPod
#   2. Run analyze_v2.py on each
#   3. Render paper_numbers.tex
#   4. Apply targeted Edits to paper.tex (manual step printed)
#   5. Compile LaTeX
#   6. Verify no [TBD] remain

set -euo pipefail

POD_HOST="root@104.255.9.187"
POD_PORT=12197
SSH_OPTS="-i $HOME/.ssh/id_ed25519 -p $POD_PORT"
PYBIN=/Users/rj/opt/anaconda3/bin/python

REPO=$( cd "$( dirname "${BASH_SOURCE[0]}" )/../.." && pwd )
cd "$REPO"

echo "==> Step 1: download all results from runpod"
mkdir -p experiments/results_v2
for tag in mod47 mod31 mod59 transformer_mod47 extended; do
  echo "  syncing $tag..."
  scp -r -q -i $HOME/.ssh/id_ed25519 -P $POD_PORT \
    "$POD_HOST:/workspace/crisp/results/$tag" \
    experiments/results_v2/ 2>/dev/null || echo "  (no results for $tag)"
done

echo "==> Step 2: run analysis on each task"
for tag in mod47 mod31 mod59; do
  if [ -f "experiments/results_v2/$tag/sweep_add$(echo $tag | sed 's/mod//').json" ]; then
    echo "  analyzing $tag..."
    mkdir -p "deliverables/figures_v2/$tag"
    $PYBIN deliverables/code/analyze_v2.py \
      --results-dir experiments/results_v2 \
      --out-dir deliverables/figures_v2/$tag \
      --main-json $tag/sweep_add$(echo $tag | sed 's/mod//').json \
      2>&1 | tee deliverables/figures_v2/$tag.log
  fi
done

echo "==> Step 3: render paper number macros"
for tag in mod47 mod31 mod59; do
  if [ -f "deliverables/figures_v2/$tag/analysis.json" ]; then
    $PYBIN deliverables/code/render_paper_numbers.py \
      --analysis "deliverables/figures_v2/$tag/analysis.json" \
      --out "deliverables/figures_v2/$tag/paper_numbers.tex"
  fi
done

# The main paper macros come from mod-47
if [ -f "deliverables/figures_v2/mod47/paper_numbers.tex" ]; then
  cp deliverables/figures_v2/mod47/paper_numbers.tex deliverables/paper_numbers.tex
  echo "==> paper_numbers.tex installed at deliverables/paper_numbers.tex"
  echo
  echo "Macro values:"
  cat deliverables/paper_numbers.tex
fi

echo
echo "==> Step 4: copy figures into deliverables/"
for fig in deliverables/figures_v2/mod47/fig*.png; do
  if [ -f "$fig" ]; then
    cp "$fig" deliverables/
    echo "  copied $(basename $fig)"
  fi
done

echo
echo "==> Step 5: NEXT - manually apply Edit operations to paper.tex"
echo "Refer to deliverables/PAPER_INTEGRATION_PLAN.md for the exact sequence."
echo
echo "To compile after edits:"
echo "  cd deliverables && pdflatex paper.tex && pdflatex paper.tex"
echo
echo "To verify no [TBD] remain:"
echo "  grep -n 'TBD' deliverables/paper.tex && echo 'WARNING: [TBD] remain' || echo 'OK: no [TBD]'"
