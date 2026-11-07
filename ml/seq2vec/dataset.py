"""
Dataset and data utilities for Seq2Vec model training and inference.

Handles loading entity sequences from JSON format, encoding entity types,
positions, and attributes, and provides collation with padding.

Includes a synthetic data generator for unit testing.
"""

import json
import random
from pathlib import Path
from typing import Any, Optional

import torch
from torch.utils.data import Dataset


# Default entity type vocabulary for SIP engineering
DEFAULT_ENTITY_TYPES: list[str] = [
    "<PAD>",
    "<UNK>",
    "SIGNAL",
    "POINT",
    "TRACK_CIRCUIT",
    "LEVEL_CROSSING",
    "BOARD",
    "INDICATOR",
    "GRADIENT",
    "OPERATION_PLACE",
    "LEVER_FRAME",
    "KEY_LOCK",
    "GATE_GOOMTY",
    "DIRECTION",
    "LINE",
    "EKT_RKT",
    "AXLE_COUNTER",
    "TRAP_POINT",
    "DEAD_END",
    "SAND_HUMP",
    "BLOCK_INSTRUMENT",
    "RELAY_ROOM",
    "LOCATION_BOX",
    "CABLE_ROUTE",
    "POWER_SUPPLY",
    "TELEPHONE",
    "TRACK_SECTION",
    "STATION_SECTION",
    "OVERLAP",
    "ROUTE",
    "ASPECT",
]


class EntitySequenceDataset(Dataset):
    """PyTorch Dataset for engineering entity sequences.

    Each sample is a sequence of entities with:
        - entity_type: categorical type index
        - position: (x, y, width, height) normalized coordinates
        - attributes: vector of 8 attribute features
        - label: optional classification target

    Args:
        data_path: Path to JSON file containing entity sequences.
        entity_vocab: Mapping from entity type names to indices.
        max_seq_len: Maximum sequence length (longer sequences are truncated).
        num_attributes: Number of attribute features per entity (default: 8).
    """

    def __init__(
        self,
        data_path: Optional[str | Path] = None,
        entity_vocab: Optional[dict[str, int]] = None,
        max_seq_len: int = 128,
        num_attributes: int = 8,
        data: Optional[list[dict[str, Any]]] = None,
    ) -> None:
        super().__init__()
        self.max_seq_len = max_seq_len
        self.num_attributes = num_attributes

        # Build vocabulary
        if entity_vocab is not None:
            self.entity_vocab = entity_vocab
        else:
            self.entity_vocab = {
                name: idx for idx, name in enumerate(DEFAULT_ENTITY_TYPES)
            }

        self.num_entity_types = len(self.entity_vocab)

        # Load data
        if data is not None:
            self.samples = data
        elif data_path is not None:
            self.samples = self._load_json(Path(data_path))
        else:
            self.samples = []

    def _load_json(self, path: Path) -> list[dict[str, Any]]:
        """Load entity sequences from a JSON file.

        Expected JSON format:
        [
            {
                "id": "drawing_001",
                "entities": [
                    {
                        "type": "SIGNAL",
                        "x": 0.1, "y": 0.2, "w": 0.05, "h": 0.08,
                        "attributes": [0.5, 1.0, 0.0, ...]
                    },
                    ...
                ],
                "label": 0  // optional classification label
            },
            ...
        ]
        """
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict) and "sequences" in data:
            return data["sequences"]
        return data

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> dict[str, torch.Tensor]:
        """Get a single sample.

        Returns:
            Dict with keys:
                'entity_types': (seq_len,) LongTensor of entity type indices.
                'positions': (seq_len, 4) float tensor of position features.
                'attributes': (seq_len, num_attributes) float tensor.
                'mask': (seq_len,) boolean mask.
                'label': scalar LongTensor if available, else -1.
                'length': scalar int of actual sequence length.
        """
        sample = self.samples[idx]
        entities = sample.get("entities", [])

        # Truncate if needed
        if len(entities) > self.max_seq_len:
            entities = entities[: self.max_seq_len]

        seq_len = len(entities)

        # Encode entity types
        entity_types = torch.zeros(seq_len, dtype=torch.long)
        positions = torch.zeros(seq_len, 4, dtype=torch.float32)
        attributes = torch.zeros(seq_len, self.num_attributes, dtype=torch.float32)

        for i, entity in enumerate(entities):
            # Entity type
            etype = entity.get("type", "<UNK>")
            entity_types[i] = self.entity_vocab.get(
                etype, self.entity_vocab.get("<UNK>", 1)
            )

            # Position features (normalized)
            positions[i, 0] = float(entity.get("x", 0.0))
            positions[i, 1] = float(entity.get("y", 0.0))
            positions[i, 2] = float(entity.get("w", 0.0))
            positions[i, 3] = float(entity.get("h", 0.0))

            # Attribute features
            attrs = entity.get("attributes", [])
            for j in range(min(len(attrs), self.num_attributes)):
                attributes[i, j] = float(attrs[j])

        # Mask (all True for actual entities)
        mask = torch.ones(seq_len, dtype=torch.bool)

        # Label
        label = torch.tensor(sample.get("label", -1), dtype=torch.long)

        return {
            "entity_types": entity_types,
            "positions": positions,
            "attributes": attributes,
            "mask": mask,
            "label": label,
            "length": torch.tensor(seq_len, dtype=torch.long),
        }


def collate_entity_sequences(
    batch: list[dict[str, torch.Tensor]],
) -> dict[str, torch.Tensor]:
    """Collate function for DataLoader — pads sequences to batch max length.

    Args:
        batch: List of sample dicts from EntitySequenceDataset.

    Returns:
        Batched dict with padded tensors.
    """
    max_len = max(item["length"].item() for item in batch)
    batch_size = len(batch)

    # Get attribute dim from first sample
    num_attrs = batch[0]["attributes"].shape[-1]

    # Initialize padded tensors
    entity_types = torch.zeros(batch_size, max_len, dtype=torch.long)
    positions = torch.zeros(batch_size, max_len, 4, dtype=torch.float32)
    attributes = torch.zeros(batch_size, max_len, num_attrs, dtype=torch.float32)
    mask = torch.zeros(batch_size, max_len, dtype=torch.bool)
    labels = torch.stack([item["label"] for item in batch])
    lengths = torch.stack([item["length"] for item in batch])

    for i, item in enumerate(batch):
        seq_len = item["length"].item()
        entity_types[i, :seq_len] = item["entity_types"]
        positions[i, :seq_len] = item["positions"]
        attributes[i, :seq_len] = item["attributes"]
        mask[i, :seq_len] = item["mask"]

    return {
        "entity_types": entity_types,
        "positions": positions,
        "attributes": attributes,
        "mask": mask,
        "labels": labels,
        "lengths": lengths,
    }


def generate_synthetic_data(
    num_samples: int = 100,
    min_seq_len: int = 5,
    max_seq_len: int = 50,
    num_classes: int = 10,
    entity_types: Optional[list[str]] = None,
    seed: int = 42,
) -> list[dict[str, Any]]:
    """Generate synthetic entity sequence data for unit testing.

    Creates random entity sequences with realistic structure for
    testing the Seq2Vec pipeline without real training data.

    Args:
        num_samples: Number of samples to generate.
        min_seq_len: Minimum sequence length.
        max_seq_len: Maximum sequence length.
        num_classes: Number of distinct class labels.
        entity_types: List of entity type names. Uses defaults if None.
        seed: Random seed for reproducibility.

    Returns:
        List of sample dicts compatible with EntitySequenceDataset.
    """
    rng = random.Random(seed)
    if entity_types is None:
        entity_types = [et for et in DEFAULT_ENTITY_TYPES if et not in ("<PAD>", "<UNK>")]

    samples: list[dict[str, Any]] = []
    for i in range(num_samples):
        seq_len = rng.randint(min_seq_len, max_seq_len)
        entities = []
        for j in range(seq_len):
            etype = rng.choice(entity_types)
            entities.append(
                {
                    "type": etype,
                    "x": round(rng.random(), 4),
                    "y": round(rng.random(), 4),
                    "w": round(rng.uniform(0.01, 0.15), 4),
                    "h": round(rng.uniform(0.01, 0.15), 4),
                    "attributes": [
                        round(rng.gauss(0.0, 1.0), 4) for _ in range(8)
                    ],
                }
            )

        samples.append(
            {
                "id": f"synthetic_{i:05d}",
                "entities": entities,
                "label": rng.randint(0, num_classes - 1),
            }
        )

    return samples
