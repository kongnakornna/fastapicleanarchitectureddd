# 📘 คู่มือการทำงาน (Work Manual)
## โครงการ: Enterprise AI Chatbot + Knowledge Management ด้วย LLM/RAG

**เวอร์ชัน:** 1.0
**วันที่:** 2026
**สถานะ:** ใช้งานจริง (Production-Ready)
**เจ้าของเอกสาร:** AI Platform Team

---

# สารบัญ

1. บทนำและภาพรวมโครงการ
2. สถาปัตยกรรมระบบ
3. โครงสร้าง Modules
4. มาตรฐานการพัฒนา (Development Standards)
5. ขั้นตอนการทำงาน (Workflow)
6. คู่มือการติดตั้งและตั้งค่า
7. คู่มือการพัฒนา Module
8. คู่มือการทดสอบ
9. คู่มือการ Deploy
10. คู่มือการ Operations
11. คู่มือการแก้ปัญหา (Troubleshooting)
12. Templates และ Checklists
13. ภาคผนวก

---

# 1. บทนำและภาพรวมโครงการ

## 1.1 วัตถุประสงค์

คู่มือนี้จัดทำขึ้นเพื่อเป็น **เอกสารอ้างอิงหลัก** สำหรับทีมพัฒนา DevOps และ Operations ในการ:
- เข้าใจสถาปัตยกรรมของระบบ Enterprise AI Chatbot + KM
- พัฒนา module ใหม่ตามมาตรฐานเดียวกัน
- Deploy และดูแลระบบใน production
- แก้ไขปัญหาที่เกิดขึ้นอย่างเป็นระบบ

## 1.2 ขอบเขตโครงการ

**ระบบที่พัฒนา:**
- Enterprise AI Chatbot สำหรับตอบคำถามจากความรู้ขององค์กร
- Knowledge Management System สำหรับจัดการเอกสาร
- RAG Pipeline สำหรับ retrieval + generation
- AI/ML Platform สำหรับ training และ serving

**กลุ่มผู้ใช้งาน:**
- พนักงานภายในองค์กร (Internal Users)
- ลูกค้า (External Users)
- ทีม Admin (Knowledge Managers)
- ทีม Developer (Platform Team)

## 1.3 บทบาทและความรับผิดชอบ

| บทบาท | ความรับผิดชอบ |
|---|---|
| **Tech Lead** | ออกแบบสถาปัตยกรรม, review code, ตัดสินใจเชิงเทคนิค |
| **Backend Developer** | พัฒนา module, repository, use case, API |
| **ML Engineer** | พัฒนา model, feature, training pipeline |
| **DevOps Engineer** | ดูแล infrastructure, CI/CD, monitoring |
| **QA Engineer** | ทดสอบ unit, integration, E2E |
| **Knowledge Manager** | จัดการเอกสาร, collection, feedback |
| **Product Owner** | กำหนด requirement, priority, roadmap |

## 1.4 แผนการทำงาน (Roadmap)

```
Phase 1 (สัปดาห์ 1-2):   Foundation
  - Setup infrastructure
  - Migration
  - Module template

Phase 2 (สัปดาห์ 3-4):   Core Modules
  - ai_ml module
  - rag module
  - llm module

Phase 3 (สัปดาห์ 5-6):   Application
  - Chat UI
  - Admin Console
  - Integration APIs

Phase 4 (สัปดาห์ 7-8):   Testing & Evaluation
  - Golden set
  - RAGAS metrics
  - Load testing

Phase 5 (สัปดาห์ 9-10):  Deployment
  - Canary deploy
  - A/B testing
  - Monitoring

Phase 6 (สัปดาห์ 11-12): Optimization
  - Cost tuning
  - Latency tuning
  - Feedback loop
```

---

# 2. สถาปัตยกรรมระบบ

## 2.1 ภาพรวมสถาปัตยกรรม

```
┌─────────────────────────────────────────────────────────────┐
│                    Client / Channels                        │
│         Web Chat, Internal Portal, LINE/Teams               │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTPS + SSE
┌──────────────────────────▼──────────────────────────────────┐
│                   API Gateway + Auth                        │
│              SSO, JWT, RBAC, Rate Limit, Audit              │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                  Chat Orchestrator                          │
│        Session, History, Intent, Routing, Feedback          │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   RAG Orchestrator                          │
│     Query Rewrite → Retrieval → Rerank → Context → LLM      │
└───────┬──────────────────┬──────────────────┬───────────────┘
        │                  │                  │
        ▼                  ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ Knowledge     │  │ Retrieval     │  │ Generation    │
│ Pipeline      │  │ Layer         │  │ Layer         │
│ (rag module)  │  │ (rag module)  │  │ (rag + llm)   │
└───────┬───────┘  └───────┬───────┘  └───────┬───────┘
        │                  │                  │
        ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                     Storage Layer                           │
│  Vector DB · Document Store · Object Storage · RDBMS · Cache│
└─────────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                  Integration Layer                          │
│     Web Apps · ERP/CRM/HR/ITSM · Webhook · Event Bus        │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│              Observability / Evaluation / Cost              │
│  Logging · Tracing · Metrics · Golden Set · Feedback Loop   │
└─────────────────────────────────────────────────────────────┘
```

## 2.2 Technology Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| **Runtime** | Python | 3.11+ | Language |
| **Web** | FastAPI | ≥ 0.115 | Framework |
| **Validation** | Pydantic | v2 | Schema |
| **ORM** | SQLAlchemy | 2.0 async | Database |
| **Database** | PostgreSQL | 16 | Primary DB |
| **Cache** | Redis | 7 | Cache + online FS |
| **Event Bus** | Kafka | 3.x | Events |
| **Vector DB** | Milvus | 2.4+ | Vector store |
| **Search** | Elasticsearch | 8+ | BM25 |
| **LLM Serving** | vLLM | 0.6+ | LLM |
| **Embedding** | OpenAI/Cohere | API | Embeddings |
| **Rerank** | Cohere/BGE | API | Reranking |
| **ML Tracking** | MLflow | 2.15+ | Experiments |
| **Feature Store** | Feast | 0.40+ | Features |
| **Training** | Ray | 2.35+ | Distributed |
| **Drift** | Evidently | 0.4+ | Monitoring |
| **Logging** | structlog/loguru | latest | Logs |
| **Tracing** | OpenTelemetry | latest | Traces |
| **Metrics** | Prometheus/Grafana | latest | Metrics |

## 2.3 Data Flow

### 2.3.1 Ingestion Flow (Offline)

```
Data Sources
  ↓
Connectors (S3, DB, API, SharePoint)
  ↓
Parser / OCR (PDF, DOCX, HTML)
  ↓
Preprocessing (Clean, Normalize, PII Mask)
  ↓
Chunking (Recursive 800 tokens, overlap 100)
  ↓
Embedding (Batch, Cached)
  ↓
Indexing (Vector DB + ES)
  ↓
rag_documents + rag_chunks + rag_embeddings
```

### 2.3.2 Query Flow (Online)

```
User Query
  ↓
API Gateway (Auth, Rate Limit)
  ↓
Chat Orchestrator (Session, History)
  ↓
RAG Orchestrator
  ├─ Query Rewrite
  ├─ Hybrid Retrieval (Vector + BM25)
  ├─ Rerank (Cohere)
  ├─ Context Assembly
  ├─ Prompt Template
  ├─ LLM Generation (Streaming)
  └─ Citation
  ↓
Response (SSE)
  ↓
rag_queries + rag_retrievals + rag_feedback
```

---

# 3. โครงสร้าง Modules

## 3.1 รายการ Modules ทั้งหมด

| # | Module | Layer | Prefix | Schema | สถานะ |
|---|---|---|---|---|---|
| 1 | `events` | 0-Core | `evt` | public | Dependency |
| 2 | `idempotency` | 0-Core | `idem` | public | Dependency |
| 3 | `tenant` | 1-Foundation | `ten` | public | Dependency |
| 4 | `user` | 1-Foundation | `usr` | public | Dependency |
| 5 | `auth` | 1-Foundation | `auth` | public | Dependency |
| 6 | `audit` | 1-Foundation | `aud` | public | Dependency |
| 7 | `tools` | 4-Ops | `tools` | public | ถัดไป |
| 8 | `automation` | 4-Ops | `automation` | public | ถัดไป |
| 9 | `llm` | 5-Intel | `llm` | public | Dependency |
| 10 | `ai_ml` | 5-Intel | `aiml` | public | ✅ เสร็จ |
| 11 | `rag` | 5-Intel | `rag` | public | ✅ เสร็จ |
| 12 | `agent` | 5-Intel | `agent` | public | ถัดไป |

## 3.2 โครงสร้าง Module มาตรฐาน

```
app/modules/{module_name}/
├── __init__.py
├── domain/                              # Layer 1
│   ├── entities/                        # 7 entities
│   ├── value_objects/                   # 5 VOs
│   ├── helpers/                         # 2-3 helpers
│   ├── events.py                        # 7 events
│   ├── enums.py                         # 6 enums
│   └── exceptions.py                    # 11-12 exceptions
├── application/                         # Layer 2
│   ├── use_case.py
│   ├── interfaces.py
│   ├── mappers.py
│   ├── exceptions.py
│   └── utils.py
├── infrastructure/                      # Layer 3
│   ├── models.py
│   ├── *_repository.py                  # 7 repos
│   ├── caches.py
│   ├── services.py
│   └── external/                        # LLM, Vector, etc.
└── presentation/                        # Layer 4
    ├── router.py
    ├── schemas.py
    ├── docs.py
    ├── dependencies.py
    └── swagger.py

db/migrations/
├── V001__create_{module}.sql
├── V002__seed_{module}.sql
└── V003__rollback_{module}.sql

migrations/versions/
└── {prefix}_001_add_{module}_tables.py

tests/
├── unit/
├── integration/
├── property/
└── manual/

docs/
├── README_{module}.md
├── API_{module}.md
└── postman/{module}.json
```

## 3.3 Dependency Rule

```
presentation → application → domain ← infrastructure
```

**กฎเหล็ก:**
- `domain` ห้าม import framework
- `application` รู้จัก domain เท่านั้น
- `infrastructure` implement interface ของ application
- `presentation` เรียก application

---

# 4. มาตรฐานการพัฒนา (Development Standards)

## 4.1 Global Constraints

```markdown
[GLOBAL CONSTRAINTS]
- ห้ามทักทาย / ห้ามสรุป / ห้ามอธิบายซ้ำ
- ตอบเฉพาะไฟล์ใน Output Scope
- โค้ดเต็ม Production-ready ห้าม `...` หรือ `# code here`
- ห้ามแตะไฟล์นอก Scope (ถ้าจำเป็น → ประกาศ SIDE-EFFECT WARNING)
- คอมเมนต์ 2 ภาษา (TH + EN) สั้น กระชับ
- Error handling:
  • Use Case   → 3-branch (DomainError → AppError → Exception)
  • Repository → 2-branch (AppError → Exception)
  • Cache      → never-raise (log + return None/False)
  • ML Call    → never-raise + retry with backoff
  • Model Load → never-raise + fallback
- Type hints ครบ / Pydantic v2 / SQLAlchemy 2.0 async
- ใช้ `Decimal` เท่านั้นสำหรับตัวเลขเงิน
- ใช้ `flush()` ห้าม `commit()` ใน Repository
- SQL style:
  • Schema: public
  • Table prefix: {module}_
  • DROP TABLE IF EXISTS ก่อน CREATE
  • Types ตรง: uuid, varchar(n) COLLATE "pg_catalog"."default",
    int4, timestamptz(6), numeric(12,8), bool, jsonb
- Routing: register ที่ `app/app.py` + `migrations/env.py`
- Docs: README + OpenAPI + Postman
- Path: `app/modules/{module}/{layer}/{file}.py`
- ข้อมูลไม่พอ → ถาม 1 คำถาม ห้ามเดา
- ห้าม log PII / API keys / raw data content
- Streaming ใช้ SSE / chunked response
```

## 4.2 Coding Standards

### 4.2.1 Python Style

```python
# ถูกต้อง
async def register_dataset(
    self,
    ctx: RequestContext,
    payload: DatasetCreate,
) -> Dataset:
    """TH: ลงทะเบียน dataset | EN: register dataset"""
    ...


# ผิด
def registerDataset(ctx,payload):
    # no docstring, no type hints
    ...
```

### 4.2.2 Naming Conventions

| ประเภท | Convention | ตัวอย่าง |
|---|---|---|
| Module | snake_case | `ai_ml`, `rag` |
| Class | PascalCase | `DatasetRepository` |
| Function | snake_case | `register_dataset` |
| Constant | UPPER_SNAKE | `MAX_RETRY` |
| Table | `{prefix}_{name}` | `aiml_datasets` |
| Index | `ix_{prefix}_{name}` | `ix_aiml_dataset_tenant` |
| Policy | `p_{prefix}_{name}` | `p_aiml_dataset` |
| Trigger | `trg_{prefix}_{name}_updated` | `trg_aiml_dataset_updated` |
| Function | `set_updated_at_{prefix}()` | `set_updated_at_aiml()` |

### 4.2.3 Error Handling Pattern

```python
# Use Case: 3-branch
async def do_something(self, ctx, payload):
    try:
        # business logic
        ...
        return result
    except DomainError as exc:
        logger.warning("domain_error", error=str(exc))
        raise AppError.from_domain(exc) from exc
    except AppError:
        raise
    except Exception as exc:
        logger.exception("unexpected_error")
        raise


# Repository: 2-branch
async def save(self, ctx, entity):
    try:
        model = Model.from_entity(entity)
        self._session.add(model)
        await self._session.flush()
        return model
    except AppError:
        raise
    except Exception as exc:
        logger.exception("save_failed")
        raise


# Cache: never-raise
async def get(self, key):
    try:
        return await self._redis.get(key)
    except Exception:
        logger.warning("cache_get_failed", key=key)
        return None
```

### 4.2.4 Logging Standards

```python
from structlog import get_logger

logger = get_logger(__name__)

# ถูกต้อง
logger.info("dataset_registered", dataset_id=str(ds.id), rows=ds.rows)

# ผิด
logger.info(f"Registered dataset {ds.id} with {ds.rows} rows")
logger.info(f"User data: {user.raw_json}")  # PII!
```

## 4.3 Git Workflow

```
main
  ↑
develop
  ↑
feature/{ticket-id}-{description}
```

**Commit Convention:**
```
feat(ai_ml): add dataset profiling
fix(rag): resolve chunk overlap bug
docs(api): update OpenAPI spec
test(ai_ml): add unit tests for metrics
chore(deps): bump fastapi to 0.115
```

**Branch Naming:**
```
feature/AIML-123-dataset-profiling
fix/RAG-456-chunk-overlap
docs/API-789-openapi-update
```

---

# 5. ขั้นตอนการทำงาน (Workflow)

## 5.1 Feature Development Workflow

```
1. รับ Requirement
   ↓
2. วิเคราะห์ + ออกแบบ
   ↓
3. สร้าง Branch
   ↓
4. เขียน Test (TDD)
   ↓
5. เขียน Code
   ↓
6. Run Test + Lint
   ↓
7. Code Review
   ↓
8. Merge to develop
   ↓
9. Deploy to staging
   ↓
10. QA Test
   ↓
11. Merge to main
   ↓
12. Deploy to production
```

## 5.2 Module Creation Workflow

```bash
# 1. สร้าง module structure
python create_module_{name}.py create {name} {layer} {prefix} --force

# 2. สร้าง SQL
python create_module_{name}.py sql {name} {prefix} --force

# 3. สร้าง Alembic
python create_module_{name}.py alembic {name} {prefix} --force

# 4. สร้าง Swagger
python create_module_{name}.py swagger {name} --force

# 5. สร้าง Postman
python create_module_{name}.py postman {name} --force

# 6. Activate (register router + models)
python create_module_{name}.py activate {name}

# 7. Apply migration
alembic upgrade head

# 8. Verify
psql -c "\dt public.{prefix}_*"
```

## 5.3 Code Review Checklist

```markdown
- [ ] Code ตรงตาม requirement
- [ ] มี test ครบ (unit, integration)
- [ ] ผ่าน lint (ruff, mypy)
- [ ] ไม่มี `...` หรือ TODO
- [ ] Type hints ครบ
- [ ] Docstring 2 ภาษา
- [ ] Error handling ตาม pattern
- [ ] ไม่ log PII
- [ ] ไม่ commit() ใน repository
- [ ] ใช้ Decimal สำหรับ cost
- [ ] Migration ถูกต้อง
- [ ] RLS เปิด
- [ ] Trigger สร้าง
- [ ] Test ผ่านทั้งหมด
- [ ] Coverage ≥ 85%
```

---

# 6. คู่มือการติดตั้งและตั้งค่า

## 6.1 Prerequisites

```bash
# Python 3.11+
pyenv install 3.11.9
pyenv local 3.11.9

# Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Docker
docker --version  # ≥ 24.0

# PostgreSQL client
psql --version  # ≥ 16
```

## 6.2 Setup Development Environment

```bash
# 1. Clone repository
git clone git@github.com:org/enterprise-ai-platform.git
cd enterprise-ai-platform

# 2. Install dependencies
poetry install

# 3. Activate virtualenv
poetry shell

# 4. Copy environment file
cp .env.example .env
# แก้ไข .env ตามต้องการ

# 5. Start infrastructure
docker-compose up -d postgres redis kafka milvus elasticsearch

# 6. Run migrations
alembic upgrade head

# 7. Seed data (optional)
psql -f db/migrations/V002__seed_ai_ml.sql
psql -f db/migrations/V002__seed_rag.sql

# 8. Run tests
pytest tests/ -v --cov=app

# 9. Start server
uvicorn app.app:app --reload --port 8000
```

## 6.3 Environment Variables

```bash
# .env
# ─── App ───────────────────────────────
APP_NAME=enterprise-ai-platform
APP_ENV=development
APP_DEBUG=true
APP_PORT=8000

# ─── Database ──────────────────────────
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/aiplatform
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# ─── Redis ─────────────────────────────
REDIS_URL=redis://localhost:6379/0
REDIS_TTL=300

# ─── Kafka ─────────────────────────────
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_GROUP_ID=ai-platform

# ─── Vector DB ─────────────────────────
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_COLLECTION_PREFIX=rag_

# ─── Elasticsearch ─────────────────────
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_INDEX_PREFIX=rag_bm25_

# ─── LLM ───────────────────────────────
OPENAI_API_KEY=sk-...
AZURE_OPENAI_ENDPOINT=https://...
AZURE_OPENAI_KEY=...
VLLM_ENDPOINT=http://localhost:8001/v1

# ─── Embedding ─────────────────────────
EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_DIM=3072
COHERE_API_KEY=...

# ─── Security ──────────────────────────
JWT_SECRET=...
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

# ─── Observability ─────────────────────
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
LOG_LEVEL=INFO
```

## 6.4 Docker Compose

```yaml
# docker-compose.yml
version: "3.9"

services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: aiplatform
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    ports:
      - "9092:9092"
    environment:
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092

  milvus:
    image: milvusdb/milvus:v2.4.0
    ports:
      - "19530:19530"
      - "9091:9091"

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      discovery.type: single-node
      xpack.security.enabled: "false"
    ports:
      - "9200:9200"

volumes:
  pgdata:
```

---

# 7. คู่มือการพัฒนา Module

## 7.1 ขั้นตอนการสร้าง Module ใหม่

### 7.1.1 วิเคราะห์และออกแบบ

```markdown
1. กำหนดชื่อ module: {name}
2. กำหนด layer: {0-Core, 1-Foundation, 4-Ops, 5-Intel}
3. กำหนด prefix: {prefix}
4. กำหนด tables: {prefix}_*
5. กำหนด entities: 7 entities
6. กำหนด VOs: 5 VOs
7. กำหนด events: 7 events
8. กำหนด enums: 6 enums
9. กำหนด exceptions: 11-12 exceptions
10. กำหนด endpoints: 21 endpoints
```

### 7.1.2 สร้าง Domain Layer

```python
# domain/entities/{entity}.py
"""TH: Entity {name} | EN: {name} entity"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, UTC

from app.modules.{module}.domain.enums import {EnumName}
from app.modules.{module}.domain.exceptions import {ErrorName}


@dataclass
class {EntityName}:
    """TH: {คำอธิบาย} | EN: {description}"""

    id: uuid.UUID
    tenant_id: uuid.UUID
    # ... fields
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def {business_method}(self, ...) -> None:
        """TH: {คำอธิบาย} | EN: {description}"""
        # validation
        # transition
        pass
```

### 7.1.3 สร้าง Application Layer

```python
# application/interfaces.py
class {Name}Repository(ABC):
    @abstractmethod
    async def save(self, ctx: RequestContext, entity: {Entity}) -> Any: ...
    @abstractmethod
    async def find_by_id(self, ctx: RequestContext, id: uuid.UUID) -> {Entity} | None: ...
    # ...


# application/use_case.py
class {Module}UseCase:
    def __init__(
        self,
        {name}_repo: {Name}Repository,
        event_bus: EventBus,
        cache: {Module}Cache,
    ) -> None:
        self._{name}_repo = {name}_repo
        self._event_bus = event_bus
        self._cache = cache

    async def {action}(self, ctx, payload) -> Any:
        """TH: {คำอธิบาย} | EN: {description}"""
        try:
            # 1. Build entity
            entity = {Entity}(...)
            # 2. Persist
            result = await self._{name}_repo.save(ctx, entity)
            # 3. Publish event
            await self._event_bus.publish({Event}(...))
            return result
        except DomainError as exc:
            logger.warning("domain_error", error=str(exc))
            raise AppError.from_domain(exc) from exc
        except AppError:
            raise
        except Exception as exc:
            logger.exception("{action}_failed")
            raise
```

### 7.1.4 สร้าง Infrastructure Layer

```python
# infrastructure/models.py
class {Entity}Model(Base):
    """TH: SQLAlchemy model | EN: SQLAlchemy model"""

    __tablename__ = "{prefix}_{table}"
    __table_args__ = {"schema": "public"}

    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=text("gen_random_uuid()"))
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    # ... columns
    created_at = Column(DateTime(timezone=True), nullable=False,
                        server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False,
                        server_default=func.now())

    @classmethod
    def from_entity(cls, entity: {Entity}) -> "{Entity}Model":
        """TH: แปลง entity → model | EN: entity → model"""
        return cls(
            id=entity.id,
            tenant_id=entity.tenant_id,
            # ...
        )

    def to_entity(self) -> {Entity}:
        """TH: แปลง model → entity | EN: model → entity"""
        return {Entity}(
            id=self.id,
            tenant_id=self.tenant_id,
            # ...
        )
```

### 7.1.5 สร้าง Presentation Layer

```python
# presentation/schemas.py
class {Entity}Create(BaseModel):
    """TH: Schema สำหรับสร้าง | EN: Create schema"""
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=1, max_length=200)
    # ...


class {Entity}Response(BaseModel):
    """TH: Schema สำหรับ response | EN: Response schema"""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    # ...


# presentation/router.py
router = APIRouter(prefix="/{module-path}", tags=["{Module}"])


@router.post("/{resource}", status_code=201)
async def create_{resource}(
    payload: {Entity}Create,
    uc: {Module}UseCase = Depends(get_use_case),
) -> {Entity}Response:
    """TH: สร้าง | EN: create"""
    result = await uc.{action}(payload)
    return {Entity}Response.model_validate(result)
```

## 7.2 Template การสร้างไฟล์

ดู Templates ใน Section 12

---

# 8. คู่มือการทดสอบ

## 8.1 ระดับการทดสอบ

| ระดับ | เครื่องมือ | Coverage Target | จำนวนขั้นต่ำ |
|---|---|---|---|
| Unit | pytest | ≥ 90% | 15 tests |
| Integration | pytest + testcontainers | ≥ 80% | 8 tests |
| Property | hypothesis | — | 6 tests |
| Manual | checklist | — | 15 scenarios |
| **รวม** | | **≥ 85%** | **44+** |

## 8.2 Unit Test Template

```python
# tests/unit/test_{module}.py
"""TH: Unit tests | EN: Unit tests"""
from __future__ import annotations

import uuid
from datetime import datetime, UTC

import pytest

from app.modules.{module}.domain.entities.{entity} import {Entity}
from app.modules.{module}.domain.enums import {Enum}


def test_{entity}_create_defaults() -> None:
    """TH: ทดสอบสร้าง | EN: test creation"""
    entity = {Entity}(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        name="test",
    )
    assert entity.status == {Enum}.DRAFT
    assert entity.version == 1
```

## 8.3 Integration Test Template

```python
# tests/integration/test_{module}_repository.py
"""TH: Integration tests | EN: Integration tests"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_save_and_find(session: AsyncSession, ctx) -> None:
    """TH: ทดสอบ save + find | EN: test save + find"""
    repo = SQLAlchemy{Entity}Repository(session)
    entity = {Entity}(...)

    saved = await repo.save(ctx, entity)
    found = await repo.find_by_id(ctx, saved.id)

    assert found is not None
    assert found.id == saved.id


@pytest.mark.asyncio
async def test_rls_blocks_other_tenant(session: AsyncSession, ctx_a, ctx_b) -> None:
    """TH: ทดสอบ RLS | EN: test RLS"""
    repo = SQLAlchemy{Entity}Repository(session)
    entity = {Entity}(tenant_id=ctx_a.tenant_id, ...)
    await repo.save(ctx_a, entity)

    # Tenant B ไม่ควรเห็น
    found = await repo.find_by_id(ctx_b, entity.id)
    assert found is None
```

## 8.4 Property Test Template

```python
# tests/property/test_{module}_invariants.py
"""TH: Property tests | EN: Property tests"""
from decimal import Decimal

from hypothesis import given, strategies as st


@given(st.decimals(min_value=0, max_value=1e9, places=8))
def test_cost_always_decimal(value: Decimal) -> None:
    """TH: cost ต้องเป็น Decimal เสมอ | EN: cost always Decimal"""
    assert isinstance(value, Decimal)
```

## 8.5 การ Run Tests

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# Property tests
pytest tests/property/ -v

# Coverage
pytest tests/ --cov=app --cov-report=html

# Specific test
pytest tests/unit/test_ai_ml.py::test_dataset_create_defaults -v

# Parallel
pytest tests/ -n auto
```

## 8.6 Manual Test Checklist

```markdown
## Manual Test: {Module}

- [ ] 1. สร้าง entity ผ่าน API
- [ ] 2. ดูรายการ entity
- [ ] 3. ดู entity detail
- [ ] 4. อัปเดต entity
- [ ] 5. ลบ entity
- [ ] 6. ทดสอบ pagination
- [ ] 7. ทดสอบ filter
- [ ] 8. ทดสอบ sort
- [ ] 9. ทดสอบ RLS (cross-tenant)
- [ ] 10. ทดสอบ idempotency
- [ ] 11. ทดสอบ rate limit
- [ ] 12. ทดสอบ error handling
- [ ] 13. ทดสอบ streaming (ถ้ามี)
- [ ] 14. ทดสอบ cache
- [ ] 15. ทดสอบ event publishing
```

---

# 9. คู่มือการ Deploy

## 9.1 สภาพแวดล้อม

| Environment | URL | Database | Purpose |
|---|---|---|---|
| Development | localhost:8000 | Local PG | พัฒนา |
| Staging | staging.ai.org | Staging PG | ทดสอบ |
| Production | ai.org | Production PG | ใช้งานจริง |

## 9.2 CI/CD Pipeline

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install poetry
      - run: poetry install
      - run: poetry run ruff check .
      - run: poetry run mypy app
      - run: poetry run pytest tests/ --cov=app --cov-fail-under=85

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t ai-platform:${{ github.sha }} .
      - run: docker push registry.ai.org/ai-platform:${{ github.sha }}
```

## 9.3 Deployment Steps

```bash
# 1. Backup database
pg_dump -h prod-db -U user aiplatform > backup_$(date +%Y%m%d).sql

# 2. Apply migrations
alembic upgrade head

# 3. Deploy canary (10% traffic)
kubectl apply -f k8s/canary.yaml

# 4. Monitor 15 นาที
# - error rate < 1%
# - latency p99 < 3s
# - no alert

# 5. ขยายเป็น 100%
kubectl apply -f k8s/production.yaml

# 6. Verify
curl https://ai.org/health
curl https://ai.org/api/v1/rag/collections
```

## 9.4 Rollback

```bash
# 1. Rollback app
kubectl rollout undo deployment/ai-platform

# 2. Rollback migration (ถ้าจำเป็น)
alembic downgrade -1

# 3. Restore database (ถ้าจำเป็น)
psql -h prod-db -U user aiplatform < backup_YYYYMMDD.sql
```

## 9.5 Deployment Checklist

```markdown
- [ ] Tests ผ่านทั้งหมด
- [ ] Coverage ≥ 85%
- [ ] Lint ผ่าน
- [ ] Type check ผ่าน
- [ ] Migration ทดสอบแล้ว
- [ ] Backup database แล้ว
- [ ] Canary deploy
- [ ] Monitor 15 นาที
- [ ] ขยาย 100%
- [ ] Health check ผ่าน
- [ ] Smoke test ผ่าน
- [ ] Rollback plan พร้อม
```

---

# 10. คู่มือการ Operations

## 10.1 Monitoring

### 10.1.1 Dashboards

| Dashboard | Metrics | เครื่องมือ |
|---|---|---|
| **Application** | Request rate, error rate, latency | Grafana |
| **Database** | Connections, queries, slow queries | Grafana + PG |
| **Cache** | Hit ratio, memory, evictions | Grafana + Redis |
| **Vector DB** | Query latency, index size | Grafana + Milvus |
| **LLM** | Token usage, cost, latency | Grafana + custom |
| **RAG** | Faithfulness, relevance, precision | Grafana + custom |

### 10.1.2 Alerts

```yaml
# alerts.yml
groups:
  - name: ai-platform
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.01
        for: 5m
        annotations:
          summary: "Error rate > 1%"

      - alert: HighLatency
        expr: histogram_quantile(0.99, http_request_duration_seconds) > 3
        for: 5m
        annotations:
          summary: "Latency p99 > 3s"

      - alert: HighCost
        expr: rate(llm_cost_usd_total[1h]) > 100
        for: 10m
        annotations:
          summary: "Cost > $100/hour"

      - alert: LowCacheHit
        expr: rate(cache_hits_total[5m]) / rate(cache_requests_total[5m]) < 0.6
        for: 10m
        annotations:
          summary: "Cache hit < 60%"
```

## 10.2 Daily Operations

```markdown
## Daily Checklist

- [ ] ตรวจสอบ dashboard (error rate, latency, cost)
- [ ] ตรวจสอบ alerts
- [ ] ตรวจสอบ log errors
- [ ] ตรวจสอบ slow queries
- [ ] ตรวจสอบ cache hit ratio
- [ ] ตรวจสอบ disk usage
- [ ] ตรวจสอบ database connections
- [ ] ตรวจสอบ Kafka lag
- [ ] ตรวจสอบ vector DB health
- [ ] ตรวจสอบ LLM quota
```

## 10.3 Weekly Operations

```markdown
## Weekly Checklist

- [ ] Review error trends
- [ ] Review performance trends
- [ ] Review cost trends
- [ ] Review RAG metrics (faithfulness, relevance)
- [ ] Review feedback (rating, comments)
- [ ] Reindex changed documents
- [ ] Update dependencies
- [ ] Run security scan
- [ ] Backup verification
- [ ] Capacity planning
```

## 10.4 Monthly Operations

```markdown
## Monthly Checklist

- [ ] Review SLO/SLA
- [ ] Postmortem (ถ้ามี incident)
- [ ] Update runbook
- [ ] Retrain models (ถ้าจำเป็น)
- [ ] Review drift
- [ ] Cost optimization
- [ ] Security audit
- [ ] Disaster recovery test
- [ ] Team retrospective
```

## 10.5 Runbook

```markdown
# Runbook: High Error Rate

## Symptom
Error rate > 1% (5 นาที)

## Diagnosis
1. ตรวจสอบ Grafana dashboard
2. ตรวจสอบ log: `kubectl logs -f deployment/ai-platform`
3. ตรวจสอบ database: `pg_stat_activity`
4. ตรวจสอบ Redis: `redis-cli info`
5. ตรวจสอบ Kafka: `kafka-consumer-groups --describe`

## Action
1. ถ้า database connection หมด → restart pool
2. ถ้า Redis ล่ม → restart Redis
3. ถ้า Kafka lag → scale consumer
4. ถ้า LLM timeout → ตรวจ quota + fallback
5. ถ้า code error → rollback

## Escalation
- Level 1: On-call engineer
- Level 2: Tech Lead
- Level 3: CTO
```

---

# 11. คู่มือการแก้ปัญหา (Troubleshooting)

## 11.1 ปัญหาที่พบบ่อย

| # | ปัญหา | สาเหตุ | แนวทางแก้ไข |
|---|---|---|---|
| 1 | Migration ล้มเหลว | `down_revision` ผิด | ตรวจ `down_revision` |
| 2 | RLS ไม่ทำงาน | ลืม `SET app.current_tenant` | Set context ก่อน query |
| 3 | Trigger ไม่ทำงาน | ลืมสร้าง function | รัน V001 ครบ |
| 4 | Cache hit ต่ำ | TTL สั้น | เพิ่ม TTL |
| 5 | Inference ช้า | Cold start | Warm pool |
| 6 | Training ล้มเหลว | OOM | ลด batch size |
| 7 | Reproducibility ไม่ได้ | ไม่ seed | ตั้ง seed ทุกที่ |
| 8 | Data leakage | Feature ไม่ PIT | ใช้ point-in-time correct |
| 9 | Retrieval ไม่เจอ | Embedding ไม่ตรง domain | Hybrid + rerank |
| 10 | คำตอบ hallucinate | Context ไม่พอ | เพิ่ม top-K |
| 11 | Citation ผิด | Chunk tracking หาย | เก็บ chunk_id |
| 12 | Latency สูง | Rerank เยอะ | ลด top-K + streaming |
| 13 | Cost พุ่ง | Embed ซ้ำ | Cache + batch |
| 14 | Multi-tenant leak | RLS ปิด | เปิด RLS |
| 15 | PII รั่ว | log raw content | Mask PII |

## 11.2 Debugging Flow

```
ปัญหาเกิดขึ้น
  ↓
1. ตรวจสอบ log (application, database, cache, kafka)
  ↓
2. ตรวจสอบ metrics (Grafana)
  ↓
3. ตรวจสอบ traces (Jaeger)
  ↓
4. Reproduce ในเครื่อง
  ↓
5. หา root cause (5 Whys)
  ↓
6. แก้ไข
  ↓
7. เขียน test
  ↓
8. Deploy
  ↓
9. Verify
  ↓
10. Postmortem (ถ้า incident)
```

## 11.3 Debug Commands

```bash
# Application logs
kubectl logs -f deployment/ai-platform --tail=100

# Database
psql -h localhost -U user aiplatform
SELECT * FROM pg_stat_activity WHERE state = 'active';
SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;

# Redis
redis-cli INFO
redis-cli MONITOR

# Kafka
kafka-consumer-groups --bootstrap-server localhost:9092 --describe --group ai-platform

# Milvus
curl http://localhost:9091/healthz

# Elasticsearch
curl http://localhost:9200/_cluster/health

# LLM
curl http://localhost:8001/v1/models
```

## 11.4 RCA Template

```markdown
## RCA: [ชื่อปัญหา]

### 1. Symptom
- อะไรผิดปกติ
- วัดได้เท่าไหร่
- เริ่มเมื่อไหร่

### 2. Impact
- กระทบ tenant ไหน
- กระทบ user กี่คน
- กระทบ revenue เท่าไหร่

### 3. Timeline
- t=0 เกิดอะไร
- t=1 เกิดอะไร

### 4. 5 Whys
1. ...
2. ...
3. ...
4. ...
5. ...

### 5. Root Cause
- สาเหตุที่แท้จริง

### 6. Action Items
- [ ] Short-term
- [ ] Mid-term
- [ ] Long-term

### 7. Prevention
- มาตรการป้องกัน

### 8. Lesson Learned
- บทเรียน
```

---

# 12. Templates และ Checklists

## 12.1 Module Creation Template

```markdown
# Module: {name}

## Metadata
- Layer: {layer}
- Prefix: {prefix}
- Schema: public
- Tables: {prefix}_*

## Files (58)
- 42 Python files
- 3 SQL files
- 1 Alembic file
- 7 Test files
- 3 Docs files
- 2 Routing files (แก้)

## Entities (7)
1. {Entity1}
2. {Entity2}
...

## Value Objects (5)
1. {VO1}
...

## Events (7)
1. {Event1}
...

## Enums (6)
1. {Enum1}
...

## Exceptions (11)
1. {Error1}
...

## Endpoints (21)
1. POST /api/v1/{module}/{resource}
...

## Tests
- Unit: 15
- Integration: 8
- Property: 6
- Manual: 15
```

## 12.2 Code Review Checklist

```markdown
- [ ] Code ตรงตาม requirement
- [ ] มี test ครบ
- [ ] ผ่าน lint (ruff, mypy)
- [ ] ไม่มี `...` หรือ TODO
- [ ] Type hints ครบ
- [ ] Docstring 2 ภาษา
- [ ] Error handling ตาม pattern
- [ ] ไม่ log PII
- [ ] ไม่ commit() ใน repository
- [ ] ใช้ Decimal สำหรับ cost
- [ ] Migration ถูกต้อง
- [ ] RLS เปิด
- [ ] Trigger สร้าง
- [ ] Test ผ่านทั้งหมด
- [ ] Coverage ≥ 85%
```

## 12.3 Deployment Checklist

```markdown
- [ ] Tests ผ่านทั้งหมด
- [ ] Coverage ≥ 85%
- [ ] Lint ผ่าน
- [ ] Type check ผ่าน
- [ ] Migration ทดสอบแล้ว
- [ ] Backup database แล้ว
- [ ] Canary deploy
- [ ] Monitor 15 นาที
- [ ] ขยาย 100%
- [ ] Health check ผ่าน
- [ ] Smoke test ผ่าน
- [ ] Rollback plan พร้อม
```

## 12.4 Daily Operations Checklist

```markdown
- [ ] ตรวจสอบ dashboard
- [ ] ตรวจสอบ alerts
- [ ] ตรวจสอบ log errors
- [ ] ตรวจสอบ slow queries
- [ ] ตรวจสอบ cache hit ratio
- [ ] ตรวจสอบ disk usage
- [ ] ตรวจสอบ database connections
- [ ] ตรวจสอบ Kafka lag
- [ ] ตรวจสอบ vector DB health
- [ ] ตรวจสอบ LLM quota
```

## 12.5 Postmortem Template

```markdown
# Postmortem: [Incident]

## Metadata
- Date: YYYY-MM-DD
- Duration: HH:MM
- Severity: P0/P1/P2/P3
- Author: {name}

## Summary
- เกิดอะไรขึ้น
- กระทบอะไร
- แก้อย่างไร

## Timeline
- HH:MM เกิดอะไร
- HH:MM เกิดอะไร

## Root Cause
- สาเหตุ

## Impact
- Users: N
- Revenue: $N
- SLO: N%

## Action Items
- [ ] Short-term
- [ ] Mid-term
- [ ] Long-term

## Lessons Learned
- บทเรียน
```

---

# 13. ภาคผนวก

## 13.1 คำสั่งที่ใช้บ่อย

```bash
# Development
poetry install                              # ติดตั้ง dependencies
poetry shell                                # activate virtualenv
uvicorn app.app:app --reload                # start server
pytest tests/ -v                            # run tests
ruff check .                                # lint
mypy app                                    # type check

# Database
alembic upgrade head                        # apply migrations
alembic downgrade -1                        # rollback 1 step
alembic revision --autogenerate -m "msg"    # create migration
psql -h localhost -U user aiplatform        # connect

# Docker
docker-compose up -d                        # start infrastructure
docker-compose down                         # stop
docker-compose logs -f postgres             # logs

# Kubernetes
kubectl get pods                            # list pods
kubectl logs -f deployment/ai-platform      # logs
kubectl rollout undo deployment/ai-platform # rollback
kubectl scale deployment/ai-platform --replicas=3

# Git
git checkout -b feature/XXX-123-desc        # create branch
git commit -m "feat(module): description"   # commit
git push origin feature/XXX-123-desc        # push
```

## 13.2 Error Codes

| Code | HTTP | Meaning |
|---|---|---|
| `DOMAIN_ERROR` | 400 | Domain exception |
| `NOT_FOUND` | 404 | Resource not found |
| `TRAINING_FAILED` | 500 | Training pipeline failed |
| `INVALID_INPUT` | 422 | Validation error |
| `SCHEMA_MISMATCH` | 422 | Schema mismatch |
| `DRIFT_DETECTED` | 409 | Drift beyond threshold |
| `RATE_LIMITED` | 429 | Too many requests |
| `IDEMPOTENCY_CONFLICT` | 409 | Idempotency key conflict |

## 13.3 Glossary

| คำศัพท์ | ความหมาย |
|---|---|
| **RAG** | Retrieval-Augmented Generation |
| **LLM** | Large Language Model |
| **Embedding** | Vector representation of text |
| **Chunk** | ส่วนย่อยของ document |
| **Vector DB** | ฐานข้อมูลเวกเตอร์ |
| **Reranker** | โมเดลจัดอันดับ |
| **Faithfulness** | คำตอบตรงกับ context |
| **RLS** | Row-Level Security |
| **Idempotency** | คำขอซ้ำได้ผลเดิม |
| **Drift** | การเปลี่ยนแปลงของการกระจายข้อมูล |
| **Feature Store** | ที่เก็บ feature |
| **MLOps** | ML Operations |
| **SSE** | Server-Sent Events |
| **NFR** | Non-Functional Requirement |

## 13.4 แหล่งอ้างอิง

| แหล่ง | URL |
|---|---|
| FastAPI Docs | https://fastapi.tiangolo.com |
| SQLAlchemy 2.0 | https://docs.sqlalchemy.org |
| Pydantic v2 | https://docs.pydantic.dev |
| LangChain | https://python.langchain.com |
| LlamaIndex | https://docs.llamaindex.ai |
| Milvus | https://milvus.io/docs |
| RAGAS | https://docs.ragas.io |
| MLflow | https://mlflow.org/docs |
| Feast | https://docs.feast.dev |
| vLLM | https://docs.vllm.ai |

## 13.5 ติดต่อทีม

| บทบาท | ชื่อ | ติดต่อ |
|---|---|---|
| Tech Lead | — | tech-lead@org.com |
| Backend Lead | — | backend@org.com |
| ML Lead | — | ml@org.com |
| DevOps Lead | — | devops@org.com |
| QA Lead | — | qa@org.com |
| Product Owner | — | product@org.com |

---

# สรุป

คู่มือการทำงานฉบับนี้ครอบคลุม:

1. **บทนำและภาพรวม** — วัตถุประสงค์ ขอบเขต บทบาท Roadmap
2. **สถาปัตยกรรมระบบ** — ภาพรวม Stack Data Flow
3. **โครงสร้าง Modules** — 12 modules, โครงสร้างมาตรฐาน
4. **มาตรฐานการพัฒนา** — Global Constraints, Coding Standards, Git Workflow
5. **ขั้นตอนการทำงาน** — Feature Development, Module Creation, Code Review
6. **การติดตั้งและตั้งค่า** — Prerequisites, Environment, Docker
7. **การพัฒนา Module** — 4 layers, Templates
8. **การทดสอบ** — Unit, Integration, Property, Manual
9. **การ Deploy** — CI/CD, Canary, Rollback
10. **การ Operations** — Monitoring, Daily/Weekly/Monthly, Runbook
11. **การแก้ปัญหา** — Troubleshooting, RCA
12. **Templates และ Checklists** — Module, Code Review, Deployment, Daily Ops, Postmortem
13. **ภาคผนวก** — คำสั่ง, Error Codes, Glossary, แหล่งอ้างอิง, ติดต่อทีม

---

**📌 เอกสารนี้เป็นคู่มือการทำงานฉบับสมบูรณ์สำหรับโครงการ Enterprise AI Chatbot + KM ด้วย LLM/RAG — ใช้เป็นเอกสารอ้างอิงหลักสำหรับทีมพัฒนา DevOps และ Operations**

**เวอร์ชัน:** 1.0
**ปรับปรุงล่าสุด:** 2026
**สถานะ:** ใช้งานจริง (Production-Ready)
