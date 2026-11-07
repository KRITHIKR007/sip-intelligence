# 00 — Project Overview

## SIP Intelligence Platform

**Multimodal Railway Signalling Plan Intelligence, Retrieval & Validation Platform**

---

## 1. Purpose & Scope

SIP Intelligence is a specialised engineering intelligence platform designed for Indian Railway **Signal & Telecommunication (S&T)** departments. It processes **Signalling and Interlocking Plans (SIP)**, **Engineering Interlocking (EI)** drawings, and related technical documents to enable:

- Intelligent search and question-answering over engineering corpora
- Automated recognition of standardised signalling symbols
- Drawing comparison and change detection
- Validation against engineering standards and safety rules

The platform operates entirely on-premise, ensuring that **confidential railway infrastructure drawings** never leave the organisation's network boundary.

> [!IMPORTANT]
> This is a **prototype / Milestone 1** system. All ML models ship with pretrained generic weights. **No model has been fine-tuned on actual SIP drawing data yet.** Production accuracy requires annotated training data from domain engineers.

---

## 2. Domain Context

| Term | Meaning |
|------|---------|
| **SIP** | Signalling and Interlocking Plan — scale drawings showing track layout, signals, points, level crossings, and interlocking relationships for a station or section |
| **EI** | Engineering Interlocking — formal specification of signal/point dependencies ensuring safe train movements |
| **S&T** | Signal & Telecommunication — the railway engineering department responsible for signalling infrastructure |
| **IRISET** | Indian Railways Institute of Signal Engineering & Telecommunications — the training institute that publishes standard symbol catalogs |
| **Kavach** | Indian Railway's indigenous Automatic Train Protection (ATP) system, successor to TPWS |
| **CLS** | Colour Light Signal |
| **LC Gate** | Level Crossing Gate |
| **BSLB** | Block Section Limit Board |
| **SLB** | Shunting Limit Board |

---

## 3. Functional Capabilities

| # | Capability | Status |
|---|-----------|--------|
| 1 | **Multi-format Document Ingestion** — PDF (native & scanned), images, DXF/DWG, Excel, Word | ✅ Implemented (DWG requires ODA converter) |
| 2 | **Intelligent Text Search (RAG)** — Hybrid 5-channel retrieval with reranking | ✅ Implemented |
| 3 | **Symbol Detection & Recognition** — YOLO11 + ConvNeXt-Tiny on engineering drawings | ⚠️ Framework implemented, requires training data |
| 4 | **OCR & Text Extraction** — PaddleOCR for scanned drawings and image-based documents | ✅ Implemented |
| 5 | **Drawing Comparison** — Side-by-side and overlay diff of drawing revisions | ✅ Implemented |
| 6 | **Engineering Entity Extraction** — Signals, points, track circuits, level crossings | ⚠️ Rule-based extraction, ML extraction requires training |
| 7 | **Validation Engine** — Check drawings against engineering rules and standards | ⚠️ Framework implemented, rules require engineer input |
| 8 | **Knowledge Graph** — Neo4j graph of engineering entities and relationships | ✅ Schema implemented, population requires entity extraction |
| 9 | **Project-based Organisation** — Multi-project workspace with access control | ✅ Implemented |
| 10 | **Audit Trail & Feedback** — Track all queries, document changes, and user feedback | ✅ Implemented |

---

## 4. Non-Functional Requirements

### 4.1 Scale Targets

| Dimension | Prototype | Production Target |
|-----------|-----------|-------------------|
| Documents | 1,000 | 100,000–1,000,000 |
| Drawings | 500 | 10,000–100,000 |
| Concurrent users | 10 | 100–500 |
| Query latency (p95) | < 3 s | < 2 s |
| Ingestion throughput | 10 docs/min | 100 docs/min |

### 4.2 Security & Confidentiality

- **All processing is on-premise** — no data leaves the deployment boundary
- **Cloud AI is disabled by default** — opt-in only, with content-type filtering
- **RBAC** with department-level isolation
- **Audit logging** of all user actions and data access
- **JWT-based authentication** with configurable token expiry

### 4.3 Infrastructure Constraints

- Minimum: 16 GB RAM, 4-core CPU
- GPU: Optional (4 GB VRAM minimum for ML inference)
- All services containerised via Docker Compose
- Single-node deployment in prototype; horizontal scaling planned

---

## 5. Implementation Status

### Milestone Summary

| Milestone | Description | Status |
|-----------|-------------|--------|
| **M1** | Foundation Infrastructure | ✅ Complete |
| **M2** | Document Ingestion Pipeline | ✅ Complete |
| **M3** | Text RAG with Hybrid Retrieval | ✅ Complete |
| **M4** | Symbol Detection Framework | ⚠️ Framework only — no trained model |
| **M5** | Engineering Entity Extraction | ⚠️ Rule-based only |
| **M6** | Drawing Comparison & Validation | ✅ Complete (rules need engineer input) |
| **M7** | Complete UI (10 pages) | ✅ Complete |

### Detailed Component Status

| Component | Implementation | Notes |
|-----------|---------------|-------|
| PostgreSQL + pgvector | ✅ Fully implemented | Schema, migrations, async ORM |
| Qdrant vector store | ✅ Fully implemented | 4 collections configured |
| Neo4j graph database | ✅ Schema implemented | Awaiting entity population |
| OpenSearch BM25 | ✅ Fully implemented | Full-text indexing pipeline |
| Redis caching + Celery | ✅ Fully implemented | Async task queue |
| MinIO object storage | ✅ Fully implemented | 4 buckets configured |
| BGE-M3 text embeddings | ✅ Fully implemented | 1024-d dense vectors |
| SigLIP2 visual embeddings | ✅ Fully implemented | For drawing page retrieval |
| BGE Reranker v2 M3 | ✅ Fully implemented | Cross-encoder reranking |
| YOLO11 symbol detection | ⚠️ Scaffold only | Requires annotated SIP dataset |
| ConvNeXt-Tiny classification | ⚠️ Scaffold only | Requires annotated SIP dataset |
| Seq2Vec structural embeddings | 🧪 Experimental | BiLSTM, untrained |
| R-GCN graph embeddings | 🧪 Experimental | PyTorch Geometric, untrained |
| PaddleOCR | ✅ Integrated | Generic model, not tuned for engineering text |
| Next.js Frontend | ✅ 10 pages complete | Dashboard, Projects, Documents, Drawings, Chat, Validation, Knowledge, Symbols, Admin, Settings |

---

## 6. Known Limitations

> [!CAUTION]
> The following limitations are critical to understand before evaluating system outputs.

1. **No ML models are trained on SIP data** — all models use generic pretrained weights
2. **No annotated dataset exists** for Indian Railway signalling symbols
3. **DWG file processing** requires the proprietary ODA File Converter (not bundled)
4. **No LLM/generative AI** is integrated in the prototype — the system is retrieval-only by default
5. **Cloud AI gateway** is disabled by default; enabling it sends data off-premise
6. **Validation rules** are placeholder templates; real rules require S&T engineer authorship
7. **Graph topology** is schema-only; spatial inference from drawing layout is not implemented
8. **4 GB VRAM constraint** limits batch sizes for GPU inference
9. **PaddleOCR** has reduced accuracy on engineering notation, subscripts, and rotated text
10. **Single-node deployment** only — no clustering or HA in the prototype

---

## 7. Document Index

| Document | Description |
|----------|-------------|
| [01 — System Architecture](01_SYSTEM_ARCHITECTURE.md) | Component diagrams, data flows, deployment topology |
| [02 — Database Design](02_DATABASE_DESIGN.md) | PostgreSQL schema, Qdrant collections, Neo4j graph model |
| [03 — ML Architecture](03_ML_ARCHITECTURE.md) | Model inventory, training pipelines, inference configuration |
| [04 — Embedding & Retrieval](04_EMBEDDING_AND_RETRIEVAL.md) | 5-channel hybrid retrieval, RRF, reranking |
| [05 — Document Ingestion](05_DOCUMENT_INGESTION.md) | Processing pipeline, chunking, format handlers |
| [06 — Symbol Recognition](06_SYMBOL_RECOGNITION.md) | 56-symbol catalog, detection/classification pipeline |
| [07 — API Reference](07_API_REFERENCE.md) | All REST endpoints with examples |
| [08 — Security & Access Control](08_SECURITY_AND_ACCESS_CONTROL.md) | RBAC, JWT, audit, data handling |
| [09 — Deployment Guide](09_DEPLOYMENT_GUIDE.md) | Docker Compose setup, configuration, troubleshooting |
| [10 — Developer Guide](10_DEVELOPER_GUIDE.md) | Repository structure, conventions, contribution workflow |
| [11 — Testing & Evaluation](11_TESTING_AND_EVALUATION.md) | Test strategy, ML evaluation metrics |
| [12 — Enterprise Scalability](12_ENTERPRISE_SCALABILITY.md) | Capacity planning, scaling strategies |
| [13 — Known Limitations](13_KNOWN_LIMITATIONS.md) | Exhaustive limitation catalog |
| [14 — Roadmap](14_ROADMAP.md) | Phase plan and acceptance criteria |
