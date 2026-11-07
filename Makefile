# =============================================================================
# SIP Intelligence Platform — Makefile
# =============================================================================

.PHONY: help setup up down restart logs infra backend frontend migrate test lint clean

# Default
help: ## Show this help
	@echo "SIP Intelligence Platform — Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# --- Environment ---
setup: ## Initial setup: copy env, create buckets, run migrations
	@if not exist .env copy .env.example .env
	docker compose up -d postgres redis qdrant neo4j minio opensearch
	@echo "Waiting for services to be healthy..."
	@timeout /t 15
	docker compose run --rm backend python -m alembic upgrade head
	@echo "Setup complete."

# --- Docker ---
up: ## Start all services
	docker compose up -d

down: ## Stop all services
	docker compose down

restart: ## Restart all services
	docker compose down
	docker compose up -d

infra: ## Start infrastructure only (no app services)
	docker compose up -d postgres qdrant neo4j redis minio opensearch

logs: ## Follow all service logs
	docker compose logs -f

logs-backend: ## Follow backend logs
	docker compose logs -f backend celery-worker

logs-frontend: ## Follow frontend logs
	docker compose logs -f frontend

# --- Development ---
backend: ## Start backend in development mode
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend-dev: ## Start frontend in development mode
	cd frontend && npm run dev

# --- Database ---
migrate: ## Run database migrations
	cd backend && python -m alembic upgrade head

migrate-create: ## Create a new migration (usage: make migrate-create MSG="description")
	cd backend && python -m alembic revision --autogenerate -m "$(MSG)"

migrate-down: ## Rollback one migration
	cd backend && python -m alembic downgrade -1

# --- Testing ---
test: ## Run all tests
	cd backend && python -m pytest tests/ -v

test-unit: ## Run unit tests
	cd backend && python -m pytest tests/unit/ -v

test-integration: ## Run integration tests
	cd backend && python -m pytest tests/integration/ -v

test-coverage: ## Run tests with coverage
	cd backend && python -m pytest tests/ -v --cov=app --cov-report=html

# --- Code Quality ---
lint: ## Run linters
	cd backend && python -m ruff check .
	cd backend && python -m mypy app/

format: ## Format code
	cd backend && python -m ruff format .

# --- Data ---
copy-symbols: ## Copy symbol catalog from reference data
	xcopy /E /I /Y "D:\sensedge\data\symbols" "data\symbols"
	copy /Y "D:\sensedge\catalog\symbols_catalog.json" "data\symbols\symbols_catalog.json"

copy-reference: ## Copy reference PDFs
	copy /Y "D:\sensedge\IRISET_SnT_Drawings_Pages_99_to_105.pdf" "data\reference\"

# --- Cleanup ---
clean: ## Remove generated files and caches
	cd backend && del /S /Q __pycache__ 2>nul
	cd backend && del /S /Q .pytest_cache 2>nul
	cd frontend && rmdir /S /Q .next 2>nul

clean-volumes: ## Remove Docker volumes (WARNING: destroys all data)
	docker compose down -v

