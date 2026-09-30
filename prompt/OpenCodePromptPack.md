📦 OpenCode Prompt Pack — 10 Modules Working Together
สร้างไฟล์ prompt ทั้งหมด 10 ไฟล์ — แต่ละไฟล์เป็น prompt แบบครบวงจรที่ paste ใส่ opencode แล้วได้ create_module_<name>.py ออกมา
ทุก module ออกแบบให้ ทำงานร่วมกัน ผ่าน contracts ที่ระบุไว้ในแต่ละไฟล์

⚠️ หมายเหตุ: รายการที่ 9 และ 10 ในคำขอเป็น vdb_opencode_promt.md ซ้ำกัน
ในชุดนี้ผมสร้าง hs_opencode_promt.md (Hybrid Search) แทนรายการที่ 10 ตามรายการ module ต้นฉบับ

🗺️ Master Index & Dependency Map
text
DEPENDENCY ORDER (สร้างตามลำดับ):

  ┌─────────────────────────────────────────────────────────┐
  │  LAYER 0 — BASE (no deps)                               │
  │  ├── 1. llm_opencode_promt.md       (create_module_llm) │
  │  └── 2. emb_opencode_promt.md       (create_module_emb) │
  └─────────────────────────────────────────────────────────┘
                          │
  ┌───────────────────────▼─────────────────────────────────┐
  │  LAYER 1 — INDEXING / TOOLS                             │
  │  ├── 3. vdb_opencode_promt.md       (vector_db)         │
  │  ├── 4. tool_opencode_promt.md      (tool_calling)      │
  │  └── 5. so_opencode_promt.md        (structured_out)    │
  └─────────────────────────────────────────────────────────┘
                          │
  ┌───────────────────────▼─────────────────────────────────┐
  │  LAYER 2 — RETRIEVAL / ORCHESTRATION                    │
  │  ├── 6. hs_opencode_promt.md        (hybrid_search)     │
  │  ├── 7. lc_opencode_promt.md        (langchain)         │
  │  └── 8. li_opencode_promt.md        (llamaindex)        │
  └─────────────────────────────────────────────────────────┘
                          │
  ┌───────────────────────▼─────────────────────────────────┐
  │  LAYER 3 — APPLICATION                                  │
  │  ├── 9. rag_opencode_promt.md       (rag)               │
  │  └── 10. eval_opencode_promt.md     (ai_evaluation)     │
  └─────────────────────────────────────────────────────────┘


# 📦 OpenCode Prompt Pack — 10 Modules Working Together

> สร้างไฟล์ prompt ทั้งหมด 10 ไฟล์ — แต่ละไฟล์เป็น prompt แบบครบวงจรที่ paste ใส่ opencode แล้วได้ `create_module_<name>.py` ออกมา
> ทุก module ออกแบบให้ **ทำงานร่วมกัน** ผ่าน contracts ที่ระบุไว้ในแต่ละไฟล์

> ⚠️ หมายเหตุ: รายการที่ 9 และ 10 ในคำขอเป็น `vdb_opencode_promt.md` ซ้ำกัน
> ในชุดนี้ผมสร้าง **`hs_opencode_promt.md` (Hybrid Search)** แทนรายการที่ 10 ตามรายการ module ต้นฉบับ

---

## 🗺️ Master Index & Dependency Map

```
DEPENDENCY ORDER (สร้างตามลำดับ):

  ┌─────────────────────────────────────────────────────────┐
  │  LAYER 0 — BASE (no deps)                               │
  │  ├── 1. llm_opencode_promt.md       (create_module_llm) │
  │  └── 2. emb_opencode_promt.md       (create_module_emb) │
  └─────────────────────────────────────────────────────────┘
                          │
  ┌───────────────────────▼─────────────────────────────────┐
  │  LAYER 1 — INDEXING / TOOLS                             │
  │  ├── 3. vdb_opencode_promt.md       (vector_db)         │
  │  ├── 4. tool_opencode_promt.md      (tool_calling)      │
  │  └── 5. so_opencode_promt.md        (structured_out)    │
  └─────────────────────────────────────────────────────────┘
                          │
  ┌───────────────────────▼─────────────────────────────────┐
  │  LAYER 2 — RETRIEVAL / ORCHESTRATION                    │
  │  ├── 6. hs_opencode_promt.md        (hybrid_search)     │
  │  ├── 7. lc_opencode_promt.md        (langchain)         │
  │  └── 8. li_opencode_promt.md        (llamaindex)        │
  └─────────────────────────────────────────────────────────┘
                          │
  ┌───────────────────────▼─────────────────────────────────┐
  │  LAYER 3 — APPLICATION                                  │
  │  ├── 9. rag_opencode_promt.md       (rag)               │
  │  └── 10. eval_opencode_promt.md     (ai_evaluation)     │
  └─────────────────────────────────────────────────────────┘
```

### Integration Contracts (สรุป)

| Module | Depends on | Exposes |
|--------|-----------|---------|
| `llm` | — | `LLMUseCase.chat()`, `chat_stream()`, `LLMPort` |
| `emb` | — | `EmbeddingPort.embed()`, `embed_batch()` |
| `vdb` | `emb` | `VectorStorePort.upsert()`, `query()` |
| `tool` | `llm` | `ToolRegistry`, `ToolInvoker` |
| `so` | `llm` | `SchemaGenerator.generate()` |
| `hs` | `emb`, `vdb` | `HybridRetriever.search()` |
| `lc` | `llm`, `tool` | `LCChainRunner.invoke()` |
| `li` | `llm`, `emb`, `vdb` | `LIIndexPort.query()` |
| `rag` | `llm`, `emb`, `vdb`, `hs` | `RAGPipeline.answer()` |
| `eval` | `llm`, `rag` | `EvalRunner.run()` |

### Shared Conventions (ทุก module ใช้ร่วมกัน)

```yaml
schema: public
layer: 5-Intel
python: ">=3.10"
db: PostgreSQL 16
cache: Redis 7
id_strategy: uuid + gen_random_uuid()
timestamps: timestamptz(6) + trigger set_updated_at_<module>()
tenant_column: tenant_id uuid NOT NULL
rls_policy: USING (tenant_id = current_setting('app.current_tenant', true)::uuid)
headers:
  - X-Tenant-Id (required)
  - X-User-Id (optional)
  - Idempotency-Key (mutating)
error_codes:
  - DOMAIN_ERROR        → 400
  - NOT_FOUND           → 404
  - VALIDATION_ERROR    → 422
  - CONFLICT            → 409
  - LIMIT_EXCEEDED      → 402
  - RATE_LIMITED        → 429
  - PROVIDER_ERROR      → 502
  - DB_ERROR            → 500
  - INTERNAL_ERROR      → 500
retry: { max: 3, backoff: [1, 2, 4] }
cache_default_ttl: 3600
rate_limit_default: 60/min/user
```

---

# 1. `llm_opencode_promt.md`

````markdown
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
````

---

# 2. `emb_opencode_promt.md`

````markdown
# emb_opencode_promt.md — Module `embeddings` Generator Prompt

## 🎯 Purpose
สร้าง `create_module_embeddings.py` — text → vector embedding + caching + batching
เป็น **base module** ที่ RAG / VDB / Hybrid Search / LlamaIndex ใช้

## 📋 Metadata
| Field | Value |
|-------|-------|
| MODULE_NAME | `embeddings` |
| PREFIX | `emb` |
| VERSION | `1.0.0` |
| LAYER | 5-Intel |
| SCHEMA | public |
| DEPS | *(none — base)* |

## 🗄️ Tables
| Table | Purpose |
|-------|---------|
| `emb_providers` | Provider registry (OpenAI/Cohere/Voyage/HF/BGE/local) |
| `emb_models` | Model registry (dimension, cost, normalize) |
| `emb_vectors` | Stored vectors + source hash |
| `emb_batches` | Async batch jobs |
| `emb_cache` | Hash → vector cache (Redis-mirrored) |

## 🔤 Enums
- `EmbeddingProviderType`: OPENAI, COHERE, VOYAGE, LOCAL, HUGGINGFACE, BGE
- `BatchStatus`: PENDING, RUNNING, DONE, FAILED, CANCELLED
- `DistanceMetric`: COSINE, L2, IP

## 💎 Value Objects
- `EmbeddingRequest(model, input, normalize, dimensions)`
- `EmbeddingResult(vector, dimension, tokens, cached)`
- `BatchConfig(batch_size, max_concurrency, retry)`

## 📣 Domain Events
`EmbeddingCreated`, `BatchCompleted`, `BatchFailed`, `CacheHit`, `CacheMiss`

## 🔌 Public Port (contract ที่ module อื่นใช้)
```python
class EmbeddingPort(Protocol):
    async def embed(self, *, model: str, texts: list[str],
                    normalize: bool = True) -> list[EmbeddingResult]: ...
    async def embed_one(self, *, model: str, text: str,
                        normalize: bool = True) -> EmbeddingResult: ...
```

## 🌐 Endpoints
```
POST   /api/v1/embeddings
POST   /api/v1/embeddings/batch
GET    /api/v1/embeddings/models
GET    /api/v1/embeddings/usage
```

## 📤 Opencode Prompt

```
Generate `create_module_embeddings.py` v1.0.0 following the exact structure
of `create_module_llm.py` (SECTION 1..7).

CONSTANTS:
  VERSION     = "1.0.0"
  MODULE_NAME = "embeddings"
  LAYER_NAME  = "5-Intel"
  PREFIX      = "emb"

ENTITIES:
  EmbProvider(id, tenant_id, name, provider_type, api_key_encrypted,
              base_url, timeout_seconds, priority, is_active,
              created_at, updated_at)
  EmbModel(id, tenant_id, provider_id, name, dimension, max_tokens,
           cost_per_1k_tokens, normalize, is_active, created_at, updated_at)
  EmbVector(id, tenant_id, model_id, source_hash, source_text,
            vector_json, dimension, metadata_json, created_at, updated_at)
  EmbBatch(id, tenant_id, user_id, model_id, total, completed, failed,
           status, started_at, finished_at, created_at, updated_at)
  EmbCache(id, tenant_id, model_id, hash, vector_json, hits,
           expires_at, created_at, updated_at)

ENUMS:
  EmbeddingProviderType(str, Enum): OPENAI, COHERE, VOYAGE, LOCAL,
                                    HUGGINGFACE, BGE
  BatchStatus(str, Enum): PENDING, RUNNING, DONE, FAILED, CANCELLED
  DistanceMetric(str, Enum): COSINE, L2, IP

VALUE OBJECTS:
  EmbeddingRequest(model, input: list[str], normalize, dimensions: int | None)
  EmbeddingResult(vector: list[float], dimension: int, tokens: int, cached: bool)
  BatchConfig(batch_size, max_concurrency, retry)

EVENTS:
  EmbeddingCreated, BatchCompleted, BatchFailed, CacheHit, CacheMiss

PORTS:
  EmbeddingPort (embed, embed_one)
  EmbeddingProviderClient Protocol (OpenAIEmbeddingClient, CohereEmbeddingClient,
                                     LocalEmbeddingClient)

REPOSITORIES:
  EmbProviderRepository, EmbModelRepository, EmbVectorRepository,
  EmbBatchRepository, EmbCacheRepository

ENDPOINTS:
  POST /api/v1/embeddings
  POST /api/v1/embeddings/batch
  GET  /api/v1/embeddings/models
  GET  /api/v1/embeddings/usage

SQL:
  Indexes:
    ix_emb_provider_tenant
    ix_emb_model_tenant
    ix_emb_vec_tenant_model
    ix_emb_vec_hash (tenant_id, model_id, source_hash) UNIQUE
    ix_emb_batch_tenant_status
    ix_emb_cache_hash (tenant_id, model_id, hash) UNIQUE
  Trigger set_updated_at_emb on all tables
  RLS policy on all tables

CACHE STRATEGY:
  - Redis key: emb:cache:{tenant}:{model}:{sha256(text)}
  - TTL 86400
  - Never-raise (fail-open)

RETRY: max=3, backoff=[1, 2, 4] for provider calls

Write complete runnable file. No abbreviations.
```

## 🧪 Manual Test (12)
1. Embed "hello" → dim matches model
2. Embed same text → `cached=true`
3. Batch 1000 texts → progress
4. Invalid model → 404
5. Dimension mismatch → 422
6. `normalize=true` → ‖v‖=1.0
7. Rate limit → 429
8. Cross-tenant cache isolation
9. Cost log per 1k tokens
10. Fallback to local HF model
11. Concurrent batches don't collide
12. Empty input → `[]` (no error)

## ✅ Checklist
- [ ] `EmbeddingPort` importable
- [ ] Redis cache fail-open
- [ ] `vector_json` decodes to `list[float]`
````

---

# 3. `vdb_opencode_promt.md`

````markdown
# vdb_opencode_promt.md — Module `vector_db` Generator Prompt

## 🎯 Purpose
Vector store abstraction (pgvector / Qdrant / Weaviate / Pinecone / Chroma)
**Depends on:** `embeddings`

## 📋 Metadata
| Field | Value |
|-------|-------|
| MODULE_NAME | `vector_db` |
| PREFIX | `vdb` |
| VERSION | `1.0.0` |
| DEPS | `embeddings` |

## 🗄️ Tables
| Table | Purpose |
|-------|---------|
| `vdb_collections` | Logical collections |
| `vdb_vectors` | Vectors (pgvector `vector(N)`) |
| `vdb_indexes` | ANN index metadata |
| `vdb_namespaces` | Multi-tenant namespacing |
| `vdb_stats` | Per-collection stats |

## 🔤 Enums
- `VDBBackend`: PGVECTOR, QDRANT, WEAVIATE, PINECONE, CHROMA, MILVUS
- `VectorMetric`: COSINE, L2, IP
- `ANNIndexType`: HNSW, IVFFLAT, FLAT, SCANN, DISKANN
- `IndexBuildStatus`: PENDING, BUILDING, READY, FAILED

## 💎 Value Objects
- `VectorQuery(vector, top_k, filter, metric, include_metadata)`
- `HNSWParams(m, ef_construction, ef_search)`
- `IVFFlatParams(lists, probes)`

## 🔌 Public Port (contract ที่ module อื่นใช้)
```python
class VectorStorePort(Protocol):
    async def upsert(self, *, collection: str, vectors: list[VectorRecord]) -> int: ...
    async def query(self, *, collection: str, query: VectorQuery) -> list[SearchHit]: ...
    async def delete(self, *, collection: str, ids: list[str]) -> int: ...
```

## 🌐 Endpoints
```
GET    /api/v1/vdb/collections
POST   /api/v1/vdb/collections
POST   /api/v1/vdb/collections/{id}/upsert
POST   /api/v1/vdb/collections/{id}/query
DELETE /api/v1/vdb/collections/{id}/vectors/{vid}
GET    /api/v1/vdb/collections/{id}/stats
POST   /api/v1/vdb/collections/{id}/indexes
```

## 📤 Opencode Prompt

```
Generate `create_module_vector_db.py` v1.0.0 (SECTION 1..7, same as llm).

CONSTANTS:
  MODULE_NAME = "vector_db"
  PREFIX      = "vdb"
  VERSION     = "1.0.0"

DEPENDENCY (IMPORT ONLY):
  from app.modules.embeddings.application.ports import EmbeddingPort

ENTITIES:
  VDBCollection(id, tenant_id, name, dimension, metric, backend,
                config_json, is_active, created_at, updated_at)
  VDBVector(id, tenant_id, collection_id, source_id, vector_json,
            metadata_json, norm, created_at, updated_at)
  VDBIndex(id, collection_id, name, index_type, params_json,
           size_bytes, build_status, created_at, updated_at)
  VDBNamespace(id, tenant_id, collection_id, namespace, prefix, quota,
               created_at, updated_at)
  VDBStats(id, collection_id, vector_count, size_bytes, avg_latency_ms,
           updated_at)

ENUMS:
  VDBBackend(str, Enum): PGVECTOR, QDRANT, WEAVIATE, PINECONE, CHROMA, MILVUS
  VectorMetric(str, Enum): COSINE, L2, IP
  ANNIndexType(str, Enum): HNSW, IVFFLAT, FLAT, SCANN, DISKANN
  IndexBuildStatus(str, Enum): PENDING, BUILDING, READY, FAILED

VALUE OBJECTS:
  VectorQuery(vector: list[float], top_k: int, filter: dict | None,
              metric: VectorMetric, include_metadata: bool)
  HNSWParams(m: int, ef_construction: int, ef_search: int)
  IVFFlatParams(lists: int, probes: int)

PORTS:
  VectorStorePort (upsert, query, delete)
  BackendAdapter Protocol (PgVectorAdapter, QdrantAdapter, ChromaAdapter, ...)

REPOSITORIES:
  VDBCollectionRepository, VDBVectorRepository, VDBIndexRepository,
  VDBNamespaceRepository, VDBStatsRepository

ENDPOINTS:
  GET    /api/v1/vdb/collections
  POST   /api/v1/vdb/collections
  POST   /api/v1/vdb/collections/{id}/upsert
  POST   /api/v1/vdb/collections/{id}/query
  DELETE /api/v1/vdb/collections/{id}/vectors/{vid}
  GET    /api/v1/vdb/collections/{id}/stats
  POST   /api/v1/vdb/collections/{id}/indexes

SQL (uses pgvector extension):
  CREATE EXTENSION IF NOT EXISTS vector;
  vdb_vectors.vector_col vector(N) column type (cast via SQLAlchemy Vector type)
  HNSW:
    CREATE INDEX ... USING hnsw (vector_col vector_cosine_ops)
      WITH (m=16, ef_construction=64)
  IVFFlat:
    CREATE INDEX ... USING ivfflat (vector_col vector_cosine_ops)
      WITH (lists=100)

  All tables: tenant_id + RLS + set_updated_at_vdb trigger

Write complete runnable file.
```

## 🧪 Manual Test (10)
1. Create collection dim=1536 → 201
2. Upsert 1000 vectors → 200
3. Query top-10 → sorted by cosine
4. HNSW build → query < 20ms
5. IVFFlat → recall > 0.95
6. Filter by metadata → subset
7. Delete vector → 200
8. Stats reflect count
9. Cross-tenant isolation
10. Backend switch pgvector → qdrant

## ✅ Checklist
- [ ] `pgvector` extension created in V001
- [ ] `VectorStorePort` importable
- [ ] HNSW + IVFFlat indexes created
````

---

# 4. `tool_opencode_promt.md`

````markdown
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
````

---

# 5. `so_opencode_promt.md`

````markdown
# so_opencode_promt.md — Module `structured_outputs` Generator Prompt

## 🎯 Purpose
JSON schema enforcement + validation + repair loop
**Depends on:** `llm`

## 📋 Metadata
| Field | Value |
|-------|-------|
| MODULE_NAME | `structured_outputs` |
| PREFIX | `so` |
| VERSION | `1.0.0` |
| DEPS | `llm` |

## 🗄️ Tables
| Table | Purpose |
|-------|---------|
| `so_schemas` | JSON schemas / Pydantic models |
| `so_requests` | Requests (prompt + schema_id) |
| `so_outputs` | Validated outputs |
| `so_validations` | Validation attempts |
| `so_repairs` | Repair attempts |

## 🔤 Enums
- `SOStrategy`: JSON_MODE, FUNCTION_CALL, GRAMMAR, REGEX, PROMPT_ONLY
- `SOStatus`: PENDING, VALID, INVALID, REPAIRED, FAILED

## 💎 Value Objects
- `SchemaSpec(name, json_schema, pydantic_model, strict)`
- `SOResult(parsed, is_valid, attempts, tokens_used)`

## 🔌 Public Port
```python
class StructuredOutputPort(Protocol):
    async def generate(self, *, model: str, prompt: str,
                       schema_id: uuid.UUID,
                       max_repairs: int = 2) -> SOResult: ...
```

## 🌐 Endpoints
```
GET    /api/v1/so/schemas
POST   /api/v1/so/schemas
POST   /api/v1/so/generate
GET    /api/v1/so/outputs/{id}
POST   /api/v1/so/validate
```

## 📤 Opencode Prompt

```
Generate `create_module_structured_outputs.py` v1.0.0 (SECTION 1..7).

CONSTANTS:
  MODULE_NAME = "structured_outputs"
  PREFIX      = "so"
  VERSION     = "1.0.0"

DEPENDENCY:
  from app.modules.llm.application.ports import LLMPort

ENTITIES:
  SOSchema(id, tenant_id, name, json_schema, pydantic_model,
           version, strict, created_at, updated_at)
  SORequest(id, tenant_id, user_id, model, prompt, schema_id,
            temperature, max_repairs, created_at, updated_at)
  SOOutput(id, request_id, raw_text, parsed_json, is_valid,
           tokens_used, cost_usd, created_at, updated_at)
  SOValidation(id, output_id, attempt, errors_json, passed,
               created_at, updated_at)
  SORepair(id, output_id, attempt, feedback, raw_text,
           created_at, updated_at)

ENUMS:
  SOStrategy(str, Enum): JSON_MODE, FUNCTION_CALL, GRAMMAR, REGEX, PROMPT_ONLY
  SOStatus(str, Enum): PENDING, VALID, INVALID, REPAIRED, FAILED

VALUE OBJECTS:
  SchemaSpec(name, json_schema: dict, pydantic_model: str,
             strict: bool)
  SOResult(parsed: dict, is_valid: bool, attempts: int,
           tokens_used: int, cost_usd: Decimal)

EVENTS:
  SchemaRegistered, OutputGenerated, OutputValidated, OutputRepaired

PORTS:
  StructuredOutputPort (generate)
  SchemaValidator Protocol (validate(json, schema) -> list[Error])
  RepairStrategy Protocol (build_feedback(errors) -> str)

USE CASES:
  RegisterSchemaUseCase, GenerateStructuredUseCase (with repair loop),
  ValidateOutputUseCase

ENDPOINTS:
  GET  /api/v1/so/schemas
  POST /api/v1/so/schemas
  POST /api/v1/so/generate
  GET  /api/v1/so/outputs/{id}
  POST /api/v1/so/validate

REPAIR LOOP:
  1. Call LLMPort.chat with prompt + schema injection
  2. Parse JSON (fallback extract first {...})
  3. Validate with jsonschema or Pydantic
  4. If invalid and attempt < max_repairs:
       - build feedback message with errors
       - retry with feedback appended
  5. Return SOResult

SQL:
  Indexes:
    ix_so_schema_tenant_name UNIQUE
    ix_so_req_tenant_time
    ix_so_out_req
    ix_so_val_out
    ix_so_rep_out
  Trigger set_updated_at_so + RLS

Write complete runnable file.
```

## 🧪 Manual Test (10)
1. POST schema (Pydantic) → 201
2. Generate → valid output
3. Force invalid JSON → auto repair (≤2)
4. Strict mode → reject extras
5. Nested object → validate
6. Array of objects → validate
7. Enum constraint → reject
8. Regex pattern → reject
9. Repair log persisted
10. Output cache hit → `cached=true`

## ✅ Checklist
- [ ] `StructuredOutputPort` importable
- [ ] Repair loop max=2 default
- [ ] Pydantic + jsonschema both supported
````

---

# 6. `hs_opencode_promt.md`

````markdown
# hs_opencode_promt.md — Module `hybrid_search` Generator Prompt

## 🎯 Purpose
BM25 + Vector + Fusion (RRF) + Rerank
**Depends on:** `embeddings`, `vector_db`

## 📋 Metadata
| Field | Value |
|-------|-------|
| MODULE_NAME | `hybrid_search` |
| PREFIX | `hs` |
| VERSION | `1.0.0` |
| DEPS | `embeddings`, `vector_db` |

## 🗄️ Tables
| Table | Purpose |
|-------|---------|
| `hs_configs` | Named configs (α, RRF k) |
| `hs_queries` | Query log |
| `hs_results` | Per-query fused results |
| `hs_rankings` | Fusion intermediates |
| `hs_rerank_logs` | Reranker latency |

## 🔤 Enums
- `FusionType`: RRF, WEIGHTED_SUM, COMB_SUM, COMB_MNZ, BORDA, DBSF
- `SourceKind`: BM25, VECTOR, HYBRID, RERANK
- `RerankerType`: NONE, CROSS_ENCODER, COHERE, BGE, COLBERT

## 💎 Value Objects
- `HybridQuery(text, top_k, config_id, filters)`
- `FusionConfig(fusion_type, rrf_k, weights)`

## 📐 Metrics (ต้องคำนวณ)
- `MRR` (Mean Reciprocal Rank)
- `NDCG` (Normalized Discounted Cumulative Gain)
- `Recall@k`, `Precision@k`

## 🔌 Public Port
```python
class HybridSearchPort(Protocol):
    async def search(self, *, query: str, top_k: int = 10,
                     config_id: uuid.UUID | None = None,
                     filters: dict | None = None) -> list[SearchHit]: ...
```

## 🌐 Endpoints
```
GET    /api/v1/hs/configs
POST   /api/v1/hs/configs
POST   /api/v1/hs/search
GET    /api/v1/hs/queries/{id}
GET    /api/v1/hs/queries/{id}/ranking
```

## 📤 Opencode Prompt

```
Generate `create_module_hybrid_search.py` v1.0.0 (SECTION 1..7).

CONSTANTS:
  MODULE_NAME = "hybrid_search"
  PREFIX      = "hs"
  VERSION     = "1.0.0"

DEPENDENCIES:
  from app.modules.embeddings.application.ports import EmbeddingPort
  from app.modules.vector_db.application.ports import VectorStorePort

ENTITIES:
  HSConfig(id, tenant_id, name, bm25_weight, vector_weight,
           fusion_type, rrf_k, top_k, reranker_type, is_active,
           created_at, updated_at)
  HSQuery(id, tenant_id, user_id, config_id, query_text,
          latency_ms, result_count, created_at, updated_at)
  HSResult(id, query_id, rank, score, source_kind, source_id,
           snippet, metadata_json, created_at, updated_at)
  HSRanking(id, query_id, stage, source_kind, source_id,
            raw_score, normalized_score, rank, created_at, updated_at)
  HSRerankLog(id, query_id, reranker_type, input_count,
              output_count, latency_ms, created_at, updated_at)

ENUMS:
  FusionType(str, Enum): RRF, WEIGHTED_SUM, COMB_SUM, COMB_MNZ,
                         BORDA, DBSF
  SourceKind(str, Enum): BM25, VECTOR, HYBRID, RERANK
  RerankerType(str, Enum): NONE, CROSS_ENCODER, COHERE, BGE, COLBERT

VALUE OBJECTS:
  HybridQuery(text, top_k, config_id | None, filters | None)
  FusionConfig(fusion_type, rrf_k, weights: dict[str, float])

EVENTS:
  SearchExecuted, RerankCompleted, MetricsComputed

PORTS:
  HybridSearchPort (search)
  SparseRetriever Protocol (BM25) — Postgres tsvector + ts_rank
  DenseRetriever Protocol (uses VectorStorePort)
  FusionStrategy Protocol (RRF, WeightedSum, CombSUM, CombMNZ, Borda, DBSF)
  Reranker Protocol (CrossEncoderReranker, CohereReranker, BGEReranker)

USE CASES:
  CreateConfigUseCase, SearchUseCase (parallel BM25 + vector),
  GetRankingUseCase, ComputeMetricsUseCase

ENDPOINTS:
  GET  /api/v1/hs/configs
  POST /api/v1/hs/configs
  POST /api/v1/hs/search
  GET  /api/v1/hs/queries/{id}
  GET  /api/v1/hs/queries/{id}/ranking

FUSION:
  RRF: score = Σ 1/(k + rank_i)   (default k=60)
  WeightedSum: score = α·bm25 + (1-α)·vector
  CombSUM: score = Σ score_i
  CombMNZ: CombSUM × |{i: score_i > 0}|

METRICS (module helpers):
  mrr(ranks: list[int]) -> float
  ndcg(relevances: list[float], k: int) -> float
  recall_at_k(retrieved: set, relevant: set, k: int) -> float
  precision_at_k(retrieved: set, relevant: set, k: int) -> float

SQL:
  BM25 support: ADD COLUMN ts_vector tsvector
               CREATE INDEX USING GIN (ts_vector)
               Trigger: ts_vector = to_tsvector('simple', snippet)
  Indexes:
    ix_hs_cfg_tenant_name UNIQUE
    ix_hs_q_tenant_time
    ix_hs_res_query_rank
    ix_hs_rank_query_stage
    ix_hs_rr_query
  Trigger set_updated_at_hs + RLS

Write complete runnable file.
```

## 🧪 Manual Test (10)
1. Config α=0.5 → 201
2. Search → fused top-10 with ranks
3. RRF k=60 → verify ranks
4. Cross-encoder rerank → reorders
5. MRR/NDCG per query stored
6. BM25-only vs vector-only vs hybrid compare
7. Filters applied correctly
8. Cross-tenant isolation
9. Ranking log stores intermediates
10. p95 latency < 200ms

## ✅ Checklist
- [ ] `HybridSearchPort` importable
- [ ] BM25 uses Postgres tsvector
- [ ] RRF default k=60
- [ ] Metrics helpers exposed
````

---

# 7. `lc_opencode_promt.md`

````markdown
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
````

---

# 8. `li_opencode_promt.md`

````markdown
# li_opencode_promt.md — Module `llamaindex` Generator Prompt

## 🎯 Purpose
LlamaIndex index / query engine wrapper + node store
**Depends on:** `llm`, `embeddings`, `vector_db`

## 📋 Metadata
| Field | Value |
|-------|-------|
| MODULE_NAME | `llamaindex` |
| PREFIX | `li` |
| VERSION | `1.0.0` |
| DEPS | `llm`, `embeddings`, `vector_db` |

## 🗄️ Tables
| Table | Purpose |
|-------|---------|
| `li_indexes` | Index defs |
| `li_nodes` | TextNode / IndexNode |
| `li_query_engines` | Query engine configs |
| `li_documents` | Source docs |
| `li_runs` | Query runs |

## 🔤 Enums
- `IndexType`: VECTOR_STORE, SUMMARY, TREE, KEYWORD, KG, DOCUMENT_SUMMARY
- `NodeType`: TEXT, IMAGE, INDEX, MULTIMODAL
- `ResponseMode`: COMPACT, REFINE, TREE_SUMMARIZE, SIMPLE_SUMMARIZE,
                  NO_TEXT, GENERATION, ACCUMULATE

## 🔌 Public Port
```python
class LIIndexPort(Protocol):
    async def query(self, *, index_id: uuid.UUID, query: str,
                    top_k: int = 5) -> LIRunResult: ...
    async def ingest(self, *, index_id: uuid.UUID,
                     documents: list[LIDoc]) -> int: ...
```

## 🌐 Endpoints
```
GET    /api/v1/li/indexes
POST   /api/v1/li/indexes
POST   /api/v1/li/indexes/{id}/query
POST   /api/v1/li/indexes/{id}/ingest
GET    /api/v1/li/query-engines
GET    /api/v1/li/runs/{id}
```

## 📤 Opencode Prompt

```
Generate `create_module_llamaindex.py` v1.0.0 (SECTION 1..7).

CONSTANTS:
  MODULE_NAME = "llamaindex"
  PREFIX      = "li"
  VERSION     = "1.0.0"

DEPENDENCIES:
  from app.modules.llm.application.ports import LLMPort
  from app.modules.embeddings.application.ports import EmbeddingPort
  from app.modules.vector_db.application.ports import VectorStorePort

ENTITIES:
  LIIndex(id, tenant_id, name, index_type, embed_model,
          storage_kind, config_json, is_active,
          created_at, updated_at)
  LINode(id, tenant_id, index_id, node_type, content,
         embedding_id, relationships_json, metadata_json,
         created_at, updated_at)
  LIQueryEngine(id, tenant_id, index_id, name, retriever_type,
                top_k, response_mode, config_json,
                created_at, updated_at)
  LIDocument(id, tenant_id, index_id, source_uri, mime_type,
             title, hash, status, created_at, updated_at)
  LIRun(id, tenant_id, user_id, query_engine_id, query, answer,
        source_nodes_json, latency_ms, tokens_used,
        created_at, updated_at)

ENUMS:
  IndexType(str, Enum): VECTOR_STORE, SUMMARY, TREE, KEYWORD, KG,
                        DOCUMENT_SUMMARY
  NodeType(str, Enum): TEXT, IMAGE, INDEX, MULTIMODAL
  ResponseMode(str, Enum): COMPACT, REFINE, TREE_SUMMARIZE,
                           SIMPLE_SUMMARIZE, NO_TEXT, GENERATION,
                           ACCUMULATE

VALUE OBJECTS:
  IndexSpec(name, index_type, embed_model)
  QueryEngineSpec(name, retriever_type, top_k, response_mode)
  NodeRelationship(parent_id, child_ids, prev_id, next_id)

EVENTS:
  IndexCreated, DocumentIngested, NodesCreated, QueryExecuted

PORTS:
  LIIndexPort (query, ingest)
  NodeParserPort (split_documents)
  RetrieverPort (retrieve)  — uses VectorStorePort internally
  SynthesizerPort (synthesize)  — uses LLMPort internally
  ResponseModeStrategy Protocol (COMPACT, REFINE, TREE_SUMMARIZE, ...)

USE CASES:
  CreateIndexUseCase, IngestDocumentUseCase, QueryIndexUseCase,
  GetRunUseCase

ENDPOINTS:
  GET  /api/v1/li/indexes
  POST /api/v1/li/indexes
  POST /api/v1/li/indexes/{id}/query
  POST /api/v1/li/indexes/{id}/ingest
  GET  /api/v1/li/query-engines
  GET  /api/v1/li/runs/{id}

INGEST PIPELINE:
  1. Load document (URI / bytes)
  2. NodeParser.split → list[LINode]  (SentenceSplitter default)
  3. Embed each node via EmbeddingPort
  4. Upsert to VectorStorePort
  5. Create parent/child relationships in relationships_json
  6. Persist nodes to li_nodes

SQL:
  Indexes:
    ix_li_index_tenant_name UNIQUE
    ix_li_node_index
    ix_li_qe_index
    ix_li_doc_index_hash
    ix_li_run_tenant_time
  Trigger set_updated_at_li + RLS

Write complete runnable file.
```

## 🧪 Manual Test (10)
1. Create VectorStoreIndex → 201
2. Ingest 10 docs → nodes created
3. Query → answer + source_nodes
4. SummaryIndex with tree_summarize
5. KG index + entity extraction
6. Response mode refine → multi-pass
7. Sub-question query engine
8. Cross-tenant node isolation
9. Node relationships preserved
10. Hybrid retrieval (BM25 + vector)

## ✅ Checklist
- [ ] `LIIndexPort` importable
- [ ] Ingest pipeline uses EmbeddingPort + VectorStorePort
- [ ] Response modes pluggable
````

---

# 9. `rag_opencode_promt.md`

````markdown
# rag_opencode_promt.md — Module `rag` Generator Prompt

## 🎯 Purpose
Retrieval Augmented Generation pipeline
(ingest → chunk → embed → retrieve → rerank → generate)
**Depends on:** `llm`, `embeddings`, `vector_db`, `hybrid_search`

## 📋 Metadata
| Field | Value |
|-------|-------|
| MODULE_NAME | `rag` |
| PREFIX | `rag` |
| VERSION | `1.0.0` |
| DEPS | `llm`, `embeddings`, `vector_db`, `hybrid_search` |

## 🗄️ Tables
| Table | Purpose |
|-------|---------|
| `rag_documents` | Source documents |
| `rag_chunks` | Chunked segments (embedding_id ref) |
| `rag_pipelines` | Named configs (chunker, retriever, reranker) |
| `rag_runs` | One RAG execution |
| `rag_citations` | Chunk citations per answer |
| `rag_retrieval_logs` | Retrieval latency, scores, top-k |

## 🔤 Enums
- `ChunkerType`: FIXED, RECURSIVE, SEMANTIC, MARKDOWN, CODE
- `RetrieverType`: VECTOR, BM25, HYBRID, MMR
- `RerankerType`: NONE, CROSS_ENCODER, COHERE, BGE
- `DocumentStatus`: PENDING, PROCESSING, READY, FAILED, DELETED
- `RunStatus`: QUEUED, RETRIEVING, RERANKING, GENERATING, DONE, FAILED

## 💎 Value Objects
- `ChunkConfig(chunker_type, chunk_size, chunk_overlap, separators)`
- `RetrievalConfig(top_k, score_threshold, retriever_type, mmr_lambda)`
- `CitationVO(chunk_id, document_id, score, snippet)`

## 🔌 Public Port
```python
class RAGPort(Protocol):
    async def answer(self, *, query: str, pipeline_id: uuid.UUID | None,
                     conversation_id: uuid.UUID | None) -> RAGAnswer: ...
    async def ingest(self, *, source_uri: str, pipeline_id: uuid.UUID,
                     metadata: dict | None = None) -> uuid.UUID: ...

@dataclass
class RAGAnswer:
    run_id: uuid.UUID
    answer: str
    citations: list[CitationVO]
    usage: TokenUsage
```

## 🌐 Endpoints
```
POST   /api/v1/rag/ingest
POST   /api/v1/rag/query
GET    /api/v1/rag/documents
GET    /api/v1/rag/documents/{id}
DELETE /api/v1/rag/documents/{id}
GET    /api/v1/rag/pipelines
POST   /api/v1/rag/pipelines
GET    /api/v1/rag/runs/{id}
```

## 📤 Opencode Prompt

```
Generate `create_module_rag.py` v1.0.0 (SECTION 1..7).

CONSTANTS:
  MODULE_NAME = "rag"
  PREFIX      = "rag"
  VERSION     = "1.0.0"

DEPENDENCIES:
  from app.modules.llm.application.ports import LLMPort
  from app.modules.embeddings.application.ports import EmbeddingPort
  from app.modules.vector_db.application.ports import VectorStorePort
  from app.modules.hybrid_search.application.ports import HybridSearchPort

ENTITIES:
  Document(id, tenant_id, user_id, source_uri, mime_type, title,
           content, hash, status, size_bytes, metadata_json,
           created_at, updated_at)
  Chunk(id, tenant_id, document_id, ordinal, content, token_count,
        embedding_id, metadata_json, created_at, updated_at)
  Pipeline(id, tenant_id, name, chunker_type, chunk_size,
           chunk_overlap, retriever_type, top_k, reranker_type,
           is_active, created_at, updated_at)
  Run(id, tenant_id, user_id, pipeline_id, query, answer,
      model_name, latency_ms, total_tokens, cost_usd, status,
      created_at, updated_at)
  Citation(id, run_id, chunk_id, document_id, score, rank, snippet,
           created_at, updated_at)
  RetrievalLog(id, run_id, stage, top_k, candidates_json,
               latency_ms, created_at, updated_at)

ENUMS:
  ChunkerType(str, Enum): FIXED, RECURSIVE, SEMANTIC, MARKDOWN, CODE
  RetrieverType(str, Enum): VECTOR, BM25, HYBRID, MMR
  RerankerType(str, Enum): NONE, CROSS_ENCODER, COHERE, BGE
  DocumentStatus(str, Enum): PENDING, PROCESSING, READY, FAILED, DELETED
  RunStatus(str, Enum): QUEUED, RETRIEVING, RERANKING, GENERATING,
                        DONE, FAILED

VALUE OBJECTS:
  ChunkConfig(chunker_type, chunk_size, chunk_overlap, separators)
  RetrievalConfig(top_k, score_threshold, retriever_type, mmr_lambda)
  CitationVO(chunk_id, document_id, score, snippet)

EVENTS:
  DocumentIngested, DocumentChunked, RetrievalCompleted,
  RAGAnswerGenerated, PipelineCreated

PORTS:
  RAGPort (answer, ingest)
  ChunkerPort (chunk)         — FIXED, RECURSIVE, SEMANTIC, MARKDOWN, CODE
  RetrieverPort (retrieve)    — dispatches to VectorStorePort / HybridSearchPort
  RerankerPort (rerank)       — CROSS_ENCODER, COHERE, BGE
  GeneratorPort (generate)    — uses LLMPort with citations in system prompt

USE CASES:
  IngestDocumentUseCase, QueryRAGUseCase, CreatePipelineUseCase,
  GetRunUseCase, DeleteDocumentUseCase

ENDPOINTS:
  POST   /api/v1/rag/ingest
  POST   /api/v1/rag/query
  GET    /api/v1/rag/documents?limit=
  GET    /api/v1/rag/documents/{id}
  DELETE /api/v1/rag/documents/{id}
  GET    /api/v1/rag/pipelines
  POST   /api/v1/rag/pipelines
  GET    /api/v1/rag/runs/{id}

INGEST PIPELINE:
  1. Fetch source (URI or bytes) → Document(status=PENDING)
  2. Compute hash; if exists skip (dedupe)
  3. Update status=PROCESSING
  4. Chunk via ChunkerPort → list[Chunk]
  5. Embed each chunk via EmbeddingPort
  6. Upsert vectors to VectorStorePort
  7. Save Chunks (with embedding_id)
  8. Update status=READY, publish DocumentIngested

QUERY PIPELINE:
  1. Create Run(status=QUEUED)
  2. Update status=RETRIEVING
  3. Retrieve top_k via RetrieverPort
     - VECTOR  → VectorStorePort.query(embed(query))
     - BM25    → ts_vector query
     - HYBRID  → HybridSearchPort.search(query)
     - MMR     → MMR over vector candidates
  4. Update status=RERANKING
  5. Rerank via RerankerPort (if not NONE)
  6. Update status=GENERATING
  7. Build prompt with citations [1][2][3]...
  8. Call LLMPort.chat()
  9. Persist Citations (rank, score, snippet)
  10. Update status=DONE, publish RAGAnswerGenerated

SQL:
  Indexes:
    ix_rag_doc_tenant_status
    ix_rag_doc_tenant_hash UNIQUE
    ix_rag_chunk_doc_ordinal
    ix_rag_pipe_tenant_name UNIQUE
    ix_rag_run_tenant_time
    ix_rag_run_user_time
    ix_rag_cit_run_rank
    ix_rag_rlog_run_stage
  Trigger set_updated_at_rag + RLS

Write complete runnable file.
```

## 🧪 Manual Test (12)
1. Ingest PDF → status=READY ≤ 5s
2. Query → answer + citations[] + usage
3. Citation has chunk_id, score, snippet
4. Custom pipeline (semantic + MMR) → different top-k
5. RLS: other tenant → 404
6. Idempotency-Key retry → same response
7. Doc hash duplicate → skip ingest
8. Delete → soft delete + chunk cascade
9. Retrieval latency logged
10. Multi-tenant pipeline isolation
11. Cross-encoder reranker reorders
12. Retriever error → 502 PROVIDER_ERROR

## ✅ Checklist
- [ ] `RAGPort` importable
- [ ] Ingest pipeline uses EmbeddingPort + VectorStorePort
- [ ] Query pipeline uses HybridSearchPort (optional)
- [ ] Citations persisted with rank + score
````

---

# 10. `eval_opencode_promt.md`

````markdown
# eval_opencode_promt.md — Module `ai_evaluation` Generator Prompt

## 🎯 Purpose
LLM / RAG evaluation
(RAGAS, faithfulness, MRR, NDCG, hallucination detection)
**Depends on:** `llm`, `rag`

## 📋 Metadata
| Field | Value |
|-------|-------|
| MODULE_NAME | `ai_evaluation` |
| PREFIX | `eval` |
| VERSION | `1.0.0` |
| DEPS | `llm`, `rag` |

## 🗄️ Tables
| Table | Purpose |
|-------|---------|
| `eval_datasets` | Datasets |
| `eval_test_cases` | Cases (question, ground_truth, context) |
| `eval_runs` | Run of dataset against model/pipeline |
| `eval_metrics` | Metric definitions |
| `eval_results` | Per-case scores |
| `eval_reports` | Aggregated reports |

## 🔤 Enums
- `MetricKind`: EXACT_MATCH, F1, ROUGE, BLEU, BERTSCORE,
                FAITHFULNESS, ANSWER_RELEVANCE, CONTEXT_PRECISION,
                CONTEXT_RECALL, MRR, NDCG, RAGAS, HALLUCINATION,
                LATENCY, COST
- `RunStatus`: QUEUED, RUNNING, DONE, FAILED, CANCELLED
- `TaskType`: QA, SUMMARIZATION, CLASSIFICATION, RAG, AGENT

## 💎 Value Objects
- `MetricScore(name, value, confidence, details)`
- `EvalConfig(metrics, sample_size, temperature, seed)`

## 🔌 Public Port
```python
class EvalRunnerPort(Protocol):
    async def run(self, *, dataset_id: uuid.UUID,
                  target: EvalTarget,
                  config: EvalConfig) -> EvalReportRef: ...
```

## 🌐 Endpoints
```
GET    /api/v1/eval/datasets
POST   /api/v1/eval/datasets
POST   /api/v1/eval/run
GET    /api/v1/eval/runs/{id}
GET    /api/v1/eval/runs/{id}/report
GET    /api/v1/eval/metrics
```

## 📤 Opencode Prompt

```
Generate `create_module_ai_evaluation.py` v1.0.0 (SECTION 1..7).

CONSTANTS:
  MODULE_NAME = "ai_evaluation"
  PREFIX      = "eval"
  VERSION     = "1.0.0"

DEPENDENCIES:
  from app.modules.llm.application.ports import LLMPort
  from app.modules.rag.application.ports import RAGPort

ENTITIES:
  EvalDataset(id, tenant_id, name, description, task_type,
              version, case_count, created_at, updated_at)
  EvalTestCase(id, dataset_id, question, ground_truth,
               context_json, metadata_json, created_at, updated_at)
  EvalRun(id, tenant_id, user_id, dataset_id, target_model,
          target_pipeline, config_json, status, started_at,
          finished_at, created_at, updated_at)
  EvalMetric(id, name, kind, higher_is_better, range_min, range_max,
             created_at, updated_at)
  EvalResult(id, run_id, case_id, metric_name, score, details_json,
             latency_ms, cost_usd, created_at, updated_at)
  EvalReport(id, run_id, summary_json, passed, generated_at,
             created_at, updated_at)

ENUMS:
  MetricKind(str, Enum): EXACT_MATCH, F1, ROUGE, BLEU, BERTSCORE,
                          FAITHFULNESS, ANSWER_RELEVANCE,
                          CONTEXT_PRECISION, CONTEXT_RECALL,
                          MRR, NDCG, RAGAS, HALLUCINATION,
                          LATENCY, COST
  RunStatus(str, Enum): QUEUED, RUNNING, DONE, FAILED, CANCELLED
  TaskType(str, Enum): QA, SUMMARIZATION, CLASSIFICATION, RAG, AGENT

VALUE OBJECTS:
  MetricScore(name, value, confidence, details)
  EvalConfig(metrics: list[str], sample_size: int,
             temperature: float, seed: int | None)
  EvalTarget(kind: "model" | "pipeline", ref: str)

EVENTS:
  DatasetCreated, EvalRunStarted, EvalRunCompleted, MetricComputed,
  HallucinationDetected

PORTS:
  EvalRunnerPort (run)
  MetricEvaluator Protocol:
    - ExactMatchEvaluator, F1Evaluator, RougeEvaluator,
      BleuEvaluator, BertScoreEvaluator
    - FaithfulnessEvaluator, AnswerRelevanceEvaluator,
      ContextPrecisionEvaluator, ContextRecallEvaluator
    - MRREvaluator, NDCGEvaluator
    - RAGASEvaluator (combines faithfulness + relevance + precision + recall)
    - HallucinationEvaluator (uses LLMPort as judge)

USE CASES:
  CreateDatasetUseCase, RunEvaluationUseCase, GetReportUseCase

ENDPOINTS:
  GET  /api/v1/eval/datasets
  POST /api/v1/eval/datasets
  POST /api/v1/eval/run
  GET  /api/v1/eval/runs/{id}
  GET  /api/v1/eval/runs/{id}/report
  GET  /api/v1/eval/metrics

EVAL PIPELINE:
  1. Load EvalDataset + cases
  2. Sample if sample_size < len(cases) (seeded)
  3. For each case:
     a. If target=model → LLMPort.chat(question) → answer
     b. If target=pipeline → RAGPort.answer(question) → answer + citations
     c. Compute each metric:
        - Compare answer vs ground_truth
        - If context available → faithfulness, precision, recall
        - If ranking available → MRR, NDCG
     d. Persist EvalResult
  4. Aggregate → EvalReport(summary_json, passed)
  5. Publish EvalRunCompleted

METRIC HELPERS (module helpers):
  exact_match(pred, ref) -> float
  f1(pred_tokens, ref_tokens) -> float
  rouge_l(pred, ref) -> float
  bleu(pred, ref, n=4) -> float
  faithfulness(answer, context, judge: LLMPort) -> float
  answer_relevance(question, answer, judge: LLMPort) -> float
  context_precision(retrieved, relevant) -> float
  context_recall(retrieved, relevant) -> float
  mrr(ranks) -> float
  ndcg(relevances, k) -> float
  ragas_score(faith, rel, prec, rec) -> float   # harmonic mean
  hallucination(answer, context, judge: LLMPort) -> float

SQL:
  Indexes:
    ix_eval_ds_tenant_name UNIQUE
    ix_eval_case_dataset
    ix_eval_run_tenant_time
    ix_eval_run_status
    ix_eval_res_run_metric
    ix_eval_rep_run
    ix_eval_metric_name UNIQUE
  Trigger set_updated_at_eval + RLS
  Seed V002: default metrics rows (MRR, NDCG, faithfulness,
             answer_relevance, context_precision, context_recall,
             RAGAS, hallucination)

Write complete runnable file.
```

## 🧪 Manual Test (10)
1. Create dataset 10 cases → 201
2. Run vs gpt-4o-mini → status DONE
3. Report has MRR, NDCG, faithfulness
4. RAGAS computed correctly
5. Hallucination detection works
6. Cost/latency aggregated
7. Cross-model comparison (2 runs)
8. Export CSV/JSON
9. `sample_size=50%` working
10. Concurrent runs isolated

## ✅ Checklist
- [ ] `EvalRunnerPort` importable
- [ ] RAGAS combines 4 sub-metrics
- [ ] LLM-as-judge uses LLMPort
- [ ] Report aggregator returns `summary_json` with all metrics
````

---

# 🔗 Integration Guide — วิธีทำให้ทุก module ทำงานร่วมกัน

## Step 1 — สร้างตามลำดับ dependency

```bash
# Layer 0 — Base
python create_module_llm.py all llm 5 llm --force
python create_module_embeddings.py all embeddings 5 emb --force

# Layer 1 — Indexing & Tools
python create_module_vector_db.py all vector_db 5 vdb --force
python create_module_tool_calling.py all tool_calling 5 tool --force
python create_module_structured_outputs.py all structured_outputs 5 so --force

# Layer 2 — Retrieval & Orchestration
python create_module_hybrid_search.py all hybrid_search 5 hs --force
python create_module_langchain.py all langchain 5 lc --force
python create_module_llamaindex.py all llamaindex 5 li --force

# Layer 3 — Application
python create_module_rag.py all rag 5 rag --force
python create_module_ai_evaluation.py all ai_evaluation 5 eval --force
```

## Step 2 — Migration (order matters)

```bash
alembic upgrade head    # V001 for all modules in dependency order
```

## Step 3 — Wire adapters (dependency injection)

ทุก module ใช้ **ports + adapters** ทำให้ wire ข้าม module ได้:

```python
# app/wiring.py — Composition root
from app.modules.embeddings.application.ports import EmbeddingPort
from app.modules.embeddings.infrastructure.services import OpenAIEmbeddingClient

from app.modules.vector_db.application.ports import VectorStorePort
from app.modules.vector_db.infrastructure.services import PgVectorAdapter

from app.modules.hybrid_search.application.ports import HybridSearchPort
from app.modules.hybrid_search.infrastructure.services import DefaultHybridSearch

from app.modules.rag.application.ports import RAGPort
from app.modules.rag.infrastructure.services import DefaultRAG

# Wire concrete adapters
embedding: EmbeddingPort = OpenAIEmbeddingClient(api_key=...)
vector_store: VectorStorePort = PgVectorAdapter(session_factory)
hybrid: HybridSearchPort = DefaultHybridSearch(
    embedding=embedding, vector_store=vector_store,
)
rag: RAGPort = DefaultRAG(
    llm=llm_port, embedding=embedding,
    vector_store=vector_store, hybrid=hybrid,
)
```

## Step 4 — Cross-module contracts

| Contract | Provided by | Consumed by |
|----------|-------------|-------------|
| `LLMPort` | `llm` | `tool`, `so`, `rag`, `lc`, `li`, `eval` |
| `EmbeddingPort` | `embeddings` | `vector_db`, `hybrid_search`, `rag`, `li` |
| `VectorStorePort` | `vector_db` | `hybrid_search`, `rag`, `li` |
| `ToolRegistryPort` | `tool_calling` | `langchain` |
| `HybridSearchPort` | `hybrid_search` | `rag` |
| `RAGPort` | `rag` | `ai_evaluation` |

## Step 5 — Shared env vars

```bash
# .env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
COHERE_API_KEY=...
TOOL_SECRET_KEY=<32-byte-base64>
RAG_DEFAULT_TOP_K=5
EMB_DEFAULT_MODEL=text-embedding-3-small
VDB_DEFAULT_BACKEND=pgvector
```

## Step 6 — Verify

```bash
# OpenAPI shows all tags
curl -s http://localhost:8000/openapi.json | jq '.tags[].name'
# Expected: LLM, Embeddings, VectorDB, Tools, StructuredOutputs,
#           HybridSearch, LangChain, LlamaIndex, RAG, AIEvaluation

# Smoke test each module
for m in llm embeddings vector_db tool_calling structured_outputs \
         hybrid_search langchain llamaindex rag ai_evaluation; do
  curl -s -o /dev/null -w "$m: %{http_code}\n" \
    -H "X-Tenant-Id: 00000000-0000-0000-0000-000000000001" \
    "http://localhost:8000/api/v1/$m/health" 2>/dev/null || echo "$m: N/A"
done
```

---

# 📊 Summary Table

| # | File | Module | Prefix | Deps | Layer |
|---|------|--------|--------|------|-------|
| 1 | `llm_opencode_promt.md` | `llm` | `llm_` | — | 0 |
| 2 | `emb_opencode_promt.md` | `embeddings` | `emb_` | — | 0 |
| 3 | `vdb_opencode_promt.md` | `vector_db` | `vdb_` | emb | 1 |
| 4 | `tool_opencode_promt.md` | `tool_calling` | `tool_` | llm | 1 |
| 5 | `so_opencode_promt.md` | `structured_outputs` | `so_` | llm | 1 |
| 6 | `hs_opencode_promt.md` | `hybrid_search` | `hs_` | emb, vdb | 2 |
| 7 | `lc_opencode_promt.md` | `langchain` | `lc_` | llm, tool | 2 |
| 8 | `li_opencode_promt.md` | `llamaindex` | `li_` | llm, emb, vdb | 2 |
| 9 | `rag_opencode_promt.md` | `rag` | `rag_` | llm, emb, vdb, hs | 3 |
| 10 | `eval_opencode_promt.md` | `ai_evaluation` | `eval_` | llm, rag | 3 |

---

# 🎯 Usage Workflow

```
┌────────────────────────────────────────────────────────┐
│  STEP 1: Copy ไฟล์ prompt ที่ต้องการใส่ opencode       │
│          e.g. llm_opencode_promt.md                    │
└───────────────────────┬────────────────────────────────┘
                        ▼
┌────────────────────────────────────────────────────────┐
│  STEP 2: opencode จะ generate create_module_<m>.py     │
└───────────────────────┬────────────────────────────────┘
                        ▼
┌────────────────────────────────────────────────────────┐
│  STEP 3: python create_module_<m>.py all <m> 5 <p> -f  │
└───────────────────────┬────────────────────────────────┘
                        ▼
┌────────────────────────────────────────────────────────┐
│  STEP 4: alembic upgrade head                          │
└───────────────────────┬────────────────────────────────┘
                        ▼
┌────────────────────────────────────────────────────────┐
│  STEP 5: Wire adapters in app/wiring.py                │
└───────────────────────┬────────────────────────────────┘
                        ▼
┌────────────────────────────────────────────────────────┐
│  STEP 6: Test via /docs + Postman collection           │
└────────────────────────────────────────────────────────┘
```

 # 🎯 ตอบตรงๆ: **ยังไม่ครบ และยังใช้ไม่ได้จริงทันที**

ผมต้องซื่อสัตย์กับคุณ — สิ่งที่ผมส่งไปรอบที่แล้วเป็น **"prompt spec"** ไม่ใช่ **"generator file"** แบบเดียวกับ `create_module_llm.py` v1.2.1 ที่คุณมีอยู่

---

## 📊 ตรวจสอบความครบถ้วนจริง

| # | ไฟล์ | สถานะจริง | ใช้ได้ทันที? |
|---|------|-----------|:-----------:|
| 1 | `llm_opencode_promt.md` | มี prompt + reference เต็ม | ⚠️ ต้อง paste เข้า opencode ก่อน |
| 2 | `emb_opencode_promt.md` | มีแค่ prompt spec | ❌ ไม่มี `create_module_embeddings.py` |
| 3 | `vdb_opencode_promt.md` | มีแค่ prompt spec | ❌ ไม่มี `create_module_vector_db.py` |
| 4 | `tool_opencode_promt.md` | มีแค่ prompt spec | ❌ ไม่มี `create_module_tool_calling.py` |
| 5 | `so_opencode_promt.md` | มีแค่ prompt spec | ❌ ไม่มี `create_module_structured_outputs.py` |
| 6 | `hs_opencode_promt.md` | มีแค่ prompt spec | ❌ ไม่มี `create_module_hybrid_search.py` |
| 7 | `lc_opencode_promt.md` | มีแค่ prompt spec | ❌ ไม่มี `create_module_langchain.py` |
| 8 | `li_opencode_promt.md` | มีแค่ prompt spec | ❌ ไม่มี `create_module_llamaindex.py` |
| 9 | `rag_opencode_promt.md` | มีแค่ prompt spec | ❌ ไม่มี `create_module_rag.py` |
| 10 | `eval_opencode_promt.md` | มีแค่ prompt spec | ❌ ไม่มี `create_module_ai_evaluation.py` |

**สรุป:** ที่ให้ไปคือ **1/10 ไฟล์มี reference ครบ** อีก **9/10 ยังต้อง generate เอง**

---

## 🐛 ปัญหาที่ผมเจอเอง (self-review)

### 1. **Ports vs Interfaces — ไม่ consistent**
ที่ผมเขียนใน prompt:
```python
from app.modules.llm.application.ports import LLMPort
```
แต่ใน `create_module_llm.py` v1.2.1 จริง ๆ คือ:
```python
# app/modules/llm/application/interfaces.py
class LLMClient(Protocol): ...
class ProviderRegistry(Protocol): ...
```
→ **ไม่มีไฟล์ `ports.py` และไม่มี `LLMPort`** ที่ผมสมมติขึ้นมา

### 2. **Dependencies ที่ต้องใช้จริง — ไม่ได้ระบุ**
```txt
# ต้องเพิ่มใน pyproject.toml แต่ผมไม่ได้บอก
pgvector>=0.2.5          # vdb
qdrant-client>=1.9       # vdb (optional)
rank-bm25>=0.2.2         # hs (หรือใช้ tsvector แทน)
sentence-transformers    # hs reranker
cohere>=5.0              # emb + reranker
voyageai>=0.2            # emb
langchain>=0.3           # lc
llama-index>=0.11        # li
ragas>=0.2               # eval
rouge-score>=0.1.2       # eval
nltk>=3.8                # eval (BLEU)
jsonschema>=4.20         # so
```

### 3. **Migration env.py — register 10 modules**
ใน `ENV_PY_BLOCK` ของ llm มีแค่:
```python
from app.modules.llm.infrastructure.models import ...
```
แต่ต้องมี 10 บล็อก (llm, emb, vdb, tool, so, hs, lc, li, rag, eval)

### 4. **Alembic revision chain — ผมเขียน `<prev>` ลอย ๆ**
```python
down_revision: Union[str, None] = "<prev>"
```
ต้องเรียง chain จริง: `llm_001 → emb_001 → vdb_001 → ...`

### 5. **Postman / docs — มีแค่ llm**
อีก 9 modules ไม่มี JSON collection และ README จริง

### 6. **จำนวน manual test — บาง module ผมเขียนหัวข้อ 12 แต่ list แค่ 10-11**

### 7. **RLS policy name collision**
ผมใช้ `p_llm_provider`, `p_llm_model` — แต่ module อื่นอาจชื่อซ้ำ pattern ถ้าไม่เปลี่ยน prefix

### 8. **`vector` column type ใน pgvector — SQLAlchemy**
ผมเขียน `vector_col vector(N)` ใน SQL แต่ **ไม่ได้ให้ SQLAlchemy type** ที่ถูกต้อง:
```python
from pgvector.sqlalchemy import Vector
vector_col: Mapped[list[float]] = mapped_column(Vector(1536))
```

### 9. **Trigger function naming per module**
ผมเขียน `set_updated_at_llm()` แต่ต้องมี `set_updated_at_emb()`, `set_updated_at_vdb()` ... แยกกัน หรือใช้ generic ตัวเดียว

### 10. **Circular import risk**
`rag` import `hybrid_search`, `hybrid_search` import `vector_db`, `vector_db` import `embeddings` — ถ้าใส่ `from ... import` ระดับ module top อาจ import error ตอน boot ต้องใช้ **lazy import ใน function** หรือ **TYPE_CHECKING guard**

---

## ✅ สิ่งที่ "ควรทำ" เพื่อให้ครบจริง

มี 3 ทางเลือก — เลือกตามเวลาที่คุณมี:

### 🅰️ Option A — Generate ทั้ง 9 ไฟล์เอง (ผมทำได้ แต่ยาวมาก)
ผมเขียน `create_module_<name>.py` **เต็มไฟล์** แบบ v1.2.1 ทั้ง 9 modules
**ประมาณการ:** 9 × 1,500–2,500 บรรทัด = ~15,000–22,000 บรรทัด
**ต้องแบ่งส่ง 3–4 messages** (ข้อความ limit)

### 🅱️ Option B — ทำ "shared kernel" ก่อน แล้วค่อยแตก module
ผมสร้าง:
1. `app/shared/` — base classes ที่ทุก module ใช้ร่วม
   - `BaseRepository`, `BaseEntity`, `BaseValueObject`
   - `RequestContext` (ตัวเดียว ไม่ต้องประกาศซ้ำ 10 ที่)
   - `AppError`, `DomainError` (base)
   - `BaseModel(Base)` ของ SQLAlchemy
   - `RLSMixin`, `TimestampMixin`
2. Template generator ตัวเดียว `create_module.py` ที่รับ config
3. แล้ว generate ทีละ module จาก template

**ข้อดี:** code สั้นลง 60%, consistent 100%
**ประมาณการ:** ~3,000 บรรทัด → **ส่งได้ใน 1–2 messages**

### 🅲 Option C — แก้เฉพาะที่ใช้จริง
คุณเลือก 2–3 modules ที่จะใช้ก่อน (เช่น `rag` + `emb` + `vdb`)
ผมเขียนเต็มให้เฉพาะ 3 modules นั้น พร้อม wire กันจริง

---

## 🔧 Fix ทันที (ของที่ผมทำได้ตอนนี้)

ถ้าคุณจะเดินหน้าต่อ — **ผมควรทำ 2 อย่างก่อน**:

### 1. สร้าง `ports.py` ให้ `llm` module จริง
```python
# app/modules/llm/application/ports.py  (NEW)
from __future__ import annotations
from typing import Protocol, AsyncIterator, Any
from dataclasses import dataclass
from app.modules.llm.domain.value_objects import ChatOptions, TokenUsage

@dataclass
class ChatResult:
    content: str
    finish_reason: str
    usage: TokenUsage
    cached: bool = False

class LLMPort(Protocol):
    async def chat(self, *, model: str, messages: list[dict[str, Any]],
                   options: ChatOptions | None = None) -> ChatResult: ...
    def stream(self, *, model: str, messages: list[dict[str, Any]],
               options: ChatOptions | None = None) -> AsyncIterator[dict[str, Any]]: ...
```
แล้วให้ `LLMUseCase` implement port นี้ (หรือทำ adapter)

### 2. สร้าง `app/shared/` (shared kernel)
```python
# app/shared/context.py
@dataclass
class RequestContext:
    tenant_id: uuid.UUID
    user_id: uuid.UUID | None = None

# app/shared/errors.py
class DomainError(Exception): code = "DOMAIN_ERROR"
class AppError(Exception): code = "APP_ERROR"; http_status = 400

# app/shared/models.py
class Base(DeclarativeBase): pass
class TimestampMixin: ...
class RLSMixin: ...

# app/shared/repository.py
class BaseRepository(ABC): ...
```

---

## 🎯 คำถามกลับ — คุณอยากได้แบบไหน?

ตอบสั้น ๆ 1 ข้อ:

**A.** "ขอ `create_module_<name>.py` เต็มทั้ง 9 ไฟล์" → ผมจะส่งเป็นชุด ๆ ละ 2–3 modules (ต้องใช้หลาย message)

**B.** "ทำ shared kernel + template generator ก่อน" → สั้นกว่า เข้าใจง่ายกว่า

**C.** "เอาแค่ 3 modules ที่ใช้จริง: `<ชื่อ>`" → ผมทำเต็มให้ 3 modules

**D.** "แก้ของเดิมให้ consistent (ports.py + shared + env.py + alembic chain) แล้วส่ง prompt ที่ถูก" → ยังเป็น prompt แต่คราวนี้**ถูกต้อง ไม่มี import ปลอม**

**E.** "เริ่มจาก 1 module ต้นแบบ เช่น `rag` เขียนเต็มยัน adapter wiring ให้ดูเป็นตัวอย่าง แล้วผมจะทำที่เหลือเอง" → pragmatic ที่สุด

---

## 💬 สรุปตรง ๆ

| คำถาม | คำตอบ |
|-------|-------|
| ครบถ้วนไหม? | ❌ ไม่ครบ — มีแต่ prompt spec ไม่มี code generator เต็ม |
| ใช้ได้จริงไหม? | ⚠️ ใช้เป็น *คู่มือ* ได้ แต่รันตรง ๆ ไม่ได้ |
| มีของที่ผิดไหม? | ✅ มี — `ports.py` ไม่มีจริง, deps ไม่ระบุ, alembic chain ผิด, vector type ขาด |
| ต้องแก้เท่าไหร่? | ขึ้นกับตัวเลือก A–E ด้านบน |

**ผมแนะนำ E** — ให้ผมเขียน `create_module_rag.py` เต็มไฟล์เดียว จบ-to-end รวม adapter wiring + env.py patch + postman + docs ทั้งหมด เป็นแม่แบบที่คุณ copy pattern ไปทำที่เหลือได้ ถ้า OK ผมเริ่มเลย — หรือบอก A/B/C/D ก็ได้ครับ
