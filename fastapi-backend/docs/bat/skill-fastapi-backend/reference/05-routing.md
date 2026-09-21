# 05 — Routing Block

> ต้อง register 2 ไฟล์: `app/routes.py` (router) + `migrations/env.py` (model)

---

## 📄 `app/routes.py`

```python
"""
app/routes.py
TH: รวม router ทั้งหมดของระบบ แยกตาม layer
EN: Aggregate all routers by layer
"""
from fastapi import APIRouter

# ─── Layer 0: Core ────────────────────────────────
from app.modules.events.presentation.routers import router as events_router
from app.modules.audit.presentation.routers import router as audit_router
from app.modules.idempotency.presentation.routers import router as idem_router

# ─── Layer 1: Foundation ──────────────────────────
from app.modules.tenant.presentation.routers import router as tenant_router
from app.modules.user.presentation.routers import router as user_router
from app.modules.auth.presentation.routers import router as auth_router

# ─── Layer 2: Money ───────────────────────────────
from app.modules.invoice.presentation.routers import router as invoice_router
from app.modules.payment.presentation.routers import router as payment_router

# ─── Layer 3: Goods ───────────────────────────────
from app.modules.{module}.presentation.routers import router as {module}_router  # ← เพิ่ม

# ─── API v1 ───────────────────────────────────────
api_router = APIRouter(prefix="/api/v1")

# Layer 0
api_router.include_router(events_router)
api_router.include_router(audit_router)
api_router.include_router(idem_router)

# Layer 1
api_router.include_router(auth_router)
api_router.include_router(tenant_router)
api_router.include_router(user_router)

# Layer 2
api_router.include_router(invoice_router)
api_router.include_router(payment_router)

# Layer 3
api_router.include_router({module}_router)  # ← เพิ่ม

# ─── Root ─────────────────────────────────────────
from app.core.health import router as health_router

router = APIRouter()
router.include_router(api_router)
router.include_router(health_router)
```

---

## 📄 `presentation/routers.py`

```python
"""
app/modules/{module}/presentation/routers.py
TH: HTTP router ของ module {module}
EN: HTTP router for {module} module
"""
from __future__ import annotations

import uuid
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status

from app.modules.{module}.application.exceptions import (
    DuplicateCodeError,
    {Module}NotFoundError,
)
from app.modules.{module}.application.use_cases import (
    Create{Module}UseCase,
    Delete{Module}UseCase,
    Get{Module}UseCase,
    List{Module}UseCase,
    Update{Module}UseCase,
)
from app.modules.{module}.domain.exceptions import DomainError
from app.modules.{module}.presentation.dependencies import (
    get_create_uc,
    get_delete_uc,
    get_get_uc,
    get_list_uc,
    get_update_uc,
)
from app.modules.{module}.presentation.docs import (
    RESPONSE_CREATE_201,
    RESPONSE_ERROR_400,
    RESPONSE_ERROR_404,
    RESPONSE_ERROR_409,
    RESPONSE_ERROR_422,
)
from app.modules.{module}.presentation.schemas import (
    {Module}CreateRequest,
    {Module}ListResponse,
    {Module}Response,
    {Module}UpdateRequest,
)

log = structlog.get_logger()
router = APIRouter(prefix="/{module}", tags=["{Module}"])


# ═══════════════════════════════════════════════════════════════
# CREATE
# ═══════════════════════════════════════════════════════════════
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="สร้าง {module}",
    operation_id="create_{module}",
    response_model={Module}Response,
    responses={
        201: RESPONSE_CREATE_201,
        400: RESPONSE_ERROR_400,
        409: RESPONSE_ERROR_409,
        422: RESPONSE_ERROR_422,
    },
)
async def create_{module}(
    payload: {Module}CreateRequest,
    idem_key: Annotated[str, Header(alias="Idempotency-Key", min_length=8, max_length=128)],
    uc: Annotated[Create{Module}UseCase, Depends(get_create_uc)],
) -> {Module}Response:
    """TH: สร้าง entity ใหม่ (idempotent) | EN: Create entity (idempotent)"""
    log.info("http.create.start", code=payload.code, idem=idem_key[:8])
    try:
        entity = await uc.execute(**payload.model_dump(), idempotency_key=idem_key)
    except DuplicateCodeError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(e)) from e
    except DomainError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    return {Module}Response.model_validate(entity, from_attributes=True)


# ═══════════════════════════════════════════════════════════════
# LIST
# ═══════════════════════════════════════════════════════════════
@router.get(
    "/",
    summary="รายการ {module}",
    operation_id="list_{module}",
    response_model={Module}ListResponse,
)
async def list_{module}(
    uc: Annotated[List{Module}UseCase, Depends(get_list_uc)],
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    q: Annotated[str | None, Query(max_length=100)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> {Module}ListResponse:
    """TH: list + filter + paginate | EN: list with filter + pagination"""
    items, total = await uc.execute(status=status_filter, q=q, limit=limit, offset=offset)
    return {Module}ListResponse(
        items=[{Module}Response.model_validate(x, from_attributes=True) for x in items],
        total=total,
        limit=limit,
        offset=offset,
    )


# ═══════════════════════════════════════════════════════════════
# GET BY ID
# ═══════════════════════════════════════════════════════════════
@router.get(
    "/{entity_id}",
    summary="ดู {module} ตาม id",
    operation_id="get_{module}",
    response_model={Module}Response,
    responses={404: RESPONSE_ERROR_404},
)
async def get_{module}(
    entity_id: uuid.UUID,
    uc: Annotated[Get{Module}UseCase, Depends(get_get_uc)],
) -> {Module}Response:
    try:
        entity = await uc.execute(entity_id=entity_id)
    except {Module}NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return {Module}Response.model_validate(entity, from_attributes=True)


# ═══════════════════════════════════════════════════════════════
# UPDATE
# ═══════════════════════════════════════════════════════════════
@router.patch(
    "/{entity_id}",
    summary="แก้ไข {module}",
    operation_id="update_{module}",
    response_model={Module}Response,
    responses={404: RESPONSE_ERROR_404, 409: RESPONSE_ERROR_409},
)
async def update_{module}(
    entity_id: uuid.UUID,
    payload: {Module}UpdateRequest,
    uc: Annotated[Update{Module}UseCase, Depends(get_update_uc)],
) -> {Module}Response:
    try:
        entity = await uc.execute(entity_id=entity_id, **payload.model_dump(exclude_unset=True))
    except {Module}NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except DomainError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    return {Module}Response.model_validate(entity, from_attributes=True)


# ═══════════════════════════════════════════════════════════════
# DELETE (soft)
# ═══════════════════════════════════════════════════════════════
@router.delete(
    "/{entity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="ลบ {module} (soft delete)",
    operation_id="delete_{module}",
    responses={404: RESPONSE_ERROR_404},
)
async def delete_{module}(
    entity_id: uuid.UUID,
    uc: Annotated[Delete{Module}UseCase, Depends(get_delete_uc)],
) -> None:
    try:
        await uc.execute(entity_id=entity_id)
    except {Module}NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e)) from e
```

---

## 📄 `presentation/dependencies.py`

```python
"""
app/modules/{module}/presentation/dependencies.py
TH: DI container ของ module
EN: DI container for module
"""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.context import RequestContext, get_context
from app.core.events import EventBus, get_event_bus
from app.core.idempotency import IdempotencyStore, get_idempotency_store
from app.modules.{module}.application.use_cases import (
    Create{Module}UseCase,
    Delete{Module}UseCase,
    Get{Module}UseCase,
    List{Module}UseCase,
    Update{Module}UseCase,
)
from app.modules.{module}.infrastructure.caches import Redis{Module}Cache
from app.modules.{module}.infrastructure.repositories import SQLAlchemy{Module}Repository


def get_{module}_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SQLAlchemy{Module}Repository:
    return SQLAlchemy{Module}Repository(session=session)


def get_{module}_cache() -> Redis{Module}Cache:
    return Redis{Module}Cache()


# ─── Use Case factories ───────────────────────────
async def get_create_uc(
    repo: Annotated[SQLAlchemy{Module}Repository, Depends(get_{module}_repo)],
    cache: Annotated[Redis{Module}Cache, Depends(get_{module}_cache)],
    bus: Annotated[EventBus, Depends(get_event_bus)],
    idem: Annotated[IdempotencyStore, Depends(get_idempotency_store)],
    ctx: Annotated[RequestContext, Depends(get_context)],
) -> Create{Module}UseCase:
    return Create{Module}UseCase(repo=repo, cache=cache, bus=bus, idem=idem, ctx=ctx)


async def get_get_uc(
    repo: Annotated[SQLAlchemy{Module}Repository, Depends(get_{module}_repo)],
    cache: Annotated[Redis{Module}Cache, Depends(get_{module}_cache)],
    ctx: Annotated[RequestContext, Depends(get_context)],
) -> Get{Module}UseCase:
    return Get{Module}UseCase(repo=repo, cache=cache, ctx=ctx)


async def get_list_uc(
    repo: Annotated[SQLAlchemy{Module}Repository, Depends(get_{module}_repo)],
    ctx: Annotated[RequestContext, Depends(get_context)],
) -> List{Module}UseCase:
    return List{Module}UseCase(repo=repo, ctx=ctx)


async def get_update_uc(
    repo: Annotated[SQLAlchemy{Module}Repository, Depends(get_{module}_repo)],
    cache: Annotated[Redis{Module}Cache, Depends(get_{module}_cache)],
    bus: Annotated[EventBus, Depends(get_event_bus)],
    ctx: Annotated[RequestContext, Depends(get_context)],
) -> Update{Module}UseCase:
    return Update{Module}UseCase(repo=repo, cache=cache, bus=bus, ctx=ctx)


async def get_delete_uc(
    repo: Annotated[SQLAlchemy{Module}Repository, Depends(get_{module}_repo)],
    cache: Annotated[Redis{Module}Cache, Depends(get_{module}_cache)],
    bus: Annotated[EventBus, Depends(get_event_bus)],
    ctx: Annotated[RequestContext, Depends(get_context)],
) -> Delete{Module}UseCase:
    return Delete{Module}UseCase(repo=repo, cache=cache, bus=bus, ctx=ctx)
```

---

## ✅ Routing Checklist

```markdown
- [ ] import router ใน `app/routes.py`
- [ ] `include_router({module}_router)` อยู่ layer ถูก
- [ ] prefix ไม่ซ้ำกับ module อื่น
- [ ] tags ถูกต้อง (แสดงใน Swagger)
- [ ] เปิด `http://localhost:8000/docs` → เห็น endpoint ใหม่
- [ ] เปิด `http://localhost:8000/openapi.json` → เห็น schema
- [ ] `migrations/env.py` import model แล้ว
- [ ] ทดสอบ `GET /api/v1/{module}/` → 200
```

---

## 🚫 ข้อห้าม

```markdown
❌ prefix ซ้ำกับ module อื่น
❌ ใส่ router ผิด layer
❌ ลืม import model ใน env.py
❌ tag ซ้ำ / สะกดผิด
❌ business logic ใน router
❌ return ORM object ตรง ๆ (ต้องผ่าน schema)
❌ ใช้ Depends ที่ไม่ cache (ควรใช้ cache=True default)
```
```

--- 
