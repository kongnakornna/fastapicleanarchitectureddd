"""Money use cases — กรณีการใช้งาน money"""
from __future__ import annotations

import structlog

from ..domain.entities import Money
from ..domain.events import (
    MoneyCreated,
    MoneyDeleted,
    MoneyUpdated,
)
from ..domain.exceptions import DomainError
from .exceptions import (
    DuplicateCodeError,
    StandardException,
    MoneyNotFoundError,
)

log = structlog.get_logger()


class CreateMoneyUseCase:
    """TH: สร้าง money ใหม่ (idempotent) | EN: create (idempotent)"""

    def __init__(self, *, repo, cache, event_bus, idempotency, ctx) -> None:
        self.repo = repo
        self.cache = cache
        self.event_bus = event_bus
        self.idempotency = idempotency
        self.ctx = ctx

    async def execute(
        self, *, code: str, name: str, amount, idempotency_key: str
    ) -> Money:
        log.info("usecase.create.start", code=code, idem=idempotency_key[:8])
        try:
            existing = await self.idempotency.check_or_lock(
                key=idempotency_key,
                scope="money.create",
                payload={"code": code, "name": name, "amount": str(amount)},
                tenant_id=str(self.ctx["tenant_id"]),
            )
            if existing is not None:
                return existing

            if await self.repo.get_by_code(code) is not None:
                raise DuplicateCodeError(code)

            entity = Money.create(
                tenant_id=self.ctx["tenant_id"],
                code=code, name=name, amount=amount,
            )

            saved = await self.repo.save(entity)

            verified = await self.repo.get_by_id(saved.id)
            if verified is None:
                raise StandardException("read-back verification failed")

            await self.cache.invalidate(f"money:{saved.id}")

            await self.idempotency.complete(
                key=idempotency_key, scope="money.create",
                tenant_id=str(self.ctx["tenant_id"]),
                status=201, body={"id": str(saved.id)},
            )

            await self.event_bus.publish(
                MoneyCreated(
                    entity_id=saved.id, tenant_id=saved.tenant_id,
                    code=saved.code, amount=saved.amount.amount,
                    occurred_at=saved.created_at,
                )
            )
            return verified
        except StandardException:
            log.warning("usecase.create.standard_error", code=code)
            raise
        except DomainError as e:
            log.warning("usecase.create.domain_error", code=code, err=str(e))
            raise
        except Exception:
            log.exception("usecase.create.unexpected", code=code)
            raise


class GetMoneyUseCase:
    """TH: ดึง money ตาม id | EN: get by id"""

    def __init__(self, *, repo, cache, ctx) -> None:
        self.repo = repo
        self.cache = cache
        self.ctx = ctx

    async def execute(self, *, entity_id) -> Money:
        log.info("usecase.get.start", entity_id=str(entity_id))
        try:
            cached = await self.cache.get(f"money:{entity_id}")
            if cached is not None:
                return cached

            entity = await self.repo.get_by_id(entity_id)
            if entity is None or entity.is_deleted():
                raise MoneyNotFoundError(entity_id)

            await self.cache.set(f"money:{entity_id}", entity, ttl=300)
            return entity
        except StandardException:
            raise
        except DomainError as e:
            log.warning("usecase.get.domain_error", err=str(e))
            raise
        except Exception:
            log.exception("usecase.get.unexpected", entity_id=str(entity_id))
            raise


class ListMoneyUseCase:
    """TH: list + filter + paginate | EN: list"""

    def __init__(self, *, repo, ctx) -> None:
        self.repo = repo
        self.ctx = ctx

    async def execute(
        self, *, status: str | None, q: str | None, limit: int, offset: int
    ) -> tuple[list[Money], int]:
        log.info("usecase.list.start", status=status, q=q, limit=limit)
        try:
            return await self.repo.list(
                status=status, q=q, limit=limit, offset=offset
            )
        except Exception:
            log.exception("usecase.list.unexpected")
            raise


class UpdateMoneyUseCase:
    """TH: แก้ไข money | EN: update"""

    def __init__(self, *, repo, cache, event_bus, ctx) -> None:
        self.repo = repo
        self.cache = cache
        self.event_bus = event_bus
        self.ctx = ctx

    async def execute(self, *, entity_id, **changes) -> Money:
        log.info("usecase.update.start", entity_id=str(entity_id))
        try:
            entity = await self.repo.get_by_id(entity_id)
            if entity is None or entity.is_deleted():
                raise MoneyNotFoundError(entity_id)

            if "name" in changes and changes["name"] is not None:
                entity.rename(changes["name"])

            saved = await self.repo.save(entity)
            await self.cache.invalidate(f"money:{entity_id}")

            await self.event_bus.publish(
                MoneyUpdated(
                    entity_id=saved.id, tenant_id=saved.tenant_id,
                    changes=changes, occurred_at=saved.updated_at,
                )
            )
            return saved
        except StandardException:
            raise
        except DomainError as e:
            log.warning("usecase.update.domain_error", err=str(e))
            raise
        except Exception:
            log.exception("usecase.update.unexpected", entity_id=str(entity_id))
            raise


class DeleteMoneyUseCase:
    """TH: ลบ money (soft) | EN: soft delete"""

    def __init__(self, *, repo, cache, event_bus, ctx) -> None:
        self.repo = repo
        self.cache = cache
        self.event_bus = event_bus
        self.ctx = ctx

    async def execute(self, *, entity_id) -> None:
        log.info("usecase.delete.start", entity_id=str(entity_id))
        try:
            entity = await self.repo.get_by_id(entity_id)
            if entity is None or entity.is_deleted():
                raise MoneyNotFoundError(entity_id)

            entity.soft_delete()
            await self.repo.save(entity)
            await self.cache.invalidate(f"money:{entity_id}")

            await self.event_bus.publish(
                MoneyDeleted(
                    entity_id=entity.id, tenant_id=entity.tenant_id,
                    deleted_at=entity.deleted_at,
                )
            )
        except StandardException:
            raise
        except DomainError as e:
            log.warning("usecase.delete.domain_error", err=str(e))
            raise
        except Exception:
            log.exception("usecase.delete.unexpected", entity_id=str(entity_id))
            raise