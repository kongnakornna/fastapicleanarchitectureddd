# บทที่ 11–20

> หนังสือ: คู่มือการใช้งาน PostgreSQL สำหรับ DevOps Engineer, Cloud Engineer และ DBA  
> ส่วนที่ 2 ติดตั้งและตั้งค่าพื้นฐาน  
> โทน: ทางการ กระชับ เน้นใช้งานจริง

---

# บทที่ 11 เตรียม Linux สำหรับ PostgreSQL

## 1. เรื่อง
การเตรียมระบบ Linux ให้พร้อมสำหรับ PostgreSQL Production ครอบคลุม Kernel Parameter, ulimit, Timezone, Filesystem และบริการพื้นฐาน

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้ระบบ Linux พร้อมรับ PostgreSQL ตั้งแต่แรก  
2. เพื่อลดปัญหาที่เกิดจาก Kernel, ulimit และ Filesystem  
3. เพื่อให้ทีม Cloud และ DevOps ตั้ง Baseline ที่ตรงกัน  
4. เพื่อให้ทุกเครื่องใน Cluster มีมาตรฐานเดียวกัน

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ตรวจสอบและตั้งค่า Kernel Parameter ที่จำเป็น  
- ตั้งค่า ulimit ของผู้ใช้ postgres ให้เพียงพอ  
- ตั้ง Timezone และ NTP ให้ถูกต้อง  
- เลือก Filesystem และ Mount Options ที่เหมาะสม  
- ปิด Transparent Huge Pages และ Swap ที่ไม่เหมาะสม

## 4. เนื้อหาโดยย่อ
Linux Baseline สำหรับ PostgreSQL ประกอบด้วย 7 ส่วน:
1. OS และ Kernel Version ที่รองรับ  
2. Kernel Parameter (`sysctl`)  
3. Resource Limit (`ulimit`)  
4. Timezone และ NTP  
5. Filesystem และ Mount Option  
6. Transparent Huge Pages และ Swap  
7. Firewall และ SSH

## 5. ประโยชน์ที่ได้รับ
- ลดปัญหา Connection มากเกินไปจาก `max_files` ไม่พอ  
- ลดปัญหา Memory Lock จาก Huge Pages  
- ลดปัญหา Time Skew ที่ทำให้ Replication และ Log สับสน  
- ลดปัญหา Filesystem ที่ไม่รองรับ fsync  
- ทำให้เครื่องใน Cluster มีพฤติกรรมเหมือนกัน

## 6. ข้อควรระวัง
- **`ulimit -n` ต่ำเกินไป** ทำให้ `max_connections` ตั้งได้ไม่ถึงที่ต้องการ  
- **Transparent Huge Pages เปิดอยู่** ทำให้เกิด Latency Spike  
- **Timezone ไม่ตรงกัน** ทำให้ Log และ PITR คลาดเคลื่อน  
- **Filesystem ไม่รองรับ fsync** เช่นบาง NFS ทำให้ข้อมูลเสียหายได้  
- **Swap บน Database Server** อาจทำให้ Query ช้าอย่างรุนแรง

## 7. ข้อดี
- Baseline ถูกต้องช่วยลด Incident ที่ไม่คาดคิด  
- ทำให้ Benchmark มีความหมาย  
- ทำให้ Performance คาดการณ์ได้  
- ทำให้ Cluster มีมาตรฐานเดียวกัน

## 8. ข้อเสีย
- ต้องทำทุกเครื่องให้เหมือนกัน  
- Kernel Parameter บางตัวต้อง Reboot  
- Transparent Huge Pages ต้องตั้งทุก Boot

## 9. ข้อห้าม
- ห้ามตั้ง `vm.overcommit_memory = 1` โดยไม่เข้าใจผล  
- ห้ามใช้ NFS ที่ไม่รองรับ fsync เป็น PGDATA  
- ห้ามใช้ `swappiness` สูงบน Database Server  
- ห้ามเปิด Transparent Huge Pages แบบ `always`  
- ห้ามใช้ Timezone ที่ไม่ตรงกับ Business

## 10. รายละเอียด

### 10.1 ตรวจสอบ OS และ Kernel

```bash
cat /etc/os-release
uname -r
lsb_release -a
```

ผลลัพธ์ (ตัวอย่าง):
```text
Ubuntu 24.04 LTS
6.8.0-45-generic
Distributor ID: Ubuntu
Description:    Ubuntu 24.04 LTS
```

### 10.2 Kernel Parameter (sysctl)

ไฟล์ `/etc/sysctl.d/99-postgresql.conf`:

```ini
# Memory
vm.swappiness = 10
vm.overcommit_memory = 2
vm.overcommit_ratio = 80
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5

# Network
net.core.somaxconn = 4096
net.ipv4.tcp_max_syn_backlog = 4096
net.ipv4.ip_local_port_range = 10000 65000
net.ipv4.tcp_keepalive_time = 300
net.ipv4.tcp_keepalive_intvl = 30
net.ipv4.tcp_keepalive_probes = 5
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216

# File
fs.file-max = 200000
fs.aio-max-nr = 1048576

# THP (ปิด)
kernel.numa_balancing = 0
```

ใช้งาน:
```bash
sudo sysctl --system
sysctl vm.swappiness net.core.somaxconn fs.file-max
```

ผลลัพธ์:
```text
vm.swappiness = 10
net.core.somaxconn = 4096
fs.file-max = 200000
```

### 10.3 Resource Limit (ulimit)

ไฟล์ `/etc/security/limits.d/99-postgresql.conf`:

```ini
postgres soft nofile 65536
postgres hard nofile 65536
postgres soft nproc  16384
postgres hard nproc  16384
postgres soft memlock unlimited
postgres hard memlock unlimited
```

ตรวจสอบ:
```bash
sudo -u postgres bash -c 'ulimit -n; ulimit -u; ulimit -l'
```

ผลลัพธ์:
```text
65536
16384
unlimited
```

> 💡 `ulimit -n` ต้องเพียงพอต่อ `max_connections × (1 + worker)` และไฟล์ที่ PostgreSQL เปิด

### 10.4 Timezone และ NTP

```bash
sudo timedatectl set-timezone Asia/Bangkok
timedatectl
```

ผลลัพธ์:
```text
               Local time: Mon 2026-11-02 09:00:00 +07
           Universal time: Mon 2026-11-02 02:00:00 UTC
                Time zone: Asia/Bangkok (+07, +0700)
```

NTP:
```bash
sudo apt install -y chrony
sudo systemctl enable --now chrony
chronyc tracking
```

ผลลัพธ์:
```text
Reference ID    : A9FEA9FE (time.cloudflare.com)
Stratum         : 3
System time     : 0.000012345 seconds fast of NTP time
```

### 10.5 Filesystem และ Mount Options

แนะนำ:
- **XFS** หรือ **ext4** สำหรับ PGDATA
- Mount options: `noatime,nodiratime`
- หลีกเลี่ยง NFS ที่ไม่รองรับ fsync
- WAL แยก Disk ถ้าเป็นไปได้

ตรวจสอบ:
```bash
df -hT /
findmnt -no OPTIONS /
```

ผลลัพธ์:
```text
Filesystem     Type  Size  Used Avail Use% Mounted on
/dev/sda1      ext4   78G   12G   63G  16% /

rw,noatime,nodiratime
```

### 10.6 Transparent Huge Pages (THP)

ตรวจสอบ:
```bash
cat /sys/kernel/mm/transparent_hugepage/enabled
cat /sys/kernel/mm/transparent_hugepage/defrag
```

ผลลัพธ์ที่ต้องการ:
```text
always madvise [never]
always defer defer+madvise [madvise] never
```

ปิดชั่วคราว:
```bash
echo never | sudo tee /sys/kernel/mm/transparent_hugepage/enabled
```

ปิดถาวรด้วย systemd service `/etc/systemd/system/disable-thp.service`:

```ini
[Unit]
Description=Disable Transparent Huge Pages
DefaultDependencies=no
After=sysinit.target local-fs.target
Before=postgresql.service

[Service]
Type=oneshot
ExecStart=/bin/sh -c 'echo never > /sys/kernel/mm/transparent_hugepage/enabled'
ExecStart=/bin/sh -c 'echo never > /sys/kernel/mm/transparent_hugepage/defrag'

[Install]
WantedBy=basic.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable disable-thp.service
```

### 10.7 Swap

ตรวจสอบ:
```bash
free -h
swapon --show
```

ผลลัพธ์ที่ต้องการบน Database Server:
```text
               total        used        free      shared  buff/cache   available
Mem:           3.8Gi       612Mi       2.1Gi        17Mi       1.3Gi       3.0Gi
Swap:             0B          0B          0B
```

> 💡 Swap = 0 บน Database Server เป็นทางเลือกที่ยอมรับได้ ถ้ามี Memory เพียงพอ  
> ถ้าจำเป็นต้องมี Swap ให้ตั้ง `vm.swappiness = 1` หรือ `10`

### 10.8 Firewall และ SSH

```bash
sudo ufw status
sudo ufw allow ssh
sudo ufw allow from 10.104.0.0/20 to any port 5432 proto tcp
sudo ufw enable
```

> ⚠️ ต้อง `ufw allow ssh` ก่อน `ufw enable` มิฉะนั้นจะล็อกตัวเองออกจากเครื่อง

### 10.9 Checklist Linux Baseline

| # | รายการ | เกณฑ์ผ่าน |
|---|---|---|
| 1 | OS Version | Ubuntu 22.04+ / RHEL 9+ |
| 2 | Kernel | 5.15+ |
| 3 | `vm.swappiness` | ≤ 10 |
| 4 | `fs.file-max` | ≥ 200000 |
| 5 | `ulimit -n` (postgres) | ≥ 65536 |
| 6 | Timezone | Asia/Bangkok |
| 7 | NTP | chrony / systemd-timesyncd active |
| 8 | Filesystem | XFS / ext4 + noatime |
| 9 | THP | never |
| 10 | Swap | 0 หรือ swappiness ≤ 10 |
| 11 | ufw | enabled + allow ssh + allow 5432 จาก CIDR |
| 12 | Password SSH | disabled (ใช้ Public Key) |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: ตรวจสอบทุกอย่างในคำสั่งเดียว

```bash
echo "=== OS ===" && cat /etc/os-release | head -2
echo "=== Kernel ===" && uname -r
echo "=== Sysctl ===" && sysctl vm.swappiness net.core.somaxconn fs.file-max
echo "=== ulimit ===" && sudo -u postgres bash -c 'ulimit -n; ulimit -u'
echo "=== Timezone ===" && timedatectl | grep "Time zone"
echo "=== THP ===" && cat /sys/kernel/mm/transparent_hugepage/enabled
echo "=== Disk ===" && df -hT /
echo "=== Swap ===" && free -h
```

### ตัวอย่างที่ 2: หลังตั้งค่าแล้ว ตรวจสอบว่า PostgreSQL ใช้ ulimit ที่ถูกต้อง

```bash
sudo systemctl show postgresql@17-main -p LimitNOFILE
```

ผลลัพธ์:
```text
LimitNOFILE=65536
```

### ตัวอย่างที่ 3: ตรวจสอบว่า THP ถูกปิดจริงหลัง Reboot

```bash
cat /sys/kernel/mm/transparent_hugepage/enabled
systemctl status disable-thp.service --no-pager | head -5
```

ผลลัพธ์:
```text
always madvise [never]
● disable-thp.service - Disable Transparent Huge Pages
     Active: active (exited) since Mon 2026-11-02 09:00:00 +07
```

## 12. สรุปย่อ จำง่าย
- **Kernel Parameter** ต้องตั้งก่อนติดตั้ง PostgreSQL  
- **ulimit -n ≥ 65536** สำหรับ Production  
- **Timezone = Asia/Bangkok + NTP = chrony**  
- **Filesystem XFS/ext4 + noatime**  
- **THP = never**  
- **Swap = 0 หรือ swappiness ≤ 10**  
- **ufw allow ssh ก่อน enable**

ประโยคจำ: **“Linux ไม่พร้อม PostgreSQL ก็ไม่พร้อม”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — Installation from Source / OS Setup: https://www.postgresql.org/docs/17/installation.html
- PostgreSQL Wiki — Tuning Your PostgreSQL Server: https://wiki.postgresql.org/wiki/Tuning_Your_PostgreSQL_Server
- Red Hat Enterprise Linux — Tuning Guide: https://access.redhat.com/documentation/
- Ubuntu Server Guide: https://ubuntu.com/server/docs
- GridCare Workshop Day 1: Lab 0.1, Lab 2.1

---

# บทที่ 12 ติดตั้ง PostgreSQL 17/18 อย่างปลอดภัย

## 1. เรื่อง
การติดตั้ง PostgreSQL 17 และ 18 บน Ubuntu 24.04 ด้วย PGDG Repository พร้อมแนวทางความปลอดภัยตั้งแต่เริ่ม

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้ติดตั้ง PostgreSQL ได้อย่างถูกต้องจาก Source ที่เชื่อถือได้  
2. เพื่อให้เข้าใจโครงสร้าง Package และ Cluster  
3. เพื่อให้ตั้ง Baseline Security ตั้งแต่แรก  
4. เพื่อให้พร้อมสำหรับ Upgrade และติดตั้ง Extension ในอนาคต

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- เพิ่ม PGDG Repository อย่างปลอดภัย  
- ติดตั้ง PostgreSQL 17/18 พร้อม Extension สำคัญ  
- ตรวจสอบ Cluster ด้วย `pg_lsclusters`  
- ยืนยัน Version, Data Checksums และ Service  
- ตั้ง Baseline Security เช่น SCRAM, listen_addresses, TLS

## 4. เนื้อหาโดยย่อ
ขั้นตอนการติดตั้ง 7 ขั้น:
1. เพิ่ม PGDG Repository  
2. ติดตั้ง `postgresql-common`  
3. ตั้ง `createcluster.conf` สำหรับ Data Checksums  
4. ติดตั้ง `postgresql-17` และ Extension  
5. ตรวจสอบ Cluster ด้วย `pg_lsclusters`  
6. ตั้งค่า `postgresql.conf` และ `pg_hba.conf`  
7. ตรวจสอบ Version และ Checksums

## 5. ประโยชน์ที่ได้รับ
- ได้ PostgreSQL ที่ติดตั้งจาก Source ที่เชื่อถือได้  
- ได้ Cluster ที่มี Data Checksums ตั้งแต่แรก  
- มี Baseline Security ที่พร้อม Production  
- มี Extension ที่จำเป็นต่อ Monitoring และ Security  
- พร้อมสำหรับ Upgrade และ HA ในอนาคต

## 6. ข้อควรระวัง
- **ติดตั้งจาก Repository ที่ไม่เป็นทางการ** อาจได้ Package ที่ไม่ปลอดภัย  
- **ตั้ง `initdb_options` หลังติดตั้ง** จะไม่ได้ Data Checksums  
- **เปิด `listen_addresses = '*'` โดยไม่มี Firewall** เสี่ยงถูกโจมตี  
- **ใช้ Default Port 5432 กับ Internet** เสี่ยงถูก Scan  
- **ตั้ง `password_encryption = md5`** ไม่ปลอดภัย

## 7. ข้อดี
- PGDG Repository เป็นทางการและอัปเดตสม่ำเสมอ  
- `postgresql-common` ช่วยจัดการหลาย Cluster  
- ตั้ง Checksums ก่อนติดตั้งได้  
- Extension ติดตั้งผ่าน apt ง่าย

## 8. ข้อเสีย
- PGDG Repository ต้องเพิ่มเอง ไม่มีใน Ubuntu Default  
- Package หลายรุ่นอาจทำให้สับสน  
- Default `pg_hba.conf` ไม่เหมาะ Production

## 9. ข้อห้าม
- ห้ามติดตั้งจาก Tarball ที่ไม่ตรวจสอบ Checksum  
- ห้ามใช้ `password_encryption = md5`  
- ห้ามเปิด `listen_addresses = '*'` โดยไม่มี Firewall  
- ห้ามใช้ Superuser กับแอป  
- ห้ามเปิด Public Access ที่ Port 5432

## 10. รายละเอียด

### 10.1 เพิ่ม PGDG Repository

```bash
sudo apt install -y curl ca-certificates
sudo install -d /usr/share/postgresql-common/pgdg
sudo curl -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc \
  --fail https://www.postgresql.org/media/keys/ACCC4CF8.asc
echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] \
  https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" \
  | sudo tee /etc/apt/sources.list.d/pgdg.list
sudo apt update
```

ผลลัพธ์:
```text
Get:1 https://apt.postgresql.org/pub/repos/apt noble-pgdg InRelease
Fetched ...
```

### 10.2 ติดตั้ง postgresql-common

```bash
sudo apt install -y postgresql-common
```

### 10.3 ตั้ง Data Checksums ก่อนติดตั้ง

```bash
sudo cp /etc/postgresql-common/createcluster.conf /etc/postgresql-common/createcluster.conf.bak
grep -q "^initdb_options = '--data-checksums'" /etc/postgresql-common/createcluster.conf || \
  echo "initdb_options = '--data-checksums'" | sudo tee -a /etc/postgresql-common/createcluster.conf
grep -n "^initdb_options" /etc/postgresql-common/createcluster.conf
```

ผลลัพธ์:
```text
42:initdb_options = '--data-checksums'
```

### 10.4 ติดตั้ง PostgreSQL 17 + Extension

```bash
sudo apt install -y postgresql-17 \
  postgresql-17-pgaudit \
  postgresql-17-partman \
  postgresql-17-repack \
  postgresql-client-17 \
  pgbackrest
```

ผลลัพธ์:
```text
Setting up postgresql-17 (17.11-1.pgdg24.04+2) ...
Creating new PostgreSQL cluster 17/main ...
/usr/lib/postgresql/17/bin/initdb -D /var/lib/postgresql/17/main \
  --auth-local peer --auth-host scram-sha-256 --no-instructions --data-checksums
Ver Cluster Port Status Owner    Data directory
17  main    5432 online postgres /var/lib/postgresql/17/main
```

### 10.5 ตรวจสอบ Cluster

```bash
pg_lsclusters
systemctl status postgresql@17-main --no-pager | head -5
```

ผลลัพธ์:
```text
Ver Cluster Port Status Owner    Data directory              Log file
17  main    5432 online postgres /var/lib/postgresql/17/main /var/log/postgresql/postgresql-17-main.log

● postgresql@17-main.service - PostgreSQL Cluster 17-main
     Loaded: loaded (/lib/systemd/system/postgresql@.service; enabled-runtime)
     Active: active (running) since Mon 2026-11-02 11:02:15 +07
```

### 10.6 ตรวจสอบ Version และ Checksums

```bash
sudo -u postgres psql -c "SELECT version()" -c "SHOW data_checksums" -c "SHOW password_encryption"
```

ผลลัพธ์:
```text
                                version                                 
------------------------------------------------------------------------
 PostgreSQL 17.11 (Ubuntu 17.11-1.pgdg24.04+2) on x86_64-pc-linux-gnu...

 data_checksums 
----------------
 on

 password_encryption 
---------------------
 scram-sha-256
```

### 10.7 Baseline Security

**`listen_addresses`** — จำกัดเฉพาะ Network ที่ต้องการ:
```ini
# /etc/postgresql/17/main/conf.d/10-gridcare-tuning.conf
listen_addresses = '127.0.0.1,10.104.0.11'
```

**`pg_hba.conf`** — ใช้ `hostssl` เท่านั้นสำหรับ Network:
```text
# TYPE     DATABASE   USER          ADDRESS         METHOD
local      all        postgres                      peer
local      all        all                           scram-sha-256
hostssl    all        all           127.0.0.1/32    scram-sha-256
hostssl    gridcare   billing_app   10.104.0.13/32  scram-sha-256
hostnossl  all        all           0.0.0.0/0       reject
```

**ตรวจสอบ:**
```sql
SELECT line_number, type, database, user_name, address, auth_method, error
FROM pg_hba_file_rules WHERE error IS NOT NULL;
```

ผลลัพธ์:
```text
 line_number | type | database | user_name | address | auth_method | error
-------------+------+----------+-----------+---------+-------------+-------
(0 rows)
```

### 10.8 ติดตั้ง PostgreSQL 18 เคียงข้าง

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

> 💡 Cluster 18 จะอยู่ Port 5433 โดยอัตโนมัติถ้า 5432 ถูกใช้แล้ว  
> ถ้าต้องการเตรียมสำหรับ Upgrade ให้ตั้ง `start.conf = manual` และหยุดไว้ก่อน

### 10.9 ตาราง Baseline Security Checklist

| # | รายการ | ค่าแนะนำ |
|---|---|---|
| 1 | `password_encryption` | scram-sha-256 |
| 2 | `ssl` | on |
| 3 | `listen_addresses` | จำกัดเฉพาะ IP ที่ต้องการ |
| 4 | `pg_hba.conf` | hostssl + scram-sha-256 + reject ที่ท้าย |
| 5 | `data_checksums` | on |
| 6 | `log_connections` | on |
| 7 | `log_disconnections` | on |
| 8 | `log_statement` | ddl |
| 9 | Superuser | ไม่ใช้กับแอป |
| 10 | Firewall | จำกัด CIDR |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: ติดตั้งแบบ One-liner สำหรับ Lab

```bash
sudo apt install -y postgresql-common && \
sudo bash -c "echo \"initdb_options = '--data-checksums'\" >> /etc/postgresql-common/createcluster.conf" && \
sudo apt install -y postgresql-17 postgresql-17-pgaudit postgresql-17-partman postgresql-17-repack && \
pg_lsclusters
```

### ตัวอย่างที่ 2: ตรวจสอบ Package ที่ติดตั้ง

```bash
dpkg -l | grep -Ei 'postgresql|pgbouncer|pgbackrest|partman|pgaudit|tmux'
```

ผลลัพธ์:
```text
ii  pgbackrest                    2.59.3-1.pgdg24.04+1   amd64  Reliable PostgreSQL Backup & Restore
ii  postgresql-17                 17.11-1.pgdg24.04+2    amd64  The World's Most Advanced Open Source
ii  postgresql-17-partman         5.5.0-1.pgdg24.04+1    amd64  PostgreSQL Partition Manager
ii  postgresql-17-pgaudit         17.1-2.pgdg24.04+1     amd64  PostgreSQL Audit Extension
ii  postgresql-17-repack          1.5.3-1.pgdg24.04+2    amd64  reorganize tables with minimal locks
```

### ตัวอย่างที่ 3: ตรวจสอบว่าเป็น Data Checksums จริง

```sql
SELECT current_setting('data_checksums') AS checksums,
       current_setting('server_version') AS version,
       current_setting('password_encryption') AS pwd_enc;
```

ผลลัพธ์:
```text
 checksums |  version |     pwd_enc     
-----------+----------+-----------------
 on        | 17.11    | scram-sha-256
```

### ตัวอย่างที่ 4: ถ้าลืมตั้ง Checksums ก่อนติดตั้ง

```bash
sudo systemctl stop postgresql@17-main
sudo pg_dropcluster 17 main --stop
sudo pg_createcluster 17 main --start -- --data-checksums
sudo -u postgres psql -c "SHOW data_checksums"
```

ผลลัพธ์:
```text
 data_checksums 
----------------
 on
```

## 12. สรุปย่อ จำง่าย
- **PGDG Repository** เท่านั้น  
- **`postgresql-common` ก่อนติดตั้ง**  
- **`initdb_options = '--data-checksums'` ก่อน `apt install`**  
- **`password_encryption = scram-sha-256`**  
- **`listen_addresses` จำกัดเฉพาะ IP ที่ต้องการ**  
- **`pg_hba.conf` ใช้ `hostssl`**  
- **`data_checksums = on`** คือ Baseline

ประโยคจำ: **“ติดตั้งให้ถูกตั้งแต่แรก ดีกว่าตามแก้ทีหลัง”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PGDG Repository: https://apt.postgresql.org/
- PostgreSQL Documentation — Installation on Ubuntu: https://www.postgresql.org/download/linux/ubuntu/
- PostgreSQL Documentation — initdb: https://www.postgresql.org/docs/17/app-initdb.html
- GridCare Workshop Day 1: Lab 3.1

---

# บทที่ 13 Data Checksums และการตรวจสอบความสมบูรณ์

## 1. เรื่อง
Data Checksums ใน PostgreSQL หน้าที่ วิธีตรวจสอบ และการแก้ไขเมื่อพบ Corruption

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจว่าทำไม Data Checksums จำเป็นต่อ Production  
2. เพื่อให้ตั้ง Checksums ได้ตั้งแต่ `initdb`  
3. เพื่อให้ตรวจสอบและแก้ไขเมื่อพบ Corruption  
4. เพื่อให้เปิด Checksums บน Cluster ที่มีอยู่เดิมได้

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ตั้ง `--data-checksums` ตอน `initdb`  
- ตรวจสอบด้วย `current_setting('data_checksums')`  
- ใช้ `pg_checksums --enable` และ `--verify`  
- อ่านผลลัพธ์ของ `pg_controldata`  
- วางแผนเปิด Checksums บนระบบ Production

## 4. เนื้อหาโดยย่อ
Data Checksums คือการเก็บ Checksum ของทุก Page ใน Data File  
ข้อดี: ตรวจพบ Corruption ได้ทันทีเมื่ออ่าน  
ข้อจำกัด: มี Overhead เล็กน้อย (CPU/Memory)  
แนะนำ: **เปิดทุก Production Cluster**  
ตั้งได้ 3 วิธี:
1. `initdb --data-checksums` (ก่อนสร้าง Cluster)  
2. `pg_createcluster -- --data-checksums`  
3. `pg_checksums --enable` (Cluster ที่มีอยู่แล้ว ต้องหยุดก่อน)

## 5. ประโยชน์ที่ได้รับ
- ตรวจพบ Disk Corruption ได้ทันที  
- ลดความเสี่ยงข้อมูลเสียหายเงียบ ๆ  
- ช่วยใน Recovery Planning  
- ทำให้ Backup Trustworthy ขึ้น  
- ช่วยยืนยันความสมบูรณ์หลัง Restore

## 6. ข้อควรระวัง
- **`pg_checksums --enable` ต้องหยุด Cluster**  
- **Checksums ไม่ได้ป้องกัน Corruption** แค่ตรวจพบ  
- **Overhead ~1-2%** ต่อ I/O  
- **ต้องรัน `pg_checksums --verify` เป็นระยะ** บน Standby หรือช่วง Maintenance  
- **Backup ที่เกิดจาก Cluster ที่ไม่มี Checksums** จะไม่มี Checksums ในไฟล์

## 7. ข้อดี
- เป็น Baseline ที่ควรเปิดทุก Production  
- ใช้ CPU ต่ำ  
- ตรวจพบ Corruption ได้ก่อนที่ข้อมูลจะเสียหายต่อ  
- ใช้ร่วมกับ Backup Verification ได้

## 8. ข้อเสีย
- ต้อง `initdb` ใหม่หรือ `pg_checksums --enable`  
- บน Cluster ใหญ่ใช้เวลานาน  
- Overhead เล็กน้อยต่อ I/O

## 9. ข้อห้าม
- ห้าม `pg_checksums --enable` บน Cluster ที่กำลังทำงาน  
- ห้ามเปิด Checksums บน Standby โดยไม่หยุด  
- ห้ามใช้ `pg_checksums --disable` บน Production  
- ห้ามลบไฟล์ใน `pg_wal` เพื่อแก้ Corruption  
- ห้าม Restore Backup โดยไม่ Verify

## 10. รายละเอียด

### 10.1 ตรวจสอบ Checksums

```sql
SHOW data_checksums;
```

ผลลัพธ์:
```text
 data_checksums 
----------------
 on
```

หรือจาก `pg_controldata`:
```bash
sudo -u postgres /usr/lib/postgresql/17/bin/pg_controldata /var/lib/postgresql/17/main | grep -i checksum
```

ผลลัพธ์:
```text
Data page checksum version:           1
```

> ค่า `1` = เปิด Checksums, `0` = ปิด

### 10.2 เปิด Checksums ตอน `initdb`

```bash
sudo -u postgres /usr/lib/postgresql/17/bin/initdb \
  -D /var/lib/postgresql/17/main \
  --auth-local peer --auth-host scram-sha-256 \
  --data-checksums
```

ผลลัพธ์:
```text
The files belonging to this database system will be owned by user "postgres".
...
Success. You can now start the database server using:
    /usr/lib/postgresql/17/bin/pg_ctl -D /var/lib/postgresql/17/main -l logfile start
```

### 10.3 เปิด Checksums บน Cluster ที่มีอยู่แล้ว

```bash
sudo systemctl stop postgresql@17-main
sudo -u postgres /usr/lib/postgresql/17/bin/pg_checksums --enable -D /var/lib/postgresql/17/main
sudo systemctl start postgresql@17-main
sudo -u postgres psql -c "SHOW data_checksums"
```

ผลลัพธ์:
```text
Checksum operation completed
Files scanned:   1234
Blocks scanned:  567890
pg_checksums: syncing data directory
pg_checksums: updating control file
Checksums enabled in cluster

 data_checksums 
----------------
 on
```

### 10.4 ตรวจสอบความสมบูรณ์

```bash
sudo systemctl stop postgresql@17-main
sudo -u postgres /usr/lib/postgresql/17/bin/pg_checksums --verify -D /var/lib/postgresql/17/main
echo "exit=$?"
```

ผลลัพธ์ (ปกติ):
```text
Checksum operation completed
Files scanned:   1234
Blocks scanned:  567890
Bad checksums:   0
Data checksum version: 1
exit=0
```

ถ้าพบ Corruption:
```text
Bad checksums:   3
Data checksum version: 1
pg_checksums: error: checksum verification failed for block 12345 in file "base/16384/16385"
exit=1
```

### 10.5 ตรวจสอบหลัง Restore

```bash
sudo -u postgres /usr/lib/postgresql/17/bin/pg_checksums --verify -D /var/tmp/gc-restore-test
```

ผลลัพธ์:
```text
Checksum operation completed
Files scanned:   1234
Blocks scanned:  567890
Bad checksums:   0
exit=0
```

### 10.6 ตารางเปรียบเทียบ Before/After

| มิติ | ไม่มี Checksums | มี Checksums |
|---|---|---|
| ตรวจ Corruption | ไม่ได้ | ได้ |
| Overhead CPU | ต่ำ | ต่ำมาก (~1%) |
| Overhead Disk | เท่าเดิม | เท่าเดิม |
| ตั้งตอน initdb | ไม่ต้อง | ต้อง `--data-checksums` |
| ตั้งภายหลัง | ทำได้ | ทำได้ (`pg_checksums --enable`) |
| แนะนำ Production | ❌ | ✅ |

### 10.7 Pipeline ที่ควรมี

```text
1) initdb ด้วย --data-checksums
        │
        ▼
2) Backup ด้วย pgBackRest
        │
        ▼
3) Restore Test
        │
        ▼
4) pg_checksums --verify บน Restore
        │
        ▼
5) รายงานผล (Pass/Fail)
```

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: ตรวจสอบว่า Cluster ใช้ Checksums จริง

```bash
sudo -u postgres /usr/lib/postgresql/17/bin/pg_controldata /var/lib/postgresql/17/main \
  | grep -iE 'checksum|state'
```

ผลลัพธ์:
```text
Database cluster state:               in production
Data page checksum version:           1
```

### ตัวอย่างที่ 2: ตรวจสอบบน Cluster ที่ Restore จาก Backup

```bash
sudo -u postgres /usr/lib/postgresql/18/bin/pg_checksums --verify -D /var/tmp/gc-restore-test
echo "exit=$?"
```

ผลลัพธ์:
```text
Checksum operation completed
Files scanned:   1500
Blocks scanned:  234567
Bad checksums:   0
exit=0
```

### ตัวอย่างที่ 3: ตั้ง Checksums ผ่าน `pg_createcluster`

```bash
sudo pg_createcluster 17 main --start -- --data-checksums
```

ผลลัพธ์:
```text
Creating new PostgreSQL cluster 17/main ...
/usr/lib/postgresql/17/bin/initdb -D /var/lib/postgresql/17/main \
  --auth-local peer --auth-host scram-sha-256 --no-instructions --data-checksums
Ver Cluster Port Status Owner    Data directory
17  main    5432 online postgres /var/lib/postgresql/17/main
```

## 12. สรุปย่อ จำง่าย
- **Checksums = Baseline ที่ควรเปิดทุก Production**  
- **ตั้งได้ 3 วิธี:** `initdb`, `pg_createcluster`, `pg_checksums --enable`  
- **ต้องหยุด Cluster ก่อน `pg_checksums --enable`**  
- **Verify ด้วย `pg_checksums --verify` เป็นระยะ**  
- **Bad checksums = 0 คือผลที่ต้องการ**  
- **หลัง Restore ต้อง Verify ก่อนใช้งาน**

ประโยคจำ: **“ไม่มี Checksums ก็ไม่รู้ว่าข้อมูลเสียตั้งแต่เมื่อไหร่”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — pg_checksums: https://www.postgresql.org/docs/17/app-pgchecksums.html
- PostgreSQL Documentation — initdb: https://www.postgresql.org/docs/17/app-initdb.html
- PostgreSQL Documentation — pg_controldata: https://www.postgresql.org/docs/17/app-pgcontroldata.html
- GridCare Workshop Day 1: Lab 3.1

---

# บทที่ 14 โครงสร้างไฟล์และ Parameter สำคัญ

## 1. เรื่อง
โครงสร้างไฟล์ของ PostgreSQL (PGDATA) และ Parameter สำคัญที่ต้องเข้าใจก่อนปรับแต่ง

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้รู้ว่าไฟล์ใดอยู่ที่ใดใน PGDATA  
2. เพื่อให้เข้าใจว่า Config File ใดมีผลกับอะไร  
3. เพื่อให้เข้าใจ Parameter สำคัญ 10+ ตัว  
4. เพื่อให้เลือก Parameter ได้ตามขนาดเครื่องและงาน

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- อธิบายโครงสร้าง PGDATA ได้  
- ระบุ Config File ที่แก้แล้วต้อง Reload หรือ Restart  
- อธิบาย Parameter สำคัญ 10 ตัวได้  
- ใช้ `pg_file_settings` และ `pg_settings` ตรวจสอบได้

## 4. เนื้อหาโดยย่อ
PGDATA ประกอบด้วย:
- `base/`, `global/` — Data File  
- `pg_wal/` — WAL  
- `pg_xact/`, `pg_subtrans/` — Transaction Log  
- `pg_stat/` — Cumulative Statistics  
- `pg_tblspc/` — Tablespace  
- `postgresql.conf` — Config หลัก  
- `pg_hba.conf` — กฎการเชื่อมต่อ  
- `pg_ident.conf` — Map User  
- `postgresql.auto.conf` — Config ที่ถูกเขียนด้วย `ALTER SYSTEM`

Parameter สำคัญ 10 ตัว:
`shared_buffers`, `effective_cache_size`, `work_mem`, `maintenance_work_mem`, `max_connections`, `wal_level`, `max_wal_size`, `checkpoint_timeout`, `random_page_cost`, `effective_io_concurrency`

## 5. ประโยชน์ที่ได้รับ
- รู้ว่าแก้ Config ที่ไหน  
- รู้ว่า Parameter ใดต้อง Restart  
- ลดการแก้ผิดไฟล์  
- ลดการตั้งค่าที่ไม่เหมาะสม  
- ทำให้ Audit Config ง่าย

## 6. ข้อควรระวัง
- **`postgresql.auto.conf`** จะถูกเขียนทับด้วย `ALTER SYSTEM`  
- **`postgresql.conf`** มักมี `include_dir = 'conf.d'` ที่ช่วยแยกไฟล์  
- **ค่า Parameter บางตัวต้อง Restart** เช่น `shared_buffers`  
- **`pg_hba.conf` อ่านบนลงล่าง** บรรทัดแรกที่ตรงถูกใช้  
- **Parameter บางตัวมีผลต่อ Planner** ไม่ใช่ Runtime

## 7. ข้อดี
- Config แยกไฟล์ได้ → จัดการง่าย  
- ตรวจสอบได้ด้วย `pg_file_settings`  
- Reload ได้โดยไม่ต้อง Restart สำหรับ Parameter ส่วนใหญ่

## 8. ข้อเสีย
- Parameter มีจำนวนมาก ต้องเข้าใจบริบท  
- `postgresql.auto.conf` อาจทำให้สับสน  
- Parameter บางตัวมี Interaction กัน

## 9. ข้อห้าม
- ห้ามแก้ `postgresql.auto.conf` ด้วยมือ  
- ห้ามใช้ `ALTER SYSTEM` กับ Patroni  
- ห้ามแก้ `pg_hba.conf` โดยไม่ตรวจ `pg_hba_file_rules`  
- ห้ามตั้ง `work_mem` สูงเกินไป (ต่อ Operation)  
- ห้ามตั้ง `random_page_cost = 1.1` บน HDD

## 10. รายละเอียด

### 10.1 โครงสร้าง PGDATA

```text
/var/lib/postgresql/17/main/
├── base/                 ← Data File ของแต่ละ Database
├── global/               ← Catalog ทั้ง Cluster
├── pg_wal/               ← Write-Ahead Log (16 MB ต่อไฟล์)
├── pg_wal/archive_status/
├── pg_xact/              ← Commit Log
├── pg_subtrans/
├── pg_multixact/
├── pg_stat/              ← Cumulative Statistics
├── pg_stat_tmp/
├── pg_tblspc/            ← Tablespace
├── pg_dynshmem/
├── pg_notify/
├── pg_replslot/
├── pg_serial/
├── pg_snapshots/
├── pg_logical/
├── postgresql.auto.conf
├── postgresql.conf
├── pg_hba.conf
├── pg_ident.conf
└── PG_VERSION
```

### 10.2 Config File ที่ต้องรู้

| ไฟล์ | ที่อยู่ | แก้แล้วต้อง |
|---|---|---|
| `postgresql.conf` | `/etc/postgresql/17/main/` | Reload หรือ Restart |
| `conf.d/*.conf` | `/etc/postgresql/17/main/conf.d/` | Reload หรือ Restart |
| `pg_hba.conf` | `/etc/postgresql/17/main/` | Reload |
| `pg_ident.conf` | `/etc/postgresql/17/main/` | Reload |
| `postgresql.auto.conf` | PGDATA | ใช้ `ALTER SYSTEM` เท่านั้น |

### 10.3 ตรวจสอบ Config

```sql
SHOW config_file;
SHOW hba_file;
SHOW data_directory;
```

ผลลัพธ์:
```text
               config_file               
-----------------------------------------
 /etc/postgresql/17/main/postgresql.conf

           hba_file           
------------------------------
 /etc/postgresql/17/main/pg_hba.conf

      data_directory       
---------------------------
 /var/lib/postgresql/17/main
```

### 10.4 Parameter สำคัญ 10+ ตัว

| Parameter | หน้าที่ | ต้อง Restart | ค่าแนะนำ (2 vCPU / 4 GB) |
|---|---|---|---|
| `shared_buffers` | Memory หลัก | ใช่ | `1GB` (25% ของ RAM) |
| `effective_cache_size` | Hint Cache ทั้งระบบ | ไม่ | `3GB` (75% ของ RAM) |
| `work_mem` | Memory ต่อ Operation | ไม่ | `8MB` |
| `maintenance_work_mem` | Memory ต่อ Maintenance | ไม่ | `256MB` |
| `max_connections` | Connection สูงสุด | ใช่ | `100` |
| `wal_level` | ระดับ WAL | ใช่ | `replica` |
| `max_wal_size` | ขนาด WAL สูงสุด | ไม่ | `4GB` |
| `checkpoint_timeout` | รอบ Checkpoint | ไม่ | `15min` |
| `random_page_cost` | Cost ของ Random Read | ไม่ | `1.1` (SSD) |
| `effective_io_concurrency` | Concurrency ต่อ Disk | ไม่ | `200` (SSD) |
| `shared_preload_libraries` | Library ที่โหลดตอน start | ใช่ | `pg_stat_statements` |
| `autovacuum_max_workers` | Worker สำหรับ Autovacuum | ใช่ | `3` |

### 10.5 ไฟล์ `conf.d/10-gridcare-tuning.conf` ตัวอย่าง

```ini
# GridCare: 2 vCPU / 4 GB RAM / SSD
listen_addresses = '*'
max_connections = 100
superuser_reserved_connections = 3
reserved_connections = 2
shared_buffers = 1GB
effective_cache_size = 3GB
work_mem = 8MB
maintenance_work_mem = 256MB
max_wal_size = 4GB
min_wal_size = 1GB
checkpoint_timeout = 15min
checkpoint_completion_target = 0.9
random_page_cost = 1.1
effective_io_concurrency = 200
shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.track = top
track_io_timing = on
autovacuum_max_workers = 3
autovacuum_vacuum_cost_limit = 1000
```

### 10.6 ตรวจสอบหลังแก้

```sql
SELECT sourcefile, sourceline, name, error
FROM pg_file_settings WHERE error IS NOT NULL;
```

ผลลัพธ์:
```text
 sourcefile | sourceline | name | error 
------------+------------+------+-------
(0 rows)
```

```sql
SELECT name, setting, unit, pending_restart
FROM pg_settings WHERE pending_restart;
```

ผลลัพธ์:
```text
          name          | setting | unit | pending_restart 
------------------------+---------+------+-----------------
 shared_buffers         | 16384   | 8kB  | t
 reserved_connections   | 2       |      | t
 shared_preload_libraries| pg_stat_statements | | t
 listen_addresses       | *       |      | t
```

### 10.7 Reload vs Restart

| ค่า | Reload | Restart |
|---|---|---|
| `work_mem` | ✅ | ❌ |
| `shared_buffers` | ❌ | ✅ |
| `max_connections` | ❌ | ✅ |
| `listen_addresses` | ❌ | ✅ |
| `shared_preload_libraries` | ❌ | ✅ |
| `pg_hba.conf` | ✅ | ❌ |
| `log_min_duration_statement` | ✅ | ❌ |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: ดู Parameter ทั้งหมดที่ขึ้นต้นด้วย pg_stat

```sql
SELECT name, setting, unit FROM pg_settings WHERE name LIKE 'pg_stat%';
```

### ตัวอย่างที่ 2: ดูค่าที่ตั้งใน Config เทียบกับ Runtime

```sql
SELECT name, setting, source, sourcefile, sourceline
FROM pg_settings WHERE name IN ('shared_buffers','work_mem','random_page_cost');
```

ผลลัพธ์:
```text
       name       | setting |  source  |               sourcefile               | sourceline
------------------+---------+----------+----------------------------------------+------------
 random_page_cost | 1.1     | file     | /etc/postgresql/17/main/conf.d/10-gridcare-tuning.conf | 12
 shared_buffers   | 131072  | file     | /etc/postgresql/17/main/conf.d/10-gridcare-tuning.conf | 6
 work_mem         | 8192    | file     | /etc/postgresql/17/main/conf.d/10-gridcare-tuning.conf | 7
```

### ตัวอย่างที่ 3: ตรวจสอบว่ามี Config File ใดที่ผิดพลาด

```sql
SELECT sourcefile, name, error FROM pg_file_settings WHERE error IS NOT NULL;
```

### ตัวอย่างที่ 4: ดู `postgresql.auto.conf`

```bash
sudo cat /var/lib/postgresql/17/main/postgresql.auto.conf
```

ผลลัพธ์:
```text
# Do not edit this file manually!
# It will be overwritten by the ALTER SYSTEM command.
```

## 12. สรุปย่อ จำง่าย
- **PGDATA มี 3 ส่วนหลัก:** Data, WAL, Config  
- **Config หลัก:** `postgresql.conf`, `conf.d/*.conf`, `pg_hba.conf`, `pg_ident.conf`, `postgresql.auto.conf`  
- **`postgresql.auto.conf` ห้ามแก้ด้วยมือ** ใช้ `ALTER SYSTEM` เท่านั้น  
- **ตรวจด้วย `pg_file_settings` และ `pg_settings`**  
- **Reload vs Restart ต่างกัน** ต้องเข้าใจ  
- **Parameter สำคัญ 10+ ตัว** ต้องเข้าใจก่อนปรับ

ประโยคจำ: **“Config ที่ถูกต้องคือ Config ที่ตรวจสอบได้ ไม่ใช่ Config ที่ดูดี”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — Configuration: https://www.postgresql.org/docs/17/runtime-config.html
- PostgreSQL Documentation — File Locations: https://www.postgresql.org/docs/17/runtime-config-file-locations.html
- PostgreSQL Documentation — View pg_file_settings: https://www.postgresql.org/docs/17/view-pg-file-settings.html
- GridCare Workshop Day 1: Lab 3.2

---

# บทที่ 15 Tuning เบื้องต้นตามขนาดเครื่อง

## 1. เรื่อง
การปรับแต่ง Parameter พื้นฐานให้เหมาะกับขนาดเครื่องและงาน โดยเริ่มจากค่าที่ปลอดภัย

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้ผู้อ่านตั้ง Baseline Tuning ที่ปลอดภัย  
2. เพื่อให้เข้าใจว่า Parameter ใดขึ้นกับ RAM, CPU, Disk  
3. เพื่อให้เลือกค่าเริ่มต้นที่เหมาะกับเครื่องเล็ก-กลาง-ใหญ่  
4. เพื่อให้ตรวจสอบผลหลังปรับด้วย Metric จริง

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- คำนวณ `shared_buffers`, `effective_cache_size`, `work_mem` ได้  
- เลือกค่า `random_page_cost` ตาม Disk  
- ตั้ง `max_connections` ให้เหมาะกับ PgBouncer  
- ตั้ง Autovacuum ให้เหมาะกับขนาดตาราง  
- ตรวจสอบ `pending_restart` และวัดผล

## 4. เนื้อหาโดยย่อ
Tuning Baseline ประกอบด้วย 5 กลุ่ม:
1. Memory (`shared_buffers`, `effective_cache_size`, `work_mem`, `maintenance_work_mem`)  
2. Connection (`max_connections`)  
3. WAL (`max_wal_size`, `min_wal_size`, `checkpoint_timeout`)  
4. Planner (`random_page_cost`, `effective_io_concurrency`)  
5. Autovacuum (`autovacuum_max_workers`, `autovacuum_vacuum_cost_limit`)

## 5. ประโยชน์ที่ได้รับ
- ระบบมี Baseline ที่ปลอดภัย  
- ลด I/O ที่ไม่จำเป็น  
- ลด Query ที่ล้น Disk (Temp Spill)  
- ทำให้ Planner เลือก Index ได้ถูก  
- ทำให้ Autovacuum ทำงานได้ทัน

## 6. ข้อควรระวัง
- **`shared_buffers` สูงเกินไป** ทำให้ระบบขาด Memory ให้ OS Cache  
- **`work_mem` สูงเกินไป** ทำให้ OOM ได้เพราะเป็นต่อ Operation  
- **`max_connections` สูงเกินไป** ทำให้ Memory และ Context Switch หนัก  
- **`random_page_cost` ต่ำเกินไป** บน HDD ทำให้ Planner เลือก Random Read ผิด  
- **`max_wal_size` สูงเกินไป** ทำให้ Recovery นาน

## 7. ข้อดี
- Baseline ที่ดีทำให้ระบบมีประสิทธิภาพโดยไม่ต้องจูนทุก Query  
- ลด Incident จาก OOM และ Temp Spill  
- ทำให้ Planner ทำงานดีขึ้น  
- ทำให้ Autovacuum ทำงานได้ทัน

## 8. ข้อเสีย
- ค่า Baseline ที่ดีสำหรับงานหนึ่งอาจไม่ดีกับอีกงาน  
- ต้องวัดผลหลังปรับ  
- ค่าบางตัวต้อง Restart

## 9. ข้อห้าม
- ห้ามตั้ง `shared_buffers` เกิน 40% ของ RAM ทั้งเครื่อง  
- ห้ามตั้ง `work_mem` เกิน 5% ของ RAM ต่อ Operation  
- ห้ามตั้ง `random_page_cost = 1.1` บน HDD  
- ห้ามตั้ง `max_connections` สูงโดยไม่มี PgBouncer  
- ห้ามปรับโดยไม่เก็บ Baseline Metric

## 10. รายละเอียด

### 10.1 กลุ่ม Memory

**`shared_buffers`** — Memory หลักของ PostgreSQL  
แนะนำ: 25% ของ RAM ทั้งเครื่อง  
ข้อยกเว้น: ไม่ควรเกิน 40% แม้ RAM จะมาก  
ต้อง Restart

**`effective_cache_size`** — Hint ให้ Planner ทราบ Cache ทั้งระบบ  
แนะนำ: 50–75% ของ RAM  
ไม่ต้อง Restart

**`work_mem`** — Memory ต่อ Operation (Sort, Hash)  
แนะนำ: `(RAM × 0.25) / (max_connections × 3)`  
ตัวอย่าง: 4 GB, 100 conn → `4096 × 0.25 / 300 ≈ 3.4 MB` → ตั้ง `8MB` ปลอดภัย  
ไม่ต้อง Restart

**`maintenance_work_mem`** — Memory ต่อ Maintenance (VACUUM, CREATE INDEX)  
แนะนำ: 5–10% ของ RAM (สูงสุด ~1–2 GB)  
ไม่ต้อง Restart

### 10.2 กลุ่ม Connection

**`max_connections`** — จำนวน Connection สูงสุด  
แนะนำ: ไม่เกิน 200–300 ถ้าไม่มี PgBouncer  
ถ้ามี PgBouncer ให้ `max_connections` ของ PostgreSQL = `pool_size × จำนวน DB + reserve`  
ต้อง Restart

### 10.3 กลุ่ม WAL

**`max_wal_size`** — ขนาด WAL สูงสุดก่อน Checkpoint  
แนะนำ: `4GB` ขึ้นไป  
ไม่ต้อง Restart

**`min_wal_size`** — ขนาด WAL ต่ำสุดที่เก็บไว้  
แนะนำ: `1GB`  
ไม่ต้อง Restart

**`checkpoint_timeout`** — รอบ Checkpoint  
แนะนำ: `15min`  
ไม่ต้อง Restart

**`checkpoint_completion_target`** — กระจายการเขียน  
แนะนำ: `0.9`  
ไม่ต้อง Restart

### 10.4 กลุ่ม Planner

**`random_page_cost`**  
- SSD/NVMe: `1.1`  
- HDD: `4.0`  
- SAN: `2.0`–`3.0`  
ไม่ต้อง Restart

**`effective_io_concurrency`**  
- SSD: `200`  
- HDD: `2`–`4`  
- SAN: `100`–`200`  
ไม่ต้อง Restart

### 10.5 กลุ่ม Autovacuum

**`autovacuum_max_workers`**  
แนะนำ: `3`–`5`  
ต้อง Restart

**`autovacuum_vacuum_cost_limit`**  
แนะนำ: `1000`–`2000`  
ไม่ต้อง Restart

**`autovacuum_naptime`**  
แนะนำ: `30s`–`60s`  
ไม่ต้อง Restart

### 10.6 ตาราง Baseline ตามขนาดเครื่อง

| เครื่อง | RAM | shared_buffers | effective_cache_size | work_mem | maintenance_work_mem | max_connections |
|---|---|---|---|---|---|---|
| เล็ก | 4 GB | 1 GB | 3 GB | 8 MB | 256 MB | 100 |
| กลาง | 16 GB | 4 GB | 12 GB | 16 MB | 1 GB | 200 |
| ใหญ่ | 64 GB | 16 GB | 48 GB | 32 MB | 2 GB | 400 |
| ใหญ่พิเศษ | 256 GB | 64 GB | 192 GB | 64 MB | 4 GB | 800 |

> 💡 ถ้าใช้ PgBouncer ให้ลด `max_connections` ของ PostgreSQL ลงเหลือ ~100–200 และใช้ `pool_size` ของ PgBouncer แทน

### 10.7 ตั้งค่าผ่าน `conf.d`

```bash
sudo truncate -s 0 /etc/postgresql/17/main/conf.d/10-gridcare-tuning.conf
sudo nano /etc/postgresql/17/main/conf.d/10-gridcare-tuning.conf
```

**เนื้อหาสำหรับ 2 vCPU / 4 GB RAM / SSD:**

```ini
# GridCare Tuning — 2 vCPU / 4 GB RAM / SSD
listen_addresses = '*'
max_connections = 100
superuser_reserved_connections = 3
reserved_connections = 2

shared_buffers = 1GB
effective_cache_size = 3GB
work_mem = 8MB
maintenance_work_mem = 256MB

max_wal_size = 4GB
min_wal_size = 1GB
checkpoint_timeout = 15min
checkpoint_completion_target = 0.9

random_page_cost = 1.1
effective_io_concurrency = 200

shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.track = top
track_io_timing = on

autovacuum_max_workers = 3
autovacuum_vacuum_cost_limit = 1000
```

```bash
sudo chown postgres:postgres /etc/postgresql/17/main/conf.d/10-gridcare-tuning.conf
```

### 10.8 ตรวจสอบและ Reload/Restart

```sql
-- ตรวจว่าไฟล์ Config ไม่มี Error
SELECT sourcefile, sourceline, name, error FROM pg_file_settings WHERE error IS NOT NULL;

-- Reload
SELECT pg_reload_conf();

-- ตรวจ Parameter ที่ต้อง Restart
SELECT name, setting, unit, pending_restart FROM pg_settings WHERE pending_restart;
```

ผลลัพธ์:
```text
          name          | setting | unit | pending_restart 
------------------------+---------+------+-----------------
 shared_buffers         | 16384   | 8kB  | t
 reserved_connections   | 2       |      | t
 shared_preload_libraries| pg_stat_statements | | t
 listen_addresses       | *       |      | t
```

```bash
sudo systemctl restart postgresql@17-main
sudo -u postgres psql -c "SELECT 'shared_buffers=' || current_setting('shared_buffers') AS result"
```

ผลลัพธ์:
```text
       result        
---------------------
 shared_buffers=1GB
```

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Script คำนวณ Baseline จาก RAM

```bash
#!/usr/bin/env bash
RAM_MB=$(awk '/MemTotal/ {printf "%d", $2/1024}' /proc/meminfo)
SB=$((RAM_MB / 4))
ECS=$((RAM_MB * 3 / 4))
WM=$((RAM_MB / 512))
MWM=$((RAM_MB / 16))
echo "RAM=${RAM_MB}MB shared_buffers=${SB}MB effective_cache_size=${ECS}MB work_mem=${WM}MB maintenance_work_mem=${MWM}MB"
```

ผลลัพธ์ (RAM 4 GB):
```text
RAM=3866MB shared_buffers=966MB effective_cache_size=2899MB work_mem=7MB maintenance_work_mem=241MB
```

### ตัวอย่างที่ 2: ตรวจสอบ Before/After

```sql
SELECT name, setting, unit
FROM pg_settings
WHERE name IN ('shared_buffers','effective_cache_size','work_mem','random_page_cost','max_connections');
```

ผลลัพธ์:
```text
        name         | setting | unit 
---------------------+---------+------
 effective_cache_size| 393216  | 8kB
 max_connections     | 100     |
 random_page_cost    | 1.1     |
 shared_buffers      | 131072  | 8kB
 work_mem            | 8192    | kB
```

### ตัวอย่างที่ 3: ตรวจสอบว่า Planner เลือก Index ถูกหลังปรับ `random_page_cost`

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT customer_id FROM customers WHERE ca_number = '020000123456';
```

ผลลัพธ์:
```text
 Index Scan using customers_ca_number_key on customers
   (cost=0.42..8.44 rows=1 width=8) (actual time=0.045..0.046 rows=1 loops=1)
   Index Cond: (ca_number = '020000123456'::bpchar)
 Planning Time: 0.123 ms
 Execution Time: 0.067 ms
```

## 12. สรุปย่อ จำง่าย
- **shared_buffers ≈ 25% ของ RAM**  
- **effective_cache_size ≈ 50–75% ของ RAM**  
- **work_mem คำนวณจาก RAM / (max_connections × 3)**  
- **maintenance_work_mem 5–10% ของ RAM**  
- **random_page_cost = 1.1 สำหรับ SSD**  
- **max_connections ไม่เกิน 200–300 ถ้าไม่มี PgBouncer**  
- **Autovacuum ต้องทำงานได้ทัน**

ประโยคจำ: **“Tuning ที่ดีคือ Tuning ที่วัดผลได้ ไม่ใช่ Tuning ที่ดูดี”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — Resource Consumption: https://www.postgresql.org/docs/17/runtime-config-resource.html
- PostgreSQL Wiki — Tuning Your PostgreSQL Server: https://wiki.postgresql.org/wiki/Tuning_Your_PostgreSQL_Server
- PGTune: https://pgtune.leopard.in.ua/
- GridCare Workshop Day 1: Lab 3.2

---

# บทที่ 16 จัดการ Cluster ด้วย pg_lsclusters และ systemd

## 1. เรื่อง
การจัดการ PostgreSQL Cluster ด้วย `pg_lsclusters`, `pg_createcluster`, `pg_dropcluster`, `pg_ctlcluster` และ systemd

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้จัดการหลาย Cluster บนเครื่องเดียวได้  
2. เพื่อให้เข้าใจระบบ systemd ของ PostgreSQL  
3. เพื่อให้สามารถ Start/Stop/Restart Cluster ได้ถูกต้อง  
4. เพื่อให้สามารถสร้าง Cluster ทดสอบแยกจาก Production

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ใช้ `pg_lsclusters` ดู Cluster ทั้งหมด  
- สร้าง/ลบ Cluster ด้วย `pg_createcluster`/`pg_dropcluster`  
- ใช้ `pg_ctlcluster` จัดการ Cluster  
- ใช้ `systemctl` กับ `postgresql@<ver>-<cluster>`  
- เข้าใจ `start.conf` และ `data_directory`

## 4. เนื้อหาโดยย่อ
`postgresql-common` ให้เครื่องมือ 4 ตัว:
- `pg_lsclusters` — ดู Cluster  
- `pg_createcluster` — สร้าง Cluster  
- `pg_dropcluster` — ลบ Cluster  
- `pg_ctlcluster` — Start/Stop/Restart Cluster

แต่ละ Cluster มี systemd unit แยก:
- `postgresql.service` — Wrapper  
- `postgresql@17-main.service` — Cluster 17/main  
- `postgresql@18-main.service` — Cluster 18/main

## 5. ประโยชน์ที่ได้รับ
- จัดการหลาย Version บนเครื่องเดียวได้  
- สร้าง Cluster ทดสอบได้  
- Restart Cluster เดียวโดยไม่กระทบ Cluster อื่น  
- ใช้ systemd จัดการได้เหมือน Service อื่น

## 6. ข้อควรระวัง
- **`postgresql.service` เป็น Wrapper** ไม่ได้ทำงานจริง  
- **`systemctl restart postgresql`** จะ Restart ทุก Cluster  
- **`start.conf = manual`** ทำให้ Cluster ไม่ Start อัตโนมัติ  
- **`pg_dropcluster` ลบข้อมูลทันที** ไม่มี Backup  
- **`pg_ctlcluster` ต้องรันด้วย sudo** สำหรับ Cluster ของ postgres

## 7. ข้อดี
- จัดการหลาย Cluster ได้ง่าย  
- ใช้ systemd มาตรฐาน  
- มี Log แยกตาม Cluster  
- มี Config แยกตาม Cluster

## 8. ข้อเสีย
- ชื่อ systemd unit ยาว  
- `postgresql.service` อาจทำให้สับสน  
- Config กระจายหลายที่

## 9. ข้อห้าม
- ห้าม `pg_dropcluster` บน Production โดยไม่สำรอง  
- ห้ามใช้ `systemctl restart postgresql` บนเครื่องที่มีหลาย Cluster  
- ห้ามแก้ `start.conf` โดยไม่เข้าใจ  
- ห้ามใช้ `pg_ctl` ตรง ๆ กับ Cluster ที่จัดการด้วย systemd  
- ห้ามลบโฟลเดอร์ Cluster ด้วยมือ

## 10. รายละเอียด

### 10.1 `pg_lsclusters`

```bash
pg_lsclusters
```

ผลลัพธ์:
```text
Ver Cluster Port Status Owner    Data directory              Log file
17  main    5432 online postgres /var/lib/postgresql/17/main /var/log/postgresql/postgresql-17-main.log
18  main    5432 down   postgres /var/lib/postgresql/18/main /var/log/postgresql/postgresql-18-main.log
```

### 10.2 `pg_createcluster`

```bash
sudo pg_createcluster 17 test --start -- --data-checksums
pg_lsclusters
```

ผลลัพธ์:
```text
Ver Cluster Port Status Owner    Data directory
17  main    5432 online postgres /var/lib/postgresql/17/main
17  test    5433 online postgres /var/lib/postgresql/17/test
```

> 💡 `pg_createcluster` จะเลือก Port ถัดไปให้อัตโนมัติถ้า Port ซ้ำ

### 10.3 `pg_dropcluster`

```bash
sudo pg_dropcluster 17 test --stop
pg_lsclusters
```

ผลลัพธ์:
```text
Ver Cluster Port Status Owner    Data directory
17  main    5432 online postgres /var/lib/postgresql/17/main
```

### 10.4 `pg_ctlcluster`

```bash
sudo pg_ctlcluster 17 main stop
sudo pg_ctlcluster 17 main start
sudo pg_ctlcluster 17 main restart
sudo pg_ctlcluster 17 main reload
sudo pg_ctlcluster 17 main status
```

ผลลัพธ์:
```text
Cluster 17/main is running
```

### 10.5 systemd

```bash
# Cluster เดียว
sudo systemctl start postgresql@17-main
sudo systemctl stop postgresql@17-main
sudo systemctl restart postgresql@17-main
sudo systemctl status postgresql@17-main --no-pager | head -5
```

ผลลัพธ์:
```text
● postgresql@17-main.service - PostgreSQL Cluster 17-main
     Loaded: loaded (/lib/systemd/system/postgresql@.service; enabled-runtime)
     Active: active (running) since Mon 2026-11-02 11:02:15 +07
```

```bash
# ทั้งหมด (ไม่แนะนำบนเครื่องหลาย Cluster)
sudo systemctl restart postgresql
```

### 10.6 `start.conf`

```bash
cat /etc/postgresql/17/main/start.conf
```

ผลลัพธ์ (ค่าเริ่มต้น):
```text
# Automatic startup configuration
# auto: automatically start/stop the cluster in the init script
# manual: do not start/stop the cluster
# disabled: do not allow the cluster to be started
auto
```

เปลี่ยนเป็น `manual` เพื่อไม่ให้ Start อัตโนมัติ:
```bash
echo manual | sudo tee /etc/postgresql/17/main/start.conf
```

### 10.7 Log Location

```bash
sudo tail -n 5 /var/log/postgresql/postgresql-17-main.log
```

ผลลัพธ์:
```text
2026-11-02 11:02:15.123 +07 [1234] LOG:  starting PostgreSQL 17.11 on x86_64-pc-linux-gnu
2026-11-02 11:02:15.456 +07 [1234] LOG:  listening on IPv4 address "0.0.0.0", port 5432
2026-11-02 11:02:15.789 +07 [1234] LOG:  database system is ready to accept connections
```

### 10.8 ตารางคำสั่งที่ใช้บ่อย

| งาน | คำสั่ง |
|---|---|
| ดู Cluster | `pg_lsclusters` |
| สร้าง Cluster | `sudo pg_createcluster 17 test --start -- --data-checksums` |
| ลบ Cluster | `sudo pg_dropcluster 17 test --stop` |
| Start Cluster | `sudo pg_ctlcluster 17 main start` |
| Restart Cluster | `sudo systemctl restart postgresql@17-main` |
| Reload Cluster | `sudo pg_ctlcluster 17 main reload` |
| Status | `systemctl status postgresql@17-main` |
| Log | `sudo tail -f /var/log/postgresql/postgresql-17-main.log` |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: สร้าง Cluster ทดสอบ

```bash
sudo pg_createcluster 17 test --start -- --data-checksums
sudo -u postgres psql -p 5433 -c "SELECT version()"
```

ผลลัพธ์:
```text
                                version                                 
------------------------------------------------------------------------
 PostgreSQL 17.11 (Ubuntu 17.11-1.pgdg24.04+2) on x86_64-pc-linux-gnu...
```

### ตัวอย่างที่ 2: หยุด Cluster เดียว

```bash
sudo systemctl stop postgresql@17-main
pg_lsclusters
```

ผลลัพธ์:
```text
Ver Cluster Port Status Owner    Data directory
17  main    5432 down   postgres /var/lib/postgresql/17/main
18  main    5432 down   postgres /var/lib/postgresql/18/main
```

### ตัวอย่างที่ 3: เปลี่ยน `start.conf` เป็น `manual`

```bash
echo manual | sudo tee /etc/postgresql/17/main/start.conf
sudo systemctl restart postgresql
pg_lsclusters
```

ผลลัพธ์:
```text
Ver Cluster Port Status Owner    Data directory
17  main    5432 down   postgres /var/lib/postgresql/17/main
18  main    5432 down   postgres /var/lib/postgresql/18/main
```

## 12. สรุปย่อ จำง่าย
- **`pg_lsclusters` ดู Cluster**  
- **`pg_createcluster`/`pg_dropcluster` สร้าง/ลบ**  
- **`pg_ctlcluster` Start/Stop/Restart**  
- **`systemctl` ใช้กับ `postgresql@17-main`**  
- **`start.conf = manual`** ป้องกัน Start อัตโนมัติ  
- **Log อยู่ที่ `/var/log/postgresql/`**  
- **หลีกเลี่ยง `systemctl restart postgresql`** ถ้ามีหลาย Cluster

ประโยคจำ: **“Cluster หนึ่งมี Service หนึ่ง มี Config หนึ่ง มี Log หนึ่ง”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- postgresql-common: https://wiki.postgresql.org/wiki/PostgreSQL_Common_Tools
- Ubuntu PostgreSQL: https://ubuntu.com/server/docs/databases-postgresql
- PostgreSQL Documentation — Managing Multiple Clusters: https://www.postgresql.org/docs/17/creating-cluster.html
- GridCare Workshop Day 1: Lab 3.1, Lab 3.2

---

# บทที่ 17 Logging มาตรฐานสำหรับ Production

## 1. เรื่อง
ชุดค่า Logging มาตรฐานสำหรับ PostgreSQL Production เพื่อใช้ Monitoring และ S troubleshooting

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้ Log มีข้อมูลที่จำเป็นต่อ Incident Response  
2. เพื่อให้สามารถใช้ pgBadger วิเคราะห์ Log ได้  
3. เพื่อให้ Log มี PII น้อยที่สุด  
4. เพื่อให้ Rotation และ Retention เหมาะกับ Production

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ตั้ง `log_line_prefix` ที่มีข้อมูลครบ  
- ตั้ง `log_min_duration_statement` ให้เหมาะสม  
- ตั้ง Log ที่เกี่ยวกับ Lock, Checkpoint, Autovacuum, Temp File  
- เลือก `log_statement` ที่ไม่ทำให้ Log บวม  
- ตั้ง `logrotate` และ Retention

## 4. เนื้อหาโดยย่อ
ชุด Log มาตรฐานสำหรับ Production:
- `log_line_prefix` — รูปแบบบรรทัด  
- `log_min_duration_statement = 500ms` — Query ช้า  
- `log_lock_waits = on` — Lock Wait  
- `log_temp_files = 0` — Temp File  
- `log_checkpoints = on` — Checkpoint  
- `log_autovacuum_min_duration = 10s` — Autovacuum  
- `log_connections = on` / `log_disconnections = on` — Connection  
- `log_statement = 'ddl'` — DDL  
- `lc_messages = 'C'` — Message ภาษาอังกฤษ  
- `log_timezone = 'Asia/Bangkok'` — Timezone

## 5. ประโยชน์ที่ได้รับ
- Incident Response เห็นบริบทครบ  
- pgBadger วิเคราะห์ได้  
- ตรวจ Lock และ Checkpoint ได้  
- ลด PII ใน Log  
- ทำให้ Log มีขนาด manageable

## 6. ข้อควรระวัง
- **`log_statement = 'all'`** ทำให้ Log บวมมาก  
- **`log_min_duration_statement = 0`** ทำให้ Log ทุก Query  
- **`log_parameter = on`** ทำให้ PII ลง Log  
- **Log ไม่ Rotate** ทำให้ Disk เต็ม  
- **`lc_messages` ไม่ใช่ 'C'** ทำให้ pgBadger แปลงไม่ได้

## 7. ข้อดี
- มีข้อมูลเพียงพอต่อการ S troubleshooting  
- ใช้ร่วมกับ pgBadger ได้  
- ตรวจ Lock, Checkpoint, Autovacuum ได้  
- ลด PII

## 8. ข้อเสีย
- Log มีขนาดใหญ่ขึ้น  
- ต้องตั้ง `logrotate`  
- ต้องกำหนด Retention

## 9. ข้อห้าม
- ห้าม `log_statement = 'all'` บน Production  
- ห้าม `log_min_duration_statement = 0` บน Production  
- ห้ามเปิด `log_parameter = on` ถ้ามี PII  
- ห้ามใช้ `lc_messages` ที่ไม่ใช่ 'C'  
- ห้ามปล่อยให้ Log ไม่ Rotate

## 10. รายละเอียด

### 10.1 `log_line_prefix` ที่แนะนำ

```ini
log_line_prefix = '%m [%p] %q%u@%d app=%a client=%h '
```

ความหมาย:
- `%m` — Timestamp พร้อม Timezone  
- `%p` — PID  
- `%q` — Stop here in non-session processes  
- `%u` — Username  
- `%d` — Database  
- `%a` — Application Name  
- `%h` — Client Host

### 10.2 ไฟล์ `conf.d/20-gridcare-logging.conf`

```ini
# GridCare Logging มาตรฐาน
log_line_prefix = '%m [%p] %q%u@%d app=%a client=%h '
log_min_duration_statement = 500ms
log_lock_waits = on
deadlock_timeout = 1s
log_temp_files = 0
log_checkpoints = on
log_autovacuum_min_duration = 10s
log_connections = on
log_disconnections = on
log_statement = 'ddl'
lc_messages = 'C'
log_timezone = 'Asia/Bangkok'
shared_preload_libraries = 'pg_stat_statements,auto_explain'
auto_explain.log_min_duration = '2s'
auto_explain.log_analyze = off
```

### 10.3 ตาราง Parameter และผลกระทบ

| Parameter | ค่าแนะนำ | ผล |
|---|---|---|
| `log_min_duration_statement` | 500ms | Log Query ช้าเท่านั้น |
| `log_lock_waits` | on | Log Lock Wait |
| `log_temp_files` | 0 | Log ทุก Temp File |
| `log_checkpoints` | on | Log Checkpoint |
| `log_autovacuum_min_duration` | 10s | Log Autovacuum ที่นาน |
| `log_connections` | on | Log การเชื่อมต่อ |
| `log_disconnections` | on | Log การตัดการเชื่อมต่อ |
| `log_statement` | 'ddl' | Log เฉพาะ DDL |
| `lc_messages` | 'C' | Message ภาษาอังกฤษ |

### 10.4 การใช้งาน

```bash
sudo truncate -s 0 /etc/postgresql/17/main/conf.d/20-gridcare-logging.conf
sudo nano /etc/postgresql/17/main/conf.d/20-gridcare-logging.conf
sudo chown postgres:postgres /etc/postgresql/17/main/conf.d/20-gridcare-logging.conf
sudo -u postgres psql -c "SELECT pg_reload_conf()"
```

### 10.5 ตรวจสอบ

```sql
SELECT sourcefile, name, error FROM pg_file_settings WHERE error IS NOT NULL;
SELECT name, pending_restart FROM pg_settings WHERE pending_restart;
```

ผลลัพธ์:
```text
          name          | pending_restart 
------------------------+-----------------
 shared_preload_libraries| t
```

> ⚠️ `shared_preload_libraries` ต้อง Restart

```bash
sudo systemctl restart postgresql@17-main
sudo -u postgres psql -c "SELECT CASE WHEN current_setting('shared_preload_libraries') LIKE '%auto_explain%' THEN 'AUTOEXPLAIN_READY' ELSE 'NOT_LOADED' END AS result"
```

ผลลัพธ์:
```text
     result       
------------------
 AUTOEXPLAIN_READY
```

### 10.6 Logrotate

ไฟล์ `/etc/logrotate.d/postgresql-common`:

```text
/var/log/postgresql/*.log {
    weekly
    rotate 4
    compress
    delaycompress
    missingok
    notifempty
    create 0640 postgres adm
    sharedscripts
    postrotate
        /usr/bin/systemctl reload postgresql.service > /dev/null 2>&1 || true
    endscript
}
```

ทดสอบ:
```bash
sudo logrotate -d /etc/logrotate.d/postgresql-common
```

### 10.7 pgBadger

```bash
sudo pgbadger -j 2 --anonymize \
  --prefix '%m [%p] %q%u@%d app=%a client=%h ' \
  -o /var/tmp/pgbadger-gridcare.html /var/log/postgresql/postgresql-17-main.log
```

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: ดู Log หลังตั้งค่า

```bash
sudo tail -n 3 /var/log/postgresql/postgresql-17-main.log
```

ผลลัพธ์:
```text
2026-11-02 13:05:23.517 +07 [4363] postgres@postgres app=[unknown] client=[local] LOG:  connection authorized: user=postgres database=postgres application_name=psql
2026-11-02 13:05:23.520 +07 [4363] postgres@postgres app=psql client=[local] LOG:  disconnection: session time: 0:00:00.004
```

### ตัวอย่างที่ 2: ดู Log Lock Wait

```bash
sudo grep "still waiting" /var/log/postgresql/postgresql-17-main.log | tail -2
```

ผลลัพธ์:
```text
2026-11-02 14:12:34.567 +07 [7665] postgres@gridcare app=migration_B client=[local] LOG:  process 7665 still waiting for AccessExclusiveLock on relation 16384 of database 16389 after 1000.123 ms
2026-11-02 14:12:34.567 +07 [7672] postgres@gridcare app=app_C client=[local] LOG:  process 7672 still waiting for AccessShareLock on relation 16384 of database 16389 after 1000.456 ms
```

### ตัวอย่างที่ 3: pgBadger Report

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

## 12. สรุปย่อ จำง่าย
- **`log_line_prefix` ต้องมี:** Timestamp, PID, User, DB, App, Client  
- **`log_min_duration_statement = 500ms`**  
- **`log_lock_waits = on`**  
- **`log_temp_files = 0`**  
- **`log_checkpoints = on`**  
- **`log_autovacuum_min_duration = 10s`**  
- **`log_statement = 'ddl'`**  
- **`lc_messages = 'C'`**  
- **`log_timezone = 'Asia/Bangkok'`**  
- **pgBadger + logrotate**

ประโยคจำ: **“Log ที่ดีทำให้ S troubleshooting เร็วขึ้น Log ที่แย่ทำให้ Disk เต็ม”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — Error Reporting and Logging: https://www.postgresql.org/docs/17/runtime-config-logging.html
- pgBadger: https://pgbadger.darold.net/
- GridCare Workshop Day 1: Lab 3.4, Day 4: Lab 4.2

---

# บทที่ 18 ความปลอดภัยเบื้องต้น: SCRAM, TLS และ pg_hba

## 1. เรื่อง
การตั้งค่าความปลอดภัยเบื้องต้นของ PostgreSQL ครอบคลุม SCRAM, TLS, pg_hba และหลักการ Least Privilege

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้การเชื่อมต่อฐานข้อมูลเข้ารหัสด้วย TLS  
2. เพื่อให้ Password ใช้ SCRAM ไม่ใช่ MD5  
3. เพื่อให้ pg_hba ถูกต้องและตรวจสอบได้  
4. เพื่อให้เข้าใจหลักการ Least Privilege

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- สร้าง Self-signed Certificate สำหรับ TLS  
- ตั้ง `ssl = on` และ `ssl_min_protocol_version`  
- ตั้ง `password_encryption = scram-sha-256`  
- เขียน `pg_hba.conf` ที่ใช้ `hostssl`  
- ตรวจสอบด้วย `pg_hba_file_rules` และ `pg_stat_ssl`

## 4. เนื้อหาโดยย่อ
Security Baseline ประกอบด้วย 3 ส่วน:
1. **Transport Security** — TLS  
2. **Authentication** — SCRAM, pg_hba  
3. **Authorization** — Role, Privilege, Least Privilege

## 5. ประโยชน์ที่ได้รับ
- การเชื่อมต่อถูกเข้ารหัส  
- Password ไม่ถูกดักได้  
- ป้องกันการเชื่อมต่อที่ไม่เข้ารหัส  
- ป้องกัน Brute Force ได้ง่ายขึ้น  
- เป็น Baseline ที่ผ่าน Audit

## 6. ข้อควรระวัง
- **Certificate ต้องมี SAN ที่ตรงกับ Hostname/IP**  
- **`server.key` ต้อง `chmod 600`**  
- **`pg_hba.conf` อ่านบนลงล่าง** บรรทัดแรกที่ตรงถูกใช้  
- **`hostnossl` reject ต้องอยู่ท้ายสุด**  
- **Superuser ไม่ควรใช้กับแอป**

## 7. ข้อดี
- TLS ป้องกันการดักข้อมูล  
- SCRAM ป้องกันการเดา Password  
- pg_hba ควบคุมการเข้าถึงได้  
- Least Privilege ลดความเสียหายเมื่อถูกโจมตี

## 8. ข้อเสีย
- TLS มี Overhead เล็กน้อย  
- SCRAM ต้อง Upgrade Client ที่เก่า  
- pg_hba ต้องดูแลให้ทันสมัย

## 9. ข้อห้าม
- ห้ามใช้ `password_encryption = md5`  
- ห้ามใช้ `trust` กับ Remote Connection  
- ห้าม `host all all 0.0.0.0/0 trust`  
- ห้าม `chmod 644 server.key`  
- ห้ามเปิด `ssl = off` บน Production

## 10. รายละเอียด

### 10.1 สร้าง Self-signed Certificate

```bash
cd /etc/postgresql/17/main
PG1_IP=$(getent hosts pg1 | awk '{print $1}')
sudo openssl req -new -x509 -days 365 -nodes -newkey rsa:3072 \
  -subj "/CN=pg1" -addext "subjectAltName=DNS:pg1,IP:${PG1_IP}" \
  -keyout server.key -out server.crt
sudo chown postgres:postgres server.key server.crt
sudo chmod 600 server.key
sudo openssl x509 -in server.crt -noout -subject -enddate -ext subjectAltName
```

ผลลัพธ์:
```text
subject=CN = pg1
notAfter=Nov  2 11:20:00 2027 GMT
X509v3 Subject Alternative Name: 
    DNS:pg1, IP Address:10.104.0.11
```

### 10.2 ตั้งค่า TLS

ไฟล์ `/etc/postgresql/17/main/conf.d/30-gridcare-ssl.conf`:

```ini
ssl = on
ssl_cert_file = '/etc/postgresql/17/main/server.crt'
ssl_key_file = '/etc/postgresql/17/main/server.key'
ssl_min_protocol_version = 'TLSv1.2'
password_encryption = 'scram-sha-256'
```

```bash
sudo chown postgres:postgres /etc/postgresql/17/main/conf.d/30-gridcare-ssl.conf
```

### 10.3 ตั้ง `pg_hba.conf`

```bash
sudo cp /etc/postgresql/17/main/pg_hba.conf /etc/postgresql/17/main/pg_hba.conf.bak
INFRA_IP=$(getent hosts infra | awk '{print $1}')
```

**ตัวอย่าง `pg_hba.conf`:**

```text
# TYPE     DATABASE   USER                                                 ADDRESS          METHOD
local      all        postgres                                                              peer
local      all        all                                                                   scram-sha-256
hostssl    all        all                                                  127.0.0.1/32     scram-sha-256
hostssl    gridcare   billing_app,callcenter_ro,report_ro,pgbouncer_auth  ${INFRA_IP}/32   scram-sha-256
hostssl    all        dba                                                  ${INFRA_IP}/32   scram-sha-256
hostnossl  all        all                                                  0.0.0.0/0        reject
```

### 10.4 ตรวจสอบก่อน Reload

```sql
SELECT line_number, type, database, user_name, address, auth_method, error
FROM pg_hba_file_rules WHERE line_number > 120 OR error IS NOT NULL;
```

ผลลัพธ์:
```text
 line_number | type     | database  | user_name                            | address      | auth_method  | error
-------------+----------+-----------+--------------------------------------+--------------+--------------+-------
         132 | hostssl  | {gridcare}| {billing_app,callcenter_ro,...}    | 10.104.0.13  | scram-sha-256|
         133 | hostssl  | {all}     | {dba}                                | 10.104.0.13  | scram-sha-256|
         136 | hostnossl| {all}     | {all}                                | 0.0.0.0/0    | reject       |
(3 rows)
```

```sql
SELECT pg_reload_conf();
```

### 10.5 ตรวจสอบ Log

```bash
sudo tail -n 3 /var/log/postgresql/postgresql-17-main.log
```

ผลลัพธ์:
```text
2026-11-02 15:30:12.345 +07 [4363] LOG:  received SIGHUP, reloading configuration files
2026-11-02 15:30:12.567 +07 [4363] LOG:  parameter "ssl" changed to "on"
2026-11-02 15:30:12.789 +07 [4363] LOG:  configuration file "/etc/postgresql/17/main/pg_hba.conf" was reloaded
```

### 10.6 ทดสอบจาก Client

```bash
psql "host=pg1 dbname=gridcare user=billing_app sslmode=require"
```

ผลลัพธ์:
```text
Password for user billing_app: (ใส่รหัส)
psql (17.11)
SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, compression: off)
```

```sql
SELECT ssl, version, cipher FROM pg_stat_ssl WHERE pid = pg_backend_pid();
```

ผลลัพธ์:
```text
 ssl | version |         cipher         
-----+---------+------------------------
 t   | TLSv1.3 | TLS_AES_256_GCM_SHA384
```

```bash
psql "host=pg1 dbname=gridcare user=billing_app sslmode=disable"
```

ผลลัพธ์:
```text
psql: error: FATAL:  pg_hba.conf rejects connection for host "10.104.0.13",
user "billing_app", database "gridcare", no encryption
```

### 10.7 ตาราง Security Baseline

| # | รายการ | ค่า |
|---|---|---|
| 1 | `ssl` | on |
| 2 | `ssl_min_protocol_version` | TLSv1.2 |
| 3 | `password_encryption` | scram-sha-256 |
| 4 | `server.key` | 600 postgres:postgres |
| 5 | `pg_hba.conf` | `hostssl` + `reject` ท้าย |
| 6 | `listen_addresses` | จำกัด |
| 7 | Superuser | ไม่ใช้กับแอป |
| 8 | Firewall | จำกัด CIDR |
| 9 | Audit Log | pgAudit |
| 10 | Password Rotation | ตามนโยบาย |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: สร้าง Certificate หลายเครื่อง

```bash
# pg1
PG1_IP=$(getent hosts pg1 | awk '{print $1}')
sudo openssl req -new -x509 -days 365 -nodes -newkey rsa:3072 \
  -subj "/CN=pg1" -addext "subjectAltName=DNS:pg1,IP:${PG1_IP}" \
  -keyout /etc/postgresql/17/main/server.key \
  -out /etc/postgresql/17/main/server.crt

# pg2
PG2_IP=$(getent hosts pg2 | awk '{print $1}')
sudo openssl req -new -x509 -days 365 -nodes -newkey rsa:3072 \
  -subj "/CN=pg2" -addext "subjectAltName=DNS:pg2,IP:${PG2_IP}" \
  -keyout /etc/postgresql/17/main/server.key \
  -out /etc/postgresql/17/main/server.crt
```

### ตัวอย่างที่ 2: ดูว่า Connection ปัจจุบันใช้ TLS

```sql
SELECT usename, ssl, version, cipher, client_addr
FROM pg_stat_ssl AS s JOIN pg_stat_activity AS a ON a.pid = s.pid
WHERE a.datname = 'gridcare';
```

### ตัวอย่างที่ 3: ตรวจสอบ Certificate วันหมดอายุ

```bash
sudo openssl x509 -in /etc/postgresql/17/main/server.crt -noout -enddate
```

ผลลัพธ์:
```text
notAfter=Nov  2 11:20:00 2027 GMT
```

## 12. สรุปย่อ จำง่าย
- **TLS = on** + `ssl_min_protocol_version = TLSv1.2`  
- **SCRAM = scram-sha-256**  
- **pg_hba: hostssl + reject ท้าย**  
- **Certificate ต้องมี SAN**  
- **`server.key` ต้อง 600**  
- **ตรวจด้วย `pg_hba_file_rules` และ `pg_stat_ssl`**  
- **Least Privilege**

ประโยคจำ: **“TLS + SCRAM + hostssl = Baseline ที่ต้องมี”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — SSL Support: https://www.postgresql.org/docs/17/ssl-tcp.html
- PostgreSQL Documentation — pg_hba.conf: https://www.postgresql.org/docs/17/auth-pg-hba-conf.html
- PostgreSQL Documentation — SCRAM: https://www.postgresql.org/docs/17/sasl-authentication.html
- GridCare Workshop Day 1: ขั้นที่ 2 (TLS)

---

# บทที่ 19 Role, Privilege และ Timeout

## 1. เรื่อง
การออกแบบ Role, Privilege และ Timeout ใน PostgreSQL Production

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจการออกแบบ Group Role และ Login Role  
2. เพื่อให้ตั้ง Timeout ต่อ Role ได้  
3. เพื่อให้เข้าใจ Predefined Role ของ PostgreSQL  
4. เพื่อให้ทำตามหลัก Least Privilege

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ออกแบบ Role Hierarchy  
- ใช้ Group Role และ Login Role  
- ตั้ง Timeout ต่อ Role  
- ใช้ Predefined Role เช่น `pg_monitor`, `pg_read_all_data`  
- ตรวจสอบสิทธิ์ด้วย `has_*_privilege` และ `pg_db_role_setting`

## 4. เนื้อหาโดยย่อ
Role ใน PostgreSQL มี 2 ประเภท:
- **Group Role** — `NOLOGIN` ทำหน้าที่รวมสิทธิ์  
- **Login Role** — `LOGIN` ใช้เชื่อมต่อ

Predefined Role ที่ควรรู้:
- `pg_monitor` — Monitoring  
- `pg_read_all_data` — อ่านทุก Data  
- `pg_read_all_settings` — อ่าน Config  
- `pg_signal_backend` — ส่งสัญญาณไปที่ Backend  
- `pg_maintain` — Maintenance  
- `pg_use_reserved_connections` — ใช้ Reserved Connections

## 5. ประโยชน์ที่ได้รับ
- ลดความซ้ำซ้อนในการให้สิทธิ์  
- ลดความเสี่ยงจากการให้ Superuser  
- Timeout ช่วยป้องกัน Query ที่ค้าง  
- ตรวจสอบสิทธิ์ได้  
- ผ่าน Audit ด้าน Least Privilege

## 6. ข้อควรระวัง
- **`SET ROLE` ไม่โหลดค่า `ALTER ROLE SET`** — ต้อง Login ใหม่ผ่าน TCP  
- **Group Role ต้องเป็น `NOLOGIN`**  
- **`REVOKE CREATE ON SCHEMA public FROM PUBLIC`** จำเป็นสำหรับ Production  
- **`default_transaction_read_only = on`** ใช้กับ Report Role  
- **`idle_in_transaction_session_timeout`** ต้องตั้งเสมอ

## 7. ข้อดี
- ลดความซ้ำซ้อน  
- ตรวจสอบง่าย  
- ลดความเสี่ยง  
- ทำให้ Onboarding User ใหม่เร็ว

## 8. ข้อเสีย
- ต้องออกแบบก่อนสร้าง  
- Role Hierarchy ที่ซับซ้อนเกินไปทำให้สับสน

## 9. ข้อห้าม
- ห้ามใช้ Superuser กับแอป  
- ห้าม `GRANT ALL ON DATABASE ... TO PUBLIC`  
- ห้ามให้ Role ที่ไม่ใช่ DBA มี `CREATEROLE`  
- ห้ามใช้ Role เดียวสำหรับทุกงาน  
- ห้ามลบ Role ที่ยังมี Object เป็นเจ้าของ

## 10. รายละเอียด

### 10.1 Group Role

```sql
CREATE ROLE gridcare_read NOLOGIN;
GRANT CONNECT ON DATABASE gridcare TO gridcare_read;
GRANT USAGE ON SCHEMA gridcare TO gridcare_read;
GRANT SELECT ON ALL TABLES IN SCHEMA gridcare TO gridcare_read;
ALTER DEFAULT PRIVILEGES IN SCHEMA gridcare GRANT SELECT ON TABLES TO gridcare_read;

CREATE ROLE gridcare_write NOLOGIN IN ROLE gridcare_read;
GRANT INSERT ON gridcare.meter_readings, gridcare.outage_events, gridcare.work_orders,
                gridcare.payments, gridcare.sms_notifications, gridcare.bills TO gridcare_write;
GRANT UPDATE ON gridcare.bills TO gridcare_write;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA gridcare TO gridcare_write;
ALTER DEFAULT PRIVILEGES IN SCHEMA gridcare GRANT USAGE ON SEQUENCES TO gridcare_write;
```

### 10.2 Login Role

```sql
CREATE ROLE billing_app   LOGIN PASSWORD 'Lab-Billing-2569'    IN ROLE gridcare_write;
CREATE ROLE callcenter_ro LOGIN PASSWORD 'Lab-CallCenter-2569' IN ROLE gridcare_read;
CREATE ROLE report_ro     LOGIN PASSWORD 'Lab-Report-2569'     IN ROLE gridcare_read;
CREATE ROLE dba           LOGIN CREATEROLE PASSWORD 'Lab-Dba-2569'
  IN ROLE pg_maintain, pg_monitor, pg_signal_backend, pg_use_reserved_connections;
GRANT gridcare_read TO dba;
CREATE ROLE pgbouncer_auth LOGIN PASSWORD 'Lab-PgbAuth-2569';
GRANT CONNECT ON DATABASE gridcare TO pgbouncer_auth;
```

### 10.3 Timeout ต่อ Role

```sql
ALTER ROLE billing_app SET lock_timeout = '3s';
ALTER ROLE billing_app SET statement_timeout = '30s';
ALTER ROLE billing_app SET idle_in_transaction_session_timeout = '60s';
ALTER ROLE billing_app SET transaction_timeout = '5min';

ALTER ROLE callcenter_ro SET statement_timeout = '5s';
ALTER ROLE callcenter_ro SET idle_in_transaction_session_timeout = '30s';
ALTER ROLE callcenter_ro SET default_transaction_read_only = on;

ALTER ROLE report_ro SET statement_timeout = '5min';
ALTER ROLE report_ro SET default_transaction_read_only = on;
ALTER ROLE report_ro SET work_mem = '64MB';

ALTER ROLE dba SET lock_timeout = '5s';
```

### 10.4 ปิดสิทธิ์ PUBLIC

```sql
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON DATABASE gridcare FROM PUBLIC;
```

### 10.5 ตรวจสอบสิทธิ์

```sql
SELECT r.rolname, s.setconfig
FROM pg_db_role_setting AS s JOIN pg_roles AS r ON r.oid = s.setrole
ORDER BY 1;
```

ผลลัพธ์:
```text
   rolname    |                                  setconfig                                   
--------------+------------------------------------------------------------------------------
 billing_app  | {lock_timeout=3s,statement_timeout=30s,idle_in_transaction_session_timeout=60s,transaction_timeout=5min}
 callcenter_ro| {statement_timeout=5s,idle_in_transaction_session_timeout=30s,default_transaction_read_only=on}
 dba          | {lock_timeout=5s}
 report_ro    | {statement_timeout=5min,default_transaction_read_only=on,work_mem=64MB}
(4 rows)
```

```sql
SELECT has_table_privilege('callcenter_ro', 'gridcare.customers', 'SELECT') AS cc_select,
       has_table_privilege('callcenter_ro', 'gridcare.bills', 'UPDATE')     AS cc_update,
       has_table_privilege('billing_app', 'gridcare.bills', 'UPDATE')       AS app_update,
       has_database_privilege('pgbouncer_auth', 'gridcare', 'CONNECT')      AS pgb_connect;
```

ผลลัพธ์:
```text
 cc_select | cc_update | app_update | pgb_connect 
-----------+-----------+------------+-------------
 t         | f         | t          | t
```

### 10.6 Predefined Role

| Predefined Role | ใช้กับ |
|---|---|
| `pg_monitor` | Monitoring เช่น postgres_exporter |
| `pg_read_all_data` | อ่านทุก Data |
| `pg_read_all_settings` | อ่าน Config |
| `pg_read_all_stats` | อ่าน Statistics |
| `pg_signal_backend` | ส่งสัญญาณไปที่ Backend |
| `pg_maintain` | VACUUM, ANALYZE |
| `pg_use_reserved_connections` | ใช้ Reserved Connections |

### 10.7 ตาราง Timeout ที่แนะนำ

| Role | lock_timeout | statement_timeout | idle_in_tx | transaction_timeout | read_only |
|---|---|---|---|---|---|
| billing_app | 3s | 30s | 60s | 5min | ❌ |
| callcenter_ro | default | 5s | 30s | default | ✅ |
| report_ro | default | 5min | default | default | ✅ |
| dba | 5s | default | default | default | ❌ |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: สร้าง Role ใหม่ที่ใช้ Group Role

```sql
CREATE ROLE new_report LOGIN PASSWORD 'Lab-NewReport-2569' IN ROLE gridcare_read;
ALTER ROLE new_report SET statement_timeout = '5min';
ALTER ROLE new_report SET default_transaction_read_only = on;
```

### ตัวอย่างที่ 2: ตรวจสอบว่า Login ใหม่ได้ Timeout ที่ถูกต้อง

```bash
psql "host=pg1 dbname=gridcare user=billing_app sslmode=require"
```

```sql
SHOW transaction_timeout;
SHOW statement_timeout;
SHOW lock_timeout;
```

ผลลัพธ์:
```text
 transaction_timeout 
---------------------
 5min

 statement_timeout 
-------------------
 30s

 lock_timeout 
--------------
 3s
```

### ตัวอย่างที่ 3: `SET ROLE` ไม่โหลดค่า `ALTER ROLE SET`

```sql
SET ROLE billing_app;
SELECT 'transaction_timeout=' || current_setting('transaction_timeout') AS result;
RESET ROLE;
```

ผลลัพธ์:
```text
       result        
---------------------
 transaction_timeout=0
```

> ⚠️ `SET ROLE` ไม่โหลดค่า `ALTER ROLE SET` — ต้อง Login ใหม่ผ่าน TCP

## 12. สรุปย่อ จำง่าย
- **Group Role (`NOLOGIN`) + Login Role** คือ Pattern หลัก  
- **`ALTER DEFAULT PRIVILEGES`** สำหรับตารางในอนาคต  
- **`ALTER ROLE SET`** ตั้ง Timeout ต่อ Role  
- **`REVOKE ... FROM PUBLIC`** จำเป็นสำหรับ Production  
- **Predefined Role** ช่วยลดการ GRANT ซ้ำ  
- **`SET ROLE` ไม่โหลด `ALTER ROLE SET`**

ประโยคจำ: **“สิทธิ์ให้น้อยที่สุด Timeout ให้สั้นที่สุด”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — CREATE ROLE: https://www.postgresql.org/docs/17/sql-createrole.html
- PostgreSQL Documentation — GRANT: https://www.postgresql.org/docs/17/sql-grant.html
- PostgreSQL Documentation — Predefined Roles: https://www.postgresql.org/docs/17/predefined-roles.html
- GridCare Workshop Day 1: ขั้นที่ 1

---

# บทที่ 20 Checklist หลังติดตั้ง

## 1. เรื่อง
Checklist ตรวจสอบระบบ PostgreSQL หลังติดตั้ง ก่อนส่งมอบให้ใช้งาน Production

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้มี Checklist มาตรฐานสำหรับตรวจหลังติดตั้ง  
2. เพื่อให้มั่นใจว่าระบบพร้อม Production  
3. เพื่อใช้เป็น Evidence สำหรับ Audit  
4. เพื่อใช้เป็น Runbook สำหรับทีมใหม่

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ตรวจสอบ Version, Checksums, Config  
- ตรวจสอบ Role, TLS, pg_hba  
- ตรวจสอบ Backup, Monitoring, Alert  
- สร้าง Baseline Evidence

## 4. เนื้อหาโดยย่อ
Checklist แบ่งเป็น 8 หมวด:
1. Version และ Cluster  
2. Configuration และ Checksums  
3. Authentication และ Authorization  
4. Security และ TLS  
5. Logging และ Rotation  
6. Backup และ Recovery  
7. Monitoring และ Alert  
8. Documentation และ Handover

## 5. ประโยชน์ที่ได้รับ
- ลดความเสี่ยงจากการลืมขั้นตอน  
- มี Evidence สำหรับ Audit  
- ทำให้ Onboarding ทีมใหม่เร็ว  
- ทำให้ Incident Response มี Baseline

## 6. ข้อควรระวัง
- **Checklist ที่ไม่มี Evidence** ไม่มีคุณค่า  
- **Checklist ที่ไม่ Reviewed** จะเก่า  
- **Checklist ที่ยาวเกินไป** จะไม่มีคนทำ

## 7. ข้อดี
- มาตรฐานเดียวกันทั้งองค์กร  
- ลด Incident จากความลืม  
- เป็น Evidence

## 8. ข้อเสีย
- ต้อง Maintain  
- ต้อง Review เป็นระยะ

## 9. ข้อห้าม
- ห้าม Skip Checklist บน Production  
- ห้ามใช้ Checklist ที่ไม่มีวันที่  
- ห้ามใช้ Checklist ที่ไม่มีผู้อนุมัติ

## 10. รายละเอียด

### 10.1 หมวด 1: Version และ Cluster

```bash
pg_lsclusters
sudo -u postgres psql -c "SELECT version()"
```

เกณฑ์ผ่าน:
- PostgreSQL 17.11+ หรือ 18.6+
- Cluster online
- ไม่มี Error ใน Status

### 10.2 หมวด 2: Configuration และ Checksums

```sql
SHOW data_checksums;
SHOW password_encryption;
SHOW shared_buffers;
SHOW max_connections;
SHOW config_file;
SELECT sourcefile, name, error FROM pg_file_settings WHERE error IS NOT NULL;
```

เกณฑ์ผ่าน:
- `data_checksums = on`
- `password_encryption = scram-sha-256`
- `pg_file_settings` ไม่มี Error
- `pending_restart = false` ทั้งหมด

### 10.3 หมวด 3: Authentication และ Authorization

```sql
SELECT line_number, type, database, user_name, address, auth_method, error
FROM pg_hba_file_rules WHERE error IS NOT NULL;
\du
SELECT r.rolname, s.setconfig FROM pg_db_role_setting AS s JOIN pg_roles AS r ON r.oid = s.setrole;
```

เกณฑ์ผ่าน:
- `pg_hba_file_rules` ไม่มี Error
- Role มี Timeout
- ไม่มี Role ที่ใช้ Superuser เกินจำเป็น
- PUBLIC ถูก REVOKE

### 10.4 หมวด 4: Security และ TLS

```sql
SELECT ssl, version, cipher FROM pg_stat_ssl WHERE pid = pg_backend_pid();
```

```bash
sudo openssl x509 -in /etc/postgresql/17/main/server.crt -noout -subject -enddate
sudo ls -la /etc/postgresql/17/main/server.key
```

เกณฑ์ผ่าน:
- `ssl = t`, `TLSv1.2` ขึ้นไป
- `server.key` เป็น `600 postgres:postgres`
- Certificate ยังไม่หมดอายุ

### 10.5 หมวด 5: Logging และ Rotation

```bash
sudo grep -E "log_line_prefix|log_min_duration|log_lock_waits|log_statement" \
  /etc/postgresql/17/main/conf.d/*.conf
sudo logrotate -d /etc/logrotate.d/postgresql-common
```

เกณฑ์ผ่าน:
- `log_line_prefix` มี `%m %p %q%u@%d app=%a client=%h`
- `log_min_duration_statement = 500ms`
- `log_statement = 'ddl'`
- `lc_messages = 'C'`
- Logrotate ผ่าน

### 10.6 หมวด 6: Backup และ Recovery

```bash
sudo -u postgres pgbackrest --stanza=gridcare check
sudo -u postgres pgbackrest --stanza=gridcare info
sudo -u postgres psql -c "SELECT failed_count FROM pg_stat_archiver"
```

เกณฑ์ผ่าน:
- `check` ผ่าน
- มี Full Backup อย่างน้อย 1 ชุด
- `failed_count = 0`
- Restore Test ผ่าน

### 10.7 หมวด 7: Monitoring และ Alert

```bash
curl -s localhost:9187/metrics | grep -E '^pg_up'
curl -s localhost:9090/api/v1/targets | grep -E '"health"'
promtool check rules /etc/prometheus/rules/*.yml
amtool check-config /etc/prometheus/alertmanager.yml
```

เกณฑ์ผ่าน:
- `pg_up 1`
- Target `health: up` ทั้งหมด
- Rule ผ่าน `promtool check rules`
- Alertmanager Config ผ่าน `amtool check-config`

### 10.8 หมวด 8: Documentation และ Handover

| # | รายการ | เกณฑ์ผ่าน |
|---|---|---|
| 1 | Runbook ทุก Alert | 100% |
| 2 | Incident Record Template | มี |
| 3 | Backup/Restore Procedure | มี |
| 4 | HA Procedure | มี |
| 5 | Upgrade Plan | มี |
| 6 | On-call Rotation | มี |
| 7 | Contact List | มี |
| 8 | Credential ใน Secret Manager | มี |
| 9 | Change Log | มี |
| 10 | KPI/SLO | มี |

### 10.9 ตารางสรุป Checklist หลังติดตั้ง

| # | หมวด | รายการ | เกณฑ์ผ่าน |
|---|---|---|---|
| 1 | Version | `pg_lsclusters` | online |
| 2 | Config | `pg_file_settings` | ไม่มี Error |
| 3 | Config | `pending_restart` | ไม่มี |
| 4 | Checksums | `data_checksums` | on |
| 5 | Auth | `pg_hba_file_rules` | ไม่มี Error |
| 6 | Auth | `password_encryption` | scram-sha-256 |
| 7 | TLS | `pg_stat_ssl` | ssl = t |
| 8 | TLS | Certificate | ไม่หมดอายุ |
| 9 | Logging | `log_line_prefix` | ครบ |
| 10 | Logging | Logrotate | ผ่าน |
| 11 | Backup | `pgbackrest check` | ผ่าน |
| 12 | Backup | Restore Test | ผ่าน |
| 13 | Monitoring | `pg_up` | 1 |
| 14 | Monitoring | Target `health` | up |
| 15 | Alert | `promtool check rules` | ผ่าน |
| 16 | Alert | `amtool check-config` | ผ่าน |
| 17 | Doc | Runbook | 100% |
| 18 | Doc | Incident Template | มี |
| 19 | Doc | Upgrade Plan | มี |
| 20 | Doc | KPI/SLO | มี |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Script ตรวจ Checklist อัตโนมัติ

```bash
#!/usr/bin/env bash
set -e

echo "=== 1. Version ==="
pg_lsclusters

echo "=== 2. Config ==="
sudo -u postgres psql -At -c "SELECT current_setting('data_checksums'), current_setting('password_encryption'), current_setting('shared_buffers')"

echo "=== 3. Errors ==="
sudo -u postgres psql -At -c "SELECT count(*) FROM pg_file_settings WHERE error IS NOT NULL"
sudo -u postgres psql -At -c "SELECT count(*) FROM pg_hba_file_rules WHERE error IS NOT NULL"

echo "=== 4. Pending Restart ==="
sudo -u postgres psql -At -c "SELECT count(*) FROM pg_settings WHERE pending_restart"

echo "=== 5. TLS ==="
sudo -u postgres psql -At -c "SELECT ssl, version FROM pg_stat_ssl WHERE pid = pg_backend_pid()"

echo "=== 6. Backup ==="
sudo -u postgres pgbackrest --stanza=gridcare check || echo "BACKUP CHECK FAILED"

echo "=== 7. Monitoring ==="
curl -s localhost:9187/metrics | grep '^pg_up'
```

### ตัวอย่างที่ 2: Evidence File

```text
Checklist PostgreSQL 17 Production
Version: PostgreSQL 17.11
Date: 2026-11-02
Tester: DBA Team

[✓] Version: 17.11
[✓] Cluster: 17/main online
[✓] data_checksums: on
[✓] password_encryption: scram-sha-256
[✓] pg_file_settings errors: 0
[✓] pg_hba_file_rules errors: 0
[✓] pending_restart: 0
[✓] pg_stat_ssl: TLSv1.3
[✓] Certificate expires: 2027-11-02
[✓] pgbackrest check: ok
[✓] Full Backup: 20261102-110000F
[✓] pg_up: 1
[✓] Targets health: up
[✓] promtool check rules: SUCCESS
[✓] amtool check-config: SUCCESS
[✓] Runbook: 23 Alert
[✓] Incident Template: มี
[✓] Upgrade Plan: มี
[✓] KPI/SLO: มี

Approved by: ______________  Date: ______________
```

### ตัวอย่างที่ 3: ตรวจสอบหลัง Upgrade

```bash
# หลัง Upgrade 17 → 18
patronictl list
sudo -u postgres psql -X -d gridcare -Atc "SELECT version()" -c "SHOW data_checksums" \
  -c "SELECT extname || ' ' || extversion FROM pg_extension ORDER BY 1" \
  -c "SELECT statistics_name FROM pg_stats_ext" -c "SELECT count(*) FROM gridcare.bills"
```

ผลลัพธ์:
```text
PostgreSQL 18.6 (Ubuntu 18.6-1.pgdg24.04+2) ...
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

## 12. สรุปย่อ จำง่าย
- **8 หมวดของ Checklist**  
- **Version, Config, Checksums, Auth, TLS, Logging, Backup, Monitoring, Doc**  
- **ทุกข้อต้องมี Evidence**  
- **ทุกข้อต้องมีผู้อนุมัติ**  
- **ทุกข้อต้องมีวันที่**  
- **Checklist ต้อง Reviewed ทุกปี**

ประโยคจำ: **“Checklist ที่ดีคือ Checklist ที่มี Evidence และมีผู้อนุมัติ”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — Security: https://www.postgresql.org/docs/17/security.html
- CIS PostgreSQL Benchmark: https://www.cisecurity.org/benchmark/postgresql
- Google SRE Book: https://sre.google/sre-book/
- GridCare Workshop: `scripts/health_check.sh`, `scripts/restore_test.sh`, `monitoring/runbooks/`

---

## สรุปส่วนที่ 2 (บทที่ 11–20)

| บท | แก่นของบท | ใช้ต่อในส่วน |
|---|---|---|
| 11 | Linux Baseline: Kernel, ulimit, Timezone, THP, Swap | ทุกส่วน |
| 12 | ติดตั้ง PostgreSQL 17/18 + PGDG + Checksums + Security | Performance, HA |
| 13 | Data Checksums: ตั้ง ตรวจ แก้ | Backup, Restore |
| 14 | PGDATA + Config File + Parameter สำคัญ | Performance |
| 15 | Tuning Baseline ตามขนาดเครื่อง | Performance, Monitoring |
| 16 | จัดการ Cluster ด้วย pg_lsclusters และ systemd | Operations, Upgrade |
| 17 | Logging มาตรฐาน + pgBadger + logrotate | S troubleshooting |
| 18 | TLS + SCRAM + pg_hba | Security, HA |
| 19 | Role + Privilege + Timeout | Security, RLS |
| 20 | Checklist หลังติดตั้ง | Handover, Upgrade |

---
 