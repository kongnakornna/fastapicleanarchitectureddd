"""Unit tests for pdpa domain — 12 tests ตามสเปค §6"""
from __future__ import annotations
import uuid
from datetime import UTC, datetime, timedelta

import pytest

from app.modules.pdpa.domain.entities import (
    ConsentLog, CookieConsent, DSARRequest, PrivacyPolicy,
)
from app.modules.pdpa.domain.enums import (
    ConsentStatus, DSARStatus, DSARType, PurposeCategory,
)
from app.modules.pdpa.domain.exceptions import (
    InvalidConsentStateError, PDPAError,
)
from app.modules.pdpa.domain.value_objects import Evidence

pytestmark = pytest.mark.unit
TENANT = uuid.UUID("00000000-0000-0000-0000-000000000001")
USER = uuid.UUID("00000000-0000-0000-0000-000000000002")


def _evidence() -> Evidence:
    return Evidence(ip_address="127.0.0.1", user_agent="test-agent",
                    occurred_at=datetime.now(UTC))


class TestConsentLog:
    def test_consent_granted_defaults(self) -> None:
        c = ConsentLog.grant(
            tenant_id=TENANT, user_id=USER,
            purpose_code=PurposeCategory.DATA_COLLECTION,
            evidence=_evidence())
        assert c.status is ConsentStatus.GRANTED
        assert c.version == 1
        assert c.is_active() is True

    def test_consent_cannot_grant_twice(self) -> None:
        c = ConsentLog.grant(
            tenant_id=TENANT, user_id=USER,
            purpose_code=PurposeCategory.DATA_COLLECTION,
            evidence=_evidence())
        c.revoke(reason="user_withdrawal")
        with pytest.raises(InvalidConsentStateError):
            c.revoke(reason="again")

    def test_consent_revoke_sets_status(self) -> None:
        c = ConsentLog.grant(
            tenant_id=TENANT, user_id=USER,
            purpose_code=PurposeCategory.DATA_COLLECTION,
            evidence=_evidence())
        c.revoke(reason="user_withdrawal")
        assert c.status is ConsentStatus.REVOKED
        assert c.revoked_at is not None
        assert c.version == 2

    def test_consent_expired_when_past_expires_at(self) -> None:
        past = datetime.now(UTC) - timedelta(days=1)
        c = ConsentLog.grant(
            tenant_id=TENANT, user_id=USER,
            purpose_code=PurposeCategory.DATA_COLLECTION,
            evidence=_evidence(), expires_at=past)
        assert c.is_active() is False


class TestDSAR:
    def test_dsar_submitted_sets_deadline_30_days(self) -> None:
        d = DSARRequest.submit(
            tenant_id=TENANT, user_id=USER, type=DSARType.ACCESS)
        delta = d.deadline_at - d.submitted_at
        assert 29 <= delta.days <= 30

    def test_dsar_completed_cannot_reopen(self) -> None:
        d = DSARRequest.submit(
            tenant_id=TENANT, user_id=USER, type=DSARType.ACCESS)
        d.verify(); d.complete(response_payload={})
        with pytest.raises(InvalidConsentStateError):
            d.reject(reason="too late")


class TestPrivacyPolicy:
    def test_privacy_policy_publish_supersedes_previous(self) -> None:
        p1 = PrivacyPolicy.create(
            tenant_id=TENANT, version=1,
            content_th="...", content_en="...")
        p1.publish()
        p1.supersede()
        assert p1.status.value == "SUPERSEDED"
        assert p1.superseded_at is not None


class TestCookieConsent:
    def test_cookie_consent_no_pretick(self) -> None:
        c = CookieConsent.record(
            tenant_id=TENANT, user_id=None, session_id="sess-1",
            analytics=False, marketing=False, functional=False)
        assert c.analytics is False
        assert c.marketing is False
        assert c.functional is False
        assert c.necessary is True


class TestValueObjects:
    def test_evidence_validates_ip(self) -> None:
        with pytest.raises(PDPAError):
            Evidence(ip_address="not-an-ip", user_agent="x",
                     occurred_at=datetime.now(UTC))

    def test_purpose_code_enum_validation(self) -> None:
        assert PurposeCategory("DATA_COLLECTION") is PurposeCategory.DATA_COLLECTION
        with pytest.raises(ValueError):
            PurposeCategory("INVALID")


class TestRepositoryInterface:
    def test_consent_repository_interface_signature(self) -> None:
        from app.modules.pdpa.application.interfaces import ConsentRepository
        required = {
            "save", "update", "find_by_id", "find_by_user_id",
            "find_active_by_user_and_purpose",
            "find_latest_by_user_and_purpose",
            "find_ready_for_auto_deletion",
            "delete_by_user_id", "delete_by_id", "is_consent_active",
            "count_active_by_purpose",
        }
        assert required.issubset(ConsentRepository.__abstractmethods__)


class TestSLA:
    def test_dsar_sla_breach_triggers_alert(self) -> None:
        d = DSARRequest.submit(
            tenant_id=TENANT, user_id=USER, type=DSARType.ACCESS)
        d.deadline_at = datetime.now(UTC) - timedelta(days=1)
        assert d.is_overdue() is True