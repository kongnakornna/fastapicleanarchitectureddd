# 📚 คู่มือ LLM / RAG Solutions ฉบับ Production-Ready

> **เวอร์ชัน:** 1.0 · **ระดับ:** Intermediate → Advanced · **กลุ่มเป้าหมาย:** Backend Engineer, ML Engineer, Solution Architect
> **Stack:** Python 3.11+ · FastAPI · LangChain / LlamaIndex / Haystack · Qdrant / Pinecone / Weaviate / Milvus / Elasticsearch · Docker · AWS / Azure / GCP

---

## สารบัญ

1. [บทนำ](#1-บทนำ)
2. [บทนิยาม](#2-บทนิยาม)
3. [บทหัวข้อ (LLM / RAG)](#3-บทหัวข้อ-llm--rag)
4. [โครงสร้างระบบ](#4-โครงสร้างระบบ)
5. [DDD + Clean Architecture + Modular Design](#5-domain-driven-design-ddd--clean-architecture--modular-design)
6. [แนวทางการประยุกต์ใช้](#6-แนวทางการประยุกต์ใช้)
7. [Root Cause Analysis (RCA)](#7-root-cause-analysis-rca)
8. [การนำไปใช้งานจริง (Production)](#8-การนำไปใช้งานจริง-production)
9. [Prompt Templates Python](#9-prompt-templates-python)
10. [AI Skill Python](#10-ai-skill-python)
11. [ปัญหาและแนวทางแก้ไข](#11-ปัญหาและแนวทางแก้ไข)
12. [สรุป](#12-สรุป)

---

## 1. บทนำ

### 1.1 ทำไมต้องใช้ LLM + RAG?

ในโลกของ AI สำหรับองค์กร มี 2 คำถามใหญ่ที่ทีมวิศวกรต้องตอบพร้อมกัน:

| คำถาม | คำตอบแบบเดิม | คำตอบแบบ LLM + RAG |
|---|---|---|
| "โมเดลรู้ข้อมูลบริษัทเราไหม?" | ❌ ไม่รู้ (cutoff date) | ✅ รู้ (retrieve จาก knowledge base) |
| "โมเดล hallucinate ไหม?" | ⚠️ บ่อย | ✅ ลดได้ (grounded ด้วย context) |
| "Fine-tune แพงไปไหม?" | 💰 แพงมาก ($10k+) | ✅ ถูก (RAG ไม่ต้อง train) |
| "อัปเดตข้อมูลทำได้ไหม?" | ❌ ต้อง train ใหม่ | ✅ เปลี่ยนแค่ vector store |
| "ตรวจสอบที่มาได้ไหม?" | ❌ ไม่ได้ | ✅ ได้ (citation) |

**RAG (Retrieval-Augmented Generation)** = เทคนิคที่ทำให้ LLM ตอบคำถามจาก **ข้อมูลเฉพาะ** โดยไม่ต้อง fine-tune:

```
User Question
      │
      ▼
┌─────────────────┐    ┌──────────────┐    ┌──────────────┐
│ 1. Embed query  │───▶│ 2. Retrieve  │───▶│ 3. Augment   │
│   (Encoder)     │    │  (Vector DB) │    │  (Prompt)    │
└─────────────────┘    └──────────────┘    └──────────────┘
                                                    │
                                                    ▼
                                            ┌──────────────┐
                                            │ 4. Generate  │
                                            │    (LLM)     │
                                            └──────────────┘
                                                    │
                                                    ▼
                                            Grounded Answer
                                            + Citations
```

### 1.2 ขอบเขตของคู่มือ

คู่มือนี้ครอบคลุม:

- ✅ **แนวคิด** RAG Architecture, Embeddings, Vector Search, Prompt Engineering
- ✅ **Framework** LangChain, LlamaIndex, Haystack
- ✅ **API Development** FastAPI + Async
- ✅ **Vector DB** Qdrant, Pinecone, Weaviate, Milvus, Elasticsearch
- ✅ **Production Deployment** Docker, AWS/Azure/GCP
- ✅ **โค้ดพร้อมใช้** Prompt Templates, AI Skills, RCA Playbooks

**ไม่ครอบคลุม:** Fine-tuning, RLHF, Training from scratch, Model architecture

### 1.3 กลุ่มเป้าหมาย

| ระดับ | ต้องการอะไร |
|---|---|
| **Junior Backend** | โค้ดพร้อมใช้ + Best practices |
| **Mid-level** | Architecture patterns + Trade-offs |
| **Senior / Architect** | RCA, Security, Cost, Scale, Governance |
| **DevOps/SRE** | Docker, K8s, Observability, Rollback |

---

## 2. บทนิยาม

### 2.1 คำศัพท์พื้นฐาน

| คำ | ความหมาย | ตัวอย่าง |
|---|---|---|
| **LLM** | Large Language Model — โมเดลภาษาขนาดใหญ่ | GPT-4o, Claude 3.5, Llama 3.1 |
| **Embedding** | เวกเตอร์ที่แทนความหมายของข้อความ | `[0.123, -0.456, ...]` (1536 มิติ) |
| **Vector Store** | ฐานข้อมูลที่เก็บและค้นหา embedding | Qdrant, Pinecone, Weaviate |
| **Chunk** | ส่วนย่อยของเอกสารหลัง split | 512 tokens/ชิ้น |
| **Context Window** | จำนวน token สูงสุดที่ LLM รับได้ | 128k (GPT-4o) |
| **Token** | หน่วยย่อยของข้อความ (~4 ตัวอักษร EN) | "Hello" = 1 token |
| **Temperature** | ความสุ่มของ output (0=deterministic) | 0.0–2.0 |
| **Top-p** | Nucleus sampling (0=แคบ, 1=กว้าง) | 0.0–1.0 |
| **Hallucination** | LLM แต่งข้อมูลเท็จ | "กรุงเทพเป็นเมืองหลวงของญี่ปุ่น" |
| **Grounding** | การอ้างอิงข้อมูลจริง | อ้างจาก context ที่ retrieve มา |

### 2.2 คำศัพท์ RAG

| คำ | ความหมาย |
|---|---|
| **Retriever** | Component ที่ดึงเอกสารที่เกี่ยวข้อง |
| **Reranker** | เรียงลำดับผลลัพธ์ใหม่ด้วย cross-encoder |
| **Hybrid Search** | รวม dense (vector) + sparse (BM25) |
| **MMR** | Maximal Marginal Relevance — ลดความซ้ำซ้อน |
| **HyDE** | Hypothetical Document Embeddings — สร้าง doc สมมติก่อน retrieve |
| **Multi-Query** | สร้างหลาย query จาก query เดียว |
| **Parent-Child** | Child chunks สำหรับ retrieve, parent สำหรับ context |
| **Self-RAG** | LLM ตัดสินใจเองว่าต้อง retrieve ไหม |
| **CRAG** | Corrective RAG — ตรวจสอบคุณภาพ retrieval |

### 2.3 คำศัพท์ Infrastructure

| คำ | ความหมาย |
|---|---|
| **HNSW** | Hierarchical Navigable Small World — algorithm สำหรับ ANN |
| **IVF** | Inverted File Index — algorithm แบบ partition |
| **Quantization** | ลดขนาด vector (float32 → int8) |
| **pgvector** | Extension ของ PostgreSQL สำหรับ vector |
| **SSE** | Server-Sent Events — streaming protocol |
| **Backpressure** | กลไกป้องกัน overload |
| **Circuit Breaker** | กลไกตัดการเชื่อมต่อเมื่อ upstream fail |
| **Idempotency** | การรันซ้ำให้ผลเหมือนกัน |

---

## 3. บทหัวข้อ (LLM / RAG)

### 3.1 RAG คืออะไร

**RAG = Retrieval + Augmented + Generation**

- Retrieval (ริ-ทรี-วัล / /rɪˈtriːvəl/): แปลว่า การค้นคืนข้อมูล
- Augmented (อ็อก-เมน-ทิด / /ɔːɡˈmɛntɪd/): แปลว่า ซึ่งถูกเพิ่ม, เสริมแต่ง หรือขยาย
- Generation (เจน-เนอ-เร-ชัน / /ˌdʒɛnəˈreɪʃən/): แปลว่า การสร้างข้อความหรือผลลัพธ์
- RAG (แร็ก / /ræɡ/): ตัวย่อที่นิยมเรียกกัน อ่านออกเสียงว่า แร็ก  

แนวคิด: แทนที่จะให้ LLM ตอบจากความจำ (parametric memory) ให้ **ดึงข้อมูลที่เกี่ยวข้องมาใส่ prompt** (non-parametric memory) แล้วให้ LLM สรุปคำตอบ

```
┌─────────────────────────────────────────────────────────────┐
│                     RAG PIPELINE                            │
│                                                             │
│  ┌──────────┐    ┌─────────────┐    ┌───────────────────┐  │
│  │ Document │───▶│  Chunking   │───▶│  Embedding Model  │  │
│  │ Sources  │    │  (512 tok)  │    │ (text-embedding-3)│  │
│  └──────────┘    └─────────────┘    └───────────────────┘  │
│                                             │               │
│                                             ▼               │
│                                     ┌───────────────┐       │
│                                     │ Vector Store  │       │
│                                     │  (Qdrant)     │       │
│                                     └───────────────┘       │
│                                             ▲               │
│                                             │               │
│  ┌──────────┐    ┌─────────────┐    ┌──────────────┐      │
│  │  User    │───▶│  Query      │───▶│  Retrieve    │      │
│  │  Query   │    │  Embedding  │    │  Top-K       │      │
│  └──────────┘    └─────────────┘    └──────────────┘      │
│                                             │               │
│                                             ▼               │
│                                     ┌───────────────┐       │
│                                     │  Augment      │       │
│                                     │  Prompt       │       │
│                                     └───────────────┘       │
│                                             │               │
│                                             ▼               │
│                                     ┌───────────────┐       │
│                                     │  LLM Generate │       │
│                                     └───────────────┘       │
│                                             │               │
│                                             ▼               │
│                                     Grounded Answer        │
│                                     + Citations            │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 RAG ทำงานอย่างไร

#### 3.2.1 ขั้นตอน Indexing (Offline)

1. **Load** — อ่านเอกสาร (PDF, HTML, Markdown, DB)
2. **Clean** — ลบ header/footer/boilerplate
3. **Chunk** — แบ่งเป็นชิ้น 256–1024 tokens (overlap 10–20%)
4. **Embed** — แปลง chunk เป็นเวกเตอร์ (1536 dims)
5. **Upsert** — เก็บลง vector DB พร้อม metadata

#### 3.2.2 ขั้นตอน Retrieval (Online)

1. **Query Rewrite** — ปรับ query ให้ชัดเจนขึ้น
2. **Embed Query** — แปลง query เป็นเวกเตอร์
3. **Search** — ค้นหา top-K (cosine similarity)
4. **Rerank** — เรียงใหม่ด้วย cross-encoder
5. **Filter** — กรองตาม metadata (tenant, date, tag)
6. **Compress** — สรุป/squeeze context

#### 3.2.3 ขั้นตอน Generation

1. **Build Prompt** — ประกอบ system + context + user query
2. **Guardrails** — ตรวจ input/output
3. **LLM Call** — sync หรือ streaming
4. **Parse** — ดึง structured output
5. **Cite** — ใส่ citation (source, page)
6. **Log** — token, cost, latency

#### 3.2.4 Sequence Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant API as FastAPI
    participant QP as Query Processor
    participant VS as Vector Store
    participant RR as Reranker
    participant LLM as LLM Provider
    participant DB as PostgreSQL

    U->>API: POST /chat {query}
    API->>QP: rewrite + guardrail
    QP->>VS: embed(query) → search(top_k=20)
    VS-->>QP: candidate chunks
    QP->>RR: rerank(candidates) → top_5
    RR-->>QP: ranked chunks
    QP->>LLM: prompt(system, context, query)
    LLM-->>QP: stream chunks
    QP-->>API: SSE chunks
    API-->>U: data: {delta}
    API->>DB: log(usage, message, conversation)
    API-->>U: data: [DONE]
```

### 3.3 การใช้งาน

#### 3.3.1 Use Cases ที่เหมาะกับ RAG

| Use Case | ตัวอย่าง | ทำไม RAG เหมาะ |
|---|---|---|
| **Customer Support** | Q&A จาก FAQ + คู่มือ | ข้อมูลเฉพาะ, ต้อง update บ่อย |
| **Enterprise Search** | ค้นหาใน Confluence/Notion | เอกสารเยอะ, ต้อง citation |
| **Legal Research** | ค้นหากฎหมาย/คำพิพากษา | ต้องแม่นยำ, อ้างอิงได้ |
| **Medical QA** | ตอบจาก clinical guidelines | ต้อง ground, ห้าม hallucinate |
| **Code Assistant** | ค้นหาใน internal codebase | context เฉพาะองค์กร |
| **Compliance** | ตรวจนโยบายบริษัท | audit trail จำเป็น |

#### 3.3.2 Use Cases ที่**ไม่**เหมาะกับ RAG

| Use Case | ควรใช้แทน |
|---|---|
| Classification ง่ายๆ | Fine-tuned BERT |
| Translation | NMT model เฉพาะทาง |
| Math/Reasoning ล้วน | Symbolic solver + LLM |
| Real-time stock price | Direct API call |
| Structured DB query | Text-to-SQL |

#### 3.3.3 ตัวอย่าง Code ขั้นต่ำ (Qdrant + OpenAI)

```python
# ═══════════════════════════════════════════════════════════════
# minimal_rag.py — RAG ขั้นต่ำ 20 บรรทัด
# ═══════════════════════════════════════════════════════════════
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from openai import OpenAI

client = QdrantClient(":memory:")     # in-memory สำหรับ demo
oai = OpenAI()

# ─── 1) Setup ────────────────────────────────────────────────
client.create_collection(
    collection_name="docs",
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
)

# ─── 2) Index ────────────────────────────────────────────────
docs = ["FastAPI is a modern Python web framework.",
        "Qdrant is a vector similarity search engine.",
        "RAG combines retrieval with generation."]

points = []
for i, text in enumerate(docs):
    vec = oai.embeddings.create(input=text, model="text-embedding-3-small").data[0].embedding
    points.append(PointStruct(id=i, vector=vec, payload={"text": text}))
client.upsert(collection_name="docs", points=points)

# ─── 3) Retrieve ─────────────────────────────────────────────
query = "What is FastAPI?"
q_vec = oai.embeddings.create(input=query, model="text-embedding-3-small").data[0].embedding
hits = client.search(collection_name="docs", query_vector=q_vec, limit=2)

# ─── 4) Generate ─────────────────────────────────────────────
context = "\n".join(h.payload["text"] for h in hits)
answer = oai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Answer using ONLY the context."},
        {"role": "user", "content": f"Context:\n{context}\n\nQ: {query}"},
    ],
).choices[0].message.content

print(answer)
# → "FastAPI is a modern Python web framework."
```

### 3.4 ข้อดีของ RAG

| ข้อดี | รายละเอียด |
|---|---|
| ✅ **ไม่ต้อง Train** | ใช้ LLM ที่มีอยู่ + vector store |
| ✅ **ข้อมูล Update ได้ทันที** | แค่ re-index เอกสารใหม่ |
| ✅ **ตรวจสอบได้ (Citation)** | รู้ว่าคำตอบมาจากไหน |
| ✅ **ลด Hallucination** | Grounding จาก context จริง |
| ✅ **Cost ต่ำ** | ถูกกว่า fine-tune 10–100x |
| ✅ **Privacy** | เก็บข้อมูลในองค์กรได้ |
| ✅ **Multi-tenant** | แยก collection/namespace |
| ✅ **ผสม Hybrid** | รวม keyword + semantic |
| ✅ **A/B Test ง่าย** | เปลี่ยน retriever ไม่กระทบ LLM |
| ✅ **Domain-specific** | ใช้กับทุกอุตสาหกรรม |

### 3.5 ข้อเสียของ RAG

| ข้อเสีย | รายละเอียด | Mitigation |
|---|---|---|
| ❌ **Retrieval Quality** | ถ้า retrieve ไม่โดน → ตอบผิด | Hybrid + reranker |
| ❌ **Chunk Boundary** | ตัดกลางประโยค → context หาย | Overlap + parent-child |
| ❌ **Latency สูง** | 2+ hops (embed + search + LLM) | Cache + parallel |
| ❌ **Token Cost** | Context ยาว → แพง | Context compression |
| ❌ **Context Window Limit** | ใส่ context ไม่ได้เกิน | Map-reduce, multi-hop |
| ❌ **Embedding Drift** | โมเดลใหม่ → ต้อง re-index | Pin version + versioning |
| ❌ **Complexity** | หลาย components | ใช้ framework (LangChain) |
| ❌ **Evaluation ยาก** | ไม่มี ground truth | RAGAS, TruLens |
| ❌ **Security** | Prompt injection | Guardrails + sanitize |
| ❌ **Stale Index** | ข้อมูลเก่า | Scheduled re-index |

### 3.6 ข้อควรระวัง / ข้อห้าม / ข้อจำกัด

#### 🚫 ข้อห้าม (Never Do)

```markdown
❌ ห้าม log prompt ที่มี PII / API key
❌ ห้ามเก็บ plaintext API key — ต้อง encrypt at rest
❌ ห้ามใช้ temperature สูงกับงานที่ต้อง deterministic
❌ ห้ามใส่ context ยาวเกิน context window
❌ ห้าม query ข้าม tenant
❌ ห้าม trust user input โดยไม่ sanitize
❌ ห้าม retry เกิน 3 ครั้ง (จะทำให้ cost พุ่ง)
❌ ห้ามใช้ float กับค่าใช้จ่าย — ใช้ Decimal
❌ ห้าม block event loop ใน streaming
❌ ห้าม deploy โดยไม่มี rate limit
```

#### ⚠️ ข้อควรระวัง (Be Careful)

| หัวข้อ | ความเสี่ยง | แนวทาง |
|---|---|---|
| **Prompt Injection** | user ฝังคำสั่งใน query | Guardrails, XML tags |
| **Data Leakage** | retrieve ข้าม tenant | RLS + metadata filter |
| **Cost Explosion** | token บาน | Budget + alerts |
| **Cold Start** | vector DB ใหม่ช้า | Warmup + replica |
| **Rate Limit** | ชน provider limit | Queue + backoff |
| **Version Drift** | embedding model เปลี่ยน | Pin version |
| **Cache Poisoning** | cache key ชนกัน | Hash รวม tenant+model |
| **Silent Failure** | 吞 error | Structured logging |

#### 📏 ข้อจำกัด (Hard Limits)

| Resource | ขีดจำกัดทั่วไป |
|---|---|
| Context window | 4k–200k tokens |
| Output tokens | 1k–16k |
| Embedding dims | 384–3072 |
| Qdrant collection | ~10M vectors/node |
| Pinecone index | 5M vectors (starter) |
| OpenAI RPM | 500–10,000 (tier) |
| Latency p95 | 3–10s (non-stream) |
| Concurrent requests | 100–1000 |

### 3.7 สรุปบทหัวข้อ

- **RAG** = Retrieval + Augmentation + Generation
- **ใช้กับ** งานที่ต้องการข้อมูลเฉพาะ + citation + update บ่อย
- **หลีกเลี่ยง** งาน classification, translation, math
- **จุดเสี่ยงหลัก** retrieval quality, cost, security
- **ทางออก** hybrid search + reranker + guardrails + monitoring

---

## 4. โครงสร้างระบบ

### 4.1 โครงสร้างคืออะไร

**โครงสร้าง (Architecture)** = การจัดวาง components ของระบบให้ทำงานร่วมกัน โดยคำนึงถึง:
- **Separation of Concerns** — แต่ละส่วนมีความรับผิดชอบชัดเจน
- **Loose Coupling** — เปลี่ยน component ได้โดยไม่กระทบอื่น
- **Testability** — ทดสอบแยกส่วนได้
- **Scalability** — ขยายแนวนอน/แนวตั้งได้
- **Observability** — มองเห็นสถานะได้

### 4.2 โครงสร้างทำงานอย่างไร

#### 4.2.1 Layered Architecture (ชั้นสถาปัตยกรรม)

```
┌───────────────────────────────────────────────────────┐
│  PRESENTATION LAYER                                   │
│  • FastAPI Routers                                    │
│  • Pydantic Schemas                                   │
│  • SSE Streaming                                      │
├───────────────────────────────────────────────────────┤
│  APPLICATION LAYER                                    │
│  • Use Cases (business logic)                         │
│  • Interfaces (ports)                                 │
│  • Mappers (DTO ↔ Domain)                             │
├───────────────────────────────────────────────────────┤
│  DOMAIN LAYER                                         │
│  • Entities · Value Objects · Enums                   │
│  • Domain Events · Domain Exceptions                  │
│  • Pure business rules (no I/O)                       │
├───────────────────────────────────────────────────────┤
│  INFRASTRUCTURE LAYER                                 │
│  • Repositories (SQLAlchemy)                          │
│  • Vector Store (Qdrant)                              │
│  • LLM Clients (OpenAI, Anthropic)                    │
│  • Cache (Redis) · Event Bus (Kafka)                  │
└───────────────────────────────────────────────────────┘
```

#### 4.2.2 RAG-Specific Components

```
┌─────────────────────────────────────────────────────────────┐
│                  RAG SYSTEM ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  INGESTION PIPELINE (Batch / Scheduled)               │ │
│  │  ┌────────┐  ┌───────┐  ┌───────┐  ┌────────────┐  │ │
│  │  │ Loader │─▶│ Clean │─▶│ Chunk │─▶│ Embedder   │  │ │
│  │  └────────┘  └───────┘  └───────┘  └────────────┘  │ │
│  │                                          │          │ │
│  │                                          ▼          │ │
│  │                                    ┌──────────┐     │ │
│  │                                    │ VectorDB │     │ │
│  │                                    └──────────┘     │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  QUERY PIPELINE (Online / Streaming)                  │ │
│  │  ┌──────┐  ┌─────────┐  ┌──────────┐  ┌──────────┐  │ │
│  │  │Query │─▶│ Embed   │─▶│ Retrieve │─▶│ Rerank   │  │ │
│  │  │Rewrite│  │ Query   │  │  Top-K   │  │ CrossEnc │  │ │
│  │  └──────┘  └─────────┘  └──────────┘  └──────────┘  │ │
│  │                                              │       │ │
│  │                                              ▼       │ │
│  │                                      ┌─────────────┐ │ │
│  │                                      │ Build Prompt│ │ │
│  │                                      └─────────────┘ │ │
│  │                                              │       │ │
│  │                                              ▼       │ │
│  │                                      ┌─────────────┐ │ │
│  │                                      │  LLM + SSE  │ │ │
│  │                                      └─────────────┘ │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  SUPPORTING SERVICES                                  │ │
│  │  Cache · Rate Limit · Idempotency · Audit · Metrics  │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 4.3 โครงสร้างการใช้งาน (Folder Layout)

```
fastapi-backend/
├── app/
│   ├── app.py                          # FastAPI app factory
│   ├── core/                           # Cross-cutting concerns
│   │   ├── config.py                   # Settings (pydantic-settings)
│   │   ├── db.py                       # SQLAlchemy engine
│   │   ├── cache.py                    # Redis client
│   │   ├── events.py                   # Kafka producer
│   │   ├── security.py                 # JWT, encryption
│   │   └── logging.py                  # structlog config
│   │
│   └── modules/
│       ├── llm/                        # ★ LLM Foundation
│       │   ├── domain/                 # Pure business rules
│       │   │   ├── entities/           # Provider, Model, Conversation...
│       │   │   ├── value_objects/      # ChatOptions, TokenUsage
│       │   │   ├── enums.py
│       │   │   ├── events.py
│       │   │   └── exceptions.py
│       │   ├── application/            # Use cases
│       │   │   ├── use_case.py
│       │   │   ├── interfaces.py
│       │   │   ├── mappers.py
│       │   │   └── utils.py
│       │   ├── infrastructure/         # Adapters
│       │   │   ├── models.py           # SQLAlchemy ORM
│       │   │   ├── provider_repository.py
│       │   │   ├── services.py         # OpenAI/Anthropic clients
│       │   │   └── caches.py
│       │   └── presentation/           # FastAPI
│       │       ├── router.py
│       │       ├── schemas.py
│       │       ├── dependencies.py
│       │       └── sse.py
│       │
│       └── rag/                        # ★ RAG Module
│           ├── domain/
│           │   ├── entities/           # Document, Chunk, Collection
│           │   ├── value_objects/      # Embedding, SearchQuery
│           │   └── enums.py
│           ├── application/
│           │   ├── ingest_use_case.py
│           │   ├── query_use_case.py
│           │   └── interfaces.py
│           ├── infrastructure/
│           │   ├── loaders/            # PDF, HTML, Markdown
│           │   ├── chunkers/           # Recursive, Semantic
│           │   ├── embedders/          # OpenAI, BGE, Cohere
│           │   ├── vector_stores/      # Qdrant, Pinecone, ...
│           │   └── rerankers/          # Cohere, BGE
│           └── presentation/
│               ├── router.py
│               └── schemas.py
│
├── db/migrations/
│   ├── V001__create_llm.sql
│   ├── V002__seed_llm.sql
│   ├── V003__rollback_llm.sql
│   └── V004__seed_llm_demo.sql
│
├── migrations/versions/
│   ├── pdpa_001_init.py
│   ├── iot_001_init.py
│   └── llm_001_add_llm_tables.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── property/
│   └── manual/
│
├── docs/
│   ├── README_llm.md
│   ├── API_llm.md
│   └── postman/llm.json
│
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .dockerignore
│
├── pyproject.toml
├── Makefile
└── README.md
```

### 4.4 สรุปโครงสร้าง

| Layer | หน้าที่ | ห้ามทำ |
|---|---|---|
| **Domain** | Business rules | ❌ import framework, I/O |
| **Application** | Orchestration | ❌ ผูก DB/HTTP |
| **Infrastructure** | Adapters | ❌ logic ธุรกิจ |
| **Presentation** | HTTP/SSE | ❌ logic ธุรกิจ |

---

## 5. Domain-Driven Design (DDD) + Clean Architecture + Modular Design

### 5.1 DDD (Domain-Driven Design)

**หลักการ:** โครงสร้างโค้ดควรสะท้อน **Ubiquitous Language** ของธุรกิจ

#### Strategic DDD

| Concept | ในระบบ LLM/RAG |
|---|---|
| **Bounded Context** | `llm`, `rag`, `agent`, `tools` |
| **Ubiquitous Language** | Provider, Model, Conversation, Chunk, Embedding |
| **Context Map** | `llm` ← `rag` ← `agent` |
| **Anti-Corruption Layer** | Mappers (domain ↔ ORM) |

#### Tactical DDD

| Building Block | ตัวอย่าง |
|---|---|
| **Entity** | `Conversation` (มี identity) |
| **Value Object** | `TokenUsage` (immutable, no id) |
| **Aggregate** | `Conversation` + `Message[]` |
| **Aggregate Root** | `Conversation` |
| **Domain Event** | `MessageSent`, `CompletionGenerated` |
| **Repository** | `ConversationRepository` |
| **Domain Service** | `CostCalculator` |

### 5.2 Clean Architecture

```
        ┌──────────────────────────────────────────┐
        │  Frameworks & Drivers  (FastAPI, ORM)    │  ← ชั้นนอกสุด
        ├──────────────────────────────────────────┤
        │  Interface Adapters    (Controllers)      │
        ├──────────────────────────────────────────┤
        │  Use Cases             (Application)      │
        ├──────────────────────────────────────────┤
        │  Entities              (Domain)           │  ← ชั้นในสุด
        └──────────────────────────────────────────┘
                    ▲
                    │ Dependency Rule: ชี้ออกจากในออกนอกเท่านั้น
```

**กฎ:** ชั้นใน **ห้ามรู้จัก** ชั้นนอก · ใช้ interface (port) ที่ชั้นใน แล้ว implement ที่ชั้นนอก

### 5.3 Modular Software Design

**หลักการ:** Module ควรเป็น **Bounded Context** ที่:
- มี public API ชัดเจน (`__init__.py` re-export)
- ซ่อน internal details (underscore prefix)
- สื่อสารผ่าน contract (interface / event)
- Deploy แยกได้ (ถ้าจำเป็น)

**Module contract ตัวอย่าง:**

```python
# app/modules/llm/__init__.py
"""TH: Public API ของ llm module | EN: llm module public API"""
from app.modules.llm.presentation.router import router as llm_router
from app.modules.llm.application.use_case import LLMUseCase
from app.modules.llm.application.interfaces import RequestContext

__all__ = ["llm_router", "LLMUseCase", "RequestContext"]
```

### 5.4 ตัวอย่างจริง: LLM + RAG Module

#### 5.4.1 RAG Domain Entities

```python
# app/modules/rag/domain/entities/document.py
"""TH: Entity Document | EN: Document entity"""
from __future__ import annotations
import uuid
from datetime import UTC, datetime
from pydantic import BaseModel, ConfigDict, Field


class Document(BaseModel):
    """TH: เอกสารต้นทาง | EN: source document"""
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID
    collection_id: uuid.UUID
    source_uri: str = Field(min_length=1, max_length=2000)
    mime_type: str = "text/plain"
    size_bytes: int = Field(default=0, ge=0)
    checksum: str = ""
    status: str = "PENDING"  # PENDING → INDEXED → FAILED
    chunk_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
```

```python
# app/modules/rag/domain/value_objects/embedding.py
"""TH: Value Object Embedding | EN: Embedding VO"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Final

EMBEDDING_DIM: Final[int] = 1536


@dataclass(frozen=True, slots=True)
class Embedding:
    """TH: เวกเตอร์ฝังตัว | EN: embedding vector"""
    vector: tuple[float, ...]
    model: str
    dim: int = EMBEDDING_DIM

    def __post_init__(self) -> None:
        if len(self.vector) != self.dim:
            raise ValueError(f"expected {self.dim} dims, got {len(self.vector)}")
```

#### 5.4.2 RAG Application (Use Case)

```python
# app/modules/rag/application/query_use_case.py
"""TH: RAG query use case | EN: RAG query use case"""
from __future__ import annotations
import logging
import uuid
from typing import Any, AsyncIterator

from app.modules.llm.application.use_case import LLMUseCase
from app.modules.rag.application.interfaces import (
    Embedder, VectorStore, Reranker, RequestContext,
)

logger = logging.getLogger(__name__)


class RAGQueryUseCase:
    """TH: Use case หลักของ RAG | EN: core RAG use case"""

    def __init__(
        self,
        *,
        embedder: Embedder,
        vector_store: VectorStore,
        reranker: Reranker | None,
        llm: LLMUseCase,
        top_k: int = 20,
        top_n: int = 5,
    ) -> None:
        self._embedder = embedder
        self._store = vector_store
        self._reranker = reranker
        self._llm = llm
        self._top_k = top_k
        self._top_n = top_n

    async def query(
        self,
        ctx: RequestContext,
        *,
        question: str,
        model: str = "gpt-4o-mini",
        collection_ids: list[uuid.UUID] | None = None,
    ) -> dict[str, Any]:
        """TH: 3-branch: DomainError → AppError → Exception"""
        try:
            # 1) embed query
            q_vec = await self._embedder.embed(question)

            # 2) retrieve candidates
            hits = await self._store.search(
                ctx, q_vec,
                top_k=self._top_k,
                collection_ids=collection_ids,
            )

            # 3) rerank (optional)
            if self._reranker and hits:
                hits = await self._reranker.rerank(question, hits, top_n=self._top_n)
            else:
                hits = hits[: self._top_n]

            # 4) build context
            context = "\n\n---\n\n".join(
                f"[{i+1}] {h.text}" for i, h in enumerate(hits)
            )

            # 5) generate via LLM module
            result = await self._llm.chat(
                ctx,
                conversation_id=None,
                model_name=model,
                user_message=question,
                system_prompt=(
                    "You are a helpful assistant. Answer ONLY from the context.\n"
                    "If the answer is not in the context, say: 'ไม่พบข้อมูลในเอกสาร'\n"
                    "Cite sources as [1], [2], ...\n\n"
                    f"CONTEXT:\n{context}"
                ),
            )

            return {
                **result,
                "citations": [
                    {"id": i + 1, "source": h.source, "score": h.score}
                    for i, h in enumerate(hits)
                ],
                "chunks_retrieved": len(hits),
            }
        except Exception:
            logger.exception("rag.query failed")
            raise
```

#### 5.4.3 Vector Store Adapters (Multi-provider)

```python
# app/modules/rag/infrastructure/vector_stores/factory.py
"""TH: Factory เลือก vector store ตาม config | EN: Vector store factory"""
from __future__ import annotations
from enum import Enum
from typing import Any


class VectorStoreKind(str, Enum):
    QDRANT = "qdrant"
    PINECONE = "pinecone"
    WEAVIATE = "weaviate"
    MILVUS = "milvus"
    ELASTICSEARCH = "elasticsearch"
    PGVECTOR = "pgvector"


def make_vector_store(kind: VectorStoreKind, **cfg: Any):
    """TH: สร้าง vector store ตาม kind | EN: build vector store"""
    if kind == VectorStoreKind.QDRANT:
        from app.modules.rag.infrastructure.vector_stores.qdrant_store import QdrantStore
        return QdrantStore(**cfg)
    if kind == VectorStoreKind.PINECONE:
        from app.modules.rag.infrastructure.vector_stores.pinecone_store import PineconeStore
        return PineconeStore(**cfg)
    if kind == VectorStoreKind.WEAVIATE:
        from app.modules.rag.infrastructure.vector_stores.weaviate_store import WeaviateStore
        return WeaviateStore(**cfg)
    if kind == VectorStoreKind.MILVUS:
        from app.modules.rag.infrastructure.vector_stores.milvus_store import MilvusStore
        return MilvusStore(**cfg)
    if kind == VectorStoreKind.ELASTICSEARCH:
        from app.modules.rag.infrastructure.vector_stores.es_store import ESStore
        return ESStore(**cfg)
    if kind == VectorStoreKind.PGVECTOR:
        from app.modules.rag.infrastructure.vector_stores.pgvector_store import PGVectorStore
        return PGVectorStore(**cfg)
    raise ValueError(f"unknown vector store: {kind}")
```

### 5.5 สรุป DDD + Clean + Modular

| หลักการ | ประโยชน์ |
|---|---|
| **DDD** | โค้ดตรงกับธุรกิจ, คุยกับ stakeholder รู้เรื่อง |
| **Clean Arch** | เปลี่ยน tech ได้, test ง่าย |
| **Modular** | แยก deploy, ลด coupling |
| **Ports & Adapters** | รองรับ multi-provider |
| **Event-Driven** | Async, scalable, decoupled |

---

## 6. แนวทางการประยุกต์ใช้

### 6.1 Framework Selection Matrix

| Framework | จุดเด่น | จุดอ่อน | เหมาะกับ |
|---|---|---|---|
| **LangChain** | Ecosystem ใหญ่, integrations เยอะ | API เปลี่ยนบ่อย, verbose | Prototype เร็ว, งาน general |
| **LlamaIndex** | RAG-first, indexing ดี, query engine หลากหลาย | Ecosystem เล็กกว่า | งาน RAG จริงจัง |
| **Haystack** | Production-ready, pipeline ชัดเจน | community เล็ก | Enterprise, on-prem |
| **Custom** | ควบคุมเต็มที่, ไม่มี dependency | ใช้เวลาเยอะ | Performance-critical |

### 6.2 เลือก Vector DB

| Vector DB | โฮสต์ | จุดเด่น | จุดอ่อน | เหมาะกับ |
|---|---|---|---|---|
| **Qdrant** | Self / Cloud | Rust เร็ว, filter ดี, RLS | ecosystem เล็กกว่า | Production ทั่วไป |
| **Pinecone** | Managed | ไม่ต้องดูแล, เร็ว | แพง, vendor lock-in | Startup, MVP |
| **Weaviate** | Self / Cloud | Schema-first, hybrid search | หนัก | ต้องการ hybrid |
| **Milvus** | Self | Scale ใหญ่ (B+), GPU | Setup ซับซ้อน | Big data |
| **Elasticsearch** | Self / Cloud | Hybrid, mature | Vector search ใหม่กว่า | มี ES อยู่แล้ว |
| **pgvector** | Self | ใช้ Postgres เดิม | Scale จำกัด | ข้อมูล < 1M vectors |

### 6.3 Embedding Model Selection

| Model | Dim | Provider | จุดเด่น |
|---|---|---|---|
| `text-embedding-3-small` | 1536 | OpenAI | ถูก, เร็ว, ดีพอ |
| `text-embedding-3-large` | 3072 | OpenAI | แม่นกว่า, แพงกว่า |
| `voyage-3` | 1024 | Voyage | SOTA, ดีกับ RAG |
| `bge-large-en-v1.5` | 1024 | BAAI | ฟรี, self-host |
| `multilingual-e5-large` | 1024 | Microsoft | หลายภาษา, ฟรี |
| `cohere-embed-v3` | 1024 | Cohere | Multilingual |

### 6.4 Chunking Strategies

```python
# app/modules/rag/infrastructure/chunkers/strategies.py
"""TH: กลยุทธ์การแบ่ง chunk | EN: chunking strategies"""
from __future__ import annotations
from typing import Any


def recursive_chunk(
    text: str,
    *,
    chunk_size: int = 512,
    overlap: int = 64,
    separators: list[str] | None = None,
) -> list[str]:
    """TH: แบ่งตาม separator แบบ recursive | EN: recursive chunking"""
    seps = separators or ["\n\n", "\n", ". ", " ", ""]
    if len(text) <= chunk_size:
        return [text] if text.strip() else []

    for sep in seps:
        if sep in text:
            parts = text.split(sep)
            chunks: list[str] = []
            buf = ""
            for p in parts:
                candidate = (buf + sep + p) if buf else p
                if len(candidate) <= chunk_size:
                    buf = candidate
                else:
                    if buf:
                        chunks.append(buf)
                    buf = p
            if buf:
                chunks.append(buf)
            # add overlap
            if overlap > 0 and len(chunks) > 1:
                overlapped: list[str] = [chunks[0]]
                for i in range(1, len(chunks)):
                    prev_tail = chunks[i - 1][-overlap:]
                    overlapped.append(prev_tail + chunks[i])
                return overlapped
            return chunks
    return [text]


def semantic_chunk(
    text: str, embed_fn, *, threshold: float = 0.75, max_size: int = 1024,
) -> list[str]:
    """TH: แบ่งตามความหมาย (ต้องใช้ embedder) | EN: semantic chunking"""
    import numpy as np
    sentences = [s.strip() for s in text.replace("\n", " ").split(". ") if s.strip()]
    if len(sentences) <= 1:
        return [text] if text.strip() else []

    embeddings = np.array([embed_fn(s) for s in sentences])
    # cosine similarity ระหว่างประโยคข้างเคียง
    sims = []
    for i in range(len(embeddings) - 1):
        a, b = embeddings[i], embeddings[i + 1]
        sim = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))
        sims.append(sim)

    chunks: list[str] = []
    current = [sentences[0]]
    for i, sim in enumerate(sims):
        if sim < threshold or len(" ".join(current)) >= max_size:
            chunks.append(" ".join(current))
            current = [sentences[i + 1]]
        else:
            current.append(sentences[i + 1])
    if current:
        chunks.append(" ".join(current))
    return chunks
```

### 6.5 Retrieval Strategies

| Strategy | คำอธิบาย | เหมาะกับ |
|---|---|---|
| **Dense** | vector similarity เท่านั้น | semantic ทั่วไป |
| **Sparse (BM25)** | keyword-based | คำเฉพาะ, code |
| **Hybrid** | dense + sparse รวมกัน | production ทั่วไป |
| **Multi-Query** | สร้างหลาย query | query สั้น/กำกวม |
| **HyDE** | สร้าง hypothetical doc | query ยาก |
| **Parent-Child** | child retrieve, parent context | เอกสารยาว |
| **Self-RAG** | LLM ตัดสินใจ retrieve | ลด latency |
| **Contextual Compression** | ย่อ context ก่อนส่ง | ประหยัด token |

### 6.6 Deployment Patterns

| Pattern | จุดเด่น | จุดอ่อน |
|---|---|---|
| **Monolith** | ง่าย, deploy เดียว | scale ยาก |
| **Modular Monolith** | แยก module, deploy เดียว | ยังต้อง scale พร้อมกัน |
| **Microservices** | scale แยก, tech ต่างกันได้ | ซับซ้อน, network overhead |
| **Serverless** | จ่ายตามใช้, auto-scale | cold start, timeout |
| **Hybrid** | monolith + async workers | ต้องมี queue |

### 6.7 เปรียบเทียบ Cloud Platform

| Platform | Managed Vector | LLM Service | เหมาะกับ |
|---|---|---|---|
| **AWS** | OpenSearch, Aurora pgvector | Bedrock | Enterprise, compliance |
| **Azure** | AI Search, Cosmos DB | Azure OpenAI | M365, enterprise |
| **GCP** | Vertex AI Vector Search | Vertex AI | Data/ML-heavy |

---

## 7. Root Cause Analysis (RCA)

### 7.1 RCA คืออะไร

**RCA** = กระบวนการหาต้นตอที่แท้จริงของปัญหา แทนการแก้อาการ

### 7.2 เครื่องมือ RCA

#### 7.2.1 5 Whys

```
ปัญหา: RAG ตอบผิดบ่อย
├─ Why 1: Context ที่ retrieve ไม่ตรง
├─ Why 2: Embedding model แปลกภาษาไทยไม่ดี
├─ Why 3: ใช้ text-embedding-3-small (EN-centric)
├─ Why 4: ทีมเลือกเพราะราคาถูก
└─ Why 5: ไม่มีการประเมิน multilingual benchmark
   → ROOT: ไม่มี evaluation pipeline ก่อนเลือก model
```

#### 7.2.2 Fishbone Diagram

```
        ┌── People ────────┐
        │ ไม่มี owner       │
        │ ขาด eval          │
        └───────────────────┘
                              ┌── Method ─────────┐
                              │ chunk 512 ตายตัว  │
                              │ ไม่มี reranker    │
                              └───────────────────┘
Problem:──────────────────────────────────────────────▶
RAG ตอบผิด                     ┌── Machine ────────┐
                              │ embedding model   │
                              │ ไม่เหมาะกับภาษา   │
                              └───────────────────┘
                              ┌── Material ───────┐
                              │ เอกสารไม่มี 구조  │
                              │ OCR อ่านผิด       │
                              └───────────────────┘
```

#### 7.2.3 Fault Tree Analysis (FTA)

```
        RAG ตอบผิด (Top Event)
              │
      ┌───────┴───────┐
      │               │
   Retrieval      Generation
    Fail            Fail
      │               │
   ┌──┴──┐        ┌──┴──┐
   │     │        │     │
 Embed  Chunk   Prompt  LLM
 bad    bad     bad     hallucinate
```

### 7.3 RCA Playbook — RAG Cases

#### Case 1: Retrieval ไม่ตรง

```markdown
**อาการ:** retrieve แล้วได้เอกสารไม่เกี่ยวข้อง

**RCA:**
1. **Embedding model ไม่เหมาะ** → ลอง multilingual-e5
2. **Chunk size ผิด** → ปรับเป็น 256–1024 ตาม content
3. **ไม่มี reranker** → เพิ่ม Cohere rerank / BGE rerank
4. **Metadata filter ขาด** → เพิ่ม tenant, lang, date
5. **Hybrid search ขาด** → ผสม BM25 + dense

**Fix priority:**
1. เพิ่ม reranker (ROI สูงสุด)
2. Hybrid search (ดึง keyword)
3. ปรับ chunk size + overlap
```

#### Case 2: Latency สูง

```markdown
**อาการ:** p95 > 8s

**RCA:**
1. **Retrieve + LLM แบบ serial** → parallelize (rerank + LLM)
2. **Embedding call block** → cache query embeddings
3. **Top-K สูงเกิน** → ลด top_k=10, top_n=3
4. **LLM response ยาว** → จำกัด max_tokens
5. **Cold start** → warmup + replica

**Fix:**
- Redis cache query + result
- Async pipeline
- Streaming (first token < 500ms)
```

#### Case 3: Cost พุ่ง

```markdown
**อาการ:** งบบาน 3x

**RCA:**
1. **Context ยาว** → ลด top_n, compression
2. **Cache miss** → cache key ผิด
3. **No retry cap** → จำกัด 3 ครั้ง
4. **Model แพงเกินจำเป็น** → gpt-4o-mini แทน gpt-4o
5. **Token counting ไม่แม่น** → tiktoken + audit

**Fix:**
- Budget alerts (Slack)
- Cost dashboard per tenant
- Model routing (cheap first)
```

#### Case 4: Hallucination

```markdown
**อาการ:** ตอบด้วยข้อมูลที่ไม่มีใน context

**RCA:**
1. **Prompt ไม่ชัด** → ระบุ "Answer ONLY from context"
2. **Temperature สูง** → ลดเป็น 0.0–0.3
3. **Context ไม่พอ** → retrieve เพิ่ม top_n
4. **Model เก่งเกินไป** → ใช้ reasoning model
5. **ไม่มี citation** → บังคับ citation

**Fix:**
- Prompt template + citation guardrail
- Faithfulness evaluation (RAGAS)
- Fallback: "ไม่พบข้อมูล"
```

### 7.4 RCA Template (ใช้ซ้ำได้)

```markdown
# RCA Report

## 1. Problem Statement
- **What:** ...
- **When:** ...
- **Impact:** ...
- **Severity:** P0/P1/P2/P3

## 2. Timeline
- T0: ...
- T1: ...
- T2: ...

## 3. Root Cause (5 Whys)
1. Why: ...
2. Why: ...
...
5. ROOT: ...

## 4. Contributing Factors
- People: ...
- Process: ...
- Technology: ...

## 5. Corrective Actions
| # | Action | Owner | Deadline | Status |
|---|---|---|---|---|
| 1 | ... | ... | ... | ... |

## 6. Preventive Actions
- ...

## 7. Lessons Learned
- ...
```

---

## 8. การนำไปใช้งานจริง (Production)

### 8.1 Production Readiness Checklist

```markdown
## 🔒 Security
- [ ] API keys encrypt at rest (KMS/Vault)
- [ ] No prompt/PII in logs
- [ ] RLS enforced (5 tables)
- [ ] Input sanitization + guardrails
- [ ] Rate limit per tenant/user
- [ ] Idempotency-Key required for mutating endpoints
- [ ] HTTPS/TLS 1.3 only
- [ ] CORS allowlist

## 📊 Observability
- [ ] Structured logging (JSON)
- [ ] Metrics: latency, tokens, cost, errors
- [ ] Tracing: OpenTelemetry
- [ ] Dashboards: Grafana
- [ ] Alerts: p95 latency, error rate, cost
- [ ] Correlation ID propagation

## ⚙️ Reliability
- [ ] Retry with backoff (max 3)
- [ ] Circuit breaker (provider)
- [ ] Fallback provider
- [ ] Health check (/health, /ready)
- [ ] Graceful shutdown
- [ ] Zero-downtime deploy

## 💰 Cost
- [ ] Token budget per tenant
- [ ] Cost alerts
- [ ] Cache hit > 30%
- [ ] Model routing (cheap → expensive)
- [ ] Context compression

## 🧪 Testing
- [ ] Unit coverage ≥ 85%
- [ ] Integration (DB + vector store)
- [ ] Load test (k6, locust)
- [ ] Chaos test (provider down)
- [ ] Evaluation (RAGAS)

## 📦 Deployment
- [ ] Docker image multi-stage
- [ ] Non-root user
- [ ] Healthchecks
- [ ] Config via env
- [ ] Secrets via K8s Secret / AWS Secrets Manager
- [ ] Blue-green / canary
- [ ] Rollback plan
```

### 8.2 Dockerfile (Multi-stage)

```dockerfile
# docker/Dockerfile
# ═══════════════════════════════════════════════════════════════
# Stage 1: Builder
# ═══════════════════════════════════════════════════════════════
FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential curl git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv==0.4.*

# Copy dependency files
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# ═══════════════════════════════════════════════════════════════
# Stage 2: Runtime
# ═══════════════════════════════════════════════════════════════
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# Non-root user
RUN groupadd --gid 1000 app && \
    useradd --uid 1000 --gid app --shell /bin/bash --create-home app

WORKDIR /app

# Copy venv from builder
COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Copy app code
COPY --chown=app:app app/ ./app/
COPY --chown=app:app migrations/ ./migrations/
COPY --chown=app:app pyproject.toml ./

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "4", "--loop", "uvloop", "--access-log"]
```

### 8.3 docker-compose.yml (Local Dev)

```yaml
# docker/docker-compose.yml
version: "3.9"

services:
  api:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:postgres@postgres:5432/ioterp
      REDIS_URL: redis://redis:6379/0
      QDRANT_URL: http://qdrant:6333
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      ENV: development
    depends_on:
      postgres: { condition: service_healthy }
      redis: { condition: service_healthy }
      qdrant: { condition: service_started }
    volumes:
      - ../app:/app/app:ro
    command: uvicorn app.app:app --host 0.0.0.0 --port 8000 --reload

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: ioterp
    ports: ["5432:5432"]
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ../db/migrations:/docker-entrypoint-initdb.d:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 5

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"  # HTTP
      - "6334:6334"  # gRPC
    volumes:
      - qdrant_data:/qdrant/storage

  kafka:
    image: bitnami/kafka:3.7
    ports: ["9092:9092"]
    environment:
      KAFKA_CFG_NODE_ID: 0
      KAFKA_CFG_PROCESS_ROLES: controller,broker
      KAFKA_CFG_LISTENERS: PLAINTEXT://:9092,CONTROLLER://:9093
      KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
      KAFKA_CFG_CONTROLLER_QUORUM_VOTERS: 0@kafka:9093
      KAFKA_CFG_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_CFG_AUTO_CREATE_TOPICS_ENABLE: "true"

volumes:
  pgdata:
  qdrant_data:
```

### 8.4 AWS Deployment (ECS Fargate)

```hcl
# infra/aws/ecs.tf
resource "aws_ecs_cluster" "main" {
  name = "llm-rag-cluster"
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_ecs_task_definition" "api" {
  family                   = "llm-rag-api"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "2048"
  memory                   = "4096"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name  = "api"
    image = "${aws_ecr_repository.api.repository_url}:${var.image_tag}"
    portMappings = [{ containerPort = 8000, protocol = "tcp" }]
    environment = [
      { name = "ENV", value = "production" },
      { name = "AWS_REGION", value = var.region },
    ]
    secrets = [
      { name = "DATABASE_URL", valueFrom = aws_secretsmanager_secret.db_url.arn },
      { name = "OPENAI_API_KEY", valueFrom = aws_secretsmanager_secret.openai_key.arn },
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.api.name
        "awslogs-region"        = var.region
        "awslogs-stream-prefix" = "api"
      }
    }
    healthCheck = {
      command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 30
    }
  }])
}

resource "aws_ecs_service" "api" {
  name            = "llm-rag-api"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = 3
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [aws_security_group.api.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name   = "api"
    container_port   = 8000
  }

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  deployment_controller { type = "ECS" }

  lifecycle {
    ignore_changes = [desired_count]
  }
}

# ─── Auto Scaling ────────────────────────────────
resource "aws_appautoscaling_target" "api" {
  max_capacity       = 20
  min_capacity       = 3
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.api.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "cpu" {
  name               = "cpu-target-tracking"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.api.resource_id
  scalable_dimension = aws_appautoscaling_target.api.scalable_dimension
  service_namespace  = aws_appautoscaling_target.api.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value       = 70.0
    scale_in_cooldown  = 60
    scale_out_cooldown = 30
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
  }
}
```

### 8.5 Kubernetes (Production)

```yaml
# infra/k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-rag-api
  namespace: llm
spec:
  replicas: 3
  selector:
    matchLabels: { app: llm-rag-api }
  strategy:
    type: RollingUpdate
    rollingUpdate: { maxSurge: 1, maxUnavailable: 0 }
  template:
    metadata:
      labels: { app: llm-rag-api }
    spec:
      serviceAccountName: llm-rag-api
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
        - name: api
          image: ghcr.io/org/llm-rag-api:1.0.0
          imagePullPolicy: IfNotPresent
          ports: [{ containerPort: 8000, name: http }]
          env:
            - name: ENV
              value: production
            - name: DATABASE_URL
              valueFrom: { secretKeyRef: { name: app-secrets, key: db-url } }
            - name: OPENAI_API_KEY
              valueFrom: { secretKeyRef: { name: app-secrets, key: openai-key } }
          resources:
            requests: { cpu: "500m", memory: "1Gi" }
            limits:   { cpu: "2000m", memory: "2Gi" }
          livenessProbe:
            httpGet: { path: /health, port: 8000 }
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet: { path: /ready, port: 8000 }
            initialDelaySeconds: 5
            periodSeconds: 5
          lifecycle:
            preStop:
              exec: { command: ["sh", "-c", "sleep 10"] }
---
apiVersion: v1
kind: Service
metadata:
  name: llm-rag-api
  namespace: llm
spec:
  selector: { app: llm-rag-api }
  ports:
    - port: 80
      targetPort: 8000
      name: http
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: llm-rag-api
  namespace: llm
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: llm-rag-api
  minReplicas: 3
  maxReplicas: 30
  metrics:
    - type: Resource
      resource: { name: cpu, target: { type: Utilization, averageUtilization: 70 } }
    - type: Pods
      pods:
        metric: { name: http_requests_per_second }
        target: { type: AverageValue, averageValue: "100" }
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 30
      policies: [{ type: Percent, value: 100, periodSeconds: 30 }]
    scaleDown:
      stabilizationWindowSeconds: 300
      policies: [{ type: Percent, value: 25, periodSeconds: 60 }]
```

### 8.6 CI/CD (GitHub Actions)

```yaml
# .github/workflows/deploy.yml
name: deploy
on:
  push:
    branches: [main]
  pull_request:

env:
  REGISTRY: ghcr.io
  IMAGE: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env: { POSTGRES_PASSWORD: postgres }
        ports: ["5432:5432"]
        options: >-
          --health-cmd pg_isready --health-interval 5s
          --health-timeout 5s --health-retries 5
      redis:
        image: redis:7-alpine
        ports: ["6379:6379"]
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv sync --frozen --all-extras
      - run: uv run ruff check .
      - run: uv run mypy app
      - run: uv run pytest -x --cov=app --cov-fail-under=85

  build-and-push:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    permissions: { contents: read, packages: write }
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          context: .
          file: docker/Dockerfile
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE }}:${{ github.sha }}
            ${{ env.REGISTRY }}/${{ env.IMAGE }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster llm-rag-cluster \
            --service llm-rag-api \
            --force-new-deployment
      - name: Wait for stable
        run: |
          aws ecs wait services-stable \
            --cluster llm-rag-cluster \
            --services llm-rag-api
```

---

## 9. Prompt Templates Python

### 9.1 RAG Prompt (Production-Ready)

```python
# app/modules/rag/prompts/rag_qa.py
"""TH: Prompt template สำหรับ RAG QA | EN: RAG QA prompt templates"""
from __future__ import annotations
from dataclasses import dataclass
from string import Template


@dataclass(frozen=True, slots=True)
class RAGPromptTemplate:
    """TH: เทมเพลตสำหรับ RAG QA | EN: RAG QA template"""
    system: str
    user: str
    citation_format: str = "[{n}]"


# ─── TH: system prompt แบบ strict (บังคับใช้ context เท่านั้น) ───
RAG_SYSTEM_STRICT = """You are a precise, grounded AI assistant.

## Rules (MUST FOLLOW)
1. Answer ONLY using information in the CONTEXT section.
2. If the answer is NOT in the context, respond EXACTLY:
   "ไม่พบข้อมูลในเอกสารที่ให้มา"
3. Cite every claim with [n] matching the context block number.
4. Never invent facts, URLs, names, or numbers.
5. If sources conflict, mention the discrepancy.
6. Keep answers concise (≤ 200 words unless asked otherwise).
7. Match the user's language (Thai ↔ English).

## Response Format
<answer>
Your grounded answer with [1], [2], ...
</answer>
<sources>
[1] <source title> — <page/line if available>
[2] ...
</sources>
"""

RAG_USER_TEMPLATE = Template("""## CONTEXT
$context

## QUESTION
$question

## ANSWER (cite sources):""")


def build_rag_prompt(
    question: str,
    context_chunks: list[dict],
    *,
    max_context_chars: int = 12000,
) -> list[dict[str, str]]:
    """TH: สร้าง prompt messages | EN: build RAG prompt messages"""
    # ─── format context พร้อม citation number ───
    parts: list[str] = []
    used = 0
    for i, c in enumerate(context_chunks, 1):
        text = c.get("text", "").strip()
        source = c.get("source", "unknown")
        page = c.get("page", "")
        header = f"[{i}] ({source}"
        if page:
            header += f", p.{page}"
        header += ")"
        block = f"{header}\n{text}"
        if used + len(block) > max_context_chars:
            break
        parts.append(block)
        used += len(block)

    context = "\n\n---\n\n".join(parts) if parts else "(no context found)"

    return [
        {"role": "system", "content": RAG_SYSTEM_STRICT},
        {"role": "user", "content": RAG_USER_TEMPLATE.substitute(
            context=context, question=question.strip(),
        )},
    ]
```

### 9.2 Query Rewriting (Multi-Query)

```python
# app/modules/rag/prompts/rewrite.py
"""TH: Query rewriting prompts | EN: Query rewriting prompts"""
from __future__ import annotations


REWRITE_SYSTEM = """You rewrite user questions into 3 diverse search queries.

## Rules
- Keep the original meaning.
- Vary vocabulary (synonyms, formal/informal).
- Output JSON: {"queries": ["...", "...", "..."]}
- Max 15 words per query.
- Match the input language.
"""


def build_rewrite_prompt(question: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": REWRITE_SYSTEM},
        {"role": "user", "content": f"Question: {question}\n\nJSON:"},
    ]


HYDE_SYSTEM = """Write a hypothetical 3-sentence document that WOULD answer the question.
Do not say you don't know. Just write the ideal answer as a passage.
Match the input language.
"""


def build_hyde_prompt(question: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": HYDE_SYSTEM},
        {"role": "user", "content": f"Question: {question}\n\nPassage:"},
    ]
```

### 9.3 Structured Output (JSON Mode)

```python
# app/modules/rag/prompts/structured.py
"""TH: Prompt templates สำหรับ structured output | EN: structured output"""
from __future__ import annotations
import json

EXTRACT_ENTITIES_SYSTEM = """Extract named entities from the text.

## Output Schema (STRICT JSON)
{
  "people":   [{"name": "...", "role": "..."}],
  "orgs":     ["..."],
  "dates":    ["YYYY-MM-DD"],
  "amounts":  [{"value": 0.0, "currency": "THB"}],
  "locations":["..."]
}

## Rules
- Return ONLY valid JSON. No prose.
- If a field is empty, use [].
- Do not invent entities.
"""


def build_extract_prompt(text: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": EXTRACT_ENTITIES_SYSTEM},
        {"role": "user", "content": f"```\n{text[:8000]}\n```"},
    ]


def parse_json_safe(raw: str) -> dict:
    """TH: parse JSON แบบปลอดภัย | EN: safe JSON parse"""
    raw = raw.strip()
    # strip markdown fence
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1]
        if raw.endswith("```"):
            raw = raw[:-3]
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # try to find first { ... }
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(raw[start:end + 1])
            except json.JSONDecodeError:
                pass
    return {}
```

### 9.4 Prompt Registry (Versioned)

```python
# app/modules/rag/prompts/registry.py
"""TH: Prompt registry แบบ versioned | EN: versioned prompt registry"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Callable

from app.modules.rag.prompts import rag_qa, rewrite, structured


@dataclass(frozen=True, slots=True)
class Prompt:
    """TH: prompt 1 รายการ | EN: single prompt entry"""
    id: str
    version: str
    description: str
    builder: Callable[..., list[dict[str, str]]]
    tags: tuple[str, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


_REGISTRY: dict[str, Prompt] = {}


def register(p: Prompt) -> None:
    """TH: ลงทะเบียน prompt | EN: register prompt"""
    key = f"{p.id}@{p.version}"
    if key in _REGISTRY:
        raise ValueError(f"prompt {key} already registered")
    _REGISTRY[key] = p


def get(prompt_id: str, version: str = "latest") -> Prompt:
    """TH: ดึง prompt | EN: get prompt"""
    if version == "latest":
        candidates = sorted(k for k in _REGISTRY if k.startswith(f"{prompt_id}@"))
        if not candidates:
            raise KeyError(f"prompt {prompt_id} not found")
        return _REGISTRY[candidates[-1]]
    return _REGISTRY[f"{prompt_id}@{version}"]


def all_prompts() -> list[Prompt]:
    """TH: list prompts ทั้งหมด | EN: list all prompts"""
    return list(_REGISTRY.values())


# ─── Bootstrap ──────────────────────────────────────────
register(Prompt(
    id="rag.qa", version="v1.0.0",
    description="RAG QA strict grounding with citations",
    builder=rag_qa.build_rag_prompt,
    tags=("rag", "qa", "strict"),
))
register(Prompt(
    id="rag.rewrite", version="v1.0.0",
    description="Multi-query rewriting (3 queries, JSON)",
    builder=rewrite.build_rewrite_prompt,
    tags=("rag", "rewrite"),
))
register(Prompt(
    id="rag.hyde", version="v1.0.0",
    description="HyDE hypothetical document",
    builder=rewrite.build_hyde_prompt,
    tags=("rag", "hyde"),
))
register(Prompt(
    id="extract.entities", version="v1.0.0",
    description="Named entity extraction (JSON)",
    builder=structured.build_extract_prompt,
    tags=("extraction", "json"),
))
```

### 9.5 Prompt Testing (Regression)

```python
# tests/prompts/test_prompt_regression.py
"""TH: ทดสอบ prompt แบบ regression | EN: prompt regression tests"""
from __future__ import annotations
import pytest

from app.modules.rag.prompts import rag_qa


def test_rag_prompt_structure() -> None:
    msgs = rag_qa.build_rag_prompt(
        "What is RAG?",
        [{"text": "RAG is Retrieval-Augmented Generation.", "source": "doc1"}],
    )
    assert len(msgs) == 2
    assert msgs[0]["role"] == "system"
    assert "ONLY" in msgs[0]["content"]
    assert "[1]" in msgs[1]["content"]


def test_rag_prompt_max_context() -> None:
    big = [{"text": "x" * 5000, "source": f"doc{i}"} for i in range(10)]
    msgs = rag_qa.build_rag_prompt("q", big, max_context_chars=8000)
    assert len(msgs[1]["content"]) < 10000


def test_rag_prompt_empty_context() -> None:
    msgs = rag_qa.build_rag_prompt("q", [])
    assert "(no context found)" in msgs[1]["content"]
```

---

## 10. AI Skill Python

**"AI Skill"** = ความสามารถที่ห่อหุ้มไว้ใน Python module เพื่อ reuse ใน agent/workflow

### 10.1 Skill Interface

```python
# app/modules/agent/skills/base.py
"""TH: Base skill interface | EN: base skill interface"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class SkillContext:
    """TH: context ของ skill | EN: skill context"""
    tenant_id: str
    user_id: str | None
    conversation_id: str | None
    metadata: dict[str, Any]


@dataclass(frozen=True, slots=True)
class SkillResult:
    """TH: ผลลัพธ์ | EN: skill result"""
    success: bool
    output: Any = None
    error: str | None = None
    tokens_used: int = 0
    latency_ms: int = 0


class BaseSkill(ABC):
    """TH: base class ของ AI skill | EN: AI skill base"""

    name: str = "base"
    description: str = ""
    version: str = "1.0.0"
    parameters: dict[str, Any] = {}

    @abstractmethod
    async def execute(
        self, ctx: SkillContext, **kwargs: Any,
    ) -> SkillResult:
        """TH: รัน skill | EN: execute skill"""
        ...
```

### 10.2 ตัวอย่าง Skills

#### Skill 1: RAG QA

```python
# app/modules/agent/skills/rag_qa.py
"""TH: Skill: RAG QA | EN: RAG QA skill"""
from __future__ import annotations
import time
from typing import Any

from app.modules.agent.skills.base import BaseSkill, SkillContext, SkillResult
from app.modules.rag.application.query_use_case import RAGQueryUseCase


class RAGQASkill(BaseSkill):
    """TH: ตอบคำถามจาก knowledge base | EN: answer from knowledge base"""

    name = "rag_qa"
    description = "Answer questions using retrieval-augmented generation."
    parameters = {
        "question": {"type": "string", "required": True},
        "collection_ids": {"type": "array", "items": "uuid", "required": False},
        "model": {"type": "string", "default": "gpt-4o-mini"},
    }

    def __init__(self, use_case: RAGQueryUseCase) -> None:
        self._uc = use_case

    async def execute(
        self, ctx: SkillContext, **kwargs: Any,
    ) -> SkillResult:
        t0 = time.monotonic()
        try:
            result = await self._uc.query(
                ctx=ctx,
                question=kwargs["question"],
                model=kwargs.get("model", "gpt-4o-mini"),
                collection_ids=kwargs.get("collection_ids"),
            )
            return SkillResult(
                success=True,
                output=result,
                tokens_used=result.get("usage", {}).get("total_tokens", 0),
                latency_ms=int((time.monotonic() - t0) * 1000),
            )
        except Exception as exc:  # noqa: BLE001
            return SkillResult(
                success=False, error=str(exc),
                latency_ms=int((time.monotonic() - t0) * 1000),
            )
```

#### Skill 2: SQL Query (Text-to-SQL)

```python
# app/modules/agent/skills/text_to_sql.py
"""TH: Skill: Text-to-SQL | EN: text-to-sql skill"""
from __future__ import annotations
import time
from typing import Any

from app.modules.agent.skills.base import BaseSkill, SkillContext, SkillResult
from app.modules.llm.application.use_case import LLMUseCase


SQL_SYSTEM = """You write PostgreSQL SELECT queries.

## Schema
- public.llm_providers(id, tenant_id, name, provider_type, is_active)
- public.llm_models(id, name, provider_id, cost_per_1k_input, cost_per_1k_output)
- public.llm_conversations(id, user_id, model_id, status, total_tokens)
- public.llm_usage_logs(id, tenant_id, user_id, cost_usd, created_at)

## Rules
- Output ONE SELECT query. No DDL/DML.
- Always filter by tenant_id = :tenant_id.
- Use LIMIT 100.
- Return JSON: {"sql": "..."}
"""


class TextToSQLSkill(BaseSkill):
    name = "text_to_sql"
    description = "Convert natural language to safe SQL SELECT."
    parameters = {
        "question": {"type": "string", "required": True},
    }

    def __init__(self, llm: LLMUseCase) -> None:
        self._llm = llm

    async def execute(
        self, ctx: SkillContext, **kwargs: Any,
    ) -> SkillResult:
        t0 = time.monotonic()
        try:
            result = await self._llm.chat(
                ctx=ctx, conversation_id=None,
                model_name="gpt-4o-mini",
                user_message=kwargs["question"],
                system_prompt=SQL_SYSTEM,
            )
            # ★ CRITICAL: sanitize SQL ก่อน execute
            sql = self._extract_sql(result.get("content", ""))
            if not self._is_safe(sql):
                return SkillResult(
                    success=False, error="unsafe SQL rejected",
                )
            return SkillResult(
                success=True,
                output={"sql": sql},
                tokens_used=result.get("usage", {}).get("total_tokens", 0),
                latency_ms=int((time.monotonic() - t0) * 1000),
            )
        except Exception as exc:  # noqa: BLE001
            return SkillResult(
                success=False, error=str(exc),
                latency_ms=int((time.monotonic() - t0) * 1000),
            )

    @staticmethod
    def _extract_sql(raw: str) -> str:
        import json
        try:
            return json.loads(raw).get("sql", "").strip()
        except Exception:
            return raw.strip()

    @staticmethod
    def _is_safe(sql: str) -> bool:
        """TH: whitelist SELECT เท่านั้น | EN: allow SELECT only"""
        s = sql.strip().lower()
        if not s.startswith("select"):
            return False
        forbidden = ["insert", "update", "delete", "drop", "alter",
                     "truncate", "grant", "revoke", "--", ";--"]
        return not any(w in s for w in forbidden)
```

#### Skill 3: Summarize

```python
# app/modules/agent/skills/summarize.py
"""TH: Skill: สรุปเอกสาร | EN: summarization skill"""
from __future__ import annotations
import time
from typing import Any

from app.modules.agent.skills.base import BaseSkill, SkillContext, SkillResult
from app.modules.llm.application.use_case import LLMUseCase


SUMMARY_SYSTEM = """Summarize the text. Output format:
<summary>
- Key point 1
- Key point 2
- ...
</summary>
<one_line>One-sentence TL;DR</one_line>
Match the input language. Max 5 bullets.
"""


class SummarizeSkill(BaseSkill):
    name = "summarize"
    description = "Summarize long text into bullets + TL;DR."
    parameters = {
        "text": {"type": "string", "required": True},
        "max_bullets": {"type": "integer", "default": 5},
    }

    def __init__(self, llm: LLMUseCase) -> None:
        self._llm = llm

    async def execute(
        self, ctx: SkillContext, **kwargs: Any,
    ) -> SkillResult:
        t0 = time.monotonic()
        try:
            text = kwargs["text"][:30000]  # hard cap
            result = await self._llm.chat(
                ctx=ctx, conversation_id=None,
                model_name="gpt-4o-mini",
                user_message=text,
                system_prompt=SUMMARY_SYSTEM,
            )
            return SkillResult(
                success=True,
                output={"summary": result.get("content", "")},
                tokens_used=result.get("usage", {}).get("total_tokens", 0),
                latency_ms=int((time.monotonic() - t0) * 1000),
            )
        except Exception as exc:  # noqa: BLE001
            return SkillResult(
                success=False, error=str(exc),
                latency_ms=int((time.monotonic() - t0) * 1000),
            )
```

### 10.3 Skill Registry + Router

```python
# app/modules/agent/skills/registry.py
"""TH: Registry รวม skills | EN: skills registry"""
from __future__ import annotations
from typing import Any

from app.modules.agent.skills.base import BaseSkill, SkillContext, SkillResult


class SkillRegistry:
    """TH: registry สำหรับ skills | EN: skills registry"""

    def __init__(self) -> None:
        self._skills: dict[str, BaseSkill] = {}

    def register(self, skill: BaseSkill) -> None:
        if skill.name in self._skills:
            raise ValueError(f"skill {skill.name} already registered")
        self._skills[skill.name] = skill

    def get(self, name: str) -> BaseSkill | None:
        return self._skills.get(name)

    def all_specs(self) -> list[dict[str, Any]]:
        """TH: ส่ง specs ให้ LLM เพื่อ tool-calling | EN: tool specs for LLM"""
        return [
            {
                "type": "function",
                "function": {
                    "name": s.name,
                    "description": s.description,
                    "parameters": {
                        "type": "object",
                        "properties": s.parameters,
                        "required": [
                            k for k, v in s.parameters.items()
                            if isinstance(v, dict) and v.get("required")
                        ],
                    },
                },
            }
            for s in self._skills.values()
        ]

    async def execute(
        self, ctx: SkillContext, name: str, **kwargs: Any,
    ) -> SkillResult:
        skill = self._skills.get(name)
        if skill is None:
            return SkillResult(success=False, error=f"unknown skill: {name}")
        return await skill.execute(ctx, **kwargs)
```

### 10.4 Agent Loop (Tool-Calling)

```python
# app/modules/agent/application/agent_loop.py
"""TH: Agent loop ที่ใช้ skill | EN: agent loop with skills"""
from __future__ import annotations
import json
import logging
from typing import Any

from app.modules.agent.skills.base import SkillContext
from app.modules.agent.skills.registry import SkillRegistry
from app.modules.llm.application.use_case import LLMUseCase

logger = logging.getLogger(__name__)

_MAX_ITERATIONS = 5


class AgentLoop:
    """TH: ReAct-style agent loop | EN: ReAct-style agent loop"""

    def __init__(
        self, *, llm: LLMUseCase, registry: SkillRegistry,
        model: str = "gpt-4o-mini",
    ) -> None:
        self._llm = llm
        self._registry = registry
        self._model = model

    async def run(
        self, ctx: SkillContext, user_message: str,
    ) -> dict[str, Any]:
        """TH: รัน agent loop | EN: run agent loop"""
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": self._system_prompt()},
            {"role": "user", "content": user_message},
        ]
        trace: list[dict[str, Any]] = []

        for i in range(_MAX_ITERATIONS):
            result = await self._llm.chat(
                ctx=ctx, conversation_id=None,
                model_name=self._model,
                user_message=user_message,
                system_prompt=messages[0]["content"],
            )
            content = result.get("content", "")

            # ─── parse tool call ───
            tool_call = self._parse_tool_call(content)
            if tool_call is None:
                return {"answer": content, "trace": trace, "iterations": i + 1}

            trace.append({"iteration": i, "tool": tool_call["name"]})
            skill_result = await self._registry.execute(
                ctx, tool_call["name"], **tool_call["arguments"],
            )
            messages.append({"role": "assistant", "content": content})
            messages.append({
                "role": "tool",
                "content": json.dumps({
                    "success": skill_result.success,
                    "output": skill_result.output,
                    "error": skill_result.error,
                }, default=str)[:4000],
            })
            # follow-up with tool result
            user_message = "Continue using the tool result above."

        return {
            "answer": "max iterations reached",
            "trace": trace,
            "iterations": _MAX_ITERATIONS,
        }

    def _system_prompt(self) -> str:
        specs = self._registry.all_specs()
        return f"""You are a helpful agent. You can call tools.

## Available Tools
{json.dumps(specs, indent=2, ensure_ascii=False)}

## Rules
- To call a tool, output ONLY:
  {{"tool_call": {{"name": "...", "arguments": {{...}}}}}}
- Otherwise output the final answer directly.
- Match the user's language.
"""

    @staticmethod
    def _parse_tool_call(content: str) -> dict[str, Any] | None:
        content = content.strip()
        if "tool_call" not in content:
            return None
        try:
            start = content.find("{")
            end = content.rfind("}")
            if start == -1 or end == -1:
                return None
            data = json.loads(content[start:end + 1])
            call = data.get("tool_call")
            if not call:
                return None
            return {
                "name": call.get("name", ""),
                "arguments": call.get("arguments", {}),
            }
        except Exception:  # noqa: BLE001
            return None
```

### 10.5 Skill Testing

```python
# tests/skills/test_rag_qa_skill.py
"""TH: ทดสอบ RAG QA skill | EN: RAG QA skill tests"""
from __future__ import annotations
import pytest

from app.modules.agent.skills.base import SkillContext
from app.modules.agent.skills.rag_qa import RAGQASkill


@pytest.mark.asyncio
async def test_skill_success(mock_rag_uc) -> None:
    skill = RAGQASkill(use_case=mock_rag_uc)
    ctx = SkillContext(tenant_id="t1", user_id="u1",
                       conversation_id=None, metadata={})
    result = await skill.execute(ctx, question="What is RAG?")
    assert result.success is True
    assert "answer" in result.output


@pytest.mark.asyncio
async def test_skill_handles_error(broken_rag_uc) -> None:
    skill = RAGQASkill(use_case=broken_rag_uc)
    ctx = SkillContext(tenant_id="t1", user_id="u1",
                       conversation_id=None, metadata={})
    result = await skill.execute(ctx, question="x")
    assert result.success is False
    assert result.error is not None
```

---

## 11. ปัญหาและแนวทางแก้ไข

### 11.1 ตารางปัญหาที่พบบ่อย

| # | ปัญหา | อาการ | Root Cause | Fix |
|---|---|---|---|---|
| 1 | **Retrieval ไม่ตรง** | ตอบไม่ตรงคำถาม | chunk ใหญ่/เล็กเกิน, ไม่มี reranker | hybrid + reranker + tune chunk |
| 2 | **Hallucination** | ตอบข้อมูลปลอม | prompt ไม่ชัด, temp สูง | strict prompt + temp=0.1 |
| 3 | **Latency สูง** | p95 > 8s | serial pipeline | parallelize + cache + stream |
| 4 | **Cost พุ่ง** | งบบาน 3x | context ยาว, cache miss | compression + cache + mini model |
| 5 | **Rate limit** | 429 errors | burst requests | queue + backoff + per-tenant |
| 6 | **Self-loop Alembic** | migrate fail | `_get_head_revision` ชนตัวเอง | exclude self + sorted |
| 7 | **SSE ตัดกลาง** | stream หยุด | proxy timeout | disable buffering + heartbeat |
| 8 | **Prompt injection** | user ฝังคำสั่ง | ไม่ sanitize | guardrails + XML tags |
| 9 | **Data leakage** | retrieve ข้าม tenant | ไม่มี RLS | RLS + metadata filter |
| 10 | **Cold start** | request แรกช้า | model/db cold | warmup + replica |
| 11 | **Embedding drift** | คุณภาพลด | เปลี่ยน model | pin version + re-index |
| 12 | **Token overflow** | 400 error | context เกิน limit | truncate + compress |
| 13 | **Cache poison** | ตอบผิดซ้ำ | cache key ชน | hash tenant+model+params |
| 14 | **Silent fail** | error หาย | swallow exception | structured log + alert |
| 15 | **DB connection leak** | pool exhausted | ไม่ close session | context manager + pool size |
| 16 | **Streaming block** | UI ค้าง | sync call ใน async | all async + yield |
| 17 | **Vector dim mismatch** | index error | model ต่าง dims | validate + migrate |
| 18 | **Metadata filter ผิด** | result ว่าง | syntax ผิด | test + validate |
| 19 | **Duplicate chunks** | context ซ้ำ | overlap สูง | dedupe + MMR |
| 20 | **Index stale** | ข้อมูลเก่า | ไม่ re-index | scheduled job |

### 11.2 Playbooks (ทำตามได้)

#### PB-1: Retrieval Quality ไม่ดี

```markdown
## Diagnose
1. วัด retrieval recall@k ด้วย labeled set
2. ตรวจ sample hits ด้วยตา (top-10)
3. เทียบ dense vs hybrid vs rerank

## Fix (ตามลำดับ ROI)
1. **เพิ่ม reranker** — Cohere rerank-3 / BGE-reranker-v2
2. **Hybrid search** — รวม BM25 (sparse) + dense
3. **Tune chunk** — 256-1024 tokens, overlap 10-20%
4. **Metadata filter** — tenant, lang, date, type
5. **Query rewrite** — multi-query / HyDE
6. **Embedding model** — multilingual-e5 / voyage-3

## Verify
- recall@5 ≥ 0.85
- MRR ≥ 0.75
- RAGAS context_precision ≥ 0.8
```

#### PB-2: Latency > SLA

```markdown
## Diagnose
1. Trace แต่ละ step: embed / search / rerank / LLM
2. ระบุ bottleneck (ปกติ LLM)

## Fix
1. **Streaming** — ลด TTFB (first token < 500ms)
2. **Parallel** — rerank + LLM
3. **Cache**
   - query embedding (Redis, TTL 1h)
   - full result (Redis, TTL 5m)
   - prompt cache (provider)
4. **Reduce top_k** — 20 → 10, top_n → 3
5. **Smaller model** — mini/flash สำหรับงานง่าย
6. **Connection pool** — httpx pool, DB pool

## Verify
- p50 < 1s
- p95 < 3s
- TTFT < 500ms
```

#### PB-3: Cost spike

```markdown
## Diagnose
1. Dashboard: cost per tenant/model/day
2. Top consumers
3. ตรวจ cache hit rate

## Fix
1. **Budget per tenant** — hard limit + alert
2. **Model routing** — cheap first, escalate
3. **Context compression** — LLMLingua
4. **Cache** — semantic cache (Redis + embed)
5. **Retry cap** — 3 ครั้ง max
6. **Token audit** — tiktoken + log

## Verify
- Cost/day ลด ≥ 40%
- Cache hit ≥ 30%
```

### 11.3 Monitoring & Alerting

```python
# app/core/metrics.py
"""TH: Prometheus metrics | EN: Prometheus metrics"""
from prometheus_client import Counter, Histogram, Gauge

LLM_REQUESTS = Counter(
    "llm_requests_total", "Total LLM requests",
    ["tenant", "model", "status"],
)
LLM_LATENCY = Histogram(
    "llm_request_duration_seconds", "LLM latency",
    ["model", "endpoint"],
    buckets=(0.1, 0.25, 0.5, 1, 2, 3, 5, 8, 13, 21),
)
LLM_TOKENS = Counter(
    "llm_tokens_total", "Total tokens",
    ["tenant", "model", "direction"],   # input/output
)
LLM_COST = Counter(
    "llm_cost_usd_total", "Total cost",
    ["tenant", "model"],
)
RAG_RETRIEVAL = Histogram(
    "rag_retrieval_duration_seconds", "Retrieval latency",
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2),
)
RAG_HITS = Histogram(
    "rag_hits_returned", "Chunks returned",
    buckets=(0, 1, 3, 5, 10, 20, 50),
)
CACHE_HITS = Counter("cache_hits_total", "Cache hits", ["kind"])
CACHE_MISS = Counter("cache_misses_total", "Cache misses", ["kind"])
```

```yaml
# infra/prometheus/alerts.yml
groups:
  - name: llm-rag
    interval: 30s
    rules:
      - alert: HighLLMLatency
        expr: histogram_quantile(0.95, rate(llm_request_duration_seconds_bucket[5m])) > 3
        for: 5m
        labels: { severity: warning }
        annotations:
          summary: "LLM p95 latency > 3s"

      - alert: HighErrorRate
        expr: sum(rate(llm_requests_total{status="error"}[5m])) / sum(rate(llm_requests_total[5m])) > 0.05
        for: 5m
        labels: { severity: critical }

      - alert: CostSpike
        expr: sum(rate(llm_cost_usd_total[1h])) > 10
        for: 15m
        labels: { severity: warning }

      - alert: LowCacheHitRate
        expr: sum(rate(cache_hits_total[1h])) / (sum(rate(cache_hits_total[1h])) + sum(rate(cache_misses_total[1h]))) < 0.2
        for: 1h
        labels: { severity: info }

      - alert: ProviderDown
        expr: up{job="llm-provider"} == 0
        for: 2m
        labels: { severity: critical }
```

### 11.4 RAG Evaluation (RAGAS)

```python
# tests/eval/test_rag_quality.py
"""TH: ประเมินคุณภาพ RAG ด้วย RAGAS | EN: RAG quality evaluation"""
from __future__ import annotations
import pytest
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    answer_relevancy, context_precision, context_recall, faithfulness,
)


@pytest.mark.eval
def test_rag_quality() -> None:
    """TH: รัน RAGAS evaluation | EN: run RAGAS evaluation"""
    samples = {
        "question": [
            "RAG คืออะไร?",
            "การใช้งาน Qdrant?",
            "LLM context window สูงสุด?",
        ],
        "answer": [
            "RAG คือเทคนิค Retrieval-Augmented Generation",
            "Qdrant เป็น vector database",
            "GPT-4o รองรับ 128k tokens",
        ],
        "contexts": [
            ["RAG = Retrieval + Augmentation + Generation"],
            ["Qdrant เป็น vector similarity search engine"],
            ["GPT-4o context window = 128,000 tokens"],
        ],
        "ground_truth": [
            "RAG ย่อมาจาก Retrieval-Augmented Generation",
            "Qdrant เป็นฐานข้อมูลเวกเตอร์",
            "128,000 tokens",
        ],
    }
    result = evaluate(
        Dataset.from_dict(samples),
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
    )
    assert result["faithfulness"] >= 0.85
    assert result["answer_relevancy"] >= 0.80
    assert result["context_precision"] >= 0.75
    assert result["context_recall"] >= 0.75
```

### 11.5 Troubleshooting Cheatsheet

```bash
# ═══════════════════════════════════════════════════════════════
# QUICK TROUBLESHOOTING
# ═══════════════════════════════════════════════════════════════

# 1) Alembic self-loop
uv run alembic heads              # ต้องเห็น head เดียว
uv run alembic history            # ตรวจ chain
# fix: ลบไฟล์ migrate ที่มีปัญหา → regenerate

# 2) DB connection
psql $DATABASE_URL -c "SELECT 1"  # เช็ค connection
psql $DATABASE_URL -c "\dt public.llm_*"

# 3) Redis
redis-cli -u $REDIS_URL ping
redis-cli -u $REDIS_URL info stats | grep hit_rate

# 4) Qdrant
curl $QDRANT_URL/collections      # list collections
curl $QDRANT_URL/collections/docs  # info

# 5) Provider
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models

# 6) Logs (structured)
docker logs app --tail 100 | jq 'select(.level=="ERROR")'

# 7) Metrics
curl http://localhost:8000/metrics | grep llm_

# 8) Health
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

---

## 12. สรุป

### 12.1 สรุปภาพรวม

คู่มือนี้ครอบคลุม **LLM/RAG Solutions** สำหรับ production ตั้งแต่แนวคิดจนถึง deployment จริง:

```
┌────────────────────────────────────────────────────────────┐
│  1. Foundation      →  นิยาม, RAG concepts                 │
│  2. Architecture    →  DDD + Clean + Modular               │
│  3. Application     →  Framework, Vector DB, Embeddings    │
│  4. Operations      →  Docker, K8s, Cloud, CI/CD           │
│  5. Quality         →  Prompt, Skills, RCA, Evaluation     │
│  6. Production      →  Security, Observability, Cost       │
└────────────────────────────────────────────────────────────┘
```

### 12.2 บทเรียนสำคัญ (Key Takeaways)

| # | บทเรียน | ทำไมสำคัญ |
|---|---|---|
| 1 | **Retrieval quality = king** | LLM เก่งแค่ไหน ถ้า context ไม่ดี → ตอบผิด |
| 2 | **Hybrid + Rerank** | ลงทุนน้อย, ผลตอบแทนสูงสุด |
| 3 | **Prompt ต้อง versioned** | เปลี่ยน prompt = เปลี่ยน behavior → ต้อง A/B test |
| 4 | **Cost control ตั้งแต่ Day 1** | Budget + cache + routing ป้องกัน surprises |
| 5 | **DDD + Clean Arch** | เปลี่ยน tech ได้, test ง่าย, evolve ปลอดภัย |
| 6 | **Observability = non-negotiable** | ไม่มี logs/metrics = debug ไม่ได้ |
| 7 | **Security = default** | RLS, encrypt, sanitize, rate limit |
| 8 | **RCA เป็นวัฒนธรรม** | หา root cause ไม่ใช่หาแพะ |
| 9 | **Evaluate เสมอ** | RAGAS + golden set ก่อน deploy |
| 10 | **ผู้ใช้คือคนตัดสิน** | Metrics ดี ≠ UX ดี |

### 12.3 Roadmap แนะนำ (3 เดือน)

```markdown
## Sprint 1 (สัปดาห์ 1-2) — Foundation
- [ ] Setup project structure (llm module + rag module)
- [ ] SQL + migrations + RLS
- [ ] FastAPI + SSE + health checks
- [ ] Docker + docker-compose local

## Sprint 2 (สัปดาห์ 3-4) — Core RAG
- [ ] Qdrant integration
- [ ] Embedding pipeline
- [ ] Basic retrieval + reranker
- [ ] RAG QA endpoint + citations

## Sprint 3 (สัปดาห์ 5-6) — Production Hardening
- [ ] Redis cache + rate limit
- [ ] Idempotency + retry + circuit breaker
- [ ] Structured logging + Prometheus metrics
- [ ] Cost tracking + budgets

## Sprint 4 (สัปดาห์ 7-8) — Quality & Scale
- [ ] RAGAS evaluation suite
- [ ] Load test (k6)
- [ ] Hybrid search + multi-query
- [ ] K8s + HPA

## Sprint 5 (สัปดาห์ 9-10) — Advanced
- [ ] Agent loop + skills
- [ ] Multi-provider failover
- [ ] Blue-green deploy
- [ ] Chaos testing

## Sprint 6 (สัปดาห์ 11-12) — Polish
- [ ] Prompt registry + A/B
- [ ] Dashboards + alerts
- [ ] Runbooks + on-call
- [ ] Security review + pen test
```

### 12.4 Checklist ไป Production (One-Page)

```markdown
## ✅ BEFORE GO-LIVE

### Functionality
- [ ] /chat sync + stream ทำงาน
- [ ] /conversations CRUD
- [ ] /usage stats ถูกต้อง (Decimal)
- [ ] Idempotency ทำงาน
- [ ] Citations แสดง

### Reliability
- [ ] Retry ≤ 3 + backoff
- [ ] Circuit breaker
- [ ] Fallback provider
- [ ] Graceful shutdown
- [ ] Zero-downtime deploy

### Security
- [ ] RLS เปิด 5 tables
- [ ] API keys encrypted
- [ ] No PII in logs
- [ ] Rate limit + idempotency
- [ ] HTTPS only

### Observability
- [ ] Structured logs
- [ ] Metrics (latency, tokens, cost)
- [ ] Tracing (OTel)
- [ ] Dashboard (Grafana)
- [ ] Alerts (Slack/PagerDuty)

### Cost
- [ ] Budget per tenant
- [ ] Alerts at 80%
- [ ] Cache hit ≥ 30%
- [ ] Model routing

### Testing
- [ ] Unit ≥ 85%
- [ ] Integration (DB + vector)
- [ ] Load test (k6)
- [ ] RAGAS eval
- [ ] Chaos test

### Docs
- [ ] README + API
- [ ] Postman collection
- [ ] Runbooks
- [ ] Rollback plan
- [ ] On-call contact
```

### 12.5 ทรัพยากรแนะนำ

#### 📚 หนังสือ & Papers
- **"Designing Data-Intensive Applications"** — Martin Kleppmann
- **"Building LLM Apps"** — Valentino Gagliardi
- **RAG Paper (Lewis et al., 2020)** — arXiv:2005.11401
- **Self-RAG (Asai et al., 2023)** — arXiv:2310.11511
- **RAGAS Paper (Es et al., 2023)** — arXiv:2309.15217

#### 🛠️ Frameworks & Tools
- **LangChain** — https://python.langchain.com
- **LlamaIndex** — https://docs.llamaindex.ai
- **Haystack** — https://haystack.deepset.ai
- **Qdrant** — https://qdrant.tech/documentation
- **RAGAS** — https://docs.ragas.io
- **FastAPI** — https://fastapi.tiangolo.com

#### 📊 Benchmarks
- **MTEB** — Massive Text Embedding Benchmark
- **MTEB Leaderboard** — https://huggingface.co/spaces/mteb/leaderboard
- **Chatbot Arena** — https://lmarena.ai

#### 🎓 Courses
- **DeepLearning.AI** — "Building Systems with the ChatGPT API"
- **DeepLearning.AI** — "LangChain for LLM Application Development"
- **DeepLearning.AI** — "Building and Evaluating Advanced RAG"

### 12.6 คำส่งท้าย

> **"RAG ไม่ใช่ silver bullet — มันคือ tool"**
>
> ความสำเร็จของ LLM/RAG solutions ไม่ได้อยู่ที่โมเดลล่าสุด
> แต่อยู่ที่:
> - **ความเข้าใจธุรกิจ** (Domain)
> - **คุณภาพของข้อมูล** (Data quality)
> - **การออกแบบระบบ** (Architecture)
> - **การวัดผล** (Evaluation)
> - **การดูแลระยะยาว** (Operations)

**เริ่มจากเล็ก** → **วัดให้ชัด** → **ขยายเมื่อพร้อม** → **ปรับปรุงเสมอ**

---

**📌 Version:** 1.0 · **Last Updated:** 2026-09-24 · **License:** Internal Use
**📧 Feedback:** ส่ง PR หรือ issue ผ่าน repo ภายใน · **🔗 Related:** `llm_opencode_promt.md`, `create_module_llm.py`, `V004__seed_llm_demo.sql`
