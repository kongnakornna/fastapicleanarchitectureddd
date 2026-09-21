"""
Audit Use Case Tests — ทดสอบ use case audit
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from audit.application.exceptions import AuditException
from audit.application.use_cases import AuditUseCases


class _Ctx:
    user_id = "user-001"
    correlation_id = "corr-001"
    ip_address = "127.0.0.1"
    user_agent = "pytest"


@pytest.fixture
def use_cases(mock_repo, mock_cache, mock_publisher, mock_events):
    return AuditUseCases(
        repo=mock_repo,
        cache=mock_cache,
        publisher=mock_publisher,
        events=mock_events,
    )


@pytest.mark.asyncio
async def test_log_appends_and_verifies(
    use_cases, mock_repo, mock_publisher, mock_events
):
    """log() must append, read-back, cache, publish — log() ต้อง append + verify + cache + publish"""
    mock_repo.get_by_id.return_value = AsyncMock()  # read-back OK

    with patch("audit.application.use_cases.get_context", return_value=_Ctx()):
        log = await use_cases.log(
            action="PAYMENT",
            resource_type="Invoice",
            resource_id="inv-001",
            before={"status": "DRAFT"},
            after={"status": "PAID"},
        )

    assert log.action == "PAYMENT"
    assert log.actor_id == "user-001"
    assert log.severity == "CRITICAL"  # payment is critical
    mock_repo.append.assert_awaited_once()
    mock_publisher.publish.assert_awaited_once()
    mock_events.publish.assert_awaited_once()


@pytest.mark.asyncio
async def test_readback_failure_raises(use_cases, mock_repo, mock_cache):
    """Read-back failure must raise AuditException — read-back fail ต้อง raise"""
    mock_repo.get_by_id.return_value = None

    with (
        patch("audit.application.use_cases.get_context", return_value=_Ctx()),
        pytest.raises(AuditException),
    ):
        await use_cases.log(
            action="UPDATE",
            resource_type="Invoice",
            resource_id="inv-001",
            before={},
            after={},
        )


@pytest.mark.asyncio
async def test_get_uses_cache_first(use_cases, mock_cache, mock_repo, sample_log):
    """get() must return cached value without hitting repo — get() ต้องคืน cache ก่อน"""
    mock_cache.get.return_value = sample_log

    result = await use_cases.get("aud-001")

    assert result is sample_log
    mock_repo.get_by_id.assert_not_awaited()
