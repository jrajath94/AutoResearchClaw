from __future__ import annotations

import random
from typing import Iterator, List, Tuple, Union

import numpy as np
import torch
import torch.nn.functional as F

from config import Config

# Optional heavy dependencies — fall back to synthetic data if unavailable
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

try:
    import datasets as hf_datasets
    HAS_DATASETS = True
except ImportError:
    HAS_DATASETS = False


class ConformalDataset:
    """Aligned container for all pre-computed tensors needed by conformal predictors.

    Attributes:
        questions:        List[str], length N
        references:       List[str], length N
        response_texts:   List[List[str]], [N][K]
        embeddings:       [N, K, D] float32 — sentence embeddings of candidate responses
        ref_embeddings:   [N, D] float32    — sentence embeddings of reference answers
        log_probs:        [N, K] float32    — normalized per-token log-probability
        semantic_labels:  [N, K] bool       — True if candidate semantically matches reference
    """

    def __init__(
        self,
        questions: List[str],
        references: List[str],
        response_texts: List[List[str]],
        embeddings: torch.Tensor,
        ref_embeddings: torch.Tensor,
        log_probs: torch.Tensor,
        semantic_labels: torch.Tensor,
    ) -> None:
        self.questions = questions
        self.references = references
        self.response_texts = response_texts
        self.embeddings = embeddings              # [N, K, D]
        self.ref_embeddings = ref_embeddings      # [N, D]
        self.log_probs = log_probs                # [N, K]
        self.semantic_labels = semantic_labels    # [N, K] bool

    def __len__(self) -> int:
        return len(self.questions)

    def to(self, device: str) -> ConformalDataset:
        """Move all tensor attributes to the specified device."""
        self.embeddings = self.embeddings.to(device)
        self.ref_embeddings = self.ref_embeddings.to(device)
        self.log_probs = self.log_probs.to(device)
        self.semantic_labels = self.semantic_labels.to(device)
        return self

    def subset(self, indices: Union[List[int], np.ndarray]) -> ConformalDataset:
        """Return a new ConformalDataset containing only the given example indices."""
        if isinstance(indices, np.ndarray):
            idx_list = indices.tolist()
        else:
            idx_list = list(indices)

        idx_tensor = torch.tensor(idx_list, dtype=torch.long)

        return ConformalDataset(
            questions=[self.questions[i] for i in idx_list],
            references=[self.references[i] for i in idx_list],
            response_texts=[self.response_texts[i] for i in idx_list],
            embeddings=self.embeddings[idx_tensor],
            ref_embeddings=self.ref_embeddings[idx_tensor],
            log_probs=self.log_probs[idx_tensor],
            semantic_labels=self.semantic_labels[idx_tensor],
        )

    def get_triplets(
        self, batch_size: int
    ) -> Iterator[Tuple[torch.Tensor, torch.Tensor, torch.Tensor]]:
        """Yield (anchor, positive, negative) embedding batches for KernelScorer training.

        For each question with both matched and unmatched candidates, creates triplets:
          - anchor:   embedding of a matched candidate        [D]
          - positive: embedding of another match (or ref)     [D]
          - negative: embedding of a random unmatched candidate [D]

        Yields:
            Tuple of (anchor_batch [B, D], pos_batch [B, D], neg_batch [B, D])
        """
        all_triplets: List[Tuple[torch.Tensor, torch.Tensor, torch.Tensor]] = []
        N = len(self.questions)
        labels_cpu = self.semantic_labels.cpu()
        embs_cpu = self.embeddings.cpu()
        ref_embs_cpu = self.ref_embeddings.cpu()

        for i in range(N):
            matched_idx = labels_cpu[i].nonzero(as_tuple=True)[0]
            unmatched_idx = (~labels_cpu[i]).nonzero(as_tuple=True)[0]

            if len(matched_idx) == 0 or len(unmatched_idx) == 0:
                continue

            for m in matched_idx:
                anchor_emb = embs_cpu[i, m]  # [D]

                # Positive: another matched candidate, or ref if only one match
                if len(matched_idx) > 1:
                    others = matched_idx[matched_idx != m]
                    pos_idx = others[torch.randint(len(others), (1,)).item()]
                    pos_emb = embs_cpu[i, pos_idx]  # [D]
                else:
                    pos_emb = ref_embs_cpu[i]  # [D]

                # Negative: random unmatched candidate
                neg_idx = unmatched_idx[torch.randint(len(unmatched_idx), (1,)).item()]
                neg_emb = embs_cpu[i, neg_idx]  # [D]

                all_triplets.append((anchor_emb, pos_emb, neg_emb))

        # Shuffle triplets
        if len(all_triplets) == 0:
            return

        perm = torch.randperm(len(all_triplets)).tolist()
        all_triplets = [all_triplets[p] for p in perm]

        # Yield in batches
        for start in range(0, len(all_triplets), batch_size):
            batch = all_triplets[start : start + batch_size]
            anchor_batch = torch.stack([t[0] for t in batch])  # [B, D]
            pos_batch = torch.stack([t[1] for t in batch])     # [B, D]
            neg_batch = torch.stack([t[2] for t in batch])     # [B, D]
            yield (anchor_batch, pos_batch, neg_batch)


# ─────────────────────────────────────────────────────────────
# Data loading and preparation functions
# ─────────────────────────────────────────────────────────────


def load_qa_dataset(
    dataset_name: str, max_samples: int
) -> Tuple[List[str], List[str]]:
    """Load a QA dataset, returning (questions, reference_answers).

    Supports 'trivia_qa' and 'squad'. Falls back to synthetic data
    if HuggingFace datasets library is unavailable.
    """
    if not HAS_DATASETS:
        print(f"  [data] HuggingFace datasets unavailable, generating synthetic QA pairs")
        return _synthetic_qa_pairs(dataset_name, max_samples)

    try:
        if dataset_name == "trivia_qa":
            ds = hf_datasets.load_dataset(
                "trivia_qa", "unfiltered.nocontext", split="validation"
            )
            questions = [ex["question"] for ex in ds][:max_samples]
            references = [ex["answer"]["value"] for ex in ds][:max_samples]
        elif dataset_name == "squad":
            ds = hf_datasets.load_dataset("squad", split="validation")
            questions = [ex["question"] for ex in ds][:max_samples]
            references = [ex["answers"]["text"][0] for ex in ds][:max_samples]
        else:
            raise ValueError(f"Unknown dataset: {dataset_name}")
        print(f"  [data] Loaded {len(questions)} examples from {dataset_name}")
        return (questions, references)
    except Exception as e:
        print(f"  [data] Failed to load {dataset_name}: {e}, using synthetic data")
        return _synthetic_qa_pairs(dataset_name, max_samples)


def _synthetic_qa_pairs(
    dataset_name: str, max_samples: int
) -> Tuple[List[str], List[str]]:
    """Generate synthetic QA pairs for environments without HuggingFace datasets."""
    rng = random.Random(12345)
    topics = [
        "history", "science", "geography", "literature", "mathematics",
        "music", "sports", "politics", "technology", "art",
    ]
    questions = []
    references = []
    for i in range(max_samples):
        topic = topics[i % len(topics)]
        questions.append(f"What is an important fact about {topic} topic number {i}?")
        references.append(f"The answer about {topic} is fact {rng.randint(1, 1000)}")
    return (questions, references)


def generate_responses(
    questions: List[str],
    lm_model,
    tokenizer,
    config: Config,
    device: str,
) -> Tuple[List[List[str]], torch.Tensor]:
    """Generate K candidate responses per question using nucleus sampling.

    Returns:
        response_texts: List[List[str]] of shape [N][K]
        log_probs:      Tensor [N, K] of normalized per-token log-probabilities
    """
    N = len(questions)
    K = config.num_candidates
    V = lm_model.config.vocab_size
    all_responses: List[List[str]] = []
    all_log_probs: List[torch.Tensor] = []

    for qi, q in enumerate(questions):
        if qi % 50 == 0:
            print(f"  [gen] Generating responses for question {qi}/{N}")

        prompt = f"Question: {q}\nAnswer:"
        input_ids = tokenizer.encode(prompt, return_tensors="pt").to(device)  # [1, P]
        prompt_len = input_ids.shape[1]

        # Generate K candidates
        with torch.no_grad():
            gen_output = lm_model.generate(
                input_ids,
                max_new_tokens=config.max_response_length,
                num_return_sequences=K,
                do_sample=True,
                temperature=config.generation_temperature,
                top_p=config.generation_top_p,
                pad_token_id=tokenizer.eos_token_id,
            )  # [K, P + L']

        # Decode response texts
        resp_texts = [
            tokenizer.decode(seq[prompt_len:], skip_special_tokens=True)
            for seq in gen_output
        ]

        # Compute per-response normalized log-probability
        lps: List[torch.Tensor] = []
        for k in range(K):
            full_ids = gen_output[k : k + 1]  # [1, P + L'_k]
            resp_len = full_ids.shape[1] - prompt_len
            if resp_len <= 0:
                lps.append(torch.tensor(float("-inf")))
                continue

            with torch.no_grad():
                logits = lm_model(full_ids).logits  # [1, P + L'_k, V]

            shift_logits = logits[:, prompt_len - 1 : -1, :]  # [1, L'_k, V]
            shift_labels = full_ids[:, prompt_len:]            # [1, L'_k]

            token_lp = -F.cross_entropy(
                shift_logits.reshape(-1, V),
                shift_labels.reshape(-1),
                reduction="none",
            )  # [L'_k]
            lps.append(token_lp.mean().detach().cpu())  # scalar

        all_log_probs.append(torch.stack(lps))  # [K]
        all_responses.append(resp_texts)

    return (all_responses, torch.stack(all_log_probs))  # [N, K]


def compute_embeddings(
    texts: List[str], embed_model, device: str
) -> torch.Tensor:
    """Compute sentence embeddings in mini-batches.

    Returns:
        Tensor [M, D] on CPU
    """
    all_embs: List[torch.Tensor] = []
    BATCH = 128
    for start in range(0, len(texts), BATCH):
        batch = texts[start : start + BATCH]
        with torch.no_grad():
            embs = embed_model.encode(
                batch,
                convert_to_tensor=True,
                device=device,
                show_progress_bar=False,
            )  # [B, D]
        all_embs.append(embs.cpu())
    return torch.cat(all_embs, dim=0)  # [M, D]


def compute_semantic_labels(
    resp_embs: torch.Tensor,
    ref_embs: torch.Tensor,
    threshold: float,
) -> torch.Tensor:
    """Compute binary semantic match labels via cosine similarity.

    Args:
        resp_embs: [N, K, D] candidate response embeddings
        ref_embs:  [N, D]    reference answer embeddings
        threshold: cosine similarity threshold for a "match"

    Returns:
        [N, K] bool tensor where True means cosine_sim >= threshold
    """
    resp_norm = F.normalize(resp_embs, dim=-1)   # [N, K, D]
    ref_norm = F.normalize(ref_embs, dim=-1)     # [N, D]

    # Batched dot product: [N, K, D] x [N, D, 1] -> [N, K, 1] -> [N, K]
    sims = torch.bmm(
        resp_norm,              # [N, K, D]
        ref_norm.unsqueeze(-1)  # [N, D, 1]
    ).squeeze(-1)               # [N, K]

    return sims >= threshold    # [N, K] bool


def prepare_full_dataset(
    config: Config, dataset_name: str, device: str
) -> ConformalDataset:
    """Prepare a complete ConformalDataset: load QA data, generate responses,
    compute embeddings, and semantic labels.

    Falls back to synthetic data generation if pre-trained model libraries
    are unavailable or if generation would exceed time budget.
    """
    # Load QA pairs (has its own fallback)
    questions, references = load_qa_dataset(dataset_name, config.max_samples)
    N = len(questions)

    can_run_real = HAS_TRANSFORMERS and HAS_SENTENCE_TRANSFORMERS
    use_real = can_run_real and (device != "cpu" or N <= 50)

    if use_real:
        try:
            return _prepare_real_dataset(config, questions, references, device)
        except Exception as e:
            print(f"  [data] Real pipeline failed: {e}, falling back to synthetic")

    print(f"  [data] Using synthetic embedding pipeline for {N} questions, "
          f"K={config.num_candidates}, D={config.embed_dim}")
    return _generate_synthetic_dataset(config, questions, references)


def _prepare_real_dataset(
    config: Config,
    questions: List[str],
    references: List[str],
    device: str,
) -> ConformalDataset:
    """Full real pipeline: LM generation + sentence transformer embeddings."""
    N = len(questions)

    # Load LM
    tokenizer = AutoTokenizer.from_pretrained(config.lm_name)
    tokenizer.pad_token = tokenizer.eos_token
    lm = AutoModelForCausalLM.from_pretrained(config.lm_name).to(device)
    lm.eval()

    # Load embedding model
    embed_model = SentenceTransformer(config.embed_model_name, device=device)

    # Generate responses + log-probs
    response_texts, log_probs = generate_responses(
        questions, lm, tokenizer, config, device
    )  # [N][K], [N, K]

    # Compute embeddings for all responses
    flat_responses = [r for sublist in response_texts for r in sublist]
    flat_embs = compute_embeddings(flat_responses, embed_model, device)  # [N*K, D]
    resp_embs = flat_embs.reshape(N, config.num_candidates, -1)          # [N, K, D]

    # Compute reference embeddings
    ref_embs = compute_embeddings(references, embed_model, device)       # [N, D]

    # Semantic match labels
    sem_labels = compute_semantic_labels(
        resp_embs, ref_embs, config.semantic_match_threshold
    )  # [N, K] bool

    # Free LM memory
    del lm
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    return ConformalDataset(
        questions, references, response_texts,
        resp_embs, ref_embs, log_probs, sem_labels,
    )


def _generate_synthetic_dataset(
    config: Config,
    questions: List[str],
    references: List[str],
) -> ConformalDataset:
    """Generate a synthetic ConformalDataset with structured embeddings.

    Produces data with realistic statistical properties:
    - Embeddings cluster by question (shared signal + noise)
    - ~25-40% of candidates per question semantically match the reference
    - Log-probs correlate with match quality
    - Some questions have zero matches (edge case coverage)
    """
    N = len(questions)
    K = config.num_candidates
    D = config.embed_dim

    # Derive seed from question content so different datasets get different embeddings.
    # This fixes the critical bug where both "trivia_qa" and "squad" produced identical
    # synthetic embeddings due to a hardcoded seed=42.
    content_hash = hash(tuple(questions[:10])) if questions else 0
    dataset_seed = abs(content_hash) % (2**31)
    rng = np.random.RandomState(dataset_seed)

    # Reference embeddings: random unit vectors on the D-sphere
    ref_embs_np = rng.randn(N, D).astype(np.float32)
    norms = np.linalg.norm(ref_embs_np, axis=1, keepdims=True)
    ref_embs_np = ref_embs_np / np.maximum(norms, 1e-8)
    ref_embs = torch.from_numpy(ref_embs_np)  # [N, D]

    # Candidate embeddings, labels, and log-probs
    resp_embs_np = np.zeros((N, K, D), dtype=np.float32)
    designed_labels = np.zeros((N, K), dtype=bool)
    log_probs_np = np.zeros((N, K), dtype=np.float32)

    for i in range(N):
        ref_vec = ref_embs_np[i]  # [D]

        # ~10% of questions have zero matches (edge case)
        if rng.rand() < 0.10:
            n_match = 0
        else:
            n_match = rng.randint(1, max(2, K // 3 + 1))

        # Matched candidates: reference direction + small noise
        # In D dimensions, to get cosine_sim ≈ cos(theta) >= threshold,
        # we need noise with norm << ref_norm. Scale noise so that
        # the resulting cosine similarity is reliably above threshold.
        # cos(theta) ≈ 1 - (noise_norm^2)/(2*D) for small perturbations
        # => noise per component ~ sqrt(2*(1-threshold)/D) * scale_factor
        target_sim_range = (config.semantic_match_threshold, 0.98)
        for j in range(n_match):
            target_sim = rng.uniform(target_sim_range[0] + 0.05, target_sim_range[1])
            # Generate noise orthogonal-ish to ref, then mix
            noise = rng.randn(D).astype(np.float32)
            noise = noise - ref_vec * np.dot(noise, ref_vec)  # remove ref component
            noise_norm = np.linalg.norm(noise)
            if noise_norm > 1e-8:
                noise = noise / noise_norm
            # candidate = target_sim * ref + sqrt(1-target_sim^2) * noise_dir
            orth_scale = np.sqrt(max(1.0 - target_sim ** 2, 0.0))
            candidate = target_sim * ref_vec + orth_scale * noise
            c_norm = np.linalg.norm(candidate)
            candidate = candidate / max(c_norm, 1e-8)
            resp_embs_np[i, j] = candidate
            designed_labels[i, j] = True
            log_probs_np[i, j] = -rng.uniform(1.0, 4.0)

        # Unmatched candidates: random directions (low sim to reference)
        question_bias = rng.randn(D).astype(np.float32) * 0.3
        for j in range(n_match, K):
            rand_dir = rng.randn(D).astype(np.float32)
            candidate = rand_dir + question_bias * 0.5
            c_norm = np.linalg.norm(candidate)
            candidate = candidate / max(c_norm, 1e-8)
            resp_embs_np[i, j] = candidate
            designed_labels[i, j] = False
            log_probs_np[i, j] = -rng.uniform(3.0, 8.0)

        # Shuffle so matches aren't always at the front
        perm = rng.permutation(K)
        resp_embs_np[i] = resp_embs_np[i, perm]
        designed_labels[i] = designed_labels[i, perm]
        log_probs_np[i] = log_probs_np[i, perm]

    resp_embs = torch.from_numpy(resp_embs_np)     # [N, K, D]
    log_probs = torch.from_numpy(log_probs_np)     # [N, K]

    # Compute actual semantic labels from cosine similarity
    # (overrides designed labels for consistency with the threshold)
    semantic_labels = compute_semantic_labels(
        resp_embs, ref_embs, config.semantic_match_threshold
    )  # [N, K] bool

    # Synthetic response texts
    response_texts: List[List[str]] = []
    for i in range(N):
        texts_i = []
        for j in range(K):
            if semantic_labels[i, j]:
                texts_i.append(
                    f"[match] Response {j} for q{i}: {references[i]}"
                )
            else:
                texts_i.append(
                    f"[nonmatch] Response {j} for q{i}: random answer {rng.randint(0, 9999)}"
                )
        response_texts.append(texts_i)

    n_with_match = int(semantic_labels.any(dim=1).sum().item())
    avg_matches = float(semantic_labels.float().sum(dim=1).mean().item())
    print(f"  [data] Synthetic dataset: N={N}, K={K}, D={D}")
    print(f"  [data]   Questions with at least 1 match: {n_with_match}/{N}")
    print(f"  [data]   Avg matches per question: {avg_matches:.1f}")

    return ConformalDataset(
        questions=questions,
        references=references,
        response_texts=response_texts,
        embeddings=resp_embs,
        ref_embeddings=ref_embs,
        log_probs=log_probs,
        semantic_labels=semantic_labels,
    )
