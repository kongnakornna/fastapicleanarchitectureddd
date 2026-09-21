# ระบบ ERP กลุ่มบริษัทอาหาร — เอกสารออกแบบสถาปัตยกรรม (ฉบับปรับปรุง)

> **Revision 2** — ปรับปรุง Part 1-2 ตามคำขอ: เพิ่ม module ครบทุกมิติของธุรกิจอาหาร (ขนส่ง, QR, โกดัง, การผลิต, traceability, รายงาน, ร้านค้า, config, forecasting, HR, KPI, satisfaction) และปรับ phase plan ให้สอดคล้อง

---

# 📘 PART 1 — ภาพรวมระบบ (ฉบับขยาย)

## 1.1 บริบททางธุรกิจ (Business Context) — ฉบับเต็ม

```text
                        ┌──────────────────────────────────────────┐
                        │     กลุ่มบริษัทอาหาร (Owner)              │
                        │     Thailand · ~60-100 คน                 │
                        │     5 นิติบุคคล · 3+ สาขา                 │
                        └────────────────────┬─────────────────────┘
                                             │
   ┌──────────────┬──────────────┬───────────┼───────────┬──────────────┐
   │              │              │           │           │              │
   ▼              ▼              ▼           ▼           ▼              ▼
┌────────┐  ┌────────┐  ┌──────────┐  ┌────────┐  ┌────────┐  ┌──────────┐
│โรงงาน  │  │บจก.    │  │ร้านพัทยา │  │ร้าน กทม│  │ร้าน กทม│  │บริษัทใน  │
│แปรรูป  │  │จัดจำหน่าย│  │(1 สาขา)  │  │1 (เปิด)│  │2 (เปิด)│  │เครือ (ใหม่)│
│เนื้อ B2B│  │ผักสด   │  │          │  │        │  │        │  │          │
│~40 คน  │  │        │  │          │  │        │  │        │  │          │
└───┬────┘  └───┬────┘  └────┬─────┘  └───┬────┘  └───┬────┘  └────┬─────┘
    │           │            │            │           │            │
    └───────────┴────────────┴────────────┴───────────┴────────────┘
                                     │
                                     ▼
                    ┌─────────────────────────────────┐
                    │   ERP กลาง (Multi-company)       │
                    │   ครอบคลุมทุกมิติ:               │
                    │   • เงิน (invoice/ledger)       │
                    │   • สินค้า (inventory/WMS)      │
                    │   • การผลิต (production)        │
                    │   • ขนส่ง (transport)           │
                    │   • ร้านค้า (retail POS)        │
                    │   • Traceability (QR/RFID/GPS)  │
                    │   • วิเคราะห์ (BI/forecast)     │
                    │   • คน (HR/KPI)                 │
                    └─────────────────────────────────┘
```

**มิติธุรกิจที่ต้องรองรับ (Business Dimensions):**

| มิติ | รายละเอียด | Module ที่เกี่ยวข้อง |
|------|-----------|---------------------|
| **การเงิน** | Invoice, Ledger, VAT, Payment, Cloud sync | invoice, ledger, payment, accounting_gateway |
| **สินค้า** | Lot, Expiry, Cold-chain, Barcode | product, inventory, warehouse |
| **การผลิต** | Recipe, Batch, Yield, Waste | production, config |
| **ขนส่ง** | Route, Cold-truck, GPS, POD | transport, delivery |
| **ร้านค้า** | POS, Shift, Cash drawer | retail, pricing |
| **Traceability** | Farm → Factory → Store → Customer | traceability (QR/RFID/GPS) |
| **วิเคราะห์** | Daily → 5Y, Forecast | reporting, analytics, forecast |
| **คน** | Employee, Shift, Payroll | employee, hr |
| **ลูกค้า** | B2B/B2C, Credit, Loyalty | customer, satisfaction |
| **KPI** | Company/Branch/Team/Individual | kpi |
| **Config** | VAT, Waste%, Pricing rules | config |
| **Audit** | ทุก action ที่แตะเงิน/สต็อก | audit, reconciliation |

---

## 1.2 ระบบภายนอกที่ต้องเชื่อม (ฉบับขยาย)

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL SYSTEMS                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─── MONEY ──────────────────────────────────────────────────────────┐     │
│  │  Thai Cloud Accounting API  ·  Bank / Payment Gateway              │     │
│  │  Credit Bureau  ·  e-Tax Invoice (Revenue Dept)                    │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  ┌─── CUSTOMER ───────────────────────────────────────────────────────┐     │
│  │  LINE Messaging API  ·  Facebook Messenger  ·  SMS / Email         │     │
│  │  Loyalty Platform  ·  Survey Platform (NPS/CSAT)                   │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  ┌─── OPERATIONS ─────────────────────────────────────────────────────┐     │
│  │  GPS Provider  ·  MQTT (IoT: temp/humidity)  ·  RFID Reader        │     │
│  │  Weighbridge  ·  Barcode Scanner  ·  Printer (label/receipt)       │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  ┌─── INFRASTRUCTURE ─────────────────────────────────────────────────┐     │
│  │  Cloud Backup (S3/GCS)  ·  Monitoring (Grafana/OTel)               │     │
│  │  Container Registry  ·  CI/CD Runner                               │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 1.3 สถาปัตยกรรมภาพรวม (High-Level Architecture)

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│                              PRESENTATION LAYER                                 │
│                                                                                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐│
│  │ REST API │ │ LINE Bot │ │ POS UI   │ │ IoT      │ │ Webhook  │ │ Admin  ││
│  │ (FastAPI)│ │          │ │ (React)  │ │ Ingest   │ │ Receiver │ │Console ││
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └───┬────┘│
└───────┼────────────┼────────────┼────────────┼────────────┼───────────┼─────┘
        │            │            │            │            │           │
        └────────────┴────────────┴────────────┴────────────┴───────────┘
                                     │
┌────────────────────────────────────┼──────────────────────────────────────────┐
│                        APPLICATION LAYER                                       │
│                                                                                │
│  Use Cases · Orchestration · Transaction · Idempotency · Outbox · Saga        │
│                                                                                │
│  ┌──────────────────────────────────────────────────────────────────────┐    │
│  │ Money      │ Stock      │ Production │ Transport │ Retail  │ HR/KPI   │    │
│  │ IssueInvoice│ PostStock │ PlanBatch  │ AssignRoute│ CloseShift│ EvalKPI│    │
│  └──────────────────────────────────────────────────────────────────────┘    │
└────────────────────────────────────┬──────────────────────────────────────────┘
                                     │
┌────────────────────────────────────┼──────────────────────────────────────────┐
│                           DOMAIN LAYER                                         │
│                                                                                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐│
│  │ Invoice  │ │ Stock    │ │ Recipe   │ │ Shipment │ │ Sale     │ │ KPI    ││
│  │ Ledger   │ │ Lot      │ │ Batch    │ │ Route    │ │ Shift    │ │ Target ││
│  │ Money VO │ │ Movement │ │ Yield    │ │ POD      │ │ Drawer   │ │ Actual ││
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ └────────┘│
│                                                                                │
│  Domain Events: InvoiceIssued · StockLow · TempAlert · BatchCompleted         │
│                 ShipmentArrived · ShiftClosed · KPIUpdated                     │
└────────────────────────────────────┬──────────────────────────────────────────┘
                                     │
┌────────────────────────────────────┼──────────────────────────────────────────┐
│                       INFRASTRUCTURE LAYER                                     │
│                                                                                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐│
│  │PostgreSQL│ │  Redis   │ │  MQTT    │ │  S3      │ │  Kafka   │ │ELK/    ││
│  │(schema/  │ │(cache +  │ │(IoT +    │ │(backup + │ │(events + │ │OpenSea ││
│  │ tenant)  │ │blacklist)│ │GPS)      │ │CCTV)     │ │streaming)│ │rch     ││
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ └────────┘│
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## 1.4 Money Path + Goods Path + Data Path

ระบบนี้ไม่ใช่แค่ Money Path — มี **3 เส้นทางหลัก** ที่ต้องทำให้เชื่อถือได้:

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│  [1] MONEY PATH — เงิน                                                       │
│                                                                              │
│  Order ──► Invoice ──► Ledger ──► Outbox ──► Cloud ──► Reconciliation      │
│                                                                              │
│  กติกา: Idempotency · DB Transaction · Domain Invariant · Audit · Read-Back │
├──────────────────────────────────────────────────────────────────────────────┤
│  [2] GOODS PATH — สินค้า                                                     │
│                                                                              │
│  PO ──► Receive ──► Lot ──► Store ──► Issue ──► Produce ──► Ship ──► Sell  │
│                                                                              │
│  กติกา: FEFO/FIFO · Lot traceability · Cold-chain · Cycle count             │
├──────────────────────────────────────────────────────────────────────────────┤
│  [3] DATA PATH — ข้อมูล                                                      │
│                                                                              │
│  Sensor/RFID/GPS/POS ──► Kafka ──► Stream Processor ──► OLAP ──► BI/KPI   │
│                                                                              │
│  กติกา: At-least-once · Dedup · Time-window · Late data handling            │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Cross-cutting invariants:**

| Invariant | ขอบเขต | ตรวจโดย |
|-----------|--------|---------|
| Invoice total = sum(lines) + VAT | Money | Money VO + test |
| sum(debit) = sum(credit) | Ledger | Domain invariant |
| Stock in − Stock out = Stock on hand | Inventory | Reconciliation |
| Σ(lot.qty) = Σ(movement.qty) | Inventory | Reconciliation |
| Batch input = output + waste | Production | Yield check |
| Shipment contents = Invoice contents | Transport | Dispatch check |
| KPI actual = Σ(source events) | KPI | Aggregation check |
| ทุก action แตะเงิน/สต็อก → audit log | ทุก module | Middleware |

---

## 1.5 Module Map — ฉบับขยาย (ฉบับสมบูรณ์)

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                       FOOD ERP MODULES (ฉบับสมบูรณ์)                         │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──── LAYER 0: CORE (cross-cutting) ────────────────────────────────┐     │
│  │  money · tenant_context · audit · idempotency · config ·          │     │
│  │  security · settings · database · redis · kafka · logging ·       │     │
│  │  middleware · events (domain event bus)                           │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  ┌──── LAYER 1: FOUNDATION ──────────────────────────────────────────┐     │
│  │  tenancy · authentication · user · employee · customer ·           │     │
│  │  supplier · product · pricing · config                            │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  ┌──── LAYER 2: MONEY PATH (priority 1) ─────────────────────────────┐     │
│  │  order · invoice · ledger · payment · accounting_gateway ·         │     │
│  │  reconciliation · tax                                             │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  ┌──── LAYER 3: GOODS PATH (priority 1) ─────────────────────────────┐     │
│  │  inventory · warehouse · lot · production · recipe ·               │     │
│  │  quality · waste · procurement · traceability                     │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  ┌──── LAYER 4: OPERATIONS (priority 2) ─────────────────────────────┐     │
│  │  transport · delivery · route · gps · retail · pos · shift ·      │     │
│  │  line_channel · promotion · loyalty                               │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  ┌──── LAYER 5: INTELLIGENCE (priority 2-3) ─────────────────────────┐     │
│  │  reporting · analytics · forecast · kpi · satisfaction ·           │     │
│  │  recommendation                                                    │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  ┌──── LAYER 6: MONITORING & SENSING (priority 2) ───────────────────┐     │
│  │  iot · cctv · monitoring · backup · alerting · audit_viewer        │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  ┌──── LAYER 7: TEMPLATES ───────────────────────────────────────────┐     │
│  │  health · example · blank                                          │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

**รายชื่อ module ทั้งหมด (30+ modules):**

| # | Module | Layer | Priority | เหตุผล |
|---|--------|-------|----------|--------|
| 1 | `money` (core) | 0 | 🔴 | Decimal primitive |
| 2 | `tenant_context` (core) | 0 | 🔴 | Multi-company |
| 3 | `audit` (core) | 0 | 🔴 | ทุก action ต้อง log |
| 4 | `idempotency` (core) | 0 | 🔴 | Retry-safe |
| 5 | `config` (core) | 0 | 🔴 | VAT, waste%, pricing rules |
| 6 | `events` (core) | 0 | 🔴 | Domain event bus |
| 7 | `tenancy` | 1 | 🔴 | Multi-company |
| 8 | `authentication` | 1 | 🔴 | ตาม template |
| 9 | `user` | 1 | 🔴 | ตาม template |
| 10 | `employee` | 1 | 🟠 | พนักงาน + shift |
| 11 | `customer` | 1 | 🔴 | B2B/B2C |
| 12 | `supplier` | 1 | 🟠 | จัดซื้อ |
| 13 | `product` | 1 | 🔴 | สินค้า + barcode |
| 14 | `pricing` | 1 | 🔴 | หลายระดับราคา |
| 15 | `order` | 2 | 🔴 | ต้นทาง |
| 16 | `invoice` | 2 | 🔴 | หัวใจ |
| 17 | `ledger` | 2 | 🔴 | บัญชี |
| 18 | `payment` | 2 | 🔴 | รับชำระ |
| 19 | `accounting_gateway` | 2 | 🔴 | Cloud sync |
| 20 | `tax` | 2 | 🔴 | VAT, WHT |
| 21 | `reconciliation` | 2 | 🔴 | Audit engine |
| 22 | `inventory` | 3 | 🔴 | สต็อก |
| 23 | `warehouse` | 3 | 🔴 | โกดัง |
| 24 | `lot` | 3 | 🔴 | Lot/Expiry |
| 25 | `production` | 3 | 🔴 | การผลิต |
| 26 | `recipe` | 3 | 🟠 | สูตร |
| 27 | `quality` | 3 | 🟠 | QC |
| 28 | `waste` | 3 | 🟠 | ของเสีย |
| 29 | `procurement` | 3 | 🟠 | จัดซื้อ |
| 30 | `traceability` | 3 | 🔴 | QR/RFID |
| 31 | `transport` | 4 | 🟠 | ขนส่ง |
| 32 | `delivery` | 4 | 🟠 | ส่งของ |
| 33 | `route` | 4 | 🟠 | เส้นทาง |
| 34 | `gps` | 4 | 🟠 | ติดตาม |
| 35 | `retail` | 4 | 🟠 | ร้านค้า |
| 36 | `pos` | 4 | 🟠 | ขายหน้าร้าน |
| 37 | `shift` | 4 | 🟠 | กะ/ลิ้นชัก |
| 38 | `line_channel` | 4 | 🟠 | รับออเดอร์ |
| 39 | `promotion` | 4 | 🟡 | โปรโมชัน |
| 40 | `loyalty` | 4 | 🟡 | สมาชิก |
| 41 | `reporting` | 5 | 🔴 | รายงาน |
| 42 | `analytics` | 5 | 🟠 | วิเคราะห์ |
| 43 | `forecast` | 5 | 🟠 | คาดเดา |
| 44 | `kpi` | 5 | 🟠 | KPI |
| 45 | `satisfaction` | 5 | 🟡 | ประเมิน |
| 46 | `recommendation` | 5 | 🟡 | แนะนำ |
| 47 | `iot` | 6 | 🟠 | เซ็นเซอร์ |
| 48 | `cctv` | 6 | 🟡 | กล้อง |
| 49 | `monitoring` | 6 | 🔴 | ติดตาม |
| 50 | `backup` | 6 | 🔴 | สำรอง |
| 51 | `alerting` | 6 | 🟠 | แจ้งเตือน |
| 52 | `audit_viewer` | 6 | 🟠 | ดู audit |
| 53 | `health` | 7 | 🔴 | ตาม template |
| 54 | `example` | 7 | 🟢 | ตาม template |
| 55 | `blank` | 7 | 🟢 | template |

---

## 1.6 หลักการออกแบบ 12 ข้อ (ขยายจาก 8 ข้อ)

```text
[1]  Money is Domain Invariant — Decimal + transaction + read-back
[2]  Read-Back Verification — เขียนแล้วอ่านกลับมาเทียบก่อน commit
[3]  Idempotency Everywhere on Money/Goods Path
[4]  Append-Only Audit — INSERT เท่านั้น
[5]  Schema-Per-Tenant — แยกบริษัทในระดับ PostgreSQL schema
[6]  Outbox for External Sync — เขียน DB ก่อน sync cloud
[7]  Reversible Ledger — ห้ามลบ entry ต้อง reversal
[8]  Observable by Default — log + money/goods-path probe
[9]  Lot Traceability — ทุก lot ต้อง trace ได้ forward+backward
[10] FEFO/FIFO by Default — สต็อกต้องหมุนตามวันหมดอายุ/รับก่อน
[11] Event-Driven for Analytics — ใช้ Kafka/outbox สำหรับ BI/KPI
[12] Config over Code — VAT, waste%, pricing ต้อง config ไม่ hardcode
```

---

## 1.7 Data Architecture (ขยาย)

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                          DATA LAYERS                                          │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─── OLTP (PostgreSQL) ─────────────────────────────────────────────┐     │
│  │  Schema-per-tenant: company_a, company_b, ...                      │     │
│  │  • Money: invoices, ledger, payments                              │     │
│  │  • Goods: inventory, lots, movements, batches                     │     │
│  │  • Ops: shipments, routes, shifts, pos_sales                      │     │
│  │  • Foundation: users, customers, products, config                 │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  ┌─── CACHE (Redis) ─────────────────────────────────────────────────┐     │
│  │  • Idempotency keys  • Token blacklist  • Rate limit              │     │
│  │  • Session cache  • Config cache  • Price cache                   │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  ┌─── STREAM (Kafka) ────────────────────────────────────────────────┐     │
│  │  • Domain events (invoice.issued, stock.posted, batch.done)       │     │
│  │  • IoT telemetry (temp, humidity, GPS)                            │     │
│  │  • POS events (sale, return, void)                                │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  ┌─── SEARCH (Elasticsearch) ────────────────────────────────────────┐     │
│  │  • Audit log  • Traceability index  • Product search              │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  ┌─── OLAP (PostgreSQL + materialized views) ───────────────────────┐     │
│  │  • Daily/weekly/monthly/quarterly/yearly aggregates              │     │
│  │  • 3Y / 5Y historical  • KPI snapshots  • Forecast inputs        │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  ┌─── OBJECT STORE (S3/GCS) ─────────────────────────────────────────┐     │
│  │  • Backup  • CCTV footage  • Invoice PDF  • Import files          │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

# 📗 PART 2 — แผนการดำเนินงาน (ฉบับปรับปรุง)

## 2.1 หลักคิดของแผน (ปรับใหม่)

เดิม: Stabilize → Harden → Handoff → Expand

ใหม่: **แยกเป็น 2 แกน** — *Reliability* (เงิน/สินค้า) + *Capability* (ธุรกิจ)

```text
        RELIABILITY (แกน Y)
             ▲
             │
        HIGH │  ┌──────────┐
             │  │ STABILIZE│  ← เดือน 1-2: เงินนิ่ง
             │  │ + GOODS  │     สต็อกนิ่ง
             │  └────┬─────┘
             │       │
             │  ┌────▼─────┐
             │  │ HARDEN   │  ← เดือน 3: test + backup
             │  │ + VERIFY │     + verify
             │  └────┬─────┘
             │       │
             │  ┌────▼─────┐
             │  │ HANDOFF  │  ← เดือน 4: คนที่ 2
             │  └────┬─────┘
             │       │
        LOW  │  ┌────▼──────────────────────────┐
             │  │ EXPAND (Capability)           │  ← เดือน 5-12
             │  │ Transport · Retail · Forecast │
             │  │ Traceability · KPI · Analytics│
             │  └───────────────────────────────┘
             └──────────────────────────────────────►
                   LOW              HIGH   CAPABILITY (แกน X)
```

**หลักคิดใหม่:**
- **Reliability ก่อน Capability** — ทำให้เงิน/สินค้านิ่งก่อน อย่าเพิ่งสร้างฟีเจอร์ใหม่
- **แกน Capability ขยายได้ตามลำดับธุรกิจ** — ขนส่ง → ร้านค้า → Traceability → วิเคราะห์
- **ทุก Capability ต้องผ่าน Reliability gate** — สร้าง module ใหม่ต้องมี audit/idempotency/reconciliation ตั้งแต่ต้น

---

## 2.2 Priority Matrix (ฉบับปรับปรุง — 4 Quadrants × 3 Layers)

```text
                     HIGH IMPACT (ต่อเงิน/สินค้า)
                              ▲
                              │
   ┌──────────────────────────┼──────────────────────────┐
   │  QUICK WIN               │  BIG BET                 │
   │  (ทำก่อน)                │  (ลงทุนหนัก)              │
   │                          │                          │
   │  • Money VO              │  • Invoice module        │
   │  • Audit log             │  • Ledger                │
   │  • Idempotency           │  • Inventory + Lot       │
   │  • Config (VAT/waste)    │  • Production            │
   │  • Recon check 5 ตัว     │  • Reconciliation engine │
   │  • Health probe          │  • Backup/Restore        │
   │  • Employee/Shift        │  • Traceability (QR/RFID)│
   │                          │  • Transport + GPS       │
   │                          │  • Reporting (D/W/M/Q/Y) │
LOW├──────────────────────────┼──────────────────────────┤HIGH
EFFORT                       │                          EFFORT
   │  FILL-IN                 │  MONEY PIT (เลี่ยง)       │
   │  (ทำทีหลัง)              │  (อย่าเพิ่ง)              │
   │                          │                          │
   │  • Satisfaction          │  • CCTV AI (full)        │
   │  • Loyalty               │  • Recommendation engine │
   │  • Promotion             │  • Rewrite ทั้งระบบ      │
   │  • CCTV store (ไม่ AI)   │  • Custom BI platform    │
   │                          │                          │
   └──────────────────────────┼──────────────────────────┘
                              │
                     LOW IMPACT (ต่อเงิน/สินค้า)
```

---

## 2.3 แผนรายเฟส (Phase Plan) — ฉบับปรับปรุง 6 เฟส

### 🔵 Phase 0 — Recon (สัปดาห์ 0)

เหมือนเดิม — แต่เพิ่มการสำรวจ **Goods Path** และ **Data Path**

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│  OBJECTIVE: เข้าใจระบบเดิม + 3 paths (Money/Goods/Data)                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  MONEY PATH RECON:                                                          │
│  □ วาด data flow ของ invoice → ledger → cloud                              │
│  □ รัน ad-hoc recon query 5 ตัว                                             │
│  □ ตรวจ backup/restore ที่มี                                                │
│                                                                             │
│  GOODS PATH RECON:                                                          │
│  □ วาด data flow ของ stock: receive → store → issue → ship                │
│  □ ตรวจ lot/expiry tracking                                                 │
│  □ ตรวจ production batch + yield                                            │
│                                                                             │
│  DATA PATH RECON:                                                           │
│  □ ตรวจ log/monitoring ที่มี                                                │
│  □ ตรวจ IoT/CCTV integration                                                │
│  □ ตรวจ reporting ที่มีอยู่                                                 │
│                                                                             │
│  DELIVERABLE: System Health Report (3 paths) + Risk Register + Gap Map     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 🟢 Phase 1 — Stabilize Money & Goods (เดือน 1-2)

**เป้าหมาย:** เงินนิ่ง + สต็อกนิ่ง + มีเครื่องมือจับปัญหา

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│  MONTH 1: MONEY PATH STABILIZE                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Week 1:  Core primitives                                                  │
│           ├─ core/money.py (Decimal + VAT)                                  │
│           ├─ core/audit.py (append-only)                                    │
│           ├─ core/idempotency.py                                            │
│           ├─ core/config.py (VAT, waste%, pricing rules)                   │
│           └─ core/events.py (domain event bus)                              │
│                                                                             │
│  Week 2:  Reconciliation + bug fix                                          │
│           ├─ modules/reconciliation/ (5 checks)                            │
│           ├─ modules/invoice/ (stabilize)                                   │
│           ├─ modules/ledger/ (stabilize)                                    │
│           └─ แก้ bug อันดับ 1-3 + regression test                            │
│                                                                             │
│  Week 3:  Backup + Monitoring                                               │
│           ├─ modules/backup/ (per-schema pg_dump)                          │
│           ├─ modules/monitoring/ (health + money probe)                    │
│           └─ modules/alerting/ (LINE/email alert)                          │
│                                                                             │
│  Week 4:  Deploy + verify                                                   │
│           ├─ Deploy production + read-back verify                           │
│           ├─ Runbook (deploy, rollback, restore)                           │
│           └─ แก้ bug อันดับ 4-7                                              │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  MONTH 2: GOODS PATH STABILIZE                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Week 5-6: Inventory core                                                   │
│            ├─ modules/inventory/ (movement, balance)                       │
│            ├─ modules/lot/ (lot, expiry, FEFO)                            │
│            ├─ modules/warehouse/ (location, bin)                          │
│            └─ Goods reconciliation: Σmovement = balance                    │
│                                                                             │
│  Week 7-8: Production + Procurement                                         │
│            ├─ modules/production/ (batch, yield)                          │
│            ├─ modules/recipe/ (BOM, yield%)                                │
│            ├─ modules/waste/ (ของเสีย, waste%)                            │
│            ├─ modules/procurement/ (PO, receive)                          │
│            └─ Yield reconciliation: input = output + waste                 │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  DELIVERABLE:                                                               │
│   • Money path: audit + idempotency + recon + backup + monitor            │
│   • Goods path: inventory + lot + production + recon                      │
│   • Bug 7 ตัวแรกถูกแก้ + test                                             │
│   • Runbook ครบ                                                            │
│                                                                             │
│  SUCCESS METRIC:                                                            │
│   • Money recon discrepancy = 0 เป็นเวลา 14 วัน                            │
│   • Goods recon discrepancy = 0 เป็นเวลา 14 วัน                            │
│   • Restore พิสูจน์ read-back 100%                                         │
│   • MoneyPathProbe + GoodsPathProbe ผ่านทุก 5 นาที                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 🟡 Phase 2 — Harden & Verify (เดือน 3)

**เป้าหมาย:** Test coverage + outbox + traceability foundation

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│  MONTH 3: HARDEN                                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Week 9-10:  Test coverage + Outbox                                         │
│              ├─ Integration test: money + goods path                       │
│              ├─ Property-based test: Money, VAT, yield                     │
│              ├─ Chaos test: kill worker → retry                            │
│              ├─ Idempotency test: ยิงซ้ำ 100 → ได้ 1                        │
│              ├─ Concurrency test: ออก invoice พร้อมกัน                     │
│              ├─ modules/accounting_gateway/ (outbox + retry)              │
│              └─ modules/tax/ (VAT, WHT)                                   │
│                                                                             │
│  Week 11-12: Traceability foundation                                        │
│              ├─ modules/traceability/ (QR generation)                     │
│              ├─ modules/product/ (barcode/QR support)                     │
│              ├─ Traceability index ใน Elasticsearch                        │
│              ├─ Forward trace: lot → shipment → customer                   │
│              └─ Backward trace: customer → lot → supplier                  │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  DELIVERABLE:                                                               │
│   • Test coverage ≥ 80% ใน money + goods path                              │
│   • Outbox + retry ทำงานได้                                                │
│   • QR traceability ทำงาน forward + backward                               │
│   • Cloud sync ไม่ double-charge                                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 🟠 Phase 3 — Handoff (เดือน 4)

**เป้าหมาย:** คนที่ 2 deploy + restore ได้

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│  MONTH 4: HANDOFF                                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Week 13-14: Documentation                                                  │
│              ├─ Architecture doc (เอกสารนี้ + ทุก module)                  │
│              ├─ Runbook: deploy, rollback, restore, incident              │
│              ├─ Onboarding guide                                            │
│              ├─ Video walkthrough money + goods path                       │
│              └─ Module-by-module deep dive                                 │
│                                                                             │
│  Week 15-16: Training & Shadow                                              │
│              ├─ สอนคนที่ 2: deploy staging                                 │
│              ├─ สอนคนที่ 2: restore backup                                 │
│              ├─ สอนคนที่ 2: รัน recon + อ่านผล                             │
│              ├─ สอนคนที่ 2: แก้ bug ด้วย AI tools                          │
│              └─ Pair deploy กับ owner                                      │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  DELIVERABLE:                                                               │
│   • คนที่ 2 deploy ได้โดยไม่มี owner                                        │
│   • คนที่ 2 restore ได้โดยไม่มี owner                                       │
│   • Bus factor ≥ 2                                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 🔴 Phase 4 — Expand Operations (เดือน 5-7)

**เป้าหมาย:** ขนส่ง + ร้านค้า + LINE + GPS

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│  MONTH 5: TRANSPORT + DELIVERY                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  ├─ modules/transport/ (shipment, carrier)                                 │
│  ├─ modules/delivery/ (POD, signature)                                     │
│  ├─ modules/route/ (route planning, optimization)                          │
│  ├─ modules/gps/ (real-time tracking, geofence)                            │
│  ├─ Cold-chain monitoring (temp sensor integration)                        │
│  └─ Delivery reconciliation: shipment = invoice                            │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  MONTH 6: RETAIL + POS                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  ├─ modules/retail/ (store, branch)                                        │
│  ├─ modules/pos/ (sale, return, void)                                      │
│  ├─ modules/shift/ (open, close, cash drawer)                              │
│  ├─ modules/pricing/ (multi-tier: B2B/B2C/promotion)                      │
│  ├─ modules/promotion/ (discount, bundle)                                  │
│  └─ modules/loyalty/ (member, points)                                      │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  MONTH 7: LINE + IoT                                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  ├─ modules/line_channel/ (webhook, order parsing)                         │
│  ├─ modules/iot/ (MQTT ingest, temp/humidity)                              │
│  ├─ Alert rules: temp out-of-range → LINE alert                           │
│  └─ modules/cctv/ (store footage, no AI yet)                               │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  DELIVERABLE:                                                               │
│   • ขนส่ง + GPS tracking ใช้งานได้                                         │
│   • ร้านค้า + POS ใช้งานได้                                                │
│   • LINE รับออเดอร์อัตโนมัติ                                                │
│   • IoT เซ็นเซอร์ + alert                                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 🟣 Phase 5 — Expand Intelligence (เดือน 8-10)

**เป้าหมาย:** รายงาน + KPI + วิเคราะห์ + คาดเดา

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│  MONTH 8: REPORTING                                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  ├─ modules/reporting/                                                     │
│  │   ├─ Daily report (sales, cash, stock)                                  │
│  │   ├─ Weekly report (branch performance)                                 │
│  │   ├─ Monthly report (P&L, VAT, stock)                                  │
│  │   ├─ Quarterly report (business review)                                 │
│  │   ├─ Yearly report (annual)                                             │
│  │   ├─ 3Y / 5Y historical report                                          │
│  │   └─ Export: PDF, Excel, LINE notification                              │
│  └─ Materialized views + scheduled refresh                                 │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  MONTH 9: KPI + SATISFACTION                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│  ├─ modules/kpi/                                                           │
│  │   ├─ KPI definition (company/branch/team/individual)                   │
│  │   ├─ KPI target vs actual                                               │
│  │   ├─ KPI cascade + scorecard                                            │
│  │   └─ KPI alert (ต่ำกว่าเป้า)                                            │
│  ├─ modules/satisfaction/                                                  │
│  │   ├─ NPS survey (LINE)                                                  │
│  │   ├─ CSAT rating                                                        │
│  │   └─ Feedback analysis                                                  │
│  └─ modules/employee/ (ขยาย: KPI ผูก employee)                            │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  MONTH 10: FORECAST + ANALYTICS                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  ├─ modules/analytics/                                                     │
│  │   ├─ Sales analytics (product, branch, channel)                         │
│  │   ├─ Customer analytics (RFM, cohort)                                   │
│  │   └─ Profitability (product, customer)                                  │
│  ├─ modules/forecast/                                                      │
│  │   ├─ Demand forecast (product × branch × day)                           │
│  │   ├─ Production plan suggestion                                         │
│  │   ├─ Purchase suggestion                                                │
│  │   └─ Seasonality + trend                                                │
│  └─ modules/recommendation/ (เริ่มเบา)                                     │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  DELIVERABLE:                                                               │
│   • รายงานครบ D/W/M/Q/Y/3Y/5Y                                              │
│   • KPI ทุกระดับ + scorecard                                               │
│   • Forecast การผลิต + การซื้อ                                              │
│   • Satisfaction + NPS                                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### ⚫ Phase 6 — Rollout to Affiliates (เดือน 11-12)

**เป้าหมาย:** นำ ERP กลางไปใช้บริษัทในเครือ

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│  MONTH 11-12: AFFILIATE ROLLOUT                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ├─ modules/tenancy/ (multi-company provisioning)                          │
│  ├─ Schema provisioning อัตโนมัติ                                          │
│  ├─ Chart of accounts มาตรฐานต่อบริษัท                                     │
│  ├─ Config per company (VAT, numbering, terms)                            │
│  ├─ Onboard ลูกค้า B2B รายใหญ่                                              │
│  ├─ สอนพนักงานบริษัทในเครือ                                                │
│  └─ Multi-tenant isolation test                                             │
│                                                                             │
│  DELIVERABLE:                                                               │
│   • บริษัทในเครือใช้งาน ERP กลางได้                                        │
│   • พนักงานบริษัทในเครือได้รับการสอน                                       │
│   • Multi-tenant isolation พิสูจน์แล้ว                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2.4 Timeline แบบ Gantt (12 เดือน)

```text
         │ M1  │ M2  │ M3  │ M4  │ M5  │ M6  │ M7  │ M8  │ M9  │ M10 │ M11 │ M12 │
─────────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
Phase 0  │██   │     │     │     │     │     │     │     │     │     │     │     │
Recon    │     │     │     │     │     │     │     │     │     │     │     │     │
─────────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
Phase 1  │█████│█████│     │     │     │     │     │     │     │     │     │     │
Stabilize│Money│Goods│     │     │     │     │     │     │     │     │     │     │
─────────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
Phase 2  │     │     │█████│     │     │     │     │     │     │     │     │     │
Harden   │     │     │     │     │     │     │     │     │     │     │     │     │
─────────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
Phase 3  │     │     │     │█████│     │     │     │     │     │     │     │     │
Handoff  │     │     │     │     │     │     │     │     │     │     │     │     │
─────────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
Phase 4  │     │     │     │     │█████│█████│█████│     │     │     │     │     │
Ops      │     │     │     │     │Trans│POS  │LINE │     │     │     │     │     │
─────────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
Phase 5  │     │     │     │     │     │     │     │█████│█████│█████│     │     │
Intel    │     │     │     │     │     │     │     │Rep  │KPI  │Fcst │     │     │
─────────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
Phase 6  │     │     │     │     │     │     │     │     │     │     │█████│█████│
Rollout  │     │     │     │     │     │     │     │     │     │     │     │     │
─────────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘
```

---

## 2.5 Module → Phase Mapping (ตารางเต็ม)

| Phase | เดือน | Module ที่ทำ | Output |
|-------|-------|-------------|--------|
| **0** | 0 | — | Health Report + Risk Register |
| **1** | 1 | money, audit, idempotency, config, events, reconciliation, invoice (stab), ledger (stab), backup, monitoring, alerting | Money นิ่ง |
| **1** | 2 | inventory, lot, warehouse, production, recipe, waste, procurement | Goods นิ่ง |
| **2** | 3 | accounting_gateway, tax, traceability, test suite | Test + Traceability |
| **3** | 4 | Documentation, Training, Handoff | คนที่ 2 |
| **4** | 5 | transport, delivery, route, gps | ขนส่ง |
| **4** | 6 | retail, pos, shift, pricing, promotion, loyalty | ร้านค้า |
| **4** | 7 | line_channel, iot, cctv (store) | LINE + IoT |
| **5** | 8 | reporting | รายงาน |
| **5** | 9 | kpi, satisfaction, employee (ขยาย) | KPI |
| **5** | 10 | analytics, forecast, recommendation | วิเคราะห์ |
| **6** | 11-12 | tenancy (rollout), affiliate onboarding | บริษัทในเครือ |

---

## 2.6 Risk Register (ฉบับขยาย)

| # | ความเสี่ยง | โอกาส | ผลกระทบ | Phase | Mitigation |
|---|-----------|-------|---------|-------|-----------|
| 1 | แก้ bug แล้วทำเงินเพี้ยน | กลาง | สูงมาก | 1 | Staging + read-back + rollback |
| 2 | Backup restore ไม่ได้ | กลาง | สูงมาก | 1 | Test restore ทุกสัปดาห์ |
| 3 | Stock ไม่ตรง | สูง | สูง | 1 | Goods recon + cycle count |
| 4 | Lot/expiry หลุด | กลาง | สูง | 1 | FEFO + alert |
| 5 | Cloud API เปลี่ยน | ต่ำ | สูง | 2 | Abstraction layer |
| 6 | Owner ติดงานอื่น | สูง | กลาง | 3 | Document + pair |
| 7 | AI tool ให้ข้อมูลผิด | สูง | กลาง | ทุก | Code review + test + read-back |
| 8 | Invoice เลขซ้ำ | ต่ำ | สูง | 1 | SELECT FOR UPDATE + unique |
| 9 | VAT คำนวณผิด | กลาง | สูง | 1-2 | Property-based test |
| 10 | คนที่ 2 ลาออก | ต่ำ | กลาง | 3 | 3 คน deploy ได้ |
| 11 | ข้อมูลลูกค้ารั่ว | ต่ำ | สูงมาก | ทุก | Encryption + audit |
| 12 | Schema migration พัง | กลาง | สูง | ทุก | Auto-migration + backup ก่อน |
| 13 | IoT sensor หลุด | กลาง | กลาง | 4 | Buffer + alert |
| 14 | GPS ไม่แม่น | กลาง | กลาง | 4 | Geofence + manual override |
| 15 | Forecast แม่นต่ำ | สูง | กลาง | 5 | Backtest + human override |
| 16 | KPI ขัดแย้งกัน | กลาง | กลาง | 5 | KPI cascade review |
| 17 | POS offline | กลาง | สูง | 4 | Offline mode + sync |
| 18 | Traceability ขาด | กลาง | สูง | 2 | End-to-end test |
| 19 | รายงานช้า | กลาง | กลาง | 5 | Materialized view + cache |
| 20 | Multi-tenant รั่ว | ต่ำ | สูงมาก | 6 | Isolation test |

---

## 2.7 Definition of Done (ต่อ Phase) — ฉบับขยาย

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 1 — STABILIZE                                                        │
│  □ Money recon ผ่าน 14 วันติด                                               │
│  □ Goods recon ผ่าน 14 วันติด                                               │
│  □ Restore พิสูจน์ read-back                                                │
│  □ Bug 7 ตัวแรกมี regression test                                           │
│  □ MoneyPathProbe + GoodsPathProbe ทำงานทุก 5 นาที                         │
│  □ Runbook ครบ                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  PHASE 2 — HARDEN                                                           │
│  □ Test coverage ≥ 80% money + goods path                                  │
│  □ Chaos test ผ่าน                                                          │
│  □ Idempotency test ผ่าน (ยิงซ้ำ 100 → 1)                                  │
│  □ Cloud sync ไม่ double-charge                                             │
│  □ Traceability forward + backward ทำงาน                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  PHASE 3 — HANDOFF                                                          │
│  □ คนที่ 2 deploy + restore ได้โดยไม่มี owner                              │
│  □ Runbook + onboarding guide + video ครบ                                  │
│  □ Bus factor ≥ 2                                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  PHASE 4 — OPERATIONS                                                       │
│  □ ขนส่ง + GPS ทำงาน E2E                                                   │
│  □ POS + Shift + Cash ทำงาน E2E                                            │
│  □ LINE รับออเดอร์อัตโนมัติ ≥ 80%                                          │
│  □ IoT alert ทำงาน < 1 นาที                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  PHASE 5 — INTELLIGENCE                                                     │
│  □ รายงาน D/W/M/Q/Y/3Y/5Y ครบ                                              │
│  □ KPI ทุกระดับ + scorecard                                                │
│  □ Forecast MAPE < 20%                                                     │
│  □ NPS + CSAT เก็บได้อัตโนมัติ                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  PHASE 6 — ROLLOUT                                                          │
│  □ บริษัทในเครือใช้งาน ERP กลางได้                                          │
│  □ Multi-tenant isolation พิสูจน์แล้ว                                       │
│  □ พนักงานบริษัทในเครือได้รับการสอน                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2.8 KPIs (ฉบับขยาย — แบ่ง 4 หมวด)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│  [1] RELIABILITY KPI                                                        │
│   • Money recon discrepancy = 0                                            │
│   • Goods recon discrepancy = 0                                            │
│   • Invoice duplicate rate = 0                                             │
│   • VAT error rate = 0                                                     │
│   • Cloud sync success rate ≥ 99.9%                                        │
│   • Stock accuracy ≥ 99%                                                   │
│   • Lot traceability = 100%                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  [2] OPERATIONAL KPI                                                        │
│   • Backup restore success = 100%                                          │
│   • MoneyPathProbe + GoodsPathProbe pass rate ≥ 99%                        │
│   • MTTR (incident) < 30 นาที                                             │
│   • Deploy โดยคนที่ 2 สำเร็จ = 100%                                        │
│   • POS uptime ≥ 99.5%                                                     │
│   • Delivery on-time ≥ 95%                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  [3] BUSINESS KPI                                                           │
│   • Gross margin ≥ target                                                  │
│   • Waste % ≤ target (config)                                              │
│   • Forecast accuracy MAPE < 20%                                           │
│   • Customer NPS ≥ target                                                  │
│   • Inventory turnover ≥ target                                            │
│   • Cash conversion cycle ≤ target                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│  [4] TEAM KPI                                                               │
│   • จำนวนคนที่ deploy ได้ ≥ 2                                              │
│   • จำนวนคนที่ restore ได้ ≥ 2                                             │
│   • Bus factor ≥ 2                                                         │
│   • Documentation coverage ≥ 90%                                           │
│   • Test coverage ≥ 80% (money + goods)                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2.9 Deliverables Summary (ฉบับขยาย)

| Phase | Deliverable หลัก | ผู้รับ |
|-------|------------------|--------|
| 0 | System Health Report (3 paths) + Risk Register | Owner |
| 1 | Money + Goods นิ่ง, Audit, Recon, Backup, Monitor | Owner |
| 2 | Test suite, Outbox, Traceability foundation | Owner |
| 3 | Runbook, Onboarding, คนที่ 2 | Owner + ทีม |
| 4 | Transport, Retail POS, LINE, IoT | ทีมปฏิบัติการ |
| 5 | Reporting, KPI, Forecast, Analytics | ผู้บริหาร |
| 6 | Multi-tenant ERP + Affiliate onboarding | บริษัทในเครือ |

---

## 2.10 แผนสำรอง (Contingency)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│  IF เงินไม่นิ่งในเดือน 1 →                                                │
│     หยุดทุกอย่าง, โฟกัส money path, เลื่อน goods path ไปเดือน 3            │
│                                                                             │
│  IF คนที่ 2 ยังไม่พร้อมในเดือน 4 →                                        │
│     เลื่อน expand ทั้งหมด, โฟกัส handoff จนเสร็จ                            │
│                                                                             │
│  IF forecast แม่นต่ำ →                                                    │
│     ใช้ rule-based + human override, ค่อย ๆ เพิ่ม ML                       │
│                                                                             │
│  IF IoT/CCTV มีปัญหา →                                                    │
│     Degrade gracefully, ไม่ให้กระทบ money/goods path                       │
│                                                                             │
│  IF บริษัทในเครือพร้อมก่อนกำหนด →                                        │
│     ทำ tenancy ตั้งแต่เดือน 3 (parallel กับ harden)                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# 📌 สรุปการเปลี่ยนแปลงจาก Revision 1

| ประเด็น | Revision 1 | Revision 2 |
|---------|-----------|-----------|
| จำนวน module | ~20 | **55** |
| Phase | 5 | **7** (เพิ่ม Recon + Intelligence + Rollout) |
| ระยะเวลา | 5 เดือน | **12 เดือน** |
| เส้นทางหลัก | Money Path | **Money + Goods + Data Path** |
| Layer | 4 | **8 layers** |
| Design principles | 8 | **12** |
| Priority matrix | 2 quadrants | **4 quadrants × 3 layers** |
| KPI | 3 หมวด | **4 หมวด** |
| Risk register | 10 | **20** |

---

## 🔜 Part 3+ (ตอนถัดไป) — ราย Module

จะลงรายละเอียด module ตามลำดับความสำคัญ:

| Part | Module | Layer | Priority |
|------|--------|-------|----------|
| **Part 3** | Core Infrastructure (money, audit, idempotency, config, events, tenant_context) | 0 | 🔴 |
| **Part 4** | Tenancy + Authentication + User | 1 | 🔴 |
| **Part 5** | Invoice + Ledger + Tax | 2 | 🔴 |
| **Part 6** | Payment + Accounting Gateway | 2 | 🔴 |
| **Part 7** | Reconciliation Engine | 2 | 🔴 |
| **Part 8** | Inventory + Warehouse + Lot | 3 | 🔴 |
| **Part 9** | Production + Recipe + Waste + Quality | 3 | 🔴 |
| **Part 10** | Procurement + Supplier | 3 | 🟠 |
| **Part 11** | Traceability (QR/RFID/GPS) | 3 | 🔴 |
| **Part 12** | Order + Pricing + Promotion + Loyalty | 2/4 | 🟠 |
| **Part 13** | Transport + Delivery + Route + GPS | 4 | 🟠 |
| **Part 14** | Retail + POS + Shift | 4 | 🟠 |
| **Part 15** | LINE Channel + IoT + CCTV | 4/6 | 🟠 |
| **Part 16** | Reporting + Analytics + Forecast | 5 | 🟠 |
| **Part 17** | KPI + Satisfaction + Employee | 5 | 🟠 |
| **Part 18** | Monitoring + Backup + Alerting + Audit Viewer | 6 | 🔴 |

**แต่ละ Part จะมี:**
1. Purpose & Scope
2. Domain Model (entities, VOs, invariants)
3. Domain Events
4. Use Cases
5. Application Interfaces (ports)
6. Infrastructure (models, repositories)
7. Presentation (API endpoints, schemas)
8. Database Schema (DDL)
9. Folder Structure
10. Tests
11. Dependencies (module → module)
12. Phase ที่ทำ + Definition of Done

---

 