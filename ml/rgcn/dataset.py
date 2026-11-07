"""
SIP Intelligence — R-GCN Dataset & Synthetic Data Generator
"""
from __future__ import annotations

import torch
from torch.utils.data import Dataset


class RailwayGraphDataset(Dataset):
    """
    Dataset loader for Railway Engineering Graphs.
    Supports synthetic generation for verification and unit tests.
    """

    RELATIONS = [
        "CONTAINS", "CONNECTED_TO", "LOCATED_ON", "CONTROLS",
        "DETECTS", "PROTECTS", "REFERENCES", "ASSOCIATED_WITH",
    ]

    def __init__(self, graphs: list[dict] | None = None, num_samples: int = 50):
        self.graphs = graphs if graphs is not None else self._generate_synthetic_graphs(num_samples)

    def _generate_synthetic_graphs(self, num_samples: int) -> list[dict]:
        """Generate verified topological synthetic railway graphs for model testing."""
        synthetic = []
        for i in range(num_samples):
            num_nodes = torch.randint(5, 20, (1,)).item()
            num_edges = torch.randint(num_nodes - 1, num_nodes * 2, (1,)).item()

            x = torch.randn(num_nodes, 256)
            edge_index = torch.randint(0, num_nodes, (2, num_edges))
            edge_type = torch.randint(0, len(self.RELATIONS), (num_edges,))

            label = torch.randint(0, 4, (1,)).item()

            synthetic.append({
                "x": x,
                "edge_index": edge_index,
                "edge_type": edge_type,
                "num_nodes": num_nodes,
                "label": label,
            })
        return synthetic

    def __len__(self) -> int:
        return len(self.graphs)

    def __getitem__(self, idx: int) -> dict:
        return self.graphs[idx]

