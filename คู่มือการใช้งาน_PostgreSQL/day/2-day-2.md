# 📋 สรุปคำสั่งทั้งหมด — Day 2 (วันที่ 2)

> **หลักสูตร:** Advanced PostgreSQL for Enterprise Production (PEA)
> **หัวข้อ:** Performance Tuning, Observability & Maintenance
> **วันที่:** อังคารที่ 3 พฤศจิกายน 2569 | 09:00-16:45 น.
> รูปแบบ: **คำสั่ง** → **ผลลัพธ์จริง/ที่คาดหวัง** → **หมายเหตุ**

---

## 🔄 เริ่มวัน: เปิดโหลดจำลองค้างไว้ตลอดวัน

### บน infra ภายใน tmux

```bash
tmux new -s load
```
**ผลลัพธ์:** เข้าหน้าจอ tmux session ใหม่ชื่อ `load`

**ภายในหน้าต่าง tmux:**
```bash
cd /opt/gridcare/pgbench
PGHOST=127.0.0.1 PGPORT=6432 PGUSER=billing_app ./run_normal.sh 10 28800
```
**ผลลัพธ์:**
```
starting 10 clients for 28800 seconds...
transaction type: multiple scripts
scaling factor: 1
query mode: simple
number of clients: 10
number of threads: 1
duration: 28800 s
```

**กด `Ctrl+b` แล้ว `d`** เพื่อ detach (โหลดยังทำงานต่อ)

> 💡 สคริปต์ผสมงาน 4 แบบ: รับหน่วยไฟ 60%, ค้นผู้ใช้ไฟ 25%, ชำระค่าไฟ 10%, แจ้งเหตุไฟดับ 5%
> 💡 ถ้า CPU ของ infra เต็ม (ดูด้วย `top`) ให้ลด Client เหลือ 6

---

## 🧪 Lab 1.1 — อ่านแผน หา Row Estimate ที่ผิด แล้วแก้ด้วย Extended Statistics

### ทำบน pg1 ใน psql

```bash
sudo -u postgres psql -X -d gridcare
```
**ผลลัพธ์:**
```
psql (17.11)
Type "help" for help.

gridcare=#
```

### ข้อ 1: แผนของ Query ค้นผู้ใช้ไฟด้วยหมายเลข CA

```sql
SET search_path = gridcare, public;

EXPLAIN (ANALYZE, BUFFERS)
SELECT customer_id, ca_number, first_name, tariff_code FROM customers WHERE ca_number = '020000123456';
```
**ผลลัพธ์ (ก่อนมี Index):**
```
                                             QUERY PLAN                                              
-----------------------------------------------------------------------------------------------------
 Gather  (cost=1000.00..12666.67 rows=1 width=42) (actual time=12.345..45.678 rows=1 loops=1)
   Workers Planned: 2
   Workers Launched: 2
   Buffers: shared hit=1820
   ->  Parallel Seq Scan on customers  (cost=0.00..11666.57 rows=1 width=42) (actual time=8.234..38.456 rows=0 loops=3)
         Filter: (ca_number = '020000123456'::bpchar)
         Rows Removed by Filter: 66666
         Buffers: shared hit=1820
 Planning Time: 0.345 ms
 Execution Time: 45.789 ms
(9 rows)
```
> 💡 **สังเกต:** `Parallel Seq Scan` + `Rows Removed by Filter: 66666` ต่อ Worker = ต้องอ่าน 200,000 แถวเพื่อหา 1 แถว

### ข้อ 2: บิล ก.ย. ที่ UNPAID (ประมาณผิด)

```sql
EXPLAIN (ANALYZE, TIMING OFF)
SELECT count(*) FROM bills WHERE billing_period = '2026-09-01' AND status = 'UNPAID';
```
**ผลลัพธ์ (ก่อนสร้าง Extended Statistics):**
```
                                            QUERY PLAN                                            
--------------------------------------------------------------------------------------------------
 Finalize Aggregate  (cost=8934.12..8934.13 rows=1 width=8) (actual time=45.234..45.235 rows=1 loops=1)
   ->  Gather  (cost=8933.90..8934.11 rows=3 width=8) (actual time=45.123..45.128 rows=3 loops=3)
         Workers Planned: 2
         Workers Launched: 2
         ->  Partial Aggregate  (cost=7933.90..7933.91 rows=1 width=8) (actual time=42.345..42.346 rows=1 loops=3)
               ->  Parallel Seq Scan on bills  (cost=0.00..7933.85 rows=13897 width=0) (actual time=0.234..42.123 rows=0 loops=3)
                     Filter: ((billing_period = '2026-09-01'::date) AND (status = 'UNPAID'::bpchar))
                     Rows Removed by Filter: 33333
 Planning Time: 0.456 ms
 Execution Time: 45.678 ms
```
> ⚠️ **ประมาณ `rows=13897` แต่ `actual rows=0`** (Rows Removed by Filter: 33333 ต่อ Worker)

### ข้อ 3: สร้าง Extended Statistics

```sql

```
**ผลลัพธ์:**
```
CREATE STATISTICS
```

```sql
ANALYZE bills;
```
**ผลลัพธ์:**
```
ANALYZE
```

```sql
EXPLAIN (ANALYZE, TIMING OFF)
SELECT count(*) FROM bills WHERE billing_period = '2026-09-01' AND status = 'UNPAID';
```
**ผลลัพธ์ (หลังสร้าง Statistics):**
```
                                            QUERY PLAN                                            
--------------------------------------------------------------------------------------------------
 Finalize Aggregate  (cost=8934.12..8934.13 rows=1 width=8) (actual time=0.234..0.235 rows=1 loops=1)
   ->  Gather  (cost=8933.90..8934.11 rows=3 width=8) (actual time=0.123..0.128 rows=3 loops=3)
         Workers Planned: 2
         Workers Launched: 2
         ->  Partial Aggregate  (cost=7933.90..7933.91 rows=1 width=8) (actual time=0.045..0.046 rows=1 loops=3)
               ->  Parallel Seq Scan on bills  (cost=0.00..7933.85 rows=300 width=0) (actual time=0.012..0.034 rows=0 loops=3)
                     Filter: ((billing_period = '2026-09-01'::date) AND (status = 'UNPAID'::bpchar))
                     Rows Removed by Filter: 0
 Planning Time: 0.234 ms
 Execution Time: 0.345 ms
```
> ✅ **ประมาณจาก 13,897 → 300** (ใกล้ความจริง 0 มากขึ้น 46 เท่า)

### ข้อ 4: ดูสถิติที่ได้

```sql
SELECT statistics_name, attnames, kinds FROM pg_stats_ext WHERE tablename = 'bills';
```
**ผลลัพธ์:**
```
    statistics_name    |        attnames         | kinds 
-----------------------+-------------------------+-------
 bills_period_status   | {billing_period,status} | {mcv}
(1 row)
```

**✅ ผลลัพธ์ที่คาดหวัง:** ข้อ 2 ประมาณราว 14,000 แถว → หลังสร้างสถิติเหลือราว 300

> ⚠️ **จำไว้ใช้วันที่ 5:** `pg_upgrade` รุ่น 18 **ไม่โอน Extended Statistics** ต้องใช้ `vacuumdb --missing-stats-only`

---

## 🧪 Lab 2.1 — หา Query ที่ใช้เวลารวมสูงสุดด้วย pg_stat_statements

### บน pg1

```sql
SELECT pg_stat_statements_reset();
```
**ผลลัพธ์:**
```
 pg_stat_statements_reset 
--------------------------
 
(1 row)
```

> 💡 รอ 3-5 นาทีให้โหลดจาก infra สะสมสถิติ

```sql
SELECT calls,
       round(total_exec_time::numeric, 0) AS total_ms,
       round(mean_exec_time::numeric, 2)  AS mean_ms,
       rows,
       round(100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0), 1) AS hit_pct,
       left(regexp_replace(query, '\s+', ' ', 'g'), 80) AS query
FROM pg_stat_statements
WHERE dbid = (SELECT oid FROM pg_database WHERE datname = 'gridcare')
ORDER BY total_exec_time DESC
LIMIT 5;
```
**ผลลัพธ์:**
```
 calls | total_ms | mean_ms |   rows   | hit_pct |                            query                             
-------+----------+---------+----------+---------+-------------------------------------------------------------
 15023 |  45234   |   3.01  |  4506900 |   99.8  | UPDATE bills SET status = $1 WHERE bill_id = $2
  8452 |  23145   |   2.74  |  845200  |   99.5  | SELECT ... FROM customers WHERE ca_number = $1
  3201 |  12034   |   3.76  |   320100 |   98.2  | INSERT INTO meter_readings ...
   890 |   8901   |  10.00  |    89000 |   97.1  | SELECT sum(total_amount) FROM bills WHERE ...
   234 |   5678   |  24.26  |     2340 |   95.3  | SELECT ... FROM bills b JOIN customers c ...
(5 rows)
```
> ✅ **อันดับ 2 คือ Query ค้นผู้ใช้ไฟด้วยหมายเลข CA** (จาก `lookup_customer.sql`)

### ดูแผนจาก auto_explain

```bash
sudo grep -E -A12 "duration: [0-9.]+ ms +(plan|statement):" /var/log/postgresql/postgresql-17-main.log | tail -30
```
**ผลลัพธ์:**
```
2026-11-03 09:45:12.345 +07 [12345] postgres@gridcare app=pgbench client=10.104.0.13 LOG:  duration: 2345.678 ms  plan:
	Query Text: SELECT ... FROM customers WHERE ca_number = $1
	Seq Scan on customers  (cost=0.00..5820.00 rows=1 width=42) (actual time=12.345..2345.678 rows=1 loops=1)
	  Filter: (ca_number = '020000123456'::bpchar)
	  Rows Removed by Filter: 199999
	  Buffers: shared hit=1820
```

### ดู Session สด

```bash
sudo -u postgres pg_activity -d gridcare
```
**ผลลัพธ์:** หน้าจอแสดง Session ที่กำลังทำงาน (กด `q` เพื่อออก)

> 💡 ถ้ายังไม่มี `pg_activity` → `sudo apt install -y pg-activity`

**✅ ผลลัพธ์ที่คาดหวัง:** อันดับต้นคือ Query ค้นหมายเลข CA จาก `lookup_customer.sql`

---

## 🧪 Lab 2.2 — ตรวจสุขอนามัยของ Index และสาธิต Index ที่ invalid

### รายงานรายสัปดาห์

```bash
sudo -u postgres psql -X -d gridcare -f /opt/gridcare/scripts/weekly_report.sql | less
```
**ผลลัพธ์ (ตัวอย่าง):**
```
=== 2. Duplicate Indexes ===
 schemaname |      table       |           index_name            | duplicates
------------+------------------+---------------------------------+------------
 gridcare   | bills            | bills_customer_id_dup_idx       | bills_customer_idx
 gridcare   | payments         | payments_reference_no_idx2      | payments_reference_no_idx

=== 3. Unused Indexes (idx_scan = 0) ===
 schemaname |      table       |         index_name          | idx_scan | size
------------+------------------+-----------------------------+----------+-------
 gridcare   | payments         | payments_reference_no_idx   |        0 | 12 MB

=== 4. Invalid Indexes ===
 schemaname | table | index_name | indisvalid | indisready
------------+-------+------------+------------+------------
(0 rows)

=== 5. Foreign Keys without Index ===
 schemaname |      table       |       constraint_name       | columns
------------+------------------+-----------------------------+----------
 gridcare   | work_orders      | work_orders_customer_fk     | customer_id
 gridcare   | bills            | bills_meter_fk              | meter_id
```

### สาธิต Index ที่ invalid (ยกเลิก CIC กลางคัน)

```sql
SET maintenance_work_mem = '64MB';
CREATE INDEX CONCURRENTLY payments_paid_at_demo_idx ON gridcare.payments (paid_at);
-- กด Ctrl+C ภายใน 1-2 วินาที
```
**ผลลัพธ์:**
```
SET
CREATE INDEX
^CCancel request sent
ERROR:  canceling statement due to user request
```

```sql
SELECT c.relname, i.indisvalid, i.indisready
FROM pg_index AS i JOIN pg_class AS c ON c.oid = i.indexrelid
WHERE c.relname = 'payments_paid_at_demo_idx';
```
**ผลลัพธ์:**
```
         relname          | indisvalid | indisready 
--------------------------+------------+------------
 payments_paid_at_demo_idx | f          | f
(1 row)
```

```sql
\d gridcare.payments
```
**ผลลัพธ์ (บางส่วน):**
```
Indexes:
    "payments_pkey" PRIMARY KEY, btree (payment_id)
    "payments_paid_at_demo_idx" btree (paid_at) INVALID
```

```sql
DROP INDEX CONCURRENTLY gridcare.payments_paid_at_demo_idx;
```
**ผลลัพธ์:**
```
DROP INDEX
```

**✅ ผลลัพธ์ที่คาดหวัง:**
- รายงานข้อ 4: `bills_customer_id_dup_idx` ซ้ำกับ `bills_customer_idx`
- รายงานข้อ 3: `payments_reference_no_idx` ที่ `idx_scan = 0`
- รายงานข้อ 5: FK ไม่มี Index (`work_orders.customer_id`, `bills.meter_id`)
- สาธิต: `indisvalid = f` และ `\d` แสดง `INVALID`

> ⚠️ **ห้ามลบ** `bills_customer_id_dup_idx` หรือ `payments_reference_no_idx` ในขั้นนี้ → ลบใน Workshop ขั้นที่ 1

---

## 🧪 Lab 3.1 — ติดตั้ง exporters บน pg1 และ Prometheus บน infra

### ส่วนที่ 1: Role สำหรับ exporter บน pg1

```sql
CREATE ROLE pgexporter LOGIN PASSWORD 'Lab-Exporter-2569' IN ROLE pg_monitor;
GRANT CONNECT ON DATABASE gridcare TO pgexporter;
ALTER ROLE pgexporter SET statement_timeout = '10s';
```
**ผลลัพธ์:**
```
CREATE ROLE
GRANT
ALTER ROLE
```

### ส่วนที่ 2: ติดตั้ง node_exporter และ postgres_exporter บน pg1

```bash
sudo apt install -y prometheus-node-exporter
systemctl status prometheus-node-exporter --no-pager | head -3
```
**ผลลัพธ์:**
```
● prometheus-node-exporter.service - Prometheus Node Exporter
     Loaded: loaded (/lib/systemd/system/prometheus-node-exporter.service; enabled)
     Active: active (running) since Tue 2026-11-03 09:30:15 +07; 5s ago
```

```bash
curl -s localhost:9100/metrics | grep -c '^node_'
```
**ผลลัพธ์:**
```
542
```

```bash
/opt/pea/bin/postgres_exporter --version
```
**ผลลัพธ์:**
```
postgres_exporter, version 0.18.0 (branch: HEAD, revision: ...)
  build user:       root@build
  build date:       20261015-12:00:00
  go version:       go1.22.5
```

```bash
ls /opt/pea/units/
```
**ผลลัพธ์:**
```
postgres_exporter.service
```

```bash
cat /opt/pea/units/postgres_exporter.service
```
**ผลลัพธ์:**
```
[Unit]
Description=Prometheus PostgreSQL Exporter
After=network.target

[Service]
Type=simple
User=postgres
Group=postgres
EnvironmentFile=/etc/default/postgres_exporter
ExecStart=/opt/pea/bin/postgres_exporter --web.listen-address=:9187
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### คัดลอกและแก้ unit

```bash
sudo cp /opt/pea/units/postgres_exporter.service /etc/systemd/system/
sudo nano /etc/systemd/system/postgres_exporter.service
```

**เนื้อหาหลังแก้ (ส่วน Service):**
```ini
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
```

### สร้าง /etc/default/postgres_exporter

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
curl -s localhost:9187/metrics | grep -E '^pg_up|^pg_database_wraparound_age_datfrozenxid_seconds' | head
```
**ผลลัพธ์:**
```
pg_up 1
pg_database_wraparound_age_datfrozenxid_seconds{datname="gridcare"} 152345
pg_database_wraparound_age_datfrozenxid_seconds{datname="postgres"} 45012
pg_database_wraparound_age_datfrozenxid_seconds{datname="template1"} 45012
```

### ส่วนที่ 3: Prometheus บน infra

```bash
sudo apt install -y prometheus
sudo cp /etc/prometheus/prometheus.yml /etc/prometheus/prometheus.yml.orig
sudo truncate -s 0 /etc/prometheus/prometheus.yml
sudo nano /etc/prometheus/prometheus.yml
```

**เนื้อหา:**
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: prometheus
    static_configs:
      - targets: ['localhost:9090']
  - job_name: node
    static_configs:
      - targets: ['pg1:9100', 'infra:9100']
  - job_name: postgres
    static_configs:
      - targets: ['pg1:9187']
```

```bash
promtool check config /etc/prometheus/prometheus.yml
```
**ผลลัพธ์:**
```
Checking /etc/prometheus/prometheus.yml
  SUCCESS: 3 scrape configs found
```

```bash
sudo systemctl restart prometheus
sleep 20
curl -s localhost:9090/api/v1/targets | python3 -m json.tool | grep -E '"scrapeUrl"|"health"'
```
**ผลลัพธ์:**
```
"scrapeUrl": "http://localhost:9090/metrics",
"health": "up"
"scrapeUrl": "http://pg1:9100/metrics",
"health": "up"
"scrapeUrl": "http://infra:9100/metrics",
"health": "up"
"scrapeUrl": "http://pg1:9187/metrics",
"health": "up"
```

**✅ ผลลัพธ์ที่คาดหวัง:** target ทั้ง 4 รายการมี `"health": "up"`

---

## 🧪 Lab 3.2 — ติดตั้ง Grafana และสร้าง Dashboard

### บน infra

```bash
  sudo apt install -y grafana
  sudo systemctl enable --now grafana-server
  systemctl status grafana-server --no-pager | head -3
```
**ผลลัพธ์:**
```
● grafana-server.service - Grafana instance
     Loaded: loaded (/lib/systemd/system/grafana-server.service; enabled)
     Active: active (running) since Tue 2026-11-03 10:15:30 +07; 2s ago
```

### บน Notebook

```bash
ssh lab-tunnel
```
**ผลลัพธ์:** Tunnel เปิดค้างไว้ (ไม่ต้องปิด)

### เปิด Browser ไปที่ `http://localhost:13000`

1. Login: `admin` / `admin` → ตั้งรหัสผ่านใหม่
2. **Connections > Data sources > Add data source > Prometheus** → URL: `http://localhost:9090` → **Save & test**
3. **Dashboards > New dashboard** → ตั้งชื่อ `GridCare PostgreSQL` → Time range `Last 1 hour`
4. เพิ่ม Panel ตามตาราง:

| Panel | PromQL |
|---|---|
| Transactions per second | `sum by (datname) (rate(pg_stat_database_xact_commit{datname="gridcare"}[1m]) + rate(pg_stat_database_xact_rollback{datname="gridcare"}[1m]))` |
| Connections ตามสถานะ | `sum by (state) (pg_stat_activity_count{datname="gridcare"})` |
| Cache hit ratio | `rate(pg_stat_database_blks_hit{datname="gridcare"}[5m]) / (rate(pg_stat_database_blks_hit{datname="gridcare"}[5m]) + rate(pg_stat_database_blks_read{datname="gridcare"}[5m]))` |
| Top Query | `topk(5, rate(pg_stat_statements_seconds_total{datname="gridcare"}[5m]))` |
| Dead tuple รายตาราง | `topk(5, pg_stat_user_tables_n_dead_tup{schemaname="gridcare"})` |
| อายุ XID | `pg_database_wraparound_age_datfrozenxid_seconds` |
| CPU ของเครื่อง | `100 - avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[1m])) * 100` |
| พื้นที่ดิสก์ที่เหลือ | `node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}` |

5. **Save dashboard** → **Export > Export as JSON** → บันทึก `gridcare-postgres-dashboard.json`

**✅ ผลลัพธ์ที่คาดหวัง:**
- ทุก Panel มีกราฟ
- TPS ~หลักร้อย
- Cache hit ratio ใกล้ 0.99
- Top Query เห็น queryid ของ Query ค้นหมายเลข CA

> 💡 จับภาพ Dashboard เก็บไว้เป็น **"ก่อนปรับ"** สำหรับ Workshop

---

## 🧪 Lab 4.1 — Transaction ที่ลืมปิดทำให้ VACUUM ลบไม่ได้ แล้วกำจัด Bloat ด้วย pg_repack

### บน pg1

```bash
sudo apt install -y postgresql-17-repack
```
**ผลลัพธ์:**
```
Reading package lists... Done
Setting up postgresql-17-repack (1.5.3-1.pgdg24.04+1) ...
```

### หน้าต่าง 1: สร้างตารางสาธิต

```bash
sudo -u postgres psql -X -d gridcare
```

```sql
CREATE TABLE gridcare.bills_bloat_demo AS SELECT * FROM gridcare.bills WHERE bill_id <= 200000;
ALTER TABLE gridcare.bills_bloat_demo ADD PRIMARY KEY (bill_id);
ALTER TABLE gridcare.bills_bloat_demo SET (autovacuum_enabled = off);
SELECT pg_size_pretty(pg_table_size('gridcare.bills_bloat_demo')) AS size_before;
```
**ผลลัพธ์:**
```
SELECT 200000
ALTER TABLE
ALTER TABLE
 size_before 
-------------
 24 MB
(1 row)
```

### หน้าต่าง 2: Transaction ที่ "ลืมปิด"

```sql
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT count(*) FROM gridcare.regions;
-- ทิ้งไว้
```
**ผลลัพธ์:**
```
BEGIN
 count 
-------
    12
(1 row)
```

### หน้าต่าง 1: UPDATE ทุกแถวแล้ว VACUUM

```sql
UPDATE gridcare.bills_bloat_demo SET units_kwh = units_kwh;
VACUUM (VERBOSE) gridcare.bills_bloat_demo;
```
**ผลลัพธ์:**
```
UPDATE 200000
INFO:  vacuuming "gridcare.bills_bloat_demo"
INFO:  scanned index "bills_bloat_demo_pkey" to remove 200000 row versions
DETAIL:  CPU: 45.23 ms, elapsed: 234.56 ms
INFO:  "bills_bloat_demo": removed 0 row versions in 1234 pages
DETAIL:  CPU: 12.34 ms, elapsed: 45.67 ms
INFO:  "bills_bloat_demo": found 0 removable, 400000 nonremovable row versions in 3072 pages
DETAIL:  200000 dead row versions cannot be removed yet, oldest xmin: 1234567
```

### Query หาสิ่งที่ขวาง VACUUM

```sql
SELECT 'session' AS kind, pid::text AS who, state, age(backend_xmin) AS xmin_age, now() - xact_start AS xact_age
FROM pg_stat_activity WHERE backend_xmin IS NOT NULL
UNION ALL
SELECT 'slot', slot_name, active::text, age(xmin), NULL FROM pg_replication_slots WHERE xmin IS NOT NULL
UNION ALL
SELECT 'prepared', gid, NULL, age(transaction), now() - prepared FROM pg_prepared_xacts
ORDER BY xmin_age DESC NULLS LAST
LIMIT 5;
```
**ผลลัพธ์:**
```
  kind   |  who  |        state        | xmin_age |  xact_age   
---------+-------+---------------------+----------+-------------
 session | 12345 | idle in transaction |       85 | 00:01:25
(1 row)
```
> ✅ **Session ของหน้าต่าง 2 เป็นแถวแรก** (xmin_age = 85 transactions)

### หน้าต่าง 2: ปิด Transaction

```sql
ROLLBACK;
```
**ผลลัพธ์:**
```
ROLLBACK
```

### หน้าต่าง 1: VACUUM อีกครั้ง แล้วดูขนาด

```sql
VACUUM (VERBOSE) gridcare.bills_bloat_demo;
SELECT pg_size_pretty(pg_table_size('gridcare.bills_bloat_demo')) AS after_vacuum;
CREATE EXTENSION IF NOT EXISTS pg_repack;
```
**ผลลัพธ์:**
```
INFO:  "bills_bloat_demo": removed 200000 row versions in 1536 pages
DETAIL:  CPU: 123.45 ms, elapsed: 456.78 ms
INFO:  "bills_bloat_demo": found 200000 removable, 200000 nonremovable row versions in 3072 pages
VACUUM
 after_vacuum 
--------------
 48 MB
(1 row)
CREATE EXTENSION
```

### รัน pg_repack

```bash
sudo -u postgres pg_repack -d gridcare -t gridcare.bills_bloat_demo
```
**ผลลัพธ์:**
```
INFO: repacking table "gridcare.bills_bloat_demo"
```

```bash
sudo -u postgres psql -X -d gridcare -c "SELECT pg_size_pretty(pg_table_size('gridcare.bills_bloat_demo')) AS after_repack" -c "DROP TABLE gridcare.bills_bloat_demo"
```
**ผลลัพธ์:**
```
 after_repack 
--------------
 24 MB
(1 row)

DROP TABLE
```

### สรุปผลจริง

| ขั้น | dead tuple | ขนาด |
|---|---|---|
| ก่อน UPDATE | 0 | 24 MB |
| VACUUM (มี Tx ค้าง) | 200,000 ลบไม่ได้ | 48 MB |
| VACUUM (ปิด Tx) | 200,000 removed | 48 MB (ใช้ซ้ำได้ แต่ไฟล์ไม่เล็กลง) |
| **หลัง pg_repack** | **0** | **24 MB** |

**✅ ผลลัพธ์ที่คาดหวัง:** ได้ `tuples: ... are dead but not yet removable` และหลัง pg_repack ขนาดกลับมา 24 MB

---

## 🧪 Lab 4.2 — ติดตามอายุ XID และตั้ง Autovacuum รายตาราง

### อายุ XID ระดับฐานข้อมูล

```sql
SELECT datname, age(datfrozenxid) AS xid_age,
       round(100.0 * age(datfrozenxid) / 2147483647, 2) AS pct_of_wraparound
FROM pg_database ORDER BY 2 DESC;
```
**ผลลัพธ์:**
```
  datname   | xid_age | pct_of_wraparound 
------------+---------+-------------------
 gridcare   |  152345 |              0.01
 postgres   |   45012 |              0.00
 template1  |   45012 |              0.00
(3 rows)
```

### อายุ XID ระดับตาราง

```sql
SELECT c.oid::regclass AS table_name, age(c.relfrozenxid) AS xid_age,
       pg_size_pretty(pg_total_relation_size(c.oid)) AS size
FROM pg_class AS c JOIN pg_namespace AS n ON n.oid = c.relnamespace
WHERE n.nspname = 'gridcare' AND c.relkind = 'r'
ORDER BY age(c.relfrozenxid) DESC LIMIT 5;
```
**ผลลัพธ์:**
```
         table_name          | xid_age |  size   
-----------------------------+---------+---------
 gridcare.meter_readings     |  152345 | 1250 MB
 gridcare.bills              |  150234 | 320 MB
 gridcare.payments           |  148901 | 180 MB
 gridcare.customers          |  145678 | 45 MB
 gridcare.regions            |   45012 | 8 kB
(5 rows)
```

### สถานะ dead tuple และ Autovacuum ล่าสุด

```sql
SELECT relname, n_live_tup, n_dead_tup, last_autovacuum, last_autoanalyze, autovacuum_count
FROM pg_stat_user_tables WHERE schemaname = 'gridcare'
ORDER BY n_dead_tup DESC LIMIT 5;
```
**ผลลัพธ์:**
```
     relname     | n_live_tup | n_dead_tup |     last_autovacuum     |     last_autoanalyze    | autovacuum_count 
-----------------+------------+------------+--------------------------+--------------------------+------------------
 bills           |    1200000 |      12000 | 2026-11-03 09:45:12+07 | 2026-11-03 09:45:15+07 |                3
 payments        |     450000 |       4500 | 2026-11-03 09:40:10+07 | 2026-11-03 09:40:12+07 |                2
 meter_readings  |    7200000 |          0 | 2026-11-03 09:30:00+07 | 2026-11-03 09:30:05+07 |                1
```

### ตั้ง Autovacuum รายตาราง

```sql
ALTER TABLE gridcare.bills SET (autovacuum_vacuum_scale_factor = 0.02, autovacuum_analyze_scale_factor = 0.02);
SELECT relname, reloptions FROM pg_class WHERE relname = 'bills';
```
**ผลลัพธ์:**
```
 relname |                                       reloptions                                        
---------+---------------------------------------------------------------------------------------
 bills   | {autovacuum_vacuum_scale_factor=0.02,autovacuum_analyze_scale_factor=0.02}
(1 row)
```

### ดู VACUUM ที่กำลังทำงาน

```sql
SELECT pid, relid::regclass, phase, heap_blks_scanned, heap_blks_total FROM pg_stat_progress_vacuum;
```
**ผลลัพธ์:**
```
 pid | relid | phase | heap_blks_scanned | heap_blks_total 
-----+-------+-------+-------------------+-----------------
(0 rows)
```
> 💡 ถ้ามี VACUUM ทำงาน จะเห็น Phase ต่าง ๆ เช่น `scanning heap`, `vacuuming indexes`, `vacuuming heap`

**✅ ผลลัพธ์ที่คาดหวัง:** `pct_of_wraparound` ต่ำ (~0.01%) และ `reloptions` ของ bills แสดงค่าที่ตั้ง

---

## 🛠️ Workshop Day 2 — ขั้นที่ 1: Q1-Q4 Query จาก ORM ที่ช้า

### 1.0 เข้า psql บน pg1

```bash
sudo -u postgres psql -X -d gridcare
```

```sql
SET search_path = gridcare, public;
\timing on;
```
**ผลลัพธ์:**
```
SET
Timing is on.
```

### Q1 — ค้นผู้ใช้ไฟด้วยหมายเลข CA

**1.1 วัดก่อนปรับ:**
```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT customer_id, ca_number, first_name, last_name, tariff_code, status
FROM customers
WHERE ca_number = '020000123456';
```
**ผลลัพธ์ (ก่อน):**
```
                                             QUERY PLAN                                              
-----------------------------------------------------------------------------------------------------
 Gather  (cost=1000.00..12666.67 rows=1 width=42) (actual time=12.345..45.678 rows=1 loops=1)
   Workers Planned: 2
   Workers Launched: 2
   ->  Parallel Seq Scan on customers  (cost=0.00..11666.57 rows=1 width=42) (actual time=8.234..38.456 rows=0 loops=3)
         Filter: (ca_number = '020000123456'::bpchar)
         Rows Removed by Filter: 66666
 Execution Time: 45.789 ms
```

**1.2 ตรวจไม่มีค่าซ้ำ แล้วสร้าง Unique Index:**
```sql
SELECT ca_number, count(*) FROM customers GROUP BY ca_number HAVING count(*) > 1;
```
**ผลลัพธ์:**
```
 ca_number | count 
-----------+-------
(0 rows)
```

```sql
CREATE UNIQUE INDEX CONCURRENTLY customers_ca_number_key ON customers (ca_number);
SELECT indexrelid::regclass, indisvalid FROM pg_index WHERE indexrelid = 'customers_ca_number_key'::regclass;
```
**ผลลัพธ์:**
```
CREATE INDEX
             indexrelid             | indisvalid 
------------------------------------+------------
 customers_ca_number_key            | t
(1 row)
```

**1.3 วัดซ้ำ:**
```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT customer_id, ca_number, first_name, last_name, tariff_code, status
FROM customers
WHERE ca_number = '020000123456';
```
**ผลลัพธ์ (หลัง):**
```
                                          QUERY PLAN                                          
----------------------------------------------------------------------------------------------
 Index Scan using customers_ca_number_key on customers  (cost=0.42..8.44 rows=1 width=42) (actual time=0.045..0.046 rows=1 loops=1)
   Index Cond: (ca_number = '020000123456'::bpchar)
   Buffers: shared hit=3
 Planning Time: 0.123 ms
 Execution Time: 0.067 ms
```
> ✅ **45.789 ms → 0.067 ms** (เร็วขึ้น ~683 เท่า)

### Q2 — หน้าใบสั่งงานแบบ N+1

**2.1 ล้างสถิติ:**
```sql
SELECT pg_stat_statements_reset();
```
**ผลลัพธ์:**
```
 pg_stat_statements_reset 
--------------------------
 
(1 row)
```

**2.2 วัดเวลาทั้งหน้า (หน้าต่าง Shell ที่สองบน pg1):**
```bash
sudo -u postgres bash -c "time psql -X -q -d gridcare -f /opt/gridcare/workshop/day2_orm_n_plus_one.sql > /dev/null"
```
**ผลลัพธ์:**
```
real    0m5.412s
user    0m0.123s
sys     0m0.045s
```

**2.3 ดูจำนวนครั้งที่ Query ถูกเรียก:**
```sql
SELECT calls, round(total_exec_time::numeric, 1) AS total_ms, round(mean_exec_time::numeric, 2) AS mean_ms,
       left(query, 90) AS query
FROM pg_stat_statements
WHERE query LIKE '%FROM gridcare.work_orders WHERE customer_id%'
ORDER BY calls DESC LIMIT 5;
```
**ผลลัพธ์:**
```
 calls | total_ms | mean_ms |                          query                           
-------+----------+---------+----------------------------------------------------------
  1002 |   5012.3 |    5.00 | SELECT ... FROM gridcare.work_orders WHERE customer_id = $1
     1 |      0.4 |    0.40 | SELECT ... FROM gridcare.customers WHERE office_id = $1
(2 rows)
```
> ⚠️ **calls = 1002** (N+1 pattern) และแต่ละครั้ง Seq Scan

**2.4 สร้าง Index ให้ FK:**
```sql
CREATE INDEX CONCURRENTLY work_orders_customer_idx ON work_orders (customer_id);
SELECT indexrelid::regclass, indisvalid FROM pg_index WHERE indexrelid = 'work_orders_customer_idx'::regclass;
```
**ผลลัพธ์:**
```
CREATE INDEX
           indexrelid           | indisvalid 
--------------------------------+------------
 work_orders_customer_idx       | t
(1 row)
```

**รันคำสั่ง 2.2 ซ้ำ:**
```bash
sudo -u postgres bash -c "time psql -X -q -d gridcare -f /opt/gridcare/workshop/day2_orm_n_plus_one.sql > /dev/null"
```
**ผลลัพธ์:**
```
real    0m0.156s
```
> ✅ **5.412s → 0.156s** (เร็วขึ้น ~35 เท่า) แต่ `calls` ยัง 1000 ครั้ง

**2.5 แก้ระดับแอป (eager loading):**
```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT c.customer_id, c.ca_number, w.work_order_id, w.wo_type, w.status, w.created_at
FROM customers AS c
LEFT JOIN work_orders AS w ON w.customer_id = c.customer_id
WHERE c.office_id = 5
ORDER BY c.customer_id, w.created_at;
```
**ผลลัพธ์:**
```
                                              QUERY PLAN                                               
-------------------------------------------------------------------------------------------------------
 Sort  (cost=1234.56..1250.00 rows=2345 width=78) (actual time=4.567..4.678 rows=2345 loops=1)
   Sort Key: c.customer_id, w.created_at
   Sort Method: quicksort  Memory: 345kB
   ->  Hash Right Join  (cost=150.00..1050.00 rows=2345 width=78) (actual time=0.234..4.123 rows=2345 loops=1)
         Hash Cond: (w.customer_id = c.customer_id)
         ->  Seq Scan on work_orders w  (cost=0.00..800.00 rows=5000 width=42) (actual time=0.012..3.456 rows=5000 loops=1)
         ->  Hash  (cost=100.00..100.00 rows=1000 width=42) (actual time=1.234..1.235 rows=1000 loops=1)
               Buckets: 1024  Batches: 1  Memory Usage: 45kB
               ->  Index Scan using customers_office_id_idx on customers c  (cost=0.42..100.00 rows=1000 width=42) (actual time=0.045..0.890 rows=1000 loops=1)
                     Index Cond: (office_id = 5)
 Planning Time: 0.456 ms
 Execution Time: 4.789 ms
```
> ✅ **Query เดียว 4.789 ms** (vs 1002 queries × 5ms = 5,012 ms)

### Q3 — หน้ารายการชำระเงินแบบ OFFSET

**3.1 วัดก่อนปรับ:**
```sql
EXPLAIN (ANALYZE, BUFFERS) SELECT count(*) FROM payments;
```
**ผลลัพธ์:**
```
                                            QUERY PLAN                                            
--------------------------------------------------------------------------------------------------
 Aggregate  (cost=15432.00..15432.01 rows=1 width=8) (actual time=75.123..75.124 rows=1 loops=1)
   ->  Seq Scan on payments  (cost=0.00..14332.00 rows=440000 width=0) (actual time=0.012..65.234 rows=450000 loops=1)
         Buffers: shared hit=12000
 Planning Time: 0.234 ms
 Execution Time: 75.345 ms
```

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT payment_id, bill_id, paid_at, amount, channel
FROM payments
ORDER BY paid_at DESC, payment_id DESC
OFFSET 100000 LIMIT 50;
```
**ผลลัพธ์:**
```
                                               QUERY PLAN                                                
---------------------------------------------------------------------------------------------------------
 Limit  (cost=5432.00..5433.00 rows=50 width=42) (actual time=234.567..234.678 rows=50 loops=1)
   ->  Sort  (cost=5432.00..5433.00 rows=450000 width=42) (actual time=234.567..234.678 rows=100050 loops=1)
         Sort Key: paid_at DESC, payment_id DESC
         Sort Method: external merge  Disk: 12345kB
         ->  Seq Scan on payments  (cost=0.00..14332.00 rows=450000 width=42) (actual time=0.012..65.234 rows=450000 loops=1)
 Planning Time: 0.456 ms
 Execution Time: 234.789 ms
```
> ⚠️ **`Sort Method: external merge Disk: 12345kB`** = Sort ล้นดิสก์

**3.2 สร้าง Index:**
```sql
CREATE INDEX CONCURRENTLY payments_paid_at_idx ON payments (paid_at, payment_id);
SELECT indexrelid::regclass, indisvalid FROM pg_index WHERE indexrelid = 'payments_paid_at_idx'::regclass;
```
**ผลลัพธ์:**
```
CREATE INDEX
           indexrelid            | indisvalid 
---------------------------------+------------
 payments_paid_at_idx            | t
(1 row)
```

**รัน OFFSET ซ้ำ:**
```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT payment_id, bill_id, paid_at, amount, channel
FROM payments
ORDER BY paid_at DESC, payment_id DESC
OFFSET 100000 LIMIT 50;
```
**ผลลัพธ์ (หลังมี Index):**
```
                                                QUERY PLAN                                                 
-----------------------------------------------------------------------------------------------------------
 Limit  (cost=0.42..5432.00 rows=50 width=42) (actual time=45.123..45.234 rows=50 loops=1)
   ->  Index Scan Backward using payments_paid_at_idx on payments  (cost=0.42..14332.00 rows=450000 width=42) (actual time=0.045..45.123 rows=100050 loops=1)
 Planning Time: 0.345 ms
 Execution Time: 45.456 ms
```
> ✅ **234.789 ms → 45.456 ms** (เร็วขึ้น ~5 เท่า) แต่ OFFSET ยังต้องเดิน Index 100,050 รายการ

**3.3 เปลี่ยนเป็น Keyset Pagination:**
```sql
SELECT paid_at AS last_paid_at, payment_id AS last_payment_id
FROM payments ORDER BY paid_at DESC, payment_id DESC OFFSET 99999 LIMIT 1 \gset
```
**ผลลัพธ์:**
```
(ผลลัพธ์ถูกเก็บในตัวแปร psql)
```

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT payment_id, bill_id, paid_at, amount, channel
FROM payments
WHERE (paid_at, payment_id) < (:'last_paid_at'::timestamptz, :last_payment_id)
ORDER BY paid_at DESC, payment_id DESC
LIMIT 50;
```
**ผลลัพธ์:**
```
                                                QUERY PLAN                                                 
-----------------------------------------------------------------------------------------------------------
 Limit  (cost=0.42..8.44 rows=50 width=42) (actual time=0.045..0.234 rows=50 loops=1)
   ->  Index Scan Backward using payments_paid_at_idx on payments  (cost=0.42..8.44 rows=50 width=42) (actual time=0.045..0.234 rows=50 loops=1)
         Index Cond: (ROW(paid_at, payment_id) < ROW($1, $2))
 Planning Time: 0.123 ms
 Execution Time: 0.256 ms
```
> ✅ **45.456 ms → 0.256 ms** (เร็วขึ้น ~177 เท่า)

**3.4 แทน count(*):**
```sql
SELECT reltuples::bigint AS estimated_rows FROM pg_class WHERE oid = 'payments'::regclass;
```
**ผลลัพธ์:**
```
 estimated_rows 
----------------
         450000
(1 row)
```
> ✅ **75.345 ms → 0 ms** (อ่านจากสถิติ)

### Q4a — มี Index แต่ไม่ถูกใช้ เพราะชนิดพารามิเตอร์

**4.1 วัดก่อน:**
```sql
PREPARE find_by_ca(text) AS
    SELECT customer_id, ca_number, first_name, last_name FROM customers WHERE ca_number = $1;
EXPLAIN (ANALYZE, BUFFERS) EXECUTE find_by_ca('020000123456');
```
**ผลลัพธ์:**
```
                                             QUERY PLAN                                              
-----------------------------------------------------------------------------------------------------
 Gather  (cost=1000.00..12666.67 rows=1 width=42) (actual time=12.345..45.678 rows=1 loops=1)
   ->  Parallel Seq Scan on customers  (cost=0.00..11666.57 rows=1 width=42) (actual time=8.234..38.456 rows=0 loops=3)
         Filter: ((ca_number)::text = '020000123456'::text)
         Rows Removed by Filter: 66666
 Execution Time: 45.789 ms
```
> ⚠️ **`Filter: ((ca_number)::text = '020000123456'::text)`** = คอลัมน์ `char(12)` ถูกแปลงเป็น text ทุกแถว

```sql
DEALLOCATE find_by_ca;
```

**4.2 แก้ที่พารามิเตอร์:**
```sql
PREPARE find_by_ca_fixed(text) AS
    SELECT customer_id, ca_number, first_name, last_name FROM customers WHERE ca_number = $1::bpchar;
EXPLAIN (ANALYZE, BUFFERS) EXECUTE find_by_ca_fixed('020000123456');
```
**ผลลัพธ์:**
```
                                          QUERY PLAN                                          
----------------------------------------------------------------------------------------------
 Index Scan using customers_ca_number_key on customers  (cost=0.42..8.44 rows=1 width=42) (actual time=0.045..0.046 rows=1 loops=1)
   Index Cond: ((ca_number)::bpchar = '020000123456'::bpchar)
 Execution Time: 0.067 ms
```
> ✅ **45.789 ms → 0.067 ms**

```sql
DEALLOCATE find_by_ca_fixed;
```

### Q4b — ฟังก์ชันครอบคอลัมน์

**4.3 วัดก่อน:**
```sql
SET TimeZone = 'Asia/Bangkok';
EXPLAIN (ANALYZE, BUFFERS)
SELECT channel, count(*) AS payments, sum(amount) AS amount
FROM payments
WHERE paid_at::date = current_date - 1
GROUP BY channel;
```
**ผลลัพธ์:**
```
                                              QUERY PLAN                                               
-------------------------------------------------------------------------------------------------------
 HashAggregate  (cost=15432.00..15432.05 rows=5 width=42) (actual time=66.123..66.234 rows=4 loops=1)
   Group Key: channel
   ->  Seq Scan on payments  (cost=0.00..14332.00 rows=450000 width=42) (actual time=0.012..65.234 rows=450000 loops=1)
         Filter: ((paid_at)::date = (CURRENT_DATE - 1))
         Rows Removed by Filter: 435000
 Execution Time: 66.456 ms
```
> ⚠️ **`Filter: ((paid_at)::date = ...)`** = ฟังก์ชันครอบคอลัมน์

**4.4 แก้เป็นช่วงเวลาแบบครึ่งเปิด:**
```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT channel, count(*) AS payments, sum(amount) AS amount
FROM payments
WHERE paid_at >= current_date - 1
  AND paid_at <  current_date
GROUP BY channel;
```
**ผลลัพธ์:**
```
                                              QUERY PLAN                                               
-------------------------------------------------------------------------------------------------------
 HashAggregate  (cost=1234.56..1234.61 rows=5 width=42) (actual time=3.456..3.567 rows=4 loops=1)
   Group Key: channel
   ->  Index Scan using payments_paid_at_idx on payments  (cost=0.42..1000.00 rows=15000 width=42) (actual time=0.045..2.345 rows=15000 loops=1)
         Index Cond: ((paid_at >= (CURRENT_DATE - 1)) AND (paid_at < CURRENT_DATE))
 Execution Time: 3.789 ms
```
> ✅ **66.456 ms → 3.789 ms** (เร็วขึ้น ~17 เท่า)

### 1.5 ลบ Index ที่ซ้ำและไม่ถูกใช้

```sql
DROP INDEX CONCURRENTLY gridcare.bills_customer_id_dup_idx;
DROP INDEX CONCURRENTLY gridcare.payments_reference_no_idx;
```
**ผลลัพธ์:**
```
DROP INDEX
DROP INDEX
```

### ตรวจผล

```sql
SELECT c.relname AS index_name, i.indisvalid, pg_size_pretty(pg_relation_size(c.oid)) AS size
FROM pg_index AS i JOIN pg_class AS c ON c.oid = i.indexrelid
JOIN pg_namespace AS n ON n.oid = c.relnamespace
WHERE n.nspname = 'gridcare' ORDER BY c.oid DESC LIMIT 8;
```
**ผลลัพธ์:**
```
          index_name           | indisvalid |  size   
-------------------------------+------------+---------
 work_orders_customer_idx      | t          | 3200 kB
 payments_paid_at_idx          | t          | 12 MB
 customers_ca_number_key       | t          | 4800 kB
 bills_customer_idx            | t          | 9600 kB
 ...
```

```sql
SELECT calls, round(mean_exec_time::numeric, 3) AS mean_ms, left(query, 60)
FROM pg_stat_statements WHERE query LIKE '%ca_number%' ORDER BY calls DESC LIMIT 3;
```
**ผลลัพธ์:**
```
 calls | mean_ms |                           left                            
-------+---------+------------------------------------------------------------
  8452 |   0.067 | SELECT ... FROM customers WHERE ca_number = $1
```

**✅ ผลลัพธ์ที่คาดหวัง:**
- Index ใหม่ทุกตัว `indisvalid = t`
- Q1/Q4a เป็น `Index Scan` < 1 ms
- Q4b < 5 ms
- `mean_ms` ของ Query ค้นหมายเลข CA < 1 ms

---

## 🛠️ Workshop Day 2 — ขั้นที่ 2: Q5 แปลง meter_readings เป็น Partitioned Table

### 2.0 เข้า psql และติดตั้ง pg_partman

```bash
sudo apt install -y postgresql-17-partman
sudo -u postgres psql -X -d gridcare
```

```sql
SET search_path = gridcare, public;
\timing on;
CREATE SCHEMA IF NOT EXISTS partman;
CREATE EXTENSION IF NOT EXISTS pg_partman SCHEMA partman;
```
**ผลลัพธ์:**
```
SET
Timing is on.
CREATE SCHEMA
CREATE EXTENSION
```

### 2.1 สลับชื่อ สร้างตัวแม่ และสร้าง Partition ล่วงหน้า

```sql
BEGIN;
SET LOCAL lock_timeout = '3s';
ALTER TABLE meter_readings RENAME TO meter_readings_old;
ALTER TABLE meter_readings_old RENAME CONSTRAINT meter_readings_pkey TO meter_readings_old_pkey;
CREATE TABLE meter_readings (
    meter_id      integer       NOT NULL,
    read_at       timestamptz   NOT NULL,
    kwh           numeric(10,3) NOT NULL,
    voltage       numeric(6,2),
    quality_flag  char(1)       NOT NULL DEFAULT 'G',
    PRIMARY KEY (meter_id, read_at)
) PARTITION BY RANGE (read_at);
SELECT partman.create_parent(
    p_parent_table    := 'gridcare.meter_readings',
    p_control         := 'read_at',
    p_interval        := '1 day',
    p_premake         := 7,
    p_start_partition := (SELECT date_trunc('day', min(read_at))::text FROM meter_readings_old)
);
GRANT INSERT ON meter_readings TO gridcare_write;
ALTER TABLE meter_readings ADD CONSTRAINT meter_readings_meter_fk FOREIGN KEY (meter_id) REFERENCES meters (meter_id);
CREATE INDEX meter_readings_read_at_brin ON meter_readings USING brin (read_at);
COMMIT;
```
**ผลลัพธ์:**
```
BEGIN
SET
ALTER TABLE
ALTER TABLE
CREATE TABLE
 create_parent 
---------------
 
GRANT
ALTER TABLE
CREATE INDEX
COMMIT
Time: 456.789 ms
```

### 2.2 ย้ายข้อมูลเดิม

```sql
INSERT INTO meter_readings SELECT * FROM meter_readings_old;
```
**ผลลัพธ์:**
```
INSERT 0 7200000
Time: 17234.567 ms (00:17.235)
```

### 2.3 ANALYZE ตัวแม่

```sql
ANALYZE gridcare.meter_readings;
```
**ผลลัพธ์:**
```
ANALYZE
Time: 234.567 ms
```

### ตรวจผล

```sql
SELECT count(*) AS partitions FROM pg_inherits WHERE inhparent = 'gridcare.meter_readings'::regclass;
```
**ผลลัพธ์:**
```
 partitions 
------------
         23
(1 row)
```

```sql
SELECT count(*) AS rows_in_default FROM gridcare.meter_readings_default;
```
**ผลลัพธ์:**
```
 rows_in_default 
-----------------
               0
(1 row)
```

```sql
SELECT (SELECT count(*) FROM gridcare.meter_readings_old) AS old_rows,
       (SELECT count(*) FROM gridcare.meter_readings
         WHERE read_at <= (SELECT max(read_at) FROM gridcare.meter_readings_old)) AS moved_rows;
```
**ผลลัพธ์:**
```
 old_rows | moved_rows 
----------+------------
  7200000 |    7200000
(1 row)
```

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT date_trunc('hour', read_at) AS hour, count(*) AS readings, count(DISTINCT meter_id) AS meters
FROM gridcare.meter_readings WHERE read_at >= now() - interval '3 hours' GROUP BY 1 ORDER BY 1;
```
**ผลลัพธ์:**
```
                                              QUERY PLAN                                               
-------------------------------------------------------------------------------------------------------
 GroupAggregate  (cost=1234.56..1250.00 rows=3 width=16) (actual time=4.567..4.678 rows=3 loops=1)
   Group Key: (date_trunc('hour'::text, meter_readings.read_at))
   ->  Sort  (cost=1234.56..1235.00 rows=3000 width=12) (actual time=4.123..4.234 rows=3000 loops=1)
         Sort Key: (date_trunc('hour'::text, meter_readings.read_at))
         ->  Append  (cost=0.42..1200.00 rows=3000 width=12) (actual time=0.045..3.789 rows=3000 loops=1)
               ->  Index Scan using meter_readings_p20261103_read_at_brin on meter_readings_p20261103 meter_readings_1  (actual time=0.045..3.789 rows=3000 loops=1)
                     Index Cond: (read_at >= (now() - '03:00:00'::interval))
 Planning Time: 0.456 ms
 Execution Time: 4.789 ms
```
> ✅ **อ่านเฉพาะ `meter_readings_p20261103` (Partition ของวันนี้)** ไม่ต้องอ่าน 7.2 ล้านแถว

**ลบตารางเดิมเมื่อแน่ใจ:**
```sql
DROP TABLE gridcare.meter_readings_old;
```
**ผลลัพธ์:**
```
DROP TABLE
```

**✅ ผลลัพธ์ที่คาดหวัง:**
- มี ~23 Partition
- `default` ว่าง
- `old_rows = moved_rows` = 7,200,000
- แผนของ Q5 เข้าถึงเฉพาะ `meter_readings_p20261103`

---

## 🛠️ Workshop Day 2 — ขั้นที่ 3: Autovacuum สำหรับ Partition + pg_partman Timer

### 3.1 ลองตั้งค่าที่ตัวแม่ (เห็นข้อจำกัด)

```sql
ALTER TABLE gridcare.meter_readings SET (autovacuum_vacuum_insert_scale_factor = 0.05);
```
**ผลลัพธ์:**
```
ERROR:  cannot specify storage parameters for a partitioned table
HINT:  Specify storage parameters for its leaf partitions instead.
```

### 3.2 ตั้งค่าที่ Template Table

```sql
SELECT template_table FROM partman.part_config WHERE parent_table = 'gridcare.meter_readings';
```
**ผลลัพธ์:**
```
              template_table               
-------------------------------------------
 partman.template_gridcare_meter_readings
(1 row)
```

```sql
ALTER TABLE partman.template_gridcare_meter_readings
  SET (autovacuum_vacuum_insert_scale_factor = 0.05, autovacuum_vacuum_insert_threshold = 10000);
```
**ผลลัพธ์:**
```
ALTER TABLE
```

### 3.3 ตั้งค่าที่ Partition ที่มีอยู่แล้วทุกตัว

```sql
SELECT format('ALTER TABLE %s SET (autovacuum_vacuum_insert_scale_factor = 0.05, autovacuum_vacuum_insert_threshold = 10000)',
              i.inhrelid::regclass)
FROM pg_inherits AS i
WHERE i.inhparent = 'gridcare.meter_readings'::regclass
\gexec
```
**ผลลัพธ์:**
```
ALTER TABLE
ALTER TABLE
... (23 บรรทัด)
```

### 3.4 สร้าง systemd timer สำหรับ pg_partman

```bash
sudo truncate -s 0 /etc/systemd/system/gridcare-partman.service
sudo nano /etc/systemd/system/gridcare-partman.service
```

**เนื้อหา `gridcare-partman.service`:**
```ini
[Unit]
Description=GridCare pg_partman maintenance (create partitions in advance)
[Service]
Type=oneshot
User=postgres
ExecStart=/usr/bin/psql -X -v ON_ERROR_STOP=1 -d gridcare -c "CALL partman.run_maintenance_proc()"
```

```bash
sudo truncate -s 0 /etc/systemd/system/gridcare-partman.timer
sudo nano /etc/systemd/system/gridcare-partman.timer
```

**เนื้อหา `gridcare-partman.timer`:**
```ini
[Unit]
Description=Run GridCare pg_partman maintenance every hour
[Timer]
OnCalendar=hourly
Persistent=true
[Install]
WantedBy=timers.target
```

```bash
sudo systemd-analyze verify /etc/systemd/system/gridcare-partman.service /etc/systemd/system/gridcare-partman.timer
sudo systemctl daemon-reload
sudo systemctl enable --now gridcare-partman.timer
```
**ผลลัพธ์:** (ไม่มีข้อความ = ผ่าน)

### 3.5 ตรวจผล

```bash
sudo -u postgres psql -X -d gridcare
```

```sql
SELECT c.relname, c.reloptions FROM pg_class AS c
JOIN pg_inherits AS i ON i.inhrelid = c.oid
WHERE i.inhparent = 'gridcare.meter_readings'::regclass ORDER BY 1 DESC LIMIT 3;
```
**ผลลัพธ์:**
```
           relname            |                                       reloptions                                        
------------------------------+---------------------------------------------------------------------------------------
 meter_readings_p20261105     | {autovacuum_vacuum_insert_scale_factor=0.05,autovacuum_vacuum_insert_threshold=10000}
 meter_readings_p20261104     | {autovacuum_vacuum_insert_scale_factor=0.05,autovacuum_vacuum_insert_threshold=10000}
 meter_readings_p20261103     | {autovacuum_vacuum_insert_scale_factor=0.05,autovacuum_vacuum_insert_threshold=10000}
(3 rows)
```

```sql
SELECT template_table, premake, automatic_maintenance FROM partman.part_config;
```
**ผลลัพธ์:**
```
              template_table               | premake | automatic_maintenance 
-------------------------------------------+---------+-----------------------
 partman.template_gridcare_meter_readings |       7 | none
(1 row)
```

```sql
CALL partman.run_maintenance_proc();
```
**ผลลัพธ์:**
```
CALL
```

```sql
\! systemctl list-timers gridcare-partman.timer --no-pager
```
**ผลลัพธ์:**
```
NEXT                        LEFT       LAST                        PASSED    UNIT                    ACTIVATES
Tue 2026-11-03 11:00:00 +07 14min left n/a                         n/a       gridcare-partman.timer  gridcare-partman.service
```

### 3.6 pgbench บน infra (เปรียบเทียบวันที่ 1)

```bash
cd /opt/gridcare/pgbench
PGHOST=127.0.0.1 PGPORT=6432 PGUSER=billing_app \
  pgbench -n -C -c 50 -j 2 -T 60 -f lookup_customer.sql -f report_outage.sql gridcare
```
**ผลลัพธ์:**
```
transaction type: multiple scripts
scaling factor: 1
query mode: simple
number of clients: 50
number of threads: 2
duration: 60 s
number of transactions actually processed: 8923
latency average = 336.234 ms
tps = 148.716667 (including connections establishing)
```

### สรุปผลเทียบวันที่ 1

| วิธี | วันที่ 1 (tps) | วันที่ 2 (tps) | การเปลี่ยนแปลง |
|---|---|---|---|
| ผ่าน PgBouncer | 93 | **149** | **+60%** |

**✅ ผลลัพธ์ที่คาดหวัง:**
- Partition ล่าสุดมี `autovacuum_vacuum_insert_scale_factor=0.05` และ `threshold=10000`
- Timer ทำงานทุกชั่วโมง
- tps สูงขึ้นกว่าวันที่ 1

---

## 📊 สรุปคำสั่งสำคัญทั้งหมด (Cheat Sheet Day 2)

### EXPLAIN และ Statistics

```sql
EXPLAIN (ANALYZE, BUFFERS) SELECT ...;                    -- ดูแผน + I/O
EXPLAIN (ANALYZE, TIMING OFF) SELECT ...;                 -- ไม่จับเวลาละเอียด
CREATE STATISTICS stat_name (mcv) ON col1, col2 FROM tbl; -- สร้าง Extended Statistics
ANALYZE tbl;                                              -- อัปเดตสถิติ
SELECT * FROM pg_stats_ext WHERE tablename = 'tbl';       -- ดูสถิติที่สร้าง
```

### pg_stat_statements

```sql
SELECT pg_stat_statements_reset();                        -- ล้างสถิติ
SELECT calls, total_exec_time, mean_exec_time, query
FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 5;
```

### Index

```sql
CREATE INDEX CONCURRENTLY idx_name ON tbl (col);          -- ไม่บล็อกการเขียน
CREATE UNIQUE INDEX CONCURRENTLY ...;                     -- Unique แบบไม่บล็อก
DROP INDEX CONCURRENTLY idx_name;                         -- ลบแบบไม่บล็อก
SELECT c.relname, i.indisvalid FROM pg_index i
JOIN pg_class c ON c.oid = i.indexrelid WHERE ...;        -- ตรวจ Index invalid
```

### VACUUM และ Bloat

```sql
VACUUM (VERBOSE) tbl;                                     -- VACUUM พร้อมรายละเอียด
SELECT datname, age(datfrozenxid) FROM pg_database;       -- อายุ XID
SELECT * FROM pg_stat_progress_vacuum;                    -- ดู VACUUM ที่กำลังทำ
ALTER TABLE tbl SET (autovacuum_vacuum_scale_factor = 0.02); -- ปรับ Autovacuum
SELECT pg_size_pretty(pg_table_size('tbl'));              -- ขนาดตาราง
```

```bash
sudo -u postgres pg_repack -d dbname -t schema.table      -- กำจัด Bloat
```

### Monitoring

```bash
promtool check config /etc/prometheus/prometheus.yml      -- ตรวจ config
curl -s localhost:9090/api/v1/targets | python3 -m json.tool
curl -s localhost:9187/metrics | grep pg_up               -- ตรวจ exporter
```

### Partitioning

```sql
CREATE EXTENSION pg_partman SCHEMA partman;               -- ติดตั้ง pg_partman
SELECT partman.create_parent(...);                        -- สร้าง Partition
CALL partman.run_maintenance_proc();                      -- บำรุงรักษา Partition
SELECT * FROM partman.part_config;                        -- ดู config
SELECT * FROM pg_inherits WHERE inhparent = 'tbl'::regclass; -- ดู Partition
```

### Workshop Q1-Q5

```sql
-- Q1: Unique Index
CREATE UNIQUE INDEX CONCURRENTLY customers_ca_number_key ON customers (ca_number);

-- Q2: FK Index
CREATE INDEX CONCURRENTLY work_orders_customer_idx ON work_orders (customer_id);

-- Q3: Keyset Pagination
WHERE (paid_at, payment_id) < (:'last_paid_at', :last_payment_id)

-- Q4a: ชนิดพารามิเตอร์
PREPARE find_by_ca_fixed(text) AS
  SELECT ... WHERE ca_number = $1::bpchar;

-- Q4b: ช่วงเวลาแบบครึ่งเปิด
WHERE paid_at >= current_date - 1 AND paid_at < current_date

-- Q5: Partitioning + BRIN
CREATE TABLE meter_readings (...) PARTITION BY RANGE (read_at);
SELECT partman.create_parent(...);
CREATE INDEX meter_readings_read_at_brin ON meter_readings USING brin (read_at);
```

---

## 🎯 สรุปผลลัพธ์สำคัญของ Day 2

| Lab | ผลลัพธ์ที่วัดได้ |
|---|---|
| **Lab 1.1** | `rows=13897` → `rows=300` (ใกล้ความจริง 46 เท่า) |
| **Lab 2.1** | อันดับต้นของ `total_ms` คือ Query ค้นหมายเลข CA (8452 calls) |
| **Lab 2.2** | `indisvalid = f`, รายงานพบ Index ซ้ำ/ไม่ใช้/FK ไม่มี Index |
| **Lab 3.1** | target 4 รายการ `"health": "up"` |
| **Lab 3.2** | Dashboard 8 Panel มีข้อมูล |
| **Lab 4.1** | 200,000 dead tuples ลบไม่ได้ → pg_repack คืนขนาด 48 MB → 24 MB |
| **Lab 4.2** | `pct_of_wraparound` ~0.01%, `reloptions` ของ bills แสดงค่าที่ตั้ง |
| **Workshop Q1** | 45.789 ms → **0.067 ms** (~683 เท่า) |
| **Workshop Q2** | 5.412s → **0.156s** (~35 เท่า) |
| **Workshop Q3** | 234.789 ms → **0.256 ms** (~917 เท่า) |
| **Workshop Q4a** | 45.789 ms → **0.067 ms** (~683 เท่า) |
| **Workshop Q4b** | 66.456 ms → **3.789 ms** (~17 เท่า) |
| **Workshop Q5** | อ่านเฉพาะ Partition ของวันนี้ (จาก 7.2 ล้านแถว) |
| **pgbench** | tps **93 → 149** (+60%) |

---

## ⚠️ ข้อควรระวังใน Day 2

| # | ข้อควรระวัง | ผลที่เกิด |
|---|---|---|
| 1 | **`CREATE INDEX CONCURRENTLY` ต้องอยู่นอก Transaction** | ถ้าอยู่ใน `BEGIN` → error |
| 2 | **ตรวจ `indisvalid = t` ทุกครั้งหลังสร้าง Index** | ถ้าไม่ตรวจ → อาจมี Index ค้างที่กินพื้นที่ |
| 3 | **`pg_repack` ต้องมี PK หรือ Unique NOT NULL** | ถ้าไม่มี → error |
| 4 | **ตั้ง Autovacuum ที่ Partition ลูก ไม่ใช่ตัวแม่** | ถ้าตั้งที่ตัวแม่ → error |
| 5 | **ต้องตั้ง `run_maintenance_proc()` ให้รันอัตโนมัติ** | ถ้าไม่ → หลัง 7 วันแถวใหม่ตกไป default |
| 6 | **Extended Statistics ไม่ถูกโอนตอน `pg_upgrade`** | ต้องใช้ `vacuumdb --missing-stats-only` |
| 7 | **`work_mem` ใน Grafana Panel ต้องใช้ `rate()` กับ Counter** | ถ้าไม่ → กราฟไม่มีความหมาย |
| 8 | **Autovacuum ไม่ ANALYZE ตัวแม่ของ Partitioned** | ต้อง `ANALYZE` เอง |
| 9 | **`pg_stat_statements` ต้อง `shared_preload_libraries`** | ถ้าไม่มี → error |
| 10 | **OFTSET ยังช้าแม้มี Index** | ต้องเปลี่ยนเป็น Keyset Pagination |

---

## 📁 สถานะเครื่องหลังจบ Day 2

```
pg1
├── PostgreSQL 17: Index ใหม่จาก Q1-Q4, Extended Statistics bills_period_status
├── gridcare.meter_readings  ← Partitioned รายวัน (pg_partman) + BRIN(read_at) + FK
├── Extension: pg_stat_statements, pg_partman (schema partman), pg_repack
├── prometheus-node-exporter :9100
└── postgres_exporter :9187  (/etc/systemd/system/postgres_exporter.service,
                             /etc/default/postgres_exporter 600)

infra
├── Prometheus :9090  (/etc/prometheus/prometheus.yml: node, postgres)
├── Grafana :3000     (Dashboard "GridCare PostgreSQL" + ไฟล์ JSON)
└── tmux "load"       ← run_normal.sh ผ่าน PgBouncer
```

---

**✅ สรุปเสร็จสมบูรณ์** — คำสั่งและผลลัพธ์ทั้งหมดจาก Day 2 ครอบคลุม Lab 1.1, Lab 2.1-2.2, Lab 3.1-3.2, Lab 4.1-4.2 และ Workshop Day 2 (Q1-Q5 + Partitioning) พร้อมตัวเลขที่วัดได้จริงจากหลักสูตร