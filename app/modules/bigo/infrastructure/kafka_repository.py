"""Kafka repositories"""
from __future__ import annotations
import uuid
from typing import Any

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.bigo.application.exceptions import ApplicationError
from app.modules.bigo.infrastructure.models import (
    KafkaConsumerModel, KafkaQueueModel, KafkaTopicModel,
)


class SqlKafkaTopicRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, ctx: Any, topic: KafkaTopicModel) -> KafkaTopicModel:
        try:
            self._session.add(topic)
            await self._session.flush()
            return topic
        except SQLAlchemyError as exc:
            raise ApplicationError(str(exc)) from exc

    async def find_by_name(self, ctx: Any, name: str) -> KafkaTopicModel | None:
        try:
            result = await self._session.execute(
                select(KafkaTopicModel).where(KafkaTopicModel.name == name)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            raise ApplicationError(str(exc)) from exc

    async def find_all_active(self, ctx: Any) -> list[KafkaTopicModel]:
        try:
            result = await self._session.execute(
                select(KafkaTopicModel).where(KafkaTopicModel.is_active.is_(True))
            )
            return list(result.scalars().all())
        except SQLAlchemyError as exc:
            raise ApplicationError(str(exc)) from exc

    async def update(self, ctx: Any, topic: KafkaTopicModel) -> KafkaTopicModel:
        try:
            await self._session.flush()
            return topic
        except SQLAlchemyError as exc:
            raise ApplicationError(str(exc)) from exc


class SqlKafkaQueueRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, ctx: Any, q: KafkaQueueModel) -> KafkaQueueModel:
        try:
            self._session.add(q)
            await self._session.flush()
            return q
        except SQLAlchemyError as exc:
            raise ApplicationError(str(exc)) from exc

    async def find_by_topic(
        self, ctx: Any, topic: str, limit: int = 100,
    ) -> list[KafkaQueueModel]:
        try:
            result = await self._session.execute(
                select(KafkaQueueModel)
                .where(KafkaQueueModel.topic == topic)
                .order_by(KafkaQueueModel.captured_at.desc())
                .limit(limit)
            )
            return list(result.scalars().all())
        except SQLAlchemyError as exc:
            raise ApplicationError(str(exc)) from exc

    async def latest_by_topic(self, ctx: Any, topic: str) -> list[KafkaQueueModel]:
        try:
            subq = (
                select(
                    KafkaQueueModel.partition,
                    func.max(KafkaQueueModel.captured_at).label("max_at"),
                )
                .where(KafkaQueueModel.topic == topic)
                .group_by(KafkaQueueModel.partition)
                .subquery()
            )
            result = await self._session.execute(
                select(KafkaQueueModel).join(
                    subq,
                    (KafkaQueueModel.partition == subq.c.partition)
                    & (KafkaQueueModel.captured_at == subq.c.max_at),
                )
            )
            return list(result.scalars().all())
        except SQLAlchemyError as exc:
            raise ApplicationError(str(exc)) from exc

    async def total_lag(self, ctx: Any, topic: str) -> int:
        try:
            result = await self._session.execute(
                select(func.coalesce(func.sum(KafkaQueueModel.lag), 0))
                .where(KafkaQueueModel.topic == topic)
            )
            return int(result.scalar() or 0)
        except SQLAlchemyError as exc:
            raise ApplicationError(str(exc)) from exc


class SqlKafkaConsumerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, ctx: Any, c: KafkaConsumerModel) -> KafkaConsumerModel:
        try:
            existing = await self.find_by_group(ctx, c.group_id)
            if existing and existing.topic == c.topic:
                existing.member_count = c.member_count
                existing.total_lag = c.total_lag
                existing.health = c.health
                existing.last_commit_at = c.last_commit_at
                await self._session.flush()
                return existing
            self._session.add(c)
            await self._session.flush()
            return c
        except SQLAlchemyError as exc:
            raise ApplicationError(str(exc)) from exc

    async def find_by_group(self, ctx: Any, group_id: str) -> KafkaConsumerModel | None:
        try:
            result = await self._session.execute(
                select(KafkaConsumerModel).where(KafkaConsumerModel.group_id == group_id)
            )
            return result.scalars().first()
        except SQLAlchemyError as exc:
            raise ApplicationError(str(exc)) from exc

    async def find_all(self, ctx: Any, limit: int = 100) -> list[KafkaConsumerModel]:
        try:
            result = await self._session.execute(
                select(KafkaConsumerModel)
                .order_by(KafkaConsumerModel.total_lag.desc())
                .limit(limit)
            )
            return list(result.scalars().all())
        except SQLAlchemyError as exc:
            raise ApplicationError(str(exc)) from exc

    async def update_lag(
        self, ctx: Any, consumer_id: uuid.UUID,
        total_lag: int, health: str,
    ) -> None:
        try:
            c = await self._session.get(KafkaConsumerModel, consumer_id)
            if c:
                c.total_lag = total_lag
                c.health = health
                await self._session.flush()
        except SQLAlchemyError as exc:
            raise ApplicationError(str(exc)) from exc
