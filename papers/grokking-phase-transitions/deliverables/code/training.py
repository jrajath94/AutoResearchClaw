"""Training strategies (conditions) and evaluation utilities.

Defines BaseCondition template and six concrete strategy classes, each
encapsulating: model creation, optimizer setup, loss computation,
one-step training logic, and superposition measurement.
"""

import math
import time
from typing import Dict, List, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

from experiment_config import Config
from models import GrokTransformer, GrokMLP

# =====================================================================
# Standalone utility functions
# =====================================================================

def evaluate(model: nn.Module, loader, device: torch.device) -> Dict[str, float]:
    """Compute accuracy and average cross-entropy loss on a data loader."""
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0
    with torch.no_grad():
        for x, y in loader:
            x = x.to(device)
            y = y.to(device)
            logits = model(x)
            total_loss += F.cross_entropy(logits, y, reduction="sum").item()
            correct += (logits.argmax(dim=1) == y).sum().item()
            total += y.size(0)
    accuracy = correct / max(total, 1)
    avg_loss = total_loss / max(total, 1)
    return {"accuracy": accuracy, "loss": avg_loss}

def find_grok_step(history: dict) -> float:
    """Return training step at which grokking occurs (inf if never)."""
    memorised = False
    for train_acc, test_acc, step in zip(
        history["train_acc"], history["test_acc"], history["step"]
    ):
        if train_acc > 0.99:
            memorised = True
        if memorised and test_acc > 0.90:
            return step
    return float("inf")

def compute_centroid_orth_reg(
    hidden: torch.Tensor, labels: torch.Tensor, num_classes: int
) -> torch.Tensor:
    """Orthogonality pressure on per-class centroid directions."""
    centroids: List[torch.Tensor] = []
    for c in range(num_classes):
        mask = labels == c
        count = mask.sum().item()
        if count > 1:
            centroids.append(hidden[mask].mean(dim=0))
    if len(centroids) < 2:
        return torch.tensor(0.0, device=hidden.device, requires_grad=False)
    C = torch.stack(centroids)
    C = F.normalize(C, dim=1)
    gram = C @ C.T
    eye = torch.eye(gram.size(0), device=gram.device)
    return ((gram - eye) ** 2).mean()

# =====================================================================
# Shared SVD superposition probe
# =====================================================================

def _svd_superposition_metric(
    model: nn.Module, loader, device: torch.device, config: Config
) -> float:
    """SVD participation-ratio probe on hidden representations.
    Returns metric in [0, 1] where 1 = full superposition, 0 = clean."""
    x_parts: List[torch.Tensor] = []
    n_collected = 0
    target = config.superposition_sample_size
    for x_batch, _ in loader:
        x_parts.append(x_batch)
        n_collected += x_batch.size(0)
        if n_collected >= target:
            break
    x_sample = torch.cat(x_parts, dim=0)[:target].to(device)

    H = model.get_hidden(x_sample)
    H = H - H.mean(dim=0)

    _, S, _ = torch.linalg.svd(H, full_matrices=False)
    S_sq = S ** 2
    PR = (S_sq.sum() ** 2) / (S_sq.pow(2).sum() + 1e-12)
    metric = 1.0 - (PR / config.d_model).item()
    metric = max(0.0, min(1.0, metric))
    return metric

# =====================================================================
# Shared AdamW optimizer builder
# =====================================================================

def _build_adamw(model: nn.Module, lr: float, weight_decay: float):
    """Build AdamW with separate decay / no-decay param groups."""
    decay_params = [p for _, p in model.named_parameters() if p.dim() >= 2]
    no_decay_params = [p for _, p in model.named_parameters() if p.dim() < 2]
    return torch.optim.AdamW(
        [
            {"params": decay_params, "weight_decay": weight_decay},
            {"params": no_decay_params, "weight_decay": 0.0},
        ],
        lr=lr,
    )

# =====================================================================
# Helper: compute grok ratio safely
# =====================================================================

def _compute_grok_ratio(grok_step: float, history: dict) -> float:
    """Compute grok_step / memorisation_step, returning inf if not grokked."""
    if grok_step == float("inf"):
        return float("inf")
    if len(history["step"]) == 0:
        return float("inf")
    mem_idx = next(
        (i for i, a in enumerate(history["train_acc"]) if a > 0.99),
        len(history["step"]) - 1,
    )
    mem_step = history["step"][mem_idx]
    return grok_step / max(mem_step, 1)

# =====================================================================
# Helper: adaptive lambda computation
# =====================================================================

def _adaptive_lambda_svd(superposition: float, base_lambda: float) -> float:
    """Compute adaptive lambda based on SVD superposition metric."""
    if superposition > 0.5:
        return base_lambda * (1.0 + superposition)
    if superposition > 0.2:
        return base_lambda * 0.5
    return base_lambda * 0.05

def _adaptive_lambda_coherence(superposition: float, base_lambda: float) -> float:
    """Compute adaptive lambda based on cheap coherence metric."""
    if superposition > 0.3:
        return base_lambda * (1.0 + 2.0 * superposition)
    return base_lambda * 0.1

def _distance_weighted_lambda(size_ratio: float, base_lambda: float) -> float:
    """Compute distance-weighted lambda relative to N_c."""
    if size_ratio < 1.0:
        return base_lambda * 2.0
    clamped_ratio = min(size_ratio, 5.0)
    return base_lambda / clamped_ratio

def _phase_aware_lr(size_ratio: float, epoch_frac: float, base_lr: float, epochs: int) -> float:
    """Compute phase-aware learning rate."""
    if size_ratio < 1.0:
        return base_lr
    predicted_period = epochs / size_ratio
    t = epoch_frac / max(predicted_period, 1e-8)
    return base_lr * (0.5 * (1.0 + math.cos(math.pi * min(t, 1.0))))

# =====================================================================
# BASE CONDITION
# =====================================================================

class BaseCondition:
    """Abstract strategy template for experiment conditions."""

    def __init__(
        self, config: Config, vocab_size: int, seq_len: int, num_classes: int
    ) -> None:
        self.config = config
        self.vocab_size = vocab_size
        self.seq_len = seq_len
        self.num_classes = num_classes
        self.name = "base"

    def _reset_run_state(self) -> None:
        pass

    def build_model(self) -> nn.Module:
        return GrokTransformer(
            vocab_size=self.vocab_size,
            seq_len=self.seq_len,
            num_classes=self.num_classes,
            d_model=self.config.d_model,
            n_heads=self.config.n_heads,
            n_layers=self.config.n_layers,
            dropout=self.config.dropout,
        )

    def configure_optimizer(self, model: nn.Module):
        return torch.optim.Adam(model.parameters(), lr=self.config.lr)

    def compute_loss(
        self, model: nn.Module, logits: torch.Tensor, labels: torch.Tensor
    ) -> torch.Tensor:
        return F.cross_entropy(logits, labels)

    def train_step(
        self,
        model: nn.Module,
        x: torch.Tensor,
        y: torch.Tensor,
        optimizer,
    ) -> float:
        model.train()
        optimizer.zero_grad()
        logits = model(x)
        loss = self.compute_loss(model, logits, y)
        loss.backward()
        optimizer.step()
        return loss.item()

    def measure_superposition(
        self, model: nn.Module, loader, device: torch.device
    ) -> Optional[float]:
        return None

    def train_epoch(
        self,
        model: nn.Module,
        loader,
        optimizer,
        device: torch.device,
    ) -> Tuple[float, float]:
        total_loss = 0.0
        correct = 0
        total = 0
        for x, y in loader:
            x = x.to(device)
            y = y.to(device)
            step_loss = self.train_step(model, x, y, optimizer)
            total_loss += step_loss * y.size(0)
            with torch.no_grad():
                preds = model(x).argmax(dim=1)
                correct += (preds == y).sum().item()
            total += y.size(0)
        avg_loss = total_loss / max(total, 1)
        accuracy = correct / max(total, 1)
        return avg_loss, accuracy

    def run(
        self, train_loader, test_loader, seed: int, device: torch.device
    ) -> dict:
        self._reset_run_state()

        model = self.build_model().to(device)
        optimizer = self.configure_optimizer(model)

        history: Dict[str, list] = {
            "train_loss": [],
            "train_acc": [],
            "test_acc": [],
            "test_loss": [],
            "superposition": [],
            "step": [],
        }

        global_step = 0
        steps_per_epoch = len(train_loader)
        start_time = time.time()

        for epoch in range(self.config.epochs):
            elapsed = time.time() - start_time
            if elapsed > self.config.max_time_per_condition:
                print(f"  TIME_BUDGET_EXCEEDED at epoch {epoch}")
                break

            avg_loss, train_acc = self.train_epoch(
                model, train_loader, optimizer, device
            )
            global_step += steps_per_epoch

            if math.isnan(avg_loss) or avg_loss > 100.0:
                print(f"  FAIL: NaN/divergence at epoch {epoch}, loss={avg_loss}")
                break

            if epoch % self.config.eval_interval == 0 or epoch == self.config.epochs - 1:
                test_met = evaluate(model, test_loader, device)
                sup = None
                if epoch % self.config.superposition_interval == 0:
                    sup = self.measure_superposition(model, train_loader, device)
                history["train_loss"].append(avg_loss)
                history["train_acc"].append(train_acc)
                history["test_acc"].append(test_met["accuracy"])
                history["test_loss"].append(test_met["loss"])
                history["superposition"].append(sup)
                history["step"].append(global_step)

            if (
                len(history["test_acc"]) >= 5
                and all(a > 0.99 for a in history["test_acc"][-5:])
            ):
                break

        final = evaluate(model, test_loader, device)
        grok_step = find_grok_step(history)
        grok_ratio = _compute_grok_ratio(grok_step, history)

        return {
            "final_test_acc": final["accuracy"],
            "final_test_loss": final["loss"],
            "grok_step": grok_step,
            "grok_step_ratio": grok_ratio,
            "total_steps": global_step,
            "history": history,
        }

# =====================================================================
# CONDITION 1: Phase_baseline_1 - MLP + Adam, no weight decay
# =====================================================================

class MLPBaseline(BaseCondition):
    """MLP baseline: GrokMLP + Adam (zero weight decay) + plain CE."""

    def __init__(
        self, config: Config, vocab_size: int, seq_len: int, num_classes: int
    ) -> None:
        super().__init__(config, vocab_size, seq_len, num_classes)
        self.name = "Phase_baseline_1"

    def build_model(self) -> nn.Module:
        return GrokMLP(
            vocab_size=self.vocab_size,
            seq_len=self.seq_len,
            num_classes=self.num_classes,
            d_model=self.config.d_model,
            hidden_dim=self.config.mlp_hidden,
        )

    def configure_optimizer(self, model: nn.Module):
        return torch.optim.Adam(
            model.parameters(), lr=self.config.lr, weight_decay=0.0
        )

    def compute_loss(
        self, model: nn.Module, logits: torch.Tensor, labels: torch.Tensor
    ) -> torch.Tensor:
        return F.cross_entropy(logits, labels)

# =====================================================================
# CONDITION 2: Phase_baseline_2 - Transformer + AdamW (classic grokking)
# =====================================================================

class TransformerBaseline(BaseCondition):
    """Classic grokking: GrokTransformer + AdamW with high weight decay."""

    def __init__(
        self, config: Config, vocab_size: int, seq_len: int, num_classes: int
    ) -> None:
        super().__init__(config, vocab_size, seq_len, num_classes)
        self.name = "Phase_baseline_2"

    def build_model(self) -> nn.Module:
        return GrokTransformer(
            vocab_size=self.vocab_size,
            seq_len=self.seq_len,
            num_classes=self.num_classes,
            d_model=self.config.d_model,
            n_heads=self.config.n_heads,
            n_layers=self.config.n_layers,
            dropout=self.config.dropout,
        )

    def configure_optimizer(self, model: nn.Module):
        return _build_adamw(model, self.config.lr, self.config.weight_decay)

# =====================================================================
# CONDITION 3: Phase_proposed - SVD probe + adaptive orth-reg
# =====================================================================

class PhaseTransitionProposed(BaseCondition):
    """Core method: Transformer + SVD superposition metric + adaptive orth-reg."""

    def __init__(
        self, config: Config, vocab_size: int, seq_len: int, num_classes: int
    ) -> None:
        super().__init__(config, vocab_size, seq_len, num_classes)
        self.name = "Phase_proposed"
        self.current_superposition: float = 0.5
        self.phase_transitioned: bool = False
        self.superposition_history: List[float] = []

    def _reset_run_state(self) -> None:
        self.current_superposition = 0.5
        self.phase_transitioned = False
        self.superposition_history = []

    def build_model(self) -> nn.Module:
        return GrokTransformer(
            vocab_size=self.vocab_size,
            seq_len=self.seq_len,
            num_classes=self.num_classes,
            d_model=self.config.d_model,
            n_heads=self.config.n_heads,
            n_layers=self.config.n_layers,
            dropout=self.config.dropout,
        )

    def configure_optimizer(self, model: nn.Module):
        return _build_adamw(model, self.config.lr, self.config.weight_decay)

    def measure_superposition(
        self, model: nn.Module, loader, device: torch.device
    ) -> float:
        metric = _svd_superposition_metric(model, loader, device, self.config)
        self.current_superposition = metric
        self.superposition_history.append(metric)
        if len(self.superposition_history) >= 3:
            if self.superposition_history[-3] > 0.5 and metric < 0.3:
                self.phase_transitioned = True
        return metric

    def compute_loss(
        self, model: nn.Module, logits: torch.Tensor, labels: torch.Tensor
    ) -> torch.Tensor:
        ce = F.cross_entropy(logits, labels)
        hidden = model.get_cached_hidden()
        orth_reg = compute_centroid_orth_reg(hidden, labels, self.num_classes)
        lam = _adaptive_lambda_svd(self.current_superposition, self.config.adaptive_reg_lambda)
        return ce + lam * orth_reg

    def train_step(
        self, model: nn.Module, x: torch.Tensor, y: torch.Tensor, optimizer
    ) -> float:
        model.train()
        optimizer.zero_grad()
        logits = model(x)
        loss = self.compute_loss(model, logits, y)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        return loss.item()

# =====================================================================
# CONDITION 4: Phase_variant - Critical-size-aware LR scheduling
# =====================================================================

class CriticalSizeVariant(BaseCondition):
    """Proposed method + theoretical critical dataset size N_c."""

    def __init__(
        self, config: Config, vocab_size: int, seq_len: int, num_classes: int
    ) -> None:
        super().__init__(config, vocab_size, seq_len, num_classes)
        self.name = "Phase_variant"
        self.current_superposition: float = 0.5
        self.n_critical = self._compute_critical_size()
        self.actual_n = int(self.num_classes ** 2 * config.train_fraction)
        self.size_ratio = self.actual_n / max(self.n_critical, 1)

    def _reset_run_state(self) -> None:
        self.current_superposition = 0.5

    def _compute_critical_size(self) -> int:
        c = self.config
        raw = (
            c.critical_size_constant
            * math.sqrt(self.num_classes)
            * c.d_model
            / (c.n_layers * c.n_heads)
        )
        return max(int(raw), 1)

    def build_model(self) -> nn.Module:
        return GrokTransformer(
            vocab_size=self.vocab_size,
            seq_len=self.seq_len,
            num_classes=self.num_classes,
            d_model=self.config.d_model,
            n_heads=self.config.n_heads,
            n_layers=self.config.n_layers,
            dropout=self.config.dropout,
        )

    def configure_optimizer(self, model: nn.Module):
        return _build_adamw(model, self.config.lr, self.config.weight_decay)

    def measure_superposition(
        self, model: nn.Module, loader, device: torch.device
    ) -> float:
        metric = _svd_superposition_metric(model, loader, device, self.config)
        self.current_superposition = metric
        return metric

    def compute_loss(
        self, model: nn.Module, logits: torch.Tensor, labels: torch.Tensor
    ) -> torch.Tensor:
        ce = F.cross_entropy(logits, labels)
        hidden = model.get_cached_hidden()
        orth_reg = compute_centroid_orth_reg(hidden, labels, self.num_classes)
        lam = _distance_weighted_lambda(self.size_ratio, self.config.adaptive_reg_lambda)
        return ce + lam * orth_reg

    def train_step(
        self,
        model: nn.Module,
        x: torch.Tensor,
        y: torch.Tensor,
        optimizer,
        epoch_frac: float = 0.0,
    ) -> float:
        model.train()
        lr = _phase_aware_lr(self.size_ratio, epoch_frac, self.config.lr, self.config.epochs)
        for pg in optimizer.param_groups:
            pg["lr"] = max(lr, 1e-6)

        optimizer.zero_grad()
        logits = model(x)
        loss = self.compute_loss(model, logits, y)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        return loss.item()

    def train_epoch(
        self,
        model: nn.Module,
        loader,
        optimizer,
        device: torch.device,
        epoch_idx: int = 0,
    ) -> Tuple[float, float]:
        epoch_frac = epoch_idx / max(self.config.epochs, 1)
        total_loss = 0.0
        correct = 0
        total = 0
        for x, y in loader:
            x = x.to(device)
            y = y.to(device)
            step_loss = self.train_step(model, x, y, optimizer, epoch_frac)
            total_loss += step_loss * y.size(0)
            with torch.no_grad():
                correct += (model(x).argmax(dim=1) == y).sum().item()
            total += y.size(0)
        return total_loss / max(total, 1), correct / max(total, 1)

    def run(
        self, train_loader, test_loader, seed: int, device: torch.device
    ) -> dict:
        self._reset_run_state()

        model = self.build_model().to(device)
        optimizer = self.configure_optimizer(model)

        history: Dict[str, list] = {
            "train_loss": [],
            "train_acc": [],
            "test_acc": [],
            "test_loss": [],
            "superposition": [],
            "step": [],
        }

        global_step = 0
        steps_per_epoch = len(train_loader)
        start_time = time.time()

        for epoch in range(self.config.epochs):
            if time.time() - start_time > self.config.max_time_per_condition:
                print(f"  TIME_BUDGET_EXCEEDED at epoch {epoch}")
                break

            avg_loss, train_acc = self.train_epoch(
                model, train_loader, optimizer, device, epoch_idx=epoch
            )
            global_step += steps_per_epoch

            if math.isnan(avg_loss) or avg_loss > 100.0:
                print(f"  FAIL: NaN/divergence at epoch {epoch}, loss={avg_loss}")
                break

            if epoch % self.config.eval_interval == 0 or epoch == self.config.epochs - 1:
                test_met = evaluate(model, test_loader, device)
                sup = None
                if epoch % self.config.superposition_interval == 0:
                    sup = self.measure_superposition(model, train_loader, device)
                history["train_loss"].append(avg_loss)
                history["train_acc"].append(train_acc)
                history["test_acc"].append(test_met["accuracy"])
                history["test_loss"].append(test_met["loss"])
                history["superposition"].append(sup)
                history["step"].append(global_step)

            if (
                len(history["test_acc"]) >= 5
                and all(a > 0.99 for a in history["test_acc"][-5:])
            ):
                break

        final = evaluate(model, test_loader, device)
        grok_step = find_grok_step(history)
        grok_ratio = _compute_grok_ratio(grok_step, history)

        return {
            "final_test_acc": final["accuracy"],
            "final_test_loss": final["loss"],
            "grok_step": grok_step,
            "grok_step_ratio": grok_ratio,
            "total_steps": global_step,
            "history": history,
        }

# =====================================================================
# CONDITION 5: without_key_component - Fixed-lambda ablation
# =====================================================================

class NoAdaptiveRegAblation(BaseCondition):
    """Ablation: same as proposed but lambda is FIXED (never adapts)."""

    def __init__(
        self, config: Config, vocab_size: int, seq_len: int, num_classes: int
    ) -> None:
        super().__init__(config, vocab_size, seq_len, num_classes)
        self.name = "without_key_component"
        self.current_superposition: float = 0.5

    def _reset_run_state(self) -> None:
        self.current_superposition = 0.5

    def build_model(self) -> nn.Module:
        return GrokTransformer(
            vocab_size=self.vocab_size,
            seq_len=self.seq_len,
            num_classes=self.num_classes,
            d_model=self.config.d_model,
            n_heads=self.config.n_heads,
            n_layers=self.config.n_layers,
            dropout=self.config.dropout,
        )

    def configure_optimizer(self, model: nn.Module):
        return _build_adamw(model, self.config.lr, self.config.weight_decay)

    def measure_superposition(
        self, model: nn.Module, loader, device: torch.device
    ) -> float:
        metric = _svd_superposition_metric(model, loader, device, self.config)
        self.current_superposition = metric
        return metric

    def compute_loss(
        self, model: nn.Module, logits: torch.Tensor, labels: torch.Tensor
    ) -> torch.Tensor:
        ce = F.cross_entropy(logits, labels)
        hidden = model.get_cached_hidden()
        orth_reg = compute_centroid_orth_reg(hidden, labels, self.num_classes)
        lam = self.config.fixed_reg_lambda
        return ce + lam * orth_reg

    def train_step(
        self, model: nn.Module, x: torch.Tensor, y: torch.Tensor, optimizer
    ) -> float:
        model.train()
        optimizer.zero_grad()
        logits = model(x)
        loss = self.compute_loss(model, logits, y)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        return loss.item()

# =====================================================================
# CONDITION 6: simplified_version - Cheap embedding-coherence metric
# =====================================================================

class SimplifiedMetricAblation(BaseCondition):
    """Ablation: replaces SVD probe with cheap embedding-coherence proxy."""

    def __init__(
        self, config: Config, vocab_size: int, seq_len: int, num_classes: int
    ) -> None:
        super().__init__(config, vocab_size, seq_len, num_classes)
        self.name = "simplified_version"
        self.current_superposition: float = 0.5

    def _reset_run_state(self) -> None:
        self.current_superposition = 0.5

    def build_model(self) -> nn.Module:
        return GrokTransformer(
            vocab_size=self.vocab_size,
            seq_len=self.seq_len,
            num_classes=self.num_classes,
            d_model=self.config.d_model,
            n_heads=self.config.n_heads,
            n_layers=self.config.n_layers,
            dropout=self.config.dropout,
        )

    def configure_optimizer(self, model: nn.Module):
        return _build_adamw(model, self.config.lr, self.config.weight_decay)

    def measure_superposition(
        self, model: nn.Module, loader, device: torch.device
    ) -> float:
        """CHEAP PROXY: embedding weight coherence (no SVD, no data pass)."""
        W = model.embedding.weight.detach()
        W_norm = F.normalize(W, dim=1)
        gram = W_norm @ W_norm.T
        v_size = gram.size(0)
        off_diag_sum = gram.abs().sum() - gram.diag().abs().sum()
        metric = (off_diag_sum / (v_size * (v_size - 1))).item()
        self.current_superposition = metric
        return metric

    def compute_loss(
        self, model: nn.Module, logits: torch.Tensor, labels: torch.Tensor
    ) -> torch.Tensor:
        ce = F.cross_entropy(logits, labels)
        hidden = model.get_cached_hidden()
        orth_reg = compute_centroid_orth_reg(hidden, labels, self.num_classes)
        lam = _adaptive_lambda_coherence(self.current_superposition, self.config.adaptive_reg_lambda)
        return ce + lam * orth_reg

    def train_step(
        self, model: nn.Module, x: torch.Tensor, y: torch.Tensor, optimizer
    ) -> float:
        model.train()
        optimizer.zero_grad()
        logits = model(x)
        loss = self.compute_loss(model, logits, y)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        return loss.item()