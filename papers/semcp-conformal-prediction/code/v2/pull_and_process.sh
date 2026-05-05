#!/bin/bash
# Pull SemCP v2 results from the pod and run the full post-processing pipeline.
# Run: bash pull_and_process.sh
set -e
POD_HOST="root@104.255.9.187"
POD_PORT="12197"

REPO_ROOT="/Users/rj/research-claw/papers/semcp-conformal-prediction"
RESULTS_LOCAL="$REPO_ROOT/artifacts/v2_results"
DATA_LOCAL="$REPO_ROOT/artifacts/v2_data"

mkdir -p "$RESULTS_LOCAL" "$DATA_LOCAL"

echo "=== [1/5] Pull results JSONs ==="
scp -P "$POD_PORT" -o StrictHostKeyChecking=no -r "$POD_HOST:/workspace/semcp/results/" "$RESULTS_LOCAL/" 2>&1 | tail -3
# Move so it's not nested
if [ -d "$RESULTS_LOCAL/results" ]; then
  rm -rf "$RESULTS_LOCAL/triviaqa" "$RESULTS_LOCAL/squad" "$RESULTS_LOCAL/nq_open" "$RESULTS_LOCAL/triviaqa_alpha" 2>/dev/null
  mv "$RESULTS_LOCAL/results"/* "$RESULTS_LOCAL/" 2>/dev/null || true
  rmdir "$RESULTS_LOCAL/results" 2>/dev/null || true
fi
ls "$RESULTS_LOCAL/"

echo "=== [2/5] Pull raw sample pools (for HF Datasets release) ==="
scp -P "$POD_PORT" -o StrictHostKeyChecking=no \
  "$POD_HOST:/workspace/semcp/data/{triviaqa,squad,nq_open}_pool.{json,npz}" \
  "$DATA_LOCAL/" 2>&1 | tail -5 || echo "(some files may not exist yet)"

echo "=== [3/5] Inject real numbers into paper ==="
cd "$REPO_ROOT"
python3 code/v2/inject_results_v2.py \
  --results_dir "$RESULTS_LOCAL" \
  --paper_in artifacts/v2_revision/paper_v2_template.tex \
  --paper_out artifacts/deliverables/paper_v2.tex \
  --audit_out artifacts/v2_revision/CLAIM_AUDIT.md

echo "=== [4/6] Regenerate figures ==="
python3 code/v2/make_figures_v2.py \
  --results_dir "$RESULTS_LOCAL" \
  --out_dir artifacts/deliverables/charts/
python3 code/v2/pareto_figure.py \
  --results_dir "$RESULTS_LOCAL" \
  --out artifacts/deliverables/charts/fig_pareto.pdf || true

echo "=== [5/6] Coverage validity analysis ==="
python3 code/v2/coverage_validity_analysis.py \
  --results_dir "$RESULTS_LOCAL" \
  --out artifacts/v2_revision/coverage_validity.json

echo "=== [6/6] Final integrity audit ==="
python3 code/v2/integrity_audit.py \
  --paper artifacts/deliverables/paper_v2.tex \
  --results_dir "$RESULTS_LOCAL" \
  --out artifacts/v2_revision/INTEGRITY_AUDIT.md

echo ""
echo "=== POST-PROCESSING DONE ==="
echo "Paper:  $REPO_ROOT/artifacts/deliverables/paper_v2.tex"
echo "Audit:  $REPO_ROOT/artifacts/v2_revision/INTEGRITY_AUDIT.md"
echo "Claims: $REPO_ROOT/artifacts/v2_revision/CLAIM_AUDIT.md"
echo ""
echo "Next: compile paper.tex, then call mcp__runpod__delete-pod to terminate."
