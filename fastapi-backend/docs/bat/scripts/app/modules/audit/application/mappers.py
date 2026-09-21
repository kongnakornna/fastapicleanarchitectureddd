"""
Audit Mappers — ตัวแปลงข้อมูล audit
Audit Mappers — entity <-> model <-> schema mappers
"""

from __future__ import annotations

from typing import Any

from audit.domain.entities import AuditLog


class AuditMapper:
    """Mapper between domain entity / ORM model / DTO — ตัวแปลงระหว่าง entity / model / DTO"""

    @staticmethod
    def to_model_dict(log: AuditLog) -> dict[str, Any]:
        """Domain entity → ORM dict — entity → dict สำหรับ ORM"""
        return {
            "id": log.id,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "actor_id": log.actor_id,
            "before_state": log.before_state,
            "after_state": log.after_state,
            "changes": log.changes,
            "ip_address": log.ip_address,
            "user_agent": log.user_agent,
            "correlation_id": log.correlation_id,
            "severity": log.severity,
            "occurred_at": log.occurred_at,
            "created_at": log.created_at,
        }

    @staticmethod
    def to_entity(model) -> AuditLog:
        """ORM model → domain entity — model → entity"""
        return AuditLog(
            id=model.id,
            action=model.action,
            resource_type=model.resource_type,
            resource_id=model.resource_id,
            actor_id=model.actor_id,
            before_state=model.before_state or {},
            after_state=model.after_state or {},
            changes=model.changes or [],
            ip_address=model.ip_address or "",
            user_agent=model.user_agent or "",
            correlation_id=model.correlation_id or "",
            severity=getattr(model, "severity", "INFO") or "INFO",
            occurred_at=model.occurred_at,
        )

    @staticmethod
    def to_dict(log: AuditLog) -> dict[str, Any]:
        """Domain entity → dict (JSON-safe) — entity → dict"""
        return {
            "id": log.id,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "actor_id": log.actor_id,
            "before_state": log.before_state,
            "after_state": log.after_state,
            "changes": log.changes,
            "ip_address": log.ip_address,
            "user_agent": log.user_agent,
            "correlation_id": log.correlation_id,
            "severity": log.severity,
            "occurred_at": log.occurred_at.isoformat() if log.occurred_at else None,
        }
