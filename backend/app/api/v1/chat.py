"""
SIP Intelligence — Chat / Engineering Assistant API
Strictly grounded in authentic Indian Railways documents.
"""
from __future__ import annotations

import time
import uuid
from typing import Optional

from fastapi import APIRouter
from app.schemas import ChatQueryRequest, ChatResponse, SourceCitation
from app.services.chat.real_rag_service import rag_service

router = APIRouter(prefix="/chat", tags=["Engineering Assistant"])


@router.post("/query", response_model=ChatResponse)
async def chat_query(
    body: ChatQueryRequest,
):
    """
    Process an engineering question grounded strictly in authentic
    Indian Railways reference documents (2.pdf, IRISET Plates 99-105,
    Asarva SIP, Amarda SIP, Bhuj SIP).
    Zero mockup data. Open model mode without mandatory login token.
    """
    start = time.time()

    query_type = body.query_type or _classify_query(body.question)

    # Perform real grounded RAG retrieval
    res = rag_service.query(body.question)
    answer = res.get("answer", "")
    raw_sources = res.get("sources", [])
    confidence = res.get("confidence", 0.95)

    sources: list[SourceCitation] = []
    for s in raw_sources:
        doc_id_raw = s.get("document_id", "doc-1")
        try:
            doc_uuid = uuid.UUID(doc_id_raw)
        except Exception:
            doc_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, str(doc_id_raw))

        sources.append(
            SourceCitation(
                document_id=doc_uuid,
                document_name=s.get("document_name", "Ingested Document"),
                page_number=s.get("page_number", 1),
                chunk_text=s.get("chunk_text", ""),
                relevance_score=s.get("relevance_score", 0.90),
            )
        )

    elapsed_ms = (time.time() - start) * 1000

    return ChatResponse(
        answer=answer,
        sources=sources,
        query_type=query_type,
        confidence=confidence,
        processing_time_ms=round(elapsed_ms, 2),
    )


def _classify_query(question: str) -> str:
    """Heuristic query classification based on keywords."""
    q = question.lower()

    if any(k in q for k in ["compare", "difference", "diff", "revision"]):
        return "drawing_comparison"
    if any(k in q for k in ["symbol", "identify", "what is this", "recognize"]):
        return "symbol_identification"
    if any(k in q for k in ["validate", "comply", "standard", "rule", "check"]):
        return "validation"
    if any(k in q for k in ["signal", "track", "point", "route", "relationship"]):
        return "engineering_relationship"
    if any(k in q for k in ["image", "visual", "drawing", "look"]):
        return "visual_search"
    if any(k in q for k in ["clause", "specification", "standard", "irs"]):
        return "standards_lookup"

    return "document_qa"
