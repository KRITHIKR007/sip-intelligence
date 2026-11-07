"""
SIP Intelligence — R-GCN Inference Service
"""
from __future__ import annotations

import torch
import numpy as np
from ml.rgcn.model import RailwayRGCN


class RGCNInference:
    """Inference helper for generating graph-level and node-level structural embeddings."""

    def __init__(self, model_path: str | None = None, device: str = "cpu"):
        self.device = device
        self.model = RailwayRGCN(in_channels=256, hidden_channels=256, out_channels=256).to(device)
        if model_path:
            self.model.load_state_dict(torch.load(model_path, map_location=device))
        self.model.eval()

    def embed_graph(self, x: np.ndarray, edge_index: np.ndarray, edge_type: np.ndarray) -> np.ndarray:
        t_x = torch.tensor(x, dtype=torch.float32, device=self.device)
        t_edge_index = torch.tensor(edge_index, dtype=torch.long, device=self.device)
        t_edge_type = torch.tensor(edge_type, dtype=torch.long, device=self.device)

        with torch.no_grad():
            emb = self.model(t_x, t_edge_index, t_edge_type)
        return emb.cpu().numpy()

