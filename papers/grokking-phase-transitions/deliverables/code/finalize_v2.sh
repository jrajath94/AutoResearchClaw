#!/usr/bin/env bash
# Final integration after all RunPod sweeps complete.
# Pulls all data, runs analyses, regenerates paper_numbers, recompiles.

set -euo pipefail

REPO=$( cd "$( dirname "${BASH_SOURCE[0]}" )/../.." && pwd )
cd "$REPO"

POD_IP="${POD_IP:-69.30.85.238}"
POD_PORT="${POD_PORT:-22058}"
SSH_KEY="$HOME/.ssh/id_ed25519"
PYBIN=/Users/rj/opt/anaconda3/bin/python

mkdir -p experiments/results_v2

echo "==> Step 1: pull all sweep data from runpod"
for tag in mod47 mod31 mod59 xfmr extended; do
  echo "  syncing $tag..."
  scp -rq -i "$SSH_KEY" -P "$POD_PORT" \
    "root@$POD_IP:/workspace/crisp/results/$tag" \
    experiments/results_v2/ 2>&1 | tail -1 || echo "  (no data for $tag)"
done

echo
echo "==> Step 2: analyze each task"
mkdir -p deliverables/figures_v2/mod47
$PYBIN deliverables/code/analyze_v2.py \
  --results-dir experiments/results_v2 \
  --out-dir deliverables/figures_v2/mod47 \
  --main-json mod47/sweep_add47.json 2>&1 | tail -10

# Multi-task analysis (smaller sweeps)
for tag in 31 59; do
  if [ -f "experiments/results_v2/mod$tag/sweep_add$tag.json" ]; then
    mkdir -p deliverables/figures_v2/mod$tag
    $PYBIN deliverables/code/analyze_v2.py \
      --results-dir experiments/results_v2 \
      --out-dir deliverables/figures_v2/mod$tag \
      --main-json mod$tag/sweep_add$tag.json 2>&1 | tail -5 || true
  fi
done

echo
echo "==> Step 3: render paper_numbers.tex"
$PYBIN deliverables/code/render_paper_numbers.py \
  --analysis-mod47 deliverables/figures_v2/mod47/analysis.json \
  --analysis-mod31 deliverables/figures_v2/mod31/analysis.json \
  --analysis-mod59 deliverables/figures_v2/mod59/analysis.json \
  --supplemental-v1 experiments/results/v1_supplemental.json \
  --extended-dir experiments/results_v2/extended \
  --out deliverables/paper_numbers.tex

echo
echo "==> Step 4: copy figures into deliverables/"
cp deliverables/figures_v2/mod47/fig*.png deliverables/ 2>/dev/null || true

echo
echo "==> Step 5: recompile paper.tex"
cd deliverables
pdflatex -interaction=nonstopmode paper.tex > /tmp/finalize.log 2>&1
pdflatex -interaction=nonstopmode paper.tex > /tmp/finalize.log 2>&1
errs=$(grep -E "^!" /tmp/finalize.log | head -3)
if [ -n "$errs" ]; then
  echo "  !! errors: $errs"
fi
pages=$(pdfinfo paper.pdf 2>/dev/null | grep Pages | awk '{print $2}')
size=$(ls -la paper.pdf 2>/dev/null | awk '{print $5}')
echo "  paper.pdf: $pages pages, $size bytes"

echo
echo "==> Step 6: TBD audit"
grep -c "TBD" paper_numbers.tex || true
echo "remaining \\TBD entries in paper_numbers.tex (lower is better)"

cat paper_numbers.tex | head -20
