"""Build NLI-partitioned + multi-granularity sample pools (v2).

Key v2 changes vs build_pools.py:
  1. NLI: DeBERTa-v3-large-mnli-fever-anli-ling-wanli (SOTA on HF Hub)
  2. Embedder: gte-Qwen2-7B-instruct primary, mxbai-embed-large-v1 sensitivity
  3. HAC-NLI partitioner with embedding prefilter (O(K log K) instead of O(K^2))
  4. Multi-granularity partitions stored at strict / medium / lenient
     thresholds for M-SemCP method
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import torch
from sentence_transformers import SentenceTransformer

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[0]))

from utils.correctness import is_correct  # noqa: E402
from partition_v2 import HACNLIPartitioner, HACNLIConfig  # noqa: E402

DEFAULT_NLI = "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli"
DEFAULT_EMB = "Alibaba-NLP/gte-Qwen2-7B-instruct"
GRAIN_TAUS = {"strict": 0.70, "medium": 0.50, "lenient": 0.30}


def save_pools(pools_meta, embeddings_per_pool, out_base: str):
    os.makedirs(os.path.dirname(out_base) or ".", exist_ok=True)
    with open(out_base + ".json", "w") as f:
        json.dump(pools_meta, f)
    np.savez_compressed(
        out_base + ".npz",
        **{f"emb_{i}": e for i, e in enumerate(embeddings_per_pool)}
    )
    print(f"[build] wrote {len(pools_meta)} pools -> {out_base}.json + .npz")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output_base", required=True)
    ap.add_argument("--nli_model", default=DEFAULT_NLI)
    ap.add_argument("--embed_model", default=DEFAULT_EMB)
    ap.add_argument("--max_pools", type=int, default=0,
                    help="Subset for smoke testing; 0 = use all.")
    ap.add_argument("--no_multi_grain", action="store_true",
                    help="Skip multi-granularity (just write the medium grain).")
    args = ap.parse_args()

    with open(args.input) as f:
        records = json.load(f)
    if args.max_pools and args.max_pools < len(records):
        records = records[: args.max_pools]
    print(f"[build] {len(records)} records from {args.input}")

    print(f"[build] loading embedder: {args.embed_model}")
    # gte-Qwen2-7B is large; we set max_seq_length=512 for speed.
    embedder = SentenceTransformer(args.embed_model, device="cuda",
                                   trust_remote_code=True)
    embedder.max_seq_length = 512

    print(f"[build] embedding samples for prefilter (used by HAC-NLI)")
    # Pre-embed every sample once
    all_embs = []
    for rec in records:
        e = embedder.encode(rec["samples"], convert_to_numpy=True,
                            normalize_embeddings=False, show_progress_bar=False)
        all_embs.append(e.astype(np.float32))

    # Build per-granularity partitioners (sharing the same HF model in memory)
    grains = list(GRAIN_TAUS.keys())
    if args.no_multi_grain:
        grains = ["medium"]
    print(f"[build] loading NLI partitioner: {args.nli_model}")
    cfg_med = HACNLIConfig(nli_model_name=args.nli_model,
                            tau_entail=GRAIN_TAUS["medium"])
    partitioner = HACNLIPartitioner(cfg_med, device="cuda")
    cfg_per_grain = {g: HACNLIConfig(nli_model_name=args.nli_model,
                                       tau_entail=GRAIN_TAUS[g])
                     for g in grains}

    pools_meta = []
    for i, (rec, embs) in enumerate(zip(records, all_embs)):
        if (i + 1) % 50 == 0:
            print(f"[build] partitioning {i + 1}/{len(records)}")
        samples = rec["samples"]
        refs = rec["answers"]
        sample_correct = [is_correct(s, refs, "exact_match") for s in samples]

        cluster_ids_by_grain: dict[str, list[int]] = {}
        for grain in grains:
            partitioner.cfg = cfg_per_grain[grain]
            cluster_ids_by_grain[grain] = partitioner.partition(
                samples, embeddings=embs
            )

        # Use medium-grain as canonical
        canonical_ids = cluster_ids_by_grain["medium"]
        n_clusters = max(canonical_ids) + 1 if canonical_ids else 0
        cluster_correct = [False] * n_clusters
        cluster_reps = [""] * n_clusters
        for s_idx, c_idx in enumerate(canonical_ids):
            if sample_correct[s_idx]:
                cluster_correct[c_idx] = True
            if not cluster_reps[c_idx]:
                cluster_reps[c_idx] = samples[s_idx]

        pools_meta.append({
            "qid": rec["qid"],
            "question": rec["question"],
            "samples": samples,
            "references": refs,
            "sample_correct": sample_correct,
            "cluster_ids": canonical_ids,
            "cluster_correct": cluster_correct,
            "cluster_reps": cluster_reps,
            "extra": {
                "mean_token_nll": rec.get("mean_token_nll", []),
                "dataset": rec.get("dataset", ""),
                "cluster_ids_by_grain": cluster_ids_by_grain,
            },
        })

    save_pools(pools_meta, all_embs, args.output_base)

    n = len(pools_meta)
    admissible = sum(1 for p in pools_meta if any(p["cluster_correct"]))
    avg_clusters = np.mean([len(set(p["cluster_ids"])) for p in pools_meta])
    avg_em = np.mean([sum(p["sample_correct"]) / len(p["samples"])
                       for p in pools_meta])
    print(f"[build] admissible: {admissible}/{n} ({admissible/n:.1%})")
    print(f"[build] avg clusters per question: {avg_clusters:.2f}")
    print(f"[build] avg per-sample EM correct:  {avg_em:.1%}")


if __name__ == "__main__":
    main()
