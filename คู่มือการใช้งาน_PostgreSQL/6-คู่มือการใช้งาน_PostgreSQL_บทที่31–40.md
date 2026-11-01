# บทที่ 31–40

> หนังสือ: คู่มือการใช้งาน PostgreSQL สำหรับ DevOps Engineer, Cloud Engineer และ DBA  
> ส่วนที่ 4 Performance Tuning  
> โทน: ทางการ กระชับ เน้นใช้งานจริง

---

# บทที่ 31 pg_stat_statements

## 1. เรื่อง
`pg_stat_statements` Extension สำหรับเก็บสถิติ Query ที่ใช้บ่อยและใช้เวลาสูง

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจว่า `pg_stat_statements` เก็บอะไร  
2. เพื่อให้ตั้งค่าให้ถูกต้อง  
3. เพื่อให้ Query สถิติเพื่อหาต้นเหตุของปัญหา  
4. เพื่อให้ใช้ `queryid` ในการติดตาม Query ข้ามเวลา

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ตั้ง `shared_preload_libraries = 'pg_stat_statements'`  
- ตั้ง `pg_stat_statements.track = top`  
- Query `calls`, `total_exec_time`, `mean_exec_time`  
- ใช้ `pg_stat_statements_reset()`  
- ใช้ `queryid` ในการติดตาม

## 4. เนื้อหาโดยย่อ
`pg_stat_statements` เป็น Extension ที่เก็บสถิติของทุก Query ที่ Planner+Executor ทำงาน:
- `calls` — จำนวนครั้งที่เรียก  
- `total_exec_time` — เวลารวม  
- `mean_exec_time` — เวลาเฉลี่ย  
- `rows` — จำนวนแถวที่คืน  
- `shared_blks_hit`, `shared_blks_read` — Cache  
- `queryid` — Hash ของ Query

## 5. ประโยชน์ที่ได้รับ
- หา Top Query ที่ใช้เวลารวมสูงสุด  
- ระบุ Query ที่ช้าที่สุด  
- ใช้ `queryid` ในการติดตาม  
- ลดเวลาการสืบสวน Performance

## 6. ข้อควรระวัง
- **ต้อง `shared_preload_libraries`** และ Restart  
- **`pg_stat_statements.max`** ต้องเพียงพอ  
- **`pg_stat_statements.track`** มี `top` และ `all`  
- **`queryid` เปลี่ยนเมื่อ Query เปลี่ยนรูปแบบ**  
- **Reset จะล้างสถิติทั้งหมด**

## 7. ข้อดี
- เป็นมาตรฐานของ PostgreSQL  
- เก็บสถิติที่ Planner+Executor ทำงาน  
- ใช้ `queryid` ติดตามได้  
- มี View `pg_stat_statements` ให้ Query ง่าย

## 8. ข้อเสีย
- ต้อง Restart  
- Memory ที่ใช้จำกัด  
- ไม่เก็บ Plan

## 9. ข้อห้าม
- ห้ามเปิด `track = all` บน Production ที่มี Nested Function มาก  
- ห้าม Reset โดยไม่บันทึกค่า  
- ห้ามตั้ง `max` ต่ำเกินไป  
- ห้ามเปิด Extension แล้วไม่ตรวจ `shared_preload_libraries`  
- ห้ามใช้ `query` String แทน `queryid` ในการ Group

## 10. รายละเอียด

### 10.1 ตั้งค่า

**`conf.d/10-gridcare-tuning.conf`:**
```ini
shared_preload_libraries = 'pg_stat_statements,auto_explain'
pg_stat_statements.track = top
pg_stat_statements.max = 10000
pg_stat_statements.track_utility = on
pg_stat_statements.track_planning = off
```

**สร้าง Extension:**
```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

**ตรวจสอบ:**
```sql
SELECT name, setting FROM pg_settings WHERE name LIKE 'pg_stat_statements%';
```

ผลลัพธ์:
```text
              name               | setting 
---------------------------------+---------
 pg_stat_statements.max          | 10000
 pg_stat_statements.track        | top
 pg_stat_statements.track_planning | off
 pg_stat_statements.track_utility| on
```

### 10.2 Query พื้นฐาน

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

ผลลัพธ์:
```text
 calls | total_ms | mean_ms |   rows   | hit_pct |                            query                             
-------+----------+---------+----------+---------+--------------------------------------------------------------
 15023 |  45234   |   3.01  |  4506900 |   99.8  | UPDATE bills SET status = $1 WHERE bill_id = $2
  8452 |  23145   |   2.74  |   845200 |   99.5  | SELECT ... FROM customers WHERE ca_number = $1
  3201 |  12034   |   3.76  |   320100 |   98.2  | INSERT INTO meter_readings ...
   890 |   8901   |  10.00  |    89000 |   97.1  | SELECT sum(total_amount) FROM bills WHERE ...
   234 |   5678   |  24.26  |     2340 |   95.3  | SELECT ... FROM bills b JOIN customers c ...
(5 rows)
```

### 10.3 Reset

```sql
SELECT pg_stat_statements_reset();
```

ผลลัพธ์:
```text
 pg_stat_statements_reset 
--------------------------
 
(1 row)
```

> 💡 Reset ก่อนวัดค่าใหม่ทุกครั้ง เช่น ก่อน/หลังสร้าง Index

### 10.4 ติดตามด้วย `queryid`

```sql
SELECT queryid,
       calls,
       round(total_exec_time::numeric, 0) AS total_ms,
       round(mean_exec_time::numeric, 2)  AS mean_ms
FROM pg_stat_statements
WHERE query LIKE '%ca_number%'
ORDER BY calls DESC LIMIT 3;
```

ผลลัพธ์:
```text
       queryid       | calls | total_ms | mean_ms 
---------------------+-------+----------+---------
 1234567890123456789 |  8452 |    23145 |    2.74
```

### 10.5 ตั้ง `track_planning`

```sql
SELECT name, setting FROM pg_settings WHERE name = 'pg_stat_statements.track_planning';
```

ผลลัพธ์:
```text
              name               | setting 
---------------------------------+---------
 pg_stat_statements.track_planning| off
```

> 💡 เปิด `track_planning = on` เพื่อเก็บเวลา Planning ด้วย แต่จะใช้ Memory เพิ่ม

### 10.6 ล้างเฉพาะ Query

```sql
SELECT pg_stat_statements_reset(queryid => '1234567890123456789');
```

### 10.7 ตาราง Field สำคัญ

| Field | ความหมาย |
|---|---|
| `queryid` | Hash ของ Query |
| `query` | Query Text ที่ Normalize |
| `calls` | จำนวนครั้งที่เรียก |
| `total_exec_time` | เวลารวม (ms) |
| `mean_exec_time` | เวลาเฉลี่ย (ms) |
| `rows` | แถวที่คืน |
| `shared_blks_hit` | Cache Hit |
| `shared_blks_read` | Cache Miss |
| `temp_blks_written` | Temp File ที่เขียน |
| `wal_bytes` | WAL ที่สร้าง |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: ตั้งค่าและตรวจสอบ

```sql
-- ตรวจว่า Extension มีอยู่
\dx

-- ตรวจ Parameter
SHOW shared_preload_libraries;
```

ผลลัพธ์:
```text
                    List of installed extensions
        Name        | Version |   Schema   |         Description          
--------------------+---------+------------+------------------------------
 pg_stat_statements | 1.11    | public     | track planning and execution
 plpgsql            | 1.0     | pg_catalog | PL/pgSQL procedural language

              shared_preload_libraries              
-----------------------------------------------------
 pg_stat_statements,auto_explain
```

### ตัวอย่างที่ 2: หา Query ที่ใช้เวลารวมสูงสุด

```sql
SELECT calls, round(total_exec_time::numeric, 0) AS total_ms,
       round(mean_exec_time::numeric, 2) AS mean_ms,
       left(query, 100) AS query
FROM pg_stat_statements
ORDER BY total_exec_time DESC LIMIT 10;
```

### ตัวอย่างที่ 3: หา Query ที่ Temp File สูง

```sql
SELECT calls, round(mean_exec_time::numeric, 2) AS mean_ms,
       round(temp_blks_written / 128.0, 2) AS temp_mb,
       left(query, 80) AS query
FROM pg_stat_statements
WHERE temp_blks_written > 0
ORDER BY temp_blks_written DESC LIMIT 5;
```

ผลลัพธ์:
```text
 calls | mean_ms | temp_mb |                       query                        
-------+---------+---------+----------------------------------------------------
   234 |  234.5  |  120.3  | SELECT ... FROM bills b JOIN customers c ORDER BY...
```

> ✅ ถ้ามี `temp_blks_written` แสดงว่า `work_mem` ไม่พอ

### ตัวอย่างที่ 4: วัด Before/After Index

```sql
-- ก่อน
SELECT pg_stat_statements_reset();
-- รอ 5 นาที
SELECT calls, round(mean_exec_time::numeric, 3) AS mean_ms
FROM pg_stat_statements WHERE query LIKE '%ca_number%';

-- สร้าง Index
CREATE UNIQUE INDEX CONCURRENTLY customers_ca_number_key ON gridcare.customers (ca_number);

-- Reset
SELECT pg_stat_statements_reset();
-- รอ 5 นาที
SELECT calls, round(mean_exec_time::numeric, 3) AS mean_ms
FROM pg_stat_statements WHERE query LIKE '%ca_number%';
```

ผลลัพธ์:
```text
-- ก่อน
 calls | mean_ms 
-------+---------
  8452 |   2.740

-- หลัง
 calls | mean_ms 
-------+---------
  8452 |   0.067
```

## 12. สรุปย่อ จำง่าย
- **`shared_preload_libraries = 'pg_stat_statements'`** และ Restart  
- **`track = top`** เหมาะกับ Production ทั่วไป  
- **Query `total_exec_time`, `mean_exec_time`, `calls`**  
- **Reset ก่อนวัด Before/After**  
- **`queryid` ใช้ติดตาม**  
- **`temp_blks_written` = `work_mem` ไม่พอ**

ประโยคจำ: **“pg_stat_statements บอกว่า Query ไหนกินเวลา ไม่ใช่ Query ไหนน่าสงสัย”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — pg_stat_statements: https://www.postgresql.org/docs/17/pgstatstatements.html
- GridCare Workshop Day 2: Lab 2.1

---

# บทที่ 32 หา Query ที่ใช้เวลารวมสูงสุด

## 1. เรื่อง
กระบวนการหา Query ที่ใช้เวลารวมสูงสุด (Top Total Time) และ Query ที่ช้าที่สุด (Top Mean Time) เพื่อปรับแต่งได้ตรงจุด

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้ผู้อ่านแยกแยะ Total Time vs Mean Time  
2. เพื่อให้หา Top Query ที่กระทบระบบโดยรวม  
3. เพื่อให้หา Query ที่ Planner ผิด  
4. เพื่อให้จัดลำดับการปรับแต่งตาม Impact

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- Query Top 5 Total Time และ Top 5 Mean Time  
- ตรวจสอบ Query ที่มี `temp_blks_written`  
- ใช้ `pg_stat_statements` ในการจัดลำดับ  
- ใช้ `auto_explain` ตรวจ Plan ของ Query ช้า

## 4. เนื้อหาโดยย่อ
**Total Time** = `calls × mean_time` → บอก Query ที่กินเวลารวมสูงสุด → ปรับแล้วได้ Impact มากที่สุด  
**Mean Time** = เวลาเฉลี่ยต่อครั้ง → บอก Query ที่ช้าที่สุด → ปรับแล้วได้ Query ที่เร็วที่สุด  
**Impact** = `Total Time × Frequency` → ใช้จัดลำดับการทำงาน

## 5. ประโยชน์ที่ได้รับ
- ปรับแต่งได้ตรงจุด  
- ลดเวลาการสืบสวน  
- ใช้ `auto_explain` ตรวจ Plan จริง  
- จัดลำดับตาม Impact

## 6. ข้อควรระวัง
- **Query ที่ Total Time สูงอาจไม่ใช่ Query ที่ช้า**  
- **Query ที่ Mean Time สูงอาจเรียกไม่บ่อย**  
- **Query ที่ถูกเรียกบ่อยมากอาจมีผลกระทบไม่มาก**  
- **`auto_explain` ต้อง Restart**  
- **`auto_explain.log_analyze = on` ทำให้ช้า**

## 7. ข้อดี
- จัดลำดับได้ตาม Impact  
- ลดเวลาโดยรวมของระบบ  
- ลด MTTR ของ Performance

## 8. ข้อเสีย
- ต้อง Reset ก่อนวัด  
- Query ที่ Total Time สูงอาจไม่ใช่ Root Cause ของ Incident

## 9. ข้อห้าม
- ห้ามปรับแต่งเฉพาะ Query ที่ Mean Time สูงโดยไม่ดู Total Time  
- ห้ามใช้ `auto_explain.log_analyze = on` บน Production  
- ห้าม Reset โดยไม่บันทึก Baseline  
- ห้ามตัดสินใจจาก 1 Metric เท่านั้น

## 10. รายละเอียด

### 10.1 Top Total Time

```sql
SELECT calls,
       round(total_exec_time::numeric, 0) AS total_ms,
       round(mean_exec_time::numeric, 2)  AS mean_ms,
       round(100.0 * total_exec_time / sum(total_exec_time) OVER (), 1) AS pct,
       left(query, 100) AS query
FROM pg_stat_statements
WHERE dbid = (SELECT oid FROM pg_database WHERE datname = 'gridcare')
ORDER BY total_exec_time DESC
LIMIT 10;
```

ผลลัพธ์:
```text
 calls | total_ms | mean_ms |  pct  |                       query                        
-------+----------+---------+-------+----------------------------------------------------
 15023 |  45234   |   3.01  |  42.1 | UPDATE bills SET status = $1 WHERE bill_id = $2
  8452 |  23145   |   2.74  |  21.5 | SELECT ... FROM customers WHERE ca_number = $1
  3201 |  12034   |   3.76  |  11.2 | INSERT INTO meter_readings ...
```

### 10.2 Top Mean Time

```sql
SELECT calls,
       round(total_exec_time::numeric, 0) AS total_ms,
       round(mean_exec_time::numeric, 2)  AS mean_ms,
       left(query, 100) AS query
FROM pg_stat_statements
WHERE calls > 10
ORDER BY mean_exec_time DESC
LIMIT 10;
```

ผลลัพธ์:
```text
 calls | total_ms | mean_ms |                       query                        
-------+----------+---------+----------------------------------------------------
   234 |   5678   |  24.26  | SELECT ... FROM bills b JOIN customers c ...
    89 |   1234   |  13.87  | SELECT sum(total_amount) FROM bills WHERE ...
```

### 10.3 Query ที่มี Temp File

```sql
SELECT calls,
       round(mean_exec_time::numeric, 2) AS mean_ms,
       round(temp_blks_written / 128.0, 2) AS temp_mb,
       left(query, 80) AS query
FROM pg_stat_statements
WHERE temp_blks_written > 0
ORDER BY temp_blks_written DESC
LIMIT 5;
```

> ✅ ถ้ามี Temp File → เพิ่ม `work_mem` หรือสร้าง Index

### 10.4 Query ที่ Cache Hit ต่ำ

```sql
SELECT calls,
       round(100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0), 1) AS hit_pct,
       shared_blks_read,
       left(query, 80) AS query
FROM pg_stat_statements
WHERE shared_blks_read > 0
ORDER BY shared_blks_read DESC
LIMIT 5;
```

### 10.5 ใช้ auto_explain

**ตั้งค่า:**
```ini
shared_preload_libraries = 'pg_stat_statements,auto_explain'
auto_explain.log_min_duration = '2s'
auto_explain.log_analyze = off
auto_explain.log_buffers = on
```

**ดู Log:**
```bash
sudo grep -E -A12 "duration: [0-9.]+ ms +(plan|statement):" \
  /var/log/postgresql/postgresql-17-main.log | tail -30
```

ผลลัพธ์:
```text
2026-11-03 09:45:12.345 +07 [12345] postgres@gridcare app=pgbench client=10.104.0.13 LOG:  duration: 2345.678 ms  plan:
	Query Text: SELECT ... FROM customers WHERE ca_number = $1
	Seq Scan on customers  (cost=0.00..5820.00 rows=1 width=42) (actual time=12.345..2345.678 rows=1 loops=1)
	  Filter: (ca_number = '020000123456'::bpchar)
	  Rows Removed by Filter: 199999
	  Buffers: shared hit=1820
```

### 10.6 ตารางเลือก Metric

| สถานการณ์ | Metric ที่เลือก |
|---|---|
| Query ที่กินเวลารวมสูงสุด | `total_exec_time` |
| Query ที่ช้าที่สุด | `mean_exec_time` |
| Query ที่กิน Cache มาก | `shared_blks_read` |
| Query ที่กิน Temp File | `temp_blks_written` |
| Query ที่สร้าง WAL มาก | `wal_bytes` |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: วัด Before/After ที่มีผลกระทบมาก

**Baseline:**
```sql
SELECT pg_stat_statements_reset();
-- รอ 5 นาที
SELECT calls, round(total_exec_time::numeric, 0) AS total_ms,
       round(mean_exec_time::numeric, 3) AS mean_ms
FROM pg_stat_statements WHERE query LIKE '%ca_number%';
```

ผลลัพธ์:
```text
 calls | total_ms | mean_ms 
-------+----------+---------
  8452 |    23145 |   2.740
```

**สร้าง Index:**
```sql
CREATE UNIQUE INDEX CONCURRENTLY customers_ca_number_key ON gridcare.customers (ca_number);
```

**หลัง:**
```sql
SELECT pg_stat_statements_reset();
-- รอ 5 นาที
SELECT calls, round(total_exec_time::numeric, 0) AS total_ms,
       round(mean_exec_time::numeric, 3) AS mean_ms
FROM pg_stat_statements WHERE query LIKE '%ca_number%';
```

ผลลัพธ์:
```text
 calls | total_ms | mean_ms 
-------+----------+---------
  8452 |      566 |   0.067
```

> ✅ `mean_ms` ลดจาก 2.740 → 0.067 (~41 เท่า)

### ตัวอย่างที่ 2: ใช้ `auto_explain` ตรวจ Plan

```bash
sudo grep -E -A10 "duration: [0-9.]+ ms" /var/log/postgresql/postgresql-17-main.log | tail -15
```

ผลลัพธ์:
```text
2026-11-03 09:45:12.345 +07 [12345] postgres@gridcare app=pgbench LOG:  duration: 2345.678 ms  plan:
	Seq Scan on customers  (cost=0.00..5820.00 rows=1 width=42) (actual time=12.345..2345.678 rows=1)
	  Filter: (ca_number = '020000123456'::bpchar)
	  Rows Removed by Filter: 199999
```

### ตัวอย่างที่ 3: ใช้ pg_activity ดู Session สด

```bash
sudo -u postgres pg_activity -d gridcare
```

ผลลัพธ์:
```text
-- แสดง Session ที่กำลังทำงาน (กด q เพื่อออก)
```

## 12. สรุปย่อ จำง่าย
- **Total Time = Impact**  
- **Mean Time = ความช้าต่อครั้ง**  
- **Temp File = `work_mem` ไม่พอ**  
- **Cache Miss = `shared_buffers` หรือ Index**  
- **`auto_explain` ช่วยดู Plan จริง**  
- **ใช้ `pg_activity` ดู Session สด**

ประโยคจำ: **“Query ที่ช้าไม่ได้สำคัญเท่า Query ที่กินเวลารวมทั้งระบบ”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — pg_stat_statements: https://www.postgresql.org/docs/17/pgstatstatements.html
- PostgreSQL Documentation — auto_explain: https://www.postgresql.org/docs/17/auto-explain.html
- pg_activity: https://github.com/dalibo/pg_activity
- GridCare Workshop Day 2: Lab 2.1

---

# บทที่ 33 Index Health: ซ้ำ ไม่ถูกใช้ และ Invalid

## 1. เรื่อง
การตรวจสอบสุขภาพ Index ใน PostgreSQL: Index ซ้ำ, Index ไม่ถูกใช้, Index Invalid และ Foreign Key ที่ไม่มี Index

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้รู้ว่า Index ใดควรลบ ควรสร้าง หรือต้องดูแล  
2. เพื่อลด Disk และลด Overhead จากการเขียน  
3. เพื่อหา Index ที่ Invalid หลัง `CREATE INDEX CONCURRENTLY` ล้ม  
4. เพื่อหา FK ที่ไม่มี Index

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- หา Duplicate Index  
- หา Unused Index  
- หา Invalid Index  
- หา FK ที่ไม่มี Index  
- ลบ Index ที่ไม่จำเป็นได้อย่างปลอดภัย

## 4. เนื้อหาโดยย่อ
รายงานสุขภาพ Index ประกอบด้วย:
- **Duplicate Index** — Index ที่มีคอลัมน์เหมือนกัน  
- **Unused Index** — `idx_scan = 0`  
- **Invalid Index** — `indisvalid = false`  
- **FK without Index** — FK ที่ไม่มี Index ฝั่งลูก

## 5. ประโยชน์ที่ได้รับ
- ลด Disk  
- ลด Overhead จากการเขียน  
- ลด Query ที่เลือก Index ผิด  
- ทำให้ Backup เร็วขึ้น  
- ลดความเสี่ยงจาก Index ที่ Invalid

## 6. ข้อควรระวัง
- **Index ที่ `idx_scan = 0` อาจถูกใช้ในอนาคต**  
- **Index ที่ดูเหมือนซ้ำอาจมี Partial หรือ Expression**  
- **Invalid Index ต้อง `DROP INDEX CONCURRENTLY`**  
- **FK ไม่มี Index ทำให้ `DELETE` ที่แม่ช้า**  
- **ต้องตรวจ `indisvalid` หลัง `CREATE INDEX CONCURRENTLY`**

## 7. ข้อดี
- ลด Disk  
- ลด Overhead  
- ทำให้ Planner เลือกแผนง่ายขึ้น

## 8. ข้อเสีย
- ลบ Index ที่ยังต้องใช้อาจทำให้ Query ช้า  
- ต้องตรวจ `idx_scan` ในช่วงเวลาที่เหมาะสม

## 9. ข้อห้าม
- ห้ามลบ Index ที่ `idx_scan = 0` ในช่วง 7 วันแรกหลังสร้าง  
- ห้ามลบ Index ที่ Unique โดยไม่ตรวจ  
- ห้ามลบ Index ที่ FK ใช้  
- ห้ามลบ Index ที่ Invalid ด้วย `DROP INDEX` (ใช้ `CONCURRENTLY`)  
- ห้ามลบ Index ระหว่าง Business Hours

## 10. รายละเอียด

### 10.1 Duplicate Index

```sql
SELECT indrelid::regclass AS table_name,
       array_agg(indexrelid::regclass) AS indexes,
       count(*) AS dup_count
FROM pg_index
GROUP BY indrelid, indkey
HAVING count(*) > 1;
```

ผลลัพธ์:
```text
 table_name |           indexes                    | dup_count 
------------+--------------------------------------+-----------
 bills      | {bills_customer_id_dup_idx,bills_customer_idx} | 2
```

### 10.2 Unused Index

```sql
SELECT s.schemaname, s.relname, s.indexrelname, s.idx_scan,
       pg_size_pretty(pg_relation_size(s.indexrelid)) AS size
FROM pg_stat_user_indexes AS s
WHERE s.idx_scan = 0
  AND s.schemaname = 'gridcare'
ORDER BY pg_relation_size(s.indexrelid) DESC;
```

ผลลัพธ์:
```text
 schemaname |  relname  |       indexrelname        | idx_scan |  size  
------------+-----------+---------------------------+----------+--------
 gridcare   | payments  | payments_reference_no_idx |        0 | 12 MB
```

### 10.3 Invalid Index

```sql
SELECT c.relname AS index_name, i.indisvalid, i.indisready
FROM pg_index AS i
JOIN pg_class AS c ON c.oid = i.indexrelid
WHERE NOT i.indisvalid;
```

ผลลัพธ์:
```text
         index_name         | indisvalid | indisready 
----------------------------+------------+------------
 payments_paid_at_demo_idx  | f          | f
```

### 10.4 FK without Index

```sql
SELECT conrelid::regclass AS table_name, conname AS constraint_name,
       conkey AS columns
FROM pg_constraint
WHERE contype = 'f'
  AND connamespace = 'gridcare'::regnamespace
  AND NOT EXISTS (
    SELECT 1
    FROM pg_index AS i
    WHERE i.indrelid = conrelid
      AND i.indkey::int2[] @> conkey
  );
```

ผลลัพธ์:
```text
       table_name       |       constraint_name        | columns 
------------------------+------------------------------+---------
 gridcare.work_orders   | work_orders_customer_fk      | {2}
 gridcare.bills         | bills_meter_fk               | {3}
```

### 10.5 สาธิต Index ที่ Invalid

```sql
SET maintenance_work_mem = '64MB';
CREATE INDEX CONCURRENTLY payments_paid_at_demo_idx ON gridcare.payments (paid_at);
-- กด Ctrl+C ภายใน 1-2 วินาที
```

ผลลัพธ์:
```text
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

ผลลัพธ์:
```text
         relname          | indisvalid | indisready 
--------------------------+------------+------------
 payments_paid_at_demo_idx | f          | f
```

```sql
\d gridcare.payments
```

ผลลัพธ์ (บางส่วน):
```text
Indexes:
    "payments_pkey" PRIMARY KEY, btree (payment_id)
    "payments_paid_at_demo_idx" btree (paid_at) INVALID
```

**ลบ:**
```sql
DROP INDEX CONCURRENTLY gridcare.payments_paid_at_demo_idx;
```

ผลลัพธ์:
```text
DROP INDEX
```

### 10.6 รายงานสุขภาพ Index

```bash
sudo -u postgres psql -X -d gridcare -f /opt/gridcare/scripts/weekly_report.sql | less
```

ผลลัพธ์ (บางส่วน):
```text
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

### 10.7 ตารางการตัดสินใจ

| ประเภท | สิ่งที่ควรทำ |
|---|---|
| Duplicate | `DROP INDEX CONCURRENTLY` ตัวที่ซ้ำ |
| Unused (`idx_scan = 0` นาน > 30 วัน) | `DROP INDEX CONCURRENTLY` |
| Invalid | `DROP INDEX CONCURRENTLY` |
| FK without Index | `CREATE INDEX CONCURRENTLY` ที่ฝั่งลูก |
| Partial ที่ไม่ถูกใช้ | ตรวจ `WHERE` ก่อนลบ |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: ตรวจ Index ที่ Invalid แล้วลบ

```sql
SELECT c.relname, i.indisvalid
FROM pg_index AS i JOIN pg_class AS c ON c.oid = i.indexrelid
WHERE NOT i.indisvalid;
```

ผลลัพธ์:
```text
         relname          | indisvalid 
--------------------------+------------
 payments_paid_at_demo_idx | f
```

```sql
DROP INDEX CONCURRENTLY gridcare.payments_paid_at_demo_idx;
```

### ตัวอย่างที่ 2: สร้าง FK Index

```sql
CREATE INDEX CONCURRENTLY work_orders_customer_idx ON gridcare.work_orders (customer_id);
SELECT indexrelid::regclass, indisvalid FROM pg_index WHERE indexrelid = 'work_orders_customer_idx'::regclass;
```

ผลลัพธ์:
```text
           indexrelid           | indisvalid 
--------------------------------+------------
 work_orders_customer_idx       | t
```

### ตัวอย่างที่ 3: ตรวจ FK ที่ไม่มี Index

```sql
SELECT conrelid::regclass AS table_name, conname, conkey
FROM pg_constraint
WHERE contype = 'f' AND connamespace = 'gridcare'::regnamespace
  AND NOT EXISTS (
    SELECT 1 FROM pg_index AS i
    WHERE i.indrelid = conrelid AND i.indkey::int2[] @> conkey
  );
```

### ตัวอย่างที่ 4: ลบ Index ซ้ำ

```sql
DROP INDEX CONCURRENTLY gridcare.bills_customer_id_dup_idx;
DROP INDEX CONCURRENTLY gridcare.payments_reference_no_idx;
```

## 12. สรุปย่อ จำง่าย
- **Duplicate = ลบตัวที่ซ้ำ**  
- **Unused (`idx_scan = 0`) = ลบถ้าไม่ใช้ > 30 วัน**  
- **Invalid = `DROP INDEX CONCURRENTLY`**  
- **FK without Index = `CREATE INDEX CONCURRENTLY`**  
- **ตรวจทุกครั้งหลัง `CREATE INDEX CONCURRENTLY`**  
- **Weekly Report ช่วยตรวจสุขภาพ Index**

ประโยคจำ: **“Index ที่ไม่ถูกใช้คือ Disk ที่เสียเปล่า และ Overhead ที่ไม่มีประโยชน์”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — Index Maintenance: https://www.postgresql.org/docs/17/routine-index-maintenance.html
- PostgreSQL Documentation — pg_stat_user_indexes: https://www.postgresql.org/docs/17/monitoring-stats.html
- GridCare Workshop Day 2: Lab 2.2, Workshop Day 2 ขั้นที่ 1

---

# บทที่ 34 N+1 และ Anti-pattern จาก ORM

## 1. เรื่อง
ปัญหา N+1 Query และ Anti-pattern ที่พบบ่อยจาก ORM พร้อมวิธีแก้

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจ N+1 Pattern  
2. เพื่อให้ตรวจพบ N+1 จาก `pg_stat_statements`  
3. เพื่อให้แก้ N+1 ด้วย Eager Loading  
4. เพื่อให้เข้าใจ Anti-pattern อื่นจาก ORM

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- อธิบาย N+1 Pattern  
- ตรวจ N+1 จาก `calls` ที่สูง  
- แก้ด้วย JOIN, `IN`, Eager Loading  
- ระบุ Anti-pattern: Query ไม่มี WHERE, `SELECT *`, `OFFSET` ใหญ่

## 4. เนื้อหาโดยย่อ
**N+1 Pattern** = Query 1 ครั้งเพื่อดึง List แล้วตามด้วย N ครั้งเพื่อดึงรายละเอียด  
เช่น:
1. `SELECT * FROM customers WHERE office_id = 5` (1 Query)  
2. `SELECT * FROM work_orders WHERE customer_id = ?` (N Query)

**ผลลัพธ์:** N+1 Query ทำให้ระบบช้า แม้ Query เดียวจะเร็ว

**วิธีแก้:**
- **JOIN** — Query เดียว  
- **`WHERE customer_id IN (...)`** — 1 Query  
- **Eager Loading** ใน ORM เช่น `JOIN FETCH`, `include`, `preload`

## 5. ประโยชน์ที่ได้รับ
- ลด Round-Trip  
- ลด Total Time  
- ลด Connection ที่ใช้  
- ทำให้ Query เร็วขึ้นอย่างมีนัยสำคัญ

## 6. ข้อควรระวัง
- **JOIN อาจทำให้ Query Plan หนักขึ้น**  
- **`IN` ที่มีค่ามากเกินไปอาจทำให้ Query ช้า**  
- **`IN` มี Limit ~32,767 ค่า (ขึ้นกับ Memory)**  
- **ORM บางตัว Auto Eager Loading** ทำให้ข้อมูลใหญ่เกิน

## 7. ข้อดี
- ลด Round-Trip  
- ลด Total Time  
- ลด Connection ที่ใช้

## 8. ข้อเสีย
- JOIN อาจทำให้ Plan หนักขึ้น  
- ต้องแก้โค้ดใน ORM

## 9. ข้อห้าม
- ห้าม N+1 บน Production โดยไม่แก้  
- ห้าม `IN` กับค่ามากเกินไป  
- ห้ามใช้ `SELECT *` ใน Eager Loading  
- ห้ามใช้ `OFFSET` ใหญ่  
- ห้าม Join ตารางใหญ่โดยไม่มี Index

## 10. รายละเอียด

### 10.1 N+1 Pattern

```text
1. SELECT ... FROM customers WHERE office_id = 5;     -- 1 Query, 1000 แถว
2. SELECT ... FROM work_orders WHERE customer_id = 1; -- N Query
3. SELECT ... FROM work_orders WHERE customer_id = 2;
...
1002. SELECT ... FROM work_orders WHERE customer_id = 1000;
```

### 10.2 ตรวจ N+1 ด้วย `pg_stat_statements`

```sql
SELECT calls,
       round(total_exec_time::numeric, 1) AS total_ms,
       round(mean_exec_time::numeric, 2) AS mean_ms,
       left(query, 90) AS query
FROM pg_stat_statements
WHERE query LIKE '%FROM gridcare.work_orders WHERE customer_id%'
ORDER BY calls DESC LIMIT 5;
```

ผลลัพธ์:
```text
 calls | total_ms | mean_ms |                          query                           
-------+----------+---------+----------------------------------------------------------
  1002 |   5012.3 |    5.00 | SELECT ... FROM gridcare.work_orders WHERE customer_id = $1
     1 |      0.4 |    0.40 | SELECT ... FROM gridcare.customers WHERE office_id = $1
```

> ⚠️ `calls = 1002` แสดง N+1 Pattern

### 10.3 วัดผลก่อนแก้

```bash
sudo -u postgres bash -c "time psql -X -q -d gridcare -f /opt/gridcare/workshop/day2_orm_n_plus_one.sql > /dev/null"
```

ผลลัพธ์:
```text
real    0m5.412s
user    0m0.123s
sys     0m0.045s
```

### 10.4 สร้าง Index ให้ FK

```sql
CREATE INDEX CONCURRENTLY work_orders_customer_idx ON gridcare.work_orders (customer_id);
```

### 10.5 วัดผลหลังแก้ Index

```bash
sudo -u postgres bash -c "time psql -X -q -d gridcare -f /opt/gridcare/workshop/day2_orm_n_plus_one.sql > /dev/null"
```

ผลลัพธ์:
```text
real    0m0.156s
```

> ✅ **5.412s → 0.156s** (~35 เท่า) แต่ `calls` ยัง 1000 ครั้ง

### 10.6 แก้ระดับ ORM ด้วย Eager Loading

**แบบ N+1:**
```python
# Python SQLAlchemy
customers = session.query(Customer).filter_by(office_id=5).all()
for c in customers:
    print(c.work_orders)  # N+1
```

**แก้ด้วย `selectinload`:**
```python
from sqlalchemy.orm import selectinload

customers = (
    session.query(Customer)
    .options(selectinload(Customer.work_orders))
    .filter_by(office_id=5)
    .all()
)
```

**หรือ JOIN:**
```sql
SELECT c.customer_id, c.ca_number, w.work_order_id, w.wo_type, w.status, w.created_at
FROM gridcare.customers AS c
LEFT JOIN gridcare.work_orders AS w ON w.customer_id = c.customer_id
WHERE c.office_id = 5
ORDER BY c.customer_id, w.created_at;
```

### 10.7 Query Plan ที่ดี

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT c.customer_id, c.ca_number, w.work_order_id, w.wo_type, w.status, w.created_at
FROM gridcare.customers AS c
LEFT JOIN gridcare.work_orders AS w ON w.customer_id = c.customer_id
WHERE c.office_id = 5
ORDER BY c.customer_id, w.created_at;
```

ผลลัพธ์:
```text
                                              QUERY PLAN                                               
-------------------------------------------------------------------------------------------------------
 Sort  (cost=1234.56..1250.00 rows=2345 width=78) (actual time=4.567..4.678 rows=2345 loops=1)
   Sort Key: c.customer_id, w.created_at
   ->  Hash Right Join  (cost=150.00..1050.00 rows=2345 width=78) (actual time=0.234..4.123 rows=2345)
         Hash Cond: (w.customer_id = c.customer_id)
         ->  Seq Scan on work_orders w  (actual time=0.012..3.456 rows=5000 loops=1)
         ->  Hash  (actual time=1.234..1.235 rows=1000 loops=1)
               ->  Index Scan using customers_office_id_idx on customers c
                     (actual time=0.045..0.890 rows=1000 loops=1)
                     Index Cond: (office_id = 5)
 Execution Time: 4.789 ms
```

> ✅ **Query เดียว 4.789 ms** (vs 1002 queries × 5ms = 5,012 ms)

### 10.8 Anti-pattern ที่พบบ่อย

| Anti-pattern | ปัญหา | วิธีแก้ |
|---|---|---|
| N+1 | Query N+1 ครั้ง | JOIN / Eager Loading |
| `SELECT *` | อ่านคอลัมน์เกิน | ระบุคอลัมน์ |
| `OFFSET` ใหญ่ | Sort ทั้งตาราง | Keyset Pagination |
| ฟังก์ชันครอบคอลัมน์ | ไม่ใช้ Index | เปลี่ยนเป็นช่วงเวลา |
| ชนิดพารามิเตอร์ไม่ตรง | ไม่ใช้ Index | Cast ให้ตรง |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: ตรวจ N+1

```sql
SELECT pg_stat_statements_reset();
-- รอ 5 นาที
SELECT calls, round(total_exec_time::numeric, 0) AS total_ms,
       left(query, 80) AS query
FROM pg_stat_statements
ORDER BY calls DESC LIMIT 5;
```

ผลลัพธ์:
```text
 calls | total_ms |                          query                           
-------+----------+----------------------------------------------------------
  1002 |   5012   | SELECT ... FROM gridcare.work_orders WHERE customer_id = $1
     1 |      0   | SELECT ... FROM gridcare.customers WHERE office_id = $1
```

### ตัวอย่างที่ 2: แก้ด้วย `IN`

```sql
SELECT *
FROM gridcare.work_orders
WHERE customer_id IN (
  SELECT customer_id FROM gridcare.customers WHERE office_id = 5
);
```

> ✅ 1 Query แทน N+1

### ตัวอย่างที่ 3: แก้ด้วย JOIN ที่ดี

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT c.customer_id, c.ca_number, w.work_order_id, w.status
FROM gridcare.customers AS c
LEFT JOIN gridcare.work_orders AS w ON w.customer_id = c.customer_id
WHERE c.office_id = 5;
```

## 12. สรุปย่อ จำง่าย
- **N+1 = Query 1 + N**  
- **ตรวจด้วย `calls` ที่สูงใน `pg_stat_statements`**  
- **แก้ด้วย JOIN, `IN`, Eager Loading**  
- **สร้าง Index ให้ FK ด้วย**  
- **ระวัง Anti-pattern: `SELECT *`, `OFFSET` ใหญ่, ฟังก์ชันครอบคอลัมน์**

ประโยคจำ: **“N+1 ทำให้ Query เดียวที่เร็ว กลายเป็นระบบที่ช้า”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — Performance Tips: https://www.postgresql.org/docs/17/performance-tips.html
- SQLAlchemy — Relationship Loading: https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html
- GridCare Workshop Day 2: Workshop Day 2 ขั้นที่ 1 (Q2)

---

# บทที่ 35 Keyset Pagination

## 1. เรื่อง
การแบ่งหน้าแบบ Keyset Pagination เพื่อทดแทน `OFFSET` ที่ช้าเมื่อข้อมูลมีจำนวนมาก

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจว่า `OFFSET` ช้าเมื่อ Offset ใหญ่  
2. เพื่อให้ใช้ Keyset Pagination ได้  
3. เพื่อให้เข้าใจข้อจำกัดของ Keyset  
4. เพื่อให้เลือกใช้ให้เหมาะกับงาน

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- อธิบายว่า `OFFSET` ช้าอย่างไร  
- เขียน Keyset Pagination ด้วย `WHERE (col1, col2) < (v1, v2)`  
- สร้าง Index ที่รองรับ Keyset  
- เปรียบเทียบ Before/After

## 4. เนื้อหาโดยย่อ
**OFFSET** — PostgreSQL ต้องอ่านแถวทั้งหมดก่อน Offset แล้วตัด  
**Keyset** — ใช้ `WHERE` กับ Index เพื่อข้ามไปจุดที่ต้องการเลย

**OFFSET:**
```sql
SELECT * FROM payments ORDER BY paid_at DESC, payment_id DESC OFFSET 100000 LIMIT 50;
```

**Keyset:**
```sql
SELECT * FROM payments
WHERE (paid_at, payment_id) < (:$last_paid_at, :$last_payment_id)
ORDER BY paid_at DESC, payment_id DESC
LIMIT 50;
```

## 5. ประโยชน์ที่ได้รับ
- เร็วขึ้นมากเมื่อ Offset ใหญ่  
- ลด Sort  
- ลด I/O  
- ทำให้ Page เร็วเท่ากันทุกหน้า

## 6. ข้อควรระวัง
- **Keyset ต้องมี Unique Tie-breaker**  
- **ต้องมี Index ที่ตรงกับ `ORDER BY` + `WHERE`**  
- **Keyset ไม่รองรับการกระโดดหน้า**  
- **ต้องส่ง `last_paid_at`, `last_payment_id` มาจาก Client**  
- **ค่า `NULL` ต้องจัดการเป็นพิเศษ**

## 7. ข้อดี
- เร็วเท่ากันทุกหน้า  
- ลด I/O  
- เหมาะกับ Infinite Scroll

## 8. ข้อเสีย
- ไม่รองรับ Jump to Page N  
- ต้องมี Unique Key  
- Client ต้องเก็บ Cursor

## 9. ข้อห้าม
- ห้ามใช้ `OFFSET` ใหญ่บน Production ที่ข้อมูลมาก  
- ห้าม Keyset โดยไม่มี Index  
- ห้าม Keyset โดยไม่มี Unique Tie-breaker  
- ห้าม Keyset กับ `NULL` โดยไม่ตรวจ  
- ห้าม Keyset กับ Sort ที่ไม่เสถียร

## 10. รายละเอียด

### 10.1 OFFSET ที่ช้า

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT payment_id, bill_id, paid_at, amount, channel
FROM gridcare.payments
ORDER BY paid_at DESC, payment_id DESC
OFFSET 100000 LIMIT 50;
```

ผลลัพธ์ (ก่อนมี Index):
```text
 Limit  (cost=5432.00..5433.00 rows=50 width=42) (actual time=234.567..234.678 rows=50 loops=1)
   ->  Sort  (cost=5432.00..5433.00 rows=450000 width=42) (actual time=234.567..234.678 rows=100050)
         Sort Key: paid_at DESC, payment_id DESC
         Sort Method: external merge  Disk: 12345kB
         ->  Seq Scan on payments (actual time=0.012..65.234 rows=450000 loops=1)
 Execution Time: 234.789 ms
```

> ⚠️ Sort ล้น Disk (`external merge`)

### 10.2 สร้าง Index ที่รองรับ Keyset

```sql
CREATE INDEX CONCURRENTLY payments_paid_at_idx ON gridcare.payments (paid_at, payment_id);
```

### 10.3 OFFSET หลังมี Index

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT payment_id, bill_id, paid_at, amount, channel
FROM gridcare.payments
ORDER BY paid_at DESC, payment_id DESC
OFFSET 100000 LIMIT 50;
```

ผลลัพธ์:
```text
 Limit  (cost=0.42..5432.00 rows=50 width=42) (actual time=45.123..45.234 rows=50 loops=1)
   ->  Index Scan Backward using payments_paid_at_idx on payments
         (cost=0.42..14332.00 rows=450000 width=42) (actual time=0.045..45.123 rows=100050 loops=1)
 Execution Time: 45.456 ms
```

> ✅ **234.789 ms → 45.456 ms** แต่ OFFSET ยังต้องเดิน Index 100,050 รายการ

### 10.4 Keyset Pagination

**หน้าแรก:**
```sql
SELECT paid_at AS last_paid_at, payment_id AS last_payment_id
FROM gridcare.payments
ORDER BY paid_at DESC, payment_id DESC
OFFSET 99999 LIMIT 1 \gset
```

**หน้าถัดไป:**
```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT payment_id, bill_id, paid_at, amount, channel
FROM gridcare.payments
WHERE (paid_at, payment_id) < (:'last_paid_at'::timestamptz, :last_payment_id)
ORDER BY paid_at DESC, payment_id DESC
LIMIT 50;
```

ผลลัพธ์:
```text
 Limit  (cost=0.42..8.44 rows=50 width=42) (actual time=0.045..0.234 rows=50 loops=1)
   ->  Index Scan Backward using payments_paid_at_idx on payments
         (cost=0.42..8.44 rows=50 width=42) (actual time=0.045..0.234 rows=50 loops=1)
         Index Cond: (ROW(paid_at, payment_id) < ROW($1, $2))
 Execution Time: 0.256 ms
```

> ✅ **45.456 ms → 0.256 ms** (~177 เท่า)

### 10.5 ตารางเปรียบเทียบ

| วิธี | หน้า 1 | หน้า 100 | หน้า 1000 |
|---|---|---|---|
| OFFSET (ไม่มี Index) | 65 ms | 234 ms | 2345 ms |
| OFFSET (มี Index) | 0.2 ms | 45 ms | 450 ms |
| Keyset | 0.2 ms | 0.2 ms | 0.2 ms |

### 10.6 Keyset ที่มี `NULL`

```sql
-- ถ้า paid_at เป็น NULL ต้องใช้ NULLS LAST
ORDER BY paid_at DESC NULLS LAST, payment_id DESC

-- ตรวจด้วย
WHERE (paid_at, payment_id) < (:'last_paid_at', :last_payment_id)
   OR (paid_at IS NULL AND :'last_paid_at' IS NOT NULL)
```

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Client ส่ง Cursor

**API Request:**
```json
{
  "limit": 50,
  "last_paid_at": "2026-11-03T10:00:00Z",
  "last_payment_id": 12345
}
```

**SQL:**
```sql
SELECT payment_id, bill_id, paid_at, amount, channel
FROM gridcare.payments
WHERE (paid_at, payment_id) < ('2026-11-03T10:00:00Z'::timestamptz, 12345)
ORDER BY paid_at DESC, payment_id DESC
LIMIT 50;
```

### ตัวอย่างที่ 2: ใช้ `\gset` ใน Script

```sql
-- หน้าแรก
SELECT paid_at AS last_paid_at, payment_id AS last_payment_id
FROM gridcare.payments
ORDER BY paid_at DESC, payment_id DESC
LIMIT 50;

-- ใช้ค่าที่ได้
SELECT *
FROM gridcare.payments
WHERE (paid_at, payment_id) < (:'last_paid_at', :last_payment_id)
ORDER BY paid_at DESC, payment_id DESC
LIMIT 50;
```

### ตัวอย่างที่ 3: ใช้ Count แบบประมาณ

```sql
-- แทน count(*) ที่ช้า
SELECT reltuples::bigint AS estimated_rows FROM pg_class WHERE oid = 'gridcare.payments'::regclass;
```

ผลลัพธ์:
```text
 estimated_rows 
----------------
         450000
```

## 12. สรุปย่อ จำง่าย
- **OFFSET ช้าเมื่อ Offset ใหญ่**  
- **Keyset = `WHERE (col1, col2) < (v1, v2)`**  
- **ต้องมี Unique Tie-breaker**  
- **ต้องมี Index ที่ตรงกับ `ORDER BY` + `WHERE`**  
- **Keyset เร็วเท่ากันทุกหน้า**  
- **แทน `count(*)` ด้วย `reltuples`**

ประโยคจำ: **“OFFSET เดินไปหา Keyset กระโดดไปหา”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — LIMIT and OFFSET: https://www.postgresql.org/docs/17/queries-limit.html
- GridCare Workshop Day 2: Workshop Day 2 ขั้นที่ 1 (Q3)

---

# บทที่ 36 ฟังก์ชันครอบคอลัมน์และชนิดข้อมูล

## 1. เรื่อง
Anti-pattern ที่ทำให้ Index ไม่ถูกใช้: ฟังก์ชันครอบคอลัมน์ (Function on Column) และชนิดข้อมูลไม่ตรง

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจว่า `WHERE f(col) = v` ทำให้ Index ไม่ถูกใช้  
2. เพื่อให้เข้าใจว่า `col = $1` ที่ชนิดไม่ตรงทำให้ Index ไม่ถูกใช้  
3. เพื่อให้แก้ด้วย Expression Index หรือการเปลี่ยน Query  
4. เพื่อให้เข้าใจว่า Planner เลือก Index ผิดได้อย่างไร

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ตรวจจับ `Filter: (f(col) = ...)` ใน Plan  
- แก้ `paid_at::date = current_date` เป็น `paid_at >= current_date AND paid_at < current_date + 1`  
- ใช้ `PREPARE ... $1::bpchar` เพื่อแก้ชนิด  
- สร้าง Expression Index เมื่อจำเป็น

## 4. เนื้อหาโดยย่อ
**Anti-pattern 1: ฟังก์ชันครอบคอลัมน์**
```sql
WHERE paid_at::date = current_date - 1
```
→ PostgreSQL ต้องคำนวณ `paid_at::date` ทุกแถว → ไม่ใช้ Index

**แก้:**
```sql
WHERE paid_at >= current_date - 1 AND paid_at < current_date
```

**Anti-pattern 2: ชนิดข้อมูลไม่ตรง**
```sql
PREPARE find_by_ca(text) AS SELECT ... WHERE ca_number = $1;
```
→ `ca_number` เป็น `char(12)` ถูก Cast เป็น `text` ทุกแถว

**แก้:**
```sql
PREPARE find_by_ca(text) AS SELECT ... WHERE ca_number = $1::bpchar;
```

## 5. ประโยชน์ที่ได้รับ
- Index ถูกใช้จริง  
- Query เร็วขึ้น  
- ลด CPU  
- ลด I/O

## 6. ข้อควรระวัง
- **Expression Index ต้องตรงกับ Expression ใน Query เป๊ะ ๆ**  
- **Cast ต้องทำที่ Parameter ไม่ใช่คอลัมน์**  
- **Planner อาจไม่ใช้ Expression Index ถ้า Statistic ไม่ครบ**  
- **`::date` บน Timestamp จะตัด Timezone**

## 7. ข้อดี
- เร็วขึ้นอย่างมีนัยสำคัญ  
- ไม่ต้องเปลี่ยน Schema  
- Expression Index ใช้ได้เมื่อจำเป็น

## 8. ข้อเสีย
- Expression Index เพิ่ม Overhead ในการเขียน  
- ต้องจำ Expression ให้ตรง

## 9. ข้อห้าม
- ห้าม `WHERE f(col) = v` บน Production  
- ห้าม Cast คอลัมน์ใน `WHERE`  
- ห้าม Expression Index ที่ไม่ตรงกับ Query  
- ห้ามใช้ `::date` กับ `timestamptz` โดยไม่เข้าใจ Timezone  
- ห้ามลืม `::bpchar` เมื่อ Column เป็น `char(n)`

## 10. รายละเอียด

### 10.1 ฟังก์ชันครอบคอลัมน์ — ปัญหา

```sql
SET TimeZone = 'Asia/Bangkok';
EXPLAIN (ANALYZE, BUFFERS)
SELECT channel, count(*) AS payments, sum(amount) AS amount
FROM gridcare.payments
WHERE paid_at::date = current_date - 1
GROUP BY channel;
```

ผลลัพธ์:
```text
 HashAggregate  (cost=15432.00..15432.05 rows=5 width=42) (actual time=66.123..66.234 rows=4 loops=1)
   Group Key: channel
   ->  Seq Scan on payments  (cost=0.00..14332.00 rows=450000 width=42) (actual time=0.012..65.234 rows=450000)
         Filter: ((paid_at)::date = (CURRENT_DATE - 1))
         Rows Removed by Filter: 435000
 Execution Time: 66.456 ms
```

> ⚠️ `Filter: ((paid_at)::date = ...)` = ฟังก์ชันครอบคอลัมน์

### 10.2 ฟังก์ชันครอบคอลัมน์ — วิธีแก้

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT channel, count(*) AS payments, sum(amount) AS amount
FROM gridcare.payments
WHERE paid_at >= current_date - 1
  AND paid_at <  current_date
GROUP BY channel;
```

ผลลัพธ์:
```text
 HashAggregate  (cost=1234.56..1234.61 rows=5 width=42) (actual time=3.456..3.567 rows=4 loops=1)
   Group Key: channel
   ->  Index Scan using payments_paid_at_idx on payments
         (cost=0.42..1000.00 rows=15000 width=42) (actual time=0.045..2.345 rows=15000 loops=1)
         Index Cond: ((paid_at >= (CURRENT_DATE - 1)) AND (paid_at < CURRENT_DATE))
 Execution Time: 3.789 ms
```

> ✅ **66.456 ms → 3.789 ms** (~17 เท่า)

### 10.3 ชนิดข้อมูลไม่ตรง — ปัญหา

```sql
PREPARE find_by_ca(text) AS
    SELECT customer_id, ca_number, first_name, last_name FROM gridcare.customers WHERE ca_number = $1;
EXPLAIN (ANALYZE, BUFFERS) EXECUTE find_by_ca('020000123456');
```

ผลลัพธ์:
```text
 Gather  (cost=1000.00..12666.67 rows=1 width=42) (actual time=12.345..45.678 rows=1 loops=1)
   ->  Parallel Seq Scan on customers (actual time=8.234..38.456 rows=0 loops=3)
         Filter: ((ca_number)::text = '020000123456'::text)
         Rows Removed by Filter: 66666
 Execution Time: 45.789 ms
```

> ⚠️ `Filter: ((ca_number)::text = '020000123456'::text)` = คอลัมน์ `char(12)` ถูกแปลงเป็น text ทุกแถว

```sql
DEALLOCATE find_by_ca;
```

### 10.4 ชนิดข้อมูลไม่ตรง — วิธีแก้

```sql
PREPARE find_by_ca_fixed(text) AS
    SELECT customer_id, ca_number, first_name, last_name FROM gridcare.customers WHERE ca_number = $1::bpchar;
EXPLAIN (ANALYZE, BUFFERS) EXECUTE find_by_ca_fixed('020000123456');
```

ผลลัพธ์:
```text
 Index Scan using customers_ca_number_key on customers
   (cost=0.42..8.44 rows=1 width=42) (actual time=0.045..0.046 rows=1 loops=1)
   Index Cond: ((ca_number)::bpchar = '020000123456'::bpchar)
 Execution Time: 0.067 ms
```

> ✅ **45.789 ms → 0.067 ms**

```sql
DEALLOCATE find_by_ca_fixed;
```

### 10.5 Expression Index

ถ้าจำเป็นต้องใช้ `::date` จริง:

```sql
CREATE INDEX payments_paid_at_date_idx ON gridcare.payments ((paid_at::date));
```

> 💡 ใช้เมื่อ Query ใช้ `paid_at::date` เสมอ

### 10.6 ตาราง Anti-pattern

| Anti-pattern | วิธีแก้ |
|---|---|
| `WHERE f(col) = v` | เปลี่ยนเป็น `WHERE col >= v AND col < v + 1` |
| `WHERE col::text = $1` | `WHERE col = $1::bpchar` |
| `WHERE col::date = today` | `WHERE col >= today AND col < today + 1` |
| `WHERE lower(email) = $1` | Expression Index `lower(email)` |
| `WHERE col = $1` ชนิดไม่ตรง | Cast Parameter |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Before/After ฟังก์ชันครอบ

**ก่อน:**
```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT count(*) FROM gridcare.payments WHERE paid_at::date = current_date - 1;
```

ผลลัพธ์:
```text
 Aggregate  (cost=15432.00..15432.01 rows=1 width=8) (actual time=66.123..66.124 rows=1 loops=1)
   ->  Seq Scan on payments (actual time=0.012..65.234 rows=450000)
         Filter: ((paid_at)::date = (CURRENT_DATE - 1))
         Rows Removed by Filter: 435000
 Execution Time: 66.456 ms
```

**หลัง:**
```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT count(*) FROM gridcare.payments
WHERE paid_at >= current_date - 1 AND paid_at < current_date;
```

ผลลัพธ์:
```text
 Aggregate  (cost=1234.56..1234.57 rows=1 width=8) (actual time=3.456..3.457 rows=1 loops=1)
   ->  Index Only Scan using payments_paid_at_idx on payments (actual time=0.045..2.345 rows=15000)
         Index Cond: ((paid_at >= (CURRENT_DATE - 1)) AND (paid_at < CURRENT_DATE))
 Execution Time: 3.789 ms
```

### ตัวอย่างที่ 2: Expression Index

```sql
CREATE INDEX CONCURRENTLY customers_email_lower_idx ON gridcare.customers (lower(email));

EXPLAIN (ANALYZE, BUFFERS)
SELECT customer_id FROM gridcare.customers WHERE lower(email) = 'foo@example.com';
```

ผลลัพธ์:
```text
 Index Scan using customers_email_lower_idx on customers (actual time=0.045..0.046 rows=1)
   Index Cond: (lower(email) = 'foo@example.com'::text)
 Execution Time: 0.067 ms
```

### ตัวอย่างที่ 3: ตรวจชนิดข้อมูล

```sql
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns
WHERE table_schema = 'gridcare' AND table_name = 'customers' AND column_name = 'ca_number';
```

ผลลัพธ์:
```text
 column_name |   data_type   | character_maximum_length 
-------------+---------------+--------------------------
 ca_number   | character     |                       12
```

> ✅ รู้ว่าเป็น `character(12)` จึงต้อง Cast Parameter เป็น `bpchar`

## 12. สรุปย่อ จำง่าย
- **`WHERE f(col) = v` ทำให้ Index ไม่ถูกใช้**  
- **แก้ด้วย `WHERE col >= v AND col < v + 1`**  
- **Cast Parameter ไม่ใช่ Column**  
- **`char(n)` ต้อง Cast เป็น `bpchar`**  
- **Expression Index ใช้เมื่อจำเป็น**  
- **ตรวจชนิดข้อมูลก่อนเขียน Query**

ประโยคจำ: **“อย่าให้ฟังก์ชันครอบคอลัมน์ ทำให้ Index ไร้ค่า”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — Indexes on Expressions: https://www.postgresql.org/docs/17/indexes-expressional.html
- PostgreSQL Documentation — Type Conversion: https://www.postgresql.org/docs/17/typeconv.html
- GridCare Workshop Day 2: Workshop Day 2 ขั้นที่ 1 (Q4a, Q4b)

---

# บทที่ 37 VACUUM และ Bloat

## 1. เรื่อง
VACUUM, Bloat และวิธีจัดการ Dead Tuple ใน PostgreSQL

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจว่า VACUUM ทำอะไร  
2. เพื่อให้ตรวจสอบ Dead Tuple และ Bloat  
3. เพื่อให้หา Transaction ที่ขวาง VACUUM  
4. เพื่อให้ตั้ง Autovacuum ให้เหมาะ

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- อธิบายความแตกต่างของ VACUUM และ VACUUM FULL  
- ตรวจ `n_dead_tup` และ `n_live_tup`  
- หา Transaction ที่ขวาง VACUUM  
- ตั้ง Autovacuum รายตาราง  
- ใช้ `pg_stat_progress_vacuum`

## 4. เนื้อหาโดยย่อ
**VACUUM** — ลบ Dead Tuple และคืนพื้นที่ให้ใช้ซ้ำ แต่ไม่คืน Disk  
**VACUUM FULL** — คืน Disk แต่ Lock ทั้งตาราง (ไม่แนะนำบน Production)  
**pg_repack** — คืน Disk โดยไม่ Lock นาน (บทที่ 38)  
**Bloat** — พื้นที่ที่ใช้เกินความจำเป็น เพราะ Dead Tuple ไม่ถูก Vacuum

Autovacuum ทำงานเมื่อ:
- `n_dead_tup > autovacuum_vacuum_threshold + autovacuum_vacuum_scale_factor × n_live_tup`

## 5. ประโยชน์ที่ได้รับ
- ลด Bloat  
- ลด Disk  
- ทำให้ Query เร็ว  
- ป้องกัน XID Wraparound

## 6. ข้อควรระวัง
- **VACUUM FULL Lock ทั้งตาราง**  
- **Transaction ค้างทำให้ VACUUM ไม่ได้**  
- **`oldest xmin`** คือตัวกำหนดว่าแถวใดลบได้  
- **Autovacuum ที่ตัวแม่ของ Partition ไม่ทำงาน**  
- **Long Running Transaction ทำให้ Bloat**

## 7. ข้อดี
- VACUUM ไม่ Lock ตาราง  
- Autovacuum ทำงานอัตโนมัติ  
- ตรวจสอบได้ด้วย View  
- ลด Bloat ได้

## 8. ข้อเสีย
- VACUUM ไม่คืน Disk  
- VACUUM FULL Lock  
- Autovacuum อาจทำงานไม่ทัน

## 9. ข้อห้าม
- ห้าม `VACUUM FULL` บน Production ที่ต้องการ Availability  
- ห้ามปิด Autovacuum  
- ห้าม Transaction ค้างนาน  
- ห้ามใช้ `VACUUM FULL` แทน `pg_repack`  
- ห้ามลบ Dead Tuple ด้วยมือ

## 10. รายละเอียด

### 10.1 VACUUM vs VACUUM FULL

| มิติ | VACUUM | VACUUM FULL |
|---|---|---|
| ลบ Dead Tuple | ✅ | ✅ |
| คืน Disk | ❌ | ✅ |
| Lock | ❌ | ✅ AccessExclusiveLock |
| แนะนำ Production | ✅ | ❌ (ใช้ pg_repack) |

### 10.2 ตรวจสอบ Dead Tuple

```sql
SELECT relname, n_live_tup, n_dead_tup,
       round(100.0 * n_dead_tup / nullif(n_live_tup + n_dead_tup, 0), 1) AS dead_pct,
       last_autovacuum, last_autoanalyze, autovacuum_count
FROM pg_stat_user_tables
WHERE schemaname = 'gridcare'
ORDER BY n_dead_tup DESC LIMIT 5;
```

ผลลัพธ์:
```text
     relname     | n_live_tup | n_dead_tup | dead_pct |     last_autovacuum     | autovacuum_count 
-----------------+------------+------------+----------+--------------------------+------------------
 bills           |    1200000 |      12000 |      1.0 | 2026-11-03 09:45:12+07 |                3
 payments        |     450000 |       4500 |      1.0 | 2026-11-03 09:40:10+07 |                2
 meter_readings  |    7200000 |          0 |      0.0 | 2026-11-03 09:30:00+07 |                1
```

### 10.3 VACUUM VERBOSE

```sql
VACUUM (VERBOSE) gridcare.bills_bloat_demo;
```

ผลลัพธ์:
```text
INFO:  vacuuming "gridcare.bills_bloat_demo"
INFO:  scanned index "bills_bloat_demo_pkey" to remove 200000 row versions
DETAIL:  CPU: 45.23 ms, elapsed: 234.56 ms
INFO:  "bills_bloat_demo": removed 0 row versions in 1234 pages
DETAIL:  CPU: 12.34 ms, elapsed: 45.67 ms
INFO:  "bills_bloat_demo": found 0 removable, 400000 nonremovable row versions in 3072 pages
DETAIL:  200000 dead row versions cannot be removed yet, oldest xmin: 1234567
```

> ⚠️ `200000 dead row versions cannot be removed yet` = มี Transaction ค้าง

### 10.4 หา Transaction ที่ขวาง VACUUM

```sql
SELECT 'session' AS kind, pid::text AS who, state, age(backend_xmin) AS xmin_age,
       now() - xact_start AS xact_age
FROM pg_stat_activity WHERE backend_xmin IS NOT NULL
UNION ALL
SELECT 'slot', slot_name, active::text, age(xmin), NULL
FROM pg_replication_slots WHERE xmin IS NOT NULL
UNION ALL
SELECT 'prepared', gid, NULL, age(transaction), now() - prepared
FROM pg_prepared_xacts
ORDER BY xmin_age DESC NULLS LAST
LIMIT 5;
```

ผลลัพธ์:
```text
  kind   |  who  |        state        | xmin_age |  xact_age    
---------+-------+---------------------+----------+--------------
 session | 12345 | idle in transaction |       85 | 00:01:25
```

> ✅ Session ที่ค้าง = ตัวขวาง VACUUM

### 10.5 VACUUM หลังปิด Transaction

```sql
VACUUM (VERBOSE) gridcare.bills_bloat_demo;
```

ผลลัพธ์:
```text
INFO:  "bills_bloat_demo": removed 200000 row versions in 1536 pages
DETAIL:  CPU: 123.45 ms, elapsed: 456.78 ms
INFO:  "bills_bloat_demo": found 200000 removable, 200000 nonremovable row versions in 3072 pages
```

> ✅ ลบได้ 200,000 Dead Tuple แต่ขนาดไฟล์ยังเท่าเดิม (เพราะ VACUUM ไม่คืน Disk)

### 10.6 pg_stat_progress_vacuum

```sql
SELECT pid, relid::regclass, phase, heap_blks_scanned, heap_blks_total
FROM pg_stat_progress_vacuum;
```

ผลลัพธ์ (ถ้ามี VACUUM ทำงาน):
```text
 pid | relid | phase | heap_blks_scanned | heap_blks_total 
-----+-------+-------+-------------------+-----------------
(0 rows)
```

### 10.7 ตั้ง Autovacuum รายตาราง

```sql
ALTER TABLE gridcare.bills SET (
  autovacuum_vacuum_scale_factor = 0.02,
  autovacuum_analyze_scale_factor = 0.02
);
SELECT relname, reloptions FROM pg_class WHERE relname = 'bills';
```

ผลลัพธ์:
```text
 relname |                                       reloptions                                        
---------+---------------------------------------------------------------------------------------
 bills   | {autovacuum_vacuum_scale_factor=0.02,autovacuum_analyze_scale_factor=0.02}
```

### 10.8 Autovacuum Global Parameter

```ini
autovacuum_max_workers = 3
autovacuum_vacuum_cost_limit = 1000
autovacuum_naptime = '30s'
```

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: ตรวจสอบ Bloat ด้วย Query

```sql
SELECT schemaname, relname,
       pg_size_pretty(pg_total_relation_size(relid)) AS total_size,
       n_live_tup, n_dead_tup,
       round(100.0 * n_dead_tup / nullif(n_live_tup + n_dead_tup, 0), 1) AS dead_pct
FROM pg_stat_user_tables
WHERE schemaname = 'gridcare' AND n_dead_tup > 1000
ORDER BY pg_total_relation_size(relid) DESC
LIMIT 10;
```

ผลลัพธ์:
```text
 schemaname |  relname  | total_size | n_live_tup | n_dead_tup | dead_pct 
------------+-----------+------------+------------+------------+----------
 gridcare   | bills     | 320 MB     |    1200000 |      12000 |      1.0
 gridcare   | payments  | 180 MB     |     450000 |       4500 |      1.0
```

### ตัวอย่างที่ 2: หา Transaction ค้าง

```sql
SELECT pid, state, age(backend_xmin) AS xmin_age, now() - xact_start AS xact_age,
       left(query, 60)
FROM pg_stat_activity
WHERE backend_xmin IS NOT NULL
ORDER BY xmin_age DESC;
```

ผลลัพธ์:
```text
  pid  |        state        | xmin_age |  xact_age  |                        left                        
-------+---------------------+----------+------------+----------------------------------------------------
 12345 | idle in transaction |       85 | 00:01:25   | SELECT count(*) FROM gridcare.regions;
```

### ตัวอย่างที่ 3: ปิด Transaction แล้ว VACUUM

```sql
-- หน้าต่าง 2
ROLLBACK;
```

```sql
-- หน้าต่าง 1
VACUUM (VERBOSE) gridcare.bills_bloat_demo;
```

ผลลัพธ์:
```text
INFO:  "bills_bloat_demo": removed 200000 row versions in 1536 pages
```

## 12. สรุปย่อ จำง่าย
- **VACUUM = ลบ Dead Tuple ไม่คืน Disk**  
- **VACUUM FULL = คืน Disk แต่ Lock**  
- **pg_repack = คืน Disk ไม่ Lock นาน**  
- **Transaction ค้างขวาง VACUUM**  
- **Autovacuum ตั้งรายตารางได้**  
- **ตรวจ `n_dead_tup` และ `pg_stat_progress_vacuum`**

ประโยคจำ: **“VACUUM ไม่คืน Disk แต่คืนพื้นที่ให้ใช้ซ้ำ”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — VACUUM: https://www.postgresql.org/docs/17/sql-vacuum.html
- PostgreSQL Documentation — Routine Vacuuming: https://www.postgresql.org/docs/17/routine-vacuuming.html
- GridCare Workshop Day 2: Lab 4.1

---

# บทที่ 38 pg_repack

## 1. เรื่อง
`pg_repack` Extension สำหรับจัดการ Bloat โดยไม่ Lock ตารางนาน

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจว่า `pg_repack` ทำงานอย่างไร  
2. เพื่อให้ติดตั้งและใช้งานได้  
3. เพื่อให้เปรียบเทียบกับ `VACUUM FULL`  
4. เพื่อให้วางแผนใช้ใน Production

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ติดตั้ง `pg_repack`  
- รัน `pg_repack -t schema.table`  
- เปรียบเทียบขนาดก่อน/หลัง  
- วางแผนใช้ในช่วง Maintenance Window

## 4. เนื้อหาโดยย่อ
`pg_repack` ทำงานโดย:
1. สร้าง Table ใหม่  
2. คัดลอกข้อมูล  
3. สร้าง Index ใหม่  
4. สลับชื่อ Table  
5. ลบ Table เก่า

ข้อดี: ไม่ Lock นานเหมือน `VACUUM FULL`  
ข้อจำกัด: ต้องมี PK หรือ Unique NOT NULL  
ต้องใช้ Disk เพิ่มชั่วคราว

## 5. ประโยชน์ที่ได้รับ
- คืน Disk โดยไม่หยุดระบบ  
- ลด Bloat  
- Query เร็วขึ้น  
- ปลอดภัยกว่า `VACUUM FULL`

## 6. ข้อควรระวัง
- **ต้องมี PK หรือ Unique NOT NULL**  
- **ต้องมี Disk เพิ่มชั่วคราว**  
- **ต้องมี Extension `pg_repack`**  
- **ต้องไม่มีการเขียนที่ Table ระหว่างดำเนินการ** (แต่ `pg_repack` จัดการให้)  
- **ใช้เวลานานสำหรับ Table ใหญ่**

## 7. ข้อดี
- ไม่ Lock นาน  
- คืน Disk  
- ปลอดภัยกว่า `VACUUM FULL`  
- รองรับ `CONCURRENTLY`

## 8. ข้อเสีย
- ต้องมี PK  
- ใช้ Disk เพิ่ม  
- ใช้เวลานาน

## 9. ข้อห้าม
- ห้าม `pg_repack` บน Table ที่ไม่มี PK  
- ห้ามรันในช่วง Peak Hours  
- ห้ามรันโดยไม่ตรวจ Disk  
- ห้ามรันโดยไม่มี Backup  
- ห้ามรันบน Table ที่มี Long Running Transaction

## 10. รายละเอียด

### 10.1 ติดตั้ง

```bash
sudo apt install -y postgresql-17-repack
```

ผลลัพธ์:
```text
Reading package lists... Done
Setting up postgresql-17-repack (1.5.3-1.pgdg24.04+1) ...
```

### 10.2 สร้าง Extension

```sql
CREATE EXTENSION IF NOT EXISTS pg_repack;
```

ผลลัพธ์:
```text
CREATE EXTENSION
```

### 10.3 สาธิต Bloat

```sql
CREATE TABLE gridcare.bills_bloat_demo AS
SELECT * FROM gridcare.bills WHERE bill_id <= 200000;
ALTER TABLE gridcare.bills_bloat_demo ADD PRIMARY KEY (bill_id);
ALTER TABLE gridcare.bills_bloat_demo SET (autovacuum_enabled = off);
SELECT pg_size_pretty(pg_table_size('gridcare.bills_bloat_demo')) AS size_before;
```

ผลลัพธ์:
```text
 size_before 
-------------
 24 MB
```

### 10.4 UPDATE ทุกแถว + VACUUM

```sql
UPDATE gridcare.bills_bloat_demo SET units_kwh = units_kwh;
VACUUM (VERBOSE) gridcare.bills_bloat_demo;
SELECT pg_size_pretty(pg_table_size('gridcare.bills_bloat_demo')) AS after_vacuum;
```

ผลลัพธ์:
```text
INFO:  "bills_bloat_demo": removed 200000 row versions in 1536 pages
 after_vacuum 
--------------
 48 MB
```

> ⚠️ VACUUM ลบ Dead Tuple แล้ว แต่ขนาดไฟล์ยัง 48 MB

### 10.5 รัน pg_repack

```bash
sudo -u postgres pg_repack -d gridcare -t gridcare.bills_bloat_demo
```

ผลลัพธ์:
```text
INFO: repacking table "gridcare.bills_bloat_demo"
```

### 10.6 ตรวจสอบผล

```bash
sudo -u postgres psql -X -d gridcare -c "SELECT pg_size_pretty(pg_table_size('gridcare.bills_bloat_demo')) AS after_repack"
```

ผลลัพธ์:
```text
 after_repack 
--------------
 24 MB
```

> ✅ **48 MB → 24 MB** (~50%)

### 10.7 ตารางเปรียบเทียบ

| วิธี | Lock | คืน Disk | ต้องมี PK | ใช้ Disk เพิ่ม |
|---|---|---|---|---|
| VACUUM | ❌ | ❌ | ❌ | ❌ |
| VACUUM FULL | ✅ AccessExclusive | ✅ | ❌ | ✅ |
| pg_repack | ⚠️ สั้น | ✅ | ✅ | ✅ |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: pg_repack Table เดียว

```bash
sudo -u postgres pg_repack -d gridcare -t gridcare.bills
```

ผลลัพธ์:
```text
INFO: repacking table "gridcare.bills"
```

### ตัวอย่างที่ 2: pg_repack พร้อม Index

```bash
sudo -u postgres pg_repack -d gridcare -t gridcare.bills --wait-timeout=60
```

### ตัวอย่างที่ 3: ตรวจ Disk ก่อน

```bash
df -h /var/lib/postgresql
```

ผลลัพธ์:
```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        78G   18G   57G  24% /
```

> ✅ ต้องมี Disk ว่าง > ขนาด Table × 1.5

### ตัวอย่างที่ 4: ตรวจสอบหลัง pg_repack

```sql
SELECT relname, pg_size_pretty(pg_table_size(oid)) AS size
FROM pg_class WHERE relname = 'bills_bloat_demo';
```

ผลลัพธ์:
```text
     relname      |  size  
------------------+--------
 bills_bloat_demo | 24 MB
```

### ตัวอย่างที่ 5: ลบ Table สาธิต

```sql
DROP TABLE gridcare.bills_bloat_demo;
```

## 12. สรุปย่อ จำง่าย
- **pg_repack = คืน Disk ไม่ Lock นาน**  
- **ต้องมี PK หรือ Unique NOT NULL**  
- **ต้องมี Disk เพิ่ม**  
- **ใช้เวลานานสำหรับ Table ใหญ่**  
- **ปลอดภัยกว่า VACUUM FULL**  
- **ตรวจ Disk ก่อนรัน**

ประโยคจำ: **“pg_repack คืน Disk ให้ โดยไม่หยุดระบบ”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- pg_repack: https://reorg.github.io/pg_repack/
- PostgreSQL Documentation — VACUUM FULL: https://www.postgresql.org/docs/17/sql-vacuum.html
- GridCare Workshop Day 2: Lab 4.1

---

# บทที่ 39 XID Wraparound

## 1. เรื่อง
Transaction ID (XID) Wraparound ปัญหาที่เกิดเมื่อ XID วนกลับ และวิธีป้องกัน

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจว่า XID Wraparound คืออะไร  
2. เพื่อให้ตรวจสอบอายุ XID  
3. เพื่อให้ป้องกันด้วย VACUUM  
4. เพื่อให้ตั้ง Alert สำหรับ XID Age

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- อธิบาย XID Wraparound  
- ตรวจ `age(datfrozenxid)`  
- ตั้ง Alert `PostgresXidAgeWarning`  
- วางแผน VACUUM เพื่อลด XID Age

## 4. เนื้อหาโดยย่อ
PostgreSQL ใช้ Transaction ID ขนาด 32-bit  
เมื่อ XID เกิน 2,147,483,647 จะเกิด Wraparound  
PostgreSQL จะหยุดรับ write เมื่อ XID Age เข้าใกล้ 2,000,000,000

การป้องกัน:
- Autovacuum ทำงานสม่ำเสมอ  
- ตั้ง Alert ที่ 1,000,000,000 และ 1,500,000,000  
- ตรวจ `age(datfrozenxid)` เป็นประจำ

## 5. ประโยชน์ที่ได้รับ
- ป้องกันระบบหยุด  
- ตรวจพบก่อนเกิดปัญหา  
- วางแผน VACUUM ได้

## 6. ข้อควรระวัง
- **`age(datfrozenxid)` เพิ่มขึ้นทุกวัน**  
- **Autovacuum ต้องทำงาน**  
- **Transaction ค้างทำให้ VACUUM ไม่ได้**  
- **Replication Slot ที่ไม่ใช้ทำให้ XID ค้าง**  
- **Prepared Transaction ค้างทำให้ XID ค้าง**

## 7. ข้อดี
- ป้องกันได้ด้วย Autovacuum  
- ตรวจสอบได้ด้วย SQL  
- Alert ได้

## 8. ข้อเสีย
- ถ้าพลาด ระบบหยุด ต้อง Downtime

## 9. ข้อห้าม
- ห้ามปิด Autovacuum  
- ห้ามปล่อย Transaction ค้าง  
- ห้ามปล่อย Replication Slot ที่ไม่ใช้  
- ห้ามลืม Prepared Transaction  
- ห้ามรอจนใกล้ 2,000,000,000

## 10. รายละเอียด

### 10.1 ตรวจสอบ XID Age ระดับ Database

```sql
SELECT datname, age(datfrozenxid) AS xid_age,
       round(100.0 * age(datfrozenxid) / 2147483647, 2) AS pct_of_wraparound
FROM pg_database ORDER BY 2 DESC;
```

ผลลัพธ์:
```text
  datname   | xid_age | pct_of_wraparound 
------------+---------+-------------------
 gridcare   |  152345 |              0.01
 postgres   |   45012 |              0.00
 template1  |   45012 |              0.00
```

### 10.2 ตรวจสอบ XID Age ระดับ Table

```sql
SELECT c.oid::regclass AS table_name, age(c.relfrozenxid) AS xid_age,
       pg_size_pretty(pg_total_relation_size(c.oid)) AS size
FROM pg_class AS c JOIN pg_namespace AS n ON n.oid = c.relnamespace
WHERE n.nspname = 'gridcare' AND c.relkind = 'r'
ORDER BY age(c.relfrozenxid) DESC LIMIT 5;
```

ผลลัพธ์:
```text
         table_name          | xid_age |  size    
-----------------------------+---------+----------
 gridcare.meter_readings     |  152345 | 1250 MB
 gridcare.bills              |  150234 | 320 MB
 gridcare.payments           |  148901 | 180 MB
 gridcare.customers          |  145678 | 45 MB
 gridcare.regions            |   45012 | 8 kB
```

### 10.3 Alert Rule

```yaml
- alert: PostgresXidAgeWarning
  expr: pg_database_wraparound_age_datfrozenxid_seconds > 1e9
  for: 1h
  labels:
    severity: warning
    owner: dba
  annotations:
    summary: "XID Age {{ $value }} ใน {{ $labels.datname }}"
    description: "Autovacuum ไม่ทำงาน หรือมี Transaction ค้าง"
    runbook_url: "http://gridcare-infra/runbooks/C05-bloat-vacuum-wraparound.md"

- alert: PostgresXidAgeCritical
  expr: pg_database_wraparound_age_datfrozenxid_seconds > 1.5e9
  for: 5m
  labels:
    severity: critical
    owner: dba
  annotations:
    summary: "XID Age {{ $value }} ใกล้ Wraparound"
    description: "ต้อง VACUUM ทันที"
    runbook_url: "http://gridcare-infra/runbooks/C05-bloat-vacuum-wraparound.md"
```

### 10.4 ตรวจสอบว่า VACUUM ทำงาน

```sql
SELECT datname, age(datfrozenxid) AS before_vacuum
FROM pg_database WHERE datname = 'gridcare';
```

ผลลัพธ์:
```text
  datname  | before_vacuum 
-----------+---------------
 gridcare  |        152345
```

```sql
VACUUM (VERBOSE) gridcare.customers;
```

ผลลัพธ์:
```text
INFO:  vacuuming "gridcare.customers"
INFO:  "customers": found 0 removable, 200000 nonremovable row versions in 4096 pages
INFO:  "customers": suspending truncate due to conflicting lock request
```

### 10.5 หา Transaction ที่ทำให้ XID ค้าง

```sql
SELECT 'session' AS kind, pid::text AS who, state, age(backend_xmin) AS xmin_age
FROM pg_stat_activity WHERE backend_xmin IS NOT NULL
UNION ALL
SELECT 'slot', slot_name, active::text, age(xmin)
FROM pg_replication_slots WHERE xmin IS NOT NULL
UNION ALL
SELECT 'prepared', gid, NULL, age(transaction)
FROM pg_prepared_xacts
ORDER BY xmin_age DESC NULLS LAST
LIMIT 5;
```

### 10.6 ตารางระดับ XID Age

| XID Age | สถานะ | การกระทำ |
|---|---|---|
| < 500M | ปกติ | ไม่ทำอะไร |
| 500M–1B | Warning | ตรวจ Autovacuum |
| 1B–1.5B | Warning | VACUUM ทันที |
| 1.5B–1.8B | Critical | VACUUM แบบ Manual |
| 1.8B–2B | Critical | หยุดแอป VACUUM |
| > 2B | ระบบหยุด | Emergency |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: ตรวจสอบ

```sql
SELECT datname, age(datfrozenxid) AS xid_age,
       round(100.0 * age(datfrozenxid) / 2147483647, 2) AS pct
FROM pg_database ORDER BY 2 DESC;
```

ผลลัพธ์:
```text
  datname   | xid_age | pct  
------------+---------+------
 gridcare   |  152345 | 0.01
 postgres   |   45012 | 0.00
 template1  |   45012 | 0.00
```

### ตัวอย่างที่ 2: Alert ที่ Firing

```bash
curl -s localhost:9090/api/v1/alerts | python3 -m json.tool | grep -E '"alertname"|"state"'
```

ผลลัพธ์ (ถ้าเกิน 1B):
```text
"alertname": "PostgresXidAgeWarning",
"state": "firing"
```

### ตัวอย่างที่ 3: ดู Metric ใน Prometheus

```promql
pg_database_wraparound_age_datfrozenxid_seconds{datname="gridcare"}
```

ผลลัพธ์:
```text
{datname="gridcare"} 152345
```

## 12. สรุปย่อ จำง่าย
- **XID Wraparound = ระบบหยุด**  
- **ตรวจด้วย `age(datfrozenxid)`**  
- **Alert ที่ 1B (warning) และ 1.5B (critical)**  
- **Autovacuum ต้องทำงาน**  
- **Transaction ค้างทำให้ XID ค้าง**  
- **Prepared Transaction และ Replication Slot ที่ไม่ใช้ก็ทำให้ค้าง**

ประโยคจำ: **“XID Wraparound คือศัตรูที่มองไม่เห็น แต่หยุดระบบได้”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — Routine Vacuuming (Preventing Transaction ID Wraparound Failures): https://www.postgresql.org/docs/17/routine-vacuuming.html#VACUUM-FOR-WRAPAROUND
- PostgreSQL Documentation — pg_database: https://www.postgresql.org/docs/17/view-pg-database.html
- GridCare Workshop Day 2: Lab 4.2

---

# บทที่ 40 Autovacuum รายตารางและ Partition

## 1. เรื่อง
การตั้ง Autovacuum รายตารางและสำหรับ Partitioned Table อย่างถูกต้อง

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจ Autovacuum Threshold และ Scale Factor  
2. เพื่อให้ตั้ง Autovacuum รายตาราง  
3. เพื่อให้ตั้ง Autovacuum สำหรับ Partitioned Table  
4. เพื่อให้ตรวจสอบ Autovacuum ที่ทำงาน

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- อธิบายสูตร Autovacuum Trigger  
- ตั้ง `autovacuum_vacuum_scale_factor` รายตาราง  
- ตั้งที่ Template Table ของ pg_partman  
- ตั้งที่ Partition ที่มีอยู่  
- ตรวจสอบด้วย `pg_stat_user_tables` และ `pg_stat_progress_vacuum`

## 4. เนื้อหาโดยย่อ
Autovacuum ทำงานเมื่อ:
```
n_dead_tup > autovacuum_vacuum_threshold + autovacuum_vacuum_scale_factor × n_live_tup
```

ค่าเริ่มต้น:
- `autovacuum_vacuum_threshold = 50`  
- `autovacuum_vacuum_scale_factor = 0.2` (20%)  
- `autovacuum_analyze_threshold = 50`  
- `autovacuum_analyze_scale_factor = 0.1` (10%)

สำหรับ Table ใหญ่ 20% ทำให้ Autovacuum ไม่ทัน → ตั้ง `scale_factor` ต่ำลง

สำหรับ Partitioned Table:
- ตั้งที่ตัวแม่ไม่ได้  
- ตั้งที่ Template Table (pg_partman)  
- ตั้งที่ Partition ที่มีอยู่

## 5. ประโยชน์ที่ได้รับ
- Autovacuum ทำงานทัน  
- ลด Bloat  
- ป้องกัน XID Wraparound  
- ลด Performance Impact

## 6. ข้อควรระวัง
- **ตั้งที่ตัวแม่ของ Partitioned ไม่ได้**  
- **Autovacuum Analyze ที่ตัวแม่ไม่ทำงาน**  
- **Partition ใหม่จะไม่ได้ค่าจาก Template ถ้าไม่ได้ตั้ง**  
- **`scale_factor` ต่ำเกินไปทำให้ Autovacuum ถี่เกิน**  
- **ต้องมี `autovacuum_max_workers` เพียงพอ**

## 7. ข้อดี
- Autovacuum ทำงานเหมาะกับขนาดตาราง  
- ลด Bloat  
- ลด XID Age  
- ควบคุมได้ด้วย `scale_factor`

## 8. ข้อเสีย
- ต้องตั้งรายตาราง  
- ต้องตั้งซ้ำทุก Partition  
- ต้องตรวจเป็นระยะ

## 9. ข้อห้าม
- ห้ามตั้ง Autovacuum ที่ตัวแม่ของ Partitioned  
- ห้ามปิด Autovacuum ที่ Table ใหญ่  
- ห้ามตั้ง `scale_factor = 0` โดยไม่มีเหตุ  
- ห้ามลืมตั้งที่ Partition ใหม่  
- ห้ามลืม `ANALYZE` หลังสร้าง Partition

## 10. รายละเอียด

### 10.1 สูตร Autovacuum

```
Vacuum Trigger = threshold + scale_factor × n_live_tup
```

ตัวอย่าง: `n_live_tup = 1,200,000`, threshold = 50, scale_factor = 0.2  
→ Trigger = 50 + 0.2 × 1,200,000 = 240,050 Dead Tuple

ถ้าตั้ง `scale_factor = 0.02`  
→ Trigger = 50 + 0.02 × 1,200,000 = 24,050 Dead Tuple → เร็วขึ้น 10 เท่า

### 10.2 ตั้ง Autovacuum รายตาราง

```sql
ALTER TABLE gridcare.bills SET (
  autovacuum_vacuum_scale_factor = 0.02,
  autovacuum_analyze_scale_factor = 0.02,
  autovacuum_vacuum_insert_scale_factor = 0.05,
  autovacuum_vacuum_insert_threshold = 10000
);
```

### 10.3 ตั้งที่ Partition ตัวแม่ (ทำไม่ได้)

```sql
ALTER TABLE gridcare.meter_readings SET (autovacuum_vacuum_insert_scale_factor = 0.05);
```

ผลลัพธ์:
```text
ERROR:  cannot specify storage parameters for a partitioned table
HINT:  Specify storage parameters for its leaf partitions instead.
```

### 10.4 ตั้งที่ Template Table ของ pg_partman

```sql
SELECT template_table
FROM partman.part_config
WHERE parent_table = 'gridcare.meter_readings';
```

ผลลัพธ์:
```text
              template_table               
-------------------------------------------
 partman.template_gridcare_meter_readings
```

```sql
ALTER TABLE partman.template_gridcare_meter_readings
  SET (autovacuum_vacuum_insert_scale_factor = 0.05,
       autovacuum_vacuum_insert_threshold = 10000);
```

ผลลัพธ์:
```text
ALTER TABLE
```

### 10.5 ตั้งที่ Partition ที่มีอยู่ทุกตัว

```sql
SELECT format('ALTER TABLE %s SET (autovacuum_vacuum_insert_scale_factor = 0.05, autovacuum_vacuum_insert_threshold = 10000)',
              i.inhrelid::regclass)
FROM pg_inherits AS i
WHERE i.inhparent = 'gridcare.meter_readings'::regclass
\gexec
```

ผลลัพธ์:
```text
ALTER TABLE
ALTER TABLE
... (23 บรรทัด)
```

### 10.6 ตรวจสอบว่า Partition ได้รับค่า

```sql
SELECT c.relname, c.reloptions
FROM pg_class AS c
JOIN pg_inherits AS i ON i.inhrelid = c.oid
WHERE i.inhparent = 'gridcare.meter_readings'::regclass
ORDER BY 1 DESC LIMIT 3;
```

ผลลัพธ์:
```text
           relname            |                                       reloptions                                        
------------------------------+---------------------------------------------------------------------------------------
 meter_readings_p20261105     | {autovacuum_vacuum_insert_scale_factor=0.05,autovacuum_vacuum_insert_threshold=10000}
 meter_readings_p20261104     | {autovacuum_vacuum_insert_scale_factor=0.05,autovacuum_vacuum_insert_threshold=10000}
 meter_readings_p20261103     | {autovacuum_vacuum_insert_scale_factor=0.05,autovacuum_vacuum_insert_threshold=10000}
```

### 10.7 ตรวจสอบ Autovacuum ที่ทำงาน

```sql
SELECT pid, relid::regclass, phase, heap_blks_scanned, heap_blks_total
FROM pg_stat_progress_vacuum;
```

ผลลัพธ์ (ถ้ามี VACUUM ทำงาน):
```text
 pid | relid | phase | heap_blks_scanned | heap_blks_total 
-----+-------+-------+-------------------+-----------------
(0 rows)
```

### 10.8 Global Parameter

```ini
autovacuum = on
autovacuum_max_workers = 3
autovacuum_naptime = '30s'
autovacuum_vacuum_cost_limit = 1000
autovacuum_vacuum_cost_delay = '2ms'
```

### 10.9 ตารางตั้ง Autovacuum

| ขนาด Table | `autovacuum_vacuum_scale_factor` | `autovacuum_analyze_scale_factor` |
|---|---|---|
| < 1M | 0.2 (default) | 0.1 (default) |
| 1M–10M | 0.05 | 0.05 |
| 10M–100M | 0.02 | 0.02 |
| > 100M | 0.01 | 0.01 |
| Partition รายวัน | 0.05 | 0.05 |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: ตั้ง Autovacuum ที่ Table ใหญ่

```sql
ALTER TABLE gridcare.bills SET (
  autovacuum_vacuum_scale_factor = 0.02,
  autovacuum_analyze_scale_factor = 0.02
);
SELECT relname, reloptions FROM pg_class WHERE relname = 'bills';
```

ผลลัพธ์:
```text
 relname |                                       reloptions                                        
---------+---------------------------------------------------------------------------------------
 bills   | {autovacuum_vacuum_scale_factor=0.02,autovacuum_analyze_scale_factor=0.02}
```

### ตัวอย่างที่ 2: ตั้งที่ Template

```sql
ALTER TABLE partman.template_gridcare_meter_readings
  SET (autovacuum_vacuum_insert_scale_factor = 0.05,
       autovacuum_vacuum_insert_threshold = 10000);
```

### ตัวอย่างที่ 3: ตั้งที่ Partition ที่มีอยู่

```sql
SELECT format('ALTER TABLE %s SET (autovacuum_vacuum_insert_scale_factor = 0.05, autovacuum_vacuum_insert_threshold = 10000)',
              i.inhrelid::regclass)
FROM pg_inherits AS i
WHERE i.inhparent = 'gridcare.meter_readings'::regclass
\gexec
```

### ตัวอย่างที่ 4: ตรวจสอบ Autovacuum ที่ทำงาน

```sql
SELECT pid, relid::regclass, phase, heap_blks_scanned, heap_blks_total
FROM pg_stat_progress_vacuum;
```

ผลลัพธ์ (ถ้ามี):
```text
  pid  |         relid          |     phase      | heap_blks_scanned | heap_blks_total 
-------+------------------------+----------------+-------------------+-----------------
 12345 | gridcare.bills         | vacuuming heap |             45000 |          100000
```

### ตัวอย่างที่ 5: ตรวจ `last_autovacuum`

```sql
SELECT relname, last_autovacuum, last_autoanalyze, autovacuum_count
FROM pg_stat_user_tables
WHERE schemaname = 'gridcare'
ORDER BY last_autovacuum DESC NULLS LAST
LIMIT 5;
```

ผลลัพธ์:
```text
     relname     |     last_autovacuum     |     last_autoanalyze    | autovacuum_count 
-----------------+-------------------------+--------------------------+------------------
 bills           | 2026-11-03 09:45:12+07 | 2026-11-03 09:45:15+07 |                3
 payments        | 2026-11-03 09:40:10+07 | 2026-11-03 09:40:12+07 |                2
 meter_readings  | 2026-11-03 09:30:00+07 | 2026-11-03 09:30:05+07 |                1
```

## 12. สรุปย่อ จำง่าย
- **Autovacuum Trigger = threshold + scale_factor × n_live_tup**  
- **Table ใหญ่ → `scale_factor` ต่ำ**  
- **Partitioned → ตั้งที่ Template + Partition ลูก**  
- **ตั้งที่ตัวแม่ไม่ได้**  
- **`autovacuum_max_workers` ต้องเพียงพอ**  
- **ตรวจด้วย `pg_stat_progress_vacuum` และ `pg_stat_user_tables`**

ประโยคจำ: **“Autovacuum ที่ดีคือ Autovacuum ที่ทำงานทันก่อน Bloat จะเกิด”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — Autovacuum: https://www.postgresql.org/docs/17/runtime-config-autovacuum.html
- PostgreSQL Documentation — Routine Vacuuming: https://www.postgresql.org/docs/17/routine-vacuuming.html
- pg_partman: https://github.com/pgpartman/pg_partman
- GridCare Workshop Day 2: Lab 4.2, Workshop Day 2 ขั้นที่ 3

---

## สรุปส่วนที่ 4 (บทที่ 31–40)

| บท | แก่นของบท | ใช้ต่อในส่วน |
|---|---|---|
| 31 | pg_stat_statements: ตั้งและ Query | Performance |
| 32 | หา Top Total Time และ Top Mean Time | Performance |
| 33 | Index Health: ซ้ำ ไม่ใช้ Invalid | Maintenance |
| 34 | N+1 และ Anti-pattern จาก ORM | Performance |
| 35 | Keyset Pagination | Performance |
| 36 | ฟังก์ชันครอบคอลัมน์และชนิดข้อมูล | Performance |
| 37 | VACUUM และ Bloat | Maintenance |
| 38 | pg_repack | Maintenance |
| 39 | XID Wraparound | Monitoring, Alert |
| 40 | Autovacuum รายตารางและ Partition | Maintenance |

---
 