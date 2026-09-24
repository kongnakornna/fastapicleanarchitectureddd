"""llm infrastructure services — Provider clients · EventBus · RateLimiter"""
from __future__ import annotations

import asyncio
import uuid
from typing import Any, AsyncIterator

import structlog

from app.modules.llm.application.interfaces import (
    LLMClient, ProviderRegistry,
)
from app.modules.llm.domain.exceptions import ProviderError
from app.modules.llm.domain.value_objects import ChatOptions
from app.modules.llm.infrastructure.models import ProviderModel

log = structlog.get_logger()

_RETRY_DELAYS = (1.0, 2.0, 4.0)


async def _retry_async(coro_factory, retries: int = 3):
    last_exc: Exception | None = None
    for attempt in range(retries):
        try:
            return await coro_factory()
        except ProviderError:
            raise
        except Exception as exc:
            last_exc = exc
            if attempt < retries - 1:
                await asyncio.sleep(_RETRY_DELAYS[attempt])
    raise last_exc if last_exc else ProviderError("retry failed")


class OpenAIClient:
    def __init__(self, api_key: str, base_url: str = "") -> None:
        self._api_key = api_key
        self._base_url = base_url

    async def chat_completion(
        self, messages: list[dict[str, Any]],
        model: str, options: ChatOptions,
    ) -> dict[str, Any]:
        async def _call() -> dict[str, Any]:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(
                api_key=self._api_key,
                base_url=self._base_url or None,
            )
            response = await client.chat.completions.create(
                model=model, messages=messages,
                temperature=options.temperature,
                top_p=options.top_p,
                max_tokens=options.max_tokens,
                stream=False,
            )
            choice = response.choices[0]
            u = response.usage
            return {
                "content": choice.message.content or "",
                "finish_reason": choice.finish_reason or "stop",
                "usage": {
                    "prompt_tokens": u.prompt_tokens if u else 0,
                    "completion_tokens": (
                        u.completion_tokens if u else 0
                    ),
                    "total_tokens": u.total_tokens if u else 0,
                },
            }
        try:
            return await _retry_async(_call)
        except Exception as e:
            log.error("openai.chat_failed", err=str(e))
            raise ProviderError(str(e)) from e

    async def stream_chat_completion(
        self, messages: list[dict[str, Any]],
        model: str, options: ChatOptions,
    ) -> AsyncIterator[dict[str, Any]]:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(
                api_key=self._api_key,
                base_url=self._base_url or None,
            )
            stream = await client.chat.completions.create(
                model=model, messages=messages,
                temperature=options.temperature,
                top_p=options.top_p,
                max_tokens=options.max_tokens,
                stream=True,
            )
            async for chunk in stream:
                if chunk.choices:
                    delta = chunk.choices[0].delta.content or ""
                    if delta:
                        yield {"delta": delta}
        except Exception as e:
            log.error("openai.stream_failed", err=str(e))
            raise ProviderError(str(e)) from e


class AnthropicClient:
    def __init__(self, api_key: str, base_url: str = "") -> None:
        self._api_key = api_key
        self._base_url = base_url

    @staticmethod
    def _split_system(
        messages: list[dict[str, Any]],
    ) -> tuple[str, list[dict[str, Any]]]:
        system = ""
        api_messages: list[dict[str, Any]] = []
        for m in messages:
            if m.get("role") == "system":
                system = m.get("content", "")
            else:
                api_messages.append(m)
        return system, api_messages

    async def chat_completion(
        self, messages: list[dict[str, Any]],
        model: str, options: ChatOptions,
    ) -> dict[str, Any]:
        async def _call() -> dict[str, Any]:
            from anthropic import AsyncAnthropic
            client = AsyncAnthropic(
                api_key=self._api_key,
                base_url=self._base_url or None,
            )
            system, api_messages = self._split_system(messages)
            response = await client.messages.create(
                model=model, messages=api_messages,
                system=system or None,
                max_tokens=options.max_tokens,
                temperature=options.temperature,
            )
            content = ""
            for block in response.content:
                if hasattr(block, "text"):
                    content += block.text
            return {
                "content": content,
                "finish_reason": response.stop_reason or "stop",
                "usage": {
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": (
                        response.usage.input_tokens
                        + response.usage.output_tokens
                    ),
                },
            }
        try:
            return await _retry_async(_call)
        except Exception as e:
            log.error("anthropic.chat_failed", err=str(e))
            raise ProviderError(str(e)) from e

    async def stream_chat_completion(
        self, messages: list[dict[str, Any]],
        model: str, options: ChatOptions,
    ) -> AsyncIterator[dict[str, Any]]:
        try:
            from anthropic import AsyncAnthropic
            client = AsyncAnthropic(
                api_key=self._api_key,
                base_url=self._base_url or None,
            )
            system, api_messages = self._split_system(messages)
            async with client.messages.stream(
                model=model, messages=api_messages,
                system=system or None,
                max_tokens=options.max_tokens,
            ) as stream:
                async for text in stream.text_stream:
                    if text:
                        yield {"delta": text}
        except Exception as e:
            log.error("anthropic.stream_failed", err=str(e))
            raise ProviderError(str(e)) from e


class DefaultProviderRegistry:
    def __init__(self, secrets_provider: Any = None) -> None:
        self._secrets = secrets_provider

    def get_client(self, provider: ProviderModel) -> LLMClient:
        api_key = self._resolve_key(provider)
        if provider.provider_type == "openai":
            return OpenAIClient(api_key, provider.base_url)
        if provider.provider_type == "anthropic":
            return AnthropicClient(api_key, provider.base_url)
        return OpenAIClient(api_key, provider.base_url)

    def select_provider(
        self, model_name: str, providers: list[ProviderModel],
    ) -> ProviderModel:
        if not providers:
            raise ProviderError("no providers available")
        return sorted(providers, key=lambda p: p.priority)[0]

    def _resolve_key(self, provider: ProviderModel) -> str:
        if self._secrets:
            try:
                return self._secrets.decrypt(
                    provider.api_key_encrypted,
                )
            except Exception:
                pass
        return provider.api_key_encrypted or ""


class RedisRateLimiter:
    def __init__(
        self, redis: object,
        tenant_limit: int = 10_000_000,
        user_limit: int = 1_000_000,
    ) -> None:
        self._redis = redis
        self._tenant_limit = tenant_limit
        self._user_limit = user_limit

    async def check(
        self, tenant_id: uuid.UUID,
        user_id: uuid.UUID, cost: int,
    ) -> bool:
        try:
            t_key = f"llm:rate:tenant:{tenant_id}"
            u_key = f"llm:rate:user:{user_id}"
            t_val = await self._redis.get(t_key) or 0
            u_val = await self._redis.get(u_key) or 0
            return (
                int(t_val) + cost <= self._tenant_limit
                and int(u_val) + cost <= self._user_limit
            )
        except Exception as e:
            log.warning("ratelimit.check_failed", err=str(e))
            return True

    async def increment(
        self, tenant_id: uuid.UUID,
        user_id: uuid.UUID, cost: int,
    ) -> None:
        try:
            t_key = f"llm:rate:tenant:{tenant_id}"
            u_key = f"llm:rate:user:{user_id}"
            pipe = self._redis.pipeline()
            pipe.incrby(t_key, cost)
            pipe.expire(t_key, 86400)
            pipe.incrby(u_key, cost)
            pipe.expire(u_key, 86400)
            await pipe.execute()
        except Exception as e:
            log.warning("ratelimit.increment_failed", err=str(e))


class KafkaEventBus:
    def __init__(
        self, producer: object, topic: str = "llm.events",
    ) -> None:
        self._producer = producer
        self._topic = topic

    async def publish(self, event: object) -> None:
        try:
            payload = {
                "type": type(event).__name__,
                "data": {k: str(v) for k, v in vars(event).items()},
            }
            await self._producer.send_and_wait(self._topic, payload)
            log.info("event.published", type=type(event).__name__)
        except Exception as e:
            log.warning("event.publish_failed", err=str(e))


class NoopEventBus:
    async def publish(self, event: object) -> None:
        log.debug("event.noop", type=type(event).__name__)
