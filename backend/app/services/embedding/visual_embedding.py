"""
SIP Intelligence — SigLIP2 Visual Embedding Service
"""
from __future__ import annotations

from typing import Optional

import numpy as np
import structlog
from PIL import Image

from app.core.config import settings

logger = structlog.get_logger()


class VisualEmbeddingService:
    """Visual embedding using SigLIP2 for image-text retrieval."""

    _model = None
    _processor = None
    _model_name = settings.visual_embedding_model
    _dimension: Optional[int] = None

    @classmethod
    def _load_model(cls):
        if cls._model is None:
            try:
                from transformers import AutoModel, AutoProcessor
                cls._processor = AutoProcessor.from_pretrained(cls._model_name)
                cls._model = AutoModel.from_pretrained(cls._model_name)
                cls._model.eval()
                cls._model.to(settings.visual_embedding_device)
                # Detect actual output dimension
                import torch
                dummy = cls._processor(
                    images=Image.new("RGB", (224, 224)),
                    return_tensors="pt",
                )
                with torch.no_grad():
                    out = cls._model.get_image_features(
                        **{k: v.to(settings.visual_embedding_device) for k, v in dummy.items() if k != "input_ids"}
                    )
                    cls._dimension = out.shape[-1]
                logger.info(
                    "Visual embedding model loaded",
                    model=cls._model_name,
                    dimension=cls._dimension,
                )
            except Exception as e:
                logger.error("Failed to load visual embedding model", error=str(e))
                raise
        return cls._model, cls._processor

    @classmethod
    def encode_images(cls, images: list[Image.Image]) -> np.ndarray:
        """Encode PIL images to visual embeddings."""
        import torch

        model, processor = cls._load_model()
        inputs = processor(images=images, return_tensors="pt", padding=True)
        inputs = {k: v.to(settings.visual_embedding_device) for k, v in inputs.items()}

        with torch.no_grad():
            embeddings = model.get_image_features(**inputs)
            embeddings = embeddings / embeddings.norm(dim=-1, keepdim=True)

        return embeddings.cpu().numpy().astype(np.float32)

    @classmethod
    def encode_text(cls, texts: list[str]) -> np.ndarray:
        """Encode text queries for image search."""
        import torch

        model, processor = cls._load_model()
        inputs = processor(text=texts, return_tensors="pt", padding=True, truncation=True)
        inputs = {k: v.to(settings.visual_embedding_device) for k, v in inputs.items()}

        with torch.no_grad():
            embeddings = model.get_text_features(**inputs)
            embeddings = embeddings / embeddings.norm(dim=-1, keepdim=True)

        return embeddings.cpu().numpy().astype(np.float32)

    @classmethod
    def get_dimension(cls) -> int:
        if cls._dimension is None:
            cls._load_model()
        return cls._dimension or 768

    @classmethod
    def get_model_info(cls) -> dict:
        return {
            "name": cls._model_name,
            "dimension": cls.get_dimension(),
            "device": settings.visual_embedding_device,
        }

