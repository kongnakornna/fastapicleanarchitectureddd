"""Unit tests for pdpa use cases"""
from __future__ import annotations
import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules.pdpa.application.exceptions import DuplicateConsentError
from app.modules.pdpa.application.use_cases import (
    RecordConsentUseCase, SubmitDSARUseCase,
)
from app.modules.pdpa.domain.entities import ConsentLog
from app.modules.pdpa.domain.enums import DSARType, PurposeCategory

pytestmark = pytest.mark.unit
TENANT = uuid.UUID("00000000-0000-0000-0000-000000000001")
USER = uuid.UUID("00000000-0000-0000-0000-000000000002")


@pytest.fixture
def ctx() -> MagicMock:
    m = MagicMock(); m.tenant_id = TENANT; m.user_id = USER; return m


@pytest.fixture
def repo() -> AsyncMock:
    r = AsyncMock()
    r.find_active_by_user_and_purpose.return_value = None
    store: dict[uuid.UUID, ConsentLog] = {}
    async def _save(c, e): store[e.id] = e; return e
    async def _get(c, i): return store.get(i)
    r.save.side_effect = _save; r.find_by_id.side_effect = _get
    return r


@pytest.fixture
def bus() -> AsyncMock: return AsyncMock()
@pytest.fixture
def idem() -> AsyncMock:
    m = AsyncMock(); m.check_or_lock.return_value = None; return m
@pytest.fixture
def email() -> AsyncMock: return AsyncMock()


class TestRecordConsent:
    async def test_happy_path(self, repo, bus, idem, ctx) -> None:
        uc = RecordConsentUseCase(repo=repo, bus=bus, idem=idem, ctx=ctx)
        out = await uc.execute(
            user_id=USER, purpose_code=PurposeCategory.DATA_COLLECTION,
            ip_address="127.0.0.1", user_agent="test", idempotency_key="k-1")
        assert out.status.value == "GRANTED"
        repo.save.assert_awaited_once(); bus.publish.assert_awaited()

    async def test_duplicate_raises(self, repo, bus, idem, ctx) -> None:
        repo.find_active_by_user_and_purpose.return_value = MagicMock(spec=ConsentLog)
        uc = RecordConsentUseCase(repo=repo, bus=bus, idem=idem, ctx=ctx)
        with pytest.raises(DuplicateConsentError):
            await uc.execute(
                user_id=USER, purpose_code=PurposeCategory.DATA_COLLECTION,
                ip_address="127.0.0.1", user_agent="test", idempotency_key="k-2")


class TestSubmitDSAR:
    async def test_submit_access(self, ctx, bus, email) -> None:
        repo = AsyncMock()
        async def _save(c, d): return d
        repo.save.side_effect = _save
        uc = SubmitDSARUseCase(repo=repo, bus=bus, email=email, ctx=ctx)
        out = await uc.execute(user_id=USER, type=DSARType.ACCESS)
        assert out.status.value == "SUBMITTED"

    async def test_submit_erasure_publishes_extra_event(self, ctx, bus, email) -> None:
        repo = AsyncMock()
        async def _save(c, d): return d
        repo.save.side_effect = _save
        uc = SubmitDSARUseCase(repo=repo, bus=bus, email=email, ctx=ctx)
        await uc.execute(user_id=USER, type=DSARType.ERASURE)
        assert bus.publish.await_count == 2