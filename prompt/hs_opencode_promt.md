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