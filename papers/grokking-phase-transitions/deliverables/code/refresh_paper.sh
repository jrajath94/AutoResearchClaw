#!/usr/bin/env bash
# Refresh: pull latest mod-47 data from RunPod, re-run analysis, re-render
# numbers, recompile paper. Idempotent; safe to run repeatedly.
#
# Usage: ./refresh_paper.sh

set -euo pipefail

REPO=$( cd "$( dirname "${BASH_SOURCE[0]}" )/../.." && pwd )
cd "$REPO"

POD="root@104.255.9.187"
PORT=12197
SSH_KEY="$HOME/.ssh/id_ed25519"
PYBIN=/Users/rj/opt/anaconda3/bin/python

mkdir -p experiments/results_v2/mod47 experiments/results_v2/extended_inc deliverables/figures_v2/mod47

echo "==> Step 1: pull mod47 data"
scp -q -i "$SSH_KEY" -P "$PORT" \
  "$POD:/workspace/crisp/results/mod47/sweep_add47.json" \
  experiments/results_v2/mod47/sweep_add47.json 2>&1 | tail -1 || echo "(no mod47 yet)"

scp -rq -i "$SSH_KEY" -P "$PORT" \
  "$POD:/workspace/crisp/results/extended_inc/" \
  experiments/results_v2/ 2>&1 | tail -1 || true

echo "==> Step 2: analyze mod47"
$PYBIN deliverables/code/analyze_v2.py \
  --results-dir experiments/results_v2 \
  --out-dir deliverables/figures_v2/mod47 \
  --main-json mod47/sweep_add47.json 2>&1 | tail -8

echo "==> Step 3: render paper_numbers.tex"
$PYBIN deliverables/code/render_paper_numbers.py \
  --analysis-mod47 deliverables/figures_v2/mod47/analysis.json \
  --supplemental-v1 experiments/results/v1_supplemental.json \
  --extended-dir experiments/results_v2/extended_inc \
  --out deliverables/paper_numbers.tex

echo "==> Step 4: copy figures into deliverables/"
cp deliverables/figures_v2/mod47/fig*.png deliverables/ 2>/dev/null || true

echo "==> Step 5: recompile paper.tex"
cd deliverables
pdflatex -interaction=nonstopmode paper.tex > /tmp/refresh.log 2>&1
pdflatex -interaction=nonstopmode paper.tex > /tmp/refresh.log 2>&1
err=$(grep -E "^!" /tmp/refresh.log | head -3)
if [ -n "$err" ]; then
  echo "  !! errors:"
  echo "$err"
fi
pages=$(pdfinfo paper.pdf 2>/dev/null | grep Pages | awk '{print $2}')
size=$(ls -la paper.pdf 2>/dev/null | awk '{print $5}')
echo "  pages: $pages | size: $size bytes"

echo
echo "==> Done. Open deliverables/paper.pdf"
