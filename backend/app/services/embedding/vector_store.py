"""
SIP Intelligence — Qdrant Vector Store Service
"""
from __future__ import annotations

import uuid
from typing import Any, Optional

import structlog
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from app.core.config import settings

logger = structlog.get_logger()

# Collection definitions
COLLECTIONS = {
    "sip_text_embeddings": {
        "size": settings.text_embedding_dim,  # 1024
        "distance": Distance.COSINE,
    },
    "sip_visual_embeddings": {
        "size": 768,  # SigLIP2 default; updated at runtime
        "distance": Distance.COSINE,
    },
    "sip_structural_embeddings": {
        "size": 256,  # Seq2Vec output
        "distance": Distance.COSINE,
    },
    "sip_entity_embeddings": {
        "size": 256,  # R-GCN output
        "distance": Distance.COSINE,
    },
}


class VectorStoreService:
    """Qdrant vector database client wrapper."""

    def __init__(self):
        self.client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            api_key=settings.qdrant_api_key or None,
        )

    def ensure_collections(self):
        """Create collections if they don't exist."""
        existing = {c.name for c in self.client.get_collections().collections}
        for name, config in COLLECTIONS.items():
            if name not in existing:
                self.client.create_collection(
                    collection_name=name,
                    vectors_config=VectorParams(
                        size=config["size"],
                        distance=config["distance"],
                    ),
                )
                logger.info("Created Qdrant collection", name=name, size=config["size"])

    def upsert(
        self,
        collection: str,
        point_id: str,
        vector: list[float],
        payload: dict[str, Any],
    ):
        """Insert or update a single vector with metadata."""
        self.client.upsert(
            collection_name=collection,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload,
                )
            ],
        )

    def upsert_batch(
        self,
        collection: str,
        ids: list[str],
        vectors: list[list[float]],
        payloads: list[dict[str, Any]],
    ):
        """Batch upsert vectors."""
        points = [
            PointStruct(id=pid, vector=vec, payload=pay)
            for pid, vec, pay in zip(ids, vectors, payloads)
        ]
        self.client.upsert(collection_name=collection, points=points)

    def search(
        self,
        collection: str,
        query_vector: list[float],
        top_k: int = 10,
        filters: Optional[dict[str, str]] = None,
    ) -> list[dict]:
        """Search for similar vectors with optional access filters."""
        qdrant_filter = None
        if filters:
            conditions = [
                FieldCondition(key=k, match=MatchValue(value=v))
                for k, v in filters.items()
            ]
            qdrant_filter = Filter(must=conditions)

        results = self.client.search(
            collection_name=collection,
            query_vector=query_vector,
            limit=top_k,
            query_filter=qdrant_filter,
        )

        return [
            {
                "id": str(r.id),
                "score": r.score,
                "payload": r.payload or {},
            }
            for r in results
        ]

    def delete(self, collection: str, point_ids: list[str]):
        """Delete points by ID."""
        from qdrant_client.models import PointIdsList
        self.client.delete(
            collection_name=collection,
            points_selector=PointIdsList(points=point_ids),
        )

