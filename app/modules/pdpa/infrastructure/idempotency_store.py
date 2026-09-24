"""pdpa idempotency store — SQLAlchemy-backed implementation"""
from __future__ import annotations
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from app.core.logging import logger
from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.pdpa.application.exceptions import (
    ApplicationError, IdempotencyConflictError, IdempotencyMismatchError,
)
from app.modules.pdpa.application.interfaces import (
    IdempotencyStore, RequestContext,
)
from app.modules.pdpa.application.mappers import idempotency_to_entity
from app.modules.pdpa.domain.enums import IdempotencyStatus
from app.modules.pdpa.domain.idempotency import (
    IdempotencyRecord, compute_request_hash,
)
from app.modules.pdpa.infrastructure.models import IdempotencyKeyModel


class IdempotencyStoreError(ApplicationError):
    """TH: idempotency ผิดพลาด | EN: idempotency failure"""


class SQLAlchemyIdempotencyStore(IdempotencyStore):
    """
    TH: เก็บ idempotency key ใน PostgreSQL (public.pdpa_idempotency_keys)
    EN: Persists idempotency keys in PostgreSQL (public.pdpa_idempotency_keys)

    Semantics:
      * check_or_lock → INSERT ... ON CONFLICT DO NOTHING then re-SELECT
      * complete      → UPDATE ... WHERE status='IN_PROGRESS'
      * fail          → DELETE row so client can retry
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ───────────────────────────────────────────────────────────
    async def check_or_lock(
        self,
        ctx: RequestContext,
        key: str,
        scope: str,
        method: str,
        path: str,
        payload: dict[str, Any],
        ttl_hours: int = 24,
    ) -> dict[str, Any] | None:
        request_hash = compute_request_hash(payload)
        try:
            # 1. Try to claim the key
            record = IdempotencyRecord.start(
                tenant_id=ctx.tenant_id,
                user_id=ctx.user_id,
                idempotency_key=key,
                request_method=method,
                request_path=path,
                request_hash=request_hash,
                ttl_hours=ttl_hours,
            )
            model = IdempotencyKeyModel(
                id=record.id,
                tenant_id=record.tenant_id,
                user_id=record.user_id,
                idempotency_key=record.idempotency_key,
                request_method=record.request_method,
                request_path=record.request_path,
                request_hash=record.request_hash,
                status=record.status.value,
                response_status=None,
                response_body=None,
                created_at=record.created_at,
                updated_at=record.updated_at,
                expires_at=record.expires_at,
            )
            self._session.add(model)
            try:
                await self._session.flush()
                # New row inserted → this is the first execution
                logger.info("idempotency.locked", key=key, scope=scope)
                return None
            except IntegrityError:
                await self._session.rollback()
                # fall through to read existing row

            # 2. Row already existed — read it
            existing = await self._load(ctx, key)
            if existing is None:
                # Lost the race and the other txn rolled back — retry once
                logger.warning("idempotency.race_retry", key=key)
                return await self.check_or_lock(
                    ctx, key, scope, method, path, payload, ttl_hours,
                )

            # 3. Expired → delete and retry
            if existing.is_expired():
                await self._delete(ctx, key)
                return await self.check_or_lock(
                    ctx, key, scope, method, path, payload, ttl_hours,
                )

            # 4. Payload mismatch
            if not existing.matches(request_hash):
                raise IdempotencyMismatchError(
                    f"idempotency_key {key} reused with different payload"
                )

            # 5. Status routing
            if existing.status == IdempotencyStatus.COMPLETED:
                logger.info("idempotency.replay", key=key, scope=scope)
                return existing.response_body or {}

            if existing.status == IdempotencyStatus.IN_PROGRESS:
                raise IdempotencyConflictError(
                    f"request with key {key} is already being processed"
                )

            # FAILED → treat as fresh
            await self._delete(ctx, key)
            return await self.check_or_lock(
                ctx, key, scope, method, path, payload, ttl_hours,
            )

        except ApplicationError:
            raise
        except Exception as e:
            logger.exception("idempotency.check_or_lock.failed", key=key)
            raise IdempotencyStoreError(str(e)) from e

    # ───────────────────────────────────────────────────────────
    async def complete(
        self,
        ctx: RequestContext,
        key: str,
        scope: str,
        response_status: int,
        response_body: dict[str, Any],
    ) -> None:
        try:
            stmt = (
                update(IdempotencyKeyModel)
                .where(
                    IdempotencyKeyModel.tenant_id == ctx.tenant_id,
                    IdempotencyKeyModel.idempotency_key == key,
                )
                .values(
                    status=IdempotencyStatus.COMPLETED.value,
                    response_status=response_status,
                    response_body=response_body,
                    updated_at=datetime.now(UTC),
                )
            )
            await self._session.execute(stmt)
            await self._session.flush()
            logger.info("idempotency.completed", key=key, scope=scope)
        except Exception as e:
            logger.exception("idempotency.complete.failed", key=key)
            raise IdempotencyStoreError(str(e)) from e

    # ───────────────────────────────────────────────────────────
    async def fail(
        self,
        ctx: RequestContext,
        key: str,
        scope: str,
    ) -> None:
        try:
            await self._delete(ctx, key)
            logger.info("idempotency.failed", key=key, scope=scope)
        except Exception as e:
            logger.exception("idempotency.fail.failed", key=key)
            raise IdempotencyStoreError(str(e)) from e

    # ───────────────────────────────────────────────────────────
    async def _load(
        self, ctx: RequestContext, key: str,
    ) -> IdempotencyRecord | None:
        stmt = select(IdempotencyKeyModel).where(
            IdempotencyKeyModel.tenant_id == ctx.tenant_id,
            IdempotencyKeyModel.idempotency_key == key,
        )
        row = (await self._session.execute(stmt)).scalar_one_or_none()
        return idempotency_to_entity(row) if row else None

    async def _delete(self, ctx: RequestContext, key: str) -> None:
        stmt = delete(IdempotencyKeyModel).where(
            IdempotencyKeyModel.tenant_id == ctx.tenant_id,
            IdempotencyKeyModel.idempotency_key == key,
        )
        await self._session.execute(stmt)
        await self._session.flush()
