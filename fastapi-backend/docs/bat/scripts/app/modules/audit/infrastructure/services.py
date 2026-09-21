"""
Audit Infrastructure Services — บริการ infrastructure audit
Audit Infrastructure Services — Kafka publisher + event bus adapters
"""

from __future__ import annotations

import json

from audit.application.mappers import AuditMapper
from audit.domain.entities import AuditLog
from loguru import logger


class AuditPublisher:
    """
    Audit publisher — ผู้เผยแพร่ audit

    Publishes audit logs to Kafka topic `audit.events`.
    """

    TOPIC = "audit.events"

    def __init__(self, producer) -> None:
        self.producer = producer

    async def publish(self, log: AuditLog) -> None:
        """Publish audit event to Kafka — เผยแพร่ event audit ไป Kafka (best-effort)"""
        try:
            payload = AuditMapper.to_dict(log)
            await self.producer.send_and_wait(
                self.TOPIC,
                key=log.id.encode("utf-8"),
                value=json.dumps(payload, default=str).encode("utf-8"),
            )
        except Exception as e:
            # Best-effort: audit must not break business flow
            # Best-effort: audit ต้องไม่ทำ business flow พัง
            logger.warning(f"Audit Kafka publish failed (ignored): {e}")


class AuditEventBus:
    """
    Internal audit event bus — event bus ภายในสำหรับ audit

    Wraps the shared event bus with audit-specific semantics.
    """

    def __init__(self, bus) -> None:
        self.bus = bus

    async def publish(self, event_name: str, payload: object) -> None:
        """Publish domain event — เผยแพร่ domain event (best-effort)"""
        try:
            await self.bus.publish(event_name, payload)
        except Exception as e:
            logger.warning(f"Audit event bus publish failed (ignored): {e}")
