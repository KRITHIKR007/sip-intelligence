# 09 Deployment Guide

## 1. Prerequisites
- Docker Engine 24+ and Docker Compose v2.20+
- Host RAM: 16 GB minimum
- Storage: 50 GB free NVMe/SSD space
- Optional GPU: NVIDIA GPU with CUDA 12+ (NVIDIA Container Toolkit installed)

---

## 2. Quickstart Deployment (One Command)

### Step 1: Clone and Configure
```bash
git clone <repository_url> sip-intelligence
cd sip-intelligence
cp .env.example .env
```
Edit `.env` to configure secure passwords for PostgreSQL, Neo4j, MinIO, and Redis.

### Step 2: Start Infrastructure & Applications
```bash
docker compose up -d
```

### Step 3: Verify Service Health
```bash
docker compose ps
curl http://localhost:8000/api/v1/health
```

Expected output:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "services": {
    "postgres": "healthy",
    "redis": "healthy",
    "qdrant": "healthy",
    "minio": "healthy"
  }
}
```

### Step 4: Run Database Migrations
```bash
docker compose exec backend python -m alembic upgrade head
```

### Step 5: Access the Platform
- **Engineering Workspace UI**: `http://localhost:3000`
- **FastAPI OpenAPI Docs**: `http://localhost:8000/api/docs`
- **Qdrant Dashboard**: `http://localhost:6333/dashboard`
- **Neo4j Browser**: `http://localhost:7474`
- **MinIO Console**: `http://localhost:9001`

