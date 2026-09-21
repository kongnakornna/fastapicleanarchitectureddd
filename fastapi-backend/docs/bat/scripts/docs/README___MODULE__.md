# Module: inventory

> Layer: 3 | Prefix: inv | Version: 1.0.0

## Purpose

TH: อธิบายวัตถุประสงค์ของ module inventory
EN: describe purpose of inventory module

## Database Schema

CREATE TABLE tenant_inv.inventorys (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    code VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    status VARCHAR(20) NOT NULL,
    amount NUMERIC(15,2) NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

## Migrations

`migrations/versions/` ships **empty** — the first migration creates the
whole schema. The application runs `alembic upgrade head` on startup, so
a fresh stack migrates itself.

    make migration m="create_inventory_model"   # autogenerate
    make migrate                                 # apply

A new model must be imported in `migrations/env.py` **and** added to its
`_ = [...]` list — see `migrations/versions/db/REGISTER_inventory.md`.
Autogenerate only sees registered models, and worse, it emits a
`drop_table` for a live table whose model it cannot see.

## Caching

Postgres is the source of truth. Redis is an accelerator you must be able
to lose at any moment.

**Read-through**

    UC -> Redis.get(key)
          hit  -> return entity
          miss -> UC reads DB -> UC best-effort set(key)

**Invalidation — tombstone first**

    1. cache.invalidate() writes tombstone (TTL) BEFORE DEL entry
    2. cache.set()        checks tombstone BEFORE writing
    3. tombstones outlive the longest plausible read-then-write window

This closes the race where a slow reader writes a stale snapshot to cache
*after* the writer has already deleted the key.

**Namespacing & versioning**

    REDIS_NAMESPACE = f"{REDIS_KEY_PREFIX}:v{REDIS_CACHE_VERSION}"

Bump `REDIS_CACHE_VERSION` whenever the serialized payload changes — the
previous generation becomes unreachable and expires by TTL on its own.

## API Endpoints

| Method | Path | Description | Auth |
|---|---|---|---|
| POST   | /api/v1/inventory/      | สร้างใหม่ | yes |
| GET    | /api/v1/inventory/      | list      | yes |
| GET    | /api/v1/inventory/{id}  | ดูตาม id  | yes |
| PATCH  | /api/v1/inventory/{id}  | แก้ไข     | yes |
| DELETE | /api/v1/inventory/{id}  | soft del  | yes |

## Domain Events

| Event | Trigger | Payload |
|---|---|---|
| InventoryCreated | after create | id, code, tenant_id |
| InventoryUpdated | after update | id, changes |
| InventoryDeleted | after delete | id, deleted_at |

## Environment Variables

    DATABASE_URL=postgresql+asyncpg://...
    REDIS_URL=redis://...
    KAFKA_BOOTSTRAP=localhost:9092

    # Redis (see Migrations.txt)
    REDIS_KEY_PREFIX=erp
    REDIS_CACHE_VERSION=1
    REDIS_DEFAULT_TTL_SECONDS=3600
    REDIS_SESSION_TTL_SECONDS=1800
    REDIS_TOMBSTONE_TTL_SECONDS=30
    REDIS_FLUSH_ON_STARTUP=True
    REDIS_MAX_CONNECTIONS=50

## Setup

    alembic upgrade head
    uvicorn app.main:app --reload

## Testing

    pytest tests/unit/test_inventory.py -v
    pytest tests/integration/test_inventory_repository.py -v
    pytest --cov=app.modules.inventory --cov-fail-under=85

## Usage Example

    curl -X POST http://localhost:8000/api/v1/inventory/ \
      -H "Authorization: Bearer $TOKEN" \
      -H "Idempotency-Key: $(uuidgen)" \
      -H "Content-Type: application/json" \
      -d '{"code":"X-001","name":"Sample","amount":"100.00"}'

## Changelog

| Version | Date | Changes |
|---|---|---|
| 1.0.0 | YYYY-MM-DD | initial release |