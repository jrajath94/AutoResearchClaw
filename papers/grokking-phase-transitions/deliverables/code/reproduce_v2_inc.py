"""CRISP v2 (incremental-save) -- writes one JSON per run instead of one
big JSON at the end.  Safe to kill and resume.  Used for follow-up sweeps.

Otherwise identical to reproduce_v2.py.

Usage:
    python reproduce_v2_inc.py --output-dir results/foo --p 47 --op add ...

Output:
    results/foo/run_w<W>_f<F>_s<S>.json   -- one file per run
    results/foo/sweep_<op><p>.json        -- aggregated, written after each run
    results/foo/summary_<op><p>.json      -- aggregated summary
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

# Re-use logic by importing from reproduce_v2 directly (same dir).
import sys
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from reproduce_v2 import (  # type: ignore
    P_DEFAULT, WIDTHS, FRACTIONS, SEEDS, STEPS, EVAL_EVERY,
    run_single, aggregate,
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", default="results_v2_inc")
    ap.add_argument("--p", type=int, default=P_DEFAULT)
    ap.add_argument("--op", default="add", choices=["add", "mul"])
    ap.add_argument("--widths", nargs="+", type=int, default=WIDTHS)
    ap.add_argument("--fractions", nargs="+", type=float, default=FRACTIONS)
    ap.add_argument("--seeds", nargs="+", type=int, default=SEEDS)
    ap.add_argument("--steps", type=int, default=STEPS)
    ap.add_argument("--eval-every", type=int, default=EVAL_EVERY)
    ap.add_argument("--fisher-subsample", type=int, default=16)
    ap.add_argument("--save-weights", action="store_true")
    args = ap.parse_args()

    out = Path(args.output_dir); out.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[inc] device={device}  p={args.p}  op={args.op}", flush=True)

    all_results: dict = {}
    total = len(args.widths) * len(args.fractions) * len(args.seeds)
    i = 0
    t_start = time.time()

    for w in args.widths:
        for f in args.fractions:
            for s in args.seeds:
                i += 1
                key = f"w{w}_f{f}_s{s}_{args.op}{args.p}"
                run_path = out / f"run_{key}.json"
                if run_path.exists():
                    # Resume: load and skip
                    r = json.loads(run_path.read_text())
                    all_results[key] = r
                    print(f"[{i:3d}/{total}] {key} (resumed from disk)", flush=True)
                    continue
                t0 = time.time()
                r = run_single(
                    width=w, frac=f, seed=s, p=args.p, op=args.op,
                    steps=args.steps, eval_every=args.eval_every,
                    device=device, fisher_subsample=args.fisher_subsample,
                )
                if not args.save_weights:
                    r.pop("W_out_final", None)
                    r.pop("W_in_a_final", None)
                    r.pop("W_in_b_final", None)
                run_path.write_text(json.dumps(r, indent=2))
                all_results[key] = r
                dt = time.time() - t0
                eta = (time.time() - t_start) / i * (total - i)
                print(
                    f"[{i:3d}/{total}] {key}  grok={r['grokked']}  "
                    f"S_H={r.get('S_H_class', [0])[-1] if r.get('S_H_class') else 0:.4f}  "
                    f"dt={dt:.1f}s  eta={eta/60:.1f}min", flush=True
                )
                # Update sweep aggregate after each run so we have a partial result file too
                (out / f"sweep_{args.op}{args.p}.json").write_text(
                    json.dumps(all_results, indent=2))

    (out / f"sweep_{args.op}{args.p}.json").write_text(
        json.dumps(all_results, indent=2))
    (out / f"summary_{args.op}{args.p}.json").write_text(
        json.dumps(aggregate(all_results), indent=2))
    print(f"[inc] done.  total time = {(time.time() - t_start) / 60:.1f} min",
          flush=True)


if __name__ == "__main__":
    main()
