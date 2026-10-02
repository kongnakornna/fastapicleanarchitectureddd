.DEFAULT_GOAL := help
COMPOSE := docker compose
DEPENDENCIES := database database-admin cache cache-admin

# ─── Python runner (fallback: uv → python -m) ────────────────
# ใช้ python -m แทน uv run เพื่อหลีกเลี่ยง Smart App Control
# และไม่ให้ uv สร้าง venv ทับซ้อน
PYTHON := python

.PHONY: help
help:
	@grep -hE '^[a-zA-Z_-]+:' $(MAKEFILE_LIST) | cut -d: -f1 | sort -u

# ═══════════════════════════════════════════════════════════
#  Docker
# ═══════════════════════════════════════════════════════════
.PHONY: start
start:
	$(COMPOSE) up -d --build --remove-orphans
	$(COMPOSE) logs -f

.PHONY: start-silent
start-silent:
	$(COMPOSE) up -d --build --remove-orphans

.PHONY: stop
stop:
	$(COMPOSE) down --remove-orphans

.PHONY: delete
delete:
	$(COMPOSE) down -v --remove-orphans

.PHONY: dependencies-up
dependencies-up:
	$(COMPOSE) up -d --remove-orphans $(DEPENDENCIES)
	$(COMPOSE) logs -f $(DEPENDENCIES)

.PHONY: dependencies-up-silent
dependencies-up-silent:
	$(COMPOSE) up -d --remove-orphans $(DEPENDENCIES)

.PHONY: dependencies-down
dependencies-down:
	$(COMPOSE) down --remove-orphans

.PHONY: logs
logs:
	$(COMPOSE) logs -f

.PHONY: view-processes
view-processes:
	docker ps -a

# ═══════════════════════════════════════════════════════════
#  Development  (ใช้ python -m แทน uv run)
# ═══════════════════════════════════════════════════════════
.PHONY: dev
dev:
	$(PYTHON) -m uvicorn app.app:app --reload

.PHONY: lint
lint:
	$(PYTHON) -m ruff check .

.PHONY: format
format:
	$(PYTHON) -m ruff format .

.PHONY: migrate
migrate:
	$(PYTHON) -m alembic upgrade head

.PHONY: migration
migration:
	$(PYTHON) -m alembic revision --autogenerate -m "$(m)"

# ═══════════════════════════════════════════════════════════
#  YOLO Module
# ═══════════════════════════════════════════════════════════
.PHONY: yolo-generate
yolo-generate:
	$(PYTHON) create_module_yolo.py all --force

.PHONY: yolo-verify
yolo-verify:
	$(PYTHON) create_module_yolo.py verify

.PHONY: yolo-clean
yolo-clean:
	$(PYTHON) create_module_yolo.py clean --yes

# ═══════════════════════════════════════════════════════════
#  Tests
# ═══════════════════════════════════════════════════════════
.PHONY: test
test:
	$(PYTHON) -m pytest tests/ -v

.PHONY: test-unit
test-unit:
	$(PYTHON) -m pytest tests/unit/ -v

# ═══════════════════════════════════════════════════════════
#  Setup (ครั้งแรก)
# ═══════════════════════════════════════════════════════════
.PHONY: setup
setup:
	py -3.11 -m venv .venv
	.\.venv\Scripts\python.exe -m pip install --upgrade pip
	.\.venv\Scripts\python.exe -m pip install -r requirements.txt

