"""Generate K=10 sample pools from Qwen3.6-27B (or any LLM) using vLLM,
then compute teacher-forced mean-token-NLL for TECP.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from vllm import LLM, SamplingParams

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils.data import load_dataset_split  # noqa: E402


SYSTEM_PROMPT = (
    "You are a precise question-answering assistant. Answer the question with "
    "the shortest factual response. Do not explain. Output only the answer."
)


def build_prompts(examples, tokenizer) -> List[str]:
    msgs = [
        [{"role": "system", "content": SYSTEM_PROMPT},
         {"role": "user", "content": q.question}]
        for q in examples
    ]
    return [tokenizer.apply_chat_template(m, tokenize=False,
                                           add_generation_prompt=True)
            for m in msgs]


def sample_with_vllm(model: str, prompts: List[str], k: int,
                     max_new_tokens: int, dtype: str,
                     gpu_mem_util: float = 0.85, max_model_len: int = 4096):
    llm = LLM(model=model, dtype=dtype, gpu_memory_utilization=gpu_mem_util,
              max_model_len=max_model_len, trust_remote_code=True)
    params = SamplingParams(n=k, temperature=1.0, top_p=0.95,
                            max_tokens=max_new_tokens, stop=["\n", "</s>"],
                            seed=42)
    outs = llm.generate(prompts, params)
    samples = [[c.text.strip() for c in o.outputs] for o in outs]
    del llm
    torch.cuda.empty_cache()
    return samples


def teacher_nll(model_name: str, prompts: List[str],
                samples_per_prompt: List[List[str]], dtype: str):
    """Mean per-token NLL for each (prompt, sample). dtype must match vllm."""
    tok = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    torch_dtype = torch.bfloat16 if dtype == "bfloat16" else torch.float16
    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch_dtype, device_map="cuda",
        trust_remote_code=True
    )
    model.train(False)
    out = []
    with torch.no_grad():
        for prompt, samples in zip(prompts, samples_per_prompt):
            row = []
            ids_p = tok(prompt, return_tensors="pt").input_ids.to(model.device)
            n_p = ids_p.size(1)
            for s in samples:
                ids_full = tok(prompt + s, return_tensors="pt").input_ids.to(model.device)
                if ids_full.size(1) <= n_p:
                    row.append(0.0); continue
                logits = model(ids_full).logits[0, n_p - 1:-1]
                target = ids_full[0, n_p:]
                nll = torch.nn.functional.cross_entropy(
                    logits, target, reduction="mean"
                )
                row.append(float(nll.item()))
            out.append(row)
    del model
    torch.cuda.empty_cache()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--n_examples", type=int, default=1000)
    ap.add_argument("--k_samples", type=int, default=10)
    ap.add_argument("--max_new_tokens", type=int, default=64)
    ap.add_argument("--model", default="Qwen/Qwen3.6-27B")
    ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument("--output", required=True)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--max_model_len", type=int, default=4096)
    ap.add_argument("--gpu_mem_util", type=float, default=0.88)
    ap.add_argument("--skip_nll", action="store_true",
                    help="Skip teacher-forced NLL pass (TECP gets fallback freq score).")
    args = ap.parse_args()

    examples = load_dataset_split(args.dataset, n=args.n_examples,
                                   seed=args.seed)
    print(f"[gen] {len(examples)} {args.dataset} examples")
    tok = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    prompts = build_prompts(examples, tok)

    print(f"[gen] sampling K={args.k_samples} responses with vLLM ...")
    samples = sample_with_vllm(args.model, prompts, args.k_samples,
                                args.max_new_tokens, args.dtype,
                                args.gpu_mem_util, args.max_model_len)

    if args.skip_nll:
        nlls = [[0.0] * len(s) for s in samples]
        print("[gen] skipped NLL pass")
    else:
        print("[gen] computing teacher-forced NLL ...")
        nlls = teacher_nll(args.model, prompts, samples, args.dtype)

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    records = []
    for ex, ss, nn in zip(examples, samples, nlls):
        records.append({"qid": ex.id, "question": ex.question,
                        "answers": ex.answers, "samples": ss,
                        "mean_token_nll": nn, "dataset": ex.dataset})
    with open(args.output, "w") as f:
        json.dump(records, f)
    print(f"[gen] wrote {len(records)} records -> {args.output}")


if __name__ == "__main__":
    main()
