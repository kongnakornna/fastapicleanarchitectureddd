"""rag use cases"""
from __future__ import annotations
import logging
import uuid
from decimal import Decimal
from typing import Any, Optional

from app.modules.rag.application.exceptions import (
    ConflictAppError, NotFoundAppError, ProviderAppError,
)
from app.modules.rag.application.utils import (
    build_context_block, json_dumps_safe, make_cache_key, ms_now,
)
from app.modules.rag.domain.enums import DocumentStatus, RunStatus
from app.modules.rag.domain.events import (
    DocumentChunked, DocumentIngested, RAGAnswerGenerated,
    RetrievalCompleted,
)
from app.modules.rag.domain.helpers.chunkers import (
    chunk_fixed, chunk_markdown, chunk_recursive,
)
from app.modules.rag.domain.helpers.hasher import document_hash
from app.modules.rag.domain.value_objects import (
    ChunkConfig, CitationVO,
)

logger = logging.getLogger(__name__)


class RAGUseCase:
    """TH: use case หลักของ RAG | EN: core RAG use case"""

    def __init__(self, **deps: Any) -> None:
        for key, value in deps.items():
            setattr(self, f"_{key}", value)
        self._collection_id = getattr(
            self, "_collection_id", None,
        ) or uuid.UUID(int=0)

    async def ingest(
        self, ctx: Any, *,
        content: str, source_uri: str = "",
        mime_type: str = "text/plain", title: str = "",
        pipeline_id: Optional[uuid.UUID] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Any:
        """TH: ingest document | EN: ingest document"""
        from app.modules.rag.infrastructure.models import (
            RAGChunkModel, RAGDocumentModel,
        )

        if not content:
            raise ProviderAppError("empty document")

        pipeline = await self._resolve_pipeline(ctx, pipeline_id)

        h = document_hash(content)
        existing = await self._documents.find_by_hash(ctx, h)
        if existing is not None and existing.status != "DELETED":
            return existing

        doc = RAGDocumentModel(
            tenant_id=ctx.tenant_id,
            user_id=ctx.user_id or ctx.tenant_id,
            source_uri=source_uri, mime_type=mime_type,
            title=title or source_uri or "untitled",
            content=content, hash=h,
            size_bytes=len(content.encode("utf-8")),
            metadata_json=json_dumps_safe(metadata or {}),
            status="PENDING",
        )
        saved = await self._documents.save(ctx, doc)

        if self._bus:
            try:
                await self._bus.publish(DocumentIngested(
                    document_id=saved.id,
                    tenant_id=saved.tenant_id,
                    source_uri=saved.source_uri,
                    size_bytes=saved.size_bytes or 0,
                ))
            except Exception:
                pass

        saved.status = "PROCESSING"
        saved = await self._documents.update(ctx, saved)

        try:
            chunk_texts = self._chunk(content, pipeline)
            if not chunk_texts:
                saved.status = "FAILED"
                await self._documents.update(ctx, saved)
                return saved

            embeddings = await self._embedder.embed(
                model=pipeline.embedding_model, texts=chunk_texts,
            )

            items: list[dict[str, Any]] = []
            for i, ct in enumerate(chunk_texts):
                vec = self._extract_vector(
                    embeddings[i],
                ) if i < len(embeddings) else []
                items.append({
                    "source_id": f"{saved.id}:{i}",
                    "vector": vec,
                    "metadata": {
                        "document_id": str(saved.id),
                        "ordinal": i,
                    },
                })
            if items:
                await self._vector_store.upsert(
                    collection_id=self._collection_id, items=items,
                )

            chunk_rows = [
                RAGChunkModel(
                    tenant_id=ctx.tenant_id,
                    document_id=saved.id,
                    ordinal=i, content=ct,
                    token_count=max(1, len(ct) // 4),
                    metadata_json="{}",
                )
                for i, ct in enumerate(chunk_texts)
            ]
            count = await self._chunks.create_many(ctx, chunk_rows)

            saved.status = "READY"
            saved.chunk_count = count
            saved = await self._documents.update(ctx, saved)

            if self._bus:
                try:
                    await self._bus.publish(DocumentChunked(
                        document_id=saved.id,
                        tenant_id=saved.tenant_id,
                        chunk_count=count,
                    ))
                except Exception:
                    pass
        except Exception as exc:
            logger.exception("ingest failed: %s", exc)
            saved.status = "FAILED"
            await self._documents.update(ctx, saved)
            raise ProviderAppError(
                f"ingest failed: {exc}"
            ) from exc
        return saved

    async def query(
        self, ctx: Any, *,
        query: str, pipeline_id: Optional[uuid.UUID] = None,
        conversation_id: Optional[uuid.UUID] = None,
        use_cache: bool = True,
    ) -> dict[str, Any]:
        """TH: query + generate | EN: query + generate"""
        from app.modules.rag.infrastructure.models import (
            RAGCitationModel, RAGRetrievalLogModel, RAGRunModel,
        )

        if not query.strip():
            raise ProviderAppError("empty query")

        pipeline = await self._resolve_pipeline(ctx, pipeline_id)

        run = RAGRunModel(
            tenant_id=ctx.tenant_id,
            user_id=ctx.user_id or ctx.tenant_id,
            pipeline_id=pipeline.id,
            conversation_id=conversation_id,
            query=query,
            model_name=pipeline.generation_model,
            status="QUEUED",
        )
        saved_run = await self._runs.save(ctx, run)
        started_ms = ms_now()

        cache_key = make_cache_key(
            str(ctx.tenant_id), pipeline.generation_model,
            query, pipeline.top_k,
        )
        if use_cache and self._cache is not None:
            try:
                cached = await self._cache.get(cache_key)
                if cached:
                    cached["cached"] = True
                    cached["run_id"] = str(saved_run.id)
                    return cached
            except Exception as exc:
                logger.debug("cache get failed: %s", exc)

        try:
            saved_run.status = "RETRIEVING"
            await self._runs.update(ctx, saved_run)

            retrieve_started = ms_now()
            candidates = await self._retrieve(ctx, pipeline, query)
            retrieve_ms = ms_now() - retrieve_started

            await self._retrieval_logs.create(ctx, RAGRetrievalLogModel(
                tenant_id=ctx.tenant_id, run_id=saved_run.id,
                stage="retrieve", top_k=pipeline.top_k,
                candidates_json=json_dumps_safe([
                    {
                        "chunk_id": str(c.get("chunk_id", "")),
                        "score": c.get("score", 0),
                    }
                    for c in candidates[:50]
                ]),
                latency_ms=retrieve_ms,
            ))

            if self._bus:
                try:
                    await self._bus.publish(RetrievalCompleted(
                        run_id=saved_run.id,
                        tenant_id=ctx.tenant_id,
                        retriever_type=str(pipeline.retriever_type),
                        top_k=pipeline.top_k,
                        latency_ms=retrieve_ms,
                    ))
                except Exception:
                    pass

            saved_run.status = "GENERATING"
            await self._runs.update(ctx, saved_run)

            context_block = build_context_block(candidates)
            messages = [{"role": "user", "content": query}]
            system_prompt = (
                "You are a helpful assistant. "
                "Answer using ONLY the following context. "
                "Cite sources as [1], [2], etc.\n\n"
                f"Context:\n{context_block}"
            )

            answer, tokens, cost = await self._generate(
                pipeline, messages, system_prompt,
            )

            saved_run.answer = answer
            saved_run.total_tokens = tokens
            saved_run.cost_usd = Decimal(str(cost))
            saved_run.latency_ms = ms_now() - started_ms
            saved_run.status = "DONE"
            await self._runs.update(ctx, saved_run)

            citations = self._build_citations(candidates)
            if citations:
                await self._citations.create_many(ctx, [
                    RAGCitationModel(
                        tenant_id=ctx.tenant_id,
                        run_id=saved_run.id,
                        chunk_id=cv.chunk_id,
                        document_id=cv.document_id,
                        score=cv.score, rank=cv.rank,
                        snippet=cv.snippet,
                    )
                    for cv in citations
                ])

            if self._bus:
                try:
                    await self._bus.publish(RAGAnswerGenerated(
                        run_id=saved_run.id,
                        tenant_id=ctx.tenant_id,
                        model_name=pipeline.generation_model,
                        citation_count=len(citations),
                        tokens_used=tokens,
                        cost_usd=str(cost),
                    ))
                except Exception:
                    pass

            result = {
                "run_id": str(saved_run.id),
                "answer": answer,
                "citations": [cv.model_dump() for cv in citations],
                "usage": {
                    "total_tokens": tokens,
                    "cost_usd": str(cost),
                },
                "cached": False,
            }

            if use_cache and self._cache is not None:
                try:
                    await self._cache.set(cache_key, {
                        "answer": answer,
                        "citations": [
                            cv.model_dump() for cv in citations
                        ],
                        "usage": {
                            "total_tokens": tokens,
                            "cost_usd": str(cost),
                        },
                    })
                except Exception as exc:
                    logger.debug("cache set failed: %s", exc)
            return result

        except Exception as exc:
            logger.exception("rag query failed: %s", exc)
            saved_run.status = "FAILED"
            saved_run.error_message = str(exc)[:500]
            try:
                await self._runs.update(ctx, saved_run)
            except Exception:
                pass
            if isinstance(exc, (NotFoundAppError, ProviderAppError)):
                raise
            raise ProviderAppError(
                f"rag query failed: {exc}"
            ) from exc

    async def list_documents(
        self, ctx: Any, *, limit: int = 50, offset: int = 0,
    ) -> list[Any]:
        return await self._documents.list(
            ctx, limit=limit, offset=offset,
        )

    async def get_document(
        self, ctx: Any, document_id: uuid.UUID,
    ) -> tuple[Any, list[Any]]:
        doc = await self._documents.find_by_id(ctx, document_id)
        if doc is None:
            raise NotFoundAppError("document not found")
        chunks = await self._chunks.find_by_document(
            ctx, document_id,
        )
        return doc, chunks

    async def delete_document(
        self, ctx: Any, document_id: uuid.UUID,
    ) -> bool:
        doc = await self._documents.find_by_id(ctx, document_id)
        if doc is None:
            raise NotFoundAppError("document not found")
        doc.status = "DELETED"
        await self._documents.update(ctx, doc)
        try:
            await self._chunks.delete_by_document(ctx, document_id)
        except Exception as exc:
            logger.debug("delete chunks failed: %s", exc)
        return True

    async def create_pipeline(
        self, ctx: Any, **kwargs: Any,
    ) -> Any:
        from app.modules.rag.infrastructure.models import (
            RAGPipelineModel,
        )
        existing = await self._pipelines.find_by_name(
            ctx, kwargs.get("name", ""),
        )
        if existing is not None:
            raise ConflictAppError("pipeline name exists")
        p = RAGPipelineModel(tenant_id=ctx.tenant_id, **kwargs)
        return await self._pipelines.save(ctx, p)

    async def list_pipelines(self, ctx: Any) -> list[Any]:
        return await self._pipelines.find_all_active(ctx)

    async def get_run(self, ctx: Any, run_id: uuid.UUID) -> Any:
        r = await self._runs.find_by_id(ctx, run_id)
        if r is None:
            raise NotFoundAppError("run not found")
        return r

    async def _resolve_pipeline(
        self, ctx: Any, pipeline_id: Optional[uuid.UUID],
    ) -> Any:
        from app.modules.rag.infrastructure.models import (
            RAGPipelineModel,
        )
        if pipeline_id is not None:
            p = await self._pipelines.find_by_id(ctx, pipeline_id)
            if p is None:
                raise NotFoundAppError("pipeline not found")
            return p
        existing = await self._pipelines.find_all_active(ctx)
        if existing:
            return existing[0]
        default = RAGPipelineModel(
            tenant_id=ctx.tenant_id, name="default",
            chunker_type="recursive", chunk_size=512,
            chunk_overlap=50, retriever_type="vector",
            top_k=5, reranker_type="none",
        )
        return await self._pipelines.save(ctx, default)

    def _chunk(self, content: str, pipeline: Any) -> list[str]:
        cfg = ChunkConfig(
            chunker_type=pipeline.chunker_type,
            chunk_size=pipeline.chunk_size,
            chunk_overlap=pipeline.chunk_overlap,
        )
        ct = str(cfg.chunker_type)
        if ct == "fixed":
            return chunk_fixed(
                content, chunk_size=cfg.chunk_size,
                chunk_overlap=cfg.chunk_overlap,
            )
        if ct == "markdown":
            return chunk_markdown(
                content, chunk_size=cfg.chunk_size,
                chunk_overlap=cfg.chunk_overlap,
            )
        return chunk_recursive(
            content, chunk_size=cfg.chunk_size,
            chunk_overlap=cfg.chunk_overlap,
            separators=cfg.separators,
        )

    @staticmethod
    def _extract_vector(item: Any) -> list[float]:
        if item is None:
            return []
        if isinstance(item, list):
            return [float(x) for x in item]
        vec = getattr(item, "vector", None)
        if vec is not None:
            return [float(x) for x in vec]
        return []

    async def _retrieve(
        self, ctx: Any, pipeline: Any, query: str,
    ) -> list[dict[str, Any]]:
        rt = str(pipeline.retriever_type)
        if rt == "hybrid" and self._hybrid is not None:
            try:
                hits = await self._hybrid.search(
                    query=query, top_k=pipeline.top_k,
                )
                return [self._hit_to_dict(h) for h in hits]
            except Exception as exc:
                logger.debug("hybrid failed: %s", exc)

        embeddings = await self._embedder.embed(
            model=pipeline.embedding_model, texts=[query],
        )
        qv = self._extract_vector(embeddings[0]) if embeddings else []
        if not qv:
            return []
        try:
            hits = await self._vector_store.query(
                collection_id=self._collection_id,
                vector=qv, top_k=pipeline.top_k,
            )
        except Exception as exc:
            logger.warning("vector query failed: %s", exc)
            return []
        return [self._hit_to_dict(h) for h in hits]

    @staticmethod
    def _hit_to_dict(hit: Any) -> dict[str, Any]:
        if isinstance(hit, dict):
            return hit
        return {
            "chunk_id": str(getattr(hit, "vector_id", "")),
            "source_id": getattr(hit, "source_id", ""),
            "score": float(getattr(hit, "score", 0.0)),
            "metadata": getattr(hit, "metadata", {}) or {},
        }

    def _build_citations(
        self, candidates: list[dict[str, Any]],
    ) -> list[CitationVO]:
        out: list[CitationVO] = []
        for i, c in enumerate(candidates, start=1):
            meta = c.get("metadata") or {}
            chunk_id_raw = meta.get("chunk_id") or c.get("chunk_id")
            doc_id_raw = meta.get("document_id") or ""
            try:
                chunk_uuid = (
                    uuid.UUID(str(chunk_id_raw))
                    if chunk_id_raw else uuid.uuid4()
                )
                doc_uuid = (
                    uuid.UUID(str(doc_id_raw))
                    if doc_id_raw else uuid.uuid4()
                )
            except ValueError:
                continue
            out.append(CitationVO(
                chunk_id=chunk_uuid, document_id=doc_uuid,
                score=float(c.get("score", 0.0)),
                rank=i,
                snippet=str(c.get("content", ""))[:240],
            ))
        return out

    async def _generate(
        self, pipeline: Any, messages: list[dict[str, Any]],
        system_prompt: str,
    ) -> tuple[str, int, Decimal]:
        if self._generator is None:
            return "", 0, Decimal("0")
        try:
            result = await self._generator.chat(
                model=pipeline.generation_model,
                messages=messages,
                system_prompt=system_prompt,
            )
        except Exception as exc:
            logger.warning("generation failed: %s", exc)
            raise ProviderAppError(
                f"generation failed: {exc}"
            ) from exc

        if isinstance(result, dict):
            content = result.get("content", "")
            usage = result.get("usage") or {}
            tokens = int(usage.get("total_tokens", 0))
            cost = Decimal(str(usage.get("cost_usd", "0")))
        else:
            content = getattr(result, "content", "")
            usage_obj = getattr(result, "usage", None)
            tokens = int(getattr(
                usage_obj, "total_tokens", 0,
            ) or 0)
            cost = Decimal(str(
                getattr(usage_obj, "cost_usd", "0") or "0",
            ))
        return content, tokens, cost
