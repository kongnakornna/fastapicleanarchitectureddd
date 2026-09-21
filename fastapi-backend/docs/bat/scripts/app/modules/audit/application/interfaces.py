"""
Audit Application Interfaces — interface ของ application layer
Audit Application Interfaces — protocols for audit application layer
"""

from __future__ import annotations

from typing import Protocol

from audit.domain.entities import AuditLog


class IAuditRepository(Protocol):
    """Audit repository interface — interface repository audit (append-only)"""

    async def append(self, log: AuditLog) -> AuditLog:
        """Append audit log — เพิ่มบันทึก audit (append-only, no update/delete)"""
        ...

    async def get_by_id(self, id: str) -> AuditLog | None:
        """Get audit log by id — ดึงบันทึก audit ตาม id"""
        ...

    async def query(
        self, filters: dict, page: int, limit: int
    ) -> tuple[list[AuditLog], int]:
        """Query audit logs with filters — ค้นหาบันทึก audit พร้อม filter"""
        ...


class IAuditCache(Protocol):
    """Audit cache interface — interface cache audit (read-through, never raises)"""

    async def get(self, id: str) -> AuditLog | None:
        """Get from cache — ดึงจาก cache"""
        ...

    async def insert(self, id: str, log: AuditLog) -> None:
        """Insert into cache — ใส่เข้า cache"""
        ...

    async def invalidate(self, id: str) -> None:
        """Invalidate cache entry — ลบ entry ใน cache"""
        ...


class IAuditPublisher(Protocol):
    """Audit publisher interface — interface publisher audit (Kafka)"""

    async def publish(self, log: AuditLog) -> None:
        """Publish audit event — เผยแพร่ event audit"""
        ...


class IAuditEventBus(Protocol):
    """Internal event bus — event bus ภายใน"""

    async def publish(self, event_name: str, payload: object) -> None:
        """Publish domain event — เผยแพร่ domain event"""
        ...
