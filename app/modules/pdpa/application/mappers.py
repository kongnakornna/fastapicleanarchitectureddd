"""pdpa mappers — ORM ↔ domain"""
from __future__ import annotations
from typing import Any

from app.modules.pdpa.domain.entities import (
    ConsentLog, CookieConsent, DSARRequest, PrivacyPolicy,
)
from app.modules.pdpa.domain.enums import (
    ConsentStatus, DSARStatus, DSARType,
    IdempotencyStatus, PrivacyPolicyStatus, PurposeCategory,
)
from app.modules.pdpa.domain.idempotency import IdempotencyRecord
from app.modules.pdpa.domain.value_objects import Evidence


def consent_to_entity(row: Any) -> ConsentLog:
    """TH: ORM → ConsentLog | EN: ORM → ConsentLog"""
    ev = row.evidence or {}
    return ConsentLog(
        id=row.id, tenant_id=row.tenant_id, user_id=row.user_id,
        purpose_code=PurposeCategory(row.purpose_code),
        status=ConsentStatus(row.status),
        granted_at=row.granted_at, revoked_at=row.revoked_at,
        expires_at=row.expires_at,
        evidence=Evidence(
            ip_address=ev.get("ip_address", "0.0.0.0"),
            user_agent=ev.get("user_agent", ""),
            occurred_at=row.granted_at,
        ),
        version=row.version, created_at=row.created_at, updated_at=row.updated_at,
    )


def dsar_to_entity(row: Any) -> DSARRequest:
    """TH: ORM → DSARRequest | EN: ORM → DSARRequest"""
    return DSARRequest(
        id=row.id, tenant_id=row.tenant_id, user_id=row.user_id,
        type=DSARType(row.type), status=DSARStatus(row.status),
        reason=row.reason, rejection_reason=row.rejection_reason,
        response_payload=dict(row.response_payload or {}),
        submitted_at=row.submitted_at, verified_at=row.verified_at,
        completed_at=row.completed_at, deadline_at=row.deadline_at,
        version=row.version, created_at=row.created_at, updated_at=row.updated_at,
    )


def policy_to_entity(row: Any) -> PrivacyPolicy:
    """TH: ORM → PrivacyPolicy | EN: ORM → PrivacyPolicy"""
    return PrivacyPolicy(
        id=row.id, tenant_id=row.tenant_id, version=row.version,
        content_th=row.content_th, content_en=row.content_en,
        status=PrivacyPolicyStatus(row.status),
        effective_from=row.effective_from,
        published_at=row.published_at, superseded_at=row.superseded_at,
        created_at=row.created_at, updated_at=row.updated_at,
    )


def cookie_to_entity(row: Any) -> CookieConsent:
    """TH: ORM → CookieConsent | EN: ORM → CookieConsent"""
    return CookieConsent(
        id=row.id, tenant_id=row.tenant_id, user_id=row.user_id,
        session_id=row.session_id, necessary=row.necessary,
        analytics=row.analytics, marketing=row.marketing,
        functional=row.functional,
        ip_address=str(row.ip_address) if row.ip_address else None,
        user_agent=row.user_agent,
        accepted_at=row.accepted_at, withdrawn_at=row.withdrawn_at,
        version=row.version, created_at=row.created_at, updated_at=row.updated_at,
    )


def idempotency_to_entity(row: Any) -> IdempotencyRecord:
    """TH: ORM → IdempotencyRecord | EN: ORM → IdempotencyRecord"""
    return IdempotencyRecord(
        id=row.id,
        tenant_id=row.tenant_id,
        user_id=row.user_id,
        idempotency_key=row.idempotency_key,
        request_method=row.request_method,
        request_path=row.request_path,
        request_hash=(row.request_hash or "").strip(),
        status=IdempotencyStatus(row.status),
        response_status=row.response_status,
        response_body=dict(row.response_body) if row.response_body else None,
        created_at=row.created_at,
        updated_at=row.updated_at,
        expires_at=row.expires_at,
    )