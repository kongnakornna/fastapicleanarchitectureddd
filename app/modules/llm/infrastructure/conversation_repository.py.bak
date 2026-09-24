"""Conversation repository"""
from __future__ import annotations
import uuid

from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.llm.application.exceptions import ApplicationError
from app.modules.llm.infrastructure.models import ConversationModel


class ConversationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(
        self, ctx: object, conv_id: uuid.UUID,
    ) -> ConversationModel | None:
        try:
            result = await self._session.execute(
                select(ConversationModel).where(
                    ConversationModel.id == conv_id,
                    ConversationModel.status != "DELETED",
                )
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            logger.error(f"conv.find_by_id failed: {exc}")
            raise ApplicationError(str(exc)) from exc

    async def find_by_user(
        self, ctx: object, user_id: uuid.UUID, limit: int = 50,
    ) -> list[ConversationModel]:
        try:
            result = await self._session.execute(
                select(ConversationModel)
                .where(
                    ConversationModel.user_id == user_id,
                    ConversationModel.status != "DELETED",
                )
                .order_by(ConversationModel.created_at.desc())
                .limit(limit)
            )
            return list(result.scalars().all())
        except SQLAlchemyError as exc:
            logger.error(f"conv.find_by_user failed: {exc}")
            raise ApplicationError(str(exc)) from exc

    async def save(
        self, ctx: object, conv: ConversationModel,
    ) -> ConversationModel:
        try:
            self._session.add(conv)
            await self._session.flush()
            return conv
        except SQLAlchemyError as exc:
            logger.error(f"conv.save failed: {exc}")
            raise ApplicationError(str(exc)) from exc

    async def update(
        self, ctx: object, conv: ConversationModel,
    ) -> ConversationModel:
        try:
            await self._session.flush()
            return conv
        except SQLAlchemyError as exc:
            logger.error(f"conv.update failed: {exc}")
            raise ApplicationError(str(exc)) from exc

    async def soft_delete(
        self, ctx: object, conv_id: uuid.UUID,
    ) -> bool:
        try:
            conv = await self.find_by_id(ctx, conv_id)
            if conv:
                conv.status = "DELETED"
                await self._session.flush()
                return True
            return False
        except SQLAlchemyError as exc:
            logger.error(f"conv.soft_delete failed: {exc}")
            raise ApplicationError(str(exc)) from exc
