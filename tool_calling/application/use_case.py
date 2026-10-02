"""tool_calling use cases"""
from __future__ import annotations
import asyncio
import uuid
from typing import Any

import structlog

from tool_calling.application.exceptions import (
    ConflictAppError, ExecutionAppError, NotFoundAppError,
    PermissionAppError, TimeoutAppError, ValidationAppError,
)
from tool_calling.application.utils import json_dumps_safe, json_loads_safe, ms_now
from tool_calling.domain.enums import ToolStatus
from tool_calling.domain.events import (
    PermissionDenied, ToolInvoked, ToolRegistered,
)
from tool_calling.domain.helpers import redact_secrets, validate_arguments
from tool_calling.domain.value_objects import InvocationResult, ToolSpec
from tool_calling.infrastructure.models import ToolDefinitionModel, ToolInvocationModel

log = structlog.get_logger()


class ToolCallingUseCase:
    def __init__(self, tool_repo: Any, registration_repo: Any,
                 invocation_repo: Any, permission_repo: Any, clients: Any,
                 rate_limiter: Any = None, event_bus: Any = None) -> None:
        self._tools = tool_repo
        self._regs = registration_repo
        self._invs = invocation_repo
        self._perms = permission_repo
        self._clients = clients
        self._rate = rate_limiter
        self._bus = event_bus

    async def register_tool(self, ctx: Any, spec: ToolSpec) -> dict[str, Any]:
        existing = await self._tools.find_by_name(ctx, spec.name)
        if existing is not None:
            raise ConflictAppError(f"tool exists: {spec.name}")
        tool = ToolDefinitionModel(
            tenant_id=ctx.tenant_id, name=spec.name,
            description=spec.description,
            parameters_json=json_dumps_safe(spec.parameters_json),
            returns_json=json_dumps_safe(spec.returns_json),
            kind=str(spec.kind), risk_level=str(spec.risk_level),
            visibility=str(spec.visibility),
            timeout_seconds=spec.timeout_seconds)
        saved = await self._tools.save(ctx, tool)
        if self._bus:
            try:
                await self._bus.publish(ToolRegistered(
                    tool_id=saved.id, tenant_id=ctx.tenant_id,
                    name=saved.name, kind=saved.kind))
            except Exception:
                pass
        return {"id": str(saved.id), "name": saved.name,
                "kind": saved.kind, "is_active": saved.is_active}

    async def list_tools(self, ctx: Any, limit: int = 100,
                          offset: int = 0) -> list[dict[str, Any]]:
        rows = await self._tools.find_all(ctx, limit, offset)
        return [
            {"id": str(r.id), "name": r.name, "description": r.description or "",
             "kind": r.kind, "risk_level": r.risk_level,
             "visibility": r.visibility, "timeout_seconds": r.timeout_seconds,
             "is_active": r.is_active}
            for r in rows
        ]

    async def get_tool(self, ctx: Any, tool_id: uuid.UUID) -> dict[str, Any]:
        t = await self._tools.find_by_id(ctx, tool_id)
        if t is None:
            raise NotFoundAppError("tool not found")
        return {"id": str(t.id), "name": t.name,
                "description": t.description or "",
                "parameters_json": json_loads_safe(t.parameters_json, {}),
                "kind": t.kind, "is_active": t.is_active}

    async def delete_tool(self, ctx: Any, tool_id: uuid.UUID) -> bool:
        t = await self._tools.find_by_id(ctx, tool_id)
        if t is None:
            raise NotFoundAppError("tool not found")
        return await self._tools.delete(ctx, tool_id)

    async def invoke(self, ctx: Any, *, tool_name: str,
                     arguments: dict[str, Any], idempotency_key: str = "",
                     role: str = "user") -> InvocationResult:
        tool = await self._tools.find_by_name(ctx, tool_name)
        if tool is None or not tool.is_active:
            raise NotFoundAppError(f"tool not found: {tool_name}")
        perm = await self._perms.check(ctx, tool.id, role)
        if perm is not None and not perm.allowed:
            if self._bus:
                try:
                    await self._bus.publish(PermissionDenied(
                        tool_id=tool.id, tenant_id=ctx.tenant_id,
                        user_id=ctx.user_id or ctx.tenant_id, role=role))
                except Exception:
                    pass
            raise PermissionAppError(
                f"role '{role}' not allowed to invoke {tool_name}")
        schema = json_loads_safe(tool.parameters_json, {})
        errors = validate_arguments(arguments, schema)
        if errors:
            raise ValidationAppError(f"invalid arguments: {'; '.join(errors)}")
        started = ms_now()
        invocation = ToolInvocationModel(
            tenant_id=ctx.tenant_id, user_id=ctx.user_id or ctx.tenant_id,
            tool_id=tool.id, tool_name=tool.name,
            args_json=json_dumps_safe(redact_secrets(arguments)),
            status=ToolStatus.SUCCESS.value,
            idempotency_key=idempotency_key or "")
        try:
            client = self._clients.get(str(tool.kind))
            output = await asyncio.wait_for(
                client.invoke(spec=tool, args=arguments, secrets={},
                              timeout=tool.timeout_seconds),
                timeout=tool.timeout_seconds + 5)
            invocation.result_json = json_dumps_safe(output)
            invocation.status = ToolStatus.SUCCESS.value
        except asyncio.TimeoutError as exc:
            invocation.status = ToolStatus.TIMEOUT.value
            invocation.error_code = "TIMEOUT"
            invocation.error_message = str(exc)[:500]
            invocation.latency_ms = ms_now() - started
            await self._invs.save(ctx, invocation)
            raise TimeoutAppError(f"tool {tool_name} timed out") from exc
        except Exception as exc:
            invocation.status = ToolStatus.ERROR.value
            invocation.error_code = "EXECUTION_ERROR"
            invocation.error_message = str(exc)[:500]
            invocation.latency_ms = ms_now() - started
            await self._invs.save(ctx, invocation)
            raise ExecutionAppError(f"tool {tool_name} failed: {exc}") from exc
        invocation.latency_ms = ms_now() - started
        saved = await self._invs.save(ctx, invocation)
        if self._bus:
            try:
                await self._bus.publish(ToolInvoked(
                    invocation_id=saved.id, tool_id=tool.id,
                    tenant_id=ctx.tenant_id,
                    user_id=ctx.user_id or ctx.tenant_id,
                    status=saved.status, latency_ms=saved.latency_ms))
            except Exception:
                pass
        return InvocationResult(
            invocation_id=str(saved.id), tool_name=tool.name,
            status=saved.status, output=json_loads_safe(saved.result_json, {}),
            latency_ms=saved.latency_ms)

    async def list_invocations(self, ctx: Any, limit: int = 50,
                                offset: int = 0) -> list[dict[str, Any]]:
        rows = await self._invs.list(ctx, limit, offset)
        return [
            {"id": str(r.id), "tool_id": str(r.tool_id),
             "tool_name": r.tool_name or "", "status": r.status,
             "latency_ms": r.latency_ms or 0,
             "created_at": r.created_at.isoformat() if r.created_at else ""}
            for r in rows
        ]
