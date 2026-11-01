# บทที่ 21–30

> หนังสือ: คู่มือการใช้งาน PostgreSQL สำหรับ DevOps Engineer, Cloud Engineer และ DBA  
> ส่วนที่ 3 SQL และการใช้งานประจำวัน  
> โทน: ทางการ กระชับ เน้นใช้งานจริง

---

# บทที่ 21 psql และ Meta-command ที่ต้องรู้

## 1. เรื่อง
การใช้งาน `psql` ซึ่งเป็น Client หลักของ PostgreSQL พร้อม Meta-command ที่ใช้บ่อยในงานประจำวัน

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้ผู้อ่านใช้ `psql` ได้อย่างมีประสิทธิภาพ  
2. เพื่อให้รู้จัก Meta-command สำคัญที่ลดเวลาในการทำงาน  
3. เพื่อให้ใช้ Variable, `\gset`, `\gexec` และ `\copy` ได้  
4. เพื่อให้ใช้ `psql` ใน Script และ Automation ได้

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- เข้า `psql` ด้วยวิธีต่าง ๆ ได้  
- ใช้ `\conninfo`, `\l`, `\du`, `\dn`, `\dx`, `\dt`, `\d`  
- ใช้ `\x`, `\timing`, `\watch`, `\e`, `\i`  
- ใช้ `\gset`, `\gexec` ในการ Automate  
- เขียน Script ที่ใช้ `psql -X -v ON_ERROR_STOP=1`

## 4. เนื้อหาโดยย่อ
`psql` เป็น Interactive Terminal สำหรับ PostgreSQL  
รองรับ:
- **SQL Statement** — ใช้ได้ตามปกติ  
- **Meta-command** — ขึ้นต้นด้วย `\` เช่น `\dt`, `\d`, `\l`  
- **Variable** — `:name` และ `:'name'`  
- **Output Format** — `\x`, `\pset`, `\copy`  
- **Input/Output** — `\i`, `\o`, `\e`  
- **Automation** — `\gset`, `\gexec`, `\if`

## 5. ประโยชน์ที่ได้รับ
- ลดเวลาการตรวจสอบฐานข้อมูล  
- เขียน Script ที่ปลอดภัยได้  
- ใช้ `\gexec` สร้างคำสั่งอัตโนมัติ  
- ใช้ `\copy` นำเข้า/ส่งออกข้อมูลได้  
- ใช้ `\watch` เฝ้าดู Metric แบบ Real-time

## 6. ข้อควรระวัง
- **`-X`** ควรใส่เสมอ เพื่อไม่ให้อ่าน `.psqlrc`  
- **`ON_ERROR_STOP`** ควรตั้งเพื่อให้ Script หยุดเมื่อเกิด Error  
- **`\gset`** เก็บค่าได้เฉพาะ Query ที่คืนค่า 1 แถว  
- **`\gexec`** รัน SQL ที่ได้จาก Query โดยตรง — ระวัง SQL Injection  
- **`\copy`** ทำงานฝั่ง Client ไม่ใช่ Server

## 7. ข้อดี
- เป็น Client มาตรฐานที่ติดมากับ PostgreSQL  
- Meta-command ครอบคลุมงานส่วนใหญ่  
- รองรับ Automation  
- ใช้ใน CI/CD และ Script ได้

## 8. ข้อเสีย
- Meta-command จำยากสำหรับผู้เริ่มต้น  
- Output Format ไม่สวยเท่า GUI  
- `\gexec` อันตรายถ้าใช้ไม่ระวัง

## 9. ข้อห้าม
- ห้ามใช้ `psql` แบบไม่ใส่ `-X` ใน Script  
- ห้ามใช้ `\gexec` กับข้อมูลที่มาจากผู้ใช้โดยไม่ Sanitize  
- ห้ามรัน `DROP` หรือ `TRUNCATE` โดยไม่มี `WHERE`/`LIMIT`  
- ห้ามใช้ Superuser ใน Script Production  
- ห้ามเปิด `.psqlrc` ที่มีคำสั่งอันตราย

## 10. รายละเอียด

### 10.1 การเข้า `psql`

```bash
# Local ด้วย Peer
sudo -u postgres psql

# ระบุ Database
sudo -u postgres psql -d gridcare

# ผ่าน TCP + SSL
psql "host=pg1 dbname=gridcare user=billing_app sslmode=require"

# ใช้ Connection String
psql "postgresql://billing_app@pg1:5432/gridcare?sslmode=require"
```

### 10.2 Meta-command สำคัญ

| Meta-command | หน้าที่ |
|---|---|
| `\conninfo` | ข้อมูลการเชื่อมต่อ |
| `\l` | ดู Database ทั้งหมด |
| `\du` | ดู Role ทั้งหมด |
| `\dn` | ดู Schema ทั้งหมด |
| `\dx` | ดู Extension |
| `\dt` | ดูตาราง |
| `\d <table>` | ดูโครงสร้างตาราง |
| `\di` | ดู Index |
| `\df` | ดู Function |
| `\dv` | ดู View |
| `\c <db>` | เปลี่ยน Database |
| `\x` | สลับแนวตั้ง/แนวนอน |
| `\timing` | เปิด/ปิดการจับเวลา |
| `\watch 5` | รันซ้ำทุก 5 วินาที |
| `\e` | เปิด Editor |
| `\i <file>` | รันไฟล์ SQL |
| `\o <file>` | เก็บ Output ลงไฟล์ |
| `\copy` | นำเข้า/ส่งออก CSV |
| `\gset` | เก็บผลลง Variable |
| `\gexec` | รัน SQL ที่ได้จาก Query |
| `\?` | Help Meta-command |
| `\h <SQL>` | Help SQL Syntax |
| `\q` | ออก |

### 10.3 ตัวอย่าง Meta-command

```sql
\conninfo
```

ผลลัพธ์:
```text
You are connected to database "gridcare" as user "postgres" via socket in "/var/run/postgresql" at port "5432".
```

```sql
\l
```

ผลลัพธ์:
```text
                                                       List of databases
   Name    |  Owner   | Encoding | Collate |  Ctype  | ICU Locale | Locale Provider |   Access privileges   
-----------+----------+----------+---------+---------+------------+-----------------+-----------------------
 postgres  | postgres | UTF8     | C.UTF-8 | C.UTF-8 |            | libc            | 
 template0 | postgres | UTF8     | C.UTF-8 | C.UTF-8 |            | libc            | =c/postgres          +
 template1 | postgres | UTF8     | C.UTF-8 | C.UTF-8 |            | libc            | =c/postgres          +
(3 rows)
```

```sql
\d gridcare.customers
```

ผลลัพธ์:
```text
                                       Table "gridcare.customers"
     Column     |           Type           | Collation | Nullable | Default 
----------------+--------------------------+-----------+----------+---------
 customer_id    | bigint                   |           | not null | 
 ca_number      | character(12)            |           | not null | 
 first_name     | text                     |           | not null | 
 phone          | text                     |           | not null | 
 citizen_id     | character(13)            |           | not null | 
 status         | character(1)             |           | not null | 
Indexes:
    "customers_pkey" PRIMARY KEY, btree (customer_id)
    "customers_ca_number_key" UNIQUE, btree (ca_number)
```

### 10.4 `\gset` และ `\gexec`

**`\gset`** — เก็บผลของ Query ลง Variable:

```sql
SELECT max(customer_id) AS max_id, count(*) AS total FROM gridcare.customers \gset
\echo 'Max ID:' :max_id 'Total:' :total
```

ผลลัพธ์:
```text
Max ID: 200000 Total: 200000
```

**`\gexec`** — รัน SQL ที่ได้จาก Query:

```sql
SELECT format('ALTER TABLE %s SET (autovacuum_vacuum_insert_scale_factor = 0.05)',
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

### 10.5 `\copy`

**ส่งออก:**
```sql
\copy (SELECT customer_id, ca_number, phone FROM gridcare.customers LIMIT 100) TO '/var/tmp/customers.csv' WITH CSV HEADER
```

**นำเข้า:**
```sql
\copy gridcare.customers FROM '/var/tmp/customers.csv' WITH CSV HEADER
```

> 💡 `\copy` ทำงานฝั่ง Client ทำให้ไม่ต้องมีสิทธิ์ Superuser บน Server

### 10.6 Variable ใน `psql`

```sql
\set last_day '2026-11-01'
SELECT * FROM gridcare.bills WHERE billing_period = :'last_day'::date LIMIT 5;
```

ผลลัพธ์:
```text
 bill_id | customer_id | billing_period | total_amount 
---------+-------------+----------------+--------------
       1 |           1 | 2026-11-01     |      1234.56
(5 rows)
```

### 10.7 Script ที่ปลอดภัย

```bash
#!/usr/bin/env bash
set -euo pipefail

psql -X -v ON_ERROR_STOP=1 \
     -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" \
     -f /opt/gridcare/scripts/weekly_report.sql
```

### 10.8 `.psqlrc` ที่แนะนำ

```ini
\set QUIET on
\pset null '∅'
\set HISTSIZE 10000
\set VERBOSITY verbose
\timing on
```

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: ตรวจสอบ Database ใน Script

```bash
psql -X -At -c "SELECT datname, pg_size_pretty(pg_database_size(datname)) FROM pg_database ORDER BY 1"
```

ผลลัพธ์:
```text
gridcare|1250 MB
postgres|7800 kB
template0|7300 kB
template1|7450 kB
```

### ตัวอย่างที่ 2: ใช้ `\gexec` สร้าง `ANALYZE`

```sql
SELECT 'ANALYZE gridcare.' || relname || ';'
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = 'gridcare' AND c.relkind = 'r'
ORDER BY relname
\gexec
```

### ตัวอย่างที่ 3: เฝ้าดู Metric ด้วย `\watch`

```sql
SELECT count(*) AS connections,
       max(now() - xact_start) AS longest_xact
FROM pg_stat_activity
WHERE state <> 'idle'
\watch 5
```

ผลลัพธ์ (ทุก 5 วินาที):
```text
 connections | longest_xact 
-------------+--------------
           3 | 00:00:02
(1 row)
```

### ตัวอย่างที่ 4: ส่งออก CSV แล้วนำกลับ

```sql
\copy (SELECT customer_id, ca_number, phone FROM gridcare.customers LIMIT 1000) TO '/var/tmp/cust.csv' WITH CSV HEADER
\copy gridcare.customers_staging FROM '/var/tmp/cust.csv' WITH CSV HEADER
```

## 12. สรุปย่อ จำง่าย
- **`psql -X` ใน Script เสมอ**  
- **Meta-command สำคัญ:** `\conninfo`, `\l`, `\du`, `\dt`, `\d`, `\dn`, `\dx`  
- **`\x` สลับแนว, `\timing` จับเวลา, `\watch` เฝ้าดู**  
- **`\gset` เก็บ Variable, `\gexec` รัน SQL ที่ได้จาก Query**  
- **`\copy` นำเข้า/ส่งออกฝั่ง Client**  
- **`ON_ERROR_STOP=1`** ใน Script

ประโยคจำ: **“`psql` คือ Swiss Army Knife ของ DBA”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — psql: https://www.postgresql.org/docs/17/app-psql.html
- PostgreSQL Documentation — psql Meta-commands: https://www.postgresql.org/docs/17/app-psql.html#APP-PSQL-META-COMMANDS
- GridCare Workshop Day 1: Lab 3.1 (ต่อ)

---

# บทที่ 22 DDL, DML และ Transaction

## 1. เรื่อง
คำสั่ง DDL, DML และการจัดการ Transaction ใน PostgreSQL ที่ใช้บ่อยในงาน Production

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจ DDL/DML และ Transaction อย่างถูกต้อง  
2. เพื่อให้หลีกเลี่ยงปัญหา Lock จาก DDL  
3. เพื่อให้ใช้ `BEGIN`/`COMMIT`/`ROLLBACK` อย่างปลอดภัย  
4. เพื่อให้เข้าใจ `SAVEPOINT` และ `ON CONFLICT`

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ใช้ `CREATE`, `ALTER`, `DROP` อย่างปลอดภัย  
- ใช้ `INSERT`, `UPDATE`, `DELETE`, `UPSERT`  
- ใช้ `BEGIN`, `COMMIT`, `ROLLBACK`, `SAVEPOINT`  
- ตั้ง `lock_timeout` ก่อน DDL  
- ใช้ `ON CONFLICT` ทำ Upsert

## 4. เนื้อหาโดยย่อ
**DDL** = `CREATE`, `ALTER`, `DROP`, `TRUNCATE`  
**DML** = `INSERT`, `UPDATE`, `DELETE`, `MERGE`  
**Transaction** = กลุ่มคำสั่งที่ Commit พร้อมกัน  
**Savepoint** = จุดย้อนกลับภายใน Transaction  
**UPSERT** = `INSERT ... ON CONFLICT`

## 5. ประโยชน์ที่ได้รับ
- ลดปัญหา Lock จาก DDL  
- เขียน Migration ที่ปลอดภัย  
- จัดการ Transaction อย่างถูกต้อง  
- ใช้ `ON CONFLICT` ลด Round-Trip  
- ลดการพังของระบบระหว่าง Migration

## 6. ข้อควรระวัง
- **DDL ต้องมี `lock_timeout`**  
- **`TRUNCATE` ต้องมีสิทธิ์ TRUNCATE**  
- **`UPDATE` ไม่มี `WHERE` กระทบทุกแถว**  
- **`DELETE` ต้องมี Index ที่เหมาะสม**  
- **`SAVEPOINT` ใช้ภายใน Transaction เท่านั้น**

## 7. ข้อดี
- Transaction ช่วยรักษาความถูกต้อง  
- `ON CONFLICT` ช่วยลด Race Condition  
- `SAVEPOINT` ช่วยย้อนกลับเฉพาะจุด  
- `lock_timeout` ช่วยป้องกันคิว Lock ยาว

## 8. ข้อเสีย
- DDL ใน Transaction อาจค้างนาน  
- `SAVEPOINT` จำนวนมากทำให้ช้า  
- `TRUNCATE` ไม่เรียก `DELETE Trigger`

## 9. ข้อห้าม
- ห้าม DDL บน Production โดยไม่ตั้ง `lock_timeout`  
- ห้าม `TRUNCATE` โดยไม่มี Backup ใน Production  
- ห้าม `UPDATE` โดยไม่มี `WHERE` โดยไม่ตั้งใจ  
- ห้าม `DELETE` จากตารางใหญ่โดยไม่มี Index  
- ห้าม `COMMIT` ทันทีหลัง DDL ที่อาจค้าง

## 10. รายละเอียด

### 10.1 DDL

```sql
CREATE TABLE gridcare.audit_log (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    action text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE gridcare.audit_log ADD COLUMN user_id text;

DROP TABLE IF EXISTS gridcare.audit_log;

TRUNCATE TABLE gridcare.audit_log RESTART IDENTITY;
```

### 10.2 DML

```sql
INSERT INTO gridcare.audit_log (action) VALUES ('login');

UPDATE gridcare.audit_log SET action = 'LOGOUT' WHERE id = 1;

DELETE FROM gridcare.audit_log WHERE id = 2;
```

### 10.3 UPSERT

```sql
INSERT INTO gridcare.audit_log (id, action) VALUES (1, 'login')
ON CONFLICT (id) DO UPDATE SET action = EXCLUDED.action;
```

### 10.4 Transaction

```sql
BEGIN;
UPDATE gridcare.bills SET status = 'PAID' WHERE bill_id = 100;
UPDATE gridcare.payments SET settled = true WHERE bill_id = 100;
COMMIT;
```

```sql
BEGIN;
UPDATE gridcare.bills SET status = 'PAID' WHERE bill_id = 100;
ROLLBACK;
```

### 10.5 Savepoint

```sql
BEGIN;
INSERT INTO gridcare.audit_log (action) VALUES ('start');
SAVEPOINT sp1;
UPDATE gridcare.audit_log SET action = 'bad' WHERE id = 1;
ROLLBACK TO SAVEPOINT sp1;
INSERT INTO gridcare.audit_log (action) VALUES ('end');
COMMIT;
```

ผลลัพธ์:
```text
BEGIN
INSERT 0 1
SAVEPOINT
UPDATE 1
ROLLBACK
INSERT 0 1
COMMIT
```

### 10.6 DDL ที่ปลอดภัย

```sql
SET lock_timeout = '3s';
ALTER TABLE gridcare.bills ADD COLUMN reminder_count smallint NOT NULL DEFAULT 0;
```

ผลลัพธ์ (ถ้า Lock ไม่ได้):
```text
ERROR:  canceling statement due to lock timeout
SQLSTATE: 55P03
```

### 10.7 `ON_ERROR_STOP` และ `\set`

```sql
\set ON_ERROR_STOP on
SET lock_timeout = '3s';
BEGIN;
ALTER TABLE ...;
COMMIT;
```

### 10.8 ตารางคำสั่งที่ใช้บ่อย

| ประเภท | คำสั่ง |
|---|---|
| Create | `CREATE TABLE`, `CREATE INDEX`, `CREATE SCHEMA` |
| Alter | `ALTER TABLE`, `ALTER INDEX`, `ALTER ROLE` |
| Drop | `DROP TABLE`, `DROP INDEX`, `DROP SCHEMA` |
| Insert | `INSERT`, `INSERT ... ON CONFLICT` |
| Update | `UPDATE` |
| Delete | `DELETE`, `TRUNCATE` |
| Transaction | `BEGIN`, `COMMIT`, `ROLLBACK`, `SAVEPOINT` |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: เพิ่มคอลัมน์แบบปลอดภัย

```sql
SET lock_timeout = '3s';
ALTER TABLE gridcare.bills ADD COLUMN reminder_count smallint NOT NULL DEFAULT 0;
```

ผลลัพธ์:
```text
SET
ALTER TABLE
```

### ตัวอย่างที่ 2: Upsert ที่ใช้บ่อย

```sql
INSERT INTO gridcare.sms_notifications (notification_id, customer_id, message_type, sent_at, status)
VALUES (2147483648, 1, 'PAYMENT_DUE', now(), 'QUEUED')
ON CONFLICT (notification_id) DO NOTHING
RETURNING notification_id;
```

ผลลัพธ์:
```text
 notification_id 
-----------------
      2147483648
(1 row)
```

### ตัวอย่างที่ 3: Transaction ที่ปลอดภัยกับ Lock Timeout

```sql
BEGIN;
SET LOCAL lock_timeout = '3s';
UPDATE gridcare.bills SET status = 'PAID' WHERE bill_id = 100;
COMMIT;
```

ผลลัพธ์:
```text
BEGIN
SET
UPDATE 1
COMMIT
```

### ตัวอย่างที่ 4: ถ้า Lock ไม่ได้

```sql
BEGIN;
SET LOCAL lock_timeout = '3s';
ALTER TABLE gridcare.tariff_rates ADD COLUMN note text;
```

ผลลัพธ์ (มีคนถือ Lock อยู่):
```text
ERROR:  canceling statement due to lock timeout
```

## 12. สรุปย่อ จำง่าย
- **DDL ต้องมี `lock_timeout`**  
- **`ON CONFLICT`** สำหรับ Upsert  
- **`SAVEPOINT`** สำหรับย้อนกลับเฉพาะจุด  
- **`TRUNCATE`** ไม่เรียก Trigger  
- **`UPDATE` ต้องมี `WHERE`**  
- **`DELETE` ต้องมี Index**  
- **`COMMIT` เฉพาะเมื่อมั่นใจ**

ประโยคจำ: **“DDL ที่ดียอมแพ้เร็ว ดีกว่าค้างคิว Lock”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — SQL Commands: https://www.postgresql.org/docs/17/sql-commands.html
- PostgreSQL Documentation — Transactions: https://www.postgresql.org/docs/17/tutorial-transactions.html
- GridCare Workshop Day 1: Lab 4.1 และ Day 5: Lab 2.2

---

# บทที่ 23 MVCC และ Isolation Level

## 1. เรื่อง
Multi-Version Concurrency Control (MVCC) และ Isolation Level ใน PostgreSQL

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจ MVCC และทำไมการอ่านไม่บล็อกการเขียน  
2. เพื่อให้เข้าใจ Isolation Level 4 ระดับ  
3. เพื่อให้รู้ว่า Isolation Level ใดเหมาะกับงานใด  
4. เพื่อให้เข้าใจ Phenomena ที่เกิดได้ในแต่ละ Level

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- อธิบาย MVCC ด้วย `xmin`, `xmax`, `ctid`  
- อธิบาย Isolation Level: Read Committed, Repeatable Read, Serializable  
- เลือก Isolation Level ที่เหมาะกับงาน  
- เข้าใจ `could not serialize access due to concurrent update`

## 4. เนื้อหาโดยย่อ
**MVCC** = การเก็บหลายเวอร์ชันของแถว  
- `xmin` — Transaction ที่สร้างแถว  
- `xmax` — Transaction ที่ลบ/อัปเดตแถว  
- `ctid` — Physical Location ของแถว

**Isolation Level:**
- **Read Uncommitted** — PostgreSQL ไม่รองรับ → ใช้ Read Committed  
- **Read Committed** — Default, เห็นเฉพาะ Commit แล้ว  
- **Repeatable Read** — Snapshot ทั้ง Transaction  
- **Serializable** — เทียบเท่า Serial Execution

## 5. ประโยชน์ที่ได้รับ
- เข้าใจว่าทำไม `UPDATE` ไม่บล็อก `SELECT`  
- เข้าใจว่า `REPEATABLE READ` อาจได้ Error เมื่อ Concurrent Update  
- เลือก Isolation Level ที่เหมาะกับงาน  
- ลดการเกิด Race Condition

## 6. ข้อควรระวัง
- **Read Committed** เห็นข้อมูลใหม่ใน Transaction  
- **Repeatable Read** อาจเกิด `serialization failure`  
- **Serializable** ต้องมี Retry Logic  
- **Long Transaction** ทำให้ Bloat  
- **MVCC ทำให้ Bloat** ถ้า Vacuum ไม่ทัน

## 7. ข้อดี
- การอ่านไม่บล็อกการเขียน  
- ลด Lock Contention  
- รองรับ Concurrency สูง  
- Isolation Level เลือกได้ตามงาน

## 8. ข้อเสีย
- ทำให้เกิด Bloat  
- Serializable ต้องมี Retry Logic  
- Snapshot เก่าทำให้ Vacuum ไม่ได้

## 9. ข้อห้าม
- ห้ามใช้ Serializable โดยไม่มี Retry Logic  
- ห้ามเปิด Transaction ค้างนาน  
- ห้ามปิด Autovacuum  
- ห้ามใช้ `SELECT FOR UPDATE` โดยไม่จำเป็น  
- ห้ามคาดหวังว่า Read Committed จะให้ผลสอดคล้องทั้ง Transaction

## 10. รายละเอียด

### 10.1 xmin, xmax, ctid

```sql
SELECT xmin, xmax, ctid, tariff_code, rate_per_kwh
FROM gridcare.tariff_rates WHERE tariff_code = 'RES';
```

ผลลัพธ์:
```text
 xmin | xmax | ctid  | tariff_code | rate_per_kwh 
------+------+-------+-------------+--------------
  745 |    0 | (0,1) | RES         |         3.90
(1 row)
```

```sql
BEGIN;
UPDATE gridcare.tariff_rates SET rate_per_kwh = rate_per_kwh WHERE tariff_code = 'RES';
SELECT xmin, xmax, ctid FROM gridcare.tariff_rates WHERE tariff_code = 'RES';
SELECT pg_current_xact_id();
ROLLBACK;
```

ผลลัพธ์:
```text
BEGIN
UPDATE 1
 xmin | xmax | ctid  
------+------+-------
  746 |    0 | (0,2)
(1 row)

 pg_current_xact_id 
--------------------
                746
(1 row)
ROLLBACK
```

> ✅ `ctid` เปลี่ยนจาก `(0,1)` เป็น `(0,2)` และ `xmin` = `pg_current_xact_id()`

### 10.2 Isolation Level

| Level | Dirty Read | Non-Repeatable Read | Phantom Read | Serialization Anomaly |
|---|---|---|---|---|
| Read Uncommitted | ❌ (ไม่รองรับ) | ✅ | ✅ | ✅ |
| Read Committed | ❌ | ✅ | ✅ | ✅ |
| Repeatable Read | ❌ | ❌ | ❌ (PostgreSQL) | ✅ |
| Serializable | ❌ | ❌ | ❌ | ❌ |

> ✅ = เกิดได้, ❌ = ไม่เกิด

### 10.3 Read Committed — Default

```sql
BEGIN;
SELECT rate_per_kwh FROM gridcare.tariff_rates WHERE tariff_code = 'SMB';
-- Transaction อื่น UPDATE
SELECT rate_per_kwh FROM gridcare.tariff_rates WHERE tariff_code = 'SMB';
COMMIT;
```

ผลลัพธ์:
```text
-- ครั้งแรก
 rate_per_kwh 
--------------
         4.50

-- ครั้งที่สอง (เห็นค่าใหม่ถ้า Commit แล้ว)
 rate_per_kwh 
--------------
         4.60
```

### 10.4 Repeatable Read — Snapshot ทั้ง Transaction

**หน้าต่าง 1:**
```sql
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT rate_per_kwh FROM gridcare.tariff_rates WHERE tariff_code = 'SMB';
```

ผลลัพธ์:
```text
 rate_per_kwh 
--------------
         4.50
```

**หน้าต่าง 2:**
```sql
UPDATE gridcare.tariff_rates SET rate_per_kwh = 4.60 WHERE tariff_code = 'SMB';
```

**หน้าต่าง 1 (อีกครั้ง):**
```sql
UPDATE gridcare.tariff_rates SET rate_per_kwh = 4.70 WHERE tariff_code = 'SMB';
```

ผลลัพธ์:
```text
ERROR:  could not serialize access due to concurrent update
```

```sql
ROLLBACK;
```

### 10.5 Serializable

```sql
BEGIN ISOLATION LEVEL SERIALIZABLE;
-- Transaction
COMMIT;
```

> 💡 ถ้าเกิด Conflict → `ERROR: could not serialize access due to read/write dependencies`  
> ต้องมี Retry Logic

### 10.6 Retry Logic ตัวอย่าง

```python
import psycopg2
import time

def run_tx_with_retry(conn, work, max_retries=3):
    for i in range(max_retries):
        try:
            with conn.cursor() as cur:
                work(cur)
                conn.commit()
                return
        except psycopg2.errors.SerializationFailure:
            conn.rollback()
            time.sleep(0.1 * (2 ** i))
    raise RuntimeError("Max retries exceeded")
```

### 10.7 Bloat จาก MVCC

```sql
SELECT relname, n_live_tup, n_dead_tup,
       round(100.0 * n_dead_tup / nullif(n_live_tup + n_dead_tup, 0), 1) AS dead_pct
FROM pg_stat_user_tables
WHERE schemaname = 'gridcare' AND n_dead_tup > 0
ORDER BY n_dead_tup DESC LIMIT 5;
```

ผลลัพธ์:
```text
     relname     | n_live_tup | n_dead_tup | dead_pct 
-----------------+------------+------------+----------
 bills           |    1200000 |      12000 |      1.0
 payments        |     450000 |       4500 |      1.0
```

### 10.8 ตารางเลือก Isolation Level

| งาน | Isolation Level |
|---|---|
| Read-only Report | Read Committed |
| Read-only Report ที่ต้องการ Snapshot | Repeatable Read |
| Transaction ที่อ่านและเขียนหลายครั้ง | Repeatable Read หรือ Serializable |
| Financial Transaction | Serializable + Retry |
| Background Job ที่อ่านค่าเดียว | Read Committed |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: ดู `xmin`/`xmax` ในตารางจริง

```sql
SELECT xmin, xmax, ctid, customer_id, status
FROM gridcare.customers WHERE customer_id = 1;
```

ผลลัพธ์:
```text
 xmin | xmax | ctid   | customer_id | status 
------+------+--------+-------------+--------
  742 |    0 | (0,1)  |           1 | A
```

### ตัวอย่างที่ 2: สาธิต Repeatable Read Error

**หน้าต่าง 1:**
```sql
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT rate_per_kwh FROM gridcare.tariff_rates WHERE tariff_code = 'SMB';
-- 4.50
```

**หน้าต่าง 2:**
```sql
UPDATE gridcare.tariff_rates SET rate_per_kwh = 4.60 WHERE tariff_code = 'SMB';
```

**หน้าต่าง 1:**
```sql
UPDATE gridcare.tariff_rates SET rate_per_kwh = 4.70 WHERE tariff_code = 'SMB';
```

ผลลัพธ์:
```text
ERROR:  could not serialize access due to concurrent update
```

### ตัวอย่างที่ 3: Transaction ค้างทำให้ Vacuum ไม่ได้

```sql
SELECT pid, state, age(backend_xmin) AS xmin_age, now() - xact_start AS xact_age
FROM pg_stat_activity WHERE backend_xmin IS NOT NULL
ORDER BY xmin_age DESC;
```

ผลลัพธ์:
```text
  pid  |        state        | xmin_age |  xact_age    
-------+---------------------+----------+--------------
 12345 | idle in transaction |       85 | 00:01:25
```

> ⚠️ Transaction ค้างทำให้ Vacuum ลบ Dead Tuple ไม่ได้

## 12. สรุปย่อ จำง่าย
- **MVCC ทำให้อ่านไม่บล็อกเขียน**  
- **`xmin` = สร้าง, `xmax` = ลบ, `ctid` = ที่อยู่**  
- **Read Committed = Default**  
- **Repeatable Read = Snapshot ทั้ง Transaction**  
- **Serializable = ต้องมี Retry Logic**  
- **Long Transaction ทำให้ Bloat**  
- **`could not serialize access` = ต้อง Retry**

ประโยคจำ: **“MVCC ให้ Concurrency แต่ต้องแลกด้วย Bloat”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — Concurrency Control: https://www.postgresql.org/docs/17/mvcc.html
- PostgreSQL Documentation — Transaction Isolation: https://www.postgresql.org/docs/17/transaction-iso.html
- GridCare Workshop Day 1: Lab 4.1

---

# บทที่ 24 Lock และคิว Lock

## 1. เรื่อง
Lock ใน PostgreSQL ประเภทของ Lock คิว Lock และวิธีหา Root Cause ของ Lock Wait

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจ Lock Mode ที่สำคัญ  
2. เพื่อให้หาต้นคิว Lock ได้  
3. เพื่อให้แก้ปัญหา Lock Wait อย่างเป็นระบบ  
4. เพื่อให้ป้องกัน Lock Queue ในอนาคต

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- อธิบาย Lock Mode: `AccessShareLock`, `AccessExclusiveLock`  
- ใช้ `pg_blocking_pids()` หาต้นคิว  
- ใช้ `log_lock_waits` เห็น Lock Wait ใน Log  
- ใช้ `lock_timeout` ป้องกันคิว  
- ใช้ `pg_cancel_backend` และ `pg_terminate_backend`

## 4. เนื้อหาโดยย่อ
Lock Mode สำคัญ:
- **AccessShareLock** — `SELECT`  
- **RowExclusiveLock** — `INSERT`, `UPDATE`, `DELETE`  
- **ShareUpdateExclusiveLock** — `VACUUM`, `CREATE INDEX CONCURRENTLY`  
- **ShareLock** — `CREATE INDEX`  
- **AccessExclusiveLock** — `ALTER TABLE`, `DROP TABLE`, `TRUNCATE`

คิว Lock:
- Lock รอเป็นคิว  
- ถ้ามี `AccessExclusiveLock` รอ → Lock อื่นทั้งหมดรอตาม  
- ต้องหา Root Cause ไม่ใช่แค่ Kill

## 5. ประโยชน์ที่ได้รับ
- หา Root Cause ของ Lock Wait ได้  
- ลดเวลาตอบสนอง Incident  
- ป้องกันคิว Lock ยาว  
- เข้าใจว่า DDL ที่รอ Lock ทำให้แอปหยุด

## 6. ข้อควรระวัง
- **`AccessExclusiveLock` ที่รอ** ทำให้ Lock อื่นรอทั้งหมด  
- **`pg_terminate_backend`** ตัด Session ทันที  
- **`lock_timeout`** ควรตั้งก่อน DDL ทุกครั้ง  
- **Transaction ค้าง** ทำให้ Lock ค้าง  
- **`log_lock_waits`** ต้องตั้ง `deadlock_timeout` ให้เหมาะ

## 7. ข้อดี
- Lock Mode ละเอียด ทำให้ Concurrency สูง  
- มี View และฟังก์ชันช่วยหา Root Cause  
- มี `lock_timeout` ป้องกันคิว  
- มี `log_lock_waits` ช่วยตรวจ

## 8. ข้อเสีย
- Lock Queue ทำให้แอปหยุดทั้งระบบ  
- การแก้ผิดวิธีทำให้เกิดปัญหาใหม่  
- ต้องเข้าใจ Lock Mode จึงจะแก้ถูก

## 9. ข้อห้าม
- ห้าม `pg_terminate_backend` โดยไม่หาสาเหตุ  
- ห้าม `ALTER TABLE` โดยไม่มี `lock_timeout`  
- ห้าม Transaction ค้างในแอป  
- ห้ามเปิด `deadlock_timeout` สูงเกินไป  
- ห้ามปิด `log_lock_waits`

## 10. รายละเอียด

### 10.1 Lock Mode

| Lock Mode | คำสั่งที่ใช้ | บล็อก |
|---|---|---|
| AccessShareLock | `SELECT` | AccessExclusiveLock |
| RowShareLock | `SELECT FOR UPDATE` | AccessExclusiveLock, ShareLock |
| RowExclusiveLock | `INSERT`, `UPDATE`, `DELETE` | ShareLock, ShareRowExclusiveLock, ExclusiveLock, AccessExclusiveLock |
| ShareUpdateExclusiveLock | `VACUUM`, `CREATE INDEX CONCURRENTLY` | ShareUpdateExclusiveLock, ShareLock, ShareRowExclusiveLock, ExclusiveLock, AccessExclusiveLock |
| ShareLock | `CREATE INDEX` | RowExclusiveLock, ShareUpdateExclusiveLock, ShareLock, ShareRowExclusiveLock, ExclusiveLock, AccessExclusiveLock |
| ShareRowExclusiveLock | `CREATE TRIGGER` | RowExclusiveLock, ShareUpdateExclusiveLock, ShareLock, ShareRowExclusiveLock, ExclusiveLock, AccessExclusiveLock |
| ExclusiveLock | `REFRESH MATERIALIZED VIEW CONCURRENTLY` | RowExclusiveLock, ShareUpdateExclusiveLock, ShareLock, ShareRowExclusiveLock, ExclusiveLock, AccessExclusiveLock |
| AccessExclusiveLock | `ALTER TABLE`, `DROP TABLE`, `TRUNCATE` | ทุก Lock |

### 10.2 ดู Lock ในปัจจุบัน

```sql
SELECT l.pid, l.locktype, l.mode, l.granted,
       a.application_name, a.state, a.query
FROM pg_locks AS l
JOIN pg_stat_activity AS a ON a.pid = l.pid
WHERE l.locktype = 'relation' AND a.datname = 'gridcare'
ORDER BY l.granted, l.pid;
```

### 10.3 หาต้นคิว Lock

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

### 10.4 หา Root Cause (ต้นคิว)

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

> ✅ **ต้นคิว = `batch_A`** (pid 7659) เพราะบล็อกคนอื่น แต่ตัวเองไม่ถูกใครบล็อก

### 10.5 Log Lock Wait

```bash
sudo grep "still waiting" /var/log/postgresql/postgresql-17-main.log | tail -2
```

ผลลัพธ์:
```text
2026-11-02 14:12:34.567 +07 [7665] postgres@gridcare app=migration_B client=[local] LOG:  process 7665 still waiting for AccessExclusiveLock on relation 16384 of database 16389 after 1000.123 ms
2026-11-02 14:12:34.567 +07 [7672] postgres@gridcare app=app_C client=[local] LOG:  process 7672 still waiting for AccessShareLock on relation 16384 of database 16389 after 1000.456 ms
```

### 10.6 แก้ตามลำดับที่ถูกต้อง

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

### 10.7 `lock_timeout` ที่ถูกต้อง

```sql
SET lock_timeout = '3s';
ALTER TABLE gridcare.tariff_rates ADD COLUMN note text;
```

ผลลัพธ์ (ถ้า Lock ไม่ได้):
```text
ERROR:  canceling statement due to lock timeout
SQLSTATE: 55P03
```

### 10.8 ตั้ง `log_lock_waits` และ `deadlock_timeout`

```ini
log_lock_waits = on
deadlock_timeout = 1s
```

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: ตั้ง tmux 4 หน้าต่าง

```bash
tmux new -s lock
# Ctrl+b " (แบ่งบนล่าง)
# Ctrl+b % (แบ่งซ้ายขวา)
# เข้า psql ทุกหน้าต่าง: sudo -u postgres psql -d gridcare
```

**หน้าต่าง 1:**
```sql
SET application_name = 'batch_A';
BEGIN;
SELECT count(*) FROM gridcare.tariff_rates;
-- ไม่ COMMIT
```

**หน้าต่าง 2:**
```sql
SET application_name = 'migration_B';
ALTER TABLE gridcare.tariff_rates ADD COLUMN note text;
-- ค้าง
```

**หน้าต่าง 3:**
```sql
SET application_name = 'app_C';
SELECT * FROM gridcare.tariff_rates;
-- ค้าง
```

**หน้าต่าง 4:**
```sql
SELECT pid, application_name, wait_event_type, pg_blocking_pids(pid)
FROM pg_stat_activity
WHERE datname = 'gridcare' AND backend_type = 'client backend';
```

ผลลัพธ์:
```text
 pid  | application_name | wait_event_type | pg_blocking_pids 
------+------------------+-----------------+------------------
 7659 | batch_A          | Client          | {}
 7665 | migration_B      | Lock            | {7659}
 7672 | app_C            | Lock            | {7665}
```

### ตัวอย่างที่ 2: Lock Timeout ที่ถูกต้อง

**หน้าต่าง 1:**
```sql
BEGIN;
SELECT count(*) FROM gridcare.tariff_rates;
```

**หน้าต่าง 2:**
```sql
SET lock_timeout = '3s';
ALTER TABLE gridcare.tariff_rates ADD COLUMN note text;
```

ผลลัพธ์:
```text
SET
ERROR:  canceling statement due to lock timeout
```

**ปิดหน้าต่าง 1:**
```sql
ROLLBACK;
```

### ตัวอย่างที่ 3: ตรวจสอบ Lock ที่ค้างบน Relation

```sql
SELECT c.relname, l.mode, l.granted, count(*) AS sessions
FROM pg_locks AS l
JOIN pg_class AS c ON c.oid = l.relation
WHERE l.locktype = 'relation' AND c.relname = 'tariff_rates'
GROUP BY c.relname, l.mode, l.granted
ORDER BY l.granted, l.mode;
```

## 12. สรุปย่อ จำง่าย
- **Lock Mode สำคัญ:** AccessShareLock, RowExclusiveLock, AccessExclusiveLock  
- **AccessExclusiveLock ที่รอ = คิวหยุด**  
- **หาต้นคิวด้วย `pg_blocking_pids`**  
- **`log_lock_waits` + `deadlock_timeout`**  
- **`lock_timeout` ก่อน DDL ทุกครั้ง**  
- **`pg_cancel_backend` ก่อน `pg_terminate_backend`**

ประโยคจำ: **“Lock ไม่ใช่ศัตรู แต่ Lock ที่ค้างคือศัตรู”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — Explicit Locking: https://www.postgresql.org/docs/17/explicit-locking.html
- PostgreSQL Documentation — Monitoring Locks: https://www.postgresql.org/docs/17/monitoring-locks.html
- PostgreSQL Documentation — pg_blocking_pids: https://www.postgresql.org/docs/17/functions-info.html#FUNCTIONS-INFO-SESSION-TABLE
- GridCare Workshop Day 1: Lab 4.1

---

# บทที่ 25 การอ่าน EXPLAIN และ EXPLAIN ANALYZE

## 1. เรื่อง
การอ่านแผนการทำงาน (Query Plan) ด้วย `EXPLAIN` และ `EXPLAIN ANALYZE` เพื่อปรับแต่ง Query

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจ Node ใน Plan  
2. เพื่อให้อ่าน Cost, Rows, Actual Rows ได้  
3. เพื่อให้หา Bottleneck ใน Query  
4. เพื่อให้ตัดสินใจเรื่อง Index ได้

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- อ่าน `EXPLAIN` และ `EXPLAIN ANALYZE`  
- ระบุ Node หลัก: Seq Scan, Index Scan, Hash Join, Nested Loop  
- เข้าใจ Cost, Rows Estimate, Actual Rows  
- ระบุ Bottleneck: Rows Removed by Filter, Sort Spill, Seq Scan

## 4. เนื้อหาโดยย่อ
**`EXPLAIN`** — แสดงแผนโดยไม่รัน  
**`EXPLAIN ANALYZE`** — รันจริงและแสดงสถิติ  
**`BUFFERS`** — แสดง I/O  
**`TIMING OFF`** — ไม่จับเวลาละเอียด (เหมาะกับ Query ที่รันเร็วมาก)

Node หลัก:
- **Seq Scan** — อ่านทั้งตาราง  
- **Index Scan** — อ่านผ่าน Index  
- **Index Only Scan** — อ่านเฉพาะ Index  
- **Bitmap Scan** — ใช้ Bitmap  
- **Hash Join** — Join ด้วย Hash  
- **Nested Loop** — Join ด้วย Loop  
- **Merge Join** — Join ด้วย Merge

## 5. ประโยชน์ที่ได้รับ
- หา Bottleneck ได้  
- ตัดสินใจสร้าง Index ได้  
- ตรวจ Extended Statistics ได้  
- ลด Query ที่ช้า

## 6. ข้อควรระวัง
- **`EXPLAIN ANALYZE` รัน Query จริง** — ระวังกับ `INSERT`/`UPDATE`/`DELETE`  
- **Cost เป็นค่าประมาณ** ไม่ใช่ ms  
- **Actual Rows ≠ Rows Estimate** = Statistic ผิด  
- **`BUFFERS`** ช่วยบอก Cache Hit  
- **`TIMING OFF`** ควรใช้กับ Query ที่รันเร็วมาก

## 7. ข้อดี
- แม่นยำที่สุดในการหา Bottleneck  
- ใช้ `BUFFERS` ดู Cache Hit  
- ใช้ `ANALYZE` ดู Actual Rows

## 8. ข้อเสีย
- `ANALYZE` รัน Query จริง  
- Plan อาจเปลี่ยนตาม Statistic  
- ต้องเข้าใจ Cost Model

## 9. ข้อห้าม
- ห้าม `EXPLAIN ANALYZE DELETE` บน Production  
- ห้ามใช้ `EXPLAIN` โดยไม่อ่าน Rows Estimate  
- ห้ามสรุปจาก Cost เพียงอย่างเดียว  
- ห้ามใช้ `EXPLAIN ANALYZE` กับ Query ที่ใช้เวลานานมากบน Production

## 10. รายละเอียด

### 10.1 `EXPLAIN` พื้นฐาน

```sql
EXPLAIN SELECT * FROM gridcare.customers WHERE ca_number = '020000123456';
```

ผลลัพธ์:
```text
                                       QUERY PLAN                                        
-----------------------------------------------------------------------------------------
 Index Scan using customers_ca_number_key on customers  (cost=0.42..8.44 rows=1 width=42)
   Index Cond: (ca_number = '020000123456'::bpchar)
(2 rows)
```

### 10.2 `EXPLAIN ANALYZE` พร้อม `BUFFERS`

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT customer_id, ca_number, first_name, tariff_code
FROM gridcare.customers WHERE ca_number = '020000123456';
```

ผลลัพธ์:
```text
                                          QUERY PLAN                                          
----------------------------------------------------------------------------------------------
 Index Scan using customers_ca_number_key on customers
   (cost=0.42..8.44 rows=1 width=42) (actual time=0.045..0.046 rows=1 loops=1)
   Index Cond: (ca_number = '020000123456'::bpchar)
   Buffers: shared hit=3
 Planning Time: 0.123 ms
 Execution Time: 0.067 ms
(5 rows)
```

### 10.3 Node ที่ควรรู้

| Node | ความหมาย | เมื่อไหร่ใช้ |
|---|---|---|
| Seq Scan | อ่านทั้งตาราง | ตารางเล็ก หรือ WHERE ไม่มี Index |
| Index Scan | อ่านผ่าน Index | WHERE มี Index และคืนไม่กี่แถว |
| Index Only Scan | อ่านเฉพาะ Index | SELECT เฉพาะคอลัมน์ใน Index |
| Bitmap Heap Scan | ใช้ Bitmap | WHERE คืนหลายแถวแต่ไม่มาก |
| Hash Join | Join ด้วย Hash | ตารางใหญ่ทั้งสองฝั่ง |
| Nested Loop | Join ด้วย Loop | ตารางเล็ก + Index |
| Merge Join | Join ด้วย Merge | ทั้งสองฝั่งมี Sort |

### 10.4 Rows Estimate vs Actual

```sql
EXPLAIN (ANALYZE, TIMING OFF)
SELECT count(*) FROM gridcare.bills
WHERE billing_period = '2026-09-01' AND status = 'UNPAID';
```

ผลลัพธ์ (ก่อน Extended Statistics):
```text
               ->  Parallel Seq Scan on bills
                     (cost=0.00..7933.85 rows=13897 width=0) (actual time=0.234..42.123 rows=0 loops=3)
                     Filter: ((billing_period = '2026-09-01'::date) AND (status = 'UNPAID'::bpchar))
                     Rows Removed by Filter: 33333
```

> ⚠️ ประมาณ `rows=13897` แต่จริง `rows=0`

หลังสร้าง Extended Statistics:
```text
               ->  Parallel Seq Scan on bills
                     (cost=0.00..7933.85 rows=300 width=0) (actual time=0.012..0.034 rows=0 loops=3)
                     Rows Removed by Filter: 0
```

### 10.5 Bottleneck ที่พบบ่อย

| อาการ | ความหมาย | การแก้ |
|---|---|---|
| `Rows Removed by Filter` สูง | อ่านมากแต่คืนน้อย | สร้าง Index |
| `Seq Scan` บนตารางใหญ่ | ไม่มี Index | สร้าง Index |
| `external merge Disk` | Sort ล้น Disk | เพิ่ม `work_mem` หรือสร้าง Index |
| `Rows Estimate ≠ Actual` | Statistic ผิด | `ANALYZE` หรือ Extended Statistics |
| `Buffers: shared read` สูง | Cache Miss | เพิ่ม `shared_buffers` หรือ Cache |

### 10.6 `TIMING OFF`

```sql
EXPLAIN (ANALYZE, TIMING OFF)
SELECT count(*) FROM gridcare.bills;
```

> 💡 ใช้เมื่อ Query รันเร็วมาก (เช่น < 1ms) เพื่อลด Overhead

### 10.7 เปรียบเทียบ Before/After Index

**ก่อน Index:**
```text
 Gather  (cost=1000.00..12666.67 rows=1 width=42) (actual time=12.345..45.678 rows=1 loops=1)
   Workers Planned: 2
   ->  Parallel Seq Scan on customers (actual time=8.234..38.456 rows=0 loops=3)
         Filter: (ca_number = '020000123456'::bpchar)
         Rows Removed by Filter: 66666
 Execution Time: 45.789 ms
```

**หลัง Index:**
```text
 Index Scan using customers_ca_number_key on customers
   (cost=0.42..8.44 rows=1 width=42) (actual time=0.045..0.046 rows=1 loops=1)
   Index Cond: (ca_number = '020000123456'::bpchar)
 Execution Time: 0.067 ms
```

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: อ่าน Plan แบบละเอียด

```sql
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT c.customer_id, c.ca_number, w.work_order_id, w.status
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
   Sort Method: quicksort  Memory: 345kB
   ->  Hash Right Join  (cost=150.00..1050.00 rows=2345 width=78) (actual time=0.234..4.123 rows=2345 loops=1)
         Hash Cond: (w.customer_id = c.customer_id)
         ->  Seq Scan on work_orders w  (actual time=0.012..3.456 rows=5000 loops=1)
         ->  Hash  (actual time=1.234..1.235 rows=1000 loops=1)
               Buckets: 1024  Batches: 1  Memory Usage: 45kB
               ->  Index Scan using customers_office_id_idx on customers c
                     (actual time=0.045..0.890 rows=1000 loops=1)
                     Index Cond: (office_id = 5)
 Planning Time: 0.456 ms
 Execution Time: 4.789 ms
```

### ตัวอย่างที่ 2: ตรวจ Sort Spill

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT payment_id, bill_id, paid_at, amount
FROM gridcare.payments
ORDER BY paid_at DESC, payment_id DESC
OFFSET 100000 LIMIT 50;
```

ผลลัพธ์ (ก่อนมี Index):
```text
 Limit  (cost=5432.00..5433.00 rows=50 width=42) (actual time=234.567..234.678 rows=50 loops=1)
   ->  Sort  (cost=5432.00..5433.00 rows=450000 width=42) (actual time=234.567..234.678 rows=100050 loops=1)
         Sort Key: paid_at DESC, payment_id DESC
         Sort Method: external merge  Disk: 12345kB
         ->  Seq Scan on payments (actual time=0.012..65.234 rows=450000 loops=1)
 Execution Time: 234.789 ms
```

> ⚠️ `external merge Disk: 12345kB` = Sort ล้น Disk

### ตัวอย่างที่ 3: ใช้ `\gexec` กับ `EXPLAIN`

```sql
SELECT 'EXPLAIN ANALYZE ' || query
FROM (VALUES
  ('SELECT count(*) FROM gridcare.bills'),
  ('SELECT count(*) FROM gridcare.payments')
) AS v(query)
\gexec
```

## 12. สรุปย่อ จำง่าย
- **`EXPLAIN` = แผน, `EXPLAIN ANALYZE` = รันจริง**  
- **`BUFFERS` = I/O, `TIMING OFF` = ลด Overhead**  
- **Node หลัก:** Seq Scan, Index Scan, Hash Join, Nested Loop  
- **`Rows Removed by Filter` สูง = ต้องสร้าง Index**  
- **`external merge Disk` = เพิ่ม `work_mem`**  
- **Rows Estimate ≠ Actual = Statistic ผิด**

ประโยคจำ: **“Plan บอกว่า PostgreSQL กำลังคิดอะไร เราแค่ต้องอ่านให้ออก”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — Using EXPLAIN: https://www.postgresql.org/docs/17/using-explain.html
- PostgreSQL Documentation — EXPLAIN: https://www.postgresql.org/docs/17/sql-explain.html
- GridCare Workshop Day 2: Lab 1.1, Workshop Day 2 ขั้นที่ 1

---

# บทที่ 26 Index เบื้องต้น

## 1. เรื่อง
Index ใน PostgreSQL ประเภทของ Index การเลือกใช้ และการดูแลสุขภาพ Index

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจ Index ประเภทต่าง ๆ  
2. เพื่อให้เลือก Index ได้เหมาะกับ Query  
3. เพื่อให้สร้าง Index แบบไม่บล็อก (`CONCURRENTLY`)  
4. เพื่อให้ตรวจสุขภาพ Index

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- อธิบาย B-tree, Hash, GiST, GIN, BRIN  
- สร้าง Index แบบ `CONCURRENTLY`  
- ตรวจ `indisvalid` และ `idx_scan`  
- หา Duplicate Index และ Unused Index

## 4. เนื้อหาโดยย่อ
Index ประเภทหลัก:
- **B-tree** — Default, ใช้กับ `=`, `<`, `>`, `ORDER BY`  
- **Hash** — ใช้กับ `=` เท่านั้น  
- **GIN** — เหมาะกับ Array, JSONB, Full-text  
- **GiST** — เหมาะกับ Geometric, Range  
- **BRIN** — เหมาะกับข้อมูลที่เรียงตามเวลา (เช่น `read_at`)  
- **SP-GiST** — เหมาะกับข้อมูลที่มีโครงสร้าง

การสร้าง Index:
- **ปกติ** — บล็อกการเขียน  
- **`CONCURRENTLY`** — ไม่บล็อก แต่ใช้เวลานานกว่า

## 5. ประโยชน์ที่ได้รับ
- Query เร็วขึ้นอย่างมีนัยสำคัญ  
- ลด I/O  
- ลด Lock  
- ตรวจสุขภาพ Index ได้

## 6. ข้อควรระวัง
- **Index เปลือง Disk**  
- **Index ทำให้ `INSERT`/`UPDATE` ช้าลง**  
- **`CONCURRENTLY` ต้องอยู่นอก Transaction**  
- **ตรวจ `indisvalid = t` หลังสร้าง**  
- **Index ที่ไม่ถูกใช้ = เปลือง Disk**

## 7. ข้อดี
- เร็วขึ้นอย่างมีนัยสำคัญ  
- มีหลายประเภทให้เลือก  
- `CONCURRENTLY` ไม่บล็อก  
- BRIN เหมาะกับข้อมูล Time-Series

## 8. ข้อเสีย
- เปลือง Disk  
- ทำให้ `INSERT`/`UPDATE` ช้าลง  
- `CONCURRENTLY` ใช้เวลานาน

## 9. ข้อห้าม
- ห้าม `CREATE INDEX` บน Production โดยไม่ตรวจ `indisvalid`  
- ห้าม `CREATE INDEX CONCURRENTLY` ใน Transaction  
- ห้ามสร้าง Index ซ้ำ  
- ห้ามลบ Index ที่ยังถูกใช้  
- ห้ามใช้ `Hash` Index กับ `>` หรือ `<`

## 10. รายละเอียด

### 10.1 B-tree — Default

```sql
CREATE INDEX customers_office_id_idx ON gridcare.customers (office_id);
```

ใช้กับ:
- `=`, `<`, `<=`, `>`, `>=`  
- `ORDER BY`  
- `IN`  
- `LIKE 'prefix%'`

### 10.2 Unique Index

```sql
CREATE UNIQUE INDEX CONCURRENTLY customers_ca_number_key
  ON gridcare.customers (ca_number);
```

### 10.3 `CONCURRENTLY`

```sql
CREATE INDEX CONCURRENTLY work_orders_customer_idx
  ON gridcare.work_orders (customer_id);
```

> ⚠️ ต้องอยู่นอก Transaction

### 10.4 Partial Index

```sql
CREATE INDEX bills_unpaid_idx ON gridcare.bills (customer_id)
  WHERE status = 'UNPAID';
```

> 💡 ใช้กับ Query ที่มี `WHERE status = 'UNPAID'` เสมอ

### 10.5 Expression Index

```sql
CREATE INDEX payments_paid_at_date_idx ON gridcare.payments ((paid_at::date));
```

> 💡 ใช้เมื่อ Query ใช้ `paid_at::date`

### 10.6 BRIN

```sql
CREATE INDEX meter_readings_read_at_brin ON gridcare.meter_readings
  USING brin (read_at);
```

> 💡 เหมาะกับข้อมูลที่เรียงตามเวลา, เปลือง Disk น้อยกว่า B-tree

### 10.7 GIN

```sql
CREATE INDEX customers_tags_gin ON gridcare.customers USING gin (tags);
```

> 💡 เหมาะกับ Array, JSONB, Full-text

### 10.8 ตรวจสุขภาพ Index

```sql
SELECT c.relname AS index_name, i.indisvalid, i.indisready,
       pg_size_pretty(pg_relation_size(c.oid)) AS size,
       s.idx_scan, s.idx_tup_read
FROM pg_index AS i
JOIN pg_class AS c ON c.oid = i.indexrelid
LEFT JOIN pg_stat_user_indexes AS s ON s.indexrelid = i.indexrelid
WHERE i.indrelid = 'gridcare.customers'::regclass;
```

ผลลัพธ์:
```text
          index_name           | indisvalid | indisready |  size    | idx_scan | idx_tup_read
-------------------------------+------------+------------+----------+----------+--------------
 customers_pkey                | t          | t          | 4800 kB  |     1234 |        12345
 customers_ca_number_key       | t          | t          | 4800 kB  |     8452 |         8452
 customers_office_id_idx       | t          | t          | 3200 kB  |     5678 |       123456
```

### 10.9 หา Duplicate Index

```sql
SELECT indrelid::regclass AS table_name,
       array_agg(indexrelid::regclass) AS indexes,
       count(*) AS dup_count
FROM pg_index
GROUP BY indrelid, indkey
HAVING count(*) > 1;
```

### 10.10 หา Unused Index

```sql
SELECT s.schemaname, s.relname, s.indexrelname, s.idx_scan,
       pg_size_pretty(pg_relation_size(s.indexrelid)) AS size
FROM pg_stat_user_indexes AS s
WHERE s.idx_scan = 0
  AND s.schemaname = 'gridcare'
ORDER BY pg_relation_size(s.indexrelid) DESC;
```

### 10.11 ตารางเลือก Index

| สถานการณ์ | Index ที่เหมาะ |
|---|---|
| `WHERE col = $1` | B-tree |
| `WHERE col > $1` | B-tree |
| `ORDER BY col` | B-tree |
| `WHERE col LIKE 'prefix%'` | B-tree (`text_pattern_ops`) |
| Array, JSONB, Full-text | GIN |
| Time-series | BRIN |
| Geometric | GiST |
| `WHERE status = 'UNPAID'` (subset) | Partial B-tree |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: สร้าง Index และตรวจสอบ

```sql
CREATE UNIQUE INDEX CONCURRENTLY customers_ca_number_key
  ON gridcare.customers (ca_number);

SELECT indexrelid::regclass, indisvalid
FROM pg_index WHERE indexrelid = 'customers_ca_number_key'::regclass;
```

ผลลัพธ์:
```text
             indexrelid             | indisvalid 
------------------------------------+------------
 customers_ca_number_key            | t
```

### ตัวอย่างที่ 2: วัด Before/After

**ก่อน:**
```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT customer_id, ca_number FROM gridcare.customers WHERE ca_number = '020000123456';
```

ผลลัพธ์:
```text
 Gather  (cost=1000.00..12666.67 rows=1 width=42) (actual time=12.345..45.678 rows=1)
   ->  Parallel Seq Scan on customers (actual time=8.234..38.456 rows=0 loops=3)
         Filter: (ca_number = '020000123456'::bpchar)
         Rows Removed by Filter: 66666
 Execution Time: 45.789 ms
```

**หลัง:**
```sql
-- สร้าง Index แล้ว
EXPLAIN (ANALYZE, BUFFERS)
SELECT customer_id, ca_number FROM gridcare.customers WHERE ca_number = '020000123456';
```

ผลลัพธ์:
```text
 Index Scan using customers_ca_number_key on customers
   (cost=0.42..8.44 rows=1 width=42) (actual time=0.045..0.046 rows=1 loops=1)
   Index Cond: (ca_number = '020000123456'::bpchar)
 Execution Time: 0.067 ms
```

> ✅ **45.789 ms → 0.067 ms** (~683 เท่า)

### ตัวอย่างที่ 3: Index ที่ค้างหลัง CIC ล้ม

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
DROP INDEX CONCURRENTLY gridcare.payments_paid_at_demo_idx;
```

## 12. สรุปย่อ จำง่าย
- **B-tree = Default**  
- **Unique Index** สำหรับคอลัมน์ที่ไม่ซ้ำ  
- **`CONCURRENTLY`** ไม่บล็อก แต่ต้องอยู่นอก Transaction  
- **BRIN** เหมาะกับ Time-series  
- **Partial Index** สำหรับ Subset  
- **ตรวจ `indisvalid` และ `idx_scan`**

ประโยคจำ: **“Index ที่ดีทำให้ Query เร็ว Index ที่ไม่ใช้ทำให้ Disk เสียเปล่า”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — Indexes: https://www.postgresql.org/docs/17/indexes.html
- PostgreSQL Documentation — CREATE INDEX: https://www.postgresql.org/docs/17/sql-createindex.html
- GridCare Workshop Day 2: Lab 2.2, Workshop Day 2 ขั้นที่ 1

---

# บทที่ 27 Statistics และ Extended Statistics

## 1. เรื่อง
Statistics ใน PostgreSQL ที่ Planner ใช้ และ Extended Statistics สำหรับคอลัมน์ที่มี Correlation

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจว่าทำไม Planner เลือกแผนผิด  
2. เพื่อให้ใช้ `ANALYZE` และ `pg_stats`  
3. เพื่อให้สร้าง Extended Statistics  
4. เพื่อให้ตรวจสอบ Row Estimate

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- อธิบาย Statistics พื้นฐานได้  
- ใช้ `pg_stats` และ `pg_stats_ext`  
- สร้าง Extended Statistics สำหรับ Multi-column  
- ตรวจสอบว่า Extended Statistics ช่วยได้จริง

## 4. เนื้อหาโดยย่อ
Planner ใช้ Statistics ในการประมาณ `rows`  
Statistics พื้นฐานได้จาก:
- `ANALYZE`  
- Autovacuum Analyze  
- `default_statistics_target`

Extended Statistics ใช้เมื่อ:
- หลายคอลัมน์มี Correlation  
- Planner ประมาณผิดมาก  
- `Rows Estimate ≠ Actual` หลายเท่า

## 5. ประโยชน์ที่ได้รับ
- Planner เลือกแผนถูก  
- Query เร็วขึ้น  
- ลด Seq Scan ที่ไม่จำเป็น  
- ลด Memory ที่ใช้ผิด

## 6. ข้อควรระวัง
- **Statistics เก่า** ทำให้ Planner เลือกผิด  
- **Extended Statistics ต้อง `ANALYZE` หลังสร้าง**  
- **`pg_upgrade` ไม่โอน Extended Statistics**  
- **Autovacuum Analyze ที่ตัวแม่ของ Partitioned Table ไม่ทำงาน**  
- **`default_statistics_target` สูงเกินไปทำให้ ANALYZE นาน**

## 7. ข้อดี
- Planner แม่นยำขึ้น  
- ลด Query ที่ช้า  
- ใช้ `pg_stats_ext` ตรวจสอบได้

## 8. ข้อเสีย
- ANALYZE ใช้เวลานานขึ้น  
- Extended Statistics ไม่โอนตอน Upgrade  
- ต้อง ANALYZE เองหลังสร้าง

## 9. ข้อห้าม
- ห้ามปิด Autovacuum Analyze  
- ห้ามลบ Extended Statistics โดยไม่ตรวจ  
- ห้ามใช้ `default_statistics_target = 10000` โดยไม่จำเป็น  
- ห้ามลืม `ANALYZE` หลัง `pg_upgrade`  
- ห้ามใช้ Extended Statistics แทน Index

## 10. รายละเอียด

### 10.1 ตรวจสอบ Statistics

```sql
SELECT attname, n_distinct, correlation
FROM pg_stats
WHERE schemaname = 'gridcare' AND tablename = 'customers'
ORDER BY attname;
```

ผลลัพธ์:
```text
   attname   | n_distinct | correlation 
-------------+------------+-------------
 ca_number   |         -1 |        0.02
 customer_id |         -1 |        1.00
 office_id   |         42 |        0.05
 status      |          3 |        0.12
```

- `n_distinct = -1` = จำนวนไม่ซ้ำเท่ากับจำนวนแถว  
- `correlation = 1.00` = เรียงตรงกับ Physical Order

### 10.2 `ANALYZE`

```sql
ANALYZE gridcare.customers;
```

ผลลัพธ์:
```text
ANALYZE
```

### 10.3 ปัญหา: Rows Estimate ผิด

```sql
EXPLAIN (ANALYZE, TIMING OFF)
SELECT count(*) FROM gridcare.bills
WHERE billing_period = '2026-09-01' AND status = 'UNPAID';
```

ผลลัพธ์ (ก่อน Extended Statistics):
```text
               ->  Parallel Seq Scan on bills
                     (cost=0.00..7933.85 rows=13897 width=0) (actual time=0.234..42.123 rows=0 loops=3)
                     Filter: ((billing_period = '2026-09-01'::date) AND (status = 'UNPAID'::bpchar))
                     Rows Removed by Filter: 33333
```

> ⚠️ ประมาณ `rows=13897` แต่จริง `rows=0`

### 10.4 สร้าง Extended Statistics

```sql
CREATE STATISTICS bills_period_status (mcv) ON billing_period, status FROM gridcare.bills;
ANALYZE gridcare.bills;
```

ผลลัพธ์:
```text
CREATE STATISTICS
ANALYZE
```

### 10.5 ตรวจสอบผล

```sql
EXPLAIN (ANALYZE, TIMING OFF)
SELECT count(*) FROM gridcare.bills
WHERE billing_period = '2026-09-01' AND status = 'UNPAID';
```

ผลลัพธ์ (หลัง):
```text
               ->  Parallel Seq Scan on bills
                     (cost=0.00..7933.85 rows=300 width=0) (actual time=0.012..0.034 rows=0 loops=3)
                     Rows Removed by Filter: 0
```

> ✅ ประมาณจาก 13,897 → 300 (ใกล้จริง 46 เท่า)

### 10.6 ดู Extended Statistics

```sql
SELECT statistics_name, attnames, kinds
FROM pg_stats_ext WHERE tablename = 'bills';
```

ผลลัพธ์:
```text
    statistics_name    |        attnames         | kinds 
-----------------------+-------------------------+-------
 bills_period_status   | {billing_period,status} | {mcv}
```

### 10.7 Kind ของ Extended Statistics

| Kind | ใช้เมื่อ |
|---|---|
| `mcv` | Multivariate Most Common Values |
| `dependencies` | Functional Dependency |
| `ndistinct` | Multivariate Distinct Count |

### 10.8 `default_statistics_target`

```sql
SHOW default_statistics_target;
```

ผลลัพธ์:
```text
 default_statistics_target 
---------------------------
                       100
```

> 💡 `100` เป็นค่าที่เหมาะกับงานทั่วไป  
> เพิ่มเป็น `500`–`1000` สำหรับคอลัมน์ที่ `Rows Estimate ≠ Actual` มาก

### 10.9 หลัง `pg_upgrade` ต้อง ANALYZE

```bash
sudo -u postgres /usr/lib/postgresql/18/bin/vacuumdb --all --analyze-in-stages --missing-stats-only
sudo -u postgres /usr/lib/postgresql/18/bin/vacuumdb --all --analyze-only --jobs 2
```

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: ตรวจสอบว่า Statistics เก่า

```sql
SELECT schemaname, relname, last_analyze, last_autoanalyze
FROM pg_stat_user_tables
WHERE schemaname = 'gridcare'
ORDER BY last_analyze NULLS FIRST;
```

ผลลัพธ์:
```text
 schemaname |     relname     |       last_analyze      |     last_autoanalyze     
------------+-----------------+-------------------------+--------------------------
 gridcare   | bills           | 2026-11-03 09:45:15+07  | 2026-11-03 09:45:12+07
 gridcare   | customers       | 2026-11-02 09:00:00+07  | 2026-11-02 09:00:05+07
```

### ตัวอย่างที่ 2: สร้าง Extended Statistics ที่ได้ผล

```sql
CREATE STATISTICS bills_period_status (mcv) ON billing_period, status FROM gridcare.bills;
ANALYZE gridcare.bills;
SELECT statistics_name, attnames, kinds FROM pg_stats_ext WHERE tablename = 'bills';
```

ผลลัพธ์:
```text
    statistics_name    |        attnames         | kinds 
-----------------------+-------------------------+-------
 bills_period_status   | {billing_period,status} | {mcv}
```

### ตัวอย่างที่ 3: ตรวจสอบ Extended Statistics หลัง Upgrade

```sql
SELECT statistics_name FROM pg_stats_ext;
```

ผลลัพธ์ (หลัง `vacuumdb --missing-stats-only`):
```text
 statistics_name 
-----------------
 bills_period_status
```

> ⚠️ ถ้าว่างแสดงว่า Extended Statistics ไม่ถูกโอน ต้องสร้างใหม่

## 12. สรุปย่อ จำง่าย
- **Planner ใช้ Statistics ในการประมาณ `rows`**  
- **`ANALYZE` อัปเดต Statistics**  
- **Extended Statistics ใช้กับ Multi-column ที่ Correlation**  
- **`mcv`, `dependencies`, `ndistinct`**  
- **`default_statistics_target = 100`** เหมาะกับงานทั่วไป  
- **หลัง `pg_upgrade` ต้อง ANALYZE**  
- **ตรวจ `Rows Estimate vs Actual`**

ประโยคจำ: **“Statistics ผิด Planner ก็ผิด Query ก็ช้า”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — Statistics Used by the Planner: https://www.postgresql.org/docs/17/planner-stats.html
- PostgreSQL Documentation — Extended Statistics: https://www.postgresql.org/docs/17/planner-stats.html#PLANNER-STATS-EXTENDED
- PostgreSQL Documentation — CREATE STATISTICS: https://www.postgresql.org/docs/17/sql-createstatistics.html
- GridCare Workshop Day 2: Lab 1.1, Day 5: Lab 1.2

---

# บทที่ 28 Partitioning เบื้องต้น

## 1. เรื่อง
Partitioning ใน PostgreSQL 17/18 ด้วย Declarative Partitioning และ pg_partman

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจ Declarative Partitioning  
2. เพื่อให้เลือก Partition Strategy (Range, List, Hash)  
3. เพื่อให้สร้าง Partition ด้วย pg_partman  
4. เพื่อให้ตั้ง Autovacuum สำหรับ Partition

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ออกแบบ Partition Strategy  
- สร้าง Partition ด้วย SQL และ pg_partman  
- ตั้ง Autovacuum ที่ Template  
- ตั้ง systemd timer สำหรับ pg_partman  
- ตรวจสอบ Partition ด้วย `pg_inherits`

## 4. เนื้อหาโดยย่อ
Partition Strategy:
- **Range** — เหมาะกับวันที่, ตัวเลข  
- **List** — เหมาะกับค่าที่จำกัด  
- **Hash** — เหมาะกับการกระจายตัว

pg_partman เป็น Extension ที่:
- สร้าง Partition ล่วงหน้า  
- ลบ Partition เก่า  
- รัน Maintenance อัตโนมัติ

Autovacuum:
- ตั้งที่ Partition ลูก ไม่ใช่ตัวแม่  
- ตั้งที่ Template Table เพื่อให้ Partition ใหม่ได้ค่าด้วย

## 5. ประโยชน์ที่ได้รับ
- Query เร็วขึ้นเพราะอ่านเฉพาะ Partition ที่เกี่ยว  
- ลด Index Size  
- ลบข้อมูลเก่าง่าย (`DROP PARTITION`)  
- Autovacuum ทำงานได้เหมาะกับแต่ละ Partition

## 6. ข้อควรระวัง
- **ตั้ง Autovacuum ที่ตัวแม่ไม่ได้**  
- **`pg_upgrade` ไม่โอน Extended Statistics**  
- **Autovacuum Analyze ที่ตัวแม่ไม่ทำงาน**  
- **ต้องตั้ง `run_maintenance_proc()` ให้รันอัตโนมัติ**  
- **ต้องตรวจ `default` Partition ไม่ให้มีข้อมูล**

## 7. ข้อดี
- Query เร็วขึ้น  
- ลบข้อมูลเก่าง่าย  
- ลด Index Size  
- Autovacuum ทำงานเฉพาะ Partition

## 8. ข้อเสีย
- Partition ไม่ช่วยเรื่อง Join ข้าม Partition  
- ต้องตั้ง Maintenance  
- การสลับ Table เป็น Partition ต้อง Lock สั้น

## 9. ข้อห้าม
- ห้ามตั้ง Autovacuum ที่ตัวแม่  
- ห้าม `DROP PARTITION` โดยไม่ Archive  
- ห้ามลืมตั้ง `run_maintenance_proc()`  
- ห้ามใช้ `default` Partition เป็นที่เก็บข้อมูลหลัก  
- ห้ามสร้าง Partition ที่มี Key ไม่ตรงกับตัวแม่

## 10. รายละเอียด

### 10.1 ตัวอย่าง Range Partition

```sql
CREATE TABLE gridcare.meter_readings (
    meter_id      integer       NOT NULL,
    read_at       timestamptz   NOT NULL,
    kwh           numeric(10,3) NOT NULL,
    voltage       numeric(6,2),
    quality_flag  char(1)       NOT NULL DEFAULT 'G',
    PRIMARY KEY (meter_id, read_at)
) PARTITION BY RANGE (read_at);
```

### 10.2 pg_partman — `create_parent`

```sql
CREATE EXTENSION IF NOT EXISTS pg_partman SCHEMA partman;

SELECT partman.create_parent(
    p_parent_table    := 'gridcare.meter_readings',
    p_control         := 'read_at',
    p_interval        := '1 day',
    p_premake         := 7,
    p_start_partition := (SELECT date_trunc('day', min(read_at))::text FROM meter_readings_old)
);
```

ผลลัพธ์:
```text
 create_parent 
---------------
 
```

### 10.3 ตรวจสอบ Partition

```sql
SELECT count(*) AS partitions
FROM pg_inherits
WHERE inhparent = 'gridcare.meter_readings'::regclass;
```

ผลลัพธ์:
```text
 partitions 
------------
         23
```

```sql
SELECT count(*) AS rows_in_default
FROM gridcare.meter_readings_default;
```

ผลลัพธ์:
```text
 rows_in_default 
-----------------
               0
```

### 10.4 ตั้ง Autovacuum ที่ Template

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

### 10.5 ตั้ง Autovacuum ที่ Partition ที่มีอยู่

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

### 10.6 systemd timer สำหรับ pg_partman

**`/etc/systemd/system/gridcare-partman.service`:**
```ini
[Unit]
Description=GridCare pg_partman maintenance
[Service]
Type=oneshot
User=postgres
ExecStart=/usr/bin/psql -X -v ON_ERROR_STOP=1 -d gridcare -c "CALL partman.run_maintenance_proc()"
```

**`/etc/systemd/system/gridcare-partman.timer`:**
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
sudo systemctl daemon-reload
sudo systemctl enable --now gridcare-partman.timer
systemctl list-timers 'gridcare-*' --no-pager
```

ผลลัพธ์:
```text
NEXT                        LEFT       LAST                        PASSED    UNIT                    ACTIVATES
Tue 2026-11-03 11:00:00 +07 14min left n/a                         n/a       gridcare-partman.timer  gridcare-partman.service
```

### 10.7 BRIN Index บน Partition

```sql
CREATE INDEX meter_readings_read_at_brin ON gridcare.meter_readings USING brin (read_at);
```

### 10.8 ตารางเลือก Strategy

| ข้อมูล | Strategy | ตัวอย่าง |
|---|---|---|
| วันที่ | Range | `read_at` รายวัน |
| ตัวเลขที่เรียง | Range | `customer_id` |
| ค่าที่จำกัด | List | `region_id` |
| กระจายตัว | Hash | `meter_id` |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: สร้าง Partition Range รายวัน

```sql
BEGIN;
SET LOCAL lock_timeout = '3s';
ALTER TABLE gridcare.meter_readings RENAME TO meter_readings_old;
ALTER TABLE gridcare.meter_readings_old RENAME CONSTRAINT meter_readings_pkey TO meter_readings_old_pkey;

CREATE TABLE gridcare.meter_readings (
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

GRANT INSERT ON gridcare.meter_readings TO gridcare_write;
ALTER TABLE gridcare.meter_readings ADD CONSTRAINT meter_readings_meter_fk
    FOREIGN KEY (meter_id) REFERENCES gridcare.meters (meter_id);
CREATE INDEX meter_readings_read_at_brin ON gridcare.meter_readings USING brin (read_at);
COMMIT;
```

### ตัวอย่างที่ 2: ตรวจสอบ Partition หลังสร้าง

```sql
SELECT count(*) AS partitions FROM pg_inherits WHERE inhparent = 'gridcare.meter_readings'::regclass;
SELECT count(*) AS rows_in_default FROM gridcare.meter_readings_default;
SELECT (SELECT count(*) FROM gridcare.meter_readings_old) AS old_rows,
       (SELECT count(*) FROM gridcare.meter_readings
         WHERE read_at <= (SELECT max(read_at) FROM gridcare.meter_readings_old)) AS moved_rows;
```

ผลลัพธ์:
```text
 partitions | 23
 rows_in_default | 0
 old_rows | moved_rows 
----------+------------
  7200000 |    7200000
```

### ตัวอย่างที่ 3: Query ที่อ่านเฉพาะ Partition

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT date_trunc('hour', read_at) AS hour,
       count(*) AS readings,
       count(DISTINCT meter_id) AS meters
FROM gridcare.meter_readings
WHERE read_at >= now() - interval '3 hours'
GROUP BY 1 ORDER BY 1;
```

ผลลัพธ์:
```text
 GroupAggregate  (cost=1234.56..1250.00 rows=3 width=16) (actual time=4.567..4.678 rows=3)
   Group Key: (date_trunc('hour'::text, meter_readings.read_at))
   ->  Sort  (actual time=4.123..4.234 rows=3000)
         ->  Append  (actual time=0.045..3.789 rows=3000)
               ->  Index Scan using meter_readings_p20261103_read_at_brin on meter_readings_p20261103
                     (actual time=0.045..3.789 rows=3000 loops=1)
                     Index Cond: (read_at >= (now() - '03:00:00'::interval))
```

> ✅ อ่านเฉพาะ `meter_readings_p20261103` (Partition ของวันนี้)

## 12. สรุปย่อ จำง่าย
- **Declarative Partitioning = PARTITION BY RANGE / LIST / HASH**  
- **pg_partman = Extension ที่ช่วยสร้าง Partition ล่วงหน้า**  
- **Autovacuum ตั้งที่ Partition ลูก ไม่ใช่ตัวแม่**  
- **BRIN เหมาะกับ Time-series**  
- **ต้องตั้ง `run_maintenance_proc()` ให้รันอัตโนมัติ**  
- **ตรวจ `pg_inherits` และ `default` Partition**

ประโยคจำ: **“Partition ที่ดีทำให้อ่านเร็ว ลบง่าย Autovacuum ทำงานได้”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — Table Partitioning: https://www.postgresql.org/docs/17/ddl-partitioning.html
- pg_partman: https://github.com/pgpartman/pg_partman
- GridCare Workshop Day 2: Workshop Day 2 ขั้นที่ 2, 3

---

# บทที่ 29 Backup เบื้องต้นด้วย pg_dump

## 1. เรื่อง
การ Backup ด้วย `pg_dump` และ `pg_dumpall` สำหรับงานประจำวันและการ Migrate

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจความแตกต่างระหว่าง Logical และ Physical Backup  
2. เพื่อให้ใช้ `pg_dump` ได้อย่างมีประสิทธิภาพ  
3. เพื่อให้เลือก Format และ Options ที่เหมาะ  
4. เพื่อให้ Backup Role และ Tablespace

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- เลือก Format: plain, custom, directory, tar  
- ใช้ `-Fd -j 2 -Z zstd:3` สำหรับ Backup ขนาดใหญ่  
- ใช้ `pg_dumpall --globals-only`  
- Restore บางส่วนด้วย `-L`  
- วางแผน Backup Strategy

## 4. เนื้อหาโดยย่อ
`pg_dump` — Logical Backup ของ Database เดียว  
`pg_dumpall` — Backup ทั้ง Cluster รวม Role  
Format:
- **plain** — SQL Script  
- **custom** — Compressed, Restore ได้บางส่วน  
- **directory** — Parallel Backup (`-j`)  
- **tar** — ไม่แนะนำ

ข้อดีของ Logical:
- Portable  
- Restore บางส่วนได้  
- ใช้กับ Version ต่างกันได้ (ส่วนใหญ่)

## 5. ประโยชน์ที่ได้รับ
- Migrate ระหว่าง Version  
- Restore บางส่วน  
- Backup Role  
- Backup ขนาดเล็ก

## 6. ข้อควรระวัง
- **`pg_dump` ไม่ใช่ Physical Backup**  
- **`pg_dump` ใช้ Snapshot เดียว** แต่ใช้เวลานาน  
- **`-Fd -j 2`** ต้องใช้ `pg_restore`  
- **`pg_dumpall --globals-only`** ต้องใช้ `--no-role-passwords`  
- **Long Running Backup** อาจทำให้ Bloat

## 7. ข้อดี
- Portable  
- Restore บางส่วน  
- ใช้ Version ต่างกันได้  
- Backup Role

## 8. ข้อเสีย
- ช้ากว่า Physical  
- Backup ใหญ่  
- ไม่ได้ WAL Archive

## 9. ข้อห้าม
- ห้ามใช้ `pg_dump` เป็น Backup เดียว  
- ห้าม Backup ด้วย Superuser ใน Script Production  
- ห้าม Restore ทับ Production โดยไม่มี Plan  
- ห้าม Backup โดยไม่ตรวจ Restore  
- ห้ามใช้ `-Fc` กับ Backup ที่ต้องการ Restore บางส่วนบ่อย ๆ (ใช้ `-Fd` ดีกว่า)

## 10. รายละเอียด

### 10.1 `pg_dump` พื้นฐาน

```bash
sudo install -d -o postgres -g postgres -m 700 /var/backups/gridcare
sudo -u postgres pg_dump -d gridcare -Fc -f /var/backups/gridcare/gc.custom
```

ผลลัพธ์:
```text
(ไม่มี output = สำเร็จ)
```

### 10.2 `pg_dump` แบบ Directory + Parallel + zstd

```bash
time sudo -u postgres pg_dump -d gridcare -Fd -j 2 -Z zstd:3 -f /var/backups/gridcare/gc.dir
sudo du -sh /var/backups/gridcare/gc.dir
```

ผลลัพธ์:
```text
real    0m9.234s

192M    /var/backups/gridcare/gc.dir
```

### 10.3 `pg_dumpall --globals-only`

```bash
sudo -u postgres pg_dumpall --globals-only --no-role-passwords \
  | sudo -u postgres tee /var/backups/gridcare/globals.sql > /dev/null
sudo grep -c "CREATE ROLE" /var/backups/gridcare/globals.sql
```

ผลลัพธ์:
```text
10
```

### 10.4 Restore บางส่วน

```bash
sudo -u postgres pg_restore -l /var/backups/gridcare/gc.dir \
  | grep -E "TABLE DATA gridcare (tariff_rates|regions) "
```

ผลลัพธ์:
```text
3975; 0 16386 TABLE DATA gridcare regions postgres
3977; 0 16405 TABLE DATA gridcare tariff_rates postgres
```

สร้าง `partial.list`:
```bash
sudo -u postgres bash -c "pg_restore -l /var/backups/gridcare/gc.dir | grep -E ' (SCHEMA - gridcare|TABLE gridcare (tariff_rates|regions)|TABLE DATA gridcare (tariff_rates|regions)) ' > /var/backups/gridcare/partial.list"
sudo cat /var/backups/gridcare/partial.list
```

ผลลัพธ์:
```text
3968; 0 16386 SCHEMA - gridcare postgres
3974; 0 16386 TABLE gridcare regions postgres
3975; 0 16386 TABLE DATA gridcare regions postgres
3976; 0 16405 TABLE gridcare tariff_rates postgres
3977; 0 16405 TABLE DATA gridcare tariff_rates postgres
```

Restore:
```bash
sudo -u postgres createdb gridcare_restore
sudo -u postgres pg_restore -d gridcare_restore -L /var/backups/gridcare/partial.list \
  --no-owner /var/backups/gridcare/gc.dir
sudo -u postgres psql -X -d gridcare_restore -c "SELECT tariff_code, rate_per_kwh FROM gridcare.tariff_rates ORDER BY 1" -c "\dt gridcare.*"
```

ผลลัพธ์:
```text
 tariff_code | rate_per_kwh 
-------------+--------------
 GOV         |         4.20
 RES         |         3.90
 SMB         |         4.50
(3 rows)

          List of relations
 Schema  |     Name     | Type  | Owner 
---------+--------------+-------+-------
 gridcare| regions      | table | postgres
 gridcare| tariff_rates | table | postgres
(2 rows)
```

```bash
sudo -u postgres dropdb gridcare_restore
```

### 10.5 ตาราง Format

| Format | ใช้เมื่อ | Parallel | Restore บางส่วน |
|---|---|---|---|
| plain (`.sql`) | ต้องการอ่าน/แก้ | ❌ | ❌ |
| custom (`-Fc`) | Backup ปกติ | ❌ | ✅ |
| directory (`-Fd`) | Backup ใหญ่ | ✅ (`-j`) | ✅ |
| tar (`-Ft`) | ไม่แนะนำ | ❌ | ✅ |

### 10.6 Strategy ที่แนะนำ

```text
Logical Backup (pg_dump -Fd -j 2 -Z zstd:3)
    └── รายวันหรือรายสัปดาห์ + เก็บ 7-30 วัน

Globals Backup (pg_dumpall --globals-only --no-role-passwords)
    └── ทุกครั้งที่มีการเปลี่ยน Role

Physical Backup (pgBackRest)
    └── รายวัน + WAL Archive สำหรับ PITR

Restore Test
    └── รายเดือน
```

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Backup ขนาดเล็ก

```bash
sudo -u postgres pg_dump -d gridcare -Fc -f /var/backups/gridcare/gc.custom
ls -lh /var/backups/gridcare/gc.custom
```

ผลลัพธ์:
```text
-rw-r--r-- 1 postgres postgres 192M Nov  4 09:15 /var/backups/gridcare/gc.custom
```

### ตัวอย่างที่ 2: Backup เฉพาะตาราง

```bash
sudo -u postgres pg_dump -d gridcare -t gridcare.tariff_rates -Fc \
  -f /var/backups/gridcare/tariff_rates.custom
```

### ตัวอย่างที่ 3: Backup เฉพาะ Schema

```bash
sudo -u postgres pg_dump -d gridcare -n gridcare -Fc \
  -f /var/backups/gridcare/schema_gridcare.custom
```

### ตัวอย่างที่ 4: ตรวจสอบ Backup ด้วย `pg_restore -l`

```bash
sudo -u postgres pg_restore -l /var/backups/gridcare/gc.dir | head -5
```

ผลลัพธ์:
```text
;
; Archive created at 2026-11-04 09:15:23 +07
;     dbname: gridcare
;     TOC Entries: 234
;     Compression: zstd
...
```

### ตัวอย่างที่ 5: Restore ขนาดเล็ก

```bash
sudo -u postgres createdb gridcare_restore
sudo -u postgres pg_restore -d gridcare_restore --no-owner /var/backups/gridcare/gc.custom
sudo -u postgres psql -X -d gridcare_restore -c "SELECT count(*) FROM gridcare.bills"
```

ผลลัพธ์:
```text
  count  
---------
 1200000
```

## 12. สรุปย่อ จำง่าย
- **`pg_dump` = Logical Backup**  
- **`-Fd -j 2 -Z zstd:3`** สำหรับ Backup ใหญ่  
- **`pg_dumpall --globals-only --no-role-passwords`** สำหรับ Role  
- **`pg_restore -L`** Restore บางส่วน  
- **ต้องมี Restore Test**  
- **`pg_dump` ไม่ใช่ Backup เดียว**

ประโยคจำ: **“Backup ที่ดีคือ Backup ที่ Restore ได้”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — pg_dump: https://www.postgresql.org/docs/17/app-pgdump.html
- PostgreSQL Documentation — pg_dumpall: https://www.postgresql.org/docs/17/app-pg-dumpall.html
- PostgreSQL Documentation — pg_restore: https://www.postgresql.org/docs/17/app-pgrestore.html
- GridCare Workshop Day 3: Lab 2.1

---

# บทที่ 30 Restore และตรวจสอบผล

## 1. เรื่อง
การ Restore จาก `pg_dump` และ `pg_restore` พร้อมการตรวจสอบผลหลัง Restore

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้ Restore ได้ถูกต้อง  
2. เพื่อให้ตรวจสอบผลหลัง Restore  
3. เพื่อให้ Restore บางส่วนได้  
4. เพื่อให้ใช้เป็นหลักฐานใน Restore Test

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- Restore จาก `-Fc` และ `-Fd`  
- Restore บางส่วนด้วย `-L`  
- ตรวจสอบ Row Count หลัง Restore  
- ตรวจสอบ Index และ Constraint  
- สร้าง Restore Report

## 4. เนื้อหาโดยย่อ
ขั้นตอน Restore:
1. สร้าง Database เปล่า  
2. `pg_restore`  
3. ตรวจสอบ Row Count  
4. ตรวจสอบ Index  
5. ตรวจสอบ Constraint  
6. ตรวจสอบ Extended Statistics  
7. Verify ด้วย `pg_checksums` (ถ้าเป็น Physical)  
8. สร้าง Report

## 5. ประโยชน์ที่ได้รับ
- มั่นใจว่า Backup ใช้ได้จริง  
- ลดความเสี่ยงเมื่อเกิด Incident  
- มี RTO ที่วัดได้จริง  
- มีหลักฐานสำหรับ Audit

## 6. ข้อควรระวัง
- **Restore ทับ Production** ต้องมี Plan  
- **`--no-owner`** ทำให้ Owner เป็น User ที่ Restore  
- **Role ต้องมีก่อน Restore**  
- **Extension ต้องติดตั้งก่อน**  
- **ตรวจ `pg_checksums`** หลัง Physical Restore

## 7. ข้อดี
- มั่นใจใน Backup  
- มี RTO ที่วัดได้  
- มี Evidence

## 8. ข้อเสีย
- ใช้เวลานาน  
- ต้องมี Disk เพียงพอ  
- ต้องมี Role ครบ

## 9. ข้อห้าม
- ห้าม Restore ทับ Production โดยไม่มี Plan  
- ห้าม Restore โดยไม่มี Role  
- ห้าม Restore โดยไม่ตรวจสอบผล  
- ห้ามลบ Backup ก่อน Restore Test  
- ห้าม Restore บน Production โดยไม่หยุดแอป

## 10. รายละเอียด

### 10.1 Restore จาก `-Fc`

```bash
sudo -u postgres createdb gridcare_restore
sudo -u postgres pg_restore -d gridcare_restore --no-owner /var/backups/gridcare/gc.custom
```

ผลลัพธ์:
```text
(ไม่มี output = สำเร็จ)
```

### 10.2 Restore จาก `-Fd`

```bash
sudo -u postgres pg_restore -d gridcare_restore -j 2 --no-owner /var/backups/gridcare/gc.dir
```

### 10.3 Restore บางส่วนด้วย `-L`

```bash
sudo -u postgres pg_restore -d gridcare_restore -L /var/backups/gridcare/partial.list \
  --no-owner /var/backups/gridcare/gc.dir
```

### 10.4 ตรวจสอบ Row Count

```sql
SELECT 'bills' AS table_name, count(*) FROM gridcare.bills
UNION ALL
SELECT 'customers', count(*) FROM gridcare.customers
UNION ALL
SELECT 'meter_readings', count(*) FROM gridcare.meter_readings;
```

ผลลัพธ์:
```text
   table_name   |  count  
----------------+---------
 bills          | 1200000
 customers      |  200000
 meter_readings | 7200000
```

### 10.5 ตรวจสอบ Index

```sql
SELECT c.relname AS index_name, i.indisvalid
FROM pg_index AS i
JOIN pg_class AS c ON c.oid = i.indexrelid
JOIN pg_namespace AS n ON n.oid = c.relnamespace
WHERE n.nspname = 'gridcare'
ORDER BY c.relname;
```

### 10.6 ตรวจสอบ Constraint

```sql
SELECT conrelid::regclass AS table_name, conname, convalidated
FROM pg_constraint
WHERE connamespace = 'gridcare'::regnamespace
ORDER BY conrelid, conname;
```

### 10.7 ตรวจสอบ Extended Statistics

```sql
SELECT statistics_name, attnames, kinds FROM pg_stats_ext;
```

ผลลัพธ์ (หลัง Restore ปกติ):
```text
    statistics_name    |        attnames         | kinds 
-----------------------+-------------------------+-------
 bills_period_status   | {billing_period,status} | {mcv}
```

> ⚠️ ถ้าว่างแสดงว่า Extended Statistics ไม่ถูกโอน ต้องสร้างใหม่

### 10.8 ตรวจสอบ Checksums (Physical Restore)

```bash
sudo -u postgres /usr/lib/postgresql/17/bin/pg_checksums --verify -D /var/tmp/gc-restore-test
echo "exit=$?"
```

ผลลัพธ์:
```text
Checksum operation completed
Files scanned:   1234
Blocks scanned:  567890
Bad checksums:   0
exit=0
```

### 10.9 Restore Report Template

```text
Restore Test Report
Date       : 2026-11-04
Backup     : /var/backups/gridcare/gc.dir (2026-11-04 09:15)
Target     : gridcare_restore
Started    : 13:05:00
Finished   : 13:05:52
Duration   : 52s
RTO        : 52s

Row Count:
  bills          : 1200000 (expected 1200000) OK
  customers      : 200000  (expected 200000)  OK
  meter_readings : 7200000 (expected 7200000) OK

Indexes       : 45/45 valid
Constraints   : 23/23 validated
Extended Stats: 1/1 present

Checksums     : 0 bad
Exit Code     : 0

Conclusion    : PASS
```

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Restore และตรวจสอบแบบครบ

```bash
sudo -u postgres createdb gridcare_restore
time sudo -u postgres pg_restore -d gridcare_restore -j 2 --no-owner /var/backups/gridcare/gc.dir
sudo -u postgres psql -X -d gridcare_restore -c "SELECT count(*) FROM gridcare.bills" -c "SELECT count(*) FROM gridcare.customers"
```

ผลลัพธ์:
```text
real    0m52.345s

  count  
---------
 1200000

  count  
---------
  200000
```

### ตัวอย่างที่ 2: ตรวจสอบ Index ที่ไม่ Valid

```sql
SELECT c.relname AS index_name, i.indisvalid
FROM pg_index AS i
JOIN pg_class AS c ON c.oid = i.indexrelid
JOIN pg_namespace AS n ON n.oid = c.relnamespace
WHERE n.nspname = 'gridcare' AND NOT i.indisvalid;
```

ผลลัพธ์ (ถ้าปกติ):
```text
 index_name | indisvalid 
------------+------------
(0 rows)
```

### ตัวอย่างที่ 3: Restore บางส่วน

```bash
sudo -u postgres createdb gridcare_restore
sudo -u postgres pg_restore -d gridcare_restore -L /var/backups/gridcare/partial.list \
  --no-owner /var/backups/gridcare/gc.dir
sudo -u postgres psql -X -d gridcare_restore -c "SELECT tariff_code, rate_per_kwh FROM gridcare.tariff_rates ORDER BY 1" -c "\dt gridcare.*"
```

ผลลัพธ์:
```text
 tariff_code | rate_per_kwh 
-------------+--------------
 GOV         |         4.20
 RES         |         3.90
 SMB         |         4.50
(3 rows)

          List of relations
 Schema  |     Name     | Type  | Owner 
---------+--------------+-------+-------
 gridcare| regions      | table | postgres
 gridcare| tariff_rates | table | postgres
(2 rows)
```

```bash
sudo -u postgres dropdb gridcare_restore
```

### ตัวอย่างที่ 4: Restore Test Script

```bash
sudo -u postgres MODE=pgbackrest STANZA=gridcare ./restore_test.sh; echo "exit=$?"
```

ผลลัพธ์:
```text
[2026-11-04 13:05:00] INFO: Starting restore test mode=pgbackrest
[2026-11-04 13:05:30] INFO: restore completed
[2026-11-04 13:05:45] INFO: Test cluster ready
[2026-11-04 13:05:46] INFO: Checking bills count >= 1000000
[2026-11-04 13:05:47] INFO: Stopping test cluster
[2026-11-04 13:05:52] PASS restore test (pgbackrest) ใช้เวลา 7 วินาที
exit=0
```

## 12. สรุปย่อ จำง่าย
- **Restore = Create DB + pg_restore + Verify**  
- **`-L`** Restore บางส่วน  
- **`--no-owner`** ทำให้ Owner เป็น User ที่ Restore  
- **ตรวจ Row Count, Index, Constraint, Extended Stats**  
- **`pg_checksums --verify`** หลัง Physical Restore  
- **ทุก Restore ต้องมี Report**

ประโยคจำ: **“Restore Test ที่ดีคือ Restore Test ที่มี Report และ Exit Code”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — pg_restore: https://www.postgresql.org/docs/17/app-pgrestore.html
- PostgreSQL Documentation — pg_checksums: https://www.postgresql.org/docs/17/app-pgchecksums.html
- GridCare Workshop Day 3: Lab 2.1, Lab 4.1

---

## สรุปส่วนที่ 3 (บทที่ 21–30)

| บท | แก่นของบท | ใช้ต่อในส่วน |
|---|---|---|
| 21 | psql + Meta-command + `\gset` + `\gexec` + `\copy` | ทุกส่วน |
| 22 | DDL/DML + Transaction + `lock_timeout` + UPSERT | Migration |
| 23 | MVCC + Isolation Level + `xmin`/`xmax` + Retry | Lock, Bloat |
| 24 | Lock Mode + คิว Lock + `pg_blocking_pids` | Migration, S troubleshooting |
| 25 | `EXPLAIN` + `EXPLAIN ANALYZE` + `BUFFERS` + Rows Estimate | Performance |
| 26 | Index: B-tree, BRIN, Partial, Expression + `CONCURRENTLY` | Performance |
| 27 | Statistics + Extended Statistics + `ANALYZE` | Performance, Upgrade |
| 28 | Partitioning + pg_partman + Autovacuum ที่ Template | Performance, Maintenance |
| 29 | `pg_dump` + `pg_dumpall` + Format + Restore บางส่วน | Backup |
| 30 | `pg_restore` + ตรวจสอบผล + Restore Report | Backup, Restore Test |

---
 