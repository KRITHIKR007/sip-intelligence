# 07 REST API Reference

The backend provides fully typed REST APIs built with FastAPI, automatic OpenAPI schema documentation (`/api/openapi.json`), and interactive Swagger UI (`/api/docs`).

All endpoints are versioned under `/api/v1/`.

---

## 1. Authentication Endpoints

### `POST /api/v1/auth/login`
- **Request Body**: `{ "email": "engineer@railways.gov.in", "password": "SecretPassword123" }`
- **Response**: `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer"
}
```

### `POST /api/v1/auth/refresh`
- **Request Body**: `{ "refresh_token": "..." }`
- **Response**: `200 OK` with refreshed access token.

### `GET /api/v1/auth/me`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `200 OK` with user profile, department, and role.

---

## 2. Projects Endpoints

### `GET /api/v1/projects`
- **Query Params**: `page` (default 1), `page_size` (default 20), `search` (optional string)
- **Response**: Paginated list of projects with document counts.

### `POST /api/v1/projects`
- **Request Body**: `{ "name": "Bhuj Quadrupling", "description": "...", "department_id": "uuid" }`
- **Response**: `201 Created`

---

## 3. Documents & Ingestion Endpoints

### `POST /api/v1/documents/upload`
- **Form Data**:
  - `project_id`: UUID
  - `file`: Binary file upload
- **Response**: `201 Created` with document metadata and asynchronous processing state (`QUEUED`).

### `GET /api/v1/documents/{document_id}/status`
- **Response**: Current pipeline status (`QUEUED`, `PROCESSING`, `COMPLETED`, `FAILED`).

### `GET /api/v1/documents/{document_id}/pages`
- **Response**: List of extracted pages with dimensions, OCR confidence, and render paths.

---

## 4. Drawing Entities & Comparison

### `GET /api/v1/drawings/{drawing_id}/entities`
- **Query Params**: `entity_type`, `min_confidence`
- **Response**: List of extracted engineering entities with bounding boxes.

### `POST /api/v1/drawings/compare`
- **Request Body**: `{ "drawing_id_a": "uuid", "drawing_id_b": "uuid" }`
- **Response**: Entity additions, removals, and modifications across drawing revisions.

---

## 5. Grounded Engineering Chat

### `POST /api/v1/chat/query`
- **Request Body**:
```json
{
  "question": "What is the function and locking criteria of signal 101B?",
  "project_id": "uuid-optional",
  "query_type": "symbol_identification"
}
```
- **Response**: Source-grounded answer with citations, confidence, and page references.

---

## 6. Deterministic Validation

### `POST /api/v1/validation/run`
- **Request Body**: `{ "document_id": "uuid", "rule_ids": ["uuid"] }`
- **Response**: `201 Created` with validation job ID.

### `GET /api/v1/validation/{job_id}/results`
- **Response**: List of rule findings (`PASS`, `FAIL`, `REVIEW_REQUIRED`) with observed evidence.

