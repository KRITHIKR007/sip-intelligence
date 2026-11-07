"""
Seq2Vec Model: BiLSTM + Attention for structural entity embeddings.

Architecture:
    Entity Type Embedding (128d) + Positional Features (32d) + Attribute Features (32d)
    → Combined Input (192d)
    → BiLSTM (2 layers, 256 hidden per direction)
    → Attention Pooling (512d → weighted sum)
    → Projection (512 → 256, GELU, Dropout)
    → L2 Normalization
    → 256-dim structural embedding
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional


class AttentionPooling(nn.Module):
    """Attention-based pooling over BiLSTM sequence outputs.

    Learns a query vector to compute attention weights over the sequence,
    then returns the weighted sum as a fixed-size representation.

    Args:
        hidden_dim: Dimension of input features (BiLSTM output dim).
    """

    def __init__(self, hidden_dim: int) -> None:
        super().__init__()
        self.attention = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.Tanh(),
            nn.Linear(hidden_dim // 2, 1),
        )

    def forward(
        self, hidden_states: torch.Tensor, mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """Compute attention-weighted sum of hidden states.

        Args:
            hidden_states: (batch, seq_len, hidden_dim) BiLSTM outputs.
            mask: (batch, seq_len) boolean mask, True for valid positions.

        Returns:
            (batch, hidden_dim) pooled representation.
        """
        # Compute attention scores: (batch, seq_len, 1)
        attn_scores = self.attention(hidden_states)

        if mask is not None:
            # Set padded positions to -inf before softmax
            attn_scores = attn_scores.masked_fill(~mask.unsqueeze(-1), float("-inf"))

        # Normalize: (batch, seq_len, 1)
        attn_weights = F.softmax(attn_scores, dim=1)

        # Weighted sum: (batch, hidden_dim)
        pooled = torch.sum(hidden_states * attn_weights, dim=1)
        return pooled


class Seq2VecModel(nn.Module):
    """Seq2Vec model for converting entity sequences to structural embeddings.

    Combines entity type embeddings, positional features, and attribute features
    through a BiLSTM encoder with attention pooling to produce fixed-size
    256-dim L2-normalized embeddings.

    Args:
        num_entity_types: Number of distinct entity types in the vocabulary.
        entity_embed_dim: Dimension of entity type embeddings (default: 128).
        position_dim: Dimension of positional features (default: 32).
        attribute_dim: Dimension of attribute features (default: 32).
        lstm_hidden: Hidden size per LSTM direction (default: 256).
        lstm_layers: Number of BiLSTM layers (default: 2).
        output_dim: Final embedding dimension (default: 256).
        dropout: Dropout probability (default: 0.2).
        num_classes: Number of classification classes, 0 to disable head (default: 0).
    """

    def __init__(
        self,
        num_entity_types: int = 128,
        entity_embed_dim: int = 128,
        position_dim: int = 32,
        attribute_dim: int = 32,
        lstm_hidden: int = 256,
        lstm_layers: int = 2,
        output_dim: int = 256,
        dropout: float = 0.2,
        num_classes: int = 0,
    ) -> None:
        super().__init__()

        self.entity_embed_dim = entity_embed_dim
        self.position_dim = position_dim
        self.attribute_dim = attribute_dim
        self.output_dim = output_dim

        # Input dimension: entity_embed + position + attribute
        combined_input_dim = entity_embed_dim + position_dim + attribute_dim  # 192

        # Entity type embedding
        self.entity_embedding = nn.Embedding(
            num_embeddings=num_entity_types,
            embedding_dim=entity_embed_dim,
            padding_idx=0,
        )

        # Positional feature projection (from raw position features to position_dim)
        self.position_proj = nn.Sequential(
            nn.Linear(4, position_dim),  # 4 raw features: x, y, w, h
            nn.LayerNorm(position_dim),
            nn.GELU(),
        )

        # Attribute feature projection
        self.attribute_proj = nn.Sequential(
            nn.Linear(8, attribute_dim),  # 8 raw attribute features
            nn.LayerNorm(attribute_dim),
            nn.GELU(),
        )

        # BiLSTM encoder
        self.lstm = nn.LSTM(
            input_size=combined_input_dim,
            hidden_size=lstm_hidden,
            num_layers=lstm_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if lstm_layers > 1 else 0.0,
        )

        # BiLSTM output dim = 2 * lstm_hidden = 512
        bilstm_output_dim = 2 * lstm_hidden

        # Attention pooling
        self.attention_pool = AttentionPooling(bilstm_output_dim)

        # Projection head: 512 → 256
        self.projection = nn.Sequential(
            nn.Linear(bilstm_output_dim, output_dim),
            nn.GELU(),
            nn.Dropout(dropout),
        )

        # Optional classification head
        self.num_classes = num_classes
        if num_classes > 0:
            self.classifier = nn.Linear(output_dim, num_classes)
        else:
            self.classifier = None

        # Layer norm before final output
        self.output_norm = nn.LayerNorm(output_dim)

        self._init_weights()

    def _init_weights(self) -> None:
        """Initialize weights using Xavier uniform for linear layers."""
        for name, param in self.named_parameters():
            if "weight" in name and param.dim() >= 2:
                nn.init.xavier_uniform_(param)
            elif "bias" in name:
                nn.init.zeros_(param)

    def forward(
        self,
        entity_types: torch.LongTensor,
        positions: torch.Tensor,
        attributes: torch.Tensor,
        mask: Optional[torch.BoolTensor] = None,
        return_logits: bool = False,
    ) -> dict[str, torch.Tensor]:
        """Forward pass.

        Args:
            entity_types: (batch, seq_len) entity type indices.
            positions: (batch, seq_len, 4) position features [x, y, w, h].
            attributes: (batch, seq_len, 8) attribute features.
            mask: (batch, seq_len) boolean mask, True for valid positions.
            return_logits: If True and classifier exists, also return class logits.

        Returns:
            Dict with keys:
                'embedding': (batch, 256) L2-normalized structural embedding.
                'logits': (batch, num_classes) if return_logits=True and classifier exists.
        """
        batch_size, seq_len = entity_types.shape

        # Embed entity types: (batch, seq_len, 128)
        entity_emb = self.entity_embedding(entity_types)

        # Project positions: (batch, seq_len, 32)
        pos_emb = self.position_proj(positions)

        # Project attributes: (batch, seq_len, 32)
        attr_emb = self.attribute_proj(attributes)

        # Concatenate: (batch, seq_len, 192)
        combined = torch.cat([entity_emb, pos_emb, attr_emb], dim=-1)

        # BiLSTM encoding: (batch, seq_len, 512)
        if mask is not None:
            # Pack padded sequence for efficient computation
            lengths = mask.sum(dim=1).cpu()
            packed = nn.utils.rnn.pack_padded_sequence(
                combined, lengths, batch_first=True, enforce_sorted=False
            )
            lstm_out, _ = self.lstm(packed)
            lstm_out, _ = nn.utils.rnn.pad_packed_sequence(
                lstm_out, batch_first=True, total_length=seq_len
            )
        else:
            lstm_out, _ = self.lstm(combined)

        # Attention pooling: (batch, 512)
        pooled = self.attention_pool(lstm_out, mask)

        # Projection: (batch, 256)
        projected = self.projection(pooled)
        projected = self.output_norm(projected)

        # L2 normalization
        embedding = F.normalize(projected, p=2, dim=-1)

        result: dict[str, torch.Tensor] = {"embedding": embedding}

        # Optional classification
        if return_logits and self.classifier is not None:
            logits = self.classifier(projected)
            result["logits"] = logits

        return result

    def get_embedding_dim(self) -> int:
        """Return the output embedding dimension."""
        return self.output_dim
