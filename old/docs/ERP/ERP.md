# ระบบ ERP กลุ่มบริษัทอาหาร — เอกสารออกแบบสถาปัตยกรรม

> แบ่งเป็น Part ตามคำขอ — เอกสารนี้ครอบคลุม **Part 1 (ภาพรวม)** และ **Part 2 (แผนการ)** โดย Part 3+ จะลงรายละเอียดแต่ละ module แยกในตอนถัดไป

---

# 📘 PART 1 — ภาพรวมระบบ

## 1.1 บริบททางธุรกิจ (Business Context)

```text
                        ┌──────────────────────────────────────┐
                        │      กลุ่มบริษัทอาหาร (Owner)           │
                        │      Thailand · ~60-80 คนรวม         │
                        └──────────────────┬───────────────────┘
                                           │
        ┌──────────────────┬───────────────┼───────────────┬──────────────────┐
        │                  │               │               │                  │
        ▼                  ▼               ▼               ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐
│ โรงงานแปรรูป   │  │ บจก.จัดจำหน่าย │  │ ร้านพัทยา │  │ ร้าน กทม.1│  │ ร้าน กทม.2   │
│ เนื้อสัตว์ B2B │  │ ผักสด          │  │  (1 สาขา) │  │ (กำลังเปิด)│  │ (กำลังเปิด)  │
│  ~40 คน        │  │                │  │          │  │          │  │              │
└───────┬───────┘  └───────┬───────┘  └────┬─────┘  └────┬─────┘  └──────┬───────┘
        │                  │               │             │               │
        └──────────────────┴───────────────┴─────────────┴───────────────┘
                                           │
                                           ▼
                            ┌──────────────────────────┐
                            │  ERP กลาง (Multi-company) │
                            │  Python + PostgreSQL      │
                            │  บน Linux + AI coding     │
                            └──────────────────────────┘
```

**คุณลักษณะพิเศษของธุรกิจนี้:**

| มิติ | ลักษณะ | ผลต่อการออกแบบ |
|------|--------|----------------|
| โครงสร้าง | หลายนิติบุคคล + หลายสาขา | ต้อง multi-tenant ตั้งแต่ต้น |
| อุตสาหกรรม | อาหารสด / เนื้อสัตว์ | มี lot, expiry, cold-chain |
| ลูกค้า | B2B เป็นหลัก + B2C ผ่านร้าน | pricing หลายระดับ, credit term |
| ช่องทาง | LINE + manual + หน้าร้าน | order ingress หลายแบบ |
| ภาษี | VAT 7% + ใบกำกับภาษี | ต้องแม่นระดับสตางค์ |
| การเงิน | เงินจริงวิ่งผ่านระบบ | audit + reconciliation = mandatory |
| ทีม | Owner คนเดียว → ต้อง handoff | ระบบต้อง operable โดยคนอื่นได้ |

---

## 1.2 ระบบภายนอกที่ต้องเชื่อม (External Systems Landscape)

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL SYSTEMS                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐                │
│   │ LINE         │   │ Thai Cloud   │   │ Cloud Backup │                │
│   │ Messaging    │   │ Accounting   │   │ (S3 / GCS)   │                │
│   │ API          │   │ API          │   │              │                │
│   └──────┬───────┘   └──────┬───────┘   └──────┬───────┘                │
│          │                  │                  │                        │
│   ┌──────┴───────┐   ┌──────┴───────┐   ┌──────┴───────┐                │
│   │ IoT Sensors  │   │ Bank /       │   │ SMS / Email  │                │
│   │ (MQTT)       │   │ Payment GW   │   │ Provider     │                │
│   └──────┬───────┘   └──────┬───────┘   └──────┬───────┘                │
│          │                  │                  │                        │
└──────────┼──────────────────┼──────────────────┼────────────────────────┘
           │                  │                  │
           ▼                  ▼                  ▼
    ┌──────────────────────────────────────────────────┐
    │            FOOD ERP (ระบบนี้)                     │
    │  FastAPI + PostgreSQL + Redis + Worker           │
    └──────────────────────────────────────────────────┘
```

---

## 1.3 สถาปัตยกรรมภาพรวม (High-Level Architecture)

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                            PRESENTATION LAYER                                 │
│                                                                              │
│   ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌──────────┐  │
│   │ REST API  │  │ LINE      │  │ IoT       │  │ Admin     │  │ Webhook  │  │
│   │ (FastAPI) │  │ Webhook   │  │ Ingest    │  │ Console   │  │ Receiver │  │
│   └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └────┬─────┘  │
└─────────┼──────────────┼──────────────┼──────────────┼─────────────┼────────┘
          │              │              │              │             │
          └──────────────┴──────────────┴──────────────┴─────────────┘
                                     │
┌────────────────────────────────────┼────────────────────────────────────────┐
│                        APPLICATION LAYER                                     │
│                                                                              │
│   Use Cases · Orchestration · Transaction Boundary · Idempotency            │
│                                                                              │
│   ┌────────────────────────────────────────────────────────────────────┐    │
│   │  IssueInvoice  │  CancelInvoice  │  PostLedger  │  Reconcile      │    │
│   │  CreateOrder   │  AssignRoute    │  SyncCloud   │  VerifyBackup   │    │
│   └────────────────────────────────────────────────────────────────────┘    │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
┌────────────────────────────────────┼────────────────────────────────────────┐
│                           DOMAIN LAYER                                       │
│                                                                              │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│   │ Invoice  │  │ Ledger   │  │ Order    │  │ Money VO │  │ Pricing  │     │
│   │ Entity   │  │ Entry    │  │ Entity   │  │          │  │ Rules    │     │
│   └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
│                                                                              │
│   Domain Events: InvoiceIssued · PaymentReceived · StockLow · TempAlert    │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
┌────────────────────────────────────┼────────────────────────────────────────┐
│                       INFRASTRUCTURE LAYER                                   │
│                                                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │
│  │PostgreSQL│ │  Redis   │ │  MQTT    │ │  S3      │ │  LINE    │         │
│  │(multi-   │ │(cache +  │ │(IoT)     │ │(backup + │ │  SDK     │         │
│  │ schema)  │ │blacklist)│ │          │ │ CCTV)    │ │          │         │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘         │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 1.4 Money Path — เส้นทางของเงิน (Critical Flow)

นี่คือ **เส้นทางที่ห้ามพัง** ทุก use case ที่แตะเส้นนี้ต้องผ่าน 5 กติกา:

```text
   [1] Idempotency Key        [4] Audit Log
   [2] DB Transaction         [5] Read-Back Verify
   [3] Domain Invariant
                │
                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│   Order ──► Invoice ──► Ledger ──► Outbox ──► Cloud ──► Reconciliation      │
│     │         │           │          │          │           │               │
│     ▼         ▼           ▼          ▼          ▼           ▼               │
│  ┌─────┐  ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐            │
│  │Credit│  │ VAT │    │Double│    │Retry│    │API  │    │Diff │            │
│  │Check │  │ 7%  │    │Entry │    │Safe │    │Sync │    │Alert│            │
│  └─────┘  └─────┘    └─────┘    └─────┘    └─────┘    └─────┘            │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Failure Mode ที่ต้องป้องกัน:**

| Failure | ผลกระทบ | การป้องกัน |
|---------|---------|-----------|
| Invoice ออกซ้ำ | เก็บเงินเกิน | Idempotency key + unique constraint |
| VAT คำนวณผิด | ปัญหาภาษี | Money VO + VatCalculator + test |
| Ledger ชี้ invoice ที่ถูก cancel | บัญชีเพี้ยน | Domain invariant + reconciliation check |
| Cloud sync ล่ม | DB-cloud ไม่ตรง | Outbox pattern + retry |
| Backup เสีย | กู้คืนไม่ได้ | Restore-to-staging + read-back verify |
| Deploy พัง | ระบบล่ม | Staging + smoke test + rollback |

---

## 1.5 Tech Stack

```text
┌──────────────────────────────────────────────────────────────────┐
│  LAYER              TECHNOLOGY              WHY                   │
├──────────────────────────────────────────────────────────────────┤
│  Runtime            Python 3.13+            ตาม template          │
│  Web Framework      FastAPI                 async, type-safe     │
│  ASGI Server        Hypercorn/Uvicorn       production-ready     │
│  ORM                SQLAlchemy 2.x async    mature, async         │
│  Database           PostgreSQL 16           JSONB, schema-per-    │
│                                              tenant, transactional│
│  Migration          Alembic                 auto-run on startup  │
│  Cache/Blacklist    Redis                   token + rate limit   │
│  Auth               JWT (JWS+JWE) + API Key  ตาม template         │
│  Password           Argon2                  ตาม template         │
│  Logging            Loguru                  daily rotate         │
│  Money              Decimal (ห้าม float)     ความแม่นระดับสตางค์   │
│  Background         Outbox + Worker         retry-safe sync      │
│  IoT                MQTT (Mosquitto)        lightweight          │
│  Backup             pg_dump + S3            per-schema           │
│  Package Manager    uv                      ตาม template         │
│  Linter             Ruff                    ตาม template         │
│  Testing            pytest + httpx          ตาม template         │
└──────────────────────────────────────────────────────────────────┘
```

---

## 1.6 Module Map (ภาพรวมทุก Module)

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                            FOOD ERP MODULES                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──── CORE (cross-cutting) ─────────────────────────────────────────┐     │
│  │  money · tenant_context · audit · idempotency · security ·        │     │
│  │  settings · database · redis · logging · middleware               │     │
│  └───────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  ┌──── FOUNDATION ───────────────────────────────────────────────────┐     │
│  │  tenancy · authentication · user · customer · supplier · product  │     │
│  └───────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  ┌──── MONEY PATH (priority 1) ──────────────────────────────────────┐     │
│  │  order · pricing · invoice · ledger · payment ·                   │     │
│  │  accounting_gateway · reconciliation                              │     │
│  └───────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  ┌──── OPERATIONS ───────────────────────────────────────────────────┐     │
│  │  delivery · inventory · line_channel · employee                   │     │
│  └───────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  ┌──── MONITORING & SENSING ─────────────────────────────────────────┐     │
│  │  iot · cctv · monitoring · backup                                 │     │
│  └───────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  ┌──── TEMPLATES ────────────────────────────────────────────────────┐     │
│  │  health · example · blank                                         │     │
│  └───────────────────────────────────────────────────────────────────┘     │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 1.7 หลักการออกแบบ 8 ข้อ (Design Principles)

```text
[1] Money is Domain Invariant
    → ทุกอย่างที่แตะเงินต้องใช้ Money VO + Decimal + transaction

[2] Read-Back Verification
    → เขียนแล้วต้องอ่านกลับมาเทียบ ก่อน commit

[3] Idempotency Everywhere on Money Path
    → retry ได้โดยไม่สร้าง invoice ซ้ำ

[4] Append-Only Audit
    → audit_log INSERT เท่านั้น ห้าม UPDATE/DELETE

[5] Schema-Per-Tenant
    → แยกบริษัทในระดับ PostgreSQL schema

[6] Outbox for External Sync
    → เขียน DB ก่อน ค่อย sync cloud ผ่าน worker

[7] Reversible Ledger
    → ห้ามลบ entry ต้อง reversal

[8] Observable by Default
    → log ที่จุดสำคัญ + money-path probe
```

---

# 📗 PART 2 — แผนการดำเนินงาน

## 2.1 หลักคิดของแผน

โจทย์บอกชัดว่า **"ช่วงแรกไม่มีฟีเจอร์ใหม่"** → แผนต้องเป็น **Stabilize → Verify → Handoff** ไม่ใช่ **Build**

```text
   เดือน 1          เดือน 2          เดือน 3          เดือน 4-5
┌────────────┐   ┌────────────┐   ┌────────────┐   ┌────────────┐
│ STABILIZE  │──►│  HARDEN    │──►│  HANDOFF   │──►│  EXPAND    │
│            │   │            │   │            │   │            │
│ Audit      │   │ Test       │   │ Train #2   │   │ Rollout to │
│ Fix bugs   │   │ Backup     │   │ Deploy     │   │ affiliates │
│ Monitor    │   │ Verify     │   │ Restore    │   │ Onboard    │
└────────────┘   └────────────┘   └────────────┘   └────────────┘
     ▲                ▲                ▲                ▲
     │                │                │                │
   เงินนิ่ง         ทดสอบได้        คนที่ 2 ทำได้      ERP กลางใช้ได้
```

---

## 2.2 Priority Matrix (Impact × Effort)

```text
                HIGH IMPACT
                     ▲
                     │
   ┌─────────────────┼─────────────────┐
   │                 │                 │
   │  QUICK WIN      │  BIG BET        │
   │                 │                 │
   │  • Audit log    │  • Invoice      │
   │  • Money VO     │    module       │
   │  • Health probe │  • Ledger       │
   │  • Recon check  │  • Recon engine │
   │                 │  • Backup/      │
   │                 │    Restore      │
   │                 │                 │
LOW├─────────────────┼─────────────────┤HIGH
   │                 │                 │
   │  FILL-IN        │  MONEY PIT      │
   │                 │                 │
   │  • IoT          │  • CCTV AI      │
   │  • CCTV store   │  • Full ERP     │
   │  • LINE parse   │    rewrite      │
   │                 │                 │
   └─────────────────┼─────────────────┘
                     │
                LOW IMPACT
                     ▼
   EFFORT: LOW ◄─────────────────► HIGH
```

**กลยุทธ์:** ทำ Quick Win ก่อน → สร้าง Big Bet → เลี่ยง Money Pit

---

## 2.3 แผนรายเฟส (Phase Plan)

### 🔵 Phase 0 — Recon (สัปดาห์ที่ 0, ก่อนเริ่มงาน)

```text
┌─────────────────────────────────────────────────────────────────┐
│  OBJECTIVE: เข้าใจระบบเดิมก่อนแตะ                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  □ อ่าน codebase ทั้งหมด (owner walkthrough 1-2 ชม.)          │
│  □ วาด data flow diagram ของ money path                       │
│  □ ระบุจุดที่ไม่มี test / ไม่มี monitoring                     │
│  □ ระบุ single point of failure                                │
│  □ รัน reconciliation check ด้วยมือ (ad-hoc query)             │
│  □ ตรวจ backup ที่มีอยู่ — restore ได้จริงหรือไม่              │
│                                                                 │
│  DELIVERABLE: System Health Report + Risk Register             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### 🟢 Phase 1 — Stabilize (เดือนที่ 1)

**เป้าหมาย:** ทำให้เส้นทางเงินเชื่อถือได้ + มีเครื่องมือจับปัญหา

```text
┌─────────────────────────────────────────────────────────────────┐
│  WEEK 1-2: AUDIT & OBSERVE                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Day 1-2:  ├─ ตั้ง dev environment                             │
│            ├─ รันระบบเดิมใน staging                             │
│            └─ ติด monitoring พื้นฐาน (log + DB metrics)         │
│                                                                 │
│  Day 3-5:  ├─ สร้าง core/money.py (Decimal + VAT)              │
│            ├─ สร้าง core/audit.py (append-only)                │
│            └─ สร้าง core/idempotency.py                        │
│                                                                 │
│  Day 6-8:  ├─ สร้าง modules/reconciliation/                    │
│            ├─ เขียน check 5 ตัว:                                │
│            │   1. CheckInvoiceVat                               │
│            │   2. CheckOrphanLedgerEntries                     │
│            │   3. CheckOvercharge                               │
│            │   4. CheckUnbalancedJournals                      │
│            │   5. CheckDuplicateInvoiceNo                      │
│            └─ รันกับ production data (read-only)                │
│                                                                 │
│  Day 9-10: ├─ จัดลำดับ bug ที่เจอตามความรุนแรง                 │
│            ├─ แก้ bug อันดับ 1-3                                │
│            └─ เขียน regression test ทุกตัว                       │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  WEEK 3-4: BACKUP & PROBE                                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Day 11-13: ├─ สร้าง modules/backup/                            │
│             ├─ BackupNow (pg_dump per schema)                   │
│             ├─ RestoreToStaging                                 │
│             └─ VerifyBackup (read-back compare)                 │
│                                                                 │
│  Day 14-16: ├─ สร้าง modules/monitoring/                        │
│             ├─ HealthCheck (DB, Redis, LINE, Cloud)             │
│             └─ MoneyPathProbe (E2E: issue → ledger → cloud)     │
│                                                                 │
│  Day 17-18: ├─ แก้ bug อันดับ 4-7                                │
│             └─ เพิ่ม regression test                             │
│                                                                 │
│  Day 19-20: ├─ เขียน runbook (backup, restore, incident)        │
│             ├─ Deploy ขึ้น production                            │
│             └─ พิสูจน์ด้วย read-back จาก production              │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  DELIVERABLE:                                                    │
│   • ระบบมี audit log ครบ                                        │
│   • Money VO ใช้ทั่วระบบ                                        │
│   • Reconciliation ทำงานได้                                     │
│   • Backup/Restore พิสูจน์แล้ว                                  │
│   • Monitoring + Money Path Probe ทำงาน                         │
│   • Bug 7 ตัวแรกถูกแก้ + มี test                                │
│                                                                 │
│  SUCCESS METRIC:                                                 │
│   • Reconciliation ไม่เจอ discrepancy ใหม่ 7 วันติด             │
│   • Restore สำเร็จ 100% และ read-back ตรง                       │
│   • MoneyPathProbe ผ่านทุก 5 นาที                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### 🟡 Phase 2 — Harden (เดือนที่ 2)

**เป้าหมาย:** เพิ่มความทนทาน + ทดสอบ + เตรียม handoff

```text
┌─────────────────────────────────────────────────────────────────┐
│  WEEK 5-6: TEST COVERAGE                                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  □ Integration test ครอบ money path ทั้งเส้น                    │
│  □ Property-based test สำหรับ Money/VAT                        │
│  □ Chaos test: kill worker กลาง sync → ดู outbox retry         │
│  □ Idempotency test: ยิง invoice ซ้ำ 100 ครั้ง → ได้ 1           │
│  □ Concurrency test: ออก invoice พร้อมกัน → เลขไม่ซ้ำ          │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  WEEK 7-8: OUTBOX & SYNC HARDENING                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  □ สร้าง modules/accounting_gateway/                            │
│  □ Outbox pattern สำหรับ sync cloud                             │
│  □ Retry + exponential backoff                                  │
│  □ Dead letter queue สำหรับ failed sync                         │
│  □ Reconciliation ระหว่าง DB ↔ Cloud                            │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  DELIVERABLE:                                                    │
│   • Test coverage ≥ 80% ใน money path                           │
│   • Outbox + retry ทำงานได้                                     │
│   • Cloud sync พิสูจน์แล้วว่าไม่ double-charge                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### 🟠 Phase 3 — Handoff (เดือนที่ 3)

**เป้าหมาย:** มีคนที่สองที่ deploy + restore ได้

```text
┌─────────────────────────────────────────────────────────────────┐
│  WEEK 9-10: DOCUMENTATION                                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  □ เขียน architecture doc (เอกสารนี้)                           │
│  □ เขียน runbook: deploy, rollback, restore, incident           │
│  □ เขียน onboarding guide สำหรับ engineer คนต่อไป              │
│  □ อัด video walkthrough ของ money path                         │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  WEEK 11-12: TRAINING & SHADOW                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  □ สอนคนที่ 2: deploy ขึ้น staging                             │
│  □ สอนคนที่ 2: restore จาก backup                               │
│  □ สอนคนที่ 2: รัน reconciliation + อ่านผล                     │
│  □ สอนคนที่ 2: แก้ bug ง่าย ๆ ด้วย AI tools                    │
│  □ Owner + คนที่ 2 อยู่ระหว่าง deploy พร้อมกัน (pair)          │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  DELIVERABLE:                                                    │
│   • คนที่ 2 deploy ได้โดยไม่มี owner                            │
│   • คนที่ 2 restore ได้โดยไม่มี owner                           │
│   • ระบบไม่ผูกกับคนคนเดียว                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### 🔴 Phase 4 — Expand (เดือนที่ 4-5)

**เป้าหมาย:** นำ ERP กลางไปใช้กับบริษัทในเครือ

```text
┌─────────────────────────────────────────────────────────────────┐
│  WEEK 13-16: AFFILIATE ROLLOUT                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  □ สร้าง modules/tenancy/ (multi-company)                       │
│  □ Provision schema สำหรับบริษัทใหม่                            │
│  □ Seed chart of accounts มาตรฐาน                               │
│  □ Config per company (VAT, numbering, terms)                   │
│  □ Onboard ลูกค้า B2B รายใหญ่                                    │
│  □ สอนพนักงานบริษัทในเครือ                                      │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  DELIVERABLE:                                                    │
│   • ERP กลางตั้งค่าให้บริษัทในเครือได้                           │
│   • พนักงานบริษัทในเครือใช้งานได้                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2.4 Timeline แบบ Gantt (ย่อ)

```text
         │ M1        │ M2        │ M3        │ M4        │ M5        │
─────────┼───────────┼───────────┼───────────┼───────────┼───────────┤
Phase 0  │██         │           │           │           │           │
Recon    │           │           │           │           │           │
─────────┼───────────┼───────────┼───────────┼───────────┼───────────┤
Phase 1  │ ██████████│           │           │           │           │
Stabilize│           │           │           │           │           │
─────────┼───────────┼───────────┼───────────┼───────────┼───────────┤
Phase 2  │           │ ██████████│           │           │           │
Harden   │           │           │           │           │           │
─────────┼───────────┼───────────┼───────────┼───────────┼───────────┤
Phase 3  │           │           │ ██████████│           │           │
Handoff  │           │           │           │           │           │
─────────┼───────────┼───────────┼───────────┼───────────┼───────────┤
Phase 4  │           │           │           │ ██████████████████████│
Expand   │           │           │           │           │           │
─────────┴───────────┴───────────┴───────────┴───────────┴───────────┘
```

---

## 2.5 Risk Register

| # | ความเสี่ยง | โอกาส | ผลกระทบ | Mitigation |
|---|-----------|-------|---------|-----------|
| 1 | แก้ bug แล้วทำเงินเพี้ยน | กลาง | สูงมาก | Staging + read-back + rollback plan |
| 2 | Backup restore ไม่ได้ | กลาง | สูงมาก | Test restore ทุกสัปดาห์ |
| 3 | Cloud API เปลี่ยน | ต่ำ | สูง | Abstraction layer (port) |
| 4 | Owner ติดงานอื่น | สูง | กลาง | Document ทุกอย่าง, pair |
| 5 | AI tool ให้ข้อมูลผิด | สูง | กลาง | Code review + test + read-back |
| 6 | Invoice เลขซ้ำ | ต่ำ | สูง | SELECT FOR UPDATE + unique |
| 7 | VAT คำนวณผิด | กลาง | สูง | Property-based test |
| 8 | คนที่ 2 ลาออก | ต่ำ | กลาง | 3 คน deploy ได้ |
| 9 | ข้อมูลลูกค้ารั่ว | ต่ำ | สูงมาก | Encryption at rest + audit |
| 10 | Schema migration พัง | กลาง | สูง | Auto-migration + backup ก่อน |

---

## 2.6 Definition of Done (ต่อ Phase)

```text
┌──────────────────────────────────────────────────────────────┐
│  PHASE 1 — STABILIZE                                         │
│  □ Reconciliation ผ่าน 7 วันติด                              │
│  □ Restore พิสูจน์ด้วย read-back                            │
│  □ Bug 7 ตัวแรกมี regression test                            │
│  □ MoneyPathProbe ทำงานทุก 5 นาที                            │
├──────────────────────────────────────────────────────────────┤
│  PHASE 2 — HARDEN                                            │
│  □ Test coverage ≥ 80% ใน money path                        │
│  □ Chaos test ผ่าน (kill worker → retry สำเร็จ)              │
│  □ Idempotency test ผ่าน (ยิงซ้ำ 100 → ได้ 1)               │
│  □ Cloud sync ไม่ double-charge                              │
├──────────────────────────────────────────────────────────────┤
│  PHASE 3 — HANDOFF                                           │
│  □ คนที่ 2 deploy ได้โดยไม่มี owner                          │
│  □ คนที่ 2 restore ได้โดยไม่มี owner                         │
│  □ Runbook ครบ (deploy, rollback, restore, incident)         │
│  □ Onboarding guide พร้อม                                   │
├──────────────────────────────────────────────────────────────┤
│  PHASE 4 — EXPAND                                            │
│  □ บริษัทในเครือใช้งาน ERP กลางได้                            │
│  □ พนักงานบริษัทในเครือได้รับการสอน                          │
│  □ Multi-tenant isolation พิสูจน์แล้ว                        │
└──────────────────────────────────────────────────────────────┘
```

---

## 2.7 Deliverables Summary

| Phase | Deliverable | ผู้รับ |
|-------|-------------|--------|
| 0 | System Health Report + Risk Register | Owner |
| 1 | Audit log + Money VO + Recon + Backup + Monitoring | Owner |
| 2 | Test suite + Outbox + Sync hardening | Owner |
| 3 | Runbook + Onboarding + คนที่ 2 | Owner + ทีม |
| 4 | Multi-tenant ERP + Affiliate onboarding | บริษัทในเครือ |

---

## 2.8 KPIs (ตัวชี้วัดความสำเร็จ)

```text
┌──────────────────────────────────────────────────────────────┐
│  MONEY RELIABILITY                                            │
│   • Reconciliation discrepancy = 0                          │
│   • Invoice duplicate rate = 0                              │
│   • VAT error rate = 0                                       │
│   • Cloud sync success rate ≥ 99.9%                         │
├──────────────────────────────────────────────────────────────┤
│  OPERATIONAL                                                  │
│   • Backup restore success = 100%                           │
│   • MoneyPathProbe pass rate ≥ 99%                          │
│   • MTTR (incident) < 30 นาที                               │
│   • Deploy โดยคนที่ 2 สำเร็จ = 100%                         │
├──────────────────────────────────────────────────────────────┤
│  TEAM                                                        │
│   • จำนวนคนที่ deploy ได้ ≥ 2                                │
│   • จำนวนคนที่ restore ได้ ≥ 2                               │
│   • Bus factor ≥ 2                                          │
└──────────────────────────────────────────────────────────────┘
```

---

# 📌 สรุปท้ายเอกสาร

## Part 1 (ภาพรวม) ครอบคลุม:
- บริบททางธุรกิจ + โครงสร้างกลุ่มบริษัท
- ระบบภายนอกที่ต้องเชื่อม
- สถาปัตยกรรม 4 layer
- Money Path + failure modes
- Tech stack
- Module map
- 8 design principles

## Part 2 (แผนการ) ครอบคลุม:
- 5 เฟส: Recon → Stabilize → Harden → Handoff → Expand
- Timeline 5 เดือน
- Priority matrix
- Risk register
- Definition of Done ต่อ phase
- KPIs

---

## 🔜 Part 3+ (ตอนถัดไป) — ราย Module แบบละเอียด

จะลงรายละเอียดแต่ละ module ตาม template นี้:

```text
┌─────────────────────────────────────────────────────────┐
│  MODULE: <name>                                          │
├─────────────────────────────────────────────────────────┤
│  1. Purpose & Scope                                      │
│  2. Domain Model (entities, VOs, invariants)             │
│  3. Domain Events                                        │
│  4. Use Cases                                            │
│  5. Application Interfaces (ports)                       │
│  6. Infrastructure (models, repositories)                │
│  7. Presentation (API endpoints, schemas)                │
│  8. Database Schema (DDL)                                │
│  9. Folder Structure                                     │
│  10. Tests                                               │
│  11. Dependencies (module → module)                      │
└─────────────────────────────────────────────────────────┘
```

**ลำดับ Part 3+ ที่แนะนำ:**

| Part | Module | ความสำคัญ |
|------|--------|-----------|
| **Part 3** | Core Infrastructure (money, audit, idempotency, tenant_context) | 🔴 |
| **Part 4** | Tenancy (multi-company) | 🔴 |
| **Part 5** | Invoice | 🔴 |
| **Part 6** | Ledger | 🔴 |
| **Part 7** | Accounting Gateway | 🔴 |
| **Part 8** | Reconciliation | 🔴 |
| **Part 9** | Order + Pricing | 🟠 |
| **Part 10** | Delivery + Inventory | 🟠 |
| **Part 11** | LINE Channel | 🟠 |
| **Part 12** | IoT + CCTV | 🟡 |
| **Part 13** | Monitoring + Backup | 🔴 |
| **Part 14** | Auth + User (reuse template) | 🟢 |

---

 