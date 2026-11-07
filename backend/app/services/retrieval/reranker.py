"""
SIP Intelligence — BGE Reranker v2 M3
"""
from __future__ import annotations

import structlog
from app.core.config import settings

logger = structlog.get_logger()


class RerankerService:
    """Cross-encoder reranking using BAAI/bge-reranker-v2-m3."""

    _model = None

    @classmethod
    def _load_model(cls):
        if cls._model is None:
            try:
                from sentence_transformers import CrossEncoder
                cls._model = CrossEncoder(
                    settings.reranker_model,
                    device=settings.reranker_device,
                )
                logger.info("Reranker loaded", model=settings.reranker_model)
            except Exception as e:
                logger.error("Failed to load reranker", error=str(e))
                raise
        return cls._model

    @classmethod
    def rerank(
        cls,
        query: str,
        documents: list[dict],
        top_k: int = 10,
        text_key: str = "text",
    ) -> list[dict]:
        """
        Rerank candidate documents against a query.

        Args:
            query: The search query.
            documents: List of dicts, each with at least a 'text' key.
            top_k: Number of results to return.
            text_key: Key to use for document text.

        Returns:
            Reranked list of documents with added 'rerank_score'.
        """
        if not documents:
            return []

        model = cls._load_model()

        pairs = [(query, doc.get(text_key, "")) for doc in documents]
        scores = model.predict(pairs, show_progress_bar=False)

        for doc, score in zip(documents, scores):
            doc["rerank_score"] = float(score)

        reranked = sorted(documents, key=lambda d: d["rerank_score"], reverse=True)
        return reranked[:top_k]

