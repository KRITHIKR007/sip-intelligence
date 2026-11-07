"""
SIP Intelligence — Text Chunking Service
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from app.core.config import settings


@dataclass
class Chunk:
    """A text chunk with metadata."""
    content: str
    chunk_index: int
    start_char: int
    end_char: int
    page_number: Optional[int] = None
    token_count: int = 0
    metadata: dict = field(default_factory=dict)


class ChunkingService:
    """
    Configurable text chunking with engineering-aware splitting.

    Preserves:
    - Semantic section boundaries
    - Technical identifiers (signal IDs, clause refs)
    - Table structure
    - Page-level references
    """

    def __init__(
        self,
        chunk_size: int = settings.chunk_size,
        chunk_overlap: int = settings.chunk_overlap,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Patterns to preserve (never split in the middle of these)
        self.preserve_patterns = [
            r'\b\d{1,4}[A-Z]{1,3}\b',          # Signal IDs like "101B", "23AG"
            r'\b[A-Z]{2,5}\s*\d+\b',             # Equipment refs like "TC 23"
            r'\bClause\s+\d+[\.\d]*\b',           # Clause references
            r'\bIRS[\s\-]\d+[\.\d]*\b',           # IRS standard refs
            r'\bRDSO[\s\-]\w+\b',                 # RDSO refs
            r'\b(?:UP|DN|N|S|E|W)\s+(?:HOME|STARTER|DISTANT)\b',  # Signal names
        ]

    def chunk_text(
        self,
        text: str,
        page_number: Optional[int] = None,
    ) -> list[Chunk]:
        """Split text into overlapping chunks preserving boundaries."""
        if not text or not text.strip():
            return []

        # Estimate tokens (rough: 1 token ≈ 4 chars for English)
        chars_per_token = 4
        chunk_chars = self.chunk_size * chars_per_token
        overlap_chars = self.chunk_overlap * chars_per_token

        # Split into sentences/paragraphs first
        segments = self._split_into_segments(text)

        chunks = []
        current_text = ""
        current_start = 0
        chunk_idx = 0

        for segment in segments:
            if len(current_text) + len(segment) > chunk_chars and current_text:
                # Emit chunk
                chunks.append(Chunk(
                    content=current_text.strip(),
                    chunk_index=chunk_idx,
                    start_char=current_start,
                    end_char=current_start + len(current_text),
                    page_number=page_number,
                    token_count=len(current_text) // chars_per_token,
                ))
                chunk_idx += 1

                # Overlap: keep last N characters
                if overlap_chars > 0 and len(current_text) > overlap_chars:
                    overlap_text = current_text[-overlap_chars:]
                    # Find clean boundary in overlap
                    boundary = overlap_text.find(". ")
                    if boundary > 0:
                        overlap_text = overlap_text[boundary + 2:]
                    current_start = current_start + len(current_text) - len(overlap_text)
                    current_text = overlap_text
                else:
                    current_start = current_start + len(current_text)
                    current_text = ""

            current_text += segment

        # Final chunk
        if current_text.strip():
            chunks.append(Chunk(
                content=current_text.strip(),
                chunk_index=chunk_idx,
                start_char=current_start,
                end_char=current_start + len(current_text),
                page_number=page_number,
                token_count=len(current_text) // chars_per_token,
            ))

        return chunks

    def chunk_table(self, rows: list[list[str]], page_number: Optional[int] = None) -> list[Chunk]:
        """Chunk table data by logical row groups."""
        if not rows:
            return []

        header = " | ".join(str(c) for c in rows[0]) if rows else ""
        chunks = []
        chunk_idx = 0
        current_rows = [header] if header else []

        for row in rows[1:]:
            row_text = " | ".join(str(c) for c in row)
            current_text = "\n".join(current_rows + [row_text])

            if len(current_text) > self.chunk_size * 4:  # chars
                chunks.append(Chunk(
                    content="\n".join(current_rows),
                    chunk_index=chunk_idx,
                    start_char=0,
                    end_char=0,
                    page_number=page_number,
                    token_count=len("\n".join(current_rows)) // 4,
                    metadata={"type": "table"},
                ))
                chunk_idx += 1
                current_rows = [header, row_text]
            else:
                current_rows.append(row_text)

        if current_rows:
            chunks.append(Chunk(
                content="\n".join(current_rows),
                chunk_index=chunk_idx,
                start_char=0,
                end_char=0,
                page_number=page_number,
                token_count=len("\n".join(current_rows)) // 4,
                metadata={"type": "table"},
            ))

        return chunks

    def _split_into_segments(self, text: str) -> list[str]:
        """Split text into segments at paragraph/sentence boundaries."""
        # Split on double newlines (paragraphs)
        paragraphs = re.split(r'\n\s*\n', text)

        segments = []
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # If paragraph is short enough, keep as one segment
            if len(para) < self.chunk_size * 4:
                segments.append(para + "\n\n")
            else:
                # Split on sentences
                sentences = re.split(r'(?<=[.!?])\s+', para)
                for sent in sentences:
                    segments.append(sent + " ")

        return segments

