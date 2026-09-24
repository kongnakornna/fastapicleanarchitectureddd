"""structured_outputs services"""
from __future__ import annotations
import logging
import uuid
from typing import Any

from app.modules.structured_outputs.application.interfaces import EventBus

logger = logging.getLogger(__name__)


class LLMPortAdapter:
    """TH: adapter ไปยัง llm module (LLMPort)
    | EN: LLM port adapter"""

    def __init__(self, llm_use_case: Any) -> None:
        self._uc = llm_use_case

    async def chat(
        self, *, tenant_id: uuid.UUID, model: str,
        messages: list[dict[str, Any]],
        system_prompt: Any = None,
    ) -> Any:
        from app.shared.context import RequestContext as SharedCtx
        ctx = SharedCtx(tenant_id=tenant_id)
        return await self._uc.chat(
            ctx,
            model_name=model, messages=messages,
            system_prompt=system_prompt,
        )


class LoggingEventBus(EventBus):
    async def publish(self, event: object) -> None:
        try:
            logger.info("event %s", type(event).__name__)
        except Exception:
            pass
