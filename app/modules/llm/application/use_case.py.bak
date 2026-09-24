"""llm use cases"""
from __future__ import annotations

import time
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any, AsyncIterator

import structlog

from app.modules.llm.application.interfaces import (
    ConversationRepository, EventBus, IdempotencyStore,
    LLMCache, MessageRepository, ModelRepository,
    ProviderRegistry, ProviderRepository, RateLimiter,
    RequestContext, UsageLogRepository,
)
from app.modules.llm.application.utils import build_cache_key
from app.modules.llm.domain.enums import MessageRole
from app.modules.llm.domain.events import (
    CompletionGenerated, ConversationCreated, MessageSent,
)
from app.modules.llm.domain.exceptions import (
    ConversationNotFoundError, LLMError,
    ModelNotFoundError, ProviderError, RateLimitExceededError,
)
from app.modules.llm.domain.helpers import count_message_tokens
from app.modules.llm.domain.value_objects import ChatOptions
from app.modules.llm.infrastructure.models import (
    ConversationModel, MessageModel, UsageLogModel,
)

log = structlog.get_logger()

_COSTS: dict[str, tuple[Decimal, Decimal]] = {
    "gpt-4o-mini": (Decimal("0.00015"), Decimal("0.0006")),
    "gpt-4o": (Decimal("0.005"), Decimal("0.015")),
    "gpt-4-turbo": (Decimal("0.01"), Decimal("0.03")),
    "claude-3-5-sonnet-20241022": (
        Decimal("0.003"), Decimal("0.015"),
    ),
    "claude-3-opus-20240229": (
        Decimal("0.015"), Decimal("0.075"),
    ),
}


class LLMUseCase:
    """TH: use cases รวมทุก operation | EN: all LLM operations"""

    def __init__(
        self,
        provider_repo: ProviderRepository,
        model_repo: ModelRepository,
        conversation_repo: ConversationRepository,
        message_repo: MessageRepository,
        usage_repo: UsageLogRepository,
        registry: ProviderRegistry,
        rate_limiter: RateLimiter,
        cache: LLMCache,
        event_bus: EventBus,
        idempotency: IdempotencyStore,
    ) -> None:
        self._provider_repo = provider_repo
        self._model_repo = model_repo
        self._conversation_repo = conversation_repo
        self._message_repo = message_repo
        self._usage_repo = usage_repo
        self._registry = registry
        self._rate_limiter = rate_limiter
        self._cache = cache
        self._bus = event_bus
        self._idem = idempotency

    async def chat(
        self,
        ctx: RequestContext,
        conversation_id: uuid.UUID | None,
        model_name: str,
        user_message: str,
        options: ChatOptions,
        system_prompt: str = "",
        idempotency_key: str = "",
    ) -> dict[str, Any]:
        """TH: chat completion | EN: chat completion (3-branch)"""
        log.info("llm.chat.start", model=model_name)
        try:
            estimated = count_message_tokens(
                [{"role": "user", "content": user_message}],
                model_name,
            )
            uid = ctx.user_id or uuid.uuid4()
            allowed = await self._rate_limiter.check(
                ctx.tenant_id, uid,
                cost=estimated + options.max_tokens,
            )
            if not allowed:
                raise RateLimitExceededError("rate limit exceeded")

            messages = self._build_messages(
                system_prompt, user_message, [],
            )
            cache_key = build_cache_key(messages, model_name, options)
            cached = await self._cache.get(cache_key)
            if cached:
                log.info("llm.chat.cache_hit", model=model_name)
                return cached

            model = await self._model_repo.find_by_name(ctx, model_name)
            if model is None:
                raise ModelNotFoundError(
                    f"model {model_name} not found",
                )

            providers = await self._provider_repo.find_all_active(ctx)
            if not providers:
                raise ProviderError("no active providers")

            provider = self._registry.select_provider(
                model_name, providers,
            )
            client = self._registry.get_client(provider)

            started = time.monotonic()
            response = await client.chat_completion(
                messages, model_name, options,
            )
            latency_ms = int((time.monotonic() - started) * 1000)

            conv_id = await self._persist_chat(
                ctx, conversation_id, model.id, model_name,
                system_prompt, user_message, response, latency_ms,
            )

            result: dict[str, Any] = {
                "conversation_id": str(conv_id),
                "model": model_name,
                "content": response.get("content", ""),
                "finish_reason": response.get("finish_reason", "stop"),
                "usage": response.get("usage", {}),
                "latency_ms": latency_ms,
            }

            await self._cache.set(cache_key, result, ttl=3600)

            usage = response.get("usage", {}) or {}
            actual_tokens = int(usage.get("total_tokens", estimated))
            await self._rate_limiter.increment(
                ctx.tenant_id, uid, cost=actual_tokens,
            )

            log.info(
                "llm.chat.success",
                model=model_name, latency_ms=latency_ms,
            )
            return result

        except LLMError:
            raise
        except Exception:
            log.exception("llm.chat.unexpected")
            raise

    async def chat_stream(
        self,
        ctx: RequestContext,
        conversation_id: uuid.UUID | None,
        model_name: str,
        user_message: str,
        options: ChatOptions,
        system_prompt: str = "",
    ) -> AsyncIterator[dict[str, Any]]:
        """TH: chat streaming | EN: chat streaming (SSE)"""
        log.info("llm.stream.start", model=model_name)
        try:
            messages = self._build_messages(
                system_prompt, user_message, [],
            )
            model = await self._model_repo.find_by_name(
                ctx, model_name,
            )
            if model is None:
                raise ModelNotFoundError(
                    f"model {model_name} not found",
                )

            providers = await self._provider_repo.find_all_active(ctx)
            if not providers:
                raise ProviderError("no active providers")

            provider = self._registry.select_provider(
                model_name, providers,
            )
            client = self._registry.get_client(provider)

            buffer: list[str] = []
            started = time.monotonic()
            async for chunk in client.stream_chat_completion(
                messages, model_name, options,
            ):
                content = chunk.get("delta", "")
                if content:
                    buffer.append(content)
                yield chunk
            latency_ms = int((time.monotonic() - started) * 1000)

            full_content = "".join(buffer)
            await self._persist_chat(
                ctx, conversation_id, model.id, model_name,
                system_prompt, user_message,
                {
                    "content": full_content,
                    "finish_reason": "stop",
                    "usage": {
                        "prompt_tokens": count_message_tokens(
                            messages, model_name,
                        ),
                        "completion_tokens": count_message_tokens(
                            [{"role": "assistant",
                              "content": full_content}],
                            model_name,
                        ),
                    },
                },
                latency_ms,
            )

        except LLMError:
            raise
        except Exception:
            log.exception("llm.stream.unexpected")
            raise

    async def create_conversation(
        self, ctx: RequestContext, model_name: str, title: str = "",
    ) -> dict[str, Any]:
        model = await self._model_repo.find_by_name(ctx, model_name)
        if model is None:
            raise ModelNotFoundError(
                f"model {model_name} not found",
            )

        conv = ConversationModel(
            tenant_id=ctx.tenant_id,
            user_id=ctx.user_id or uuid.uuid4(),
            title=title or f"Chat with {model_name}",
            model_id=model.id,
            status="ACTIVE",
        )
        saved = await self._conversation_repo.save(ctx, conv)
        await self._bus.publish(ConversationCreated(
            conversation_id=saved.id,
            tenant_id=ctx.tenant_id,
            user_id=ctx.user_id or uuid.uuid4(),
            model_id=model.id,
        ))
        return {
            "id": str(saved.id), "title": saved.title,
            "model_id": str(saved.model_id),
            "status": saved.status,
            "message_count": saved.message_count,
            "total_tokens": saved.total_tokens,
        }

    async def list_conversations(
        self, ctx: RequestContext, limit: int = 50,
    ) -> list[dict[str, Any]]:
        uid = ctx.user_id or uuid.uuid4()
        rows = await self._conversation_repo.find_by_user(
            ctx, uid, limit,
        )
        return [
            {
                "id": str(r.id), "title": r.title,
                "model_id": str(r.model_id),
                "status": r.status,
                "message_count": r.message_count,
                "total_tokens": r.total_tokens,
            }
            for r in rows
        ]

    async def get_conversation(
        self, ctx: RequestContext, conversation_id: uuid.UUID,
    ) -> dict[str, Any]:
        conv = await self._conversation_repo.find_by_id(
            ctx, conversation_id,
        )
        if conv is None:
            raise ConversationNotFoundError(
                "conversation not found",
            )
        messages = await self._message_repo.find_by_conversation(
            ctx, conversation_id, limit=200,
        )
        return {
            "id": str(conv.id), "title": conv.title,
            "status": conv.status,
            "model_id": str(conv.model_id),
            "messages": [
                {
                    "id": str(m.id), "role": m.role,
                    "content": m.content,
                    "created_at": (
                        m.created_at.isoformat()
                        if m.created_at else ""
                    ),
                }
                for m in messages
            ],
        }

    async def list_providers(
        self, ctx: RequestContext,
    ) -> list[dict[str, Any]]:
        rows = await self._provider_repo.find_all_active(ctx)
        return [
            {
                "id": str(r.id), "name": r.name,
                "provider_type": r.provider_type,
                "base_url": r.base_url,
                "is_active": r.is_active,
                "priority": r.priority,
            }
            for r in rows
        ]

    async def list_models(
        self, ctx: RequestContext,
    ) -> list[dict[str, Any]]:
        rows = await self._model_repo.find_all_active(ctx)
        return [
            {
                "id": str(r.id), "name": r.name,
                "display_name": r.display_name,
                "context_window": r.context_window,
                "max_output_tokens": r.max_output_tokens,
                "supports_streaming": r.supports_streaming,
                "supports_tools": r.supports_tools,
            }
            for r in rows
        ]

    async def get_usage(
        self, ctx: RequestContext, since_days: int = 30,
    ) -> dict[str, Any]:
        since = datetime.now(UTC) - timedelta(days=since_days)
        tenant_sum = await self._usage_repo.sum_by_tenant(
            ctx, since,
        )
        uid = ctx.user_id or uuid.uuid4()
        user_sum = await self._usage_repo.sum_by_user(
            ctx, uid, since,
        )
        return {
            "tenant": tenant_sum,
            "user": user_sum,
            "since": since.isoformat(),
        }

    def _build_messages(
        self,
        system_prompt: str,
        user_message: str,
        history: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        msgs: list[dict[str, Any]] = []
        if system_prompt:
            msgs.append(
                {"role": "system", "content": system_prompt},
            )
        msgs.extend(history)
        msgs.append({"role": "user", "content": user_message})
        return msgs

    async def _persist_chat(
        self,
        ctx: RequestContext,
        conversation_id: uuid.UUID | None,
        model_id: uuid.UUID,
        model_name: str,
        system_prompt: str,
        user_message: str,
        response: dict[str, Any],
        latency_ms: int,
    ) -> uuid.UUID:
        uid = ctx.user_id or uuid.uuid4()

        if conversation_id is None:
            conv = ConversationModel(
                tenant_id=ctx.tenant_id,
                user_id=uid,
                title=user_message[:50],
                model_id=model_id,
                system_prompt=system_prompt,
            )
            conv = await self._conversation_repo.save(ctx, conv)
            conversation_id = conv.id
        else:
            conv = await self._conversation_repo.find_by_id(
                ctx, conversation_id,
            )
            if conv is None:
                raise ConversationNotFoundError(
                    "conversation not found",
                )

        usage = response.get("usage", {}) or {}
        tokens_in = int(usage.get("prompt_tokens", 0) or 0)
        tokens_out = int(usage.get("completion_tokens", 0) or 0)

        user_msg = MessageModel(
            tenant_id=ctx.tenant_id,
            conversation_id=conversation_id,
            role=MessageRole.USER.value,
            content=user_message,
            tokens_input=tokens_in,
        )
        await self._message_repo.create(ctx, user_msg)

        asst_msg = MessageModel(
            tenant_id=ctx.tenant_id,
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT.value,
            content=response.get("content", ""),
            tokens_output=tokens_out,
            finish_reason=response.get("finish_reason", "stop"),
            latency_ms=latency_ms,
        )
        saved = await self._message_repo.create(ctx, asst_msg)

        conv.message_count = (conv.message_count or 0) + 2
        conv.total_tokens = (
            (conv.total_tokens or 0) + tokens_in + tokens_out
        )
        await self._conversation_repo.update(ctx, conv)

        cost = self._compute_cost(model_name, tokens_in, tokens_out)
        usage_log = UsageLogModel(
            tenant_id=ctx.tenant_id,
            user_id=uid,
            model_id=model_id,
            conversation_id=conversation_id,
            tokens_input=tokens_in,
            tokens_output=tokens_out,
            cost_usd=cost,
            source="chat",
        )
        await self._usage_repo.create(ctx, usage_log)

        await self._bus.publish(MessageSent(
            message_id=saved.id,
            conversation_id=conversation_id,
            tenant_id=ctx.tenant_id,
            role=MessageRole.ASSISTANT.value,
            tokens_input=tokens_in,
            tokens_output=tokens_out,
        ))
        await self._bus.publish(CompletionGenerated(
            message_id=saved.id,
            tenant_id=ctx.tenant_id,
            model_name=model_name,
            finish_reason=response.get("finish_reason", "stop"),
            latency_ms=latency_ms,
        ))

        return conversation_id

    def _compute_cost(
        self, model_name: str, tokens_in: int, tokens_out: int,
    ) -> Decimal:
        """TH: คำนวณค่าใช้จ่าย | EN: compute cost (Decimal only)"""
        in_cost, out_cost = _COSTS.get(
            model_name, (Decimal("0"), Decimal("0")),
        )
        total = (
            in_cost * Decimal(tokens_in) / Decimal(1000)
            + out_cost * Decimal(tokens_out) / Decimal(1000)
        )
        return total.quantize(Decimal("0.00000001"))
