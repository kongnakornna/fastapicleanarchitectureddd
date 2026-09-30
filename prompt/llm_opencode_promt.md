# llm_opencode_promt.md — Module `llm` Generator Prompt

## 🎯 Purpose
สร้าง `create_module_llm.py` v1.2.1 — Unified LLM Gateway
เป็น **base module** ที่ทุก module อื่นเรียกใช้ผ่าน `LLMPort`

## 📋 Metadata
| Field | Value |
|-------|-------|
| MODULE_NAME | `llm` |
| PREFIX | `llm` |
| VERSION | `1.2.1` |
| LAYER | 5-Intel |
| SCHEMA | public |
| DEPS | *(none — base)* |

## 🗄️ Tables
| Table | Purpose |
|-------|---------|
| `llm_providers` | Provider registry (openai/anthropic/local/azure) |
| `llm_models` | Model registry + cost |
| `llm_conversations` | Conversations |
| `llm_messages` | Messages |
| `llm_usage_logs` | Token/cost usage |

## 🔤 Enums
- `ProviderType`: OPENAI, ANTHROPIC, LOCAL, AZURE
- `MessageRole`: SYSTEM, USER, ASSISTANT, TOOL
- `ConversationStatus`: ACTIVE, ARCHIVED, DELETED
- `FinishReason`: STOP, LENGTH, TOOL_CALLS, CONTENT_FILTER, ERROR

## 💎 Value Objects
- `ChatOptions` (temperature, top_p, max_tokens, stop, tools, tool_choice, stream, seed)
- `ProviderConfig` (name, provider_type, api_key, base_url, timeout)
- `TokenUsage` (input_tokens, output_tokens, total_tokens, cost_usd)

## 📣 Domain Events
`ConversationCreated`, `MessageSent`, `CompletionGenerated`, `ProviderRegistered`, `TokenLimitExceeded`

## 🔌 Public Ports (contract ที่ module อื่นใช้)
```python
class LLMPort(Protocol):
    async def chat(self, *, model: str, messages: list[dict],
                   options: ChatOptions | None = None,
                   conversation_id: uuid.UUID | None = None) -> ChatResult: ...
    def stream(self, *, model: str, messages: list[dict],
               options: ChatOptions | None = None) -> AsyncIterator[Chunk]: ...

@dataclass
class ChatResult:
    content: str
    finish_reason: str
    usage: TokenUsage
    cached: bool
```

## 🌐 Endpoints
```
POST   /api/v1/llm/chat
POST   /api/v1/llm/chat/stream
POST   /api/v1/llm/completions
GET    /api/v1/llm/conversations
POST   /api/v1/llm/conversations
GET    /api/v1/llm/conversations/{id}
GET    /api/v1/llm/providers
GET    /api/v1/llm/models
GET    /api/v1/llm/usage
GET    /api/v1/llm/usage/me
```

## 📤 Opencode Prompt (paste ตรงนี้)

```
Generate `create_module_llm.py` v1.2.1 following the exact structure of
the reference file provided in the conversation context.

CONSTANTS:
  VERSION     = "1.2.1"
  MODULE_NAME = "llm"
  LAYER_NAME  = "5-Intel"
  PREFIX      = "llm"

REQUIREMENTS:
  1. Python 3.10+ (no StrEnum — use `class X(str, Enum)` + __str__)
  2. Force UTF-8 stdout/stderr at module top
  3. SECTION 1: 38 PY_* string constants (full source of generated module)
  4. SECTION 2: SQL_V001 (create), SQL_V002 (seed), SQL_V003 (rollback)
  5. SECTION 3: ALEMBIC_FILE, POSTMAN_JSON, DOCS_README, DOCS_API, DOCS_MANUAL
  6. SECTION 4: PY_FILES, SQL_FILES, DOCS_FILES registries
  7. SECTION 5: log(), write_file(), write_many(), append_if_missing()
  8. SECTION 6: action_create, action_sql, action_alembic, action_swagger,
               action_postman, action_docs, action_update, action_update_env,
               action_activate, action_all
  9. SECTION 7: CLI with argparse, --version, --force, --root
 10. Force newline="\n" when writing files
 11. _check_python_version() returns False if < 3.10
 12. KeyboardInterrupt handler returns 130
 13. Print log symbols: [OK]  [SKIP] [WARN] [ERR]  [INFO]

EXPOSE (for downstream modules):
  - LLMPort Protocol with chat() and stream()
  - ChatResult dataclass
  - ChatOptions value object reusable from other modules

Write the complete runnable file. Do not abbreviate.
```

## 🧪 Manual Test (12 scenarios)
1. `POST /llm/chat` → 200 + content + usage
2. Repeat → `cached=true`
3. Invalid model → 404 NOT_FOUND
4. SSE stream → `data:` chunks + `[DONE]`
5. Client disconnect mid-stream → partial message persisted
6. `POST /llm/conversations` → 201
7. `GET /llm/conversations` → array
8. `GET /llm/conversations/{id}` → detail + messages
9. `GET /llm/providers` → array
10. `GET /llm/models` → array
11. `GET /llm/usage?days=30` → tenant + user
12. RLS: other tenant → empty/404

## ✅ Checklist
- [ ] `python -m py_compile create_module_llm.py` ผ่าน
- [ ] `python create_module_llm.py -v` แสดง version
- [ ] `python create_module_llm.py all llm 5 llm --force` สำเร็จ
- [ ] `/docs` แสดง tag "LLM"
- [ ] SSE format ถูกต้อง
- [ ] Decimal cost serialize เป็น string