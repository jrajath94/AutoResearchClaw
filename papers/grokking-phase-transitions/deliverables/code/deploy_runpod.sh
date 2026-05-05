#!/usr/bin/env bash
# Deploy CRISP code to RunPod and launch sweeps. Run from local Mac.
#
# Usage:  POD_IP=ip POD_PORT=port ./deploy_runpod.sh

set -euo pipefail

POD_IP="${POD_IP:?set POD_IP}"
POD_PORT="${POD_PORT:?set POD_PORT}"
SSH_KEY="$HOME/.ssh/id_ed25519"
REPO=$( cd "$( dirname "${BASH_SOURCE[0]}" )/../.." && pwd )

SSH="ssh -o StrictHostKeyChecking=accept-new -i $SSH_KEY -p $POD_PORT root@$POD_IP"
SCP="scp -o StrictHostKeyChecking=accept-new -i $SSH_KEY -P $POD_PORT"

echo "==> Verify connection"
$SSH "echo connected; nvidia-smi --query-gpu=name --format=csv,noheader; python --version"

echo "==> Prepare workspace"
$SSH "mkdir -p /workspace/crisp/code /workspace/crisp/results"
$SSH "pip -q install scipy 2>&1 | tail -2"

echo "==> Upload code"
$SCP \
  $REPO/deliverables/code/reproduce_v2.py \
  $REPO/deliverables/code/reproduce_v2_inc.py \
  $REPO/deliverables/code/reproduce_transformer.py \
  $REPO/deliverables/code/analyze_v2.py \
  root@$POD_IP:/workspace/crisp/code/

echo "==> Smoke test"
$SSH "cd /workspace/crisp && python -u code/reproduce_v2_inc.py \
    --output-dir results/smoke \
    --widths 128 --fractions 0.5 --seeds 42 \
    --steps 1500 --eval-every 200 --fisher-subsample 16" 2>&1 | tail -5

echo "==> Launch mod-47 (full instrumentation, 120 runs)"
$SSH 'cd /workspace/crisp && nohup python -u code/reproduce_v2_inc.py \
    --output-dir results/mod47 --p 47 --op add \
    --widths 32 48 64 96 128 \
    --fractions 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 \
    --seeds 42 137 256 \
    --steps 10000 --eval-every 100 --fisher-subsample 32 \
    --save-weights \
    > results/mod47.log 2>&1 < /dev/null & disown'

sleep 5
$SSH "ps -ef | grep reproduce_v2_inc | grep -v grep | head -2"
$SSH "tail -5 /workspace/crisp/results/mod47.log"

echo
echo "==> mod47 launched. To monitor:"
echo "    $SSH 'tail -f /workspace/crisp/results/mod47.log'"
echo "    $SSH 'ls /workspace/crisp/results/mod47/run_*.json | wc -l'"
