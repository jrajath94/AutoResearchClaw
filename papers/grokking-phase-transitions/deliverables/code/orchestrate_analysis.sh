#!/bin/bash
# Orchestrates: wait for all sweeps, download JSONs, run analyses, fill paper.
# Run from local Mac.

set -e
POD_HOST="root@104.255.9.187"
POD_PORT="12197"
SSH="ssh -i $HOME/.ssh/id_ed25519 -p $POD_PORT $POD_HOST"
SCP="scp -i $HOME/.ssh/id_ed25519 -P $POD_PORT"

REPO_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../.." && pwd )"
LOCAL_RESULTS="$REPO_DIR/experiments/results_v2"
mkdir -p "$LOCAL_RESULTS"

echo "==> Polling for sweep completion..."
while true; do
  status=$($SSH 'cd /workspace/crisp && \
    for d in mod47 transformer_mod47 mod31 mod59; do \
      if [ -f "results/$d/sweep_$(echo $d | sed s/transformer_//).json" ] || \
         [ -f "results/$d/sweep_xfmr_mod47.json" ] || \
         [ -f "results/$d/sweep_add_$(echo $d | sed s/mod//).json" ]; then \
        echo "$d:DONE"; \
      else \
        if ps aux | grep -E "reproduce.*--output-dir results/$d" | grep -v grep > /dev/null; then \
          echo "$d:RUNNING"; \
        else \
          echo "$d:STOPPED"; \
        fi; \
      fi; \
    done')
  echo "$(date +%H:%M:%S) $status"
  if echo "$status" | grep -qv DONE; then
    sleep 60
  else
    echo "all done"
    break
  fi
done

echo "==> Downloading results..."
$SCP -r $POD_HOST:/workspace/crisp/results/mod47          "$LOCAL_RESULTS/" || true
$SCP -r $POD_HOST:/workspace/crisp/results/transformer_mod47  "$LOCAL_RESULTS/" || true
$SCP -r $POD_HOST:/workspace/crisp/results/mod31          "$LOCAL_RESULTS/" || true
$SCP -r $POD_HOST:/workspace/crisp/results/mod59          "$LOCAL_RESULTS/" || true

echo "==> Running analyses..."
PYBIN="/Users/rj/opt/anaconda3/bin/python"
$PYBIN "$REPO_DIR/deliverables/code/analyze_v2.py" \
  --results-dir "$LOCAL_RESULTS" \
  --out-dir "$REPO_DIR/deliverables/figures_v2/mod47" \
  --main-json "mod47/sweep_add47.json" 2>&1 | tee "$REPO_DIR/deliverables/figures_v2/mod47.log"

for tag in 31 59; do
  $PYBIN "$REPO_DIR/deliverables/code/analyze_v2.py" \
    --results-dir "$LOCAL_RESULTS" \
    --out-dir "$REPO_DIR/deliverables/figures_v2/mod$tag" \
    --main-json "mod$tag/sweep_add$tag.json" 2>&1 | tee "$REPO_DIR/deliverables/figures_v2/mod$tag.log" || true
done

echo "==> Done. Outputs in $REPO_DIR/deliverables/figures_v2/"
