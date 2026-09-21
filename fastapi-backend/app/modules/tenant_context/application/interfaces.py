"""tenant_context application interfaces — ports (Protocol).

พอร์ตสำหรับ repository / cache / resolver
"""

from typing import Protocol

from ..domain.value_objects import TenantContext


class ITenantContextProvider(Protocol):
    """ITenantContextProvider — พอร์ตจัดการ context."""

    def get(self) -> TenantContext: ...

    def set(self, ctx: TenantContext) -> None: ...

    def clear(self) -> None: ...


class ITenantResolver(Protocol):
    """ITenantResolver — พอร์ตค้นหา tenant จาก identifier."""

    async def resolve(self, identifier: str) -> TenantContext | None: ...


class ITenantCache(Protocol):
    """ITenantCache — พอร์ตแคชข้อมูล tenant."""

    async def get(self, identifier: str) -> TenantContext | None: ...

    async def insert(self, identifier: str, ctx: TenantContext) -> None: ...

    async def delete(self, identifier: str) -> None: ...


__all__ = [
    "ITenantCache",
    "ITenantContextProvider",
    "ITenantResolver",
]
