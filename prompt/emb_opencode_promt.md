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