"""Property tests for pdpa invariants — 4 tests §6"""
from __future__ import annotations
import uuid
from datetime import UTC, datetime

import pytest
from hypothesis import given, settings, strategies as st

from app.modules.pdpa.domain.entities import ConsentLog, DSARRequest
from app.modules.pdpa.domain.enums import DSARType, PurposeCategory
from app.modules.pdpa.domain.value_objects import Evidence

pytestmark = pytest.mark.property
TENANT = uuid.UUID("00000000-0000-0000-0000-000000000001")
USER = uuid.UUID("00000000-0000-0000-0000-000000000002")

PURPOSES = st.sampled_from(list(PurposeCategory))
DSAR_TYPES = st.sampled_from(list(DSARType))


def _ev() -> Evidence:
    return Evidence(ip_address="127.0.0.1", user_agent="t",
                    occurred_at=datetime.now(UTC))


@settings(max_examples=50)
@given(purpose=PURPOSES)
def test_new_consent_always_granted(purpose: PurposeCategory) -> None:
    c = ConsentLog.grant(
        tenant_id=TENANT, user_id=USER, purpose_code=purpose, evidence=_ev())
    assert c.status.value == "GRANTED"
    assert c.version == 1
    assert c.is_active() is True


@settings(max_examples=50)
@given(purpose=PURPOSES)
def test_revoke_always_increments_version(purpose: PurposeCategory) -> None:
    c = ConsentLog.grant(
        tenant_id=TENANT, user_id=USER, purpose_code=purpose, evidence=_ev())
    c.revoke(reason="test")
    assert c.version == 2


@settings(max_examples=50)
@given(t=DSAR_TYPES)
def test_dsar_deadline_always_in_future(t: DSARType) -> None:
    d = DSARRequest.submit(tenant_id=TENANT, user_id=USER, type=t)
    assert d.deadline_at > d.submitted_at


@settings(max_examples=50)
@given(purpose=PURPOSES)
def test_revoked_consent_never_active(purpose: PurposeCategory) -> None:
    c = ConsentLog.grant(
        tenant_id=TENANT, user_id=USER, purpose_code=purpose, evidence=_ev())
    c.revoke(reason="x")
    assert c.is_active() is False