"""langchain services — adapters + simple runners + bus"""
from __future__ import annotations
import logging
import uuid
from typing import Any, Optional

from app.modules.langchain.application.interfaces import (
    EventBus,
)

logger = logging.getLogger(__name__)


class LLMPortAdapter:
    """TH: adapter ไปยัง llm module | EN: LLM port adapter"""

    def __init__(self, llm_use_case: Any) -> None:
        self._uc = llm_use_case

    async def chat(
        self, *, tenant_id: uuid.UUID, model: str,
        messages: list[dict[str, Any]],
        system_prompt: Optional[str] = None,
    ) -> Any:
        try:
            from app.shared.context import RequestContext as SharedCtx
            ctx = SharedCtx(tenant_id=tenant_id)
            return await self._uc.chat(
                ctx, model_name=model, messages=messages,
                system_prompt=system_prompt,
            )
        except Exception as exc:
            logger.warning("llm adapter failed: %s", exc)
            raise

    def stream(
        self, *, tenant_id: uuid.UUID, model: str,
        messages: list[dict[str, Any]],
        system_prompt: Optional[str] = None,
    ) -> Any:
        from app.shared.context import RequestContext as SharedCtx
        ctx = SharedCtx(tenant_id=tenant_id)
        return self._uc.chat_stream(
            ctx, model_name=model, messages=messages,
            system_prompt=system_prompt,
        )


class ToolInvokerAdapter:
    """TH: adapter ไปยัง tool_calling module
    | EN: tool invoker adapter"""

    def __init__(self, tool_use_case: Any) -> None:
        self._uc = tool_use_case

    async def invoke(
        self, *, tenant_id: uuid.UUID,
        tool_name: str, args: dict[str, Any],
        role: str = "user",
    ) -> Any:
        from app.shared.context import RequestContext as SharedCtx
        from app.modules.tool_calling.domain.value_objects import (
            InvocationRequest,
        )
        ctx = SharedCtx(tenant_id=tenant_id)
        return await self._uc.invoke(
            ctx, InvocationRequest(tool_name=tool_name, args=args),
            role=role,
        )


class LCELChainRunner:
    """TH: LCEL runner (simple prompt → llm → output)
    | EN: LCEL runner"""

    def __init__(self, llm: Any) -> None:
        self._llm = llm

    async def run(
        self, *, chain_type: str, config: dict[str, Any],
        inputs: dict[str, Any], ctx: Any,
    ) -> dict[str, Any]:
        model = config.get("model", "gpt-4o-mini")
        prompt = inputs.get("input") or inputs.get("query") or ""
        system_prompt = config.get("system_prompt")
        messages = [{"role": "user", "content": str(prompt)}]
        result = await self._llm.chat(
            tenant_id=ctx.tenant_id, model=model,
            messages=messages, system_prompt=system_prompt,
        )
        content = getattr(result, "content", "") or ""
        usage = getattr(result, "usage", None)
        tokens = int(getattr(usage, "total_tokens", 0) or 0) \
            if usage is not None else 0
        return {"output": content, "tokens_used": tokens}


class SimpleReActAgent:
    """TH: simple ReAct (placeholder) | EN: simple ReAct agent"""

    def __init__(self, llm: Any, tool_invoker: Any) -> None:
        self._llm = llm
        self._tool = tool_invoker

    async def run(
        self, *, agent_type: str, tools: list[str], model: str,
        max_iterations: int, question: str,
        system_prompt: str, ctx: Any,
    ) -> dict[str, Any]:
        messages = [{"role": "user", "content": question}]
        tokens = 0
        iterations = 0
        tool_calls = 0

        for i in range(1, max_iterations + 1):
            iterations = i
            result = await self._llm.chat(
                tenant_id=ctx.tenant_id, model=model,
                messages=messages, system_prompt=system_prompt,
            )
            content = getattr(result, "content", "") or ""
            usage = getattr(result, "usage", None)
            if usage is not None:
                tokens += int(getattr(usage, "total_tokens", 0) or 0)
            raw_calls = getattr(result, "tool_calls", None) or []
            if not raw_calls:
                return {
                    "answer": content, "iterations": i,
                    "tool_calls": tool_calls, "tokens_used": tokens,
                }
            for call in raw_calls:
                tool_calls += 1
                try:
                    await self._tool.invoke(
                        tenant_id=ctx.tenant_id,
                        tool_name=call.get("name", ""),
                        args=call.get("arguments", {}) or {},
                    )
                except Exception as exc:
                    logger.debug("tool failed: %s", exc)
            messages.append({"role": "assistant", "content": content})
            messages.append({"role": "user", "content":
                             "Continue to final answer."})
        return {
            "answer": "max iterations reached",
            "iterations": iterations, "tool_calls": tool_calls,
            "tokens_used": tokens,
        }


class LoggingEventBus(EventBus):
    async def publish(self, event: object) -> None:
        try:
            logger.info("event %s", type(event).__name__)
        except Exception:
            pass
