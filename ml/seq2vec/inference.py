"""
Inference helper for Seq2Vec model.

Provides a simple interface to load a trained model checkpoint
and encode entity sequences to 256-dim structural embeddings.
"""

import logging
from pathlib import Path
from typing import Any, Optional

import torch
import numpy as np

from .model import Seq2VecModel
from .dataset import (
    EntitySequenceDataset,
    collate_entity_sequences,
    DEFAULT_ENTITY_TYPES,
)

logger = logging.getLogger(__name__)


class Seq2VecInference:
    """Inference wrapper for the Seq2Vec structural embedding model.

    Loads a trained checkpoint and provides methods for encoding
    entity sequences to fixed 256-dim embeddings.

    Args:
        checkpoint_path: Path to a saved model checkpoint (.pt file).
        device: Device to run inference on ('auto', 'cpu', 'cuda').
        entity_vocab: Optional custom entity type vocabulary.
    """

    def __init__(
        self,
        checkpoint_path: str | Path,
        device: str = "auto",
        entity_vocab: Optional[dict[str, int]] = None,
    ) -> None:
        self.checkpoint_path = Path(checkpoint_path)

        if device == "auto":
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        self.entity_vocab = entity_vocab or {
            name: idx for idx, name in enumerate(DEFAULT_ENTITY_TYPES)
        }

        self.model = self._load_model()

    def _load_model(self) -> Seq2VecModel:
        """Load model from checkpoint.

        Returns:
            Loaded Seq2VecModel in eval mode.

        Raises:
            FileNotFoundError: If checkpoint file doesn't exist.
            RuntimeError: If checkpoint format is invalid.
        """
        if not self.checkpoint_path.exists():
            raise FileNotFoundError(
                f"Checkpoint not found: {self.checkpoint_path}. "
                "Train the model first using train.py."
            )

        checkpoint = torch.load(
            self.checkpoint_path, map_location=self.device, weights_only=False
        )

        config = checkpoint.get("config", {})

        model = Seq2VecModel(
            num_entity_types=config.get("num_entity_types", 128),
            num_classes=config.get("num_classes", 0),
            output_dim=config.get("output_dim", 256),
        )

        model.load_state_dict(checkpoint["model_state_dict"], strict=False)
        model.to(self.device)
        model.eval()

        logger.info(
            f"Loaded Seq2Vec model from {self.checkpoint_path} "
            f"(epoch {checkpoint.get('epoch', '?')}, "
            f"val_loss={checkpoint.get('val_loss', '?')})"
        )

        return model

    @torch.no_grad()
    def encode(
        self,
        entity_sequences: list[dict[str, Any]],
        batch_size: int = 32,
    ) -> np.ndarray:
        """Encode entity sequences to 256-dim structural embeddings.

        Args:
            entity_sequences: List of sequence dicts, each with 'entities' key
                containing list of entity dicts with 'type', 'x', 'y', 'w', 'h',
                'attributes' fields.
            batch_size: Inference batch size.

        Returns:
            (N, 256) numpy array of L2-normalized embeddings.
        """
        # Wrap in dataset format
        samples = []
        for seq in entity_sequences:
            if "entities" in seq:
                samples.append(seq)
            else:
                # If raw entity list passed, wrap it
                samples.append({"entities": seq, "label": -1})

        dataset = EntitySequenceDataset(
            data=samples,
            entity_vocab=self.entity_vocab,
        )

        dataloader = torch.utils.data.DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=False,
            collate_fn=collate_entity_sequences,
            num_workers=0,
        )

        all_embeddings: list[np.ndarray] = []

        for batch in dataloader:
            entity_types = batch["entity_types"].to(self.device)
            positions = batch["positions"].to(self.device)
            attributes = batch["attributes"].to(self.device)
            mask = batch["mask"].to(self.device)

            output = self.model(
                entity_types=entity_types,
                positions=positions,
                attributes=attributes,
                mask=mask,
                return_logits=False,
            )

            embeddings = output["embedding"].cpu().numpy()
            all_embeddings.append(embeddings)

        return np.concatenate(all_embeddings, axis=0)

    @torch.no_grad()
    def encode_single(self, entities: list[dict[str, Any]]) -> np.ndarray:
        """Encode a single entity sequence.

        Args:
            entities: List of entity dicts.

        Returns:
            (256,) numpy array — the L2-normalized embedding.
        """
        result = self.encode([{"entities": entities}], batch_size=1)
        return result[0]

    def get_embedding_dim(self) -> int:
        """Return the output embedding dimension."""
        return self.model.get_embedding_dim()
