# บทที่ 61–70

> หนังสือ: คู่มือการใช้งาน PostgreSQL สำหรับ DevOps Engineer, Cloud Engineer และ DBA  
> ส่วนที่ 7 Backup, Recovery และ Security  
> โทน: ทางการ กระชับ เน้นใช้งานจริง

---

# บทที่ 61 Backup Strategy, RPO และ RTO

## 1. เรื่อง
การวางแผนกลยุทธ์การ Backup สำหรับ PostgreSQL Production โดยอิงจาก RPO และ RTO

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจ RPO และ RTO อย่างถูกต้อง  
2. เพื่อให้เลือกประเภท Backup ที่เหมาะกับงาน  
3. เพื่อให้วางแผน Backup Retention  
4. เพื่อให้ผูก Backup กับ Incident Response

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- อธิบาย RPO และ RTO  
- เลือก Physical vs Logical Backup  
- วางแผน Retention และ Restore Test  
- กำหนด SLO ของ Backup

## 4. เนื้อหาโดยย่อ
**RPO (Recovery Point Objective)** = ปริมาณข้อมูลที่ยอมรับได้ว่าจะสูญหายเมื่อเกิดเหตุ  
**RTO (Recovery Time Objective)** = เวลาที่ระบบต้องกลับมาใช้งานได้

**Physical Backup** (pgBackRest) — Full + WAL Archive → เหมาะกับ Production  
**Logical Backup** (pg_dump) — Portable, Restore บางส่วนได้  
**WAL Archive** — จำเป็นสำหรับ PITR

## 5. ประโยชน์ที่ได้รับ
- วางแผน Backup ได้เหมาะกับธุรกิจ  
- รู้ว่า RPO/RTO ที่ทำได้จริง  
- ลดความเสี่ยงข้อมูลหาย  
- ทำให้ Audit ผ่าน

## 6. ข้อควรระวัง
- **RPO = 0 ต้องมี Synchronous Replication**  
- **Backup ที่ไม่เคย Restore Test = ไม่มี Backup**  
- **WAL Archive ที่ไม่ทำงานทำให้ PITR ไม่ได้**  
- **Retention สั้นเกินไปทำให้ย้อนหลังไม่ได้**  
- **Backup บนเครื่องเดียวกับ Database เสี่ยงหายทั้งคู่**

## 7. ข้อดี
- วางแผนได้  
- ลดความเสี่ยง  
- Audit ผ่าน  
- ทำให้ Incident Response มีแผน

## 8. ข้อเสีย
- ต้องลงทุน Storage  
- ต้องมีคนดูแล  
- ต้องทดสอบเป็นระยะ

## 9. ข้อห้าม
- ห้ามใช้ `pg_dump` เป็น Backup เดียว  
- ห้ามเก็บ Backup ไว้เครื่องเดียวกับ Database  
- ห้าม Backup โดยไม่ Encrypt  
- ห้ามลบ Backup ก่อน Restore Test  
- ห้ามใช้ RPO = 0 โดยไม่มี Sync Replication

## 10. รายละเอียด

### 10.1 ความหมาย RPO/RTO

```text
Incident ──────► Last Backup ──────► Recovery Point ──────► System Up
                    │                     │                     │
                    │◄──── RPO ──────────►│                     │
                    │                                           │
                    │◄──────────────── RTO ────────────────────►│
```

### 10.2 ตาราง RPO/RTO ตามธุรกิจ

| ประเภทระบบ | RPO | RTO | Backup Strategy |
|---|---|---|---|
| ระบบชำระเงิน | ≤ 5 นาที | ≤ 30 นาที | Physical + WAL + Sync Replica |
| ระบบรับหน่วยไฟ | ≤ 5 นาที | ≤ 30 นาที | Physical + WAL |
| ระบบรายงาน | ≤ 1 ชั่วโมง | ≤ 4 ชั่วโมง | Physical + WAL |
| ระบบภายใน | ≤ 24 ชั่วโมง | ≤ 1 วัน | Physical Daily |
| ระบบทดสอบ | ไม่กำหนด | ไม่กำหนด | pg_dump |

### 10.3 ประเภท Backup

| ประเภท | ตัวอย่าง | ข้อดี | ข้อเสีย |
|---|---|---|---|
| Logical | pg_dump, pg_dumpall | Portable, Restore บางส่วน | ช้า, ไม่มี PITR |
| Physical | pgBackRest Full | เร็ว, PITR | ต้องมี Version เดียวกัน |
| WAL Archive | pgBackRest archive-push | PITR | ต้องตั้งค่า |
| Snapshot | Cloud Snapshot | เร็ว | ไม่ Consistent |

### 10.4 Retention ที่แนะนำ

| ประเภท | Retention | เหตุผล |
|---|---|---|
| Full Backup | 2 ชุด | Restore ได้ |
| Diff/Incr Backup | 7 วัน | ลดเวลา Restore |
| WAL Archive | 7–30 วัน | PITR |
| pg_dump | 7 วัน | Backup เสริม |
| Globals | ทุกครั้งที่เปลี่ยน Role | Role Recovery |

### 10.5 Restore Test

- **รายเดือน** — Restore Full ล่าสุด  
- **รายไตรมาส** — Restore + PITR  
- **รายปี** — DR Drill เต็มรูปแบบ

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Strategy Table

```text
GridCare Production
├── pgBackRest Full Backup     รายวัน 02:00 → Retention 2 ชุด
├── pgBackRest Diff Backup     รายวัน 10:00, 18:00 → Retention 7 วัน
├── pgBackRest WAL Archive     Real-time → Retention 30 วัน
├── pg_dump -Fd -j 2           รายสัปดาห์ → Retention 4 สัปดาห์
├── pg_dumpall --globals-only  ทุกครั้งที่เปลี่ยน Role
└── Restore Test               ทุกวันที่ 1 ของเดือน
```

### ตัวอย่างที่ 2: ตรวจสอบ RPO/RTO ที่ทำได้จริง

**บน infra:**
```bash
# เปิดโหลด
cd /opt/gridcare/pgbench && PGHOST=127.0.0.1 PGPORT=6432 PGUSER=billing_app ./run_payday.sh 20 600
# เปิด Probe
~/probe.sh 180 | tee ~/probe.log
# Kill Primary
sudo systemctl kill -s SIGKILL patroni@17-main
```

ผลลัพธ์:
```text
kill=03:03:43.351 first_ok_after_fail=03:04:14.662
RTO = 31.3 วินาที
RPO (รายการที่ยืนยันแล้วแต่หาย) = 0
```

### ตัวอย่างที่ 3: ตรวจ Backup ที่มีอยู่

```bash
sudo -u postgres pgbackrest --stanza=gridcare info
```

ผลลัพธ์:
```text
stanza: gridcare
    status: ok
    cipher: aes-256-cbc

    db (current)
        wal archive min/max (17): 000000010000000000000001/000000010000000000000005

        full backup: 20261104-091700F
            database size: 1.25GB, backup size: 320MB
```

## 12. สรุปย่อ จำง่าย
- **RPO = ข้อมูลที่ยอมหาย, RTO = เวลาที่ต้องกลับมา**  
- **Physical + WAL = Production**  
- **Logical = Portable + Restore บางส่วน**  
- **Retention ที่เหมาะกับธุรกิจ**  
- **Restore Test ทุกเดือน**  
- **Backup บนเครื่องเดียว = เสี่ยง**

ประโยคจำ: **"Backup ที่ไม่เคย Restore Test คือ Backup ที่ไม่มีอยู่จริง"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — Backup and Restore: https://www.postgresql.org/docs/17/backup.html
- pgBackRest Documentation: https://pgbackrest.org/
- Google SRE Book — Data Integrity: https://sre.google/sre-book/data-integrity/
- GridCare Workshop Day 3: Lab 2.1, Lab 3.2

---

# บทที่ 62 pgBackRest

## 1. เรื่อง
`pgBackRest` เครื่องมือ Backup/Restore สำหรับ PostgreSQL Production

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้ติดตั้งและตั้งค่า `pgBackRest`  
2. เพื่อให้ใช้ Stanza  
3. เพื่อให้ใช้ Full/Diff/Incr Backup  
4. เพื่อให้ใช้ Parallel และ Encryption

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- เขียน `pgbackrest.conf` ที่ใช้งานได้จริง  
- สร้าง Stanza  
- รัน Full/Diff/Incr Backup  
- ใช้ Verify  
- ใช้ Encryption

## 4. เนื้อหาโดยย่อ
`pgBackRest` เป็นเครื่องมือ Backup ที่:
- รองรับ Full/Diff/Incr  
- รองรับ Parallel Backup  
- รองรับ Encryption  
- รองรับ S3/MinIO  
- รองรับ PITR  
- ใช้ Stanza แยก Cluster

## 5. ประโยชน์ที่ได้รับ
- Backup เร็ว  
- Restore ได้  
- รองรับ PITR  
- Encryption ใน Backup  
- รองรับ S3

## 6. ข้อควรระวัง
- **`repo1-cipher-pass` หาย = Backup ทั้งหมดเปิดไม่ได้**  
- **`stanza-create` ต้องทำก่อน `archive_mode = on`**  
- **ต้องมี Disk เพียงพอ**  
- **ต้องตั้ง `archive_command`**  
- **ต้องตรวจ `check` เป็นระยะ**

## 7. ข้อดี
- มาตรฐาน  
- รองรับ S3  
- Encryption  
- Parallel Backup  
- PITR

## 8. ข้อเสีย
- Config ซับซ้อน  
- ต้องมี Stanza  
- ต้องตั้ง `archive_command`

## 9. ข้อห้าม
- ห้ามลบ `repo1-cipher-pass`  
- ห้าม `stanza-create` หลัง `archive_mode = on`  
- ห้าม Backup โดยไม่ตรวจ `check`  
- ห้าม Restore โดยไม่ Verify  
- ห้าม Backup บนเครื่องเดียวกับ Database

## 10. รายละเอียด

### 10.1 ติดตั้ง

```bash
sudo apt install -y pgbackrest
```

### 10.2 เตรียมโฟลเดอร์

```bash
sudo install -d -o postgres -g postgres -m 750 \
  /etc/pgbackrest /var/spool/pgbackrest /var/log/pgbackrest
```

### 10.3 `pgbackrest.conf`

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

### 10.4 สร้าง Stanza

```bash
sudo -u postgres pgbackrest --stanza=gridcare stanza-create
```

ผลลัพธ์:
```text
2026-11-04 09:15:23.456 P00   INFO: stanza-create for stanza 'gridcare' on repo1
2026-11-04 09:15:23.789 P00   INFO: stanza-create command end: completed successfully (334ms)
```

### 10.5 ตั้ง `archive_mode`

**`/etc/postgresql/17/main/conf.d/40-gridcare-archive.conf`:**
```ini
archive_mode = on
archive_command = 'pgbackrest --stanza=gridcare archive-push %p'
archive_timeout = 60s
wal_level = replica
max_wal_senders = 10
```

```bash
sudo systemctl restart postgresql@17-main
```

### 10.6 Full Backup

```bash
sudo -u postgres pgbackrest --stanza=gridcare --type=full backup
```

ผลลัพธ์:
```text
2026-11-04 09:17:00.123 P00   INFO: backup command begin 2.59.3: --stanza=gridcare --type=full
2026-11-04 09:18:30.789 P00   INFO: backup command end: completed successfully (90666ms)
```

### 10.7 Diff Backup

```bash
sudo -u postgres pgbackrest --stanza=gridcare --type=diff backup
```

ผลลัพธ์:
```text
2026-11-04 10:00:15.789 P00   INFO: diff backup size = 45MB
2026-11-04 10:00:15.789 P00   INFO: backup command end: completed successfully (15666ms)
```

### 10.8 Incr Backup

```bash
sudo -u postgres pgbackrest --stanza=gridcare --type=incr backup
```

ผลลัพธ์:
```text
2026-11-04 10:01:08.789 P00   INFO: incr backup size = 12MB
2026-11-04 10:01:08.789 P00   INFO: backup command end: completed successfully (8666ms)
```

### 10.9 Verify

```bash
sudo -u postgres pgbackrest --stanza=gridcare verify
```

ผลลัพธ์:
```text
2026-11-04 10:10:30.789 P00   INFO: verify command end: completed successfully (330666ms)
```

### 10.10 ตารางคำสั่งที่ใช้บ่อย

| คำสั่ง | ใช้ |
|---|---|
| `stanza-create` | สร้าง Stanza |
| `check` | ตรวจ WAL Archive |
| `--type=full backup` | Full Backup |
| `--type=diff backup` | Diff Backup |
| `--type=incr backup` | Incr Backup |
| `info` | ดูข้อมูล Backup |
| `verify` | ตรวจ checksum |
| `restore` | Restore |
| `stanza-upgrade` | Upgrade Stanza |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Full Backup ครั้งแรก

```bash
sudo -u postgres pgbackrest --stanza=gridcare check
sudo -u postgres pgbackrest --stanza=gridcare --type=full backup
sudo -u postgres pgbackrest --stanza=gridcare info
```

ผลลัพธ์:
```text
stanza: gridcare
    status: ok

    db (current)
        full backup: 20261104-091700F
            database size: 1.25GB, backup size: 320MB
```

### ตัวอย่างที่ 2: Diff Backup

```bash
# สร้างการเปลี่ยนแปลงเล็กน้อย
sudo -u postgres psql -X -d gridcare -c "UPDATE gridcare.customers SET status = status WHERE customer_id <= 1000"

time sudo -u postgres pgbackrest --stanza=gridcare --type=diff backup
```

ผลลัพธ์:
```text
real    0m15.789s
```

### ตัวอย่างที่ 3: ตรวจ `pg_stat_archiver`

```sql
SELECT archived_count, last_archived_wal, last_archived_time, failed_count
FROM pg_stat_archiver;
```

ผลลัพธ์:
```text
 archived_count |       last_archived_wal        |    last_archived_time     | failed_count 
----------------+-------------------------------+---------------------------+--------------
             15 | 000000010000000000000005      | 2026-11-04 09:20:12.345+07|            0
```

## 12. สรุปย่อ จำง่าย
- **`pgbackrest.conf` + Stanza + `archive_mode`**  
- **`--type=full/diff/incr backup`**  
- **`check` และ `verify` เป็นระยะ**  
- **Encryption ด้วย `repo1-cipher-pass`**  
- **`stanza-create` ก่อน `archive_mode = on`**  
- **`stanza-upgrade` หลัง Upgrade**

ประโยคจำ: **"pgBackRest ที่ดีคือ pgBackRest ที่ Restore ได้ ตรวจสอบได้ และ Encrypt"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- pgBackRest Documentation: https://pgbackrest.org/
- pgBackRest — Command Reference: https://pgbackrest.org/command.html
- GridCare Workshop Day 3: Lab 3.2, Lab 3.3

---

# บทที่ 63 WAL Archiving

## 1. เรื่อง
WAL Archiving สำหรับ PostgreSQL เพื่อรองรับ PITR และ Backup ที่สอดคล้องกัน

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจ WAL และ WAL Archiving  
2. เพื่อให้ตั้ง `archive_mode`, `archive_command`  
3. เพื่อให้ตรวจสอบ `pg_stat_archiver`  
4. เพื่อให้แก้ไข WAL Archive ที่ล้ม

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ตั้ง `archive_mode = on`  
- ตั้ง `archive_command` ด้วย pgBackRest  
- ตรวจ `pg_stat_archiver`  
- แก้ไข `failed_count > 0`

## 4. เนื้อหาโดยย่อ
**WAL (Write-Ahead Log)** = บันทึกการเปลี่ยนแปลงก่อนเขียน Data Page  
**WAL Archiving** = การเก็บ WAL ไว้ใช้ PITR  
- `archive_mode = on`  
- `archive_command = 'pgbackrest --stanza=gridcare archive-push %p'`  
- `archive_timeout = 60s`

## 5. ประโยชน์ที่ได้รับ
- PITR ได้  
- Backup สอดคล้อง  
- Replication ได้  
- Recovery ได้

## 6. ข้อควรระวัง
- **`archive_mode` ต้อง Restart**  
- **`archive_command` ต้องคืนค่า 0**  
- **`archive_timeout` สั้นเกินไปทำให้ WAL เยอะ**  
- **`failed_count > 0` ต้องแก้ทันที**  
- **WAL Archive ค้างทำให้ Disk เต็ม**

## 7. ข้อดี
- PITR  
- Backup สอดคล้อง  
- Replication

## 8. ข้อเสีย
- ต้องตั้งค่า  
- ต้องมี Storage  
- ต้องตรวจ `failed_count`

## 9. ข้อห้าม
- ห้าม `archive_mode = off` บน Production  
- ห้ามลบ WAL ที่ยังไม่ Archive  
- ห้าม `archive_command` ที่ไม่ตรวจ Status  
- ห้าม `archive_timeout` สั้นเกินไป  
- ห้าม `wal_level = minimal` ถ้าต้องการ PITR

## 10. รายละเอียด

### 10.1 ตั้ง `archive_mode`

```ini
archive_mode = on
archive_command = 'pgbackrest --stanza=gridcare archive-push %p'
archive_timeout = 60s
wal_level = replica
max_wal_senders = 10
```

### 10.2 ตรวจสอบ

```sql
SELECT archived_count, last_archived_wal, last_archived_time, failed_count
FROM pg_stat_archiver;
```

ผลลัพธ์:
```text
 archived_count |       last_archived_wal        |    last_archived_time     | failed_count 
----------------+-------------------------------+---------------------------+--------------
             15 | 000000010000000000000005      | 2026-11-04 09:20:12.345+07|            0
```

### 10.3 ตรวจสอบ WAL Directory

```sql
SELECT pg_size_pretty(sum(size)) AS pg_wal_size FROM pg_ls_waldir();
```

ผลลัพธ์:
```text
 pg_wal_size 
-------------
 768 MB
```

### 10.4 ตรวจสอบ `pg_wal` ใน File System

```bash
sudo ls -la /var/lib/postgresql/17/main/pg_wal | head
```

ผลลัพธ์:
```text
total 32772
drwx------ 3 postgres postgres     4096 Nov  2 11:15 .
drwx------ 21 postgres postgres     4096 Nov  2 11:02 ..
-rw------- 1 postgres postgres 16777216 Nov  2 11:15 000000010000000000000017
-rw------- 1 postgres postgres 16777216 Nov  2 11:15 000000010000000000000018
drwx------ 2 postgres postgres     4096 Nov  2 11:15 archive_status
```

> 💡 ไฟล์ใน `pg_wal` มีขนาด 16 MB ต่อไฟล์

### 10.5 ตรวจสอบ `archive_status`

```bash
sudo ls /var/lib/postgresql/17/main/pg_wal/archive_status | head
```

### 10.6 ตรวจสอบ Log

```bash
sudo tail -n 5 /var/log/postgresql/postgresql-17-main.log | grep -i archive
```

ผลลัพธ์:
```text
2026-11-04 09:20:12.345 +07 [1234] LOG:  archived write-ahead log file "000000010000000000000005"
```

### 10.7 แก้ไข `failed_count > 0`

```sql
-- 1) ตรวจว่า `archive_command` ทำงานได้
-- 2) ตรวจ Disk และ Network
-- 3) ตรวจ MinIO/S3
-- 4) รัน `pgbackrest check`
-- 5) Restart PostgreSQL ถ้าจำเป็น
sudo -u postgres pgbackrest --stanza=gridcare check
```

ผลลัพธ์:
```text
2026-11-04 09:16:14.567 P00   INFO: check command end: completed successfully (2222ms)
```

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: ตั้งค่า WAL Archiving

**`/etc/postgresql/17/main/conf.d/40-gridcare-archive.conf`:**
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

### ตัวอย่างที่ 2: ตรวจสอบว่า Archive ทำงาน

```sql
SELECT archived_count, failed_count, last_archived_time
FROM pg_stat_archiver;
```

ผลลัพธ์:
```text
 archived_count | failed_count |    last_archived_time     
----------------+--------------+---------------------------
             45 |            0 | 2026-11-05 15:22:00.789+07
```

### ตัวอย่างที่ 3: ตรวจสอบ WAL ที่ยังไม่ Archive

```bash
sudo ls /var/lib/postgresql/17/main/pg_wal/archive_status/*.ready 2>/dev/null | wc -l
```

ผลลัพธ์:
```text
0
```

> ✅ ถ้ามี `.ready` แสดงว่ามี WAL ที่ยังไม่ Archive

### ตัวอย่างที่ 4: ตรวจสอบการ Archive ที่ล้ม

```bash
sudo grep -i "archive-push" /var/log/postgresql/postgresql-17-main.log | tail -5
```

ผลลัพธ์:
```text
2026-11-04 09:20:12.345 +07 [1234] LOG:  archived write-ahead log file "000000010000000000000005"
```

### ตัวอย่างที่ 5: หลัง PITR ต้อง Full Backup ใหม่

```bash
sudo -u postgres pgbackrest --stanza=gridcare --type=full backup
sudo -u postgres pgbackrest --stanza=gridcare check
```

## 12. สรุปย่อ จำง่าย
- **`archive_mode = on` + `archive_command` + `archive_timeout`**  
- **`pg_stat_archiver` ตรวจ `failed_count`**  
- **WAL 16 MB ต่อไฟล์**  
- **`.ready` = ยังไม่ Archive**  
- **หลัง PITR ต้อง Full Backup ใหม่**  
- **`pgbackrest check` เป็นประจำ**

ประโยคจำ: **"WAL Archive ที่ดีคือ WAL Archive ที่ `failed_count = 0`"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — WAL: https://www.postgresql.org/docs/17/wal.html
- PostgreSQL Documentation — Continuous Archiving: https://www.postgresql.org/docs/17/continuous-archiving.html
- pgBackRest — Archive Push: https://pgbackrest.org/command.html
- GridCare Workshop Day 3: Lab 3.2

---

# บทที่ 64 MinIO/S3 Repository

## 1. เรื่อง
การตั้งค่า MinIO หรือ S3 เป็น Backup Repository สำหรับ pgBackRest ด้วย TLS

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้ติดตั้งและตั้งค่า MinIO ด้วย TLS  
2. เพื่อให้สร้าง Bucket  
3. เพื่อให้ตั้ง pgBackRest ให้ใช้ S3  
4. เพื่อให้ตรวจสอบ Health

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ตั้ง MinIO ด้วย TLS  
- สร้าง Bucket ด้วย `curl`  
- ตั้ง pgBackRest ให้ใช้ S3  
- ตรวจ Health

## 4. เนื้อหาโดยย่อ
MinIO เป็น Object Storage ที่รองรับ S3 API  
ใช้เป็น Backup Repository สำหรับ pgBackRest ได้:
- รองรับ TLS  
- รองรับ Versioning  
- รองรับ Lifecycle  
- รองรับ Encryption

## 5. ประโยชน์ที่ได้รับ
- Backup แยกจาก Database  
- รองรับ S3-Compatible  
- TLS  
- Retention ผ่าน Bucket

## 6. ข้อควรระวัง
- **Certificate ต้องชื่อ `public.crt` และ `private.key`**  
- **MinIO User ต้องอ่าน Cert ได้**  
- **pgBackRest ต้องมี CA Cert**  
- **`repo1-storage-port` ต้องระบุ**  
- **`repo1-s3-uri-style = path`** สำหรับ MinIO

## 7. ข้อดี
- รองรับ S3  
- TLS  
- Retention  
- Backup แยกจาก Database

## 8. ข้อเสีย
- ต้องดูแล MinIO  
- ต้องตั้ง Certificate  
- ต้องตรวจ Health

## 9. ข้อห้าม
- ห้ามใช้ HTTP แทน HTTPS ใน Production  
- ห้ามใช้ Root Credential ใน pgBackRest  
- ห้ามลบ Bucket โดยไม่ Archive  
- ห้ามลบ Cert

## 10. รายละเอียด

### 10.1 ตรวจสอบ MinIO

```bash
systemctl cat minio | grep -E "User|EnvironmentFile|ExecStart"
sudo cat /etc/default/minio
cat /opt/pea/VERSIONS | grep -i minio
```

ผลลัพธ์:
```text
User=minio-user
EnvironmentFile=/etc/default/minio
ExecStart=/usr/local/bin/minio server $MINIO_OPTS $MINIO_VOLUMES

MINIO_VOLUMES="/var/lib/minio"
MINIO_OPTS="--address :9000 --console-address 127.0.0.1:9001"
MINIO_ROOT_USER=""
MINIO_ROOT_PASSWORD=""

MinIO: RELEASE.2025-04-22T22-12-26Z
```

### 10.2 สร้าง Certificate

```bash
INFRA_IP=$(getent hosts infra | awk '{print $1}')
sudo install -d -m 755 /etc/minio/certs
sudo openssl req -new -x509 -days 365 -nodes -newkey rsa:3072 \
  -subj "/CN=infra" -addext "subjectAltName=DNS:infra,IP:${INFRA_IP}" \
  -keyout /etc/minio/certs/private.key -out /etc/minio/certs/public.crt
```

ผลลัพธ์:
```text
Generating a RSA private key
...
writing new private key to '/etc/minio/certs/private.key'
```

### 10.3 ตั้ง User

```bash
MINIO_USER=$(systemctl show -p User --value minio)
sudo chown -R "${MINIO_USER}": /etc/minio/certs
sudo chmod 600 /etc/minio/certs/private.key
```

### 10.4 ตั้ง `/etc/default/minio`

```ini
MINIO_VOLUMES="/var/lib/minio"
MINIO_OPTS="--address :9000 --console-address 127.0.0.1:9001 --certs-dir /etc/minio/certs"
MINIO_ROOT_USER="gridcare-backup"
MINIO_ROOT_PASSWORD="Lab-Minio-Secret-2569"
```

```bash
sudo install -d -o "${MINIO_USER}" -g "${MINIO_USER}" -m 750 /var/lib/minio
sudo systemctl enable --now minio
```

### 10.5 ตรวจ Health

```bash
curl -s -o /dev/null -w "%{http_code}\n" --cacert /etc/minio/certs/public.crt https://infra:9000/minio/health/live
```

ผลลัพธ์:
```text
200
```

### 10.6 สร้าง Bucket

```bash
curl -s -o /dev/null -w "%{http_code}\n" --cacert /etc/minio/certs/public.crt \
  --aws-sigv4 "aws:amz:us-east-1:s3" --user "gridcare-backup:Lab-Minio-Secret-2569" \
  -X PUT https://infra:9000/pgbackrest
```

ผลลัพธ์:
```text
200
```

> 💡 ถ้าสั่งซ้ำจะได้ `409` (Bucket มีอยู่แล้ว)

### 10.7 คัดลอก CA ไป pg1

```bash
# Notebook
scp lab-infra:/etc/minio/certs/public.crt minio-ca.crt
scp minio-ca.crt lab-pg1:/tmp/minio-ca.crt
```

```bash
# บน pg1
sudo install -o postgres -g postgres -m 644 /tmp/minio-ca.crt /etc/pgbackrest/minio-ca.crt
```

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: ตรวจ Health

```bash
curl -s -o /dev/null -w "%{http_code}\n" --cacert /etc/minio/certs/public.crt https://infra:9000/minio/health/live
```

ผลลัพธ์:
```text
200
```

### ตัวอย่างที่ 2: สร้าง Bucket

```bash
curl -s -o /dev/null -w "%{http_code}\n" --cacert /etc/minio/certs/public.crt \
  --aws-sigv4 "aws:amz:us-east-1:s3" --user "gridcare-backup:Lab-Minio-Secret-2569" \
  -X PUT https://infra:9000/pgbackrest
```

ผลลัพธ์:
```text
200
```

### ตัวอย่างที่ 3: ตรวจ pgBackRest ต่อ S3

```bash
sudo -u postgres pgbackrest --stanza=gridcare check
```

ผลลัพธ์:
```text
2026-11-04 09:16:14.567 P00   INFO: check repo1 (standby) succeeded
2026-11-04 09:16:14.789 P00   INFO: check command end: completed successfully (2222ms)
```

### ตัวอย่างที่ 4: `pgbackrest.conf` ที่ใช้ S3

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
```

## 12. สรุปย่อ จำง่าย
- **MinIO = Object Storage ที่รองรับ S3**  
- **TLS Cert ต้องชื่อ `public.crt` และ `private.key`**  
- **pgBackRest ต่อ S3 ด้วย `repo1-s3-*`**  
- **`repo1-s3-uri-style = path`** สำหรับ MinIO  
- **Health Check ต้อง 200**  
- **pgBackRest `check` ต้องผ่าน**

ประโยคจำ: **"MinIO ที่ดีคือ MinIO ที่มี TLS และ Health 200"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- MinIO Documentation: https://min.io/docs/
- pgBackRest — S3 Support: https://pgbackrest.org/user-guide.html#repo/repo-s3
- GridCare Workshop Day 3: Lab 3.1

---

# บทที่ 65 Full, Differential และ Incremental Backup

## 1. เรื่อง
การใช้งาน Full, Differential และ Incremental Backup ใน pgBackRest เพื่อให้ Backup Strategy มีประสิทธิภาพ

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจความแตกต่างของ Full/Diff/Incr  
2. เพื่อให้เลือกใช้ให้เหมาะ  
3. เพื่อให้ตรวจสอบผลใน `info`  
4. เพื่อให้วางแผน Retention

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- รัน Full/Diff/Incr Backup  
- อ่าน `pgbackrest info`  
- วางแผน Retention  
- เปรียบเทียบเวลาและขนาด

## 4. เนื้อหาโดยย่อ
**Full** = สำรองทั้งหมด  
**Differential** = สำรองเฉพาะที่เปลี่ยนจาก Full ล่าสุด  
**Incremental** = สำรองเฉพาะที่เปลี่ยนจาก Backup ล่าสุด (Diff หรือ Incr)

## 5. ประโยชน์ที่ได้รับ
- Backup เร็วขึ้น  
- Storage ประหยัด  
- Restore เร็วขึ้น  
- วางแผน Retention ได้

## 6. ข้อควรระวัง
- **Diff/Incr ต้องมี Full เป็น Base**  
- **Restore ต้องมี Chain ครบ**  
- **Retention ต้องเก็บ Full ที่ Diff/Incr อ้างอิง**  
- **Verify ต้องตรวจทุก Chain**  
- **Incr ที่มากเกินไปทำให้ Restore ช้า**

## 7. ข้อดี
- Backup เร็ว  
- Storage ประหยัด  
- Restore เร็ว

## 8. ข้อเสีย
- Chain ซับซ้อน  
- Restore ต้องมี Chain ครบ  
- Verify ใช้เวลานาน

## 9. ข้อห้าม
- ห้ามลบ Full ที่ Diff/Incr อ้างอิง  
- ห้าม Restore จาก Diff/Incr โดยไม่มี Full  
- ห้าม Diff/Incr ที่ไม่มี Full Base  
- ห้าม Retention ที่ตัด Full ที่ยังมี Diff/Incr อ้างอิง

## 10. รายละเอียด

### 10.1 เปรียบเทียบ

| ประเภท | สำรอง | เวลา | ขนาด |
|---|---|---|---|
| Full | ทั้งหมด | นาน | ใหญ่ |
| Diff | เปลี่ยนจาก Full ล่าสุด | ปานกลาง | ปานกลาง |
| Incr | เปลี่ยนจาก Backup ล่าสุด | เร็ว | เล็ก |

### 10.2 Full Backup

```bash
time sudo -u postgres pgbackrest --stanza=gridcare --type=full backup
```

ผลลัพธ์:
```text
2026-11-04 09:18:30.789 P00   INFO: full backup size = 1.25GB
real    1m30.666s
```

### 10.3 Diff Backup

```bash
time sudo -u postgres pgbackrest --stanza=gridcare --type=diff backup
```

ผลลัพธ์:
```text
2026-11-04 10:00:15.789 P00   INFO: diff backup size = 45MB
real    0m15.789s
```

### 10.4 Incr Backup

```bash
time sudo -u postgres pgbackrest --stanza=gridcare --type=incr backup
```

ผลลัพธ์:
```text
2026-11-04 10:01:08.789 P00   INFO: incr backup size = 12MB
real    0m8.789s
```

### 10.5 `pgbackrest info`

```bash
sudo -u postgres pgbackrest --stanza=gridcare info
```

ผลลัพธ์:
```text
stanza: gridcare
    status: ok
    cipher: aes-256-cbc

    db (current)
        wal archive min/max (17): 000000010000000000000001/000000010000000000000008

        full backup: 20261104-091700F
            timestamp start/stop: 2026-11-04 09:17:00+07 / 2026-11-04 09:18:30+07
            database size: 1.25GB, backup size: 320MB
            repo1: backup set size: 320MB

        diff backup: 20261104-100000D
            backup reference list: 20261104-091700F
            database size: 1.25GB, backup size: 45MB

        incr backup: 20261104-100100I
            backup reference list: 20261104-091700F, 20261104-100000D
            database size: 1.25GB, backup size: 12MB
```

### 10.6 Strategy ที่แนะนำ

```text
สัปดาห์ที่ 1
├── อาทิตย์ 02:00 Full Backup
├── จันทร์–เสาร์ 10:00 Diff Backup
├── ทุกวัน 18:00 Incr Backup
└── WAL Archive Real-time

Retention
├── Full: 2 ชุด
├── Diff: 7 วัน
├── Incr: 7 วัน
└── WAL: 30 วัน
```

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Full Backup ครั้งแรก

```bash
sudo -u postgres pgbackrest --stanza=gridcare --type=full backup
```

### ตัวอย่างที่ 2: Diff Backup

```bash
sudo -u postgres psql -X -d gridcare -c "UPDATE gridcare.customers SET status = status WHERE customer_id <= 1000"
time sudo -u postgres pgbackrest --stanza=gridcare --type=diff backup
```

### ตัวอย่างที่ 3: Incr Backup

```bash
time sudo -u postgres pgbackrest --stanza=gridcare --type=incr backup
```

### ตัวอย่างที่ 4: `info` ที่มี Chain

```bash
sudo -u postgres pgbackrest --stanza=gridcare info | grep -E "full backup|diff backup|incr backup|backup reference"
```

ผลลัพธ์:
```text
        full backup: 20261104-091700F
        diff backup: 20261104-100000D
            backup reference list: 20261104-091700F
        incr backup: 20261104-100100I
            backup reference list: 20261104-091700F, 20261104-100000D
```

## 12. สรุปย่อ จำง่าย
- **Full = ทั้งหมด**  
- **Diff = เปลี่ยนจาก Full ล่าสุด**  
- **Incr = เปลี่ยนจาก Backup ล่าสุด**  
- **Restore ต้องมี Chain ครบ**  
- **Retention ต้องเก็บ Full ที่อ้างอิง**  
- **Verify ตรวจทุก Chain**

ประโยคจำ: **"Full ให้ Base, Diff ให้ความเร็ว, Incr ให้ประหยัด"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- pgBackRest — Backup Types: https://pgbackrest.org/user-guide.html
- GridCare Workshop Day 3: Lab 3.3

---

# บทที่ 66 Restore Test

## 1. เรื่อง
การทำ Restore Test เพื่อยืนยันว่า Backup ใช้งานได้จริง และวัด RTO

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้ Restore Test ได้  
2. เพื่อให้วัด RTO  
3. เพื่อให้ตรวจสอบผลหลัง Restore  
4. เพื่อให้สร้าง Report

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- รัน `restore_test.sh`  
- ตรวจ Row Count  
- ตรวจ Index และ Constraint  
- สร้าง Report

## 4. เนื้อหาโดยย่อ
Restore Test ประกอบด้วย:
1. Restore ไปที่ Path ใหม่  
2. Start Cluster บน Port ใหม่  
3. ตรวจสอบ Data  
4. หยุด Cluster  
5. ล้างข้อมูล  
6. สร้าง Report

## 5. ประโยชน์ที่ได้รับ
- มั่นใจว่า Backup ใช้ได้  
- วัด RTO จริง  
- ผ่าน Audit  
- ลดความเสี่ยงเมื่อเกิด Incident

## 6. ข้อควรระวัง
- **ต้องมี Disk เพียงพอ**  
- **ต้องใช้ Port ที่ว่าง**  
- **ต้องมี Role ครบ**  
- **ต้องตรวจ `pg_checksums`**  
- **ต้องล้าง Cluster ทดสอบ**

## 7. ข้อดี
- มั่นใจใน Backup  
- วัด RTO ได้  
- มี Evidence

## 8. ข้อเสีย
- ใช้เวลา  
- ใช้ Disk  
- ต้องมี Test Environment

## 9. ข้อห้าม
- ห้าม Restore ทับ Production  
- ห้ามใช้ Port เดียวกับ Production  
- ห้ามลบ Backup ก่อน Restore Test  
- ห้าม Restore โดยไม่ตรวจผล

## 10. รายละเอียด

### 10.1 ตรวจ Disk

```bash
df -h /var/tmp
```

ผลลัพธ์:
```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        78G   18G   57G  24% /
```

### 10.2 รัน `restore_test.sh`

```bash
sudo -u postgres MODE=pgbackrest STANZA=gridcare ./restore_test.sh; echo "exit=$?"
```

ผลลัพธ์:
```text
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

### 10.3 ตรวจสอบระหว่าง Restore

```sql
SELECT pg_is_in_recovery();
```

ผลลัพธ์ (ระหว่าง Restore):
```text
 pg_is_in_recovery 
-------------------
 t
```

### 10.4 ทดสอบว่า Restore ล้มเหลว

**สาธิตการแก้ไฟล์ใน Repository:**
```text
pgbackrest verify  →  INFO: invalid checksum '20261026-025448F/bundle/2'
restore_test.sh    →  ERROR: [095]: ... cipher header missing
                      FAIL ที่ขั้น: pgbackrest restore         exit=1
```

### 10.5 Restore Test Report

```text
Restore Test Report
Date       : 2026-11-04
Backup     : 2026-11-04 09:17 (Full)
Target     : /var/tmp/gc-restore-test
Duration   : 7s
RTO        : 7s

Checks:
  - bills          : 1200000 OK
  - customers      : 200000  OK
  - meter_readings : 7200000 OK
  - Index validity : 45/45 OK
  - Constraints    : 23/23 OK
  - Checksums      : 0 bad

Exit Code  : 0
Conclusion : PASS
```

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Restore Test ที่ผ่าน

```bash
sudo -u postgres MODE=pgbackrest STANZA=gridcare ./restore_test.sh; echo "exit=$?"
```

ผลลัพธ์:
```text
PASS restore test (pgbackrest) ใช้เวลา 7 วินาที
exit=0
```

### ตัวอย่างที่ 2: Restore Test ที่ล้ม

```text
ERROR: [095]: ... cipher header missing
FAIL ที่ขั้น: pgbackrest restore         exit=1
```

### ตัวอย่างที่ 3: Restore ด้วย `pg_basebackup`

```bash
sudo -u postgres pg_basebackup -D /var/tmp/gc-restore-test -h pg1 -U replicator -X stream
```

### ตัวอย่างที่ 4: ตรวจสอบ Checksums

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

### ตัวอย่างที่ 5: systemd timer

```bash
systemctl list-timers 'gridcare-*' --no-pager
```

ผลลัพธ์:
```text
NEXT                        LEFT       LAST                        PASSED    UNIT                          ACTIVATES
Sun 2026-12-06 02:00:00 +07 4 weeks left n/a                        n/a       gridcare-restore-test.timer  gridcare-restore-test.service
```

## 12. สรุปย่อ จำง่าย
- **Restore Test = Restore + ตรวจสอบ + Report**  
- **ทุกเดือนเป็นอย่างน้อย**  
- **ต้องมี Disk เพียงพอ**  
- **ต้องตรวจ Checksums**  
- **Report ต้องมี Exit Code**  
- **Backup ที่ไม่เคย Restore = ไม่มี Backup**

ประโยคจำ: **"Restore Test ที่ดีคือ Restore Test ที่มี Report และ Exit Code"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- pgBackRest — Restore: https://pgbackrest.org/command.html#command-restore
- GridCare Workshop Day 3: Lab 4.1

---

# บทที่ 67 Point-in-Time Recovery (PITR)

## 1. เรื่อง
PITR สำหรับ PostgreSQL เพื่อกู้คืนข้อมูลไปยังเวลาที่กำหนด

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจ PITR  
2. เพื่อให้ระบุ `TARGET` จาก Log  
3. เพื่อให้รัน PITR  
4. เพื่อให้ตรวจสอบผล

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- อ่าน Log หาเวลาเป้าหมาย  
- รัน `pgbackrest restore --type=time --target=...`  
- ตรวจสอบ `pg_is_in_recovery`  
- ตรวจสอบ `timeline_id`  
- ยืนยันข้อมูล

## 4. เนื้อหาโดยย่อ
PITR ประกอบด้วย:
1. หยุดแอป (หยุดการเขียน)  
2. หา Time Target จาก Log  
3. Restore ด้วย pgBackRest  
4. Start และรอ Promote  
5. ตรวจสอบข้อมูล  
6. Full Backup ใหม่  
7. เปิดแอป

## 5. ประโยชน์ที่ได้รับ
- กู้คืนข้อมูลได้  
- ลด RPO/RTO  
- ผ่าน Audit  
- ทำให้ Incident Response มี Plan

## 6. ข้อควรระวัง
- **ต้องหยุด PostgreSQL ก่อน Restore**  
- **ต้องมี WAL Archive ครบ**  
- **ต้องระบุ Time Target ถูก**  
- **หลัง PITR ต้อง Full Backup ใหม่**  
- **Timeline จะเปลี่ยน**

## 7. ข้อดี
- กู้คืนได้  
- ระบุเวลาได้  
- ผ่าน Audit

## 8. ข้อเสีย
- ต้องมี Downtime  
- ต้องมี WAL Archive  
- ซับซ้อน

## 9. ข้อห้าม
- ห้าม PITR บน Production โดยไม่มี Plan  
- ห้าม PITR โดยไม่หยุดการเขียน  
- ห้าม PITR โดยไม่มี Backup  
- ห้าม PITR โดยไม่มีผู้อนุมัติ  
- ห้าม PITR โดยไม่ตรวจสอบผล

## 10. รายละเอียด

### 10.1 ขั้นที่ 1: ยืนยันข้อมูลเสีย

```bash
date +%T
sudo -u postgres psql -X -d gridcare <<'EOF'
SELECT tariff_code, rate_per_kwh, updated_at FROM gridcare.tariff_rates ORDER BY tariff_code;
EOF
```

ผลลัพธ์ (หลัง Batch ผิด):
```text
 tariff_code | rate_per_kwh |         updated_at         
-------------+--------------+----------------------------
 GOV         |       420.00 | 2026-11-04 14:51:15+07
 RES         |       390.00 | 2026-11-04 14:51:15+07
 SMB         |       450.00 | 2026-11-04 14:51:15+07
```

### 10.2 ขั้นที่ 2: หา Time Target จาก Log

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

### 10.3 ขั้นที่ 3: หยุดการเขียน

```bash
# บน infra: หยุด pgbench
tmux attach -t load
# Ctrl+c

# บน pg1: หยุด PostgreSQL
sudo systemctl stop postgresql@17-main
pg_lsclusters
```

ผลลัพธ์:
```text
Ver Cluster Port Status Owner    Data directory
17  main    5432 down   postgres /var/lib/postgresql/17/main
```

### 10.4 ขั้นที่ 4: Restore PITR

```bash
date +%T
sudo -u postgres pgbackrest --stanza=gridcare --delta --type=time \
  --target="$TARGET" --target-action=promote restore
date +%T
```

ผลลัพธ์:
```text
14:53:00
2026-11-04 14:53:31.012 P00   INFO: restore command end: completed successfully (31889ms)
14:53:31
```

### 10.5 ขั้นที่ 5: Start และรอ Promote

```bash
sudo systemctl start postgresql@17-main
sudo tail -n 8 /var/log/postgresql/postgresql-17-main.log
```

ผลลัพธ์:
```text
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
```

ผลลัพธ์:
```text
f
```

### 10.6 ขั้นที่ 6: ตรวจสอบข้อมูล

```bash
sudo -u postgres psql -X -d gridcare <<'EOF'
SELECT tariff_code, rate_per_kwh, updated_at FROM gridcare.tariff_rates ORDER BY tariff_code;
EOF
```

ผลลัพธ์:
```text
 tariff_code | rate_per_kwh |         updated_at         
-------------+--------------+----------------------------
 GOV         |         4.20 | 2026-11-04 08:00:00+07
 RES         |         3.90 | 2026-11-04 08:00:00+07
 SMB         |         4.50 | 2026-11-04 08:00:00+07
```

> ✅ ข้อมูลกลับมาปกติ

### 10.7 ขั้นที่ 7: Full Backup ใหม่

```bash
sudo -u postgres pgbackrest --stanza=gridcare --type=full backup
sudo -u postgres pgbackrest --stanza=gridcare check
```

### 10.8 ขั้นที่ 8: เปิดโหลดกลับ

```bash
tmux attach -t load
cd /opt/gridcare/pgbench
PGHOST=127.0.0.1 PGPORT=6432 PGUSER=billing_app ./run_normal.sh 8 25200
```

### 10.9 Timeline

```sql
SELECT timeline_id FROM pg_control_checkpoint();
```

ผลลัพธ์:
```text
 timeline_id 
-------------
           2
```

> ✅ Timeline เพิ่มจาก 1 → 2

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: RTO ของ PITR

| ขั้น | เวลา | ระยะเวลา |
|---|---|---|
| ตรวจพบ | 14:45:30 | - |
| ตัดสินใจ | 14:52:34 | 7 นาที 4 วินาที |
| Restore เริ่ม | 14:53:00 | 26 วินาที |
| Restore เสร็จ | 14:53:31 | 31 วินาที |
| Promote เสร็จ | 14:53:55 | 24 วินาที |
| ตรวจเสร็จ | 14:54:02 | 7 วินาที |
| **RTO รวม** | | **8 นาที 32 วินาที** |

### ตัวอย่างที่ 2: ตรวจสอบ Log

```bash
sudo grep -E "starting point-in-time recovery|recovery stopping|selected new timeline|archive recovery complete" /var/log/postgresql/postgresql-17-main.log | tail -4
```

ผลลัพธ์:
```text
LOG:  starting point-in-time recovery to 2026-11-04 14:51:12+07
LOG:  recovery stopping before commit of transaction 2494, time 2026-11-04 14:51:12.123456+07
LOG:  selected new timeline ID: 2
LOG:  archive recovery complete
```

### ตัวอย่างที่ 3: ตรวจสอบ Timeline

```sql
SELECT timeline_id FROM pg_control_checkpoint();
SELECT pg_is_in_recovery();
```

ผลลัพธ์:
```text
 timeline_id 
-------------
           2

 pg_is_in_recovery 
-------------------
 f
```

### ตัวอย่างที่ 4: `pgbackrest info`

```bash
sudo -u postgres pgbackrest --stanza=gridcare info | grep -E "full backup|wal archive"
```

ผลลัพธ์:
```text
        wal archive min/max (17): 000000010000000000000001/000000020000000000000012
        full backup: 20261104-145430F
        full backup: 20261104-091700F
```

## 12. สรุปย่อ จำง่าย
- **PITR = Restore + Target Time + WAL Archive**  
- **ต้องหยุด PostgreSQL ก่อน Restore**  
- **หา Time Target จาก Log**  
- **หลัง PITR ต้อง Full Backup ใหม่**  
- **Timeline เพิ่มขึ้น**  
- **RTO ของ PITR ขึ้นกับขนาดข้อมูล**

ประโยคจำ: **"PITR คือการย้อนเวลา แต่ต้องมี WAL Archive และ Plan"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — PITR: https://www.postgresql.org/docs/17/continuous-archiving.html
- pgBackRest — Restore Time: https://pgbackrest.org/command.html#command-restore
- GridCare Workshop Day 3: Workshop Day 3 ขั้นที่ 1

---

# บทที่ 68 Row-Level Security (RLS)

## 1. เรื่อง
Row-Level Security (RLS) ใน PostgreSQL สำหรับจำกัดการเข้าถึงข้อมูลในระดับแถว

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจ RLS  
2. เพื่อให้สร้าง Policy  
3. เพื่อให้ผูก RLS กับ Role  
4. เพื่อให้ทดสอบ RLS

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- เปิด RLS บนตาราง  
- สร้าง Policy สำหรับ Role  
- ใช้ `USING` และ `WITH CHECK`  
- ตรวจสอบผลด้วย `EXPLAIN`

## 4. เนื้อหาโดยย่อ
RLS ทำให้แต่ละ Role เห็นเฉพาะแถวที่อนุญาต  
- `ALTER TABLE ... ENABLE ROW LEVEL SECURITY`  
- `CREATE POLICY ... FOR SELECT TO role USING (condition)`  
- Policy สำหรับ `INSERT`/`UPDATE`/`DELETE`  
- Policy สำหรับ Admin (เห็นทุกแถว)

## 5. ประโยชน์ที่ได้รับ
- จำกัดการเข้าถึงข้อมูล  
- PDPA Compliance  
- ลดความเสี่ยงจาก Insider  
- ลดความเสี่ยงจากการโจมตี

## 6. ข้อควรระวัง
- **Role ที่ไม่มี Policy เห็น 0 แถว**  
- **View ที่ใช้ `security_invoker = true`** ถึงจะใช้ RLS  
- **Policy ที่มี Subquery ทำให้ช้า**  
- **Superuser ข้าม RLS**  
- **Owner ข้าม RLS** (ถ้าไม่ได้ `FORCE ROW LEVEL SECURITY`)

## 7. ข้อดี
- ปลอดภัย  
- Compliance  
- ไม่ต้องแก้แอป

## 8. ข้อเสีย
- Policy ที่ซับซ้อนทำให้ช้า  
- ต้องทดสอบทุก Role  
- ต้องดูแล Policy

## 9. ข้อห้าม
- ห้ามเปิด RLS โดยไม่มี Policy ที่ครอบคลุม  
- ห้ามใช้ Superuser กับแอป  
- ห้ามใช้ View ที่ไม่มี `security_invoker` กับ RLS  
- ห้าม Policy ที่มี Subquery ที่ช้า  
- ห้ามลืม Policy สำหรับ Admin

## 10. รายละเอียด

### 10.1 สร้างตาราง Mapping

```sql
CREATE TABLE gridcare.staff_regions (
    role_name text     PRIMARY KEY,
    region_id smallint NOT NULL REFERENCES gridcare.regions (region_id)
);
INSERT INTO gridcare.staff_regions (role_name, region_id) VALUES ('staff_n1', 1), ('staff_s3', 12);
GRANT SELECT ON gridcare.staff_regions TO gridcare_staff;
```

### 10.2 เปิด RLS และสร้าง Policy

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
```

### 10.3 ตรวจสอบผล

```sql
SET ROLE staff_n1;
SELECT 'staff_n1' AS who, count(*) FROM gridcare.customers;
RESET ROLE;

SET ROLE staff_s3;
SELECT 'staff_s3' AS who, count(*) FROM gridcare.customers;
RESET ROLE;

SET ROLE callcenter_ro;
SELECT 'callcenter_ro' AS who, count(*) FROM gridcare.customers;
RESET ROLE;
```

ผลลัพธ์:
```text
     who      | count  
--------------+--------
 staff_n1     |  16676
 staff_s3     |  16454
 callcenter_ro| 200000
```

### 10.4 ตรวจสอบ Plan

```sql
SET ROLE staff_n1;
EXPLAIN (ANALYZE, COSTS OFF, TIMING OFF) SELECT count(*) FROM gridcare.customers;
RESET ROLE;
```

ผลลัพธ์:
```text
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

### 10.5 View ที่ใช้ RLS

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

> ⚠️ ต้องใช้ `security_invoker = true` มิฉะนั้น View จะข้าม RLS

### 10.6 `FORCE ROW LEVEL SECURITY`

```sql
ALTER TABLE gridcare.customers FORCE ROW LEVEL SECURITY;
```

> 💡 ทำให้ Owner ก็ต้องผ่าน RLS

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: RLS ที่จำกัดตาม Region

```sql
ALTER TABLE gridcare.customers ENABLE ROW LEVEL SECURITY;

CREATE POLICY staff_own_region ON gridcare.customers
    FOR SELECT TO gridcare_staff
    USING (office_id IN (SELECT o.office_id
                         FROM gridcare.offices AS o
                         JOIN gridcare.staff_regions AS s ON s.region_id = o.region_id
                         WHERE s.role_name = current_user));
```

### ตัวอย่างที่ 2: Policy สำหรับ Admin

```sql
CREATE POLICY app_all_rows ON gridcare.customers
    FOR ALL TO billing_app, callcenter_ro, report_ro, dba
    USING (true) WITH CHECK (true);
```

### ตัวอย่างที่ 3: ตรวจสอบ Role ที่ไม่มี Policy

```sql
SET ROLE gridcare_staff;
SELECT count(*) FROM gridcare.customers;
```

ผลลัพธ์ (ถ้าไม่มี Policy):
```text
 count 
-------
     0
```

### ตัวอย่างที่ 4: ตรวจสอบ View

```sql
SET ROLE callcenter_ro;
SELECT customer_id, citizen_id_masked, phone_masked
FROM gridcare.customers_masked WHERE customer_id = 1;
RESET ROLE;
```

ผลลัพธ์:
```text
 customer_id | citizen_id_masked | phone_masked 
-------------+-------------------+--------------
           1 | 2-xxxx-xxxxx-xx-2 | 086-xxx-xx40
```

### ตัวอย่างที่ 5: ตรวจสอบ RLS ใน `pg_policies`

```sql
SELECT schemaname, tablename, policyname, roles, cmd, qual
FROM pg_policies WHERE schemaname = 'gridcare';
```

ผลลัพธ์:
```text
 schemaname | tablename |    policyname    |        roles        | cmd | qual
------------+-----------+------------------+---------------------+-----+-------
 gridcare   | customers | staff_own_region | {gridcare_staff}    | SELECT | ...
 gridcare   | customers | app_all_rows     | {billing_app,...}   | ALL | true
```

## 12. สรุปย่อ จำง่าย
- **RLS = Row-Level Security**  
- **Policy = USING + WITH CHECK**  
- **Role ที่ไม่มี Policy เห็น 0 แถว**  
- **View ต้องมี `security_invoker = true`**  
- **Superuser ข้าม RLS**  
- **`FORCE ROW LEVEL SECURITY` ทำให้ Owner ต้องผ่าน RLS**

ประโยคจำ: **"RLS ที่ดีคือ RLS ที่ทุก Role มี Policy ที่ชัดเจน"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — Row Security Policies: https://www.postgresql.org/docs/17/ddl-rowsecurity.html
- GridCare Workshop Day 3: Workshop Day 3 ขั้นที่ 2

---

# บทที่ 69 Masking และ pgcrypto

## 1. เรื่อง
การปิดบังข้อมูล (Masking) และการเข้ารหัสด้วย `pgcrypto` ใน PostgreSQL

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจ Masking vs Encryption  
2. เพื่อให้ใช้ `pgcrypto`  
3. เพื่อให้สร้าง View ที่ Mask  
4. เพื่อให้ทดสอบ

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ใช้ `left`, `right` ทำ Masking  
- ใช้ `pgp_sym_encrypt` และ `pgp_sym_decrypt`  
- สร้าง View ที่ Mask  
- เก็บ Key อย่างปลอดภัย

## 4. เนื้อหาโดยย่อ
**Masking** — ปิดบังบางส่วน เช่น `1234-xxxx-5678`  
**Encryption** — เข้ารหัสด้วย Key เช่น AES-256 ผ่าน `pgcrypto`

Masking เหมาะกับ: การแสดงผล, Report  
Encryption เหมาะกับ: การเก็บข้อมูลที่ละเอียดอ่อน

## 5. ประโยชน์ที่ได้รับ
- PDPA Compliance  
- ลด PII  
- ปลอดภัย  
- ใช้ใน Report ได้

## 6. ข้อควรระวัง
- **Masking ไม่ใช่ Encryption**  
- **Encryption ต้องมี Key**  
- **Key ต้องไม่เก็บใน Code**  
- **Key ต้องหมุนเวียน**  
- **Search ที่เข้ารหัสทำได้ยาก**

## 7. ข้อดี
- PDPA  
- ป้องกัน Insider  
- ใช้ใน Report ได้

## 8. ข้อเสีย
- ต้องมี Key Management  
- Search ที่เข้ารหัสทำได้ยาก  
- Encryption มี Overhead

## 9. ข้อห้าม
- ห้ามเก็บ Key ใน Code หรือ Git  
- ห้ามใช้ `md5` หรือ `sha256` เป็นการเข้ารหัส  
- ห้าม Masking แล้วเรียกว่า Encryption  
- ห้ามเข้ารหัสโดยไม่มี Backup Key  
- ห้ามใช้ `pgcrypto` ใน Query ที่ Index

## 10. รายละเอียด

### 10.1 Masking ด้วย `left`/`right`

```sql
SELECT customer_id,
       left(citizen_id, 1) || '-xxxx-xxxxx-xx-' || right(citizen_id, 1) AS citizen_id_masked,
       left(phone, 3) || '-xxx-xx' || right(phone, 2)                   AS phone_masked
FROM gridcare.customers
WHERE customer_id <= 5;
```

ผลลัพธ์:
```text
 customer_id | citizen_id_masked | phone_masked 
-------------+-------------------+--------------
           1 | 2-xxxx-xxxxx-xx-2 | 086-xxx-xx40
```

### 10.2 View ที่ Mask

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

### 10.3 `pgcrypto`

```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypt
SELECT pgp_sym_encrypt('1234567890121', 'Lab-Key-2569', 'cipher-algo=aes256');

-- Decrypt
SELECT pgp_sym_decrypt(encrypted_col, 'Lab-Key-2569');
```

### 10.4 เก็บเฉพาะ Encrypted

```sql
CREATE TABLE gridcare.customer_secret_demo AS
SELECT customer_id,
       pgp_sym_encrypt(citizen_id, 'Lab-Key-2569', 'cipher-algo=aes256') AS citizen_id_enc
FROM gridcare.customers
WHERE customer_id <= 5;
```

### 10.5 ตรวจสอบ

```sql
SELECT d.customer_id,
       left(encode(d.citizen_id_enc, 'hex'), 16) || '...'           AS stored_bytes,
       pgp_sym_decrypt(d.citizen_id_enc, 'Lab-Key-2569') = c.citizen_id AS decrypt_ok
FROM gridcare.customer_secret_demo AS d
JOIN gridcare.customers AS c USING (customer_id)
ORDER BY d.customer_id;
```

ผลลัพธ์:
```text
 customer_id |   stored_bytes    | decrypt_ok 
-------------+-------------------+------------
           1 | c30d04070302...   | t
           2 | c30d04070302...   | t
```

### 10.6 Wrong Key

```sql
SELECT pgp_sym_decrypt(citizen_id_enc, 'wrong-key') FROM gridcare.customer_secret_demo LIMIT 1;
```

ผลลัพธ์:
```text
ERROR:  Wrong key or corrupt data
```

### 10.7 ตรวจเลข 13 หลัก

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
       gridcare.is_valid_thai_id('1234567890123') AS bad;
```

ผลลัพธ์:
```text
 good | bad 
------+-----
 t    | f
```

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: View ที่ Mask

```sql
SET ROLE callcenter_ro;
SELECT customer_id, citizen_id_masked, phone_masked
FROM gridcare.customers_masked WHERE customer_id = 1;
RESET ROLE;
```

ผลลัพธ์:
```text
 customer_id | citizen_id_masked | phone_masked 
-------------+-------------------+--------------
           1 | 2-xxxx-xxxxx-xx-2 | 086-xxx-xx40
```

### ตัวอย่างที่ 2: pgcrypto Roundtrip

```sql
SELECT pgp_sym_decrypt(
  pgp_sym_encrypt('1234567890121', 'Lab-Key-2569', 'cipher-algo=aes256'),
  'Lab-Key-2569'
) AS roundtrip;
```

ผลลัพธ์:
```text
   roundtrip   
---------------
 1234567890121
```

### ตัวอย่างที่ 3: เพิ่ม CHECK Constraint

```sql
SET lock_timeout = '3s';
ALTER TABLE gridcare.customers
    ADD CONSTRAINT customers_citizen_id_check
    CHECK (gridcare.is_valid_thai_id(citizen_id)) NOT VALID;
ALTER TABLE gridcare.customers VALIDATE CONSTRAINT customers_citizen_id_check;
RESET lock_timeout;
```

### ตัวอย่างที่ 4: ตรวจสอบ Constraint

```sql
SELECT conname, convalidated FROM pg_constraint WHERE conname LIKE 'customers_citizen%';
SELECT count(*) FILTER (WHERE NOT gridcare.is_valid_thai_id(citizen_id)) AS invalid_rows
FROM gridcare.customers;
```

ผลลัพธ์:
```text
           conname           | convalidated 
-----------------------------+--------------
 customers_citizen_id_check  | t

 invalid_rows 
--------------
            0
```

### ตัวอย่างที่ 5: Audit Log

```bash
sudo grep "AUDIT: OBJECT" /var/log/postgresql/postgresql-17-main.log | tail -2 | cut -c1-200
```

ผลลัพธ์:
```text
2026-11-04 15:45:12.345 +07 [2345] callcenter_ro@gridcare app=psql client=[local] LOG:  AUDIT: OBJECT,1,1,READ,SELECT,TABLE,gridcare.customers,SELECT customer_id, ca_number, ... FROM gridcare.customers_masked WHERE customer_id = 1,<not logged>
```

## 12. สรุปย่อ จำง่าย
- **Masking = ปิดบัง, Encryption = เข้ารหัส**  
- **View ที่ Mask ต้องมี `security_invoker = true`**  
- **`pgp_sym_encrypt` / `pgp_sym_decrypt`**  
- **Key ต้องไม่อยู่ใน Git**  
- **ตรวจเลข 13 หลักด้วย `is_valid_thai_id`**  
- **CHECK NOT VALID + VALIDATE** ปลอดภัย

ประโยคจำ: **"Masking ทำให้อ่านได้ แต่ไม่เปิดเผย Encryption ทำให้อ่านได้เฉพาะคนที่มี Key"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — pgcrypto: https://www.postgresql.org/docs/17/pgcrypto.html
- PDPA Thailand: https://www.pdpc.or.th/
- GridCare Workshop Day 3: Workshop Day 3 ขั้นที่ 3

---

# บทที่ 70 pgAudit

## 1. เรื่อง
`pgAudit` Extension สำหรับ Audit การเข้าถึงข้อมูลและการเปลี่ยนแปลง Schema

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้ติดตั้งและตั้งค่า `pgAudit`  
2. เพื่อให้เลือก Audit Level ที่เหมาะ  
3. เพื่อให้ตรวจสอบ Log  
4. เพื่อให้ผูกกับ Compliance

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ติดตั้ง `pgAudit`  
- ตั้ง `pgaudit.log = 'ddl, role'`  
- ตั้ง `pgaudit.role`  
- ตรวจสอบ Log  
- ป้องกัน PII ใน Log

## 4. เนื้อหาโดยย่อ
`pgAudit` เป็น Extension ที่:
- Audit Session  
- Audit Object  
- Audit DDL, Role, Function  
- ใช้กับ Role ที่กำหนด

## 5. ประโยชน์ที่ได้รับ
- Compliance  
- Audit ครบ  
- ตรวจสอบ Insider  
- ลดความเสี่ยง

## 6. ข้อควรระวัง
- **`pgaudit.log_parameter = off`** ป้องกัน PII  
- **`pgaudit.log = 'all'` ทำให้ Log บวม**  
- **ต้องมี Role ที่กำหนด**  
- **ต้องตั้ง `shared_preload_libraries`**  
- **ต้อง Restart**

## 7. ข้อดี
- Compliance  
- Audit ครบ  
- ตรวจสอบได้

## 8. ข้อเสีย
- Log บวม  
- ต้องตั้ง Role  
- ต้อง Restart

## 9. ข้อห้าม
- ห้าม `pgaudit.log = 'all'` บน Production  
- ห้าม `pgaudit.log_parameter = on` ถ้ามี PII  
- ห้าม Audit ทุกอย่างโดยไม่จำเป็น  
- ห้ามลืม `shared_preload_libraries`

## 10. รายละเอียด

### 10.1 ติดตั้ง

```bash
sudo apt install -y postgresql-17-pgaudit
cd /etc/postgresql/17/main
sudo sed -i "/^shared_preload_libraries/ s/'\$/,pgaudit'/" conf.d/20-gridcare-logging.conf
grep shared_preload_libraries conf.d/*.conf
```

ผลลัพธ์:
```text
conf.d/20-gridcare-logging.conf:shared_preload_libraries = 'pg_stat_statements,auto_explain,pgaudit'
```

### 10.2 ตั้งค่า `pgaudit`

**`/etc/postgresql/17/main/conf.d/50-gridcare-audit.conf`:**
```ini
pgaudit.log = 'ddl, role'
pgaudit.log_catalog = off
pgaudit.log_relation = on
pgaudit.log_parameter = off
pgaudit.role = 'gridcare_auditor'
```

```bash
sudo chown postgres:postgres /etc/postgresql/17/main/conf.d/50-gridcare-audit.conf
sudo systemctl restart postgresql@17-main
```

### 10.3 สร้าง Extension และ Role

```sql
CREATE EXTENSION IF NOT EXISTS pgaudit;
CREATE ROLE gridcare_auditor NOLOGIN;
GRANT SELECT, UPDATE ON gridcare.customers TO gridcare_auditor;
```

### 10.4 ทดสอบ

```sql
SET ROLE callcenter_ro;
SELECT first_name FROM gridcare.customers WHERE customer_id = 7;
SELECT count(*) FROM gridcare.offices;
RESET ROLE;

CREATE ROLE temp_x;
DROP ROLE temp_x;
```

### 10.5 ตรวจสอบ Log

```bash
sudo grep "AUDIT:" /var/log/postgresql/postgresql-17-main.log | tail -4
```

ผลลัพธ์:
```text
2026-11-04 14:30:12.345 +07 [1234] postgres@gridcare app=psql client=[local] LOG:  AUDIT: OBJECT,1,1,READ,SELECT,TABLE,gridcare.customers,SELECT first_name FROM gridcare.customers WHERE customer_id = 7,<not logged>
2026-11-04 14:30:12.456 +07 [1234] postgres@gridcare app=psql client=[local] LOG:  AUDIT: SESSION,1,1,ROLE,CREATE ROLE,,,CREATE ROLE temp_x,<not logged>
2026-11-04 14:30:12.567 +07 [1234] postgres@gridcare app=psql client=[local] LOG:  AUDIT: SESSION,2,1,ROLE,DROP ROLE,,,DROP ROLE temp_x,<not logged>
```

> ✅ ไม่มีบรรทัดของ `offices` เพราะไม่ให้สิทธิ์ `gridcare_auditor` บน offices

### 10.6 `pgaudit.log` Options

| Option | Audit |
|---|---|
| `READ` | SELECT, COPY |
| `WRITE` | INSERT, UPDATE, DELETE |
| `FUNCTION` | Function Call |
| `ROLE` | GRANT, CREATE ROLE |
| `DDL` | CREATE, ALTER, DROP |
| `MISC` | FETCH, DISCARD |
| `ALL` | ทุกอย่าง |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Config พื้นฐาน

```ini
pgaudit.log = 'ddl, role'
pgaudit.log_catalog = off
pgaudit.log_relation = on
pgaudit.log_parameter = off
pgaudit.role = 'gridcare_auditor'
```

### ตัวอย่างที่ 2: Role ที่ Audit

```sql
CREATE ROLE gridcare_auditor NOLOGIN;
GRANT SELECT, UPDATE ON gridcare.customers TO gridcare_auditor;
```

### ตัวอย่างที่ 3: ทดสอบ

```sql
SET ROLE callcenter_ro;
SELECT first_name FROM gridcare.customers WHERE customer_id = 7;
SELECT count(*) FROM gridcare.offices;
RESET ROLE;
```

### ตัวอย่างที่ 4: ตรวจสอบ Audit Log

```bash
sudo grep "AUDIT:" /var/log/postgresql/postgresql-17-main.log | tail -3
```

ผลลัพธ์:
```text
LOG:  AUDIT: OBJECT,1,1,READ,SELECT,TABLE,gridcare.customers,...
LOG:  AUDIT: SESSION,1,1,ROLE,CREATE ROLE,,,CREATE ROLE temp_x,...
LOG:  AUDIT: SESSION,2,1,ROLE,DROP ROLE,,,DROP ROLE temp_x,...
```

### ตัวอย่างที่ 5: ตรวจสอบว่า PII ไม่ลง Log

```bash
sudo grep "AUDIT:" /var/log/postgresql/postgresql-17-main.log | grep -E "1234567890121|0812345678" | wc -l
```

ผลลัพธ์:
```text
0
```

> ✅ ไม่มี PII ใน Log

## 12. สรุปย่อ จำง่าย
- **`pgAudit` = Audit Session + Object**  
- **`pgaudit.log = 'ddl, role'`**  
- **`pgaudit.log_parameter = off` ป้องกัน PII**  
- **`pgaudit.role = 'gridcare_auditor'`**  
- **ต้องตั้ง `shared_preload_libraries`**  
- **ตรวจด้วย `grep AUDIT:`**

ประโยคจำ: **"`pgAudit` ที่ดีคือ `pgAudit` ที่ Audit สิ่งที่ต้อง Audit และไม่ลง PII"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- pgAudit: https://github.com/pgaudit/pgaudit
- PostgreSQL Documentation — Logging: https://www.postgresql.org/docs/17/runtime-config-logging.html
- GridCare Workshop Day 3: Lab 5.1

---

## สรุปส่วนที่ 7 (บทที่ 61–70)

| บท | แก่นของบท | ใช้ต่อในส่วน |
|---|---|---|
| 61 | Backup Strategy + RPO/RTO | Backup |
| 62 | pgBackRest | Backup |
| 63 | WAL Archiving | PITR |
| 64 | MinIO/S3 Repository | Backup |
| 65 | Full/Diff/Incr Backup | Backup Strategy |
| 66 | Restore Test | Compliance |
| 67 | PITR | Incident Recovery |
| 68 | RLS | Security |
| 69 | Masking + pgcrypto | PDPA |
| 70 | pgAudit | Compliance |

---
 