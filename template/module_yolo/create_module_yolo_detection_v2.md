# 🎯 YOLO Detection — 7 Use Cases ที่ต้องเพิ่ม

จาก Manual และ Generator ที่มีอยู่ ผมวิเคราะห์แล้วว่าคุณต้องการ **7 Use Cases** เฉพาะทาง เพิ่มจาก generic detection ที่มีอยู่:

| # | Use Case | คำอธิบาย | Domain |
|---|----------|----------|--------|
| 1 | **YOLO Settings** | ตั้งค่า platform (default model, device, thresholds, storage) | Config |
| 2 | **YOLO Report** | รายงานผล (training, inference, accuracy, drift) | Analytics |
| 3 | **YOLO Category** | หมวดหมู่สินค้า/โรค/พืช (category taxonomy) | Taxonomy |
| 4 | **YOLO on FastAPI** | Deployment patterns (sync/async/streaming/worker) | Platform |
| 5 | **YOLO ตรวจนับสินค้า** | Product counting (shelf, warehouse, checkout) | Retail |
| 6 | **YOLO ตรวจโรคพืช** | Plant disease detection (leaf, severity, treatment) | Agriculture |
| 7 | **YOLO ตรวจการเติบโตพืช** | Plant growth monitoring (stage, height, health) | Agriculture |

---

## 📐 สถาปัตยกรรมที่แนะนำ

### Option A: **Sub-modules ภายใน `yolo`** (แนะนำ)

```
app/modules/yolo/
├── domain/
│   ├── settings/          ← #1 Settings
│   ├── report/            ← #2 Report
│   ├── category/          ← #3 Category
│   └── applications/      ← #5,6,7 Use cases
├── application/
│   ├── settings_use_case.py
│   ├── report_use_case.py
│   ├── category_use_case.py
│   ├── product_counting_use_case.py
│   ├── plant_disease_use_case.py
│   └── plant_growth_use_case.py
├── infrastructure/
│   ├── models_settings.py
│   ├── models_report.py
│   ├── models_category.py
│   └── ...
└── presentation/
    ├── router_settings.py
    ├── router_report.py
    ├── router_category.py
    ├── router_counting.py
    ├── router_plant_disease.py
    └── router_plant_growth.py
```

**ข้อดี:** ใช้ infra ร่วมกัน (Ultralytics, S3, Cache) — ไม่ duplicate

### Option B: **Modules แยก** (`yolo_settings`, `yolo_report`, ...)

**ข้อเสีย:** duplicate infra, สับสน — **ไม่แนะนำ**

---

## 1️⃣ YOLO Settings

### Domain

```python
# domain/settings/entities.py
@dataclass(frozen=True, slots=True)
class PlatformSettings:
    """TH: ตั้งค่า platform YOLO | EN: YOLO platform settings"""
    tenant_id: uuid.UUID
    default_model: str = "yolov8n.pt"
    device: str = "auto"              # auto | cpu | cuda:0
    conf_threshold: float = 0.25
    iou_threshold: float = 0.45
    max_batch_size: int = 32
    timeout_seconds: int = 30
    cache_ttl: int = 300
    artifact_bucket: str = "yolo-artifacts"
    enable_tensorrt: bool = False
    enable_half_precision: bool = True
    max_concurrent_trainings: int = 1
    retention_days: int = 90
```

### Application

```python
# application/settings_use_case.py
class SettingsUseCase:
    async def get_settings(self, ctx) -> dict: ...
    async def update_settings(self, ctx, patch: dict) -> dict: ...
    async def reset_to_defaults(self, ctx) -> dict: ...
    async def validate_settings(self, ctx, patch: dict) -> list[str]: ...
```

### Presentation (4 endpoints)

```
GET    /api/v1/yolo/settings               — ดู settings ปัจจุบัน
PATCH  /api/v1/yolo/settings               — อัปเดต
POST   /api/v1/yolo/settings/reset         — reset to defaults
POST   /api/v1/yolo/settings/validate      — validate ก่อน save
```

### DB Table

```sql
CREATE TABLE public.yolo_settings (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       uuid NOT NULL UNIQUE,
    default_model   varchar(50) NOT NULL DEFAULT 'yolov8n.pt',
    device          varchar(20) NOT NULL DEFAULT 'auto',
    conf_threshold  numeric(4,3) NOT NULL DEFAULT 0.25,
    iou_threshold   numeric(4,3) NOT NULL DEFAULT 0.45,
    max_batch_size  int4 NOT NULL DEFAULT 32,
    timeout_seconds int4 NOT NULL DEFAULT 30,
    cache_ttl       int4 NOT NULL DEFAULT 300,
    artifact_bucket varchar(200) NOT NULL DEFAULT 'yolo-artifacts',
    enable_tensorrt bool NOT NULL DEFAULT false,
    enable_half     bool NOT NULL DEFAULT true,
    max_trainings   int4 NOT NULL DEFAULT 1,
    retention_days  int4 NOT NULL DEFAULT 90,
    settings_json   jsonb NOT NULL DEFAULT '{}',
    created_at      timestamptz NOT NULL DEFAULT now(),
    updated_at      timestamptz NOT NULL DEFAULT now()
);
```

---

## 2️⃣ YOLO Report

### Domain

```python
# domain/report/entities.py
@dataclass(frozen=True, slots=True)
class TrainingReport:
    """TH: รายงานการฝึก | EN: training report"""
    training_id: uuid.UUID
    model_id: uuid.UUID
    dataset_id: uuid.UUID
    model_type: str
    epochs_completed: int
    duration_ms: int
    final_mAP50: float
    final_mAP50_95: float
    best_epoch: int
    loss_curve: tuple[tuple[int, float], ...]
    per_class_ap: tuple[tuple[str, float], ...]
    generated_at: datetime


@dataclass(frozen=True, slots=True)
class InferenceReport:
    """TH: รายงานการ inference | EN: inference report"""
    model_id: uuid.UUID
    period_start: datetime
    period_end: datetime
    total_inferences: int
    total_detections: int
    avg_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    cache_hit_rate: float
    top_classes: tuple[tuple[str, int], ...]
    drift_score: float
```

### Application

```python
class ReportUseCase:
    async def training_report(self, ctx, training_id) -> TrainingReport: ...
    async def model_report(self, ctx, model_id, period_days: int = 30) -> InferenceReport: ...
    async def dataset_report(self, ctx, dataset_id) -> dict: ...
    async def tenant_summary(self, ctx) -> dict: ...
    async def export_report_pdf(self, ctx, report_id) -> bytes: ...
    async def export_report_csv(self, ctx, report_id) -> str: ...
```

### Presentation (6 endpoints)

```
GET  /api/v1/yolo/reports/training/{training_id}
GET  /api/v1/yolo/reports/model/{model_id}?period_days=30
GET  /api/v1/yolo/reports/dataset/{dataset_id}
GET  /api/v1/yolo/reports/summary
POST /api/v1/yolo/reports/{report_id}/export/pdf
POST /api/v1/yolo/reports/{report_id}/export/csv
```

### Reports ที่ควรมี

| Report | Metrics |
|--------|---------|
| **Training** | Loss curve, mAP progression, per-class AP, best epoch |
| **Inference** | Latency (p50/95/99), cache hit rate, detections/day |
| **Dataset** | Class distribution, image splits, hard examples |
| **Drift** | Score over time, class distribution shift |
| **Cost** | GPU hours, S3 storage, inferences/day |
| **Summary** | Cross-model comparison, top performers |

---

## 3️⃣ YOLO Category

### Domain

```python
# domain/category/entities.py
@dataclass(frozen=True, slots=True)
class Category:
    """TH: หมวดหมู่ | EN: category taxonomy"""
    id: uuid.UUID
    tenant_id: uuid.UUID
    parent_id: uuid.UUID | None
    slug: str                    # 'fresh-produce', 'leafy-greens'
    name_th: str
    name_en: str
    description: str
    icon: str | None
    color: str
    sort_order: int
    is_active: bool
    class_count: int             # จำนวน class ที่อยู่ใน category นี้
    metadata: dict


class CategoryTree:
    """TH: ต้นไม้หมวดหมู่ | EN: category tree"""
    def __init__(self, categories: list[Category]) -> None:
        self._by_parent: dict[uuid.UUID | None, list[Category]] = {}
        for c in categories:
            self._by_parent.setdefault(c.parent_id, []).append(c)

    def children(self, parent_id: uuid.UUID | None) -> list[Category]: ...
    def ancestors(self, category_id: uuid.UUID) -> list[Category]: ...
    def descendants(self, category_id: uuid.UUID) -> list[Category]: ...
    def depth(self, category_id: uuid.UUID) -> int: ...
```

### ตัวอย่าง Taxonomy

```
🏪 สินค้า (Retail)
├── 🥬 ผักสด
│   ├── 🥬 ผักใบเขียว (คะน้า, ผักบุ้ง)
│   ├── 🥕 ผักหัว (แครอท, มัน)
│   └── 🍅 ผักผล (มะเขือเทศ, แตงกวา)
├── 🍎 ผลไม้
└── 🥩 เนื้อสัตว์

🌱 โรคพืช (Plant Disease)
├── 🍃 โรคใบ
│   ├── ราสนิม
│   ├── ใบจุด
│   └── ใบไหม้
├── 🍂 โรคลำต้น
└── 🌾 โรคเชื้อรา

🌿 การเติบโต (Growth Stage)
├── 🌱 ระยะต้นกล้า (Seedling)
├── 🌿 ระยะเจริญเติบโต (Vegetative)
├── 🌸 ระยะออกดอก (Flowering)
└── 🍎 ระยะติดผล (Fruiting)
```

### Application

```python
class CategoryUseCase:
    async def create_category(self, ctx, payload) -> Category: ...
    async def get_category(self, ctx, category_id) -> Category: ...
    async def get_tree(self, ctx, root_id: uuid.UUID | None = None) -> dict: ...
    async def list_categories(self, ctx, parent_id: uuid.UUID | None) -> list[Category]: ...
    async def move_category(self, ctx, id, new_parent_id) -> Category: ...
    async def assign_class(self, ctx, class_id, category_id) -> None: ...
    async def unassign_class(self, ctx, class_id) -> None: ...
    async def delete_category(self, ctx, id, cascade: bool = False) -> None: ...
```

### Presentation (8 endpoints)

```
POST   /api/v1/yolo/categories                    — create
GET    /api/v1/yolo/categories                    — list (flat)
GET    /api/v1/yolo/categories/tree               — tree
GET    /api/v1/yolo/categories/{id}               — detail
PATCH  /api/v1/yolo/categories/{id}               — update
POST   /api/v1/yolo/categories/{id}/move          — move parent
DELETE /api/v1/yolo/categories/{id}               — delete
POST   /api/v1/yolo/categories/{id}/classes       — assign class
```

### DB Table

```sql
CREATE TABLE public.yolo_categories (
    id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id    uuid NOT NULL,
    parent_id    uuid REFERENCES public.yolo_categories(id) ON DELETE RESTRICT,
    slug         varchar(100) NOT NULL,
    name_th      varchar(200) NOT NULL,
    name_en      varchar(200) NOT NULL,
    description  text NOT NULL DEFAULT '',
    icon         varchar(20),
    color        varchar(7) NOT NULL DEFAULT '#3B82F6',
    sort_order   int4 NOT NULL DEFAULT 0,
    is_active    bool NOT NULL DEFAULT true,
    metadata_json jsonb NOT NULL DEFAULT '{}',
    created_at   timestamptz NOT NULL DEFAULT now(),
    updated_at   timestamptz NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, slug),
    CHECK (parent_id IS NULL OR parent_id != id)
);
CREATE INDEX ix_yolo_cat_tenant ON public.yolo_categories(tenant_id);
CREATE INDEX ix_yolo_cat_parent ON public.yolo_categories(parent_id);
CREATE INDEX ix_yolo_cat_slug ON public.yolo_categories(tenant_id, slug);
```

---

## 4️⃣ YOLO on FastAPI — Deployment Patterns

### 4.1 Architecture Patterns

```python
# app/modules/yolo/presentation/deployment.py

class YOLODeploymentPattern:
    """TH: pattern การ deploy YOLO บน FastAPI"""
    
    # Pattern 1: Sync (blocking) — สำหรับ CLI/testing
    @staticmethod
    def sync_predict(image: bytes) -> list[Detection]: ...
    
    # Pattern 2: Async + to_thread — แนะนำ (default)
    @staticmethod
    async def async_predict(image: bytes) -> list[Detection]: ...
    
    # Pattern 3: Batch async — สำหรับ throughput สูง
    @staticmethod
    async def batch_async(images: list[bytes]) -> list[list[Detection]]: ...
    
    # Pattern 4: SSE streaming — สำหรับ video
    @staticmethod
    async def stream_sse(video_uri: str) -> AsyncIterator[dict]: ...
    
    # Pattern 5: Background worker — สำหรับ training
    @staticmethod
    async def train_background(training_id: uuid.UUID) -> None: ...
    
    # Pattern 6: WebSocket — real-time bi-directional
    @staticmethod
    async def ws_detect(websocket: WebSocket) -> None: ...
```

### 4.2 FastAPI App Configuration

```python
# app/app.py additions
from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    from app.modules.yolo.infrastructure.services import LRUModelRegistry
    from app.modules.yolo.presentation.dependencies import (
        _get_registry, _get_trainer, _get_store,
    )
    registry = _get_registry()
    trainer = _get_trainer()
    store = _get_store()
    
    # Pre-warm default model ถ้ามี
    default_model = os.getenv("YOLO_DEFAULT_MODEL", "yolov8n.pt")
    if default_model:
        try:
            await registry.load(uuid.UUID(int=0), default_model, "pt")
        except Exception:
            pass
    
    # Start background worker (optional)
    from app.modules.yolo.infrastructure.worker import start_worker
    worker_task = asyncio.create_task(start_worker())
    
    yield
    
    # Shutdown
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass


app = FastAPI(lifespan=lifespan)

# Register routers
from app.modules.yolo.presentation.router import router as yolo_router
from app.modules.yolo.presentation.router_settings import router as yolo_settings_router
from app.modules.yolo.presentation.router_report import router as yolo_report_router
from app.modules.yolo.presentation.router_category import router as yolo_category_router
from app.modules.yolo.presentation.router_counting import router as yolo_counting_router
from app.modules.yolo.presentation.router_plant_disease import router as yolo_plant_disease_router
from app.modules.yolo.presentation.router_plant_growth import router as yolo_plant_growth_router

app.include_router(yolo_router, prefix="/api/v1")
app.include_router(yolo_settings_router, prefix="/api/v1")
app.include_router(yolo_report_router, prefix="/api/v1")
app.include_router(yolo_category_router, prefix="/api/v1")
app.include_router(yolo_counting_router, prefix="/api/v1")
app.include_router(yolo_plant_disease_router, prefix="/api/v1")
app.include_router(yolo_plant_growth_router, prefix="/api/v1")
```

### 4.3 Background Worker

```python
# app/modules/yolo/infrastructure/worker.py
"""Training worker — แยก process สำหรับ long-running training"""

import asyncio
from loguru import logger
from app.modules.yolo.presentation.dependencies import (
    _get_trainer, _get_store,
)

async def start_worker():
    """Poll for pending trainings จาก queue"""
    while True:
        try:
            # ... poll DB หรือ Redis queue
            await asyncio.sleep(5)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"worker error: {e}")
            await asyncio.sleep(10)
```

### 4.4 Scaling Patterns

| Pattern | Use Case | Pros | Cons |
|---------|----------|------|------|
| **Single-process** | Dev / small | ง่าย | ไม่ scale |
| **Multi-worker** | Production | Scale ได้ | โหลด model ซ้ำ |
| **Dedicated GPU worker** | High throughput | GPU 100% | ซับซ้อน |
| **Queue-based** | Batch | Retry ได้ | Latency สูง |
| **ONNX Runtime** | CPU prod | เร็ว | Export ก่อน |

### 4.5 Deployment Endpoints

```
GET  /api/v1/yolo/deployment/health        — health check (GPU, models, cache)
GET  /api/v1/yolo/deployment/metrics       — Prometheus metrics
GET  /api/v1/yolo/deployment/readyz        — readiness (model loaded)
GET  /api/v1/yolo/deployment/livez         — liveness
GET  /api/v1/yolo/deployment/registry      — loaded models
POST /api/v1/yolo/deployment/registry/load — pre-load model
POST /api/v1/yolo/deployment/registry/unload — unload
```

---

## 5️⃣ YOLO ตรวจนับสินค้า (Product Counting)

### Business Rules

```python
# domain/applications/counting.py
@dataclass(frozen=True, slots=True)
class CountingConfig:
    """TH: config การนับ | EN: counting config"""
    mode: str = "shelf"          # shelf | warehouse | checkout | conveyor
    line_position: float = 0.5   # สำหรับ conveyor (0-1)
    line_orientation: str = "vertical"  # vertical | horizontal
    class_filter: tuple[int, ...] = ()   # นับเฉพาะ class เหล่านี้
    min_confidence: float = 0.5
    merge_distance: float = 0.05  # merge bbox ที่ใกล้กัน
    track_persistence: int = 5    # frames ที่ต้อง track ก่อนนับ
    deduplication: bool = True


@dataclass(frozen=True, slots=True)
class CountingResult:
    """TH: ผลการนับ | EN: counting result"""
    total_count: int
    per_class_count: tuple[tuple[str, int], ...]
    regions: tuple[dict, ...]      # สำหรับ shelf (แยกชั้น)
    confidence_avg: float
    processing_ms: int
    warnings: tuple[str, ...]


class ProductCounter:
    """TH: ตัวนับสินค้า | EN: product counter"""
    
    def count_shelf(self, detections: list[Detection], img_size: tuple[int, int]) -> CountingResult:
        """นับบนชั้นวาง — แยกตาม shelf row"""
        # 1. Sort bboxes by y_center
        # 2. Cluster into rows (gap > threshold = new row)
        # 3. Count per row
        ...
    
    def count_conveyor(self, detections: list[Detection], 
                        line_pos: float, orientation: str) -> CountingResult:
        """นับบนสายพาน — ใช้ virtual line + tracking"""
        # 1. Filter detections crossing line
        # 2. Track object_id ข้าม frame
        # 3. Count unique objects
        ...
    
    def count_checkout(self, detections: list[Detection]) -> CountingResult:
        """นับที่จุดชำระเงิน — merge สินค้าที่ทับกัน"""
        ...
```

### Application

```python
class ProductCountingUseCase:
    async def count_image(self, ctx, model_id, image_bytes, 
                           config: CountingConfig) -> CountingResult: ...
    async def count_video(self, ctx, model_id, video_uri,
                           config: CountingConfig) -> AsyncIterator[CountingResult]: ...
    async def count_batch(self, ctx, model_id, images, config) -> list[CountingResult]: ...
    async def create_counting_session(self, ctx, config) -> dict: ...
    async def get_session_results(self, ctx, session_id) -> dict: ...
    async def export_session_csv(self, ctx, session_id) -> str: ...
```

### Presentation (6 endpoints)

```
POST /api/v1/yolo/counting/image            — นับรูปเดียว
POST /api/v1/yolo/counting/batch            — นับหลายรูป
POST /api/v1/yolo/counting/video            — นับจาก video (SSE)
POST /api/v1/yolo/counting/sessions         — create session
GET  /api/v1/yolo/counting/sessions/{id}    — get results
GET  /api/v1/yolo/counting/sessions/{id}/csv — export
```

### Request/Response

```json
POST /api/v1/yolo/counting/image
{
  "model_id": "uuid",
  "mode": "shelf",
  "class_filter": [0, 1, 2],
  "min_confidence": 0.5,
  "merge_distance": 0.05
}

Response 200:
{
  "session_id": "uuid",
  "total_count": 47,
  "per_class_count": [
    {"class_name": "cola", "count": 12},
    {"class_name": "pepsi", "count": 10},
    {"class_name": "water", "count": 25}
  ],
  "regions": [
    {"row": 1, "count": 15, "y_range": [0.1, 0.3]},
    {"row": 2, "count": 18, "y_range": [0.35, 0.55]},
    {"row": 3, "count": 14, "y_range": [0.6, 0.8]}
  ],
  "confidence_avg": 0.87,
  "processing_ms": 124,
  "warnings": []
}
```

### DB Tables

```sql
CREATE TABLE public.yolo_counting_sessions (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       uuid NOT NULL,
    model_id        uuid NOT NULL,
    mode            varchar(20) NOT NULL,
    config_json     jsonb NOT NULL DEFAULT '{}',
    total_count     int4 NOT NULL DEFAULT 0,
    status          varchar(20) NOT NULL DEFAULT 'RUNNING',
    started_at      timestamptz NOT NULL DEFAULT now(),
    finished_at     timestamptz,
    created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE public.yolo_counting_results (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      uuid NOT NULL REFERENCES public.yolo_counting_sessions(id) ON DELETE CASCADE,
    tenant_id       uuid NOT NULL,
    frame_index     int4,
    total_count     int4 NOT NULL,
    per_class_json  jsonb NOT NULL DEFAULT '[]',
    regions_json    jsonb NOT NULL DEFAULT '[]',
    confidence_avg  numeric(4,3),
    processing_ms   int4,
    created_at      timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ix_yolo_counting_session ON public.yolo_counting_results(session_id);
```

---

## 6️⃣ YOLO ตรวจโรคพืช (Plant Disease Detection)

### Business Rules

```python
# domain/applications/plant_disease.py
@dataclass(frozen=True, slots=True)
class DiseaseSeverity:
    """TH: ระดับความรุนแรง | EN: severity level"""
    level: str          # healthy | mild | moderate | severe | critical
    percentage: float   # % ของพื้นที่ใบที่เป็นโรค
    score: float        # 0.0 - 1.0


@dataclass(frozen=True, slots=True)
class DiseaseDetection:
    """TH: ผลตรวจโรค | EN: disease detection"""
    bbox: BBox
    disease_id: uuid.UUID
    disease_code: str            # 'rice-blast', 'tomato-late-blight'
    disease_name_th: str
    disease_name_en: str
    confidence: float
    severity: DiseaseSeverity
    affected_area_pct: float
    pathogen_type: str           # fungal | bacterial | viral | pest


@dataclass(frozen=True, slots=True)
class PlantDiagnosis:
    """TH: การวินิจฉัยโรคพืช | EN: plant diagnosis"""
    image_id: uuid.UUID
    plant_species: str | None
    detections: tuple[DiseaseDetection, ...]
    overall_severity: str
    overall_health_score: float  # 0-100
    recommendations: tuple[str, ...]
    treatment_plan: tuple[dict, ...]
    follow_up_days: int
    confidence: float


class PlantDiseaseDiagnoser:
    """TH: ตัววินิจฉัยโรคพืช | EN: plant disease diagnoser"""
    
    DISEASE_CATALOG = {
        "rice-blast": {
            "name_th": "โรคไหม้ข้าว",
            "name_en": "Rice Blast",
            "pathogen": "fungal",
            "treatment": ["fungicide: tricyclazole", "reduce nitrogen"],
        },
        "tomato-late-blight": {
            "name_th": "โรคใบไหม้มะเขือเทศ",
            "name_en": "Tomato Late Blight",
            "pathogen": "fungal",
            "treatment": ["fungicide: chlorothalonil", "remove infected"],
        },
        # ... 100+ diseases
    }
    
    def diagnose(self, detections: list[Detection], 
                  plant_species: str | None) -> PlantDiagnosis:
        """วินิจฉัยจาก detections"""
        # 1. Map class_id → disease_code
        # 2. คำนวณ severity จาก affected_area
        # 3. Generate recommendations
        # 4. Build treatment plan
        ...
    
    def calc_severity(self, bbox: BBox, leaf_area: float) -> DiseaseSeverity:
        """คำนวณ severity level"""
        pct = bbox.width * bbox.height / max(leaf_area, 1e-6)
        if pct < 0.05: return DiseaseSeverity("mild", pct, pct / 0.05)
        if pct < 0.20: return DiseaseSeverity("moderate", pct, 0.25 + pct / 0.20 * 0.5)
        if pct < 0.50: return DiseaseSeverity("severe", pct, 0.75 + pct / 0.50 * 0.2)
        return DiseaseSeverity("critical", pct, 0.95 + min(pct, 1.0) * 0.05)
```

### Application

```python
class PlantDiseaseUseCase:
    async def diagnose_image(self, ctx, model_id, image_bytes,
                              plant_species: str | None = None) -> PlantDiagnosis: ...
    async def diagnose_batch(self, ctx, model_id, images, 
                              plant_species: str | None = None) -> list[PlantDiagnosis]: ...
    async def diagnose_video(self, ctx, model_id, video_uri) -> AsyncIterator[PlantDiagnosis]: ...
    async def get_disease_catalog(self, ctx, pathogen_type: str | None = None) -> list[dict]: ...
    async def get_treatment_plan(self, ctx, disease_code: str) -> dict: ...
    async def create_monitoring_plan(self, ctx, field_id: uuid.UUID, 
                                       schedule_days: int) -> dict: ...
    async def get_field_history(self, ctx, field_id: uuid.UUID) -> dict: ...
```

### Presentation (7 endpoints)

```
POST /api/v1/yolo/plant-disease/diagnose         — วินิจฉัยรูปเดียว
POST /api/v1/yolo/plant-disease/diagnose/batch   — วินิจฉัยหลายรูป
POST /api/v1/yolo/plant-disease/diagnose/video   — วินิจฉัย video (SSE)
GET  /api/v1/yolo/plant-disease/catalog          — disease catalog
GET  /api/v1/yolo/plant-disease/treatment/{code} — treatment plan
POST /api/v1/yolo/plant-disease/fields/{id}/plan — monitoring plan
GET  /api/v1/yolo/plant-disease/fields/{id}/history — field history
```

### Response

```json
POST /api/v1/yolo/plant-disease/diagnose
{
  "model_id": "uuid",
  "plant_species": "rice",
  "image_base64": "..."
}

Response 200:
{
  "diagnosis_id": "uuid",
  "plant_species": "rice",
  "overall_severity": "moderate",
  "overall_health_score": 62.5,
  "detections": [
    {
      "disease_code": "rice-blast",
      "disease_name_th": "โรคไหม้ข้าว",
      "disease_name_en": "Rice Blast",
      "pathogen_type": "fungal",
      "confidence": 0.91,
      "severity": {
        "level": "moderate",
        "percentage": 0.15,
        "score": 0.45
      },
      "affected_area_pct": 0.15
    }
  ],
  "recommendations": [
    "พ่นสารป้องกันเชื้อรา tricyclazole 20% WP",
    "ลดปริมาณปุ๋ยไนโตรเจน",
    "เพิ่มการระบายอากาศในแปลงนา"
  ],
  "treatment_plan": [
    {"day": 0, "action": "spray", "product": "tricyclazole", "dose": "20g/20L"},
    {"day": 7, "action": "inspect", "notes": "ประเมินผล"},
    {"day": 14, "action": "spray", "product": "tricyclazole", "dose": "20g/20L"}
  ],
  "follow_up_days": 7,
  "confidence": 0.91
}
```

### DB Tables

```sql
CREATE TABLE public.yolo_diseases (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       uuid,
    code            varchar(100) NOT NULL UNIQUE,
    name_th         varchar(200) NOT NULL,
    name_en         varchar(200) NOT NULL,
    pathogen_type   varchar(20) NOT NULL,
    plant_species   varchar(200)[] DEFAULT '{}',
    description     text NOT NULL DEFAULT '',
    symptoms        text NOT NULL DEFAULT '',
    treatment_json  jsonb NOT NULL DEFAULT '[]',
    prevention_json jsonb NOT NULL DEFAULT '[]',
    severity_levels jsonb NOT NULL DEFAULT '[]',
    icon            varchar(20),
    reference_url   text,
    created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE public.yolo_plant_diagnoses (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       uuid NOT NULL,
    model_id        uuid NOT NULL,
    field_id        uuid,
    image_hash      varchar(64) NOT NULL,
    plant_species   varchar(200),
    detections_json jsonb NOT NULL DEFAULT '[]',
    overall_severity varchar(20) NOT NULL,
    health_score    numeric(5,2),
    recommendations jsonb NOT NULL DEFAULT '[]',
    treatment_plan  jsonb NOT NULL DEFAULT '[]',
    confidence      numeric(4,3),
    created_at      timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ix_yolo_diag_tenant ON public.yolo_plant_diagnoses(tenant_id, created_at DESC);
CREATE INDEX ix_yolo_diag_field ON public.yolo_plant_diagnoses(field_id, created_at DESC);
```

---

## 7️⃣ YOLO ตรวจการเติบโตพืช (Plant Growth Monitoring)

### Business Rules

```python
# domain/applications/plant_growth.py
class GrowthStage(StrEnum):
    """TH: ระยะการเติบโต | EN: growth stage"""
    SEEDLING = "seedling"       # 🌱 ต้นกล้า
    VEGETATIVE = "vegetative"   # 🌿 เจริญเติบโต
    FLOWERING = "flowering"     # 🌸 ออกดอก
    FRUITING = "fruiting"       # 🍎 ติดผล
    MATURE = "mature"           # 🌾 สุกแก่
    HARVEST = "harvest"         # ✂️ เก็บเกี่ยว


@dataclass(frozen=True, slots=True)
class GrowthMetrics:
    """TH: ตัวชี้วัดการเติบโต | EN: growth metrics"""
    stage: str
    stage_confidence: float
    plant_height_px: float
    plant_height_cm: float | None       # ถ้ามี reference
    leaf_area_px: float
    leaf_area_pct: float                # % ของภาพ
    leaf_count: int
    canopy_width_px: float
    greenness_index: float              # 0-1 (ExG)
    health_score: float                 # 0-100
    growth_rate_pct: float | None       # เทียบกับครั้งก่อน


@dataclass(frozen=True, slots=True)
class GrowthAssessment:
    """TH: การประเมินการเติบโต | EN: growth assessment"""
    plant_id: uuid.UUID | None
    field_id: uuid.UUID | None
    image_id: uuid.UUID
    metrics: GrowthMetrics
    stage_history: tuple[tuple[datetime, str], ...]
    predictions: tuple[dict, ...]       # คาดการณ์ล่วงหน้า
    alerts: tuple[str, ...]             # แจ้งเตือน
    recommendations: tuple[str, ...]


class PlantGrowthAnalyzer:
    """TH: ตัววิเคราะห์การเติบโต | EN: growth analyzer"""
    
    # ExG = 2G - R - B (Excess Green Index)
    def calc_greenness(self, image: np.ndarray) -> float:
        r = image[:, :, 0].astype(float)
        g = image[:, :, 1].astype(float)
        b = image[:, :, 2].astype(float)
        exg = 2 * g - r - b
        return float(np.mean(np.clip(exg / 255.0, 0, 1)))
    
    def detect_stage(self, detections: list[Detection], 
                      greenness: float) -> tuple[str, float]:
        """ตรวจระยะการเติบโต"""
        # Map class_id → stage
        # หรือใช้ heuristics จาก greenness + leaf area
        ...
    
    def estimate_height(self, detections: list[Detection], 
                         img_h: int, px_per_cm: float | None = None) -> tuple[float, float | None]:
        """ประเมินความสูง"""
        if not detections:
            return 0.0, None
        y_max = max(d.bbox.y_center + d.bbox.height / 2 for d in detections)
        y_min = min(d.bbox.y_center - d.bbox.height / 2 for d in detections)
        h_px = (y_max - y_min) * img_h
        h_cm = h_px / px_per_cm if px_per_cm else None
        return h_px, h_cm
    
    def predict_growth(self, history: list[GrowthMetrics], 
                        days_ahead: int = 7) -> list[dict]:
        """คาดการณ์การเติบโต"""
        # ใช้ linear regression จาก history
        ...
    
    def generate_alerts(self, metrics: GrowthMetrics, 
                         expected: GrowthMetrics | None) -> list[str]:
        """สร้างการแจ้งเตือน"""
        alerts = []
        if metrics.health_score < 50:
            alerts.append("สุขภาพพืชต่ำกว่าเกณฑ์")
        if metrics.growth_rate_pct is not None and metrics.growth_rate_pct < 0:
            alerts.append("การเติบโตลดลง")
        if expected and metrics.stage != expected.stage:
            alerts.append(f"ระยะการเติบโตไม่ตรงกับที่คาด ({metrics.stage} vs {expected.stage})")
        return alerts
```

### Application

```python
class PlantGrowthUseCase:
    async def assess_growth(self, ctx, model_id, image_bytes,
                            field_id: uuid.UUID | None = None,
                            plant_id: uuid.UUID | None = None,
                            px_per_cm: float | None = None) -> GrowthAssessment: ...
    async def assess_batch(self, ctx, model_id, images, field_id) -> list[GrowthAssessment]: ...
    async def assess_video(self, ctx, model_id, video_uri, field_id) -> AsyncIterator[GrowthAssessment]: ...
    async def get_field_timeline(self, ctx, field_id, days: int = 30) -> dict: ...
    async def predict_harvest(self, ctx, field_id) -> dict: ...
    async def create_growth_plan(self, ctx, field_id, crop_type: str, 
                                   planting_date: datetime) -> dict: ...
    async def get_growth_chart(self, ctx, field_id, period_days: int) -> dict: ...
    async def compare_plants(self, ctx, plant_ids: list[uuid.UUID]) -> dict: ...
```

### Presentation (8 endpoints)

```
POST /api/v1/yolo/plant-growth/assess             — ประเมินรูปเดียว
POST /api/v1/yolo/plant-growth/assess/batch       — ประเมินหลายรูป
POST /api/v1/yolo/plant-growth/assess/video       — ประเมิน video (SSE)
GET  /api/v1/yolo/plant-growth/fields/{id}/timeline — timeline
GET  /api/v1/yolo/plant-growth/fields/{id}/chart  — กราฟการเติบโต
GET  /api/v1/yolo/plant-growth/fields/{id}/predict-harvest
POST /api/v1/yolo/plant-growth/fields/{id}/plan   — สร้างแผน
POST /api/v1/yolo/plant-growth/compare            — เปรียบเทียบ
```

### Response

```json
POST /api/v1/yolo/plant-growth/assess
{
  "model_id": "uuid",
  "field_id": "uuid",
  "plant_id": "uuid",
  "px_per_cm": 12.5,
  "image_base64": "..."
}

Response 200:
{
  "assessment_id": "uuid",
  "field_id": "uuid",
  "plant_id": "uuid",
  "metrics": {
    "stage": "vegetative",
    "stage_confidence": 0.88,
    "plant_height_px": 340.5,
    "plant_height_cm": 27.2,
    "leaf_area_px": 45230,
    "leaf_area_pct": 0.18,
    "leaf_count": 12,
    "canopy_width_px": 285.0,
    "greenness_index": 0.72,
    "health_score": 85.5,
    "growth_rate_pct": 12.3
  },
  "stage_history": [
    {"date": "2026-09-15", "stage": "seedling"},
    {"date": "2026-09-22", "stage": "vegetative"},
    {"date": "2026-10-01", "stage": "vegetative"}
  ],
  "predictions": [
    {"date": "2026-10-08", "stage": "flowering", "confidence": 0.75},
    {"date": "2026-10-20", "stage": "fruiting", "confidence": 0.62},
    {"date": "2026-11-05", "stage": "harvest", "confidence": 0.55}
  ],
  "alerts": [],
  "recommendations": [
    "พืชเติบโตตามปกติ ควรรดน้ำสม่ำเสมอ",
    "คาดว่าจะออกดอกใน 7 วัน เตรียมปุ๋ยฟอสฟอรัส"
  ]
}
```

### DB Tables

```sql
CREATE TABLE public.yolo_fields (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       uuid NOT NULL,
    name            varchar(200) NOT NULL,
    crop_type       varchar(100) NOT NULL,
    area_sqm        numeric(10,2),
    location_lat    numeric(10,7),
    location_lng    numeric(10,7),
    planting_date   date,
    expected_harvest date,
    px_per_cm       numeric(6,2),
    status          varchar(20) NOT NULL DEFAULT 'ACTIVE',
    metadata_json   jsonb NOT NULL DEFAULT '{}',
    created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE public.yolo_growth_assessments (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       uuid NOT NULL,
    field_id        uuid REFERENCES public.yolo_fields(id) ON DELETE CASCADE,
    plant_id        uuid,
    model_id        uuid NOT NULL,
    image_hash      varchar(64) NOT NULL,
    stage           varchar(20) NOT NULL,
    stage_confidence numeric(4,3),
    metrics_json    jsonb NOT NULL DEFAULT '{}',
    health_score    numeric(5,2),
    growth_rate_pct numeric(6,2),
    alerts_json     jsonb NOT NULL DEFAULT '[]',
    recommendations jsonb NOT NULL DEFAULT '[]',
    created_at      timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ix_yolo_growth_field ON public.yolo_growth_assessments(field_id, created_at DESC);
CREATE INDEX ix_yolo_growth_stage ON public.yolo_growth_assessments(field_id, stage, created_at DESC);
```

---

## 🗂️ สรุป Database Tables ทั้งหมด

| # | Table | Purpose |
|---|-------|---------|
| 1 | `yolo_datasets` | (มีอยู่) |
| 2 | `yolo_classes` | (มีอยู่) |
| 3 | `yolo_images` | (มีอยู่) |
| 4 | `yolo_annotations` | (มีอยู่) |
| 5 | `yolo_trainings` | (มีอยู่) |
| 6 | `yolo_models` | (มีอยู่) |
| 7 | `yolo_inferences` | (มีอยู่) |
| **8** | **`yolo_settings`** | #1 Settings |
| **9** | **`yolo_reports`** | #2 Report (cache) |
| **10** | **`yolo_categories`** | #3 Category |
| **11** | **`yolo_counting_sessions`** | #5 Counting |
| **12** | **`yolo_counting_results`** | #5 Counting |
| **13** | **`yolo_diseases`** | #6 Disease catalog |
| **14** | **`yolo_plant_diagnoses`** | #6 Disease results |
| **15** | **`yolo_fields`** | #7 Growth |
| **16** | **`yolo_growth_assessments`** | #7 Growth |

**รวม 16 tables** (7 เดิม + 9 ใหม่)

---

## 🚀 API Endpoints รวม

| หมวด | Endpoints |
|------|-----------|
| Core (เดิม) | 14 |
| **Settings** | 4 |
| **Report** | 6 |
| **Category** | 8 |
| **Deployment** | 7 |
| **Counting** | 6 |
| **Plant Disease** | 7 |
| **Plant Growth** | 8 |
| **รวม** | **60 endpoints** |

---

## 📋 ขั้นตอนการ Generate

```bash
# 1. Generate module หลัก (เดิม)
python create_module_yolo_detection.py all yolo 5 yolo --force

# 2. Generate extensions (ใหม่ — ต้องเขียนเพิ่ม)
python create_module_yolo_detection.py create-settings yolo --force
python create_module_yolo_detection.py create-report yolo --force
python create_module_yolo_detection.py create-category yolo --force
python create_module_yolo_detection.py create-deployment yolo --force
python create_module_yolo_detection.py create-counting yolo --force
python create_module_yolo_detection.py create-plant-disease yolo --force
python create_module_yolo_detection.py create-plant-growth yolo --force

# 3. Migrate
alembic upgrade head

# 4. Verify
python create_module_yolo_detection.py verify yolo

# 5. Run
uvicorn app.app:app --reload
```

---

## ❓ คำถามก่อน implement

1. **ต้องการให้ผมเขียน Generator extension** (เพิ่ม actions ใหม่ 7 actions ใน `create_module_yolo_detection.py`) หรือ
2. **ต้องการ code files โดยตรง** (แยกเป็นไฟล์ๆ ให้ copy ไปวาง) หรือ
3. **ต้องการแค่ design/schema** ก่อน แล้วค่อย implement ทีหลัง?

แนะนำ **Option 1** — เพิ่ม actions ใน Generator เพื่อให้ consistent กับ pattern เดิม + reusable

ถ้าเลือก Option 1 ผมจะเขียน:
- `create-settings` action → 4 ไฟล์ (domain/application/presentation/repo)
- `create-report` action → 5 ไฟล์
- `create-category` action → 5 ไฟล์
- `create-deployment` action → 3 ไฟล์
- `create-counting` action → 5 ไฟล์
- `create-plant-disease` action → 6 ไฟล์
- `create-plant-growth` action → 6 ไฟล์
- `sql-v2` action → V004-V010 migrations
- `all-v2` action → รวมทุกอย่าง

 