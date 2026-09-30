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