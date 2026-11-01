# บทที่ 81–90

> หนังสือ: คู่มือการใช้งาน PostgreSQL สำหรับ DevOps Engineer, Cloud Engineer และ DBA  
> ส่วนที่ 9 Upgrade และ Safe Migration  
> โทน: ทางการ กระชับ เน้นใช้งานจริง

---

# บทที่ 81 นโยบายเวอร์ชัน PostgreSQL

## 1. เรื่อง
นโยบายเวอร์ชันของ PostgreSQL และการวางแผน Upgrade สำหรับระบบ Production

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจนโยบายเวอร์ชันของ PostgreSQL  
2. เพื่อให้วางแผน Upgrade ล่วงหน้า  
3. เพื่อให้หลีกเลี่ยงการใช้งานเวอร์ชันที่หมดอายุ  
4. เพื่อให้เชื่อมโยง Upgrade กับ Security และ Support

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- อธิบาย Major/Minor Version ได้  
- วางแผน Upgrade ตามนโยบาย  
- ระบุความเสี่ยงของเวอร์ชันที่หมดอายุ  
- กำหนดปฏิทิน Upgrade ประจำปี

## 4. เนื้อหาโดยย่อ
PostgreSQL มี 2 ประเภทเวอร์ชัน:
- **Major Version** (เช่น 17, 18) — ออกทุกปี รองรับ 5 ปี  
- **Minor Version** (เช่น 17.11) — ออกทุกไตรมาส เป็น Patch

**Major Version** ต้อง `pg_upgrade`  
**Minor Version** ต้อง Restart เท่านั้น

## 5. ประโยชน์ที่ได้รับ
- วางแผน Upgrade ได้  
- หลีกเลี่ยงเวอร์ชันหมดอายุ  
- ลดความเสี่ยงจาก CVE  
- ผ่าน Audit

## 6. ข้อควรระวัง
- **Major Version รองรับ 5 ปี**  
- **Minor Version ทุกไตรมาส**  
- **เวอร์ชันหมดอายุไม่ได้รับ Security Fix**  
- **ต้อง Upgrade Minor ก่อน Major**  
- **ต้องทดสอบบน Test Environment ก่อน**

## 7. ข้อดี
- มีแผนชัดเจน  
- หลีกเลี่ยง CVE  
- ผ่าน Audit  
- ใช้ Feature ใหม่ได้

## 8. ข้อเสีย
- ต้องลงทุนเวลา  
- ต้องมี Downtime  
- ต้องทดสอบ

## 9. ข้อห้าม
- ห้ามใช้เวอร์ชันที่หมดอายุบน Production  
- ห้าม Upgrade Major โดยไม่ทดสอบ  
- ห้าม Upgrade Minor โดยไม่ตรวจ Release Notes  
- ห้าม Upgrade ในช่วง Peak Hours  
- ห้าม Upgrade โดยไม่มี Backup ล่าสุด

## 10. รายละเอียด

### 10.1 ตารางเวอร์ชัน PostgreSQL

| Major | เปิดตัว | หมดอายุ | สถานะ |
|---|---|---|---|
| 13 | 2020-09 | 2025-11 | EOL |
| 14 | 2021-09 | 2026-11 | EOL ใกล้ |
| 15 | 2022-10 | 2027-11 | Supported |
| 16 | 2023-09 | 2028-11 | Supported |
| 17 | 2024-09 | 2029-11 | Supported |
| 18 | 2025-09 | 2030-11 | Supported |

> 💡 ตรวจสอบล่าสุดที่ https://www.postgresql.org/support/versioning/

### 10.2 Minor Version

Minor Version ออกทุกไตรมาส:
- 17.11, 17.12, 17.13, ...
- เป็น Patch ที่ไม่เปลี่ยน Format
- Upgrade ด้วย `apt upgrade` + Restart

### 10.3 นโยบาย Upgrade

```text
ทุกปี: อ่าน Release Notes Major Version ใหม่
ทุก 3 เดือน: Upgrade Minor
ทุก 2-3 ปี: วางแผน Upgrade Major
ทุก 5 ปี: ต้อง Upgrade Major ก่อน EOL
```

### 10.4 ขั้นตอน Upgrade

**Minor:**
1. อ่าน Release Notes  
2. Backup  
3. `apt upgrade`  
4. Restart  
5. ตรวจสอบ

**Major:**
1. อ่าน Release Notes  
2. ทดสอบบน Test  
3. `pg_upgrade --check`  
4. Backup  
5. `pg_upgrade --link`  
6. ตรวจสอบ  
7. เปิดใช้งาน

### 10.5 ปฏิทิน Upgrade

| เดือน | งาน |
|---|---|
| มกราคม | อ่าน Roadmap |
| เมษายน | Upgrade Minor |
| กรกฎาคม | Upgrade Minor |
| ตุลาคม | Upgrade Minor + วางแผน Major |
| พฤศจิกายน | Upgrade Major (ถ้าจำเป็น) |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: ตรวจสอบเวอร์ชันปัจจุบัน

```sql
SELECT version();
SHOW server_version;
SHOW server_version_num;
```

ผลลัพธ์:
```text
 PostgreSQL 17.11 (Ubuntu 17.11-1.pgdg24.04+2) on x86_64-pc-linux-gnu

 17.11

 170011
```

### ตัวอย่างที่ 2: ตรวจสอบเวอร์ชันที่ติดตั้ง

```bash
pg_lsclusters
```

ผลลัพธ์:
```text
Ver Cluster Port Status Owner    Data directory
17  main    5432 online postgres /var/lib/postgresql/17/main
18  main    5432 down   postgres /var/lib/postgresql/18/main
```

### ตัวอย่างที่ 3: ตรวจสอบ EOL

```bash
# ตรวจสอบที่ https://www.postgresql.org/support/versioning/
# PostgreSQL 14 จะ EOL พฤศจิกายน 2026
```

### ตัวอย่างที่ 4: Upgrade Minor

```bash
sudo apt update
sudo apt upgrade -y postgresql-17
sudo systemctl restart postgresql@17-main
sudo -u postgres psql -c "SELECT version()"
```

## 12. สรุปย่อ จำง่าย
- **Major Version = 5 ปี**  
- **Minor Version = ทุกไตรมาส**  
- **Major ต้อง `pg_upgrade`**  
- **Minor ต้อง Restart**  
- **ต้อง Upgrade Minor ก่อน Major**  
- **ห้ามใช้เวอร์ชันที่หมดอายุ**

ประโยคจำ: **"เวอร์ชันที่หมดอายุคือช่องโหว่ที่รอวันโจมตี"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Versioning Policy: https://www.postgresql.org/support/versioning/
- PostgreSQL Release Notes: https://www.postgresql.org/docs/release/
- GridCare Workshop Day 5: Lab 1.1

---

# บทที่ 82 pg_upgrade --check

## 1. เรื่อง
การตรวจสอบความพร้อมก่อน Upgrade ด้วย `pg_upgrade --check`

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจ `pg_upgrade --check`  
2. เพื่อให้ตรวจสอบ Cluster Compatibility  
3. เพื่อให้แก้ไขปัญหาก่อน Upgrade จริง  
4. เพื่อให้วางแผน Downtime

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- รัน `pg_upgrade --check`  
- อ่านผลลัพธ์  
- แก้ไข Extension ที่ไม่รองรับ  
- แก้ไข Checksums ที่ไม่ตรงกัน

## 4. เนื้อหาโดยย่อ
`pg_upgrade --check` ตรวจสอบ:
- Cluster Version  
- Database User  
- Connection Settings  
- Prepared Transaction  
- Contrib/isn  
- Tables WITH OIDS  
- `sql_identifier` Columns  
- Required Libraries  
- New Cluster Tablespaces

## 5. ประโยชน์ที่ได้รับ
- ลดความเสี่ยง Upgrade ล้ม  
- ตรวจสอบก่อน Downtime  
- วางแผนได้  
- ผ่าน Audit

## 6. ข้อควรระวัง
- **ต้อง `cd /var/lib/postgresql` ก่อนรัน**  
- **Extension ต้องติดตั้งรุ่นใหม่ก่อน**  
- **`data_checksums` ต้องตรงกัน**  
- **Old Cluster ต้องไม่มีการเปลี่ยนแปลง**  
- **ต้องมี Disk เพียงพอ**

## 7. ข้อดี
- ลดความเสี่ยง  
- ตรวจสอบได้  
- วางแผนได้

## 8. ข้อเสีย
- ต้องมี Test Environment  
- ต้องใช้เวลา

## 9. ข้อห้าม
- ห้าม Upgrade โดยไม่ `--check`  
- ห้าม Upgrade โดยไม่ Backup  
- ห้าม Upgrade โดยไม่ทดสอบ  
- ห้าม Upgrade ในช่วง Peak Hours

## 10. รายละเอียด

### 10.1 เตรียมรุ่น 18

```bash
sudo apt install -y postgresql-18 postgresql-18-pgaudit postgresql-18-partman postgresql-18-repack
pg_lsclusters
```

ผลลัพธ์:
```text
Ver Cluster Port Status Owner    Data directory
17  main    5432 online postgres /var/lib/postgresql/17/main
18  main    5432 down   postgres /var/lib/postgresql/18/main
```

### 10.2 หยุด Cluster 18 และตั้ง `start.conf`

```bash
sudo systemctl stop postgresql@18-main 2>/dev/null
echo manual | sudo tee /etc/postgresql/18/main/start.conf
```

### 10.3 คัดลอก Config และ Cert

```bash
sudo cp /etc/postgresql/17/main/conf.d/*.conf /etc/postgresql/18/main/conf.d/
sudo cp /etc/postgresql/17/main/server.crt /etc/postgresql/17/main/server.key /etc/postgresql/18/main/
sudo sed -i 's#/etc/postgresql/17/main/server#/etc/postgresql/18/main/server#' /etc/postgresql/18/main/conf.d/30-gridcare-ssl.conf
sudo chown -R postgres:postgres /etc/postgresql/18/main
sudo chmod 600 /etc/postgresql/18/main/server.key
```

### 10.4 ตรวจสอบ Checksums

```bash
sudo -u postgres /usr/lib/postgresql/18/bin/pg_controldata /var/lib/postgresql/18/main | grep -i checksum
```

ผลลัพธ์:
```text
Data page checksum version:           1
```

### 10.5 ตรวจสอบ Extension

```bash
sudo -u postgres psql -X -d gridcare -c "SELECT extname, extversion FROM pg_extension ORDER BY 1" -c "SHOW data_checksums"
```

ผลลัพธ์:
```text
   extname          | extversion 
--------------------+------------
 auto_explain       | 1.0
 pgaudit            | 17.1
 pgcrypto           | 1.3
 pg_partman         | 5.5.0
 pg_stat_statements | 1.11
 plpgsql            | 1.0

 data_checksums 
----------------
 on
```

### 10.6 รัน `pg_upgrade --check`

```bash
cd /var/lib/postgresql
sudo -u postgres /usr/lib/postgresql/18/bin/pg_upgrade --check \
  -b /usr/lib/postgresql/17/bin -B /usr/lib/postgresql/18/bin \
  -d /var/lib/postgresql/17/main -D /var/lib/postgresql/18/main \
  -o "-c config_file=/etc/postgresql/17/main/postgresql.conf" \
  -O "-c config_file=/etc/postgresql/18/main/postgresql.conf"
```

ผลลัพธ์:
```text
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

### 10.7 ปัญหาที่พบบ่อย

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `could not load library "$libdir/pgaudit"` | ยังไม่ติดตั้ง Extension รุ่น 18 | `apt install postgresql-18-pgaudit` |
| `could not open log file ... Permission denied` | รันจากโฟลเดอร์ที่ postgres เขียนไม่ได้ | `cd /var/lib/postgresql` ก่อน |
| `old cluster does not use data checksums but the new one does` | รุ่น 17 ปิด Checksums | สร้างรุ่น 18 ด้วย `--no-data-checksums` |
| `2 or more clusters running` | หลาย Cluster ทำงาน | หยุด Cluster ที่ไม่ใช้ |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: `pg_upgrade --check` ที่ผ่าน

```bash
cd /var/lib/postgresql
sudo -u postgres /usr/lib/postgresql/18/bin/pg_upgrade --check \
  -b /usr/lib/postgresql/17/bin -B /usr/lib/postgresql/18/bin \
  -d /var/lib/postgresql/17/main -D /var/lib/postgresql/18/main \
  -o "-c config_file=/etc/postgresql/17/main/postgresql.conf" \
  -O "-c config_file=/etc/postgresql/18/main/postgresql.conf"
```

ผลลัพธ์:
```text
*Clusters are compatible*
```

### ตัวอย่างที่ 2: `pg_upgrade --check` ที่ล้ม

```text
Checking for presence of required libraries                   fatal
Your installation references loadable libraries that are missing from the
new installation.  You can add these libraries to the new installation,
or remove the functions using them from the old installation.  A list of
problem libraries is in the file:
    loadable_libraries.txt
```

**แก้ไข:**
```bash
sudo apt install -y postgresql-18-pgaudit
```

### ตัวอย่างที่ 3: ตรวจสอบ Checksums

```bash
sudo -u postgres /usr/lib/postgresql/17/bin/pg_controldata /var/lib/postgresql/17/main | grep -i checksum
sudo -u postgres /usr/lib/postgresql/18/bin/pg_controldata /var/lib/postgresql/18/main | grep -i checksum
```

ผลลัพธ์:
```text
Data page checksum version:           1
Data page checksum version:           1
```

> ✅ ต้องตรงกัน

### ตัวอย่างที่ 4: ไฟล์ที่ต้องเก็บ

```bash
ls /var/lib/postgresql/
```

ผลลัพธ์:
```text
delete_old_cluster.sh  pg_upgrade_output.d  update_extensions.sql
```

> 💡 `update_extensions.sql` และ `delete_old_cluster.sh` ถูกสร้างโดย `pg_upgrade`

## 12. สรุปย่อ จำง่าย
- **`pg_upgrade --check` = ตรวจก่อน Upgrade**  
- **ต้อง `cd /var/lib/postgresql`**  
- **Extension ต้องติดตั้งรุ่นใหม่ก่อน**  
- **`data_checksums` ต้องตรงกัน**  
- **`*Clusters are compatible*` คือผ่าน**  
- **เก็บ `update_extensions.sql`**

ประโยคจำ: **"`--check` ที่ดีคือ `--check` ที่ผ่านก่อน Downtime"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — pg_upgrade: https://www.postgresql.org/docs/18/pgupgrade.html
- GridCare Workshop Day 5: Lab 1.1

---

# บทที่ 83 pg_upgrade --link

## 1. เรื่อง
การ Upgrade ด้วย `pg_upgrade --link` สำหรับ Production

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจ `--link`  
2. เพื่อให้ Upgrade ได้เร็ว  
3. เพื่อให้ตรวจสอบผล  
4. เพื่อให้จัดการ Extension และ Statistics

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- รัน `pg_upgrade --link`  
- ตรวจสอบผล  
- จัดการ `update_extensions.sql`  
- ใช้ `vacuumdb --missing-stats-only`

## 4. เนื้อหาโดยย่อ
`--link` ทำให้ Upgrade เร็วเพราะ **Hard Link ไฟล์** แทน Copy  
ข้อดี: เร็วมาก  
ข้อจำกัด: ถ้าล้ม Old Cluster เสียหาย — ต้อง Backup ก่อน

ขั้นตอน:
1. หยุด Cluster ทั้งหมด  
2. Backup  
3. `pg_upgrade --link --jobs 2`  
4. Start Cluster ใหม่  
5. `stanza-upgrade`  
6. `update_extensions.sql`  
7. `vacuumdb --missing-stats-only`

## 5. ประโยชน์ที่ได้รับ
- Upgrade เร็ว  
- ลด Downtime  
- ใช้ได้กับ Cluster ใหญ่

## 6. ข้อควรระวัง
- **`--link` ทำให้ Old Cluster เสียหายถ้าล้ม**  
- **ต้อง Backup ก่อน**  
- **ต้องหยุด Cluster ทั้งหมด**  
- **ต้อง `stanza-upgrade`**  
- **ต้อง `vacuumdb --missing-stats-only`**

## 7. ข้อดี
- เร็วมาก  
- ลด Downtime  
- ใช้กับ Cluster ใหญ่

## 8. ข้อเสีย
- Old Cluster เสียหายถ้าล้ม  
- ต้อง Backup ก่อน

## 9. ข้อห้าม
- ห้าม `--link` โดยไม่มี Backup  
- ห้าม `--link` โดยไม่หยุด Cluster  
- ห้าม `--link` โดยไม่ทดสอบ `--check` ก่อน  
- ห้ามลืม `stanza-upgrade`  
- ห้ามลืม `vacuumdb --missing-stats-only`

## 10. รายละเอียด

### 10.1 หยุด Cluster

```bash
# บน pg2 (Replica ก่อน)
sudo systemctl stop patroni@17-main

# บน pg1 (Primary)
sudo systemctl stop patroni@17-main

pgrep -u postgres -ax postgres | head -3
```

ผลลัพธ์:
```text
(ไม่มี output = หยุดแล้ว)
```

### 10.2 `pg_upgrade --link`

```bash
cd /var/lib/postgresql
time sudo -u postgres /usr/lib/postgresql/18/bin/pg_upgrade --link --jobs 2 \
  -b /usr/lib/postgresql/17/bin -B /usr/lib/postgresql/18/bin \
  -d /var/lib/postgresql/17/main -D /var/lib/postgresql/18/main \
  -o "-c config_file=/etc/postgresql/17/main/postgresql.conf" \
  -O "-c config_file=/etc/postgresql/18/main/postgresql.conf"
```

ผลลัพธ์:
```text
Upgrade Complete
----------------
Some statistics are not transferred by pg_upgrade.
Once you start the new server, consider running:
    /usr/lib/postgresql/18/bin/vacuumdb --all --analyze-in-stages --missing-stats-only
    /usr/lib/postgresql/18/bin/vacuumdb --all --analyze-only

pg_upgrade --link: 2 s
```

### 10.3 Patroni Config 18

```bash
sudo sed -e 's#/17/#/18/#g' -e 's#17-main#18-main#g' \
  /etc/patroni/17-main.yml | sudo tee /etc/patroni/18-main.yml > /dev/null
sudo chown postgres:postgres /etc/patroni/18-main.yml
sudo chmod 640 /etc/patroni/18-main.yml
grep -nE "data_dir|config_dir|bin_dir|pgpass|log_filename" /etc/patroni/18-main.yml
```

ผลลัพธ์:
```text
17:  data_dir: /var/lib/postgresql/18/main
18:  config_dir: /etc/postgresql/18/main
19:  bin_dir: /usr/lib/postgresql/18/bin
20:  pgpass: /var/lib/postgresql/18-main.pgpass
35:    log_filename: postgresql-18-main.log
```

### 10.4 ลบ DCS

```bash
sudo -u postgres patronictl -c /etc/patroni/18-main.yml remove gridcare
```

ผลลัพธ์:
```text
Please confirm the cluster name to remove: gridcare
You are about to remove all information in DCS for gridcare, please type: "Yes I am aware": Yes I am aware
```

### 10.5 Start Patroni 18

```bash
sudo systemctl disable patroni@17-main
sudo systemctl enable --now patroni@18-main
sleep 15
patronictl list
```

ผลลัพธ์:
```text
| pg1 | 10.104... | Leader | running | 2 |
```

### 10.6 `stanza-upgrade`

```bash
sudo sed -i 's#^pg1-path=.*#pg1-path=/var/lib/postgresql/18/main#' /etc/pgbackrest.conf
sudo -u postgres pgbackrest --stanza=gridcare stanza-upgrade
sudo -u postgres pgbackrest --stanza=gridcare check
```

ผลลัพธ์:
```text
2026-11-06 10:52:30.456 P00   INFO: stanza-upgrade command end: completed successfully (333ms)
2026-11-06 10:52:47.012 P00   INFO: check command end: completed successfully (1889ms)
```

### 10.7 Full Backup

```bash
sudo -u postgres pgbackrest --stanza=gridcare --type=full backup
```

### 10.8 `update_extensions.sql`

```bash
sudo -u postgres psql -X -f /var/lib/postgresql/update_extensions.sql
```

ผลลัพธ์:
```text
ALTER EXTENSION
ALTER EXTENSION
ALTER EXTENSION
ERROR:  extension "pgaudit" has no update path from version "17.1" to version "18.0"
ALTER EXTENSION
```

**แก้ไข:**
```bash
sudo -u postgres psql -X -d gridcare -c "DROP EXTENSION pgaudit" -c "CREATE EXTENSION pgaudit"
```

### 10.9 `vacuumdb --missing-stats-only`

```bash
sudo -u postgres /usr/lib/postgresql/18/bin/vacuumdb --all --analyze-in-stages --missing-stats-only
sudo -u postgres /usr/lib/postgresql/18/bin/vacuumdb --all --analyze-only --jobs 2
```

ผลลัพธ์:
```text
vacuumdb: processing database "gridcare": Generating minimal optimizer statistics (1 target)
...
vacuumdb: processing database "gridcare": Generating default (full) optimizer statistics
```

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: `pg_upgrade --link`

```bash
cd /var/lib/postgresql
time sudo -u postgres /usr/lib/postgresql/18/bin/pg_upgrade --link --jobs 2 \
  -b /usr/lib/postgresql/17/bin -B /usr/lib/postgresql/18/bin \
  -d /var/lib/postgresql/17/main -D /var/lib/postgresql/18/main \
  -o "-c config_file=/etc/postgresql/17/main/postgresql.conf" \
  -O "-c config_file=/etc/postgresql/18/main/postgresql.conf"
```

ผลลัพธ์:
```text
Upgrade Complete
pg_upgrade --link: 2 s
```

### ตัวอย่างที่ 2: ตรวจสอบหลัง Upgrade

```bash
patronictl list
sudo -u postgres psql -X -d gridcare -Atc "SELECT version()" -c "SHOW data_checksums" \
  -c "SELECT extname || ' ' || extversion FROM pg_extension ORDER BY 1" \
  -c "SELECT statistics_name FROM pg_stats_ext" -c "SELECT count(*) FROM gridcare.bills"
```

ผลลัพธ์:
```text
| pg1 | ... | Leader | running | 2 |
| pg2 | ... | Replica | streaming | 2 |

PostgreSQL 18.6 (Ubuntu 18.6-1.pgdg24.04+2) on x86_64-pc-linux-gnu
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

### ตัวอย่างที่ 3: `pgbackrest info`

```bash
sudo -u postgres pgbackrest --stanza=gridcare info | grep -E "db \(|full backup"
```

ผลลัพธ์:
```text
    db (prior)    wal archive min/max (17): ...
        full backup: 20261105-152200F
    db (current)  wal archive min/max (18): ...
        full backup: 20261106-110000F
```

### ตัวอย่างที่ 4: `pg2` Replica

```bash
sudo systemctl enable --now patroni@18-main
journalctl -u patroni@18-main -f
```

ผลลัพธ์:
```text
INFO: trying to bootstrap from leader 'pg1'
INFO: replica has been created using basebackup
INFO: bootstrapped from leader 'pg1'
INFO: no action. I am (pg2), a secondary, and following a leader (pg1)
```

## 12. สรุปย่อ จำง่าย
- **`--link` = เร็ว แต่ Old Cluster เสียหายถ้าล้ม**  
- **ต้อง Backup ก่อน**  
- **ต้องหยุด Cluster ทั้งหมด**  
- **`stanza-upgrade` หลัง Upgrade**  
- **`update_extensions.sql`**  
- **`vacuumdb --missing-stats-only`**

ประโยคจำ: **"`--link` ให้ความเร็ว แต่ต้องแลกด้วยความเสี่ยง"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — pg_upgrade: https://www.postgresql.org/docs/18/pgupgrade.html
- Patroni — Major Upgrade: https://patroni.readthedocs.io/en/latest/existing_data.html
- GridCare Workshop Day 5: Lab 1.2

---

# บทที่ 84 Upgrade คลัสเตอร์ Patroni

## 1. เรื่อง
การ Upgrade คลัสเตอร์ Patroni จาก PostgreSQL 17 เป็น 18

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้ Upgrade Patroni Cluster ได้  
2. เพื่อให้จัดการ DCS  
3. เพื่อให้จัดการ Config  
4. เพื่อให้จัดการ Replica

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- หยุด Patroni ตามลำดับ  
- รัน `pg_upgrade --link`  
- ลบ DCS  
- Start Patroni 18  
- สร้าง Replica ใหม่

## 4. เนื้อหาโดยย่อ
ขั้นตอน:
1. หยุด Patroni Replica ก่อน  
2. หยุด Patroni Primary  
3. `pg_upgrade --link`  
4. สร้าง `patroni.yml` รุ่น 18  
5. ลบ DCS  
6. Start Patroni 18  
7. `stanza-upgrade`  
8. Replica Rebuild

## 5. ประโยชน์ที่ได้รับ
- Upgrade Cluster ได้  
- ลด Downtime  
- ไม่มี Split-Brain  
- ผ่าน Audit

## 6. ข้อควรระวัง
- **หยุด Replica ก่อน Primary**  
- **`patronictl remove` หลัง Upgrade**  
- **`stanza-upgrade` ทันที**  
- **Replica ต้อง Rebuild**  
- **ต้อง Full Backup หลัง Upgrade**

## 7. ข้อดี
- มาตรฐาน  
- ลด Downtime  
- ไม่มี Split-Brain

## 8. ข้อเสีย
- ต้องหยุด Cluster  
- ต้อง Rebuild Replica  
- ต้อง Full Backup

## 9. ข้อห้าม
- ห้ามหยุด Primary ก่อน Replica  
- ห้าม Start Patroni โดยไม่ลบ DCS  
- ห้ามลืม `stanza-upgrade`  
- ห้ามลืม Full Backup  
- ห้ามใช้ `ALTER SYSTEM` กับ Patroni

## 10. รายละเอียด

### 10.1 หยุด Replica ก่อน

```bash
# บน pg2
date +%T
sudo systemctl stop patroni@17-main
```

ผลลัพธ์:
```text
10:45:12
```

### 10.2 หยุด Primary

```bash
# บน pg1
sudo systemctl stop patroni@17-main
sudo -u postgres patronictl -c /etc/patroni/17-main.yml list
pgrep -u postgres -ax postgres | head -3
```

ผลลัพธ์:
```text
(ไม่มี Leader, ไม่มี process)
```

### 10.3 `pg_upgrade --link`

```bash
cd /var/lib/postgresql
time sudo -u postgres /usr/lib/postgresql/18/bin/pg_upgrade --link --jobs 2 \
  -b /usr/lib/postgresql/17/bin -B /usr/lib/postgresql/18/bin \
  -d /var/lib/postgresql/17/main -D /var/lib/postgresql/18/main \
  -o "-c config_file=/etc/postgresql/17/main/postgresql.conf" \
  -O "-c config_file=/etc/postgresql/18/main/postgresql.conf"
```

### 10.4 `patroni.yml` 18

```bash
sudo sed -e 's#/17/#/18/#g' -e 's#17-main#18-main#g' \
  /etc/patroni/17-main.yml | sudo tee /etc/patroni/18-main.yml > /dev/null
sudo chown postgres:postgres /etc/patroni/18-main.yml
sudo chmod 640 /etc/patroni/18-main.yml
```

### 10.5 ลบ DCS

```bash
sudo -u postgres patronictl -c /etc/patroni/18-main.yml remove gridcare
# ยืนยัน: gridcare + Yes I am aware
```

### 10.6 Start Patroni 18

```bash
sudo systemctl disable patroni@17-main
sudo systemctl enable --now patroni@18-main
sleep 15
patronictl list
```

ผลลัพธ์:
```text
| pg1 | 10.104... | Leader | running | 2 |
```

### 10.7 `stanza-upgrade`

```bash
sudo sed -i 's#^pg1-path=.*#pg1-path=/var/lib/postgresql/18/main#' /etc/pgbackrest.conf
sudo -u postgres pgbackrest --stanza=gridcare stanza-upgrade
sudo -u postgres pgbackrest --stanza=gridcare check
```

### 10.8 Replica Rebuild

```bash
# บน pg2
sudo -u postgres bash -c 'rm -rf /var/lib/postgresql/18/main/*'
sudo sed -e 's#/17/#/18/#g' -e 's#17-main#18-main#g' \
  /etc/patroni/17-main.yml | sudo tee /etc/patroni/18-main.yml > /dev/null
sudo chown postgres:postgres /etc/patroni/18-main.yml
sudo chmod 640 /etc/patroni/18-main.yml
sudo systemctl disable patroni@17-main
sudo systemctl enable --now patroni@18-main
journalctl -u patroni@18-main -f
```

ผลลัพธ์:
```text
INFO: trying to bootstrap from leader 'pg1'
INFO: replica has been created using basebackup
INFO: bootstrapped from leader 'pg1'
INFO: no action. I am (pg2), a secondary, and following a leader (pg1)
```

### 10.9 ตรวจสอบ

```bash
patronictl list
```

ผลลัพธ์:
```text
| pg1 | 10.104... | Leader  | running   | 2 |
| pg2 | 10.104... | Replica | streaming | 2 |
```

### 10.10 Full Backup

```bash
sudo -u postgres pgbackrest --stanza=gridcare --type=full backup
```

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: หยุด Replica ก่อน

```bash
# บน pg2
sudo systemctl stop patroni@17-main
```

### ตัวอย่างที่ 2: หยุด Primary

```bash
# บน pg1
sudo systemctl stop patroni@17-main
```

### ตัวอย่างที่ 3: `pg_upgrade --link`

```bash
cd /var/lib/postgresql
sudo -u postgres /usr/lib/postgresql/18/bin/pg_upgrade --link --jobs 2 \
  -b /usr/lib/postgresql/17/bin -B /usr/lib/postgresql/18/bin \
  -d /var/lib/postgresql/17/main -D /var/lib/postgresql/18/main \
  -o "-c config_file=/etc/postgresql/17/main/postgresql.conf" \
  -O "-c config_file=/etc/postgresql/18/main/postgresql.conf"
```

### ตัวอย่างที่ 4: ลบ DCS

```bash
sudo -u postgres patronictl -c /etc/patroni/18-main.yml remove gridcare
```

### ตัวอย่างที่ 5: Start Patroni 18

```bash
sudo systemctl enable --now patroni@18-main
sleep 15
patronictl list
```

## 12. สรุปย่อ จำง่าย
- **หยุด Replica ก่อน Primary**  
- **`pg_upgrade --link`**  
- **`patronictl remove`**  
- **Start Patroni 18**  
- **`stanza-upgrade`**  
- **Replica Rebuild**

ประโยคจำ: **"Upgrade Patroni ที่ดีคือ Upgrade ที่ไม่มี Split-Brain"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- Patroni — Major Upgrade: https://patroni.readthedocs.io/en/latest/existing_data.html
- pgBackRest — stanza-upgrade: https://pgbackrest.org/command.html
- GridCare Workshop Day 5: Lab 1.2

---

# บทที่ 85 Extension และ Statistics หลัง Upgrade

## 1. เรื่อง
การจัดการ Extension และ Statistics หลัง `pg_upgrade`

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้จัดการ Extension ที่ไม่มี Update Path  
2. เพื่อให้ใช้ `update_extensions.sql`  
3. เพื่อให้ใช้ `vacuumdb --missing-stats-only`  
4. เพื่อให้ตรวจสอบ Extended Statistics

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- รัน `update_extensions.sql`  
- แก้ไข `pgaudit` ที่ไม่มี Update Path  
- รัน `vacuumdb --missing-stats-only`  
- ตรวจสอบ `pg_stats_ext`

## 4. เนื้อหาโดยย่อ
หลัง Upgrade:
1. `update_extensions.sql` — อัปเดต Extension  
2. `DROP EXTENSION` + `CREATE EXTENSION` สำหรับ pgaudit  
3. `vacuumdb --analyze-in-stages --missing-stats-only`  
4. `vacuumdb --analyze-only`  
5. ตรวจสอบ `pg_stats_ext`

## 5. ประโยชน์ที่ได้รับ
- Extension ทำงานได้  
- Statistics ครบ  
- Planner เลือกแผนถูก  
- ผ่าน Audit

## 6. ข้อควรระวัง
- **`pgaudit` ไม่มี Update Path 17→18**  
- **Extended Statistics ไม่ถูกโอน**  
- **`vacuumdb --missing-stats-only` ต้องใช้ Path เต็ม**  
- **ต้องตรวจสอบ `pg_stats_ext`**  
- **ต้อง Backup ก่อน**

## 7. ข้อดี
- Extension ทำงานได้  
- Statistics ครบ  
- Planner เลือกแผนถูก

## 8. ข้อเสีย
- ต้อง DROP/CREATE pgaudit  
- ต้อง ANALYZE ใหม่  
- ต้องใช้เวลา

## 9. ข้อห้าม
- ห้ามลืม `update_extensions.sql`  
- ห้ามใช้ `pgaudit` ที่ไม่มี Update Path  
- ห้ามลืม `vacuumdb --missing-stats-only`  
- ห้ามลืมตรวจสอบ Extended Statistics

## 10. รายละเอียด

### 10.1 `update_extensions.sql`

```bash
sudo -u postgres psql -X -f /var/lib/postgresql/update_extensions.sql
```

ผลลัพธ์:
```text
ALTER EXTENSION
ALTER EXTENSION
ALTER EXTENSION
ERROR:  extension "pgaudit" has no update path from version "17.1" to version "18.0"
ALTER EXTENSION
```

### 10.2 แก้ไข `pgaudit`

```bash
sudo -u postgres psql -X -d gridcare -c "DROP EXTENSION pgaudit" -c "CREATE EXTENSION pgaudit"
```

ผลลัพธ์:
```text
DROP EXTENSION
CREATE EXTENSION
```

### 10.3 `vacuumdb --missing-stats-only`

```bash
sudo -u postgres /usr/lib/postgresql/18/bin/vacuumdb --all --analyze-in-stages --missing-stats-only
sudo -u postgres /usr/lib/postgresql/18/bin/vacuumdb --all --analyze-only --jobs 2
```

ผลลัพธ์:
```text
vacuumdb: processing database "gridcare": Generating minimal optimizer statistics (1 target)
...
vacuumdb: processing database "gridcare": Generating default (full) optimizer statistics
```

### 10.4 ตรวจสอบ Extension

```bash
sudo -u postgres psql -X -d gridcare -c "SELECT extname || ' ' || extversion FROM pg_extension ORDER BY 1"
```

ผลลัพธ์:
```text
 auto_explain 1.0
 pg_partman 5.5.0
 pgaudit 18.0
 pgcrypto 1.4
 pg_stat_statements 1.12
 plpgsql 1.0
```

### 10.5 ตรวจสอบ Extended Statistics

```sql
SELECT statistics_name, attnames, kinds FROM pg_stats_ext;
```

ผลลัพธ์ (หลัง `vacuumdb --missing-stats-only`):
```text
    statistics_name    |        attnames         | kinds 
-----------------------+-------------------------+-------
 bills_period_status   | {billing_period,status} | {mcv}
```

> ⚠️ ถ้าว่างแสดงว่า Extended Statistics ไม่ถูกโอน ต้องสร้างใหม่

### 10.6 สร้าง Extended Statistics ใหม่ (ถ้าจำเป็น)

```sql
CREATE STATISTICS bills_period_status (mcv) ON billing_period, status FROM gridcare.bills;
ANALYZE gridcare.bills;
```

### 10.7 ตรวจสอบว่า Planner เลือกแผนถูก

```sql
EXPLAIN (ANALYZE, TIMING OFF)
SELECT count(*) FROM gridcare.bills WHERE billing_period = '2026-09-01' AND status = 'UNPAID';
```

ผลลัพธ์:
```text
               ->  Parallel Seq Scan on bills
                     (cost=0.00..7933.85 rows=300 width=0) (actual time=0.012..0.034 rows=0 loops=3)
```

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: `update_extensions.sql`

```bash
sudo -u postgres psql -X -f /var/lib/postgresql/update_extensions.sql
```

### ตัวอย่างที่ 2: แก้ไข `pgaudit`

```bash
sudo -u postgres psql -X -d gridcare -c "DROP EXTENSION pgaudit" -c "CREATE EXTENSION pgaudit"
```

### ตัวอย่างที่ 3: `vacuumdb --missing-stats-only`

```bash
sudo -u postgres /usr/lib/postgresql/18/bin/vacuumdb --all --analyze-in-stages --missing-stats-only
sudo -u postgres /usr/lib/postgresql/18/bin/vacuumdb --all --analyze-only --jobs 2
```

### ตัวอย่างที่ 4: ตรวจสอบ Extended Statistics

```sql
SELECT statistics_name FROM pg_stats_ext;
```

ผลลัพธ์:
```text
    statistics_name    
-----------------------
 bills_period_status
```

### ตัวอย่างที่ 5: ตรวจสอบ Extension

```sql
SELECT extname, extversion FROM pg_extension ORDER BY 1;
```

ผลลัพธ์:
```text
 auto_explain       | 1.0
 pg_partman         | 5.5.0
 pgaudit            | 18.0
 pgcrypto           | 1.4
 pg_stat_statements | 1.12
 plpgsql            | 1.0
```

## 12. สรุปย่อ จำง่าย
- **`update_extensions.sql` ต้องรัน**  
- **`pgaudit` ต้อง DROP/CREATE**  
- **`vacuumdb --missing-stats-only` ต้องรัน**  
- **ตรวจสอบ `pg_stats_ext`**  
- **ตรวจสอบ `pg_extension`**  
- **Full Backup หลัง Upgrade**

ประโยคจำ: **"Extension ที่ดีคือ Extension ที่ทำงานหลัง Upgrade"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — pg_upgrade: https://www.postgresql.org/docs/18/pgupgrade.html
- pgAudit — Upgrading: https://github.com/pgaudit/pgaudit
- GridCare Workshop Day 5: Lab 1.2

---

# บทที่ 86 หลักการ Safe Migration

## 1. เรื่อง
หลักการทำ Migration บน Production อย่างปลอดภัย โดยไม่บล็อกระบบ

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจหลักการ Safe Migration  
2. เพื่อให้หลีกเลี่ยง Lock ที่ทำให้ระบบหยุด  
3. เพื่อให้เลือกวิธี Migration ที่เหมาะ  
4. เพื่อให้ทดสอบก่อนใช้จริง

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- อธิบายหลักการ 7 ข้อ  
- เลือกวิธี Migration ตามขนาดตาราง  
- ตั้ง `lock_timeout` ก่อน DDL  
- ใช้ `run_migration.sh`

## 4. เนื้อหาโดยย่อ
หลักการ 7 ข้อ:
1. ขอ Lock แรงให้สั้นที่สุด  
2. ใช้ `lock_timeout` ทุกครั้ง  
3. ใช้ `CONCURRENTLY` สำหรับ Index  
4. ใช้ `NOT VALID` + `VALIDATE` สำหรับ Constraint  
5. Backfill เป็นช่วง  
6. ใช้ `run_migration.sh`  
7. ทดสอบบน Test

## 5. ประโยชน์ที่ได้รับ
- ไม่บล็อกระบบ  
- ลด Downtime  
- ลดความเสี่ยง  
- ผ่าน Audit

## 6. ข้อควรระวัง
- **`ALTER TABLE` ขอ AccessExclusiveLock**  
- **`CREATE INDEX` บล็อกการเขียน**  
- **`NOT NULL` ต้อง Scan ทั้งตาราง**  
- **`ADD COLUMN DEFAULT` ในรุ่น 11+ ไม่ Scan**  
- **`lock_timeout` ต้องตั้งทุกครั้ง**

## 7. ข้อดี
- ไม่บล็อกระบบ  
- ลด Downtime  
- ลดความเสี่ยง

## 8. ข้อเสีย
- Migration ใช้เวลานานขึ้น  
- ต้องทำหลายขั้น  
- ต้องทดสอบ

## 9. ข้อห้าม
- ห้าม `ALTER TABLE` โดยไม่ `lock_timeout`  
- ห้าม `CREATE INDEX` โดยไม่ `CONCURRENTLY`  
- ห้าม `ALTER TABLE ... ADD COLUMN ... NOT NULL` โดยไม่มี DEFAULT  
- ห้าม Backfill ทั้งตารางในครั้งเดียว  
- ห้าม Migration ในช่วง Peak Hours

## 10. รายละเอียด

### 10.1 Lock ที่ Migration ใช้

| คำสั่ง | Lock |
|---|---|
| `SELECT` | AccessShareLock |
| `INSERT`/`UPDATE`/`DELETE` | RowExclusiveLock |
| `CREATE INDEX` | ShareLock |
| `CREATE INDEX CONCURRENTLY` | ShareUpdateExclusiveLock |
| `ALTER TABLE` | AccessExclusiveLock |
| `VALIDATE CONSTRAINT` | ShareUpdateExclusiveLock |

### 10.2 `lock_timeout`

```sql
SET lock_timeout = '3s';
ALTER TABLE gridcare.bills ADD COLUMN reminder_count smallint NOT NULL DEFAULT 0;
```

ผลลัพธ์ (ถ้า Lock ไม่ได้):
```text
ERROR:  canceling statement due to lock timeout
SQLSTATE: 55P03
```

### 10.3 หลักการ 7 ข้อ

**1. ขอ Lock แรงให้สั้นที่สุด**
```sql
SET lock_timeout = '3s';
ALTER TABLE ...;
```

**2. `lock_timeout` ทุกครั้ง**
```sql
SET LOCAL lock_timeout = '3s';
```

**3. `CONCURRENTLY` สำหรับ Index**
```sql
CREATE INDEX CONCURRENTLY idx ON table (col);
```

**4. `NOT VALID` + `VALIDATE` สำหรับ Constraint**
```sql
ALTER TABLE ... ADD CONSTRAINT ... CHECK (...) NOT VALID;
ALTER TABLE ... VALIDATE CONSTRAINT ...;
```

**5. Backfill เป็นช่วง**
```sql
DO $$
DECLARE
    lo bigint := 0;
    hi bigint;
    max_id bigint;
BEGIN
    SELECT max(id) INTO max_id FROM table;
    WHILE lo <= max_id LOOP
        hi := lo + 10000;
        UPDATE table SET col = value WHERE id >= lo AND id < hi;
        COMMIT;
        lo := hi;
    END LOOP;
END $$;
```

**6. ใช้ `run_migration.sh`**
```bash
PGDATABASE=gridcare /opt/gridcare/scripts/run_migration.sh /var/tmp/migrations/m2a.sql
```

**7. ทดสอบบน Test**
```bash
# ทดสอบบน gridcare_restore ก่อน
```

### 10.3 `run_migration.sh`

```bash
PGDATABASE=gridcare /opt/gridcare/scripts/run_migration.sh /var/tmp/migrations/m2a_add_constraints.sql
```

ผลลัพธ์:
```text
[2026-11-06 10:30:12] ครั้งที่ 1/5: /var/tmp/migrations/m2a_add_constraints.sql (lock_timeout=3s)
[2026-11-06 10:30:12] สำเร็จ
```

### 10.4 `CREATE INDEX CONCURRENTLY`

```sql
CREATE INDEX CONCURRENTLY IF NOT EXISTS outage_events_office_started_idx
  ON outage_events (office_id, started_at);
```

> ⚠️ ต้องอยู่นอก Transaction

### 10.5 `NOT VALID` + `VALIDATE`

```sql
ALTER TABLE bills ADD CONSTRAINT bills_total_nonnegative CHECK (total_amount >= 0) NOT VALID;
ALTER TABLE bills VALIDATE CONSTRAINT bills_total_nonnegative;
```

### 10.6 ตารางเลือกวิธี

| งาน | วิธี |
|---|---|
| เพิ่ม Index | `CREATE INDEX CONCURRENTLY` |
| เพิ่ม Constraint | `NOT VALID` + `VALIDATE` |
| เพิ่ม Column NULL | `ADD COLUMN` |
| เพิ่ม Column NOT NULL DEFAULT | `ADD COLUMN ... DEFAULT` (รุ่น 11+) |
| เพิ่ม FK | `NOT VALID` + Index + `VALIDATE` |
| เปลี่ยน Type | Column ใหม่ + Trigger + Backfill + Swap |
| เปลี่ยน PK int→bigint | Column ใหม่ + Trigger + Backfill + Swap |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: เพิ่ม Column

```sql
SET lock_timeout = '3s';
ALTER TABLE gridcare.bills ADD COLUMN reminder_count smallint NOT NULL DEFAULT 0;
```

ผลลัพธ์:
```text
SET
ALTER TABLE
```

> ✅ รุ่น 11+ ไม่ Scan ทั้งตาราง

### ตัวอย่างที่ 2: เพิ่ม Constraint

```sql
SET lock_timeout = '3s';
ALTER TABLE bills ADD CONSTRAINT bills_total_nonnegative CHECK (total_amount >= 0) NOT VALID;
ALTER TABLE bills VALIDATE CONSTRAINT bills_total_nonnegative;
```

### ตัวอย่างที่ 3: เพิ่ม FK

```sql
SET lock_timeout = '3s';
ALTER TABLE sms_notifications ADD CONSTRAINT sms_notifications_bill_fk
    FOREIGN KEY (bill_id) REFERENCES bills (bill_id) NOT VALID;
CREATE INDEX CONCURRENTLY sms_notifications_bill_idx ON sms_notifications (bill_id);
ALTER TABLE sms_notifications VALIDATE CONSTRAINT sms_notifications_bill_fk;
```

### ตัวอย่างที่ 4: Backfill

```sql
DO $$
DECLARE
    lo int := 0;
    hi int;
    max_id int;
BEGIN
    SELECT max(customer_id) INTO max_id FROM customers;
    WHILE lo <= max_id LOOP
        hi := lo + 20000;
        UPDATE customers SET phone_e164 = '+66' || replace(substr(phone, 2), '-', '')
        WHERE customer_id >= lo AND customer_id < hi AND phone_e164 IS NULL;
        COMMIT;
        lo := hi;
    END LOOP;
END $$;
```

### ตัวอย่างที่ 5: `run_migration.sh`

```bash
sudo -u postgres PGDATABASE=gridcare /opt/gridcare/scripts/run_migration.sh /var/tmp/migrations/m2a_add_constraints.sql
```

## 12. สรุปย่อ จำง่าย
- **Lock แรงให้สั้นที่สุด**  
- **`lock_timeout` ทุกครั้ง**  
- **`CONCURRENTLY` สำหรับ Index**  
- **`NOT VALID` + `VALIDATE` สำหรับ Constraint**  
- **Backfill เป็นช่วง**  
- **`run_migration.sh`**  
- **ทดสอบบน Test**

ประโยคจำ: **"Migration ที่ดีคือ Migration ที่ไม่ทำให้ระบบหยุด"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — ALTER TABLE: https://www.postgresql.org/docs/17/sql-altertable.html
- PostgreSQL Documentation — CREATE INDEX: https://www.postgresql.org/docs/17/sql-createindex.html
- GridCare Workshop Day 5: Lab 2.1, Lab 2.2

---

# บทที่ 87 CREATE INDEX CONCURRENTLY

## 1. เรื่อง
`CREATE INDEX CONCURRENTLY` สำหรับสร้าง Index โดยไม่บล็อกการเขียน

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจ `CONCURRENTLY`  
2. เพื่อให้สร้าง Index แบบไม่บล็อก  
3. เพื่อให้จัดการ Index ที่ล้ม  
4. เพื่อให้ตรวจสอบ `indisvalid`

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- รัน `CREATE INDEX CONCURRENTLY`  
- ตรวจสอบ `indisvalid`  
- ใช้ `DROP INDEX CONCURRENTLY`  
- จัดการ Index ที่ค้าง

## 4. เนื้อหาโดยย่อ
`CREATE INDEX CONCURRENTLY` สร้าง Index โดย:
1. สร้าง Index ชั่วคราว  
2. รอ Transaction เก่า  
3. สร้าง Index จริง  
4. สลับ

ข้อดี: ไม่บล็อกการเขียน  
ข้อจำกัด: ต้องอยู่นอก Transaction, ใช้เวลานานกว่า

## 5. ประโยชน์ที่ได้รับ
- ไม่บล็อกการเขียน  
- ลด Downtime  
- รองรับ Production

## 6. ข้อควรระวัง
- **ต้องอยู่นอก Transaction**  
- **ใช้เวลานานกว่า**  
- **ถ้าล้มต้อง `DROP INDEX CONCURRENTLY`**  
- **ตรวจ `indisvalid = t`**  
- **Unique Index อาจล้มถ้ามีข้อมูลซ้ำ**

## 7. ข้อดี
- ไม่บล็อกการเขียน  
- ลด Downtime  
- รองรับ Production

## 8. ข้อเสีย
- ใช้เวลานาน  
- ถ้าล้มต้อง Drop  
- Unique อาจล้ม

## 9. ข้อห้าม
- ห้าม `CONCURRENTLY` ใน Transaction  
- ห้ามลืมตรวจ `indisvalid`  
- ห้าม `DROP INDEX` (ไม่ `CONCURRENTLY`) บน Production  
- ห้ามสร้าง Unique ถ้ามีข้อมูลซ้ำ

## 10. รายละเอียด

### 10.1 สร้าง Index

```sql
CREATE INDEX CONCURRENTLY IF NOT EXISTS work_orders_customer_idx
  ON gridcare.work_orders (customer_id);
```

ผลลัพธ์:
```text
CREATE INDEX
```

### 10.2 ตรวจสอบ `indisvalid`

```sql
SELECT c.relname, i.indisvalid, i.indisready
FROM pg_index AS i
JOIN pg_class AS c ON c.oid = i.indexrelid
WHERE c.relname = 'work_orders_customer_idx';
```

ผลลัพธ์:
```text
         relname           | indisvalid | indisready 
---------------------------+------------+------------
 work_orders_customer_idx  | t          | t
```

### 10.3 Unique Index ที่ล้ม

```sql
CREATE UNIQUE INDEX CONCURRENTLY customers_phone_key ON gridcare.customers (phone);
```

ผลลัพธ์:
```text
ERROR:  could not create unique index "customers_phone_key"
DETAIL:  Key (phone)=(086xxxxxxx) is duplicated.
```

### 10.4 ตรวจสอบ Index ที่ค้าง

```sql
SELECT c.relname, i.indisvalid, i.indisready
FROM pg_index AS i
JOIN pg_class AS c ON c.oid = i.indexrelid
WHERE c.relname = 'customers_phone_key';
```

ผลลัพธ์:
```text
         relname          | indisvalid | indisready 
--------------------------+------------+------------
 customers_phone_key      | f          | f
```

### 10.5 ลบ Index ที่ค้าง

```sql
DROP INDEX CONCURRENTLY IF EXISTS gridcare.customers_phone_key;
```

ผลลัพธ์:
```text
DROP INDEX
```

### 10.6 ตรวจสอบ Index ที่ Invalid

```sql
SELECT c.relname AS index_name, i.indisvalid
FROM pg_index AS i
JOIN pg_class AS c ON c.oid = i.indexrelid
WHERE NOT i.indisvalid;
```

ผลลัพธ์:
```text
 index_name | indisvalid 
------------+------------
(0 rows)
```

### 10.7 เปรียบเทียบ

| วิธี | Lock | ใช้เวลา | ต้องอยู่นอก Transaction |
|---|---|---|---|
| `CREATE INDEX` | ShareLock | เร็ว | ❌ |
| `CREATE INDEX CONCURRENTLY` | ShareUpdateExclusiveLock | ช้ากว่า | ✅ |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: สร้าง Index

```sql
CREATE INDEX CONCURRENTLY IF NOT EXISTS outage_events_office_started_idx
  ON gridcare.outage_events (office_id, started_at);
SELECT indexrelid::regclass, indisvalid
FROM pg_index
WHERE indexrelid = 'outage_events_office_started_idx'::regclass;
```

ผลลัพธ์:
```text
             indexrelid             | indisvalid 
------------------------------------+------------
 outage_events_office_started_idx   | t
```

### ตัวอย่างที่ 2: Unique ที่ล้ม

```sql
CREATE UNIQUE INDEX CONCURRENTLY customers_phone_key ON gridcare.customers (phone);
```

ผลลัพธ์:
```text
ERROR:  could not create unique index "customers_phone_key"
DETAIL:  Key (phone)=(086xxxxxxx) is duplicated.
```

### ตัวอย่างที่ 3: Drop Index ที่ค้าง

```sql
DROP INDEX CONCURRENTLY IF EXISTS gridcare.customers_phone_key;
```

### ตัวอย่างที่ 4: ตรวจสอบ Index ที่ Invalid

```sql
SELECT c.relname AS index_name, i.indisvalid
FROM pg_index AS i
JOIN pg_class AS c ON c.oid = i.indexrelid
WHERE NOT i.indisvalid;
```

### ตัวอย่างที่ 5: นับ Index ที่ Invalid

```sql
SELECT count(*) AS invalid_indexes FROM pg_index WHERE NOT indisvalid;
```

ผลลัพธ์:
```text
 invalid_indexes 
-----------------
               0
```

## 12. สรุปย่อ จำง่าย
- **`CONCURRENTLY` = ไม่บล็อกการเขียน**  
- **ต้องอยู่นอก Transaction**  
- **ช้ากว่า แต่ปลอดภัยกว่า**  
- **ตรวจ `indisvalid`**  
- **ถ้าล้ม Drop ด้วย `CONCURRENTLY`**  
- **Unique อาจล้มถ้ามีข้อมูลซ้ำ**

ประโยคจำ: **"`CREATE INDEX CONCURRENTLY` ที่ดีคือ Index ที่ `indisvalid = t`"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — CREATE INDEX: https://www.postgresql.org/docs/17/sql-createindex.html
- GridCare Workshop Day 5: Lab 2.1

---

# บทที่ 88 NOT VALID และ VALIDATE CONSTRAINT

## 1. เรื่อง
การเพิ่ม Constraint บนตารางขนาดใหญ่ด้วย `NOT VALID` และ `VALIDATE CONSTRAINT`

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจ `NOT VALID`  
2. เพื่อให้เพิ่ม Constraint โดยไม่บล็อก  
3. เพื่อให้ `VALIDATE` แบบไม่บล็อก  
4. เพื่อให้ตรวจสอบ `convalidated`

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- เพิ่ม CHECK แบบ `NOT VALID`  
- เพิ่ม FK แบบ `NOT VALID`  
- `VALIDATE` Constraint  
- ตรวจสอบ `convalidated`

## 4. เนื้อหาโดยย่อ
`NOT VALID` ทำให้ Constraint บังคับกับแถวใหม่เท่านั้น  
`VALIDATE CONSTRAINT` ตรวจแถวเก่าโดยใช้ `ShareUpdateExclusiveLock`  
ข้อดี: ไม่ต้อง Scan ทั้งตารางตอนเพิ่ม Constraint

## 5. ประโยชน์ที่ได้รับ
- ไม่บล็อกการเขียน  
- ลด Downtime  
- รองรับ Production  
- ผ่าน Audit

## 6. ข้อควรระวัง
- **`NOT VALID` ไม่ได้ตรวจแถวเก่า**  
- **`VALIDATE` ต้องรันแยก**  
- **FK ต้องมี Index ฝั่งลูกก่อน `VALIDATE`**  
- **`VALIDATE` ใช้ `ShareUpdateExclusiveLock`**  
- **ต้องตรวจ `convalidated`**

## 7. ข้อดี
- ไม่บล็อก  
- ลด Downtime  
- รองรับ Production

## 8. ข้อเสีย
- ต้องทำ 2 ขั้น  
- ต้องตรวจ `convalidated`

## 9. ข้อห้าม
- ห้าม `ADD CONSTRAINT` แบบปกติบนตารางใหญ่  
- ห้าม `VALIDATE` โดยไม่มี Index ฝั่งลูก  
- ห้ามลืม `VALIDATE`  
- ห้ามลบ `NOT VALID` ก่อน `VALIDATE`

## 10. รายละเอียด

### 10.1 CHECK NOT VALID

```sql
ALTER TABLE bills ADD CONSTRAINT bills_total_nonnegative CHECK (total_amount >= 0) NOT VALID;
ALTER TABLE bills VALIDATE CONSTRAINT bills_total_nonnegative;
```

### 10.2 FK NOT VALID

```sql
ALTER TABLE sms_notifications ADD CONSTRAINT sms_notifications_bill_fk
    FOREIGN KEY (bill_id) REFERENCES bills (bill_id) NOT VALID;

CREATE INDEX CONCURRENTLY sms_notifications_bill_idx ON sms_notifications (bill_id);

ALTER TABLE sms_notifications VALIDATE CONSTRAINT sms_notifications_bill_fk;
```

### 10.3 ตรวจสอบ `convalidated`

```sql
SELECT conrelid::regclass AS table_name, conname, convalidated
FROM pg_constraint
WHERE conname IN ('bills_total_nonnegative', 'sms_notifications_bill_fk');
```

ผลลัพธ์:
```text
         table_name         |          conname          | convalidated 
----------------------------+---------------------------+--------------
 gridcare.bills             | bills_total_nonnegative   | t
 gridcare.sms_notifications | sms_notifications_bill_fk | t
```

### 10.4 ขั้นตอน

1. `ADD CONSTRAINT ... NOT VALID` — Lock สั้น  
2. สร้าง Index (ถ้า FK) — `CONCURRENTLY`  
3. `VALIDATE CONSTRAINT` — Lock ปานกลาง  
4. ตรวจ `convalidated = t`

### 10.5 ตาราง Constraint

| ประเภท | `NOT VALID` | `VALIDATE` |
|---|---|---|
| CHECK | ✅ | ✅ |
| FK | ✅ | ✅ |
| UNIQUE | ❌ | ❌ |
| PRIMARY KEY | ❌ | ❌ |
| EXCLUDE | ❌ | ❌ |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: CHECK NOT VALID

```sql
ALTER TABLE gridcare.bills ADD CONSTRAINT bills_total_nonnegative CHECK (total_amount >= 0) NOT VALID;
ALTER TABLE gridcare.bills VALIDATE CONSTRAINT bills_total_nonnegative;
```

### ตัวอย่างที่ 2: FK NOT VALID

```sql
ALTER TABLE gridcare.sms_notifications ADD CONSTRAINT sms_notifications_bill_fk
    FOREIGN KEY (bill_id) REFERENCES gridcare.bills (bill_id) NOT VALID;
CREATE INDEX CONCURRENTLY sms_notifications_bill_idx ON gridcare.sms_notifications (bill_id);
ALTER TABLE gridcare.sms_notifications VALIDATE CONSTRAINT sms_notifications_bill_fk;
```

### ตัวอย่างที่ 3: ตรวจสอบ

```sql
SELECT conrelid::regclass AS table_name, conname, convalidated
FROM pg_constraint
WHERE conname IN ('bills_total_nonnegative', 'sms_notifications_bill_fk');
```

ผลลัพธ์:
```text
         table_name         |          conname          | convalidated 
----------------------------+---------------------------+--------------
 gridcare.bills             | bills_total_nonnegative   | t
 gridcare.sms_notifications | sms_notifications_bill_fk | t
```

### ตัวอย่างที่ 4: ตรวจสอบ Index ฝั่งลูก

```sql
SELECT indexrelid::regclass, indisvalid
FROM pg_index
WHERE indrelid = 'gridcare.sms_notifications'::regclass;
```

ผลลัพธ์:
```text
           indexrelid            | indisvalid 
---------------------------------+------------
 sms_notifications_pkey          | t
 sms_notifications_bill_idx      | t
```

### ตัวอย่างที่ 5: `\d`

```sql
\d gridcare.bills
```

ผลลัพธ์:
```text
Check constraints:
    "bills_total_nonnegative" CHECK (total_amount >= 0.00)
```

## 12. สรุปย่อ จำง่าย
- **`NOT VALID` = บังคับแถวใหม่**  
- **`VALIDATE` = ตรวจแถวเก่า**  
- **FK ต้องมี Index ฝั่งลูกก่อน `VALIDATE`**  
- **`VALIDATE` ใช้ `ShareUpdateExclusiveLock`**  
- **ตรวจ `convalidated = t`**  
- **ทำ 2 ขั้นเสมอ**

ประโยคจำ: **"`NOT VALID` + `VALIDATE` = Constraint ที่ไม่บล็อกระบบ"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — ALTER TABLE: https://www.postgresql.org/docs/17/sql-altertable.html
- GridCare Workshop Day 5: Lab 2.2

---

# บทที่ 89 Backfill และ PK Swap

## 1. เรื่อง
การ Backfill ข้อมูลเป็นช่วง และการสลับ PK จาก `integer` เป็น `bigint` โดยไม่บล็อก

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้ Backfill ข้อมูลเป็นช่วง  
2. เพื่อให้สลับ PK จาก int → bigint  
3. เพื่อให้ใช้ Trigger Sync  
4. เพื่อให้ Swap โดยไม่บล็อกนาน

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- Backfill เป็นช่วง  
- ใช้ Trigger Sync  
- สร้าง Unique Index  
- Swap PK ใน Transaction สั้น  
- ตรวจสอบผล

## 4. เนื้อหาโดยย่อ
การสลับ PK int → bigint ต้องทำ 5 ขั้น:
1. เพิ่มคอลัมน์ใหม่ (bigint)  
2. สร้าง Trigger Sync  
3. Backfill เป็นช่วง  
4. สร้าง Unique Index  
5. Swap ใน Transaction สั้น

## 5. ประโยชน์ที่ได้รับ
- ไม่บล็อกระบบ  
- ลด Downtime  
- รองรับข้อมูลขนาดใหญ่  
- ผ่าน Audit

## 6. ข้อควรระวัง
- **Trigger ต้อง Sync คอลัมน์ใหม่**  
- **Backfill ต้องเป็นช่วง**  
- **Unique Index ต้องตรวจก่อน Swap**  
- **Swap ต้อง Lock สั้น**  
- **Sequence ต้องตั้ง `setval`**

## 7. ข้อดี
- ไม่บล็อก  
- รองรับข้อมูลใหญ่  
- ลด Downtime

## 8. ข้อเสีย
- ต้องทำหลายขั้น  
- ต้องมี Disk เพิ่ม  
- ต้องทดสอบ

## 9. ข้อห้าม
- ห้าม Swap โดยไม่ Backfill  
- ห้าม Swap โดยไม่มี Unique Index  
- ห้าม Swap โดยไม่มี `LOCK TABLE ... ACCESS EXCLUSIVE`  
- ห้ามลืม `setval`  
- ห้ามลืม Drop Trigger

## 10. รายละเอียด

### 10.1 ขั้น a: เพิ่มคอลัมน์ + Trigger

```sql
ALTER TABLE sms_notifications ADD COLUMN notification_id_new bigint;

CREATE OR REPLACE FUNCTION sms_notifications_id_sync() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.notification_id_new := NEW.notification_id;
    RETURN NEW;
END $$;

CREATE TRIGGER sms_notifications_id_sync BEFORE INSERT OR UPDATE ON sms_notifications
    FOR EACH ROW EXECUTE FUNCTION sms_notifications_id_sync();
```

### 10.2 ขั้น b: Backfill

```sql
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
```

ผลลัพธ์:
```text
NOTICE:  id 1 ขึ้นไป: 50000 แถว
NOTICE:  id 50001 ขึ้นไป: 50000 แถว
...
NOTICE:  id 150001 ขึ้นไป: 50000 แถว
```

### 10.3 ขั้น c: Unique Index + CHECK NOT NULL

```sql
SET lock_timeout = '3s';
CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS sms_notifications_id_new_key ON sms_notifications (notification_id_new);
ALTER TABLE sms_notifications ADD CONSTRAINT sms_notifications_id_new_nn CHECK (notification_id_new IS NOT NULL) NOT VALID;
ALTER TABLE sms_notifications VALIDATE CONSTRAINT sms_notifications_id_new_nn;
```

### 10.4 ขั้น d: Swap

```sql
SET lock_timeout = '3s';
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

ผลลัพธ์:
```text
[2026-11-06 11:09:11] ครั้งที่ 1/5: m3d_swap.sql (lock_timeout=3s)
[2026-11-06 11:09:11] สำเร็จ
```

> ✅ Swap ใช้ 0.13 วินาที

### 10.5 ตรวจสอบ

```sql
SELECT a.attname, format_type(a.atttypid, a.atttypmod) AS type
FROM pg_attribute AS a
WHERE a.attrelid = 'gridcare.sms_notifications'::regclass AND a.attnum > 0 AND NOT a.attisdropped;
```

ผลลัพธ์:
```text
      attname      |        type         
-------------------+---------------------
 notification_id   | bigint
 notification_id_old| integer
 customer_id       | integer
```

### 10.6 ตรวจสอบ Sequence

```sql
SELECT sequencename, data_type, last_value FROM pg_sequences WHERE sequencename LIKE 'sms_notifications%';
```

ผลลัพธ์:
```text
            sequencename              | data_type | last_value 
--------------------------------------+-----------+------------
 sms_notifications_notification_id_seq | bigint    |    1664422
```

### 10.7 ทดสอบ INSERT ID ใหญ่

```sql
BEGIN;
INSERT INTO gridcare.sms_notifications (notification_id, customer_id, message_type, sent_at, status)
VALUES (2147483648, 1, 'PAYMENT_DUE', now(), 'QUEUED') RETURNING notification_id;
ROLLBACK;
```

ผลลัพธ์:
```text
 notification_id 
-----------------
      2147483648
```

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: ตรวจ Sequence ก่อนเริ่ม

```sql
SELECT s.sequencename, s.data_type, s.last_value, s.max_value,
       round(100.0 * s.last_value / s.max_value, 3) AS used_pct
FROM pg_sequences AS s
WHERE s.schemaname = 'gridcare'
ORDER BY used_pct DESC NULLS LAST;
```

ผลลัพธ์:
```text
         sequencename          | data_type | last_value |  max_value  | used_pct
-------------------------------+-----------+------------+-------------+----------
 sms_notifications_notification_id_seq | integer   |   1664422 |  2147483647 |   99.920
```

### ตัวอย่างที่ 2: เพิ่มคอลัมน์ + Trigger

```sql
ALTER TABLE sms_notifications ADD COLUMN notification_id_new bigint;

CREATE OR REPLACE FUNCTION sms_notifications_id_sync() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.notification_id_new := NEW.notification_id;
    RETURN NEW;
END $$;

CREATE TRIGGER sms_notifications_id_sync BEFORE INSERT OR UPDATE ON sms_notifications
    FOR EACH ROW EXECUTE FUNCTION sms_notifications_id_sync();
```

### ตัวอย่างที่ 3: Backfill

```sql
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
```

### ตัวอย่างที่ 4: Swap

```sql
SET lock_timeout = '3s';
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

### ตัวอย่างที่ 5: ทดสอบ

```sql
BEGIN;
INSERT INTO gridcare.sms_notifications (notification_id, customer_id, message_type, sent_at, status)
VALUES (2147483648, 1, 'PAYMENT_DUE', now(), 'QUEUED') RETURNING notification_id;
ROLLBACK;
```

ผลลัพธ์:
```text
 notification_id 
-----------------
      2147483648
```

## 12. สรุปย่อ จำง่าย
- **Backfill เป็นช่วง**  
- **Trigger Sync คอลัมน์ใหม่**  
- **Unique Index ก่อน Swap**  
- **Swap ใน Transaction สั้น**  
- **`setval` หลัง ADD IDENTITY**  
- **ทดสอบ INSERT ID ใหญ่**

ประโยคจำ: **"PK Swap ที่ดีคือ Swap ที่ใช้เวลาไม่ถึงวินาที"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — ALTER TABLE: https://www.postgresql.org/docs/17/sql-altertable.html
- GridCare Workshop Day 5: Lab 2.3

---

# บทที่ 90 Checklist Zero-Downtime Migration

## 1. เรื่อง
Checklist สำหรับการทำ Zero-Downtime Migration บน PostgreSQL Production

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้มี Checklist มาตรฐาน  
2. เพื่อให้ลดความเสี่ยง  
3. เพื่อให้ผ่าน Audit  
4. เพื่อให้ On-call ทำงานได้

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ใช้ Checklist ก่อน Migration  
- ใช้ Checklist ระหว่าง Migration  
- ใช้ Checklist หลัง Migration  
- สร้าง Evidence

## 4. เนื้อหาโดยย่อ
Checklist แบ่งเป็น 4 ระยะ:
1. ก่อน Migration  
2. ระหว่าง Migration  
3. หลัง Migration  
4. หลัง 24 ชั่วโมง

## 5. ประโยชน์ที่ได้รับ
- ลดความเสี่ยง  
- ผ่าน Audit  
- On-call ทำงานได้  
- มี Evidence

## 6. ข้อควรระวัง
- **Checklist ที่ไม่มี Evidence ไม่มีคุณค่า**  
- **Checklist ที่ไม่ Reviewed จะเก่า**  
- **Checklist ที่ยาวเกินไปจะไม่มีคนทำ**

## 7. ข้อดี
- มาตรฐาน  
- ลดความเสี่ยง  
- Audit ผ่าน

## 8. ข้อเสีย
- ต้อง Maintain  
- ต้อง Review

## 9. ข้อห้าม
- ห้าม Skip Checklist บน Production  
- ห้ามใช้ Checklist ที่ไม่มีวันที่  
- ห้ามใช้ Checklist ที่ไม่มีผู้อนุมัติ

## 10. รายละเอียด

### 10.1 Checklist ก่อน Migration

| # | รายการ | เกณฑ์ผ่าน |
|---|---|---|
| 1 | Backup ล่าสุด | มี + Restore Test ผ่าน |
| 2 | Test Environment | ทดสอบผ่าน |
| 3 | `lock_timeout` | ตั้งใน Script |
| 4 | `CONCURRENTLY` | ใช้กับ Index |
| 5 | `NOT VALID` | ใช้กับ Constraint |
| 6 | Backfill Script | แบ่งช่วง |
| 7 | Monitoring | เปิด |
| 8 | Alert | ตั้ง |
| 9 | Rollback Plan | มี |
| 10 | ผู้อนุมัติ | มี |

### 10.2 Checklist ระหว่าง Migration

| # | รายการ | เกณฑ์ผ่าน |
|---|---|---|
| 1 | Lock Wait | ไม่มี |
| 2 | `pg_stat_activity` | ไม่มี Long Transaction |
| 3 | Error Rate | ปกติ |
| 4 | TPS | ปกติ |
| 5 | Latency | ปกติ |
| 6 | `indisvalid` | t |

### 10.3 Checklist หลัง Migration

| # | รายการ | เกณฑ์ผ่าน |
|---|---|---|
| 1 | Index `indisvalid` | t |
| 2 | Constraint `convalidated` | t |
| 3 | `pg_stat_user_tables` | ปกติ |
| 4 | Query Plan | ใช้ Index |
| 5 | Alert | ไม่มี Firing |
| 6 | Log | ไม่มี Error |
| 7 | Backup ใหม่ | มี |

### 10.4 Checklist หลัง 24 ชั่วโมง

| # | รายการ | เกณฑ์ผ่าน |
|---|---|---|
| 1 | Performance | ปกติ |
| 2 | Bloat | ไม่เพิ่ม |
| 3 | XID Age | ปกติ |
| 4 | Replication Lag | 0 |
| 5 | Backup | Success |

### 10.5 Template Migration Report

```text
Migration Report
Date       : 2026-11-06
Migration  : m2a_add_constraints.sql
Operator   : DBA A
Approver   : DBA Lead

Before:
- Backup: 20261106-110000F
- Test: PASS
- Rollback Plan: DROP CONSTRAINT / DROP INDEX

During:
- Lock Wait: 0
- Error Rate: 0
- TPS: 149 → 148

After:
- bills_total_nonnegative: convalidated=t
- sms_notifications_bill_fk: convalidated=t
- sms_notifications_bill_idx: indisvalid=t
- Alert: 0 Firing
- Log: 0 Error

After 24h:
- Performance: ปกติ
- Bloat: ไม่เพิ่ม
- XID Age: ปกติ
- Replication Lag: 0
- Backup: 20261107-020000F

Conclusion: PASS
```

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: ตรวจก่อน Migration

```bash
# Backup ล่าสุด
sudo -u postgres pgbackrest --stanza=gridcare info | grep -E "full backup" | tail -1

# Test
sudo -u postgres MODE=pgbackrest STANZA=gridcare ./restore_test.sh

# Lock
# (ตรวจใน Script)
```

### ตัวอย่างที่ 2: ระหว่าง Migration

```sql
SELECT pid, state, wait_event_type, pg_blocking_pids(pid), left(query, 60)
FROM pg_stat_activity
WHERE datname = 'gridcare' AND state <> 'idle';
```

### ตัวอย่างที่ 3: หลัง Migration

```sql
SELECT conrelid::regclass AS table_name, conname, convalidated
FROM pg_constraint
WHERE conname IN ('bills_total_nonnegative', 'sms_notifications_bill_fk');

SELECT indexrelid::regclass, indisvalid
FROM pg_index
WHERE indrelid = 'gridcare.sms_notifications'::regclass;
```

### ตัวอย่างที่ 4: ตรวจ Alert

```bash
curl -s localhost:9090/api/v1/alerts | python3 -m json.tool | grep -E '"alertname"|"state"'
```

### ตัวอย่างที่ 5: ตรวจ Performance

```sql
SELECT calls, round(mean_exec_time::numeric, 3) AS mean_ms, left(query, 60)
FROM pg_stat_statements
WHERE query LIKE '%ca_number%' ORDER BY calls DESC LIMIT 3;
```

## 12. สรุปย่อ จำง่าย
- **Checklist 4 ระยะ: ก่อน / ระหว่าง / หลัง / 24 ชั่วโมง**  
- **ทุกข้อต้องมี Evidence**  
- **ทุกข้อต้องมีผู้อนุมัติ**  
- **ทุก Migration ต้องมี Report**  
- **Rollback Plan ต้องมี**  
- **Full Backup หลัง Migration**

ประโยคจำ: **"Zero-Downtime Migration ที่ดีคือ Migration ที่มี Checklist และ Report"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — ALTER TABLE: https://www.postgresql.org/docs/17/sql-altertable.html
- Google SRE Book — Release Engineering: https://sre.google/sre-book/release-engineering/
- GridCare Workshop Day 5: Lab 2.1, Lab 2.2, Lab 2.3

---

## สรุปส่วนที่ 9 (บทที่ 81–90)

| บท | แก่นของบท | ใช้ต่อในส่วน |
|---|---|---|
| 81 | นโยบายเวอร์ชัน | Upgrade |
| 82 | `pg_upgrade --check` | Upgrade |
| 83 | `pg_upgrade --link` | Upgrade |
| 84 | Upgrade Patroni | Upgrade |
| 85 | Extension + Statistics | Upgrade |
| 86 | Safe Migration | Migration |
| 87 | `CREATE INDEX CONCURRENTLY` | Migration |
| 88 | `NOT VALID` + `VALIDATE` | Migration |
| 89 | Backfill + PK Swap | Migration |
| 90 | Checklist Zero-Downtime | Migration |

---