"""
SIP Intelligence — OpenSearch BM25 Search Service
"""
from __future__ import annotations

from typing import Any, Optional

import structlog
from opensearchpy import OpenSearch

from app.core.config import settings

logger = structlog.get_logger()


class SearchService:
    """OpenSearch BM25 full-text search integration."""

    INDEX = f"{settings.opensearch_index_prefix}_chunks"

    def __init__(self):
        self.client = OpenSearch(
            hosts=[{"host": settings.opensearch_host, "port": settings.opensearch_port}],
            http_auth=(settings.opensearch_user, settings.opensearch_password)
            if settings.opensearch_user else None,
            use_ssl=False,
            verify_certs=False,
        )

    def ensure_index(self):
        """Create the search index if it doesn't exist."""
        if not self.client.indices.exists(self.INDEX):
            self.client.indices.create(
                self.INDEX,
                body={
                    "settings": {"number_of_shards": 1, "number_of_replicas": 0},
                    "mappings": {
                        "properties": {
                            "text": {"type": "text", "analyzer": "standard"},
                            "document_id": {"type": "keyword"},
                            "project_id": {"type": "keyword"},
                            "page_number": {"type": "integer"},
                            "chunk_index": {"type": "integer"},
                        }
                    },
                },
            )
            logger.info("OpenSearch index created", index=self.INDEX)

    def index_chunk(self, chunk_id: str, text: str, metadata: dict):
        """Index a text chunk."""
        body = {"text": text, **metadata}
        self.client.index(index=self.INDEX, id=chunk_id, body=body)

    def index_chunks_bulk(self, chunks: list[dict]):
        """Bulk index chunks."""
        from opensearchpy.helpers import bulk

        actions = [
            {
                "_index": self.INDEX,
                "_id": c["id"],
                "_source": {"text": c["text"], **c.get("metadata", {})},
            }
            for c in chunks
        ]
        bulk(self.client, actions)

    def search(
        self,
        query: str,
        top_k: int = 50,
        filters: Optional[dict] = None,
    ) -> list[dict]:
        """BM25 search with optional filters."""
        must = [{"match": {"text": {"query": query, "operator": "or"}}}]

        filter_clauses = []
        if filters:
            for key, value in filters.items():
                filter_clauses.append({"term": {key: value}})

        body = {
            "size": top_k,
            "query": {
                "bool": {
                    "must": must,
                    "filter": filter_clauses,
                }
            },
        }

        try:
            response = self.client.search(index=self.INDEX, body=body)
            hits = response.get("hits", {}).get("hits", [])
            return [
                {
                    "id": hit["_id"],
                    "score": hit["_score"],
                    "text": hit["_source"].get("text", ""),
                    "document_id": hit["_source"].get("document_id", ""),
                    "page_number": hit["_source"].get("page_number"),
                }
                for hit in hits
            ]
        except Exception as e:
            logger.warning("OpenSearch search failed", error=str(e))
            return []

