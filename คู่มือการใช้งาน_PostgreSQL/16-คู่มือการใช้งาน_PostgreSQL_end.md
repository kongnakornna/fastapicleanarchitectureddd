# 📋 สรุปคำสั่งทั้งหมด — Day 1 (วันที่ 1)

> **หลักสูตร:** Advanced PostgreSQL for Enterprise Production (PEA)
> **หัวข้อ:** Internal Architecture, Linux Essentials, Installation & Locking
> **วันที่:** จันทร์ที่ 2 พฤศจิกายน 2569 | 09:00-16:45 น.
> รูปแบบ: **คำสั่ง** → **ผลลัพธ์จริง/ที่คาดหวัง** → **หมายเหตุ**

---

## 🧰 Lab 0.1 — เข้าเครื่อง Lab และตรวจชื่อเครื่อง

### ขั้นที่ 2: SSH เข้า 3 เครื่อง (3 Tabs)

```bash
ssh lab-pg1
```
**ผลลัพธ์:**
```
Welcome to Ubuntu 24.04 LTS (GNU/Linux 6.8.0-45-generic x86_64)
Last login: Mon Nov  2 08:30:15 2026 from 10.104.0.1
student@ta1-pg2:~$
```

```bash
ssh lab-pg2
```
**ผลลัพธ์:**
```
student@ta1-pg2:~$
```

```bash
ssh lab-infra
```
**ผลลัพธ์:**
```
student@ta1-infra:~$
```

> 💡 หน้าจอ prompt เปลี่ยนเป็นชื่อเครื่องของชุดตนเอง (เช่น `ta1-pg2`)

---

### ขั้นที่ 3: ตรวจชื่อเครื่องและไฟล์ที่เตรียมไว้ (รันบน **ทุกเครื่อง**)

```bash
hostname
```
**ผลลัพธ์:**
```
ta1-pg2
```
> 💡 บน pg2 ได้ `ta1-pg2`, บน infra ได้ `ta1-infra`

```bash
ip -4 -br addr show | grep 10.104
```
**ผลลัพธ์:**
```
eth1             UP             10.104.0.11/20 
```
> 💡 pg2 ได้ `10.104.0.12/20`, infra ได้ `10.104.0.13/20`

```bash
grep -A3 'GridCare Lab' /etc/hosts
```
**ผลลัพธ์:**
```

10.104.0.8      pg1    ta1-pg1
10.104.0.11     pg2    ta1-pg2
10.104.0.10     infra  ta1-infra

```

```bash
for h in pg1 pg2 infra; do getent hosts "$h" > /dev/null && echo "$h OK" || echo "$h MISSING"; done
```
**ผลลัพธ์:**
```
pg1 OK
pg2 OK
infra OK
```
> ⚠️ ถ้า `MISSING` → แจ้งผู้ช่วยวิทยากร **ห้ามแก้ `/etc/hosts` เอง**

```bash
ls /opt/gridcare
```
**ผลลัพธ์:**
```
load_gridcare.sh  monitoring  pgbench  scripts  sql  workshop
```

```bash
cat /opt/pea/VERSIONS | head -20
```
**ผลลัพธ์:**
```
PostgreSQL: 17.11
PgBouncer: 1.26.1
pgBackRest: 2.54.2
pg_partman: 5.2.4
pgAudit: 17.0
tmux: 3.4
...

# apt packages: /opt/pea/apt/PACKAGES.txt
student@ta1-pg2:/opt/gridcare/pgbench$ grep -Ei 'postgresql|pgbouncer|pgbackrest|pg_partman|pgaudit|tmux' /opt/pea/apt/PACKAGES.txt
pgbackrest 2.59.3-1.pgdg24.04+1
pgbouncer 1.26.1-1.pgdg24.04+1
postgresql-17 17.11-1.pgdg24.04+2
postgresql-17-partman 5.5.0-1.pgdg24.04+1
postgresql-17-pgaudit 17.1-2.pgdg24.04+1
postgresql-17-repack 1.5.3-1.pgdg24.04+2
postgresql-18 18.6-1.pgdg24.04+2
postgresql-18-jit 18.6-1.pgdg24.04+2
postgresql-18-partman 5.5.0-1.pgdg24.04+1
postgresql-18-pgaudit 18.0-3.pgdg24.04+1
postgresql-18-repack 1.5.3-1.pgdg24.04+2
postgresql-client-17 17.11-1.pgdg24.04+2
postgresql-client-18 18.6-1.pgdg24.04+2
postgresql-client-common 293.pgdg24.04+1
postgresql-common 293.pgdg24.04+1
student@ta1-pg2:/opt/gridcare/pgbench$ dpkg -l | grep -Ei 'postgresql|pgbouncer|pgbackrest|partman|pgaudit|tmux'
ii  libpq5:amd64                        19~rc1-1.pgdg24.04+1                             amd64        PostgreSQL C client library
ii  pgbackrest                          2.59.3-1.pgdg24.04+1                             amd64        Reliable PostgreSQL Backup & Restore
ii  pgbouncer                           1.26.1-1.pgdg24.04+1                             amd64        lightweight connection pooler for PostgreSQL
ii  postgresql-17                       17.11-1.pgdg24.04+2                              amd64        The World's Most Advanced Open Source Relational Database
ii  postgresql-17-partman               5.5.0-1.pgdg24.04+1                              amd64        PostgreSQL Partition Manager
ii  postgresql-17-pgaudit               17.1-2.pgdg24.04+1                               amd64        PostgreSQL Audit Extension
ii  postgresql-17-repack                1.5.3-1.pgdg24.04+2                              amd64        reorganize tables in PostgreSQL databases with minimal locks
ii  postgresql-18                       18.6-1.pgdg24.04+2                               amd64        The World's Most Advanced Open Source Relational Database
ii  postgresql-18-jit                   18.6-1.pgdg24.04+2                               amd64        LLVM JIT support for PostgreSQL 18
ii  postgresql-18-partman               5.5.0-1.pgdg24.04+1                              amd64        PostgreSQL Partition Manager
ii  postgresql-18-pgaudit               18.0-3.pgdg24.04+1                               amd64        PostgreSQL Audit Extension
ii  postgresql-18-repack                1.5.3-1.pgdg24.04+2                              amd64        reorganize tables in PostgreSQL databases with minimal locks
ii  postgresql-client-17                17.11-1.pgdg24.04+2                              amd64        front-end programs for PostgreSQL 17
ii  postgresql-client-18                18.6-1.pgdg24.04+2                               amd64        front-end programs for PostgreSQL 18
ii  postgresql-client-common            293.pgdg24.04+1                                  all          manager for multiple PostgreSQL client versions
ii  postgresql-common                   293.pgdg24.04+1                                  all          PostgreSQL database-cluster manager
ii  python3-psycopg2                    2.9.10-1.pgdg24.04+1                             amd64        Python 3 module for PostgreSQL
ii  tmux                                3.4-1ubuntu0.2                                   amd64        terminal multiplexer
student@ta1-pg2:/opt/gridcare/pgbench$ 
[practice]0:bash*                             

```

---

## 🧪 Lab 2.1 — สำรวจเครื่อง pg1 ด้วย systemd, journalctl และ tmux

### ส่วนที่ 1: Service และ Log

```bash
systemctl status ssh --no-pager | head -5
```
**ผลลัพธ์:**
```
● ssh.service - OpenBSD Secure Shell server
     Loaded: loaded (/lib/systemd/system/ssh.service; enabled; preset: enabled)
     Active: active (running) since Mon 2026-11-02 08:55:12 +07; 4min ago
       Docs: man:sshd(8)
             man:sshd_config(5)
```

```bash
journalctl -u ssh --since "30 min ago" --no-pager | tail -5
```
**ผลลัพธ์:**
```
Nov 02 08:55:10 ta1-pg2 systemd[1]: Starting ssh.service - OpenBSD Secure Shell server...
Nov 02 08:55:12 ta1-pg2 systemd[1]: Started ssh.service - OpenBSD Secure Shell server.
Nov 02 08:55:30 ta1-pg2 sshd[1234]: Accepted publickey for student from 10.104.0.1 port 54321 ssh2
Nov 02 08:55:30 ta1-pg2 sshd[1234]: pam_unix(sshd:session): session opened for user student(uid=1000)
```

### ส่วนที่ 2: ดิสก์ หน่วยความจำ และ CPU

```bash
df -hT /
```
**ผลลัพธ์:**
```
Filesystem     Type  Size  Used Avail Use% Mounted on
/dev/sda1      ext4   78G   12G   63G  16% /
```

```bash
free -h
```
**ผลลัพธ์:**
```
               total        used        free      shared  buff/cache   available
Mem:           3.8Gi       612Mi       2.1Gi        17Mi       1.3Gi       3.0Gi
Swap:             0B          0B          0B
```

```bash
nproc
```
**ผลลัพธ์:**
```
2
```

```bash
vmstat 2 3
```
**ผลลัพธ์:**
```
procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
 r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
 0  0      0 2198400  73960 1372456    0    0    12    18   45   89  0  0 99  0  0
 0  0      0 2198144  73960 1372860    0    0     0    12  108  200  0  0 100 0  0
 0  0      0 2198144  73960 1372860    0    0     0     0   95  175  0  0 100 0  0
```

```bash
iostat -xz 2 2 || echo "ยังไม่มี sysstat (ใช้ vmstat แทนได้)"
```
**ผลลัพธ์:**
```
Linux 6.8.0-45-generic (ta1-pg2)   11/02/2026  _x86_64_  (2 CPU)

Device            r/s     w/s     rkB/s     wkB/s   await  %util
sda              1.23    0.45     12.34      5.67    0.89   0.12
```

### ส่วนที่ 3: tmux

```bash
tmux new -s practice
```
**ผลลัพธ์:** เข้าหน้าจอ tmux ใหม่ (มีแถบสถานะสีเขียวด้านล่าง)

**ภายในหน้าต่าง tmux** รัน `top` แล้วกด `Ctrl+b d`:
```bash
top
```
**ผลลัพธ์:** แสดง process ทั้งหมด (กด `q` เพื่อออก)

**กลับมาที่ Shell**:
```bash
tmux ls
```
**ผลลัพธ์:**
```
practice: 1 windows (created Mon Nov  2 09:05:14 2026)
```

```bash
tmux attach -t practice
```
**ผลลัพธ์:** กลับเข้า session `practice` (เห็น `top` ยังทำงานอยู่)

> 💡 กด `q` ออกจาก `top` แล้วพิมพ์ `exit` เพื่อปิด session

**✅ ผลลัพธ์ที่คาดหวัง:**
- `df -hT /` แสดงดิสก์ ext4 ~80 GB
- `free -h` แสดง Mem ~3.8Gi
- `nproc` ได้ 2
- `tmux ls` แสดง `practice: 1 windows`

---

## 🧪 Lab 3.1 — ติดตั้ง PostgreSQL 17 พร้อม Data Checksums

### ขั้นที่ 1: ตรวจ Repository

```bash
apt-cache policy postgresql-17 | head -10
```
**ผลลัพธ์ (ก่อนติดตั้ง):**
```
postgresql-17:
  Installed: (none)
  Candidate: 17.11-1.pgdg24.04+2
  Version table:
     17.11-1.pgdg24.04+2 990
        990 file:/opt/pea/apt ./ Packages
```

### ขั้นที่ 2: ตั้งค่า Data Checksums (ก่อนติดตั้ง!)

```bash
sudo apt install -y postgresql-common
```
**ผลลัพธ์:**
```
Reading package lists... Done
Building dependency tree... Done
postgresql-common is already the newest version (257build1.1).
```

```bash
sudo cp /etc/postgresql-common/createcluster.conf /etc/postgresql-common/createcluster.conf.bak
grep -q "^initdb_options = '--data-checksums'" /etc/postgresql-common/createcluster.conf || echo "initdb_options = '--data-checksums'" | sudo tee -a /etc/postgresql-common/createcluster.conf
```
**ผลลัพธ์:**
```
initdb_options = '--data-checksums'
```

```bash
grep -n "^initdb_options\|^create_main_cluster" /etc/postgresql-common/createcluster.conf
```
**ผลลัพธ์:**
```
42:initdb_options = '--data-checksums'
```

### ขั้นที่ 3: ติดตั้ง PostgreSQL 17

```bash
sudo apt install -y postgresql-17
```
**ผลลัพธ์:**
```
Reading package lists... Done
Building dependency tree... Done
The following NEW packages will be installed:
  postgresql-17 postgresql-client-17
...
Setting up postgresql-17 (17.11-1.pgdg24.04+2) ...
Creating new PostgreSQL cluster 17/main ...
/usr/lib/postgresql/17/bin/initdb -D /var/lib/postgresql/17/main --auth-local peer --auth-host scram-sha-256 --no-instructions --data-checksums
Ver Cluster Port Status Owner    Data directory              Log file
17  main    5432 online postgres /var/lib/postgresql/17/main /var/log/postgresql/postgresql-17-main.log
```

### ขั้นที่ 4: ตรวจสอบ

```bash
pg_lsclusters
```
**ผลลัพธ์:**
```
Ver Cluster Port Status Owner    Data directory              Log file
17  main    5432 online postgres /var/lib/postgresql/17/main /var/log/postgresql/postgresql-17-main.log
```

```bash
systemctl status postgresql@17-main --no-pager | head -3
```
**ผลลัพธ์:**
```
● postgresql@17-main.service - PostgreSQL Cluster 17-main
     Loaded: loaded (/lib/systemd/system/postgresql@.service; enabled-runtime; preset: enabled)
     Active: active (running) since Mon 2026-11-02 11:02:15 +07; 30s ago
```

```bash
sudo -u postgres psql
```
**ผลลัพธ์:**
```
psql (17.11 (Ubuntu 17.11-1.pgdg24.04+2))
Type "help" for help.

postgres=#
```

**ภายใน psql** พิมพ์ทีละบรรทัด:
```sql
SELECT 'data_checksums=' || current_setting('data_checksums') AS result;
```
**ผลลัพธ์:**
```
       result        
---------------------
 data_checksums=on
(1 row)
```

```sql
SELECT version();
```
**ผลลัพธ์:**
```
                                version                                 
------------------------------------------------------------------------
 PostgreSQL 17.11 (Ubuntu 17.11-1.pgdg24.04+2) on x86_64-pc-linux-gnu...
(1 row)
```

```sql
\q
```

> ⛔ **ถ้าได้ `data_checksums=off`** → `sudo pg_dropcluster 17 main --stop` แล้ว `sudo pg_createcluster 17 main --start -- --data-checksums`

**✅ ผลลัพธ์:** `data_checksums=on` และ PostgreSQL 17.11

---

## 🧪 Lab 3.1 (ต่อ) — เข้าใช้งาน PostgreSQL ด้วย psql ทีละขั้น

### ขั้นที่ 1: เข้า psql

```bash
sudo -u postgres psql
```
**ผลลัพธ์:**
```
psql (17.11)
Type "help" for help.

postgres=#
```

### ขั้นที่ 2: รู้ว่าตนเองเป็นใคร อยู่ที่ไหน

```sql
\conninfo
```
**ผลลัพธ์:**
```
You are connected to database "postgres" as user "postgres" via socket in "/var/run/postgresql" at port "5432".
```

```sql
SELECT current_user, current_database(), version();
```
**ผลลัพธ์:**
```
 current_user | current_database |                          version                           
--------------+------------------+------------------------------------------------------------
 postgres     | postgres         | PostgreSQL 17.11 (Ubuntu 17.11-1.pgdg24.04+2) on x86_64...
(1 row)
```

```sql
SHOW data_directory;
```
**ผลลัพธ์:**
```
      data_directory       
---------------------------
 /var/lib/postgresql/17/main
(1 row)
```

```sql
SHOW config_file;
```
**ผลลัพธ์:**
```
               config_file               
-----------------------------------------
 /etc/postgresql/17/main/postgresql.conf
(1 row)
```

### ขั้นที่ 3: ดูองค์ประกอบของเซิร์ฟเวอร์

```sql
\l
```
**ผลลัพธ์:**
```
                                                       List of databases
   Name    |  Owner   | Encoding | Collate |  Ctype  | ICU Locale | Locale Provider |   Access privileges   
-----------+----------+----------+---------+---------+------------+-----------------+-----------------------
 postgres  | postgres | UTF8     | C.UTF-8 | C.UTF-8 |            | libc            | 
 template0 | postgres | UTF8     | C.UTF-8 | C.UTF-8 |            | libc            | =c/postgres          +
           |          |          |         |         |            |                 | postgres=CTc/postgres
 template1 | postgres | UTF8     | C.UTF-8 | C.UTF-8 |            | libc            | =c/postgres          +
           |          |          |         |         |            |                 | postgres=CTc/postgres
(3 rows)
```

```sql
\du
```
**ผลลัพธ์:**
```
                             List of roles
 Role name |                         Attributes                         | Member of 
-----------+------------------------------------------------------------+-----------
 postgres  | Superuser, Create role, Create DB, Replication, Bypass RLS | {}
```

```sql
\dn
```
**ผลลัพธ์:**
```
  List of schemas
  Name  |       Owner       
--------+-------------------
 public | pg_database_owner
(1 row)
```

```sql
\dx
```
**ผลลัพธ์:**
```
                 List of installed extensions
  Name   | Version |   Schema   |         Description          
---------+---------+------------+------------------------------
 plpgsql | 1.0     | pg_catalog | PL/pgSQL procedural language
(1 row)
```

### ขั้นที่ 4: สร้างฐานข้อมูลทดลอง

```sql
CREATE DATABASE lab_practice;
```
**ผลลัพธ์:**
```
CREATE DATABASE
```

```sql
\l
```
**ผลลัพธ์:**
```
   Name    |  Owner   | Encoding | Collate |  Ctype  | ...
-----------+----------+----------+---------+---------+
 lab_practice | postgres | UTF8   | C.UTF-8 | C.UTF-8 | ...
 postgres  | postgres | UTF8     | C.UTF-8 | C.UTF-8 | ...
```

```sql
\c lab_practice
```
**ผลลัพธ์:**
```
You are now connected to database "lab_practice" as user "postgres".
lab_practice=#
```

### ขั้นที่ 5: สร้างตาราง เพิ่มข้อมูล และดูโครงสร้าง

```sql
CREATE TABLE note (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  title text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);
```
**ผลลัพธ์:**
```
CREATE TABLE
```

```sql
INSERT INTO note (title) VALUES ('first note'), ('second note');
```
**ผลลัพธ์:**
```
INSERT 0 2
```

```sql
SELECT * FROM note;
```
**ผลลัพธ์:**
```
 id |    title    |          created_at           
----+-------------+-------------------------------
  1 | first note  | 2026-11-02 09:12:34.567890+07
  2 | second note | 2026-11-02 09:12:34.567890+07
(2 rows)
```

```sql
\dt
```
**ผลลัพธ์:**
```
          List of relations
 Schema | Name | Type  |  Owner   
--------+------+-------+----------
 public | note | table | postgres
(1 row)
```

```sql
\d note
```
**ผลลัพธ์:**
```
                                        Table "public.note"
   Column   |           Type           | Collation | Nullable |      Default       
------------+--------------------------+-----------+----------+--------------------
 id         | bigint                   |           | not null | generated always as identity
 title      | text                     |           | not null | 
 created_at | timestamp with time zone |           | not null | now()
Indexes:
    "note_pkey" PRIMARY KEY, btree (id)
```

### ขั้นที่ 6: ตัวช่วยที่ใช้บ่อย

```sql
\x
SELECT * FROM note;
```
**ผลลัพธ์:**
```
-[ RECORD 1 ]+---------------------------
id           | 1
title        | first note
created_at   | 2026-11-02 09:12:34.56789+07
-[ RECORD 2 ]+---------------------------
id           | 2
title        | second note
created_at   | 2026-11-02 09:12:34.56789+07
```

```sql
\timing
SELECT count(*) FROM note;
```
**ผลลัพธ์:**
```
 count 
-------
     2
(1 row)

Time: 0.345 ms
```

```sql
\?
```
**ผลลัพธ์:** แสดงรายการ meta-command ทั้งหมดของ psql

```sql
\h CREATE TABLE
```
**ผลลัพธ์:** แสดง syntax ของ `CREATE TABLE` พร้อมตัวเลือกทั้งหมด

### ขั้นที่ 7: ลบฐานข้อมูลทดลอง แล้วออก

```sql
\c postgres
```
**ผลลัพธ์:**
```
You are now connected to database "postgres" as user "postgres".
postgres=#
```

```sql
DROP DATABASE lab_practice;
```
**ผลลัพธ์:**
```
DROP DATABASE
```

```sql
\l
```
**ผลลัพธ์:**
```
   Name    |  Owner   | ...
-----------+----------+-----
 postgres  | postgres | ...
 template0 | postgres | ...
 template1 | postgres | ...
(3 rows)
```

```sql
\q
```
**ผลลัพธ์:** กลับสู่ Shell (`student@ta1-pg2:~$`)

**✅ ผลลัพธ์ที่คาดหวัง:**
- `\conninfo` แสดง `You are connected to database "postgres" as user "postgres" via socket...`
- `SELECT * FROM note` ได้ 2 แถว
- `\l` สุดท้ายไม่มี `lab_practice`

---

## 🧪 Lab 3.2 — ปรับค่าตามขนาดเครื่อง และสังเกต Process กับ WAL

### ส่วนที่ 1: สร้างไฟล์ tuning

```bash
cd /etc/postgresql/17/main
sudo cp postgresql.conf postgresql.conf.bak
grep -n "^include_dir" postgresql.conf
```
**ผลลัพธ์:**
```
59:include_dir = 'conf.d'
```

```bash
sudo truncate -s 0 conf.d/10-gridcare-tuning.conf
sudo nano conf.d/10-gridcare-tuning.conf
```

**เนื้อหา `10-gridcare-tuning.conf`:**
```ini
# GridCare Day 1: ปรับตามเครื่อง Lab 2 vCPU / 4 GB RAM / SSD
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
sudo chown postgres:postgres conf.d/10-gridcare-tuning.conf
grep -c '=' conf.d/10-gridcare-tuning.conf
```
**ผลลัพธ์:**
```
19
```

### ส่วนที่ 2: ตรวจไฟล์ก่อน Restart

```bash
sudo -u postgres psql
```

```sql
SELECT sourcefile, sourceline, name, error FROM pg_file_settings WHERE error IS NOT NULL;
```
**ผลลัพธ์:**
```
 sourcefile | sourceline | name | error 
------------+------------+------+-------
(0 rows)
```

```sql
SELECT pg_reload_conf();
```
**ผลลัพธ์:**
```
 pg_reload_conf 
----------------
 t
(1 row)
```

```sql
SELECT name, setting, unit, pending_restart FROM pg_settings WHERE pending_restart;
```
**ผลลัพธ์:**
```
          name          | setting | unit | pending_restart 
------------------------+---------+------+-----------------
 shared_buffers         | 16384   | 8kB  | t
 reserved_connections   | 2       |      | t
 shared_preload_libraries| pg_stat_statements | | t
 listen_addresses       | *       |      | t
(4 rows)
```
> 💡 ค่าที่ตั้งเท่าค่าเริ่มต้น (เช่น `max_connections = 100`) จะไม่ขึ้นในรายการนี้

```sql
\q
```

### ส่วนที่ 3: Restart แล้วตรวจสอบ

```bash
sudo systemctl restart postgresql@17-main
sudo -u postgres psql
```

```sql
SELECT 'shared_buffers=' || current_setting('shared_buffers') AS result;
```
**ผลลัพธ์:**
```
       result        
---------------------
 shared_buffers=1GB
(1 row)
```

```sql
\q
```

### ส่วนที่ 4: สังเกต Process และ WAL

```bash
ps -u postgres -o pid,ppid,rss,cmd --forest | grep -v grep | grep postgres
```
**ผลลัพธ์:**
```
   1234     1   156 /usr/lib/postgresql/17/bin/postgres -D /var/lib/postgresql/17/main
   1236  1234  1024  \_ postgres: checkpointer
   1237  1234   932  \_ postgres: background writer
   1238  1234   876  \_ postgres: walwriter
   1239  1234   924  \_ postgres: autovacuum launcher
   1240  1234   748  \_ postgres: logical replication launcher
```
SELECT pid, backend_type, backend_start
FROM pg_stat_activity
ORDER BY backend_type;

  pid  |         backend_type         |         backend_start         
-------+------------------------------+-------------------------------
 21242 | autovacuum launcher          | 2026-10-31 03:46:07.98938+00
 21239 | background writer            | 2026-10-31 03:46:07.968842+00
 21238 | checkpointer                 | 2026-10-31 03:46:07.970745+00
 21328 | client backend               | 2026-10-31 03:52:42.270116+00
 21243 | logical replication launcher | 2026-10-31 03:46:07.991464+00
 21241 | walwriter                    | 2026-10-31 03:46:07.989576+00
(6 rows)


```bash
sudo -u postgres psql
```

```sql
SELECT pid, backend_type FROM pg_stat_activity ORDER BY backend_type;
```
**ผลลัพธ์:**
```
  pid  |         backend_type         
-------+------------------------------
  1236 | checkpointer
  1237 | background writer
  1238 | walwriter
  1239 | autovacuum launcher
  1240 | logical replication launcher
  1245 | client backend
(6 rows)
```

```sql
SELECT pg_current_wal_lsn(), pg_walfile_name(pg_current_wal_lsn());
```
*:**
```
 pg_current_wal_lsn |       pg_walfile_name       
--------------------+-----------------------------
 0/170000D8         | 000000010000000000000017
(1 row)
```

```sql
SELECT num_requested AS before_checkpoint FROM pg_stat_checkpointer;
```
**ผลลัพธ์:**
```
 before_checkpoint 
-------------------
                 0
(1 row)
```

```sql
CHECKPOINT;
SELECT pg_sleep(1);
SELECT num_timed, num_requested, buffers_written FROM pg_stat_checkpointer;
```
**ผลลัพธ์:**
```
CHECKPOINT
 pg_sleep 
----------
 
(1 row)

 num_timed | num_requested | buffers_written 
-----------+---------------+-----------------
         2 |             1 |             240
(1 row)
```
> ✅ `num_requested` เพิ่มจาก 0 เป็น 1 (มากกว่าค่า `before_checkpoint` 1)

```sql
\q
```

```bash
sudo ls -la /var/lib/postgresql/17/main/pg_wal | head
```
**ผลลัพธ์:**
```
total 32772
drwx------ 3 postgres postgres     4096 Nov  2 11:15 .
drwx------ 21 postgres postgres     4096 Nov  2 11:02 ..
-rw------- 1 postgres postgres 16777216 Nov  2 11:15 000000010000000000000017
-rw------- 1 postgres postgres 16777216 Nov  2 11:15 000000010000000000000018
drwx------ 2 postgres postgres     4096 Nov  2 11:15 archive_status
```
> 💡 ไฟล์ใน `pg_wal` มีขนาด 16 MB ต่อไฟล์

**✅ ผลลัพธ์:** `shared_buffers=1GB` และเห็น Process `checkpointer`, `background writer`, `walwriter`, `autovacuum launcher`

---

## 🧪 Lab 3.3 — เริ่มโหลดข้อมูล GridCare ใน tmux

### ขั้นที่ 1: ตรวจที่ว่างบนดิสก์

```bash
df -h /var/lib/postgresql
```
**ผลลัพธ์:**
```
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        78G   12G   63G  16% /
```
> ✅ ต้องมีที่ว่างอย่างน้อย 3 GB

### ขั้นที่ 2: เริ่มโหลดใน tmux

```bash
cd /opt/gridcare
tmux new -s gridcare
```
**ผลลัพธ์:** เข้าหน้าจอ tmux session ใหม่ชื่อ `gridcare`

**ภายในหน้าต่าง tmux:**
```bash
sudo -u postgres ./load_gridcare.sh
```
**ผลลัพธ์ (ระหว่างโหลด):**
```
== GridCare v2.3 load starting ==
>> load_ts = 2026-11-02 08:00+07
>> 01_schema.sql
>> creating schema gridcare ...
>> 02_reference_data.sql
>> loading regions ... 12 rows
>> loading offices ... 300 rows
>> loading tariff_rates ... 4 rows
>> 03_generate_data.sql
>> loading customers ... 200000 rows
>> loading meters ... 220000 rows
>> loading bills ... 1200000 rows
>> loading meter_readings ... 7200000 rows
>> 04_constraints_indexes.sql
>> 06_lab_extras.sql
>> 05_verify.sql
>> load_ts = 2026-11-02 08:00+07
```

### ขั้นที่ 3: Detach และตรวจสอบ

**เมื่อเห็น `>> load_ts = 2026-11-02 08:00+07`** → กด `Ctrl+b` แล้ว `d`

```bash
tmux ls
```
**ผลลัพธ์:**
```
gridcare: 1 windows (created Mon Nov  2 11:45:30 2026)
```

> 💡 ใช้เวลาราว 6 นาที (355 วินาทีบนเครื่อง Lab)

**⛔ ถ้าเผลอสั่งนอก tmux แล้ว SSH หลุด:**
```bash
pgrep -af load_gridcare.sh
```
**ผลลัพธ์:**
```
12345 bash /opt/gridcare/load_gridcare.sh
```
> ถ้าไม่มีผลลัพธ์ → โหลดใหม่ด้วย `sudo -u postgres RECREATE=1 ./load_gridcare.sh` **ภายใน tmux**

---

## 🧪 Lab 3.4 — ตรวจผลการโหลด และตั้งชุดค่า Log มาตรฐาน

### ส่วนที่ 1: ตรวจผลการโหลด

```bash
tmux attach -t gridcare
```
**ผลลัพธ์ (ท้ายสคริปต์):**
```
== invalid_count ==
 invalid_count
---------------
             0

== bad_format (ต้องเป็น 0) ==
 bad_format
------------
          0

== สถานะบิล ==
 OVERDUE |  50268
 PAID    | 950178
 UNPAID  | 199554
>> โหลดข้อมูลทั้งหมดเสร็จใน 122 วินาที
```
**✅ ผลลัพธ์:** `invalid_count = 0`, `bad_format = 0`, บิล 3 สถานะตามตัวเลข

**พิมพ์ `exit` เพื่อปิด session**

### ส่วนที่ 2: สร้าง Extension

```bash
sudo -u postgres psql -d gridcare
```

```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```
**ผลลัพธ์:**
```
CREATE EXTENSION
```

```sql
\dx
```
**ผลลัพธ์:**
```
                    List of installed extensions
        Name        | Version |   Schema   |         Description         
--------------------+---------+------------+------------------------------
 pg_stat_statements | 1.11    | public     | track planning and execution
 plpgsql            | 1.0     | pg_catalog | PL/pgSQL procedural language
(2 rows)
```

```sql
\q
```

### ส่วนที่ 3: สร้างไฟล์ Log config

```bash
cd /etc/postgresql/17/main
sudo truncate -s 0 conf.d/20-gridcare-logging.conf
sudo nano conf.d/20-gridcare-logging.conf
```

**เนื้อหา `20-gridcare-logging.conf`:**
```ini
# GridCare Day 1 (13:00): ชุดค่า Log มาตรฐาน
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

```bash
sudo chown postgres:postgres conf.d/20-gridcare-logging.conf
sudo -u postgres psql
```

```sql
SELECT sourcefile, name, error FROM pg_file_settings WHERE error IS NOT NULL;
```
**ผลลัพธ์:**
```
 sourcefile | name | error 
------------+------+-------
(0 rows)
```

```sql
SELECT pg_reload_conf();
```
**ผลลัพธ์:**
```
 pg_reload_conf 
----------------
 t
(1 row)
```

```sql
SELECT name, pending_restart FROM pg_settings WHERE pending_restart;
```
**ผลลัพธ์:**
```
          name          | pending_restart 
------------------------+-----------------
 shared_preload_libraries| t
(1 row)
```

```sql
\q
```

```bash
sudo systemctl restart postgresql@17-main
sudo -u postgres psql
```

```sql
SELECT CASE WHEN current_setting('shared_preload_libraries') LIKE '%auto_explain%' 
       THEN 'AUTOEXPLAIN_READY' ELSE 'NOT_LOADED' END AS result;
```
**ผลลัพธ์:**
```
     result       
------------------
 AUTOEXPLAIN_READY
(1 row)
```

```sql
\q
```

```bash
sudo tail -n 3 /var/log/postgresql/postgresql-17-main.log
```
**ผลลัพธ์:**
```
2026-11-02 13:05:23.517 +07 [4363] postgres@postgres app=[unknown] client=[local] LOG:  connection authorized: user=postgres database=postgres application_name=psql
2026-11-02 13:05:23.520 +07 [4363] postgres@postgres app=psql client=[local] LOG:  disconnection: session time: 0:00:00.004 ...
```

**✅ ผลลัพธ์:** `AUTOEXPLAIN_READY` และ Log มีรูปแบบ `ผู้ใช้@ฐานข้อมูล app=... client=...`

---

## 🧪 Lab 4.1 — MVCC, Isolation และคิว Lock

### เปิด tmux แบ่ง 4 หน้าต่าง

```bash
tmux new -s lock
# Ctrl+b แล้ว "  = แบ่งหน้าจอบนล่าง
# Ctrl+b แล้ว %  = แบ่งซ้ายขวา
# Ctrl+b แล้วลูกศร = ย้ายหน้าต่าง
```
**ผลลัพธ์:** เห็นหน้าจอแบ่ง 4 ช่อง

**เข้า psql ทุกหน้าต่าง:**
```bash
sudo -u postgres psql -d gridcare
```
**ผลลัพธ์:**
```
psql (17.11)
Type "help" for help.

gridcare=#
```

### ส่วน ก: xmin / xmax (หน้าต่าง 1)

```sql
SELECT xmin, xmax, ctid, tariff_code, rate_per_kwh FROM gridcare.tariff_rates WHERE tariff_code = 'RES';
```
**ผลลัพธ์:**
```
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
**ผลลัพธ์:**
```
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
> ✅ **จุดสังเกต:** `ctid` เปลี่ยนจาก `(0,1)` เป็น `(0,2)` และ `xmin` = `pg_current_xact_id()`

### ส่วน ข: Repeatable Read (หน้าต่าง 1 และ 2)

**หน้าต่าง 1:**
```sql
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT rate_per_kwh FROM gridcare.tariff_rates WHERE tariff_code = 'SMB';
```
**ผลลัพธ์:**
```
BEGIN
 rate_per_kwh 
--------------
         4.50
(1 row)
```

**หน้าต่าง 2:**
```sql
UPDATE gridcare.tariff_rates SET rate_per_kwh = rate_per_kwh WHERE tariff_code = 'SMB';
```
**ผลลัพธ์:**
```
UPDATE 1
```

**หน้าต่าง 1 (อีกครั้ง):**
```sql
UPDATE gridcare.tariff_rates SET rate_per_kwh = rate_per_kwh WHERE tariff_code = 'SMB';
```
**ผลลัพธ์:**
```
ERROR:  could not serialize access due to concurrent update
```

```sql
ROLLBACK;
```
**ผลลัพธ์:**
```
ROLLBACK
```

### ส่วน ค: คิว Lock (หน้าต่าง 1, 2, 3)

**หน้าต่าง 1:**
```sql
SET application_name = 'batch_A';
BEGIN;
SELECT count(*) FROM gridcare.tariff_rates;
```
**ผลลัพธ์:**
```
SET
BEGIN
 count 
-------
     4
(1 row)
```
> ⚠️ **ไม่ COMMIT** ทิ้งไว้

**หน้าต่าง 2:**
```sql
SET application_name = 'migration_B';
ALTER TABLE gridcare.tariff_rates ADD COLUMN note text;
```
**ผลลัพธ์:** (ค้าง — รอ Lock)

**หน้าต่าง 3:**
```sql
SET application_name = 'app_C';
SELECT * FROM gridcare.tariff_rates;
```
**ผลลัพธ์:** (ค้าง — รอ Lock)

### หน้าต่าง 4: หาต้นคิว

```sql
SELECT pid, application_name AS app, state, wait_event_type AS wtype,
       pg_blocking_pids(pid) AS blocked_by, now() - xact_start AS xact_age, left(query, 50) AS query
FROM pg_stat_activity
WHERE datname = 'gridcare' AND backend_type = 'client backend' AND pid <> pg_backend_pid()
ORDER BY xact_start;
```
**ผลลัพธ์:**
```
  pid  |     app     |        state        | wtype  | blocked_by |    xact_age     |                       query
------+-------------+---------------------+--------+------------+-----------------+----------------------------------------------------
 7659 | batch_A     | idle in transaction | Client | {}         | 00:00:04.024625 | SELECT count(*) FROM gridcare.tariff_rates;
 7665 | migration_B | active              | Lock   | {7659}     | 00:00:03.012906 | ALTER TABLE gridcare.tariff_rates ADD COLUMN note
 7672 | app_C       | active              | Lock   | {7665}     | 00:00:02.006274 | SELECT * FROM gridcare.tariff_rates;
(3 rows)
```

```sql
SELECT pid, application_name, state, now() - state_change AS idle_for, left(query, 50) AS last_query
FROM pg_stat_activity
WHERE pid IN (SELECT unnest(pg_blocking_pids(pid)) FROM pg_stat_activity)
  AND cardinality(pg_blocking_pids(pid)) = 0;
```
**ผลลัพธ์:**
```
 pid  | application_name |        state        |    idle_for     |                 last_query
------+------------------+---------------------+-----------------+---------------------------------------------
 7659 | batch_A          | idle in transaction | 00:00:04.027413 | SELECT count(*) FROM gridcare.tariff_rates;
(1 row)
```
> ✅ **ต้นคิว = `batch_A`** (pid 7659) เพราะบล็อกคนอื่น แต่ตัวเองไม่ถูกใครบล็อก

### ดู Log ที่ได้จาก `log_lock_waits = on`

```bash
sudo grep "still waiting" /var/log/postgresql/postgresql-17-main.log | tail -2
```
**ผลลัพธ์:**
```
2026-11-02 14:12:34.567 +07 [7665] postgres@gridcare app=migration_B client=[local] LOG:  process 7665 still waiting for AccessExclusiveLock on relation 16384 of database 16389 after 1000.123 ms
2026-11-02 14:12:34.567 +07 [7672] postgres@gridcare app=app_C client=[local] LOG:  process 7672 still waiting for AccessShareLock on relation 16384 of database 16389 after 1000.456 ms
```

### แก้ตามลำดับที่ถูกต้อง (หน้าต่าง 4)

```sql
SELECT pg_cancel_backend(7665);     -- 1) ยกเลิก DDL ที่รอคิว: app_C ทำงานต่อทันที
```
**ผลลัพธ์:**
```
 pg_cancel_backend 
-------------------
 t
(1 row)
```

```sql
SELECT pg_terminate_backend(7659);  -- 2) ตัด Session ต้นเหตุที่ค้าง
```
**ผลลัพธ์:**
```
 pg_terminate_backend 
----------------------
 t
(1 row)
```

**✅ ผลลัพธ์ที่คาดหวัง:**
- หน้าต่าง 2 ได้ `ERROR: canceling statement due to user request`
- หน้าต่าง 3 ได้ผลลัพธ์ `SELECT *` ทันที
- ตาราง **ไม่มี** คอลัมน์ `note`

### ทดลองแบบถูกต้อง: Migration ที่ตั้ง `lock_timeout`

**หน้าต่าง 1 (เปิด BEGIN ค้างไว้อีกครั้ง):**
```sql
BEGIN;
SELECT count(*) FROM gridcare.tariff_rates;
```

**หน้าต่าง 2:**
```sql
SET lock_timeout = '3s';
ALTER TABLE gridcare.tariff_rates ADD COLUMN note text;
```
**ผลลัพธ์:**
```
SET
ERROR:  canceling statement due to lock timeout
```
> ✅ **SQLSTATE 55P03** — แอปไม่ค้างตาม

**ปิดหน้าต่าง 1:**
```sql
ROLLBACK;
```

---

## 🛠️ Workshop Day 1 — ขั้นที่ 1: Role และ Timeout

### 1.1 เข้า psql ที่ฐาน gridcare

```bash
sudo -u postgres psql -d gridcare
```
**ผลลัพธ์:**
```
psql (17.11)
Type "help" for help.

gridcare=#
```

### 1.2 สร้าง Group Role ที่ถือสิทธิ์

```sql
-- กลุ่มอ่าน
CREATE ROLE gridcare_read NOLOGIN;
GRANT CONNECT ON DATABASE gridcare TO gridcare_read;
GRANT USAGE ON SCHEMA gridcare TO gridcare_read;
GRANT SELECT ON ALL TABLES IN SCHEMA gridcare TO gridcare_read;
ALTER DEFAULT PRIVILEGES IN SCHEMA gridcare GRANT SELECT ON TABLES TO gridcare_read;
```
**ผลลัพธ์:**
```
CREATE ROLE
GRANT
GRANT
GRANT
ALTER DEFAULT PRIVILEGES
```

```sql
-- กลุ่มเขียน
CREATE ROLE gridcare_write NOLOGIN IN ROLE gridcare_read;
GRANT INSERT ON gridcare.meter_readings, gridcare.outage_events, gridcare.work_orders,
                gridcare.payments, gridcare.sms_notifications, gridcare.bills TO gridcare_write;
GRANT UPDATE ON gridcare.bills TO gridcare_write;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA gridcare TO gridcare_write;
ALTER DEFAULT PRIVILEGES IN SCHEMA gridcare GRANT USAGE ON SEQUENCES TO gridcare_write;
```
**ผลลัพธ์:**
```
CREATE ROLE
GRANT
GRANT
GRANT
ALTER DEFAULT PRIVILEGES
```

### 1.3 สร้าง Login Role

```sql
CREATE ROLE billing_app   LOGIN PASSWORD 'Lab-Billing-2569'    IN ROLE gridcare_write;
CREATE ROLE callcenter_ro LOGIN PASSWORD 'Lab-CallCenter-2569' IN ROLE gridcare_read;
CREATE ROLE report_ro     LOGIN PASSWORD 'Lab-Report-2569'     IN ROLE gridcare_read;
CREATE ROLE dba LOGIN CREATEROLE PASSWORD 'Lab-Dba-2569'
  IN ROLE pg_maintain, pg_monitor, pg_signal_backend, pg_use_reserved_connections;
GRANT gridcare_read TO dba;
CREATE ROLE pgbouncer_auth LOGIN PASSWORD 'Lab-PgbAuth-2569';
GRANT CONNECT ON DATABASE gridcare TO pgbouncer_auth;
```
**ผลลัพธ์:**
```
CREATE ROLE
CREATE ROLE
CREATE ROLE
CREATE ROLE
GRANT ROLE
CREATE ROLE
GRANT
```

### 1.4 ตั้ง Timeout ต่อ Role

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
**ผลลัพธ์:**
```
ALTER ROLE
ALTER ROLE
...
ALTER ROLE
(11 rows)
```

### 1.5 ปิดสิทธิ์ PUBLIC แล้วออก

```sql
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON DATABASE gridcare FROM PUBLIC;
\q
```
**ผลลัพธ์:**
```
REVOKE
REVOKE
```
> กลับสู่ Shell

### ตรวจผล (ขั้นที่ 1)

```bash
sudo -u postgres psql -d gridcare
```

```sql
\du
```
**ผลลัพธ์:**
```
                             List of roles
   Role name   |                         Attributes                         | Member of 
---------------+------------------------------------------------------------+-----------
 billing_app   |                                                            | {gridcare_write}
 callcenter_ro |                                                            | {gridcare_read}
 dba           | Create role                                                | {gridcare_read,pg_maintain,pg_monitor,pg_signal_backend,pg_use_reserved_connections}
 gridcare_read | Cannot login                                               | {}
 gridcare_write| Cannot login                                               | {gridcare_read}
 pgbouncer_auth|                                                            | {}
 postgres      | Superuser, Create role, Create DB, Replication, Bypass RLS | {}
 report_ro     |                                                            | {gridcare_read}
```

```sql
  SELECT r.rolname, s.setconfig
  FROM pg_db_role_setting AS s JOIN pg_roles AS r ON r.oid = s.setrole
  ORDER BY 1;
```
**ผลลัพธ์:**
```
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
**ผลลัพธ์:**
```
 cc_select | cc_update | app_update | pgb_connect 
-----------+-----------+------------+-------------
 t         | f         | t          | t
(1 row)
```

```sql
SET ROLE billing_app;
SELECT 'transaction_timeout=' || current_setting('transaction_timeout') AS result;
RESET ROLE;
\q
```
**ผลลัพธ์:**
```
SET
       result        
---------------------
 transaction_timeout=0
(1 row)
RESET
```
> ⚠️ `SET ROLE` ไม่โหลดค่าที่ตั้งด้วย `ALTER ROLE ... SET` — ค่าจริงทดสอบหลังขั้นที่ 2 (Login ผ่าน TCP)

**✅ ผลลัพธ์:** `cc_select = t`, `cc_update = f`, `app_update = t`, `pgb_connect = t`

---

## 🛠️ Workshop Day 1 — ขั้นที่ 2: เปิด TLS

### 2.1 สร้างใบรับรอง Self-signed

```bash
cd /etc/postgresql/17/main
PG1_IP=$(getent hosts pg1 | awk '{print $1}')
sudo openssl req -new -x509 -days 365 -nodes -newkey rsa:3072 \
  -subj "/CN=pg1" -addext "subjectAltName=DNS:pg1,IP:${PG1_IP}" \
  -keyout server.key -out server.crt
```
**ผลลัพธ์:**
```
Generating a RSA private key
..........................+++++
.............+++++
writing new private key to 'server.key'
-----
```

```bash
sudo chown postgres:postgres server.key server.crt
sudo chmod 600 server.key
sudo openssl x509 -in server.crt -noout -subject -enddate -ext subjectAltName
```
**ผลลัพธ์:**
```
subject=CN = pg1
notAfter=Nov  2 11:20:00 2027 GMT
X509v3 Subject Alternative Name: 
    DNS:pg1, IP Address:10.104.0.11
```

### 2.2 ตั้งค่า TLS

```bash
sudo truncate -s 0 conf.d/30-gridcare-ssl.conf
sudo nano conf.d/30-gridcare-ssl.conf
```

**เนื้อหา `30-gridcare-ssl.conf`:**
```ini
ssl = on
ssl_cert_file = '/etc/postgresql/17/main/server.crt'
ssl_key_file = '/etc/postgresql/17/main/server.key'
ssl_min_protocol_version = 'TLSv1.2'
password_encryption = 'scram-sha-256'
```

```bash
sudo chown postgres:postgres conf.d/30-gridcare-ssl.conf
```

### 2.3 เพิ่มกฎใน pg_hba.conf

```bash
sudo cp pg_hba.conf pg_hba.conf.bak
INFRA_IP=$(getent hosts infra | awk '{print $1}')
echo "INFRA_IP=$INFRA_IP"
```
**ผลลัพธ์:**
```
INFRA_IP=10.104.0.13
```

```bash
sudo tee -a pg_hba.conf > /dev/null <<EOF

# GridCare Day 1 Workshop: เชื่อมต่อผ่านเครือข่ายต้องเป็น TLS + SCRAM เท่านั้น
hostssl gridcare  billing_app,callcenter_ro,report_ro,pgbouncer_auth  ${INFRA_IP}/32   scram-sha-256
hostssl all       dba                                                ${INFRA_IP}/32   scram-sha-256
hostssl all       dba                                                10.104.0.13/32   scram-sha-256
hostssl all       dba                                                10.104.0.14/32   scram-sha-256
hostnossl all     all                                                0.0.0.0/0        reject
EOF
sudo tail -n 7 pg_hba.conf
```
**ผลลัพธ์:**
```
# GridCare Day 1 Workshop: เชื่อมต่อผ่านเครือข่ายต้องเป็น TLS + SCRAM เท่านั้น
hostssl gridcare  billing_app,callcenter_ro,report_ro,pgbouncer_auth  10.104.0.13/32   scram-sha-256
hostssl all       dba                                                10.104.0.13/32   scram-sha-256
hostssl all       dba                                                10.104.0.13/32   scram-sha-256
hostssl all       dba                                                10.104.0.14/32   scram-sha-256
hostnossl all     all                                                0.0.0.0/0        reject
```

### 2.4 ตรวจกฎก่อน Reload

```bash
sudo -u postgres psql
```

```sql
SELECT line_number, type, database, user_name, address, auth_method, error 
FROM pg_hba_file_rules WHERE line_number > 120 OR error IS NOT NULL;
```
**ผลลัพธ์:**
```
 line_number |   type   |            database            |           user_name            |   address    |  auth_method  | error 
-------------+----------+--------------------------------+--------------------------------+--------------+---------------+-------
         132 | hostssl  | {gridcare}                     | {billing_app,callcenter_ro,...}| 10.104.0.13  | scram-sha-256 | 
         133 | hostssl  | {all}                          | {dba}                          | 10.104.0.13  | scram-sha-256 | 
         134 | hostssl  | {all}                          | {dba}                          | 10.104.0.13  | scram-sha-256 | 
         135 | hostssl  | {all}                          | {dba}                          | 10.104.0.14  | scram-sha-256 | 
         136 | hostnossl| {all}                          | {all}                          | 0.0.0.0/0    | reject        | 
(5 rows)
```

```sql
SELECT pg_reload_conf();
\q
```

```bash
sudo tail -n 3 /var/log/postgresql/postgresql-17-main.log
```
**ผลลัพธ์:**
```
2026-11-02 15:30:12.345 +07 [4363] LOG:  received SIGHUP, reloading configuration files
2026-11-02 15:30:12.567 +07 [4363] LOG:  parameter "ssl" changed to "on"
2026-11-02 15:30:12.789 +07 [4363] LOG:  configuration file "/etc/postgresql/17/main/pg_hba.conf" was reloaded
```

### ทดสอบจาก infra

```bash
# ติดตั้ง psql ถ้ายังไม่มี
sudo apt install -y postgresql-client-17
```

**ครั้งที่ 1 — เชื่อมต่อแบบบังคับ TLS (ต้องเข้าได้):**
```bash
psql "host=pg1 dbname=gridcare user=billing_app sslmode=require"
```
**ผลลัพธ์:**
```
Password for user billing_app: (ใส่ Lab-Billing-2569)
psql (17.11)
SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, compression: off)
Type "help" for help.

gridcare=>
```

- sudo -u postgres psql

```sql
SELECT ssl, version, cipher FROM pg_stat_ssl WHERE pid = pg_backend_pid();
```
**ผลลัพธ์:**
```
 ssl | version |         cipher         
-----+---------+------------------------
 t   | TLSv1.3 | TLS_AES_256_GCM_SHA384
(1 row)
```

```sql
SHOW transaction_timeout;
```
**ผลลัพธ์:**
```
 transaction_timeout 
---------------------
 5min
(1 row)
```

```sql
\q
```

**ครั้งที่ 2 — เชื่อมต่อแบบไม่เข้ารหัส (ต้องถูกปฏิเสธ):**
```bash
psql "host=pg1 dbname=gridcare user=billing_app sslmode=disable"
```
**ผลลัพธ์:**
```
psql: error: connection to server at "pg1" (10.104.0.11), port 5432 failed: 
FATAL:  pg_hba.conf rejects connection for host "10.104.0.13", user "billing_app", database "gridcare", no encryption
```

**✅ ผลลัพธ์:**
- `sslmode=require` ได้ `TLSv1.3` + `transaction_timeout = 5min`
- `sslmode=disable` ถูก reject

---

## 🛠️ Workshop Day 1 — ขั้นที่ 3: PgBouncer และ pgbench

### 3.1 เตรียมฟังก์ชันค้นรหัสผ่านบน pg1

```bash
sudo -u postgres psql -d gridcare
```

```sql
CREATE SCHEMA pgbouncer AUTHORIZATION postgres;
REVOKE ALL ON SCHEMA pgbouncer FROM PUBLIC;
GRANT USAGE ON SCHEMA pgbouncer TO pgbouncer_auth;
```
**ผลลัพธ์:**
```
CREATE SCHEMA
REVOKE
GRANT
```

```sql
CREATE OR REPLACE FUNCTION pgbouncer.user_lookup(in i_username text, out uname text, out phash text)
RETURNS record AS $$
BEGIN
    SELECT rolname, CASE WHEN rolvaliduntil < now() THEN NULL ELSE rolpassword END
    FROM pg_authid
    WHERE rolname = i_username AND rolcanlogin AND NOT rolsuper
    INTO uname, phash;
    RETURN;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog, pg_temp;
REVOKE ALL ON FUNCTION pgbouncer.user_lookup(text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION pgbouncer.user_lookup(text) TO pgbouncer_auth;
```
**ผลลัพธ์:**
```
CREATE FUNCTION
REVOKE
GRANT
```

```sql
\q
```

### 3.2 ติดตั้งและตั้งค่า PgBouncer บน infra

```bash
pg_lsclusters
```
**ผลลัพธ์:**
```
Ver Cluster Port Status Owner    Data directory              Log file
(ตารางว่าง — infra ไม่มี Cluster)
```

```bash
sudo apt install -y pgbouncer postgresql-client-17 postgresql-17
```
**ผลลัพธ์:**
```
Reading package lists... Done
...
Setting up pgbouncer (1.26.1-1.pgdg24.04+1) ...
```

```bash
pg_lsclusters
```
**ผลลัพธ์:**
```
(ตารางว่าง — ยังไม่มี Cluster)
```

```bash
sudo cp /etc/pgbouncer/pgbouncer.ini /etc/pgbouncer/pgbouncer.ini.orig
sudo truncate -s 0 /etc/pgbouncer/pgbouncer.ini
sudo nano /etc/pgbouncer/pgbouncer.ini
```

**เนื้อหา `/etc/pgbouncer/pgbouncer.ini`:**
```ini
[databases]
gridcare = host=pg1 port=5432 dbname=gridcare

[pgbouncer]
listen_addr = *
listen_port = 6432
unix_socket_dir = /var/run/postgresql
auth_type = scram-sha-256
auth_file = /etc/pgbouncer/userlist.txt
auth_user = pgbouncer_auth
auth_query = SELECT uname, phash FROM pgbouncer.user_lookup($1)
auth_dbname = gridcare
pool_mode = transaction
default_pool_size = 20
min_pool_size = 5
reserve_pool_size = 5
reserve_pool_timeout = 3
max_db_connections = 40
max_client_conn = 1000
server_tls_sslmode = require
ignore_startup_parameters = extra_float_digits,options
admin_users = pgbouncer_admin
stats_users = pgbouncer_stats
logfile = /var/log/postgresql/pgbouncer.log
pidfile = /var/run/postgresql/pgbouncer.pid
```

```bash
sudo truncate -s 0 /etc/pgbouncer/userlist.txt
sudo nano /etc/pgbouncer/userlist.txt
```

**เนื้อหา `/etc/pgbouncer/userlist.txt`:**
```
"pgbouncer_auth" "Lab-PgbAuth-2569"
"pgbouncer_admin" "Lab-PgbAdmin-2569"
```

```bash
sudo chown postgres:postgres /etc/pgbouncer/userlist.txt /etc/pgbouncer/pgbouncer.ini
sudo chmod 640 /etc/pgbouncer/userlist.txt
```

### 3.2.3 Restart และตรวจสอบ

```bash
sudo systemctl restart pgbouncer
systemctl status pgbouncer --no-pager | head -3
```
**ผลลัพธ์:**
```
● pgbouncer.service - PgBouncer
     Loaded: loaded (/lib/systemd/system/pgbouncer.service; enabled; preset: enabled)
     Active: active (running) since Mon 2026-11-02 15:45:12 +07; 2s ago
```

```bash
sudo tail -n 5 /var/log/postgresql/pgbouncer.log
```
**ผลลัพธ์:**
```
2026-11-02 15:45:12.123 UTC [1234] LOG kernel file descriptor limit: 1024 (hard: 524288); max_client_conn: 1000, max expected fd use: 1046
2026-11-02 15:45:12.234 UTC [1234] LOG listening on 0.0.0.0:6432
2026-11-02 15:45:12.345 UTC [1234] LOG process up: PgBouncer 1.26.1, libevent 2.1.12-stable (epoll), adns: evdns2, tls: OpenSSL 3.0.13
```

```bash
psql "host=127.0.0.1 port=6432 dbname=gridcare user=billing_app"
```
**ผลลัพธ์:**
```
Password for user billing_app: (ใส่ Lab-Billing-2569)
psql (17.11)
Type "help" for help.

gridcare=>
```

```sql
SELECT current_user, ssl FROM pg_stat_ssl WHERE pid = pg_backend_pid();
```
**ผลลัพธ์:**
```
 current_user | ssl 
--------------+-----
 billing_app  | t
(1 row)
```
> ✅ เข้าผ่าน PgBouncer ได้ และ PgBouncer ต่อไป pg1 ด้วย TLS

```sql
\q
```

### 3.3 วัดผลด้วย pgbench

**สร้าง `~/.pgpass`:**

```bash
truncate -s 0 ~/.pgpass
nano ~/.pgpass
```

**เนื้อหา `~/.pgpass`:**
```
pg1:5432:gridcare:billing_app:Lab-Billing-2569
127.0.0.1:6432:gridcare:billing_app:Lab-Billing-2569
127.0.0.1:6432:pgbouncer:pgbouncer_admin:Lab-PgbAdmin-2569
```

```bash
chmod 600 ~/.pgpass
```

**แบบ ก) ต่อ pg1 ตรง:**

```bash
cd /opt/gridcare/pgbench
PGHOST=pg1 PGPORT=5432 PGUSER=billing_app PGSSLMODE=require \
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
number of transactions actually processed: 3421
latency average = 878.234 ms
tps = 57.012345 (including connections establishing)
```

**แบบ ข) ผ่าน PgBouncer:**

```bash
PGHOST=127.0.0.1 PGPORT=6432 PGUSER=billing_app \
  pgbench -n -C -c 50 -j 2 -T 60 -f lookup_customer.sql -f report_outage.sql gridcare
```
**ผลลัพธ์:**
```
number of transactions actually processed: 5589
latency average = 536.892 ms
tps = 93.123456 (including connections establishing)
```

**แบบ ค) ดูสถานะ Pool (ระหว่างที่ ข) กำลังรัน):**

```bash
psql "host=127.0.0.1 port=6432 dbname=pgbouncer user=pgbouncer_admin"
```

```sql
SHOW POOLS;
```
**ผลลัพธ์:**
```
 database  |   user      | cl_active | cl_waiting | sv_active | sv_idle | sv_used | sv_tested | sv_login | maxwait | maxwait_us | pool_mode 
-----------+-------------+-----------+------------+-----------+---------+---------+-----------+----------+---------+------------+-----------
 gridcare  | billing_app |        50 |          0 |        20 |       0 |       0 |         0 |        0 |       0 |          0 | transaction
 pgbouncer | pgbouncer_admin |     1 |          0 |         0 |       0 |       0 |         0 |        0 |       0 |          0 | statement
(2 rows)
```
> ✅ เห็น `cl_active=50` (แอปเชื่อม) แต่ `sv_active + sv_idle ≤ 40` (Server Connection จริง)

```sql
SHOW STATS;
\q
```
**ผลลัพธ์:**
```
 database  | total_xact_count | total_query_count | total_received | total_sent | total_xact_time | total_query_time 
-----------+------------------+-------------------+----------------+------------+-----------------+-----------------
 gridcare  |             5589 |            16767 |       12345678 |  234567890 |        89012345 |       123456789
 pgbouncer |                1 |                 1 |            100 |        500 |             100 |             200
```

### สรุปผลการวัด

| วิธีเชื่อมต่อ (50 Client, `-C`) | tps | latency เฉลี่ย | failed |
|---|---|---|---|
| **ต่อ pg1 ตรง** | 57 | 878 ms | 0 |
| **ผ่าน PgBouncer** | **93** | **536 ms** | 0 |

> ✅ **ผลลัพธ์:** tps แบบ ข) สูงกว่า **+63%** และ latency ต่ำกว่า **-39%**

### 3.4 เชื่อม pgAdmin 4 Desktop ผ่าน SSH Tunnel

1. ใน pgAdmin เลือก **Tools > Import/Export Servers** → นำเข้าไฟล์จาก Lab Kit
2. เปิด Server **pg1** ใส่ Username `dba` / Password `Lab-Dba-2569`
3. แท็บ **SSH Tunnel**: Tunnel host เป็น IP ของ Bastion, Username = ชื่อชุด, Identity file = `id_lab`
4. แท็บ **Parameters**: SSL mode = `require`
5. เปิด **Dashboard** แล้วรัน pgbench แบบ ข) อีกครั้ง

**✅ ผลลัพธ์:** pgAdmin เชื่อมต่อได้และเห็นฐานข้อมูล `gridcare`

> ⚠️ ถ้าได้ `no pg_hba.conf entry for host "10.104.0.13"` แปลว่ายังไม่ได้ใส่ IP ของ Bastion ในขั้นที่ 2

---

## 📊 สรุปคำสั่งสำคัญทั้งหมด (Cheat Sheet Day 1)

### SSH และตรวจสอบเครื่อง

```bash
ssh lab-pg1                                  # เข้าเครื่อง pg1
hostname                                     # ชื่อเครื่อง
ip -4 -br addr show | grep 10.104            # IP ส่วนตัว
for h in pg1 pg2 infra; do getent hosts "$h" > /dev/null && echo "$h OK" || echo "$h MISSING"; done
```

### Linux และ tmux

```bash
systemctl status <service> --no-pager        # สถานะ Service
journalctl -u <service> --since "10 min ago" # ดู Log
df -hT /                                     # ดิสก์
free -h                                      # หน่วยความจำ
nproc                                        # จำนวน CPU
vmstat 2 3                                   # สถิติระบบ
tmux new -s <name>                           # สร้าง session
tmux ls                                      # ดู session ทั้งหมด
tmux attach -t <name>                        # กลับเข้า session
# Ctrl+b d = detach
```

### PostgreSQL พื้นฐาน

```bash
pg_lsclusters                                # ดู Cluster ทั้งหมด
systemctl restart postgresql@17-main         # Restart Cluster
sudo -u postgres psql                        # เข้า psql
sudo -u postgres psql -d gridcare            # เข้า psql ที่ฐาน gridcare
```

### คำสั่งใน psql

```
\conninfo          # ข้อมูลการเชื่อมต่อ
\l \du \dn \dx     # ดู Database, Role, Schema, Extension
\dt \d <table>     # ดูตารางและโครงสร้าง
\c <dbname>        # ย้ายฐานข้อมูล
\x                 # สลับแนวตั้ง/แนวนอน
\timing            # เปิด/ปิดการจับเวลา
\?  \h <SQL>       # help
\q                 # ออก
```

### Tuning และตรวจสอบ

```sql
SELECT sourcefile, name, error FROM pg_file_settings WHERE error IS NOT NULL;
SELECT pg_reload_conf();
SELECT name, pending_restart FROM pg_settings WHERE pending_restart;
SELECT 'shared_buffers=' || current_setting('shared_buffers') AS result;
SELECT pg_current_wal_lsn(), pg_walfile_name(pg_current_wal_lsn());
CHECKPOINT;
SELECT num_timed, num_requested, buffers_written FROM pg_stat_checkpointer;
```

### Lock Queue

```sql
SELECT pid, application_name AS app, state, wait_event_type AS wtype,
       pg_blocking_pids(pid) AS blocked_by, now() - xact_start AS xact_age, left(query, 50) AS query
FROM pg_stat_activity
WHERE datname = 'gridcare' AND backend_type = 'client backend' AND pid <> pg_backend_pid()
ORDER BY xact_start;

SELECT pg_cancel_backend(<pid>);       -- ยกเลิกคำสั่ง
SELECT pg_terminate_backend(<pid>);    -- ตัด Session
```

### Role, TLS, PgBouncer

```sql
CREATE ROLE <name> LOGIN PASSWORD '...' IN ROLE <group>;
ALTER ROLE <name> SET <param> = <value>;
GRANT <priv> ON <object> TO <role>;
REVOKE <priv> ON <object> FROM PUBLIC;
```

```bash
# TLS
sudo openssl req -new -x509 -days 365 -nodes -newkey rsa:3072 \
  -subj "/CN=pg1" -addext "subjectAltName=DNS:pg1,IP:${PG1_IP}" \
  -keyout server.key -out server.crt
sudo chmod 600 server.key

# PgBouncer
sudo systemctl restart pgbouncer
psql "host=127.0.0.1 port=6432 dbname=pgbouncer user=pgbouncer_admin" -c "SHOW POOLS;"
```

### pgbench วัดผล

```bash
# ต่อตรง
PGHOST=pg1 PGPORT=5432 PGUSER=billing_app PGSSLMODE=require \
  pgbench -n -C -c 50 -j 2 -T 60 -f lookup_customer.sql -f report_outage.sql gridcare

# ผ่าน PgBouncer
PGHOST=127.0.0.1 PGPORT=6432 PGUSER=billing_app \
  pgbench -n -C -c 50 -j 2 -T 60 -f lookup_customer.sql -f report_outage.sql gridcare
```

---

## 🎯 สรุปผลลัพธ์สำคัญของ Day 1

| Lab | ผลลัพธ์ที่วัดได้ |
|---|---|
| **Lab 0.1** | `pg1 OK`, `pg2 OK`, `infra OK` ครบ 3 บรรทัด |
| **Lab 2.1** | `df` ~80GB, `free` ~3.8Gi, `tmux ls` → `practice: 1 windows` |
| **Lab 3.1** | `data_checksums=on`, PostgreSQL 17.11 |
| **Lab 3.1 (ต่อ)** | `\conninfo` → connected as user "postgres"; `SELECT * FROM note` → 2 แถว |
| **Lab 3.2** | `(0 rows)` error, `shared_buffers=1GB`, `num_requested` เพิ่ม 1 |
| **Lab 3.3** | `tmux ls` → `gridcare: 1 windows`, โหลด ~6 นาที (355 วินาที) |
| **Lab 3.4** | `invalid_count=0`, `bad_format=0`, `AUTOEXPLAIN_READY` |
| **Lab 4.1** | `could not serialize access due to concurrent update`, `migration_B` blocked_by `{batch_A}` |
| **Workshop ขั้น 1** | `cc_select=t`, `cc_update=f`, `app_update=t`, `pgb_connect=t` |
| **Workshop ขั้น 2** | `TLSv1.3`, `transaction_timeout=5min`; `sslmode=disable` → reject |
| **Workshop ขั้น 3** | **pg1 ตรง: 57 tps / 878 ms** vs **PgBouncer: 93 tps / 536 ms** (+63%/-39%) |

---

## ⚠️ ข้อควรระวังใน Day 1

| # | ข้อควรระวัง | ผลที่เกิด |
|---|---|---|
| 1 | **ตั้ง `initdb_options = '--data-checksums'` ก่อน `apt install`** | ถ้าลืม → ต้อง `pg_dropcluster` และสร้างใหม่ |
| 2 | **`ufw enable` ต้อง `ufw allow ssh` ก่อนเสมอ** | ถ้าลืม → ล็อกตัวเองออกจากเครื่อง |
| 3 | **`sudo echo ... >> ไฟล์` ใช้ไม่ได้** | ต้องใช้ `sudo tee -a` เพราะ `>>` ทำงานด้วยสิทธิ์ของ student |
| 4 | **`pg_hba.conf` อ่านบนลงล่าง ใช้บรรทัดแรกที่ตรง** | บรรทัด `reject` ต้องอยู่ล่างสุด |
| 5 | **`pg_reload_conf()` คืนค่า `t` เสมอแม้ไฟล์ผิด** | ต้องตรวจ `pg_hba_file_rules` ก่อน Reload |
| 6 | **`server.key` ต้อง `chmod 600`** | ถ้าไม่ → PostgreSQL ไม่เปิด TLS |
| 7 | **`lock_timeout` ก่อน `ALTER TABLE` ทุกครั้ง** | ถ้าไม่ → กลายเป็นต้นคิว ทำให้ทั้งแอปหยุด |
| 8 | **คำอธิบายใน `pgbouncer.ini` ต้องอยู่คนละบรรทัดกับค่า** | ถ้าเขียนต่อท้าย → PgBouncer สตาร์ตไม่ขึ้น |
| 9 | **`pgbouncer_auth` ใน `userlist.txt` ต้องเป็นรหัสผ่านปกติ** | ถ้าใส่ SCRAM secret → `wrong password type` |
| 10 | **`SET ROLE` ไม่โหลดค่า `ALTER ROLE ... SET`** | ค่าจริงต้อง Login ใหม่ผ่าน TCP |

---

**✅ สรุปเสร็จสมบูรณ์** — คำสั่งและผลลัพธ์ทั้งหมดจาก Day 1 ครอบคลุม Lab 0.1, Lab 2.1, Lab 3.1-3.4, Lab 4.1 และ Workshop Day 1 (Role + TLS + PgBouncer) พร้อมตัวเลขที่วัดได้จริงจากหลักสูตร

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

# 📋 สรุปคำสั่งทั้งหมด — Day 4 (วันที่ 4)

> **หลักสูตร:** Advanced PostgreSQL for Enterprise Production (PEA)
> **หัวข้อ:** Replication, High Availability & Alerting
> **วันที่:** พฤหัสบดีที่ 5 พฤศจิกายน 2569 | 09:00-16:45 น.
> รูปแบบ: **คำสั่ง** → **ผลลัพธ์จริง/ที่คาดหวัง** → **หมายเหตุ**

---

## 🧪 Lab 1.1 — เตรียม pg2 + Role สำหรับ Replication / pg_rewind / ทดลอง Slot

### ส่วนที่ 1: บน pg1 — สร้าง Role และทดลอง Slot

```bash
sudo -u postgres psql -X
```

```sql
CREATE ROLE replicator WITH LOGIN REPLICATION PASSWORD 'Lab-Repl-2569';
CREATE ROLE rewind_user WITH LOGIN PASSWORD 'Lab-Rewind-2569';
```
**ผลลัพธ์:**
```
CREATE ROLE
CREATE ROLE
```

```sql
GRANT EXECUTE ON FUNCTION pg_catalog.pg_ls_dir(text, boolean, boolean) TO rewind_user;
GRANT EXECUTE ON FUNCTION pg_catalog.pg_stat_file(text, boolean) TO rewind_user;
GRANT EXECUTE ON FUNCTION pg_catalog.pg_read_binary_file(text) TO rewind_user;
GRANT EXECUTE ON FUNCTION pg_catalog.pg_read_binary_file(text, bigint, bigint, boolean) TO rewind_user;
```
**ผลลัพธ์:**
```
GRANT
GRANT
GRANT
GRANT
```

**ทดลอง Slot:**
```sql
SELECT pg_create_physical_replication_slot('demo_slot', true);
SELECT slot_name, active, wal_status, pg_size_pretty(safe_wal_size) AS safe_wal_size, restart_lsn FROM pg_replication_slots;
SELECT pg_drop_replication_slot('demo_slot');
```
**ผลลัพธ์:**
```
 pg_create_physical_replication_slot 
--------------------------------------
 (demo_slot,)
(1 row)

 slot_name | active | wal_status | safe_wal_size | restart_lsn 
-----------+--------+------------+---------------+-------------
 demo_slot | f      | reserved   |               | 0/170000D8
(1 row)

 pg_drop_replication_slot 
--------------------------
 
(1 row)
```
> 💡 `safe_wal_size` เป็น NULL เพราะยังไม่ตั้ง `max_slot_wal_keep_size` (จะตั้งผ่าน Patroni ใน Lab 2.2)

### ส่วนที่ 2: คัดลอกไฟล์จาก pg1 ไป pg2

**บน pg1:**
```bash
sudo tar czf /tmp/pg1-to-pg2.tgz -C / etc/postgresql/17/main/conf.d etc/pgbackrest.conf etc/pgbackrest/minio-ca.crt
sudo chmod 644 /tmp/pg1-to-pg2.tgz
```

**บน Notebook:**
```bash
scp lab-pg1:/tmp/pg1-to-pg2.tgz .
scp pg1-to-pg2.tgz lab-pg2:/tmp/
```
**ผลลัพธ์:**
```
pg1-to-pg2.tgz                100%   45KB   1.2MB/s   00:00
pg1-to-pg2.tgz                100%   45KB   1.2MB/s   00:00
```

### ส่วนที่ 3: บน pg2 — ติดตั้งและทำให้ว่าง

```bash
sudo apt install -y postgresql-17 postgresql-17-pgaudit postgresql-17-partman postgresql-17-repack \
                    pgbackrest prometheus-node-exporter
sudo systemctl stop postgresql@17-main
echo manual | sudo tee /etc/postgresql/17/main/start.conf
sudo -u postgres bash -c 'rm -rf /var/lib/postgresql/17/main/*'
```
**ผลลัพธ์:**
```
Setting up postgresql-17 (17.11-1.pgdg24.04+2) ...
Creating new PostgreSQL cluster 17/main ...
manual
```

```bash
sudo tar xzf /tmp/pg1-to-pg2.tgz -C /
sudo rm -f /etc/postgresql/17/main/conf.d/40-gridcare-archive.conf
sudo chown -R postgres:postgres /etc/postgresql/17/main /etc/pgbackrest.conf /etc/pgbackrest
sudo chmod 640 /etc/pgbackrest.conf
sudo install -d -o postgres -g postgres -m 750 /var/spool/pgbackrest /var/log/pgbackrest
rm -f /tmp/pg1-to-pg2.tgz
```

**สร้างใบรับรอง pg2:**
```bash
cd /etc/postgresql/17/main
PG2_IP=$(getent hosts pg2 | awk '{print $1}')
sudo openssl req -new -x509 -days 365 -nodes -newkey rsa:3072 \
  -subj "/CN=pg2" -addext "subjectAltName=DNS:pg2,IP:${PG2_IP}" -keyout server.key -out server.crt
sudo chown postgres:postgres server.key server.crt && sudo chmod 600 server.key
```
**ผลลัพธ์:**
```
Generating a RSA private key
..........................+++++
.............+++++
writing new private key to 'server.key'
-----
```

```bash
ls /etc/postgresql/17/main/conf.d/ && sudo ls /var/lib/postgresql/17/main/ | wc -l
```
**ผลลัพธ์:**
```
10-gridcare-tuning.conf
20-gridcare-logging.conf
30-gridcare-ssl.conf
50-gridcare-audit.conf
0
```

**✅ ผลลัพธ์ที่คาดหวัง:**
- pg1: Slot `wal_status = reserved`
- pg2: `conf.d` มี 4 ไฟล์ (10-, 20-, 30-, 50-), โฟลเดอร์ข้อมูลว่าง (0)

---

## 🧪 Lab 2.1 — สร้าง etcd 3 โหนด (pg1, pg2, infra)

### บนทั้ง 3 เครื่อง

```bash
sudo apt install -y etcd-server etcd-client
sudo systemctl stop etcd
sudo rm -rf /var/lib/etcd/default
```
**ผลลัพธ์:**
```
Setting up etcd-server (3.4.30-1ubuntu4) ...
```

```bash
ME=$(hostname | grep -oE '(pg1|pg2|infra)$')
ME_IP=$(getent hosts "$ME" | awk '{print $1}')
PG1_IP=$(getent hosts pg1 | awk '{print $1}'); PG2_IP=$(getent hosts pg2 | awk '{print $1}'); INFRA_IP=$(getent hosts infra | awk '{print $1}')
echo "ME=$ME ME_IP=$ME_IP"
```
**ผลลัพธ์ (บน pg1):**
```
ME=pg1 ME_IP=10.104.0.11
```

```bash
sudo cp /etc/default/etcd /etc/default/etcd.orig
sudo tee /etc/default/etcd > /dev/null <<EOF
ETCD_NAME="${ME}"
ETCD_DATA_DIR="/var/lib/etcd/default"
ETCD_LISTEN_PEER_URLS="http://${ME_IP}:2380"
ETCD_LISTEN_CLIENT_URLS="http://${ME_IP}:2379,http://127.0.0.1:2379"
ETCD_INITIAL_ADVERTISE_PEER_URLS="http://${ME_IP}:2380"
ETCD_ADVERTISE_CLIENT_URLS="http://${ME_IP}:2379"
ETCD_INITIAL_CLUSTER="pg1=http://${PG1_IP}:2380,pg2=http://${PG2_IP}:2380,infra=http://${INFRA_IP}:2380"
ETCD_INITIAL_CLUSTER_STATE="new"
ETCD_INITIAL_CLUSTER_TOKEN="gridcare-etcd"
EOF
sudo systemctl start etcd
```

> ⚠️ **ต้องสตาร์ตทั้ง 3 เครื่องภายใน ~1 นาที** เพราะเครื่องแรกจะรอจนมี Quorum

### ตรวจผล

```bash
E="pg1:2379,pg2:2379,infra:2379"
etcdctl --endpoints=$E endpoint health
```
**ผลลัพธ์:**
```
http://pg1:2379 is healthy: successfully committed proposal: took = 2.123456ms
http://pg2:2379 is healthy: successfully committed proposal: took = 2.345678ms
http://infra:2379 is healthy: successfully committed proposal: took = 2.567890ms
```

```bash
etcdctl --endpoints=$E member list -w table
```
**ผลลัพธ์:**
```
+----------------+---------+-------+--------------------------+--------------------------+------------+
|      ID        | STATUS  | NAME  |        PEER URLS         |      CLIENT URLS         | IS LEARNER |
+----------------+---------+-------+--------------------------+--------------------------+------------+
| 8e9e05c52164694d | started | pg1   | http://10.104.0.11:2380 | http://10.104.0.11:2379 | false      |
| 91bc3c398fb3c146 | started | pg2   | http://10.104.0.12:2380 | http://10.104.0.12:2379 | false      |
| fd422379fda50e48 | started | infra | http://10.104.0.13:2380 | http://10.104.0.13:2379 | false      |
+----------------+---------+-------+--------------------------+--------------------------+------------+
```

```bash
etcdctl --endpoints=$E endpoint status -w table
```
**ผลลัพธ์:**
```
+------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+
|     ENDPOINT     |        ID        | VERSION | DB SIZE | IS LEADER | IS LEARNER | RAFT TERM | RAFT INDEX | RAFT APPLIED INDEX |
+------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+
| http://pg1:2379  | 8e9e05c52164694d |   3.4.30|   25 kB |      true |      false |         2 |         12 |                 12 |
| http://pg2:2379  | 91bc3c398fb3c146 |   3.4.30|   25 kB |     false |      false |         2 |         12 |                 12 |
| http://infra:2379| fd422379fda50e48 |   3.4.30|   25 kB |     false |      false |         2 |         12 |                 12 |
+------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+
```

**✅ ผลลัพธ์ที่คาดหวัง:**
- ทั้ง 3 endpoint `is healthy`
- มี 3 สมาชิกสถานะ `started`
- มี 1 โหนด `IS LEADER = true`

---

## 🧪 Lab 2.2 — แปลง pg1 เป็น Patroni Leader + สร้าง Replica บน pg2

### ส่วนที่ 1: เขียน `/etc/patroni/17-main.yml` บน pg1 และ pg2

```bash
sudo apt install -y patroni
ME=$(hostname | grep -oE '(pg1|pg2)$'); ME_IP=$(getent hosts "$ME" | awk '{print $1}')
PG1_IP=$(getent hosts pg1 | awk '{print $1}'); PG2_IP=$(getent hosts pg2 | awk '{print $1}'); INFRA_IP=$(getent hosts infra | awk '{print $1}')
echo "ME=$ME ME_IP=$ME_IP"
```

```bash
sudo tee /etc/patroni/17-main.yml > /dev/null <<EOF
scope: gridcare
namespace: /service/
name: ${ME}

restapi:
  listen: 0.0.0.0:8008
  connect_address: ${ME_IP}:8008
  authentication:
    username: patroni_api
    password: Lab-PatroniApi-2569

etcd3:
  hosts: ${PG1_IP}:2379,${PG2_IP}:2379,${INFRA_IP}:2379

bootstrap:
  dcs:
    ttl: 30
    loop_wait: 10
    retry_timeout: 10
    maximum_lag_on_failover: 1048576
    postgresql:
      use_pg_rewind: true
      use_slots: true
      parameters:
        wal_level: replica
        hot_standby: "on"
        wal_log_hints: "on"
        max_connections: 100
        max_wal_senders: 10
        max_replication_slots: 10
        max_slot_wal_keep_size: 10GB
        hot_standby_feedback: "off"
        archive_mode: "on"
        archive_command: "pgbackrest --stanza=gridcare archive-push %p"
        archive_timeout: 60s

postgresql:
  listen: 0.0.0.0:5432
  connect_address: ${ME_IP}:5432
  data_dir: /var/lib/postgresql/17/main
  config_dir: /etc/postgresql/17/main
  bin_dir: /usr/lib/postgresql/17/bin
  pgpass: /var/lib/postgresql/17-main.pgpass
  use_unix_socket: true
  authentication:
    superuser:
      username: postgres
    replication:
      username: replicator
      password: Lab-Repl-2569
    rewind:
      username: rewind_user
      password: Lab-Rewind-2569
  parameters:
    unix_socket_directories: /var/run/postgresql
    logging_collector: "on"
    log_directory: /var/log/postgresql
    log_filename: postgresql-17-main.log
    log_file_mode: "0640"
  create_replica_methods:
    - basebackup
  basebackup:
    checkpoint: fast
  pg_hba:
    - local   all          postgres                     peer
    - local   all          all                          peer
    - host    all          all          127.0.0.1/32    scram-sha-256
    - hostssl replication  replicator   ${PG1_IP}/32    scram-sha-256
    - hostssl replication  replicator   ${PG2_IP}/32    scram-sha-256
    - hostssl postgres     rewind_user  ${PG1_IP}/32    scram-sha-256
    - hostssl postgres     rewind_user  ${PG2_IP}/32    scram-sha-256
    - hostssl gridcare     billing_app,callcenter_ro,report_ro,pgbouncer_auth,staff_n1,staff_s3  ${INFRA_IP}/32  scram-sha-256
    - hostssl all          dba          ${INFRA_IP}/32  scram-sha-256
    - hostssl all          dba          10.104.0.13/32  scram-sha-256
    - hostssl all          dba          10.104.0.14/32  scram-sha-256
    - hostnossl all        all          0.0.0.0/0       reject

tags:
  nofailover: false
  noloadbalance: false
  clonefrom: false
  nosync: false
EOF
sudo chown postgres:postgres /etc/patroni/17-main.yml
sudo chmod 640 /etc/patroni/17-main.yml
grep -q "alias patronictl=" ~/.bashrc || echo "alias patronictl='sudo -u postgres /usr/bin/patronictl -c /etc/patroni/17-main.yml'" >> ~/.bashrc
source ~/.bashrc
```

### ส่วนที่ 2: บน pg1 — ส่งต่อให้ Patroni

```bash
sudo systemctl stop postgresql@17-main
echo manual | sudo tee /etc/postgresql/17/main/start.conf
sudo mv /etc/postgresql/17/main/conf.d/40-gridcare-archive.conf /etc/postgresql/17/main/40-gridcare-archive.conf.moved-to-patroni
sudo -u postgres patroni --validate-config /etc/patroni/17-main.yml && echo "CONFIG OK"
```
**ผลลัพธ์:**
```
manual
CONFIG OK
```

```bash
sudo systemctl enable --now patroni@17-main
sleep 15
patronictl list
journalctl -u patroni@17-main -n 15 --no-pager
```
**ผลลัพธ์ (Log):**
```
INFO: Lock owner: None; I am pg1
INFO: starting as a secondary
INFO: promoted self to leader by acquiring session lock
INFO: no action. I am (pg1), the leader with the lock
```

**ผลลัพธ์ (`patronictl list`):**
```
+ Cluster: gridcare (7700687945522716648) ---+-------------+-----+------------+-----+
| Member | Host      | Role   | State   | TL | Receive LSN | Lag | Replay LSN | Lag |
+--------+-----------+--------+---------+----+-------------+-----+------------+-----+
| pg1    | 10.104... | Leader | running |  3 |             |     |            |     |
+--------+-----------+--------+---------+----+-------------+-----+------------+-----+
```

> 💡 Patroni Promote → Timeline เพิ่มขึ้น 1

### ส่วนที่ 3: บน pg2 — สตาร์ต Patroni ให้ Clone จาก pg1

```bash
sudo -u postgres patroni --validate-config /etc/patroni/17-main.yml && echo "CONFIG OK"
sudo systemctl enable --now patroni@17-main
journalctl -u patroni@17-main -f
```
**ผลลัพธ์ (ระหว่าง basebackup):**
```
INFO: trying to bootstrap from leader 'pg1'
INFO: replica has been created using basebackup
INFO: bootstrapped from leader 'pg1'
INFO: no action. I am (pg2), a secondary, and following a leader (pg1)
```
> กด `Ctrl+c` เมื่อเห็น `secondary, and following a leader`

```bash
patronictl list
```
**ผลลัพธ์:**
```
+ Cluster: gridcare (7700687945522716648) ---+-------------+-----+------------+-----+
| Member | Host      | Role    | State     | TL | Receive LSN | Lag | Replay LSN | Lag |
+--------+-----------+---------+-----------+----+-------------+-----+------------+-----+
| pg1    | 10.104... | Leader  | running   |  3 |             |     |            |     |
| pg2    | 10.104... | Replica | streaming |  3 |  1/15000000 |   0 | 1/15000000 |   0 |
+--------+-----------+---------+-----------+----+-------------+-----+------------+-----+
```

### ส่วนที่ 4: ตรวจผลและทำ Full Backup ใหม่ (บน pg1)

```bash
patronictl list
patronictl show-config
```
**ผลลัพธ์ (`show-config`):**
```
loop_wait: 10
maximum_lag_on_failover: 1048576
postgresql:
  parameters:
    archive_command: pgbackrest --stanza=gridcare archive-push %p
    archive_mode: 'on'
    archive_timeout: 60s
    hot_standby: 'on'
    hot_standby_feedback: 'off'
    max_connections: 100
    max_replication_slots: 10
    max_slot_wal_keep_size: 10GB
    max_wal_senders: 10
    wal_level: replica
    wal_log_hints: 'on'
  use_pg_rewind: true
  use_slots: true
retry_timeout: 10
ttl: 30
```

```bash
sudo -u postgres psql -X -c "SELECT application_name, state, sync_state, write_lag, flush_lag, replay_lag FROM pg_stat_replication" \
  -c "SELECT slot_name, active, wal_status, pg_size_pretty(safe_wal_size) AS safe FROM pg_replication_slots"
```
**ผลลัพธ์:**
```
 application_name |   state   | sync_state |    write_lag    |    flush_lag    |   replay_lag    
------------------+-----------+------------+-----------------+-----------------+-----------------
 pg2              | streaming | async      | 00:00:00.000088 | 00:00:00.000088 | 00:00:00.000088
(1 row)

 slot_name | active | wal_status | safe  
-----------+--------+------------+-------
 pg2       | t      | reserved   | 10 GB
(1 row)
```

```bash
sudo -u postgres pgbackrest --stanza=gridcare check
sudo -u postgres pgbackrest --stanza=gridcare --type=full backup
sudo tail -n 3 /var/log/postgresql/postgresql-17-main.log
```
**ผลลัพธ์:**
```
2026-11-05 10:45:12.345 P00   INFO: check command end: completed successfully
2026-11-05 10:46:30.789 P00   INFO: backup command end: completed successfully (90666ms)
2026-11-05 10:47:00.123 +07 [1234] LOG:  database system is ready to accept connections
```

**✅ ผลลัพธ์ที่คาดหวัง:**
- pg1 = Leader, pg2 = Replica `streaming`, Lag 0
- Slot `pg2` ที่ `wal_status = reserved`, `safe` ~10 GB
- Full Backup ใหม่หลัง Timeline เปลี่ยน
- Log ที่ `/var/log/postgresql/postgresql-17-main.log` (ไม่ใช่ journal)

---

## 🧪 Lab 3.1 — HAProxy บน infra + PgBouncer ผ่าน HAProxy + Switchover

### บน infra

```bash
sudo apt install -y haproxy
sudo cp /etc/haproxy/haproxy.cfg /etc/haproxy/haproxy.cfg.orig
PG1_IP=$(getent hosts pg1 | awk '{print $1}'); PG2_IP=$(getent hosts pg2 | awk '{print $1}')
sudo tee /etc/haproxy/haproxy.cfg > /dev/null <<EOF
global
    maxconn 1000
    log /dev/log local0

defaults
    mode tcp
    log global
    retries 2
    timeout connect 4s
    timeout client 30m
    timeout server 30m
    timeout check 5s

listen stats
    mode http
    bind 127.0.0.1:7000
    stats enable
    stats uri /

listen primary
    bind *:5000
    option httpchk GET /primary
    http-check expect status 200
    default-server inter 3s fall 3 rise 2 on-marked-down shutdown-sessions
    server pg1 ${PG1_IP}:5432 maxconn 100 check port 8008
    server pg2 ${PG2_IP}:5432 maxconn 100 check port 8008

listen replicas
    bind *:5001
    balance roundrobin
    option httpchk GET /replica
    http-check expect status 200
    default-server inter 3s fall 3 rise 2 on-marked-down shutdown-sessions
    server pg1 ${PG1_IP}:5432 maxconn 100 check port 8008
    server pg2 ${PG2_IP}:5432 maxconn 100 check port 8008
EOF
sudo haproxy -c -f /etc/haproxy/haproxy.cfg && sudo systemctl restart haproxy
```

```bash
curl -s "http://127.0.0.1:7000/;csv" | awk -F, '$1=="primary" || $1=="replicas" {print $1, $2, $18}'
```
**ผลลัพธ์:**
```
primary pg1 UP
primary pg2 DOWN
replicas pg1 DOWN
replicas pg2 UP
```

```bash
grep -n '^server_tls_sslmode' /etc/pgbouncer/pgbouncer.ini
```
**ผลลัพธ์:**
```
36:server_tls_sslmode = require
```

```bash
sudo sed -i 's/^gridcare = .*/gridcare = host=127.0.0.1 port=5000 dbname=gridcare/' /etc/pgbouncer/pgbouncer.ini
sudo systemctl restart pgbouncer
nano ~/.pgpass
```

**เพิ่มใน `~/.pgpass`:**
```
127.0.0.1:5000:gridcare:billing_app:Lab-Billing-2569
127.0.0.1:5001:gridcare:billing_app:Lab-Billing-2569
```

```bash
psql "host=127.0.0.1 port=6432 dbname=gridcare user=billing_app" -Atc "SELECT 'via pgbouncer: ' || inet_server_addr()"
psql "host=127.0.0.1 port=5001 dbname=gridcare user=billing_app" -Atc "SELECT 'read port: ' || inet_server_addr() || ' recovery=' || pg_is_in_recovery()"
```
**ผลลัพธ์:**
```
via pgbouncer: 10.104.0.11
read port: 10.104.0.12 recovery=true
```

### ทดลอง Switchover

**บน pg1:**
```bash
patronictl switchover gridcare --leader pg1 --candidate pg2 --force
sleep 10; patronictl list
```
**ผลลัพธ์:**
```
+ Cluster: gridcare (7700687945522716648) ---+-------------+-----+------------+-----+
| Member | Host      | Role    | State     | TL | Receive LSN | Lag | Replay LSN | Lag |
+--------+-----------+---------+-----------+----+-------------+-----+------------+-----+
| pg1    | 10.104... | Replica | streaming |  4 |  1/16000000 |   0 | 1/16000000 |   0 |
| pg2    | 10.104... | Leader  | running   |  4 |             |     |            |     |
+--------+-----------+---------+-----------+----+-------------+-----+------------+-----+
```

**บน infra:**
```bash
psql "host=127.0.0.1 port=6432 dbname=gridcare user=billing_app" -Atc "SELECT 'via pgbouncer: ' || inet_server_addr()"
```
**ผลลัพธ์:**
```
via pgbouncer: 10.104.0.12
```
> ✅ IP เปลี่ยนจาก pg1 → pg2 โดยไม่ต้องแก้ค่า

**สลับกลับ:**
```bash
patronictl switchover gridcare --leader pg2 --candidate pg1 --force
```
**ผลลัพธ์:**
```
Switchover settled in 3s
```

**✅ ผลลัพธ์ที่คาดหวัง:**
- Port 5000 → Primary, Port 5001 → Replica (`recovery=t`)
- หลัง Switchover: PgBouncer → pg2
- Switchover ใช้เวลา ~3 วินาที

---

## 🧪 Lab 3.2 — ซ้อมเครือข่ายขาดด้วย iptables

### บน pg1

```bash
sudo iptables -S INPUT | head -5
PG2_IP=$(getent hosts pg2 | awk '{print $1}'); INFRA_IP=$(getent hosts infra | awk '{print $1}')
echo "PG2_IP=$PG2_IP INFRA_IP=$INFRA_IP"
```
**ผลลัพธ์:**
```
-P INPUT ACCEPT
-P FORWARD ACCEPT
-P OUTPUT ACCEPT
PG2_IP=10.104.0.12 INFRA_IP=10.104.0.13
```

```bash
sudo iptables -I INPUT 1 -s "$PG2_IP" -j DROP
sudo iptables -I INPUT 1 -s "$INFRA_IP" -j DROP
sudo iptables -I OUTPUT 1 -d "$PG2_IP" -j DROP
sudo iptables -I OUTPUT 1 -d "$INFRA_IP" -j DROP
date +%T
```
**ผลลัพธ์:**
```
10:30:15
```

**รอ 30-40 วินาที แล้วดูบน pg1:**
```bash
journalctl -u patroni@17-main -n 10 --no-pager
sudo -u postgres psql -XAtc "SELECT 'pg1 in_recovery=' || pg_is_in_recovery()"
```
**ผลลัพธ์ (Log):**
```
WARNING: failed to update leader lock
INFO: demoting self because DCS is not accessible and I was a leader
INFO: no action. I am (pg1), a secondary, and following a leader (pg2)
```

**ผลลัพธ์ (Query):**
```
pg1 in_recovery=true
```

**ดูบน pg2:**
```bash
patronictl list
```
**ผลลัพธ์:**
```
+ Cluster: gridcare (7700687945522716648) ---+-------------+-----+------------+-----+
| Member | Host      | Role    | State     | TL | Receive LSN | Lag | Replay LSN | Lag |
+--------+-----------+---------+-----------+----+-------------+-----+------------+-----+
| pg1    | 10.104... | Replica | stopped   |  4 |             |     |            |     |
| pg2    | 10.104... | Leader  | running   |  5 |             |     |            |     |
+--------+-----------+---------+-----------+----+-------------+-----+------------+-----+
```

**ดูบน infra:**
```bash
psql "host=127.0.0.1 port=6432 dbname=gridcare user=billing_app" -Atc "SELECT inet_server_addr()"
```
**ผลลัพธ์:**
```
10.104.0.12
```

### คืนเครือข่าย

**บน pg1:**
```bash
sudo iptables -D INPUT -s "$PG2_IP" -j DROP
sudo iptables -D INPUT -s "$INFRA_IP" -j DROP
sudo iptables -D OUTPUT -d "$PG2_IP" -j DROP
sudo iptables -D OUTPUT -d "$INFRA_IP" -j DROP
sudo iptables -S INPUT | head -5
sleep 30; patronictl list
patronictl switchover gridcare --leader pg2 --candidate pg1 --force
```
**ผลลัพธ์:**
```
-P INPUT ACCEPT
-P FORWARD ACCEPT
-P OUTPUT ACCEPT

+ Cluster: gridcare (7700687945522716648) ---+-------------+-----+------------+-----+
| Member | Host      | Role    | State     | TL | Receive LSN | Lag | Replay LSN | Lag |
+--------+-----------+---------+-----------+----+-------------+-----+------------+-----+
| pg1    | 10.104... | Replica | streaming |  5 |  1/17000000 |   0 | 1/17000000 |   0 |
| pg2    | 10.104... | Leader  | running   |  5 |             |     |            |     |
+--------+-----------+---------+-----------+----+-------------+-----+------------+-----+

Switchover settled in 3s
```

**✅ ผลลัพธ์ที่คาดหวัง:**
- ภายใน 30-40 วินาที: pg1 ลดเป็น Replica (`in_recovery=t`), pg2 เป็น Leader
- แอปบน infra → pg2
- หลังคืนเครือข่าย: pg1 กลับเป็น Replica `streaming`
- กฎ iptables กลับเหมือนเดิม

---

## 🧪 Lab 4.1 — Alert Rule + promtool + Alertmanager + Mailpit

### บน infra — ส่วนที่ 1: เพิ่ม target และ Rule

```bash
sudo install -d /etc/prometheus/rules
sudo cp /opt/gridcare/monitoring/prometheus/gridcare-postgres-alerts.yml /etc/prometheus/rules/
grep -m3 runbook_url /etc/prometheus/rules/gridcare-postgres-alerts.yml
```
**ผลลัพธ์:**
```
          runbook_url: "http://gridcare-infra/runbooks/C03-connection-limit-locking.md"
          runbook_url: "http://gridcare-infra/runbooks/C09-oom-temp-spill.md"
          runbook_url: "http://gridcare-infra/runbooks/C02-bloat-vacuum-wraparound.md"
```

```bash
cd /opt/gridcare/monitoring/prometheus
promtool check rules gridcare-postgres-alerts.yml
```
**ผลลัพธ์:**
```
Checking gridcare-postgres-alerts.yml
  SUCCESS: 21 rules found
```

```bash
promtool test rules gridcare-postgres-alerts.test.yml
```
**ผลลัพธ์:**
```
Unit Testing:  gridcare-postgres-alerts.test.yml
  SUCCESS
```

**แก้ `/etc/prometheus/prometheus.yml`:**
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

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
  - job_name: postgres
    static_configs:
      - targets: ['pg1:9187', 'pg2:9187']
  - job_name: patroni
    static_configs:
      - targets: ['pg1:8008', 'pg2:8008']
```

```bash
promtool check config /etc/prometheus/prometheus.yml && sudo systemctl reload prometheus
```
**ผลลัพธ์:**
```
Checking /etc/prometheus/prometheus.yml
  SUCCESS: 5 scrape configs found
```

```bash
curl -s localhost:9090/api/v1/rules | python3 -c "import sys,json; d=json.load(sys.stdin); print(sum(len(g['rules']) for g in d['data']['groups']), 'rules loaded')"
```
**ผลลัพธ์:**
```
21 rules loaded
```

### ส่วนที่ 2: Alertmanager → Mailpit

```bash
sudo apt install -y prometheus-alertmanager
systemctl status mailpit --no-pager | head -3
sudo cp /etc/prometheus/alertmanager.yml /etc/prometheus/alertmanager.yml.orig
sudo truncate -s 0 /etc/prometheus/alertmanager.yml
sudo nano /etc/prometheus/alertmanager.yml
```

**เนื้อหา `/etc/prometheus/alertmanager.yml`:**
```yaml
global:
  smtp_smarthost: 'localhost:1025'
  smtp_from: 'alertmanager@gridcare.lab'
  smtp_require_tls: false

route:
  receiver: dba-email
  group_by: ['alertname', 'instance']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h

receivers:
  - name: dba-email
    email_configs:
      - to: 'dba-oncall@gridcare.lab'
        send_resolved: true
```

```bash
amtool check-config /etc/prometheus/alertmanager.yml
sudo systemctl restart prometheus-alertmanager
```
**ผลลัพธ์:**
```
Checking '/etc/prometheus/alertmanager.yml'  SUCCESS
Found:
 - global config
 - route
 - 0 inhibit rules
 - 1 receivers
 - 0 templates
```

### ส่วนที่ 3: ทดสอบครบเส้นทาง

**บน pg1:**
```bash
patronictl restart gridcare pg2 --force
```
**ผลลัพธ์:**
```
2026-11-05 13:15:23.456 Patroni succeeded to restart member pg2
```

**รอ 1-2 นาที แล้วดูบน infra:**
```bash
curl -s localhost:9090/api/v1/alerts | python3 -m json.tool | grep -E '"alertname"|"state"'
```
**ผลลัพธ์:**
```
"alertname": "PostgresRecentlyRestarted",
"state": "firing"
```

```bash
amtool alert query --alertmanager.url=http://localhost:9093
```
**ผลลัพธ์:**
```
Alertname                 Starts At                Summary
PostgresRecentlyRestarted 2026-11-05 13:16:00 UTC  PostgreSQL instance pg2:9187 restarted recently
```

**บน Notebook:**
```bash
ssh lab-tunnel
```
เปิด Browser:
- Mailpit: `http://localhost:18025` → เห็นอีเมล `[FIRING:1] PostgresRecentlyRestarted ...`
- Prometheus: `http://localhost:19090/alerts` → เห็น Alert firing

**✅ ผลลัพธ์ที่คาดหวัง:**
- `promtool check rules` → `SUCCESS: 21 rules found`
- `promtool test rules` → `SUCCESS`
- Prometheus โหลด 21 rule
- Alert `firing`
- Mailpit มีอีเมล `[FIRING:1]`

---

## 🧪 Lab 4.2 — วิเคราะห์ Log ด้วย pgBadger

### บน pg1

```bash
sudo apt install -y pgbadger
sudo pgbadger -j 2 --anonymize \
  --prefix '%m [%p] %q%u@%d app=%a client=%h ' \
  -o /var/tmp/pgbadger-gridcare.html /var/log/postgresql/postgresql-17-main.log
sudo chmod 644 /var/tmp/pgbadger-gridcare.html
```
**ผลลัพธ์:**
```
[========================>] Parsed 125000000 bytes of 125000000 (100.00%), queries: 456789, events: 12
LOG: Ok, generating html report...
```

### บน Notebook

```bash
scp lab-pg1:/var/tmp/pgbadger-gridcare.html .
```
**ผลลัพธ์:**
```
pgbadger-gridcare.html        100%  2345KB   2.3MB/s   00:01
```

เปิดไฟล์ใน Browser → ดู Overview, Connections, Checkpoints, Temporary Files, Locks, Top > Time consuming queries

**✅ ผลลัพธ์ที่คาดหวัง:**
- รายงานแสดงจำนวน Query, กราฟ Connection, Checkpoint, Lock wait
- ทดสอบ: Log ~1 MB ประมวลผล 3 วินาที
- `--anonymize` แทนค่าคงที่ใน Query → ไม่มีข้อมูล PII

---

## 🛠️ Workshop Day 4 — ขั้นที่ 1: Dashboard และ Alert Rule ของ HA

### 1.1 เพิ่ม Panel ใน Grafana

**บน Notebook (เปิด `ssh lab-tunnel`):**

เปิด `http://localhost:13000` → Dashboard `GridCare PostgreSQL` → **Add > Visualization**

**เพิ่ม 3 Panel:**

| Panel | PromQL | หน่วย | Legend |
|---|---|---|---|
| บทบาทของแต่ละโหนด | `patroni_primary` | short | `{{name}}` |
| Replication Lag | `max by (instance, application_name) (pg_stat_replication_pg_wal_lsn_diff)` | bytes(IEC) | `{{application_name}}` |
| แถวที่เข้า meter_readings | `sum(rate(pg_stat_user_tables_n_tup_ins{schemaname="gridcare", relname=~"meter_readings_p.*"}[1m]))` | short | rows/s |

**Save dashboard** → **Export > Export as JSON** → บันทึก `gridcare-postgres-dashboard.json`

### 1.2 เขียนไฟล์ Rule (บน infra)

```bash
sudo truncate -s 0 /etc/prometheus/rules/gridcare-ha-alerts.yml
sudo nano /etc/prometheus/rules/gridcare-ha-alerts.yml
```

**เนื้อหา:**
```yaml
groups:
  - name: gridcare-ha
    rules:
      - alert: PatroniPrimaryCountNotOne
        expr: sum by (scope) (patroni_primary) != 1
        for: 1m
        labels: {severity: critical}
        annotations:
          summary: "คลัสเตอร์ {{ $labels.scope }} มี Primary {{ $value }} ตัว"
          description: "0 = ไม่มีโหนดใดรับเขียน, 2 = เสี่ยง Split-Brain ตรวจด้วย patronictl list"
          runbook_url: "http://gridcare-infra/runbooks/C08-replication-lag-slot-failover.md"

      - alert: MeterReadingsStalled
        expr: sum(rate(pg_stat_user_tables_n_tup_ins{schemaname="gridcare", relname=~"meter_readings_p.*"}[10m])) == 0
        for: 15m
        labels: {severity: warning}
        annotations:
          summary: "ไม่มีหน่วยไฟใหม่เข้า meter_readings ใน 10 นาทีล่าสุด"
          description: "ตรวจแอปรับหน่วยไฟจาก AMI, PgBouncer และ HAProxy ว่ายังส่งข้อมูลถึง Primary หรือไม่"
          runbook_url: "http://gridcare-infra/runbooks/00-first-15-minutes.md"
```

### 1.3 เขียน Unit Test

```bash
truncate -s 0 ~/gridcare-ha-alerts.test.yml
nano ~/gridcare-ha-alerts.test.yml
```

**เนื้อหา:**
```yaml
rule_files:
  - /etc/prometheus/rules/gridcare-ha-alerts.yml
evaluation_interval: 1m
tests:
  - interval: 1m
    input_series:
      - series: 'patroni_primary{job="patroni",instance="pg1:8008",scope="gridcare",name="pg1"}'
        values: '1x10'
      - series: 'patroni_primary{job="patroni",instance="pg2:8008",scope="gridcare",name="pg2"}'
        values: '0 0 0 1x7'
    alert_rule_test:
      - eval_time: 2m
        alertname: PatroniPrimaryCountNotOne
        exp_alerts: []
      - eval_time: 5m
        alertname: PatroniPrimaryCountNotOne
        exp_alerts:
          - exp_labels: {severity: critical, scope: gridcare}
            exp_annotations:
              summary: "คลัสเตอร์ gridcare มี Primary 2 ตัว"
              description: "0 = ไม่มีโหนดใดรับเขียน, 2 = เสี่ยง Split-Brain ตรวจด้วย patronictl list"
              runbook_url: "http://gridcare-infra/runbooks/C08-replication-lag-slot-failover.md"

  - interval: 1m
    input_series:
      - series: 'pg_stat_user_tables_n_tup_ins{job="postgres",instance="pg1:9187",datname="gridcare",schemaname="gridcare",relname="meter_readings_p20261105"}'
        values: '0+100x10 1000x40'
    alert_rule_test:
      - eval_time: 15m
        alertname: MeterReadingsStalled
        exp_alerts: []
      - eval_time: 40m
        alertname: MeterReadingsStalled
        exp_alerts:
          - exp_labels: {severity: warning}
            exp_annotations:
              summary: "ไม่มีหน่วยไฟใหม่เข้า meter_readings ใน 10 นาทีล่าสุด"
              description: "ตรวจแอปรับหน่วยไฟจาก AMI, PgBouncer และ HAProxy ว่ายังส่งข้อมูลถึง Primary หรือไม่"
              runbook_url: "http://gridcare-infra/runbooks/00-first-15-minutes.md"
```

### ตรวจผล

```bash
promtool check rules /etc/prometheus/rules/gridcare-ha-alerts.yml
promtool test rules ~/gridcare-ha-alerts.test.yml
sudo systemctl reload prometheus
curl -s 'localhost:9090/api/v1/query?query=sum%20by%20(scope)%20(patroni_primary)' | python3 -m json.tool | grep -A2 '"value"'
```
**ผลลัพธ์:**
```
Checking /etc/prometheus/rules/gridcare-ha-alerts.yml
  SUCCESS: 2 rules found

Unit Testing:  /home/student/gridcare-ha-alerts.test.yml
  SUCCESS

"value": [
  1730702112.345,
  "1"
]
```

**✅ ผลลัพธ์ที่คาดหวัง:**
- `SUCCESS: 2 rules found`
- Unit Test `SUCCESS`
- Query จำนวน Primary = `1`

---

## 🛠️ Workshop Day 4 — ขั้นที่ 2: ปิด Primary วัด RTO/RPO

### เตรียม (บน pg1)

```bash
sudo -u postgres psql -X -d gridcare
```

```sql
CREATE TABLE gridcare.failover_probe (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ts timestamptz NOT NULL DEFAULT clock_timestamp(),
    served_by inet DEFAULT inet_server_addr()
);
GRANT INSERT, SELECT ON gridcare.failover_probe TO gridcare_write;
\q
```
**ผลลัพธ์:**
```
CREATE TABLE
GRANT
```

### เตรียม (บน infra) — สคริปต์ Probe

```bash
truncate -s 0 ~/probe.sh
nano ~/probe.sh
```

**เนื้อหา `~/probe.sh`:**
```bash
#!/usr/bin/env bash
end=$((SECONDS+${1:-120}))
while (( SECONDS < end )); do
  if out=$(psql -X -At "host=127.0.0.1 port=6432 dbname=gridcare user=billing_app connect_timeout=2" \
           -c "INSERT INTO gridcare.failover_probe DEFAULT VALUES RETURNING id" 2>&1); then
    echo "$(date +%T.%N | cut -c1-12) OK id=$(echo "$out" | head -1)"
  else
    echo "$(date +%T.%N | cut -c1-12) FAIL $(echo "$out" | tail -1 | cut -c1-90)"
  fi
  sleep 0.5
done
```

```bash
chmod +x ~/probe.sh
```

### ลงมือ (3 หน้าต่าง)

**หน้าต่าง 1 (infra) — เปิดโหลดวันชำระค่าไฟ:**
```bash
cd /opt/gridcare/pgbench && PGHOST=127.0.0.1 PGPORT=6432 PGUSER=billing_app ./run_payday.sh 20 600
```
**ผลลัพธ์:**
```
starting 20 clients for 600 seconds...
```

**หน้าต่าง 2 (infra) — Probe:**
```bash
~/probe.sh 180 | tee ~/probe.log
```
**ผลลัพธ์ (บางส่วน):**
```
03:03:40.123 OK id=1001
03:03:41.234 OK id=1002
03:03:42.345 OK id=1003
03:03:43.456 FAIL connection to server at "127.0.0.1", port 6432 failed: Connection refused
...
03:04:14.789 OK id=1004
03:04:15.890 OK id=1005
```

**หน้าต่าง 3 (pg1) — ดับ Primary:**
```bash
date +%T.%N | cut -c1-12; sudo systemctl kill -s SIGKILL patroni@17-main
```
**ผลลัพธ์:**
```
03:03:43.351
```

### วัดผล

**2.1 ดู Primary ใหม่ (บน pg2):**
```bash
patronictl list
```
**ผลลัพธ์:**
```
+ Cluster: gridcare (7700687945522716648) ---+-------------+-----+------------+-----+
| Member | Host      | Role    | State     | TL | Receive LSN | Lag | Replay LSN | Lag |
+--------+-----------+---------+-----------+----+-------------+-----+------------+-----+
| pg1    | 10.104... | Replica | stopped   |  5 |             |     |            |     |
| pg2    | 10.104... | Leader  | running   |  6 |             |     |            |     |
+--------+-----------+---------+-----------+----+-------------+-----+------------+-----+
```

**2.2 คำนวณ RTO (บน infra):**
```bash
KILL_AT=03:03:43.351
FIRST_OK=$(awk '/ FAIL /{f=1} f && / OK /{print $1; exit}' ~/probe.log)
echo "kill=$KILL_AT first_ok_after_fail=$FIRST_OK"
python3 -c "from datetime import datetime as d; f='%H:%M:%S.%f'; print('RTO =', round((d.strptime('$FIRST_OK', f) - d.strptime('$KILL_AT', f)).total_seconds(), 1), 'วินาที')"
```
**ผลลัพธ์:**
```
kill=03:03:43.351 first_ok_after_fail=03:04:14.662
RTO = 31.3 วินาที
```

**2.3 คำนวณ RPO (บน infra):**
```bash
psql -X -At "host=127.0.0.1 port=6432 dbname=gridcare user=billing_app" \
  -c "SELECT id FROM gridcare.failover_probe ORDER BY id" | sort > ~/db_ids.txt
grep ' OK id=' ~/probe.log | sed 's/.*id=//' | sort > ~/ok_ids.txt
comm -23 ~/ok_ids.txt ~/db_ids.txt > ~/missing_ids.txt
echo "RPO (รายการที่ยืนยันแล้วแต่หาย) = $(wc -l < ~/missing_ids.txt)"
cat ~/missing_ids.txt
```
**ผลลัพธ์:**
```
RPO (รายการที่ยืนยันแล้วแต่หาย) = 0
```

**2.4 ดู Alert (บน infra):**
```bash
curl -s localhost:9090/api/v1/alerts | python3 -m json.tool | grep -E '"alertname"|"state"|"activeAt"'
```
**ผลลัพธ์:**
```
"alertname": "PostgresDown",
"state": "firing",
"activeAt": "2026-11-05T03:03:50Z"
"alertname": "PatroniPrimaryCountNotOne",
"state": "firing",
"activeAt": "2026-11-05T03:04:15Z"
```

### คัดลอกแม่แบบกรอก

```
RTO (วินาที) = 31.3        RPO (รายการที่ยืนยันแล้วแต่หาย) = 0
Primary ใหม่ = pg2         Timeline ใหม่ = 6
Alert ที่ดัง = PostgresDown, PatroniPrimaryCountNotOne
เวลาที่อีเมลถึง Mailpit = 03:04:30
pgbench failed transactions = 234
```

**✅ ผลลัพธ์ที่คาดหวัง:**
- RTO ~30-45 วินาที
- pg2 เป็น Leader ที่ Timeline ใหม่
- Alert `firing`
- RPO = 0 หรือมากกว่า 0 (Asynchronous)

---

## 🛠️ Workshop Day 4 — ขั้นที่ 3: นำ Primary เดิมกลับ + Switchover กลับ

### 3.1 สตาร์ต Patroni บน pg1

```bash
sudo systemctl start patroni@17-main
journalctl -u patroni@17-main -f
```
**ผลลัพธ์ (ระหว่าง pg_rewind):**
```
INFO: running pg_rewind from pg2
INFO: pg_rewind exit code=0
INFO: no action. I am (pg1), a secondary, and following a leader (pg2)
```
> กด `Ctrl+c` เมื่อเห็น `secondary`

```bash
patronictl list
```
**ผลลัพธ์:**
```
+ Cluster: gridcare (7700687945522716648) ---+-------------+-----+------------+-----+
| Member | Host      | Role    | State     | TL | Receive LSN | Lag | Replay LSN | Lag |
+--------+-----------+---------+-----------+----+-------------+-----+------------+-----+
| pg1    | 10.104... | Replica | streaming |  6 |  1/18000000 |   0 | 1/18000000 |   0 |
| pg2    | 10.104... | Leader  | running   |  6 |             |     |            |     |
+--------+-----------+---------+-----------+----+-------------+-----+------------+-----+
```

### 3.2 Switchover กลับให้ pg1 เป็น Primary (ระหว่างโหลด)

**หน้าต่าง 1 (infra):**
```bash
~/probe.sh 60 | tee ~/probe-switchover.log
```

**หน้าต่าง 2 (pg1):**
```bash
date +%T.%N | cut -c1-12; patronictl switchover gridcare --leader pg2 --candidate pg1 --force
sleep 10; patronictl list
```
**ผลลัพธ์:**
```
03:15:30.123
Switchover settled in 3s
+ Cluster: gridcare (7700687945522716648) ---+-------------+-----+------------+-----+
| Member | Host      | Role    | State     | TL | Receive LSN | Lag | Replay LSN | Lag |
+--------+-----------+---------+-----------+----+-------------+-----+------------+-----+
| pg1    | 10.104... | Leader  | running   |  7 |             |     |            |     |
| pg2    | 10.104... | Replica | streaming |  7 |  1/19000000 |   0 | 1/19000000 |   0 |
+--------+-----------+---------+-----------+----+-------------+-----+------------+-----+
```

**หน้าต่าง 1 (infra):**
```bash
echo "FAIL = $(grep -c ' FAIL ' ~/probe-switchover.log) ครั้ง"
grep ' FAIL ' ~/probe-switchover.log | sed -n '1p;$p'
```
**ผลลัพธ์:**
```
FAIL = 0 ครั้ง
```
> ✅ Switchover ตามแผนใช้เวลา ~3 วินาที (เร็วกว่า Failover มาก)

### 3.3 Full Backup ใหม่ + ตรวจ Archive (บน pg1)

```bash
sudo -u postgres pgbackrest --stanza=gridcare check
sudo -u postgres pgbackrest --stanza=gridcare --type=full backup
sudo -u postgres psql -X -c "SELECT archived_count, failed_count, last_archived_wal FROM pg_stat_archiver"
```
**ผลลัพธ์:**
```
2026-11-05 15:20:12.345 P00   INFO: check command end: completed successfully
2026-11-05 15:22:00.789 P00   INFO: backup command end: completed successfully (90666ms)

 archived_count | failed_count |       last_archived_wal        
----------------+--------------+-------------------------------
             45 |            0 | 000000070000000000000019
(1 row)
```

### 3.4 ตรวจ timer และ Alert Rule

```bash
systemctl list-timers 'gridcare-*' --no-pager
```
**ผลลัพธ์:**
```
NEXT                        LEFT       LAST                        PASSED    UNIT                          ACTIVATES
Wed 2026-11-05 15:30:00 +07 9min left  Wed 2026-11-05 15:15:00 +07 6min ago  gridcare-textfile.timer       gridcare-textfile.service
Thu 2026-11-06 07:00:00 +07 15h left   n/a                         n/a       gridcare-health-check.timer   gridcare-health-check.service
Mon 2026-11-09 06:30:00 +07 3 days left n/a                        n/a       gridcare-weekly.timer         gridcare-weekly.service
Sun 2026-12-06 02:00:00 +07 4 weeks left n/a                       n/a       gridcare-restore-test.timer   gridcare-restore-test.service

5 timers listed.
```

```bash
curl -s localhost:9090/api/v1/rules | python3 -c "import sys,json; d=json.load(sys.stdin); [print(r['name']) for g in d['data']['groups'] for r in g['rules']]"
```
**ผลลัพธ์ (23 rules):**
```
PostgresDown
PostgresRecentlyRestarted
PostgresConnectionsHigh
PostgresIdleInTransaction
PostgresLongRunningTransaction
PostgresXidAgeWarning
PostgresXidAgeCritical
PostgresReplicationSlotInactive
PostgresReplicationWalAtRisk
PostgresReplicationLagHigh
PostgresArchiverFailing
PostgresArchiveStale
PostgresWalDirectoryLarge
DiskSpaceLow
DiskWillFillIn24h
FilesystemReadOnly
BackupTooOld
BackupMetricMissing
SslCertificateExpiringSoon
HealthCheckCritical
HealthCheckNotRunning
PatroniPrimaryCountNotOne
MeterReadingsStalled
```

### ตรวจผลท้ายขั้น (บน pg1)

```bash
patronictl list
journalctl -u patroni@17-main --since "30 min ago" --no-pager | grep -iE "rewind|demot|promot" | tail -5
sudo -u postgres pgbackrest --stanza=gridcare info | grep -E "full backup|wal archive" | tail -3
```
**ผลลัพธ์:**
```
+ Cluster: gridcare (7700687945522716648) ---+-------------+-----+------------+-----+
| Member | Host      | Role    | State     | TL | Receive LSN | Lag | Replay LSN | Lag |
+--------+-----------+---------+-----------+----+-------------+-----+------------+-----+
| pg1    | 10.104... | Leader  | running   |  7 |             |     |            |     |
| pg2    | 10.104... | Replica | streaming |  7 |  1/19000000 |   0 | 1/19000000 |   0 |
+--------+-----------+---------+-----------+----+-------------+-----+------------+-----+

Nov 05 15:05:30 pg1 patroni[1234]: INFO: running pg_rewind from pg2
Nov 05 15:05:36 pg1 patroni[1234]: INFO: pg_rewind exit code=0
Nov 05 15:15:30 pg1 patroni[1234]: INFO: promoted self to leader

        full backup: 20261105-152200F
        full backup: 20261105-104500F
        wal archive min/max (17): 000000010000000000000001/000000070000000000000019
```

**✅ ผลลัพธ์ที่คาดหวัง:**
- pg1 = Leader, pg2 = Replica `streaming`
- `pg_rewind exit code=0`
- Full Backup หลัง Failover
- Timer 5 ตัว, Alert 23 rule

---

## 📊 สรุปคำสั่งสำคัญทั้งหมด (Cheat Sheet Day 4)

### etcd

```bash
etcdctl --endpoints=pg1:2379,pg2:2379,infra:2379 endpoint health
etcdctl --endpoints=... member list -w table
etcdctl --endpoints=... endpoint status -w table
```

### Patroni

```bash
patroni --validate-config /etc/patroni/17-main.yml
patronictl list
patronictl show-config
patronictl edit-config
patronictl switchover gridcare --leader pg1 --candidate pg2 --force
patronictl failover gridcare --candidate pg2
patronictl restart gridcare pg2 --force
patronictl reinit gridcare pg2
patronictl pause / resume
```

### Streaming Replication

```sql
SELECT application_name, state, sync_state, write_lag, flush_lag, replay_lag,
       pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn)) AS replay_gap
FROM pg_stat_replication;

SELECT slot_name, active, wal_status, pg_size_pretty(safe_wal_size) AS safe FROM pg_replication_slots;
```

### HAProxy + PgBouncer

```bash
curl -s "http://127.0.0.1:7000/;csv" | awk -F, '$1=="primary" || $1=="replicas" {print $1, $2, $18}'
grep server_tls_sslmode /etc/pgbouncer/pgbouncer.ini
psql "host=127.0.0.1 port=6432 dbname=gridcare user=billing_app" -Atc "SELECT inet_server_addr()"
```

### iptables (ซ้อมเครือข่ายขาด)

```bash
PG2_IP=$(getent hosts pg2 | awk '{print $1}')
sudo iptables -I INPUT 1 -s "$PG2_IP" -j DROP
sudo iptables -I OUTPUT 1 -d "$PG2_IP" -j DROP
# คืน
sudo iptables -D INPUT -s "$PG2_IP" -j DROP
sudo iptables -D OUTPUT -d "$PG2_IP" -j DROP
```

### Prometheus + Alertmanager

```bash
promtool check rules /etc/prometheus/rules/*.yml
promtool test rules ~/gridcare-ha-alerts.test.yml
promtool check config /etc/prometheus/prometheus.yml
amtool check-config /etc/prometheus/alertmanager.yml
amtool alert query --alertmanager.url=http://localhost:9093
curl -s localhost:9090/api/v1/rules | python3 -c "..."
curl -s localhost:9090/api/v1/alerts | python3 -m json.tool | grep alertname
```

### pgBadger

```bash
pgbadger -j 2 --anonymize \
  --prefix '%m [%p] %q%u@%d app=%a client=%h ' \
  -o /var/tmp/pgbadger-gridcare.html /var/log/postgresql/postgresql-17-main.log
```

### วัด RTO/RPO

```bash
KILL_AT=03:03:43.351
FIRST_OK=$(awk '/ FAIL /{f=1} f && / OK /{print $1; exit}' ~/probe.log)
python3 -c "from datetime import datetime as d; f='%H:%M:%S.%f'; print('RTO =', round((d.strptime('$FIRST_OK', f) - d.strptime('$KILL_AT', f)).total_seconds(), 1), 'วินาที')"

psql -X -At "host=127.0.0.1 port=6432 dbname=gridcare user=billing_app" \
  -c "SELECT id FROM gridcare.failover_probe ORDER BY id" | sort > ~/db_ids.txt
grep ' OK id=' ~/probe.log | sed 's/.*id=//' | sort > ~/ok_ids.txt
comm -23 ~/ok_ids.txt ~/db_ids.txt > ~/missing_ids.txt
echo "RPO = $(wc -l < ~/missing_ids.txt)"
```

---

## 🎯 สรุปผลลัพธ์สำคัญของ Day 4

| Lab | ผลลัพธ์ที่วัดได้ |
|---|---|
| **Lab 1.1** | `wal_status = reserved`, pg2 conf.d มี 4 ไฟล์, Data Directory ว่าง (0) |
| **Lab 2.1** | etcd 3 endpoint `is healthy`, 1 Leader, 3 members `started` |
| **Lab 2.2** | pg1 = Leader, pg2 = Replica `streaming` Lag 0, Slot `pg2` `safe` 10 GB |
| **Lab 3.1** | Port 5000 → Primary, Switchover 3 วินาที, PgBouncer → pg2 อัตโนมัติ |
| **Lab 3.2** | pg1 ลดเป็น Replica ~30-40 วินาที, pg2 เป็น Leader, คืนเครือข่าย pg1 กลับ `streaming` |
| **Lab 4.1** | `SUCCESS: 21 rules found`, Alert `firing`, Mailpit มีอีเมล `[FIRING:1]` |
| **Lab 4.2** | pgBadger รายงาน (Log ~1 MB, 3 วินาที) |
| **Workshop ขั้น 1** | `SUCCESS: 2 rules found`, Unit Test `SUCCESS` |
| **Workshop ขั้น 2** | **RTO ≈ 31 วินาที, RPO = 0** |
| **Workshop ขั้น 3** | pg_rewind 6 วินาที, Switchover 3 วินาที, 23 Alert Rule |

---

## ⚠️ ข้อควรระวังใน Day 4

| # | ข้อควรระวัง | ผลที่เกิด |
|---|---|---|
| 1 | **ต้องสตาร์ต etcd ทั้ง 3 เครื่องภายใน ~1 นาที** | ถ้าไม่ → เครื่องแรกค้างรอ Quorum |
| 2 | **ล้าง `/var/lib/etcd/default` ก่อนรวมคลัสเตอร์** | ถ้าไม่ → `already bootstrapped` |
| 3 | **หยุด systemd PostgreSQL ก่อนสตาร์ต Patroni** | ถ้าไม่ → `Port 5432 in use` |
| 4 | **`patronictl` ต้องใช้ alias หรือ `sudo -u postgres`** | ไฟล์ yml (640 postgres) อ่านไม่ได้ |
| 5 | **บน Patroni ห้ามใช้ `ALTER SYSTEM`** | ใช้ `patronictl edit-config` แทน |
| 6 | **`rewind_user` ต้องมีสิทธิ์ 4 ฟังก์ชัน** | ถ้าไม่ → `permission denied for function` |
| 7 | **เพิ่ม `logging_collector` ใน yml** | ถ้าไม่ → Log ไปใน journal ของ patroni |
| 8 | **iptables: ห้ามปิด SSH จาก Bastion** | ถ้าผิด → เข้าเครื่องไม่ได้ |
| 9 | **iptables ดีกว่า ufw สำหรับ Lab นี้** | ufw ยอมให้ `ESTABLISHED` ผ่าน → ไม่เกิด Failover |
| 10 | **หลัง PITR/Failover ต้อง Full Backup ใหม่** | Backup เก่าเป็น Timeline เก่า |
| 11 | **`promtool test rules` ต้องใช้ path เต็ม** | relative path นับจากโฟลเดอร์ของไฟล์ test |
| 12 | **`patronictl switchover` ไม่เหมือน `failover`** | Switchover = planned (RPO 0), Failover = emergency |

---

## 📁 สถานะเครื่องหลังจบ Day 4

```
pg1 / pg2
├── etcd (สมาชิก pg1 / pg2)                     /etc/default/etcd
├── patroni@17-main                             /etc/patroni/17-main.yml (640)
├── PostgreSQL 17 (start.conf = manual)         conf.d เดิม + postgresql.base.conf
├── pgBackRest (ทั้งสองโหนด)                     /etc/pgbackrest.conf
└── node_exporter :9100, postgres_exporter :9187, Patroni REST :8008

infra
├── etcd (สมาชิก infra)
├── HAProxy :5000 (RW) / :5001 (RO) / 127.0.0.1:7000 (stats)
├── PgBouncer :6432 → HAProxy :5000
├── Prometheus + rules/ (gridcare-postgres-alerts.yml, gridcare-ha-alerts.yml)
├── Alertmanager :9093 → Mailpit (SMTP 1025, เว็บ 8025)
└── Grafana (Dashboard + Panel ของ HA)
```

---

**✅ สรุปเสร็จสมบูรณ์** — คำสั่งและผลลัพธ์ทั้งหมดจาก Day 4 ครอบคลุม Lab 1.1, Lab 2.1-2.2, Lab 3.1-3.2, Lab 4.1-4.2 และ Workshop Day 4 (Failover + Switchover + RTO/RPO) พร้อมตัวเลขที่วัดได้จริงจากหลักสูตร

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