# 10 Developer Onboarding Guide

## 1. Local Development Setup

### Backend (Python 3.11 / 3.12)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (Next.js 16 + React 19)
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` to access the hot-reloading development server.

---

## 2. Running Automated Tests
```bash
# Run all unit tests
pytest backend/tests/unit/ -v

# Run integration tests
pytest backend/tests/integration/ -v

# Run ML model verification tests
pytest backend/tests/unit/test_seq2vec.py -v
```

---

## 3. Database Migration Workflow
When modifying SQLAlchemy models in `backend/app/models/`:
```bash
cd backend
# Generate migration script
python -m alembic revision --autogenerate -m "add_new_entity_fields"

# Apply migration
python -m alembic upgrade head
```

