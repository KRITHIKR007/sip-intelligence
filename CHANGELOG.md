# Changelog

All notable changes to the SIP Intelligence Platform are documented in this file.

## [v0.1.0] - 2026-11-05
### Initial Functional Prototype
- **Core Infrastructure**: Multi-container Docker Compose with PostgreSQL 16 (`pgvector`), Qdrant v1.12, Neo4j 5.26, Redis 7, MinIO, and OpenSearch.
- **Backend**: FastAPI asynchronous backend with SQLAlchemy 2.0 async sessions, Alembic migrations, direct bcrypt authentication, and Pydantic v2 schemas.
- **Multimodal Ingestion**: PyMuPDF & pdfplumber PDF processor, OpenCV + PaddleOCR scanner, ezdxf CAD processor, and openpyxl/pandas/python-docx office processors.
- **Signalling Taxonomy**: 56-class catalog loaded from IRISET S&T Drawing Standards (Plates 99 to 105).
- **ML Models**:
  - `BAAI/bge-m3` text embeddings (1024d)
  - `google/siglip2-base-patch16-224` visual embeddings
  - `BAAI/bge-reranker-v2-m3` cross-encoder reranker
  - Custom BiLSTM + Attention `Seq2Vec` structural model (256d)
  - Custom PyTorch Geometric `RailwayRGCN` relational graph model (256d)
- **5-Channel Hybrid RAG**: Dense vector + BM25 + Visual + Structural + Graph retrieval combined via Weighted Reciprocal Rank Fusion (RRF).
- **Deterministic Validation Engine**: Non-LLM rule evaluation framework checking safety distances, locking timers, and clearance limits.
- **Drawing Comparison**: Topological differencing identifying added, removed, and modified signalling entities across revisions.
- **Frontend Workspace**: Next.js 16 App Router application with all 10 required pages, Tailwind CSS light engineering theme, and interactive drawing viewer canvas.
- **Documentation**: Comprehensive 15-document technical suite in `/docs`.

