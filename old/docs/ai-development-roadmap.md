# แผนพัฒนาทักษะ AI ในโปรเจคนี้ (AI Career Development Roadmap)

เอกสารนี้แปลงเส้นทางอาชีพ AI 3 สาย ให้เป็น **งานพัฒนาจริงในโปรเจค FastAPI Clean Architecture + DDD** เพื่อให้เรียนรู้ผ่านการลงมือทำ (Learning by Doing) บน codebase เดียวกัน

---

## ทำไมโปรเจคนี้เหมาะเป็นฐานฝึก AI

| สิ่งที่โปรเจคมีอยู่แล้ว | ประโยชน์ต่อสาย AI |
|---|---|
| โครงสร้าง DDD 4 ชั้น (domain / application / infrastructure / presentation) | ฝึกออกแบบระบบ AI แบบแยก business logic ออกจาก AI provider |
| Modules ธุรกิจจริง: `customer`, `quotation`, `purchaseorder`, `payment`, `document`, `report`, `wos` | มีข้อมูลและ use case ธุรกิจจริงให้ AI ช่วยทำงาน |
| PostgreSQL + Alembic migration | ต่อยอดเป็น Vector Database ด้วย pgvector ได้ทันที |
| Docker / docker-compose / Makefile | ฐานของ MLOps — deploy model server เป็น container ได้เลย |
| MQTT (Mosquitto) + InfluxDB + Redis | ข้อมูล IoT time-series สำหรับฝึก anomaly detection |
| JWT Authentication + RBAC | ควบคุมการเข้าถึง endpoint ของ AI อย่างปลอดภัย |
| pytest + ruff | วัฒนธรรม quality gate ที่ MLOps ต้องใช้ |

---

## เส้นทางที่ 1: AI / ML Engineer (สายวิจัยและพัฒนาโมเดล)

### ทักษะเดิมที่ใช้ต่อได้

- OOP → ออกแบบ class สำหรับ dataset, model wrapper
- Python → ภาษาหลักของ ML ecosystem
- Git → version control ของ experiment และโค้ด
- Data Structures → จัดการ batch, tensor, embedding

### ทักษะที่ต้องเรียนเพิ่ม

| หมวด | รายการ |
|---|---|
| Frameworks | PyTorch (เริ่มตัวนี้), Scikit-Learn, TensorFlow (รู้จักพอ) |
| Math | Linear Algebra, Calculus, Statistics & Probability |
| Core Concepts | Deep Learning, NLP (สำคัญมากสำหรับข้อมูลภาษาไทย), Computer Vision |

### งานพัฒนาในโปรเจคนี้

สร้างโฟลเดอร์ `ml/` แยกจาก `app/` (โมเดลไม่ควรปนกับ API runtime):

```text
ml/
├── notebooks/          # ทดลอง EDA, training
├── data/
│   ├── raw/            # ข้อมูลดิบจาก modules เช่น document, quotation
│   └── processed/
├── src/
│   ├── datasets.py     # Dataset/DataLoader classes
│   ├── models.py       # นิยามโมเดล
│   ├── train.py        # training loop
│   └── evaluate.py     # metrics
└── experiments/        # config + ผล run แต่ละครั้ง
```

**โปรเจคฝึกมือ (เรียงตามลำดับความยาก):**

1. **Document Classification** — ใช้ Scikit-Learn จำแนกประเภทเอกสารจาก module `document` (quotation / invoice / PO) ด้วย TF-IDF + Logistic Regression เป็น baseline
2. **Thai NLP: Information Extraction** — ดึงข้อมูลจากใบเสนอราคา (ชื่อลูกค้า, จำนวนเงิน, วันที่) ด้วย fine-tune โมเดลภาษาไทย เช่น WangchanBERTa หรือ typhoon
3. **IoT Anomaly Detection** — ใช้ข้อมูลจาก InfluxDB/MQTT ฝึก autoencoder ตรวจค่าผิดปกติของเซนเซอร์
4. **Fine-tuning LLM** — fine-tune small LLM (เช่น Qwen/Llama ขนาดเล็กด้วย LoRA) ให้ตอบคำถามเฉพาะ domain ของบริษัท

### Checklist ความก้าวหน้า

- [ ] เขียน training pipeline ด้วย PyTorch ได้ครบ train/val/test
- [ ] อธิบาย backpropagation และ loss function ได้ด้วย math
- [ ] Fine-tune pretrained model 1 ตัวบนข้อมูลภาษาไทยของโปรเจค
- [ ] Export โมเดลเป็น artifact ที่ MLOps นำไป serve ได้ (ONNX หรือ .safetensors)
- [ ] จด experiment ทุกครั้ง (config, seed, metric) — ต่อยอดด้วย MLflow ในสาย 2

---

## เส้นทางที่ 2: MLOps Engineer (สายระบบและโครงสร้างพื้นฐาน)

### ทักษะเดิมที่ใช้ต่อได้

- CI/CD, Docker, Linux, Cloud → หัวใจของสายนี้อยู่แล้ว
- ประสบการณ์ DevOps ย้ายมา MLOps ได้ ~70%

### ทักษะที่ต้องเรียนเพิ่ม

| หมวด | รายการ |
|---|---|
| ML Pipeline Tools | MLflow (tracking + registry), Airflow หรือ Prefect (orchestration), Kubeflow (ระดับ K8s) |
| Model Deployment | Serving API (FastAPI), batch vs real-time inference, model versioning |
| Monitoring | Data drift, model drift, latency, token/cost monitoring |
| Vector DB | pgvector (ใช้ PostgreSQL เดิม), Pinecone, Milvus, Qdrant |

### งานพัฒนาในโปรเจคนี้

**โปรเจคฝึกมือ:**

1. **Model Serving Service** — เพิ่ม service `model-server` ใน `docker-compose.yaml` เป็น FastAPI แยกที่ load โมเดลจากสาย 1 แล้ว expose `/predict` (GPU/CPU resource limit ใน compose)
2. **MLflow Tracking** — รัน MLflow เป็น container อีกตัว ผูกกับ `ml/experiments` ให้ทุก training run ถูก log อัตโนมัติ และมี Model Registry สำหรับ promote model → staging → production
3. **CI/CD สำหรับ ML** — ต่อยอด GitHub Actions: lint/test (`ruff`, `pytest`) → build image → deploy; เพิ่ม stage ตรวจ metric ของโมเดลก่อน allow deploy (model quality gate)
4. **Monitoring** — เก็บ prediction log ลง PostgreSQL/InfluxDB แล้วทำ dashboard ดู latency, error rate, input distribution drift
5. **Vector DB Infrastructure** — เปิดใช้ extension `pgvector` ใน PostgreSQL เดิม สร้าง migration ตาราง embeddings ด้วย Alembic (แนวคิดเดียวกับ Pinecone แต่ไม่ต้องเพิ่ม service)

### Checklist ความก้าวหน้า

- [ ] Deploy model server เป็น container ที่ scale/restart ได้
- [ ] มี MLflow tracking ครบทุก experiment + registry มี staged model อย่างน้อย 1 ตัว
- [ ] Pipeline retrain ทำงานอัตโนมัติตาม schedule (Airflow/Prefect/cron)
- [ ] Dashboard monitoring แสง latency + drift ได้จริง
- [ ] Rollback โมเดลเป็นเวอร์ชันก่อนหน้าได้ภายใน 5 นาที

---

## เส้นทางที่ 3: AI Application Developer (สายประยุกต์ใช้ API) ⭐ เร็วที่สุด

### ทักษะเดิมที่ใช้ต่อได้

- Web Development, REST APIs, JSON → โปรเจคนี้คือ FastAPI อยู่แล้ว ย้ายสายได้เร็วที่สุด
- ความเข้าใจ DDD ช่วยให้ integrate AI อย่างถูกสถาปัตยกรรม

### ทักษะที่ต้องเรียนเพิ่ม

| หมวด | รายการ |
|---|---|
| LLM Orchestration | LangChain / LlamaIndex, function calling / tool use |
| Advanced Prompting | system prompt design, few-shot, structured output (JSON mode) |
| Semantic Search | Embedding, RAG (Retrieval-Augmented Generation), reranking |

### งานพัฒนาในโปรเจคนี้

สร้าง module ใหม่ตามโครงสร้าง DDD เดิม:

```text
app/modules/aichat/
├── domain/
│   ├── entities/chat_session.py      # entity บทสนทนา
│   └── value_objects/message.py
├── application/
│   ├── use_cases/ask_question.py     # use case เรียก LLM ผ่าน port
│   └── ports/llm_provider.py         # interface (port) ของ LLM
├── infrastructure/
│   ├── llm/openai_provider.py        # adapter จริง
│   ├── llm/ollama_provider.py        # adapter local (สลับได้)
│   └── repositories/pgvector_repository.py
└── presentation/
    ├── routes/chat_router.py
    └── schemas/chat_schemas.py       # request/response Pydantic
```

> จุดสำคัญ: Domain/Application ต้อง **ไม่รู้จัก OpenAI โดยตรง** — ผูกผ่าน port แล้ว inject ด้วย DI เหมือน repository อื่น ๆ ในโปรเจค ทำให้สลับ provider (OpenAI ↔ Claude ↔ Ollama local) ได้โดยไม่แตะ business logic

**โปรเจคฝึกมือ (เรียงตามลำดับ):**

1. **Chat Endpoint พื้นฐาน** — `POST /api/v1/aichat/ask` เรียก LLM API พร้อม streaming response (SSE) และบันทึก session ลง DB
2. **RAG ค้นเอกสารบริษัท** — ingest ไฟล์จาก module `document` → chunk → embed (เก็บใน pgvector) → retrieve → ส่งเป็น context ให้ LLM ตอบพร้อมอ้างอิง source
3. **ผู้ช่วยธุรกิจใน modules เดิม** — สรุป quotation เป็นภาษาคน, ร่าง email ตอบลูกค้าจาก module `email`, สรุป work order จาก `wos`
4. **Tool Calling / Agent** — ให้ LLM เรียก use case ที่มีอยู่แล้ว เช่น "สร้างใบเสนอราคาให้ลูกค้า X" → LLM เรียก `CreateQuotationUseCase` ผ่าน tool schema
5. **Guardrails** — จำกัดสิทธิ์ตาม JWT role, กรอง prompt injection, จำกัด token/cost ต่อ user

### Checklist ความก้าวหน้า

- [ ] มี chat endpoint ที่ streaming ได้ + auth ครบ
- [ ] RAG ตอบคำถามจากเอกสารจริงพร้อม cite แหล่งอ้างอิง
- [ ] สลับ LLM provider ได้โดยแก้แค่ DI binding
- [ ] Structured output ได้ JSON ตาม schema ที่กำหนด
- [ ] เขียน test mock LLM port ได้ (ไม่เรียก API จริงตอน test)

---

## Roadmap 12 สัปดาห์ (แนะนำเริ่มจากสาย 3)

| สัปดาห์ | เป้าหมาย | สาย |
|---|---|---|
| 1–2 | Chat endpoint + streaming + auth (module `aichat`) | 3 |
| 3–4 | pgvector + RAG บน module `document` | 3 + 2 |
| 5–6 | Baseline ML (Scikit-Learn) จำแนกเอกสาร + MLflow tracking | 1 + 2 |
| 7–8 | Model server container + CI/CD quality gate | 2 |
| 9–10 | Fine-tune Thai NLP (extract ข้อมูล quotation) + deploy ผ่าน registry | 1 + 2 |
| 11 | Tool calling agent เชื่อม use case ธุรกิจ + guardrails | 3 |
| 12 | Monitoring dashboard + drift detection + สรุป portfolio | 2 |

---

## กฎการ Integrate AI เข้ากับสถาปัตยกรรมเดิม

1. **AI Provider = Infrastructure Adapter** — ห้าม import SDK ของ OpenAI/LangChain ในชั้น domain/application ให้นิยาม port แล้ว implement ใน infrastructure
2. **โมเดลที่เทรนเอง = External Service** — serve แยกเป็น container (`model-server`) แล้วเรียกผ่าน HTTP เหมือน external API อื่น
3. **Config ผ่าน pydantic-settings** — API key, model name, endpoint ทั้งหมดอยู่ใน `.env` (ดูแนวทางจาก `.env.example`)
4. **Test ทุก use case** — mock port ของ LLM เสมอ ห้าม test แล้วยิง API จริง
5. **Cost & Latency เป็น non-functional requirement** — log token usage ทุก request เพื่อควบคุมค่าใช้จ่าย

---

## แหล่งเรียนรู้แนะนำ

- **FastAPI + AI:** เอกสาร SSE/streaming ของ FastAPI, โครงสร้าง module ใน README-TH.md ของโปรเจคนี้
- **RAG/LLM:** เอกสาร LangChain, LlamaIndex, OpenAI Cookbook
- **MLOps:** เอกสาร MLflow, Made With ML (madewithml.com)
- **ML Fundamentals:** fast.ai, Andrew Ng (Coursera), 3Blue1Brown (Linear Algebra / Neural Networks)
- **Thai NLP:** WangchanBERTa (VISTEC), Typhoon (SCB 10X), PyThaiNLP
