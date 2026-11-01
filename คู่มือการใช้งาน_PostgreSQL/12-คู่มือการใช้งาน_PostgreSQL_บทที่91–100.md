# บทที่ 91–100

> หนังสือ: คู่มือการใช้งาน PostgreSQL สำหรับ DevOps Engineer, Cloud Engineer และ DBA  
> ส่วนที่ 10 Troubleshooting และ Game Day  
> โทน: ทางการ กระชับ เน้นใช้งานจริง

---

# บทที่ 91 ลำดับ 15 นาทีแรก

## 1. เรื่อง
ลำดับขั้นตอนการตอบสนอง Incident ภายใน 15 นาทีแรก สำหรับทีม DBA, DevOps และ Cloud Engineer

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้ทุกทีมมีขั้นตอนเดียวกันใน 15 นาทีแรก  
2. เพื่อให้ตรวจพบ Root Cause ได้เร็ว  
3. เพื่อให้ Handover ราบรื่น  
4. เพื่อให้ Incident Record มีข้อมูลครบ

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ทำตามลำดับ 15 นาทีแรกได้  
- แยก "ล่ม" กับ "ช้า" ได้  
- ระบุ Symptom, Root Cause และ Action  
- Escalate ได้ถูกเวลา

## 4. เนื้อหาโดยย่อ
ลำดับ 15 นาทีแรก:
1. **นาที 0–2:** รับแจ้ง, ยืนยัน Symptom  
2. **นาที 2–5:** ตรวจ Availability  
3. **นาที 5–8:** ตรวจ Resource  
4. **นาที 8–12:** ตรวจ Database  
5. **นาที 12–15:** ตัดสินใจ Escalate

## 5. ประโยชน์ที่ได้รับ
- ลด MTTA  
- ลด MTTR  
- มีมาตรฐานเดียวกัน  
- ผ่าน Audit

## 6. ข้อควรระวัง
- **ห้ามแก้ก่อนยืนยัน Symptom**  
- **ห้าม Kill Session ก่อนหาสาเหตุ**  
- **ห้าม Restart ก่อน Backup**  
- **ห้าม Escalate ช้า**  
- **ต้องบันทึกทุกขั้นตอน**

## 7. ข้อดี
- มาตรฐานเดียวกัน  
- ลด MTTA/MTTR  
- ผ่าน Audit

## 8. ข้อเสีย
- ต้องฝึก  
- ต้องมี Runbook

## 9. ข้อห้าม
- ห้ามแก้โดยไม่ยืนยัน Symptom  
- ห้าม Restart โดยไม่ตรวจ  
- ห้าม Escalate โดยไม่มี Handover  
- ห้ามลืม Incident Record

## 10. รายละเอียด

### 10.1 ลำดับ 15 นาทีแรก

**นาที 0–2: รับแจ้ง**

```bash
# ตรวจ Alert
curl -s localhost:9090/api/v1/alerts | python3 -m json.tool | grep -E '"alertname"|"state"|"activeAt"'

# ตรวจ Alertmanager
amtool alert query --alertmanager.url=http://localhost:9093
```

**นาที 2–5: ตรวจ Availability**

```bash
# PostgreSQL Up
pg_isready -h 127.0.0.1 -p 5000

# Patroni
patronictl list

# pg_up
curl -s localhost:9187/metrics | grep '^pg_up'
```

**นาที 5–8: ตรวจ Resource**

```bash
df -hT /
free -h
nproc
vmstat 2 3
```

**นาที 8–12: ตรวจ Database**

```sql
SELECT pid, usename, application_name, state, wait_event_type, wait_event,
       now() - xact_start AS xact_age, pg_blocking_pids(pid) AS blocked_by,
       left(query, 60)
FROM pg_stat_activity
WHERE state <> 'idle'
ORDER BY xact_start;

SELECT pg_size_pretty(sum(size)) FROM pg_ls_waldir();
SELECT slot_name, active, wal_status FROM pg_replication_slots;
SELECT failed_count, last_archived_time FROM pg_stat_archiver;
SELECT datname, age(datfrozenxid) FROM pg_database ORDER BY 2 DESC LIMIT 3;
SELECT application_name, write_lag, flush_lag, replay_lag FROM pg_stat_replication;
SELECT calls, round(total_exec_time::numeric), left(query, 60)
FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 3;
```

**นาที 12–15: ตัดสินใจ**

```text
ถ้า PostgreSQL Down → Escalate ไปที่ DBA + DevOps
ถ้า Lock Queue → ใช้ pg_cancel_backend หรือ pg_terminate_backend
ถ้า Disk Full → Escalate ไปที่ Cloud Engineer
ถ้า Replication Lag → ตรวจ Network + WAL
ถ้า OOM → Escalate ไปที่ Cloud Engineer
ถ้า Data Loss → ตัดสินใจ PITR
```

### 10.2 Decision Tree

```text
Symptom: แอปเชื่อมต่อไม่ได้
   │
   ├── pg_isready = accepting?
   │    ├── ใช่ → ตรวจ Lock/Query
   │    └── ไม่ → ตรวจ pg_up
   │
   ├── pg_up = 1?
   │    ├── ใช่ → ตรวจ Resource (CPU, Disk, Memory)
   │    └── ไม่ → ตรวจ Patroni + etcd
   │
   └── Patroni มี Leader?
        ├── ใช่ → ตรวจ Replication
        └── ไม่ → Failover
```

### 10.3 Handover Note

```markdown
# Handover Note

## From: DBA A
## To: DBA B
## Date: 2026-11-05 14:30

## Active Incidents
- INC-2026-11-05-001: PostgresDown (pg1:9187)
  - Symptom: pg1 ถูก SIGKILL
  - Action: Patroni failover ไป pg2
  - Status: Resolved

## สิ่งที่ต้องติดตาม
- pg1 กำลัง Rebuild Replica
- Backup ที่รัน 17:00 ต้องตรวจ
```

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Incident "แอปเชื่อมต่อไม่ได้"

```text
14:30:15  Alert PostgresDown (firing)
14:30:20  ตรวจ pg_isready → ไม่รับ
14:30:25  ตรวจ patronictl list → ไม่มี Leader
14:30:30  ตรวจ etcd → 2/3 healthy
14:30:35  ตรวจ pg_up → 0
14:30:40  Escalate ไปที่ DBA Lead
14:31:00  Patroni promote pg2
14:31:15  ยืนยัน pg_up = 1 บน pg2
14:31:20  เปิด Incident Record
```

### ตัวอย่างที่ 2: Incident "แอปช้า"

```text
14:30:15  Alert PostgresConnectionsHigh (firing)
14:30:20  ตรวจ pg_stat_activity → พบ idle in transaction 150
14:30:25  ตรวจ pg_blocking_pids → batch_A ถือ Lock
14:30:30  Escalate ไปที่ DBA
14:31:00  pg_cancel_backend(7665)
14:31:30  pg_terminate_backend(7659)
14:32:00  Alert Resolved
```

### ตัวอย่างที่ 3: Incident "Disk เต็ม"

```text
14:30:15  Alert DiskSpaceLow (firing)
14:30:20  ตรวจ df -h → 95%
14:30:25  Escalate ไปที่ Cloud Engineer
14:30:30  ตรวจ pg_ls_waldir → 5 GB
14:30:35  ตรวจ Archive Status → failed
14:30:40  ตรวจ MinIO → Down
14:31:00  Cloud Engineer แก้ MinIO
14:31:30  WAL Archive ทำงาน
14:32:00  Alert Resolved
```

### ตัวอย่างที่ 4: Incident Record

```markdown
# Incident Record

## ข้อมูลเบื้องต้น
- **Incident ID:** INC-2026-11-05-001
- **Started:** 2026-11-05 14:30:15
- **Detected:** 2026-11-05 14:30:20
- **Resolved:** 2026-11-05 14:32:00
- **Duration:** 1 นาที 45 วินาที
- **Severity:** critical

## Alert
- **Name:** PostgresDown
- **Instance:** pg1:9187
- **Runbook:** C08-postgres-down.md

## Root Cause
- pg1 ถูก SIGKILL
- Patroni failover ไป pg2

## Actions Taken
1. ตรวจ Patroni → ไม่มี Leader
2. Escalate ไปที่ DBA Lead
3. Patroni promote pg2 อัตโนมัติ
4. ยืนยัน pg_up = 1 บน pg2
```

## 12. สรุปย่อ จำง่าย
- **นาที 0–2: รับแจ้ง**  
- **นาที 2–5: ตรวจ Availability**  
- **นาที 5–8: ตรวจ Resource**  
- **นาที 8–12: ตรวจ Database**  
- **นาที 12–15: ตัดสินใจ Escalate**  
- **ทุกขั้นตอนต้องบันทึก**

ประโยคจำ: **"15 นาทีแรกตัดสินทั้ง Incident"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- Google SRE Book — Managing Incidents: https://sre.google/sre-book/managing-incidents/
- PagerDuty Incident Response: https://response.pagerduty.com/
- GridCare Workshop Day 5: Lab 3.1

---

# บทที่ 92 แยก "ล่ม" กับ "ช้า"

## 1. เรื่อง
การแยกแยะ Incident ประเภท "ล่ม" (Down) กับ "ช้า" (Slow) เพื่อเลือกวิธีแก้ที่ถูกต้อง

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้แยก Symptom ได้  
2. เพื่อให้เลือก Runbook ถูก  
3. เพื่อให้ลดเวลา S troubleshooting  
4. เพื่อให้ Handover ราบรื่น

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- แยก "ล่ม" กับ "ช้า" ได้  
- เลือก Runbook ที่ถูก  
- ใช้ Metric ที่เหมาะ  
- Escalate ถูกทีม

## 4. เนื้อหาโดยย่อ
**ล่ม (Down)** = ระบบไม่ตอบสนอง, Connection refused  
**ช้า (Slow)** = ระบบตอบสนองแต่ Latency สูง

| ประเภท | Symptom | Metric |
|---|---|---|
| ล่ม | Connection refused, Timeout | `pg_up = 0` |
| ช้า | Latency สูง, TPS ต่ำ | `pg_stat_statements`, Lock |

## 5. ประโยชน์ที่ได้รับ
- แยก Symptom ได้  
- เลือก Runbook ถูก  
- ลด MTTR

## 6. ข้อควรระวัง
- **"ช้า" อาจกลายเป็น "ล่ม"**  
- **"ล่ม" อาจเกิดจาก "ช้า" สะสม**  
- **ต้องตรวจทั้งสอง**  
- **อย่าด่วน Restart**

## 7. ข้อดี
- แยกได้  
- เลือก Runbook ถูก  
- ลด MTTR

## 8. ข้อเสีย
- ต้องฝึก  
- ต้องมี Metric

## 9. ข้อห้าม
- ห้าม Restart เมื่อ "ช้า"  
- ห้ามรอเมื่อ "ล่ม"  
- ห้ามแก้ก่อนยืนยัน Symptom  
- ห้ามลืม Incident Record

## 10. รายละเอียด

### 10.1 ตารางเปรียบเทียบ

| มิติ | ล่ม | ช้า |
|---|---|---|
| Symptom | Connection refused, Timeout | Latency สูง, TPS ต่ำ |
| `pg_isready` | No response | Accepting connections |
| `pg_up` | 0 | 1 |
| `pg_stat_activity` | ไม่มี Session | Session ค้าง |
| Root Cause | Process ตาย, Disk เต็ม, OOM | Lock, Query ช้า, Disk I/O |
| Runbook | C08 (PostgresDown) | C01, C03, C06 |
| ทีม | DBA + DevOps + Cloud | DBA |

### 10.2 Decision Tree

```text
Symptom: แอปแจ้งปัญหา
   │
   ▼
pg_isready = accepting?
   │
   ├── ไม่ → "ล่ม"
   │         │
   │         ├── pg_up = 0?
   │         │    ├── ใช่ → ตรวจ Process + Disk + Memory
   │         │    └── ไม่ → ตรวจ Exporter
   │         │
   │         └── Patroni มี Leader?
   │              ├── ใช่ → ตรวจ Network
   │              └── ไม่ → Failover
   │
   └── ใช่ → "ช้า"
              │
              ├── Lock?
              │    ├── ใช่ → pg_cancel_backend
              │    └── ไม่ → ตรวจ pg_stat_statements
              │
              ├── Disk I/O?
              │    ├── ใช่ → ตรวจ Bloat + Cache
              │    └── ไม่ → ตรวจ CPU + Memory
              │
              └── Query ช้า?
                   ├── ใช่ → EXPLAIN
                   └── ไม่ → ตรวจ Network
```

### 10.3 Metric ที่ใช้แยก

| Metric | ล่ม | ช้า |
|---|---|---|
| `pg_up` | 0 | 1 |
| `pg_stat_activity_count` | 0 | สูง |
| `pg_stat_activity_max_tx_duration` | - | สูง |
| `pg_locks_count` | - | สูง |
| `pg_stat_database_xact_commit` | 0 | ลดลง |
| `node_filesystem_avail_bytes` | 0 | ต่ำ |
| `node_memory_MemAvailable_bytes` | 0 | ต่ำ |

### 10.4 ตัวอย่าง Runbook

| Runbook | ล่ม | ช้า |
|---|---|---|
| C01 Lock Queue | ❌ | ✅ |
| C03 Connection Full | ❌ | ✅ |
| C04 Disk Full | ✅ | ✅ |
| C05 XID Wraparound | ⚠️ | ⚠️ |
| C06 OOM | ✅ | ✅ |
| C07 Backup | ❌ | ⚠️ |
| C08 PostgresDown | ✅ | ❌ |
| C09 Temp Spill | ❌ | ✅ |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Incident "ล่ม"

```text
Symptom: Connection refused
pg_isready: No response
pg_up: 0
patronictl list: ไม่มี Leader
Root Cause: pg1 ถูก SIGKILL
Action: Patroni failover ไป pg2
Runbook: C08
```

### ตัวอย่างที่ 2: Incident "ช้า"

```text
Symptom: Latency สูง
pg_isready: Accepting
pg_up: 1
pg_stat_activity: idle in transaction 150
pg_blocking_pids: batch_A ถือ Lock
Root Cause: Long transaction
Action: pg_cancel_backend + pg_terminate_backend
Runbook: C01, C03
```

### ตัวอย่างที่ 3: Incident "ช้า" ที่กลายเป็น "ล่ม"

```text
14:30  pg_up = 1 แต่ Latency สูง
14:35  Connection เต็ม
14:40  pg_up = 0
14:45  Restart PostgreSQL
```

> ⚠️ ถ้าแก้ "ช้า" ตั้งแต่ 14:30 จะไม่กลายเป็น "ล่ม"

### ตัวอย่างที่ 4: Decision Tree

```text
Symptom: TPS ลดจาก 149 → 50
pg_isready: Accepting
pg_up: 1
pg_stat_activity: idle in transaction 200
Root Cause: idle in transaction จาก pgbench -C
Action: ตั้ง idle_in_transaction_session_timeout
```

## 12. สรุปย่อ จำง่าย
- **ล่ม = ไม่ตอบสนอง**  
- **ช้า = ตอบสนองแต่ Latency สูง**  
- **`pg_isready` แยกได้**  
- **`pg_up` แยกได้**  
- **"ช้า" อาจกลายเป็น "ล่ม"**  
- **Runbook ต่างกัน**

ประโยคจำ: **"แยกให้ออกก่อนแก้ จะประหยัดเวลาและลด Downtime"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — Monitoring: https://www.postgresql.org/docs/17/monitoring.html
- Google SRE Book: https://sre.google/sre-book/
- GridCare Workshop Day 5: Lab 3.1

---

# บทที่ 93 Connection Full

## 1. เรื่อง
การแก้ไขปัญหา Connection Full ใน PostgreSQL

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจสาเหตุ Connection Full  
2. เพื่อให้ตรวจสอบ Session  
3. เพื่อให้แก้ไขได้อย่างถูกต้อง  
4. เพื่อให้ป้องกันการเกิดซ้ำ

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ตรวจสอบ Connection  
- หา Root Cause  
- แก้ไขชั่วคราวและถาวร  
- ตั้ง Alert

## 4. เนื้อหาโดยย่อ
สาเหตุ Connection Full:
- PgBouncer ไม่ทำงาน  
- Session ค้าง  
- idle in transaction  
- Connection leak จากแอป  
- `max_connections` ต่ำเกินไป

## 5. ประโยชน์ที่ได้รับ
- แก้ไขเร็ว  
- ป้องกันการเกิดซ้ำ  
- ลด Downtime

## 6. ข้อควรระวัง
- **ห้ามเพิ่ม `max_connections` โดยไม่ตรวจ Memory**  
- **ห้าม Kill Session โดยไม่หาสาเหตุ**  
- **ต้องตั้ง `idle_in_transaction_session_timeout`**  
- **ต้องใช้ PgBouncer**

## 7. ข้อดี
- แก้ไขเร็ว  
- ป้องกันได้  
- ลด Downtime

## 8. ข้อเสีย
- ต้องตรวจ Session  
- ต้องตั้งค่า

## 9. ข้อห้าม
- ห้ามเพิ่ม `max_connections` สูงเกิน Memory  
- ห้าม Kill Session ที่เป็น Owner  
- ห้ามปิด PgBouncer เพื่อแก้  
- ห้ามใช้ Superuser กับแอป

## 10. รายละเอียด

### 10.1 ตรวจสอบ Connection

```sql
SELECT state, count(*) FROM pg_stat_activity GROUP BY state;
```

ผลลัพธ์:
```text
        state        | count 
---------------------+-------
 active              |    12
 idle                |    45
 idle in transaction |   143
(3 rows)
```

### 10.2 ตรวจสอบ `max_connections`

```sql
SHOW max_connections;
```

ผลลัพธ์:
```text
 max_connections 
-----------------
 100
```

```sql
SELECT 143 + 45 + 12 AS total_connections;
```

ผลลัพธ์:
```text
 total_connections 
-------------------
               200
```

> ⚠️ 200 > 100 = Connection Full

### 10.3 หา Session ที่ค้าง

```sql
SELECT pid, usename, application_name, state,
       now() - state_change AS idle_for,
       now() - xact_start AS xact_age,
       left(query, 60)
FROM pg_stat_activity
WHERE state = 'idle in transaction'
ORDER BY state_change;
```

ผลลัพธ์:
```text
  pid  |  usename   | application_name |        state        | idle_for  | xact_age  |                left                
-------+------------+------------------+---------------------+-----------+-----------+------------------------------------
 12345 | billing_app| pgbench          | idle in transaction | 00:05:23  | 00:05:23  | SELECT count(*) FROM gridcare.bills;
```

### 10.4 ตรวจสอบ PgBouncer

```bash
sudo systemctl status pgbouncer --no-pager | head -3
psql "host=127.0.0.1 port=6432 dbname=pgbouncer user=pgbouncer_admin" -c "SHOW POOLS;"
```

ผลลัพธ์:
```text
 database  |   user      | cl_active | cl_waiting | sv_active | sv_idle 
-----------+-------------+-----------+------------+-----------+---------
 gridcare  | billing_app |        50 |          0 |        20 |       0 
```

### 10.5 แก้ไขชั่วคราว

```sql
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle in transaction'
  AND now() - state_change > interval '5 minutes';
```

ผลลัพธ์:
```text
 pg_terminate_backend 
----------------------
 t
 t
 t
```

### 10.6 แก้ไขถาวร

**1. ตั้ง `idle_in_transaction_session_timeout`:**
```sql
ALTER ROLE billing_app SET idle_in_transaction_session_timeout = '60s';
ALTER ROLE callcenter_ro SET idle_in_transaction_session_timeout = '30s';
```

**2. ใช้ PgBouncer:**
```ini
pool_mode = transaction
max_db_connections = 40
```

**3. เพิ่ม `max_connections` (ถ้าจำเป็น):**
```sql
ALTER SYSTEM SET max_connections = 200;
```

> ⚠️ ต้อง Restart

### 10.7 Alert

```yaml
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

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Connection Full

```sql
SELECT state, count(*) FROM pg_stat_activity GROUP BY state;
```

ผลลัพธ์:
```text
        state        | count 
---------------------+-------
 idle in transaction |   143
```

```sql
-- Kill
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle in transaction'
  AND now() - state_change > interval '5 minutes';
```

### ตัวอย่างที่ 2: ตรวจสอบ PgBouncer

```bash
psql "host=127.0.0.1 port=6432 dbname=pgbouncer user=pgbouncer_admin" -c "SHOW POOLS;"
```

ผลลัพธ์:
```text
 gridcare  | billing_app |        50 |          0 |        20 |       0 
```

> ✅ `cl_active = 50` แต่ `sv_active + sv_idle = 20` (น้อยกว่ามาก)

### ตัวอย่างที่ 3: ตั้ง `idle_in_transaction_session_timeout`

```sql
ALTER ROLE billing_app SET idle_in_transaction_session_timeout = '60s';
```

### ตัวอย่างที่ 4: ตรวจสอบหลังแก้

```sql
SELECT state, count(*) FROM pg_stat_activity GROUP BY state;
```

ผลลัพธ์:
```text
        state        | count 
---------------------+-------
 active              |    12
 idle                |    30
 idle in transaction |     0
(3 rows)
```

### ตัวอย่างที่ 5: Alert Firing

```bash
curl -s localhost:9090/api/v1/alerts | python3 -m json.tool | grep -E '"alertname"|"state"'
```

ผลลัพธ์:
```text
"alertname": "PostgresConnectionsHigh",
"state": "firing"
```

## 12. สรุปย่อ จำง่าย
- **Connection Full = Session > max_connections**  
- **ตรวจด้วย `pg_stat_activity`**  
- **สาเหตุ: idle in transaction, Connection leak**  
- **แก้ชั่วคราว: `pg_terminate_backend`**  
- **แก้ถาวร: `idle_in_transaction_session_timeout` + PgBouncer**  
- **Alert ที่ 80%**

ประโยคจำ: **"Connection Full ที่ดีคือ Connection ที่ไม่เต็ม เพราะมี PgBouncer"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — Connections: https://www.postgresql.org/docs/17/runtime-config-connection.html
- PgBouncer Documentation: https://www.pgbouncer.org/
- GridCare Workshop Day 5: Lab 3.1

---

# บทที่ 94 Lock Queue

## 1. เรื่อง
การแก้ไขปัญหา Lock Queue ใน PostgreSQL

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจ Lock Queue  
2. เพื่อให้หาต้นคิว  
3. เพื่อให้แก้ไขอย่างถูกต้อง  
4. เพื่อให้ป้องกันการเกิดซ้ำ

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- หาต้นคิวด้วย `pg_blocking_pids`  
- ใช้ `pg_cancel_backend` และ `pg_terminate_backend`  
- ตั้ง `lock_timeout`  
- ตั้ง Alert

## 4. เนื้อหาโดยย่อ
**Lock Queue** เกิดเมื่อ Transaction หนึ่งถือ Lock ไว้ แล้ว Transaction อื่นรอ  
ถ้ามี `AccessExclusiveLock` รอ → Lock อื่นทั้งหมดรอตาม

สาเหตุ:
- Long transaction  
- DDL ไม่มี `lock_timeout`  
- Session ค้าง  
- `idle in transaction`

## 5. ประโยชน์ที่ได้รับ
- แก้ไขเร็ว  
- ลด Downtime  
- ป้องกันการเกิดซ้ำ

## 6. ข้อควรระวัง
- **`AccessExclusiveLock` ที่รอทำให้คิวหยุด**  
- **`pg_terminate_backend` ตัด Session ทันที**  
- **ต้องตั้ง `lock_timeout`**  
- **ต้องหา Root Cause**

## 7. ข้อดี
- แก้ไขเร็ว  
- ป้องกันได้

## 8. ข้อเสีย
- ต้องตรวจ  
- ต้องตั้งค่า

## 9. ข้อห้าม
- ห้าม Kill Session โดยไม่หาสาเหตุ  
- ห้าม DDL โดยไม่ `lock_timeout`  
- ห้าม Transaction ค้าง  
- ห้ามปิด `log_lock_waits`

## 10. รายละเอียด

### 10.1 หาต้นคิว

```sql
SELECT pid, application_name AS app, state, wait_event_type AS wtype,
       pg_blocking_pids(pid) AS blocked_by,
       now() - xact_start AS xact_age,
       left(query, 50) AS query
FROM pg_stat_activity
WHERE datname = 'gridcare'
  AND backend_type = 'client backend'
  AND pid <> pg_backend_pid()
ORDER BY xact_start;
```

ผลลัพธ์:
```text
  pid  |     app     |        state        | wtype  | blocked_by |  xact_age  |                       query                       
-------+-------------+---------------------+--------+------------+------------+---------------------------------------------------
 7659 | batch_A     | idle in transaction | Client | {}         | 00:00:04   | SELECT count(*) FROM gridcare.tariff_rates;
 7665 | migration_B | active              | Lock   | {7659}     | 00:00:03   | ALTER TABLE gridcare.tariff_rates ADD COLUMN note
 7672 | app_C       | active              | Lock   | {7665}     | 00:00:02   | SELECT * FROM gridcare.tariff_rates;
```

### 10.2 หา Root Cause (ต้นคิว)

```sql
SELECT pid, application_name, state, now() - state_change AS idle_for,
       left(query, 50) AS last_query
FROM pg_stat_activity
WHERE pid IN (SELECT unnest(pg_blocking_pids(pid)) FROM pg_stat_activity)
  AND cardinality(pg_blocking_pids(pid)) = 0;
```

ผลลัพธ์:
```text
 pid  | application_name |        state        |    idle_for     |                 last_query                  
------+------------------+---------------------+-----------------+---------------------------------------------
 7659 | batch_A          | idle in transaction | 00:00:04.027413 | SELECT count(*) FROM gridcare.tariff_rates;
```

> ✅ ต้นคิว = `batch_A` (pid 7659)

### 10.3 ดู Log

```bash
sudo grep "still waiting" /var/log/postgresql/postgresql-17-main.log | tail -2
```

ผลลัพธ์:
```text
2026-11-02 14:12:34.567 +07 [7665] postgres@gridcare app=migration_B client=[local] LOG:  process 7665 still waiting for AccessExclusiveLock on relation 16384 of database 16389 after 1000.123 ms
2026-11-02 14:12:34.567 +07 [7672] postgres@gridcare app=app_C client=[local] LOG:  process 7672 still waiting for AccessShareLock on relation 16384 of database 16389 after 1000.456 ms
```

### 10.4 แก้ตามลำดับที่ถูกต้อง

```sql
-- 1) ยกเลิก DDL ที่รอคิว: app_C ทำงานต่อทันที
SELECT pg_cancel_backend(7665);

-- 2) ตัด Session ต้นเหตุที่ค้าง
SELECT pg_terminate_backend(7659);
```

ผลลัพธ์:
```text
 pg_cancel_backend | t
 pg_terminate_backend | t
```

### 10.5 ตั้ง `lock_timeout` (แก้ถาวร)

```sql
SET lock_timeout = '3s';
ALTER TABLE gridcare.tariff_rates ADD COLUMN note text;
```

ผลลัพธ์ (ถ้า Lock ไม่ได้):
```text
ERROR:  canceling statement due to lock timeout
SQLSTATE: 55P03
```

### 10.6 ตั้ง `log_lock_waits`

```ini
log_lock_waits = on
deadlock_timeout = 1s
```

### 10.7 Alert

```yaml
- alert: PostgresLongRunningTransaction
  expr: |
    max by (instance) (
      pg_stat_activity_max_tx_duration{datname="gridcare", state="idle in transaction"}
    ) > 60
  for: 5m
  labels: {severity: warning, owner: dba}
  annotations:
    summary: "Idle in transaction > 60s"
    description: "ตรวจ pg_blocking_pids และ pg_terminate_backend"
    runbook_url: "http://gridcare-infra/runbooks/C01-lock-queue.md"
```

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Lock Queue

```sql
SELECT pid, application_name, state, wait_event_type, pg_blocking_pids(pid)
FROM pg_stat_activity
WHERE datname = 'gridcare' AND backend_type = 'client backend';
```

ผลลัพธ์:
```text
 pid  | application_name | state | wait_event_type | pg_blocking_pids
------+------------------+-------+-----------------+------------------
 7659 | batch_A          | idle  | Client          | {}
 7665 | migration_B      | active| Lock            | {7659}
 7672 | app_C            | active| Lock            | {7665}
```

### ตัวอย่างที่ 2: หา Root Cause

```sql
SELECT pid, application_name, state, now() - state_change AS idle_for
FROM pg_stat_activity
WHERE pid IN (SELECT unnest(pg_blocking_pids(pid)) FROM pg_stat_activity)
  AND cardinality(pg_blocking_pids(pid)) = 0;
```

ผลลัพธ์:
```text
 pid  | application_name |        state        |    idle_for     
------+------------------+---------------------+-----------------
 7659 | batch_A          | idle in transaction | 00:00:04.027413
```

### ตัวอย่างที่ 3: แก้ไข

```sql
SELECT pg_cancel_backend(7665);
SELECT pg_terminate_backend(7659);
```

### ตัวอย่างที่ 4: ตั้ง `lock_timeout`

```sql
SET lock_timeout = '3s';
ALTER TABLE gridcare.tariff_rates ADD COLUMN note text;
```

### ตัวอย่างที่ 5: ตรวจสอบหลังแก้

```sql
SELECT pid, application_name, state FROM pg_stat_activity WHERE datname = 'gridcare';
```

ผลลัพธ์:
```text
 pid  | application_name | state
------+------------------+-------
 7672 | app_C            | active
```

> ✅ app_C ทำงานต่อทันที

## 12. สรุปย่อ จำง่าย
- **Lock Queue เกิดจาก Transaction ค้าง**  
- **หาต้นคิวด้วย `pg_blocking_pids`**  
- **`pg_cancel_backend` ก่อน `pg_terminate_backend`**  
- **`lock_timeout` ก่อน DDL ทุกครั้ง**  
- **`log_lock_waits` + `deadlock_timeout`**  
- **ตั้ง `idle_in_transaction_session_timeout`**

ประโยคจำ: **"Lock Queue ที่ดีคือ Lock Queue ที่ไม่มี เพราะตั้ง `lock_timeout`"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — Explicit Locking: https://www.postgresql.org/docs/17/explicit-locking.html
- PostgreSQL Documentation — Monitoring Locks: https://www.postgresql.org/docs/17/monitoring-locks.html
- GridCare Workshop Day 1: Lab 4.1

---

# บทที่ 95 Disk Full และ WAL

## 1. เรื่อง
การแก้ไขปัญหา Disk Full ที่เกิดจาก WAL และ Data

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจสาเหตุ Disk Full  
2. เพื่อให้ตรวจสอบ WAL  
3. เพื่อให้แก้ไขอย่างถูกต้อง  
4. เพื่อให้ป้องกันการเกิดซ้ำ

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ตรวจสอบ Disk  
- ตรวจสอบ WAL  
- แก้ไข Disk Full  
- ตั้ง Alert

## 4. เนื้อหาโดยย่อ
สาเหตุ Disk Full:
- WAL บวม (Slot ค้าง, Archive ล้ม)  
- Temp File  
- Data Bloat  
- Log  
- Backup

## 5. ประโยชน์ที่ได้รับ
- แก้ไขเร็ว  
- ป้องกันได้  
- ลด Downtime

## 6. ข้อควรระวัง
- **ห้ามลบ `pg_wal` ด้วยมือ**  
- **`max_slot_wal_keep_size` ต้องตั้ง**  
- **Archive ล้มทำให้ WAL บวม**  
- **Log ไม่ Rotate ทำให้ Disk เต็ม**

## 7. ข้อดี
- แก้ไขเร็ว  
- ป้องกันได้

## 8. ข้อเสีย
- ต้องตรวจ  
- ต้องตั้งค่า

## 9. ข้อห้าม
- ห้ามลบ `pg_wal` ด้วยมือ  
- ห้ามปิด Autovacuum  
- ห้ามเปิด `archive_mode = off`  
- ห้ามลบ Backup ก่อนตรวจ

## 10. รายละเอียด

### 10.1 ตรวจสอบ Disk

```bash
df -hT /
df -h /var/lib/postgresql
```

ผลลัพธ์:
```text
Filesystem     Type  Size  Used Avail Use% Mounted on
/dev/sda1      ext4   78G   75G   1G   99% /
```

### 10.2 ตรวจสอบ WAL

```sql
SELECT pg_size_pretty(sum(size)) AS pg_wal_size FROM pg_ls_waldir();
```

ผลลัพธ์:
```text
 pg_wal_size 
-------------
 5 GB
```

```bash
sudo ls -la /var/lib/postgresql/17/main/pg_wal | head -5
```

ผลลัพธ์:
```text
-rw------- 1 postgres postgres 16777216 Nov  2 11:15 000000010000000000000017
-rw------- 1 postgres postgres 16777216 Nov  2 11:15 000000010000000000000018
...
```

### 10.3 ตรวจสอบ Replication Slot

```sql
SELECT slot_name, active, wal_status,
       pg_size_pretty(safe_wal_size) AS safe,
       pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS retained
FROM pg_replication_slots;
```

ผลลัพธ์:
```text
 slot_name | active | wal_status | safe  | retained 
-----------+--------+------------+-------+----------
 pg2       | f      | unreserved | 10 GB | 4 GB
```

> ⚠️ `active = f` = Slot ค้าง, WAL บวม

### 10.4 ตรวจสอบ Archive

```sql
SELECT archived_count, failed_count, last_archived_time
FROM pg_stat_archiver;
```

ผลลัพธ์:
```text
 archived_count | failed_count |    last_archived_time     
----------------+--------------+---------------------------
             45 |            3 | 2026-11-04 09:20:12.345+07
```

> ⚠️ `failed_count = 3` = Archive ล้ม

### 10.5 ตรวจสอบ `archive_status`

```bash
sudo ls /var/lib/postgresql/17/main/pg_wal/archive_status/*.ready 2>/dev/null | wc -l
```

ผลลัพธ์:
```text
45
```

> ⚠️ 45 ไฟล์ `.ready` = ยังไม่ Archive

### 10.6 แก้ไข

**1. ลบ Slot ที่ไม่ใช้:**
```sql
SELECT pg_drop_replication_slot('pg2');
```

**2. ตรวจและแก้ Archive:**
```bash
sudo -u postgres pgbackrest --stanza=gridcare check
```

**3. Archive ที่ค้าง:**
```bash
sudo systemctl restart postgresql@17-main
```

**4. ถ้าเป็น Temp File:**
```sql
-- ตรวจ Temp File
SELECT datname, temp_files, pg_size_pretty(temp_bytes) AS temp_size
FROM pg_stat_database WHERE temp_files > 0;
```

**5. ถ้าเป็น Bloat:**
```bash
sudo -u postgres pg_repack -d gridcare -t gridcare.bills
```

### 10.7 ป้องกัน

```ini
# 1) max_slot_wal_keep_size
max_slot_wal_keep_size = 10GB

# 2) archive_timeout
archive_timeout = 60s

# 3) logrotate
# /etc/logrotate.d/postgresql-common
/var/log/postgresql/*.log {
    weekly
    rotate 4
    compress
}
```

### 10.8 Alert

```yaml
- alert: DiskSpaceLow
  expr: node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"} < 0.15
  for: 5m
  labels: {severity: critical, owner: cloud}
  annotations:
    summary: "Disk / บน {{ $labels.instance }} เหลือ < 15%"
    runbook_url: "http://gridcare-infra/runbooks/C04-disk-full.md"

- alert: PostgresWalDirectoryLarge
  expr: |
    sum by (instance) (pg_ls_waldir_size_bytes) > 5 * 1024 * 1024 * 1024
  for: 10m
  labels: {severity: warning, owner: dba}
  annotations:
    summary: "WAL Directory > 5 GB"
    runbook_url: "http://gridcare-infra/runbooks/C04-disk-full.md"
```

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Disk เต็ม

```bash
df -hT /
```

ผลลัพธ์:
```text
/dev/sda1      ext4   78G   75G   1G   99% /
```

```sql
SELECT pg_size_pretty(sum(size)) AS pg_wal_size FROM pg_ls_waldir();
SELECT slot_name, active, wal_status FROM pg_replication_slots;
```

ผลลัพธ์:
```text
 pg_wal_size = 5 GB
 slot_name = pg2 | active = f | wal_status = unreserved
```

### ตัวอย่างที่ 2: ลบ Slot ที่ไม่ใช้

```sql
SELECT pg_drop_replication_slot('pg2');
```

### ตัวอย่างที่ 3: ตรวจสอบหลังแก้

```sql
SELECT pg_size_pretty(sum(size)) AS pg_wal_size FROM pg_ls_waldir();
```

ผลลัพธ์:
```text
 pg_wal_size 
-------------
 512 MB
```

### ตัวอย่างที่ 4: ตั้ง `max_slot_wal_keep_size`

```sql
ALTER SYSTEM SET max_slot_wal_keep_size = '10GB';
SELECT pg_reload_conf();
```

### ตัวอย่างที่ 5: Alert Firing

```bash
curl -s localhost:9090/api/v1/alerts | python3 -m json.tool | grep -E '"alertname"|"state"'
```

ผลลัพธ์:
```text
"alertname": "DiskSpaceLow",
"state": "firing"
```

## 12. สรุปย่อ จำง่าย
- **Disk Full เกิดจาก WAL, Temp File, Bloat, Log**  
- **ตรวจ `pg_ls_waldir`, `pg_replication_slots`, `pg_stat_archiver`**  
- **ห้ามลบ `pg_wal` ด้วยมือ**  
- **ตั้ง `max_slot_wal_keep_size`**  
- **Archive ต้องทำงาน**  
- **Alert ที่ 15%**

ประโยคจำ: **"Disk Full ที่ดีคือ Disk Full ที่ไม่เกิด เพราะ Monitor ก่อน"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — WAL: https://www.postgresql.org/docs/17/wal.html
- PostgreSQL Documentation — Replication Slots: https://www.postgresql.org/docs/17/warm-standby.html#STREAMING-REPLICATION-SLOTS
- GridCare Workshop Day 5: Workshop Day 5 เหตุการณ์ที่ 3

---

# บทที่ 96 Replication Lag

## 1. เรื่อง
การแก้ไขปัญหา Replication Lag ใน PostgreSQL

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจสาเหตุ Replication Lag  
2. เพื่อให้ตรวจสอบ Lag  
3. เพื่อให้แก้ไข  
4. เพื่อให้ตั้ง Alert

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ตรวจสอบ Lag  
- หา Root Cause  
- แก้ไข  
- ตั้ง Alert

## 4. เนื้อหาโดยย่อ
สาเหตุ Replication Lag:
- Network  
- Replica Resource ไม่พอ  
- WAL ใหญ่  
- `hot_standby_feedback`  
- Long Transaction บน Replica  
- Slot ค้าง

## 5. ประโยชน์ที่ได้รับ
- แก้ไขเร็ว  
- ป้องกันได้  
- ลด Downtime

## 6. ข้อควรระวัง
- **Lag อาจทำให้ RPO สูง**  
- **Slot ที่มี Lag สูงทำให้ WAL บวม**  
- **ต้องตรวจทั้ง Primary และ Replica**  
- **ต้องตั้ง Alert**

## 7. ข้อดี
- แก้ไขเร็ว  
- ป้องกันได้

## 8. ข้อเสีย
- ต้องตรวจ  
- ต้องตั้งค่า

## 9. ข้อห้าม
- ห้ามลบ Slot ที่ Lag สูง  
- ห้าม Restart Replica โดยไม่ตรวจ  
- ห้ามใช้ Sync Replication ที่ไม่มี Quorum  
- ห้ามเปิด `hot_standby_feedback` โดยไม่จำเป็น

## 10. รายละเอียด

### 10.1 ตรวจสอบ Lag

```sql
SELECT application_name, state, sync_state,
       write_lag, flush_lag, replay_lag,
       pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn)) AS replay_gap
FROM pg_stat_replication;
```

ผลลัพธ์:
```text
 application_name |   state   | sync_state |    write_lag    |    flush_lag    |   replay_lag    | replay_gap 
------------------+-----------+------------+-----------------+-----------------+-----------------+------------
 pg2              | streaming | async      | 00:00:05.000    | 00:00:05.000    | 00:00:05.000    | 100 MB
```

> ⚠️ `replay_gap = 100 MB` = Lag สูง

### 10.2 ตรวจสอบ Slot

```sql
SELECT slot_name, active, wal_status,
       pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS retained
FROM pg_replication_slots;
```

ผลลัพธ์:
```text
 slot_name | active | wal_status | retained 
-----------+--------+------------+----------
 pg2       | t      | reserved   | 100 MB
```

### 10.3 ตรวจสอบ Network

```bash
# บน Primary
ping -c 3 pg2
mtr -c 5 pg2

# บน Replica
ping -c 3 pg1
```

### 10.4 ตรวจสอบ Resource บน Replica

```bash
# บน pg2
df -hT /
free -h
nproc
vmstat 2 3
```

### 10.5 ตรวจสอบ `hot_standby_feedback`

```sql
SHOW hot_standby_feedback;
```

ผลลัพธ์:
```text
 hot_standby_feedback 
----------------------
 off
```

> 💡 ถ้า `on` ทำให้ Primary ไม่ Vacuum Dead Tuple ที่ Replica ต้องการ → Bloat

### 10.6 ตรวจสอบ Long Transaction บน Replica

```sql
-- บน pg2
SELECT pid, state, now() - xact_start AS xact_age,
       pg_blocking_pids(pid) AS blocked_by
FROM pg_stat_activity
WHERE state <> 'idle'
ORDER BY xact_start;
```

### 10.7 แก้ไข

**1. Network:**
```bash
# ตรวจ MTU, Bandwidth
ip link show
```

**2. Resource:**
```bash
# เพิ่ม Memory, CPU
```

**3. Slot:**
```sql
-- ตรวจว่า Slot Active
SELECT slot_name, active FROM pg_replication_slots;

-- ถ้า Inactive → ตรวจ Replica
```

**4. `hot_standby_feedback`:**
```sql
-- บน pg2
ALTER SYSTEM SET hot_standby_feedback = 'off';
SELECT pg_reload_conf();
```

**5. Long Transaction:**
```sql
-- บน pg2
SELECT pg_cancel_backend(pid)
FROM pg_stat_activity
WHERE state <> 'idle' AND now() - xact_start > interval '5 minutes';
```

### 10.8 Alert

```yaml
- alert: PostgresReplicationLagHigh
  expr: max by (instance, application_name) (pg_stat_replication_pg_wal_lsn_diff) > 100 * 1024 * 1024
  for: 5m
  labels: {severity: warning, owner: dba}
  annotations:
    summary: "Replication Lag > 100 MB"
    runbook_url: "http://gridcare-infra/runbooks/C08-replication-lag-slot-failover.md"
```

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Lag สูง

```sql
SELECT application_name, state, sync_state,
       pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn)) AS replay_gap
FROM pg_stat_replication;
```

ผลลัพธ์:
```text
 application_name |   state   | sync_state | replay_gap 
------------------+-----------+------------+------------
 pg2              | streaming | async      | 100 MB
```

### ตัวอย่างที่ 2: ตรวจสอบ Network

```bash
ping -c 3 pg2
mtr -c 5 pg2
```

ผลลัพธ์:
```text
3 packets transmitted, 3 received, 0% packet loss
```

### ตัวอย่างที่ 3: ตรวจสอบ Resource

```bash
# บน pg2
free -h
df -hT /
```

### ตัวอย่างที่ 4: ตรวจสอบ `hot_standby_feedback`

```sql
SHOW hot_standby_feedback;
```

ผลลัพธ์:
```text
 hot_standby_feedback 
----------------------
 on
```

> ⚠️ `on` อาจทำให้ Lag

### ตัวอย่างที่ 5: แก้ไข

```sql
-- บน pg2
ALTER SYSTEM SET hot_standby_feedback = 'off';
SELECT pg_reload_conf();
```

## 12. สรุปย่อ จำง่าย
- **Replication Lag = WAL ที่ Replica ตามไม่ทัน**  
- **ตรวจด้วย `pg_stat_replication`**  
- **สาเหตุ: Network, Resource, Slot, `hot_standby_feedback`**  
- **แก้ได้ด้วยเพิ่ม Resource, ปรับ Config**  
- **Alert ที่ 100 MB**

ประโยคจำ: **"Replication Lag ที่ดีคือ Lag ที่ไม่เกิน 100 MB"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — Replication: https://www.postgresql.org/docs/17/warm-standby.html
- GridCare Workshop Day 5: Workshop Day 5 เหตุการณ์ที่ 3

---

# บทที่ 97 OOM

## 1. เรื่อง
การแก้ไขปัญหา OOM (Out of Memory) ใน PostgreSQL

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจสาเหตุ OOM  
2. เพื่อให้ตรวจสอบ OOM  
3. เพื่อให้แก้ไข  
4. เพื่อให้ตั้ง Alert

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ตรวจสอบ OOM  
- หา Root Cause  
- ปรับ `work_mem`, `shared_buffers`  
- ตั้ง Alert

## 4. เนื้อหาโดยย่อ
สาเหตุ OOM:
- `work_mem` สูงเกิน  
- `shared_buffers` สูงเกิน  
- Connection สูง  
- Memory leak ใน Extension  
- Autovacuum Worker เยอะ

## 5. ประโยชน์ที่ได้รับ
- แก้ไขเร็ว  
- ป้องกันได้  
- ลด Downtime

## 6. ข้อควรระวัง
- **`work_mem` เป็นต่อ Operation**  
- **`shared_buffers` ต้องไม่เกิน 40% ของ RAM**  
- **`max_connections` สูงทำให้ Memory ต่อ Process สูง**  
- **ต้องตั้ง `vm.overcommit_memory`**

## 7. ข้อดี
- แก้ไขเร็ว  
- ป้องกันได้

## 8. ข้อเสีย
- ต้องตรวจ  
- ต้องตั้งค่า

## 9. ข้อห้าม
- ห้าม `work_mem` สูงเกิน  
- ห้าม `shared_buffers` สูงเกิน  
- ห้ามเพิ่ม `max_connections` โดยไม่ตรวจ Memory  
- ห้ามปิด OOM Killer

## 10. รายละเอียด

### 10.1 ตรวจสอบ OOM

```bash
dmesg | grep -i "out of memory"
dmesg | grep -i "killed process"
```

ผลลัพธ์:
```text
[12345.678] Out of memory: Killed process 12345 (postgres) total-vm:5123456kB
```

```bash
# ดู PostgreSQL Log
sudo grep -i "terminated by signal 9" /var/log/postgresql/postgresql-17-main.log | tail -5
```

ผลลัพธ์:
```text
LOG:  server process (PID 12345) was terminated by signal 9: Killed
```

### 10.2 ตรวจสอบ Memory

```bash
free -h
```

ผลลัพธ์:
```text
               total        used        free      shared  buff/cache   available
Mem:           3.8Gi       3.5Gi        50Mi        17Mi       200Mi       100Mi
Swap:             0B          0B          0B
```

> ⚠️ Available < 100 Mi = OOM

### 10.3 ตรวจสอบ Parameter

```sql
SHOW shared_buffers;
SHOW work_mem;
SHOW maintenance_work_mem;
SHOW max_connections;
```

ผลลัพธ์:
```text
 shared_buffers = 1GB
 work_mem = 64MB
 maintenance_work_mem = 256MB
 max_connections = 200
```

> ⚠️ `work_mem = 64MB` × 200 = 12.8 GB (เกิน RAM)

### 10.4 ตรวจสอบ Connection

```sql
SELECT state, count(*) FROM pg_stat_activity GROUP BY state;
```

ผลลัพธ์:
```text
        state        | count 
---------------------+-------
 active              |   180
 idle                |    20
```

### 10.5 ตรวจสอบ Query ที่ใช้ Memory สูง

```sql
SELECT pid, state, now() - xact_start AS xact_age,
       left(query, 80) AS query
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY xact_start;
```

### 10.6 แก้ไข

**1. ลด `work_mem`:**
```sql
ALTER SYSTEM SET work_mem = '8MB';
SELECT pg_reload_conf();
```

**2. ลด `max_connections`:**
```sql
ALTER SYSTEM SET max_connections = 100;
-- ต้อง Restart
```

**3. ใช้ PgBouncer:**
```ini
pool_mode = transaction
```

**4. ตั้ง `vm.overcommit_memory`:**
```bash
sudo sysctl vm.overcommit_memory=2
sudo sysctl vm.overcommit_ratio=80
```

**5. ตั้ง `vm.swappiness`:**
```bash
sudo sysctl vm.swappiness=10
```

**6. เพิ่ม RAM (ถ้าจำเป็น):**

### 10.7 Alert

```yaml
- alert: NodeMemoryHigh
  expr: (1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100 > 90
  for: 5m
  labels: {severity: warning, owner: cloud}
  annotations:
    summary: "Memory บน {{ $labels.instance }} > 90%"
    runbook_url: "http://gridcare-infra/runbooks/C06-oom-temp-spill.md"

- alert: PostgresOomKilled
  expr: increase(pg_postmaster_start_time_seconds[5m]) > 0
  for: 1m
  labels: {severity: critical, owner: dba}
  annotations:
    summary: "PostgreSQL Restart — อาจเกิดจาก OOM"
    runbook_url: "http://gridcare-infra/runbooks/C06-oom-temp-spill.md"
```

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: OOM

```bash
dmesg | grep -i "killed process"
```

ผลลัพธ์:
```text
Out of memory: Killed process 12345 (postgres) total-vm:5123456kB
```

### ตัวอย่างที่ 2: ตรวจสอบ Parameter

```sql
SHOW shared_buffers;
SHOW work_mem;
SHOW max_connections;
```

ผลลัพธ์:
```text
 shared_buffers = 1GB
 work_mem = 64MB
 max_connections = 200
```

### ตัวอย่างที่ 3: ลด `work_mem`

```sql
ALTER SYSTEM SET work_mem = '8MB';
SELECT pg_reload_conf();
```

### ตัวอย่างที่ 4: ตั้ง `overcommit_memory`

```bash
sudo sysctl vm.overcommit_memory=2
sudo sysctl vm.overcommit_ratio=80
```

### ตัวอย่างที่ 5: ตรวจสอบหลังแก้

```bash
free -h
```

ผลลัพธ์:
```text
               total        used        free      shared  buff/cache   available
Mem:           3.8Gi       1.5Gi       1.5Gi        17Mi       800Mi       2.0Gi
```

> ✅ Available > 1 Gi

## 12. สรุปย่อ จำง่าย
- **OOM = Memory ไม่พอ**  
- **สาเหตุ: `work_mem`, `shared_buffers`, Connection**  
- **`work_mem` เป็นต่อ Operation**  
- **ตั้ง `vm.overcommit_memory`**  
- **ใช้ PgBouncer**  
- **Alert ที่ 90%**

ประโยคจำ: **"OOM ที่ดีคือ OOM ที่ไม่เกิด เพราะตั้ง `work_mem` เหมาะสม"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — Resource Consumption: https://www.postgresql.org/docs/17/runtime-config-resource.html
- Linux Kernel — Overcommit: https://www.kernel.org/doc/Documentation/vm/overcommit-accounting
- GridCare Workshop Day 5: Workshop Day 5 เหตุการณ์ที่ 3

---

# บทที่ 98 Data Loss และการตัดสินใจ PITR

## 1. เรื่อง
การตัดสินใจทำ PITR เมื่อเกิด Data Loss

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจ Data Loss  
2. เพื่อให้ตรวจสอบก่อนตัดสินใจ  
3. เพื่อให้ทำ PITR ได้ถูกต้อง  
4. เพื่อให้ตรวจสอบผล

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ตรวจสอบ Data Loss  
- หา Time Target  
- ตัดสินใจ PITR  
- ตรวจสอบผล

## 4. เนื้อหาโดยย่อ
Data Loss มี 2 ประเภท:
- **Soft Data Loss** — ข้อมูลถูกลบ/แก้ไขผิด → PITR  
- **Hard Data Loss** — Disk เสียหาย → Restore + PITR

การตัดสินใจ:
1. ยืนยันว่าเป็น Data Loss  
2. หา Time Target  
3. ตรวจสอบ WAL Archive  
4. ตรวจสอบ Backup  
5. ตัดสินใจ PITR

## 5. ประโยชน์ที่ได้รับ
- กู้คืนได้  
- ลด Downtime  
- มี Plan

## 6. ข้อควรระวัง
- **PITR ต้องมี WAL Archive ครบ**  
- **ต้องหยุด PostgreSQL ก่อน**  
- **ต้องมีผู้อนุมัติ**  
- **หลัง PITR ต้อง Full Backup ใหม่**  
- **PITR อาจทำให้ข้อมูลหลัง Target หาย**

## 7. ข้อดี
- กู้คืนได้  
- ระบุเวลาได้

## 8. ข้อเสีย
- ต้องมี Downtime  
- ข้อมูลหลัง Target หาย  
- ต้องมี WAL Archive

## 9. ข้อห้าม
- ห้าม PITR โดยไม่ยืนยัน Data Loss  
- ห้าม PITR โดยไม่มี WAL Archive  
- ห้าม PITR โดยไม่มีผู้อนุมัติ  
- ห้าม PITR โดยไม่หยุด PostgreSQL  
- ห้ามลืม Full Backup หลัง PITR

## 10. รายละเอียด

### 10.1 ยืนยัน Data Loss

```sql
SELECT tariff_code, rate_per_kwh, updated_at FROM gridcare.tariff_rates ORDER BY tariff_code;
```

ผลลัพธ์ (ผิดปกติ):
```text
 tariff_code | rate_per_kwh |         updated_at         
-------------+--------------+----------------------------
 GOV         |       420.00 | 2026-11-04 14:51:15+07
 RES         |       390.00 | 2026-11-04 14:51:15+07
 SMB         |       450.00 | 2026-11-04 14:51:15+07
```

> ⚠️ `rate_per_kwh` ผิดปกติ (ควรเป็น 3.90–4.50)

### 10.2 หา Time Target จาก Log

```bash
sudo grep "duration:.*UPDATE" /var/log/postgresql/postgresql-17-main.log | tail -3 | cut -c1-160
```

ผลลัพธ์:
```text
2026-11-04 14:51:12.409 +07 [8982] postgres@gridcare app=psql client=[local] LOG:  duration: 7969.774 ms  statement: UPDATE bills AS b ...
```

```bash
TARGET="2026-11-04 14:51:12+07"
echo "TARGET=$TARGET"
```

### 10.3 ตรวจสอบ WAL Archive

```sql
SELECT archived_count, failed_count, last_archived_time
FROM pg_stat_archiver;
```

ผลลัพธ์:
```text
 archived_count | failed_count |    last_archived_time     
----------------+--------------+---------------------------
             45 |            0 | 2026-11-04 15:00:00.000+07
```

> ✅ `failed_count = 0` = WAL Archive ครบ

### 10.4 ตรวจสอบ Backup

```bash
sudo -u postgres pgbackrest --stanza=gridcare info
```

ผลลัพธ์:
```text
        full backup: 20261104-091700F
        diff backup: 20261104-100000D
        incr backup: 20261104-100100I
```

> ✅ มี Backup ครบ

### 10.5 ตรวจสอบว่าต้อง PITR หรือไม่

```text
ถ้า Data Loss:
  - ยืนยันว่าเป็น Data Loss
  - หา Time Target
  - ตรวจสอบ WAL Archive
  - ตรวจสอบ Backup
  - ตัดสินใจ PITR

ถ้า Data Loss = Disk เสียหาย:
  - Restore Backup
  - PITR ไปยัง Time Target
```

### 10.6 PITR

```bash
# หยุด PostgreSQL
sudo systemctl stop postgresql@17-main

# Restore
sudo -u postgres pgbackrest --stanza=gridcare --delta --type=time \
  --target="$TARGET" --target-action=promote restore

# Start
sudo systemctl start postgresql@17-main
```

### 10.7 ตรวจสอบผล

```sql
SELECT tariff_code, rate_per_kwh FROM gridcare.tariff_rates ORDER BY tariff_code;
SELECT timeline_id FROM pg_control_checkpoint();
SELECT pg_is_in_recovery();
```

ผลลัพธ์:
```text
 tariff_code | rate_per_kwh 
-------------+--------------
 GOV         |         4.20
 RES         |         3.90
 SMB         |         4.50

 timeline_id = 2
 pg_is_in_recovery = f
```

### 10.8 Full Backup ใหม่

```bash
sudo -u postgres pgbackrest --stanza=gridcare --type=full backup
sudo -u postgres pgbackrest --stanza=gridcare check
```

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Data Loss

```sql
SELECT tariff_code, rate_per_kwh, updated_at FROM gridcare.tariff_rates ORDER BY tariff_code;
```

ผลลัพธ์:
```text
 tariff_code | rate_per_kwh |         updated_at         
-------------+--------------+----------------------------
 GOV         |       420.00 | 2026-11-04 14:51:15+07
```

### ตัวอย่างที่ 2: หา Time Target

```bash
sudo grep "duration:.*UPDATE" /var/log/postgresql/postgresql-17-main.log | tail -3
```

ผลลัพธ์:
```text
2026-11-04 14:51:12.409 +07 ... duration: 7969.774 ms ...
```

### ตัวอย่างที่ 3: PITR

```bash
sudo systemctl stop postgresql@17-main
sudo -u postgres pgbackrest --stanza=gridcare --delta --type=time \
  --target="2026-11-04 14:51:12+07" --target-action=promote restore
sudo systemctl start postgresql@17-main
```

### ตัวอย่างที่ 4: ตรวจสอบ

```sql
SELECT tariff_code, rate_per_kwh FROM gridcare.tariff_rates ORDER BY tariff_code;
```

ผลลัพธ์:
```text
 tariff_code | rate_per_kwh 
-------------+--------------
 GOV         |         4.20
 RES         |         3.90
 SMB         |         4.50
```

### ตัวอย่างที่ 5: Full Backup ใหม่

```bash
sudo -u postgres pgbackrest --stanza=gridcare --type=full backup
```

## 12. สรุปย่อ จำง่าย
- **Data Loss = ข้อมูลหาย/ผิด**  
- **PITR = กู้คืนไปยังเวลา**  
- **ต้องมี WAL Archive ครบ**  
- **ต้องหยุด PostgreSQL ก่อน**  
- **ต้องมีผู้อนุมัติ**  
- **หลัง PITR ต้อง Full Backup ใหม่**

ประโยคจำ: **"PITR ที่ดีคือ PITR ที่มี WAL Archive และ Plan"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — PITR: https://www.postgresql.org/docs/17/continuous-archiving.html
- pgBackRest — Restore Time: https://pgbackrest.org/command.html#command-restore
- GridCare Workshop Day 3: Workshop Day 3 ขั้นที่ 1

---

# บทที่ 99 Incident Record Template

## 1. เรื่อง
Template สำหรับการบันทึก Incident Record ที่มีคุณภาพ

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้ Incident Record มีมาตรฐาน  
2. เพื่อให้ RCA/PSR มีข้อมูลครบ  
3. เพื่อให้ Handover ราบรื่น  
4. เพื่อให้ Audit ผ่าน

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- เขียน Incident Record ได้  
- ใช้ Template  
- บันทึก Timeline  
- ใช้ Handover Note

## 4. เนื้อหาโดยย่อ
Incident Record ประกอบด้วย:
1. ข้อมูลเบื้องต้น  
2. Alert  
3. Symptom  
4. Root Cause  
5. Actions Taken  
6. Handover  
7. PSR

## 5. ประโยชน์ที่ได้รับ
- มาตรฐาน  
- ผ่าน Audit  
- RCA/PSR มีข้อมูลครบ  
- Handover ราบรื่น

## 6. ข้อควรระวัง
- **Incident Record ที่ไม่มี Timeline ไม่มีคุณค่า**  
- **Incident Record ที่ไม่ Reviewed จะเก่า**  
- **Incident Record ที่ไม่ Blameless จะทำให้ทีมกลัว**

## 7. ข้อดี
- มาตรฐาน  
- Audit ผ่าน  
- เรียนรู้จากเหตุการณ์

## 8. ข้อเสีย
- ต้อง Maintain  
- ต้อง Review

## 9. ข้อห้าม
- ห้าม Incident Record ที่ไม่มีวันที่  
- ห้าม Incident Record ที่ไม่ Blameless  
- ห้าม Incident Record ที่ไม่มี Action Item

## 10. รายละเอียด

### 10.1 Incident Record Template

```markdown
# Incident Record

## ข้อมูลเบื้องต้น
- **Incident ID:** INC-YYYY-MM-DD-NNN
- **Started:** YYYY-MM-DD HH:MM:SS
- **Detected:** YYYY-MM-DD HH:MM:SS
- **Resolved:** YYYY-MM-DD HH:MM:SS
- **Duration:** X นาที Y วินาที
- **Severity:** critical / warning / info

## Alert
- **Name:** <Alert Name>
- **Instance:** <instance>
- **Runbook:** <Runbook URL>

## Symptoms
- <Symptom 1>
- <Symptom 2>

## Root Cause
- <Root Cause>

## Timeline
- HH:MM:SS — <Event>
- HH:MM:SS — <Event>
- HH:MM:SS — <Event>

## Actions Taken
1. <Action 1>
2. <Action 2>

## Handover
- <Handover Note>

## PSR (Post-Incident Review)
- **Date:** YYYY-MM-DD
- **Attendees:** <Names/Roles>
- **Action Items:**
  - [ ] <Action 1> — Owner: <Name> — Due: <Date>
  - [ ] <Action 2> — Owner: <Name> — Due: <Date>
```

### 10.2 ตัวอย่าง Incident Record

```markdown
# Incident Record

## ข้อมูลเบื้องต้น
- **Incident ID:** INC-2026-11-05-001
- **Started:** 2026-11-05 14:30:15
- **Detected:** 2026-11-05 14:30:20
- **Resolved:** 2026-11-05 14:31:20
- **Duration:** 1 นาที 5 วินาที
- **Severity:** critical

## Alert
- **Name:** PostgresDown
- **Instance:** pg1:9187
- **Runbook:** http://gridcare-infra/runbooks/C08-postgres-down.md

## Symptoms
- pg1 ไม่ตอบสนอง
- Application Connection refused
- PgBouncer คืน Connection refused

## Root Cause
- pg1 ถูก SIGKILL
- Patroni failover ไป pg2 อัตโนมัติ

## Timeline
- 14:30:15 — Alert PostgresDown (firing)
- 14:30:20 — ตรวจ Patroni: ไม่มี Leader
- 14:30:30 — Escalate ไปที่ DBA Lead
- 14:30:45 — Patroni promote pg2
- 14:31:00 — ยืนยัน pg_up = 1 บน pg2
- 14:31:20 — Alert Resolved

## Actions Taken
1. ตรวจ pg_isready → No response
2. ตรวจ Patroni → ไม่มี Leader
3. Escalate ไปที่ DBA Lead
4. Patroni promote pg2 อัตโนมัติ
5. ยืนยัน pg_up = 1 บน pg2

## Handover
- pg1 กำลัง Rebuild Replica
- Backup ที่รัน 17:00 ต้องตรวจ

## PSR
- **Date:** 2026-11-05 16:00
- **Attendees:** DBA A, DBA B, DevOps A, Cloud A
- **Action Items:**
  - [ ] ตรวจสอบว่า SIGKILL มาจากอะไร — Owner: Cloud A — Due: 2026-11-06
  - [ ] เพิ่ม Alert "OOMKilled" — Owner: DevOps A — Due: 2026-11-07
  - [ ] เพิ่ม `vm.overcommit_memory` — Owner: Cloud A — Due: 2026-11-10
```

### 10.3 Handover Note Template

```markdown
# Handover Note

## From: <Name>
## To: <Name>
## Date: YYYY-MM-DD HH:MM

## Active Incidents
- <Incident ID>: <Status>

## Alerts ที่ Silence อยู่
- <Alert>: <Until>

## สิ่งที่ต้องติดตาม
- <Item 1>
- <Item 2>

## Recent Changes
- <Change 1>
- <Change 2>
```

### 10.4 PSR Template

```markdown
# Post-Incident Review

## Incident
- **ID:** INC-2026-11-05-001
- **Date:** 2026-11-05
- **Severity:** critical

## Summary
- <Summary 2-3 บรรทัด>

## Impact
- Downtime: X นาที
- Users affected: Y
- Data loss: Z

## Timeline
- <Timeline>

## Root Cause
- <Root Cause>

## Contributing Factors
- <Factor 1>
- <Factor 2>

## Action Items
- [ ] <Action 1> — Owner: <Name> — Due: <Date>
- [ ] <Action 2> — Owner: <Name> — Due: <Date>

## Lessons Learned
- <Lesson 1>
- <Lesson 2>
```

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Incident Record

```markdown
# Incident Record

## ข้อมูลเบื้องต้น
- **Incident ID:** INC-2026-11-05-001
- **Started:** 2026-11-05 14:30:15
- **Detected:** 2026-11-05 14:30:20
- **Resolved:** 2026-11-05 14:31:20
- **Duration:** 1 นาที 5 วินาที
- **Severity:** critical

## Alert
- **Name:** PostgresDown
- **Runbook:** http://gridcare-infra/runbooks/C08-postgres-down.md

## Root Cause
- pg1 ถูก SIGKILL, Patroni failover ไป pg2
```

### ตัวอย่างที่ 2: Handover Note

```markdown
# Handover Note

## From: DBA A
## To: DBA B
## Date: 2026-11-05 18:00

## Active Incidents
- ไม่มี

## Alerts ที่ Silence อยู่
- PostgresXidAgeWarning (pg1:9187) — ถึง 2026-11-06 08:00

## สิ่งที่ต้องติดตาม
- pg2 กำลัง Rebuild Replica (คาดเสร็จ 19:00)
- Backup ที่รัน 17:00 ต้องตรวจ
```

### ตัวอย่างที่ 3: PSR

```markdown
# Post-Incident Review

## Incident
- **ID:** INC-2026-11-05-001
- **Date:** 2026-11-05
- **Severity:** critical

## Summary
- pg1 ถูก SIGKILL ทำให้ต้อง Failover ไป pg2 ใช้เวลา 1 นาที 5 วินาที

## Impact
- Downtime: 65 วินาที
- Users affected: ~50
- Data loss: 0

## Root Cause
- pg1 ถูก SIGKILL (สาเหตุ: OOMKilled)

## Action Items
- [ ] ตรวจสอบว่า SIGKILL มาจากอะไร — Owner: Cloud A — Due: 2026-11-06
- [ ] เพิ่ม Alert "OOMKilled" — Owner: DevOps A — Due: 2026-11-07
- [ ] เพิ่ม `vm.overcommit_memory` — Owner: Cloud A — Due: 2026-11-10
```

## 12. สรุปย่อ จำง่าย
- **Incident Record ต้องมี 7 ส่วน**  
- **Timeline คือหัวใจ**  
- **Handover Note ต้องมี**  
- **PSR ต้องมี Action Item**  
- **Blameless**  
- **ทุกข้อต้องมีเจ้าของและวันที่**

ประโยคจำ: **"Incident Record ที่ดีคือ Record ที่มี Timeline และ Action Item"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- Google SRE Book — Postmortem Culture: https://sre.google/sre-book/postmortem-culture/
- PagerDuty Incident Response: https://response.pagerduty.com/
- GridCare Workshop: Incident Record Template

---

# บทที่ 100 Game Day Scenarios

## 1. เรื่อง
Game Day 5 เหตุการณ์จำลองสำหรับฝึกทีม DBA, DevOps และ Cloud Engineer

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้ทีมฝึกตอบสนอง Incident  
2. เพื่อให้วัด RTO/RPO  
3. เพื่อให้ฝึก PSR  
4. เพื่อให้ค้นหา Weakness

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ฝึก 5 เหตุการณ์  
- วัด RTO/RPO  
- เขียน Incident Record  
- เขียน PSR

## 4. เนื้อหาโดยย่อ
5 เหตุการณ์:
1. **Connection Full** (C03)  
2. **Lock Queue** (C01)  
3. **Disk Full + Replication Lag** (C04, C08)  
4. **Primary ล่ม** (C08)  
5. **Data Loss** (C07)

## 5. ประโยชน์ที่ได้รับ
- ฝึกทีม  
- วัด RTO/RPO  
- ค้นหา Weakness  
- ผ่าน Audit

## 6. ข้อควรระวัง
- **ห้ามทำใน Production**  
- **ต้องมีผู้ดูแล**  
- **ต้องมี Backup**  
- **ต้องมี Incident Record**  
- **ต้องมี PSR**

## 7. ข้อดี
- ฝึกทีม  
- วัดได้  
- ค้นหา Weakness

## 8. ข้อเสีย
- ใช้เวลา  
- ต้องมี Test Environment

## 9. ข้อห้าม
- ห้าม Game Day ใน Production  
- ห้ามไม่บันทึก Incident  
- ห้ามไม่มี PSR  
- ห้ามไม่วัด RTO/RPO

## 10. รายละเอียด

### 10.1 เหตุการณ์ที่ 1: Connection Full

**สถานการณ์:**
```bash
# เปิด Session ค้าง
for i in $(seq 1 150); do
  psql "host=pg1 dbname=gridcare user=billing_app" -c "BEGIN; SELECT 1; SELECT pg_sleep(3600);" &
done
```

**อาการ:**
- Connection Full
- Alert `PostgresConnectionsHigh`
- App Connection refused

**การแก้ไข:**
```sql
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle in transaction' AND now() - state_change > interval '5 minutes';
```

**การป้องกัน:**
- `idle_in_transaction_session_timeout = '60s'`
- PgBouncer
- Alert ที่ 80%

### 10.2 เหตุการณ์ที่ 2: Lock Queue

**สถานการณ์:**
```sql
-- หน้าต่าง 1
BEGIN;
SELECT count(*) FROM gridcare.bills;
-- ไม่ COMMIT

-- หน้าต่าง 2
ALTER TABLE gridcare.bills ADD COLUMN test text;
-- ค้าง

-- หน้าต่าง 3
SELECT * FROM gridcare.bills LIMIT 10;
-- ค้าง
```

**การแก้ไข:**
```sql
SELECT pg_cancel_backend(<pid_DDL>);
SELECT pg_terminate_backend(<pid_idle>);
```

**การป้องกัน:**
- `lock_timeout = '3s'`
- `idle_in_transaction_session_timeout`
- Alert `PostgresLongRunningTransaction`

### 10.3 เหตุการณ์ที่ 3: Disk Full + Replication Lag

**สถานการณ์:**
```bash
# เติม Disk
dd if=/dev/zero of=/var/lib/postgresql/fill bs=1M count=50000

# หยุด Replica
sudo systemctl stop patroni@17-main  # บน pg2
```

**อาการ:**
- Disk 99%
- WAL บวม
- Replication Lag สูง
- Alert `DiskSpaceLow` + `PostgresReplicationLagHigh`

**การแก้ไข:**
```bash
# ลบไฟล์
rm /var/lib/postgresql/fill

# ตรวจ Slot
sudo -u postgres psql -c "SELECT slot_name, active FROM pg_replication_slots;"

# เริ่ม Replica
sudo systemctl start patroni@17-main
```

**การป้องกัน:**
- `max_slot_wal_keep_size`
- Alert Disk 15%
- Alert WAL > 5 GB

### 10.4 เหตุการณ์ที่ 4: Primary ล่ม

**สถานการณ์:**
```bash
# บน pg1
sudo systemctl kill -s SIGKILL patroni@17-main
```

**อาการ:**
- pg1 Down
- Patroni Failover ไป pg2
- Alert `PostgresDown` + `PatroniPrimaryCountNotOne`

**การแก้ไข:**
- Patroni Failover อัตโนมัติ
- ตรวจสอบ `patronictl list`
- Full Backup ใหม่

**วัด RTO/RPO:**
```bash
# RTO
KILL_AT=$(date +%T.%N | cut -c1-12)
FIRST_OK=$(awk '/ FAIL /{f=1} f && / OK /{print $1; exit}' ~/probe.log)
echo "RTO = $..."

# RPO
comm -23 ~/ok_ids.txt ~/db_ids.txt | wc -l
```

**การป้องกัน:**
- etcd 3 โหนด
- Patroni
- HAProxy
- Alert `PatroniPrimaryCountNotOne`

### 10.5 เหตุการณ์ที่ 5: Data Loss

**สถานการณ์:**
```sql
UPDATE gridcare.tariff_rates SET rate_per_kwh = rate_per_kwh * 100;
```

**อาการ:**
- `rate_per_kwh` ผิดปกติ
- Alert ไม่มี (ไม่มี Alert สำหรับ Data Loss)

**การแก้ไข:**
- หา Time Target จาก Log
- PITR
- Full Backup ใหม่

**การป้องกัน:**
- ใช้ `default_transaction_read_only = on` สำหรับ Report
- ใช้ `SET ROLE` ก่อน UPDATE
- Backup ที่ Restore ได้

### 10.6 ตาราง RTO/RPO

| เหตุการณ์ | RTO | RPO | Alert |
|---|---|---|---|
| 1. Connection Full | 5 นาที | 0 | PostgresConnectionsHigh |
| 2. Lock Queue | 3 นาที | 0 | PostgresLongRunningTransaction |
| 3. Disk Full + Lag | 10 นาที | 0 | DiskSpaceLow, ReplicationLagHigh |
| 4. Primary ล่ม | 31 วินาที | 0 | PostgresDown, PatroniPrimaryCountNotOne |
| 5. Data Loss | 8 นาที 32 วินาที | 0 | (ไม่มี) |

### 10.7 Incident Record Template

```markdown
เหตุการณ์ที่ 4  เริ่ม 14:30:15  ตรวจพบ 14:30:46  แก้เสร็จ 14:31:00  ยืนยันปกติ 14:31:15
อาการ    : แอปเขียนไม่ได้, PgBouncer คืน Connection refused
ต้นเหตุ   : Primary (pg1) ถูก SIGKILL, Patroni failover ไป pg2
สิ่งที่ทำ : Patroni promote pg2 อัตโนมัติ, HAProxy สลับ health check
ตรวจพบจาก: Alert PostgresDown (firing 14:30:30) + probe.sh FAIL
RTO = 31.2 วินาที  RPO = 0
```

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: เตรียม Game Day

```bash
patronictl list
sudo -u postgres pgbackrest --stanza=gridcare info | grep -E "full backup" | tail -1
curl -s localhost:9090/api/v1/alerts | python3 -c "import sys,json; print([a['labels']['alertname'] for a in json.load(sys.stdin)['data']['alerts'] if a['state']=='firing'])"
```

ผลลัพธ์:
```text
| pg1 | ... | Leader  | running   | 2 |
| pg2 | ... | Replica | streaming | 2 |

        full backup: 20261106-110000F
[]
```

### ตัวอย่างที่ 2: เหตุการณ์ที่ 4 (Primary ล่ม)

```bash
# หน้าต่าง 1 (infra)
cd /opt/gridcare/pgbench && PGHOST=127.0.0.1 PGPORT=6432 PGUSER=billing_app ./run_payday.sh 20 600

# หน้าต่าง 2 (infra)
~/probe.sh 180 | tee ~/probe.log

# หน้าต่าง 3 (pg1)
date +%T.%N | cut -c1-12
sudo systemctl kill -s SIGKILL patroni@17-main
```

### ตัวอย่างที่ 3: วัด RTO

```bash
KILL_AT=03:03:43.351
FIRST_OK=$(awk '/ FAIL /{f=1} f && / OK /{print $1; exit}' ~/probe.log)
python3 -c "from datetime import datetime as d; f='%H:%M:%S.%f'; print('RTO =', round((d.strptime('$FIRST_OK', f) - d.strptime('$KILL_AT', f)).total_seconds(), 1), 'วินาที')"
```

ผลลัพธ์:
```text
RTO = 31.3 วินาที
```

### ตัวอย่างที่ 4: วัด RPO

```bash
psql -X -At "host=127.0.0.1 port=6432 dbname=gridcare user=billing_app" \
  -c "SELECT id FROM gridcare.failover_probe ORDER BY id" | sort > ~/db_ids.txt
grep ' OK id=' ~/probe.log | sed 's/.*id=//' | sort > ~/ok_ids.txt
comm -23 ~/ok_ids.txt ~/db_ids.txt > ~/missing_ids.txt
echo "RPO = $(wc -l < ~/missing_ids.txt)"
```

ผลลัพธ์:
```text
RPO = 0
```

### ตัวอย่างที่ 5: Debrief

**สิ่งที่ต้องส่ง:**
1. ตาราง RTO/RPO ของเหตุการณ์ที่ 4-5  
2. Alert ที่ดังก่อนผู้ใช้แจ้ง vs ที่ไม่ดัง  
3. งานป้องกันอย่างน้อย 3 รายการ + อย่างน้อย 1 เป็น Alert

## 12. สรุปย่อ จำง่าย
- **5 เหตุการณ์:** Connection Full, Lock Queue, Disk Full, Primary ล่ม, Data Loss  
- **ทุกเหตุการณ์ต้องมี Incident Record**  
- **ทุกเหตุการณ์ต้องมี PSR**  
- **ทุกเหตุการณ์ต้องวัด RTO/RPO**  
- **ทุกเหตุการณ์ต้องมี Preventive Action**

ประโยคจำ: **"Game Day ที่ดีคือ Game Day ที่ทำให้ทีมเก่งขึ้นและมี Action Item"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- Google SRE Book — Postmortem Culture: https://sre.google/sre-book/postmortem-culture/
- PagerDuty Incident Response: https://response.pagerduty.com/
- GridCare Workshop Day 5: Workshop Day 5 ขั้นที่ 2, 3

---

## สรุปส่วนที่ 10 (บทที่ 91–100)

| บท | แก่นของบท | ใช้ต่อในส่วน |
|---|---|---|
| 91 | ลำดับ 15 นาทีแรก | Incident Response |
| 92 | แยก "ล่ม" กับ "ช้า" | S troubleshooting |
| 93 | Connection Full | S troubleshooting |
| 94 | Lock Queue | S troubleshooting |
| 95 | Disk Full + WAL | S troubleshooting |
| 96 | Replication Lag | S troubleshooting |
| 97 | OOM | S troubleshooting |
| 98 | Data Loss + PITR | Incident Response |
| 99 | Incident Record Template | SRE |
| 100 | Game Day Scenarios | SRE, Continuous Improvement |

---
 