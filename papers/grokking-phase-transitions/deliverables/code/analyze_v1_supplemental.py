"""Compute supplementary numbers from the EXISTING v1 sweep_results.json.

These don't require new instrumentation:
  - n_c per width (we already report this in Table 3)
  - beta fit per width on test loss (NEW)
  - bootstrap CI for beta
  - Schaeffer F1 sanity check (test loss vs accuracy curves)

Used while we wait for v2 data.
"""
import json
from pathlib import Path

import numpy as np
from scipy import stats


def load_v1(p: str = "experiments/results/sweep_results.json") -> list[dict]:
    return list(json.load(open(p)).values())


def critical_nc(runs: list[dict]) -> dict:
    """Smallest n where >=50% of seeds grokked, per width."""
    by_wf: dict = {}
    for r in runs:
        by_wf.setdefault((r["width"], r["train_frac"]), []).append(r)
    rates = {k: sum(rr["grokked"] for rr in v) / len(v) for k, v in by_wf.items()}

    nc_per_w: dict = {}
    widths = sorted({k[0] for k in rates.keys()})
    for w in widths:
        wfs = sorted([f for (ww, f), rate in rates.items()
                      if ww == w and rate >= 0.5])
        if not wfs:
            nc_per_w[w] = {"f_c": None, "n_c": None}
            continue
        f_c = wfs[0]
        n_c = next((rr["n_train"]
                    for (ww, ff), runs_ in by_wf.items()
                    for rr in runs_ if ww == w and ff == f_c), None)
        nc_per_w[w] = {"f_c": f_c, "n_c": n_c}
    return nc_per_w


def beta_fit(runs: list[dict], nc: dict, n_bootstrap: int = 1000) -> dict:
    """Fit log L_test = -beta * log(n) + C on n > n_c per width with bootstrap CI."""
    out = {}
    for w, info in nc.items():
        if info.get("n_c") is None:
            continue
        ns = []
        ls = []
        for r in runs:
            if r["width"] != w:
                continue
            n = r["n_train"]
            if n <= info["n_c"]:
                continue
            l = r.get("final_test_loss")
            if l is None or l == float("inf") or l <= 0:
                continue
            ns.append(n)
            ls.append(l)

        if len(ns) < 3:
            out[w] = {"n_points": len(ns), "beta": None}
            continue

        ns_a = np.array(ns)
        ls_a = np.array(ls)

        # Direct fit
        slope, intercept, r_val, p_val, sterr = stats.linregress(np.log(ns_a), np.log(ls_a))

        # Bootstrap (skip degenerate samples where all x are identical)
        rng = np.random.default_rng(42)
        bootstrap_betas = []
        attempts = 0
        while len(bootstrap_betas) < n_bootstrap and attempts < 10 * n_bootstrap:
            attempts += 1
            idx = rng.choice(len(ns_a), len(ns_a), replace=True)
            xs = np.log(ns_a[idx])
            if len(np.unique(xs)) < 2:
                continue
            slope_b, _, _, _, _ = stats.linregress(xs, np.log(ls_a[idx]))
            bootstrap_betas.append(-slope_b)
        if not bootstrap_betas:
            continue
        ci_lo, ci_hi = np.percentile(bootstrap_betas, [2.5, 97.5])

        out[w] = {
            "n_points": len(ns),
            "beta": float(-slope),
            "stderr": float(sterr),
            "r_squared": float(r_val ** 2),
            "p_value": float(p_val),
            "bootstrap_ci_95": [float(ci_lo), float(ci_hi)],
            "bootstrap_median": float(np.median(bootstrap_betas)),
        }
    return out


def f1_smoothness_check(runs: list[dict], nc: dict) -> dict:
    """F1: does test loss show same transition as test accuracy?

    For each width, check if final test loss decreases sharply at n_c.
    """
    out = {}
    for w, info in nc.items():
        nc_val = info.get("n_c")
        if nc_val is None:
            continue
        below = []
        above = []
        for r in runs:
            if r["width"] != w:
                continue
            l = r.get("final_test_loss")
            if l is None or l == float("inf"):
                continue
            if r["n_train"] < nc_val:
                below.append(l)
            else:
                above.append(l)
        if not below or not above:
            continue
        out[w] = {
            "n_below": len(below),
            "n_above": len(above),
            "loss_mean_below_nc": float(np.mean(below)),
            "loss_mean_above_nc": float(np.mean(above)),
            "ratio": float(np.mean(below) / max(np.mean(above), 1e-9)),
        }
    return out


if __name__ == "__main__":
    runs = load_v1()
    print(f"Loaded {len(runs)} runs from v1 sweep")
    print(f"  grokked: {sum(r['grokked'] for r in runs)}")
    print()

    nc = critical_nc(runs)
    print("Critical n_c per width (v1 data):")
    for w, info in nc.items():
        print(f"  w={w}  f_c={info['f_c']}  n_c={info['n_c']}")
    print()

    betas = beta_fit(runs, nc)
    print("beta fit per width (n > n_c regime):")
    for w, b in betas.items():
        if b.get("beta") is not None:
            ci = b["bootstrap_ci_95"]
            print(f"  w={w}  beta={b['beta']:.3f}  95% CI=[{ci[0]:.3f}, {ci[1]:.3f}]  R^2={b['r_squared']:.3f}  n={b['n_points']}")
        else:
            print(f"  w={w}  insufficient data")
    print()

    f1 = f1_smoothness_check(runs, nc)
    print("F1 smoothness check (test loss below vs above n_c):")
    for w, info in f1.items():
        print(f"  w={w}  loss_below={info['loss_mean_below_nc']:.3f}  loss_above={info['loss_mean_above_nc']:.3f}  ratio={info['ratio']:.1f}x")

    # Save all to JSON
    out = {"n_c": nc, "beta": betas, "f1": f1}
    Path("experiments/results/v1_supplemental.json").write_text(json.dumps(out, indent=2))
    print("\nSaved to experiments/results/v1_supplemental.json")
