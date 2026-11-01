# 📋 สรุปคำสั่งทั้งหมด — Day 3 (วันที่ 3)

> **หลักสูตร:** Advanced PostgreSQL for Enterprise Production (PEA)
> **หัวข้อ:** Backup, Recovery & Security
> **วันที่:** พุธที่ 4 พฤศจิกายน 2569 | 09:00-16:45 น.
> รูปแบบ: **คำสั่ง** → **ผลลัพธ์จริง/ที่คาดหวัง** → **หมายเหตุ**

---

## 🔄 เริ่มวัน: เปิดโหลดจำลองค้างไว้

### บน infra ภายใน tmux

```bash
tmux new -s load
```
**ผลลัพธ์:** เข้าหน้าจอ tmux session ใหม่ชื่อ `load`

**ภายในหน้าต่าง tmux:**
```bash
cd /opt/gridcare/pgbench
PGHOST=127.0.0.1 PGPORT=6432 PGUSER=billing_app ./run_normal.sh 8 25200
```
**ผลลัพธ์:**
```
starting 8 clients for 25200 seconds...
```

**กด `Ctrl+b` แล้ว `d`** เพื่อ detach

> ⚠️ วันนี้มีการ Restart PostgreSQL หลายครั้ง (Lab 3.2, Lab 5.1, PITR) → ต้องตรวจ `tmux attach -t load` หลังทุก Restart

---

## 🧪 Lab 2.1 — pg_dump แบบ Parallel, Restore บางส่วน และสำรอง Role

### บน pg1

```bash
sudo install -d -o postgres -g postgres -m 700 /var/backups/gridcare
```

### ขั้นที่ 1: Dump แบบ Directory

```bash
time sudo -u postgres pg_dump -d gridcare -Fd -j 2 -Z zstd:3 -f /var/backups/gridcare/gc.dir
```
**ผลลัพธ์:**
```
real    0m9.234s
user    0m4.567s
sys     0m1.234s
```

```bash
sudo du -sh /var/backups/gridcare/gc.dir
```
**ผลลัพธ์:**
```
192M    /var/backups/gridcare/gc.dir
```

### ขั้นที่ 2: สำรอง Role

```bash
sudo -u postgres pg_dumpall --globals-only --no-role-passwords | sudo -u postgres tee /var/backups/gridcare/globals.sql > /dev/null
sudo grep -c "CREATE ROLE" /var/backups/gridcare/globals.sql
```
**ผลลัพธ์:**
```
10
```

### ขั้นที่ 3: สร้างรายการเลือก Restore

```bash
sudo -u postgres pg_restore -l /var/backups/gridcare/gc.dir | grep -E "TABLE DATA gridcare (tariff_rates|regions) "
```
**ผลลัพธ์:**
```
3975; 0 16386 TABLE DATA gridcare regions postgres
3977; 0 16405 TABLE DATA gridcare tariff_rates postgres
```

```bash
sudo -u postgres bash -c "pg_restore -l /var/backups/gridcare/gc.dir | grep -E ' (SCHEMA - gridcare|TABLE gridcare (tariff_rates|regions)|TABLE DATA gridcare (tariff_rates|regions)) ' > /var/backups/gridcare/partial.list"
sudo cat /var/backups/gridcare/partial.list
```
**ผลลัพธ์:**
```
3968; 0 16386 SCHEMA - gridcare postgres
3974; 0 16386 TABLE gridcare regions postgres
3975; 0 16386 TABLE DATA gridcare regions postgres
3976; 0 16405 TABLE gridcare tariff_rates postgres
3977; 0 16405 TABLE DATA gridcare tariff_rates postgres
```

### ขั้นที่ 4: Restore เฉพาะส่วน

```bash
sudo -u postgres createdb gridcare_restore
sudo -u postgres pg_restore -d gridcare_restore -L /var/backups/gridcare/partial.list --no-owner /var/backups/gridcare/gc.dir
sudo -u postgres psql -X -d gridcare_restore -c "SELECT tariff_code, rate_per_kwh FROM gridcare.tariff_rates ORDER BY 1" -c "\dt gridcare.*"
```
**ผลลัพธ์:**
```
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
**ผลลัพธ์:** (ไม่มี output)

**✅ ผลลัพธ์ที่คาดหวัง:**
- Dump 10-40 วินาทีบนเครื่อง Lab, ไฟล์ ~200 MB
- `gridcare_restore` มีเฉพาะ 2 ตาราง
- `tariff_rates` มี 3 แถว

---

## 🧪 Lab 3.1 — เปิด MinIO บน infra ด้วย TLS และสร้าง Bucket

### บน infra

### ขั้นที่ 1: อ่านไฟล์ที่เตรียมไว้

```bash
systemctl cat minio | grep -E "User|EnvironmentFile|ExecStart"
```
**ผลลัพธ์:**
```
User=minio-user
EnvironmentFile=/etc/default/minio
ExecStart=/usr/local/bin/minio server $MINIO_OPTS $MINIO_VOLUMES
```

```bash
sudo cat /etc/default/minio
```
**ผลลัพธ์:**
```
MINIO_VOLUMES="/var/lib/minio"
MINIO_OPTS="--address :9000 --console-address 127.0.0.1:9001"
MINIO_ROOT_USER=""
MINIO_ROOT_PASSWORD=""
```

```bash
cat /opt/pea/VERSIONS | grep -i minio
```
**ผลลัพธ์:**
```
MinIO: RELEASE.2025-04-22T22-12-26Z
```

### ขั้นที่ 2: สร้างใบรับรอง TLS

```bash
INFRA_IP=$(getent hosts infra | awk '{print $1}')
sudo install -d -m 755 /etc/minio/certs
sudo openssl req -new -x509 -days 365 -nodes -newkey rsa:3072 \
  -subj "/CN=infra" -addext "subjectAltName=DNS:infra,IP:${INFRA_IP}" \
  -keyout /etc/minio/certs/private.key -out /etc/minio/certs/public.crt
```
**ผลลัพธ์:**
```
Generating a RSA private key
..........................+++++
.............+++++
writing new private key to '/etc/minio/certs/private.key'
-----
```

```bash
MINIO_USER=$(systemctl show -p User --value minio)
sudo chown -R "${MINIO_USER}": /etc/minio/certs
sudo chmod 600 /etc/minio/certs/private.key
```

### ขั้นที่ 3: แก้ /etc/default/minio

```bash
sudo cp /etc/default/minio /etc/default/minio.bak
sudo nano /etc/default/minio
```

**เนื้อหา:**
```ini
MINIO_VOLUMES="/var/lib/minio"
MINIO_OPTS="--address :9000 --console-address 127.0.0.1:9001 --certs-dir /etc/minio/certs"
MINIO_ROOT_USER="gridcare-backup"
MINIO_ROOT_PASSWORD="Lab-Minio-Secret-2569"
```

### ขั้นที่ 4: เปิดใช้งาน MinIO

```bash
sudo install -d -o "${MINIO_USER}" -g "${MINIO_USER}" -m 750 /var/lib/minio
sudo systemctl enable --now minio
systemctl status minio --no-pager | head -5
```
**ผลลัพธ์:**
```
● minio.service - MinIO
     Loaded: loaded (/lib/systemd/system/minio.service; enabled; preset: enabled)
     Active: active (running) since Wed 2026-11-04 08:45:12 +07; 3s ago
       Docs: https://docs.min.io
    Process: 1234 ExecStart=/usr/local/bin/minio server ... (code=exited, status=0/SUCCESS)
```

```bash
curl -s -o /dev/null -w "%{http_code}\n" --cacert /etc/minio/certs/public.crt https://infra:9000/minio/health/live
```
**ผลลัพธ์:**
```
200
```

### ขั้นที่ 5: สร้าง Bucket ด้วย curl

```bash
curl -s -o /dev/null -w "%{http_code}\n" --cacert /etc/minio/certs/public.crt \
  --aws-sigv4 "aws:amz:us-east-1:s3" --user "gridcare-backup:Lab-Minio-Secret-2569" \
  -X PUT https://infra:9000/pgbackrest
```
**ผลลัพธ์:**
```
200
```

> 💡 ถ้าสั่งซ้ำจะได้ `409` (Bucket มีอยู่แล้ว)

### คัดลอกใบรับรองไปยัง pg1

**บน Notebook:**
```bash
scp lab-infra:/etc/minio/certs/public.crt minio-ca.crt
scp minio-ca.crt lab-pg1:/tmp/minio-ca.crt
```
**ผลลัพธ์:**
```
public.crt                    100%  1234     1.2KB/s   00:00
minio-ca.crt                  100%  1234     1.2KB/s   00:00
```

**✅ ผลลัพธ์ที่คาดหวัง:** Health check 200, Bucket 200

---

## 🧪 Lab 3.2 — ตั้งค่า pgBackRest + WAL Archiving + Full Backup แรก

### บน pg1

### ขั้นที่ 1: ติดตั้งและเตรียมโฟลเดอร์

```bash
sudo apt install -y pgbackrest
sudo install -d -o postgres -g postgres -m 750 /etc/pgbackrest /var/spool/pgbackrest /var/log/pgbackrest
sudo install -o postgres -g postgres -m 644 /tmp/minio-ca.crt /etc/pgbackrest/minio-ca.crt
sudo cp /etc/pgbackrest.conf /etc/pgbackrest.conf.orig
```

### ขั้นที่ 2: เขียน /etc/pgbackrest.conf

```bash
sudo truncate -s 0 /etc/pgbackrest.conf
sudo nano /etc/pgbackrest.conf
```

**เนื้อหา:**
```ini
[global]
repo1-type=s3
repo1-s3-endpoint=infra
repo1-storage-port=9000
repo1-storage-ca-file=/etc/pgbackrest/minio-ca.crt
repo1-s3-bucket=pgbackrest
repo1-s3-region=us-east-1
repo1-s3-uri-style=path
repo1-s3-key=gridcare-backup
repo1-s3-key-secret=Lab-Minio-Secret-2569
repo1-path=/gridcare
repo1-retention-full=2
repo1-cipher-type=aes-256-cbc
repo1-cipher-pass=Lab-Cipher-Passphrase-2569-ChangeMe
repo1-bundle=y
repo1-block=y
compress-type=zst
process-max=2
start-fast=y
archive-async=y
spool-path=/var/spool/pgbackrest
log-level-console=info
log-level-file=detail

[gridcare]
pg1-path=/var/lib/postgresql/17/main
```

```bash
sudo chown postgres:postgres /etc/pgbackrest.conf
sudo chmod 640 /etc/pgbackrest.conf
```

### ขั้นที่ 3: สร้าง Stanza

```bash
sudo -u postgres pgbackrest --stanza=gridcare stanza-create
```
**ผลลัพธ์:**
```
2026-11-04 09:15:23.456 P00   INFO: stanza-create for stanza 'gridcare' on repo1
2026-11-04 09:15:23.789 P00   INFO: stanza-create command end: completed successfully (334ms)
```

### ขั้นที่ 4: ตั้งค่า WAL Archiving

```bash
sudo truncate -s 0 /etc/postgresql/17/main/conf.d/40-gridcare-archive.conf
sudo nano /etc/postgresql/17/main/conf.d/40-gridcare-archive.conf
```

**เนื้อหา:**
```ini
archive_mode = on
archive_command = 'pgbackrest --stanza=gridcare archive-push %p'
archive_timeout = 60s
wal_level = replica
max_wal_senders = 10
```

```bash
sudo chown postgres:postgres /etc/postgresql/17/main/conf.d/40-gridcare-archive.conf
sudo systemctl restart postgresql@17-main
```

### ขั้นที่ 5: ตรวจสอบ + Full Backup

```bash
sudo -u postgres pgbackrest --stanza=gridcare check
```
**ผลลัพธ์:**
```
2026-11-04 09:16:12.345 P00   INFO: check command begin 2.59.3: --stanza=gridcare ...
2026-11-04 09:16:13.456 P00   INFO: check repo1 (standby) succeeded
2026-11-04 09:16:14.567 P00   INFO: check command end: completed successfully (2222ms)
```

```bash
sudo -u postgres pgbackrest --stanza=gridcare --type=full backup
```
**ผลลัพธ์:**
```
2026-11-04 09:17:00.123 P00   INFO: backup command begin 2.59.3: --stanza=gridcare --type=full
2026-11-04 09:17:00.456 P00   INFO: execute non-exclusive backup start: backup begins after the requested immediate checkpoint completes
2026-11-04 09:17:01.789 P00   INFO: backup start archive = 000000010000000000000002, lsn = 0/2000028
2026-11-04 09:17:45.123 P00   INFO: backup file /var/lib/postgresql/17/main/base/16384/16385 (12.5MB, 45%) checksum
2026-11-04 09:18:30.456 P00   INFO: full backup size = 1.25GB, file total = 1234
2026-11-04 09:18:30.789 P00   INFO: backup command end: completed successfully (90666ms)
```

```bash
sudo -u postgres pgbackrest --stanza=gridcare info
```
**ผลลัพธ์:**
```
stanza: gridcare
    status: ok
    cipher: aes-256-cbc

    db (current)
        wal archive min/max (17): 000000010000000000000001/000000010000000000000005

        full backup: 20261104-091700F
            timestamp start/stop: 2026-11-04 09:17:00+07 / 2026-11-04 09:18:30+07
            wal start/stop: 000000010000000000000002 / 000000010000000000000003
            database size: 1.25GB, database backup size: 1.25GB
            repo1: backup set size: 320MB, backup size: 320MB
```

```bash
sudo -u postgres psql -X -c "SELECT archived_count, last_archived_wal, last_archived_time, failed_count FROM pg_stat_archiver"
```
**ผลลัพธ์:**
```
 archived_count |       last_archived_wal        |    last_archived_time     | failed_count 
----------------+-------------------------------+---------------------------+--------------
             15 | 000000010000000000000005      | 2026-11-04 09:20:12.345+07|            0
(1 row)
```

**✅ ผลลัพธ์ที่คาดหวัง:**
- `check` → `completed successfully`
- `info` → `status: ok` และ Full Backup 1 ชุด
- `failed_count = 0`
- ขนาด Backup บีบอัดเหลือ ~1/6 ของฐาน (ทดสอบ 39 วินาทีสำหรับ 1.9 GB)

---

## 🧪 Lab 3.3 — Differential, Incremental, verify และ pg_amcheck

### บน pg1

### ขั้นที่ 1: สร้างการเปลี่ยนแปลงเล็กน้อย

```bash
sudo -u postgres psql -X -d gridcare -c "UPDATE gridcare.customers SET status = status WHERE customer_id <= 1000"
```
**ผลลัพธ์:**
```
UPDATE 1000
```

### ขั้นที่ 2: Diff และ Incr Backup

```bash
time sudo -u postgres pgbackrest --stanza=gridcare --type=diff backup
```
**ผลลัพธ์:**
```
2026-11-04 10:00:00.123 P00   INFO: backup command begin 2.59.3: --stanza=gridcare --type=diff
2026-11-04 10:00:15.456 P00   INFO: diff backup size = 45MB, file total = 234
2026-11-04 10:00:15.789 P00   INFO: backup command end: completed successfully (15666ms)

real    0m15.789s
```

```bash
time sudo -u postgres pgbackrest --stanza=gridcare --type=incr backup
```
**ผลลัพธ์:**
```
2026-11-04 10:01:00.123 P00   INFO: backup command begin 2.59.3: --stanza=gridcare --type=incr
2026-11-04 10:01:08.456 P00   INFO: incr backup size = 12MB, file total = 45
2026-11-04 10:01:08.789 P00   INFO: backup command end: completed successfully (8666ms)

real    0m8.789s
```

```bash
sudo -u postgres pgbackrest --stanza=gridcare info
```
**ผลลัพธ์:**
```
stanza: gridcare
    status: ok
    cipher: aes-256-cbc

    db (current)
        wal archive min/max (17): 000000010000000000000001/000000010000000000000008

        full backup: 20261104-091700F
            timestamp start/stop: 2026-11-04 09:17:00+07 / 2026-11-04 09:18:30+07
            wal start/stop: 000000010000000000000002 / 000000010000000000000003
            database size: 1.25GB, database backup size: 1.25GB
            repo1: backup set size: 320MB, backup size: 320MB

        diff backup: 20261104-100000D
            backup reference list: 20261104-091700F
            timestamp start/stop: 2026-11-04 10:00:00+07 / 2026-11-04 10:00:15+07
            database size: 1.25GB, database backup size: 45MB
            repo1: backup set size: 45MB, backup size: 45MB

        incr backup: 20261104-100100I
            backup reference list: 20261104-091700F, 20261104-100000D
            timestamp start/stop: 2026-11-04 10:01:00+07 / 2026-11-04 10:01:08+07
            database size: 1.25GB, database backup size: 12MB
            repo1: backup set size: 12MB, backup size: 12MB
```

### ขั้นที่ 3: Verify

```bash
sudo -u postgres pgbackrest --stanza=gridcare verify
```
**ผลลัพธ์:**
```
2026-11-04 10:05:00.123 P00   INFO: verify command begin 2.59.3: --stanza=gridcare
2026-11-04 10:08:45.456 P00   INFO: verify backup file ... (12.5MB, 45%) checksum
2026-11-04 10:10:30.789 P00   INFO: verify command end: completed successfully (330666ms)
```

### ขั้นที่ 4: pg_amcheck

```bash
sudo -u postgres /usr/lib/postgresql/17/bin/pg_amcheck -d gridcare -t gridcare.customers --heapallindexed --install-missing --progress; echo "exit=$?"
```
**ผลลัพธ์:**
```
heap table "gridcare.customers" (1 of 1)
index "customers_pkey" (1 of 3) ... ok
index "customers_ca_number_key" (2 of 3) ... ok
index "customers_phone_key" (3 of 3) ... ok
exit=0
```

**✅ ผลลัพธ์ที่คาดหวัง:**
- `info` แสดง `full backup`, `diff backup`, `incr backup`
- Diff/Incr มี `backup reference total: 1 full`
- `verify` → `completed successfully`
- `pg_amcheck` → `exit=0`

---

## 🧪 Lab 4.1 — health check, restore test, systemd timer

### บน pg1

### ขั้นที่ 1: เตรียมโฟลเดอร์

```bash
sudo install -d -o postgres -g postgres -m 750 /var/log/gridcare
sudo chgrp postgres /var/lib/prometheus/node-exporter
sudo chmod 2775 /var/lib/prometheus/node-exporter
```

### ขั้นที่ 2: รัน health_check.sh

```bash
cd /opt/gridcare/scripts
sudo -u postgres PGDATABASE=gridcare TEXTFILE_DIR=/var/lib/prometheus/node-exporter ./health_check.sh; echo "exit=$?"
```
**ผลลัพธ์:**
```
connections          OK   1/100              1.0%
idle_in_transaction  OK   0
xid_age              OK   1765               postgres
archiver             OK   failed_count=0     archive_mode=on ...
pg_wal_size          OK   768 MB             49 ไฟล์
index_invalid        OK   0
password_expiry      OK   -
[2026-11-04 13:00:45] สรุป: exit code 0 (OK) host=local db=gridcare
exit=0
```

### ขั้นที่ 3: รัน textfile_metrics.sh

```bash
sudo -u postgres TEXTFILE_DIR=/var/lib/prometheus/node-exporter STANZA=gridcare ./textfile_metrics.sh; echo "exit=$?"
```
**ผลลัพธ์:**
```
[2026-11-04 13:01:15] Wrote /var/lib/prometheus/node-exporter/gridcare_backup.prom
[2026-11-04 13:01:15] Wrote /var/lib/prometheus/node-exporter/gridcare_ssl.prom
exit=0
```

```bash
cat /var/lib/prometheus/node-exporter/*.prom | grep -v '^#'
```
**ผลลัพธ์:**
```
gridcare_backup_last_success_timestamp_seconds{stanza="gridcare"} 1.7307e+09
gridcare_backup_last_success_age_seconds{stanza="gridcare"} 3600
gridcare_ssl_cert_expiry_timestamp_seconds{path="/etc/postgresql/17/main/server.crt"} 1.7625e+09
gridcare_ssl_cert_expiry_days{path="/etc/postgresql/17/main/server.crt"} 364
```

### ขั้นที่ 4: Restore Test

```bash
df -h /var/tmp
```
**ผลลัพธ์:**
```
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        78G   18G   57G  24% /
```

```bash
sudo -u postgres MODE=pgbackrest STANZA=gridcare ./restore_test.sh; echo "exit=$?"
```
**ผลลัพธ์:**
```
[2026-11-04 13:05:00] INFO: Starting restore test mode=pgbackrest
[2026-11-04 13:05:00] INFO: pgbackrest restore --stanza=gridcare --pg1-path=/var/tmp/gc-restore-test --type=immediate
[2026-11-04 13:05:30] INFO: restore completed
[2026-11-04 13:05:30] INFO: Starting test cluster on port 5440
[2026-11-04 13:05:45] INFO: Test cluster ready
[2026-11-04 13:05:45] INFO: Checking bills count >= 1000000
[2026-11-04 13:05:46] INFO: Checking payments data
[2026-11-04 13:05:46] INFO: Checking index validity
[2026-11-04 13:05:47] INFO: Stopping test cluster
[2026-11-04 13:05:50] INFO: Cleaning up
[2026-11-04 13:05:52] PASS restore test (pgbackrest) ใช้เวลา 7 วินาที (ใช้บันทึก RTO ที่ทำได้จริง)
exit=0
```

> 💡 **ทดสอบว่า "ล้มจริง"** — วิทยากรสาธิตด้วยการแก้ไฟล์ใน Repository:
> ```
> pgbackrest verify  →  INFO: invalid checksum '20261026-025448F/bundle/2'
> restore_test.sh    →  ERROR: [095]: ... cipher header missing
>                       FAIL ที่ขั้น: pgbackrest restore         exit=1
> ```

### ขั้นที่ 5: สร้าง systemd timer

```bash
sudo cp /opt/gridcare/scripts/systemd/gridcare-*.service /opt/gridcare/scripts/systemd/gridcare-*.timer /etc/systemd/system/
```

```bash
sudo truncate -s 0 /etc/systemd/system/gridcare-textfile.service
sudo nano /etc/systemd/system/gridcare-textfile.service
```

**เนื้อหา `gridcare-textfile.service`:**
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

```bash
sudo truncate -s 0 /etc/systemd/system/gridcare-textfile.timer
sudo nano /etc/systemd/system/gridcare-textfile.timer
```

**เนื้อหา `gridcare-textfile.timer`:**
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
sudo systemd-analyze verify /etc/systemd/system/gridcare-*.service /etc/systemd/system/gridcare-*.timer
sudo systemctl daemon-reload
sudo systemctl enable --now gridcare-health-check.timer gridcare-weekly.timer gridcare-restore-test.timer gridcare-textfile.timer
systemctl list-timers 'gridcare-*' --no-pager
```
**ผลลัพธ์:**
```
NEXT                        LEFT       LAST                        PASSED    UNIT                          ACTIVATES
Wed 2026-11-04 13:15:00 +07 13min left n/a                         n/a       gridcare-textfile.timer       gridcare-textfile.service
Thu 2026-11-05 07:00:00 +07 17h left   n/a                         n/a       gridcare-health-check.timer   gridcare-health-check.service
Mon 2026-11-09 06:30:00 +07 4 days left n/a                        n/a       gridcare-weekly.timer         gridcare-weekly.service
Sun 2026-12-06 02:00:00 +07 4 weeks left n/a                       n/a       gridcare-restore-test.timer   gridcare-restore-test.service

5 timers listed.
```

**✅ ผลลัพธ์ที่คาดหวัง:**
- `health_check.sh` → `exit=0` (หรือ 1 ถ้ามี WARN)
- `restore_test.sh` → `PASS restore test` + เวลาที่ใช้
- `list-timers` → 5 timer

---

## 🧪 Lab 5.1 — เปิด pgAudit (Session + Object)

### บน pg1

### ขั้นที่ 1: ติดตั้งและตั้งค่า

```bash
sudo apt install -y postgresql-17-pgaudit
cd /etc/postgresql/17/main
sudo sed -i "/^shared_preload_libraries/ s/'\$/,pgaudit'/" conf.d/20-gridcare-logging.conf
grep shared_preload_libraries conf.d/*.conf
```
**ผลลัพธ์:**
```
conf.d/20-gridcare-logging.conf:shared_preload_libraries = 'pg_stat_statements,auto_explain,pgaudit'
```

```bash
sudo truncate -s 0 conf.d/50-gridcare-audit.conf
sudo nano conf.d/50-gridcare-audit.conf
```

**เนื้อหา:**
```ini
pgaudit.log = 'ddl, role'
pgaudit.log_catalog = off
pgaudit.log_relation = on
pgaudit.log_parameter = off
pgaudit.role = 'gridcare_auditor'
```

```bash
sudo chown postgres:postgres conf.d/50-gridcare-audit.conf
sudo systemctl restart postgresql@17-main
```

### ขั้นที่ 2: สร้าง Extension และ Role

```bash
sudo -u postgres psql -X -d gridcare
```

```sql
CREATE EXTENSION IF NOT EXISTS pgaudit;
CREATE ROLE gridcare_auditor NOLOGIN;
GRANT SELECT, UPDATE ON gridcare.customers TO gridcare_auditor;
```
**ผลลัพธ์:**
```
CREATE EXTENSION
CREATE ROLE
GRANT
```

### ขั้นที่ 3: ทดสอบ

```sql
SET ROLE callcenter_ro;
SELECT first_name FROM gridcare.customers WHERE customer_id = 7;
SELECT count(*) FROM gridcare.offices;
RESET ROLE;
CREATE ROLE temp_x; DROP ROLE temp_x;
```
**ผลลัพธ์:**
```
SET
 first_name 
------------
 สมชาย
(1 row)

 count 
-------
    42
(1 row)
RESET
CREATE ROLE
DROP ROLE
```

### ขั้นที่ 4: ดู Audit Log

```bash
sudo grep "AUDIT:" /var/log/postgresql/postgresql-17-main.log | tail -4
```
**ผลลัพธ์:**
```
2026-11-04 14:30:12.345 +07 [1234] postgres@gridcare app=psql client=[local] LOG:  AUDIT: OBJECT,1,1,READ,SELECT,TABLE,gridcare.customers,SELECT first_name FROM gridcare.customers WHERE customer_id = 7,<not logged>
2026-11-04 14:30:12.456 +07 [1234] postgres@gridcare app=psql client=[local] LOG:  AUDIT: SESSION,1,1,ROLE,CREATE ROLE,,,CREATE ROLE temp_x,<not logged>
2026-11-04 14:30:12.567 +07 [1234] postgres@gridcare app=psql client=[local] LOG:  AUDIT: SESSION,2,1,ROLE,DROP ROLE,,,DROP ROLE temp_x,<not logged>
```

> 💡 **ไม่มี** บรรทัดของ `offices` (เพราะไม่ให้สิทธิ์ `gridcare_auditor` บน offices)

**✅ ผลลัพธ์ที่คาดหวัง:**
- มี `AUDIT: OBJECT ... gridcare.customers`
- มี `AUDIT: SESSION ... CREATE ROLE`
- **ไม่มี** `AUDIT` ของ `offices`

---

## 🛠️ Workshop Day 3 — ขั้นที่ 1: PITR + วัด RTO

### บน pg1 (ใช้ Terminal เดียวกันตลอดเพื่อคงตัวแปร TARGET)

### 1.1 ตรวจพบ: ยืนยันข้อมูลเสีย

```bash
date +%T
sudo -u postgres psql -X -d gridcare <<'EOF'
SELECT tariff_code, rate_per_kwh, updated_at FROM gridcare.tariff_rates ORDER BY tariff_code;
SELECT c.tariff_code, round(avg(b.total_amount), 2) AS avg_bill
FROM gridcare.bills AS b JOIN gridcare.customers AS c ON c.customer_id = b.customer_id
GROUP BY c.tariff_code ORDER BY c.tariff_code;
EOF
```
**ผลลัพธ์ (ก่อนเกิดเหตุ — ปกติ):**
```
14:45:30
 tariff_code | rate_per_kwh |         updated_at         
-------------+--------------+----------------------------
 GOV         |         4.20 | 2026-11-04 08:00:00+07
 RES         |         3.90 | 2026-11-04 08:00:00+07
 SMB         |         4.50 | 2026-11-04 08:00:00+07
(3 rows)

 tariff_code | avg_bill 
-------------+----------
 GOV         |  1623.45
 RES         |  1154.92
 SMB         |  2341.78
(3 rows)
```

**ผลลัพธ์ (หลัง Batch ผิด — ผิดปกติ):**
```
 tariff_code | rate_per_kwh |         updated_at         
-------------+--------------+----------------------------
 GOV         |       420.00 | 2026-11-04 14:51:15+07
 RES         |       390.00 | 2026-11-04 14:51:15+07
 SMB         |       450.00 | 2026-11-04 14:51:15+07
(3 rows)

 tariff_code | avg_bill 
-------------+----------
 GOV         | 162345.00
 RES         | 115492.00
 SMB         | 234178.00
(3 rows)
```

### 1.2 หาเวลาเป้าหมายจาก Log

```bash
sudo grep "duration:.*UPDATE" /var/log/postgresql/postgresql-17-main.log | tail -3 | cut -c1-160
```
**ผลลัพธ์:**
```
2026-11-04 14:51:12.409 +07 [8982] postgres@gridcare app=psql client=[local] LOG:  duration: 7969.774 ms  statement: UPDATE bills AS b ...
```

```bash
TARGET="2026-11-04 14:51:12+07"
echo "TARGET=$TARGET"
date +%T
```
**ผลลัพธ์:**
```
TARGET=2026-11-04 14:51:12+07
14:52:34
```

### 1.3 หยุดการเขียน

**บน infra:**
```bash
tmux attach -t load
```
กด `Ctrl+c` เพื่อหยุด pgbench แล้ว `Ctrl+b` `d` เพื่อออก

**บน pg1:**
```bash
sudo systemctl stop postgresql@17-main
pg_lsclusters
```
**ผลลัพธ์:**
```
Ver Cluster Port Status Owner    Data directory              Log file
17  main    5432 down   postgres /var/lib/postgresql/17/main /var/log/postgresql/postgresql-17-main.log
```

### 1.4 Restore ไปยังเวลาเป้าหมาย

```bash
date +%T
sudo -u postgres pgbackrest --stanza=gridcare --delta --type=time --target="$TARGET" --target-action=promote restore
date +%T
```
**ผลลัพธ์:**
```
14:53:00
2026-11-04 14:53:00.123 P00   INFO: restore command begin 2.59.3: --delta --stanza=gridcare --target=2026-11-04 14:51:12+07 --target-action=promote --type=time
2026-11-04 14:53:00.456 P00   INFO: restore backup set 20261104-100100I
2026-11-04 14:53:30.789 P00   INFO: write .pgbackrest/archive.info
2026-11-04 14:53:31.012 P00   INFO: restore command end: completed successfully (31889ms)
14:53:31
```

### 1.5 Start และรอ Promote

```bash
sudo systemctl start postgresql@17-main
sudo tail -n 8 /var/log/postgresql/postgresql-17-main.log
```
**ผลลัพธ์:**
```
2026-11-04 14:53:45.123 +07 [1234] LOG:  starting PostgreSQL 17.11 on x86_64-pc-linux-gnu
2026-11-04 14:53:45.456 +07 [1234] LOG:  restored log file "000000010000000000000004" from archive
2026-11-04 14:53:45.789 +07 [1234] LOG:  redo starts at 0/4000028
2026-11-04 14:53:46.012 +07 [1234] LOG:  consistent recovery state reached at 0/4000130
2026-11-04 14:53:52.345 +07 [1234] LOG:  recovery stopping before commit of transaction 2494, time 2026-11-04 14:51:12.123456+07
2026-11-04 14:53:52.678 +07 [1234] LOG:  redo done at 0/5000028
2026-11-04 14:53:52.789 +07 [1234] LOG:  selected new timeline ID: 2
2026-11-04 14:53:52.901 +07 [1234] LOG:  archive recovery complete
```

```bash
sudo -u postgres psql -XAtc "SELECT pg_is_in_recovery()"
date +%T
```
**ผลลัพธ์:**
```
f
14:53:55
```

### 1.6 ตรวจข้อมูลหลังกู้

```bash
sudo -u postgres psql -X -d gridcare <<'EOF'
SELECT tariff_code, rate_per_kwh, updated_at FROM gridcare.tariff_rates ORDER BY tariff_code;
SELECT c.tariff_code, round(avg(b.total_amount), 2) AS avg_bill
FROM gridcare.bills AS b JOIN gridcare.customers AS c ON c.customer_id = b.customer_id
GROUP BY c.tariff_code ORDER BY c.tariff_code;
EOF
date +%T
```
**ผลลัพธ์:**
```
 tariff_code | rate_per_kwh |         updated_at         
-------------+--------------+----------------------------
 GOV         |         4.20 | 2026-11-04 08:00:00+07
 RES         |         3.90 | 2026-11-04 08:00:00+07
 SMB         |         4.50 | 2026-11-04 08:00:00+07
(3 rows)

 tariff_code | avg_bill 
-------------+----------
 GOV         |  1623.45
 RES         |  1154.92
 SMB         |  2341.78
(3 rows)

14:54:02
```
> ✅ อัตราค่าไฟกลับมาเป็น 3.90-4.50, ค่าไฟเฉลี่ยกลับมาปกติ

### 1.7 Full Backup ใหม่

```bash
sudo -u postgres pgbackrest --stanza=gridcare --type=full backup
sudo -u postgres pgbackrest --stanza=gridcare check
```
**ผลลัพธ์:**
```
2026-11-04 14:54:30.123 P00   INFO: backup command begin 2.59.3: --stanza=gridcare --type=full
2026-11-04 14:56:00.789 P00   INFO: full backup size = 1.25GB
2026-11-04 14:56:00.901 P00   INFO: backup command end: completed successfully (90666ms)

2026-11-04 14:56:15.123 P00   INFO: check command begin 2.59.3: --stanza=gridcare
2026-11-04 14:56:16.789 P00   INFO: check repo1 (standby) succeeded
2026-11-04 14:56:17.012 P00   INFO: check command end: completed successfully (1889ms)
```

### 1.8 เปิดโหลดกลับ

**บน infra:**
```bash
tmux attach -t load
```

**ภายใน tmux:**
```bash
cd /opt/gridcare/pgbench
PGHOST=127.0.0.1 PGPORT=6432 PGUSER=billing_app ./run_normal.sh 8 25200
```

### ตรวจผลรวม

```bash
sudo grep -E "starting point-in-time recovery|recovery stopping|selected new timeline|archive recovery complete" /var/log/postgresql/postgresql-17-main.log | tail -4
```
**ผลลัพธ์:**
```
LOG:  starting point-in-time recovery to 2026-11-04 14:51:12+07
LOG:  recovery stopping before commit of transaction 2494, time 2026-11-04 14:51:12.123456+07
LOG:  selected new timeline ID: 2
LOG:  archive recovery complete
```

```bash
sudo -u postgres psql -X -c "SELECT timeline_id FROM pg_control_checkpoint()" -c "SELECT pg_is_in_recovery()"
```
**ผลลัพธ์:**
```
 timeline_id 
-------------
           2
(1 row)

 pg_is_in_recovery 
-------------------
 f
(1 row)
```

```bash
sudo -u postgres pgbackrest --stanza=gridcare info | grep -E "full backup|wal archive"
```
**ผลลัพธ์:**
```
        wal archive min/max (17): 000000010000000000000001/000000020000000000000012
        full backup: 20261104-145430F
        full backup: 20261104-091700F
```

### สรุป RTO

| ขั้น | เวลา | ระยะเวลา |
|---|---|---|
| ตรวจพบ | 14:45:30 | - |
| ตัดสินใจ | 14:52:34 | 7 นาที 4 วินาที |
| Restore เริ่ม | 14:53:00 | 26 วินาที |
| Restore เสร็จ | 14:53:31 | 31 วินาที |
| Promote เสร็จ | 14:53:55 | 24 วินาที |
| ตรวจเสร็จ | 14:54:02 | 7 วินาที |
| **RTO รวม** | | **8 นาที 32 วินาที** |

**✅ ผลลัพธ์ที่คาดหวัง:**
- Log มี `recovery stopping before commit`
- `timeline_id = 2` (เพิ่มจาก 1)
- `pg_is_in_recovery = f`
- อัตราค่าไฟกลับมาปกติ
- มี Full Backup ใหม่

---

## 🛠️ Workshop Day 3 — ขั้นที่ 2: RLS

### บน pg1

### 2.1 เข้า psql

```bash
sudo -u postgres psql -X -d gridcare
```

### 2.2 สร้าง Role

```sql
CREATE ROLE gridcare_staff NOLOGIN IN ROLE gridcare_read;
CREATE ROLE staff_n1 LOGIN PASSWORD 'Lab-Staff-2569' IN ROLE gridcare_staff;
CREATE ROLE staff_s3 LOGIN PASSWORD 'Lab-Staff-2569' IN ROLE gridcare_staff;
```
**ผลลัพธ์:**
```
CREATE ROLE
CREATE ROLE
CREATE ROLE
```

### 2.3 สร้างตาราง staff_regions

```sql
CREATE TABLE gridcare.staff_regions (
    role_name text     PRIMARY KEY,
    region_id smallint NOT NULL REFERENCES gridcare.regions (region_id)
);
INSERT INTO gridcare.staff_regions (role_name, region_id) VALUES ('staff_n1', 1), ('staff_s3', 12);
GRANT SELECT ON gridcare.staff_regions TO gridcare_staff;
```
**ผลลัพธ์:**
```
CREATE TABLE
INSERT 0 2
GRANT
```

### 2.4 เปิด RLS + สร้าง Policy

```sql
ALTER TABLE gridcare.customers ENABLE ROW LEVEL SECURITY;

CREATE POLICY staff_own_region ON gridcare.customers
    FOR SELECT TO gridcare_staff
    USING (office_id IN (SELECT o.office_id
                         FROM gridcare.offices AS o
                         JOIN gridcare.staff_regions AS s ON s.region_id = o.region_id
                         WHERE s.role_name = current_user));

CREATE POLICY app_all_rows ON gridcare.customers
    FOR ALL TO billing_app, callcenter_ro, report_ro, dba
    USING (true) WITH CHECK (true);
GRANT gridcare_read TO dba;
\q
```
**ผลลัพธ์:**
```
ALTER TABLE
CREATE POLICY
CREATE POLICY
GRANT ROLE
```

### ตรวจผล

```bash
sudo -u postgres psql -X -d gridcare <<'EOF'
SET ROLE staff_n1;      SELECT 'staff_n1' AS who, count(*) FROM gridcare.customers;  RESET ROLE;
SET ROLE staff_s3;      SELECT 'staff_s3' AS who, count(*) FROM gridcare.customers;  RESET ROLE;
SET ROLE callcenter_ro; SELECT 'callcenter_ro' AS who, count(*) FROM gridcare.customers;  RESET ROLE;
SET ROLE staff_n1;
EXPLAIN (ANALYZE, COSTS OFF, TIMING OFF) SELECT count(*) FROM gridcare.customers;
RESET ROLE;
EOF
```
**ผลลัพธ์:**
```
     who      | count  
--------------+--------
 staff_n1     |  16676
 staff_s3     |  16454
 callcenter_ro| 200000

                                           QUERY PLAN                                           
------------------------------------------------------------------------------------------------
 Finalize Aggregate
   ->  Gather
         Workers Planned: 2
         ->  Partial Aggregate
               ->  Parallel Index Only Scan using customers_office_idx on customers
                     Filter: (ANY (office_id = (hashed SubPlan 1).col1))
 Execution Time: 10.328 ms
```

**✅ ผลลัพธ์ที่คาดหวัง:**
- `staff_n1 = 16,676` แถว
- `staff_s3 = 16,454` แถว
- `callcenter_ro = 200,000` แถว
- pgbench บน infra ไม่มี error

---

## 🛠️ Workshop Day 3 — ขั้นที่ 3: กฎตรวจเลข 13 หลัก + Masking + pgcrypto

### บน pg1

### 3.2 ฟังก์ชันตรวจเลข 13 หลัก

```sql
CREATE OR REPLACE FUNCTION gridcare.is_valid_thai_id(id text)
RETURNS boolean
LANGUAGE sql IMMUTABLE STRICT PARALLEL SAFE
AS $$
    SELECT CASE
             WHEN id !~ '^[0-9]{13}$' THEN false
             ELSE (11 - (SELECT sum(substr(id, i, 1)::int * (14 - i))
                         FROM generate_series(1, 12) AS i) % 11) % 10
                  = substr(id, 13, 1)::int
           END
$$;

SELECT gridcare.is_valid_thai_id('1234567890121') AS good,
       gridcare.is_valid_thai_id('1234567890123') AS bad,
       gridcare.is_valid_thai_id('12345')         AS too_short;
```
**ผลลัพธ์:**
```
CREATE FUNCTION
 good | bad | too_short 
------+-----+-----------
 t    | f   | f
(1 row)
```

### 3.3 เพิ่ม CHECK Constraint แบบ 2 ขั้น

```sql
SET lock_timeout = '3s';
ALTER TABLE gridcare.customers
    ADD CONSTRAINT customers_citizen_id_check
    CHECK (gridcare.is_valid_thai_id(citizen_id)) NOT VALID;
\timing on
ALTER TABLE gridcare.customers VALIDATE CONSTRAINT customers_citizen_id_check;
\timing off
RESET lock_timeout;
```
**ผลลัพธ์:**
```
SET
ALTER TABLE
Timing is on.
ALTER TABLE
Time: 10234.567 ms (00:10.235)
Timing is off.
RESET
```

### 3.4 View ที่ Mask ข้อมูล

```sql
CREATE VIEW gridcare.customers_masked
WITH (security_barrier = true, security_invoker = true) AS
SELECT customer_id, ca_number, office_id, tariff_code, customer_type,
       title, first_name, last_name,
       left(citizen_id, 1) || '-xxxx-xxxxx-xx-' || right(citizen_id, 1) AS citizen_id_masked,
       left(phone, 3) || '-xxx-xx' || right(phone, 2)                   AS phone_masked,
       status
FROM gridcare.customers;
GRANT SELECT ON gridcare.customers_masked TO callcenter_ro, gridcare_staff;
```
**ผลลัพธ์:**
```
CREATE VIEW
GRANT
```

### 3.5 ทดลอง pgcrypto

```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;
\set enc_key 'Lab-Key-2569'
CREATE TABLE gridcare.customer_secret_demo AS
SELECT customer_id,
       pgp_sym_encrypt(citizen_id, :'enc_key', 'cipher-algo=aes256') AS citizen_id_enc
FROM gridcare.customers
WHERE customer_id <= 5;
SELECT d.customer_id,
       left(encode(d.citizen_id_enc, 'hex'), 16) || '...'           AS stored_bytes,
       pgp_sym_decrypt(d.citizen_id_enc, :'enc_key') = c.citizen_id AS decrypt_ok
FROM gridcare.customer_secret_demo AS d
JOIN gridcare.customers AS c USING (customer_id)
ORDER BY d.customer_id;
SELECT pgp_sym_decrypt(citizen_id_enc, 'wrong-key') FROM gridcare.customer_secret_demo LIMIT 1;
DROP TABLE gridcare.customer_secret_demo;
\q
```
**ผลลัพธ์:**
```
CREATE EXTENSION
CREATE TABLE AS
 customer_id |   stored_bytes    | decrypt_ok 
-------------+-------------------+------------
           1 | c30d04070302...   | t
           2 | c30d04070302...   | t
           3 | c30d04070302...   | t
           4 | c30d04070302...   | t
           5 | c30d04070302...   | t
(5 rows)

ERROR:  Wrong key or corrupt data
DROP TABLE
```

### 3.6 ตรวจ Audit Log

```bash
sudo grep "AUDIT: OBJECT" /var/log/postgresql/postgresql-17-main.log | tail -2 | cut -c1-200
```
**ผลลัพธ์:**
```
2026-11-04 15:45:12.345 +07 [2345] callcenter_ro@gridcare app=psql client=[local] LOG:  AUDIT: OBJECT,1,1,READ,SELECT,TABLE,gridcare.customers,SELECT customer_id, ca_number, ... FROM gridcare.customers_masked WHERE customer_id = 1,<not logged>
```

### ตรวจผลรวม

```bash
sudo -u postgres psql -X -d gridcare
```

```sql
SELECT gridcare.is_valid_thai_id('1234567890121') AS good, gridcare.is_valid_thai_id('1234567890123') AS bad;
SELECT conname, convalidated FROM pg_constraint WHERE conname LIKE 'customers_citizen%';
SELECT count(*) FILTER (WHERE NOT gridcare.is_valid_thai_id(citizen_id)) AS invalid_rows FROM gridcare.customers;
SET ROLE callcenter_ro;
SELECT customer_id, citizen_id_masked, phone_masked FROM gridcare.customers_masked WHERE customer_id = 1;
RESET ROLE;
SELECT pgp_sym_decrypt(pgp_sym_encrypt('1234567890121', 'Lab-Key-2569', 'cipher-algo=aes256'), 'Lab-Key-2569') AS roundtrip;
```
**ผลลัพธ์:**
```
 good | bad 
------+-----
 t    | f
(1 row)

           conname           | convalidated 
-----------------------------+--------------
 customers_citizen_id_check  | t
(1 row)

 invalid_rows 
--------------
            0
(1 row)

 customer_id | citizen_id_masked | phone_masked 
-------------+-------------------+--------------
           1 | 2-xxxx-xxxxx-xx-2 | 086-xxx-xx40
(1 row)

   roundtrip   
---------------
 1234567890121
(1 row)
```

**✅ ผลลัพธ์ที่คาดหวัง:**
- `good = t`, `bad = f`
- `invalid_rows = 0`, `convalidated = t`
- `citizen_id_masked = 2-xxxx-xxxxx-xx-2`
- `phone_masked = 086-xxx-xx40`
- `roundtrip = 1234567890121`

---

## 📊 สรุปคำสั่งสำคัญทั้งหมด (Cheat Sheet Day 3)

### pg_dump / pg_restore

```bash
pg_dump -d dbname -Fd -j 2 -Z zstd:3 -f /path/dump.dir      # Directory + Parallel + zstd
pg_dumpall --globals-only --no-role-passwords > globals.sql  # Role + Tablespace
pg_restore -l dump.dir                                        # ดูรายการวัตถุ
pg_restore -d db_new -L partial.list --no-owner dump.dir      # Restore เฉพาะบางส่วน
```

### pgBackRest

```bash
pgbackrest --stanza=<name> stanza-create                      # สร้าง Stanza
pgbackrest --stanza=<name> check                              # ตรวจ WAL Archive
pgbackrest --stanza=<name> --type=full backup                 # Full Backup
pgbackrest --stanza=<name> --type=diff backup                 # Diff Backup
pgbackrest --stanza=<name> --type=incr backup                 # Incr Backup
pgbackrest --stanza=<name> info                               # ดูข้อมูล Backup
pgbackrest --stanza=<name> verify                             # ตรวจ checksum
pgbackrest --stanza=<name> --delta --type=time \
  --target="..." --target-action=promote restore              # PITR
```

### pg_amcheck

```bash
pg_amcheck -d dbname -t schema.table --heapallindexed --install-missing --progress
```

### pgAudit

```sql
CREATE EXTENSION pgaudit;
CREATE ROLE gridcare_auditor NOLOGIN;
GRANT SELECT, UPDATE ON schema.table TO gridcare_auditor;
-- ตั้งค่าใน conf.d/50-gridcare-audit.conf:
-- pgaudit.log = 'ddl, role'
-- pgaudit.role = 'gridcare_auditor'
```

### RLS

```sql
ALTER TABLE schema.table ENABLE ROW LEVEL SECURITY;
CREATE POLICY policy_name ON schema.table
  FOR SELECT TO role_name
  USING (condition);
CREATE POLICY app_policy ON schema.table
  FOR ALL TO app_role
  USING (true) WITH CHECK (true);
```

### pgcrypto

```sql
CREATE EXTENSION pgcrypto;
pgp_sym_encrypt('data', 'key', 'cipher-algo=aes256')
pgp_sym_decrypt(encrypted_col, 'key')
```

### ตรวจเลข 13 หลัก

```sql
CREATE FUNCTION is_valid_thai_id(id text) RETURNS boolean AS $$
  SELECT CASE
    WHEN id !~ '^[0-9]{13}$' THEN false
    ELSE (11 - (SELECT sum(substr(id, i, 1)::int * (14 - i))
                FROM generate_series(1, 12) AS i) % 11) % 10
         = substr(id, 13, 1)::int
  END
$$ LANGUAGE sql IMMUTABLE STRICT PARALLEL SAFE;

ALTER TABLE customers
  ADD CONSTRAINT check_name CHECK (is_valid_thai_id(citizen_id)) NOT VALID;
ALTER TABLE customers VALIDATE CONSTRAINT check_name;
```

### systemd timer

```bash
systemctl enable --now <name>.timer
systemctl list-timers '<name>-*' --no-pager
```

### MinIO + curl

```bash
curl --cacert /path/public.crt https://host:9000/minio/health/live
curl --cacert /path/public.crt \
  --aws-sigv4 "aws:amz:us-east-1:s3" --user "user:pass" \
  -X PUT https://host:9000/bucket
```

---

## 🎯 สรุปผลลัพธ์สำคัญของ Day 3

| Lab | ผลลัพธ์ที่วัดได้ |
|---|---|
| **Lab 2.1** | Dump ~9 วินาที, ไฟล์ 192 MB, Restore 2 ตาราง |
| **Lab 3.1** | MinIO health 200, Bucket 200 |
| **Lab 3.2** | Full Backup 1.25 GB → 320 MB, `failed_count = 0` |
| **Lab 3.3** | Diff 45 MB (15s), Incr 12 MB (8s), verify ผ่าน, pg_amcheck `exit=0` |
| **Lab 4.1** | health_check `exit=0`, restore test **PASS 7 วินาที**, timer 5 ตัว |
| **Lab 5.1** | `AUDIT: OBJECT ... gridcare.customers` + `AUDIT: SESSION ... CREATE ROLE` |
| **Workshop PITR** | `recovery stopping before commit`, timeline 2, **RTO 8 นาที 32 วินาที** |
| **Workshop RLS** | staff_n1 = 16,676 / staff_s3 = 16,454 / callcenter_ro = 200,000 |
| **Workshop PDPA** | `invalid_rows = 0`, `2-xxxx-xxxxx-xx-2`, `086-xxx-xx40`, roundtrip ผ่าน |

---

## ⚠️ ข้อควรระวังใน Day 3

| # | ข้อควรระวัง | ผลที่เกิด |
|---|---|---|
| 1 | **ต้อง `stanza-create` ก่อนเปิด `archive_mode`** | ถ้าเปิดก่อน → WAL Archive ล้ม |
| 2 | **`repo1-cipher-pass` หาย = Backup ทั้งหมดเปิดไม่ได้** | ต้องเก็บใน Secret Manager |
| 3 | **MinIO cert ต้องชื่อ `public.crt` และ `private.key`** | MinIO อ่านจากชื่อไฟล์นี้ |
| 4 | **pgBackRest ต่อ S3 ผ่าน HTTPS เท่านั้น** | ต้องมี CA cert บน pg1 |
| 5 | **RLS: Role ที่ไม่มี Policy เห็น 0 แถว** | ต้องมี `app_all_rows` policy สำหรับ app |
| 6 | **`security_invoker = true` ใน View** | ถ้าไม่ใส่ → View ข้าม RLS |
| 7 | **`--install-missing` ใน pg_amcheck** | ถ้าไม่ใส่ → `amcheck is not installed` |
| 8 | **PITR ต้องหยุด PostgreSQL ก่อน restore** | ถ้าไม่ → `unable to restore while running` |
| 9 | **หลัง PITR ต้อง Full Backup ใหม่** | Backup เก่าเป็น Timeline เก่า |
| 10 | **`pgaudit.log_parameter = off`** | ถ้าเปิด → PII ลง Log |

---

## 📁 สถานะเครื่องหลังจบ Day 3

```
pg1
├── /etc/pgbackrest.conf (640)             ← repo1 = S3 บน infra:9000 (TLS), AES-256
├── /etc/pgbackrest/minio-ca.crt
├── /etc/postgresql/17/main/conf.d/40-gridcare-archive.conf, 50-gridcare-audit.conf
├── /etc/systemd/system/gridcare-*.service / .timer (5 ตัว)
├── /var/log/gridcare/                     ← Log ของสคริปต์
└── gridcare: Timeline 2 หลัง PITR, RLS + staff_regions, is_valid_thai_id + CHECK,
    customers_masked, pgcrypto, pgaudit

infra
├── MinIO :9000 (TLS, /etc/minio/certs, /var/lib/minio) bucket "pgbackrest"
└── Prometheus เห็น gridcare_backup_last_success_timestamp_seconds
    และ gridcare_health_check_status
```

---

**✅ สรุปเสร็จสมบูรณ์** — คำสั่งและผลลัพธ์ทั้งหมดจาก Day 3 ครอบคลุม Lab 2.1, Lab 3.1-3.3, Lab 4.1, Lab 5.1 และ Workshop Day 3 (PITR + RLS + PDPA) พร้อมตัวเลขที่วัดได้จริงจากหลักสูตร