# บทที่ 41–50

> หนังสือ: คู่มือการใช้งาน PostgreSQL สำหรับ DevOps Engineer, Cloud Engineer และ DBA  
> ส่วนที่ 5 Observability  
> โทน: ทางการ กระชับ เน้นใช้งานจริง

---

# บทที่ 41 ตัวชี้วัดสำคัญของ PostgreSQL

## 1. เรื่อง
ตัวชี้วัด (Metrics) สำคัญของ PostgreSQL ที่ต้องเก็บและเฝ้าระวังในระบบ Production

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้รู้ว่า Metric ใดสำคัญต่อ Availability, Performance, Security  
2. เพื่อให้เลือก Metric ที่ actionable  
3. เพื่อให้ผูก Metric กับ Alert และ Runbook  
4. เพื่อให้เห็นภาพรวมก่อนลงลึกใน Prometheus

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ระบุ Metric สำคัญ 5 กลุ่มได้  
- อธิบาย Metric แต่ละตัวว่าตอบคำถามอะไร  
- เลือก Metric สำหรับ Dashboard และ Alert  
- ผูก Metric กับ Runbook

## 4. เนื้อหาโดยย่อ
Metric สำคัญแบ่งเป็น 5 กลุ่ม:
1. **Availability** — `pg_up`, `pg_postmaster_start_time`  
2. **Connection** — `pg_stat_activity_count`, `pg_settings_max_connections`  
3. **Transaction** — `pg_stat_database_xact_commit`, `xact_rollback`, `tup_*`  
4. **Resource** — `shared_buffers`, `blks_hit/read`, `temp_bytes`, `wal_bytes`  
5. **Health** — XID Age, Dead Tuple, Replication Lag, Backup Age, SSL Expiry

## 5. ประโยชน์ที่ได้รับ
- Dashboard มี Metric ที่ตอบคำถาม  
- Alert มี Metric ที่ actionable  
- ลด Metric ที่ไม่จำเป็น  
- ทำให้ Incident Response มีข้อมูลครบ

## 6. ข้อควรระวัง
- **Metric ที่ไม่มี Label ที่ดี** ทำให้กรองไม่ได้  
- **Metric ที่ Cardinality สูง** ทำให้ Prometheus หนัก  
- **Metric ที่ไม่ actionable** ทำให้ Alert Fatigue  
- **Metric ที่ไม่เก็บย้อนหลัง** ทำให้วิเคราะห์ไม่ได้  
- **Metric ที่ไม่ผูกกับ Runbook** ทำให้ตอบสนองช้า

## 7. ข้อดี
- ทำให้ทุกทีมเห็นภาพเดียวกัน  
- ทำให้ Alert มีคุณภาพ  
- ทำให้ RCA/PSR มีข้อมูล

## 8. ข้อเสีย
- Metric มากเกินไปทำให้ Dashboard รก  
- ต้อง Maintain Metric ให้ทันสมัย

## 9. ข้อห้าม
- ห้ามเก็บ Metric ทุกตัวโดยไม่คัด  
- ห้ามใช้ Label ที่ Cardinality สูง เช่น `query`  
- ห้ามตั้ง Alert ที่ไม่มี Runbook  
- ห้ามเก็บ Metric ที่ไม่ตอบคำถามธุรกิจ

## 10. รายละเอียด

### 10.1 ตาราง Metric สำคัญ

| กลุ่ม | Metric | ความหมาย | Alert |
|---|---|---|---|
| Availability | `pg_up` | PostgreSQL ทำงานหรือไม่ | Critical |
| Availability | `pg_postmaster_start_time_seconds` | เวลา Start | Info (Restart) |
| Connection | `pg_stat_activity_count{state="active"}` | Session ที่ทำงาน | Warning |
| Connection | `pg_settings_max_connections` | Connection สูงสุด | - |
| Transaction | `pg_stat_database_xact_commit` | Commit | - |
| Transaction | `pg_stat_database_xact_rollback` | Rollback | Warning (ratio) |
| Buffer | `pg_stat_database_blks_hit` | Cache Hit | - |
| Buffer | `pg_stat_database_blks_read` | Cache Miss | - |
| WAL | `pg_stat_wal_wal_bytes` | WAL ที่สร้าง | - |
| XID | `pg_database_wraparound_age_datfrozenxid_seconds` | อายุ XID | Warning/Critical |
| Bloat | `pg_stat_user_tables_n_dead_tup` | Dead Tuple | Warning |
| Replication | `pg_stat_replication_pg_wal_lsn_diff` | Replication Lag | Warning |
| Slot | `pg_replication_slots_pg_wal_status` | สถานะ Slot | Critical |
| Backup | `gridcare_backup_last_success_timestamp_seconds` | เวลา Backup สำเร็จ | Critical |
| SSL | `gridcare_ssl_cert_expiry_days` | วันหมดอายุ Cert | Warning |
| Disk | `node_filesystem_avail_bytes` | Disk ว่าง | Critical |
| CPU | `node_cpu_seconds_total` | CPU | Warning |
| Patroni | `patroni_primary` | จำนวน Primary | Critical |

### 10.2 Metric ที่ตอบคำถาม

| คำถาม | Metric |
|---|---|
| ระบบยังอยู่ไหม | `pg_up` |
| Connection เต็มไหม | `pg_stat_activity_count / pg_settings_max_connections` |
| Query ช้าลงไหม | `pg_stat_statements` (ไม่ใช่ Metric ตรง) |
| Cache ดีไหม | `blks_hit / (blks_hit + blks_read)` |
| WAL โตไหม | `pg_stat_wal_wal_bytes` |
| Bloat ไหม | `n_dead_tup` |
| XID ใกล้ Wraparound ไหม | `age(datfrozenxid)` |
| Replica ตามทันไหม | `pg_stat_replication_pg_wal_lsn_diff` |
| Backup ล่าสุดเมื่อไหร่ | `gridcare_backup_last_success_timestamp_seconds` |
| Cert หมดอายุไหม | `gridcare_ssl_cert_expiry_days` |
| Primary มี 1 ตัวไหม | `patroni_primary` |

### 10.3 Metric ที่ควรละเว้น

- `pg_stat_statements` ทุก Query ที่มี `query` เป็น Label (Cardinality สูง)  
- Metric ที่ไม่เคย Alert หรือ Dashboard ไม่ใช้  
- Metric ที่ซ้ำซ้อนกับ Metric อื่น  
- Metric ที่ไม่ actionable

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Dashboard ที่แนะนำ

```text
Row 1: Availability + TPS + Connections + Cache Hit
Row 2: CPU + Memory + Disk
Row 3: XID Age + Dead Tuple + Replication Lag
Row 4: Top 5 Query by Total Time
Row 5: Alert Status + Recent Restart
```

### ตัวอย่างที่ 2: Alert ที่แนะนำ

```yaml
- alert: PostgresDown
  expr: pg_up == 0
  for: 1m
  labels: {severity: critical, owner: dba}

- alert: PostgresConnectionsHigh
  expr: sum by (instance) (pg_stat_activity_count{datname="gridcare"})
        / max by (instance) (pg_settings_max_connections) * 100 > 80
  for: 5m
  labels: {severity: warning, owner: dba}

- alert: PostgresXidAgeWarning
  expr: pg_database_wraparound_age_datfrozenxid_seconds > 1e9
  for: 1h
  labels: {severity: warning, owner: dba}
```

### ตัวอย่างที่ 3: PromQL ที่ใช้บ่อย

```promql
# TPS
sum by (datname) (
  rate(pg_stat_database_xact_commit{datname="gridcare"}[1m])
  + rate(pg_stat_database_xact_rollback{datname="gridcare"}[1m])
)

# Cache Hit Ratio
rate(pg_stat_database_blks_hit{datname="gridcare"}[5m])
/
(
  rate(pg_stat_database_blks_hit{datname="gridcare"}[5m])
  + rate(pg_stat_database_blks_read{datname="gridcare"}[5m])
)

# Connections
sum by (state) (pg_stat_activity_count{datname="gridcare"})

# XID Age
pg_database_wraparound_age_datfrozenxid_seconds

# Replication Lag
max by (instance, application_name) (pg_stat_replication_pg_wal_lsn_diff)
```

## 12. สรุปย่อ จำง่าย
- **Metric 5 กลุ่ม:** Availability, Connection, Transaction, Resource, Health  
- **Metric ต้องตอบคำถามได้**  
- **Metric ต้อง actionable**  
- **Metric ต้องมี Runbook**  
- **Metric ต้องมี Label ที่ดี**  
- **Metric ไม่ควร Cardinality สูง**

ประโยคจำ: **“Metric ที่ดีคือ Metric ที่ทำให้รู้ว่าต้องทำอะไร”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — Monitoring Database Activity: https://www.postgresql.org/docs/17/monitoring.html
- postgres_exporter: https://github.com/prometheus-community/postgres_exporter
- GridCare Workshop Day 2: Lab 3.1, Lab 3.2

---

# บทที่ 42 postgres_exporter

## 1. เรื่อง
`postgres_exporter` สำหรับแปลง Metric จาก PostgreSQL ให้ Prometheus อ่าน

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้ติดตั้งและตั้งค่า `postgres_exporter`  
2. เพื่อให้เลือก Collector ที่ต้องการ  
3. เพื่อให้ใช้ Role ที่ปลอดภัย  
4. เพื่อให้ตรวจสอบ Metric ที่ Export

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- สร้าง Role `pgexporter` ที่ปลอดภัย  
- ตั้ง `DATA_SOURCE_NAME` ใน `/etc/default/postgres_exporter`  
- ตั้ง Collector ที่ต้องการ  
- ตรวจ Metric ด้วย `curl localhost:9187/metrics`

## 4. เนื้อหาโดยย่อ
`postgres_exporter` เป็น Exporter ที่:
- ต่อ PostgreSQL ผ่าน Connection String  
- Query Metric จาก `pg_stat_*` View  
- แปลงเป็น Prometheus Format  
- เปิด HTTP Port 9187

## 5. ประโยชน์ที่ได้รับ
- Prometheus อ่าน Metric ได้  
- ใช้ Role ที่ปลอดภัย  
- เลือก Collector ได้  
- ใช้ Custom Metric ได้

## 6. ข้อควรระวัง
- **ใช้ Role ที่มีสิทธิ์ `pg_monitor`**  
- **`DATA_SOURCE_NAME` ควรใช้ TLS**  
- **`/etc/default/postgres_exporter` ต้อง `chmod 600`**  
- **Collector ที่ไม่ใช้ปิดได้เพื่อลดโหลด**  
- **ต้องตรวจ Metric ที่ Export จริง**

## 7. ข้อดี
- เป็นมาตรฐาน  
- มี Collector พร้อมใช้  
- ใช้ Role ที่ปลอดภัยได้  
- รองรับ Custom Query

## 8. ข้อเสีย
- ต้องดูแล Version  
- Collector บางตัวต้อง Query หนัก  
- Metric บางตัว Cardinality สูง

## 9. ข้อห้าม
- ห้ามใช้ Superuser กับ Exporter  
- ห้ามเปิด Metric ที่ Cardinality สูง  
- ห้ามใช้ `sslmode=disable` ใน Production  
- ห้ามเก็บ Password ในที่ Public  
- ห้ามใช้ Exporter เป็นช่องทาง Backup

## 10. รายละเอียด

### 10.1 สร้าง Role สำหรับ Exporter

```sql
CREATE ROLE pgexporter LOGIN PASSWORD 'Lab-Exporter-2569' IN ROLE pg_monitor;
GRANT CONNECT ON DATABASE gridcare TO pgexporter;
ALTER ROLE pgexporter SET statement_timeout = '10s';
```

ผลลัพธ์:
```text
CREATE ROLE
GRANT
ALTER ROLE
```

### 10.2 ติดตั้ง node_exporter

```bash
sudo apt install -y prometheus-node-exporter
systemctl status prometheus-node-exporter --no-pager | head -3
curl -s localhost:9100/metrics | grep -c '^node_'
```

ผลลัพธ์:
```text
● prometheus-node-exporter.service - Prometheus Node Exporter
     Active: active (running) since Tue 2026-11-03 09:30:15 +07

542
```

### 10.3 ติดตั้ง postgres_exporter

```bash
/opt/pea/bin/postgres_exporter --version
```

ผลลัพธ์:
```text
postgres_exporter, version 0.18.0 (branch: HEAD, revision: ...)
  build user:       root@build
  build date:       20261015-12:00:00
  go version:       go1.22.5
```

### 10.4 ตั้งค่า Unit

```bash
sudo cp /opt/pea/units/postgres_exporter.service /etc/systemd/system/
sudo nano /etc/systemd/system/postgres_exporter.service
```

**เนื้อหา:**
```ini
[Unit]
Description=Prometheus PostgreSQL Exporter
After=network.target

[Service]
Type=simple
User=postgres
Group=postgres
EnvironmentFile=/etc/default/postgres_exporter
ExecStart=/opt/pea/bin/postgres_exporter \
  --web.listen-address=:9187 \
  --collector.database_wraparound \
  --collector.long_running_transactions \
  --collector.stat_checkpointer \
  --collector.stat_statements \
  --collector.postmaster
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 10.5 ตั้ง `DATA_SOURCE_NAME`

```bash
sudo truncate -s 0 /etc/default/postgres_exporter
sudo nano /etc/default/postgres_exporter
```

**เนื้อหา:**
```bash
DATA_SOURCE_NAME=postgresql://pgexporter:Lab-Exporter-2569@127.0.0.1:5432/gridcare?sslmode=require
```

```bash
sudo chmod 600 /etc/default/postgres_exporter
sudo systemctl daemon-reload
sudo systemctl enable --now postgres_exporter
```

### 10.6 ตรวจสอบ Metric

```bash
curl -s localhost:9187/metrics | grep -E '^pg_up|^pg_database_wraparound_age_datfrozenxid_seconds' | head
```

ผลลัพธ์:
```text
pg_up 1
pg_database_wraparound_age_datfrozenxid_seconds{datname="gridcare"} 152345
pg_database_wraparound_age_datfrozenxid_seconds{datname="postgres"} 45012
pg_database_wraparound_age_datfrozenxid_seconds{datname="template1"} 45012
```

### 10.7 Collector ที่มีประโยชน์

| Collector | หน้าที่ |
|---|---|
| `database_wraparound` | XID Age |
| `long_running_transactions` | Transaction ที่ค้าง |
| `stat_checkpointer` | Checkpoint |
| `stat_statements` | Query จาก `pg_stat_statements` |
| `postmaster` | Process ของ PostgreSQL |
| `stat_database` | Database Statistics |
| `stat_user_tables` | Table Statistics |
| `locks` | Lock |

### 10.8 ตาราง Collector ที่ควรเปิด

| Collector | เปิด | เหตุผล |
|---|---|---|
| `database_wraparound` | ✅ | XID |
| `long_running_transactions` | ✅ | Transaction ค้าง |
| `stat_checkpointer` | ✅ | Checkpoint |
| `stat_statements` | ⚠️ | Cardinality สูง — เปิดเฉพาะเมื่อจำเป็น |
| `postmaster` | ✅ | Process |
| `locks` | ⚠️ | Cardinality สูง |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: ตรวจ Metric ที่ Export

```bash
curl -s localhost:9187/metrics | grep '^pg_' | wc -l
```

ผลลัพธ์:
```text
542
```

### ตัวอย่างที่ 2: ตรวจ Metric สำคัญ

```bash
curl -s localhost:9187/metrics | grep -E '^pg_up|^pg_stat_database_xact_commit|^pg_stat_activity_count' | head
```

ผลลัพธ์:
```text
pg_up 1
pg_stat_activity_count{datname="gridcare",state="active"} 3
pg_stat_activity_count{datname="gridcare",state="idle"} 5
pg_stat_database_xact_commit{datname="gridcare"} 1234567
```

### ตัวอย่างที่ 3: ตรวจ Log

```bash
sudo journalctl -u postgres_exporter -n 10 --no-pager
```

ผลลัพธ์:
```text
Nov 03 09:30:15 ta1-pg1 postgres_exporter[1234]: ts=2026-11-03T09:30:15.123Z caller=main.go:458 level=info msg="Listening on" address=[::]:9187
```

## 12. สรุปย่อ จำง่าย
- **Role `pgexporter` + `pg_monitor`**  
- **`DATA_SOURCE_NAME` ต้อง `chmod 600`**  
- **Collector เปิดเฉพาะที่ใช้**  
- **`pg_up` ต้องเป็น 1**  
- **ตรวจ Metric ด้วย `curl`**  
- **TLS ต้องเปิดใน Production**

ประโยคจำ: **“postgres_exporter คือล่ามที่แปลภาษา PostgreSQL ให้ Prometheus เข้าใจ”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- postgres_exporter: https://github.com/prometheus-community/postgres_exporter
- GridCare Workshop Day 2: Lab 3.1

---

# บทที่ 43 node_exporter

## 1. เรื่อง
`node_exporter` สำหรับเก็บ Metric ของระบบ Linux ที่ PostgreSQL ทำงานอยู่

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้ติดตั้งและใช้งาน `node_exporter`  
2. เพื่อให้เลือก Metric สำคัญของระบบ  
3. เพื่อให้ผูก Metric กับ Alert ของ Disk, CPU, Memory  
4. เพื่อให้ใช้ Metric ใน Dashboard

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ติดตั้ง `prometheus-node-exporter`  
- ตรวจ Metric ด้วย `curl localhost:9100/metrics`  
- ใช้ Metric `node_filesystem_avail_bytes`, `node_cpu_seconds_total`  
- ตั้ง Alert Disk และ CPU

## 4. เนื้อหาโดยย่อ
`node_exporter` เก็บ Metric ของ Linux:
- CPU  
- Memory  
- Disk  
- Network  
- Filesystem  
- Load  
- Process

Port มาตรฐาน: 9100

## 5. ประโยชน์ที่ได้รับ
- รู้ว่า Disk ใกล้เต็ม  
- รู้ว่า CPU สูง  
- รู้ว่า Memory ต่ำ  
- รู้ Network  
- ใช้ Alert ก่อนระบบล่ม

## 6. ข้อควรระวัง
- **`node_filesystem_avail_bytes` มี Label `mountpoint`**  
- **Disk เต็มทำให้ PostgreSQL ล่ม**  
- **Memory ต่ำทำให้ OOM**  
- **CPU สูงอาจเป็น Query ที่ไม่ดี**  
- **Metric ที่ Cardinality สูง เช่น Process ควรปิด**

## 7. ข้อดี
- มาตรฐาน  
- Metric ครบ  
- ใช้ร่วมกับ Grafana ได้  
- Alert ได้ง่าย

## 8. ข้อเสีย
- Metric มาก  
- ต้องเลือกใช้  
- ต้องตั้ง Alert ให้เหมาะ

## 9. ข้อห้าม
- ห้ามเปิด Collector ที่ไม่ใช้  
- ห้าม Alert CPU จาก `node_cpu_seconds_total` โดยตรง (ต้อง `rate()`)  
- ห้าม Alert Disk ที่ Mountpoint ที่ไม่ใช่ PGDATA  
- ห้ามใช้ `node_load1` กับ CPU หลาย Core โดยไม่ Normalize

## 10. รายละเอียด

### 10.1 ติดตั้ง

```bash
sudo apt install -y prometheus-node-exporter
systemctl status prometheus-node-exporter --no-pager | head -3
```

ผลลัพธ์:
```text
● prometheus-node-exporter.service - Prometheus Node Exporter
     Loaded: loaded (/lib/systemd/system/prometheus-node-exporter.service; enabled)
     Active: active (running) since Tue 2026-11-03 09:30:15 +07
```

### 10.2 ตรวจ Metric

```bash
curl -s localhost:9100/metrics | grep -c '^node_'
```

ผลลัพธ์:
```text
542
```

### 10.3 Metric สำคัญ

| Metric | ใช้กับ |
|---|---|
| `node_cpu_seconds_total{mode="idle"}` | CPU Usage |
| `node_memory_MemAvailable_bytes` | Memory Available |
| `node_filesystem_avail_bytes{mountpoint="/"}` | Disk Available |
| `node_filesystem_size_bytes{mountpoint="/"}` | Disk Size |
| `node_load1`, `node_load5`, `node_load15` | Load Average |
| `node_network_receive_bytes_total` | Network |
| `node_disk_io_time_seconds_total` | Disk I/O |
| `node_uname_info` | OS Info |

### 10.4 PromQL ที่ใช้บ่อย

```promql
# CPU Usage %
100 - avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100

# Memory Available %
node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes * 100

# Disk Available %
node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"} * 100

# Disk Predicted Full in 24h
predict_linear(node_filesystem_avail_bytes{mountpoint="/"}[6h], 24*3600) < 0
```

### 10.5 Alert Disk

```yaml
- alert: DiskSpaceLow
  expr: node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"} < 0.15
  for: 5m
  labels: {severity: critical, owner: cloud}
  annotations:
    summary: "Disk / บน {{ $labels.instance }} เหลือ < 15%"
    runbook_url: "http://gridcare-infra/runbooks/C04-disk-full.md"

- alert: DiskWillFillIn24h
  expr: predict_linear(node_filesystem_avail_bytes{mountpoint="/"}[6h], 24*3600) < 0
  for: 10m
  labels: {severity: warning, owner: cloud}
  annotations:
    summary: "Disk / จะเต็มภายใน 24 ชั่วโมง"
    runbook_url: "http://gridcare-infra/runbooks/C04-disk-full.md"
```

### 10.6 Alert CPU

```yaml
- alert: PostgreSQLHighCPU
  expr: |
    100 - avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100 > 80
  for: 10m
  labels: {severity: warning, owner: dba}
  annotations:
    summary: "CPU ของ {{ $labels.instance }} สูงเกิน 80%"
    runbook_url: "http://gridcare-infra/runbooks/C06-oom-temp-spill.md"
```

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: ตรวจ Metric Disk

```bash
curl -s localhost:9100/metrics | grep 'node_filesystem_avail_bytes{mountpoint="/"}'
```

ผลลัพธ์:
```text
node_filesystem_avail_bytes{device="/dev/sda1",fstype="ext4",mountpoint="/"} 67633152000
```

### ตัวอย่างที่ 2: ตรวจ CPU

```bash
curl -s localhost:9100/metrics | grep '^node_cpu_seconds_total' | head -5
```

ผลลัพธ์:
```text
node_cpu_seconds_total{cpu="0",mode="idle"} 123456.78
node_cpu_seconds_total{cpu="0",mode="iowait"} 1234.56
node_cpu_seconds_total{cpu="0",mode="system"} 5678.90
node_cpu_seconds_total{cpu="0",mode="user"} 8901.23
```

### ตัวอย่างที่ 3: ตรวจ Memory

```bash
curl -s localhost:9100/metrics | grep 'node_memory_MemAvailable_bytes'
```

ผลลัพธ์:
```text
node_memory_MemAvailable_bytes 3.142857e+09
```

## 12. สรุปย่อ จำง่าย
- **`node_exporter` Port 9100**  
- **Metric สำคัญ: CPU, Memory, Disk, Network**  
- **`node_filesystem_avail_bytes` คือ Metric Disk ที่ต้อง Alert**  
- **ใช้ `rate()` กับ `node_cpu_seconds_total`**  
- **`predict_linear` ทำนาย Disk เต็ม**  
- **Alert Disk และ CPU เป็น Baseline**

ประโยคจำ: **“node_exporter บอกว่าระบบยังมีลมหายใจไหม”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- node_exporter: https://github.com/prometheus/node_exporter
- GridCare Workshop Day 2: Lab 3.1

---

# บทที่ 44 Prometheus Scrape Configuration

## 1. เรื่อง
การตั้งค่า `scrape_config` ใน Prometheus สำหรับ PostgreSQL, Node Exporter และ Patroni

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เขียน `prometheus.yml` ที่ใช้งานได้จริง  
2. เพื่อให้ใช้ `promtool check config`  
3. เพื่อให้เลือก Target และ Label ที่ดี  
4. เพื่อให้ตรวจสอบ Target Health

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- เขียน `scrape_configs` สำหรับ PostgreSQL, Node และ Patroni  
- เพิ่ม Label ให้ Metric  
- ใช้ `promtool check config`  
- ตรวจ Target Health ด้วย API

## 4. เนื้อหาโดยย่อ
`scrape_configs` ประกอบด้วย:
- `job_name`  
- `scrape_interval` (optional)  
- `static_configs` หรือ `file_sd_configs`  
- `relabel_configs` (optional)

Target ที่ควรมี:
- `prometheus` (self)  
- `node` (pg1, pg2, infra)  
- `postgres` (pg1, pg2)  
- `patroni` (pg1, pg2)

## 5. ประโยชน์ที่ได้รับ
- Prometheus เก็บ Metric ครบ  
- Target Health ตรวจได้  
- Label ช่วยกรอง  
- Config ตรวจสอบได้ด้วย `promtool`

## 6. ข้อควรระวัง
- **`scrape_interval` สั้นเกินไปทำให้โหลดสูง**  
- **Target ที่ Down ทำให้ Alert False Positive**  
- **Label ที่ Cardinality สูงทำให้ Prometheus หนัก**  
- **`static_configs` ต้อง Update เมื่อ Target เปลี่ยน**  
- **`file_sd_configs` เหมาะกับ Dynamic Target**

## 7. ข้อดี
- Config ตรงไปตรงมา  
- ตรวจสอบได้ด้วย `promtool`  
- Target Health ดูได้จาก UI

## 8. ข้อเสีย
- `static_configs` ต้องแก้มือ  
- Target ที่เปลี่ยน IP ต้อง Update

## 9. ข้อห้าม
- ห้าม `scrape_interval: 1s`  
- ห้ามใช้ Label ที่ Cardinality สูง  
- ห้ามลืม `promtool check config`  
- ห้ามปล่อย Target Down โดยไม่ตรวจ  
- ห้ามใช้ `static_configs` กับ Dynamic Environment โดยไม่ใช้ `file_sd`

## 10. รายละเอียด

### 10.1 `prometheus.yml` ตัวอย่างสมบูรณ์

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
        labels:
          role: node

  - job_name: postgres
    static_configs:
      - targets: ['pg1:9187', 'pg2:9187']
        labels:
          role: database

  - job_name: patroni
    static_configs:
      - targets: ['pg1:8008', 'pg2:8008']
        labels:
          role: ha
```

### 10.2 `promtool check config`

```bash
promtool check config /etc/prometheus/prometheus.yml
```

ผลลัพธ์:
```text
Checking /etc/prometheus/prometheus.yml
  SUCCESS: 5 scrape configs found
```

### 10.3 Reload Prometheus

```bash
sudo systemctl reload prometheus
```

### 10.4 ตรวจ Target Health

```bash
curl -s localhost:9090/api/v1/targets | python3 -m json.tool | grep -E '"scrapeUrl"|"health"'
```

ผลลัพธ์:
```text
"scrapeUrl": "http://localhost:9090/metrics",
"health": "up"
"scrapeUrl": "http://pg1:9100/metrics",
"health": "up"
"scrapeUrl": "http://infra:9100/metrics",
"health": "up"
"scrapeUrl": "http://pg1:9187/metrics",
"health": "up"
"scrapeUrl": "http://pg2:9187/metrics",
"health": "up"
"scrapeUrl": "http://pg1:8008/metrics",
"health": "up"
"scrapeUrl": "http://pg2:8008/metrics",
"health": "up"
```

### 10.5 `file_sd_configs` สำหรับ Dynamic

```yaml
  - job_name: postgres
    file_sd_configs:
      - files:
          - /etc/prometheus/targets/postgres.json
        refresh_interval: 30s
```

**`/etc/prometheus/targets/postgres.json`:**
```json
[
  {
    "targets": ["pg1:9187", "pg2:9187"],
    "labels": {
      "cluster": "gridcare",
      "role": "database"
    }
  }
]
```

### 10.6 Relabel ที่มีประโยชน์

```yaml
  - job_name: node
    static_configs:
      - targets: ['pg1:9100', 'pg2:9100', 'infra:9100']
    relabel_configs:
      - source_labels: [__address__]
        regex: '([^:]+):.*'
        target_label: instance_name
        replacement: '$1'
```

### 10.7 ตาราง Target ที่ควรมี

| Job | Target | Port | Label |
|---|---|---|---|
| prometheus | localhost | 9090 | - |
| node | pg1, pg2, infra | 9100 | role=node |
| postgres | pg1, pg2 | 9187 | role=database |
| patroni | pg1, pg2 | 8008 | role=ha |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: ตรวจ Config

```bash
promtool check config /etc/prometheus/prometheus.yml
```

ผลลัพธ์:
```text
Checking /etc/prometheus/prometheus.yml
  SUCCESS: 5 scrape configs found
```

### ตัวอย่างที่ 2: ตรวจ Target ที่ Down

```bash
curl -s localhost:9090/api/v1/targets?state=down | python3 -m json.tool | grep -E '"scrapeUrl"|"lastError"'
```

ผลลัพธ์ (ถ้ามี Down):
```text
"scrapeUrl": "http://pg2:9187/metrics",
"lastError": "Get \"http://pg2:9187/metrics\": dial tcp: connect: connection refused"
```

### ตัวอย่างที่ 3: ตรวจ Target Health

```bash
curl -s localhost:9090/api/v1/targets | python3 -c "
import sys,json
d=json.load(sys.stdin)
for t in d['data']['activeTargets']:
    print(t['labels']['job'], t['scrapeUrl'], t['health'])
"
```

ผลลัพธ์:
```text
prometheus http://localhost:9090/metrics up
node http://pg1:9100/metrics up
node http://pg2:9100/metrics up
node http://infra:9100/metrics up
postgres http://pg1:9187/metrics up
postgres http://pg2:9187/metrics up
patroni http://pg1:8008/metrics up
patroni http://pg2:8008/metrics up
```

## 12. สรุปย่อ จำง่าย
- **`scrape_configs` = Target + Interval + Label**  
- **`promtool check config`** ก่อน Reload  
- **ตรวจ Target Health ด้วย API**  
- **`file_sd_configs` สำหรับ Dynamic**  
- **`relabel_configs` สำหรับ Label**  
- **Target ต้องครบ: prometheus, node, postgres, patroni**

ประโยคจำ: **“Prometheus ที่ดีคือ Prometheus ที่ Target ครบและ Health ดี”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- Prometheus Configuration: https://prometheus.io/docs/prometheus/latest/configuration/configuration/
- GridCare Workshop Day 2: Lab 3.1, Day 4: Lab 4.1

---

# บทที่ 45 PromQL พื้นฐาน

## 1. เรื่อง
ภาษา PromQL สำหรับ Query Metric ใน Prometheus พื้นฐาน

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจ Selector, Operator, Function  
2. เพื่อให้ใช้ `rate()`, `increase()`, `sum by()`, `avg by()`  
3. เพื่อให้ Query Metric ที่พบบ่อย  
4. เพื่อให้เข้าใจ Counter vs Gauge

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- เขียน Selector ที่มี Label  
- ใช้ `rate()`, `increase()`, `irate()`  
- ใช้ `sum by()`, `avg by()`, `topk()`  
- ใช้ `histogram_quantile()`  
- หลีกเลี่ยง `rate()` กับ Gauge

## 4. เนื้อหาโดยย่อ
PromQL มี:
- **Selector** — เลือก Series  
- **Operator** — คำนวณ  
- **Function** — แปลงข้อมูล  
- **Aggregation** — รวมกลุ่ม

ตัวอย่าง:
```promql
rate(pg_stat_database_xact_commit{datname="gridcare"}[5m])
```

## 5. ประโยชน์ที่ได้รับ
- Query Metric ได้  
- สร้าง Dashboard ได้  
- สร้าง Alert Rule ได้  
- วิเคราะห์ข้อมูลได้

## 6. ข้อควรระวัง
- **`rate()` ใช้กับ Counter เท่านั้น**  
- **`rate()` ต้องมี Range ≥ 2 Samples**  
- **`sum by()` ต้องมี Label ที่ต้องการ Group**  
- **`topk()` ต้องมี `k`**  
- **`histogram_quantile()` ต้องมี `le` Label**

## 7. ข้อดี
- ยืดหยุ่นสูง  
- ใช้ได้กับทุก Metric  
- ใช้ใน Alert Rule ได้

## 8. ข้อเสีย
- Syntax ต้องจำ  
- Function เยอะ  
- ต้องเข้าใจ Type ของ Metric

## 9. ข้อห้าม
- ห้าม `rate()` กับ Gauge  
- ห้าม `sum()` โดยไม่มี `by()` เมื่อต้องการแยกมิติ  
- ห้าม `rate()` กับ Range ที่เล็กเกินไป  
- ห้ามใช้ `irate()` กับ Alert ที่ต้องการเสถียร  
- ห้ามใช้ `topk()` โดยไม่ระบุ `k`

## 10. รายละเอียด

### 10.1 Selector

```promql
# เลือก Series ทั้งหมด
pg_up

# เลือกเฉพาะ datname
pg_up{datname="gridcare"}

# เลือกด้วย Regex
pg_up{instance=~"pg.*"}
```

### 10.2 Operators

| Operator | ใช้ |
|---|---|
| `+ - * /` | คำนวณ |
| `== != > < >= <=` | เปรียบเทียบ |
| `and or unless` | Logic |

### 10.3 Functions ที่ใช้บ่อย

| Function | Type | ใช้ |
|---|---|---|
| `rate()` | Counter | อัตราต่อวินาที |
| `irate()` | Counter | อัตรา瞬时 |
| `increase()` | Counter | เพิ่มขึ้นในช่วง |
| `sum by()` | Aggregation | รวมกลุ่ม |
| `avg by()` | Aggregation | เฉลี่ยกลุ่ม |
| `topk()` | Aggregation | Top K |
| `count()` | Aggregation | นับ |
| `histogram_quantile()` | Histogram | Quantile |
| `predict_linear()` | Gauge | ทำนาย |
| `delta()` | Gauge | เปลี่ยนแปลง |
| `abs()` | - | ค่าสัมบูรณ์ |

### 10.4 Counter vs Gauge

| Type | ตัวอย่าง | ใช้ |
|---|---|---|
| Counter | `pg_stat_database_xact_commit` | `rate()`, `increase()` |
| Gauge | `pg_up`, `pg_stat_activity_count` | ค่าตรง |

### 10.5 ตัวอย่าง PromQL ที่ใช้บ่อย

```promql
# TPS
sum by (datname) (
  rate(pg_stat_database_xact_commit{datname="gridcare"}[1m])
  + rate(pg_stat_database_xact_rollback{datname="gridcare"}[1m])
)

# Connections ตามสถานะ
sum by (state) (pg_stat_activity_count{datname="gridcare"})

# Cache Hit Ratio
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

# CPU %
100 - avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100

# Memory Available %
node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes * 100

# Disk Available %
node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"} * 100

# Top 5 Query by Total Time
topk(5, rate(pg_stat_statements_seconds_total{datname="gridcare"}[5m]))
```

### 10.6 Counter vs `rate()`

**ผิด:**
```promql
rate(pg_up[5m])  -- pg_up เป็น Gauge
```

**ถูก:**
```promql
pg_up == 0
```

### 10.7 `histogram_quantile()`

```promql
histogram_quantile(0.95,
  rate(pg_stat_statements_mean_exec_time_seconds_bucket[5m])
)
```

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Query TPS

```promql
sum by (datname) (
  rate(pg_stat_database_xact_commit{datname="gridcare"}[1m])
  + rate(pg_stat_database_xact_rollback{datname="gridcare"}[1m])
)
```

ผลลัพธ์:
```text
{datname="gridcare"} 149.7
```

### ตัวอย่างที่ 2: Query Connection

```promql
sum by (state) (pg_stat_activity_count{datname="gridcare"})
```

ผลลัพธ์:
```text
{state="active"} 12
{state="idle"} 45
{state="idle in transaction"} 2
```

### ตัวอย่างที่ 3: Query Cache Hit

```promql
rate(pg_stat_database_blks_hit{datname="gridcare"}[5m])
/
(
  rate(pg_stat_database_blks_hit{datname="gridcare"}[5m])
  + rate(pg_stat_database_blks_read{datname="gridcare"}[5m])
)
```

ผลลัพธ์:
```text
{datname="gridcare"} 0.997
```

### ตัวอย่างที่ 4: Query Disk

```promql
node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}
```

ผลลัพธ์:
```text
{instance="pg1:9100",mountpoint="/"} 0.81
```

### ตัวอย่างที่ 5: Top 5 Query

```promql
topk(5, rate(pg_stat_statements_seconds_total{datname="gridcare"}[5m]))
```

## 12. สรุปย่อ จำง่าย
- **Selector = Metric + Label**  
- **Counter ใช้ `rate()` / Gauge ใช้ค่าตรง**  
- **`sum by()` สำหรับ Group**  
- **`topk()` สำหรับ Top N**  
- **`histogram_quantile()` สำหรับ Quantile**  
- **`rate()` ต้องมี Range ≥ 2 Samples**

ประโยคจำ: **“PromQL ที่ดีคือ PromQL ที่รู้ว่า Metric เป็น Counter หรือ Gauge”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- Prometheus Documentation — Querying Basics: https://prometheus.io/docs/prometheus/latest/querying/basics/
- Prometheus Documentation — Functions: https://prometheus.io/docs/prometheus/latest/querying/functions/
- GridCare Workshop Day 2: Lab 3.2

---

# บทที่ 46 PromQL ขั้นสูง

## 1. เรื่อง
PromQL ขั้นสูงสำหรับงาน Monitoring ที่ซับซ้อน เช่น `subquery`, `label_replace`, `absent()`, `predict_linear()`

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้ใช้ Function ขั้นสูงได้  
2. เพื่อให้สร้าง Alert ที่ซับซ้อน  
3. เพื่อให้สร้าง Metric ที่ยังไม่มี  
4. เพื่อให้วิเคราะห์ข้อมูลเชิงลึก

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ใช้ `absent()` ตรวจ Metric ที่หายไป  
- ใช้ `predict_linear()` ทำนาย Disk เต็ม  
- ใช้ `label_replace()` ปรับ Label  
- ใช้ `subquery` ในการคำนวณ  
- ใช้ `increase()` กับ Counter

## 4. เนื้อหาโดยย่อ
Function ขั้นสูง:
- **`absent()`** — ตรวจ Metric ที่หาย  
- **`predict_linear()`** — ทำนาย  
- **`label_replace()`** — ปรับ Label  
- **`label_join()`** — รวม Label  
- **`subquery`** — Query ซ้อน  
- **`@`** — Time modifier

## 5. ประโยชน์ที่ได้รับ
- Alert ที่ซับซ้อนได้  
- Metric ที่ยังไม่มี  
- วิเคราะห์เชิงลึก  
- ปรับ Label ให้ตรงกับ Dashboard

## 6. ข้อควรระวัง
- **`absent()` ต้องใช้กับ Metric ที่ควรมี**  
- **`predict_linear()` ต้องมีข้อมูลพอ**  
- **`label_replace()` ต้องมี Regex ที่ถูก**  
- **`subquery` ทำให้ Query หนัก**  
- **`@` ใช้กับ Time ที่ต้องการ Fix**

## 7. ข้อดี
- สร้าง Metric ที่ยังไม่มี  
- Alert ที่ซับซ้อน  
- วิเคราะห์เชิงลึก

## 8. ข้อเสีย
- Syntax ซับซ้อน  
- Query หนัก  
- ต้องเข้าใจ Type

## 9. ข้อห้าม
- ห้าม `absent()` กับ Metric ที่ไม่ควรมี  
- ห้าม `predict_linear()` กับข้อมูลน้อยกว่า 2 Samples  
- ห้าม `subquery` ที่ซ้อนลึกเกิน  
- ห้าม `@` ที่ไม่จำเป็น

## 10. รายละเอียด

### 10.1 `absent()`

```promql
absent(pg_up{instance="pg1:9187"})
```

> ✅ คืนค่า `1` ถ้า Metric หาย → ใช้ Alert "Exporter Down"

```yaml
- alert: PostgresExporterDown
  expr: absent(pg_up{instance=~"pg.*"})
  for: 2m
  labels: {severity: critical, owner: devops}
  annotations:
    summary: "ไม่พบ Metric pg_up จาก {{ $labels.instance }}"
    runbook_url: "http://gridcare-infra/runbooks/C11-monitoring.md"
```

### 10.2 `predict_linear()`

```promql
predict_linear(node_filesystem_avail_bytes{mountpoint="/"}[6h], 24*3600) < 0
```

> ✅ คืนค่า `true` ถ้า Disk จะเต็มภายใน 24 ชั่วโมง

### 10.3 `label_replace()`

```promql
label_replace(pg_up, "db_host", "$1", "instance", "(.*):.*")
```

> ✅ เพิ่ม Label `db_host` จาก `instance`

### 10.4 `label_join()`

```promql
label_join(pg_up, "full_name", "-", "cluster", "instance")
```

> ✅ รวม Label `cluster` และ `instance` เป็น `full_name`

### 10.5 `subquery`

```promql
max_over_time(
  rate(pg_stat_database_xact_commit{datname="gridcare"}[1m])[1h:1m]
)
```

> ✅ หาค่าสูงสุดใน 1 ชั่วโมงที่ผ่านมา

### 10.6 `@` Time Modifier

```promql
pg_up @ 1730702112
```

> ✅ Query ที่ Time ที่กำหนด (Unix Timestamp)

### 10.7 `increase()` กับ Counter

```promql
increase(pg_stat_database_xact_commit{datname="gridcare"}[1h])
```

> ✅ จำนวน Commit ใน 1 ชั่วโมงที่ผ่านมา

### 10.8 `delta()` กับ Gauge

```promql
delta(pg_stat_activity_count{datname="gridcare"}[10m])
```

> ✅ การเปลี่ยนแปลงของ Connection ใน 10 นาที

### 10.9 `holt_winters()` (ถ้ามี)

```promql
holt_winters(rate(pg_stat_database_xact_commit[5m]), 0.5, 0.5)
```

> ✅ พยากรณ์ TPS

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Alert ที่ใช้ `absent()`

```yaml
- alert: PostgresExporterDown
  expr: absent(pg_up{instance=~"pg.*"})
  for: 2m
  labels: {severity: critical, owner: devops}
  annotations:
    summary: "ไม่พบ Metric pg_up จาก {{ $labels.instance }}"
    runbook_url: "http://gridcare-infra/runbooks/C11-monitoring.md"
```

### ตัวอย่างที่ 2: Alert Disk จะเต็ม

```yaml
- alert: DiskWillFillIn24h
  expr: predict_linear(node_filesystem_avail_bytes{mountpoint="/"}[6h], 24*3600) < 0
  for: 10m
  labels: {severity: warning, owner: cloud}
  annotations:
    summary: "Disk / จะเต็มภายใน 24 ชั่วโมง"
    runbook_url: "http://gridcare-infra/runbooks/C04-disk-full.md"
```

### ตัวอย่างที่ 3: TPS สูงสุดใน 1 ชั่วโมง

```promql
max_over_time(
  sum by (datname) (
    rate(pg_stat_database_xact_commit{datname="gridcare"}[1m])
    + rate(pg_stat_database_xact_rollback{datname="gridcare"}[1m])
  )[1h:1m]
)
```

### ตัวอย่างที่ 4: รวม Label

```promql
label_replace(pg_up, "role", "database", "job", "postgres")
```

### ตัวอย่างที่ 5: Counter Increase

```promql
increase(pg_stat_database_xact_commit{datname="gridcare"}[1h])
```

ผลลัพธ์:
```text
{datname="gridcare"} 540000
```

## 12. สรุปย่อ จำง่าย
- **`absent()` = Alert Metric หาย**  
- **`predict_linear()` = ทำนาย Disk เต็ม**  
- **`label_replace()` = ปรับ Label**  
- **`subquery` = Query ซ้อน**  
- **`@` = Time Modifier**  
- **`increase()` = Counter ในช่วง**

ประโยคจำ: **“PromQL ขั้นสูงทำให้ Metric ธรรมดา กลายเป็นข้อมูลเชิงลึก”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- Prometheus Documentation — Functions: https://prometheus.io/docs/prometheus/latest/querying/functions/
- Prometheus Documentation — Subquery: https://prometheus.io/docs/prometheus/latest/querying/basics/#subquery
- Prometheus Documentation — @ Modifier: https://prometheus.io/docs/prometheus/latest/querying/basics/#modifier

---

# บทที่ 47 Grafana Dashboard

## 1. เรื่อง
การสร้าง Dashboard ใน Grafana สำหรับ PostgreSQL Production

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้ติดตั้งและตั้งค่า Grafana  
2. เพื่อให้เพิ่ม Data Source Prometheus  
3. เพื่อให้สร้าง Panel ที่มีคุณภาพ  
4. เพื่อให้ Export Dashboard เป็น JSON

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ติดตั้ง Grafana  
- เพิ่ม Prometheus เป็น Data Source  
- สร้าง Panel ที่ใช้ PromQL  
- Export Dashboard

## 4. เนื้อหาโดยย่อ
Grafana Dashboard ที่ดี:
- แถวที่ 1: SLO/KPI  
- แถวที่ 2: Resource  
- แถวที่ 3: Database  
- แถวที่ 4: Top N  
- แถวที่ 5: Alert

Panel ที่แนะนำ:
- Time Series  
- Stat  
- Gauge  
- Table  
- Heatmap

## 5. ประโยชน์ที่ได้รับ
- เห็นภาพรวมระบบ  
- ลดเวลาตรวจสอบ  
- แชร์ให้ทีม  
- ใช้ Alert จาก Grafana

## 6. ข้อควรระวัง
- **Panel ที่ใช้ `rate()` กับ Gauge** ไม่มีความหมาย  
- **Panel ที่ Cardinality สูง** ทำให้ Grafana ช้า  
- **Time Range ที่ใหญ่เกินไป** ทำให้ Query หนัก  
- **Dashboard ที่มี Panel เยอะเกินไป** ทำให้ช้า

## 7. ข้อดี
- ใช้งานง่าย  
- สวยงาม  
- รองรับ Data Source หลายตัว  
- Export/Import ได้

## 8. ข้อเสีย
- ต้องดูแล Dashboard  
- Panel เยอะทำให้ช้า  
- ต้องตั้ง Alert แยกจาก Prometheus

## 9. ข้อห้าม
- ห้าม Panel ที่ไม่มีหน่วย  
- ห้าม Panel ที่ไม่มี Legend  
- ห้าม Panel ที่ใช้ Gauge กับ `rate()`  
- ห้าม Dashboard ที่ไม่ Reviewed  
- ห้าม Panel ที่ Cardinality สูง

## 10. รายละเอียด

### 10.1 ติดตั้ง Grafana

```bash
sudo apt install -y grafana
sudo systemctl enable --now grafana-server
systemctl status grafana-server --no-pager | head -3
```

ผลลัพธ์:
```text
● grafana-server.service - Grafana instance
     Loaded: loaded (/lib/systemd/system/grafana-server.service; enabled)
     Active: active (running) since Tue 2026-11-03 10:15:30 +07
```

### 10.2 เพิ่ม Data Source

1. Login: `admin` / `admin` → ตั้งรหัสผ่านใหม่  
2. **Connections > Data sources > Add data source > Prometheus**  
3. URL: `http://localhost:9090`  
4. **Save & test**

### 10.3 สร้าง Dashboard

1. **Dashboards > New dashboard** → ตั้งชื่อ `GridCare PostgreSQL`  
2. Time range: `Last 1 hour`  
3. เพิ่ม Panel ตามตาราง

### 10.4 Panel ที่แนะนำ

| Panel | PromQL | หน่วย | Legend |
|---|---|---|---|
| TPS | `sum by (datname) (rate(pg_stat_database_xact_commit{datname="gridcare"}[1m]) + rate(pg_stat_database_xact_rollback{datname="gridcare"}[1m]))` | ops/s | `{{datname}}` |
| Connections | `sum by (state) (pg_stat_activity_count{datname="gridcare"})` | count | `{{state}}` |
| Cache Hit | `rate(pg_stat_database_blks_hit{datname="gridcare"}[5m]) / (rate(...hit...) + rate(...read...))` | % | `cache_hit` |
| Top Query | `topk(5, rate(pg_stat_statements_seconds_total{datname="gridcare"}[5m]))` | s | `{{queryid}}` |
| Dead Tuple | `topk(5, pg_stat_user_tables_n_dead_tup{schemaname="gridcare"})` | count | `{{relname}}` |
| XID Age | `pg_database_wraparound_age_datfrozenxid_seconds` | s | `{{datname}}` |
| CPU | `100 - avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[1m])) * 100` | % | `{{instance}}` |
| Disk | `node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}` | % | `{{instance}}` |

### 10.5 Panel Settings

- **Unit:** เลือกให้ถูก เช่น `ops/s`, `bytes`, `%`, `s`  
- **Legend:** ใช้ `{{label}}`  
- **Thresholds:** Critical = แดง, Warning = เหลือง  
- **Time Range:** `Last 1 hour` สำหรับ Dashboard ทั่วไป

### 10.6 Export Dashboard

**Dashboard > Export > Export as JSON** → บันทึก `gridcare-postgres-dashboard.json`

### 10.7 Import Dashboard

**Dashboards > Import** → Upload JSON → เลือก Data Source → Import

### 10.8 Dashboard ที่แนะนำให้มี

| Dashboard | ใช้กับ |
|---|---|
| GridCare PostgreSQL | DBA Daily |
| GridCare Node | Cloud/DevOps |
| GridCare HA | DBA + DevOps |
| GridCare Alert Status | ทั้งทีม |
| GridCare Slow Query | DBA |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: TPS Panel

```promql
sum by (datname) (
  rate(pg_stat_database_xact_commit{datname="gridcare"}[1m])
  + rate(pg_stat_database_xact_rollback{datname="gridcare"}[1m])
)
```

ผลลัพธ์:
```text
datname="gridcare" → 149.7 ops/s
```

### ตัวอย่างที่ 2: Connections Panel

```promql
sum by (state) (pg_stat_activity_count{datname="gridcare"})
```

ผลลัพธ์:
```text
state="active" → 12
state="idle" → 45
state="idle in transaction" → 2
```

### ตัวอย่างที่ 3: Cache Hit Panel

```promql
rate(pg_stat_database_blks_hit{datname="gridcare"}[5m])
/
(
  rate(pg_stat_database_blks_hit{datname="gridcare"}[5m])
  + rate(pg_stat_database_blks_read{datname="gridcare"}[5m])
)
```

ผลลัพธ์:
```text
datname="gridcare" → 0.997 (99.7%)
```

### ตัวอย่างที่ 4: Disk Panel

```promql
node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"} * 100
```

ผลลัพธ์:
```text
instance="pg1:9100" → 81.2
```

## 12. สรุปย่อ จำง่าย
- **Grafana + Prometheus = Dashboard ที่ดี**  
- **Panel ต้องมี Unit, Legend, Thresholds**  
- **Dashboard ที่ดีเรียงจากบนลงล่าง**  
- **Export JSON เพื่อ Backup**  
- **Import JSON เพื่อ Restore**  
- **Panel ที่ใช้ `rate()` ต้องเป็น Counter**

ประโยคจำ: **“Dashboard ที่ดีทำให้เห็นปัญหาได้ก่อน Alert จะดัง”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- Grafana Documentation: https://grafana.com/docs/
- GridCare Workshop Day 2: Lab 3.2

---

# บทที่ 48 Dashboard สำหรับ DBA และ DevOps

## 1. เรื่อง
การออกแบบ Dashboard ที่เหมาะกับ DBA, DevOps และ Cloud Engineer แต่ละบทบาท

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้ Dashboard ตอบโจทย์แต่ละบทบาท  
2. เพื่อให้ลดเวลาการสืบสวน  
3. เพื่อให้ทุกทีมเห็นภาพเดียวกัน  
4. เพื่อให้ Dashboard มีลำดับความสำคัญ

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ออกแบบ Dashboard สำหรับ DBA  
- ออกแบบ Dashboard สำหรับ DevOps  
- ออกแบบ Dashboard สำหรับ Cloud Engineer  
- ออกแบบ Dashboard สำหรับ On-call

## 4. เนื้อหาโดยย่อ
Dashboard แบ่งตามบทบาท:
- **DBA** — Database Health, Performance, Bloat, Lock, Replication  
- **DevOps** — Availability, Error Rate, Deploy, Exporter  
- **Cloud Engineer** — Disk, Network, IAM, Cost  
- **On-call** — Alert Status, Recent Changes, Runbook

## 5. ประโยชน์ที่ได้รับ
- ลดเวลาสืบสวน  
- ทุกทีมเห็นภาพเดียวกัน  
- ลด Alert Fatigue

## 6. ข้อควรระวัง
- **Dashboard ที่เยอะเกินไปทำให้ไม่มีใครดู**  
- **Dashboard ที่ไม่มีเจ้าของจะเก่า**  
- **Dashboard ที่ไม่ Reviewed จะไม่ตรงกับระบบ**

## 7. ข้อดี
- ตรงกับบทบาท  
- ลดเวลา  
- ทำให้ Onboarding เร็ว

## 8. ข้อเสีย
- ต้องดูแลหลาย Dashboard  
- ต้อง Reviewed เป็นระยะ

## 9. ข้อห้าม
- ห้าม Dashboard ที่ไม่มีเจ้าของ  
- ห้าม Dashboard ที่ไม่มีวันที่ Review  
- ห้าม Dashboard ที่ใช้ Metric ที่ไม่ถูกต้อง

## 10. รายละเอียด

### 10.1 Dashboard สำหรับ DBA

**แถว 1: Availability**
- `pg_up`
- `pg_postmaster_start_time_seconds`
- `pg_settings_max_connections`

**แถว 2: Performance**
- TPS
- Cache Hit Ratio
- Top 5 Query by Total Time
- Temp File

**แถว 3: Health**
- XID Age
- Dead Tuple
- Invalid Index
- Long Running Transaction

**แถว 4: Replication**
- Replication Lag
- Slot Status
- WAL Size

**แถว 5: Backup**
- Backup Age
- WAL Archive Failed Count

### 10.2 Dashboard สำหรับ DevOps

**แถว 1: Availability**
- `pg_up` (ทุก Instance)
- Target Health

**แถว 2: Error**
- Error Rate (จาก Log)
- Failed Connection

**แถว 3: Deploy**
- Restart Count
- Last Deploy Time
- Config Reload

**แถว 4: Exporter**
- Exporter Up
- Scrape Duration
- Scrape Errors

### 10.3 Dashboard สำหรับ Cloud Engineer

**แถว 1: Disk**
- Disk Available %
- Disk Predicted Full
- Disk I/O

**แถว 2: Network**
- Network Throughput
- Network Errors
- Connection Count

**แถว 3: Compute**
- CPU %
- Memory Available %
- Load Average

**แถว 4: Cost**
- Estimated Monthly Cost
- Storage Growth

### 10.4 Dashboard สำหรับ On-call

**แถว 1: Alert Status**
- Firing Alerts
- Silenced Alerts
- Alert Age

**แถว 2: Recent Changes**
- Last Restart
- Last Config Change
- Last Backup

**แถว 3: Runbook**
- Link ไปยัง Runbook
- Link ไปยัง Incident Record

### 10.5 ตาราง Dashboard ที่แนะนำ

| Dashboard | Owner | Review |
|---|---|---|
| GridCare PostgreSQL | DBA | รายเดือน |
| GridCare Node | Cloud Engineer | รายเดือน |
| GridCare HA | DBA + DevOps | รายเดือน |
| GridCare Alert Status | DevOps | รายสัปดาห์ |
| GridCare Slow Query | DBA | รายเดือน |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: DBA Dashboard Panel

```promql
# XID Age
pg_database_wraparound_age_datfrozenxid_seconds

# Dead Tuple
topk(5, pg_stat_user_tables_n_dead_tup{schemaname="gridcare"})

# Replication Lag
max by (instance, application_name) (pg_stat_replication_pg_wal_lsn_diff)

# Temp File
sum by (datname) (rate(pg_stat_database_temp_bytes{datname="gridcare"}[5m]))
```

### ตัวอย่างที่ 2: DevOps Dashboard Panel

```promql
# Up
pg_up

# Target Health
up{job="postgres"}

# Scrape Duration
scrape_duration_seconds{job="postgres"}

# Restart
time() - pg_postmaster_start_time_seconds < 300
```

### ตัวอย่างที่ 3: Cloud Engineer Dashboard Panel

```promql
# Disk
node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"} * 100

# CPU
100 - avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100

# Memory
node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes * 100

# Network
rate(node_network_receive_bytes_total[5m])
```

### ตัวอย่างที่ 4: On-call Dashboard Panel

```promql
# Firing Alerts
ALERTS{alertstate="firing"}

# Alert Age
time() - ALERTS_FOR_STATE

# Recent Restart
time() - pg_postmaster_start_time_seconds
```

## 12. สรุปย่อ จำง่าย
- **DBA Dashboard = Database Health + Performance + Replication**  
- **DevOps Dashboard = Availability + Deploy + Exporter**  
- **Cloud Dashboard = Disk + Network + Compute**  
- **On-call Dashboard = Alert + Recent Changes + Runbook**  
- **ทุก Dashboard ต้องมีเจ้าของและ Reviewed**

ประโยคจำ: **“Dashboard ที่ดีตอบคำถามของคนที่ดู ไม่ใช่ของคนที่สร้าง”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- Grafana Documentation: https://grafana.com/docs/
- Google SRE Book — Monitoring: https://sre.google/sre-book/monitoring-distributed-systems/
- GridCare Workshop Day 2: Lab 3.2, Day 4: Workshop Day 4 ขั้นที่ 1

---

# บทที่ 49 pgBadger และ Log Analytics

## 1. เรื่อง
`pgBadger` สำหรับวิเคราะห์ PostgreSQL Log เพื่อหา Bottleneck และ Pattern ที่ผิดปกติ

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้ติดตั้งและใช้งาน `pgBadger`  
2. เพื่อให้ตั้งค่า Log ให้ `pgBadger` อ่านได้  
3. เพื่อให้อ่าน Report ที่สำคัญ  
4. เพื่อให้ใช้ `--anonymize` เพื่อลด PII

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- รัน `pgBadger` กับ Log  
- อ่าน Overview, Connections, Checkpoints, Temporary Files, Locks  
- ใช้ `--prefix` ให้ตรงกับ `log_line_prefix`  
- ใช้ `--anonymize` เพื่อลด PII

## 4. เนื้อหาโดยย่อ
`pgBadger` เป็น Perl Script ที่:
- อ่าน Log PostgreSQL  
- สร้าง HTML Report  
- แสดง Top Query, Connection, Checkpoint, Lock, Temp File

ต้องตั้ง `log_line_prefix` ให้ตรงกับ `--prefix` ของ `pgBadger`

## 5. ประโยชน์ที่ได้รับ
- วิเคราะห์ Log ได้  
- เห็น Top Query  
- เห็น Connection Pattern  
- เห็น Checkpoint  
- เห็น Lock Wait  
- เห็น Temp File

## 6. ข้อควรระวัง
- **`--prefix` ต้องตรงกับ `log_line_prefix`**  
- **`log_min_duration_statement` ต้องตั้ง**  
- **`log_lock_waits` ต้องตั้ง**  
- **`log_checkpoints` ต้องตั้ง**  
- **`--anonymize` เพื่อลด PII**

## 7. ข้อดี
- HTML Report สวยงาม  
- ใช้ได้กับ Log ที่มีอยู่  
- วิเคราะห์ได้หลายมิติ  
- `--anonymize` ลด PII

## 8. ข้อเสีย
- ต้องตั้ง Log ให้ถูก  
- Log ใหญ่ใช้เวลานาน  
- ไม่ Real-time

## 9. ข้อห้าม
- ห้าม `--prefix` ไม่ตรงกับ `log_line_prefix`  
- ห้ามใช้ Log ที่ไม่มี `log_min_duration_statement`  
- ห้าม `--anonymize` ไม่เปิดใน Log ที่มี PII  
- ห้ามใช้ Log ที่ไม่ Rotate

## 10. รายละเอียด

### 10.1 ติดตั้ง

```bash
sudo apt install -y pgbadger
```

### 10.2 รัน `pgBadger`

```bash
sudo pgbadger -j 2 --anonymize \
  --prefix '%m [%p] %q%u@%d app=%a client=%h ' \
  -o /var/tmp/pgbadger-gridcare.html /var/log/postgresql/postgresql-17-main.log
```

ผลลัพธ์:
```text
[========================>] Parsed 125000000 bytes of 125000000 (100.00%), queries: 456789, events: 12
LOG: Ok, generating html report...
```

### 10.3 `log_line_prefix` ที่ต้องตั้ง

```ini
log_line_prefix = '%m [%p] %q%u@%d app=%a client=%h '
```

### 10.4 Report ที่ต้องดู

| Report | ใช้ |
|---|---|
| Overview | ภาพรวม |
| Connections | Connection Pattern |
| Sessions | Session Duration |
| Checkpoints | Checkpoint Frequency |
| Temporary Files | Temp Spill |
| Locks | Lock Wait |
| Top > Time consuming queries | Query ที่ช้า |
| Top > Most frequent queries | Query ที่เรียกบ่อย |

### 10.5 ตัวอย่าง Report

**Overview:**
```text
Overall stats
- Queries: 456,789
- Duration: 1h 20m
- Connections: 1,234
- Sessions: 5,678
```

**Checkpoints:**
```text
- Timed: 12
- Requested: 3
- Avg Buffers Written: 240
```

**Temporary Files:**
```text
- Count: 45
- Total Size: 1.2 GB
- Top Query: SELECT ... FROM bills b JOIN customers c ORDER BY...
```

**Locks:**
```text
- Total Lock Waits: 23
- Longest Wait: 12.3s
- Top Query: ALTER TABLE gridcare.tariff_rates ADD COLUMN note
```

### 10.6 ตาราง Option ที่ใช้บ่อย

| Option | ใช้ |
|---|---|
| `-j 2` | ใช้ 2 Job |
| `--anonymize` | ลด PII |
| `--prefix` | `log_line_prefix` |
| `-o` | Output HTML |
| `--exclude-line` | ไม่เอา Line ที่ตรง |
| `--exclude-query` | ไม่เอา Query ที่ตรง |
| `--retention` | เก็บ Retention |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: รัน `pgBadger`

```bash
sudo pgbadger -j 2 --anonymize \
  --prefix '%m [%p] %q%u@%d app=%a client=%h ' \
  -o /var/tmp/pgbadger-gridcare.html /var/log/postgresql/postgresql-17-main.log
```

ผลลัพธ์:
```text
[========================>] Parsed 125000000 bytes of 125000000 (100.00%), queries: 456789
LOG: Ok, generating html report...
```

### ตัวอย่างที่ 2: เปิด Report

```bash
# Notebook
scp lab-pg1:/var/tmp/pgbadger-gridcare.html .
# เปิดใน Browser
```

### ตัวอย่างที่ 3: รันกับ Log ที่ Rotate

```bash
sudo pgbadger -j 2 --anonymize \
  --prefix '%m [%p] %q%u@%d app=%a client=%h ' \
  -o /var/tmp/pgbadger-weekly.html \
  /var/log/postgresql/postgresql-17-main.log.* /var/log/postgresql/postgresql-17-main.log
```

## 12. สรุปย่อ จำง่าย
- **pgBadger = HTML Report จาก Log**  
- **`--prefix` ต้องตรงกับ `log_line_prefix`**  
- **`log_min_duration_statement = 500ms`**  
- **`log_lock_waits = on`**  
- **`log_checkpoints = on`**  
- **`--anonymize` ลด PII**

ประโยคจำ: **“Log ที่ดีทำให้ pgBadger มีเรื่องเล่า Log ที่แย่ทำให้ pgBadger เงียบ”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- pgBadger: https://pgbadger.darold.net/
- PostgreSQL Documentation — Error Reporting and Logging: https://www.postgresql.org/docs/17/runtime-config-logging.html
- GridCare Workshop Day 4: Lab 4.2

---

# บทที่ 50 Textfile Metrics และ Custom Metrics

## 1. เรื่อง
การสร้าง Custom Metric ด้วย `node_exporter` Textfile Collector สำหรับ Metric ที่ไม่มีใน Exporter

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้สร้าง Metric ของตนเอง  
2. เพื่อให้เขียนไฟล์ `.prom`  
3. เพื่อให้ตั้ง systemd timer  
4. เพื่อให้ใช้กับ Backup Age, SSL Expiry

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- เขียนไฟล์ `.prom`  
- ตั้ง `TEXTFILE_DIR`  
- ใช้ `node_exporter --collector.textfile.directory`  
- ตั้ง systemd timer  
- ตรวจ Metric ที่ Export

## 4. เนื้อหาโดยย่อ
Textfile Collector เป็นฟีเจอร์ของ `node_exporter`:
- อ่านไฟล์ `.prom` จาก Directory  
- Metric ที่อยู่ในไฟล์จะถูก Export  
- ใช้เมื่อ Metric ไม่มีใน Exporter

ตัวอย่าง Metric:
- `gridcare_backup_last_success_timestamp_seconds`  
- `gridcare_ssl_cert_expiry_days`  
- `gridcare_health_check_status`

## 5. ประโยชน์ที่ได้รับ
- Metric ที่ไม่มีใน Exporter  
- Backup Age  
- SSL Expiry  
- Health Check  
- Custom Business Metric

## 6. ข้อควรระวัง
- **ไฟล์ `.prom` ต้อง Format ถูก**  
- **Atomic Write** เพื่อไม่ให้อ่านไฟล์ครึ่ง ๆ  
- **Metric ที่ Cardinality สูงไม่ควรใช้**  
- **ต้องตั้ง `chmod` ให้ node_exporter อ่านได้**  
- **ต้องตั้ง timer ให้รันสม่ำเสมอ**

## 7. ข้อดี
- ยืดหยุ่น  
- ไม่ต้องเขียน Exporter ใหม่  
- ใช้ Metric ที่มีอยู่แล้ว

## 8. ข้อเสีย
- ไม่มี Type หรือ Help  
- ต้องเขียน Script เอง  
- ไม่มี Histogram

## 9. ข้อห้าม
- ห้ามเขียน Metric ที่ Cardinality สูง  
- ห้ามใช้ Textfile เป็น Log  
- ห้ามลืม Atomic Write  
- ห้ามรัน Script ถี่เกินไป  
- ห้ามลืม `chmod`

## 10. รายละเอียด

### 10.1 ตั้ง Textfile Collector

```bash
sudo chgrp postgres /var/lib/prometheus/node-exporter
sudo chmod 2775 /var/lib/prometheus/node-exporter
```

### 10.2 Script `textfile_metrics.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

TEXTFILE_DIR="${TEXTFILE_DIR:-/var/lib/prometheus/node-exporter}"
STANZA="${STANZA:-gridcare}"
TMPFILE="$(mktemp "${TEXTFILE_DIR}/.gridcare_backup.XXXXXX")"

# Backup Age
LAST=$(sudo -u postgres pgbackrest --stanza="${STANZA}" info --output=json \
  | jq -r '[.[] | .backup[] | select(.type=="full")] | sort_by(.timestamp.stop) | last | .timestamp.stop')
NOW=$(date +%s)
AGE=$((NOW - LAST))

cat > "${TMPFILE}" <<EOF
# HELP gridcare_backup_last_success_timestamp_seconds Timestamp ของ Backup สำเร็จล่าสุด
# TYPE gridcare_backup_last_success_timestamp_seconds gauge
gridcare_backup_last_success_timestamp_seconds{stanza="${STANZA}"} ${LAST}
# HELP gridcare_backup_last_success_age_seconds อายุของ Backup ล่าสุด
# TYPE gridcare_backup_last_success_age_seconds gauge
gridcare_backup_last_success_age_seconds{stanza="${STANZA}"} ${AGE}
EOF

# SSL Expiry
CERT="/etc/postgresql/17/main/server.crt"
DAYS=$(sudo -u postgres openssl x509 -in "${CERT}" -noout -enddate \
  | sed 's/notAfter=//' | xargs -I{} date -d "{}" +%s)
DAYS_LEFT=$(( (DAYS - NOW) / 86400 ))
cat >> "${TMPFILE}" <<EOF
# HELP gridcare_ssl_cert_expiry_timestamp_seconds วันหมดอายุ Certificate
# TYPE gridcare_ssl_cert_expiry_timestamp_seconds gauge
gridcare_ssl_cert_expiry_timestamp_seconds{path="${CERT}"} ${DAYS}
# HELP gridcare_ssl_cert_expiry_days จำนวนวันที่เหลือ
# TYPE gridcare_ssl_cert_expiry_days gauge
gridcare_ssl_cert_expiry_days{path="${CERT}"} ${DAYS_LEFT}
EOF

mv "${TMPFILE}" "${TEXTFILE_DIR}/gridcare_backup.prom"
```

### 10.3 ตั้ง systemd Service

**`/etc/systemd/system/gridcare-textfile.service`:**
```ini
[Unit]
Description=GridCare textfile metrics (backup age, SSL expiry)
[Service]
Type=oneshot
User=postgres
Group=postgres
Environment=TEXTFILE_DIR=/var/lib/prometheus/node-exporter
Environment=STANZA=gridcare
ExecStart=/opt/gridcare/scripts/textfile_metrics.sh
```

### 10.4 ตั้ง systemd Timer

**`/etc/systemd/system/gridcare-textfile.timer`:**
```ini
[Unit]
Description=Run GridCare textfile metrics every 15 minutes
[Timer]
OnCalendar=*:0/15
Persistent=true
[Install]
WantedBy=timers.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now gridcare-textfile.timer
systemctl list-timers 'gridcare-*' --no-pager
```

ผลลัพธ์:
```text
NEXT                        LEFT       LAST                        PASSED    UNIT                    ACTIVATES
Wed 2026-11-04 13:15:00 +07 13min left n/a                         n/a       gridcare-textfile.timer gridcare-textfile.service
```

### 10.5 ตรวจ Metric

```bash
sudo -u postgres TEXTFILE_DIR=/var/lib/prometheus/node-exporter STANZA=gridcare \
  /opt/gridcare/scripts/textfile_metrics.sh
cat /var/lib/prometheus/node-exporter/*.prom | grep -v '^#'
```

ผลลัพธ์:
```text
gridcare_backup_last_success_timestamp_seconds{stanza="gridcare"} 1.7307e+09
gridcare_backup_last_success_age_seconds{stanza="gridcare"} 3600
gridcare_ssl_cert_expiry_timestamp_seconds{path="/etc/postgresql/17/main/server.crt"} 1.7625e+09
gridcare_ssl_cert_expiry_days{path="/etc/postgresql/17/main/server.crt"} 364
```

### 10.6 Alert จาก Custom Metric

```yaml
- alert: BackupTooOld
  expr: gridcare_backup_last_success_age_seconds > 86400
  for: 10m
  labels: {severity: critical, owner: dba}
  annotations:
    summary: "Backup ล่าสุดเก่ากว่า 24 ชั่วโมง"
    runbook_url: "http://gridcare-infra/runbooks/C07-backup-recovery.md"

- alert: SslCertificateExpiringSoon
  expr: gridcare_ssl_cert_expiry_days < 30
  for: 1h
  labels: {severity: warning, owner: dba}
  annotations:
    summary: "Certificate เหลือ {{ $value }} วัน"
    runbook_url: "http://gridcare-infra/runbooks/C10-security.md"
```

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Metric ที่ Export

```bash
cat /var/lib/prometheus/node-exporter/*.prom | grep -v '^#'
```

ผลลัพธ์:
```text
gridcare_backup_last_success_timestamp_seconds{stanza="gridcare"} 1.7307e+09
gridcare_backup_last_success_age_seconds{stanza="gridcare"} 3600
gridcare_ssl_cert_expiry_timestamp_seconds{path="/etc/postgresql/17/main/server.crt"} 1.7625e+09
gridcare_ssl_cert_expiry_days{path="/etc/postgresql/17/main/server.crt"} 364
```

### ตัวอย่างที่ 2: ตรวจ Metric ใน Prometheus

```bash
curl -s localhost:9090/api/v1/query?query=gridcare_backup_last_success_age_seconds | python3 -m json.tool
```

ผลลัพธ์:
```json
{
  "status": "success",
  "data": {
    "resultType": "vector",
    "result": [
      {
        "metric": {"stanza": "gridcare"},
        "value": [1730702112.345, "3600"]
      }
    ]
  }
}
```

### ตัวอย่างที่ 3: Alert ที่ Firing

```yaml
- alert: BackupTooOld
  expr: gridcare_backup_last_success_age_seconds > 86400
  for: 10m
  labels: {severity: critical, owner: dba}
  annotations:
    summary: "Backup ล่าสุดเก่ากว่า 24 ชั่วโมง"
```

### ตัวอย่างที่ 4: ตรวจ Timer

```bash
systemctl list-timers 'gridcare-*' --no-pager
```

ผลลัพธ์:
```text
NEXT                        LEFT       LAST                        PASSED    UNIT                    ACTIVATES
Wed 2026-11-04 13:15:00 +07 13min left n/a                         n/a       gridcare-textfile.timer gridcare-textfile.service
Thu 2026-11-05 07:00:00 +07 17h left   n/a                         n/a       gridcare-health-check.timer gridcare-health-check.service
```

## 12. สรุปย่อ จำง่าย
- **Textfile Collector = Metric ที่เขียนเอง**  
- **ไฟล์ `.prom` ต้อง Format ถูก**  
- **Atomic Write ด้วย `mktemp` + `mv`**  
- **ตั้ง `chmod` ให้ node_exporter อ่านได้**  
- **ตั้ง systemd timer**  
- **ใช้กับ Backup Age, SSL Expiry**

ประโยคจำ: **“Metric ที่ยังไม่มี We สร้างได้ด้วย Textfile Collector”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- node_exporter — Textfile Collector: https://github.com/prometheus/node_exporter#textfile-collector
- GridCare Workshop Day 3: Lab 4.1

---

## สรุปส่วนที่ 5 (บทที่ 41–50)

| บท | แก่นของบท | ใช้ต่อในส่วน |
|---|---|---|
| 41 | Metric สำคัญของ PostgreSQL | Monitoring, Alert |
| 42 | postgres_exporter | Prometheus |
| 43 | node_exporter | Prometheus |
| 44 | Prometheus Scrape Config | Monitoring |
| 45 | PromQL พื้นฐาน | Dashboard, Alert |
| 46 | PromQL ขั้นสูง | Dashboard, Alert |
| 47 | Grafana Dashboard | Operations |
| 48 | Dashboard สำหรับ DBA และ DevOps | Operations |
| 49 | pgBadger และ Log Analytics | S troubleshooting |
| 50 | Textfile Metrics และ Custom Metrics | Alert, Monitoring |

---

 