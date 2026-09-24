"""app.shared.context — RequestContext ที่ทุก module ใช้ร่วม

TH: Context ของคำขอ — ใช้ร่วมทุก module (llm, embeddings, rag, ...)
EN: Request context — shared across all modules

Design notes:
  • frozen dataclass → immutable, thread-safe, hashable
  • tenant_id required, อื่น ๆ optional
  • รองรับ tracing (request_id, trace_id) และ RBAC (roles, scopes)
  • Helper methods: effective_user(), with_user(), with_tenant(), to_dict()
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field, replace
from typing import Any, Optional


# ═══════════════════════════════════════════════════════════════
#  System tenant — ใช้สำหรับ internal calls / background jobs
# ═══════════════════════════════════════════════════════════════
SYSTEM_TENANT_ID = uuid.UUID(int=0)
SYSTEM_USER_ID = uuid.UUID(int=0)


# ═══════════════════════════════════════════════════════════════
#  RequestContext
# ═══════════════════════════════════════════════════════════════
@dataclass(frozen=True)
class RequestContext:
    """TH: tenant/user context | EN: tenant/user request context

    Attributes:
        tenant_id:   TH: ID ของ tenant (required) | EN: tenant UUID (required)
        user_id:     TH: ID ของ user (optional)  | EN: user UUID (optional)
        request_id:  TH: ID ของคำขอ (สำหรับ tracing) | EN: request id
        trace_id:    TH: distributed trace id | EN: trace id
        roles:       TH: roles ของ user (RBAC) | EN: user roles
        scopes:      TH: scopes (OAuth-like) | EN: permission scopes
        metadata:    TH: ข้อมูลเพิ่มเติม | EN: extra metadata
    """

    tenant_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    request_id: Optional[str] = None
    trace_id: Optional[str] = None
    roles: tuple[str, ...] = ()
    scopes: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    # ─── Core helpers ────────────────────────────────────────

    def effective_user(self) -> uuid.UUID:
        """TH: fallback เป็น tenant ถ้าไม่มี user | EN: fallback to tenant"""
        return self.user_id or self.tenant_id

    def has_user(self) -> bool:
        """TH: มี user_id หรือยัง | EN: has explicit user"""
        return self.user_id is not None

    def is_system(self) -> bool:
        """TH: เป็น system context หรือไม่ | EN: system context?"""
        return self.tenant_id == SYSTEM_TENANT_ID

    # ─── Immutable mutators ──────────────────────────────────

    def with_user(self, user_id: Optional[uuid.UUID]) -> "RequestContext":
        """TH: คืน context ใหม่พร้อม user_id | EN: clone with user_id"""
        return replace(self, user_id=user_id)

    def with_tenant(self, tenant_id: uuid.UUID) -> "RequestContext":
        """TH: คืน context ใหม่พร้อม tenant_id | EN: clone with tenant_id"""
        return replace(self, tenant_id=tenant_id)

    def with_request_id(self, request_id: str) -> "RequestContext":
        """TH: คืน context ใหม่พร้อม request_id | EN: clone with request_id"""
        return replace(self, request_id=request_id)

    def with_trace_id(self, trace_id: str) -> "RequestContext":
        """TH: คืน context ใหม่พร้อม trace_id | EN: clone with trace_id"""
        return replace(self, trace_id=trace_id)

    def with_roles(self, roles: list[str] | tuple[str, ...]) -> "RequestContext":
        """TH: คืน context ใหม่พร้อม roles | EN: clone with roles"""
        return replace(self, roles=tuple(roles))

    def with_scopes(self, scopes: list[str] | tuple[str, ...]) -> "RequestContext":
        """TH: คืน context ใหม่พร้อม scopes | EN: clone with scopes"""
        return replace(self, scopes=tuple(scopes))

    def with_metadata(self, **kwargs: Any) -> "RequestContext":
        """TH: คืน context ใหม่พร้อม metadata เพิ่ม | EN: clone with extra metadata"""
        merged = {**self.metadata, **kwargs}
        return replace(self, metadata=merged)

    # ─── RBAC helpers ────────────────────────────────────────

    def has_role(self, role: str) -> bool:
        """TH: ตรวจ role | EN: check role"""
        return role in self.roles

    def has_scope(self, scope: str) -> bool:
        """TH: ตรวจ scope | EN: check scope"""
        return scope in self.scopes

    def has_any_role(self, *roles: str) -> bool:
        """TH: ตรวจว่ามี role ใดก็ได้ | EN: any role match"""
        return any(r in self.roles for r in roles)

    # ─── Serialization ───────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        """TH: แปลงเป็น dict (สำหรับ log) | EN: serialize for logging"""
        return {
            "tenant_id": str(self.tenant_id),
            "user_id": str(self.user_id) if self.user_id else None,
            "request_id": self.request_id,
            "trace_id": self.trace_id,
            "roles": list(self.roles),
            "scopes": list(self.scopes),
            "metadata": dict(self.metadata) if self.metadata else {},
        }

    def __str__(self) -> str:
        """TH: string ที่อ่านง่าย | EN: human-readable string"""
        user = f" user={self.user_id}" if self.user_id else " user=∅"
        req = f" req={self.request_id}" if self.request_id else ""
        return f"RequestContext(tenant={self.tenant_id}{user}{req})"


# ═══════════════════════════════════════════════════════════════
#  Factories — สำหรับสร้าง context ในสถานการณ์ต่าง ๆ
# ═══════════════════════════════════════════════════════════════
def system_context(
    *,
    request_id: Optional[str] = None,
    trace_id: Optional[str] = None,
    **metadata: Any,
) -> RequestContext:
    """TH: context สำหรับ internal / background jobs
    | EN: system context for internal calls"""
    return RequestContext(
        tenant_id=SYSTEM_TENANT_ID,
        user_id=SYSTEM_USER_ID,
        request_id=request_id,
        trace_id=trace_id,
        roles=("system",),
        metadata=dict(metadata),
    )


def anonymous_context(tenant_id: uuid.UUID) -> RequestContext:
    """TH: context ที่ไม่มี user (anonymous)
    | EN: anonymous context (no user)"""
    return RequestContext(tenant_id=tenant_id)


def from_headers(
    *,
    x_tenant_id: Optional[str] = None,
    x_user_id: Optional[str] = None,
    x_request_id: Optional[str] = None,
    x_trace_id: Optional[str] = None,
    x_roles: Optional[str] = None,
    x_scopes: Optional[str] = None,
) -> RequestContext:
    """TH: สร้าง context จาก HTTP headers
    | EN: build context from HTTP headers

    Raises:
        ValueError: ถ้า X-Tenant-Id หายหรือไม่ใช่ UUID
    """
    if not x_tenant_id:
        raise ValueError("X-Tenant-Id required")

    try:
        tenant_id = uuid.UUID(x_tenant_id)
    except (ValueError, AttributeError) as exc:
        raise ValueError(f"invalid tenant_id: {x_tenant_id}") from exc

    user_id: Optional[uuid.UUID] = None
    if x_user_id:
        try:
            user_id = uuid.UUID(x_user_id)
        except (ValueError, AttributeError):
            user_id = None

    roles = tuple(
        r.strip() for r in (x_roles or "").split(",") if r.strip()
    )
    scopes = tuple(
        s.strip() for s in (x_scopes or "").split(",") if s.strip()
    )

    return RequestContext(
        tenant_id=tenant_id,
        user_id=user_id,
        request_id=x_request_id,
        trace_id=x_trace_id,
        roles=roles,
        scopes=scopes,
    )


# ═══════════════════════════════════════════════════════════════
#  Public API
# ═══════════════════════════════════════════════════════════════
__all__ = [
    "RequestContext",
    "SYSTEM_TENANT_ID",
    "SYSTEM_USER_ID",
    "system_context",
    "anonymous_context",
    "from_headers",
    "anonymous_context",
    "system_context",
]
