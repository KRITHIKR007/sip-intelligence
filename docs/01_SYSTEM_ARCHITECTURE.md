# 01 — System Architecture

## SIP Intelligence Platform — Architecture Documentation

---

## 1. High-Level Architecture

```mermaid
flowchart TD
    subgraph Client["Client Layer"]
        FE["Next.js Frontend<br/>(TypeScript + Tailwind CSS)"]
    end

    subgraph API["API Gateway Layer"]
        FASTAPI["FastAPI Application<br/>(Uvicorn, async)"]
        AUTH["Auth Middleware<br/>(JWT + RBAC)"]
        RATE["Rate Limiter<br/>(Redis-backed)"]
    end

    subgraph Services["Service Layer"]
        INGEST["Document Ingestion<br/>Service"]
        EMBED["Embedding<br/>Service"]
        RETRIEVE["Retrieval<br/>Service"]
        DETECT["Symbol Detection<br/>Service"]
        VALIDATE["Validation<br/>Engine"]
        COMPARE["Drawing Comparison<br/>Service"]
        ENTITY["Entity Extraction<br/>Service"]
        KNOWLEDGE["Knowledge Graph<br/>Service"]
        CHAT["Chat / Q&A<br/>Service"]
    end

    subgraph Workers["Async Workers"]
        CELERY["Celery Workers<br/>(concurrency=2)"]
    end

    subgraph Storage["Data Layer"]
        PG["PostgreSQL 16<br/>(pgvector)"]
        QD["Qdrant v1.12<br/>(Vector Store)"]
        NEO["Neo4j 5.26<br/>(Graph DB)"]
        OS["OpenSearch 2.18<br/>(BM25 Index)"]
        REDIS["Redis 7<br/>(Cache + Broker)"]
        MINIO["MinIO<br/>(Object Storage)"]
    end

    FE -->|"REST API"| FASTAPI
    FASTAPI --> AUTH --> RATE
    RATE --> INGEST & RETRIEVE & DETECT & VALIDATE & COMPARE & CHAT
    INGEST -->|"async tasks"| CELERY
    CELERY --> EMBED & DETECT & ENTITY
    EMBED --> PG & QD & OS
    RETRIEVE --> PG & QD & OS & NEO
    DETECT --> MINIO
    KNOWLEDGE --> NEO
    INGEST --> MINIO
    CHAT --> RETRIEVE
    VALIDATE --> PG & NEO
    CELERY --> REDIS
```

---

## 2. Component Architecture

```mermaid
flowchart LR
    subgraph app["backend/app/"]
        direction TB
        MAIN["main.py<br/>FastAPI app factory"]
        subgraph api["api/"]
            ROUTES["v1 routes:<br/>health, auth, projects,<br/>documents, drawings,<br/>chat, validation,<br/>knowledge, models,<br/>feedback, admin"]
        end
        subgraph core["core/"]
            CONFIG["config.py — Settings"]
            SECURITY["security.py — JWT/hashing"]
            DEPS["dependencies.py — DI"]
            LOGGING["logging.py — structlog"]
        end
        subgraph models_dir["models/"]
            ORM["SQLAlchemy ORM models:<br/>User, Project, Document,<br/>Page, Chunk, Drawing,<br/>Symbol, Entity, Validation,<br/>Feedback, AuditLog"]
        end
        subgraph schemas_dir["schemas/"]
            PYDANTIC["Pydantic v2 schemas:<br/>Request/Response DTOs"]
        end
        subgraph services_dir["services/"]
            SVC_INGEST["ingestion.py"]
            SVC_EMBED["embedding.py"]
            SVC_RETRIEVE["retrieval.py"]
            SVC_DETECT["detection.py"]
            SVC_CLASSIFY["classification.py"]
            SVC_OCR["ocr.py"]
            SVC_VALID["validation.py"]
            SVC_COMPARE["comparison.py"]
            SVC_ENTITY["entity_extraction.py"]
            SVC_GRAPH["graph.py"]
            SVC_RERANK["reranking.py"]
        end
        subgraph workers_dir["workers/"]
            CELERY_APP["celery_app.py"]
            TASKS["tasks.py"]
        end
        subgraph db["db/"]
            SESSION["session.py — async engine"]
            QDRANT_CL["qdrant_client.py"]
            NEO_CL["neo4j_client.py"]
            OS_CL["opensearch_client.py"]
            REDIS_CL["redis_client.py"]
            MINIO_CL["minio_client.py"]
        end
    end

    MAIN --> api
    api --> services_dir
    services_dir --> db
    services_dir --> models_dir
    api --> schemas_dir
    MAIN --> core
```

---

## 3. Data Flow — Document Processing

```mermaid
flowchart TD
    UPLOAD["User uploads document<br/>(PDF, Image, DXF, XLSX, DOCX)"]
    VALIDATE_FILE["Validate file type, size,<br/>malware scan"]
    STORE_RAW["Store raw file in MinIO<br/>(sip-documents bucket)"]
    CREATE_RECORD["Create Document record<br/>in PostgreSQL"]
    QUEUE["Queue processing task<br/>via Celery + Redis"]
    PARSE["Parse document<br/>(PyMuPDF / pdfplumber / OpenCV / ezdxf)"]
    EXTRACT_PAGES["Extract pages / sheets"]
    OCR{"Is scanned?"}
    RUN_OCR["Run PaddleOCR<br/>(deskew → threshold → recognize)"]
    CHUNK["Chunk text<br/>(512 tokens, 80 overlap,<br/>table-aware boundaries)"]
    EMBED_TEXT["Generate text embeddings<br/>(BGE-M3 → 1024d)"]
    EMBED_VIS["Generate visual embeddings<br/>(SigLIP2)"]
    STORE_VECTORS["Store vectors in Qdrant<br/>+ pgvector backup"]
    INDEX_BM25["Index text in OpenSearch<br/>(BM25)"]
    EXTRACT_ENT["Extract engineering entities<br/>(rule-based)"]
    STORE_GRAPH["Store entities in Neo4j"]
    STORE_PROCESSED["Store processed output<br/>in MinIO (sip-processed)"]
    UPDATE_STATUS["Update document status<br/>to COMPLETED"]

    UPLOAD --> VALIDATE_FILE --> STORE_RAW --> CREATE_RECORD --> QUEUE
    QUEUE --> PARSE --> EXTRACT_PAGES
    EXTRACT_PAGES --> OCR
    OCR -->|"Yes"| RUN_OCR --> CHUNK
    OCR -->|"No"| CHUNK
    CHUNK --> EMBED_TEXT & EMBED_VIS
    EMBED_TEXT --> STORE_VECTORS
    EMBED_VIS --> STORE_VECTORS
    STORE_VECTORS --> INDEX_BM25
    INDEX_BM25 --> EXTRACT_ENT
    EXTRACT_ENT --> STORE_GRAPH
    STORE_GRAPH --> STORE_PROCESSED --> UPDATE_STATUS
```

---

## 4. Retrieval Flow

```mermaid
flowchart TD
    QUERY["User query"]
    ROUTER["Query Router<br/>(classify query type)"]

    subgraph Channels["5 Retrieval Channels"]
        DENSE["Channel 1: Dense<br/>BGE-M3 → Qdrant<br/>(cosine similarity)"]
        BM25["Channel 2: BM25<br/>OpenSearch<br/>(term matching)"]
        VISUAL["Channel 3: Visual<br/>SigLIP2 → Qdrant<br/>(image similarity)"]
        STRUCT["Channel 4: Structural<br/>Seq2Vec → Qdrant<br/>(layout similarity)"]
        GRAPH["Channel 5: Graph<br/>R-GCN → Neo4j<br/>(entity traversal)"]
    end

    NORM["Score Normalization<br/>(min-max per channel)"]
    RRF["Reciprocal Rank Fusion<br/>RRF(d) = Σ 1/(k + rank_i)<br/>k = 60"]
    FUSE["Weighted Score Fusion<br/>(experimental)"]
    DEDUP["Deduplicate results"]
    RERANK["BGE Reranker v2 M3<br/>(cross-encoder)"]
    FILTER["Apply RBAC filters<br/>(project + department)"]
    RESPONSE["Return top-K results<br/>with citations"]

    QUERY --> ROUTER
    ROUTER --> DENSE & BM25 & VISUAL & STRUCT & GRAPH
    DENSE & BM25 & VISUAL & STRUCT & GRAPH --> NORM
    NORM --> RRF
    RRF --> FUSE
    FUSE --> DEDUP --> RERANK --> FILTER --> RESPONSE
```

---

## 5. Service Boundaries

Each service follows the **repository pattern**:

| Service | Responsibility | Databases Used | Async |
|---------|---------------|----------------|-------|
| `IngestionService` | Parse, chunk, and orchestrate document processing | PostgreSQL, MinIO, Redis | ✅ Celery |
| `EmbeddingService` | Generate and store text/visual/structural embeddings | Qdrant, pgvector, OpenSearch | ✅ Celery |
| `RetrievalService` | Execute multi-channel retrieval and fusion | Qdrant, OpenSearch, Neo4j, pgvector | Sync |
| `RerankingService` | Cross-encoder reranking of candidate results | — (in-memory) | Sync |
| `DetectionService` | YOLO11 symbol detection on drawing pages | MinIO, PostgreSQL | ✅ Celery |
| `ClassificationService` | ConvNeXt-Tiny symbol classification of crops | PostgreSQL | Sync |
| `OCRService` | PaddleOCR text extraction from images | — (in-memory) | Sync |
| `EntityExtractionService` | Rule-based extraction of engineering entities | PostgreSQL, Neo4j | ✅ Celery |
| `GraphService` | Neo4j CRUD for knowledge graph queries | Neo4j | Sync |
| `ValidationService` | Run validation rules against drawings/entities | PostgreSQL, Neo4j | Sync |
| `ComparisonService` | Drawing diff — visual overlay and entity delta | MinIO, PostgreSQL | Sync |
| `ChatService` | Orchestrate query → retrieval → formatting | All retrieval stores | Sync |

---

## 6. Model Interactions

```mermaid
flowchart LR
    subgraph Models["ML Model Zoo"]
        BGE["BGE-M3<br/>1024d text"]
        SIGLIP["SigLIP2<br/>visual"]
        SEQ["Seq2Vec<br/>256d structural"]
        RGCN["R-GCN<br/>256d graph"]
        YOLO["YOLO11<br/>detection"]
        CONVNEXT["ConvNeXt-Tiny<br/>classification"]
        PADDLE["PaddleOCR<br/>text recognition"]
        RERANKER["BGE Reranker v2 M3<br/>cross-encoder"]
    end

    subgraph Pipelines["Usage in Pipelines"]
        P_INGEST["Ingestion Pipeline"]
        P_RETRIEVAL["Retrieval Pipeline"]
        P_SYMBOL["Symbol Pipeline"]
    end

    P_INGEST --> BGE & SIGLIP & SEQ & PADDLE
    P_RETRIEVAL --> BGE & SIGLIP & SEQ & RGCN & RERANKER
    P_SYMBOL --> YOLO --> CONVNEXT --> PADDLE
```

---

## 7. Deployment Topology (Docker Compose)

```mermaid
flowchart TD
    subgraph DockerNetwork["Docker Network: sip-network"]
        subgraph Infrastructure["Infrastructure Services"]
            PG["sip-postgres<br/>:5432"]
            QD["sip-qdrant<br/>:6333/:6334"]
            NEO["sip-neo4j<br/>:7474/:7687"]
            OS["sip-opensearch<br/>:9200"]
            RD["sip-redis<br/>:6379"]
            MN["sip-minio<br/>:9000/:9001"]
        end

        subgraph Application["Application Services"]
            BE["sip-backend<br/>:8000<br/>(FastAPI + Uvicorn)"]
            CW["sip-celery-worker<br/>(concurrency=2)"]
            FE_SVC["sip-frontend<br/>:3000<br/>(Next.js)"]
        end
    end

    subgraph Volumes["Persistent Volumes"]
        V1["postgres_data"]
        V2["qdrant_data"]
        V3["neo4j_data"]
        V4["redis_data"]
        V5["minio_data"]
        V6["opensearch_data"]
        V7["model_cache"]
    end

    FE_SVC -->|"HTTP :8000"| BE
    BE --> PG & QD & NEO & OS & RD & MN
    CW --> PG & QD & NEO & OS & RD & MN
    BE -->|"task queue"| RD
    RD -->|"task dispatch"| CW

    PG --- V1
    QD --- V2
    NEO --- V3
    RD --- V4
    MN --- V5
    OS --- V6
    BE --- V7
    CW --- V7
```

### Port Mapping

| Service | Internal Port | External Port | Purpose |
|---------|--------------|---------------|---------|
| PostgreSQL | 5432 | 5432 | SQL + pgvector |
| Qdrant | 6333 / 6334 | 6333 / 6334 | REST / gRPC |
| Neo4j | 7474 / 7687 | 7474 / 7687 | Browser / Bolt |
| OpenSearch | 9200 | 9200 | REST API |
| Redis | 6379 | 6379 | Cache + broker |
| MinIO | 9000 / 9001 | 9000 / 9001 | API / Console |
| Backend | 8000 | 8000 | FastAPI |
| Frontend | 3000 | 3000 | Next.js |

---

## 8. Technology Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| API framework | FastAPI | Native async, automatic OpenAPI docs, Pydantic validation |
| ORM | SQLAlchemy 2.0 (async) | Mature, supports async via `asyncpg`, Alembic migrations |
| Task queue | Celery + Redis | Battle-tested, supports priorities, retries, rate limiting |
| Vector store | Qdrant + pgvector | Qdrant for speed, pgvector for transactional backup |
| Graph database | Neo4j | Industry standard for property graphs, Cypher query language |
| Full-text search | OpenSearch | BM25 scoring, analyzers, query DSL |
| Object storage | MinIO | S3-compatible, on-premise, supports large files |
| Text embeddings | BGE-M3 | Multilingual, strong retrieval benchmarks, 1024d |
| Visual embeddings | SigLIP2 | Image-text alignment, efficient vision encoder |
| Reranker | BGE Reranker v2 M3 | Cross-encoder accuracy, pairs well with BGE-M3 |
| Detection | YOLO11 | Real-time, single-stage, good for symbol-scale objects |
| Classification | ConvNeXt-Tiny | Efficient CNN, strong transfer learning |
| OCR | PaddleOCR | Open-source, multi-language, runs on CPU |
| Frontend | Next.js 14+ | App Router, SSR/SSG, TypeScript-first |
| Containerisation | Docker Compose | Simple orchestration for single-node prototypes |
| Logging | structlog | Structured JSON logging, request correlation |
