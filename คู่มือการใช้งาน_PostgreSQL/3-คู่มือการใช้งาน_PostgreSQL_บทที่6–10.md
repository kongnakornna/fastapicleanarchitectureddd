# บทที่ 6–10

> หนังสือ: คู่มือการใช้งาน PostgreSQL สำหรับ DevOps Engineer, Cloud Engineer และ DBA  
> ส่วนที่ 1 ปฐมบทและสถาปัตยกรรม  
> โทน: ทางการ กระชับ เน้นใช้งานจริง

---

# บทที่ 6 Prometheus: สถาปัตยกรรมและ Time-Series

## 1. เรื่อง
สถาปัตยกรรมของ Prometheus ในฐานะระบบจัดเก็บข้อมูลแบบ Time-Series Database (TSDB) และเครื่องมือดึงข้อมูลตัวชี้วัด (Metrics) สำหรับงาน PostgreSQL Production

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจว่าทำไม Prometheus เหมาะกับงาน Observability ของ PostgreSQL  
2. เพื่อให้เข้าใจ Pull Model, Scrape, Exporter และ TSDB  
3. เพื่อให้วางแผน Retention, Storage และ Cardinality ได้  
4. เพื่อให้ผู้อ่านเลือกใช้ Prometheus ร่วมกับ Alertmanager และ Grafana ได้ถูกต้อง

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- อธิบายสถาปัตยกรรม Prometheus ได้ครบ 5 องค์ประกอบ
- เขียน `prometheus.yml` สำหรับ PostgreSQL ได้
- อธิบายความหมายของ Time-Series, Labels, Samples, Series ได้
- เลือก Cardinality ที่เหมาะสมและหลีกเลี่ยง High Cardinality
- เลือก PromQL พื้นฐานได้

## 4. เนื้อหาโดยย่อ
Prometheus คือระบบ **Pull-based Metrics Collector** และ **Time-Series Database**  
ทำหน้าที่:
- **Scrape** Metric จาก Target (Exporter) ทุก `scrape_interval`
- **จัดเก็บ** ข้อมูลเป็น Sample ที่มี Timestamp
- **Query** ด้วย PromQL
- **Evaluate** Alert Rule
- **ส่ง Alert** ให้ Alertmanager

Prometheus ไม่ใช่ Log Store หรือ Trace Store และไม่ใช่ที่เก็บ Metric ที่มี Label Cardinality สูงมากในระยะยาว

## 5. ประโยชน์ที่ได้รับ
- เข้าใจว่าทำไม Prometheus ไม่เก็บทุกอย่าง และจะเลือก Metric อย่างไร
- ออกแบบ `scrape_config` สำหรับ PostgreSQL ได้ถูกต้อง
- วางแผน Storage และ Retention ได้
- หลีกเลี่ยง High Cardinality ที่ทำให้ Prometheus ล่ม
- ใช้ PromQL ได้ตรงกับข้อมูลที่เป็น Counter และ Gauge

## 6. ข้อควรระวัง
- **High Cardinality** เช่น Label จาก `query`, `user_id`, `customer_id` ทำให้ Storage บวมและ Query ช้า  
- ** scrape_interval สั้นเกินไป** เช่น 1s ทำให้ Load ระบบและ Storage สูงเกินจำเป็น  
- **`rate()` ใช้กับ Counter เท่านั้น** ไม่ใช่ Gauge  
- **Alert `for: 0s`** ทำให้เกิด False Positive บ่อย  
- **Retention สั้นเกินไป** ทำให้ไม่สามารถวิเคราะห์เชิงประวัติได้

## 7. ข้อดี
- Pull Model ทำให้ควบคุม Load ได้จากฝั่ง Prometheus  
- PromQL ยืดหยุ่นสูง  
- มี Exporter สำเร็จรูปจำนวนมาก  
- ใช้งานร่วมกับ Alertmanager และ Grafana ได้โดยตรง  
- Open Source และมี Community ขนาดใหญ่

## 8. ข้อเสีย
- ไม่เหมาะกับข้อมูล Cardinality สูงมาก  
- ไม่เก็บ Log หรือ Trace  
- Long-term Storage ต้องพึ่งระบบเสริม เช่น Thanos, Mimir, VictoriaMetrics  
- Pull Model ต้องเข้าถึง Target ได้ฝั่ง Network

## 9. ข้อห้าม
- ห้ามใช้ Label จากค่าที่ไม่จำกัด เช่น `query_id` แบบดิบ หรือ `session_id`  
- ห้ามตั้ง `scrape_interval: 1s` สำหรับงาน Production ทั่วไป  
- ห้ามใช้ `sum()` โดยไม่มี `by()` เมื่อต้องการแยกตามมิติ  
- ห้ามใช้ Gauge กับ `rate()`  
- ห้ามใช้ Prometheus เป็นที่เก็บ Log

## 10. รายละเอียด

### 10.1 สถาปัตยกรรม Prometheus

```text
┌──────────────────────────────────────────────┐
│                Prometheus Server              │
│                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌───────┐ │
│  │  Retrieval  │  │   TSDB      │  │ HTTP  │ │
│  │  (Scraper)  │  │  (Storage)  │  │  API  │ │
│  └──────┬──────┘  └──────┬──────┘  └───┬───┘ │
│         │                │             │     │
│  ┌──────▼──────┐  ┌──────▼──────┐  ┌───▼───┐ │
│  │ Alert Rule  │  │  PromQL     │  │Grafana│ │
│  │ Evaluation  │  │  Engine     │  │ Dash  │ │
│  └──────┬──────┘  └─────────────┘  └───────┘ │
│         │                                    │
└─────────┼────────────────────────────────────┘
          ▼
   Alertmanager
```

### 10.2 องค์ประกอบหลัก 5 ส่วน

| องค์ประกอบ | หน้าที่ |
|---|---|
| Retrieval (Scraper) | ไปดึง Metric จาก Target ตาม `scrape_interval` |
| TSDB | เก็บ Sample เป็น Time-Series พร้อม Timestamp |
| PromQL Engine | Query ข้อมูลตามภาษา PromQL |
| Alert Rule Evaluation | ประเมิน Rule ตาม `evaluation_interval` |
| HTTP API | ให้ Grafana หรือระบบอื่น Query |

### 10.3 Data Model: Time-Series

**Series** = Metric Name + Labels  
**Sample** = (Value, Timestamp)  
**Metric** = ชุดของ Sample ที่เกิดต่อเนื่องตามเวลา

ตัวอย่าง:
```text
pg_stat_database_xact_commit{instance="pg1:9187", datname="gridcare"} 1234 @ 1730702112
pg_stat_database_xact_commit{instance="pg1:9187", datname="gridcare"} 1236 @ 1730702127
pg_stat_database_xact_commit{instance="pg1:9187", datname="gridcare"} 1238 @ 1730702142
```

- **Metric Name:** `pg_stat_database_xact_commit`
- **Labels:** `instance`, `datname`
- **Series:** ชุดของ Sample ที่มี Label เดียวกันตลอด

### 10.4 ประเภท Metric

| ประเภท | ลักษณะ | ตัวอย่าง | การใช้งาน |
|---|---|---|---|
| Counter | เพิ่มขึ้นเท่านั้น | `pg_stat_database_xact_commit` | `rate()`, `increase()` |
| Gauge | ขึ้น-ลงได้ | `pg_up`, `pg_stat_activity_count` | ใช้ค่าตรง |
| Histogram | แจกแจงแบบ Bucket | `pg_stat_statements_mean_exec_time_seconds` | `histogram_quantile()` |
| Summary | Quantile คำนวณฝั่ง Target | `pg_stat_statements_seconds` | ใช้น้อยกว่า Histogram |

### 10.5 Pull vs Push

| มิติ | Pull (Prometheus) | Push |
|---|---|---|
| ทิศทาง | Prometheus ไปดึง | Target ส่งไป |
| การควบคุม | จาก Prometheus | จาก Target |
| Health Check | รู้ทันทีถ้า Target Down | ต้องสร้าง Heartbeat |
| Firewall | ต้องเปิดให้ Prometheus เข้า Target | เปิดให้ Target ออก |

### 10.6 Cardinality

**Cardinality** = จำนวน Series ที่ไม่ซ้ำกัน  
สูตรประมาณ: `จำนวน Metric × จำนวน Label × จำนวน Value ที่ไม่ซ้ำ`

**ตัวอย่างที่ดี:**
```text
pg_stat_database_xact_commit{instance="pg1:9187", datname="gridcare"}
pg_stat_database_xact_commit{instance="pg1:9187", datname="postgres"}
pg_stat_database_xact_commit{instance="pg1:9187", datname="template1"}
```
→ Cardinality ต่ำ ควบคุมได้

**ตัวอย่างที่แย่:**
```text
pg_stat_statements_seconds_total{query="SELECT * FROM customers WHERE id=1"}
pg_stat_statements_seconds_total{query="SELECT * FROM customers WHERE id=2"}
pg_stat_statements_seconds_total{query="SELECT * FROM customers WHERE id=3"}
```
→ Cardinality สูงมาก ไม่ควรทำ

**วิธีแก้:** ใช้ `queryid` แทน `query` ที่เป็น String ดิบ

### 10.7 `prometheus.yml` ตัวอย่างสมบูรณ์

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: gridcare
    env: production

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

### 10.8 Retention และ Storage

| ค่า | ค่าแนะนำสำหรับ Production ทั่วไป |
|---|---|
| `--storage.tsdb.retention.time` | 15d–30d |
| `--storage.tsdb.retention.size` | ตาม Capacity ของ Disk |
| `scrape_interval` | 15s–30s |
| `evaluation_interval` | 15s–30s |

> 💡 Storage โดยประมาณ = `Series × Sample size × Retention`  
> Sample size ~1.7 bytes (จริงขึ้นกับ Compression)

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: ตรวจสอบ Target ใน Prometheus

```bash
curl -s localhost:9090/api/v1/targets | python3 -m json.tool | grep -E '"scrapeUrl"|"health"'
```

ผลลัพธ์:
```text
"scrapeUrl": "http://localhost:9090/metrics",
"health": "up"
"scrapeUrl": "http://pg1:9100/metrics",
"health": "up"
"scrapeUrl": "http://pg1:9187/metrics",
"health": "up"
```

### ตัวอย่างที่ 2: Query Metric ด้วย PromQL

```bash
curl -s 'localhost:9090/api/v1/query?query=pg_up' | python3 -m json.tool
```

ผลลัพธ์:
```json
{
  "status": "success",
  "data": {
    "resultType": "vector",
    "result": [
      {
        "metric": {"instance": "pg1:9187", "job": "postgres"},
        "value": [1730702112.345, "1"]
      }
    ]
  }
}
```

### ตัวอย่างที่ 3: `promtool` ตรวจ Config

```bash
promtool check config /etc/prometheus/prometheus.yml
```

ผลลัพธ์:
```text
Checking /etc/prometheus/prometheus.yml
  SUCCESS: 5 scrape configs found
```

### ตัวอย่างที่ 4: คำนวณ Series Cardinality

```promql
count({__name__=~"pg_.*"})
```

ผลลัพธ์:
```text
{ } → 4521
```

### ตัวอย่างที่ 5: ตรวจ Retention และ Storage

```bash
promtool tsdb list /var/lib/prometheus
```

ผลลัพธ์:
```text
BLOCKULID              MIN TIME              MAX TIME              DURATION     NUM SAMPLES  NUM CHUNKS  NUM SERIES  SIZE
01HQZ8XXXX             2026-10-20T00:00:00Z  2026-10-21T00:00:00Z  24h          1234567      5678        4521        120 MB
...
```

## 12. สรุปย่อ จำง่าย
- **Prometheus = Pull + TSDB + PromQL + Alert Evaluation**  
- **Series = Metric + Labels**  
- **Counter ใช้ `rate()` / Gauge ใช้ค่าตรง**  
- **Cardinality สูง = อันตราย** ให้ใช้ `queryid` ไม่ใช่ `query`  
- ** scrape_interval 15s–30s** เพียงพอสำหรับงาน Production ทั่วไป  
- **Retention 15d–30d** เพียงพอและประหยัด Storage

ประโยคจำ: **“Prometheus ไม่ใช่ที่เก็บทุกอย่าง Prometheus เก็บเฉพาะสิ่งที่ตอบคำถามได้”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- Prometheus Documentation — Overview: https://prometheus.io/docs/introduction/overview/
- Prometheus Documentation — Storage: https://prometheus.io/docs/prometheus/latest/storage/
- Prometheus Documentation — Data Model: https://prometheus.io/docs/concepts/data_model/
- Prometheus Documentation — PromQL Basics: https://prometheus.io/docs/prometheus/latest/querying/basics/
- GridCare Workshop Day 2: Lab 3.1 (Prometheus Config), Day 4: Lab 4.1 (Rule และ Alertmanager)

---

# บทที่ 7 Alertmanager: บทบาทและการแจ้งเตือน

## 1. เรื่อง
บทบาทของ Alertmanager ในระบบ Monitoring และหลักการออกแบบการแจ้งเตือนให้ actionable

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจบทบาทของ Alertmanager ในระบบ Observability  
2. เพื่อให้เข้าใจ Grouping, Routing, Inhibition และ Silencing  
3. เพื่อให้ตั้งค่า Email/Slack/Webhook ได้  
4. เพื่อให้ลด Alert Fatigue และเพิ่มคุณภาพการแจ้งเตือน

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- อธิบาย Pipeline ของ Alert ตั้งแต่ Prometheus ถึงช่องทางแจ้งเตือน  
- เขียน `alertmanager.yml` สำหรับ Production ได้  
- เลือกใช้ Grouping, Routing และ Inhibition ได้ถูกต้อง  
- ทดสอบ Alert ด้วย Mailpit หรือ Webhook ได้  
- เชื่อม Alert กับ Runbook และ On-call Rotation ได้

## 4. เนื้อหาโดยย่อ
**Alertmanager** เป็นระบบแยกจาก Prometheus ทำหน้าที่รับ Alert จาก Prometheus และจัดการ:
- **Grouping** — รวม Alert ที่เหมือนกันเป็นกลุ่ม  
- **Routing** — ส่งไปยัง Receiver ที่ถูกต้อง  
- **Inhibition** — ยับยั้ง Alert ที่ไม่จำเป็นเมื่อมี Alert ที่รุนแรงกว่าดังอยู่  
- **Silencing** — ปิด Alert ชั่วคราวตามช่วงเวลา  
- **Receivers** — Email, Slack, Webhook, Pager, SMS

## 5. ประโยชน์ที่ได้รับ
- ลดจำนวน Alert ที่ส่งเข้าช่องทางคน  
- ทำให้ Alert ที่สำคัญไปถึงคนที่ถูกต้องทันที  
- ลด False Positive ด้วย Inhibition  
- ทำให้สามารถ Silence Alert ระหว่าง Maintenance ได้  
- ทำให้ On-call Rotation ทำงานได้จริง

## 6. ข้อควรระวัง
- **Grouping ที่กว้างเกินไป** ทำให้ Alert ที่ไม่เกี่ยวข้องถูกรวมเข้าด้วยกัน  
- **Routing ที่ไม่มี Fallback** ทำให้ Alert ตกหล่น  
- **Inhibition ที่ผิด** อาจยับยั้ง Critical Alert ที่ควรดัง  
- **Silence ที่ลืมลบ** ทำให้ Alert ไม่ดังในอนาคต  
- **`repeat_interval` สั้นเกินไป** ทำให้ส่งซ้ำรบกวน

## 7. ข้อดี
- แยก Concern ระหว่าง Detection (Prometheus) และ Notification (Alertmanager)  
- มี Deduplication และ Grouping ในตัว  
- ยืดหยุ่นสูงผ่าน YAML  
- รองรับ Receiver หลายประเภท

## 8. ข้อเสีย
- YAML ซับซ้อน ต้องใช้ `amtool` ตรวจสอบ  
- Inhibition ต้องออกแบบให้ดี มิฉะนั้นอาจปิด Alert ที่สำคัญ  
- ไม่มี UI สำหรับจัดการ On-call Rotation (ต้องใช้ PagerDuty หรือ Grafana OnCall)  
- ส่ง Alert แบบ Fire-and-Forget — ไม่มี Ack ในตัว

## 9. ข้อห้าม
- ห้ามส่งทุก Alert ไปช่องทางเดียว  
- ห้ามตั้ง `repeat_interval: 1m` สำหรับ Alert ที่รุนแรง  
- ห้ามใช้ Silence โดยไม่ระบุวันสิ้นสุด  
- ห้าม Inhibition ที่ทำให้ Critical ถูกกลบด้วย Warning  
- ห้ามใช้ Alertmanager เป็นที่เก็บ Audit

## 10. รายละเอียด

### 10.1 Pipeline ของ Alert

```text
Metric (Prometheus)
   │
   ▼
Alert Rule (expr + for + labels)
   │
   ▼
Pending (ยังไม่แจ้ง)
   │ (ครบ for:)
   ▼
Firing
   │
   ▼ (ส่งทุก evaluation_interval)
Alertmanager
   │
   ├── Grouping
   ├── Routing
   ├── Inhibition
   ├── Silencing
   ▼
Receiver (Email, Slack, Webhook, Pager)
```

### 10.2 หลักการของแต่ละฟีเจอร์

| ฟีเจอร์ | หน้าที่ | ตัวอย่าง |
|---|---|---|
| Grouping | รวม Alert เป็นกลุ่มเดียว | `group_by: ['alertname', 'instance']` |
| Routing | ส่งตาม Label | severity=critical → pager |
| Inhibition | ยับยั้งถ้ามี Alert ที่แรงกว่า | `PostgresDown` ยับยั้ง `PostgresConnectionsHigh` |
| Silencing | ปิดชั่วคราว | ระหว่าง Maintenance |
| Receivers | ปลายทาง | email_configs, slack_configs, webhook_configs |

### 10.3 ตัวอย่าง `alertmanager.yml` สำหรับ Production

```yaml
global:
  smtp_smarthost: 'localhost:1025'
  smtp_from: 'alertmanager@gridcare.lab'
  smtp_require_tls: false
  resolve_timeout: 5m

route:
  receiver: default-email
  group_by: ['alertname', 'cluster', 'instance']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  routes:
    - match:
        severity: critical
      receiver: pager-critical
      group_wait: 10s
      repeat_interval: 30m
    - match:
        severity: warning
      receiver: dba-email
      repeat_interval: 2h
    - match:
        severity: info
      receiver: log-only

inhibit_rules:
  - source_match:
      alertname: PostgresDown
    target_match_re:
      alertname: Postgres.*
    equal: ['instance']

receivers:
  - name: default-email
    email_configs:
      - to: 'dba-oncall@gridcare.lab'
        send_resolved: true

  - name: dba-email
    email_configs:
      - to: 'dba-oncall@gridcare.lab'
        send_resolved: true

  - name: pager-critical
    email_configs:
      - to: 'pager@gridcare.lab'
    webhook_configs:
      - url: 'http://pagerduty.local/api/alert'
        send_resolved: true

  - name: log-only
    webhook_configs:
      - url: 'http://logs.local/alert'
        send_resolved: false
```

### 10.4 การทดสอบ Config

```bash
amtool check-config /etc/prometheus/alertmanager.yml
```

ผลลัพธ์:
```text
Checking '/etc/prometheus/alertmanager.yml'  SUCCESS
Found:
 - global config
 - route
 - 1 inhibit rules
 - 4 receivers
 - 0 templates
```

### 10.5 หลักการ Group

- `group_by: ['alertname', 'instance']` — เหมาะกับ Alert ที่มาเป็นคู่  
- `group_by: ['cluster']` — เหมาะกับการดูภาพรวม  
- `group_wait: 30s` — รอให้ Alert ที่เกิดพร้อมกันรวมกลุ่ม  
- `group_interval: 5m` — รอส่งกลุ่มถัดไป  
- `repeat_interval: 4h` — ส่งซ้ำถ้าไม่ Resolve

### 10.6 Mailpit สำหรับทดสอบ Email

```bash
# ตั้งค่า SMTP ของ Alertmanager ชี้ไปที่ Mailpit
smtp_smarthost: 'localhost:1025'
```

ทดสอบด้วย `amtool`:
```bash
amtool alert add alertname=TestAlert severity=warning
```

ตรวจอีเมลที่ Mailpit: `http://localhost:18025`

### 10.7 KPI ของ Alert

| KPI | ค่าเป้าหมาย |
|---|---|
| MTTA (Mean Time To Acknowledge) | ≤ 5 นาที |
| MTTR (Mean Time To Resolve) | ≤ 30 นาที |
| False Positive Rate | ≤ 10% |
| Alert ที่ไม่มี Runbook | 0 |
| Alert ที่ไม่มีเจ้าของ | 0 |
| Alert ที่ Silence เกิน 7 วัน | 0 |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Alert ถูกส่งไป Email

```bash
# ทดสอบ
amtool alert add alertname=PostgresDown severity=critical instance="pg1:9187" summary="PostgreSQL down"
```

ผลลัพธ์ใน Mailpit: เห็นอีเมล `[FIRING:1] PostgresDown (pg1:9187)`

### ตัวอย่างที่ 2: Query Alert ปัจจุบัน

```bash
amtool alert query --alertmanager.url=http://localhost:9093
```

ผลลัพธ์:
```text
Alertname              Starts At                Summary
PostgresRecentlyRestarted 2026-11-05 13:16:00 UTC  PostgreSQL instance pg2:9187 restarted recently
```

### ตัวอย่างที่ 3: Silence Alert ระหว่าง Maintenance

```bash
amtool silence add alertname="Postgres.*" instance="pg1:9187" \
  --duration=2h \
  --comment="Maintenance: upgrade PostgreSQL 17→18" \
  --alertmanager.url=http://localhost:9093
```

ผลลัพธ์:
```text
a3b1c2d4-e5f6-7890-abcd-ef1234567890
```

### ตัวอย่างที่ 4: ตรวจสอบว่า Alert ถูก Inhibition หรือไม่

ใน UI ของ Alertmanager: `http://localhost:9093/#/alerts`  
จะเห็น Alert ที่มี Status = **suppressed** พร้อมระบุ Inhibited By

### ตัวอย่างที่ 5: ตรวจสอบ Configuration ด้วย `amtool`

```bash
amtool config routes show --alertmanager.url=http://localhost:9093
```

ผลลัพธ์:
```text
Routing tree:
├── default-email
├── severity=critical → pager-critical
├── severity=warning → dba-email
└── severity=info → log-only
```

## 12. สรุปย่อ จำง่าย
- **Alertmanager = Router + Grouper + Silencer + Inhibitor**  
- **Prometheus ตรวจ, Alertmanager แจ้ง**  
- **Grouping** รวม, **Routing** แยก, **Inhibition** ยับยั้ง, **Silencing** ปิดชั่วคราว  
- **ทุก Alert ต้องมี Severity, Summary, Runbook**  
- **ทุก Receiver ต้องมี Fallback**  
- **ทุก Silence ต้องมีวันสิ้นสุด**

ประโยคจำ: **“Prometheus ถามว่าเป็นอะไร Alertmanager ถามว่าใครต้องรู้”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- Alertmanager Documentation: https://prometheus.io/docs/alerting/latest/alertmanager/
- Alertmanager Configuration: https://prometheus.io/docs/alerting/latest/configuration/
- `amtool` Documentation: https://github.com/prometheus/alertmanager#amtool
- GridCare Workshop Day 4: Lab 4.1 (Alertmanager + Mailpit)
- Mailpit: https://mailpit.axllent.org/

---

# บทที่ 8 การออกแบบระบบแจ้งเตือนที่มีประสิทธิภาพ

## 1. เรื่อง
หลักการออกแบบ Alert ที่ actionable ไม่รบกวน และเชื่อมโยงกับ Runbook และ On-call Process

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้ผู้อ่านออกแบบ Alert ที่ตอบคำถาม “ต้องทำอะไร” ได้ทันที  
2. เพื่อลด Alert Fatigue และ False Positive  
3. เพื่อให้ทุก Alert มี Severity, Runbook และเจ้าของ  
4. เพื่อให้เชื่อม Alert กับ On-call Rotation และ Incident Process

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ออกแบบ Alert Rule ที่ actionable  
- กำหนด Severity ได้ถูกต้อง  
- เขียน `summary`, `description`, `runbook_url` ที่มีประโยชน์  
- ทดสอบ Alert Rule ด้วย `promtool test rules`  
- วัดคุณภาพ Alert ด้วย KPI

## 4. เนื้อหาโดยย่อ
Alert ที่ดีต้อง **Actionable**, **Timely**, **Specific** และ **Owned**  
หลักการออกแบบ 7 ข้อ:
1. บอกอาการ ไม่ใช่บอกทุก Metric  
2. มี Severity ที่ชัดเจน  
3. มี `for:` ที่เหมาะสม  
4. มี `summary` + `description` + `runbook_url`  
5. มีเจ้าของและช่องทางแจ้ง  
6. ผ่าน `promtool check rules` และ `promtool test rules`  
7. ทบทวนหลังเกิดเหตุ (PSR) เพื่อลด Alert ที่ไม่ actionable

## 5. ประโยชน์ที่ได้รับ
- ลด Alert ที่รบกวนตอนกลางคืน  
- ลดเวลา MTTA และ MTTR  
- ทำให้ On-call Rotation มีคุณภาพ  
- ทำให้ทุก Alert มี Runbook ทำให้ตอบสนองเร็ว  
- ทำให้เกิด Continuous Improvement

## 6. ข้อควรระวัง
- **Alert ที่ไม่มี Runbook** ทำให้คนตอบสนองตัดสินใจช้า  
- **Severity ที่ไม่ชัด** ทำให้ Critical ถูกกลบด้วย Warning  
- **Alert ที่ดังซ้ำโดยไม่มีอะไรเปลี่ยน** ทำให้ทีมละเลย  
- **Alert ที่ผูกกับ Threshold คงที่** ไม่เหมาะกับระบบที่ Load เปลี่ยน  
- **Alert ที่ไม่มี `for:`** ทำให้เกิด False Positive

## 7. ข้อดี
- ลด Alert Fatigue  
- ทำให้ On-call ได้รับข้อมูลครบ  
- ทำให้ PSR มีข้อมูลคุณภาพ  
- ทำให้ทีมเรียนรู้จาก Alert ที่ดี

## 8. ข้อเสีย
- ต้องลงทุนเวลาออกแบบและทดสอบ  
- ต้องทบทวนเป็นระยะ  
- ต้องมีคนรับผิดชอบ Alert ทุกตัว

## 9. ข้อห้าม
- ห้าม Alert ที่ไม่มี Severity  
- ห้าม Alert ที่ไม่มี Runbook URL  
- ห้าม Alert ที่ไม่มีเจ้าของ  
- ห้าม Alert ที่ไม่ actionable (เช่น “CPU สูง” โดยไม่มีเกณฑ์)  
- ห้ามใช้ Alert เป็น Log

## 10. รายละเอียด

### 10.1 4 เกณฑ์ของ Alert ที่ดี

| เกณฑ์ | ความหมาย | ตัวอย่าง |
|---|---|---|
| Actionable | มีสิ่งที่ต้องทำ | `PostgresDown` → เปิด Runbook C08 |
| Timely | มาตรงเวลา | `for: 1m` ไม่ดังช้าเกินไป |
| Specific | เจาะจง | `instance="pg1:9187"` ไม่ใช่ “ทุกอย่าง” |
| Owned | มีเจ้าของ | DBA เป็น Primary, DevOps Secondary |

### 10.2 Severity

| Severity | เกณฑ์ | ช่องทาง | ตัวอย่าง |
|---|---|---|---|
| Critical | กระทบผู้ใช้หรือข้อมูล | Pager + Email + Slack | `PostgresDown`, `PatroniPrimaryCountNotOne`, `DiskFull` |
| Warning | เสี่ยงจะเกิดปัญหา | Slack + Email | `PostgresConnectionsHigh`, `ReplicationLagHigh` |
| Info | บันทึกเหตุการณ์ | Log Only | `PostgresRecentlyRestarted`, `BackupSuccess` |

### 10.3 โครงสร้าง Annotation

```yaml
annotations:
  summary: "คลัสเตอร์ {{ $labels.scope }} มี Primary {{ $value }} ตัว"
  description: "0 = ไม่มีโหนดใดรับเขียน, 2 = เสี่ยง Split-Brain ตรวจด้วย patronictl list"
  runbook_url: "http://gridcare-infra/runbooks/C08-replication-lag-slot-failover.md"
```

- **summary** — บอกอาการสั้น ๆ  
- **description** — บอกบริบทและสิ่งที่ต้องทำ  
- **runbook_url** — บอกขั้นตอนแก้ไข

### 10.4 `for:` ที่เหมาะสม

| กลุ่ม | `for:` แนะนำ |
|---|---|
| Down | 1m |
| Connection High | 5m |
| Replication Lag | 1m–3m |
| Backup Old | 1h |
| XID Age Warning | 15m |
| Disk Fill Predicted | 30m |
| Restart Event | 0s (Info) |

### 10.5 ตัวอย่าง Alert Rule ที่ดี

```yaml
groups:
  - name: gridcare-postgres
    rules:
      - alert: PostgresDown
        expr: pg_up == 0
        for: 1m
        labels:
          severity: critical
          owner: dba
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
          owner: dba
        annotations:
          summary: "Connection ใช้งานเกิน 80%"
          description: "ตรวจ PgBouncer, session ค้าง และ idle in transaction"
          runbook_url: "http://gridcare-infra/runbooks/C03-connection-limit-locking.md"

      - alert: PostgresRecentlyRestarted
        expr: time() - pg_postmaster_start_time_seconds < 300
        for: 0s
        labels:
          severity: info
          owner: dba
        annotations:
          summary: "PostgreSQL instance {{ $labels.instance }} just restarted"
          description: "ตรวจ log ล่าสุด, patronictl list และ event ล่าสุด"
          runbook_url: "http://gridcare-infra/runbooks/C08-postgres-down.md"
```

### 10.6 การทดสอบ Alert ด้วย `promtool test rules`

**ไฟล์ทดสอบ:**
```yaml
rule_files:
  - /etc/prometheus/rules/gridcare-ha-alerts.yml
evaluation_interval: 1m
tests:
  - interval: 1m
    input_series:
      - series: 'patroni_primary{job="patroni",instance="pg1:8008",scope="gridcare",name="pg1"}'
        values: '1x10'
      - series: 'patroni_primary{job="patroni",instance="pg2:8008",scope="gridcare",name="pg2"}'
        values: '0 0 0 1x7'
    alert_rule_test:
      - eval_time: 2m
        alertname: PatroniPrimaryCountNotOne
        exp_alerts: []
      - eval_time: 5m
        alertname: PatroniPrimaryCountNotOne
        exp_alerts:
          - exp_labels: {severity: critical, scope: gridcare}
            exp_annotations:
              summary: "คลัสเตอร์ gridcare มี Primary 2 ตัว"
```

**รัน:**
```bash
promtool test rules ~/gridcare-ha-alerts.test.yml
```

ผลลัพธ์:
```text
Unit Testing:  /home/student/gridcare-ha-alerts.test.yml
  SUCCESS
```

### 10.7 KPI ของ Alert System

| KPI | เป้าหมาย |
|---|---|
| % Alert ที่มี Runbook | 100% |
| % Alert ที่มีเจ้าของ | 100% |
| False Positive Rate | ≤ 10% |
| MTTA | ≤ 5 นาที |
| MTTR | ≤ 30 นาที |
| Alert ที่ Silence เกิน 7 วัน | 0 |
| Alert ที่ไม่เคย Reviewed 90 วัน | 0 |

### 10.8 Alert Review Process

```text
ทุกเดือน:
  1. Export Alert ทั้งหมดจาก Prometheus
  2. ทบทวน Alert ที่ Firing บ่อย
  3. ตรวจ Alert ที่ไม่มี Runbook
  4. ตรวจ Alert ที่ไม่มีเจ้าของ
  5. ตรวจ Alert ที่ Silence ค้าง
  6. ปรับ Threshold หรือ `for:`
  7. อัปเดต Runbook
```

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Alert ที่ไม่ Actionable (ผิด)

```yaml
- alert: HighCPU
  expr: node_cpu_seconds_total{mode="idle"} < 0.2
  labels:
    severity: critical
  annotations:
    summary: "CPU สูง"
```

> ⚠️ ไม่ actionable, ไม่มี `for:`, ไม่มี Runbook, ไม่มีบริบท

### ตัวอย่างที่ 2: Alert ที่ Actionable (ถูก)

```yaml
- alert: PostgreSQLHighCPU
  expr: |
    100 - avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100 > 80
  for: 10m
  labels:
    severity: warning
    owner: dba
  annotations:
    summary: "CPU ของ {{ $labels.instance }} สูงเกิน 80%"
    description: "ตรวจ pg_stat_statements Top 5, pg_stat_activity, autovacuum, pgbench"
    runbook_url: "http://gridcare-infra/runbooks/C06-oom-temp-spill.md"
```

### ตัวอย่างที่ 3: Alert ที่ทำให้เกิด Alert Fatigue (ผิด)

```yaml
- alert: PostgresWarning
  expr: pg_stat_activity_count > 0
  for: 0s
  labels:
    severity: warning
  annotations:
    summary: "มี session"
```

> ⚠️ ดังตลอดเวลา ไม่มีประโยชน์

### ตัวอย่างที่ 4: Alert ที่ใช้ `rate()` กับ Gauge (ผิด)

```yaml
- alert: BadAlert
  expr: rate(pg_up[5m]) == 0
```

> ⚠️ `pg_up` เป็น Gauge ใช้ `rate()` ไม่ได้

### ตัวอย่างที่ 5: Alert ที่ใช้ `rate()` กับ Counter (ถูก)

```yaml
- alert: PostgresXactRollbackHigh
  expr: |
    sum by (instance) (rate(pg_stat_database_xact_rollback[5m]))
    /
    sum by (instance) (
      rate(pg_stat_database_xact_commit[5m])
      + rate(pg_stat_database_xact_rollback[5m])
    ) > 0.05
  for: 10m
  labels:
    severity: warning
    owner: dba
  annotations:
    summary: "Rollback ratio สูงเกิน 5%"
    description: "ตรวจ deadlock, serialization failure, connection error"
    runbook_url: "http://gridcare-infra/runbooks/C01-lock-queue.md"
```

## 12. สรุปย่อ จำง่าย
- Alert ที่ดี = **Actionable + Timely + Specific + Owned**  
- **Severity** ต้องชัด แยก Critical / Warning / Info  
- **`for:`** ต้องเหมาะสมกับอาการ  
- **`summary` + `description` + `runbook_url`** ต้องมีทุก Alert  
- **ทดสอบด้วย `promtool test rules`** ก่อนใช้งาน  
- **ทบทวนเป็นระยะ** เพื่อลด Alert Fatigue  
- **ทุก Alert มีเจ้าของ** และ **ทุกเจ้าของมี Runbook**

ประโยคจำ: **“Alert ที่ดีทำให้คนรู้ว่าต้องทำอะไร ไม่ใช่แค่รู้ว่ามีอะไรผิดปกติ”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- Prometheus Alerting Rules: https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/
- Prometheus Unit Testing: https://prometheus.io/docs/prometheus/latest/configuration/unit_testing_rules/
- Google SRE Book — Monitoring Distributed Systems: https://sre.google/sre-book/monitoring-distributed-systems/
- Rob Ewaschuk — My Philosophy on Alerting: https://docs.google.com/document/d/199PqyG3UsyXlwieHaqbGiWVa8eMWi8zzAn0YfcApr8Q/
- GridCare Workshop Day 4: Lab 4.1, Workshop Day 4 ขั้นที่ 1 (Alert Rule ของ HA)

---

# บทที่ 9 Workflow ภาพรวม Data, Metric และ Alert

## 1. เรื่อง
Workflow องค์รวมของข้อมูลตั้งแต่ PostgreSQL ไปจนถึง Dashboard และ Alert พร้อมโครงสร้าง Diagram และ Actor ที่ชัดเจน

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เห็นภาพการไหลของข้อมูล (Data Workflow) ตั้งแต่ต้นทางถึงปลายทาง  
2. เพื่อให้เห็นการไหลของ Metric (Metric Workflow) และการไหลของ Alert (Alert Workflow)  
3. เพื่อให้แต่ละบทบาทรู้ว่าตนอยู่ในขั้นตอนใด  
4. เพื่อให้ออกแบบ Flow ที่มีจุดตรวจ (Checkpoint) และจุดยืนยัน (Confirmation)

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- วาด Data Workflow, Metric Workflow, Alert Workflow ได้  
- อธิบาย Input / Process / Storage / Output ของแต่ละ Flow  
- ระบุ Actor และ Rule ในแต่ละขั้น  
- ออกแบบ Flow ที่ลดความผิดพลาดและลดเวลาตอบสนอง

## 4. เนื้อหาโดยย่อ

### Data Workflow
คือการไหลของข้อมูลจาก Source → Process → Storage → Output  
ในหนังสือเล่มนี้ Data Workflow หมายถึง **การไหลของ Metric, Log และ Backup**

### Metric Workflow
คือการไหลของ Metric ตั้งแต่ PostgreSQL/Linux → Exporter → Prometheus → Query/Dashboard/Alert

### Alert Workflow
คือการไหลของ Alert ตั้งแต่ Metric ผิดปกติ → Alert Rule → Alertmanager → Receiver → Runbook → Incident Record → PSR

## 5. ประโยชน์ที่ได้รับ
- เห็นภาพรวมว่าปัญหาอยู่ชั้นไหน  
- ออกแบบ Flow ที่มีจุดตรวจได้  
- ทำให้แต่ละทีมรู้ว่าตนอยู่จุดใด  
- ทำให้ Runbook และ Incident Record เชื่อมกัน  
- ทำให้ Capacity Planning และ PSR มีข้อมูลที่ครบ

## 6. ข้อควรระวัง
- **Flow ที่ไม่มี Output** จะไม่มีใครใช้  
- **Flow ที่ไม่มี Storage** จะไม่มีข้อมูลย้อนหลัง  
- **Flow ที่ไม่มี Alert** จะไม่ตอบสนองเร็ว  
- **Flow ที่ไม่มี Runbook** จะทำให้ตอบสนองช้า  
- **Flow ที่ไม่มี Incident Record** จะไม่มี PSR

## 7. ข้อดี
- เห็นภาพรวมชัดเจน  
- ทำให้ Onboarding ทีมใหม่เร็ว  
- ทำให้ตรวจสอบได้ว่าแต่ละขั้นมีอะไรผิด  
- ทำให้เพิ่มหรือลด Metric ได้อย่างมีหลักการ

## 8. ข้อเสีย
- Flow ที่ซับซ้อนเกินไปทำให้ทีมใหม่เข้าใจยาก  
- ต้องดูแล Flow ให้ทันสมัย  
- การเพิ่ม Metric/Alert โดยไม่ทบทวน Flow ทำให้เกิดความสับสน

## 9. ข้อห้าม
- ห้ามใช้ Flow ที่ไม่มีเจ้าของขั้นตอน  
- ห้าม Flow ที่มี Alert แต่ไม่มี Runbook  
- ห้าม Flow ที่มี Dashboard แต่ไม่มี Metric  
- ห้าม Flow ที่มี Backup แต่ไม่เคย Restore Test  
- ห้าม Flow ที่มี Incident แต่ไม่มี Incident Record

## 10. รายละเอียด

### 10.1 Data Workflow

```text
[Source: PostgreSQL / Application / Log]
        │
        ▼
[Process: Extract / Transform / Aggregate]
        │
        ▼
[Storage: Prometheus TSDB / Log Store / Backup Repository]
        │
        ▼
[Output: Grafana Dashboard / Alertmanager / Report]
```

**องค์ประกอบ:**
- Input: PostgreSQL, Application, Log, Backup  
- Process: Exporter, Prometheus Scrape, Log Parser, Backup Tool  
- Storage: Prometheus TSDB, Log Store, Object Storage (MinIO/S3)  
- Output: Dashboard, Alert, Report, PSR

### 10.2 Metric Workflow

```text
PostgreSQL + Linux
        │
        ├── postgres_exporter :9187
        └── node_exporter :9100
        │
        ▼ (Pull ทุก 15s)
Prometheus :9090 (TSDB)
        │
        ├── PromQL → Grafana :3000 (Dashboard)
        └── Alert Rule → Alertmanager :9093
```

**Actor:**
- PostgreSQL — ผู้ให้ Metric  
- Exporter — ผู้แปลง Metric  
- Prometheus — ผู้เก็บและ Query  
- Grafana — ผู้แสดงผล  
- Alertmanager — ผู้จัดการแจ้งเตือน

### 10.3 Alert Workflow

```text
Metric ผิดปกติ
   │
   ▼
Alert Rule (expr + for + labels)
   │
   ▼
Pending (ยังไม่แจ้ง)
   │ (ครบ for:)
   ▼
Firing
   │
   ▼
Alertmanager (Grouping / Routing / Inhibition / Silencing)
   │
   ▼
Email / Slack / Webhook / Pager
   │
   ▼
เปิด Runbook
   │
   ▼
แก้ไข
   │
   ▼
Resolve
   │
   ▼
Incident Record → PSR → Preventive Action
```

### 10.4 ตารางเปรียบเทียบ 3 Workflow

| มิติ | Data Workflow | Metric Workflow | Alert Workflow |
|---|---|---|---|
| จุดเริ่ม | Source Data | PostgreSQL + Linux | Metric ผิดปกติ |
| การประมวลผล | Exporter / Parser | Prometheus Scrape | Alert Rule |
| Storage | TSDB / Log / Object | Prometheus TSDB | Alertmanager (ชั่วคราว) |
| ปลายทาง | Dashboard / Report | Grafana / Alertmanager | Email / Slack / Pager |
| Actor | DevOps + DBA | DevOps + DBA | DBA + DevOps + Cloud |
| Rule | Retention, Schema | Scrape Interval, Cardinality | Severity, `for:`, Runbook |

### 10.5 Swimlane Diagram (ตัวอย่าง)

```text
                │ DevOps          │ Cloud Engineer   │ DBA              │
────────────────┼─────────────────┼──────────────────┼──────────────────┤
Provision       │                 │ VM/Storage/Net   │                  │
Configure       │ Prometheus cfg  │                  │ PostgreSQL cfg   │
Operate         │ Scrape + Dash   │                  │ Backup + Vacuum  │
Alert Design    │ Alert Rules     │                  │ Runbook + Owner  │
Incident        │ First Responder │ Cloud Path Check │ DB Deep Dive     │
PSR             │ Notes           │ Notes            │ Notes            │
```

### 10.6 Workflow Gate

ทุกระยะของ Flow ควรมี **Gate**:

| Gate | เงื่อนไขผ่าน |
|---|---|
| Gate 1: Exporter Up | `curl -s localhost:9187/metrics` ได้ `pg_up 1` |
| Gate 2: Prometheus Up | `http://localhost:9090/api/v1/targets` → `"health": "up"` |
| Gate 3: Dashboard | Grafana Panel มีข้อมูลจริง |
| Gate 4: Alert Rule | `promtool check rules` + `promtool test rules` ผ่าน |
| Gate 5: Alertmanager | `amtool check-config` ผ่าน และมี Receiver |
| Gate 6: Runbook | ทุก Alert มี `runbook_url` |
| Gate 7: Incident Record | มี Template และ On-call Rotation |
| Gate 8: PSR | มี Action Item พร้อมเจ้าของและวันที่ |

### 10.7 Flow ที่ดี vs Flow ที่ไม่ดี

| Flow ที่ดี | Flow ที่ไม่ดี |
|---|---|
| มี Metric ที่ actionable | มี Metric ทุกอย่าง |
| มี Alert ที่มี Runbook | มี Alert ที่ไม่มี Runbook |
| มี Dashboard ที่ตอบคำถาม | มี Dashboard ที่เต็มไปด้วยกราฟ |
| มี Incident Record | ไม่มีบันทึก |
| มี PSR | ไม่มี PSR |
| มี Owner ชัด | ไม่มีเจ้าของ |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Metric Workflow จริง

```bash
# บน pg1: ตรวจสอบ Exporter
curl -s localhost:9187/metrics | grep -E '^pg_up'
```

ผลลัพธ์:
```text
pg_up 1
```

```bash
# บน infra: ตรวจสอบ Target ใน Prometheus
curl -s localhost:9090/api/v1/targets | python3 -m json.tool | grep -E '"scrapeUrl"|"health"'
```

ผลลัพธ์:
```text
"scrapeUrl": "http://pg1:9187/metrics",
"health": "up"
```

### ตัวอย่างที่ 2: Alert Workflow จริง

```bash
# 1) Restart pg2 → Alert ควรดัง
patronictl restart gridcare pg2 --force

# 2) ตรวจ Prometheus Alert
curl -s localhost:9090/api/v1/alerts | python3 -m json.tool | grep -E '"alertname"|"state"'
```

ผลลัพธ์:
```text
"alertname": "PostgresRecentlyRestarted",
"state": "firing"
```

```bash
# 3) ตรวจ Alertmanager
amtool alert query --alertmanager.url=http://localhost:9093
```

ผลลัพธ์:
```text
Alertname                    Starts At                Summary
PostgresRecentlyRestarted    2026-11-05 13:16:00 UTC  PostgreSQL instance pg2:9187 restarted recently
```

```bash
# 4) ตรวจ Mailpit
# เปิด http://localhost:18025
# เห็นอีเมล [FIRING:1] PostgresRecentlyRestarted
```

### ตัวอย่างที่ 3: Incident Record จาก Alert

```text
เหตุการณ์   : PostgresRecentlyRestarted
เริ่ม        : 2026-11-05 13:15:23
ตรวจพบ     : 2026-11-05 13:16:00 (Alert firing)
แก้เสร็จ    : 2026-11-05 13:16:30
ยืนยันปกติ  : 2026-11-05 13:17:00 (Alert Resolved)

อาการ      : pg2 Restart, Alert ดัง
ต้นเหตุ     : Patroni restart ตาม Plan (ไม่ใช่ Incident)
สิ่งที่ทำ    : ยืนยันผล, ปิด Alert
ตรวจพบจาก   : Alert PostgresRecentlyRestarted

PSR        : ไม่ต้องทำ (planned maintenance)
```

## 12. สรุปย่อ จำง่าย
- **Data Workflow** = Source → Process → Storage → Output  
- **Metric Workflow** = PostgreSQL → Exporter → Prometheus → Grafana/Alert  
- **Alert Workflow** = Metric → Rule → Alertmanager → Receiver → Runbook → Incident → PSR  
- **ทุก Flow มี Input / Process / Storage / Output**  
- **ทุก Gate มีเงื่อนไขผ่าน**  
- **ทุก Incident มี Incident Record**  
- **ทุก PSR มี Action Item**

ประโยคจำ: **“Flow ที่ดีคือ Flow ที่ทำให้คนรู้ว่าต้องทำอะไร ที่ไหน เมื่อไหร่”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- Prometheus Documentation: https://prometheus.io/docs/
- Alertmanager Documentation: https://prometheus.io/docs/alerting/latest/alertmanager/
- Google SRE Book — Being On-Call: https://sre.google/sre-book/being-on-call/
- GridCare Workshop: `monitoring/runbooks/`, `scripts/`, Incident Record Template
- Outline หลักสูตร Advanced PostgreSQL for Enterprise Production (PEA)

---

# บทที่ 10 นิยามศัพท์และตัวย่อ

## 1. เรื่อง
รวบรวมนิยามศัพท์และตัวย่อที่ใช้ในหนังสือเล่มนี้ พร้อมคำอธิบายที่ใช้งานได้จริง

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้ผู้อ่านใช้ศัพท์เทคนิคได้ตรงกัน  
2. เพื่อให้ทีมใหม่ Onboarding ได้เร็ว  
3. เพื่อลดการตีความผิดใน Meeting และ Documentation  
4. เพื่อให้เอกสาร Runbook และ Incident Record ใช้ภาษากลาง

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- อธิบายศัพท์เทคนิคที่ใช้ในหนังสือได้  
- ใช้ตัวย่อได้ถูกต้อง  
- อ้างอิงนิยามใน Runbook และ Incident Record ได้  
- สื่อสารกับทีมได้แม่นยำขึ้น

## 4. เนื้อหาโดยย่อ
นิยามถูกจัดกลุ่มเป็น 8 หมวด:
1. PostgreSQL Core  
2. Performance  
3. Backup และ Recovery  
4. Replication และ HA  
5. Security  
6. Observability  
7. Prometheus และ Alertmanager  
8. Incident และ Process

## 5. ประโยชน์ที่ได้รับ
- ลดการตีความผิด  
- Onboarding ทีมใหม่เร็ว  
- เอกสารมีมาตรฐานเดียวกัน  
- การสื่อสารใน Incident เร็วขึ้น

## 6. ข้อควรระวัง
- ศัพท์บางคำใช้ต่างกันในแต่ละองค์กร ควรตกลงกัน  
- ศัพท์บางคำมีนิยามที่เปลี่ยนตามบริบท  
- ควรมี Glossary ขององค์กรเอง

## 7. ข้อดี
- ทำให้เอกสารสอดคล้องกัน  
- ทำให้ Runbook และ PSR ใช้ภาษากลาง  
- ทำให้การสื่อสารใน Incident แม่นยำ

## 8. ข้อเสีย
- Glossary ที่ไม่ทบทวนจะเก่า  
- Glossary ที่ยาวเกินไปจะไม่มีคนอ่าน

## 9. ข้อห้าม
- ห้ามใช้ศัพท์โดยไม่ตกลงความหมาย  
- ห้ามใช้ตัวย่อที่ไม่มีใน Glossary  
- ห้ามใช้ศัพท์ต่างกันในเอกสารเดียวกัน

## 10. รายละเอียด

### 10.1 PostgreSQL Core

| คำ | นิยาม |
|---|---|
| PostgreSQL | ระบบฐานข้อมูลเชิงสัมพันธ์แบบ Open Source |
| Cluster | กลุ่มของ Database ที่ใช้ Data Directory เดียวกัน |
| Database | ฐานข้อมูลภายใน Cluster |
| Schema | พื้นที่เก็บ Object ภายใน Database |
| Role | ผู้ใช้หรือกลุ่มผู้ใช้ |
| Extension | Module ที่เพิ่มความสามารถ เช่น pg_stat_statements, pgcrypto |
| PGDATA | Data Directory ของ Cluster |
| pg_hba.conf | ไฟล์กำหนดกฎการเชื่อมต่อ |
| postgresql.conf | ไฟล์ Parameter หลัก |
| `pg_file_settings` | View ตรวจสอบค่าที่อ่านได้จากไฟล์ Config |
| `pg_settings` | View ตรวจสอบ Parameter ที่ใช้งานจริง |
| Postmaster | Parent Process ของ PostgreSQL |
| Backend | Process ที่ให้บริการแต่ละ Connection |
| Checkpointer | Process เขียน Dirty Page ลงดิสก์เป็นรอบ |
| Background Writer | Process เขียน Page ล่วงหน้า |
| Walwriter | Process เขียน WAL Buffer ลงดิสก์ |
| Autovacuum Launcher | Process เรียก Autovacuum Worker |

### 10.2 Performance

| คำ | นิยาม |
|---|---|
| EXPLAIN | คำสั่งแสดงแผนการทำงาน |
| EXPLAIN ANALYZE | คำสั่งรัน Query จริงและแสดงแผนพร้อมสถิติ |
| Seq Scan | การอ่านทั้งตาราง |
| Index Scan | การอ่านผ่าน Index |
| Index Only Scan | การอ่านเฉพาะ Index ไม่ต้องอ่าน Table |
| Bitmap Scan | การใช้ Bitmap จาก Index |
| Parallel Query | การประมวลผลแบบขนาน |
| pg_stat_statements | Extension เก็บสถิติ Query |
| Extended Statistics | สถิติหลายคอลัมน์สำหรับ Planner |
| work_mem | Memory ต่อ Operation เช่น Sort หรือ Hash |
| shared_buffers | Memory หลักของ PostgreSQL |
| effective_cache_size | Hint ให้ Planner ทราบ Cache ทั้งระบบ |
| Bloat | พื้นที่ที่ถูกใช้เกินความจำเป็น |
| VACUUM | ลบแถวที่ไม่มีใครเห็นและคืนพื้นที่ |
| Autovacuum | VACUUM อัตโนมัติ |
| n_dead_tup | จำนวน Dead Tuple ในตาราง |
| XID Wraparound | ปัญหาที่ Transaction ID วนกลับ |
| pg_repack | เครื่องมือจัดเรียงตารางใหม่โดยไม่บล็อกนาน |

### 10.3 Backup และ Recovery

| คำ | นิยาม |
|---|---|
| pg_dump | สำรองข้อมูลระดับ Logical |
| pg_dumpall | สำรองทั้ง Cluster รวม Role |
| pg_restore | กู้คืนจาก Format ของ pg_dump |
| pgBackRest | เครื่องมือ Backup/Restore สำหรับ PostgreSQL |
| Stanza | กลุ่ม Config ของ Backup ใน pgBackRest |
| Full Backup | สำรองข้อมูลทั้งหมด |
| Differential Backup | สำรองเฉพาะที่เปลี่ยนจาก Full ล่าสุด |
| Incremental Backup | สำรองเฉพาะที่เปลี่ยนจาก Backup ล่าสุด |
| WAL | Write-Ahead Log |
| WAL Archive | การเก็บ WAL ไว้ใช้ PITR |
| PITR | Point-in-Time Recovery |
| RTO | Recovery Time Objective |
| RPO | Recovery Point Objective |
| Restore Test | การทดสอบการกู้คืนจริง |

### 10.4 Replication และ HA

| คำ | นิยาม |
|---|---|
| Streaming Replication | การส่ง WAL จาก Primary ไป Replica |
| Logical Replication | การส่งข้อมูลเชิง Logical |
| Replication Slot | ตัวเก็บสถานะการส่ง WAL |
| Primary | โหนดที่รับเขียน |
| Replica | โหนดที่ตาม Primary |
| Failover | การสลับ Primary อัตโนมัติเมื่อ Primary ล่ม |
| Switchover | การสลับ Primary ตามแผน |
| Patroni | เครื่องมือจัดการ HA ของ PostgreSQL |
| etcd | Key-Value Store สำหรับ Distributed Consensus |
| HAProxy | Load Balancer / Proxy |
| PgBouncer | Connection Pooler |
| Split-Brain | สถานะที่มี Primary มากกว่าหนึ่งตัว |
| pg_rewind | เครื่องมือ Sync Replica เดิมกลับมา |
| Quorum | จำนวนขั้นต่ำของสมาชิกที่ทำให้ระบบทำงาน |

### 10.5 Security

| คำ | นิยาม |
|---|---|
| SCRAM | วิธีการ Hash Password ที่ปลอดภัย |
| TLS | การเข้ารหัสการเชื่อมต่อ |
| pg_hba.conf | กฎการเชื่อมต่อ |
| RLS | Row-Level Security |
| Policy | กฎ RLS |
| pgcrypto | Extension สำหรับเข้ารหัสข้อมูล |
| Masking | การปิดบังข้อมูล |
| pgAudit | Extension สำหรับ Audit |
| Superuser | ผู้ใช้ที่มีสิทธิ์สูงสุด |
| Least Privilege | หลักการให้สิทธิ์เท่าที่จำเป็น |

### 10.6 Observability

| คำ | นิยาม |
|---|---|
| Metric | ตัวเลขที่วัดสถานะของระบบ |
| Log | บันทึกเหตุการณ์ |
| Trace | เส้นทางการไหลของ Request |
| SLI | Service Level Indicator |
| SLO | Service Level Objective |
| SLA | Service Level Agreement |
| Monitoring | การเฝ้าระวัง Metric ที่รู้ล่วงหน้า |
| Observability | ความสามารถตอบคำถามใหม่จากข้อมูล |
| Dashboard | หน้าจอแสดง Metric |
| Runbook | คู่มือแก้ไขเมื่อเกิด Alert |

### 10.7 Prometheus และ Alertmanager

| คำ | นิยาม |
|---|---|
| Prometheus | ระบบเก็บ Metric แบบ Pull และ TSDB |
| TSDB | Time-Series Database |
| Exporter | โปรแกรมแปลง Metric ให้ Prometheus อ่าน |
| Scrape | การที่ Prometheus ไปดึง Metric จาก Target |
| Scrape Interval | รอบเวลาการ Scrape |
| Target | ปลายทางที่ Prometheus ไปดึง Metric |
| Series | Metric + Labels |
| Sample | ค่าและ Timestamp ของ Series |
| Label | มิติของ Metric |
| Cardinality | จำนวน Series ที่ไม่ซ้ำกัน |
| PromQL | ภาษา Query ของ Prometheus |
| Alert Rule | กฎที่ทำให้เกิด Alert |
| Pending | สถานะที่ Alert ยังไม่ถึงเกณฑ์ `for:` |
| Firing | สถานะที่ Alert กำลังแจ้ง |
| Alertmanager | ระบบจัดการและส่ง Alert |
| Receiver | ปลายทางของ Alert |
| Grouping | การรวม Alert เป็นกลุ่ม |
| Routing | การส่ง Alert ตาม Label |
| Inhibition | การยับยั้ง Alert ที่ไม่จำเป็น |
| Silencing | การปิด Alert ชั่วคราว |
| `promtool` | เครื่องมือตรวจสอบ Config และ Rule |
| `amtool` | เครื่องมือจัดการ Alertmanager |

### 10.8 Incident และ Process

| คำ | นิยาม |
|---|---|
| Incident | เหตุการณ์ที่กระทบหรืออาจกระทบサービス |
| Incident Record | บันทึกเหตุการณ์ |
| RCA | Root Cause Analysis |
| PSR | Post-Incident Review |
| MTTA | Mean Time To Acknowledge |
| MTTR | Mean Time To Resolve |
| On-call | การเข้าเวรรับแจ้งเหตุ |
| Runbook | คู่มือแก้ไข |
| Playbook | คู่มือสำหรับสถานการณ์ที่ซับซ้อน |
| Change Management | กระบวนการอนุมัติและบันทึกการเปลี่ยนแปลง |
| Blameless Postmortem | การทบทวนที่ไม่กล่าวโทษบุคคล |
| Preventive Action | การดำเนินการป้องกัน |
| KPI | Key Performance Indicator |
| SMART | Specific, Measurable, Achievable, Relevant, Time-bound |

### 10.9 ตัวย่อที่ใช้บ่อย

| ตัวย่อ | คำเต็ม |
|---|---|
| ACK | Acknowledge |
| DBA | Database Administrator |
| DCS | Distributed Configuration Store |
| ETL | Extract Transform Load |
| HA | High Availability |
| IAC | Infrastructure as Code |
| LB | Load Balancer |
| LSN | Log Sequence Number |
| MVCC | Multi-Version Concurrency Control |
| PITR | Point-In-Time Recovery |
| PGDATA | PostgreSQL Data Directory |
| RLS | Row-Level Security |
| SRE | Site Reliability Engineering |
| SSO | Single Sign-On |
| TLS | Transport Layer Security |
| TSDB | Time-Series Database |
| WAL | Write-Ahead Log |
| XID | Transaction ID |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: การใช้ Glossary ใน Incident Record

```text
เหตุการณ์   : PostgresDown
RTO          : 31 วินาที (เป้าหมาย ≤ 45 วินาที)
RPO          : 0
MTTA         : 30 วินาที
MTTR         : 45 วินาที
Runbook      : C08-postgres-down.md
PSR          : 2026-11-05
```

### ตัวอย่างที่ 2: การใช้ Glossary ใน Runbook

```text
Alert       : PostgresConnectionsHigh
Severity    : warning
Metric      : pg_stat_activity_count / pg_settings_max_connections
Threshold   : > 80% ต่อเนื่อง 5 นาที
Action      : ตรวจ PgBouncer, session ค้าง, idle in transaction
Runbook URL : C03-connection-limit-locking.md
Owner       : DBA (Primary), DevOps (Secondary)
```

### ตัวอย่างที่ 3: การใช้ Glossary ใน Dashboard

```text
Panel       : TPS
Metric      : pg_stat_database_xact_commit + pg_stat_database_xact_rollback
PromQL      : sum by (datname) (rate(...) + rate(...))
Unit        : ops/s
Target      : ≥ 100 tps
```

## 12. สรุปย่อ จำง่าย
- **Glossary ทำให้ทุกคนพูดภาษาเดียวกัน**  
- **ศัพท์มี 8 หมวด:** Core, Performance, Backup, HA, Security, Observability, Prometheus, Incident  
- **ตัวย่อต้องมีใน Glossary** ก่อนใช้  
- **Glossary ต้องทบทวนเป็นระยะ**  
- **Glossary ที่ดีทำให้ Incident ตอบสนองเร็วขึ้น**

ประโยคจำ: **“ภาษากลางคือเครื่องมือแรกของทีมที่ทำงานด้วยกัน”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — Glossary: https://www.postgresql.org/docs/17/glossary.html
- Prometheus Documentation — Glossary: https://prometheus.io/docs/introduction/glossary/
- Google SRE Book — Glossary: https://sre.google/sre-book/table-of-contents/
- ITIL 4 — Glossary of Terms
- GridCare Workshop: `monitoring/runbooks/`, Incident Record Template

---

## สรุปส่วนที่ 1 (บทที่ 2–10)

| บท | แก่นของบท | จุดเชื่อมโยงกับส่วนถัดไป |
|---|---|---|
| 2 | บทบาทและ RACI ของ DevOps / Cloud / DBA | ทุกบท |
| 3 | สถาปัตยกรรม PostgreSQL และ Metric ที่ผูกกับมัน | Performance, Monitoring |
| 4 | วงจรชีวิต 8 ระยะ + Gate + KPI | Operations, Evolution |
| 5 | Monitoring vs Observability, 3 เสาหลัก | Prometheus, Alertmanager |
| 6 | Prometheus สถาปัตยกรรม + TSDB + Pull Model | Exporter, PromQL |
| 7 | Alertmanager + Grouping + Routing + Inhibition | Alert Design |
| 8 | Alert ที่ actionable + Severity + Runbook + Test | Incident, PSR |
| 9 | Workflow Data / Metric / Alert | Operations |
| 10 | Glossary กลางของทีม | ทุกบท |

---