"""embeddings use cases"""
from __future__ import annotations
import asyncio
import logging
import time
import uuid
from typing import Any, Optional

from app.modules.embeddings.application.exceptions import (
    NotFoundAppError, ProviderAppError, RateLimitAppError,
)
from app.modules.embeddings.application.utils import (
    make_cache_key, make_vector_hash, ms_now, vector_to_json,
)
from app.modules.embeddings.domain.events import (
    BatchStarted, EmbeddingCreated,
)
from app.modules.embeddings.domain.helpers.normalizer import (
    normalize_vector,
)
from app.modules.embeddings.domain.value_objects import (
    BatchConfig, EmbeddingRequest, EmbeddingResult,
)

logger = logging.getLogger(__name__)

_MAX_RETRIES = 3
_BACKOFF = [1.0, 2.0, 4.0]
_CACHE_TTL = 86400


class EmbeddingUseCase:
    """TH: use case หลัก | EN: core use case"""

    def __init__(self, **deps: Any) -> None:
        for key, value in deps.items():
            setattr(self, f"_{key}", value)

    async def embed(
        self, ctx: Any, req: EmbeddingRequest,
    ) -> list[EmbeddingResult]:
        """TH: embed หลายข้อความ | EN: embed many"""
        if not req.input:
            return []

        model = await self._models.find_by_name(ctx, req.model)
        if model is None or not model.is_active:
            raise NotFoundAppError(f"model not found: {req.model}")

        provider = await self._providers.find_by_id(ctx, model.provider_id)
        if provider is None or not provider.is_active:
            raise NotFoundAppError("provider not found")

        try:
            allowed = await self._rate.check(
                ctx.tenant_id, ctx.user_id or ctx.tenant_id,
                len(req.input),
            )
            if not allowed:
                raise RateLimitAppError("rate limit exceeded")
        except RateLimitAppError:
            raise
        except Exception as exc:
            logger.debug("rate limiter fail-open: %s", exc)

        results: list[Optional[EmbeddingResult]] = [None] * len(req.input)
        pending_idx: list[int] = []
        pending_text: list[str] = []

        for i, text in enumerate(req.input):
            key = make_cache_key(str(ctx.tenant_id), req.model, text)
            try:
                cached_vec = await self._cache.get(key)
                if cached_vec:
                    results[i] = EmbeddingResult.from_vector(
                        cached_vec, cached=True,
                    )
                    continue
            except Exception as exc:
                logger.debug("cache get failed: %s", exc)
            pending_idx.append(i)
            pending_text.append(text)

        if pending_text:
            client = self._registry.get_client(provider)
            vectors = await self._call_with_retry(
                client, pending_text, req.model,
                normalize=req.normalize,
                dimensions=req.dimensions,
            )

            for j, vec in enumerate(vectors):
                idx = pending_idx[j]
                text = pending_text[j]
                if req.normalize:
                    vec = normalize_vector(vec)
                if req.dimensions and len(vec) > req.dimensions:
                    vec = vec[: req.dimensions]

                results[idx] = EmbeddingResult.from_vector(vec)
                key = make_cache_key(
                    str(ctx.tenant_id), req.model, text,
                )
                try:
                    await self._cache.set(key, vec, ttl=_CACHE_TTL)
                except Exception as exc:
                    logger.debug("cache set failed: %s", exc)

                try:
                    h = make_vector_hash(text, req.model)
                    await self._vectors.save(ctx, {
                        "tenant_id": ctx.tenant_id,
                        "model_id": model.id,
                        "source_hash": h,
                        "source_text": text[:2000],
                        "vector_json": vector_to_json(vec),
                        "dimension": len(vec),
                        "metadata_json": "{}",
                    })
                except Exception as exc:
                    logger.debug("vector persist failed: %s", exc)

            if self._bus:
                try:
                    await self._bus.publish(EmbeddingCreated(
                        vector_id=uuid.uuid4(),
                        tenant_id=ctx.tenant_id,
                        model_id=model.id,
                        dimension=len(vectors[0]) if vectors else 0,
                        tokens=sum(len(t) // 4 for t in pending_text),
                        cached=False,
                    ))
                except Exception as exc:
                    logger.debug("publish failed: %s", exc)

        return [r for r in results if r is not None]

    async def embed_batch(
        self, ctx: Any, *,
        model_name: str, texts: list[str],
        config: Optional[BatchConfig] = None,
    ) -> uuid.UUID:
        """TH: batch embedding (async) | EN: batch embedding"""
        cfg = config or BatchConfig()
        model = await self._models.find_by_name(ctx, model_name)
        if model is None or not model.is_active:
            raise NotFoundAppError(f"model not found: {model_name}")

        batch_data = {
            "tenant_id": ctx.tenant_id,
            "user_id": ctx.user_id or ctx.tenant_id,
            "model_id": model.id,
            "total": len(texts),
        }
        saved = await self._batches.create(ctx, batch_data)

        if self._bus:
            try:
                await self._bus.publish(BatchStarted(
                    batch_id=saved.id,
                    tenant_id=ctx.tenant_id,
                    total=len(texts),
                ))
            except Exception as exc:
                logger.debug("publish failed: %s", exc)

        asyncio.create_task(
            self._run_batch(ctx, saved.id, model_name, texts, cfg)
        )
        return saved.id

    async def _run_batch(
        self, ctx: Any, batch_id: uuid.UUID,
        model_name: str, texts: list[str], cfg: BatchConfig,
    ) -> None:
        started = ms_now()
        completed = 0
        failed = 0
        try:
            sem = asyncio.Semaphore(cfg.max_concurrency)

            async def one(text: str) -> bool:
                async with sem:
                    try:
                        await self.embed(ctx, EmbeddingRequest(
                            model=model_name, input=[text],
                        ))
                        return True
                    except Exception as exc:
                        logger.warning("batch item failed: %s", exc)
                        return False

            for i in range(0, len(texts), cfg.batch_size):
                chunk = texts[i : i + cfg.batch_size]
                outs = await asyncio.gather(*(one(t) for t in chunk))
                completed += sum(1 for o in outs if o)
                failed += sum(1 for o in outs if not o)

                batch = await self._batches.find_by_id(ctx, batch_id)
                if batch is not None:
                    batch.completed = completed
                    batch.failed = failed
                    if batch.status == "PENDING":
                        batch.status = "RUNNING"
                    await self._batches.update(ctx, batch)

            batch = await self._batches.find_by_id(ctx, batch_id)
            if batch is not None:
                batch.status = "DONE"
                from datetime import datetime, timezone
                batch.finished_at = datetime.now(timezone.utc)
                batch.completed = completed
                batch.failed = failed
                await self._batches.update(ctx, batch)

            logger.info(
                "batch done id=%s ok=%d fail=%d ms=%d",
                batch_id, completed, failed, ms_now() - started,
            )
        except Exception as exc:
            logger.exception("batch failed: %s", exc)
            try:
                b = await self._batches.find_by_id(ctx, batch_id)
                if b is not None:
                    b.status = "FAILED"
                    await self._batches.update(ctx, b)
            except Exception:
                pass

    async def list_models(self, ctx: Any) -> list[Any]:
        return await self._models.find_all_active(ctx)

    async def list_providers(self, ctx: Any) -> list[Any]:
        return await self._providers.find_all_active(ctx)

    async def _call_with_retry(
        self, client: Any, texts: list[str], model_name: str,
        *, normalize: bool, dimensions: Optional[int],
    ) -> list[list[float]]:
        last_exc: Optional[Exception] = None
        for attempt in range(_MAX_RETRIES):
            try:
                return await client.embed(
                    texts, model_name,
                    normalize=normalize, dimensions=dimensions,
                )
            except Exception as exc:
                last_exc = exc
                logger.warning(
                    "embed attempt=%d failed: %s", attempt + 1, exc,
                )
                if attempt < _MAX_RETRIES - 1:
                    await asyncio.sleep(_BACKOFF[attempt])
        raise ProviderAppError(
            f"embedding provider failed: {last_exc}"
        )
