"""LLM-judge inter-rater agreement on cluster equivalence labels.

Council issue #2: human kappa study on cluster equivalence is the gold
standard. We provide an LLM-judge proxy: two independent LLM judges
classify (within-cluster, between-cluster) pairs as semantically
equivalent or not, and we compute Cohen's kappa across:
  - judge1 vs judge2  (inter-judge agreement)
  - judge1 vs partition  (judge1 vs cosine-cluster ground-proxy)
  - judge2 vs partition

Judges:
  J1 = MiniMax-M2  (native API, terse rule-based prompt)
  J2 = MiniMax-M2.7 via anthropic endpoint (different model version,
       different prompting persona)

Reads:  artifacts/v2_data/{triviaqa,squad,nq_open}_raw.json
Writes: artifacts/v2_revision/llm_judge_kappa.{json,md}

This is HONESTLY a SUBSTITUTE for the human kappa requested by the
council, framed as inter-LLM-judge kappa with the partition as a third
rater. It does not replace human evaluation but provides an
independent signal that the cosine-cluster partition labels are
recoverable by strong LLMs in agreement.
"""
from __future__ import annotations

import json
import os
import random
import time
import urllib.request
from pathlib import Path
from typing import List, Tuple

import numpy as np
from scipy import stats

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "artifacts/v2_data"
OUT_JSON = REPO / "artifacts/v2_revision/llm_judge_kappa.json"
OUT_MD = REPO / "artifacts/v2_revision/llm_judge_kappa.md"

DATASETS = ["triviaqa", "squad", "nq_open"]
N_PAIRS_PER_DS = int(os.environ.get("LLMJUDGE_N_PAIRS", "33"))
TAU_COS = float(os.environ.get("LLMJUDGE_TAU_COS", "0.85"))
SEED = int(os.environ.get("LLMJUDGE_SEED", "2026"))
N_POOLS_PER_DS = int(os.environ.get("LLMJUDGE_N_POOLS", "50"))

OLLAMA_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "mxbai-embed-large"
MINIMAX_KEY = os.environ.get("MINIMAX_API_KEY", "")
MINIMAX_URL = "https://api.minimax.io/v1/text/chatcompletion_v2"
ANTHROPIC_URL = "https://api.minimax.io/anthropic/v1/messages"

J1_NAME = "MiniMax-M2 (rigorous logic persona)"
J2_NAME = "MiniMax-M2.7 (commonsense persona)"

PROMPT_J1 = (
    "You are a strict logical equivalence checker for QA answers.\n"
    "Question: {q}\nCandidate A: {a}\nCandidate B: {b}\n\n"
    "Decide whether A and B refer to the same entity, fact, or quantity "
    "in any reasonable reading. Surface paraphrases of the same meaning "
    "are EQUIVALENT. Different entities or contradicting facts are "
    "DIFFERENT.\n\n"
    "REQUIRED: The very FIRST line of your reply must be exactly one of "
    "the two tokens: `EQUIVALENT` or `DIFFERENT`. Then you may explain."
)
PROMPT_J2 = (
    "Question: {q}\nAnswer A: {a}\nAnswer B: {b}\n\n"
    "As an everyday knowledgeable reader, would a typical user accept "
    "these two answers as conveying the same information for the "
    "question?\n\n"
    "REQUIRED: The very FIRST line of your reply must be exactly one of "
    "the two tokens: `EQUIVALENT` or `DIFFERENT`. Then you may explain."
)


def ollama_embed(text: str) -> np.ndarray:
    body = json.dumps({"model": EMBED_MODEL, "prompt": text}).encode()
    req = urllib.request.Request(OLLAMA_URL, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.loads(r.read())
    return np.array(d["embedding"], dtype=np.float32)


def cluster_cosine(emb: np.ndarray, tau: float) -> List[int]:
    K = emb.shape[0]
    if K == 0:
        return []
    norm = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-12)
    sim = norm @ norm.T
    parent = list(range(K))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb: parent[ra] = rb
    for i in range(K):
        for j in range(i + 1, K):
            if sim[i, j] >= tau:
                union(i, j)
    root2cid = {}
    cids = []
    for i in range(K):
        r = find(i)
        if r not in root2cid:
            root2cid[r] = len(root2cid)
        cids.append(root2cid[r])
    return cids


def call_minimax_m2(prompt: str, retries: int = 3) -> str:
    body = json.dumps({
        "model": "MiniMax-M2",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1024,
        "temperature": 0.0,
    }).encode()
    req = urllib.request.Request(
        MINIMAX_URL, data=body,
        headers={"Authorization": f"Bearer {MINIMAX_KEY}",
                 "Content-Type": "application/json"})
    for k in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                d = json.loads(r.read())
            msg = d["choices"][0]["message"]
            content = msg.get("content") or ""
            if not content.strip():
                # Fallback: scan reasoning_content for answer if main content empty.
                rc = msg.get("reasoning_content") or ""
                content = rc
            return content
        except Exception as e:
            if k == retries - 1:
                raise
            time.sleep(1 + k)
    return ""


def call_anthropic_endpoint(prompt: str, retries: int = 3) -> str:
    body = json.dumps({
        "model": "claude-sonnet-4-5",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()
    req = urllib.request.Request(
        ANTHROPIC_URL, data=body,
        headers={"x-api-key": MINIMAX_KEY,
                 "anthropic-version": "2023-06-01",
                 "Content-Type": "application/json"})
    for k in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                d = json.loads(r.read())
            chunks = d.get("content", [])
            text = "".join(c.get("text", "") for c in chunks if c.get("type") == "text")
            return text
        except Exception as e:
            if k == retries - 1:
                raise
            time.sleep(1 + k)
    return ""


def parse_label(text: str) -> int:
    """Return 1 if EQUIVALENT, 0 if DIFFERENT, -1 if unparseable.
    Prefer the FIRST occurrence of either token (so the answer-first
    instruction is honored even if explanation contains both words).
    """
    t = (text or "").upper()
    i_eq = t.find("EQUIVALENT")
    i_df = t.find("DIFFERENT")
    if i_eq < 0 and i_df < 0:
        return -1
    if i_eq < 0:
        return 0
    if i_df < 0:
        return 1
    return 1 if i_eq < i_df else 0


def cohen_kappa(a: List[int], b: List[int]) -> float:
    a = np.array(a); b = np.array(b)
    mask = (a >= 0) & (b >= 0)
    a = a[mask]; b = b[mask]
    if len(a) == 0:
        return float("nan")
    return float(stats.cohen_kappa_score(a, b)) if hasattr(stats, "cohen_kappa_score") else float("nan")


def cohen_kappa_safe(a: List[int], b: List[int]) -> Tuple[float, int]:
    """Returns (kappa, n_used). Hand-rolled to avoid sklearn dep."""
    a_arr = np.array(a); b_arr = np.array(b)
    mask = (a_arr >= 0) & (b_arr >= 0)
    a_arr = a_arr[mask]; b_arr = b_arr[mask]
    n = len(a_arr)
    if n == 0:
        return float("nan"), 0
    obs = float((a_arr == b_arr).mean())
    p_a1 = float((a_arr == 1).mean())
    p_b1 = float((b_arr == 1).mean())
    p_a0 = 1.0 - p_a1; p_b0 = 1.0 - p_b1
    expected = p_a1 * p_b1 + p_a0 * p_b0
    if expected >= 1.0:
        return float("nan"), n
    return float((obs - expected) / (1.0 - expected)), n


def sample_pairs(rec_list: List[dict], n_pools: int, n_pairs: int,
                 rng: random.Random) -> List[Tuple[str, str, str, int, int]]:
    """Returns list of (qid, question, sample_a, sample_b, label).
    label = 1 within-cluster (cosine partition says equivalent), 0 between.
    """
    out: List[Tuple[str, str, str, str, int]] = []
    indices = rng.sample(range(len(rec_list)), min(n_pools, len(rec_list)))
    cluster_inventory: List[Tuple[str, str, str, str, int]] = []
    for k in indices:
        rec = rec_list[k]
        samples = rec.get("samples", [])
        if len(samples) < 2:
            continue
        try:
            emb = np.stack([ollama_embed(s) for s in samples])
        except Exception:
            continue
        cids = cluster_cosine(emb, TAU_COS)
        if not cids:
            continue
        # Build candidate within and between pairs
        K = len(samples)
        within: List[Tuple[int, int]] = []
        between: List[Tuple[int, int]] = []
        for i in range(K):
            for j in range(i + 1, K):
                if samples[i] == samples[j]:
                    continue  # exact duplicates uninformative
                if cids[i] == cids[j]:
                    within.append((i, j))
                else:
                    between.append((i, j))
        for (i, j) in within[:1]:  # 1 within-pair per pool max
            cluster_inventory.append((rec["qid"], rec["question"],
                                      samples[i], samples[j], 1))
        for (i, j) in between[:1]:
            cluster_inventory.append((rec["qid"], rec["question"],
                                      samples[i], samples[j], 0))
    # Balance and shuffle
    pos = [x for x in cluster_inventory if x[4] == 1]
    neg = [x for x in cluster_inventory if x[4] == 0]
    rng.shuffle(pos); rng.shuffle(neg)
    take = min(n_pairs // 2, len(pos), len(neg))
    out = pos[:take] + neg[:take]
    rng.shuffle(out)
    return out


def main() -> None:
    if not MINIMAX_KEY:
        raise SystemExit("MINIMAX_API_KEY not set")
    rng = random.Random(SEED)

    all_pairs = []
    for ds in DATASETS:
        rec_list = json.load(open(DATA / f"{ds}_raw.json"))
        print(f"[{ds}] sampling pairs from {len(rec_list)} records...", flush=True)
        pairs = sample_pairs(rec_list, N_POOLS_PER_DS, N_PAIRS_PER_DS, rng)
        print(f"[{ds}] got {len(pairs)} balanced pairs "
              f"({sum(1 for p in pairs if p[4]==1)} within, "
              f"{sum(1 for p in pairs if p[4]==0)} between)", flush=True)
        for q in pairs:
            all_pairs.append((ds, *q))

    # Shuffle so judges see datasets interleaved
    rng.shuffle(all_pairs)

    rows = []
    j1_labels, j2_labels, partition_labels = [], [], []
    t0 = time.time()
    for k, (ds, qid, q, a, b, lab) in enumerate(all_pairs):
        p1 = PROMPT_J1.format(q=q, a=a, b=b)
        p2 = PROMPT_J2.format(q=q, a=a, b=b)
        try:
            r1 = call_minimax_m2(p1)
        except Exception as e:
            r1 = f"ERROR {e}"
        try:
            r2 = call_anthropic_endpoint(p2)
        except Exception as e:
            r2 = f"ERROR {e}"
        l1 = parse_label(r1); l2 = parse_label(r2)
        j1_labels.append(l1); j2_labels.append(l2); partition_labels.append(lab)
        rows.append({"dataset": ds, "qid": qid, "question": q,
                     "answer_a": a, "answer_b": b,
                     "partition_label": lab,
                     "j1_text": (r1[:120] if r1 else ""),
                     "j2_text": (r2[:120] if r2 else ""),
                     "j1_label": l1, "j2_label": l2})
        if (k + 1) % 10 == 0 or k == 0:
            print(f"  {k+1}/{len(all_pairs)} pairs in {time.time()-t0:.1f}s "
                  f"(j1 unparseable: {j1_labels.count(-1)}, "
                  f"j2 unparseable: {j2_labels.count(-1)})", flush=True)

    k_inter, n_inter = cohen_kappa_safe(j1_labels, j2_labels)
    k_j1_part, n_j1p = cohen_kappa_safe(j1_labels, partition_labels)
    k_j2_part, n_j2p = cohen_kappa_safe(j2_labels, partition_labels)

    out = {
        "n_pairs_total": len(all_pairs),
        "tau_cos_partition": TAU_COS,
        "judge1": J1_NAME,
        "judge2": J2_NAME,
        "embed_model": EMBED_MODEL,
        "n_pools_per_dataset": N_POOLS_PER_DS,
        "n_pairs_per_dataset": N_PAIRS_PER_DS,
        "kappa": {
            "judge1_vs_judge2": {"value": k_inter, "n": n_inter},
            "judge1_vs_partition": {"value": k_j1_part, "n": n_j1p},
            "judge2_vs_partition": {"value": k_j2_part, "n": n_j2p},
        },
        "rate_unparseable": {
            "judge1": float(j1_labels.count(-1) / len(j1_labels)) if j1_labels else None,
            "judge2": float(j2_labels.count(-1) / len(j2_labels)) if j2_labels else None,
        },
        "rows": rows,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=2))

    lines = [
        "# LLM-judge inter-rater agreement (Cohen's kappa)",
        "",
        f"**Judge 1** ({J1_NAME}) and **Judge 2** ({J2_NAME}) classify "
        f"each of {len(all_pairs)} balanced pairs as EQUIVALENT or DIFFERENT. "
        f"The cosine-cluster partition (single-link cosine threshold "
        f"`tau={TAU_COS}` on `{EMBED_MODEL}` embeddings) is treated as a "
        f"third rater (the proxy ground truth from the partitioner). "
        f"Pairs are balanced 50/50 within-cluster vs between-cluster, "
        f"sampled uniformly across TriviaQA / SQuAD / NQ-open.",
        "",
        "## Cohen's kappa",
        "",
        "| Comparison | kappa | n |",
        "|---|---|---|",
        f"| Judge 1 vs Judge 2 (inter-judge) | {k_inter:.3f} | {n_inter} |",
        f"| Judge 1 vs partition | {k_j1_part:.3f} | {n_j1p} |",
        f"| Judge 2 vs partition | {k_j2_part:.3f} | {n_j2p} |",
        "",
        "## Unparseable response rate",
        "",
        f"- Judge 1: {out['rate_unparseable']['judge1']*100:.1f}%",
        f"- Judge 2: {out['rate_unparseable']['judge2']*100:.1f}%",
        "",
        "## Honest framing",
        "",
        "This is an **LLM-judge proxy** for the human inter-annotator "
        "study requested by the council. It does NOT replace human "
        "evaluation. It does provide an independent signal: two LLM "
        "judges with different model versions and different prompting "
        "personas classify the equivalence labels of a balanced pair "
        "set, and we report Cohen's kappa against each other and "
        "against the cosine-cluster partition. A high inter-judge kappa "
        "(judges agree) combined with a high judge-vs-partition kappa "
        "(judges agree with the proxy) is the operational signal that "
        "the cosine-cluster partition labels are recoverable by strong "
        "LLM judges; a high inter-judge kappa with low judge-vs-"
        "partition kappa would indicate that the judges agree but "
        "disagree with the partition (suspicious). We disclose all "
        "three numbers and the per-pair labels in the released "
        "artifact.",
    ]
    OUT_MD.write_text("\n".join(lines))
    print(f"[llmjudge] wrote {OUT_JSON} and {OUT_MD}")
    print(f"[llmjudge] kappa(j1, j2)={k_inter:.3f}; "
          f"kappa(j1, part)={k_j1_part:.3f}; "
          f"kappa(j2, part)={k_j2_part:.3f}")


if __name__ == "__main__":
    main()
