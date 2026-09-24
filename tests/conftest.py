"""tests/conftest.py — Global fixtures"""
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
    AsyncSession, async_sessionmaker, create_async_engine,
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
def decimal_factory() -> Any:
    def _make(value: str | int) -> Decimal:
        return Decimal(str(value)).quantize(Decimal("0.01"))
    return _make