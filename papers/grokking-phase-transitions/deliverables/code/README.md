# Reproduction Code: CRISP Paper

## Environment

```
python >= 3.11
torch  >= 2.1
numpy
scipy
matplotlib
```

## Reproduce the 120-run sweep

```bash
pip install torch numpy scipy matplotlib
python reproduce.py --output-dir results/
```

This produces:
- `results/sweep_results.json` — per-run training histories (120 runs)
- `results/summary.json` — per-condition aggregates (grok rate, mean delay, mean accuracy)

## Regenerate figures

After running the sweep, use `parse_and_plot.py` from the paper supplementary
(included in the `experiments/` folder of the repository) to regenerate the 6
publication figures from `sweep_results.json`.

## Configuration

Defaults match the paper (mod-47, AdamW lr=0.03, wd=0.3, 10K steps):

| Parameter | Value |
|-----------|-------|
| Task | (a+b) mod 47 |
| Widths | {32, 48, 64, 96, 128} |
| Training fractions | {0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9} |
| Seeds | {42, 137, 256} |
| Optimizer | AdamW |
| Learning rate | 0.03 |
| Weight decay | 0.3 |
| Training steps | 10,000 |
| Grokking criterion | test accuracy > 90% |

Override via CLI flags, e.g.:
```bash
python reproduce.py --widths 32 64 --fractions 0.5 0.7 --seeds 42
```

## Hardware

- Single A100: ~30 minutes
- Single V100 / 3090: ~45 minutes
- CPU: ~2 hours (numpy + torch CPU kernels)

## Expected Results

The paper reports:
- 69/120 runs (57.5%) grokked
- Grokking delay drops from 8,333 steps at w=64, f=0.5 to 667 steps at w=96, f=0.6
- Critical fraction f_c decreases monotonically: 0.7 (w=32), 0.6 (w=48), 0.5 (w=64, 96), 0.4 (w=128)

Seeds are fixed so results are deterministic up to hardware-level nondeterminism in CUDA.
