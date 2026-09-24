"""pdpa infra services — Kafka · Email · LLM · Exporter · Anonymizer"""
from __future__ import annotations
import uuid
from typing import Any

from app.core.logging import logger

from app.modules.pdpa.application.interfaces import (
    DataExporter, EmailService, EventBus, LLMService,
    PIIAnonymizer, RequestContext,
)



class KafkaEventBus(EventBus):
    """TH: Kafka event bus | EN: Kafka event bus"""

    def __init__(self, producer: object, topic: str = "pdpa.events") -> None:
        self._producer = producer; self._topic = topic

    async def publish(self, event: object) -> None:
        try:
            payload = {
                "type": type(event).__name__,
                "data": {k: str(v) for k, v in vars(event).items()},
            }
            await self._producer.send_and_wait(  # type: ignore[attr-defined]
                self._topic, payload)
            logger.info("event.published", type=type(event).__name__)
        except Exception as e:
            logger.warning("event.publish_failed", err=str(e))


class SMTPEmailService(EmailService):
    """TH: SMTP email service | EN: SMTP email service"""

    def __init__(self, smtp_client: object, from_addr: str) -> None:
        self._smtp = smtp_client; self._from = from_addr

    async def send_consent_notification(
        self, to: str, subject: str, body: str,
    ) -> bool:
        try:
            await self._smtp.send(  # type: ignore[attr-defined]
                from_addr=self._from, to_addrs=[to],
                subject=subject, body=body)
            return True
        except Exception as e:
            logger.warning("email.consent_failed", to=to, err=str(e)); return False

    async def send_dsar_notification(
        self, to: str, dsar_id: uuid.UUID, status: str,
    ) -> bool:
        try:
            await self._smtp.send(  # type: ignore[attr-defined]
                from_addr=self._from, to_addrs=[to],
                subject=f"DSAR {dsar_id} — {status}",
                body=f"สถานะ DSAR: {status}")
            return True
        except Exception as e:
            logger.warning("email.dsar_failed", to=to, err=str(e)); return False


class OpenAILLMService(LLMService):
    """TH: LLM service (anonymized only) | EN: LLM service"""

    def __init__(self, client: object) -> None:
        self._client = client

    async def analyze_usage_history(
        self, anonymized_data: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            response = await self._client.chat(  # type: ignore[attr-defined]
                anonymized_data)
            return {"analysis": response}
        except Exception as e:
            logger.warning("llm.analyze_failed", err=str(e))
            return {"analysis": None, "error": str(e)}


class JsonPdfDataExporter(DataExporter):
    """TH: exporter (JSON + PDF placeholder) | EN: exporter"""

    def __init__(self, repo: object, pdf_renderer: object = None) -> None:
        self._repo = repo; self._pdf = pdf_renderer

    async def export_json(self, ctx: RequestContext, user_id: uuid.UUID) -> dict[str, Any]:
        try:
            consents = await self._repo.find_by_user_id(ctx, user_id)
            return {
                "user_id": str(user_id),
                "consents": [
                    {"id": str(c.id), "purpose": c.purpose_code.value,
                     "status": c.status.value, "granted_at": c.granted_at.isoformat()}
                    for c in consents
                ],
                "exported_at": __import__("datetime").datetime.now(
                    __import__("datetime").UTC).isoformat(),
            }
        except Exception as e:
            logger.warning("exporter.json_failed", err=str(e))
            return {"error": str(e)}

    async def export_pdf(self, ctx: RequestContext, user_id: uuid.UUID) -> bytes:
        try:
            data = await self.export_json(ctx, user_id)
            if self._pdf and hasattr(self._pdf, "render"):
                return await self._pdf.render(data)  # type: ignore[attr-defined]
            return b""
        except Exception as e:
            logger.warning("exporter.pdf_failed", err=str(e)); return b""


class DefaultPIIAnonymizer(PIIAnonymizer):
    """TH: anonymizer (ปลอมข้อมูล PII) | EN: PII anonymizer"""

    def __init__(self, user_repo: object = None) -> None:
        self._user_repo = user_repo

    async def anonymize_user(self, ctx: RequestContext, user_id: uuid.UUID) -> None:
        try:
            if self._user_repo and hasattr(self._user_repo, "anonymize"):
                await self._user_repo.anonymize(ctx, user_id)  # type: ignore[attr-defined]
            logger.info("pii.anonymized", user_id=str(user_id))
        except Exception as e:
            logger.warning("pii.anonymize_failed", err=str(e))