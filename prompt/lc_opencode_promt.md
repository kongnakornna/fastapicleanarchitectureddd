# lc_opencode_promt.md — Module `langchain` Generator Prompt

## 🎯 Purpose
LangChain chain/agent/memory wrapper + tracing
**Depends on:** `llm`, `tool_calling`

## 📋 Metadata
| Field | Value |
|-------|-------|
| MODULE_NAME | `langchain` |
| PREFIX | `lc` |
| VERSION | `1.0.0` |
| DEPS | `llm`, `tool_calling` |

## 🗄️ Tables
| Table | Purpose |
|-------|---------|
| `lc_chains` | Chain definitions (LCEL / legacy) |
| `lc_agents` | Agent configs (ReAct, OpenAI Tools, Plan-Execute) |
| `lc_memories` | Conversation memory snapshots |
| `lc_runs` | Execution traces |
| `lc_traces` | Step-level trace events |

## 🔤 Enums
- `ChainType`: LCEL, SEQUENTIAL, ROUTER, MAP_REDUCE, REFINE, STUFF
- `AgentType`: REACT, OPENAI_TOOLS, PLAN_EXECUTE, SELF_ASK, REFLEXION
- `MemoryType`: BUFFER, WINDOW, SUMMARY, SUMMARY_BUFFER, VECTOR, KG

## 🔌 Public Port
```python
class LCChainRunnerPort(Protocol):
    async def invoke(self, *, chain_id: uuid.UUID, inputs: dict,
                     ctx: RequestContext) -> dict: ...
    def stream(self, *, chain_id: uuid.UUID, inputs: dict,
               ctx: RequestContext) -> AsyncIterator[dict]: ...
```

## 🌐 Endpoints
```
GET    /api/v1/lc/chains
POST   /api/v1/lc/chains
POST   /api/v1/lc/chains/{id}/invoke
GET    /api/v1/lc/agents
POST   /api/v1/lc/agents
POST   /api/v1/lc/agents/{id}/invoke
GET    /api/v1/lc/runs/{id}
GET    /api/v1/lc/runs/{id}/trace
```

## 📤 Opencode Prompt

```
Generate `create_module_langchain.py` v1.0.0 (SECTION 1..7).

CONSTANTS:
  MODULE_NAME = "langchain"
  PREFIX      = "lc"
  VERSION     = "1.0.0"

DEPENDENCIES:
  from app.modules.llm.application.ports import LLMPort
  from app.modules.tool_calling.application.ports import (
      ToolRegistryPort, ToolInvokerPort)

ENTITIES:
  LCChain(id, tenant_id, name, chain_type, config_json,
          version, is_active, created_at, updated_at)
  LCAgent(id, tenant_id, name, agent_type, tools_json, model,
          max_iterations, config_json, created_at, updated_at)
  LCMemory(id, tenant_id, conversation_id, memory_type,
           snapshot_json, size_bytes, created_at, updated_at)
  LCRun(id, tenant_id, user_id, kind, target_id, input_json,
        output_json, status, latency_ms, tokens_used, cost_usd,
        created_at, updated_at)
  LCTrace(id, run_id, step, kind, payload_json, latency_ms,
          occurred_at)

ENUMS:
  ChainType(str, Enum): LCEL, SEQUENTIAL, ROUTER, MAP_REDUCE, REFINE, STUFF
  AgentType(str, Enum): REACT, OPENAI_TOOLS, PLAN_EXECUTE,
                        SELF_ASK, REFLEXION
  MemoryType(str, Enum): BUFFER, WINDOW, SUMMARY, SUMMARY_BUFFER,
                         VECTOR, KG

VALUE OBJECTS:
  ChainSpec(name, chain_type, config)
  AgentSpec(name, agent_type, tools, model, max_iterations)
  MemorySnapshot(memory_type, payload, size_bytes)

EVENTS:
  ChainInvoked, AgentStepExecuted, MemoryUpdated, RunCompleted

PORTS:
  LCChainRunnerPort (invoke, stream)
  LCAgentRunnerPort (invoke)
  MemoryStorePort (get, set, trim)
  TracerPort (record_step, record_run)

ADAPTERS:
  LCELAdapter, ReActAgentAdapter, OpenAIToolsAgentAdapter,
  ReflexionAdapter, SummaryMemoryAdapter

ENDPOINTS:
  GET  /api/v1/lc/chains
  POST /api/v1/lc/chains
  POST /api/v1/lc/chains/{id}/invoke
  GET  /api/v1/lc/agents
  POST /api/v1/lc/agents
  POST /api/v1/lc/agents/{id}/invoke
  GET  /api/v1/lc/runs/{id}
  GET  /api/v1/lc/runs/{id}/trace

TRACE MODEL:
  - Every chain/agent invocation creates 1 LCRun
  - Every internal step creates 1 LCTrace
  - step = monotonically increasing integer
  - kind = "llm_call" | "tool_call" | "memory_read" | "memory_write"
          | "router_branch" | "retrieval"

SQL:
  Indexes:
    ix_lc_chain_tenant_name UNIQUE
    ix_lc_agent_tenant_name UNIQUE
    ix_lc_memory_conv
    ix_lc_run_tenant_time
    ix_lc_trace_run_step
  Trigger set_updated_at_lc + RLS

Write complete runnable file.
```

## 🧪 Manual Test (10)
1. Create LCEL chain → invoke → result
2. ReAct agent + tools → multi-step trace
3. Memory summary after 10 turns → compressed
4. Trace step-by-step complete
5. Router selects correct branch
6. Map-reduce over 5 docs
7. Reflexion agent retry loop
8. Cross-tenant trace isolation
9. Cost accounting per run
10. SSE stream for LCEL chain

## ✅ Checklist
- [ ] `LCChainRunnerPort` importable
- [ ] Tracing creates step events
- [ ] Memory store pluggable