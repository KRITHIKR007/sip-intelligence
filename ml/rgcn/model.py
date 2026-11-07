"""
SIP Intelligence — Relational Graph Convolutional Network (R-GCN)
PyTorch Geometric implementation for Railway Knowledge Graph embeddings.
"""
from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

try:
    from torch_geometric.nn import RGCNConv, global_mean_pool
except ImportError:
    RGCNConv = None
    global_mean_pool = None


class RailwayRGCN(nn.Module):
    """
    R-GCN Architecture:
    - Input features: 256
    - Two relational graph convolution layers
    - Hidden dimension: 256
    - Relation-aware aggregation
    - Attention pooling / global pooling
    - Output dimension: 256
    """

    def __init__(
        self,
        in_channels: int = 256,
        hidden_channels: int = 256,
        out_channels: int = 256,
        num_relations: int = 16,
        num_bases: int = 4,
        dropout: float = 0.2,
    ):
        super().__init__()
        self.in_channels = in_channels
        self.hidden_channels = hidden_channels
        self.out_channels = out_channels
        self.num_relations = num_relations
        self.dropout = dropout

        if RGCNConv is not None:
            self.conv1 = RGCNConv(in_channels, hidden_channels, num_relations, num_bases=num_bases)
            self.conv2 = RGCNConv(hidden_channels, out_channels, num_relations, num_bases=num_bases)
        else:
            self.conv1 = nn.Linear(in_channels, hidden_channels)
            self.conv2 = nn.Linear(hidden_channels, out_channels)

        self.attn_pool = nn.Sequential(
            nn.Linear(out_channels, 64),
            nn.Tanh(),
            nn.Linear(64, 1),
        )

        self.projection = nn.Sequential(
            nn.Linear(out_channels, out_channels),
            nn.GELU(),
            nn.Dropout(dropout),
        )

    def forward(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        edge_type: torch.Tensor,
        batch: torch.Tensor | None = None,
    ) -> torch.Tensor:
        """
        Forward pass.
        Args:
            x: Node feature tensor [num_nodes, in_channels]
            edge_index: Graph connectivity [2, num_edges]
            edge_type: Edge relation types [num_edges]
            batch: Batch vector mapping nodes to graphs [num_nodes]
        Returns:
            Normalized graph-level or node-level embedding [batch_size, out_channels]
        """
        if RGCNConv is not None:
            h = self.conv1(x, edge_index, edge_type)
            h = F.relu(h)
            h = F.dropout(h, p=self.dropout, training=self.training)
            h = self.conv2(h, edge_index, edge_type)
        else:
            h = F.relu(self.conv1(x))
            h = self.conv2(h)

        if batch is not None:
            attn_weights = F.softmax(self.attn_pool(h), dim=0)
            if global_mean_pool is not None:
                pooled = global_mean_pool(h * attn_weights, batch)
            else:
                pooled = torch.mean(h, dim=0, keepdim=True)
            out = self.projection(pooled)
        else:
            out = self.projection(h)

        # L2 normalize
        out = F.normalize(out, p=2, dim=-1)
        return out

