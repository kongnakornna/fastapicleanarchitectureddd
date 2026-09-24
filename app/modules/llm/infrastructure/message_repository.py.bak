"""Message repository"""
from __future__ import annotations
import uuid

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.llm.application.exceptions import ApplicationError
from app.modules.llm.infrastructure.models import MessageModel


class MessageRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self, ctx: object, msg: MessageModel,
    ) -> MessageModel:
        try:
            self._session.add(msg)
            await self._session.flush()
            return msg
        except SQLAlchemyError as exc:
            logger.error(f"msg.create failed: {exc}")
            raise ApplicationError(str(exc)) from exc

    async def find_by_conversation(
        self, ctx: object, conv_id: uuid.UUID, limit: int = 200,
    ) -> list[MessageModel]:
        try:
            result = await self._session.execute(
                select(MessageModel)
                .where(MessageModel.conversation_id == conv_id)
                .order_by(MessageModel.created_at.asc())
                .limit(limit)
            )
            return list(result.scalars().all())
        except SQLAlchemyError as exc:
            logger.error(f"msg.find_by_conv failed: {exc}")
            raise ApplicationError(str(exc)) from exc

    async def count_by_conversation(
        self, ctx: object, conv_id: uuid.UUID,
    ) -> int:
        try:
            result = await self._session.execute(
                select(func.count())
                .select_from(MessageModel)
                .where(MessageModel.conversation_id == conv_id)
            )
            return int(result.scalar() or 0)
        except SQLAlchemyError as exc:
            logger.error(f"msg.count failed: {exc}")
            raise ApplicationError(str(exc)) from exc
