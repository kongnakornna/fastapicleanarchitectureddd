# 📋 สรุปคำสั่งทั้งหมด — Day 5 (วันที่ 5)

> **หลักสูตร:** Advanced PostgreSQL for Enterprise Production (PEA)
> **หัวข้อ:** Upgrade, Safe Schema Change, Troubleshooting, Kubernetes & Game Day
> **วันที่:** ศุกร์ที่ 6 พฤศจิกายน 2569 | 09:00-16:30 น.
> รูปแบบ: **คำสั่ง** → **ผลลัพธ์จริง/ที่คาดหวัง** → **หมายเหตุ**

---

## 🧪 Lab 1.1 — เตรียมรุ่น 18 และตรวจความพร้อมด้วย `pg_upgrade --check`

### บน pg1 และ pg2

### ขั้นที่ 1: ติดตั้ง PostgreSQL 18 + Extensions

```bash
sudo apt install -y postgresql-18 postgresql-18-pgaudit postgresql-18-partman postgresql-18-repack
pg_lsclusters
```
**ผลลัพธ์:**
```
Ver Cluster Port Status Owner    Data directory              Log file
17  main    5432 online postgres /var/lib/postgresql/17/main /var/log/postgresql/postgresql-17-main.log
18  main    5432 down   postgres /var/lib/postgresql/18/main /var/log/postgresql/postgresql-18-main.log
```

### ขั้นที่ 2: หยุดคลัสเตอร์ 18 และตั้ง `start.conf = manual`

```bash
sudo systemctl stop postgresql@18-main 2>/dev/null; echo manual | sudo tee /etc/postgresql/18/main/start.conf
```
**ผลลัพธ์:**
```
manual
```

### ขั้นที่ 3: คัดลอกค่าตั้งและใบรับรอง

```bash
sudo cp /etc/postgresql/17/main/conf.d/*.conf /etc/postgresql/18/main/conf.d/
sudo cp /etc/postgresql/17/main/server.crt /etc/postgresql/17/main/server.key /etc/postgresql/18/main/
sudo sed -i 's#/etc/postgresql/17/main/server#/etc/postgresql/18/main/server#' /etc/postgresql/18/main/conf.d/30-gridcare-ssl.conf
sudo chown -R postgres:postgres /etc/postgresql/18/main
sudo chmod 600 /etc/postgresql/18/main/server.key
sudo -u postgres /usr/lib/postgresql/18/bin/pg_controldata /var/lib/postgresql/18/main | grep -i checksum
```
**ผลลัพธ์:**
```
Data page checksum version:           1
```

### ขั้นที่ 4: ตรวจสอบ Extension ที่ติดตั้งในรุ่น 17

**บน pg1 (Primary) เท่านั้น:**
```bash
sudo -u postgres psql -X -d gridcare -c "SELECT extname, extversion FROM pg_extension ORDER BY 1" -c "SHOW data_checksums"
```
**ผลลัพธ์:**
```
   extname          | extversion 
--------------------+------------
 auto_explain       | 1.0
 pgaudit            | 17.1
 pgcrypto           | 1.3
 pg_partman         | 5.5.0
 pg_stat_statements | 1.11
 plpgsql            | 1.0
(6 rows)

 data_checksums 
----------------
 on
(1 row)
```

### ขั้นที่ 5: รัน `pg_upgrade --check`

```bash
cd /var/lib/postgresql
sudo -u postgres /usr/lib/postgresql/18/bin/pg_upgrade --check \
  -b /usr/lib/postgresql/17/bin -B /usr/lib/postgresql/18/bin \
  -d /var/lib/postgresql/17/main -D /var/lib/postgresql/18/main \
  -o "-c config_file=/etc/postgresql/17/main/postgresql.conf" \
  -O "-c config_file=/etc/postgresql/18/main/postgresql.conf"
```
**ผลลัพธ์:**
```
Performing Consistency Checks
-----------------------------
Checking cluster versions                                     ok
Checking database user is the install user                    ok
Checking database connection settings                         ok
Checking for prepared transactions                            ok
Checking for contrib/isn with bigint-passing mismatch         ok
Checking for tables WITH OIDS                                 ok
Checking for invalid "sql_identifier" user columns            ok
Checking for presence of required libraries                   ok
Checking database connection settings                         ok
Checking for prepared transactions                            ok
Checking for new cluster tablespace directories               ok

*Clusters are compatible*
```

**✅ ผลลัพธ์ที่คาดหวัง:**
- `Data page checksum version: 1` บนรุ่น 18
- `*Clusters are compatible*`

> 💡 ต้อง `cd /var/lib/postgresql` ก่อน เพราะ `pg_upgrade` เขียนไฟล์ผลลัพธ์ (`update_extensions.sql`, `delete_old_cluster.sh`) ลงโฟลเดอร์ปัจจุบัน

---

## 🧪 Lab 1.2 — Upgrade คลัสเตอร์ Patroni จาก 17 เป็น 18

### ขั้นที่ 1: หยุดโหลดบน infra + หยุด Patroni (Replica ก่อน)

**บน infra:**
```bash
pgrep -a pgbench
```
**ผลลัพธ์:** (ต้องว่าง ถ้ามีให้กด `Ctrl+c`)

**บน pg1 — ตรวจว่า pg1 เป็น Leader:**
```bash
sudo -u postgres patronictl -c /etc/patroni/17-main.yml list
```
**ผลลัพธ์:**
```
+ Cluster: gridcare (7700687945522716648) ---+-------------+-----+------------+-----+
| Member | Host      | Role    | State     | TL | Receive LSN | Lag | Replay LSN | Lag |
+--------+-----------+---------+-----------+----+-------------+-----+------------+-----+
| pg1    | 10.104... | Leader  | running   |  7 |             |     |            |     |
| pg2    | 10.104... | Replica | streaming |  7 |  1/19000000 |   0 | 1/19000000 |   0 |
+--------+-----------+---------+-----------+----+-------------+-----+------------+-----+
```

**บน pg2 — หยุด Replica ก่อน:**
```bash
date +%T   # จดเวลาเริ่มหยุดระบบ
sudo systemctl stop patroni@17-main
```
**ผลลัพธ์:**
```
10:45:12
```

**บน pg1 — หยุด Primary ทีหลัง:**
```bash
sudo systemctl stop patroni@17-main
sudo -u postgres patronictl -c /etc/patroni/17-main.yml list
```
**ผลลัพธ์:** (ไม่มีโหนดใดเป็น Leader)

```bash
pgrep -u postgres -ax postgres | head -3
```
**ผลลัพธ์:** (ต้องว่าง — ไม่มี Process ของ PostgreSQL 17)

### ขั้นที่ 2: รัน `pg_upgrade --link` บน pg1

```bash
cd /var/lib/postgresql
time sudo -u postgres /usr/lib/postgresql/18/bin/pg_upgrade --link --jobs 2 \
  -b /usr/lib/postgresql/17/bin -B /usr/lib/postgresql/18/bin \
  -d /var/lib/postgresql/17/main -D /var/lib/postgresql/18/main \
  -o "-c config_file=/etc/postgresql/17/main/postgresql.conf" \
  -O "-c config_file=/etc/postgresql/18/main/postgresql.conf"
```
**ผลลัพธ์:**
```
Your installation contains extensions that should be updated
with the ALTER EXTENSION command.  The file
    update_extensions.sql
when executed by psql by the database superuser will update
these extensions.

Upgrade Complete
----------------
Some statistics are not transferred by pg_upgrade.
Once you start the new server, consider running these two commands:
    /usr/lib/postgresql/18/bin/vacuumdb --all --analyze-in-stages --missing-stats-only
    /usr/lib/postgresql/18/bin/vacuumdb --all --analyze-only
pg_upgrade --link: 2 s
```

### ขั้นที่ 3: `patroni.yml` ของรุ่น 18 + ลบ DCS + สตาร์ต

```bash
sudo sed -e 's#/17/#/18/#g' -e 's#17-main#18-main#g' /etc/patroni/17-main.yml | sudo tee /etc/patroni/18-main.yml > /dev/null
sudo chown postgres:postgres /etc/patroni/18-main.yml && sudo chmod 640 /etc/patroni/18-main.yml
grep -nE "data_dir|config_dir|bin_dir|pgpass|log_filename" /etc/patroni/18-main.yml
```
**ผลลัพธ์:**
```
17:  data_dir: /var/lib/postgresql/18/main
18:  config_dir: /etc/postgresql/18/main
19:  bin_dir: /usr/lib/postgresql/18/bin
20:  pgpass: /var/lib/postgresql/18-main.pgpass
35:    log_filename: postgresql-18-main.log
```

```bash
sudo -u postgres patronictl -c /etc/patroni/18-main.yml remove gridcare
```
**ผลลัพธ์:**
```
Please confirm the cluster name to remove: gridcare
You are about to remove all information in DCS for gridcare, please type: "Yes I am aware": Yes I am aware
```

```bash
sudo systemctl disable patroni@17-main
sudo systemctl enable --now patroni@18-main
sleep 15; sudo -u postgres patronictl -c /etc/patroni/18-main.yml list
```
**ผลลัพธ์:**
```
+ Cluster: gridcare (7700687945522716648) ---+-------------+-----+------------+-----+
| Member | Host      | Role   | State   | TL | Receive LSN | Lag | Replay LSN | Lag |
+--------+-----------+--------+---------+----+-------------+-----+------------+-----+
| pg1    | 10.104... | Leader | running |  2 |             |     |            |     |
+--------+-----------+--------+---------+----+-------------+-----+------------+-----+
```

```bash
sed -i 's#/etc/patroni/17-main.yml#/etc/patroni/18-main.yml#' ~/.bashrc && source ~/.bashrc
sudo sed -i 's#^pg1-path=.*#pg1-path=/var/lib/postgresql/18/main#' /etc/pgbackrest.conf
sudo -u postgres pgbackrest --stanza=gridcare stanza-upgrade
sudo -u postgres pgbackrest --stanza=gridcare check
```
**ผลลัพธ์:**
```
2026-11-06 10:52:30.123 P00   INFO: stanza-upgrade for stanza 'gridcare' on repo1
2026-11-06 10:52:30.456 P00   INFO: stanza-upgrade command end: completed successfully (333ms)

2026-11-06 10:52:45.123 P00   INFO: check command begin 2.59.3: --stanza=gridcare
2026-11-06 10:52:46.789 P00   INFO: check repo1 (standby) succeeded
2026-11-06 10:52:47.012 P00   INFO: check command end: completed successfully (1889ms)
```

### ขั้นที่ 4: pg2 — สร้าง Replica รุ่น 18 ใหม่

**บน pg2:**
```bash
sudo -u postgres bash -c 'rm -rf /var/lib/postgresql/18/main/*'
sudo sed -e 's#/17/#/18/#g' -e 's#17-main#18-main#g' /etc/patroni/17-main.yml | sudo tee /etc/patroni/18-main.yml > /dev/null
sudo chown postgres:postgres /etc/patroni/18-main.yml && sudo chmod 640 /etc/patroni/18-main.yml
sudo systemctl disable patroni@17-main
sudo systemctl enable --now patroni@18-main
sed -i 's#/etc/patroni/17-main.yml#/etc/patroni/18-main.yml#' ~/.bashrc && source ~/.bashrc
sudo sed -i 's#^pg1-path=.*#pg1-path=/var/lib/postgresql/18/main#' /etc/pgbackrest.conf
journalctl -u patroni@18-main -f
```
**ผลลัพธ์ (ระหว่าง basebackup):**
```
INFO: trying to bootstrap from leader 'pg1'
INFO: replica has been created using basebackup
INFO: bootstrapped from leader 'pg1'
INFO: no action. I am (pg2), a secondary, and following a leader (pg1)
```
> กด `Ctrl+c` เมื่อเห็น `secondary, and following a leader`

### ขั้นที่ 5: หลัง Upgrade — Full Backup, Extensions, Statistics

**บน pg1:**
```bash
sudo -u postgres pgbackrest --stanza=gridcare check
sudo -u postgres pgbackrest --stanza=gridcare --type=full backup
```
**ผลลัพธ์:**
```
2026-11-06 11:00:30.123 P00   INFO: backup command end: completed successfully (90666ms)
```

```bash
sudo -u postgres psql -X -f /var/lib/postgresql/update_extensions.sql
```
**ผลลัพธ์:**
```
ALTER EXTENSION
ALTER EXTENSION
ALTER EXTENSION
ERROR:  extension "pgaudit" has no update path from version "17.1" to version "18.0"
ALTER EXTENSION
```
> ⚠️ ERROR ของ pgaudit คาดไว้แล้ว — จะจัดการขั้นถัดไป

```bash
sudo -u postgres psql -X -d gridcare -c "DROP EXTENSION pgaudit" -c "CREATE EXTENSION pgaudit"
```
**ผลลัพธ์:**
```
DROP EXTENSION
CREATE EXTENSION
```

```bash
sudo -u postgres /usr/lib/postgresql/18/bin/vacuumdb --all --analyze-in-stages --missing-stats-only
sudo -u postgres /usr/lib/postgresql/18/bin/vacuumdb --all --analyze-only --jobs 2
```
**ผลลัพธ์:**
```
vacuumdb: processing database "gridcare": Generating minimal optimizer statistics (1 target)
...
vacuumdb: processing database "gridcare": Generating default (full) optimizer statistics
```

### ขั้นที่ 6: ตรวจผล

```bash
patronictl list
```
**ผลลัพธ์:**
```
+ Cluster: gridcare (7700687945522716648) ---+-------------+-----+------------+-----+
| Member | Host      | Role    | State     | TL | Receive LSN | Lag | Replay LSN | Lag |
+--------+-----------+---------+-----------+----+-------------+-----+------------+-----+
| pg1    | 10.104... | Leader  | running   |  2 |             |     |            |     |
| pg2    | 10.104... | Replica | streaming |  2 |  1/21000000 |   0 | 1/21000000 |   0 |
+--------+-----------+---------+-----------+----+-------------+-----+------------+-----+
```

```bash
sudo -u postgres psql -X -d gridcare -Atc "SELECT version()" -c "SHOW data_checksums" \
  -c "SELECT extname || ' ' || extversion FROM pg_extension ORDER BY 1" \
  -c "SELECT statistics_name FROM pg_stats_ext" -c "SELECT count(*) FROM gridcare.bills"
```
**ผลลัพธ์:**
```
PostgreSQL 18.6 (Ubuntu 18.6-1.pgdg24.04+2) on x86_64-pc-linux-gnu, compiled by gcc (Ubuntu 13.2.0-23ubuntu4) 13.2.0, 64-bit
on
auto_explain 1.0
pg_partman 5.5.0
pgaudit 18.0
pgcrypto 1.4
pg_stat_statements 1.12
plpgsql 1.0
bills_period_status
1200000
```

```bash
sudo -u postgres pgbackrest --stanza=gridcare info | grep -E "db \(|full backup"
```
**ผลลัพธ์:**
```
    db (prior)    wal archive min/max (17): 000000010000000000000001/000000070000000000000019
        full backup: 20261105-152200F
    db (current)  wal archive min/max (18): 000000020000000000000001/000000020000000000000012
        full backup: 20261106-110000F
```

### ขั้นที่ 7: ปรับสคริปต์ restore test

```bash
sudo sed -i 's#^Environment=MODE=pgbackrest#Environment=MODE=pgbackrest\nEnvironment=PGVER=18#' /etc/systemd/system/gridcare-restore-test.service
sudo systemctl daemon-reload
grep PGVER /etc/systemd/system/gridcare-restore-test.service
```
**ผลลัพธ์:**
```
Environment=PGVER=18
```

**✅ ผลลัพธ์ที่คาดหวัง:**
- `patronictl list`: pg1 = Leader, pg2 = Replica `streaming`
- `version()` ขึ้นต้นด้วย `PostgreSQL 18`
- `data_checksums = on`
- pgaudit 18.0, `bills_period_status` กลับมา
- `pgbackrest info` มีทั้ง `db (prior)` 17 และ `db (current)` 18

---

## 🧪 Lab 2.1 — Migration 1: CONCURRENTLY Index + Unique Index ที่ล้ม

### เตรียมโหลด (3 หน้าต่าง)

**หน้าต่าง 1 (infra):**
```bash
cd /opt/gridcare/pgbench && PGHOST=127.0.0.1 PGPORT=6432 PGUSER=billing_app ./run_normal.sh 8 3600
```

**หน้าต่าง 2 (infra):**
```bash
cd /opt/gridcare/pgbench && PGHOST=127.0.0.1 PGPORT=6432 PGUSER=billing_app pgbench -n -c 4 -j 2 -R 50 -T 3600 -P 30 -f notify_sms.sql gridcare
```

**หน้าต่าง 3 (pg1):**
```bash
watch -n 2 "sudo -u postgres psql -X -d gridcare -c \"SELECT pid, application_name, pg_blocking_pids(pid) AS blocked_by, wait_event_type, state, left(query, 50) FROM pg_stat_activity WHERE datname = 'gridcare' AND state <> 'idle' AND pid <> pg_backend_pid()\""
```

### เตรียมโฟลเดอร์ Migration

```bash
mkdir -p /var/tmp/migrations && chmod 755 /var/tmp/migrations
```

### 2.1.1 เขียนไฟล์ Migration 1

```bash
sudo truncate -s 0 /var/tmp/migrations/m1_indexes.sql
sudo nano /var/tmp/migrations/m1_indexes.sql
```

**เนื้อหา `m1_indexes.sql`:**
```sql
\set ON_ERROR_STOP off
SET search_path = gridcare, public;
SET lock_timeout = '3s';

\echo '== 1.1 Index สำหรับรายงาน SAIFI/SAIDI =='
CREATE INDEX CONCURRENTLY IF NOT EXISTS outage_events_office_started_idx ON outage_events (office_id, started_at);

\echo '== 1.2 Unique Index บนเบอร์โทร (คาดว่าจะล้ม เพราะมีเบอร์ซ้ำอยู่แล้ว) =='
CREATE UNIQUE INDEX CONCURRENTLY customers_phone_key ON customers (phone);

\echo '== Index ที่ค้างหลังล้ม =='
SELECT indexrelid::regclass AS index_name, indisvalid, indisready, pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_index WHERE indrelid = 'customers'::regclass AND NOT indisvalid;
```

### 2.1.2 รันด้วย `psql` (ไม่ใช้ `run_migration.sh` เพราะ CIC รันใน Transaction ไม่ได้)

```bash
sudo -u postgres psql -X -d gridcare -f /var/tmp/migrations/m1_indexes.sql
```
**ผลลัพธ์:**
```
== 1.1 Index สำหรับรายงาน SAIFI/SAIDI ==
CREATE INDEX
== 1.2 Unique Index บนเบอร์โทร (คาดว่าจะล้ม เพราะมีเบอร์ซ้ำอยู่แล้ว) ==
ERROR:  could not create unique index "customers_phone_key"
DETAIL:  Key (phone)=(086xxxxxxx) is duplicated.
== Index ที่ค้างหลังล้ม ==
         index_name         | indisvalid | indisready | size 
----------------------------+------------+------------+------
 customers_phone_key        | f          | f          | 0
(1 row)
```

### 2.1.3 ตรวจผลก่อนเก็บกวาด

```bash
sudo -u postgres psql -X -d gridcare
```

```sql
SELECT c.relname AS index_name, i.indisvalid, i.indisready
FROM pg_index AS i JOIN pg_class AS c ON c.oid = i.indexrelid
WHERE c.relname IN ('outage_events_office_started_idx', 'customers_phone_key');
SELECT count(*) AS invalid_indexes FROM pg_index WHERE NOT indisvalid;
```
**ผลลัพธ์:**
```
            index_name            | indisvalid | indisready 
----------------------------------+------------+------------
 outage_events_office_started_idx | t          | t
 customers_phone_key              | f          | f
(2 rows)

 invalid_indexes 
-----------------
               1
(1 row)
```

```sql
\q
```

### 2.1.4 เก็บกวาด

```bash
sudo truncate -s 0 /var/tmp/migrations/m1_cleanup.sql
sudo nano /var/tmp/migrations/m1_cleanup.sql
```

**เนื้อหา `m1_cleanup.sql`:**
```sql
\set ON_ERROR_STOP on
SET search_path = gridcare, public;
SET lock_timeout = '3s';
DROP INDEX CONCURRENTLY IF EXISTS customers_phone_key;
SELECT count(*) AS duplicated_phones
FROM (SELECT phone FROM customers GROUP BY phone HAVING count(*) > 1) AS d;
```

```bash
sudo -u postgres psql -X -d gridcare -f /var/tmp/migrations/m1_cleanup.sql
```
**ผลลัพธ์:**
```
DROP INDEX
 duplicated_phones 
-------------------
                62
(1 row)
```

**ตรวจสอบ:** `invalid_indexes = 0`

**✅ ผลลัพธ์ที่คาดหวัง:**
- `outage_events_office_started_idx`: `indisvalid = t`
- `customers_phone_key`: ล้มด้วย `could not create unique index` + `is duplicated`
- `invalid_indexes = 0` หลังเก็บกวาด

---

## 🧪 Lab 2.2 — Migration 2: NOT VALID + คอลัมน์ใหม่ + Backfill

### 2.2.1 ส่วนที่ขอ Lock แรงแต่สั้น

```bash
sudo truncate -s 0 /var/tmp/migrations/m2a_add_constraints.sql
sudo nano /var/tmp/migrations/m2a_add_constraints.sql
```

**เนื้อหา `m2a_add_constraints.sql`:**
```sql
SET search_path = gridcare, public;
ALTER TABLE bills ADD CONSTRAINT bills_total_nonnegative CHECK (total_amount >= 0) NOT VALID;
ALTER TABLE sms_notifications ADD CONSTRAINT sms_notifications_bill_fk
    FOREIGN KEY (bill_id) REFERENCES bills (bill_id) NOT VALID;
ALTER TABLE bills ADD COLUMN reminder_count smallint NOT NULL DEFAULT 0;
ALTER TABLE customers ADD COLUMN phone_e164 text;

CREATE OR REPLACE FUNCTION customers_phone_e164_sync() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.phone_e164 := '+66' || replace(substr(NEW.phone, 2), '-', '');
    RETURN NEW;
END $$;
CREATE TRIGGER customers_phone_e164_sync BEFORE INSERT OR UPDATE OF phone ON customers
    FOR EACH ROW EXECUTE FUNCTION customers_phone_e164_sync();
```

```bash
sudo -u postgres PGDATABASE=gridcare /opt/gridcare/scripts/run_migration.sh /var/tmp/migrations/m2a_add_constraints.sql
```
**ผลลัพธ์:**
```
[2026-11-06 10:30:12] ครั้งที่ 1/5: /var/tmp/migrations/m2a_add_constraints.sql (lock_timeout=3s)
[2026-11-06 10:30:12] สำเร็จ
```

### 2.2.2 สร้าง Index ฝั่งลูกของ FK แล้ว VALIDATE

```bash
sudo truncate -s 0 /var/tmp/migrations/m2b_validate.sql
sudo nano /var/tmp/migrations/m2b_validate.sql
```

**เนื้อหา `m2b_validate.sql`:**
```sql
\set ON_ERROR_STOP on
SET search_path = gridcare, public;
SET lock_timeout = '3s';
\timing on
CREATE INDEX CONCURRENTLY IF NOT EXISTS sms_notifications_bill_idx ON sms_notifications (bill_id);
ALTER TABLE bills VALIDATE CONSTRAINT bills_total_nonnegative;
ALTER TABLE sms_notifications VALIDATE CONSTRAINT sms_notifications_bill_fk;
```

```bash
sudo -u postgres psql -X -d gridcare -f /var/tmp/migrations/m2b_validate.sql
```
**ผลลัพธ์:**
```
CREATE INDEX
Time: 2345.678 ms
ALTER TABLE
Time: 1234.567 ms
ALTER TABLE
Time: 3456.789 ms
```

### 2.2.3 Backfill `phone_e164` ทีละ 20,000 แถว

```bash
sudo truncate -s 0 /var/tmp/migrations/m2c_backfill_phone.sql
sudo nano /var/tmp/migrations/m2c_backfill_phone.sql
```

**เนื้อหา `m2c_backfill_phone.sql`:**
```sql
\set ON_ERROR_STOP on
SET search_path = gridcare, public;
DO $$
DECLARE
    lo int := 0;
    hi int;
    max_id int;
    n bigint;
BEGIN
    SELECT max(customer_id) INTO max_id FROM customers;
    WHILE lo <= max_id LOOP
        hi := lo + 20000;
        UPDATE customers SET phone_e164 = '+66' || replace(substr(phone, 2), '-', '')
        WHERE customer_id >= lo AND customer_id < hi AND phone_e164 IS NULL;
        GET DIAGNOSTICS n = ROW_COUNT;
        RAISE NOTICE 'customer_id % - %: % แถว', lo, hi - 1, n;
        COMMIT;
        PERFORM pg_sleep(0.2);
        lo := hi;
    END LOOP;
END $$;
SELECT count(*) FILTER (WHERE phone_e164 IS NULL) AS remaining FROM customers;
```

```bash
sudo -u postgres psql -X -d gridcare -f /var/tmp/migrations/m2c_backfill_phone.sql
```
**ผลลัพธ์:**
```
NOTICE:  customer_id 0 - 19999: 20000 แถว
NOTICE:  customer_id 20000 - 39999: 20000 แถว
...
NOTICE:  customer_id 180000 - 199999: 20000 แถว
 remaining 
-----------
         0
(1 row)

Time: 8234.567 ms
```

### 2.2.4 ตรวจผล

```bash
sudo -u postgres psql -X -d gridcare
```

```sql
SELECT conrelid::regclass AS table_name, conname, convalidated
FROM pg_constraint WHERE conname IN ('bills_total_nonnegative', 'sms_notifications_bill_fk');
SELECT indexrelid::regclass, indisvalid FROM pg_index WHERE indrelid = 'gridcare.sms_notifications'::regclass;
SELECT count(*) FILTER (WHERE phone_e164 IS NULL) AS remaining, count(*) AS total FROM gridcare.customers;
SELECT attname, atthasmissing FROM pg_attribute WHERE attrelid = 'gridcare.bills'::regclass AND attname = 'reminder_count';
```
**ผลลัพธ์:**
```
         table_name         |          conname          | convalidated
----------------------------+---------------------------+--------------
 gridcare.bills             | bills_total_nonnegative   | t
 gridcare.sms_notifications | sms_notifications_bill_fk | t
(2 rows)

           indexrelid            | indisvalid
---------------------------------+------------
 sms_notifications_bill_idx      | t
(1 row)

 remaining |  total  
-----------+---------
         0 | 200000
(1 row)

    attname      | atthasmissing
-----------------+---------------
 reminder_count  | t
(1 row)
```

**✅ ผลลัพธ์ที่คาดหวัง:**
- ทั้งสอง Constraint `convalidated = t`
- `sms_notifications_bill_idx` valid
- `remaining = 0`
- `atthasmissing = t`

---

## 🧪 Lab 2.3 — Migration 3: PK integer → bigint

### 2.3.1 ตรวจ Sequence ก่อนเริ่ม

```bash
sudo -u postgres psql -X -d gridcare
```

```sql
SELECT s.sequencename, s.data_type, s.last_value, s.max_value,
       round(100.0 * s.last_value / s.max_value, 3) AS used_pct
FROM pg_sequences AS s WHERE s.schemaname = 'gridcare' ORDER BY used_pct DESC NULLS LAST;
```
**ผลลัพธ์:**
```
         sequencename          | data_type | last_value |  max_value  | used_pct
-------------------------------+-----------+------------+-------------+----------
 sms_notifications_notification_id_seq | integer   |   1664422 |  2147483647 |   99.920
(1 row)
```

```sql
\q
```

### 2.3.2 ขั้น a: เพิ่มคอลัมน์ bigint + Trigger

```bash
sudo truncate -s 0 /var/tmp/migrations/m3a_prepare.sql
sudo nano /var/tmp/migrations/m3a_prepare.sql
```

**เนื้อหา `m3a_prepare.sql`:**
```sql
SET search_path = gridcare, public;
ALTER TABLE sms_notifications ADD COLUMN notification_id_new bigint;
CREATE OR REPLACE FUNCTION sms_notifications_id_sync() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.notification_id_new := NEW.notification_id;
    RETURN NEW;
END $$;
CREATE TRIGGER sms_notifications_id_sync BEFORE INSERT OR UPDATE ON sms_notifications
    FOR EACH ROW EXECUTE FUNCTION sms_notifications_id_sync();
```

```bash
sudo -u postgres PGDATABASE=gridcare /opt/gridcare/scripts/run_migration.sh /var/tmp/migrations/m3a_prepare.sql
```
**ผลลัพธ์:**
```
[2026-11-06 10:42:30] ครั้งที่ 1/5: ...
[2026-11-06 10:42:30] สำเร็จ
```

### 2.3.3 ขั้น b: Backfill

```bash
sudo truncate -s 0 /var/tmp/migrations/m3b_backfill.sql
sudo nano /var/tmp/migrations/m3b_backfill.sql
```

**เนื้อหา `m3b_backfill.sql`:**
```sql
\set ON_ERROR_STOP on
SET search_path = gridcare, public;
DO $$
DECLARE
    lo bigint;
    max_id bigint;
    n bigint;
BEGIN
    SELECT min(notification_id), max(notification_id) INTO lo, max_id FROM sms_notifications;
    WHILE lo <= max_id LOOP
        UPDATE sms_notifications SET notification_id_new = notification_id
        WHERE notification_id >= lo AND notification_id < lo + 50000 AND notification_id_new IS NULL;
        GET DIAGNOSTICS n = ROW_COUNT;
        RAISE NOTICE 'id % ขึ้นไป: % แถว', lo, n;
        COMMIT;
        PERFORM pg_sleep(0.2);
        lo := lo + 50000;
    END LOOP;
END $$;
SELECT count(*) FILTER (WHERE notification_id_new IS NULL) AS remaining FROM sms_notifications;
```

```bash
sudo -u postgres psql -X -d gridcare -f /var/tmp/migrations/m3b_backfill.sql
```
**ผลลัพธ์:**
```
NOTICE:  id 1 ขึ้นไป: 50000 แถว
NOTICE:  id 50001 ขึ้นไป: 50000 แถว
...
NOTICE:  id 150001 ขึ้นไป: 50000 แถว
 remaining 
-----------
         0
(1 row)

Time: 7234.567 ms
```

### 2.3.4 ขั้น c: Unique Index + CHECK NOT NULL

```bash
sudo truncate -s 0 /var/tmp/migrations/m3c_index_check.sql
sudo nano /var/tmp/migrations/m3c_index_check.sql
```

**เนื้อหา `m3c_index_check.sql`:**
```sql
\set ON_ERROR_STOP on
SET search_path = gridcare, public;
SET lock_timeout = '3s';
\timing on
CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS sms_notifications_id_new_key ON sms_notifications (notification_id_new);
SELECT indexrelid::regclass, indisvalid FROM pg_index WHERE indexrelid = 'sms_notifications_id_new_key'::regclass;
ALTER TABLE sms_notifications ADD CONSTRAINT sms_notifications_id_new_nn CHECK (notification_id_new IS NOT NULL) NOT VALID;
ALTER TABLE sms_notifications VALIDATE CONSTRAINT sms_notifications_id_new_nn;
```

```bash
sudo -u postgres psql -X -d gridcare -f /var/tmp/migrations/m3c_index_check.sql
```
**ผลลัพธ์:**
```
CREATE INDEX
Time: 1234.567 ms
           indexrelid           | indisvalid 
--------------------------------+------------
 sms_notifications_id_new_key   | t
(1 row)

ALTER TABLE
ALTER TABLE
Time: 234.567 ms
```

### 2.3.5 ขั้น d: สลับคอลัมน์และ PK

```bash
sudo truncate -s 0 /var/tmp/migrations/m3d_swap.sql
sudo nano /var/tmp/migrations/m3d_swap.sql
```

**เนื้อหา `m3d_swap.sql`:**
```sql
SET search_path = gridcare, public;
LOCK TABLE sms_notifications IN ACCESS EXCLUSIVE MODE;

DROP TRIGGER sms_notifications_id_sync ON sms_notifications;
ALTER TABLE sms_notifications DROP CONSTRAINT sms_notifications_pkey;
ALTER TABLE sms_notifications ALTER COLUMN notification_id DROP IDENTITY;
ALTER TABLE sms_notifications RENAME COLUMN notification_id TO notification_id_old;
ALTER TABLE sms_notifications RENAME COLUMN notification_id_new TO notification_id;
ALTER TABLE sms_notifications ALTER COLUMN notification_id SET NOT NULL;
ALTER TABLE sms_notifications ADD CONSTRAINT sms_notifications_pkey PRIMARY KEY USING INDEX sms_notifications_id_new_key;
ALTER TABLE sms_notifications DROP CONSTRAINT sms_notifications_id_new_nn;
ALTER TABLE sms_notifications ALTER COLUMN notification_id_old DROP NOT NULL;
ALTER TABLE sms_notifications ALTER COLUMN notification_id ADD GENERATED BY DEFAULT AS IDENTITY;
SELECT setval(pg_get_serial_sequence('gridcare.sms_notifications', 'notification_id'),
              (SELECT max(notification_id) FROM sms_notifications));
```

```bash
sudo -u postgres PGDATABASE=gridcare /opt/gridcare/scripts/run_migration.sh /var/tmp/migrations/m3d_swap.sql
```
**ผลลัพธ์:**
```
[2026-11-06 11:09:11] ครั้งที่ 1/5: .../m3d_swap.sql (lock_timeout=3s)
[2026-11-06 11:09:11] สำเร็จ
```
> ขั้นสลับใช้ 0.13 วินาที

### 2.3.6 ตรวจผล

```bash
sudo -u postgres psql -X -d gridcare
```

```sql
SELECT a.attname, format_type(a.atttypid, a.atttypmod) AS type
FROM pg_attribute AS a WHERE a.attrelid = 'gridcare.sms_notifications'::regclass AND a.attnum > 0 AND NOT a.attisdropped;
SELECT sequencename, data_type, last_value FROM pg_sequences WHERE sequencename LIKE 'sms_notifications%';
BEGIN;
INSERT INTO gridcare.sms_notifications (notification_id, customer_id, message_type, sent_at, status)
VALUES (2147483648, 1, 'PAYMENT_DUE', now(), 'QUEUED') RETURNING notification_id;
ROLLBACK;
```
**ผลลัพธ์:**
```
      attname      |        type         
-------------------+---------------------
 notification_id   | bigint
 notification_id_old| integer
 customer_id       | integer
 ...

            sequencename              | data_type | last_value 
---------------------------------------+-----------+------------
 sms_notifications_notification_id_seq | bigint    |    1664422
(1 row)

 notification_id 
-----------------
      2147483648
(1 row)
```

**✅ ผลลัพธ์ที่คาดหวัง:**
- `notification_id` เป็น `bigint`
- Sequence เป็น `bigint`
- INSERT ID `2147483648` ได้
- pgbench notify_sms ไม่มี error

---

## 🧪 Lab 3.1 — ซ้อม 15 นาทีแรก

### ส่วนที่ 1: จับคู่ข้อความ error กับชั้นของปัญหา

**ตารางคำตอบ:**

| # | ข้อความ | ชั้น | การ์ด |
|---|---|---|---|
| 1 | `FATAL: sorry, too many clients already` | connection | C03 |
| 2 | `ERROR: canceling statement due to lock timeout` | lock | C01 |
| 3 | `PANIC: could not write to file "pg_wal/xlogtemp.123": No space left on device` | ดิสก์ | C04 |
| 4 | `FATAL: could not open file "global/pg_filenode.map": Input/output error` | storage | C12 |
| 5 | `WARNING: database "gridcare" must be vacuumed within 39985967 transactions` | XID | C05 |
| 6 | `FATAL: requested WAL segment ... has already been removed` | replica | C08 |
| 7 | `LOG: server process (PID 3391) was terminated by signal 9: Killed` | OOM | C06 |
| 8 | `FATAL: no pg_hba.conf entry for host ...` | การเข้าถึง | C03 |

### ส่วนที่ 2: ไล่สายช้าบนคลัสเตอร์จริง

**บน infra:**
```bash
pg_isready -h 127.0.0.1 -p 5000
```
**ผลลัพธ์:**
```
127.0.0.1:5000 - accepting connections
```

**บน pg1:**
```bash
patronictl list
```
**ผลลัพธ์:**
```
+ Cluster: gridcare (7700687945522716648) ---+-------------+-----+------------+-----+
| Member | Host      | Role    | State     | TL | Receive LSN | Lag | Replay LSN | Lag |
+--------+-----------+---------+-----------+----+-------------+-----+------------+-----+
| pg1    | 10.104... | Leader  | running   |  2 |             |     |            |     |
| pg2    | 10.104... | Replica | streaming |  2 |  1/21000000 |   0 | 1/21000000 |   0 |
+--------+-----------+---------+-----------+----+-------------+-----+------------+-----+
```

```sql
SELECT pid, usename, application_name, state, wait_event_type, wait_event,
       now() - xact_start AS xact_age, pg_blocking_pids(pid) AS blocked_by, left(query, 60)
FROM pg_stat_activity WHERE state <> 'idle' ORDER BY xact_start;
```
**ผลลัพธ์:**
```
  pid  |   usename   | application_name |        state        | wait_event_type | wait_event |  xact_age  | blocked_by |                   left                    
-------+-------------+------------------+---------------------+-----------------+------------+------------+------------+-------------------------------------------
 12345 | billing_app | pgbench          | active              | Client          | ClientRead | 00:00:00.5 | {}         | UPDATE bills SET ...
 12346 | billing_app | notify_sms       | active              | Client          | ClientRead | 00:00:00.3 | {}         | INSERT INTO sms_notifications ...
```

```sql
SELECT pg_size_pretty(sum(size)) AS pg_wal_size FROM pg_ls_waldir();
SELECT slot_name, active, wal_status FROM pg_replication_slots;
SELECT failed_count, last_archived_time FROM pg_stat_archiver;
SELECT datname, age(datfrozenxid) FROM pg_database ORDER BY 2 DESC LIMIT 3;
SELECT application_name, write_lag, flush_lag, replay_lag FROM pg_stat_replication;
SELECT calls, round(total_exec_time::numeric) AS total_ms, left(query, 60) FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 3;
```
**ผลลัพธ์:**
```
 pg_wal_size 
-------------
 512 MB

 slot_name | active | wal_status 
-----------+--------+------------
 pg2       | t      | reserved

 failed_count |    last_archived_time     
--------------+---------------------------
            0 | 2026-11-06 10:35:12.345+07

  datname   |   age    
------------+----------
 gridcare   | 152345678
 postgres   |  45012
 template1  |  45012

 application_name | write_lag | flush_lag | replay_lag 
------------------+-----------+-----------+------------
 pg2              | 00:00:00  | 00:00:00  | 00:00:00

 calls | total_ms |                           left                            
-------+----------+------------------------------------------------------------
 15023 |   45234  | UPDATE bills SET status = $1 WHERE bill_id = $2
```

**✅ ผลลัพธ์ที่คาดหวัง:** ตารางจับคู่ครบ 8 ข้อ + สรุป 3 บรรทัด (อาการ / ต้นเหตุ / สิ่งที่ทำ)

---

## 🛠️ Workshop Day 5 — Game Day

### ขั้นที่ 1: เตรียมทีมและ Baseline

**บน pg1:**
```bash
patronictl list
sudo -u postgres pgbackrest --stanza=gridcare info | grep -E "full backup" | tail -1
```
**ผลลัพธ์:**
```
+ Cluster: gridcare (7700687945522716648) ---+-------------+-----+------------+-----+
| Member | Host      | Role    | State     | TL | Receive LSN | Lag | Replay LSN | Lag |
+--------+-----------+---------+-----------+----+-------------+-----+------------+-----+
| pg1    | 10.104... | Leader  | running   |  2 |             |     |            |     |
| pg2    | 10.104... | Replica | streaming |  2 |  1/21000000 |   0 | 1/21000000 |   0 |
+--------+-----------+---------+-----------+----+-------------+-----+------------+-----+

        full backup: 20261106-110000F
```

**บน infra:**
```bash
curl -s localhost:9090/api/v1/alerts | python3 -c "import sys,json; print([a['labels']['alertname'] for a in json.load(sys.stdin)['data']['alerts'] if a['state']=='firing'])"
```
**ผลลัพธ์:**
```
[]
```

**✅ ผลลัพธ์ที่คาดหวัง:** pg1 = Leader รุ่น 18, Full Backup หลัง Upgrade, Alert firing ว่าง

### ขั้นที่ 2: เหตุการณ์ 1-5

**ตารางเหตุการณ์:**

| # | สถานการณ์ | การ์ด |
|---|---|---|
| 1 | พายุเข้า แอปเชื่อมต่อไม่ได้ | C03 |
| 2 | Batch ออกบิลทำให้แอปช้า | C01 |
| 3 | ข้อมูล AMI ทำดิสก์เต็ม + Replication Lag | C04, C08 |
| 4 | Primary ล่มช่วงชำระค่าไฟ | C08 |
| 5 | ข้อมูลรอบบิลถูกลบผิด | C07 |

**แม่แบบบันทึก:**
```
เหตุการณ์ที่ 4  เริ่ม 14:30:15  ตรวจพบ 14:30:46  แก้เสร็จ 14:31:00  ยืนยันปกติ 14:31:15
อาการ    : แอปเขียนไม่ได้, PgBouncer คืน Connection refused
ต้นเหตุ   : Primary (pg1) ถูก SIGKILL, Patroni failover ไป pg2
สิ่งที่ทำ : Patroni promote pg2 อัตโนมัติ, HAProxy สลับ health check
ตรวจพบจาก: Alert PostgresDown (firing 14:30:30) + probe.sh FAIL
RTO = 31.2 วินาที  RPO = 0
```

**✅ ผลลัพธ์ที่คาดหวัง:** บันทึกครบ 5 เหตุการณ์ ทุกเหตุการณ์ระบุต้นเหตุที่พิสูจน์แล้ว

### ขั้นที่ 3: Debrief

**สิ่งที่ต้องส่ง:**
1. ตาราง RPO/RTO ของเหตุการณ์ที่ 4-5 เทียบเป้าหมาย
2. Alert ที่ดังก่อนผู้ใช้แจ้ง vs ที่ไม่ดัง
3. งานป้องกันอย่างน้อย 3 รายการ + อย่างน้อย 1 เป็น Alert/การตรวจอัตโนมัติ

**✅ ผลลัพธ์ที่คาดหวัง:** สรุป 1 หน้า (ผลกระทบ / ตรวจพบ / ต้นเหตุ / สิ่งที่ได้ผล-ไม่ได้ผล / งานป้องกัน)

---

## 🧪 Lab 6.1 — แผน 30 วันหลังอบรม

**ตารางแผน:**

| สัปดาห์ | งาน | เครื่องมือ | ผลที่ส่ง |
|---|---|---|---|
| 1 | รัน health check กับระบบจริง (อ่านอย่างเดียว) | `scripts/health_check.sh` | ผล WARN/CRIT |
| 1 | รายงานรายสัปดาห์ (Index ซ้ำ/FK ไม่มี Index/Sequence >85%) | `scripts/weekly_report.sql` | รายการที่ต้องแก้ |
| 2 | PostgreSQL 14: `pg_upgrade --check` บนเครื่องทดสอบ | Lab 1.1 | ผล `--check` |
| 3 | ทดลองกู้ Backup ของระบบตนเอง + วัด RTO | `scripts/restore_test.sh` | RTO จริง |
| 4 | นำ Dashboard + Alert Rule เข้า Monitoring ขององค์กร | ไฟล์ JSON + Rule | Alert ดังครั้งแรก |

**ตัวอย่างคำสั่งตรวจความพร้อมรุ่น 14 (บนเครื่องทดสอบเท่านั้น):**
```bash
sudo -u postgres /usr/lib/postgresql/17/bin/pg_upgrade --check \
  -b /usr/lib/postgresql/14/bin -B /usr/lib/postgresql/17/bin \
  -d /var/lib/postgresql/14/main -D /var/lib/postgresql/17/main \
  -o "-c config_file=/etc/postgresql/14/main/postgresql.conf" \
  -O "-c config_file=/etc/postgresql/17/main/postgresql.conf"
```
**ผลลัพธ์:**
```
Performing Consistency Checks
-----------------------------
Checking cluster versions                                   ok
...
*Clusters are compatible*
```

**✅ ผลลัพธ์ที่คาดหวัง:** แผนครบ 4 สัปดาห์ มีชื่อย่อระบบ, ทีมรับผิดชอบ, วันที่ส่งผล

---

## 📊 สรุปคำสั่งสำคัญทั้งหมด (Cheat Sheet Day 5)

### Upgrade

```bash
# ตรวจความพร้อม
pg_upgrade --check -b <old_bin> -B <new_bin> -d <old_data> -D <new_data> \
  -o "-c config_file=<old_conf>" -O "-c config_file=<new_conf>"

# Upgrade
pg_upgrade --link --jobs 2 -b <old_bin> -B <new_bin> -d <old_data> -D <new_data> ...

# หลัง Upgrade
pgbackrest --stanza=<name> stanza-upgrade
pgbackrest --stanza=<name> --type=full backup
psql -f /var/lib/postgresql/update_extensions.sql
psql -d <db> -c "DROP EXTENSION pgaudit" -c "CREATE EXTENSION pgaudit"
vacuumdb --all --analyze-in-stages --missing-stats-only
vacuumdb --all --analyze-only --jobs 2
```

### Safe Migration

```bash
# รันผ่าน run_migration.sh (Transaction เดียว + lock_timeout + retry)
PGDATABASE=<db> /opt/gridcare/scripts/run_migration.sh <file.sql>

# รันด้วย psql (สำหรับ CONCURRENTLY หรือมี COMMIT)
psql -X -d <db> -f <file.sql>
```

```sql
-- NOT VALID
ALTER TABLE tbl ADD CONSTRAINT chk CHECK (...) NOT VALID;
ALTER TABLE tbl VALIDATE CONSTRAINT chk;

-- คอลัมน์ใหม่
ALTER TABLE tbl ADD COLUMN col type NOT NULL DEFAULT 0;

-- CHECK NOT NULL ล่วงหน้า (หลีกเลี่ยงสแกนตอน SET NOT NULL)
ALTER TABLE tbl ADD CONSTRAINT nn CHECK (col_new IS NOT NULL) NOT VALID;
ALTER TABLE tbl VALIDATE CONSTRAINT nn;
```

### Troubleshooting

```sql
-- 15 นาทีแรก: สายช้า
SELECT pid, usename, application_name, state, wait_event_type, wait_event,
       now() - xact_start AS xact_age, pg_blocking_pids(pid) AS blocked_by, left(query, 60)
FROM pg_stat_activity WHERE state <> 'idle' ORDER BY xact_start;

SELECT pg_size_pretty(sum(size)) FROM pg_ls_waldir();
SELECT slot_name, active, wal_status FROM pg_replication_slots;
SELECT failed_count, last_archived_time FROM pg_stat_archiver;
SELECT datname, age(datfrozenxid) FROM pg_database ORDER BY 2 DESC LIMIT 3;
SELECT application_name, write_lag, flush_lag, replay_lag FROM pg_stat_replication;
SELECT calls, round(total_exec_time::numeric), left(query, 60) FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 3;
```

---

## 🎯 สรุปผลลัพธ์สำคัญของ Day 5

| Lab | ผลลัพธ์ที่วัดได้ |
|---|---|
| **Lab 1.1** | `*Clusters are compatible*`, Checksum version 1 |
| **Lab 1.2** | pg_upgrade 2 วินาที, pg2 streaming, pgaudit 18.0, bills_period_status กลับมา, 1,200,000 bills |
| **Lab 2.1** | `outage_events_office_started_idx` valid, `customers_phone_key` ล้ม, `invalid_indexes = 0` |
| **Lab 2.2** | `convalidated = t` ทั้งสอง, `remaining = 0`, `atthasmissing = t` |
| **Lab 2.3** | `notification_id bigint`, INSERT `2147483648` ได้, ขั้นสลับ 0.13 วินาที, pgbench failed = 0 |
| **Lab 3.1** | ตารางจับคู่ 8 ข้อ + สรุป 3 บรรทัด |
| **Workshop ขั้น 1** | pg1 = Leader รุ่น 18, Alert firing ว่าง |
| **Workshop ขั้น 2** | 5 เหตุการณ์ พร้อม RTO/RPO |
| **Workshop ขั้น 3** | สรุป + งานป้องกัน 3 รายการ |
| **Lab 6.1** | แผน 30 วัน 4 สัปดาห์ |

---

## ⚠️ ข้อควรระวังใน Day 5

| # | ข้อควรระวัง | ผลที่เกิด |
|---|---|---|
| 1 | **`pg_upgrade --check` ก่อนเสมอ** | ถ้าไม่ → อาจล้มกลางทาง |
| 2 | **ต้อง `cd /var/lib/postgresql`** | postgres เขียนโฟลเดอร์อื่นไม่ได้ |
| 3 | **หยุด Replica ก่อน Primary** | ป้องกัน Failover กลางขั้นตอน |
| 4 | **`patronictl remove` หลัง pg_upgrade** | System Identifier ใหม่ |
| 5 | **`stanza-upgrade` ทันทีหลัง Primary รุ่น 18 ขึ้น** | WAL Archive จะล้มถ้าไม่ทำ |
| 6 | **`DROP/CREATE EXTENSION pgaudit`** | ไม่มี update path 17→18 |
| 7 | **`vacuumdb --missing-stats-only`** | Extended Statistics ไม่ถูกโอน |
| 8 | **pgbench ต้องใส่ `-R 50`** | ID integer อาจเต็มก่อน migration เสร็จ |
| 9 | **`CREATE INDEX CONCURRENTLY` ห้ามใน `run_migration.sh`** | error: cannot run inside transaction |
| 10 | **`DROP NOT NULL` ที่คอลัมน์เดิม** | ถ้าลืม → INSERT ใหม่ล้ม |
| 11 | **`setval` หลัง ADD IDENTITY** | Sequence ต่อจากค่าสูงสุด |
| 12 | **ห้าม `pg_resetwal` ใน Game Day** | ข้อมูลเสียหายถาวร |
| 13 | **ห้าม PITR ทับคลัสเตอร์โดยผู้ตรวจทานไม่เห็นด้วย** | เสียข้อมูลหลังเวลาเป้าหมาย |

---

## 📁 สถานะเครื่องหลังจบหลักสูตร

```
pg1 / pg2
├── PostgreSQL 18.6 + Patroni (patroni@18-main, /etc/patroni/18-main.yml)
├── ข้อมูลรุ่น 17 ยังอยู่ (ยังไม่ได้รัน delete_old_cluster.sh)
├── pgBackRest: db (prior) 17 + db (current) 18
└── gridcare: Index ใหม่จาก Migration 1,
    Constraint + phone_e164 จาก Migration 2,
    sms_notifications PK bigint

infra
└── HAProxy, PgBouncer, etcd, Prometheus + Rule, Alertmanager,
    Mailpit, Grafana, MinIO

Notebook
└── Lab Kit: หลังจบหลักสูตรรัน 3_uninstall ตามคู่มือใน Kit
    เพื่อคืนค่าเครื่อง (ห้ามนำข้อมูล GridCare ออกจาก Lab)
```

---

## 🏆 สรุปหลักสูตร 5 วัน

| วัน | สิ่งที่ทำได้แล้ว |
|---|---|
| **วันที่ 1** | ติดตั้ง PostgreSQL 17 ที่ถูกต้อง, Log มาตรฐาน, คิว Lock, Role + Timeout, TLS, PgBouncer (57→93 tps) |
| **วันที่ 2** | EXPLAIN, Index, Query จาก ORM, Prometheus + Grafana, VACUUM/Bloat/XID, Partitioning + BRIN (tps 93→149) |
| **วันที่ 3** | pgBackRest + MinIO, PITR, health check + restore test, RLS (16,676/16,454/200,000), pgcrypto, Masking, pgAudit |
| **วันที่ 4** | etcd + Patroni + HAProxy, Split-Brain, Alert Rule + Alertmanager, Failover (RTO 31s, RPO 0), Switchover 3s |
| **วันที่ 5** | Upgrade 17→18 (pg_upgrade 2s), Migration 3 ชุด (0.13s swap), 15 นาทีแรก, Kubernetes, Game Day 5 เหตุการณ์ |

**💡 คำคมส่งท้าย:**

> "ระบบที่ดีไม่ใช่ระบบที่ไม่เคยมีเหตุ แต่เป็นระบบที่ทุกเหตุทำให้ทีมเก่งขึ้น และทิ้งไว้อย่างน้อยหนึ่ง Alert ที่จะดังก่อนครั้งหน้า"

---

**✅ สรุปเสร็จสมบูรณ์** — คำสั่งและผลลัพธ์ทั้งหมดจาก Day 5 ครอบคลุม Lab 1.1-1.2, Lab 2.1-2.3, Lab 3.1, Workshop Day 5 (Game Day 5 เหตุการณ์ + Debrief) และ Lab 6.1 (แผน 30 วัน) พร้อมตัวเลขที่วัดได้จริงจากหลักสูตร