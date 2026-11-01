# บทที่ 51–60 

> หนังสือ: คู่มือการใช้งาน PostgreSQL สำหรับ DevOps Engineer, Cloud Engineer และ DBA  
> ส่วนที่ 6 Alerting  
> โทน: ทางการ กระชับ เน้นใช้งานจริง

---

# บทที่ 51 หลักการออกแบบ Alert

## 1. เรื่อง
หลักการออกแบบ Alert ที่ actionable ไม่รบกวน และเชื่อมโยงกับ Runbook และ Incident Process

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้ผู้อ่านออกแบบ Alert ที่ตอบคำถาม "ต้องทำอะไร" ได้ทันที  
2. เพื่อลด Alert Fatigue และ False Positive  
3. เพื่อให้ทุก Alert มี Severity, Runbook และเจ้าของ  
4. เพื่อให้ Alert ที่ดีเชื่อมโยงกับ Incident Response

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- อธิบาย 4 เกณฑ์ของ Alert ที่ดี (Actionable, Timely, Specific, Owned)  
- เลือก Severity ได้ถูกต้อง  
- เขียน `summary`, `description`, `runbook_url` ที่มีประโยชน์  
- เลือก `for:` ที่เหมาะสมกับอาการ  
- ออกแบบ Alert Review Process

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
- ห้าม Alert ที่ไม่ actionable (เช่น "CPU สูง" โดยไม่มีเกณฑ์)  
- ห้ามใช้ Alert เป็น Log

## 10. รายละเอียด

### 10.1 4 เกณฑ์ของ Alert ที่ดี

| เกณฑ์ | ความหมาย | ตัวอย่าง |
|---|---|---|
| Actionable | มีสิ่งที่ต้องทำ | `PostgresDown` → เปิด Runbook C08 |
| Timely | มาตรงเวลา | `for: 1m` ไม่ดังช้าเกินไป |
| Specific | เจาะจง | `instance="pg1:9187"` ไม่ใช่ "ทุกอย่าง" |
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

### 10.5 Alert Review Process

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

### 10.6 ตาราง Owner ของ Alert

| Alert | Primary Owner | Secondary | Runbook |
|---|---|---|---|
| `PostgresDown` | DBA | DevOps | `C08-postgres-down.md` |
| `PostgresConnectionsHigh` | DBA | DevOps | `C03-connection-limit-locking.md` |
| `DiskSpaceLow` | Cloud Engineer | DBA | `C04-disk-full.md` |
| `BackupTooOld` | DBA | Cloud Engineer | `C07-backup-recovery.md` |
| `SslCertificateExpiringSoon` | DBA | Cloud Engineer | `C10-security.md` |
| `PatroniPrimaryCountNotOne` | DBA | DevOps | `C08-replication-lag-slot-failover.md` |
| `NodeExporterDown` | DevOps | Cloud Engineer | `C11-monitoring.md` |

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
    description: "ตรวจ pg_stat_statements Top 5, pg_stat_activity, autovacuum"
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

ประโยคจำ: **"Alert ที่ดีทำให้คนรู้ว่าต้องทำอะไร ไม่ใช่แค่รู้ว่ามีอะไรผิดปกติ"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- Prometheus Alerting Rules: https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/
- Google SRE Book — Monitoring Distributed Systems: https://sre.google/sre-book/monitoring-distributed-systems/
- Rob Ewaschuk — My Philosophy on Alerting: https://docs.google.com/document/d/199PqyG3UsyXlwieHaqbGiWVa8eMWi8zzAn0YfcApr8Q/
- GridCare Workshop Day 4: Lab 4.1

---

# บทที่ 52 Prometheus Alert Rules

## 1. เรื่อง
การเขียน Alert Rule ใน Prometheus ด้วย YAML และการใช้งานกับ PostgreSQL

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เขียน Alert Rule ที่ถูกต้อง  
2. เพื่อให้ใช้ Label และ Annotation ที่ดี  
3. เพื่อให้ใช้ `for:`, `keep_firing_for`  
4. เพื่อให้จัดกลุ่ม Rule ด้วย `groups`

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- เขียน Rule ด้วย `expr`, `for`, `labels`, `annotations`  
- จัดกลุ่ม Rule ด้วย `groups`  
- ใช้ `record` สำหรับ Recording Rule  
- ใช้ `keep_firing_for`  
- ตรวจสอบด้วย `promtool check rules`

## 4. เนื้อหาโดยย่อ
Alert Rule ประกอบด้วย:
- **`alert`** — ชื่อ  
- **`expr`** — PromQL  
- **`for`** — ระยะเวลาที่ต้องเป็นจริงก่อน Firing  
- **`keep_firing_for`** — ระยะเวลาที่ต้องเป็นจริงก่อน Resolve (PG 2.42+)  
- **`labels`** — Severity, Owner  
- **`annotations`** — Summary, Description, Runbook

Recording Rule ใช้:
- **`record`** — ชื่อ Metric ใหม่  
- **`expr`** — PromQL

## 5. ประโยชน์ที่ได้รับ
- Alert ทำงานตามที่ต้องการ  
- ลด False Positive  
- ใช้ Recording Rule ลด Query ซ้ำ  
- ตรวจสอบได้ด้วย `promtool`

## 6. ข้อควรระวัง
- **`expr` ต้องคืนค่า Boolean หรือ Vector**  
- **`for: 0s` กับ Gauge ที่กระพริบทำให้ Alert ถี่**  
- **`labels` ที่ซ้ำกับ Metric เดิมจะทับ**  
- **`keep_firing_for` ต้องใช้ Prometheus 2.42+**  
- **Recording Rule ต้องไม่ Cardinality สูง**

## 7. ข้อดี
- ยืดหยุ่น  
- ตรวจสอบได้  
- ใช้ Recording Rule ลด Query ซ้ำ

## 8. ข้อเสีย
- Syntax เข้มงวด  
- ต้อง Reload เมื่อแก้  
- ต้องทดสอบด้วย `promtool test rules`

## 9. ข้อห้าม
- ห้าม Alert Rule ที่ไม่มี `for:` สำหรับ Warning  
- ห้าม Recording Rule ที่ Cardinality สูง  
- ห้ามใช้ `expr` ที่คืนค่า String  
- ห้าม Alert ที่ไม่มี Runbook  
- ห้าม Recording Rule ที่ซ้ำกับ Metric ที่มีอยู่

## 10. รายละเอียด

### 10.1 โครงสร้างไฟล์ Alert Rule

```yaml
groups:
  - name: gridcare-postgres
    interval: 30s
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
```

### 10.2 ตัวอย่าง Alert Rule ที่ครบ

```yaml
groups:
  - name: gridcare-postgres
    interval: 30s
    rules:
      - alert: PostgresDown
        expr: pg_up == 0
        for: 1m
        labels: {severity: critical, owner: dba}
        annotations:
          summary: "PostgreSQL instance {{ $labels.instance }} down"
          description: "pg_up = 0 ต่อเนื่อง 1 นาที"
          runbook_url: "http://gridcare-infra/runbooks/C08-postgres-down.md"

      - alert: PostgresConnectionsHigh
        expr: |
          sum by (instance) (pg_stat_activity_count{datname="gridcare"})
          /
          max by (instance) (pg_settings_max_connections) * 100 > 80
        for: 5m
        labels: {severity: warning, owner: dba}
        annotations:
          summary: "Connection ใช้งานเกิน 80%"
          description: "ตรวจ PgBouncer, session ค้าง และ idle in transaction"
          runbook_url: "http://gridcare-infra/runbooks/C03-connection-limit-locking.md"

      - alert: PostgresXidAgeWarning
        expr: pg_database_wraparound_age_datfrozenxid_seconds > 1e9
        for: 1h
        labels: {severity: warning, owner: dba}
        annotations:
          summary: "XID Age {{ $value }} ใน {{ $labels.datname }}"
          description: "Autovacuum ไม่ทำงาน หรือมี Transaction ค้าง"
          runbook_url: "http://gridcare-infra/runbooks/C05-bloat-vacuum-wraparound.md"

      - alert: PostgresXidAgeCritical
        expr: pg_database_wraparound_age_datfrozenxid_seconds > 1.5e9
        for: 5m
        labels: {severity: critical, owner: dba}
        annotations:
          summary: "XID Age {{ $value }} ใกล้ Wraparound"
          description: "ต้อง VACUUM ทันที"
          runbook_url: "http://gridcare-infra/runbooks/C05-bloat-vacuum-wraparound.md"

      - alert: PostgresReplicationLagHigh
        expr: max by (instance, application_name) (pg_stat_replication_pg_wal_lsn_diff) > 100 * 1024 * 1024
        for: 5m
        labels: {severity: warning, owner: dba}
        annotations:
          summary: "Replication Lag > 100 MB"
          description: "ตรวจ network, WAL, replica resource"
          runbook_url: "http://gridcare-infra/runbooks/C08-replication-lag-slot-failover.md"
```

### 10.3 Recording Rule

```yaml
groups:
  - name: gridcare-recording
    interval: 30s
    rules:
      - record: gridcare:tps:rate5m
        expr: |
          sum by (datname) (
            rate(pg_stat_database_xact_commit{datname="gridcare"}[5m])
            + rate(pg_stat_database_xact_rollback{datname="gridcare"}[5m])
          )

      - record: gridcare:cache_hit_ratio
        expr: |
          rate(pg_stat_database_blks_hit{datname="gridcare"}[5m])
          /
          (
            rate(pg_stat_database_blks_hit{datname="gridcare"}[5m])
            + rate(pg_stat_database_blks_read{datname="gridcare"}[5m])
          )
```

### 10.4 `keep_firing_for`

```yaml
- alert: PostgresDown
  expr: pg_up == 0
  for: 1m
  keep_firing_for: 5m
  labels: {severity: critical, owner: dba}
```

> 💡 `keep_firing_for` ทำให้ Alert ยังคง Firing ถึงแม้ Metric กลับมาปกติแล้วเป็นเวลา 5 นาที — เหมาะกับ Alert ที่ไม่ต้องการให้ Resolve เร็วเกินไป

### 10.5 ตรวจสอบ Rule

```bash
promtool check rules /etc/prometheus/rules/*.yml
```

ผลลัพธ์:
```text
Checking gridcare-postgres-alerts.yml
  SUCCESS: 21 rules found
```

### 10.6 ตาราง Field สำคัญ

| Field | ใช้ |
|---|---|
| `alert` | ชื่อ Alert |
| `expr` | PromQL |
| `for` | ระยะเวลาที่ต้องเป็นจริง |
| `keep_firing_for` | ระยะเวลาคง Firing หลัง Resolve |
| `labels` | Severity, Owner |
| `annotations` | Summary, Description, Runbook |
| `record` | Recording Rule |
| `groups` | กลุ่ม Rule |
| `interval` | รอบ Evaluation |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Alert Rule ครบชุด

```yaml
groups:
  - name: gridcare-postgres
    interval: 30s
    rules:
      - alert: PostgresDown
        expr: pg_up == 0
        for: 1m
        labels: {severity: critical, owner: dba}
        annotations:
          summary: "PostgreSQL instance {{ $labels.instance }} down"
          description: "pg_up = 0 ต่อเนื่อง 1 นาที"
          runbook_url: "http://gridcare-infra/runbooks/C08-postgres-down.md"
```

### ตัวอย่างที่ 2: Alert Rule ที่ใช้ `absent()`

```yaml
- alert: PostgresExporterDown
  expr: absent(pg_up{instance=~"pg.*"})
  for: 2m
  labels: {severity: critical, owner: devops}
  annotations:
    summary: "ไม่พบ Metric pg_up จาก {{ $labels.instance }}"
    runbook_url: "http://gridcare-infra/runbooks/C11-monitoring.md"
```

### ตัวอย่างที่ 3: Recording Rule

```yaml
- record: gridcare:tps:rate5m
  expr: |
    sum by (datname) (
      rate(pg_stat_database_xact_commit{datname="gridcare"}[5m])
      + rate(pg_stat_database_xact_rollback{datname="gridcare"}[5m])
    )
```

### ตัวอย่างที่ 4: Alert ที่ใช้ Recording Rule

```yaml
- alert: PostgresTpsDrop
  expr: gridcare:tps:rate5m < 10
  for: 10m
  labels: {severity: warning, owner: dba}
  annotations:
    summary: "TPS ของ gridcare < 10"
    description: "ตรวจแอป, PgBouncer, HAProxy"
    runbook_url: "http://gridcare-infra/runbooks/C08-replication-lag-slot-failover.md"
```

### ตัวอย่างที่ 5: ตรวจ Rule

```bash
promtool check rules /etc/prometheus/rules/gridcare-postgres-alerts.yml
```

ผลลัพธ์:
```text
Checking /etc/prometheus/rules/gridcare-postgres-alerts.yml
  SUCCESS: 21 rules found
```

## 12. สรุปย่อ จำง่าย
- **Alert Rule = `alert` + `expr` + `for` + `labels` + `annotations`**  
- **Recording Rule = `record` + `expr`**  
- **`keep_firing_for`** ทำให้ Alert คง Firing หลัง Resolve  
- **`promtool check rules`** ก่อน Reload  
- **`groups`** จัดกลุ่ม Rule  
- **`interval`** รอบ Evaluation

ประโยคจำ: **"Alert Rule ที่ดีคือ Alert Rule ที่ตรวจสอบได้และมี Runbook"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- Prometheus Alerting Rules: https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/
- Prometheus Recording Rules: https://prometheus.io/docs/prometheus/latest/configuration/recording_rules/
- GridCare Workshop Day 4: Lab 4.1

---

# บทที่ 53 promtool check และ test

## 1. เรื่อง
`promtool` สำหรับตรวจสอบและทดสอบ Config และ Alert Rule ของ Prometheus

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้ตรวจ Config ด้วย `promtool check config`  
2. เพื่อให้ตรวจ Rule ด้วย `promtool check rules`  
3. เพื่อให้ทดสอบ Rule ด้วย `promtool test rules`  
4. เพื่อให้ใช้ Unit Test ก่อนใช้งานจริง

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ใช้ `promtool check config`  
- ใช้ `promtool check rules`  
- เขียน Unit Test ด้วย `promtool test rules`  
- ใช้ `promtool query instant` และ `query range`

## 4. เนื้อหาโดยย่อ
`promtool` เป็นเครื่องมือมาตรฐานของ Prometheus:
- **`check config`** — ตรวจ `prometheus.yml`  
- **`check rules`** — ตรวจ Rule  
- **`test rules`** — ทดสอบ Rule ด้วย Unit Test  
- **`query instant`** — Query Metric ทันที  
- **`query range`** — Query Metric ช่วงเวลา  
- **`tsdb`** — ตรวจ TSDB

## 5. ประโยชน์ที่ได้รับ
- ลด Error ก่อน Reload  
- ทดสอบ Rule ก่อนใช้งานจริง  
- ลด False Positive  
- ทำให้ CI/CD มี Gate

## 6. ข้อควรระวัง
- **`promtool test rules` ต้องใช้ Path เต็ม**  
- **Unit Test ต้องมี `input_series` และ `alert_rule_test`**  
- **`promtool check rules` ตรวจ Syntax เท่านั้น ไม่ได้ตรวจ Logic**  
- **`promtool query` ต้องมี Prometheus ที่ทำงาน**

## 7. ข้อดี
- มาตรฐาน  
- ใช้งานง่าย  
- ใช้ใน CI/CD ได้  
- ตรวจ Syntax ก่อน Reload

## 8. ข้อเสีย
- Unit Test ต้องเขียนเอง  
- `check` ไม่ได้ตรวจ Logic

## 9. ข้อห้าม
- ห้าม Reload Config โดยไม่ `check config`  
- ห้าม Reload Rule โดยไม่ `check rules`  
- ห้ามใช้ `test rules` กับ Rule ที่ไม่มี Test  
- ห้ามใช้ `promtool` กับ Prometheus ที่ไม่มี

## 10. รายละเอียด

### 10.1 `promtool check config`

```bash
promtool check config /etc/prometheus/prometheus.yml
```

ผลลัพธ์:
```text
Checking /etc/prometheus/prometheus.yml
  SUCCESS: 5 scrape configs found
```

### 10.2 `promtool check rules`

```bash
promtool check rules /etc/prometheus/rules/*.yml
```

ผลลัพธ์:
```text
Checking gridcare-postgres-alerts.yml
  SUCCESS: 21 rules found
```

### 10.3 `promtool test rules`

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

```bash
promtool test rules ~/gridcare-ha-alerts.test.yml
```

ผลลัพธ์:
```text
Unit Testing:  /home/student/gridcare-ha-alerts.test.yml
  SUCCESS
```

### 10.4 `promtool query`

```bash
promtool query instant http://localhost:9090 'pg_up'
```

ผลลัพธ์:
```text
pg_up{instance="pg1:9187", job="postgres"} => 1 @[1730702112.345]
```

```bash
promtool query range --start=1730702000 --end=1730702112 --step=15s \
  http://localhost:9090 'pg_up'
```

### 10.5 `promtool tsdb`

```bash
promtool tsdb list /var/lib/prometheus
```

ผลลัพธ์:
```text
BLOCKULID              MIN TIME              MAX TIME              DURATION     NUM SAMPLES  NUM CHUNKS  NUM SERIES  SIZE
01HQZ8XXXX             2026-10-20T00:00:00Z  2026-10-21T00:00:00Z  24h          1234567      5678        4521        120 MB
```

### 10.6 ตาราง `promtool` Command

| Command | ใช้ |
|---|---|
| `check config` | ตรวจ `prometheus.yml` |
| `check rules` | ตรวจ Rule |
| `test rules` | ทดสอบ Rule ด้วย Unit Test |
| `query instant` | Query ทันที |
| `query range` | Query ช่วงเวลา |
| `tsdb list` | ตรวจ Block ของ TSDB |
| `tsdb analyze` | วิเคราะห์ TSDB |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: ตรวจ Config ก่อน Reload

```bash
promtool check config /etc/prometheus/prometheus.yml && sudo systemctl reload prometheus
```

ผลลัพธ์:
```text
Checking /etc/prometheus/prometheus.yml
  SUCCESS: 5 scrape configs found
```

### ตัวอย่างที่ 2: ตรวจ Rule ก่อน Reload

```bash
promtool check rules /etc/prometheus/rules/*.yml && sudo systemctl reload prometheus
```

ผลลัพธ์:
```text
Checking gridcare-postgres-alerts.yml
  SUCCESS: 21 rules found
```

### ตัวอย่างที่ 3: ทดสอบ Rule ด้วย Unit Test

```bash
promtool test rules ~/gridcare-ha-alerts.test.yml
```

ผลลัพธ์:
```text
Unit Testing:  /home/student/gridcare-ha-alerts.test.yml
  SUCCESS
```

### ตัวอย่างที่ 4: ตรวจ Metric ที่ Firing

```bash
curl -s localhost:9090/api/v1/alerts | python3 -m json.tool | grep -E '"alertname"|"state"'
```

ผลลัพธ์:
```text
"alertname": "PostgresRecentlyRestarted",
"state": "firing"
```

### ตัวอย่างที่ 5: ใช้ `promtool query` ใน CI/CD

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "== Check config =="
promtool check config /etc/prometheus/prometheus.yml

echo "== Check rules =="
promtool check rules /etc/prometheus/rules/*.yml

echo "== Test rules =="
promtool test rules /etc/prometheus/tests/*.test.yml

echo "== Reload =="
sudo systemctl reload prometheus
```

## 12. สรุปย่อ จำง่าย
- **`promtool check config`** — ตรวจ Config  
- **`promtool check rules`** — ตรวจ Rule  
- **`promtool test rules`** — ทดสอบ Rule ด้วย Unit Test  
- **`promtool query`** — Query Metric  
- **`promtool tsdb`** — ตรวจ TSDB  
- **ทุก Change ต้องผ่าน `promtool` ก่อน Reload**

ประโยคจำ: **"`promtool` คือประตูด่านแรกก่อน Reload Prometheus"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- promtool: https://prometheus.io/docs/prometheus/latest/command-line/promtool/
- Prometheus Unit Testing: https://prometheus.io/docs/prometheus/latest/configuration/unit_testing_rules/
- GridCare Workshop Day 4: Lab 4.1

---

# บทที่ 54 Alertmanager Configuration

## 1. เรื่อง
การตั้งค่า Alertmanager สำหรับ Production: Global, Route, Receiver และ Inhibit Rule

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เขียน `alertmanager.yml` ที่ใช้งานได้จริง  
2. เพื่อให้ใช้ `amtool check-config`  
3. เพื่อให้ตั้ง Global SMTP และ Receiver  
4. เพื่อให้ตั้ง Route และ Inhibit Rule

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- เขียน `alertmanager.yml` ครบ  
- ใช้ `amtool check-config`  
- ใช้ `amtool alert query`  
- ใช้ `amtool config routes show`

## 4. เนื้อหาโดยย่อ
`alertmanager.yml` ประกอบด้วย:
- **`global`** — SMTP, Resolve Timeout  
- **`route`** — Routing Tree  
- **`inhibit_rules`** — กฎยับยั้ง  
- **`receivers`** — ปลายทาง  
- **`templates`** — Template (optional)

## 5. ประโยชน์ที่ได้รับ
- Alert ถูกส่งถูกที่  
- ลด Alert ซ้ำ  
- ใช้ `amtool` ตรวจสอบได้  
- รองรับหลาย Receiver

## 6. ข้อควรระวัง
- **`route` ที่ไม่มี Fallback** ทำให้ Alert ตกหล่น  
- **`inhibit_rules` ที่ผิด** อาจยับยั้ง Critical  
- **`receivers` ที่ไม่มี Config** ทำให้ Alert ไม่ถึง  
- **`resolve_timeout` สั้นเกินไป** อาจ Resolve ก่อนกำหนด

## 7. ข้อดี
- ยืดหยุ่น  
- ตรวจสอบได้  
- รองรับหลาย Channel

## 8. ข้อเสีย
- YAML ซับซ้อน  
- ต้องใช้ `amtool` ตรวจ  
- ไม่มี UI สำหรับ On-call Rotation

## 9. ข้อห้าม
- ห้าม Route ที่ไม่มี Fallback  
- ห้าม Inhibit ที่ทำให้ Critical ถูกกลบ  
- ห้าม Receiver ที่ไม่มี Config  
- ห้าม Silence ที่ไม่มีวันสิ้นสุด  
- ห้าม `repeat_interval: 1m` สำหรับ Critical

## 10. รายละเอียด

### 10.1 โครงสร้าง `alertmanager.yml`

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

### 10.2 `amtool check-config`

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

### 10.3 `amtool alert query`

```bash
amtool alert query --alertmanager.url=http://localhost:9093
```

ผลลัพธ์:
```text
Alertname              Starts At                Summary
PostgresRecentlyRestarted 2026-11-05 13:16:00 UTC  PostgreSQL instance pg2:9187 restarted recently
```

### 10.4 `amtool config routes show`

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

### 10.5 `amtool silence add`

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

### 10.6 ตาราง Field สำคัญ

| Field | ใช้ |
|---|---|
| `global.smtp_smarthost` | SMTP Server |
| `global.resolve_timeout` | เวลาที่ถือว่า Resolve |
| `route.receiver` | Receiver หลัก |
| `route.group_by` | จัดกลุ่ม |
| `route.group_wait` | รอรวมกลุ่ม |
| `route.group_interval` | รอส่งกลุ่มถัดไป |
| `route.repeat_interval` | ส่งซ้ำ |
| `route.routes` | Sub-Route |
| `inhibit_rules` | ยับยั้ง |
| `receivers` | ปลายทาง |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Config พื้นฐาน

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

### ตัวอย่างที่ 2: Config ที่มี Inhibit

```yaml
inhibit_rules:
  - source_match:
      alertname: PostgresDown
    target_match_re:
      alertname: Postgres.*
    equal: ['instance']
```

> 💡 `PostgresDown` ยับยั้ง Alert อื่น ๆ ของ Instance เดียวกัน เพราะเมื่อ Down แล้ว Alert อื่นไม่มีความหมาย

### ตัวอย่างที่ 3: Config ที่มี Webhook

```yaml
receivers:
  - name: pager-critical
    webhook_configs:
      - url: 'http://pagerduty.local/api/alert'
        send_resolved: true
```

### ตัวอย่างที่ 4: ตรวจ Config

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

## 12. สรุปย่อ จำง่าย
- **`alertmanager.yml` = Global + Route + Inhibit + Receiver**  
- **`amtool check-config`** ก่อน Reload  
- **`route` ต้องมี Fallback**  
- **`inhibit_rules` ต้องไม่กลบ Critical**  
- **`receivers` ต้องมี Config**  
- **`amtool silence` ต้องมีวันสิ้นสุด**

ประโยคจำ: **"Alertmanager Configuration ที่ดีคือ Configuration ที่ตรวจสอบได้"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- Alertmanager Configuration: https://prometheus.io/docs/alerting/latest/configuration/
- `amtool`: https://github.com/prometheus/alertmanager#amtool
- GridCare Workshop Day 4: Lab 4.1

---

# บทที่ 55 Routing, Grouping และ Inhibition

## 1. เรื่อง
การจัดการ Alert ด้วย Routing, Grouping และ Inhibition ใน Alertmanager

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจว่า Routing, Grouping, Inhibition ทำงานอย่างไร  
2. เพื่อให้ตั้งค่าให้เหมาะกับ Severity และ Owner  
3. เพื่อให้ลด Alert ซ้ำ  
4. เพื่อให้ลด False Positive

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- อธิบาย Routing Tree  
- ตั้ง `group_by`, `group_wait`, `group_interval`  
- ตั้ง `inhibit_rules`  
- ใช้ `amtool config routes` ตรวจ

## 4. เนื้อหาโดยย่อ
**Routing** — ส่ง Alert ตาม Label  
**Grouping** — รวม Alert เป็นกลุ่ม  
**Inhibition** — ยับยั้ง Alert ที่ไม่จำเป็น  
**Silencing** — ปิด Alert ชั่วคราว

## 5. ประโยชน์ที่ได้รับ
- Alert ถูกส่งถูกคน  
- ลด Alert ซ้ำ  
- ลด Alert Fatigue  
- ตั้ง On-call ได้

## 6. ข้อควรระวัง
- **`group_by` กว้างเกินไป** ทำให้ Alert ที่ไม่เกี่ยวข้องรวมกัน  
- **`group_wait` นานเกินไป** ทำให้ Alert มาช้า  
- **`inhibit_rules` ผิด** อาจยับยั้ง Critical  
- **`silence` ค้าง** ทำให้ Alert ไม่ดัง

## 7. ข้อดี
- ยืดหยุ่น  
- ลด Alert ซ้ำ  
- ตั้ง On-call ได้

## 8. ข้อเสีย
- YAML ซับซ้อน  
- ต้องออกแบบให้ดี  
- ต้องทบทวนเป็นระยะ

## 9. ข้อห้าม
- ห้าม `group_by: []` (รวมทั้งหมด)  
- ห้าม `inhibit_rules` ที่กลบ Critical  
- ห้าม Silence ค้าง  
- ห้าม `repeat_interval` ที่สั้นเกินไป

## 10. รายละเอียด

### 10.1 Routing Tree

```text
default-email
├── severity=critical → pager-critical (group_wait=10s, repeat=30m)
├── severity=warning → dba-email (repeat=2h)
└── severity=info → log-only
```

### 10.2 Routing Config

```yaml
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
```

### 10.3 Grouping

| Field | ใช้ | ค่าแนะนำ |
|---|---|---|
| `group_by` | จัดกลุ่ม | `['alertname', 'instance']` |
| `group_wait` | รอรวมกลุ่ม | `30s` (Critical `10s`) |
| `group_interval` | รอส่งกลุ่มถัดไป | `5m` |
| `repeat_interval` | ส่งซ้ำ | `4h` (Critical `30m`) |

### 10.4 Inhibition

```yaml
inhibit_rules:
  - source_match:
      alertname: PostgresDown
    target_match_re:
      alertname: Postgres.*
    equal: ['instance']

  - source_match:
      severity: critical
    target_match:
      severity: warning
    equal: ['instance']
```

> 💡 Critical ยับยั้ง Warning ของ Instance เดียวกัน  
> 💡 PostgresDown ยับยั้ง Alert อื่น ๆ ของ Instance เดียวกัน

### 10.5 Silencing

```bash
amtool silence add alertname="Postgres.*" instance="pg1:9187" \
  --duration=2h \
  --comment="Maintenance: upgrade" \
  --alertmanager.url=http://localhost:9093
```

### 10.6 ตรวจสอบ Routes

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

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Critical ไปที่ Pager

```yaml
routes:
  - match:
      severity: critical
    receiver: pager-critical
    group_wait: 10s
    repeat_interval: 30m
```

### ตัวอย่างที่ 2: Warning ไปที่ Email

```yaml
routes:
  - match:
      severity: warning
    receiver: dba-email
    repeat_interval: 2h
```

### ตัวอย่างที่ 3: Inhibition ที่ดี

```yaml
inhibit_rules:
  - source_match:
      alertname: PostgresDown
    target_match_re:
      alertname: Postgres.*
    equal: ['instance']
```

### ตัวอย่างที่ 4: ตรวจ Routes

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

### 示例ที่ 5: ตรวจ Silence

```bash
amtool silence query --alertmanager.url=http://localhost:9093
```

ผลลัพธ์:
```text
ID                                    Matchers                     Ends At                  Created By  Comment
a3b1c2d4-e5f6-7890-abcd-ef1234567890  alertname=Postgres.*        2026-11-05 15:30:00 UTC  student     Maintenance: upgrade
```

## 12. สรุปย่อ จำง่าย
- **Routing** = ส่งตาม Label  
- **Grouping** = รวม Alert เป็นกลุ่ม  
- **Inhibition** = ยับยั้ง Alert ที่ไม่จำเป็น  
- **Silencing** = ปิดชั่วคราว  
- **Critical → Pager, Warning → Email, Info → Log**  
- **Critical ยับยั้ง Warning ของ Instance เดียวกัน**

ประโยคจำ: **"Routing ที่ดีคือ Routing ที่ทำให้ Alert ไปถึงคนที่ถูกต้อง ไม่ใช่ทุกคน"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- Alertmanager Configuration: https://prometheus.io/docs/alerting/latest/configuration/
- GridCare Workshop Day 4: Lab 4.1

---

# บทที่ 56 Email, Slack และ Webhook

## 1. เรื่อง
การตั้งค่า Receiver ประเภทต่าง ๆ ใน Alertmanager: Email, Slack, Webhook และ Pager

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้ตั้ง Receiver แต่ละประเภท  
2. เพื่อให้ใช้ Template  
3. เพื่อให้ทดสอบ Receiver  
4. เพื่อให้ผูกกับ Severity

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ตั้ง `email_configs`, `slack_configs`, `webhook_configs`  
- ใช้ Template  
- ทดสอบด้วย `amtool`  
- ผูก Receiver กับ Severity

## 4. เนื้อหาโดยย่อ
Receiver ประเภทหลัก:
- **Email** — SMTP  
- **Slack** — Webhook URL  
- **Webhook** — HTTP POST  
- **Pager** — PagerDuty, Opsgenie

## 5. ประโยชน์ที่ได้รับ
- Alert ไปถึงทุกช่องทาง  
- ใช้ Severity ในการเลือก  
- ใช้ Template ทำให้อ่านง่าย

## 6. ข้อควรระวัง
- **Slack Webhook URL มี Secret**  
- **Email ต้องมี SMTP**  
- **Webhook ต้องตอบ 200 OK**  
- **Template ต้อง Format ถูก**  
- **Pager ต้องมี Integration Key**

## 7. ข้อดี
- หลายช่องทาง  
- Template ยืดหยุ่น  
- ใช้ Severity ได้

## 8. ข้อเสีย
- ต้องตั้งหลายที่  
- Secret ต้องจัดการ  
- Template ต้องเขียนเอง

## 9. ข้อห้าม
- ห้าม Secret ใน Git  
- ห้าม Email ที่ไม่มี `send_resolved`  
- ห้าม Webhook ที่ไม่มี Retry  
- ห้าม Pager ที่ไม่มี Escalation

## 10. รายละเอียด

### 10.1 Email Receiver

```yaml
receivers:
  - name: dba-email
    email_configs:
      - to: 'dba-oncall@gridcare.lab'
        send_resolved: true
        headers:
          Subject: '[{{ .Status | toUpper }}] {{ .GroupLabels.alertname }}'
```

### 10.2 Slack Receiver

```yaml
receivers:
  - name: dba-slack
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/T000/B000/XXXX'
        channel: '#dba-alerts'
        send_resolved: true
        title: '[{{ .Status | toUpper }}] {{ .GroupLabels.alertname }}'
        text: |
          {{ range .Alerts }}
          *Summary:* {{ .Annotations.summary }}
          *Description:* {{ .Annotations.description }}
          *Runbook:* {{ .Annotations.runbook_url }}
          {{ end }}
```

### 10.3 Webhook Receiver

```yaml
receivers:
  - name: pager-critical
    webhook_configs:
      - url: 'http://pagerduty.local/api/alert'
        send_resolved: true
        max_alerts: 0
```

### 10.4 PagerDuty Receiver

```yaml
receivers:
  - name: pager-critical
    pagerduty_configs:
      - service_key: '<PAGERDUTY_SERVICE_KEY>'
        severity: '{{ .CommonLabels.severity }}'
```

### 10.5 Template ที่มีประโยชน์

```text
{{ range .Alerts }}
*Alert:* {{ .Labels.alertname }}
*Severity:* {{ .Labels.severity }}
*Instance:* {{ .Labels.instance }}
*Summary:* {{ .Annotations.summary }}
*Description:* {{ .Annotations.description }}
*Runbook:* {{ .Annotations.runbook_url }}
*Started At:* {{ .StartsAt }}
{{ end }}
```

### 10.6 ตาราง Receiver

| Receiver | Secret | ใช้ |
|---|---|---|
| Email | SMTP Password | DBA, DevOps |
| Slack | Webhook URL | ทีม |
| Webhook | URL + Token | Pager, Ticketing |
| PagerDuty | Service Key | Critical |
| Opsgenie | API Key | Critical |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Email Receiver

```yaml
receivers:
  - name: dba-email
    email_configs:
      - to: 'dba-oncall@gridcare.lab'
        send_resolved: true
```

### ตัวอย่างที่ 2: Slack Receiver

```yaml
receivers:
  - name: dba-slack
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/T000/B000/XXXX'
        channel: '#dba-alerts'
        send_resolved: true
        title: '[{{ .Status | toUpper }}] {{ .GroupLabels.alertname }}'
```

### ตัวอย่างที่ 3: Webhook Receiver

```yaml
receivers:
  - name: pager-critical
    webhook_configs:
      - url: 'http://pagerduty.local/api/alert'
        send_resolved: true
```

### ตัวอย่างที่ 4: ทดสอบด้วย `amtool`

```bash
amtool alert add alertname=TestAlert severity=warning instance="pg1:9187"
```

ผลลัพธ์:
```text
-- ส่ง Alert ไปยัง Receiver ที่ตรงกับ severity=warning
```

### ตัวอย่างที่ 5: ตรวจสอบว่า Alert ถึง Mailpit

```bash
# เปิด http://localhost:18025
# เห็นอีเมล [FIRING:1] TestAlert (pg1:9187)
```

## 12. สรุปย่อ จำง่าย
- **Email = SMTP + send_resolved**  
- **Slack = Webhook URL + channel**  
- **Webhook = HTTP POST**  
- **Pager = Service Key**  
- **Secret ต้องไม่อยู่ใน Git**  
- **Template ทำให้อ่านง่าย**

ประโยคจำ: **"Receiver ที่ดีคือ Receiver ที่ทำให้ Alert ถึงคนที่ต้องทำ"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- Alertmanager Receivers: https://prometheus.io/docs/alerting/latest/configuration/#receiver
- Slack Incoming Webhooks: https://api.slack.com/messaging/webhooks
- PagerDuty Integration: https://support.pagerduty.com/docs/prometheus
- GridCare Workshop Day 4: Lab 4.1

---

# บทที่ 57 Mailpit และการทดสอบอีเมล

## 1. เรื่อง
การทดสอบอีเมลจาก Alertmanager ด้วย Mailpit

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้ตั้ง Mailpit สำหรับทดสอบ Email  
2. เพื่อให้ตั้ง Alertmanager ให้ส่งไปที่ Mailpit  
3. เพื่อให้ตรวจสอบอีเมล  
4. เพื่อให้ใช้ Mailpit ใน Lab และ CI

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ตั้ง Mailpit บน Port 1025 (SMTP) และ 8025 (Web)  
- ตั้ง Alertmanager SMTP ไปที่ Mailpit  
- ทดสอบ Alert และตรวจอีเมล  
- ใช้ Mailpit เป็น Mail Catcher

## 4. เนื้อหาโดยย่อ
Mailpit เป็น Mail Catcher:
- SMTP บน Port 1025  
- Web UI บน Port 8025  
- เก็บอีเมลทั้งหมดใน Memory  
- เหมาะกับ Lab และ CI

## 5. ประโยชน์ที่ได้รับ
- ทดสอบ Email ได้โดยไม่ส่งจริง  
- ตรวจอีเมลได้  
- ใช้ใน CI ได้  
- ไม่ต้องมี SMTP จริง

## 6. ข้อควรระวัง
- **Mailpit ไม่ใช่ SMTP จริง**  
- **ใช้กับ Lab เท่านั้น**  
- **ไม่ควรใช้ใน Production**  
- **Web UI ควรจำกัด IP**

## 7. ข้อดี
- ง่าย  
- ใช้ใน CI ได้  
- ตรวจอีเมลได้

## 8. ข้อเสีย
- ไม่ใช่ SMTP จริง  
- ไม่มี Authentication

## 9. ข้อห้าม
- ห้ามใช้ Mailpit ใน Production  
- ห้ามเปิด Web UI ให้ Public  
- ห้ามใช้ Mailpit แทน SMTP จริง

## 10. รายละเอียด

### 10.1 ตรวจสอบ Mailpit

```bash
systemctl status mailpit --no-pager | head -3
```

ผลลัพธ์:
```text
● mailpit.service - Mailpit
     Loaded: loaded (/lib/systemd/system/mailpit.service; enabled)
     Active: active (running) since Tue 2026-11-04 09:00:00 +07
```

### 10.2 ตั้ง Alertmanager SMTP ไปที่ Mailpit

```yaml
global:
  smtp_smarthost: 'localhost:1025'
  smtp_from: 'alertmanager@gridcare.lab'
  smtp_require_tls: false
```

### 10.3 ทดสอบ Alert

```bash
amtool alert add alertname=TestAlert severity=warning instance="pg1:9187" \
  --alertmanager.url=http://localhost:9093
```

ผลลัพธ์:
```text
-- Alert ถูกส่งไปที่ Mailpit
```

### 10.4 ตรวจอีเมล

เปิด Browser: `http://localhost:18025`  
จะเห็นอีเมล `[FIRING:1] TestAlert (pg1:9187)`

### 10.5 ใช้ Mailpit ใน CI

```yaml
# docker-compose
services:
  mailpit:
    image: axllent/mailpit
    ports:
      - "1025:1025"
      - "8025:8025"
```

### 10.6 ตาราง Mailpit Port

| Port | ใช้ |
|---|---|
| 1025 | SMTP |
| 8025 | Web UI |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: ตั้ง Alertmanager

```yaml
global:
  smtp_smarthost: 'localhost:1025'
  smtp_from: 'alertmanager@gridcare.lab'
  smtp_require_tls: false
```

### ตัวอย่างที่ 2: ตรวจ Mailpit

```bash
curl -s http://localhost:8025/api/v1/messages | python3 -m json.tool | head -20
```

ผลลัพธ์:
```json
{
  "total": 3,
  "messages": [
    {
      "ID": "abc123",
      "Subject": "[FIRING:1] PostgresDown (pg1:9187)",
      "From": "alertmanager@gridcare.lab",
      "To": ["dba-oncall@gridcare.lab"]
    }
  ]
}
```

### ตัวอย่างที่ 3: Alert ถึง Mailpit

```text
Subject: [FIRING:1] PostgresDown (pg1:9187)
From: alertmanager@gridcare.lab
To: dba-oncall@gridcare.lab

[FIRING:1] PostgresDown (pg1:9187)

Alert: PostgresDown
Severity: critical
Instance: pg1:9187
Summary: PostgreSQL instance pg1:9187 down
Description: pg_up = 0 ต่อเนื่อง 1 นาที
Runbook: http://gridcare-infra/runbooks/C08-postgres-down.md
```

## 12. สรุปย่อ จำง่าย
- **Mailpit = Mail Catcher สำหรับ Lab**  
- **SMTP 1025, Web 8025**  
- **ตั้ง Alertmanager SMTP ไปที่ Mailpit**  
- **ตรวจอีเมลที่ Web UI**  
- **ไม่ใช้ใน Production**

ประโยคจำ: **"Mailpit ทำให้ทดสอบอีเมลได้โดยไม่ต้องส่งจริง"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- Mailpit: https://mailpit.axllent.org/
- GridCare Workshop Day 4: Lab 4.1

---

# บทที่ 58 Runbook URL และ Severity

## 1. เรื่อง
การกำหนด Runbook URL และ Severity ใน Alert Rule ให้เป็นมาตรฐานเดียวกัน

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้ทุก Alert มี Runbook  
2. เพื่อให้ Severity มีมาตรฐาน  
3. เพื่อให้ Runbook มีโครงสร้างที่อ่านง่าย  
4. เพื่อให้ On-call ทำงานได้เร็ว

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ออกแบบ Runbook URL Pattern  
- เขียน Runbook ที่มีโครงสร้าง  
- กำหนด Severity ที่ชัดเจน  
- ผูก Runbook กับ Alert

## 4. เนื้อหาโดยย่อ
Runbook ควรมี:
- ชื่อ Alert  
- Severity  
- Metric  
- Threshold  
- Steps  
- Escalation

Severity ควรมี:
- Critical  
- Warning  
- Info

## 5. ประโยชน์ที่ได้รับ
- On-call ตอบสนองเร็ว  
- ลด MTTR  
- ทำให้ Runbook มีมาตรฐาน  
- ทำให้ Audit ได้

## 6. ข้อควรระวัง
- **Runbook ที่เก่า** ทำให้ On-call สับสน  
- **Severity ที่ไม่ชัด** ทำให้ Critical ถูกกลบ  
- **Runbook ที่ไม่มีวันที่** ทำให้ไม่รู้ว่าอัปเดตล่าสุด  
- **Runbook ที่ไม่มีเจ้าของ** ทำให้ไม่มีคนดูแล

## 7. ข้อดี
- มาตรฐานเดียวกัน  
- ลด MTTR  
- Audit ได้

## 8. ข้อเสีย
- ต้อง Maintain  
- ต้อง Review เป็นระยะ

## 9. ข้อห้าม
- ห้าม Alert ที่ไม่มี Runbook  
- ห้าม Runbook ที่ไม่มีวันที่  
- ห้าม Runbook ที่ไม่มีเจ้าของ  
- ห้าม Severity ที่ไม่ตรงกับผลกระทบ

## 10. รายละเอียด

### 10.1 Runbook URL Pattern

```text
http://gridcare-infra/runbooks/<CARD>-<name>.md
```

ตัวอย่าง:
- `C01-lock-queue.md`  
- `C02-bloat-vacuum-wraparound.md`  
- `C03-connection-limit-locking.md`  
- `C04-disk-full.md`  
- `C05-bloat-vacuum-wraparound.md`  
- `C06-oom-temp-spill.md`  
- `C07-backup-recovery.md`  
- `C08-replication-lag-slot-failover.md`  
- `C09-oom-temp-spill.md`  
- `C10-security.md`  
- `C11-monitoring.md`  
- `C12-storage.md`

### 10.2 โครงสร้าง Runbook

```markdown
# C08 — PostgresDown

## Alert
- **Name:** PostgresDown
- **Severity:** critical
- **Metric:** pg_up
- **Threshold:** == 0 ต่อเนื่อง 1m
- **Owner:** DBA (Primary), DevOps (Secondary)
- **Last Reviewed:** 2026-11-01

## Symptoms
- pg_up = 0
- Connection refused
- Alertmanager firing

## Steps
1. ตรวจ `systemctl status postgresql@17-main`
2. ตรวจ `patronictl list`
3. ตรวจ `pg_lsclusters`
4. ตรวจ Log `/var/log/postgresql/postgresql-17-main.log`
5. ถ้า Patroni: ตรวจ etcd
6. ถ้า Patroni: ตรวจ `patronictl list` ว่ามี Leader
7. ถ้าไม่มี Leader: `patronictl failover`
8. ยืนยัน `pg_up = 1`

## Escalation
- 5 นาที: แจ้ง DevOps
- 15 นาที: แจ้ง Cloud Engineer
- 30 นาที: แจ้งหัวหน้าทีม

## Related Alerts
- PostgresConnectionsHigh (ถูก Inhibit)
- PostgresReplicationLagHigh (ถูก Inhibit)
```

### 10.3 Severity Matrix

| Severity | ผลกระทบ | MTTA | MTTR | Escalation |
|---|---|---|---|---|
| Critical | กระทบผู้ใช้หรือข้อมูล | ≤ 5 นาที | ≤ 30 นาที | Pager + Email + Slack |
| Warning | เสี่ยงจะเกิดปัญหา | ≤ 30 นาที | ≤ 4 ชั่วโมง | Slack + Email |
| Info | บันทึกเหตุการณ์ | ไม่กำหนด | ไม่กำหนด | Log Only |

### 10.4 Runbook ที่ดี

| องค์ประกอบ | มี |
|---|---|
| Alert Name | ✅ |
| Severity | ✅ |
| Metric | ✅ |
| Threshold | ✅ |
| Owner | ✅ |
| Steps | ✅ |
| Escalation | ✅ |
| Last Reviewed | ✅ |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Runbook PostgresDown

```markdown
# C08 — PostgresDown

## Alert
- **Name:** PostgresDown
- **Severity:** critical
- **Metric:** pg_up
- **Threshold:** == 0 ต่อเนื่อง 1m
- **Owner:** DBA (Primary), DevOps (Secondary)
- **Last Reviewed:** 2026-11-01

## Symptoms
- pg_up = 0
- Connection refused
- Alertmanager firing

## Steps
1. `systemctl status postgresql@17-main`
2. `patronictl list`
3. `pg_lsclusters`
4. `tail -n 50 /var/log/postgresql/postgresql-17-main.log`
5. ถ้า Patroni: ตรวจ etcd ด้วย `etcdctl endpoint health`
6. ถ้าไม่มี Leader: `patronictl failover gridcare --candidate pg2`
7. ยืนยัน `pg_up = 1`

## Escalation
- 5 นาที: DevOps
- 15 นาที: Cloud Engineer
- 30 นาที: หัวหน้าทีม
```

### ตัวอย่างที่ 2: Alert ที่มี Runbook

```yaml
- alert: PostgresDown
  expr: pg_up == 0
  for: 1m
  labels: {severity: critical, owner: dba}
  annotations:
    summary: "PostgreSQL instance {{ $labels.instance }} down"
    description: "pg_up = 0 ต่อเนื่อง 1 นาที"
    runbook_url: "http://gridcare-infra/runbooks/C08-postgres-down.md"
```

### ตัวอย่างที่ 3: ตรวจ Runbook Coverage

```bash
curl -s localhost:9090/api/v1/rules | python3 -c "
import sys,json
d=json.load(sys.stdin)
total=0
missing=0
for g in d['data']['groups']:
    for r in g['rules']:
        if 'alert' in r:
            total += 1
            if 'runbook_url' not in r.get('annotations', {}):
                missing += 1
                print('MISSING:', r['name'])
print(f'Total: {total}, Missing: {missing}')
"
```

ผลลัพธ์:
```text
Total: 23, Missing: 0
```

## 12. สรุปย่อ จำง่าย
- **ทุก Alert ต้องมี Runbook**  
- **Runbook URL Pattern = `<CARD>-<name>.md`**  
- **Severity Matrix: Critical / Warning / Info**  
- **Runbook ต้องมี Owner และ Last Reviewed**  
- **Runbook ต้องมี Steps และ Escalation**

ประโยคจำ: **"Runbook ที่ดีคือ Runbook ที่ On-call เปิดอ่านแล้วทำได้ทันที"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- Google SRE Book — Being On-Call: https://sre.google/sre-book/being-on-call/
- PagerDuty Runbook: https://response.pagerduty.com/
- GridCare Workshop: `monitoring/runbooks/`

---

# บทที่ 59 Alert Fatigue

## 1. เรื่อง
Alert Fatigue และวิธีลด Alert ที่ไม่ actionable

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจ Alert Fatigue  
2. เพื่อให้วัด Alert Fatigue  
3. เพื่อให้ลด Alert ที่ไม่ actionable  
4. เพื่อให้ทบทวน Alert เป็นระยะ

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- อธิบาย Alert Fatigue  
- วัด Alert Fatigue ด้วย KPI  
- ลด Alert ที่ไม่ actionable  
- ตั้ง Alert Review Process

## 4. เนื้อหาโดยย่อ
**Alert Fatigue** = สภาวะที่ทีมละเลย Alert เพราะมีมากเกินไปหรือไม่ actionable  
สาเหตุ:
- Alert ที่ไม่ actionable  
- Alert ที่ดังซ้ำ  
- Alert ที่ไม่มี Runbook  
- Alert ที่ Severity ไม่ชัด  
- Alert ที่ไม่มีเจ้าของ

วิธีลด:
- ทบทวน Alert เป็นระยะ  
- ลบ Alert ที่ไม่ actionable  
- ปรับ `for:`  
- ปรับ Threshold  
- ใช้ Inhibition

## 5. ประโยชน์ที่ได้รับ
- ลด Alert ที่ไม่จำเป็น  
- ทำให้ On-call ไม่ละเลย  
- ลด MTTA และ MTTR  
- ทำให้ทีมมีคุณภาพชีวิตดีขึ้น

## 6. ข้อควรระวัง
- **Alert ที่ไม่ actionable** ทำให้ทีมเพิกเฉย  
- **Alert ที่ดังซ้ำ** ทำให้ทีม R&eacute;  
- **Alert ที่ไม่มี Runbook** ทำให้ทีมไม่รู้จะทำอะไร  
- **Alert ที่ Severity ไม่ชัด** ทำให้ Critical ถูกกลบ

## 7. ข้อดี
- ลด Alert ที่ไม่จำเป็น  
- ทำให้ On-call มีคุณภาพชีวิตดีขึ้น  
- ลด MTTA และ MTTR

## 8. ข้อเสีย
- ต้องลงทุนเวลาในการทบทวน  
- ต้องมีข้อมูล

## 9. ข้อห้าม
- ห้าม Alert ที่ไม่ actionable  
- ห้าม Alert ที่ไม่มี Runbook  
- ห้าม Alert ที่ไม่มีเจ้าของ  
- ห้าม Alert ที่ดังซ้ำโดยไม่มีอะไรเปลี่ยน  
- ห้ามปิด Alert โดยไม่บันทึกเหตุผล

## 10. รายละเอียด

### 10.1 KPI ของ Alert Fatigue

| KPI | เป้าหมาย |
|---|---|
| % Alert ที่มี Runbook | 100% |
| % Alert ที่มีเจ้าของ | 100% |
| False Positive Rate | ≤ 10% |
| Alert ที่ Silence เกิน 7 วัน | 0 |
| Alert ที่ไม่ Reviewed 90 วัน | 0 |
| Alert ที่ Firing ซ้ำโดยไม่มี Action | 0 |

### 10.2 Alert Review Process

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

### 10.3 วิธีลด Alert Fatigue

| วิธี | ใช้ |
|---|---|
| ลบ Alert ที่ไม่ actionable | ทบทวน |
| ปรับ `for:` | ลด False Positive |
| ปรับ Threshold | ลด Alert ที่ไม่จำเป็น |
| ใช้ Inhibition | ลด Alert ซ้ำ |
| ใช้ Silencing | Maintenance |
| ใช้ Runbook | ทำให้ On-call ทำงานได้ |

### 10.4 Alert ที่ควรลบ

- Alert ที่ดังทุกวันแต่ไม่มี Action  
- Alert ที่ไม่มี Runbook  
- Alert ที่ไม่มีเจ้าของ  
- Alert ที่ Cardinality สูง  
- Alert ที่ซ้ำกับ Alert อื่น  
- Alert ที่ดังจาก Maintenance

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Alert ที่ควรลบ

```yaml
# ผิด — ดังทุกวัน ไม่มี Action
- alert: PostgresWarning
  expr: pg_stat_activity_count > 0
  for: 0s
  labels:
    severity: warning
  annotations:
    summary: "มี session"
```

### ตัวอย่างที่ 2: Alert ที่แก้แล้ว

```yaml
# ถูก — มี Action
- alert: PostgresConnectionsHigh
  expr: |
    sum by (instance) (pg_stat_activity_count{datname="gridcare"})
    / max by (instance) (pg_settings_max_connections) * 100 > 80
  for: 5m
  labels: {severity: warning, owner: dba}
  annotations:
    summary: "Connection ใช้งานเกิน 80%"
    description: "ตรวจ PgBouncer, session ค้าง, idle in transaction"
    runbook_url: "http://gridcare-infra/runbooks/C03-connection-limit-locking.md"
```

### ตัวอย่างที่ 3: วัด Alert Fatigue

```bash
curl -s localhost:9090/api/v1/rules | python3 -c "
import sys,json
d=json.load(sys.stdin)
total=0
missing_runbook=0
missing_owner=0
for g in d['data']['groups']:
    for r in g['rules']:
        if 'alert' in r:
            total += 1
            if 'runbook_url' not in r.get('annotations', {}):
                missing_runbook += 1
            if 'owner' not in r.get('labels', {}):
                missing_owner += 1
print(f'Total: {total}')
print(f'Missing Runbook: {missing_runbook}')
print(f'Missing Owner: {missing_owner}')
"
```

ผลลัพธ์:
```text
Total: 23
Missing Runbook: 0
Missing Owner: 0
```

### ตัวอย่างที่ 4: ตรวจ Silence ค้าง

```bash
amtool silence query --alertmanager.url=http://localhost:9093
```

ผลลัพธ์:
```text
ID                                    Matchers                Ends At                  Created By  Comment
a3b1c2d4-e5f6-7890-abcd-ef1234567890  alertname=Postgres.*   2026-11-05 15:30:00 UTC  student     Maintenance: upgrade
```

## 12. สรุปย่อ จำง่าย
- **Alert Fatigue = ทีมละเลย Alert เพราะมีมากเกินไป**  
- **สาเหตุ:** Alert ไม่ actionable, ดังซ้ำ, ไม่มี Runbook, Severity ไม่ชัด  
- **วิธีลด:** ทบทวน, ลบ, ปรับ `for:`, ปรับ Threshold, ใช้ Inhibition  
- **KPI:** 100% มี Runbook, 100% มี Owner, FP ≤ 10%  
- **ทบทวนทุกเดือน**

ประโยคจำ: **"Alert ที่ดีคือ Alert ที่ทำให้ทีมทำงาน ไม่ใช่ทำให้ทีมละเลย"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- Google SRE Book — Monitoring: https://sre.google/sre-book/monitoring-distributed-systems/
- Rob Ewaschuk — My Philosophy on Alerting: https://docs.google.com/document/d/199PqyG3UsyXlwieHaqbGiWVa8eMWi8zzAn0YfcApr8Q/
- GridCare Workshop Day 4: Workshop Day 4 ขั้นที่ 1

---

# บทที่ 60 Incident Notification Workflow

## 1. เรื่อง
Workflow การแจ้งเตือน Incident ตั้งแต่ Alert Firing จนถึง Incident Record และ PSR

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจ Workflow การแจ้งเตือน  
2. เพื่อให้ทุก Alert มี Incident Record  
3. เพื่อให้ On-call ทำงานตามขั้นตอน  
4. เพื่อให้ PSR มีข้อมูลครบ

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- อธิบาย Workflow การแจ้งเตือน  
- สร้าง Incident Record  
- ใช้ Handover Note  
- ใช้ Runbook และ Escalation

## 4. เนื้อหาโดยย่อ
Workflow:
1. Alert Firing  
2. Alertmanager ส่งไปยัง Receiver  
3. On-call รับแจ้ง  
4. เปิด Runbook  
5. สร้าง Incident Record  
6. แก้ไข  
7. Resolve  
8. PSR

## 5. ประโยชน์ที่ได้รับ
- ลด MTTA และ MTTR  
- ทุก Incident มีบันทึก  
- PSR มีข้อมูลครบ  
- Handover ราบรื่น

## 6. ข้อควรระวัง
- **ไม่สร้าง Incident Record** ทำให้ PSR ไม่มีข้อมูล  
- **ไม่ใช้ Runbook** ทำให้ตอบสนองช้า  
- **ไม่ Escalate** ทำให้ Incident ลุกลาม  
- **Handover ที่ไม่มี Note** ทำให้ข้อมูลขาด

## 7. ข้อดี
- มาตรฐานเดียวกัน  
- PSR มีข้อมูลครบ  
- ลด MTTA และ MTTR

## 8. ข้อเสีย
- ต้องลงทุนทำ Incident Record  
- ต้องมี Handover Process

## 9. ข้อห้าม
- ห้าม On-call ที่ไม่เปิด Runbook  
- ห้าม Incident ที่ไม่มี Record  
- ห้าม Handover ที่ไม่มี Note  
- ห้าม Escalate ที่ไม่มีการบันทึก

## 10. รายละเอียด

### 10.1 Workflow

```text
Alert Firing
   │
   ▼
Alertmanager → Receiver
   │
   ▼
On-call รับแจ้ง (≤ 5 นาที)
   │
   ▼
เปิด Runbook
   │
   ▼
สร้าง Incident Record
   │
   ▼
แก้ไข
   │
   ├── ถ้าแก้ไม่ได้ → Escalate
   │
   ▼
Resolve
   │
   ▼
PSR (≤ 48 ชั่วโมง)
```

### 10.2 Incident Record Template

```markdown
# Incident Record

## ข้อมูลเบื้องต้น
- **Incident ID:** INC-2026-11-05-001
- **Started:** 2026-11-05 13:15:23
- **Detected:** 2026-11-05 13:16:00
- **Resolved:** 2026-11-05 13:17:00
- **Duration:** 1 นาที 37 วินาที
- **Severity:** critical

## Alert
- **Name:** PostgresRecentlyRestarted
- **Instance:** pg2:9187
- **Runbook:** C08-postgres-down.md

## Symptoms
- pg2 Restart
- Alert ดัง

## Root Cause
- Patroni restart ตาม Plan (planned maintenance)
- ไม่ใช่ Incident

## Actions Taken
1. ยืนยันผล
2. ปิด Alert
3. ไม่ต้อง PSR

## Handover
- ไม่ต้อง Handover (planned)

## PSR
- ไม่ต้องทำ (planned maintenance)
```

### 10.3 Handover Note

```markdown
# Handover Note

## From: DBA A
## To: DBA B
## Date: 2026-11-05 18:00

## Active Incidents
- ไม่มี

## Alerts ที่ Silence อยู่
- PostgresXidAgeWarning (pg1:9187) — Maintenance ถึง 2026-11-06 08:00

## สิ่งที่ต้องติดตาม
- pg2 กำลัง Rebuild Replica (คาดเสร็จ 19:00)
- Backup ที่รัน 17:00 ต้องตรวจ

## Recent Changes
- Upgrade PostgreSQL 17→18 (2026-11-06 10:00)
```

### 10.4 Escalation Matrix

| ระดับ | เวลา | Escalate ไปที่ |
|---|---|---|
| L1 | 5 นาที | On-call DBA |
| L2 | 15 นาที | DevOps + Cloud Engineer |
| L3 | 30 นาที | หัวหน้าทีม |
| L4 | 60 นาที | Management |

### 10.5 ตาราง Receiver

| Severity | ช่องทาง | Escalation |
|---|---|---|
| Critical | Pager + Email + Slack | 5 นาที |
| Warning | Slack + Email | 30 นาที |
| Info | Log Only | ไม่มี |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Incident Record ที่ดี

```markdown
# Incident Record

## ข้อมูลเบื้องต้น
- **Incident ID:** INC-2026-11-05-002
- **Started:** 2026-11-05 14:30:15
- **Detected:** 2026-11-05 14:30:46
- **Resolved:** 2026-11-05 14:31:00
- **Duration:** 45 วินาที
- **Severity:** critical

## Alert
- **Name:** PostgresDown
- **Instance:** pg1:9187
- **Runbook:** C08-postgres-down.md

## Symptoms
- pg1 Down
- Application Connection refused
- PgBouncer คืน Connection refused

## Root Cause
- pg1 ถูก SIGKILL
- Patroni failover ไป pg2

## Actions Taken
1. Patroni promote pg2 อัตโนมัติ
2. HAProxy สลับ Health Check
3. ยืนยัน pg_up = 1 บน pg2

## Handover
- ไม่ต้อง Handover (resolved)

## PSR
- Action: ตรวจสอบว่า SIGKILL มาจากอะไร
- Action: เพิ่ม Alert "OOMKilled"
```

### ตัวอย่างที่ 2: Alert ที่ Firing

```bash
curl -s localhost:9090/api/v1/alerts | python3 -m json.tool | grep -E '"alertname"|"state"'
```

ผลลัพธ์:
```text
"alertname": "PostgresDown",
"state": "firing"
```

### ตัวอย่างที่ 3: Alert ที่ Resolve

```bash
curl -s localhost:9090/api/v1/alerts | python3 -m json.tool | grep -E '"alertname"|"state"'
```

ผลลัพธ์:
```text
"alertname": "PostgresDown",
"state": "resolved"
```

### ตัวอย่างที่ 4: Mailpit ที่มีอีเมล Firing และ Resolved

```text
[FIRING:1] PostgresDown (pg1:9187)
[RESOLVED] PostgresDown (pg1:9187)
```

## 12. สรุปย่อ จำง่าย
- **Alert Firing → Runbook → Incident Record → Resolve → PSR**  
- **ทุก Incident มี Record**  
- **ทุก Handover มี Note**  
- **Escalation Matrix ชัดเจน**  
- **PSR ภายใน 48 ชั่วโมง**  
- **Severity กำหนดช่องทาง**

ประโยคจำ: **"Workflow ที่ดีคือ Workflow ที่ทำให้ทุก Incident มีร่องรอยและบทเรียน"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- Google SRE Book — Managing Incidents: https://sre.google/sre-book/managing-incidents/
- PagerDuty Incident Response: https://response.pagerduty.com/
- GridCare Workshop: Incident Record Template

---

## สรุปส่วนที่ 6 (บทที่ 51–60)

| บท | แก่นของบท | ใช้ต่อในส่วน |
|---|---|---|
| 51 | หลักการออกแบบ Alert | Alert Rule |
| 52 | Prometheus Alert Rules | Alertmanager |
| 53 | promtool check และ test | CI/CD |
| 54 | Alertmanager Configuration | Routing |
| 55 | Routing, Grouping, Inhibition | Alert Design |
| 56 | Email, Slack, Webhook | Receiver |
| 57 | Mailpit | Lab, CI |
| 58 | Runbook URL และ Severity | Incident |
| 59 | Alert Fatigue | Continuous Improvement |
| 60 | Incident Notification Workflow | SRE |

---
 