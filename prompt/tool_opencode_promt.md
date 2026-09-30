# tool_opencode_promt.md — Module `tool_calling` Generator Prompt

## 🎯 Purpose
Function/tool registry + invoke + permission + sandbox (ReAct loop)
**Depends on:** `llm`

## 📋 Metadata
| Field | Value |
|-------|-------|
| MODULE_NAME | `tool_calling` |
| PREFIX | `tool` |
| VERSION | `1.0.0` |
| DEPS | `llm` |

## 🗄️ Tables
| Table | Purpose |
|-------|---------|
| `tool_definitions` | JSON-schema tool specs |
| `tool_registrations` | Per-tenant enabled tools |
| `tool_invocations` | Invocation logs |
| `tool_permissions` | RBAC (role → tool) |
| `tool_secrets` | Encrypted secrets |

## 🔤 Enums
- `ToolStatus`: SUCCESS, ERROR, TIMEOUT, DENIED, RATE_LIMITED
- `ToolKind`: HTTP, PYTHON, SQL, SHELL, MCP, OPENAPI

## 💎 Value Objects
- `ToolSpec(name, description, parameters_json, returns_json)`
- `InvocationRequest(tool_id, args, idempotency_key)`
- `InvocationResult(status, output, error, latency_ms)`

## 📣 Domain Events
`ToolRegistered`, `ToolInvoked`, `ToolFailed`, `PermissionDenied`

## 🔌 Public Port
```python
class ToolRegistryPort(Protocol):
    async def register(self, spec: ToolSpec) -> uuid.UUID: ...
    async def list(self, *, tenant_id: uuid.UUID) -> list[ToolSpec]: ...
    def get_client(self, name: str) -> ToolClient: ...

class ToolInvokerPort(Protocol):
    async def invoke(self, *, name: str, args: dict,
                     ctx: RequestContext) -> InvocationResult: ...
```

## 🌐 Endpoints
```
GET    /api/v1/tools
POST   /api/v1/tools
GET    /api/v1/tools/{id}
DELETE /api/v1/tools/{id}
POST   /api/v1/tools/{id}/invoke
GET    /api/v1/tools/invocations
```

## 📤 Opencode Prompt

```
Generate `create_module_tool_calling.py` v1.0.0 (SECTION 1..7).

CONSTANTS:
  MODULE_NAME = "tool_calling"
  PREFIX      = "tool"
  VERSION     = "1.0.0"

DEPENDENCY:
  from app.modules.llm.application.ports import LLMPort   # for ReAct loop

ENTITIES:
  ToolDefinition(id, tenant_id, name, description, parameters_json,
                 returns_json, version, kind, is_active,
                 created_at, updated_at)
  ToolRegistration(id, tenant_id, tool_id, enabled, rate_limit_per_min,
                   scopes_json, created_at, updated_at)
  ToolInvocation(id, tenant_id, user_id, tool_id, args_json, result_json,
                 status, latency_ms, error_code, tokens_used,
                 created_at, updated_at)
  ToolPermission(id, tenant_id, tool_id, role, allowed,
                 created_at, updated_at)
  ToolSecret(id, tenant_id, tool_id, key, value_encrypted,
             created_at, updated_at)

ENUMS:
  ToolStatus(str, Enum): SUCCESS, ERROR, TIMEOUT, DENIED, RATE_LIMITED
  ToolKind(str, Enum): HTTP, PYTHON, SQL, SHELL, MCP, OPENAPI

VALUE OBJECTS:
  ToolSpec(name, description, parameters_json, returns_json, kind)
  InvocationRequest(tool_id, args, idempotency_key | None)
  InvocationResult(status, output, error, latency_ms)

EVENTS:
  ToolRegistered, ToolInvoked, ToolFailed, PermissionDenied

PORTS:
  ToolRegistryPort (register, list, get_client)
  ToolInvokerPort (invoke)
  ToolClient Protocol (invoke(args) -> dict)

ADAPTERS:
  HttpToolClient, PythonToolClient, SqlToolClient, ShellToolClient,
  McpToolClient, OpenApiToolClient

USE CASES:
  RegisterToolUseCase, ListToolsUseCase, InvokeToolUseCase,
  ReActLoopUseCase (uses LLMPort for tool-call orchestration)

ENDPOINTS:
  GET    /api/v1/tools
  POST   /api/v1/tools
  GET    /api/v1/tools/{id}
  DELETE /api/v1/tools/{id}
  POST   /api/v1/tools/{id}/invoke
  GET    /api/v1/tools/invocations

SQL:
  Indexes:
    ix_tool_def_tenant_name (tenant_id, name) UNIQUE
    ix_tool_reg_tenant_tool
    ix_tool_inv_tenant_time
    ix_tool_perm_tenant_role
  Secrets encrypted via AES-GCM (key from env TOOL_SECRET_KEY)
  Trigger set_updated_at_tool + RLS

REACT LOOP (LLMPort integration):
  1. Call LLMPort.chat(tools=[tool_specs...])
  2. If response has tool_calls → invoke tools in parallel
  3. Append tool results → loop until no more tool_calls
  4. Max iterations = 10

Write complete runnable file.
```

## 🧪 Manual Test (10)
1. Register `get_weather` (HTTP) → 201
2. Invoke valid args → 200 + result
3. Invalid args → 422
4. Rate limit → 429
5. Permission denied → 403
6. ReAct auto-invoke via LLM
7. Timeout → status=TIMEOUT
8. Secret injection works
9. Invocation log stores args+result
10. Cross-tenant isolation

## ✅ Checklist
- [ ] `ToolRegistryPort` importable
- [ ] `ReActLoopUseCase` uses `LLMPort`
- [ ] Secrets encrypted