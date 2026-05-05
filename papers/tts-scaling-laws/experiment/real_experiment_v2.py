#!/usr/bin/env python3
"""STAIR V2 real-LLM experiment driver.

Replaces V1's `real_experiment.py` (which hardcoded N_PROBLEMS=40 / S=4 while
the paper claimed 100/8 — Reproducibility Archeologist W1).

Backends supported (in order of preference):
  1. Ollama HTTP API at http://127.0.0.1:11434 (local; default for canary).
  2. OpenRouter HTTP API at https://openrouter.ai/api/v1 (cloud; fallback).

Models supported (all served as `provider:model_id` via Ollama or OpenRouter):
  - qwen3:4b              (Ollama or OpenRouter `qwen/qwen3-4b`)
  - qwen3:8b              (Ollama or OpenRouter `qwen/qwen3-8b`)
  - qwen3:14b             (Ollama or OpenRouter `qwen/qwen3-14b`)
  - qwen3.6:35b-a3b       (Ollama or OpenRouter `qwen/qwen3.6-35b-a3b`)
  - llama4:scout          (OpenRouter `meta-llama/llama-4-scout`)

Outputs:
  real_results_v3/
    results_<MODEL>.npy        # shape (n_problems, n_budgets, n_temps, n_samples)
    results_<MODEL>_meta.json  # config, timings, gzip overhead, p50/p95/p99
    accuracy_<MODEL>.npy       # shape (n_problems, n_budgets, n_temps), means
    successes_<MODEL>.npy      # shape (n_problems, n_budgets, n_temps), counts

Reviewer-mapping:
  T0.2  S sensitivity (8/16/32) -- run with --samples-per-cell={8,16,32}
  T0.4  Larger model (>30% accuracy) -- pick a model that crosses that threshold
  T0.9  Reproducibility patch -- this script reproduces every reported number
  T1.2  MATH-500 cross-domain -- pass --dataset math500
  T1.3  Cross-architecture -- pass --model llama4:scout
  T1.5  p99 latency -- collected automatically
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np

REPO = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO / "real_results_v3"

# Defaults aligned with V2 checklist (REVISION_V2_CHECKLIST.md §4.3)
DEFAULT_BUDGETS = (32, 64, 128, 256, 512, 1024, 2048)
DEFAULT_TEMPS = (0.1, 0.5, 1.0)
DEFAULT_SAMPLES = 16
DEFAULT_N_PROBLEMS = 100


def load_env() -> dict:
    env_path = REPO / ".env"
    out = {}
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                out[k.strip()] = v.strip()
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Datasets
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class Problem:
    pid: int
    question: str
    gold_answer: str
    step_count: int
    gzip_len: int


def parse_gsm8k_answer(text: str) -> str:
    m = re.search(r"####\s*(-?[\d,]+)", text)
    return m.group(1).replace(",", "") if m else ""


def parse_math500_answer(text: str) -> str:
    """MATH-500 answers are wrapped in \\boxed{...}. Extract."""
    m = re.search(r"\\boxed\{([^{}]+)\}", text)
    return m.group(1).strip() if m else text.strip()


def load_dataset(name: str, n: int) -> list[Problem]:
    """Load `n` problems from the named dataset. Lazy import datasets lib."""
    from datasets import load_dataset as _load
    if name == "gsm8k":
        ds = _load("openai/gsm8k", "main", split=f"test[:{n}]")
        out = []
        for i, row in enumerate(ds):
            out.append(Problem(
                pid=i,
                question=row["question"],
                gold_answer=parse_gsm8k_answer(row["answer"]),
                step_count=row["answer"].count("\n") + 1,
                gzip_len=len(gzip.compress(row["question"].encode(), compresslevel=9)),
            ))
        return out
    elif name == "math500":
        ds = _load("HuggingFaceH4/MATH-500", split=f"test[:{n}]")
        out = []
        for i, row in enumerate(ds):
            out.append(Problem(
                pid=i,
                question=row["problem"],
                gold_answer=parse_math500_answer(row["answer"]),
                step_count=row.get("solution", "").count("\n") + 1,
                gzip_len=len(gzip.compress(row["problem"].encode(), compresslevel=9)),
            ))
        return out
    else:
        raise ValueError(f"unknown dataset {name}")


# ─────────────────────────────────────────────────────────────────────────────
# Backends
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class GenerationResult:
    text: str
    latency_ms: float


class Backend:
    name: str

    def generate(self, prompt: str, max_tokens: int, temperature: float, seed: int) -> GenerationResult:
        raise NotImplementedError


class OllamaBackend(Backend):
    """Local Ollama HTTP API. Free, deterministic with seed."""

    def __init__(self, model: str, host: str = "http://127.0.0.1:11434"):
        import requests  # lazy import
        self.requests = requests
        self.model = model
        self.host = host.rstrip("/")
        self.name = f"ollama:{model}"

    def generate(self, prompt: str, max_tokens: int, temperature: float, seed: int) -> GenerationResult:
        t0 = time.time()
        # Use /api/chat (applies chat template) with think:false (disable Qwen3
        # extended-thinking mode that otherwise consumes the entire token budget
        # before any answer is emitted). Falls back gracefully on models that
        # don't support thinking mode -- the `think` flag is ignored.
        r = self.requests.post(
            f"{self.host}/api/chat",
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "think": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature,
                    "seed": seed,
                    "num_ctx": 4096,
                },
            },
            timeout=600,
        )
        r.raise_for_status()
        dt = (time.time() - t0) * 1000.0
        body = r.json()
        text = (body.get("message") or {}).get("content", "") or body.get("response", "")
        return GenerationResult(text=text, latency_ms=dt)


class OpenRouterBackend(Backend):
    """Cloud OpenRouter HTTP API. Fallback when local can't fit the model."""

    MODEL_MAP = {
        "qwen3:4b": "qwen/qwen3-4b",
        "qwen3:8b": "qwen/qwen3-8b",
        "qwen3:14b": "qwen/qwen3-14b",
        "qwen3.6:35b-a3b": "qwen/qwen3.6-35b-a3b",
        "llama4:scout": "meta-llama/llama-4-scout",
        "llama4:maverick": "meta-llama/llama-4-maverick",
    }

    def __init__(self, model: str, api_key: str):
        import requests
        self.requests = requests
        self.model = self.MODEL_MAP.get(model, model)
        self.api_key = api_key
        self.name = f"openrouter:{self.model}"
        self.url = "https://openrouter.ai/api/v1/chat/completions"

    def generate(self, prompt: str, max_tokens: int, temperature: float, seed: int) -> GenerationResult:
        t0 = time.time()
        # `reasoning.exclude=True` asks OpenRouter to suppress thinking-mode
        # tokens in the response (Qwen3 / DeepSeek-R1 behavior). Saves budget
        # for the actual answer. If a model ignores it, we still recover by
        # falling back to the `reasoning` field when `content` is null.
        r = self.requests.post(
            self.url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "seed": seed,
                "reasoning": {"exclude": True},
            },
            timeout=600,
        )
        r.raise_for_status()
        dt = (time.time() - t0) * 1000.0
        body = r.json()
        msg = body.get("choices", [{}])[0].get("message", {}) or {}
        text = msg.get("content")
        if not text:
            # Some models still emit thinking tokens despite reasoning.exclude;
            # parse them out of the `reasoning` field if present.
            text = msg.get("reasoning") or ""
        return GenerationResult(text=text or "", latency_ms=dt)


def make_backend(model: str, env: dict) -> Backend:
    """Choose Ollama if model is locally pulled; else OpenRouter."""
    import requests
    try:
        r = requests.get(f"{env.get('OLLAMA_HOST', 'http://127.0.0.1:11434')}/api/tags", timeout=2)
        local = [m["name"] for m in r.json().get("models", [])]
        if model in local or model.replace(":latest", "") in local:
            return OllamaBackend(model=model, host=env.get("OLLAMA_HOST", "http://127.0.0.1:11434"))
    except Exception:
        pass
    api_key = env.get("OPENROUTER_API_KEY") or os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        raise RuntimeError(f"model {model!r} not available locally and no OPENROUTER_API_KEY in .env")
    return OpenRouterBackend(model=model, api_key=api_key)


# ─────────────────────────────────────────────────────────────────────────────
# Answer extraction & scoring
# ─────────────────────────────────────────────────────────────────────────────


_NUM_RE = re.compile(r"-?\d[\d,]*(?:\.\d+)?")


def extract_final_number(text: str) -> str:
    """Generic numeric-answer extractor with priority for #### and \\boxed."""
    m = re.search(r"####\s*(-?[\d,]+(?:\.\d+)?)", text)
    if m:
        return m.group(1).replace(",", "")
    m = re.search(r"\\boxed\{([^{}]+)\}", text)
    if m:
        candidate = m.group(1).strip()
        m2 = _NUM_RE.search(candidate)
        if m2:
            return m2.group(0).replace(",", "")
        return candidate
    nums = _NUM_RE.findall(text)
    return nums[-1].replace(",", "") if nums else ""


def is_correct(pred: str, gold: str) -> bool:
    if not pred or not gold:
        return False
    try:
        return abs(float(pred) - float(gold)) < 1e-6
    except ValueError:
        return pred.strip() == gold.strip()


# ─────────────────────────────────────────────────────────────────────────────
# Prompt builder
# ─────────────────────────────────────────────────────────────────────────────


PROMPT_TEMPLATE_GSM8K = (
    "Solve this math problem step by step. End your answer with '#### <number>'.\n\n"
    "Problem: {question}\n\nSolution:"
)

PROMPT_TEMPLATE_MATH = (
    "Solve this problem step by step. Put your final answer in \\boxed{{}}.\n\n"
    "Problem: {question}\n\nSolution:"
)


def build_prompt(problem: Problem, dataset: str) -> str:
    template = PROMPT_TEMPLATE_GSM8K if dataset == "gsm8k" else PROMPT_TEMPLATE_MATH
    return template.format(question=problem.question)


# ─────────────────────────────────────────────────────────────────────────────
# Main loop
# ─────────────────────────────────────────────────────────────────────────────


def run(
    model: str,
    dataset: str = "gsm8k",
    n_problems: int = DEFAULT_N_PROBLEMS,
    budgets: tuple[int, ...] = DEFAULT_BUDGETS,
    temperatures: tuple[float, ...] = DEFAULT_TEMPS,
    samples_per_cell: int = DEFAULT_SAMPLES,
    out_dir: Path = DEFAULT_OUT,
    seed_base: int = 42,
    progress_every: int = 25,
    concurrency: int = 1,
):
    env = load_env()
    backend = make_backend(model, env)
    problems = load_dataset(dataset, n_problems)
    out_dir.mkdir(exist_ok=True, parents=True)

    safe_name = model.replace("/", "_").replace(":", "_")
    out_npy = out_dir / f"results_{safe_name}_{dataset}.npy"
    out_meta = out_dir / f"results_{safe_name}_{dataset}_meta.json"
    out_acc = out_dir / f"accuracy_{safe_name}_{dataset}.npy"
    out_k = out_dir / f"successes_{safe_name}_{dataset}.npy"

    n_b, n_t, n_s = len(budgets), len(temperatures), samples_per_cell
    correct = np.zeros((n_problems, n_b, n_t, n_s), dtype=np.int8)
    completed_mask = np.zeros((n_problems, n_b, n_t, n_s), dtype=bool)
    accuracy = np.zeros((n_problems, n_b, n_t), dtype=np.float64)
    successes = np.zeros((n_problems, n_b, n_t), dtype=np.int64)
    latencies_ms: list[float] = []
    gzip_overhead_ms: list[float] = []

    # ── Resume from checkpoint if present
    ckpt_npy = out_npy.with_suffix(".ckpt.npy")
    ckpt_mask = out_npy.with_suffix(".ckpt_mask.npy")
    if ckpt_npy.exists() and ckpt_mask.exists():
        prev = np.load(ckpt_npy)
        prev_mask = np.load(ckpt_mask)
        if prev.shape == correct.shape and prev_mask.shape == completed_mask.shape:
            correct[:] = prev
            completed_mask[:] = prev_mask
            print(f"  [exp_v2] resumed from checkpoint: {int(prev_mask.sum())} cells already complete",
                  flush=True)

    total_calls = n_problems * n_b * n_t * n_s
    completed = 0
    t_start = time.time()
    print(f"[exp_v2] backend={backend.name} dataset={dataset} n={n_problems} "
          f"budgets={budgets} temps={temperatures} S={samples_per_cell} "
          f"total_calls={total_calls}", flush=True)

    # Build the task list, skipping cells already completed in a previous run.
    tasks = []  # (pi, bi, ti, si, prompt, budget, temp, seed, gold_answer)
    for pi, problem in enumerate(problems):
        t0 = time.time()
        _ = len(gzip.compress(problem.question.encode(), compresslevel=9))
        gzip_overhead_ms.append((time.time() - t0) * 1000.0)
        prompt = build_prompt(problem, dataset)
        for bi, budget in enumerate(budgets):
            for ti, temp in enumerate(temperatures):
                for si in range(n_s):
                    if completed_mask[pi, bi, ti, si]:
                        completed += 1  # count toward total but skip
                        continue
                    seed = seed_base + pi * 1000 + bi * 100 + ti * 10 + si
                    tasks.append((pi, bi, ti, si, prompt, budget, temp, seed, problem.gold_answer))
    if completed > 0:
        print(f"  [exp_v2] skipping {completed} already-completed cells", flush=True)

    def _one(task):
        pi, bi, ti, si, prompt, budget, temp, seed, gold = task
        try:
            r = backend.generate(prompt, max_tokens=budget, temperature=temp, seed=seed)
            text = r.text or ""
            pred = extract_final_number(text)
            ok = is_correct(pred, gold)
            return (pi, bi, ti, si, int(ok), r.latency_ms, None)
        except Exception as e:
            return (pi, bi, ti, si, 0, 0.0, str(e))

    # ── Run inference, checkpointing every CHECKPOINT_EVERY successful cells.
    CHECKPOINT_EVERY = 100
    consecutive_errors = 0
    MAX_CONSECUTIVE_ERRORS = 50  # bail out fast on rate-limit / quota hits

    def _record(pi, bi, ti, si, ok, lat_ms, err):
        nonlocal consecutive_errors
        if err:
            consecutive_errors += 1
        else:
            consecutive_errors = 0
            latencies_ms.append(lat_ms)
        correct[pi, bi, ti, si] = ok
        completed_mask[pi, bi, ti, si] = (err is None)

    def _checkpoint():
        np.save(ckpt_npy, correct)
        np.save(ckpt_mask, completed_mask)

    if concurrency <= 1:
        for task in tasks:
            pi, bi, ti, si, ok, lat_ms, err = _one(task)
            if err:
                print(f"  ERR pi={pi} bi={bi} ti={ti} si={si}: {err}", flush=True)
            _record(pi, bi, ti, si, ok, lat_ms, err)
            completed += 1
            if completed % CHECKPOINT_EVERY == 0:
                _checkpoint()
            if completed % progress_every == 0:
                elapsed = time.time() - t_start
                rate = completed / max(elapsed, 1e-3)
                eta = (total_calls - completed) / max(rate, 1e-3)
                print(f"  [{completed}/{total_calls}] elapsed={elapsed:.0f}s rate={rate:.1f}/s "
                      f"eta={eta:.0f}s acc={correct.sum() / max(completed,1):.3f}", flush=True)
            if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                print(f"  [exp_v2] aborting: {consecutive_errors} consecutive errors "
                      f"(rate-limit / quota? checkpoint saved at {int(completed_mask.sum())} cells)",
                      flush=True)
                _checkpoint()
                break
    else:
        with ThreadPoolExecutor(max_workers=concurrency) as ex:
            futures = [ex.submit(_one, t) for t in tasks]
            for f in as_completed(futures):
                pi, bi, ti, si, ok, lat_ms, err = f.result()
                if err:
                    print(f"  ERR pi={pi} bi={bi} ti={ti} si={si}: {err}", flush=True)
                _record(pi, bi, ti, si, ok, lat_ms, err)
                completed += 1
                if completed % CHECKPOINT_EVERY == 0:
                    _checkpoint()
                if completed % progress_every == 0:
                    elapsed = time.time() - t_start
                    rate = completed / max(elapsed, 1e-3)
                    eta = (total_calls - completed) / max(rate, 1e-3)
                    print(f"  [{completed}/{total_calls}] elapsed={elapsed:.0f}s rate={rate:.1f}/s "
                          f"eta={eta:.0f}s acc={correct.sum() / max(completed,1):.3f}", flush=True)
                if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                    print(f"  [exp_v2] aborting: {consecutive_errors} consecutive errors. "
                          f"Checkpoint saved at {int(completed_mask.sum())} cells.", flush=True)
                    _checkpoint()
                    for fut in futures:
                        fut.cancel()
                    break
    # Always save a final checkpoint at end, even if we aborted
    _checkpoint()

    # Aggregate
    successes[:] = correct.sum(axis=-1)
    accuracy[:] = successes / max(n_s, 1)
    np.save(out_npy, correct)
    np.save(out_acc, accuracy)
    np.save(out_k, successes)

    # Latency stats
    if latencies_ms:
        lat = np.asarray(latencies_ms)
        meta_lat = {
            "mean_ms": float(lat.mean()),
            "median_ms": float(np.median(lat)),
            "p95_ms": float(np.percentile(lat, 95)),
            "p99_ms": float(np.percentile(lat, 99)),
            "max_ms": float(lat.max()),
            "n": int(len(lat)),
        }
    else:
        meta_lat = {}
    if gzip_overhead_ms:
        gz = np.asarray(gzip_overhead_ms)
        meta_gz = {
            "mean_ms": float(gz.mean()),
            "median_ms": float(np.median(gz)),
            "p95_ms": float(np.percentile(gz, 95)),
            "p99_ms": float(np.percentile(gz, 99)),
            "max_ms": float(gz.max()),
            "n": int(len(gz)),
        }
    else:
        meta_gz = {}
    elapsed_total = time.time() - t_start
    meta = {
        "model": model,
        "backend": backend.name,
        "dataset": dataset,
        "n_problems": int(n_problems),
        "budgets": list(budgets),
        "temperatures": list(temperatures),
        "samples_per_cell": int(samples_per_cell),
        "total_calls": int(total_calls),
        "elapsed_seconds": float(elapsed_total),
        "calls_per_second": float(total_calls / max(elapsed_total, 1e-3)),
        "overall_accuracy": float(accuracy.mean()),
        "latency_ms": meta_lat,
        "gzip_overhead_ms": meta_gz,
        "produced_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "seed_base": int(seed_base),
    }
    out_meta.write_text(json.dumps(meta, indent=2))
    print(f"[exp_v2] done. acc={accuracy.mean():.3f} elapsed={elapsed_total:.0f}s "
          f"-> {out_npy}", flush=True)
    print(f"  meta -> {out_meta}", flush=True)
    return meta


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--dataset", default="gsm8k", choices=["gsm8k", "math500"])
    p.add_argument("--n-problems", type=int, default=DEFAULT_N_PROBLEMS)
    p.add_argument("--budgets", type=int, nargs="+", default=list(DEFAULT_BUDGETS))
    p.add_argument("--temperatures", type=float, nargs="+", default=list(DEFAULT_TEMPS))
    p.add_argument("--samples-per-cell", type=int, default=DEFAULT_SAMPLES)
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p.add_argument("--seed-base", type=int, default=42)
    p.add_argument("--concurrency", type=int, default=1,
                   help="Number of parallel inference requests (use 8-16 for OpenRouter)")
    args = p.parse_args()
    run(
        model=args.model,
        dataset=args.dataset,
        n_problems=args.n_problems,
        budgets=tuple(args.budgets),
        temperatures=tuple(args.temperatures),
        samples_per_cell=args.samples_per_cell,
        out_dir=args.out,
        seed_base=args.seed_base,
        concurrency=args.concurrency,
    )


if __name__ == "__main__":
    main()
