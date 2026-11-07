"""
SIP Intelligence — BGE-M3 Text Embedding Service
"""
from __future__ import annotations

from typing import Optional

import numpy as np
import structlog

from app.core.config import settings

logger = structlog.get_logger()


class TextEmbeddingService:
    """Text embedding using BAAI/bge-m3 via sentence-transformers."""

    _model = None
    _model_name = settings.text_embedding_model
    _dimension = settings.text_embedding_dim

    @classmethod
    def _load_model(cls):
        if cls._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                cls._model = SentenceTransformer(
                    cls._model_name,
                    device=settings.text_embedding_device,
                )
                logger.info("Text embedding model loaded", model=cls._model_name)
            except Exception as e:
                logger.error("Failed to load text embedding model", error=str(e))
                raise
        return cls._model

    @classmethod
    def encode(
        cls,
        texts: list[str],
        batch_size: int = settings.text_embedding_batch_size,
        normalize: bool = True,
    ) -> np.ndarray:
        """Encode texts to dense vectors."""
        model = cls._load_model()
        embeddings = model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=normalize,
            show_progress_bar=False,
        )
        return np.array(embeddings, dtype=np.float32)

    @classmethod
    def encode_single(cls, text: str) -> np.ndarray:
        """Encode a single text."""
        return cls.encode([text])[0]

    @classmethod
    def get_model_info(cls) -> dict:
        return {
            "name": cls._model_name,
            "dimension": cls._dimension,
            "device": settings.text_embedding_device,
            "normalize": True,
            "similarity": "cosine",
        }

