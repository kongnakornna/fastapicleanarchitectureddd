"""
Audit Test Fixtures — fixture สำหรับทดสอบ audit
Audit Test Fixtures — pytest fixtures
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock

import pytest
from audit.domain.entities import AuditLog


@pytest.fixture
def sample_before() -> dict[str, Any]:
    return {"status": "DRAFT", "amount": 100.0, "note": "old"}


@pytest.fixture
def sample_after() -> dict[str, Any]:
    return {"status": "APPROVED", "amount": 150.0, "note": "new"}


@pytest.fixture
def sample_log(sample_before, sample_after) -> AuditLog:
    return AuditLog(
        id="aud-001",
        action="UPDATE",
        resource_type="Invoice",
        resource_id="inv-001",
        actor_id="user-001",
        before_state=sample_before,
        after_state=sample_after,
        correlation_id="corr-001",
        occurred_at=datetime(2025, 1, 1, tzinfo=UTC),
    )


@pytest.fixture
def mock_repo() -> AsyncMock:
    repo = AsyncMock()
    repo.append = AsyncMock(side_effect=lambda log: log)
    repo.get_by_id = AsyncMock(return_value=None)
    repo.query = AsyncMock(return_value=([], 0))
    return repo


@pytest.fixture
def mock_cache() -> AsyncMock:
    cache = AsyncMock()
    cache.get = AsyncMock(return_value=None)
    cache.insert = AsyncMock(return_value=None)
    cache.invalidate = AsyncMock(return_value=None)
    return cache


@pytest.fixture
def mock_publisher() -> AsyncMock:
    pub = AsyncMock()
    pub.publish = AsyncMock(return_value=None)
    return pub


@pytest.fixture
def mock_events() -> AsyncMock:
    ev = AsyncMock()
    ev.publish = AsyncMock(return_value=None)
    return ev
