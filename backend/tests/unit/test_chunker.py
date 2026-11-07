"""
Unit Tests for Text Chunking Service
"""
import pytest
from app.services.ingestion.chunker import ChunkingService

def test_chunk_text_basic(mock_text_document):
    chunker = ChunkingService(chunk_size=50, chunk_overlap=10)
    chunks = chunker.chunk_text(mock_text_document, page_number=1)

    assert len(chunks) > 0
    assert chunks[0].page_number == 1
    assert "Signal 101B" in chunks[0].content

def test_chunk_table():
    chunker = ChunkingService(chunk_size=100)
    table = [
        ["Signal ID", "Type", "Aspect", "Chainage"],
        ["101B", "HOME", "4A_CL", "1250"],
        ["102", "STARTER", "3A_CL", "1850"],
    ]
    chunks = chunker.chunk_table(table, page_number=2)
    assert len(chunks) == 1
    assert "101B" in chunks[0].content
    assert chunks[0].metadata.get("type") == "table"

def test_empty_text():
    chunker = ChunkingService()
    assert chunker.chunk_text("") == []

