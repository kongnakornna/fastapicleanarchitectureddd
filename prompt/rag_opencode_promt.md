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