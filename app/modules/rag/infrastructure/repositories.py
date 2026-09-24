"""rag repositories — SQLAlchemy 2.0 async"""
from __future__ import annotations
import uuid

from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.rag.application.exceptions import AppError
from app.modules.rag.infrastructure.models import (
    RAGChunkModel, RAGCitationModel, RAGDocumentModel,
    RAGPipelineModel, RAGRetrievalLogModel, RAGRunModel,
)


class DocumentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, ctx: object, d: RAGDocumentModel) -> RAGDocumentModel:
        try:
            self._session.add(d)
            await self._session.flush()
            return d
        except SQLAlchemyError as exc:
            logger.error(f"doc.save failed: {exc}")
            raise AppError(str(exc)) from exc

    async def find_by_id(self, ctx: object, id: uuid.UUID) -> RAGDocumentModel | None:
        try:
            r = await self._session.execute(
                select(RAGDocumentModel).where(
                    RAGDocumentModel.id == id,
                    RAGDocumentModel.status != "DELETED",
                )
            )
            return r.scalar_one_or_none()
        except SQLAlchemyError as exc:
            logger.error(f"doc.find failed: {exc}")
            raise AppError(str(exc)) from exc

    async def find_by_hash(self, ctx: object, h: str) -> RAGDocumentModel | None:
        try:
            r = await self._session.execute(
                select(RAGDocumentModel).where(
                    RAGDocumentModel.hash == h,
                )
            )
            return r.scalar_one_or_none()
        except SQLAlchemyError as exc:
            logger.error(f"doc.find_hash failed: {exc}")
            raise AppError(str(exc)) from exc

    async def list(self, ctx: object, limit: int, offset: int) -> list:
        try:
            r = await self._session.execute(
                select(RAGDocumentModel)
                .where(RAGDocumentModel.status != "DELETED")
                .order_by(RAGDocumentModel.created_at.desc())
                .limit(max(1, min(limit, 500)))
                .offset(max(0, offset))
            )
            return list(r.scalars().all())
        except SQLAlchemyError as exc:
            logger.error(f"doc.list failed: {exc}")
            raise AppError(str(exc)) from exc

    async def update(self, ctx: object, d: RAGDocumentModel) -> RAGDocumentModel:
        try:
            await self._session.flush()
            return d
        except SQLAlchemyError as exc:
            logger.error(f"doc.update failed: {exc}")
            raise AppError(str(exc)) from exc


class ChunkRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_many(self, ctx: object, chunks: list) -> int:
        try:
            for c in chunks:
                self._session.add(c)
            await self._session.flush()
            return len(chunks)
        except SQLAlchemyError as exc:
            logger.error(f"chunk.create failed: {exc}")
            raise AppError(str(exc)) from exc

    async def find_by_document(self, ctx: object, document_id: uuid.UUID) -> list:
        try:
            r = await self._session.execute(
                select(RAGChunkModel)
                .where(RAGChunkModel.document_id == document_id)
                .order_by(RAGChunkModel.ordinal.asc())
            )
            return list(r.scalars().all())
        except SQLAlchemyError as exc:
            logger.error(f"chunk.find failed: {exc}")
            raise AppError(str(exc)) from exc

    async def delete_by_document(self, ctx: object, document_id: uuid.UUID) -> int:
        try:
            from sqlalchemy import delete
            res = await self._session.execute(
                delete(RAGChunkModel).where(
                    RAGChunkModel.document_id == document_id,
                )
            )
            await self._session.flush()
            return int(res.rowcount or 0)
        except SQLAlchemyError as exc:
            logger.error(f"chunk.delete failed: {exc}")
            raise AppError(str(exc)) from exc


class PipelineRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, ctx: object, p: RAGPipelineModel) -> RAGPipelineModel:
        try:
            self._session.add(p)
            await self._session.flush()
            return p
        except SQLAlchemyError as exc:
            logger.error(f"pipe.save failed: {exc}")
            raise AppError(str(exc)) from exc

    async def find_by_id(self, ctx: object, id: uuid.UUID) -> RAGPipelineModel | None:
        try:
            r = await self._session.execute(
                select(RAGPipelineModel).where(
                    RAGPipelineModel.id == id,
                )
            )
            return r.scalar_one_or_none()
        except SQLAlchemyError as exc:
            logger.error(f"pipe.find failed: {exc}")
            raise AppError(str(exc)) from exc

    async def find_by_name(self, ctx: object, name: str) -> RAGPipelineModel | None:
        try:
            r = await self._session.execute(
                select(RAGPipelineModel).where(
                    RAGPipelineModel.name == name,
                )
            )
            return r.scalar_one_or_none()
        except SQLAlchemyError as exc:
            logger.error(f"pipe.find_name failed: {exc}")
            raise AppError(str(exc)) from exc

    async def find_all_active(self, ctx: object) -> list:
        try:
            r = await self._session.execute(
                select(RAGPipelineModel)
                .where(RAGPipelineModel.is_active.is_(True))
                .order_by(RAGPipelineModel.name.asc())
            )
            return list(r.scalars().all())
        except SQLAlchemyError as exc:
            logger.error(f"pipe.list failed: {exc}")
            raise AppError(str(exc)) from exc


class RunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, ctx: object, r: RAGRunModel) -> RAGRunModel:
        try:
            self._session.add(r)
            await self._session.flush()
            return r
        except SQLAlchemyError as exc:
            logger.error(f"run.save failed: {exc}")
            raise AppError(str(exc)) from exc

    async def find_by_id(self, ctx: object, id: uuid.UUID) -> RAGRunModel | None:
        try:
            r = await self._session.execute(
                select(RAGRunModel).where(RAGRunModel.id == id)
            )
            return r.scalar_one_or_none()
        except SQLAlchemyError as exc:
            logger.error(f"run.find failed: {exc}")
            raise AppError(str(exc)) from exc

    async def update(self, ctx: object, r: RAGRunModel) -> RAGRunModel:
        try:
            await self._session.flush()
            return r
        except SQLAlchemyError as exc:
            logger.error(f"run.update failed: {exc}")
            raise AppError(str(exc)) from exc


class CitationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_many(self, ctx: object, citations: list) -> int:
        try:
            for c in citations:
                self._session.add(c)
            await self._session.flush()
            return len(citations)
        except SQLAlchemyError as exc:
            logger.error(f"cit.create failed: {exc}")
            raise AppError(str(exc)) from exc

    async def find_by_run(self, ctx: object, run_id: uuid.UUID) -> list:
        try:
            r = await self._session.execute(
                select(RAGCitationModel)
                .where(RAGCitationModel.run_id == run_id)
                .order_by(RAGCitationModel.rank.asc())
            )
            return list(r.scalars().all())
        except SQLAlchemyError as exc:
            logger.error(f"cit.find failed: {exc}")
            raise AppError(str(exc)) from exc


class RetrievalLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, ctx: object, log: RAGRetrievalLogModel) -> RAGRetrievalLogModel:
        try:
            self._session.add(log)
            await self._session.flush()
            return log
        except SQLAlchemyError as exc:
            logger.error(f"log.create failed: {exc}")
            raise AppError(str(exc)) from exc

    async def find_by_run(self, ctx: object, run_id: uuid.UUID) -> list:
        try:
            r = await self._session.execute(
                select(RAGRetrievalLogModel)
                .where(RAGRetrievalLogModel.run_id == run_id)
                .order_by(RAGRetrievalLogModel.created_at.asc())
            )
            return list(r.scalars().all())
        except SQLAlchemyError as exc:
            logger.error(f"log.find failed: {exc}")
            raise AppError(str(exc)) from exc
