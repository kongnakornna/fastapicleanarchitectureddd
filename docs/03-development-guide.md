# Development Guide

Step-by-step guide for contributing to the ICMON Auto Repair FastAPI DDD project.

---

## Adding a New Module

Every module follows the **Onion Architecture** with 4 layers. Below is a complete step-by-step walkthrough using a hypothetical `supplier` module.

### Step 1: Create the Module Directory Structure

```
app/modules/supplier/
  __init__.py
  domain/
    __init__.py
    entities/
      __init__.py
      supplier.py        # SQLAlchemy entity + domain model
    value_objects.py      # (optional) Value objects
    services.py           # (optional) Domain services
    mappers.py            # (optional) Entity <-> Schema mappers
  application/
    __init__.py
    use_case.py           # Business logic
    interfaces.py         # Repository port (ABC)
    enums.py              # (optional) Module-specific enums
  infrastructure/
    __init__.py
    supplier_repository.py  # Repository implementation
  presentation/
    __init__.py
    router.py             # FastAPI router
    schemas.py            # Pydantic request/response schemas
    dependencies.py       # Dependency injection
    exceptions.py         # Module-specific exceptions
    docs.py               # (optional) OpenAPI docs metadata
```

### Step 2: Define the Domain Entity

`app/modules/supplier/domain/entities/supplier.py`:

```python
from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModel


class Supplier(BaseModel):
    __tablename__ = "m_supplier"

    supplier_code: Mapped[str] = mapped_column(
        String(20), name="supplier_code", unique=True, comment="Supplier code"
    )
    name: Mapped[str] = mapped_column(
        String(200), name="name", comment="Supplier name"
    )
    contact_person: Mapped[str | None] = mapped_column(
        String(100), name="contact_person", nullable=True, comment="Contact person"
    )
    phone: Mapped[str | None] = mapped_column(
        String(20), name="phone", nullable=True, comment="Phone number"
    )
    email: Mapped[str | None] = mapped_column(
        String(100), name="email", nullable=True, comment="Email"
    )
    address: Mapped[str | None] = mapped_column(
        Text, name="address", nullable=True, comment="Address"
    )
```

**Convention:** All business entities extend `BaseModel` (which provides `id`, `is_active`, `created_at`, `updated_at`).

### Step 3: Create the Repository Interface (Application Layer)

`app/modules/supplier/application/interfaces.py`:

```python
from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.supplier.domain.entities.supplier import Supplier


class ISupplierRepository(ABC):
    @abstractmethod
    async def find_by_id(self, supplier_id: UUID) -> Supplier | None: ...

    @abstractmethod
    async def find_all_paginated(
        self, page: int = 1, page_size: int = 10
    ) -> tuple[list[Supplier], int]: ...

    @abstractmethod
    async def create(self, supplier: Supplier) -> Supplier: ...

    @abstractmethod
    async def update(self, supplier: Supplier) -> Supplier: ...

    @abstractmethod
    async def delete(self, supplier_id: UUID) -> bool: ...
```

### Step 4: Implement the Repository

`app/modules/supplier/infrastructure/supplier_repository.py`:

```python
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.supplier.application.interfaces import ISupplierRepository
from app.modules.supplier.domain.entities.supplier import Supplier


class SupplierRepository(ISupplierRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, supplier_id: UUID) -> Supplier | None:
        result = await self._session.execute(
            select(Supplier).where(Supplier.id == supplier_id)
        )
        return result.scalar_one_or_none()

    async def find_all_paginated(
        self, page: int = 1, page_size: int = 10
    ) -> tuple[list[Supplier], int]:
        count_result = await self._session.execute(
            select(func.count()).select_from(Supplier).where(
                Supplier.is_active.is_(True)
            )
        )
        total = count_result.scalar() or 0
        query = (
            select(Supplier)
            .where(Supplier.is_active.is_(True))
            .order_by(Supplier.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all()), total

    async def create(self, supplier: Supplier) -> Supplier:
        self._session.add(supplier)
        await self._session.flush()
        return supplier

    async def update(self, supplier: Supplier) -> Supplier:
        await self._session.flush()
        return supplier

    async def delete(self, supplier_id: UUID) -> bool:
        supplier = await self.find_by_id(supplier_id)
        if supplier:
            supplier.is_active = False
            await self._session.flush()
            return True
        return False
```

### Step 5: Write the Use Case

`app/modules/supplier/application/use_case.py`:

```python
from uuid import UUID

from app.modules.supplier.application.interfaces import ISupplierRepository
from app.modules.supplier.domain.entities.supplier import Supplier


class SupplierUseCase:
    def __init__(self, supplier_repository: ISupplierRepository) -> None:
        self._repo = supplier_repository

    async def get_suppliers(
        self, page: int = 1, page_size: int = 10
    ) -> tuple[list[Supplier], int]:
        return await self._repo.find_all_paginated(page, page_size)

    async def get_supplier(self, supplier_id: UUID) -> Supplier | None:
        return await self._repo.find_by_id(supplier_id)

    async def create_supplier(self, supplier: Supplier) -> Supplier:
        return await self._repo.create(supplier)

    async def update_supplier(
        self, supplier_id: UUID, values: dict
    ) -> Supplier | None:
        supplier = await self._repo.find_by_id(supplier_id)
        if not supplier:
            return None
        for key, value in values.items():
            if hasattr(supplier, key):
                setattr(supplier, key, value)
        return await self._repo.update(supplier)

    async def delete_supplier(self, supplier_id: UUID) -> bool:
        return await self._repo.delete(supplier_id)
```

### Step 6: Create Pydantic Schemas

`app/modules/supplier/presentation/schemas.py`:

```python
from pydantic import BaseModel


class SupplierCreateRequest(BaseModel):
    supplier_code: str
    name: str
    contact_person: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None


class SupplierUpdateRequest(BaseModel):
    name: str | None = None
    contact_person: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None


class SupplierResponse(BaseModel):
    id: str
    supplier_code: str
    name: str
    contact_person: str | None
    phone: str | None
    email: str | None
    address: str | None
    created_at: str
    updated_at: str


class PaginatedSuppliersResponse(BaseModel):
    items: list[SupplierResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
```

### Step 7: Create Dependencies

`app/modules/supplier/presentation/dependencies.py`:

```python
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.modules.supplier.application.use_case import SupplierUseCase
from app.modules.supplier.infrastructure.supplier_repository import SupplierRepository


async def get_supplier_use_case(
    session: AsyncSession = Depends(get_async_session),
) -> SupplierUseCase:
    return SupplierUseCase(
        supplier_repository=SupplierRepository(session)
    )
```

### Step 8: Write the Router

`app/modules/supplier/presentation/router.py`:

```python
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.modules.supplier.application.use_case import SupplierUseCase
from app.modules.supplier.domain.entities.supplier import Supplier
from app.modules.supplier.infrastructure.supplier_repository import SupplierRepository
from app.modules.supplier.presentation.schemas import (
    PaginatedSuppliersResponse,
    SupplierCreateRequest,
    SupplierResponse,
    SupplierUpdateRequest,
)

router = APIRouter(prefix="/supplier", tags=["Supplier"])


async def get_supplier_use_case(
    session: AsyncSession = Depends(get_async_session),
) -> SupplierUseCase:
    return SupplierUseCase(supplier_repository=SupplierRepository(session))


def _supplier_to_response(s: Supplier) -> SupplierResponse:
    return SupplierResponse(
        id=str(s.id),
        supplier_code=s.supplier_code,
        name=s.name,
        contact_person=s.contact_person,
        phone=s.phone,
        email=s.email,
        address=s.address,
        created_at=s.created_at.isoformat() if s.created_at else "",
        updated_at=s.updated_at.isoformat() if s.updated_at else "",
    )


@router.get("/")
async def get_suppliers(
    page: int = 1,
    per_page: int = 10,
    use_case: SupplierUseCase = Depends(get_supplier_use_case),
) -> PaginatedSuppliersResponse:
    per_page = min(per_page, 100)
    suppliers, total = await use_case.get_suppliers(page=page, page_size=per_page)
    total_pages = (total + per_page - 1) // per_page
    return PaginatedSuppliersResponse(
        items=[_supplier_to_response(s) for s in suppliers],
        total=total, page=page, per_page=per_page, total_pages=total_pages,
    )


@router.post("/")
async def create_supplier(
    payload: SupplierCreateRequest,
    use_case: SupplierUseCase = Depends(get_supplier_use_case),
) -> SupplierResponse:
    supplier = Supplier(
        supplier_code=payload.supplier_code,
        name=payload.name,
        contact_person=payload.contact_person,
        phone=payload.phone,
        email=payload.email,
        address=payload.address,
    )
    result = await use_case.create_supplier(supplier)
    return _supplier_to_response(result)


@router.get("/{supplier_id}")
async def get_supplier(
    supplier_id: str,
    use_case: SupplierUseCase = Depends(get_supplier_use_case),
) -> SupplierResponse:
    from uuid import UUID
    supplier = await use_case.get_supplier(UUID(supplier_id))
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return _supplier_to_response(supplier)


@router.put("/{supplier_id}")
async def update_supplier(
    supplier_id: str,
    payload: SupplierUpdateRequest,
    use_case: SupplierUseCase = Depends(get_supplier_use_case),
) -> SupplierResponse:
    from uuid import UUID
    values = payload.model_dump(exclude_none=True)
    supplier = await use_case.update_supplier(UUID(supplier_id), values)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return _supplier_to_response(supplier)


@router.delete("/{supplier_id}")
async def delete_supplier(
    supplier_id: str,
    use_case: SupplierUseCase = Depends(get_supplier_use_case),
) -> dict[str, bool]:
    from uuid import UUID
    success = await use_case.delete_supplier(UUID(supplier_id))
    if not success:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return {"success": True}
```

### Step 9: Register the Router

In `app/app.py`, add:

```python
from app.modules.supplier.presentation.router import router as supplier_router

# Add to the routers list:
routers = [
    ...
    supplier_router,
]
```

### Step 10: Create an Alembic Migration

```bash
alembic revision --autogenerate -m "add supplier tables"
alembic upgrade head
```

---

## Code Conventions

### Naming

| Item              | Convention                          | Example                     |
|-------------------|-------------------------------------|-----------------------------|
| Module directory  | lowercase, no separators            | `purchaseorder`             |
| Table name        | `m_` prefix (business), `iot_` prefix (IoT) | `m_supplier`    |
| SQLAlchemy model  | `PascalCase` + `Model` (infra)      | `UserModel`, `SessionModel` |
| Domain entity     | `PascalCase` (no suffix)            | `Customer`, `WosOrder`      |
| Use case class   | `PascalCase` + `UseCase`/`UseCases` | `CustomerUseCase`           |
| Repository       | `PascalCase` + `Repository`         | `CustomerRepository`        |
| Router           | `snake_case` variable, module-level  | `router = APIRouter(...)`   |
| Pydantic schema  | `PascalCase` + `Request`/`Response` | `CustomerCreateRequest`     |
| UUID columns     | `UUID(as_uuid=True)`                | All PKs and FKs             |

### File Naming

| Layer             | File Name              | Example                          |
|-------------------|------------------------|----------------------------------|
| Router            | `router.py` or `routers.py` | `customer/router.py`       |
| Schemas           | `schemas.py`           | `customer/schemas.py`            |
| Dependencies      | `dependencies.py`      | `customer/dependencies.py`       |
| Exceptions        | `exceptions.py`        | `customer/exceptions.py`         |
| Use case          | `use_case.py` or `use_cases.py` | `customer/use_case.py`  |
| Repository        | `{name}_repository.py` | `customer_repository.py`         |
| Domain entities   | `entities.py` or `entities/{name}.py` | `entities/customer.py` |

### Pagination

All list endpoints use consistent pagination:

**Query params:** `page` (default 1), `per_page` (default 10, max 100)

**Response:**
```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "per_page": 10,
  "total_pages": 15
}
```

### Soft Delete

All entities use `is_active = False` for soft deletion. Never hard-delete business records.

### Error Handling

Module-specific exceptions inherit from `StandardException`:

```python
# app/modules/supplier/presentation/exceptions.py
from app.modules.shared.presentation.exceptions import StandardException


class SupplierException(StandardException):
    def __init__(self):
        super().__init__(
            status_code=500,
            message="An error occurred in the supplier module.",
        )
```

Router pattern:
```python
try:
    # ... business logic
except StandardException:
    raise
except DomainError as e:
    raise DomainException(e)
except Exception as e:
    logger.opt(exception=e).error("Error message")
    raise SupplierException()
```

### Ruff Configuration

From `pyproject.toml`:
- Line length: 100
- Python target: 3.13
- Enabled rules: `E`, `F`, `W`, `I`, `N`, `UP`, `B`, `A`, `C4`, `SIM`
- Ignored: `B008` (Depends in default args)

---

## Testing Approach

### Directory Structure

```
test/
  modules/
    {module}/
      __init__.py
      domain/
        __init__.py
        test_entities.py        # Domain entity tests
        test_value_objects.py   # Value object tests
        test_mappers.py         # Mapper tests
      application/
        __init__.py
        test_use_cases.py       # Use case tests (with mocked repos)
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific module tests
pytest test/modules/authentication/

# Run with verbose output
pytest -v

# Run specific test file
pytest test/modules/user/domain/test_entities.py
```

### Test Conventions

- Tests use `pytest` with `asyncio_mode = "auto"`
- Domain tests verify entity validation and business rules
- Application tests mock repository interfaces and verify use case logic
- Presentation layer tests are integration tests via `TestClient`

### Example Domain Test

```python
# test/modules/supplier/domain/test_entities.py
import pytest
from app.modules.supplier.domain.entities.supplier import Supplier


class TestSupplier:
    def test_supplier_creation(self):
        supplier = Supplier(
            supplier_code="SUP-001",
            name="Thai Auto Parts Co.",
        )
        assert supplier.supplier_code == "SUP-001"
        assert supplier.name == "Thai Auto Parts Co."
```

### Example Use Case Test

```python
# test/modules/supplier/application/test_use_cases.py
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from app.modules.supplier.application.use_case import SupplierUseCase


class TestSupplierUseCase:
    @pytest.fixture
    def mock_repo(self):
        repo = AsyncMock()
        repo.find_all_paginated.return_value = ([], 0)
        return repo

    @pytest.fixture
    def use_case(self, mock_repo):
        return SupplierUseCase(supplier_repository=mock_repo)

    async def test_get_suppliers(self, use_case, mock_repo):
        suppliers, total = await use_case.get_suppliers(page=1, page_size=10)
        assert total == 0
        mock_repo.find_all_paginated.assert_called_once_with(1, 10)
```

---

## Migration Workflow

### Creating a Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "description of changes"

# Review the generated file in migrations/versions/
# Edit if needed (especially for data migrations)

# Apply migration
alembic upgrade head
```

### Rolling Back

```bash
# Rollback one step
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>
```

### Migration File Naming

Alembic auto-generates names like `2026_07_21_1431_4586f82a4d7e.py`. When creating manually, use the format:

```
YYYY_MM_DD_HHMM_<hash>.py
```

### Best Practices

1. **Always review** auto-generated migrations before applying
2. **Never edit** applied migrations; create a new one instead
3. **Test rollback** paths for every migration
4. **Separate** schema changes from data migrations
5. **Add indexes** explicitly in migrations for performance-critical queries

---

## Project Quick Reference

### Environment Variables

All configuration is in `.env` (see `.env.example`). Key groups:

| Group         | Variables                                        |
|---------------|--------------------------------------------------|
| Application   | `APPLICATION_TITLE`, `APPLICATION_ENVIRONMENT`, etc. |
| Auth/JWT      | `JWT_ISSUER`, `JWT_AUDIENCE`, key paths          |
| PostgreSQL    | `POSTGRESQL_HOST`, `POSTGRESQL_DATABASE`, etc.   |
| Redis         | `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`     |
| InfluxDB      | `INFLUXDB_URL`, `INFLUXDB_TOKEN`, `INFLUXDB_ORG` |
| MQTT          | `MQTT_BROKER`, `MQTT_USERNAME`, `MQTT_PASSWORD`  |
| Security      | `SECURITY_ALLOW_ORIGINS`, `AUTH_API_KEY`         |

### Makefile Commands

| Command                   | Description                           |
|---------------------------|---------------------------------------|
| `make start`              | Build and start all Docker services   |
| `make start-silent`       | Start in detached mode                |
| `make delete`             | Stop and remove all containers        |
| `make dependencies-up`    | Start only Postgres + admin tools     |
| `make dependencies-down`  | Stop dependency services              |

### Key Files

| File                       | Purpose                               |
|----------------------------|---------------------------------------|
| `app/app.py`              | FastAPI app, middleware, routers       |
| `app/core/settings.py`    | All environment variables             |
| `app/core/database.py`    | SQLAlchemy engines + sessions         |
| `app/core/security.py`    | Authentication dependencies           |
| `alembic.ini`             | Alembic configuration                 |
| `pyproject.toml`          | Dependencies, Ruff, pytest config     |
| `seed_admin.py`           | Seed initial admin user               |
