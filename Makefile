.PHONY: help server server-prod test test-verbose test-cov lint lint-fix typecheck \
       migrate migrate-down migrate-current migrate-history migrate-stamp \
       docker-up docker-down docker-restart docker-db docker-logs docker-status \
       mqtt-sub mqtt-pub info endpoints tables modules

.DEFAULT_GOAL := help

# ── Server ──

server: ## Run dev server (http://127.0.0.1:8000)
	python -m uvicorn app.app:app --host 0.0.0.0 --port 8000 --reload

server-prod: ## Run production server (4 workers)
	python -m uvicorn app.app:app --host 0.0.0.0 --port 8000 --workers 4

# ── Tests ──

test: ## Run all tests
	python -m pytest test/ -q --tb=short

test-verbose: ## Run tests (verbose)
	python -m pytest test/ -v --tb=short

test-cov: ## Run tests with coverage
	python -m pytest test/ -q --tb=short --cov=app --cov-report=term-missing

test-one: ## Run single test (usage: make test-one path=test/modules/iot/...)
	python -m pytest $(path) -v --tb=short

# ── Lint ──

lint: ## Run ruff lint
	python -m ruff check app/ test/

lint-fix: ## Run ruff lint with auto-fix
	python -m ruff check app/ test/ --fix

typecheck: ## Run mypy type check
	python -m mypy app/ --ignore-missing-imports

# ── Database Migrations ──

migrate: ## Apply migrations (usage: make migrate msg="add users")
	python -m alembic revision --autogenerate -m "$(msg)"

migrate-up: ## Upgrade to head
	python -m alembic upgrade head

migrate-down: ## Downgrade one revision
	python -m alembic downgrade -1

migrate-current: ## Show current version
	python -m alembic current

migrate-history: ## Show migration history
	python -m alembic history --verbose

migrate-stamp: ## Stamp database to head
	python -m alembic stamp head

# ── Docker ──

docker-up: ## Start all services
	docker-compose up -d

docker-down: ## Stop all services
	docker-compose down

docker-restart: ## Restart all services
	docker-compose restart

docker-db: ## Start PostgreSQL + InfluxDB only
	docker-compose up -d postgres influxdb

docker-logs: ## Show docker logs
	docker-compose logs -f

docker-status: ## Show docker status
	docker-compose ps

# ── MQTT ──

mqtt-sub: ## Subscribe to test/# (Ctrl+C to stop)
	C:\mosquitto\mosquitto_sub.exe -t "test/#" -v

mqtt-pub: ## Publish test message
	C:\mosquitto\mosquitto_pub.exe -t "test/hello" -m "Hello MQTT"

# ── Info ──

info: ## Show project structure
	tree /F /A app\modules | findstr /V "__pycache__"

endpoints: ## Show all API endpoints
	python -c "from app.app import app; [print(f'  {r.methods} {r.path}') for r in app.routes if hasattr(r, 'methods')]"

tables: ## Show all database tables
	python -c "from app.modules.shared.infrastructure.models import Base; [print(f'  {t}') for t in sorted(Base.metadata.tables.keys())]"

modules: ## Show module line counts
	@for /r app\modules %%d in (.) do @if exist "%%d\__init__.py" @(echo %%d & dir /b "%%d\*.py" 2>nul | find /c /v "") 

# ── Help ──

help: ## Show this help
	@echo.
	@echo ICMON Auto Repair - FastAPI DDD
	@echo ──────────────────────────────────────────
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo.
