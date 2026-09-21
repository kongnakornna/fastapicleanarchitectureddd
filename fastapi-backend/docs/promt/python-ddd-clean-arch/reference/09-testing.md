# 09 — Testing Block

> Test pyramid · conftest · templates · commands · coverage map

---

## 9.1 Test Pyramid

```mermaid
graph TD
    A["🔺 E2E / Manual (5%)<br/>8 scenarios"] --> B["🔷 Integration (25%)<br/>Repository + DB + Redis"]
    B --> C["🟩 Unit (70%)<br/>Domain / UseCase / Mapper"]
    C --> D["🟪 Property (bonus)<br/>Hypothesis invariants"]
```

| ระดับ | เป้าหมาย | เครื่องมือ | จำนวนขั้นต่ำ |
|---|---|---|---|
| Unit | Domain + Application logic | pytest + pytest-asyncio + unittest.mock | ≥ 8 / module |
| Integration | Repository + SQL + RLS | pytest + testcontainers + asyncpg | ≥ 4 / module |
| Property | Invariants | hypothesis | ≥ 3 / module |
| Manual | Smoke E2E | Postman / curl | 8 scenarios |

---

## 9.2 Dependencies (`pyproject.toml`)

```toml
[project.optional-dependencies]
test = [
    "pytest==8.3.*",
    "pytest-asyncio==0.24.*",
    "pytest-cov==6.0.*",
    "pytest-benchmark==5.1.*",
    "pytest-xdist==3.6.*",
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
    --cov-report=xml:coverage.xml
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
    "@abstractmethod",
]
```

---

## 9.3 `tests/conftest.py` — Fixtures กลาง

```python
"""
tests/conftest.py
Global fixtures — ใช้ร่วมทุก module
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
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

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

## 9.4 Unit Test — Domain Template

```python
"""
tests/unit/test_{module}.py — Domain Layer
"""
from __future__ import annotations

import uuid
from decimal import Decimal

import pytest

from app.modules.{module}.domain.entities import {Module}
from app.modules.{module}.domain.enums import {Module}Status
from app.modules.{module}.domain.exceptions import (
    InvalidAmountError,
    InvalidStatusTransitionError,
)
from app.modules.{module}.domain.value_objects import Money

pytestmark = pytest.mark.unit


@pytest.fixture
def tenant_id() -> uuid.UUID:
    return uuid.UUID("00000000-0000-0000-0000-000000000001")


@pytest.fixture
def make_{module}(tenant_id: uuid.UUID):
    def _make(
        code: str = "INV-001",
        name: str = "Sample",
        amount: Decimal = Decimal("100.00"),
        status: {Module}Status = {Module}Status.ACTIVE,
    ) -> {Module}:
        return {Module}.create(
            tenant_id=tenant_id, code=code, name=name,
            amount=amount, status=status,
        )
    return _make


class TestCreate:
    def test_create_sets_defaults(self, make_{module}) -> None:
        e = make_{module}()
        assert e.id is not None
        assert e.version == 1
        assert e.status is {Module}Status.ACTIVE
        assert e.deleted_at is None

    def test_create_with_zero_amount(self, make_{module}) -> None:
        e = make_{module}(amount=Decimal("0.00"))
        assert e.amount == Decimal("0.00")


class TestEdgeCases:
    def test_code_is_immutable(self, make_{module}) -> None:
        e = make_{module}()
        with pytest.raises(AttributeError):
            e.code = "NEW"  # type: ignore[misc]

    def test_amount_precision_quantized(self, make_{module}) -> None:
        e = make_{module}(amount=Decimal("100.005"))
        assert e.amount == Decimal("100.01")


class TestErrors:
    def test_negative_amount_raises(self, make_{module}) -> None:
        with pytest.raises(InvalidAmountError):
            make_{module}(amount=Decimal("-1.00"))

    def test_invalid_status_transition(self, make_{module}) -> None:
        e = make_{module}(status={Module}Status.ARCHIVED)
        with pytest.raises(InvalidStatusTransitionError):
            e.activate()

    def test_empty_code_raises(self, make_{module}) -> None:
        with pytest.raises(ValueError, match="code"):
            make_{module}(code="")


class TestMoneyVO:
    def test_money_add(self) -> None:
        a = Money(Decimal("10.00"))
        b = Money(Decimal("5.50"))
        assert (a + b).amount == Decimal("15.50")

    def test_money_currency_mismatch(self) -> None:
        a = Money(Decimal("10.00"), "THB")
        b = Money(Decimal("5.00"), "USD")
        with pytest.raises(ValueError, match="currency"):
            _ = a + b
```

---

## 9.5 Unit Test — Use Case Template

```python
"""
tests/unit/test_{module}_use_cases.py — Application Layer
"""
from __future__ import annotations

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules.{module}.application.exceptions import DuplicateCodeError
from app.modules.{module}.application.use_cases import Create{Module}UseCase
from app.modules.{module}.domain.entities import {Module}
from app.modules.{module}.domain.events import {Module}Created

pytestmark = pytest.mark.unit


@pytest.fixture
def repo() -> AsyncMock:
    r = AsyncMock()
    r.get_by_code.return_value = None
    r.save.side_effect = lambda e: e
    return r


@pytest.fixture
def cache() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def event_bus() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def idem() -> AsyncMock:
    m = AsyncMock()
    m.check_or_lock.return_value = None
    return m


@pytest.fixture
def uc(repo, cache, event_bus, idem, tenant_ctx) -> Create{Module}UseCase:
    return Create{Module}UseCase(
        repo=repo, cache=cache, event_bus=event_bus,
        idempotency=idem, ctx=tenant_ctx,
    )


class TestCreateUseCase:
    async def test_happy_path(self, uc, repo, event_bus) -> None:
        out = await uc.execute(
            code="INV-001", name="Test", amount=Decimal("100.00"),
            idempotency_key="k-1",
        )
        assert out.code == "INV-001"
        repo.save.assert_awaited_once()
        event_bus.publish.assert_awaited_once()
        evt = event_bus.publish.await_args.args[0]
        assert isinstance(evt, {Module}Created)

    async def test_duplicate_code_raises(self, uc, repo) -> None:
        repo.get_by_code.return_value = MagicMock(spec={Module})
        with pytest.raises(DuplicateCodeError):
            await uc.execute(
                code="INV-001", name="Dup", amount=Decimal("1.00"),
                idempotency_key="k-2",
            )
        repo.save.assert_not_awaited()

    async def test_cache_failure_does_not_break(
        self, uc, cache, event_bus
    ) -> None:
        cache.invalidate.side_effect = RuntimeError("redis down")
        out = await uc.execute(
            code="INV-002", name="X", amount=Decimal("1.00"),
            idempotency_key="k-3",
        )
        assert out.code == "INV-002"
        event_bus.publish.assert_awaited_once()

    async def test_readback_verification(self, uc, repo) -> None:
        await uc.execute(
            code="INV-003", name="X", amount=Decimal("1.00"),
            idempotency_key="k-4",
        )
        repo.get_by_id.assert_awaited_once()
```

---

## 9.6 Integration Test — Repository + RLS

```python
"""
tests/integration/test_{module}_repository.py
"""
from __future__ import annotations

import uuid
from decimal import Decimal

import pytest
from sqlalchemy import text

from app.modules.{module}.domain.entities import {Module}
from app.modules.{module}.infrastructure.repositories import (
    SQLAlchemy{Module}Repository,
)

pytestmark = pytest.mark.integration


@pytest.fixture
def repo(db_session) -> SQLAlchemy{Module}Repository:
    return SQLAlchemy{Module}Repository(session=db_session)


class TestRepository:
    async def test_save_and_get(self, repo, tenant_ctx) -> None:
        e = {Module}.create(
            tenant_id=tenant_ctx["tenant_id"],
            code=f"INV-{uuid.uuid4().hex[:6]}",
            name="Repo Test",
            amount=Decimal("99.99"),
        )
        saved = await repo.save(e)
        assert saved.id is not None
        fetched = await repo.get_by_id(saved.id)
        assert fetched is not None
        assert fetched.code == saved.code
        assert fetched.amount == Decimal("99.99")

    async def test_rls_blocks_other_tenant(
        self, repo, db_session, tenant_ctx, other_tenant_ctx
    ) -> None:
        e = {Module}.create(
            tenant_id=tenant_ctx["tenant_id"],
            code="INV-RLS-1", name="RLS", amount=Decimal("1.00"),
        )
        await repo.save(e)

        await db_session.execute(
            text("SELECT set_config('app.current_tenant', :tid, true)"),
            {"tid": str(other_tenant_ctx["tenant_id"])},
        )
        found = await repo.get_by_id(e.id)
        assert found is None

    async def test_unique_code_conflict(self, repo, tenant_ctx) -> None:
        code = f"INV-{uuid.uuid4().hex[:6]}"
        e1 = {Module}.create(
            tenant_id=tenant_ctx["tenant_id"],
            code=code, name="A", amount=Decimal("1.00"),
        )
        await repo.save(e1)
        e2 = {Module}.create(
            tenant_id=tenant_ctx["tenant_id"],
            code=code, name="B", amount=Decimal("2.00"),
        )
        with pytest.raises(Exception):
            await repo.save(e2)

    async def test_soft_delete_filter(self, repo, tenant_ctx) -> None:
        e = {Module}.create(
            tenant_id=tenant_ctx["tenant_id"],
            code=f"INV-{uuid.uuid4().hex[:6]}",
            name="Soft", amount=Decimal("1.00"),
        )
        saved = await repo.save(e)
        await repo.soft_delete(saved.id)
        found = await repo.get_by_id(saved.id)
        assert found is None
```

---

## 9.7 Property Test — Invariants

```python
"""
tests/property/test_{module}_invariants.py
"""
from __future__ import annotations

import uuid
from decimal import Decimal

import pytest
from hypothesis import given, settings, strategies as st

from app.modules.{module}.domain.entities import {Module}
from app.modules.{module}.domain.exceptions import InvalidAmountError
from app.modules.{module}.domain.value_objects import Money

pytestmark = pytest.mark.property

TENANT = uuid.UUID("00000000-0000-0000-0000-000000000001")

amounts = st.decimals(
    min_value=Decimal("0.00"),
    max_value=Decimal("999999999.99"),
    places=2,
    allow_nan=False,
    allow_infinity=False,
)

codes = st.text(
    alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-",
    min_size=1, max_size=50,
)


@settings(max_examples=100)
@given(amount=amounts, code=codes)
def test_non_negative_amount_always_valid(amount: Decimal, code: str) -> None:
    e = {Module}.create(
        tenant_id=TENANT, code=code or "X", name="P", amount=amount,
    )
    assert e.amount >= Decimal("0.00")


@settings(max_examples=100)
@given(amount=st.decimals(
    min_value=Decimal("-9999"), max_value=Decimal("-0.01"), places=2,
))
def test_negative_amount_always_rejected(amount: Decimal) -> None:
    with pytest.raises(InvalidAmountError):
        {Module}.create(
            tenant_id=TENANT, code="X", name="P", amount=amount,
        )


@settings(max_examples=100)
@given(a=amounts, b=amounts)
def test_sum_is_commutative(a: Decimal, b: Decimal) -> None:
    m1 = Money(a); m2 = Money(b)
    assert (m1 + m2).amount == (m2 + m1).amount
```

---

## 9.8 Manual Test Checklist

```markdown
# Manual Test — {module}

## Pre-conditions
- [ ] DB migrated (V001–V003)
- [ ] Redis running
- [ ] Kafka running (ถ้ามี)
- [ ] `.env` set TEST_DATABASE_URL

## Scenarios (8)
| # | Scenario | Method | Endpoint | Expected | ✅ |
|---|---|---|---|---|---|
| 1 | Create happy | POST | `/api/v1/{module}/` | 201 + body | ☐ |
| 2 | Create duplicate | POST | `/api/v1/{module}/` | 409 | ☐ |
| 3 | Create invalid amount | POST | `/api/v1/{module}/` | 422 | ☐ |
| 4 | Get by id | GET | `/api/v1/{module}/{id}` | 200 | ☐ |
| 5 | List + filter | GET | `/api/v1/{module}/?status=ACTIVE` | 200 | ☐ |
| 6 | Update | PATCH | `/api/v1/{module}/{id}` | 200 + version+1 | ☐ |
| 7 | Delete (soft) | DELETE | `/api/v1/{module}/{id}` | 204 + deleted_at | ☐ |
| 8 | Cross-tenant | GET | other tenant token | 404 | ☐ |

## Idempotency
- [ ] POST ซ้ำด้วย `Idempotency-Key` เดิม → ได้ response เดิม
- [ ] POST ด้วย key เดิม + payload ต่าง → 422

## Security
- [ ] ไม่มี token → 401
- [ ] token ผิด scope → 403
- [ ] SQL injection ที่ code → 422
```

---

## 9.9 Test Commands Cheatsheet

```bash
# ─── Run both ────────────────────────────────────
pytest                                  # ทั้งหมด
pytest -m unit                          # unit เท่านั้น
pytest -m integration                   # integration เท่านั้น
pytest -m "not slow"                    # ข้าม slow
pytest -m property                      # property

# ─── Single file / test ──────────────────────────
pytest tests/unit/test_inventory.py
pytest tests/unit/test_inventory.py::TestCreate::test_create_sets_defaults
pytest -k "duplicate or invalid"         # keyword match

# ─── Coverage ────────────────────────────────────
pytest --cov=app --cov-report=term-missing
pytest --cov=app --cov-report=html:htmlcov
pytest --cov=app --cov-fail-under=85

# ─── Debug ───────────────────────────────────────
pytest -x                                # หยุดที่ fail แรก
pytest --lf                              # last failed
pytest --ff                              # failed first
pytest -vv --tb=long                     # verbose + full traceback
pytest -s                                # แสดง print/stdout
pytest --pdb                             # drop เข้า pdb ตอน fail
pytest --pdbcls=IPython.terminal.debugger:TerminalPdb

# ─── Parallel ────────────────────────────────────
pytest -n auto                           # pytest-xdist

# ─── Benchmark ───────────────────────────────────
pytest --benchmark-only
pytest --benchmark-compare=0001
```

---

## 9.10 Coverage Map

| Layer | Coverage ขั้นต่ำ | เหตุผล |
|---|---|---|
| `domain/` | **95%** | Business logic ล้วน ไม่มี IO |
| `application/` | **90%** | Use cases |
| `infrastructure/` | **80%** | IO-bound, บางส่วน override ด้วย integration |
| `presentation/` | **70%** | Thin — วัดผ่าน integration |
| **รวมทั้งโปรเจกต์** | **85%** | CI gate |
```

--- 
