# SIP Intelligence Platform

> **Multimodal Railway Signalling Plan Intelligence, Retrieval and Validation Platform**

SIP Intelligence is an enterprise-oriented railway engineering intelligence system designed to interpret Railway Signalling and Interlocking Plans (SIP), Electronic Interlocking (EI) schemes, Kavach (TCAS) documentation, and Indian Railways Standards (IRS / SEM / RDSO).

---

## Key Capabilities

- **Multimodal Document Ingestion**: Ingests vector PDFs, scanned drawings (PaddleOCR), DXF CAD files, Word specifications, and Excel track circuit tables.
- **56-Class Signalling Symbol Taxonomy**: Authoritative symbol catalogue extracted from IRISET Drawing Standards (Plates 99 to 105).
- **5-Channel Hybrid Retrieval Engine**: Combines Dense Vector Search (`BAAI/bge-m3`), BM25 Keyword Search, Visual Similarity (`SigLIP 2`), Structural Sequences (`Seq2Vec`), and Neo4j Graph traversals via Weighted Reciprocal Rank Fusion (RRF).
- **Neural Reranking**: Cross-encoder precision reranking via `BAAI/bge-reranker-v2-m3`.
- **Structural Seq2Vec & R-GCN**: PyTorch BiLSTM Attention model (256d) and PyTorch Geometric Relational GCN (256d) for topological sequence and knowledge graph embeddings.
- **Drawing Comparison**: Automated topological differencing detecting symbol additions, removals, and attribute shifts across revisions.
- **Deterministic Validation Engine**: Non-hallucinatory standards compliance verification against safety rules (IRS, SEM, RDSO).
- **Enterprise Engineering Workspace**: Next.js 16 App Router interface featuring 10 dedicated engineering pages.

---

## System Architecture

```
                    ┌───────────────────────────────────────────────┐
                    │      Next.js 16 Enterprise Frontend           │
                    │ (Dashboard, Viewer, Assistant, Validation...) │
                    └───────────────────────┬───────────────────────┘
                                            │ HTTP / REST
                                            ▼
                    ┌───────────────────────────────────────────────┐
                    │            FastAPI Backend Service            │
                    │  (Auth, Ingestion, Hybrid RAG, Diff, Rules)   │
                    └───────┬───────────────┬───────────────┬───────┘
                            │               │               │
            ┌───────────────▼───┐   ┌───────▼───────┐   ┌───▼───────────────┐
            │   PostgreSQL 16   │   │  Qdrant v1.12 │   │    Neo4j 5.26     │
            │ (pgvector, pgtrgm)│   │(4 Collections)│   │ (Knowledge Graph) │
            └───────────────────┘   └───────────────┘   └───────────────────┘
                            │               │               │
            ┌───────────────▼───┐   ┌───────▼───────┐   ┌───▼───────────────┐
            │   Redis 7 Queue   │   │  MinIO Storage│   │ OpenSearch BM25   │
            │  (Celery Tasks)   │   │ (Raw & Crops) │   │ (Keyword Index)   │
            └───────────────────┘   └───────────────┘   └───────────────────┘
```

---

## Quickstart

### 1. Configure Environment
```bash
cp .env.example .env
```

### 2. Launch with Docker Compose
```bash
docker compose up -d
```

### 3. Run Database Migrations
```bash
docker compose exec backend python -m alembic upgrade head
```

### 4. Access Interfaces
- **Web Workspace**: `http://localhost:3000`
- **REST API Docs**: `http://localhost:8000/api/docs`
- **Qdrant Dashboard**: `http://localhost:6333/dashboard`
- **Neo4j Browser**: `http://localhost:7474`
- **MinIO Console**: `http://localhost:9001`

---

## Documentation

Full architectural specifications are available in the `/docs` directory:
- [00_PROJECT_OVERVIEW.md](docs/00_PROJECT_OVERVIEW.md)
- [01_SYSTEM_ARCHITECTURE.md](docs/01_SYSTEM_ARCHITECTURE.md)
- [02_DATABASE_DESIGN.md](docs/02_DATABASE_DESIGN.md)
- [03_ML_ARCHITECTURE.md](docs/03_ML_ARCHITECTURE.md)
- [04_EMBEDDING_AND_RETRIEVAL.md](docs/04_EMBEDDING_AND_RETRIEVAL.md)
- [05_DOCUMENT_INGESTION.md](docs/05_DOCUMENT_INGESTION.md)
- [06_SYMBOL_RECOGNITION.md](docs/06_SYMBOL_RECOGNITION.md)
- [07_API_REFERENCE.md](docs/07_API_REFERENCE.md)
- [08_SECURITY_AND_ACCESS_CONTROL.md](docs/08_SECURITY_AND_ACCESS_CONTROL.md)
- [09_DEPLOYMENT_GUIDE.md](docs/09_DEPLOYMENT_GUIDE.md)
- [10_DEVELOPER_GUIDE.md](docs/10_DEVELOPER_GUIDE.md)
- [11_TESTING_AND_EVALUATION.md](docs/11_TESTING_AND_EVALUATION.md)
- [12_ENTERPRISE_SCALABILITY.md](docs/12_ENTERPRISE_SCALABILITY.md)
- [13_KNOWN_LIMITATIONS.md](docs/13_KNOWN_LIMITATIONS.md)
- [14_ROADMAP.md](docs/14_ROADMAP.md)

---

## License
Proprietary & Confidential — Developed for Railway Signalling and Interlocking Operations.

