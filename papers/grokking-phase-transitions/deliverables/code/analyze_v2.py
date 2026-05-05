"""CRISP v2 analysis pipeline — converts sweep JSONs into all NeurIPS revision figures.

Reads sweep_*.json and produces:
  - F3 Pearson r values for each candidate S metric (P1.2)
  - n_eff(t) trajectories aligned to grok onset (P1.1)
  - Spectral analysis -> F_eff(w) and gamma (P1.3)
  - Power-law fit of test-loss in clean regime -> beta (P2.1)
  - Finite-size scaling collapse (Novelty boost N1)
  - Multi-task universality table (P2.2)

Usage:
    python analyze_v2.py --results-dir results/ --out-dir figures_v2/
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

# NeurIPS-style figure defaults
plt.rcParams.update({
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 11,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "axes.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 100,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.05,
})


# ============================================================================
# F3: correlation between S-drop step and grok onset
# ============================================================================
def s_midpoint_step(steps: list[int], traj: list[float]) -> int | None:
    """Return first step at which S(t) crosses the midpoint between S(0) and S(end).

    More robust than thresholding at 0.5*S_initial, especially when the initial
    value is already small (as is the case for S_W_out under Glorot init).
    """
    if not traj or len(traj) < 2:
        return None
    s0, s_end = traj[0], traj[-1]
    if abs(s0 - s_end) < 1e-9:
        return None
    mid = (s0 + s_end) / 2.0
    sign = 1.0 if s0 > s_end else -1.0
    for st, s in zip(steps, traj):
        if sign * (s0 - s) >= sign * (s0 - mid):
            return st
    return None


def f3_correlation(runs: list[dict], s_metric: str) -> dict:
    """Pearson r between S-mid step and grokking onset across all grokking runs.

    Uses midpoint-based drop step (more robust than 50%-of-initial threshold).
    Also reports correlation against the *legacy* drop step from JSON for ref.

    NOTE: F3 is meant to measure cross-(width, fraction) correlation -- the
    statement is "S drops at the same time grokking happens, across conditions."
    Within a single width/fraction, variance is mostly seed noise and is not
    expected to correlate.  We therefore also report the correlation aggregated
    by condition (mean grok_step vs mean S-mid step per (w, f) cell).
    """
    pairs_mid = []
    pairs_legacy = []
    by_cond: dict = {}
    for r in runs:
        if not r.get("grokked"):
            continue
        if r.get("grok_step") is None:
            continue
        traj = r.get(s_metric)
        if not traj:
            continue
        midstep = s_midpoint_step(r["step"], traj)
        if midstep is not None:
            pairs_mid.append((midstep, r["grok_step"]))
            cond = (r["width"], r["train_frac"])
            by_cond.setdefault(cond, []).append((midstep, r["grok_step"]))
        legacy = r.get(f"{s_metric}_drop_step")
        if legacy is not None:
            pairs_legacy.append((legacy, r["grok_step"]))

    out = {"s_metric": s_metric}
    if len(pairs_mid) >= 3:
        xs, ys = zip(*pairs_mid)
        r_mid, p_mid = stats.pearsonr(xs, ys)
        out["r_midpoint"] = float(r_mid)
        out["p_midpoint"] = float(p_mid)
        out["n_midpoint"] = len(pairs_mid)
        out["median_alignment_err_midpoint"] = float(
            np.median([abs(x - y) for x, y in pairs_mid]))
    else:
        out["r_midpoint"] = None
        out["n_midpoint"] = len(pairs_mid)

    if len(pairs_legacy) >= 3:
        xs, ys = zip(*pairs_legacy)
        r_lg, p_lg = stats.pearsonr(xs, ys)
        out["r_legacy"] = float(r_lg)
        out["p_legacy"] = float(p_lg)
        out["n_legacy"] = len(pairs_legacy)
    else:
        out["r_legacy"] = None
        out["n_legacy"] = len(pairs_legacy)

    # Cross-condition correlation (one (S-mid, grok) pair per condition)
    cond_pairs = [
        (np.mean([s for s, g in v]), np.mean([g for s, g in v]))
        for v in by_cond.values() if len(v) >= 1
    ]
    if len(cond_pairs) >= 3:
        xs, ys = zip(*cond_pairs)
        r_cc, p_cc = stats.pearsonr(xs, ys)
        out["r_cross_cond"] = float(r_cc)
        out["p_cross_cond"] = float(p_cc)
        out["n_cross_cond"] = len(cond_pairs)
    else:
        out["r_cross_cond"] = None
        out["n_cross_cond"] = len(cond_pairs)

    return out


# ============================================================================
# n_eff(t) tracking: derived from accumulated Fisher information
# ============================================================================
def fit_n_eff_alignment(runs: list[dict]) -> dict:
    """For each grokking run, find the step at which fisher_trace falls to 5x its
    final value (the 'information saturation' step) and correlate with grok_step.

    Definition: n_eff(t) := n * (Fisher(0) / Fisher(t)) is monotone increasing.
    The grok step should align with n_eff(t) crossing n_c.  We approximate this
    by finding when Fisher(t) drops below a threshold.
    """
    saturated_steps = []
    grok_steps = []
    for r in runs:
        if not r.get("grokked"):
            continue
        ft = r.get("fisher_trace") or []
        steps = r.get("step") or []
        if not ft or not steps:
            continue
        ft_final = max(ft[-1], 1e-10)
        threshold = 5.0 * ft_final
        sat = None
        for st, f in zip(steps, ft):
            if f <= threshold:
                sat = st
                break
        if sat is not None:
            saturated_steps.append(sat)
            grok_steps.append(r["grok_step"])

    if len(saturated_steps) < 3:
        return {"n": len(saturated_steps), "r": None}
    r, p = stats.pearsonr(saturated_steps, grok_steps)
    return {
        "n": len(saturated_steps),
        "r": float(r),
        "p": float(p),
        "median_alignment_error": float(
            np.median([abs(s - g) for s, g in zip(saturated_steps, grok_steps)])),
    }


# ============================================================================
# F_eff(w): from spectral analysis of W_out
# ============================================================================
def spectral_F_eff(runs: list[dict]) -> dict:
    """Compute effective rank of W_out W_out^T (spectral entropy) per width,
    averaged over seeds at the largest grokking fraction.  Then fit
    F_eff(w) ~ F * (w/w_0)^(-gamma)."""
    by_width: dict = {}
    for r in runs:
        if not r.get("grokked"):
            continue
        w = r["width"]
        if r.get("eff_rank_W_out"):
            by_width.setdefault(w, []).append(r["eff_rank_W_out"][-1])
    if len(by_width) < 3:
        return {"n_widths": len(by_width)}
    widths = sorted(by_width.keys())
    F_eff = [float(np.mean(by_width[w])) for w in widths]

    log_w = np.log(np.array(widths))
    log_F = np.log(np.array(F_eff))
    slope, intercept, r_val, p_val, _ = stats.linregress(log_w, log_F)
    return {
        "widths": widths,
        "F_eff_per_width": F_eff,
        "gamma": float(-slope),
        "intercept": float(intercept),
        "r_squared": float(r_val ** 2),
        "p_value": float(p_val),
    }


# ============================================================================
# Beta scaling: power-law fit on clean regime
# ============================================================================
def beta_fit(runs: list[dict], n_c_per_width: dict[int, float]) -> dict:
    """Fit log L_test = -beta * log(n) + C for n > n_c, per width."""
    out = {}
    for w, n_c in n_c_per_width.items():
        ns = []
        ls = []
        for r in runs:
            if r["width"] != w:
                continue
            n = r["n_train"]
            if n <= n_c:
                continue
            l_te = r.get("final_test_loss")
            if l_te is None or l_te == float("inf") or l_te <= 0:
                continue
            ns.append(n)
            ls.append(l_te)
        if len(ns) < 3:
            out[w] = {"n_points": len(ns), "beta": None}
            continue
        slope, intercept, r_val, p_val, sterr = stats.linregress(np.log(ns), np.log(ls))
        out[w] = {
            "n_points": len(ns),
            "beta": float(-slope),
            "intercept": float(intercept),
            "r_squared": float(r_val ** 2),
            "p_value": float(p_val),
            "stderr": float(sterr),
        }
    return out


# ============================================================================
# Critical n_c per width
# ============================================================================
def critical_nc(runs: list[dict]) -> dict[int, dict]:
    """For each width, find smallest n_train where >= 50% of seeds grokked."""
    by_wf: dict = {}
    for r in runs:
        key = (r["width"], r["train_frac"])
        by_wf.setdefault(key, []).append(r)
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


# ============================================================================
# Finite-size scaling collapse
# ============================================================================
def scaling_collapse_data(runs: list[dict], nc_per_w: dict, nu: float = 0.5) -> dict:
    """Compute rescaled (n - n_c) * w^{1/nu} vs grok_rate for collapse plot."""
    out = []
    by_wf: dict = {}
    for r in runs:
        by_wf.setdefault((r["width"], r["train_frac"]), []).append(r)
    for (w, f), rs in by_wf.items():
        info = nc_per_w.get(w, {})
        if info.get("n_c") is None:
            continue
        n = rs[0]["n_train"]
        n_c = info["n_c"]
        x = (n - n_c) * (w ** (1.0 / nu))
        rate = sum(rr["grokked"] for rr in rs) / len(rs)
        out.append({"width": w, "frac": f, "n_train": n, "x_rescaled": float(x), "grok_rate": rate})
    return {"nu_used": nu, "points": out}


# ============================================================================
# Plotting (one figure per analysis)
# ============================================================================
def plot_n_eff_trajectories(runs: list[dict], out_path: Path) -> None:
    """Figure 7: log10(fisher_trace) vs step, colored by grokked, with grok_step marked."""
    fig, ax = plt.subplots(1, 1, figsize=(8, 5))
    for r in runs:
        if not r.get("step"):
            continue
        ft = r.get("fisher_trace") or []
        if not ft:
            continue
        color = "C2" if r.get("grokked") else "0.7"
        alpha = 0.6 if r.get("grokked") else 0.2
        ax.plot(r["step"], np.log10(np.maximum(np.array(ft), 1e-10)),
                color=color, alpha=alpha, lw=0.8)
        if r.get("grok_step") and r["grok_step"] in r["step"]:
            i = r["step"].index(r["grok_step"])
            ax.scatter([r["grok_step"]], [np.log10(max(ft[i], 1e-10))],
                       color="C3", s=15, alpha=0.8, zorder=10)
    ax.set_xlabel("Training step")
    ax.set_ylabel(r"$\log_{10}(\mathrm{tr}\,\hat F)$")
    ax.set_title(r"Fisher trace trajectories (red dots = grokking onset)")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_F_eff(spectral: dict, out_path: Path) -> None:
    """Figure 8: log F_eff vs log w with power-law fit."""
    if "widths" not in spectral:
        return
    widths = spectral["widths"]
    F_eff = spectral["F_eff_per_width"]
    gamma = spectral["gamma"]
    fig, ax = plt.subplots(1, 1, figsize=(7, 5))
    ax.loglog(widths, F_eff, "o-", color="C0", label="measured")
    fit_ys = [np.exp(spectral["intercept"]) * (w ** (-gamma)) for w in widths]
    ax.loglog(widths, fit_ys, "--", color="C3",
              label=fr"fit: $F_{{eff}} \propto w^{{-{gamma:.3f}}}$ ($R^2={spectral['r_squared']:.3f}$)")
    ax.set_xlabel("width $w$")
    ax.set_ylabel("effective rank of $W_{out} W_{out}^T$")
    ax.set_title(r"$F_{eff}(w)$ from spectral entropy")
    ax.legend()
    ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_S_metrics(runs: list[dict], out_path: Path) -> None:
    """Figure 4-supp: Compare S_W_out, S_W_in_a, S_H_class trajectories for grokking runs."""
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.5), sharey=False)
    metrics = ["S_W_out", "S_W_in_a", "S_H_class"]
    titles = [r"$S(W_{out})$", r"$S(W_{in}^a)$", r"$S(H_{class})$"]
    for ax, m, t in zip(axes, metrics, titles):
        for r in runs:
            if not r.get(m):
                continue
            color = "C2" if r.get("grokked") else "0.6"
            alpha = 0.5 if r.get("grokked") else 0.15
            ax.plot(r["step"], r[m], color=color, alpha=alpha, lw=0.8)
        ax.set_xlabel("Training step")
        ax.set_ylabel(t)
        ax.set_title(f"{t}: green=grokked, gray=memorized")
        ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_f3_scatter(runs: list[dict], out_path: Path, s_metric: str = "S_W_in_b") -> None:
    """Figure 4-main: scatter of S-midpoint step vs grok step, colored by width."""
    pts = []
    for r in runs:
        if not r.get("grokked") or r.get("grok_step") is None:
            continue
        traj = r.get(s_metric)
        if not traj:
            continue
        midstep = s_midpoint_step(r["step"], traj)
        if midstep is not None:
            pts.append((r["width"], midstep, r["grok_step"]))
    if not pts:
        return
    fig, ax = plt.subplots(figsize=(7, 5.5))
    widths = sorted({p[0] for p in pts})
    cmap = plt.colormaps["viridis"]
    for i, w in enumerate(widths):
        wpts = [p for p in pts if p[0] == w]
        xs = [p[1] for p in wpts]
        ys = [p[2] for p in wpts]
        ax.scatter(xs, ys, color=cmap(i / max(1, len(widths)-1)),
                   label=f"w={w}", s=40, alpha=0.7)
    ax.plot([0, max(p[2] for p in pts)], [0, max(p[2] for p in pts)],
            "k--", alpha=0.5, label="$y=x$")
    ax.set_xlabel(f"$S({s_metric})$ midpoint step $t_{{mid}}$")
    ax.set_ylabel("Grokking onset $t_{grok}$")
    ax.set_title(f"F3: $t_{{mid}}$ vs $t_{{grok}}$ (each point = one grokking run)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_scaling_collapse(collapse: dict, out_path: Path) -> None:
    pts = collapse["points"]
    if not pts:
        return
    fig, ax = plt.subplots(1, 1, figsize=(7, 5))
    widths = sorted({p["width"] for p in pts})
    cmap = plt.colormaps["viridis"]
    for i, w in enumerate(widths):
        wpts = [p for p in pts if p["width"] == w]
        wpts.sort(key=lambda p: p["x_rescaled"])
        xs = [p["x_rescaled"] for p in wpts]
        ys = [p["grok_rate"] for p in wpts]
        ax.plot(xs, ys, "o-", color=cmap(i / max(1, len(widths) - 1)),
                label=f"w={w}")
    ax.axvline(0, color="k", linestyle=":", alpha=0.5)
    ax.set_xlabel(r"$(n - n_c) \cdot w^{1/\nu}$")
    ax.set_ylabel("grok rate")
    ax.set_title(fr"Finite-size scaling collapse ($\nu={collapse['nu_used']}$)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


# ============================================================================
# Main
# ============================================================================
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", default="results")
    ap.add_argument("--out-dir", default="figures_v2")
    ap.add_argument("--main-json", default="mod47/sweep_add47.json",
                    help="path within results-dir to the main sweep JSON")
    args = ap.parse_args()

    rd = Path(args.results_dir)
    od = Path(args.out_dir); od.mkdir(parents=True, exist_ok=True)
    main_json = rd / args.main_json
    print(f"[analyze] reading {main_json}")
    data = json.loads(main_json.read_text())
    runs = list(data.values())
    print(f"[analyze]   total runs: {len(runs)}; grokked: {sum(r.get('grokked', False) for r in runs)}")

    # --- F3 correlations: try all known S metrics; report only those that exist
    candidate_metrics = (
        "S_W_out", "S_W_in_a", "S_W_in_b", "S_H_class",
        "S_tok_embed",  # transformer
    )
    sample = runs[0] if runs else {}
    actual_metrics = [m for m in candidate_metrics if m in sample]
    f3 = {m: f3_correlation(runs, m) for m in actual_metrics}
    print("[analyze] F3 Pearson correlations (midpoint-based):")
    for k, v in f3.items():
        rmid = v.get("r_midpoint")
        n = v.get("n_midpoint", 0)
        if rmid is None:
            print(f"   {k}: insufficient data (n={n})")
        else:
            p = v.get("p_midpoint", 0)
            print(f"   {k}: r={rmid:.3f}, p={p:.2e}, n={n}")

    # --- n_eff(t) Fisher saturation
    n_eff = fit_n_eff_alignment(runs)
    print(f"[analyze] n_eff(t) (Fisher saturation) alignment: r={n_eff.get('r')}, n={n_eff.get('n')}")

    # --- Critical n_c per width
    nc = critical_nc(runs)
    print(f"[analyze] n_c per width: {nc}")

    # --- F_eff(w) spectral
    spectral = spectral_F_eff(runs)
    print(f"[analyze] F_eff(w) gamma fit: gamma={spectral.get('gamma')}, R^2={spectral.get('r_squared')}")

    # --- beta from scaling
    nc_dict = {w: v["n_c"] for w, v in nc.items() if v.get("n_c")}
    betas = beta_fit(runs, nc_dict)
    print(f"[analyze] beta per width: {betas}")

    # --- Scaling collapse
    collapse = scaling_collapse_data(runs, nc, nu=0.5)
    print(f"[analyze] scaling collapse points: {len(collapse['points'])}")

    # --- Save analysis JSON
    analysis = {
        "f3_correlations": f3,
        "n_eff_alignment": n_eff,
        "n_c_per_width": nc,
        "spectral_F_eff": spectral,
        "beta_per_width": betas,
        "scaling_collapse": collapse,
    }
    (od / "analysis.json").write_text(json.dumps(analysis, indent=2))

    # --- Figures
    plot_n_eff_trajectories(runs, od / "fig7_n_eff.png")
    plot_F_eff(spectral, od / "fig8_F_eff.png")
    plot_S_metrics(runs, od / "fig4_supp_S_metrics.png")
    plot_scaling_collapse(collapse, od / "fig9_scaling_collapse.png")
    plot_f3_scatter(runs, od / "fig4_f3_scatter.png", s_metric="S_W_in_b")
    plot_f3_scatter(runs, od / "fig4b_f3_Hclass.png", s_metric="S_H_class")

    print(f"[analyze] wrote analysis to {od}")


if __name__ == "__main__":
    main()
