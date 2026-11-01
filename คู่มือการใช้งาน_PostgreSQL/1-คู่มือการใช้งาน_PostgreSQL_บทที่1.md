# หนังสือ: คู่มือการใช้งาน PostgreSQL สำหรับ DevOps Engineer, Cloud Engineer และ DBA  
## ด้วย Prometheus, Alertmanager และ Monitoring สำหรับงาน Production

> หมายเหตุ: คำว่า **“Ppostgresql”** ในโจทย์ขอปรับเป็น **PostgreSQL** เพื่อความถูกต้องทางเทคนิค  
> เนื่องจากหนังสือ 120 บทมีขนาด เอกสารนี้จึงเป็น **โครงเล่มสมบูรณ์ 120 บท + ต้นแบบบทมาตรฐาน + ตัวอย่างบทสำคัญ + Template พร้อมใช้งานจริง** สามารถนำไปขยายเป็นเล่มเต็มหรือสั่งเขียนรายบทต่อได้

---

# 1. ข้อมูลหนังสือ

| รายการ | รายละเอียด |
|---|---|
| ชื่อหนังสือ | คู่มือการใช้งาน PostgreSQL สำหรับ DevOps Engineer, Cloud Engineer และ DBA |
| ชื่อรอง | Monitoring, Prometheus และ Alertmanager สำหรับระบบ Production |
| กลุ่มผู้อ่าน | DevOps Engineer, Cloud Engineer, DBA, SRE, System Engineer |
| โทน | ทางการ กระชับ เน้นใช้งานจริง |
| จำนวนบท | 120 บท |
| ขอบเขต | PostgreSQL, Prometheus, Alertmanager, Monitoring, Workflow, KPI/SMART/RCA/PSR |
| รูปแบบบท | เรื่อง → วัตถุประสงค์ → เป้าหมาย → เนื้อหาย่อ → ประโยชน์ → ข้อควรระวัง → ข้อดี/ข้อเสีย → ข้อห้าม → รายละเอียด → ตัวอย่าง → สรุป → แหล่งอ้างอิง |

---

# 2. บทนำของหนังสือ

## 2.1 วัตถุประสงค์
1. เพื่อให้ผู้อ่านเข้าใจการใช้งาน PostgreSQL ในสภาพแวดล้อม Production อย่างถูกต้อง  
2. เพื่อให้ DevOps Engineer และ Cloud Engineer สามารถติดตั้ง ดูแล ปรับแต่ง และ Monitoring PostgreSQL ได้  
3. เพื่อให้ DBA ใช้ Prometheus และ Alertmanager ในการเฝ้าระวังและแจ้งเตือนเหตุการณ์ผิดปกติ  
4. เพื่อสร้างมาตรฐานการทำงานร่วมกันระหว่างทีมปฏิบัติการ ทีมฐานข้อมูล และทีมพัฒนา  
5. เพื่อลดเวลาในการตรวจจับปัญหา แก้ไขปัญหา และป้องกันปัญหาเกิดซ้ำ

## 2.2 เป้าหมาย
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ติดตั้งและตั้งค่า PostgreSQL ที่เหมาะกับ Production
- ออกแบบ Dashboard และ Alert ที่มีคุณภาพ
- ใช้ Prometheus เก็บ Metric จาก PostgreSQL และระบบ
- ใช้ Alertmanager จัดเส้นทางการแจ้งเตือน
- วิเคราะห์ปัญหาเบื้องต้นภายใน 15 นาทีแรก
- วางแผน Backup, Recovery, HA, Upgrade และ Maintenance
- ใช้ KPI, SMART, RCA และ PSR ในการวัดและปรับปรุงระบบ

## 2.3 สรุปย่อ
หนังสือเล่มนี้แบ่งเป็น 12 ส่วน 120 บท ครอบคลุมตั้งแต่สถาปัตยกรรม PostgreSQL การติดตั้ง การปรับแต่ง Performance การทำ Observability ด้วย Prometheus/Grafana การแจ้งเตือนด้วย Alertmanager การ Backup/Recovery ความปลอดภัย HA/Replication การ Upgrade การทำ Safe Migration การ Troubleshooting และ Game Day พร้อมแบบฝึกหัดและ Template ที่นำไปใช้ได้จริง

---

# 3. บทนิยามสำคัญ

| คำศัพท์ | ความหมายโดยย่อ |
|---|---|
| PostgreSQL | ระบบฐานข้อมูลเชิงสัมพันธ์แบบ Open Source ที่มีความสามารถสูง |
| Metric | ตัวเลขที่วัดสถานะของระบบ ณ เวลาหนึ่ง เช่น CPU, Connections, TPS |
| Time-Series Database: TSDB | ฐานข้อมูลที่ออกแบบสำหรับเก็บข้อมูลอนุกรมเวลา |
| Prometheus | ระบบเก็บ Metric แบบ Pull และเป็น TSDB |
| Exporter | โปรแกรมแปลง Metric จากระบบต้นทางให้ Prometheus อ่านได้ |
| Scrape | การที่ Prometheus ไปดึง Metric จาก Target ตามรอบเวลา |
| Alert Rule | กฎที่กำหนดว่าเมื่อ Metric ตรงเงื่อนไขให้แจ้งเตือน |
| Alertmanager | ระบบจัดการเส้นทาง การจัดกลุ่ม และการส่งแจ้งเตือน |
| Monitoring | การเฝ้าระวังสถานะระบบอย่างต่อเนื่อง |
| Observability | ความสามารถในการเข้าใจสถานะภายในระบบจากข้อมูลที่เก็บได้ |
| SLI / SLO | ตัวชี้วัดระดับบริการ / เป้าหมายระดับบริการ |
| RPO | ปริมาณข้อมูลที่ยอมรับได้ว่าจะสูญหายเมื่อเกิดเหตุ |
| RTO | เวลาที่ระบบต้องกลับมาใช้งานได้ |
| RCA | การวิเคราะห์สาเหตุราก |
| PSR | Postmortem / Post-Incident Review การทบทวนหลังเหตุการณ์ |

---

# 4. โครงสร้างหนังสือ 120 บท

## ส่วนที่ 1 ปฐมบทและสถาปัตยกรรม บทที่ 1–10

| บท | ชื่อบท |
|---|---|
| 1 | บทนำ: PostgreSQL ในงาน Production |
| 2 | บทบาท DevOps, Cloud Engineer และ DBA |
| 3 | สถาปัตยกรรม PostgreSQL โดยย่อ |
| 4 | วงจรชีวิตฐานข้อมูล Production |
| 5 | หลักการ Monitoring และ Observability |
| 6 | Prometheus: สถาปัตยกรรมและ Time-Series |
| 7 | Alertmanager: บทบาทและการแจ้งเตือน |
| 8 | การออกแบบระบบแจ้งเตือนที่มีประสิทธิภาพ |
| 9 | Workflow ภาพรวม Data, Metric และ Alert |
| 10 | นิยามศัพท์และตัวย่อ |

## ส่วนที่ 2 ติดตั้งและตั้งค่าพื้นฐาน บทที่ 11–20

| บท | ชื่อบท |
|---|---|
| 11 | เตรียม Linux สำหรับ PostgreSQL |
| 12 | ติดตั้ง PostgreSQL 17/18 อย่างปลอดภัย |
| 13 | Data Checksums และการตรวจสอบความสมบูรณ์ |
| 14 | โครงสร้างไฟล์และ Parameter สำคัญ |
| 15 | Tuning เบื้องต้นตามขนาดเครื่อง |
| 16 | จัดการ Cluster ด้วย pg_lsclusters และ systemd |
| 17 | Logging มาตรฐานสำหรับ Production |
| 18 | ความปลอดภัยเบื้องต้น: SCRAM, TLS และ pg_hba |
| 19 | Role, Privilege และ Timeout |
| 20 | Checklist หลังติดตั้ง |

## ส่วนที่ 3 SQL และการใช้งานประจำวัน บทที่ 21–30

| บท | ชื่อบท |
|---|---|
| 21 | psql และ Meta-command ที่ต้องรู้ |
| 22 | DDL, DML และ Transaction |
| 23 | MVCC และ Isolation Level |
| 24 | Lock และคิว Lock |
| 25 | การอ่าน EXPLAIN และ EXPLAIN ANALYZE |
| 26 | Index เบื้องต้น |
| 27 | Statistics และ Extended Statistics |
| 28 | Partitioning เบื้องต้น |
| 29 | Backup เบื้องต้นด้วย pg_dump |
| 30 | Restore และตรวจสอบผล |

## ส่วนที่ 4 Performance Tuning บทที่ 31–40

| บท | ชื่อบท |
|---|---|
| 31 | pg_stat_statements |
| 32 | หา Query ที่ใช้เวลารวมสูงสุด |
| 33 | Index Health: ซ้ำ ไม่ถูกใช้ และ Invalid |
| 34 | N+1 และ Anti-pattern จาก ORM |
| 35 | Keyset Pagination |
| 36 | ฟังก์ชันครอบคอลัมน์และชนิดข้อมูล |
| 37 | VACUUM และ Bloat |
| 38 | pg_repack |
| 39 | XID Wraparound |
| 40 | Autovacuum รายตารางและ Partition |

## ส่วนที่ 5 Observability บทที่ 41–50

| บท | ชื่อบท |
|---|---|
| 41 | ตัวชี้วัดสำคัญของ PostgreSQL |
| 42 | postgres_exporter |
| 43 | node_exporter |
| 44 | Prometheus Scrape Configuration |
| 45 | PromQL พื้นฐาน |
| 46 | PromQL ขั้นสูง |
| 47 | Grafana Dashboard |
| 48 | Dashboard สำหรับ DBA และ DevOps |
| 49 | pgBadger และ Log Analytics |
| 50 | Textfile Metrics และ Custom Metrics |

## ส่วนที่ 6 Alerting บทที่ 51–60

| บท | ชื่อบท |
|---|---|
| 51 | หลักการออกแบบ Alert |
| 52 | Prometheus Alert Rules |
| 53 | promtool check และ test |
| 54 | Alertmanager Configuration |
| 55 | Routing, Grouping และ Inhibition |
| 56 | Email, Slack และ Webhook |
| 57 | Mailpit และการทดสอบอีเมล |
| 58 | Runbook URL และ Severity |
| 59 | Alert Fatigue |
| 60 | Incident Notification Workflow |

## ส่วนที่ 7 Backup, Recovery และ Security บทที่ 61–70

| บท | ชื่อบท |
|---|---|
| 61 | Backup Strategy, RPO และ RTO |
| 62 | pgBackRest |
| 63 | WAL Archiving |
| 64 | MinIO/S3 Repository |
| 65 | Full, Differential และ Incremental Backup |
| 66 | Restore Test |
| 67 | Point-in-Time Recovery: PITR |
| 68 | Row-Level Security: RLS |
| 69 | Masking และ pgcrypto |
| 70 | pgAudit |

## ส่วนที่ 8 HA และ Replication บทที่ 71–80

| บท | ชื่อบท |
|---|---|
| 71 | Streaming Replication |
| 72 | Replication Slots |
| 73 | Patroni และ etcd |
| 74 | HAProxy |
| 75 | PgBouncer |
| 76 | Switchover |
| 77 | Failover |
| 78 | Split-Brain |
| 79 | pg_rewind |
| 80 | HA Monitoring และ Alert |

## ส่วนที่ 9 Upgrade และ Safe Migration บทที่ 81–90

| บท | ชื่อบท |
|---|---|
| 81 | นโยบายเวอร์ชัน PostgreSQL |
| 82 | pg_upgrade --check |
| 83 | pg_upgrade --link |
| 84 | Upgrade คลัสเตอร์ Patroni |
| 85 | Extension และ Statistics หลัง Upgrade |
| 86 | หลักการ Safe Migration |
| 87 | CREATE INDEX CONCURRENTLY |
| 88 | NOT VALID และ VALIDATE CONSTRAINT |
| 89 | Backfill และ PK Swap |
| 90 | Checklist Zero-Downtime Migration |

## ส่วนที่ 10 Troubleshooting และ Game Day บทที่ 91–100

| บท | ชื่อบท |
|---|---|
| 91 | ลำดับ 15 นาทีแรก |
| 92 | แยก “ล่ม” กับ “ช้า” |
| 93 | Connection Full |
| 94 | Lock Queue |
| 95 | Disk Full และ WAL |
| 96 | Replication Lag |
| 97 | OOM |
| 98 | Data Loss และการตัดสินใจ PITR |
| 99 | Incident Record Template |
| 100 | Game Day Scenarios |

## ส่วนที่ 11 KPI, SMART, RCA และ PSR บทที่ 101–110

| บท | ชื่อบท |
|---|---|
| 101 | KPI สำหรับฐานข้อมูล |
| 102 | KPI สำหรับ Monitoring และ Alert |
| 103 | SMART Goals |
| 104 | Root Cause Analysis: RCA |
| 105 | Post-Incident Review: PSR |
| 106 | SLI, SLO และ Error Budget |
| 107 | Capacity Planning |
| 108 | Maintenance Calendar |
| 109 | แผน 30 วันหลังอบรม |
| 110 | Continuous Improvement |

## ส่วนที่ 12 ตัวอย่างจริงและภาคผนวก บทที่ 111–120

| บท | ชื่อบท |
|---|---|
| 111 | ตัวอย่าง Data Workflow |
| 112 | ตัวอย่าง Metric Workflow |
| 113 | ตัวอย่าง Alert Workflow |
| 114 | Template Runbook |
| 115 | Template Incident Record |
| 116 | แบบฝึกหัดบทที่ 1–4 พร้อมเฉลย |
| 117 | แบบฝึกหัดบทที่ 5–8 พร้อมเฉลย |
| 118 | Cheatsheet PostgreSQL |
| 119 | Cheatsheet Prometheus และ Alertmanager |
| 120 | สรุปหนังสือและแหล่งอ้างอิง |

---

# 5. ต้นแบบบทมาตรฐาน

ทุกบทใช้โครงสร้างเดียวกัน:

1. เรื่อง  
2. วัตถุประสงค์ของหัวข้อ  
3. เป้าหมายของหัวข้อ  
4. เนื้อหาโดยย่อ กระชับ  
5. ประโยชน์ที่ได้รับ  
6. ข้อควรระวัง  
7. ข้อดี  
8. ข้อเสีย  
9. ข้อห้าม ถ้ามี  
10. รายละเอียด  
11. ตัวอย่าง  
12. สรุปย่อ  
13. แหล่งที่มาและแหล่งอ้างอิง  

---


## บทที่ 1 บทนำ: PostgreSQL ในงาน Production

### 1. เรื่อง
ภาพรวมการใช้ PostgreSQL ในระบบ Production สำหรับ DevOps Engineer, Cloud Engineer และ DBA

### 2. วัตถุประสงค์
เพื่อให้ผู้อ่านเข้าใจบทบาทของ PostgreSQL ในระบบจริง และเห็นความเชื่อมโยงระหว่างฐานข้อมูล การ Monitoring และการแจ้งเตือน

### 3. เป้าหมาย
ผู้อ่านสามารถอธิบายองค์ประกอบหลักของระบบ PostgreSQL Production และระบุความรับผิดชอบของแต่ละทีมได้

### 4. เนื้อหาโดยย่อ
PostgreSQL เป็นฐานข้อมูลเชิงสัมพันธ์ที่เหมาะกับงาน Production เพราะมี Transaction, MVCC, Replication, Backup, Extension และเครื่องมือ Monitoring ที่ครบถ้วน ระบบ Production ที่ดีไม่ใช่เพียงฐานข้อมูลที่ทำงานได้ แต่ต้องมี Backup, Recovery, Monitoring, Alerting, Security และ Procedure ที่ชัดเจน

### 5. ประโยชน์ที่ได้รับ
- เข้าใจภาพรวมระบบก่อนลงมือปฏิบัติ
- วางแผนความรับผิดชอบร่วมกันระหว่าง DevOps, Cloud และ DBA
- ลดความเสี่ยงจากการดูแลแบบแยกส่วน

### 6. ข้อควรระวัง
- ห้ามนำคำสั่งจากห้องทดลองไปใช้กับ Production โดยไม่ทดสอบ
- ห้ามใช้ Superuser กับแอปพลิเคชัน
- ห้ามปิด Monitoring หรือ Alert โดยไม่มีเหตุผลและบันทึกไว้

### 7. ข้อดี
- PostgreSQL มี ecosystem ที่สมบูรณ์
- ใช้งานร่วมกับ Prometheus และ Grafana ได้ดี
- มีชุมชนและเอกสารทางการที่เชื่อถือได้

### 8. ข้อเสีย
- Parameter มีจำนวนมาก ต้องเข้าใจก่อนปรับ
- การทำ HA และ Backup ต้องออกแบบให้เหมาะสม
- Alert ที่ไม่ดีทำให้เกิด Alert Fatigue

### 9. ข้อห้าม
- ห้ามปรับ `shared_buffers`, `max_connections` หรือ `work_mem` โดยไม่วัดผล
- ห้ามลบ Index หรือ Backup โดยไม่ตรวจสอบการใช้งาน
- ห้ามทำ PITR ทับระบบจริงโดยไม่มีผู้อนุมัติและแผนยืนยันผล

### 10. รายละเอียด
ระบบ PostgreSQL Production ประกอบด้วย:
1. PostgreSQL Cluster
2. PgBouncer หรือ Connection Pooler
3. HAProxy หรือ Load Balancer
4. Backup Repository เช่น pgBackRest + MinIO/S3
5. Exporters: postgres_exporter, node_exporter
6. Prometheus
7. Alertmanager
8. Grafana
9. Runbook และ Incident Process

### 11. ตัวอย่าง
ตัวอย่างเส้นทางข้อมูลและเหตุการณ์:

```text
Application
   │
   ▼
PgBouncer :6432
   │
   ▼
HAProxy :5000 → Primary PostgreSQL
   │
   ├── postgres_exporter :9187 ──► Prometheus :9090
   ├── node_exporter :9100 ─────► Prometheus :9090
   │
   ▼
Alert Rule → Alertmanager :9093 → Email/Slack → Runbook → ทีมปฏิบัติการ
```

ตัวอย่าง Metric ที่ต้องมี:
- `pg_up`
- `pg_stat_database_xact_commit`
- `pg_stat_activity_count`
- `pg_database_wraparound_age_datfrozenxid_seconds`
- `pg_stat_replication_pg_wal_lsn_diff`
- `node_filesystem_avail_bytes`

### 12. สรุปย่อ
PostgreSQL Production ต้องมีทั้งฐานข้อมูลที่ถูกตั้งค่า การ Monitoring ที่มองเห็นปัญหา และ Alert ที่นำไปสู่การแก้ไขได้จริง บทต่อ ๆ ไปจะเริ่มจากติดตั้งและตั้งค่าพื้นฐานก่อนเข้าสู่ Performance, Observability และ HA

### 13. แหล่งอ้างอิง
- PostgreSQL Documentation: https://www.postgresql.org/docs/
- Prometheus Documentation: https://prometheus.io/docs/
- Alertmanager Documentation: https://prometheus.io/docs/alerting/latest/alertmanager/
- Google SRE Book: https://sre.google/sre-book/

---

# 7. ตัวอย่างบทที่ 51 หลักการออกแบบ Alert

## บทที่ 51 หลักการออกแบบ Alert

### วัตถุประสงค์
เพื่อให้ผู้อ่านออกแบบ Alert ที่ actionable ไม่รบกวน และเชื่อมโยงกับ Runbook ได้

### เป้าหมาย
Alert ทุกตัวต้องตอบได้ว่า “เกิดอะไรขึ้น”, “รุนแรงแค่ไหน”, “ต้องทำอะไรต่อ” และ “ใครรับผิดชอบ”

### หลักการสำคัญ
1. Alert ต้องบอกอาการ ไม่ใช่บอกทุกMetric  
2. ต้องมี Severity: critical, warning, info  
3. ต้องมี `for:` เพื่อลดการกระพริบ  
4. ต้องมี `summary`, `description`, `runbook_url`  
5. ต้องมีเจ้าของและช่องทางแจ้งเตือน  
6. ต้องทดสอบด้วย `promtool test rules`  
7. ต้องทบทวนหลังเกิดเหตุและลด Alert ที่ไม่ actionable

### ตัวอย่าง Alert Rule

```yaml
groups:
  - name: gridcare-postgres
    rules:
      - alert: PostgresDown
        expr: pg_up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "PostgreSQL instance {{ $labels.instance }} down"
          description: "pg_up = 0 ต่อเนื่อง 1 นาที ตรวจ process, network และ exporter"
          runbook_url: "http://gridcare-infra/runbooks/C08-postgres-down.md"

      - alert: PostgresConnectionsHigh
        expr: |
          sum by (instance) (pg_stat_activity_count{datname="gridcare"})
          /
          max by (instance) (pg_settings_max_connections) * 100 > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Connection ใช้งานเกิน 80%"
          description: "ตรวจ PgBouncer, session ค้าง และ idle in transaction"
          runbook_url: "http://gridcare-infra/runbooks/C03-connection-limit-locking.md"
```

### ข้อควรระวัง
- Alert ที่ไม่มี Runbook ทำให้ผู้รับแจ้งเตือนตัดสินใจช้า
- Alert ที่ดังบ่อยเกินไปจะทำให้ทีมละเลย
- ต้องแยก Warning และ Critical ให้ชัดเจน

### ข้อดี
- ลดเวลา detect และตอบสนอง
- ทำให้เกิดมาตรฐานการปฏิบัติการ
- เชื่อมโยง Monitoring กับ Incident Process

### ข้อเสีย
- ต้องใช้เวลาเริ่มต้นในการออกแบบ
- ต้องดูแล Rule ให้ทันสมัย

### ข้อห้าม
- ห้ามตั้ง Alert ทุก Metric โดยไม่มีเกณฑ์
- ห้ามใช้ `for: 0s` กับทุก Rule
- ห้ามส่ง Alert เข้าช่องทางเดียวกันทั้งหมดโดยไม่แยก Severity

### สรุปย่อ
Alert ที่ดีต้อง actionable มี Severity มี Runbook และผ่านการทดสอบ การออกแบบ Alert คือการออกแบบกระบวนการตอบสนอง ไม่ใช่เพียงการเขียน PromQL

---

# 8. Workflow

## 8.1 Data Workflow

```text
[Source: PostgreSQL / Application / Log]
        │
        ▼
[Process: Extract / Transform / Aggregate]
        │
        ▼
[Storage: Prometheus TSDB / Log / Backup Repository]
        │
        ▼
[Output: Grafana Dashboard / Alertmanager / Report]
```

## 8.2 Metric Workflow

```text
PostgreSQL + Linux
        │
        ├── postgres_exporter :9187
        └── node_exporter :9100
        │
        ▼
Prometheus Scrape ทุก 15s
        │
        ▼
Prometheus TSDB
        │
        ├── PromQL → Grafana Dashboard
        └── Alert Rules → Alertmanager
```

## 8.3 Alert Workflow

```text
Metric ผิดปกติ
   │
   ▼
Alert Rule เป็น Pending
   │
   ▼
ครบเงื่อนไข for: → Firing
   │
   ▼
Alertmanager จัดกลุ่ม/เส้นทาง
   │
   ▼
Email / Slack / Webhook
   │
   ▼
เปิด Runbook → แก้ไข → Resolve
   │
   ▼
บันทึก Incident → RCA/PSR → Preventive Action
```

### องค์ประกอบ Workflow
- Input: Metric, Log, Event
- Process: Scrape, Evaluate, Group, Route
- Storage: Prometheus TSDB, Log, Backup
- Output: Dashboard, Alert, Report
- Actor: DevOps, Cloud Engineer, DBA, On-call
- Rule: Threshold, `for:`, Severity, Runbook

### ประโยชน์
- ลดความสับสน
- ลดเวลาตรวจพบและแก้ไข
- ติดตามสถานะและเจ้าของเหตุการณ์ได้

---

# 9. Template พร้อมใช้งานจริง

## 9.1 Prometheus Config

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - /etc/prometheus/rules/*.yml

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['localhost:9093']

scrape_configs:
  - job_name: prometheus
    static_configs:
      - targets: ['localhost:9090']

  - job_name: node
    static_configs:
      - targets: ['pg1:9100', 'pg2:9100', 'infra:9100']

  - job_name: postgres
    static_configs:
      - targets: ['pg1:9187', 'pg2:9187']

  - job_name: patroni
    static_configs:
      - targets: ['pg1:8008', 'pg2:8008']
```

## 9.2 Alertmanager Config

```yaml
global:
  smtp_smarthost: 'localhost:1025'
  smtp_from: 'alertmanager@gridcare.lab'
  smtp_require_tls: false

route:
  receiver: dba-email
  group_by: ['alertname', 'instance']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h

receivers:
  - name: dba-email
    email_configs:
      - to: 'dba-oncall@gridcare.lab'
        send_resolved: true
```

## 9.3 PromQL ที่ใช้บ่อย

```promql
# TPS
sum by (datname) (
  rate(pg_stat_database_xact_commit{datname="gridcare"}[1m])
  + rate(pg_stat_database_xact_rollback{datname="gridcare"}[1m])
)

# Connections ตามสถานะ
sum by (state) (pg_stat_activity_count{datname="gridcare"})

# Cache hit ratio
rate(pg_stat_database_blks_hit{datname="gridcare"}[5m])
/
(
  rate(pg_stat_database_blks_hit{datname="gridcare"}[5m])
  + rate(pg_stat_database_blks_read{datname="gridcare"}[5m])
)

# XID Age
pg_database_wraparound_age_datfrozenxid_seconds

# Replication Lag
max by (instance, application_name) (pg_stat_replication_pg_wal_lsn_diff)
```

---

# 10. KPI / SMART / RCA / PSR

## 10.1 KPI ตัวอย่าง

| KPI | เป้าหมายตัวอย่าง | เครื่องมือ |
|---|---|---|
| Availability | ≥ 99.9% | Prometheus + Grafana |
| RTO | ≤ 30 นาที | Restore Test / Failover Test |
| RPO | ≤ 5 นาที | pgBackRest / WAL Archive |
| Cache Hit Ratio | ≥ 99% | postgres_exporter |
| Connection Usage | < 80% | Prometheus |
| Replication Lag | < 10 MB หรือ < 5s | pg_stat_replication |
| Backup Success | 100% | pgBackRest + textfile metrics |
| Alert MTTA | ≤ 5 นาที | Alertmanager + Incident Log |
| Alert MTTR | ≤ 30 นาที | Incident Log |
| Invalid Index | 0 | weekly report |

## 10.2 SMART

| องค์ประกอบ | ตัวอย่าง |
|---|---|
| Specific | ลด RTO ของ PostgreSQL Primary Failover |
| Measurable | วัดด้วย probe.sh และ pg_stat_replication |
| Achievable | เป้าหมาย ≤ 45 วินาที จากค่าจริง 31 วินาที |
| Relevant | ลดผลกระทบต่อระบบชำระค่าไฟ |
| Time-bound | ภายใน 30 วันหลังอบรม |

## 10.3 RCA
ขั้นตอน:
1. ระบุอาการและเวลา
2. รวบรวมหลักฐาน: Log, Metric, Alert, Change
3. หา Timeline
4. ระบุ Root Cause
5. ระบุ Contributing Factors
6. กำหนด Preventive Action
7. ติดตามผล

## 10.4 PSR / Postmortem
หลักการ:
- Blameless
- เน้นระบบและขั้นตอน
- มี Action Item ที่วัดได้
- มีเจ้าของและกำหนดเวลา
- เผยแพร่ให้ทีมเรียนรู้

---

# 11. สรุปหนังสือ

## ประโยชน์ที่ได้รับ
- ได้มาตรฐานการใช้งาน PostgreSQL Production
- มี Monitoring และ Alert ที่ actionable
- ลดเวลา detect และ recover
- มี Workflow และ Runbook ที่ทีมใช้ร่วมกัน

## ข้อดี
- ครอบคลุมตั้งแต่ติดตั้งถึง Game Day
- มี Template จริง
- เชื่อมโยง PostgreSQL กับ Prometheus/Alertmanager

## ข้อเสีย
- ต้องปรับค่าตามสภาพแวดล้อมจริง
- ต้องฝึกซ้อมและทบทวนสม่ำเสมอ
- Alert ที่ไม่ดูแลจะกลายเป็นภาระ

## ข้อควรระวัง
- วัดก่อนปรับทุกครั้ง
- ตรวจ `pg_file_settings`, `pg_hba_file_rules` ก่อน reload
- ตรวจ `indisvalid` หลังสร้าง Index
- ต้องมี Backup ที่ restore ได้จริง
- ต้องมี Runbook ทุก Alert

## ข้อห้าม
- ห้ามทดลองกับ Production โดยไม่มีแผน
- ห้ามใช้ Superuser กับแอป
- ห้ามลบ Backup/Index โดยไม่ตรวจสอบ
- ห้าม PITR โดยไม่มีผู้อนุมัติ
- ห้ามปิด Alert โดยไม่บันทึกเหตุผล

## ตัวอย่างตัวเลขจากหลักสูตร 5 วัน
| ตัวชี้วัด | ค่าที่วัดได้ |
|---|---|
| PgBouncer | 57 → 93 tps |
| หลัง Optimize | 93 → 149 tps |
| PITR RTO | 8 นาที 32 วินาที |
| Failover RTO | 31 วินาที |
| RPO | 0 |
| Switchover | 3 วินาที |
| pg_upgrade | 2 วินาที |
| PK Swap | 0.13 วินาที |

---

# 12. ข้อเสนอการดำเนินการต่อ

ฉบับนี้เป็น **โครงเล่ม 120 บท + ตัวอย่างบท + Template พร้อมใช้**  
ขั้นตอนถัดไปสามารถทำได้ดังนี้:

1. เขียนบทที่ 2–10 ฉบับเต็ม  
2. เขียนส่วน Observability บทที่ 41–50 ก่อน เพราะเป็นหัวใจของ Prometheus  
3. เขียนส่วน Alerting บทที่ 51–60 พร้อม Template และแบบฝึกหัด  
4. รวมเป็นไฟล์ Markdown/PDF/DOCX ตามรูปแบบหนังสือ  
5. เพิ่มรูป Diagram, ตาราง Cheatsheet และเฉลยแบบฝึกหัดท้ายบท

หากต้องการให้ดำเนินการต่อ ให้ระบุลำดับบทที่ต้องการ เช่น  
**“เขียนบทที่ 2–5 ฉบับเต็ม”** หรือ **“เขียนส่วน Observability บทที่ 41–50”**