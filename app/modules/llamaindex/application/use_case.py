"""llamaindex use cases"""
from __future__ import annotations
import logging
import uuid
from typing import Any, Optional

from app.modules.llamaindex.application.exceptions import (
    ConflictAppError, IngestionAppError, NotFoundAppError,
    QueryAppError, ValidationAppError,
)
from app.modules.llamaindex.application.utils import (
    document_hash, json_dumps_safe, json_loads_safe, ms_now,
)
from app.modules.llamaindex.domain.enums import (
    DocumentStatus, NodeType, ResponseMode,
)
from app.modules.llamaindex.domain.events import (
    DocumentIngested, IndexCreated, NodesCreated, QueryExecuted,
    ResponseSynthesized,
)
from app.modules.llamaindex.domain.helpers.relationships import (
    build_node_relationships,
)
from app.modules.llamaindex.domain.helpers.splitter import (
    SentenceSplitter,
)
from app.modules.llamaindex.domain.helpers.synthesizer import (
    synthesize_compact, synthesize_refine, synthesize_tree_summarize,
)
from app.modules.llamaindex.domain.value_objects import (
    IndexSpec, QueryEngineSpec,
)

logger = logging.getLogger(__name__)


class LlamaIndexUseCase:
    """TH: use case หลัก | EN: core use case"""

    def __init__(self, **deps: Any) -> None:
        for key, value in deps.items():
            setattr(self, f"_{key}", value)

    # ─── Index ────────────────────────────────────
    async def create_index(
        self, ctx: Any, spec: IndexSpec,
    ) -> Any:
        from app.modules.llamaindex.infrastructure.models import (
            LIIndexModel,
        )
        existing = await self._indexes.find_by_name(ctx, spec.name)
        if existing is not None:
            raise ConflictAppError(f"index exists: {spec.name}")

        row = LIIndexModel(
            tenant_id=ctx.tenant_id, name=spec.name,
            index_type=str(spec.index_type),
            embed_model=spec.embed_model,
            storage_kind=spec.storage_kind,
            config_json=json_dumps_safe(spec.config or {}),
            is_active=True,
        )
        saved = await self._indexes.save(ctx, row)
        if self._bus:
            try:
                await self._bus.publish(IndexCreated(
                    index_id=saved.id, tenant_id=ctx.tenant_id,
                    name=saved.name, index_type=str(spec.index_type),
                ))
            except Exception:
                pass
        return saved

    async def list_indexes(self, ctx: Any) -> list[Any]:
        return await self._indexes.find_all_active(ctx)

    async def get_index(self, ctx: Any, index_id: uuid.UUID) -> Any:
        idx = await self._indexes.find_by_id(ctx, index_id)
        if idx is None:
            raise NotFoundAppError("index not found")
        return idx

    # ─── Ingest ───────────────────────────────────
    async def ingest(
        self, ctx: Any, *, index_id: uuid.UUID,
        content: str, source_uri: str = "",
        mime_type: str = "text/plain", title: str = "",
        chunk_size: int = 512, chunk_overlap: int = 50,
    ) -> Any:
        """TH: ingest document → nodes | EN: ingest document"""
        from app.modules.llamaindex.infrastructure.models import (
            LIDocumentModel, LINodeModel,
        )

        if not content:
            raise IngestionAppError("empty content")

        index = await self.get_index(ctx, index_id)
        h = document_hash(content)

        existing = await self._documents.find_by_hash(ctx, h)
        if existing is not None and existing.status == DocumentStatus.READY.value:
            return existing

        doc = LIDocumentModel(
            tenant_id=ctx.tenant_id, index_id=index.id,
            source_uri=source_uri, mime_type=mime_type,
            title=title or source_uri or "untitled",
            hash=h, status=DocumentStatus.PROCESSING.value,
        )
        saved_doc = await self._documents.save(ctx, doc)

        try:
            parser = SentenceSplitter(
                chunk_size=chunk_size, chunk_overlap=chunk_overlap,
            )
            chunks = parser.split(content)
            if not chunks:
                raise IngestionError("no chunks produced")

            # embed chunks
            embeddings: list[Any] = []
            if self._embedder is not None:
                try:
                    embeddings = await self._embedder.embed(
                        model=index.embed_model, texts=chunks,
                    )
                except Exception as exc:
                    logger.warning("embed failed: %s", exc)

            # upsert to vector store
            if self._vector_store is not None:
                collection_id = self._collection_id(index)
                try:
                    items = []
                    for i, chunk in enumerate(chunks):
                        vec = self._extract_vector(
                            embeddings[i] if i < len(embeddings) else None
                        )
                        items.append({
                            "source_id": f"{saved_doc.id}:{i}",
                            "vector": vec,
                            "metadata": {
                                "index_id": str(index.id),
                                "document_id": str(saved_doc.id),
                                "ordinal": i,
                            },
                        })
                    if items:
                        await self._vector_store.upsert(
                            collection_id=collection_id, items=items,
                        )
                except Exception as exc:
                    logger.warning("vector upsert failed: %s", exc)

            # persist nodes
            node_rows: list[LINodeModel] = []
            for i, chunk in enumerate(chunks):
                node_rows.append(LINodeModel(
                    tenant_id=ctx.tenant_id, index_id=index.id,
                    document_id=saved_doc.id,
                    node_type=NodeType.TEXT.value,
                    ordinal=i, content=chunk,
                    token_count=max(1, len(chunk) // 4),
                    relationships_json="{}",
                    metadata_json="{}",
                ))
            count = await self._nodes.create_many(ctx, node_rows)

            saved_doc.status = DocumentStatus.READY.value
            saved_doc.node_count = count
            await self._documents.update(ctx, saved_doc)

            if self._bus:
                try:
                    await self._bus.publish(DocumentIngested(
                        document_id=saved_doc.id,
                        tenant_id=ctx.tenant_id,
                        index_id=index.id,
                        source_uri=source_uri,
                    ))
                    await self._bus.publish(NodesCreated(
                        index_id=index.id,
                        tenant_id=ctx.tenant_id,
                        node_count=count,
                    ))
                except Exception:
                    pass

            return saved_doc
        except Exception as exc:
            logger.exception("ingest failed: %s", exc)
            saved_doc.status = DocumentStatus.FAILED.value
            try:
                await self._documents.update(ctx, saved_doc)
            except Exception:
                pass
            if isinstance(exc, IngestionError):
                raise
            raise IngestionAppError(f"ingest failed: {exc}") from exc

    # ─── Query ────────────────────────────────────
    async def query(
        self, ctx: Any, *, index_id: uuid.UUID,
        query: str, query_engine_id: Optional[uuid.UUID] = None,
        top_k: Optional[int] = None,
        response_mode: Optional[str] = None,
        model: str = "gpt-4o-mini",
    ) -> dict[str, Any]:
        """TH: query index | EN: query index"""
        from app.modules.llamaindex.infrastructure.models import (
            LIRunModel,
        )

        if not query.strip():
            raise ValidationAppError("empty query")

        index = await self.get_index(ctx, index_id)

        # resolve query engine
        engine = None
        if query_engine_id is not None:
            engine = await self._engines.find_by_id(ctx, query_engine_id)
            if engine is None:
                raise NotFoundAppError("query engine not found")
        else:
            engines = await self._engines.find_by_index(ctx, index.id)
            engine = engines[0] if engines else None

        eff_top_k = int(top_k or (engine.top_k if engine else 5))
        eff_mode = response_mode or (
            engine.response_mode if engine else ResponseMode.COMPACT.value
        )

        run = LIRunModel(
            tenant_id=ctx.tenant_id,
            user_id=ctx.user_id or ctx.tenant_id,
            index_id=index.id,
            query_engine_id=engine.id if engine else None,
            query=query,
            status="RUNNING",
        )
        saved_run = await self._runs.create(ctx, run)
        started = ms_now()

        source_nodes: list[dict[str, Any]] = []
        answer = ""
        tokens = 0

        try:
            source_nodes = await self._retrieve(
                ctx, index, query, top_k=eff_top_k,
                model=index.embed_model,
            )
            result = await self._synthesize(
                ctx, query=query, nodes=source_nodes,
                mode=eff_mode, model=model,
            )
            answer = result.get("content", "")
            tokens = int(result.get("tokens_used", 0) or 0)
        except Exception as exc:
            logger.exception("query failed: %s", exc)
            saved_run.status = "FAILED"
            saved_run.error_message = str(exc)[:500]
            saved_run.latency_ms = ms_now() - started
            await self._runs.update(ctx, saved_run)
            if isinstance(exc, (NotFoundAppError, ValidationAppError)):
                raise
            raise QueryAppError(f"query failed: {exc}") from exc

        latency = ms_now() - started
        saved_run.answer = answer
        saved_run.source_nodes_json = json_dumps_safe(source_nodes)
        saved_run.latency_ms = latency
        saved_run.tokens_used = tokens
        saved_run.status = "DONE"
        await self._runs.update(ctx, saved_run)

        if self._bus:
            try:
                await self._bus.publish(QueryExecuted(
                    run_id=saved_run.id, tenant_id=ctx.tenant_id,
                    query_engine_id=engine.id if engine else uuid.uuid4(),
                    latency_ms=latency,
                    source_count=len(source_nodes),
                ))
                await self._bus.publish(ResponseSynthesized(
                    run_id=saved_run.id, tenant_id=ctx.tenant_id,
                    response_mode=eff_mode, tokens_used=tokens,
                ))
            except Exception:
                pass

        return {
            "run_id": str(saved_run.id),
            "answer": answer,
            "source_nodes": source_nodes,
            "latency_ms": latency,
            "tokens_used": tokens,
            "response_mode": eff_mode,
        }

    # ─── Query Engines ────────────────────────────
    async def create_query_engine(
        self, ctx: Any, *, index_id: uuid.UUID, spec: QueryEngineSpec,
    ) -> Any:
        from app.modules.li.infrastructure.models import (
            LIQueryEngineModel,
        )
        await self.get_index(ctx, index_id)
        row = LIQueryEngineModel(
            tenant_id=ctx.tenant_id, index_id=index_id,
            name=spec.name,
            retriever_type=spec.retriever_type,
            top_k=spec.top_k,
            response_mode=str(spec.response_mode),
            similarity_top_k=spec.similarity_top_k,
        )
        return await self._engines.save(ctx, row)

    async def list_query_engines(
        self, ctx: Any, index_id: uuid.UUID,
    ) -> list[Any]:
        await self.get_index(ctx, index_id)
        return await self._engines.find_by_index(ctx, index_id)

    # ─── Runs ─────────────────────────────────────
    async def get_run(self, ctx: Any, run_id: uuid.UUID) -> Any:
        r = await self._runs.find_by_id(ctx, run_id)
        if r is None:
            raise NotFoundAppError("run not found")
        return r

    # ─── Internal ─────────────────────────────────
    async def _retrieve(
        self, ctx: Any, index: Any, query: str,
        *, top_k: int, model: str,
    ) -> list[dict[str, Any]]:
        if self._embedder is None or self._vector_store is None:
            return []
        try:
            embeddings = await self._embedder.embed(
                model=model, texts=[query],
            )
            qv = self._extract_vector(
                embeddings[0] if embeddings else None,
            )
            if not qv:
                return []
            collection_id = self._collection_id(index)
            hits = await self._vector_store.query(
                collection_id=collection_id, vector=qv, top_k=top_k,
            )
            return [self._hit_to_dict(h) for h in hits]
        except Exception as exc:
            logger.warning("retrieve failed: %s", exc)
            return []

    async def _synthesize(
        self, ctx: Any, *, query: str,
        nodes: list[dict[str, Any]],
        mode: str, model: str,
    ) -> dict[str, Any]:
        if self._llm is None:
            return {"content": "", "tokens_used": 0}
        if mode == ResponseMode.REFINE.value:
            return await synthesize_refine(
                self._llm, tenant_id=ctx.tenant_id, model=model,
                query=query, nodes=nodes,
            )
        if mode == ResponseMode.TREE_SUMMARIZE.value:
            return await synthesize_tree_summarize(
                self._llm, tenant_id=ctx.tenant_id, model=model,
                query=query, nodes=nodes,
            )
        return await synthesize_compact(
            self._llm, tenant_id=ctx.tenant_id, model=model,
            query=query, nodes=nodes,
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

    @staticmethod
    def _hit_to_dict(hit: Any) -> dict[str, Any]:
        if isinstance(hit, dict):
            return hit
        return {
            "source_id": str(getattr(hit, "source_id", "")),
            "chunk_id": str(getattr(hit, "vector_id", "")),
            "score": float(getattr(hit, "score", 0.0)),
            "content": str(getattr(hit, "snippet", "")),
            "metadata": getattr(hit, "metadata", {}) or {},
        }

    @staticmethod
    def _collection_id(index: Any) -> uuid.UUID:
        """TH: ดึง collection_id จาก config (fallback)"""
        cfg = json_loads_safe(getattr(index, "config_json", "{}"), {})
        cid = cfg.get("collection_id")
        if cid:
            try:
                return uuid.UUID(str(cid))
            except ValueError:
                pass
        return uuid.UUID(int=0)
