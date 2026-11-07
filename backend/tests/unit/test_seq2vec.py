"""
Unit Tests for Seq2Vec and R-GCN ML Models
"""
import pytest
import torch
from ml.seq2vec.model import Seq2VecModel
from ml.rgcn.model import RailwayRGCN

def test_seq2vec_forward():
    model = Seq2VecModel(num_entity_types=60)
    batch_size = 2
    seq_len = 5
    types = torch.randint(0, 50, (batch_size, seq_len))
    positions = torch.randn(batch_size, seq_len, 4)
    attributes = torch.randn(batch_size, seq_len, 8)
    mask = torch.ones(batch_size, seq_len, dtype=torch.bool)

    output = model(types, positions, attributes, mask)
    embedding = output["embedding"]
    assert embedding.shape == (batch_size, 256)
    # Check L2 normalization
    norms = torch.norm(embedding, p=2, dim=-1)
    assert torch.allclose(norms, torch.ones_like(norms), atol=1e-5)

def test_rgcn_forward():
    model = RailwayRGCN()
    num_nodes = 8
    num_edges = 12
    x = torch.randn(num_nodes, 256)
    edge_index = torch.randint(0, num_nodes, (2, num_edges))
    edge_type = torch.randint(0, 8, (num_edges,))

    out = model(x, edge_index, edge_type)
    assert out.shape == (num_nodes, 256)
