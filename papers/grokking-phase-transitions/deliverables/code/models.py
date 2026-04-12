"""Two model architectures for grokking experiments.

GrokTransformer  - Learnable token + positional embedding -> TransformerEncoder
                   -> mean-pool -> linear classifier.
GrokMLP          - Learnable embedding -> flatten -> 3-layer ReLU MLP -> classifier.

Both share the same forward interface:
    input:  [B, seq_len]   (long token ids)
    output: [B, num_classes] (logits)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional

class GrokTransformer(nn.Module):
    """Small transformer for modular-arithmetic / sparse-parity grokking."""

    def __init__(
        self,
        vocab_size: int,
        seq_len: int,
        num_classes: int,
        d_model: int,
        n_heads: int,
        n_layers: int,
        dropout: float,
    ) -> None:
        super().__init__()

        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_embed = nn.Parameter(
            torch.randn(1, seq_len, d_model) * 0.02
        )

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=n_heads,
            dim_feedforward=4 * d_model,
            dropout=dropout,
            batch_first=True,
            norm_first=True,
        )
        self.transformer = nn.TransformerEncoder(
            encoder_layer, num_layers=n_layers
        )

        self.classifier = nn.Linear(d_model, num_classes)
        self._cached_hidden: Optional[torch.Tensor] = None

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = self.embedding(x) + self.pos_embed       # [B, S, d]
        h = self.transformer(h)                       # [B, S, d]
        h = h.mean(dim=1)                             # [B, d]
        self._cached_hidden = h
        return self.classifier(h)                     # [B, C]

    def get_cached_hidden(self) -> Optional[torch.Tensor]:
        return self._cached_hidden

    def get_hidden(self, x: torch.Tensor) -> torch.Tensor:
        with torch.no_grad():
            h = self.embedding(x) + self.pos_embed
            h = self.transformer(h)
            return h.mean(dim=1)

class GrokMLP(nn.Module):
    """Three-layer ReLU MLP baseline (no attention)."""

    def __init__(
        self,
        vocab_size: int,
        seq_len: int,
        num_classes: int,
        d_model: int,
        hidden_dim: int,
    ) -> None:
        super().__init__()

        self.embedding = nn.Embedding(vocab_size, d_model)

        flat_dim = seq_len * d_model
        self.fc1 = nn.Linear(flat_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, hidden_dim)
        self.classifier = nn.Linear(hidden_dim, num_classes)
        self._cached_hidden: Optional[torch.Tensor] = None

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = self.embedding(x)                          # [B, S, d]
        h = h.reshape(h.size(0), -1)                   # [B, S*d]
        h = F.relu(self.fc1(h))                        # [B, H]
        h = F.relu(self.fc2(h))                        # [B, H]
        h = F.relu(self.fc3(h))                        # [B, H]
        self._cached_hidden = h
        return self.classifier(h)                      # [B, C]

    def get_cached_hidden(self) -> Optional[torch.Tensor]:
        return self._cached_hidden

    def get_hidden(self, x: torch.Tensor) -> torch.Tensor:
        with torch.no_grad():
            h = self.embedding(x).reshape(x.size(0), -1)
            h = F.relu(self.fc1(h))
            h = F.relu(self.fc2(h))
            return F.relu(self.fc3(h))