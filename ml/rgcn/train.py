"""
SIP Intelligence — R-GCN Training Pipeline
"""
from __future__ import annotations

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from ml.rgcn.model import RailwayRGCN
from ml.rgcn.dataset import RailwayGraphDataset


def train_rgcn(epochs: int = 5, lr: float = 1e-3, device: str = "cpu"):
    """
    Train R-GCN on verified graph data or synthetic test harness.
    """
    dataset = RailwayGraphDataset(num_samples=20)
    model = RailwayRGCN(in_channels=256, hidden_channels=256, out_channels=256).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()

    model.train()
    print(f"Starting R-GCN training on {device}...")
    for epoch in range(epochs):
        total_loss = 0.0
        for sample in dataset:
            x = sample["x"].to(device)
            edge_index = sample["edge_index"].to(device)
            edge_type = sample["edge_type"].to(device)
            target = torch.tensor([sample["label"]], dtype=torch.long, device=device)

            optimizer.zero_grad()
            emb = model(x, edge_index, edge_type)
            # Classification head
            logits = torch.mean(emb, dim=0, keepdim=True)[:, :4]
            loss = criterion(logits, target)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        avg_loss = total_loss / len(dataset)
        print(f"Epoch {epoch+1}/{epochs} - Loss: {avg_loss:.4f}")

    print("R-GCN training verification completed.")
    return model


if __name__ == "__main__":
    train_rgcn()

