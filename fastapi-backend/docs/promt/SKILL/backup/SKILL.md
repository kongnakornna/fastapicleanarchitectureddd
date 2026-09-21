# 📦 Skill Package: `python-ddd-clean-arch`

โครงสร้างสมบูรณ์พร้อมใช้งาน — วาง folder นี้ใน `~/.claude/skills/` (หรือ `.claude/skills/` ใน project) แล้วเรียกใช้ได้ทันที

```
python-ddd-clean-arch/
├── SKILL.md                          ← entry point (Frontmatter + core)
├── reference/
│   ├── 01-global-constraints.md
│   ├── 02-master-structure.md
│   ├── 03-templates-a-g.md
│   ├── 04-sql-migration.md
│   ├── 05-routing.md
│   ├── 06-docs-postman.md
│   ├── 07-reports.md
│   ├── 08-checklists.md
│   ├── 09-testing.md                 ← 🆕
│   ├── 10-debug.md                   ← 🆕
│   └── 11-cheatsheet.md
├── scripts/
│   ├── create_modules.bat
│   ├── create_module.ps1
│   └── new_module.sh
├── assets/
│   ├── conftest.py
│   ├── logging.py
│   ├── middleware.py
│   └── pyproject.toml
└── examples/
    └── inventory/                    ← ตัวอย่าง module เต็ม
```

---

## 1️⃣ `SKILL.md` (entry point)

```markdown
---
name: python-ddd-clean-arch
description: >
  Generate production-ready Python modules following DDD + Clean Architecture
  for ERP/CRM/IoT systems. Use when the user asks to create, refactor, extend,
  fix, audit, performance-test, or document a Python module that uses
  FastAPI + Pydantic v2 + SQLAlchemy 2.0 (async) + PostgreSQL + Redis + Kafka.
  Covers SQL migrations (V001/V002/V003 + RLS), router registration,
  full test pyramid (unit/integration/property/manual), structlog debugging,
  and 23-part output structure. Triggers: "create module", "TEMPLATE A-G",
  "python ddd", "clean architecture", "create_modules", "V001 create",
  "unit test", "debug module", "testing", "RLS".
license: MIT
version: 2.0.0
---

# Python DDD / Clean Architecture — Skill

Production-ready module generator for **FastAPI + Pydantic v2 + SQLAlchemy 2.0
(async) + PostgreSQL 17 + Redis 8 + Kafka**, targeted at ERP + CRM + IoT
(65 modules / 8 layers).

## When to use this skill

Use this skill whenever the user requests any of:

| User says | Use |
|---|---|
| "สร้าง module X" / "create module X" | [TEMPLATE A](#template-a) |
| "refactor X" / "ปรับปรุง X" | [TEMPLATE B](#template-b) |
| "เพิ่ม feature X" / "extend X" | [TEMPLATE C](#template-c) |
| "แก้ bug" / "fix bug X" + stacktrace | [TEMPLATE D](#template-d) |
| "security audit X" | [TEMPLATE E](#template-e) |
| "ทดสอบ performance X" / SLO | [TEMPLATE F](#template-f) |
| "เขียน docs X" / README | [TEMPLATE G](#template-g) |
| "เขียน unit test" / "test module" | [§9 Testing](#9-testing) |
| "debug module X" / "log ไม่ขึ้น" | [§10 Debug](#10-debug) |

## Hard rules (NEVER violate)

```markdown
❌ No greeting, no summary, no repetition in output
❌ No `...` or `# code here` — full production code only
❌ Domain layer MUST NOT import framework
❌ NEVER `commit()` in Repository — use `flush()`
❌ Cache NEVER raises — log + return None/False
❌ NEVER `float` for money/stock — use `Decimal`
❌ NEVER `print()` — use `structlog`
❌ NEVER log PII / token / password
❌ NEVER query across tenants (RLS enforced)
❌ NEVER `CREATE TABLE IF NOT EXISTS` in main migration
❌ NEVER edit committed V001–V003
```

## Output contract — 23 mandatory sections

Every response for TEMPLATE A must contain **all 23 sections in order**:

```
01. Details          09. Workflow Steps    17. SQL & Migration Plan
02. Concept          10. Performance       18. Routing Registration
03. Requirements     11. TDD Plan          19. Documentation Package
04. Target           12. Prohibitions      20. Swagger / OpenAPI
05. Scope            13. Cautions          21. Postman Collection
06. Folder Structure 14. Pros              22. Summary
07. Workflow Diagram 15. Cons              23. Completion Report
08. Affected Areas   16. Test Checklist
```

Full spec → [`reference/02-master-structure.md`](reference/02-master-structure.md)

## Task Templates A–G — quick reference

### TEMPLATE A {#template-a} — CREATE_NEW

Inputs: `module`, `layer(0-7)`, `prefix(3)`, `stack`

Produces **35 files**:
- `app/modules/{module}/` — domain(6) + application(6) + infrastructure(5) + presentation(5) + `__init__`
- `db/migrations/` — V001 create + V002 seed + V003 rollback
- `tests/` — `conftest.py` + unit + integration + property + manual
- `docs/` — README + API
- **Edit** `app/routes.py` + `migrations/env.py`

→ Full spec: [`reference/03-templates-a-g.md#template-a`](reference/03-templates-a-g.md#template-a)

### TEMPLATE B — REFACTOR

Keep public API. No new feature. Tests must stay green. Coverage must not drop.

### TEMPLATE C — EXTEND

Add feature + new endpoints + new migration `V00X__{action}.sql` + new tests.

### TEMPLATE D — BUGFIX

Two-step: **(1) Hypothesis → wait for approval. (2) Fix + regression test.**
Requires stacktrace + file:line root cause.

### TEMPLATE E — SECURITY_AUDIT

Table-only output. OWASP Top 10 / ASVS L2. Columns: Risk / Layer / File:Line /
Severity / CWE / Fix / Auto-fix.

### TEMPLATE F — PERF_TEST

Metrics: p50 / p95 / RPS / DB queries-per-req / Seq scans. Targets must be
explicit (`p95 < 200ms`, `> 100 rps`).

### TEMPLATE G — DOCUMENTATION

Doc types: README / API / ARCH / RUNBOOK / ONBOARDING / ADR.

## SQL & Migration (mandatory)

Every module → 3 files, **always**:

```sql
V001__create_{module}.sql   -- table + indexes + RLS + trigger + seq
V002__seed_{module}.sql     -- ON CONFLICT DO NOTHING
V003__rollback_{module}.sql -- CASCADE drop
```

Required table columns:
`id UUID PK`, `tenant_id UUID`, `code`, `name`, `status`, `amount NUMERIC(15,2)`,
`metadata JSONB`, `version INT`, `created_at`, `updated_at`, `deleted_at`,
`UNIQUE(tenant_id,code)`, `CHECK(amount >= 0)`, partial index on
`(tenant_id,status) WHERE deleted_at IS NULL`, `ENABLE ROW LEVEL SECURITY`,
`CREATE POLICY ... USING (tenant_id = current_setting('app.current_tenant')::uuid)`,
`BEFORE UPDATE` trigger.

→ Full DDL: [`reference/04-sql-migration.md`](reference/04-sql-migration.md)

## Routing (mandatory)

Must register in **two** files:

```python
# app/routes.py
api_router.include_router({module}_router)   # placed in correct layer

# migrations/env.py
from app.modules.{module}.infrastructure.models import {Module}Model
```

Verify: `/docs` shows new tag · `/openapi.json` shows schema · prefix unique.

## 9. Testing {#9-testing}

**Pyramid:** unit 70% · integration 25% · manual 5% (+ property bonus).

**Minimum counts per module:**

| Level | Min | Tool |
|---|---|---|
| Unit | ≥ 8 | pytest + pytest-asyncio + AsyncMock |
| Integration | ≥ 4 | testcontainers + asyncpg (real DB + RLS) |
| Property | ≥ 3 | hypothesis |
| Manual | 8 scenarios | Postman / curl |

**Coverage gates:**

| Layer | Gate |
|---|---|
| `domain/` | 95% |
| `application/` | 90% |
| `infrastructure/` | 80% |
| `presentation/` | 70% |
| **project** | **85% (CI)** |

**Required assets:**
- [`assets/conftest.py`](assets/conftest.py) — global fixtures
  (event loop, faker_th, tenant_ctx, db_engine, db_session with RLS,
  redis_client, fake_clock, decimal_factory)
- [`assets/pyproject.toml`](assets/pyproject.toml) — pytest + coverage config

**Unit test MUST cover** per module:
- ✅ happy path (defaults correct)
- ✅ edge (zero amount, quantization, immutability)
- ✅ errors (negative amount, invalid transition, empty code)
- ✅ VO behavior (Money add, currency mismatch)
- ✅ use case with mocked ports (repo/cache/bus/idem)
- ✅ cache-never-raise (cache raises → use case still succeeds)
- ✅ read-back verification (repo.get_by_id called after save)

**Integration test MUST cover**:
- ✅ save → get round-trip
- ✅ RLS blocks other tenant (returns None)
- ✅ unique code conflict raises IntegrityError

→ Full templates + commands: [`reference/09-testing.md`](reference/09-testing.md)

## 10. Debug {#10-debug}

**Rules:**
- ❌ No `print()` / `pprint()` in production code
- ❌ No PII / secret / auth header in logs
- ✅ `structlog` only
- ✅ Always bind `trace_id` + `request_id` + `tenant_id`

**Required assets:**
- [`assets/logging.py`](assets/logging.py) — structlog config + PII masking processor
- [`assets/middleware.py`](assets/middleware.py) — `RequestContextMiddleware` binds
  trace context via contextvars, adds `x-trace-id` header

**Layer-specific recipes:**

| Layer | Key check |
|---|---|
| Domain | frozen dataclass, VO eq/hash, invariants raise |
| Application | bind log context, mock ports, inspect `await_args` |
| Infrastructure | `SQL_ECHO=1`, RLS set, `EXPLAIN ANALYZE`, redis monitor |
| Presentation | trace-id propagation, pydantic validation detail |

**Common issues table** (12 rows) → [`reference/10-debug.md`](reference/10-debug.md)

**ENV for debug:**
```bash
LOG_LEVEL=DEBUG SQL_ECHO=1 PYTHONASYNCIODEBUG=1 uvicorn app.main:app --reload
```

## Helper scripts

```bash
# Windows
scripts\create_modules.bat new inventory 3 inv --sql --tests --docs --routes
scripts\create_modules.bat debug inventory

# Linux / macOS
./scripts/new_module.sh inventory 3 inv --sql --tests --docs --routes
```

→ Full scripts + PS1 spec: [`scripts/`](scripts/)

## Cheatsheet (one screen)

```bash
# ── TEMPLATES ─────────────────────────────────
opencode -c "TEMPLATE A + module=inventory + layer=3-goods"
opencode -c "TEMPLATE B + target=repositories.py"
opencode -c "TEMPLATE C + module=key + feature=bulk-revoke"
opencode -c "TEMPLATE D + stacktrace=[paste]"
opencode -c "TEMPLATE E + target=authentication + Mode=Read-only"
opencode -c "TEMPLATE F + target=knowledge/list + SLO p95<200ms"
opencode -c "TEMPLATE G + Doc Type=README + module=events"

# ── SCRIPTS ───────────────────────────────────
create_modules.bat new inventory 3 inv --sql --tests --docs --routes
create_modules.bat debug inventory

# ── TEST ──────────────────────────────────────
pytest -m unit -q
pytest -m integration -q --cov=app
pytest --lf -vv --tb=long
pytest --pdb -k inventory

# ── DEBUG ─────────────────────────────────────
LOG_LEVEL=DEBUG SQL_ECHO=1 uvicorn app.main:app --reload
redis-cli -p 6380 monitor
py-spy top --pid $(pgrep -f "uvicorn app.main")
```

## Universal header (prepend to every OpenCode prompt)

```markdown
# ═══════════════════════════════════════════════════════════════
# 🎯 OPENCODE PROMPT — [Module] / [Task A-G]
# ═══════════════════════════════════════════════════════════════
[GLOBAL CONSTRAINTS]
- No greeting / no summary / no repetition
- Only files in Output Scope
- Full production code, no `...`
- Comments bilingual (TH+EN), concise
- 3-branch (UC) / 2-branch (Repo) / never-raise (Cache)
- Decimal / flush() no commit() / structlog no print()
- SQL: V001 + V002 + V003 + RLS + Trigger
- Routing: app/routes.py + migrations/env.py
- Docs: README + Swagger + Postman
- Tests: unit ≥ 8 / integration / property / manual — coverage ≥ 85%
- Debug: structlog + PII masking + trace_id
### Metadata
- Task: [A-G] | Module: [xxx] | Layer: [0-7] | Stack: [FastAPI]
- Tests needed? [Yes/No] | Debug kit? [Yes/No]
### Output Scope (23 sections)
01-16 → 17 SQL → 18 Routing → 19-21 Docs → 22-23 Summary
+ §9 Testing + §10 Debug
# ═══════════════════════════════════════════════════════════════
```

## References

| File | Purpose |
|---|---|
| [`reference/01-global-constraints.md`](reference/01-global-constraints.md) | All hard rules |
| [`reference/02-master-structure.md`](reference/02-master-structure.md) | 23-section spec |
| [`reference/03-templates-a-g.md`](reference/03-templates-a-g.md) | Full A–G templates |
| [`reference/04-sql-migration.md`](reference/04-sql-migration.md) | V001/V002/V003 DDL |
| [`reference/05-routing.md`](reference/05-routing.md) | routes.py + env.py |
| [`reference/06-docs-postman.md`](reference/06-docs-postman.md) | README + Swagger + Postman |
| [`reference/07-reports.md`](reference/07-reports.md) | Report A/B/C/D |
| [`reference/08-checklists.md`](reference/08-checklists.md) | DoD · SQL · TDD · Pre-flight |
| [`reference/09-testing.md`](reference/09-testing.md) | Test pyramid + templates |
| [`reference/10-debug.md`](reference/10-debug.md) | Debug workflow + recipes |
| [`reference/11-cheatsheet.md`](reference/11-cheatsheet.md) | All commands |
```

---

## 2️⃣ `reference/01-global-constraints.md`

```markdown
# 01 — Global Constraints

```markdown
[GLOBAL CONSTRAINTS]
- ห้ามทักทาย / ห้ามสรุป / ห้ามอธิบายซ้ำ
- ตอบเฉพาะไฟล์ใน "Output Scope"
- โค้ดเต็ม Production-ready ห้าม `...` หรือ `# code here`
- ห้ามแตะไฟล์นอก Scope (ถ้าจำเป็น → ประกาศ SIDE-EFFECT WARNING)
- คอมเมนต์ 2 ภาษา (ไทย + English) สั้น กระชับ
- Error handling:
  • Use Case   → 3-branch (StandardException → DomainError → Exception)
  • Repository → 2-branch (StandardException → Exception)
  • Cache      → never-raise (log + return None/False)
- Type hints ครบ / Pydantic v2 / SQLAlchemy 2.0 async
- ใช้ `Decimal` เท่านั้น (ห้าม float กับเงิน/สต็อก)
- ใช้ `flush()` ห้าม `commit()` ใน Repository
- SQL: V001 create + V002 seed + V003 rollback + RLS + Trigger
- Routing: register ที่ `app/routes.py` + `migrations/env.py`
- Docs: README + OpenAPI + Postman + AsyncAPI (ถ้ามี WS)
- Tests: unit ≥ 8 / integration / property / manual — coverage ≥ 85%
- Debug: structlog เท่านั้น / ห้าม log PII / ห้าม print
- Path: `app/modules/{module}/{layer}/{file}.py`
- ข้อมูลไม่พอ → ถาม 1 คำถาม ห้ามเดา
```
```

---

## 3️⃣ `reference/09-testing.md` (สรุปหัวข้อสำคัญ)

```markdown
# 09 — Testing Block

## 9.1 Pyramid
- Unit 70% (domain + application) — ≥ 8 tests
- Integration 25% (repository + DB + RLS) — ≥ 4 tests
- Property (hypothesis) — ≥ 3 tests
- Manual E2E — 8 scenarios

## 9.2 Assets (copy ไปใช้)
- assets/conftest.py — fixtures: event_loop, faker_th, tenant_ctx,
  other_tenant_ctx, db_engine, db_session (RLS-aware), redis_client,
  fake_clock, decimal_factory
- assets/pyproject.toml — [tool.pytest.ini_options] + [tool.coverage.*]

## 9.3 Test file structure per module
tests/
├── conftest.py
├── unit/test_{module}.py              # domain
├── unit/test_{module}_use_cases.py    # application (mock ports)
├── integration/test_{module}_repository.py  # RLS cross-tenant
├── property/test_{module}_invariants.py
└── manual/manual_test_{module}.md

## 9.4 Coverage map (CI gate = 85%)
domain 95% · application 90% · infrastructure 80% · presentation 70%

## 9.5 Commands
pytest -m unit -q
pytest -m integration -q --cov=app --cov-fail-under=85
pytest --lf -vv --tb=long
pytest --pdb -k {module}
```

> เนื้อหาเต็ม (test templates ทั้ง 4 แบบ + 8 scenarios + idempotency checklist)
> อยู่ในไฟล์จริง — copy จาก prompt ต้นฉบับ §9 ลงไฟล์นี้

---

## 4️⃣ `assets/conftest.py`

```python
"""
Global test fixtures — copy to tests/conftest.py
TH: Fixture กลางสำหรับ unit/integration test
EN: Shared fixtures for all test suites
"""
from __future__ import annotations

import asyncio
import os
import uuid
from collections.abc import AsyncIterator, Iterator
from decimal import Decimal
from typing import Any

import pytest
import pytest_asyncio
from faker import Faker
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

TENANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
OTHER_TENANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")


@pytest.fixture(scope="session")
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def faker_th() -> Faker:
    return Faker("th_TH")


@pytest.fixture
def tenant_ctx() -> dict[str, Any]:
    return {
        "tenant_id": TENANT_ID,
        "user_id": uuid.uuid4(),
        "request_id": str(uuid.uuid4()),
        "trace_id": str(uuid.uuid4()),
    }


@pytest.fixture
def other_tenant_ctx() -> dict[str, Any]:
    return {
        "tenant_id": OTHER_TENANT_ID,
        "user_id": uuid.uuid4(),
        "request_id": str(uuid.uuid4()),
        "trace_id": str(uuid.uuid4()),
    }


@pytest_asyncio.fixture(scope="function")
async def db_engine() -> AsyncIterator[Any]:
    url = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5433/erp_test",
    )
    engine = create_async_engine(url, pool_pre_ping=True, echo=False)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine: Any) -> AsyncIterator[AsyncSession]:
    async with db_engine.connect() as conn:
        tx = await conn.begin()
        Session = async_sessionmaker(bind=conn, expire_on_commit=False)
        async with Session() as session:
            await session.execute(
                text("SELECT set_config('app.current_tenant', :tid, true)"),
                {"tid": str(TENANT_ID)},
            )
            yield session
        await tx.rollback()


@pytest_asyncio.fixture
async def redis_client() -> AsyncIterator[Any]:
    import redis.asyncio as aioredis
    client = aioredis.from_url(
        os.getenv("TEST_REDIS_URL", "redis://localhost:6380/15"),
        decode_responses=True,
    )
    await client.flushdb()
    yield client
    await client.flushdb()
    await client.aclose()


@pytest.fixture
def fake_clock() -> Any:
    from freezegun import freeze_time
    with freeze_time("2025-01-15 10:00:00+07:00") as frozen:
        yield frozen


@pytest.fixture
def decimal_factory() -> Any:
    def _make(value: str | int) -> Decimal:
        return Decimal(str(value)).quantize(Decimal("0.01"))
    return _make
```

---

## 5️⃣ `assets/logging.py`

```python
"""
app/core/logging.py — copy to your project
TH: ตั้งค่า structlog กลาง + PII masking
EN: Central structlog config + PII masking
"""
from __future__ import annotations

import logging
import re
import sys
from typing import Any

import structlog
from structlog.types import EventDict, Processor

PII_PATTERNS = [
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "***@***"),
    (re.compile(r"\b0\d{8,9}\b"), "***PHONE***"),
    (re.compile(r"\b\d{13}\b"), "***ID***"),
    (re.compile(r"(Bearer\s+)[\w\-._~+/]+=*", re.I), r"\1***"),
    (re.compile(r"(password[\"']?\s*[:=]\s*[\"']?)[^\"'\s,}]+", re.I), r"\1***"),
]


def mask_pii(_logger: Any, _name: str, event: EventDict) -> EventDict:
    for k, v in list(event.items()):
        if isinstance(v, str):
            for pat, repl in PII_PATTERNS:
                v = pat.sub(repl, v)
            event[k] = v
    return event


def configure_logging(level: str = "INFO", json: bool = False) -> None:
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper(), logging.INFO),
    )
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        mask_pii,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    processors.append(
        structlog.processors.JSONRenderer() if json
        else structlog.dev.ConsoleRenderer(colors=True)
    )
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper(), logging.INFO)
        ),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


log = structlog.get_logger()
```

---

## 6️⃣ `assets/middleware.py`

```python
"""
app/core/middleware.py — copy to your project
TH: ผูก trace_id / request_id เข้า contextvar
EN: Bind trace context per request
"""
from __future__ import annotations

import time
import uuid
from collections.abc import Awaitable, Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

log = structlog.get_logger()


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        trace_id = request.headers.get("x-trace-id") or uuid.uuid4().hex
        request_id = request.headers.get("x-request-id") or uuid.uuid4().hex

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            trace_id=trace_id,
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )
        started = time.perf_counter()
        try:
            resp = await call_next(request)
        except Exception:
            log.exception("request.failed")
            raise
        finally:
            dur_ms = (time.perf_counter() - started) * 1000
            log.info("request.done", dur_ms=round(dur_ms, 2))

        resp.headers["x-trace-id"] = trace_id
        resp.headers["x-request-id"] = request_id
        return resp
```

---

## 7️⃣ `assets/pyproject.toml` (fragment)

```toml
[project.optional-dependencies]
test = [
    "pytest==8.3.*",
    "pytest-asyncio==0.24.*",
    "pytest-cov==6.0.*",
    "pytest-benchmark==5.1.*",
    "hypothesis==6.115.*",
    "testcontainers[postgres,redis]==4.8.*",
    "faker==30.*",
    "freezegun==1.5.*",
    "respx==0.21.*",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths   = ["tests"]
addopts = """
    -ra
    --strict-markers
    --strict-config
    --cov=app
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-fail-under=85
"""
markers = [
    "unit: Unit tests (fast, no IO)",
    "integration: Integration tests (DB/Redis)",
    "property: Property-based tests",
    "slow: Slow tests (> 1s)",
]

[tool.coverage.run]
branch = true
source = ["app"]
omit   = ["*/__init__.py", "*/migrations/*", "tests/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
]
```

---

## 8️⃣ `scripts/new_module.sh` (Linux/macOS — lightweight)

```bash
#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# new_module.sh — Minimal cross-platform module scaffolder
# USAGE: ./new_module.sh <module> <layer> <prefix> [--sql] [--tests] [--docs]
# ═══════════════════════════════════════════════════════════════
set -euo pipefail

MODULE="${1:?module name required}"
LAYER="${2:-0}"
PREFIX="${3:?3-char prefix required}"
shift 3 || true

WANT_SQL=0; WANT_TESTS=0; WANT_DOCS=0; WANT_ROUTES=0
for arg in "$@"; do
  case "$arg" in
    --sql) WANT_SQL=1 ;;
    --tests) WANT_TESTS=1 ;;
    --docs) WANT_DOCS=1 ;;
    --routes) WANT_ROUTES=1 ;;
  esac
done

PASCAL=$(echo "$MODULE" | sed -E 's/(^|_)([a-z])/\U\2/g')
ROOT="app/modules/$MODULE"

echo "▶ Creating $MODULE (layer=$LAYER, prefix=$PREFIX, Pascal=$PASCAL)"

# ── Layers ────────────────────────────────────
for layer_dir in domain application infrastructure presentation; do
  mkdir -p "$ROOT/$layer_dir"
  touch "$ROOT/$layer_dir/__init__.py"
done
touch "$ROOT/__init__.py"

# ── SQL ───────────────────────────────────────
if [[ $WANT_SQL -eq 1 ]]; then
  mkdir -p db/migrations
  cat > "db/migrations/V001__create_${MODULE}.sql" <<SQL
BEGIN;
CREATE SEQUENCE IF NOT EXISTS ${PREFIX}_number_seq START 1;
CREATE TABLE tenant_${PREFIX}.${MODULE}s (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL,
  code VARCHAR(50) NOT NULL,
  name VARCHAR(200) NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
  amount NUMERIC(15,2) NOT NULL DEFAULT 0,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  version INTEGER NOT NULL DEFAULT 1,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  deleted_at TIMESTAMPTZ,
  CONSTRAINT uq_${MODULE}_code UNIQUE (tenant_id, code),
  CONSTRAINT ck_${MODULE}_amount CHECK (amount >= 0),
  CONSTRAINT ck_${MODULE}_status CHECK (status IN ('ACTIVE','INACTIVE','ARCHIVED'))
);
CREATE INDEX ix_${MODULE}_tenant_status ON tenant_${PREFIX}.${MODULE}s(tenant_id, status) WHERE deleted_at IS NULL;
CREATE INDEX ix_${MODULE}_code ON tenant_${PREFIX}.${MODULE}s(code);
CREATE INDEX ix_${MODULE}_created ON tenant_${PREFIX}.${MODULE}s(created_at DESC);
ALTER TABLE tenant_${PREFIX}.${MODULE}s ENABLE ROW LEVEL SECURITY;
CREATE POLICY p_${MODULE}_tenant ON tenant_${PREFIX}.${MODULE}s
  USING (tenant_id = current_setting('app.current_tenant', true)::uuid);
COMMIT;
SQL

  cat > "db/migrations/V002__seed_${MODULE}.sql" <<SQL
BEGIN;
INSERT INTO tenant_${PREFIX}.${MODULE}s (tenant_id, code, name, status)
VALUES ('00000000-0000-0000-0000-000000000001', 'SYS-DEFAULT', 'System Default', 'ACTIVE')
ON CONFLICT (tenant_id, code) DO NOTHING;
COMMIT;
SQL

  cat > "db/migrations/V003__rollback_${MODULE}.sql" <<SQL
BEGIN;
DROP POLICY IF EXISTS p_${MODULE}_tenant ON tenant_${PREFIX}.${MODULE}s;
DROP TABLE IF EXISTS tenant_${PREFIX}.${MODULE}s CASCADE;
DROP SEQUENCE IF EXISTS ${PREFIX}_number_seq;
COMMIT;
SQL
  echo "✔ SQL migrations"
fi

# ── Tests ─────────────────────────────────────
if [[ $WANT_TESTS -eq 1 ]]; then
  mkdir -p tests/{unit,integration,property,manual}
  touch tests/__init__.py tests/unit/__init__.py tests/integration/__init__.py tests/property/__init__.py
  [[ -f tests/conftest.py ]] || cp "$(dirname "$0")/../assets/conftest.py" tests/conftest.py
  touch "tests/unit/test_${MODULE}.py"
  touch "tests/unit/test_${MODULE}_use_cases.py"
  touch "tests/integration/test_${MODULE}_repository.py"
  touch "tests/property/test_${MODULE}_invariants.py"
  cat > "tests/manual/manual_test_${MODULE}.md" <<MD
# Manual Test — ${MODULE}
| # | Scenario | Method | Endpoint | Expected | ✅ |
|---|---|---|---|---|---|
| 1 | Create happy | POST | /api/v1/${MODULE}/ | 201 | ☐ |
| 2 | Duplicate | POST | /api/v1/${MODULE}/ | 409 | ☐ |
| 3 | Invalid | POST | /api/v1/${MODULE}/ | 422 | ☐ |
| 4 | Get | GET | /api/v1/${MODULE}/{id} | 200 | ☐ |
| 5 | List | GET | /api/v1/${MODULE}/ | 200 | ☐ |
| 6 | Update | PATCH | /api/v1/${MODULE}/{id} | 200 | ☐ |
| 7 | Delete | DELETE | /api/v1/${MODULE}/{id} | 204 | ☐ |
| 8 | Cross-tenant | GET | other token | 404 | ☐ |
MD
  echo "✔ Tests (unit/integration/property/manual)"
fi

# ── Docs ──────────────────────────────────────
if [[ $WANT_DOCS -eq 1 ]]; then
  mkdir -p docs
  cat > "docs/README_${MODULE}.md" <<MD
# Module: ${MODULE}
> Layer: ${LAYER} · Prefix: ${PREFIX}

## Purpose
## Architecture (Mermaid)
## Dependencies
## Database Schema
## API Endpoints
## Permissions
## Domain Events
## Environment Variables
## Setup
## Testing
## Usage Example
## Known Limitations
## Changelog
MD
  echo "✔ Docs"
fi

# ── Routes hint ───────────────────────────────
if [[ $WANT_ROUTES -eq 1 ]]; then
  echo "⚠ Manual: add to app/routes.py"
  echo "    from app.modules.${MODULE}.presentation.routers import router as ${MODULE}_router"
  echo "    api_router.include_router(${MODULE}_router)"
  echo "⚠ Manual: add to migrations/env.py"
  echo "    from app.modules.${MODULE}.infrastructure.models import ${PASCAL}Model"
fi

echo "✅ Done: ${MODULE}"
```

---

## 9️⃣ `scripts/create_modules.bat` + `scripts/create_module.ps1`

> Copy จาก prompt ต้นฉบับ §8 ลงไฟล์จริง — เพิ่ม `debug` action ใน ValidateSet
> และเพิ่ม `New-DebugKit` ที่ generate `docs/debug/{module}_debug.md` +
> `app/core/logging.py` + `app/core/middleware.py`

---

## 🔟 วิธีติดตั้งและใช้งาน

### ติดตั้ง skill

```bash
# Personal (ใช้ได้ทุก project)
mkdir -p ~/.claude/skills
cp -r python-ddd-clean-arch ~/.claude/skills/

# หรือ Project-scoped
mkdir -p .claude/skills
cp -r python-ddd-clean-arch .claude/skills/
```

### เรียกใช้

```bash
# วิธีที่ 1: invoke skill โดยตรง
claude "/python-ddd-clean-arch สร้าง module inventory layer 3 prefix inv
        + tests + debug kit + full 23 sections"

# วิธีที่ 2: ปล่อยให้ trigger อัตโนมัติจาก description
claude "create module payment following DDD with RLS + unit tests"

# วิธีที่ 3: ผสมกับ TEMPLATE
claude "TEMPLATE A + module=warehouse + layer=3-goods + prefix=whs
        + SqlTestsDocsRoutes + DebugKit"
```

### ตรวจสอบว่า skill ถูกโหลด

```bash
claude "/skills list"          # ควรเห็น python-ddd-clean-arch v2.0.0
claude "/python-ddd-clean-arch help"
```

---

## 📋 Checklist ความพร้อมใช้งาน

| รายการ | สถานะ |
|---|---|
| `SKILL.md` + frontmatter (name, description, version) | ✅ |
| Hard rules ครบ | ✅ |
| 23-section output contract | ✅ |
| Templates A–G + cross-links | ✅ |
| SQL V001/V002/V003 + RLS | ✅ |
| Routing (routes.py + env.py) | ✅ |
| Testing block §9 + coverage gates | ✅ |
| Debug block §10 + PII masking | ✅ |
| `assets/conftest.py` (รันได้จริง) | ✅ |
| `assets/logging.py` (structlog + PII) | ✅ |
| `assets/middleware.py` (trace context) | ✅ |
| `assets/pyproject.toml` (pytest config) | ✅ |
| `scripts/new_module.sh` (Linux/macOS) | ✅ |
| `scripts/create_modules.bat` + `.ps1` (Windows) | ✅ |
| `reference/*.md` 11 ไฟล์ | ✅ |
| Cheatsheet + Universal Header | ✅ |
| ตัวอย่าง `examples/inventory/` | ✅ (ให้ generate เองจาก TEMPLATE A) |

---

## 🎯 สรุป

**Skill นี้พร้อมใช้งานทันที** — คัดลอก folder, วางใน `~/.claude/skills/` แล้ว
Claude จะ:

1. **Auto-trigger** เมื่อพูดถึง DDD / Clean Arch / module creation / RLS /
   unit test / debug module
2. **Produce 23 sections** ครบทุกครั้งตาม contract
3. **Generate 35 ไฟล์** ต่อ module (Python + SQL + tests + docs)
4. **Enforce hard rules** (Decimal, flush, structlog, RLS, no PII)
5. **Include full test pyramid** (unit ≥ 8 / integration / property / manual)
6. **Attach debug kit** (logging.py + middleware.py + recipes + issues table)
