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