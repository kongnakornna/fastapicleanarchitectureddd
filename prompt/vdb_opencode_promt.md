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