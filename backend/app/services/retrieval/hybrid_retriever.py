"""
SIP Intelligence — Hybrid Retrieval Engine
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np
import structlog

from app.core.config import settings

logger = structlog.get_logger()


@dataclass
class RetrievalResult:
    """A single retrieval result with source metadata."""
    document_id: str
    chunk_id: str = ""
    text: str = ""
    score: float = 0.0
    source_type: str = ""  # dense, bm25, visual, structural, graph
    page_number: Optional[int] = None
    metadata: dict = field(default_factory=dict)


class HybridRetriever:
    """
    5-channel hybrid retrieval engine with Reciprocal Rank Fusion.

    Channels:
    1. Dense text retrieval (BGE-M3 → Qdrant)
    2. BM25 keyword retrieval (OpenSearch)
    3. Visual retrieval (SigLIP2 → Qdrant)
    4. Structural retrieval (Seq2Vec → Qdrant)
    5. Graph retrieval (Neo4j)
    """

    # Query-type-specific weight profiles
    WEIGHT_PROFILES = {
        "document_qa": {"dense": 0.35, "bm25": 0.25, "visual": 0.10, "structural": 0.10, "graph": 0.20},
        "symbol_identification": {"dense": 0.10, "bm25": 0.10, "visual": 0.40, "structural": 0.20, "graph": 0.20},
        "visual_search": {"dense": 0.05, "bm25": 0.05, "visual": 0.60, "structural": 0.15, "graph": 0.15},
        "standards_lookup": {"dense": 0.40, "bm25": 0.35, "visual": 0.00, "structural": 0.05, "graph": 0.20},
        "engineering_relationship": {"dense": 0.15, "bm25": 0.10, "visual": 0.10, "structural": 0.25, "graph": 0.40},
        "drawing_comparison": {"dense": 0.10, "bm25": 0.05, "visual": 0.25, "structural": 0.35, "graph": 0.25},
        "validation": {"dense": 0.25, "bm25": 0.25, "visual": 0.05, "structural": 0.15, "graph": 0.30},
        "general": {"dense": 0.30, "bm25": 0.20, "visual": 0.20, "structural": 0.15, "graph": 0.15},
    }

    def __init__(self):
        self.top_k = settings.retrieval_top_k
        self.rrf_k = 60  # RRF constant

    async def retrieve(
        self,
        query: str,
        query_type: str = "general",
        top_k: int = 50,
        project_id: Optional[str] = None,
        document_ids: Optional[list[str]] = None,
    ) -> list[RetrievalResult]:
        """Execute hybrid retrieval across all channels."""
        weights = self.WEIGHT_PROFILES.get(query_type, self.WEIGHT_PROFILES["general"])

        all_results: dict[str, list[RetrievalResult]] = {}
        filters = {}
        if project_id:
            filters["project_id"] = project_id

        # Channel 1: Dense text retrieval
        if weights["dense"] > 0:
            try:
                dense_results = await self._dense_retrieval(query, top_k, filters)
                all_results["dense"] = dense_results
            except Exception as e:
                logger.warning("Dense retrieval failed", error=str(e))

        # Channel 2: BM25 retrieval
        if weights["bm25"] > 0:
            try:
                bm25_results = await self._bm25_retrieval(query, top_k, filters)
                all_results["bm25"] = bm25_results
            except Exception as e:
                logger.warning("BM25 retrieval failed", error=str(e))

        # Channel 3: Visual retrieval
        if weights["visual"] > 0:
            try:
                visual_results = await self._visual_retrieval(query, top_k, filters)
                all_results["visual"] = visual_results
            except Exception as e:
                logger.warning("Visual retrieval failed", error=str(e))

        # Channel 4: Structural retrieval
        if weights["structural"] > 0:
            try:
                structural_results = await self._structural_retrieval(query, top_k, filters)
                all_results["structural"] = structural_results
            except Exception as e:
                logger.warning("Structural retrieval failed", error=str(e))

        # Channel 5: Graph retrieval
        if weights["graph"] > 0:
            try:
                graph_results = await self._graph_retrieval(query, filters)
                all_results["graph"] = graph_results
            except Exception as e:
                logger.warning("Graph retrieval failed", error=str(e))

        # Reciprocal Rank Fusion
        fused = self._reciprocal_rank_fusion(all_results, weights)

        # Deduplicate
        seen = set()
        deduped = []
        for r in fused:
            key = (r.document_id, r.chunk_id)
            if key not in seen:
                seen.add(key)
                deduped.append(r)

        return deduped[:top_k]

    def _reciprocal_rank_fusion(
        self,
        channel_results: dict[str, list[RetrievalResult]],
        weights: dict[str, float],
    ) -> list[RetrievalResult]:
        """Combine results using weighted Reciprocal Rank Fusion."""
        # RRF formula: score(d) = Σ weight_i / (k + rank_i(d))
        scores: dict[str, float] = {}
        result_map: dict[str, RetrievalResult] = {}

        for channel, results in channel_results.items():
            w = weights.get(channel, 0.0)
            if w == 0:
                continue

            for rank, result in enumerate(results):
                key = f"{result.document_id}:{result.chunk_id}"
                rrf_score = w / (self.rrf_k + rank + 1)
                scores[key] = scores.get(key, 0.0) + rrf_score

                if key not in result_map:
                    result_map[key] = result

        # Sort by fused score
        sorted_keys = sorted(scores.keys(), key=lambda k: scores[k], reverse=True)

        results = []
        for key in sorted_keys:
            r = result_map[key]
            r.score = scores[key]
            results.append(r)

        return results

    async def _dense_retrieval(self, query: str, top_k: int, filters: dict) -> list[RetrievalResult]:
        """Dense vector retrieval via BGE-M3 + Qdrant."""
        from app.services.embedding.text_embedding import TextEmbeddingService
        from app.services.embedding.vector_store import VectorStoreService

        query_vec = TextEmbeddingService.encode_single(query).tolist()
        vs = VectorStoreService()
        results = vs.search("sip_text_embeddings", query_vec, top_k, filters or None)

        return [
            RetrievalResult(
                document_id=r["payload"].get("document_id", ""),
                chunk_id=r["id"],
                text=r["payload"].get("text", ""),
                score=r["score"],
                source_type="dense",
                page_number=r["payload"].get("page_number"),
                metadata=r["payload"],
            )
            for r in results
        ]

    async def _bm25_retrieval(self, query: str, top_k: int, filters: dict) -> list[RetrievalResult]:
        """BM25 keyword retrieval via OpenSearch."""
        from app.services.retrieval.search_service import SearchService

        svc = SearchService()
        results = svc.search(query, top_k, filters)
        return [
            RetrievalResult(
                document_id=r.get("document_id", ""),
                chunk_id=r.get("id", ""),
                text=r.get("text", ""),
                score=r.get("score", 0.0),
                source_type="bm25",
                page_number=r.get("page_number"),
            )
            for r in results
        ]

    async def _visual_retrieval(self, query: str, top_k: int, filters: dict) -> list[RetrievalResult]:
        """Visual retrieval via SigLIP2 text-to-image."""
        from app.services.embedding.visual_embedding import VisualEmbeddingService
        from app.services.embedding.vector_store import VectorStoreService

        query_vec = VisualEmbeddingService.encode_text([query])[0].tolist()
        vs = VectorStoreService()
        results = vs.search("sip_visual_embeddings", query_vec, top_k, filters or None)

        return [
            RetrievalResult(
                document_id=r["payload"].get("document_id", ""),
                chunk_id=r["id"],
                text=r["payload"].get("description", ""),
                score=r["score"],
                source_type="visual",
                page_number=r["payload"].get("page_number"),
                metadata=r["payload"],
            )
            for r in results
        ]

    async def _structural_retrieval(self, query: str, top_k: int, filters: dict) -> list[RetrievalResult]:
        """Structural retrieval via Seq2Vec embeddings (experimental)."""
        return []  # Requires trained Seq2Vec model

    async def _graph_retrieval(self, query: str, filters: dict) -> list[RetrievalResult]:
        """Graph-based retrieval via Neo4j."""
        try:
            from app.services.graph.neo4j_service import Neo4jService
            svc = Neo4jService()
            return svc.search_entities(query)
        except Exception:
            return []

