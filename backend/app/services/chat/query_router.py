"""
SIP Intelligence — Query Router and Orchestrator
"""
from __future__ import annotations

import uuid
from typing import Any, Optional

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import SourceCitation

logger = structlog.get_logger()


class QueryRouter:
    """
    Intelligent query router that classifies questions and invokes
    only the relevant retrieval channels.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def process(
        self,
        question: str,
        project_id: Optional[uuid.UUID] = None,
        document_ids: Optional[list[uuid.UUID]] = None,
        query_type: str = "general",
    ) -> dict[str, Any]:
        """Process a question through the hybrid retrieval pipeline."""
        from app.services.retrieval.hybrid_retriever import HybridRetriever

        retriever = HybridRetriever()

        # Retrieve
        results = await retriever.retrieve(
            query=question,
            query_type=query_type,
            top_k=50,
            project_id=str(project_id) if project_id else None,
        )

        if not results:
            return {
                "answer": "No relevant information found. Please upload and process documents first.",
                "sources": [],
            }

        # Rerank top candidates
        try:
            from app.services.retrieval.reranker import RerankerService
            docs_for_rerank = [
                {"text": r.text, "document_id": r.document_id, "chunk_id": r.chunk_id,
                 "page_number": r.page_number, "metadata": r.metadata}
                for r in results if r.text
            ]
            reranked = RerankerService.rerank(question, docs_for_rerank, top_k=10)
        except Exception:
            reranked = [
                {"text": r.text, "document_id": r.document_id, "chunk_id": r.chunk_id,
                 "page_number": r.page_number, "rerank_score": r.score}
                for r in results[:10]
            ]

        # Build source-grounded answer
        sources = []
        context_parts = []
        for doc in reranked[:5]:
            context_parts.append(doc.get("text", ""))
            sources.append(SourceCitation(
                document_id=uuid.UUID(doc["document_id"]) if doc.get("document_id") else uuid.uuid4(),
                document_name=doc.get("metadata", {}).get("filename", "Unknown"),
                page_number=doc.get("page_number"),
                chunk_text=doc.get("text", "")[:200],
                relevance_score=doc.get("rerank_score", 0.0),
            ))

        # Generate answer from retrieved context
        context = "\n\n---\n\n".join(context_parts)
        answer = self._generate_answer(question, context, query_type)

        return {"answer": answer, "sources": sources}

    def _generate_answer(self, question: str, context: str, query_type: str) -> str:
        """
        Generate a source-grounded answer from retrieved context.

        NOTE: In the prototype, this uses extractive summarization.
        Cloud LLM integration is disabled by default and requires
        explicit approval via the AI gateway.
        """
        if not context.strip():
            return "No relevant context found to answer this question."

        # Extractive approach: return relevant passages with context
        answer_parts = [
            f"**Question:** {question}\n",
            f"**Query Type:** {query_type}\n",
            "**Retrieved Evidence:**\n",
        ]

        for i, passage in enumerate(context.split("\n\n---\n\n")[:5], 1):
            if passage.strip():
                answer_parts.append(f"\n**Source {i}:**\n{passage[:500]}")

        answer_parts.append(
            "\n\n*Note: This response is based on retrieved document passages. "
            "Enable the external AI gateway for natural language synthesis.*"
        )

        return "\n".join(answer_parts)

